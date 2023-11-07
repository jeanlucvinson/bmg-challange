import pandas as pd
import re
import time
from functools import wraps
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd


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
    pass


def main() -> None:
    contour_df: pd.DataFrame = read_contour_file('PSATCMG_CAMARGOS.bln')
    data_df: pd.DataFrame = read_data_file('forecast_files/ETA40_p011221a021221.dat')
    contour_df: pd.DataFrame = apply_contour(contour_df=contour_df, data_df=data_df)


if __name__ == '__main__':
    main()


df_02 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a021221.dat'))
df_03 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a031221.dat'))
df_04 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a041221.dat'))
df_05 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a051221.dat'))
df_06 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a061221.dat'))
df_07 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a071221.dat'))
df_08 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a081221.dat'))
df_09 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a091221.dat'))
df_10 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a101221.dat'))
df_11 = pd.DataFrame(read_data_file('forecast_files/ETA40_p011221a111221.dat'))



# Lista de DataFrames
dfs = [df_02, df_03, df_04, df_05, df_06, df_07, df_08, df_09, df_10, df_11]

# Mesclando DataFrames usando merge encadeado
merged_df = pd.merge(df_02, df_02, on=['lat', 'long'], how='inner')

merged_df['data_value'] = merged_df['data_value_x'] + merged_df['data_value_y']
del merged_df['data_value_x']
del merged_df['data_value_y']

for df in dfs[2:]:
    merged_df = pd.merge(merged_df, df, on=['lat', 'long'], how='inner')
    merged_df['data_value'] = merged_df['data_value_x'] + merged_df['data_value_y']
    del merged_df['data_value_x']
    del merged_df['data_value_y']

for x, y in merged_df.iterrows():

    if y['long'] < -50 or y['long'] > -40:
        del y
    elif y['lat'] < -23 or y['lat'] > -20:
        del y


df_contour = read_contour_file('/Users/jeanlucevinson/Documents/Projetos/btg/bmg-challange/PSATCMG_CAMARGOS.bln')

# Cria um gráfico de dispersão com as coordenadas
plt.figure(figsize=(5, 6))  # Define o tamanho do gráfico (opcional)
plt.scatter(df_contour['lat'], df_contour['long'], color='blue', marker='o', s=8)  # Cria o gráfico de dispersão
plt.xlabel('Longitude')  # Adiciona rótulo ao eixo x
plt.ylabel('Latitude')   # Adiciona rótulo ao eixo y
plt.title('Mapa de Coordenadas')  # Adiciona um título ao gráfico
plt.show()  # Exibe o gráfico

# Criando um mapa de contorno (contour plot) usando matplotlib
plt.figure(figsize=(10, 8))
contour_plot = plt.tricontourf(df['long'], df['lat'], df['data_value'], cmap='YlGnBu')
plt.colorbar(contour_plot, label='Precipitação Acumulada (mm)')
plt.title('Previsão de Precipitação Acumulada em 01/12/2021')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()


print('oi')

