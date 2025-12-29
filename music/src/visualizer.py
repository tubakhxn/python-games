from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class AudioVisualizer(QWidget):
    """Matplotlib-based bar visualizer embedded into a QWidget."""

    def __init__(self, bars: int = 32, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bars = bars
        self._figure = Figure(figsize=(5, 2.5), facecolor="none")
        self._canvas = FigureCanvas(self._figure)
        self._ax = self._figure.add_subplot(111)
        self._ax.set_facecolor("#030712")
        self._ax.set_xticks([])
        self._ax.set_yticks([])
        self._ax.set_ylim(0, 1)
        self._ax.set_xlim(-0.5, self._bars - 0.5)
        self._ax.spines["bottom"].set_color("#1f2937")
        self._ax.spines["top"].set_color("#1f2937")
        self._ax.spines["left"].set_color("#1f2937")
        self._ax.spines["right"].set_color("#1f2937")
        initial_data = np.zeros(self._bars)
        self._rects = self._ax.bar(range(self._bars), initial_data, color="#38bdf8", width=0.8)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)
        self.setLayout(layout)

        self._decay = np.zeros(self._bars)
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._decay_step)
        self._timer.start()

    # Public API -----------------------------------------------------------
    def push_spectrum(self, magnitudes: np.ndarray) -> None:
        if magnitudes.size == 0:
            return
        grouped = np.interp(
            np.linspace(0, magnitudes.size - 1, self._bars),
            np.arange(magnitudes.size),
            magnitudes,
        )
        normalized = grouped / (grouped.max() or 1)
        normalized = np.clip(normalized, 0, 1)
        self._decay = normalized
        for rect, height in zip(self._rects, normalized):
            rect.set_height(height)
        self._ax.set_ylim(0, max(1.0, normalized.max() * 1.2))
        self._canvas.draw_idle()

    # Internal -------------------------------------------------------------
    def _decay_step(self) -> None:
        if not np.any(self._decay):
            return
        self._decay *= 0.92
        for rect, height in zip(self._rects, self._decay):
            rect.set_height(height)
        self._canvas.draw_idle()
