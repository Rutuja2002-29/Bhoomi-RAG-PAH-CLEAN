from fastapi import FastAPI
from pydantic import BaseModel
from test_chatbot import SmartAgriChatbot

app = FastAPI()

# chatbot init (once)
chatbot = SmartAgriChatbot()

# request format
class Query(BaseModel):
    query: str

# home route
@app.get("/")
def home():
    return {"message": "Agri Chatbot Running 🚀"}

# chat API
@app.post("/chat")
def chat(q: Query):
    answer = chatbot.generate_response(q.query)
    return {
        "query": q.query,
        "answer": answer
    }