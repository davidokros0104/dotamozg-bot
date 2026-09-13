import asyncio
import logging
import os
import random
import sqlite3

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 12 вопросов за сессию (4 блока по 3 вопроса)
QUESTIONS_PER_QUIZ = 12

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

QUESTIONS_BASE = [
    # --- БЛОК 1: Предметы ---
    {"category": "items", "question": "Какой предмет даёт полный иммунитет к заклинаниям на время действия?", "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Pipe of Insight"], "correct": "Black King Bar"},
    {"category": "items", "question": "Какой предмет собирается из Blink Dagger и Reaver?", "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Wind Waker"], "correct": "Overwhelming Blink"},
    {"category": "items", "question": "Сколько стоит рецепт для сборки Hand of Midas?", "options": ["1750", "1500", "1400", "2200"], "correct": "1750"},
    {"category": "items", "question": "Какой предмет даёт эффект 'True Sight' вокруг владельца?", "options": ["Dust of Appearance", "Sentry Ward", "Gem of True Sight", "Shadow Blade"], "correct": "Gem of True Sight"},

    # --- БЛОК 2: Герои и Механики ---
    {"category": "heroes", "question": "Какой атрибут является основным для героя Pudge?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Сила"},
    {"category": "heroes", "question": "Сколько сфер у Invoker одновременно вращается вокруг него?", "options": ["2", "3", "4", "5"], "correct": "3"},
    {"category": "heroes", "question": "Как называется ультимейт героя Rubick?", "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"], "correct": "Spell Steal"},
    {"category": "heroes", "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?", "options": ["Phantom Lancer", "Naga Siren", "Meepo", "Chaos Knight"], "correct": "Meepo"},

    # --- БЛОК 3: Киберспорт и Лор ---
    {"category": "lore", "question": "Какая команда выиграла The International 2021 (TI10)?", "options": ["PSG.LGD", "OG", "Team Spirit", "Team Liquid"], "correct": "Team Spirit"},
    {"category": "lore", "question": "Какая команда выиграла два TI подряд (TI8 и TI9)?", "options": ["Na'Vi", "OG", "Alliance", "Team Liquid"], "correct": "OG"},
    {"category": "lore", "question": "Как зовут нейтрального босса, из которого выпадает Aegis of the Immortal?", "options": ["Tormentor", "Roshan", "Satanic", "Ancient Blue Dragon"], "correct": "Roshan"},
    {"category": "lore", "question": "Кто выиграл самый первый The International (TI1) в 2011 году?", "options": ["Natus Vincere (Na'Vi)", "EHOME", "Invictus Gaming", "Alliance"], "correct": "Natus Vincere (Na'Vi)"},

    # --- БЛОК 4: Сложный микс ---
    {"category": "mix", "question": "Какой предмет перезаряжает все способности и предметы героя?", "options": ["Refresher Orb", "Scythe of Vyse", "Octarine Core", "Bloodstone"], "correct": "Refresher Orb"},
    {"category": "mix", "question": "Какой предмет выпадает из Торментора (Tormentor)?", "options": ["Aghanim's Shard", "Aegis", "Cheese", "Refresher Shard"], "correct": "Aghanim's Shard"},
    {"category": "mix", "question": "Какое максимальное число зарядов может хранить Magic Wand?", "options": ["20", "15", "10", "25"], "correct": "20"},
    {"category": "mix", "question": "Какой герой произносит знаменитую фразу 'Fresh meat!'?", "options": ["Pudge", "Lifestealer", "Doom", "Night Stalker"], "correct": "Pudge"}
]

class QuizStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_rank = State()
    choosing_category = State()
    in_quiz = State()

def main_menu():
    kb = [
        [KeyboardButton(text="🎮 Начать викторину")],
        [KeyboardButton(text="🏆 Моя доска почёта")],
        [KeyboardButton(text="📊 Мой профиль / Сменить ранг")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def category_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎲 Играть 12 вопросов (4 блока по 3)", callback_data="cat_all")],
        [InlineKeyboardButton(text="🗡 Только Предметы", callback_data="cat_items")],
        [InlineKeyboardButton(text="🧙‍♂️ Только Герои", callback_data="cat_heroes")],
        [InlineKeyboardButton(text="🏆 Только Киберспорт/Лор", callback_data="cat_lore")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

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
    kb = []
    for i in range(0, len(ranks), 2):
        row = [InlineKeyboardButton(text=ranks[i], callback_data=f"rank_{ranks[i]}")]
        if i + 1 < len(ranks):
            row.append(InlineKeyboardButton(text=ranks[i+1], callback_data=f"rank_{ranks[i+1]}"))
        kb.append(row)
    
    await message.answer("Отлично! Теперь выбери свой текущий ранг в Dota 2:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(QuizStates.waiting_for_rank)

@dp.callback_query(F.data.startswith("rank_"))
async def process_rank(callback: types.CallbackQuery, state: FSMContext):
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

    await callback.message.answer(f"Регистрация завершена! Твой ранг: {selected_rank}.", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "🎮 Начать викторину")
async def ask_category(message: types.Message, state: FSMContext):
    await message.answer("Выбери режим игры:", reply_markup=category_keyboard())
    await state.set_state(QuizStates.choosing_category)

@dp.callback_query(F.data.startswith("cat_"), QuizStates.choosing_category)
async def start_quiz_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    
    if cat == "all":
        # Формируем 4 блока по 3 вопроса = 12 вопросов
        items = [q for q in QUESTIONS_BASE if q.get("category") == "items"]
        heroes = [q for q in QUESTIONS_BASE if q.get("category") == "heroes"]
        lore = [q for q in QUESTIONS_BASE if q.get("category") == "lore"]
        mix = [q for q in QUESTIONS_BASE if q.get("category") == "mix"]

        block1 = random.sample(items, min(3, len(items)))
        block2 = random.sample(heroes, min(3, len(heroes)))
        block3 = random.sample(lore, min(3, len(lore)))
        block4 = random.sample(mix, min(3, len(mix)))

        selected_questions = block1 + block2 + block3 + block4
    else:
        pool = [q for q in QUESTIONS_BASE if q.get("category") == cat]
        selected_questions = random.sample(pool, min(12, len(pool)))

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=selected_questions,
        current_index=0,
        correct_count=0,
        wrong_count=0
    )
    
    await render_question(callback.message, state)

async def render_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]

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
        """, (total, correct, wrong, message.chat.id))
        conn.commit()
        conn.close()

        text = f"🎉 **Викторина окончена!**\n\nПравильных ответов: **{correct} из {total}**\nПосмотри результаты в «🏆 Моя доска почёта»."
        await message.edit_text(text, parse_mode="Markdown")
        await state.clear()
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]
    
    # Визуальное разделение на 4 блока
    block_num = (index // 3) + 1
    q_text = f"**Блок {block_num} | Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"

    await message.edit_text(q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("ans_"), QuizStates.in_quiz)
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    user_ans = callback.data.replace("ans_", "")
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]
    q = questions[index]

    if user_ans == q["correct"]:
        await callback.answer("✅ Правильно!", show_alert=False)
        correct_count = data["correct_count"] + 1
        wrong_count = data["wrong_count"]
    else:
        await callback.answer(f"❌ Неверно! Ответ: {q['correct']}", show_alert=False)
        correct_count = data["correct_count"]
        wrong_count = data["wrong_count"] + 1

    await state.update_data(
        current_index=index + 1,
        correct_count=correct_count,
        wrong_count=wrong_count
    )

    await render_question(callback.message, state)

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
        f"📊 **Всего ответов:** {total}\n"
        f"✅ **Правильных:** {correct}\n"
        f"❌ **Ошибок:** {wrong}\n"
        f"🎯 **Точность:** {accuracy}%"
    )
    await message.answer(stats_text, parse_mode="Markdown")

@dp.message(F.text == "📊 Мой профиль / Сменить ранг")
async def change_rank_prompt(message: types.Message, state: FSMContext):
    ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
    kb = []
    for i in range(0, len(ranks), 2):
        row = [InlineKeyboardButton(text=ranks[i], callback_data=f"rank_{ranks[i]}")]
        if i + 1 < len(ranks):
            row.append(InlineKeyboardButton(text=ranks[i+1], callback_data=f"rank_{ranks[i+1]}"))
        kb.append(row)
    
    await message.answer("Выбери новый ранг для своего профиля:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(QuizStates.waiting_for_rank)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
