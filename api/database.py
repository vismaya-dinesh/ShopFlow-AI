
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "shopflow.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                item_name TEXT NOT NULL,
                order_status TEXT NOT NULL,
                order_date TEXT NOT NULL,
                expected_delivery TEXT,
                payment_status TEXT NOT NULL,
                total_amount REAL NOT NULL,
                currency TEXT NOT NULL
            )
        """)

        orders = [
            (
                "ORD-1001", "alex@example.com", "Wireless Headphones",
                "shipped", "2026-10-10", "2026-10-20",
                "paid", 199.99, "AED"
            ),
            (
                "ORD-1002", "sam@example.com", "Running Shoes",
                "delivered", "2026-10-05", "2026-10-12",
                "paid", 249.00, "AED"
            ),
            (
                "ORD-1003", "jamie@example.com", "Laptop Stand",
                "processing", "2026-10-17", None,
                "paid", 89.50, "AED"
            ),
        ]

        connection.executemany("""
            INSERT OR IGNORE INTO orders (
                order_id, customer_email, item_name, order_status,
                order_date, expected_delivery, payment_status,
                total_amount, currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders)


def get_order(order_id: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id.upper(),)
        ).fetchone()

    return dict(row) if row else None
