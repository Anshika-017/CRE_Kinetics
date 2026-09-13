"""
Smoothing + derivative estimation used ONLY for the differential method.

The integral method always uses raw experimental data directly (see
analysis/integral.py). The differential method needs dC_A/dt, and a naive
finite difference on noisy data is unstable, so a smoothing spline is fit
to C_A(t) first and differentiated analytically.

Method: scipy.interpolate.UnivariateSpline (a cubic smoothing spline).
The smoothing factor `s` controls how tightly the spline follows the raw
points; it is exposed to the frontend as a user-adjustable "smoothing
strength" so nothing is hidden.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import UnivariateSpline


def fit_smooth_curve(t: np.ndarray, c: np.ndarray, smoothing_strength: float = 0.5):
    """
    smoothing_strength in [0, 1]:
        0   -> near-interpolating spline (s close to 0)
        1   -> heavily smoothed spline (large s)

    Returns (spline, s_used, method_description).
    """
    t = np.asarray(t, dtype=float)
    c = np.asarray(c, dtype=float)

    order = np.argsort(t, kind="stable")
    t_sorted, c_sorted = t[order], c[order]

    # Deduplicate time values (average concentration) -- required by
    # UnivariateSpline, which needs strictly increasing x.
    unique_t, inverse = np.unique(t_sorted, return_inverse=True)
    if len(unique_t) != len(t_sorted):
        c_avg = np.zeros_like(unique_t)
        counts = np.zeros_like(unique_t)
        for idx, ci in zip(inverse, c_sorted):
            c_avg[idx] += ci
            counts[idx] += 1
        c_unique = c_avg / counts
    else:
        c_unique = c_sorted

    n = len(unique_t)
    k = 3 if n > 3 else max(1, n - 1)

    # Map smoothing_strength [0,1] to a smoothing factor `s`.
    # s=0 => interpolation; larger s => more smoothing.
    residual_scale = np.var(c_unique) * n if n > 0 else 1.0
    s = smoothing_strength * residual_scale

    spline = UnivariateSpline(unique_t, c_unique, k=k, s=s)

    return spline, float(s), (
        "A cubic smoothing spline (scipy.UnivariateSpline) is fit to the "
        "experimental C_A(t) data. The derivative dC_A/dt is evaluated "
        "analytically from this spline, not from raw finite differences, "
        "to reduce noise amplification."
    )


def evaluate_derivative(spline, t_eval: np.ndarray):
    t_eval = np.asarray(t_eval, dtype=float)
    c_smooth = spline(t_eval)
    dcdt = spline.derivative()(t_eval)
    return c_smooth, dcdt
