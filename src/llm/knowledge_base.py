# Our RAG knowledge base: a small curated set of documents combining
# MITRE ATT&CK guidance and example past incident learnings.
# In a real company, this would grow over time from actual incident reports,
# internal playbooks, and updated threat intelligence.

KNOWLEDGE_BASE_DOCUMENTS = [
    {
        "id": "mitre_t1110",
        "content": (
            "T1110 Brute Force (MITRE ATT&CK, Credential Access tactic): Adversaries may use "
            "brute force techniques to gain access to accounts when passwords are unknown or "
            "when password hashes are obtained. Common sub-techniques include Password Guessing, "
            "Password Cracking, Password Spraying, and Credential Stuffing. Recommended mitigations "
            "include enforcing account lockout policies after a defined number of failed attempts, "
            "implementing multi-factor authentication (MFA), monitoring for high volumes of failed "
            "authentication attempts, and using CAPTCHA on public-facing login forms."
        )
    },
    {
        "id": "mitre_t1078",
        "content": (
            "T1078 Valid Accounts (MITRE ATT&CK, Initial Access/Persistence/Privilege Escalation/"
            "Defense Evasion tactics): Adversaries may obtain and abuse credentials of existing "
            "accounts. Compromised valid accounts can provide access while bypassing typical "
            "detection since the activity looks like normal user behavior. Recommended mitigations "
            "include enforcing MFA especially for remote access, monitoring for impossible travel "
            "and anomalous login locations, implementing conditional access policies, and rotating "
            "credentials immediately upon suspected compromise."
        )
    },
    {
        "id": "past_incident_1",
        "content": (
            "Past Incident Learning: In a previous brute force incident, an attacker attempted "
            "12 rapid password guesses against a single account within 30 seconds before succeeding. "
            "Investigation revealed the account did not have MFA enabled, unlike most accounts in "
            "the organization. Lesson learned: prioritize immediate password reset and MFA enrollment "
            "for the affected account, and audit all accounts organization-wide for MFA coverage gaps, "
            "since brute force success often correlates with missing MFA rather than weak passwords alone."
        )
    },
    {
        "id": "past_incident_2",
        "content": (
            "Past Incident Learning: A previous impossible travel case involved a user account "
            "logging in from two countries 6,000km apart within 4 minutes. Root cause was a phished "
            "credential used by an attacker while the legitimate user was also actively logged in "
            "from their normal location. Lesson learned: impossible travel alerts should trigger "
            "immediate session termination for all active sessions of the affected account, not just "
            "a password reset, since the attacker may still have an active session even after password "
            "changes if session tokens aren't also invalidated."
        )
    },
    {
        "id": "severity_guidance",
        "content": (
            "Severity Classification Guidance: Critical severity applies when an attack results in "
            "confirmed successful unauthorized access to sensitive systems or data. High severity "
            "applies when an attack technique succeeded (e.g., brute force resulted in a successful "
            "login) but scope of impact is still being determined. Medium severity applies to detected "
            "attack attempts that did not succeed. Low severity applies to anomalies that may have "
            "benign explanations requiring further investigation."
        )
    }
]