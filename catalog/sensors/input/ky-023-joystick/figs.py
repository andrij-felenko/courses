# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-023 — джойстик-модуль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WIPER = "#c0392b"   # повзунок
KNOB  = "#3b4048"   # ковпачок ручки


# ── 1. Що всередині: дві осі — два потенціометри; нахил крутить повзунок ───────
def fig_inside():
    W, H = 900, 520
    f = [text(W / 2, 30, "Усередині KY-023: два потенціометри на схрещених осях + кнопка під натиск",
              size=15, bold=True)]

    # --- ліворуч: сам механізм — ручка на кардані, дві осі ---
    cx, cy = 250, 250
    # рамка механізму
    f.append(rect(cx - 150, cy - 150, 300, 300, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(cx, cy - 165, "механізм ручки (вид зверху)", size=11.5, bold=True, color=MUTED))

    # вісь X — горизонтальне коромисло з потенціометром ліворуч
    f.append(line(cx - 120, cy, cx + 120, cy, color=NEG, sw=2.4))
    # вісь Y — вертикальне коромисло з потенціометром угорі
    f.append(line(cx, cy - 120, cx, cy + 120, color=FIELD, sw=2.4))
    # два кружечки-осі обертання по краях
    f.append(circle(cx - 120, cy, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(cx - 120, cy - 22, "пот. X", size=10.5, bold=True, color=NEG))
    f.append(circle(cx, cy - 120, 12, fill="#eafaef", stroke=FIELD, sw=2))
    f.append(text(cx + 34, cy - 118, "пот. Y", size=10.5, bold=True, color=FIELD))

    # ручка в центрі (ковпачок) + діапазон похитування
    f.append(circle(cx, cy, 40, fill="none", stroke="#cfd4da", sw=1.2, ))
    f.append(circle(cx, cy, 22, fill=KNOB, stroke=INK, sw=1.6))
    f.append(circle(cx, cy, 8, fill="#5b616b", stroke=INK, sw=1))
    # стрілки: похитування рухає обидві осі
    f.append(arrow(cx + 46, cy, cx + 96, cy, color=NEG, sw=1.6))
    f.append(arrow(cx - 46, cy, cx - 96, cy, color=NEG, sw=1.6))
    f.append(arrow(cx, cy - 46, cx, cy - 96, color=FIELD, sw=1.6))
    f.append(arrow(cx, cy + 46, cx, cy + 96, color=FIELD, sw=1.6))
    # підпис ручки — у порожньому куті, ПОЗА осьовими лініями
    f.append(text(cx - 96, cy + 64, "ручка", size=10.5, bold=True, color=KNOB, anchor="start"))
    f.append(line(cx - 70, cy + 60, cx - 18, cy + 18, color="#cfd4da", sw=1.0))
    # натиск донизу = кнопка
    f.append(text(cx + 96, cy + 128, "натиск ↓ = кнопка SW", size=10.5, bold=True, color=POS, anchor="end"))

    # --- праворуч: один потенціометр крупно — як нахил зсуває повзунок ---
    px, py = 660, 250
    f.append(text(px, py - 165, "одна вісь = один потенціометр", size=11.5, bold=True, color=MUTED))
    # доріжка опору (горизонтальна смужка)
    tx0, tx1 = px - 130, px + 130
    ty = py
    f.append(rect(tx0, ty - 14, tx1 - tx0, 28, fill="#f0e6e6", stroke=WIPER, sw=1.6, rx=6))
    f.append(text(tx0 - 12, ty + 5, "+", size=17, bold=True, color=POS, anchor="end"))
    f.append(text(tx1 + 12, ty + 5, "−", size=17, bold=True, color=NEG, anchor="start"))
    f.append(text(px, ty - 26, "смужка опору 10 кОм (кінці на + і −)", size=10, color=MUTED))

    # повзунок у центрі + відведення вгору (сигнал осі)
    wx = px  # центр = спокій
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (wx, ty - 14, wx - 12, ty - 40, wx + 12, ty - 40, WIPER, INK))
    f.append(line(wx, ty - 40, wx, ty - 66, color=WIPER, sw=2.4))
    f.append(text(wx, ty - 74, "напруга осі → VRx / VRy", size=10.5, bold=True, color=WIPER))
    # позиції повзунка: спокій (центр) і зсув
    f.append(circle(wx, ty, 5, fill=WIPER, stroke=INK, sw=1))
    f.append(text(px, ty + 40, "спокій → повзунок посередині → ≈ ½ живлення",
                  size=10.5, bold=True, color=INK))
    f.append(text(px, ty + 60, "нахил → повзунок їде до кінця → напруга до + чи −",
                  size=10.5, color=MUTED))
    # маленькі стрілки руху повзунка
    f.append(arrow(wx + 20, ty + 90, wx + 90, ty + 90, color=NEG, sw=1.4))
    f.append(arrow(wx - 20, ty + 90, wx - 90, ty + 90, color=NEG, sw=1.4))

    b, _, _ = textbox(W / 2, 486,
                      "джойстик = дві незалежні «крутилки-гучності» на схрещених осях: похитування ручки крутить\n"
                      "обидва повзунки, і кожна вісь віддає свою напругу; натиск ручки донизу тисне окрему кнопку",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Схема модуля: дільники X/Y (кінці +/−, повзунок = вихід) + гола кнопка ──
def fig_schematic():
    W, H = 900, 540
    f = [text(W / 2, 30, "Схема KY-023: два потенціометри-дільники (X, Y) + гола кнопка SW на землю",
              size=14.5, bold=True)]

    xL, xR = 130, 640
    yPlus, yGnd = 84, 470
    # шина +
    f.append(line(xL, yPlus, xR, yPlus, color=POS, sw=2.2))
    f.append(text(xL - 14, yPlus + 5, "+", size=18, bold=True, color=POS, anchor="end"))
    f.append(text(xR + 12, yPlus + 5, "живлення +5 В", size=10.5, color=POS, anchor="start"))
    # шина земля
    f.append(line(xL, yGnd, xR, yGnd, color=INK, sw=2.2))
    f.append(text(xL - 14, yGnd + 5, "−", size=18, bold=True, color=NEG, anchor="end"))
    f.append(text(xR + 12, yGnd + 5, "земля (GND)", size=10.5, color=INK, anchor="start"))

    def potentiometer(x, label, out_name, col):
        """Вертикальний потенціометр між + і −: смужка опору, повзунок-стрілка вбік = вихід."""
        top, bot = yPlus + 26, yGnd - 26
        # смужка опору
        f.append(rect(x - 11, top, 22, bot - top, fill="#f0e6e6", stroke=WIPER, sw=1.6, rx=6))
        f.append(line(x, yPlus, x, top, color=INK, sw=2))
        f.append(line(x, bot, x, yGnd, color=INK, sw=2))
        # підпис «10 кОм» — праворуч від смужки, ПОЗА проводом-стовпом
        f.append(text(x + 18, top + 14, "10 кОм", size=10, bold=True, color=MUTED, anchor="start"))
        # повзунок посередині — стрілка вбік
        wy = (top + bot) / 2
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.3"/>'
                 % (x - 11, wy, x - 34, wy - 10, x - 34, wy + 10, WIPER, INK))
        f.append(line(x - 34, wy, x - 74, wy, color=col, sw=2.2))
        f.append(rect(x - 74 - 52, wy - 14, 52, 28, fill="#eef2f8", stroke=col, sw=1.6, rx=4))
        f.append(text(x - 74 - 26, wy + 5, out_name, size=12, bold=True, color=col))
        f.append(text(x + 16, wy + 3, "повзунок", size=8.5, color="#7a4040", anchor="start"))
        # підпис осі — праворуч від нижнього проводу, ПОЗА ним
        f.append(text(x + 18, bot + 18, label, size=11, bold=True, anchor="start"))

    potentiometer(300, "вісь X", "VRx", NEG)
    potentiometer(560, "вісь Y", "VRy", FIELD)

    # кнопка SW: гола, один бік на землю, другий — вихід SW (БЕЗ підтяжки!)
    sx = 770
    top, bot = yPlus + 90, yGnd
    f.append(text(sx, yPlus + 70, "кнопка (натиск ручки)", size=10.5, bold=True, color=POS))
    # вивід SW угорі (нікуди не тягнеться на платі)
    f.append(line(sx, top, sx, top - 20, color=POS, sw=2))
    f.append(rect(sx - 26, top - 46, 52, 26, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    f.append(text(sx, top - 27, "SW", size=12, bold=True, color=POS))
    # символ кнопки (розімкнена): дві точки + місток
    f.append(circle(sx, top, 3.5, fill=BG, stroke=INK, sw=1.6))
    f.append(circle(sx, top + 46, 3.5, fill=BG, stroke=INK, sw=1.6))
    f.append(line(sx - 16, top + 16, sx + 16, top + 16, color=INK, sw=2.2))  # рухомий місток
    f.append(line(sx, top + 16, sx, top + 4, color=INK, sw=1.4))
    f.append(text(sx + 22, top + 20, "натиск", size=9, color=MUTED, anchor="start"))
    f.append(line(sx, top + 46, sx, bot, color=INK, sw=2))
    f.append(text(sx + 20, (top + bot) / 2, "інший бік —\nна землю", size=9, color=MUTED, anchor="start"))

    # застереження про відсутність підтяжки — плашка над кнопкою, ліворуч від її стовпа
    b1 = fitbox(660, yPlus + 4, 210, 52,
                "УВАГА: на SW НЕМАЄ підтяжки\nна платі — висить у повітрі!",
                size=10, fill="#fdf0ee", stroke=POS, bold=True)
    f.append(b1)

    b, _, _ = textbox(W / 2, 506,
                      "X і Y — звичайні дільники напруги: кінці смужки на + і −, повзунок віддає напругу за положенням "
                      "(спокій ≈ ½).\nКнопка SW — гола, замикає лише на землю; підтяжки на модулі немає, тож вмикай "
                      "внутрішню (INPUT_PULLUP).",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "schematic.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: 5 дротів до плати (2 АЦП + 1 GPIO + жив./земля) ──
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 28, "Підключення KY-023: 5 дротів — VRx/VRy в АЦП, SW у цифровий вхід із підтяжкою",
              size=14, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 80, 96, 210, 250
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "KY-023", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 44, "джойстик (дві осі + кнопка)", size=9, color=MUTED))
    # ручка схематично
    f.append(circle(mx + mw / 2, my + 96, 28, fill="none", stroke="#cfd4da", sw=1.2))
    f.append(circle(mx + mw / 2, my + 96, 16, fill=KNOB, stroke=INK, sw=1.4))

    # п'ять пінів у рядок знизу модуля
    pins = [("GND", INK, "#f2f2f2"), ("+5V", POS, "#fdecea"),
            ("VRx", NEG, "#eaf0fd"), ("VRy", FIELD, "#eafaef"), ("SW", POS, "#fdecea")]
    pin_x = []
    for i, (nm, col, fl) in enumerate(pins):
        px = mx + 24 + i * 41
        pin_x.append(px)
        f.append(rect(px - 17, my + mh - 4, 34, 24, fill=fl, stroke=col, sw=1.4, rx=3))
        f.append(text(px, my + mh + 12, nm, size=9.5, bold=True, color=col))

    # МК праворуч
    ax, ay, aw, ah = 600, 110, 210, 240
    f.append(rect(ax, ay, aw, ah, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(ax + aw / 2, ay + 44, "(Arduino / ESP32 …)", size=9, color=MUTED))
    mpins = [("GND", INK), ("5 В / 3.3 В", POS), ("A0 (АЦП)", NEG),
             ("A1 (АЦП)", FIELD), ("D-пін", POS)]
    mpin_y = []
    for i, (nm, col) in enumerate(mpins):
        py = ay + 74 + i * 32
        mpin_y.append(py)
        f.append(rect(ax - 4, py - 11, 8, 22, fill="#fff", stroke=col, sw=1.4, rx=2))
        f.append(text(ax - 12, py + 4, nm, size=9.5, bold=True, color=col, anchor="end"))

    # дроти: кожен пін модуля → відповідний пін МК, різні рівні розводки
    routes = [
        (pin_x[0], mpin_y[0], INK,   356),   # GND
        (pin_x[1], mpin_y[1], POS,   372),   # +5V
        (pin_x[2], mpin_y[2], NEG,   388),   # VRx -> A0
        (pin_x[3], mpin_y[3], FIELD, 404),   # VRy -> A1
        (pin_x[4], mpin_y[4], POS,   420),   # SW  -> D
    ]
    for sxp, ryp, col, ylevel in routes:
        f.append(line(sxp, my + mh + 20, sxp, ylevel, color=col, sw=1.8))
        f.append(line(sxp, ylevel, ax - 4, ryp, color=col, sw=1.8))

    b, _, _ = textbox(W / 2, 448,
                      "GND→GND, +5V→живлення під логіку плати; VRx→аналоговий A0, VRy→аналоговий A1 (обидва читаєш АЦП); "
                      "SW→будь-який цифровий вхід,\nувімкнений як INPUT_PULLUP (на модулі підтяжки немає). Живиш 5 В — "
                      "на 3.3-В плату VRx/VRy дадуть завеликий розмах, зважай.",
                      size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Історія: лінія аналогового стика від 1982 до KY-023 ────────────────────
def fig_lineage():
    """Часова лінія: несамоцентрований Atari 5200 і самоцентрований Vectrex (1982)
    → аркадний флайт-стик Space Harrier (1985) → лінія Sony (1996–1997) → KY-023."""
    W, H = 1240, 620
    f = [text(W / 2, 30, "Лінія аналогового стика: від 1982 до грибоподібної ручки KY-023",
              size=16, bold=True)]

    # головна вісь часу
    ax0, ax1, ay = 90, W - 110, 118
    f.append(line(ax0, ay, ax1, ay, color=MUTED, sw=2.4))
    f.append(arrow(ax1 - 2, ay, ax1 + 24, ay, color=MUTED, sw=2.4))
    f.append(text(ax1 + 20, ay - 14, "час", size=11, italic=True, color=MUTED))

    # мітки років на осі (нерівномірні, з підписами під запас)
    years = [(1982, 150), (1985, 400), (1996, 690), (1997, 900), ("KY-023", 1090)]
    for yr, xx in years:
        f.append(line(xx, ay - 8, xx, ay + 8, color=MUTED, sw=2))
        f.append(text(xx, ay - 16, str(yr), size=12.5, bold=True, color=INK))

    # ── картки етапів: центр X прив'язаний до року, рознесені по вертикалі ──
    # body — список КОРОТКИХ рядків (кожен влазить у картку без стиску шрифту)
    # stem=True → ніжка від осі часу; stem_from=(x,y) → ніжка від заданої точки
    def card(cx, top, w, head, headcol, body, bodyfill, stem=True, stem_from=None):
        bh = 22 + len(body) * 16          # висота тіла під кількість рядків
        b1, hw, hh = textbox(cx, top + 15, head, size=11.5, pad=8, bold=True,
                             fill="#fff", stroke=headcol, color=headcol, min_w=w)
        b2 = fitbox(cx - w / 2, top + 32, w, bh, body, size=11, pad=8,
                    fill=bodyfill, stroke=headcol, color=INK)
        st = ""
        if stem:
            st = line(cx, ay + 8, cx, top, color=headcol, sw=1.4, dash="3,3")
        elif stem_from is not None:
            st = line(stem_from[0], stem_from[1], cx, top, color=headcol, sw=1.4, dash="3,3")
        return st + b1 + b2

    # 1982 — дві гілки того самого року: Atari від осі, Vectrex нижче,
    # ніжка Vectrex іде збоку (не крізь картку Atari)
    ATARI_BOTTOM = 168 + 32 + (22 + 6 * 16)   # низ картки Atari
    f.append(card(150, 168, 216, "Atari 5200 — НЕ центрується",
                  POS,
                  ["Перший аналог-стик на",
                   "потенціометрах у домашній",
                   "консолі. Відпустив ручку —",
                   "лишилась де є. Гумовий чохол",
                   "замість пружин, дрейф, масові",
                   "заміни. Урок «як не треба»."],
                  "#fdecea"))

    f.append(card(150, 348, 216, "Vectrex — самоцентрований",
                  FIELD,
                  ["Той самий 1982-й, зворотне",
                   "рішення: пружини вертають",
                   "ручку в центр. Саме ця",
                   "пружина-центр і лишилась",
                   "в усіх дальших стиках,",
                   "зокрема в KY-023."],
                  "#eafaef",
                  stem=False, stem_from=(245, ATARI_BOTTOM + 2)))

    f.append(card(400, 226, 234, "Sega Space Harrier — флайт-стик",
                  NEG,
                  ["Аркада (Ю Судзукі, Sega).",
                   "Аналоговий флайт-стик: не",
                   "лише напрямок, а й НАСКІЛЬКИ",
                   "відхилив — величина натиску",
                   "керує швидкістю. Аналог",
                   "довів свою силу."],
                  "#eaf0fd"))

    f.append(card(695, 306, 226, "Sony PS Analog Joystick",
                  NEG,
                  ["SCPH-1110 (1996): великий",
                   "аналоговий джойстик до",
                   "PlayStation (плутають із",
                   "«флайтстиком»). Sony заводить",
                   "аналог у масову консоль."],
                  "#eaf0fd"))

    f.append(card(905, 204, 234, "Sony Dual Analog → DualShock",
                  NEG,
                  ["1997: ДВА стики під великі",
                   "пальці на одному геймпаді.",
                   "Спершу увігнуті (Dual Analog),",
                   "тоді гумові опуклі ковпачки",
                   "(DualShock) — власне «гриб»."],
                  "#eaf0fd"))

    # KY-023 — фінальна картка, виділена
    b, kw, kh = textbox(1090, 198, ["KY-023", "той самий гриб", "на синій платі"],
                        size=11, pad=10, bold=True, fill="#fff5d6", stroke="#b8860b",
                        color="#7a5c00", min_w=156)
    f.append(line(1090, ay + 8, 1090, 172, color="#b8860b", sw=1.8, dash="3,3"))
    f.append(b)
    b2 = fitbox(1090 - 110, 232, 220, 96,
                ["Механізм грибоподібного",
                 "стика PlayStation, винесений",
                 "як окремий модуль до Arduino:",
                 "два потенціометри + кнопка-",
                 "натиск на самій ручці."],
                size=11, pad=8, fill="#fff5d6", stroke="#b8860b", color=INK)
    f.append(b2)

    # нижній підсумковий рядок
    b3, _, _ = textbox(W / 2, 555,
                       ["Дві ідеї 1982-го — «аналог напрямку» (обидва) і «пружина-центр» (Vectrex) — злилися;",
                        "аркада додала «величину відхилення», Sony звела два стики під пальці й одягла їх у гумовий гриб.",
                        "KY-023 — цей самий гриб, винесений на синю плату."],
                       size=10.5, pad=10, fill=FILL, stroke=MUTED)
    f.append(b3)

    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


# ── 5. Дві осі → 8 напрямків: решітка 3×3 з порогом-хрестом (для proj-вставки) ─
def fig_directions():
    W, H = 900, 470
    f = [text(W / 2, 30, "Вісім напрямків із двох осей: кожну вісь → −1/0/+1, решітка 3×3",
              size=15, bold=True)]

    # ── ліворуч: сама решітка 3×3 ──
    cx, cy = 250, 228          # центр решітки
    cell = 80                  # крок клітини
    def cellxy(sx, sy):        # -1,0,+1 по осях; +Y угору = північ
        return cx + sx * cell, cy - sy * cell

    # мертвий хрест (центральна смуга спокою) — світла підкладка
    f.append(rect(cx - cell * 1.5, cy - cell / 2 - 6, cell * 3, cell + 12,
                  fill="#eef2f8", stroke="none", rx=8))
    f.append(rect(cx - cell / 2 - 6, cy - cell * 1.5, cell + 12, cell * 3,
                  fill="#eef2f8", stroke="none", rx=8))

    labels = {(0, 1): "Пн", (1, 1): "ПнСх", (1, 0): "Сх", (1, -1): "ПдСх",
              (0, -1): "Пд", (-1, -1): "ПдЗх", (-1, 0): "Зх", (-1, 1): "ПнЗх"}
    for sx in (-1, 0, 1):
        for sy in (-1, 0, 1):
            x, y = cellxy(sx, sy)
            if sx == 0 and sy == 0:
                f.append(circle(x, y, 30, fill="#f2f2f2", stroke=MUTED, sw=1.6))
                f.append(text(x, y - 3, "спокій", size=10.5, bold=True, color=MUTED))
                f.append(text(x, y + 12, "(0,0)", size=9, color=MUTED))
                continue
            diag = (sx != 0 and sy != 0)
            col = FIELD if diag else NEG
            fillc = "#eafaef" if diag else "#eaf0fd"
            f.append(rect(x - 34, y - 26, 68, 52, fill=fillc, stroke=col, sw=1.6, rx=8))
            f.append(text(x, y - 4, labels[(sx, sy)], size=12, bold=True, color=col))
            f.append(text(x, y + 13, "(%+d,%+d)" % (sx, sy), size=9, color=MUTED))

    # осьові стрілки навколо решітки
    f.append(arrow(cx, cy - cell * 1.5 - 14, cx, cy - cell * 1.5 - 40, color=INK, sw=1.6))
    f.append(text(cx, cy - cell * 1.5 - 48, "+Y (вгору)", size=10, bold=True))
    f.append(arrow(cx + cell * 1.5 + 14, cy, cx + cell * 1.5 + 40, cy, color=INK, sw=1.6))
    f.append(text(cx + cell * 1.5 + 52, cy + 4, "+X", size=10, bold=True, anchor="start"))

    # ── праворуч: одна вісь → поріг → трійка −1/0/+1 ──
    px = 660
    bar_y = 150
    bx0, bx1 = px - 120, px + 120
    f.append(text(px, bar_y - 40, "як вісь стає трійкою −1 / 0 / +1", size=12, bold=True, color=MUTED))
    f.append(rect(bx0, bar_y - 16, bx1 - bx0, 32, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=8))
    tw = 42  # піврозмір порогу в пікселях
    f.append(rect(px - tw, bar_y - 16, tw * 2, 32, fill="#eef2f8", stroke="none"))
    f.append(text(px, bar_y + 5, "0", size=12, bold=True, color=MUTED))
    f.append(text(bx0 - 10, bar_y + 5, "−100", size=10, color=NEG, anchor="end"))
    f.append(text(bx1 + 10, bar_y + 5, "+100", size=10, color=NEG, anchor="start"))
    f.append(text((bx0 + px - tw) / 2, bar_y + 42, "−1", size=15, bold=True, color=NEG))
    f.append(text(px, bar_y + 42, "0", size=15, bold=True, color=MUTED))
    f.append(text((bx1 + px + tw) / 2, bar_y + 42, "+1", size=15, bold=True, color=NEG))
    f.append(line(px - tw, bar_y - 22, px - tw, bar_y + 24, color=POS, sw=1.4, dash="4,3"))
    f.append(line(px + tw, bar_y - 22, px + tw, bar_y + 24, color=POS, sw=1.4, dash="4,3"))
    f.append(text(px, bar_y - 58, "поріг ±40 %", size=10, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 372,
                      "Кожну плавну вісь зводимо порогом до −1/0/+1; дві такі трійки дають решітку 3×3 — центр\n"
                      "= спокій, боки = 4 прямі напрямки, кути = 4 діагоналі. Ширший поріг = ширший хрест спокою\n"
                      "(важче зачепити напрямок випадково), вужчий = чутливіше й тремкіше на межі секторів.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "directions.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_schematic()
    fig_wiring()
    fig_lineage()
    fig_directions()
    print("OK: 5 figures ->", IMG)
