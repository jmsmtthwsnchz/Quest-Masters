import pygame
import os
from config import script_dir, settings_state

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.path = os.path.join(script_dir, "assets", "sounds")

        self.menu_music = os.path.join(self.path, "menu_music.ogg.mp3")
        self.game_music = os.path.join(self.path, "game_music.ogg.mp3")

        self.sounds = {
            "hover":    pygame.mixer.Sound(os.path.join(self.path, "hover.wav.mp3")),
            "click":    pygame.mixer.Sound(os.path.join(self.path, "click.wav.mp3")),
            "play":     pygame.mixer.Sound(os.path.join(self.path, "start.wav.mp3")),
            "shop":     pygame.mixer.Sound(os.path.join(self.path, "shop.wav.mp3")),
            "heal":     pygame.mixer.Sound(os.path.join(self.path, "heal_chime.wav")),
            "slash":    pygame.mixer.Sound(os.path.join(self.path, "sword_swoosh.wav")),
            "start":    pygame.mixer.Sound(os.path.join(self.path, "game_start.wav"))
        }

    def play_music(self, music_path, volume=0.5):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Music Error: {e}")

    # Remove the required volume argument and use the global property[cite: 11]
    def play_sfx(self, name):
        if name in self.sounds:
            current_vol = settings_state.get("sound_volume", 1.0)
            self.sounds[name].set_volume(current_vol)
            self.sounds[name].play()
            