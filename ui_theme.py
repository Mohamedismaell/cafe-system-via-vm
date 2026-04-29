import os
import subprocess
import sys
import tkinter as tk

#  Paths 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


#  Palette 
CREAM    = "#F3E9DC"
CARAMEL  = "#C08552"
BROWNIE  = "#5E3023"
COFFEE   = "#895737"
WHITE    = "#FFFFFF"
LIGHT_BR = "#D4A96A"
DISABLED = "#D8CEC3"
DANGER   = "#C0392B"
SUCCESS  = "#4CAF50"
WARNING  = "#E8A020"
TEXT_DARK  = "#3B2314"
TEXT_MUTED = "#8B6555"
BG_ALT     = "#FAF6EF"

#  Typography 
FONT_TITLE    = ("Georgia", 22, "bold")
FONT_SECTION  = ("Georgia", 17, "bold")
FONT_LABEL    = ("Georgia", 13, "bold")
FONT_BODY     = ("Georgia", 11)
FONT_SMALL    = ("Georgia", 9)
FONT_BUTTON   = ("Georgia", 10, "bold")
FONT_SUBTITLE = ("Georgia", 10, "italic")
FONT_TOTAL    = ("Georgia", 14, "bold")
FONT_BTN_ICON = ("Segoe UI Emoji", 26)
FONT_BTN_LBL  = ("Georgia", 11, "bold")
FONT_BTN_SUB  = ("Georgia", 8)
FONT_WELCOME  = ("Georgia", 12)


def configure_root(root, title):
    root.title(title)
    root.state("zoomed")
    root.configure(bg=CREAM)


def _set_button_bg(button, color):
    if str(button.cget("state")) != "disabled":
        button.config(bg=color)


def hover_button(button, base_color, hover_color):
    button.bind("<Enter>", lambda e, b=button, c=hover_color: _set_button_bg(b, c))
    button.bind("<Leave>", lambda e, b=button, c=base_color:  _set_button_bg(b, c))
    return button


def make_button(parent, text, bg, command, hover=None, font=None, **kwargs):
    button = tk.Button(
        parent,
        text=text,
        bg=bg,
        fg=WHITE,
        font=font or FONT_BUTTON,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=command,
        activebackground=hover or LIGHT_BR,
        activeforeground=BROWNIE,
        **kwargs,
    )
    return hover_button(button, bg, hover or LIGHT_BR)


def build_header(root, title, subtitle=None):
    tk.Frame(root, bg=BROWNIE, height=6).pack(fill="x")
    header = tk.Frame(root, bg=BROWNIE, pady=12)
    header.pack(fill="x")
    tk.Label(header, text=title, font=FONT_SECTION, bg=BROWNIE, fg=CREAM).pack(side="left", padx=20)
    if subtitle:
        tk.Label(header, text=subtitle, font=FONT_SMALL, bg=BROWNIE, fg=CARAMEL).pack(side="left", padx=(0, 8))
    tk.Frame(root, bg=CARAMEL, height=3).pack(fill="x")
    return header


def build_footer(root):
    footer = tk.Frame(root, bg=BROWNIE, pady=6)
    footer.pack(fill="x", side="bottom")
    tk.Label(
        footer,
        text="Copyright 2025 Corner Cafe System  |  All rights reserved",
        font=FONT_SMALL,
        bg=BROWNIE,
        fg=CARAMEL,
    ).pack()
    return footer


def make_scrollable_list(parent, select_bg=None, **kwargs):
    """Return (frame, listbox) with a vertical scrollbar already packed."""
    frame = tk.Frame(parent, bg=WHITE)
    scrollbar = tk.Scrollbar(frame, orient="vertical")
    listbox = tk.Listbox(
        frame,
        font=FONT_BODY,
        bg=CREAM,
        fg=BROWNIE,
        selectbackground=select_bg or CARAMEL,
        selectforeground=WHITE,
        relief="flat",
        bd=0,
        activestyle="none",
        yscrollcommand=scrollbar.set,
        **kwargs,
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(fill="both", expand=True)
    return frame, listbox


def go_back(navigate, username, role, root, dash=None):
    """Navigate back to the dashboard, or fall back to relaunching it."""
    if navigate:
        navigate("dashboard", username=username, role=role)
        return
    root.destroy()
    if dash:
        try:
            dash.deiconify()
            dash.state("zoomed")
            return
        except Exception:
            pass
    dash_path = os.path.join(BASE_DIR, "dashboard.py")
    if os.path.exists(dash_path):
        subprocess.Popen([sys.executable, dash_path])
