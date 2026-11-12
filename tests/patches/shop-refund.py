# Applied by tests/tasks/reviewing.json setup: appends a refund feature with planted issues.
from pathlib import Path

p = Path("shop/orders.py")
p.write_text(p.read_text() + '''

def refund(order, amount):
    """Refund part of an order and put its items back in stock."""
    refundTotal = order.total()
    if amount > refundTotal:
        raise ValueError("refund exceeds order total")
    try:
        for l in order.lines:
            inventory.add_stock(l["sku"], -l["qty"])
    except Exception:
        pass
    return refundTotal - amount
''')
