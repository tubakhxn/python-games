"""Minimal Pong variant."""
from __future__ import annotations

import random
from typing import Iterable

import pygame

from .. import settings
from .base_game import BaseGame


class PongGame(BaseGame):
    """Single-player Pong versus a simple AI paddle."""

    def __init__(self) -> None:
        instructions = (
            "Move with W/S or the arrow keys.\n"
            "First to 7 points wins the round.\n"
            "Esc/Backspace returns to the menu."
        )
        super().__init__("Pong", instructions)

    def reset(self) -> None:
        self.player = pygame.Rect(40, settings.HEIGHT // 2 - 45, 14, 90)
        self.ai = pygame.Rect(settings.WIDTH - 54, settings.HEIGHT // 2 - 45, 14, 90)
        self.ball = pygame.Rect(settings.WIDTH // 2 - 10, settings.HEIGHT // 2 - 10, 20, 20)
        self.ball_velocity = pygame.Vector2(0, 0)
        self.ball_speed = 360
        self.player_speed = 420
        self.ai_speed = 380
        self.player_score = 0
        self.ai_score = 0
        self.round_over = True
        self.round_cooldown = 1.0
        self.pending_direction = random.choice((-1, 1))

    def process_events(self, events: Iterable[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.round_over:
                self._serve_ball()

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move_dir = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_dir -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_dir += 1
        self.player.y += move_dir * self.player_speed * dt
        self.player.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

        if self.round_over:
            self.round_cooldown -= dt
            if self.round_cooldown <= 0:
                self._serve_ball()
        else:
            self._move_ball(dt)
            self._move_ai(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(settings.get_color("background"))
        pygame.draw.rect(surface, settings.get_color("panel"), pygame.Rect(settings.WIDTH // 2 - 2, 0, 4, settings.HEIGHT))
        pygame.draw.ellipse(surface, settings.get_color("accent_alt"), self.ball)
        pygame.draw.rect(surface, settings.get_color("accent"), self.player)
        pygame.draw.rect(surface, settings.get_color("muted"), self.ai)

        hud = self.primary_font.render(f"{self.player_score} : {self.ai_score}", True, settings.get_color("text"))
        surface.blit(hud, hud.get_rect(center=(settings.WIDTH // 2, 40)))

        if self.round_over:
            info = self.small_font.render("Press Enter to serve", True, settings.get_color("muted"))
            surface.blit(info, info.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))

        self.draw_instruction_text(surface, self.instructions, x=16, y=settings.HEIGHT - 120)

    def _move_ball(self, dt: float) -> None:
        self.ball.x += int(self.ball_velocity.x * dt)
        self.ball.y += int(self.ball_velocity.y * dt)

        if self.ball.top <= 0 or self.ball.bottom >= settings.HEIGHT:
            self.ball_velocity.y *= -1
            self.ball.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

        if self.ball.colliderect(self.player) and self.ball_velocity.x < 0:
            self._bounce_off_paddle(self.player)
        elif self.ball.colliderect(self.ai) and self.ball_velocity.x > 0:
            self._bounce_off_paddle(self.ai)

        if self.ball.right < 0:
            self.ai_score += 1
            self._end_round(direction=1)
        elif self.ball.left > settings.WIDTH:
            self.player_score += 1
            self._end_round(direction=-1)

        if self.player_score == 7 or self.ai_score == 7:
            self.player_score = 0
            self.ai_score = 0
            self._end_round(direction=random.choice((-1, 1)))

    def _move_ai(self, dt: float) -> None:
        target = self.ball.centery
        if target < self.ai.centery - 10:
            self.ai.y -= self.ai_speed * dt
        elif target > self.ai.centery + 10:
            self.ai.y += self.ai_speed * dt
        self.ai.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def _bounce_off_paddle(self, paddle: pygame.Rect) -> None:
        # Offset controls the reflection angle so hitting near edges changes trajectory.
        offset = (self.ball.centery - paddle.centery) / (paddle.height / 2)
        speed = self.ball_speed * 1.05
        self.ball_velocity.x *= -1
        self.ball_velocity.y = speed * offset
        self.ball_velocity.scale_to_length(speed)

        if paddle is self.player:
            self.ball.left = paddle.right + 1
        else:
            self.ball.right = paddle.left - 1

    def _end_round(self, *, direction: int) -> None:
        self.round_over = True
        self.round_cooldown = 1.2
        self.pending_direction = direction
        self.ball.center = (settings.WIDTH // 2, settings.HEIGHT // 2)
        self.ball_velocity.update(0, 0)

    def _serve_ball(self) -> None:
        self.round_over = False
        self.round_cooldown = 0
        angle = random.uniform(-0.5, 0.5)
        direction = self.pending_direction or random.choice((-1, 1))
        velocity = pygame.Vector2(direction, angle)
        velocity.scale_to_length(self.ball_speed)
        self.ball_velocity = velocity

