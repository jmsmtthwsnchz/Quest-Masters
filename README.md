# Desert Adventure: Pygame RPG

A top-down 2D action game built with Python and Pygame. Explore an expansive desert ruins map, battle snakes and camels with a tactical slash attack, and survive the ancient tombs.

## 🚀 Features

- **Dynamic Camera System:** A smooth scrolling camera that follows the player through a massive, high-resolution world map.
- **Combat System:** Tactical sword-slashing mechanics with custom hitbox logic (0.6 ratio) for precise gameplay.
- **Smart Enemy AI:** Enemies feature patrol paths and "Zombie-style" chasing logic with reaction delays when the player is spotted.
- **Animated Entities:** Fully animated player movement and enemy death sequences using sprite-sheet logic.
- **Stage System:** Multiple difficulty levels (Easy, Medium, Hard) set within different sections of the ancient ruins.

## 🛠️ Tech Stack

- **Language:** Python 3.13+
- **Library:** Pygame 2.6.1+
- **Assets:** Custom pixel art sprites and PNG environmental textures.

## 📦 Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name

   ```

2. **Set up a Virtual Environment:**

   ```python -m venv venv
       # On Windows:
       venv\Scripts\activate
       # On Mac/Linux:
       source venv/bin/activate
   ```

## Project Structure

```
├── 📁 assets
│   ├── 📁 main_menu_imgs
│   │   ├── 🖼️ back.png
│   │   ├── 🖼️ back_hover.png
│   │   ├── 🖼️ fire_knob.gif
│   │   ├── 🖼️ main_menu_bg.png
│   │   ├── 🖼️ music_post.png
│   │   ├── 🖼️ music_text.png
│   │   ├── 🖼️ post.png
│   │   ├── 🖼️ quit_hover.png
│   │   ├── 🖼️ settings_bg.png
│   │   ├── 🖼️ settings_hover.png
│   │   ├── 🖼️ settings_title.png
│   │   ├── 🖼️ skull.png
│   │   ├── 🖼️ sounds_post.png
│   │   ├── 🖼️ sounds_text.png
│   │   ├── 📄 stage1.jfif
│   │   ├── 🖼️ stage1_bg.png
│   │   ├── 📄 stage2.jfif
│   │   ├── 🖼️ stage2_bg.png
│   │   ├── 📄 stage3.jfif
│   │   ├── 🖼️ stage3_bg.png
│   │   ├── 🖼️ start_hover.png
│   │   └── 🖼️ tree_branch.png
│   └── 📁 resource
│       ├── 📁 character
│       │   ├── 📁 health
│       │   │   ├── 🖼️ 0.png
│       │   │   ├── 🖼️ 1.png
│       │   │   ├── 🖼️ 2.png
│       │   │   ├── 🖼️ 3.png
│       │   │   ├── 🖼️ 4.png
│       │   │   └── 🖼️ 5.png
│       │   └── 📁 movement
│       │       ├── 🖼️ d1.png
│       │       ├── 🖼️ d2.png
│       │       ├── 🖼️ d3.png
│       │       ├── 🖼️ d4.png
│       │       ├── 🖼️ l1.png
│       │       ├── 🖼️ l2.png
│       │       ├── 🖼️ l3.png
│       │       ├── 🖼️ l4.png
│       │       ├── 🖼️ r1.png
│       │       ├── 🖼️ r2.png
│       │       ├── 🖼️ r3.png
│       │       ├── 🖼️ r4.png
│       │       ├── 🖼️ raw.png
│       │       ├── 🖼️ u1.png
│       │       ├── 🖼️ u2.png
│       │       ├── 🖼️ u3.png
│       │       └── 🖼️ u4.png
│       ├── 📁 enemies
│       │   ├── 📁 camel
│       │   │   ├── 📁 DEATH
│       │   │   │   ├── 🖼️ 1.png
│       │   │   │   ├── 🖼️ 2.png
│       │   │   │   ├── 🖼️ 3.png
│       │   │   │   ├── 🖼️ 4.png
│       │   │   │   └── 🖼️ 5.png
│       │   │   ├── 📁 DOWN
│       │   │   │   ├── 🖼️ 1.png
│       │   │   │   ├── 🖼️ 2.png
│       │   │   │   ├── 🖼️ 3.png
│       │   │   │   ├── 🖼️ 4.png
│       │   │   │   └── 🖼️ 5.png
│       │   │   ├── 📁 LEFT
│       │   │   │   ├── 🖼️ 1.png
│       │   │   │   ├── 🖼️ 2.png
│       │   │   │   ├── 🖼️ 3.png
│       │   │   │   ├── 🖼️ 4.png
│       │   │   │   └── 🖼️ 5.png
│       │   │   ├── 📁 RIGHT
│       │   │   │   ├── 🖼️ 1.png
│       │   │   │   ├── 🖼️ 2.png
│       │   │   │   ├── 🖼️ 3.png
│       │   │   │   ├── 🖼️ 4.png
│       │   │   │   └── 🖼️ 5.png
│       │   │   └── 📁 UP
│       │   │       ├── 🖼️ 1.png
│       │   │       ├── 🖼️ 2.png
│       │   │       ├── 🖼️ 3.png
│       │   │       ├── 🖼️ 4.png
│       │   │       └── 🖼️ 5.png
│       │   └── 📁 snake
│       │       ├── 📁 DEATH
│       │       │   ├── 🖼️ 1.png
│       │       │   ├── 🖼️ 2.png
│       │       │   ├── 🖼️ 3.png
│       │       │   ├── 🖼️ 4.png
│       │       │   └── 🖼️ 5.png
│       │       ├── 📁 DOWN
│       │       │   ├── 🖼️ 1.png
│       │       │   ├── 🖼️ 2.png
│       │       │   ├── 🖼️ 3.png
│       │       │   ├── 🖼️ 4.png
│       │       │   └── 🖼️ 5.png
│       │       ├── 📁 LEFT
│       │       │   ├── 🖼️ 1.png
│       │       │   ├── 🖼️ 2.png
│       │       │   ├── 🖼️ 3.png
│       │       │   ├── 🖼️ 4.png
│       │       │   └── 🖼️ 5.png
│       │       ├── 📁 RIGHT
│       │       │   ├── 🖼️ 1.png
│       │       │   ├── 🖼️ 2.png
│       │       │   ├── 🖼️ 3.png
│       │       │   ├── 🖼️ 4.png
│       │       │   └── 🖼️ 5.png
│       │       └── 📁 UP
│       │           ├── 🖼️ 1.png
│       │           ├── 🖼️ 2.png
│       │           ├── 🖼️ 3.png
│       │           ├── 🖼️ 4.png
│       │           └── 🖼️ 5.png
│       ├── 📁 environment
│       │   ├── 🖼️ grass.png
│       │   └── 🖼️ grass1.png
│       ├── 📁 slash
│       │   ├── 🖼️ S1.png
│       │   ├── 🖼️ S2.png
│       │   ├── 🖼️ S3.png
│       │   ├── 🖼️ S4.png
│       │   ├── 🖼️ S5.png
│       │   ├── 🖼️ S6.png
│       │   ├── 🖼️ S7.png
│       │   └── 🖼️ S8.png
│       ├── 🖼️ stage1map.png
│       └── 🖼️ surface.png
├── 📁 entities
│   ├── 🐍 enemy.py
│   └── 🐍 player.py
├── 📁 screens
│   ├── 🐍 __init__.py
│   ├── 🐍 game_screen.py
│   ├── 🐍 level_select.py
│   ├── 🐍 main_menu.py
│   └── 🐍 settings.py
├── 📁 ui
│   ├── 🐍 __init__.py
│   ├── 🐍 buttons.py
│   ├── 🐍 health.py
│   ├── 🐍 portrait.py
│   └── 🐍 sliders.py
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 config.py
├── 🐍 main.py
└── 🐍 utils.py
```
