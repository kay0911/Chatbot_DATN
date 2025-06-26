import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sẽ set PORT động
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=4)