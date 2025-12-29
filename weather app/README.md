# Gentle Weather Desktop App

Crafted by **tubakhxn**. Nebula-inspired Tkinter dashboard with ambient gradients, layered clouds, and instant preview data.

## Features
- Bold gradient UI with animated hero clouds and multi-panel dashboard.
- Preview mode ships with curated dummy weather so the app looks polished immediately.
- Optional OpenWeather integration for live temperature, condition, and icon data.
- Responsive threaded fetches plus graceful handling of network/API issues.

## Requirements
- Python 3.9+
- An OpenWeather API key (free tier works).

Install dependencies:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure your API key (optional)
The dashboard boots in **Preview** mode using designer-friendly dummy data. To flip into live mode add an API key from https://openweathermap.org/: 
```
setx OPENWEATHER_API_KEY "YOUR_KEY"
```
Restart VS Code/PowerShell so the environment variable loads, then relaunch the app. If the key is omitted or blank the UI simply stays in preview.

## Run the app
```
python weather_app.py
```
Type any city name and press Enter or click **Refresh**. Without an API key the app cycles curated preview data so screenshots look premium out of the box.

## Forking / contributions
1. **Fork** the repository on GitHub.
2. Clone your fork and add the original repo as `upstream` if you plan to sync changes.
3. Create a fresh branch (e.g., `feature/theme-toggle`).
4. Make edits, run `python -m py_compile weather_app.py` (or your preferred tests), and push the branch.
5. Open a Pull Request against the main repo describing the change, screenshots encouraged.
6. Mention whether you used preview mode or live API data so reviewers can replicate your setup.

## Troubleshooting
- **City not found**: Double-check spelling or include the country code (e.g., `Paris,FR`).
- **API key message**: Ensure `OPENWEATHER_API_KEY` is set and reopen your terminal.
- **No internet**: The app reports when it cannot reach the weather service; try again once online.
