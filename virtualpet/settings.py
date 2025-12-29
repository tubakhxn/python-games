from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_FILE = BASE_DIR / "storage" / "pet_state.json"
SOUND_DIR = BASE_DIR / "assets" / "sounds"

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

STAT_MIN = 0
STAT_MAX = 100

STAT_NAMES = [
    "hunger",
    "happiness",
    "energy",
    "cleanliness",
    "health",
]

# Per-second decay for each stat when the app is running or closed
DECAY_PER_SECOND = {
    "hunger": 0.006,
    "happiness": 0.004,
    "energy": 0.005,
    "cleanliness": 0.003,
    "health": 0.001,
}

# Gains applied during each action
ACTION_EFFECTS = {
    "feed": {"hunger": 28, "health": 4},
    "play": {"happiness": 25, "energy": -14, "cleanliness": -6},
    "sleep": {"energy": 35, "health": 5},
    "clean": {"cleanliness": 40, "happiness": 8},
    "pet": {"happiness": 12},
}

MOOD_THRESHOLDS = {
    "happy": {
        "hunger": 60,
        "happiness": 70,
        "energy": 55,
        "cleanliness": 50,
        "health": 60,
    },
    "hungry": {"hunger": 35},
    "sleepy": {"energy": 30},
    "dirty": {"cleanliness": 35},
    "sick": {"health": 35},
    "bored": {"happiness": 40},
}

COLOR_PALETTE = {
    "sky_day": (160, 210, 255),
    "sky_evening": (255, 193, 140),
    "sky_night": (24, 34, 70),
    "ground_day": (255, 248, 230),
    "ground_night": (40, 45, 70),
    "panel": (34, 34, 50),
    "panel_light": (67, 67, 100),
    "text_primary": (240, 240, 255),
    "accent": (255, 160, 180),
    "accent_dark": (220, 110, 140),
    "health": (255, 99, 132),
    "happiness": (255, 206, 86),
    "energy": (54, 162, 235),
    "hunger": (75, 192, 192),
    "cleanliness": (153, 102, 255),
}

BUTTON_LAYOUT = [
    {"label": "Feed", "action": "feed"},
    {"label": "Play", "action": "play"},
    {"label": "Sleep", "action": "sleep"},
    {"label": "Clean", "action": "clean"},
]

IDLE_MESSAGES = [
    "I love hanging out with you!",
    "Tap me or type something!",
    "What game should we play next?",
    "I could go for a snack...",
    "Let's dance together!",
]

RESPONSE_LIBRARY = {
    "food": "Mmm that sounds tasty!",
    "sleep": "I could nap for days.",
    "play": "Games? I am in!",
    "love": "Love you right back!",
}

TYPE_RESPONSE_FALLBACKS = [
    "Tell me more!",
    "Haha, you're funny!",
    "Interesting...",
    "I am listening.",
]

SPEECH_DURATION = 4.2
IDLE_DIALOGUE_INTERVAL = (14, 28)
PET_AREA = (SCREEN_WIDTH // 2 - 140, 160, 280, 280)

SLEEP_MIN_DURATION = 8.0
