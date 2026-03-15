# MVP frontend contract mínimo

Objetivo: desbloquear una primera pantalla móvil útil sin abrir otro frente grande.

## Endpoints suficientes para un MVP inicial
Sí, **`/events` + `/events/{id}/snapshots` + `/events/{id}/predictions` bastan** para una primera pantalla útil si el frontend se limita a:
- listar eventos,
- mostrar las dos opciones del mercado,
- enseñar precio/probabilidad actual por outcome,
- abrir detalle simple con histórico reciente.

## Contrato recomendado

### 1) `GET /events`
Usarlo para la lista principal.

Campos clave a consumir por tarjeta:
- `id`: id interno para navegar a detalle
- `question`: texto principal
- `slug`: opcional para URL/share
- `active`, `closed`: estado
- `end_date`: deadline
- `latest_snapshot_at`: frescura de mercado
- `outcomes[]`:
  - `id`
  - `outcome_index`
  - `name`
  - `latest_price`
  - `latest_price_timestamp`

Con esto frontend **ya no necesita llamar a `/predictions` para pintar la lista**.

### 2) `GET /events/{id}/predictions`
Usarlo para detalle ligero / bloque de "current odds" si se quiere mantener separado.

Devuelve:
- `event`: `id`, `external_id`, `source`, `question`
- `predictions[]`:
  - `outcome_id`
  - `outcome_index`
  - `outcome_name`
  - `price`
  - `timestamp`

### 3) `GET /events/{id}/snapshots`
Usarlo para mini chart / histórico reciente.

Devuelve:
- `event`: `id`, `external_id`, `source`, `question`
- `snapshots[]`:
  - `outcome_id`
  - `outcome_index`
  - `outcome_name`
  - `price`
  - `timestamp`

Nota: ahora devuelve una lista plana intercalada por timestamps/outcomes. Eso sirve para MVP, pero frontend tendrá que agrupar por `outcome_id` o `outcome_name` para dibujar series.

## Ajuste mínimo aplicado backend
Se añadió a `GET /events`:
- `latest_snapshot_at` a nivel evento
- `latest_price`
- `latest_price_timestamp`

Esto reduce llamadas y simplifica mucho la home móvil.

## Qué está listo ya
- Backend FastAPI con los 3 endpoints mínimos.
- Identidad útil de evento: `id`, `external_id`, `source`.
- Lista de outcomes por evento.
- Histórico reciente por outcome vía snapshots.
- Precio actual por outcome vía predictions.
- Mejora mínima para que la lista principal consuma solo `/events`.

## Qué no está listo / límites actuales
- No hay payload optimizado para chart (series agrupadas por outcome); frontend debe transformar `snapshots[]`.
- No hay campo explícito de "featured event" o ranking/prioridad para home.
- No hay recomendación, stake sugerido ni señal de producto; solo market data.
- No hay flujo real frontend consumiendo estos endpoints en `src/App.js` todavía.
- No hay confirmación E2E móvil real sobre esta nueva pantalla.

## Sugerencia práctica para frontend
Secuencia mínima:
1. `GET /events`
2. Render de cards con `question`, `outcomes[].name`, `outcomes[].latest_price`, `end_date`
3. Al abrir detalle: `GET /events/{id}/snapshots`
4. Opcionalmente `GET /events/{id}/predictions` si quieren separar current odds del histórico

Si quieren recortar aún más, **home = `/events` y detalle = `/events/{id}/snapshots`** ya da para una primera demo funcional.
