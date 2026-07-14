import { useState } from 'react';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  async function runAnalysis() {
    setLoading(true);
    setError(null);

    try {
      // Step 1: fetch our sample log data from the backend
      const logsResponse = await fetch('http://127.0.0.1:5000/sample-logs');
      const logs = await logsResponse.json();

      // Step 2: send those logs to our /analyze endpoint
      const analyzeResponse = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logs)
      });

      console.log('Response status:', analyzeResponse.status);

      if (!analyzeResponse.ok) {
        const errorText = await analyzeResponse.text();
        throw new Error(`Server returned ${analyzeResponse.status}: ${errorText}`);
      }

      const data = await analyzeResponse.json();
      setResults(data);
    } catch (err) {
      console.error('Full error details:', err);
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>AI-Powered SOC Analyst Dashboard</h1>

      <button onClick={runAnalysis} disabled={loading}>
        {loading ? 'Analyzing...' : 'Run Analysis'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {results && (
        <div style={{ marginTop: '20px' }}>
          <h2>Summary</h2>
          <p>Rule-Based Alerts: {results.summary.total_rule_based_alerts}</p>
          <p>ML-Flagged Events: {results.summary.total_ml_flagged_events}</p>

          <h2>Incident Report (AI-Generated)</h2>
          <div style={{ background: '#f4f4f4', padding: '15px', whiteSpace: 'pre-wrap' }}>
            {results.incident_summary}
          </div>

          <h2>Brute Force Alerts</h2>
          <ul>
            {results.rule_based.brute_force_alerts.map((alert, i) => (
              <li key={i}>
                {alert.user} — {alert.failed_login_count} failed logins
                ({alert.mitre_technique_id}: {alert.mitre_technique_name})
              </li>
            ))}
          </ul>

          <h2>Impossible Travel Alerts</h2>
          <ul>
            {results.rule_based.impossible_travel_alerts.map((alert, i) => (
              <li key={i}>
                {alert.user}: {alert.first_location} → {alert.second_location}
                ({alert.required_speed_kmh} km/h)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;