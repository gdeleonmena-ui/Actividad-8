# Actividad 8 - Observabilidad y respuesta a incidentes para un modelo de abandono

Continuación académica del servicio FastAPI de predicción de abandono de clientes en retail omnicanal. Datos y latencias simulados; sin datos personales ni incidente real de producción.

## Contenido

- `app/api.py` y `app/observability.py`: API de referencia de Fase 2 instrumentada con logs JSON por solicitud, `trace_id` y `GET /metrics` por proceso.
- `models/`: modelo entrenado sobre datos sintéticos de la fase previa, solo para pruebas locales.
- `config/alerts.json`: SLO, alertas, ruido, prioridades y respuesta.
- `scripts/simulate_monitoring.py`: simula 18 ventanas, detecta alertas P1/P2 y ejecuta respuestas **dentro del simulador**.
- `scripts/create_dashboard.py`: dashboard HTML y gráficas PNG de métricas simuladas.
- `scripts/log_to_mlflow.py`: integración opcional, requiere `pip install mlflow`; no se presume ejecutada.
- `docs/RUNBOOKS.md`: procedimientos operativos.
- `evidence/`: CSV, logs estructurados, registro de dos incidentes, capturas gráficas y resultados de tests.

## Reproducción (Python 3.10+)

```bash
python scripts/simulate_monitoring.py
python scripts/create_dashboard.py
python -m pytest -q tests
```

Para probar la API local de ejemplo:

```bash
pip install -r requirements-api.txt
uvicorn app.api:app --host 127.0.0.1 --port 8080
```

Endpoints: `/docs`, `/health`, `/predict`, `/metrics`. El endpoint `/metrics` es únicamente por proceso y de uso local: no cuenta con almacenamiento persistente.

Para registrar métricas simuladas en MLflow de manera opcional:

```bash
pip install mlflow
python scripts/log_to_mlflow.py
```

## Alcance y limitaciones

- Las latencias, errores y distribuciones de los dashboards se **generan por simulación**, NO se recopilaron de la API real o de Cloud Run.
- Los runbooks automatizados modifican **estados simulados**; no ejecutan rollback ni reentrenan modelos reales.
- El registro MLflow está implementado de modo opcional. Su ejecución debe verificarse en el equipo del usuario antes de adjuntar capturas del panel.
- Los resultados de Fase 2 no se usan para afirmar medición en producción.
