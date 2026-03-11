# ROADMAP SPRINT 2 SEMANAS
**Asymetric Elon Bets - Desarrollo Producto Completo**

| Campo | Valor |
|---|---|
| Sprint Start | 12 Marzo 2026 |
| Sprint End | 26 Marzo 2026 |
| Objetivo | Producto web completo MVP listo para launch |
| Notas | Múltiples eventos despriorizados (v1.1) |

---

## 🎯 OBJETIVOS SPRINT

**Meta principal:** Convertir el prototipo funcional en un producto web completo con monetización, historial, SEO y UX profesional.

**Criterio de éxito:** 
- Usuario puede usar el producto completo sin fricción
- Tips en USDC funcionan end-to-end 
- Historial del modelo muestra accuracy >60%
- Product-market fit listo para distribución

---

## 📅 CRONOGRAMA DETALLADO

### SEMANA 1 (12-19 Marzo) - CORE INFRASTRUCTURE

#### **DÍA 1-2: Database & Jobs (Backend Priority)**
- **✅ Migrar de JSON a PostgreSQL**
  - Schema completo: events, bucket_snapshots, model_predictions, tips
  - Migraciones Alembic
  - Docker compose con PostgreSQL
- **✅ Jobs programados con APScheduler**
  - `fetch_active_events` (5 min)
  - `snapshot_bucket_prices` (10 min) 
  - `compute_default_prediction` (10 min)
  - `resolve_finished_events` (1 hora)

#### **DÍA 3-4: Web3 Monetización (Frontend Priority)**
- **✅ Integración RainbowKit + Wagmi**
  - Setup providers Polygon mainnet
  - TipModal con wallet connect
  - Transacción USDC (0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174)
- **✅ QR Code alternativa**
  - EIP-681 encoding para mobile wallets
  - Importes sugeridos: 1, 5, 10 USDC

#### **DÍA 5: Backend Tips Webhook**
- **✅ Webhook Alchemy para confirmaciones**
  - Endpoint `/api/tips/webhook`
  - Persistir tips en PostgreSQL
  - Stats endpoint `/api/tips/recent`

### SEMANA 2 (20-26 Marzo) - PRODUCT COMPLETION

#### **DÍA 6-7: Historial & Calibración (Data + Backend)**
- **✅ Recopilar datos históricos**
  - 20+ semanas tweets Elon desde xtracker
  - Poblar BD con resultados reales
- **✅ Vista History/Performance**
  - `/history` page con accuracy table
  - Coverage accuracy chart
  - Calibración μ, σ con datos reales

#### **DÍA 8-9: UX Polish (Frontend)**
- **✅ Framer Motion animations**
  - Hero fade-in, counter animado, transitions
- **✅ Mobile responsive**
  - Breakpoints: 360px, 768px, 1280px
  - Touch-friendly buckets interface
- **✅ Dark mode refinements**
  - Contrast accessibility WCAG AA
  - Loading states + skeletons

#### **DÍA 10-11: SEO & Distribution**
- **✅ SEO técnico**
  - Meta tags dinámicas
  - OG images con Next.js ImageResponse
  - sitemap.xml, robots.txt
- **✅ Analytics**
  - Plausible.io privacy-friendly
  - Conversión tracking tips

#### **DÍA 12-14: Polish & Launch Prep**
- **✅ Deep links Polymarket**
  - Botón por bucket → Polymarket direct
  - URL construction helper
- **✅ Error handling & monitoring**
  - Toast notifications
  - Uptime monitoring setup
- **✅ QA completo**
  - E2E testing manual
  - Cross-browser validation
  - Performance validation

---

## 🏗️ ARQUITECTURA TARGET

### Stack Técnico Final
```yaml
Frontend:
  - Next.js 15 + TypeScript 
  - RainbowKit + Wagmi + Viem (web3)
  - Framer Motion (animations)
  - Plausible Analytics

Backend:
  - FastAPI + SQLAlchemy async
  - PostgreSQL 16 (shared/dedicated)
  - APScheduler (jobs)
  - Alchemy webhooks

Infrastructure:
  - Hetzner VPS (existing)
  - Docker compose
  - Nginx reverse proxy
  - Let's Encrypt SSL
```

---

## 📋 ENTREGABLES POR ROL

### **Backend Developer**

#### Sprint Backlog
| Task | Priority | Effort | Done When |
|------|----------|--------|-----------|
| PostgreSQL migration + schema | P0 | 1d | `docker-compose up` works |
| APScheduler jobs setup | P0 | 1d | BD auto-populates every 10min |
| Tips webhook /api/tips/webhook | P0 | 0.5d | Alchemy test webhook confirmed |
| History endpoints | P1 | 1d | `/api/history/*` returns real data |
| Data collection script | P1 | 1d | 20+ weeks in PostgreSQL |

#### Definition of Done
- PostgreSQL schema matches PLAN.md specification
- Jobs running stable for 48h without errors
- Tips webhook tested with real USDC transaction
- History API returns accuracy >60% with real data

### **Frontend Developer**

#### Sprint Backlog  
| Task | Priority | Effort | Done When |
|------|----------|--------|-----------|
| RainbowKit integration | P0 | 1.5d | USDC transfer works on mainnet |
| TipModal complete UX | P0 | 1d | Both wallet+QR flows functional |
| History page /history | P1 | 1d | Shows accuracy table + chart |
| Framer Motion animations | P1 | 1d | Hero, counters, transitions smooth |
| Mobile responsive | P1 | 1d | Works on iPhone/Android |
| SEO + OG images | P1 | 1d | Dynamic images with weekly range |

#### Definition of Done
- Web3 tips: 1-click experience, <30s confirmation
- Mobile: fully functional on 360px+ screens  
- Animations: 60fps, no jank
- SEO: Lighthouse score >80, proper meta tags

### **PM/QA**

#### Sprint Backlog
| Task | Priority | Effort | Done When |
|------|----------|--------|-----------|
| User testing flow | P0 | 0.5d | 3 users complete tip flow <60s |
| Cross-browser QA | P0 | 0.5d | Chrome, Firefox, Safari working |
| Performance validation | P1 | 0.5d | Lighthouse >80, real device testing |
| Launch checklist prep | P1 | 0.5d | Distribution plan documented |

---

## 🎨 UX REQUIREMENTS CRÍTICOS

### Visual Polish Must-Haves
- **Hero animation**: Recommendation fades in smoothly
- **Counter animations**: Payout/EV numbers count up visually
- **Mobile first**: Touch targets >44px, readable typography
- **Loading states**: Skeletons while API loads, no flash
- **Error states**: Friendly messages, retry options

### Accessibility (WCAG AA)
- Contrast ratio >4.5:1 en dark theme
- Keyboard navigation completo
- Screen reader labels
- Focus management en modals

---

## 💰 MONETIZACIÓN IMPLEMENTATION

### Wallet Integration Spec
```typescript
// Target UX flow
Button "Leave Tip" → 
  Modal opens → 
  [1 USDC] [5 USDC] [10 USDC] [Custom] →
  Connect Wallet OR Scan QR →
  Transaction → 
  Success animation →
  Share on X option

// Technical requirements  
- USDC Polygon: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
- Gas estimation + approval for USDC spend
- Transaction status tracking
- Mobile QR fallback for wallet-less users
```

### Social Proof
- Footer widget: "🌟 47 traders sent tips · Total: 234 USDC"
- Recent tips feed (anonymous): "2h ago: 5 USDC"

---

## 🔍 TESTING & VALIDATION

### Pre-Launch Checklist
- [ ] **E2E happy path**: Land → see recommendation → tip works
- [ ] **Edge cases**: No internet, API down, wallet reject, mobile
- [ ] **Performance**: <3s LCP, <0.1 CLS, <100ms FID
- [ ] **Data accuracy**: Stakes math verified, model predictions match
- [ ] **SEO**: Meta tags, OG preview, sitemap crawlable

### User Acceptance Criteria
1. **New user** sees optimal range in <3 seconds
2. **Manual adjustment** updates stakes and EV instantly  
3. **Tip flow** completes in <60 seconds with no friction
4. **History view** shows model accuracy with real data
5. **Mobile experience** fully functional on iPhone/Android

---

## 🚧 RISKS & MITIGATION

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Web3 integration complexity | High | Start day 3, budget 2 full days |
| Historical data quality | Medium | Use multiple sources, manual validation |
| Mobile UX issues | Medium | Test on real devices daily |
| Performance degradation | Medium | Lighthouse CI, lazy loading |
| Alchemy webhook reliability | Low | Fallback to manual tip detection |

---

## 🚀 POST-SPRINT (Week 3)

### Launch Activities
- Beta testing with 5 Polymarket users
- Distribution in Polymarket Discord
- X/Twitter thread with demo
- Product Hunt submission consideration

### Success Metrics (Week 1 post-launch)
- **Users**: >100 unique visitors
- **Tips**: >5 USDC total received  
- **Engagement**: >2min average session
- **Technical**: >99% uptime, <3s load time

---

## 📁 REPOSITORY STRUCTURE POST-SPRINT

```
elon-asymetric-tweet-bets/
├── frontend/                 # Next.js app
├── backend/                  # FastAPI app  
├── shared/                   # Tipos TypeScript compartidos
├── docs/                     # Documentation
│   ├── API.md               # Backend endpoints
│   ├── DEPLOYMENT.md        # Infra setup
│   └── USER-GUIDE.md        # Product usage
├── docker-compose.yml       # Full stack
├── ROADMAP-SPRINT-2WEEKS.md # Este documento
└── PLAN.md                  # Spec original
```

---

**Aprobación PM**: Este roadmap cubre TODO lo crítico para un producto viable. Enfoque láser en 2 semanas, sin scope creep.

**Next Step**: Asignar ownership específico y comenzar Día 1 con PostgreSQL migration.

---
*Última actualización: 11 Marzo 2026 - Mick AI*