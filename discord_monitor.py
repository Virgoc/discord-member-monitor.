import os
import json
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATA_FILE = "guild_members.json"

headers = {
    "Authorization": DISCORD_TOKEN,  # User token used as is
    "Content-Type": "application/json"
}

def load_saved_members():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_members(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_guilds():
    url = "https://discord.com/api/v9/users/@me/guilds"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_guild_members(guild_id):
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def send_webhook_message(content):
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except Exception as e:
        print(f"Webhook error: {e}")

def main():
    saved_members = load_saved_members()
    current_members = {}

    guilds = get_guilds()

    for guild in guilds:
        guild_id = guild["id"]
        members = get_guild_members(guild_id)
        current_member_ids = set(member["user"]["id"] for member in members)
        current_members[guild_id] = list(current_member_ids)

        previous_member_ids = set(saved_members.get(guild_id, []))
        new_members = current_member_ids - previous_member_ids

        for member in members:
            user_id = member["user"]["id"]
            if user_id in new_members:
                username = f'{member["user"]["username"]}#{member["user"]["discriminator"]}'
                send_webhook_message(f"New member joined guild {guild_id}: {username} ({user_id})")

    save_members(current_members)

if __name__ == "__main__":
    if not DISCORD_TOKEN or not WEBHOOK_URL:
        print("Please set DISCORD_TOKEN and WEBHOOK_URL environment variables.")
    else:
        main()
