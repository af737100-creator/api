import requests

def perform_scan(target_ip, user, password):
    # يتصل بالـ Backend الخاص بك للحصول على التقرير
    url = f"http://your-server-url/scan?ip={target_ip}&user={user}&password={password}"
    response = requests.get(url)
    return response.json()
