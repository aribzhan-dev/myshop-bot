from .connection import get_conn

def add_item_to_cart(cart_id: int, item_id: int, qty:int):
    if qty <= 0:
        raise ValueError('qty 0 dan kop bolishi kerak')
    with get_conn() as conn, conn.cursor() as cur:
        # Item ma'lumotlari (narx va sklad qoldig‘i)
        cur.execute("SELECT price, stock FROM items WHERE id=%s;", (item_id, ))
        it = cur.fetchone()
        if not it:
            raise ValueError('Item yoq')
        if it['stock'] < qty:
            raise ValueError(f'sklatta yetarli stock yoq')

        #  Shu cartda bu item oldin bormi?
        cur.execute("SELECT id, qty FROM cart_items WHERE cart_id=%s AND item_id=%s;", (cart_id, item_id))
        row = cur.fetchone()
        if row:
            # bor bo‘lsa — qty oshiramiz
            new_qty = row['qty'] + qty
            cur.execute("UPDATE cart_items SET qty=%s WHERE id=%s;", (new_qty, row['id']))
        else:
            # yo‘q bo‘lsa — yangi qatordan qo‘shamiz (unit_price snapshot!)
            cur.execute("INSERT INTO cart_items(cart_id, item_id, qty, unit_price) VALUES (%s, %s, %s, %s);", (cart_id, item_id, qty, it['price']))

def set_item_qty(cart_id: int, item_id: int, qty:int):
    with get_conn() as conn, conn.cursor() as cur:
        if qty <= 0:
            cur.execute("DELETE FROM cart_items WHERE cart_id=%s AND item_id=%s;", (cart_id, item_id))
            return cur.rowcount

        #stock check
        cur.execute("SELECT stock FROM items WHERE id=%s;", (item_id, ))
        it = cur.fetchone()
        if not it or it['stock'] < qty:
            raise ValueError("Stock yetarli emas")
        cur.execute("UPDATE cart_items SET qty=%s WHERE cart_id=%s AND item_id=%s;", (qty, cart_id, item_id))
        return cur.rowcount

def remove_item(cart_id: int, item_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM cart_items WHERE cart_id=%s AND item_id=%s;", (cart_id, item_id))
        return cur.rowcount

def get_cart_detail(cart_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT ci.item_id, i.name, ci.qty, ci.unit_price, (ci.qty*ci.unit_price) AS line_total FROM cart_items ci JOIN items i ON i.id = ci.item_id WHERE ci.cart_id=%s ORDER BY ci.id;", (cart_id, ))
        rows = cur.fetchall()
        total = sum(r['line_total'] for r in rows) if rows else 0
        return rows, total






