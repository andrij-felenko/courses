# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір контейнерів STL: механіки пам'яті, інвалідація та ціна доступу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Внутрішня структура пам'яті основних категорій контейнерів ────────────
def fig_memory_layouts():
    W, H = 1000, 560
    f = []

    # 1. std::vector / std::array — Неперервний масив
    f.append(rect(30, 40, 450, 220, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(text(255, 68, "std::vector / std::array (Неперервний масив)", size=13, color=FIELD, bold=True))
    f.append(rect(50, 95, 410, 48, fill="#e8f6ee", stroke=FIELD, sw=1.5))
    for i in range(5):
        x = 50 + i * 82
        f.append(rect(x, 95, 82, 48, fill="#e8f6ee", stroke=FIELD))
        f.append(text(x + 41, 124, f"Elem {i}", size=11, color=INK))
    f.append(mtext(255, 172,
                   ["100% кеш-локальність: елементи лежать один за одним.",
                    "Виділення: 1 цілісний блок у купі (або стек для std::array).",
                    "Крок ітератора: просто зсув вказівника ptr++."],
                   size=11, color=INK, lh=1.4))

    # 2. std::deque — Сегментований буфер
    f.append(rect(520, 40, 450, 220, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(text(745, 68, "std::deque (Масив покажчиків на блоки)", size=13, color=FIELD, bold=True))
    # Масив покажчиків (Map)
    f.append(rect(540, 95, 140, 36, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(610, 117, "Map (Pointers)", size=10, color=NEG, bold=True))
    # Блоки даних
    f.append(rect(720, 90, 230, 32, fill="#e8f6ee", stroke=FIELD))
    f.append(text(835, 110, "Page 0: [E0][E1][E2][E3]", size=10, color=INK))
    f.append(rect(720, 130, 230, 32, fill="#e8f6ee", stroke=FIELD))
    f.append(text(835, 150, "Page 1: [E4][E5][E6][E7]", size=10, color=INK))
    f.append(arrow(680, 105, 720, 105))
    f.append(arrow(680, 120, 720, 145))
    f.append(mtext(745, 192,
                   ["Двовенцева черга без перевиділення всього буфера.",
                    "Індексація: (index / block_size) та (index % block_size).",
                    "Розширення в обидва боки без копіювання наявних елементів."],
                   size=11, color=INK, lh=1.4))

    # 3. std::list — Вузлова структура (двозв'язний список)
    f.append(rect(30, 280, 450, 250, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(text(255, 308, "std::list (Двозв'язний список вузлів)", size=13, color=POS, bold=True))
    # Вузли
    xs = [50, 195, 340]
    for idx, x in enumerate(xs):
        f.append(rect(x, 335, 110, 56, fill="#fdecea", stroke=POS, sw=1.5))
        f.append(text(x + 55, 355, f"Node {idx}", size=11, color=POS, bold=True))
        f.append(text(x + 55, 376, "Prev | Data | Next", size=9, color=MUTED))
    f.append(arrow(160, 355, 195, 355))
    f.append(arrow(195, 375, 160, 375))
    f.append(arrow(305, 355, 340, 355))
    f.append(arrow(340, 375, 305, 375))
    f.append(mtext(255, 422,
                   ["Кожен елемент — окрема алокація у купі (+16/24 байт оверхеду).",
                    "Повна інвалідаційна стабільність: вказівники не ламаються.",
                    "Кеш-промахи на кожному кроці iterator++ (pointer chasing)."],
                   size=11, color=INK, lh=1.4))

    # 4. std::flat_map (C++23) — Два впорядковані неперервні вектори
    f.append(rect(520, 280, 450, 250, fill="#f8fafc", stroke=MUTED, sw=1.5))
    f.append(text(745, 308, "std::flat_map (C++23 Векторні ключі та значення)", size=13, color=FIELD, bold=True))
    # Ключі
    f.append(rect(540, 335, 410, 36, fill="#e8f6ee", stroke=FIELD))
    f.append(text(745, 357, "Keys Vector:   [ K0 ][ K1 ][ K2 ][ K3 ][ K4 ] (Sorted)", size=10, color=INK))
    # Значення
    f.append(rect(540, 380, 410, 36, fill="#eaf0fd", stroke=NEG))
    f.append(text(745, 402, "Values Vector: [ V0 ][ V1 ][ V2 ][ V3 ][ V4 ]", size=10, color=INK))
    f.append(mtext(745, 442,
                   ["Заміна std::map для переважно читальних сценаріїв.",
                    "Пошук: std::lower_bound (двійковий пошук у кеш-дружньому масиві).",
                    "Вставка: O(N) через зсув елементів, але без алокації нових вузлів."],
                   size=11, color=INK, lh=1.4))

    render(os.path.join(OUT, 'memory-layouts.svg'), W, H, *f,
           title="Фізичне розташування даних у пам'яті для різних класів STL-контейнерів")


# ── 2. Дерево прийняття рішень для вибору контейнера ────────────────────────
def fig_decision_tree():
    W, H = 1000, 520
    f = []

    # Корінь
    f.append(fitbox(370, 30, 260, 50, "Яка головна вимога\nдо даних?", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    # Гілка 1: Послідовність
    f.append(arrow(430, 80, 200, 130))
    f.append(fitbox(80, 130, 240, 46, "Впорядкована послідовність\n(Sequence)", size=11, fill="#f8fafc", stroke=MUTED))

    f.append(arrow(140, 176, 80, 220))
    f.append(fitbox(20, 220, 120, 44, "Фіксований\nрозмір?", size=10))
    f.append(arrow(80, 264, 80, 300))
    f.append(fitbox(20, 300, 120, 44, "std::array", size=11, bold=True, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(200, 176, 200, 220))
    f.append(fitbox(150, 220, 110, 44, "Додавання\nз обох кінців?", size=10))
    f.append(arrow(205, 264, 205, 300))
    f.append(fitbox(150, 300, 110, 44, "std::deque", size=11, bold=True, fill="#e8f6ee", stroke=FIELD))

    f.append(arrow(260, 176, 330, 220))
    f.append(fitbox(275, 220, 115, 44, "Потрібна абсолютна\nстабільність посилань?", size=10))
    f.append(arrow(332, 264, 332, 300))
    f.append(fitbox(275, 300, 115, 44, "std::list", size=11, bold=True, fill="#fdecea", stroke=POS))

    # Стандартний вибір для послідовності
    f.append(fitbox(100, 380, 240, 50, "За замовчуванням для послідовностей:\nstd::vector", size=12, bold=True, fill="#e8f6ee", stroke=FIELD))

    # Гілка 2: Ключ-Значення / Множина
    f.append(arrow(570, 80, 770, 130))
    f.append(fitbox(660, 130, 240, 46, "Пошук за ключем / Унікальність\n(Associative)", size=11, fill="#f8fafc", stroke=MUTED))

    f.append(arrow(720, 176, 620, 220))
    f.append(fitbox(550, 220, 140, 44, "Потрібен порядок ключів\nабо діапазонний пошук?", size=10))
    f.append(arrow(580, 264, 530, 300))
    f.append(fitbox(460, 300, 130, 44, "Рідкісні вставки:\nstd::flat_map (C++23)", size=10, bold=True, fill="#e8f6ee", stroke=FIELD))
    f.append(arrow(650, 264, 660, 300))
    f.append(fitbox(605, 300, 125, 44, "Часті вставки:\nstd::map / std::set", size=10, bold=True, fill="#fdecea", stroke=POS))

    f.append(arrow(840, 176, 840, 220))
    f.append(fitbox(750, 220, 180, 44, "Найшвидший точковий пошук O(1)?\n(Порядок ключів не важливий)", size=10))
    f.append(arrow(840, 264, 840, 300))
    f.append(fitbox(740, 300, 200, 44, "std::unordered_map / set", size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    # Нижнє підсумкове правило
    f.append(rect(40, 450, 920, 50, fill="#ffffff", stroke=MUTED))
    f.append(text(500, 480, "Золоте правило STL: починайте з std::vector. Змінюйте контейнер лише за наявності чіткого профілю навантаження.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, 'decision-tree.svg'), W, H, *f,
           title="Алгоритм вибору оптимального STL-контейнера за вимогами до обходу та стабільності")


# ── 3. Ціна стрибка в пам'яті: Кеш-ієрархія проти розкиданих вузлів ──────────
def fig_cache_latency_wall():
    W, H = 1000, 460
    f = []

    # Ліва частина: Неперервний масив у кшеі L1/L2
    f.append(rect(40, 40, 430, 380, fill="#e8f6ee", stroke=FIELD, sw=2))
    f.append(text(255, 75, "Неперервний масив (std::vector)", size=13, color=FIELD, bold=True))

    f.append(rect(70, 110, 370, 60, fill="#ffffff", stroke=FIELD))
    f.append(text(255, 135, "CPU L1 Cache Line (64 байти)", size=11, color=FIELD, bold=True))
    f.append(text(255, 155, "Завантажує 8-16 елементів за один такт!", size=10, color=INK))

    f.append(arrow(255, 170, 255, 220))

    f.append(rect(70, 220, 370, 70, fill="#ffffff", stroke=FIELD))
    f.append(text(255, 245, "Hardware Prefetcher", size=11, color=FIELD, bold=True))
    f.append(text(255, 268, "Передбачає послідовний доступ і префетчить наступну лінію", size=10, color=INK))

    f.append(fitbox(70, 320, 370, 60, "Затримка доступу: ~1-4 такти CPU\nПропускна здатність: ~100+ ГБ/с", size=12, bold=True, fill="#e8f6ee", stroke=FIELD))

    # Права частина: Стрибки по вузлах у RAM
    f.append(rect(530, 40, 430, 380, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(745, 75, "Вузловий список (std::list / std::map)", size=13, color=POS, bold=True))

    f.append(rect(560, 110, 370, 60, fill="#ffffff", stroke=POS))
    f.append(text(745, 135, "Pointer Chasing (Стрибок за адресою)", size=11, color=POS, bold=True))
    f.append(text(745, 155, "Адреса наступного вузла невідома до прочитання поточного!", size=10, color=INK))

    f.append(arrow(745, 170, 745, 220))

    f.append(rect(560, 220, 370, 70, fill="#ffffff", stroke=POS))
    f.append(text(745, 245, "L3 / Main RAM Miss", size=11, color=POS, bold=True))
    f.append(text(745, 268, "Кожен вузол лежить у випадковому місці купи (промах кешу)", size=10, color=INK))

    f.append(fitbox(560, 320, 370, 60, "Затримка доступу: ~150-300 тактів CPU!\nКонвеєр процесора простоює (Stall)", size=12, bold=True, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'cache-latency-wall.svg'), W, H, *f,
           title="Чому неперервність у пам'яті компенсує неоптимальну теоретичну складність O(N)")


if __name__ == '__main__':
    fig_memory_layouts()
    fig_decision_tree()
    fig_cache_latency_wall()
    print("ok")
