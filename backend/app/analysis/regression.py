"""
Ordinary least-squares regression and fit-quality metrics.

These are the only numerical primitives used for every linear fit in the
application (integral transformations, differential log-log fit, etc.).
Nothing here is a "black box" -- it is textbook OLS plus standard error
metrics, applied to whatever x/y arrays the caller has already transformed
according to the chosen kinetic model.
"""
from __future__ import annotations

import numpy as np


def ols_fit(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Fit y = slope * x + intercept by ordinary least squares.

    Returns slope, intercept, r_squared, rmse, mae, and the fitted y values
    (y_hat) so the caller can also compute original-domain residuals.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    mask = np.isfinite(x) & np.isfinite(y)
    x_clean, y_clean = x[mask], y[mask]

    if x_clean.size < 2:
        return {
            "slope": None,
            "intercept": None,
            "r_squared": None,
            "rmse": None,
            "mae": None,
            "n_points": int(x_clean.size),
            "valid": False,
            "reason": "Fewer than 2 valid points after removing non-finite values.",
        }

    # np.polyfit(deg=1) solves the normal equations for a straight line.
    slope, intercept = np.polyfit(x_clean, y_clean, 1)
    y_hat = slope * x_clean + intercept

    ss_res = float(np.sum((y_clean - y_hat) ** 2))
    ss_tot = float(np.sum((y_clean - np.mean(y_clean)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else (1.0 if ss_res == 0 else 0.0)

    rmse = float(np.sqrt(np.mean((y_clean - y_hat) ** 2)))
    mae = float(np.mean(np.abs(y_clean - y_hat)))

    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "rmse": rmse,
        "mae": mae,
        "n_points": int(x_clean.size),
        "valid": True,
        "reason": None,
    }


def original_domain_errors(c_exp: np.ndarray, c_pred: np.ndarray) -> dict:
    """RMSE / MAE / max-abs-error between experimental and predicted C_A(t)."""
    c_exp = np.asarray(c_exp, dtype=float)
    c_pred = np.asarray(c_pred, dtype=float)
    mask = np.isfinite(c_exp) & np.isfinite(c_pred)
    if mask.sum() == 0:
        return {"rmse": None, "mae": None, "max_abs_error": None}
    resid = c_exp[mask] - c_pred[mask]
    return {
        "rmse": float(np.sqrt(np.mean(resid ** 2))),
        "mae": float(np.mean(np.abs(resid))),
        "max_abs_error": float(np.max(np.abs(resid))),
    }
