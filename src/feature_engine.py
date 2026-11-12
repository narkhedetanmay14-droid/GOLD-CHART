import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd

from config_loader import ConfigLoader
from indicators import TechnicalIndicators
from market_structure import MarketStructureEngine

logger = logging.getLogger(__name__)

class FeatureEngine:
    """Combines cleaned candles, technical indicators, and market structure into a unified feature set."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
        self.processed_dir = self.config_loader.resolve_path("data/processed")
        self.features_dir = self.config_loader.resolve_path("data/features")
        self.metadata_dir = self.config_loader.resolve_path("data/metadata")
        self.quality_dir = self.config_loader.resolve_path("data/quality_reports")

        for d in [self.features_dir, self.metadata_dir, self.quality_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def build_feature_dataset(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        candles_path = self.processed_dir / "clean_candles.parquet"
        if not candles_path.exists():
            logger.error("Clean candles not found at %s. Run cleaning first.", candles_path)
            return pd.DataFrame(), {}

        df = pd.read_parquet(candles_path)
        if df.empty:
            return df, {}

        # 1. Technical Indicators
        df = TechnicalIndicators.compute_all(df)

        # 2. Market Structure
        df = MarketStructureEngine.compute_all(df)

        # 3. Price Action Features
        df["body_size"] = (df["close"] - df["open"]).abs()
        df["candle_range"] = df["high"] - df["low"]
        df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)
        df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]
        df["body_ratio"] = df["body_size"] / (df["candle_range"] + 1e-10)

        # Drop NaN warmup rows
        df = df.dropna().reset_index(drop=True)

        # Save feature dataset
        out_parquet = self.features_dir / "xauusd_features.parquet"
        df.to_parquet(out_parquet, index=False)
        logger.info("Saved %d rows of features to %s", len(df), out_parquet)

        # Build Feature Dictionary
        feature_dict = {}
        for col in df.columns:
            feature_dict[col] = {
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "inference_safe": True,
                "description": f"Feature {col} computed for XAU/USD"
            }

        dict_path = self.metadata_dir / "feature_dictionary.json"
        with open(dict_path, "w", encoding="utf-8") as f:
            json.dump(feature_dict, f, indent=2)

        # Feature Report
        report = {
            "total_features": len(df.columns),
            "total_rows": len(df),
            "features": list(df.columns)
        }
        report_path = self.quality_dir / "feature_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return df, feature_dict
