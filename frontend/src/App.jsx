import { useState } from 'react';
import './Dashboard.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [view, setView] = useState('analysis'); // 'analysis' or 'history'
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const logsResponse = await fetch(`${API_URL}/sample-logs`);
      const logs = await logsResponse.json();

      const analyzeResponse = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logs)
      });

      if (!analyzeResponse.ok) {
        const errorText = await analyzeResponse.text();
        throw new Error(`Server returned ${analyzeResponse.status}`);
      }

      const data = await analyzeResponse.json();
      setResults(data);
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory() {
    setView('history');
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_URL}/incidents`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      setError('Error loading history: ' + err.message);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function viewIncident(id) {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_URL}/incidents/${id}`);
      const data = await res.json();
      setResults(data.full_result_json);
      setView('analysis');
    } catch (err) {
      setError('Error loading incident: ' + err.message);
    } finally {
      setHistoryLoading(false);
    }
  }

  function confidenceClass(confidence) {
    if (confidence >= 0.7) return 'confidence-high';
    return 'confidence-medium';
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>🛡️ AI-Powered SOC Analyst</h1>
        <p>Autonomous threat detection, explainability & incident reporting</p>

        <div className="view-toggle">
          <button
            className={`toggle-btn ${view === 'analysis' ? 'active' : ''}`}
            onClick={() => setView('analysis')}
          >
            Analysis
          </button>
          <button
            className={`toggle-btn ${view === 'history' ? 'active' : ''}`}
            onClick={loadHistory}
          >
            History
          </button>
        </div>

        {view === 'analysis' && (
          <>
            <button className="run-button" onClick={runAnalysis} disabled={loading}>
              {loading ? (
                <span className="button-loading">
                  <span className="spinner"></span>
                  Analyzing...
                </span>
              ) : 'Run Analysis'}
            </button>
            {loading && (
              <p className="loading-hint">
                Running ML inference, SHAP explanations & generating AI report — this can take up to a minute.
              </p>
            )}
          </>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>

      {view === 'history' && (
        <div className="section">
          <h2>🕘 Past Incidents</h2>
          {historyLoading ? (
            <p className="empty-state">Loading history...</p>
          ) : history.length === 0 ? (
            <p className="empty-state">No past incidents yet. Run an analysis to create one.</p>
          ) : (
            <table className="alert-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Rule-Based Alerts</th>
                  <th>ML-Flagged Events</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {history.map((incident) => (
                  <tr key={incident.id}>
                    <td>{new Date(incident.created_at).toLocaleString()}</td>
                    <td>{incident.total_alerts}</td>
                    <td>{incident.ml_flagged_count}</td>
                    <td>
                      <button className="view-link" onClick={() => viewIncident(incident.id)}>
                        View →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {view === 'analysis' && results && (
        <>
          <div className="detection-legend">
            <div className="legend-item">
              <span className="legend-dot rule-dot"></span>
              <strong>Rule-Based:</strong> deterministic checks (e.g. failed login count, travel speed) — always triggers on exact thresholds, no ambiguity
            </div>
            <div className="legend-item">
              <span className="legend-dot ml-dot"></span>
              <strong>ML-Based:</strong> probabilistic model (Random Forest) — flags subtler patterns with a confidence score, explained below via SHAP
            </div>
          </div>

          <div className="summary-cards">
            <div className="summary-card rule-based">
              <div className="value">{results.summary.total_rule_based_alerts}</div>
              <div className="label">Rule-Based Alerts</div>
            </div>
            <div className="summary-card ml-based">
              <div className="value">{results.summary.total_ml_flagged_events}</div>
              <div className="label">ML-Flagged Events</div>
            </div>
          </div>

          <div className="section">
            <h2>📋 Incident Report (AI-Generated)</h2>
            <div className="incident-report">{results.incident_summary}</div>
          </div>

          <div className="section">
            <h2>🚨 Brute Force Alerts (T1110)</h2>
            {results.rule_based.brute_force_alerts.length === 0 ? (
              <p className="empty-state">No brute force activity detected.</p>
            ) : (
              <table className="alert-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Failed Logins</th>
                    <th>MITRE Technique</th>
                  </tr>
                </thead>
                <tbody>
                  {results.rule_based.brute_force_alerts.map((alert, i) => (
                    <tr key={i}>
                      <td>{alert.user}</td>
                      <td>{alert.failed_login_count}</td>
                      <td><span className="mitre-badge">{alert.mitre_technique_id}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="section">
            <h2>🌍 Impossible Travel Alerts (T1078)</h2>
            {results.rule_based.impossible_travel_alerts.length === 0 ? (
              <p className="empty-state">No impossible travel detected.</p>
            ) : (
              <table className="alert-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>From → To</th>
                    <th>Required Speed</th>
                    <th>MITRE Technique</th>
                  </tr>
                </thead>
                <tbody>
                  {results.rule_based.impossible_travel_alerts.map((alert, i) => (
                    <tr key={i}>
                      <td>{alert.user}</td>
                      <td>{alert.first_location} → {alert.second_location}</td>
                      <td>{alert.required_speed_kmh} km/h</td>
                      <td><span className="mitre-badge">{alert.mitre_technique_id}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="section">
            <h2>🤖 ML Model Predictions</h2>
            <p className="section-hint">
              Confidence is the model's predicted probability of an attack. Top factors show which features pushed the prediction toward "attack" (↑) or away from it (↓), per SHAP.
            </p>
            <table className="alert-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Timestamp</th>
                  <th>Confidence</th>
                  <th>Top Contributing Factors (SHAP)</th>
                </tr>
              </thead>
              <tbody>
                {results.ml_based.attack_predictions.slice(0, 15).map((pred, i) => (
                  <tr key={i}>
                    <td>{pred.user}</td>
                    <td>{pred.timestamp}</td>
                    <td>
                      <span className={`confidence-badge ${confidenceClass(pred.ml_confidence)}`}>
                        {(pred.ml_confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>
                      <div className="shap-factors">
                        {pred.top_contributing_features.map((feat, j) => (
                          <span
                            key={j}
                            className={`shap-tag ${feat.contribution >= 0 ? 'shap-positive' : 'shap-negative'}`}
                          >
                            {feat.contribution >= 0 ? '↑' : '↓'} {feat.feature}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {results.ml_based.attack_predictions.length > 15 && (
              <p className="empty-state">
                Showing 15 of {results.ml_based.attack_predictions.length} flagged events.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;