import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd

from config_loader import ConfigLoader
from data_validator import DataValidator

logger = logging.getLogger(__name__)

class DataProcessor:
    """High-level pipeline: load raw data, validate, normalize timestamps, deduplicate, and save cleaned data."""

    def __init__(self, config_loader: ConfigLoader = None):
        self.config_loader = config_loader or ConfigLoader()
        self.raw_candles_dir = self.config_loader.resolve_path("data/raw/historical_candles")
        self.raw_ticks_dir = self.config_loader.resolve_path("data/raw/historical_ticks")
        self.processed_dir = self.config_loader.resolve_path("data/processed")
        self.quality_dir = self.config_loader.resolve_path("data/quality_reports")
        for d in [self.processed_dir, self.quality_dir]:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _ensure_utc(df: pd.DataFrame) -> pd.DataFrame:
        if "timestamp" in df.columns:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            else:
                # If already datetime, localize/convert to UTC
                try:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                except Exception:
                    pass
        return df.sort_values("timestamp").reset_index(drop=True)

    def process_candles(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        all_files = list(self.raw_candles_dir.glob("*.parquet"))
        if not all_files:
            logger.error("No raw candle files found in %s", self.raw_candles_dir)
            return pd.DataFrame(), {}
        dfs = [pd.read_parquet(p) for p in all_files]
        df = pd.concat(dfs, ignore_index=True)
        df = self._ensure_utc(df)
        df, report = DataValidator.validate_candles(df)
        out_path = self.processed_dir / "clean_candles.parquet"
        df.to_parquet(out_path, index=False)
        report_path = self.quality_dir / "cleaning_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            import json
            json.dump(report, f, indent=2)
        logger.info("Clean candles saved to %s", out_path)
        return df, report

    def process_ticks(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        all_files = list(self.raw_ticks_dir.glob("*.parquet"))
        if not all_files:
            logger.error("No raw tick files found in %s", self.raw_ticks_dir)
            return pd.DataFrame(), {}
        dfs = [pd.read_parquet(p) for p in all_files]
        df = pd.concat(dfs, ignore_index=True)
        df = self._ensure_utc(df)
        df, report = DataValidator.validate_ticks(df)
        out_path = self.processed_dir / "clean_ticks.parquet"
        df.to_parquet(out_path, index=False)
        report_path = self.quality_dir / "cleaning_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            import json
            json.dump(report, f, indent=2)
        logger.info("Clean ticks saved to %s", out_path)
        return df, report

    def clean_pipeline(self) -> Dict[str, Any]:
        candle_df, candle_report = self.process_candles()
        tick_df, tick_report = self.process_ticks()
        summary = {
            "candles": candle_report,
            "ticks": tick_report,
            "candle_rows": len(candle_df),
            "tick_rows": len(tick_df)
        }
        return summary
