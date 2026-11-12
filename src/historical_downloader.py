import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from config_loader import ConfigLoader
from biquote_client import BiQuoteClient

logger = logging.getLogger(__name__)

class HistoricalDownloader:
    """Downloads and archives historical XAU/USD data from BiQuote."""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
        self.biquote_cfg = self.config_loader.get_biquote_config()
        self.client = BiQuoteClient(
            base_url=self.biquote_cfg.get("api", {}).get("base_url"),
            timeout=self.biquote_cfg.get("api", {}).get("timeout", 30),
            retry_count=self.biquote_cfg.get("api", {}).get("retry_count", 3)
        )
        self.symbol = self.biquote_cfg.get("symbol", "XAU/USD")
        self.timeframes = self.biquote_cfg.get("supported_timeframes", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])

        self.raw_candles_dir = self.config_loader.resolve_path("data/raw/historical_candles")
        self.raw_ticks_dir = self.config_loader.resolve_path("data/raw/historical_ticks")
        self.metadata_dir = self.config_loader.resolve_path("data/metadata")

        for d in [self.raw_candles_dir, self.raw_ticks_dir, self.metadata_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def download_candles(self, interval: str = "1h", limit: int = 2000) -> pd.DataFrame:
        logger.info("Downloading %s candles for %s (limit=%d)...", interval, self.symbol, limit)
        df = self.client.get_ohlc(symbol=self.symbol, interval=interval, limit=limit)
        if not df.empty:
            out_path = self.raw_candles_dir / f"candles_{interval}.parquet"
            df.to_parquet(out_path, index=False)
            logger.info("Saved %d %s candles to %s", len(df), interval, out_path)
        return df

    def download_ticks(self, count: int = 1000) -> pd.DataFrame:
        logger.info("Downloading historical ticks for %s (count=%d)...", self.symbol, count)
        df = self.client.get_tick_history(symbol=self.symbol, count=count)
        if not df.empty:
            out_path = self.raw_ticks_dir / "ticks_history.parquet"
            df.to_parquet(out_path, index=False)
            logger.info("Saved %d ticks to %s", len(df), out_path)
        return df

    def download_all(self) -> Dict[str, Any]:
        report = {}
        # Download ticks
        try:
            ticks_df = self.download_ticks(count=1000)
            report["ticks"] = {
                "count": len(ticks_df),
                "earliest": str(ticks_df["timestamp"].min()) if not ticks_df.empty else None,
                "latest": str(ticks_df["timestamp"].max()) if not ticks_df.empty else None,
            }
        except Exception as e:
            logger.error("Failed to download ticks: %s", e)
            report["ticks"] = {"error": str(e)}

        # Download candles for each timeframe
        candles_report = {}
        for tf in self.timeframes:
            try:
                cdf = self.download_candles(interval=tf, limit=2000)
                candles_report[tf] = {
                    "count": len(cdf),
                    "earliest": str(cdf["timestamp"].min()) if not cdf.empty else None,
                    "latest": str(cdf["timestamp"].max()) if not cdf.empty else None,
                }
            except Exception as e:
                logger.error("Failed to download candles for %s: %s", tf, e)
                candles_report[tf] = {"error": str(e)}
        report["candles"] = candles_report

        # Save metadata report
        meta_path = self.metadata_dir / "data_availability.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Data availability report saved to %s", meta_path)
        return report
