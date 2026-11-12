import pytest
import os
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, os.path.abspath(Path(__file__).parent.parent / "src"))

from data_processor import DataProcessor
from config_loader import ConfigLoader

def test_clean_pipeline_runs():
    processor = DataProcessor()
    summary = processor.clean_pipeline()
    # Expect both candle and tick reports present
    assert "candles" in summary
    assert "ticks" in summary
    # At least some rows cleaned
    assert summary["candle_rows"] > 0
    assert summary["tick_rows"] > 0
    # Issues should be recorded but not fatal
    assert isinstance(summary["candles"], dict)
    assert isinstance(summary["ticks"], dict)
