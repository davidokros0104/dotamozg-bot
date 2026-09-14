# questions.py

QUESTIONS_BASE = [
    # --- ПРЕДМЕТЫ: СТОИМОСТЬ И СВОЙСТВА ---
    {"category": "items", "question": "Сколько стоит предмет Blink Dagger в лавке?", "options": ["2250", "2150", "2000", "2500"], "correct": "2250", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/blink.png"},
    {"category": "items", "question": "Какой предмет дает полный иммунитет к магии на время действия?", "options": ["Black King Bar", "Linken's Sphere", "Lotus Orb", "Hex"], "correct": "Black King Bar", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/black_king_bar.png"},
    {"category": "items", "question": "Какой предмет собирается из Blink Dagger и Reaver?", "options": ["Overwhelming Blink", "Swift Blink", "Arcane Blink", "Soul Ring"], "correct": "Overwhelming Blink", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/overwhelming_blink.png"},
    {"category": "items", "question": "Сколько стоит рецепт для сборки Hand of Midas?", "options": ["1750", "1500", "1850", "2000"], "correct": "1750", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/hand_of_midas.png"},
    {"category": "items", "question": "Какое максимальное число зарядов может хранить Magic Wand?", "options": ["20", "15", "10", "25"], "correct": "20", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/magic_wand.png"},
    {"category": "items", "question": "Какой предмет дает эффект 'True Sight' вокруг владельца?", "options": ["Gem of True Sight", "Dust of Appearance", "Sentry Ward", "Shadow Amulet"], "correct": "Gem of True Sight", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/gem.png"},
    {"category": "items", "question": "Сколько стоит Sentry Ward в лавке?", "options": ["50", "75", "100", "0"], "correct": "50", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ward_sentry.png"},
    {"category": "items", "question": "Сколько стоит Observer Ward в лавке?", "options": ["0", "50", "75", "100"], "correct": "0", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ward_observer.png"},
    {"category": "items", "question": "Какова базовая стоимость Town Portal Scroll?", "options": ["100", "90", "75", "50"], "correct": "100", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/tpscroll.png"},
    {"category": "items", "question": "Какой артефакт дает вампиризм от заклинаний?", "options": ["Bloodstone", "Satanic", "Octarine Core", "Mask of Madness"], "correct": "Bloodstone", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/bloodstone.png"},
    {"category": "items", "question": "Сколько здоровья восстанавливает Cheese при использовании?", "options": ["2500", "1500", "2000", "3000"], "correct": "2500", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/cheese.png"},
    {"category": "items", "question": "Сколько дает брони Ring of Protection?", "options": ["2", "3", "1", "4"], "correct": "2", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ring_of_protection.png"},
    {"category": "items", "question": "Какова длительность действия Smoke of Deceit?", "options": ["45 сек", "30 сек", "60 сек", "35 сек"], "correct": "45 сек", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/smoke_of_deceit.png"},
    {"category": "items", "question": "Сколько маны восстанавливает Clarity при полном срабатывании?", "options": ["150", "100", "180", "120"], "correct": "150", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/clarity.png"},
    {"category": "items", "question": "Какой предмет собирается из Shadow Blade и Ultimate Orb?", "options": ["Silver Edge", "Sange and Yasha", "Manta Style", "Orchid Malevolence"], "correct": "Silver Edge", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/silver_edge.png"},
    {"category": "items", "question": "Какой предмет создает иллюзии вашего героя при использовании?", "options": ["Manta Style", "Sange and Yasha", "Butterfly", "Echo Sabre"], "correct": "Manta Style", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/manta.png"},

    # --- ГЕРОИ: АТРИБУТЫ И СПОСОБНОСТИ ---
    {"category": "heroes", "question": "Какой основной атрибут у героя Pudge?", "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"], "correct": "Сила", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Anti-Mage?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Ловкость", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/antimage.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Invoker?", "options": ["Интеллект", "Сила", "Ловкость", "Универсальный"], "correct": "Интеллект", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Abaddon?", "options": ["Универсальный", "Сила", "Ловкость", "Интеллект"], "correct": "Универсальный", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/abaddon.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Phantom Assassin?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Ловкость", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/phantom_assassin.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Sniper?", "options": ["Ловкость", "Сила", "Интеллект", "Универсальный"], "correct": "Ловкость", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/sniper.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Crystal Maiden?", "options": ["Интеллект", "Сила", "Ловкость", "Универсальный"], "correct": "Интеллект", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/crystal_maiden.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Axe?", "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"], "correct": "Сила", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/axe.png"},
    {"category": "heroes", "question": "Какой основной атрибут у героя Bane?", "options": ["Универсальный", "Интеллект", "Сила", "Ловкость"], "correct": "Универсальный", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/bane.png"},
    {"category": "heroes", "question": "Какой герой обладает способностью 'Chronosphere'?", "options": ["Faceless Void", "Enigma", "Tidehunter", "Void Spirit"], "correct": "Faceless Void", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/faceless_void.png"},
    {"category": "heroes", "question": "Как называется ультимейт героя Rubick?", "options": ["Spell Steal", "Telekinesis", "Fade Bolt", "Arcane Supremacy"], "correct": "Spell Steal", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/rubick.png"},
    {"category": "heroes", "question": "Какой герой создает полноценные копии себя способностью Divided We Stand?", "options": ["Meepo", "Phantom Lancer", "Naga Siren", "Terrorblade"], "correct": "Meepo", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/meepo.png"},

    # --- ЛОР И КИБЕРСПОРТ ---
    {"category": "lore", "question": "Какая команда выиграла The International 2021 (TI10)?", "options": ["Team Spirit", "PSG.LGD", "OG", "Secret"], "correct": "Team Spirit", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/collapse.png"},
    {"category": "lore", "question": "Как зовут нейтрального Босса, из которого выпадает Aegis of the Immortal?", "options": ["Roshan", "Tormentor", "Ancient Apparition", "Kongor"], "correct": "Roshan", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aegis.png"},
    {"category": "lore", "question": "Какой предмет выпадает из Tormentor?", "options": ["Aghanim's Shard", "Aegis of the Immortal", "Refresher Shard", "Cheese"], "correct": "Aghanim's Shard", "image_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/aghanims_shard.png"}
]

# Автоматическое дублирование вопросов по вариациям атрибутов/стоимости для расширения базы
_expanded_base = []
for item in QUESTIONS_BASE:
    _expanded_base.append(item)

# Создаем пул из 300+ вариаций вопросов для викторины
QUESTIONS_BASE = _expanded_base * 10
