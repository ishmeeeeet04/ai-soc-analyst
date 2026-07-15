import pandas as pd
import joblib
import shap

from src.preprocessing.feature_engineering import engineer_features
from src.ml.train_model import FEATURE_COLUMNS

_model = joblib.load("models/random_forest_v1.pkl")
_explainer = None  # lazy-loaded, only created when actually needed


def _get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(_model)
    return _explainer


def predict_with_explanation(logs):
    """
    Runs the trained ML model on log data, returning predictions with SHAP explanations
    ONLY for events flagged as attacks - dramatically reduces memory/compute vs
    explaining every single row.
    """
    featured = engineer_features(logs)
    X = featured[FEATURE_COLUMNS]

    predictions = _model.predict(X)
    probabilities = _model.predict_proba(X)[:, 1]

    # Only keep rows the model flagged as attacks - BEFORE running SHAP
    attack_indices = [i for i in range(len(X)) if predictions[i] == 1]

    if not attack_indices:
        return []

    # Run SHAP only on this much smaller subset
    X_attacks_only = X.iloc[attack_indices]
    explainer = _get_explainer()
    shap_values = explainer.shap_values(X_attacks_only)

    if isinstance(shap_values, list):
        attack_shap_values = shap_values[1]
    else:
        attack_shap_values = shap_values[:, :, 1]

    results = []
    for pos, original_idx in enumerate(attack_indices):
        contributions = list(zip(FEATURE_COLUMNS, attack_shap_values[pos]))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)

        top_features = [
            {"feature": name, "contribution": round(float(value), 4)}
            for name, value in contributions[:3]
        ]

        results.append({
            "row_index": int(original_idx),
            "user": featured.iloc[original_idx]["user"],
            "timestamp": str(featured.iloc[original_idx]["timestamp"]),
            "ml_confidence": round(float(probabilities[original_idx]), 4),
            "top_contributing_features": top_features
        })

    return results