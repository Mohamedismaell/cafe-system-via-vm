import csv
import os
import tkinter as tk
from datetime import datetimeS
from tkinter import messagebox, ttk

from auth import get_user_full_names
from ui_theme import (
    BROWNIE, CARAMEL, COFFEE, CREAM, SUCCESS, WHITE,
    DATA_DIR, ensure_data_dir,
    FONT_BODY, FONT_LABEL, FONT_SMALL,
    build_footer, build_header, configure_root, go_back, make_button,
)

ATTENDANCE_FILE    = os.path.join(DATA_DIR, "data/attendance.csv")
ATTENDANCE_HEADERS = ["staff_name", "date", "clock_in", "clock_out", "worked_hours", "status"]


def ensure_attendance_file():
    ensure_data_dir()
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(ATTENDANCE_HEADERS)


def load_attendance():
    ensure_attendance_file()
    with open(ATTENDANCE_FILE, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save_attendance(rows):
    ensure_attendance_file()
    with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ATTENDANCE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def calculate_hours(date_text, clock_in_text, clock_out_text):
    fmt = "%Y-%m-%d %H:%M:%S"
    clock_in  = datetime.strptime(f"{date_text} {clock_in_text}",  fmt)
    clock_out = datetime.strptime(f"{date_text} {clock_out_text}", fmt)
    seconds = max(0, int((clock_out - clock_in).total_seconds()))
    return f"{seconds / 3600:.2f}"


class AttendanceApp:
    def __init__(self, root, dashboard_window=None, username="Admin", role="admin", navigate=None):
        self.root = root
        self.dash = dashboard_window
        self.username = username
        self.role = role
        self.navigate = navigate

        self.staff_names  = get_user_full_names() or [username]
        default_staff     = username if username in self.staff_names else self.staff_names[0]
        self.staff_var    = tk.StringVar(value=default_staff)
        self.time_var     = tk.StringVar()
        self.rows         = load_attendance()

        configure_root(self.root, "Corner Cafe - Attendance")
        self._build_ui()
        self._refresh_table()
        self._tick()

    def _build_ui(self):
        build_header(self.root, "CORNER CAFE - Staff Timeclock")

        toolbar = tk.Frame(self.root, bg=COFFEE, pady=8)
        toolbar.pack(fill="x")
        make_button(toolbar, "Back to Dashboard", BROWNIE, self._back, padx=14, pady=6).pack(side="left", padx=12)
        tk.Label(toolbar, textvariable=self.time_var, font=FONT_BODY, bg=COFFEE, fg=CREAM).pack(side="right", padx=16)

        body = tk.Frame(self.root, bg=CREAM)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        # Clock-in/out control card
        ctrl = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL, padx=18, pady=18)
        ctrl.pack(fill="x", pady=(0, 10))

        tk.Label(ctrl, text="Staff Member", font=FONT_SMALL, bg=WHITE, fg=COFFEE).grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            ctrl, textvariable=self.staff_var, values=self.staff_names,
            state="readonly", font=FONT_BODY, width=18,
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        make_button(ctrl, "Clock In",  CARAMEL, self._clock_in,  padx=16, pady=7).grid(row=1, column=1, padx=(18, 8), sticky="w")
        make_button(ctrl, "Clock Out", COFFEE,  self._clock_out, padx=16, pady=7).grid(row=1, column=2, sticky="w")

        # Attendance table card
        table_card = tk.Frame(body, bg=WHITE, highlightthickness=2, highlightbackground=CARAMEL)
        table_card.pack(fill="both", expand=True)

        table_hdr = tk.Frame(table_card, bg=BROWNIE, pady=10)
        table_hdr.pack(fill="x")
        tk.Label(table_hdr, text="Today's Attendance", font=FONT_LABEL, bg=BROWNIE, fg=CREAM).pack()

        table_wrap = tk.Frame(table_card, bg=WHITE)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=12)

        columns = ("staff_name", "clock_in", "clock_out", "worked_hours", "status")
        self.table = ttk.Treeview(table_wrap, columns=columns, show="headings", height=16)
        col_cfg = {
            "staff_name":   ("Staff",       160),
            "clock_in":     ("Clock In",    160),
            "clock_out":    ("Clock Out",   160),
            "worked_hours": ("Hours",       120),
            "status":       ("Status",      120),
        }
        for key, (label, width) in col_cfg.items():
            self.table.heading(key, text=label)
            self.table.column(key, width=width, anchor="center")

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        build_footer(self.root)

    def _tick(self):
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self._tick)

    def _today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _selected_staff(self):
        return self.staff_var.get().strip()

    def _open_shift(self, staff_name):
        return next(
            (row for row in reversed(self.rows) if row["staff_name"] == staff_name and row["status"] == "Open"),
            None,
        )

    def _clock_in(self):
        staff_name = self._selected_staff()
        if not staff_name:
            messagebox.showwarning("Missing Staff", "Please choose a staff member.")
            return
        if self._open_shift(staff_name):
            messagebox.showwarning("Open Shift", f"{staff_name} already has an open shift.")
            return
        now = datetime.now()
        self.rows.append({
            "staff_name":   staff_name,
            "date":         now.strftime("%Y-%m-%d"),
            "clock_in":     now.strftime("%H:%M:%S"),
            "clock_out":    "",
            "worked_hours": "",
            "status":       "Open",
        })
        save_attendance(self.rows)
        self._refresh_table()

    def _clock_out(self):
        staff_name = self._selected_staff()
        if not staff_name:
            messagebox.showwarning("Missing Staff", "Please choose a staff member.")
            return
        row = self._open_shift(staff_name)
        if not row:
            messagebox.showwarning("No Open Shift", f"{staff_name} does not have an open shift.")
            return
        now = datetime.now()
        row["clock_out"]    = now.strftime("%H:%M:%S")
        row["worked_hours"] = calculate_hours(row["date"], row["clock_in"], row["clock_out"])
        row["status"]       = "Closed"
        save_attendance(self.rows)
        self._refresh_table()

    def _refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for row in reversed([r for r in self.rows if r["date"] == self._today()]):
            self.table.insert("", "end", values=(
                row["staff_name"],
                row["clock_in"],
                row["clock_out"]    or "-",
                row["worked_hours"] or "-",
                row["status"],
            ))

    def _back(self):
        go_back(self.navigate, self.username, self.role, self.root, self.dash)


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
