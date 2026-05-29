import json
import os
from librouteros import connect

def run_security_scan(ip, user, password):
    # مسار ملف القواعد (يصعد خطوة واحدة للمجلد الرئيسي ثم يدخل config)
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'security_rules.json')
    
    try:
        # تحميل القواعد
        with open(rules_path, 'r') as f:
            rules = json.load(f)
        
        # الاتصال بالراوتر
        api = connect(host=ip, username=user, password=password)
        vulnerabilities = []
        
        # 1. فحص الخدمات بناءً على القواعد
        if rules['check_settings']['check_services']:
            services = api(cmd='/ip/service/print')
            for s in services:
                if s['name'] in rules['dangerous_services'] and s['disabled'] == 'false':
                    vulnerabilities.append(f"خطر: الخدمة {s['name']} مفتوحة على المنفذ {s['port']}")
        
        # 2. فحص المستخدمين (admin)
        if rules['check_settings']['check_admin_pass']:
            users = api(cmd='/user/print')
            for u in users:
                if u['name'] in rules['critical_users'] and not u.get('password'):
                    vulnerabilities.append("خطر: حساب admin بدون كلمة مرور!")
        
        api.close()
        return vulnerabilities

    except FileNotFoundError:
        return ["خطأ: ملف القواعد security_rules.json غير موجود."]
    except Exception as e:
        return [f"خطأ في الاتصال: {str(e)}"]
