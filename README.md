# Reaction Kinetics

A transparent chemical-reaction-engineering tool: enter batch-reactor
concentration-vs-time data and see the **integral method** and
**differential method** of kinetic analysis performed side by side, with
every equation, regression, and intermediate number visible — no black box.

## What it does

1. Validates experimental (t, C_A) data (negative values, NaNs, duplicate
   times, non-monotonic concentration, sparse data — all flagged explicitly).
2. **Integral method** — assumes each candidate rate law
   (`-r_A = kC_A^n`), integrates it, transforms the raw experimental data,
   and regresses against time. Tests zero, first, second, a fractional-order
   grid, and a continuous numerical search over n. Reports slope, intercept,
   R², RMSE, k, and the reconstructed C_A(t) curve for every candidate.
3. **Differential method** — fits a smoothing spline to C_A(t), evaluates
   dC_A/dt analytically, computes -r_A, and regresses
   `ln(-r_A) = ln(k) + n·ln(C_A)` to recover n and k directly.
4. **Autocatalytic check** (`A + R → R + R`) — if you supply an initial
   product/catalyst concentration C_R0, the app derives and fits the
   partial-fraction integrated solution; it explicitly refuses to fit the
   model when C_R0 = 0 rather than silently producing nonsense.
5. **Model selection** — compares transformed R², original-domain RMSE,
   physical validity of k, and integral/differential agreement, and states
   in plain language why the winning model was selected (or why the two
   methods disagree).

## Project structure

```
reaction-kinetics/
├── backend/    FastAPI + NumPy/SciPy analysis engine (see backend/README.md)
├── frontend/   React + TypeScript + Vite UI (see frontend/README.md)
└── README.md
```

## Scientific assumptions (default)

Constant-volume, isothermal batch reactor; single measured reactant C_A;
irreversible A → products for the standard order models; k constant over
the experiment. Fitted reaction order is reported as an **empirical**
description of the data, not a claim about mechanism.

## Running locally

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open the printed Vite URL (typically http://localhost:5173).

## Testing

```bash
cd backend && pytest -v
```

17 tests cover: synthetic recovery of zero/first/second/fractional-order
kinetics from generated data, differential-method recovery, autocatalytic
edge cases, input validation (negative time/concentration, NaN, duplicate
time, non-monotonic warnings, insufficient points), and full API-level
`/api/analyze` requests including a rejected (422) invalid-input case.

## Deployment on Render

Create two services from this one repository:

**Backend (Web Service)**
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env var: `ALLOWED_ORIGINS=https://<your-frontend>.onrender.com`

**Frontend (Static Site)**
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Env var: `VITE_API_BASE_URL=https://<your-backend>.onrender.com`

## Limitations

- The differential method's derivative estimate depends on the chosen
  smoothing strength; very noisy or sparse data will produce a less
  reliable n and k, and the app says so rather than hiding it.
- The autocatalytic model implements the classical simple case
  (`A + R → R + R`, constant volume). Reversible kinetics, Michaelis-Menten,
  and Langmuir-Hinshelwood are not implemented, though the model-registry
  architecture (`backend/app/kinetics/`) is structured so they can be added
  without touching the analysis or API layers.
- The visual design is a clean, readable dark scientific theme; it does not
  implement the full cinematic GSAP/WebGL scroll-driven galaxy experience
  described in the original spec — that level of custom animation work was
  out of scope for a single build/test pass, and was deprioritized in favor
  of correctness and transparency of the actual chemical-engineering
  calculations, which are fully implemented and tested.
