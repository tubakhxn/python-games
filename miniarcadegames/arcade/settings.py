"""Shared configuration values for the Mini Arcade."""

WIDTH = 960
HEIGHT = 600
FPS = 60

COLORS = {
    "background": (10, 12, 24),
    "panel": (21, 24, 45),
    "accent": (255, 176, 59),
    "accent_alt": (59, 206, 255),
    "text": (235, 239, 247),
    "muted": (114, 125, 140),
    "danger": (255, 87, 102),
    "success": (93, 255, 206),
}

def get_color(name: str) -> tuple[int, int, int]:
    """Return a color tuple, defaulting to white for unknown keys."""
    return COLORS.get(name, (255, 255, 255))
