import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
USER_HEADERS = ["user_id", "full_name", "username", "password", "role", "phone", "email"]
DEFAULT_USERS = [
    {
        "user_id": "1",
        "full_name": "Amina Hassan",
        "username": "admin",
        "password": "Admin123",
        "role": "admin",
        "phone": "01000000001",
        "email": "admin@cornercafe.local",
    },
    {
        "user_id": "2",
        "full_name": "Karim Ali",
        "username": "manager1",
        "password": "Manager123",
        "role": "manager",
        "phone": "01000000002",
        "email": "manager1@cornercafe.local",
    },
    {
        "user_id": "3",
        "full_name": "Nour Salah",
        "username": "manager2",
        "password": "Manager456",
        "role": "manager",
        "phone": "01000000003",
        "email": "manager2@cornercafe.local",
    },
    {
        "user_id": "4",
        "full_name": "Omar Adel",
        "username": "staff1",
        "password": "Staff123",
        "role": "staff",
        "phone": "01000000004",
        "email": "staff1@cornercafe.local",
    },
    {
        "user_id": "5",
        "full_name": "Mona Youssef",
        "username": "staff2",
        "password": "Staff234",
        "role": "staff",
        "phone": "01000000005",
        "email": "staff2@cornercafe.local",
    },
    {
        "user_id": "6",
        "full_name": "Yara Mahmoud",
        "username": "staff3",
        "password": "Staff345",
        "role": "staff",
        "phone": "01000000006",
        "email": "staff3@cornercafe.local",
    },
    {
        "user_id": "7",
        "full_name": "Hassan Tarek",
        "username": "staff4",
        "password": "Staff456",
        "role": "staff",
        "phone": "01000000007",
        "email": "staff4@cornercafe.local",
    },
]


def ensure_users_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(USERS_FILE):
        return
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=USER_HEADERS)
        writer.writeheader()
        writer.writerows(DEFAULT_USERS)


def load_users():
    ensure_users_file()
    with open(USERS_FILE, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def get_user_full_names():
    return [user["full_name"].strip() for user in load_users() if user.get("full_name", "").strip()]


def authenticate_user(username, password):
    username = username.strip().lower()
    password = password.strip()
    for user in load_users():
        if user["username"].strip().lower() == username and user["password"] == password:
            return user
    return None
