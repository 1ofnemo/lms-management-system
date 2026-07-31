import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function ScoreTrendChart({ data }) {
  if (data.length < 2) return null; // a single point isn't a trend

  return (
    <div style={{ height: 100 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
          <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
          <YAxis
            domain={[0, 1]}
            tickFormatter={(v) => `${Math.round(v * 100)}%`}
            width={36}
            tick={{ fontSize: 10 }}
          />
          <Tooltip formatter={(v) => `${Math.round(v * 100)}%`} labelFormatter={(d) => d} />
          <Line type="monotone" dataKey="score" stroke="var(--bs-primary)" dot={{ r: 3 }} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ScoreTrendChart;