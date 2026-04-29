# Corner Cafe System

A Tkinter-based cafe management system with a shared module router, login screen, dashboard, inventory, order flow, checkout flow, attendance tracking, and sales reporting.

## Current Modules

- `main.py`: central router and module launcher
- `app_config.py`: shared module registry
- `ui_theme.py`: shared theme constants and reusable UI helpers
- `login.py`: login screen and role entry point
- `dashboard.py`: dashboard built from the shared module registry
- `inventory.py`: manage menu products, stock, and pricing
- `order.py`: create carts from the menu and save them for checkout
- `checkout_ui.py`: process cash payments and save completed sales
- `attendance.py`: staff clock-in / clock-out timeclock
- `report.py`: daily sales summary and completed-sales table

## How To Run

Run the full system from the project root:

```powershell
py main.py
```

You can also open modules directly:

```powershell
py dashboard.py
py inventory.py
py order.py
py checkout_ui.py
py attendance.py
py report.py
```

## Data Flow

- `data/menu.csv`
  - Input file for `order.py`
  - Expected to contain menu items, prices, stock, and categories

- `data/cart.csv`
  - Written by `order.py`
  - Read and updated by `checkout_ui.py`

- `data/sales.csv`
  - Written by `sales_store.py`
  - Read by `report.py`

- `data/attendance.csv`
  - Written and updated by `attendance.py`

The `data/` folder is created automatically by modules that write CSV files. `menu.csv` is still expected to be provided for the order screen to function fully.

## Role Status

- Role 1: Login Window
  - Implemented

- Role 2: Main Dashboard
  - Implemented

- Role 3: Order Window
  - Implemented

- Role 4: Inventory Window
  - Implemented

- Role 5: Checkout Window
  - Implemented

- Role 6: Staff Timeclock
  - Implemented

- Role 7: Sales Report
  - Implemented

## Wiring Notes

- `main.py` now routes navigation inside one app window
- `app_config.py` holds the shared module registry
- `dashboard.py` reads dashboard cards from that registry
- `logout` now returns to `login.py` inside the same app window
- Each module still works as a standalone script
- Shared colors, fonts, and common UI helpers live in `ui_theme.py`
