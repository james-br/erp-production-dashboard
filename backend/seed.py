"""Seed the database with realistic manufacturing data.

Generates ~140 work orders spread over the past 60 days (most complete,
some active, some queued) plus a parts inventory, so the dashboard has
believable throughput history the moment you run it.

Usage:  python seed.py
"""
import random
from datetime import datetime, date, timedelta

from app import create_app
from models import db, WorkOrder, InventoryItem, WORKCENTERS

random.seed(42)

PRODUCTS = [
    ("Aluminum Spray Enclosure 48x36", "ASSY-3"),
    ("Aluminum Spray Enclosure 60x48", "ASSY-3"),
    ("Vinyl Window Frame 3050", "CNC-1"),
    ("Vinyl Window Frame 4060", "CNC-1"),
    ("Steel Mounting Bracket B-220", "WELD-2"),
    ("Steel Mounting Bracket B-340", "WELD-2"),
    ("Powder-Coated Panel 24x24", "PAINT-1"),
    ("Powder-Coated Panel 36x36", "PAINT-1"),
    ("Retail Display Crate", "PACK-1"),
]

CUSTOMERS = [
    "Pacific Coatings Co", "Westside Glass & Door", "Herrera Fabrication",
    "Delta Building Supply", "Monarch Interiors", "Cal-South Distributors",
    "Ironwood Manufacturing", "Bluewater Marine Outfitters",
]

INVENTORY = [
    ("AL-EXT-6063", "Aluminum Extrusion 6063-T5 20ft", "Raw Material", "ea", 12.40),
    ("AL-SHT-125", 'Aluminum Sheet .125" 4x8', "Raw Material", "ea", 68.00),
    ("ST-TUBE-2X2", "Steel Tube 2x2 11ga 24ft", "Raw Material", "ea", 41.25),
    ("VNL-LINEAL-W", "Vinyl Lineal White 16ft", "Raw Material", "ea", 9.80),
    ("PWD-RAL9005", "Powder Coat RAL 9005 Black 50lb", "Consumable", "box", 210.00),
    ("PWD-RAL9016", "Powder Coat RAL 9016 White 50lb", "Consumable", "box", 195.00),
    ("HW-RIVET-316", 'Rivet 3/16" SS (1000ct)', "Hardware", "box", 34.50),
    ("HW-SCREW-10", "#10 Self-Tap Screw (500ct)", "Hardware", "box", 18.75),
    ("GSK-EPDM-38", 'EPDM Gasket 3/8" 100ft', "Hardware", "roll", 52.00),
    ("LBL-ZT411-4X6", "Thermal Label 4x6 (roll of 500)", "Consumable", "roll", 22.00),
    ("PKG-CRATE-KIT", "Crate Kit 40x40", "Packaging", "kit", 61.00),
    ("PKG-FOAM-2IN", 'Foam Sheet 2" 4x8', "Packaging", "ea", 27.50),
]


def make_order(n, created, status):
    product, wc = random.choice(PRODUCTS)
    qty = random.choice([10, 20, 25, 40, 50, 75, 100])
    lead = random.randint(5, 12)
    due = created.date() + timedelta(days=lead)
    o = WorkOrder(
        order_number=f"WO-{2400 + n}",
        product=product,
        customer=random.choice(CUSTOMERS),
        workcenter=wc,
        qty_ordered=qty,
        status=status,
        priority=random.choices(["low", "normal", "hot"], weights=[2, 6, 2])[0],
        due_date=due,
        created_at=created,
    )
    if status == "queued":
        return o

    o.started_at = created + timedelta(days=random.randint(0, 2))
    if status == "in_progress":
        o.qty_completed = int(qty * random.uniform(0.1, 0.9))
    elif status == "qc_hold":
        o.qty_completed = int(qty * random.uniform(0.8, 1.0))
    else:  # complete / shipped
        o.qty_completed = qty
        slip = random.choices([-2, -1, 0, 0, 0, 1, 3], weights=[1, 2, 4, 4, 3, 2, 1])[0]
        o.completed_at = datetime.combine(due, datetime.min.time()) + timedelta(
            days=slip, hours=random.randint(8, 17)
        )
    o.scrap_count = random.choices([0, 0, 0, 1, 2, 4], weights=[5, 4, 3, 2, 1, 1])[0]
    return o


def run():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        n = 0
        today = datetime.utcnow()

        # Historical completed/shipped orders over the past 60 days
        for day_offset in range(60, 6, -1):
            created = today - timedelta(days=day_offset)
            for _ in range(random.randint(1, 3)):
                n += 1
                status = random.choice(["complete", "shipped", "shipped"])
                db.session.add(make_order(n, created, status))

        # Active floor: in progress / QC hold
        for _ in range(9):
            n += 1
            created = today - timedelta(days=random.randint(1, 6))
            db.session.add(make_order(n, created, "in_progress"))
        for _ in range(3):
            n += 1
            created = today - timedelta(days=random.randint(2, 7))
            db.session.add(make_order(n, created, "qc_hold"))

        # Backlog
        for _ in range(7):
            n += 1
            created = today - timedelta(days=random.randint(0, 3))
            db.session.add(make_order(n, created, "queued"))

        for sku, name, cat, unit, cost in INVENTORY:
            reorder = random.choice([10, 15, 20, 25])
            # a few items intentionally below reorder point for the demo
            on_hand = random.choice([reorder - 6, reorder - 3, reorder + 15,
                                     reorder + 30, reorder + 60])
            db.session.add(InventoryItem(
                sku=sku, name=name, category=cat, unit=unit,
                on_hand=max(on_hand, 0), reorder_point=reorder, unit_cost=cost,
            ))

        db.session.commit()
        print(f"Seeded {n} work orders and {len(INVENTORY)} inventory items.")


if __name__ == "__main__":
    run()
