import pytest
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(Path(__file__).parent.parent / "src"))

from backtest_engine import BacktestEngine
from execution_simulator import ExecutionSimulator
from calibration_engine import CalibrationEngine
from confidence_engine import ConfidenceEngine
from efficiency_engine import EfficiencyEngine
from limit_entry_engine import LimitEntryEngine
from prediction_validator import PredictionValidator
from walk_forward_engine import WalkForwardEngine

def test_execution_simulator_costs():
    sim = ExecutionSimulator(spread=0.20, slippage=0.05, commission=0.02)
    entry = sim.simulate_entry(price=4000.0, direction="BUY")
    assert entry["filled"] is True
    # BUY enters at 4000 + 0.10 + 0.05 = 4000.15
    assert np.isclose(entry["fill_price"], 4000.15)

    exit_price = sim.simulate_exit(price=4020.0, direction="BUY")
    # BUY exits at 4020 - 0.10 - 0.05 - 0.02 = 4019.83
    assert np.isclose(exit_price, 4019.83)

def test_intrabar_ambiguity_conservative():
    sim = ExecutionSimulator()
    # If both target (4020) and stop (3990) are within candle low (3985) and high (4025)
    outcome = sim.resolve_intrabar(high=4025.0, low=3985.0, stop=3990.0, target=4020.0, direction="BUY")
    assert outcome == "AMBIGUOUS_LOSS"

def test_calibration_engine():
    cal = CalibrationEngine(method="sigmoid")
    # Synthetic probabilities and labels
    raw_probs = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 0.9])
    y_true = np.array([0, 0, 0, 1, 1, 1])
    cal.fit(raw_probs, y_true)
    calibrated = cal.predict_proba(raw_probs)
    assert len(calibrated) == len(raw_probs)
    assert np.all(calibrated >= 0.0) and np.all(calibrated <= 1.0)
    ece = CalibrationEngine.expected_calibration_error(y_true, calibrated)
    assert 0.0 <= ece <= 1.0

def test_confidence_and_efficiency_gates():
    conf_eng = ConfidenceEngine()
    eff_eng = EfficiencyEngine()

    assert conf_eng.evaluate_gate(92.0, threshold=90.0) is True
    assert conf_eng.evaluate_gate(88.0, threshold=90.0) is False

    assert eff_eng.evaluate_gate(95.0, threshold=90.0) is True
    assert eff_eng.evaluate_gate(89.9, threshold=90.0) is False

def test_prediction_validator_90_90():
    # Pass case
    res_pass = PredictionValidator.validate_signal(confidence_score=92.0, efficiency_score=94.0, direction="BUY")
    assert res_pass["can_trade"] is True
    assert res_pass["action"] == "BUY"

    # Fail cases: one score below 90
    res_fail1 = PredictionValidator.validate_signal(confidence_score=89.5, efficiency_score=95.0, direction="BUY")
    assert res_fail1["can_trade"] is False
    assert res_fail1["action"] == "NO_TRADE"

    res_fail2 = PredictionValidator.validate_signal(confidence_score=95.0, efficiency_score=85.0, direction="SELL")
    assert res_fail2["can_trade"] is False
    assert res_fail2["action"] == "NO_TRADE"

def test_limit_entry_engine():
    limit_buy = LimitEntryEngine.calculate_limit_price(current_price=4000.0, atr=5.0, direction="BUY", pullback_pct=0.4)
    # BUY limit should be below current price
    assert limit_buy < 4000.0
    assert limit_buy == 3998.0

    limit_sell = LimitEntryEngine.calculate_limit_price(current_price=4000.0, atr=5.0, direction="SELL", pullback_pct=0.4)
    # SELL limit should be above current price
    assert limit_sell > 4000.0
    assert limit_sell == 4002.0

def test_walk_forward_engine():
    df = pd.DataFrame({"close": range(200)})
    wfe = WalkForwardEngine(train_window=50, test_window=20, expanding=False)
    folds = wfe.generate_folds(df)
    assert len(folds) > 0
    train_fold, test_fold = folds[0]
    assert len(train_fold) == 50
    assert len(test_fold) == 20
