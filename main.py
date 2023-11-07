import pandas as pd
import re
import time
from functools import wraps
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon, Point


def read_data_file(file_path: str) -> pd.DataFrame:
    with open(file_path, 'r') as f:
        raw_file = f.readlines()

    list_dados = [line.split() for line in raw_file]
    float_raw_lines = [list(map(float, raw_line)) for raw_line in list_dados]
    return pd.DataFrame(float_raw_lines, columns=['lat', 'long', 'data_value'])


def read_contour_file(file_path: str) -> pd.DataFrame:
    line_split_comp = re.compile(r'\s*,')

    with open(file_path, 'r') as f:
        raw_file = f.readlines()

    l_raw_lines = [line_split_comp.split(raw_file_line.strip()) for raw_file_line in raw_file]
    l_raw_lines = list(filter(lambda item: bool(item[0]), l_raw_lines))
    float_raw_lines = [list(map(float, raw_line))[:2] for raw_line in l_raw_lines]
    header_line = float_raw_lines.pop(0)
    assert len(float_raw_lines) == int(header_line[0])
    return pd.DataFrame(float_raw_lines, columns=['lat', 'long'])


def apply_contour(contour_df: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
    
    #ler o arquivo do contour e criar coluna com as coordenadas
    df_contour = read_contour_file('PSATCMG_CAMARGOS.bln')
    df_map = df_coordenadas(df=df_contour)

    nomes_arquivos = lista_arquvios(pasta="forecast_files")

    df_final = []
    for arquivo in nomes_arquivos:

        data_inicial, data_final = extrair_datas(arquivo=arquivo)

        #lendo o arquivo ETA
        df_forcast_file = pd.DataFrame(read_data_file(f'forecast_files/{arquivo}'))

        #criar coluna com as coordenadas do ETA
        df_eta = df_coordenadas(df=df_forcast_file)

        #Coordenadas dos polígonos camargos em uma lista
        polygon_coordinates = df_map['coordenadas'].tolist()

        # Criando um objeto Polygon com as coordenadas dos polígonos
        polygon = Polygon(polygon_coordinates)

        # Coordenadas a serem verificadas em uma lista
        points_to_check = df_eta['coordenadas'].tolist()

        # Verificando se as coordenadas estão dentro do polígono e adicionando as coordenadas corretas em uma lista
        lista_coordenadas = coordeandas_dentro_da_area(polygon, points_to_check)

        #somar a precipitação do dia caso as coordenadas estejam iguais
        soma = soma_precipitacao(df_forcast_file, lista_coordenadas)

        # Criar um DataFrame com as datas
        df = montar_df_parcial(data_inicial, data_final, soma)

        #
        df_final.append(df)

    #concatenando o df final 
    df_tratado = pd.concat(df_final, ignore_index=True)
    print(df_tratado)

def montar_df_parcial(data_inicial, data_final, soma):
    return pd.DataFrame(
        {
            'forecast_date': [data_inicial],
            'forecasted_date': [data_final],
            'data_value': [soma]
        }
        )

def soma_precipitacao(df_forcast_file, lista_coordenadas):
    soma = 0
    for index, row in df_forcast_file.iterrows():
        if [row['lat'], row['long']] in lista_coordenadas:
            soma += row['data_value']
    return soma

def coordeandas_dentro_da_area(polygon, points_to_check):
    lista_coordenadas = []
    for point in points_to_check:
        x, y = point[0], point[1]
        point_obj = Point(x, y)
        if polygon.contains(point_obj):
            lista_coordenadas.append(point)
    return lista_coordenadas

def df_coordenadas(df):
    lista = []

    for index, row in df.iterrows():
        row['coordenadas'] = [row['lat'], row['long']]
        lista.append(row)

    return pd.DataFrame(lista) 

def lista_arquvios(pasta):
    nomes_arquivos = []

    #lendo todos arquvios e colocando os nomes em uma lista
    for nome_arquivo in os.listdir(pasta):
        if os.path.isfile(os.path.join(pasta, nome_arquivo)):
            nomes_arquivos.append(nome_arquivo)
    return nomes_arquivos

def extrair_datas(arquivo):
    # Extrair as datas do nome do arquivo
    data_inicial_str = arquivo.split("_p")[1][:6]
    data_final_str = arquivo.split("a")[1][:6]

    # Converter as datas para o formato desejado (DD/MM/YYYY)
    data_inicial = pd.to_datetime(data_inicial_str, format='%d%m%y').strftime('%d/%m/%Y')
    data_final = pd.to_datetime(data_final_str, format='%d%m%y').strftime('%d/%m/%Y')

    return data_inicial, data_final

def main() -> None:
    contour_df: pd.DataFrame = read_contour_file('PSATCMG_CAMARGOS.bln')
    data_df: pd.DataFrame = read_data_file('forecast_files/ETA40_p011221a021221.dat')
    contour_df: pd.DataFrame = apply_contour(contour_df=contour_df, data_df=data_df)

if __name__ == '__main__':
    main()