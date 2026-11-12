import numpy as np
import pandas as pd
from typing import Dict, Any

class LabelGenerator:
    """Generates leakage-free triple-barrier target labels for 1:2 Risk/Reward."""

    @staticmethod
    def triple_barrier_labels(
        df: pd.DataFrame,
        risk_rr: float = 2.0,
        horizon: int = 15,
        atr_multiplier: float = 1.5
    ) -> pd.DataFrame:
        """Calculate forward 1:2 R:R triple-barrier labels.
        Labels:
         1: BUY target hit before stop
        -1: SELL target hit before stop
         0: NO_TRADE / time expired without reaching either barrier
        """
        df_out = df.copy()
        n = len(df_out)
        labels = np.zeros(n, dtype=int)
        mfe_list = np.zeros(n, dtype=float)
        mae_list = np.zeros(n, dtype=float)

        highs = df_out["high"].values
        lows = df_out["low"].values
        closes = df_out["close"].values
        atrs = df_out["atr_14"].values if "atr_14" in df_out.columns else closes * 0.002

        for i in range(n - horizon):
            entry_price = closes[i]
            r = max(atrs[i] * atr_multiplier, entry_price * 0.001)

            # BUY barriers: target = +2R, stop = -1R
            buy_target = entry_price + (risk_rr * r)
            buy_stop = entry_price - r

            # SELL barriers: target = -2R, stop = +1R
            sell_target = entry_price - (risk_rr * r)
            sell_stop = entry_price + r

            # Look forward within horizon
            fwd_highs = highs[i+1 : i+1+horizon]
            fwd_lows = lows[i+1 : i+1+horizon]

            # Track MFE / MAE relative to entry
            max_high = fwd_highs.max()
            min_low = fwd_lows.min()
            mfe_list[i] = max(0.0, max_high - entry_price)
            mae_list[i] = max(0.0, entry_price - min_low)

            # Evaluate BUY outcome
            buy_hit_target = np.where(fwd_highs >= buy_target)[0]
            buy_hit_stop = np.where(fwd_lows <= buy_stop)[0]

            first_buy_target = buy_hit_target[0] if len(buy_hit_target) > 0 else 999
            first_buy_stop = buy_hit_stop[0] if len(buy_hit_stop) > 0 else 999

            # Evaluate SELL outcome
            sell_hit_target = np.where(fwd_lows <= sell_target)[0]
            sell_hit_stop = np.where(fwd_highs >= sell_stop)[0]

            first_sell_target = sell_hit_target[0] if len(sell_hit_target) > 0 else 999
            first_sell_stop = sell_hit_stop[0] if len(sell_hit_stop) > 0 else 999

            if first_buy_target < first_buy_stop and first_buy_target <= horizon:
                labels[i] = 1  # BUY WIN
            elif first_sell_target < first_sell_stop and first_sell_target <= horizon:
                labels[i] = -1  # SELL WIN
            else:
                labels[i] = 0  # NO TRADE / Neutral

        df_out["target_label"] = labels
        df_out["mfe"] = mfe_list
        df_out["mae"] = mae_list
        return df_out
