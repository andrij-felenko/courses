# -*- coding: utf-8 -*-
"""Фігури до теми «Алгоритми STL замість ручних циклів» (reference/cpp-standards/library/stl-algorithms)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Таксономія алгоритмів та вимоги до ітераторів ────────────────────────
def fig_algo_taxonomy():
    W, H = 920, 480
    f = []

    f.append(text(W / 2, 35, "Класифікація алгоритмів STL та сумісність із категоріями ітераторів", size=16, bold=True))

    categories = [
        ("Немодифікуючі пошукові", ["std::find, std::count", "std::all_of, std::search"], "Input / Forward", POS, "#fdecea"),
        ("Модифікуючі та мутуючі", ["std::transform, std::copy", "std::fill, std::replace"], "Output / Forward", FIELD, "#eaf7ee"),
        ("Впорядкування й розділення", ["std::sort, std::nth_element", "std::partition, std::stable_sort"], "RandomAccess / Bidi", NEG, "#eef2ff"),
        ("Двійковий пошук", ["std::lower_bound", "std::equal_range"], "Forward (O(log N) на Random)", MUTED, "#f4f6f8"),
        ("Чисельні (Numerics)", ["std::accumulate, std::reduce", "std::inclusive_scan, std::iota"], "InputIterator", INK, "#fcf8e3"),
    ]

    for i, (title_str, algo_lines, iter_req, color, bg_fill) in enumerate(categories):
        y = 90 + i * 72
        
        tb, tw, th = textbox(210, y, [title_str], size=13, pad=10, fill=bg_fill, stroke=color, sw=1.5, bold=True)
        f.append(tb)

        ab, aw, ah = textbox(530, y, algo_lines, size=12, pad=8, fill=BG, stroke=LINE, sw=1.2)
        f.append(ab)

        ib, iw, ih = textbox(810, y, [iter_req], size=12, pad=8, fill=bg_fill, stroke=color, sw=1.2, bold=True)
        f.append(ib)

        f.append(arrow(210 + tw / 2 + 6, y, 530 - aw / 2 - 6, y, color=color, sw=1.5))
        f.append(arrow(530 + aw / 2 + 6, y, 810 - iw / 2 - 6, y, color=color, sw=1.5))

    f.append(text(W / 2, 455, "Невідповідність категорії ітератора вимогам алгоритму виявляється на етапі компіляції", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "algo-taxonomy.svg"), W, H, *f,
           title="Таксономія алгоритмів STL")


# ── 2. Механіка Remove-Erase ідіоми ──────────────────────────────────────────
def fig_remove_erase_idiom():
    W, H = 920, 450
    f = []

    f.append(text(W / 2, 32, "Двофазна механіка видалення елементів: std::remove + container.erase()", size=16, bold=True))

    # Фаза 1: Вхідний вектор
    f.append(text(120, 85, "1. Початковий вектор:", size=13, anchor="start", bold=True))
    v1_items = ["10", "0", "20", "0", "30", "0"]
    for j, val in enumerate(v1_items):
        x = 340 + j * 75
        cell_fill = "#fdecea" if val == "0" else BG
        cell_stroke = POS if val == "0" else LINE
        b, w, h = textbox(x, 85, val, size=14, pad=10, fill=cell_fill, stroke=cell_stroke, sw=1.5)
        f.append(b)
    f.append(text(830, 85, "розмір = 6", size=13, color=MUTED))

    f.append(arrow(460, 120, 460, 155, color=LINE, sw=1.8))
    f.append(text(475, 142, "std::remove(v.begin(), v.end(), 0)", size=12, color=POS, anchor="start", bold=True))

    # Фаза 2: Після std::remove
    f.append(text(120, 200, "2. Після std::remove:", size=13, anchor="start", bold=True))
    v2_items = ["10", "20", "30", "?", "?", "?"]
    for j, val in enumerate(v2_items):
        x = 340 + j * 75
        is_moved = j >= 3
        cell_fill = "#f4f6f8" if is_moved else "#eaf7ee"
        cell_stroke = MUTED if is_moved else FIELD
        b, w, h = textbox(x, 200, val, size=14, pad=10, fill=cell_fill, stroke=cell_stroke, sw=1.5)
        f.append(b)
    
    # Вказівник new_end
    f.append(arrow(565, 260, 565, 225, color=FIELD, sw=2))
    f.append(text(565, 278, "ітератор new_end (повертає std::remove)", size=12, color=FIELD, bold=True))
    f.append(text(830, 200, "розмір = 6 (!)", size=13, color=POS, bold=True))

    f.append(arrow(460, 290, 460, 325, color=LINE, sw=1.8))
    f.append(text(475, 312, "v.erase(new_end, v.end())", size=12, color=FIELD, anchor="start", bold=True))

    # Фаза 3: Після erase
    f.append(text(120, 370, "3. Після v.erase(...):", size=13, anchor="start", bold=True))
    v3_items = ["10", "20", "30"]
    for j, val in enumerate(v3_items):
        x = 340 + j * 75
        b, w, h = textbox(x, 370, val, size=14, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.5)
        f.append(b)
    f.append(text(830, 370, "розмір = 3", size=13, color=FIELD, bold=True))

    f.append(text(W / 2, 425, "std::remove не змінює розмір контейнера — він лише зсуває валідні елементи ліворуч", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "remove-erase-idiom.svg"), W, H, *f,
           title="Механіка Remove-Erase ідіоми")


# ── 3. C++20 Ranges та проєкції в пайплайнах ─────────────────────────────────
def fig_ranges_projections_pipe():
    W, H = 920, 380
    f = []

    f.append(text(W / 2, 35, "Архітектура обробки даних у C++20 Ranges: проєкції та конвеєри", size=16, bold=True))

    b1, w1, h1 = textbox(130, 160, ["Джерело даних", "std::vector<User>", "[User1, User2, ...]"], size=13, pad=12, fill="#eef2ff", stroke=NEG)
    b2, w2, h2 = textbox(360, 160, ["Проєкція", "&User::score", "витягує поле без копії"], size=13, pad=12, fill="#fcf8e3", stroke=MUTED)
    b3, w3, h3 = textbox(590, 160, ["Фільтр (View)", "views::filter", "score >= 50"], size=13, pad=12, fill="#eaf7ee", stroke=FIELD)
    b4, w4, h4 = textbox(810, 160, ["Акумуляція / Алгоритм", "std::ranges::copy / sum", "кінцевий результат"], size=13, pad=12, fill="#fdecea", stroke=POS)

    f += [b1, b2, b3, b4]

    f.append(arrow(130 + w1 / 2 + 6, 160, 360 - w2 / 2 - 6, 160, color=NEG, sw=1.8))
    f.append(arrow(360 + w2 / 2 + 6, 160, 590 - w3 / 2 - 6, 160, color=FIELD, sw=1.8))
    f.append(arrow(590 + w3 / 2 + 6, 160, 810 - w4 / 2 - 6, 160, color=POS, sw=1.8))

    f.append(text(W / 2, 270, "Переваги конвеєра: нульова ціна абстракції (Zero-Cost), ліниве обчислення (Lazy), відсутність аллокацій", size=13, bold=True, color=INK))
    f.append(text(W / 2, 305, "Елементи обробляються по одному по мірі потреби в циклі — тимчасові вектори не створюються", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "ranges-projections-pipe.svg"), W, H, *f,
           title="C++20 Ranges та проєкції у конвеєрах")


if __name__ == "__main__":
    fig_algo_taxonomy()
    fig_remove_erase_idiom()
    fig_ranges_projections_pipe()
    print("Figures generated successfully.")
