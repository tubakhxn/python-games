# Aurora Music Player

Aurora Music Player is a modern, visually rich desktop music player built with PyQt5. It supports local MP3/WAV playback, animated audio visualizations powered by Matplotlib, and full playlist management.

## Features
- Sleek PyQt5 interface with layered gradients, shadows, and animated metadata transitions.
- Local MP3/WAV playback via Qt Multimedia with play, pause, stop, next, and previous controls.
- Volume control, seekable progress bar, and realtime time display.
- Playlist management: add or remove tracks at runtime and instantly reorder by interacting with the list.
- Metadata display (title, artist, album, and duration) sourced automatically from audio tags.
- Embedded Matplotlib-powered spectrum bars that react to the currently playing audio stream.
- Smooth UI touches: animated metadata card fades, glowing visualizer, and responsive button states.

## Project Structure
```
.
├── assets/
│   └── style.qss          # Centralized theme overrides
├── requirements.txt       # Python dependencies
├── README.md              # This document
└── src/
    ├── __init__.py
    ├── main.py            # Application entrypoint (PyQt window + wiring)
    ├── metadata.py        # Audio metadata helpers & dataclasses
    ├── playlist.py        # Playlist management logic
    └── visualizer.py      # Matplotlib-based spectrum widget
```

## Prerequisites
- Python 3.10+
- FFmpeg is **not** required because playback relies on Qt Multimedia.

## Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Running the Player
```bash
python -m src.main
```

## Usage Tips
- Click **Add Songs** to load `.mp3` or `.wav` files into the playlist.
- Double-click any track (or use the transport controls) to start playback.
- Drag the progress slider to seek; use the volume slider for precise gain changes.
- The animated spectrum bars respond to the live audio buffer via `QAudioProbe`.

## Creator
- Designed and developed by **tubakhxn**.

## Forking & Installing
1. Fork this repository to your GitHub account.
2. Clone your fork locally:
    ```bash
    git clone https://github.com/<your-username>/aurora-music-player.git
    cd aurora-music-player
    ```
3. Create and activate a virtual environment, then install dependencies:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    python -m pip install -r requirements.txt
    ```
4. Launch the application:
    ```bash
    python -m src.main
    ```

## License
This project is provided as-is for personal or educational use.
