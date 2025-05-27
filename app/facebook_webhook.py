from fastapi import APIRouter, Request
import requests
from app.config import FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
from app.database import chat_history_collection

router = APIRouter()

VERIFY_TOKEN = "650072"

@router.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    return {"error": "Invalid verification token"}

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message_text = messaging.get("message", {}).get("text")

            if not sender_id or not message_text:
                continue

            reply = "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."
            try:
                response = requests.post("http://localhost:8000/chat", json={"message": message_text})
                if response.status_code == 200:
                    reply = response.json().get("reply", reply)
            except Exception as e:
                print(f"Error forwarding to chatbot: {e}")

            send_url = f"https://graph.facebook.com/v22.0/{FB_PAGE_ID}/messages"
            headers = {
                "Authorization": f"Bearer {FB_PAGE_ACCESS_TOKEN}",
                "Content-Type": "application/json"
                }
            requests.post(send_url, json={
                "recipient": {"id": sender_id},
                "message": {"text": reply}
            }, headers=headers)
            chat_history_collection.insert_one({
                "sender_id": sender_id,
                "message": message_text,
                "reply": reply,
                "timestamp": entry.get("time")
            })

    return {"status": "ok"}
