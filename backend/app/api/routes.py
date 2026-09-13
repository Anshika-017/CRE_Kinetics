from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.models import AnalyzeRequest, HealthResponse
from app.validation.validators import validate_data
from app.analysis.integral import run_integral_analysis
from app.analysis.differential import run_differential_analysis
from app.analysis.autocatalytic import run_autocatalytic_analysis
from app.analysis.selection import compare_methods
from app.utils.units import k_units

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "service": "reaction-kinetics-backend"}


@router.post("/analyze")
def analyze(payload: AnalyzeRequest):
    times = [p.time for p in payload.data]
    concentrations = [p.concentration for p in payload.data]

    validation = validate_data(times, concentrations)
    if not validation["valid"]:
        # Data errors -> return validation only, HTTP 422 so the frontend
        # can distinguish "bad input" from "server error".
        raise HTTPException(status_code=422, detail={"validation": validation})

    integral = run_integral_analysis(
        times, concentrations, payload.n_search_min, payload.n_search_max
    )
    differential = run_differential_analysis(times, concentrations, payload.smoothing_strength)
    autocatalytic = run_autocatalytic_analysis(times, concentrations, payload.autocatalytic_C_R0)
    comparison = compare_methods(integral, differential)

    best = integral["best_model"]
    n_best = best.get("n")
    result = {
        "validation": validation,
        "units": {
            "concentration_unit": payload.concentration_unit,
            "time_unit": payload.time_unit,
            "k_units": k_units(n_best, payload.concentration_unit, payload.time_unit)
            if n_best is not None else None,
        },
        "integral": integral,
        "differential": differential,
        "autocatalytic": autocatalytic,
        "comparison": comparison,
        "assumptions": [
            "Constant-volume batch reactor.",
            "Single measured reactant concentration C_A.",
            "Irreversible reaction A -> products (standard order models).",
            "Isothermal conditions; k constant over the experiment.",
            "No mass-transfer limitation and no volume change unless stated.",
            "Reaction order is an empirical fit to the supplied data, not a claim about mechanism.",
        ],
    }
    return result
