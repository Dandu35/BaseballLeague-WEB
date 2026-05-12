import requests
from bs4 import BeautifulSoup
import json
import datetime

def scrape_equipo(url, nombre_equipo):
    jugadores = []
    nombres_vistos = set() # Para evitar duplicados
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8' 
        soup = BeautifulSoup(res.text, 'html.parser')
        
        pre_tag = soup.find('pre')
        if not pre_tag: return []

        lineas = pre_tag.text.split('\n')
        
        empezar_bateo = False
        for linea in lineas:
            # Detectamos el inicio real de la tabla de estadísticas
            if "Sorted by Batting avg" in linea:
                empezar_bateo = True
                continue
            
            if empezar_bateo:
                # Si llegamos a los totales o líneas vacías, paramos
                if "Totals" in linea or "Opponents" in linea or len(linea.strip()) < 20:
                    if len(jugadores) > 0: break
                    else: continue
                
                # EXTRACCIÓN POR POSICIÓN FIJA (Método StatCrew)
                # En estos archivos .htm, cada dato está SIEMPRE en el mismo caracter
                nombre = linea[2:23].strip() # Nombre: caracteres del 2 al 23
                avg = linea[23:29].strip()    # AVG: caracteres del 23 al 29
                h = linea[42:46].strip()      # Hits: caracteres del 42 al 46
                rbi = linea[62:66].strip()    # RBI: caracteres del 62 al 66

                # Validaciones de seguridad:
                # 1. Que tenga un punto (el .AVG)
                # 2. Que no sea un encabezado (Player, Avg...)
                # 3. Que no hayamos visto este nombre ya
                if "." in avg and nombre not in nombres_vistos and "Player" not in nombre:
                    jugadores.append({
                        "nombre": nombre,
                        "equipo": nombre_equipo,
                        "stat": avg,
                        "tipo": "AVG",
                        "h": h,
                        "rbi": rbi,
                        "puntos": [1, 2, 1, 1, 2]
                    })
                    nombres_vistos.add(nombre)
                    
        print(f"✅ {nombre_equipo}: {len(jugadores)} jugadores únicos.")
    except Exception as e:
        print(f"❌ Error en {nombre_equipo}: {e}")
    
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

    # Captura de Clasificación (Simplificada)
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

    # Captura de Jugadores
    todos = []
    for eq, url in urls_equipos.items():
        todos.extend(scrape_equipo(url, eq))
    
    # Ordenar por AVG
    todos.sort(key=lambda x: x['stat'], reverse=True)
    data["top_bateadores"] = todos

    with open('liga_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    scrape_fenabs()
