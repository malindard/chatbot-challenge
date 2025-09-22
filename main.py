from fastapi import FastAPI
from pydantic import BaseModel
from app.chatbot import run_chat

app = FastAPI(title="Fashion Store Chatbot")

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    reply = run_chat(req.session_id, req.message)
    return {"reply": reply}

@app.get('/')
def root():
    return {"status": "ok", "info": "Synapsis Fashion Store Chatbot API aktif!"}