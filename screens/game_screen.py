import pygame
import random
import os
from config import SCREEN, BLACK, WHITE, s_g, script_dir
from utils import load_image
from entities.player import Player
from entities.enemy import Creature
from ui.health import HealthBar
from screens.settings import settings_state

class GameScreen:
    def __init__(self, switch_func, sound_manager=None):
        self.switch_screen = switch_func
        self.current_stage_idx = 0
        self.current_difficulty = None
        self.current_selected_char = "male"
        self.is_game_over = False

        self.hotbar_slots = [None] * 3 #[cite: 10]
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.source_slot_index = None
        self.bg_image = None
        
        # Load UI Icons once
        self.ui_bag_icon = load_image("resource/inventory_imgs/bag_icon.png", scale=(80, 80))
        self.ui_slot_bg = load_image("resource/inventory_imgs/slot_icon.png", scale=(100, 100))
        
        from config import WIDTH, HEIGHT
        self.vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.vignette.fill((0, 0, 0, 180)) # The darkness of the corners
        center_x, center_y = WIDTH // 2, HEIGHT // 2

        # Carve out the center transparency[cite: 5]
        for r in range(int(WIDTH // 1.2), 0, -5):
            alpha = int(255 * (r / (WIDTH // 1.2)))
            if alpha > 255: alpha = 255
            pygame.draw.circle(self.vignette, (0, 0, 0, alpha), (center_x, center_y), r)

        
        self.sound_manager = sound_manager
        self.reset()

    def reset(self, stage_index=None, difficulty=None, char_type=None, **kwargs):

        if stage_index is None and difficulty is None and char_type is None and getattr(self, 'player', None) is not None:
            self.is_paused = False
            self.show_system_menu = False
            return

        idx = stage_index if stage_index is not None else self.current_stage_idx
        pygame.mixer.music.stop()
        track_name = "desert_ambient.mp3" if idx == 0 else "default_bg.mp3"
        full_track_path = os.path.join(self.sound_manager.path, track_name)

        try:
            self.sound_manager.play_music(full_track_path, settings_state["music_volume"])
        except Exception as e:
            print(f"could not load music: {e}")

        old_inventory = None
        old_hotbar = None

        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()

        if hasattr(self, 'player') and self.player is not None:
            old_inventory = self.player.inventory.slots
            old_hotbar = self.hotbar_slots

        self.player = Player(2000, 2000, gender=self.current_selected_char)
        if old_inventory:
            self.player.inventory.slots = old_inventory
        if old_hotbar:
            self.hotbar_slots = old_hotbar

        self.all_sprites.add(self.player)

        if char_type is not None:
            self.current_selected_char = "male" if char_type == "percival" else "female"
        
        if stage_index is not None:
            self.current_stage_idx = stage_index
        if difficulty is not None:
            self.current_difficulty = difficulty

        if hasattr(self, 'player') and self.player is not None and stage_index is None:
            self.is_paused = True 
            return
        
        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()

        from map_data import (
            STAGE_1_CHAPTER_1_OBSTACLES, STAGE_1_CHAPTER_2_OBSTACLES, STAGE_1_CHAPTER_3_OBSTACLES,
            STAGE_2_CHAPTER_1_OBSTACLES, STAGE_2_CHAPTER_2_OBSTACLES, STAGE_2_CHAPTER_3_OBSTACLES
        )
        
        from config import DESIGN_W, DESIGN_H
        map_files = [
            "resource/stg1chapter1map.png", "resource/stg1chapter2map.jpg", "resource/stg1chapter3map.jpg",
            "resource/stg2chapter1map.png", "resource/stg2chapter2map.png", "resource/stg2chapterl3map.png"
        ]
        obstacle_sets = [
            STAGE_1_CHAPTER_1_OBSTACLES, STAGE_1_CHAPTER_2_OBSTACLES, STAGE_1_CHAPTER_3_OBSTACLES,
            STAGE_2_CHAPTER_1_OBSTACLES, STAGE_2_CHAPTER_2_OBSTACLES, STAGE_2_CHAPTER_3_OBSTACLES
        ]

        idx = max(0, min(self.current_stage_idx, len(map_files) - 1))
        self.bg_image = load_image(map_files[idx], alpha=False, scale=(DESIGN_W * 3.5, DESIGN_H * 3.5))
        self.obstacles = obstacle_sets[idx]

        self.player = Player(2000, 2000, gender=self.current_selected_char)
        self.all_sprites.add(self.player)
        self.health_bar = HealthBar(1820, 20)

        enemy_types = ["snake", "camel"]
        enemy_count = 20 if self.current_difficulty == "hard" else 12 if self.current_difficulty == "medium" else 5

        spawn_center_x, spawn_center_y, spawn_radius = 2000, 2000, 1200
        for i in range(enemy_count):
            safe = False
            attempts = 0
            while not safe and attempts < 100:
                attempts += 1
                rx = random.randint(spawn_center_x - spawn_radius, spawn_center_x + spawn_radius)
                ry = random.randint(spawn_center_y - spawn_radius, spawn_center_y + spawn_radius)
                test_hitbox = pygame.Rect(0, 0, 65, 20)
                from config import s_x, s_y
                test_hitbox.midbottom = (s_x(rx), s_y(ry))
                if (test_hitbox.collidelist(self.obstacles) == -1 and 
                    not any(test_hitbox.colliderect(e.hitbox) for e in self.enemies_group) and 
                    not test_hitbox.colliderect(self.player.hitbox.inflate(200, 200))):
                    enemy = Creature(rx, ry, random.choice(enemy_types))
                    self.all_sprites.add(enemy)
                    self.enemies_group.add(enemy)
                    safe = True

        self.offset_x = self.offset_y = 0
        self.is_paused = self.show_system_menu = self.show_inventory = self.dev_drawing = False

        if stage_index is not None or char_type is not None:
            try:
                self.sound_manager.play_sfx("start")
            except AttributeError:
                pass

    def update(self, events):
        now = pygame.time.get_ticks()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Hotbar Inputs (1, 2, 3)[cite: 7]
                hotkeys = [pygame.K_1, pygame.K_2, pygame.K_3]
                if event.key in hotkeys:
                    idx = hotkeys.index(event.key)
                    item = self.hotbar_slots[idx]
                    if item and hasattr(item, 'use'):
                        if item.use(self.player): #[cite: 8]
                            self.hotbar_slots[idx] = None
                            print(f"Used Hotbar Item {idx + 1}!")

                # Test Item Spawner[cite: 9]
                if event.key == pygame.K_p:
                    from logic.item_factory import create_test_item
                    new_item = create_test_item(self.health_bar)
                    added = False
                    for i in range(len(self.hotbar_slots)):
                        if self.hotbar_slots[i] is None:
                            self.hotbar_slots[i] = new_item
                            added = True
                            break
                    if not added:
                        self.player.inventory.add_item(new_item)
                if event.key == pygame.K_k:
                    self.trigger_slash()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.is_paused:
                        self.trigger_slash()

                if event.key == pygame.K_ESCAPE:
                    self.show_system_menu = not self.show_system_menu
                    self.show_inventory = False
                    self.is_paused = self.show_system_menu

                if event.key in [pygame.K_e, pygame.K_i]:
                    self.show_inventory = not self.show_inventory
                    self.show_system_menu = False
                    self.is_paused = self.show_inventory

        # Handle UI Clicks while paused
        from config import get_scaled_mouse_pos, WIDTH, HEIGHT
        mx, my = get_scaled_mouse_pos()
        
        # Calculate Bag Rect for clicking[cite: 7]
        gap = s_g(15)
        bag_w, bag_h = self.ui_bag_icon.get_size()
        hp_w = self.health_bar.rect.width
        total_ui_width = hp_w + gap + bag_w
        start_x = (WIDTH // 2) - (total_ui_width // 2)
        bag_x = start_x + hp_w + gap
        ui_y_base = HEIGHT - s_g(110)
        bag_rect = pygame.Rect(bag_x, ui_y_base, bag_w, bag_h)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if bag_rect.collidepoint((mx, my)):
                    self.show_inventory = not self.show_inventory
                    self.is_paused = self.show_inventory

        if self.is_paused:
            self.update_ui_interaction(events)
            return

        # --- Gameplay Logic ---
        map_w, map_h = self.bg_image.get_width(), self.bg_image.get_height()
        self.player.handle_input(map_w, map_h, self.obstacles)
        self.all_sprites.update(self.player, self.obstacles)

        # Combat and Death Logic
        if self.health_bar.hp_index >= len(self.health_bar.frames) - 1 or self.player.is_dead:
            self.player.is_dead = True
            self.player.image = pygame.transform.rotate(self.player.image, 90)
            self.draw()
            pygame.display.flip()
            pygame.time.delay(1500)
            self.reset()
            self.switch_screen("game_select")
            return

        taken_hits = [e for e in self.enemies_group if self.player.rect.inflate(-100, -100).colliderect(e.rect.inflate(-60, -60)) and not getattr(e, 'is_dying', False)]
        if taken_hits and (now - self.player.last_hit_time > self.player.invulnerability_duration):
            self.health_bar.take_damage() 
            self.player.last_hit_time = now
            if not self.player.is_dead:
                enemy = taken_hits[0]
                kb = self.player.speed * 8
                self.player.hitbox.x += kb if self.player.hitbox.centerx > enemy.hitbox.centerx else -kb
                self.player.hitbox.y += kb if self.player.hitbox.centery > enemy.hitbox.centery else -kb
                self.player.rect.midbottom = self.player.hitbox.midbottom
        
        is_already_dead = self.health_bar.hp_index >= len(self.health_bar.frames) - 1
        if (is_already_dead or self.player.is_dead) and not self.is_game_over:
            self.is_game_over = True
            self.is_paused = True
            self.player.is_dead = True
            self.player.image = pygame.transform.rotate(self.player.image, 90)
            print("player has fallen")

        if self.player.slashing and self.player.slashframe == 3:
            for enemy in self.enemies_group:
                if self.player.slashrect.inflate(-20, -20).colliderect(enemy.rect):
                    enemy.hit()

    def update_ui_interaction(self, events):
        from config import get_scaled_mouse_pos, WIDTH, HEIGHT
        mx, my = get_scaled_mouse_pos()

        for e in events:
            # --- 1. PICK UP LOGIC ---
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.show_system_menu and e.button == 1:
                    mid_x, mid_y = WIDTH // 2, HEIGHT // 2
                    if pygame.Rect(mid_x-110, mid_y-130, 220, 60).collidepoint((mx, my)):
                        self.show_system_menu = False
                        self.is_paused = False
                    if pygame.Rect(mid_x-110, mid_y-30, 220, 60).collidepoint((mx, my)):
                        self.switch_screen("settings", return_to="game")
                    if pygame.Rect(mid_x-110, mid_y+70, 220, 60).collidepoint((mx, my)):
                        self.reset()
                        self.switch_screen("game_select")

                elif self.show_inventory:
                    inv_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
                    
                    if e.button == 1: # Left Click: Close or Drag
                        close_btn = pygame.Rect(inv_rect.right - 50, inv_rect.top + 10, 40, 40)
                        if close_btn.collidepoint((mx, my)):
                            self.show_inventory = False
                            self.is_paused = False
                            return

                        # Check Bag Slots for dragging
                        for i in range(12):
                            row, col = i // 4, i % 4
                            slot_rect = pygame.Rect(inv_rect.x + 70 + (col * 175), inv_rect.y + 120 + (row * 140), 100, 100)
                            if slot_rect.collidepoint((mx, my)):
                                self.dragging_item = self.player.inventory.slots[i]
                                if self.dragging_item:
                                    self.player.inventory.slots[i] = None
                                    self.source_slot_index = i # 0-11 for Bag
                                    return

                        # Check Hotbar Slots for dragging[cite: 8]
                        ui_y_base = HEIGHT - s_g(110)
                        hotbar_y = ui_y_base - s_g(110)
                        for i in range(3):
                            hot_slot_rect = pygame.Rect((WIDTH // 2) - s_g(165) + (i * s_g(110)), hotbar_y, s_g(100), s_g(100))
                            if hot_slot_rect.collidepoint((mx, my)):
                                self.dragging_item = self.hotbar_slots[i]
                                if self.dragging_item:
                                    self.hotbar_slots[i] = None
                                    self.source_slot_index = i + 100 # 100+ for Hotbar[cite: 8]
                                    return

                    elif e.button == 3: # Right Click: Use[cite: 7, 8]
                        for i in range(12):
                            row, col = i // 4, i % 4
                            slot_rect = pygame.Rect(inv_rect.x + 70 + (col * 175), inv_rect.y + 120 + (row * 140), 100, 100)
                            if slot_rect.collidepoint((mx, my)):
                                item = self.player.inventory.slots[i]
                                if item and hasattr(item, 'use') and item.use(self.player):
                                    self.player.inventory.slots[i] = None

            # --- 2. DROP LOGIC ---
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if self.dragging_item:
                    dropped = False
                    inv_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
                    
                    # Try dropping into Hotbar[cite: 8]
                    ui_y_base = HEIGHT - s_g(110)
                    hotbar_y = ui_y_base - s_g(110)
                    for i in range(3):
                        hot_slot_rect = pygame.Rect((WIDTH // 2) - s_g(165) + (i * s_g(110)), hotbar_y, s_g(100), s_g(100))
                        if hot_slot_rect.collidepoint((mx, my)):
                            # Swap if slot already has an item[cite: 8]
                            temp = self.hotbar_slots[i]
                            self.hotbar_slots[i] = self.dragging_item
                            self.dragging_item = temp
                            dropped = True
                            break
                    
                    # Try dropping into Bag[cite: 8]
                    if not dropped:
                        for i in range(12):
                            row, col = i // 4, i % 4
                            slot_rect = pygame.Rect(inv_rect.x + 70 + (col * 175), inv_rect.y + 120 + (row * 140), 100, 100)
                            if slot_rect.collidepoint((mx, my)):
                                temp = self.player.inventory.slots[i]
                                self.player.inventory.slots[i] = self.dragging_item
                                self.dragging_item = temp
                                dropped = True
                                break

                    # If dropped in empty space or no swap occurred, return to source[cite: 8]
                    if self.dragging_item:
                        if self.source_slot_index >= 100:
                            idx = self.source_slot_index - 100
                            # If the source slot is now empty, put it back[cite: 8]
                            if self.hotbar_slots[idx] is None: self.hotbar_slots[idx] = self.dragging_item
                            else: self.player.inventory.add_item(self.dragging_item) # Fallback to bag[cite: 7]
                        else:
                            idx = self.source_slot_index
                            if self.player.inventory.slots[idx] is None: self.player.inventory.slots[idx] = self.dragging_item
                            else: self.player.inventory.add_item(self.dragging_item)
                    
                    self.dragging_item = None
        if self.is_game_over:
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if pygame.Rect(WIDTH//2 - 110, HEIGHT//2, 220, 60).collidepoint((mx, my)):
                        # Reset WITHOUT carrying over items (The Penalty)
                        self.player = None 
                        self.reset(stage_index=self.current_stage_idx)
                        self.is_game_over = False
                        
                    # Quit Button
                    if pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 80, 220, 60).collidepoint((mx, my)):
                        self.is_game_over = False
                        self.switch_screen("game_select")
    def draw(self):
        from config import WIDTH, HEIGHT, get_scaled_mouse_pos
        mx, my = get_scaled_mouse_pos()

        # 1. Camera & Background
        self.offset_x = max(0, min(self.player.hitbox.centerx - (WIDTH // 2), self.bg_image.get_width() - WIDTH))
        self.offset_y = max(0, min(self.player.hitbox.centery - (HEIGHT // 2), self.bg_image.get_height() - HEIGHT))
        SCREEN.fill(BLACK)
        SCREEN.blit(self.bg_image, (-self.offset_x, -self.offset_y))
        
        # 2. Shadows & Sprites
        for sprite in self.all_sprites:
            sh_w = int(sprite.rect.width * 0.45)
            shadow_surf = pygame.Surface((sh_w, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0,0,0, 80), (0, 0, sh_w, 12))
            SCREEN.blit(shadow_surf, ((sprite.rect.x - self.offset_x) + (sprite.rect.width - sh_w) // 2, (sprite.rect.bottom - self.offset_y) - 25))
            if not (sprite == self.player and getattr(self.player, 'slashing', False)):
                SCREEN.blit(sprite.image, (sprite.rect.x - self.offset_x, sprite.rect.y - self.offset_y))

        if getattr(self.player, 'slashing', False) and self.player.imageslash:
            SCREEN.blit(self.player.imageslash, (self.player.slashrect.x - self.offset_x, self.player.slashrect.y - self.offset_y))

        # 3. Main HUD (Centered Bottom)
        gap, ui_y_base = s_g(15), HEIGHT - s_g(110)
        bag_w, bag_h = self.ui_bag_icon.get_size()
        total_ui_width = self.health_bar.rect.width + gap + bag_w
        start_x = (WIDTH // 2) - (total_ui_width // 2)
        
        self.health_bar.rect.topleft = (start_x, ui_y_base + (bag_h // 2) - (self.health_bar.rect.height // 2))
        SCREEN.blit(self.health_bar.image, self.health_bar.rect)
        SCREEN.blit(self.ui_bag_icon, (start_x + self.health_bar.rect.width + gap, ui_y_base))
        
        # 4.5 Atmosphere
        SCREEN.blit(self.vignette, (0, 0))

        if not self.is_paused:
            self.draw_hotbar()
            
        # 5. Menus & Tooltips
        if self.is_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
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

                self.draw_hotbar()

                title = pygame.font.SysFont("Arial", 40, bold=True).render("INVENTORY", True, (255, 204, 51))
                SCREEN.blit(title, (inv_rect.x + 20, inv_rect.top + 20))
                
                close_btn = pygame.Rect(inv_rect.right - 50, inv_rect.top + 10, 40, 40)
                pygame.draw.rect(SCREEN, (255, 50, 50) if close_btn.collidepoint((mx, my)) else (150, 0, 0), close_btn)
                pygame.draw.line(SCREEN, WHITE, (close_btn.x+10, close_btn.y+10), (close_btn.right-10, close_btn.bottom-10), 3)
                pygame.draw.line(SCREEN, WHITE, (close_btn.right-10, close_btn.y+10), (close_btn.x+10, close_btn.bottom-10), 3)
                
                hovered_item = None
                for i in range(12):
                    row, col = i // 4, i % 4
                    slot_x, slot_y = inv_rect.x + 70 + (col * 175), inv_rect.y + 120 + (row * 140)
                    slot_rect = pygame.Rect(slot_x, slot_y, 100, 100)
                    if self.ui_slot_bg: SCREEN.blit(self.ui_slot_bg, (slot_x, slot_y))
                    if slot_rect.collidepoint((mx, my)):
                        s = pygame.Surface((100, 100), pygame.SRCALPHA); s.fill((255, 255, 255, 60))
                        SCREEN.blit(s, (slot_x, slot_y))
                        hovered_item = self.player.inventory.slots[i]
                    item = self.player.inventory.slots[i]
                    if item: SCREEN.blit(item.image, (slot_x + 15, slot_y + 15))
                
                if hovered_item: self.draw_tooltip(hovered_item, mx, my)

            if self.dragging_item:
                SCREEN.blit(self.dragging_item.image, (mx - 35, my - 35))
        if self.is_game_over:
            death_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            death_overlay.fill((50, 0 ,0, 200))
            SCREEN.blit(death_overlay, (0, 0))

            font = pygame.font.SysFont("Arial", 80, bold=True)
            text = font.render("GAME OVER", True, (255, 50, 50))
            SCREEN.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

            self.draw_ui_button("RESTART", WIDTH // 2, HEIGHT // 2 + 30, (50, 50, 50))
            self.draw_ui_button("QUIT", WIDTH // 2, HEIGHT // 2 + 110, (100, 0, 0))

    def draw_hotbar(self):
        from config import WIDTH, HEIGHT

        ui_y_base = HEIGHT - s_g(110)
        hotbar_y = ui_y_base - s_g(110)
        for i in range(3):
            slot_x = (WIDTH // 2) - s_g(165) + (i * s_g(110))
            if self.ui_slot_bg:
                SCREEN.blit(pygame.transform.scale(self.ui_slot_bg, (s_g(100), s_g(100))), (slot_x, hotbar_y))
            item = self.hotbar_slots[i]
            if item:
                SCREEN.blit(pygame.transform.scale(item.image, (s_g(70), s_g(70))), (slot_x + s_g(15), hotbar_y + s_g(15)))
        
    def draw_tooltip(self, item, x, y):
        font = pygame.font.SysFont("Arial", 20)
        name_s = font.render(item.name, True, (255, 204, 51))
        desc_s = font.render(item.description, True, WHITE)
        tw = max(name_s.get_width(), desc_s.get_width()) + 20
        th = name_s.get_height() + desc_s.get_height() + 15
        tr = pygame.Rect(x + 15, y + 15, tw, th)
        pygame.draw.rect(SCREEN, (20, 20, 30), tr)
        pygame.draw.rect(SCREEN, (255, 204, 51), tr, 1)
        SCREEN.blit(name_s, (tr.x + 10, tr.y + 5))
        SCREEN.blit(desc_s, (tr.x + 10, tr.y + 25))

    def draw_ui_button(self, text, x, y, color):
        btn_rect = pygame.Rect(0, 0, 220, 60); btn_rect.center = (x, y)
        pygame.draw.rect(SCREEN, color, btn_rect, border_radius=5)
        text_surf = pygame.font.SysFont("Arial", 30, bold=True).render(text, True, WHITE)
        SCREEN.blit(text_surf, text_surf.get_rect(center=(x, y)))

    def play_slash_sfx(self):
        self.sfx_slash.set_volume(settings_state["sound_volume"])
        self.sfx_slash.play()
    
    def trigger_slash(self):
        if not self.player.slashing:
            self.player.slashing = True
            self.player.slashframe = 0
            
            self.sound_manager.play_sfx("slash")
