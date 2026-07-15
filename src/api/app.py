from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from src.ingestion.read_logs import load_logs
from src.detections.brute_force import detect_brute_force
from src.detections.impossible_travel import detect_impossible_travel
from src.ml.predict import predict_with_explanation
from src.llm.summarize import generate_incident_summary


app = Flask(__name__)
CORS(app) 


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "AI SOC Analyst API is running"})


@app.route("/sample-logs", methods=["GET"])
def get_sample_logs():
    """
    Returns our synthetic log dataset as JSON, so the frontend can fetch it
    and use it to trigger analysis - avoids needing a file upload feature yet.
    """
    logs = pd.read_csv("data/raw/synthetic_logs.csv").head(100)
    logs["timestamp"] = logs["timestamp"].astype(str)
    return jsonify(logs.to_dict(orient="records"))
@app.route("/analyze", methods=["POST"])
def analyze_logs():
    input_data = request.get_json()

    if not input_data:
        return jsonify({"error": "No log data provided"}), 400

    logs = pd.DataFrame(input_data)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])

    brute_force_results = detect_brute_force(logs, threshold=3)
    travel_results = detect_impossible_travel(logs, max_speed_kmh=900)
    ml_results = predict_with_explanation(logs)

    # Generate a human-readable summary using the LLM, based on everything detected
    incident_summary = generate_incident_summary(brute_force_results, travel_results, ml_results)

    return jsonify({
        "rule_based": {
            "brute_force_alerts": brute_force_results,
            "impossible_travel_alerts": travel_results
        },
        "ml_based": {
            "attack_predictions": ml_results
        },
        "incident_summary": incident_summary,
        "summary": {
            "total_rule_based_alerts": len(brute_force_results) + len(travel_results),
            "total_ml_flagged_events": len(ml_results)
        }
    })


if __name__ == "__main__":
    app.run(debug=False, port=5000)