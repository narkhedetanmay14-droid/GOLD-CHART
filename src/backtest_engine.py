import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

class BacktestEngine:
    """Simple historical backtesting engine.

    Parameters
    ----------
    config: dict
        Backtesting configuration dictionary (risk/reward, costs, etc.).
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        # Defaults
        self.risk_reward = self.config.get("risk_reward", 2.0)  # 1:2
        self.spread = self.config.get("spread", 0.0)
        self.slippage = self.config.get("slippage", 0.0)
        self.commission = self.config.get("commission", 0.0)

    def _apply_costs(self, price: float, side: str) -> float:
        """Adjust price for spread, slippage and commission.
        side: "buy" or "sell".
        """
        if side == "buy":
            price = price + self.spread / 2 + self.slippage + self.commission
        else:
            price = price - self.spread / 2 - self.slippage - self.commission
        return price

    def run_backtest(
        self,
        market_df: pd.DataFrame,
        feature_df: pd.DataFrame,
        signal_df: pd.DataFrame,
        models: List[Any] | None = None,
    ) -> Dict[str, Any]:
        """Run backtest over provided data.

        Returns a dictionary with trade log DataFrame and summary metrics.
        """
        # Basic validation
        if market_df.empty:
            raise ValueError("market_df is empty")
        if signal_df.empty:
            raise ValueError("signal_df is empty")
        # Align indices
        df = market_df.join(signal_df, how="inner")
        trades = []
        n_rows = len(df)
        for i in range(n_rows):
            row = df.iloc[i]
            idx = df.index[i]
            signal = row.get("signal")
            if signal not in ["BUY", "SELL"]:
                continue
            price = row.get("mid") if "mid" in row else row.get("close")
            if price is None:
                continue
            side = "buy" if signal == "BUY" else "sell"
            entry_price = self._apply_costs(price, side)
            atr = row.get("atr", price * 0.001)
            risk = atr * 1.0  # 1R defined as 1 ATR
            target = entry_price + (self.risk_reward * risk) if side == "buy" else entry_price - (self.risk_reward * risk)
            stop = entry_price - risk if side == "buy" else entry_price + risk

            next_price = entry_price
            exit_price = None
            outcome = "NO_TRADE"

            if i + 1 < n_rows:
                next_row = df.iloc[i + 1]
                next_price = next_row.get("mid") if "mid" in next_row else next_row.get("close", entry_price)
                if side == "buy":
                    if next_price >= target:
                        exit_price = target
                        outcome = "WIN"
                    elif next_price <= stop:
                        exit_price = stop
                        outcome = "LOSS"
                else:
                    if next_price <= target:
                        exit_price = target
                        outcome = "WIN"
                    elif next_price >= stop:
                        exit_price = stop
                        outcome = "LOSS"

            if exit_price is None:
                exit_price = next_price

            trades.append({
                "timestamp": idx,
                "direction": signal,
                "entry": entry_price,
                "exit": exit_price,
                "outcome": outcome,
                "risk_reward": self.risk_reward,
            })
        trade_log = pd.DataFrame(trades)
        summary = self._compute_summary(trade_log)
        return {"trade_log": trade_log, "summary": summary}

    def _compute_summary(self, trade_log: pd.DataFrame) -> Dict[str, Any]:
        if trade_log.empty:
            return {}
        total = len(trade_log)
        wins = trade_log[trade_log["outcome"] == "WIN"]
        losses = trade_log[trade_log["outcome"] == "LOSS"]
        win_rate = len(wins) / total if total else 0.0
        avg_win = (wins["exit"] - wins["entry"]).mean() if not wins.empty else 0.0
        avg_loss = (losses["entry"] - losses["exit"]).mean() if not losses.empty else 0.0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        profit_factor = (wins["exit"].sum() - wins["entry"].sum()) / (
            losses["entry"].sum() - losses["exit"].sum()
        ) if not losses.empty else float("inf")
        max_dd = self._max_drawdown(trade_log)
        return {
            "total_trades": total,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
            "profit_factor": profit_factor,
            "max_drawdown": max_dd,
        }

    def _max_drawdown(self, trade_log: pd.DataFrame) -> float:
        if trade_log.empty:
            return 0.0
        equity = (trade_log["exit"] - trade_log["entry"]).cumsum()
        peak = equity.cummax()
        drawdown = (peak - equity).max()
        return drawdown
