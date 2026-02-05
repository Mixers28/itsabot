export default function HistoryList({ snapshots }) {
  if (!snapshots || snapshots.length === 0) {
    return <div className="card">No history yet.</div>;
  }
  return (
    <div className="card">
      <h3>History</h3>
      <ul>
        {snapshots.map((snap) => (
          <li key={snap.snapshot_id}>
            {snap.collected_at} — automation {snap.automation_score}, coordination {snap.coordination_score ?? '—'}
          </li>
        ))}
      </ul>
    </div>
  );
}
