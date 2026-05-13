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
        
        # --- 1. EXTRACCIÓN DE BATEADORES ---
        if "BATTING ANALYSIS" in texto:
            seccion_bat = texto.split("BATTING ANALYSIS")[1].split("PITCHING ANALYSIS")[0]
            lineas_bat = seccion_bat.split('\n')
            pattern_bat = r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+(\d+)\s+(\d+)\s+([\d.]+)'
            
            for l in lineas_bat:
                m = re.search(pattern_bat, l)
                if m:
                    nombre = m.group(1).strip()
                    if "Totals" in nombre or "Opponents" in nombre: continue
                    jugadores.append({
                        "nombre": nombre, "equipo": equipo_nombre, "posicion": "INFIELD",
                        "avg_vs_r": m.group(2), "avg_runners": m.group(3), "avg_empty": m.group(4),
                        "fly_out": m.group(5), "gnd_out": m.group(6), "ratio": m.group(7)
                    })

        # --- 2. EXTRACCIÓN DE LANZADORES (NUEVA LÓGICA) ---
        if "PITCHING ANALYSIS" in texto:
            seccion_pit = texto.split("PITCHING ANALYSIS")[1]
            lineas_pit = seccion_pit.split('\n')
            
            # Buscamos en la primera tabla de pitcheo (Situacional)
            # Buscamos: Nombre, vs Right, w/Runners, Bases Empty
            pattern_pit = r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)'
            
            for l in lineas_pit:
                m = re.search(pattern_pit, l)
                if m:
                    nombre = m.group(1).strip()
                    if "Totals" in nombre or "Opponents" in nombre or "Player" in nombre: continue
                    
                    # Si ya existía como bateador, lo marcamos como PITCHER
                    # Si no existía (pitcher puro), lo añadimos
                    found = False
                    for j in jugadores:
                        if j["nombre"] == nombre:
                            j["posicion"] = "PITCHER"
                            found = True; break
                    
                    if not found:
                        jugadores.append({
                            "nombre": nombre, "equipo": equipo_nombre, "posicion": "PITCHER",
                            "avg_vs_r": m.group(2), "avg_runners": m.group(3), "avg_empty": m.group(4),
                            "fly_out": "0", "gnd_out": "0", "ratio": "0.0"
                        })
        
        print(f"✅ {equipo_nombre}: Procesados {len(jugadores)} jugadores/lanzadores.")
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
    data = {"actualizado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "clasificacion": [], "jugadores": []}
    
    # Clasificación
    try:
        r = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php", timeout=10)
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
