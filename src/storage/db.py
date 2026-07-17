import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/db/incidents.db"


def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates the incidents table if it doesn't already exist.
    Safe to call every time the app starts.
    """
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            total_alerts INTEGER NOT NULL,
            ml_flagged_count INTEGER NOT NULL,
            incident_summary TEXT,
            full_result_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_incident(brute_force_results, travel_results, ml_results, incident_summary, full_response):
    """
    Saves one analysis run as a row in the incidents table.
    full_response is the complete JSON response we send to the frontend,
    stored so we can retrieve the exact same data later.
    """
    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO incidents (created_at, total_alerts, ml_flagged_count, incident_summary, full_result_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(),
            len(brute_force_results) + len(travel_results),
            len(ml_results),
            incident_summary,
            json.dumps(full_response),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_incidents(limit=20):
    """
    Returns the most recent incidents, newest first, as a list of dicts.
    Does NOT include the full_result_json (too heavy for a list view) —
    use get_incident_by_id for full detail.
    """
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT id, created_at, total_alerts, ml_flagged_count, incident_summary
        FROM incidents
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_incident_by_id(incident_id):
    """
    Returns the full stored result (including full_result_json) for one incident.
    """
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["full_result_json"] = json.loads(result["full_result_json"])
    return result