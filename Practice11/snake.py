import pygame
import random
import sys

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# ── Grid & window ──
CELL        = 20          # pixels per grid cell
COLS        = 28          # cells wide
ROWS        = 26          # cells tall
HUD_HEIGHT  = 60          # pixels reserved for the HUD strip above the grid

SCREEN_W    = COLS * CELL
SCREEN_H    = ROWS * CELL + HUD_HEIGHT
screen      = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# ── Colours ──
BG_DARK      = (15,  20,  30)
GRID_COLOR   = (25,  32,  45)
WALL_COLOR   = (80,  80, 100)
SNAKE_HEAD   = (80, 220,  80)
SNAKE_BODY   = (50, 170,  50)
SNAKE_EYE    = (10,  10,  10)
HUD_BG       = (20,  25,  38)
WHITE        = (255, 255, 255)
YELLOW       = (255, 220,   0)
GRAY         = (140, 140, 140)

# Food type definitions: (name, points, color, probability, lifetime_frames)
# Lifetime = how many frames before the food disappears (Practice 11 task 2)
FOOD_TYPES = [
    # name,     pts, colour,           prob,  lifetime
    ("apple",    1,  (220,  60,  60),  0.55,  300),   # common,   5 s at 60 fps
    ("cherry",   2,  (180,   0, 100),  0.30,  240),   # uncommon, 4 s
    ("star",     5,  (255, 220,   0),  0.15,  180),   # rare,     3 s
]

# ── Fonts ──
font_large  = pygame.font.SysFont("monospace", 26, bold=True)
font_medium = pygame.font.SysFont("monospace", 18, bold=True)
font_small  = pygame.font.SysFont("monospace", 13)

# ── Game constants ──
FOODS_PER_LEVEL = 3         # how many foods to eat before levelling up
BASE_FPS        = 8         # starting game speed (updates per second)
FPS_INCREMENT   = 2         # extra FPS per level
MAX_FPS         = 24        # cap so the game doesn't become unplayable
WALL_THICKNESS  = 1         # wall is 1 cell thick around the border

# ── Directions ──
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)


# ─────────────────────────────────────────────
# GRID helpers
# ─────────────────────────────────────────────
def cell_rect(col, row):
    """Return the pixel Rect for a given grid cell."""
    return pygame.Rect(col * CELL, row * CELL + HUD_HEIGHT, CELL, CELL)


def is_wall(col, row):
    """Return True if (col, row) is a border wall cell."""
    return (col < WALL_THICKNESS or col >= COLS - WALL_THICKNESS or
            row < WALL_THICKNESS or row >= ROWS - WALL_THICKNESS)


def random_free_cell(occupied):
    """
    Pick a random grid cell that is not a wall and not in the occupied set.
    occupied: a set/list of (col, row) tuples already in use.
    """
    while True:
        col = random.randint(WALL_THICKNESS, COLS - WALL_THICKNESS - 1)
        row = random.randint(WALL_THICKNESS, ROWS - WALL_THICKNESS - 1)
        if (col, row) not in occupied:
            return col, row


# ─────────────────────────────────────────────
# FOOD class   (Practice 10: random placement; Practice 11: weighted + timer)
# ─────────────────────────────────────────────
class Food:
    """A food item with a random weighted type and a disappear timer."""

    def __init__(self, occupied):
        # Choose food type by probability weight
        rng   = random.random()
        cumul = 0.0
        self.kind = FOOD_TYPES[0]
        for ftype in FOOD_TYPES:
            cumul += ftype[4]          # index 4 = probability
            if rng <= cumul:
                self.kind = ftype
                break

        self.name     = self.kind[0]
        self.points   = self.kind[1]
        self.color    = self.kind[2]
        self.lifetime = self.kind[4]  # max frames before expiry
        self.timer    = self.lifetime  # counts down each frame

        # Place on a free cell (not wall, not snake)
        self.col, self.row = random_free_cell(occupied)

    def update(self):
        """Decrement the disappearance timer."""
        self.timer -= 1

    def expired(self):
        """Return True when the food's time is up."""
        return self.timer <= 0

    def draw(self, surface):
        """Draw the food with a pulsing alpha to warn when about to expire."""
        rect = cell_rect(self.col, self.row)

        # Compute flash intensity: starts fading when < 25 % lifetime left
        ratio = self.timer / self.lifetime
        if ratio < 0.25:
            # Alpha oscillates between 80 and 255 for a warning flash
            alpha = int(80 + 175 * abs(pygame.time.get_ticks() % 400 - 200) / 200)
        else:
            alpha = 255

        # Draw on a temp surface to support alpha
        food_surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pygame.draw.ellipse(food_surf, (*self.color, alpha),
                            (2, 2, CELL - 4, CELL - 4))
        surface.blit(food_surf, rect.topleft)

        # Timer bar underneath the food (shows remaining life as a thin line)
        bar_w = max(1, int((CELL - 4) * ratio))
        bar_rect = pygame.Rect(rect.x + 2, rect.bottom - 3, bar_w, 2)
        pygame.draw.rect(surface, WHITE, bar_rect)

    def pos(self):
        return (self.col, self.row)


# ─────────────────────────────────────────────
# SNAKE class
# ─────────────────────────────────────────────
class Snake:
    """The player-controlled snake."""

    def __init__(self):
        # Start in the middle, 3 cells long, moving right
        mid_col = COLS // 2
        mid_row = ROWS // 2
        self.body = [(mid_col - i, mid_row) for i in range(3)]
        self.direction   = RIGHT
        self.next_dir    = RIGHT
        self.grew        = False   # True for one frame after eating

    def set_direction(self, new_dir):
        """Change direction; prevent reversing directly into self."""
        opposite = (-new_dir[0], -new_dir[1])
        if new_dir != opposite:
            self.next_dir = new_dir

    def move(self):
        """Advance the snake one cell in the current direction."""
        self.direction = self.next_dir
        head_col, head_row = self.body[0]
        new_head = (head_col + self.direction[0],
                    head_row + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grew:
            self.body.pop()           # remove tail unless we just ate
        self.grew = False

    def grow(self):
        """Signal that the snake should grow on the next move."""
        self.grew = True

    def head(self):
        return self.body[0]

    def body_set(self):
        """Return body positions as a set for quick lookup."""
        return set(self.body)

    def self_collision(self):
        """Return True if the head overlaps any body segment."""
        return self.body[0] in self.body[1:]

    def draw(self, surface):
        """Render every body segment; the head has eyes."""
        for i, (col, row) in enumerate(self.body):
            rect  = cell_rect(col, row)
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(surface, color, rect, border_radius=4)
            # Draw eyes on the head
            if i == 0:
                eye_offset = 4
                dx, dy = self.direction
                # Perpendicular offsets for two eyes
                if dx == 0:   # moving vertically
                    eye1 = (rect.centerx - 4, rect.centery + dy * eye_offset)
                    eye2 = (rect.centerx + 4, rect.centery + dy * eye_offset)
                else:          # moving horizontally
                    eye1 = (rect.centerx + dx * eye_offset, rect.centery - 4)
                    eye2 = (rect.centerx + dx * eye_offset, rect.centery + 4)
                pygame.draw.circle(surface, SNAKE_EYE, eye1, 2)
                pygame.draw.circle(surface, SNAKE_EYE, eye2, 2)


# ─────────────────────────────────────────────
# DRAW functions
# ─────────────────────────────────────────────
def draw_grid(surface):
    """Draw background grid and wall cells."""
    surface.fill(BG_DARK)

    # HUD background
    pygame.draw.rect(surface, HUD_BG, (0, 0, SCREEN_W, HUD_HEIGHT))
    pygame.draw.line(surface, WALL_COLOR, (0, HUD_HEIGHT), (SCREEN_W, HUD_HEIGHT), 2)

    # Grid lines
    for col in range(COLS):
        for row in range(ROWS):
            r = cell_rect(col, row)
            if is_wall(col, row):
                pygame.draw.rect(surface, WALL_COLOR, r)
            else:
                pygame.draw.rect(surface, GRID_COLOR, r, 1)


def draw_hud(surface, score, level, foods_eaten):
    """Render score, level, and next-level progress in the HUD strip."""
    # Score
    score_surf = font_large.render(f"Score: {score}", True, YELLOW)
    surface.blit(score_surf, (12, 12))

    # Level
    level_surf = font_medium.render(f"Level {level}", True, WHITE)
    surface.blit(level_surf, (SCREEN_W - 110, 10))

    # Progress bar toward next level
    progress = (foods_eaten % FOODS_PER_LEVEL) / FOODS_PER_LEVEL
    bar_x, bar_y = SCREEN_W - 110, 34
    bar_w, bar_h = 90, 10
    pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, SNAKE_HEAD,
                     (bar_x, bar_y, int(bar_w * progress), bar_h), border_radius=4)
    next_surf = font_small.render("next lvl", True, GRAY)
    surface.blit(next_surf, (bar_x, bar_y + 12))


def show_screen(surface, title, sub="Press SPACE to play"):
    """Show a full-screen overlay with title and subtitle."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    t1 = font_large.render(title, True, YELLOW)
    t2 = font_medium.render(sub,  True, WHITE)
    surface.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 40))
    surface.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 + 10))
    pygame.display.flip()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    # ── Start screen ──
    draw_grid(screen)
    show_screen(screen, "SNAKE", "Arrow keys to move | SPACE to start")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    # ── Initialise game state ──
    snake       = Snake()
    score       = 0
    foods_eaten = 0    # total foods consumed (used for levelling)
    level       = 1
    fps         = BASE_FPS

    # Spawn the first food
    food_list = [Food(snake.body_set())]

    # Timer to spawn additional food occasionally
    food_spawn_timer    = 0
    FOOD_SPAWN_INTERVAL = 180   # frames between extra food spawns

    running = True

    while running:
        clock.tick(fps)   # game speed controlled by fps variable

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    snake.set_direction(UP)
                if event.key == pygame.K_DOWN:  snake.set_direction(DOWN)
                if event.key == pygame.K_LEFT:  snake.set_direction(LEFT)
                if event.key == pygame.K_RIGHT: snake.set_direction(RIGHT)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Move snake ──
        snake.move()

        # ── Border collision  (Practice 10 task 1) ──
        head_col, head_row = snake.head()
        if is_wall(head_col, head_row):
            running = False    # hit a wall
            break

        # ── Self collision ──
        if snake.self_collision():
            running = False
            break

        # ── Update food timers; remove expired food ──
        for f in food_list:
            f.update()
        food_list = [f for f in food_list if not f.expired()]

        # ── Food consumption ──
        occupied = snake.body_set() | {f.pos() for f in food_list}
        for food in list(food_list):
            if snake.head() == food.pos():
                score       += food.points
                foods_eaten += 1
                snake.grow()
                food_list.remove(food)

                # Ensure at least one food is on the board
                if not food_list:
                    food_list.append(Food(occupied))

        # ── Periodically spawn additional food ──
        food_spawn_timer += 1
        if food_spawn_timer >= FOOD_SPAWN_INTERVAL and len(food_list) < 3:
            food_spawn_timer = 0
            occupied = snake.body_set() | {f.pos() for f in food_list}
            food_list.append(Food(occupied))

        # ── Level progression  (Practice 10 tasks 3 & 4) ──
        new_level = foods_eaten // FOODS_PER_LEVEL + 1
        if new_level > level:
            level = new_level
            fps   = min(BASE_FPS + (level - 1) * FPS_INCREMENT, MAX_FPS)

        # ── Draw ──
        draw_grid(screen)
        for f in food_list:
            f.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, foods_eaten)
        pygame.display.flip()

    # ── Game Over ──
    draw_grid(screen)
    snake.draw(screen)
    show_screen(screen, "GAME OVER",
                f"Score: {score}  Level: {level}  |  SPACE to retry")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()