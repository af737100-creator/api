import socket
import requests

def run_network_scan(ip, tool_id):
    # تعريف المنافذ للأدوات الـ 30
    tools = {
        1: [80, 21, 23, 8291], 2: [80, 443], 3: [21], 4: [23], 5: [8291],
        6: [8728, 8729], 7: [22], 8: [80], 9: [8080, 9090], 10: [21, 22, 23, 80],
        11: [53], 12: [110], 13: [143], 14: [161], 15: [445], 16: [3306], 
        17: [3389], 18: [5432], 19: [6379], 20: [8081], 21: [1194], 
        22: [5060], 23: [5900], 24: [8000], 25: [8443], 26: [9000], 
        27: [9200], 28: [27017], 29: [10000], 30: [25565]
    }
    
    ports = tools.get(tool_id, [80])
    results = []
    
    # محاولة الفحص عبر Socket
    for port in ports:
        try:
            # زيادة وقت الانتظار قليلاً لضمان الاستجابة في الشبكات البطيئة
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5) 
                if s.connect_ex((str(ip), int(port))) == 0:
                    results.append(f"المنفذ {port} مفتوح ومتاح")
        except:
            continue
    
    # إضافة فحص إضافي للمواقع عبر HTTP إذا فشل الـ Socket
    if not results and tool_id in [2, 8]:
        try:
            url = f"http://{ip}"
            response = requests.get(url, timeout=3)
            results.append(f"تم الوصول للخدمة عبر HTTP، رمز الحالة: {response.status_code}")
        except:
            results.append("لم يتم العثور على خدمات نشطة على المنافذ المختارة.")
            
    return results if results else ["لم يتم العثور على خدمات نشطة أو أن الوصول محظور."]
