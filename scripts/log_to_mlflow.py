"""Integracion OPCIONAL con MLflow (no ejecutada en el entorno de creación).
Instalar: pip install mlflow
Usa SQLite para evitar el backend file-store en mantenimiento.
"""
import json
from pathlib import Path

def main():
    import mlflow
    root=Path(__file__).resolve().parents[1]
    evidence=root/'evidence'
    summary=json.loads((evidence/'simulation_summary.json').read_text(encoding='utf-8'))
    mlflow.set_tracking_uri('sqlite:///'+str((root/'mlflow_monitoring.db').resolve()))
    mlflow.set_experiment('Actividad8_Monitorizacion_Simulada')
    with mlflow.start_run(run_name='simulacion_incidentes_seed42'):
        mlflow.set_tag('datos','sinteticos_no_produccion')
        mlflow.log_param('seed',summary['seed'])
        mlflow.log_param('slo_availability',.99)
        mlflow.log_metrics({'availability_simulated':summary['period_availability'],
           'error_budget_remaining':summary['error_budget_remaining'],
           'incident_count':len(summary['incidents'])})
        for name in ['simulation_summary.json','metrics_windows.csv','structured_events.jsonl',
                     'dashboard_operativo.png','dashboard_drift.png','incident_register.json']:
            mlflow.log_artifact(str(evidence/name),artifact_path='simulation_evidence')
    print('Run MLflow registrado en SQLite, origen: simulación académica')
if __name__=='__main__':main()
