from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.ingestion.read_logs import load_logs
from src.detections.brute_force import detect_brute_force
from src.detections.impossible_travel import detect_impossible_travel
from src.ml.predict import predict_with_explanation
from src.llm.summarize import generate_incident_summary
from src.storage.db import init_db, save_incident, get_recent_incidents, get_incident_by_id


app = Flask(__name__)
CORS(app)

init_db()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
) 


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "AI SOC Analyst API is running"})


@app.route("/sample-logs", methods=["GET"])
def get_sample_logs():
    """
    Returns our synthetic log dataset as JSON, so the frontend can fetch it
    and use it to trigger analysis - avoids needing a file upload feature yet.
    """
    logs = pd.read_csv("data/raw/synthetic_logs.csv").head(40)
    logs["timestamp"] = logs["timestamp"].astype(str)
    return jsonify(logs.to_dict(orient="records"))
@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze_logs():
    input_data = request.get_json(silent=True)

    # Check 1: valid JSON was sent at all
    if input_data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Check 2: must be a non-empty list of log records
    if not isinstance(input_data, list) or len(input_data) == 0:
        return jsonify({"error": "Expected a non-empty list of log records"}), 400

    # Check 3: cap request size to prevent abuse (adjust limit as needed)
    MAX_LOGS_PER_REQUEST = 5000
    if len(input_data) > MAX_LOGS_PER_REQUEST:
        return jsonify({"error": f"Too many records. Max {MAX_LOGS_PER_REQUEST} per request"}), 400

    # Check 4: required columns must be present in every record
    REQUIRED_FIELDS = {"user", "timestamp"}
    for i, record in enumerate(input_data):
        if not isinstance(record, dict):
            return jsonify({"error": f"Record at index {i} is not a valid object"}), 400
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            return jsonify({"error": f"Record at index {i} is missing required fields: {missing}"}), 400

    try:
        logs = pd.DataFrame(input_data)
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse log data: {e}")
        return jsonify({"error": "Invalid timestamp format in one or more records"}), 400

    try:
        brute_force_results = detect_brute_force(logs, threshold=3)
        travel_results = detect_impossible_travel(logs, max_speed_kmh=900)
        ml_results = predict_with_explanation(logs)
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
        return jsonify({"error": "Internal error while analyzing logs. Please check log format."}), 500

    # Generate a human-readable summary using the LLM, based on everything detected
    incident_summary = generate_incident_summary(brute_force_results, travel_results, ml_results)

    response_data = {
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
    }

    try:
        save_incident(brute_force_results, travel_results, ml_results, incident_summary, response_data)
    except Exception as e:
        logger.warning(f"Failed to save incident to history: {e}")

    return jsonify(response_data)

@app.route("/incidents", methods=["GET"])
def list_incidents():
    """Returns the most recent incidents (summary view, not full detail)."""
    incidents = get_recent_incidents(limit=20)
    return jsonify(incidents)


@app.route("/incidents/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    """Returns full detail for one specific past incident."""
    incident = get_incident_by_id(incident_id)
    if incident is None:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(incident)
if __name__ == "__main__":
    app.run(debug=False, port=5000)