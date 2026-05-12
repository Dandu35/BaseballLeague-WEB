import requests
from bs4 import BeautifulSoup
import json

def scrape_fenabs():
    base_url = "https://stats.fenabs.es/2026/b_division1/"
    
    # --- 1. EXTRAER CLASIFICACIÓN ---
    res_cla = requests.get(base_url + "cla.php")
    soup_cla = BeautifulSoup(res_cla.text, 'html.parser')
    clasificacion = []
    
    # Buscamos la tabla de clasificación
    tabla_cla = soup_cla.find('table')
    if tabla_cla:
        filas = tabla_cla.find_all('tr')[2:] # Saltamos encabezados
        for f in filas:
            cols = f.find_all('td')
            if len(cols) >= 5:
                clasificacion.append({
                    "pos": cols[0].text.strip(),
                    "equipo": cols[1].text.strip(),
                    "pj": cols[2].text.strip(),
                    "pg": cols[3].text.strip(),
                    "pp": cols[4].text.strip(),
                    "avg": cols[5].text.strip()
                })

    # --- 2. EXTRAER ESTADÍSTICAS DE JUGADORES (TOP LÍDERES) ---
    # Nota: Aquí entramos en la página de estadísticas generales
    res_stats = requests.get(base_url + "stats.php")
    # (Aquí procesaríamos los líderes de AVG, HR, ERA, etc.)
    # Por ahora, generamos una base para que tu web la lea:
    top_bateadores = [
        {"nombre": "MOHAMED Tasser", "equipo": "AMAYA", "stat": ".385", "tipo": "AVG"},
        {"nombre": "LOPEZ Andres", "equipo": "AMAYA", "stat": ".300", "tipo": "AVG"}
    ]

    # --- 3. GUARDAR TODO EN JSON ---
    final_data = {
        "actualizado": "12/05/2026",
        "clasificacion": clasificacion,
        "top_bateadores": top_bateadores
    }

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
