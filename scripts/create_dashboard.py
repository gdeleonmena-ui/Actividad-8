"""Genera dashboard y figuras reproducibles a partir de CSV SIMULADO."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence'
rows=list(csv.DictReader((EV/'metrics_windows.csv').open(encoding='utf-8')))
xs=[int(x['window']) for x in rows]
p95=[float(x['p95_ms']) for x in rows]
errors=[float(x['error_rate'])*100 for x in rows]
psi=[float(x['psi']) for x in rows]
summary=json.loads((EV/'simulation_summary.json').read_text(encoding='utf-8'))

fig,axes=plt.subplots(2,1,figsize=(10,6.3),sharex=True)
axes[0].plot(xs,p95,marker='o',label='p95 simulado')
axes[0].axhline(400,linestyle='--',label='SLO p95 400 ms')
axes[0].set_ylabel('Latencia p95 (ms)');axes[0].legend();axes[0].grid(alpha=.2)
axes[1].bar(xs,errors,label='Errores simulados (%)')
axes[1].axhline(1,linestyle='--',label='Objetivo 1% errores')
axes[1].set_ylabel('Errores (%)');axes[1].set_xlabel('Ventana de 5 min');axes[1].legend();axes[1].grid(alpha=.2)
fig.suptitle('Actividad 8 | Dashboard operacional (datos simulados)')
fig.tight_layout();fig.savefig(EV/'dashboard_operativo.png',dpi=155,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(9,3.8))
ax.plot(xs,psi,marker='o',label='PSI simulado')
ax.axhline(.2,linestyle='--',label='Alerta PSI > 0.20')
ax.set(xlabel='Ventana de 5 min',ylabel='PSI',title='Cambio distribucional (PSI por ventana)')
ax.legend();ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(EV/'dashboard_drift.png',dpi=155,bbox_inches='tight');plt.close(fig)

html=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Actividad 8 - Dashboard simulado</title>
<style>body{{font-family:Arial,sans-serif;max-width:1050px;margin:32px auto;color:#18212a}}h1{{color:#176e79}}.cards{{display:flex;gap:15px;flex-wrap:wrap}}.card{{background:#f3f7f8;padding:16px 24px;border-radius:9px}}.card b{{font-size:24px;display:block}}img{{max-width:100%}}small{{color:#555}}</style></head><body>
<h1>Actividad 8 | Observabilidad del modelo de abandono</h1><p><b>Simulación académica reproducible.</b> No son mediciones de una API en producción.</p>
<div class="cards"><div class="card">Solicitudes simuladas<b>{summary['total_requests_simulated']}</b></div><div class="card">Disponibilidad del período<b>{summary['period_availability']*100:.2f}%</b></div><div class="card">Presupuesto de error restante<b>{summary['error_budget_remaining']}/{summary['error_budget_allowed']}</b></div><div class="card">Incidentes simulados<b>{len(summary['incidents'])}</b></div></div>
<h2>Indicadores y alertas</h2><img src="dashboard_operativo.png" alt="Latencia p95 y errores"><img src="dashboard_drift.png" alt="PSI de distribución">
<h2>Incident response</h2><p>INC-001 P1: latencia alta, reversión simulada de configuración. INC-002 P2: PSI, revisión humana y ticket de reentrenamiento simulado.</p>
<small>Fuente: scripts/simulate_monitoring.py, semilla 42. No es un panel en vivo ni prueba de producción.</small></body></html>'''
(EV/'dashboard.html').write_text(html,encoding='utf-8')
print('Dashboard de simulacion generado')
