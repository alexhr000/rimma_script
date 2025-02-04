import json
import os
from driver import get_driver
from logger import setup_logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from logger import setup_logger,send_to_telegram


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def calculate_next_occurrence(body_value):
    if "повторять каждый месяц" in body_value:
        return timedelta(days=30)
    elif "повторять каждые 3 месяца" in body_value:
        return timedelta(days=90) 
    elif "повторять каждые 6 месяцев" in body_value:
        return timedelta(days=180)  
    elif "повторять каждые 12 месяцев" in body_value:
        return timedelta(days=365)  
    elif "повторять каждую минуту" in body_value:
        return timedelta(minutes=1) 
    else:
        return None  

# def check_task_list(logger):
#     try:
#         driver = get_driver()

#         driver.get('https://engir.by/user/login')
#         # driver.get('https://rimma.fabg.space/user/login')

#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "edit-submit")))

#         email_field = driver.find_element(By.ID, 'edit-name')
#         email_field.send_keys('help@wbx.by')
#         # email_field.send_keys('admin@example.com')

#         password_field = driver.find_element(By.ID, 'edit-pass')
#         password_field.send_keys('4?Zm9y!U/c-2_6yv')
#         # password_field.send_keys('FDBfhsbfjBBFE213bbuYFG2')

#         submit_button = driver.find_element(By.ID, 'edit-submit')
#         submit_button.click()


#         time.sleep(5)
#         driver.get('https://engir.by/eam?building=&applicant=&realwork=&run_eam=All&done_eam=All&created=&changed=&items_per_page=100')
#         time.sleep(5)

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
#                 "field_place_value":  place_results[i].get_attribute("value"),
#                 "field_done_value":  field_done_value,
#                 "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "daily_time":  daily_time,
                
#             })

#         # Проверка на разницу с предыдущим файлом
#         old_data = []
#         if os.path.exists("output.json"):
#             with open("output.json", "r", encoding="utf-8") as f:
#                 old_data = json.load(f)

#         # Сравнение значений body_value
#         old_body_values = {item["entity_id"] for item in old_data}
#         new_body_values = {item["entity_id"] for item in data}

#         changed_data = []

#         if old_body_values != new_body_values:
#             # Если есть различия, перезаписываем файл
#             with open("output.json", "w", encoding="utf-8") as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)

#             # Вызываем функцию send_to_telegram для каждого нового body_value
#             for item in data:
#                 if item["entity_id"] not in old_body_values:
#                     msg = (
#                         f"<b>Новая заявка на обслуживание! </b>\n"
#                         f"<b>Описание: </b>{item["body_value"]}\n"
#                         f"<b>Место: </b>{item["field_place_value"]}\n"
#                         f"<b>Этаж: </b>{item["floor_result"]}\n"
#                         f"<b>Здание: </b>{item["building_result"]}"
#                     )
#                     send_to_telegram(msg)

#         else:
#             logger.info("Изменений в entity_id не обнаружено.")

#     except Exception as e:
#         logger.info(f"Ошибка: {e}")
#     finally:
#         if driver:
#             driver.quit()
#         else:
#             logger.info("Драйвер не был инициализирован.")






def check_task_list(logger):
    try:
        options = Options()
        options.binary_location = "/usr/bin/chromium-browser"  # Путь к Chromium
        options.add_argument("--headless")  # Запуск без GUI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        proxy = "gw.dataimpulse.com:823"

        # options.add_argument(f"--proxy-server={proxy}")
        service = Service("/usr/bin/chromedriver")  # Путь к ChromeDriver
        driver = webdriver.Chrome(service=service, options=options)

        logger.info('пытаюсь зайти на сайт')
    
        driver.get('https://engir.by/user/login')
        logger.info('зашел на сайт')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "edit-submit")))

        email_field = driver.find_element(By.ID, 'edit-name')
        email_field.send_keys('help@wbx.by')

        password_field = driver.find_element(By.ID, 'edit-pass')
        password_field.send_keys('4?Zm9y!U/c-2_6yv')

        submit_button = driver.find_element(By.ID, 'edit-submit')
        submit_button.click()

        time.sleep(5)
        driver.get('https://engir.by/eam')
        logger.info('зашел в eam')
        time.sleep(5)

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
            send_to_telegram(msg)

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








# def chek_daily(logger):
#     output_file = 'output.json'
#     changed_file = 'changed_data.json'
#     messages_file = 'sent_messages.json'
#     try:
#         if not os.path.exists(output_file):
#             raise FileNotFoundError(f"Файл {output_file} не найден.")

#         with open(output_file, "r", encoding="utf-8") as f:
#             output_data = json.load(f)

#         changed_data = []
#         if os.path.exists(changed_file):
#             with open(changed_file, "r", encoding="utf-8") as f:
#                 changed_data = json.load(f)

#         changed_keys = set()
#         for item in changed_data:
#             key = (
#                 item["entity_id"],
#                 item["body_value"],
#                 item["building_result"],
#                 item["floor_result"],
#                 item["field_place_value"],
#             )
#             changed_keys.add(key)

#         new_entries = []
#         for item in output_data:
#             if item["daily_time"] is None or item["field_done_value"] != 1:
#                 continue

#             key = (
#                 item["entity_id"],
#                 item["body_value"],
#                 item["building_result"],
#                 item["floor_result"],
#                 item["field_place_value"],
#             )

#             if key not in changed_keys:
#                 new_entries.append(item)

#         if new_entries:
#             changed_data.extend(new_entries)
#             with open(changed_file, "w", encoding="utf-8") as f:
#                 json.dump(changed_data, f, ensure_ascii=False, indent=4)
#             with open(messages_file, "w", encoding="utf-8") as f:
#                 json.dump(changed_data, f, ensure_ascii=False, indent=4)
#             logger.info(f"Добавлено {len(new_entries)} новых записей в {changed_file}.")
#         else:
#             logger.info("Новых записей для добавления не обнаружено.")

#     except Exception as e:
#         logger.info(f"Произошла ошибка: {e}")


# def chek_daily(logger):
#     output_file = 'output.json'
#     changed_file = 'changed_data.json'
#     messages_file = 'sent_messages.json'

#     try:
#         if not os.path.exists(output_file):
#             raise FileNotFoundError(f"Файл {output_file} не найден.")

#         with open(output_file, "r", encoding="utf-8") as f:
#             output_data = json.load(f)

#         # Загружаем уже измененные данные
#         changed_data = []
#         if os.path.exists(changed_file):
#             with open(changed_file, "r", encoding="utf-8") as f:
#                 changed_data = json.load(f)

#         # Загружаем уже отправленные сообщения
#         sent_messages = set()
#         if os.path.exists(messages_file):
#             with open(messages_file, "r", encoding="utf-8") as f:
#                 try:
#                     sent_data = json.load(f)
#                     sent_messages = {item["entity_id"] for item in sent_data}  # Делаем set() только из entity_id
#                 except json.JSONDecodeError:
#                     sent_messages = set()

#         # Собираем ключи уже обработанных записей (делаем кортежи, а не dict!)
#         changed_keys = {
#             (item["entity_id"], item["body_value"], item["building_result"],
#              item["floor_result"], item["field_place_value"]) 
#             for item in changed_data
#         }

#         new_entries = []
#         for item in output_data:
#             if item["daily_time"] is None or item["field_done_value"] != 1:
#                 continue

#             key = (
#                 item["entity_id"],
#                 item["body_value"],
#                 item["building_result"],
#                 item["floor_result"],
#                 item["field_place_value"],
#             )

#             # Проверяем, если entity_id уже был отправлен, пропускаем его
#             if item["entity_id"] in sent_messages:
#                 continue

#             if key not in changed_keys:
#                 new_entries.append(item)

#         if new_entries:
#             changed_data.extend(new_entries)

#             # Записываем новые данные в changed_data.json
#             with open(changed_file, "w", encoding="utf-8") as f:
#                 json.dump(changed_data, f, ensure_ascii=False, indent=4)

#             # Обновляем список отправленных entity_id
#             sent_messages.update(item["entity_id"] for item in new_entries)
#             with open(messages_file, "w", encoding="utf-8") as f:
#                 json.dump(list(sent_messages), f, ensure_ascii=False, indent=4)

#             logger.info(f"Добавлено {len(new_entries)} новых записей в {changed_file}.")
#         else:
#             logger.info("Новых записей для добавления не обнаружено.")

#     except Exception as e:
#         logger.info(f"Произошла ошибка: {e}")



import os
import json

def chek_daily(logger):
    output_file = 'output.json'
    changed_file = 'changed_data.json'
    messages_file = 'sent_messages.json'

    try:
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Файл {output_file} не найден.")

        with open(output_file, "r", encoding="utf-8") as f:
            output_data = json.load(f)

        # Загружаем уже измененные данные
        changed_data = []
        if os.path.exists(changed_file):
            with open(changed_file, "r", encoding="utf-8") as f:
                changed_data = json.load(f)

        # Загружаем уже отправленные сообщения
        sent_messages = []
        if os.path.exists(messages_file):
            with open(messages_file, "r", encoding="utf-8") as f:
                try:
                    sent_messages = json.load(f)  # Теперь это список словарей
                except json.JSONDecodeError:
                    sent_messages = []

        # Создаем множества для быстрого поиска по entity_id и ключевым полям
        sent_entity_ids = {item["entity_id"] for item in sent_messages}
        changed_keys = {
            (item["entity_id"], item["body_value"], item["building_result"],
             item["floor_result"], item["field_place_value"]) 
            for item in changed_data
        }

        new_entries = []
        for item in output_data:
            if item["daily_time"] is None or item["field_done_value"] != 1:
                continue

            key = (
                item["entity_id"],
                item["body_value"],
                item["building_result"],
                item["floor_result"],
                item["field_place_value"],
            )

            # Проверяем, если entity_id уже был отправлен, пропускаем его
            if item["entity_id"] in sent_entity_ids:
                continue

            if key not in changed_keys:
                new_entries.append(item)

        if new_entries:
            changed_data.extend(new_entries)

            # Записываем новые данные в changed_data.json
            with open(changed_file, "w", encoding="utf-8") as f:
                json.dump(changed_data, f, ensure_ascii=False, indent=4)

            # Обновляем список отправленных сообщений (теперь это список словарей!)
            sent_messages.extend(new_entries)
            with open(messages_file, "w", encoding="utf-8") as f:
                json.dump(sent_messages, f, ensure_ascii=False, indent=4)

            logger.info(f"Добавлено {len(new_entries)} новых записей в {changed_file}.")
        else:
            logger.info("Новых записей для добавления не обнаружено.")

    except Exception as e:
        logger.info(f"Произошла ошибка: {e}")


# logger = setup_logger()
# check_task_list(logger)
# chek_daily(logger)