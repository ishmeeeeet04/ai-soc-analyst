# Central reference for MITRE ATT&CK mappings used across our detection engine.
# Source: https://attack.mitre.org/

MITRE_MAPPING = {
    "brute_force": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": (
            "Adversaries may use brute force techniques to gain access to accounts "
            "when passwords are unknown, attempting many possible passwords/usernames "
            "until a correct combination is found."
        ),
        "mitre_url": "https://attack.mitre.org/techniques/T1110/"
    },
    "impossible_travel": {
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "tactic": "Initial Access, Persistence, Privilege Escalation, Defense Evasion",
        "description": (
            "Adversaries may obtain and abuse credentials of existing accounts as a means "
            "of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion. "
            "Impossible travel patterns (logins from geographically distant locations in an "
            "unrealistic timeframe) are a strong behavioral indicator of compromised valid accounts."
        ),
        "mitre_url": "https://attack.mitre.org/techniques/T1078/"
    }
}


def get_mitre_info(detection_type):
    """
    Retrieves MITRE ATT&CK details for a given detection type.
    Input: detection_type (string) - e.g. "brute_force" or "impossible_travel"
    Output: a dictionary of MITRE details, or None if not found
    """
    return MITRE_MAPPING.get(detection_type)