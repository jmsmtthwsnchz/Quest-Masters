import pygame
from config import SCREEN, DESIGN_W, DESIGN_H, CLOCK
from utils import load_image

class SplashScreen:
    def __init__(self, switch_func):
        self.switch_screen = switch_func

        # Load your generated welcome screen image
        self.image = load_image("resource/welcome_screen.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        
        # Timing (in milliseconds)
        self.start_time = pygame.time.get_ticks()
        self.initial_delay = 1500  # 1.5 seconds of black
        self.fade_duration = 2000   # 2 seconds to fade in/out
        self.stay_duration = 4000   # 4 seconds of full visibility
        
        self.alpha = 0
        self.phase = "INITIAL_BLACK" # INITIAL_BLACK, FADE_IN, STAY, FADE_OUT

    def update(self, events):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        if self.phase == "INITIAL_BLACK":
            if elapsed > self.initial_delay:
                self.phase = "FADE_IN"
                self.start_time = now # Reset timer for next phase

        elif self.phase == "FADE_IN":
            # Calculate alpha based on percentage of duration complete
            self.alpha = min(255, (elapsed / self.fade_duration) * 255)
            if elapsed > self.fade_duration:
                self.phase = "STAY"
                self.start_time = now

        elif self.phase == "STAY":
            self.alpha = 255
            if elapsed > self.stay_duration:
                self.phase = "FADE_OUT"
                self.start_time = now

        elif self.phase == "FADE_OUT":
            self.alpha = max(0, 255 - (elapsed / self.fade_duration) * 255)
            if elapsed > self.fade_duration:
                # Sequence finished! Move to character selection
                self.switch_screen("main")

    def draw(self):
        SCREEN.fill((0, 0, 0)) # Background is always black
        if self.image and self.alpha > 0:
            self.image.set_alpha(int(self.alpha))
            SCREEN.blit(self.image, (0, 0))