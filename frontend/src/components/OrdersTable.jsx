const STATUSES = ["queued", "in_progress", "qc_hold", "complete", "shipped"];

export default function OrdersTable({ orders, onStatusChange, onShowLabel }) {
  return (
    <div className="panel">
      <h2>Active work orders ({orders.length})</h2>
      {orders.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>
          No active orders. Run the seed script to load demo data.
        </p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Product</th>
              <th>Customer</th>
              <th>WC</th>
              <th>Qty</th>
              <th>Due</th>
              <th>Status</th>
              <th>Label</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td className="mono">
                  {o.order_number}{" "}
                  {o.priority === "hot" && <span className="badge hot">Hot</span>}{" "}
                  {(o.is_late || o.at_risk) && (
                    <span className="badge late">{o.is_late ? "Late" : "Risk"}</span>
                  )}
                </td>
                <td>{o.product}</td>
                <td>{o.customer}</td>
                <td className="mono">{o.workcenter}</td>
                <td className="mono">
                  {o.qty_completed}/{o.qty_ordered}
                </td>
                <td className="mono">{o.due_date.slice(5)}</td>
                <td>
                  <select
                    className="status-select"
                    value={o.status}
                    aria-label={`Status for ${o.order_number}`}
                    onChange={(e) => onStatusChange(o.id, e.target.value)}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </td>
                <td>
                  <button className="link" onClick={() => onShowLabel(o)}>
                    ZPL
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
