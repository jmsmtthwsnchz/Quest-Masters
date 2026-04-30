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
        self.bg_image = load_image("resource/stage1map.png", alpha=False, scale=(DESIGN_W * 3.5, DESIGN_H * 3.5))
        
        self.ui_bag_icon = load_image("resource/inventory_imgs/bag_icon.png", scale=(80, 80))
        self.ui_slot_bg = load_image("resource/inventory_imgs/slot_icon.png", scale=(100, 100))
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

        from map_data import STAGE_1_OBSTACLES

        self.obstacles = STAGE_1_OBSTACLES

        self.dev_drawing = False
        self.dev_start = (0, 0)
        self.dev_rect = None

        self.offset_x = 0
        self.offset_y = 0

        self.is_paused = False
        self.show_system_menu = False
        self.show_inventory = False
        
    def update(self, events):
        now = pygame.time.get_ticks()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_system_menu = not self.show_system_menu
                    self.show_inventory = False
                    self.is_paused = self.show_system_menu

                if event.key == pygame.K_e:
                    self.show_inventory = not self.show_inventory
                    self.show_system_menu = False
                    self.is_paused = self.show_inventory

        if self.is_paused:
            self.update_ui_interaction(events)
            return

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

        map_w = self.bg_image.get_width()
        map_h = self.bg_image.get_height()

        self.player.handle_input(map_w, map_h, self.obstacles)

        # 2. Standard Updates (Only runs if alive)
        self.all_sprites.update(self.player)

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

        from config import get_scaled_mouse_pos
        mx, my = get_scaled_mouse_pos()
        world_x = mx + self.offset_x
        world_y = my + self.offset_y

        for e in events:
            # 1. Start drawing on Right-Click Down
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3: 
                self.dev_drawing = True
                self.dev_start = (world_x, world_y)
            
            # 2. Finish drawing on Right-Click Up
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 3:
                self.dev_drawing = False
                if self.dev_rect:
                    # Print the exact code you need for your obstacles list!
                    print(f"pygame.Rect({self.dev_rect.x}, {self.dev_rect.y}, {self.dev_rect.width}, {self.dev_rect.height}),")

        # 3. Calculate the box while dragging
        if self.dev_drawing:
            width = world_x - self.dev_start[0]
            height = world_y - self.dev_start[1]
            
            # This math allows you to drag the box in any direction (up, down, left, right)
            left = self.dev_start[0] if width > 0 else world_x
            top = self.dev_start[1] if height > 0 else world_y
            
            self.dev_rect = pygame.Rect(int(left), int(top), int(abs(width)), int(abs(height)))

    def update_menu(self, events):
        from config import get_scaled_mouse_pos, WIDTH, HEIGHT
        mx, my = get_scaled_mouse_pos()

        quit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 220, 200, 50)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if quit_rect.collidepoint((mx, my)):
                    self.reset()
                    self.switch_screen("level_select")

    def draw(self):
        from config import WIDTH, HEIGHT

        SCREEN.fill(BLACK)
        self.offset_x = self.player.hitbox.centerx - (WIDTH // 2)
        self.offset_y = self.player.hitbox.centery - (HEIGHT // 2)

        if self.bg_image:
            map_w = self.bg_image.get_width()
            map_h = self.bg_image.get_height()

            self.offset_x = max(0, min(self.offset_x, map_w - WIDTH))
            self.offset_y = max(0, min(self.offset_y, map_h - HEIGHT))

            SCREEN.blit(self.bg_image, (-self.offset_x, -self.offset_y))
        
        for sprite in self.all_sprites:

            sh_w = int(sprite.rect.width * 0.6)
            sh_h = 12

            shadow_surface = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0,0,0, 80), (0, 0, sh_w, sh_h))
            
            shadow_x = (sprite.rect.x - self.offset_x) + (sprite.rect.width - sh_w) // 2
            shadow_y = (sprite.rect.bottom - self.offset_y) - 8

            SCREEN.blit(shadow_surface, (shadow_x, shadow_y))
        
        for sprite in self.all_sprites:
            SCREEN.blit(sprite.image, (sprite.rect.x - self.offset_x, sprite.rect.y - self.offset_y))

        if getattr(self.player, 'slashing', False) and self.player.imageslash:
            SCREEN.blit(self.player.imageslash, (self.player.slashrect.x - self.offset_x, self.player.slashrect.y - self.offset_y))

        SCREEN.blit(self.health_bar.image, self.health_bar.rect)

        hitbox_screen_rect = self.player.hitbox.move(-self.offset_x, -self.offset_y)
        pygame.draw.rect(SCREEN, (0, 255, 0), hitbox_screen_rect, 2)

        if hasattr(self, 'obstacles'):
            for wall in self.obstacles:

                wall_screen_rect = wall.move(-self.offset_x, -self.offset_y)
                pygame.draw.rect(SCREEN, (255, 0, 0), wall_screen_rect, 2)
        
        if self.dev_drawing and self.dev_rect:
            screen_rect = self.dev_rect.move(-self.offset_x, -self.offset_y)
            pygame.draw.rect(SCREEN, (0, 0, 255), screen_rect, 3)

        if self.is_paused:
            from config import WIDTH, HEIGHT
            # Darken the background for focus
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            SCREEN.blit(overlay, (0, 0))

            # --- SYSTEM MENU ---
            if self.show_system_menu:
                # Smaller, vertical panel for System Menu
                menu_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 200, 300, 400)
                pygame.draw.rect(SCREEN, (26, 22, 54), menu_rect)
                pygame.draw.rect(SCREEN, (255, 204, 51), menu_rect, 4)
                
                # Manual Button Drawing with Text
                self.draw_ui_button("RESUME", WIDTH//2, HEIGHT//2 - 100, (0, 255, 100))
                self.draw_ui_button("SETTINGS", WIDTH//2, HEIGHT//2, (100, 100, 255))
                self.draw_ui_button("QUIT", WIDTH//2, HEIGHT//2 + 100, (255, 42, 109))

            # --- INVENTORY ---
            elif self.show_inventory:
                # Large panel for Inventory
                inv_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
                pygame.draw.rect(SCREEN, (26, 22, 54), inv_rect)
                pygame.draw.rect(SCREEN, (255, 204, 51), inv_rect, 4)

                # Draw Grid
                for i in range(12):
                    row, col = i // 4, i % 4
                    slot_x = inv_rect.x + 70 + (col * 175)
                    slot_y = inv_rect.y + 100 + (row * 140)

                    if self.ui_slot_bg:
                        SCREEN.blit(self.ui_slot_bg, (slot_x, slot_y))

                    item = self.player.inventory.slots[i]
                    if item:
                        SCREEN.blit(item.image, (slot_x + 15, slot_y + 15))

    def draw_ui_button(self, text, x, y, color):
        from config import WHITE
        btn_rect = pygame.Rect(0, 0, 220, 60)
        btn_rect.center = (x, y)
        pygame.draw.rect(SCREEN, color, btn_rect, border_radius=5)
        
        # Simple font rendering
        font = pygame.font.SysFont("Arial", 30, bold=True)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(x, y))
        SCREEN.blit(text_surf, text_rect)

    def update_ui_interaction(self, events):
        from config import get_scaled_mouse_pos, WIDTH, HEIGHT
        mx, my = get_scaled_mouse_pos()
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.show_system_menu:
                    # Check Quit Button (Centered at +100 y)
                    quit_area = pygame.Rect(0, 0, 220, 60)
                    quit_area.center = (WIDTH//2, HEIGHT//2 + 100)
                    if quit_area.collidepoint((mx, my)):
                        self.reset()
                        self.switch_screen("level_select")


                    settings_area = pygame.Rect(0, 0, 220, 60)
                    settings_area.center = (WIDTH // 2, HEIGHT // 2)
                    if settings_area.collidepoint((mx, my)):
                        self.switch_screen("settings")

                    # Check Resume Button (Centered at -100 y)
                    resume_area = pygame.Rect(0, 0, 220, 60)
                    resume_area.center = (WIDTH//2, HEIGHT//2 - 100)
                    if resume_area.collidepoint((mx, my)):
                        self.show_system_menu = False
                        self.is_paused = False

                    
