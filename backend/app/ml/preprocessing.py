import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import TimeSeriesSplit


class LeakageSafePreprocessor:
    def __init__(self, variance_threshold: float = 1e-4, corr_threshold: float = 0.95):
        self.scaler = RobustScaler()
        self.variance_threshold = variance_threshold
        self.corr_threshold = corr_threshold
        self.selected_features: List[str] = []
        self.is_fitted: bool = False

    def fit(self, df_train: pd.DataFrame, feature_cols: List[str]) -> "LeakageSafePreprocessor":
        """
        Fits variance filter, correlation filter, and scaler strictly on TRAINING data.
        """
        X_train = df_train[feature_cols].copy()

        # 1. Variance Filter
        variances = X_train.var()
        non_constant = variances[variances > self.variance_threshold].index.tolist()

        # 2. Correlation Filter (Remove multicollinear features)
        corr_matrix = X_train[non_constant].corr().abs()
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > self.corr_threshold)]
        
        self.selected_features = [f for f in non_constant if f not in to_drop]

        # 3. Fit Scaler strictly on selected features of X_train
        self.scaler.fit(X_train[self.selected_features])
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted. Call fit() on training data first.")
        X = df[self.selected_features].copy()
        return self.scaler.transform(X)

    def fit_transform(self, df_train: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        return self.fit(df_train, feature_cols).transform(df_train)


def create_chronological_splits(
    df: pd.DataFrame, train_ratio: float = 0.7, val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits DataFrame strictly chronologically: Train (70%), Validation (15%), Test (15%).
    No shuffling or temporal overlap.
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    return train_df, val_df, test_df
