from fastapi import FastAPI
from backend.scanner_logic import run_security_scan

app = FastAPI()

@app.get("/scan")
def scan(ip: str, user: str, password: str):
    # يستدعي منطق الفحص الموجود في الملف الآخر
    return {"results": run_security_scan(ip, user, password)}
