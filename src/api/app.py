from flask import Flask, request, jsonify
import pandas as pd

from src.ingestion.read_logs import load_logs
from src.detections.brute_force import detect_brute_force
from src.detections.impossible_travel import detect_impossible_travel

# Create the Flask application instance - this object represents our entire web app
app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    """
    A simple endpoint to confirm the API is running.
    Real production systems always have a health check endpoint -
    used by monitoring tools to verify the service is alive.
    """
    return jsonify({"status": "ok", "message": "AI SOC Analyst API is running"})


@app.route("/analyze", methods=["POST"])
def analyze_logs():
    """
    Accepts log data as JSON, runs it through our detection engine,
    and returns detected threats with MITRE ATT&CK context.

    Expected input JSON format: a list of log row objects, e.g.:
    [
        {"timestamp": "2024-01-15 09:05:47", "source_ip": "203.0.113.99",
         "destination_ip": "10.0.0.5", "user": "alice", "action": "login", "status": "failed"},
        ...
    ]
    """
    # Get the JSON data sent in the request body
    input_data = request.get_json()

    if not input_data:
        return jsonify({"error": "No log data provided"}), 400

    # Convert the incoming list of dictionaries into a pandas DataFrame,
    # exactly like our load_logs() function does when reading a CSV
    logs = pd.DataFrame(input_data)
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])

    # Run our existing detection engine - completely unchanged from earlier milestones
    brute_force_results = detect_brute_force(logs, threshold=3)
    travel_results = detect_impossible_travel(logs, max_speed_kmh=900)

    return jsonify({
        "brute_force_alerts": brute_force_results,
        "impossible_travel_alerts": travel_results,
        "total_alerts": len(brute_force_results) + len(travel_results)
    })


if __name__ == "__main__":
    # debug=True auto-reloads the server when code changes, and shows detailed error pages -
    # extremely helpful during development, but NEVER used in real production (security risk)
    app.run(debug=True, port=5000)