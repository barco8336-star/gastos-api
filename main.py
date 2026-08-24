from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import re
import requests

app = FastAPI(title="Control de Gastos API")

# Modelo de datos que enviará el iPhone
class Transaccion(BaseModel):
    fecha: str = ""
    comercio: str
    monto: str
    categoria: str = ""
    tarjeta: str = "Mastercard"

# Función para categorizar comercios automáticamente
def auto_categorizar(comercio: str) -> str:
    nombre = comercio.lower()
    
    reglas = {
        "Supermercado": ["super", "la torre", "paiz", "walmart", "pricesmart", "summa"],
        "Restaurantes y Café": ["cafe", "coffee", "starbucks", "mcdonald", "san martin", "restaurante", "bar", "pizza", "burger", "tacos"],
        "Transporte y Gasolina": ["uber", "didi", "gasolinera", "shell", "puma", "uno", "texaco"],
        "Salud y Fitness": ["gym", "smartfit", "gimnasio", "farmacia", "meykos", "galeno", "cruz verde", "suplementos"],
        "Servicios y Suscripciones": ["spotify", "netflix", "apple", "google", "amazon", "claro", "tigo", "eegsa", "empagua"]
    }
    
    for categoria, palabras_clave in reglas.items():
        if any(palabra in nombre for palabra in palabras_clave):
            return categoria
            
    return "Otros / General"

# Función para limpiar el monto a número flotante
def limpiar_monto(monto_raw: str) -> float:
    try:
        # Remueve símbolos como Q, $, comas y espacios
        limpio = re.sub(r"[^\d.]", "", monto_raw.replace(",", ""))
        return float(limpio) if limpio else 0.0
    except Exception:
        return 0.0

@app.get("/")
def home():
    return {"status": "online", "message": "API de control de gastos activa"}

@app.post("/transaccion")
def recibir_transaccion(item: Transaccion):
    # 1. Limpieza de datos
    monto_numerico = limpiar_monto(item.monto)
    categoria_final = item.categoria if item.categoria else auto_categorizar(item.comercio)
    fecha_final = item.fecha if item.fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    registro = {
        "fecha": fecha_final,
        "comercio": item.comercio.strip(),
        "monto": monto_numerico,
        "categoria": categoria_final,
        "tarjeta": item.tarjeta
    }
    
    # Aquí puedes imprimir en consola o conectarlo a tu base de datos / hoja
    print(f"Nuevo gasto registrado: {registro}")
    
    return {
        "status": "ok",
        "datos": registro
    }