from fastapi import FastAPI, Header, HTTPException
from scanner_logic import run_security_scan

app = FastAPI()

# مفتاح حماية للـ API الخاص بك
API_KEY = "your_secure_key"

@app.post("/scan")
async def trigger_scan(ip: str, user: str, password: str, api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="غير مصرح به")
    
    # تنفيذ الفحص
    results = run_security_scan(ip, user, password)
    return {"status": "success", "data": results}
