import os
import pygame
from PIL import Image, ImageSequence
from config import s_x, s_y, s_g, script_dir

class Slider:
    def __init__(self, x, y, width, start_val=0.5, track_img=None, gif_filename=None, gif_scale=(50, 50), rotate=0, stick_offset_y=0, speed_factor=1.0):
        self.rect = pygame.Rect(s_x(x), s_y(y), s_x(width), s_g(30))
        self.value = start_val
        self.dragging = False
        self.track_img = track_img
        self.stick_offset_y = s_y(stick_offset_y)

        if track_img:
            aspect = track_img.get_height() / track_img.get_width()
            v_w = self.rect.width + s_x(90)
            v_h = int(v_w * aspect)
            scaled = pygame.transform.smoothscale(track_img, (v_w, v_h))
            self.track_img = pygame.transform.rotate(scaled, rotate) if rotate != 0 else scaled
            self.tx_off = (self.rect.width - self.track_img.get_width()) // 2
            self.ty_off = (self.rect.height - self.track_img.get_height()) // 2
        else:
            self.tx_off, self.ty_off = 0, 0
        self.frames = []

        if gif_filename:
            try:
                path = os.path.join(script_dir, "assets", gif_filename)
                with Image.open(path) as pil_img:
                    for frame in ImageSequence.Iterator(pil_img):
                        f = frame.convert("RGBA")
                        surf = pygame.image.frombytes(f.tobytes(), f.size, "RGBA")
                        self.frames.append(pygame.transform.smoothscale(surf, (s_g(gif_scale[0]), s_g(gif_scale[1]))))
                    self.delay = pil_img.info.get("duration", 100) / speed_factor
            except Exception as e:
                print(f"Failed to load GIF {gif_filename}: {e}")
        
        self.anim_idx = 0
        self.last_tick = pygame.time.get_ticks()

    def draw(self, surface):
        if self.track_img:
            surface.blit(self.track_img, (self.rect.x + self.tx_off, self.rect.y + self.ty_off + self.stick_offset_y))

        knob_x = self.rect.x + int(self.value * self.rect.width)
        knob_y = self.rect.centery

        if self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_tick > getattr(self, "delay", 100):
                self.anim_idx = (self.anim_idx + 1) % len(self.frames)
                self.last_tick = now
            k_rect = self.frames[self.anim_idx].get_rect(center=(knob_x, knob_y))
            surface.blit(self.frames[self.anim_idx], k_rect)
        else:
            pygame.draw.circle(surface, (255, 220, 100), (knob_x, knob_y), s_g(12))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(s_x(40), s_y(80)).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.value = (x - self.rect.left) / self.rect.width
