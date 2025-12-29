from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from mutagen import File as MutagenFile


@dataclass
class AudioTrack:
    """Domain object representing a single audio track."""

    title: str
    artist: str
    album: str
    duration: float  # seconds
    path: Path

    @property
    def duration_label(self) -> str:
        minutes, seconds = divmod(int(self.duration), 60)
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def display_text(self) -> str:
        artist_text = self.artist or "Unknown Artist"
        return f"{self.title} - {artist_text}"


def _safe_tag(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        for entry in value:
            text = _safe_tag(entry)
            if text:
                return text
        return ""
    if hasattr(value, "text"):
        return _safe_tag(getattr(value, "text"))
    return str(value).strip()


def load_track_metadata(path: str | Path) -> Optional[AudioTrack]:
    """Load metadata for the provided file path using mutagen."""

    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return None

    title = resolved.stem
    artist = ""
    album = ""
    duration = 0.0

    try:
        meta = MutagenFile(resolved, easy=True)
        if meta is not None:
            duration = getattr(getattr(meta, "info", None), "length", 0.0) or 0.0
            tags = getattr(meta, "tags", {}) or {}
            title = _safe_tag(tags.get("title")) or title
            artist = _safe_tag(tags.get("artist"))
            album = _safe_tag(tags.get("album"))
    except Exception:
        # Fall back to filename-derived metadata if mutagen fails.
        duration = 0.0 if duration == 0.0 else duration

    return AudioTrack(
        title=title or resolved.stem,
        artist=artist,
        album=album,
        duration=duration,
        path=resolved,
    )
