# Grow a Plant

Dark, moody, firefly-lit idle planter built with Python + Tkinter. Watch a neon plant breathe, glow, and bloom as you check in each day.

**Creator / Dev:** tubakhxn

## Requirements
- Python 3.9+ (3.11 recommended)
- Tkinter (included with the official Windows/macOS installers; `sudo apt install python3-tk` on many Linux distros)

## Quick start
1. (Optional) Create and activate a virtual environment.
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install Tkinter if your Python build does not already include it.
3. Run the app from the project root:
   ```bash
   python main.py
   ```

## How the garden works
- Passive growth accrues automatically based on real-world time, even when the window is closed.
- Watering is limited to **one sip per 24 hours** and adds a gentle boost (`WATER_BONUS`).
- Growth stages (Seed → Sprout → Young Plant → Blooming) animate visually via the custom canvas scene.
- Stats (last watered timestamp, manual boosts, total growth) are stored in `plant_state.json` so progress survives restarts.

## Controls & UI
- **Water Plant** button: gives the daily sip. If the soil is damp you will see a friendly reminder showing the remaining wait time.
- **Progress bar**: tracks cumulative growth points relative to the Blooming milestone.
- **Metric card**: breaks down passive vs. watering progress plus the daily limit reminder.
- **Animated scene**: gradients, breathing glow, and drifting fireflies keep the experience from feeling static.

## Project files
- `main.py` — full Tkinter application with animation loops and state storage.
- `plant_state.json` — auto-generated save file; delete it if you ever want a fresh start.
- `README.md` — you are reading it!

Enjoy the calm vibes, keep the plant hydrated, and check in tomorrow for more glow. 🌱
