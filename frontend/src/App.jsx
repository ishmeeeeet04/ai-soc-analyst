import { useState } from 'react';
import './Dashboard.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const logsResponse = await fetch('http://127.0.0.1:5000/sample-logs');
      const logsResponse = await fetch(`${API_URL}/sample-logs`);
      const logs = await logsResponse.json();

      const analyzeResponse = await fetch('http://127.0.0.1:5000/analyze', {
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

  function confidenceClass(confidence) {
    if (confidence >= 0.7) return 'confidence-high';
    return 'confidence-medium';
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>🛡️ AI-Powered SOC Analyst</h1>
        <p>Autonomous threat detection, explainability & incident reporting</p>
        <button className="run-button" onClick={runAnalysis} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </button>
        {error && <p className="error-message">{error}</p>}
      </div>

      {results && (
        <>
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
            <table className="alert-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Timestamp</th>
                  <th>Confidence</th>
                  <th>Top Factor</th>
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
                    <td>{pred.top_contributing_features[0].feature}</td>
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