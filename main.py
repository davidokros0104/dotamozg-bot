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

# БАЗА 120+ ВОПРОСОВ
QUESTIONS_BASE = [
    # --- ПРЕДМЕТЫ (ITEMS) ---
    {"category": "items", "question": "Какой предмет дает полный иммунитет к магии на время действия?", "options": ["Шестигранный жезл", "Black King Bar", "Linken's Sphere", "Lotus Orb"], "correct": "Black King Bar"},
    {"category": "items", "question": "Какой предмет собирается из Blink Dagger и Reaver?", "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Soul Ring"], "correct": "Overwhelming Blink"},
    {"category": "items", "question": "Сколько стоит рецепт для сборки Hand of Midas?", "options": ["1750", "1500", "1850", "2000"], "correct": "1750"},
    {"category": "items", "question": "Какое максимальное число зарядов может хранить Magic Wand?", "options": ["20", "15", "10", "25"], "correct": "20"},
    {"category": "items", "question": "Какой предмет дает эффект 'True Sight' вокруг владельца?", "options": ["Gem of True Sight", "Dust of Appearance", "Sentry Ward", "Shadow Amulet"], "correct": "Gem of True Sight"},
    {"category": "items", "question": "Какой предмет выпадает при уничтожении Терзателя (Tormentor)?", "options": ["Aghanim's Shard", "Aghanim's Scepter", "Cheese", "Refresher Shard"], "correct": "Aghanim's Shard"},
    {"category": "items", "question": "Какой предмет дает наибольший бонус к интеллекту?", "options": ["Scythe of Vyse", "Shiva's Guard", "Octarine Core", "Kaya and Sange"], "correct": "Scythe of Vyse"},
    {"category": "items", "question": "Какой из этих предметов собирается из Daedalus и Sacred Relic?", "options": ["Никакой (нет такого рецепта)", "Divine Rapier", "Nullifier", "Bloodthorn"], "correct": "Никакой (нет такого рецепта)"},
    {"category": "items", "question": "Сколько секунд длится перезарядка Blink Dagger после получения урона от игрока?", "options": ["3 сек", "5 сек", "2 сек", "4 сек"], "correct": "3 сек"},
    {"category": "items", "question": "Какой предмет снижает перезарядку всех способностей и предметов на 25%?", "options": ["Octarine Core", "Kaya", "Spell Prism", "Refresher Orb"], "correct": "Octarine Core"},
    {"category": "items", "question": "Какой предмет вражеского юнита в безвредное существо (Hex)?", "options": ["Scythe of Vyse", "Eul's Scepter of Divinity", "Orchid Malevolence", "Rod of Atos"], "correct": "Scythe of Vyse"},
    {"category": "items", "question": "Сколько стоит Sentry Ward в лавке?", "options": ["50", "75", "100", "0"], "correct": "50"},
    {"category": "items", "question": "Какова базовая стоимость Town Portal Scroll?", "options": ["100", "90", "75", "50"], "correct": "100"},
    {"category": "items", "question": "Какой артефакт дает вампиризм от заклинаний?", "options": ["Bloodstone", "Satanic", "Voodoo Mask", "Heart of Tarrasque"], "correct": "Bloodstone"},
    {"category": "items", "question": "Какой предмет дает активную способность 'Echo Sweep'?", "options": ["Echo Sabre", "Manta Style", "Harpoon", "Diffusal Blade"], "correct": "Echo Sabre"},
    {"category": "items", "question": "Сколько здоровья восстанавливает Cheese при использовании?", "options": ["2500", "1500", "2000", "3000"], "correct": "2500"},
    {"category": "items", "question": "Какой предмет ТРЕБУЕТ покупку рецепта?", "options": ["Manta Style", "Force Staff", "Blink Dagger", "Boots of Speed"], "correct": "Manta Style"},
    {"category": "items", "question": "Какой эффект накладывает предмет Spirit Vessel на врага?", "options": ["Снижает лечение и наносит урон", "Оглушает", "Замедляет и безмолвит", "Обездвиживает"], "correct": "Снижает лечение и наносит урон"},
    {"category": "items", "question": "Какой из этих предметов НЕ продается в Потайной лавке (Secret Shop)?", "options": ["Hyperstone", "Demon Edge", "Ultimate Orb", "Claymore"], "correct": "Claymore"},
    {"category": "items", "question": "Какой предмет временно снимает положительные эффекты с врага при активации?", "options": ["Nullifier", "Diffusal Blade", "Orchid Malevolence", "Heavens Halberd"], "correct": "Nullifier"},
    {"category": "items", "question": "Сколько дает брони Ring of Protection?", "options": ["2", "3", "1", "4"], "correct": "2"},
    {"category": "items", "question": "Какова длительность действия Smoke of Deceit?", "options": ["45 сек", "30 сек", "60 сек", "35 сек"], "correct": "35 сек"},
    {"category": "items", "question": "Какой предмет собирается из Shadow Blade и Ultimate Orb?", "options": ["Silver Edge", "Bloodthorn", "Nullifier", "Kaya and Sange"], "correct": "Silver Edge"},
    {"category": "items", "question": "Какой предмет дает пассивный прорубающий урон (Cleave)?", "options": ["Battle Fury", "Maelstrom", "Desolator", "Radiance"], "correct": "Battle Fury"},
    {"category": "items", "question": "Сколько маны восстанавливает Clarity при полном срабатывании?", "options": ["150", "100", "180", "200"], "correct": "150"},
    {"category": "items", "question": "Какой предмет дает максимальный пассивный шанс критического удара?", "options": ["Daedalus", "Crystalys", "Bloodthorn", "Witch Blade"], "correct": "Daedalus"},
    {"category": "items", "question": "Какой из артефактов накладывает эффект 'Disarm' (Бессилие) на цель?", "options": ["Heaven's Halberd", "Rod of Atos", "Solar Crest", "Abyssal Blade"], "correct": "Heaven's Halberd"},
    {"category": "items", "question": "Какой предмет собирается из Helm of Iron Will и Crown?", "options": ["Armlet of Mordiggian", "Helm of the Dominator", "Veil of Discord", "Buckler"], "correct": "Helm of the Dominator"},
    {"category": "items", "question": "Какое преимущество дает предмет Phase Boots в активном состоянии?", "options": ["Прохождение сквозь юнитов и скорость", "Неуязвимость", "Дополнительную броню", "Teleportation"], "correct": "Прохождение сквозь юнитов и скорость"},
    {"category": "items", "question": "Какой предмет создает иллюзии вашего героя при использовании?", "options": ["Manta Style", "Phantasm", "Disruption", "Shadow Amulet"], "correct": "Manta Style"},
    {"category": "items", "question": "Сколько секунд длится активный эффект Satanic (Unholy Rage)?", "options": ["6 сек", "5 сек", "4 сек", "8 сек"], "correct": "6 сек"},
    {"category": "items", "question": "Какой предмет дает пассивное сжигание маны при атаках?", "options": ["Diffusal Blade", "Maelstrom", "Radiance", "Desolator"], "correct": "Diffusal Blade"},
    {"category": "items", "question": "Сколько стоит Observer Ward в лавке?", "options": ["0", "50", "75", "25"], "correct": "0"},
    {"category": "items", "question": "Какой предмет блокирует следующее направленное вражеское заклинание?", "options": ["Linken's Sphere", "Lotus Orb", "Black King Bar", "Aeon Disk"], "correct": "Linken's Sphere"},
    {"category": "items", "question": "Какой из предметов снижает броню цели при атаках?", "options": ["Desolator", "Solar Crest", "Medallion of Courage", "Assault Cuirass"], "correct": "Desolator"},
    {"category": "items", "question": "Какой артефакт срабатывает автоматически при падении здоровья ниже 70%?", "options": ["Aeon Disk", "Heart of Tarrasque", "Satanic", "Linken's Sphere"], "correct": "Aeon Disk"},
    {"category": "items", "question": "Какой предмет собирается из Ogre Axe, Staff of Wizardry и Blade of Alacrity?", "options": ["Aghanim's Scepter", "Ultimate Orb", "Kaya and Sange", "Sange and Yasha"], "correct": "Aghanim's Scepter"},
    {"category": "items", "question": "Какой предмет дает активную ауру-эффект защиты от магии союзникам?", "options": ["Pipe of Insight", "Crimson Guard", "Mekansm", "Guardian Greaves"], "correct": "Pipe of Insight"},
    {"category": "items", "question": "Какую скорость передвижения прибавляет предмет Boots of Speed?", "options": ["45", "50", "40", "35"], "correct": "45"},

    # --- ГЕРОИ И МЕХАНИКИ (HEROES) ---
    {"category": "heroes", "question": "Какой атрибут является основным для героя Pudge?", "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"], "correct": "Сила"},
    {"category": "heroes", "question": "Сколько сфер у Invoker одновременно вращается вокруг него?", "options": ["3", "4", "5", "2"], "correct": "3"},
    {"category": "heroes", "question": "Как называется ультимейт героя Rubick?", "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"], "correct": "Spell Steal"},
    {"category": "heroes", "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?", "options": ["Meepo", "Phantom Lancer", "Naga Siren", "Terrorblade"], "correct": "Meepo"},
    {"category": "heroes", "question": "Какой герой имеет наибольшую базовую дальность атаки в игре?", "options": ["Techies", "Sniper", "Lina", "Clinkz"], "correct": "Techies"},
    {"category": "heroes", "question": "Какое максимальное количество душ может собирать Shadow Fiend без Aghanim's Scepter?", "options": ["20", "36", "18", "40"], "correct": "20"},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Global Silence'?", "options": ["Silencer", "Disruptor", "Death Prophet", "Drow Ranger"], "correct": "Silencer"},
    {"category": "heroes", "question": "Какой герой может погрузить себя способностью Reincarnation?", "options": ["Wraith King", "Undying", "Abaddon", "Skeleton King"], "correct": "Wraith King"},
    {"category": "heroes", "question": "Какой герой может переместиться в любую точку карты к союзному юниту ультимейтом?", "options": ["Underlord", "Nature's Prophet", "Tinker", "Io"], "correct": "Underlord"},
    {"category": "heroes", "question": "Какая способность Axe принуждает врагов атаковать его?", "options": ["Berserker's Call", "Battle Hunger", "Counter Helix", "Culling Blade"], "correct": "Berserker's Call"},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Chronosphere'?", "options": ["Faceless Void", "Enigma", "Tidehunter", "Void Spirit"], "correct": "Faceless Void"},
    {"category": "heroes", "question": "Какая основная характеристика у героя Invoker после патча 7.337?", "options": ["Универсальный", "Интеллект", "Сила", "Ловкость"], "correct": "Универсальный"},
    {"category": "heroes", "question": "Как называется ультимативная способность героя Enigma?", "options": ["Black Hole", "Midnight Pulse", "Malefice", "Gravity Well"], "correct": "Black Hole"},
    {"category": "heroes", "question": "Как называется ультимейт героя Earthshaker?", "options": ["Echo Slam", "Fissure", "Enchant Totem", "Aftershock"], "correct": "Echo Slam"},
    {"category": "heroes", "question": "Как называется ультимативная способность Tidehunter?", "options": ["Ravage", "Gush", "Anchor Smash", "Kraken Shell"], "correct": "Ravage"},
    {"category": "heroes", "question": "Какой герой использует способность 'Reverse Polarity' (RP)?", "options": ["Magnus", "Enigma", "Sardar", "Tidehunter"], "correct": "Magnus"},
    {"category": "heroes", "question": "Какой ультимейт у героя Juggernaut?", "options": ["Omnislash", "Blade Fury", "Healing Ward", "Blade Dance"], "correct": "Omnislash"},
    {"category": "heroes", "question": "Какой герой может летать сквозь деревья способностью Firefly?", "options": ["Batrider", "Dragon Knight", "Viper", "Jakiro"], "correct": "Batrider"},
    {"category": "heroes", "question": "Какой герой при смерти выпускает снаряды способностью 'Requiem of Souls'?", "options": ["Shadow Fiend", "Nevermore", "Terrorblade", "Doom"], "correct": "Shadow Fiend"},
    {"category": "heroes", "question": "Как называется пассивная способность Bristleback, снижающая урон со спины?", "options": ["Bristleback", "Viscous Nasal Goo", "Quill Spray", "Warpath"], "correct": "Bristleback"},
    {"category": "heroes", "question": "Какая способность Sniper увеличивает дальность его атаки?", "options": ["Take Aim", "Headshot", "Shrapnel", "Assassinate"], "correct": "Take Aim"},
    {"category": "heroes", "question": "Какой герой спавнит иллюзии с помощью пассивки Juxtapose?", "options": ["Phantom Lancer", "Naga Siren", "Terrorblade", "Chaos Knight"], "correct": "Phantom Lancer"},
    {"category": "heroes", "question": "Какой герой обладает ультимейтом 'Supernova'?", "options": ["Phoenix", "Lina", "Jakiro", "Dragon Knight"], "correct": "Phoenix"},
    {"category": "heroes", "question": "Какой атрибут является основным для героя Anti-Mage?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Ловкость"},
    {"category": "heroes", "question": "Какой герой умеет мгновенно перемещаться к деревьям способностью Tree Dance?", "options": ["Monkey King", "Hoodwink", "Treant Protector", "Timbersaw"], "correct": "Monkey King"},
    {"category": "heroes", "question": "Как называется ультимейт героя Sven?", "options": ["God's Strength", "Storm Hammer", "Great Cleave", "Warcry"], "correct": "God's Strength"},
    {"category": "heroes", "question": "Какой герой призывает 'Медведя' (Bear) как отдельного юнита?", "options": ["Lone Druid", "Ursa", "Lycan", "Beastmaster"], "correct": "Lone Druid"},
    {"category": "heroes", "question": "Какая способность Dazzle предотвращает смерть союзника на 5 секунд?", "options": ["Shallow Grave", "Poison Touch", "Shadow Wave", "Bad Juju"], "correct": "Shallow Grave"},
    {"category": "heroes", "question": "Какой герой крадет интеллект у вражеских героев при их смерти неподалеку?", "options": ["Silencer", "Outworld Destroyer", "Pugna", "Skywrath Mage"], "correct": "Silencer"},
    {"category": "heroes", "question": "Как называется способность 'Doom', запрещающая магию и предметы?", "options": ["Doom", "Devour", "Scorched Earth", "Infernal Blade"], "correct": "Doom"},
    {"category": "heroes", "question": "Как называется ультимейт Storm Spirit?", "options": ["Ball Lightning", "Electric Vortex", "Static Remnant", "Overload"], "correct": "Ball Lightning"},

    # --- КИБЕРСПОРТ И ЛОР (LORE / ESPORTS) ---
    {"category": "lore", "question": "Какая фракция защищает Древнего (Ancient) в Dota 2?", "options": ["Radiant (Силы Света) / Dire (Силы Тьмы)", "Sentinel / Scourge", "Alliance / Horde", "Order / Chaos"], "correct": "Radiant (Силы Света) / Dire (Силы Тьмы)"},
    {"category": "lore", "question": "Какая команда выиграла The International 2021 (TI10)?", "options": ["Team Spirit", "PSG.LGD", "OG", "Secret"], "correct": "Team Spirit"},
    {"category": "lore", "question": "Какая команда выиграла два TI подряд (TI8 и TI9)?", "options": ["OG", "Na'Vi", "Liquid", "EG"], "correct": "OG"},
    {"category": "lore", "question": "Как зовут нейтрального Босса, из которого выпадает Aegis of the Immortal?", "options": ["Roshan", "Tormentor", "Ancient Apparition", "Kongor"], "correct": "Roshan"},
    {"category": "lore", "question": "Кто выиграл самый первый The International (TI1) в 2011 году?", "options": ["Natus Vincere (Na'Vi)", "EHOME", "Scythe Gaming", "DK"], "correct": "Natus Vincere (Na'Vi)"},
    {"category": "lore", "question": "Как называется главный приз турнира The International?", "options": ["Aegis of Champions", "Summoner's Cup", "The TI Trophy", "Immortal Shield"], "correct": "Aegis of Champions"},
    {"category": "lore", "question": "Какое имя носит Брат-Близнец героя Anti-Mage в лоре игры?", "options": ["Terrorblade", "Soulkeeper", "Magina", "Invoker"], "correct": "Terrorblade"},
    {"category": "lore", "question": "Как зовут Богиню Луны, которой поклоняются Mirana и Luna?", "options": ["Selemene", "Verodicia", "Nyx", "Skadi"], "correct": "Selemene"},
    {"category": "lore", "question": "Как называется родной мир героя Void Spirit?", "options": ["Hidden Temple", "Aether Realm", "Violet Plateau", "The Void"], "correct": "Aether Realm"},
    {"category": "lore", "question": "Какая команда выиграла The International 2013 на легендарном пятом карте финала?", "options": ["Alliance", "Na'Vi", "Orange", "TongFu"], "correct": "Alliance"},
    {"category": "lore", "question": "Как зовут дракона, в которого превращается Dragon Knight на 3-ем уровне ультимейта?", "options": ["Blue Dragon (Frost)", "Red Dragon", "Green Dragon", "Black Dragon"], "correct": "Blue Dragon (Frost)"},
    {"category": "lore", "question": "Какая страна принимала турнир The International 2018 (TI8)?", "options": ["Канада", "США", "Китай", "Румыния"], "correct": "Канада"},
    {"category": "lore", "question": "Как называется родной мир героя Void Spirit и других Спиритов?", "options": ["Hidden Temple", "The Void", "Aether Realm", "Confluence"], "correct": "Aether Realm"},
    {"category": "lore", "question": "Кем по лору является герой Pudge?", "options": ["Мясником на поле битвы тел", "Палачом короля", "Демоном Бездны", "Пожирателем душ"], "correct": "Мясником на поле битвы тел"},
    {"category": "lore", "question": "Какой игрок известен своим легендарным 'Pudge + Chen' (Fountain Hook) на TI3?", "options": ["Dendi", "Puppey", "Loda", "ChuaN"], "correct": "Dendi"},
    {"category": "lore", "question": "Какая фракция противостоит Radiant в Dota 2?", "options": ["Dire (Силы Тьмы)", "Scourge", "Shadow", "Abyss"], "correct": "Dire (Силы Тьмы)"},
    {"category": "lore", "question": "Как называется место, куда попадают души умерших героев перед перерожденьем (в лоре Razor и Visage)?", "options": ["Underscape", "Narrow Maze", "Nether Realm", "Hell"], "correct": "Narrow Maze"},
    {"category": "lore", "question": "Какой герой является заклятым врагом Tidehunter?", "options": ["Kunkka", "Slardar", "Naga Siren", "Morphling"], "correct": "Kunkka"},
    {"category": "lore", "question": "Какая финская организация выиграла The International 2017 (TI7)?", "options": ["Team Liquid", "OG", "Newbee", "Virtus.pro"], "correct": "Team Liquid"},
    {"category": "lore", "question": "Как зовут фундаментала, представляющего собой силу притяжения (Gravity)?", "options": ["Enigma", "Keeper of the Light", "Chaos Knight", "Io"], "correct": "Enigma"}
]

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
        [InlineKeyboardButton(text="🛡 Герои и Механики", callback_data="cat_heroes")],
        [InlineKeyboardButton(text="🏆 Киберспорт и Лор", callback_data="cat_lore")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ЕДИНСТВЕННОЕ ОБНОВЛЕННОЕ МЕСТО: ЭФФЕКТ СВОРАЧИВАНИЯ СООБЩЕНИЙ
async def safe_delete_message(chat_id: int, message_id: int):
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⌛")
        await asyncio.sleep(0.2)
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
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
    await callback.message.answer(f"Профиль обновлён! Ваш ранг: **{selected_rank}**.", parse_mode="Markdown", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text.in_(["📝 Пройти тест", "Играть", "играть"]))
@dp.callback_query(F.data == "restart_quiz")
async def ask_category(event: types.Message | types.CallbackQuery, state: FSMContext):
    chat_id = event.chat.id if isinstance(event, types.Message) else event.message.chat.id
    message_id = event.message_id if isinstance(event, types.Message) else event.message.message_id

    await safe_delete_message(chat_id, message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(chat_id, data["last_msg_id"])

    msg = await bot.send_message(chat_id, "Выбери режим тестирования:", reply_markup=category_keyboard())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(QuizStates.choosing_category)

@dp.callback_query(F.data.startswith("cat_"), QuizStates.choosing_category)
async def start_quiz_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    
    if cat == "all":
        pool = QUESTIONS_BASE.copy()
    else:
        pool = [q for q in QUESTIONS_BASE if q.get("category") == cat]

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

        text = (
            f"🎉 **Тест завершен!**\n\n"
            f"🎯 Правильно ответов: **{correct}** из {total}!\n\n"
            f"📊 Посмотреть статистику можно в разделе 📊 Моя статистика."
        )

        restart_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Пройти еще раз", callback_data="restart_quiz")]
        ])

        await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())
        msg = await bot.send_message(chat_id, "Хотите сыграть еще раз?", reply_markup=restart_kb)
        
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(None)
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]
    q_text = f"**Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"
    image_url = q.get("image") or BACKGROUND_IMAGES.get(q.get("category"), BACKGROUND_IMAGES["general"])

    try:
        msg = await bot.send_photo(chat_id, photo=image_url, caption=q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except Exception:
        msg = await bot.send_message(chat_id, q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

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
        msg = await message.answer("Профиль не найден. Нажмите /start для регистрации.", reply_markup=main_menu())
        await state.update_data(last_msg_id=msg.message_id)
        return

    nick, rank, total, correct, wrong = user_data
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    stats_text = (
        f"📊 **Личная статистика**\n\n"
        f"👤 **Игрок:** {nick}\n"
        f"🏆 **Ранг:** {rank}\n"
        f"🎯 **Всего ответов:** {total}\n"
        f"✅ **Правильных:** {correct}\n"
        f"❌ **Ошибок:** {wrong}\n"
        f"📈 **Точность:** {accuracy}%"
    )

    msg = await message.answer(stats_text, parse_mode="Markdown", reply_markup=main_menu())
    await state.update_data(last_msg_id=msg.message_id)

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])

    conn = sqlite3.connect("dotamozg.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, rank FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        msg = await message.answer("Профиль не найден. Нажмите /start для регистрации.", reply_markup=main_menu())
        await state.update_data(last_msg_id=msg.message_id)
        return

    nick, rank = user_data
    profile_text = (
        f"👤 **Ваш профиль**\n\n"
        f"⚙️ **Никнейм:** {nick}\n"
        f"🏆 **Текущий ранг:** {rank}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Изменить ранг", callback_data="change_rank")]
    ])

    msg = await message.answer(profile_text, parse_mode="Markdown", reply_markup=kb)
    await state.update_data(last_msg_id=msg.message_id)

@dp.callback_query(F.data == "change_rank")
async def change_rank_prompt(callback: types.CallbackQuery, state: FSMContext):
    ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
    kb = []
    for i in range(0, len(ranks), 2):
        row = [InlineKeyboardButton(text=ranks[i], callback_data=f"rank_{ranks[i]}")]
        if i + 1 < len(ranks):
            row.append(InlineKeyboardButton(text=ranks[i+1], callback_data=f"rank_{ranks[i+1]}"))
        kb.append(row)

    await callback.message.edit_text("Выбери новый ранг для своего профиля:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(QuizStates.waiting_for_rank)

# --- ДОБАВЛЕННЫЙ ВЕБ-СЕРВЕР ДЛЯ НЕПРЕРЫВНОЙ РАБОТЫ НА RENDER (FREE TIER) ---
async def handle(request):
    return web.Response(text="DotaMozg Bot is online 24/7!")

async def start_website():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    asyncio.create_task(start_website())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
