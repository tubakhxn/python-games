"""Simple Snake implementation for the arcade."""
from __future__ import annotations

import random
from typing import Iterable

import pygame

from .. import settings
from .base_game import BaseGame


class SnakeGame(BaseGame):
    """Classic grid-based snake."""

    def __init__(self) -> None:
        instructions = (
            "Grow the snake by eating the glowing squares.\n"
            "Arrow keys turn, Enter restarts after a crash.\n"
            "Press Esc or Backspace to return to the menu."
        )
        super().__init__("Snake", instructions)

    def reset(self) -> None:
        self.grid = 20
        self.cols = settings.WIDTH // self.grid
        self.rows = settings.HEIGHT // self.grid
        center = pygame.Vector2(self.cols // 2, self.rows // 2)
        self.body: list[pygame.Vector2] = [center - pygame.Vector2(i, 0) for i in range(4)]
        self.direction = pygame.Vector2(1, 0)
        self.next_direction = pygame.Vector2(1, 0)
        self.apple = self._random_cell()
        self.move_timer = 0.0
        self.move_delay = 0.12
        self.score = 0
        self.game_over = False

    def process_events(self, events: Iterable[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.game_over:
                    self.reset()
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT) and not self.game_over:
                    self._queue_direction(event.key)

    def _queue_direction(self, key: int) -> None:
        mapping = {
            pygame.K_UP: pygame.Vector2(0, -1),
            pygame.K_DOWN: pygame.Vector2(0, 1),
            pygame.K_LEFT: pygame.Vector2(-1, 0),
            pygame.K_RIGHT: pygame.Vector2(1, 0),
        }
        new_dir = mapping[key]
        if len(self.body) <= 1 or self.body[0] + new_dir != self.body[1]:
            self.next_direction = new_dir

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        # Move at a fixed cadence so speed stays consistent regardless of FPS.
        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            self.move_timer -= self.move_delay
            self.direction = self.next_direction
            new_head = self.body[0] + self.direction
            if self._hits_wall(new_head) or new_head in self.body:
                self.game_over = True
                return
            self.body.insert(0, new_head)
            if new_head == self.apple:
                self.score += 1
                self.apple = self._random_cell()
            else:
                self.body.pop()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.get_color("background"))
        self._draw_grid(surface)
        for index, segment in enumerate(self.body):
            color = settings.get_color("accent") if index == 0 else settings.get_color("accent_alt")
            rect = pygame.Rect(segment.x * self.grid, segment.y * self.grid, self.grid, self.grid)
            pygame.draw.rect(surface, color, rect)
        apple_rect = pygame.Rect(self.apple.x * self.grid, self.apple.y * self.grid, self.grid, self.grid)
        pygame.draw.rect(surface, settings.get_color("success"), apple_rect)

        score_text = self.primary_font.render(f"Score: {self.score}", True, settings.get_color("text"))
        surface.blit(score_text, (16, 12))

        if self.game_over:
            self._draw_game_over(surface)

        self.draw_instruction_text(surface, self.instructions, x=16, y=settings.HEIGHT - 120)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        line_color = settings.get_color("panel")
        for x in range(0, settings.WIDTH, self.grid):
            pygame.draw.line(surface, line_color, (x, 0), (x, settings.HEIGHT), 1)
        for y in range(0, settings.HEIGHT, self.grid):
            pygame.draw.line(surface, line_color, (0, y), (settings.WIDTH, y), 1)

    def _draw_game_over(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 180))
        surface.blit(overlay, (0, 0))
        title = self.primary_font.render("Crash! Press Enter to reset", True, settings.get_color("danger"))
        rect = title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
        surface.blit(title, rect)

    def _random_cell(self) -> pygame.Vector2:
        while True:
            cell = pygame.Vector2(
                random.randint(0, self.cols - 1),
                random.randint(0, self.rows - 1),
            )
            if cell not in self.body:
                return cell

    def _hits_wall(self, position: pygame.Vector2) -> bool:
        return not (0 <= position.x < self.cols and 0 <= position.y < self.rows)
