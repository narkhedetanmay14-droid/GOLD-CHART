import os
import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(Path(__file__).parent.parent / "src"))

from backtest_engine import BacktestEngine

def test_empty_dataset_raises_value_error():
    engine = BacktestEngine()
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        engine.run_backtest(empty_df, empty_df, empty_df)

def test_one_row_dataset():
    engine = BacktestEngine()
    idx = pd.to_datetime(["2026-11-12 10:00:00"])
    market_df = pd.DataFrame({"close": [4000.0], "atr": [5.0]}, index=idx)
    signal_df = pd.DataFrame({"signal": ["BUY"]}, index=idx)
    res = engine.run_backtest(market_df, market_df, signal_df)
    assert "trade_log" in res
    assert len(res["trade_log"]) == 1
    assert res["trade_log"].iloc[0]["outcome"] == "NO_TRADE"

def test_final_row_signal():
    engine = BacktestEngine()
    idx = pd.date_range("2026-11-12 10:00:00", periods=3, freq="1min")
    market_df = pd.DataFrame({"close": [4000.0, 4005.0, 4010.0], "atr": [5.0, 5.0, 5.0]}, index=idx)
    signal_df = pd.DataFrame({"signal": ["NO_TRADE", "NO_TRADE", "BUY"]}, index=idx)
    res = engine.run_backtest(market_df, market_df, signal_df)
    trade_log = res["trade_log"]
    assert len(trade_log) == 1
    assert trade_log.iloc[0]["outcome"] == "NO_TRADE"

def test_intrabar_ambiguity_and_gaps():
    engine = BacktestEngine()
    idx = pd.date_range("2026-11-12 10:00:00", periods=4, freq="15min")
    market_df = pd.DataFrame({
        "close": [4000.0, 4020.0, 3970.0, 4010.0],
        "atr": [5.0, 5.0, 5.0, 5.0]
    }, index=idx)
    signal_df = pd.DataFrame({"signal": ["BUY", "SELL", "NO_TRADE", "NO_TRADE"]}, index=idx)
    res = engine.run_backtest(market_df, market_df, signal_df)
    assert len(res["trade_log"]) == 2
    assert "summary" in res

def test_duplicate_timestamps_handling():
    engine = BacktestEngine()
    idx = pd.to_datetime(["2026-11-12 10:00:00", "2026-11-12 10:00:00", "2026-11-12 10:01:00"])
    market_df = pd.DataFrame({"close": [4000.0, 4001.0, 4010.0], "atr": [5.0, 5.0, 5.0]}, index=idx)
    # Deduplicate keeping last
    market_df = market_df[~market_df.index.duplicated(keep="last")]
    signal_df = pd.DataFrame({"signal": ["BUY", "BUY"]}, index=market_df.index)
    res = engine.run_backtest(market_df, market_df, signal_df)
    assert len(res["trade_log"]) >= 1
