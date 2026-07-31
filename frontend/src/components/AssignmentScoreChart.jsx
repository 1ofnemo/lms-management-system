import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { BUCKET_CHART_COLOR } from "../masteryDisplay";

function AssignmentScoreChart({ submissions }) {
  const data = submissions
    .filter((s) => s.score !== null)
    .map((s) => ({
      label: `${s.topic_name} (${s.assignment_type})`,
      date: s.graded_at.slice(0, 10),
      score: s.score,
      bucket: s.bucket,
    }));

  if (data.length === 0) return null;

  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body">
        <h2 className="h6 text-muted mb-3">Assignment Scores</h2>
        <div style={{ height: 220 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
              {/* Individual labels get crowded past a handful of bars -- the tooltip carries
                  full detail on hover instead, so this stays readable at any submission count. */}
              <XAxis dataKey="label" tick={false} />
              <YAxis
                domain={[0, 1]}
                tickFormatter={(v) => `${Math.round(v * 100)}%`}
                width={36}
                tick={{ fontSize: 10 }}
              />
              <Tooltip
                formatter={(value) => [`${Math.round(value * 100)}%`, "Score"]}
                labelFormatter={(label, payload) =>
                  payload[0] ? `${label} — ${payload[0].payload.date}` : label
                }
              />
              <Bar dataKey="score">
                {data.map((entry, i) => (
                  <Cell key={i} fill={BUCKET_CHART_COLOR[entry.bucket] ?? "var(--bs-secondary)"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default AssignmentScoreChart;