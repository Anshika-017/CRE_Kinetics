# Reaction Kinetics — Backend

FastAPI service implementing transparent integral- and differential-method
kinetic analysis of batch-reactor concentration-time data. No machine
learning is used — every number comes from explicit OLS regression, scipy
spline smoothing, or closed-form kinetic integration.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Set `ALLOWED_ORIGINS` (comma-separated) to control CORS, e.g.:

```bash
export ALLOWED_ORIGINS=http://localhost:5173
```

## Test

```bash
pytest -v
```

## API

- `GET /api/health`
- `POST /api/analyze` — body: `{ data: [{time, concentration}, ...], concentration_unit, time_unit, smoothing_strength, n_search_min, n_search_max, autocatalytic_C_R0 }`

See `app/api/routes.py` and `app/schemas/models.py` for the full request/response shape.

## Deployment (Render)

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `ALLOWED_ORIGINS=https://your-frontend.onrender.com`
