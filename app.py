import pandas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


try:
    # DRIVER
    options = Options()
    # options.add_argument('-headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    planilha = pandas.read_csv('editais.csv', dtype=str)

    # SELECTORS
    input_busca = '#content_txtPalavrasChave'
    btn_busca = '#content_btnBuscar'
    btn_fechar = 'div.joyride-tip-guide:nth-child(7) > div:nth-child(2) > a:nth-child(3)'
    btn_ordem = '#content_lnkOrderByData'
    txt_entrada = 'div.card:nth-child(4) > div:nth-child(1) > a:nth-child(1)'

    # ROTINA
    for linha, coluna in planilha.iterrows():
        driver.get('https://www.imprensaoficial.com.br')
        driver.find_element(By.CSS_SELECTOR, input_busca).send_keys(
            f'nº {coluna["EDITAL"]}')
        driver.find_element(By.CSS_SELECTOR, btn_busca).click()

        if linha == 0:
            espera_btn_fechar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, btn_fechar)))
            espera_btn_fechar.click()

        espera_btn_ordem = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, btn_ordem)))
        ActionChains(driver).move_to_element(espera_btn_ordem).click().perform()

        link_at = driver.find_element(By.CSS_SELECTOR, txt_entrada)

        data_at = link_at.get_attribute('textContent').strip()
        data_at = data_at.split('-')
        coluna['ULTIMA AT'] = data_at[0].strip()

        coluna['LINK'] = link_at.get_attribute('href').strip()

    driver.quit()

    planilha.to_csv('editais.csv', index=False)

except Exception as error:
    driver.quit()
    print(error)
