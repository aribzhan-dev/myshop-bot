
from .connection import get_conn

def create_client(name: str, phone: str, email: str,):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO clients (name, phone, email) VALUES (%s, %s, %s) RETURNING id;", (name, phone, email))
        return cur.fetchone()['id']
    print('Successfully:', cur.fetchone()['id'])


def get_or_create_client_by_telegram(telegram_id:int, name: str| None = None, username: str | None = None):
    with get_conn() as conn,  conn.cursor() as cur:
        cur.execute("SELECT id FROM clients WHERE telegram_id=%s;", (telegram_id,))
        row = cur.fetchone()
        if row:
            return row['id']

        display_name = name or username or f'Telegram user {telegram_id}'
        cur.execute("INSERT INTO clients (name, telegram_id) VALUES (%s, %s) RETURNING id;", (display_name, telegram_id))
        return cur.fetchone()['id']


# clients table lidan hamma clientlarni olish
def list_clients():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, phone, email FROM clients ORDER BY id;")
        return cur.fetchall()
    print('Successfully:', cur.fetchall())


# client table lidagi bitta clientni id si bilan olish
def get_client(client_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, phone, email FROM clients WHERE id=%s;", (client_id, ))
        return cur.fetchone()
    print('Successfully:', cur.fetchone())

#client table lini update qilish
def update_client(client_id: int, name: str |None= None, phone: str | None = None, email: str | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        if not name and not phone and not email:
            print("hech narsa yoq")
            return 0

        sets, params = [], []
        if name:
            sets.append("name=%s"), params.append(name)
        if phone:
            sets.append("phone=%s"), params.append(phone)
        if email:
            sets.append("email=%s"), params.append(email)
        params.append(client_id)
        q = f"UPDATE clients SET {', '.join(sets)} WHERE id=%s;"
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(q, tuple(params))
            return cur.rowcount
        print('Successfully:', cur.rowcount)


# clientni uchirish
def delete_client(client_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id=%s;", (client_id,))
        return cur.rowcount
    print('Successfully:', cur.rowcount)
