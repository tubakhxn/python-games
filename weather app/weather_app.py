"""Bold Tkinter weather dashboard with layered visuals and preview mode."""

from __future__ import annotations

import base64
import copy
import os
import random
import threading
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

import requests


class WeatherClientError(Exception):
    """Custom error type for user-facing weather issues."""


class WeatherApp:
    """Encapsulates the Tkinter UI and weather fetching logic."""

    ROOT_BG = "#081027"
    PANEL_BG = "#101a3f"
    PANEL_DARK = "#0c1433"
    PANEL_LIGHT = "#1a2854"
    BORDER_COLOR = "#1f2d5c"
    ACCENT_PRIMARY = "#9b5cf5"
    ACCENT_SECONDARY = "#4fa5ff"
    TEXT_PRIMARY = "#f8fafc"
    TEXT_MUTED = "#98a3d8"
    CHIP_BG = "#ffffff"
    SKY_TOP = "#6235ff"
    SKY_BOTTOM = "#182461"
    SUN_COLOR = "#ffd884"
    CLOUD_COLOR = "#f3f6ff"
    HERO_WIDTH = 520
    HERO_HEIGHT = 240

    HERO_CHIPS = ["Feels Like", "Wind", "Humidity"]
    DETAIL_FIELDS = ["Pressure", "Visibility", "UV", "Air Quality"]

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENWEATHER_API_KEY")
        self.root = tk.Tk()
        self.root.title("Nebula Weather")
        self.root.geometry("890x660")
        self.root.configure(bg=self.ROOT_BG)
        self.root.resizable(False, False)
        self._prepare_window_alpha()

        self.city_var = tk.StringVar(value="Lisbon")
        self.status_var = tk.StringVar(value="Preview mode · sample data active")

        self.icon_image: Optional[tk.PhotoImage] = None
        self.hero_icon_image: Optional[tk.PhotoImage] = None
        self.sky_canvas: Optional[tk.Canvas] = None
        self.hero_temp_item: Optional[int] = None
        self.hero_location_item: Optional[int] = None
        self.hero_condition_item: Optional[int] = None
        self.hero_icon_symbol_item: Optional[int] = None
        self.hero_icon_image_item: Optional[int] = None
        self.hero_chip_items: List[Dict[str, int]] = []
        self.clouds: List[Dict[str, object]] = []
        self.detail_labels: Dict[str, tk.Label] = {}
        self.hourly_cards: List[Dict[str, tk.Label]] = []
        self.weekly_cards: List[Dict[str, tk.Label]] = []
        self.preview_profiles = self._build_dummy_profiles()
        self.sample_index = 0

        self._build_styles()
        self._build_ui()
        self.root.after(250, self._start_cloud_animation)
        self.root.after(150, self._fade_window_in)

        # Boot with the first sample profile so the UI never feels empty.
        self._apply_weather(self._sample_weather(self.city_var.get()), None)

    def _build_dummy_profiles(self) -> List[Dict[str, object]]:
        """Curate a handful of designer-friendly weather snapshots."""
        return [
            {
                "location": "Lisbon, PT",
                "temperature": "24°C",
                "description": "Hazy Sunshine",
                "icon": "01d",
                "chips": {"Feels Like": "26°C", "Wind": "12 km/h", "Humidity": "58%"},
                "details": {
                    "Pressure": "1018 hPa",
                    "Visibility": "10 km",
                    "UV": "Moderate",
                    "Air Quality": "42 AQI",
                },
                "hourly": [
                    {"time": "09:00", "temp": "22°", "icon": "01d"},
                    {"time": "12:00", "temp": "25°", "icon": "02d"},
                    {"time": "15:00", "temp": "27°", "icon": "02d"},
                    {"time": "18:00", "temp": "23°", "icon": "03d"},
                    {"time": "21:00", "temp": "20°", "icon": "03n"},
                    {"time": "00:00", "temp": "18°", "icon": "04n"},
                ],
                "weekly": [
                    {"day": "Mon", "status": "☀️", "high": "28°", "low": "18°"},
                    {"day": "Tue", "status": "⛅", "high": "26°", "low": "17°"},
                    {"day": "Wed", "status": "🌦", "high": "24°", "low": "16°"},
                    {"day": "Thu", "status": "🌤", "high": "25°", "low": "15°"},
                    {"day": "Fri", "status": "☀️", "high": "27°", "low": "18°"},
                ],
            },
            {
                "location": "Kyoto, JP",
                "temperature": "19°C",
                "description": "Gentle Rain",
                "icon": "10d",
                "chips": {"Feels Like": "18°C", "Wind": "8 km/h", "Humidity": "72%"},
                "details": {
                    "Pressure": "1009 hPa",
                    "Visibility": "7 km",
                    "UV": "Low",
                    "Air Quality": "55 AQI",
                },
                "hourly": [
                    {"time": "08:00", "temp": "17°", "icon": "10d"},
                    {"time": "11:00", "temp": "18°", "icon": "10d"},
                    {"time": "14:00", "temp": "19°", "icon": "10d"},
                    {"time": "17:00", "temp": "18°", "icon": "04d"},
                    {"time": "20:00", "temp": "17°", "icon": "10n"},
                    {"time": "23:00", "temp": "16°", "icon": "10n"},
                ],
                "weekly": [
                    {"day": "Sat", "status": "🌧", "high": "20°", "low": "15°"},
                    {"day": "Sun", "status": "🌦", "high": "22°", "low": "16°"},
                    {"day": "Mon", "status": "☁️", "high": "21°", "low": "15°"},
                    {"day": "Tue", "status": "🌤", "high": "24°", "low": "17°"},
                    {"day": "Wed", "status": "☀️", "high": "26°", "low": "18°"},
                ],
            },
        ]

    def _prepare_window_alpha(self) -> None:
        try:
            self.root.attributes("-alpha", 0.0)
        except tk.TclError:
            pass

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=10,
            background=self.ACCENT_PRIMARY,
            foreground="#ffffff",
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_SECONDARY), ("disabled", "#4c4c6b")],
        )
        style.configure(
            "Search.TEntry",
            fieldbackground=self.PANEL_LIGHT,
            foreground=self.TEXT_PRIMARY,
            insertcolor=self.TEXT_PRIMARY,
            padding=6,
        )

    def _build_ui(self) -> None:
        wrapper = tk.Frame(self.root, bg=self.ROOT_BG)
        wrapper.pack(fill="both", expand=True, padx=22, pady=22)

        # Top bar with title and search controls
        top_bar = tk.Frame(wrapper, bg=self.ROOT_BG)
        top_bar.pack(fill="x", pady=(0, 18))

        title = tk.Label(
            top_bar,
            text="Nebula Weather",
            font=("Segoe UI Semibold", 22),
            fg=self.TEXT_PRIMARY,
            bg=self.ROOT_BG,
        )
        title.pack(side="left")

        control_box = tk.Frame(top_bar, bg=self.ROOT_BG)
        control_box.pack(side="right")

        entry = ttk.Entry(control_box, textvariable=self.city_var, width=24, style="Search.TEntry")
        entry.pack(side="left")
        entry.bind("<Return>", self.fetch_weather)

        self.fetch_button = ttk.Button(control_box, text="Refresh", style="Accent.TButton", command=self.fetch_weather)
        self.fetch_button.pack(side="left", padx=(10, 0))

        self.mode_badge = tk.Label(
            control_box,
            text="Preview",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.ACCENT_PRIMARY,
            padx=10,
            pady=4,
        )
        self.mode_badge.pack(side="left", padx=(10, 0))

        content = tk.Frame(wrapper, bg=self.ROOT_BG)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        hero_container = tk.Frame(content, bg=self.PANEL_BG, bd=0)
        hero_container.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 14))
        hero_container.grid_propagate(False)

        self.sky_canvas = tk.Canvas(
            hero_container,
            width=self.HERO_WIDTH,
            height=self.HERO_HEIGHT,
            bd=0,
            highlightthickness=0,
        )
        self.sky_canvas.pack(fill="both", expand=True)
        self._paint_sky_gradient()
        self._add_hero_content()
        self._create_clouds()

        detail_frame = tk.Frame(
            content,
            bg=self.PANEL_BG,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            padx=18,
            pady=18,
        )
        detail_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 14))

        detail_header = tk.Label(
            detail_frame,
            text="Atmosphere",
            font=("Segoe UI Semibold", 16),
            fg=self.TEXT_PRIMARY,
            bg=self.PANEL_BG,
        )
        detail_header.pack(anchor="w")
        detail_sub = tk.Label(
            detail_frame,
            text="Live stats snapshot",
            font=("Segoe UI", 11),
            fg=self.TEXT_MUTED,
            bg=self.PANEL_BG,
        )
        detail_sub.pack(anchor="w", pady=(0, 14))

        for field in self.DETAIL_FIELDS:
            row = tk.Frame(detail_frame, bg=self.PANEL_BG)
            row.pack(fill="x", pady=6)
            label = tk.Label(row, text=field, font=("Segoe UI", 11), fg=self.TEXT_MUTED, bg=self.PANEL_BG)
            label.pack(side="left")
            value = tk.Label(row, text="--", font=("Segoe UI", 12, "bold"), fg=self.TEXT_PRIMARY, bg=self.PANEL_BG)
            value.pack(side="right")
            self.detail_labels[field] = value

        hourly_frame = tk.Frame(
            content,
            bg=self.PANEL_DARK,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            padx=18,
            pady=18,
        )
        hourly_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 16), pady=(0, 0))

        hourly_title = tk.Label(
            hourly_frame,
            text="Next hours",
            font=("Segoe UI Semibold", 14),
            fg=self.TEXT_PRIMARY,
            bg=self.PANEL_DARK,
        )
        hourly_title.pack(anchor="w")

        hourly_row = tk.Frame(hourly_frame, bg=self.PANEL_DARK)
        hourly_row.pack(fill="x", pady=(12, 0))

        for _ in range(6):
            card = tk.Frame(
                hourly_row,
                bg=self.PANEL_LIGHT,
                padx=10,
                pady=10,
                highlightbackground=self.BORDER_COLOR,
                highlightthickness=1,
            )
            card.pack(side="left", expand=True, fill="both", padx=4)
            time_label = tk.Label(card, text="--", font=("Segoe UI", 10), fg=self.TEXT_MUTED, bg=self.PANEL_LIGHT)
            time_label.pack(anchor="w")
            icon_label = tk.Label(card, text="☀️", font=("Segoe UI", 18), fg=self.TEXT_PRIMARY, bg=self.PANEL_LIGHT)
            icon_label.pack(anchor="center", pady=(4, 4))
            temp_label = tk.Label(card, text="--", font=("Segoe UI Semibold", 13), fg=self.TEXT_PRIMARY, bg=self.PANEL_LIGHT)
            temp_label.pack(anchor="center")
            self.hourly_cards.append({"time": time_label, "icon": icon_label, "temp": temp_label})

        weekly_frame = tk.Frame(
            content,
            bg=self.PANEL_DARK,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            padx=18,
            pady=18,
        )
        weekly_frame.grid(row=1, column=1, sticky="nsew")

        weekly_title = tk.Label(
            weekly_frame,
            text="Week glance",
            font=("Segoe UI Semibold", 14),
            fg=self.TEXT_PRIMARY,
            bg=self.PANEL_DARK,
        )
        weekly_title.pack(anchor="w")

        for _ in range(5):
            row = tk.Frame(weekly_frame, bg=self.PANEL_DARK)
            row.pack(fill="x", pady=6)
            day_label = tk.Label(row, text="--", font=("Segoe UI", 11), fg=self.TEXT_MUTED, bg=self.PANEL_DARK)
            day_label.pack(side="left")
            icon_label = tk.Label(row, text="☁️", font=("Segoe UI", 12), fg=self.TEXT_PRIMARY, bg=self.PANEL_DARK)
            icon_label.pack(side="left", padx=10)
            temp_label = tk.Label(row, text="--", font=("Segoe UI", 11), fg=self.TEXT_PRIMARY, bg=self.PANEL_DARK)
            temp_label.pack(side="right")
            self.weekly_cards.append({"day": day_label, "icon": icon_label, "temp": temp_label})

        status_bar = tk.Label(
            wrapper,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg=self.TEXT_MUTED,
            bg=self.ROOT_BG,
        )
        status_bar.pack(anchor="w", pady=(12, 0))

    def _paint_sky_gradient(self) -> None:
        if not self.sky_canvas:
            return
        self.sky_canvas.delete("sky")
        steps = 60
        for index in range(steps):
            ratio = index / (steps - 1)
            color = self._interpolate_color(self.SKY_TOP, self.SKY_BOTTOM, ratio)
            y0 = (self.HERO_HEIGHT / steps) * index
            self.sky_canvas.create_rectangle(
                0,
                y0,
                self.HERO_WIDTH,
                y0 + (self.HERO_HEIGHT / steps) + 2,
                outline="",
                fill=color,
                tags="sky",
            )
        self.sky_canvas.create_oval(
            self.HERO_WIDTH - 160,
            10,
            self.HERO_WIDTH - 30,
            140,
            fill=self.SUN_COLOR,
            outline="",
            tags="sky",
        )

    def _add_hero_content(self) -> None:
        if not self.sky_canvas:
            return
        self.hero_temp_item = self.sky_canvas.create_text(
            110,
            130,
            text="--",
            font=("Segoe UI", 56, "bold"),
            fill=self.TEXT_PRIMARY,
            anchor="w",
        )
        self.hero_location_item = self.sky_canvas.create_text(
            40,
            60,
            text="--",
            font=("Segoe UI Semibold", 20),
            fill=self.TEXT_PRIMARY,
            anchor="w",
        )
        self.hero_condition_item = self.sky_canvas.create_text(
            40,
            95,
            text="--",
            font=("Segoe UI", 14),
            fill=self.TEXT_MUTED,
            anchor="w",
        )

        self.hero_icon_symbol_item = self.sky_canvas.create_text(
            self.HERO_WIDTH - 110,
            110,
            text="☀️",
            font=("Segoe UI", 58),
            fill="#fff",
        )
        self.hero_icon_image_item = self.sky_canvas.create_image(
            self.HERO_WIDTH - 110,
            110,
            image="",
        )

        chip_x = [90, 255, 420]
        for index, label in enumerate(self.HERO_CHIPS):
            center = chip_x[index]
            rect = self.sky_canvas.create_rectangle(
                center - 80,
                170,
                center + 70,
                215,
                fill=self.CHIP_BG,
                outline="",
                tags="chip",
            )
            self.sky_canvas.itemconfig(rect, stipple="gray50")
            label_id = self.sky_canvas.create_text(
                center - 60,
                178,
                text=label,
                font=("Segoe UI", 10),
                fill=self.TEXT_MUTED,
                anchor="w",
            )
            value_id = self.sky_canvas.create_text(
                center - 60,
                200,
                text="--",
                font=("Segoe UI", 14, "bold"),
                fill=self.TEXT_PRIMARY,
                anchor="w",
            )
            self.hero_chip_items.append({"label": label_id, "value": value_id})

    def _create_clouds(self) -> None:
        if not self.sky_canvas:
            return
        self.clouds.clear()
        specs = [
            {"x": -140, "y": 150, "scale": 1.3, "speed": 0.4},
            {"x": 30, "y": 80, "scale": 0.9, "speed": 0.7},
            {"x": 220, "y": 140, "scale": 1.1, "speed": 0.5},
        ]
        for spec in specs:
            parts = self._draw_cloud(spec["x"], spec["y"], spec["scale"])
            self.clouds.append({"parts": parts, "speed": spec["speed"]})

    def _draw_cloud(self, x: float, y: float, scale: float) -> List[int]:
        if not self.sky_canvas:
            return []
        blobs = [
            (0, 0, 90, 40),
            (25, -18, 120, 35),
            (70, 6, 155, 48),
        ]
        ids: List[int] = []
        for left, top, right, bottom in blobs:
            ids.append(
                self.sky_canvas.create_oval(
                    x + left * scale,
                    y + top * scale,
                    x + right * scale,
                    y + bottom * scale,
                    fill=self.CLOUD_COLOR,
                    outline="",
                    tags="cloud",
                )
            )
        return ids

    def _start_cloud_animation(self) -> None:
        if not self.sky_canvas or not self.clouds:
            self.root.after(180, self._start_cloud_animation)
            return
        width = self.sky_canvas.winfo_width() or self.HERO_WIDTH
        for cloud in self.clouds:
            parts = cloud.get("parts", [])
            speed = cloud.get("speed", 0.5)
            for part in parts:
                self.sky_canvas.move(part, speed, 0)
            if parts:
                bbox = self.sky_canvas.bbox(*parts)
                if bbox and bbox[0] > width + 60:
                    shift = -(bbox[2] + 60)
                    for part in parts:
                        self.sky_canvas.move(part, shift, 0)
        self.root.after(60, self._start_cloud_animation)

    def _interpolate_color(self, start_hex: str, end_hex: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        start_rgb = self._hex_to_rgb(start_hex)
        end_rgb = self._hex_to_rgb(end_hex)
        blended = tuple(int(s + (e - s) * ratio) for s, e in zip(start_rgb, end_rgb))
        return self._rgb_to_hex(blended)

    @staticmethod
    def _hex_to_rgb(value: str) -> Tuple[int, int, int]:
        value = value.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    @staticmethod
    def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        return "#" + "".join(f"{component:02x}" for component in rgb)

    def _fade_window_in(self, step: float = 0.0) -> None:
        try:
            alpha = min(step, 1.0)
            self.root.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.root.after(30, self._fade_window_in, alpha + 0.05)
        except tk.TclError:
            pass

    def fetch_weather(self, event: Optional[tk.Event] = None) -> None:
        city = self.city_var.get().strip()
        if not city:
            self._show_error("Please enter a city name.")
            return
        self._set_loading_state(True)
        if not self.api_key:
            preview_weather = self._sample_weather(city)
            self.root.after(350, lambda: self._apply_weather(preview_weather, None))
            return
        worker = threading.Thread(target=self._retrieve_weather, args=(city,), daemon=True)
        worker.start()

    def _set_loading_state(self, loading: bool) -> None:
        text = "Fetching..." if loading else "Refresh"
        self.fetch_button.config(text=text, state="disabled" if loading else "normal")
        if loading:
            self.status_var.set("Updating panels...")

    def _retrieve_weather(self, city: str) -> None:
        try:
            weather = self._call_weather_api(city)
            icon_data = self._download_icon(weather.get("icon", ""))
        except WeatherClientError as exc:
            self.root.after(0, lambda: self._show_error(str(exc)))
        else:
            self.root.after(0, lambda: self._apply_weather(weather, icon_data))

    def _call_weather_api(self, city: str) -> Dict[str, object]:
        endpoint = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        try:
            response = requests.get(endpoint, params=params, timeout=8)
        except requests.RequestException as exc:
            raise WeatherClientError("Unable to reach the weather service.") from exc
        if response.status_code == 404:
            raise WeatherClientError("City not found. Try another search.")
        if response.status_code != 200:
            raise WeatherClientError("Weather service error. Please try later.")
        payload = response.json()
        return self._normalize_live_payload(payload)

    def _download_icon(self, icon_code: str) -> Optional[str]:
        if not icon_code:
            return None
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            response = requests.get(icon_url, timeout=8)
            response.raise_for_status()
        except requests.RequestException:
            return None
        return base64.b64encode(response.content).decode("ascii")

    def _sample_weather(self, city: str) -> Dict[str, object]:
        profile = copy.deepcopy(self.preview_profiles[self.sample_index % len(self.preview_profiles)])
        self.sample_index += 1
        if city:
            parts = profile["location"].split(",")
            suffix = parts[1].strip() if len(parts) > 1 else ""
            profile["location"] = f"{city.title()}, {suffix}" if suffix else city.title()
        # add light randomness so each refresh feels alive
        delta = random.randint(-2, 2)
        profile["temperature"] = f"{int(profile['temperature'].rstrip('°C')) + delta}°C"
        return profile

    def _normalize_live_payload(self, payload: Dict[str, object]) -> Dict[str, object]:
        main = payload["main"]
        sys_data = payload.get("sys", {})
        wind = payload.get("wind", {})
        weather = payload["weather"][0]
        temp = round(main.get("temp", 0))
        return {
            "location": f"{payload['name']}, {sys_data.get('country', '')}",
            "temperature": f"{temp}°C",
            "description": weather.get("description", "").title(),
            "icon": weather.get("icon", ""),
            "chips": {
                "Feels Like": f"{round(main.get('feels_like', temp))}°C",
                "Wind": f"{round(wind.get('speed', 0))} km/h",
                "Humidity": f"{int(main.get('humidity', 0))}%",
            },
            "details": {
                "Pressure": f"{int(main.get('pressure', 0))} hPa",
                "Visibility": f"{int(payload.get('visibility', 0)) / 1000:.1f} km",
                "UV": "Check app",
                "Air Quality": "N/A",
            },
            "hourly": self._generate_hourly_stub(temp),
            "weekly": self._generate_weekly_stub(temp),
        }

    def _generate_hourly_stub(self, temp: int) -> List[Dict[str, str]]:
        labels = ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00"]
        data = []
        for index, label in enumerate(labels):
            delta = (-2, 3, 4, 0, -3, -4)[index]
            data.append({"time": label, "temp": f"{temp + delta}°", "icon": "01d"})
        return data

    def _generate_weekly_stub(self, temp: int) -> List[Dict[str, str]]:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        emojis = ["☀️", "⛅", "🌦", "☁️", "☀️"]
        data = []
        for idx, day in enumerate(days):
            data.append({"day": day, "status": emojis[idx], "high": f"{temp + idx}°", "low": f"{temp - 4 + idx}°"})
        return data

    def _apply_weather(self, weather: Dict[str, object], icon_data: Optional[str]) -> None:
        self._set_loading_state(False)
        self._update_hero_card(weather, icon_data)
        self._update_detail_panel(weather)
        self._update_hourly_panel(weather)
        self._update_weekly_panel(weather)

        mode_text = "Live" if self.api_key else "Preview"
        self.mode_badge.config(text=mode_text)
        self.status_var.set("Updated from sample set." if not self.api_key else "Live data refreshed.")

    def _update_hero_card(self, weather: Dict[str, object], icon_data: Optional[str]) -> None:
        if not self.sky_canvas:
            return
        self.sky_canvas.itemconfigure(self.hero_location_item, text=str(weather.get("location", "--")))
        self.sky_canvas.itemconfigure(self.hero_temp_item, text=str(weather.get("temperature", "--")))
        self.sky_canvas.itemconfigure(self.hero_condition_item, text=str(weather.get("description", "--")))

        chips: Dict[str, str] = weather.get("chips", {})  # type: ignore[assignment]
        for index, label in enumerate(self.HERO_CHIPS):
            value = chips.get(label, "--") if isinstance(chips, dict) else "--"
            self.sky_canvas.itemconfigure(self.hero_chip_items[index]["value"], text=value)

        if icon_data:
            self.hero_icon_image = tk.PhotoImage(data=icon_data)
            self.sky_canvas.itemconfigure(self.hero_icon_image_item, image=self.hero_icon_image)
            self.sky_canvas.itemconfigure(self.hero_icon_symbol_item, text="")
        else:
            self.sky_canvas.itemconfigure(self.hero_icon_image_item, image="")
            self.sky_canvas.itemconfigure(self.hero_icon_symbol_item, text="☀️")

    def _update_detail_panel(self, weather: Dict[str, object]) -> None:
        details: Dict[str, str] = weather.get("details", {})  # type: ignore[assignment]
        for field, label in self.detail_labels.items():
            label.config(text=details.get(field, "--"))

    def _update_hourly_panel(self, weather: Dict[str, object]) -> None:
        hourly: List[Dict[str, str]] = weather.get("hourly", [])  # type: ignore[assignment]
        for card, data in zip(self.hourly_cards, hourly):
            card["time"].config(text=data.get("time", "--"))
            card["icon"].config(text=self._icon_to_emoji(data.get("icon", "")))
            card["temp"].config(text=data.get("temp", "--"))

    def _update_weekly_panel(self, weather: Dict[str, object]) -> None:
        weekly: List[Dict[str, str]] = weather.get("weekly", [])  # type: ignore[assignment]
        for card, data in zip(self.weekly_cards, weekly):
            card["day"].config(text=data.get("day", "--"))
            card["icon"].config(text=data.get("status", "☁️"))
            card["temp"].config(text=f"{data.get('high', '--')}/{data.get('low', '--')}")

    def _icon_to_emoji(self, icon_code: str) -> str:
        mapping = {
            "01": "☀️",
            "02": "🌤",
            "03": "☁️",
            "04": "☁️",
            "09": "🌧",
            "10": "🌦",
            "11": "⛈",
            "13": "❄️",
            "50": "🌫",
        }
        return mapping.get(icon_code[:2], "☁️")

    def _show_error(self, message: str) -> None:
        self._set_loading_state(False)
        self.status_var.set(message)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = WeatherApp()
    app.run()


if __name__ == "__main__":
    main()
