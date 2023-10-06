import pandas
from colorama import Fore
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def scroll_to_element(driver, element):
    x = element.location['x']
    y = element.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    driver.execute_script(scroll_by_coord)
    driver.execute_script(scroll_nav_out_of_way)


try:
    # DRIVER
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)

    # SELECTORS
    input_busca = '#content_txtPalavrasChave'
    btn_busca = '#content_btnBuscar'
    btn_ordem = '#content_lnkOrderByData'
    txt_entrada = 'div.card:nth-child(4) > div:nth-child(1) > a:nth-child(1)'

    # ROTINA
    today = datetime.today().strftime('%d/%m/%Y')
    planilha = pandas.read_csv('./editais.csv', dtype=str)
    print('ÚLTIMAS ATUALIZAÇÕES')

    for linha, coluna in planilha.iterrows():
        driver.get('https://www.imprensaoficial.com.br')
        driver.add_cookie({"name": "PortalIOJoyRide", "value": "ridden"})

        driver.find_element(By.CSS_SELECTOR, input_busca).send_keys(f'\"nº {coluna["EDITAL"]}\"')
        driver.find_element(By.CSS_SELECTOR, btn_busca).click()

        scroll_to_element(driver, driver.find_element(By.CSS_SELECTOR, btn_ordem))
        driver.find_element(By.CSS_SELECTOR, btn_ordem).click()

        link_at = driver.find_element(By.CSS_SELECTOR, txt_entrada)
        data_at = link_at.get_attribute('textContent').strip()
        data_at = data_at.split('-')
        coluna['ULTIMA AT'] = data_at[0].strip()
        coluna['LINK'] = link_at.get_attribute('href').strip()

        if coluna["ULTIMA AT"] == today:
            print(Fore.GREEN + f'{coluna["EDITAL"]} | {coluna["ULTIMA AT"]} - {coluna["MATERIA"]}')
        else:
            print(Fore.YELLOW + f'{coluna["EDITAL"]} | {coluna["ULTIMA AT"]} - {coluna["MATERIA"]}')

    driver.quit()

    planilha.to_csv('./editais.csv', index=False)

except Exception as error:
    driver.quit()
    print(error)
