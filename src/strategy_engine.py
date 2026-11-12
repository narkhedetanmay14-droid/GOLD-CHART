import numpy as np
import pandas as pd
from typing import Dict, Any, List

class StrategyEngine:
    """Implements 10 systematic trading strategies (S01 to S10) on XAU/USD market features."""

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        n = len(df_out)

        # S01: EMA 9/21 cross + RSI momentum
        s01_buy = (df_out["ema_9"] > df_out["ema_21"]) & (df_out["rsi_14"] > 50) & (df_out["rsi_14"] < 70)
        s01_sell = (df_out["ema_9"] < df_out["ema_21"]) & (df_out["rsi_14"] < 50) & (df_out["rsi_14"] > 30)

        # S02: EMA 20/50 alignment + strong trend
        s02_buy = (df_out["sma_20"] > df_out["sma_50"]) & (df_out["close"] > df_out["sma_20"])
        s02_sell = (df_out["sma_20"] < df_out["sma_50"]) & (df_out["close"] < df_out["sma_20"])

        # S03: Liquidity sweep + CHoCH confirmation
        s03_buy = df_out.get("sweep_low", False) & df_out.get("choch_bullish", False)
        s03_sell = df_out.get("sweep_high", False) & df_out.get("choch_bearish", False)

        # S04: BOS confirmation + pullback to EMA 21
        s04_buy = df_out.get("bos_bullish", False) & (df_out["close"] >= df_out["ema_21"])
        s04_sell = df_out.get("bos_bearish", False) & (df_out["close"] <= df_out["ema_21"])

        # S05: FVG imbalance fill + trend alignment
        s05_buy = df_out.get("fvg_bullish", False) & (df_out["ema_9"] > df_out["ema_50"])
        s05_sell = df_out.get("fvg_bearish", False) & (df_out["ema_9"] < df_out["ema_50"])

        # S06: Breakout + ATR expansion
        atr_avg = df_out["atr_14"].rolling(20).mean()
        s06_buy = (df_out["close"] > df_out["bb_upper"]) & (df_out["atr_14"] > atr_avg)
        s06_sell = (df_out["close"] < df_out["bb_lower"]) & (df_out["atr_14"] > atr_avg)

        # S07: EMA + RSI + Liquidity sweep
        s07_buy = (df_out["ema_9"] > df_out["ema_21"]) & (df_out["rsi_14"] < 40) & df_out.get("sweep_low", False)
        s07_sell = (df_out["ema_9"] < df_out["ema_21"]) & (df_out["rsi_14"] > 60) & df_out.get("sweep_high", False)

        # S08: Momentum + Candle range expansion
        s08_buy = (df_out["macd_hist"] > 0) & (df_out["body_ratio"] > 0.6) & (df_out["close"] > df_out["open"])
        s08_sell = (df_out["macd_hist"] < 0) & (df_out["body_ratio"] > 0.6) & (df_out["close"] < df_out["open"])

        # S09: Mean reversion on Bollinger Band extreme
        s09_buy = (df_out["close"] < df_out["bb_lower"]) & (df_out["stoch_k"] < 20)
        s09_sell = (df_out["close"] > df_out["bb_upper"]) & (df_out["stoch_k"] > 80)

        # S10: SMC Confluence (Sweep + FVG + Trend)
        s10_buy = df_out.get("sweep_low", False) & df_out.get("fvg_bullish", False) & (df_out["ema_21"] > df_out["ema_50"])
        s10_sell = df_out.get("sweep_high", False) & df_out.get("fvg_bearish", False) & (df_out["ema_21"] < df_out["ema_50"])

        for i in range(1, 11):
            key = f"S{i:02d}"
            b = locals()[f"s{i:02d}_buy"]
            s = locals()[f"s{i:02d}_sell"]
            sig = np.where(b, "BUY", np.where(s, "SELL", "NO_TRADE"))
            df_out[f"signal_{key}"] = sig

        # Primary composite signal: consensus majority or S01 fallback
        buy_votes = sum(df_out[f"signal_S{i:02d}"] == "BUY" for i in range(1, 11))
        sell_votes = sum(df_out[f"signal_S{i:02d}"] == "SELL" for i in range(1, 11))

        df_out["signal"] = np.where(buy_votes >= 2, "BUY", np.where(sell_votes >= 2, "SELL", "NO_TRADE"))
        return df_out
