import os
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
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
    url = (driver.current_url or "").lower()
    if "/user/" in url and "/user/login" not in url and "/user/password" not in url:
        return True
    body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    if "выйти" in body or "log out" in body:
        return True
    return False


def _unlock_antibot(driver, logger):
    """Снимает Drupal Antibot и остатки в кэше после удаления модуля."""
    info = driver.execute_script("""
      const form = document.getElementById('user-login-form');
      if (!form) return {found: false};

      const before = form.getAttribute('action') || '';
      let after = before;
      let keySet = false;
      let source = 'none';
      const keyInput = form.querySelector('[name="antibot_key"]');

      try {
        const forms = (window.drupalSettings && drupalSettings.antibot && drupalSettings.antibot.forms) || {};
        const conf = forms['user-login-form'] || forms[form.getAttribute('id')] || null;
        if (conf) {
          if (conf.action) {
            form.setAttribute('action', conf.action);
            after = conf.action;
            source = 'drupalSettings';
          }
          if (keyInput && conf.key) {
            keyInput.value = conf.key;
            keySet = true;
          }
        }
      } catch (e) {}

      if ((after || '').toLowerCase().indexOf('antibot') !== -1) {
        const dataAction = form.getAttribute('data-action')
          || form.getAttribute('data-antibot-action');
        if (dataAction) {
          form.setAttribute('action', dataAction);
          after = dataAction;
          source = source === 'none' ? 'data-action' : source + '+data-action';
        } else {
          form.setAttribute('action', '/user/login');
          after = '/user/login';
          source = source === 'none' ? 'force-/user/login' : source + '+force';
        }
      }

      if (keyInput && !keyInput.value) {
        keyInput.value = 'unlocked';
        keySet = true;
      }

      form.classList.remove('antibot');
      form.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));
      form.dispatchEvent(new Event('touchstart', {bubbles: true}));

      return {
        found: true,
        before: before,
        after: after,
        keySet: keySet,
        source: source,
        hasAntibotKey: !!keyInput
      };
    """)
    logger.info(f"antibot unlock: {info}")
    return info


def _wait_login_result(driver, timeout=20):
    def login_finished(d):
        if "/user/login" not in d.current_url:
            return True
        for sel in (".messages--error", ".messages--status", ".alert-danger"):
            for el in d.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed() and el.text.strip():
                    return True
        return False

    try:
        WebDriverWait(driver, timeout).until(login_finished)
        return True
    except Exception:
        return False


def _submit_login_form(driver, logger):
    """Несколько способов отправки — на серверном headless click иногда молчит."""
    form = driver.find_element(By.ID, "user-login-form")
    submit = driver.find_element(By.ID, "edit-submit")
    password_field = driver.find_element(By.ID, "edit-pass")

    attempts = [
        ("click", lambda: submit.click()),
        ("requestSubmit", lambda: driver.execute_script(
            "arguments[0].requestSubmit(arguments[1]);", form, submit
        )),
        ("ENTER", lambda: password_field.send_keys("\n")),
    ]

    for name, action in attempts:
        if "/user/login" not in driver.current_url:
            logger.info(f"уже ушли с login до попытки {name}")
            return
        logger.info(f"submit попытка: {name}")
        try:
            action()
        except Exception as e:
            logger.warning(f"submit {name} не удался: {e}")
            continue
        if _wait_login_result(driver, timeout=12):
            logger.info(f"submit {name}: страница изменилась")
            return
        logger.warning(f"submit {name}: всё ещё на login")


def login(driver, logger):
    """Логин в Drupal. Возвращает config. Бросает RuntimeError при неудаче."""
    config = get_site_config()
    login_url = config["login_url"]
    logger.info(f"логин: {config['login']} @ {login_url} (пароль: {len(config['password'])} символов)")

    driver.get(login_url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "edit-submit")))

    email_field = driver.find_element(By.ID, "edit-name")
    password_field = driver.find_element(By.ID, "edit-pass")
    # value + input/change events — надёжнее для Drupal на headless
    driver.execute_script(
        """
        const [email, pass, login, password] = arguments;
        email.value = login;
        pass.value = password;
        for (const el of [email, pass]) {
          el.dispatchEvent(new Event('input', {bubbles: true}));
          el.dispatchEvent(new Event('change', {bubbles: true}));
        }
        """,
        email_field,
        password_field,
        config["login"],
        config["password"],
    )

    _unlock_antibot(driver, logger)

    name_len = len(email_field.get_attribute("value") or "")
    pass_len = len(password_field.get_attribute("value") or "")
    logger.info(f"поля перед submit: login_len={name_len}, pass_len={pass_len}")

    _submit_login_form(driver, logger)

    time_url = driver.current_url
    title = driver.title or ""
    error_nodes = driver.find_elements(
        By.CSS_SELECTOR, ".messages--error, .messages--status, .alert-danger"
    )
    error_text = " | ".join(e.text.strip() for e in error_nodes if e.text.strip())
    logger.info(f"после submit: url={time_url}, title={title!r}, messages={error_text!r}")

    if error_text and (
        "ошиб" in error_text.lower()
        or "неверн" in error_text.lower()
        or "invalid" in error_text.lower()
        or "попыток" in error_text.lower()
        or "flood" in error_text.lower()
    ):
        raise RuntimeError(f"Ошибка логина: {error_text}")
    if "/user/login" in time_url and not _is_logged_in(driver):
        hint = f" Сообщение сайта: {error_text}" if error_text else ""
        raise RuntimeError(
            f"Логин не выполнен, остались на {time_url}, title={title!r}.{hint} "
            "Возможна блокировка Drupal Flood по IP сервера "
            "(много неудачных попыток) — подожди или очисти таблицу flood. "
            "Также Clear all caches на /admin/config/development/performance"
        )
    if "запрещ" in title.lower() or "access denied" in title.lower():
        raise RuntimeError(f"После логина доступ запрещён: url={time_url}, title={title!r}")

    driver.get(config["base_url"] + "/user")
    time_url = driver.current_url
    title = driver.title or ""
    if not _is_logged_in(driver) and "/user/login" in time_url:
        raise RuntimeError(
            f"Сессия не создана после логина (url={time_url}, title={title!r}). "
            f"Проверь LOGIN/PASSWORD в .env и кэш Drupal."
        )

    logger.info(f"логин успешен: url={time_url}, title={title!r}, logged_in={_is_logged_in(driver)}")
    return config
