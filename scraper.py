import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_fenabs():
    base_url = "https://stats.fenabs.es/2026/b_division1/"
    data = {
        "actualizado": "12/05/2026",
        "clasificacion": [],
        "top_bateadores": [],
        "top_lanzadores": []
    }

    try:
        # 1. CLASIFICACIÓN
        res = requests.get(base_url + "cla.php")
        soup = BeautifulSoup(res.text, 'html.parser')
        tabla = soup.find('table')
        if tabla:
            filas = tabla.find_all('tr')[2:]
            for f in filas:
                cols = f.find_all('td')
                if len(cols) >= 6:
                    data["clasificacion"].append({
                        "pos": cols[0].text.strip(),
                        "equipo": cols[1].text.strip(),
                        "pj": cols[2].text.strip(),
                        "pg": cols[3].text.strip(),
                        "pp": cols[4].text.strip(),
                        "avg": cols[5].text.strip()
                    })

        # 2. DATOS DE EJEMPLO (AMAYA) - Esto se puede automatizar más leyendo stats.php
        # Basado en el código que enviaste al principio
        data["top_bateadores"] = [
            {"nombre": "MOHAMED Tasser", "equipo": "AMAYA", "stat": ".385", "tipo": "AVG", "h": 5, "rbi": 6, "puntos": [1,2,0,1,1]},
            {"nombre": "LOPEZ Andres", "equipo": "AMAYA", "stat": ".300", "tipo": "AVG", "h": 6, "rbi": 2, "puntos": [1,1,2,0,2]},
            {"nombre": "ARNAL Unax", "equipo": "AMAYA", "stat": ".286", "tipo": "AVG", "h": 6, "rbi": 3, "puntos": [0,1,3,1,1]}
        ]
        
        data["top_lanzadores"] = [
            {"nombre": "MENA Alejandro", "equipo": "AMAYA", "stat": "5.70", "tipo": "ERA", "so": 20, "puntos": [4,3,5,2,6]},
            {"nombre": "DEL ARBOL Daniel", "equipo": "AMAYA", "stat": "8.53", "tipo": "ERA", "so": 11, "puntos": [2,2,3,1,3]}
        ]

    except Exception as e:
        print(f"Error en el scraping: {e}")

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
