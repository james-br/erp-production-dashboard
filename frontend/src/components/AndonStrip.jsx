const LABELS = {
  green: "Running",
  amber: "QC hold",
  red: "Attention",
  idle: "No load",
};

export default function AndonStrip({ andon, load }) {
  const loadByWc = Object.fromEntries(load.map((l) => [l.workcenter, l]));
  return (
    <div className="andon" role="status" aria-label="Workcenter status board">
      {Object.entries(andon).map(([wc, state]) => (
        <div key={wc} className={`andon-tile ${state}`}>
          <div className="wc">{wc}</div>
          <div className="st">
            {LABELS[state]} · {loadByWc[wc]?.orders ?? 0} orders ·{" "}
            {loadByWc[wc]?.units_remaining ?? 0} units
          </div>
        </div>
      ))}
    </div>
  );
}
