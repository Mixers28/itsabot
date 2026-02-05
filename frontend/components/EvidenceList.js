export default function EvidenceList({ reasons }) {
  const links = (reasons || []).flatMap((r) => r.evidence || []);
  if (links.length === 0) {
    return <div className="card">No evidence links yet.</div>;
  }
  return (
    <div className="card">
      <h3>Evidence</h3>
      <ul>
        {links.map((link, idx) => (
          <li key={idx}>
            <a href={link} target="_blank" rel="noreferrer">
              {link}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
