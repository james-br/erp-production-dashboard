export default function LabelModal({ label, onClose }) {
  const copy = () => navigator.clipboard.writeText(label.zpl);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Traveler label — {label.order.order_number}</h3>
        <p className="hint">
          Raw ZPL II, ready for a Zebra printer over port 9100. Paste it into{" "}
          <a href="http://labelary.com/viewer.html" target="_blank" rel="noreferrer">
            the Labelary viewer
          </a>{" "}
          (4x6 @ 8dpmm) to preview the rendered label.
        </p>
        <pre>{label.zpl}</pre>
        <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
          <button className="primary" onClick={copy}>
            Copy ZPL
          </button>
          <button className="primary" style={{ background: "var(--line)", color: "var(--text)" }} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
