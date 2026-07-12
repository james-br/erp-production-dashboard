from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

STATUSES = ["queued", "in_progress", "qc_hold", "complete", "shipped"]
WORKCENTERS = ["CNC-1", "WELD-2", "PAINT-1", "ASSY-3", "PACK-1"]


class WorkOrder(db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    product = db.Column(db.String(120), nullable=False)
    customer = db.Column(db.String(120), nullable=False)
    workcenter = db.Column(db.String(20), nullable=False)
    qty_ordered = db.Column(db.Integer, nullable=False)
    qty_completed = db.Column(db.Integer, default=0)
    scrap_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="queued", nullable=False)
    priority = db.Column(db.String(10), default="normal")  # low / normal / hot
    due_date = db.Column(db.Date, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_late(self):
        if self.status in ("complete", "shipped"):
            return self.completed_at and self.completed_at.date() > self.due_date
        return date.today() > self.due_date

    @property
    def at_risk(self):
        if self.status in ("complete", "shipped"):
            return False
        days_left = (self.due_date - date.today()).days
        pct_done = self.qty_completed / self.qty_ordered if self.qty_ordered else 0
        return days_left <= 2 and pct_done < 0.8

    def to_dict(self):
        return {
            "id": self.id,
            "order_number": self.order_number,
            "product": self.product,
            "customer": self.customer,
            "workcenter": self.workcenter,
            "qty_ordered": self.qty_ordered,
            "qty_completed": self.qty_completed,
            "scrap_count": self.scrap_count,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_late": self.is_late,
            "at_risk": self.at_risk,
        }


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    unit = db.Column(db.String(10), default="ea")
    on_hand = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=0)
    unit_cost = db.Column(db.Float, default=0.0)

    @property
    def low_stock(self):
        return self.on_hand <= self.reorder_point

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "on_hand": self.on_hand,
            "reorder_point": self.reorder_point,
            "unit_cost": self.unit_cost,
            "low_stock": self.low_stock,
        }
