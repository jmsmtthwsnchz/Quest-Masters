import pygame
import sys
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

    def switch_screen(self, name):
        self.current = name

    def run(self):
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
                    else:
                        self.current = "main"

            self.screens[self.current].update(events)
            self.screens[self.current].draw()

            pygame.display.flip()
            CLOCK.tick(FPS)

if __name__ == "__main__":
    App().run()
