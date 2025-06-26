# Sử dụng Python base image tối ưu hơn
FROM python:3.10-slim

# Tạo thư mục ứng dụng
WORKDIR /app

# Copy file yêu cầu cài đặt trước để tận dụng cache
COPY requirements.txt .

# Cài đặt pip và thư viện (bản CPU nếu có torch)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Copy thư mục và file chính
COPY app/ app/
COPY data/ data/
COPY run.py .

# Expose cổng
EXPOSE 8000

# Lệnh mặc định khi container chạy
CMD ["python", "run.py"]

