from typing import Optional
from decimal import Decimal
from .connection import get_conn

def create_item(
    name: str,
    price: Decimal | float,
    stock: int = 0,
    sku: Optional[str] = None,
    is_active: bool = True,
) -> int:
    """Yangi item yaratadi va id qaytaradi."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO items (name, price, stock, sku, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (name, price, stock, sku, is_active),
        )
        return cur.fetchone()["id"]

def list_items(only_active: bool = False):
    q = "SELECT id, name, price, stock, sku, is_active FROM items"
    if only_active:
        q += " WHERE is_active"
    q += " ORDER BY id;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q)
        return cur.fetchall()

def get_item(item_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, price, stock, sku, is_active FROM items WHERE id=%s;",
            (item_id,),
        )
        return cur.fetchone()

def update_item(item_id: int, **fields) -> int:
    sets, params = [], []
    for k in ("name", "price", "stock", "sku", "is_active"):
        if k in fields and fields[k] is not None:
            sets.append(f"{k}=%s")
            params.append(fields[k])
    if not sets:
        return 0
    params.append(item_id)
    q = f"UPDATE items SET {', '.join(sets)} WHERE id=%s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, tuple(params))
        return cur.rowcount

def delete_item(item_id: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM items WHERE id=%s;", (item_id,))
        return cur.rowcount