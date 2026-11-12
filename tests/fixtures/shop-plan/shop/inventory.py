_stock = {}


def add_stock(sku, qty):
    _stock[sku] = _stock.get(sku, 0) + qty


def get_inv(sku):
    return _stock.get(sku, 0)


def remove_stock(sku, qty):
    if _stock.get(sku, 0) < qty:
        return False
    _stock[sku] -= qty
    return True


def reset():
    _stock.clear()
