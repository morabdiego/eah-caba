import requests
from bs4 import BeautifulSoup

def get_pagination():
    # configuración inicial
    root_url = 'https://www.estadisticaciudad.gob.ar/eyc/?cat=6215'
    h = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
    urls = [root_url]
    root = requests.get(urls[0], headers=h)
    parser = 'html.parser'
    soup = BeautifulSoup(root.text, parser)
    paginas = soup.find_all('a', class_='inactive')
    
    for pagina in paginas:
        pg = pagina.get('href')
        urls.append(pg)
    
    return urls

print(get_pagination())