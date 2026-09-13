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

# Расширенная база вопросов с изображениями
QUESTIONS_BASE = [
    # --- ПРЕДМЕТЫ ---
    {
        "category": "items",
        "question": "Какой предмет даёт полный иммунитет к магии на время действия?",
        "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Pipe of Insight"],
        "correct": "Black King Bar",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/black_king_bar.png"
    },
    {
        "category": "items",
        "question": "Какой предмет собирается из Blink Dagger и Reaver?",
        "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Wind Waker"],
        "correct": "Overwhelming Blink",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/overwhelming_blink.png"
    },
    {
        "category": "items",
        "question": "Сколько стоит рецепт для сборки Hand of Midas?",
        "options": ["1750", "1500", "1400", "2200"],
        "correct": "1750",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/hand_of_midas.png"
    },
    {
        "category": "items",
        "question": "Какое максимальное число зарядов может хранить Magic Wand?",
        "options": ["20", "15", "10", "25"],
        "correct": "20",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/magic_wand.png"
    },
    {
        "category": "items",
        "question": "Какой предмет даёт эффект 'True Sight' вокруг владельца?",
        "options": ["Gem of True Sight", "Dust of Appearance", "Sentry Ward", "Shadow Blade"],
        "correct": "Gem of True Sight",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/gem.png"
    },
    {
        "category": "items",
        "question": "Какой предмет сбрасывает большинство негативных эффектов и создаёт две иллюзии героя?",
        "options": ["Manta Style", "Satanic", "Eul's Scepter", "Blink Dagger"],
        "correct": "Manta Style",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/manta.png"
    },
    {
        "category": "items",
        "question": "Какой предмет выпадает при ушибе Торментора (Tormentor)?",
        "options": ["Aghanim's Shard", "Aegis of the Immortal", "Cheese", "Refresher Shard"],
        "correct": "Aghanim's Shard",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aghanims_shard.png"
    },

    # --- ГЕРОИ И МЕХАНИКИ ---
    {
        "category": "heroes",
        "question": "Какой атрибут является основным для героя Pudge?",
        "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"],
        "correct": "Сила",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"
    },
    {
        "category": "heroes",
        "question": "Сколько сфер у Invoker одновременно вращается вокруг него?",
        "options": ["3", "2", "4", "5"],
        "correct": "3",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png"
    },
    {
        "category": "heroes",
        "question": "Как называется ультимейт героя Rubick?",
        "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"],
        "correct": "Spell Steal",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/rubick.png"
    },
    {
        "category": "heroes",
        "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?",
        "options": ["Meepo", "Phantom Lancer", "Naga Siren", "Chaos Knight"],
        "correct": "Meepo",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/meepo.png"
    },
    {
        "category": "heroes",
        "question": "Какой герой произносит знаменитую фразу 'Fresh meat!'?",
        "options": ["Pudge", "Lifestealer", "Doom", "Night Stalker"],
        "correct": "Pudge",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"
    },

    # --- КИБЕРСПОРТ И ЛОР ---
    {
        "category": "lore",
        "question": "Какая команда выиграла The International 2021 (TI10)?",
        "options": ["Team Spirit", "PSG.LGD", "OG", "Team Liquid"],
        "correct": "Team Spirit",
        "image": "https://images.steamusercontent.com/ugc/1759187313627993355/B30FA8F0A2F3D9280E767E28E93467A04D6B633C/"
    },
    {
        "category": "lore",
        "question": "Какая команда выиграла два TI подряд (TI8 и TI9)?",
        "options": ["OG", "Na'Vi", "Alliance", "Team Liquid"],
        "correct": "OG",
        "image": "https://images.steamusercontent.com/ugc/785233939229007425/82767087A9A1EAEB4C29419E75338D6433F53BD8/"
    },
    {
        "category": "lore",
        "question": "Как зовут нейтрального босса, из которого выпадает Aegis of the Immortal?",
        "options": ["Roshan", "Tormentor", "Satanic", "Ancient Blue Dragon"],
        "correct": "Roshan",
        "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aegis.png"
    },
    {
        "category": "lore",
        "question": "Кто выиграл самый первый The International (TI1) в 2011 году?",
        "options": ["Natus Vincere (Na'Vi)", "EHOME", "Invictus Gaming", "Alliance"],
        "correct": "Natus Vincere (Na'Vi)",
        "image": "https://images.steamusercontent.com/ugc/576673666601445763/305E82B4BC6F97354674E9F76288593F38992D23/"
    }
]

class QuizStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_rank = State()
    choosing_category = State()
    in_quiz = State()

def main_menu():
    kb = [
        [KeyboardButton(text="🎯 Пройти тест")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="👤 Профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def category_keyboard():
    kb = [
        [InlineKeyboardButton(text="🎲 Все категории (12 вопросов)", callback_data="cat_all")],
        [InlineKeyboardButton(text="🗡 Предметы", callback_data="cat_items")],
        [InlineKeyboardButton(text="🧙‍♂️ Герои и Механики", callback_data="cat_heroes")],
        [InlineKeyboardButton(text="🏆 Киберспорт и Лор", callback_data="cat_lore")]
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
        msg = await message.answer("Привет! Добро пожаловать в «ДотаМозг»! 🧠\n\nВведи свой игровой никнейм:")
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(QuizStates.waiting_for_nickname)
    else:
        await message.answer(f"Добро пожаловать, {user[0]}!", reply_markup=main_menu())

@dp.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()
    await state.clear()
    await message.answer("🔄 Ваш профиль полностью очищен!\nНажмите /start для регистрации.")

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
    
    msg = await message.answer("Выбери свой текущий ранг в Dota 2:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.update_data(last_msg_id=msg.message_id)
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

    await safe_delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(f"Профиль сохранён! Ваш ранг: **{selected_rank}**.", parse_mode="Markdown", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "🎯 Пройти тест")
async def ask_category(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])

    msg = await message.answer("Выбери режим:", reply_markup=category_keyboard())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(QuizStates.choosing_category)

@dp.callback_query(F.data.startswith("cat_"), QuizStates.choosing_category)
async def start_quiz_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    
    if cat == "all":
        items = [q for q in QUESTIONS_BASE if q.get("category") == "items"]
        heroes = [q for q in QUESTIONS_BASE if q.get("category") == "heroes"]
        lore = [q for q in QUESTIONS_BASE if q.get("category") == "lore"]

        block1 = random.sample(items, min(4, len(items)))
        block2 = random.sample(heroes, min(4, len(heroes)))
        block3 = random.sample(lore, min(4, len(lore)))

        selected_questions = block1 + block2 + block3
    else:
        pool = [q for q in QUESTIONS_BASE if q.get("category") == cat]
        selected_questions = random.sample(pool, min(len(pool), 12))

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

        text = (
            f"🎉 **Тест завершён!**\n\n"
            f"✅ Правильных ответов: **{correct} из {total}**\n\n"
            f"Результаты обновлены в меню «📊 Моя статистика»."
        )
        msg = await bot.send_message(chat_id, text, parse_mode="Markdown")
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(None)
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]
    q_text = f"**Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"

    if "image" in q and q["image"]:
        msg = await bot.send_photo(chat_id, photo=q["image"], caption=q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        msg = await bot.send_message(chat_id, text=q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

    await state.update_data(last_msg_id=msg.message_id)

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

    await asyncio.sleep(0.5)
    await render_question(callback.message.chat.id, state)

@dp.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])

    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, rank, total_questions, correct_answers, wrong_answers FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        msg = await message.answer("Профиль не найден. Напишите /start для регистрации.")
        await state.update_data(last_msg_id=msg.message_id)
        return

    nick, rank, total, correct, wrong = user_data
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    stats_text = (
        f"📊 **Личная статистика**\n\n"
        f"👤 **Игрок:** {nick}\n"
        f"🎖 **Ранг:** {rank}\n"
        f"🎯 **Всего ответов:** {total}\n"
        f"✅ **Правильных:** {correct}\n"
        f"❌ **Ошибок:** {wrong}\n"
        f"📈 **Точность:** {accuracy}%"
    )
    msg = await message.answer(stats_text, parse_mode="Markdown")
    await state.update_data(last_msg_id=msg.message_id)

@dp.message(F.text == "👤 Профиль")
async def change_rank_prompt(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])

    ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
    kb = []
    for i in range(0, len(ranks), 2):
        row = [InlineKeyboardButton(text=ranks[i], callback_data=f"rank_{ranks[i]}")]
        if i + 1 < len(ranks):
            row.append(InlineKeyboardButton(text=ranks[i+1], callback_data=f"rank_{ranks[i+1]}"))
        kb.append(row)
    
    msg = await message.answer("Выбери новый ранг для своего профиля:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(QuizStates.waiting_for_rank)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
