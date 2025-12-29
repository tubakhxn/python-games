from __future__ import annotations

from typing import Iterable, List, Optional

from .metadata import AudioTrack, load_track_metadata


class PlaylistManager:
    """In-memory playlist model with navigation helpers."""

    def __init__(self) -> None:
        self._tracks: List[AudioTrack] = []
        self._current_index: int = -1

    # Public API -----------------------------------------------------------
    def tracks(self) -> List[AudioTrack]:
        return list(self._tracks)

    def current_track(self) -> Optional[AudioTrack]:
        if 0 <= self._current_index < len(self._tracks):
            return self._tracks[self._current_index]
        return None

    def add_paths(self, paths: Iterable[str]) -> List[AudioTrack]:
        added: List[AudioTrack] = []
        for path in paths:
            track = load_track_metadata(path)
            if track:
                self._tracks.append(track)
                added.append(track)
        if self._tracks and self._current_index == -1:
            self._current_index = 0
        return added

    def remove_index(self, index: int) -> Optional[AudioTrack]:
        if 0 <= index < len(self._tracks):
            removed = self._tracks.pop(index)
            if not self._tracks:
                self._current_index = -1
            else:
                if self._current_index >= index:
                    self._current_index -= 1
                self._current_index = max(0, min(self._current_index, len(self._tracks) - 1))
            return removed
        return None

    def set_current_index(self, index: int) -> Optional[AudioTrack]:
        if 0 <= index < len(self._tracks):
            self._current_index = index
            return self._tracks[index]
        return None

    def next_track(self) -> Optional[AudioTrack]:
        if not self._tracks:
            return None
        self._current_index = (self._current_index + 1) % len(self._tracks)
        return self._tracks[self._current_index]

    def previous_track(self) -> Optional[AudioTrack]:
        if not self._tracks:
            return None
        self._current_index = (self._current_index - 1) % len(self._tracks)
        return self._tracks[self._current_index]

    def index_of(self, track: AudioTrack) -> int:
        try:
            return self._tracks.index(track)
        except ValueError:
            return -1

    def has_tracks(self) -> bool:
        return bool(self._tracks)
