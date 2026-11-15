import sys, json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'scripts'))
from simulate_monitoring import run, psi

def test_psi_same_distribution_zero():
    assert abs(psi([.2,.5,.3],[.2,.5,.3]))<1e-10

def test_incidents_and_recovery():
    rows,cases,summary=run()
    assert len(rows)==18 and len(cases)==2
    assert [x['id'] for x in cases]==['INC-001','INC-002']
    assert all(x['status']=='resolved_simulated' for x in cases)
    assert cases[0]['recovered_p95_ms']<400
    assert cases[1]['recovered_psi']<0.2
    assert summary['alerts_fired']==2
    assert summary['error_budget_remaining']==12

def test_no_pii_in_event_log():
    run()
    events=(HERE/'evidence'/'structured_events.jsonl').read_text()
    assert all(x not in events.lower() for x in ['email','telefono','nombre_cliente','password'])

def test_manual_review_after_drift_alert():
    rows,_,_=run()
    assert rows[12]['routing_mode']=='manual_review'
    assert rows[13]['routing_mode']=='automatic'
