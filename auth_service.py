import json
import os
from datetime import datetime
from typing import Dict

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None

from utils.security import hash_password


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
LOGIN_LOG_FILE = os.path.join(BASE_DIR, "login_data.txt")
DEFAULT_USERS = {
    "admin": {
        "password": hash_password("CS499Dash!"),
        "question": "Favorite color?",
        "answer": "blue",
    }
}


class FileUserRepository:
    def __init__(self, users_file: str = USERS_FILE, login_log_file: str = LOGIN_LOG_FILE):
        self.users_file = users_file
        self.login_log_file = login_log_file
        self._ensure_users_file()

    def _ensure_users_file(self) -> None:
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as file:
                json.dump(DEFAULT_USERS, file, indent=2)

    def load_users(self) -> Dict[str, Dict[str, str]]:
        with open(self.users_file, "r", encoding="utf-8") as file:
            users = json.load(file)

        if users and isinstance(next(iter(users.values())), str):
            users = {
                name: {"password": pwd, "question": "Favorite color?", "answer": "blue"}
                for name, pwd in users.items()
            }
            self.save_users(users)

        return users

    def save_users(self, users: Dict[str, Dict[str, str]]) -> None:
        with open(self.users_file, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

    def append_login_attempt(self, username: str, success: bool) -> None:
        with open(self.login_log_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now().isoformat()} | user={username} | success={success}\n")


class PostgresUserRepository:
    table_name = "users"

    def __init__(self, dsn: str, login_log_file: str = LOGIN_LOG_FILE):
        if psycopg is None:
            raise RuntimeError("psycopg is not installed. Install it with 'pip install psycopg[binary]'.")
        self.dsn = dsn
        self.login_log_file = login_log_file
        self._ensure_table()
        self._ensure_default_user()

    def _get_connection(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _ensure_table(self) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL
                    )
                    """
                )
            connection.commit()

    def _ensure_default_user(self) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.table_name} (username, password, question, answer)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                    """,
                    (
                        "admin",
                        DEFAULT_USERS["admin"]["password"],
                        DEFAULT_USERS["admin"]["question"],
                        DEFAULT_USERS["admin"]["answer"],
                    ),
                )
            connection.commit()

    def load_users(self) -> Dict[str, Dict[str, str]]:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT username, password, question, answer FROM {self.table_name} ORDER BY username")
                rows = cursor.fetchall()

        return {
            row["username"]: {
                "password": row["password"],
                "question": row["question"],
                "answer": row["answer"],
            }
            for row in rows
        }

    def save_users(self, users: Dict[str, Dict[str, str]]) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {self.table_name}")
                for username, data in users.items():
                    cursor.execute(
                        f"""
                        INSERT INTO {self.table_name} (username, password, question, answer)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (username, data["password"], data["question"], data["answer"]),
                    )
            connection.commit()

    def append_login_attempt(self, username: str, success: bool) -> None:
        with open(self.login_log_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now().isoformat()} | user={username} | success={success}\n")


def build_user_repository():
    postgres_dsn = os.getenv("POSTGRES_DSN")
    if postgres_dsn:
        try:
            return PostgresUserRepository(postgres_dsn)
        except Exception:
            pass
    return FileUserRepository()
