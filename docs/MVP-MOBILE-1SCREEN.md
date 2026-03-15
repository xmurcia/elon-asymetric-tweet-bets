# MVP móvil táctico — 1 pantalla

## Objetivo de esta iteración
Cerrar una **demo móvil creíble en una sola pantalla**: abrir app, entender la oportunidad, conectar wallet y ejecutar **un CTA principal claro** sin navegar por tabs ni depender de features secundarias.

## Pantalla MVP (buildable hoy)
1. **Top bar compacta**: nombre corto del producto + estado backend (`Live` / `Sync delayed`) + botón `Connect wallet`.
2. **Hero de oportunidad**: pregunta del evento seleccionada por defecto en 2-3 líneas máximo.
3. **Recomendación principal**: badge único `BUY YES`, `BUY NO` o `NO BET` con color/jerarquía fuerte.
4. **Precio actual + edge**: mostrar precio de mercado actual, precio/valor estimado del modelo y delta (%) en una misma fila.
5. **Stake sugerido**: cantidad recomendada en USDC y rango simple (`light / base / max`) para que no sea solo opinión.
6. **Confidence + freshness**: nivel (`low/med/high`) + timestamp `Updated Xm ago` para dar contexto de fiabilidad.
7. **Mini visual**: sparkline o banda simple de últimos snapshots; si no llega, fallback textual (`24h range`). No meter chart complejo si retrasa.
8. **Rationale ultra corto**: 2-3 bullets de por qué existe la oportunidad, sin ensayo ni bloque largo.
9. **CTA sticky principal**: botón fijo abajo con estado dinámico (`Connect wallet`, `Switch to Polygon`, `Send tip`, `Try demo tx`).
10. **Feedback transaccional inline**: estados visibles `awaiting wallet`, `pending`, `confirmed`, `failed` + link/hash corto cuando exista.

## CTA principal recomendado
**Recomendado ahora:** `Send tip with USDC` en Polygon, **solo si** el frontend puede firmar una transferencia ERC-20 USDC real y el backend puede reflejar confirmación o al menos el hash de forma coherente.

**Fallback honesto si eso no se puede cerrar hoy:** usar `Try demo tx` (la tx nativa 0 actual) como CTA de demo técnica, pero etiquetarlo explícitamente como **wallet demo / not USDC yet**. Mejor eso que fingir un flujo de tip cerrado.

## Scope recortado — NO entra en esta iteración
- Multi-event browsing, buscador, filtros, tabs o carruseles.
- Trades table, paper trading y formularios manuales de compra/venta.
- Heatmap, gauss chart complejo, simuladores interactivos o sliders.
- Historial/accuracy exhaustivo; como mucho un dato resumido o badge simple.
- Desktop-first polish, SEO, auth, perfil, settings o onboarding largo.
- Integraciones extra de mercado más allá de las ya necesarias para poblar **un evento principal**.
- Cualquier flujo que obligue a navegar a una segunda pantalla para completar la demo.

## Criterios de done para una demo móvil creíble
- En viewport móvil (390x844 aprox.) toda la propuesta de valor cabe en una sola pantalla con scroll corto y CTA sticky siempre visible.
- La pantalla carga un evento real por defecto desde backend y muestra: pregunta, recomendación, precio actual y stake sugerido.
- El usuario entiende en menos de 5 segundos qué hacer y por qué.
- `Connect wallet` funciona en móvil y los estados de red/error están controlados (reject, wrong network, pending largo, fail).
- Existe **un CTA principal real** y demostrable end-to-end; si es fallback demo tx, queda explícito en UI para no engañar.
- No hay spinners infinitos ni bloques vacíos; toda ausencia de datos tiene fallback legible.
- La UI no depende de tablas anchas ni componentes desktop que rompan el layout.
- Demo script de 30-45 segundos sale limpia: abrir app -> ver edge -> conectar wallet -> pulsar CTA -> ver estado final.

## Orden de ejecución sugerido hoy
1. Sustituir home shell por layout mobile-first de una sola columna.
2. Consumir `/events` + `/events/{id}/predictions` para poblar el hero y la recomendación.
3. Resolver CTA principal real (USDC si llega; si no, fallback honesto con demo tx).
4. Añadir estados transaccionales y de error inline.
5. Rematar con smoke móvil/manual en iPhone-sized viewport.
