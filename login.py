import tkinter as tk
from tkinter import messagebox

from auth import authenticate_user, ensure_users_file
from ui_theme import (
    BROWNIE,
    CARAMEL,
    COFFEE,
    CREAM,
    WHITE,
    FONT_BODY,
    FONT_SMALL,
    FONT_TITLE,
    configure_root,
    make_button,
)


class LoginApp:
    def __init__(self, root, username="Guest", role="staff", navigate=None):
        self.root = root
        self.navigate = navigate
        self.username_var = tk.StringVar(value="" if username == "Guest" else username)
        self.password_var = tk.StringVar()

        ensure_users_file()
        configure_root(self.root, "Corner Cafe - Login")
        self._build_ui()

    def _build_ui(self):
        tk.Frame(self.root, bg=BROWNIE, height=8).pack(fill="x")

        wrapper = tk.Frame(self.root, bg=CREAM)
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(wrapper, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL, padx=30, pady=26)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="☕  CORNER CAFE", font=FONT_TITLE, bg=WHITE, fg=BROWNIE).pack(pady=(0, 6))
        tk.Label(card, text="Sign in with your username and password", font=FONT_SMALL, bg=WHITE, fg=COFFEE).pack(pady=(0, 20))

        tk.Label(card, text="Username", font=FONT_SMALL, bg=WHITE, fg=COFFEE, anchor="w").pack(fill="x")
        username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            font=FONT_BODY,
            bg=CREAM,
            fg=BROWNIE,
            relief="flat",
            insertbackground=BROWNIE,
            width=28,
        )
        username_entry.pack(fill="x", ipady=7, pady=(4, 14))

        tk.Label(card, text="Password", font=FONT_SMALL, bg=WHITE, fg=COFFEE, anchor="w").pack(fill="x")
        password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            font=FONT_BODY,
            bg=CREAM,
            fg=BROWNIE,
            relief="flat",
            insertbackground=BROWNIE,
            width=28,
            show="*",
        )
        password_entry.pack(fill="x", ipady=7, pady=(4, 20))

        make_button(card, "Login", CARAMEL, self._login, padx=20, pady=8).pack(fill="x")

        username_entry.focus_set()
        password_entry.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        user = authenticate_user(username, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.password_var.set("")
            return

        if self.navigate:
            self.navigate("dashboard", username=user["full_name"], role=user["role"])


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
