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
WIDTH, HEIGHT = 1920, 1080
DESIGN_W, DESIGN_H = 1920, 1080
SCALE_X, SCALE_Y = WIDTH / DESIGN_W, HEIGHT / DESIGN_H
G_SCALE = min(SCALE_X, SCALE_Y)

#Scaling Functions
def s_x(val): return int(val * SCALE_X)
def s_y(val): return int(val * SCALE_Y)
def s_g(val): return int(val * G_SCALE)
def get_scaled_mouse_pos():
    mx, my = pygame.mouse.get_pos()

    window_w, window_h = WINDOW.get_size()
    
    ratio_x = WIDTH / window_w
    ratio_y = HEIGHT / window_h
    
    return int(mx * ratio_x), int(my * ratio_y)

#Create Global Screen
WINDOW = pygame.display.set_mode((1280, 720), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, 32)
pygame.display.set_caption("Universal Adventure Game")

SCREEN = pygame.Surface((WIDTH, HEIGHT))

#Colors & Clock
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
CLOCK = pygame.time.Clock()
FPS = 60

#Global State
settings_state = {"music_volume": 0.5, "sound_volume": 0.5}
script_dir = os.path.dirname(os.path.abspath(__file__))
