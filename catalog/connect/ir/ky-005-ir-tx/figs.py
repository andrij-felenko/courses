# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def schematic():
    """Принципова схема KY-005: три піни -> посадкове місце під резистор -> ІЧ-світлодіод -> земля."""
    W, H = 720, 300
    parts = []

    # Рамка плати
    parts.append(rect(40, 60, 640, 200, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(360, 84, "плата KY-005", size=13, color=MUTED, italic=True))

    # Три піни зліва
    px = 90
    pins = [("S", 120, POS, "сигнал"), ("+", 170, INK, "живлення"), ("−", 220, NEG, "земля")]
    for lbl, py, col, cap in pins:
        parts.append(circle(px, py, 9, fill="#eef1f4", stroke=col, sw=2))
        parts.append(text(px, py + 4, lbl, size=13, color=col, bold=True))
        parts.append(text(px, py + 26, cap, size=11, color=MUTED))

    # Вузол після пінів
    node_s = 260   # лінія від S
    node_g = 220   # земля

    # S -> пляма під резистор -> анод LED
    parts.append(line(px + 9, 120, node_s, 120, color=LINE, sw=1.6))
    # посадкове місце під резистор (порожня рамка — не впаяно); підпис — НАД рамкою, поза лініями
    rbx, rby, rbw, rbh = node_s, 106, 120, 28
    parts.append(rect(rbx, rby, rbw, rbh, fill="#ffffff", stroke=MUTED, sw=1.4, rx=4))
    parts.append(text(rbx + rbw / 2, rby - 8, "місце під R (порожнє)", size=11, color=MUTED))
    # зигзаг усередині — умовний резистор (по осі y=120, у межах рамки)
    zx = rbx + 18
    zig = [zx, zx + 14, zx + 28, zx + 42, zx + 56, zx + 70, zx + 84]
    zy = [120, 113, 127, 113, 127, 113, 120]
    d = " ".join("%s%.0f,%.0f" % ("M" if i == 0 else "L", zig[i], zy[i]) for i in range(len(zig)))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (d, MUTED))

    # від резистора до світлодіода
    led_x = rbx + rbw + 60
    parts.append(line(rbx + rbw, 120, led_x - 18, 120, color=LINE, sw=1.6))

    # Символ світлодіода (трикутник + смужка + дві стрілки випромінювання)
    tx = led_x
    parts.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f z" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
                 % (tx - 16, 106, tx - 16, 134, tx + 8, 120, POS))
    parts.append(line(tx + 8, 106, tx + 8, 134, color=POS, sw=2.4))   # катодна смужка
    # стрілки випромінювання
    parts.append(arrow(tx + 2, 100, tx + 22, 82, color=POS, sw=1.6))
    parts.append(arrow(tx + 12, 104, tx + 32, 86, color=POS, sw=1.6))
    parts.append(text(tx + 40, 120, "ІЧ-світлодіод", size=11, color=INK, anchor="start"))
    parts.append(text(tx + 40, 136, "940 нм", size=11, color=INK, anchor="start"))

    # від катода LED вниз і до землі
    parts.append(line(tx + 8, 134, tx + 8, 220, color=LINE, sw=1.6))
    parts.append(line(tx + 8, 220, px + 9, 220, color=LINE, sw=1.6))   # спільна земля до піна −

    # Примітка про «+» — окремим рядком унизу, поза всіма лініями й пінами
    parts.append(text(360, 244, "контакт «+» виведено на пади; з LED внутрішньо не сполучений",
                      size=10, color=MUTED))

    render(os.path.join(IMG, "schematic.svg"), W, H, *parts)


def wiring():
    """Розводка пін-у-пін: KY-005 -> послідовний резистор -> цифровий вивід МК; земля спільна."""
    W, H = 720, 340
    parts = []

    # Ліворуч — модуль
    mbx, mby, mbw, mbh = 60, 90, 150, 170
    parts.append(rect(mbx, mby, mbw, mbh, fill="#fbfcfd", stroke=INK, sw=1.6, rx=10))
    parts.append(text(mbx + mbw / 2, mby - 12, "KY-005", size=14, color=INK, bold=True))
    m_pins = [("S", 130, POS), ("+", 175, INK), ("−", 220, NEG)]
    for lbl, py, col in m_pins:
        parts.append(circle(mbx + mbw - 14, py, 9, fill="#eef1f4", stroke=col, sw=2))
        parts.append(text(mbx + mbw - 14, py + 4, lbl, size=12, color=col, bold=True))

    # Праворуч — мікроконтролер
    cbx, cby, cbw, cbh = 500, 90, 160, 170
    parts.append(rect(cbx, cby, cbw, cbh, fill="#fbfcfd", stroke=INK, sw=1.6, rx=10))
    parts.append(text(cbx + cbw / 2, cby - 12, "мікроконтролер", size=13, color=INK, bold=True))
    c_pins = [("D3", 130, POS, "цифровий вивід"), ("5V", 175, INK, "живлення"), ("GND", 220, NEG, "земля")]
    for lbl, py, col, cap in c_pins:
        parts.append(circle(cbx + 14, py, 10, fill="#eef1f4", stroke=col, sw=2))
        parts.append(text(cbx + 14, py + 4, lbl, size=11, color=col, bold=True))
        parts.append(text(cbx + 34, py + 4, cap, size=11, color=MUTED, anchor="start"))

    sx = mbx + mbw - 5      # правий край пінів модуля
    cx = cbx + 4            # лівий край пінів МК

    # S -> послідовний резистор -> D3
    ry = 130
    parts.append(line(sx, ry, 300, ry, color=LINE, sw=1.8))
    # резистор у розриві
    rbx, rbw = 300, 110
    parts.append(rect(rbx, ry - 14, rbw, 28, fill="#ffffff", stroke=INK, sw=1.5, rx=4))
    parts.append(text(rbx + rbw / 2, ry - 20, "220 Ω  (5 В) / 120 Ω  (3.3 В)", size=11, color=INK))
    zx = rbx + 14
    zig = [zx, zx + 13, zx + 27, zx + 41, zx + 55, zx + 69, zx + 82]
    zy = [ry, ry - 8, ry + 8, ry - 8, ry + 8, ry - 8, ry]
    d = " ".join("%s%.0f,%.0f" % ("M" if i == 0 else "L", zig[i], zy[i]) for i in range(len(zig)))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, INK))
    parts.append(line(rbx + rbw, ry, cx, ry, color=LINE, sw=1.8))

    # + -> 5V  (пряма)
    parts.append(line(sx, 175, cx, 175, color=INK, sw=1.6))

    # − -> GND (спільна земля, ведемо низом, повз написи)
    parts.append(line(sx, 220, 360, 220, color=NEG, sw=1.8))
    parts.append(line(360, 220, 360, 290, color=NEG, sw=1.8))
    parts.append(line(360, 290, cx - 20, 290, color=NEG, sw=1.8))
    parts.append(line(cx - 20, 290, cx - 20, 220, color=NEG, sw=1.8))
    parts.append(line(cx - 20, 220, cx, 220, color=NEG, sw=1.8))

    # Підпис-нагадування знизу
    b = fitbox(60, 300, 240, 30, "Резистор ОБОВʼЯЗКОВИЙ — на платі його немає",
               size=11, color=POS, stroke=POS, fill="#fdecea")
    parts.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *parts)


schematic()
wiring()
print("figs done")
