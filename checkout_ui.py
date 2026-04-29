
import tkinter as tk
from tkinter import messagebox

from order_store import load_pending_orders, save_pending_orders
from sales_store import append_sale
from ui_theme import (
    BROWNIE, CARAMEL, COFFEE, CREAM, DANGER, DISABLED, LIGHT_BR, SUCCESS, WHITE,
    FONT_BODY, FONT_LABEL, FONT_SMALL, FONT_TOTAL,
    build_footer, build_header, configure_root, go_back, make_button,
)


class CheckoutApp:
    def __init__(self, root, dashboard_window=None, username="Admin", role="admin", navigate=None):
        self.root      = root
        self.dash      = dashboard_window
        self.username  = username
        self.role      = role
        self.navigate  = navigate
        self.orders    = load_pending_orders()
        self.selected_order_id   = None
        self.selected_list_name  = "active"

        self.cash_var          = tk.StringVar()
        self.cash_var.trace_add("write", lambda *_: self._update_summary())
        self.order_var         = tk.StringVar(value="No order selected")
        self.summary_var       = tk.StringVar(value="0 item(s)")
        self.subtotal_var      = tk.StringVar(value="0.00 EGP")
        self.paid_var          = tk.StringVar(value="0.00 EGP")
        self.balance_label_var = tk.StringVar(value="Remaining")
        self.change_var        = tk.StringVar(value="0.00 EGP")
        self.status_var        = tk.StringVar(value="")

        configure_root(self.root, "Corner Cafe - Checkout")
        self._build_ui()
        self._render_orders()
        self._update_summary()

    # widget builders 

    def _make_order_list(self, parent, select_bg):
        """Scrollable Listbox inside *parent*; returns the Listbox."""
        scroll  = tk.Scrollbar(parent, orient="vertical")
        listbox = tk.Listbox(
            parent,
            font=FONT_BODY, bg=CREAM, fg=BROWNIE,
            selectbackground=select_bg, selectforeground=WHITE,
            relief="flat", bd=0, width=28, activestyle="none",
            yscrollcommand=scroll.set,
        )
        scroll.config(command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.pack(fill="both", expand=True)
        return listbox

    def _panel(self, parent, title):
        """Titled card panel; returns its inner content frame."""
        wrap   = tk.Frame(parent, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        wrap.pack(side="left", fill="both", expand=True)
        header = tk.Frame(wrap, bg=BROWNIE, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=title, font=FONT_LABEL, bg=BROWNIE, fg=CREAM).pack()
        inner  = tk.Frame(wrap, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=8, pady=8)
        return inner

    #  UI build 

    def _build_ui(self):
        build_header(self.root, "CORNER CAFE - Checkout")

        toolbar = tk.Frame(self.root, bg=COFFEE, pady=8)
        toolbar.pack(fill="x")
        make_button(toolbar, "Back to Dashboard", BROWNIE, self._back,          padx=14, pady=6).pack(side="left", padx=12)
        make_button(toolbar, "Refresh Orders",    CARAMEL, self._reload_orders, padx=14, pady=6).pack(side="left", padx=6)
        tk.Label(toolbar, text="Select a saved order, then apply full or partial cash payments.",
                 font=FONT_SMALL, bg=COFFEE, fg=CREAM).pack(side="left", padx=6)

        body = tk.Frame(self.root, bg=CREAM)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        self._build_order_lists(body)
        self._build_items_canvas(body)
        self._build_payment_panel(body)

        build_footer(self.root)

    def _build_order_lists(self, body):
        left = tk.Frame(body, bg=CREAM)
        left.pack(side="left", fill="y", padx=(0, 8))

        active_inner = self._panel(left, "Saved Orders")
        self.order_list = self._make_order_list(active_inner, CARAMEL)
        self.order_list.bind("<<ListboxSelect>>", self._select_active_order)

        paid_inner = self._panel(left, "Paid Orders")
        self.paid_list = self._make_order_list(paid_inner, SUCCESS)
        self.paid_list.bind("<<ListboxSelect>>", self._select_paid_order)

    def _build_items_canvas(self, body):
        middle = tk.Frame(body, bg=CREAM)
        middle.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(middle, textvariable=self.order_var, font=("Georgia", 16, "bold"), bg=CREAM, fg=BROWNIE).pack(anchor="w", pady=(0, 8))

        wrap = tk.Frame(middle, bg=CREAM)
        wrap.pack(fill="both", expand=True)
        self.canvas      = tk.Canvas(wrap, bg=CREAM, highlightthickness=0)
        items_scroll     = tk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=items_scroll.set)
        items_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.items_frame  = tk.Frame(self.canvas, bg=CREAM)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw")
        self.items_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",      lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def _build_payment_panel(self, body):
        right = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        right.pack(side="right", fill="y", ipadx=4)

        hdr = tk.Frame(right, bg=BROWNIE, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Payment Summary", font=FONT_LABEL, bg=BROWNIE, fg=CREAM).pack()

        sb = tk.Frame(right, bg=WHITE)
        sb.pack(fill="both", expand=True, padx=14, pady=12)

        def _row(label, var, font=FONT_SMALL, fg=COFFEE):
            tk.Label(sb, text=label, font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(anchor="w")
            tk.Label(sb, textvariable=var, font=font, bg=WHITE, fg=fg).pack(anchor="w", pady=(0, 10))

        _row("Items",        self.summary_var,  FONT_BODY,  BROWNIE)
        _row("Order Total",  self.subtotal_var, FONT_TOTAL, BROWNIE)
        _row("Already Paid", self.paid_var,     FONT_TOTAL, SUCCESS)

        tk.Frame(sb, bg=CARAMEL, height=2).pack(fill="x", pady=(2, 12))
        tk.Label(sb, text="Cash Received Now", font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(anchor="w")
        self.cash_entry = tk.Entry(
            sb, textvariable=self.cash_var, font=FONT_BODY,
            bg=CREAM, fg=BROWNIE, relief="flat", insertbackground=BROWNIE, width=22,
        )
        self.cash_entry.pack(fill="x", ipady=7, pady=(0, 12))
        tk.Label(sb, textvariable=self.balance_label_var, font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(anchor="w")
        tk.Label(sb, textvariable=self.change_var,        font=FONT_TOTAL, bg=WHITE, fg=BROWNIE).pack(anchor="w", pady=(0, 12))
        tk.Label(sb, textvariable=self.status_var,        font=FONT_SMALL, bg=WHITE, fg=DANGER,
                 justify="left", wraplength=260).pack(anchor="w", pady=(6, 0))

        actions = tk.Frame(sb, bg=WHITE)
        actions.pack(fill="x", pady=(18, 0))
        self.confirm_btn = make_button(actions, "Apply Payment",      COFFEE,  self._confirm_payment, pady=8)
        self.confirm_btn.pack(fill="x", pady=(0, 6))
        self.clear_btn   = make_button(actions, "Clear Selected Order", BROWNIE, self._clear_order, hover=DANGER, pady=8)
        self.clear_btn.pack(fill="x")

    #  load orders 

    def _reload_orders(self):
        self.orders = load_pending_orders()
        self.selected_order_id  = None
        self.selected_list_name = "active"
        self.cash_var.set("")
        self._render_orders()
        self._render_items()
        self._update_summary()

    def _render_orders(self):
        self.order_list.delete(0, tk.END)
        self.paid_list.delete(0, tk.END)
        self.active_order_ids = []
        self.paid_order_ids   = []
        for order in self.orders:
            if order["status"] == "Paid":
                self.paid_list.insert(tk.END, f"{order['order_id']} | Paid | {order['total_amount']:.2f}")
                self.paid_order_ids.append(order["order_id"])
            else:
                self.order_list.insert(tk.END, f"{order['order_id']} | {order['status']} | Due {order['balance_due']:.2f}")
                self.active_order_ids.append(order["order_id"])
        self._restore_selection()

    def _restore_selection(self):
        self.order_list.selection_clear(0, tk.END)
        self.paid_list.selection_clear(0, tk.END)
        if not self.selected_order_id:
            return
        if self.selected_list_name == "paid" and self.selected_order_id in self.paid_order_ids:
            idx = self.paid_order_ids.index(self.selected_order_id)
            self.paid_list.selection_set(idx)
            self.paid_list.see(idx)
        elif self.selected_order_id in self.active_order_ids:
            idx = self.active_order_ids.index(self.selected_order_id)
            self.order_list.selection_set(idx)
            self.order_list.see(idx)
        elif self.selected_order_id in self.paid_order_ids:
            self.selected_list_name = "paid"
            idx = self.paid_order_ids.index(self.selected_order_id)
            self.paid_list.selection_set(idx)
            self.paid_list.see(idx)

    def _selected_order(self):
        return next((o for o in self.orders if o["order_id"] == self.selected_order_id), None)

    def _select_active_order(self, _event=None):
        sel = self.order_list.curselection()
        if not sel:
            return
        self.paid_list.selection_clear(0, tk.END)
        self.selected_list_name = "active"
        self.selected_order_id  = self.active_order_ids[sel[0]]
        self.cash_var.set("")
        self._render_items()
        self._update_summary()

    def _select_paid_order(self, _event=None):
        sel = self.paid_list.curselection()
        if not sel:
            return
        self.order_list.selection_clear(0, tk.END)
        self.selected_list_name = "paid"
        self.selected_order_id  = self.paid_order_ids[sel[0]]
        self.cash_var.set("")
        self._render_items()
        self._update_summary()

    def _render_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        order = self._selected_order()
        if not order:
            self.order_var.set("No order selected")
            empty = tk.Frame(self.items_frame, bg=WHITE, highlightthickness=1, highlightbackground=CARAMEL, padx=18, pady=18)
            empty.pack(fill="x", padx=8, pady=8)
            tk.Label(empty, text="Select a saved order from the left.", font=FONT_LABEL, bg=WHITE, fg=BROWNIE).pack(anchor="w")
            return
        self.order_var.set(f"Order {order['order_id']}  |  {order['created_at']}  |  {order['status']}")
        for item in order["items"]:
            card = tk.Frame(self.items_frame, bg=WHITE, highlightthickness=1, highlightbackground=CARAMEL, padx=18, pady=14)
            card.pack(fill="x", padx=8, pady=6)
            top = tk.Frame(card, bg=WHITE)
            top.pack(fill="x")
            tk.Label(top, text=item["name"],                        font=FONT_LABEL, bg=WHITE, fg=BROWNIE).pack(side="left")
            tk.Label(top, text=f"{item['price']:.2f} EGP each",    font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(side="right")
            tk.Label(card, text=f"Qty: {item['quantity']}  |  Line Total: {item['quantity'] * item['price']:.2f} EGP",
                     font=FONT_BODY, bg=WHITE, fg=BROWNIE).pack(anchor="w", pady=(8, 0))

    #  payment  

    def _parse_cash(self):
        raw = self.cash_var.get().strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _disable_btn(self, btn):
        btn.config(state="disabled", bg=DISABLED, activebackground=DISABLED)

    def _enable_btn(self, btn, bg, hover):
        btn.config(state="normal", bg=bg, activebackground=hover)

    def _update_summary(self):
        order = self._selected_order()
        if not order:
            self.summary_var.set("0 item(s)")
            self.subtotal_var.set("0.00 EGP")
            self.paid_var.set("0.00 EGP")
            self.balance_label_var.set("Remaining")
            self.change_var.set("0.00 EGP")
            self.status_var.set("Choose an order to review or pay.")
            self._disable_btn(self.confirm_btn)
            self._disable_btn(self.clear_btn)
            return

        item_count = sum(item["quantity"] for item in order["items"])
        self.summary_var.set(f"{item_count} item(s)")
        self.subtotal_var.set(f"{order['total_amount']:.2f} EGP")
        self.paid_var.set(f"{order['amount_paid']:.2f} EGP")
        self._enable_btn(self.clear_btn, BROWNIE, DANGER)

        if order["status"] == "Paid":
            self.balance_label_var.set("Remaining")
            self.change_var.set("0.00 EGP")
            self.status_var.set("This order is fully paid.")
            self._disable_btn(self.confirm_btn)
            return

        cash = self._parse_cash()
        self._enable_btn(self.confirm_btn, COFFEE, LIGHT_BR)

        if cash is None:
            self.balance_label_var.set("Remaining")
            self.change_var.set(f"{order['balance_due']:.2f} EGP")
            self.status_var.set("Enter cash received for this order.")
            return

        if cash < 0:
            self.balance_label_var.set("Remaining")
            self.change_var.set(f"{order['balance_due']:.2f} EGP")
            self.status_var.set("Cash received cannot be negative.")
            self._disable_btn(self.confirm_btn)
            return

        new_balance = order["balance_due"] - cash
        if new_balance > 0:
            self.balance_label_var.set("Still Due")
            self.change_var.set(f"{new_balance:.2f} EGP")
            self.status_var.set(f"After this payment, customer still owes {new_balance:.2f} EGP.")
        else:
            self.balance_label_var.set("Change Due")
            self.change_var.set(f"{abs(new_balance):.2f} EGP")
            self.status_var.set("This payment will settle the order.")

    def _confirm_payment(self):
        order = self._selected_order()
        if not order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        if order["status"] == "Paid":
            messagebox.showinfo("Already Paid", "This order is already fully paid.")
            return
        cash = self._parse_cash()
        if cash is None or cash < 0:
            messagebox.showwarning("Payment Error", "Enter a valid cash amount before confirming payment.")
            return

        order["amount_paid"] += cash
        order["balance_due"]  = max(0.0, order["total_amount"] - order["amount_paid"])
        order["status"]       = "Paid" if order["balance_due"] <= 0 else "Partial"
        if order["status"] == "Paid" and not order["sale_recorded"]:
            append_sale(order, cash)
            order["sale_recorded"] = True

        save_pending_orders(self.orders)
        paid_now = cash
        self.cash_var.set("")
        self._render_orders()
        self._render_items()
        self._update_summary()

        if order["status"] == "Paid":
            extra = max(0.0, order["amount_paid"] - order["total_amount"])
            messagebox.showinfo("Payment Complete",    f"Order {order['order_id']} is fully paid.\nChange due: {extra:.2f} EGP")
        else:
            messagebox.showinfo("Partial Payment Saved", f"Payment of {paid_now:.2f} EGP saved.\nStill due: {order['balance_due']:.2f} EGP")

    def _clear_order(self):
        order = self._selected_order()
        if not order:
            return
        if not messagebox.askyesno("Clear Order", f"Remove order {order['order_id']} from checkout list?"):
            return
        self.orders = [o for o in self.orders if o["order_id"] != order["order_id"]]
        save_pending_orders(self.orders)
        self.selected_order_id  = None
        self.selected_list_name = "active"
        self.cash_var.set("")
        self._render_orders()
        self._render_items()
        self._update_summary()

    def _back(self):
        go_back(self.navigate, self.username, self.role, self.root, self.dash)
