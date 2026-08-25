# -*- coding: utf-8 -*-
"""Фігури для теми «Обтискні кліщі (Dupont/JST)». Чистий Python, svgkit зі scripts/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

STEEL = "#5a6270"    # сталь інструмента
STEELF = "#c9ced6"   # світла заливка сталі
GRIP = "#c0392b"     # червона ручка
GRIPF = "#f0c9c4"
BRASS = "#b8860b"    # латунний контакт
BRASSF = "#f3e2b3"
COPPER = "#c0522a"   # мідна жила
GOOD = "#27ae60"
BAD = "#c0392b"


# ── Фігура 1: анатомія кліщів — губки, тріскачка, важіль звільнення ──────────
def fig_anatomy():
    W, H = 860, 560
    frags = []

    # дві ручки, що сходяться до шарніра праворуч
    hinge_x, hinge_y = 610, 300
    # верхня ручка
    frags.append('<path d="M %d %d L 120 200 L 150 235 L %d %d Z" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (hinge_x, hinge_y, hinge_x - 20, hinge_y - 8, GRIPF, GRIP))
    # нижня ручка
    frags.append('<path d="M %d %d L 120 400 L 150 365 L %d %d Z" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (hinge_x, hinge_y, hinge_x - 20, hinge_y + 8, GRIPF, GRIP))
    # шарнір
    frags.append(circle(hinge_x, hinge_y, 14, fill=STEELF, stroke=STEEL, sw=2))

    # голова з губками (виступає вправо-вгору від шарніра) — під кутом ~20°
    # верхня губка
    frags.append('<path d="M %d %d L 720 175 L 800 195 L 790 235 L %d %d Z" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (hinge_x + 6, hinge_y - 10, hinge_x + 6, hinge_y - 2, STEELF, STEEL))
    # нижня губка
    frags.append('<path d="M %d %d L 800 275 L 800 235 L 790 235 L %d %d Z" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (hinge_x + 6, hinge_y + 10, hinge_x + 6, hinge_y + 2, STEELF, STEEL))
    # профільовані гнізда в губках (три «зубці»-профілі)
    for i, gx in enumerate((720, 752, 784)):
        frags.append(rect(gx, 205, 14, 26, fill=BG, stroke=STEEL, sw=1.5, rx=2))

    # тріскачка — зубчаста дуга біля шарніра
    import math
    arc = ['<path d="M %.1f %.1f' % (hinge_x + 40, hinge_y - 34)]
    for k in range(9):
        a = math.radians(-40 + k * 10)
        rr = 52 + (6 if k % 2 else 0)
        arc.append('L %.1f %.1f' % (hinge_x + rr * math.cos(a), hinge_y + rr * math.sin(a)))
    arc.append('" fill="none" stroke="%s" stroke-width="2"/>' % STEEL)
    frags.append("".join(arc))

    # важіль швидкого звільнення — маленький важілець між ручок
    frags.append(rect(hinge_x - 70, hinge_y - 6, 46, 12, fill="#e8a33d", stroke=STEEL, sw=1.5, rx=4))

    # ── підписи-виноски з ЗАПАСОМ, кожен веде до своєї точки ────────────────
    def label(bx, by, s, tx, ty, bold=True):
        b, bw, bh = textbox(bx, by, s, size=12.5, pad=7, bold=bold)
        frags.append(b)
        frags.append(line(bx, by + bh / 2 if by < ty else by - bh / 2, tx, ty,
                          color=MUTED, sw=1, dash="4 3"))

    # профільовані губки — угорі праворуч
    label(700, 90, ["профільовані губки", "(гнізда під розмір)"], 752, 205)
    # тріскачка — унизу праворуч від шарніра
    label(720, 470, ["тріскачка: не пустить,", "поки не дотиснеш"], hinge_x + 52, hinge_y + 40)
    # важіль звільнення — унизу ліворуч
    label(330, 470, ["важіль звільнення —", "розтиснути достроково"], hinge_x - 47, hinge_y + 10)
    # ручки
    label(150, 110, "ручки (важіль сили)", 190, 210)

    render(os.path.join(IMG, "anatomy.svg"), W, H, *frags,
           title="Обтискні кліщі: губки, тріскачка, важіль звільнення")


# ── Фігура 2: чому профіль, а не плоска губка — B-обтиск проти «млинця» ──────
def fig_bcrimp():
    W, H = 900, 470
    frags = []

    def panel(x0, title_s):
        frags.append(text(x0 + 150, 60, title_s, size=15, bold=True))

    # ЛІВА: профільована губка загортає крила в «B»
    panel(20, "Профіль губки → B-обтиск")
    # верхня губка з увігнутим профілем (дві западинки)
    frags.append('<path d="M 60 100 L 320 100 L 320 150 '
                 'Q 250 210 190 150 Q 130 210 60 150 Z" '
                 'fill="%s" stroke="%s" stroke-width="2"/>' % (STEELF, STEEL))
    # нижня опора
    frags.append(rect(60, 250, 260, 40, fill=STEELF, stroke=STEEL, sw=2, rx=4))
    # відкритий контакт із двома крилами, що загинаються всередину до жили
    frags.append('<path d="M 150 250 Q 150 180 190 195 Q 230 180 230 250" '
                 'fill="none" stroke="%s" stroke-width="4"/>' % BRASS)
    # жила — пучок точок у центрі
    for dx, dy in ((-8, 220), (0, 214), (8, 220), (-4, 228), (4, 228)):
        frags.append(circle(190 + dx, dy, 4, fill=COPPER, stroke=BRASS, sw=1))
    frags.append(text(190, 330, "крила загорнулись досередини,", size=12.5, color=INK))
    frags.append(text(190, 350, "обняли жилу — щільно й рівномірно", size=12.5, color=INK))
    frags.append(text(190, 378, "✓ добре", size=14, color=GOOD, bold=True))

    # роздільник
    frags.append(line(W / 2, 80, W / 2, 400, color=MUTED, sw=1.5, dash="6 4"))

    # ПРАВА: плоска губка розчавлює
    panel(W / 2 + 20, "Плоска губка → «млинець»")
    fx = 560
    # плоска верхня губка
    frags.append(rect(fx, 130, 260, 34, fill=STEELF, stroke=STEEL, sw=2, rx=3))
    # плоска нижня
    frags.append(rect(fx, 250, 260, 40, fill=STEELF, stroke=STEEL, sw=2, rx=4))
    # розплющений контакт — крила розійшлись убік плазом
    frags.append('<path d="M %d 250 L %d 235 M %d 250 L %d 235" '
                 'stroke="%s" stroke-width="4" fill="none"/>'
                 % (fx + 90, fx + 55, fx + 170, fx + 205, BRASS))
    # жила видно між розчепіреними крилами
    for dx in (-6, 2, 10):
        frags.append(circle(fx + 130 + dx, 244, 4, fill=COPPER, stroke=BRASS, sw=1))
    frags.append(text(fx + 130, 330, "крила розійшлись, контакт плаский —", size=12.5, color=INK))
    frags.append(text(fx + 130, 350, "тисне нерівно, жила вільна, у корпус не сяде", size=12, color=INK))
    frags.append(text(fx + 130, 378, "✗ брак", size=14, color=BAD, bold=True))

    render(os.path.join(IMG, "bcrimp.svg"), W, H, *frags,
           title="Навіщо особлива губка: загорнути крила, а не розплющити")


# ── Фігура 3: карта гнізд — яке під що (крок · AWG) ──────────────────────────
def fig_nests():
    W, H = 900, 430
    frags = []
    frags.append(text(W / 2, 52, "Ряд гнізд на кліщах: обери за кроком і товщиною дроту",
                      size=14, color=MUTED))

    # губка як довга смуга з підписаними гніздами
    bar_x, bar_y, bar_w, bar_h = 70, 110, 760, 60
    frags.append(rect(bar_x, bar_y, bar_w, bar_h, fill=STEELF, stroke=STEEL, sw=2, rx=6))

    nests = [
        ("ZH", "1.5 мм", "28–26 AWG", "дрібний JST"),
        ("PH", "2.0 мм", "28–24 AWG", "JST PH"),
        ("XH", "2.5 мм", "28–22 AWG", "JST XH"),
        ("Dupont", "2.54 мм", "28–20 AWG", "хедери 0.1\""),
        ("VH", "3.96 мм", "22–16 AWG", "силовий JST"),
    ]
    n = len(nests)
    slot_w = bar_w / n
    for i, (name, pitch, awg, note) in enumerate(nests):
        cx = bar_x + slot_w * (i + 0.5)
        # само гніздо-проріз у смузі
        frags.append(rect(cx - 12, bar_y + 12, 24, bar_h - 24, fill=BG, stroke=STEEL, sw=1.5, rx=3))
        # підпис-картка під смугою, з запасом по ширині
        b, bw, bh = textbox(cx, 250, [name, pitch, awg], size=12.5, pad=8, bold=False, min_w=slot_w - 16)
        frags.append(b)
        frags.append(line(cx, bar_y + bar_h, cx, 250 - bh / 2, color=MUTED, sw=1, dash="3 3"))
        # дрібна нотатка ще нижче
        frags.append(text(cx, 320, note, size=11, color=MUTED))

    # легенда-стрілка «тонший ← крок → грубший»
    frags.append(text(bar_x + 60, 372, "дрібніший крок, тонший дріт", size=11.5, color=MUTED, anchor="middle"))
    frags.append(text(bar_x + bar_w - 70, 372, "більший крок, товщий дріт", size=11.5, color=MUTED, anchor="middle"))
    frags.append(arrow(bar_x + 150, 388, bar_x + bar_w - 150, 388, color=MUTED, sw=1.5))

    render(os.path.join(IMG, "nests.svg"), W, H, *frags,
           title="Карта гнізд обтискних кліщів (Dupont / JST)")


if __name__ == "__main__":
    fig_anatomy()
    fig_bcrimp()
    fig_nests()
    print("figures written to", IMG)
