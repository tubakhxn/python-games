from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

import pygame

from effects import ParticleSystem
from settings import (
    BUTTON_LAYOUT,
    COLOR_PALETTE,
    PET_AREA,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from utils import ease_out_back, get_day_night_colors, lerp, screen_center, wrap_text


class Button:
    def __init__(self, rect: Tuple[int, int, int, int], label: str, action: str) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.is_pressed = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, active: bool = True) -> None:
        base_color = COLOR_PALETTE["accent_dark" if active else "panel_light"]
        hover_color = COLOR_PALETTE["accent"]
        color = hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) and active else base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=18)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=18)
        label_surface = font.render(self.label, True, COLOR_PALETTE["text_primary"])
        surface.blit(label_surface, label_surface.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return True
            self.is_pressed = False
        return False


class StatBar:
    def __init__(self, label: str, color: Tuple[int, int, int], rect: Tuple[int, int, int, int]) -> None:
        self.label = label
        self.color = color
        self.rect = pygame.Rect(rect)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, value: float) -> None:
        pygame.draw.rect(surface, COLOR_PALETTE["panel_light"], self.rect, border_radius=10)
        inner_width = int(self.rect.width * (value / 100))
        inner_rect = pygame.Rect(self.rect.x, self.rect.y, inner_width, self.rect.height)
        pygame.draw.rect(surface, self.color, inner_rect, border_radius=10)
        text_surface = font.render(f"{self.label}: {int(value)}%", True, COLOR_PALETTE["text_primary"])
        surface.blit(text_surface, (self.rect.x + 12, self.rect.y + 6))


class SpeechBubble:
    def __init__(self) -> None:
        self.padding = 16

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, text: str) -> None:
        if not text:
            return
        max_width = 320
        lines = wrap_text(text, font, max_width)
        width = max(font.size(line)[0] for line in lines) + self.padding * 2
        height = len(lines) * font.get_linesize() + self.padding * 2
        pet_center = (PET_AREA[0] + PET_AREA[2] // 2, PET_AREA[1])
        bubble_rect = pygame.Rect(0, 0, width, height)
        bubble_rect.midbottom = (pet_center[0], PET_AREA[1] - 20)
        bubble_rect.y = max(30, bubble_rect.y)
        pygame.draw.rect(surface, COLOR_PALETTE["panel"], bubble_rect, border_radius=18)
        pygame.draw.rect(surface, COLOR_PALETTE["accent"], bubble_rect, width=2, border_radius=18)
        tip = [
            (bubble_rect.centerx, bubble_rect.bottom),
            (bubble_rect.centerx + 20, bubble_rect.bottom + 20),
            (bubble_rect.centerx - 20, bubble_rect.bottom + 20),
        ]
        pygame.draw.polygon(surface, COLOR_PALETTE["panel"], tip)
        for index, line in enumerate(lines):
            render = font.render(line, True, COLOR_PALETTE["text_primary"])
            surface.blit(render, (bubble_rect.x + self.padding, bubble_rect.y + self.padding + index * font.get_linesize()))


class TextInput:
    def __init__(self, rect: Tuple[int, int, int, int]) -> None:
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.active = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = COLOR_PALETTE["accent"] if self.active else COLOR_PALETTE["panel_light"]
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, COLOR_PALETTE["panel"], self.rect, width=2, border_radius=14)
        render = font.render(self.text or "Type to chat...", True, COLOR_PALETTE["text_primary"])
        surface.blit(render, (self.rect.x + 12, self.rect.y + 10))

    def handle_event(self, event: pygame.event.Event) -> Tuple[bool, str]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False, ""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                text = self.text.strip()
                self.text = ""
                return True, text
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and len(self.text) <= 60:
                self.text += event.unicode
        return False, ""


class SoundToggle:
    def __init__(self, rect: Tuple[int, int, int, int], enabled: bool = True) -> None:
        self.rect = pygame.Rect(rect)
        self.enabled = enabled

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        base_color = COLOR_PALETTE["panel_light"]
        pygame.draw.rect(surface, base_color, self.rect, border_radius=20)
        knob_radius = self.rect.height // 2 - 4
        knob_x = self.rect.x + knob_radius + 4 if not self.enabled else self.rect.right - knob_radius - 4
        knob_color = COLOR_PALETTE["accent" if self.enabled else "panel"]
        pygame.draw.circle(surface, knob_color, (knob_x, self.rect.centery), knob_radius)
        label = font.render("Sound", True, COLOR_PALETTE["text_primary"])
        surface.blit(label, (self.rect.right + 12, self.rect.y + 5))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.enabled = not self.enabled
            return True
        return False


class PetRenderer:
    def __init__(self) -> None:
        self.surface = pygame.Surface((PET_AREA[2], PET_AREA[3]), pygame.SRCALPHA)

    def draw(self, surface: pygame.Surface, pet, dt: float) -> None:
        self.surface.fill((0, 0, 0, 0))
        bounce = 1 + 0.18 * ease_out_back(min(1.0, max(0.0, pet.screen_bounce)))
        scale = 1 + 0.08 * math.sin(pygame.time.get_ticks() / 500)
        if pet.screen_bounce > 0:
            pet.screen_bounce = max(0.0, pet.screen_bounce - dt * 1.5)
        radius = 110 * scale * bounce
        center = (PET_AREA[2] // 2, PET_AREA[3] // 2)
        mood_colors = {
            "idle": (255, 220, 220),
            "excited": (255, 250, 180),
            "hungry": (255, 180, 150),
            "sleeping": (200, 200, 230),
            "dirty": (210, 200, 255),
            "bored": (200, 255, 220),
            "sick": (255, 200, 200),
            "sleepy": (230, 230, 255),
        }
        body_color = mood_colors.get(pet.mood, (255, 240, 220))
        pygame.draw.circle(self.surface, body_color, center, int(radius))
        self._draw_face(pet, center, radius)
        self._draw_ears(body_color, center, radius)
        surface.blit(self.surface, (PET_AREA[0], PET_AREA[1]))

    def _draw_face(self, pet, center: Tuple[int, int], radius: float) -> None:
        eye_offset_x = 45
        eye_offset_y = -20
        blink_scale = pet.blink_state
        for direction in (-1, 1):
            eye_center = (center[0] + eye_offset_x * direction, center[1] + eye_offset_y)
            eye_rect = pygame.Rect(0, 0, 24, max(6, int(24 * blink_scale)))
            eye_rect.center = eye_center
            pygame.draw.ellipse(self.surface, (40, 40, 60), eye_rect)
        mouth_rect = pygame.Rect(0, 0, 60, 25)
        mouth_rect.center = (center[0], center[1] + 30)
        curve = 10 if pet.mood in ("excited", "idle") else -10
        pygame.draw.arc(self.surface, (60, 20, 20), mouth_rect, math.radians(180 - curve), math.radians(360 + curve), 4)

    def _draw_ears(self, color: Tuple[int, int, int], center: Tuple[int, int], radius: float) -> None:
        ear_positions = [(-radius * 0.6, -radius * 0.5), (radius * 0.6, -radius * 0.5)]
        for offset_x, offset_y in ear_positions:
            ear_center = (center[0] + int(offset_x), center[1] + int(offset_y))
            pygame.draw.circle(self.surface, color, ear_center, int(radius * 0.45))


class GameUI:
    def __init__(self, font_large: pygame.font.Font, font_small: pygame.font.Font) -> None:
        self.font_large = font_large
        self.font_small = font_small
        self.buttons: List[Button] = []
        self._create_buttons()
        self.stat_bars: Dict[str, StatBar] = {}
        self._create_stat_bars()
        self.speech_bubble = SpeechBubble()
        self.text_input = TextInput((SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 70, 520, 50))
        self.particles = ParticleSystem()
        self.sound_toggle = SoundToggle((40, 40, 80, 36))
        self.pet_renderer = PetRenderer()

    def _create_buttons(self) -> None:
        width = 150
        height = 60
        spacing = 20
        total_width = len(BUTTON_LAYOUT) * width + (len(BUTTON_LAYOUT) - 1) * spacing
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        y = SCREEN_HEIGHT - 140
        for index, config in enumerate(BUTTON_LAYOUT):
            x = start_x + index * (width + spacing)
            self.buttons.append(Button((x, y, width, height), config["label"], config["action"]))

    def _create_stat_bars(self) -> None:
        x = 60
        y = 60
        bar_width = 220
        bar_height = 30
        spacing = 40
        colors = {
            "hunger": COLOR_PALETTE["hunger"],
            "happiness": COLOR_PALETTE["happiness"],
            "energy": COLOR_PALETTE["energy"],
            "cleanliness": COLOR_PALETTE["cleanliness"],
            "health": COLOR_PALETTE["health"],
        }
        for index, (stat, color) in enumerate(colors.items()):
            rect = (x, y + index * spacing, bar_width, bar_height)
            self.stat_bars[stat] = StatBar(stat.capitalize(), color, rect)

    def draw(self, surface: pygame.Surface, pet, dt: float) -> None:
        sky, ground = get_day_night_colors()
        surface.fill(sky)
        pygame.draw.rect(surface, ground, (0, SCREEN_HEIGHT - 160, SCREEN_WIDTH, 200))
        for stat, bar in self.stat_bars.items():
            bar.draw(surface, self.font_small, pet.stats[stat])
        for button in self.buttons:
            button.draw(surface, self.font_small, active=not pet.sleeping)
        self.text_input.draw(surface, self.font_small)
        if pet.is_showing_message:
            self.speech_bubble.draw(surface, self.font_small, pet.message)
        self.pet_renderer.draw(surface, pet, dt)
        self.particles.draw(surface)
        status = self.font_small.render(f"Mood: {pet.mood}", True, COLOR_PALETTE["text_primary"])
        surface.blit(status, (SCREEN_WIDTH - status.get_width() - 40, 40))
        self.sound_toggle.draw(surface, self.font_small)

    def handle_event(self, event: pygame.event.Event, on_action: Callable[[str], None]) -> Tuple[bool, str]:
        submitted = False
        submitted_text = ""
        for button in self.buttons:
            if button.handle_event(event):
                on_action(button.action)
        if self.sound_toggle.handle_event(event):
            pass
        triggered, submitted_text = self.text_input.handle_event(event)
        if triggered:
            submitted = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(PET_AREA).collidepoint(event.pos):
                on_action("pet")
        return submitted, submitted_text

    def update(self, dt: float) -> None:
        self.particles.update(dt)

    def spawn_effect(self, effect_type: str, center: Tuple[int, int]) -> None:
        if effect_type == "heart":
            self.particles.emit_heart(center)
        elif effect_type == "star":
            self.particles.emit_star(center)

    def center_of_pet(self) -> Tuple[int, int]:
        return (PET_AREA[0] + PET_AREA[2] // 2, PET_AREA[1] + PET_AREA[3] // 2)
