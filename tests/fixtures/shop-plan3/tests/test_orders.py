import unittest

from shop.orders import Order, page


class OrdersTest(unittest.TestCase):
    def test_total_with_code(self):
        order = Order(1, [{"sku": "a", "price": 10, "qty": 1}], code="SAVE10")
        self.assertEqual(order.total(), 10.8)

    def test_first_page(self):
        orders = list(range(25))
        self.assertEqual(page(orders, 1), list(range(10)))
