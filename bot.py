import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 5833487732  # O'zingizning Telegram ID raqamingiz

# Klub va davlat formalari
clubs = {
    "Real Madrid": "images/real_madrid.jpg",
    "Barcelona": "images/barcelona.jpg",
    "Manchester United": "images/manu.jpg"
}

countries = {
    "O‘zbekiston": "images/uzbekistan.jpg",
    "Braziliya": "images/brazil.jpg",
    "Frantsiya": "images/france.jpg"
}

colors = ["Qizil 🔴", "Oq ⚪", "Ko'k 🔵", "Qora ⚫"]
sizes = ["S", "M", "L", "XL", "XXL"]

# Foydalanuvchi buyurtmalarini vaqtincha saqlash
orders = {}

# Asosiy menyu
def main_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text="Klub Formalari ⚽", callback_data="clubs"),
        types.InlineKeyboardButton(text="Davlat Formalari 🌍", callback_data="countries")
    )
    return kb

# Orqaga tugma yaratish
def back_button(destination="main"):
    if not destination:
        destination = "main"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="⬅ Orqaga", callback_data=f"back_{destination}"))
    return kb

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Salom! Futbol formasi do‘koniga xush kelibsiz 👕\nQuyidagilardan birini tanlang:",
        reply_markup=main_menu()
    )

# Klublarni ko'rsatish
def show_clubs(call):
    kb = types.InlineKeyboardMarkup()
    for club in clubs:
        kb.add(types.InlineKeyboardButton(text=club, callback_data=f"club_{club}"))
    kb.add(back_button("main").keyboard[0][0])  # Orqaga tugma
    bot.edit_message_text(
        "Klubni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb
    )

# Davlatlarni ko'rsatish
def show_countries(call):
    kb = types.InlineKeyboardMarkup()
    for country in countries:
        kb.add(types.InlineKeyboardButton(text=country, callback_data=f"country_{country}"))
    kb.add(back_button("main").keyboard[0][0])  # Orqaga tugma
    bot.edit_message_text(
        "Davlatni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb
    )

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    # Orqaga tugma bosilganda
    if call.data.startswith("back_"):
        destination = call.data.replace("back_", "")
        if destination == "main":
            bot.edit_message_text(
                "Quyidagilardan birini tanlang:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_menu()
            )
        elif destination == "clubs":
            show_clubs(call)
        elif destination == "countries":
            show_countries(call)
        return

    # Klublar va davlatlar
    if call.data == "clubs":
        show_clubs(call)
    elif call.data == "countries":
        show_countries(call)

    # Klub yoki davlatni tanlash
    elif call.data.startswith("club_") or call.data.startswith("country_"):
        item_type, name = call.data.split("_", 1)
        img_path = clubs[name] if item_type == "club" else countries[name]

        orders[user_id] = {"type": item_type, "name": name}

        kb = types.InlineKeyboardMarkup()
        for color in colors:
            kb.add(types.InlineKeyboardButton(text=color, callback_data=f"color_{color}"))
        kb.add(back_button("clubs" if item_type=="club" else "countries").keyboard[0][0])
        bot.send_photo(
            call.message.chat.id,
            open(img_path, 'rb'),
            caption=f"{name} formasi\nRangni tanlang:",
            reply_markup=kb
        )

    # Rang tanlash
    elif call.data.startswith("color_"):
        color = call.data.replace("color_", "")
        orders[user_id]["color"] = color
        kb = types.InlineKeyboardMarkup()
        for size in sizes:
            kb.add(types.InlineKeyboardButton(text=size, callback_data=f"size_{size}"))
        kb.add(back_button("clubs").keyboard[0][0])
        bot.send_message(call.message.chat.id, "O‘lchamni tanlang:", reply_markup=kb)

        # O'lcham tanlash
    elif call.data.startswith("size_"):
        size = call.data.replace("size_", "")
        orders[user_id]["size"] = size
        bot.send_message(call.message.chat.id, "Necha dona kerakligini yozing:")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, get_quantity)

def get_quantity(message):
        user_id = message.from_user.id
        if user_id in orders:
            try:
                quantity = int(message.text)
            except:
                bot.send_message(message.chat.id, "Iltimos, son kiriting.")
                bot.register_next_step_handler(message, get_quantity)
                return
            orders[user_id]["quantity"] = quantity

            order = orders[user_id]
            summary = (
                f"Buyurtma tasdiqlandi ✅\n\n"
                f"Foydalanuvchi: {message.from_user.first_name} @{message.from_user.username}\n"
                f"Tur: {'Klub' if order['type'] == 'club' else 'Davlat'}\n"
                f"Nom: {order['name']}\n"
                f"Rang: {order['color']}\n"
                f"O‘lcham: {order['size']}\n"
                f"Miqdor: {order['quantity']}"
            )

            bot.send_message(message.chat.id, "Buyurtmangiz qabul qilindi ✅\nTez orada siz bilan bog‘lanamiz!")
            bot.send_message(ADMIN_ID, summary)

            del orders[user_id]
        else:
            bot.send_message(message.chat.id, "Xato yuz berdi. /start bilan qayta boshlang.")

bot.infinity_polling()