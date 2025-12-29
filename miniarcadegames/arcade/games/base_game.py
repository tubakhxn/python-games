"""Base class shared by all arcade games."""
from __future__ import annotations

from typing import Iterable

import pygame


class BaseGame:
    """Simple template that exposes the methods the arcade expects."""

    EXIT_KEYS = {pygame.K_ESCAPE, pygame.K_BACKSPACE}

    def __init__(self, name: str, instructions: str) -> None:
        self.name = name
        self.instructions = instructions
        self.primary_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.reset()

    def reset(self) -> None:  # pragma: no cover - runtime behavior
        raise NotImplementedError

    def handle_events(self, events: Iterable[pygame.event.Event]) -> bool:
        """Return False when the player wants to exit back to the menu."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in self.EXIT_KEYS:
                return False
        self.process_events(events)
        return True

    def process_events(self, events: Iterable[pygame.event.Event]) -> None:
        """Hook for subclasses to consume events after exit keys were handled."""

    def update(self, dt: float) -> None:  # pragma: no cover - runtime behavior
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:  # pragma: no cover
        raise NotImplementedError

    def draw_instruction_text(
        self,
        surface: pygame.Surface,
        text: str,
        *,
        x: int = 10,
        y: int = 10,
    ) -> None:
        """Render helper used by several mini games."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            rendered = self.small_font.render(line, True, (230, 234, 244))
            surface.blit(rendered, (x, y))
            y += rendered.get_height() + 4
