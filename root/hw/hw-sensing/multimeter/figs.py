# -*- coding: utf-8 -*-
"""Фігури до теми «Мультиметр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Колірна угода (§5): червоний/POS = «+», червоний щуп, небезпека;
синій/NEG = вольтметр; зелений/FIELD = омметр та «добре»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math

ORANGE = "#e08030"   # попередження (гніздо/запобіжник)
WIRE   = "#cf8b5e"   # колір дроту в схемах


# ── допоміжне: батарея (вертикальна, з підписом) ──────────────────────────────
def battery(x, ytop, ybot, label="9 В", sw=2.2):
    """Вертикальний дріт батареї x:[ytop..ybot] з парою пластин і підписом зліва."""
    ymid = (ytop + ybot) / 2
    f = [line(x, ytop, x, ymid - 8, color=INK, sw=sw),
         line(x, ymid + 8, x, ybot, color=INK, sw=sw),
         line(x - 16, ymid - 8, x + 16, ymid - 8, color=INK, sw=3),   # довга пластина (+)
         line(x - 9, ymid + 8, x + 9, ymid + 8, color=INK, sw=5),     # коротка пластина (−)
         text(x - 24, ymid + 3, label, size=10, color=INK, anchor="end", bold=True)]
    return f


def resistor(x, y, w, h, label="R", lx=None, anchor="start", italic=True):
    """Прямокутник-резистор (вертикальний), підпис збоку."""
    if lx is None:
        lx = x + w + 6
    f = [rect(x, y, w, h, fill=BG, stroke=INK, sw=2, rx=3),
         text(lx, y + h / 2 + 4, label, size=12, color=INK, anchor=anchor, bold=True, italic=italic)]
    return f


def resistor_h(x, y, w, h, label="R"):
    """Горизонтальний резистор: прямокутник по центру лінії y, з підписом зверху."""
    rx0 = x + (w - 46) / 2
    return [rect(rx0, y - h / 2, 46, h, fill=BG, stroke=INK, sw=2, rx=3),
            line(x, y, rx0, y, color=INK, sw=2),
            line(rx0 + 46, y, x + w, y, color=INK, sw=2),
            text(x + w / 2, y - h / 2 - 6, label, size=11, color=INK, bold=True, italic=True)]


def node(x, y, color=INK, r=3.5):
    return circle(x, y, r, fill=color, stroke=color, sw=1)


# ── 1. Огляд: тіло мультиметра ────────────────────────────────────────────────
def fig_overview():
    W, H = 820, 400
    f = [text(W / 2, 52, "перемикач обирає режим; щупи — червоний у «+», чорний у COM (земля)",
              size=11, color=MUTED, italic=True)]

    # корпус
    f.append(rect(300, 80, 240, 290, fill="#f0f2f5", stroke="#9aa3ad", sw=2.2, rx=16))
    # дисплей
    f.append(rect(330, 100, 180, 56, fill="#1c2b1c", stroke=INK, sw=2, rx=6))
    f.append(text(420, 140, "5.00 V", size=26, color="#7CFC7C", bold=True))

    # поворотний перемикач
    cx, cy, R = 420, 235, 60
    f.append(circle(cx, cy, R, fill=BG, stroke=INK, sw=2.4))
    f.append(circle(cx, cy, 6, fill=INK, stroke=INK, sw=1))

    # позначки режимів навколо (кут, підпис) — мітки на радіусі rl, риски на колі
    rt, rl = R - 14, R + 16
    modes = [
        (90,  "V⎓"),    # верх
        (45,  "V~"),    # верх-право
        (0,   "Ω"),     # право
        (-45, "A"),     # низ-право
        (-90, "•))"),   # низ
        (180, "OFF"),   # ліво
    ]
    for ang, lbl in modes:
        a = math.radians(ang)
        dx, dy = math.cos(a), -math.sin(a)
        f.append(line(cx + dx * 14, cy + dy * 14, cx + dx * rt, cy + dy * rt,
                      color="#cfcfcf", sw=1.4))
        f.append(text(cx + dx * rl, cy + dy * rl + 4, lbl, size=11, color=INK, bold=True))
    # стрілка перемикача вказує на V⎓ (верх)
    f.append(line(cx, cy, cx, cy - (R - 16), color=POS, sw=3))

    # три гнізда
    jacks = [(355, "COM", INK), (420, "VΩmA", POS), (485, "10A", POS)]
    for jx, lbl, col in jacks:
        f.append(circle(jx, 348, 8, fill=BG, stroke=col, sw=2))
        f.append(text(jx, 368, lbl, size=9, color=col, bold=True))

    # червоний щуп від VΩmA назовні
    f.append(line(420, 348, 660, 150, color=POS, sw=2.6))
    f.append(node(660, 150, color=POS))
    f.append(text(620, 140, "червоний", size=10, color=POS, bold=True))

    # чорний щуп від COM назовні
    f.append(line(355, 348, 150, 200, color=INK, sw=2.6))
    f.append(node(150, 200, color=INK))
    f.append(text(180, 190, "чорний (COM)", size=10, color=INK, bold=True))

    render(os.path.join(IMG, "overview.svg"), W, H, *f,
           title="Мультиметр: один прилад на V, A, Ω (і не тільки)")


# ── 2. Напруга — паралельно ───────────────────────────────────────────────────
def fig_voltage():
    W, H = 820, 340
    f = [text(W / 2, 52, "щупи прикладають до двох точок, не розриваючи коло; прилад високоомний",
              size=11, color=MUTED, italic=True)]

    # коло: батарея зліва, R справа
    f += battery(120, 140, 280, "9 В")
    f.append(line(120, 140, 400, 140, color="#cf8b5e", sw=2.4))   # верхній дріт
    f.append(line(120, 280, 400, 280, color="#cf8b5e", sw=2.4))   # нижній дріт
    f += resistor(388, 165, 24, 90, "R", lx=418, anchor="start")
    f.append(line(400, 140, 400, 165, color="#cf8b5e", sw=2.4))
    f.append(line(400, 255, 400, 280, color="#cf8b5e", sw=2.4))

    # вольтметр ПАРАЛЕЛЬНО R
    vcx, vcy, vr = 560, 210, 26
    f.append(circle(vcx, vcy, vr, fill=BG, stroke=NEG, sw=2.4))
    f.append(text(vcx, vcy + 7, "V", size=24, color=NEG, bold=True))
    # червоний щуп до верхнього вузла
    f.append(line(vcx, vcy - vr, 405, 150, color=POS, sw=2.6))
    f.append(node(405, 150, color=POS))
    # чорний щуп до нижнього вузла
    f.append(line(vcx, vcy + vr, 405, 270, color=INK, sw=2.6))
    f.append(node(405, 270, color=INK))

    # рамка-нотатка (без §-посилань)
    f.append(fitbox(160, 300, 500, 34,
                    "Високий опір вольтметра майже не відбирає струму — коло лишається незмінним.",
                    size=11, pad=10, fill="#eaf0fb", stroke=NEG, bold=True))

    render(os.path.join(IMG, "voltage.svg"), W, H, *f,
           title="Напругу міряють ПАРАЛЕЛЬНО")


# ── 3. Струм — послідовно (в розрив) ──────────────────────────────────────────
def fig_current():
    W, H = 820, 340
    f = [text(W / 2, 52, "коло розривають і вмикають прилад у розрив; він малоомний",
              size=11, color=MUTED, italic=True)]

    f += battery(120, 140, 280, "9 В")
    # верхній дріт іде до точки розриву
    f.append(line(120, 140, 300, 140, color="#cf8b5e", sw=2.4))
    f.append(node(300, 140))
    # розрив: дроти йдуть угору до амперметра
    f.append(line(300, 140, 380, 110, color=INK, sw=2.6))
    f.append(node(380, 110))

    acx, acy, ar = 430, 110, 24
    f.append(circle(acx, acy, ar, fill=BG, stroke=POS, sw=2.4))
    f.append(text(acx, acy + 7, "A", size=23, color=POS, bold=True))
    f.append(line(480, 110, 560, 140, color=POS, sw=2.6))
    f.append(node(560, 140, color=POS))
    f.append(node(560, 140))

    # далі до R і назад
    f.append(line(560, 140, 660, 140, color="#cf8b5e", sw=2.4))
    f += resistor(648, 165, 24, 90, "R", lx=642, anchor="end")
    f.append(line(660, 140, 660, 165, color="#cf8b5e", sw=2.4))
    f.append(line(660, 255, 660, 280, color="#cf8b5e", sw=2.4))
    f.append(line(120, 280, 660, 280, color="#cf8b5e", sw=2.4))

    f.append(text(430, 160, "увімкнено В РОЗРИВ", size=10, color=POS, bold=True))

    # рамка-попередження (помаранчева)
    f.append(fitbox(150, 300, 520, 34,
                    "Малий опір амперметра майже не заважає струму. Не забудьте правильне гніздо (mA чи 10A)!",
                    size=11, pad=10, fill="#fff3e8", stroke=ORANGE, bold=True))

    render(os.path.join(IMG, "current.svg"), W, H, *f,
           title="Струм міряють ПОСЛІДОВНО (розірвавши коло)")


# ── 4. Опір — на знеструмленому елементі ──────────────────────────────────────
def fig_resistance():
    W, H = 820, 340
    f = [text(W / 2, 52, "живлення вимкнено, деталь краще вийняти з кола; прилад сам пускає малий струм",
              size=11, color=MUTED, italic=True)]

    # ізольований резистор з короткими «вусами»
    f.append(rect(330, 147, 90, 26, fill=BG, stroke=INK, sw=2, rx=3))
    f.append(text(375, 139, "R = ?", size=12, color=INK, bold=True, italic=True))
    f.append(line(290, 160, 330, 160, color="#cf8b5e", sw=2.2))
    f.append(line(420, 160, 460, 160, color="#cf8b5e", sw=2.2))

    # омметр
    ocx, ocy, orr = 375, 250, 24
    f.append(circle(ocx, ocy, orr, fill=BG, stroke=FIELD, sw=2.4))
    f.append(text(ocx, ocy + 7, "Ω", size=23, color=FIELD, bold=True))
    # червоний + чорний щуп до кінців R
    f.append(line(355, 232, 300, 175, color=POS, sw=2.6))
    f.append(node(300, 175, color=POS))
    f.append(line(395, 232, 450, 175, color=INK, sw=2.6))
    f.append(node(450, 175, color=INK))

    # зелена інфо-рамка про прозвонку (праворуч)
    f.append(rect(540, 120, 250, 130, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(665, 146, "Режим «прозвонка» •))", size=12, color=FIELD, bold=True))
    f.append(text(560, 174, "пищить, якщо опір ≈ 0", size=10, color=INK, anchor="start"))
    f.append(text(560, 196, "(є з'єднання) — швидко", size=10, color=INK, anchor="start"))
    f.append(text(560, 218, "перевіряти дроти й доріжки", size=10, color=INK, anchor="start"))

    # червона рамка-попередження знизу
    f.append(fitbox(120, 296, 580, 36,
                    "НІКОЛИ не міряйте опір на ввімкненому колі — чужа напруга зіб'є показ і може зашкодити приладу.",
                    size=10, pad=10, fill="#fbecea", stroke=POS, bold=True))

    render(os.path.join(IMG, "resistance.svg"), W, H, *f,
           title="Опір — на ЗНЕСТРУМЛЕНОМУ елементі")


# ── 5. Дві небезпечні помилки ─────────────────────────────────────────────────
def fig_mistakes():
    W, H = 820, 360
    f = [text(W / 2, 52, "найчастіші — і найприкріші: вони псують запобіжник або прилад",
              size=11, color=MUTED, italic=True)]

    # вертикальний пунктирний розділювач
    f.append(line(410, 76, 410, 320, color="#e4e4e4", sw=1.4, dash="4,5"))

    # ── ЛІВО: амперметр у паралель = майже КЗ ──
    f.append(text(210, 104, "Амперметр у ПАРАЛЕЛЬ", size=12, color=POS, bold=True))
    f += battery(110, 140, 250, "9 В", sw=2.2)
    f.append(line(110, 140, 250, 140, color="#cf8b5e", sw=2.2))
    f.append(line(110, 250, 250, 250, color="#cf8b5e", sw=2.2))
    f.append(line(250, 140, 250, 250, color="#cf8b5e", sw=2.2))
    acx, acy, ar = 310, 195, 22
    f.append(circle(acx, acy, ar, fill=BG, stroke=POS, sw=2.4))
    f.append(text(acx, acy + 6, "A", size=21, color=POS, bold=True))
    f.append(line(acx, acy - ar, 252, 145, color=POS, sw=2.6))
    f.append(node(252, 145, color=POS))
    f.append(line(acx, acy + ar, 252, 245, color=INK, sw=2.6))
    f.append(node(252, 245, color=INK))
    f.append(text(210, 285, "малий опір = майже КЗ →", size=10, color=POS, bold=True))
    f.append(text(210, 303, "величезний струм, ЗАПОБІЖНИК згоряє", size=10, color=INK, bold=True))

    # ── ПРАВО: омметр на живому колі ──
    f.append(text(610, 104, "Омметр на ЖИВОМУ колі", size=12, color=POS, bold=True))
    f += battery(500, 140, 250, "9 В", sw=2.2)
    f.append(line(500, 140, 680, 140, color="#cf8b5e", sw=2.2))
    f += resistor(668, 160, 24, 70, "R", lx=662, anchor="end")
    f.append(line(680, 140, 680, 160, color="#cf8b5e", sw=2.2))
    f.append(line(680, 230, 680, 250, color="#cf8b5e", sw=2.2))
    f.append(line(500, 250, 680, 250, color="#cf8b5e", sw=2.2))
    ocx, ocy, orr = 600, 300, 20
    f.append(circle(ocx, ocy, orr, fill=BG, stroke=FIELD, sw=2.4))
    f.append(text(ocx, ocy + 6, "Ω", size=19, color=FIELD, bold=True))
    f.append(line(582, 286, 510, 145, color=POS, sw=2.6))
    f.append(node(510, 145, color=POS))
    f.append(line(618, 286, 680, 200, color=INK, sw=2.6))
    f.append(node(680, 200, color=INK))
    f.append(text(610, 333, "чужа напруга → хибний показ, ризик шкоди", size=10, color=POS, bold=True))

    render(os.path.join(IMG, "mistakes.svg"), W, H, *f,
           title="Дві небезпечні помилки")


# ── 6. Блок-схема DMM: усе зводиться до напруги ────────────────────────────────
def fig_blockdiagram():
    W, H = 920, 470
    f = [text(W / 2, 52, "вхідний каскад залежить від режиму; далі тракт спільний для всіх",
              size=12, color=MUTED, italic=True)]

    # гнізда ліворуч
    jx = 64
    f.append(text(jx, 96, "Гнізда", size=12, color=INK, bold=True))
    f.append(circle(jx, 128, 9, fill=BG, stroke=POS, sw=2.4))
    f.append(text(jx + 18, 132, "VΩmA", size=11, color=POS, anchor="start", bold=True))
    f.append(circle(jx, 200, 9, fill=BG, stroke=ORANGE, sw=2.4))
    f.append(text(jx + 18, 204, "10A", size=11, color=ORANGE, anchor="start", bold=True))
    f.append(circle(jx, 312, 9, fill=BG, stroke=INK, sw=2.4))
    f.append(text(jx + 18, 316, "COM", size=11, color=INK, anchor="start", bold=True))
    f.append(text(jx, 342, "опорна точка", size=10, color=MUTED))

    # каскади обробки за режимом
    bx, bw = 184, 200
    f.append(text(bx + bw / 2, 90, "вибирає перемикач режиму", size=10, color=MUTED, italic=True))
    blocks = [
        (104, NEG,   "#eef3fb", "Режим V — дільник", "вхід ≈ 10 МОм"),
        (178, POS,   "#fdeeee", "Режим A — шунт", "малий опір, спад напруги"),
        (252, FIELD, "#eef7f0", "Режим Ω — джерело I", "пускає струм, міряє спад"),
    ]
    for yy, col, fillc, t1, t2 in blocks:
        f.append(rect(bx, yy, bw, 54, fill=fillc, stroke=col, sw=1.6, rx=8))
        f.append(text(bx + bw / 2, yy + 23, t1, size=11, color=col, bold=True))
        f.append(text(bx + bw / 2, yy + 41, t2, size=10, color=MUTED))
    f.append(line(jx + 9, 128, bx, 128, color=POS, sw=2))
    f.append(line(jx + 9, 200, bx, 200, color=ORANGE, sw=2))

    # опорна напруга + АЦП
    mx = 440
    f.append(arrow(bx + bw, 131, mx, 188, color=INK, sw=1.8))
    f.append(arrow(bx + bw, 205, mx, 200, color=INK, sw=1.8))
    f.append(arrow(bx + bw, 279, mx, 212, color=INK, sw=1.8))
    f.append(rect(mx, 100, 156, 44, fill="#f7f7f7", stroke=MUTED, sw=1.4, rx=6))
    f.append(text(mx + 78, 121, "Опорна напруга", size=11, color=INK, bold=True))
    f.append(text(mx + 78, 137, "еталон для порівняння", size=10, color=MUTED))
    f.append(arrow(mx + 78, 144, mx + 78, 166, color=MUTED, sw=1.6))
    f.append(rect(mx, 166, 156, 76, fill=BG, stroke=INK, sw=2, rx=8))
    f.append(text(mx + 78, 196, "АЦП", size=15, color=INK, bold=True))
    f.append(text(mx + 78, 216, "напруга → число", size=10, color=MUTED))
    f.append(text(mx + 78, 264, "інтегрувальний (dual-slope)", size=10, color=MUTED))
    f.append(text(mx + 78, 280, "або сигма-дельта", size=10, color=MUTED))

    # табло
    dx = 658
    f.append(arrow(mx + 156, 204, dx, 204, color=INK, sw=2))
    f.append(rect(dx, 166, 162, 84, fill="#101814", stroke="#101814", sw=2, rx=8))
    f.append(text(dx + 81, 220, "4.236", size=30, color="#5dff9b", bold=True))
    f.append(text(dx + 81, 272, "табло (лічильник + дисплей)", size=10, color=MUTED))

    f.append(fitbox(130, 396, 660, 54,
                    ["Головна ідея: цифрувати прилад уміє лише НАПРУГУ.",
                     "Струм і опір він спершу обертає на напругу — шунтом чи джерелом струму — і вже її злічує."],
                    size=11, pad=10, fill="#f3f6fb", stroke=NEG, bold=False))

    render(os.path.join(IMG, "blockdiagram.svg"), W, H, *f,
           title="Що всередині DMM: будь-яку величину звести до напруги")


# ── 7. Два числа з паспорта: вхідний опір і напруга навантаження ───────────────
def fig_impedance():
    W, H = 900, 470
    f = [line(450, 70, 450, H - 20, color="#e4e4e4", sw=2)]

    # ── ЛІВОРУЧ: вольтметр 10 МОм паралельно ──
    f.append(text(228, 84, "Вольтметр — 10 МОм у паралель", size=13, color=NEG, bold=True))
    f.append(rect(44, 140, 42, 46, fill=BG, stroke=POS, sw=1.8, rx=4))
    f.append(text(65, 168, "Uвх", size=11, color=POS, bold=True))
    f.append(line(86, 163, 156, 163, color=INK, sw=2))
    f += resistor_h(156, 163, 70, 22, "Rдж")
    f.append(line(226, 163, 300, 163, color=INK, sw=2))
    f.append(node(300, 163))
    f.append(text(300, 150, "вузол", size=10, color=MUTED))
    f.append(line(300, 163, 300, 236, color=INK, sw=2))
    f.append(circle(300, 260, 23, fill=BG, stroke=NEG, sw=2))
    f.append(text(300, 258, "V", size=15, color=NEG, bold=True))
    f.append(text(300, 274, "10 МОм", size=9, color=MUTED))
    f.append(line(300, 283, 300, 320, color=INK, sw=2))
    f.append(line(282, 320, 318, 320, color=INK, sw=2))
    f.append(line(288, 326, 312, 326, color=INK, sw=2))
    f.append(line(294, 332, 306, 332, color=INK, sw=2))
    f.append(rect(40, 356, 388, 96, fill="#f3f6fb", stroke=NEG, sw=1.4, rx=8))
    f.append(text(234, 379, "10 МОм майже не відбирають струму — але:", size=11, color=INK, bold=True))
    f.append(text(60, 402, "Rдж = 1 кОм → похибка ≈ 0.01 %", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(60, 424, "Rдж = 1 МОм → показ занижений на ~9 %", size=11, color=POS, anchor="start", bold=True))
    f.append(text(60, 443, "на високоомних вузлах ефект відчутний", size=10, color=MUTED, anchor="start", italic=True))

    # ── ПРАВОРУЧ: амперметр — шунт послідовно ──
    f.append(text(678, 84, "Амперметр — шунт послідовно", size=13, color=POS, bold=True))
    f.append(rect(492, 190, 42, 46, fill=BG, stroke=POS, sw=1.8, rx=4))
    f.append(text(513, 218, "3.3 В", size=10, color=POS, bold=True))
    f.append(line(513, 190, 513, 163, color=INK, sw=2))
    f.append(line(513, 163, 562, 163, color=INK, sw=2))
    f.append(circle(587, 163, 23, fill=BG, stroke=POS, sw=2))
    f.append(text(587, 169, "A", size=15, color=POS, bold=True))
    f.append(text(587, 132, "шунт усередині", size=10, color=MUTED))
    f.append(text(587, 210, "спад Uнав ≈ 0.2 В", size=10, color=POS, bold=True))
    f.append(line(610, 163, 682, 163, color=INK, sw=2))
    f += resistor_h(682, 163, 80, 22, "Rнав")
    f.append(line(762, 163, 822, 163, color=INK, sw=2))
    f.append(line(822, 163, 822, 282, color=INK, sw=2))
    f.append(line(822, 282, 513, 282, color=INK, sw=2))
    f.append(line(513, 282, 513, 236, color=INK, sw=2))
    f.append(rect(494, 356, 378, 96, fill="#fdeeee", stroke=POS, sw=1.4, rx=8))
    f.append(text(683, 379, "Амперметр «краде» трохи напруги:", size=11, color=INK, bold=True))
    f.append(text(514, 402, "A-діапазон — десятки мВ (дрібниця)", size=11, color=MUTED, anchor="start"))
    f.append(text(514, 424, "µA/mA — сотні мВ: коло 3.3 В це відчує", size=11, color=POS, anchor="start", bold=True))
    f.append(text(514, 443, "тому надовго в розрив амперметр не лишають", size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "impedance.svg"), W, H, *f,
           title="Прилад не «безкоштовний»: вхідний опір і спад на шунті")


# ── 8. Counts і цифри: скільки знаків видно ────────────────────────────────────
def fig_counts():
    W, H = 900, 410
    f = [text(W / 2, 52, "та сама напруга ≈ 4.2361 В на табло різної роздільності",
              size=12, color=MUTED, italic=True)]
    cards = [
        (60,  "Кишеньковий", "2000 counts · 3½ цифри", "4.23", "крок 10 мВ", MUTED),
        (330, "Польовий", "6000 counts · 3¾ цифри", "4.236", "крок 1 мВ", NEG),
        (600, "Лабораторний", "6½ цифри (1199999)", "4.23612", "крок 10 мкВ", FIELD),
    ]
    for x, ttl, spec, val, step, col in cards:
        f.append(rect(x, 80, 240, 156, fill="#fafafa", stroke=col, sw=1.6, rx=10))
        f.append(text(x + 120, 106, ttl, size=13, color=col, bold=True))
        f.append(text(x + 120, 125, spec, size=10, color=MUTED))
        f.append(rect(x + 30, 140, 180, 52, fill="#101814", stroke="#101814", sw=2, rx=6))
        f.append(text(x + 120, 176, val, size=26, color="#5dff9b", bold=True))
        f.append(text(x + 120, 213, step + "  (В)", size=11, color=INK, bold=True))
    f.append(fitbox(120, 260, 660, 120,
                    ["Counts — найбільше число, що влазить на табло (2000 → до 1999).",
                     "Більше counts чи цифр = дрібніший крок = більше значущих знаків.",
                     "Автодіапазон сам обирає найменший діапазон, де число влазить,",
                     "щоб лишилося найбільше корисних цифр (4.236, а не 04.23).",
                     "«Точність» (±%) — це інше: межа правдивості показу, не його дрібність."],
                    size=11, pad=12, fill="#f7f7f7", stroke=MUTED, bold=False))

    render(os.path.join(IMG, "counts.svg"), W, H, *f,
           title="Counts і цифри вирішують, скільки знаків ви бачите")


if __name__ == "__main__":
    fig_overview()
    fig_voltage()
    fig_current()
    fig_resistance()
    fig_mistakes()
    fig_blockdiagram()
    fig_impedance()
    fig_counts()
    print("OK: 8 figures ->", IMG)
