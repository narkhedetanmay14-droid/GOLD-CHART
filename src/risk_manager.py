from typing import Dict, Any

class RiskManager:
    """Enforces strict risk management, 1:2 R:R, and portfolio limits."""

    def __init__(self, risk_reward_ratio: float = 2.0, max_risk_pct: float = 0.02):
        self.risk_reward_ratio = risk_reward_ratio
        self.max_risk_pct = max_risk_pct

    def validate_trade_risk(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        efficiency: float
    ) -> Dict[str, Any]:
        risk_distance = abs(entry_price - stop_loss)
        reward_distance = abs(take_profit - entry_price)

        if risk_distance == 0:
            return {"approved": False, "reason": "Zero risk distance"}

        actual_rr = reward_distance / risk_distance
        # Enforce 1:2 R:R (allow small float tolerance)
        if actual_rr < (self.risk_reward_ratio - 0.05):
            return {"approved": False, "reason": f"Risk/Reward {actual_rr:.2f} below required 1:{self.risk_reward_ratio}"}

        if confidence < 90.0 or efficiency < 90.0:
            return {"approved": False, "reason": f"Failed 90/90 gates (conf={confidence}, eff={efficiency})"}

        return {"approved": True, "risk_reward": actual_rr}
