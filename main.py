import asyncio
import logging
import os
import random
import sqlite3

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from questions import QUESTIONS_BASE

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

BACKGROUND_IMAGES = {
    "items": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/black_king_bar.png",
    "heroes": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png",
    "lore": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/blog/archive_header.jpg",
    "general": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/home/hero_trio.png"
}

def init_db():
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            nickname TEXT,
            rank TEXT,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            wrong_answers INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

class QuizStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_rank = State()
    choosing_category = State()
    in_quiz = State()

def main_menu():
    kb = [
        [KeyboardButton(text="📝 Пройти тест")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="👤 Профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def category_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎯 Микс (Всё подряд)", callback_data="cat_all")],
        [InlineKeyboardButton(text="🗡 Предметы", callback_data="cat_items")],
        [InlineKeyboardButton(text="🦸 Герои и Механики", callback_data="cat_heroes")],
        [InlineKeyboardButton(text="📜 Киберспорт и Лор", callback_data="cat_lore")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def safe_delete_message(chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        msg = await message.answer("Привет! Добро пожаловать в «ДотаМозг»! ❤️\n\nВведи свой игровой никнейм:")
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(QuizStates.waiting_for_nickname)
    else:
        await message.answer(f"С возвращением, {user[0]}!", reply_markup=main_menu())

@dp.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await state.clear()
    await message.answer("🔄 Профиль очищен! Отправьте /start для регистрации.", reply_markup=main_menu())

@dp.message(QuizStates.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])
    await safe_delete_message(message.chat.id, message.message_id)

    await state.update_data(nickname=message.text)
    ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
    kb = []
    for i in range(0, len(ranks), 2):
        row = [InlineKeyboardButton(text=ranks[i], callback_data=f"rank_{ranks[i]}")]
        if i + 1 < len(ranks):
            row.append(InlineKeyboardButton(text=ranks[i+1], callback_data=f"rank_{ranks[i+1]}"))
        kb.append(row)

    msg = await message.answer("Выбери твой текущий ранг в Dota 2:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(QuizStates.waiting_for_rank)

@dp.callback_query(F.data.startswith("rank_"))
async def process_rank(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    selected_rank = callback.data.split("_")[1]
    data = await state.get_data()
    nickname = data.get("nickname") or callback.from_user.first_name or "Игрок"

    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, nickname, rank) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET nickname=excluded.nickname, rank=excluded.rank
    """, (callback.from_user.id, nickname, selected_rank))
    conn.commit()
    conn.close()

    await safe_delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(f"Профиль обновлен! Ваш ранг: **{selected_rank}**.", parse_mode="Markdown", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text.in_(["📝 Пройти тест", "Играть", "играть"]))
@dp.callback_query(F.data == "restart_quiz")
async def ask_category(event: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        await event.answer()
        chat_id = event.message.chat.id
        message_id = event.message.message_id
    else:
        chat_id = event.chat.id
        message_id = event.message_id

    await safe_delete_message(chat_id, message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(chat_id, data["last_msg_id"])

    msg = await bot.send_message(chat_id, "Выбери режим тестирования:", reply_markup=category_keyboard())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(QuizStates.choosing_category)

@dp.callback_query(F.data.startswith("cat_"), QuizStates.choosing_category)
async def start_quiz_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    cat = callback.data.replace("cat_", "")

    if cat == "all":
        pool = QUESTIONS_BASE.copy()
    elif cat == "heroes":
        pool = [q for q in QUESTIONS_BASE if q.get("category") in ["heroes", "hero"]]
    elif cat == "items":
        pool = [q for q in QUESTIONS_BASE if q.get("category") in ["items", "item"]]
    elif cat == "lore":
        pool = [q for q in QUESTIONS_BASE if q.get("category") in ["lore", "general"]]
    else:
        pool = QUESTIONS_BASE.copy()

    if not pool:
        pool = QUESTIONS_BASE.copy()

    random.shuffle(pool)
    selected_questions = pool[:min(10, len(pool))]

    await safe_delete_message(callback.message.chat.id, callback.message.message_id)

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=selected_questions,
        current_index=0,
        correct_count=0,
        wrong_count=0
    )

    await render_question(callback.message.chat.id, state)

async def render_question(chat_id: int, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]

    if "last_msg_id" in data:
        await safe_delete_message(chat_id, data["last_msg_id"])

    if index >= len(questions):
        correct = data["correct_count"]
        wrong = data["wrong_count"]
        total = correct + wrong

        conn = sqlite3.connect("dotamozg.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET total_questions = total_questions + ?,
                correct_answers = correct_answers + ?,
                wrong_answers = wrong_answers + ?
            WHERE user_id = ?
        """, (total, correct, wrong, chat_id))
        conn.commit()
        conn.close()

        kb = [[InlineKeyboardButton(text="🔄 Играть снова", callback_data="restart_quiz")]]
        msg = await bot.send_message(
            chat_id,
            f"🎉 **Тест завершен!**\n\n"
            f"✅ Правильно: {correct}\n"
            f"❌ Ошибок: {wrong}\n"
            f"📊 Итог: {correct}/{total}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
        await state.clear()
        return

    q = questions[index]
    text = f"❓ **Вопрос {index + 1}/{len(questions)}**\n\n{q['question']}"
    kb = []
    for idx, option in enumerate(q['options']):
        kb.append([InlineKeyboardButton(text=option, callback_data=f"ans_{idx}")])

    image_url = q.get("image") or BACKGROUND_IMAGES.get(q.get("category"), BACKGROUND_IMAGES["general"])

    try:
        msg = await bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
    except Exception:
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )

    await state.update_data(last_msg_id=msg.message_id)

@dp.callback_query(F.data.startswith("ans_"), QuizStates.in_quiz)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    ans_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]
    q = questions[index]

    if ans_idx == q["correct"]:
        await state.update_data(correct_count=data.get("correct_count", 0) + 1)
    else:
        await state.update_data(wrong_count=data.get("wrong_count", 0) + 1)

    await state.update_data(current_index=index + 1)
    await render_question(callback.message.chat.id, state)

@dp.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message):
    await safe_delete_message(message.chat.id, message.message_id)
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, rank, total_questions, correct_answers, wrong_answers FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        await message.answer("Сначала пройдите регистрацию через /start")
        return

    nickname, rank, total, correct, wrong = user
    winrate = round((correct / total * 100), 1) if total > 0 else 0

    text = (
        f"📊 **Статистика {nickname}**\n\n"
        f"🏅 Ранг: {rank}\n"
        f"📝 Всего вопросов: {total}\n"
        f"✅ Правильных ответов: {correct}\n"
        f"❌ Ошибок: {wrong}\n"
        f"🎯 Точность: {winrate}%"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
    await safe_delete_message(message.chat.id, message.message_id)
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, rank FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        await message.answer("Сначала пройдите регистрацию через /start")
        return

    text = f"👤 **Профиль пользователя**\n\nНикнейм: **{user[0]}**\nРанг: **{user[1]}**"
    await message.answer(text, parse_mode="Markdown")

async def handle_healthcheck(request):
    return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
