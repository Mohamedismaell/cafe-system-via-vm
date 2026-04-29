import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# ─── Color Palette ───────────────────────────────────────────────
CREAM    = "#F3E9DC"
CARAMEL  = "#C08552"
BROWNIE  = "#5E3023"
COFFEE   = "#895737"
WHITE    = "#FFFFFF"
LIGHT_BR = "#D4A96A"

# ─── Font Definitions ────────────────────────────────────────────
FONT_TITLE   = ("Georgia", 22, "bold")
FONT_SUBTITLE= ("Georgia", 10, "italic")
FONT_BTN_ICON= ("Segoe UI Emoji", 26)
FONT_BTN_LBL = ("Georgia", 11, "bold")
FONT_BTN_SUB = ("Georgia", 8)
FONT_WELCOME = ("Georgia", 12)
FONT_SMALL   = ("Georgia", 9)

BASE_DIR = os.path.dirname(__file__)


def launch_script(script_name: str):
    """Launch a script as a separate process."""
    path = os.path.join(BASE_DIR, script_name)
    if os.path.exists(path):
        subprocess.Popen([sys.executable, path])
    else:
        messagebox.showwarning(
            "Not Ready",
            f"'{script_name}' is not available yet.\nPlease check back later."
        )


class DashboardApp:
    def __init__(self, root, username="Admin", role="admin"):
        self.root = root
        self.username = username
        self.role = role

        self.root.title("Café System — Dashboard")
        self.root.state('zoomed')
        self.root.configure(bg=CREAM)

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────
    def _build_ui(self):
        # Top decorative banner
        tk.Frame(self.root, bg=BROWNIE, height=8).pack(fill="x")

        # Header section
        header = tk.Frame(self.root, bg=BROWNIE, pady=20)
        header.pack(fill="x")

        tk.Label(
            header, text="☕  CORNER CAFÉ",
            font=FONT_TITLE,
            bg=BROWNIE, fg=CREAM
        ).pack()

        tk.Label(
            header,
            text="Café Management Dashboard",
            font=FONT_SUBTITLE,
            bg=BROWNIE, fg=CARAMEL
        ).pack(pady=(2, 0))

        # Caramel divider
        tk.Frame(self.root, bg=CARAMEL, height=4).pack(fill="x")

        # Welcome bar
        welcome_bar = tk.Frame(self.root, bg=COFFEE, pady=8)
        welcome_bar.pack(fill="x")

        tk.Label(
            welcome_bar,
            text=f"👤  Welcome, {self.username.upper()}   |   Role: {self.role.capitalize()}",
            font=FONT_WELCOME,
            bg=COFFEE, fg=CREAM
        ).pack()

        # Subtitle
        tk.Label(
            self.root,
            text="Select a module to get started",
            font=FONT_SUBTITLE,
            bg=CREAM, fg=COFFEE
        ).pack(pady=(18, 5))

        # ── Button Grid ──────────────────────────────────────────
        # Each tuple: (emoji, label, sublabel, script, always_visible)
        modules = [
            ("🛒", "New Order",     "Browse menu & place orders",  "order.py",      True),
            ("📦", "Inventory",     "Manage products & prices",    "inventory.py",  True),
            ("💳", "Checkout",      "Process payment & print bill","checkout.py",   True),
            ("🕐", "Attendance",    "Staff shift clock in/out",    "attendance.py", True),
            ("📊", "Sales Report",  "View daily revenue & stats",  "report.py",     True),
        ]

        grid_frame = tk.Frame(self.root, bg=CREAM, padx=30)
        grid_frame.pack(fill="both", expand=True, pady=10)

        # 2-column grid
        for i, (icon, label, sublabel, script, _) in enumerate(modules):
            row = i // 2
            col = i % 2
            is_sales_report = label == "Sales Report"

            btn_outer = tk.Frame(
                grid_frame, bg=BROWNIE,
                padx=2, pady=2
            )
            btn_outer.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            btn_inner = tk.Frame(btn_outer, bg=WHITE, cursor="hand2")
            btn_inner.pack(fill="both", expand=True)

            # Icon
            icon_lbl = tk.Label(
                btn_inner, text=icon,
                font=(FONT_BTN_ICON[0], 32 if is_sales_report else FONT_BTN_ICON[1]),
                bg=WHITE, fg=BROWNIE,
                pady=16 if is_sales_report else 12
            )
            icon_lbl.pack()

            # Label
            name_lbl = tk.Label(
                btn_inner, text=label,
                font=(FONT_BTN_LBL[0], 14 if is_sales_report else FONT_BTN_LBL[1], FONT_BTN_LBL[2]),
                bg=WHITE, fg=BROWNIE
            )
            name_lbl.pack()

            # Sublabel
            sub_lbl = tk.Label(
                btn_inner, text=sublabel,
                font=(FONT_BTN_SUB[0], 10 if is_sales_report else FONT_BTN_SUB[1]),
                bg=WHITE, fg=COFFEE,
                wraplength=300 if is_sales_report else 170,
                pady=10 if is_sales_report else 6
            )
            sub_lbl.pack()

            # Bind click & hover to all widgets inside the card
            widgets = [btn_inner, icon_lbl, name_lbl, sub_lbl]
            for w in widgets:
                w.bind("<Button-1>", lambda e, s=script: launch_script(s))
                w.bind("<Enter>",    lambda e, f=btn_inner, o=btn_outer, il=icon_lbl, nl=name_lbl, sl=sub_lbl:
                       self._hover_on(f, o, il, nl, sl))
                w.bind("<Leave>",    lambda e, f=btn_inner, o=btn_outer, il=icon_lbl, nl=name_lbl, sl=sub_lbl:
                       self._hover_off(f, o, il, nl, sl))

        # Make grid columns equal width
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # If odd number of modules, make the last one (Sales Report) bigger
        if len(modules) % 2 != 0:
            last_row = (len(modules) - 1) // 2
            for widget in grid_frame.grid_slaves(row=last_row):
                if widget.grid_info()['column'] == 0:
                    widget.grid_configure(columnspan=2, sticky="ew")

        # ── Footer ───────────────────────────────────────────────
        footer = tk.Frame(self.root, bg=BROWNIE, pady=8)
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="© 2025 Corner Café System  |  All rights reserved",
            font=FONT_SMALL, bg=BROWNIE, fg=CARAMEL
        ).pack()

        # Logout button inside footer
        logout_btn = tk.Button(
            footer,
            text="🚪 Logout",
            font=("Georgia", 9, "bold"),
            bg=COFFEE, fg=WHITE,
            activebackground=CARAMEL,
            activeforeground=BROWNIE,
            relief="flat", bd=0,
            padx=12, pady=4,
            cursor="hand2",
            command=self._logout
        )
        logout_btn.pack(pady=(6, 0))
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg=CARAMEL, fg=BROWNIE))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg=COFFEE,  fg=WHITE))

    # ── Hover Effects ────────────────────────────────────────────
    def _hover_on(self, frame, outer, icon_lbl, name_lbl, sub_lbl):
        outer.config(bg=CARAMEL)
        frame.config(bg=BROWNIE)
        for w in [icon_lbl, name_lbl, sub_lbl]:
            w.config(bg=BROWNIE, fg=CREAM)

    def _hover_off(self, frame, outer, icon_lbl, name_lbl, sub_lbl):
        outer.config(bg=BROWNIE)
        frame.config(bg=WHITE)
        icon_lbl.config(bg=WHITE, fg=BROWNIE)
        name_lbl.config(bg=WHITE, fg=BROWNIE)
        sub_lbl.config(bg=WHITE,  fg=COFFEE)

    # ── Logout ───────────────────────────────────────────────────
    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "login.py")])


# ─── Entry Point ─────────────────────────────────────────────────
if __name__ == "__main__":
    # Accept optional args: username, role (passed from login.py)
    username = sys.argv[1] if len(sys.argv) > 1 else "Admin"
    role     = sys.argv[2] if len(sys.argv) > 2 else "admin"

    root = tk.Tk()
    app = DashboardApp(root, username, role)
    root.mainloop()