"""
Transparent model-selection logic (Part 11 / Part 39 of the spec).

Rather than "highest R2 wins", the final recommendation considers:
  1. Physical validity (k >= 0)
  2. Transformed-data linearity (R^2)
  3. Original-domain prediction error (RMSE)
  4. Agreement between the integral and differential estimates of n

This module does not use machine learning; it is a small, fully
explainable rule set operating on numbers already computed by the
integral and differential analyses.
"""
from __future__ import annotations


CONSISTENCY_THRESHOLD_N = 0.3  # |n_integral - n_differential| below this => "consistent"
GOOD_R2_THRESHOLD = 0.95


def compare_methods(integral_result: dict, differential_result: dict) -> dict:
    best_integral = integral_result.get("best_model") or {}
    n_int = best_integral.get("n")
    k_int = best_integral.get("k")
    r2_int = best_integral.get("r_squared")
    rmse_int = best_integral.get("original_domain_rmse")

    diff_best = differential_result.get("best_model") if differential_result.get("valid") else None
    n_diff = diff_best.get("n") if diff_best else None
    k_diff = diff_best.get("k") if diff_best else None
    r2_diff = diff_best.get("r_squared") if diff_best else None

    agreement = None
    delta_n = None
    if n_int is not None and n_diff is not None:
        delta_n = abs(n_int - n_diff)
        agreement = delta_n <= CONSISTENCY_THRESHOLD_N

    reasons = []
    if r2_int is not None:
        reasons.append(
            f"Integral method: transformed-plot R\u00b2 = {r2_int:.4f} for order n = {n_int:.3g}."
        )
    if r2_diff is not None:
        reasons.append(
            f"Differential method: ln(-r_A) vs ln(C_A) gives n = {n_diff:.3g} with R\u00b2 = {r2_diff:.4f}."
        )
    if agreement is True:
        reasons.append(
            f"The two methods agree closely (\u0394n = {delta_n:.3g} \u2264 {CONSISTENCY_THRESHOLD_N}), "
            "which increases confidence in the selected kinetic order."
        )
    elif agreement is False:
        reasons.append(
            f"The two methods disagree (\u0394n = {delta_n:.3g} > {CONSISTENCY_THRESHOLD_N}). "
            "Possible causes: experimental noise amplified by differentiation, sparse data, "
            "a narrow concentration range, outliers, or smoothing sensitivity. "
            "The integral-method result is generally weighted more heavily because it does "
            "not require numerical differentiation of noisy data."
        )

    if k_int is not None and k_int < 0:
        reasons.append(
            "Integral-method k is negative, which is not physically meaningful; this model "
            "is de-prioritized in favor of the next best physically valid candidate."
        )

    quality_int = "high" if (r2_int or 0) >= GOOD_R2_THRESHOLD else "moderate" if (r2_int or 0) >= 0.8 else "low"
    quality_diff = None
    if r2_diff is not None:
        quality_diff = "high" if r2_diff >= GOOD_R2_THRESHOLD else "moderate" if r2_diff >= 0.8 else "low"

    final_model_name = best_integral.get("name", "unknown")
    final_n = n_int
    final_k = k_int

    return {
        "integral": {
            "n": n_int, "k": k_int, "r_squared": r2_int, "rmse": rmse_int,
            "rate_law_latex": best_integral.get("rate_law_latex"),
            "quality": quality_int,
        },
        "differential": {
            "n": n_diff, "k": k_diff, "r_squared": r2_diff,
            "rate_law_latex": diff_best.get("rate_law_latex") if diff_best else None,
            "quality": quality_diff,
        },
        "delta_n": delta_n,
        "methods_agree": agreement,
        "reasons": reasons,
        "final_model_name": final_model_name,
        "final_n": final_n,
        "final_k": final_k,
        "conclusion": (
            f"Best overall kinetic model: {final_model_name}"
            + (f" (n = {final_n:.3g})" if final_n is not None else "")
        ),
    }
