import json
import math
import random
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

STATE_FILE = Path(__file__).with_name("plant_state.json")
DAY_SECONDS = 24 * 60 * 60
WATER_BONUS = 0.8
DISPLAY_CAP = 6.0  # Used only for progress visuals.

COLORS = {
    "ink": "#050809",
    "panel": "#0f1619",
    "card": "#151f23",
    "outline": "#1f2c30",
    "canvas": "#0f1a1d",
    "deep": "#060b0d",
    "accent": "#7cf0c5",
    "accent_dim": "#59b897",
    "leaf": "#6de3a5",
    "leaf_dim": "#356d54",
    "text_primary": "#e5fff2",
    "text_muted": "#9fb6aa",
    "text_soft": "#6c7f76",
    "button": "#1f4035",
    "button_active": "#2d5c4a",
}

STAGES = [
    {
        "name": "Seed",
        "limit": 1.5,
        "description": "A tiny kernel gathers strength beneath the soil.",
    },
    {
        "name": "Sprout",
        "limit": 3.0,
        "description": "A slim sprout pierces the dark, chasing moonlit air.",
    },
    {
        "name": "Young Plant",
        "limit": 4.5,
        "description": "Confident leaves stretch outward, steady and sure.",
    },
    {
        "name": "Blooming",
        "limit": float("inf"),
        "description": "The plant gleams with petals and quiet resilience.",
    },
]


def mix(color_a: str, color_b: str, factor: float) -> str:
    """Blend two hex colors for subtle gradients."""
    factor = max(0.0, min(1.0, factor))
    a = tuple(int(color_a[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(color_b[i : i + 2], 16) for i in (1, 3, 5))
    blended = tuple(int(x + (y - x) * factor) for x, y in zip(a, b))
    return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"


def load_state():
    """Load plant data from disk or create a fresh record."""
    if STATE_FILE.exists():
        try:
            with STATE_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if {"start_time", "last_watered", "manual_growth"} <= data.keys():
                    return data
        except (OSError, ValueError):
            pass

    now = time.time()
    data = {"start_time": now, "last_watered": 0, "manual_growth": 0.0}
    save_state(data)
    return data


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def growth_points(state):
    """Blend passive time-based growth with gentle boosts from watering."""
    elapsed_days = (time.time() - state["start_time"]) / DAY_SECONDS
    passive_growth = max(0.0, elapsed_days * 0.6)
    return passive_growth + float(state.get("manual_growth", 0.0))


def pick_stage(points):
    for stage in STAGES:
        if points < stage["limit"]:
            return stage
    return STAGES[-1]


def format_timestamp(ts):
    if not ts:
        return "Never"
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%b %d, %Y at %I:%M %p")


class PlantScene:
    """Animated canvas that keeps the experience from feeling static."""

    def __init__(self, master):
        self.canvas = tk.Canvas(
            master,
            width=420,
            height=260,
            bg=COLORS["canvas"],
            highlightthickness=0,
        )
        self.canvas.pack(pady=(12, 20))
        self.base_y = 212
        self.center_x = 210
        self.breath_phase = 0.0
        self.fireflies = []
        self.leaf_pairs = []
        self._build_layers()

    def _build_layers(self):
        gradient_steps = 26
        for step in range(gradient_steps):
            ratio = step / gradient_steps
            color = mix(COLORS["canvas"], COLORS["deep"], ratio)
            y = (self.canvas.winfo_reqheight() / gradient_steps) * step
            self.canvas.create_rectangle(
                0,
                y,
                self.canvas.winfo_reqwidth(),
                y + (self.canvas.winfo_reqheight() / gradient_steps),
                fill=color,
                outline="",
            )

        self.glow = self.canvas.create_oval(0, 0, 0, 0, fill="#08251b", outline="")

        pot_top = self.base_y + 6
        self.canvas.create_polygon(
            self.center_x - 70,
            pot_top,
            self.center_x + 70,
            pot_top,
            self.center_x + 50,
            pot_top + 50,
            self.center_x - 50,
            pot_top + 50,
            fill="#1e282b",
            outline=COLORS["outline"],
        )
        self.canvas.create_rectangle(
            self.center_x - 70,
            pot_top - 18,
            self.center_x + 70,
            pot_top,
            fill="#232f33",
            outline="",
        )

        self.stem = self.canvas.create_line(
            self.center_x,
            self.base_y,
            self.center_x,
            self.base_y - 60,
            width=7,
            fill=COLORS["leaf"],
            capstyle="round",
        )

        for _ in range(3):
            left = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=COLORS["leaf"], outline="")
            right = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=COLORS["leaf"], outline="")
            self.leaf_pairs.append((left, right))

        self.flower = self.canvas.create_oval(0, 0, 0, 0, fill=COLORS["accent"], outline="", state="hidden")

        for _ in range(10):
            self._spawn_firefly()

    def _spawn_firefly(self):
        x = random.randint(40, 380)
        y = random.randint(40, 230)
        size = random.uniform(2.0, 4.0)
        color = random.choice([COLORS["accent"], COLORS["accent_dim"], "#4fd29b"])
        item = self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
        self.fireflies.append({"id": item, "speed": random.uniform(0.2, 0.7)})

    def render(self, stage_index: int, stage_ratio: float):
        stage_ratio = max(0.0, min(1.0, stage_ratio))
        height = 70 + stage_index * 20 + stage_ratio * 36
        self.canvas.coords(
            self.stem,
            self.center_x,
            self.base_y,
            self.center_x,
            self.base_y - height,
        )

        visible_pairs = min(stage_index, len(self.leaf_pairs))
        for idx, (left, right) in enumerate(self.leaf_pairs):
            y = self.base_y - (40 + idx * 32 + stage_ratio * 10)
            spread = 28 + idx * 12 + stage_ratio * 8
            sway = 6 * math.sin(self.breath_phase + idx)

            left_coords = [
                self.center_x,
                y,
                self.center_x - spread,
                y - 10 - sway,
                self.center_x - spread + 8,
                y + 12,
            ]
            right_coords = [
                self.center_x,
                y,
                self.center_x + spread,
                y - 10 + sway,
                self.center_x + spread - 8,
                y + 12,
            ]
            for item, coords in ((left, left_coords), (right, right_coords)):
                self.canvas.coords(item, *coords)
                color = mix(COLORS["leaf_dim"], COLORS["leaf"], 0.4 + 0.6 * stage_ratio)
                self.canvas.itemconfigure(item, fill=color)
                state = "normal" if idx < visible_pairs else "hidden"
                self.canvas.itemconfigure(item, state=state)

        flower_y = self.base_y - (height + 18)
        radius = 10 + stage_ratio * 5
        if stage_index >= len(self.leaf_pairs):
            self.canvas.coords(
                self.flower,
                self.center_x - radius,
                flower_y - radius,
                self.center_x + radius,
                flower_y + radius,
            )
            self.canvas.itemconfigure(self.flower, state="normal")
        else:
            self.canvas.itemconfigure(self.flower, state="hidden")

    def animate(self):
        self.breath_phase = (self.breath_phase + 0.08) % (math.pi * 2)
        glow_radius = 150 + 12 * math.sin(self.breath_phase)
        self.canvas.coords(
            self.glow,
            self.center_x - glow_radius,
            self.base_y - glow_radius * 0.7,
            self.center_x + glow_radius,
            self.base_y + glow_radius * 0.25,
        )
        glow_color = mix("#03110c", COLORS["leaf"], 0.4 + 0.2 * math.sin(self.breath_phase))
        self.canvas.itemconfigure(self.glow, fill=glow_color)

        for data in self.fireflies:
            drift_x = math.sin(self.breath_phase * 0.5) * 0.4
            self.canvas.move(data["id"], drift_x, -data["speed"])
            x1, y1, x2, y2 = self.canvas.coords(data["id"])
            if y2 < -5:
                reset_y = self.base_y + random.randint(30, 120)
                delta_x = random.randint(-160, 160)
                self.canvas.move(data["id"], delta_x, reset_y - y1)


class PlantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grow a Plant")
        self.root.configure(bg=COLORS["ink"])
        self.root.geometry("580x660")
        self.root.minsize(540, 640)
        self.state = load_state()

        self.scene = None
        self._build_ui()
        self._update_ui()
        self.root.after(5000, self._heartbeat)
        self.root.after(120, self._animate_scene)

    def _build_ui(self):
        self.wrapper = tk.Frame(self.root, bg=COLORS["ink"])
        self.wrapper.pack(fill="both", expand=True)

        self.card = tk.Frame(
            self.wrapper,
            bg=COLORS["card"],
            highlightbackground=COLORS["outline"],
            highlightcolor=COLORS["outline"],
            highlightthickness=1,
            bd=0,
        )
        self.card.pack(padx=32, pady=34, fill="both", expand=True)

        self.title_label = tk.Label(
            self.card,
            text="Grow a Plant",
            font=("Bahnschrift", 26, "bold"),
            bg=COLORS["card"],
            fg=COLORS["accent"],
        )
        self.title_label.pack(pady=(24, 6))

        self.subtitle_label = tk.Label(
            self.card,
            text="Night garden companion",
            font=("Bahnschrift", 12),
            bg=COLORS["card"],
            fg=COLORS["text_soft"],
        )
        self.subtitle_label.pack()

        self.scene = PlantScene(self.card)

        self.stage_label = tk.Label(
            self.card,
            text="",
            font=("Bahnschrift", 16, "bold"),
            bg=COLORS["card"],
            fg=COLORS["text_primary"],
        )
        self.stage_label.pack()

        self.description_label = tk.Label(
            self.card,
            text="",
            font=("Bahnschrift", 11),
            bg=COLORS["card"],
            fg=COLORS["text_muted"],
            wraplength=420,
            justify="center",
        )
        self.description_label.pack(pady=(6, 16))

        self.progress_canvas = tk.Canvas(
            self.card,
            width=420,
            height=52,
            bg=COLORS["panel"],
            highlightthickness=0,
        )
        self.progress_canvas.pack(pady=(0, 10))
        self.progress_canvas.create_rectangle(10, 10, 410, 42, outline=COLORS["outline"], width=2)
        self.progress_fill = self.progress_canvas.create_rectangle(12, 12, 12, 40, fill=COLORS["accent_dim"], outline="")
        self.progress_text = self.progress_canvas.create_text(
            212,
            26,
            text="",
            fill=COLORS["text_primary"],
            font=("Bahnschrift", 11, "bold"),
        )

        self.metrics_label = tk.Label(
            self.card,
            text="",
            font=("Consolas", 11),
            bg=COLORS["panel"],
            fg=COLORS["text_primary"],
            justify="left",
            padx=16,
            pady=12,
            wraplength=420,
        )
        self.metrics_label.pack(pady=(6, 10))

        self.last_watered_label = tk.Label(
            self.card,
            text="",
            font=("Bahnschrift", 10),
            bg=COLORS["card"],
            fg=COLORS["text_muted"],
        )
        self.last_watered_label.pack()

        self.status_label = tk.Label(
            self.card,
            text="",
            font=("Bahnschrift", 10, "italic"),
            bg=COLORS["card"],
            fg=COLORS["text_soft"],
            wraplength=380,
        )
        self.status_label.pack(pady=(4, 14))

        self.water_button = tk.Button(
            self.card,
            text="Water Plant",
            command=self.water_plant,
            font=("Bahnschrift", 13, "bold"),
            bg=COLORS["button"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["button_active"],
            activeforeground=COLORS["text_primary"],
            relief="flat",
            padx=28,
            pady=12,
            cursor="hand2",
        )
        self.water_button.pack(pady=(4, 22))

    def water_plant(self):
        now = time.time()
        if now - self.state["last_watered"] < DAY_SECONDS:
            remaining = DAY_SECONDS - (now - self.state["last_watered"])
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            messagebox.showinfo(
                "Easy there",
                f"The soil is still moist. Try again in {hours}h {minutes}m.",
            )
            return

        self.state["last_watered"] = now
        self.state["manual_growth"] = float(self.state.get("manual_growth", 0.0)) + WATER_BONUS
        save_state(self.state)
        self.status_label.config(text="Your plant happily soaks up the water.")
        self._update_ui()

    def _heartbeat(self):
        self._update_ui()
        self.root.after(5000, self._heartbeat)

    def _animate_scene(self):
        self.scene.animate()
        self.root.after(120, self._animate_scene)

    def _update_ui(self):
        points = growth_points(self.state)
        stage = pick_stage(points)
        stage_index = STAGES.index(stage)
        prev_limit = STAGES[stage_index - 1]["limit"] if stage_index else 0.0
        span = stage["limit"] - prev_limit if math.isfinite(stage["limit"]) else 1.0
        stage_ratio = 1.0 if not math.isfinite(stage["limit"]) else max(0.0, min(1.0, (points - prev_limit) / max(0.001, span)))

        overall_ratio = max(0.0, min(1.0, points / DISPLAY_CAP))
        fill_width = 12 + overall_ratio * (410 - 12)
        self.progress_canvas.coords(self.progress_fill, 12, 12, fill_width, 40)
        self.progress_canvas.itemconfigure(self.progress_text, text=f"{points:.1f} growth points")

        passive = max(0.0, points - float(self.state.get("manual_growth", 0.0)))
        self.metrics_label.config(
            text=(
                f"Passive glow   : {passive:.1f}\n"
                f"Water bonuses : {self.state.get('manual_growth', 0.0):.1f}\n"
                f"Daily limit    : 1 sip / 24h"
            )
        )

        self.stage_label.config(text=f"Stage: {stage['name']}")
        self.description_label.config(text=stage["description"])
        self.last_watered_label.config(text=f"Last watered: {format_timestamp(self.state['last_watered'])}")
        if not self.status_label.cget("text"):
            self.status_label.config(text="Water gently once per day to keep the glow steady.")

        self.scene.render(stage_index, stage_ratio)


def main():
    root = tk.Tk()
    PlantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
