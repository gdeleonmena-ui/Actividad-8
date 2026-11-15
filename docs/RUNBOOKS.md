# Runbooks para monitoreo del modelo de abandono (actividad académica)

## RB-01 — P1: latencia p95 sostenida

**Disparador:** p95 > 400 ms durante 2 ventanas consecutivas de 5 minutos, con tráfico suficiente. La alerta se agrupa por servicio e incidente y aplica cooldown de tres ventanas.

1. Confirmar p95, error rate, volumen y traces por endpoint. Declarar incidente P1 si afecta inferencia en la ruta crítica.
2. Verificar si existe cambio reciente de configuración, versión, dependencias o consumo de memoria. No consultar payloads de clientes.
3. Congelar despliegues y ejecutar rollback de configuración **solo bajo política aprobada y reversión comprobada**.
4. Probar `/health` y `/predict` con datos sintéticos; comprobar p95 inferior a 400 ms dos ventanas y ausencia de nuevos errores.
5. Documentar responsable, hora, `trace_id`, evidencia y causa raíz; iniciar postmortem si aplica.

**Alcance de la actividad:** rollback representado con cambio de estado **dentro de una simulación**, no sobre infraestructura real.

## RB-02 — P2: cambio de distribución de datos

**Disparador:** PSI > 0.20 en la misma variable y con bins fijos frente a referencia durante 2 ventanas consecutivas. Requiere mínimo de 100 registros por ventana en el ejercicio.

1. Confirmar la integridad de los datos, la referencia de bins y el volumen de eventos.
2. Revisar cambios de ETL y segmentar por canal sin revelar información personal.
3. Desviar predicciones de baja confianza hacia **revisión humana**; no tomar acciones comerciales automatizadas.
4. Abrir ticket de reentrenamiento / calibración con validación temporal y por segmentos. **Nunca reentrenar o desplegar automáticamente ante PSI**.
5. Validar retorno bajo umbral y confirmar que la calidad del modelo con etiquetas posteriores se mantiene; entonces cerrar incidente con evidencia.

**Alcance de la actividad:** los datos vuelven a la referencia de forma simulada. No se afirma mejora real en precisión o recall.

## Priorización y ruido operativo

- P1: indisponibilidad, exceso de latencia de inferencia, consumo acelerado del presupuesto de error.
- P2: deriva sostenida, degrade gradual, revisión de calidad de datos.
- Deduplicación por clave `incident_id`, 2 ventanas consecutivas y cooldown de tres ventanas; inhibición por mantenimiento declarado.
- Presupuesto por período: 1% de solicitudes elegibles para SLO 99%; el burn rate es error_rate/(1-0.99), interpretado sobre ventanas con tráfico.
- Los eventos simulados no prueban que los límites propuestos sean apropiados para producción; deben calibrarse.
