import pygame
import random
from config import SCREEN, BLACK, WHITE
from utils import load_image
from entities.player import Player
from entities.enemy import Creature
from ui.health import HealthBar

class GameScreen:
    def __init__(self, switch_func):
        self.switch_screen = switch_func

        self.current_stage_idx = 0
        self.current_difficulty = None

        self.bg_image = None
        
        # Load UI Icons once
        self.ui_bag_icon = load_image("resource/inventory_imgs/bag_icon.png", scale=(80, 80))
        self.ui_slot_bg = load_image("resource/inventory_imgs/slot_icon.png", scale=(100, 100))
        
        self.reset()

    def reset(self, stage_index=None, difficulty=None, **kwargs):

        # CHANGE 2: Only update the stored variables if NEW data is provided
        if stage_index is not None:
            self.current_stage_idx = stage_index
        if difficulty is not None:
            self.current_difficulty = difficulty

        # CHANGE 3: The "Resume" Check
        # If we already have a player and NO new stage_index was passed, 
        # it means we are just returning from Settings. DO NOT wipe the level.
        if hasattr(self, 'player') and self.player is not None and stage_index is None:
            self.is_paused = True # Keep the system menu open if you like
            return
        
        # --- FROM HERE DOWN: ONLY RUNS FOR FRESH LEVEL STARTS ---
        
        # 1. Clear out old sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()

        # 2. Dynamic Map & Obstacle Loading
        from map_data import (
            STAGE_1_LEVEL_1_OBSTACLES, STAGE_1_LEVEL_2_OBSTACLES, STAGE_1_LEVEL_3_OBSTACLES,
            STAGE_2_LEVEL_1_OBSTACLES, STAGE_2_LEVEL_2_OBSTACLES, STAGE_2_LEVEL_3_OBSTACLES
        )
        
        from config import DESIGN_W, DESIGN_H
        
        map_files = [
            "resource/stg1level1map.png", "resource/stg1level2map.jpg", "resource/stg1level3map.jpg",
            "resource/stg2level1map.png", "resource/stg2level2map.png", "resource/stg2level3map.png"
        ]

        obstacle_sets = [
            STAGE_1_LEVEL_1_OBSTACLES, STAGE_1_LEVEL_2_OBSTACLES, STAGE_1_LEVEL_3_OBSTACLES,
            STAGE_2_LEVEL_1_OBSTACLES, STAGE_2_LEVEL_2_OBSTACLES, STAGE_2_LEVEL_3_OBSTACLES
        ]

        # Use self.current_stage_idx (which we updated at the top) to pick the map
        idx = max(0, min(self.current_stage_idx, len(map_files) - 1))
        
        self.bg_image = load_image(map_files[idx], alpha=False, scale=(DESIGN_W * 3.5, DESIGN_H * 3.5))
        self.obstacles = obstacle_sets[idx]

        # 3. Initialize Player & UI
        self.player = Player(2000, 2000)
        self.all_sprites.add(self.player)
        self.health_bar = HealthBar(1820, 20)

        # 4. Difficulty-Based Enemy Spawning using self.current_difficulty
        enemy_types = ["snake", "camel"]
        
        if self.current_difficulty == "hard":
            enemy_count = 20
        elif self.current_difficulty == "medium":
            enemy_count = 12
        else:
            enemy_count = 5

        spawn_center_x = 2000
        spawn_center_y = 2000
        spawn_radius = 1200
        
        for i in range(enemy_count):
            safe = False
            attempts = 0

            while not safe and attempts < 100:
                attempts += 1
                rx = random.randint(spawn_center_x - spawn_radius, spawn_center_x + spawn_radius)
                ry = random.randint(spawn_center_y - spawn_radius, spawn_center_y + spawn_radius)
                
                # Test location with a dummy hitbox[cite: 9]
                test_hitbox = pygame.Rect(0, 0, 65, 20)
                from config import s_x, s_y
                test_hitbox.midbottom = (s_x(rx), s_y(ry))
                
                # Check for collisions with walls, other enemies, or the player[cite: 9]
                hit_wall = test_hitbox.collidelist(self.obstacles) != -1
                hit_enemy = any(test_hitbox.colliderect(e.hitbox) for e in self.enemies_group)
                hit_player = test_hitbox.colliderect(self.player.hitbox.inflate(200, 200))

                if not hit_wall and not hit_enemy and not hit_player:
                    enemy = Creature(rx, ry, random.choice(enemy_types))
                    self.all_sprites.add(enemy)
                    self.enemies_group.add(enemy)
                    safe = True
            
            if not safe:
                print(f"WARNING: Could not find spawn point for enemy {i}")

        # 5. Reset Camera and State Variables[cite: 9]
        self.offset_x = 0
        self.offset_y = 0
        self.is_paused = False
        self.show_system_menu = False
        self.show_inventory = False
        self.dev_drawing = False

    def update(self, events):
        now = pygame.time.get_ticks()

        # --- MENU TOGGLES ---
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_system_menu = not self.show_system_menu
                    self.show_inventory = False
                    self.is_paused = self.show_system_menu

                if event.key == pygame.K_e or event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.show_system_menu = False
                    self.is_paused = self.show_inventory

        if self.is_paused:
            self.update_ui_interaction(events)
            return

        # --- DEATH MONITOR ---
        is_already_dead = self.health_bar.hp_index >= len(self.health_bar.frames) - 1
        if is_already_dead or self.player.is_dead:
            self.player.is_dead = True
            self.player.movingleft = self.player.movingright = False
            self.player.movingup = self.player.movingdown = False
            
            # Rotate image to sideways for death animation
            self.player.image = pygame.transform.rotate(self.player.image, 90)
            self.draw()
            pygame.display.flip()
            
            pygame.time.delay(1500)
            self.reset()
            self.switch_screen("level_select")
            return

        # --- GAMEPLAY LOGIC ---
        map_w = self.bg_image.get_width()
        map_h = self.bg_image.get_height()

        self.player.handle_input(map_w, map_h, self.obstacles)
        self.all_sprites.update(self.player, self.obstacles)

        # 1. Hitbox Enemy Collision
        taken_hits = [e for e in self.enemies_group if self.player.rect.inflate(-100, -100).colliderect(e.rect.inflate(-60, -60)) and not getattr(e, 'is_dying', False)]
        
        if taken_hits and (now - self.player.last_hit_time > self.player.invulnerability_duration):
            self.health_bar.take_damage() 
            self.player.last_hit_time = now # Triggers player flicker
            
            # Smart Knockback
            if not self.player.is_dead:
                enemy = taken_hits[0]
                if self.player.hitbox.centerx < enemy.hitbox.centerx:
                    self.player.hitbox.x -= self.player.speed * 8
                else:
                    self.player.hitbox.x += self.player.speed * 8
                    
                if self.player.hitbox.centery < enemy.hitbox.centery:
                    self.player.hitbox.y -= self.player.speed * 8
                else:
                    self.player.hitbox.y += self.player.speed * 8
                
                # Snap visual sprite to the knocked-back hitbox
                self.player.rect.midbottom = self.player.hitbox.midbottom

        # 2. Frame-Perfect Attack Logic
        if self.player.slashing and self.player.slashframe == 3 and self.player.imageslash:
            for enemy in self.enemies_group:
                if self.player.slashrect.inflate(-20, -20).colliderect(enemy.rect):
                    enemy.hit()

        # --- DEV TOOLS (Right Click Map Drawing) ---
        from config import get_scaled_mouse_pos
        mx, my = get_scaled_mouse_pos()
        world_x = mx + self.offset_x
        world_y = my + self.offset_y

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3: 
                self.dev_drawing = True
                self.dev_start = (world_x, world_y)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 3:
                self.dev_drawing = False
                if self.dev_rect:
                    print(f"pygame.Rect({self.dev_rect.x}, {self.dev_rect.y}, {self.dev_rect.width}, {self.dev_rect.height}),")

        if self.dev_drawing:
            width = world_x - self.dev_start[0]
            height = world_y - self.dev_start[1]
            left = self.dev_start[0] if width > 0 else world_x
            top = self.dev_start[1] if height > 0 else world_y
            self.dev_rect = pygame.Rect(int(left), int(top), int(abs(width)), int(abs(height)))

    def update_ui_interaction(self, events):
        from config import get_scaled_mouse_pos, WIDTH, HEIGHT
        mx, my = get_scaled_mouse_pos()
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.show_system_menu:
                    # Resume
                    resume_area = pygame.Rect(0, 0, 220, 60)
                    resume_area.center = (WIDTH//2, HEIGHT//2 - 100)
                    if resume_area.collidepoint((mx, my)):
                        self.show_system_menu = False
                        self.is_paused = False

                    # Settings
                    settings_area = pygame.Rect(0, 0, 220, 60)
                    settings_area.center = (WIDTH // 2, HEIGHT // 2)
                    if settings_area.collidepoint((mx, my)):
                        self.switch_screen("settings")

                    # Quit
                    quit_area = pygame.Rect(0, 0, 220, 60)
                    quit_area.center = (WIDTH//2, HEIGHT//2 + 100)
                    if quit_area.collidepoint((mx, my)):
                        self.reset()
                        self.switch_screen("level_select")

    def draw_ui_button(self, text, x, y, color):
        from config import WHITE
        btn_rect = pygame.Rect(0, 0, 220, 60)
        btn_rect.center = (x, y)
        pygame.draw.rect(SCREEN, color, btn_rect, border_radius=5)
        
        font = pygame.font.SysFont("Arial", 30, bold=True)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(x, y))
        SCREEN.blit(text_surf, text_rect)

    def draw(self):
        from config import WIDTH, HEIGHT

        # 1. Camera Offset
        SCREEN.fill(BLACK)
        self.offset_x = self.player.hitbox.centerx - (WIDTH // 2)
        self.offset_y = self.player.hitbox.centery - (HEIGHT // 2)

        if self.bg_image:
            map_w = self.bg_image.get_width()
            map_h = self.bg_image.get_height()
            self.offset_x = max(0, min(self.offset_x, map_w - WIDTH))
            self.offset_y = max(0, min(self.offset_y, map_h - HEIGHT))
            SCREEN.blit(self.bg_image, (-self.offset_x, -self.offset_y))
        
        # 2. Shadows
        for sprite in self.all_sprites:
            sh_w = int(sprite.rect.width * 0.6)
            sh_h = 12
            shadow_surface = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0,0,0, 80), (0, 0, sh_w, sh_h))
            
            shadow_x = (sprite.rect.x - self.offset_x) + (sprite.rect.width - sh_w) // 2
            shadow_y = (sprite.rect.bottom - self.offset_y) - 8
            SCREEN.blit(shadow_surface, (shadow_x, shadow_y))
        
        # 3. Sprites
        for sprite in self.all_sprites:
            # FIX: Skip drawing normal player body if they are slashing
            if sprite == self.player and getattr(self.player, 'slashing', False):
                continue
            SCREEN.blit(sprite.image, (sprite.rect.x - self.offset_x, sprite.rect.y - self.offset_y))

        # 4. Slashing Animation Overlay
        if getattr(self.player, 'slashing', False) and self.player.imageslash:
            SCREEN.blit(self.player.imageslash, (self.player.slashrect.x - self.offset_x, self.player.slashrect.y - self.offset_y))

        # 5. UI Elements
        SCREEN.blit(self.health_bar.image, self.health_bar.rect)
        if self.ui_bag_icon:
            SCREEN.blit(self.ui_bag_icon, (20, HEIGHT - 100))

        # 6. Dev Rectangles (Hitboxes & Obstacles)
        hitbox_screen_rect = self.player.hitbox.move(-self.offset_x, -self.offset_y)
        pygame.draw.rect(SCREEN, (0, 255, 0), hitbox_screen_rect, 2)
        
        # Uncomment this to see enemy hitboxes
        # for e in self.enemies_group:
        #    pygame.draw.rect(SCREEN, (255, 0, 255), e.hitbox.move(-self.offset_x, -self.offset_y), 2)

        if hasattr(self, 'obstacles'):
            for wall in self.obstacles:
                wall_screen_rect = wall.move(-self.offset_x, -self.offset_y)
                pygame.draw.rect(SCREEN, (255, 0, 0), wall_screen_rect, 2)
        
        if self.dev_drawing and self.dev_rect:
            screen_rect = self.dev_rect.move(-self.offset_x, -self.offset_y)
            pygame.draw.rect(SCREEN, (0, 0, 255), screen_rect, 3)

        # 7. Menus
        if self.is_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            SCREEN.blit(overlay, (0, 0))

            if self.show_system_menu:
                menu_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 200, 300, 400)
                pygame.draw.rect(SCREEN, (26, 22, 54), menu_rect)
                pygame.draw.rect(SCREEN, (255, 204, 51), menu_rect, 4)
                
                self.draw_ui_button("RESUME", WIDTH//2, HEIGHT//2 - 100, (0, 255, 100))
                self.draw_ui_button("SETTINGS", WIDTH//2, HEIGHT//2, (100, 100, 255))
                self.draw_ui_button("QUIT", WIDTH//2, HEIGHT//2 + 100, (255, 42, 109))

            elif self.show_inventory:
                inv_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
                pygame.draw.rect(SCREEN, (26, 22, 54), inv_rect)
                pygame.draw.rect(SCREEN, (255, 204, 51), inv_rect, 4)

                for i in range(12):
                    row, col = i // 4, i % 4
                    slot_x = inv_rect.x + 70 + (col * 175)
                    slot_y = inv_rect.y + 100 + (row * 140)

                    if self.ui_slot_bg:
                        SCREEN.blit(self.ui_slot_bg, (slot_x, slot_y))

                    item = self.player.inventory.slots[i]
                    if item:
                        SCREEN.blit(item.image, (slot_x + 15, slot_y + 15))