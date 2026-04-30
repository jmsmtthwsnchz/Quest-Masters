import pygame
import ctypes
import os

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

#Display Settings
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
DESIGN_W, DESIGN_H = 1920, 1080
SCALE_X, SCALE_Y = WIDTH / DESIGN_W, HEIGHT / DESIGN_H
G_SCALE = min(SCALE_X, SCALE_Y)

#Scaling Functions
def s_x(val): return int(val * SCALE_X)
def s_y(val): return int(val * SCALE_Y)
def s_g(val): return int(val * G_SCALE)

#Create Global Screen
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE, 32)
pygame.display.set_caption("Universal Adventure Game")

#Colors & Clock
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
CLOCK = pygame.time.Clock()
FPS = 60

#Global State
settings_state = {"music_volume": 0.5, "sound_volume": 0.5}
script_dir = os.path.dirname(os.path.abspath(__file__))
