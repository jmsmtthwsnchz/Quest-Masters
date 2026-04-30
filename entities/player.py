# entities/player.py
import pygame
from utils import load_image
from config import s_x, s_y, s_g

class Player(pygame.sprite.Sprite):
    def __init__(self, startx, starty):
        super().__init__()
        
        self.CLEFT = [load_image(f"resource/character/movement/l{i}.png") for i in range(1, 5)]
        self.CRIGHT = [load_image(f"resource/character/movement/r{i}.png") for i in range(1, 5)]
        self.CUP = [load_image(f"resource/character/movement/u{i}.png") for i in range(1, 5)]
        self.CDOWN = [load_image(f"resource/character/movement/d{i}.png") for i in range(1, 5)]

        # Movement State
        self.movingleft = False
        self.movingright = False
        self.movingup = False
        self.movingdown = False
        self.moveframe = 0

        # Slash State
        self.SCALEDLOADEDSLASH = []
        for i in range(1, 9):
            img = load_image(f"resource/slash/S{i}.png", scale=(300, 300))
            if img:
                self.SCALEDLOADEDSLASH.append(img)
                
        if not self.SCALEDLOADEDSLASH:
            print("WARNING: Slash images missing! Using yellow box.")
            fallback = pygame.Surface((150, 150))
            fallback.fill((255, 255, 0)) 
            self.SCALEDLOADEDSLASH = [fallback] * 8 

        self.slashframe = 0
        self.slashing = False

        # Animation Speeds
        self.slashanimation_speed = 3
        self.animation_timer = 0
        self.moveanimation_speed = 10
        self.moveanimation_time = 0

        # Set starting image and rect
        self.image = self.CDOWN[0] 
        self.rect = self.image.get_rect()
        self.rect.topleft = (s_x(startx), s_y(starty))

        # Setup slash rect
        self.imageslash = self.SCALEDLOADEDSLASH[0]
        self.slashrect = self.imageslash.get_rect()

        self.last_direction = "DOWN"
        self.speed = s_g(5)

        self.is_dead = False

    def update(self):
        self.handle_input()
        self.movementanimation()
        self.attackanimation()

    def handle_input(self):

        if self.is_dead:
            self.movingleft = self.movingleft = self.movingup = self.movingdown = False
            return
        
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        self.movingleft = self.movingright = self.movingup = self.movingdown = False

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.movingleft = True
            self.last_direction = "LEFT"
        elif keys[pygame.K_d]:
            self.rect.x += self.speed
            self.movingright = True
            self.last_direction = "RIGHT"
        elif keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.movingup = True
            self.last_direction = "UP"
        elif keys[pygame.K_s]:
            self.rect.y += self.speed
            self.movingdown = True
            self.last_direction = "DOWN"

        # Attack Input
        if mouse[0] and not self.slashing:
            self.slashing = True
            self.slashframe = 0
            self.animation_timer = 0 
            self.imageslash = self.SCALEDLOADEDSLASH[0] 

            self.slashrect.center = self.rect.center

            print("SLASH TRIGGERED! Drawing Frame 0...")

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.top < 0: self.rect.top = 0

    def movementanimation(self):
        if self.is_dead:
            return
        
        if self.movingleft or self.movingright or self.movingup or self.movingdown:
            self.moveanimation_time += 1
            if self.moveanimation_time >= self.moveanimation_speed:
                self.moveanimation_time = 0
                self.moveframe = (self.moveframe + 1) % 4
            
            if self.movingleft: self.image = self.CLEFT[self.moveframe]
            elif self.movingright: self.image = self.CRIGHT[self.moveframe]
            elif self.movingup: self.image = self.CUP[self.moveframe]
            elif self.movingdown: self.image = self.CDOWN[self.moveframe]
        else:
            self.moveframe = 0
            if self.last_direction == "LEFT": self.image = self.CLEFT[0]
            elif self.last_direction == "RIGHT": self.image = self.CRIGHT[0] 
            elif self.last_direction == "UP": self.image = self.CUP[0]       
            elif self.last_direction == "DOWN": self.image = self.CDOWN[0]   

    def attackanimation(self):
        if self.slashing and self.imageslash:
            self.slashrect.center = self.rect.center

            self.animation_timer += 1 
            if self.animation_timer >= self.slashanimation_speed:
                self.animation_timer = 0
                self.slashframe += 1

                if self.slashframe >= len(self.SCALEDLOADEDSLASH):
                    self.slashing = False
                    self.slashframe = 0 
                else:
                    self.imageslash = self.SCALEDLOADEDSLASH[self.slashframe]