from fastapi import FastAPI
from scanner_logic import run_security_scan

app = FastAPI()

@app.get("/scan")
def scan(ip: str, user: str, password: str):
    # يقوم باستدعاء المنطق وإرجاع النتيجة مباشرة دون حفظها في قاعدة بيانات
    return {"results": run_security_scan(ip, user, password)}
