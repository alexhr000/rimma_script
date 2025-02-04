import json
import time

from datetime import datetime
from add_task import add_task

# Подключение к базе данных


# Функция для проверки и удаления записей с наступившим "daily_time"
def process_changed_data(file_path,logger):
    try:
        # Чтение данных из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.info(f"Ошибка при чтении файла {file_path}: {e}")
        return

    # Получаем текущее время
    current_time = datetime.now()

    # Новый список данных после удаления записей с наступившим daily_time
    updated_data = []

    # Проверка каждой записи
    for record in data:
        # Парсим строку daily_time в объект datetime
        daily_time = datetime.strptime(record["daily_time"], "%Y-%m-%d %H:%M:%S")

        # Если daily_time наступило, выводим сообщение в логи и не добавляем запись в новый список
        if daily_time <= current_time:
            logger.info(f"Запись с entity_id {record['entity_id']} и body_value '{record['body_value']}' была удалена, так как daily_time {daily_time} наступило.")            
            add_task(record['body_value'], record['field_place_value'], record['floor_result'], record['building_result'],logger)
        else:
            updated_data.append(record)


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

    # if updated_data:
    #     # Перезапись файла с отфильтрованными данными
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         json.dump(updated_data, f, ensure_ascii=False, indent=4)

    #     logger.info(f"Файл {file_path} был обновлен.")
    # else:
    #     logger.info(f"Файл {file_path} не был обновлен.")

# # Указываем путь к файлу
# json_file_path = "changed_data.json"

# while True:
#     process_changed_data(json_file_path)
#     time.sleep(5)


