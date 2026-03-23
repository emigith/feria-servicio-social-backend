from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(title="Feria Servicio Social API", version="0.1.0")

# CORS — permite llamadas desde archivos HTML locales y cualquier origen en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción (semana 8) cambiar por dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Feria Servicio Social API running"}