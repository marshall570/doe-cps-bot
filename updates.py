import os
import requests
from dotenv import load_dotenv

def receber_updates():
    load_dotenv()
    TOKEN = os.getenv('BOT-TOKEN')
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(requests.get(url).json())

receber_updates()
