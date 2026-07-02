# -*- coding: utf-8 -*-
"""Фігури до теми «Суматор із прискореним переносом».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_ripple_vs_ahead():
    """Головний контраст: ланцюговий перенос біжить розряд за розрядом (послідовно),
    а прискорений — усі переноси рахуються водночас прямо зі входів."""
    W, H = 760, 430
    f = []
    # --- Верх: ланцюговий (серійний) ---
    f.append(text(W / 2, 30, "Ланцюговий перенос: одне за одним", size=15, bold=True, color=POS))
    n = 4
    bx0, bw, gap, by, bh = 120, 96, 40, 56, 56
    for i in range(n):
        x = bx0 + (n - 1 - i) * (bw + gap)
        f.append(fitbox(x, by, bw, bh, "ПС%d" % i, size=14, fill="#fdecea", stroke=POS, bold=True))
    # перенос біжить справа наліво (від молодшого до старшого)
    for i in range(n - 1):
        xr = bx0 + (n - 1 - i) * (bw + gap)            # лівий край молодшого
        xl = bx0 + (n - 2 - i) * (bw + gap) + bw       # правий край старшого
        ymid = by + bh / 2
        f.append(arrow(xr, ymid, xl, ymid, color=POS, sw=2.2))
    f.append(text(bx0 + 3 * (bw + gap) + bw / 2, by - 8, "старший", size=11, color=MUTED))
    f.append(text(bx0 + bw / 2, by - 8, "молодший", size=11, color=MUTED))
    f.append(text(W / 2, by + bh + 26,
                  "кожен перенос ЧЕКАЄ на попередній → час росте з кількістю розрядів",
                  size=12, color=MUTED))

    # --- Низ: прискорений (паралельний) ---
    yb = 250
    f.append(text(W / 2, yb - 16, "Прискорений перенос: усі водночас", size=15, bold=True, color=FIELD))
    # блок логіки переносу, що дивиться на всі входи одразу
    lk_x, lk_y, lk_w, lk_h = 250, yb + 8, 260, 52
    f.append(fitbox(lk_x, lk_y, lk_w, lk_h, "логіка прискорення\n(дивиться на ВСІ входи)",
                    size=13, fill="#eafaf1", stroke=FIELD, bold=True))
    # стрілки вгору до кожного суматора
    for i in range(n):
        x = bx0 + (n - 1 - i) * (bw + gap) + bw / 2
        f.append(arrow(lk_x + lk_w / 2, lk_y, x, yb + 92, color=FIELD, sw=1.8))
    for i in range(n):
        x = bx0 + (n - 1 - i) * (bw + gap)
        f.append(fitbox(x, yb + 92, bw, bh, "ПС%d" % i, size=14, fill="#eafaf1", stroke=FIELD, bold=True))
    f.append(text(W / 2, yb + 92 + bh + 24,
                  "перенос кожного розряду готовий одразу → час майже НЕ залежить від ширини",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'ripple-vs-ahead.svg'), W, H, *f)


def fig_gpk():
    """Що пара бітів робить із переносом: породжує (generate), пропускає (propagate),
    гасить (kill). Таблиця на чотири рядки — серце всієї ідеї."""
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 30, "Що пара бітів (aᵢ, bᵢ) робить із переносом", size=16, bold=True))

    cols = [(110, "aᵢ"), (190, "bᵢ"), (300, "Cout"), (470, "роль")]
    y0 = 70
    for x, cap in cols:
        f.append(text(x, y0, cap, size=13, bold=True, color=MUTED))
    f.append(line(80, y0 + 10, W - 60, y0 + 10, color=MUTED, sw=1))

    rows = [
        ("0", "0", "0", "гасить (kill): нуль на виході, хай що прийшло", NEG),
        ("0", "1", "Cin", "пропускає (propagate): перенос проходить наскрізь", "#b8860b"),
        ("1", "0", "Cin", "пропускає (propagate): перенос проходить наскрізь", "#b8860b"),
        ("1", "1", "1", "породжує (generate): одиниця сама, без жодного входу", POS),
    ]
    y = y0 + 42
    for a, b, co, role, c in rows:
        f.append(text(110, y, a, size=14))
        f.append(text(190, y, b, size=14))
        f.append(text(300, y, co, size=14, bold=True, color=c))
        f.append(text(470, y, role, size=12.5, color=c, anchor="middle"))
        y += 42
    f.append(line(80, y - 18, W - 60, y - 18, color="#e5e7eb", sw=1))

    # підсумкові формули
    box = fitbox(150, y + 6, 440, 64,
                 "Gᵢ = aᵢ · bᵢ   (породжує)\nPᵢ = aᵢ ⊕ bᵢ   (пропускає)",
                 size=14, fill=FILL, stroke=LINE, bold=True)
    f.append(box)
    render(os.path.join(OUT, 'generate-propagate-kill.svg'), W, H, *f)


def fig_blocks():
    """Ієрархія: 16 бітів ділять на 4 групи по 4 розряди; кожна група віддає
    свої груповий G* і P*, а другий рівень прискорення роздає переноси між групами."""
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 30, "Блоковий (ярусний) прискорений перенос", size=16, bold=True))

    # верхній рівень — міжгруповий блок прискорення
    top_x, top_y, top_w, top_h = 190, 70, 380, 50
    f.append(fitbox(top_x, top_y, top_w, top_h,
                    "міжгруповий блок прискорення (працює з G*, P* груп)",
                    size=13, fill="#eafaf1", stroke=FIELD, bold=True))

    # чотири групи по 4 біти
    gx0, gw, gap, gy, gh = 110, 130, 30, 210, 70
    labels = ["біти 0–3", "біти 4–7", "біти 8–11", "біти 12–15"]
    for i in range(4):
        x = gx0 + i * (gw + gap)
        f.append(fitbox(x, gy, gw, gh, "група\n%s" % labels[i], size=12.5,
                        fill="#eef4ff", stroke=NEG, bold=True))
        cx = x + gw / 2
        # вниз: переноси-входи від верхнього рівня (зелені)
        f.append(arrow(top_x + top_w / 2 - 120 + i * 80, top_y + top_h, cx - 18, gy, color=FIELD, sw=1.7))
        # вгору: груповий G*/P* (сині)
        f.append(arrow(cx + 18, gy, top_x + top_w / 2 - 120 + i * 80, top_y + top_h, color=NEG, sw=1.7))

    f.append(text(150, gy + gh + 30, "↑ кожна група віддає свої G*, P*", size=12, color=NEG, anchor="start"))
    f.append(text(W - 150, gy + gh + 30, "↓ і одержує готовий перенос-вхід", size=12, color=FIELD, anchor="end"))
    f.append(text(W / 2, gy + gh + 58,
                  "глибина росте як log від ширини, а не лінійно — ось де виграш на широких словах",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'block-lookahead.svg'), W, H, *f)


def fig_history():
    """Історична нитка ідеї «не чекати перенос, а порахувати наперед»:
    Беббідж (замисел) → Цузе (перша робоча реалізація в двійковому комп'ютері)
    → NBS / Вайнберґер-Сміт (перша чітка логіка G/P на електроніці) → префіксні
    суматори в процесорах. Показує, що ідея старша за «IBM 1958»."""
    W, H = 780, 340
    f = []
    f.append(text(W / 2, 30, "Хто вчив машину не чекати на перенос", size=16, bold=True))

    # горизонтальна вісь часу
    axis_y = 150
    f.append(line(70, axis_y, W - 40, axis_y, color=MUTED, sw=2))

    # чотири віхи: (x, рік, хто, що саме, підпис зверху чи знизу)
    marks = [
        (150, "1837", "Чарлз Беббідж", "«передбачлива тяга»\nу задуманій\nаналітичній машині", True, NEG),
        (330, "1936–41", "Конрад Цузе\n(Z1, Z3)", "перша РОБОЧА\nреалізація в\nдвійковому комп'ютері", False, FIELD),
        (520, "1956", "Вайнберґер і Сміт\n(NBS, не IBM)", "чітка логіка G/P;\n53 біти за 1 мкс;\nпатент США, уряд", True, POS),
        (690, "1958→", "IBM та інші", "класика арифметики;\nпрефіксні суматори\nв ядрах донині", False, NEG),
    ]
    for x, year, who, what, above, c in marks:
        f.append(circle(x, axis_y, 7, fill="#ffffff", stroke=c, sw=3))
        f.append(text(x, axis_y - 14 if above else axis_y + 24, year, size=13, bold=True, color=c))
        if above:
            f.append(fitbox(x - 82, axis_y - 118, 164, 44, who, size=12.5, fill=FILL, stroke=c, bold=True))
            f.append(mtext(x, axis_y - 66, what, size=11, color=MUTED, lh=1.25))
        else:
            f.append(fitbox(x - 82, axis_y + 40, 164, 44, who, size=12.5, fill=FILL, stroke=c, bold=True))
            f.append(mtext(x, axis_y + 100, what, size=11, color=MUTED, lh=1.25))

    render(os.path.join(OUT, 'history-timeline.svg'), W, H, *f)


if __name__ == "__main__":
    fig_ripple_vs_ahead()
    fig_gpk()
    fig_blocks()
    fig_history()
    print("OK: figures written to", OUT)
