import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(brute_force_alerts, travel_alerts, ml_predictions):
    """
    Constructs a clear, structured prompt describing our detection results,
    for the LLM to summarize into a human-readable incident report.
    """
    prompt = "You are a Security Operations Center (SOC) assistant. "
    prompt += "Summarize the following detected security events into a clear, concise incident report "
    prompt += "for a human analyst. Be specific about users, techniques, and recommended next steps.\n\n"

    if brute_force_alerts:
        prompt += "=== Brute Force Detections (Rule-Based) ===\n"
        for alert in brute_force_alerts:
            prompt += f"- User '{alert['user']}' had {alert['failed_login_count']} failed login attempts. "
            prompt += f"MITRE Technique: {alert['mitre_technique_id']} ({alert['mitre_technique_name']})\n"
        prompt += "\n"

    if travel_alerts:
        prompt += "=== Impossible Travel Detections (Rule-Based) ===\n"
        for alert in travel_alerts:
            prompt += f"- User '{alert['user']}' logged in from {alert['first_location']} then "
            prompt += f"{alert['second_location']}, requiring {alert['required_speed_kmh']} km/h "
            prompt += f"(MITRE: {alert['mitre_technique_id']})\n"
        prompt += "\n"

    if ml_predictions:
        prompt += "=== ML Model Flagged Events ===\n"
        for pred in ml_predictions:
            prompt += f"- User '{pred['user']}' at {pred['timestamp']}, "
            prompt += f"confidence: {pred['ml_confidence']:.0%}. "
            top_feature = pred['top_contributing_features'][0]['feature']
            prompt += f"Primary factor: {top_feature}\n"
        prompt += "\n"

    prompt += "Provide: 1) A brief overall summary, 2) Severity assessment (Low/Medium/High/Critical), "
    prompt += "3) Recommended immediate actions."

    return prompt


def generate_incident_summary(brute_force_alerts, travel_alerts, ml_predictions):
    """
    Calls the Gemini API to generate a human-readable incident summary
    from our structured detection results.
    """
    if not brute_force_alerts and not travel_alerts and not ml_predictions:
        return "No security incidents detected. All monitored activity appears normal."

    prompt = build_prompt(brute_force_alerts, travel_alerts, ml_predictions)

    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text