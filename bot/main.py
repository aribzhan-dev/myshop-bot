
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)


from bot.menus import main_menu, clients_menu, items_menu, cart_menu





# DB qatlamidan keraklilar
from db.clients import create_client, list_clients, get_or_create_client_by_telegram
from db.items import create_item, list_items
from db.cart import get_or_create_active_cart, get_cart_total, checkout_cart
from db.cart_items import add_item_to_cart, set_item_qty, remove_item, get_cart_detail




load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def resolve_client_id(update: Update) -> int:
    u = update.effective_user
    return get_or_create_client_by_telegram(
        u.id,
        name=u.full_name,
        username=u.username
    )

# ---- States ----
(CL_CREATE_NAME, CL_CREATE_PHONE, CL_CREATE_EMAIL,
 IT_CREATE_NAME, IT_CREATE_PRICE, IT_CREATE_STOCK, IT_CREATE_SKU,
 CART_ADD_ITEM_ID, CART_ADD_QTY,
 CART_SET_ITEM_ID, CART_SET_QTY,
 CART_REMOVE_ITEM_ID) = range(12)

# ---- /start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await (update.message or update.callback_query.message).reply_text(
        "Botga hush kelibsiz:", reply_markup=main_menu()
    )

# ---- Main router (inline buttons) ----
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "clients":
        await q.edit_message_text("Clients:", reply_markup=clients_menu()); return ConversationHandler.END
    if data == "items":
        await q.edit_message_text("Items:", reply_markup=items_menu()); return ConversationHandler.END
    if data == "cart":
        await q.edit_message_text("Cart:", reply_markup=cart_menu()); return ConversationHandler.END
    if data == "back_main":
        await q.edit_message_text("Main:", reply_markup=main_menu()); return ConversationHandler.END

    # ---- Clients submenu ----
    if data == "cl_create":
        await q.edit_message_text("Clientni ismi?"); return CL_CREATE_NAME
    if data == "cl_list":
        rows = list_clients()
        if not rows:
            await q.edit_message_text(" clients yoq")
        else:
            lines = [f"{r['id']}. {r['name']} — {r.get('phone') or '-'} - {r.get('email') or '-'}" for r in rows]
            await q.edit_message_text("Clients:\n" + "\n".join(lines))
        await q.message.reply_text("Main:", reply_markup=main_menu())
        return ConversationHandler.END


    # ---- Items submenu ----
    if data == "it_create":
        await q.edit_message_text("Item title?"); return IT_CREATE_NAME
    if data == "it_list":
        rows = list_items(only_active=False)
        if not rows:
            await q.edit_message_text("Item yoq.")
        else:
            lines = [f"{r['id']}. {r['name']} — price={r['price']} stock={r['stock']}" for r in rows]
            await q.edit_message_text("Items:\n" + "\n".join(lines))
        await q.message.reply_text("Main:", reply_markup=main_menu())
        return ConversationHandler.END

    # ---- Cart submenu ----
    if data == "cart_add":
        await q.edit_message_text("Item ID?"); return CART_ADD_ITEM_ID
    if data == "cart_show":
        client_id = resolve_client_id(update)
        cart_id = get_or_create_active_cart(client_id)
        rows, total = get_cart_detail(cart_id)
        if not rows:
            await q.edit_message_text("Cart pustoy.")
        else:
            lines = [f"{r['item_id']} {r['name']} x{r['qty']} = {r['line_total']}" for r in rows]
            await q.edit_message_text("Cart:\n" + "\n".join(lines) + f"\n\nTotal: {total}")
        await q.message.reply_text("main:", reply_markup=cart_menu())
        return ConversationHandler.END
    if data == "cart_setqty":
        await q.edit_message_text("Item ID to set qty?"); return CART_SET_ITEM_ID
    if data == "cart_remove":
        await q.edit_message_text("Item ID to remove?"); return CART_REMOVE_ITEM_ID
    if data == "cart_checkout":
        client_id = resolve_client_id(update)
        cart_id = get_or_create_active_cart(client_id)
        try:
            checkout_cart(cart_id)
            await q.edit_message_text("✅Hamma narsa tekshirildi!", reply_markup=cart_menu())
        except Exception as e:
            await q.edit_message_text(f"❌ Hamma nersa tekshirilmadi: {e}", reply_markup=cart_menu())
        return ConversationHandler.END

    # default
    await q.edit_message_text("Unknown action."); return ConversationHandler.END

# ---- Clients create flow ----
async def cl_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cl_name"] = update.message.text.strip()
    await update.message.reply_text("Phone? (yoki '-' tashab ketish)")
    return CL_CREATE_PHONE

async def cl_create_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    context.user_data["cl_phone"] = None if phone == "-" else phone
    await update.message.reply_text("Email? (or '-' to skip)")
    return CL_CREATE_EMAIL

async def cl_create_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if email == "-": email = None
    try:
        new_id = create_client(
            context.user_data["cl_name"],
            context.user_data["cl_phone"],
            email,
        )
        await update.message.reply_text(f"✅ Client created: id={new_id}", reply_markup=clients_menu())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=clients_menu())
    return ConversationHandler.END

# ---- Items create flow ----
async def it_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["it_name"] = update.message.text.strip()
    await update.message.reply_text("Price? (e.g. 1999.99)")
    return IT_CREATE_PRICE

async def it_create_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    try:
        price = float(txt)  # oddiy
    except:
        await update.message.reply_text("Raqam kiriting, masalan: 1999.99"); return IT_CREATE_PRICE
    context.user_data["it_price"] = price
    await update.message.reply_text("Stock? (e.g. 10)")
    return IT_CREATE_STOCK



async def it_create_stock(update, context):
    txt = update.message.text.strip()
    if not txt.isdigit():
        await update.message.reply_text("Butun son kiriting, masalan: 10"); return IT_CREATE_STOCK
    context.user_data["it_stock"] = int(txt)
    await update.message.reply_text("SKU? (o‘tkazib yuborish uchun '-')")
    return IT_CREATE_SKU

async def it_create_sku(update, context):
    sku_txt = update.message.text.strip()
    sku = None if sku_txt == '-' else sku_txt
    try:
        new_id = create_item(
            context.user_data["it_name"],
            context.user_data["it_price"],
            stock=context.user_data["it_stock"],
            sku=sku
        )
        await update.message.reply_text(f"✅ Item created: id={new_id}", reply_markup=items_menu())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=items_menu())
    return ConversationHandler.END

# ---- Cart add flow ----
async def cart_add_item_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit():
        await update.message.reply_text("Raqam kiriting (item id)"); return CART_ADD_ITEM_ID
    context.user_data["add_item_id"] = int(txt)
    await update.message.reply_text("Qty?")
    return CART_ADD_QTY

async def cart_add_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit() or int(txt) <= 0:
        await update.message.reply_text("Musbat butun son kiriting (qty)"); return CART_ADD_QTY
    qty = int(txt)
    client_id = resolve_client_id(update)
    cart_id = get_or_create_active_cart(client_id)
    try:
        add_item_to_cart(cart_id, context.user_data["add_item_id"], qty)
        await update.message.reply_text("✅ Added to cart", reply_markup=cart_menu())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=cart_menu())
    return ConversationHandler.END

# ---- Cart set qty flow ----
async def cart_set_item_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit():
        await update.message.reply_text("Raqam kiriting (item id)"); return CART_SET_ITEM_ID
    context.user_data["set_item_id"] = int(txt)
    await update.message.reply_text("New qty? (0 => remove)")
    return CART_SET_QTY

async def cart_set_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not (txt.lstrip("-").isdigit()):
        await update.message.reply_text("Butun son kiriting"); return CART_SET_QTY
    qty = int(txt)
    client_id = resolve_client_id(update)
    cart_id = get_or_create_active_cart(client_id)
    try:

        changed = set_item_qty(cart_id, context.user_data["set_item_id"], qty)
        msg = "✅ Qty updated" if changed else "ℹ️ Nothing changed"
        await update.message.reply_text(msg, reply_markup=cart_menu())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=cart_menu())
    return ConversationHandler.END

# ---- Cart remove flow ----
async def cart_remove_item_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not txt.isdigit():
        await update.message.reply_text("Raqam kiriting (item id)"); return CART_REMOVE_ITEM_ID
    client_id = resolve_client_id(update)
    cart_id = get_or_create_active_cart(client_id)
    try:
        removed = remove_item(cart_id, int(txt))
        msg = "✅ Removed" if removed else "ℹ️ Not found"
        await update.message.reply_text(msg, reply_markup=cart_menu())
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}", reply_markup=cart_menu())
    return ConversationHandler.END

def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(router, pattern="^(clients|items|cart|back_main|cl_create|cl_list|it_create|it_list|cart_add|cart_show|cart_setqty|cart_remove|cart_checkout)$")],
        states={
            CL_CREATE_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, cl_create_name)],
            CL_CREATE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cl_create_phone)],
            CL_CREATE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cl_create_email)],

            IT_CREATE_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, it_create_name)],
            IT_CREATE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, it_create_price)],
            IT_CREATE_STOCK:[MessageHandler(filters.TEXT & ~filters.COMMAND, it_create_stock)],
            IT_CREATE_SKU:   [MessageHandler(filters.TEXT & ~filters.COMMAND, it_create_sku)],


            CART_ADD_ITEM_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, cart_add_item_id)],
            CART_ADD_QTY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, cart_add_qty)],

            CART_SET_ITEM_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, cart_set_item_id)],
            CART_SET_QTY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, cart_set_qty)],

            CART_REMOVE_ITEM_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, cart_remove_item_id)],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(router))  # qolgan callbacklar uchun

    return app

if __name__ == "__main__":
    app = build_app()
    print("Bot running. /start")
    app.run_polling()