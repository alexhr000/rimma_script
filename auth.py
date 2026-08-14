import os
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def load_env(path=".env"):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip("'\"")
    return env


def get_site_config():
    env = load_env()
    login_url = env.get("SITE")
    login = env.get("LOGIN")
    password = env.get("PASSWORD")
    missing = [name for name, value in (
        ("SITE", login_url),
        ("LOGIN", login),
        ("PASSWORD", password),
    ) if not value]
    if missing:
        raise RuntimeError(
            f"В .env не заданы: {', '.join(missing)}. "
            "Нужны SITE, LOGIN, PASSWORD (файл .env не коммитится)."
        )
    parsed = urlparse(login_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return {
        "login_url": login_url,
        "base_url": base_url,
        "login": login,
        "password": password,
    }


def create_chrome_driver():
    """Chrome для Linux-сервера и локальной Windows (Selenium Manager)."""
    env = load_env()
    options = Options()
    options.page_load_strategy = "eager"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    )

    chrome_binary = env.get("CHROME_BINARY")
    if not chrome_binary:
        for candidate in (
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/google-chrome",
        ):
            if os.path.exists(candidate):
                chrome_binary = candidate
                break
    if chrome_binary:
        options.binary_location = chrome_binary

    chromedriver = env.get("CHROMEDRIVER")
    if not chromedriver and os.path.exists("/usr/bin/chromedriver"):
        chromedriver = "/usr/bin/chromedriver"

    # На Windows/без явного chromedriver Selenium Manager подтянет драйвер сам
    if chromedriver:
        service = Service(chromedriver)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)
    return driver


def _is_logged_in(driver):
    if driver.find_elements(By.CSS_SELECTOR, 'a[href*="/user/logout"]'):
        return True
    body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    if "выйти" in body or "log out" in body:
        return True
    return False


def login(driver, logger):
    """Логин в Drupal. Возвращает config. Бросает RuntimeError при неудаче."""
    config = get_site_config()
    login_url = config["login_url"]
    logger.info(f"логин: {config['login']} @ {login_url} (пароль: {len(config['password'])} символов)")

    driver.get(login_url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "edit-submit")))

    # Drupal Antibot: пока JS не отработал, action=/antibot и ключ пустой
    try:
        WebDriverWait(driver, 10).until(
            lambda d: "antibot" not in (
                (d.find_element(By.ID, "user-login-form").get_attribute("action") or "").lower()
            )
        )
    except Exception:
        logger.warning("Antibot action не сменился вовремя — пробуем логин всё равно")

    email_field = driver.find_element(By.ID, "edit-name")
    password_field = driver.find_element(By.ID, "edit-pass")
    email_field.send_keys(Keys.CONTROL, "a")
    email_field.send_keys(Keys.BACKSPACE)
    password_field.send_keys(Keys.CONTROL, "a")
    password_field.send_keys(Keys.BACKSPACE)
    email_field.send_keys(config["login"])
    password_field.send_keys(config["password"])

    # Только обычный click: JS-click / form.submit() ломают Antibot
    driver.find_element(By.ID, "edit-submit").click()

    def login_finished(d):
        if "/user/login" not in d.current_url:
            return True
        if d.find_elements(By.CSS_SELECTOR, ".messages--error, .messages--status, .alert-danger, .messages"):
            return True
        return False

    try:
        WebDriverWait(driver, 20).until(login_finished)
    except Exception:
        pass

    time_url = driver.current_url
    title = driver.title or ""
    error_nodes = driver.find_elements(
        By.CSS_SELECTOR, ".messages--error, .messages--status, .alert-danger, .messages"
    )
    error_text = " | ".join(e.text.strip() for e in error_nodes if e.text.strip())

    if error_text and ("ошиб" in error_text.lower() or "неверн" in error_text.lower() or "invalid" in error_text.lower()):
        raise RuntimeError(f"Ошибка логина: {error_text}")
    if "/user/login" in time_url and not _is_logged_in(driver):
        hint = f" Сообщение сайта: {error_text}" if error_text else ""
        raise RuntimeError(
            f"Логин не выполнен, остались на {time_url}, title={title!r}.{hint} "
            "Проверь LOGIN/PASSWORD в .env в браузере на том же SITE."
        )
    if "запрещ" in title.lower() or "access denied" in title.lower():
        raise RuntimeError(f"После логина доступ запрещён: url={time_url}, title={title!r}")

    driver.get(config["base_url"] + "/user")
    time_url = driver.current_url
    title = driver.title or ""
    if not _is_logged_in(driver) and "/user/login" in time_url:
        raise RuntimeError(
            f"Сессия не создана после логина (url={time_url}, title={title!r}). "
            f"Проверь LOGIN/PASSWORD в .env."
        )

    logger.info(f"логин успешен: url={time_url}, title={title!r}, logged_in={_is_logged_in(driver)}")
    return config
