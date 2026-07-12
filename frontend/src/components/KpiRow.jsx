export default function KpiRow({ metrics }) {
  const kpis = [
    { label: "Open orders", value: metrics.open_orders },
    {
      label: "At risk / late",
      value: metrics.at_risk,
      cls: metrics.at_risk > 0 ? "alarm" : "good",
    },
    {
      label: "On-time (30d)",
      value: metrics.on_time_pct != null ? `${metrics.on_time_pct}%` : "—",
      cls: metrics.on_time_pct >= 90 ? "good" : "",
    },
    {
      label: "Scrap rate (30d)",
      value:
        metrics.scrap_rate_pct != null ? `${metrics.scrap_rate_pct}%` : "—",
    },
  ];
  return (
    <div className="kpis">
      {kpis.map((k) => (
        <div key={k.label} className="kpi">
          <div className="label">{k.label}</div>
          <div className={`value ${k.cls || ""}`}>{k.value}</div>
        </div>
      ))}
    </div>
  );
}
