import logging
import requests


class Updates:
    def get_updates(token):
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            logging.info(requests.get(url).json())
        except Exception as error:
            logging.critical(error)
