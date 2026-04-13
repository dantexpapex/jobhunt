# JobHunt AI - Sistema de Búsqueda de Empleo con IA

## Resumen Ejecutivo

Sistema automatizado de búsqueda de empleo que busca vacantes 24/7, genera CVs personalizados ATS-optimized, y aplica automáticamente a ofertas.

**Inspirado en**: Career-Ops (Santiago Fernández de Valderrama) y ApplyPilot

---

## Objetivos del Proyecto

- Buscar vacantes en múltiples portales automáticamente
- Evaluar ofertas con scoring IA (dimensiones A-F)
- Generar CVs personalizados ATS-optimized por empresa
- Aplicar automáticamente mientras duermes
- Tracking de todas las aplicaciones
- Notificaciones en tiempo real (Telegram)
- Dashboard para monitoreo

---

## Tech Stack

| Componente | Tecnología |
|------------|-------------|
| **Backend** | Python 3.11+ / Flask |
| **Scraping** | Playwright, Requests, python-jobspy |
| **IA** | Gemini API (gratis), OpenAI (fallback) |
| **DB** | SQLite (local) / PostgreSQL (producción) |
| **Scheduler** | APScheduler |
| **PDF** | ReportLab, FPDF |
| **UI** | Bootstrap 5 + JavaScript |
| **Notificaciones** | Telegram Bot API |
| **Deployment** | Contabo VPS (Ubuntu) + systemd |

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     JOBHUNT AI                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  SCRAPER    │───▶│   ANALYZER  │───▶│  CV GEN     │     │
│  │  (Playwright│    │  (Gemini    │    │  (PDF ATS   │     │
│  │   + Jobspy) │    │   API)      │    │   Optimized)│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  DATABASE (SQLite)                  │   │
│  │   - Jobs, Companies, Applications, CVs, Logs         │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  AUTO-APPLY │    │   SCHEDULER │    │   DASHBOARD │     │
│  │  (Playwright│    │  (24/7 runs)│    │  (Flask UI) │     │
│  │   forms)    │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                       │          │
│         ▼                                       ▼          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              TELEGRAM BOT (Notifications)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Módulos del Sistema

### 1. JobScraper
- **Fuente**: LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs
- **Workday**: 48+ portales de empresas
- **Careers Pages**: Meta, Google, Amazon, Microsoft, etc.
- **Tecnologías**: Playwright, python-jobspy, Requests

### 2. JobAnalyzer
- **Scoring** (dimensiones A-F):
  - A - Salary: Rango salarial vs esperado
  - B - Remote: Modalidad (remote/hybrid/onsite)
  - C - Tech Stack: Tecnologías requeridas
  - D - Experience: Nivel requerido
  - E - Company: Tamaño, etapa, reputación
  - F - Fit: Match general (0-100%)
- **Output**: Reporte JSON por oferta
- **IA**: Gemini API (gratis)

### 3. CVGenerator
- **Entrada**: Job description + CV base
- **Proceso**: Extraer keywords, reescribir experiencia, optimizar ATS
- **Salida**: PDF personalizado por empresa
- **Features**:
  - Keywords naturalizados
  - Formato ATS-compatible (sin imágenes, fuentes estándar)
  - Sections: Summary, Experience, Skills, Education

### 4. AutoApplier
- **Form filling**: Playwright automatizado
- **Rate limiting**: Delays entre aplicaciones
- **Anti-detection**: Rotación de user-agents, proxies
- **Human-in-the-loop**: Opción de revisión antes de enviar

### 5. JobTracker
- **Estados**: New, Evaluated, Applied, Interview, Rejected, Offer
- **Métricas**: Rate de éxito, tiempo promedio, empresas top
- **Historial**: Timeline por aplicación

### 6. Scheduler
- **Frecuencia**: Configurable (cada 1h, 6h, 12h, 24h)
- **Modos**:
  - Discovery: Buscar nuevas ofertas
  - Apply: Aplicar a ofertas calificadas
  - Follow-up: Revisar estado de aplicaciones
- **Ejecución**: 24/7 enbackground

### 7. Dashboard
- **UI Web**: Flask + Bootstrap
- **Features**:
  - Stats generales (aplicaciones, entrevistas,成功率)
  - Lista de ofertas encontradas
  - Estado de aplicaciones
  - Configuración de búsqueda
  - Logs de actividad

### 8. TelegramBot
- **Comandos**:
  - /start - Bienvenida
  - /stats - Estadísticas del día
  - /jobs - Ofertas recientes
  - /apply - Forzar aplicación
  - /stop - Pausar búsqueda
  - /resume - Reanudar búsqueda
- **Notificaciones**:
  - Nueva oferta encontrada
  - Aplicación enviada
  - Entrevista programada
  - Error/crash

---

## Fuentes de Búsqueda

### Portales Principales
| Portal | URL Base | Notes |
|--------|----------|-------|
| LinkedIn | linkedin.com/jobs | Requiere login |
| Indeed | indeed.com | Easy apply |
| Glassdoor | glassdoor.com | Reviews included |
| ZipRecruiter | ziprecruiter.com | API disponible |
| Google Jobs | jobs.google.com | Aggregator |

### Workday Portals (48+)
Automatizado para empresas como: Meta, Amazon, Google, Microsoft, etc.

### Careers Pages Directas
Configurables por usuario: lista de URLs de careers pages

---

## Configuración de Scoring

```python
SCORING_WEIGHTS = {
    'salary': 0.20,      # 20%
    'remote': 0.15,      # 15%
    'tech_stack': 0.25,  # 25%
    'experience': 0.15,  # 15%
    'company': 0.10,     # 10%
    'fit_score': 0.15,  # 15%
}

# Thresholds
APPLY_THRESHOLD = 70    # Apply automatically if >= 70%
REVIEW_THRESHOLD = 50   # Review if >= 50%
REJECT_THRESHOLD = 50   # Reject if < 50%
```

---

## Estructura de Archivos

```
jobhunt/
├── app.py                    # Flask app principal
├── requirements.txt          # Dependencias
├── config.py                 # Configuración
├── .env                      # Variables de entorno
├── │
├── core/
│   ├── __init__.py
│   ├── scraper.py           # Job scraper
│   ├── analyzer.py          # AI job analyzer
│   ├── cv_generator.py      # CV generator
│   ├── auto_applier.py      # Auto apply
│   ├── tracker.py           # Job tracker
│   ├── scheduler.py         # Scheduler
│   └── telegram_bot.py      # Telegram notifications
│
├── models/
│   ├── __init__.py
│   ├── database.py          # SQLite setup
│   ├── job.py              # Job model
│   ├── application.py      # Application model
│   └── cv.py               # CV model
│
├── routes/
│   ├── __init__.py
│   ├── api.py              # API endpoints
│   └── web.py              # Web routes
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── jobs.html
│   └── settings.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── data/
│   ├── jobs.db             # SQLite database
│   ├── cvs/                # Generated CVs
│   └── logs/               # Application logs
│
└── scripts/
    ├── init_db.py          # Initialize database
    ├── test_scraper.py     # Test scraper
    └── run_scheduler.py    # Run scheduler
```

---

## Variables de Entorno (.env)

```env
# API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

# Database
DATABASE_URL=sqlite:///data/jobs.db

# Search Configuration
SEARCH_KEYWORDS=software engineer,python,backend
SEARCH_LOCATIONS=Remote,United States,Europe
SEARCH_PORTALS=linkedin,indeed,glassdoor

# Application Settings
AUTO_APPLY_ENABLED=true
APPLY_THRESHOLD=70
MAX_APPLICATIONS_PER_DAY=50
MIN_DELAY_BETWEEN_APPLIES=300

# Login Credentials (for portals that need it)
LINKEDIN_EMAIL=your_email
LINKEDIN_PASSWORD=your_password
```

---

## Costos Estimados

| Servicio | Costo |
|----------|-------|
| **Gemini API** | Gratis (15 RPM, 1M tokens/día) |
| **OpenAI API** | $10-50/mes (fallback) |
| **Contabo VPS** | Ya tienes (~$7-15/mes) |
| **Dominio** | $5-10/año (opcional) |
| **Proxies** | $20-50/mes (opcional, para evitarblocks) |
| **Total** | **~$15-70/mes** |

---

## Cronograma de Desarrollo

| Fase | Descripción | Tiempo |
|------|-------------|--------|
| 1 | Setup proyecto + JobScraper básico | 1 semana |
| 2 | JobAnalyzer (IA) + CV Generator | 1 semana |
| 3 | AutoApplier + Scheduler | 1 semana |
| 4 | Dashboard + Telegram Bot | 1 semana |
| 5 | Testing + Debugging + Deploy | 1 semana |
| **Total** | | **5-6 semanas** |

---

## Métricas Objetivo

| Métrica | Objetivo |
|---------|----------|
| Ofertas analizadas/día | 100-500 |
| CVs enviados/día | 50-100+ |
| Entrevistas/semana | 5-15 |
| Rate de éxito | 10-30% |
| Tiempo activo | 24/7 |

---

## Consideraciones Éticas y Legales

### ⚠️ Riesgos
- **Términos de Servicio**: LinkedIn/portales pueden prohibir automatización
- **Anti-bot**: Probabilidad de blocks/bans
- **Ética**: No falsificar información en CVs

### ✅ Mejores Prácticas
- Usar con precaución y responsabilidad
- Human-in-the-loop para revisión
- Delays adecuados entre acciones
- Rotación de user-agents
- No abusar de rate limits
- Respetar robots.txt donde aplique

### 🔒 Privacidad
- No almacenar credenciales en texto plano
- Usar variables de entorno
- Logs sin información sensible

---

## Referencias

- [Career-Ops](https://github.com/santifer/career-ops) - Sistema original (30K+ stars)
- [ApplyPilot](https://github.com/Pickle-Pixel/ApplyPilot) - Auto-apply open source
- [python-jobspy](https://github.com/professor-lol/professor-lol) - Job scraping library

---

## Pendiente

- [ ] Inicializar proyecto
- [ ] Configurar entorno
- [ ] Implementar scraper
- [ ] Implementar analyzer
- [ ] Implementar CV generator
- [ ] Implementar auto-applier
- [ ] Implementar scheduler
- [ ] Implementar dashboard
- [ ] Implementar Telegram bot
- [ ] Deploy en Contabo

---

*Creado: 2026-04-13*
*Inspirado en Career-Ops by Santiago Fernández de Valderrama*