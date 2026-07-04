# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «HC-SR501 — PIR-давач руху».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Диференційний принцип: два електроди + сегментна лінза бачать РУХ ───────
def fig_principle():
    W, H = 820, 470
    f = [text(W / 2, 30, "Чому давач бачить РУХ, а не тепло: два електроди + сегментна лінза",
              size=15, bold=True)]

    # лінза-бані ліворуч, промені збираються на елемент
    lens_x, lens_y = 150, 235
    f.append('<path d="M %.1f %.1f a 46 90 0 0 1 0 180" fill="#eef6ef" '
             'stroke="%s" stroke-width="1.8"/>' % (lens_x, lens_y - 90, FIELD))
    f.append(text(lens_x - 8, lens_y - 105, "лінза Френеля", size=11, bold=True, color=FIELD, anchor="middle"))
    f.append(text(lens_x - 8, lens_y + 118, "(багато секцій-зон)", size=10, color=MUTED, anchor="middle"))
    # сегменти лінзи — короткі риски
    for k in range(-4, 5):
        yy = lens_y + k * 20
        f.append(line(lens_x - 6, yy, lens_x + 8, yy, color=FIELD, sw=1.0))

    # два електроди-квадратики (елемент) праворуч від лінзи
    ex = 300
    f.append(rect(ex, lens_y - 34, 30, 30, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(ex + 15, lens_y - 15, "A", size=13, bold=True, color=POS))
    f.append(rect(ex, lens_y + 6, 30, 30, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(ex + 15, lens_y + 27, "B", size=13, bold=True, color=NEG))
    f.append(text(ex + 15, lens_y + 62, "піроелемент", size=10.5, bold=True))
    f.append(text(ex + 15, lens_y + 78, "(2 половини)", size=9.5, color=MUTED))

    # тепла людина, що йде — три позиції, стрілка руху
    for i, hx in enumerate((560, 640, 720)):
        col = "#e07b39"
        f.append(circle(hx, lens_y - 40, 12, fill=col, stroke="#a95a20", sw=1.4))
        f.append(rect(hx - 9, lens_y - 24, 18, 40, fill=col, stroke="#a95a20", sw=1.4, rx=5))
        if i < 2:
            f.append(text(hx + 40, lens_y - 34, "→", size=20, color=INK))
    f.append(text(640, lens_y - 70, "тепле тіло рухається", size=11, bold=True, color="#a95a20"))

    # промінь від тіла крізь лінзу на елемент (пунктир)
    f.append(line(560, lens_y - 10, lens_x + 8, lens_y - 4, color="#e07b39", sw=1.2, dash="4,3"))
    f.append(line(lens_x - 4, lens_y, ex, lens_y - 18, color="#e07b39", sw=1.2, dash="4,3"))

    # нижня смуга: що дає рух
    b, _, _ = textbox(W / 2, 415,
                      "коли тіло переходить із зони в зону, тепло падає то на A, то на B — і між ними\n"
                      "виникає РІЗНИЦЯ сигналу; рівне нерухоме тепло гріє обидві половини однаково → нуль",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "principle.svg"), W, H, *f)


# ── 2. Будова модуля: елемент → BISS0001 → регулятор 3.3 В → OUT ──────────────
def fig_board():
    W, H = 880, 430
    f = [text(W / 2, 28, "Що на платі HC-SR501: піроелемент → BISS0001 → вихід 3.3 В",
              size=15, bold=True)]

    y = 150
    bh = 90

    def blk(x, w, title, sub, fill, stroke):
        f.append(rect(x, y, w, bh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        f.append(text(x + w / 2, y + bh / 2 - 6, title, size=12.5, bold=True))
        f.append(text(x + w / 2, y + bh / 2 + 14, sub, size=10, color=MUTED))

    # елемент
    blk(60, 150, "піроелемент", "2 половини A/B", "#fdf0ee", POS)
    # BISS0001
    blk(300, 200, "BISS0001", "підсилення + логіка", "#eef6ef", FIELD)
    # вихід
    blk(600, 120, "OUT", "3.3 В TTL", "#eaf0fd", NEG)

    # стрілки між блоками
    f.append(arrow(210, y + bh / 2, 298, y + bh / 2, color=INK, sw=2.0))
    f.append(mtext(254, y + bh / 2 - 18, ["слабкий", "сигнал"], size=9, color=MUTED))
    f.append(arrow(500, y + bh / 2, 598, y + bh / 2, color=INK, sw=2.0))
    f.append(text(549, y + bh / 2 - 10, "0/1", size=10, color=INK))

    # живлення знизу: VCC 4.5-20 → регулятор 3.3 → BISS
    ry = y + bh + 60
    f.append(rect(300, ry, 200, 46, fill="#fff6e6", stroke="#c8901f", sw=1.6, rx=8))
    f.append(text(400, ry + 20, "регулятор 3.3 В", size=11, bold=True, color="#8a6410"))
    f.append(text(400, ry + 37, "на платі", size=9.5, color=MUTED))
    # VCC вхід
    f.append(text(150, ry + 26, "VCC 4.5–20 В", size=11.5, bold=True, color=POS, anchor="middle"))
    f.append(arrow(232, ry + 22, 298, ry + 22, color=POS, sw=1.8))
    # регулятор живить BISS (стрілка вгору)
    f.append(arrow(400, ry, 400, y + bh + 4, color="#c8901f", sw=1.8))
    f.append(text(430, ry - 10, "3.3 В на чип", size=9.5, color="#8a6410", anchor="start"))

    # два підстроювачі + перемичка — коротко позначені над BISS
    f.append(circle(330, y - 22, 9, fill="#f2f2f2", stroke=INK, sw=1.4))
    f.append(text(330, y - 34, "Sx", size=9.5, bold=True))
    f.append(circle(400, y - 22, 9, fill="#f2f2f2", stroke=INK, sw=1.4))
    f.append(text(400, y - 34, "Tx", size=9.5, bold=True))
    f.append(rect(452, y - 30, 26, 16, fill="#f2f2f2", stroke=INK, sw=1.2, rx=3))
    f.append(text(465, y - 18, "H/L", size=9, bold=True))
    f.append(text(400, y - 48, "два підстроювачі (чутливість Sx, час Tx) і перемичка режиму", size=9.5, color=MUTED))

    render(os.path.join(IMG, "board.svg"), W, H, *f)


# ── 3. Підключення до МК: три дроти, вихід 3.3 В прямо в цифровий вхід ─────────
def fig_wiring():
    W, H = 820, 430
    f = [text(W / 2, 28, "Підключення: три дроти; вихід 3.3 В читаємо як цифровий вхід",
              size=15, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 90, 120, 200, 190
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "HC-SR501", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 46, "(бані догори)", size=9.5, color=MUTED))
    # три піни знизу модуля
    pins = [("VCC", POS, "#fdecea"), ("OUT", NEG, "#eaf0fd"), ("GND", INK, "#f2f2f2")]
    for i, (nm, col, fl) in enumerate(pins):
        px = mx + 40 + i * 60
        f.append(rect(px - 16, my + mh - 4, 32, 22, fill=fl, stroke=col, sw=1.4, rx=3))
        f.append(text(px, my + mh + 11, nm, size=10, bold=True, color=col))

    # МК праворуч
    cx, cy, cw, ch = 540, 130, 190, 170
    f.append(rect(cx, cy, cw, ch, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(cx + cw / 2, cy + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(cx + cw / 2, cy + 44, "(Arduino / ESP32 …)", size=9.5, color=MUTED))
    cpins = [("5 В", POS), ("GPIO", NEG), ("GND", INK)]
    for i, (nm, col) in enumerate(cpins):
        py = cy + 70 + i * 34
        f.append(rect(cx - 4, py - 12, 8, 22, fill="#fff", stroke=col, sw=1.4, rx=2))
        f.append(text(cx - 40, py + 4, nm, size=10, bold=True, color=col, anchor="middle"))

    # дроти: VCC-5В, OUT-GPIO, GND-GND
    vx = mx + 40
    ox = mx + 100
    gx = mx + 160
    ylow = my + mh + 40
    # VCC → 5 В
    f.append(line(vx, my + mh + 18, vx, ylow, color=POS, sw=1.8))
    f.append(line(vx, ylow, cx - 4, cy + 70, color=POS, sw=1.8))
    # OUT → GPIO
    f.append(line(ox, my + mh + 18, ox, ylow + 22, color=NEG, sw=1.8))
    f.append(line(ox, ylow + 22, cx - 4, cy + 104, color=NEG, sw=1.8))
    # GND → GND
    f.append(line(gx, my + mh + 18, gx, ylow + 44, color=INK, sw=1.8))
    f.append(line(gx, ylow + 44, cx - 4, cy + 138, color=INK, sw=1.8))

    # приписка про рівень
    b, _, _ = textbox(W / 2, 400,
                      "живимо 5 В на VCC; вихід дає лише 3.3 В — цього досить для «1» на 5-В МК,\n"
                      "тож OUT іде прямо в GPIO без подільника; резистор підтяжки не потрібен",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Режим перемички: H (повторний) проти L (одиночний) на осі часу ─────────
def fig_retrigger():
    W, H = 840, 460
    f = [text(W / 2, 28, "Перемичка H проти L: що робить вихід, коли рух триває",
              size=15, bold=True)]

    x0, x1 = 90, 760
    # шкала руху зверху: три поштовхи руху
    my = 80
    f.append(text(x0 - 20, my - 14, "рух:", size=11, bold=True, anchor="start"))
    moves = [(140, 200), (280, 320), (360, 400)]
    for a, b in moves:
        f.append(rect(a, my, b - a, 20, fill="#e07b39", stroke="#a95a20", sw=1.2, rx=3))
    f.append(text((moves[1][0] + moves[2][1]) / 2, my - 8,
                  "рух не припиняється", size=9.5, color="#a95a20"))

    def axis(y, l1, l2, col):
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.0))
        f.append(mtext(x0 - 22, y - 4, [l1, l2], size=10.5, color=col, anchor="end", bold=True))

    # ── H: повторний — timer перезапускається щоразу, вихід тримається ─────────
    yH = 175
    axis(yH, "H", "(повтор)", FIELD)
    # OUT стрибає на першому русі й тримається до Tx ПІСЛЯ останнього руху
    hi = yH - 46
    hstart = moves[0][0]
    hend = moves[2][1] + 150   # Tx після останнього поштовху
    f.append(line(hstart, yH, hstart, hi, color=FIELD, sw=2.2))
    f.append(line(hstart, hi, hend, hi, color=FIELD, sw=2.2))
    f.append(line(hend, hi, hend, yH, color=FIELD, sw=2.2))
    f.append(text((hstart + hend) / 2, hi - 8, "вихід тримається весь час руху + Tx після",
                  size=10, bold=True, color=FIELD))
    f.append(line(moves[2][1], yH, moves[2][1], hi, color=MUTED, sw=0.8, dash="3,3"))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="9" fill="%s" text-anchor="middle">'
             'Tx</text>' % ((moves[2][1] + hend) / 2, hi + 14, FONT, MUTED))

    # ── L: одиночний — вихід гасне через Tx ПІСЛЯ ПЕРШОГО руху, решту ігнорує ──
    yL = 320
    axis(yL, "L", "(одиночн.)", NEG)
    lo = yL - 46
    lstart = moves[0][0]
    lend = moves[0][0] + 150   # Tx після ПЕРШОГО поштовху
    f.append(line(lstart, yL, lstart, lo, color=NEG, sw=2.2))
    f.append(line(lstart, lo, lend, lo, color=NEG, sw=2.2))
    f.append(line(lend, lo, lend, yL, color=NEG, sw=2.2))
    f.append(text((lstart + lend) / 2, lo - 8, "тільки Tx від ПЕРШОГО, далі ігнор",
                  size=10, bold=True, color=NEG))
    # блок-час після падіння
    f.append(rect(lend, yL, 42, 8, fill="#eee", stroke=MUTED, sw=1.0, rx=2))
    f.append(text(lend + 60, yL + 6, "≈2.5 с блок", size=9, color=MUTED, anchor="start"))
    # пізніші поштовхи руху не дають нічого (перекреслені)
    for a, b in moves[1:]:
        f.append(line((a + b) / 2 - 8, yL - 12, (a + b) / 2 + 8, yL, color=MUTED, sw=1.2))

    b, _, _ = textbox(W / 2, 420,
                      "H: доки в кадрі є рух — вихід «1»; відлік Tx стартує від ОСТАННЬОГО руху (для присутності).\n"
                      "L: «1» рівно на Tx від ПЕРШОГО руху, рух під час Tx не подовжує (для одного спрацювання).",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "retrigger.svg"), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_board()
    fig_wiring()
    fig_retrigger()
    print("OK: 4 figures ->", IMG)
