import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CandleBuilder:
    """Builds and resamples OHLC candles from tick data or 1-minute bars."""

    TIMEFRAME_MAP = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1D"
    }

    @classmethod
    def resample(cls, df: pd.DataFrame, timeframe: str = "5m") -> pd.DataFrame:
        """Resample candles to target timeframe.
        df must have 'timestamp' and OHLC columns.
        """
        if df.empty or "timestamp" not in df.columns:
            return pd.DataFrame()

        freq = cls.TIMEFRAME_MAP.get(timeframe.lower(), timeframe)
        df_work = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_work["timestamp"]):
            df_work["timestamp"] = pd.to_datetime(df_work["timestamp"], utc=True)

        df_work = df_work.set_index("timestamp").sort_index()

        agg_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last"
        }
        if "volume" in df_work.columns:
            agg_dict["volume"] = "sum"
        if "tickVolume" in df_work.columns:
            agg_dict["tickVolume"] = "sum"
        if "spread" in df_work.columns:
            agg_dict["spread"] = "mean"

        resampled = df_work.resample(freq).agg(agg_dict).dropna(subset=["open", "close"]).reset_index()
        return resampled

    @classmethod
    def from_ticks(cls, ticks_df: pd.DataFrame, timeframe: str = "1m") -> pd.DataFrame:
        """Construct OHLC candles from raw tick records."""
        if ticks_df.empty or "timestamp" not in ticks_df.columns:
            return pd.DataFrame()

        df_work = ticks_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_work["timestamp"]):
            df_work["timestamp"] = pd.to_datetime(df_work["timestamp"], utc=True)

        price_col = "mid" if "mid" in df_work.columns else "bid"
        df_work = df_work.set_index("timestamp").sort_index()

        freq = cls.TIMEFRAME_MAP.get(timeframe.lower(), timeframe)
        resampled = df_work[price_col].resample(freq).ohlc().dropna().reset_index()

        if "spread" in df_work.columns:
            spread_mean = df_work["spread"].resample(freq).mean().dropna().reset_index(drop=True)
            resampled["spread"] = spread_mean

        resampled["volume"] = df_work[price_col].resample(freq).count().dropna().values
        return resampled
