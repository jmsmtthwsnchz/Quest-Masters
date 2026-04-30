
class Inventory:
    def __init__(self, size=12):
        self.slots = [None] * size

    def add_item(self, item):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = item
                return True
        return False
