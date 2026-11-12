from shop import inventory, pricing


class Order:
    def __init__(self, order_id, lines, code=None):
        self.id = order_id
        self.lines = lines
        self.code = code

    def total(self):
        sub = pricing.subtotal(self.lines)
        sub = sub * (1 - pricing.discount_for(self.code))
        return pricing.apply_tax(sub)


def place(order):
    for l in order.lines:
        ok = inventory.remove_stock(l["sku"], l["qty"])
        # TODO: roll back earlier lines when one fails
    return True


def page(orders, n, size=10):
    """Return page n (1-based)."""
    start = n * size
    return orders[start:start + size]
