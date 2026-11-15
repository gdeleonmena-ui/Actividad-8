"""Simulacion reproducible de observabilidad y respuesta controlada (sin produccion).

Ejecutar desde la raiz: python scripts/simulate_monitoring.py
Los valores de latencia son sinteticos y no provienen de Docker, MLflow ni usuarios reales.
"""
from __future__ import annotations
import csv, json, math, random, uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
CONF = json.loads((ROOT / 'config' / 'alerts.json').read_text(encoding='utf-8'))
RANDOM_SEED = 42
N_WINDOWS = 18
N_PER_WINDOW = CONF['slo']['window_requests']
START = datetime(2026,11,15,12,0,tzinfo=timezone.utc)


def psi(expected: list[float], observed: list[float]) -> float:
    """Population Stability Index entre proporciones de bins; usar mismo esquema de bins."""
    assert len(expected) == len(observed) and len(expected) > 0
    eps = 1e-6
    return sum((o-e) * math.log((o+eps)/(e+eps)) for e,o in zip(expected,observed))


def time_label(window: int) -> str:
    return (START+timedelta(minutes=5*window)).isoformat()


def event(window, event_name, severity, incident_id, metric, value, action, outcome):
    return {'ts':time_label(window), 'trace_id':str(uuid.uuid5(uuid.NAMESPACE_DNS, f'act8-trace-{window}-{event_name}')),
            'span_id':f'span-{window:03d}', 'incident_id':incident_id, 'severity':severity,
            'event':event_name, 'metric':metric, 'value':round(value,4) if isinstance(value,float) else value,
            'action':action, 'outcome':outcome}


def run():
    rng = random.Random(RANDOM_SEED)
    base = [0.2,0.5,0.3]
    normal = [0.21,0.49,0.30]
    moved = [0.61,0.24,0.15]
    log=[]; rows=[]; cases=[]
    active={'latency':False,'data_drift':False,'error_rate':False}
    streak={'latency':0,'data_drift':0}
    last_alert={'latency':-100,'data_drift':-100,'error_rate':-100}
    for w in range(N_WINDOWS):
        latency_degraded=w in (4,5)
        drift_active=w in (11,12)
        recovered_latency=w>=6
        recovered_drift=w>=13
        latencies=[round(max(1,rng.gauss(680 if latency_degraded else 115,55 if latency_degraded else 25)),1) for _ in range(N_PER_WINDOW)]
        ordered=sorted(latencies); p95=ordered[math.ceil(.95*N_PER_WINDOW)-1]
        error_count=0 if w not in (4,5) else 3
        error_rate=error_count/N_PER_WINDOW
        distribution=moved if drift_active else normal
        drift_psi=psi(base,distribution)
        streak['latency']=streak['latency']+1 if p95>CONF['alerts']['latency']['p95_ms'] else 0
        streak['data_drift']=streak['data_drift']+1 if drift_psi>CONF['alerts']['data_drift']['psi_threshold'] else 0
        row={'window':w,'timestamp':time_label(w),'requests':N_PER_WINDOW,
             'p95_ms':p95,'error_count':error_count,'error_rate':error_rate,
             'availability':1-error_rate,'psi':round(drift_psi,4),
             'mode':'latency_degradation' if latency_degraded else 'drift' if drift_active else 'normal',
             'model_version':'v1-reference','routing_mode':'automatic'}
        if streak['latency']>=2 and not active['latency'] and w-last_alert['latency']>=3:
            active['latency']=True; last_alert['latency']=w
            inc='INC-001'
            log.append(event(w,'alert_fired','P1',inc,'p95_latency_ms',p95,'escalate_and_revert_simulated_config','triggered'))
            log.append(event(w,'runbook_step','P1',inc,'p95_latency_ms',p95,'freeze_changes_and_revert_simulated_config','executed_in_simulator'))
            cases.append({'id':inc,'type':'latency','detected_at':time_label(w),'detected_window':w,
                          'observed_p95_ms':p95,'action':'simulate_revert_of_latency_configuration',
                          'status':'open','severity':'P1'})
        if active['latency'] and not latency_degraded and p95<400:
            active['latency']=False
            cases[0].update({'resolved_at':time_label(w), 'resolved_window':w,'recovered_p95_ms':p95,'status':'resolved_simulated'})
            log.append(event(w,'incident_recovered','P1','INC-001','p95_latency_ms',p95,'validate_p95_and_close','recovered_in_simulator'))
        if streak['data_drift']>=2 and not active['data_drift'] and w-last_alert['data_drift']>=3:
            active['data_drift']=True;last_alert['data_drift']=w
            inc='INC-002'
            log.append(event(w,'alert_fired','P2',inc,'psi',drift_psi,'switch_to_manual_review_and_open_retrain_ticket','triggered'))
            log.append(event(w,'runbook_step','P2',inc,'psi',drift_psi,'pause_auto_decisions_in_simulation','executed_in_simulator'))
            cases.append({'id':inc,'type':'data_drift','detected_at':time_label(w),'detected_window':w,
                          'observed_psi':round(drift_psi,4),'action':'manual_review_and_retrain_ticket_only',
                          'status':'open','severity':'P2'})
        if active['data_drift'] and recovered_drift and drift_psi<0.2:
            active['data_drift']=False
            cases[-1].update({'resolved_at':time_label(w),'resolved_window':w,'recovered_psi':round(drift_psi,4),'status':'resolved_simulated'})
            log.append(event(w,'incident_recovered','P2','INC-002','psi',drift_psi,'validate_distribution_and_close','recovered_in_simulator'))
        row['routing_mode']='manual_review' if active['data_drift'] else 'automatic'
        rows.append(row)
    total=sum(r['requests'] for r in rows); failures=sum(r['error_count'] for r in rows)
    budget=round((1-CONF['slo']['availability'])*total)
    summary={'source':'simulacion_sintetica_software_no_produccion','seed':RANDOM_SEED,
             'total_requests_simulated':total,'total_errors_simulated':failures,
             'period_availability':round(1-failures/total,6), 'error_budget_allowed':budget,
             'error_budget_used':failures,'error_budget_remaining':budget-failures,
             'incidents':cases,'alerts_fired':len([e for e in log if e['event']=='alert_fired']),
             'sl_o_note':'SLO 99% evaluado por total de solicitudes simuladas; p95 400ms como SLI separado.',
             'monitoring_note':'PSI mide cambios distribucionales, no mide calidad real del modelo ni exactitud.'}
    with (EVIDENCE/'metrics_windows.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    with (EVIDENCE/'structured_events.jsonl').open('w',encoding='utf-8') as f:
        for entry in log:f.write(json.dumps(entry,ensure_ascii=False)+'\n')
    for filename,obj in [('incident_register.json',cases),('simulation_summary.json',summary)]:
        (EVIDENCE/filename).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return rows, cases, summary

if __name__=='__main__': run()
