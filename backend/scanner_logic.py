import socket

def run_network_scan(ip, tool_id):
    # تعريف 30 أداة فحص (منافذ وخدمات)
    tools = {
        # 1-10: الأدوات الأساسية
        1: [80, 21, 23, 8291], 2: [80, 443], 3: [21], 4: [23], 5: [8291],
        6: [8728, 8729], 7: [22], 8: [80], 9: [8080, 9090], 10: [21, 22, 23, 80],
        # 11-20: أدوات الشبكات والخدمات
        11: [53], 12: [110], 13: [143], 14: [161], 15: [445], 16: [3306], 17: [3389], 18: [5432], 19: [6379], 20: [8081],
        # 21-30: أدوات متقدمة واستكشاف
        21: [1194], 22: [5060], 23: [5900], 24: [8000], 25: [8443], 26: [9000], 27: [9200], 28: [27017], 29: [10000], 30: [25565]
    }
    
    # وصف الأدوات (لإظهارها في النتائج)
    descriptions = {
        1: "فحص أساسي", 7: "SSH", 11: "DNS", 14: "SNMP", 16: "MySQL", 
        17: "RDP", 21: "OpenVPN", 23: "VNC", 30: "Minecraft/Game"
    }

    ports = tools.get(tool_id, [80])
    results = []
    
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3) # وقت استجابة سريع
                if s.connect_ex((str(ip), int(port))) == 0:
                    results.append(f"المنفذ {port} مفتوح ومتاح")
        except:
            continue
            
    return results if results else ["لا توجد خدمات نشطة على المنافذ المحددة"]
