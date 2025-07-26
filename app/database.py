from pymongo import MongoClient
from app.config import MONGODB_URI, DATABASE_NAME

MONGO_URI = MONGODB_URI
DB_NAME = DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
chat_history_collection = db["chat_fb_history"]  # Để dùng cho tin nhắn fb
data_collection = db["memory"]