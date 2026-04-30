import csv
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from ui_theme import (
    BG_ALT,
    BROWNIE,
    CARAMEL,
    COFFEE,
    CREAM,
    DANGER,
    FONT_BODY,
    FONT_BUTTON,
    FONT_LABEL,
    FONT_SECTION,
    FONT_SMALL,
    SUCCESS,
    TEXT_DARK,
    TEXT_MUTED,
    WARNING,
    WHITE,
    build_footer,
    build_header,
    configure_root,
    make_button,
)

BASE = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE, "data", "menu.csv")
LOW_STOCK_THRESHOLD = 10


def load_menu():
    if not os.path.exists(MENU_FILE):
        return []
    with open(MENU_FILE, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    items = []
    for index, row in enumerate(rows, start=1):
        items.append(
            {
                "id": index,
                "item_name": row.get("item_name", "").strip(),
                "price": float(row.get("price", 0) or 0),
                "category": row.get("category", "General").strip(),
                "quantity": int(row.get("quantity", 0) or 0),
            }
        )
    return items


def save_menu(items):
    os.makedirs(os.path.dirname(MENU_FILE), exist_ok=True)
    with open(MENU_FILE, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["item_name", "price", "category", "quantity"])
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "item_name": item["item_name"],
                    "price": item["price"],
                    "category": item["category"],
                    "quantity": item["quantity"],
                }
            )


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


class InventoryApp:
    def __init__(self, root, dashboard_window=None, username="Admin", role="admin", navigate=None):
        self.root = root
        self.dash = dashboard_window
        self.username = username
        self.role = role
        self.navigate = navigate
        self.items = load_menu()
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        self.status_var = tk.StringVar()

        configure_root(self.root, "Corner Cafe - Inventory")
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        build_header(self.root, "CORNER CAFE - Inventory", "Inventory Manager")

        toolbar = tk.Frame(self.root, bg=COFFEE, pady=8)
        toolbar.pack(fill="x")
        make_button(toolbar, "Back to Dashboard", BROWNIE, self._back, padx=14, pady=6).pack(side="left", padx=12)
        make_button(toolbar, "Add Item", CARAMEL, self.add_item, padx=14, pady=6).pack(side="left", padx=(6, 0))
        make_button(toolbar, "Edit Item", COFFEE, self.edit_item, padx=14, pady=6).pack(side="left", padx=(6, 0))
        make_button(toolbar, "Delete Item", DANGER, self.delete_item, hover=WARNING, padx=14, pady=6).pack(side="left", padx=(6, 0))
        make_button(toolbar, "Low Stock", WARNING, self.check_low_stock, hover=CARAMEL, padx=14, pady=6).pack(side="left", padx=(6, 0))

        body = tk.Frame(self.root, bg=CREAM)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        search_card = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL, padx=18, pady=14)
        search_card.pack(fill="x", pady=(0, 10))
        tk.Label(search_card, text="Search Menu Items", font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(anchor="w")
        tk.Entry(
            search_card,
            textvariable=self.search_var,
            font=FONT_BODY,
            bg=CREAM,
            fg=TEXT_DARK,
            relief="flat",
            insertbackground=TEXT_DARK,
            width=32,
        ).pack(anchor="w", ipady=7, pady=(6, 0))

        self.stats_frame = tk.Frame(body, bg=CREAM)
        self.stats_frame.pack(fill="x", pady=(0, 10))

        table_card = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=BROWNIE, pady=10)
        table_header.pack(fill="x")
        tk.Label(table_header, text="Inventory List", font=FONT_LABEL, bg=BROWNIE, fg=CREAM).pack()

        table_wrap = tk.Frame(table_card, bg=WHITE)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=12)

        columns = ("id", "item_name", "category", "quantity", "price", "status")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=16)
        labels = {
            "id": "ID",
            "item_name": "Item Name",
            "category": "Category",
            "quantity": "Quantity",
            "price": "Price (EGP)",
            "status": "Status",
        }
        widths = {"id": 60, "item_name": 260, "category": 160, "quantity": 100, "price": 120, "status": 120}
        for key in columns:
            self.tree.heading(key, text=labels[key], command=lambda c=key: self._sort(c))
            self.tree.column(key, width=widths[key], anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=TEXT_DARK, fieldbackground=WHITE, rowheight=32, font=FONT_BODY)
        style.configure("Treeview.Heading", background=BROWNIE, foreground=WHITE, font=FONT_BUTTON, relief="flat")
        style.map("Treeview", background=[("selected", CARAMEL)])

        self.tree.tag_configure("low", background="#FAE5E0", foreground=DANGER)
        self.tree.tag_configure("alt", background=BG_ALT, foreground=TEXT_DARK)
        self.tree.tag_configure("ok", background=WHITE, foreground=TEXT_DARK)
        self.tree.bind("<Double-1>", lambda e: self.edit_item())

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(body, textvariable=self.status_var, font=FONT_SMALL, bg=CREAM, fg=COFFEE, justify="left").pack(anchor="w", pady=(8, 0))
        build_footer(self.root)

    def _update_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        total = len(self.items)
        low_count = sum(1 for item in self.items if item["quantity"] <= LOW_STOCK_THRESHOLD)
        categories = len(set(item["category"] for item in self.items))
        stock_value = sum(item["quantity"] * item["price"] for item in self.items)
        cards = [
            ("Total Items", str(total), TEXT_DARK),
            ("Low Stock", str(low_count), DANGER if low_count else SUCCESS),
            ("Categories", str(categories), CARAMEL),
            ("Stock Value", f"EGP {stock_value:,.2f}", SUCCESS),
        ]
        for label, value, color in cards:
            card = tk.Frame(self.stats_frame, bg=WHITE, highlightthickness=1, highlightbackground=CARAMEL, padx=16, pady=10)
            card.pack(side="left", padx=(0, 10))
            tk.Label(card, text=label, font=FONT_SMALL, bg=WHITE, fg=TEXT_MUTED).pack(anchor="w")
            tk.Label(card, text=value, font=FONT_SECTION, bg=WHITE, fg=color).pack(anchor="w")

    def refresh_table(self):
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        filtered = [
            item for item in self.items
            if query in item["item_name"].lower() or query in item["category"].lower()
        ]
        for index, item in enumerate(filtered):
            low = item["quantity"] <= LOW_STOCK_THRESHOLD
            status = "LOW" if low else "OK"
            tag = "low" if low else ("alt" if index % 2 else "ok")
            self.tree.insert(
                "",
                "end",
                iid=str(item["id"]),
                values=(
                    item["id"],
                    item["item_name"],
                    item["category"],
                    item["quantity"],
                    f"{item['price']:.2f}",
                    status,
                ),
                tags=(tag,),
            )
        self._update_stats()
        low_total = sum(1 for item in self.items if item["quantity"] <= LOW_STOCK_THRESHOLD)
        self.status_var.set(
            f"Showing {len(filtered)} of {len(self.items)} items  |  Low stock: {low_total}  |  Threshold <= {LOW_STOCK_THRESHOLD}"
        )

    def check_low_stock(self):
        low = [item for item in self.items if item["quantity"] <= LOW_STOCK_THRESHOLD]
        if not low:
            messagebox.showinfo("Stock Check", "All items are well stocked.")
            return
        lines = "\n".join(f"- {item['item_name']}: {item['quantity']} pcs" for item in low)
        messagebox.showwarning("Low Stock Alert", f"These items need restocking:\n\n{lines}")

    def _selected_item(self):
        selected = self.tree.selection()
        if not selected:
            return None
        item_id = int(selected[0])
        return next((item for item in self.items if item["id"] == item_id), None)

    def add_item(self):
        dialog = ItemDialog(self.root, "Add Item")
        self.root.wait_window(dialog)
        if dialog.result:
            dialog.result["id"] = next_id(self.items)
            self.items.append(dialog.result)
            save_menu(self.items)
            self.refresh_table()

    def edit_item(self):
        item = self._selected_item()
        if not item:
            messagebox.showinfo("Edit Item", "Please select an item first.")
            return
        dialog = ItemDialog(self.root, "Edit Item", prefill=item)
        self.root.wait_window(dialog)
        if dialog.result:
            dialog.result["id"] = item["id"]
            index = next(i for i, row in enumerate(self.items) if row["id"] == item["id"])
            self.items[index] = dialog.result
            save_menu(self.items)
            self.refresh_table()

    def delete_item(self):
        item = self._selected_item()
        if not item:
            messagebox.showinfo("Delete Item", "Please select an item first.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete '{item['item_name']}' from the menu?"):
            self.items = [row for row in self.items if row["id"] != item["id"]]
            save_menu(self.items)
            self.refresh_table()

    def _sort(self, key):
        self.items.sort(key=lambda item: item[key])
        self.refresh_table()

    def _back(self):
        if self.navigate:
            self.navigate("dashboard", username=self.username, role=self.role)
            return
        self.root.destroy()
        dash = os.path.join(BASE, "dashboard.py")
        if os.path.exists(dash):
            subprocess.Popen([sys.executable, dash])


class ItemDialog(tk.Toplevel):
    def __init__(self, parent, title, prefill=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=CREAM)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text=title, font=FONT_SECTION, bg=CREAM, fg=BROWNIE).pack(pady=(18, 10))

        fields = [
            ("Item Name", "item_name", "str"),
            ("Category", "category", "str"),
            ("Quantity", "quantity", "int"),
            ("Price", "price", "float"),
        ]
        self.entries = {}
        form = tk.Frame(self, bg=CREAM, padx=24, pady=8)
        form.pack(fill="both", expand=True)
        for label, key, data_type in fields:
            row = tk.Frame(form, bg=CREAM)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=FONT_SMALL, bg=CREAM, fg=COFFEE, width=10, anchor="w").pack(side="left")
            entry = tk.Entry(row, font=FONT_BODY, bg=WHITE, fg=TEXT_DARK, relief="flat", insertbackground=TEXT_DARK)
            entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(10, 0))
            if prefill:
                entry.insert(0, str(prefill.get(key, "")))
            self.entries[key] = (entry, data_type)

        buttons = tk.Frame(self, bg=CREAM, pady=16)
        buttons.pack()
        make_button(buttons, "Save", CARAMEL, self._save, padx=18, pady=8).pack(side="left", padx=8)
        make_button(buttons, "Cancel", COFFEE, self.destroy, padx=18, pady=8).pack(side="left", padx=8)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _save(self):
        result = {}
        for key, (entry, data_type) in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Invalid Input", f"{key} cannot be empty.")
                return
            try:
                if data_type == "int":
                    value = int(value)
                    if value < 0:
                        raise ValueError
                elif data_type == "float":
                    value = float(value)
                    if value < 0:
                        raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", f"Invalid value for {key}.")
                return
            result[key] = value
        self.result = result
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
