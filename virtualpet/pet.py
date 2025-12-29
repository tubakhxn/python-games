from __future__ import annotations

import random
import time
from typing import Dict

from settings import (
    ACTION_EFFECTS,
    DECAY_PER_SECOND,
    IDLE_DIALOGUE_INTERVAL,
    IDLE_MESSAGES,
    MOOD_THRESHOLDS,
    SLEEP_MIN_DURATION,
    SPEECH_DURATION,
    STAT_MAX,
    STAT_MIN,
    STAT_NAMES,
    TYPE_RESPONSE_FALLBACKS,
    RESPONSE_LIBRARY,
)
from utils import clamp, pick_response, random_in_range


class Pet:
    def __init__(self, stats: Dict[str, float], sleeping: bool = False) -> None:
        self.stats = {name: clamp(value, STAT_MIN, STAT_MAX) for name, value in stats.items()}
        for stat in STAT_NAMES:
            self.stats.setdefault(stat, STAT_MAX * 0.8)
        self.sleeping = sleeping
        self.sleep_timer = 0.0
        self.mood = "happy"
        self.message = "Welcome back!"
        self.message_timer = SPEECH_DURATION
        self.idle_timer = 0.0
        self.next_idle_trigger = random_in_range(IDLE_DIALOGUE_INTERVAL)
        self.screen_bounce = 0.0
        self.blink_timer = random.uniform(2.0, 5.0)
        self.blink_state = 1.0

    def apply_time_skip(self, seconds_passed: float) -> None:
        seconds_passed = max(0.0, seconds_passed)
        for stat, decay in DECAY_PER_SECOND.items():
            self.stats[stat] = clamp(self.stats[stat] - decay * seconds_passed, STAT_MIN, STAT_MAX)
        self._sync_health()

    def update(self, dt: float) -> None:
        if not self.sleeping:
            self._apply_decay(dt)
        else:
            self.sleep_timer -= dt
            self.stats["energy"] = clamp(self.stats["energy"] + 4 * dt, STAT_MIN, STAT_MAX)
            self.stats["health"] = clamp(self.stats["health"] + 1.5 * dt, STAT_MIN, STAT_MAX)
            if self.sleep_timer <= 0:
                self.sleeping = False
                self.say("That nap was perfect!")
        self.idle_timer += dt
        if self.idle_timer >= self.next_idle_trigger and not self.sleeping:
            self.say(random.choice(IDLE_MESSAGES))
            self.idle_timer = 0
            self.next_idle_trigger = random_in_range(IDLE_DIALOGUE_INTERVAL)
        if self.message_timer > 0:
            self.message_timer -= dt
        self._update_blink(dt)
        self._sync_health()
        self._update_mood()

    def perform_action(self, action: str) -> Dict[str, str | float]:
        response: Dict[str, str | float] = {}
        if action == "sleep":
            if self.sleeping:
                self.say("Shh... already napping.")
                return response
            self.sleeping = True
            self.sleep_timer = SLEEP_MIN_DURATION
            self.say("Goodnight! Wake me soon.")
            response["sound_freq"] = 220
            return response
        if action not in ACTION_EFFECTS:
            return response
        for stat, delta in ACTION_EFFECTS[action].items():
            self.stats[stat] = clamp(self.stats[stat] + delta, STAT_MIN, STAT_MAX)
        if action == "feed":
            self.say("Nom nom nom!")
            response["effect"] = "heart"
            response["sound_freq"] = 520
        elif action == "play":
            self.say("Woohoo! That was fun!")
            response["effect"] = "star"
            response["sound_freq"] = 700
        elif action == "clean":
            self.say("Sparkly clean!")
            response["effect"] = "heart"
            response["sound_freq"] = 600
        self.screen_bounce = 1.0
        return response

    def pet_interaction(self) -> Dict[str, str | float]:
        self.say("Hehe! That tickles!")
        self.stats["happiness"] = clamp(self.stats["happiness"] + ACTION_EFFECTS["pet"]["happiness"], STAT_MIN, STAT_MAX)
        self.screen_bounce = 1.1
        return {"effect": "heart", "sound_freq": 650}

    def respond_to_text(self, text: str) -> Dict[str, str | float]:
        response_text = pick_response(text, RESPONSE_LIBRARY, TYPE_RESPONSE_FALLBACKS)
        self.say(response_text)
        self.screen_bounce = 0.7
        return {"sound_freq": 420}

    def say(self, text: str) -> None:
        self.message = text
        self.message_timer = SPEECH_DURATION

    @property
    def is_showing_message(self) -> bool:
        return self.message_timer > 0 and bool(self.message)

    def _apply_decay(self, dt: float) -> None:
        for stat, decay in DECAY_PER_SECOND.items():
            self.stats[stat] = clamp(self.stats[stat] - decay * dt, STAT_MIN, STAT_MAX)

    def _update_mood(self) -> None:
        if self.sleeping:
            self.mood = "sleeping"
            return
        if self.stats["health"] <= MOOD_THRESHOLDS["sick"]["health"]:
            self.mood = "sick"
            return
        priority = ["hungry", "sleepy", "dirty", "bored"]
        for mood in priority:
            for stat, limit in MOOD_THRESHOLDS[mood].items():
                if self.stats[stat] <= limit:
                    self.mood = mood
                    return
        thresholds = MOOD_THRESHOLDS["happy"]
        if all(self.stats[name] >= limit for name, limit in thresholds.items()):
            self.mood = "excited"
        else:
            self.mood = "idle"

    def _sync_health(self) -> None:
        avg = sum(self.stats[key] for key in ("hunger", "happiness", "energy", "cleanliness")) / 4
        delta = (avg - self.stats["health"]) * 0.02
        self.stats["health"] = clamp(self.stats["health"] + delta, STAT_MIN, STAT_MAX)

    def _update_blink(self, dt: float) -> None:
        self.blink_timer -= dt
        if self.blink_timer <= 0:
            self.blink_state = 0.0
            self.blink_timer = random.uniform(3.0, 6.0)
        if self.blink_state < 1.0:
            self.blink_state += dt * 4
            if self.blink_state > 1.0:
                self.blink_state = 1.0

    def to_dict(self) -> Dict[str, float]:
        return {name: float(value) for name, value in self.stats.items()}
