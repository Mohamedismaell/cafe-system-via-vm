"""
sales_store.py — persistence layer for completed sales (sales.csv).
"""
import csv
import os
from datetime import datetime

from ui_theme import DATA_DIR, ensure_data_dir

SALES_FILE    = os.path.join(DATA_DIR, "sales.csv")
SALES_HEADERS = [
    "sale_id", "date", "time", "items",
    "total_amount", "cash_received", "change_given", "payment_method",
]


def ensure_sales_file():
    ensure_data_dir()
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(SALES_HEADERS)


def append_sale(order, payment_now):
    ensure_sales_file()
    now           = datetime.now()
    item_snapshot = " | ".join(
        f"{item['name']} x{item['quantity']} @ {item['price']:.2f}"
        for item in order["items"]
    )
    change_given  = max(0.0, order["amount_paid"] - order["total_amount"])
    row = [
        order["order_id"],
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        item_snapshot,
        f"{order['total_amount']:.2f}",
        f"{order['amount_paid']:.2f}",
        f"{change_given:.2f}",
        "Cash" if change_given >= 0 else "Cash - Debt",
    ]
    with open(SALES_FILE, "a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(row)
