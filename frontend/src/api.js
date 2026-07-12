async function req(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  const ct = res.headers.get("content-type") || "";
  return ct.includes("json") ? res.json() : res.text();
}

export const api = {
  activeOrders: () => req("/api/orders?active=1"),
  updateOrder: (id, data) =>
    req(`/api/orders/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  orderLabel: (id) => req(`/api/orders/${id}/label`),
  inventory: () => req("/api/inventory"),
  metrics: () => req("/api/metrics/summary"),
  briefing: () => req("/api/ai/briefing", { method: "POST" }),
};
