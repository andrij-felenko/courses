# -*- coding: utf-8 -*-
"""
Фігури для вставки «-Os, gc-sections і LTO: стиснути образ, не зламавши його»
(⚙️ вставка до §4.2.4, файл ch21-s4-a-size-opt.md).

Нумерація: Рис. 4.2.4b.1, Рис. 4.2.4b.2
SVG-файли: fig-21-4b-1-levers.svg, fig-21-4b-2-measure-verify.svg → ./img/

Запуск: python figs-ch21-s4-a-size-opt.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра вставки (відповідно до каркасу)
GOLD_FILL   = "#fff8e6"
GOLD_STROKE = "#caa24a"
GREEN_FILL  = "#eef6ef"
GREEN_STROKE= "#27ae60"
BLUE_FILL   = "#e8eef8"
BLUE_STROKE = "#2457d6"
DARK_CODE   = "#0f1b14"
DARK_CODE2  = "#13202a"


# ── §21.4b (вставка до 4.2.4) — -Os, gc-sections, LTO ───────────────────────

def fig4b1_levers():
    """
    Рис. 4.2.4b.1 — Три незалежні важелі стиснення образу.
    Три картки поруч (стиль fig2a1_levels): -Os (GOLD), gc-sections (GREEN), LTO (BLUE).
    """
    W, H = 900, 380

    # Заголовок
    frags = []
    frags.append(text(W / 2, 30,
                      "Три незалежні важелі стиснення образу прошивки",
                      size=17, bold=True))
    frags.append(text(W / 2, 52,
                      "кожен діє своїм механізмом; вмикати можна разом",
                      size=12, color=MUTED, italic=True))

    # Позиції трьох карток
    card_w = 246
    card_h = 250
    card_y = 74
    gaps   = [36, 36]
    x1 = 28
    x2 = x1 + card_w + gaps[0]
    x3 = x2 + card_w + gaps[1]

    # Картка 1: -Os (GOLD)
    frags.append(rect(x1, card_y, card_w, card_h,
                      fill=GOLD_FILL, stroke=GOLD_STROKE, sw=2.2, rx=10))
    frags.append(text(x1 + card_w / 2, card_y + 34,
                      "-Os", size=22, color="#8a6a14", bold=True))
    frags.append(text(x1 + card_w / 2, card_y + 56,
                      "оптимізація за розміром", size=11, color=MUTED, italic=True))
    frags.append(text(x1 + card_w / 2, card_y + 70,
                      "optimize for size", size=10, color=MUTED, italic=True))
    # Роздільник
    frags.append(line(x1 + 16, card_y + 74, x1 + card_w - 16, card_y + 74,
                      color=GOLD_STROKE, sw=1.2))

    os_body, _, _ = textbox(x1 + card_w / 2, card_y + 134,
                             "компілятор обирає\nкомпактний варіант\nкоду, а не швидкий\n"
                             "(не розгортає цикли,\nвикликає спільне\nзамість вбудовування)",
                             size=11, pad=8, fill=GOLD_FILL, stroke=GOLD_STROKE,
                             sw=0.8, color=INK, min_w=card_w - 32)
    frags.append(os_body)

    frags.append(text(x1 + card_w / 2, card_y + card_h - 22,
                      "жме .text (код)", size=11, color=GOLD_STROKE, bold=True))

    # Картка 2: gc-sections (GREEN)
    frags.append(rect(x2, card_y, card_w, card_h,
                      fill=GREEN_FILL, stroke=GREEN_STROKE, sw=2.2, rx=10))
    frags.append(text(x2 + card_w / 2, card_y + 34,
                      "--gc-sections", size=16, color="#1a6b30", bold=True))
    frags.append(text(x2 + card_w / 2, card_y + 55,
                      "прибирання секцій", size=11, color=MUTED, italic=True))
    frags.append(text(x2 + card_w / 2, card_y + 68,
                      "garbage collection of sections", size=10, color=MUTED, italic=True))
    frags.append(line(x2 + 16, card_y + 80, x2 + card_w - 16, card_y + 80,
                      color=GREEN_STROKE, sw=1.2))

    gc_body, _, _ = textbox(x2 + card_w / 2, card_y + 139,
                             "лінкер викидає функції\nта змінні, на які\nніхто не посилається\n"
                             "(кожна — в окремій\nсекції; невжиті секції\nпросто не входять в образ)",
                             size=11, pad=8, fill=GREEN_FILL, stroke=GREEN_STROKE,
                             sw=0.8, color=INK, min_w=card_w - 32)
    frags.append(gc_body)

    frags.append(text(x2 + card_w / 2, card_y + card_h - 22,
                      "вирізає невжите з бібліотек", size=11, color=GREEN_STROKE, bold=True))

    # Картка 3: LTO (BLUE)
    frags.append(rect(x3, card_y, card_w, card_h,
                      fill=BLUE_FILL, stroke=BLUE_STROKE, sw=2.2, rx=10))
    frags.append(text(x3 + card_w / 2, card_y + 34,
                      "-flto", size=22, color="#1a3880", bold=True))
    frags.append(text(x3 + card_w / 2, card_y + 56,
                      "оптимізація під час лінкування", size=10, color=MUTED, italic=True))
    frags.append(text(x3 + card_w / 2, card_y + 69,
                      "link-time optimization, LTO", size=10, color=MUTED, italic=True))
    frags.append(line(x3 + 16, card_y + 80, x3 + card_w - 16, card_y + 80,
                      color=BLUE_STROKE, sw=1.2))

    lto_body, _, _ = textbox(x3 + card_w / 2, card_y + 137,
                              "оптимізація переноситься\nна момент лінкування,\nколи видно всю програму:\n"
                              "інлайн і прибирання\nмертвого коду працюють\nміж файлами разом",
                              size=11, pad=8, fill=BLUE_FILL, stroke=BLUE_STROKE,
                              sw=0.8, color=INK, min_w=card_w - 32)
    frags.append(lto_body)

    frags.append(text(x3 + card_w / 2, card_y + card_h - 22,
                      "чистить крізь межі файлів", size=11, color=BLUE_STROKE, bold=True))

    render(os.path.join(OUT, "fig-21-4b-1-levers.svg"), W, H, *frags,
           title=None)
    print("wrote fig-21-4b-1-levers.svg")


def fig4b2_measure_verify():
    """
    Рис. 4.2.4b.2 — Дисципліна стиснення: петля «важіль → map → залив → перевірка».
    Чотири вузли по колу + червона гілка «зламалось».
    """
    W, H = 800, 480

    frags = []
    frags.append(text(W / 2, 28,
                      "Дисципліна стиснення — петля, а не один прапорець",
                      size=16, bold=True))
    frags.append(text(W / 2, 50,
                      "один важіль → міряй → перевір на залізі → тоді наступний",
                      size=12, color=MUTED, italic=True))

    # Чотири вузли по колу (cx, cy, текст, fill, stroke)
    CX, CY = 400, 280   # центр петлі
    RX, RY = 200, 140   # радіуси еліпса

    import math
    # кути: верх=270° (важіль), праворуч=0° (size/map), низ=90° (залив+перевірка), ліворуч=180° (успіх→далі)
    angles = [270, 0, 90, 180]
    node_cx = [CX + RX * math.cos(math.radians(a)) for a in angles]
    node_cy = [CY + RY * math.sin(math.radians(a)) for a in angles]

    node_specs = [
        # текст, fill, stroke, text_color
        ("увімкни\nОДИН важіль",       GOLD_FILL,  GOLD_STROKE,  "#8a6a14"),
        ("глянь у size/map:\nскільки і де",  "#f4f6f8",  "#555555",    INK),
        ("залий і перевір\nна залізі,\nпристрій робить\nте саме?", GREEN_FILL, GREEN_STROKE, "#1a6b30"),
        ("✓ наступний\nважіль",         GREEN_FILL, GREEN_STROKE, "#1a6b30"),
    ]

    node_w = 148
    node_h = 82

    # Малюємо вузли
    for i, (lbl, nfill, nstroke, ncol) in enumerate(node_specs):
        nx, ny = node_cx[i], node_cy[i]
        box, _, _ = textbox(nx, ny, lbl, size=12, pad=9,
                            fill=nfill, stroke=nstroke, sw=2.0,
                            color=ncol, bold=True, min_w=node_w)
        frags.append(box)

    # Стрілки по колу (0→1→2→3→0), але оминаємо самі вузли
    # Наближена геометрія: стріляємо між центрами з невеликим offset
    arrow_defs = [
        (0, 1),  # важіль → map
        (1, 2),  # map → залив
        (2, 3),  # залив → успіх/наступний
        (3, 0),  # наступний → важіль (замикає петлю)
    ]

    # Обчислюємо точки на межі рамок (спрощено — зсув до сусіднього центру)
    def edge_point(nx, ny, tx, ty, bw=node_w, bh=node_h):
        """Знайти точку на межі рамки (cx,cy,bw,bh) у напрямку до (tx,ty)."""
        dx, dy = tx - nx, ty - ny
        if abs(dx) < 0.001 and abs(dy) < 0.001:
            return nx, ny
        # Перетин з прямокутником
        hw, hh = bw / 2 + 4, bh / 2 + 4
        if abs(dx) * hh > abs(dy) * hw:
            # перетин по вертикальній межі
            t = hw / abs(dx)
        else:
            t = hh / abs(dy)
        return nx + dx * t, ny + dy * t

    colors_arr = [GOLD_STROKE, "#555555", GREEN_STROKE, GOLD_STROKE]
    for (i, j), col in zip(arrow_defs, colors_arr):
        ax, ay = edge_point(node_cx[i], node_cy[i], node_cx[j], node_cy[j])
        bx, by = edge_point(node_cx[j], node_cy[j], node_cx[i], node_cy[i])
        frags.append(arrow(ax, ay, bx, by, color=col, sw=2.0))

    # Червона гілка «зламалось» — від вузла 2 (залив+перевірка) вниз-праворуч
    fail_x1 = node_cx[2] + node_w / 2 + 4
    fail_y1 = node_cy[2]
    fail_x2 = fail_x1 + 90
    fail_y2 = fail_y1

    frags.append(arrow(fail_x1, fail_y1, fail_x2, fail_y2, color=POS, sw=2.0))

    fail_box, _, _ = textbox(fail_x2 + 82, fail_y2,
                              "зламалось!\nвинуватець\nочевидний —\nце останній\nважіль",
                              size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.8,
                              color=POS, bold=True, min_w=110)
    frags.append(fail_box)

    # Підпис внизу
    frags.append(text(W / 2, H - 18,
                      "Мета: не найменший образ, а найменший образ, що досі ПРАЦЮЄ.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-21-4b-2-measure-verify.svg"), W, H, *frags,
           title=None)
    print("wrote fig-21-4b-2-measure-verify.svg")


if __name__ == "__main__":
    fig4b1_levers()
    fig4b2_measure_verify()
