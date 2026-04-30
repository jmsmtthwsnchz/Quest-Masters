import pygame
from config import SCREEN, DESIGN_W, DESIGN_H, settings_state, s_x, s_y
from utils import load_image
from ui.buttons import ImageButton
from ui.sliders import Slider

class SettingsMenu:
    def __init__(self, switch_func):
        self.switch_screen = switch_func
        self.return_to = "main"

        self.bg = load_image("main_menu_imgs/settings_bg.png", alpha=False, scale=(DESIGN_W, DESIGN_H))
        self.branch_img = load_image("main_menu_imgs/tree_branch.png")
        self.post_img = load_image("main_menu_imgs/post.png", scale=(750, 918), rotate=-50)
        self.skull_img = load_image("main_menu_imgs/skull.png", scale=(330, 200), rotate=18)
        self.title_img = load_image("main_menu_imgs/settings_title.png", scale=(480, 185), rotate=-3)
        self.music_txt = load_image("main_menu_imgs/music_post.png", scale=(350, 160), rotate=-2)
        self.sound_txt = load_image("main_menu_imgs/sounds_post.png", scale=(350,160), rotate=4)

        back_img = load_image("main_menu_imgs/back.png", scale=(450, 180), rotate=-3)
        back_hover = load_image("main_menu_imgs/back_hover.png", scale=(450, 180), rotate=-3)

        self.music_slider = Slider(
            645, 400, 570, settings_state["music_volume"], self.branch_img,
            gif_filename="main_menu_imgs/fire_knob.gif", gif_scale=(220, 220), stick_offset_y=62, speed_factor=0.8
        )
        self.sound_slider = Slider(
            645, 640, 570, settings_state["sound_volume"], self.branch_img,
            gif_filename="main_menu_imgs/fire_knob.gif", gif_scale=(220, 220), rotate=181, stick_offset_y=50, speed_factor=0.8
        )
        self.back_btn = ImageButton(100, 800, back_img, back_hover)

    def update(self, events):
        self.back_btn.update()
        
        for event in events:
            self.music_slider.handle_event(event)
            self.sound_slider.handle_event(event)

            settings_state["music_volume"] = self.music_slider.value
            settings_state["sound_volume"] = self.sound_slider.value

            if self.back_btn.is_clicked(event):
                self.switch_screen(self.return_to)

    def draw(self):
        if self.bg: SCREEN.blit(self.bg, (0, 0))
        if self.post_img: SCREEN.blit(self.post_img, (s_x(-250), s_y(15)))
        if self.skull_img: SCREEN.blit(self.skull_img, (s_x(200), s_y(-50)))
        if self.title_img: SCREEN.blit(self.title_img, (s_x(205), s_y(160)))
        if self.music_txt: SCREEN.blit(self.music_txt, (s_x(175), s_y(370)))
        if self.sound_txt: SCREEN.blit(self.sound_txt, (s_x(130), s_y(600)))

        self.music_slider.draw(SCREEN)
        self.sound_slider.draw(SCREEN)
        self.back_btn.draw(SCREEN)