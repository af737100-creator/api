from librouteros import connect

def run_security_scan(ip, user, password):
    try:
        api = connect(host=ip, username=user, password=password)
        vulnerabilities = []
        
        # فحص الخدمات
        services = api(cmd='/ip/service/print')
        for s in services:
            if s['name'] in ['telnet', 'ftp', 'www'] and s['disabled'] == 'false':
                vulnerabilities.append(f"خطر: الخدمة {s['name']} مفتوحة")
        
        api.close()
        return vulnerabilities
    except Exception as e:
        return [f"خطأ اتصال: {str(e)}"]
