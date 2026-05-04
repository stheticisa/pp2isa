"""
ui.py — Screen drawing helpers for TSIS 3 Racer
"""

import pygame

# ── Colours ──
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
YELLOW  = (255, 220,   0)
GRAY    = (160, 160, 160)
DARK    = (20,  22,  35)
PANEL   = (35,  38,  55)
GREEN   = (60,  200,  80)
RED     = (220,  50,  50)
BLUE    = (80,  140, 240)
ORANGE  = (255, 140,   0)


class Button:
    """A simple clickable button drawn with pygame primitives."""

    def __init__(self, rect, label, color=PANEL, text_color=WHITE):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.color      = color
        self.text_color = text_color
        self._font      = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("monospace", 20, bold=True)
        return self._font

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        bg      = tuple(min(255, c + 30) for c in self.color) if hovered else self.color
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, GRAY, self.rect, 2, border_radius=8)
        lbl = self._get_font().render(self.label, True, self.text_color)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                            self.rect.centery - lbl.get_height() // 2))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


def draw_title(surface, text, y, color=YELLOW, size=48):
    font = pygame.font.SysFont("monospace", size, bold=True)
    surf = font.render(text, True, color)
    surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, y))


def draw_text(surface, text, x, y, color=WHITE, size=20, bold=False):
    font = pygame.font.SysFont("monospace", size, bold=bold)
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_width()


def draw_overlay(surface, alpha=180):
    """Draw a semi-transparent dark overlay over the whole surface."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))