import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo(url, nombre_equipo):
    jugadores = []
    try:
        # Añadimos un User-Agent para que la web no nos bloquee
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8' 
        
        # FENABS usa texto preformateado, el texto plano es más fiable que el HTML
        soup = BeautifulSoup(res.text, 'html.parser')
        texto_completo = soup.get_text()
        lineas = texto_completo.split('\n')
        
        for linea in lineas:
            linea = linea.strip()
            
            # Buscamos el patrón: un número, un nombre largo, y un .AVG (ej: .385)
            # Esta expresión regular es mucho más flexible
            match = re.search(r'(\d+)\s+([A-Za-z\s\.,]+)\s+(\.\d{3})', linea)
            
            if match:
                numero = match.group(1)
                nombre = match.group(2).strip()
                avg = match.group(3)
                
                # Para evitar basura, el nombre debe tener al menos 5 caracteres
                if len(nombre) > 5 and "Totals" not in nombre and "Opponents" not in nombre:
                    # Intentamos sacar H y RBI buscando los números que siguen al AVG
                    partes = linea.split(avg)[1].split()
                    h = partes[3] if len(partes) > 3 else "0"
                    rbi = partes[7] if len(partes) > 7 else "0"
                    
                    jugadores.append({
                        "nombre": nombre,
                        "equipo": nombre_equipo,
                        "stat": avg,
                        "tipo": "AVG",
                        "h": h,
                        "rbi": rbi,
                        "puntos": [1, 2, 1, 1, 2]
                    })
        print(f"✅ {nombre_equipo}: Encontrados {len(jugadores)} jugadores.")
    except Exception as e:
        print(f"❌ Error en {nombre_equipo}: {e}")
    
    return jugadores

def scrape_fenabs():
    # Diccionario completo de URLs del Grupo Norte
    urls_equipos = {
        "AMAYA": "https://stats.fenabs.es/2026/b_division1/stats/ama.htm",
        "IRABIA": "https://stats.fenabs.es/2026/b_division1/stats/ira.htm",
        "MIRALBUENO": "https://stats.fenabs.es/2026/b_division1/stats/mir.htm",
        "TOROS": "https://stats.fenabs.es/2026/b_division1/stats/tor.htm",
        "ARGA": "https://stats.fenabs.es/2026/b_division1/stats/arg.htm",
        "SAN INAZIO": "https://stats.fenabs.es/2026/b_division1/stats/ina.htm"
    }

    data = {
        "actualizado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "clasificacion": [],
        "top_bateadores": [],
        "top_lanzadores": []
    }

    # Captura de Clasificación
    try:
        res_cla = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php", timeout=10)
        soup_cla = BeautifulSoup(res_cla.text, 'html.parser')
        for f in soup_cla.find_all('tr'):
            cols = f.find_all('td')
            if len(cols) >= 6 and cols[0].text.strip().isdigit():
                data["clasificacion"].append({
                    "pos": cols[0].text.strip(),
                    "equipo": cols[1].text.strip(),
                    "pj": cols[2].text.strip(),
                    "pg": cols[3].text.strip(),
                    "pp": cols[4].text.strip(),
                    "avg": cols[5].text.strip()
                })
    except: pass

    # Captura de Jugadores Equipo por Equipo
    todos = []
    for eq, url in urls_equipos.items():
        todos.extend(scrape_equipo(url, eq))
    
    # Ordenar por AVG de mayor a menor
    todos.sort(key=lambda x: x['stat'], reverse=True)
    data["top_bateadores"] = todos

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
