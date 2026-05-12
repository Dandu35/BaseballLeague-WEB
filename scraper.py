import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo(url, nombre_equipo):
    jugadores = []
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8' 
        soup = BeautifulSoup(res.text, 'html.parser')
        
        texto = soup.get_text()
        lineas = texto.split('\n')
        
        # Buscamos la sección de bateo de forma más flexible
        buscando_bateo = False
        for linea in lineas:
            # Detectamos el inicio de la tabla de bateo
            if "Batting avg" in linea or "AVG" in linea and "GP-GS" in linea:
                buscando_bateo = True
                continue
            
            if buscando_bateo:
                # Si llegamos al final de la tabla, paramos
                if "Totals" in linea or "Opponents" in linea or len(linea.strip()) < 10:
                    if len(jugadores) > 0: break 
                    else: continue

                # Usamos una expresión regular para limpiar la línea
                # Buscamos: Numero Nombre (letras y espacios) .AVG
                match = re.search(r'(\d+)\s+([A-Za-z\s\.]+)\s+(\.\d{3})', linea)
                if match:
                    num = match.group(1)
                    nombre = match.group(2).strip()
                    avg = match.group(3)
                    
                    # Intentamos coger Hits y RBIs buscando números después del AVG
                    resto = linea[linea.find(avg) + len(avg):].split()
                    h = resto[3] if len(resto) > 3 else "0"
                    rbi = resto[7] if len(resto) > 7 else "0"

                    jugadores.append({
                        "nombre": f"{nombre}",
                        "equipo": nombre_equipo,
                        "stat": avg,
                        "tipo": "AVG",
                        "h": h,
                        "rbi": rbi,
                        "puntos": [1, 2, 1, 1, 2]
                    })
    except Exception as e:
        print(f"Error en {nombre_equipo}: {e}")
    
    return jugadores

def scrape_fenabs():
    # URLs actualizadas
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

    # 1. CLASIFICACIÓN (Simplificada para asegurar captura)
    try:
        res_cla = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php", timeout=10)
        soup_cla = BeautifulSoup(res_cla.text, 'html.parser')
        filas = soup_cla.find_all('tr')
        for f in filas:
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

    # 2. JUGADORES
    todos = []
    for eq, url in urls_equipos.items():
        todos.extend(scrape_equipo(url, eq))
    
    # Ordenamos por AVG (de mayor a menor)
    todos.sort(key=lambda x: x['stat'], reverse=True)
    data["top_bateadores"] = todos

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
