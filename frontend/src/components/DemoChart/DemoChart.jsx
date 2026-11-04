import "./DemoChart.css";

const W = 640;
const H = 260;
const PAD = { top: 28, right: 16, bottom: 56, left: 48 };

// Bar chart of help_count per week, drawn with plain SVG.
// A week with no session gets a dashed marker, not a zero bar.
export default function DemoChart({ data }) {
  if (data.length === 0) {
    return <p className="muted">No history yet. The app has not seen any sessions before this week.</p>;
  }

  const top = Math.max(4, ...data.map((d) => d.help_count));
  const step = Math.ceil(top / 4);
  const max = step * 4;
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const slot = innerW / data.length;
  const barW = Math.min(48, slot * 0.6);
  const y = (v) => PAD.top + innerH - (v / max) * innerH;

  const ticks = [0, 1, 2, 3, 4].map((i) => i * step);
  const summary = data
    .map((d) => (d.sessions === 0 ? `week ${d.week}: no session` : `week ${d.week}: ${d.help_count}`))
    .join(", ");

  return (
    <figure className="demo-chart">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Times help was used each week. ${summary}`}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={PAD.left} x2={W - PAD.right} y1={y(t)} y2={y(t)} className="grid" />
            <text x={PAD.left - 8} y={y(t) + 4} textAnchor="end" className="axis">
              {t}
            </text>
          </g>
        ))}

        {data.map((d, i) => {
          const cx = PAD.left + slot * i + slot / 2;
          return (
            <g key={d.week}>
              {d.sessions === 0 ? (
                <rect x={cx - barW / 2} y={y(0) - 6} width={barW} height={6} className="skipped" />
              ) : (
                <>
                  <rect x={cx - barW / 2} y={y(d.help_count)} width={barW} height={y(0) - y(d.help_count)} className="bar" />
                  <text x={cx} y={y(d.help_count) - 6} textAnchor="middle" className="value">
                    {d.help_count}
                  </text>
                </>
              )}
              <text x={cx} y={H - PAD.bottom + 24} textAnchor="middle" className="axis">
                {d.week}
              </text>
            </g>
          );
        })}

        <text x={PAD.left + innerW / 2} y={H - 8} textAnchor="middle" className="axis">
          Week
        </text>
      </svg>
      <figcaption>
        Times help was used each week. A dashed marker means no session that week.
      </figcaption>

      <details>
        <summary>Show as a table</summary>
        <table>
          <thead>
            <tr>
              <th>Week</th>
              <th>Sessions</th>
              <th>Help used</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.week}>
                <td>{d.week}</td>
                <td>{d.sessions}</td>
                <td>{d.sessions === 0 ? "No session" : d.help_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
