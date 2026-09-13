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
    # --- КАТЕГОРИЯ: Предметы и Рецепты ---
    {
        "category": "items",
        "question": "Какой предмет даёт полный иммунитет к эффектам заклинаниям на время действия?",
        "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Pipe of Insight"],
        "correct": "Black King Bar"
    },
    {
        "category": "items",
        "question": "Какой предмет собирается из Blink Dagger и Reaver?",
        "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Wind Waker"],
        "correct": "Overwhelming Blink"
    },
    {
        "category": "items",
        "question": "Сколько стоит рецепт для сборки Hand of Midas?",
        "options": ["1750", "1500", "1400", "2200"],
        "correct": "1750"
    },
    {
        "category": "items",
        "question": "Какой предмет даёт эффект 'True Sight' вокруг владельца?",
        "options": ["Dust of Appearance", "Sentry Ward", "Gem of True Sight", "Shadow Blade"],
        "correct": "Gem of True Sight"
    },
    {
        "category": "items",
        "question": "Какое максимальное число зарядов может хранить Magic Wand?",
        "options": ["10", "15", "20", "25"],
        "correct": "20"
    },
    {
        "category": "items",
        "question": "Какой предмет даёт способность пассивно наносить урон вокруг себя огнём?",
        "options": ["Radiance", "Shiva's Guard", "Maelstrom", "Battle Fury"],
        "correct": "Radiance"
    },
    {
        "category": "items",
        "question": "Сколько секунд длится действие Aegis of the Immortal в инвентаре?",
        "options": ["3 минуты", "5 минут", "6 минут", "10 минут"],
        "correct": "5 минут"
    },
    {
        "category": "items",
        "question": "Какой предмет мгновенно снимает большинство негативных эффектов и создаёт 2 иллюзии?",
        "options": ["Manta Style", "Sange and Yasha", "Satanic", "Nullifier"],
        "correct": "Manta Style"
    },
    {
        "category": "items",
        "question": "Какой из этих предметов НЕ покупается в потайной лавке (Secret Shop)?",
        "options": ["Demon Edge", "Reaver", "Hyperstone", "Claymore"],
        "correct": "Claymore"
    },
    {
        "category": "items",
        "question": "Какой артефакт сжигает ману цели при каждой физической атаке?",
        "options": ["Diffusal Blade", "Desolator", "MKB", "Basher"],
        "correct": "Diffusal Blade"
    },

    # --- КАТЕГОРИЯ: Герои и Механики ---
    {
        "category": "heroes",
        "question": "Какой атрибут является основным для героя Pudge?",
        "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"],
        "correct": "Сила"
    },
    {
        "category": "heroes",
        "question": "Сколько сфер у Invoker вокруг него одновременно?",
        "options": ["2", "3", "4", "5"],
        "correct": "3"
    },
    {
        "category": "heroes",
        "question": "Как называется ультимейт героя Rubick?",
        "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"],
        "correct": "Spell Steal"
    },
    {
        "category": "heroes",
        "question": "Какой атрибут был добавлен в Dota 2 в обновлении 7.33?",
        "options": ["Магия", "Универсальный", "Стойкость", "Мудрость"],
        "correct": "Универсальный"
    },
    {
        "category": "heroes",
        "question": "Какой герой может создавать полноценные копии самого себя с помощью способности Divided We Stand?",
        "options": ["Phantom Lancer", "Naga Siren", "Meepo", "Chaos Knight"],
        "correct": "Meepo"
    },
    {
        "category": "heroes",
        "question": "Какой герой произносит знаменитую фразу 'Fresh meat!'?",
        "options": ["Lifestealer", "Pudge", "Doom", "Night Stalker"],
        "correct": "Pudge"
    },
    {
        "category": "heroes",
        "question": "Какая способность Butcher (Pudge) притягивает врага или союзника к себе?",
        "options": ["Meat Hook", "Rot", "Dismember", "Flesh Heap"],
        "correct": "Meat Hook"
    },
    {
        "category": "heroes",
        "question": "Какой нейтральный объект появляется на 20-й минуте игры и даёт Aghanim's Shard?",
        "options": ["Рошан", "Терзатель (Tormentor)", "Аванпост", "Святилище"],
        "correct": "Терзатель (Tormentor)"
    },
    {
        "category": "heroes",
        "question": "Сколько активных заклинаний может призвать Invoker с помощью способности Invoke?",
        "options": ["8", "10", "12", "14"],
        "correct": "10"
    },
    {
        "category": "heroes",
        "question": "Какой герой может переманивать нейтральных крипов под свой контроль?",
        "options": ["Chen", "Enchantress", "Doom", "Все перечисленные"],
        "correct": "Все перечисленные"
    },

    # --- КАТЕГОРИЯ: Киберспорт и Лор ---
    {
        "category": "lore",
        "question": "Какая команда выиграла The International 2021 (TI10)?",
        "options": ["PSG.LGD", "OG", "Team Spirit", "Team Liquid"],
        "correct": "Team Spirit"
    },
    {
        "category": "lore",
        "question": "Какая команда выиграла первые два турнира The International подряд (TI8 и TI9)?",
        "options": ["Na'Vi", "OG", "Alliance", "Team Liquid"],
        "correct": "OG"
    },
    {
        "category": "lore",
        "question": "Как зовут нейтрального босса, из которого выпадает Aegis of the Immortal?",
        "options": ["Tormentor", "Roshan", "Satanic", "Ancient Blue Dragon"],
        "correct": "Roshan"
    },
    {
        "category": "lore",
        "question": "Как называется родной монастырь в лоре героя Anti-Mage?",
        "options": ["Турстаркар", "Ясеневый лес", "Подземный город", "Остров Ультима"],
        "correct": "Турстаркар"
    },
    {
        "category": "lore",
        "question": "Кто выиграл самый первый The International (TI1) в 2011 году?",
        "options": ["Natus Vincere (Na'Vi)", "EHOME", "Invictus Gaming", "Alliance"],
        "correct": "Natus Vincere (Na'Vi)"
    },

    # --- КАТЕГОРИЯ: Угадай по картинке ---
    {
        "category": "photo",
        "photo": "https://raw.githubusercontent.com/dotabuff/dota2-skills/master/images/pudge_meat_hook.png",
        "question": "Чья это иконка способности?",
        "options": ["Pudge (Meat Hook)", "Clockwerk (Hookshot)", "Vengeful Spirit", "Abaddon"],
        "correct": "Pudge (Meat Hook)"
    },
    {
        "category": "photo",
        "photo": "https://raw.githubusercontent.com/dotabuff/dota2-skills/master/images/invoker_sun_strike.png",
        "question": "Как называется эта способность Invoker?",
        "options": ["Sun Strike", "Chaos Meteor", "EMP", "Deafening Blast"],
        "correct": "Sun Strike"
    },
    {
        "category": "photo",
        "photo": "https://raw.githubusercontent.com/dotabuff/dota2-skills/master/images/enigma_black_hole.png",
        "question": "Какая способность изображена на картинке?",
        "options": ["Black Hole", "Chronosphere", "Supernova", "Reverse Polarity"],
        "correct": "Black Hole"
    },
    {
        "category": "photo",
        "photo": "https://raw.githubusercontent.com/dotabuff/dota2-skills/master/images/juggernaut_omnislash.png",
        "question": "Какой герой использует эту ультимативную способность?",
        "options": ["Juggernaut", "Sven", "Phantom Assassin", "Slayer"],
        "correct": "Juggernaut"
    }
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
        [InlineKeyboardButton(text="🗡 Предметы и Рецепты", callback_data="cat_items")],
        [InlineKeyboardButton(text="🧙‍♂️ Герои и Механики", callback_data="cat_heroes")],
        [InlineKeyboardButton(text="🏆 Киберспорт и Лор", callback_data="cat_lore")],
        [InlineKeyboardButton(text="🖼 Угадай по картинке", callback_data="cat_photo")],
        [InlineKeyboardButton(text="🎲 Микс (Все категории)", callback_data="cat_all")]
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

@dp.message(F.text == "🎮 Начать викторину")
async def ask_category(message: types.Message, state: FSMContext):
    await message.answer("Выбери категорию вопросов для раунда:", reply_markup=category_keyboard())
    await state.set_state(QuizStates.choosing_category)

@dp.callback_query(F.data.startswith("cat_"), QuizStates.choosing_category)
async def start_quiz_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    
    if cat == "all":
        pool = QUESTIONS_BASE
    else:
        pool = [q for q in QUESTIONS_BASE if q.get("category") == cat]

    count = min(QUESTIONS_PER_QUIZ, len(pool))
    selected_questions = random.sample(pool, count)

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=selected_questions,
        current_index=0,
        correct_count=0,
        wrong_count=0
    )
    try:
        await callback.message.delete()
    except Exception:
        pass
    await send_next_question(callback.message, state)

async def send_next_question(message: types.Message, state: FSMContext):
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

        text = f"🎉 **Викторина окончена!**\n\nПравильных ответов: {correct} из {total}\nПосмотри результаты в «🏆 Моя доска почёта»."
        await message.answer(text, parse_mode="Markdown", reply_markup=main_menu())
        await state.clear()
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]

    q_text = f"**Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"

    if "photo" in q and q["photo"]:
        await message.answer_photo(photo=q["photo"], caption=q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        await message.answer(q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

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
        await callback.answer(f"❌ Неверно! Правильный ответ: {q['correct']}", show_alert=True)
        correct_count = data["correct_count"]
        wrong_count = data["wrong_count"] + 1

    await state.update_data(
        current_index=index + 1,
        correct_count=correct_count,
        wrong_count=wrong_count
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass

    await send_next_question(callback.message, state)

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
