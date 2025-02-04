# import json
# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from datetime import datetime, timedelta
# from load_task import calculate_next_occurrence
# from logger import send_to_telegram, setup_logger

# options = Options()
# options.binary_location = "/usr/bin/chromium-browser"  # Путь к Chromium
# options.add_argument("--headless")  # Запуск без GUI
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# proxy = "gw.dataimpulse.com:823"

# options.add_argument(f"--proxy-server={proxy}")
# service = Service("/usr/bin/chromedriver")  # Путь к ChromeDriver
# driver = webdriver.Chrome(service=service, options=options)

# logger = setup_logger()
# try:
#         # Настройка веб-драйвера
#         logger.info('пытаюсь зайти на сайт')
    
#         driver.get('https://engir.by/user/login')
#         logger.info('зашел на сайт')
#         time.sleep(5)

#         email_field = driver.find_element(By.ID, 'edit-name')
#         email_field.send_keys('help@wbx.by')

#         password_field = driver.find_element(By.ID, 'edit-pass')
#         password_field.send_keys('4?Zm9y!U/c-2_6yv')

#         submit_button = driver.find_element(By.ID, 'edit-submit')
#         submit_button.click()

#         time.sleep(5)
#         driver.get('https://engir.by/eam')
#         logger.info('зашел в eam')
#         time.sleep(10)
#         entity_ids = driver.find_elements(By.XPATH, '//*[@headers="view-field-serial-table-column"]')
#         body_values = driver.find_elements(By.XPATH, '//*[@headers="view-body-table-column"]')
#         building_results = driver.find_elements(By.XPATH, '//*[@headers="view-field-building-table-column"]')
#         floor_results = driver.find_elements(By.XPATH, '//*[@headers="view-field-floor-table-column"]')
#         place_results = driver.find_elements(By.XPATH, '//input[@data-drupal-selector="edit-field-place-0-value"]')
#         field_done_results = driver.find_elements(By.XPATH, '//input[@data-drupal-selector="edit-field-done-value"]')

#         min_length = min(len(body_values), len(building_results), len(place_results))

#         data = []
#         for i in range(min_length):
#             field_done_value = 1 if field_done_results[i].is_selected() else 0

#             daily_time = calculate_next_occurrence(body_values[i].text.strip())

#             if daily_time:
#                 timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + daily_time
#                 daily_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
#             else:
#                 daily_time = None

#             data.append({
#                 "entity_id": entity_ids[i].text.strip(),
#                 "body_value": body_values[i].text.strip(),
#                 "building_result": building_results[i].text.strip().split("\n")[-1],
#                 "floor_result": floor_results[i].text.strip().split("\n")[-1],
#                 "field_place_value": place_results[i].get_attribute("value"),
#                 "field_done_value": field_done_value,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "daily_time": daily_time,
#             })

#         # Загружаем старые данные
#         old_data = []
#         if os.path.exists("output.json"):
#             with open("output.json", "r", encoding="utf-8") as f:
#                 old_data = json.load(f)

#         old_data_dict = {item["entity_id"]: item for item in old_data}
#         new_data_dict = {item["entity_id"]: item for item in data}

#         has_changes = False
#         new_entries = []

#         # Проверяем изменения
#         for entity_id, new_item in new_data_dict.items():
#             if entity_id not in old_data_dict:
#                 # Новая заявка (отправляем в Telegram)
#                 new_entries.append(new_item)
#                 has_changes = True
#             else:
#                 old_item = old_data_dict[entity_id]
#                 if old_item["field_done_value"] != new_item["field_done_value"]:
#                     # Изменение field_done_value (не отправляем в Telegram)
#                     has_changes = True

#         # Если есть изменения, перезаписываем output.json
#         if has_changes:
#             with open("output.json", "w", encoding="utf-8") as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)
#             logger.info("Файл output.json обновлен.")

#         # Отправляем сообщения только для новых заявок
#         for item in new_entries:
#             msg = (
#                 f"<b>Новая заявка на обслуживание! </b>\n"
#                 f"<b>Описание: </b>{item['body_value']}\n"
#                 f"<b>Место: </b>{item['field_place_value']}\n"
#                 f"<b>Этаж: </b>{item['floor_result']}\n"
#                 f"<b>Здание: </b>{item['building_result']}"
#             )
#             # send_to_telegram(msg)
#             logger.info(msg)

#         if new_entries:
#             logger.info(f"Добавлено {len(new_entries)} новых записей и отправлено в Telegram.")
#         else:
#             logger.info("Новых записей не обнаружено.")

# except Exception as e:
#     logger.error(f"Ошибка: {e}")
# finally:
#     if driver:
#         driver.quit()
#     else:
#         logger.info("Драйвер не был инициализирован.")



import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from load_task import calculate_next_occurrence
from logger import send_to_telegram, setup_logger

options = Options()
options.binary_location = "/usr/bin/chromium-browser"  # Путь к Chromium
options.add_argument("--headless")  # Запуск без GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
proxy = "gw.dataimpulse.com:823"

options.add_argument(f"--proxy-server={proxy}")
service = Service("/usr/bin/chromedriver")  # Путь к ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

logger = setup_logger()
try:
        # Настройка веб-драйвера
        logger.info('пытаюсь зайти на сайт')
    
        driver.get('https://engir.by/user/login')
        logger.info('зашел на сайт')
        time.sleep(5)

        email_field = driver.find_element(By.ID, 'edit-name')
        email_field.send_keys('help@wbx.by')

        password_field = driver.find_element(By.ID, 'edit-pass')
        password_field.send_keys('4?Zm9y!U/c-2_6yv')

        submit_button = driver.find_element(By.ID, 'edit-submit')
        submit_button.click()

        time.sleep(5)
        driver.get('https://engir.by/eam')
        logger.info('зашел в eam')
        time.sleep(10)
        entity_ids = driver.find_elements(By.XPATH, '//*[@headers="view-field-serial-table-column"]')
        body_values = driver.find_elements(By.XPATH, '//*[@headers="view-body-table-column"]')
        building_results = driver.find_elements(By.XPATH, '//*[@headers="view-field-building-table-column"]')
        floor_results = driver.find_elements(By.XPATH, '//*[@headers="view-field-floor-table-column"]')
        place_results = driver.find_elements(By.XPATH, '//input[@data-drupal-selector="edit-field-place-0-value"]')
        field_done_results = driver.find_elements(By.XPATH, '//input[@data-drupal-selector="edit-field-done-value"]')

        min_length = min(len(body_values), len(building_results), len(place_results))

        data = []
        for i in range(min_length):
            field_done_value = 1 if field_done_results[i].is_selected() else 0

            daily_time = calculate_next_occurrence(body_values[i].text.strip())

            if daily_time:
                timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + daily_time
                daily_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                daily_time = None

            data.append({
                "entity_id": entity_ids[i].text.strip(),
                "body_value": body_values[i].text.strip(),
                "building_result": building_results[i].text.strip().split("\n")[-1],
                "floor_result": floor_results[i].text.strip().split("\n")[-1],
                "field_place_value": place_results[i].get_attribute("value"),
                "field_done_value": field_done_value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "daily_time": daily_time,
            })

        # Загружаем старые данные
        old_data = []
        if os.path.exists("output.json"):
            with open("output.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)

        old_data_dict = {item["entity_id"]: item for item in old_data}
        new_data_dict = {item["entity_id"]: item for item in data}

        has_changes = False
        new_entries = []

        # Проверяем изменения
        for entity_id, new_item in new_data_dict.items():
            if entity_id not in old_data_dict:
                # Новая заявка (отправляем в Telegram)
                new_entries.append(new_item)
                has_changes = True
            else:
                old_item = old_data_dict[entity_id]
                if old_item["field_done_value"] != new_item["field_done_value"]:
                    # Изменение field_done_value (не отправляем в Telegram)
                    has_changes = True

        # Если есть изменения, перезаписываем output.json
        if has_changes:
            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info("Файл output.json обновлен.")

        # Отправляем сообщения только для новых заявок
        for item in new_entries:
            msg = (
                f"<b>Новая заявка на обслуживание! </b>\n"
                f"<b>Описание: </b>{item['body_value']}\n"
                f"<b>Место: </b>{item['field_place_value']}\n"
                f"<b>Этаж: </b>{item['floor_result']}\n"
                f"<b>Здание: </b>{item['building_result']}"
            )
            # send_to_telegram(msg)
            logger.info(msg)

        if new_entries:
            logger.info(f"Добавлено {len(new_entries)} новых записей и отправлено в Telegram.")
        else:
            logger.info("Новых записей не обнаружено.")

except Exception as e:
    logger.error(f"Ошибка: {e}")
finally:
    if driver:
        driver.quit()
    else:
        logger.info("Драйвер не был инициализирован.")