"""
Dimensional bookkeeping for the rate constant k.

For -r_A = k * C_A^n, dimensional analysis of
    [concentration]/[time] = k * [concentration]^n
gives:
    k -> [concentration]^(1-n) / [time]
"""
from __future__ import annotations


def k_units(n: float, concentration_unit: str, time_unit: str) -> str:
    if n is None:
        return "undefined"
    # Round for display purposes only -- does not affect any calculation.
    n_disp = round(n, 4)
    exponent = round(1 - n_disp, 4)

    if abs(exponent) < 1e-9:
        # n == 1 -> k has units of 1/time
        return f"{time_unit}^-1"
    if abs(exponent - 1) < 1e-9:
        return f"{concentration_unit}/{time_unit}"
    # General case
    exp_str = f"{exponent:g}"
    return f"({concentration_unit})^{exp_str}/{time_unit}"
