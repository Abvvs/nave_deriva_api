import math
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
#from .schemas import StatusResponse
import random

from pydantic import BaseModel

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
saturation_data = {
    10: {"v_l": 0.0035, "v_v": 0.0035},  # punto crítico
    5: {"v_l": 0.0012, "v_v": 0.02},
    1: {"v_l": 0.001, "v_v": 0.1},
    0.05: {"v_l": 0.00105, "v_v": 30.0},  # aproximado de la imagen
    # puedes seguir llenando con más valores
}

# Se asume que todos los valores de presión en este diccionario tienen T > 30 °C
MIN_PRESSURE = 0.05  # MPa
MAX_PRESSURE = 10.0  # MPa

class PhaseChangeResponse(BaseModel):
    specific_volume_liquid: float
    specific_volume_vapor: float

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

@app.get("/phase-change-diagram", response_model=PhaseChangeResponse)
def get_phase_change_data(pressure: float = Query(..., gt=0)):
    if pressure not in saturation_data:
        raise HTTPException(
            status_code=404,
            detail=f"No data available for pressure={pressure} MPa or T <= 30°C"
        )
    data = saturation_data[pressure]
    return {
        "specific_volume_liquid": data["v_l"],
        "specific_volume_vapor": data["v_v"]
    }