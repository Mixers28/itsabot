import { useState } from 'react';
import ScoreCard from '../components/ScoreCard';
import ReasonList from '../components/ReasonList';
import EvidenceList from '../components/EvidenceList';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function Home() {
  const [username, setUsername] = useState('');
  const [status, setStatus] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastStatus, setLastStatus] = useState(null);

  const updateStatus = (nextStatus) => {
    setStatus(nextStatus);
    if (nextStatus !== lastStatus) {
      console.info(`job_status ${nextStatus}`);
      setLastStatus(nextStatus);
    }
  };

  const analyze = async () => {
    setLoading(true);
    setReport(null);
    updateStatus('queued');
    const res = await fetch(`${API_BASE}/api/analyze/reddit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    setJobId(data.job_id || null);
    if (data.status === 'cached' && data.report_url) {
      const reportRes = await fetch(`${API_BASE}${data.report_url}`);
      const reportJson = await reportRes.json();
      setReport(reportJson);
      updateStatus('cached');
      setLoading(false);
      return;
    }
    const jobId = data.job_id;
    if (jobId) {
      console.info(`job_id ${jobId}`);
    }
    let attempts = 0;
    const poll = async () => {
      attempts += 1;
      const statusRes = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      const statusJson = await statusRes.json();
      if (statusJson.status === 'finished' && statusJson.result_url) {
        const reportRes = await fetch(`${API_BASE}${statusJson.result_url}`);
        const reportJson = await reportRes.json();
        setReport(reportJson);
        updateStatus('finished');
        setLoading(false);
        return;
      }
      if (attempts < 20) {
        updateStatus(statusJson.status);
        setTimeout(poll, 3000);
      } else {
        updateStatus('timeout');
        setLoading(false);
      }
    };
    poll();
  };

  return (
    <main>
      <header>
        <h1>Bot-Likelihood Analyzer</h1>
        <p>Analyze a Reddit account for automation likelihood with transparent evidence.</p>
      </header>

      <div className="card">
        <label htmlFor="username">Reddit username or URL</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="u/username or https://www.reddit.com/user/username"
        />
        <button onClick={analyze} disabled={!username || loading}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
        {status && <p>Status: {status}</p>}
        {jobId && <p>Job ID: {jobId}</p>}
      </div>

      {report && (
        <>
          <div className="grid">
            <ScoreCard title="Automation Likelihood" score={report.scores?.automation_score} />
            <ScoreCard title="Coordination Proxy" score={report.scores?.coordination_score} />
            <ScoreCard title="Confidence" score={report.scores?.confidence?.toFixed(2)} />
          </div>
          <ReasonList reasons={report.reasons} />
          <EvidenceList reasons={report.reasons} />
        </>
      )}
    </main>
  );
}
