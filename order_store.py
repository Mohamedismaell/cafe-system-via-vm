import csv
import json
import os
from datetime import datetime

from ui_theme import DATA_DIR, ensure_data_dir

PENDING_ORDERS_FILE    = os.path.join(DATA_DIR, "pending_orders.csv")
PENDING_ORDER_HEADERS  = [
    "order_id", "created_at", "items_json",
    "total_amount", "amount_paid", "balance_due",
    "status", "sale_recorded",
]


def ensure_pending_orders_file():
    ensure_data_dir()
    if not os.path.exists(PENDING_ORDERS_FILE):
        with open(PENDING_ORDERS_FILE, "w", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=PENDING_ORDER_HEADERS).writeheader()


def _cart_to_items(cart):
    return [{"name": name, "quantity": data["qty"], "price": data["price"]} for name, data in cart.items()]


def _items_total(items):
    return sum(item["quantity"] * item["price"] for item in items)


def create_pending_order(cart):
    ensure_pending_orders_file()
    items        = _cart_to_items(cart)
    total_amount = _items_total(items)
    row = {
        "order_id":     datetime.now().strftime("ORD%Y%m%d%H%M%S"),
        "created_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items_json":   json.dumps(items),
        "total_amount": f"{total_amount:.2f}",
        "amount_paid":  "0.00",
        "balance_due":  f"{total_amount:.2f}",
        "status":       "Pending",
        "sale_recorded": "no",
    }
    with open(PENDING_ORDERS_FILE, "a", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=PENDING_ORDER_HEADERS).writerow(row)
    return row


def load_pending_orders():
    ensure_pending_orders_file()
    with open(PENDING_ORDERS_FILE, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    orders = []
    for row in rows:
        try:
            items = json.loads(row.get("items_json", "[]"))
        except json.JSONDecodeError:
            items = []
        orders.append({
            "order_id":      row.get("order_id",    "").strip(),
            "created_at":    row.get("created_at",  "").strip(),
            "items":         items,
            "total_amount":  float(row.get("total_amount", 0) or 0),
            "amount_paid":   float(row.get("amount_paid",  0) or 0),
            "balance_due":   float(row.get("balance_due",  0) or 0),
            "status":        row.get("status", "Pending").strip() or "Pending",
            "sale_recorded": row.get("sale_recorded", "no").strip().lower() == "yes",
        })
    return orders


def save_pending_orders(orders):
    ensure_pending_orders_file()
    with open(PENDING_ORDERS_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PENDING_ORDER_HEADERS)
        writer.writeheader()
        for order in orders:
            writer.writerow({
                "order_id":      order["order_id"],
                "created_at":    order["created_at"],
                "items_json":    json.dumps(order["items"]),
                "total_amount":  f"{order['total_amount']:.2f}",
                "amount_paid":   f"{order['amount_paid']:.2f}",
                "balance_due":   f"{order['balance_due']:.2f}",
                "status":        order["status"],
                "sale_recorded": "yes" if order.get("sale_recorded") else "no",
            })
