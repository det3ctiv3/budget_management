# Fintech MVP

FastAPI-based personal finance API + static web UI.
Core features: accounts, expenses, incomes, transfers, debts, budgets, analytics, and rule-based AI category/alerts.

## Run with Docker (Recommended)
```bash
cp .env.example .env
docker compose up --build
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:5500`

## Run Manually (Local Python)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload
```

Serve UI:
```bash
cd ui
python -m http.server 5500
```

## Quick Demo
After API is running:
```bash
./demo.sh
```
