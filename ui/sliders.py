import os
import pygame
from PIL import Image, ImageSequence
from config import s_x, s_y, s_g, script_dir

class Slider:
    def __init__(self, x, y, width, start_val=0.5, track_img=None, gif_filename=None, gif_scale=(50, 50), rotate=0, stick_offset_y=0, speed_factor=1.0):
        # Store original values for dynamic scaling[cite: 3]
        self.orig_x = x
        self.orig_y = y
        self.orig_width = width
        self.orig_stick_y = stick_offset_y
        
        self.value = start_val
        self.dragging = False
        self.track_img_raw = track_img # Keep raw for re-scaling
        self.rotate = rotate
        self.gif_scale = gif_scale
        
        self.frames = []
        if gif_filename:
            try:
                path = os.path.join(script_dir, "assets", gif_filename)
                with Image.open(path) as pil_img:
                    for frame in ImageSequence.Iterator(pil_img):
                        f = frame.convert("RGBA")
                        surf = pygame.image.frombytes(f.tobytes(), f.size, "RGBA")
                        self.frames.append(surf) # Scaled in draw()
                    self.delay = pil_img.info.get("duration", 100) / speed_factor
            except Exception as e:
                print(f"Failed to load GIF {gif_filename}: {e}")
        
        self.anim_idx = 0
        self.last_tick = pygame.time.get_ticks()

    def get_current_rect(self):
        # Always calculate based on current window scale[cite: 3]
        return pygame.Rect(s_x(self.orig_x), s_y(self.orig_y), s_x(self.orig_width), s_g(30))

    def draw(self, surface):
        rect = self.get_current_rect()
        
        if self.track_img_raw:
            # Re-scale track image to current window size[cite: 3]
            aspect = self.track_img_raw.get_height() / self.track_img_raw.get_width()
            tw = rect.width + s_x(90)
            th = int(tw * aspect)
            scaled_track = pygame.transform.smoothscale(self.track_img_raw, (tw, th))
            if self.rotate != 0: 
                scaled_track = pygame.transform.rotate(scaled_track, self.rotate)
            
            tx = rect.x + (rect.width - scaled_track.get_width()) // 2
            ty = rect.y + (rect.height - scaled_track.get_height()) // 2 + s_y(self.orig_stick_y)
            surface.blit(scaled_track, (tx, ty))

        knob_x = rect.x + int(self.value * rect.width)
        knob_y = rect.centery

        if self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_tick > getattr(self, "delay", 100):
                self.anim_idx = (self.anim_idx + 1) % len(self.frames)
                self.last_tick = now
            
            # Scale gif frame dynamically[cite: 3]
            frame = pygame.transform.smoothscale(self.frames[self.anim_idx], (s_g(self.gif_scale[0]), s_g(self.gif_scale[1])))
            k_rect = frame.get_rect(center=(knob_x, knob_y))
            surface.blit(frame, k_rect)
        else:
            pygame.draw.circle(surface, (255, 220, 100), (knob_x, knob_y), s_g(12))

    def handle_event(self, event):
        rect = self.get_current_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.inflate(s_x(40), s_y(80)).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(rect.left, min(event.pos[0], rect.right))
            self.value = (x - rect.left) / rect.width