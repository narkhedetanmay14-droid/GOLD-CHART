import numpy as np
import pandas as pd
from typing import Dict, Any

class OutcomeLabeler:
    """Labels trades based strictly on target-before-stop outcomes for 1:2 R:R."""

    @staticmethod
    def label_target_before_stop(
        df: pd.DataFrame,
        direction: str = "BUY",
        risk_rr: float = 2.0,
        horizon_bars: int = 15
    ) -> pd.Series:
        n = len(df)
        labels = np.zeros(n, dtype=int)
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        atrs = df["atr_14"].values if "atr_14" in df.columns else closes * 0.002

        for i in range(n - horizon_bars):
            entry = closes[i]
            r = max(atrs[i], entry * 0.001)

            if direction == "BUY":
                target = entry + (risk_rr * r)
                stop = entry - r
                fwd_highs = highs[i+1 : i+1+horizon_bars]
                fwd_lows = lows[i+1 : i+1+horizon_bars]
                t_hit = np.where(fwd_highs >= target)[0]
                s_hit = np.where(fwd_lows <= stop)[0]
            else:
                target = entry - (risk_rr * r)
                stop = entry + r
                fwd_highs = highs[i+1 : i+1+horizon_bars]
                fwd_lows = lows[i+1 : i+1+horizon_bars]
                t_hit = np.where(fwd_lows <= target)[0]
                s_hit = np.where(fwd_highs >= stop)[0]

            first_t = t_hit[0] if len(t_hit) > 0 else 999
            first_s = s_hit[0] if len(s_hit) > 0 else 999

            if first_t < first_s and first_t <= horizon_bars:
                labels[i] = 1  # Win
            else:
                labels[i] = 0  # Loss or timeout

        return pd.Series(labels, index=df.index, name=f"outcome_{direction}")
