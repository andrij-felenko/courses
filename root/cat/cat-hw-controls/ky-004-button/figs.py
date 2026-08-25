# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-004 — тактильна кнопка на платі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def button_symbol(f, x, y, col=INK):
    """Символ момент-кнопки (два контакти + рухома перемичка над ними).
    (x,y) — лівий контакт; повертає координату правого контакту."""
    gap = 40
    rx = x + gap
    # два контакти-стовпчики
    f.append(line(x, y - 8, x, y + 8, color=col, sw=2.0))
    f.append(line(rx, y - 8, rx, y + 8, color=col, sw=2.0))
    # рухома перемичка (нахилена — «розімкнено»)
    f.append(line(x - 4, y - 8, rx + 8, y - 20, color=col, sw=2.2))
    # штовхач
    f.append(line((x + rx) / 2, y - 16, (x + rx) / 2, y - 30, color=col, sw=1.6))
    f.append(rect((x + rx) / 2 - 9, y - 38, 18, 8, fill=FILL, stroke=col, sw=1.6, rx=2))
    return rx


def resistor_symbol(f, x, y1, y2, label, col=INK):
    """Вертикальний резистор між y1 (верх) і y2 (низ) на координаті x."""
    bx = 14
    f.append(line(x, y1, x, y1 + 10, color=col, sw=1.6))
    f.append(rect(x - bx, y1 + 10, 2 * bx, (y2 - y1) - 20, fill=BG, stroke=col, sw=1.6, rx=3))
    f.append(line(x, y2 - 10, x, y2, color=col, sw=1.6))
    f.append(text(x + bx + 6, (y1 + y2) / 2 - 4, label, size=11, bold=True, color=col, anchor="start"))
    f.append(text(x + bx + 6, (y1 + y2) / 2 + 11, "10 кОм", size=9, color=MUTED, anchor="start"))


# ── 1. Дві схеми KY-004: pull-down (класика) і pull-up (клони) ────────────────────
def fig_schematic():
    W, H = 940, 560
    f = [text(W / 2, 28, "Одна назва — дві схеми: куди підтягує єдиний резистор, така й полярність",
              size=15, bold=True)]

    def scene(ox, title, tcol, pull_down):
        """Малює одну плату в рамці, ліва межа ox. Ширина сцени ~ 380."""
        bx, by, bw, bh = ox, 66, 380, 400
        f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
        f.append(text(bx + bw / 2, by + 26, title, size=13, bold=True, color=tcol))

        vcc_y = by + 66
        gnd_y = by + bh - 44
        vcc_x0, vcc_x1 = bx + 40, bx + bw - 40
        # шини живлення й землі
        f.append(line(vcc_x0, vcc_y, vcc_x1, vcc_y, color=POS, sw=2.2))
        f.append(text(vcc_x0, vcc_y - 10, "+  (VCC 3.3–5 В)", size=11, bold=True, color=POS, anchor="start"))
        f.append(line(vcc_x0, gnd_y, vcc_x1, gnd_y, color=NEG, sw=2.2))
        f.append(text(vcc_x0, gnd_y + 22, "−  (GND)", size=11, bold=True, color=NEG, anchor="start"))

        # вузол S — на середній горизонталі, ближче до правого краю
        node_x = bx + bw - 70
        node_y = (vcc_y + gnd_y) / 2
        # вивід S праворуч
        f.append(line(node_x, node_y, bx + bw - 30, node_y, color=FIELD, sw=2.0))
        f.append(circle(bx + bw - 30, node_y, 5, fill=BG, stroke=FIELD, sw=2))
        f.append(text(bx + bw - 24, node_y - 9, "S", size=13, bold=True, color=FIELD, anchor="start"))
        f.append(circle(node_x, node_y, 3.4, fill=INK, stroke=INK, sw=1))

        # кнопка й резистор — ліворуч від вузла, у стовпчик
        btn_x = bx + 70
        if pull_down:
            # кнопка: між S-вузлом і VCC (натиск → S до VCC)
            # ведемо S-вузол ліворуч на висоту кнопки
            btn_y = vcc_y + 70
            f.append(line(node_x, node_y, node_x, btn_y, color=INK, sw=1.6))
            f.append(line(node_x, btn_y, btn_x + 40, btn_y, color=INK, sw=1.6))
            rxc = button_symbol(f, btn_x, btn_y, col=INK)
            f.append(line(btn_x, btn_y, btn_x, vcc_y, color=INK, sw=1.6))   # лівий контакт → VCC
            f.append(circle(btn_x, vcc_y, 3, fill=POS, stroke=POS, sw=1))
            f.append(text(btn_x - 14, btn_y - 26, "кнопка", size=9.5, color=MUTED, anchor="end"))
            # резистор: між S-вузлом і GND (підтяжка ДОНИЗУ)
            res_x = node_x
            resistor_symbol(f, res_x, node_y + 10, gnd_y, "R", col=INK)
            f.append(circle(res_x, gnd_y, 3, fill=NEG, stroke=NEG, sw=1))
            note = "R тягне S до GND;\nнатиск кидає S до VCC"
            rest = "спокій: S = «0»"
            press = "натиск: S = «1»"
        else:
            # кнопка: між S-вузлом і GND (натиск → S до GND)
            btn_y = gnd_y - 70
            f.append(line(node_x, node_y, node_x, btn_y, color=INK, sw=1.6))
            f.append(line(node_x, btn_y, btn_x + 40, btn_y, color=INK, sw=1.6))
            rxc = button_symbol(f, btn_x, btn_y, col=INK)
            f.append(line(btn_x, btn_y, btn_x, gnd_y, color=INK, sw=1.6))   # лівий контакт → GND
            f.append(circle(btn_x, gnd_y, 3, fill=NEG, stroke=NEG, sw=1))
            f.append(text(btn_x - 14, btn_y - 26, "кнопка", size=9.5, color=MUTED, anchor="end"))
            # резистор: між S-вузлом і VCC (підтяжка ДОГОРИ)
            res_x = node_x
            resistor_symbol(f, res_x, vcc_y, node_y - 10, "R", col=INK)
            f.append(circle(res_x, vcc_y, 3, fill=POS, stroke=POS, sw=1))
            note = "R тягне S до VCC;\nнатиск кидає S до GND"
            rest = "спокій: S = «1»"
            press = "натиск: S = «0»"

        # висновок під платою (поза рамкою)
        b, _, _ = textbox(bx + bw / 2, by + bh + 46,
                          rest + "     " + press,
                          size=11.5, fill="#eef6ef", stroke=tcol, bold=True)
        f.append(b)

    scene(40,  "Pull-down  (класичні Keyes)", NEG, True)
    scene(520, "Pull-up  (напр. Joy-IT)",     POS, False)

    render(os.path.join(IMG, "ky004-schematic.svg"), W, H, *f)


# ── 2. Підключення пін-у-пін: KY-004 ↔ мікроконтролер ───────────────────────────
def fig_wiring():
    W, H = 940, 470
    f = [text(W / 2, 28, "Підключення KY-004: три дроти — сигнал, живлення в середині, земля",
              size=15, bold=True)]

    # Модуль ліворуч
    mx, my, mw, mh = 80, 92, 260, 250
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=NEG, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 30, "KY-004", size=16, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 50, "кнопка на платі", size=10, color=MUTED))
    # маленька кнопка-іконка в центрі модуля
    f.append(rect(mx + mw / 2 - 22, my + 70, 44, 44, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(circle(mx + mw / 2, my + 92, 12, fill="#fdf4ec", stroke=INK, sw=1.6))

    pads = [("S", FIELD, my + 150), ("+", POS, my + 190), ("−", NEG, my + 230)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=14, bold=True, color=col, anchor="end"))
    f.append(text(mx + mw - 18, my + 172, "(середній = +)", size=9, color=MUTED, anchor="end"))

    # Плата праворуч
    bx, by, bw, bh = 620, 92, 240, 250
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 30, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("D2", FIELD, my + 150, "цифровий вхід (INPUT)"),
            ("3.3–5 В", POS, my + 190, "під логіку плати"),
            ("GND", NEG, my + 230, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # три дроти
    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    # застереження унизу
    b, _, _ = textbox(W / 2, 410,
                      "Підтяжка вже на платі → пін як INPUT (не INPUT_PULLUP). Полярність (спокій «0» чи «1») звір виміром.\n"
                      "Живлення бери під логіку плати: рівень на S дорівнює VCC, тож 5 В б'є по 3.3-вольтовому входу.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky004-wiring.svg"), W, H, *f)


# ── 3. Брязкіт у часі: сирий сигнал vs усталений стан, який тримає клас ──────────
def fig_debounce_timeline():
    W, H = 940, 430
    f = [text(W / 2, 30, "Брязкіт у часі: одне натиснення дає пачку клацань — клас чекає, поки вщухне",
              size=15, bold=True)]

    # осі часу: дві доріжки — «сирий пін» і «усталений стан класу»
    x0, x1 = 90, W - 40
    top_y = 110          # рівень «сирого» HIGH
    bot_y = 170          # рівень «сирого» LOW
    st_hi = 300          # усталений PRESSED
    st_lo = 360          # усталений RELEASED

    def track_label(y, s, col):
        f.append(text(80, y - 26, s, size=11.5, bold=True, color=col, anchor="end"))

    # підписи доріжок
    f.append(text(46, top_y + 34, "сирий\nпін", size=10.5, color=MUTED, anchor="middle"))
    f.append(text(46, st_lo - 26, "стан у\nкласі", size=10.5, color=MUTED, anchor="middle"))

    # рівні-підписи праворуч
    f.append(text(x1 + 6, top_y + 4, "HIGH", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x1 + 6, bot_y + 4, "LOW", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x1 + 6, st_hi + 4, "PRESSED", size=9.5, color=FIELD, anchor="start"))
    f.append(text(x1 + 6, st_lo + 4, "RELEASED", size=9.5, color=MUTED, anchor="start"))

    # тонкі опорні лінії рівнів
    for yy in (top_y, bot_y):
        f.append(line(x0, yy, x1, yy, color="#e2e6ea", sw=1.0))
    for yy in (st_hi, st_lo):
        f.append(line(x0, yy, x1, yy, color="#e2e6ea", sw=1.0))

    # --- сирий сигнал: спокій LOW, пачка брязкоту, стабільний HIGH, потім знову брязкіт вниз ---
    def seg(xa, xb, y):
        f.append(line(xa, y, xb, y, color=INK, sw=2.4))
    def edge(x, ya, yb):
        f.append(line(x, ya, x, yb, color=INK, sw=2.4))

    # спокій LOW до t1
    t1 = 250
    seg(x0, t1, bot_y)
    # зона брязкоту 1 (натиск): смикається між LOW і HIGH
    bxs = [t1, t1 + 14, t1 + 24, t1 + 40, t1 + 52, t1 + 70]
    lvl = bot_y
    prev = t1
    for bx in bxs[1:]:
        edge(prev, lvl, top_y if lvl == bot_y else bot_y)
        lvl = top_y if lvl == bot_y else bot_y
        seg(prev, bx, lvl)
        prev = bx
    # після брязкоту — усталений HIGH
    edge(prev, lvl, top_y); lvl = top_y
    t2 = 620
    seg(prev, t2, top_y)
    # зона брязкоту 2 (відпускання)
    bxs2 = [t2, t2 + 12, t2 + 26, t2 + 40, t2 + 60]
    prev = t2
    for bx in bxs2[1:]:
        edge(prev, lvl, bot_y if lvl == top_y else top_y)
        lvl = bot_y if lvl == top_y else top_y
        seg(prev, bx, lvl)
        prev = bx
    edge(prev, lvl, bot_y)
    seg(prev, x1, bot_y)

    # напівпрозорі «вікна тремтіння» ~15 мс
    for (za, zb) in ((t1, t1 + 70), (t2, t2 + 60)):
        f.append(rect(za, top_y - 12, zb - za, bot_y - top_y + 24, fill="#fdecea", stroke="none", sw=0, rx=4))
    f.append(text((t1 + t1 + 70) / 2, top_y - 20, "брязкіт ~5–15 мс", size=9.5, color=POS))
    f.append(text((t2 + t2 + 60) / 2, top_y - 20, "брязкіт", size=9.5, color=POS))

    # --- усталений стан у класі: перемикається ОДИН раз, коли вікно тремтіння минуло ---
    # RELEASED до кінця вікна 1, потім PRESSED, потім RELEASED після вікна 2
    settle1 = t1 + 70 + 8      # +debounce-затримка
    settle2 = t2 + 60 + 8
    f.append(line(x0, st_lo, settle1, st_lo, color=MUTED, sw=2.6))
    f.append(line(settle1, st_lo, settle1, st_hi, color=FIELD, sw=2.6))
    f.append(line(settle1, st_hi, settle2, st_hi, color=FIELD, sw=2.6))
    f.append(line(settle2, st_hi, settle2, st_lo, color=MUTED, sw=2.6))
    f.append(line(settle2, st_lo, x1, st_lo, color=MUTED, sw=2.6))

    # маркери подій, які віддає клас
    f.append(circle(settle1, st_hi, 5, fill=FIELD, stroke=FIELD, sw=1))
    b1, _, _ = textbox(settle1, st_hi - 30, "подія «натиснуто»\n(рівно одна)", size=9.5, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    f.append(circle(settle2, st_lo, 5, fill=MUTED, stroke=MUTED, sw=1))
    b2, _, _ = textbox(settle2, st_lo + 34, "подія «відпущено»", size=9.5, fill="#f1f3f5", stroke=MUTED)
    f.append(b2)

    render(os.path.join(IMG, "ky004-debounce.svg"), W, H, *f)


# ── 4. Скінченний автомат кнопки в класі: спокій → чекаю → натиск → утримання → довгий
def fig_states():
    W, H = 940, 360
    f = [text(W / 2, 30, "Кнопка як маленький автомат: клас крокує станами й на переходах віддає події",
              size=15, bold=True)]

    def node(cx, cy, w, s, col, sub=None):
        f.append(rect(cx - w / 2, cy - 26, w, 52, fill="#f7f9fc", stroke=col, sw=2.0, rx=10))
        f.append(text(cx, cy - 2, s, size=12.5, bold=True, color=col))
        if sub:
            f.append(text(cx, cy + 15, sub, size=9, color=MUTED))

    y = 130
    xs = [140, 350, 560, 790]
    node(xs[0], y, 150, "IDLE", MUTED, "стан спокою")
    node(xs[1], y, 175, "MAYBE", "#b8860b", "зміна — чекаю вікно")
    node(xs[2], y, 150, "PRESSED", FIELD, "утримується")
    node(xs[3], y, 150, "LONG", POS, "довгий натиск")

    def conn(xa, xb, lab, col, up=True):
        ya = y
        f.append(arrow(xa + 78, ya - (10 if up else -10), xb - 78, ya - (10 if up else -10), color=col, sw=2.0))
        yy = ya - 24 if up else ya + 26
        f.append(text((xa + xb) / 2, yy, lab, size=9.5, color=col))

    # прямі переходи
    f.append(arrow(xs[0] + 76, y, xs[1] - 90, y, color=INK, sw=1.8))
    f.append(text((xs[0] + xs[1]) / 2, y - 12, "рівень != спокій", size=9, color=INK))

    f.append(arrow(xs[1] + 90, y, xs[2] - 76, y, color=FIELD, sw=1.8))
    f.append(text((xs[1] + xs[2]) / 2, y - 12, "устоявся →", size=9, color=FIELD))
    f.append(text((xs[1] + xs[2]) / 2, y + 16, "подія «натиснуто»", size=9, color=FIELD))

    f.append(arrow(xs[2] + 76, y, xs[3] - 76, y, color=POS, sw=1.8))
    f.append(text((xs[2] + xs[3]) / 2, y - 12, "утримується > T_long", size=9, color=POS))
    f.append(text((xs[2] + xs[3]) / 2, y + 16, "подія «довгий»", size=9, color=POS))

    # повернення в IDLE (дуга знизу від PRESSED і LONG)
    def back(xa, lab):
        yb = y + 70
        f.append(line(xa, y + 26, xa, yb, color=MUTED, sw=1.6, dash="4,4"))
        f.append(line(xa, yb, xs[0], yb, color=MUTED, sw=1.6, dash="4,4"))
        f.append(arrow(xs[0], yb, xs[0], y + 28, color=MUTED, sw=1.6))
        f.append(text((xa + xs[0]) / 2, yb + 16, lab, size=9, color=MUTED))

    back(xs[2], "відпущено → подія «відпущено», назад в IDLE")

    # хибний брязкіт: MAYBE → IDLE (не встоявся)
    f.append(line(xs[1], y + 26, xs[1], y + 52, color="#b8860b", sw=1.5, dash="3,4"))
    f.append(line(xs[1], y + 52, xs[0] + 30, y + 52, color="#b8860b", sw=1.5, dash="3,4"))
    f.append(arrow(xs[0] + 30, y + 52, xs[0] + 20, y + 30, color="#b8860b", sw=1.5))
    f.append(text((xs[1] + xs[0]) / 2 + 20, y + 44, "не встоявся (брязкіт) → назад, події немає", size=9, color="#b8860b"))

    render(os.path.join(IMG, "ky004-states.svg"), W, H, *f)


if __name__ == "__main__":
    fig_schematic()
    fig_wiring()
    fig_debounce_timeline()
    fig_states()
    print("KY-004 figs done ->", IMG)
