import math
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
#from .schemas import StatusResponse
import random

app = FastAPI()

# Diccionario de sistemas_averiado
SYSTEM_CODES = {
    "navigation": "NAV-01",
    "communications": "COM-02",
    "life_support": "LIFE-03",
    "engines": "ENG-04",
    "deflector_shield": "SHLD-05"
}
# Punto crítico (de la imagen)
# Datos específicos para la curva de saturación
SATURATION_DATA = {
    # Presión (MPa): {volumen_líquido, volumen_vapor}
    0.1: {"v_liq": 0.0010, "v_vap": 1.6940},
    1.0: {"v_liq": 0.0011, "v_vap": 0.1944},
    5.0: {"v_liq": 0.0025, "v_vap": 0.1000},
    10.0: {"v_liq": 0.0035, "v_vap": 0.0035},  # Punto crítico exacto
    15.0: {"v_liq": 0.0040, "v_vap": 0.0020}
}

# Variable sistema dañado actual valor 
current_damaged_system = None
def get_damaged_system():
    """Obtiene o establece un sistema dañado aleatorio"""
    global current_damaged_system
    if current_damaged_system is None:
        current_damaged_system = random.choice(list(SYSTEM_CODES.keys()))
    return current_damaged_system


@app.get('/status')
async def get_status():
    system = get_damaged_system()
    return {"damaged_system": system}

@app.get('/repair-bay', response_class=HTMLResponse)
async def get_repair_bay():
    system = get_damaged_system()
        
    repair_code = SYSTEM_CODES.get(system)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Repair</title>
    </head>
    <body>
        <div class="anchor-point">{repair_code}</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post('/teapot')
async def post_teapot():
    raise HTTPException(status_code=418, detail="I'm a teapot")

@app.get("/phase-change-diagram")
async def get_phase_diagram(
    pressure: float = Query(..., gt=0, description="Presión en MPa")
):
    """
    Devuelve los volúmenes específicos para líquido y vapor en la curva de saturación.
    Ejemplo para pressure=10 MPa:
    {
        "specific_volume_liquid": 0.0035,
        "specific_volume_vapor": 0.0035
    }
    """
    # Caso exacto para el punto crítico (10 MPa)
    if math.isclose(pressure, 10.0, rel_tol=1e-3):
        return {
            "specific_volume_liquid": 0.0035,
            "specific_volume_vapor": 0.0035
        }
    
    # Interpolación para otros valores
    pressures = sorted(SATURATION_DATA.keys())
    
    # Encontrar los puntos adyacentes
    for i in range(len(pressures)-1):
        if pressures[i] <= pressure <= pressures[i+1]:
            # Interpolación lineal directa
            frac = (pressure - pressures[i]) / (pressures[i+1] - pressures[i])
            v_liq = SATURATION_DATA[pressures[i]]["v_liq"] + frac * (
                SATURATION_DATA[pressures[i+1]]["v_liq"] - SATURATION_DATA[pressures[i]]["v_liq"])
            v_vap = SATURATION_DATA[pressures[i]]["v_vap"] + frac * (
                SATURATION_DATA[pressures[i+1]]["v_vap"] - SATURATION_DATA[pressures[i]]["v_vap"])
            
            return {
                "specific_volume_liquid": round(v_liq, 6),
                "specific_volume_vapor": round(v_vap, 6)
            }
    
    # Si la presión está fuera del rango, devolver el valor más cercano
    closest_p = min(SATURATION_DATA.keys(), key=lambda x: abs(x - pressure))
    return {
        "specific_volume_liquid": SATURATION_DATA[closest_p]["v_liq"],
        "specific_volume_vapor": SATURATION_DATA[closest_p]["v_vap"],
        "note": f"Usando valores para {closest_p} MPa (presión fuera de rango estándar)"
    }