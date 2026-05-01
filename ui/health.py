# ui/health.py
import pygame
from utils import load_image
from config import s_x, s_y

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []

        for i in range(5, -1, -1): 
            img = load_image(f"resource/character/health/{i}.png", scale=(300, 50))
            if img:
                self.frames.append(img)
        
        self.hp_index = 0 # Index 0 is full health (5.png), Index 5 is dead (0.png)
        
        # Fallback if image fails to load
        if self.frames:
            self.image = self.frames[self.hp_index]
        else:
            self.image = pygame.Surface((s_x(300), s_y(50)))
            self.image.fill((0, 255, 0))
            
        # Top-Right corner positioning
        self.rect = self.image.get_rect(topright=(s_x(x), s_y(y)))

    def update_visuals(self):
        self.image = self.frames[self.hp_index]

    def take_damage(self):
        """Advances the health bar visually. Returns True if dead."""
        if self.hp_index < len(self.frames) - 1:
            self.hp_index += 1
            self.image = self.frames[self.hp_index]
            self.update_visuals()
            return False 
        return True # Player has died!
