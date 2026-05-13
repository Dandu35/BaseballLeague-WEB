import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

def scrape_equipo_completo(url, equipo_nombre):
    jugadores = {}
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        texto = res.text

        # --- 1. TOTALES ACUMULADOS (Bateo General) ---
        if "Sorted by Batting avg" in texto:
            sec_std = texto.split("Sorted by Batting avg")[1].split("BATTING ANALYSIS")[0]
            for l in sec_std.split('\n'):
                # Captura: Nombre, AVG, G, AB, R, H, 2B, 3B, HR, RBI, TB, SLG, BB, HBP, SO, OB%...
                m = re.search(r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+([\w.-]+)\s+[\d-]+\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+\s+(\d+)\s+[\d.]+\s+[\d.]+\s+(\d+)\s+\d+\s+(\d+)', l)
                if m:
                    nom = m.group(1).strip()
                    if "Totals" in nom or "Opponents" in nom: continue
                    jugadores[nom] = {
                        "nombre": nom, "equipo": equipo_nombre, "posicion": "BATTER",
                        "avg": m.group(2), "ab": m.group(3), "r": m.group(4), "h": m.group(5),
                        "rbi": m.group(6), "bb": m.group(7), "so": m.group(8)
                    }

        # --- 2. DATOS SITUACIONALES Y AVANZADOS (Análisis) ---
        if "BATTING ANALYSIS" in texto:
            sec_ana = texto.split("BATTING ANALYSIS")[1]
            # AVG Situacionales
            pat_sit = r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+(\d+)\s+(\d+)\s+([\d.]+)'
            for l in sec_ana.split('\n'):
                ms = re.search(pat_sit, l)
                if ms and ms.group(1).strip() in jugadores:
                    jugadores[ms.group(1).strip()].update({
                        "vs_r": ms.group(2), "clutch": ms.group(3), "empty": ms.group(4),
                        "leadoff": ms.group(5), "fly": ms.group(6), "gnd": ms.group(7), "ratio": ms.group(8)
                    })
            # KL, ERR, LOB, FC
            for l in sec_ana.split('\n'):
                m_adv = re.search(r'([A-Za-z\s\.,]+)\.+\s+.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$', l)
                if m_adv and m_adv.group(1).strip() in jugadores:
                    jugadores[m_adv.group(1).strip()].update({
                        "lob": m_adv.group(2), "err": m_adv.group(3), "fc": m_adv.group(4), "kl": m_adv.group(5)
                    })

        # --- 3. DATOS DE PITCHEO ---
        if "PITCHING ANALYSIS" in texto:
            sec_pit = texto.split("PITCHING ANALYSIS")[1]
            for l in sec_pit.split('\n'):
                mp = re.search(r'^\s*\d*\s*([A-Za-z\s\.,]+)\.+\s+[\d-]+\s+[\d-]+\s+[\w.-]+\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)\s+[\d-]+\s+[\d-]+\s+([\w.-]+)', l)
                if mp:
                    n = mp.group(1).strip()
                    if n in jugadores: 
                        jugadores[n]["posicion"] = "TWO-WAY"
                        jugadores[n].update({"p_vs_r": mp.group(2), "p_runners": mp.group(3)})
                    elif "Totals" not in n:
                        jugadores[n] = {"nombre": n, "equipo": equipo_nombre, "posicion": "PITCHER", "p_vs_r": mp.group(2), "p_runners": mp.group(3)}

    except Exception as e: print(f"Error: {e}")
    return list(jugadores.values())

def scrape_fenabs():
    urls = {"AMAYA": "https://stats.fenabs.es/2026/b_division1/stats/ama.htm", "IRABIA": "https://stats.fenabs.es/2026/b_division1/stats/ira.htm", "MIRALBUENO": "https://stats.fenabs.es/2026/b_division1/stats/mir.htm", "TOROS": "https://stats.fenabs.es/2026/b_division1/stats/tor.htm", "ARGA": "https://stats.fenabs.es/2026/b_division1/stats/arg.htm", "SAN INAZIO": "https://stats.fenabs.es/2026/b_division1/stats/ina.htm"}
    data = {"actualizado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "clasificacion": [], "jugadores": []}
    try:
        r = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php")
        s = BeautifulSoup(r.text, 'html.parser')
        for f in s.find_all('tr'):
            cols = f.find_all('td')
            if len(cols) >= 6 and cols[0].text.strip().isdigit():
                data["clasificacion"].append({"pos": cols[0].text.strip(), "equipo": cols[1].text.strip(), "pg": cols[3].text.strip(), "pp": cols[4].text.strip(), "avg": cols[5].text.strip()})
    except: pass
    for eq, url in urls.items(): data["jugadores"].extend(scrape_equipo_completo(url, eq))
    with open('liga_data.json', 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__": scrape_fenabs()
