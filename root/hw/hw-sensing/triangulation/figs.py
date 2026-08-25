# -*- coding: utf-8 -*-
"""Фігури до теми «Тріангуляція» (book/electronics/sensors).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Принцип: положення плями кодує кут, кут — відстань ────────────────────
def fig_geometry():
    W, H = 720, 340
    f = [text(W / 2, 28, "Тріангуляція: відстань із кута, під яким вернувся промінь", size=16, bold=True)]

    # давач ліворуч: світлодіод (зверху) і лінза+приймач (знизу), рознесені на базу
    ledx, ledy = 95, 175
    lensx, lensy = 95, 250
    f.append(rect(ledx - 13, ledy - 17, 26, 34, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>'
             % (ledx + 13, ledy - 5, ledx + 24, ledy, ledx + 13, ledy + 5, POS))
    f.append(text(ledx, ledy - 24, "ІЧ-світлодіод", size=11, color=INK, bold=True))
    f.append('<ellipse cx="%.0f" cy="%.0f" rx="7" ry="22" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (lensx, lensy, NEG))
    f.append(text(lensx - 18, lensy + 38, "лінза + приймач", size=11, color=NEG, bold=True))

    # база між світлодіодом і приймачем
    f.append(line(ledx, ledy + 18, lensx, lensy - 24, color=MUTED, sw=1.3, dash="3,3"))
    f.append(text(ledx - 16, (ledy + lensy) / 2, "база b", size=11, color=MUTED, anchor="end", italic=True))

    # промінь до цілей
    f.append(arrow(ledx + 26, ledy, 600, ledy, color=POS, sw=2.0))
    f.append(text(360, ledy - 10, "промінь →", size=11, color=POS, bold=True))

    # ближча ціль (зелена) і дальша (червона)
    f.append(rect(360, ledy - 26, 12, 52, fill="#eee", stroke=FIELD, sw=1.8))
    f.append(text(366, ledy - 34, "ближча", size=11, color=FIELD, bold=True))
    f.append(rect(560, ledy - 22, 12, 44, fill="#eee", stroke=POS, sw=1.6))
    f.append(text(566, ledy + 40, "дальша", size=11, color=POS, bold=True))

    # відбиті промені назад до лінзи під різними кутами
    f.append(arrow(360, ledy + 8, lensx + 7, lensy - 8, color=FIELD, sw=1.8))
    f.append(arrow(560, ledy + 8, lensx + 7, lensy - 6, color=POS, sw=1.8))

    # дві плями на приймачі (різні місця)
    f.append(circle(lensx - 26, lensy + 14, 4, fill=FIELD, stroke="none", sw=1))
    f.append(circle(lensx - 26, lensy + 2, 4, fill=POS, stroke="none", sw=1))
    f.append(text(lensx - 34, lensy - 4, "пляма: близько ≠ далеко", size=10.5, color=INK, anchor="end", italic=True))

    f.append(text(W / 2, 318, "положення плями кодує кут, а кут — відстань · часу міряти не треба",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "geometry.svg"), W, H, *f)


# ── 2. Подібні трикутники дають d = f·b/x ────────────────────────────────────
def fig_similar_triangles():
    W, H = 660, 320
    f = [text(W / 2, 28, "Подібні трикутники: d = f · b / x", size=16, bold=True)]

    # великий трикутник: вершина в цілі, основа — база на давачі
    apex_x, apex_y = 560, 120
    b_top, b_bot = 170, 240
    bx = 95
    f.append(line(bx, b_bot, bx, b_top, color=INK, sw=2.2))
    f.append(text(bx - 12, (b_top + b_bot) / 2, "b", size=14, color=INK, anchor="end", bold=True))
    f.append(line(bx, b_bot, apex_x, apex_y, color=FIELD, sw=2.0))
    f.append(line(bx, b_top, apex_x, apex_y, color=FIELD, sw=2.0))
    f.append(line(bx, b_bot, apex_x, b_bot, color=INK, sw=1.4, dash="4,3"))
    f.append(text((bx + apex_x) / 2, b_bot + 22, "відстань d", size=12, color=INK, bold=True))
    f.append(rect(apex_x, apex_y - 12, 12, b_bot - apex_y + 12, fill="#eee", stroke=INK, sw=1.3))
    f.append(text(apex_x + 6, apex_y - 18, "ціль", size=11, color=INK, bold=True))

    # малий трикутник усередині давача
    f.append(rect(130, 95, 140, 90, fill="#fbfbfb", stroke="#e4e4e4", sw=1.0, rx=6))
    f.append(text(200, 110, "усередині давача", size=10.5, color=MUTED, italic=True))
    sx, sy = 150, 168
    f.append(line(sx, sy, sx, sy - 26, color=INK, sw=1.8))
    f.append(text(sx - 8, sy - 12, "x", size=12, color=INK, anchor="end", bold=True))
    f.append(line(sx, sy, sx + 100, sy, color=INK, sw=1.8))
    f.append(text(sx + 50, sy + 16, "f", size=12, color=INK, bold=True))
    f.append(line(sx, sy - 26, sx + 100, sy, color=NEG, sw=1.8))

    b2, _, _ = textbox(W / 2, 296, "d / b = f / x   ⇒   d = f · b / x   (обернено: d ∝ 1/x)",
                       size=14, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b2)
    render(os.path.join(IMG, "similar-triangles.svg"), W, H, *f)


# ── 3. Будова: світлодіод, лінза, позиційний приймач, мерехтіння ────────────
def fig_anatomy():
    W, H = 720, 260
    f = [text(W / 2, 28, "Будова ІЧ-далекоміра: світлодіод, лінза, позиційний приймач", size=15, bold=True)]

    # корпус давача
    f.append(rect(45, 80, 150, 120, fill="#fbfbfb", stroke=MUTED, sw=1.3, rx=8))
    f.append(text(120, 70, "давач", size=11, color=MUTED, italic=True))

    # світлодіод
    f.append(rect(68, 105, 22, 30, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append('<polygon points="90,115 100,120 90,125" fill="%s"/>' % POS)
    f.append(text(79, 154, "ІЧ-світлодіод", size=10, color=POS, bold=True))
    f.append(text(79, 167, "мерехтить", size=10, color=MUTED, italic=True))

    # лінза + PSD
    f.append('<ellipse cx="160" cy="162" rx="7" ry="22" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>' % NEG)
    f.append(text(160, 196, "лінза + приймач (PSD)", size=10, color=NEG, bold=True))

    # ціль
    f.append(rect(560, 70, 16, 130, fill="#eee", stroke=INK, sw=1.4))
    f.append(text(568, 214, "ціль", size=11, color=INK, bold=True))

    # промінь туди
    f.append(arrow(98, 112, 552, 112, color=POS, sw=2.0))
    f.append(text(330, 102, "мерехтливий промінь →", size=11, color=POS, bold=True))
    # відбита пляма назад крізь лінзу
    f.append(arrow(556, 150, 178, 160, color=NEG, sw=2.0))
    f.append(text(360, 180, "← відбита пляма крізь лінзу", size=11, color=NEG, bold=True))

    f.append(text(W / 2, 238, "мерехтіння → синхронне детектування відсіює стале денне світло",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 4. Вихід — гіпербола, а коло нуля немонотонний ──────────────────────────
def fig_nonlinear():
    W, H = 680, 320
    f = [text(W / 2, 28, "Вихід — гіпербола (d ∝ 1/x), а коло нуля ще й немонотонний", size=15, bold=True)]

    ox, oy = 95, 255
    top = 55
    right = 600
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(ox - 8, top + 6, "вихід", size=11, color=INK, anchor="end", bold=True))
    f.append(text(right - 4, oy + 20, "відстань d", size=11, color=INK, anchor="middle", bold=True))

    # спадна гілка (зростання відстані → вихід падає, майже пласко вдалині)
    import math
    pts = []
    x0 = ox + 50
    for i in range(60):
        dd = 0.4 + i * 0.06          # умовна відстань
        xx = x0 + i * 8.0
        yy = oy - 165.0 / dd * 0.55  # вихід ∝ 1/d
        if yy < top + 6:
            yy = top + 6
        pts.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))

    # «поворот» коло нуля: дуже близька ціль — вихід падає назад
    turn_x = x0
    turn_y = float(pts[0].split(",")[1])
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>'
             % (ox + 12, oy - 70, ox + 30, turn_y - 40, turn_x, turn_y, POS))
    f.append(text(ox + 16, oy - 78, "поворот!", size=10.5, color=POS, anchor="start", bold=True))

    # одна горизонталь перетинає обидві гілки → дві відстані
    yline = turn_y - 18
    f.append(line(ox, yline, x0 + 120, yline, color=MUTED, sw=1.2, dash="4,3"))
    f.append(circle(ox + 22, yline, 4, fill=POS, stroke="none", sw=1))
    f.append(circle(x0 + 60, yline, 4, fill=FIELD, stroke="none", sw=1))
    f.append(text(x0 + 70, yline - 8, "один вихід — дві відстані", size=10.5, color=POS, anchor="start", bold=True))
    f.append(text(360, oy - 95, "далеко → крива майже пласка", size=10.5, color=FIELD, anchor="start", italic=True))

    f.append(text(W / 2, 300, "треба калібрувати й шанувати мінімальну дальність",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "nonlinear.svg"), W, H, *f)


# ── 5. Роздільність тане з відстанню (рівні Δd → дедалі менший Δx) ───────────
def fig_resolution():
    W, H = 700, 280
    f = [text(W / 2, 26, "Роздільність тане: рівні кроки Δd дають дедалі менший зсув плями", size=14.5, bold=True)]

    # верхня вісь — відстань, рівні мітки
    ax, ay = 80, 110
    f.append(line(ax, ay, 640, ay, color=INK, sw=2))
    f.append(arrow(610, ay, 648, ay, color=INK, sw=2))
    f.append(text(644, ay + 22, "відстань d, м", size=11, color=INK, anchor="middle", bold=True))
    f.append(rect(50, ay - 14, 20, 28, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    f.append('<polygon points="70,105 80,110 70,115" fill="%s"/>' % POS)

    marks = [(215, "0.5"), (350, "1.0"), (485, "1.5"), (620, "2.0")]
    for mx, lab in marks:
        f.append(line(mx, ay - 8, mx, ay + 8, color=INK, sw=1.6))
        f.append(text(mx, ay + 24, lab, size=10, color=INK))

    # нижня вісь — приймач PSD: ті самі відстані тиснуться вдалині
    px, py = 80, 220
    f.append(line(px, py, 380, py, color=NEG, sw=2))
    f.append(text(px - 6, py + 4, "PSD:", size=10.5, color=NEG, anchor="end", bold=True))
    # положення плями ∝ 1/d: d=0.5→x велике, далі тиснуться
    for d, lab in [(0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0")]:
        sx = px + 150.0 / d
        f.append(circle(sx, py, 4, fill=NEG, stroke="none", sw=1))
        f.append(text(sx, py - 10, lab, size=9, color=NEG))
    f.append(text(290, py + 24, "далекі цілі тиснуться разом → їх не різнити", size=10, color=NEG, anchor="start", italic=True))

    f.append(text(W / 2, 256, "похибка росте ≈ як d²  →  тріангуляція — давач близької дії",
                  size=12, color=INK, bold=True))
    render(os.path.join(IMG, "resolution.svg"), W, H, *f)


# ── 6. Родичі: стереозір (пасивно) і структуроване світло (активно) ─────────
def fig_variants():
    W, H = 720, 290
    f = [text(W / 2, 26, "Родичі тріангуляції: стереозір і структуроване світло", size=15, bold=True)]

    # ── ліва панель: стереозір
    f.append(rect(24, 50, 330, 215, fill="#eef4fb", stroke=NEG, sw=1.4, rx=8))
    f.append(text(189, 72, "стереозір (пасивно)", size=13, color=NEG, bold=True))
    # дві камери, рознесені на базу
    f.append(rect(60, 115, 40, 30, fill="#eef1f6", stroke=INK, sw=1.6, rx=3))
    f.append(circle(94, 130, 6, fill=BG, stroke=INK, sw=1.4))
    f.append(rect(60, 185, 40, 30, fill="#eef1f6", stroke=INK, sw=1.6, rx=3))
    f.append(circle(94, 200, 6, fill=BG, stroke=INK, sw=1.4))
    f.append(line(80, 145, 80, 185, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(56, 168, "база", size=9.5, color=MUTED, anchor="end", italic=True))
    f.append(rect(300, 150, 16, 50, fill="#eee", stroke=INK, sw=1.4))
    f.append(arrow(102, 130, 298, 158, color=FIELD, sw=1.6))
    f.append(arrow(102, 200, 298, 192, color=POS, sw=1.6))
    f.append(text(189, 248, "зсув об'єкта між кадрами (паралакс) → глибина", size=10, color=INK, italic=True))

    # ── права панель: структуроване світло
    f.append(rect(366, 50, 330, 215, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    f.append(text(531, 72, "структуроване світло (активно)", size=12.5, color=POS, bold=True))
    f.append(rect(407, 132, 26, 36, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    f.append('<polygon points="433,145 443,150 433,155" fill="%s"/>' % POS)
    f.append(text(420, 192, "проєктор візерунка", size=9.5, color=INK, bold=True))
    # рельєф із візерунком
    f.append('<polygon points="560,110 600,120 600,210 560,200" fill="#eee" stroke="%s" stroke-width="1.2"/>' % INK)
    for yy in range(120, 200, 18):
        f.append(line(560, yy, 600, yy + 6, color=POS, sw=1.4))
    f.append(arrow(440, 150, 556, 150, color=POS, sw=1.6))
    f.append(text(531, 248, "візерунок спотворюється на рельєфі → карта глибини", size=10, color=INK, italic=True))

    render(os.path.join(IMG, "variants.svg"), W, H, *f)


if __name__ == "__main__":
    fig_geometry()
    fig_similar_triangles()
    fig_anatomy()
    fig_nonlinear()
    fig_resolution()
    fig_variants()
    print("OK: 6 figures ->", IMG)
