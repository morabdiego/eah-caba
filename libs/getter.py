import requests
import os
import pandas as pd
import zipfile
from bs4 import BeautifulSoup
from typing import Dict, List, Union
from .constants import EAH_URL, USER_AGENT, PARSER

def get_pagination_v1() -> Union[List[str], int]:
    # configuración inicial
    headers = {'user-agent': USER_AGENT}
    urls = [EAH_URL]
    
    # obtener la URL raíz o inicial
    try:
        root = requests.get(urls[0], headers=headers, timeout=10)
        root.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al obtener la página inicial: {e}")
        return root.status_code if hasattr(root, 'status_code') else 500
    
    # extraer links de paginado
    soup = BeautifulSoup(root.text, PARSER)
    paginado = soup.find_all('a', class_='inactive')
    urls.extend(i.get('href') for i in paginado if i.get('href'))
    
    return urls

def obtener_listas_v1_1() -> Dict[str, str]:
    headers = {'user-agent': USER_AGENT}
    urls = get_pagination_v1()
    bases = {}
    
    if isinstance(urls, int):
        print(f"Error al obtener las URLs de paginación. Código de estado: {urls}")
        return bases

    for url in urls:
        try:
            req = requests.get(url, headers=headers, timeout=10)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, PARSER)
            for i in soup.find_all('h2'):
                bases[i.text.split(' ')[-1]] = i.a.get('href')
        except requests.RequestException as e:
            print(f'Error al descargar bases: {url} no responde. Error: {e}')
    
    return bases

def get_file(year: Union[str, List[str]]) -> None:
    headers = {'user-agent': USER_AGENT}
    bases = obtener_listas_v1_1()
    
    if isinstance(year, str):
        years = [year]
    else:
        years = year
    
    for y in years:
        if y not in bases:
            print(f"No se encontró información para el año {y}")
            continue

        loc = bases[y]
        try:
            req = requests.get(loc, headers=headers, timeout=10)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, PARSER)
            file_url = soup.find('div', class_='entry-content').a.get('href')
            file = requests.get(file_url, timeout=10)
            file.raise_for_status()
            
            os.makedirs('cache', exist_ok=True)
            with open(f'cache/eah-{y}.zip', 'wb') as f:
                f.write(file.content)
            print(f'Descarga exitosa para el año {y}')
        except requests.RequestException as e:
            print(f'Error al descargar el archivo para el año {y}: {e}')
        except AttributeError:
            print(f'Error al encontrar el enlace de descarga para el año {y}')

def extraer_archivos(nombre_archivo_zip: str, directorio_destino: str) -> None:
    try:
        with zipfile.ZipFile(nombre_archivo_zip, 'r') as archivo_zip:
            archivo_zip.extractall(directorio_destino)
    except zipfile.BadZipFile:
        print(f"Error: El archivo {nombre_archivo_zip} no es un archivo ZIP válido.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {nombre_archivo_zip}.")

def descomprimir_archivo_requerido(year: str) -> None:
    path = f'cache/eah-{year}.zip'
    extraer_archivos(nombre_archivo_zip=path, directorio_destino=f'cache/eah-{year}')

def get_base_eah(year: str, base: str) -> Union[pd.DataFrame, None]:
    get_file(year=[year])  # Ahora get_file acepta una lista de años
    descomprimir_archivo_requerido(year=year)
    if base in ['ind', 'hog']:
        try:
            df = pd.read_csv(f'cache/eah-{year}/eah{year}_bu_ampliada_{base}.txt', sep=';', encoding='utf-8')
            return df
        except FileNotFoundError:
            print(f"No se encontró el archivo para el año {year} y base {base}")
            return None
    else:
        print(f'El valor del parámetro {base} es inválido\nEl valor de base debe ser ind o hog, según desee obtener la base de datos individual o de hogares de la EAH del año {year}')
        return None

