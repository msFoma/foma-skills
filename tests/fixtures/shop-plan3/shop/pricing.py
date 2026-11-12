from shop.utils import round_money

TAX = 0.2


def subtotal(lines):
    total = 0
    for l in lines:
        total = total + l["price"] * l["qty"]
    return total


def apply_tax(amount):
    return round_money(amount * (1 + TAX))


def discount_for(code):
    if code == "SAVE10": return 0.1
    elif code == "SAVE20": return 0.2
    else: return 0
