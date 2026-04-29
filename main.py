import tkinter as tk

from done.app_config import MODULES


_APP_REGISTRY = {
    "login":      ("login",      "LoginApp"),
    "dashboard":  ("dashboard",  "DashboardApp"),
    "order":      ("order",      "OrderApp"),
    "inventory":  ("inventory",  "InventoryApp"),
    "checkout":   ("checkout_ui","CheckoutApp"),
    "attendance": ("attendance", "AttendanceApp"),
    "report":     ("report",     "ReportApp"),
}


def get_app_class(module_key):
    entry = _APP_REGISTRY.get(module_key)
    if not entry:
        return None
    mod_name, cls_name = entry
    module = __import__(mod_name)
    return getattr(module, cls_name, None)


class AppRouter:
    def __init__(self, root, username="Guest", role="staff"):
        self.root = root
        self.username = username
        self.role = role
        self.current_app = None

    def _clear_root(self):
        for event in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.unbind_all(event)
        for widget in self.root.winfo_children():
            widget.destroy()

    def show(self, module_key, **kwargs):
        config = MODULES.get(module_key)
        if not config or not config["ready"]:
            return False

        self.username = kwargs.pop("username", self.username)
        self.role = kwargs.pop("role", self.role)

        app_class = get_app_class(module_key)
        if app_class is None:
            return False

        self._clear_root()
        self.current_app = app_class(
            self.root,
            username=self.username,
            role=self.role,
            navigate=self.show,
            **kwargs,
        )
        return True


def main():
    root = tk.Tk()
    router = AppRouter(root)
    router.show("login")
    root.mainloop()


if __name__ == "__main__":
    main()
