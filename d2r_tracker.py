import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

# Resolve config file location — next to .exe when packaged, next to script otherwise
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "config.json")

DEFAULT_CONFIG = {
    "game_prefix": "casual",
    "game_number": 1,
    "password": "123"
}

# Theme
BG       = "#1a1a2e"
BG2      = "#16213e"
ACCENT   = "#e94560"
TEXT     = "#eaeaea"
SUBTEXT  = "#777777"
BTN_BG   = "#0f3460"


class D2RTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("D2R Game Tracker")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.status_timer = None

        self.config = self.load_config()
        self.setup_ui()
        self.root.attributes('-topmost', True)

    # ------------------------------------------------------------------ config

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    cfg = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in cfg:
                        cfg[k] = v
                return cfg
            except Exception:
                pass
        cfg = DEFAULT_CONFIG.copy()
        self._write_config(cfg)
        return cfg

    def save_config(self):
        self._write_config(self.config)

    def _write_config(self, cfg):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save config:\n{e}")

    # ------------------------------------------------------------------ helpers

    def get_game_name(self):
        return f"{self.config['game_prefix']}{self.config['game_number']}"

    def copy_to_clipboard(self, text, label):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.show_status(f"Copied {label}")

    def show_status(self, message):
        self.status_var.set(message)
        if self.status_timer:
            self.root.after_cancel(self.status_timer)
        self.status_timer = self.root.after(2000, lambda: self.status_var.set(""))

    # ------------------------------------------------------------------ actions

    def increment(self):
        self.config['game_number'] += 1
        self.save_config()
        self.game_name_var.set(self.get_game_name())

    def decrement(self):
        if self.config['game_number'] > 1:
            self.config['game_number'] -= 1
            self.save_config()
            self.game_name_var.set(self.get_game_name())

    def toggle_topmost(self):
        self.root.attributes('-topmost', self.topmost_var.get())

    # ------------------------------------------------------------------ settings

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.attributes('-topmost', True)

        pad = {"padx": 12, "pady": 6}

        fields = [
            ("Game Prefix", "prefix", self.config['game_prefix']),
            ("Password",    "password", self.config['password']),
            ("Game Number", "number",  str(self.config['game_number'])),
        ]

        entries = {}
        for i, (label, key, val) in enumerate(fields):
            tk.Label(win, text=label + ":", bg=BG, fg=TEXT,
                     font=('Segoe UI', 9), anchor='e', width=12).grid(
                row=i, column=0, sticky='e', **pad)
            var = tk.StringVar(value=val)
            tk.Entry(win, textvariable=var, bg=BG2, fg=TEXT,
                     insertbackground=TEXT, relief='flat',
                     font=('Consolas', 10), width=16).grid(
                row=i, column=1, sticky='w', **pad)
            entries[key] = var

        def save():
            prefix = entries['prefix'].get().strip()
            password = entries['password'].get()
            try:
                number = int(entries['number'].get())
                if number < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid", "Game number must be a positive integer.", parent=win)
                return
            if not prefix:
                messagebox.showerror("Invalid", "Game prefix cannot be empty.", parent=win)
                return

            self.config['game_prefix'] = prefix
            self.config['password'] = password
            self.config['game_number'] = number
            self.save_config()
            self.game_name_var.set(self.get_game_name())
            self.password_var.set(self.config['password'])
            win.destroy()

        btn_row = tk.Frame(win, bg=BG)
        btn_row.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self._btn(btn_row, "Save", save, ACCENT).pack(side='left', padx=6)
        self._btn(btn_row, "Cancel", win.destroy, BTN_BG).pack(side='left', padx=6)

    # ------------------------------------------------------------------ UI build

    def _btn(self, parent, text, cmd, bg, **kwargs):
        defaults = dict(font=('Segoe UI', 9), padx=12, pady=4)
        defaults.update(kwargs)
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=TEXT,
                         relief='flat', cursor='hand2', activebackground=ACCENT,
                         activeforeground=TEXT, bd=0, **defaults)

    def _info_row(self, parent, label, var, copy_cmd):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill='x', pady=3)

        tk.Label(row, text=label, bg=BG, fg=SUBTEXT,
                 font=('Segoe UI', 9), width=5, anchor='e').pack(side='left')

        box = tk.Frame(row, bg=BG2, padx=10, pady=5)
        box.pack(side='left', padx=6)
        tk.Label(box, textvariable=var, bg=BG2, fg=TEXT,
                 font=('Consolas', 13, 'bold'), width=12, anchor='w').pack(side='left')

        self._btn(row, "Copy", copy_cmd, BTN_BG,
                  font=('Segoe UI', 8), padx=8, pady=2).pack(side='left')

    def setup_ui(self):
        self.game_name_var = tk.StringVar(value=self.get_game_name())
        self.password_var  = tk.StringVar(value=self.config['password'])
        self.status_var    = tk.StringVar()
        self.topmost_var   = tk.BooleanVar(value=True)

        # Header bar
        header = tk.Frame(self.root, bg=BG2, pady=7)
        header.pack(fill='x')
        tk.Label(header, text="D2R Game Tracker", bg=BG2, fg=ACCENT,
                 font=('Segoe UI', 11, 'bold')).pack(side='left', padx=12)
        tk.Button(header, text="⚙", command=self.open_settings,
                  bg=BG2, fg=SUBTEXT, relief='flat', font=('Segoe UI', 11),
                  cursor='hand2', activebackground=BG2, activeforeground=TEXT,
                  bd=0).pack(side='right', padx=10)

        # Info rows
        content = tk.Frame(self.root, bg=BG, padx=14, pady=10)
        content.pack(fill='both')
        self._info_row(content, "Game:", self.game_name_var,
                       lambda: self.copy_to_clipboard(self.game_name_var.get(), "game name"))
        self._info_row(content, "Pass:", self.password_var,
                       lambda: self.copy_to_clipboard(self.password_var.get(), "password"))

        # Increment / decrement
        nav = tk.Frame(self.root, bg=BG, pady=8)
        nav.pack()
        self._btn(nav, "  ◄  ", self.decrement, BTN_BG).pack(side='left', padx=6)
        tk.Label(nav, text="game #", bg=BG, fg=SUBTEXT,
                 font=('Segoe UI', 8)).pack(side='left', padx=2)
        self._btn(nav, "  ►  ", self.increment, BTN_BG).pack(side='left', padx=6)

        # Always on top checkbox
        chk_frame = tk.Frame(self.root, bg=BG, pady=2)
        chk_frame.pack()
        tk.Checkbutton(chk_frame, text="Always on top", variable=self.topmost_var,
                       command=self.toggle_topmost, bg=BG, fg=SUBTEXT,
                       selectcolor=BG2, activebackground=BG, activeforeground=TEXT,
                       font=('Segoe UI', 8)).pack()

        # Status bar
        status_bar = tk.Frame(self.root, bg=BG2, pady=3)
        status_bar.pack(fill='x', side='bottom')
        tk.Label(status_bar, textvariable=self.status_var, bg=BG2, fg=ACCENT,
                 font=('Segoe UI', 8)).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = D2RTracker(root)
    root.mainloop()
