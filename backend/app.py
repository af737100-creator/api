import os
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# استيراد محرك الفحص المتطور الفعلي لميكروتيك
from backend.scanner_logic import run_mikrotik_deep_scan

app = FastAPI(
    title="محرّك فحص ثغرات MikroTik المتقدّم",
    description="نظام فحص ذكي ومصادق للاتصال والتحقق من قواعد الأمان والثغرات في أجهزة ميكروتيك",
    version="2.0.0"
)

# تفعيل CORS للتوافق مع تطبيقات الويب الحديثة (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# قاعدة بيانات مؤقتة في الذاكرة لتخزين نتائج المسح (لا لحفظ دائم التزاماً بـ No-Persistence)
SCAN_RESULTS_DB: Dict[str, Any] = {}

class ScanRequest(BaseModel):
    ip: str = Field(..., description="عنوان الـ IP للجهاز المستهدف", example="192.168.88.1")
    port: int = Field(8291, description="منفذ الاتصال بـ RouterOS API أو Winbox", example=8291)
    username: Optional[str] = Field("admin", description="اسم مستخدم الراوتر")
    password: Optional[str] = Field("", description="كلمة مرور الراوتر لعمل الفحص المصادق")
    check_default_credentials: bool = Field(True, description="التحقق من بقاء حساب admin بدون كلمة مرور")

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

# مسار الفحص الفعلي والآمن المستجيب لبيانات POST المشفرة
@app.post("/scan", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    SCAN_RESULTS_DB[scan_id] = {
        "scan_id": scan_id,
        "status": "processing",
        "target": request.ip,
        "results": None
    }
    
    # تشغيل الفحص في الخلفية لضمان عدم حدوث Timeout للاتصال
    background_tasks.add_task(
        execute_and_save_scan,
        scan_id=scan_id,
        ip=request.ip,
        port=request.port,
        username=request.username,
        password=request.password,
        check_default_pass=request.check_default_credentials
    )
    
    return {
        "scan_id": scan_id,
        "status": "processing",
        "message": "تم بدء فحص ميكروتيك العميق في الخلفية بنجاح"
    }

# مسار النتائج الذي كان يتصل به تطبيق الموبايل ولكنه مفقود
@app.get("/results")
async def get_all_results():
    """عرض ملخص للعمليات الجارية والمكتملة في السيرفر"""
    return SCAN_RESULTS_DB

@app.get("/results/{scan_id}")
async def get_scan_results(scan_id: str):
    """جلب تفاصيل فحص معين بالكامل برمز المعرف الخاص به"""
    if scan_id not in SCAN_RESULTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="لم يتم العثور على فحص بهذا المعرّف"
        )
    return SCAN_RESULTS_DB[scan_id]

async def execute_and_save_scan(scan_id: str, ip: str, port: int, username: str, password: str, check_default_pass: bool):
    try:
        # استدعاء دالة الفحص العميقة الحقيقية
        scan_report = run_mikrotik_deep_scan(
            ip=ip,
            port=port,
            username=username,
            password=password,
            check_default_pass=check_default_pass
        )
        SCAN_RESULTS_DB[scan_id]["status"] = "completed"
        SCAN_RESULTS_DB[scan_id]["results"] = scan_report
    except Exception as e:
        SCAN_RESULTS_DB[scan_id]["status"] = "failed"
        SCAN_RESULTS_DB[scan_id]["results"] = {
            "error": f"فشل فحص الجهاز بسبب: {str(e)}"
        }
