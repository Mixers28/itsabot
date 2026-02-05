export default function ScoreCard({ title, score }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ fontSize: '32px', fontWeight: 700 }}>{score ?? '—'}</div>
    </div>
  );
}
