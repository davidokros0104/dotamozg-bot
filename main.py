import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Вставьте ваш новый токен сюда
import os
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- База данных SQLite ---
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

# --- Состояния FSM ---
class QuizStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_rank = State()
    in_quiz = State()

# --- База вопросов ---
QUESTIONS = [
    {
        "q": "Какой герой обладает способностью 'Black Hole'?",
        "options": ["Enigma", "Tidehunter", "Magnus", "Faceless Void"],
        "correct": 0,
        "desc": "Black Hole — ультимативная способность героя Enigma, затягивающая всех врагов в область действия.",
    },
    {
        "q": "Какой предмет даёт полный иммунитет к заклинаниям на время действия?",
        "options": ["Manta Style", "Black King Bar", "Linken's Sphere", "Satanic"],
        "correct": 1,
        "desc": "Black King Bar (BKB) активирует эффекты Avatar, давая защитный барьер и иммунитет к магии.",
    },
    {
        "q": "Какая команда выиграла The International 2021 (TI10)?",
        "options": ["PSG.LGD", "OG", "Team Spirit", "Team Liquid"],
        "correct": 2,
        "desc": "Team Spirit одержала победу на TI10, обыграв PSG.LGD в финале со счетом 3:2.",
    },
]

# --- Клавиатуры ---
def main_menu():
    kb = [
        [types.KeyboardButton(text="🎮 Начать викторину")],
        [types.KeyboardButton(text="🏆 Моя доска почёта")],
        [types.KeyboardButton(text="📊 Мой профиль / Сменить ранг")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- Обработчики ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        await message.answer("Привет! Добро пожаловать в викторину «ДотаМозг»! 🧠\nВведи свой игровой никнейм:")
        await state.set_state(QuizStates.waiting_for_nickname)
    else:
        await message.answer(f"С возвращением, {user[0]}!", reply_markup=main_menu())

@dp.message(QuizStates.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
    kb = [[InlineKeyboardButton(text=r, callback_data=f"rank_{r}")] for r in ranks]
    await message.answer("Отлично! Теперь выбери свой текущий ранг в Dota 2:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(QuizStates.waiting_for_rank)

@dp.callback_query(F.data.startswith("rank_"), QuizStates.waiting_for_rank)
async def process_rank(callback: types.CallbackQuery, state: FSMContext):
    selected_rank = callback.data.split("_")[1]
    data = await state.get_data()
    nickname = data.get("nickname")

    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, nickname, rank) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET nickname=excluded.nickname, rank=excluded.rank
    """, (callback.from_user.id, nickname, selected_rank))
    conn.commit()
    conn.close()

    await callback.message.answer(f"Регистрация завершена! Твой ранг: {selected_rank}.", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "🏆 Моя доска почёта")
async def show_stats(message: types.Message):
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, rank, total_questions, correct_answers, wrong_answers FROM users WHERE user_id = ?", (message.from_user.id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        await message.answer("Профиль не найден. Напиши /start для регистрации.")
        return

    nick, rank, total, correct, wrong = data
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    stats_text = (
        f"🏆 **Личная доска почёта**\n\n"
        f"👤 **Игрок:** {nick}\n"
        f"🎖 **Ранг:** {rank}\n"
        f"📝 **Всего ответов:** {total}\n"
        f"✅ **Правильных:** {correct}\n"
        f"❌ **Ошибок:** {wrong}\n"
        f"🎯 **Точность:** {accuracy}%"
    )
    await message.answer(stats_text, parse_mode="Markdown")

@dp.message(F.text == "🎮 Начать викторину")
async def start_quiz(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(QuizStates.in_quiz)
    
    # Отправляем первый вопрос из массива QUESTIONS
    q = QUESTIONS[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"ans_0_{i}")] 
        for i, opt in enumerate(q["options"])
    ])
    await message.answer(f"Вопрос 1:\n{q['q']}", reply_markup=kb)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
