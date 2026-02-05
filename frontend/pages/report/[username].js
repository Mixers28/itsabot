import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import ScoreCard from '../../components/ScoreCard';
import ReasonList from '../../components/ReasonList';
import EvidenceList from '../../components/EvidenceList';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function ReportPage() {
  const router = useRouter();
  const { username } = router.query;
  const [report, setReport] = useState(null);

  useEffect(() => {
    if (!username) return;
    fetch(`${API_BASE}/api/report/reddit/${username}?snapshot=latest`)
      .then((res) => res.json())
      .then((data) => setReport(data));
  }, [username]);

  return (
    <main>
      <header>
        <h1>Report for {username}</h1>
      </header>
      {!report && <div className="card">Loading…</div>}
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
