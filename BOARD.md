# DEVELOPMENT BOARD - Sprint 2 Semanas
**Estado:** 🚀 **INICIADO** - 12 Marzo 2026 08:00  
**Objetivo:** Producto web completo MVP  

---

## 📋 KANBAN BOARD

### 🆕 TODO (Listas para asignar)

#### **BACKEND-DB-001** 📊 PostgreSQL Schema Migration
**Owner:** `DatabaseAgent`  
**Priority:** P0  
**Effort:** 1d  
**Dependencies:** None  

**Tasks:**
- [ ] Crear schema PostgreSQL completo (events, bucket_snapshots, model_predictions, tips)
- [ ] Setup Alembic migrations en `backend/migrations/`
- [ ] Actualizar docker-compose.yml con PostgreSQL service
- [ ] Migrar datos existentes JSON → PostgreSQL
- [ ] Tests de conexión y CRUD básico

**DoD:** `docker-compose up` works, tables created, sample data inserted

---

#### **BACKEND-JOBS-002** ⏰ APScheduler Jobs Setup  
**Owner:** `SchedulerAgent`  
**Priority:** P0  
**Effort:** 1d  
**Dependencies:** BACKEND-DB-001  

**Tasks:**
- [ ] Setup APScheduler en FastAPI app
- [ ] Job: `fetch_active_events` cada 5 min
- [ ] Job: `snapshot_bucket_prices` cada 10 min  
- [ ] Job: `compute_default_prediction` cada 10 min
- [ ] Job: `resolve_finished_events` cada 1 hora
- [ ] Logging y error handling para jobs

**DoD:** Jobs running stable for 2h, BD auto-populates, logs clean

---

#### **BACKEND-API-003** 🌐 History API Endpoints
**Owner:** `APIAgent`  
**Priority:** P1  
**Effort:** 0.5d  
**Dependencies:** BACKEND-DB-001  

**Tasks:**
- [ ] GET `/api/history/events` - eventos pasados con resultado
- [ ] GET `/api/history/accuracy` - métricas globales modelo
- [ ] GET `/api/history/events/{id}` - detalle evento histórico
- [ ] Actualizar endpoints existentes para usar PostgreSQL
- [ ] Tests unitarios de endpoints

**DoD:** Postman collection pasa, retorna datos reales de BD

---

#### **FRONTEND-WEB3-004** 💰 RainbowKit Integration
**Owner:** `Web3Agent`  
**Priority:** P0  
**Effort:** 1.5d  
**Dependencies:** None  

**Tasks:**
- [ ] Setup RainbowKit + Wagmi + Viem providers
- [ ] Configurar Polygon mainnet
- [ ] TipModal component completo
- [ ] USDC transfer logic (0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174)
- [ ] QR code fallback con EIP-681
- [ ] Gas estimation y approval flows

**DoD:** USDC tip works on Polygon mainnet, both wallet+QR flows

---

#### **FRONTEND-HISTORY-005** 📈 History Page & Components
**Owner:** `UIAgent`  
**Priority:** P1  
**Effort:** 1d  
**Dependencies:** BACKEND-API-003  

**Tasks:**
- [ ] `/history` page con Next.js routing
- [ ] AccuracyTable component - semanas + if acertó
- [ ] AccuracyChart component - coverage over time
- [ ] PerformanceStats component - métricas globales
- [ ] Integrar con History API endpoints

**DoD:** History page functional, shows real accuracy data

---

#### **BACKEND-WEBHOOK-006** 🔗 Tips Webhook System
**Owner:** `WebhookAgent`  
**Priority:** P0  
**Effort:** 0.5d  
**Dependencies:** BACKEND-DB-001  

**Tasks:**
- [ ] Endpoint POST `/api/tips/webhook` para Alchemy
- [ ] Verificar signature webhook Alchemy
- [ ] Persistir tips confirmados en BD
- [ ] GET `/api/tips/recent` y `/api/tips/stats`
- [ ] Setup webhook URL en Alchemy dashboard

**DoD:** Real USDC tip confirmed via webhook, appears in BD

---

#### **DATA-HISTORICAL-007** 🔍 Historical Data Collection  
**Owner:** `DataAgent`  
**Priority:** P1  
**Effort:** 1d  
**Dependencies:** BACKEND-DB-001  

**Tasks:**
- [ ] Script para scrape/download 20+ semanas datos Elon tweets
- [ ] Fuentes: xtracker.polymarket.com, resolved markets
- [ ] Poblar BD con resultados reales
- [ ] Calcular μ, σ históricos reales
- [ ] Validar datos para accuracy >60%

**DoD:** BD tiene ≥20 semanas reales, model accuracy calculada

---

#### **FRONTEND-UX-008** 🎨 UX Polish & Animations
**Owner:** `UXAgent`  
**Priority:** P1  
**Effort:** 1d  
**Dependencies:** FRONTEND-WEB3-004  

**Tasks:**
- [ ] Framer Motion setup - hero animations
- [ ] Counter animations para payout/EV  
- [ ] Mobile responsive breakpoints (360px, 768px, 1280px)
- [ ] Loading states + skeleton screens
- [ ] Dark theme accessibility improvements

**DoD:** Smooth 60fps animations, mobile friendly, WCAG AA

---

#### **DEVOPS-SEO-009** 🔍 SEO & Meta Tags
**Owner:** `SEOAgent`  
**Priority:** P1  
**Effort:** 0.5d  
**Dependencies:** None  

**Tasks:**
- [ ] Dynamic meta tags Next.js
- [ ] OG images con ImageResponse API
- [ ] sitemap.xml generation  
- [ ] robots.txt
- [ ] Schema.org markup financiero

**DoD:** Lighthouse SEO >90, OG preview works, crawlable

---

#### **DEVOPS-DEPLOY-010** 🚀 Production Deployment
**Owner:** `DevOpsAgent`  
**Priority:** P1  
**Effort:** 0.5d  
**Dependencies:** Multiple  

**Tasks:**
- [ ] Docker compose production ready
- [ ] Nginx config con SSL
- [ ] Environment variables setup
- [ ] Backup strategy PostgreSQL
- [ ] Uptime monitoring

**DoD:** Deployed to Hetzner VPS, SSL working, monitored

---

### 🔄 IN PROGRESS

*Tareas serán movidas aquí cuando los agentes las tomen*

---

### 👀 REVIEW 

*PRs listos para review irán aquí*

---

### ✅ DONE

*Tareas completadas*

---

## 🎯 SCHEDULE MAÑANA (12 Marzo)

### **08:00 - Sprint Start**
1. **Database migration** (DatabaseAgent) - `BACKEND-DB-001`
2. **Web3 integration** (Web3Agent) - `FRONTEND-WEB3-004` 

### **Mid-day PRs Target**
- PR #1: PostgreSQL schema + Docker setup  
- PR #2: RainbowKit basic integration

### **End of Day Target**  
- PostgreSQL functional
- Web3 providers configured
- Base para jobs y webhook

---

## 🚧 DEPENDENCIES GRAPH

```
BACKEND-DB-001 (PostgreSQL)
├── BACKEND-JOBS-002 (APScheduler)
├── BACKEND-API-003 (History API)  
├── BACKEND-WEBHOOK-006 (Tips webhook)
└── DATA-HISTORICAL-007 (Data collection)

FRONTEND-WEB3-004 (RainbowKit)
├── FRONTEND-UX-008 (Animations)
└── BACKEND-WEBHOOK-006 (Tips webhook)

BACKEND-API-003 (History API)
└── FRONTEND-HISTORY-005 (History page)
```

---

## 📝 PR GUIDELINES

### **Branch Naming**
- `feature/backend-db-migration`
- `feature/frontend-web3-tips`
- `feature/history-page`

### **PR Description Template**
```markdown
## Task: [TASK-ID] - [Title]

### Changes
- [ ] Task 1 completed
- [ ] Task 2 completed

### Testing  
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] No console errors

### DoD Checklist
- [ ] [Specific DoD criteria from task]

### Screenshots (if UI)
*Add before/after screenshots*
```

---

## 🔍 TESTING STRATEGY

### **Per PR**
- Unit tests pass
- No TypeScript errors
- Manual smoke testing
- No console errors in dev

### **Integration Testing**
- End-to-end tip flow
- Database consistency  
- API endpoint functionality
- Cross-browser basics

---

## 📊 PROGRESS TRACKING

| Task ID | Owner | Status | Progress | ETA |
|---------|--------|--------|---------|-----|
| BACKEND-DB-001 | DatabaseAgent | 🆕 TODO | 0% | 12 Mar |
| FRONTEND-WEB3-004 | Web3Agent | 🆕 TODO | 0% | 12 Mar |
| BACKEND-JOBS-002 | SchedulerAgent | 🆕 TODO | 0% | 13 Mar |
| ... | ... | ... | ... | ... |

---

**Next Update:** Daily standup en BOARD.md con progress  
**Blocker Escalation:** Update BOARD.md + notify PM

---

*Última actualización: 11 Marzo 2026 21:05 - Sprint Setup Complete*