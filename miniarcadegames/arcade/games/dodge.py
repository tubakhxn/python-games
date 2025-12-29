"""Falling block dodge mini-game."""
from __future__ import annotations

import random
from typing import Iterable

import pygame

from .. import settings
from .base_game import BaseGame


class DodgeGame(BaseGame):
    """Stay alive by dodging randomly falling blocks."""

    def __init__(self) -> None:
        instructions = (
            "Move with WASD or the arrow keys.\n"
            "Survive as long as possible without touching a block.\n"
            "Enter restarts after a crash, Esc/Backspace exits."
        )
        super().__init__("Dodge", instructions)

    def reset(self) -> None:
        self.player = pygame.Rect(settings.WIDTH // 2 - 18, settings.HEIGHT - 70, 36, 36)
        self.speed = 420
        self.obstacles: list[pygame.Rect] = []
        self.obstacle_speeds: list[float] = []
        self.spawn_timer = 0.0
        self.spawn_delay = 0.9
        self.elapsed = 0.0
        self.best_time = getattr(self, "best_time", 0.0)
        self.game_over = False

    def process_events(self, events: Iterable[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.game_over:
                self.reset()

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if move.length_squared() > 0:
            move = move.normalize()
        self.player.x += int(move.x * self.speed * dt)
        self.player.y += int(move.y * self.speed * dt)
        self.player.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

        if self.game_over:
            return

        self.elapsed += dt
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            self._spawn_obstacle()
            # Slowly ramp the difficulty by shrinking the delay each spawn.
            self.spawn_delay = max(0.35, self.spawn_delay * 0.98)

        for idx, obstacle in list(enumerate(self.obstacles)):
            obstacle.y += int(self.obstacle_speeds[idx] * dt)
            if obstacle.top > settings.HEIGHT:
                self.obstacles.pop(idx)
                self.obstacle_speeds.pop(idx)

        for obstacle in self.obstacles:
            if obstacle.colliderect(self.player):
                self.game_over = True
                self.best_time = max(self.best_time, self.elapsed)
                break

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.get_color("panel"))
        pygame.draw.rect(surface, settings.get_color("accent"), self.player, border_radius=6)
        for obstacle in self.obstacles:
            pygame.draw.rect(surface, settings.get_color("danger"), obstacle, border_radius=4)

        hud = self.primary_font.render(f"Time: {self.elapsed:0.1f}s", True, settings.get_color("text"))
        surface.blit(hud, (20, 20))
        best = self.small_font.render(f"Best: {self.best_time:0.1f}s", True, settings.get_color("muted"))
        surface.blit(best, (20, 60))

        if self.game_over:
            self._draw_game_over(surface)

        self.draw_instruction_text(surface, self.instructions, x=16, y=settings.HEIGHT - 120)

    def _spawn_obstacle(self) -> None:
        width = random.randint(40, 140)
        x = random.randint(0, settings.WIDTH - width)
        rect = pygame.Rect(x, -40, width, random.randint(20, 40))
        speed = random.randint(240, 420)
        self.obstacles.append(rect)
        self.obstacle_speeds.append(speed)

    def _draw_game_over(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        text = self.primary_font.render("Hit! Press Enter to retry", True, settings.get_color("danger"))
        surface.blit(text, text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))
