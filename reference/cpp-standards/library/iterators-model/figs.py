# -*- coding: utf-8 -*-
"""Фігури до теми «Ітератори: категорії й модель обходу» (reference/cpp-standards/library)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Місток між алгоритмами й контейнерами ───────────────────────────────
def fig_iterators_bridge():
    W, H = 920, 360
    f = []

    # Контейнери ліворуч
    containers = ["std::vector", "std::list", "std::unordered_map"]
    c_boxes = []
    for i, name in enumerate(containers):
        y = 90 + i * 85
        b, w, h = textbox(150, y, [name, "контейнер"], size=13, pad=10, fill=FILL, stroke=LINE)
        f.append(b)
        c_boxes.append((150 + w/2, y))

    # Алгоритми праворуч
    algorithms = ["std::sort", "std::find", "std::accumulate"]
    a_boxes = []
    for i, name in enumerate(algorithms):
        y = 90 + i * 85
        b, w, h = textbox(770, y, [name, "алгоритм"], size=13, pad=10, fill=FILL, stroke=LINE)
        f.append(b)
        a_boxes.append((770 - w/2, y))

    # Міст-ітератор посередині
    bridge, bw, bh = textbox(460, 175, [
        "Інтерфейс Ітераторів",
        "begin() / end()",
        "operator* , operator++",
        "N + M зв'язків замість N × M"
    ], size=14, pad=14, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True)
    f.append(bridge)

    # Стрілки від контейнерів до ітераторів
    for cx, cy in c_boxes:
        f.append(arrow(cx + 10, cy, 460 - bw/2 - 10, 175, color=FIELD))

    # Стрілки від ітераторів до алгоритмів
    for ax, ay in a_boxes:
        f.append(arrow(460 + bw/2 + 10, 175, ax - 10, ay, color=FIELD))

    f.append(text(460, 320, "Алгоритми не знають про улаштування пам'яті контейнера — лише про операції ітератора", size=13, color=MUTED))

    render(os.path.join(IMG, "iterators-bridge.svg"), W, H, *f,
           title="Ітератори як абстрактний міст між алгоритмами та контейнерами")


# ── 2. Ієрархія категорій ітераторів ────────────────────────────────────────
def fig_iterator_taxonomy():
    W, H = 940, 480
    f = []

    # Рівні ієрархії
    levels = [
        ("InputIterator", "OutputIterator", "Однопрохідний обхід (single-pass), read/write"),
        ("ForwardIterator", "", "Мультипрохідний (multi-pass), збереження стану"),
        ("BidirectionalIterator", "", "Двонапрямлений обхід: operator--"),
        ("RandomAccessIterator", "", "Довільний доступ за O(1): operator+=, operator[]"),
        ("ContiguousIterator", "", "Суцільна пам'ять у RAM: std::to_address, raw pointer")
    ]

    y_start = 80

    for i, (cat1, cat2, desc) in enumerate(levels):
        y = y_start + i * 72
        if cat2:
            # Два на першому рівні
            b1, w1, h1 = textbox(270, y, [cat1, "читання (std::cin)"], size=13, pad=8, fill="#fdecea", stroke=POS)
            b2, w2, h2 = textbox(670, y, [cat2, "запис (std::cout)"], size=13, pad=8, fill="#fdecea", stroke=POS)
            f += [b1, b2]
            f.append(text(470, y + 25, desc, size=11, color=MUTED))
        else:
            fill_color = "#eaf7ee" if "Contiguous" in cat1 else FILL
            stroke_color = FIELD if "Contiguous" in cat1 else LINE
            b, w, h = textbox(470, y, [cat1, desc], size=13, pad=9, fill=fill_color, stroke=stroke_color)
            f.append(b)

            if i > 0 and i < 4:
                # стрілка успадкування вимог вгору
                f.append(arrow(470, y - 22, 470, y - 50, color=LINE))
            elif i == 4:
                f.append(arrow(470, y - 22, 470, y - 50, color=FIELD))

    f.append(text(470, 445, "Кожна наступна категорія розширює вимоги та гарантії попередньої", size=13, color=MUTED))

    render(os.path.join(IMG, "iterator-taxonomy.svg"), W, H, *f,
           title="Ієрархія категорій ітераторів та їхніх можливостей")


# ── 3. Модель Iterator + Sentinel у C++20 ───────────────────────────────────
def fig_sentinel_model():
    W, H = 900, 360
    f = []

    # C++98 симетрична пара
    f.append(text(230, 50, "Модель C++98/17: Симетрична пара", size=14, bold=True, color=INK))
    b1, w1, h1 = textbox(130, 110, ["begin()", "тип: Iter"], size=13, pad=10, fill=FILL)
    b2, w2, h2 = textbox(330, 110, ["end()", "той самий тип: Iter"], size=13, pad=10, fill=FILL)
    f += [b1, b2]
    f.append(line(130 + w1/2, 110, 330 - w2/2, 110, color=POS, dash="4,4"))
    f.append(text(230, 150, "Вимагає обчислення кінця наперед!", size=12, color=POS))

    # C++20 асиметрична пара
    f.append(text(670, 50, "Модель C++20: Iterator + Sentinel", size=14, bold=True, color=FIELD))
    b3, w3, h3 = textbox(570, 110, ["it", "тип: Iter"], size=13, pad=10, fill="#eaf7ee", stroke=FIELD)
    b4, w4, h4 = textbox(770, 110, ["sentinel", "інший тип: Sentinel"], size=13, pad=10, fill="#eaf7ee", stroke=FIELD)
    f += [b3, b4]
    f.append(line(570 + w3/2, 110, 770 - w4/2, 110, color=FIELD))
    f.append(text(670, 150, "Перевірка: it != sentinel (наприклад *it == '\\0')", size=12, color=FIELD))

    # Опис унизу
    desc_b, dw, dh = textbox(450, 260, [
        "Вартовий (Sentinel) виражає умову зупинки, а не обов'язково конкретну адресу.",
        "Це дозволяє обробку нескінченних потоків та рядків без попереднього strlen()."
    ], size=13, pad=14, fill=FILL, min_w=650)
    f.append(desc_b)

    render(os.path.join(IMG, "sentinel-model.svg"), W, H, *f,
           title="Від симетричної пари ітераторів до концепту вартового в C++20")


# ── 4. Хронологія еволюції ітераторів ─────────────────────────────────────────
def fig_iterator_history():
    W, H = 920, 340
    f = []

    milestones = [
        ("1994", "STL Степанова", "Прийняття до C++98:\nпочаток абстракції"),
        ("1998", "C++98 Standard", "5 категорій,\ntag dispatch, traits"),
        ("2011", "C++11", "range-for, auto,\nstd::begin / std::end"),
        ("2017", "C++17", "std::size, std::data,\nconstexpr ітератори"),
        ("2020", "C++20 Ranges", "Concepts, Sentinels,\nContiguousIterator")
    ]

    # Лінія хронології
    f.append(line(70, 160, 850, 160, color=FIELD, sw=3))

    for i, (year, title, desc) in enumerate(milestones):
        cx = 100 + i * 180
        cy_box = 80 if i % 2 == 0 else 240
        fill_c = "#eaf7ee" if "2020" in year else FILL
        stroke_c = FIELD if "2020" in year else LINE

        # Вузол на лінії
        f.append(circle(cx, 160, 7, fill=stroke_c, stroke=BG, sw=2))

        # Блок опису
        b, w, h = textbox(cx, cy_box, [f"{year}: {title}", desc], size=12, pad=9, fill=fill_c, stroke=stroke_c)
        f.append(b)

        # Стрілка/лінія до вузла
        if i % 2 == 0:
            f.append(line(cx, cy_box + h/2, cx, 160 - 7, color=stroke_c))
        else:
            f.append(line(cx, cy_box - h/2, cx, 160 + 7, color=stroke_c))

    f.append(text(460, 315, "Еволюція від вказівникової магії C++98 до концептуальних діапазонів C++20", size=13, color=MUTED))

    render(os.path.join(IMG, "iterator-history.svg"), W, H, *f,
           title="Хронологія розвитку абстракції ітераторів у C++")


if __name__ == "__main__":
    fig_iterators_bridge()
    fig_iterator_taxonomy()
    fig_sentinel_model()
    fig_iterator_history()
    print("Всі фігури для iterators-model успішно згенеровано.")
