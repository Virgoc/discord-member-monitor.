import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SELF_TOKEN = os.getenv("SELF_TOKEN")  # Discord self-token from environment variable
WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1401983244173574206/LsvwfguWcPHsBOwUpOV6XdmQ0wqTcBXMjxGy4x0SE9MzIMdyXUg715iUov6J_t5kqzic"
CHECK_INTERVAL = 60  # Time between checks in seconds

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def login_with_token(driver, token):
    driver.get("https://discord.com/channels/@me")
    time.sleep(5)
    script = """
    (() => {
        function login(token) {
            setInterval(() => {
                document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
            }, 50);
            setTimeout(() => { location.reload(); }, 2500);
        }
        login(arguments[0]);
    })();
    """
    driver.execute_script(script, token)
    time.sleep(10)

def get_servers(driver):
    servers = driver.find_elements(By.CSS_SELECTOR, 'nav[aria-label="Servers"] a')
    server_data = []
    for s in servers:
        name = s.get_attribute("aria-label")
        href = s.get_attribute("href")
        server_data.append({"name": name, "href": href, "element": s})
    return server_data

def open_member_list(driver):
    try:
        member_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Show Member List"]')
        if member_button:
            member_button.click()
            time.sleep(3)
            return True
    except:
        pass
    return False

def scrape_members(driver):
    members = set()
    try:
        member_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"] div[class*="username"]')
        for el in member_elements:
            username = el.text.strip()
            if username:
                members.add(username)
    except:
        pass
    return members

def send_webhook_alert(server_name, new_members):
    content = f"**New members joined server:** {server_name}\n"
    content += "\n".join(f"- {member}" for member in new_members)
    data = {
        "content": content
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Failed to send webhook: {e}")

def main():
    driver = setup_driver()
    login_with_token(driver, SELF_TOKEN)
    time.sleep(10)

    previous_members = dict()

    while True:
        servers = get_servers(driver)
        for server in servers:
            try:
                driver.get(server["href"])
                time.sleep(5)
                if not open_member_list(driver):
                    print(f"Could not open member list for server: {server['name']}")
                    continue
                current_members = scrape_members(driver)
                old_members = previous_members.get(server["name"], set())
                new_joined = current_members - old_members
                if new_joined:
                    send_webhook_alert(server["name"], new_joined)
                previous_members[server["name"]] = current_members
                time.sleep(3)
            except Exception as e:
                print(f"Error processing server {server['name']}: {e}")

        print("Cycle complete. Waiting for next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
