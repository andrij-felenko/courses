# -*- coding: utf-8 -*-
"""Фігури до статті «Супер-чарунка» (book/electronics/analog/supermesh).
Чотири фігури:
  idea.svg      — суть: джерело струму на спільній гілці двох вікон рве закон напруг,
                  супер-чарунка обходить його по зовнішньому периметру
  why-break.svg — чому саме воно ламає: спад R·I відомий, напруга на джерелі струму — ні
  cut.svg       — обхід по периметру минає джерело: спади лише на зовнішніх резисторах
  recipe.svg    — три кроки: упізнати → обійти по периметру → додати обмеження за струмом
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ────────────────────────────────────────────────────
def resistor_h(x0, x1, y, label=None, above=True, color=INK):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 7
    out.append(line(x0, y, x0 + seg, y, color=color, sw=1.7))
    xx = x0 + seg
    prev = y
    for i in range(n):
        ny = y - amp if i % 2 == 0 else y + amp
        out.append(line(xx, prev, xx + seg, ny, color=color, sw=1.7))
        xx += seg
        prev = ny
    out.append(line(xx, prev, x1, y, color=color, sw=1.7))
    if label:
        ly = y - 16 if above else y + 22
        out.append(text((x0 + x1) / 2, ly, label, size=13, color=color, bold=True))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="right", color=INK):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    amp = 7
    out.append(line(x, y0, x, y0 + seg, color=color, sw=1.7))
    yy = y0 + seg
    prev = x
    for i in range(n):
        nx = x + amp if i % 2 == 0 else x - amp
        out.append(line(prev, yy, nx, yy + seg, color=color, sw=1.7))
        yy += seg
        prev = nx
    out.append(line(prev, yy, x, y1, color=color, sw=1.7))
    if label:
        lx = x + 16 if side == "right" else x - 16
        an = "start" if side == "right" else "end"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=13, color=color, bold=True, anchor=an))
    return "".join(out)


def battery_v(x, y0, y1, label=None, plus_top=True, color=INK):
    """Джерело напруги (батарея) вертикально: довга риска = +, коротка = −."""
    ym = (y0 + y1) / 2
    out = [line(x, y0, x, ym - 7, color=color, sw=1.7),
           line(x, ym + 7, x, y1, color=color, sw=1.7)]
    out.append(line(x - 13, ym - 7, x + 13, ym - 7, color=color, sw=2.6))   # довга +
    out.append(line(x - 7, ym - 1, x + 7, ym - 1, color=color, sw=1.7))     # коротка −
    out.append(line(x - 13, ym + 5, x + 13, ym + 5, color=color, sw=2.6))
    out.append(line(x - 7, ym + 11, x + 7, ym + 11, color=color, sw=1.7))
    ptxt, mtxt_ = ("+", "−") if plus_top else ("−", "+")
    out.append(text(x - 20, y0 + 14, ptxt, size=15, color=POS if plus_top else NEG, bold=True, anchor="end"))
    out.append(text(x - 20, y1 - 4, mtxt_, size=15, color=NEG if plus_top else POS, bold=True, anchor="end"))
    if label:
        out.append(text(x - 20, ym + 4, label, size=13, color=color, bold=True, anchor="end"))
    return "".join(out)


def isrc_v(x, y0, y1, label=None, up=True, color=INK):
    """Джерело струму вертикально: кружечок зі стрілкою (напрям струму)."""
    ym = (y0 + y1) / 2
    r = 15
    out = [line(x, y0, x, ym - r, color=color, sw=1.7),
           line(x, ym + r, x, y1, color=color, sw=1.7),
           circle(x, ym, r, fill="#ffffff", stroke=color, sw=1.8)]
    if up:
        out.append(arrow(x, ym + 9, x, ym - 9, color=NEG, sw=2.4))
    else:
        out.append(arrow(x, ym - 9, x, ym + 9, color=NEG, sw=2.4))
    if label:
        out.append(text(x + r + 8, ym + 4, label, size=13, color=NEG, bold=True, anchor="start"))
    return "".join(out)


def loop_arrow(cx, cy, r, color, label=None, cw=True, lab_dy=0):
    """Колова стрілка контурного струму (майже повне коло зі стрілкою)."""
    a0, a1 = (-50, 250) if cw else (250, -50)
    pts = []
    steps = 36
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    out = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.4" '
           'marker-end="url(#arrow)" opacity="0.9"/>' % (d, color)]
    if label:
        out.append(text(cx, cy + lab_dy + 5, label, size=15, color=color, bold=True))
    return "".join(out)


def node_dot(x, y, color=INK):
    return circle(x, y, 3.0, fill=color, stroke=color)


def two_mesh_skeleton(xL, xM, xR, yT, yB, mid="isrc", mid_label="J",
                      shared_color=POS, with_loops=True):
    """Кістяк двох вікон: V зліва, R₁ зверху-зліва, R₃ зверху-справа,
    низ — спільний провід, посередині — спільна гілка (джерело/резистор).
    Повертає список фрагментів."""
    f = []
    col = INK
    # верхні резистори
    f.append(resistor_h(xL + 18, xM - 18, yT, label="R₁", above=True))
    f.append(resistor_h(xM + 18, xR - 18, yT, label="R₃", above=True))
    # стики кутів
    f.append(line(xL, yT, xL + 18, yT, color=col, sw=1.7))
    f.append(line(xM - 18, yT, xM, yT, color=col, sw=1.7))
    f.append(line(xM, yT, xM + 18, yT, color=col, sw=1.7))
    f.append(line(xR - 18, yT, xR, yT, color=col, sw=1.7))
    # низ — спільний провід
    f.append(line(xL, yB, xR, yB, color=col, sw=1.7))
    # ліва вертикаль — джерело напруги V
    f.append(battery_v(xL, yT, yB, label="V", plus_top=True))
    # права вертикаль — простий провід (замикає праве вікно)
    f.append(line(xR, yT, xR, yB, color=col, sw=1.7))
    # середня вертикаль — спільна гілка
    if mid == "isrc":
        f.append(isrc_v(xM, yT, yB, label=mid_label, up=False, color=shared_color))
    else:
        f.append(resistor_v(xM, yT + 8, yB - 8, label=mid_label, side="right", color=shared_color))
    # вузли
    for (x, y) in [(xL, yT), (xM, yT), (xR, yT), (xL, yB), (xM, yB), (xR, yB)]:
        f.append(node_dot(x, y))
    # контурні струми
    if with_loops:
        f.append(loop_arrow((xL + xM) / 2, (yT + yB) / 2 + 4, 42, NEG, label="I₁", lab_dy=-4))
        f.append(loop_arrow((xM + xR) / 2, (yT + yB) / 2 + 4, 42, FIELD, label="I₂", lab_dy=-4))
    return f


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — біда зліва, порятунок справа
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 760, 380
    f = []

    # ── панель «біда» ──
    f.append(text(195, 40, "Біда", size=15, bold=True, color=POS))
    xL, xM, xR = 70, 200, 330
    yT, yB = 80, 230
    f += two_mesh_skeleton(xL, xM, xR, yT, yB, mid="isrc", mid_label="J")
    f.append(text(xM + 24, yB + 4, "?", size=18, color=POS, bold=True, anchor="start"))
    body, _, _ = textbox(200, 330,
                         "Напруга на джерелі струму J невідома →\nзакон напруг для вікон не записати",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)

    # роздільник
    f.append(line(W / 2, 64, W / 2, 300, color="#d6dadf", sw=1.4, dash="5 5"))

    # ── панель «порятунок» ──
    f.append(text(575, 40, "Порятунок: супер-чарунка", size=15, bold=True, color=FIELD))
    xL2, xM2, xR2 = 450, 580, 710
    # зовнішня бульбашка-периметр навколо обох вікон (без середини)
    f.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="18" fill="none" '
             'stroke="%s" stroke-width="2.4" stroke-dasharray="7 5"/>'
             % (xL2 - 26, yT - 24, (xR2 - xL2) + 52, (yB - yT) + 48, FIELD))
    f += two_mesh_skeleton(xL2, xM2, xR2, yT, yB, mid="isrc", mid_label="J", with_loops=False)
    # стрілка обходу по периметру (схематичне кільце трохи всередині бульбашки)
    f.append(loop_arrow((xL2 + xR2) / 2, (yT + yB) / 2, 92, FIELD, cw=True))
    f.append(text((xL2 + xR2) / 2, yT - 32, "обхід минає J", size=11, color=FIELD, bold=True))
    body, _, _ = textbox(580, 330,
                         "Один закон напруг по зовнішньому кільцю\n+ обмеження  I₁ − I₂ = J",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. why-break.svg — спад R·I відомий, напруга на джерелі струму невідома
# ════════════════════════════════════════════════════════════════════════════
def fig_why_break():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 34, "Чому саме джерело струму ламає обхід", size=16, bold=True))

    # ── ліворуч: резистор, спад R·I ──
    lx = 175
    yT, yB = 90, 220
    f.append(rect(lx - 120, 70, 240, 200, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=10))
    f.append(resistor_v(lx, yT, yB, label="R", side="right", color=INK))
    f.append(node_dot(lx, yT)); f.append(node_dot(lx, yB))
    f.append(arrow(lx - 30, yT + 6, lx - 30, yB - 6, color=NEG, sw=2.2))
    f.append(text(lx - 38, (yT + yB) / 2 + 4, "I", size=13, color=NEG, bold=True, anchor="end"))
    f.append(text(lx, yB + 30, "спад = R·I", size=14, color=FIELD, bold=True))
    f.append(text(lx, yB + 50, "відомий через струм", size=11, color=MUTED))

    # ── праворуч: джерело струму, напруга ? ──
    rx = 505
    f.append(rect(rx - 120, 70, 240, 200, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    f.append(isrc_v(rx, yT, yB, label="J", up=False, color=INK))
    f.append(node_dot(rx, yT)); f.append(node_dot(rx, yB))
    # дужка напруги збоку зі знаком питання
    f.append(line(rx + 44, yT, rx + 44, yB, color=POS, sw=1.6))
    f.append(line(rx + 40, yT, rx + 44, yT, color=POS, sw=1.6))
    f.append(line(rx + 40, yB, rx + 44, yB, color=POS, sw=1.6))
    f.append(text(rx + 54, (yT + yB) / 2 + 5, "U = ?", size=14, color=POS, bold=True, anchor="start"))
    f.append(text(rx, yB + 30, "спад R·J — не визначений", size=12.5, color=POS, bold=True))
    f.append(text(rx, yB + 50, "напругу нема чим підставити", size=11, color=MUTED))

    render(os.path.join(IMG, "why-break.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. cut.svg — обхід по периметру минає джерело
# ════════════════════════════════════════════════════════════════════════════
def fig_cut():
    W, H = 680, 380
    f = []
    f.append(text(W / 2, 34, "Що входить у рівняння супер-чарунки", size=16, bold=True))

    xL, xM, xR = 150, 340, 530
    yT, yB = 95, 245
    f += two_mesh_skeleton(xL, xM, xR, yT, yB, mid="isrc", mid_label="J", with_loops=False)

    # підсвітити периметр обходу (зелене кільце по зовнішніх гілках)
    perim = [(xL, yT, xR, yT), (xR, yT, xR, yB), (xR, yB, xL, yB), (xL, yB, xL, yT)]
    for (x1_, y1_, x2_, y2_) in perim:
        f.append(line(x1_, y1_, x2_, y2_, color=FIELD, sw=4.5, dash="2 0"))
    # перемалювати елементи поверх підсвітки
    f += two_mesh_skeleton(xL, xM, xR, yT, yB, mid="isrc", mid_label="J", with_loops=False)

    # галочки на зовнішніх резисторах (входять), хрестик на джерелі (ні)
    def mark(x, y, ok):
        c = FIELD if ok else POS
        s = "✓" if ok else "✕"
        fl = "#eef7f0" if ok else "#fdecea"
        return circle(x, y, 9, fill=fl, stroke=c, sw=2.0) + text(x, y + 4, s, size=12, color=c, bold=True)
    f.append(mark((xL + xM) / 2, yT, True))     # R1 на периметрі
    f.append(mark((xM + xR) / 2, yT, True))     # R3 на периметрі
    f.append(mark(xR, (yT + yB) / 2, True))     # права вітка периметра
    f.append(mark(xM, (yT + yB) / 2, False))    # джерело J — усередині

    body, _, _ = textbox(W / 2, 350,
                         "✓ спади на резисторах периметра — кожен через свій струм (I₁ чи I₂)\n"
                         "✕ джерело J лишається всередині — його напруга в суму не входить",
                         size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(body)
    render(os.path.join(IMG, "cut.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. recipe.svg — три кроки
# ════════════════════════════════════════════════════════════════════════════
def fig_recipe():
    W, H = 740, 300
    f = []
    f.append(text(W / 2, 34, "Супер-чарунка у три кроки", size=16, bold=True))

    cards = [
        ("1", "Упізнати", ["джерело струму J", "на гілці, спільній", "для двох вікон"], POS),
        ("2", "Обійти по периметру", ["один закон напруг", "по зовнішньому кільцю —", "обхід минає джерело"], FIELD),
        ("3", "Додати обмеження", ["рівняння джерела", "I₁ − I₂ = J", "(знак за напрямком)"], NEG),
    ]
    cw, ch, gap = 210, 150, 30
    x0 = (W - (3 * cw + 2 * gap)) / 2
    cy = 70
    for i, (num, title_, lines, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, cy, cw, ch, fill="#ffffff", stroke=col, sw=2.2, rx=12))
        f.append(circle(x + 26, cy + 26, 15, fill=col, stroke=col))
        f.append(text(x + 26, cy + 31, num, size=16, color="#ffffff", bold=True))
        f.append(text(x + cw / 2 + 14, cy + 31, title_, size=13.5, color=col, bold=True))
        f.append(mtext(x + cw / 2, cy + 72, lines, size=12, color=INK))
        if i < 2:
            ax = x + cw + gap / 2
            f.append(arrow(ax - 10, cy + ch / 2, ax + 10, cy + ch / 2, color=MUTED, sw=2.4))

    f.append(text(W / 2, 268,
                  "Дві невідомі (I₁, I₂) — два рівняння: закон напруг супер-чарунки + обмеження джерела",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "recipe.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_why_break()
    fig_cut()
    fig_recipe()
    print("OK: 4 фігури у", IMG)
