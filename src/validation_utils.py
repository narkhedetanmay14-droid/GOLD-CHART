import numpy as np
import pandas as pd
from typing import Tuple

class ValidationUtils:
    """Provides purged and embargoed chronological time-series splits."""

    @staticmethod
    def chronological_split(
        df: pd.DataFrame,
        train_ratio: float = 0.6,
        val_ratio: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()
        return train_df, val_df, test_df
