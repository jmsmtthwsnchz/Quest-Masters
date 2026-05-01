import pygame
import sys
import config
from config import CLOCK, FPS
from screens.main_menu import MainMenu
from screens.settings import SettingsMenu
from screens.level_select import LevelSelect
from screens.game_screen import GameScreen

class App:
    def __init__(self):
        self.screens = {
            "main": MainMenu(self.switch_screen),
            "settings": SettingsMenu(self.switch_screen),
            "level_select": LevelSelect(self.switch_screen),
            "game": GameScreen(self.switch_screen)
        }
        self.current = "main"

    def switch_screen(self, name, **kwargs):
        # 1. Save the PREVIOUS screen before changing current
        if name == "settings":
            self.screens["settings"].return_to = self.current
        
        # 2. Now update to the new screen
        self.current = name
        
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
                    elif self.current == "level_select":
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
