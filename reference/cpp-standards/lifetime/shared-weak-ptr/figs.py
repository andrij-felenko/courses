# -*- coding: utf-8 -*-
"""Фігури до теми «shared_ptr і weak_ptr: спільне володіння й розрив циклів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"   # стан після смерті об'єкта
COOL = "#eef2fb"   # стан після звільнення блока
LIVE = "#e8f6ee"   # усе живе


# ── 1. Два лічильники — дві смерті ─────────────────────────────────────────
def fig_two_counters():
    W, H = 820, 480
    f = []

    states = [
        (40,  "сильних 2 · слабких 1", "об'єкт живий, блок живий", LIVE, FIELD),
        (150, "сильних 1 · слабких 1", "об'єкт живий, блок живий", LIVE, FIELD),
        (260, "сильних 0 · слабких 1", "об'єкта нема, блок живий: lock() дає порожньо", WARM, POS),
        (370, "сильних 0 · слабких 0", "блок звільнено, у купі не лишилось нічого", COOL, NEG),
    ]
    for y, counters, note, fill, stroke in states:
        f.append(fitbox(50, y, 320, 68, counters + "\n" + note,
                        size=12, fill=fill, stroke=stroke))

    events = [
        (112, "знищено одну з копій shared_ptr"),
        (222, "пішов ОСТАННІЙ власник → деструктор об'єкта"),
        (332, "пішов останній спостерігач"),
    ]
    for y, label in events:
        f.append(arrow(210, y, 210, y + 36))
        f.append(text(240, y + 24, label, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, 'two-counters.svg'), W, H, *f,
           title="Дві смерті: об'єкт гине на нулі сильних, блок — на нулі обох")


# ── 2. Два виділення проти одного ──────────────────────────────────────────
def fig_make_shared_layout():
    W, H = 920, 250
    f = []

    # Ліворуч: shared_ptr(new T)
    f.append(text(50, 40, "shared_ptr<T>(new T)", size=14, color=INK,
                  anchor="start", bold=True))
    f.append(fitbox(50, 62, 150, 96, "керівний блок\nсильних\nслабких\nвидаляч", size=12))
    f.append(arrow(204, 110, 250, 110))
    f.append(fitbox(254, 62, 150, 96, "об'єкт T", size=13))
    f.append(text(50, 190, "два виділення в купі", size=11, color=MUTED, anchor="start"))
    f.append(text(50, 210, "об'єкт звільняється окремо, блок живе далі",
                  size=11, color=MUTED, anchor="start"))

    f.append(line(452, 26, 452, 220, color=MUTED, sw=1, dash="6 5"))

    # Праворуч: make_shared<T>()
    f.append(text(500, 40, "make_shared<T>()", size=14, color=INK,
                  anchor="start", bold=True))
    f.append(rect(496, 56, 374, 108, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(fitbox(510, 68, 168, 84, "керівний блок\nсильних\nслабких", size=12))
    f.append(fitbox(694, 68, 162, 84, "об'єкт T", size=13))
    f.append(text(500, 190, "одне виділення на двох", size=11, color=MUTED, anchor="start"))
    f.append(text(500, 210, "ділянка повертається лише цілком — блок і об'єкт разом",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'make-shared-layout.svg'), W, H, *f,
           title="Де лежить керівний блок: окремо від об'єкта чи впритул до нього")


# ── 3. Цикл із сильних посилань і його розрив ──────────────────────────────
def fig_cycle_break():
    W, H = 880, 410
    f = []

    # Верхня панель: обидва ребра сильні
    f.append(text(50, 44, "обидва ребра сильні", size=14, color=INK,
                  anchor="start", bold=True))
    f.append(fitbox(120, 66, 200, 62, "вузол «батько»\nсильних: 1", size=12,
                    fill=WARM, stroke=POS))
    f.append(fitbox(540, 66, 200, 62, "вузол «дитина»\nсильних: 1", size=12,
                    fill=WARM, stroke=POS))
    f.append(text(430, 80, "kids: shared_ptr", size=11, color=MUTED))
    f.append(arrow(324, 90, 536, 90))
    f.append(arrow(536, 114, 324, 114))
    f.append(text(430, 136, "parent: shared_ptr", size=11, color=MUTED))
    f.append(text(430, 172,
                  "зовнішніх власників нема, а лічильники стоять на одиниці — жоден не впаде до нуля",
                  size=11, color=MUTED))

    f.append(line(40, 200, 840, 200, color=MUTED, sw=1, dash="6 5"))

    # Нижня панель: зворотне ребро слабке
    f.append(text(50, 246, "зворотне ребро — слабке", size=14, color=INK,
                  anchor="start", bold=True))
    f.append(fitbox(120, 268, 200, 62, "вузол «батько»\nсильних: 1 → 0", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(540, 268, 200, 62, "вузол «дитина»\nсильних: 1 → 0", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(text(430, 282, "kids: shared_ptr", size=11, color=MUTED))
    f.append(arrow(324, 292, 536, 292))
    f.append(line(536, 316, 324, 316, color=MUTED, sw=1.5, dash="7 5"))
    f.append(text(430, 338, "parent: weak_ptr — спостерігає, не тримає", size=11, color=MUTED))
    f.append(text(430, 374,
                  "корінь відпущено — сильний лічильник падає до нуля, дерево згортається знизу вгору",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'cycle-break.svg'), W, H, *f,
           title="Цикл із сильних посилань і його розрив слабким ребром")


# ── 4. Гонка між смертю об'єкта й прибиранням запису (вставка про кеш) ─────
def fig_weak_cache_race():
    W, H = 940, 400
    f = []

    cols = [185, 365, 545, 725]
    CW, BH = 165, 64
    rows = [70, 180, 290]

    for y, label in zip(rows, ["потік A", "мапа кешу", "потік B"]):
        f.append(text(24, y + 38, label, size=12, color=INK, anchor="start", bold=True))

    f.append(line(cols[1], 52, cols[3] + CW, 52, color=MUTED, sw=1, dash="6 5"))
    f.append(text((cols[1] + cols[3] + CW) / 2, 40,
                  "вікно: об'єкта вже нема, запис іще є", size=11, color=MUTED))

    f.append(fitbox(cols[0], rows[0], CW, BH,
                    "останній власник пішов\nсильних → 0, ~Texture()",
                    size=11, fill=WARM, stroke=POS))
    f.append(fitbox(cols[3], rows[0], CW, BH,
                    "видаляч бере замок:\nзапис не expired → не чіпає",
                    size=11, fill=LIVE, stroke=FIELD))

    f.append(fitbox(cols[1], rows[1], CW, BH,
                    "weak є, об'єкта нема:\nexpired() == true",
                    size=11, fill=WARM, stroke=POS))
    f.append(fitbox(cols[2], rows[1], CW, BH,
                    "запис перезаписано\nна новий об'єкт",
                    size=11, fill=LIVE, stroke=FIELD))

    f.append(fitbox(cols[2], rows[2], CW, BH,
                    "get(): lock() дає порожньо\n→ вантажить новий",
                    size=11, stroke=NEG))

    f.append(text(24, 378,
                  "Без перевірки expired() видаляч A стер би живий запис B — "
                  "і на один ключ у програмі було б два об'єкти.",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'weak-cache-race.svg'), W, H, *f,
           title="Чому видаляч не має права стирати запис наосліп")


if __name__ == '__main__':
    fig_two_counters()
    fig_make_shared_layout()
    fig_cycle_break()
    fig_weak_cache_race()
    print("ok")
