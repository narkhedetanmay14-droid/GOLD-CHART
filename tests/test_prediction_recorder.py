import os
import json
import sqlite3
import pytest
from datetime import datetime, timezone, timedelta
from prediction_recorder import PredictionRecorder

def test_prediction_recorder_sqlite_and_json(tmp_path):
    recorder = PredictionRecorder(data_dir=str(tmp_path))
    utc_now = datetime.now(timezone.utc)
    record = {
        "prediction_id": "TEST-PRED-001",
        "utc_timestamp": utc_now.isoformat(),
        "local_timestamp": "2026-11-12 16:00:00 UTC",
        "symbol": "XAUUSD",
        "current_price": 2915.50,
        "bid": 2915.40,
        "ask": 2915.60,
        "spread": 0.20,
        "market_regime": "TRENDING",
        "market_structure": "BULLISH",
        "direction": "NO_TRADE",
        "confidence": 18.5,
        "efficiency": 85.0,
        "limit_entry_price": 2914.80,
        "touch_probability": 0.52,
        "expected_time_to_touch_sec": 120.0,
        "stop_loss": 2910.00,
        "take_profit": 2924.40,
        "risk_reward": "1:2.0",
        "final_decision": "NO_TRADE",
        "validation_status": "REJECTED",
        "rejection_reasons": ["FAILED_90_90_GATES"],
        "signal_expiry_utc": (utc_now + timedelta(seconds=180)).isoformat(),
        "model_version": "v1.0-validated",
        "data_source": "BiQuote SignalR",
        "features": {"atr_14": 2.0}
    }

    recorder.record_prediction(record)

    # 1. Verify SQLite
    recent = recorder.get_recent_predictions(limit=5)
    assert len(recent) == 1
    assert recent[0]["prediction_id"] == "TEST-PRED-001"
    assert recent[0]["bid"] == 2915.40
    assert recent[0]["final_decision"] == "NO_TRADE"

    # 2. Verify JSON history
    json_path = tmp_path / "prediction_history.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["prediction_id"] == "TEST-PRED-001"
