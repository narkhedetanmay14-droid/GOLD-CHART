from typing import Dict, Any

class PredictionValidator:
    """Enforces the strict 90/90 decision gates and signal validity.

    Independent Boolean gates:
    - confidence_pass = confidence >= 90
    - efficiency_pass = efficiency >= 90
    A signal passes only if both are true.
    """

    @staticmethod
    def format_confidence_gate(confidence: float) -> str:
        """Format independent confidence gate status."""
        if confidence >= 90.0:
            return f"Confidence Gate: PASS ({confidence:.2f} >= 90)"
        else:
            return f"Confidence Gate: FAIL ({confidence:.2f} < 90)"

    @staticmethod
    def format_efficiency_gate(efficiency: float) -> str:
        """Format independent efficiency gate status."""
        if efficiency >= 90.0:
            return f"Efficiency Gate: PASS ({efficiency:.2f} >= 90)"
        else:
            return f"Efficiency Gate: FAIL ({efficiency:.2f} < 90)"

    @staticmethod
    def validate_signal(
        confidence_score: float,
        efficiency_score: float,
        direction: str,
        is_limit_valid: bool = True,
        is_data_fresh: bool = True
    ) -> Dict[str, Any]:
        """Strict 90/90 gate enforcement:
        confidence_pass = confidence >= 90
        efficiency_pass = efficiency >= 90
        A signal passes only if both are true (along with fresh data and valid limit).
        Otherwise: NO_TRADE.
        """
        confidence_pass = bool(confidence_score >= 90.0)
        efficiency_pass = bool(efficiency_score >= 90.0)

        confidence_gate_str = PredictionValidator.format_confidence_gate(confidence_score)
        efficiency_gate_str = PredictionValidator.format_efficiency_gate(efficiency_score)

        gates_passed = confidence_pass and efficiency_pass
        can_trade = (
            gates_passed
            and is_limit_valid
            and is_data_fresh
            and direction in ["BUY", "SELL"]
        )

        final_action = direction if can_trade else "NO_TRADE"

        reasons = []
        if not confidence_pass:
            reasons.append(confidence_gate_str)
        if not efficiency_pass:
            reasons.append(efficiency_gate_str)
        if not is_limit_valid:
            reasons.append("Limit Gate: FAIL (Invalid limit price)")
        if not is_data_fresh:
            reasons.append("Freshness Gate: FAIL (Stale market data)")
        if direction not in ["BUY", "SELL"] and gates_passed:
            reasons.append("Direction Gate: FAIL (No directional bias)")

        reason_str = "PASSED_ALL_GATES" if can_trade else "; ".join(reasons)

        return {
            "action": final_action,
            "can_trade": can_trade,
            "confidence": confidence_score,
            "efficiency": efficiency_score,
            "confidence_pass": confidence_pass,
            "efficiency_pass": efficiency_pass,
            "confidence_gate": confidence_gate_str,
            "efficiency_gate": efficiency_gate_str,
            "gates_passed": gates_passed,
            "reason": reason_str,
            "reasons": reasons
        }
