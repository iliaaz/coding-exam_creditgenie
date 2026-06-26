import sqlite3
from pathlib import Path
from typing import Any

from order_history.seed_data import SEED_ORDERS

_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    status TEXT NOT NULL,
    total REAL NOT NULL,
    items INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT,
    refund_reason TEXT,
    note TEXT
);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database(db_path: Path) -> None:
    """Create schema and preload customer order data for testing."""
    with connect(db_path) as connection:
        connection.executescript(_SCHEMA)
        row = connection.execute("SELECT COUNT(*) FROM orders").fetchone()
        if row is not None and int(row[0]) > 0:
            return
        connection.executemany(
            """
            INSERT INTO orders (
                id, customer_id, status, total, items,
                created_at, delivered_at, refund_reason, note
            ) VALUES (
                :id, :customer_id, :status, :total, :items,
                :created_at, :delivered_at, :refund_reason, :note
            )
            """,
            [_order_row(order) for order in SEED_ORDERS],
        )
        connection.commit()


def _order_row(order: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": order["id"],
        "customer_id": order["customer_id"],
        "status": order["status"],
        "total": order["total"],
        "items": order["items"],
        "created_at": order["created_at"],
        "delivered_at": order.get("delivered_at"),
        "refund_reason": order.get("refund_reason"),
        "note": order.get("note"),
    }
