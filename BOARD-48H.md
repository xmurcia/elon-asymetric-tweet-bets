# BOARD 48H — Stabilización Wallet + Backend/Frontend

## Objetivo
Ver `OBJECTIVE-WEBAPP.md` como fuente de verdad. En este ciclo: dejar una **demo móvil creíble de 1 pantalla** con recomendación visible, stake sugerido y **un único CTA principal** de wallet, sin errores críticos y con backend/frontend alineados.

Referencia táctica: `docs/MVP-MOBILE-1SCREEN.md`.

## Prioridades
- P0: Reemplazar la home shell por la **pantalla móvil única** definida en `docs/MVP-MOBILE-1SCREEN.md`.
- P0: Cerrar **un solo CTA principal** de wallet (USDC real si llega; fallback honesto a demo tx si no).
- P0: QA móvil E2E del flujo principal + edge cases de rechazo/red/pending.
- P1: Hygiene de repos/arquitectura (backend oficial FastAPI, legado Node marcado claramente).

## Backlog

### FE-01 (P0) — Estabilizar arranque y configuración web3
**Owner:** Frontend
**Estimación:** M (4–6h)
**Tareas:**
- Arreglar build (`App.css` ausente o import innecesario).
- Añadir dependencia `chart.js` si se usa `GaussChart`.
- Mover WalletConnect projectId a `REACT_APP_WALLETCONNECT_PROJECT_ID`.
- Ajustar config RainbowKit para SPA (sin SSR en CRA).
- Configurar conexión frontend-backend (`proxy` dev o `axios.baseURL` por env).
**DoD:**
- `npm start` sin errores.
- Flujo connect wallet funcional.
- Config documentada en `.env.example`.

### FE-02 (P0) — Pantalla MVP móvil de 1 pantalla
**Owner:** Frontend
**Estimación:** M (4–6h)
**Tareas:**
- Sustituir la home actual por layout mobile-first de una sola columna.
- Mostrar evento por defecto + recomendación + precio actual + stake sugerido.
- Añadir rationale corto, freshness y CTA sticky inferior.
- Evitar tablas anchas/componentes desktop en la home.
**DoD:**
- En viewport móvil se entiende la propuesta y el CTA en <5s.
- La pantalla consume datos reales del backend para al menos un evento.
- El CTA principal está visible sin depender de navegación secundaria.

### FE-03 (P0) — Manejo robusto de errores de wallet en CTA principal
**Owner:** Frontend
**Estimación:** M (3–5h)
**Tareas:**
- Manejar: reject usuario, fondos insuficientes, chain mismatch, tx dropped/pending.
- UI: toasts claros + estado inline en la pantalla principal, sin spinner infinito.
- Si USDC no llega hoy, etiquetar claramente el fallback demo tx.
**DoD:**
- Todos los edge cases muestran feedback accionable y estado consistente.
- No hay ambigüedad sobre si el CTA es real o demo.

### BE-01 (P0) — API mínima y observabilidad básica
**Owner:** Backend
**Estimación:** M (5–7h)
**Tareas:**
- Endpoints: `/health`, `/events`, `/events/{id}/snapshots`, `/events/{id}/predictions`.
- Logging razonable (evitar ruido excesivo SQL en modo normal).
**DoD:**
- Endpoints responden correctamente en local.
- Smoke test simple documentado.

### BE-02 (P0) — Identidad de eventos correcta
**Owner:** Backend
**Estimación:** M (4–6h)
**Tareas:**
- Modelo `Event`: introducir `external_id` + `source` y unicidad compuesta.
- Usar `external_id` en llamadas de precios/market.
- Ajustar persistencia/scheduler acorde.
**DoD:**
- Snapshots/predicciones ligados a identificador externo correcto.

### QA-01 (P0) — Checklist móvil E2E + bug report priorizado
**Owner:** Analyst (QA)
**Estimación:** S–M (3–4h)
**Tareas:**
- Ejecutar casos: connect/approve/send/reject/back/offline/API down.
- Reportar bugs con severidad y pasos reproducibles.
**DoD:**
- Reporte con P0/P1/P2 y evidencias.

### OPS-01 (P1) — Hygiene de repos y handoff
**Owner:** PM
**Estimación:** S (1–2h)
**Tareas:**
- Declarar backend oficial (FastAPI) y marcar Node como legacy/deprecated.
- Actualizar documentación de arranque real.
- Preparar resumen de release interno.
**DoD:**
- Cualquier dev nuevo identifica stack y flujo en <5 min.

## Estado inicial
- To Do: QA-01, OPS-01
- In Progress: FE-02
- Done: FE-01 (parcialmente cerrado), BE-01, BE-02

## Re-enfoque inmediato
- La prioridad ya no es "mejorar dashboard" sino **cerrar una home móvil que venda una sola decisión**.
- `TradesTable`, paper trading y visualizaciones complejas salen del critical path.
- Si el flujo USDC real no queda hoy, se demoa con fallback explícito y no se maquilla como feature terminada.

## Estado real verificado
- FE-01: muy avanzado/casi cerrado. Ya existe `App.css`, `chart.js` está en `package.json`, RainbowKit usa `REACT_APP_WALLETCONNECT_PROJECT_ID`, `ssr: false` está configurado para CRA y existe `src/api/client.js` con `REACT_APP_API_BASE_URL` + `proxy` en `package.json`.
- FE-02: parcial. Ya existe normalización básica de errores wallet (`src/utils/walletErrors.js`) y UI con toasts/estado en `SendNativeTokenButton`, incluyendo reject, insufficient funds, chain mismatch y pending largo. Falta validar/afinar casos reales E2E en móvil y conectar este manejo al flujo final de tip en USDC si ese va a ser el CTA principal.
- BE-01: implementado en FastAPI (`/health`, `/events`, `/events/{id}/snapshots`, `/events/{id}/predictions`, `/coverage`).
- BE-02: implementado a nivel de modelo/endpoints con `external_id` + `source`; conviene revisar migración de datos si ya existía esquema previo en entornos persistentes.

## Gaps bloqueantes para demo interna móvil
- La home actual (`src/App.js`) no enseña todavía recomendación, stake, histórico ni lista de eventos: solo `ConnectButton` + `Send 0 (demo tx)`.
- No veo flujo USDC/tip end-to-end en frontend; el webhook/backend de tips existe, pero la UI no lo consume todavía.
- `TradesTable` sigue apuntando a `/api/trades/paper`, pero ese contrato no está reflejado en el backend FastAPI actual ni en la pantalla principal.
- QA móvil real sigue pendiente; el smoke actual solo valida render básico del shell.
- Persiste ambigüedad arquitectónica por coexistencia de `backend/` legado Node y `fastapi_backend/` como backend actual.
