"""
Embedding Generator Module
Creates embeddings for text chunks and queries
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np


class EmbeddingGenerator:
    """
    Handles embedding generation using Sentence Transformers
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model

        Args:
            model_name: Name of the embedding model
        """
        print("\n🔄 Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded: {model_name}")

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for text chunks

        Args:
            chunks: List of text chunks

        Returns:
            Chunks with embeddings added
        """
        if not chunks:
            print("❌ No chunks provided for embedding!")
            return []

        print(f"\n🔢 Generating embeddings for {len(chunks)} chunks...")

        # Extract text from chunks
        texts = []
        for chunk in chunks:
            if "text" in chunk:
                texts.append(chunk["text"])
            else:
                print("⚠️ Missing 'text' key in chunk!")

        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Attach embeddings back to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()

        print("✅ Embeddings created successfully!")

        return chunks

    def embed_query(self, query: str):
        """
        🔥 NEW FUNCTION (FIXES YOUR ERROR)

        Generate embedding for a single query

        Args:
            query: User query string

        Returns:
            Embedding vector
        """
        if not query:
            print("⚠️ Empty query received!")
            return None

        print(f"\n🔍 Creating embedding for query: {query}")

        embedding = self.model.encode([query])[0]

        return embedding.tolist()

    def cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def batch_embed_queries(self, queries: List[str]):
        """
        Generate embeddings for multiple queries

        Args:
            queries: List of query strings

        Returns:
            List of embeddings
        """
        if not queries:
            print("⚠️ No queries provided!")
            return []

        print(f"\n🔍 Generating embeddings for {len(queries)} queries...")

        embeddings = self.model.encode(queries, show_progress_bar=True)

        return [emb.tolist() for emb in embeddings]

    def print_embedding_info(self, embedding):
        """
        Debug helper to inspect embedding

        Args:
            embedding: Vector embedding
        """
        if embedding is None:
            print("❌ No embedding to display")
            return

        print("\n📊 Embedding Info:")
        print(f"Length: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}...")


# 🔧 Testing
if __name__ == "__main__":
    print("\n🚀 Testing Embedding Generator\n")

    embedder = EmbeddingGenerator()

    # Test query embedding
    query = "What is rice blast disease?"
    emb = embedder.embed_query(query)

    embedder.print_embedding_info(emb)

    print("\n✅ Test completed!")