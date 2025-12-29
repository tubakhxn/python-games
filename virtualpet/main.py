from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict

import pygame

from data_manager import load_state, save_state
from pet import Pet
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from ui import GameUI
from utils import create_tone_sound


class SoundManager:
    def __init__(self) -> None:
        self.cache: Dict[int, pygame.mixer.Sound] = {}
        self.enabled = True

    def play(self, frequency: float) -> None:
        if not self.enabled:
            return
        freq_key = int(frequency)
        if freq_key not in self.cache:
            self.cache[freq_key] = create_tone_sound(pygame, freq_key, 0.2)
        self.cache[freq_key].play()


class VirtualPetGame:
    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 1, 256)
        pygame.init()
        pygame.display.set_caption("Mochi the Virtual Pal")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        stats, last_timestamp, sleeping = load_state()
        self.pet = Pet(stats, sleeping)
        seconds_passed = time.time() - last_timestamp
        self.pet.apply_time_skip(seconds_passed)
        self.font_large = pygame.font.SysFont("fredokaone", 42)
        self.font_small = pygame.font.SysFont("poppins", 24)
        self.ui = GameUI(self.font_large, self.font_small)
        self.sound_manager = SoundManager()
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                submitted, text = self.ui.handle_event(event, self.handle_action)
                if submitted and text:
                    reaction = self.pet.respond_to_text(text)
                    self.process_reaction(reaction)
            self.pet.update(dt)
            self.ui.update(dt)
            self.sound_manager.enabled = self.ui.sound_toggle.enabled
            self.ui.draw(self.screen, self.pet, dt)
            pygame.display.flip()
        self.shutdown()

    def handle_action(self, action: str) -> None:
        if action == "pet":
            reaction = self.pet.pet_interaction()
        else:
            reaction = self.pet.perform_action(action)
        self.process_reaction(reaction)

    def process_reaction(self, reaction: Dict[str, str | float]) -> None:
        if not reaction:
            return
        if "effect" in reaction:
            self.ui.spawn_effect(reaction["effect"], self.ui.center_of_pet())
        if "sound_freq" in reaction:
            self.sound_manager.play(float(reaction["sound_freq"]))

    def shutdown(self) -> None:
        save_state(self.pet.to_dict(), self.pet.sleeping)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = VirtualPetGame()
    game.run()
