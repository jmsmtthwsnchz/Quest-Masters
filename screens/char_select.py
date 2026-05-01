import pygame
from config import SCREEN, DESIGN_W, DESIGN_H, WIDTH, HEIGHT, s_g
from utils import load_image

class CharacterSelect:
    def __init__(self, switch_func):
        self.switch_screen = switch_func
        # Load background (Now contains your baked-in descriptions)
        self.bg_original = load_image("resource/char_select.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        
        # Coordinates for the interactive frames
        self.base_male_rect = pygame.Rect(110, 220, 800, 680) 
        self.base_female_rect = pygame.Rect(1010, 220, 800, 680)

        # Slice the boxes for the hover-zoom effect
        self.male_surf_base = self.bg_original.subsurface(self.base_male_rect).copy()
        self.female_surf_base = self.bg_original.subsurface(self.base_female_rect).copy()

        self.show_dev_grid = False

    def get_dynamic_rects(self):
        """Calculates where the boxes are based on current window size."""
        male = pygame.Rect(s_g(self.base_male_rect.x), s_g(self.base_male_rect.y), 
                          s_g(self.base_male_rect.width), s_g(self.base_male_rect.height))
        female = pygame.Rect(s_g(self.base_female_rect.x), s_g(self.base_female_rect.y), 
                            s_g(self.base_female_rect.width), s_g(self.base_female_rect.height))
        return male, female

    def update(self, events):
        from config import get_scaled_mouse_pos
        mx, my = get_scaled_mouse_pos()
        male_rect, female_rect = self.get_dynamic_rects()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.show_dev_grid = not self.show_dev_grid
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clicking the box selects the character and starts the game
                if male_rect.collidepoint((mx, my)):
                    self.switch_screen("game", char_type="percival", stage_index=0)
                elif female_rect.collidepoint((mx, my)):
                    self.switch_screen("game", char_type="celena", stage_index=0)

    def draw(self):
        from config import get_scaled_mouse_pos
        mx, my = get_scaled_mouse_pos()
        
        # Draw background[cite: 3]
        bg_scaled = pygame.transform.scale(self.bg_original, (WIDTH, HEIGHT))
        SCREEN.blit(bg_scaled, (0, 0))

        male_rect, female_rect = self.get_dynamic_rects()

        # Percival Hover Logic[cite: 3]
        if male_rect.collidepoint((mx, my)):
            scaled_surf = pygame.transform.smoothscale(self.male_surf_base, (int(male_rect.width * 1.05), int(male_rect.height * 1.05)))
            offset_x = (scaled_surf.get_width() - male_rect.width) // 2
            offset_y = (scaled_surf.get_height() - male_rect.height) // 2
            SCREEN.blit(scaled_surf, (male_rect.x - offset_x, male_rect.y - offset_y))
        else:
            scaled_surf = pygame.transform.smoothscale(self.male_surf_base, (male_rect.width, male_rect.height))
            SCREEN.blit(scaled_surf, (male_rect.x, male_rect.y))

        # Celena Hover Logic[cite: 3]
        if female_rect.collidepoint((mx, my)):
            scaled_surf = pygame.transform.smoothscale(self.female_surf_base, (int(female_rect.width * 1.05), int(female_rect.height * 1.05)))
            offset_x = (scaled_surf.get_width() - female_rect.width) // 2
            offset_y = (scaled_surf.get_height() - female_rect.height) // 2
            SCREEN.blit(scaled_surf, (female_rect.x - offset_x, female_rect.y - offset_y))
        else:
            scaled_surf = pygame.transform.smoothscale(self.female_surf_base, (female_rect.width, female_rect.height))
            SCREEN.blit(scaled_surf, (female_rect.x, female_rect.y))

        # Dev tool for alignment[cite: 3]
        if self.show_dev_grid:
            self.draw_dev_alignment()

    def draw_dev_alignment(self):
        """Draws alignment guides and the current collision rects."""
        if not self.show_dev_grid:
            return

        male_rect, female_rect = self.get_dynamic_rects()

        # 1. Draw the Active Collision Rects (What the mouse actually 'hits')
        # Red for Percival, Blue for Celena
        pygame.draw.rect(SCREEN, (255, 0, 0), male_rect, 3) 
        pygame.draw.rect(SCREEN, (0, 0, 255), female_rect, 3)

        # 2. Draw a Coordinate Grid (Every 100 pixels)
        # This helps you find the 'Base' coordinates for __init__
        for x in range(0, DESIGN_W, 100):
            pygame.draw.line(SCREEN, (100, 100, 100), (s_g(x), 0), (s_g(x), HEIGHT), 1)
        for y in range(0, DESIGN_H, 100):
            pygame.draw.line(SCREEN, (100, 100, 100), (0, s_g(y)), (WIDTH, s_g(y)), 1)