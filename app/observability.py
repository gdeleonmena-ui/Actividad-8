"""Instrumentacion liviana de la API para demostracion local.
No es un almacen duradero ni reemplaza un backend de telemetria en produccion.
"""
from __future__ import annotations
import json, logging, math, threading, time, uuid
from collections import defaultdict
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse

LOGGER=logging.getLogger('churn_telemetry')
LOGGER.setLevel(logging.INFO)
if not LOGGER.handlers:
    handler=logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    LOGGER.addHandler(handler)
_LOCK=threading.Lock()
_COUNT=defaultdict(int)
_LATENCY=defaultdict(list)

def attach_telemetry(app):
    @app.middleware('http')
    async def monitor_requests(request: Request, call_next):
        if request.url.path == '/metrics':
            return await call_next(request)
        t0=time.perf_counter()
        trace_id=request.headers.get('x-trace-id')
        if not trace_id or len(trace_id)>128:
            trace_id=str(uuid.uuid4())
        span_id=uuid.uuid4().hex[:16]
        status=500
        try:
            response=await call_next(request)
            status=response.status_code
            response.headers['x-trace-id']=trace_id
            return response
        finally:
            elapsed=(time.perf_counter()-t0)*1000
            route=request.scope.get('route')
            path=getattr(route,'path',None) or '/unmatched'
            with _LOCK:
                _COUNT[(path,status)]+=1
                _LATENCY[path].append(elapsed)
                if len(_LATENCY[path])>1000:
                    _LATENCY[path]=_LATENCY[path][-1000:]
            # Nunca serializar query, payload ni headers sensibles.
            LOGGER.info(json.dumps({'ts':datetime.now(timezone.utc).isoformat(),
              'trace_id':trace_id,'span_id':span_id,'event':'http_request',
              'path':path,'method':request.method,'status':status,
              'latency_ms':round(elapsed,2)}))

    @app.get('/metrics')
    def metrics():
        with _LOCK:
            counts=[{'route':r,'status':s,'requests':n} for (r,s),n in sorted(_COUNT.items())]
            routes={}
            for route,values in _LATENCY.items():
                v=sorted(values)
                routes[route]={'observations':len(v), 'p95_latency_ms':round(v[math.ceil(.95*len(v))-1],2)}
        return {'scope':'single_process_ephemeral','counts':counts,'latency':routes,
                'note':'Datos del proceso actual: usar exportador centralizado en produccion.'}
