import pygame
from config import s_x, s_y, s_g, WIDTH, HEIGHT

class ImageButton:
    def __init__(self, x, y, img, hover_img):
        self.image = img
        self.hover_image = hover_img

        if isinstance(x, float) and x <= 1.0:
            final_x = int(WIDTH * x)
        else:
            final_x = s_x(x)
        
        if isinstance(y, float) and y <= 1.0:
            final_y = int(HEIGHT * y)
        else:
            final_y = s_y(y)
            
        self.pos = (final_x, final_y)
        self.rect = self.image.get_rect(topleft=self.pos) if self.image else pygame.Rect(self.pos[0], self.pos[1], s_g(360), s_g(120))
        self.hovered = False

    def update(self):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, surface):
        img_to_draw = self.hover_image if (self.hovered and self.hover_image) else self.image
        if img_to_draw:
            surface.blit(img_to_draw, self.rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered
