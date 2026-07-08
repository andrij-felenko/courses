# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-027 — Magic Light Cup».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def led_symbol(cx, cy, color=INK):
    """Символ світлодіода: трикутник + катодна риска + дві стрілки світла.
    Анод зверху (вхід струму), катод знизу."""
    s = []
    # трикутник (вістрям униз — від анода до катода)
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
             % (cx - 12, cy - 12, cx + 12, cy - 12, cx, cy + 8, color))
    # катодна риска
    s.append(line(cx - 12, cy + 8, cx + 12, cy + 8, color=color, sw=2))
    # дві стрілочки «світло»
    s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (cx + 13, cy - 8, cx + 26, cy - 20, POS))
    s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (cx + 15, cy + 0, cx + 28, cy - 12, POS))
    return "".join(s)


def tilt_symbol(cx, cy, closed=True):
    """Схематичний кульковий вимикач: трубка похило, кулька + два контакти."""
    s = []
    # корпус-трубка (нахилена рамка)
    s.append('<rect x="%.1f" y="%.1f" width="60" height="26" rx="13" fill="#f4f6f8" stroke="%s" stroke-width="1.6"/>'
             % (cx - 30, cy - 13, LINE))
    # два контакти на лівому кінці
    s.append(line(cx - 22, cy - 13, cx - 22, cy + 13, color=LINE, sw=1.4))
    s.append(line(cx - 14, cy - 13, cx - 14, cy + 13, color=LINE, sw=1.4))
    # кулька (біля контактів = ON; далеко = OFF)
    bx = cx - 18 if closed else cx + 18
    s.append(circle(bx, cy, 8, fill="#9aa0a6", stroke=INK, sw=1.2))
    return "".join(s)


# ── 1. Що на одній платі KY-027: гребінка, вимикач, LED із резистором ─────────
def fig_board():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 34, "Одна плата KY-027: що на ній", size=17, bold=True))

    # межа плати
    f.append(rect(70, 70, 620, 300, fill="#ffffff", stroke=INK, sw=1.8, rx=10))
    f.append(text(90, 96, "плата (одна з пари)", size=12, color=MUTED, anchor="start"))

    # 4-контактна гребінка ліворуч
    hx, hy = 150, 150
    labels = ["G", "+", "S", "L"]
    lab_full = ["земля (GND)", "живлення 3.3–5 В", "вихід вимикача", "вхід LED (ШІМ)"]
    lab_col = [INK, POS, NEG, FIELD]
    for i, (lb, lf, lc) in enumerate(zip(labels, lab_full, lab_col)):
        y = hy + i * 55
        f.append(rect(hx - 20, y - 16, 40, 32, fill="#f4f6f8", stroke=INK, sw=1.4, rx=4))
        f.append(text(hx, y + 5, lb, size=15, bold=True, color=lc))
        f.append(text(hx - 34, y + 5, lf, size=11, color=lc, anchor="end"))
    f.append(text(hx, hy - 34, "гребінка 4 піни", size=12, color=MUTED))

    # рейки: «+» коротка (живить лише підтяжку вимикача), «G» унизу спільна
    railL_x, railg_x = 470, 620
    top_y, bot_y = 130, 330
    # рейка «G» від піна G — спільна знизу
    f.append(line(hx + 20, hy, 240, hy, color=INK, sw=1.6))
    f.append(line(240, hy, 240, bot_y, color=INK, sw=1.6))
    f.append(line(240, bot_y, 660, bot_y, color=INK, sw=1.6))
    f.append(text(360, bot_y + 20, "G  (спільна земля)", size=12, color=INK))
    # рейка «+» від піна + до верху праворуч (лише до підтяжки вимикача)
    f.append(line(hx + 20, hy + 55, 340, hy + 55, color=POS, sw=1.6))
    f.append(line(340, hy + 55, 340, top_y, color=POS, sw=1.6))
    f.append(line(340, top_y, railg_x, top_y, color=POS, sw=1.6))
    f.append(text(430, top_y - 8, "+  (живлення)", size=12, color=POS))

    # гілка світлодіода: пін L → резистор → LED(анод→катод) → земля.
    # Струм у LED дає САМ пін L; тримаючи L під ШІМ, МК задає яскравість.
    lx = railL_x
    # від піна L праворуч і вгору до резистора
    f.append(line(hx + 20, hy + 165, 210, hy + 165, color=FIELD, sw=1.8))
    f.append(line(210, hy + 165, 210, top_y + 38, color=FIELD, sw=1.8))
    f.append(line(210, top_y + 38, lx, top_y + 38, color=FIELD, sw=1.8))
    f.append(text(300, top_y + 30, "струм LED тече з L", size=11, color=FIELD))
    # резистор
    f.append(rect(lx - 16, top_y + 38, 32, 40, fill="#fff", stroke=INK, sw=1.5, rx=3))
    f.append(text(lx + 40, top_y + 60, "резистор", size=11, color=MUTED, anchor="start"))
    f.append(text(lx + 40, top_y + 74, "≈220 Ом", size=11, color=MUTED, anchor="start"))
    # LED
    f.append(led_symbol(lx, 258, color=INK))
    f.append(line(lx, top_y + 78, lx, 258 - 12, color=INK, sw=1.6))
    f.append(text(lx + 44, 258, "LED", size=12, color=INK, anchor="start"))
    f.append(line(lx, 258 + 8, lx, bot_y, color=INK, sw=1.6))

    # гілка вимикача: + → підтяжка 10к → вузол S → вимикач → G
    sx = railg_x
    f.append(rect(sx - 16, top_y + 18, 32, 40, fill="#fff", stroke=INK, sw=1.5, rx=3))
    f.append(text(sx + 22, top_y + 34, "10 кОм", size=11, color=MUTED, anchor="start"))
    f.append(text(sx + 22, top_y + 50, "підтяжка", size=11, color=MUTED, anchor="start"))
    f.append(line(sx, top_y, sx, top_y + 18, color=POS, sw=1.6))
    # вимикач
    f.append(tilt_symbol(sx, 250, closed=True))
    f.append(line(sx, top_y + 58, sx, 250 - 13, color=INK, sw=1.6))
    f.append(line(sx, 250 + 13, sx, bot_y, color=INK, sw=1.6))
    f.append(text(sx + 38, 246, "вимикач", size=11, color=MUTED, anchor="start"))
    f.append(text(sx + 38, 260, "нахилу", size=11, color=MUTED, anchor="start"))
    # вихід S — з вузла між підтяжкою і вимикачем
    node_y = top_y + 58 + 20
    f.append(circle(sx, node_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(line(sx, node_y, sx + 60, node_y, color=NEG, sw=1.6, dash="5 4"))
    f.append(text(sx + 66, node_y + 4, "S", size=13, bold=True, color=NEG, anchor="start"))
    render(os.path.join(IMG, 'board.svg'), W, H, "".join(f))


# ── 2. Розводка пін-у-пін: дві плати до Arduino ──────────────────────────────
def fig_wiring():
    W, H = 780, 470
    f = []
    f.append(text(W / 2, 34, "Розводка пари KY-027 до Arduino", size=17, bold=True))

    # МК посередині
    mx, my, mw, mh = 320, 110, 150, 250
    f.append(rect(mx, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "Arduino", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 44, "(UNO)", size=11, color=MUTED))

    mc_pins = ["5V", "GND", "D8", "~D9", "D7", "~D6"]
    mc_y = {}
    for i, p in enumerate(mc_pins):
        y = my + 74 + i * 30
        mc_y[p] = y
        f.append(rect(mx + mw - 46, y - 12, 42, 24, fill="#fff", stroke=NEG, sw=1.2, rx=4))
        f.append(text(mx + mw - 25, y + 4, p, size=12, bold=True, color=NEG))
    # ліві піни живлення виходять ліворуч
    f.append(rect(mx + 4, mc_y["5V"] - 12, 42, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(mx + 25, mc_y["5V"] + 4, "5V", size=12, bold=True, color=POS))
    f.append(rect(mx + 4, mc_y["GND"] - 12, 42, 24, fill="#f4f6f8", stroke=INK, sw=1.2, rx=4))
    f.append(text(mx + 25, mc_y["GND"] + 4, "GND", size=11, bold=True, color=INK))

    # Плата A праворуч
    ax, ay = 610, 90
    f.append(rect(ax, ay, 130, 150, fill="#ffffff", stroke=INK, sw=1.6, rx=8))
    f.append(text(ax + 65, ay + 24, "Плата A", size=13, bold=True))
    f.append(text(ax + 65, ay + 42, "(перша чашка)", size=10, color=MUTED))
    a_pins = ["G", "+", "S", "L"]
    a_col = [INK, POS, NEG, FIELD]
    a_y = {}
    for i, (p, c) in enumerate(zip(a_pins, a_col)):
        y = ay + 66 + i * 20
        a_y[p] = y
        f.append(rect(ax + 6, y - 9, 26, 18, fill="#f4f6f8", stroke=c, sw=1.2, rx=3))
        f.append(text(ax + 19, y + 4, p, size=11, bold=True, color=c))

    # Плата B ліворуч
    bx, by = 40, 90
    f.append(rect(bx, by, 130, 150, fill="#ffffff", stroke=INK, sw=1.6, rx=8))
    f.append(text(bx + 65, by + 24, "Плата B", size=13, bold=True))
    f.append(text(bx + 65, by + 42, "(друга чашка)", size=10, color=MUTED))
    b_pins = ["G", "+", "S", "L"]
    b_col = [INK, POS, NEG, FIELD]
    b_y = {}
    for i, (p, c) in enumerate(zip(b_pins, b_col)):
        y = by + 66 + i * 20
        b_y[p] = y
        f.append(rect(bx + 98, y - 9, 26, 18, fill="#f4f6f8", stroke=c, sw=1.2, rx=3))
        f.append(text(bx + 111, y + 4, p, size=11, bold=True, color=c))

    # ── дроти A (праворуч від МК) ──
    # + шина: 5V(лівий) не тут; беремо правий 5V пін? Живлення — з лівого 5V/GND до обох плат.
    # Проведемо живлення з лівих пінів угору-в-обхід. Простіше: правий бік — сигнали, лівий — живлення.
    # A: S→D8, L→~D9
    f.append(line(ax, a_y["S"], mx + mw + 4, mc_y["D8"], color=NEG, sw=1.6))
    f.append(line(ax, a_y["L"], mx + mw + 4, mc_y["~D9"], color=FIELD, sw=1.6))
    # B: S→D7, L→~D6
    f.append(line(bx + 130, b_y["S"], mx - 4, mc_y["D7"], color=NEG, sw=1.6))
    f.append(line(bx + 130, b_y["L"], mx - 4, mc_y["~D6"], color=FIELD, sw=1.6))

    # живлення: спільні нижні шини «+» і «G»; кожен споживач падає на них своїм відводом.
    # МК-піни живлення виходять ліворуч і падають у смузі між платою B (≤170) і МК (≥320).
    powy = 400
    gndy = 432
    # + рейка
    f.append(line(mx + 4, mc_y["5V"], 300, mc_y["5V"], color=POS, sw=1.6))
    f.append(line(300, mc_y["5V"], 300, powy, color=POS, sw=1.6))
    f.append(line(24, powy, 758, powy, color=POS, sw=1.8))
    f.append(text(430, powy - 8, "+  (живлення 5 В на обидві плати)", size=11, color=POS))
    f.append(line(bx + 111, b_y["+"], bx + 111, powy, color=POS, sw=1.4, dash="4 3"))
    f.append(line(ax + 19, a_y["+"], ax + 19, powy, color=POS, sw=1.4, dash="4 3"))
    # G рейка
    f.append(line(mx + 4, mc_y["GND"], 286, mc_y["GND"], color=INK, sw=1.6))
    f.append(line(286, mc_y["GND"], 286, gndy, color=INK, sw=1.6))
    f.append(line(24, gndy, 758, gndy, color=INK, sw=1.8))
    f.append(text(430, gndy + 18, "G  (спільна земля)", size=11, color=INK))
    f.append(line(bx + 98 + 13, b_y["G"], bx + 98 + 13, gndy, color=INK, sw=1.4, dash="4 3"))
    f.append(line(ax + 6 + 13, a_y["G"], ax + 6 + 13, gndy, color=INK, sw=1.4, dash="4 3"))

    # легенда кольорів (верхній лівий кут, поза платами)
    f.append(line(150, 66, 176, 66, color=NEG, sw=2))
    f.append(text(182, 70, "S — вихід вимикача (будь-який пін)", size=10, color=NEG, anchor="start"))
    f.append(line(150, 84, 176, 84, color=FIELD, sw=2))
    f.append(text(182, 88, "L — вхід LED (тільки ~ШІМ-пін)", size=10, color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'wiring.svg'), W, H, "".join(f))


# ── 3. Головний фокус: перелив світла зі збереженням сумарної яскравості ──────
def fig_pour():
    W, H = 760, 340
    f = []
    f.append(text(W / 2, 34, "Фокус: світло «переливається», сума стала", size=17, bold=True))

    # три стани: спокій (50/50), нахил до A (яскраво/тьмяно), нахил до B (тьмяно/яскраво)
    states = [
        (150, "спокій", 128, 128),
        (380, "нахил у бік A", 235, 20),
        (610, "нахил у бік B", 20, 235),
    ]
    baseY = 150
    for cx, cap, a, b in states:
        f.append(text(cx, 78, cap, size=13, bold=True, color=MUTED))
        # дві «чашки» = кружечки, яскравість = радіус заливки
        for dx, val, lbl in [(-46, a, "A"), (46, b, "B")]:
            # опалесценція: більше val → яскравіше (ближче до POS), радіус ореолу
            r = 10 + val / 255 * 20
            f.append(circle(cx + dx, baseY, 24, fill="#ffffff", stroke=INK, sw=1.6))
            # ореол світла
            op = 0.15 + val / 255 * 0.85
            f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f"/>'
                     % (cx + dx, baseY, r, POS, op))
            f.append(text(cx + dx, baseY + 44, lbl, size=12, bold=True))
            f.append(text(cx + dx, baseY + 62, "%d" % val, size=11, color=MUTED))
        # сумарна яскравість
        f.append(text(cx, baseY + 92, "A + B = %d" % (a + b), size=12, bold=True, color=FIELD))

    # стрілки-переливи між станами
    f.append('<line x1="228" y1="150" x2="290" y2="150" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % MUTED)
    f.append('<line x1="458" y1="150" x2="520" y2="150" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % MUTED)
    f.append(text(259, 138, "нахил", size=10, color=MUTED))
    f.append(text(489, 138, "нахил", size=10, color=MUTED))

    render(os.path.join(IMG, 'pour.svg'), W, H, "".join(f))


if __name__ == "__main__":
    fig_board()
    fig_wiring()
    fig_pour()
    print("OK: board.svg, wiring.svg, pour.svg")
