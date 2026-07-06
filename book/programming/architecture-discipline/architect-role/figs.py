# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')

# ── Фігура 1: сценарій якісного атрибута — шість частин ───────────────────────
def fig_scenario():
    W, H = 760, 430
    parts = []
    # шість клітин у два ряди, широкі колонки з запасом
    cells = [
        ("Джерело",   "хто/що\nстворює стимул", "клієнт застосунку"),
        ("Стимул",    "подія, на яку\nсистема має\nвідреагувати", "надходить запит"),
        ("Артефакт",  "що саме\nпід стимулом", "шлюз + сервіс цін"),
        ("Оточення",  "у якому стані\nсистема", "пік навантаження"),
        ("Відповідь", "як система\nсебе поводить", "віддає ціну"),
        ("Міра",      "чим міряємо\nуспіх", "95% за ≤ 300 мс"),
    ]
    cw, ch = 220, 128
    gapx, gapy = 30, 34
    x0 = (W - (3 * cw + 2 * gapx)) / 2
    y0 = 78
    order = [POS, INK, INK, INK, NEG, FIELD]
    for i, (name, desc, ex) in enumerate(cells):
        r, c = divmod(i, 3)
        x = x0 + c * (cw + gapx)
        y = y0 + r * (ch + gapy)
        parts.append(rect(x, y, cw, ch, fill="#f4f6f8", stroke=LINE, sw=1.5))
        parts.append(text(x + cw / 2, y + 26, name, size=16, bold=True, color=order[i]))
        parts.append(mtext(x + cw / 2, y + 50, desc, size=12.5, color=MUTED, lh=1.25))
        parts.append(line(x + 14, y + ch - 34, x + cw - 14, y + ch - 34, color="#d0d5db", sw=1))
        parts.append(text(x + cw / 2, y + ch - 14, ex, size=12.5, bold=True, color=INK))
    parts.append(text(W / 2, 42, "Один сценарій = шість відповідей", size=15, bold=True, color=INK))
    render(os.path.join(IMG, 'scenario.svg'), W, H, *parts)


# ── Фігура 2: важіль рішення — вартість зміни росте з часом ───────────────────
def fig_leverage():
    W, H = 720, 400
    parts = []
    ox, oy = 90, 320          # початок осей
    axw, axh = 560, 250
    # осі
    parts.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    parts.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    parts.append(text(ox + axw / 2, oy + 44, "час життя системи →", size=13, color=MUTED))
    # вертикальний підпис осі — трьома короткими рядками ліворуч, поза кривою
    parts.append(mtext(30, oy - axh / 2, "вартість\nзміни\nрішення", size=12, color=MUTED, lh=1.25))
    # крива вартості зміни (експонента), точками
    import math
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        x = ox + t * axw
        y = oy - (axh * 0.92) * (math.exp(2.7 * t) - 1) / (math.exp(2.7) - 1)
        pts.append("%.1f,%.1f" % (x, y))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))
    # три віхи на кривій
    def milestone(t, label, dy):
        x = ox + t * axw
        y = oy - (axh * 0.92) * (math.exp(2.7 * t) - 1) / (math.exp(2.7) - 1)
        out = circle(x, y, 5, fill=BG, stroke=INK, sw=1.8)
        return out, x, y
    m1, x1, y1 = milestone(0.06, "", 0)
    m2, x2, y2 = milestone(0.5, "", 0)
    m3, x3, y3 = milestone(0.9, "", 0)
    parts += [m1, m2, m3]
    # підписи-віхи у власних рамках, розставлені з запасом, лінії ведуть повз написи
    b1 = fitbox(ox + 12, oy - axh - 4, 210, 48, "на старті: дешево\nобрати інакше", size=12.5, fill="#eaf0fd", stroke=NEG, color=NEG)
    parts.append(b1)
    parts.append(line(x1, y1, ox + 60, oy - axh + 44, color=NEG, sw=1.2, dash="4,3"))
    b2 = fitbox(ox + axw / 2 - 95, oy - 118, 200, 46, "у середині: боляче,\nале ще можливо", size=12.5, fill="#f4f6f8", stroke=LINE, color=INK)
    parts.append(b2)
    parts.append(line(x2, y2, ox + axw / 2, oy - 118 + 46, color=LINE, sw=1.2, dash="4,3"))
    b3 = fitbox(ox + axw - 240, oy - 92, 232, 46, "наприкінці: майже\nнеможливо, дорого", size=12.5, fill="#fdecea", stroke=POS, color=POS)
    parts.append(b3)
    parts.append(line(x3, y3, ox + axw - 60, oy - 92 + 46, color=POS, sw=1.2, dash="4,3"))
    parts.append(text(W / 2, 34, "Раннє рішення важить найбільше", size=16, bold=True, color=INK))
    render(os.path.join(IMG, 'leverage.svg'), W, H, *parts)


# ── Фігура 3: одне рішення тягне атрибути в різні боки (компроміс) ─────────────
def fig_tradeoff():
    W, H = 720, 400
    parts = []
    cx, cy = W / 2, 214
    # центральне рішення
    bd, bw, bh = textbox(cx, cy, "Рішення:\nкешувати ціни", size=14, bold=True,
                         fill="#fff7e6", stroke="#b8860b", sw=2, pad=14)
    # спиці до атрибутів: + (виграш) і − (програш), розставлені по колу з запасом
    # gain=True → зелена рамка + плюс; gain=False → синя рамка + мінус
    spokes = [
        (True,  "Продуктивність", "менше запитів\nдо бази", -250, -130),
        (True,  "Вартість",       "менше обчислень\nна кожен запит", -250, 130),
        (False, "Свіжість",       "клієнт бачить\nстару ціну", 250, -130),
        (False, "Складність",     "інвалідація кешу —\nвічна морока", 250, 130),
    ]
    for gain, name, why, dx, dy in spokes:
        tx, ty = cx + dx, cy + dy
        # спиця від краю центральної рамки
        edge_x = cx + (bw / 2 if dx > 0 else -bw / 2)
        parts.append(line(edge_x, cy, tx + (-70 if dx > 0 else 70), ty, color="#c4c9d0", sw=1.6))
        b = fitbox(tx - 108, ty - 30, 216, 60, name + "\n" + why, size=12.5,
                   fill=("#eaf7ee" if gain else "#eaf0fd"),
                   stroke=(FIELD if gain else NEG), color=INK)
        parts.append(b)
        # значок + / − на спиці, ближче до центра, поза рамками
        mk_x = cx + (0.42 * dx)
        mk_y = cy + (0.42 * dy)
        parts.append(plus(mk_x, mk_y, 11) if gain else minus(mk_x, mk_y, 11))
    parts.append(bd)
    parts.append(text(W / 2, 34, "Одне рішення — і виграш, і плата", size=16, bold=True, color=INK))
    parts.append(text(W / 2, H - 18, "точка компромісу: тягне кілька атрибутів у різні боки",
                      size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, 'tradeoff.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_scenario()
    fig_leverage()
    fig_tradeoff()
    print("figures written")
