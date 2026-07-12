export default function InventoryPanel({ items }) {
  const sorted = [...items].sort((a, b) => Number(b.low_stock) - Number(a.low_stock));
  return (
    <div className="panel">
      <h2>
        Inventory{" "}
        {items.some((i) => i.low_stock) && (
          <span className="badge late" style={{ marginLeft: 6 }}>
            {items.filter((i) => i.low_stock).length} low
          </span>
        )}
      </h2>
      {sorted.map((i) => (
        <div key={i.sku} className={`inv-row ${i.low_stock ? "low" : ""}`}>
          <div>
            <div className="sku">{i.sku}</div>
            <div className="name">{i.name}</div>
          </div>
          <div className="qty">
            {i.on_hand} {i.unit}
            <span style={{ color: "var(--muted)" }}> / {i.reorder_point}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
