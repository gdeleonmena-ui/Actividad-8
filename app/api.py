"""API de demostración académica de abandono, no apta para decisiones reales."""
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Literal
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

MODEL_PATH = Path(os.getenv('MODEL_PATH', str(Path(__file__).resolve().parents[1] / 'models' / 'churn_pipeline.joblib')))

class Cliente(BaseModel):
    model_config = ConfigDict(extra='forbid')
    visitas_30d: int = Field(ge=0, le=500)
    dias_ultima_compra: int = Field(ge=0, le=3650)
    importe_90d: float | None = Field(default=None, ge=0, le=10000000)
    tickets_soporte: int = Field(ge=0, le=100)
    descuento_promedio: float = Field(ge=0, le=1)
    canal: Literal['app','web','tienda']
    tipo_cliente: Literal['nuevo','recurrente']

class Prediccion(BaseModel):
    clase_predicha: int
    probabilidad_abandono: float
    umbral: float
    aviso: str

@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.is_file():
        raise RuntimeError(f'Modelo ausente en {MODEL_PATH}. Ejecuta scripts/train_model.py')
    # joblib/pickle solo deben proceder de artefactos propios y confiables.
    return joblib.load(MODEL_PATH)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title='API académica de predicción de abandono', version='1.0.0', lifespan=lifespan,
              description='Modelo sintético para demostración. No usar para decisiones reales de clientes.')

@app.get('/health')
def health():
    return {'status':'ok','model_loaded':True,'version':'1.0.0'}

@app.post('/predict',response_model=Prediccion)
def predict(cliente: Cliente):
    try:
        x = pd.DataFrame([cliente.model_dump()])
        score = float(load_model().predict_proba(x)[0,1])
        threshold = float(os.getenv('DECISION_THRESHOLD','0.45'))
        if not 0 < threshold < 1:
            raise ValueError('DECISION_THRESHOLD fuera de rango')
        return Prediccion(clase_predicha=int(score >= threshold), probabilidad_abandono=round(score,6),
                         umbral=threshold,aviso='Demostración académica con datos sintéticos; no usar para decidir acciones comerciales.')
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=500,detail='Error de configuración del servidor') from exc

# Telemetria sin datos personales y endpoint auxiliar de consulta.
from app.observability import attach_telemetry
attach_telemetry(app)
