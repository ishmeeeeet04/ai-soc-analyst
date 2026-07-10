import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from src.ingestion.read_logs import load_logs
from src.preprocessing.feature_engineering import engineer_features


# The exact columns our model will use as input - must be numeric only
FEATURE_COLUMNS = [
    "hour_of_day",
    "is_failed",
    "failed_count_last_10min",
    "unique_ips_last_10min",
    "seconds_since_last_login",
    "is_new_ip_for_user"
]


def prepare_training_data(filepath):
    """
    Loads raw logs, engineers features, and separates inputs (X) from labels (y).
    Input: filepath (string) - path to labeled CSV log file
    Output: X (DataFrame of features), y (Series of labels)
    """
    logs = load_logs(filepath)
    featured = engineer_features(logs)

    X = featured[FEATURE_COLUMNS]
    y = featured["is_attack"]

    return X, y


def train_model(X_train, y_train):
    """
    Trains a Random Forest classifier on the given training data.
    Input: X_train (features), y_train (labels)
    Output: a trained model object
    """
    model = RandomForestClassifier(
        n_estimators=100,      # number of trees in the forest
        max_depth=10,          # limits how deep each tree can grow (prevents overfitting)
        random_state=42,       # makes results reproducible - same "randomness" every run
        class_weight="balanced"  # compensates for our class imbalance (few attacks, many normal)
    )
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    print("Loading and preparing data...")
    X, y = prepare_training_data("data/raw/synthetic_logs.csv")

    print(f"Total samples: {len(X)}")
    print(f"Attack samples: {y.sum()}")
    print(f"Normal samples: {(y == 0).sum()}")

    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,       # 25% held back for testing
        random_state=42,      # reproducibility
        stratify=y            # ensures both sets keep the same attack/normal ratio
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    print("\nTraining model...")
    model = train_model(X_train, y_train)

    print("\nEvaluating on test data...")
    y_pred = model.predict(X_test)

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Attack"]))

    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    # Save the trained model to disk so we can reuse it later without retraining
    joblib.dump(model, "models/random_forest_v1.pkl")
    print("\nModel saved to models/random_forest_v1.pkl")