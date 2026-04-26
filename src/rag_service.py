import logging
import os
from pathlib import Path
from typing import List

from .chroma_handler import ChromaDBHandler
from .chunking_handler import TextChunker
from .embeddings import EmbeddingGenerator
from .groq_handler import GroqHandler
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.pdf_dir = Path(os.getenv("PDF_DATA_DIR", "data/pdfs"))
        self.collection_names = self._collection_names()
        self.primary_collection = self.collection_names[0]
        self.embedder = EmbeddingGenerator(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
        self.databases = [
            ChromaDBHandler(collection_name=name)
            for name in self.collection_names
        ]
        self.llm = GroqHandler()
        self.ensure_vector_database()

    def _collection_names(self) -> List[str]:
        raw_names = os.getenv("RAG_COLLECTION_NAMES") or os.getenv("RAG_COLLECTION_NAME") or "rice_crops"
        names = [name.strip() for name in raw_names.split(",") if name.strip()]
        return names or ["rice_crops"]

    def ensure_vector_database(self) -> None:
        total_chunks = sum(db.count() for db in self.databases)
        if total_chunks > 0:
            logger.info("Using existing ChromaDB with %s chunks", total_chunks)
            return

        logger.info("No existing ChromaDB data found. Starting first-run PDF ingestion.")
        self.download_pdfs_if_needed()
        self.build_vector_database()

    def download_pdfs_if_needed(self) -> None:
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        existing_pdfs = list(self.pdf_dir.rglob("*.pdf"))
        if existing_pdfs:
            logger.info("Using %s existing PDF files from %s", len(existing_pdfs), self.pdf_dir)
            return

        folder_url = os.getenv("GOOGLE_DRIVE_FOLDER_URL")
        file_urls = [
            url.strip()
            for url in os.getenv("GOOGLE_DRIVE_FILE_URLS", "").split(",")
            if url.strip()
        ]

        if folder_url:
            self._download_google_drive_folder(folder_url)
        elif file_urls:
            self._download_google_drive_files(file_urls)
        else:
            raise RuntimeError(
                "No PDFs found and no Google Drive source configured. "
                "Set GOOGLE_DRIVE_FOLDER_URL or GOOGLE_DRIVE_FILE_URLS."
            )

        downloaded_pdfs = list(self.pdf_dir.rglob("*.pdf"))
        if not downloaded_pdfs:
            raise RuntimeError("Google Drive download completed, but no PDF files were found.")

    def _download_google_drive_folder(self, folder_url: str) -> None:
        try:
            import gdown
        except ImportError as exc:
            raise RuntimeError("Install gdown to download Google Drive folders.") from exc

        logger.info("Downloading PDFs from Google Drive folder into %s", self.pdf_dir)
        gdown.download_folder(
            url=folder_url,
            output=str(self.pdf_dir),
            quiet=False,
            use_cookies=False,
        )

    def _download_google_drive_files(self, file_urls: List[str]) -> None:
        try:
            import gdown
        except ImportError as exc:
            raise RuntimeError("Install gdown to download Google Drive files.") from exc

        logger.info("Downloading %s Google Drive PDF files into %s", len(file_urls), self.pdf_dir)
        for index, url in enumerate(file_urls, start=1):
            output_path = self.pdf_dir / f"document_{index}.pdf"
            gdown.download(url=url, output=str(output_path), quiet=False, fuzzy=True)

    def build_vector_database(self) -> None:
        processor = PDFProcessor(str(self.pdf_dir))
        documents = processor.process_all_pdfs()
        if not documents:
            raise RuntimeError(f"No readable PDFs found in {self.pdf_dir}")

        chunker = TextChunker(
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        )
        chunks = chunker.chunk_multiple_documents(documents)
        if not chunks:
            raise RuntimeError("PDF processing finished but produced no text chunks.")

        embedded_chunks = self.embedder.embed_chunks(chunks)
        if not embedded_chunks:
            raise RuntimeError("Embedding generation failed.")

        primary_db = self.databases[0]
        if not primary_db.add_chunks_to_db(embedded_chunks):
            raise RuntimeError("Failed to save chunks into ChromaDB.")

    def retrieve_context(self, query: str, n_results: int = 4) -> List[str]:
        query_embedding = self.embedder.embed_query(query)
        if not query_embedding:
            return []

        docs: List[str] = []
        per_db_results = max(1, n_results // max(1, len(self.databases)))

        for db in self.databases:
            if db.count() == 0:
                continue

            result = db.query(query_embedding, n_results=per_db_results)
            if result and result.get("documents"):
                docs.extend(result["documents"][0])

        return docs[:n_results]

    def ask(self, query: str) -> dict:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Query cannot be empty.")

        context = self.retrieve_context(
            clean_query,
            n_results=int(os.getenv("RAG_TOP_K", "4")),
        )
        if not context:
            return {
                "query": clean_query,
                "answer": "I don't have enough information",
                "sources_found": 0,
            }

        answer = self.llm.generate_answer(clean_query, context[:3])
        return {
            "query": clean_query,
            "answer": answer,
            "sources_found": len(context),
        }
