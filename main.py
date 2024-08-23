import requests
import os
import pandas as pd
import zipfile
from bs4 import BeautifulSoup
from pprint import pprint

def default_settings():
    settings = { 
        'eah_url': 'https://www.estadisticaciudad.gob.ar/eyc/?cat=93',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'parser': 'html.parser'
    }
    return settings

def get_pagination_v1():
    # configuración inicial
    config = default_settings()
    h = {
        'user-agent': config['user-agent']
    }
    urls = [config['eah_url']]
    
    # get a url root o inicial
    root = requests.get(urls[0], headers=h)
    
    # si no hay error de página extraemos links de paginado
    if root.status_code < 400:
        soup = BeautifulSoup(root.text, config['parser'])
        paginado = soup.find_all('a', class_='inactive')
        for i in paginado:
            pg = i.get('href')
            urls.append(pg)
        return urls
    else:
        return root.status_code
    
def obtener_listas_v1_1():
    # configuración inicial
    config = default_settings()
    h = {
        'user-agent': config['user-agent']
    }
    urls = get_pagination_v1()
    bases = {}
    
    for url in urls:
        req = requests.get(url, headers=h)
        if req.status_code < 400:
            soup = BeautifulSoup(req.text, config['parser'])
            for i in soup.find_all('h2'):
                bases[i.text.split(' ')[-1]] = i.a.get('href')
        else:
            print(f'Error al descargar bases: {url} no responde, código de error: {req.status_code}')
    
    return bases

def get_file(year):
    config = default_settings()
    h = {
        'user-agent': config['user-agent']
    }
    bases = obtener_listas_v1_1()
    loc = bases[year]
    req = requests.get(loc, headers=h)
    if req.status_code < 400:
        soup = BeautifulSoup(req.text, config['parser'])
        file_url = soup.find('div', class_='entry-content').a.get('href')
        try:
            file = requests.get(file_url)
            if not os.path.exists('cache'):
                os.mkdir('cache')
            with open(f'cache/eah-{year}.zip', 'wb') as f:
                f.write(file.content)
            return print('Descarga exitosa')
        except:
            return print('Revisar error')

def extraer_archivos(nombre_archivo_zip, directorio_destino):
    with zipfile.ZipFile(nombre_archivo_zip, 'r') as archivo_zip:
        archivo_zip.extractall(directorio_destino)

def descomprimir_archivo_requerido(year):
    path = f'cache/eah-{year}.zip'
    extraer_archivos(nombre_archivo_zip=path, directorio_destino=f'cache/eah-{year}')


def get_base_eah(year, base):
    get_file(year=year)
    descomprimir_archivo_requerido(year=year)
    if base in ['ind', 'hog']:
        df = pd.read_csv(f'cache/eah-{year}/eah{year}_bu_ampliada_{base}.txt', sep=';', encoding='utf-8')
        return df
    else:
        print(f'El valor del parámetro {base} es inválido\nEl valor de base debe ser ind o hog, según desee obtener la base de datos individual o de hogares de la EAH del año {year}')
        

pprint(obtener_listas_v1_1())
get_file('2013')
