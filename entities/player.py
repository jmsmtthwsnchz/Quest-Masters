import pygame
from utils import load_image
from config import s_x, s_y, s_g
from logic.inventory import Inventory

class Player(pygame.sprite.Sprite):
    def __init__(self, startx, starty):
        super().__init__()
        
        self.CLEFT = [load_image(f"resource/character/movement/l{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CRIGHT = [load_image(f"resource/character/movement/r{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CUP = [load_image(f"resource/character/movement/u{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CDOWN = [load_image(f"resource/character/movement/d{i}.png", scale=(145, 145)) for i in range(1, 5)]

        # Movement State
        self.movingleft = False
        self.movingright = False
        self.movingup = False
        self.movingdown = False
        self.moveframe = 0

        # Slash State
        self.SCALEDLOADEDSLASH = []
        for i in range(1, 9):
            img = load_image(f"resource/slash/S{i}.png", scale=(135, 135))
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

        self.inventory = Inventory(size=12)

        # Create the Hitbox (Using the Full Body style or Boots style)
        #self.hitbox = pygame.Rect(0, 0, int(self.rect.width * 0.5), int(self.rect.height * 0.8))
        #self.hitbox.midbottom = self.rect.midbottom
        self.hitbox = pygame.Rect(0, 0, int(self.rect.width * 0.5), 20)
        self.hitbox.midbottom = self.rect.midbottom

        # Setup slash rect
        self.imageslash = self.SCALEDLOADEDSLASH[0]
        self.slashrect = self.imageslash.get_rect()

        self.last_direction = "DOWN"
        self.speed = s_g(4)

        self.is_dead = False

    def update(self, *args):
        self.handle_input()
        self.movementanimation()
        self.attackanimation()

    def handle_input(self, map_width=None, map_height=None, obstacles=None):
        if self.is_dead:
            self.movingleft = self.movingright = self.movingup = self.movingdown = False
            return
        
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        
        if obstacles is None:
            obstacles = []

        # Reset movement states
        self.movingleft = self.movingright = self.movingup = self.movingdown = False
        dx = 0
        dy = 0

        # --- Calculate Intended Movement ---
        if keys[pygame.K_a]:
            dx = -self.speed
            self.movingleft = True
            self.last_direction = "LEFT"
        elif keys[pygame.K_d]:
            dx = self.speed
            self.movingright = True
            self.last_direction = "RIGHT"

        if keys[pygame.K_w]:
            dy = -self.speed
            self.movingup = True
            self.last_direction = "UP"
        elif keys[pygame.K_s]:
            dy = self.speed
            self.movingdown = True
            self.last_direction = "DOWN"

        # --- 1. Apply X Movement & Resolve X Collisions ---
        if dx != 0:
            self.hitbox.x += dx
            for wall in obstacles:
                if self.hitbox.colliderect(wall):
                    # TOLERANCE CHECK: We only snap if the penetration depth is tiny.
                    # If it's larger than your speed, you are safely sliding alongside a parallel wall!
                    if dx > 0 and (self.hitbox.right - wall.left) <= self.speed + 5:
                        self.hitbox.right = wall.left
                    elif dx < 0 and (wall.right - self.hitbox.left) <= self.speed + 5:
                        self.hitbox.left = wall.right

        # --- 2. Apply Y Movement & Resolve Y Collisions ---
        if dy != 0:
            self.hitbox.y += dy
            for wall in obstacles:
                if self.hitbox.colliderect(wall):
                    if dy > 0 and (self.hitbox.bottom - wall.top) <= self.speed + 5:
                        self.hitbox.bottom = wall.top
                    elif dy < 0 and (wall.bottom - self.hitbox.top) <= self.speed + 5:
                        self.hitbox.top = wall.bottom

        # --- Map Boundary Checks (Using Hitbox) ---
        if self.hitbox.left < 0: self.hitbox.left = 0
        if self.hitbox.top < 0: self.hitbox.top = 0
        if map_width and self.hitbox.right > map_width:
            self.hitbox.right = map_width
        if map_height and self.hitbox.bottom > map_height:
            self.hitbox.bottom = map_height

        # --- GLUE VISUAL SPRITE TO THE HITBOX ---
        self.rect.midbottom = self.hitbox.midbottom

        # --- Attack Input ---
        if mouse[0] and not self.slashing:
            self.slashing = True
            self.slashframe = 0
            self.animation_timer = 0 
            self.imageslash = self.SCALEDLOADEDSLASH[0] 
            self.slashrect.center = self.rect.center

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

    def shadow(self):
        shadow = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        shadow.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return shadow
