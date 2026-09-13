"""
Simple autocatalytic reaction:  A + R -> R + R

Rate law:      -r_A = k C_A C_R
Constant volume, mass balance:   C_A + C_R = C_A0 + C_R0 = C0

Substituting C_R = C0 - C_A:
    -dC_A/dt = k C_A (C0 - C_A)

Partial fractions on 1/[C_A(C0-C_A)] and integrating from (C_A0, 0) to (C_A, t)
gives the classical result:

    ln[ C_A0 (C0 - C_A) / (C_A (C0 - C_A0)) ] = C0 k t

Linear form:  y = C0 * k * t  (a straight line through the origin in t),
so we regress y = ln[...] against x = t; slope = C0 * k  =>  k = slope / C0.
"""
from __future__ import annotations

import numpy as np


def autocatalytic_transform(t, C, C0_a, C0_r):
    """
    Returns (x, y) for the autocatalytic linear plot, using only points
    where the log argument is mathematically valid (C_A in (0, C0)) .
    """
    C = np.asarray(C, dtype=float)
    t = np.asarray(t, dtype=float)
    C0 = C0_a + C0_r

    valid = (C > 0) & (C < C0)
    C_valid = C[valid]
    t_valid = t[valid]

    numerator = C0_a * (C0 - C_valid)
    denominator = C_valid * (C0 - C0_a)
    with np.errstate(divide="ignore", invalid="ignore"):
        y = np.log(numerator / denominator)

    finite = np.isfinite(y)
    return t_valid[finite], y[finite], C0


def autocatalytic_predict(t, C0_a, C0_r, k):
    """Analytical solution for C_A(t) of the autocatalytic model."""
    t = np.asarray(t, dtype=float)
    C0 = C0_a + C0_r
    if C0_r <= 0:
        # Cannot initiate: no product/catalyst present at t = 0.
        return np.full_like(t, np.nan)
    # From ln[C0_a(C0-C_A)/(C_A(C0-C0_a))] = C0 k t, solve for C_A:
    # Let R = exp(C0 k t). Then C0_a(C0-C_A) = R * C_A * (C0-C0_a)
    # => C0_a*C0 - C0_a*C_A = R*(C0-C0_a)*C_A
    # => C_A [R*(C0-C0_a) + C0_a] = C0_a*C0
    R = np.exp(C0 * k * t)
    denom = R * (C0 - C0_a) + C0_a
    with np.errstate(divide="ignore", invalid="ignore"):
        c = (C0_a * C0) / denom
    return c


def autocatalytic_k_from_slope(slope, C0):
    if C0 == 0:
        return None
    return slope / C0
