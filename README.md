# JobHunt AI 🤖

Sistema automatizado de búsqueda de empleo con IA. Busca, filtra, adapta tu CV y te ayuda en todo el proceso.

---

## Estado del Proyecto

**Última actualización:** 13/04/2026  
**Versión:** 1.0.0

---

## 🚀 Quick Start

```bash
# Clonar
git clone https://github.com/dantexpapex/jobhunt.git
cd jobhunt

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tu GEMINI_API_KEY

# Ejecutar
python app.py
```

**Web:** http://localhost:5000

---

## 📋 Módulos Implementados

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **Scraper** | ✅ | RemoteOK, HackerNews, Indeed |
| **ATS Optimizer** | ✅ | Keywords + Score 0-100 |
| **CV Adapter** | ✅ | Adapta tu CV al job |
| **Pipeline** | ✅ | Automático (cada 6h) |
| **Tracker (CSV)** | ✅ | Seguimiento local |
| **Dashboard** | ✅ | UI web Flask |
| **Company Ranking** | ✅ | Tier S/A/B/C/D |
| **Success Prediction** | ✅ | IA predice % éxito |
| **Interview Bot** | ✅ | Respuestas + Cheatsheet |
| **Follow-up Emails** | ✅ | Emails automático |

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# API Keys
GEMINI_API_KEY=tu_api_key_de_gemini

# Búsqueda
SEARCH_KEYWORDS=python,backend,developer
SEARCH_LOCATIONS=Remote,United States
SEARCH_PORTALS=remoteok

# Aplicación
AUTO_APPLY_ENABLED=false
APPLY_THRESHOLD=70
MAX_APPLICATIONS_PER_DAY=50
```

### Obtener Gemini API Key
1. Ve a: https://aistudio.google.com/app/apikey
2. Crea una nueva clave
3. Agrega a .env

---

## 📊 Uso del Sistema

### Pipeline Automático

```bash
# Ejecutar pipeline manualmente
python scripts/run_pipeline.py
```

**Flujo:**
1. Scraper busca jobs (RemoteOK)
2. ATS Analyzer extrae keywords
3. Score ATS >70% → cola
4. Dashboard → Revisas → Apruebas

### API Endpoints

```bash
# Buscar jobs
POST /api/search

# Ver tracker
GET /api/tracker/all

# Ranking empresa
GET /api/ranking/company/Google

# Predicción éxito
POST /api/predict/success
{"job_data": {...}, "history": {"applied": 10, "interview": 2}}

# Respuesta entrevista
POST /api/interview/response
{"question": "Tell me about yourself", "context": "Python role"}

# Email follow-up
POST /api/email/followup
{"type": "after_apply", "company": "TechCorp", "position": "Developer"}
```

### Dashboard

| URL | Descripción |
|-----|-------------|
| `/` | Dashboard principal |
| `/jobs` | Lista de trabajos |
| `/applications` | Cola de aplicaciones |
| `/interview` | Prep de entrevistas |
| `/settings` | Configuración |

---

## 📁 Estructura del Proyecto

```
jobhunt/
├── app.py                 # Flask app
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── .env                  # Variables (no subir a git)
│
├── core/                 # Módulos principales
│   ├── scraper.py       # Buscar jobs
│   ├── ats_optimizer.py # Optimización ATS
│   ├── cv_adapter.py    # Adaptar CV
│   ├── cv_manager.py    # Gestionar CVs
│   ├── ai_engine.py     # Motor IA
│   ├── pipeline.py      # Pipeline completo
│   ├── tracker.py      # Seguimiento
│   ├── interview_bot.py # Entrevistas
│   └── advanced_features.py # Ranking + Predicción
│
├── models/               # Modelos DB
├── routes/              # API + Web
├── templates/           # UI HTML
├── scripts/             # Tests
└── CV-trabajp/        # Tus CVs
```

---

## 🔄 Historial de Versiones

### v1.0.0 (13/04/2026)
- ✅ Scraper implementado (RemoteOK, HackerNews)
- ✅ ATS Optimizer con keywords
- ✅ CV Adapter que adapta CVs
- ✅ Pipeline automático
- ✅ Tracker CSV local
- ✅ Dashboard web
- ✅ Company Ranking
- ✅ Success Prediction
- ✅ Interview Response Generator
- ✅ Follow-up Email Bot

---

## ⚠️ Limitaciones Actuales

- **Gemini API:** Cuota gratuita limitada (puede agotarse)
- **LinkedIn/Indeed:** Bloquean scraping (no funcionan)
- **Google Sheets:** Requiere credenciales (opcional)

---

## 📈 Métricas Objetivo

| Métrica | Objetivo |
|---------|----------|
| Jobs encontrados/día | 50-100 |
| Matches ATS (>70%) | 10-20 |
| Aplicaciones/día | 10-30 |
| Entrevistas/semana | 3-10 |

---

## 🤝 Contribuir

1. Fork el repo
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m "Agrega..."`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Usa el código freely

---

*Creado con ❤️ por Dante Montaño*
