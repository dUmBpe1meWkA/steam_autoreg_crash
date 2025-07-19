import os
import string
import time
import imaplib
import email
import re
import numpy as np
import bezier
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
import time
from selenium.webdriver.common.action_chains import ActionChains
import random

STEAM_JOIN_URL = "https://store.steampowered.com/join"
IMAP_HOST = "mail.steamcode.ru"
IMAP_PORT = 993


def human_like_mouse_move(driver, start_element, target_element, steps=30):
    def get_element_center(el):
        loc = el.location_once_scrolled_into_view
        size = el.size
        return loc['x'] + size['width'] / 2, loc['y'] + size['height'] / 2

    x1, y1 = get_element_center(start_element)
    x4, y4 = get_element_center(target_element)

    # Генерация контрольных точек
    x2, y2 = x1 + random.randint(50, 150), y1 + random.randint(-100, 100)
    x3, y3 = x4 + random.randint(-150, -50), y4 + random.randint(-100, 100)

    nodes = np.asfortranarray([[x1, x2, x3, x4],
                               [y1, y2, y3, y4]])
    curve = bezier.Curve(nodes, degree=3)

    action = ActionChains(driver)

    # Инициализация – move_to_element
    action.move_to_element(start_element).pause(random.uniform(0.05, 0.1))

    prev_x, prev_y = x1, y1

    for s in np.linspace(0, 1, steps):
        x, y = curve.evaluate(s).flatten()
        dx = x - prev_x
        dy = y - prev_y

        try:
            action.move_by_offset(dx, dy)
        except:
            print("[WARN] Mouse move out of bounds prevented.")
            break

        prev_x, prev_y = x, y
        action.pause(random.uniform(0.01, 0.04))

    action.perform()


def human_typing(element, text, delay=0.1):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.15))


def move_mouse_randomly(driver):
    body = driver.find_element_by_tag_name('body')
    x = random.randint(100, 800)
    y = random.randint(100, 600)
    action = ActionChains(driver)
    action.move_to_element_with_offset(body, x, y)
    action.perform()
    time.sleep(random.uniform(1, 3))


def random_mouse_interactions(driver):
    actions = ActionChains(driver)
    random_position_x = random.randint(100, 800)
    random_position_y = random.randint(100, 600)
    actions.move_by_offset(random_position_x, random_position_y).click().perform()
    time.sleep(random.uniform(1, 2))


def random_sleep(min_delay=1, max_delay=2):
    time.sleep(random.uniform(min_delay, max_delay))


def get_current_ip():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        return ip
    except Exception as e:
        return f"Error fetching IP: {e}"


def random_user_agent():
    chrome_major = random.randint(110, 122)
    chrome_full = f"{chrome_major}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_full} Safari/537.36"


def setup_browser(profile_id):
    print(f"[DEBUG] Setting up browser for profile {profile_id}")
    profile_path = os.path.abspath(f"profiles/profile_{profile_id}")
    os.makedirs(profile_path, exist_ok=True)

    options = uc.ChromeOptions()
    extensions_dir = os.path.abspath("extensions")
    all_extensions = [os.path.join(extensions_dir, name) for name in os.listdir(extensions_dir)]
    extensions_str = ",".join(all_extensions)
    options.add_argument(f"--load-extension={extensions_str}")
    print(f"[DEBUG] Loaded extensions: {extensions_str}")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable AutomationControlled
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1280,800")
    options.add_argument(f"--user-agent={random_user_agent()}")

    options.headless = False  # Disable headless mode

    # Using undetected-chromedriver for bypassing detection
    driver = uc.Chrome(headless=False, options=options)
    from spoof_generator import generate_dynamic_spoof
    spoof_script = generate_dynamic_spoof()

    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": spoof_script
        })
        print("[DEBUG] Spoof.js injected successfully.")
    except Exception as e:
        print(f"[WARN] Failed to inject spoof.js: {e}")

    # options.add_argument("--load-extension=spoof_extension_path")
    return driver


def get_confirmation_link(email_login, email_password):
    print("[IMAP] Checking mail for:", email_login)
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(f"{email_login}@steamcode.ru", email_password)

    mail.select("inbox")

    for _ in range(30):
        result, data = mail.search(None, "ALL")
        mail_ids = data[0].split()
        for num in reversed(mail_ids):
            result, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            if "Steam" in msg.get("From"):
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                match = re.search(r"https://store\.steampowered\.com/account/newaccountverification\?.+", body)
                if match:
                    print("[IMAP] Confirmation link found.")
                    return match.group(0)
        random_sleep(2, 4)

    raise Exception("[IMAP] Confirmation link not found")


def generate_username(email_login):
    base = ''.join(c for c in email_login if c.isalnum())
    while True:
        username = base + str(random.randint(1000, 9999))
        if "steam" not in username.lower():
            return username


def generate_password():
    forbidden_patterns = ["steam", "password", "qwerty", "1234"]
    while True:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choices(chars, k=12))
        lower_pass = password.lower()
        if (
                any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in "!@#$%^&*" for c in password) and
                not any(pat in lower_pass for pat in forbidden_patterns)
        ):
            return password


def generate_dynamic_spoof():
    platform = random.choice(["Win32", "Linux x86_64", "MacIntel"])
    webgl_vendor = random.choice(["Intel Inc.", "NVIDIA", "AMD"])
    renderer = random.choice(["ANGLE", "Intel Iris", "AMD Radeon", "NVIDIA GeForce"])
    ...
    spoof_script = f"""
    Object.defineProperty(navigator, 'platform', {{get: () => '{platform}'}});
    ...
    """
    return spoof_script


def register_account(email_login, email_pass, profile_id):
    full_email = f"{email_login}@steamcode.ru"
    ip = get_current_ip()
    print(f"[+] Registering {email_login} | Current IP: {ip}")
    browser = setup_browser(profile_id)

    browser.get(STEAM_JOIN_URL)
    browser.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    browser.delete_all_cookies()

    # Ввод email
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'email')))
    email_input = browser.find_element(By.ID, "email")
    reenter_input = browser.find_element(By.ID, "reenter_email")  # ← восстановить
    human_like_mouse_move(browser, email_input, reenter_input)
    human_typing(email_input, full_email)
    time.sleep(random.uniform(0.5, 1.0))
    human_typing(reenter_input, full_email)

    print("[INFO] Email entered. Moving mouse before captcha.")
    human_like_mouse_move(browser, email_input, reenter_input)
    time.sleep(random.uniform(3, 6))
    input(">>> Press Enter after solving the captcha and ticking the checkbox...")

    # Получаем ссылку подтверждения
    confirm_link = get_confirmation_link(email_login, email_pass)

    print("[INFO] Opening confirmation link in a new tab...")
    browser.execute_script("window.open(arguments[0], '_blank');", confirm_link)

    # Безопасно ждём появления второй вкладки и переключаемся в неё
    WebDriverWait(browser, 10).until(lambda d: len(d.window_handles) > 1)
    browser.switch_to.window(browser.window_handles[-1])

    print("[INFO] Confirmation page opened. Waiting for confirmation page to process...")

    try:
        if len(browser.window_handles) > 1:
            confirm_tab = browser.window_handles[-1]
            main_tab = browser.window_handles[0]

            browser.switch_to.window(confirm_tab)

            # Ждём, пока Steam завершит подтверждение
            WebDriverWait(browser, 10).until(
                lambda d: "createaccount" in d.current_url.lower()
            )
            print("[INFO] Confirmation processed by Steam.")

            time.sleep(random.uniform(1.0, 2.0))  # даём чуть-чуть времени Steam

            browser.close()
            browser.switch_to.window(main_tab)
            print("[INFO] Confirmation tab closed and returned to main.")
        else:
            print("[INFO] Only one tab open. Skipping close step.")
    except Exception as e:
        print(f"[WARN] Error while closing tab or switching: {e}")
        if len(browser.window_handles) > 0:
            browser.switch_to.window(browser.window_handles[0])
            print("[INFO] Forced switch to main tab.")
        else:
            print("[FATAL] No tabs left open!")
            return

    # Ждём форму логина/пароля
    print("[INFO] Waiting for login and password form...")

    try:
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, "accountname")))
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, "password")))
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, "reenter_password")))
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, "createAccountButton")))

        # 🔄 Сохраняем актуальные DOM-элементы после возврата
        account_input = browser.find_element(By.ID, "accountname")
        password_input = browser.find_element(By.ID, "password")
        reenter_pass_input = browser.find_element(By.ID, "reenter_password")
        create_button = browser.find_element(By.ID, "createAccountButton")

    except Exception as e:
        print(f"[ERROR] Failed to load registration form: {e}")
        browser.quit()
        return

    # Генерация логина и пароля
    username = generate_username(email_login)
    password = generate_password()

    # Ввод логина с проверкой
    while True:
        human_like_mouse_move(browser, email_input, reenter_input)
        human_like_mouse_move(browser, password_input, account_input)

        account_input.clear()
        human_typing(account_input, username)
        time.sleep(random.uniform(1.0, 2.0))

        errors = browser.execute_script("""
            return Array.from(document.querySelectorAll(".error")).map(e => e.textContent);
        """)
        if not any("not available" in e.lower() or "not allowed" in e.lower() for e in errors):
            print(f"[INFO] Login accepted: {username}")
            break

        print(f"[WARN] Login {username} rejected. Steam error: {errors}")
        username = generate_username(email_login)

    # Ввод пароля
    # Ввод пароля

    account_input = browser.find_element(By.ID, "accountname")  # добавить это
    password_input = browser.find_element(By.ID, "password")
    reenter_pass_input = browser.find_element(By.ID, "reenter_password")

    human_like_mouse_move(browser, account_input, password_input)
    password_input.clear()
    human_typing(password_input, password)
    time.sleep(random.uniform(0.5, 1.0))

    human_like_mouse_move(browser, password_input, reenter_pass_input)
    reenter_pass_input.clear()
    human_typing(reenter_pass_input, password)
    time.sleep(random.uniform(0.5, 1.0))

    human_like_mouse_move(browser, reenter_pass_input, create_button)
    create_button.click()
    time.sleep(5)

    # Проверка на ошибки после отправки формы
    post_errors = browser.execute_script("""
        return Array.from(document.querySelectorAll(".error")).map(e => e.textContent.toLowerCase());
    """)
    if any("not available" in err or "not allowed" in err or "password" in err for err in post_errors):
        raise Exception("[STEAM ERROR] Error during account creation after form submission: " + "; ".join(post_errors))

    # Сохраняем данные
    filename = f"{email_login}_steam.txt"
    os.makedirs("accounts", exist_ok=True)
    with open(f"accounts/{filename}", "w", encoding="utf-8") as f:
        f.write(f"Email: {full_email}\n")
        f.write(f"EmailPass: {email_pass}\n")
        f.write(f"SteamLogin: {username}\n")
        f.write(f"SteamPass: {password}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")

    print(f"[OK] Account {username} successfully registered.")
    time.sleep(5)
    browser.quit()


def read_accounts(filename="mails.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            accounts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[ERROR] Не удалось прочитать файл с аккаунтами: {e}")

    return accounts


# Add all the previous improvements into your main code
if __name__ == "__main__":
    accounts = read_accounts()
    for i, line in enumerate(accounts):
        browser = None  # ← добавлено
        try:
            parts = line.split(":")
            email_login, email_pass = parts[0], parts[1]
            register_account(email_login, email_pass, profile_id=i)
        except Exception as e:
            print(f"[ERROR] {parts[0]}: {e}")
            if browser:
                try:
                    browser.quit()
                except:
                    pass
