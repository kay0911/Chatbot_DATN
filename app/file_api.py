from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import os

router = APIRouter()
BASE_PATH = Path("data/knowledge_base")
SUPPORTED_EXT = [".txt", ".pdf", ".docx", ".csv"]

# Lấy nội dung sample.txt
@router.get("/files/sample")
def get_sample_txt():
    sample_path = BASE_PATH / "sample.txt"
    if not sample_path.exists():
        return {"content": ""}
    return {"content": sample_path.read_text(encoding="utf-8")}

# Ghi nội dung mới vào sample.txt
@router.post("/files/sample")
def update_sample_txt(content: str):
    sample_path = BASE_PATH / "sample.txt"
    sample_path.write_text(content, encoding="utf-8")
    return {"message": "Đã lưu nội dung sample.txt."}

# Danh sách các file đã upload (ngoại trừ sample.txt)
@router.get("/files/list")
def list_files():
    files = [f.name for f in BASE_PATH.iterdir() if f.is_file() and f.name != "sample.txt"]
    return {"files": files}

# Upload file
@router.post("/files/upload")
def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(status_code=400, detail="Định dạng không hỗ trợ.")
    
    save_path = BASE_PATH / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"Đã upload {file.filename}"}

# Xoá file
@router.delete("/files/delete/{filename}")
def delete_file(filename: str):
    file_path = BASE_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file.")
    if filename == "sample.txt":
        raise HTTPException(status_code=403, detail="Không được xóa sample.txt.")
    file_path.unlink()
    return {"message": f"Đã xoá {filename}"}

# Cập nhật retriever
from app.chatbot import update_vectorstore

@router.post("/files/update_retriever")
def retrain_retriever():
    update_vectorstore()
    return {"message": "Đã cập nhật retriever thành công."}
