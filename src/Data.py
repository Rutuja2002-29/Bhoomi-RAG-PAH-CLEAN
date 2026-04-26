"""
Add More PDFs to Existing Chroma DB
Without deleting old data - append mode
"""

from pdf_processor import PDFProcessor
from chunking_handler import TextChunker
from embeddings import EmbeddingGenerator
from chroma_handler import ChromaDBHandler
import os


def add_more_pdfs(pdf_folder_path: str, collection_name: str = "rice_crops"):
    """
    Add new PDFs to existing Chroma DB
    """

    print("\n" + "=" * 70)
    print("📥 ADDING MORE PDFs TO EXISTING CHROMA DB")
    print("=" * 70)

    # ✅ Validate path
    if not os.path.exists(pdf_folder_path):
        print(f"❌ Path does not exist: {pdf_folder_path}")
        return False

    # Step 1: Extract PDFs
    print(f"\n[1/4] Extracting PDFs from: {pdf_folder_path}")
    processor = PDFProcessor(pdf_folder_path)
    new_docs = processor.process_all_pdfs()

    if not new_docs:
        print("❌ No PDFs found in this folder!")
        return False

    print(f"✅ Extracted {len(new_docs)} document(s)")

    # Step 2: Chunk
    print("\n[2/4] Chunking text...")
    chunker = TextChunker(chunk_size=800, overlap=100)
    new_chunks = chunker.chunk_multiple_documents(new_docs)
    chunker.print_chunk_stats(new_chunks)

    if not new_chunks:
        print("❌ Chunking failed!")
        return False

    # Step 3: Embedding
    print("\n[3/4] Creating embeddings...")
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    embedded_chunks = embedder.embed_chunks(new_chunks)

    if not embedded_chunks:
        print("❌ Embedding failed!")
        return False

    # Step 4: Store in Chroma DB
    print(f"\n[4/4] Adding to Chroma DB (collection: {collection_name})...")
    chroma = ChromaDBHandler(collection_name=collection_name)

    chunks_before = chroma.collection.count()
    print(f"\n📊 Before: {chunks_before} chunks")

    success = chroma.add_chunks_to_db(embedded_chunks)

    if success:
        chunks_after = chroma.collection.count()
        print(f"\n📊 After: {chunks_after} chunks")
        print(f"✅ Added {chunks_after - chunks_before} new chunks!")
        return True
    else:
        print("❌ Failed to add chunks!")
        return False


# 🔧 MAIN EXECUTION
if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("🌾 ADD MORE DATA TO RAG SYSTEM")
    print("=" * 70)

    print("\nEnter FULL folder path containing PDFs")
    print("Example: C:\\Bhoomi-RAG-PAH\\DATA\\RICE\\Diseases")

    pdf_folder = input("\n📁 PDF Folder Path: ").strip()

    if not pdf_folder:
        print("❌ No path provided!")
        sys.exit(1)

    print("\nWhich collection to add to?")
    print("1. rice_crops")
    print("2. wheat_crops")
    print("3. maize_crops")
    print("4. custom name")

    choice = input("\nEnter choice (1-4): ").strip() or "1"

    collection_mapping = {
        "1": "rice_crops",
        "2": "wheat_crops",
        "3": "maize_crops"
    }

    if choice in collection_mapping:
        collection_name = collection_mapping[choice]
    else:
        collection_name = input("Enter custom collection name: ").strip() or "rice_crops"

    success = add_more_pdfs(pdf_folder, collection_name)

    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Data added to Chroma DB")
        print("=" * 70)
        print("\n👉 Now run chatbot:")
        print("python test_chatbot.py")
    else:
        print("\n❌ Failed to add data!")