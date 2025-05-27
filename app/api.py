from fastapi import APIRouter, Request
from app.chatbot import generate_response, update_vectorstore
from app.database import chat_history_collection
import requests
from app.config import FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
import time

router = APIRouter()

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    reply = generate_response(user_message)
    return {"reply": reply}

@router.post("/update_retriever")
async def update_retriever_api():
    update_vectorstore()
    return {"message": "Retriever updated successfully"}


@router.get("/fb/messages")
def get_recent_messages():
    messages = chat_history_collection.find().sort("timestamp", -1).limit(10)
    return [
        {
            "sender_id": msg["sender_id"],
            "message": msg["message"],
            "reply": msg["reply"],
            "timestamp": msg.get("timestamp")
        } for msg in messages
    ]

@router.post("/fb/reply")
def reply_to_user(data: dict):
    sender_id = data["sender_id"]
    message = data["message"]

    send_url = f"https://graph.facebook.com/v22.0/{FB_PAGE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {FB_PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
        }
    res = requests.post(send_url, json={
        "recipient": {"id": sender_id},
        "message": {"text": message}
    }, headers=headers)
    # chat_history_collection.insert_one({
    #     "sender_id": sender_id,
    #     "message": '',
    #     "reply": message,
    #     "timestamp": int(time.time() * 1000)
    # })
    
    return {"status": "sent", "fb_response": res.json()}
