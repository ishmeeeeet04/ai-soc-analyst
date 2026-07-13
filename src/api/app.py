from flask import Flask, request, jsonify
import pandas as pd

from src.ingestion.read_logs import load_logs
from src.detections.brute_force import detect_brute_force
from src.detections.impossible_travel import detect_impossible_travel
from src.ml.predict import predict_with_explanation

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "AI SOC Analyst API is running"})


@app.route("/analyze", methods=["POST"])
def analyze_logs():
    """
    Accepts log data as JSON, runs it through BOTH our rule-based detection engine
    AND our ML model, returning combined results with MITRE context and SHAP explanations.
    """
    input_data = request.get_json()

    if not input_data:
        return jsonify({"error": "No log data provided"}), 400

    logs = pd.DataFrame(input_data)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])

    # Rule-based detections (fast, deterministic, explainable by design)
    brute_force_results = detect_brute_force(logs, threshold=3)
    travel_results = detect_impossible_travel(logs, max_speed_kmh=900)

    # ML-based detection (catches subtler patterns, explained via SHAP)
    ml_results = predict_with_explanation(logs)

    return jsonify({
        "rule_based": {
            "brute_force_alerts": brute_force_results,
            "impossible_travel_alerts": travel_results
        },
        "ml_based": {
            "attack_predictions": ml_results
        },
        "summary": {
            "total_rule_based_alerts": len(brute_force_results) + len(travel_results),
            "total_ml_flagged_events": len(ml_results)
        }
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)