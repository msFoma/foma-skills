import time
import unittest

from shop import inventory


class InventoryTest(unittest.TestCase):
    def setUp(self):
        inventory.reset()

    def test_add_and_remove(self):
        inventory.add_stock("a", 5)
        self.assertTrue(inventory.remove_stock("a", 3))
        self.assertFalse(inventory.remove_stock("a", 3))

    def test_bulk_restock_slow(self):
        for _ in range(3):
            inventory.add_stock("b", 1)
            time.sleep(0.5)
        self.assertEqual(inventory._stock["b"], 3)
