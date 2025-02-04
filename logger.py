import logging
import requests

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
    bot_token = "7464445799:AAEhWqqFpZDyFKA6o9fklAIaguig7yHHpaM"
    chat_id = "-1002479952681"
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}  
    response = requests.post(url, data=data)
    return response.status_code == 200