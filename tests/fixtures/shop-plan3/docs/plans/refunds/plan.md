# Plan: refunds

Spec: none (small feature, agreed in chat)
Base: initial commit

## T1 — Add refund() to shop/orders.py
Files: shop/orders.py
Steps: add `refund(order, amount)`: raise ValueError if amount > order.total(); put every line back in stock with `inventory.add_stock(sku, qty)`; return `order.total() - amount`.
Done when: `python3 -c "from shop import inventory; from shop.orders import Order, refund; inventory.reset(); o = Order(1, [{'sku': 'a', 'price': 10, 'qty': 2}]); print(refund(o, 4), inventory.get_inv('a'))"` prints `20.0 2`
Blocked by: none
Model: sonnet · effort medium — new logic with a stock side effect
Status: todo

## T2 — Rename get_inv to get_inventory
Files: shop/inventory.py, shop/report.py
Steps: rename the function and update every caller; no behaviour change.
Done when: `grep -rn "get_inv\b" shop` finds nothing and the suite result is unchanged (only test_first_page fails)
Blocked by: T1
Model: haiku · effort low — mechanical rename
Status: todo

## T3 — Add refund_line() to shop/report.py
Files: shop/report.py
Steps: add `refund_line(order, amount)` returning `"<order id>: refunded <amount>"` with the amount formatted by `roundMoney`.
Done when: `python3 -c "from shop.report import refund_line; from shop.orders import Order; print(refund_line(Order(7, []), 4))"` prints `7: refunded 4`
Blocked by: T2
Model: sonnet · effort low — small addition behind a clear contract
Status: todo
