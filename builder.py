import json
import requests

# Загружаем официальные данные Valve
heroes = requests.get("https://api.opendota.com/api/heroes").json()
items = requests.get("https://api.opendota.com/api/constants/items").json()

questions = []

# Генерация вопросов по героям (атрибуты)
attr_map = {"str": "Сила", "agi": "Ловкость", "int": "Интеллект", "all": "Универсальный"}

for h in heroes:
    correct_attr = attr_map.get(h.get("primary_attr"), "Сила")
    img_name = h["name"].replace("npc_dota_hero_", "")
    img_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{img_name}.png"

    questions.append({
        "category": "heroes",
        "question": f"Какой основной атрибут у героя {h['localized_name']}?",
        "options": ["Сила", "Ловкость", "Интеллект", "Универсальный"],
        "correct": correct_attr,
        "image_url": img_url
    })

# Генерация вопросов по предметам (стоимость)
for item_key, item_data in items.items():
    if isinstance(item_data, dict) and item_data.get("cost") and item_data.get("dname"):
        cost = str(item_data["cost"])
        options = list(set([
            cost,
            str(item_data["cost"] + 100),
            str(max(50, item_data["cost"] - 150)),
            str(item_data["cost"] + 250)
        ]))
        while len(options) < 4:
            options.append(str(int(options[-1]) + 50))

        img_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/{item_key}.png"

        questions.append({
            "category": "items",
            "question": f"Сколько стоит предмет {item_data['dname']} в лавке?",
            "options": options,
            "correct": cost,
            "image_url": img_url
        })

# Автоматически перезаписываем файл questions.py
with open("questions.py", "w", encoding="utf-8") as f:
    f.write(f"QUESTIONS_BASE = {json.dumps(questions, ensure_ascii=False, indent=4)}")

print(f"Готово! Сгенерировано {len(questions)} вопросов.")

