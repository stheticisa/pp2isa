"""
Paint Application - Practice 10 & 11
=======================================
Extended from https://nerdparadise.com/programming/pygame/part6

Practice 10 features:
  - Draw rectangle
  - Draw circle
  - Eraser
  - Color selection palette

Practice 11 features:
  - Draw square
  - Draw right triangle
  - Draw equilateral triangle
  - Draw rhombus

Controls:
  - Click a tool button to select it
  - Click a colour swatch to pick a colour
  - Click a pen-size button to change line width
  - Drag on canvas to draw shapes / freehand
  - Press C or click Clear to wipe the canvas
  - Press Escape to quit
"""

import pygame
import math
import sys

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# Window dimensions
CANVAS_W  = 900
CANVAS_H  = 620
TOOLBAR_H = 70           # top toolbar strip height

SCREEN_W  = CANVAS_W
SCREEN_H  = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")

# Clock - controls the frame rate
clock = pygame.time.Clock()

# Colour constants
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
TOOLBAR_BG   = (35,  35,  45)
CANVAS_BG    = (255, 255, 255)
HIGHLIGHT    = (100, 180, 255)
BUTTON_HOVER = (55,  55,  70)
TEXT_COLOR   = (210, 210, 210)
BORDER_DIM   = (80,  80, 100)

# Colour palette shown in the toolbar
PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (220,  50,  50),  # red
    (50,  200,  50),  # green
    (50,  100, 220),  # blue
    (255, 220,   0),  # yellow
    (255, 140,   0),  # orange
    (180,   0, 180),  # purple
    (0,   180, 180),  # cyan
    (180, 100,  50),  # brown
    (255, 182, 193),  # pink
    (100, 100, 100),  # gray
]

# Tool list - ASCII names only to avoid Unicode encoding issues on Windows
TOOLS = [
    "Pencil",
    "Rect",       # rectangle
    "Square",
    "Circle",
    "R-Tri",      # right triangle
    "Eq-Tri",     # equilateral triangle
    "Rhombus",
    "Eraser",
]

# Fonts
font    = pygame.font.SysFont("monospace", 13, bold=True)
font_sm = pygame.font.SysFont("monospace", 11)


# ─────────────────────────────────────────────
# SHAPE DRAWING HELPERS
# Each accepts: surface, color, line-width lw, start (x0,y0), end (x1,y1)
# ─────────────────────────────────────────────

def draw_rect(surface, color, lw, x0, y0, x1, y1):
    """Draw an axis-aligned rectangle from two corner points."""
    rx = min(x0, x1)
    ry = min(y0, y1)
    rw = abs(x1 - x0)
    rh = abs(y1 - y0)
    if rw > 0 and rh > 0:
        pygame.draw.rect(surface, color, (rx, ry, rw, rh), lw)


def draw_square(surface, color, lw, x0, y0, x1, y1):
    """
    Draw a square anchored at (x0, y0).
    Side = min(|dx|, |dy|) so the shape stays square while dragging.
    """
    side = min(abs(x1 - x0), abs(y1 - y0))
    sx   = x0 if x1 >= x0 else x0 - side
    sy   = y0 if y1 >= y0 else y0 - side
    if side > 0:
        pygame.draw.rect(surface, color, (sx, sy, side, side), lw)


def draw_circle(surface, color, lw, x0, y0, x1, y1):
    """
    Draw a circle centred at (x0, y0).
    Radius = distance from drag-start to current cursor.
    """
    radius = int(math.hypot(x1 - x0, y1 - y0))
    if radius > 0:
        pygame.draw.circle(surface, color, (x0, y0), radius, lw)


def draw_right_triangle(surface, color, lw, x0, y0, x1, y1):
    """
    Right triangle with the right angle at (x0, y0).
    Vertices: (x0,y0) -- (x1,y0) -- (x0,y1)
    """
    if abs(x1 - x0) > 1 and abs(y1 - y0) > 1:
        pts = [(x0, y0), (x1, y0), (x0, y1)]
        pygame.draw.polygon(surface, color, pts, lw)


def draw_equilateral_triangle(surface, color, lw, x0, y0, x1, y1):
    """
    Equilateral triangle with base from (x0,y0) to (x1,y0).
    Apex is above the base when dragging upward, below when downward.
    """
    base   = x1 - x0
    height = abs(base) * math.sqrt(3) / 2
    sign   = -1 if y1 <= y0 else 1      # direction of apex
    apex   = (int(x0 + base / 2), int(y0 + sign * height))
    if abs(base) > 2:
        pts = [(x0, y0), (x1, y0), apex]
        pygame.draw.polygon(surface, color, pts, lw)


def draw_rhombus(surface, color, lw, x0, y0, x1, y1):
    """
    Rhombus centred at (x0, y0).
    Half-diagonals: dx = |x1-x0|, dy = |y1-y0|.
    """
    dx = x1 - x0
    dy = y1 - y0
    if abs(dx) > 1 and abs(dy) > 1:
        pts = [
            (x0,      y0 - dy),   # top
            (x0 + dx, y0     ),   # right
            (x0,      y0 + dy),   # bottom
            (x0 - dx, y0     ),   # left
        ]
        pygame.draw.polygon(surface, color, pts, lw)


# Map tool name to its drawing function
SHAPE_DRAWERS = {
    "Rect":    draw_rect,
    "Square":  draw_square,
    "Circle":  draw_circle,
    "R-Tri":   draw_right_triangle,
    "Eq-Tri":  draw_equilateral_triangle,
    "Rhombus": draw_rhombus,
}

# Tools that require a drag gesture (start to end point)
DRAG_TOOLS = set(SHAPE_DRAWERS.keys())


# ─────────────────────────────────────────────
# TOOLBAR LAYOUT  (geometry calculated once at module level)
# ─────────────────────────────────────────────
TOOL_BTN_W   = 66
TOOL_BTN_H   = 40
TOOL_BTN_Y   = (TOOLBAR_H - TOOL_BTN_H) // 2
TOOL_START_X = 6

SWATCH_SIZE  = 22
SWATCH_GAP   = 3
PALETTE_X    = TOOL_START_X + len(TOOLS) * (TOOL_BTN_W + 4) + 10
PALETTE_Y    = (TOOLBAR_H - SWATCH_SIZE) // 2

LW_OPTIONS   = [1, 2, 4, 8]
LW_BTN_SIZE  = 20
LW_BTN_GAP   = 4
LW_START_X   = PALETTE_X + len(PALETTE) * (SWATCH_SIZE + SWATCH_GAP) + 14
LW_START_Y   = (TOOLBAR_H - LW_BTN_SIZE) // 2

CLEAR_X = LW_START_X + len(LW_OPTIONS) * (LW_BTN_SIZE + LW_BTN_GAP) + 14
CLEAR_Y = LW_START_Y
CLEAR_W = 50
CLEAR_H = LW_BTN_SIZE


def get_tool_rect(i):
    """Pixel Rect for the i-th tool button."""
    x = TOOL_START_X + i * (TOOL_BTN_W + 4)
    return pygame.Rect(x, TOOL_BTN_Y, TOOL_BTN_W, TOOL_BTN_H)


def get_swatch_rect(i):
    """Pixel Rect for the i-th colour swatch."""
    x = PALETTE_X + i * (SWATCH_SIZE + SWATCH_GAP)
    return pygame.Rect(x, PALETTE_Y, SWATCH_SIZE, SWATCH_SIZE)


def get_lw_rect(i):
    """Pixel Rect for the i-th line-width button."""
    x = LW_START_X + i * (LW_BTN_SIZE + LW_BTN_GAP)
    return pygame.Rect(x, LW_START_Y, LW_BTN_SIZE, LW_BTN_SIZE)


def get_clear_rect():
    """Pixel Rect for the Clear button."""
    return pygame.Rect(CLEAR_X, CLEAR_Y, CLEAR_W, CLEAR_H)


# ─────────────────────────────────────────────
# TOOLBAR RENDERING
# ─────────────────────────────────────────────

def draw_toolbar(surface, current_tool, current_color, current_lw, mouse_pos):
    """Render the full toolbar strip at the top of the window."""

    # Background bar
    pygame.draw.rect(surface, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))
    pygame.draw.line(surface, BORDER_DIM,
                     (0, TOOLBAR_H - 1), (SCREEN_W, TOOLBAR_H - 1), 1)

    # Tool buttons
    for i, name in enumerate(TOOLS):
        rect    = get_tool_rect(i)
        hovered = rect.collidepoint(mouse_pos)
        active  = (name == current_tool)
        bg      = HIGHLIGHT if active else (BUTTON_HOVER if hovered else TOOLBAR_BG)
        pygame.draw.rect(surface, bg, rect, border_radius=5)
        pygame.draw.rect(surface, BORDER_DIM, rect, 1, border_radius=5)
        label = font.render(name, True, WHITE if active else TEXT_COLOR)
        surface.blit(label, (rect.centerx - label.get_width() // 2,
                              rect.centery - label.get_height() // 2))

    # Colour swatches
    for i, col in enumerate(PALETTE):
        rect     = get_swatch_rect(i)
        hovered  = rect.collidepoint(mouse_pos)
        selected = (col == current_color)
        pygame.draw.rect(surface, col, rect, border_radius=3)
        bdr_color = HIGHLIGHT if selected else ((200, 200, 200) if hovered else (80, 80, 80))
        bdr_width = 3 if selected else (2 if hovered else 1)
        pygame.draw.rect(surface, bdr_color, rect, bdr_width, border_radius=3)

    # Line-width buttons
    lw_label = font_sm.render("Pen:", True, TEXT_COLOR)
    surface.blit(lw_label, (LW_START_X - 30, LW_START_Y + 4))
    for i, lw in enumerate(LW_OPTIONS):
        rect    = get_lw_rect(i)
        hovered = rect.collidepoint(mouse_pos)
        active  = (lw == current_lw)
        bg      = HIGHLIGHT if active else (BUTTON_HOVER if hovered else TOOLBAR_BG)
        pygame.draw.rect(surface, bg, rect, border_radius=3)
        pygame.draw.rect(surface, BORDER_DIM, rect, 1, border_radius=3)
        mid_y = rect.centery
        pygame.draw.line(surface, TEXT_COLOR,
                         (rect.x + 3, mid_y), (rect.right - 3, mid_y),
                         min(lw, rect.height - 4))

    # Clear button
    clr_rect = get_clear_rect()
    hovered  = clr_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 50, 50) if hovered else (120, 40, 40),
                     clr_rect, border_radius=5)
    clr_surf = font.render("Clear", True, WHITE)
    surface.blit(clr_surf, (clr_rect.centerx - clr_surf.get_width() // 2,
                             clr_rect.centery - clr_surf.get_height() // 2))


# ─────────────────────────────────────────────
# COORDINATE HELPERS
# ─────────────────────────────────────────────

def to_canvas(screen_x, screen_y):
    """Convert a screen position to canvas-local coordinates."""
    return screen_x, screen_y - TOOLBAR_H


def in_canvas(screen_x, screen_y):
    """Return True if the screen position is inside the canvas area."""
    return screen_y >= TOOLBAR_H


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def main():
    # Persistent surface - everything drawn here is kept between frames
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    # Application state
    current_tool  = "Pencil"
    current_color = BLACK
    current_lw    = 2
    eraser_radius = 18      # radius of the eraser brush in pixels

    drawing    = False      # True while left mouse button is held
    last_pos   = None       # previous mouse canvas-pos (for pencil/eraser trails)
    drag_start = None       # canvas-coord anchor for shape drag tools

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_c:
                    canvas.fill(CANVAS_BG)   # C key clears canvas

            # Left mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my      = event.pos
                toolbar_hit = False

                # Check tool buttons
                for i, name in enumerate(TOOLS):
                    if get_tool_rect(i).collidepoint(mx, my):
                        current_tool = name
                        toolbar_hit  = True
                        break

                # Check colour swatches
                if not toolbar_hit:
                    for i, col in enumerate(PALETTE):
                        if get_swatch_rect(i).collidepoint(mx, my):
                            current_color = col
                            toolbar_hit   = True
                            break

                # Check line-width buttons
                if not toolbar_hit:
                    for i, lw in enumerate(LW_OPTIONS):
                        if get_lw_rect(i).collidepoint(mx, my):
                            current_lw  = lw
                            toolbar_hit = True
                            break

                # Check Clear button
                if not toolbar_hit and get_clear_rect().collidepoint(mx, my):
                    canvas.fill(CANVAS_BG)
                    toolbar_hit = True

                # Begin drawing on canvas
                if not toolbar_hit and in_canvas(mx, my):
                    drawing    = True
                    cx, cy     = to_canvas(mx, my)
                    last_pos   = (cx, cy)
                    drag_start = (cx, cy)

                    # Pencil: stamp a dot on initial click
                    if current_tool == "Pencil":
                        r = max(1, current_lw // 2)
                        pygame.draw.circle(canvas, current_color, (cx, cy), r)

                    # Eraser: erase on initial click too
                    elif current_tool == "Eraser":
                        pygame.draw.circle(canvas, CANVAS_BG, (cx, cy), eraser_radius)

            # Left mouse button released - commit the shape to canvas
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and drag_start is not None:
                    mx, my = event.pos
                    cx, cy = to_canvas(mx, my)
                    x0, y0 = drag_start

                    # Paint the finished shape onto the persistent canvas
                    if current_tool in DRAG_TOOLS:
                        SHAPE_DRAWERS[current_tool](
                            canvas, current_color, current_lw,
                            x0, y0, cx, cy)

                drawing    = False
                last_pos   = None
                drag_start = None

            # Mouse moved while button held
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                cx, cy = to_canvas(mx, my)

                if in_canvas(mx, my):
                    if current_tool == "Pencil" and last_pos:
                        # Connect previous and current position
                        pygame.draw.line(canvas, current_color,
                                         last_pos, (cx, cy), current_lw)
                        last_pos = (cx, cy)

                    elif current_tool == "Eraser" and last_pos:
                        # Erase a filled circle under the cursor
                        pygame.draw.circle(canvas, CANVAS_BG,
                                           (cx, cy), eraser_radius)
                        last_pos = (cx, cy)

                    else:
                        # Shape tool - just track position for preview
                        last_pos = (cx, cy)

        # Render frame
        screen.fill(CANVAS_BG)
        screen.blit(canvas, (0, TOOLBAR_H))

        # Live translucent shape preview while dragging
        if drawing and drag_start is not None and current_tool in DRAG_TOOLS:
            mx, my = mouse_pos
            cx, cy = to_canvas(mx, my)
            x0, y0 = drag_start

            # Use a per-pixel-alpha surface so the preview is semi-transparent
            preview  = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
            pr_color = (current_color[0], current_color[1], current_color[2], 140)
            SHAPE_DRAWERS[current_tool](preview, pr_color, current_lw, x0, y0, cx, cy)
            screen.blit(preview, (0, TOOLBAR_H))

        # Eraser cursor outline
        if current_tool == "Eraser":
            mx, my = mouse_pos
            if in_canvas(mx, my):
                pygame.draw.circle(screen, (200, 0, 0), (mx, my), eraser_radius, 2)

        # Draw toolbar on top
        draw_toolbar(screen, current_tool, current_color, current_lw, mouse_pos)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()