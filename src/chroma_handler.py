"""
Chroma DB Handler (FINAL STABLE VERSION)
- Batch insert fix
- Persistent DB
- Unique IDs
"""

import os
from pathlib import Path
from typing import Dict, List
import logging
import chromadb
import uuid

logger = logging.getLogger(__name__)


class ChromaDBHandler:
    def __init__(self, collection_name: str = "default", persist_path: str | None = None):
        logger.info("Initializing ChromaDB collection '%s'", collection_name)

        db_path = Path(
            persist_path
            or os.getenv("CHROMA_DB_PATH")
            or "chroma_data"
        )
        db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(db_path)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        logger.info("Connected to Chroma collection '%s' at %s", collection_name, db_path)

    def add_chunks_to_db(self, chunks: List[Dict]) -> bool:
        if not chunks:
            logger.warning("No chunks supplied for Chroma insert")
            return False

        logger.info("Adding %s chunks to ChromaDB", len(chunks))

        # 🔥 IMPORTANT: Batch size fix
        batch_size = 4000

        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]

                documents = []
                embeddings = []
                ids = []
                metadatas = []

                for chunk in batch:
                    documents.append(chunk["text"])
                    embeddings.append(chunk["embedding"])

                    # ✅ UNIQUE ID FIX
                    ids.append(str(uuid.uuid4()))

                    metadatas.append({
                        "source": chunk.get("filename") or chunk.get("source", "unknown"),
                        "path": chunk.get("filepath", "unknown")
                    })

                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=metadatas
                )

                logger.info("Added Chroma batch %s", (i // batch_size) + 1)

            logger.info("All chunks stored successfully")
            return True

        except Exception as e:
            logger.exception("Error adding chunks to ChromaDB: %s", e)
            return False

    def query(self, query_embedding, n_results=3):
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        except Exception as e:
            logger.exception("Chroma query error: %s", e)
            return None

    def count(self):
        try:
            return self.collection.count()
        except Exception:
            logger.exception("Unable to count Chroma collection")
            return 0
