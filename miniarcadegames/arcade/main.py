"""Entry point for the Mini Arcade application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import pygame

from . import settings
from .games.dodge import DodgeGame
from .games.pong import PongGame
from .games.snake import SnakeGame


@dataclass
class Button:
    """Basic button used on the menu screen."""

    rect: pygame.Rect
    label: str
    action: Callable[[], None]
    hovered: bool = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        base_color = settings.get_color("panel")
        accent = settings.get_color("accent")
        color = accent if self.hovered else base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_color = settings.get_color("background") if self.hovered else settings.get_color("text")
        text = font.render(self.label, True, text_color)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def handle_click(self) -> None:
        self.action()


class FadeTransition:
    """Handles fade-to-black transitions between scenes."""

    def __init__(self, duration: float = 0.4) -> None:
        self.duration = duration
        self.state = "idle"
        self.timer = 0.0
        self.target: Optional[str] = None

    def busy(self) -> bool:
        return self.state != "idle"

    def start(self, target: Optional[str]) -> None:
        if self.busy():
            return
        self.state = "out"
        self.timer = 0.0
        self.target = target

    def update(self, dt: float, switch_callback: Callable[[Optional[str]], None]) -> None:
        if self.state == "idle":
            return
        self.timer += dt
        if self.timer >= self.duration:
            self.timer = 0.0
            if self.state == "out":
                switch_callback(self.target)
                self.state = "in"
            else:
                self.state = "idle"

    def alpha(self) -> int:
        if self.state == "idle":
            return 0
        progress = min(self.timer / self.duration, 1.0)
        if self.state == "out":
            return int(progress * 255)
        return int((1 - progress) * 255)


class ArcadeApp:
    """Coordinates the menu, transitions, and individual games."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Mini Arcade")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 80)
        self.menu_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 26)
        self.credit_tag = "Developer: tubakhxn"

        self.games = {
            "Snake": SnakeGame(),
            "Pong": PongGame(),
            "Dodge": DodgeGame(),
        }
        self.active_game: Optional[str] = None
        # Centralized transition controller keeps every scene change consistent.
        self.transition = FadeTransition(0.4)
        self.buttons = self._build_buttons()
        self.menu_hint = self.buttons[0].label
        self.running = True

    def _build_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        total = len(self.games)
        button_width = 280
        button_height = 72
        spacing = 18
        start_y = settings.HEIGHT // 2 - (total * (button_height + spacing)) // 2
        for index, label in enumerate(self.games.keys()):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = settings.WIDTH // 4
            rect.y = start_y + index * (button_height + spacing)
            buttons.append(Button(rect, label, lambda name=label: self._queue_state_change(name)))
        return buttons

    def _queue_state_change(self, target: Optional[str]) -> None:
        if target == self.active_game:
            return
        self.transition.start(target)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.active_game:
                self._run_active_game(events, dt)
            else:
                self._run_menu(events)

            self.transition.update(dt, self._apply_state_change)
            self._draw_transition_overlay()
            pygame.display.flip()
        pygame.quit()

    def _run_menu(self, events: list[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = None
        for button in self.buttons:
            button.hovered = button.rect.collidepoint(mouse_pos)
            if button.hovered:
                hovered = button.label
        if hovered:
            self.menu_hint = hovered
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button.hovered:
                        button.handle_click()
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    index = event.key - pygame.K_1
                    if 0 <= index < len(self.buttons):
                        self.buttons[index].handle_click()

        self._draw_menu()

    def _draw_menu(self) -> None:
        self.screen.fill(settings.get_color("background"))
        title = self.title_font.render("Mini Arcade", True, settings.get_color("text"))
        self.screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, 120)))

        for button in self.buttons:
            button.draw(self.screen, self.menu_font)

        info_panel = pygame.Rect(settings.WIDTH // 2 + 60, 220, settings.WIDTH // 2 - 120, 260)
        pygame.draw.rect(self.screen, settings.get_color("panel"), info_panel, border_radius=16)
        pygame.draw.rect(self.screen, settings.get_color("accent_alt"), info_panel, width=2, border_radius=16)

        hint_game = self.games.get(self.menu_hint)
        if hint_game:
            title = self.menu_font.render(hint_game.name, True, settings.get_color("text"))
            self.screen.blit(title, title.get_rect(midtop=(info_panel.centerx, info_panel.y + 16)))
            self._draw_wrapped_text(hint_game.instructions, info_panel.inflate(-40, -80), 28)
        else:
            placeholder = self.small_font.render("Hover a game to view its controls", True, settings.get_color("muted"))
            self.screen.blit(placeholder, placeholder.get_rect(center=info_panel.center))

        footer = self.small_font.render("Press 1/2/3 as shortcuts", True, settings.get_color("muted"))
        self.screen.blit(footer, footer.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 40)))

        credit = self.small_font.render(self.credit_tag, True, settings.get_color("accent_alt"))
        self.screen.blit(credit, credit.get_rect(bottomright=(settings.WIDTH - 24, settings.HEIGHT - 24)))

    def _draw_wrapped_text(self, text: str, rect: pygame.Rect, line_height: int) -> None:
        words = text.split()
        line = ""
        y = rect.y
        for word in words:
            test = f"{line} {word}".strip()
            rendered = self.small_font.render(test, True, settings.get_color("text"))
            if rendered.get_width() > rect.width and line:
                rendered = self.small_font.render(line, True, settings.get_color("text"))
                self.screen.blit(rendered, (rect.x, y))
                y += line_height
                line = word
            else:
                line = test
        if line:
            rendered = self.small_font.render(line, True, settings.get_color("text"))
            self.screen.blit(rendered, (rect.x, y))

    def _run_active_game(self, events: list[pygame.event.Event], dt: float) -> None:
        game = self.games[self.active_game]
        keep_playing = game.handle_events(events)
        if not keep_playing:
            self._queue_state_change(None)
        else:
            game.update(dt)
        # Always render the latest state so the fade overlay works on the final frame too.
        game.draw(self.screen)
        header = self.small_font.render(f"Playing: {game.name}", True, settings.get_color("text"))
        self.screen.blit(header, (16, settings.HEIGHT - 36))
        credit = self.small_font.render(self.credit_tag, True, settings.get_color("accent_alt"))
        credit_pos = credit.get_rect(bottomright=(settings.WIDTH - 24, settings.HEIGHT - 36))
        self.screen.blit(credit, credit_pos)

    def _apply_state_change(self, target: Optional[str]) -> None:
        if target is None:
            self.active_game = None
        else:
            game = self.games[target]
            game.reset()
            self.active_game = target

    def _draw_transition_overlay(self) -> None:
        alpha = self.transition.alpha()
        if alpha <= 0:
            return
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))


def main() -> None:
    """Convenience wrapper so the module is executable."""
    ArcadeApp().run()


if __name__ == "__main__":  # pragma: no cover - manual launch only
    main()
