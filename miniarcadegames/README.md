# Mini Arcade App

A compact pygame-powered arcade that bundles three lightweight games behind a shared menu and smooth scene transitions.

> Creator & Developer: **tubakhxn**

## Included games
- **Snake** – Classic grid eater with quick turns.
- **Pong** – Solo rally against an adaptive paddle.
- **Dodge** – Avoid the falling blocks for as long as possible.

## Requirements
- Python 3.11+ (works with any modern CPython 3.x build)
- `pygame` (installed via `requirements.txt`)

## Setup
1. *(Optional but recommended)* Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the arcade
Run the package entry point from the project root:
```bash
python -m arcade.main
```

## Controls
| Game  | Controls |
| --- | --- |
| Snake | Arrow keys to turn, Enter to restart after crashing, Esc/Backspace to leave |
| Pong | W/S or Arrow keys move the paddle, Enter serves the ball, Esc/Backspace exits |
| Dodge | WASD or Arrow keys to move, Enter restarts after a hit, Esc/Backspace exits |

## Project structure
```
Mini Arcade App/
├─ arcade/
│  ├─ main.py
│  ├─ settings.py
│  └─ games/
│     ├─ base_game.py
│     ├─ snake.py
│     ├─ pong.py
│     └─ dodge.py
├─ requirements.txt
└─ README.md
```

Feel free to extend the `arcade/games` package with additional mini games—each game simply needs to subclass `BaseGame` and expose the expected `handle_events`, `update`, and `draw` methods.

## Credits
- Concept, code, and design by **tubakhxn**

## Forking instructions
1. Open the repository page in your browser and click **Fork**.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mini-arcade-app.git
   cd mini-arcade-app
   ```
3. Add the original repository as an upstream remote to pull in future updates:
   ```bash
   git remote add upstream https://github.com/<original-owner>/mini-arcade-app.git
   ```
4. Create a new branch for your feature or fix, make changes, and push to your fork before opening a pull request.
