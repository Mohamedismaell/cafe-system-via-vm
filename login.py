import tkinter as tk
from tkinter import messagebox
import csv
import os
import sys

# ─── Color Palette ───────────────────────────────────────────────
CREAM    = "#F3E9DC"
CARAMEL  = "#C08552"
BROWNIE  = "#5E3023"
COFFEE   = "#895737"
WHITE    = "#FFFFFF"
ERROR_RED = "#C0392B"

# ─── Font Definitions ────────────────────────────────────────────
FONT_TITLE   = ("Georgia", 26, "bold")
FONT_SUBTITLE= ("Georgia", 11, "italic")
FONT_LABEL   = ("Georgia", 11)
FONT_ENTRY   = ("Courier New", 12)
FONT_BUTTON  = ("Georgia", 12, "bold")
FONT_SMALL   = ("Georgia", 9)

# ─── CSV Path ────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "users.csv")


def verify_login(username: str, password: str) -> dict | None:
    """Read users.csv and verify credentials. Returns user row or None."""
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return row
    return None


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Café System — Login")
        self.root.state('zoomed')
        self.root.configure(bg=CREAM)

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────
    def _build_ui(self):
        # Top decorative banner
        banner = tk.Frame(self.root, bg=BROWNIE, height=8)
        banner.pack(fill="x")

        # Logo / icon area
        logo_frame = tk.Frame(self.root, bg=CREAM, pady=30)
        logo_frame.pack(fill="x")

        # Coffee cup emoji as logo
        tk.Label(
            logo_frame, text="☕",
            font=("Segoe UI Emoji", 52),
            bg=CREAM, fg=BROWNIE
        ).pack()

        tk.Label(
            logo_frame,
            text="CORNER CAFÉ",
            font=FONT_TITLE,
            bg=CREAM, fg=BROWNIE
        ).pack()

        tk.Label(
            logo_frame,
            text="Café Management System",
            font=FONT_SUBTITLE,
            bg=CREAM, fg=COFFEE
        ).pack(pady=(2, 0))

        # Divider line
        tk.Frame(self.root, bg=CARAMEL, height=2).pack(fill="x", padx=40, pady=(0, 10))

        # Centered container
        center_container = tk.Frame(self.root, bg=CREAM)
        center_container.pack(expand=True, fill="both")

        # Card frame for login form
        card = tk.Frame(center_container, bg=WHITE, bd=1, relief="raised",
                        padx=40, pady=35)
        card.pack(side="top", expand=False, padx=50, pady=20, fill="x")

        # Username field
        tk.Label(card, text="USERNAME", font=("Georgia", 9, "bold"),
                 bg=WHITE, fg=COFFEE, anchor="w").pack(fill="x")

        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            card, textvariable=self.username_var,
            font=FONT_ENTRY, bg=CREAM, fg=BROWNIE,
            relief="flat", bd=0, insertbackground=BROWNIE
        )
        username_entry.pack(fill="x", ipady=8, pady=(4, 0))
        tk.Frame(card, bg=CARAMEL, height=2).pack(fill="x", pady=(0, 16))

        # Password field
        tk.Label(card, text="PASSWORD", font=("Georgia", 9, "bold"),
                 bg=WHITE, fg=COFFEE, anchor="w").pack(fill="x")

        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            card, textvariable=self.password_var,
            show="●", font=FONT_ENTRY, bg=CREAM, fg=BROWNIE,
            relief="flat", bd=0, insertbackground=BROWNIE
        )
        password_entry.pack(fill="x", ipady=8, pady=(4, 0))
        tk.Frame(card, bg=CARAMEL, height=2).pack(fill="x", pady=(0, 20))

        # Error label (hidden by default)
        self.error_var = tk.StringVar()
        self.error_label = tk.Label(
            card, textvariable=self.error_var,
            font=FONT_SMALL, bg=WHITE, fg=ERROR_RED
        )
        self.error_label.pack()

        # Login button — below the card
        btn_frame = tk.Frame(center_container, bg=CREAM)
        btn_frame.pack(side="top", expand=False, padx=50, fill="x", pady=(0, 20))

        self.login_btn = tk.Button(
            btn_frame,
            text="SIGN IN  →",
            font=FONT_BUTTON,
            bg=BROWNIE, fg=WHITE,
            activebackground=COFFEE,
            activeforeground=WHITE,
            relief="flat", bd=0,
            cursor="hand2",
            pady=14,
            command=self._handle_login
        )
        self.login_btn.pack(fill="x")

        # Hover effects
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=COFFEE))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=BROWNIE))

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._handle_login())

        # Footer
        tk.Label(
            self.root,
            text="© 2025 Corner Café System",
            font=FONT_SMALL, bg=CREAM, fg=COFFEE
        ).pack(side="bottom", fill="x", pady=10)

        # Bottom decorative banner
        tk.Frame(self.root, bg=BROWNIE, height=8).pack(side="bottom", fill="x")

        # Focus on username field
        username_entry.focus()

    # ── Login Logic ──────────────────────────────────────────────
    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # Basic validation
        if not username or not password:
            self._show_error("Please fill in all fields.")
            return

        # Verify against CSV
        user = verify_login(username, password)

        if user:
            self._show_error("")
            self.root.destroy()
            self._open_dashboard(user)
        else:
            self._show_error("Invalid username or password.")
            self.password_var.set("")

    def _show_error(self, msg: str):
        self.error_var.set(msg)

    def _open_dashboard(self, user: dict):
        """Launch the dashboard after successful login."""
        import subprocess
        subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(__file__), "dashboard.py"),
             user['username'], user['role']]
        )


# ─── Entry Point ─────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()