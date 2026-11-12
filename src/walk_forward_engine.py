import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

class WalkForwardEngine:
    """Chronological Walk-Forward validation with rolling or expanding windows."""

    def __init__(self, train_window: int = 100, test_window: int = 30, expanding: bool = False):
        self.train_window = train_window
        self.test_window = test_window
        self.expanding = expanding

    def generate_folds(self, df: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        n = len(df)
        folds = []
        start = 0
        while start + self.train_window + self.test_window <= n:
            train_start = 0 if self.expanding else start
            train_end = start + self.train_window
            test_end = train_end + self.test_window

            train_df = df.iloc[train_start:train_end].copy()
            test_df = df.iloc[train_end:test_end].copy()
            folds.append((train_df, test_df))

            start += self.test_window
        return folds
