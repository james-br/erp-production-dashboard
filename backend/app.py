import os
from collections import defaultdict
from datetime import date, datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from models import db, WorkOrder, InventoryItem, STATUSES, WORKCENTERS
from services.ai import generate_briefing
from services.zpl import work_order_label

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///erp_demo.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    CORS(app)

    # ---------- Work orders ----------

    @app.get("/api/orders")
    def list_orders():
        q = WorkOrder.query
        status = request.args.get("status")
        if status:
            q = q.filter(WorkOrder.status == status)
        active_only = request.args.get("active") == "1"
        if active_only:
            q = q.filter(WorkOrder.status.in_(["queued", "in_progress", "qc_hold"]))
        orders = q.order_by(WorkOrder.due_date.asc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.patch("/api/orders/<int:order_id>")
    def update_order(order_id):
        o = db.get_or_404(WorkOrder, order_id)
        data = request.get_json(force=True)

        if "status" in data:
            if data["status"] not in STATUSES:
                return jsonify({"error": f"status must be one of {STATUSES}"}), 400
            o.status = data["status"]
            if o.status == "in_progress" and not o.started_at:
                o.started_at = datetime.utcnow()
            if o.status in ("complete", "shipped") and not o.completed_at:
                o.completed_at = datetime.utcnow()
                o.qty_completed = o.qty_ordered

        for field in ("qty_completed", "scrap_count", "priority"):
            if field in data:
                setattr(o, field, data[field])

        db.session.commit()
        return jsonify(o.to_dict())

    @app.get("/api/orders/<int:order_id>/label")
    def order_label(order_id):
        o = db.get_or_404(WorkOrder, order_id)
        zpl = work_order_label(o)
        return Response(zpl, mimetype="text/plain")

    # ---------- Inventory ----------

    @app.get("/api/inventory")
    def list_inventory():
        items = InventoryItem.query.order_by(InventoryItem.sku).all()
        return jsonify([i.to_dict() for i in items])

    # ---------- Metrics ----------

    @app.get("/api/metrics/summary")
    def metrics_summary():
        orders = WorkOrder.query.all()
        today = date.today()
        window_start = today - timedelta(days=30)

        finished = [
            o for o in orders
            if o.completed_at and o.completed_at.date() >= window_start
        ]
        on_time = [o for o in finished if o.completed_at.date() <= o.due_date]
        total_good = sum(o.qty_completed for o in finished)
        total_scrap = sum(o.scrap_count for o in finished)

        # Daily throughput (units completed) for the last 30 days
        by_day = defaultdict(int)
        for o in finished:
            by_day[o.completed_at.date().isoformat()] += o.qty_completed
        throughput = [
            {"date": (window_start + timedelta(days=i)).isoformat(),
             "units": by_day.get((window_start + timedelta(days=i)).isoformat(), 0)}
            for i in range(31)
        ]

        # Open load per workcenter
        active = [o for o in orders if o.status in ("queued", "in_progress", "qc_hold")]
        load = defaultdict(lambda: {"orders": 0, "units_remaining": 0})
        for o in active:
            load[o.workcenter]["orders"] += 1
            load[o.workcenter]["units_remaining"] += max(
                o.qty_ordered - o.qty_completed, 0
            )
        workcenter_load = [
            {"workcenter": wc, **load[wc]} for wc in WORKCENTERS
        ]

        # Andon status per workcenter: red if any late/at-risk, amber if QC hold
        andon = {}
        for wc in WORKCENTERS:
            wc_orders = [o for o in active if o.workcenter == wc]
            if any(o.is_late or o.at_risk for o in wc_orders):
                andon[wc] = "red"
            elif any(o.status == "qc_hold" for o in wc_orders):
                andon[wc] = "amber"
            elif wc_orders:
                andon[wc] = "green"
            else:
                andon[wc] = "idle"

        return jsonify({
            "open_orders": len(active),
            "at_risk": len([o for o in active if o.at_risk or o.is_late]),
            "on_time_pct": round(len(on_time) / len(finished) * 100, 1) if finished else None,
            "scrap_rate_pct": round(total_scrap / (total_good + total_scrap) * 100, 2)
            if (total_good + total_scrap) else None,
            "throughput_30d": throughput,
            "workcenter_load": workcenter_load,
            "andon": andon,
        })

    # ---------- AI briefing ----------

    @app.post("/api/ai/briefing")
    def ai_briefing():
        orders = WorkOrder.query.all()
        low_stock = [i for i in InventoryItem.query.all() if i.low_stock]
        return jsonify(generate_briefing(orders, low_stock))

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5001)
