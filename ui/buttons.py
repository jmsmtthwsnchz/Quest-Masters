import pygame
from config import s_x, s_y, s_g, WIDTH, HEIGHT, get_scaled_mouse_pos
from sound_manager import SoundManager # Import your new manager

# Try to import volume settings, fallback to 1.0 if not found
try:
    from screens.settings import settings_state
except ImportError:
    settings_state = {"sound_volume": 1.0}

class ImageButton:
    # Added sound_manager as an optional parameter to share one instance if you want
    def __init__(self, x, y, img, hover_img, sound_manager=None): 
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
        
        # Fixed inconsistent variable name (you had self.hovered here but self.is_hovered below)
        self.is_hovered = False 
        
        # Setup the sound manager
        self.sound_manager = sound_manager if sound_manager else SoundManager()

    def update(self):
        mx, my = get_scaled_mouse_pos()
        
        # Check if the mouse is currently over the button
        currently_hovered = self.rect.collidepoint((mx, my))
        
        # Only play the sound if it JUST became hovered (prevents continuous noise)
        if currently_hovered and not self.is_hovered:
            vol = settings_state.get("sound_volume")
            self.sound_manager.play_sfx("hover")
            
        # Update the state
        self.is_hovered = currently_hovered

    def draw(self, surface):
        # Use the consistent self.is_hovered variable
        img_to_draw = self.hover_image if (self.is_hovered and self.hover_image) else self.image
        if img_to_draw:
            surface.blit(img_to_draw, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = get_scaled_mouse_pos()
            
            if self.rect.collidepoint((mx, my)):
                # Play the click sound when successfully clicked
                vol = settings_state.get("sound_volume")
                self.sound_manager.play_sfx("click")
                return True
        return False