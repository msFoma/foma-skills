from shop import inventory
from shop.utils import roundMoney


def summary(orders):
    lines = []
    for o in orders:
        lines.append("%s: %s" % (o.id, roundMoney(o.total())))
    return "\n".join(lines)


def stock_line(sku):
    return "%s: %d in stock" % (sku, inventory.get_inv(sku))
