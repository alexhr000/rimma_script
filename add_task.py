from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options



def add_task(body_value,field_place_value, floor_result, building_result,logger):
    try:
        options = Options()
        options.binary_location = "/usr/bin/chromium-browser"  
        options.add_argument("--headless")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        proxy = "gw.dataimpulse.com:823"

        # options.add_argument(f"--proxy-server={proxy}")
        service = Service("/usr/bin/chromedriver")  
        driver = webdriver.Chrome(service=service, options=options)

        logger.info('пытаюсь зайти на сайт, что бы отправить новую заявку')

        driver.get('https://engir.by/user/login')
        logger.info('зашел на сайт, что бы отправить новую заявку')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "edit-submit")))

        email_field = driver.find_element(By.ID, 'edit-name')
        email_field.send_keys('help@wbx.by')

        password_field = driver.find_element(By.ID, 'edit-pass')
        password_field.send_keys('4?Zm9y!U/c-2_6yv')

        submit_button = driver.find_element(By.ID, 'edit-submit')
        submit_button.click()

        time.sleep(5)
        driver.get('https://engir.by/apply')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "edit-submit")))

        time.sleep(3)
        try:
            cancel_review_button = driver.find_element(By.CLASS_NAME, 'cancel-review-button')
            cancel_review_button.click()  # Клик по кнопке "Нет, не сейчас"
            logger.info("Всплывающее окно закрыто")
        except:
            logger.info("Всплывающее окно не найдено")

        time.sleep(3)
        description_field = driver.find_element(By.ID, 'edit-body')
        description_field.send_keys(body_value)

        place_field = driver.find_element(By.ID, 'edit-place')
        place_field.send_keys(field_place_value)




        dropdown_button = driver.find_element(By.CSS_SELECTOR, '.dropdown-toggle[data-id="edit-building"]')
        # dropdown_button.click()
        driver.execute_script("arguments[0].click();", dropdown_button)
        
        # Ожидаем появления элементов в выпадающем списке
        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.dropdown-menu.inner li a span.text'))
        )

        logger.info(f"Найдено {len(options)} элементов в списке.")
        
        # Переменная для отслеживания найденного элемента
        target_found = False


        for option in options:
            # logger.info(f"Проверяется элемент с текстом: {option.text.strip()}")
            if option.text.strip() == building_result:
                logger.info(f"Элемент {building_result} найден. Кликаем по нему.")
                option.click()
                target_found = True
                break

        # Если элемент с текстом "Левкова 24" не найден, кликаем по первому элементу
        if not target_found:
            logger.info(f"Элемент {building_result} не найден. Кликаем по первому элементу.")
            if options:
                options[0].click()
            else:
                logger.info("Список пуст!")





        dropdown_button = driver.find_element(By.CSS_SELECTOR, '.dropdown-toggle[data-id="edit-floor"]')
        # dropdown_button.click()
        driver.execute_script("arguments[0].click();", dropdown_button)
        
        # Ожидаем появления элементов в выпадающем списке
        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.dropdown-menu.inner li a span.text'))
        )

        logger.info(f"Найдено {len(options)} элементов в списке.")
        
        # Переменная для отслеживания найденного элемента
        target_found = False


        for option in options:
            # logger.info(f"Проверяется элемент с текстом: {option.text.strip()}")
            if option.text.strip() == floor_result:
                logger.info(f"Элемент {floor_result} найден. Кликаем по нему.")
                option.click()
                target_found = True
                break

        # Если элемент с текстом "Левкова 24" не найден, кликаем по первому элементу
        if not target_found:
            logger.info(f"Элемент {floor_result} не найден. Кликаем по первому элементу.")
            if options:
                options[0].click()
            else:
                logger.info("Список пуст!")

        # Отправка формы
        submit_button = driver.find_element(By.ID, 'edit-submit')
        submit_button.click()
        time.sleep(5)

    except Exception as e:
        logger.info(f"Ошибка: {e}")
    finally:
        if driver:
            driver.quit()
        else:
            logger.info("Драйвер не был инициализирован.")

# add_task('body_value','field_place_value', '1','Левкова 24')