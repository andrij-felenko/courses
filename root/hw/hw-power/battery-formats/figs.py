# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Декодування коду циліндричної комірки DDHHX ──────────────────────────
def fig_naming():
    W, H = 720, 300
    s = []
    # великий код зверху
    digits = ["1", "8", "6", "5", "0"]
    x0, gap, w = 150, 78, 60
    cy = 92
    for i, d in enumerate(digits):
        x = x0 + i * gap
        col = POS if i < 2 else (NEG if i < 4 else FIELD)
        s.append(rect(x, cy - 34, w, 68, fill="#ffffff", stroke=col, sw=2.4, rx=8))
        s.append(text(x + w / 2, cy + 20, d, size=44, color=col, bold=True))

    # підписи-скоби під групами
    def brace(xa, xb, y, label, sub, col):
        out = line(xa, y, xb, y, color=col, sw=2)
        out += line(xa, y, xa, y - 7, color=col, sw=2)
        out += line(xb, y, xb, y - 7, color=col, sw=2)
        out += text((xa + xb) / 2, y + 22, label, size=15, color=col, bold=True)
        out += text((xa + xb) / 2, y + 42, sub, size=13, color=MUTED)
        return out

    by = cy + 52
    s.append(brace(x0, x0 + w + gap, by, "діаметр", "18 мм", POS))
    s.append(brace(x0 + 2 * gap, x0 + 2 * gap + w + gap, by, "довжина", "65.0 мм", NEG))
    s.append(brace(x0 + 4 * gap, x0 + 4 * gap + w, by, "форма", "0 = циліндр", FIELD))

    # приклади праворуч не тиснуться — окремим рядком унизу
    s.append(text(W / 2, 250,
                  "21700 → 21 мм × 70.0 мм · 14500 → 14 мм × 50.0 мм · 26650 → 26 мм × 65.0 мм",
                  size=14, color=INK))
    s.append(text(W / 2, 274,
                  "довжина — у десятих міліметра (65 = 65.0 мм)",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, 'cylindrical-code.svg'), W, H, *s,
           title="Код циліндричної комірки: розміри просто в цифрах")


# ── 2. Три родини форматів поряд: циліндр / пакет / призма ───────────────────
def fig_families():
    W, H = 720, 360
    s = []
    colw = W / 3
    cx = [colw * 0.5, colw * 1.5, colw * 2.5]
    top = 70

    # 2a циліндр
    cyx = cx[0]
    s.append(rect(cyx - 26, top, 52, 130, fill=FILL, stroke=INK, sw=2, rx=14))
    s.append(rect(cyx - 12, top - 10, 24, 12, fill="#e8ecf0", stroke=INK, sw=2, rx=3))  # плюс-виступ
    s.append(plus(cyx, top - 4, r=6))
    s.append(text(cyx, top + 155, "Циліндр", size=16, bold=True))
    s.append(text(cyx, top + 176, "18650 · 21700", size=13, color=MUTED))

    # 2b пакет (pouch) — м'який плоский
    px = cx[1]
    s.append(rect(px - 40, top + 6, 80, 118, fill="#eef4ff", stroke=NEG, sw=2, rx=6))
    # виводи-язички
    s.append(rect(px - 20, top - 6, 12, 16, fill="#d7e2f7", stroke=NEG, sw=1.6, rx=2))
    s.append(rect(px + 8, top - 6, 12, 16, fill="#d7e2f7", stroke=NEG, sw=1.6, rx=2))
    s.append(text(px, top + 155, "Пакет", size=16, bold=True))
    s.append(text(px, top + 176, "LiPo, «пакетик»", size=13, color=MUTED))

    # 2c призма — твердий плоский корпус
    prx = cx[2]
    s.append(rect(prx - 34, top, 68, 124, fill="#eafaf0", stroke=FIELD, sw=2, rx=4))
    s.append(circle(prx - 16, top - 6, 5, fill="#ffffff", stroke=FIELD, sw=2))
    s.append(circle(prx + 16, top - 6, 5, fill="#ffffff", stroke=FIELD, sw=2))
    s.append(text(prx, top + 155, "Призма", size=16, bold=True))
    s.append(text(prx, top + 176, "твердий короб", size=13, color=MUTED))

    # рядок-порівняння знизу — три короткі тези
    ry = top + 210
    s.append(fitbox(cx[0] - colw / 2 + 14, ry, colw - 28, 78,
                    "міцний корпус\nтримає тиск сам\nгірше вкладається",
                    size=12.5, fill="#fdf0ee", stroke=POS))
    s.append(fitbox(cx[1] - colw / 2 + 14, ry, colw - 28, 78,
                    "легкий, тонкий\nформа будь-яка\nтреба захисту й\nкаркаса ззовні",
                    size=12.5, fill="#eef4ff", stroke=NEG))
    s.append(fitbox(cx[2] - colw / 2 + 14, ry, colw - 28, 78,
                    "щільно в ряд\nміцніший за пакет\nважчий корпус",
                    size=12.5, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, 'form-families.svg'), W, H, *s,
           title="Три формати одної хімії: як спакували, те й вирішує")


# ── 3. Код монетної комірки: хімія-літерою, розмір-числом ────────────────────
def fig_coin():
    W, H = 700, 290
    s = []
    # приклад CR2032 великими блоками
    parts = [("C", POS), ("R", NEG), ("20", FIELD), ("32", INK)]
    x0, cy = 150, 96
    x = x0
    widths = {"C": 56, "R": 56, "20": 82, "32": 82}
    positions = []
    for lab, col in parts:
        w = widths[lab]
        s.append(rect(x, cy - 34, w, 68, fill="#ffffff", stroke=col, sw=2.4, rx=8))
        s.append(text(x + w / 2, cy + 18, lab, size=40, color=col, bold=True))
        positions.append((x + w / 2, w))
        x += w + 16

    ly = cy + 60
    labels = [
        ("C", "хімія: літій", "(3 В)", POS),
        ("R", "форма: кругла", "", NEG),
        ("20", "Ø 20 мм", "", FIELD),
        ("32", "3.2 мм товщ.", "", INK),
    ]
    for (px, w), (lab, t1, t2, col) in zip(positions, labels):
        s.append(text(px, ly, t1, size=13.5, color=col, bold=True))
        if t2:
            s.append(text(px, ly + 19, t2, size=12.5, color=MUTED))

    # контраст із лужною
    s.append(line(60, 214, W - 60, 214, color="#dddddd", sw=1.4))
    s.append(text(W / 2, 240,
                  "Літера — хімія:  C → літій 3 В   ·   L → лужна 1.5 В   ·   S → срібло 1.55 В",
                  size=14, color=INK))
    s.append(text(W / 2, 264,
                  "тому CR2032 і LR44 — не про розмір, а насамперед про різну напругу",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, 'coin-code.svg'), W, H, *s,
           title="Код ґудзикової комірки: перша літера — це хімія")


# ── 4. Історична дуга 18650: від хімії до електромобіля (для hist-18650) ──────
def fig_hist_timeline():
    W, H = 760, 420
    s = []
    # вісь часу
    ax_y = 300
    x_l, x_r = 60, W - 60
    s.append(line(x_l, ax_y, x_r, ax_y, color=INK, sw=2.2))
    s.append(text(x_r, ax_y + 26, "час", size=13, color=MUTED, anchor="end", italic=True))

    # вузли: (рік-мітка, x-частка, підпис-зверху, підпис-знизу, колір, вгору?)
    nodes = [
        ("1970-ті", 0.04, "Уіттінгем", "перша\nлітієва комірка", MUTED, True),
        ("1980", 0.17, "Ґуденаф", "катод LiCoO₂", MUTED, False),
        ("1985", 0.30, "Йосіно", "вугільний анод →\nповна Li-ion", MUTED, True),
        ("1991", 0.45, "Sony CCD-TR1", "18650 у камкодері", POS, False),
        ("1990-ті", 0.60, "ноутбуки", "18650 стає\nтоварним стандартом", NEG, True),
        ("2008", 0.74, "Tesla Roadster", "6831 банка 18650", FIELD, False),
        ("2017", 0.86, "Model 3", "зсув на 21700", NEG, True),
        ("2020", 0.97, "Battery Day", "4680, без язичків", POS, False),
    ]
    for yr, fx, top, bot, col, up in nodes:
        x = x_l + fx * (x_r - x_l)
        s.append(circle(x, ax_y, 6, fill=col, stroke=col, sw=2))
        # рік — біля осі
        s.append(text(x, ax_y + (-14 if up else 22), yr, size=12.5, color=INK, bold=True))
        # виносна лінія + підпис далі від осі
        if up:
            s.append(line(x, ax_y - 26, x, ax_y - 58, color="#cccccc", sw=1.2))
            s.append(text(x, ax_y - 74, top, size=13, color=col, bold=True))
            for i, ln in enumerate(bot.split("\n")):
                s.append(text(x, ax_y - 56 + i * 16, ln, size=11.5, color=MUTED))
        else:
            s.append(line(x, ax_y + 34, x, ax_y + 62, color="#cccccc", sw=1.2))
            s.append(text(x, ax_y + 78, top, size=13, color=col, bold=True))
            for i, ln in enumerate(bot.split("\n")):
                s.append(text(x, ax_y + 96 + i * 16, ln, size=11.5, color=MUTED))

    # дужка «хімію винайшли троє» над першими трьома вузлами
    hx1 = x_l + 0.04 * (x_r - x_l)
    hx3 = x_l + 0.30 * (x_r - x_l)
    s.append(line(hx1, 150, hx3, 150, color=MUTED, sw=1.4, dash="4 3"))
    s.append(text((hx1 + hx3) / 2, 142, "хімія — троє незалежних кроків (Нобель-2019)",
                  size=12, color=MUTED, italic=True))

    # підпис-мораль унизу
    s.append(text(W / 2, H - 14,
                  "розмір 18×65 мм ніхто не «винайшов» — його усталили; далі індустрія переросла й його",
                  size=12.5, color=INK, italic=True))
    render(os.path.join(OUT, 'hist-18650-timeline.svg'), W, H, *s,
           title="Дуга формату 18650: хімія → камкодер → ноутбук → електромобіль")


if __name__ == '__main__':
    fig_naming()
    fig_families()
    fig_coin()
    fig_hist_timeline()
    print("figs done")
