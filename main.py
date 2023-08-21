# -*- coding: utf-8 -*-
import RPA_Selenium as RPA_Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
# from sqlalchemy import create_engine
# import pandas as pd
import platform
import time
from configparser import ConfigParser
from colorama import Fore
import colorama
from datetime import date, timedelta, datetime
import psutil
import sys


#################################################################################

configINI = ConfigParser()
arquivoini = 'parametro.ini'
configINI.read(arquivoini, encoding='utf-8')

# alterar para o banco de dados ##
download_dir = configINI.get('configuracao', 'dir_meupc')
file_name = configINI.get('configuracao', 'file_name')
ref_final = configINI.getint('configuracao', 'ref_final')

colorama.init(autoreset=True)

print('\n\nDiretório destino: ', download_dir)
print('-------------------------------------------')

allSections = configINI.sections()
del(allSections[0])  # excluo o grupo de parametrização do programa
del(allSections[0])  # excluo o grupo de parametrização do programa
# print(allSections)
#################################################################################

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    FLASH = '\33[5m'

    def getCorMemoria(valor):
        if valor < 60:
            cor = f'{bcolors.OKGREEN}' + str(valor) + f'%{bcolors.ENDC}'
        elif valor < 80:
            cor = f'{bcolors.WARNING}' + str(valor) + f'%{bcolors.ENDC}'
        else:
            cor = f'{bcolors.FAIL}' + str(valor) + f'%{bcolors.ENDC}'

        return cor

# ontem como referencia final
yesterday = date.today() - timedelta(days=ref_final)

# Por conta do limite de 6 meses do INMET temos que pegar em blocos de 6 em 6 meses no máximo
seis_meses_antes = yesterday - timedelta(days=6*30)

# Aguarde até que um elemento específico esteja presente
# WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'tb')))


for section in allSections:

    # Pega a ultima data de atualização da planilha
    data_ultima_att = configINI.get(section, 'data_ultima_att')
    data_ultima_att = datetime.strptime(data_ultima_att, '%d/%m/%Y').date()
    estacao = configINI.get(section, 'estacao')

    while data_ultima_att != yesterday:

        # Pega a ultima data de atualização da planilha
        data_ultima_att = configINI.get(section, 'data_ultima_att')
        data_ultima_att = datetime.strptime(
            data_ultima_att, '%d/%m/%Y').date()

        print(
            f'Iniciando a importação da estação {Fore.GREEN}{estacao} {Fore.WHITE}a partir do dia {Fore.GREEN}{data_ultima_att} \n\n')

        valMemRam = psutil.virtual_memory()[2] # pego o valor da memória

        corMemRam = bcolors.getCorMemoria(valMemRam) # aplico a cor

        print('Ram: ' + corMemRam + '\n\n')

        if data_ultima_att == yesterday:
            print(f"{Fore.YELLOW}A planilha ja esta atualizada\n\n")
            continue  # talvez tenha que mudar aqui

        if (data_ultima_att < seis_meses_antes):
            data_att = RPA_Selenium.BuscaSeisMeses(estacao=estacao, primeira_data=data_ultima_att,
                                                   download_dir=download_dir, file_name=file_name)

            if data_att == 0:
                print(
                    f"{Fore.RED}Ocorreu um erro de execução....reiniciando o RPA\n\n")
                #time.sleep(6)
                sys.exit(0)

            else:
                configINI.set(section, 'data_ultima_att', data_att)

                with open(arquivoini, 'w', encoding= 'utf-8') as f:
                    configINI.write(f)

        elif (data_ultima_att > seis_meses_antes):
            data_att = RPA_Selenium.BuscaMenorSeisMeses(estacao=estacao, primeira_data=data_ultima_att,
                                                        download_dir=download_dir, file_name=file_name)

            print(data_att)
            if data_att == 0:
                print(
                    f"{Fore.RED}Ocorreu um erro de execução....reiniciando o RPA\n\n")
                #time.sleep(6)
                sys.exit(0)
            else:
                configINI.set(section, 'data_ultima_att', data_att)

                with open(arquivoini, 'w', encoding= 'utf-8') as f:
                    configINI.write(f)


print("{Fore.BLUE}*******************************************")
print("{Fore.BLUE}*******************************************")
print("{Fore.BLUE}   ATUALIZAÇÃO FINALIZAÇÃO COM SUCESSO")
print("{Fore.BLUE}*******************************************")
print("{Fore.BLUE}*******************************************")
