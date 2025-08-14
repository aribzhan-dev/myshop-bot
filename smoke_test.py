# myshop_bot/script/smoke_test.py
from pathlib import Path
from dotenv import load_dotenv

# .env ni myshop_bot/ ichidan yuklaymiz (har doim to‘g‘ri topsin)
ROOT = Path(__file__).resolve().parents[1]   # .../myshop_bot
load_dotenv(ROOT / ".env")

# 🔽 NISBIY IMPORTLAR (absolute o‘rniga)
from db.clients import create_client, get_client, list_clients, update_client, delete_client
from db.items import create_item, get_item, list_items, update_item, delete_item
from db.cart import get_or_create_active_cart, get_cart_total, checkout_cart
from db.cart_items import add_item_to_cart, set_item_qty, remove_item, get_cart_detail


def main():
    # Client
    cid = create_client("Smoke Tester", None, "qqwqwqw@example.com")
    print("Client:", cid, get_client(cid))

    # Items
    iid1 = create_item("Pen", 2000.00, stock=100, sku="PEN-11100")
    iid2 = create_item("Notebook", 15000.00, stock=20, sku="NB-0220")
    print("Items:", list_items())

    # Cart
    cart_id = get_or_create_active_cart(cid)
    add_item_to_cart(cart_id, iid1, 5)
    add_item_to_cart(cart_id, iid2, 2)
    rows, total = get_cart_detail(cart_id)
    print("Cart rows:", rows)
    print("Total:", total)

    set_item_qty(cart_id, iid1, 3)  # pen qty 3
    rows, total = get_cart_detail(cart_id)
    print("After set qty:", rows, total)

    remove_item(cart_id, iid2)      # notebookni olib tashlash
    rows, total = get_cart_detail(cart_id)
    print("After remove:", rows, total)

    checkout_cart(cart_id)
    print("Checked-out total via view:", get_cart_total(cart_id))


if __name__ == "__main__":
    main()