# -*- coding: utf-8 -*-
import os
import time
from sqlalchemy import create_engine, text
from configparser import ConfigParser
import pandas as pd
import sys

def get_station_metadata(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()[:7]
    metadata = dict()
    for line in lines:
        key, value = line.strip().split(';')
        metadata[key] = value

    station_keys = ["ESTAÇÃO:", "ESTACAO:", "ESTAC?O:"]

    station_key = None
    for key in station_keys:
        if key in metadata:
            station_key = key
            break

    if station_key is None:
        raise KeyError("Nenhuma chave de estação válida encontrada!")

    return metadata[station_key], metadata['CODIGO (WMO):']

def insert_data_from_csv(file_name, engine):
    start_time = time.time()

    dc_nome, cd_estacao = get_station_metadata(file_name)

    data = pd.read_csv(file_name, sep=';', decimal=',', skiprows=9, encoding='cp1252', na_values="-9999",
                       names=['data', 'hora', 'precipitacao', 'pressao_atmosferica_media',
                          'pressao_atmosferica_maxima', 'pressao_atmosferica_minima',
                          'radiacao_global', 'temperatura_media', 'ponto_orvalho_medio',
                          'temperatura_maxima', 'temperatura_minima', 'ponto_orvalho_maximo',
                          'ponto_orvalho_minimo', 'umidade_relativa_maxima', 'umidade_relativa_minima',
                          'umidade_relativa_media', 'vento_direcao_horaria', 'rajada_vento', 'vento_velocidade_horaria'],
                       low_memory=False, index_col=False) # nrows=3,

    data['dc_nome'] = dc_nome
    data['cd_estacao'] = cd_estacao
    data['data'] = data['data'].str.replace("/", "-")
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')
    data['hora'] = data['hora'].str.replace(':', '').str.replace(' UTC', '')
    #print(data['hora'][0])

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
with engine.connect() as connection:
    connection.execute(text("TRUNCATE TABLE weather_data"))
    connection.commit()

directory_path = 'C:/Users/cjddu/Dropbox/lucas/HIST'

file_names = [f for f in os.listdir(directory_path) if f.endswith('.CSV')]

start_time_1 = time.time()
for file_name in file_names:
    file_path = os.path.join(directory_path, file_name)
    insert_data_from_csv(file_path, engine)

end_time_1 = time.time()
