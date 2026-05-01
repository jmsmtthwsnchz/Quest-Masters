import pygame
import os
from pyvidplayer2 import Video
from config import SCREEN, DESIGN_W, DESIGN_H, script_dir, settings_state

class CutsceneScreen:
    def __init__(self, switch_func, sound_manager):
        self.switch_screen = switch_func
        self.sound_manager = sound_manager
        self.video = None
        self.char_type = None

    def reset(self, char_type=None, **kwargs):
        self.char_type = char_type
        
        # 1. Stop any menu music before the video starts
        pygame.mixer.music.stop()

        # 2. Determine which video to play based on character choice
        if char_type == "percival":
            video_name = "BOY.mp4"
        else:
            video_name = "GIRL.mp4" # Replace with your actual filename
            
        video_path = os.path.join(script_dir, "assets", "videos", video_name)

        # 3. Load the video
        try:
            self.video = Video(video_path)
            # Resize video to fit your screen perfectly
            self.video.resize((DESIGN_W, DESIGN_H))

            self.video.set_volume(settings_state["music_volume"])
        except Exception as e:
            print(f"Video Load Error ({video_path}): {e}")
            # If the video fails to load (missing file, etc.), skip straight to the game
            self.skip()

    def update(self, events):
        if not self.video:
            return
            
        for event in events:
            # Allow skipping the cutscene with ESC, Space, or Left-Click
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                self.skip()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.skip()
        
        # Auto-skip to the game when the video finishes playing naturally
        if not self.video.active:
            self.skip()

    def draw(self):
        SCREEN.fill((0, 0, 0)) # Black background
        if self.video and self.video.active:
            # Draw the current video frame to the main Pygame screen
            self.video.draw(SCREEN, (0, 0), force_draw=True)
            
    def skip(self):
        # Clean up the video memory
        if self.video:
            self.video.close()
            self.video = None
        
        # Jump into the game, passing the stage_index and the char_type!
        self.switch_screen("game", stage_index=0, char_type=self.char_type)