import requests
from bs4 import BeautifulSoup
import json

def obtener_datos():
    url = "https://stats.fenabs.es/2026/b_division1/res.php"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    
    # Aquí el robot busca las filas de la tabla de resultados
    resultados = []
    filas = soup.find_all('tr')
    for fila in filas:
        # Lógica para extraer: Fecha, Equipos y Marcador
        # ... 
        pass

    # Guardamos todo en un archivo que leerá la web
    data = {
        "actualizado": "12/05/2026",
        "resultados": resultados,
        "equipos": ["AMAYA", "TOROS", "IRABIA", "ARGA", "MIRALBUENO", "SAN INAZIO"]
    }
    
    with open('liga_data.json', 'w') as f:
        json.dump(data, f)

obtener_datos()
