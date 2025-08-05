import requests
import websocket
import json
import threading
import time
import os
from fastapi import FastAPI
import uvicorn

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = FastAPI()

def send_to_webhook(content):
    payload = {"content": content}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            print("Failed to send webhook:", response.text)
    except Exception as e:
        print("Webhook error:", e)

def on_message(ws, message):
    data = json.loads(message)
    if data.get("t") == "GUILD_MEMBER_ADD":
        user = data["d"]["user"]
        guild_id = data["d"]["guild_id"]
        username = f'{user["username"]}#{user["discriminator"]}'
        content = f"New user joined in guild {guild_id}: {username}"
        print(content)
        send_to_webhook(content)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    def identify():
        payload = {
            "op": 2,
            "d": {
                "token": DISCORD_TOKEN,
                "intents": 1 << 0 | 1 << 9,
                "properties": {
                    "$os": "linux",
                    "$browser": "my_library",
                    "$device": "my_library"
                }
            }
        }
        ws.send(json.dumps(payload))
    threading.Thread(target=identify).start()

def run_discord_monitor():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://gateway.discord.gg/?v=10&encoding=json",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print("WebSocket connection error:", e)
        time.sleep(10)

@app.get("/")
def root():
    return {"status": "Discord monitor running"}

if __name__ == "__main__":
    threading.Thread(target=run_discord_monitor).start()
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
