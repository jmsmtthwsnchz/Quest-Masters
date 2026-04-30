import pygame
from config import SCREEN, BLACK, WHITE
from utils import load_image
from entities.player import Player
from entities.enemy import Creature
from ui.health import HealthBar

class GameScreen:
    def __init__(self, switch_func):
        self.switch_screen = switch_func
        
        from config import DESIGN_W, DESIGN_H
        self.bg_image = load_image("resource/stage1map.png", alpha=False, scale=(DESIGN_W * 3, DESIGN_H * 3))
        
        # We don't need to spawn anything here anymore. 
        # Just call reset() and let it do all the heavy lifting!
        self.reset()

    def reset(self):
        # 1. Clear out old sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()

        # 2. Spawn Player
        self.player = Player(2000, 2000)
        self.all_sprites.add(self.player)

        # 3. Spawn UI
        self.health_bar = HealthBar(1820, 20)

        # 4. Spawn Enemies
        spawnset = {
            (1500, 600): "snake",
            (1000, 700): "camel",
        }
        for position, creature_name in spawnset.items():
            enemy = Creature(position[0], position[1], creature_name)
            self.all_sprites.add(enemy)
            self.enemies_group.add(enemy)

        self.last_damage_time = 0

    def update(self, events):
        now = pygame.time.get_ticks()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.reset()
                self.switch_screen("level_select")

        # 1. THE PERMANENT DEATH MONITOR
        # This checks if the hp_index has reached the final '0' health frame
        is_already_dead = self.health_bar.hp_index >= len(self.health_bar.frames) - 1
        
        if is_already_dead or self.player.is_dead:
            self.player.is_dead = True
            # Force movement to stop immediately
            self.player.movingleft = self.player.movingright = False
            self.player.movingup = self.player.movingdown = False
            
            # Rotate image to sideways
            self.player.image = pygame.transform.rotate(self.player.image, 90)
            
            # Draw the death frame and update display
            self.draw()
            pygame.display.flip()
            
            # Dramatic pause
            pygame.time.delay(1500)
            
            # Reset and leave level
            self.reset()
            self.switch_screen("level_select")
            return # Stop all other logic

        # 2. Standard Updates (Only runs if alive)
        self.all_sprites.update()

        # 3. Collision Logic
        taken_hits = pygame.sprite.spritecollide(self.player, self.enemies_group, False, pygame.sprite.collide_rect_ratio(0.6))
        
        if taken_hits and (now - self.last_damage_time > 1000):
            # take_damage() advances the bar
            self.health_bar.take_damage() 
            self.last_damage_time = now
            
            # Knockback only if not dying
            if not self.player.is_dead:
                self.player.rect.x -= self.player.speed * 5

        # 4. Attack logic
        if self.player.slashing and self.player.imageslash:
            for enemy in self.enemies_group:
                if self.player.slashrect.inflate(-20, -20).colliderect(enemy.rect):
                    enemy.hit()

    def draw(self):
        SCREEN.fill(BLACK)
        offset_x = self.player.rect.centerx - (1920 // 2)
        offset_y = self.player.rect.centery - (1080 // 2)

        if self.bg_image:
            map_w = self.bg_image.get_width()
            map_h = self.bg_image.get_height()

            offset_x = max(0, min(offset_x, map_w - 1920))
            offset_y = max(0, min(offset_y, map_h - 1080))

            SCREEN.blit(self.bg_image, (-offset_x, -offset_y))

        for sprite in self.all_sprites:
            SCREEN.blit(sprite.image, (sprite.rect.x - offset_x, sprite.rect.y - offset_y))

        if getattr(self.player, 'slashing', False) and self.player.imageslash:
            SCREEN.blit(self.player.imageslash, (self.player.slashrect.x - offset_x, self.player.slashrect.y - offset_y))

        SCREEN.blit(self.health_bar.image, self.health_bar.rect)

