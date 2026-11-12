import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates OHLC candle and tick integrity."""

    @staticmethod
    def validate_candles(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Validate OHLC relationships, positive prices, and missing timestamps."""
        if df.empty:
            return df, {"status": "empty", "issues": 0}

        issues = {
            "negative_prices": 0,
            "invalid_high_low": 0,
            "invalid_open_close": 0,
            "duplicates": 0,
            "missing_timestamps": 0
        }

        # Check duplicates on timestamp
        if "timestamp" in df.columns:
            dups = df.duplicated(subset=["timestamp"], keep="first").sum()
            issues["duplicates"] = int(dups)
            df = df.drop_duplicates(subset=["timestamp"], keep="first").sort_values("timestamp").reset_index(drop=True)

        # Check price columns > 0
        price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
        if price_cols:
            neg_mask = (df[price_cols] <= 0).any(axis=1)
            issues["negative_prices"] = int(neg_mask.sum())
            if issues["negative_prices"] > 0:
                logger.warning("Found %d rows with non-positive prices", issues["negative_prices"])

            # High >= Low
            if "high" in df.columns and "low" in df.columns:
                hl_mask = df["high"] < df["low"]
                issues["invalid_high_low"] = int(hl_mask.sum())
                if issues["invalid_high_low"] > 0:
                    logger.warning("Found %d rows where High < Low", issues["invalid_high_low"])

            # High >= max(Open, Close) and Low <= min(Open, Close)
            if all(c in df.columns for c in ["open", "high", "low", "close"]):
                oc_mask = (df["high"] < df[["open", "close"]].max(axis=1)) | (df["low"] > df[["open", "close"]].min(axis=1))
                issues["invalid_open_close"] = int(oc_mask.sum())
                if issues["invalid_open_close"] > 0:
                    logger.warning("Found %d rows where High/Low do not encompass Open/Close", issues["invalid_open_close"])

        total_issues = sum(issues.values())
        report = {
            "status": "passed_with_warnings" if total_issues > 0 else "passed",
            "total_rows": len(df),
            "issues": issues
        }
        return df, report

    @staticmethod
    def validate_ticks(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Validate bid/ask consistency in ticks."""
        if df.empty:
            return df, {"status": "empty", "issues": 0}

        issues = {"invalid_spread": 0, "duplicates": 0}
        if "timestamp" in df.columns:
            dups = df.duplicated(subset=["timestamp"], keep="first").sum()
            issues["duplicates"] = int(dups)
            df = df.drop_duplicates(subset=["timestamp"], keep="first").sort_values("timestamp").reset_index(drop=True)

        if "bid" in df.columns and "ask" in df.columns:
            spread_mask = df["ask"] < df["bid"]
            issues["invalid_spread"] = int(spread_mask.sum())
            if issues["invalid_spread"] > 0:
                logger.warning("Found %d ticks where Ask < Bid", issues["invalid_spread"])

        report = {
            "status": "passed",
            "total_ticks": len(df),
            "issues": issues
        }
        return df, report
