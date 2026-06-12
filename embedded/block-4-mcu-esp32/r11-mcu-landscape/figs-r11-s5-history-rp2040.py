# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки «📜 Raspberry Pi: фундація, що зробила власний чип».
Тема 4.11.5, файл r11-s5-history-rp2040.md.
Нумерація фігур: Рис. 4.11.5i.k.

fig-r11-5i-1-foundation-to-chip.svg  — часова лінія: місія → рішення → чип
fig-r11-5i-2-borrowed-vs-built.svg   — що в RP2040 чуже, а що своє
fig-r11-5i-3-mission-loop.svg        — петля місії→чип→спільнота→місія

Запуск: python figs-r11-s5-history-rp2040.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.5i.1 — Від місії до власного кремнію (timeline)
# ══════════════════════════════════════════════════════════════════════════════
def fig1_foundation_to_chip():
    W, H = 900, 380
    frags = []

    frags.append(text(W / 2, 28, "Від освітньої місії до власного кремнію",
                      size=16, bold=True))
    frags.append(text(W / 2, 50,
                      "кожен щабель випливає з мети «навчити дітей кодувати», а не з ринкової гонки",
                      size=11, color=MUTED))

    stages = [
        ("2008–2009",
         "Raspberry Pi\nFoundation",
         "Освітня благодійна\nорганізація.\nМета: вчити дітей\nкодувати.",
         FILL, LINE),
        ("2012",
         "Одноплатний Pi\n+ Trading Ltd",
         "Перший RPi-комп'ютер.\nКомерційна «дочка»\nнаправляє прибуток\nна доброчинність.",
         "#e8f4f8", NEG),
        ("2019–2020",
         "Рішення: ВЛАСНИЙ\nчип (RP2040)",
         "Ліцензія Cortex-M0+\nчерез Arm Flexible Access.\nПроєктування в Кембриджі.\nFab: TSMC 40 нм.",
         "#eef6ee", FIELD),
        ("21.01.2021",
         "RP2040 + Pico\n(у дефіцит чипів!)",
         "Чип ~$1 у партії.\nPlate Pico = $4.\nЧип відкрито\nпродають конкурентам.",
         "#fff8e6", POS),
    ]

    margin = 44
    gap = 24
    n = len(stages)
    total_w = W - 2 * margin
    box_w = (total_w - gap * (n - 1)) / n
    box_h = 150
    top_y = 72

    for i, (yr, title, desc, fill, stroke) in enumerate(stages):
        cx = margin + i * (box_w + gap) + box_w / 2
        cy = top_y + box_h / 2

        frags.append(fitbox(cx - box_w / 2, top_y, box_w, box_h,
                            title, size=12, pad=8, fill=fill, stroke=stroke, sw=2, rx=8,
                            bold=True, color=INK))

        frags.append(text(cx, top_y - 11, yr, size=10, color=MUTED))

        desc_lines = desc.split("\n")
        desc_y = top_y + box_h + 20
        for j, dl in enumerate(desc_lines):
            frags.append(text(cx, desc_y + j * 14, dl, size=10, color=INK))

        if i < n - 1:
            ax1 = cx + box_w / 2
            ax2 = ax1 + gap
            frags.append(arrow(ax1, cy, ax2 - 5, cy, color=LINE, sw=2))

    # Нитка-теза внизу
    thread_y = H - 26
    frags.append(line(margin, thread_y, W - margin, thread_y, color=FIELD, sw=2, dash="8 4"))
    tb, _, _ = textbox(W / 2, H - 10,
                       "наскрізна нитка: освітня мета визначає кожне рішення — від назви до відсутнього флешу",
                       size=11, pad=7, fill="#f0faf0", stroke=FIELD, color=FIELD, sw=1.5)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r11-5i-1-foundation-to-chip.svg"),
           W, H, *frags,
           title=None)
    print("wrote fig-r11-5i-1-foundation-to-chip.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.5i.2 — Що в RP2040 чуже, а що своє (дві колонки)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_borrowed_vs_built():
    W, H = 800, 380
    frags = []

    frags.append(text(W / 2, 28, "RP2040: чесна атрибуція — що чуже і що своє",
                      size=16, bold=True))
    frags.append(text(W / 2, 50,
                      "Raspberry Pi не винаходила процесор — але додала власну обв'язку й PIO",
                      size=11, color=MUTED))

    mid = W / 2
    col_l = mid / 2
    col_r = mid + mid / 2
    top = 70
    col_w = 310
    item_h = 44
    pad_x = 20
    gap_y = 10

    # ── Ліворуч: «ліцензоване / чуже» ─────────────────────────────────────────
    tb_l, _, _ = textbox(col_l, top + 20, "Ліцензоване / чуже",
                         size=14, pad=10, fill="#fdecea", stroke=POS, sw=2, bold=True, color=POS)
    frags.append(tb_l)

    left_items = [
        "Ядро: ARM Cortex-M0+ (ARMv6-M)",
        "Базовий Cortex-M RTL від ARM",
        "Доступ: Arm Flexible Access",
        "Виробництво: TSMC 40 нм",
    ]
    item_y = top + 58
    for item in left_items:
        frags.append(fitbox(col_l - col_w / 2, item_y, col_w, item_h,
                            item, size=12, pad=8, fill="#fff0f0", stroke=POS, sw=1, rx=6))
        item_y += item_h + gap_y

    # ── Роздільник ─────────────────────────────────────────────────────────────
    frags.append(line(mid, top, mid, H - 60, color=MUTED, sw=1, dash="5 5"))
    tb_vs, _, _ = textbox(mid, top + 20, "vs", size=14, pad=6,
                          fill=BG, stroke=MUTED, sw=1.2, color=MUTED)
    frags.append(tb_vs)

    # ── Праворуч: «своє / внесок» ──────────────────────────────────────────────
    tb_r, _, _ = textbox(col_r, top + 20, "Власний внесок Raspberry Pi",
                         size=14, pad=10, fill="#eaf0fd", stroke=NEG, sw=2, bold=True, color=NEG)
    frags.append(tb_r)

    right_items = [
        "Компонування SoC (peripherals, bus)",
        "264 КБ SRAM — внутрішня",
        "Зовнішній QSPI-Flash (навмисно!)",
        "PIO — Programmable I/O (патент-pending)",
    ]
    item_y2 = top + 58
    for j, item in enumerate(right_items):
        # PIO — виділити яскравіше
        clr = FIELD if j == 3 else "#eaf4ff"
        strk = FIELD if j == 3 else NEG
        frags.append(fitbox(col_r - col_w / 2, item_y2, col_w, item_h,
                            item, size=12, pad=8, fill=clr, stroke=strk, sw=(2 if j == 3 else 1), rx=6))
        item_y2 += item_h + gap_y

    # Висновок внизу
    concl_y = H - 32
    frags.append(line(44, concl_y - 16, W - 44, concl_y - 16, color=MUTED, sw=1, dash="4 4"))
    tb_c, _, _ = textbox(W / 2, concl_y,
                         "Raspberry Pi НЕ «винайшла процесор» — взяла ліцензоване ядро і додала власну обв'язку та PIO",
                         size=11, pad=8, fill="#f0faf0", stroke=FIELD, sw=1.5, color=FIELD)
    frags.append(tb_c)

    render(os.path.join(OUT, "fig-r11-5i-2-borrowed-vs-built.svg"),
           W, H, *frags)
    print("wrote fig-r11-5i-2-borrowed-vs-built.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.5i.3 — Петля місії→чип→спільнота→місія
# ══════════════════════════════════════════════════════════════════════════════
def fig3_mission_loop():
    W, H = 720, 420
    frags = []

    frags.append(text(W / 2, 28, "Петля, де чип служить місії",
                      size=16, bold=True))
    frags.append(text(W / 2, 50,
                      "чому продати власний чип конкурентам — для charity раціонально",
                      size=11, color=MUTED))

    # Чотири вузли по колу (центр W/2, H/2+10)
    import math
    cx0, cy0 = W / 2, H / 2 + 20
    R = 130  # радіус кола вузлів
    nodes = [
        # (кут у градусах, label, color, stroke_color)
        (90,  "Освітня мета\nфундації", "#eef6ee", FIELD),
        (0,   "Дешевий відкритий\nчип RP2040 (~$1)", "#e8f4f8", NEG),
        (270, "Виробники плат\n(Adafruit, Arduino,\nPimoroni, SparkFun…)", "#fff8e6", POS),
        (180, "Прибуток → фундація\n+ ширша спільнота\n+ більше новачків", FILL, LINE),
    ]

    node_w, node_h = 160, 70
    node_centers = []
    for deg, lbl, fill, strk in nodes:
        rad = math.radians(deg)
        nx = cx0 + R * math.cos(rad)
        ny = cy0 - R * math.sin(rad)
        node_centers.append((nx, ny))
        frags.append(fitbox(nx - node_w / 2, ny - node_h / 2, node_w, node_h,
                            lbl, size=11, pad=8, fill=fill, stroke=strk, sw=2, rx=10))

    # Стрілки між вузлами (по колу за годинниковою стрілкою: 0→3→2→1→0)
    order = [0, 3, 2, 1, 0]  # індекси: 90°→180°→270°→0°→90°
    arrow_labels = [
        "фінансує відкриту\nрозробку чипа",
        "відкритий продаж\nчипа конкурентам",
        "ширша екосистема\n→ більше навчання",
        "прибуток компанії\n→ фінансує місію",
    ]
    for k in range(4):
        i1 = order[k]
        i2 = order[k + 1]
        x1, y1 = node_centers[i1]
        x2, y2 = node_centers[i2]
        # Вкоротити стрілку до краю рамки
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        shrink = 48
        sx1 = x1 + dx / dist * shrink
        sy1 = y1 + dy / dist * shrink
        sx2 = x2 - dx / dist * (shrink + 6)
        sy2 = y2 - dy / dist * (shrink + 6)
        frags.append(arrow(sx1, sy1, sx2, sy2, color=LINE, sw=1.8))

        # Підпис стрілки
        lx = (sx1 + sx2) / 2
        ly = (sy1 + sy2) / 2
        lbl_lines = arrow_labels[k].split("\n")
        for m, ll in enumerate(lbl_lines):
            frags.append(text(lx, ly - 8 + m * 13, ll, size=9, color=MUTED))

    # Центральний підпис
    tb_c, _, _ = textbox(cx0, cy0, "Замкнений\nмаховик", size=12, pad=10,
                         fill="#f0f8ff", stroke=NEG, sw=1.5, color=NEG, bold=True)
    frags.append(tb_c)

    render(os.path.join(OUT, "fig-r11-5i-3-mission-loop.svg"),
           W, H, *frags)
    print("wrote fig-r11-5i-3-mission-loop.svg")


if __name__ == "__main__":
    fig1_foundation_to_chip()
    fig2_borrowed_vs_built()
    fig3_mission_loop()
    print("Done.")
