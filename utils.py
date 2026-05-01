import os
import pygame
from config import script_dir

def load_image(filename, alpha=True, scale=None, rotate=0):
    try:
        path = os.path.join(script_dir, "assets", filename)
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()

        if scale:
            img = pygame.transform.scale(img, (int(scale[0]), int(scale[1])))
        if rotate:
            img = pygame.transform.rotate(img, rotate)
        return img
    except Exception as e:
        print(f"Error loading image '{filename}': {e}")
        return None
