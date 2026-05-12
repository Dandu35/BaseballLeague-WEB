import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo(url, equipo_nombre):
    jugadores = []
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        texto = res.text
        
        # --- EXTRACCIÓN DE BATEO SITUACIONAL ---
        # Buscamos la tabla "BATTING ANALYSIS"
        analysis_part = texto.split("BATTING ANALYSIS")[1].split("------------------------------------------------------------------------------------------------------------------------------------")[1]
        lineas = analysis_part.split('\n')
        
        for l in lineas:
            # Regex para capturar: Nombre, vs Right, w/Runners, Bases Empty y Fly/Gnd
            m = re.search(r'([A-Za-z\s\.,]+)\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+\d+\s+\d+\s+(\.\d{3})\s+\d+\s+\d+\s+(\.\d{3})\s+\d+\s+\d+\s+(\.\d{3}).*?(\d+)\s+(\d+)\s+([\d.]+)', l)
            if m:
                jugadores.append({
                    "nombre": m.group(1).strip(),
                    "equipo": equipo_nombre,
                    "avg_vs_r": m.group(2),
                    "avg_w_runners": m.group(3),
                    "avg_empty": m.group(4),
                    "fly_outs": m.group(5),
                    "ground_outs": m.group(6),
                    "ratio_fly_gnd": m.group(7),
                    "tipo": "BATEADOR"
                })
        
        print(f"✅ {equipo_nombre}: {len(jugadores)} analizados.")
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

    # Clasificación
    try:
        r = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php")
        s = BeautifulSoup(r.text, 'html.parser')
        for f in s.find_all('tr'):
            cols = f.find_all('td')
            if len(cols) >= 6 and cols[0].text.strip().isdigit():
                data["clasificacion"].append({
                    "pos": cols[0].text.strip(), "equipo": cols[1].text.strip(),
                    "pg": cols[3].text.strip(), "pp": cols[4].text.strip(), "avg": cols[5].text.strip()
                })
    except: pass

    for eq, url in urls.items():
        data["jugadores"].extend(scrape_equipo(url, eq))

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
