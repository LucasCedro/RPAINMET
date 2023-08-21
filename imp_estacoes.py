from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
import pandas as pd
import platform
import time
from configparser import ConfigParser

from pyproj import CRS, Transformer
import utm
import math

class ChromeAuto:
    def __init__(self):
        if platform.system() == 'Linux':
            self.driver_path = '/usr/bin/chromedriver'
        else:
            self.driver_path = 'chromedriver.exe'

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('--disable-extensions')
        self.options.add_argument("--start-maximized")

        self.service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

# Inicializando o driver
browser = ChromeAuto().driver

# Acessando a página
browser.get('https://portal.inmet.gov.br/paginas/catalogoaut')

# Aguarde até que um elemento específico esteja presente
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'tb')))

# Obtendo o código HTML da página
html = browser.page_source

# Parseando o HTML com o BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Encontrando a tabela no HTML
table = soup.find('table', attrs={'id': 'tb'})

# Lendo a tabela com o Pandas
df = pd.read_html(str(table), decimal=',', thousands='.')[0]

# Convertendo a coluna 'Data de Instalação' para datetime
df['Data de Instalação'] = pd.to_datetime(df['Data de Instalação'], format='%d/%m/%Y')

# Abrindo a conexão
configINI = ConfigParser()
arquivoini = 'parametro.ini'
configINI.read(arquivoini, encoding='utf-8')

db_params = configINI['postgresql']
engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}?sslmode=require")

# Nome da tabela que será criada no PostgreSQL
table_name = 'estacoes'

# Substituindo os dados da tabela com os dados do DataFrame
with engine.begin() as connection:
    # Remove todas as linhas da tabela
    connection.execute(text(f"TRUNCATE TABLE {table_name}"))

    # Insere os dados do DataFrame na tabela
    df.to_sql(table_name, connection, if_exists='append', index=False)

# Encerrando o driver
browser.quit()
