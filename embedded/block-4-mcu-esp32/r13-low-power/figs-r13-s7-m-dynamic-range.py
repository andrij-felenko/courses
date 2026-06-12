# -*- coding: utf-8 -*-
"""
Фігура для вставки 🧮 «Динамічний діапазон вимірювання»
Розділ r13-low-power, тема 4.13.7, вставка m.

fig-4-13-7m-1-dynamic-range-ladder.svg — лінійка магнітуд струму (лог-вісь нА→А)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig1():
    W, H = 920, 500
    frags = []

    # ── Заголовок ───────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Лінійка магнітуд струму: нА → А (логарифмічна вісь)", size=15, bold=True))

    # ── Параметри логарифмічної осі ─────────────────────────────────────────────
    # Вісь: 10⁻⁹ (1 нА) → 10⁰ (1 А) — 9 порядків
    # Фізичний діапазон осі: x від AX0 до AX1
    AX0   = 60    # x-ліва межа (1 нА = 10⁻⁹)
    AX1   = 860   # x-права межа (1 А = 10⁰)
    AY    = 200   # y-рівень осі
    AXLEN = AX1 - AX0  # 800 px на 9 порядків → 88.9 px/порядок

    def log_x(amps):
        """Перетворити значення в амперах на x-координату осі."""
        import math
        # log10(1e-9)=-9, log10(1)=0 → нормуємо [-9, 0]
        frac = (math.log10(amps) - (-9)) / 9.0
        return AX0 + frac * AXLEN

    # ── Головна вісь (стрілка) ──────────────────────────────────────────────────
    frags.append(arrow(AX0 - 10, AY, AX1 + 18, AY, color=LINE, sw=2.0))

    # Мітки декад і вертикальні риски
    decades = [
        (1e-9,  "1 нА\n10⁻⁹"),
        (1e-8,  "10 нА\n10⁻⁸"),
        (1e-7,  "100 нА\n10⁻⁷"),
        (1e-6,  "1 мкА\n10⁻⁶"),
        (1e-5,  "10 мкА\n10⁻⁵"),
        (1e-4,  "100 мкА\n10⁻⁴"),
        (1e-3,  "1 мА\n10⁻³"),
        (1e-2,  "10 мА\n10⁻²"),
        (1e-1,  "100 мА\n10⁻¹"),
        (1e0,   "1 А\n10⁰"),
    ]
    for val, lbl in decades:
        xd = log_x(val)
        frags.append(line(xd, AY - 8, xd, AY + 8, color=LINE, sw=1.5))
        frags.append(mtext(xd, AY + 22, lbl, size=10, color=MUTED, anchor="middle"))

    # ── Смуги робочих станів вузла ──────────────────────────────────────────────
    # (y-розташування смуг — вище осі)
    STATES = [
        # (I_min, I_max, label_short, fill, stroke, label_y_rel)
        (10e-9,  10e-6,   "Deep-sleep\nRTC+ULP\n~10 нА–10 мкА",   "#dff5e8", FIELD,  -120),
        (0.1e-3, 1e-3,    "Light-sleep\n~0.1–1 мА",                "#e8f0ff", NEG,    -80),
        (20e-3,  40e-3,   "Modem-sleep /\nактивне ядро\n~20–40 мА","#f4f6f8", LINE,   -120),
        (80e-3,  100e-3,  "RX\n~80–100 мА",                        "#fff3cd", "#e0a020", -80),
        (300e-3, 500e-3,  "TX-сплеск\n~300–500 мА",                "#fdecea", POS,    -120),
    ]

    BAR_H = 20  # висота смуги стану

    for (imin, imax, lbl, fill, stroke, y_rel) in STATES:
        x1 = log_x(imin)
        x2 = log_x(imax)
        bw = max(x2 - x1, 6)
        by = AY - BAR_H / 2
        frags.append(rect(x1, by, bw, BAR_H, fill=fill, stroke=stroke, sw=1.8, rx=4))

        # Підпис через textbox — над смугою
        label_cy = AY + y_rel
        tb, tw, th = textbox((x1 + x2) / 2, label_cy, lbl, size=10,
                              fill=fill, stroke=stroke, sw=1.2, pad=5)
        frags.append(tb)

        # Вертикальна лінія від підпису до смуги
        mid_x = (x1 + x2) / 2
        line_y_top = label_cy + th / 2
        frags.append(line(mid_x, line_y_top, mid_x, by, color=stroke, sw=1.0, dash="3,2"))

    # ── Загальна дужка «повний розмах ≈ 7 порядків» ─────────────────────────────
    brace_y = AY + 65
    x_full_l = log_x(10e-9)
    x_full_r = log_x(500e-3)
    frags.append(line(x_full_l, brace_y - 6, x_full_l, brace_y + 6, color=INK, sw=1.5))
    frags.append(line(x_full_r, brace_y - 6, x_full_r, brace_y + 6, color=INK, sw=1.5))
    frags.append(line(x_full_l, brace_y, x_full_r, brace_y, color=INK, sw=1.5))
    brace_mid = (x_full_l + x_full_r) / 2
    tb2, _, _ = textbox(brace_mid, brace_y + 22, "повний розмах ≈ 7 порядків / ≈ 140 дБ",
                         size=11, bold=True, fill="#fffbe6", stroke="#c0a000", sw=1.5, pad=6)
    frags.append(tb2)

    # ── Вікно «один шунт + 12-бітний АЦП» (≈ 3 декади) — два положення ─────────
    WIN_W_DECADES = 2.1   # ширина вікна в порядках (~42 дБ, приклад з тексту)
    WIN_PX = WIN_W_DECADES / 9.0 * AXLEN

    WIN_Y  = AY - 75       # вертикальна смуга вікна (між смугами станів і підписами)
    WIN_H  = 26

    win_configs = [
        # (ліва межа вікна в А, підпис, offset_y для textbox)
        (10e-9,  "Вікно 1: дно сну\n(нА-сплеск не бачить)", -52),
        (20e-3,  "Вікно 2: пік передачі\n(нА-сон не бачить)", -52),
    ]

    for (i_left, lbl, wlbl_y_rel) in win_configs:
        wx1 = log_x(i_left)
        wx2 = wx1 + WIN_PX
        # напів-прозора жовта смуга
        frags.append(rect(wx1, WIN_Y - WIN_H / 2, WIN_PX, WIN_H,
                           fill="#fffacc", stroke="#d4a000", sw=2.0, rx=4))

        # мітки меж
        frags.append(line(wx1, WIN_Y - WIN_H, wx1, AY + 8, color="#d4a000", sw=1.0, dash="4,3"))
        frags.append(line(wx2, WIN_Y - WIN_H, wx2, AY + 8, color="#d4a000", sw=1.0, dash="4,3"))

        # підпис вікна
        wcx = (wx1 + wx2) / 2
        wlbl_cy = WIN_Y + wlbl_y_rel
        wtb, _, wth = textbox(wcx, wlbl_cy, lbl, size=9,
                               fill="#fffacc", stroke="#d4a000", sw=1.2, pad=4)
        frags.append(wtb)

    # Підпис "одне вікно ≈ 2–3 декади"
    win1_cx = log_x(10e-9) + WIN_PX / 2
    frags.append(text(win1_cx, WIN_Y + 18, "~2.1 порядку", size=9, color="#b08000", anchor="middle"))
    win2_cx = log_x(20e-3) + WIN_PX / 2
    frags.append(text(win2_cx, WIN_Y + 18, "~2.1 порядку", size=9, color="#b08000", anchor="middle"))

    # Стрілка "діра між вікнами"
    gap_l = log_x(10e-9) + WIN_PX + 4
    gap_r = log_x(50e-3) - 4
    gap_mid = (gap_l + gap_r) / 2
    gap_y   = WIN_Y
    if gap_r > gap_l + 10:
        frags.append(line(gap_l, gap_y, gap_r, gap_y, color=POS, sw=1.8, dash="5,3"))
        frags.append(text(gap_mid, gap_y - 12, "«діра» — невидима зона", size=9, color=POS, anchor="middle"))

    # ── Смуги автодіапазону (нижня частина) ─────────────────────────────────────
    AUTO_Y = AY + 115
    AUTO_H = 16

    auto_ranges = [
        (10e-9,  10e-6,   "нА-шунт (~2.5 порядки)",  "#dff5e8", FIELD),
        (5e-6,   5e-3,    "мкА-шунт (~3 порядки)",   "#e8f0ff", NEG),
        (2e-3,   100e-3,  "мА-шунт (~2 порядки)",    "#f4f6f8", LINE),
        (50e-3,  500e-3,  "А-шунт (~1 порядок)",     "#fdecea", POS),
    ]

    frags.append(text(AX0 + 20, AUTO_Y - 12, "Автодіапазон (4 шунти — разом ≈ 7 порядків):",
                       size=10, bold=True, color=INK, anchor="start"))

    for i, (imin, imax, lbl, fill, stroke) in enumerate(auto_ranges):
        ax1 = log_x(imin)
        ax2 = log_x(imax)
        aw  = max(ax2 - ax1, 8)
        ay  = AUTO_Y + i * (AUTO_H + 4)
        frags.append(rect(ax1, ay, aw, AUTO_H, fill=fill, stroke=stroke, sw=1.5, rx=3))
        tb_a, _, _ = textbox(ax1 + aw / 2, ay + AUTO_H / 2, lbl, size=9,
                              fill=fill, stroke=stroke, sw=0.8, pad=3)
        frags.append(tb_a)

    # ── Нижній підпис-висновок ───────────────────────────────────────────────────
    frags.append(text(W / 2, H - 12,
        "Одне фіксоване вікно (~2 порядки) не накриває розмах (~7 порядків) → потрібні автодіапазон або зовнішній АЦП",
        size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'fig-4-13-7m-1-dynamic-range-ladder.svg'), W, H, *frags)
    print("fig-4-13-7m-1-dynamic-range-ladder.svg — OK")


if __name__ == '__main__':
    fig1()
