export default function ReasonList({ reasons }) {
  if (!reasons || reasons.length === 0) {
    return <div className="card">No reasons available yet.</div>;
  }
  return (
    <div className="card">
      <h3>Top Reasons</h3>
      {reasons.map((reason, idx) => (
        <div key={idx} style={{ marginBottom: 12 }}>
          <div style={{ fontWeight: 600 }}>
            {reason.title} <span className="badge">+{reason.impact}</span>
          </div>
          <div style={{ color: '#6b6b6b' }}>{reason.details}</div>
        </div>
      ))}
    </div>
  );
}
