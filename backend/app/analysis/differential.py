"""
Differential method of analysis.

1. Fit a smoothing spline to experimental C_A(t).
2. Evaluate the spline and its derivative at the experimental time points
   to get C_smooth and dC_A/dt.
3. -r_A = -dC_A/dt.
4. Test:
     - zero order:  -r_A vs 1               (rate ~ constant)
     - first order: -r_A vs C_A             (slope = k)
     - second order:-r_A vs C_A^2           (slope = k)
     - nth order:   ln(-r_A) vs ln(C_A)     (slope = n, intercept = ln k)
"""
from __future__ import annotations

from typing import List

import numpy as np

from app.analysis.regression import ols_fit
from app.analysis.smoothing import fit_smooth_curve, evaluate_derivative


def run_differential_analysis(t: List[float], C: List[float], smoothing_strength: float = 0.5) -> dict:
    t_arr = np.asarray(t, dtype=float)
    c_arr = np.asarray(C, dtype=float)
    order = np.argsort(t_arr, kind="stable")
    t_sorted, c_sorted = t_arr[order], c_arr[order]

    if len(t_sorted) < 4:
        return {
            "method": "differential",
            "valid": False,
            "reason": "Insufficient data for reliable differential analysis "
                      "(at least 4 points are recommended for spline-based "
                      "derivative estimation).",
        }

    spline, s_used, smoothing_desc = fit_smooth_curve(t_sorted, c_sorted, smoothing_strength)
    c_smooth, dcdt = evaluate_derivative(spline, t_sorted)
    rate = -dcdt  # -r_A = -dC_A/dt

    table = []
    for ti, ci, csi, dci, ri in zip(t_sorted, c_sorted, c_smooth, dcdt, rate):
        row = {
            "t": float(ti),
            "C_A": float(ci),
            "C_smooth": float(csi),
            "dC_A_dt": float(dci),
            "minus_r_A": float(ri),
            "ln_C_A": float(np.log(ci)) if ci > 0 else None,
            "ln_minus_r_A": float(np.log(ri)) if ri > 0 else None,
        }
        table.append(row)

    valid_mask = rate > 0
    valid_c = c_smooth[valid_mask]
    valid_rate = rate[valid_mask]

    models = []

    # --- Zero order: rate approx constant -> rate vs constant(1) ---
    if len(valid_rate) >= 2:
        mean_rate = float(np.mean(valid_rate))
        ss_tot = float(np.sum((valid_rate - mean_rate) ** 2))
        ss_res = float(np.sum((valid_rate - mean_rate) ** 2))  # model = constant
        r2_zero = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
        models.append({
            "id": "zero_order", "name": "Zero order", "n": 0.0,
            "graph": "-r_A vs t (approximately constant)",
            "slope": 0.0, "intercept": mean_rate,
            "k": mean_rate, "r_squared": r2_zero if ss_tot > 0 else 1.0,
            "rate_law_latex": r"-r_A = k",
        })

    # --- First order: -r_A vs C_A, slope = k ---
    if len(valid_c) >= 2:
        fit1 = ols_fit(valid_c, valid_rate)
        models.append({
            "id": "first_order", "name": "First order", "n": 1.0,
            "graph": "-r_A vs C_A", "slope": fit1["slope"], "intercept": fit1["intercept"],
            "k": fit1["slope"], "r_squared": fit1["r_squared"],
            "rate_law_latex": r"-r_A = kC_A",
        })

    # --- Second order: -r_A vs C_A^2, slope = k ---
    if len(valid_c) >= 2:
        fit2 = ols_fit(valid_c ** 2, valid_rate)
        models.append({
            "id": "second_order", "name": "Second order", "n": 2.0,
            "graph": "-r_A vs C_A^2", "slope": fit2["slope"], "intercept": fit2["intercept"],
            "k": fit2["slope"], "r_squared": fit2["r_squared"],
            "rate_law_latex": r"-r_A = kC_A^2",
        })

    # --- General nth order: ln(-r_A) vs ln(C_A) ---
    ln_valid_mask = (c_smooth > 0) & (rate > 0)
    nth_result = None
    if np.sum(ln_valid_mask) >= 2:
        x_ln = np.log(c_smooth[ln_valid_mask])
        y_ln = np.log(rate[ln_valid_mask])
        fit_n = ols_fit(x_ln, y_ln)
        n_est = fit_n["slope"]
        k_est = float(np.exp(fit_n["intercept"])) if fit_n["intercept"] is not None else None
        x_line = np.linspace(float(np.min(x_ln)), float(np.max(x_ln)), 50)
        y_line = fit_n["slope"] * x_line + fit_n["intercept"]
        nth_result = {
            "id": "nth_order", "name": f"n = {n_est:.3g} order" if n_est is not None else "nth order",
            "n": n_est,
            "graph": "ln(-r_A) vs ln(C_A)",
            "slope": fit_n["slope"], "intercept": fit_n["intercept"],
            "k": k_est, "r_squared": fit_n["r_squared"],
            "rmse": fit_n["rmse"],
            "rate_law_latex": r"-r_A = kC_A^n",
            "equation_latex": r"\ln(-r_A) = \ln k + n\ln C_A",
            "points": {"x": list(map(float, x_ln)), "y": list(map(float, y_ln))},
            "regression_line": {"x": list(map(float, x_line)), "y": list(map(float, y_line))},
        }
        models.append(nth_result)

    ranked = sorted(
        [m for m in models if m.get("r_squared") is not None],
        key=lambda m: m["r_squared"], reverse=True,
    )
    for i, m in enumerate(ranked):
        m["rank"] = i + 1
        m["status"] = "BEST" if i == 0 else None

    best = nth_result if nth_result is not None else (ranked[0] if ranked else None)

    return {
        "method": "differential",
        "valid": True,
        "smoothing": {
            "strength": smoothing_strength,
            "s_parameter": s_used,
            "description": smoothing_desc,
        },
        "derivative_table": table,
        "models": ranked,
        "best_model": best,
        "explanation": (
            "The differential method estimates the instantaneous rate -r_A = "
            "-dC_A/dt directly from a smoothed C_A(t) curve, then fits "
            "ln(-r_A) = ln(k) + n ln(C_A) by linear regression: the slope gives "
            "the reaction order n and the intercept gives ln(k). This method is "
            "more direct than the integral method but more sensitive to noise, "
            "since differentiation amplifies measurement error."
        ),
    }
