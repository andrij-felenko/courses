# -*- coding: utf-8 -*-
"""Діаграми для розділу JSON: текстове подання об'єктів і масивів."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)


def fig_json_grammar_types():
    """Шість базових типів JSON та їхня структурна граматика."""
    w, h = 880, 360
    p = []

    # Заголовок / фон
    p.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Ліва колонка: Прості (атомарні) типи
    p.append(rect(25, 25, 400, 310, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    p.append(text(225, 48, "Атомарні типи (примітиви)", size=13, color=INK, bold=True))

    primitives = [
        ("null", "null", "Позначає відсутність значення (один літерал)"),
        ("boolean", "true | false", "Логічні значення у нижньому регістрі"),
        ("number", "42, -3.14, 1.2e+5", "Десяткові цілі та дійсні з експонентою"),
        ("string", '"рядок\\n"', 'Послідовність Unicode у подвійних лапках ""'),
    ]

    for i, (name, syntax, desc) in enumerate(primitives):
        y_box = 70 + i * 62
        p.append(rect(40, y_box, 370, 52, fill=FILL, stroke=LINE, sw=1.0, rx=4))
        p.append(text(55, y_box + 20, name, size=12, color=NEG, bold=True, anchor="start"))
        p.append(text(125, y_box + 20, syntax, size=11, color=FIELD, bold=True, anchor="start"))
        p.append(text(55, y_box + 40, desc, size=10, color=MUTED, anchor="start"))

    # Права колонка: Складені (контейнерні) типи
    p.append(rect(445, 25, 410, 310, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    p.append(text(650, 48, "Контейнерні типи (рекурсивні)", size=13, color=INK, bold=True))

    # Object
    p.append(rect(460, 70, 380, 115, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    p.append(text(475, 92, "object (словник / відображення)", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(475, 112, '{ "key1": value1, "key2": value2 }', size=11, color=INK, bold=True, anchor="start"))
    p.append(text(475, 132, "• Ключі — завжди тільки рядки у подвійних лапках", size=10, color=MUTED, anchor="start"))
    p.append(text(475, 148, "• Роздільник пари — двокрапка ':', між парами — кома ','", size=10, color=MUTED, anchor="start"))
    p.append(text(475, 164, "• Порядок пар не є значущим за стандартом RFC 8259", size=10, color=MUTED, anchor="start"))

    # Array
    p.append(rect(460, 195, 380, 95, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    p.append(text(475, 217, "array (впорядкований список)", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(475, 237, '[ value1, value2, value3 ]', size=11, color=INK, bold=True, anchor="start"))
    p.append(text(475, 257, "• Елементи будь-яких типів (гетерогенні списки)", size=10, color=MUTED, anchor="start"))
    p.append(text(475, 273, "• Порядок елементів суворо фіксований за індексом 0..N-1", size=10, color=MUTED, anchor="start"))

    # Пробільні символи
    p.append(text(650, 312, "Пробіли між токенами: SP (0x20), TAB (0x09), LF (0x0A), CR (0x0D)", size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "json-grammar-types.svg"), w, h, *p)


def fig_utf16_surrogates():
    """Декодування сурогатних пар UTF-16 у 21-бітний Unicode та UTF-8."""
    w, h = 880, 340
    p = []

    p.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Рядок JSON з ескейпом
    p.append(rect(30, 25, 820, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(50, 50, "Рядок у JSON:", size=12, color=MUTED, anchor="start"))
    p.append(text(155, 50, '"\\uD83D\\uDE00"', size=13, color=POS, bold=True, anchor="start"))
    p.append(text(300, 50, "→ символ емодзі 😀 (код U+1F600, поза межами 16-бітної BMP)", size=11.5, color=INK, anchor="start"))

    # Стрілка вниз
    p.append(arrow(440, 68, 440, 92, color=LINE, sw=1.5))

    # Дві коробки: High Surrogate та Low Surrogate
    # Старший сурогат
    p.append(rect(40, 95, 380, 90, fill=FILL, stroke=NEG, sw=1.3, rx=6))
    p.append(text(60, 118, "Старший сурогат (High): \\uD83D", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(60, 138, "Діапазон: 0xD800 .. 0xDBFF  (110110xx xxxxxxxx)", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 156, "Зсув: 0xD83D − 0xD800 = 0x003D  (біти 10..19)", size=10.5, color=MUTED, anchor="start"))
    p.append(text(60, 172, "10-бітне значення: 0000111101₂", size=10, color=FIELD, bold=True, anchor="start"))

    # Молодший сурогат
    p.append(rect(460, 95, 380, 90, fill=FILL, stroke=NEG, sw=1.3, rx=6))
    p.append(text(480, 118, "Молодший сурогат (Low): \\uDE00", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(480, 138, "Діапазон: 0xDC00 .. 0xDFFF  (110111xx xxxxxxxx)", size=10.5, color=INK, anchor="start"))
    p.append(text(480, 156, "Зсув: 0xDE00 − 0xDC00 = 0x0200  (біти 0..9)", size=10.5, color=MUTED, anchor="start"))
    p.append(text(480, 172, "10-бітне значення: 1000000000₂", size=10, color=FIELD, bold=True, anchor="start"))

    # Стрілки до зведення
    p.append(arrow(230, 186, 380, 218, color=LINE, sw=1.4))
    p.append(arrow(650, 186, 500, 218, color=LINE, sw=1.4))

    # Зведена формула
    p.append(rect(140, 220, 600, 52, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(440, 240, "Формула відновлення кодової точки Unicode:", size=11, color=INK, bold=True))
    p.append(text(440, 258, "CodePoint = 0x10000 + ((High − 0xD800) « 10) + (Low − 0xDC00) = 0x1F600", size=11.5, color=FIELD, bold=True))

    # Стрілка до UTF-8
    p.append(arrow(440, 273, 440, 290, color=LINE, sw=1.4))

    # UTF-8 результат
    p.append(rect(180, 292, 520, 36, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(440, 315, "Фінальне кодування в UTF-8 (4 байти): 0xF0 0x9F 0x98 0x80", size=11.5, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "utf16-surrogates.svg"), w, h, *p)


def fig_ieee754_int53_precision():
    """Межа точності 2^53 у форматі IEEE 754 binary64 та втрата цілих чисел."""
    w, h = 880, 330
    p = []

    p.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Вісь чисел
    p.append(line(50, 130, 830, 130, color=LINE, sw=2.0))
    p.append(arrow(820, 130, 840, 130, color=LINE, sw=2.0))

    # Позначки на осі
    # Ліва зона: крок 1 (безпечна зона)
    p.append(rect(50, 35, 410, 60, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(255, 58, "Точне подання цілих чисел (крок сітки = 1)", size=11.5, color=FIELD, bold=True))
    p.append(text(255, 78, "Мантиса 53 біти вміщує всі цілі від 0 до 2⁵³ − 1 без втрат", size=10, color=INK))

    # Права зона: крок 2 і більше (зона втрати точності)
    p.append(rect(500, 35, 330, 60, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    p.append(text(665, 58, "Втрата непарних чисел (крок сітки = 2)", size=11.5, color=POS, bold=True))
    p.append(text(665, 78, "Числа > 2⁵³ округлюються до найближчих парних", size=10, color=INK))

    # Роздільник 2^53
    p.append(line(480, 105, 480, 155, color=POS, sw=2.5))
    p.append(text(480, 172, "2⁵³ = 9 007 199 254 740 992", size=11, color=POS, bold=True))
    p.append(text(480, 188, "Number.MAX_SAFE_INTEGER = 2⁵³ − 1", size=10, color=MUTED))

    # Точки на осі зліва
    pts_left = [
        (130, "9 007 199 254 740 990", "точно"),
        (300, "9 007 199 254 740 991", "точно"),
    ]
    for x, val, note in pts_left:
        p.append(circle(x, 130, 4.5, fill=FIELD, stroke=FIELD, sw=1.5))
        p.append(line(x, 125, x, 135, color=FIELD, sw=1.5))
        p.append(text(x, 115, val, size=9.5, color=INK))
        p.append(text(x, 148, note, size=9, color=FIELD, bold=True))

    # Точки на осі справа
    # 2^53 + 1 (втрачено)
    x_lost = 600
    p.append(circle(x_lost, 130, 4.5, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(x_lost, 115, "9 007 199 254 740 993", size=9.5, color=POS, bold=True))
    p.append(text(x_lost, 148, "НЕ існує в double", size=9, color=POS, bold=True))
    # Стрілка округлення назад до парного
    p.append(arrow(x_lost - 15, 122, 495, 122, color=POS, sw=1.5))

    # 2^53 + 2 (існує)
    x_even = 740
    p.append(circle(x_even, 130, 4.5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(text(x_even, 115, "9 007 199 254 740 994", size=9.5, color=INK))
    p.append(text(x_even, 148, "парне (точно)", size=9, color=FIELD))

    # Нижнє попередження для практики
    p.append(rect(40, 215, 800, 90, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=6))
    p.append(text(60, 238, "Практичний наслідок для розподілених систем:", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(60, 258, "• 64-бітні ідентифікатори баз даних (uint64_t / Snowflake ID) у JSON-полі number втрачають молодші біти в JS!", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 276, "• Приклад: ID 9007199254740993 парситься як 9007199254740992 → колізія і підміна чужого запису в базі.", size=10.5, color=MUTED, anchor="start"))
    p.append(text(60, 294, "• Правильне рішення: серіалізувати 64-бітні ID та точні грошові суми як рядки string: \"9007199254740993\".", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG_DIR, "ieee754-int53-precision.svg"), w, h, *p)


def fig_simd_structural_indexing():
    """Двоетапний конвеєр векторизованого парсингу JSON (simdjson)."""
    w, h = 880, 360
    p = []

    p.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))

    # Етап 1: Векторна класифікація (Stage 1)
    p.append(rect(30, 25, 400, 310, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    p.append(text(230, 48, "Етап 1: Структурна індексація (SIMD)", size=12.5, color=INK, bold=True))

    steps_stage1 = [
        ("1. Завантаження блоку 64 байти", "Регістри AVX-512 / 2×AVX2 (64 символи за раз)"),
        ("2. Паралельна класифікація", "Векторне порівняння: лапки '\"', слеші '\\', '{', '}', '[', ']', ':', ','"),
        ("3. Відстеження лапок (CLMUL)", "Префіксний XOR для маски лапок: знаходження меж рядків"),
        ("4. Фільтрація структури", "structural_mask = candidate_mask & ~in_string"),
        ("5. Запис індексів токенів (tzcnt)", "Видобування бітів без умовних переходів у буфер зміщень"),
    ]

    for i, (title, desc) in enumerate(steps_stage1):
        y_box = 68 + i * 50
        p.append(rect(45, y_box, 370, 44, fill=FILL, stroke=LINE, sw=1.0, rx=4))
        p.append(text(60, y_box + 18, title, size=11, color=NEG, bold=True, anchor="start"))
        p.append(text(60, y_box + 34, desc, size=9.5, color=MUTED, anchor="start"))

    # Стрілка між етапами
    p.append(arrow(435, 180, 465, 180, color=LINE, sw=2.0))
    p.append(text(450, 170, "Tape", size=10, color=FIELD, bold=True))

    # Етап 2: Генерація лінійного масиву (Stage 2)
    p.append(rect(470, 25, 380, 310, fill="#ffffff", stroke="#c8d1dc", sw=1.2, rx=6))
    p.append(text(660, 48, "Етап 2: Синтаксичний обхід за індексами", size=12.5, color=INK, bold=True))

    p.append(rect(485, 68, 350, 120, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    p.append(text(500, 90, "Парсинг без перегляду проміжних байтів:", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(500, 110, "• Парсер перестрибує від індексу до індексу", size=10, color=INK, anchor="start"))
    p.append(text(500, 128, "• Пропускає пробіли та символи всередині рядків", size=10, color=MUTED, anchor="start"))
    p.append(text(500, 146, "• Нуль branch mispredictions на скануванні", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(500, 164, "• Швидкість: 2.5 – 5.0 ГБ/с на одне ядро CPU", size=10, color=NEG, bold=True, anchor="start"))

    # Структура Tape (лінійний масив вузлів)
    p.append(rect(485, 200, 350, 120, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(500, 222, "Компактне дерево Tape (64-бітні дескриптори):", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(500, 244, "[0] ROOT: OBJECT (перехід на кінець: індекс 12)", size=9.5, color=INK, anchor="start"))
    p.append(text(500, 262, "[1] STRING: \"user_id\"  →  [2] UINT64: 1048576", size=9.5, color=MUTED, anchor="start"))
    p.append(text(500, 280, "[3] STRING: \"roles\"    →  [4] ARRAY (довжина 3)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(500, 298, "Дерево лежить у суцільному буфері без malloc/free на кожен вузол", size=9, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "simd-structural-indexing.svg"), w, h, *p)


if __name__ == "__main__":
    fig_json_grammar_types()
    fig_utf16_surrogates()
    fig_ieee754_int53_precision()
    fig_simd_structural_indexing()
    print("All figures generated successfully.")
