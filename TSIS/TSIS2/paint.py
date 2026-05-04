"""
paint.py  —  TSIS 2: Extended Paint Application
================================================
Extends Practice 10 & 11 Paint with:
  3.1  Pencil (freehand) + Straight line tool with live preview
  3.2  Three brush sizes (2/5/10 px) via buttons or keys 1/2/3
  3.3  Flood-fill tool (BFS pixel-based)
  3.4  Ctrl+S  saves canvas as timestamped PNG
  3.5  Text tool: click → type → Enter to commit / Escape to cancel
  All existing shapes from Practice 10–11 respect active brush size.
"""

import sys
import math
import pygame
from datetime import datetime
from tools import (
    SHAPE_DRAWERS, DRAG_TOOLS, FREEHAND_TOOLS,
    flood_fill, TextTool,
    draw_pencil_segment,
)

# ─────────────────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────────────────
pygame.init()

CANVAS_W  = 960
CANVAS_H  = 640
TOOLBAR_H = 72

SCREEN_W = CANVAS_W
SCREEN_H = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint — TSIS 2")

clock = pygame.time.Clock()

# ── Colours ──
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
CANVAS_BG    = (255, 255, 255)
TOOLBAR_BG   = (30,  30,  42)
HIGHLIGHT    = (90,  170, 255)
BUTTON_HOVER = (50,  50,  65)
TEXT_COLOR   = (210, 210, 210)
BORDER_DIM   = (75,  75,  95)

# ── Palette ──
PALETTE = [
    (0,   0,   0), (255,255,255), (220,50,50),  (50,200,50),
    (50,100,220),  (255,220,0),   (255,140,0),   (180,0,180),
    (0,180,180),   (180,100,50),  (255,182,193), (100,100,100),
]

# ── Tools ──
TOOLS = ["Pencil","Line","Rect","Square","Circle","R-Tri","Eq-Tri","Rhombus","Fill","Text","Eraser"]

# ── Brush sizes ──
BRUSH_SIZES   = [2, 5, 10]
BRUSH_LABELS  = ["S", "M", "L"]
BRUSH_KEYS    = [pygame.K_1, pygame.K_2, pygame.K_3]

# ── Fonts ──
font    = pygame.font.SysFont("monospace", 13, bold=True)
font_sm = pygame.font.SysFont("monospace", 11)
font_text = pygame.font.SysFont("arial", 20)   # used by text tool

# ── Text tool instance ──
text_tool = TextTool(font_text)

# ─────────────────────────────────────────────────────────────────────────────
# TOOLBAR GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────
TOOL_BTN_W   = 62
TOOL_BTN_H   = 38
TOOL_BTN_Y   = (TOOLBAR_H - TOOL_BTN_H) // 2
TOOL_START_X = 4

SWATCH_SIZE  = 21
SWATCH_GAP   = 3
PALETTE_X    = TOOL_START_X + len(TOOLS) * (TOOL_BTN_W + 3) + 8
PALETTE_Y    = (TOOLBAR_H - SWATCH_SIZE) // 2

BRUSH_BTN_SIZE = 22
BRUSH_BTN_GAP  = 4
BRUSH_X        = PALETTE_X + len(PALETTE) * (SWATCH_SIZE + SWATCH_GAP) + 12
BRUSH_Y        = (TOOLBAR_H - BRUSH_BTN_SIZE) // 2

ACTION_X = BRUSH_X + len(BRUSH_SIZES) * (BRUSH_BTN_SIZE + BRUSH_BTN_GAP) + 12
ACTION_Y = BRUSH_Y
ACTION_H = BRUSH_BTN_SIZE
ACTION_W = 48


def get_tool_rect(i):
    return pygame.Rect(TOOL_START_X + i * (TOOL_BTN_W + 3), TOOL_BTN_Y, TOOL_BTN_W, TOOL_BTN_H)

def get_swatch_rect(i):
    return pygame.Rect(PALETTE_X + i * (SWATCH_SIZE + SWATCH_GAP), PALETTE_Y, SWATCH_SIZE, SWATCH_SIZE)

def get_brush_rect(i):
    return pygame.Rect(BRUSH_X + i * (BRUSH_BTN_SIZE + BRUSH_BTN_GAP), BRUSH_Y, BRUSH_BTN_SIZE, BRUSH_BTN_SIZE)

def get_clear_rect():
    return pygame.Rect(ACTION_X, ACTION_Y, ACTION_W, ACTION_H)

def get_quit_rect():
    return pygame.Rect(ACTION_X + ACTION_W + 6, ACTION_Y, ACTION_W, ACTION_H)


# ─────────────────────────────────────────────────────────────────────────────
# TOOLBAR RENDERING
# ─────────────────────────────────────────────────────────────────────────────

def draw_toolbar(surface, cur_tool, cur_color, cur_brush_idx, mouse_pos):
    pygame.draw.rect(surface, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))
    pygame.draw.line(surface, BORDER_DIM, (0, TOOLBAR_H-1), (SCREEN_W, TOOLBAR_H-1), 1)

    # Tool buttons
    for i, name in enumerate(TOOLS):
        r       = get_tool_rect(i)
        hovered = r.collidepoint(mouse_pos)
        active  = (name == cur_tool)
        bg      = HIGHLIGHT if active else (BUTTON_HOVER if hovered else TOOLBAR_BG)
        pygame.draw.rect(surface, bg, r, border_radius=5)
        pygame.draw.rect(surface, BORDER_DIM, r, 1, border_radius=5)
        lbl = font.render(name, True, WHITE if active else TEXT_COLOR)
        surface.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

    # Colour swatches
    for i, col in enumerate(PALETTE):
        r       = get_swatch_rect(i)
        hovered = r.collidepoint(mouse_pos)
        sel     = (col == cur_color)
        pygame.draw.rect(surface, col, r, border_radius=3)
        bc = HIGHLIGHT if sel else ((200,200,200) if hovered else (70,70,70))
        pygame.draw.rect(surface, bc, r, 3 if sel else (2 if hovered else 1), border_radius=3)

    # Brush size buttons
    brush_lbl = font_sm.render("Size:", True, TEXT_COLOR)
    surface.blit(brush_lbl, (BRUSH_X - 34, BRUSH_Y + 5))
    for i, (sz, lbl) in enumerate(zip(BRUSH_SIZES, BRUSH_LABELS)):
        r       = get_brush_rect(i)
        hovered = r.collidepoint(mouse_pos)
        active  = (i == cur_brush_idx)
        bg      = HIGHLIGHT if active else (BUTTON_HOVER if hovered else TOOLBAR_BG)
        pygame.draw.rect(surface, bg, r, border_radius=3)
        pygame.draw.rect(surface, BORDER_DIM, r, 1, border_radius=3)
        s = font.render(lbl, True, WHITE if active else TEXT_COLOR)
        surface.blit(s, (r.centerx - s.get_width()//2, r.centery - s.get_height()//2))

    # Clear button
    cr = get_clear_rect()
    h  = cr.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (170,45,45) if h else (110,35,35), cr, border_radius=5)
    cs = font.render("Clear", True, WHITE)
    surface.blit(cs, (cr.centerx - cs.get_width()//2, cr.centery - cs.get_height()//2))

    # Quit button
    qr = get_quit_rect()
    h  = qr.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (200,28,28) if h else (140,18,18), qr, border_radius=5)
    pygame.draw.rect(surface, (220,80,80), qr, 1, border_radius=5)
    qs = font.render("Quit", True, WHITE)
    surface.blit(qs, (qr.centerx - qs.get_width()//2, qr.centery - qs.get_height()//2))


# ─────────────────────────────────────────────────────────────────────────────
# COORDINATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def to_canvas(sx, sy):
    return sx, sy - TOOLBAR_H

def in_canvas(sx, sy):
    return sy >= TOOLBAR_H


# ─────────────────────────────────────────────────────────────────────────────
# SAVE CANVAS
# ─────────────────────────────────────────────────────────────────────────────

def save_canvas(canvas):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    print(f"Canvas saved → {filename}")
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(CANVAS_BG)

    cur_tool      = "Pencil"
    cur_color     = BLACK
    cur_brush_idx = 0        # index into BRUSH_SIZES

    drawing    = False
    last_pos   = None
    drag_start = None

    # Save notification
    save_msg      = ""
    save_msg_time = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        lw        = BRUSH_SIZES[cur_brush_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ──
            if event.type == pygame.KEYDOWN:
                # Text tool intercepts keys when active
                if text_tool.active:
                    result = text_tool.handle_key(event)
                    if result == "commit":
                        text_tool.commit_to_canvas(canvas)
                    continue  # swallow all keys while typing

                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # Brush size shortcuts  1 / 2 / 3
                for i, k in enumerate(BRUSH_KEYS):
                    if event.key == k:
                        cur_brush_idx = i

                # Ctrl+S — save
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    fn            = save_canvas(canvas)
                    save_msg      = f"Saved: {fn}"
                    save_msg_time = pygame.time.get_ticks()

                # C — clear
                if event.key == pygame.K_c:
                    canvas.fill(CANVAS_BG)

            # ── Mouse button down ──
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my      = event.pos
                toolbar_hit = False

                # Tool buttons
                for i, name in enumerate(TOOLS):
                    if get_tool_rect(i).collidepoint(mx, my):
                        cur_tool    = name
                        toolbar_hit = True
                        # Cancel text if switching away
                        if name != "Text":
                            text_tool.active = False
                        break

                # Colour swatches
                if not toolbar_hit:
                    for i, col in enumerate(PALETTE):
                        if get_swatch_rect(i).collidepoint(mx, my):
                            cur_color   = col
                            toolbar_hit = True
                            break

                # Brush size buttons
                if not toolbar_hit:
                    for i in range(len(BRUSH_SIZES)):
                        if get_brush_rect(i).collidepoint(mx, my):
                            cur_brush_idx = i
                            toolbar_hit   = True
                            break

                # Clear / Quit
                if not toolbar_hit and get_clear_rect().collidepoint(mx, my):
                    canvas.fill(CANVAS_BG)
                    toolbar_hit = True
                if not toolbar_hit and get_quit_rect().collidepoint(mx, my):
                    pygame.quit(); sys.exit()

                # Canvas interaction
                if not toolbar_hit and in_canvas(mx, my):
                    cx, cy = to_canvas(mx, my)

                    if cur_tool == "Fill":
                        # Flood-fill on click
                        flood_fill(canvas, cx, cy, cur_color)

                    elif cur_tool == "Text":
                        # Start text entry at click position
                        text_tool.start(cx, cy, cur_color)

                    else:
                        drawing    = True
                        last_pos   = (cx, cy)
                        drag_start = (cx, cy)

                        if cur_tool == "Pencil":
                            pygame.draw.circle(canvas, cur_color,
                                               (cx, cy), max(1, lw // 2))
                        elif cur_tool == "Eraser":
                            pygame.draw.circle(canvas, CANVAS_BG, (cx, cy), lw * 3)

            # ── Mouse button up — commit drag shape ──
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and drag_start and cur_tool in DRAG_TOOLS:
                    mx, my = event.pos
                    cx, cy = to_canvas(mx, my)
                    x0, y0 = drag_start
                    SHAPE_DRAWERS[cur_tool](canvas, cur_color, lw, x0, y0, cx, cy)
                drawing    = False
                last_pos   = None
                drag_start = None

            # ── Mouse motion ──
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                cx, cy = to_canvas(mx, my)
                if in_canvas(mx, my):
                    if cur_tool == "Pencil" and last_pos:
                        draw_pencil_segment(canvas, cur_color, lw,
                                            last_pos[0], last_pos[1], cx, cy)
                        last_pos = (cx, cy)
                    elif cur_tool == "Eraser" and last_pos:
                        pygame.draw.circle(canvas, CANVAS_BG, (cx, cy), lw * 3)
                        last_pos = (cx, cy)
                    else:
                        last_pos = (cx, cy)

        # ── Render ──
        screen.fill(CANVAS_BG)
        screen.blit(canvas, (0, TOOLBAR_H))

        # Live preview for drag tools (semi-transparent)
        if drawing and drag_start and cur_tool in DRAG_TOOLS:
            mx, my = mouse_pos
            cx, cy = to_canvas(mx, my)
            x0, y0 = drag_start
            preview = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
            pc      = (*cur_color[:3], 140)
            SHAPE_DRAWERS[cur_tool](preview, pc, lw, x0, y0, cx, cy)
            screen.blit(preview, (0, TOOLBAR_H))

        # Text tool preview
        text_tool.render_preview(screen, TOOLBAR_H)

        # Eraser cursor circle
        if cur_tool == "Eraser":
            mx, my = mouse_pos
            if in_canvas(mx, my):
                pygame.draw.circle(screen, (200, 0, 0), (mx, my), lw * 3, 2)

        draw_toolbar(screen, cur_tool, cur_color, cur_brush_idx, mouse_pos)

        # Save notification
        if save_msg and pygame.time.get_ticks() - save_msg_time < 2500:
            notif = font.render(save_msg, True, (80, 220, 80))
            screen.blit(notif, (SCREEN_W - notif.get_width() - 10,
                                TOOLBAR_H + 6))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()