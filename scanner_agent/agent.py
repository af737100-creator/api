import sys
import json
import requests
import socket

def send_scan_report_securely(server_url: str, target_ip: str, user: str, pasw: str):
    headers = {
        "Content-Type": "application/json",
        "X-Agent-Signature": "agent_secure_hmac_signature_token"
    }
    
    # تحويل الحمولة لتكون داخل جسم طلب POST لحماية البيانات الحساسة
    payload = {
        "ip": target_ip,
        "username": user,
        "password": pasw,
        "check_default_credentials": True
    }
    
    try:
        response = requests.post(
            f"{server_url}/scan", 
            json=payload, 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 202:
            print("🚀 [Agent] تم دفع الفحص بنجاح ومعرّف العملية هو:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ [Agent] فشل دفع التقرير: رمز الحالة {response.status_code}")
    except Exception as e:
        print(f"❌ [Agent] حدث خطأ أثناء الاتصال بالسيرفر المركزي: {str(e)}")

if __name__ == "__main__":
    SERVER = "https://your-secured-cloud-api.onrender.com"
    TARGET = "192.168.88.1"
    
    print("🛰️ [Agent] بدء تشغيل الماسح الميداني لميكروتيك...")
    send_scan_report_securely(SERVER, TARGET, "admin", "")
