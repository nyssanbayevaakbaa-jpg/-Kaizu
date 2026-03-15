import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = "8108218311:AAEGmucXX6BBfricxzPGDacJEdtTfWp4uhA"
ADMIN_ID = 6436250126

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("premii.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    total_money INTEGER DEFAULT 0
)
""")
conn.commit()


def add_money(user_id, username, amount):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, total_money) VALUES (?, ?, ?)",
            (user_id, username, amount)
        )
    else:
        cursor.execute(
            "UPDATE users SET total_money = total_money + ? WHERE user_id = ?",
            (amount, user_id)
        )

    conn.commit()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("💸 Бот для премий запущен!")


@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(f"Твой ID: {message.from_user.id}")


# ВЫДАТЬ ПРЕМИЮ
@dp.message(F.text.startswith("+"))
async def give_premia(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение игрока и напиши +сумма")
        return

    try:
        amount = int(message.text[1:])
    except:
        await message.answer("Пример: +5000")
        return

    user = message.reply_to_message.from_user

    if user.is_bot:
        return

    username = user.username if user.username else user.full_name

    add_money(user.id, username, amount)

    await message.answer(f"💰 @{username} получил {amount}$ премии!")


# УБРАТЬ ПРЕМИЮ
@dp.message(F.text.startswith("-"))
async def remove_premia(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение игрока и напиши -сумма")
        return

    try:
        amount = int(message.text[1:])
    except:
        await message.answer("Пример: -5000")
        return

    user = message.reply_to_message.from_user

    if user.is_bot:
        return

    username = user.username if user.username else user.full_name

    cursor.execute(
        "UPDATE users SET total_money = total_money - ? WHERE user_id = ?",
        (amount, user.id)
    )
    conn.commit()

    await message.answer(f"❌ У @{username} убрали {amount}$ премии")


# ТОП ПРЕМИЙ
@dp.message(Command("top"))
async def top_players(message: Message):

    cursor.execute("""
    SELECT username, total_money 
    FROM users 
    WHERE total_money > 0
    ORDER BY total_money DESC 
    LIMIT 10
    """)

    top = cursor.fetchall()

    if not top:
        await message.answer("Пока нет выданных премий.")
        return

    text = "🏆 Топ по премиям:\n\n"

    for i, (username, money) in enumerate(top, start=1):
        text += f"{i}. {username} — {money}$\n"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())