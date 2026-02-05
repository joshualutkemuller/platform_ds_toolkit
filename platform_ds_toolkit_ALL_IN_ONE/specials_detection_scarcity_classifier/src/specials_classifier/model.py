
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support

class SpecialsClassifier:
    def __init__(self, C: float = 1.0):
        self.pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=C,
                        solver="lbfgs",
                        max_iter=1000,
                        class_weight="balanced",
                    ),
                ),
            ]
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.pipeline.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(X)[:, 1]

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> dict:
        preds = self.predict(X)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y, preds, average="binary"
        )
        return {
            "precision_special": precision,
            "recall_special": recall,
            "f1_special": f1,
        }
