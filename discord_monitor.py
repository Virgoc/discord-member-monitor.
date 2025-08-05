import os
import json
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
HEADERS = {
    "Authorization": DISCORD_TOKEN,
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

MEMBERS_FILE = "members.json"

def load_saved_members():
    try:
        with open(MEMBERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_members(data):
    with open(MEMBERS_FILE, "w") as f:
        json.dump(data, f)

def send_to_webhook(message):
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Webhook send error: {e}")

def get_guilds():
    r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=HEADERS)
    return r.json()

def get_guild_members(guild_id):
    r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000", headers=HEADERS)
    if r.status_code == 200:
        return [member['user']['id'] for member in r.json()]
    return []

def main():
    saved_members = load_saved_members()
    guilds = get_guilds()

    updated_members = {}

    for guild in guilds:
        guild_id = guild['id']
        current_members = get_guild_members(guild_id)
        previous_members = saved_members.get(guild_id, [])

        # Detect new members
        new_members = set(current_members) - set(previous_members)

        for member_id in new_members:
            send_to_webhook(f"New member joined guild {guild_id}: User ID {member_id}")

        updated_members[guild_id] = current_members

    save_members(updated_members)

if __name__ == "__main__":
    if not DISCORD_TOKEN or not WEBHOOK_URL:
        print("Missing environment variables.")
    else:
        main()
