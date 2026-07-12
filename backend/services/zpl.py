"""ZPL II label generation for work orders.

Produces a 4x6 (203 dpi) travel label for Zebra printers — the same class
of label used on real production floors. The output can be sent straight
to a ZT411/ZT230 over port 9100, or previewed via the Labelary API.
"""


def work_order_label(order) -> str:
    """Render a 4x6 work-order traveler label as raw ZPL."""
    due = order.due_date.strftime("%m/%d/%Y")
    priority_flag = "^GB240,60,60^FS" if order.priority == "hot" else ""
    hot_text = (
        "^FO560,180^A0N,40,40^FR^FDHOT^FS" if order.priority == "hot" else ""
    )
    return f"""^XA
^CI28
^PW812
^LL1218

^FO40,40^A0N,36,36^FDPRODUCTION TRAVELER^FS
^FO40,90^GB732,3,3^FS

^FO40,120^A0N,80,80^FD{order.order_number}^FS
^FO520,150{priority_flag}
{hot_text}

^FO40,230^A0N,28,28^FDPRODUCT^FS
^FO40,265^A0N,42,42^FD{order.product[:34]}^FS

^FO40,340^A0N,28,28^FDCUSTOMER^FS
^FO40,375^A0N,38,38^FD{order.customer[:36]}^FS

^FO40,450^A0N,28,28^FDQTY^FS
^FO40,485^A0N,54,54^FD{order.qty_ordered}^FS
^FO300,450^A0N,28,28^FDWORKCENTER^FS
^FO300,485^A0N,54,54^FD{order.workcenter}^FS
^FO560,450^A0N,28,28^FDDUE^FS
^FO560,485^A0N,40,40^FD{due}^FS

^FO40,580^GB732,3,3^FS

^FO180,640^BY3
^BCN,220,Y,N,N
^FD{order.order_number}^FS

^FO40,960^A0N,24,24^FDScan at each workcenter to log completion.^FS
^XZ"""
