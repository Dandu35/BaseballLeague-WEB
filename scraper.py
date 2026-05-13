import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo_completo(url, equipo_nombre):
    jugadores = []
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        texto = res.text
        
        # 1. Identificar lanzadores
        pitchers_names = []
        if "PITCHING ANALYSIS" in texto:
            p_seccion = texto.split("PITCHING ANALYSIS")[1].split("-----------------")[1]
            p_lineas = p_seccion.split('\n')
            for pl in p_lineas:
                m_p = re.search(r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+', pl)
                if m_p: pitchers_names.append(m_p.group(1).strip())

        # 2. Extraer datos situacionales de bateo
        if "BATTING ANALYSIS" in texto:
            seccion_bat = texto.split("BATTING ANALYSIS")[1]
            lineas_bat = seccion_bat.split('\n')
            pattern_bat = r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+(\d+)\s+(\d+)\s+([\d.]+)'
            
            for l in lineas_bat:
                match = re.search(pattern_bat, l)
                if match:
                    nombre = match.group(1).strip()
                    if "Totals" in nombre or "Opponents" in nombre: continue
                    
                    # Lógica de posición
                    es_pitcher = nombre in pitchers_names
                    posicion = "TWO-WAY" if es_pitcher else "INFIELD"
                    
                    jugadores.append({
                        "nombre": nombre,
                        "equipo": equipo_nombre,
                        "posicion": posicion,
                        "avg_vs_r": match.group(2),
                        "avg_runners": match.group(3),
                        "avg_empty": match.group(4),
                        "fly_out": match.group(5),
                        "gnd_out": match.group(6),
                        "ratio": match.group(7)
                    })
        
        # 3. Añadir Pitchers puros (que no aparecen en bateo)
        for p_nom in pitchers_names:
            if not any(j['nombre'] == p_nom for j in jugadores):
                jugadores.append({
                    "nombre": p_nom, "equipo": equipo_nombre, "posicion": "PITCHER",
                    "avg_vs_r": ".000", "avg_runners": ".000", "avg_empty": ".000",
                    "fly_out": "0", "gnd_out": "0", "ratio": "0.0"
                })
    except Exception as e:
        print(f"Error en {equipo_nombre}: {e}")
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
    data = {"actualizado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "clasificacion": [], "jugadores": []}
    
    # Ranking
    try:
        r = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php")
        s = BeautifulSoup(r.text, 'html.parser')
        for f in s.find_all('tr'):
            cols = f.find_all('td')
            if len(cols) >= 6 and cols[0].text.strip().isdigit():
                data["clasificacion"].append({"pos": cols[0].text.strip(), "equipo": cols[1].text.strip(), "pg": cols[3].text.strip(), "pp": cols[4].text.strip(), "avg": cols[5].text.strip()})
    except: pass

    for eq, url in urls.items():
        data["jugadores"].extend(scrape_equipo_completo(url, eq))

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
