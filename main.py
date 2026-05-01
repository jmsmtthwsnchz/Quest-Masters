import pygame
import sys
import config
import os
from config import CLOCK, FPS, settings_state, script_dir
from screens.main_menu import MainMenu
from screens.settings import SettingsMenu
from screens.game_select import GameSelect
from screens.game_screen import GameScreen
from screens.splash_screen import SplashScreen
from screens.char_select import CharacterSelect
from screens.cutscene import CutsceneScreen
from sound_manager import SoundManager

pygame.init()
pygame.mixer.init()

class App:
    def __init__(self):
        self.sound_manager = SoundManager()
        self.screens = {
            "splash": SplashScreen(self.switch_screen),
            "char_select": CharacterSelect(self.switch_screen),
            "cutscene": CutsceneScreen(self.switch_screen, self.sound_manager),
            "main": MainMenu(self.switch_screen, self.sound_manager),
            "settings": SettingsMenu(self.switch_screen, self.sound_manager),
            "game_select": GameSelect(self.switch_screen, self.sound_manager),
            "game": GameScreen(self.switch_screen, self.sound_manager)
        }
        self.current = "splash"

        default_bg_path = os.path.join(script_dir, "assets", "sounds", "default_bg.mp3")
        try:
            pygame.mixer.music.load(default_bg_path)
            pygame.mixer.music.set_volume(settings_state["music_volume"])
            pygame.mixer.music.play(-1)
        except pygame.error:
            print(f"Initial music load failed. Check: {default_bg_path}")

    def switch_screen(self, name, **kwargs):
        # 1. Remember where we came from
        prev_screen = self.current
        
        if name == "settings":
            self.screens["settings"].return_to = self.current

        # 2. Update to the new screen
        self.current = name

        # --- MUSIC LOGIC START ---
        # Stop the intro music when moving from splash to char_select

        import pygame # Ensure pygame is imported if not globally available
        if prev_screen == "splash" and name == "char_select":
            import pygame 
            pygame.mixer.music.fadeout(1000) 

        # FIX: Instantly kill all background music when a cutscene starts
        elif name == "cutscene":
            import pygame
            pygame.mixer.music.stop()

        # If returning to menus from the game, switch back to menu music
        elif prev_screen == "game" and name in ["main", "game_select"]:
            self.sound_manager.play_music(self.sound_manager.menu_music, settings_state["music_volume"])
            
        # If arriving at the main menu from character selection, start menu music
        elif prev_screen == "char_select" and name == "main":
            self.sound_manager.play_music(self.sound_manager.menu_music, settings_state["music_volume"])        # --- MUSIC LOGIC END ---

        # 3. Trigger resets
        if hasattr(self.screens[self.current], 'reset'):
            self.screens[self.current].reset(**kwargs)
        elif self.current == "settings":
            self.switch_screen(self.screens["settings"].return_to)

    def run(self):
        import config
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.current == "main":
                        pygame.quit()
                        sys.exit()
                    elif self.current == "settings":
                        self.switch_screen(self.screens["settings"].return_to)
                    elif self.current == "game_select":
                        self.current = "main"
                    elif self.current == "game":
                        pass
                elif e.type == pygame.VIDEORESIZE:
                    config.WINDOW = pygame.display.set_mode(
                        (e.w, e.h),
                        pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE,
                        32
                    )

            self.screens[self.current].update(events)
            self.screens[self.current].draw()

            scaled_canvas = pygame.transform.scale(config.SCREEN, config.WINDOW.get_size())

            config.WINDOW.blit(scaled_canvas, (0, 0))
            pygame.display.flip()

            CLOCK.tick(FPS)

if __name__ == "__main__":
    App().run()
