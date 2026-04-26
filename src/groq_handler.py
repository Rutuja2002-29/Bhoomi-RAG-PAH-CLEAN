"""
Groq LLM Handler (FAST + DETAILED + ACCURATE)
"""

from typing import List, Union, Dict
from groq import Groq
import os
from dotenv import load_dotenv


class GroqHandler:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in .env file!")

        self.client = Groq(api_key=api_key)

        # ✅ UPDATED MODEL (WORKING + FAST)
        self.model = "llama-3.1-8b-instant"

        print(f"✅ Groq initialized with model: {self.model}")

    def create_prompt(self, question: str, context_chunks: List[Union[str, Dict]]) -> str:
        processed_chunks = []

        for chunk in context_chunks:
            if isinstance(chunk, str):
                processed_chunks.append(chunk[:700])  # थोड़ा बड़ा context
            elif isinstance(chunk, dict):
                text = chunk.get("text", "")
                processed_chunks.append(text[:700])

        # ✅ 3 chunks for better answer
        context_text = "\n\n".join(processed_chunks[:3])

        prompt = f"""
You are an expert in rice agriculture.

Answer the question using ONLY the given context.

Context:
{context_text}

Question:
{question}

Instructions:
- Give clear and detailed answer (5-8 lines)
- Use simple language
- Do not guess
- If not found, say: "I don't have enough information"

Answer:
"""
        return prompt

    def generate_answer(self, question: str, context_chunks: List[Union[str, Dict]]) -> str:
        try:
            prompt = self.create_prompt(question, context_chunks)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,     # ✅ balanced detail
                temperature=0.3     # ✅ accuracy + natural
            )

            answer = response.choices[0].message.content

            return answer.strip()

        except Exception as e:
            return f"❌ Error generating answer: {e}"


# TEST
if __name__ == "__main__":
    handler = GroqHandler()

    test_context = [
        "Rice blast is a fungal disease affecting rice crops.",
        "It causes lesions on leaves and reduces yield.",
        "It spreads in humid conditions."
    ]

    question = "What is rice blast disease?"

    print(handler.generate_answer(question, test_context))