# logic/inventory.py
class Inventory:
    def __init__(self, size=12):
        self.slots = [None] * size

    def add_item(self, item):
        """Finds the first empty slot and adds the item[cite: 5]."""
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = item
                return True
        return False
