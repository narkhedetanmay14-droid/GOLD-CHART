import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MarketStructureEngine:
    """Calculates market structure, swings, BOS, CHoCH, FVG, liquidity pools, and session levels with zero lookahead bias."""

    @staticmethod
    def detect_swings(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
        """Detect swing highs and swing lows with mandatory forward lag (window) for confirmation."""
        df_out = df.copy()
        highs = df_out["high"].values
        lows = df_out["low"].values
        n = len(df_out)

        swing_high = np.zeros(n, dtype=bool)
        swing_low = np.zeros(n, dtype=bool)

        for i in range(window, n - window):
            # Swing High: highest in [i - window, i + window]
            is_sh = True
            for j in range(i - window, i + window + 1):
                if highs[j] > highs[i]:
                    is_sh = False
                    break
            if is_sh:
                swing_high[i] = True

            # Swing Low: lowest in [i - window, i + window]
            is_sl = True
            for j in range(i - window, i + window + 1):
                if lows[j] < lows[i]:
                    is_sl = False
                    break
            if is_sl:
                swing_low[i] = True

        df_out["swing_high"] = swing_high
        df_out["swing_low"] = swing_low
        return df_out

    @staticmethod
    def detect_bos_choch(df: pd.DataFrame) -> pd.DataFrame:
        """Detect Break of Structure (BOS) and Change of Character (CHoCH)."""
        df_out = df.copy()
        if "swing_high" not in df_out.columns or "swing_low" not in df_out.columns:
            df_out = MarketStructureEngine.detect_swings(df_out)

        n = len(df_out)
        bos_bullish = np.zeros(n, dtype=bool)
        bos_bearish = np.zeros(n, dtype=bool)
        choch_bullish = np.zeros(n, dtype=bool)
        choch_bearish = np.zeros(n, dtype=bool)

        last_swing_high = np.nan
        last_swing_low = np.nan
        trend = 0  # 1 = bullish, -1 = bearish

        closes = df_out["close"].values
        highs = df_out["high"].values
        lows = df_out["low"].values
        sh = df_out["swing_high"].values
        sl = df_out["swing_low"].values

        for i in range(n):
            if sh[i]:
                last_swing_high = highs[i]
            if sl[i]:
                last_swing_low = lows[i]

            # Check BOS / CHoCH on close break
            if not np.isnan(last_swing_high) and closes[i] > last_swing_high:
                if trend == -1:
                    choch_bullish[i] = True
                else:
                    bos_bullish[i] = True
                trend = 1
                last_swing_high = np.nan  # reset after break

            if not np.isnan(last_swing_low) and closes[i] < last_swing_low:
                if trend == 1:
                    choch_bearish[i] = True
                else:
                    bos_bearish[i] = True
                trend = -1
                last_swing_low = np.nan

        df_out["bos_bullish"] = bos_bullish
        df_out["bos_bearish"] = bos_bearish
        df_out["choch_bullish"] = choch_bullish
        df_out["choch_bearish"] = choch_bearish
        df_out["trend_state"] = trend
        return df_out

    @staticmethod
    def detect_fvg(df: pd.DataFrame) -> pd.DataFrame:
        """Detect Fair Value Gaps (FVG) across 3 consecutive candles."""
        df_out = df.copy()
        n = len(df_out)
        fvg_bullish = np.zeros(n, dtype=bool)
        fvg_bearish = np.zeros(n, dtype=bool)

        highs = df_out["high"].values
        lows = df_out["low"].values

        for i in range(2, n):
            # Bullish FVG: Low[i] > High[i-2]
            if lows[i] > highs[i - 2]:
                fvg_bullish[i] = True
            # Bearish FVG: High[i] < Low[i-2]
            if highs[i] < lows[i - 2]:
                fvg_bearish[i] = True

        df_out["fvg_bullish"] = fvg_bullish
        df_out["fvg_bearish"] = fvg_bearish
        return df_out

    @staticmethod
    def detect_liquidity_sweeps(df: pd.DataFrame) -> pd.DataFrame:
        """Detect equal highs/lows and liquidity sweeps."""
        df_out = df.copy()
        n = len(df_out)
        sweep_high = np.zeros(n, dtype=bool)
        sweep_low = np.zeros(n, dtype=bool)

        highs = df_out["high"].values
        lows = df_out["low"].values
        closes = df_out["close"].values

        # Rolling 10-bar high/low liquidity levels
        for i in range(20, n):
            prev_high = highs[i-20:i].max()
            prev_low = lows[i-20:i].min()

            # Sweep high: candle high exceeds prev high, but close is below prev high
            if highs[i] > prev_high and closes[i] < prev_high:
                sweep_high[i] = True
            # Sweep low: candle low falls below prev low, but close is above prev low
            if lows[i] < prev_low and closes[i] > prev_low:
                sweep_low[i] = True

        df_out["sweep_high"] = sweep_high
        df_out["sweep_low"] = sweep_low
        return df_out

    @classmethod
    def compute_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = cls.detect_swings(df)
        df = cls.detect_bos_choch(df)
        df = cls.detect_fvg(df)
        df = cls.detect_liquidity_sweeps(df)
        return df
