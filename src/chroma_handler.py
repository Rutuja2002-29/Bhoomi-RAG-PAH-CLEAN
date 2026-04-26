"""
Chroma DB Handler (FINAL STABLE VERSION)
- Batch insert fix
- Persistent DB
- Unique IDs
"""

import chromadb
from typing import List, Dict
import uuid


class ChromaDBHandler:
    def __init__(self, collection_name: str = "default"):
        print("\n🔄 Initializing ChromaDB...")

        # ✅ Persistent DB
        self.client = chromadb.PersistentClient(
            path="C:/Bhoomi-RAG-PAH/chroma_data"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        print(f"✅ Connected to collection: {collection_name}")

    def add_chunks_to_db(self, chunks: List[Dict]) -> bool:
        if not chunks:
            print("❌ No chunks to add!")
            return False

        print(f"\n📥 Adding {len(chunks)} chunks...")

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
                        "source": chunk.get("filename", "unknown"),
                        "path": chunk.get("filepath", "unknown")
                    })

                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=metadatas
                )

                print(f"✅ Batch {(i // batch_size) + 1} added")

            print("🎉 All data stored successfully!")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def query(self, query_embedding, n_results=3):
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        except Exception as e:
            print(f"❌ Query error: {e}")
            return None

    def count(self):
        try:
            return self.collection.count()
        except:
            return 0