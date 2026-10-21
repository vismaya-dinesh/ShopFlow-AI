
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

        connection.execute("""
            CREATE TABLE IF NOT EXISTS review_cases (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_message TEXT NOT NULL,
                intent TEXT NOT NULL,
                urgency TEXT NOT NULL,
                requires_human_review INTEGER NOT NULL DEFAULT 1,
                review_status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TEXT
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


def create_review_case(
    customer_message: str,
    intent: str,
    urgency: str,
):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO review_cases (
                customer_message,
                intent,
                urgency,
                requires_human_review,
                review_status
            )
            VALUES (?, ?, ?, 1, 'pending')
        """, (customer_message, intent, urgency))

        review_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM review_cases WHERE review_id = ?",
            (review_id,)
        ).fetchone()

    return dict(row)


def get_review_cases():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM review_cases
            ORDER BY
                CASE review_status
                    WHEN 'pending' THEN 0
                    ELSE 1
                END,
                created_at DESC,
                review_id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def get_review_case(review_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM review_cases WHERE review_id = ?",
            (review_id,)
        ).fetchone()

    return dict(row) if row else None


def mark_review_case_completed(review_id: int):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE review_cases
            SET review_status = 'reviewed',
                reviewed_at = CURRENT_TIMESTAMP
            WHERE review_id = ?
              AND review_status = 'pending'
        """, (review_id,))

        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            "SELECT * FROM review_cases WHERE review_id = ?",
            (review_id,)
        ).fetchone()

    return dict(row)
