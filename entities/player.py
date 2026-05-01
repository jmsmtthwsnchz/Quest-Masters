import pygame
from utils import load_image
from config import s_x, s_y, s_g
from logic.inventory import Inventory

class Player(pygame.sprite.Sprite):
    def __init__(self, startx, starty, gender="male"):
        super().__init__()
        
        self.gender = gender
        
        self.CLEFT = [load_image(f"resource/character/movement/{self.gender}/l{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CRIGHT = [load_image(f"resource/character/movement/{self.gender}/r{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CUP = [load_image(f"resource/character/movement/{self.gender}/u{i}.png", scale=(145, 145)) for i in range(1, 5)]
        self.CDOWN = [load_image(f"resource/character/movement/{self.gender}/d{i}.png", scale=(145, 145)) for i in range(1, 5)]

        self.LOADEDrSlash = []
        self.LOADEDlSlash = []
        for i in range(1, 7):
            r_img = load_image(f"resource/character/slash/{self.gender}/atk{i}.png", scale=(135, 135))
            l_img = load_image(f"resource/character/slash/{self.gender}/atk{i}L.png", scale=(135, 135))
            if r_img: self.LOADEDrSlash.append(r_img)
            if l_img: self.LOADEDlSlash.append(l_img) 

        if not self.LOADEDrSlash:
            fallback = pygame.Surface((150, 150))
            fallback.fill((255, 255, 0))
            self.LOADEDrSlash = [fallback] * 6
            self.LOADEDlSlash = [fallback] * 6

        self.slashframe = 0
        self.slashing = False

        # Movement State
        self.movingleft = False
        self.movingright = False
        self.movingup = False
        self.movingdown = False
        self.moveframe = 0
        self.slashframe = 0
        self.slashing = False
        self.last_direction = "DOWN"

        # Animation Speeds
        self.slashanimation_speed = 3
        self.animation_timer = 0
        self.moveanimation_speed = 10
        self.moveanimation_time = 0

        self.last_hit_time = 0
        self.invulnerability_duration = 2000
        self.is_invulnerable = False
        self.visible = True
        self.flicker_timer = 0
        self.flicker_speed = 10

        # Set starting image and rect
        self.image = self.CDOWN[0] 
        self.rect = self.image.get_rect()
        self.rect.topleft = (s_x(startx), s_y(starty))

        self.hitbox = pygame.Rect(0, 0, int(self.rect.width * 0.5), 20)
        self.hitbox.midbottom = (self.rect.centerx, self.rect.bottom - 15)

        # Setup slash rect
        self.imageslash = self.LOADEDrSlash[0]
        self.slashrect = self.imageslash.get_rect()

        self.speed = s_g(4)
        self.is_dead = False
        self.inventory = Inventory(size=12)

    def update(self, *args):
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

            if self.last_direction == "LEFT":
                self.imageslash = self.LOADEDlSlash[0]
            else:
                self.imageslash = self.LOADEDrSlash[0]
            self.slashrect.center = self.rect.center

    def movementanimation(self):
        if self.is_dead:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time < self.invulnerability_duration:
            self.flicker_timer += 1
            if self.flicker_timer >= self.flicker_speed:
                self.visible = not self.visible
                self.flicker_timer = 0
            self.image.set_alpha(255 if self.visible else 100)
        else:
            self.image.set_alpha(255)
            self.visible = True
        
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

                if self.slashframe >= len(self.LOADEDrSlash):
                    self.slashing = False
                    self.slashframe = 0 
                else:
                    if self.last_direction == "LEFT":
                        self.imageslash = self.LOADEDlSlash[self.slashframe]
                    else:
                        self.imageslash = self.LOADEDrSlash[self.slashframe]

    def shadow(self):
        shadow = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        shadow.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return shadow
