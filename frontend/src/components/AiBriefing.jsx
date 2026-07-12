import { useState } from "react";
import { api } from "../api.js";

export default function AiBriefing() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      setResult(await api.briefing());
    } catch {
      setResult({
        source: "error",
        briefing: "Briefing failed. Check that the API is running.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel briefing">
      <h2>AI production briefing</h2>
      <button className="primary" onClick={generate} disabled={loading}>
        {loading ? "Generating…" : "Generate briefing"}
      </button>
      {result ? (
        <>
          <p>{result.briefing}</p>
          <div className="source">
            Source: {result.source === "openai" ? "OpenAI" : "rule-based fallback"}
            {result.note ? ` — ${result.note}` : ""}
          </div>
        </>
      ) : (
        <p style={{ color: "var(--muted)", fontSize: 13 }}>
          Summarizes floor state, flags at-risk orders, and calls out material
          shortages. Uses OpenAI when a key is configured, otherwise a
          rule-based fallback.
        </p>
      )}
    </div>
  );
}
