import os
import requests
import zipfile
import pandas as pd
from bs4 import BeautifulSoup
from logging import getLogger
from pprint import pprint

logger = getLogger(__name__)

# Constantes
EAH_URL = 'https://www.estadisticaciudad.gob.ar/eyc/?cat=93'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
PARSER = 'html.parser'
CACHE_DIR = 'cache'

def get_eah_url(year):
    return f'{EAH_URL}&year={year}'

def download_file(url, filename):
    logger.info(f'Descargando archivo {filename} desde {url}')
    response = requests.get(url, headers={'User-Agent': USER_AGENT})
    if response.status_code == 200:
        with open(os.path.join(CACHE_DIR, filename), 'wb') as f:
            f.write(response.content)
        logger.info(f'Archivo {filename} descargado correctamente')
    else:
        logger.error(f'Error al descargar archivo {filename}: {response.status_code}')

def extract_zipfile(zipfile_path, extract_dir):
    logger.info(f'Extrayendo archivo {zipfile_path} a {extract_dir}')
    with zipfile.ZipFile(zipfile_path, 'r') as zip_file:
        zip_file.extractall(extract_dir)
    logger.info(f'Archivo {zipfile_path} extraído correctamente')

def read_csv_file(year, base):
    filename = f'eah{year}_bu_ampliada_{base}.txt'
    filepath = os.path.join(CACHE_DIR, year, filename)
    logger.info(f'Leyendo archivo {filename} desde {filepath}')
    return pd.read_csv(filepath, sep=';', encoding='utf-8')

def get_base_eah(year, base):
    if base not in ['ind', 'hog']:
        logger.error(f'Valor de base inválido: {base}')
        return None
    filename = f'eah-{year}.zip'
    download_file(get_eah_url(year), filename)
    extract_zipfile(os.path.join(CACHE_DIR, filename), os.path.join(CACHE_DIR, year))
    return read_csv_file(year, base)

if __name__ == '__main__':
    logger.info('Iniciando descarga de archivos')
    get_base_eah('2011', 'ind')