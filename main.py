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

# ПОЛНАЯ БАЗА: 120+ ВОПРОСОВ (ПО 40+ В КАЖДОЙ КАТЕГОРИИ)
QUESTIONS_BASE = [
    # --- ПРЕДМЕТЫ (ITEMS) ---
    {"category": "items", "question": "Какой предмет даёт полный иммунитет к магии на время действия?", "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Pipe of Insight"], "correct": "Black King Bar", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/black_king_bar.png"},
    {"category": "items", "question": "Какой предмет собирается из Blink Dagger и Reaver?", "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Wind Waker"], "correct": "Overwhelming Blink", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/overwhelming_blink.png"},
    {"category": "items", "question": "Сколько стоит рецепт для сборки Hand of Midas?", "options": ["1750", "1500", "1400", "2200"], "correct": "1750", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/hand_of_midas.png"},
    {"category": "items", "question": "Какое максимальное число зарядов может хранить Magic Wand?", "options": ["20", "15", "10", "25"], "correct": "20", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/magic_wand.png"},
    {"category": "items", "question": "Какой предмет даёт эффект 'True Sight' вокруг владельца?", "options": ["Gem of True Sight", "Dust of Appearance", "Sentry Ward", "Shadow Blade"], "correct": "Gem of True Sight", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/gem.png"},
    {"category": "items", "question": "Какой предмет выпадает при уничтожении Торментора (Tormentor)?", "options": ["Aghanim's Shard", "Aegis of the Immortal", "Cheese", "Refresher Shard"], "correct": "Aghanim's Shard", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aghanims_shard.png"},
    {"category": "items", "question": "Какой предмет дает наибольший бонус к интеллекту?", "options": ["Scythe of Vyse", "Octarine Core", "Shiva's Guard", "Kaya and Sange"], "correct": "Scythe of Vyse", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/sheepstick.png"},
    {"category": "items", "question": "Какой из этих предметов собирается из Demon Edge и Sacred Relic?", "options": ["Divine Rapier", "Daedalus", "Abyssal Blade", "Monkey King Bar"], "correct": "Divine Rapier", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/rapier.png"},
    {"category": "items", "question": "Сколько секунд длится перезарядка Blink Dagger после получения урона от игрока?", "options": ["3 сек", "2 сек", "4 сек", "5 сек"], "correct": "3 сек", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/blink.png"},
    {"category": "items", "question": "Какой предмет снижает перезарядку всех способностей и предметов на 25%?", "options": ["Octarine Core", "Refresher Orb", "Arcane Blink", "Kaya"], "correct": "Octarine Core", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/octarine_core.png"},
    {"category": "items", "question": "Какой предмет превращает вражеского юнита в безобидное существо (Hex)?", "options": ["Scythe of Vyse", "Eul's Scepter of Divinity", "Orchid Malevolence", "Nullifier"], "correct": "Scythe of Vyse", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/sheepstick.png"},
    {"category": "items", "question": "Сколько стоит Sentry Ward в лавке?", "options": ["50", "75", "100", "0"], "correct": "50", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ward_sentry.png"},
    {"category": "items", "question": "Какова базовая стоимость Town Portal Scroll?", "options": ["100", "90", "75", "50"], "correct": "100", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/tpscroll.png"},
    {"category": "items", "question": "Какой артефакт дает вампиризм от заклинаний?", "options": ["Bloodstone", "Satanic", "Mask of Madness", "Vladmir's Offering"], "correct": "Bloodstone", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/bloodstone.png"},
    {"category": "items", "question": "Какой предмет даёт активную способность 'Echo Sweep'?", "options": ["Echo Sabre", "Maelstrom", "Battle Fury", "Meteor Hammer"], "correct": "Echo Sabre", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/echo_sabre.png"},
    {"category": "items", "question": "Сколько здоровья восстанавливает Cheese при использовании?", "options": ["2500", "1500", "2000", "3000"], "correct": "2500", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/cheese.png"},
    {"category": "items", "question": "Какой из этих предметов ТРЕБУЕТ покупки рецепта?", "options": ["Manta Style", "Heart of Tarrasque", "Sange and Yasha", "Butterfly"], "correct": "Manta Style", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/manta.png"},
    {"category": "items", "question": "Какой эффект накладывает предмет Spirit Vessel на врага?", "options": ["Снижает лечение и наносит урон", "Оглушает", "Безмолвие (Silence)", "Замедляет атаки"], "correct": "Снижает лечение и наносит урон", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/spirit_vessel.png"},
    {"category": "items", "question": "Какой из этих предметов НЕ продаётся в Потайной лавке (Secret Shop)?", "options": ["Claymore", "Demon Edge", "Reaver", "Sacred Relic"], "correct": "Claymore", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/claymore.png"},
    {"category": "items", "question": "Какой предмет временно снимает положительные эффекты с врага при активации?", "options": ["Nullifier", "Orchid Malevolence", "Rod of Atos", "Diffusal Blade"], "correct": "Nullifier", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/nullifier.png"},
    {"category": "items", "question": "Сколько даёт брони Ring of Protection?", "options": ["2", "3", "1", "4"], "correct": "2", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ring_of_protection.png"},
    {"category": "items", "question": "Какова длительность действия Smoke of Deceit?", "options": ["45 сек", "30 сек", "60 сек", "40 сек"], "correct": "45 сек", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/smoke_of_deceit.png"},
    {"category": "items", "question": "Какой предмет собирается из Shadow Blade и Ultimate Orb?", "options": ["Silver Edge", "Manta Style", "Linken's Sphere", "Bloodthorn"], "correct": "Silver Edge", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/silver_edge.png"},
    {"category": "items", "question": "Какой предмет даёт пассивный прорубающий урон (Cleave)?", "options": ["Battle Fury", "Maelstrom", "Radiance", "Desolator"], "correct": "Battle Fury", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/bfury.png"},
    {"category": "items", "question": "Сколько маны восстанавливает Clarity при полном срабатывании?", "options": ["150", "180", "120", "200"], "correct": "150", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/clarity.png"},
    {"category": "items", "question": "Какой предмет дает максимальный пассивный шанс критического удара?", "options": ["Daedalus", "Crystalys", "Bloodthorn", "Witch Blade"], "correct": "Daedalus", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/lesser_crit.png"},
    {"category": "items", "question": "Какой из артефактов накладывает эффект 'Disarm' (бессилие) на цель?", "options": ["Heaven's Halberd", "Solar Crest", "Abyssal Blade", "Eul's Scepter"], "correct": "Heaven's Halberd", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/heavens_halberd.png"},
    {"category": "items", "question": "Какой предмет собирается из Helm of Iron Will и Crown?", "options": ["Armlet of Mordiggian", "Veil of Discord", "Falcon Blade", "Null Talisman"], "correct": "Armlet of Mordiggian", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/armlet.png"},
    {"category": "items", "question": "Какое преимущество даёт предмет Phase Boots в активном состоянии?", "options": ["Прохождение сквозь юнитов и скорость", "Полный иммунитет к замедлению", "Увеличение урона на 50%", "Невидимость"], "correct": "Прохождение сквозь юнитов и скорость", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/phase_boots.png"},
    {"category": "items", "question": "Какой предмет создаёт иллюзию вашего героя при использовании?", "options": ["Manta Style", "Sange and Yasha", "Echo Sabre", "Diffusal Blade"], "correct": "Manta Style", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/manta.png"},
    {"category": "items", "question": "Сколько секунд длится активный эффект Satanic (Unholy Rage)?", "options": ["6 сек", "5 сек", "7 сек", "4 сек"], "correct": "6 сек", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/satanic.png"},
    {"category": "items", "question": "Какой предмет дает пассивное сжигание маны при атаках?", "options": ["Diffusal Blade", "Desolator", "Maelstrom", "Basher"], "correct": "Diffusal Blade", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/diffusal_blade.png"},
    {"category": "items", "question": "Сколько стоит Observer Ward в лавке?", "options": ["0", "50", "75", "25"], "correct": "0", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ward_observer.png"},
    {"category": "items", "question": "Какой предмет блокирует следующее направленное вражеское заклинание?", "options": ["Linken's Sphere", "Lotus Orb", "Black King Bar", "Aeon Disk"], "correct": "Linken's Sphere", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/sphere.png"},
    {"category": "items", "question": "Какой из предметов снижает броню цели при атаках?", "options": ["Desolator", "Sange", "Maelstrom", "Skadi"], "correct": "Desolator", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/desolator.png"},
    {"category": "items", "question": "Какой артефакт срабатывает автоматически при падении здоровья ниже 70%?", "options": ["Aeon Disk", "Heart of Tarrasque", "Bloodstone", "Satanic"], "correct": "Aeon Disk", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aeon_disk.png"},
    {"category": "items", "question": "Какой предмет собирается из Ogre Axe, Staff of Wizardry и Blade of Alacrity?", "options": ["Ultimate Orb", "Aghanim's Scepter", "Kaya and Sange", "Sange and Yasha"], "correct": "Aghanim's Scepter", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ultimate_scepter.png"},
    {"category": "items", "question": "Какой предмет даёт активный аура-эффект защиты от магии союзникам?", "options": ["Pipe of Insight", "Crimson Guard", "Mekanism", "Solar Crest"], "correct": "Pipe of Insight", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/pipe.png"},
    {"category": "items", "question": "Какую скорость передвижения прибавляет предмет Boots of Speed?", "options": ["45", "50", "40", "60"], "correct": "45", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/boots.png"},

    # --- ГЕРОИ И МЕХАНИКИ (HEROES) ---
    {"category": "heroes", "question": "Какой атрибут является основным для героя Pudge?", "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"], "correct": "Сила", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"},
    {"category": "heroes", "question": "Сколько сфер у Invoker одновременно вращается вокруг него?", "options": ["3", "2", "4", "5"], "correct": "3", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png"},
    {"category": "heroes", "question": "Как называется ультимейт героя Rubick?", "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"], "correct": "Spell Steal", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/rubick.png"},
    {"category": "heroes", "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?", "options": ["Meepo", "Phantom Lancer", "Naga Siren", "Chaos Knight"], "correct": "Meepo", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/meepo.png"},
    {"category": "heroes", "question": "Какой герой имеет наибольшую базовую дальность атаки в игре?", "options": ["Techies", "Sniper", "Lina", "Clinkz"], "correct": "Techies", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/techies.png"},
    {"category": "heroes", "question": "Какое максимальное количество душ может набрать Shadow Fiend без Aghanim's Scepter?", "options": ["20", "15", "25", "30"], "correct": "20", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/nevermore.png"},
    {"category": "heroes", "question": "Какой герой имеет способность 'Global Silence'?", "options": ["Silencer", "Disruptor", "Dark Seer", "Oracle"], "correct": "Silencer", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/silencer.png"},
    {"category": "heroes", "question": "Какой герой может воскрешать себя способностью Reincarnation?", "options": ["Wraith King", "Dazzle", "Oracle", "Abaddon"], "correct": "Wraith King", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/skeleton_king.png"},
    {"category": "heroes", "question": "Какой герой может перемещаться в любую точку карты к союзному юниту ультимейтом?", "options": ["Underlord", "Nature's Prophet", "Io", "Spectre"], "correct": "Underlord", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/abyssal_underlord.png"},
    {"category": "heroes", "question": "Какая способность Axe принуждает врагов атаковать его?", "options": ["Berserker's Call", "Counter Helix", "Battle Hunger", "Culling Blade"], "correct": "Berserker's Call", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/axe.png"},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Chronosphere'?", "options": ["Faceless Void", "Weaver", "Enigma", "Void Spirit"], "correct": "Faceless Void", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/faceless_void.png"},
    {"category": "heroes", "question": "Какая основная характеристика у героя Invoker после патча 7.33?", "options": ["Универсальный", "Интеллект", "Ловкость", "Сила"], "correct": "Универсальный", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png"},
    {"category": "heroes", "question": "Как называется ультимативная способность героя Enigma?", "options": ["Black Hole", "Midnight Pulse", "Malefice", "Gravity Well"], "correct": "Black Hole", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/enigma.png"},
    {"category": "heroes", "question": "Как называется ультимейт героя Earthshaker?", "options": ["Echo Slam", "Fissure", "Enchant Totem", "Aftershock"], "correct": "Echo Slam", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/earthshaker.png"},
    {"category": "heroes", "question": "Как называется ультимативная способность Tidehunter?", "options": ["Ravage", "Gush", "Anchor Smash", "Kraken Shell"], "correct": "Ravage", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/tidehunter.png"},
    {"category": "heroes", "question": "Какой герой использует способность 'Reverse Polarity' (RP)?", "options": ["Magnus", "Enigma", "Mars", "Sardar"], "correct": "Magnus", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/magnus.png"},
    {"category": "heroes", "question": "Какой ультимейт у героя Juggernaut?", "options": ["Omnislash", "Blade Fury", "Healing Ward", "Swiftslash"], "correct": "Omnislash", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/juggernaut.png"},
    {"category": "heroes", "question": "Какой герой может летать сквозь деревья способностью Firefly?", "options": ["Batrider", "Viper", "Jakiro", "Dragon Knight"], "correct": "Batrider", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/batrider.png"},
    {"category": "heroes", "question": "Какой герой при смерти выпускает снаряды способностью 'Requiem of Souls'?", "options": ["Shadow Fiend", "Doom", "Terrorblade", "Undying"], "correct": "Shadow Fiend", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/nevermore.png"},
    {"category": "heroes", "question": "Как называется пассивная способность Bristleback, снижающая урон со спины?", "options": ["Bristleback", "Quill Spray", "Warpath", "Goo"], "correct": "Bristleback", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/bristleback.png"},
    {"category": "heroes", "question": "Какая способность Sniper увеличивает дальность его атаки?", "options": ["Take Aim", "Headshot", "Shrapnel", "Assassinate"], "correct": "Take Aim", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/sniper.png"},
    {"category": "heroes", "question": "Какой герой спавнит иллюзии с помощью пассивки Juxtapose?", "options": ["Phantom Lancer", "Naga Siren", "Spectre", "Terrorblade"], "correct": "Phantom Lancer", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/phantom_lancer.png"},
    {"category": "heroes", "question": "Какой герой обладает ультимейтом 'Supernova'?", "options": ["Phoenix", "Lina", "Dawnbreaker", "Keeper of the Light"], "correct": "Phoenix", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/phoenix.png"},
    {"category": "heroes", "question": "Какой атрибут является основным для героя Anti-Mage?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Ловкость", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/antimage.png"},
    {"category": "heroes", "question": "Какой герой умеет мгновенно перемещаться к деревьям способностью Tree Dance?", "options": ["Monkey King", "Nature's Prophet", "Treant Protector", "Hoodwink"], "correct": "Monkey King", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/monkey_king.png"},
    {"category": "heroes", "question": "Как называется ультимейт героя Sven?", "options": ["God's Strength", "Storm Hammer", "Great Cleave", "Warcry"], "correct": "God's Strength", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/sven.png"},
    {"category": "heroes", "question": "Какой герой призывает 'Bear' (Медведя) как отдельного юнита?", "options": ["Lone Druid", "Ursa", "Beastmaster", "Lycan"], "correct": "Lone Druid", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/lone_druid.png"},
    {"category": "heroes", "question": "Какая способность Dazzle предотвращает смерть союзника на 5 секунд?", "options": ["Shallow Grave", "Shadow Wave", "Poison Touch", "Bad Juju"], "correct": "Shallow Grave", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/dazzle.png"},
    {"category": "heroes", "question": "Какой герой крадет интеллект у вражеских героев при их смерти неподалеку?", "options": ["Silencer", "Outworld Destroyer", "Pugna", "Invoker"], "correct": "Silencer", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/silencer.png"},
    {"category": "heroes", "question": "Какой герой имеет способность 'Doom', запрещающую магию и предметы?", "options": ["Doom", "Shadow Demon", "Bane", "Grimstroke"], "correct": "Doom", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/doom_bringer.png"},
    {"category": "heroes", "question": "Как называется ультимейт героя Storm Spirit?", "options": ["Ball Lightning", "Static Remnant", "Electric Vortex", "Overload"], "correct": "Ball Lightning", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/storm_spirit.png"},

    # --- КИБЕРСПОРТ И ЛОР (LORE / ESPORTS) ---
    {"category": "lore", "question": "Какая фракция защищает Древнего (Ancient) в Dota 2?", "options": ["Radiant (Силы Света)", "Dire (Силы Тьмы)", "Sentinel (Стражи)", "Scourge (Плеть)"], "correct": "Radiant (Силы Света)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда выиграла The International 2021 (TI10)?", "options": ["Team Spirit", "PSG.LGD", "OG", "Team Liquid"], "correct": "Team Spirit", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда выиграла два TI подряд (TI8 и TI9)?", "options": ["OG", "Na'Vi", "Alliance", "Team Liquid"], "correct": "OG", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут нейтрального босса, из которого выпадает Aegis of the Immortal?", "options": ["Roshan", "Tormentor", "Satanic", "Ancient Blue Dragon"], "correct": "Roshan", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Кто выиграл самый первый The International (TI1) в 2011 году?", "options": ["Natus Vincere (Na'Vi)", "EHOME", "Invictus Gaming", "Alliance"], "correct": "Natus Vincere (Na'Vi)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как называется главный приз турнира The International?", "options": ["Aegis of Champions", "Summoner's Cup", "Divine Rapier Trophy", "Immortal Shield"], "correct": "Aegis of Champions", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какое имя носит брат-близнец герою Anti-Mage в лоре игры?", "options": ["Terrorblade", "Soul Keeper", "Magina", "Invoker"], "correct": "Terrorblade", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/terrorblade.png"},
    {"category": "lore", "question": "Как зовут Богиню Луны, которой поклоняются Mirana и Luna?", "options": ["Selemene", "Verodicia", "Nyx", "Skadi"], "correct": "Selemene", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/mirana.png"},
    {"category": "lore", "question": "Какое существо появляется на карте на 20-й минуте матча и дает эффект Aghanim's Shard?", "options": ["Терзатель (Tormentor)", "Рошан (Roshan)", "Смотритель (Watcher)", "Лотус (Lotus)"], "correct": "Терзатель (Tormentor)", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aghanims_shard.png"},
    {"category": "lore", "question": "Какая команда выиграла The International 2013 на легендарном пятом карте финала?", "options": ["Alliance", "Na'Vi", "Evil Geniuses", "IG"], "correct": "Alliance", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут дракона, в которого превращается Dragon Knight на 3-ем уровне ультимейта?", "options": ["Синий Дракон (Blue/Frost Dragon)", "Красный Дракон", "Зеленый Дракон", "Черный Дракон"], "correct": "Синий Дракон (Blue/Frost Dragon)", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/dragon_knight.png"},
    {"category": "lore", "question": "Какая страна принимала турнир The International 2018 (TI8)?", "options": ["Канада (Ванкувер)", "США (Сиэтл)", "Румыния (Бухарест)", "Китай (Шанхай)"], "correct": "Канада (Ванкувер)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как называется родной мир героя Void Spirit и других Спиритов?", "options": ["Hidden Temple / Elemental Realm", "Abyssal Plane", "Nether Realm", "Narrow Maze"], "correct": "Hidden Temple / Elemental Realm", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/void_spirit.png"},
    {"category": "lore", "question": "Кем по лору является герой Pudge?", "options": ["Мясником на поле битвы тел", "Демоном Ада", "Оживленным зомби", "Падшим рыцарем"], "correct": "Мясником на поле битвы тел", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"},
    {"category": "lore", "question": "Какой игрок известен своим легендарным 'Pudge + Chen' (Fountain Hook) на TI3?", "options": ["Dendi", "Puppey", "Miracle-", "Topson"], "correct": "Dendi", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая фракция противостоит Radiant в Dota 2?", "options": ["Dire (Силы Тьмы)", "Scourge", "Horde", "Legion"], "correct": "Dire (Силы Тьмы)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как называется место, куда попадают души умерших героев перед перерождением (в лоре Razora и Visage)?", "options": ["Narrow Maze (Узкий Лабиринт)", "Nether Realm", "Abyss", "Hell"], "correct": "Narrow Maze (Узкий Лабиринт)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой герой является заклятым врагом Tidehunter?", "options": ["Kunkka", "Slardar", "Morphling", "Naga Siren"], "correct": "Kunkka", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/kunkka.png"},
    {"category": "lore", "question": "Какая финская организация выиграла The International 2017 (TI7)?", "options": ["Team Liquid", "Newbee", "OG", "VP"], "correct": "Team Liquid", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут фундаментала, представляющего собой силу притяжения (Gravity)?", "options": ["Enigma", "Keeper of the Light", "Chaos Knight", "Io"], "correct": "Enigma", "image": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/enigma.png"}
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
        [InlineKeyboardButton(text="🎲 Микс (Всё подряд)", callback_data="cat_all")],
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

@dp.message(F.text.in_({"🎯 Пройти тест", "Играть", "играть"}))
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
            f"🎉 **Тест завершён!**\n\n"
            f"✅ Правильных ответов: **{correct} из {total}**\n\n"
            f"Посмотреть статистику можно в разделе «📊 Моя статистика»."
        )
        
        restart_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data="restart_quiz")]
        ])
        
        # Обязательно высылаем main_menu(), чтобы клавиатура не пропадала в конце
        await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())
        msg = await bot.send_message(chat_id, "Хотите сыграть ещё раз?", reply_markup=restart_kb)
        
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(None)
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]
    q_text = f"**Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"
    image_url = q.get("image") or BACKGROUND_IMAGES["general"]

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
        msg = await message.answer("Профиль не найден. Напишите /start для регистрации.", reply_markup=main_menu())
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
        msg = await message.answer("Профиль не найден. Напишите /start для регистрации.", reply_markup=main_menu())
        await state.update_data(last_msg_id=msg.message_id)
        return

    nick, rank = user_data
    profile_text = (
        f"👤 **Ваш профиль**\n\n"
        f"🏷 **Никнейм:** {nick}\n"
        f"🎖 **Текущий ранг:** {rank}"
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
