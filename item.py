# entities/item.py
from utils import load_image

class Item:
    def __init__(self, name, icon_name, description="A mysterious item."):
        self.name = name
        self.description = description
        # We use your utility to keep scaling consistent
        self.image = load_image(f"resource/items/{icon_name}.png", scale=(70, 70))