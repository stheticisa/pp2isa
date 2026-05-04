"""
tools.py — Drawing tool implementations for TSIS 2 Paint
=========================================================
Contains:
  - All shape drawers (from Practice 10 & 11, now brush-size aware)
  - Straight line tool with live preview
  - Flood-fill  (BFS pixel-based)
  - Text tool state machine
"""

import pygame
import math
from collections import deque


# ─────────────────────────────────────────────────────────────────────────────
# SHAPE DRAWERS
# All accept: (surface, color, lw, x0, y0, x1, y1)
# ─────────────────────────────────────────────────────────────────────────────

def draw_pencil_segment(surface, color, lw, x0, y0, x1, y1):
    """Draw a freehand segment between two points."""
    pygame.draw.line(surface, color, (x0, y0), (x1, y1), lw)
    # Round cap so strokes look smooth
    pygame.draw.circle(surface, color, (x1, y1), max(1, lw // 2))


def draw_line(surface, color, lw, x0, y0, x1, y1):
    """Straight line from (x0,y0) to (x1,y1)."""
    if (x0, y0) != (x1, y1):
        pygame.draw.line(surface, color, (x0, y0), (x1, y1), lw)


def draw_rect(surface, color, lw, x0, y0, x1, y1):
    """Axis-aligned rectangle."""
    rx, ry = min(x0, x1), min(y0, y1)
    rw, rh = abs(x1 - x0), abs(y1 - y0)
    if rw > 0 and rh > 0:
        pygame.draw.rect(surface, color, (rx, ry, rw, rh), lw)


def draw_square(surface, color, lw, x0, y0, x1, y1):
    """Square with equal sides (shorter dimension wins)."""
    side = min(abs(x1 - x0), abs(y1 - y0))
    sx   = x0 if x1 >= x0 else x0 - side
    sy   = y0 if y1 >= y0 else y0 - side
    if side > 0:
        pygame.draw.rect(surface, color, (sx, sy, side, side), lw)


def draw_circle(surface, color, lw, x0, y0, x1, y1):
    """Circle centred at start; radius = distance to cursor."""
    radius = int(math.hypot(x1 - x0, y1 - y0))
    if radius > 0:
        pygame.draw.circle(surface, color, (x0, y0), radius, lw)


def draw_right_triangle(surface, color, lw, x0, y0, x1, y1):
    """Right angle at (x0,y0); vertices (x0,y0),(x1,y0),(x0,y1)."""
    if abs(x1 - x0) > 1 and abs(y1 - y0) > 1:
        pygame.draw.polygon(surface, color, [(x0, y0), (x1, y0), (x0, y1)], lw)


def draw_equilateral_triangle(surface, color, lw, x0, y0, x1, y1):
    """Base from (x0,y0) to (x1,y0); apex above or below."""
    base   = x1 - x0
    height = abs(base) * math.sqrt(3) / 2
    sign   = -1 if y1 <= y0 else 1
    apex   = (int(x0 + base / 2), int(y0 + sign * height))
    if abs(base) > 2:
        pygame.draw.polygon(surface, color, [(x0, y0), (x1, y0), apex], lw)


def draw_rhombus(surface, color, lw, x0, y0, x1, y1):
    """Rhombus centred at (x0,y0); half-diagonals = |dx|, |dy|."""
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) > 1 and abs(dy) > 1:
        pts = [(x0, y0 - dy), (x0 + dx, y0), (x0, y0 + dy), (x0 - dx, y0)]
        pygame.draw.polygon(surface, color, pts, lw)


# Map tool name → draw function
SHAPE_DRAWERS = {
    "Pencil":  draw_pencil_segment,
    "Line":    draw_line,
    "Rect":    draw_rect,
    "Square":  draw_square,
    "Circle":  draw_circle,
    "R-Tri":   draw_right_triangle,
    "Eq-Tri":  draw_equilateral_triangle,
    "Rhombus": draw_rhombus,
}

# Tools that use drag (start → end) for final commit
DRAG_TOOLS = {"Line", "Rect", "Square", "Circle", "R-Tri", "Eq-Tri", "Rhombus"}
# Tools that draw continuously as the mouse moves
FREEHAND_TOOLS = {"Pencil", "Eraser"}


# ─────────────────────────────────────────────────────────────────────────────
# FLOOD FILL  (BFS, pixel-exact)
# ─────────────────────────────────────────────────────────────────────────────

def flood_fill(surface, x, y, fill_color):
    """
    BFS flood-fill starting at (x, y) on `surface`.
    Replaces all connected pixels of the target colour with `fill_color`.
    """
    if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
        return

    target_color = surface.get_at((x, y))[:3]   # ignore alpha
    fill_rgb     = fill_color[:3]

    if target_color == fill_rgb:
        return   # already the right colour — nothing to do

    visited = set()
    queue   = deque([(x, y)])
    w, h    = surface.get_width(), surface.get_height()

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        surface.set_at((cx, cy), fill_rgb)
        visited.add((cx, cy))

        queue.extend([(cx + 1, cy), (cx - 1, cy),
                      (cx, cy + 1), (cx, cy - 1)])


# ─────────────────────────────────────────────────────────────────────────────
# TEXT TOOL STATE
# ─────────────────────────────────────────────────────────────────────────────

class TextTool:
    """
    Manages the text-placement state machine:
      idle  →  (click on canvas)  →  typing  →  Enter = commit / Escape = cancel
    """

    def __init__(self, font):
        self.font     = font
        self.active   = False
        self.text     = ""
        self.position = (0, 0)   # canvas coordinates of the text cursor
        self.color    = (0, 0, 0)

    def start(self, cx, cy, color):
        """Begin text entry at canvas position (cx, cy)."""
        self.active   = True
        self.text     = ""
        self.position = (cx, cy)
        self.color    = color

    def handle_key(self, event):
        """
        Process a KEYDOWN event.
        Returns:
          'commit'  — Enter pressed, caller should blit text onto canvas
          'cancel'  — Escape pressed
          None      — normal character typed
        """
        if not self.active:
            return None
        if event.key == pygame.K_RETURN:
            self.active = False
            return "commit"
        if event.key == pygame.K_ESCAPE:
            self.active = False
            self.text   = ""
            return "cancel"
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            char = event.unicode
            if char and char.isprintable():
                self.text += char
        return None

    def render_preview(self, surface, canvas_offset_y):
        """Draw the live text preview on screen (not yet committed to canvas)."""
        if not self.active:
            return
        cx, cy = self.position
        sy     = cy + canvas_offset_y

        # Blinking cursor
        ticks       = pygame.time.get_ticks()
        show_cursor = (ticks // 500) % 2 == 0
        display     = self.text + ("|" if show_cursor else " ")

        surf = self.font.render(display, True, self.color)
        surface.blit(surf, (cx, sy))

    def commit_to_canvas(self, canvas):
        """Blit the typed text permanently onto the canvas surface."""
        if not self.text:
            return
        cx, cy = self.position
        surf   = self.font.render(self.text, True, self.color)
        canvas.blit(surf, (cx, cy))
        self.text = ""