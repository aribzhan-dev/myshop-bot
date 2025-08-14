
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Clients", callback_data="clients")],
        [InlineKeyboardButton("📦 Items",   callback_data="items")],
        [InlineKeyboardButton("🛒 Cart",    callback_data="cart")],
    ])

def clients_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Create Client", callback_data="cl_create")],
        [InlineKeyboardButton("📋 List Clients",  callback_data="cl_list")],
        [InlineKeyboardButton("⬅️ Back",          callback_data="back_main")],
    ])

def items_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Create Item", callback_data="it_create")],
        [InlineKeyboardButton("📋 List Items",  callback_data="it_list")],
        [InlineKeyboardButton("⬅️ Back",        callback_data="back_main")],
    ])

def cart_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Item",     callback_data="cart_add")],
        [InlineKeyboardButton("🧾 Show Cart",    callback_data="cart_show")],
        [InlineKeyboardButton("✏️ Set Qty",      callback_data="cart_setqty")],
        [InlineKeyboardButton("❌ Remove Item",  callback_data="cart_remove")],
        [InlineKeyboardButton("✅ Checkout",     callback_data="cart_checkout")],
        [InlineKeyboardButton("⬅️ Back",         callback_data="back_main")],
    ])