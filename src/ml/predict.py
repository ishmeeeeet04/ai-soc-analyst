import pandas as pd
import joblib
import shap

from src.preprocessing.feature_engineering import engineer_features
from src.ml.train_model import FEATURE_COLUMNS

# Load the model and create the SHAP explainer ONCE, at import time -
# not every time we get a request. Loading a model from disk is relatively slow,
# so doing it repeatedly per-request would make our API sluggish.
_model = joblib.load("models/random_forest_v1.pkl")
_explainer = shap.TreeExplainer(_model)


def predict_with_explanation(logs):
    """
    Runs the trained ML model on log data, returning predictions with SHAP explanations
    for any events flagged as attacks.

    Input: logs (DataFrame) - raw log data
    Output: a list of dictionaries, one per event flagged as an attack by the model,
            including confidence score and top contributing features
    """
    featured = engineer_features(logs)
    X = featured[FEATURE_COLUMNS]

    predictions = _model.predict(X)
    probabilities = _model.predict_proba(X)[:, 1]  # probability of "Attack" class

    shap_values = _explainer.shap_values(X)

    # Handle both SHAP output formats, same as in explain_predictions.py
    if isinstance(shap_values, list):
        attack_shap_values = shap_values[1]
    else:
        attack_shap_values = shap_values[:, :, 1]

    results = []
    for i in range(len(X)):
        if predictions[i] == 1:  # only report events the model flagged as attacks
            # Pair feature names with their SHAP contributions for this specific row
            contributions = list(zip(FEATURE_COLUMNS, attack_shap_values[i]))
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)

            # Keep only the top 3 most influential features - concise, readable explanation
            top_features = [
                {"feature": name, "contribution": round(float(value), 4)}
                for name, value in contributions[:3]
            ]

            results.append({
                "row_index": int(i),
                "user": featured.iloc[i]["user"],
                "timestamp": str(featured.iloc[i]["timestamp"]),
                "ml_confidence": round(float(probabilities[i]), 4),
                "top_contributing_features": top_features
            })

    return results