import requests
import json
from librouteros import connect

# إعدادات الاتصال بالراوتر المحلي
ROUTER_CONFIG = {
    'host': '192.168.88.1',
    'user': 'admin',
    'password': 'yourpassword'
}

# عنوان السيرفر المركزي الخاص بك (الذي رفعناه على Render)
CENTRAL_SERVER_URL = "https://your-api.onrender.com/scan"
API_KEY = "your_secure_key"

def run_agent():
    try:
        # 1. الاتصال بالراوتر
        api = connect(**ROUTER_CONFIG)
        
        # 2. جمع البيانات (نفس منطق الفحص)
        services = api(cmd='/ip/service/print')
        data = {"services": str(services)}
        
        # 3. إرسال النتائج للسيرفر المركزي
        response = requests.post(
            CENTRAL_SERVER_URL, 
            json={"ip": ROUTER_CONFIG['host'], "data": data},
            headers={"api-key": API_KEY}
        )
        print("تم إرسال التقرير للسيرفر:", response.status_code)
        
    except Exception as e:
        print("فشل الفحص:", e)

if __name__ == "__main__":
    run_agent()
