# -*- coding: utf-8 -*-
"""Діаграми для розділу JSON Schema."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_json_schema_pipeline():
    """Конвеєр валідації: розбір схеми, побудова AST, резолюція посилань та обхід документа."""
    w, h = 940, 350
    frags = []

    # Головний контейнер
    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Стадія 1: Вхідні дані
    frags.append(rect(30, 45, 180, 275, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(120, 72, "1. Вхідні дані", size=13, color=INK, bold=True))
    frags.append(fitbox(45, 95, 150, 95, "JSON Schema\n{\"$schema\": ...,\n \"type\": \"object\",\n \"properties\": ...}", size=11, color=NEG, bold=True))
    frags.append(fitbox(45, 205, 150, 95, "JSON Payload\n(Екземпляр даних)\n{\"id\": 1024,\n \"email\": \"user@...\"}", size=11, color=FIELD, bold=True))

    # Стрілки
    frags.append(arrow(210, 142, 245, 142, color=LINE, sw=1.8))
    frags.append(arrow(210, 252, 490, 252, color=LINE, sw=1.8))

    # Стадія 2: Синтез AST та Резолюція
    frags.append(rect(250, 45, 215, 195, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(357, 72, "2. Компіляція схеми", size=13, color=INK, bold=True))
    frags.append(fitbox(265, 90, 185, 40, "Лексичний аналіз\nі побудова Schema AST", size=11, color=INK))
    frags.append(arrow(357, 130, 357, 145, color=LINE, sw=1.4))
    frags.append(fitbox(265, 145, 185, 42, "Нормалізація URI ($id)\nта резолюція $defs / $ref", size=10, color=NEG))
    frags.append(arrow(357, 187, 357, 200, color=LINE, sw=1.4))
    frags.append(fitbox(265, 200, 185, 28, "Перевірка відсутності циклів", size=10, color=MUTED))

    # Стрілка від компілятора до рушія
    frags.append(arrow(465, 142, 495, 142, color=LINE, sw=1.8))

    # Стадія 3: Рушій виконання
    frags.append(rect(500, 45, 215, 275, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(607, 72, "3. Рушій валідації", size=13, color=INK, bold=True))
    frags.append(fitbox(515, 90, 185, 46, "Предикати типів\n(числа, рядки, межі,\nрегулярні вирази)", size=10, color=INK))
    frags.append(arrow(607, 136, 607, 148, color=LINE, sw=1.4))
    frags.append(fitbox(515, 148, 185, 46, "Логічні аплікатори\n(allOf, anyOf, oneOf,\nif / then / else, not)", size=10, color=NEG))
    frags.append(arrow(607, 194, 607, 206, color=LINE, sw=1.4))
    frags.append(fitbox(515, 206, 185, 48, "Збір анотацій\n(unevaluatedProperties,\nunevaluatedItems)", size=10, color=FIELD))
    frags.append(arrow(607, 254, 607, 268, color=LINE, sw=1.4))
    frags.append(fitbox(515, 268, 185, 42, "Зіставлення з деревом\nвхідного документа", size=10, color=INK, bold=True))

    # Стрілка до стадії 4
    frags.append(arrow(715, 182, 745, 182, color=LINE, sw=1.8))

    # Стадія 4: Результат валідації
    frags.append(rect(750, 45, 160, 275, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(830, 72, "4. Результат", size=13, color=INK, bold=True))
    frags.append(fitbox(760, 95, 140, 52, "Flag Output\n{\"valid\": true / false}", size=10, color=FIELD, bold=True))
    frags.append(fitbox(760, 155, 140, 68, "Basic Output\n[{\"instanceLocation\": ...,\n  \"keywordLocation\": ...,\n  \"error\": ...}]", size=9, color=POS))
    frags.append(fitbox(760, 230, 140, 78, "Detailed Output\nІєрархічне дерево\nвсіх оцінених вузлів\nта вкладених помилок", size=9, color=MUTED))

    render(os.path.join(OUT, "json-schema-pipeline.svg"), w, h, *frags)


def fig_json_pointer_resolution():
    """Резолюція JSON Pointer (RFC 6901) та область видимості базового URI ($id / $defs / $ref)."""
    w, h = 940, 360
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Лівий блок: Коренева схема
    frags.append(rect(30, 45, 415, 290, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(237, 72, "Коренева схема ($id: https://api.org/order.json)", size=12, color=INK, bold=True))
    frags.append(fitbox(45, 88, 385, 60, "\"$defs\": {\n  \"Address\": { \"type\": \"object\", \"properties\": { ... } },\n  \"UUID\": { \"type\": \"string\", \"format\": \"uuid\" }\n}", size=10, color=NEG))
    frags.append(fitbox(45, 155, 385, 72, "\"properties\": {\n  \"order_id\": { \"$ref\": \"#/$defs/UUID\" },\n  \"shipping\": { \"$ref\": \"#/$defs/Address\" },\n  \"billing\":  { \"$ref\": \"https://schemas.org/address.json\" }\n}", size=10, color=FIELD))
    frags.append(fitbox(45, 235, 385, 88, "Синтаксис JSON Pointer (RFC 6901):\n• '#' позначає фрагмент URI всередині документа\n• Роздільник '/' переходить на один рівень ключа чи індексу\n• Ескейп: '~1' кодує '/', а '~0' кодує '~'\n• Приклад: \"#/$defs/Address/properties/street\"", size=9, color=INK))

    # Стрілки
    frags.append(arrow(445, 175, 485, 125, color=NEG, sw=1.8))
    frags.append(arrow(445, 205, 485, 255, color=POS, sw=1.8))

    # Правий верхній блок: Локальна резолюція
    frags.append(rect(490, 45, 420, 140, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(700, 72, "Локальна інтра-документна резолюція (#/...)", size=12, color=NEG, bold=True))
    frags.append(fitbox(505, 88, 390, 85, "1. Базовий URI: https://api.org/order.json\n2. Обхід AST дерева за токенами [\"$defs\", \"UUID\"]\n3. Вузол зв'язується в пам'яті за O(1) без мережі\n4. Вказівник кешується у таблиці символів валідатора", size=10, color=INK))

    # Правий нижній блок: Міждокументна резолюція
    frags.append(rect(490, 195, 420, 140, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    frags.append(text(700, 222, "Зовнішня міждокументна резолюція (URI)", size=12, color=POS, bold=True))
    frags.append(fitbox(505, 238, 390, 85, "1. Нормалізація абсолютного URI за RFC 3986\n2. Пошук у локальному реєстрі скомпільованих схем\n3. Якщо схема відсутня: блокування або Schema Loader\n4. Захист від SSRF через заборону неперевірених хостів", size=10, color=INK))

    render(os.path.join(OUT, "json-pointer-resolution.svg"), w, h, *frags)


def fig_unevaluated_properties():
    """Порівняння additionalProperties проти unevaluatedProperties при allOf композиції."""
    w, h = 940, 360
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Ліва колонка: Проблема additionalProperties: false
    frags.append(rect(30, 45, 420, 290, fill="#fff5f5", stroke="#e8a7a1", sw=1.2, rx=6))
    frags.append(text(240, 72, "Пастка additionalProperties: false (Draft-04..07)", size=12, color=POS, bold=True))
    frags.append(fitbox(45, 88, 390, 85, "\"allOf\": [\n  { \"properties\": { \"name\": { \"type\": \"string\" } },\n    \"additionalProperties\": false },\n  { \"properties\": { \"age\": { \"type\": \"integer\" } },\n    \"additionalProperties\": false }\n]", size=10, color=INK))
    frags.append(fitbox(45, 180, 390, 52, "Дані: {\"name\": \"Олена\", \"age\": 28}\n• Гілка 1: поле \"name\" валідне, але \"age\" вважається зайвим!\n• Помилка: additionalProperties: false відкидає \"age\"", size=10, color=POS, bold=True))
    frags.append(fitbox(45, 240, 390, 82, "Причина ізоляції:\nКожна підсхема в allOf обчислюється повністю автономно.\nКлючове слово additionalProperties бачить лише локальні\nвластивості своєї підсхеми і не знає про сусідні гілки.", size=9, color=MUTED))

    # Права колонка: Рішення unevaluatedProperties: false
    frags.append(rect(490, 45, 420, 290, fill="#f2f9f4", stroke="#9cd4ae", sw=1.2, rx=6))
    frags.append(text(700, 72, "Динамічні анотації: unevaluatedProperties (2020-12)", size=12, color=FIELD, bold=True))
    frags.append(fitbox(505, 88, 390, 85, "\"allOf\": [\n  { \"properties\": { \"name\": { \"type\": \"string\" } } },\n  { \"properties\": { \"age\": { \"type\": \"integer\" } } }\n],\n\"unevaluatedProperties\": false", size=10, color=INK))
    frags.append(fitbox(505, 180, 390, 52, "Дані: {\"name\": \"Олена\", \"age\": 28}\n• Гілка 1 анотує \"name\" як перевірене.\n• Гілка 2 анотує \"age\" як перевірене.\n• unevaluatedProperties перевіряє залишок: ∅ → УСПІХ!", size=10, color=FIELD, bold=True))
    frags.append(fitbox(505, 240, 390, 82, "Механізм динамічних анотацій:\nУ Draft 2020-12 збирається список усіх властивостей,\nоцінених будь-якими підсхемами (properties, allOf, if).\nЗалишок перевіряється через unevaluatedProperties.", size=9, color=MUTED))

    render(os.path.join(OUT, "unevaluated-properties.svg"), w, h, *frags)


def fig_schema_ast_composition():
    """Деревоподібна композиція логічних аплікаторів (allOf, anyOf, oneOf, if/then/else)."""
    w, h = 940, 350
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Кореневий вузол
    frags.append(fitbox(370, 35, 200, 48, "Schema AST Root\nObject Assertions", size=12, color=INK, bold=True))

    # Рівень аплікаторів
    frags.append(fitbox(60, 125, 160, 42, "allOf (Кон'юнкція)\n∀ S_i: Valid(S_i) = true", size=11, color=NEG, bold=True))
    frags.append(fitbox(280, 125, 160, 42, "anyOf (Диз'юнкція)\n∃ S_i: Valid(S_i) = true", size=11, color=FIELD, bold=True))
    frags.append(fitbox(500, 125, 160, 42, "oneOf (XOR)\n∑ [Valid(S_i)] == 1", size=11, color=POS, bold=True))
    frags.append(fitbox(720, 125, 160, 42, "if / then / else\nУмовна валідація", size=11, color=MUTED, bold=True))

    # Стрілки від кореня до аплікаторів
    frags.append(arrow(420, 83, 140, 125, color=LINE, sw=1.4))
    frags.append(arrow(450, 83, 360, 125, color=LINE, sw=1.4))
    frags.append(arrow(490, 83, 580, 125, color=LINE, sw=1.4))
    frags.append(arrow(520, 83, 800, 125, color=LINE, sw=1.4))

    # Підлеглі перевірки / поведінка
    frags.append(fitbox(45, 195, 190, 125, "Перетин обмежень:\n• Зупинка на першій\n  помилці (fail-fast)\n• Без повернення назад\n• Складність: O(∑ T(S_i))", size=10, color=INK))
    frags.append(fitbox(265, 195, 190, 125, "Швидкий вихід:\n• Зупинка на першому\n  успіху\n• Помилка якщо всі S_i хибні\n• Складність: O(k · T(S_i))", size=10, color=INK))
    frags.append(fitbox(485, 195, 190, 125, "Вичерпна перевірка:\n• Обов'язковий прохід ВСІХ\n  гілок S_i\n• Немає fail-fast!\n• Ризик вибуху складності", size=10, color=POS))
    frags.append(fitbox(705, 195, 190, 125, "Умовне розгалуження:\n• Обчислення предикату 'if'\n• Якщо 'if' true → перевірка 'then'\n• Якщо 'if' false → перевірка 'else'", size=10, color=INK))

    # Стрілки вниз
    frags.append(arrow(140, 167, 140, 195, color=LINE, sw=1.2))
    frags.append(arrow(360, 167, 360, 195, color=LINE, sw=1.2))
    frags.append(arrow(580, 167, 580, 195, color=LINE, sw=1.2))
    frags.append(arrow(800, 167, 800, 195, color=LINE, sw=1.2))

    render(os.path.join(OUT, "schema-ast-composition.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_json_schema_pipeline()
    fig_json_pointer_resolution()
    fig_unevaluated_properties()
    fig_schema_ast_composition()
    print("Всі 4 діаграми JSON Schema успішно згенеровано.")