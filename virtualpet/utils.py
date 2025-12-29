import math
import random
import time
from typing import Iterable, List, Sequence, Tuple

from settings import COLOR_PALETTE, SCREEN_HEIGHT, SCREEN_WIDTH


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max - in_min == 0:
        return out_min
    normalized = (value - in_min) / (in_max - in_min)
    return out_min + normalized * (out_max - out_min)


def get_day_night_colors(system_time: float | None = None) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Return sky and ground colors based on local time of day."""
    if system_time is None:
        system_time = time.time()
    tm = time.localtime(system_time)
    day_fraction = (tm.tm_hour * 60 + tm.tm_min) / (24 * 60)
    sky = blend_palette(
        COLOR_PALETTE["sky_night"],
        COLOR_PALETTE["sky_day"],
        COLOR_PALETTE["sky_evening"],
        day_fraction,
    )
    ground = blend_palette(
        COLOR_PALETTE["ground_night"],
        COLOR_PALETTE["ground_day"],
        COLOR_PALETTE["ground_day"],
        day_fraction,
    )
    return sky, ground


def blend_palette(night: Sequence[int], day: Sequence[int], evening: Sequence[int], fraction: float) -> Tuple[int, int, int]:
    if 0.2 <= fraction <= 0.8:
        t = map_range(fraction, 0.2, 0.8, 0.0, 1.0)
        color = tuple(int(lerp(day[i], evening[i], abs(0.5 - t) * 2)) for i in range(3))
    elif fraction < 0.2:
        t = fraction / 0.2
        color = tuple(int(lerp(night[i], day[i], t)) for i in range(3))
    else:
        t = map_range(fraction, 0.8, 1.0, 0.0, 1.0)
        color = tuple(int(lerp(evening[i], night[i], t)) for i in range(3))
    return color


def wrap_text(text: str, font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def random_in_range(bounds: Tuple[float, float]) -> float:
    return random.uniform(bounds[0], bounds[1])


def screen_center() -> Tuple[int, int]:
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2


def build_tone_samples(frequency: float, duration: float, volume: float = 0.4, sample_rate: int = 44100) -> bytearray:
    sample_count = int(sample_rate * duration)
    buffer = bytearray()
    for index in range(sample_count):
        sample = volume * math.sin(2 * math.pi * frequency * index / sample_rate)
        sample_int = int(sample * 32767)
        buffer.extend(sample_int.to_bytes(2, byteorder="little", signed=True))
    return buffer


def create_tone_sound(pygame_module, frequency: float, duration: float, volume: float = 0.4):
    samples = build_tone_samples(frequency, duration, volume)
    return pygame_module.mixer.Sound(buffer=samples)


def pick_response(text: str, library: dict[str, str], fallbacks: Iterable[str]) -> str:
    lowered = text.lower()
    for keyword, line in library.items():
        if keyword in lowered:
            return line
    return random.choice(list(fallbacks))
