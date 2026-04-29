import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk

from order_store import create_pending_order
from ui_theme import (
    BROWNIE, CARAMEL, COFFEE, CREAM, DANGER, LIGHT_BR, WHITE,
    DATA_DIR, ensure_data_dir,
    FONT_BODY,  FONT_SMALL,
    build_footer, build_header, configure_root, go_back, make_button,
)

MENU_FILE = os.path.join(DATA_DIR, "menu.csv")
CART_FILE = os.path.join(DATA_DIR, "cart.csv")

FONT_ITEM  = ("Georgia", 13, "bold")
FONT_PRICE = ("Georgia", 12, "bold")
FONT_CAT   = ("Georgia", 9)

MENU_FIELDS = ["item_name", "price", "quantity", "category"]


def ensure_menu():
    """Create menu.csv with headers only if it doesn't exist yet."""
    if os.path.exists(MENU_FILE):
        return
    ensure_data_dir()
    with open(MENU_FILE, "w", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=MENU_FIELDS).writeheader()


def load_menu():
    ensure_menu()
    try:
        with open(MENU_FILE, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        return [
            {
                "name":     row["item_name"].strip(),
                "price":    float(row.get("price", 0)),
                "quantity": int(row.get("quantity", 0)),
                "category": row.get("category", "General").strip(),
            }
            for row in rows if row.get("item_name", "").strip()
        ]
    except Exception as exc:
        messagebox.showerror("Error", str(exc))
        return []


def write_cart(cart):
    ensure_data_dir()
    with open(CART_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["item_name", "quantity", "price"])
        for name, data in cart.items():
            writer.writerow([name, data["qty"], data["price"]])


class OrderApp:
    def __init__(self, root, dashboard_window=None, username="Admin", role="admin", navigate=None):
        self.root = root
        self.dash = dashboard_window
        self.username = username
        self.role = role
        self.navigate = navigate
        self.items = load_menu()
        self.cart = {}
        self.sv = tk.StringVar()
        self.sv.trace_add("write", lambda *_: self.render())
        self.cv = tk.StringVar(value="All")
        self.cv.trace_add("write", lambda *_: self.render())

        configure_root(self.root, "Corner Cafe - Order")
        self._build_ui()
        self.render()

    def _build_ui(self):
        build_header(self.root, "CORNER CAFE - New Order")

        toolbar = tk.Frame(self.root, bg=COFFEE, pady=8)
        toolbar.pack(fill="x")
        make_button(toolbar, "Dashboard", BROWNIE, self._back, padx=14, pady=6).pack(side="left", padx=12)

        search_frame = tk.Frame(toolbar, bg=WHITE, highlightthickness=1, highlightbackground=CARAMEL)
        search_frame.pack(side="left", padx=16, ipadx=4, ipady=2)
        tk.Label(search_frame, text="Search", bg=WHITE, fg=COFFEE, font=FONT_BODY).pack(side="left", padx=4)
        tk.Entry(
            search_frame, textvariable=self.sv, bg=WHITE, fg=BROWNIE,
            relief="flat", font=FONT_BODY, width=26, insertbackground=BROWNIE,
        ).pack(side="left", ipady=4, padx=(0, 6))

        categories = ["All"] + sorted({item["category"] for item in self.items})
        ttk.Combobox(toolbar, textvariable=self.cv, values=categories, state="readonly", font=FONT_SMALL, width=14).pack(side="left", padx=4, ipady=3)
        self.badge = tk.Label(toolbar, text="", font=FONT_SMALL, bg=COFFEE, fg=CREAM)
        self.badge.pack(side="right", padx=16)

        body = tk.Frame(self.root, bg=CREAM)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=CREAM)
        left.pack(side="left", fill="both", expand=True, padx=(12, 4), pady=10)
        tk.Label(left, text="Menu", font=("Georgia", 16, "bold"), bg=CREAM, fg=BROWNIE).pack(anchor="w", pady=(0, 6))

        wrap = tk.Frame(left, bg=CREAM)
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, bg=CREAM, highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.sf = tk.Frame(self.canvas, bg=CREAM)
        self.cw = self.canvas.create_window((0, 0), window=self.sf, anchor="nw")
        self.sf.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.cw, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))
        self.canvas.bind_all("<Button-4>",   lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>",   lambda e: self.canvas.yview_scroll(1, "units"))

        right = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        right.pack(side="right", fill="y", padx=(4, 12), pady=10, ipadx=4)

        cart_header = tk.Frame(right, bg=BROWNIE, pady=10)
        cart_header.pack(fill="x")
        tk.Label(cart_header, text="Your Cart", font=("Georgia", 13, "bold"), bg=BROWNIE, fg=CREAM).pack()

        list_wrap = tk.Frame(right, bg=WHITE)
        list_wrap.pack(fill="both", expand=True, padx=8, pady=8)
        csb = tk.Scrollbar(list_wrap, orient="vertical")
        self.cl = tk.Listbox(
            list_wrap, font=FONT_BODY, bg=CREAM, fg=BROWNIE,
            selectbackground=CARAMEL, selectforeground=WHITE,
            relief="flat", bd=0, width=32, activestyle="none",
            yscrollcommand=csb.set,
        )
        csb.config(command=self.cl.yview)
        csb.pack(side="right", fill="y")
        self.cl.pack(fill="both", expand=True)

        tk.Frame(right, bg=CARAMEL, height=2).pack(fill="x", padx=8)
        self.tot = tk.Label(right, text="Total:  0.00 EGP", font=("Georgia", 13, "bold"), bg=WHITE, fg=BROWNIE, pady=8)
        self.tot.pack()

        buttons = tk.Frame(right, bg=WHITE)
        buttons.pack(fill="x", padx=10, pady=(0, 10))
        make_button(buttons, "Save & Send to Checkout", CARAMEL, self._save, pady=9).pack(fill="x", pady=(0, 6))
        make_button(buttons, "Clear Cart", BROWNIE, self._clear, hover=DANGER, pady=9).pack(fill="x")

        build_footer(self.root)

    def render(self):
        for widget in self.sf.winfo_children():
            widget.destroy()
        query    = self.sv.get().lower()
        category = self.cv.get()
        data = [
            item for item in self.items
            if query in item["name"].lower() and (category == "All" or item["category"] == category)
        ]
        self.badge.config(text=f"  {len(data)} item(s)  ")
        if not data:
            tk.Label(self.sf, text="No items found.", font=FONT_BODY, bg=CREAM, fg=COFFEE, pady=30).pack()
            return

        for item in data:
            ok   = item["quantity"] > 0
            card = tk.Frame(self.sf, bg=WHITE, highlightthickness=1, highlightbackground=CARAMEL, padx=18, pady=14)
            card.pack(fill="x", padx=12, pady=6)

            top = tk.Frame(card, bg=WHITE)
            top.pack(fill="x")
            tk.Label(top, text=item["name"], font=FONT_ITEM, bg=WHITE, fg=BROWNIE).pack(side="left")
            tk.Label(top, text=f"  {item['category']}  ", font=FONT_CAT, bg=CARAMEL, fg=WHITE, padx=4, pady=2).pack(side="right")

            info = tk.Frame(card, bg=WHITE)
            info.pack(fill="x", pady=(4, 8))
            tk.Label(info, text=f"{item['price']:.2f} EGP", font=FONT_PRICE, bg=WHITE, fg=COFFEE).pack(side="left")
            
            stock_color = COFFEE if ok else DANGER
            tk.Label(info, text=f"  Stock: {item['quantity']}", font=FONT_CAT, bg=WHITE, fg=stock_color).pack(side="left", padx=10)

            actions = tk.Frame(card, bg=WHITE)
            actions.pack(anchor="w")
            
            btn_state = "normal" if ok else "disabled"
            bg_color = CARAMEL if ok else LIGHT_BR
            make_button(actions, "Add to Cart", bg_color, lambda i=item: self._add(i), state=btn_state, padx=18, pady=6).pack(side="left", padx=(0, 8))
            make_button(actions, "Remove", BROWNIE, lambda i=item: self._rem(i), hover=DANGER, padx=18, pady=6).pack(side="left")

        self.canvas.yview_moveto(0)

    def _add(self, item):
        name = item["name"]
        self.cart.setdefault(name, {"qty": 0, "price": item["price"]})
        self.cart[name]["qty"] += 1
        self._refresh_cart()

    def _rem(self, item):
        name = item["name"]
        if name in self.cart:
            self.cart[name]["qty"] -= 1
            if self.cart[name]["qty"] <= 0:
                del self.cart[name]
        self._refresh_cart()

    def _refresh_cart(self):
        self.cl.delete(0, tk.END)
        total = 0
        for name, data in self.cart.items():
            line_total = data["qty"] * data["price"]
            total += line_total
            self.cl.insert(tk.END, f"  {name}  x{data['qty']}  =  {line_total:.2f} EGP")
        self.tot.config(text=f"Total:  {total:.2f} EGP")

    def _clear(self):
        if self.cart and messagebox.askyesno("Clear", "Remove all items?"):
            self.cart.clear()
            self._refresh_cart()

    def _save(self):
        if not self.cart:
            messagebox.showwarning("Empty", "Add at least one item first.")
            return
        write_cart(self.cart)
        order = create_pending_order(self.cart)
        self.cart.clear()
        self._refresh_cart()
        messagebox.showinfo("Saved", f"Order saved as {order['order_id']}.\nYou can add another order or open Checkout.")

    def _back(self):
        go_back(self.navigate, self.username, self.role, self.root, self.dash)


if __name__ == "__main__":
    root = tk.Tk()
    app = OrderApp(root)
    root.mainloop()
