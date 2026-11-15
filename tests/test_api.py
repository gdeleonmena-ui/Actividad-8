import os
os.environ['DECISION_THRESHOLD']='0.45'
from fastapi.testclient import TestClient
from app.api import app

VALID={'visitas_30d':4,'dias_ultima_compra':60,'importe_90d':1200,'tickets_soporte':2,'descuento_promedio':0.1,'canal':'app','tipo_cliente':'nuevo'}

def test_health():
    with TestClient(app) as client:
        r=client.get('/health'); assert r.status_code==200 and r.json()['model_loaded']

def test_predict():
    with TestClient(app) as client:
        r=client.post('/predict',json=VALID); assert r.status_code==200
        data=r.json(); assert 0<=data['probabilidad_abandono']<=1
        assert data['clase_predicha'] in (0,1) and data['umbral']==0.45

def test_zero_activity_extreme():
    with TestClient(app) as client:
        data={**VALID,'visitas_30d':0,'importe_90d':None,'dias_ultima_compra':3650,'tickets_soporte':100}
        r=client.post('/predict',json=data); assert r.status_code==200

def test_negative_amount_rejected():
    with TestClient(app) as client:
        r=client.post('/predict',json={**VALID,'importe_90d':-1}); assert r.status_code==422

def test_unknown_category_rejected():
    with TestClient(app) as client:
        r=client.post('/predict',json={**VALID,'canal':'telefono'}); assert r.status_code==422

def test_missing_field_rejected():
    with TestClient(app) as client:
        invalid=VALID.copy();del invalid['visitas_30d'];assert client.post('/predict',json=invalid).status_code==422

def test_unknown_field_rejected():
    with TestClient(app) as client:
        assert client.post('/predict',json={**VALID,'password':'secret'}).status_code==422
