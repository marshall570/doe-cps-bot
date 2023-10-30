import os
import pandas
import requests
from dotenv import load_dotenv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def scrollar_ate_elemento(driver, element):
    x = element.location['x']   
    y = element.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    driver.execute_script(scroll_by_coord)
    driver.execute_script(scroll_nav_out_of_way)


def iniciar_driver():
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)

    return driver


def enviar_mensagem(id, atualizados, nao_atualizados):
    mensagem = f'{atualizados}\n\n{nao_atualizados}\n\n<i>Mais atualizações amanhã!</i>'
    load_dotenv()
    TOKEN = os.getenv('BOT-TOKEN')
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={id}&parse_mode=html&text={mensagem}"
    requests.get(url).json()


def scrap_editais(pessoa, id):
    try:
        hoje = datetime.today().strftime('%d/%m/%Y')
        mensagem_atualizados = f'🎯 <b>EDITAIS COM ATUALIZAÇÃO EM {hoje}</b>'
        mensagem_nao_atualizados = '⏳ <b>EDITAIS SEM ATUALIZAÇÃO</b>'

        input_busca = '#content_txtPalavrasChave'
        btn_busca = '#content_btnBuscar'
        btn_ordem = '#content_lnkOrderByData'
        txt_entrada = 'div.card:nth-child(4) > div:nth-child(1) > a:nth-child(1)'  

        planilha = pandas.read_csv(f'./editais-{pessoa.lower()}.csv', dtype=str)
        driver = iniciar_driver()

        for linha, coluna in planilha.iterrows():
            driver.get('https://www.imprensaoficial.com.br')
            driver.add_cookie({"name": "PortalIOJoyRide", "value": "ridden"})

            driver.find_element(By.CSS_SELECTOR, input_busca).send_keys(f'\"nº {coluna["EDITAL"]}\"')
            driver.find_element(By.CSS_SELECTOR, btn_busca).click()
            
            scrollar_ate_elemento(driver, driver.find_element(By.CSS_SELECTOR, btn_ordem))
            driver.find_element(By.CSS_SELECTOR, btn_ordem).click()
            link_at = driver.find_element(By.CSS_SELECTOR, txt_entrada)
            
            data_at = link_at.get_attribute('textContent').strip()
            data_at = data_at.split('-')
            coluna['ULTIMA AT'] = data_at[0].strip()
            coluna['LINK'] = link_at.get_attribute('href').strip()

            if coluna["ULTIMA AT"] == hoje:
                mensagem_atualizados += f'''\n<b>{coluna['EDITAL']}</b> | <i>{coluna['MATERIA']}</i>'''
            else:
                mensagem_nao_atualizados += f'''\n<b>{coluna['EDITAL']}</b> | <i>{coluna['MATERIA']}</i>'''

        if mensagem_atualizados.find('|') == -1:
            mensagem_atualizados += '\n<i>Não houveram atualizações nos editais</i>'

        if mensagem_nao_atualizados.find('|') == -1:
            mensagem_nao_atualizados += '\n<i>Todos os editais tiveram atualizações</i>'

        driver.quit()

        planilha.to_csv(f'./editais-{pessoa.lower()}.csv', index=False)
        enviar_mensagem(id, mensagem_atualizados, mensagem_nao_atualizados)
        print(f'{pessoa.upper()}: OK')
    
    except Exception as error:
        driver.quit()
        print(f'{pessoa.upper()}: {error}')
    
load_dotenv()
scrap_editais(pessoa='gustavo', id=os.getenv('ID-GUSTAVO'))
scrap_editais(pessoa='ana', id=os.getenv('ID-GUSTAVO'))
