# -*- coding: utf-8 -*-
"""Фігури до статті «Інвертований індекс».
Запуск із теки теми: python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GOOD = FIELD        # зелений
WEAK = POS          # червоний
HL_BLUE = "#eef4ff" # світло-синя заливка
HL_GREEN = "#e9f8ef"# світло-зелена заливка
HL_YELLOW = "#fef9e7"
ACCENT_BLUE = "#2457d6"
ACCENT_PURPLE = "#8e44ad"

# ── Фіг. 1: Прямий індекс проти інвертованого індексу ─────────────────────────
def fig_inverted_index_structure():
    W, H = 960, 480
    parts = [text(W / 2, 28, "Прямий індекс (документ -> слова) проти інвертованого індексу (терм -> постинги)", size=16, bold=True)]

    # Ліва панель: Прямий індекс (Forward Index)
    parts.append(rect(20, 55, 435, 405, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(237, 82, "Прямий індекс (Forward Index)", size=14, bold=True, color=INK))
    parts.append(text(237, 102, "Документи містять послідовність слів", size=12, color=MUTED))

    # Документи D1, D2, D3
    docs = [
        ("Doc 1", "алгоритм пошук дерево", 125),
        ("Doc 2", "пошук граф дерево граф", 205),
        ("Doc 3", "алгоритм хеш граф", 285)
    ]
    for dname, dwords, dy in docs:
        parts.append(rect(40, dy, 395, 62, fill=FILL, stroke=LINE, sw=1.2))
        parts.append(rect(50, dy + 12, 70, 38, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.2))
        parts.append(text(85, dy + 35, dname, size=12, bold=True, color=ACCENT_BLUE))
        parts.append(text(135, dy + 35, "->", size=14, bold=True, color=MUTED))
        parts.append(text(160, dy + 35, dwords, size=12, bold=False, anchor="start", color=INK))

    parts.append(fitbox(40, 365, 395, 80,
                        "Пошук слова 'дерево': необхідно послідовно просканувати\nкожен документ від початку до кінця -> O(N · L).\nПри мільйонах документів повний перебір блокує систему.",
                        size=11, fill="#fff5f5", stroke=WEAK, sw=1.2, color=INK))

    # Права панель: Інвертований індекс (Inverted Index)
    parts.append(rect(485, 55, 455, 405, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(712, 82, "Інвертований індекс (Inverted Index)", size=14, bold=True, color=INK))
    parts.append(text(712, 102, "Словник термів вказує на списки постингу", size=12, color=MUTED))

    # Словник + Постинги
    terms = [
        ("алгоритм", ["Doc 1 (tf:1)", "Doc 3 (tf:1)"], 125),
        ("дерево",   ["Doc 1 (tf:1)", "Doc 2 (tf:1)"], 185),
        ("граф",     ["Doc 2 (tf:2)", "Doc 3 (tf:1)"], 245),
        ("пошук",    ["Doc 1 (tf:1)", "Doc 2 (tf:1)"], 305)
    ]

    for tname, plist, ty in terms:
        # Терм у словнику
        parts.append(rect(505, ty, 95, 46, fill=HL_YELLOW, stroke=LINE, sw=1.2))
        parts.append(text(552, ty + 28, tname, size=11, bold=True, color=INK))

        # Стрілка до постингу
        parts.append(arrow(605, ty + 23, 630, ty + 23, color=GOOD, sw=1.5))

        # Постинг-список (ланцюжок блоків)
        px = 635
        for pdoc in plist:
            parts.append(rect(px, ty, 130, 46, fill=HL_GREEN, stroke=GOOD, sw=1.2))
            parts.append(text(px + 65, ty + 28, pdoc, size=10.5, bold=True, color=GOOD))
            px += 140

    parts.append(fitbox(505, 365, 415, 80,
                        "Пошук слова 'дерево': за O(1) або O(log |V|) знаходимо терм\nу словнику та миттєво зчитуємо готовий список [Doc 1, Doc 2].\nШвидкість відповіді залежить від довжини списку, а не розміру бази.",
                        size=11, fill="#f0fdf4", stroke=GOOD, sw=1.2, color=INK))

    render(os.path.join(OUT, "inverted-index-structure.svg"), W, H, *parts)
    print("Generated inverted-index-structure.svg")


# ── Фіг. 2: Дельта-кодування (d-gaps) та VByte компресія ───────────────────────
def fig_posting_compression():
    W, H = 960, 470
    parts = [text(W / 2, 28, "Стиснення списків постингу: d-gaps (дельти) та побайтовий Varint (VByte)", size=16, bold=True)]

    # 1. Абсолютні DocID -> d-gaps
    parts.append(rect(20, 55, 920, 160, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(480, 80, "Етап 1: Перетворення абсолютних DocID у різниці (d-gaps)", size=13, bold=True, color=INK))

    # Рядок абсолютних ID
    parts.append(text(120, 115, "Абсолютні DocID:", size=12, bold=True, anchor="start", color=MUTED))
    abs_ids = [104, 107, 119, 120, 145, 1000]
    ax = 270
    for val in abs_ids:
        parts.append(rect(ax, 98, 75, 30, fill=FILL, stroke=LINE, sw=1.2))
        parts.append(text(ax + 37, 118, str(val), size=11, bold=True, color=INK))
        ax += 85

    # Стрілка перетворення
    parts.append(arrow(480, 134, 480, 150, color=ACCENT_BLUE, sw=1.8))

    # Рядок дельт (d-gaps)
    parts.append(text(120, 178, "Дельти (d-gaps):", size=12, bold=True, anchor="start", color=GOOD))
    deltas = ["104", "+3", "+12", "+1", "+25", "+855"]
    dx = 270
    for dval in deltas:
        parts.append(rect(dx, 160, 75, 30, fill=HL_GREEN, stroke=GOOD, sw=1.2))
        parts.append(text(dx + 37, 180, dval, size=11, bold=True, color=GOOD))
        dx += 85

    parts.append(text(800, 180, "Малі числа = менше байтів", size=11, italic=True, color=MUTED))

    # 2. Формат VByte (Varint)
    parts.append(rect(20, 230, 920, 220, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(480, 255, "Етап 2: Побайтове кодування змінної довжини VByte (Varint)", size=13, bold=True, color=INK))

    # Приклад малого числа (1 байт)
    parts.append(rect(40, 275, 415, 160, fill="#f8fafc", stroke=LINE, sw=1.2))
    parts.append(text(247, 300, "Мале число: delta = 12 (двійкове 0001100)", size=12, bold=True, color=INK))

    parts.append(rect(80, 320, 45, 40, fill="#ffebee", stroke=WEAK, sw=1.5))
    parts.append(text(102, 345, "0", size=14, bold=True, color=WEAK))
    parts.append(text(102, 375, "MSB = 0", size=10, bold=True, color=WEAK))
    parts.append(text(102, 390, "(останній)", size=9, color=MUTED))

    parts.append(rect(130, 320, 280, 40, fill=HL_GREEN, stroke=GOOD, sw=1.5))
    parts.append(text(270, 345, "0 0 0 1 1 0 0", size=13, bold=True, color=GOOD))
    parts.append(text(270, 375, "7 біт корисного навантаження (значення = 12)", size=10, color=GOOD))

    parts.append(text(247, 420, "Результат: рівно 1 байт замість 4 байтів uint32 (економія 75%)", size=10.5, bold=True, color=INK))

    # Приклад великого числа (2 байти)
    parts.append(rect(495, 275, 425, 160, fill="#f8fafc", stroke=LINE, sw=1.2))
    parts.append(text(707, 300, "Більше число: delta = 855 (двійкове 1101010111)", size=12, bold=True, color=INK))

    # Байт 1
    parts.append(rect(520, 320, 35, 40, fill="#e8f5e9", stroke=GOOD, sw=1.5))
    parts.append(text(537, 345, "1", size=13, bold=True, color=GOOD))
    parts.append(rect(560, 320, 125, 40, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
    parts.append(text(622, 345, "0 1 0 1 1 1", size=11, bold=True, color=ACCENT_BLUE))
    parts.append(text(600, 375, "Байт 1: MSB=1 (продовжити)", size=9.5, color=MUTED))

    # Байт 2
    parts.append(rect(710, 320, 35, 40, fill="#ffebee", stroke=WEAK, sw=1.5))
    parts.append(text(727, 345, "0", size=13, bold=True, color=WEAK))
    parts.append(rect(750, 320, 150, 40, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
    parts.append(text(825, 345, "0 0 0 0 1 1 0", size=11, bold=True, color=ACCENT_BLUE))
    parts.append(text(790, 375, "Байт 2: MSB=0 (кінець)", size=9.5, color=MUTED))

    parts.append(text(707, 420, "Результат: 2 байти замість 4 байтів uint32 (економія 50%)", size=10.5, bold=True, color=INK))

    render(os.path.join(OUT, "posting-compression-dgap.svg"), W, H, *parts)
    print("Generated posting-compression-dgap.svg")


# ── Фіг. 3: Перетин списків зі Skip-вказівниками ──────────────────────────────
def fig_query_intersection_skip():
    W, H = 960, 450
    parts = [text(W / 2, 28, "Перетин списків постингу: прискорення стрибками зі Skip-вказівниками", size=16, bold=True)]

    # Загальний контейнер
    parts.append(rect(20, 55, 920, 380, fill=BG, stroke=MUTED, sw=1.2))

    # Короткий список (Term A)
    parts.append(text(40, 95, "Список A (короткий):", size=12, bold=True, anchor="start", color=ACCENT_BLUE))
    a_docs = [45, 120]
    ax = 220
    for ad in a_docs:
        parts.append(rect(ax, 75, 75, 40, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
        parts.append(text(ax + 37, 100, "Doc " + str(ad), size=11.5, bold=True, color=ACCENT_BLUE))
        ax += 240

    # Довгий список (Term B) зі скіп-вказівниками
    parts.append(text(40, 205, "Список B (довгий):", size=12, bold=True, anchor="start", color=GOOD))

    b_blocks = [
        ([3, 12, 19, 28], "Блок 0 (max: 28)", 180),
        ([31, 39, 45, 52], "Блок 1 (max: 52)", 430),
        ([65, 80, 95, 120], "Блок 2 (max: 120)", 680)
    ]

    for doc_ids, blabel, bx in b_blocks:
        parts.append(rect(bx, 160, 230, 90, fill="#f8fafc", stroke=LINE, sw=1.2))
        parts.append(text(bx + 115, 180, blabel, size=10.5, bold=True, color=MUTED))

        # Елементи всередині блоку
        elem_x = bx + 10
        for did in doc_ids:
            is_match = (did == 45 or did == 120)
            parts.append(rect(elem_x, 195, 48, 35, fill="#dcfce7" if is_match else FILL,
                              stroke=GOOD if is_match else LINE, sw=1.8 if is_match else 1.0))
            parts.append(text(elem_x + 24, 218, str(did), size=11, bold=is_match, color=GOOD if is_match else INK))
            elem_x += 54

    # Скіп-вказівники зверху (стрілки над блоками)
    parts.append(arrow(295, 155, 430, 155, color=POS, sw=2))
    parts.append(text(360, 142, "Skip Pointer (max=28 < 45)", size=10, bold=True, color=POS))

    parts.append(arrow(545, 155, 680, 155, color=POS, sw=2))
    parts.append(text(615, 142, "Skip Pointer (max=52 >= 45 -> пошук у Блоці 1)", size=10, bold=True, color=POS))

    # Стрілка пошуку конкретного Doc 45
    parts.append(arrow(257, 120, 565, 190, color=ACCENT_BLUE, sw=1.8))
    parts.append(text(410, 130, "Шукаємо Doc 45: перестрибуємо весь Блок 0!", size=11, bold=True, color=ACCENT_BLUE))

    # Пояснення внизу
    parts.append(fitbox(40, 270, 880, 145,
                        "Механізм Skip Pointers (стрибкових покажчиків):\n"
                        "1. Якщо поточний DocID у списку A (наприклад, 45) більший за максимальний DocID блоку B (28),\n"
                        "   весь блок з усіма проміжними значеннями пропускається без побайтового декодування.\n"
                        "2. Сканується лише той блок, максимальний ідентифікатор якого не менший за шуканий (Блок 1, max 52).\n"
                        "Складність перетину скорочується з O(|A| + |B|) до O(|A| · log(|B|/|A|)).",
                        size=11.5, fill="#f0fdf4", stroke=GOOD, sw=1.2, color=INK))

    render(os.path.join(OUT, "query-intersection-skip.svg"), W, H, *parts)
    print("Generated query-intersection-skip.svg")


# ── Фіг. 4: Сегментна модель оновлення (Lucene/Elasticsearch) ─────────────────
def fig_segment_merge_lifecycle():
    W, H = 960, 500
    parts = [text(W / 2, 28, "Сегментна архітектура оновлень: буфер у пам'яті, незмінні сегменти та Merge", size=16, bold=True)]

    # 1. Запис та In-Memory Buffer
    parts.append(rect(20, 55, 270, 310, fill="#f8fafc", stroke=MUTED, sw=1.2))
    parts.append(text(155, 80, "1. Буферизація в RAM", size=13, bold=True, color=INK))
    parts.append(text(155, 100, "Нові документи та видалення", size=11, color=MUTED))

    parts.append(rect(40, 120, 230, 50, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5))
    parts.append(text(155, 145, "In-Memory Index Buffer", size=12, bold=True, color=ACCENT_BLUE))
    parts.append(text(155, 160, "Накопичення (RAM)", size=10, color=MUTED))

    parts.append(rect(40, 190, 230, 50, fill="#ffebee", stroke=WEAK, sw=1.2))
    parts.append(text(155, 215, "Pending Deletes", size=12, bold=True, color=WEAK))
    parts.append(text(155, 230, "Бітова маска видалень", size=10, color=MUTED))

    parts.append(arrow(155, 250, 155, 285, color=GOOD, sw=2))
    parts.append(text(155, 270, "Flush / Commit", size=11, bold=True, color=GOOD))

    parts.append(fitbox(35, 290, 240, 65, "Скидання буфера на диск\nкожні 1–30 с або при 512 MB\nу вигляді нового сегмента.",
                        size=10.5, fill=BG, stroke="none", color=MUTED))

    # Стрілка на диск
    parts.append(arrow(295, 145, 335, 145, color=GOOD, sw=2))

    # 2. Незмінні сегменти на диску
    parts.append(rect(340, 55, 275, 310, fill="#f8fafc", stroke=MUTED, sw=1.2))
    parts.append(text(477, 80, "2. Незмінні сегменти (Disk)", size=13, bold=True, color=INK))
    parts.append(text(477, 100, "Immutable Segment Files", size=11, color=MUTED))

    segs = [
        ("Сегмент _0 (10k docs)", "#f0fdf4", GOOD, 120),
        ("Сегмент _1 (15k docs)", "#f0fdf4", GOOD, 175),
        ("Сегмент _2 (8k docs)",  "#f0fdf4", GOOD, 230),
        ("Сегмент _3 (новий)",    HL_YELLOW, LINE, 285)
    ]
    for sname, sfill, sstroke, sy in segs:
        parts.append(rect(360, sy, 235, 42, fill=sfill, stroke=sstroke, sw=1.2))
        parts.append(text(477, sy + 25, sname, size=11, bold=True, color=INK))

    # Стрілка на Merge
    parts.append(arrow(620, 200, 660, 200, color=ACCENT_PURPLE, sw=2))
    parts.append(text(640, 185, "Merge", size=11, bold=True, color=ACCENT_PURPLE))

    # 3. Фоновий Merge (Compaction)
    parts.append(rect(665, 55, 275, 310, fill="#f8fafc", stroke=MUTED, sw=1.2))
    parts.append(text(802, 80, "3. Фоновий Segment Merge", size=13, bold=True, color=ACCENT_PURPLE))
    parts.append(text(802, 100, "Каскадне об'єднання файлів", size=11, color=MUTED))

    parts.append(rect(685, 120, 235, 120, fill="#f3e8ff", stroke=ACCENT_PURPLE, sw=1.5))
    parts.append(text(802, 150, "Об'єднаний Сегмент _merged", size=12, bold=True, color=ACCENT_PURPLE))
    parts.append(text(802, 175, "33k активних документів", size=11, color=INK))
    parts.append(text(802, 195, "• Видалені DocID фізично стерті", size=10, color=WEAK))
    parts.append(text(802, 215, "• Постинги впорядковані", size=10, color=GOOD))

    parts.append(fitbox(685, 255, 235, 95,
                        "Старі сегменти _0, _1, _2 видаляються з файлової системи.\n"
                        "Кількість відкритих дескрипторів файлів зменшується,\n"
                        "швидкість пошуку відновлюється.",
                        size=10, fill=BG, stroke="none", color=MUTED))

    # 4. Нижній блок: Читання (Read Path)
    parts.append(rect(20, 380, 920, 100, fill="#f0fdf4", stroke=GOOD, sw=1.5))
    parts.append(text(480, 405, "Паралельне виконання пошукового запиту (Read Path):", size=13, bold=True, color=GOOD))
    parts.append(fitbox(40, 415, 880, 55,
                        "Запит шукає одночасно по всіх активних незмінних сегментах без блокування запису.\n"
                        "Результати фільтруються за локальними бітовими масками видалення (.del) та зливаються в єдиний Top-K скор.",
                        size=11, fill="#f0fdf4", stroke="none", color=INK))

    render(os.path.join(OUT, "segment-merge-lifecycle.svg"), W, H, *parts)
    print("Generated segment-merge-lifecycle.svg")


if __name__ == "__main__":
    fig_inverted_index_structure()
    fig_posting_compression()
    fig_query_intersection_skip()
    fig_segment_merge_lifecycle()
