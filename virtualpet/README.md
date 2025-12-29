# Mochi the Virtual Pet

A fully featured desktop virtual pet built with Python and Pygame. Mochi reacts to your actions, keeps track of needs over real time, and chats with lighthearted dialogue just like a modern companion app.

## Features

- Smooth Pygame UI with bouncing animations, particles, and day/night cycle
- Core stats (hunger, happiness, energy, cleanliness, health) that decay even while the app is closed
- Actions: Feed, Play, Sleep, Clean, and pet via mouse clicks
- Multiple moods and contextual speech bubbles
- Text chat input with keyword-aware responses
- Idle dialogues, screen bounce reactions, and optional synthesized sound effects
- Local persistence (JSON) storing stats, sleep state, and last play timestamp

## Getting Started

1. **Install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the game**
   ```bash
   python main.py
   ```

Mochi stores progress at `storage/pet_state.json`. Delete that file if you want to reset the pet.

## Controls

- Click the large buttons to feed, play, clean, or tuck Mochi into bed.
- Click directly on Mochi to pet them.
- Type in the bottom text box and press `Enter` to chat.
- Toggle sound using the switch near the top-left corner.
- Press `Esc` or close the window to exit (progress saves automatically).

## Creator

- Lead creator & developer: **tubakhxn**

## Forking & Installing

1. **Fork** this repository under your GitHub account.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mochi-pet.git
   cd mochi-pet
   ```
3. Follow the **Getting Started** steps above to create a virtual environment and install dependencies.
4. Run `python main.py` to launch Mochi from your forked copy.

Enjoy caring for Mochi! ❤️
