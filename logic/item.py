class Item:
    def __init__(self, name, description, image, effect_func=None):
        self.name = name
        self.description = description
        self.image = image
        self.effect_func = effect_func

    def use(self, target):
        """Executes the item's unique effect function.[cite: 5]"""
        if self.effect_func:
            return self.effect_func(target)
        return False
