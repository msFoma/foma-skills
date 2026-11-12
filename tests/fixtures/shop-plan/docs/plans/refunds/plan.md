# Plan: refunds

Spec: none (small feature, agreed in chat)
Base: initial commit

## T1 — Add refund() to shop/orders.py
Files: shop/orders.py
Steps: add `refund(order, amount)`: raise ValueError if amount > order.total(); put every line back in stock with `inventory.add_stock(sku, qty)`; return `order.total() - amount`.
Done when: `python3 -c "from shop import inventory; from shop.orders import Order, refund; inventory.reset(); o = Order(1, [{'sku': 'a', 'price': 10, 'qty': 2}]); print(refund(o, 4), inventory.get_inv('a'))"` prints `20.0 2`
Model:
Status: todo

## T2 — Rename get_inv to get_inventory
Files: shop/inventory.py, shop/report.py
Steps: rename the function and update every caller; no behaviour change.
Done when: `grep -rn "get_inv\b" shop` finds nothing and the suite result is unchanged (only test_first_page fails)
Model:
Status: todo
