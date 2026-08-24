from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import re
import requests

app = FastAPI(title="Control de Gastos API")

# Tu webhook de Google Apps Script
GOOGLE_SHEETS_WEBHOOK = "https://script.google.com/macros/s/AKfycbxfjANkic47syU1Z7dOQicC3q9etq-kxXUN45zfev4yfu0CcvNWHXprDG1AUYFfy3CXng/exec"

class Transaccion(BaseModel):
    fecha: str = ""
    comercio: str = "Comercio de prueba"
    monto: str = "0.00"
    categoria: str = ""
    tarjeta: str = "Mastercard"

def auto_categorizar(comercio: str) -> str:
    nombre = comercio.lower()
    
    reglas = {
        "Supermercado": ["super", "la torre", "paiz", "walmart", "pricesmart", "summa"],
        "Restaurantes y Café": ["cafe", "coffee", "starbucks", "mcdonald", "san martin", "restaurante", "bar", "pizza", "burger", "tacos", "anfora"],
        "Transporte y Gasolina": ["uber", "didi", "gasolinera", "shell", "puma", "uno", "texaco"],
        "Salud y Fitness": ["gym", "smartfit", "gimnasio", "farmacia", "meykos", "galeno", "cruz verde", "suplementos", "gnc"],
        "Servicios y Suscripciones": ["spotify", "netflix", "apple", "google", "amazon", "claro", "tigo", "eegsa", "empagua"]
    }
    
    for categoria, palabras_clave in reglas.items():
        if any(palabra in nombre for palabra in palabras_clave):
            return categoria
            
    return "Otros / General"

def limpiar_monto(monto_raw: str) -> float:
    try:
        limpio = re.sub(r"[^\d.]", "", str(monto_raw).replace(",", ""))
        return float(limpio) if limpio else 0.0
    except Exception:
        return 0.0

@app.get("/")
def home():
    return {"status": "online", "message": "API de control de gastos activa"}

@app.post("/transaccion")
def recibir_transaccion(item: Transaccion):
    monto_numerico = limpiar_monto(item.monto)
    categoria_final = item.categoria if item.categoria else auto_categorizar(item.comercio)
    fecha_final = item.fecha if item.fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    payload = {
        "fecha": fecha_final,
        "comercio": item.comercio.strip(),
        "monto": str(monto_numerico),
        "categoria": categoria_final,
        "tarjeta": item.tarjeta
    }
    
    # Reenvío de datos limpios y categorizados a Google Sheets
    try:
        res = requests.post(GOOGLE_SHEETS_WEBHOOK, json=payload, timeout=10)
        sheets_status = res.status_code
    except Exception as e:
        sheets_status = str(e)
    
    return {
        "status": "ok",
        "datos": payload,
        "sheets_response": sheets_status
    }
    
    return {
        "status": "ok",
        "datos": registro
    }
