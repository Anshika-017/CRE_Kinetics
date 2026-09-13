"""
Strict validation of experimental (t, C_A) data.

Errors  -> analysis cannot proceed at all (e.g. negative time).
Warnings -> analysis proceeds, but the user is told about a data-quality
            concern (e.g. slight non-monotonicity, sparse data).

Nothing here silently modifies the user's raw data. Sorting and dedup
decisions are surfaced as explicit warnings, not hidden mutations.
"""
from __future__ import annotations

import math
from typing import List

import numpy as np


def validate_data(times: List[float], concentrations: List[float]) -> dict:
    errors: List[str] = []
    warnings: List[str] = []

    n = len(times)
    if n != len(concentrations):
        errors.append("Time and concentration arrays have different lengths.")
        return {"valid": False, "errors": errors, "warnings": warnings, "n_points": n}

    if n < 3:
        errors.append(
            f"At least 3 data points are required; only {n} were provided."
        )

    for i, (t, c) in enumerate(zip(times, concentrations)):
        if t is None or c is None:
            errors.append(f"Row {i + 1}: empty cell.")
            continue
        if not (isinstance(t, (int, float)) and isinstance(c, (int, float))):
            errors.append(f"Row {i + 1}: non-numeric value.")
            continue
        if isinstance(t, float) and (math.isnan(t) or math.isinf(t)):
            errors.append(f"Row {i + 1}: time is NaN or infinite.")
        if isinstance(c, float) and (math.isnan(c) or math.isinf(c)):
            errors.append(f"Row {i + 1}: concentration is NaN or infinite.")
        if isinstance(t, (int, float)) and t < 0:
            errors.append(f"Row {i + 1}: negative time (t = {t}).")
        if isinstance(c, (int, float)) and c < 0:
            errors.append(f"Row {i + 1}: negative concentration (C_A = {c}).")

    if errors:
        # Don't try to run duplicate/monotonicity checks on broken data.
        return {"valid": False, "errors": errors, "warnings": warnings, "n_points": n}

    t_arr = np.asarray(times, dtype=float)
    c_arr = np.asarray(concentrations, dtype=float)

    # Duplicate time values
    unique_t, counts = np.unique(t_arr, return_counts=True)
    if np.any(counts > 1):
        dup_values = ", ".join(f"{v:g}" for v in unique_t[counts > 1])
        warnings.append(
            f"Duplicate time value(s) found (t = {dup_values}). "
            "These points are kept as separate observations; consider "
            "averaging replicate measurements before analysis."
        )

    # Unsorted time data
    if not np.all(np.diff(t_arr) >= 0):
        warnings.append(
            "Time values are not sorted in ascending order. The analysis "
            "sorts a working copy by time for regression and derivative "
            "estimation, but your original entered order is preserved for display."
        )

    # Zero concentration -> logarithmic transforms (first order, nth order,
    # differential ln-ln plot) cannot use these points.
    n_zero = int(np.sum(c_arr == 0))
    if n_zero > 0:
        warnings.append(
            f"{n_zero} point(s) have C_A = 0. These points are excluded from any "
            "logarithmic transformation (first-order, nth-order, and the "
            "differential ln(-r_A) vs ln(C_A) plot) because ln(0) is undefined."
        )

    # Non-monotonic concentration (sorted order)
    order = np.argsort(t_arr, kind="stable")
    c_sorted = c_arr[order]
    t_sorted = t_arr[order]
    increases = np.where(np.diff(c_sorted) > 0)[0]
    if len(increases) > 0:
        first = increases[0]
        warnings.append(
            f"Warning: concentration increases between t = {t_sorted[first]:g} and "
            f"t = {t_sorted[first + 1]:g}. This may indicate experimental noise or "
            "measurement error. Analysis continues, but treat the fitted model with "
            "appropriate caution in this region."
        )

    if n_points_effective_low(n):
        warnings.append(
            "Fewer than 6 points were supplied. Regression and especially the "
            "differential (derivative-based) method become increasingly unreliable "
            "with sparse data."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "n_points": n,
    }


def n_points_effective_low(n: int) -> bool:
    return n < 6
