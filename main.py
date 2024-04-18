import requests
from bs4 import BeautifulSoup

def default_settings():
    settings = { 
        'root_url': 'https://www.estadisticaciudad.gob.ar/eyc/?cat=93',
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
    urls = [config['root_url']]
    
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
        
        
def obtener_listas_v1():
    h = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    res = requests.get(url_page, headers=h)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        bases_disponibles = {}
        for i in soup.find_all('h2'):
            bases_disponibles[i.text.split(' ')[-1]] = i.a.get('href')
        url_page2 = soup.find('div', class_='pagination').find('a', class_='paginador-derecha').get('href')
        res2 = requests.get(url_page2, headers=h)
        if res2.status_code == 200:
            soup2 = BeautifulSoup(res2.text, 'html.parser')
            for i in soup2.find_all('h2'):
                bases_disponibles[i.text.split(' ')[-1]] = i.a.get('href')
    return bases_disponibles

print(obtener_listas_v1_1())