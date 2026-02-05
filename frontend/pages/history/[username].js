import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import HistoryList from '../../components/HistoryList';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function HistoryPage() {
  const router = useRouter();
  const { username } = router.query;
  const [history, setHistory] = useState(null);

  useEffect(() => {
    if (!username) return;
    fetch(`${API_BASE}/api/history/reddit/${username}`)
      .then((res) => res.json())
      .then((data) => setHistory(data));
  }, [username]);

  return (
    <main>
      <header>
        <h1>History for {username}</h1>
      </header>
      {!history && <div className="card">Loading…</div>}
      {history && <HistoryList snapshots={history.snapshots} />}
    </main>
  );
}
