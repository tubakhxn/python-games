from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple

import pygame

from settings import COLOR_PALETTE


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    color: Tuple[int, int, int]
    size: float

    def update(self, dt: float) -> None:
        self.life -= dt
        self.position += self.velocity * dt
        self.velocity.y -= 10 * dt

    def draw(self, surface: pygame.Surface) -> None:
        alpha = max(0, min(255, int(255 * (self.life / 1.2))))
        if alpha <= 0:
            return
        color = (*self.color, alpha)
        temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
        surface.blit(temp_surface, (self.position.x - self.size, self.position.y - self.size))


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def emit_heart(self, origin: Tuple[int, int]) -> None:
        for _ in range(6):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-5, 5))
            part = Particle(
                position=pygame.Vector2(origin),
                velocity=vel,
                life=random.uniform(0.6, 1.2),
                color=COLOR_PALETTE["accent"],
                size=random.uniform(6, 10),
            )
            self.particles.append(part)

    def emit_star(self, origin: Tuple[int, int]) -> None:
        for _ in range(4):
            vel = pygame.Vector2(random.uniform(-15, 15), random.uniform(-5, 5))
            part = Particle(
                position=pygame.Vector2(origin),
                velocity=vel,
                life=random.uniform(0.4, 0.9),
                color=COLOR_PALETTE["accent_dark"],
                size=random.uniform(4, 7),
            )
            self.particles.append(part)

    def update(self, dt: float) -> None:
        for particle in list(self.particles):
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(surface)
