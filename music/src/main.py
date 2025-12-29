from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
from PyQt5.QtCore import (
    QEasingCurve,
    QCoreApplication,
    QPropertyAnimation,
    Qt,
    QUrl,
)
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import (
    QAudioBuffer,
    QAudioFormat,
    QAudioProbe,
    QMediaContent,
    QMediaPlayer,
)
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .metadata import AudioTrack
from .playlist import PlaylistManager
from .visualizer import AudioVisualizer

APP_NAME = "Aurora Music Player"
BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR.parent / "assets"
STYLE_SHEET = ASSET_DIR / "style.qss"
SUPPORTED_EXTENSIONS = ["*.mp3", "*.MP3", "*.wav", "*.WAV"]


class MusicPlayer(QMainWindow):
    """Main window hosting the music player UI and behavior."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1180, 720)

        self.playlist = PlaylistManager()
        self._slider_pressed = False

        self._build_player()
        self._wire_player()
        self._load_stylesheet()

        self.statusBar().showMessage("Add songs to begin listening.")

    # ------------------------------------------------------------------
    def _build_player(self) -> None:
        self.player = QMediaPlayer(self)
        self.player.setVolume(60)
        self.player.setNotifyInterval(100)

        self.audio_probe = QAudioProbe(self)
        self._probe_available = self.audio_probe.setSource(self.player)

        central = QWidget(self)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # Left pane with playlist controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        self.playlist_title = QLabel("Playlist")
        self.playlist_title.setFont(QFont("Segoe UI", 18, QFont.DemiBold))
        left_panel.addWidget(self.playlist_title)

        self.playlist_list = QListWidget()
        self.playlist_list.setSpacing(6)
        self.playlist_list.setFixedWidth(320)
        left_panel.addWidget(self.playlist_list, stretch=1)

        playlist_button_row = QHBoxLayout()
        self.add_button = QPushButton("Add Songs")
        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("secondary")
        playlist_button_row.addWidget(self.add_button)
        playlist_button_row.addWidget(self.remove_button)
        left_panel.addLayout(playlist_button_row)

        # Right pane hosts metadata, controls, and visualizer
        right_panel = QVBoxLayout()
        right_panel.setSpacing(18)

        self.metadata_shell = QFrame()
        shell_layout = QVBoxLayout(self.metadata_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)

        self.metadata_card = QFrame(self.metadata_shell)
        self.metadata_card.setObjectName("metadataCard")
        metadata_layout = QVBoxLayout(self.metadata_card)
        metadata_layout.setContentsMargins(24, 24, 24, 24)
        metadata_layout.setSpacing(8)

        self.track_title = QLabel("No track selected")
        self.track_title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        metadata_layout.addWidget(self.track_title)

        self.track_artist = QLabel("Artist")
        self.track_artist.setFont(QFont("Segoe UI", 16))
        metadata_layout.addWidget(self.track_artist)

        self.track_album = QLabel("Album")
        metadata_layout.addWidget(self.track_album)

        self.track_duration = QLabel("00:00")
        metadata_layout.addWidget(self.track_duration)

        opacity = QGraphicsOpacityEffect(self.metadata_card)
        self.metadata_card.setGraphicsEffect(opacity)
        self.metadata_anim = QPropertyAnimation(opacity, b"opacity", self)
        self.metadata_anim.setDuration(450)
        self.metadata_anim.setStartValue(0.0)
        self.metadata_anim.setEndValue(1.0)
        self.metadata_anim.setEasingCurve(QEasingCurve.InOutQuad)

        drop_shadow = QGraphicsDropShadowEffect(self.metadata_shell)
        drop_shadow.setBlurRadius(32)
        drop_shadow.setOffset(0, 12)
        drop_shadow.setColor(Qt.black)
        self.metadata_shell.setGraphicsEffect(drop_shadow)
        shell_layout.addWidget(self.metadata_card)

        right_panel.addWidget(self.metadata_shell)

        # Progress controls
        progress_layout = QVBoxLayout()
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.time_label = QLabel("00:00 / 00:00")
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.time_label)
        right_panel.addLayout(progress_layout)

        # Transport controls
        transport_layout = QHBoxLayout()
        transport_layout.setSpacing(12)
        self.prev_button = QToolButton()
        self.prev_button.setText("Prev")
        self.prev_button.setObjectName("secondary")
        self.play_button = QToolButton()
        self.play_button.setText("Play")
        self.stop_button = QToolButton()
        self.stop_button.setText("Stop")
        self.stop_button.setObjectName("secondary")
        self.next_button = QToolButton()
        self.next_button.setText("Next")
        self.next_button.setObjectName("secondary")
        for widget in (self.prev_button, self.play_button, self.stop_button, self.next_button):
            widget.setMinimumWidth(90)
        transport_layout.addWidget(self.prev_button)
        transport_layout.addWidget(self.play_button)
        transport_layout.addWidget(self.stop_button)
        transport_layout.addWidget(self.next_button)
        right_panel.addLayout(transport_layout)

        # Volume controls
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(12)
        volume_label = QLabel("Volume")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        right_panel.addLayout(volume_layout)

        # Visualizer section
        self.visualizer = AudioVisualizer(bars=48)
        viz_shadow = QGraphicsDropShadowEffect(self.visualizer)
        viz_shadow.setBlurRadius(24)
        viz_shadow.setOffset(0, 8)
        viz_shadow.setColor(Qt.black)
        self.visualizer.setGraphicsEffect(viz_shadow)
        right_panel.addWidget(self.visualizer, stretch=1)

        main_layout.addLayout(left_panel, stretch=0)
        main_layout.addLayout(right_panel, stretch=1)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar(self))

    def _wire_player(self) -> None:
        self.add_button.clicked.connect(self._add_tracks)
        self.remove_button.clicked.connect(self._remove_track)
        self.playlist_list.itemDoubleClicked.connect(self._play_from_double_click)
        self.playlist_list.currentRowChanged.connect(self._handle_selection_change)

        self.prev_button.clicked.connect(self._play_previous)
        self.next_button.clicked.connect(self._play_next)
        self.play_button.clicked.connect(self._toggle_play_pause)
        self.stop_button.clicked.connect(self._stop_playback)

        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.progress_slider.sliderPressed.connect(self._mark_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._mark_slider_released)
        self.progress_slider.sliderMoved.connect(self._preview_scrub)

        self.player.positionChanged.connect(self._sync_position)
        self.player.durationChanged.connect(self._sync_duration)
        self.player.stateChanged.connect(self._refresh_transport_labels)
        self.player.mediaStatusChanged.connect(self._handle_media_status)
        if hasattr(self.player, "errorOccurred"):
            self.player.errorOccurred.connect(self._handle_error)
        else:
            self.player.error.connect(self._handle_error)

        if self._probe_available:
            self.audio_probe.audioBufferProbed.connect(self._handle_buffer)
        else:
            self.statusBar().showMessage(
                "Audio visualizer unavailable on this device.",
                6000,
            )

    # Slots ---------------------------------------------------------------
    def _add_tracks(self) -> None:
        dialog_filter = "Audio Files (" + " ".join(SUPPORTED_EXTENSIONS) + ")"
        paths, _ = QFileDialog.getOpenFileNames(self, "Select audio files", str(Path.home()), dialog_filter)
        if not paths:
            return
        added_tracks = self.playlist.add_paths(paths)
        if not added_tracks:
            QMessageBox.information(self, APP_NAME, "No readable audio files were added.")
            return
        self._refresh_playlist_view()
        self.statusBar().showMessage(f"Added {len(added_tracks)} track(s).", 3000)
        if self.playlist.current_track() and self.player.mediaStatus() == QMediaPlayer.NoMedia:
            self._load_track(self.playlist.current_track(), autoplay=False)

    def _remove_track(self) -> None:
        row = self.playlist_list.currentRow()
        if row < 0:
            QMessageBox.information(self, APP_NAME, "Select a track to remove.")
            return
        removed = self.playlist.remove_index(row)
        if removed:
            self._refresh_playlist_view()
            self.statusBar().showMessage(f"Removed {removed.title}.", 3000)
            if not self.playlist.has_tracks():
                self.player.stop()
                self.player.setMedia(QMediaContent())
                self._update_metadata(None)

    def _play_from_double_click(self, item: QListWidgetItem) -> None:
        index = self.playlist_list.row(item)
        track = self.playlist.set_current_index(index)
        self._load_track(track, autoplay=True)

    def _handle_selection_change(self, index: int) -> None:
        track = self.playlist.set_current_index(index)
        if track:
            self._update_metadata(track)

    def _toggle_play_pause(self) -> None:
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            return
        if not self.playlist.has_tracks():
            QMessageBox.information(self, APP_NAME, "Add at least one track to start playback.")
            return
        current = self.playlist.current_track()
        if self.player.mediaStatus() == QMediaPlayer.NoMedia and current:
            self._load_track(current, autoplay=True)
            return
        self.player.play()

    def _stop_playback(self) -> None:
        self.player.stop()
        self.progress_slider.setValue(0)
        self._update_time_label(position=0)

    def _play_next(self) -> None:
        track = self.playlist.next_track()
        self._load_track(track, autoplay=True)

    def _play_previous(self) -> None:
        track = self.playlist.previous_track()
        self._load_track(track, autoplay=True)

    def _mark_slider_pressed(self) -> None:
        self._slider_pressed = True

    def _mark_slider_released(self) -> None:
        if self.player.duration() > 0:
            self.player.setPosition(self.progress_slider.value())
        self._slider_pressed = False

    def _preview_scrub(self, value: int) -> None:
        self._update_time_label(position=value)

    def _sync_position(self, position: int) -> None:
        if not self._slider_pressed:
            self.progress_slider.setValue(position)
        self._update_time_label(position=position)

    def _sync_duration(self, duration: int) -> None:
        self.progress_slider.setRange(0, duration)
        self._update_time_label(duration=duration)

    def _refresh_transport_labels(self) -> None:
        if self.player.state() == QMediaPlayer.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

    def _handle_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.EndOfMedia:
            self._play_next()

    def _handle_error(self, *args) -> None:
        error = args[0] if args else self.player.error()
        error_string = args[1] if len(args) > 1 else self.player.errorString()
        if error == QMediaPlayer.NoError:
            return
        message = error_string or self.player.errorString() or "Unknown error"
        QMessageBox.critical(self, APP_NAME, f"Playback error: {message}")

    def _handle_buffer(self, buffer: QAudioBuffer) -> None:
        magnitudes = self._buffer_to_magnitudes(buffer)
        if magnitudes.size:
            self.visualizer.push_spectrum(magnitudes)

    # Helpers -------------------------------------------------------------
    def _refresh_playlist_view(self) -> None:
        self.playlist_list.clear()
        for track in self.playlist.tracks():
            item = QListWidgetItem(track.display_text)
            self.playlist_list.addItem(item)
        current = self.playlist.current_track()
        if current:
            current_index = self.playlist.index_of(current)
            self.playlist_list.setCurrentRow(current_index)

    def _load_track(self, track: Optional[AudioTrack], autoplay: bool) -> None:
        if not track:
            return
        media = QMediaContent(QUrl.fromLocalFile(str(track.path)))
        self.player.setMedia(media)
        self._update_metadata(track)
        index = self.playlist.index_of(track)
        if index >= 0:
            self.playlist_list.setCurrentRow(index)
        if autoplay:
            self.player.play()
        else:
            self.player.pause()

    def _update_metadata(self, track: Optional[AudioTrack]) -> None:
        if track is None:
            self.track_title.setText("No track selected")
            self.track_artist.setText("Artist")
            self.track_album.setText("Album")
            self.track_duration.setText("00:00")
            return
        self.track_title.setText(track.title)
        self.track_artist.setText(track.artist or "Unknown artist")
        self.track_album.setText(track.album or "Unknown album")
        self.track_duration.setText(track.duration_label)
        self.metadata_anim.stop()
        self.metadata_anim.start()

    def _update_time_label(self, position: Optional[int] = None, duration: Optional[int] = None) -> None:
        pos = position if position is not None else self.player.position()
        dur = duration if duration is not None else self.player.duration()
        self.time_label.setText(f"{self._format_ms(pos)} / {self._format_ms(dur)}")

    @staticmethod
    def _format_ms(value: int) -> str:
        seconds = value // 1000
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _buffer_to_magnitudes(self, buffer: QAudioBuffer) -> np.ndarray:
        # Convert the raw PCM data captured via QAudioProbe into an FFT magnitude array.
        fmt: QAudioFormat = buffer.format()
        sample_type = fmt.sampleType()
        sample_size = fmt.sampleSize()
        channel_count = fmt.channelCount() or 1

        if sample_type == QAudioFormat.Float:
            dtype = np.float32
        elif sample_type == QAudioFormat.SignedInt:
            dtype = np.int16 if sample_size <= 16 else np.int32
        elif sample_type == QAudioFormat.UnSignedInt:
            dtype = np.uint16 if sample_size <= 16 else np.uint32
        else:
            return np.array([])

        raw = buffer.data()
        if isinstance(raw, (bytes, bytearray, memoryview)):
            array = np.frombuffer(raw, dtype=dtype)
        else:
            array = np.frombuffer(bytes(raw), dtype=dtype)

        if array.size == 0:
            return np.array([])

        if sample_type == QAudioFormat.UnSignedInt:
            array = array.astype(np.int32) - (np.iinfo(dtype).max // 2)
        else:
            array = array.astype(np.float32)

        frames = (array.size // channel_count) * channel_count
        array = array[:frames]
        if channel_count > 1:
            array = array.reshape(-1, channel_count).mean(axis=1)

        if not array.size:
            return np.array([])

        window = np.hanning(array.size)
        spectrum = np.fft.rfft(array * window)
        magnitudes = np.abs(spectrum)
        magnitudes = np.log1p(magnitudes)
        return magnitudes

    def _load_stylesheet(self) -> None:
        if STYLE_SHEET.exists():
            with STYLE_SHEET.open("r", encoding="utf-8") as handle:
                self.setStyleSheet(handle.read())


def main() -> None:
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
