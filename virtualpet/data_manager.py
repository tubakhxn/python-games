import json
import time
from pathlib import Path
from typing import Dict, Tuple

from settings import BASE_DIR, STAT_NAMES, STORAGE_FILE, STAT_MAX

DEFAULT_STATS = {name: STAT_MAX * 0.8 for name in STAT_NAMES}


def ensure_storage_file() -> None:
    """Make sure we have a valid storage file for the pet state."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STORAGE_FILE.exists():
        save_state(DEFAULT_STATS, sleeping=False)


def load_state() -> Tuple[Dict[str, float], float, bool]:
    ensure_storage_file()
    try:
        with STORAGE_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            stats = data.get("stats", DEFAULT_STATS.copy())
            last_ts = float(data.get("last_timestamp", time.time()))
            sleeping = bool(data.get("sleeping", False))
            return stats, last_ts, sleeping
    except (json.JSONDecodeError, OSError):
        return DEFAULT_STATS.copy(), time.time(), False


def save_state(stats: Dict[str, float], sleeping: bool) -> None:
    payload = {
        "stats": stats,
        "last_timestamp": time.time(),
        "sleeping": sleeping,
    }
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STORAGE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
