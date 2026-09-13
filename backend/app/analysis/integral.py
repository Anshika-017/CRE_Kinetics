"""
Integral method of analysis.

For each candidate reaction order n, the (already-derived) integrated
rate law transformation is applied to the RAW experimental data, a linear
regression against t is performed, and fit quality is recorded. The model
whose transformed plot is most linear (subject to the selection rules in
analysis/selection.py) is the integral-method candidate.
"""
from __future__ import annotations

from typing import List

import numpy as np
from scipy.optimize import minimize_scalar

from app.analysis.regression import ols_fit, original_domain_errors
from app.kinetics.models import (
    FIXED_ORDER_MODELS,
    make_nth_order_model,
)

FRACTIONAL_GRID = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]


def _evaluate_model(model: dict, t: np.ndarray, C: np.ndarray, C0: float) -> dict:
    x, y = model["transform"](t, C, C0)
    fit = ols_fit(x, y)

    result = {
        "id": model["id"],
        "name": model["name"],
        "n": model["n"],
        "rate_law_latex": model["rate_law_latex"],
        "integrated_equation_latex": model["integrated_equation_latex"],
        "transformation": model["transform_description"],
        "slope": fit["slope"],
        "intercept": fit["intercept"],
        "r_squared": fit["r_squared"],
        "rmse_transformed": fit["rmse"],
        "mae_transformed": fit["mae"],
        "n_points_used": fit["n_points"],
        "valid": fit["valid"],
        "reason": fit["reason"],
        "k": None,
        "k_units_exponent": model["n"],
        "original_domain_rmse": None,
        "original_domain_mae": None,
        "original_domain_max_error": None,
        "transformed_points": {"x": list(map(float, x)), "y": list(map(float, y))},
        "regression_line": None,
    }

    if not fit["valid"]:
        return result

    k = model["k_from_fit"](fit["slope"], fit["intercept"])
    result["k"] = float(k) if k is not None else None

    # Regression line for plotting (over the transformed x-range)
    x_line = np.linspace(float(np.min(x)), float(np.max(x)), 50)
    y_line = fit["slope"] * x_line + fit["intercept"]
    result["regression_line"] = {"x": list(map(float, x_line)), "y": list(map(float, y_line))}

    # Original-domain reconstruction & error, only if k is physically valid
    if result["k"] is not None and result["k"] >= 0:
        c_pred = model["predict"](t, C0, result["k"])
        errs = original_domain_errors(C, c_pred)
        result["original_domain_rmse"] = errs["rmse"]
        result["original_domain_mae"] = errs["mae"]
        result["original_domain_max_error"] = errs["max_abs_error"]
        result["prediction_curve"] = {
            "t": list(map(float, np.sort(t))),
        }
    else:
        result["warning"] = (
            "Fitted k is negative, which is not physically meaningful for an "
            "irreversible disappearance reaction. This model is de-prioritized."
        )

    return result


def _continuous_n_search(t: np.ndarray, C: np.ndarray, C0: float, n_min: float, n_max: float) -> dict:
    """Golden-section-style scalar optimization of n to maximize transformed R^2."""

    def neg_r2(n):
        if abs(n - 1.0) < 1e-6:
            from app.kinetics.models import FIRST_ORDER
            model = FIRST_ORDER
        else:
            model = make_nth_order_model(n)
        x, y = model["transform"](t, C, C0)
        fit = ols_fit(x, y)
        if not fit["valid"] or fit["r_squared"] is None:
            return 1.0  # worst possible (neg of -1 style penalty)
        return -fit["r_squared"]

    res = minimize_scalar(neg_r2, bounds=(n_min, n_max), method="bounded",
                           options={"xatol": 1e-3})
    best_n = float(res.x)
    if abs(best_n - 1.0) < 1e-6:
        from app.kinetics.models import FIRST_ORDER
        model = FIRST_ORDER
    else:
        model = make_nth_order_model(best_n)
    return _evaluate_model(model, t, C, C0)


def run_integral_analysis(
    t: List[float], C: List[float], n_min: float = -2.0, n_max: float = 5.0
) -> dict:
    t_arr = np.asarray(t, dtype=float)
    c_arr = np.asarray(C, dtype=float)
    order = np.argsort(t_arr, kind="stable")
    t_sorted, c_sorted = t_arr[order], c_arr[order]
    C0 = float(c_sorted[0])

    candidates = []
    for model in FIXED_ORDER_MODELS:
        candidates.append(_evaluate_model(model, t_sorted, c_sorted, C0))

    for n in FRACTIONAL_GRID:
        if n in (0.0, 1.0, 2.0):
            continue  # already covered by fixed-order models
        model = make_nth_order_model(n)
        candidates.append(_evaluate_model(model, t_sorted, c_sorted, C0))

    continuous_best = _continuous_n_search(t_sorted, c_sorted, C0, n_min, n_max)
    candidates.append({**continuous_best, "id": continuous_best["id"] + "_continuous",
                        "name": continuous_best["name"] + " (continuous search)"})

    # Rank by transformed R^2 among physically valid (k >= 0) candidates.
    def sort_key(c):
        if not c["valid"] or c["r_squared"] is None:
            return -1
        if c.get("k") is None or c["k"] < 0:
            return c["r_squared"] - 1.0  # penalize but keep visible
        return c["r_squared"]

    ranked = sorted(candidates, key=sort_key, reverse=True)
    for i, c in enumerate(ranked):
        c["rank"] = i + 1
        c["status"] = "BEST" if i == 0 else None

    best = ranked[0]

    return {
        "method": "integral",
        "C_A0": C0,
        "n_search_range": {"min": n_min, "max": n_max},
        "fractional_grid_tested": FRACTIONAL_GRID,
        "models": ranked,
        "best_model": best,
        "explanation": (
            "The integral method assumes a candidate rate law, integrates it, and "
            "transforms the raw experimental concentration data so that a correctly "
            "chosen kinetic order produces a straight line versus time. Each "
            "candidate order is scored by the linearity (R\u00b2) of its transformed "
            "plot and by how well the reconstructed C_A(t) curve matches the "
            "original experimental data."
        ),
    }
