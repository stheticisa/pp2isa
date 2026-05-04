"""
racer.py  —  TSIS 3: Advanced Racer Game
=========================================
Extends Practice 10 & 11 with:
  3.1  Lane hazards (oil spills, slow zones), nitro boost strips
  3.2  Traffic cars, road obstacles, safe spawn logic, difficulty scaling
  3.3  Three power-ups: Nitro, Shield, Repair
  3.4  Score (coins + distance + bonuses), distance meter, leaderboard
  3.5  Main Menu, Settings, Game Over, Leaderboard screens
"""

import pygame
import random
import sys
import os
import math
from persistence import load_settings, save_settings, load_leaderboard, add_entry
from ui import Button, draw_title, draw_text, draw_overlay

# ─────────────────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 520, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer — TSIS 3")
clock = pygame.time.Clock()
FPS   = 60

# ── Colours ──
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
YELLOW     = (255, 220,   0)
GOLD       = (255, 180,   0)
RED        = (220,  50,  50)
ORANGE     = (255, 140,   0)
GREEN      = (60,  200,  80)
CYAN       = (0,   220, 220)
PURPLE     = (180,  60, 220)
DARK       = (18,  20,  30)
ROAD_COL   = (55,  55,  55)
GRASS_COL  = (30,  90,  30)
LINE_COL   = (200, 200, 200)

# ── Road geometry ──
ROAD_LEFT  = 30
ROAD_RIGHT = WIDTH - 30
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

# ── Difficulty multipliers ──
DIFFICULTY = {
    "easy":   {"enemy_speed": 2.5, "spawn_interval": 100, "obstacle_freq": 0.003},
    "normal": {"enemy_speed": 3.0, "spawn_interval": 80,  "obstacle_freq": 0.005},
    "hard":   {"enemy_speed": 4.0, "spawn_interval": 60,  "obstacle_freq": 0.008},
}

COINS_PER_LEVEL      = 10
SPEED_INCREMENT      = 0.4
POWERUP_TIMEOUT      = 300   # frames a power-up stays on road if uncollected

# ── Fonts ──
font_lg  = pygame.font.SysFont("monospace", 30, bold=True)
font_md  = pygame.font.SysFont("monospace", 20, bold=True)
font_sm  = pygame.font.SysFont("monospace", 14)

# ── Load optional assets ──
def _load_img(name, size):
    path = os.path.join(os.path.dirname(__file__), "assets", name)
    if not os.path.exists(path):
        return None
    try:
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except Exception:
        return None

def _load_snd(name):
    path = os.path.join(os.path.dirname(__file__), "assets", name)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

IMG_PLAYER  = _load_img("player_car.png",  (70, 100))
IMG_ENEMY   = _load_img("enemy_car.png",   (85, 100))
IMG_COIN_B  = _load_img("coin_bronze.png", (36, 36))
IMG_COIN_S  = _load_img("coin_silver.png", (42, 42))
IMG_COIN_G  = _load_img("coin_gold.png",   (50, 50))
SND_COIN    = _load_snd("sound_coin.wav")
SND_CRASH   = _load_snd("sound_crash.wav")
SND_POWERUP = _load_snd("sound_coin.wav")   # reuse coin sound for power-ups

COIN_IMGS   = {"bronze": IMG_COIN_B, "silver": IMG_COIN_S, "gold": IMG_COIN_G}

os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# GAME OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class RoadStripe:
    H, GAP = 50, 30
    def __init__(self, y): self.y = y
    def update(self, spd):
        self.y += spd
        if self.y > HEIGHT + self.GAP:
            self.y -= (self.H + self.GAP) * 6
    def draw(self, surf):
        mid = WIDTH // 2
        pygame.draw.rect(surf, LINE_COL, (mid - 3, int(self.y), 6, self.H))


class LaneHazard:
    """Oil spill or slow zone — slows the player on contact."""
    TYPES = [
        {"name": "oil",   "color": (40, 40, 60),   "effect": "slow",  "w": 60, "h": 30},
        {"name": "bump",  "color": (120, 80, 40),   "effect": "slow",  "w": 80, "h": 12},
        {"name": "nitro", "color": (0,  200, 255),  "effect": "boost", "w": 60, "h": 20},
    ]

    def __init__(self, speed):
        t       = random.choice(self.TYPES)
        self.effect = t["effect"]
        self.color  = t["color"]
        self.w      = t["w"]
        self.h      = t["h"]
        self.speed  = speed
        self.x      = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - self.w - 10)
        self.y      = float(-self.h)

    def update(self): self.y += self.speed
    def off_screen(self): return self.y > HEIGHT

    def draw(self, surf):
        r = pygame.Rect(self.x, int(self.y), self.w, self.h)
        pygame.draw.rect(surf, self.color, r, border_radius=4)
        lbl = font_sm.render("OIL" if self.effect == "slow" else "NITRO", True, WHITE)
        surf.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

    def get_rect(self): return pygame.Rect(self.x, int(self.y), self.w, self.h)


class Obstacle:
    """Static-ish road obstacle (barrier / pothole)."""
    TYPES = [
        {"name": "barrier",  "color": (220, 60, 60),  "w": 30, "h": 18},
        {"name": "pothole",  "color": (40,  30, 20),  "w": 28, "h": 20},
        {"name": "barrier2", "color": (240, 160, 0),  "w": 80, "h": 14},
    ]

    def __init__(self, speed, player_rect):
        t          = random.choice(self.TYPES)
        self.color = t["color"]
        self.w     = t["w"]
        self.h     = t["h"]
        self.speed = speed
        # Safe spawn: not directly above the player
        for _ in range(20):
            self.x = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.w - 5)
            self.y = float(-self.h - random.randint(0, 200))
            if not self.get_rect().colliderect(player_rect):
                break

    def update(self): self.y += self.speed
    def off_screen(self): return self.y > HEIGHT
    def get_rect(self): return pygame.Rect(self.x, int(self.y), self.w, self.h)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.get_rect(), border_radius=3)


class Coin:
    TYPES = [
        ("bronze", 1,  18, (205,127, 50), 0.55),
        ("silver", 3,  21, (192,192,192), 0.30),
        ("gold",   5,  25, (255,215,  0), 0.15),
    ]

    def __init__(self, speed):
        rng   = random.random(); cumul = 0.0; self.kind = self.TYPES[0]
        for ct in self.TYPES:
            cumul += ct[4]
            if rng <= cumul: self.kind = ct; break
        self.name   = self.kind[0]
        self.points = self.kind[1]
        self.radius = self.kind[2]
        self.color  = self.kind[3]
        self.speed  = speed
        self.image  = COIN_IMGS.get(self.name)
        self.w = self.image.get_width()  if self.image else self.radius * 2
        self.h = self.image.get_height() if self.image else self.radius * 2
        m      = self.w // 2 + 8
        self.x = random.randint(ROAD_LEFT + m, ROAD_RIGHT - m)
        self.y = float(-self.h)

    def update(self): self.y += self.speed
    def off_screen(self): return self.y - self.h // 2 > HEIGHT

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (int(self.x - self.w//2), int(self.y - self.h//2)))
        else:
            cx, cy = int(self.x), int(self.y)
            pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
            pygame.draw.circle(surf, BLACK, (cx, cy), self.radius, 2)
        lbl = font_sm.render(f"+{self.points}", True, YELLOW)
        surf.blit(lbl, (int(self.x) - lbl.get_width()//2, int(self.y) + self.h//2 + 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)


class PowerUp:
    """Nitro, Shield, or Repair power-up."""
    DEFS = {
        "Nitro":  {"color": CYAN,   "symbol": "⚡N"},
        "Shield": {"color": PURPLE, "symbol": "🛡S"},
        "Repair": {"color": GREEN,  "symbol": "🔧R"},
    }
    W = H = 32

    def __init__(self, speed):
        name         = random.choice(list(self.DEFS.keys()))
        self.name    = name
        self.color   = self.DEFS[name]["color"]
        self.symbol  = self.DEFS[name]["symbol"]
        self.speed   = speed
        self.x       = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20 - self.W)
        self.y       = float(-self.H)
        self.timer   = POWERUP_TIMEOUT   # frames until auto-disappear

    def update(self):
        self.y     += self.speed
        self.timer -= 1

    def off_screen(self): return self.y > HEIGHT or self.timer <= 0

    def draw(self, surf):
        r = pygame.Rect(self.x, int(self.y), self.W, self.H)
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        pygame.draw.rect(surf, WHITE, r, 2, border_radius=6)
        lbl = font_sm.render(self.symbol, True, BLACK)
        surf.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

    def get_rect(self): return pygame.Rect(self.x, int(self.y), self.W, self.H)


class Enemy:
    W, H = 85, 100
    COLORS = [RED, (180,50,180), (50,180,50), ORANGE, (50,200,200)]

    def __init__(self, speed, player_rect):
        self.speed = speed
        self.color = random.choice(self.COLORS)
        # Safe spawn
        for _ in range(20):
            self.x = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.W - 5)
            self.y = float(-self.H - random.randint(0, 100))
            if not self.get_rect().colliderect(player_rect):
                break

    def update(self): self.y += self.speed
    def off_screen(self): return self.y > HEIGHT

    def draw(self, surf):
        if IMG_ENEMY:
            surf.blit(IMG_ENEMY, (self.x, int(self.y)))
        else:
            r = pygame.Rect(self.x, int(self.y), self.W, self.H)
            pygame.draw.rect(surf, self.color, r, border_radius=8)
            win = (160, 220, 255)
            pygame.draw.rect(surf, win, (self.x+8, int(self.y)+8, self.W-16, self.H//3), border_radius=4)

    def get_rect(self):
        mx, my = 18, 12
        return pygame.Rect(self.x+mx, self.y+my, self.W-mx*2, self.H-my*2)


class Player:
    W, H  = 70, 100
    SPEED = 5

    def __init__(self, color):
        self.x         = WIDTH // 2 - self.W // 2
        self.y         = HEIGHT - self.H - 20
        self.color     = tuple(color)
        # Power-up state
        self.shield    = False
        self.nitro     = False
        self.nitro_end = 0      # pygame ticks
        self.slow      = False
        self.slow_end  = 0
        self.speed_mult = 1.0

    def move(self, keys):
        spd = int(self.SPEED * self.speed_mult)
        if keys[pygame.K_LEFT]:  self.x -= spd
        if keys[pygame.K_RIGHT]: self.x += spd
        self.x = max(ROAD_LEFT + 2, min(self.x, ROAD_RIGHT - self.W - 2))

    def update_powerups(self):
        now = pygame.time.get_ticks()
        if self.nitro and now > self.nitro_end:
            self.nitro      = False
            self.speed_mult = 1.0
        if self.slow and now > self.slow_end:
            self.slow       = False
            self.speed_mult = 1.0

    def apply_powerup(self, name):
        now = pygame.time.get_ticks()
        if name == "Nitro":
            self.nitro      = True
            self.nitro_end  = now + 4000
            self.speed_mult = 1.6
        elif name == "Shield":
            self.shield     = True
        elif name == "Repair":
            pass   # instant — handled in main loop

    def activate_slow(self):
        now            = pygame.time.get_ticks()
        self.slow      = True
        self.slow_end  = now + 2000
        self.speed_mult = 0.6

    def draw(self, surf):
        if IMG_PLAYER:
            surf.blit(IMG_PLAYER, (self.x, self.y))
        else:
            r = pygame.Rect(self.x, self.y, self.W, self.H)
            pygame.draw.rect(surf, self.color, r, border_radius=8)
            win = (160, 220, 255)
            pygame.draw.rect(surf, win, (self.x+6, self.y+6, self.W-12, self.H//3), border_radius=4)

        if self.shield:
            pygame.draw.circle(surf, PURPLE,
                               (self.x + self.W//2, self.y + self.H//2),
                               max(self.W, self.H)//2 + 6, 3)

    def get_rect(self):
        mx, my = 14, 10
        return pygame.Rect(self.x+mx, self.y+my, self.W-mx*2, self.H-my*2)


# ─────────────────────────────────────────────────────────────────────────────
# DRAWING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def draw_road(surf):
    surf.fill(GRASS_COL)
    pygame.draw.rect(surf, ROAD_COL, (ROAD_LEFT, 0, ROAD_W, HEIGHT))
    pygame.draw.rect(surf, WHITE, (ROAD_LEFT, 0, 5, HEIGHT))
    pygame.draw.rect(surf, WHITE, (ROAD_RIGHT-5, 0, 5, HEIGHT))


def draw_hud(surf, player, total_coins, score, level, speed, dodged, distance, active_pu, pu_end):
    now = pygame.time.get_ticks()

    # Score
    surf.blit(font_md.render(f"Score: {score}", True, WHITE), (ROAD_LEFT+4, 8))
    surf.blit(font_sm.render(f"Lvl:{level}  Spd:{speed:.1f}", True, GRAY), (ROAD_LEFT+4, 34))
    surf.blit(font_sm.render(f"Dodged:{dodged}", True, CYAN), (ROAD_LEFT+4, 52))
    surf.blit(font_sm.render(f"Dist:{int(distance)}m", True, (200,200,200)), (ROAD_LEFT+4, 70))

    # Speed-up bar
    coins_in = total_coins % COINS_PER_LEVEL
    ratio    = coins_in / COINS_PER_LEVEL
    rem      = COINS_PER_LEVEL - coins_in
    bx, by, bw, bh = ROAD_LEFT+4, 90, 150, 9
    bar_col = (255,80,80) if rem <= 2 else ((255,180,0) if rem <= 4 else (80,200,80))
    pygame.draw.rect(surf, (60,60,60), (bx,by,bw,bh), border_radius=4)
    if ratio > 0:
        pygame.draw.rect(surf, bar_col, (bx,by,int(bw*ratio),bh), border_radius=4)
    pygame.draw.rect(surf, (140,140,140), (bx,by,bw,bh), 1, border_radius=4)
    lc = (255,80,80) if rem<=2 else (200,200,200)
    surf.blit(font_sm.render(f"Speed up in {rem}", True, lc), (bx+bw+6, by-1))

    # Coin counter (top-right)
    ix, iy = WIDTH - 160, 8
    pygame.draw.circle(surf, GOLD, (ix, iy+9), 11)
    pygame.draw.circle(surf, BLACK, (ix, iy+9), 11, 2)
    surf.blit(font_md.render(f"x{total_coins}", True, WHITE), (ix+16, iy))

    # Active power-up indicator
    if active_pu:
        remain_s = max(0, (pu_end - now) / 1000)
        pu_cols  = {"Nitro": CYAN, "Shield": PURPLE, "Repair": GREEN}
        col      = pu_cols.get(active_pu, WHITE)
        surf.blit(font_md.render(f"⚡{active_pu}", True, col), (WIDTH-160, 40))
        if pu_end > 0:
            surf.blit(font_sm.render(f"{remain_s:.1f}s", True, col), (WIDTH-160, 64))

    # Quit button
    qr = pygame.Rect(WIDTH-58, 8, 50, 24)
    hov = qr.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surf, (180,40,40) if hov else (120,30,30), qr, border_radius=5)
    pygame.draw.rect(surf, (220,80,80), qr, 1, border_radius=5)
    surf.blit(font_sm.render("QUIT", True, WHITE),
              (qr.centerx - font_sm.size("QUIT")[0]//2, qr.centery - 7))
    return qr

GRAY = (160,160,160)

# ─────────────────────────────────────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────────────────────────────────────

def username_screen():
    """Prompt for username before game starts."""
    username = ""
    font_inp = pygame.font.SysFont("monospace", 24, bold=True)
    font_lbl = pygame.font.SysFont("monospace", 16)
    while True:
        screen.fill(DARK)
        draw_title(screen, "RACER", 80)
        draw_text(screen, "Enter your name:", WIDTH//2 - 100, 200, size=20)

        # Input box
        box = pygame.Rect(WIDTH//2 - 120, 240, 240, 44)
        pygame.draw.rect(screen, (50,50,70), box, border_radius=8)
        pygame.draw.rect(screen, YELLOW, box, 2, border_radius=8)
        inp = font_inp.render(username + "|", True, WHITE)
        screen.blit(inp, (box.x+10, box.y+8))

        draw_text(screen, "Press ENTER to continue", WIDTH//2-130, 310, color=GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and len(username) < 20:
                        username += ch
        clock.tick(60)


def main_menu(settings):
    """Main menu with Play, Leaderboard, Settings, Quit."""
    buttons = {
        "play":   Button((WIDTH//2-100, 200, 200, 50), "▶  Play",   color=(40,140,60)),
        "leader": Button((WIDTH//2-100, 270, 200, 50), "🏆 Scores", color=(60,80,160)),
        "settings":Button((WIDTH//2-100,340, 200, 50), "⚙  Settings"),
        "quit":   Button((WIDTH//2-100, 410, 200, 50), "✖  Quit",   color=(140,40,40)),
    }
    while True:
        screen.fill(DARK)
        draw_road(screen)
        draw_overlay(screen, 160)
        draw_title(screen, "RACER", 100)
        draw_text(screen, "TSIS 3", WIDTH//2 - 35, 158, color=GRAY, size=18)

        mp = pygame.mouse.get_pos()
        for btn in buttons.values():
            btn.draw(screen, mp)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if buttons["play"].is_clicked(event):       return "play"
            if buttons["leader"].is_clicked(event):     return "leader"
            if buttons["settings"].is_clicked(event):   return "settings"
            if buttons["quit"].is_clicked(event):
                pygame.quit(); sys.exit()
        clock.tick(60)


def leaderboard_screen():
    """Display top 10 scores."""
    entries = load_leaderboard()
    back    = Button((WIDTH//2-60, HEIGHT-70, 120, 44), "◀ Back")

    while True:
        screen.fill(DARK)
        draw_title(screen, "TOP 10", 30, size=36)

        hdr = ["#", "Name", "Score", "Dist", "Coins"]
        xs  = [20, 55, 185, 280, 360]
        for xi, h in zip(xs, hdr):
            draw_text(screen, h, xi, 90, color=YELLOW, size=16, bold=True)
        pygame.draw.line(screen, GRAY, (10, 112), (WIDTH-10, 112), 1)

        for i, e in enumerate(entries):
            y    = 122 + i * 34
            col  = YELLOW if i == 0 else WHITE
            vals = [str(i+1), e["name"][:10], str(e["score"]),
                    f'{e["distance"]}m', str(e["coins"])]
            for xi, v in zip(xs, vals):
                draw_text(screen, v, xi, y, color=col, size=15)

        mp = pygame.mouse.get_pos()
        back.draw(screen, mp)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if back.is_clicked(event):
                return
        clock.tick(60)


def settings_screen(settings):
    """Settings: sound toggle, car colour, difficulty."""
    CAR_COLORS = [
        ("Blue",   [50, 100, 220]),
        ("Red",    [220, 50, 50]),
        ("Green",  [50, 180, 80]),
        ("Orange", [255, 140, 0]),
        ("Purple", [160, 60, 200]),
    ]
    DIFFS = ["easy", "normal", "hard"]

    cur_color_idx = next((i for i, (_, c) in enumerate(CAR_COLORS)
                          if c == settings["car_color"]), 0)
    cur_diff_idx  = DIFFS.index(settings["difficulty"]) if settings["difficulty"] in DIFFS else 1

    save_btn = Button((WIDTH//2-60, HEIGHT-70, 120, 44), "Save & Back", color=(40,140,60))

    while True:
        screen.fill(DARK)
        draw_title(screen, "SETTINGS", 40, size=36)

        # Sound toggle
        s_on  = settings["sound"]
        s_lbl = "Sound:  ON " if s_on else "Sound:  OFF"
        s_col = GREEN if s_on else RED
        draw_text(screen, s_lbl, WIDTH//2-80, 130, color=s_col, size=20)
        toggle = pygame.Rect(WIDTH//2+60, 126, 80, 32)
        pygame.draw.rect(screen, s_col, toggle, border_radius=6)
        draw_text(screen, "Toggle", toggle.x+8, toggle.y+6, size=16)

        # Car colour
        draw_text(screen, "Car Colour:", WIDTH//2-80, 200, size=18)
        cname, cval = CAR_COLORS[cur_color_idx]
        pygame.draw.circle(screen, tuple(cval), (WIDTH//2+40, 212), 18)
        pygame.draw.circle(screen, WHITE,        (WIDTH//2+40, 212), 18, 2)
        draw_text(screen, f"< {cname} >", WIDTH//2-20, 232, size=14, color=GRAY)
        l_arr = pygame.Rect(WIDTH//2-60, 200, 36, 28)
        r_arr = pygame.Rect(WIDTH//2+80, 200, 36, 28)
        pygame.draw.rect(screen, (60,60,80), l_arr, border_radius=4)
        pygame.draw.rect(screen, (60,60,80), r_arr, border_radius=4)
        draw_text(screen, "◀", l_arr.x+8, l_arr.y+4)
        draw_text(screen, "▶", r_arr.x+8, r_arr.y+4)

        # Difficulty
        draw_text(screen, "Difficulty:", WIDTH//2-80, 290, size=18)
        diff_lbl = DIFFS[cur_diff_idx].upper()
        d_cols   = {"EASY": GREEN, "NORMAL": YELLOW, "HARD": RED}
        draw_text(screen, f"< {diff_lbl} >", WIDTH//2-40, 320, size=16,
                  color=d_cols.get(diff_lbl, WHITE))
        dl = pygame.Rect(WIDTH//2-80, 312, 36, 28)
        dr = pygame.Rect(WIDTH//2+60, 312, 36, 28)
        pygame.draw.rect(screen, (60,60,80), dl, border_radius=4)
        pygame.draw.rect(screen, (60,60,80), dr, border_radius=4)
        draw_text(screen, "◀", dl.x+8, dl.y+4)
        draw_text(screen, "▶", dr.x+8, dr.y+4)

        mp = pygame.mouse.get_pos()
        save_btn.draw(screen, mp)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if toggle.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                if l_arr.collidepoint(mx, my):
                    cur_color_idx = (cur_color_idx - 1) % len(CAR_COLORS)
                if r_arr.collidepoint(mx, my):
                    cur_color_idx = (cur_color_idx + 1) % len(CAR_COLORS)
                if dl.collidepoint(mx, my):
                    cur_diff_idx = (cur_diff_idx - 1) % len(DIFFS)
                if dr.collidepoint(mx, my):
                    cur_diff_idx = (cur_diff_idx + 1) % len(DIFFS)
                if save_btn.is_clicked(event):
                    settings["car_color"]  = list(CAR_COLORS[cur_color_idx][1])
                    settings["difficulty"] = DIFFS[cur_diff_idx]
                    save_settings(settings)
                    return
        clock.tick(60)


def game_over_screen(score, distance, coins, dodged):
    """Game Over screen with Retry and Main Menu buttons."""
    retry = Button((WIDTH//2-110, 380, 200, 48), "↺  Retry",    color=(40,140,60))
    menu  = Button((WIDTH//2+10,  380, 200, 48), "⌂  Main Menu",color=(60,80,160))

    while True:
        screen.fill(DARK)
        draw_overlay(screen, 180)
        draw_title(screen, "GAME OVER", HEIGHT//2 - 160, color=RED)
        draw_text(screen, f"Score    : {score}",    WIDTH//2-100, HEIGHT//2-80, size=20)
        draw_text(screen, f"Distance : {int(distance)}m", WIDTH//2-100, HEIGHT//2-50, size=20)
        draw_text(screen, f"Coins    : {coins}",    WIDTH//2-100, HEIGHT//2-20, size=20)
        draw_text(screen, f"Dodged   : {dodged}",   WIDTH//2-100, HEIGHT//2+10, size=20)

        mp = pygame.mouse.get_pos()
        retry.draw(screen, mp)
        menu.draw(screen, mp)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if retry.is_clicked(event): return "retry"
            if menu.is_clicked(event):  return "menu"
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAME
# ─────────────────────────────────────────────────────────────────────────────

def play_game(username, settings):
    diff_cfg = DIFFICULTY.get(settings.get("difficulty", "normal"), DIFFICULTY["normal"])

    # Stripes
    spacing = RoadStripe.H + RoadStripe.GAP
    stripes = [RoadStripe(y) for y in range(0, HEIGHT, spacing)]

    player      = Player(settings["car_color"])
    enemies     = []
    coins_list  = []
    hazards     = []
    obstacles   = []
    powerups    = []

    total_coins  = 0
    score        = 0
    level        = 1
    dodged       = 0
    distance     = 0.0

    base_speed    = diff_cfg["enemy_speed"]
    enemy_speed   = base_speed
    road_speed    = base_speed

    e_timer = 0
    e_int   = diff_cfg["spawn_interval"]
    c_timer = 0
    h_timer = 0
    o_timer = 0
    p_timer = 0

    # Power-up tracking
    active_pu    = None   # name of current power-up
    pu_end_time  = 0      # ticks when effect ends (0 = permanent like shield)

    running  = True
    quit_btn = pygame.Rect(WIDTH-58, 8, 50, 24)

    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu", score, distance, total_coins, dodged
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if quit_btn.collidepoint(event.pos):
                    return "menu", score, distance, total_coins, dodged

        player.move(pygame.key.get_pressed())
        player.update_powerups()

        # ── Spawn enemies ──
        e_timer += 1
        if e_timer >= e_int:
            enemies.append(Enemy(enemy_speed, player.get_rect()))
            e_timer = 0
            e_int   = max(35, diff_cfg["spawn_interval"] - level * 3)

        # ── Spawn coins ──
        c_timer += 1
        if c_timer >= 55:
            coins_list.append(Coin(road_speed))
            c_timer = 0

        # ── Spawn lane hazards ──
        h_timer += 1
        if h_timer >= 120:
            hazards.append(LaneHazard(road_speed))
            h_timer = 0

        # ── Spawn obstacles ──
        o_timer += 1
        if o_timer >= 90 and random.random() < diff_cfg["obstacle_freq"] * 30:
            obstacles.append(Obstacle(road_speed, player.get_rect()))
            o_timer = 0

        # ── Spawn power-ups ──
        p_timer += 1
        if p_timer >= 180 and not powerups:
            powerups.append(PowerUp(road_speed))
            p_timer = 0

        # ── Update ──
        for o in enemies:   o.update()
        for o in coins_list: o.update()
        for o in hazards:   o.update()
        for o in obstacles: o.update()
        for o in powerups:  o.update()
        for s in stripes:   s.update(road_speed)

        distance += road_speed / FPS   # metres per frame

        # Remove off-screen
        before   = len(enemies)
        enemies  = [e for e in enemies  if not e.off_screen()]
        dodged  += before - len(enemies)
        coins_list = [c for c in coins_list if not c.off_screen()]
        hazards    = [h for h in hazards    if not h.off_screen()]
        obstacles  = [o for o in obstacles  if not o.off_screen()]
        powerups   = [p for p in powerups   if not p.off_screen()]

        prect = player.get_rect()

        # ── Collision: enemy ──
        for e in enemies:
            if prect.colliderect(e.get_rect()):
                if player.shield:
                    player.shield = False
                    active_pu     = None
                    enemies.remove(e)
                else:
                    if SND_CRASH and settings.get("sound"): SND_CRASH.play()
                    pygame.time.delay(250)
                    running = False
                break

        # ── Collision: obstacle ──
        for o in list(obstacles):
            if prect.colliderect(o.get_rect()):
                if player.shield:
                    player.shield = False
                    active_pu     = None
                    obstacles.remove(o)
                else:
                    running = False
                break

        # ── Collision: hazard ──
        for h in hazards:
            if prect.colliderect(h.get_rect()):
                if h.effect == "slow":
                    player.activate_slow()
                else:   # nitro strip
                    player.nitro      = True
                    player.nitro_end  = now + 3000
                    player.speed_mult = 1.5

        # ── Collision: coin ──
        for c in list(coins_list):
            if prect.colliderect(c.get_rect()):
                total_coins += 1
                score       += c.points
                coins_list.remove(c)
                if SND_COIN and settings.get("sound"): SND_COIN.play()

        # ── Collision: power-up ──
        for p in list(powerups):
            if prect.colliderect(p.get_rect()):
                active_pu = p.name
                player.apply_powerup(p.name)
                pu_end_time = now + (4000 if p.name == "Nitro" else 0)
                powerups.remove(p)
                if SND_POWERUP and settings.get("sound"): SND_POWERUP.play()
                score += 10   # bonus for collecting power-up

        # ── Level up ──
        new_level = total_coins // COINS_PER_LEVEL + 1
        if new_level > level:
            level        = new_level
            enemy_speed += SPEED_INCREMENT
            road_speed  += SPEED_INCREMENT
            for e in enemies: e.speed = enemy_speed
            for c in coins_list: c.speed = road_speed

        # ── Distance bonus ──
        score = total_coins * 3 + int(distance) // 10 + (level - 1) * 50

        # ── Draw ──
        draw_road(screen)
        for s in stripes:    s.draw(screen)
        for h in hazards:    h.draw(screen)
        for o in obstacles:  o.draw(screen)
        for e in enemies:    e.draw(screen)
        for c in coins_list: c.draw(screen)
        for p in powerups:   p.draw(screen)
        player.draw(screen)
        quit_btn = draw_hud(screen, player, total_coins, score, level,
                            enemy_speed, dodged, distance, active_pu, pu_end_time)
        pygame.display.flip()

    return "gameover", score, distance, total_coins, dodged


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    settings = load_settings()
    username = username_screen()

    while True:
        action = main_menu(settings)

        if action == "play":
            result = play_game(username, settings)
            outcome, score, distance, coins, dodged = result
            add_entry(username, score, int(distance), coins)
            if outcome == "gameover":
                choice = game_over_screen(score, distance, coins, dodged)
                if choice == "retry":
                    continue   # restart loop → main menu → play
            # else "menu" → just loop back to main menu

        elif action == "leader":
            leaderboard_screen()

        elif action == "settings":
            settings_screen(settings)
            settings = load_settings()   # reload after save


if __name__ == "__main__":
    main()