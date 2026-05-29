from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# استيراد دالة الفحص من ملف scanner_logic
from backend.scanner_logic import run_network_scan

app = FastAPI()

# المسار الرئيسي الذي يعرض واجهة المستخدم (index.html)
@app.get("/")
def read_root():
    # تأكد أن ملف index.html موجود في المجلد الرئيسي للمشروع
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found in root directory"}

# مسار الفحص الذي يستقبل الـ IP ورقم الأداة
@app.get("/scan")
def scan(ip: str, tool_id: int = Query(...)):
    # استدعاء دالة الفحص
    results = run_network_scan(ip, tool_id)
    return {"ip": ip, "tool_id": tool_id, "results": results}

# في حالة أردت إضافة ملفات CSS أو JS إضافية لاحقاً
# app.mount("/static", StaticFiles(directory="static"), name="static")
