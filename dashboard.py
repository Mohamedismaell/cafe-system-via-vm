import sys
import tkinter as tk
from tkinter import messagebox

from app_config import get_dashboard_modules
from ui_theme import (
    BROWNIE, CARAMEL, COFFEE, CREAM, DISABLED, WHITE,
    FONT_BTN_ICON, FONT_BTN_LBL, FONT_BTN_SUB, FONT_SMALL, FONT_SUBTITLE, FONT_TITLE, FONT_WELCOME,
    build_footer, configure_root, go_back, make_button,
)


class DashboardApp:
    def __init__(self, root, username="Admin", role="admin", navigate=None):
        self.root = root
        self.username = username
        self.role = role
        self.navigate = navigate
        self.modules = get_dashboard_modules(role)

        configure_root(self.root, "Corner Cafe - Dashboard")
        self._build_ui()

    def _build_ui(self):
        # Header
        tk.Frame(self.root, bg=BROWNIE, height=8).pack(fill="x")
        header = tk.Frame(self.root, bg=BROWNIE, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="☕  CORNER CAFE",         font=FONT_TITLE,    bg=BROWNIE, fg=CREAM).pack()
        tk.Label(header, text="Cafe Management Dashboard", font=FONT_SUBTITLE, bg=BROWNIE, fg=CARAMEL).pack(pady=(2, 0))
        tk.Frame(self.root, bg=CARAMEL, height=4).pack(fill="x")

        # Welcome bar
        welcome = tk.Frame(self.root, bg=COFFEE, pady=8)
        welcome.pack(fill="x")
        tk.Label(
            welcome,
            text=f"Welcome, {self.username.upper()}   |   Role: {self.role.capitalize()}",
            font=FONT_WELCOME, bg=COFFEE, fg=CREAM,
        ).pack()

        tk.Label(self.root, text="Select a module to get started", font=FONT_SUBTITLE, bg=CREAM, fg=COFFEE).pack(pady=(18, 5))

        # Module grid
        grid = tk.Frame(self.root, bg=CREAM, padx=30)
        grid.pack(fill="both", expand=True, pady=10)

        for index, (module_key, module) in enumerate(self.modules):
            row, col  = divmod(index, 2)
            is_wide   = module["label"] == "Sales Report"
            card_bg   = WHITE if module["ready"] else DISABLED

            btn_outer = tk.Frame(grid, bg=BROWNIE, padx=2, pady=2)
            btn_outer.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            btn_inner = tk.Frame(btn_outer, bg=card_bg, cursor="hand2")
            btn_inner.pack(fill="both", expand=True)

            icon_lbl = tk.Label(
                btn_inner,
                text=module["icon"],
                font=(FONT_BTN_ICON[0], 32 if is_wide else FONT_BTN_ICON[1]),
                bg=card_bg,
                fg=BROWNIE if module["ready"] else COFFEE,
                pady=16 if is_wide else 12,
            )
            icon_lbl.pack()

            name_lbl = tk.Label(
                btn_inner,
                text=module["label"],
                font=(FONT_BTN_LBL[0], 14 if is_wide else FONT_BTN_LBL[1], FONT_BTN_LBL[2]),
                bg=card_bg, fg=BROWNIE,
            )
            name_lbl.pack()

            sub_lbl = tk.Label(
                btn_inner,
                text=module["subtitle"],
                font=(FONT_BTN_SUB[0], 10 if is_wide else FONT_BTN_SUB[1]),
                bg=card_bg, fg=COFFEE,
                wraplength=300 if is_wide else 170,
                pady=10 if is_wide else 6,
                justify="center",
            )
            sub_lbl.pack()

            widgets = [btn_inner, icon_lbl, name_lbl, sub_lbl]
            for w in widgets:
                w.bind("<Button-1>", lambda e, k=module_key: self._open(k))
                w.bind("<Enter>",    lambda e, f=btn_inner, o=btn_outer, il=icon_lbl, nl=name_lbl, sl=sub_lbl: self._hover_on(f, o, il, nl, sl))
                w.bind("<Leave>",    lambda e, f=btn_inner, o=btn_outer, il=icon_lbl, nl=name_lbl, sl=sub_lbl, bg=card_bg: self._hover_off(f, o, il, nl, sl, bg))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Centre last card if odd count
        if len(self.modules) % 2 != 0:
            last_row = (len(self.modules) - 1) // 2
            for w in grid.grid_slaves(row=last_row):
                if w.grid_info()["column"] == 0:
                    w.grid_configure(columnspan=2, sticky="ew")

        # Footer with logout
        footer = build_footer(self.root)
        make_button(footer, "Logout", COFFEE, self._logout, hover=CARAMEL, padx=12, pady=4,
                    font=("Georgia", 9, "bold")).pack(pady=(6, 0))

    def _open(self, module_key):
        module = dict(self.modules)[module_key]
        if not module["ready"]:
            messagebox.showwarning("Not Ready", f"'{module['label']}' is planned but not implemented yet.")
            return
        if self.navigate:
            self.navigate(module_key, username=self.username, role=self.role)

    def _hover_on(self, frame, outer, icon_lbl, name_lbl, sub_lbl):
        outer.config(bg=CARAMEL)
        frame.config(bg=BROWNIE)
        for w in (icon_lbl, name_lbl, sub_lbl):
            w.config(bg=BROWNIE, fg=CREAM)

    def _hover_off(self, frame, outer, icon_lbl, name_lbl, sub_lbl, bg):
        outer.config(bg=BROWNIE)
        frame.config(bg=bg)
        icon_lbl.config(bg=bg, fg=BROWNIE if bg == WHITE else COFFEE)
        name_lbl.config(bg=bg, fg=BROWNIE)
        sub_lbl.config(bg=bg, fg=COFFEE)

    def _logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return
        if self.navigate:
            self.navigate("login", username="", role="staff")
        else:
            self.root.destroy()


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Admin"
    role     = sys.argv[2] if len(sys.argv) > 2 else "admin"
    root = tk.Tk()
    app  = DashboardApp(root, username, role)
    root.mainloop()
