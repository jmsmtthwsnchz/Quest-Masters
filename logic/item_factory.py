from logic.item import Item # Assuming you have an Item class
from utils import load_image

def create_test_item(health_bar):
    img = load_image("resource/inventory_imgs/cactus_fruit.jpg", scale=(70, 70))
    
    def heal_effect(target):
        if health_bar.hp_index > 0:
            health_bar.hp_index -= 1
            # NEW: Sync the visual image with the new index
            if hasattr(health_bar, 'update_visuals'):
                health_bar.update_visuals()
                
            print(f"Healed! Current HP Index: {health_bar.hp_index}")
            return True 
        return False 

    return Item(
        name="Cactus Fruit",
        description="A juicy fruit. Heals 1 HP.",
        image=img,
        effect_func=heal_effect
    )