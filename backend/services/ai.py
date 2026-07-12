"""AI production briefing.

Aggregates the current floor state and asks an LLM for a short
plain-language briefing: what's on track, what's at risk, what to do first.
Falls back to a rule-based summary when OPENAI_API_KEY is not set, so the
demo never breaks in front of a reviewer.
"""
import json
import os


def _floor_snapshot(orders, low_stock_items):
    active = [o for o in orders if o.status in ("queued", "in_progress", "qc_hold")]
    return {
        "date": __import__("datetime").date.today().isoformat(),
        "open_orders": len(active),
        "at_risk_orders": [
            {
                "order": o.order_number, "product": o.product,
                "customer": o.customer, "due": o.due_date.isoformat(),
                "pct_complete": round(o.qty_completed / o.qty_ordered * 100)
                if o.qty_ordered else 0,
                "workcenter": o.workcenter, "priority": o.priority,
            }
            for o in active if o.at_risk or o.is_late
        ],
        "qc_hold": [
            {"order": o.order_number, "product": o.product}
            for o in active if o.status == "qc_hold"
        ],
        "low_stock": [
            {"sku": i.sku, "name": i.name, "on_hand": i.on_hand,
             "reorder_point": i.reorder_point}
            for i in low_stock_items
        ],
    }


def _fallback_briefing(snap):
    lines = [f"{snap['open_orders']} open orders on the floor."]
    if snap["at_risk_orders"]:
        lines.append(
            f"{len(snap['at_risk_orders'])} order(s) at risk of missing due date: "
            + ", ".join(o["order"] for o in snap["at_risk_orders"][:5])
            + ". Prioritize these first."
        )
    if snap["qc_hold"]:
        lines.append(
            f"{len(snap['qc_hold'])} order(s) sitting in QC hold — "
            "clear these to free downstream capacity."
        )
    if snap["low_stock"]:
        lines.append(
            "Low stock: "
            + ", ".join(f"{i['sku']} ({i['on_hand']} on hand)" for i in snap["low_stock"])
            + ". Reorder today to avoid line stoppage."
        )
    if len(lines) == 1:
        lines.append("No orders at risk and no material shortages. Floor is healthy.")
    return " ".join(lines)


def generate_briefing(orders, low_stock_items):
    snap = _floor_snapshot(orders, low_stock_items)
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return {"source": "rules", "briefing": _fallback_briefing(snap)}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=400,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a production supervisor's assistant at a small "
                        "manufacturer. Given a JSON snapshot of the shop floor, "
                        "write a briefing of 4-6 sentences: overall state, which "
                        "orders need attention first and why, QC holds, and any "
                        "material shortages. Be direct and specific. Plain text only."
                    ),
                },
                {"role": "user", "content": json.dumps(snap)},
            ],
        )
        return {"source": "openai", "briefing": resp.choices[0].message.content.strip()}
    except Exception as e:  # noqa: BLE001 — demo must never 500 on AI failure
        return {
            "source": "rules",
            "briefing": _fallback_briefing(snap),
            "note": f"AI unavailable ({type(e).__name__}); rule-based fallback used.",
        }
