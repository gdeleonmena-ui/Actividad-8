from fastapi.testclient import TestClient
from app.api import app

VALID={'visitas_30d':4,'dias_ultima_compra':60,'importe_90d':1200,
       'tickets_soporte':2,'descuento_promedio':0.1,'canal':'app','tipo_cliente':'nuevo'}

def test_metrics_count_and_tracing():
    with TestClient(app) as client:
        r=client.post('/predict',json=VALID,headers={'x-trace-id':'test-correlation-100'})
        assert r.status_code==200
        assert r.headers['x-trace-id']=='test-correlation-100'
        stats=client.get('/metrics').json()
        assert stats['scope']=='single_process_ephemeral'
        assert any(x['route']=='/predict' and x['status']==200 for x in stats['counts'])
        assert '/predict' in stats['latency']

def test_no_input_content_in_metrics():
    with TestClient(app) as client:
        client.post('/predict',json={**VALID,'importe_90d':1234})
        payload=client.get('/metrics').text
        assert '1234' not in payload
