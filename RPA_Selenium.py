# -*- coding: utf-8 -*-
# AVISO: NÃO RODE ESSE ARQUIVO DIRETAMENTE!!!! ACESSE O ARQUIVO main.py

import os
import time
from datetime import date, timedelta, datetime
import colorama
from colorama import Fore

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import platform
from configparser import ConfigParser

configINI = ConfigParser()
arquivoini = 'parametro.ini'
configINI.read(arquivoini, encoding='utf-8')

# alterar para o banco de dados ##
download_dir = configINI.get('configuracao', 'dir_meupc')
ref_final = configINI.getint('configuracao', 'ref_final')



class ChromeAuto:
    def __init__(self):
        if platform.system() == 'Linux':
            self.driver_path = '/usr/bin/chromedriver'
        else:
            self.driver_path = 'chromedriver.exe'
            self.driver_path = ''

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('--disable-extensions')
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Adicione esta linha
        self.options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            'excludeSwitches': 'enable-logging'
        })


        self.service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)


def BuscaSeisMeses(estacao, primeira_data, download_dir, file_name):

    colorama.init(autoreset=True)

    # pegar o cod da estacao
    campos = estacao.split("(")
    cod_estacao = campos[-1][:4]
    dc_nome = campos[0][:]
    dc_nome = dc_nome.strip()
    # primeiro dia a ser importado
    primeira_data += timedelta(days=1)

    # conta 6 meses depois
    segunda_data = primeira_data + timedelta(days=6*30)

    #para colocar o nome no arquivo
    primeira_data_str = primeira_data.strftime('%Y%m%d')
    segunda_data_str = segunda_data.strftime('%Y%m%d')

    # formatar a data como string no formato "dd/mm/yyyy"
    segunda_data = segunda_data.strftime('%d/%m/%Y')

    # formatar a data como string no formato "dd/mm/yyyy"
    primeira_data = primeira_data.strftime('%d/%m/%Y')

    # verifica se o arquivo já existe e remove se existir
    if os.path.exists(download_dir + 'dados_inmet.csv'):
        os.remove(download_dir + 'dados_inmet.csv')

    try:
        # acessa a página
        # Inicializando o driver
        browser = ChromeAuto().driver
        browser.get(f'https://tempo.inmet.gov.br/TabelaEstacoes/{cod_estacao}')

        # tempo máximo que o loop irá esperar pelo elemento em segundos
        tempo_maximo = 60

        while tempo_maximo > 0:
            try:
                # Tenta encontrar o elemento com o xpath do botão lateral
                elemento = WebDriverWait(browser, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div[1]/div[1]/i'))
                )
                # Se encontrou o elemento, clica no botão e sai do loop
                elemento.click()
                break
            except:
                # Se o elemento ainda não está visível na página, espera mais 1 segundo
                tempo_maximo -= 1
                time.sleep(1)

            if tempo_maximo == 0:
                return 0

        time.sleep(1)

        # preenche o campo de estação
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input').send_keys(estacao)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input').send_keys(Keys.ENTER)

        # Preenche a Data de Inicio
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').click()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').clear()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').send_keys(primeira_data)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').send_keys(Keys.ENTER)

        # Preenche a Data Fim
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').click()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').clear()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').send_keys(segunda_data)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').send_keys(Keys.ENTER)

        # espera a página ser carregada
        time.sleep(3)

        # Clica no botão "Gerar Tabela"
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/button').click()

        tempo_maximo = 60

        while tempo_maximo > 0:
            try:
                # Tenta encontrar o elemento com o xpath especificado
                elemento = WebDriverWait(browser, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div[2]/div[2]/div/div/div/span/a'))
                )
                # Se encontrou o elemento, clica no botão e sai do loop
                elemento.click()
                break
            except:
                # Se o elemento ainda não está visível na página, espera mais 1 segundo
                tempo_maximo -= 1
                time.sleep(1)

            if tempo_maximo == 0:
                return 0

        # esperando o arquivo ser baixado
        while not os.path.exists(download_dir + file_name):
            time.sleep(1)

        # renomeando o arquivo
        new_file_name = f'{cod_estacao}-{primeira_data_str}-{segunda_data_str}-{dc_nome}.csv'
        os.rename(download_dir + file_name, download_dir + new_file_name)

        print(
            f"Raspagem de dados da estação {Fore.GREEN}{estacao} {Fore.WHITE}finalizada\n\n")

        #print("Iniciando processo de unificação de bases...\n\n")

        #RPA_ETL.TratarTabela(ref_dir=download_dir, estacao=estacao,  cod_estacao=cod_estacao)

        #print(f"{Fore.YELLOW}Bases unificadas....passando para a próxima leva de dados\n{datetime.now()}\n")
        print(f"O arquivo {new_file_name} foi baixado com sucesso\n\n")
        browser.quit()

        return segunda_data

    except Exception as e:
        print(f"{Fore.RED}Erro de execução: a página apresentou um erro em um de seus componentes...abortando processo de raspagem\n{datetime.now()}\n")
        print(f"Ocorreu um erro: {e}\n\n")
        return 0


def BuscaMenorSeisMeses(estacao, primeira_data, download_dir, file_name):

    colorama.init(autoreset=True)

    # pegar o cod da estacao
    campos = estacao.split("(")
    cod_estacao = campos[-1][:4]
    dc_nome = campos[0][:]
    dc_nome = dc_nome.strip()


    # primeiro dia a ser importado
    primeira_data += timedelta(days=1)

    # ontem como referencia final
    segunda_data = date.today() - timedelta(days=ref_final)

    #para colocar o nome no arquivo
    primeira_data_str = primeira_data.strftime('%Y%m%d')
    segunda_data_str = segunda_data.strftime('%Y%m%d')

    # formatar a data como string no formato "dd/mm/yyyy"
    segunda_data = segunda_data.strftime('%d/%m/%Y')

    # formatar a data como string no formato "dd/mm/yyyy"
    primeira_data = primeira_data.strftime('%d/%m/%Y')

    # verifica se o arquivo já existe e remove se existir
    if os.path.exists(download_dir + 'dados_inmet.csv'):
        os.remove(download_dir + 'dados_inmet.csv')

    # verifica se o arquivo já existe e remove se existir
    if os.path.exists(download_dir + 'generatedBy_react-csv.csv'):
        os.remove(download_dir + 'generatedBy_react-csv.csv')

    try:
        # acessa a página
        # Inicializando o driver
        browser = ChromeAuto().driver
        browser.get(f'https://tempo.inmet.gov.br/TabelaEstacoes/{cod_estacao}')

        # tempo máximo que o loop irá esperar pelo elemento em segundos
        tempo_maximo = 60

        while tempo_maximo > 0:
            try:
                # Tenta encontrar o elemento com o xpath do botão lateral
                print('CLICA')
                elemento = WebDriverWait(browser, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div[1]/div[1]/i'))
                )
                print('CLIQUEI')
                # Se encontrou o elemento, clica no botão e sai do loop
                elemento.click()
                break
            except:
                # Se o elemento ainda não está visível na página, espera mais 1 segundo
                tempo_maximo -= 1
                time.sleep(1)

            if tempo_maximo == 0:
                return 0

        # preenche o campo de estação
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input').send_keys(estacao)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input').send_keys(Keys.ENTER)

        # Preenche a Data de Inicio
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').click()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').clear()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').send_keys(primeira_data)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[4]/input').send_keys(Keys.ENTER)

        # Preenche a Data Fim
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').click()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').clear()
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').send_keys(segunda_data)
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/div[5]/input').send_keys(Keys.ENTER)

        # espera a página ser carregada
        time.sleep(3)

        # Clica no botão "Gerar Tabela"
        browser.find_element(
            By.XPATH, '//*[@id="root"]/div[2]/div[1]/div[2]/button').click()

        tempo_maximo = 60

        while tempo_maximo > 0:
            # print('TO AQUI')
            # sys.exit(0)

            try:
                # Tenta encontrar o elemento com o xpath especificado
                elemento = WebDriverWait(browser, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div[2]/div[2]/div/div/div/span/a'))
                )
                # Se encontrou o elemento, clica no botão e sai do loop
                elemento.click()
                break
            except:
                # Se o elemento ainda não está visível na página, espera mais 1 segundo
                tempo_maximo -= 1
                time.sleep(1)

            if tempo_maximo == 0:
                return 0

        # esperando o arquivo ser baixado
        # print('TO AQUI 2')
        #print(os.path.exists(download_dir + file_name), download_dir + file_name)
        while not os.path.exists(download_dir + file_name):
            time.sleep(1)
        #print('TO AQUI 3')

        # renomeando o arquivo
        new_file_name = f'{cod_estacao}-{primeira_data_str}-{segunda_data_str}-{dc_nome}.csv'
        os.rename(download_dir + file_name, download_dir + new_file_name)


        print(
            f"Raspagem de dados da estação {Fore.GREEN}{estacao} {Fore.WHITE}finalizada\n\n")

        #print("Iniciando processo de unificação de bases...\n\n")


        # indo para a proxima etapa....unificando bases
        #try:
        #    RPA_ETL.TratarTabela(ref_dir=download_dir,
        #                         estacao=estacao, cod_estacao=cod_estacao)
        #    print(
        #        f"{Fore.YELLOW}Bases unificadas....passando para a próxima leva de dados\n{datetime.now()}\n")
        #except:
        #    print(
        #        f"{Fore.RED}Não foi possível inserir os dados da estacao {estacao} na tabela\n{datetime.now()}\n")
        #    return primeira_data

        print(f"O arquivo {new_file_name} foi baixado com sucesso\n\n")
        # Inicializando o driver
        browser.quit()

        return segunda_data

    except Exception as e:
        print(F"{Fore.RED}Erro de execução: a página apresentou um erro em um de seus componentes...abortando processo de raspagem\n\n")
        print(f"Ocorreu um erro: {e}\n\n")
        return 0
