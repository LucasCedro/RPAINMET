# -*- coding: utf-8 -*-
import os
import time
from sqlalchemy import create_engine, text
from configparser import ConfigParser
import pandas as pd

def insert_data_from_csv(file_name, dc_nome, cd_estacao, engine):
    start_time = time.time()

    data = pd.read_csv(file_name, sep=';', decimal=',', skiprows=1,
                       names=['data', 'hora', 'temperatura_media', 'temperatura_maxima', 'temperatura_minima',
                              'umidade_relativa_media', 'umidade_relativa_maxima', 'umidade_relativa_minima',
                              'ponto_orvalho_medio', 'ponto_orvalho_maximo', 'ponto_orvalho_minimo',
                              'pressao_atmosferica_media', 'pressao_atmosferica_maxima', 'pressao_atmosferica_minima',
                              'vento_velocidade_horaria', 'vento_direcao_horaria', 'rajada_vento',
                              'radiacao_global', 'precipitacao'],
                       low_memory=False)  # Adicionado para melhorar a performance

    data['dc_nome'] = dc_nome
    data['cd_estacao'] = cd_estacao
    data['data'] = pd.to_datetime(data['data'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    data['hora'] = data['hora'].apply(lambda x: f"{x:04d}") # Adicionando zeros à esquerda na coluna 'hora'

    data.to_sql('weather_data', engine, if_exists='append', index=False)

    end_time = time.time()
    print(f"Tempo de inserção para {os.path.basename(file_name)}: {round(end_time - start_time, 1)} segundos")

# Abrindo a conexão
configINI    = ConfigParser()
arquivoini   = 'parametro.ini'
configINI.read(arquivoini, encoding='utf-8')

db_params = configINI['postgresql']
engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}?sslmode=require")

# Truncate table before loading
'''
with engine.connect() as connection:
    connection.execute(text("TRUNCATE TABLE weather_data"))
    connection.commit()
'''
directory_path = 'C:/Users/cjddu/Dropbox/lucas/Downloads'

file_names = [f for f in os.listdir(directory_path) if f.endswith('.csv')]

start_time_1 = time.time()
for file_name in file_names:

    file_name_without_extension = os.path.splitext(file_name)[0] ## Remover a extensão do arquivo
    station_code = file_name_without_extension.split('-')[0]

    split_names = file_name_without_extension.split('-')
    station_name = '-'.join(split_names[3:]).strip()

    file_path = os.path.join(directory_path, file_name)
    insert_data_from_csv(file_path, station_name, station_code, engine)

end_time_1 = time.time()
print(f"\nTempo total para insert_data_from_csv: {round(end_time_1 - start_time_1, 1)} segundos\n")