import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_webhook(username, user_id, server_name):
    data = {
        "content": f"New member joined **{server_name}**\nUsername: `{username}`\nUser ID: `{user_id}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print("Failed to send webhook:", e)

def get_member_ids(driver):
    members = driver.find_elements(By.CLASS_NAME, 'member-username')
    return [m.text for m in members if m.text]

def login_and_monitor():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://discord.com/login")
    time.sleep(5)

    driver.execute_script(f'''
        window.t = "{DISCORD_TOKEN}";
        localStorage.token = `"${{window.t}}"`;
        location.reload();
    ''')
    time.sleep(8)

    known_ids = set()

    while True:
        try:
            members = get_member_ids(driver)
            for member in members:
                if member not in known_ids:
                    known_ids.add(member)
                    send_webhook(username=member, user_id="N/A", server_name="Joined Server")
            time.sleep(60)
        except Exception as e:
            print("Error during monitoring:", e)
            time.sleep(60)

if __name__ == "__main__":
    login_and_monitor()
