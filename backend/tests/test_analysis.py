import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.validation.validators import validate_data
from app.analysis.integral import run_integral_analysis
from app.analysis.differential import run_differential_analysis
from app.kinetics.autocatalytic import autocatalytic_predict

client = TestClient(app)

RNG = np.random.default_rng(42)


def make_data(n_func, C0, k, t_max=100, n_points=12, noise=0.0):
    t = np.linspace(0, t_max, n_points)
    C = n_func(t, C0, k)
    if noise > 0:
        C = C + RNG.normal(0, noise, size=C.shape)
        C = np.clip(C, 0.001, None)
    return t.tolist(), C.tolist()


def zero_order_curve(t, C0, k):
    return np.clip(C0 - k * t, 0, None)


def first_order_curve(t, C0, k):
    return C0 * np.exp(-k * t)


def second_order_curve(t, C0, k):
    return 1.0 / (1.0 / C0 + k * t)


def nth_order_curve(t, C0, k, n):
    one_minus_n = 1 - n
    base = C0 ** one_minus_n - one_minus_n * k * t
    return np.power(np.clip(base, 1e-6, None), 1 / one_minus_n)


# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------
def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# --------------------------------------------------------------------------
# Synthetic recovery tests
# --------------------------------------------------------------------------
def test_recovers_zero_order():
    t, C = make_data(zero_order_curve, C0=10, k=0.03, t_max=100, n_points=10)
    result = run_integral_analysis(t, C)
    best = result["best_model"]
    assert best["n"] == pytest.approx(0.0, abs=1e-6)
    assert best["k"] == pytest.approx(0.03, rel=0.05)
    assert best["r_squared"] > 0.999


def test_recovers_first_order():
    t, C = make_data(first_order_curve, C0=10, k=0.02, t_max=150, n_points=12)
    result = run_integral_analysis(t, C)
    best = result["best_model"]
    assert best["n"] == pytest.approx(1.0, abs=1e-6)
    assert best["k"] == pytest.approx(0.02, rel=0.05)
    assert best["r_squared"] > 0.999


def test_recovers_second_order():
    t, C = make_data(second_order_curve, C0=10, k=0.01, t_max=150, n_points=12)
    result = run_integral_analysis(t, C)
    best = result["best_model"]
    assert best["n"] == pytest.approx(2.0, abs=1e-6)
    assert best["k"] == pytest.approx(0.01, rel=0.05)


def test_recovers_fractional_order_half():
    t, C = make_data(lambda t, C0, k: nth_order_curve(t, C0, k, 0.5), C0=10, k=0.05, t_max=150, n_points=14)
    result = run_integral_analysis(t, C, n_min=-2, n_max=5)
    best = result["best_model"]
    assert best["n"] == pytest.approx(0.5, abs=0.15)


def test_recovers_fractional_order_1_5():
    t, C = make_data(lambda t, C0, k: nth_order_curve(t, C0, k, 1.5), C0=10, k=0.01, t_max=150, n_points=14)
    result = run_integral_analysis(t, C, n_min=-2, n_max=5)
    best = result["best_model"]
    assert best["n"] == pytest.approx(1.5, abs=0.2)


def test_differential_method_recovers_first_order():
    t, C = make_data(first_order_curve, C0=10, k=0.02, t_max=150, n_points=15)
    result = run_differential_analysis(t, C, smoothing_strength=0.1)
    assert result["valid"]
    nth = result["best_model"]
    assert nth["n"] == pytest.approx(1.0, abs=0.25)


def test_autocatalytic_predict_matches_initial_condition():
    c0 = autocatalytic_predict(np.array([0.0]), C0_a=10.0, C0_r=1.0, k=0.001)
    assert c0[0] == pytest.approx(10.0)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_validation_rejects_negative_time():
    result = validate_data([-1, 0, 5], [10, 9, 8])
    assert not result["valid"]
    assert any("negative time" in e.lower() for e in result["errors"])


def test_validation_rejects_negative_concentration():
    result = validate_data([0, 5, 10], [10, -1, 5])
    assert not result["valid"]
    assert any("negative concentration" in e.lower() for e in result["errors"])


def test_validation_flags_duplicate_time():
    result = validate_data([0, 5, 5, 10], [10, 8, 8, 5])
    assert result["valid"]
    assert any("duplicate" in w.lower() for w in result["warnings"])


def test_validation_flags_non_monotonic_as_warning_not_error():
    result = validate_data([0, 20, 40, 60], [10, 8, 6, 6.5])
    assert result["valid"]
    assert any("increases" in w.lower() for w in result["warnings"])


def test_validation_rejects_insufficient_points():
    result = validate_data([0, 5], [10, 8])
    assert not result["valid"]


def test_validation_rejects_nan():
    result = validate_data([0, 5, float("nan")], [10, 8, 5])
    assert not result["valid"]


# --------------------------------------------------------------------------
# API-level tests
# --------------------------------------------------------------------------
def test_api_analyze_first_order():
    t, C = make_data(first_order_curve, C0=10, k=0.02, t_max=150, n_points=12)
    payload = {
        "data": [{"time": ti, "concentration": ci} for ti, ci in zip(t, C)],
        "concentration_unit": "mol/L",
        "time_unit": "s",
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["integral"]["best_model"]["n"] == pytest.approx(1.0, abs=1e-4)
    assert body["comparison"]["conclusion"].startswith("Best overall kinetic model")


def test_api_analyze_rejects_negative_time():
    payload = {
        "data": [
            {"time": -1, "concentration": 10},
            {"time": 5, "concentration": 8},
            {"time": 10, "concentration": 6},
        ],
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 422


def test_api_analyze_autocatalytic_zero_CR0_warns():
    t = [0, 10, 20, 30, 40]
    C = [10, 9.5, 9.0, 8.6, 8.3]
    payload = {
        "data": [{"time": ti, "concentration": ci} for ti, ci in zip(t, C)],
        "autocatalytic_C_R0": 0,
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["autocatalytic"]["applicable"] is False
    assert "C_R0 = 0" in body["autocatalytic"]["reason"]
