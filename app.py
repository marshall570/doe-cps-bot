import os
import logging
from datetime import datetime

import pandas
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions


from updates import Updates


logging.basicConfig(
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()],
    encoding='utf-8',
    format='%(asctime)s [%(levelname)s: %(filename)s (line %(lineno)d)] %(message)s',
    datefmt='%d/%m/%Y - %H:%M:%S',
    level=logging.INFO
)


def scroll_to_element(driver, element):
    x = element.location['x']
    y = element.location['y']
    scroll_by_coord = f'window.scrollTo({x},{y});'
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    driver.execute_script(scroll_by_coord)
    driver.execute_script(scroll_nav_out_of_way)


def init_driver():
    if os.path.exists('/usr/bin/firefox'):
        options = FirefoxOptions()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(10)
    else:
        options = ChromeOptions()
        options.binary_location = os.getenv('CHROME-PATH')
        options.add_argument('-headless')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

    return driver


def has_publication(driver):
    try:
        driver.get('https://www.imprensaoficial.com.br')
        txt_publication = driver.find_element(By.CSS_SELECTOR, '#txtError').get_attribute('style')

        return True if txt_publication.find('hidden') != -1 else False

    except Exception:
        return False


def process_edicts(driver, row):
    input_search = '#content_txtPalavrasChave'
    btn_search = '#content_btnBuscar'
    btn_order = '#content_lnkOrderByData'
    txt_entry = 'div.card:nth-child(4) > div:nth-child(1) > a:nth-child(1)'

    driver.get('https://www.imprensaoficial.com.br')
    driver.add_cookie({"name": "PortalIOJoyRide", "value": "ridden"})

    driver.find_element(By.CSS_SELECTOR, input_search).send_keys(f'\"nº {row["EDITAL"]}\"')
    driver.find_element(By.CSS_SELECTOR, btn_search).click()

    if os.path.exists('/usr/bin/firefox'):
        scroll_to_element(driver, driver.find_element(By.CSS_SELECTOR, btn_order))

    driver.find_element(By.CSS_SELECTOR, btn_order).click()
    entry_link = driver.find_element(By.CSS_SELECTOR, txt_entry)

    entry_date = entry_link.get_attribute('textContent').strip()
    entry_date = entry_date.split('-')
    row['ULTIMA AT'] = entry_date[0].strip()
    row['LINK'] = entry_link.get_attribute('href').strip()


def send_no_publication(id, date):
    message = f'📭 <b>SEM PUBLICAÇÃO NO DIÁRIO OFICIAL</b>\n\nNão foram encontradas publicações em {date}\n\n<i>Mais atualizações amanhã!</i>'
    url = f"https://api.telegram.org/bot{os.getenv('BOT-TOKEN')}/sendMessage?chat_id={id}&parse_mode=html&text={message}"
    requests.get(url).json()


def send_updates(id, updated):
    message = f'{updated}\n\n<i>Mais atualizações amanhã!</i>'
    url = f"https://api.telegram.org/bot{os.getenv('BOT-TOKEN')}/sendMessage?chat_id={id}&parse_mode=html&text={message}"
    requests.get(url).json()


def scrap_routine(person, id):
    try:
        driver = init_driver()
        today = datetime.today().strftime('%d/%m/%Y')

        if has_publication(driver):
            message = f'🎯 <b>EDITAIS COM ATUALIZAÇÃO EM {today}</b>'

            spreadsheet = pandas.read_csv(
                f'./editais-{person.lower()}.csv',
                dtype=str
            )

            for index, row in spreadsheet.iterrows():
                process_edicts(driver, row)
                if row["ULTIMA AT"] == today:
                    message += f'''\n<b>{row['EDITAL']}</b> | <i>{row['MATERIA']}</i>'''

            if message.find('|') == -1:
                message = f'⏳ <b>EDITAIS SEM ATUALIZAÇÃO EM {today}</b>\n\n<i>Não houveram atualizações nos editais cadastrados :(</i>'

            spreadsheet.to_csv(f'./editais-{person.lower()}.csv', index=False)
            send_updates(id, message)

        else:
            send_no_publication(id, today)

        logging.info(f'{person.upper()}: OK')

    except Exception as error:
        logging.critical(f'{person.upper()}: {error}')

    finally:
        driver.quit()


load_dotenv()
Updates.get_updates(os.getenv('BOT-TOKEN'))
scrap_routine('gustavo', os.getenv('ID-GUSTAVO'))
scrap_routine('ana', os.getenv('ID-ANA'))
