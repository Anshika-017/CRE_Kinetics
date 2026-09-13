"""
Kinetic model registry.

Sign convention used throughout the whole backend (Part 62 of the spec):

    -r_A = -dC_A/dt = k * C_A^n        (irreversible disappearance of A)

so both -r_A and k are positive for a normal disappearance reaction.

Each model exposes:
    name, order_fixed (or None for a search), rate_law_latex,
    integrated_equation_latex, transform(t, C, C0) -> (x, y),
    predict(t, C0, k) -> C_A(t),
    k_from_slope_intercept(slope, intercept) -> k
    domain_valid(C) -> bool / warning

This keeps every model self-contained so new models (Michaelis-Menten,
reversible kinetics, etc.) can be added later without touching the
integral/differential analysis code.
"""
from __future__ import annotations

import numpy as np


class ModelDomainError(Exception):
    pass


# ---------------------------------------------------------------------------
# ZERO ORDER:  -r_A = k            =>   C_A = C_A0 - k t
# ---------------------------------------------------------------------------
def zero_order_transform(t, C, C0):
    return np.asarray(t, dtype=float), np.asarray(C, dtype=float)


def zero_order_predict(t, C0, k):
    t = np.asarray(t, dtype=float)
    c = C0 - k * t
    # Physically, concentration cannot go negative -- clip but flag via caller.
    return np.clip(c, 0, None)


def zero_order_k_from_fit(slope, intercept):
    return -slope  # slope = -k


ZERO_ORDER = {
    "id": "zero_order",
    "name": "Zero order",
    "n": 0.0,
    "rate_law_latex": r"-r_A = k",
    "integrated_equation_latex": r"C_A = C_{A0} - kt",
    "transform_description": "y = C_A, x = t",
    "transform": zero_order_transform,
    "predict": zero_order_predict,
    "k_from_fit": zero_order_k_from_fit,
    "slope_meaning": "slope = -k",
    "intercept_meaning": "intercept = C_A0",
}


# ---------------------------------------------------------------------------
# FIRST ORDER: -r_A = k C_A        =>   ln(C_A) = ln(C_A0) - k t
# ---------------------------------------------------------------------------
def first_order_transform(t, C, C0):
    C = np.asarray(C, dtype=float)
    t = np.asarray(t, dtype=float)
    valid = C > 0
    return t[valid], np.log(C[valid])


def first_order_predict(t, C0, k):
    t = np.asarray(t, dtype=float)
    return C0 * np.exp(-k * t)


def first_order_k_from_fit(slope, intercept):
    return -slope


FIRST_ORDER = {
    "id": "first_order",
    "name": "First order",
    "n": 1.0,
    "rate_law_latex": r"-r_A = kC_A",
    "integrated_equation_latex": r"\ln(C_A) = \ln(C_{A0}) - kt",
    "transform_description": "y = ln(C_A), x = t",
    "transform": first_order_transform,
    "predict": first_order_predict,
    "k_from_fit": first_order_k_from_fit,
    "slope_meaning": "slope = -k",
    "intercept_meaning": "intercept = ln(C_A0)",
}


# ---------------------------------------------------------------------------
# SECOND ORDER: -r_A = k C_A^2     =>   1/C_A = 1/C_A0 + k t
# ---------------------------------------------------------------------------
def second_order_transform(t, C, C0):
    C = np.asarray(C, dtype=float)
    t = np.asarray(t, dtype=float)
    valid = C > 0
    return t[valid], 1.0 / C[valid]


def second_order_predict(t, C0, k):
    t = np.asarray(t, dtype=float)
    denom = (1.0 / C0) + k * t
    with np.errstate(divide="ignore"):
        c = np.where(denom > 0, 1.0 / denom, np.nan)
    return c


def second_order_k_from_fit(slope, intercept):
    return slope  # slope = k directly


SECOND_ORDER = {
    "id": "second_order",
    "name": "Second order",
    "n": 2.0,
    "rate_law_latex": r"-r_A = kC_A^2",
    "integrated_equation_latex": r"\frac{1}{C_A} = \frac{1}{C_{A0}} + kt",
    "transform_description": "y = 1/C_A, x = t",
    "transform": second_order_transform,
    "predict": second_order_predict,
    "k_from_fit": second_order_k_from_fit,
    "slope_meaning": "slope = k",
    "intercept_meaning": "intercept = 1/C_A0",
}


# ---------------------------------------------------------------------------
# GENERAL nTH ORDER (n != 1):
#   -dC_A/dt = k C_A^n
#   C_A^(1-n) = C_A0^(1-n) - (1-n) k t
# Linear form (works for both n>1 and n<1 with correct sign):
#   y = C_A^(1-n),  x = t
#   slope = -(1-n) k   =>  k = -slope / (1-n)
# ---------------------------------------------------------------------------
def nth_order_transform(t, C, C0, n):
    C = np.asarray(C, dtype=float)
    t = np.asarray(t, dtype=float)
    valid = C > 0
    y = np.power(C[valid], 1.0 - n)
    return t[valid], y


def nth_order_predict(t, C0, k, n):
    t = np.asarray(t, dtype=float)
    one_minus_n = 1.0 - n
    base = np.power(C0, one_minus_n) - one_minus_n * k * t
    # The inverse power is only real/physical while base >= 0.
    with np.errstate(invalid="ignore"):
        c = np.where(base >= 0, np.power(np.clip(base, 0, None), 1.0 / one_minus_n), np.nan)
    return c


def nth_order_k_from_fit(slope, intercept, n):
    one_minus_n = 1.0 - n
    return -slope / one_minus_n


def make_nth_order_model(n: float) -> dict:
    """Build an nth-order model dict for a specific (possibly fractional) n != 1."""
    if abs(n - 1.0) < 1e-9:
        return FIRST_ORDER
    n_disp = round(n, 4)
    return {
        "id": f"nth_order_{n_disp}",
        "name": f"n = {n_disp:g} order",
        "n": n,
        "rate_law_latex": rf"-r_A = kC_A^{{{n_disp:g}}}",
        "integrated_equation_latex": (
            rf"C_A^{{{round(1 - n_disp, 4):g}}} = "
            rf"C_{{A0}}^{{{round(1 - n_disp, 4):g}}} - ({round(1 - n_disp, 4):g})kt"
        ),
        "transform_description": f"y = C_A^(1-n) = C_A^{round(1 - n_disp, 4):g}, x = t",
        "transform": lambda t, C, C0, n=n: nth_order_transform(t, C, C0, n),
        "predict": lambda t, C0, k, n=n: nth_order_predict(t, C0, k, n),
        "k_from_fit": lambda slope, intercept, n=n: nth_order_k_from_fit(slope, intercept, n),
        "slope_meaning": "slope = -(1-n)k",
        "intercept_meaning": "intercept = C_A0^(1-n)",
    }


FIXED_ORDER_MODELS = [ZERO_ORDER, FIRST_ORDER, SECOND_ORDER]
