# OBJECTIVE-WEBAPP (single source of truth)

## Objetivo final (v1 MVP)
Entregar una web app de predicción para eventos de Polymarket (enfocada en Elon) que permita:
1. Ver recomendación y rango óptimo de stake con UX clara en una **pantalla móvil única**.
2. Conectar wallet y ejecutar **un único CTA principal** sin fricción (idealmente tip en USDC; si no llega, fallback honesto de demo técnica).
3. Mostrar contexto mínimo suficiente para confiar en la recomendación (precio actual, freshness, rationale corto).
4. Operar con backend estable (jobs + persistencia + endpoints) y observabilidad mínima.

Referencia táctica de producto: `docs/MVP-MOBILE-1SCREEN.md`.

## Qué significa "DONE"
- Flujo E2E completo en móvil:
  - abrir app -> ver recomendación -> conectar wallet -> CTA principal -> confirmación/estado final.
- La home es una sola pantalla mobile-first y no depende de tablas/componentes desktop para explicar el producto.
- Backend responde con datos reales de eventos/buckets/precios (no mocks críticos) para al menos un evento visible.
- Métricas mínimas: `/health` OK, errores controlados, sin blockers P0 abiertos.
- QA validado con checklist y evidencias.

## Fuera de alcance inmediato (si no bloquea el MVP)
- Extras visuales/SEO avanzados.
- Optimizaciones no críticas de performance.
- Features v1.1 no necesarias para el flujo principal.

## Prioridades operativas actuales
P0:
- Cerrar la home como **pantalla MVP móvil de 1 pantalla**.
- Poblarla con datos reales de `/events` + `/events/{id}/predictions`.
- Cerrar un único CTA principal de wallet/tip o dejar fallback honesto de demo tx.
- QA móvil E2E con edge cases (reject/offline/API down).

P1:
- Cleanup arquitectura/documentación.
- Historial/accuracy ampliado y mejoras UX no bloqueantes.
