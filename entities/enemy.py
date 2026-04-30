# entities/enemy.py
import pygame
from utils import load_image
from config import s_x, s_y, s_g

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, name, patrol_distance=300):
        super().__init__()
        self.name = name
        self.direction = "DOWN"
        self.frame = 0
        self.speed = s_g(2)

        # 1. Load Data cleanly using your system
        self.animations = {"LEFT": [], "RIGHT": [], "UP": [], "DOWN": [], "DEATH": []}
        
        for action in self.animations.keys():
            for i in range(1, 6):
                # IMPORTANT: Adjust this path to wherever you put the enemy images!
                path = f"resource/enemies/{name}/{action}/{i}.png" 
                img = load_image(path, scale=(125, 125))
                if img:
                    self.animations[action].append(img)
        
        # Fallback if images fail to load (draws a red square so you can still test)
        if self.animations[self.direction]:
            self.image = self.animations[self.direction][0]
        else:
            self.image = pygame.Surface((s_g(50), s_g(50)))
            self.image.fill((255, 0, 0))
            
        self.rect = self.image.get_rect(center=(s_x(x), s_y(y)))

        # 2. Patrol logic variables
        self.start_x = self.rect.x
        self.end_x = self.rect.x + s_x(patrol_distance)
        self.target_x = self.end_x

        self.anim_timer = 0
        self.anim_speed = 5

        self.is_dying = False
        self.death_frame = 0
        self.death_timer = 0

        self.detection_radius = 400
        self.attack_range = 40
        self.is_chasing = False
        self.reaction_timer = 0
        self.has_spotted_player = False

    def update(self, player):
        if self.is_dying:
            if self.animations["DEATH"]:
                self.death_timer += 1
                if self.death_timer >= self.anim_speed:
                    self.death_timer = 0
                    self.death_frame += 1

                    if self.death_frame >= len(self.animations["DEATH"]):
                        self.kill()
                    else:
                        self.image = self.animations["DEATH"][self.death_frame]
            else:
                self.kill()

            return
        
        #Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        
        #State logic detect pleyer
        if distance < self.detection_radius:
            if not self.has_spotted_player:
                self.has_spotted_player = True
                self.reaction_timer = 20

            if self.reaction_timer > 0:
                self.reaction_timer -= 1
                return
            self.is_chasing = True
        else:
            self.is_chasing = False
            self.has_spotted_player = False

        #Movement Logic
        if self.is_chasing:
            if distance > self.attack_range:
                if distance != 0:
                    self.rect.x += (dx / distance) * self.speed
                    self.rect.y += (dy / distance) * self.speed

                if abs(dx) > abs(dy):
                    self.direction = "RIGHT" if dx > 0 else "LEFT"
                else:
                    self.direction = "DOWN" if dy > 0 else "UP"
        else:
            # Move towards the target
            if self.rect.x < self.target_x:
                self.rect.x += self.speed
                self.direction = "RIGHT"
            elif self.rect.x > self.target_x:
                self.rect.x -= self.speed
                self.direction = "LEFT"

            # Turn around if we reached the patrol point
            if abs(self.rect.x - self.target_x) <= self.speed:
                self.target_x = self.start_x if self.target_x == self.end_x else self.end_x
            pass

        # Animate walking
        if self.animations[self.direction]:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame = (self.frame + 1) % len(self.animations[self.direction])
                self.image = self.animations[self.direction][self.frame]

    def hit(self):
        if not self.is_dying:
            self.is_dying = True
            self.death_frame = 0
            self.death_timer = 0

            if self.animations["DEATH"]:
                self.image = self.animations["DEATH"][0]
    
    def shadow(self):
        shadow = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

        shadow.fill((0,0,0, 100))

        shadow.blit(self.iamge, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return shadow
