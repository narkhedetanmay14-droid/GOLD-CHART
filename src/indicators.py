import numpy as np
import pandas as pd

class TechnicalIndicators:
    """Vectorized technical indicators calculation using pandas and numpy."""

    @staticmethod
    def compute_all(df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        if df_out.empty or "close" not in df_out.columns:
            return df_out

        close = df_out["close"]
        high = df_out["high"] if "high" in df_out.columns else close
        low = df_out["low"] if "low" in df_out.columns else close

        # EMAs
        for span in [9, 21, 50, 200]:
            df_out[f"ema_{span}"] = close.ewm(span=span, adjust=False).mean()

        # SMAs
        for window in [20, 50]:
            df_out[f"sma_{window}"] = close.rolling(window=window).mean()

        # RSI (14)
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df_out["rsi_14"] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df_out["macd"] = ema_12 - ema_26
        df_out["macd_signal"] = df_out["macd"].ewm(span=9, adjust=False).mean()
        df_out["macd_hist"] = df_out["macd"] - df_out["macd_signal"]

        # ATR (14)
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df_out["atr_14"] = tr.ewm(span=14, adjust=False).mean()

        # Bollinger Bands (20, 2)
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df_out["bb_upper"] = sma_20 + (std_20 * 2)
        df_out["bb_lower"] = sma_20 - (std_20 * 2)
        df_out["bb_width"] = (df_out["bb_upper"] - df_out["bb_lower"]) / (sma_20 + 1e-10)

        # Rate of Change (ROC 10)
        df_out["roc_10"] = close.pct_change(10) * 100

        # Stochastic %K (14, 3)
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        df_out["stoch_k"] = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
        df_out["stoch_d"] = df_out["stoch_k"].rolling(window=3).mean()

        return df_out
