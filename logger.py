import logging
import os
import requests


def _load_env_value(key):
    value = os.environ.get(key)
    if value:
        return value
    env_path = ".env"
    if not os.path.exists(env_path):
        return None
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip().strip("'\"")
    return None


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) 
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def send_to_telegram(message):
    bot_token = _load_env_value("TELEGRAM_BOT_TOKEN")
    chat_id = _load_env_value("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}  
    response = requests.post(url, data=data)
    return response.status_code == 200
