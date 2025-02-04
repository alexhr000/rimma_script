import json
import time
from daily_check import process_changed_data
from load_task import check_task_list, chek_daily
from logger import setup_logger,send_to_telegram

logger = setup_logger()

def append_json(file_path, data):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(data)
    logger.info(data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)


def remove_zero_field_done_value(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.info(f"Файл {file_path} не существует или пуст.")
        return

    filtered_data = [record for record in data if record["daily_time"] is not None and record["field_done_value"] != 0]

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)

    logger.info(f"Записи с 'field_done_value': 0 удалены из {file_path}.")

def main():
    while True:
        try:
            check_task_list(logger)
            chek_daily(logger)
            process_changed_data("changed_data.json",logger)
            time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Программа остановлена пользователем.")
            break

if __name__ == "__main__":
    main()