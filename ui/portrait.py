import pygame
from config import s_x, WIDTH, HEIGHT

class PortraitBox:
    def __init__(self, index, img_obj):
        self.image = img_obj
        
        self.anchors = [-s_x(500), WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4, WIDTH + s_x(500)]
        self.target_idx = index + 2

        self.curr_x = self.anchors[self.target_idx]
        self.curr_scale = 1.0 if self.target_idx == 2 else 0.5
        self.curr_alpha = 255 if self.target_idx == 2 else 128

    def update_target(self, new_idx):
        self.target_idx = new_idx

    def update_animation(self, speed=0.1):
        idx = max(0, min(len(self.anchors) - 1, self.target_idx))
        t_x = self.anchors[idx]
        t_scale = 1.0 if idx == 2 else 0.5
        t_alpha = 255 if idx == 2 else 128

        if idx == 0 or idx == 4:
            t_alpha = 0

        self.curr_x += (t_x - self.curr_x) * speed
        self.curr_scale += (t_scale - self.curr_scale) * speed
        self.curr_alpha += (t_alpha - self.curr_alpha) * speed

    def draw(self, surface):
        if not self.image or self.curr_alpha < 5:
            return
        
        w, h = self.image.get_size()
        sw, sh = int(w * self.curr_scale), int(h * self.curr_scale)

        if sw <= 0 or sh <= 0:
            return
        
        temp = pygame.transform.smoothscale(self.image, (sw, sh))
        temp.set_alpha(int(self.curr_alpha))
        rect = temp.get_rect(center=(int(self.curr_x), HEIGHT // 2))
        
        surface.blit(temp, rect)
