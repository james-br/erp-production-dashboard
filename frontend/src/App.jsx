import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import AndonStrip from "./components/AndonStrip.jsx";
import KpiRow from "./components/KpiRow.jsx";
import ThroughputChart from "./components/ThroughputChart.jsx";
import OrdersTable from "./components/OrdersTable.jsx";
import AiBriefing from "./components/AiBriefing.jsx";
import InventoryPanel from "./components/InventoryPanel.jsx";
import LabelModal from "./components/LabelModal.jsx";

export default function App() {
  const [orders, setOrders] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [label, setLabel] = useState(null); // { order, zpl }
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [o, i, m] = await Promise.all([
        api.activeOrders(),
        api.inventory(),
        api.metrics(),
      ]);
      setOrders(o);
      setInventory(i);
      setMetrics(m);
      setError(null);
    } catch (e) {
      setError("Can't reach the API. Is the Flask server running on port 5001?");
    }
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 30000);
    return () => clearInterval(t);
  }, [refresh]);

  const handleStatusChange = async (id, status) => {
    await api.updateOrder(id, { status });
    refresh();
  };

  const handleShowLabel = async (order) => {
    const zpl = await api.orderLabel(order.id);
    setLabel({ order, zpl });
  };

  return (
    <div className="app">
      <header className="header">
        <h1>
          Production <span>Dashboard</span>
        </h1>
        <div className="clock">{new Date().toDateString()}</div>
      </header>

      {error && (
        <div className="panel" style={{ borderColor: "var(--alarm)" }}>
          {error}
        </div>
      )}

      {metrics && <AndonStrip andon={metrics.andon} load={metrics.workcenter_load} />}
      {metrics && <KpiRow metrics={metrics} />}

      <div className="grid">
        <div>
          {metrics && <ThroughputChart data={metrics.throughput_30d} />}
          <OrdersTable
            orders={orders}
            onStatusChange={handleStatusChange}
            onShowLabel={handleShowLabel}
          />
        </div>
        <div>
          <AiBriefing />
          <InventoryPanel items={inventory} />
        </div>
      </div>

      {label && <LabelModal label={label} onClose={() => setLabel(null)} />}
    </div>
  );
}
