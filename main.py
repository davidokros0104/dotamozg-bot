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

# Надёжные прямодоступные изображения для категории
BACKGROUND_IMAGES = {
    "items": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800",
    "heroes": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800",
    "lore": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800",
    "general": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800"
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

# База знаний (100+ вопросов)
QUESTIONS_BASE = [
    # ==================== ПРЕДМЕТЫ (ITEMS) ====================
    {"category": "items", "question": "Какой предмет даёт полный иммунитет к магии на время действия?", "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Pipe of Insight"], "correct": "Black King Bar", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет собирается из Blink Dagger и Reaver?", "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Wind Waker"], "correct": "Overwhelming Blink", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько стоит рецепт для сборки Hand of Midas?", "options": ["1750", "1500", "1400", "2200"], "correct": "1750", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какое максимальное число зарядов может хранить Magic Wand?", "options": ["20", "15", "10", "25"], "correct": "20", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет даёт эффект 'True Sight' вокруг владельца?", "options": ["Gem of True Sight", "Dust of Appearance", "Sentry Ward", "Shadow Blade"], "correct": "Gem of True Sight", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет выпадает при уничтожении Торментора (Tormentor)?", "options": ["Aghanim's Shard", "Aegis of the Immortal", "Cheese", "Refresher Shard"], "correct": "Aghanim's Shard", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет дает наибольший бонус к интеллекту?", "options": ["Scythe of Vyse", "Octarine Core", "Shiva's Guard", "Kaya and Sange"], "correct": "Scythe of Vyse", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой из этих предметов собирается из Demon Edge и Sacred Relic?", "options": ["Divine Rapier", "Daedalus", "Abyssal Blade", "Monkey King Bar"], "correct": "Divine Rapier", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько секунд длится перезарядка Blink Dagger после получения урона от игрока?", "options": ["3 сек", "2 сек", "4 сек", "5 сек"], "correct": "3 сек", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет снижает перезарядку всех способностей и предметов на 25%?", "options": ["Octarine Core", "Refresher Orb", "Arcane Blink", "Kaya"], "correct": "Octarine Core", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет превращает вражеского юнита в безобидное существо (Hex)?", "options": ["Scythe of Vyse", "Eul's Scepter of Divinity", "Orchid Malevolence", "Nullifier"], "correct": "Scythe of Vyse", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько стоит Sentry Ward в вардинг лавке?", "options": ["50", "75", "100", "0"], "correct": "50", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какова базовая стоимость Town Portal Scroll?", "options": ["100", "90", "75", "50"], "correct": "100", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой артефакт дает вампиризм от заклинаний?", "options": ["Bloodstone", "Satanic", "Mask of Madness", "Vladmir's Offering"], "correct": "Bloodstone", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой нейтральный предмет 5 тира увеличивает дальность атаки ближнего боя?", "options": ["Giant's Ring", "Apex", "Book of Shadows", "Stygian Desolator"], "correct": "Giant's Ring", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет даёт активную способность 'Echo Sweep'?", "options": ["Echo Sabre", "Maelstrom", "Battle Fury", "Meteor Hammer"], "correct": "Echo Sabre", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько здоровья восстанавливает Cheese при использовании?", "options": ["2500", "1500", "2000", "3000"], "correct": "2500", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой из этих предметов ТРЕБУЕТ покупки рецепта?", "options": ["Manta Style", "Heart of Tarrasque", "Sange and Yasha", "Butterfly"], "correct": "Manta Style", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой эффект накладывает предмет Spirit Vessel на врага?", "options": ["Снижает лечение и наносит урон", "Оглушает", "Безмолвие (Silence)", "Замедляет атаки"], "correct": "Снижает лечение и наносит урон", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой из этих предметов НЕ продаётся в Потайной лавке (Secret Shop)?", "options": ["Claymore", "Demon Edge", "Reaver", "Sacred Relic"], "correct": "Claymore", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет временно снимает положительные эффекты (развеивание) с врага при атаке или активации?", "options": ["Nullifier", "Orchid Malevolence", "Rod of Atos", "Diffusal Blade"], "correct": "Nullifier", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько даёт брони Ring of Protection?", "options": ["2", "3", "1", "4"], "correct": "2", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какова длительность действия Smoke of Deceit?", "options": ["45 сек", "30 сек", "60 сек", "40 сек"], "correct": "45 сек", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет собирается из Shadow Blade и Ultimate Orb?", "options": ["Silver Edge", "Manta Style", "Linken's Sphere", "Bloodthorn"], "correct": "Silver Edge", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет даёт пассивный прорубающий урон (Cleave) для героев ближнего боя?", "options": ["Battle Fury", "Maelstrom", "Radiance", "Desolator"], "correct": "Battle Fury", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Что делает предмет Hurricane Pike при применении на врага?", "options": ["Толкает вас и врага друг от друга", "Притягивает врага", "Оглушает врага на 2 сек", "Накладывает безмолвие"], "correct": "Толкает вас и врага друг от друга", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет даёт ауру снижения брони окружающим зданиям и врагам?", "options": ["Assault Cuirass", "Desolator", "Solar Crest", "Shiva's Guard"], "correct": "Assault Cuirass", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какое максимальное число Observer Ward может одновременно находиться в лавке?", "options": ["4", "3", "2", "6"], "correct": "4", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет собирается из Helm of the Dominator и Ultimate Orb?", "options": ["Helm of the Overlord", "Satanic", "Vladmir's Offering", "Nullifier"], "correct": "Helm of the Overlord", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой артефакт при активации создаёт ураган и поднимает владельца или врага в воздух?", "options": ["Eul's Scepter of Divinity", "Wind Waker", "Force Staff", "Scythe of Vyse"], "correct": "Eul's Scepter of Divinity", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько секунд составляет время перезарядки Refresher Orb?", "options": ["180 сек", "160 сек", "200 сек", "120 сек"], "correct": "180 сек", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой нейтральный предмет 1-го тира даёт бонус к восстановлению маны?", "options": ["Arcane Ring", "Safety Bubble", "Spark of Courage", "Royal Jelly"], "correct": "Arcane Ring", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Какой предмет позволяет проходить сквозь деревья и ландшафт при активации?", "options": ["Phase Boots", "Force Staff", "Shadow Blade", "Wind Waker"], "correct": "Phase Boots", "image": BACKGROUND_IMAGES["items"]},
    {"category": "items", "question": "Сколько снижает броню предмет Desolator при атаке?", "options": ["6", "7", "5", "8"], "correct": "6", "image": BACKGROUND_IMAGES["items"]},

    # ==================== ГЕРОИ И МЕХАНИКИ (HEROES) ====================
    {"category": "heroes", "question": "Какой атрибут является основным для героя Pudge?", "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"], "correct": "Сила", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Сколько сфер у Invoker одновременно вращается вокруг него?", "options": ["3", "2", "4", "5"], "correct": "3", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Как называется ультимейт героя Rubick?", "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"], "correct": "Spell Steal", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?", "options": ["Meepo", "Phantom Lancer", "Naga Siren", "Chaos Knight"], "correct": "Meepo", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой произносит знаменитую фразу 'Fresh meat!'?", "options": ["Pudge", "Lifestealer", "Doom", "Night Stalker"], "correct": "Pudge", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой имеет наибольшую базовую дальность атаки в игре?", "options": ["Techies", "Sniper", "Lina", "Clinkz"], "correct": "Techies", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какое максимальное количество душ может набрать Shadow Fiend без Aghanim's Scepter?", "options": ["20", "15", "25", "30"], "correct": "20", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой имеет способность 'Global Silence'?", "options": ["Silencer", "Disruptor", "Dark Seer", "Oracle"], "correct": "Silencer", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какова базовая скорость передвижения героя Enchantress?", "options": ["320", "335", "310", "300"], "correct": "320", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой может воскрешать себя способностью Reincarnation?", "options": ["Wraith King", "Dazzle", "Oracle", "Abaddon"], "correct": "Wraith King", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Каким типом урона обладает способность Laguna Blade героя Lina без Aghanim's Scepter?", "options": ["Магический", "Чистый", "Физический", "Смешанный"], "correct": "Магический", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой может перемещаться в любую точку карты к союзному юниту ультимейтом?", "options": ["Underlord", "Nature's Prophet", "Io", "Spectre"], "correct": "Underlord", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "У какого героя базовая броня равна -1?", "options": ["Visage", "Doom", "Phoenix", "Tiny"], "correct": "Visage", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какая способность Axe принуждает врагов атаковать его?", "options": ["Berserker's Call", "Counter Helix", "Battle Hunger", "Culling Blade"], "correct": "Berserker's Call", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Сколько максимум иллюзий создает способность Phantasm героя Chaos Knight?", "options": ["3", "4", "2", "5"], "correct": "3", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой может воровать интеллект при убийстве врагов?", "options": ["Silencer", "Outworld Destroyer", "Pugna", "Invoker"], "correct": "Silencer", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Chronosphere'?", "options": ["Faceless Void", "Weaver", "Enigma", "Void Spirit"], "correct": "Faceless Void", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какая основная характеристика у героя Invoker после патча 7.33?", "options": ["Универсальный", "Интеллект", "Ловкость", "Сила"], "correct": "Универсальный", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой наносит урон ультимейтом в зависимости от недостающего здоровья врага?", "options": ["Necrophos", "Ancient Apparition", "Lion", "Zeus"], "correct": "Necrophos", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Как называется ультимативная способность героя Enigma?", "options": ["Black Hole", "Midnight Pulse", "Malefice", "Gravity Well"], "correct": "Black Hole", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой НЕ имеет активных способностей до 6-го уровня по умолчанию?", "options": ["Wraith King", "Spectre", "Phantom Assassin", "Никакой"], "correct": "Никакой", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой использует способность 'Static Storm'?", "options": ["Disruptor", "Razor", "Zeus", "Storm Spirit"], "correct": "Disruptor", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Как называется ультимейт героя Earthshaker?", "options": ["Echo Slam", "Fissure", "Enchant Totem", "Aftershock"], "correct": "Echo Slam", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какая способность Morphling позволяет ему менять атрибуты силы и ловкости?", "options": ["Attribute Shift", "Waveform", "Adaptive Strike", "Morph"], "correct": "Attribute Shift", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой при смерти оставляет после себя мины и взрывается?", "options": ["Techies", "Pugna", "Clockwerk", "Gyrocopter"], "correct": "Techies", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Как называется способность Storm Spirit, позволяющая ему летать по карте?", "options": ["Ball Lightning", "Static Remnant", "Electric Vortex", "Overload"], "correct": "Ball Lightning", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой персонаж превращает врагов в камень ультимейтом Stone Gaze?", "options": ["Medusa", "Gorgon", "Naga Siren", "Tidehunter"], "correct": "Medusa", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой крадёт урон от атаки врага способностью Static Link?", "options": ["Razor", "Vengeful Spirit", "Bane", "Viper"], "correct": "Razor", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой персонаж способен полностью блокировать урон благодаря Refraction?", "options": ["Templar Assassin", "Phantom Assassin", "Spectre", "Templar"], "correct": "Templar Assassin", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Как называется ультимативная способность Tidehunter?", "options": ["Ravage", "Gush", "Anchor Smash", "Kraken Shell"], "correct": "Ravage", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой получает бонус к броне и здоровью за каждого убитого врага (Flesh Heap)?", "options": ["Pudge", "Axe", "Bristleback", "Centaur Warrunner"], "correct": "Pudge", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какая способность героя Tinker позволяет сбрасывать перезарядку предметов?", "options": ["Rearm", "Heat-Seeking Missile", "Laser", "Defense Matrix"], "correct": "Rearm", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какого типа урон наносит способность Sun Strike героя Invoker?", "options": ["Чистый", "Магический", "Физический", "Смешанный"], "correct": "Чистый", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой может превращать деревья в своих подконтрольных юнитов?", "options": ["Nature's Prophet", "Treant Protector", "Timbersaw", "Beastmaster"], "correct": "Nature's Prophet", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Supernova'?", "options": ["Phoenix", "Dawnbreaker", "Keeper of the Light", "Lina"], "correct": "Phoenix", "image": BACKGROUND_IMAGES["heroes"]},
    {"category": "heroes", "question": "У какого героя есть способность 'Shallow Grave', спасающая от смерти?", "options": ["Dazzle", "Oracle", "Abaddon", "Shadow Priest"], "correct": "Dazzle", "image": BACKGROUND_IMAGES["heroes"]},

    # ==================== КИБЕРСПОРТ И ЛОР (LORE / ESPORTS) ====================
    {"category": "lore", "question": "Какая команда выиграла The International 2021 (TI10)?", "options": ["Team Spirit", "PSG.LGD", "OG", "Team Liquid"], "correct": "Team Spirit", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда выиграла два TI подряд (TI8 и TI9)?", "options": ["OG", "Na'Vi", "Alliance", "Team Liquid"], "correct": "OG", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут нейтрального босса, из которого выпадает Aegis of the Immortal?", "options": ["Roshan", "Tormentor", "Satanic", "Ancient Blue Dragon"], "correct": "Roshan", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Кто выиграл самый первый The International (TI1) в 2011 году?", "options": ["Natus Vincere (Na'Vi)", "EHOME", "Invictus Gaming", "Alliance"], "correct": "Natus Vincere (Na'Vi)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "В каком городе проходил первый турнир The International (TI1)?", "options": ["Кёльн", "Сиэтл", "Ванкувер", "Шанхай"], "correct": "Кёльн", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой игрок известен своим легендарным моментом 'The Million Dollar Dream Coil' на TI3?", "options": ["S4", "Dendi", "Puppey", "Loda"], "correct": "S4", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда выиграла The International 2023 (TI12)?", "options": ["Team Spirit", "Gaimin Gladiators", "LGD Gaming", "Liquid"], "correct": "Team Spirit", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Кто из этих игроков принимал участие во всех турнирах The International до TI11?", "options": ["Puppey", "KuroKy", "Notail", "Dendi"], "correct": "Puppey", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой игрок играл на Pudge в знаменитой связке 'Fountain Hook' на TI3?", "options": ["Dendi", "Puppey", "XBOCT", "Funn1k"], "correct": "Dendi", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как называется главный приз турнира The International?", "options": ["Aegis of Champions", "Summoner's Cup", "Divine Rapier Trophy", "Immortal Shield"], "correct": "Aegis of Champions", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой игрок стал самым молодым победителем The International в истории (TI5)?", "options": ["SumaiL", "Topson", "Yatoro", "Miracle-"], "correct": "SumaiL", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какое имя носит брат-близнец герою Anti-Mage в лоре игры?", "options": ["Terrorblade", "Soul Keeper", "Magina", "Invoker"], "correct": "Terrorblade", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда стала победителем The International 2017 (TI7)?", "options": ["Team Liquid", "Newbee", "LFY", "VP"], "correct": "Team Liquid", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут Богиню Луны, которой поклоняются Mirana и Luna?", "options": ["Selemene", "Verodicia", "Nyx", "Skadi"], "correct": "Selemene", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой персонаж по лору является древним драконом, принявшим человеческий облик?", "options": ["Davion (Dragon Knight)", "Jakiro", "Viper", "Winter Wyvern"], "correct": "Davion (Dragon Knight)", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Назовите имя легендарного игрока, сформировавшего золотой состав Virtus.Pro (2016-2019 гг.)?", "options": ["Solo", "RAMZES666", "No[o]ne", "9pasha"], "correct": "Solo", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая фракция защищает древо Силы (World Tree)?", "options": ["Radiant", "Dire", "Sentinel", "Scourge"], "correct": "Radiant", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда одержала победу на TI4 со знаменитой стратегией 'Fast Push'?", "options": ["Newbee", "Vici Gaming", "DK", "EG"], "correct": "Newbee", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как зовут древнего титана, сотворившего мир Dota 2?", "options": ["Elder Titan", "Earthshaker", "Tiny", "Void Spirit"], "correct": "Elder Titan", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Сколько игроков входит в официальный состав команды по Dota 2 на карте?", "options": ["5", "6", "4", "3"], "correct": "5", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая организация выиграла The International 2016 (TI6)?", "options": ["Wings Gaming", "Digital Chaos", "Evil Geniuses", "FNATIC"], "correct": "Wings Gaming", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Кем по лору является Kunkka?", "options": ["Адмиралом флота", "Пиратом", "Духом океана", "Наёмником"], "correct": "Адмиралом флота", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "В каком году официально вышло глобальное обновление 7.00?", "options": ["2016", "2015", "2017", "2018"], "correct": "2016", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какое имя носит ткач времени и нитей судьбы?", "options": ["Weaver", "Faceless Void", "Oracle", "Clockwerk"], "correct": "Weaver", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какая команда проиграла в финале TI10 со счетом 2:3 против Team Spirit?", "options": ["PSG.LGD", "Secret", "OG", "VG"], "correct": "PSG.LGD", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как по лору зовут героя Shadow Fiend?", "options": ["Nevermore", "Shadow Demon", "Doom", "Lucifer"], "correct": "Nevermore", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "К какому виду принадлежит герой Jakiro?", "options": ["Двуглавый Дракон", "Виверна", "Феникс", "Гидра"], "correct": "Двуглавый Дракон", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какой из этих героев НЕ является демоном по лору?", "options": ["Sven", "Doom", "Shadow Demon", "Terrorblade"], "correct": "Sven", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Как называется анимационный сериал по мотивам Dota 2 от Netflix?", "options": ["Dota: Dragon's Blood", "Dota: Arcane", "Dota: Heroes United", "Dota: Book of Selemene"], "correct": "Dota: Dragon's Blood", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какое оригинальное имя героя Sniper?", "options": ["Kardel Sharpeye", "Sniper Rifle", "Dwarven Sniper", "Snippy"], "correct": "Kardel Sharpeye", "image": BACKGROUND_IMAGES["lore"]},
    {"category": "lore", "question": "Какое оружие использует герой Sven?", "options": ["Двуручный меч", "Молот", "Топор", "Копьё"], "correct": "Двуручный меч", "image": BACKGROUND_IMAGES["lore"]}
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
    await message.answer("🔄 Профиль очищен! Отправьте /start для регистрации.")

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

@dp.message(F.text == "🎯 Пройти тест")
async def ask_category(message: types.Message, state: FSMContext):
    await safe_delete_message(message.chat.id, message.message_id)
    data = await state.get_data()
    if "last_msg_id" in data:
        await safe_delete_message(message.chat.id, data["last_msg_id"])

    msg = await message.answer("Выбери режим тестирования:", reply_markup=category_keyboard())
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
        msg = await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(None)
        return

    q = questions[index]
    options = q["options"][:]
    random.shuffle(options)

    kb = [[InlineKeyboardButton(text=opt, callback_data=f"ans_{opt}")] for opt in options]
    q_text = f"**Вопрос {index + 1} из {len(questions)}**\n\n{q['question']}"

    try:
        msg = await bot.send_photo(chat_id, photo=q["image"], caption=q_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except Exception as e:
        # Резервный вариант, если Telegram не смог обработать картинку
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
        msg = await message.answer("Профиль не найден. Напишите /start для регистрации.")
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

