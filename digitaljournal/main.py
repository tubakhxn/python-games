"""Mobile-inspired Tkinter journaling experience."""
from __future__ import annotations

import os
import random
import subprocess
import sys
import textwrap
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import font as tkfont, messagebox, ttk

APP_TITLE = "Calm Journal"
ENTRY_DIR = Path(__file__).parent / "entries"
DATE_FORMAT = "%Y-%m-%d"

COLORS = {
    "gradient_top": "#d7e8ff",
    "gradient_bottom": "#f4f2ff",
    "left_bg": "#0d101f",
    "left_muted": "#9fa7c9",
    "right_bg": "#e9f5f2",
    "right_surface": "#fdfefe",
    "accent": "#6c63ff",
    "accent_soft": "#cdd7ff",
    "text_dark": "#0f172a",
    "text_muted": "#566171",
    "warning": "#f97316",
}

CARD_COLORS = ["#fcb89a", "#ffe6a7", "#c9e1ff", "#ffd8eb"]

PROMPTS = [
    "Describe one sensory detail you remember from today.",
    "If today had a soundtrack, what song would play?",
    "What tiny win did you overlook at first?",
    "Write a message you need to hear tonight.",
    "Capture the mood outside your window in three lines.",
]

AFFIRMATIONS = [
    "Your words do not need polish to matter.",
    "Tiny reflections grow into clarity.",
    "Pause, breathe, capture the moment.",
    "You are crafting proof that you were here.",
]


def blend_colors(color_a: str, color_b: str, factor: float) -> str:
    """Linearly blend two hex colors for soft gradients."""
    def hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex_to_rgb(color_a)
    r2, g2, b2 = hex_to_rgb(color_b)
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class CloudLayer:
    """Renders slow floating cloud blobs behind the phone cards."""

    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self.clouds: list[dict[str, object]] = []
        self.canvas.bind("<Configure>", self._reset, add="+")
        self.canvas.after(50, self._reset)
        self.canvas.after(120, self._animate)

    def _reset(self, event: tk.Event[tk.Canvas] | None = None) -> None:
        width = event.width if event else self.canvas.winfo_width()
        height = event.height if event else self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        self.canvas.delete("cloud")
        self.clouds.clear()
        cloud_count = max(width // 220, 4)
        for idx in range(cloud_count):
            tag = f"cloud_{idx}"
            size = random.randint(160, 260)
            x = random.randint(-80, width - size)
            y = random.randint(40, int(height * 0.6))
            tint = blend_colors(COLORS["gradient_top"], "#ffffff", random.uniform(0.4, 0.75))
            for bump in range(3):
                offset = bump * size * 0.4
                self.canvas.create_oval(
                    x + offset,
                    y + random.randint(-10, 15),
                    x + offset + size,
                    y + random.randint(50, 90),
                    fill=tint,
                    outline="",
                    tags=("cloud", tag),
                    stipple="gray25",
                )
            self.clouds.append({
                "tag": tag,
                "speed": 0.2 + random.random() * 0.2,
                "vertical": y,
            })

    def _animate(self) -> None:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for cloud in self.clouds:
            tag = cloud["tag"]
            speed = cloud["speed"]
            self.canvas.move(tag, speed, 0)
            bbox = self.canvas.bbox(tag)
            if not bbox:
                continue
            if bbox[0] > width + 60:
                new_left = -random.randint(150, 280)
                new_top = random.randint(40, int(height * 0.6))
                delta_x = new_left - bbox[0]
                delta_y = new_top - bbox[1]
                self.canvas.move(tag, delta_x, delta_y)
        self.canvas.after(60, self._animate)


class JournalApp:
    """Renders a dual-phone layout inspired by the reference mockup."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1280x720")
        self.root.minsize(1100, 620)
        ENTRY_DIR.mkdir(exist_ok=True)

        self.body_font = tkfont.Font(family="Segoe UI", size=11)
        self.bold_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.italic_font = tkfont.Font(family="Segoe UI", size=11, slant="italic")

        self.date_var = tk.StringVar(value=self._today_string())
        self.metrics_var = tk.StringVar(value="0 chars  0 words")
        self.status_var = tk.StringVar(value="Ready")
        self.prompt_var = tk.StringVar(value=random.choice(PROMPTS))
        self.affirmation_var = tk.StringVar(value=random.choice(AFFIRMATIONS))
        self.card_widgets: dict[str, tk.Frame] = {}

        self._configure_styles()
        self._build_layout()
        self._load_entry_dates()
        self._update_metrics()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Toolbar.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 4), relief="flat")
        style.map(
            "Toolbar.TButton",
            background=[("active", COLORS["accent_soft"])],
            foreground=[("active", COLORS["text_dark"])]
        )
        style.configure("Minimal.TFrame", background=COLORS["right_bg"])

    def _build_layout(self) -> None:
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_canvas_resize)
        self.cloud_layer = CloudLayer(self.bg_canvas)

        self.left_phone = tk.Frame(self.bg_canvas, bg=COLORS["left_bg"], bd=0, highlightthickness=0)
        self.right_phone = tk.Frame(self.bg_canvas, bg=COLORS["right_bg"], bd=0, highlightthickness=0)
        self.left_phone.configure(padx=24, pady=26)
        self.right_phone.configure(padx=26, pady=28)

        self.left_window = self.bg_canvas.create_window(0, 0, anchor="nw", window=self.left_phone)
        self.right_window = self.bg_canvas.create_window(0, 0, anchor="nw", window=self.right_phone)
        self.bg_canvas.tag_raise(self.left_window)
        self.bg_canvas.tag_raise(self.right_window)

        self._build_left_phone()
        self._build_right_phone()

    def _build_left_phone(self) -> None:
        header = tk.Frame(self.left_phone, bg=COLORS["left_bg"])
        header.pack(fill="x")
        tk.Label(
            header,
            text="Hi, Tuba", 
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=COLORS["left_bg"],
        ).pack(anchor="w")
        tk.Label(
            header,
            text="My Notes",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg=COLORS["left_bg"],
            pady=6,
        ).pack(anchor="w")

        chip_row = tk.Frame(self.left_phone, bg=COLORS["left_bg"])
        chip_row.pack(fill="x", pady=(6, 10))
        for label in ("All", "Ideas", "Daily"):
            active = label == "All"
            tk.Label(
                chip_row,
                text=label,
                fg="white" if active else COLORS["left_muted"],
                bg=COLORS["accent"] if active else "#1a1f34",
                padx=14,
                pady=6,
                font=("Segoe UI", 10, "bold" if active else "normal"),
                bd=0,
                relief="flat",
                cursor="hand2",
            ).pack(side="left", padx=4)

        self.cards_frame = tk.Frame(self.left_phone, bg=COLORS["left_bg"])
        self.cards_frame.pack(fill="both", expand=True, pady=(12, 12))

        prompt_box = tk.Frame(self.left_phone, bg="#151a2d", bd=0, highlightthickness=0)
        prompt_box.pack(fill="x", pady=(4, 0))
        tk.Label(
            prompt_box,
            text="Tonight's spark",
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["left_muted"],
            bg="#151a2d",
        ).pack(anchor="w", pady=(4, 2))
        tk.Label(
            prompt_box,
            textvariable=self.prompt_var,
            font=("Segoe UI", 11),
            wraplength=250,
            fg="white",
            bg="#151a2d",
        ).pack(anchor="w")
        tk.Label(
            prompt_box,
            textvariable=self.affirmation_var,
            font=("Segoe UI", 10),
            fg=COLORS["left_muted"],
            bg="#151a2d",
            wraplength=250,
            pady=6,
        ).pack(anchor="w")
        tk.Button(
            prompt_box,
            text="New spark",
            command=self._refresh_prompt,
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["text_dark"],
            bg=COLORS["accent_soft"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 8))

        tk.Button(
            self.left_phone,
            text="View archive",
            command=self._open_entries_folder,
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["left_bg"],
            bg="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(anchor="w", pady=(8, 0))

    def _build_right_phone(self) -> None:
        tk.Label(
            self.right_phone,
            text="Journal entry",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_dark"],
            bg=COLORS["right_bg"],
        ).pack(anchor="w")
        tk.Label(
            self.right_phone,
            text="Capture the details of today before they fade",
            font=("Segoe UI", 11),
            fg=COLORS["text_muted"],
            bg=COLORS["right_bg"],
            pady=4,
        ).pack(anchor="w")

        date_row = tk.Frame(self.right_phone, bg=COLORS["right_bg"])
        date_row.pack(fill="x", pady=(12, 6))
        tk.Label(
            date_row,
            text="Entry date",
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["text_muted"],
            bg=COLORS["right_bg"],
        ).pack(anchor="w")
        entry_bar = tk.Frame(self.right_phone, bg=COLORS["right_bg"])
        entry_bar.pack(fill="x")
        self.date_entry = ttk.Entry(entry_bar, textvariable=self.date_var, font=("Segoe UI", 12))
        self.date_entry.pack(side="left", fill="x", expand=True, ipadx=4, ipady=4)
        tk.Button(
            entry_bar,
            text="Today",
            command=self._set_today,
            bg=COLORS["accent_soft"],
            fg=COLORS["text_dark"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
        ).pack(side="left", padx=6)
        tk.Button(
            entry_bar,
            text="New page",
            command=self._new_entry,
            bg="white",
            fg=COLORS["text_dark"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
        ).pack(side="left")

        toolbar = ttk.Frame(self.right_phone, style="Minimal.TFrame")
        toolbar.pack(fill="x", pady=(14, 6))
        ttk.Button(toolbar, text="Bold", style="Toolbar.TButton", command=lambda: self._apply_format("bold")).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Italic", style="Toolbar.TButton", command=lambda: self._apply_format("italic")).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Clear", style="Toolbar.TButton", command=self._clear_formatting).pack(side="left", padx=6)

        editor_shell = tk.Frame(self.right_phone, bg=COLORS["right_surface"], bd=0, highlightthickness=0)
        editor_shell.pack(fill="both", expand=True, pady=(6, 10))
        editor_shell.rowconfigure(0, weight=1)
        editor_shell.columnconfigure(0, weight=1)

        self.text_widget = tk.Text(
            editor_shell,
            wrap="word",
            font=self.body_font,
            bg=COLORS["right_surface"],
            fg=COLORS["text_dark"],
            relief="flat",
            padx=14,
            pady=14,
            spacing3=8,
            insertbackground=COLORS["text_dark"],
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(editor_shell, orient="vertical", command=self.text_widget.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.text_widget.configure(yscrollcommand=scroll.set)
        self.text_widget.tag_configure("bold", font=self.bold_font)
        self.text_widget.tag_configure("italic", font=self.italic_font)
        self.text_widget.bind("<<Modified>>", self._on_text_modified)

        status = tk.Frame(self.right_phone, bg=COLORS["right_bg"])
        status.pack(fill="x", pady=(0, 10))
        tk.Label(status, textvariable=self.metrics_var, fg=COLORS["text_muted"], bg=COLORS["right_bg"], font=("Segoe UI", 10)).pack(side="left")
        tk.Label(status, textvariable=self.status_var, fg=COLORS["warning"], bg=COLORS["right_bg"], font=("Segoe UI", 10, "bold")).pack(side="right")

        action_row = tk.Frame(self.right_phone, bg=COLORS["right_bg"])
        action_row.pack(fill="x")
        tk.Button(
            action_row,
            text="Save entry",
            command=self._save_entry,
            bg=COLORS["accent"],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
        ).pack(side="left")
        tk.Button(
            action_row,
            text="Open folder",
            command=self._open_entries_folder,
            bg="white",
            fg=COLORS["text_dark"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(side="left", padx=10)

    def _draw_gradient(self, width: int, height: int) -> None:
        self.bg_canvas.delete("gradient")
        steps = 80
        for i in range(steps):
            ratio = i / max(steps - 1, 1)
            color = blend_colors(COLORS["gradient_top"], COLORS["gradient_bottom"], ratio)
            y0 = int(height * i / steps)
            y1 = int(height * (i + 1) / steps)
            self.bg_canvas.create_rectangle(0, y0, width, y1, outline="", fill=color, tags="gradient")
        self.bg_canvas.tag_lower("gradient")

    def _on_canvas_resize(self, event: tk.Event[tk.Canvas]) -> None:
        self._draw_gradient(event.width, event.height)
        gap = 50
        phone_height = min(event.height - 120, 620)
        phone_height = max(phone_height, 520)
        left_width = 360
        right_width = 420
        total_width = left_width + right_width + gap
        start_x = max((event.width - total_width) / 2, 30)
        top_y = max((event.height - phone_height) / 2, 30)
        self.bg_canvas.coords(self.left_window, start_x, top_y)
        self.bg_canvas.coords(self.right_window, start_x + left_width + gap, top_y - 15)
        self.bg_canvas.itemconfigure(self.left_window, width=left_width, height=phone_height)
        self.bg_canvas.itemconfigure(self.right_window, width=right_width, height=phone_height + 30)

    def _render_cards(self, entries: list[Path]) -> None:
        for child in self.cards_frame.winfo_children():
            child.destroy()
        self.card_widgets.clear()
        if not entries:
            tk.Label(
                self.cards_frame,
                text="No entries yet. Tap New page to begin",
                fg=COLORS["left_muted"],
                bg=COLORS["left_bg"],
                wraplength=240,
            ).pack(anchor="w", pady=20)
            return
        for idx, file in enumerate(entries[:4]):
            color = CARD_COLORS[idx % len(CARD_COLORS)]
            card = tk.Frame(self.cards_frame, bg=color, bd=0, highlightthickness=2, highlightbackground=color)
            card.pack(fill="x", pady=6)
            try:
                content = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = ""
            snippet = textwrap.shorten(content.strip().replace("\n", " "), width=90, placeholder=" ") if content.strip() else "Empty entry"
            pretty_date = datetime.strptime(file.stem, DATE_FORMAT).strftime("%b %d")
            tk.Label(card, text=pretty_date, font=("Segoe UI", 12, "bold"), bg=color, fg=COLORS["text_dark"]).pack(anchor="w", pady=(8, 2), padx=12)
            tk.Label(card, text=snippet, font=("Segoe UI", 10), bg=color, fg=COLORS["text_dark"], wraplength=250, justify="left").pack(anchor="w", padx=12, pady=(0, 10))
            card.bind("<Button-1>", lambda _e, date=file.stem: self._load_entry_by_date(date))
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda _e, date=file.stem: self._load_entry_by_date(date))
            self.card_widgets[file.stem] = card

    def _highlight_card(self, date_text: str) -> None:
        for date, widget in self.card_widgets.items():
            widget.config(highlightbackground=CARD_COLORS[list(self.card_widgets).index(date) % len(CARD_COLORS)])
        if date_text in self.card_widgets:
            self.card_widgets[date_text].config(highlightbackground=COLORS["accent"])

    def _today_string(self) -> str:
        return datetime.now().strftime(DATE_FORMAT)

    def _set_today(self) -> None:
        self.date_var.set(self._today_string())
        self.status_var.set("Ready")

    def _new_entry(self) -> None:
        self._set_today()
        self.text_widget.delete("1.0", tk.END)
        self.status_var.set("Fresh page")
        self._update_metrics()

    def _validate_date(self, value: str) -> datetime:
        try:
            return datetime.strptime(value, DATE_FORMAT)
        except ValueError as exc:
            raise ValueError("Enter date as YYYY-MM-DD") from exc

    def _entry_path(self, date_obj: datetime) -> Path:
        return ENTRY_DIR / f"{date_obj.strftime(DATE_FORMAT)}.txt"

    def _save_entry(self) -> None:
        date_text = self.date_var.get().strip()
        try:
            date_obj = self._validate_date(date_text)
        except ValueError as error:
            messagebox.showerror("Invalid date", str(error))
            return
        content = self.text_widget.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showinfo("Empty entry", "Write something before saving.")
            return
        self._entry_path(date_obj).write_text(content, encoding="utf-8")
        self.status_var.set("Saved")
        self._load_entry_dates(select_date=date_text)

    def _load_entry_dates(self, select_date: str | None = None) -> None:
        entries = sorted(ENTRY_DIR.glob("*.txt"), reverse=True)
        self._render_cards(entries)
        if select_date:
            self._load_entry_by_date(select_date)
        elif entries:
            self._load_entry_by_date(entries[0].stem)

    def _load_entry_by_date(self, date_text: str) -> None:
        path = ENTRY_DIR / f"{date_text}.txt"
        if not path.exists():
            return
        content = path.read_text(encoding="utf-8")
        self.date_var.set(date_text)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        self.status_var.set(f"Loaded {date_text}")
        self._update_metrics()
        self._highlight_card(date_text)

    def _apply_format(self, tag: str) -> None:
        try:
            start = self.text_widget.index("sel.first")
            end = self.text_widget.index("sel.last")
        except tk.TclError:
            messagebox.showinfo("Select text", "Highlight text before applying formatting.")
            return
        self.text_widget.tag_add(tag, start, end)

    def _clear_formatting(self) -> None:
        self.text_widget.tag_remove("bold", "1.0", tk.END)
        self.text_widget.tag_remove("italic", "1.0", tk.END)

    def _on_text_modified(self, _event: tk.Event[tk.Text]) -> None:
        if self.text_widget.edit_modified():
            self._update_metrics()
            self.status_var.set("Unsaved changes")
            self.text_widget.edit_modified(False)

    def _update_metrics(self) -> None:
        text = self.text_widget.get("1.0", "end-1c").strip()
        chars = len(text)
        words = len(text.split()) if text else 0
        self.metrics_var.set(f"{chars} chars  {words} words")

    def _refresh_prompt(self) -> None:
        self.prompt_var.set(random.choice(PROMPTS))
        self.affirmation_var.set(random.choice(AFFIRMATIONS))

    def _open_entries_folder(self) -> None:
        path = ENTRY_DIR.resolve()
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except OSError as error:
            messagebox.showerror("Unable to open folder", str(error))


def main() -> None:
    root = tk.Tk()
    JournalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
