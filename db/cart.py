from .connection import get_conn

def get_or_create_active_cart(client_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT id FROM carts WHERE client_id=%s AND status='active' ORDER BY id DESC LIMIT 1;""", (client_id,))
        row = cur.fetchone()
        if row:
            return row['id']
        cur.execute("""INSERT INTO carts(client_id) VALUES(%s) RETURNING id;""", (client_id,))
        return cur.fetchone()['id']

def get_cart(cart_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT * FROM carts WHERE id=%s;""", (cart_id,))
        return cur.fetchone()


def get_cart_total(cart_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT * FROM v_cart_totals WHERE cart_id=%s;""", (cart_id,))
        return cur.fetchone()

def checkout_cart(cart_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM carts WHERE id=%s FOR UPDATE;", (cart_id,))
        cart = cur.fetchone()
        if not cart or cart['status'] != 'active':
            raise ValueError("Cart topilmadi yoki active emas")
        cur.execute("SELECT item_id, qty FROM cart_items WHERE cart_id=%s FOR UPDATE;", (cart_id,))
        lines = cur.fetchall()
        if not lines:
            raise ValueError("Bosh cart")
        for ln in lines:
            cur.execute("SELECT stock FROM items WHERE id=%s FOR UPDATE;", (ln['item_id'],))
            it = cur.fetchone()
            if not it or it['stock'] < ln['qty']:
                raise ValueError("Stok etarli emas")
            # kamaytirish
            cur.execute("UPDATE  items SET stock = stock - %s WHERE id=%s;", (ln['qty'], ln['item_id'],))
        #cartni yopish
        cur.execute("UPDATE carts SET status='checked_out' WHERE id=%s;", (cart_id, ))
        return True

