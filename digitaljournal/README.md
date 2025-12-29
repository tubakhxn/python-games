# Digital Journal App

A mobile-inspired desktop journal built with Python and Tkinter. The latest version mirrors the dual-phone layout from the reference shot: a dark "My Notes" phone on the left with colorful cards, and a light mint writing phone on the right with tactile buttons and toolbar chips.

## Features
- Full-screen gradient canvas with two floating "phones" plus animated cloud blobs drifting in the background
- Left phone shows vibrant sticky-note cards for recent entries, quick filter chips, and nightly prompts/affirmations
- Right phone hosts the live editor with bold/italic formatting buttons, status readouts, and tactile primary buttons
- Entries still save as `entries/YYYY-MM-DD.txt`, so every date owns its own file and can be opened outside the app
- Word/character counter, unsaved-change indicator, and New Page/Today shortcuts keep the workflow tight

## Requirements
- Python 3.10+
- Tkinter (bundled with the default Python installers on Windows/macOS/Linux)

## Getting Started
1. Open a terminal in this project folder.
2. Activate the provided virtual environment or your own, then run:
   ```bash
   python main.py
   ```
3. The dual-phone scene will appear: click one of the left cards to load it, or hit **New page** on the right phone to begin a fresh entry.

## Developer & Credits
- Concept, design, and build: **tubakhxn**
- Tech stack: Python 3.11 + Tkinter, no external UI kits
- Assets: all UI drawn procedurally (gradients, clouds, cards)

## Tips
- Use the **Today** button to jump back to the current date.
- Tap any colored card on the dark phone to load that entry instantly into the editor.
- Highlight text inside the editor, then click **Bold** or **Italic** for quick emphasis.
- Files live in the `entries/` folder—use **Open folder** on either phone to browse them in your OS.
