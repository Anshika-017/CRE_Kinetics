from __future__ import annotations

from typing import List, Optional

import numpy as np

from app.analysis.regression import ols_fit, original_domain_errors
from app.kinetics.autocatalytic import (
    autocatalytic_transform,
    autocatalytic_predict,
    autocatalytic_k_from_slope,
)


def run_autocatalytic_analysis(t: List[float], C: List[float], C_R0: Optional[float]) -> dict:
    t_arr = np.asarray(t, dtype=float)
    c_arr = np.asarray(C, dtype=float)
    order = np.argsort(t_arr, kind="stable")
    t_sorted, c_sorted = t_arr[order], c_arr[order]
    C_A0 = float(c_sorted[0])

    if C_R0 is None:
        return {
            "method": "autocatalytic",
            "applicable": False,
            "reason": (
                "No initial product/catalyst concentration C_R0 was supplied. "
                "The autocatalytic check is skipped; provide C_R0 to enable it."
            ),
        }

    if C_R0 <= 0:
        return {
            "method": "autocatalytic",
            "applicable": False,
            "reason": (
                "Autocatalytic model cannot be initialized with C_R0 = 0 under the "
                "idealized A + R -> 2R model, since the rate law -r_A = kC_A C_R "
                "would be zero at t = 0. Supply a nonzero C_R0 to test this model."
            ),
        }

    x, y, C0 = autocatalytic_transform(t_sorted, c_sorted, C_A0, C_R0)
    fit = ols_fit(x, y)

    result = {
        "method": "autocatalytic",
        "applicable": True,
        "C_A0": C_A0,
        "C_R0": C_R0,
        "C0": C0,
        "rate_law_latex": r"-r_A = kC_AC_R",
        "integrated_equation_latex": (
            r"\ln\left[\frac{C_{A0}(C_0-C_A)}{C_A(C_0-C_{A0})}\right] = C_0 kt"
        ),
        "slope": fit["slope"],
        "intercept": fit["intercept"],
        "r_squared": fit["r_squared"],
        "n_points_used": fit["n_points"],
        "valid": fit["valid"],
        "transformed_points": {"x": list(map(float, x)), "y": list(map(float, y))},
    }

    if not fit["valid"]:
        result["reason"] = fit["reason"]
        return result

    k = autocatalytic_k_from_slope(fit["slope"], C0)
    result["k"] = float(k) if k is not None else None

    x_line = np.linspace(float(np.min(x)), float(np.max(x)), 50) if len(x) else []
    y_line = fit["slope"] * np.asarray(x_line) + fit["intercept"] if len(x) else []
    result["regression_line"] = {"x": list(map(float, x_line)), "y": list(map(float, y_line))}

    if result["k"] is not None and result["k"] >= 0:
        c_pred = autocatalytic_predict(t_sorted, C_A0, C_R0, result["k"])
        errs = original_domain_errors(c_sorted, c_pred)
        result["original_domain_rmse"] = errs["rmse"]
        result["original_domain_mae"] = errs["mae"]
        result["prediction_curve"] = {
            "t": list(map(float, t_sorted)),
            "C_A_predicted": [None if np.isnan(v) else float(v) for v in c_pred],
        }

    return result
