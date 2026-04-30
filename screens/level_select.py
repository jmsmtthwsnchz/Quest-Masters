import pygame
from config import SCREEN, DESIGN_W, DESIGN_H
from utils import load_image
from ui.buttons import ImageButton
from ui.portrait import PortraitBox

class LevelSelect:
    def __init__(self, switch_func):
        self.switch_screen = switch_func
        self.stage_data =[]

        default_bg = load_image("main_menu_imgs/main_menu_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        for i in range(3):
            portrait = load_image(f"main_menu_imgs/stage{i+1}.jfif", scale=(400, 600)) or default_bg
            bg = load_image(f"main_menu_imgs/stage{i+1}_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
            self.stage_data.append({"portrait": portrait, "bg": bg})

        self.stages = [PortraitBox(i, self.stage_data[i]["portrait"]) for i in range(3)]
        self.current_center = 0

        back_img = load_image("main_menu_imgs/back.png", scale=(450, 180), rotate=-3)
        back_hover = load_image("main_menu_imgs/back_hover.png", scale=(450, 180), rotate=-3)
        self.back_btn = ImageButton(50, 50, back_img, back_hover)

        self.last_move_time = 0
        self.cooldown_ms = 600
        self.bg_fade = 255
        self.prev_bg = None

    def refresh_positions(self):
        for i, stage in enumerate(self.stages):
            stage.update_target(i - self.current_center + 2)
        self.bg_fade = 0

    def navigate(self, direction):
        now = pygame.time.get_ticks()
        if now - self.last_move_time > self.cooldown_ms:
            new_val = self.current_center + direction
            if 0 <= new_val <= 2:
                self.prev_bg = self.stage_data[self.current_center]["bg"]
                self.current_center = new_val
                self.refresh_positions()
                self.last_move_time = now

    def update(self, events):
        self.back_btn.update()
        for s in self.stages:
            s.update_animation(0.12)

        if self.bg_fade < 255:
            self.bg_fade = min(255, self.bg_fade + 18)

        now = pygame.time.get_ticks()
        for e in events:
            # Keyboard Controls
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT or e.key == pygame.K_a: self.navigate(-1)
                if e.key == pygame.K_RIGHT or e.key == pygame.K_d: self.navigate(1)
                if e.key == pygame.K_RETURN and (now - self.last_move_time > self.cooldown_ms):
                    self.switch_screen("main")
            
            # Mouse Controls
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                from config import s_g, WIDTH, HEIGHT
                center_hitbox = pygame.Rect(0, 0, s_g(400), s_g(600))
                center_hitbox.center = (WIDTH // 2, HEIGHT // 2)

                if center_hitbox.collidepoint(e.pos) and (now - self.last_move_time > self.cooldown_ms):
                    self.switch_screen("game")

            if self.back_btn.is_clicked(e):
                self.switch_screen("main")

    def draw(self):
        if self.prev_bg:
            SCREEN.blit(self.prev_bg, (0, 0))
        else:
            SCREEN.fill((20, 20, 25))

        curr_bg = self.stage_data[self.current_center]["bg"]
        if curr_bg:
            curr_bg.set_alpha(self.bg_fade)
            SCREEN.blit(curr_bg, (0, 0))

        for s in sorted(self.stages, key=lambda x: x.curr_scale):
            s.draw(SCREEN)

        self.back_btn.draw(SCREEN)
