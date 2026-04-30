import pygame
import sys
from config import SCREEN, DESIGN_W, DESIGN_H, WIDTH, HEIGHT, get_scaled_mouse_pos
from utils import load_image
from ui.buttons import ImageButton

class MainMenu:
    def __init__(self, switch_func):
        self.switch_screen = switch_func

        self.bg = load_image("main_menu_imgs/main_menu_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        self.start_hover = load_image("main_menu_imgs/start_hover.png", scale=(390, 130), rotate=5)
        self.settings_hover = load_image("main_menu_imgs/settings_hover.png", scale=(378, 145), rotate=-2)
        self.quit_hover = load_image("main_menu_imgs/quit_hover.png", scale=(378, 130), rotate=4)

        self.start_btn = ImageButton(0.402, 0.315, None, self.start_hover)
        self.settings_btn = ImageButton(0.391, 0.440, None, self.settings_hover)
        self.quit_btn = ImageButton(0.370, 0.567, None, self.quit_hover)

    def update(self, events):
        self.start_btn.update()
        self.settings_btn.update()
        self.quit_btn.update()
        
        for e in events:
            if self.start_btn.is_clicked(e): self.switch_screen("level_select")
            if self.settings_btn.is_clicked(e): self.switch_screen("settings")
            if self.quit_btn.is_clicked(e):
                pygame.quit()
                sys.exit()

    def draw(self):
        if self.bg:
            SCREEN.blit(self.bg, (0, 0))
        self.start_btn.draw(SCREEN)
        self.settings_btn.draw(SCREEN)
        self.quit_btn.draw(SCREEN)
