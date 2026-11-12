import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(Path(__file__).parent.parent / "src"))

from prediction_validator import PredictionValidator

def test_confidence_below_90():
    res = PredictionValidator.validate_signal(
        confidence_score=89.9,
        efficiency_score=95.0,
        direction="BUY"
    )
    assert res["confidence_pass"] is False
    assert res["efficiency_pass"] is True
    assert res["confidence_gate"] == "Confidence Gate: FAIL (89.90 < 90)"
    assert res["efficiency_gate"] == "Efficiency Gate: PASS (95.00 >= 90)"
    assert res["can_trade"] is False
    assert res["action"] == "NO_TRADE"
    assert "Confidence Gate: FAIL (89.90 < 90)" in res["reasons"]

def test_confidence_exactly_90():
    res = PredictionValidator.validate_signal(
        confidence_score=90.0,
        efficiency_score=90.0,
        direction="BUY"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is True
    assert res["confidence_gate"] == "Confidence Gate: PASS (90.00 >= 90)"
    assert res["efficiency_gate"] == "Efficiency Gate: PASS (90.00 >= 90)"
    assert res["can_trade"] is True
    assert res["action"] == "BUY"

def test_confidence_above_90():
    res = PredictionValidator.validate_signal(
        confidence_score=92.5,
        efficiency_score=91.0,
        direction="SELL"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is True
    assert res["confidence_gate"] == "Confidence Gate: PASS (92.50 >= 90)"
    assert res["efficiency_gate"] == "Efficiency Gate: PASS (91.00 >= 90)"
    assert res["can_trade"] is True
    assert res["action"] == "SELL"

def test_efficiency_below_90():
    res = PredictionValidator.validate_signal(
        confidence_score=95.0,
        efficiency_score=89.99,
        direction="BUY"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is False
    assert res["confidence_gate"] == "Confidence Gate: PASS (95.00 >= 90)"
    assert res["efficiency_gate"] == "Efficiency Gate: FAIL (89.99 < 90)"
    assert res["can_trade"] is False
    assert res["action"] == "NO_TRADE"
    assert "Efficiency Gate: FAIL (89.99 < 90)" in res["reasons"]

def test_efficiency_exactly_90():
    res = PredictionValidator.validate_signal(
        confidence_score=90.0,
        efficiency_score=90.0,
        direction="SELL"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is True
    assert res["efficiency_gate"] == "Efficiency Gate: PASS (90.00 >= 90)"
    assert res["can_trade"] is True
    assert res["action"] == "SELL"

def test_efficiency_above_90():
    res = PredictionValidator.validate_signal(
        confidence_score=91.0,
        efficiency_score=94.8,
        direction="BUY"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is True
    assert res["efficiency_gate"] == "Efficiency Gate: PASS (94.80 >= 90)"
    assert res["can_trade"] is True
    assert res["action"] == "BUY"

def test_both_gates_passing():
    res = PredictionValidator.validate_signal(
        confidence_score=93.4,
        efficiency_score=96.2,
        direction="BUY"
    )
    assert res["confidence_pass"] is True
    assert res["efficiency_pass"] is True
    assert res["gates_passed"] is True
    assert res["can_trade"] is True
    assert res["action"] == "BUY"
    assert res["reason"] == "PASSED_ALL_GATES"

def test_either_gate_failing():
    # Case 1: Confidence fails, efficiency passes
    res1 = PredictionValidator.validate_signal(
        confidence_score=85.0,
        efficiency_score=95.0,
        direction="BUY"
    )
    assert res1["confidence_pass"] is False
    assert res1["efficiency_pass"] is True
    assert res1["can_trade"] is False
    assert res1["action"] == "NO_TRADE"

    # Case 2: Confidence passes, efficiency fails
    res2 = PredictionValidator.validate_signal(
        confidence_score=95.0,
        efficiency_score=85.0,
        direction="BUY"
    )
    assert res2["confidence_pass"] is True
    assert res2["efficiency_pass"] is False
    assert res2["can_trade"] is False
    assert res2["action"] == "NO_TRADE"

    # Case 3: Both fail
    res3 = PredictionValidator.validate_signal(
        confidence_score=85.0,
        efficiency_score=85.0,
        direction="BUY"
    )
    assert res3["confidence_pass"] is False
    assert res3["efficiency_pass"] is False
    assert res3["can_trade"] is False
    assert res3["action"] == "NO_TRADE"

    # Case 4: The exact scenario from prompt (Confidence 16.28, Efficiency 100.0)
    res4 = PredictionValidator.validate_signal(
        confidence_score=16.28,
        efficiency_score=100.0,
        direction="BUY"
    )
    assert res4["confidence_pass"] is False
    assert res4["efficiency_pass"] is True
    assert res4["confidence_gate"] == "Confidence Gate: FAIL (16.28 < 90)"
    assert res4["efficiency_gate"] == "Efficiency Gate: PASS (100.00 >= 90)"
    assert res4["can_trade"] is False
    assert res4["action"] == "NO_TRADE"
