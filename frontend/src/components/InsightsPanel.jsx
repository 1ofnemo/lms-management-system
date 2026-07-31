const RECENT_SUBMISSIONS_CONSIDERED = 8;
const MAX_ITEMS_PER_LIST = 5;

function collectUnique(submissions, field, limit) {
  const seen = new Set();
  const result = [];
  for (const s of submissions) {
    for (const item of s.feedback?.[field] ?? []) {
      if (seen.has(item)) continue;
      seen.add(item);
      result.push(item);
      if (result.length >= limit) return result;
    }
  }
  return result;
}

function InsightsPanel({ submissions }) {
  const recent = [...submissions]
    .filter((s) => s.feedback)
    .sort((a, b) => new Date(b.graded_at) - new Date(a.graded_at))
    .slice(0, RECENT_SUBMISSIONS_CONSIDERED);

  const strengths = collectUnique(recent, "strengths", MAX_ITEMS_PER_LIST);
  const gaps = collectUnique(recent, "gaps", MAX_ITEMS_PER_LIST);

  if (strengths.length === 0 && gaps.length === 0) return null;

  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body">
        <h2 className="h6 text-muted mb-3">Insights</h2>
        <div className="row g-3">
          <div className="col-md-6">
            <h6 className="text-success">What's going well</h6>
            {strengths.length === 0 ? (
              <p className="text-muted small mb-0">Nothing to highlight yet.</p>
            ) : (
              <ul className="mb-0 ps-3">
                {strengths.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
          </div>
          <div className="col-md-6">
            <h6 className="text-danger">What needs improvement</h6>
            {gaps.length === 0 ? (
              <p className="text-muted small mb-0">Nothing flagged yet.</p>
            ) : (
              <ul className="mb-0 ps-3">
                {gaps.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default InsightsPanel;