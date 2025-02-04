import requests
import subprocess

APP_NAME = "app"
URL = "167.172.38.252"  # Измени на свой URL

def check_pm2():
    result = subprocess.run(["pm2", "status", APP_NAME], capture_output=True, text=True)
    return "online" in result.stdout

def check_http():
    try:
        response = requests.get(URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if not check_pm2():
    print(f"❌ {APP_NAME} упал! Перезапускаем...")
    # subprocess.run(["pm2", "restart", APP_NAME])
else:
    print("Живой!")

if not check_http():
    print(f"⚠️ {URL} недоступен! Проверь сервер.")
