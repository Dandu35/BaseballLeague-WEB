import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo_situacional(url, equipo_nombre):
    jugadores = []
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        texto = res.text
        
        # Localizamos la sección de análisis
        if "BATTING ANALYSIS" not in texto:
            return []
            
        seccion = texto.split("BATTING ANALYSIS")[1]
        lineas = seccion.split('\n')
        
        for l in lineas:
            # Esta REGEX busca: 
            # 1. Número y Nombre
            # 2. vs Left (H, AB, Avg)
            # 3. vs Right (H, AB, Avg) -> CAPTURAMOS ESTE
            # 4. w/Runners (H, AB, Avg) -> CAPTURAMOS ESTE
            # 5. Bases Empty (H, AB, Avg) -> CAPTURAMOS ESTE
            # 6. Fly Out, Gnd Out -> CAPTURAMOS ESTOS
            
            # Expresión regular ajustada a las columnas de FENABS
            pattern = r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+\d+\s+\d+\s+[\w.-]+\s+(\d+)\s+(\d+)\s+([\d.]+)'
            
            match = re.search(pattern, l)
            
            if match:
                nombre = match.group(1).strip()
                if "Totals" in nombre or "Opponents" in nombre: continue
                
                jugadores.append({
                    "nombre": nombre,
                    "equipo": equipo_nombre,
                    "avg_vs_r": match.group(2),
                    "avg_runners": match.group(3),
                    "avg_empty": match.group(4),
                    "fly_out": match.group(5),
                    "gnd_out": match.group(6),
                    "ratio": match.group(7),
                    "puntos_grafico": [match.group(2), match.group(3), match.group(4)]
                })
        print(f"✅ {equipo_nombre}: capturados {len(jugadores)} jugadores de la tabla de análisis.")
    except Exception as e:
        print(f"❌ Error en {equipo_nombre}: {e}")
    return jugadores

def scrape_fenabs():
    urls = {
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
        "jugadores": []
    }

    # Scrape Clasificación
    try:
        r = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php")
        s = BeautifulSoup(r.text, 'html.parser')
        for f in s.find_all('tr'):
            cols = f.find_all('td')
            if len(cols) >= 6 and cols[0].text.strip().isdigit():
                data["clasificacion"].append({
                    "pos": cols[0].text.strip(),
                    "equipo": cols[1].text.strip(),
                    "pg": cols[3].text.strip(),
                    "pp": cols[4].text.strip(),
                    "avg": cols[5].text.strip()
                })
    except: pass

    for eq, url in urls.items():
        data["jugadores"].extend(scrape_equipo_situacional(url, eq))

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
