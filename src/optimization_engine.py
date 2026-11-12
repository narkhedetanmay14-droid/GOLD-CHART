import itertools
import logging
from typing import Dict, Any, List, Callable

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """Performs grid and random search hyperparameter optimization with robustness penalization."""

    @staticmethod
    def grid_search(
        param_grid: Dict[str, List[Any]],
        eval_fn: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        best_score = -float("inf")
        best_params = {}
        history = []

        for combination in itertools.product(*values):
            params = dict(zip(keys, combination))
            try:
                score = eval_fn(params)
                history.append({"params": params, "score": score})
                if score > best_score:
                    best_score = score
                    best_params = params
            except Exception as e:
                logger.warning("Error evaluating params %s: %s", params, e)

        return {
            "best_params": best_params,
            "best_score": best_score,
            "history": history
        }

    @staticmethod
    def robust_objective(
        expectancy: float,
        trade_count: int,
        max_drawdown: float,
        min_trades: int = 20
    ) -> float:
        """Penalize low trade counts and large drawdowns."""
        if trade_count < min_trades:
            penalty = trade_count / float(min_trades)
        else:
            penalty = 1.0
        # Drawdown penalty
        score = (expectancy * penalty) - (0.5 * max_drawdown)
        return float(score)
