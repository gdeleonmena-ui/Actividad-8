# Validación — Actividad 8

## Evidencia ejecutada (2026-11-15)

- `python scripts/simulate_monitoring.py`: 18 ventanas de 100 solicitudes simuladas, semilla 42.
- `python scripts/create_dashboard.py`: generó figuras y dashboard HTML a partir del CSV.
- `python -m pytest -q tests`: 13 pruebas aprobadas (7 API, 2 observabilidad, 4 simulación).
- P1 INC-001 (latencia p95): 779.2 ms al detectar; 142.4 ms en ventana de recuperación.
- P2 INC-002 (PSI): 0.752 al detectar; 0.0007 en ventana de recuperación.
- Disponibilidad simulada: 99.6667% (1,794/1,800). Presupuesto de errores: 18; 6 consumidos.

## Qué se validó y qué no

Se comprobó con `TestClient` la carga del modelo y la API, instrumentación `/metrics` y la correlación `x-trace-id`. Se verificó el simulador y sus acciones **de estado**. La simulación no mide latencia real de FastAPI ni ejecuta rollback, reentrenamiento o alertas en infraestructura productiva. Los logs son sintéticos. `scripts/log_to_mlflow.py` está preparado para registrar los artefactos en SQLite si MLflow se instala; no se adjunta captura de MLflow.

## Correspondencia con la rúbrica

1. Métricas, logs, trazas: `app/observability.py`, `evidence/structured_events.jsonl`, métricas CSV y SLO en `config/alerts.json`.
2. Alertas inteligentes: severidad P1/P2, persistencia dos ventanas, cooldown, error budget y enfoque de reducción de ruido.
3. Dos incidentes y runbooks: `docs/RUNBOOKS.md`, `evidence/incident_register.json` y gráficas antes/después.
4. Respuesta automatizada: `scripts/simulate_monitoring.py`, eventos de escalamiento, cambio de estado de revisión humana, recuperación y pruebas.
