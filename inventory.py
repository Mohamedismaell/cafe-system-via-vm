import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# ─── Constants ───────────────────────────────────────────────────────────────
MENU_FILE           = os.path.join(os.path.dirname(__file__), "data", "menu.csv")
LOW_STOCK_THRESHOLD = 10

# Colors - Brew & Co. Cafe Theme
BG_DARK    = "#F5F0E8"
BG_CARD    = "#FFFFFF"
BG_ALT     = "#FAF6EF"
ACCENT     = "#7B3F2B"
ACCENT2    = "#A0522D"
TEXT_DARK  = "#3B2314"
TEXT_MUTED = "#8B6555"
SUCCESS    = "#4CAF50"
WARNING    = "#E8A020"
DANGER     = "#C0392B"

FONT_TITLE = ("Georgia", 22, "bold")
FONT_HEAD  = ("Georgia", 11, "bold")
FONT_BODY  = ("Georgia", 11)
FONT_SMALL = ("Georgia", 9)
FONT_BTN   = ("Georgia", 10, "bold")

# ─── CSV Helpers ──────────────────────────────────────────────────────────────

def load_menu():
    items = []
    if not os.path.exists(MENU_FILE):
        return items
    with open(MENU_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            items.append({
                "id":        idx,
                "item_name": row.get("item_name", "").strip(),
                "price":     float(row.get("price", 0) or 0),
                "category":  row.get("category", "General").strip(),
                "quantity":  int(row.get("quantity", 20) or 20),
            })
    return items

def save_menu(items):
    with open(MENU_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item_name", "price", "category", "quantity"])
        writer.writeheader()
        for item in items:
            writer.writerow({
                "item_name": item["item_name"],
                "price":     item["price"],
                "category":  item["category"],
                "quantity":  item["quantity"],
            })

def next_id(items):
    return max((i["id"] for i in items), default=0) + 1

# ─── Main App ─────────────────────────────────────────────────────────────────

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("☕ Corner Cafe — Inventory")
        self.state('zoomed')  # Fullscreen
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        self.items = load_menu()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_table())

        self._build_ui()
        self.refresh_table()
        self.after(500, lambda: self.check_low_stock(startup=True))

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=ACCENT)
        header.pack(fill="x")
        tk.Label(header, text="☕  CORNER CAFE", font=("Georgia", 18, "bold"),
                 bg=ACCENT, fg="white").pack(side="left", padx=20, pady=12)
        tk.Label(header, text="Inventory Manager", font=FONT_SMALL,
                 bg=ACCENT, fg="#E8D5C4").pack(side="left", pady=16)
        self.clock_lbl = tk.Label(header, text="", font=FONT_SMALL,
                                  bg=ACCENT, fg="#E8D5C4")
        self.clock_lbl.pack(side="right", padx=20)
        self._tick()

        # Toolbar
        bar = tk.Frame(self, bg=BG_DARK)
        bar.pack(fill="x", padx=20, pady=12)
        sf = tk.Frame(bar, bg=BG_CARD, highlightthickness=1, highlightbackground=ACCENT)
        sf.pack(side="left")
        tk.Label(sf, text="🔍", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_BODY).pack(side="left", padx=(8, 2))
        tk.Entry(sf, textvariable=self.search_var, bg=BG_CARD, fg=TEXT_DARK,
                 insertbackground=TEXT_DARK, relief="flat", font=FONT_BODY,
                 width=24).pack(side="left", pady=6, padx=(0, 8))

        for label, color, cmd in [
            ("＋ Add",      ACCENT,   self.add_item),
            ("✏ Edit",      ACCENT2,  self.edit_item),
            ("🗑 Delete",    DANGER,   self.delete_item),
            ("⚠ Low Stock", WARNING,  lambda: self.check_low_stock(False)),
        ]:
            tk.Button(bar, text=label, bg=color, fg="white", relief="flat",
                      font=FONT_BTN, padx=14, pady=6, cursor="hand2",
                      activebackground=color, command=cmd).pack(side="left", padx=(10, 0))

        # Stats
        self.stats_frame = tk.Frame(self, bg=BG_DARK)
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 8))

        # Table
        tf = tk.Frame(self, bg=BG_CARD)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        cols = ("ID", "Item Name", "Category", "Quantity", "Price (EGP)", "Status")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, [45, 240, 130, 90, 110, 100]):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=BG_CARD, foreground=TEXT_DARK,
                        fieldbackground=BG_CARD, rowheight=32, font=FONT_BODY)
        style.configure("Treeview.Heading", background=ACCENT, foreground="white",
                        font=FONT_HEAD, relief="flat")
        style.map("Treeview", background=[("selected", ACCENT2)])

        self.tree.tag_configure("low", background="#FAE5E0", foreground=DANGER)
        self.tree.tag_configure("ok",  background=BG_CARD,  foreground=TEXT_DARK)
        self.tree.tag_configure("alt", background=BG_ALT,   foreground=TEXT_DARK)
        self.tree.bind("<Double-1>", lambda e: self.edit_item())

        # Status bar
        self.status_lbl = tk.Label(self, text="", font=FONT_SMALL,
                                   bg=ACCENT, fg="white", anchor="w")
        self.status_lbl.pack(fill="x", side="bottom")

    def _tick(self):
        self.clock_lbl.config(text=datetime.now().strftime("%a %d %b %Y  %H:%M:%S"))
        self.after(1000, self._tick)

    def _update_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        total     = len(self.items)
        low_count = sum(1 for i in self.items if i["quantity"] <= LOW_STOCK_THRESHOLD)
        cats      = len(set(i["category"] for i in self.items))
        val       = sum(i["quantity"] * i["price"] for i in self.items)
        for title, value, color in [
            ("📦 Total Items", str(total),          TEXT_DARK),
            ("⚠ Low Stock",    str(low_count),      DANGER if low_count else SUCCESS),
            ("🏷 Categories",  str(cats),           ACCENT2),
            ("💰 Stock Value", f"EGP {val:,.2f}",  SUCCESS),
        ]:
            card = tk.Frame(self.stats_frame, bg=BG_CARD, padx=16, pady=8)
            card.pack(side="left", padx=(0, 10))
            tk.Label(card, text=title, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
            tk.Label(card, text=value, font=("Georgia", 14, "bold"), bg=BG_CARD, fg=color).pack(anchor="w")

    def refresh_table(self):
        q = self.search_var.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        filtered = [i for i in self.items
                    if q in i["item_name"].lower() or q in i["category"].lower()]
        for idx, item in enumerate(filtered):
            low    = item["quantity"] <= LOW_STOCK_THRESHOLD
            status = "⚠ LOW" if low else "✓ OK"
            tag    = "low" if low else ("alt" if idx % 2 else "ok")
            self.tree.insert("", "end", iid=str(item["id"]),
                             values=(item["id"], item["item_name"], item["category"],
                                     item["quantity"], f"{item['price']:.2f}", status),
                             tags=(tag,))
        self._update_stats()
        low_total = sum(1 for i in self.items if i["quantity"] <= LOW_STOCK_THRESHOLD)
        self.status_lbl.config(
            text=f"   Showing {len(filtered)} of {len(self.items)} items  |  "
                 f"Low stock: {low_total}  |  Threshold ≤ {LOW_STOCK_THRESHOLD}"
        )

    def check_low_stock(self, startup=False):
        low = [i for i in self.items if i["quantity"] <= LOW_STOCK_THRESHOLD]
        if not low:
            if not startup:
                self._show_alert(
                    title="Stock Check",
                    message="All items are well stocked!",
                    icon="info"
                )
            return

        lines = "\n".join(
            f"  • {i['item_name']:28s}→  {i['quantity']} pcs"
            for i in sorted(low, key=lambda x: x["quantity"])
        )
        self._show_alert(
            title="Low Stock Alert",
            message=(f"{len(low)} item(s) need restocking:\n\n"
                     f"{lines}\n\nThreshold: ≤ {LOW_STOCK_THRESHOLD}"),
            icon="warning"
        )

    def _show_alert(self, title, message, icon="info"):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=BG_DARK)
        dialog.resizable(False, False)
        dialog.grab_set()

        banner_color = ACCENT if icon == "info" else WARNING
        icon_text = "ℹ️" if icon == "info" else "⚠"

        header = tk.Frame(dialog, bg=banner_color)
        header.pack(fill="x")
        tk.Label(header, text=f" {icon_text} {title}", font=("Georgia", 14, "bold"),
                 bg=banner_color, fg="white").pack(padx=16, pady=12)

        content = tk.Frame(dialog, bg=BG_CARD, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        tk.Label(content, text=message, font=FONT_BODY, bg=BG_CARD,
                 fg=TEXT_DARK, justify="left", wraplength=420).pack()

        btn_area = tk.Frame(dialog, bg=BG_DARK, pady=16)
        btn_area.pack(fill="x")
        tk.Button(btn_area, text="OK", bg=ACCENT, fg="white",
                  font=FONT_BTN, relief="flat", padx=20, pady=8,
                  cursor="hand2", command=dialog.destroy).pack()

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def add_item(self):
        dlg = ItemDialog(self, "Add New Item")
        self.wait_window(dlg)
        if dlg.result:
            dlg.result["id"] = next_id(self.items)
            self.items.append(dlg.result)
            save_menu(self.items)
            self.refresh_table()
            if dlg.result["quantity"] <= LOW_STOCK_THRESHOLD:
                self._show_alert(
                    title="Low Stock",
                    message=(f"'{dlg.result['item_name']}' added with low quantity "
                             f"({dlg.result['quantity']})!"),
                    icon="warning"
                )

    def edit_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Edit", "Please select an item first.")
            return
        item_id = int(sel[0])
        item = next((i for i in self.items if i["id"] == item_id), None)
        if not item:
            return
        dlg = ItemDialog(self, "Edit Item", prefill=item)
        self.wait_window(dlg)
        if dlg.result:
            dlg.result["id"] = item_id
            idx = next(i for i, x in enumerate(self.items) if x["id"] == item_id)
            self.items[idx] = dlg.result
            save_menu(self.items)
            self.refresh_table()
            if dlg.result["quantity"] <= LOW_STOCK_THRESHOLD:
                self._show_alert(
                    title="Low Stock",
                    message=(f"'{dlg.result['item_name']}' quantity is low "
                             f"({dlg.result['quantity']})!"),
                    icon="warning"
                )

    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Please select an item first.")
            return
        item_id = int(sel[0])
        item = next((i for i in self.items if i["id"] == item_id), None)
        if not item:
            return
        if messagebox.askyesno("Confirm Delete", f"Delete '{item['item_name']}' from menu?"):
            self.items = [i for i in self.items if i["id"] != item_id]
            save_menu(self.items)
            self.refresh_table()

    def _sort(self, col):
        key = {"ID": "id", "Item Name": "item_name", "Category": "category",
               "Quantity": "quantity", "Price (EGP)": "price", "Status": "quantity"}.get(col, "item_name")
        self.items.sort(key=lambda x: x[key])
        self.refresh_table()


# ─── Item Dialog ──────────────────────────────────────────────────────────────

class ItemDialog(tk.Toplevel):
    def __init__(self, parent, title="Item", prefill=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.geometry("440x360")
        self._center(parent)

        tk.Label(self, text=title, font=FONT_TITLE, bg=BG_DARK, fg=ACCENT).pack(pady=(20, 12))

        fields = [
            ("Item Name", "item_name", "str"),
            ("Category",  "category",  "str"),
            ("Quantity",  "quantity",  "int"),
            ("Price",     "price",     "float"),
        ]
        self.entries = {}
        form = tk.Frame(self, bg=BG_DARK)
        form.pack(padx=30, fill="x")

        for label, key, typ in fields:
            row = tk.Frame(form, bg=BG_DARK)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=FONT_HEAD, bg=BG_DARK,
                     fg=TEXT_MUTED, width=11, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=BG_CARD, fg=TEXT_DARK, insertbackground=TEXT_DARK,
                         relief="flat", font=FONT_BODY, highlightthickness=1,
                         highlightbackground=ACCENT)
            e.pack(side="left", fill="x", expand=True, ipady=5, padx=(8, 0))
            if prefill and key in prefill:
                e.insert(0, str(prefill[key]))
            self.entries[key] = (e, typ)

        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(pady=16)
        tk.Button(btn_row, text="💾 Save", bg=ACCENT, fg="white", relief="flat",
                  font=FONT_BTN, padx=20, pady=8, cursor="hand2",
                  command=self._save).pack(side="left", padx=8)
        tk.Button(btn_row, text="✕ Cancel", bg=TEXT_MUTED, fg="white", relief="flat",
                  font=FONT_BTN, padx=20, pady=8, cursor="hand2",
                  command=self.destroy).pack(side="left", padx=8)

    def _center(self, parent):
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - 440) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 360) // 2
        self.geometry(f"+{x}+{y}")

    def _save(self):
        data = {}
        for key, (entry, typ) in self.entries.items():
            val = entry.get().strip()
            if not val:
                messagebox.showerror("Error", f"{key} cannot be empty!")
                return
            try:
                if typ == "int":
                    val = int(val)
                    if val < 0: raise ValueError
                elif typ == "float":
                    val = float(val)
                    if val < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {key}!")
                return
            data[key] = val
        self.result = data
        self.destroy()


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()