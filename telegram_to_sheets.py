from telethon import TelegramClient
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# ========= TELEGRAM =========
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
group_username = os.environ["GROUP_USERNAME"]

client = TelegramClient("session", api_id, api_hash)

# ========= GOOGLE SHEETS =========
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    eval(os.environ["GOOGLE_CREDS"]), scope
)

gs = gspread.authorize(creds)
sheet = gs.open("Ofertas Telegram").sheet1

KEYWORDS = [
    "detergente",
    "shampoo",
    "papel higienico",
    "ariel",
    "nupec",
    "croquetas"
]

def contiene_keyword(texto):
    texto = texto.lower()
    return any(k in texto for k in KEYWORDS)

def extraer_precio(texto):
    match = re.search(r"\$ ?([0-9,.]+)", texto)
    return match.group(1) if match else ""

async def main():
    await client.start()
    group = await client.get_entity(group_username)

    async for message in client.iter_messages(group, limit=200):
        if message.message and contiene_keyword(message.message):
            sheet.append_row([
                message.date.strftime("%Y-%m-%d %H:%M"),
                group_username,
                message.message,
                extraer_precio(message.message),
                f"https://t.me/{group_username}/{message.id}"
            ])

with client:
    client.loop.run_until_complete(main())
