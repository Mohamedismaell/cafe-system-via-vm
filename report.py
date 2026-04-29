import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from sales_store import SALES_FILE
from ui_theme import (
    BROWNIE, CARAMEL, COFFEE, CREAM, WHITE,
    FONT_BODY, FONT_LABEL, FONT_SMALL, FONT_TOTAL,
    build_footer, build_header, configure_root, go_back, make_button,
)


def load_sales():
    if not os.path.exists(SALES_FILE):
        return []
    with open(SALES_FILE, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class ReportApp:
    def __init__(self, root, dashboard_window=None, username="Admin", role="admin", navigate=None):
        self.root = root
        self.dash = dashboard_window
        self.username = username
        self.role = role
        self.navigate = navigate
        self.sales_rows = load_sales()

        self.date_var        = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.status_var      = tk.StringVar(value="")
        self.revenue_var     = tk.StringVar(value="0.00 EGP")
        self.sales_count_var = tk.StringVar(value="0")
        self.average_var     = tk.StringVar(value="0.00 EGP")
        self.cash_var        = tk.StringVar(value="0.00 EGP")

        configure_root(self.root, "Corner Cafe - Sales Report")
        self._build_ui()
        self._apply_filter()

    def _build_ui(self):
        build_header(self.root, "CORNER CAFE - Sales Report")

        # Toolbar
        toolbar = tk.Frame(self.root, bg=COFFEE, pady=8)
        toolbar.pack(fill="x")
        make_button(toolbar, "Back to Dashboard", BROWNIE, self._back,        padx=14, pady=6).pack(side="left", padx=12)
        tk.Label(toolbar, text="Report Date", font=FONT_SMALL, bg=COFFEE, fg=CREAM).pack(side="left", padx=(8, 4))
        tk.Entry(
            toolbar, textvariable=self.date_var, font=FONT_BODY,
            width=14, relief="flat", bg=WHITE, fg=BROWNIE, insertbackground=BROWNIE,
        ).pack(side="left", ipady=4)
        make_button(toolbar, "Apply", CARAMEL, self._apply_filter, padx=12, pady=5).pack(side="left", padx=8)
        make_button(toolbar, "Today", BROWNIE, self._set_today,    padx=12, pady=5).pack(side="left")

        body = tk.Frame(self.root, bg=CREAM)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        # Summary cards
        summary_grid = tk.Frame(body, bg=CREAM)
        summary_grid.pack(fill="x", pady=(0, 10))
        cards = [
            ("Total Revenue",  self.revenue_var),
            ("Sales Count",    self.sales_count_var),
            ("Average Sale",   self.average_var),
            ("Cash Collected", self.cash_var),
        ]
        for index, (label, var) in enumerate(cards):
            card = tk.Frame(summary_grid, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL, padx=16, pady=14)
            card.grid(row=0, column=index, padx=6, sticky="nsew")
            tk.Label(card, text=label, font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(anchor="w")
            tk.Label(card, textvariable=var, font=FONT_TOTAL, bg=WHITE, fg=BROWNIE).pack(anchor="w", pady=(8, 0))
            summary_grid.columnconfigure(index, weight=1)

        # Sales table
        table_card = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        table_card.pack(fill="both", expand=True)

        table_hdr = tk.Frame(table_card, bg=BROWNIE, pady=10)
        table_hdr.pack(fill="x")
        tk.Label(table_hdr, text="Completed Sales", font=FONT_LABEL, bg=BROWNIE, fg=CREAM).pack()

        table_wrap = tk.Frame(table_card, bg=WHITE)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=12)

        columns = ("time", "sale_id", "items", "total_amount", "cash_received", "change_given")
        self.table = ttk.Treeview(table_wrap, columns=columns, show="headings", height=16)
        col_cfg = {
            "time":          ("Time",          100),
            "sale_id":       ("Sale ID",       180),
            "items":         ("Items",         420),
            "total_amount":  ("Total",         110),
            "cash_received": ("Cash Received", 120),
            "change_given":  ("Change",        110),
        }
        for key, (label, width) in col_cfg.items():
            self.table.heading(key, text=label)
            self.table.column(key, width=width, anchor="center" if key != "items" else "w")

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        tk.Label(body, textvariable=self.status_var, font=FONT_SMALL, bg=CREAM, fg=COFFEE, justify="left").pack(anchor="w", pady=(8, 0))
        build_footer(self.root)

    def _set_today(self):
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self._apply_filter()

    def _rows_for_date(self):
        date = self.date_var.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format for the report date.")
            return None
        return [row for row in self.sales_rows if row.get("date") == date]

    def _money(self, value):
        try:
            return float(value or 0)
        except ValueError:
            return 0.0

    def _apply_filter(self):
        filtered = self._rows_for_date()
        if filtered is None:
            return

        for item in self.table.get_children():
            self.table.delete(item)

        revenue       = sum(self._money(r.get("total_amount"))  for r in filtered)
        cash_collected = sum(self._money(r.get("cash_received")) for r in filtered)
        count         = len(filtered)
        average       = revenue / count if count else 0.0

        self.revenue_var.set(f"{revenue:.2f} EGP")
        self.sales_count_var.set(str(count))
        self.average_var.set(f"{average:.2f} EGP")
        self.cash_var.set(f"{cash_collected:.2f} EGP")

        if not os.path.exists(SALES_FILE):
            self.status_var.set("No sales.csv file found yet. Complete a checkout sale to populate this report.")
            return
        if not filtered:
            self.status_var.set(f"No completed sales found for {self.date_var.get().strip()}.")
            return

        for row in filtered:
            self.table.insert("", "end", values=(
                row.get("time",          "-"),
                row.get("sale_id",       "-"),
                row.get("items",         "-"),
                f"{self._money(row.get('total_amount')):.2f} EGP",
                f"{self._money(row.get('cash_received')):.2f} EGP",
                f"{self._money(row.get('change_given')):.2f} EGP",
            ))
        self.status_var.set(f"Showing {count} sale(s) for {self.date_var.get().strip()}.")

    def _back(self):
        go_back(self.navigate, self.username, self.role, self.root, self.dash)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()
