from fastapi import FastAPI
from app.api import router as api_router
from app.facebook_webhook import router as fb_router
from app.file_api import router as file_router
app = FastAPI(title="Chatbot Shop API")

app.include_router(api_router)
app.include_router(fb_router)
app.include_router(file_router, prefix="/api")