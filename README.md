# AI Medical Report Analyzer

> **Disclaimer:** This system is for informational purposes only and does not provide medical diagnosis.

A production-ready AI-powered medical transcription analysis system built with FastAPI, PostgreSQL, and a glassmorphism frontend.

---

## Features

| Feature | Details |
|---------|---------|
| 📄 **File Upload** | TXT and PDF support (up to 10MB) |
| 🧠 **AI Analysis** | GPT-4o-mini via OpenAI API (or compatible) |
| 🔬 **Entity Extraction** | Symptoms, medications, procedures, lab values, body parts |
| 🏥 **Specialty Classification** | AI + rule-based fallback |
| ⚠️ **Risk Detection** | High-priority clinical keyword flagging |
| 📝 **Dual Summaries** | Professional + patient-friendly |
| 🎯 **Confidence Score** | 0–100% analysis confidence |
| 💾 **History** | PostgreSQL persistence + paginated view |
| 📊 **Export** | Download full analysis as JSON |
| 🔒 **Security** | Rate limiting, CORS, file validation |
| ⚡ **Caching** | Redis cache + in-memory fallback |
| 🐳 **Docker** | Full containerized deployment |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <your-repo>
cd "HealthTech system"
cp .env.example .env
```

Edit `.env` and set your API key:
```
MEDICAL_AI_API_KEY=your-openai-api-key-here
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start PostgreSQL (local)

```bash
# Using Docker
docker run -d --name medanalyze_db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=medical_analyzer \
  -p 5432:5432 postgres:16-alpine
```

### 4. Run the Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open: **http://localhost:8000**  
Swagger API Docs: **http://localhost:8000/docs**

---

## Docker Deployment

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your MEDICAL_AI_API_KEY

# Build and start all services
docker compose up -d --build

# Check logs
docker compose logs -f app

# Run database migrations
docker compose exec app alembic upgrade head
```

Services:
- **App:** http://localhost:8000
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

---

## Database Migrations

```bash
# Run all migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one step
alembic downgrade -1
```

---

## API Reference

### Upload & Analyze

```bash
curl -X POST http://localhost:8000/api/v1/reports/upload \
  -F "file=@report.txt"
```

### List History

```bash
curl "http://localhost:8000/api/v1/reports?page=1&per_page=20"
```

### Get Report

```bash
curl http://localhost:8000/api/v1/reports/{report-uuid}
```

### Export JSON

```bash
curl -O http://localhost:8000/api/v1/reports/{report-uuid}/export
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

---

## Project Structure

```
HealthTech system/
├── app/
│   ├── main.py                     # FastAPI entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── reports.py          # Report CRUD endpoints
│   │   │   └── health.py           # Health check
│   │   └── middleware/
│   │       ├── rate_limiter.py     # Sliding window rate limit
│   │       └── logging_middleware.py
│   ├── services/
│   │   ├── ai_service.py           # LLM integration + retry
│   │   ├── extraction_service.py   # Analysis orchestration
│   │   ├── classification_service.py # Specialty + risk detection
│   │   └── cache_service.py        # Redis cache
│   ├── models/
│   │   └── report.py               # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── report.py               # Pydantic request/response schemas
│   ├── database/
│   │   └── session.py              # Async SQLAlchemy engine
│   ├── core/
│   │   ├── config.py               # Centralized settings (Pydantic)
│   │   └── logging_config.py
│   └── utils/
│       ├── file_handler.py         # PDF/TXT text extraction
│       └── text_chunker.py         # Document chunking strategy
├── frontend/
│   ├── index.html                  # Glassmorphism dashboard
│   ├── style.css                   # 3D effects, animations, dark mode
│   └── app.js                      # Vanilla JS Fetch API
├── alembic/                        # Database migrations
├── scripts/
│   └── preprocess_kaggle.py        # Kaggle dataset preprocessor
├── Dockerfile                      # Multi-stage production build
├── docker-compose.yml              # Full stack deployment
├── requirements.txt
└── .env.example
```

---

## Kaggle Dataset

To preprocess the [Medical Transcriptions dataset](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions):

```bash
# 1. Download mtsamples.csv from Kaggle
# 2. Place in scripts/data/mtsamples.csv
# 3. Run:
python scripts/preprocess_kaggle.py

# Output: scripts/data/cleaned_transcriptions.csv
#         scripts/data/sample_reports/ (TXT files for testing upload)
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MEDICAL_AI_API_KEY` | ✅ Yes | — | OpenAI (or compatible) API key |
| `DATABASE_URL` | ✅ Yes | — | PostgreSQL async connection URL |
| `AI_MODEL` | No | `gpt-4o-mini` | LLM model to use |
| `AI_TEMPERATURE` | No | `0.2` | AI response temperature |
| `REDIS_ENABLED` | No | `false` | Enable Redis caching |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL |
| `RATE_LIMIT_REQUESTS` | No | `5` | Max requests per window |
| `RATE_LIMIT_WINDOW` | No | `60` | Rate limit window (seconds) |
| `MAX_FILE_SIZE_MB` | No | `10` | Maximum upload file size |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## Security

- ✅ API key never hardcoded — loaded from environment only
- ✅ File type and size validation before processing
- ✅ Rate limiting (5 req/60s per IP)
- ✅ CORS configured per environment
- ✅ Non-root Docker user
- ✅ Input sanitization (HTML escaping in frontend)
- ✅ Structured error responses (no stack traces in production)

---

## License

MIT License — For educational and informational use only.

> **Medical Disclaimer:** This system is for informational purposes only and does not provide medical diagnosis. Always consult a qualified healthcare professional for medical advice.
