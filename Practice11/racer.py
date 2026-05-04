"""
Racer Game - Practice 10 & 11  (with images & music)
======================================================

PUT THESE FILES IN THE SAME FOLDER AS racer.py:
------------------------------------------------
Images (PNG, any size – they will be auto-scaled):
  player_car.png      – your car (top-down view, portrait)
  enemy_car.png       – enemy car (top-down view, portrait)
  coin_bronze.png     – bronze coin icon
  coin_silver.png     – silver coin icon
  coin_gold.png       – gold coin icon
  road_bg.png         – (optional) tiling road texture; if absent, plain colour is used

Music / Sound (put in same folder):
  music_bg.mp3        – background music loop  (or .ogg)
  sound_coin.wav      – coin collect sound      (or .ogg)
  sound_crash.wav     – crash sound             (or .ogg)

Any missing file is silently ignored – the game falls back to
coloured shapes / silence so it always runs.
"""

import pygame
import random
import sys
import os

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init()   # initialise audio subsystem

# ── Window ──
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS   = 60

# ── Colours (fallbacks when images are missing) ──
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
YELLOW     = (255, 220,   0)
GOLD       = (255, 180,   0)
RED        = (220,  50,  50)
BLUE       = (50,  100, 220)
ORANGE     = (255, 140,   0)
ROAD_COLOR = (60,  60,   60)
LINE_COLOR = (200, 200, 200)
GRASS      = (34,  100,  34)

# ── Fonts ──
font_large  = pygame.font.SysFont("monospace", 32, bold=True)
font_medium = pygame.font.SysFont("monospace", 22, bold=True)
font_small  = pygame.font.SysFont("monospace", 16)

# ── Road geometry ──
ROAD_LEFT  = 30
ROAD_RIGHT = WIDTH - 30
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

# ── Level / speed settings ──
COINS_PER_LEVEL       = 10    # coins needed to advance a level
ENEMY_SPEED_INCREMENT = 0.5   # extra speed added per level


# ─────────────────────────────────────────────
# ASSET LOADER  – never crashes; returns None on failure
# ─────────────────────────────────────────────
ASSET_DIR = os.path.dirname(os.path.abspath(__file__))  # same folder as this script

def load_image(filename, size=None):
    """
    Load a PNG from the game folder and scale it to `size` (w, h).
    Returns None if the file doesn't exist or fails to load.
    """
    path = os.path.join(ASSET_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


def load_sound(filename):
    """
    Load a sound file (.wav / .ogg / .mp3).
    Returns None if the file doesn't exist or fails to load.
    """
    path = os.path.join(ASSET_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


def play_music(filename, volume=0.4):
    """Start looping background music. Silently skips if file is missing."""
    path = os.path.join(ASSET_DIR, filename)
    if not os.path.exists(path):
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)   # -1 = loop forever
    except Exception:
        pass


# ── Load all assets once at start-up ──
# Cars  – wider (70 px) and taller (100 px) for better visibility
IMG_PLAYER = load_image("player_car.png", size=(70, 100))
IMG_ENEMY  = load_image("enemy_car.png",  size=(85, 100))

# Road background (optional tiling texture)
IMG_ROAD   = load_image("road_bg.png", size=(ROAD_W, HEIGHT))

# Coin images – bigger so they're easy to see and collect
IMG_COIN = {
    "bronze": load_image("coin_bronze.png", size=(36, 36)),
    "silver": load_image("coin_silver.png", size=(42, 42)),
    "gold":   load_image("coin_gold.png",   size=(50, 50)),
}

# Sounds
SND_COIN  = load_sound("sound_coin.wav")
SND_CRASH = load_sound("sound_crash.wav")

# Start background music
play_music("music_bg.mp3")


# ─────────────────────────────────────────────
# FALLBACK car drawing (used when PNG is missing)
# ─────────────────────────────────────────────
def draw_car_fallback(surface, x, y, w, h, body_color):
    """Simple coloured rectangle car for when no image is available."""
    pygame.draw.rect(surface, body_color, (x, y, w, h), border_radius=8)
    window = (160, 220, 255)
    pygame.draw.rect(surface, window, (x + 6, y + 6,      w - 12, h // 3),  border_radius=4)
    pygame.draw.rect(surface, window, (x + 6, y + h - h//4 - 3, w - 12, h // 4), border_radius=4)


# ─────────────────────────────────────────────
# COIN TYPES
# (name, points, fallback_radius, fallback_colour, spawn_probability)
#
# Weighted scoring:  bronze = 1 pt,  silver = 3 pts,  gold = 5 pts
# Probabilities:     bronze most common, gold rarest
# ─────────────────────────────────────────────
COIN_TYPES = [
    ("bronze", 1,  18, (205, 127,  50), 0.55),
    ("silver", 3,  21, (192, 192, 192), 0.30),
    ("gold",   5,  25, (255, 215,   0), 0.15),
]


class Coin:
    """
    A coin that scrolls down the road.
    Type is chosen randomly by weighted probability.
    Higher-weight coins award more points.
    If a PNG is provided for that type, it is drawn instead of a circle.
    """

    def __init__(self, speed):
        # ── Choose type by cumulative probability ──
        rng   = random.random()
        cumul = 0.0
        self.kind = COIN_TYPES[0]          # default: bronze
        for ctype in COIN_TYPES:
            cumul += ctype[4]
            if rng <= cumul:
                self.kind = ctype
                break

        self.name   = self.kind[0]         # "bronze" / "silver" / "gold"
        self.points = self.kind[1]         # score value
        self.radius = self.kind[2]         # fallback circle radius
        self.color  = self.kind[3]         # fallback circle colour
        self.speed  = speed
        self.image  = IMG_COIN.get(self.name)  # PNG or None

        # Actual display size (from image or fallback radius)
        if self.image:
            self.w = self.image.get_width()
            self.h = self.image.get_height()
        else:
            self.w = self.radius * 2
            self.h = self.radius * 2

        # Random horizontal position within road boundaries
        margin = self.w // 2 + 8
        self.x = random.randint(ROAD_LEFT + margin, ROAD_RIGHT - margin)
        self.y = -self.h                   # start just above the screen

    def update(self):
        """Move the coin downward by its speed."""
        self.y += self.speed

    def draw(self, surface):
        """Draw the coin using its PNG image, or fall back to a circle."""
        if self.image:
            # Centre the image on (self.x, self.y)
            surface.blit(self.image,
                         (int(self.x - self.w // 2), int(self.y - self.h // 2)))
        else:
            cx, cy = int(self.x), int(self.y)
            pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
            pygame.draw.circle(surface, BLACK,      (cx, cy), self.radius, 2)
            # Shine highlight
            pygame.draw.circle(surface, WHITE,
                               (cx - self.radius // 3, cy - self.radius // 3),
                               self.radius // 4)

        # Draw the point value label beneath the coin (always visible)
        label = font_small.render(f"+{self.points}", True, YELLOW)
        surface.blit(label, (int(self.x) - label.get_width() // 2,
                              int(self.y) + self.h // 2 + 2))

    def off_screen(self):
        """True when the coin has scrolled past the bottom edge."""
        return self.y - self.h // 2 > HEIGHT

    def get_rect(self):
        """Collision rectangle centred on the coin's position."""
        return pygame.Rect(self.x - self.w // 2,
                           self.y - self.h // 2,
                           self.w, self.h)


# ─────────────────────────────────────────────
# ENEMY CAR
# ─────────────────────────────────────────────
ENEMY_COLORS = [RED, (180, 50, 180), (50, 180, 50), ORANGE, (50, 200, 200)]

class Enemy:
    """
    An oncoming enemy car.
    Uses enemy_car.png if available, otherwise a coloured rectangle.
    """
    W, H = 85, 100

    def __init__(self, speed):
        self.speed = speed
        self.x     = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.W - 5)
        self.y     = -self.H
        self.color = random.choice(ENEMY_COLORS)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        if IMG_ENEMY:
            surface.blit(IMG_ENEMY, (self.x, int(self.y)))
        else:
            draw_car_fallback(surface, self.x, int(self.y),
                              self.W, self.H, self.color)

    def off_screen(self):
        return self.y > HEIGHT

    def get_rect(self):
        # Shrink hitbox inward – feels fairer and matches the car body, not bumpers
        mx, my = 18, 12
        return pygame.Rect(self.x + mx, self.y + my,
                           self.W - mx * 2, self.H - my * 2)


# ─────────────────────────────────────────────
# PLAYER CAR
# ─────────────────────────────────────────────
class Player:
    """
    The player's car, controlled with LEFT / RIGHT arrow keys.
    Uses player_car.png if available, otherwise a blue rectangle.
    """
    W, H  = 70, 100
    SPEED = 5

    def __init__(self):
        self.x = WIDTH // 2 - self.W // 2
        self.y = HEIGHT - self.H - 20

    def move(self, keys):
        """Horizontal movement clamped within road boundaries."""
        if keys[pygame.K_LEFT]:
            self.x -= self.SPEED
        if keys[pygame.K_RIGHT]:
            self.x += self.SPEED
        self.x = max(ROAD_LEFT + 2, min(self.x, ROAD_RIGHT - self.W - 2))

    def draw(self, surface):
        if IMG_PLAYER:
            surface.blit(IMG_PLAYER, (self.x, self.y))
        else:
            draw_car_fallback(surface, self.x, self.y, self.W, self.H, BLUE)

    def get_rect(self):
        # Shrink hitbox inward so edge-grazing cars don't instantly kill you
        mx, my = 14, 10
        return pygame.Rect(self.x + mx, self.y + my,
                           self.W - mx * 2, self.H - my * 2)


# ─────────────────────────────────────────────
# ROAD STRIPE (scrolling dashes)
# ─────────────────────────────────────────────
class RoadStripe:
    """Dashed centre-line stripe that scrolls downward."""
    H_PX = 50
    GAP  = 30

    def __init__(self, y):
        self.y = y

    def update(self, speed):
        self.y += speed
        if self.y > HEIGHT + self.GAP:
            self.y -= (self.H_PX + self.GAP) * 6

    def draw(self, surface):
        mid = WIDTH // 2
        pygame.draw.rect(surface, LINE_COLOR, (mid - 3, int(self.y), 6, self.H_PX))


# ─────────────────────────────────────────────
# ROAD BACKGROUND
# ─────────────────────────────────────────────
def draw_road(surface):
    """Draw the road (PNG texture or plain colour) plus grass shoulders."""
    # Grass strips on the sides
    surface.fill(GRASS)
    if IMG_ROAD:
        # Tile or stretch the road texture
        surface.blit(IMG_ROAD, (ROAD_LEFT, 0))
    else:
        pygame.draw.rect(surface, ROAD_COLOR,
                         (ROAD_LEFT, 0, ROAD_W, HEIGHT))
    # White kerb lines
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT,      0, 5, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 5, 0, 5, HEIGHT))


# ─────────────────────────────────────────────
# HUD  (score, coin count, level)
# ─────────────────────────────────────────────
def draw_hud(surface, total_coins, score, level, enemy_speed, dodged):
    """Render the heads-up display."""

    # ── Top-right: coin counter with gold circle icon ──
    ix, iy = WIDTH - 170, 10
    pygame.draw.circle(surface, GOLD,  (ix, iy + 9), 11)
    pygame.draw.circle(surface, BLACK, (ix, iy + 9), 11, 2)
    ct = font_medium.render(f"x {total_coins}", True, WHITE)
    surface.blit(ct, (ix + 16, iy))

    # ── Top-left: score ──
    surface.blit(font_medium.render(f"Score: {score}", True, WHITE),
                 (ROAD_LEFT + 4, 10))

    # ── Second row: level & current speed ──
    surface.blit(font_small.render(f"Level: {level}   Spd: {enemy_speed:.1f}",
                                   True, (180, 180, 180)),
                 (ROAD_LEFT + 4, 36))

    # ── Third row: dodged enemies counter ──
    surface.blit(font_small.render(f"Dodged: {dodged}",
                                   True, (120, 220, 255)),
                 (ROAD_LEFT + 4, 56))

    # ── Speed-up progress bar ──
    # Shows how many coins into the current level the player is,
    # and how many are left until the next speed increase.
    coins_in_level  = total_coins % COINS_PER_LEVEL   # progress within current level
    coins_remaining = COINS_PER_LEVEL - coins_in_level

    bar_x  = ROAD_LEFT + 4
    bar_y  = 76
    bar_w  = 160
    bar_h  = 10
    fill_w = int(bar_w * coins_in_level / COINS_PER_LEVEL)

    # Flash the bar red when only 1–2 coins away from speed-up
    if coins_remaining <= 2:
        bar_color = (255, 80, 80)
    elif coins_remaining <= 4:
        bar_color = (255, 180, 0)
    else:
        bar_color = (80, 200, 80)

    # Background track
    pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    # Filled portion
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
    # Outline
    pygame.draw.rect(surface, (140, 140, 140), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    # Label: "Speed up in N coins"
    label_color = (255, 80, 80) if coins_remaining <= 2 else (200, 200, 200)
    spd_label = font_small.render(f"Speed up in {coins_remaining} coin{'s' if coins_remaining != 1 else ''}",
                                   True, label_color)
    surface.blit(spd_label, (bar_x + bar_w + 8, bar_y - 1))


# ─────────────────────────────────────────────
# OVERLAY SCREENS (start / game-over)
# ─────────────────────────────────────────────
def show_screen(surface, title, subtitle="Press SPACE to play"):
    """Darken the screen and show a centred title + subtitle."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surface.blit(overlay, (0, 0))
    t1 = font_large.render(title,    True, YELLOW)
    t2 = font_medium.render(subtitle, True, WHITE)
    surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()


# ─────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────
def main():
    # Build the initial set of road stripes
    spacing = RoadStripe.H_PX + RoadStripe.GAP
    stripes  = [RoadStripe(y) for y in range(0, HEIGHT, spacing)]

    # ── Start screen ──
    draw_road(screen)
    show_screen(screen, "RACER", "Press SPACE to start")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                break
        else:
            continue
        break

    # ── Initialise game-state variables ──
    player       = Player()
    enemies      = []
    coins        = []

    total_coins  = 0      # raw number of coins collected (for level gating)
    score        = 0      # weighted score (bronze=1, silver=3, gold=5)
    level        = 1
    dodged       = 0      # number of enemy cars successfully avoided

    base_speed   = 3.0
    enemy_speed  = base_speed
    road_speed   = base_speed

    enemy_timer    = 0
    enemy_interval = 90   # frames between enemy spawns (decreases each level)

    coin_timer     = 0
    coin_interval  = 60   # frames between coin spawns

    running = True

    while running:
        clock.tick(FPS)

        # ── Event handling ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # ── Player movement ──
        player.move(pygame.key.get_pressed())

        # ── Spawn enemy cars ──
        enemy_timer += 1
        if enemy_timer >= enemy_interval:
            enemies.append(Enemy(enemy_speed))
            enemy_timer    = 0
            enemy_interval = max(45, 90 - level * 4)   # shorter gap at higher levels

        # ── Spawn coins ──
        coin_timer += 1
        if coin_timer >= coin_interval:
            coins.append(Coin(road_speed))
            coin_timer = 0

        # ── Update positions ──
        for e in enemies: e.update()
        for c in coins:   c.update()
        for s in stripes:  s.update(road_speed)

        # Remove off-screen objects; count each enemy that scrolls past as dodged
        before    = len(enemies)
        enemies   = [e for e in enemies if not e.off_screen()]
        dodged   += before - len(enemies)   # each removed enemy was successfully avoided
        coins     = [c for c in coins if not c.off_screen()]

        # ── Collision: player ↔ enemy (crash) ──
        player_rect = player.get_rect()
        for e in enemies:
            if player_rect.colliderect(e.get_rect()):
                # Play crash sound then end the game
                if SND_CRASH:
                    SND_CRASH.play()
                pygame.time.delay(300)   # brief pause so the sound plays
                running = False
                break

        # ── Collision: player ↔ coin (collect) ──
        for c in list(coins):
            if player_rect.colliderect(c.get_rect()):
                total_coins += 1
                score       += c.points   # weighted by coin type
                coins.remove(c)
                if SND_COIN:
                    SND_COIN.play()

        # ── Level progression ──
        # Every COINS_PER_LEVEL coins collected increases speed and level
        new_level = total_coins // COINS_PER_LEVEL + 1
        if new_level > level:
            level        = new_level
            enemy_speed += ENEMY_SPEED_INCREMENT
            road_speed  += ENEMY_SPEED_INCREMENT
            # Apply new speed to all active objects immediately
            for e in enemies: e.speed = enemy_speed
            for c in coins:   c.speed = road_speed

        # ── Draw frame ──
        draw_road(screen)
        for s in stripes:  s.draw(screen)
        for e in enemies:  e.draw(screen)
        for c in coins:    c.draw(screen)
        player.draw(screen)
        draw_hud(screen, total_coins, score, level, enemy_speed, dodged)
        pygame.display.flip()

    # ── Game-Over screen ──
    draw_road(screen)                # keep the road visible behind overlay
    show_screen(screen, "GAME OVER",
                f"Score:{score}  Coins:{total_coins}  Dodged:{dodged}  |  SPACE")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()   # restart from the beginning
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()