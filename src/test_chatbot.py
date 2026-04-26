"""
Smart Agri Chatbot (AUTO RUN FIXED)
Rice + Wheat
"""

from embeddings import EmbeddingGenerator
from chroma_handler import ChromaDBHandler
from groq_handler import GroqHandler


class SmartAgriChatbot:
    def __init__(self):
        print("\n🚀 Initializing Smart Agri Chatbot...\n")

        self.embedder = EmbeddingGenerator()

        self.rice_db = ChromaDBHandler("rice_crops")
        self.wheat_db = ChromaDBHandler("wheat_crops")

        self.llm = GroqHandler()

        print("\n📊 Database Status:")
        print("Rice DB:", self.rice_db.count())
        print("Wheat DB:", self.wheat_db.count())

        print("\n✅ Chatbot Ready!\n")

    def retrieve_context(self, query: str):
        query = query.lower()
        query_embedding = self.embedder.embed_query(query)

        docs = []

        try:
            if "wheat" in query:
                print("🌾 Searching WHEAT...")
                res = self.wheat_db.query(query_embedding, n_results=4)
                if res and "documents" in res:
                    docs.extend(res["documents"][0])

            elif "rice" in query:
                print("🌾 Searching RICE...")
                res = self.rice_db.query(query_embedding, n_results=4)
                if res and "documents" in res:
                    docs.extend(res["documents"][0])

            else:
                print("🌾 Searching BOTH...")
                r = self.rice_db.query(query_embedding, n_results=2)
                w = self.wheat_db.query(query_embedding, n_results=2)

                if r and "documents" in r:
                    docs.extend(r["documents"][0])

                if w and "documents" in w:
                    docs.extend(w["documents"][0])

        except Exception as e:
            print("⚠️ Error:", e)

        return docs

    def generate_response(self, query):
        docs = self.retrieve_context(query)

        if not docs:
            return "❌ No data found"

        docs = docs[:3]

        return self.llm.generate_answer(query, docs)

    def chat(self):
        print("💬 Ask about Rice & Wheat (type 'exit')\n")

        while True:
            query = input("❓ Your Question: ")

            if query.lower() == "exit":
                break

            print("\n🔍 Searching...\n")

            answer = self.generate_response(query)

            print("\n🧠 Answer:\n", answer)
            print("\n" + "-"*50)


# 🔥 MAIN FIX (IMPORTANT)
if __name__ == "__main__":
    chatbot = SmartAgriChatbot()
    chatbot.chat()