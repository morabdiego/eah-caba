from libs import *
import pandas as pd

# years = [str(x) for x in range(2012, 2024)]

# get_file(year=years)



import os

def listar_txt_en_carpeta(carpeta: str) -> list[str]:
    return [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.txt')]

bases = listar_txt_en_carpeta('cache/')

for base in bases:
    df = pd.read_csv(f'cache/{base}')
    print(df.head())