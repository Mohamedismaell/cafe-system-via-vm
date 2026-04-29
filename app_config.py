MODULES = {
    "login": {
        "label": "Login",
        "subtitle": "User authentication entry screen",
        "script": "login.py",
        "icon": "🔐",
        "roles": ("admin", "manager", "staff"),
        "dashboard_visible": False,
        "ready": True,
    },
    "dashboard": {
        "label": "Dashboard",
        "subtitle": "Cafe management home screen",
        "script": "dashboard.py",
        "icon": "🏠",
        "roles": ("admin", "manager", "staff"),
        "dashboard_visible": False,
        "ready": True,
    },
    "order": {
        "label": "New Order",
        "subtitle": "Browse menu & place orders",
        "script": "order.py",
        "icon": "🛒",
        "roles": ("admin", "manager", "staff"),
        "dashboard_visible": True,
        "ready": True,
    },
    "inventory": {
        "label": "Inventory",
        "subtitle": "Manage products & prices",
        "script": "inventory.py",
        "icon": "📦",
        "roles": ("admin", "manager"),
        "dashboard_visible": True,
        "ready": True,
    },
    "checkout": {
        "label": "Checkout",
        "subtitle": "Process payment & print bill",
        "script": "checkout_ui.py",
        "icon": "💳",
        "roles": ("admin", "manager", "staff"),
        "dashboard_visible": True,
        "ready": True,
    },
    "attendance": {
        "label": "Attendance",
        "subtitle": "Staff shift clock in/out",
        "script": "attendance.py",
        "icon": "🕐",
        "roles": ("admin", "manager", "staff"),
        "dashboard_visible": True,
        "ready": True,
    },
    "report": {
        "label": "Sales Report",
        "subtitle": "View daily revenue & stats",
        "script": "report.py",
        "icon": "📊",
        "roles": ("admin", "manager"),
        "dashboard_visible": True,
        "ready": True,
    },
}


def get_dashboard_modules(role="admin"):
    return [
        (key, config)
        for key, config in MODULES.items()
        if config["dashboard_visible"] and role in config["roles"]
    ]
