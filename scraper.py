import requests
from bs4 import BeautifulSoup
import json
import datetime

def scrape_equipo(url, nombre_equipo):
    jugadores = []
    try:
        res = requests.get(url)
        # Forzamos codificación para evitar errores con tildes o eñes
        res.encoding = 'utf-8' 
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # En las páginas .htm de FENABS, los datos suelen estar en etiquetas <pre>
        pre_tag = soup.find('pre')
        if not pre_tag:
            return []

        # Convertimos el texto del <pre> en líneas para procesarlas
        lineas = pre_tag.text.split('\n')
        
        # Buscamos la sección de bateo (Sorted by Batting avg)
        empezar_bateo = False
        for linea in lineas:
            if "Sorted by Batting avg" in linea:
                empezar_bateo = True
                continue
            
            if empezar_bateo and len(linea.strip()) > 30:
                # Si llegamos a los totales, paramos
                if "Totals" in linea or "Opponents" in linea:
                    break
                
                # Extraemos datos por posición de caracteres (es texto preformateado)
                # Basado en la estructura estándar de StatCrew/FENABS
                nombre = linea[3:24].strip()
                avg = linea[24:29].strip()
                h = linea[43:47].strip()
                rbi = linea[63:67].strip()
                
                if avg.startswith('.'): # Validamos que sea una línea de jugador
                    jugadores.append({
                        "nombre": nombre,
                        "equipo": nombre_equipo,
                        "stat": avg,
                        "tipo": "AVG",
                        "h": h,
                        "rbi": rbi,
                        "puntos": [1, 2, 1, 0, 1] # Datos para el gráfico
                    })
    except Exception as e:
        print(f"Error parseando {nombre_equipo}: {e}")
    
    return jugadores

def scrape_fenabs():
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

    # 1. CLASIFICACIÓN (Mantenemos la lógica de la página principal)
    try:
        res_cla = requests.get("https://stats.fenabs.es/2026/b_division1/cla.php")
        soup_cla = BeautifulSoup(res_cla.text, 'html.parser')
        tabla_cla = soup_cla.find('table')
        if tabla_cla:
            for f in tabla_cla.find_all('tr')[2:]:
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
    except: pass

    # 2. JUGADORES EQUIPO POR EQUIPO
    todos_los_jugadores = []
    for equipo, url in urls_equipos.items():
        print(f"Extrayendo datos de {equipo}...")
        jugadores_equipo = scrape_equipo(url, equipo)
        todos_los_jugadores.extend(jugadores_equipo)

    # Ordenamos por AVG para mostrar los mejores primero
    todos_los_jugadores.sort(key=lambda x: x['stat'], reverse=True)
    data["top_bateadores"] = todos_los_jugadores

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
