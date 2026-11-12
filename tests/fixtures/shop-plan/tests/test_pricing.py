import unittest

from shop import pricing


class PricingTest(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(pricing.subtotal([{"price": 2, "qty": 3}, {"price": 1, "qty": 1}]), 7)

    def test_discount_codes(self):
        self.assertEqual(pricing.discount_for("SAVE10"), 0.1)
        self.assertEqual(pricing.discount_for("nope"), 0)

    def test_tax(self):
        self.assertEqual(pricing.apply_tax(10), 12)
