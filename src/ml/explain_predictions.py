import pandas as pd
import joblib
import shap

from src.ml.train_model import prepare_training_data, FEATURE_COLUMNS


def load_trained_model(model_path="models/random_forest_v1.pkl"):
    """
    Loads a previously trained and saved model from disk.
    Input: model_path (string) - path to the saved .pkl model file
    Output: the trained model object
    """
    return joblib.load(model_path)


def explain_prediction(model, X, row_index):
    """
    Explains a single prediction using SHAP values.
    Input:
        model - the trained model
        X (DataFrame) - the full feature table
        row_index (int) - which row to explain
    Output: prints a human-readable breakdown of the prediction
    """
    # Create a SHAP explainer specifically built for tree-based models (fast and exact)
    explainer = shap.TreeExplainer(model)

    # Get the single row we want to explain, keeping it as a DataFrame (not a Series)
    row = X.iloc[[row_index]]

    # Calculate SHAP values for this row
    shap_values = explainer.shap_values(row)

    # For a binary classifier, shap_values has a slightly different shape depending on version -
    # this handles both common cases safely
    if isinstance(shap_values, list):
        # Older SHAP versions: list of arrays, one per class - we want the "Attack" class (index 1)
        values_for_attack_class = shap_values[1][0]
    else:
        # Newer SHAP versions: single array with an extra dimension for class
        values_for_attack_class = shap_values[0, :, 1]

    # Get the model's actual prediction and confidence for this row
    prediction = model.predict(row)[0]
    probability = model.predict_proba(row)[0][1]  # probability of being "Attack"

    print(f"\n{'='*60}")
    print(f"Explaining Row {row_index}")
    print(f"{'='*60}")
    print(f"Prediction: {'🚨 ATTACK' if prediction == 1 else '✅ NORMAL'}")
    print(f"Confidence (probability of attack): {probability:.2%}")
    print(f"\nActual feature values for this event:")
    for col in FEATURE_COLUMNS:
        print(f"  {col}: {row[col].values[0]}")

    print(f"\nWhy the model made this decision (SHAP feature contributions):")
    # Pair each feature name with its SHAP contribution value
    feature_contributions = list(zip(FEATURE_COLUMNS, values_for_attack_class))
    # Sort by absolute impact - biggest influences first, regardless of direction
    feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    for feature_name, contribution in feature_contributions:
        direction = "pushed TOWARD attack" if contribution > 0 else "pushed TOWARD normal"
        print(f"  {feature_name}: {contribution:+.4f}  ({direction})")


if __name__ == "__main__":
    print("Loading model and data...")
    model = load_trained_model()
    X, y = prepare_training_data("data/raw/synthetic_logs.csv")

    # Find a row that's actually labeled as an attack, to get an interesting explanation
    attack_indices = y[y == 1].index

    print(f"Found {len(attack_indices)} attack rows in the dataset.")
    print(f"Explaining the first attack example...")

    first_attack_index = attack_indices[0]
    explain_prediction(model, X, first_attack_index)