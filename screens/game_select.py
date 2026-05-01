import pygame
from config import SCREEN, DESIGN_W, DESIGN_H, WIDTH, HEIGHT, s_x, s_y, s_g
from utils import load_image
from ui.buttons import ImageButton
from ui.portrait import PortraitBox

class GameSelect:
    def __init__(self, switch_func, sound_manager=None):
        self.switch_screen = switch_func
        self.stage_data = []

        # Load assets
        default_bg = load_image("main_menu_imgs/main_menu_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        for i in range(3):
            portrait = load_image(f"main_menu_imgs/stage{i+1}.jfif", scale=(400, 600)) or default_bg
            bg = load_image(f"main_menu_imgs/stage{i+1}_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
            self.stage_data.append({"portrait": portrait, "bg": bg})

        self.stages = [PortraitBox(i, self.stage_data[i]["portrait"]) for i in range(3)]
        self.current_center = 0

        # UI Elements
        back_img = load_image("main_menu_imgs/back.png", scale=(450, 180), rotate=-3)
        back_hover = load_image("main_menu_imgs/back_hover.png", scale=(450, 180), rotate=-3)
        self.back_btn = ImageButton(s_x(50), s_y(50), back_img, back_hover)

        # State Variables
        self.last_move_time = 0
        self.cooldown_ms = 600
        self.bg_fade = 255
        self.prev_bg = None

        self.is_zooming = False
        self.zoom_scale = 1.0
        self.zoom_alpha = 255
        self.show_difficulty_menu = False
        self.selected_stage_idx = 0

        # Clickable rects for the sub-menu (initialized as None)
        self.easy_rect = self.med_rect = self.hard_rect = None

    def reset(self, **kwargs):
        self.is_zooming = False
        self.zoom_scale = 1.0
        self.zoom_alpha = 255
        self.show_difficulty_menu = False

        self.current_center = 0
        self.refresh_positions()

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
        now = pygame.time.get_ticks()

        # Phase 1: Carousel Mode - Only update movement if menu is closed
        if not self.show_difficulty_menu and not self.is_zooming:
            self.back_btn.update()
            for s in self.stages:
                s.update_animation(0.12)
            
            if self.bg_fade < 255:
                self.bg_fade = min(255, self.bg_fade + 18)

        # Phase 2: Zoom Animation Logic
        if self.is_zooming:
            self.zoom_scale += 0.05
            # FIXED MATH: Using zoom_scale to drive the fade
            self.zoom_alpha = max(0, 255 - (self.zoom_scale - 1.0) * 400)

            if self.zoom_alpha <= 0:
                self.is_zooming = False 
                self.show_difficulty_menu = True
        
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.show_difficulty_menu:
                        # Just close the sub-menu (Stay on this screen)
                        self.show_difficulty_menu = False
                        self.zoom_scale = 1.0
                        self.zoom_alpha = 255
                    else:
                        # Reset states before leaving to Main Menu
                        self.reset() 
                        self.switch_screen("main")
                
                # Only allow navigation if not in a sub-menu
                if not self.show_difficulty_menu and not self.is_zooming:
                    if e.key == pygame.K_LEFT or e.key == pygame.K_a: self.navigate(-1)
                    if e.key == pygame.K_RIGHT or e.key == pygame.K_d: self.navigate(1)

            # --- MOUSE CONTROLS ---
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # --- Carousel Mode Clicks ---
                    if not self.is_zooming and not self.show_difficulty_menu:
                        sorted_stages = sorted(self.stages, key=lambda x: x.curr_scale, reverse=True)
                        for s in sorted_stages:
                            if hasattr(s, 'rect') and s.rect and s.rect.collidepoint(e.pos):
                                clicked_idx = self.stages.index(s)
                                
                                if clicked_idx == self.current_center:
                                    self.is_zooming = True
                                    self.selected_stage_idx = clicked_idx
                                else:
                                    # Logic only runs if clicked_idx was successfully found
                                    self.navigate(1 if clicked_idx > self.current_center else -1)
                                break # Essential: stops checking other islands once one is hit
                
                    # --- Sub-Menu Clicks ---
                    elif self.show_difficulty_menu:
                        self.handle_difficulty_clicks(e.pos)

            # Back Button Logic
            if self.back_btn.is_clicked(e):
                if self.show_difficulty_menu:
                    self.show_difficulty_menu = False
                    self.zoom_scale = 1.0
                    self.zoom_alpha = 255
                else:
                    self.switch_screen("main")

    def draw(self):
        # Draw Background
        if self.prev_bg: SCREEN.blit(self.prev_bg, (0, 0))
        curr_bg = self.stage_data[self.current_center]["bg"]
        if curr_bg:
            curr_bg.set_alpha(self.bg_fade)
            SCREEN.blit(curr_bg, (0, 0))

        # Draw Carousel
        if not self.show_difficulty_menu:
            for s in sorted(self.stages, key=lambda x: x.curr_scale):
                if self.is_zooming and self.stages.index(s) == self.selected_stage_idx:
                    continue 
                s.draw(SCREEN)

        # Draw Zoom Effect
        if self.is_zooming:
            portrait = self.stage_data[self.selected_stage_idx]["portrait"]
            w, h = portrait.get_size()

            target_w = int(s_g(w) * self.zoom_scale)
            target_h = int(s_g(h) * self.zoom_scale)

            temp = pygame.transform.smoothscale(portrait, (target_w, target_h))
            temp.set_alpha(int(self.zoom_alpha))
            rect = temp.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(temp, rect)

        # Draw Difficulty Overlay
        if self.show_difficulty_menu:
            self.draw_difficulty_overlay()

        self.back_btn.draw(SCREEN)

    def draw_difficulty_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))

        # Create/Draw buttons
        self.easy_rect = self.draw_btn("Chapter 1", HEIGHT // 2 - 120, (50, 200, 50))
        self.med_rect = self.draw_btn("Chapter 2", HEIGHT // 2, (200, 200, 50))
        self.hard_rect = self.draw_btn("Chapter 3", HEIGHT // 2 + 120, (200, 50, 50))

    def draw_btn(self, text, y, color):
        from config import WHITE, s_x, s_y, s_g
        font = pygame.font.SysFont("Arial", 50, bold=True)
        surf = font.render(text, True, WHITE)

        rect = surf.get_rect(center=(WIDTH // 2, y))
        box = rect.inflate(60, 30)

        pygame.draw.rect(SCREEN, color, box, border_radius=s_g(15))
        pygame.draw.rect(SCREEN, WHITE, box, s_g(3), border_radius=s_g(15))
        SCREEN.blit(surf, rect)
        return box
 
    def handle_difficulty_clicks(self, pos):
        base = self.selected_stage_idx * 3

        if self.easy_rect and self.easy_rect.collidepoint(pos):
            self.switch_screen("game", stage_index=base + 0, difficulty="easy")
        elif self.med_rect and self.med_rect.collidepoint(pos):
            self.switch_screen("game", stage_index=base + 1, difficulty="medium")
        elif self.hard_rect and self.hard_rect.collidepoint(pos):
            self.switch_screen("game", stage_index=base + 2, difficulty="hard")

