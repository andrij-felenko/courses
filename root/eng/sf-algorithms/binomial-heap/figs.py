# -*- coding: utf-8 -*-
"""Фігури для статті «Біноміальна купа». Запуск із теки теми: python figs.py"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
from svgkit import _fit_viewbox

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

R = 20  # радіус вузла


def draw_node(cx, cy, key, fill=FILL, stroke=LINE, sw=1.6, key_color=INK):
    s = circle(cx, cy, R, fill=fill, stroke=stroke, sw=sw)
    s += text(cx, cy + 5.5, str(key), size=14, color=key_color, bold=True)
    return s


def draw_edge(x1, y1, x2, y2, color=LINE, sw=1.5, dash=None):
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    return line(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R, color=color, sw=sw, dash=dash)


def draw_arrow(x1, y1, x2, y2, color=LINE, sw=1.5):
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    return arrow(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R, color=color, sw=sw)


# ── Фігура 1: Структура біноміальних дерев B_0, B_1, B_2, B_3 ───────────────
def fig_binomial_trees():
    W, H = 880, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    f.append(text(W / 2, 28, "Рекурсивна сімейка біноміальних дерев B₀, B₁, B₂, B₃", size=17, bold=True))

    # B_0 (cx=70, cy=100)
    b0_x, b0_y = 70, 90
    f.append(draw_node(b0_x, b0_y, 0))
    f.append(text(b0_x, b0_y + 110, "B₀", size=16, color=NEG, bold=True))
    f.append(mtext(b0_x, b0_y + 135, ["Вузлів: 1 (2⁰)", "Висота: 0", "Степінь: 0"], size=12, color=MUTED))

    # B_1 (cx=200, cy=90)
    b1_x, b1_y = 200, 90
    f.append(draw_edge(b1_x, b1_y, b1_x, b1_y + 60))
    f.append(draw_node(b1_x, b1_y, 1))
    f.append(draw_node(b1_x, b1_y + 60, 5))
    f.append(text(b1_x, b1_y + 170, "B₁", size=16, color=NEG, bold=True))
    f.append(mtext(b1_x, b1_y + 195, ["Вузлів: 2 (2¹)", "Висота: 1", "Степінь: 1"], size=12, color=MUTED))

    # B_2 (cx=400, cy=90)
    b2_x, b2_y = 400, 90
    f.append(draw_edge(b2_x, b2_y, b2_x - 45, b2_y + 60))
    f.append(draw_edge(b2_x, b2_y, b2_x + 45, b2_y + 60))
    f.append(draw_edge(b2_x - 45, b2_y + 60, b2_x - 45, b2_y + 120))
    f.append(draw_node(b2_x, b2_y, 2))
    f.append(draw_node(b2_x - 45, b2_y + 60, 4))
    f.append(draw_node(b2_x + 45, b2_y + 60, 8))
    f.append(draw_node(b2_x - 45, b2_y + 120, 9))
    f.append(text(b2_x, b2_y + 200, "B₂", size=16, color=NEG, bold=True))
    f.append(mtext(b2_x, b2_y + 225, ["Вузлів: 4 (2²)", "Висота: 2", "Степінь: 2"], size=12, color=MUTED))

    # B_3 (cx=700, cy=90)
    b3_x, b3_y = 700, 90
    # Ребра до трьох дітей кореня B_3
    f.append(draw_edge(b3_x, b3_y, b3_x - 120, b3_y + 60))  # B_2 child
    f.append(draw_edge(b3_x, b3_y, b3_x - 10, b3_y + 60))   # B_1 child
    f.append(draw_edge(b3_x, b3_y, b3_x + 90, b3_y + 60))   # B_0 child

    # B_2 піддерево під лівою дитиною (b3_x - 120)
    b3_l_x = b3_x - 120
    f.append(draw_edge(b3_l_x, b3_y + 60, b3_l_x - 35, b3_y + 120))
    f.append(draw_edge(b3_l_x, b3_y + 60, b3_l_x + 35, b3_y + 120))
    f.append(draw_edge(b3_l_x - 35, b3_y + 120, b3_l_x - 35, b3_y + 180))

    # B_1 піддерево під середньою дитиною (b3_x - 10)
    f.append(draw_edge(b3_x - 10, b3_y + 60, b3_x - 10, b3_y + 120))

    # Вузли для B_3
    f.append(draw_node(b3_x, b3_y, 3))
    f.append(draw_node(b3_l_x, b3_y + 60, 6))
    f.append(draw_node(b3_x - 10, b3_y + 60, 10))
    f.append(draw_node(b3_x + 90, b3_y + 60, 15))

    f.append(draw_node(b3_l_x - 35, b3_y + 120, 7))
    f.append(draw_node(b3_l_x + 35, b3_y + 120, 12))
    f.append(draw_node(b3_x - 10, b3_y + 120, 14))

    f.append(draw_node(b3_l_x - 35, b3_y + 180, 11))

    f.append(text(b3_x + 30, b3_y + 170, "B₃", size=16, color=NEG, bold=True))
    f.append(mtext(b3_x + 30, b3_y + 195, ["Вузлів: 8 (2³)", "Висота: 3", "Степінь: 3"], size=12, color=MUTED))

    body = "".join(f)
    vw_x, vw_y, vw_w, vw_h = _fit_viewbox(body, W, H, margin=15)
    full_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%d" height="%d">\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s"/></marker></defs>\n%s\n</svg>'
                % (vw_x, vw_y, vw_w, vw_h, int(vw_w), int(vw_h), LINE, body))
    with open(os.path.join(OUT, "binomial-trees.svg"), "w", encoding="utf-8") as out_f:
        out_f.write(full_svg)


# ── Фігура 2: Структура біноміальної купи N = 13 (1101_2 = B_0 + B_2 + B_3) ──
def fig_heap_structure():
    W, H = 900, 420
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    f.append(text(W / 2, 28, "Біноміальна купа N = 13 (двійковий запис 1101₂ = B₀ + B₂ + B₃)", size=17, bold=True))

    # Корневий список
    r0_x, ry = 100, 110
    r2_x = 280
    r3_x = 580

    # Стрілки кореневого списку (sibling)
    f.append(draw_arrow(r0_x, ry, r2_x, ry, color=NEG, sw=2))
    f.append(draw_arrow(r2_x, ry, r3_x, ry, color=NEG, sw=2))
    f.append(text((r0_x + r2_x) / 2, ry - 14, "sibling", size=12, color=NEG, italic=True))
    f.append(text((r2_x + r3_x) / 2, ry - 14, "sibling", size=12, color=NEG, italic=True))

    # Позначки min_node
    f.append(text(r0_x - 60, ry + 5, "min_node", size=13, color=FIELD, bold=True))
    f.append(arrow(r0_x - 30, ry, r0_x - R - 4, ry, color=FIELD, sw=2))

    # Дерево B_0 (корінь 4)
    f.append(draw_node(r0_x, ry, 4, fill="#eaf0fd", stroke=NEG, sw=2.2))
    f.append(text(r0_x, ry + 45, "B₀ (deg 0)", size=13, color=MUTED, bold=True))

    # Дерево B_2 (корінь 7)
    f.append(draw_node(r2_x, ry, 7))
    f.append(text(r2_x, ry + 45, "B₂ (deg 2)", size=13, color=MUTED, bold=True))
    # Діти 7: 12 (B_1) та 25 (B_0)
    f.append(draw_arrow(r2_x, ry, r2_x - 50, ry + 90, color=LINE))  # child pointer
    f.append(draw_arrow(r2_x - 50, ry + 90, r2_x + 50, ry + 90, color=NEG))  # sibling pointer
    f.append(draw_node(r2_x - 50, ry + 90, 12))
    f.append(draw_node(r2_x + 50, ry + 90, 25))
    # Дитина 12: 18
    f.append(draw_arrow(r2_x - 50, ry + 90, r2_x - 50, ry + 170, color=LINE))
    f.append(draw_node(r2_x - 50, ry + 170, 18))

    # Дерево B_3 (корінь 10)
    f.append(draw_node(r3_x, ry, 10))
    f.append(text(r3_x, ry + 45, "B₃ (deg 3)", size=13, color=MUTED, bold=True))

    # Діти 10: 15 (B_2), 20 (B_1), 30 (B_0)
    c1_x, c2_x, c3_x = r3_x - 140, r3_x, r3_x + 120
    cy1 = ry + 100

    f.append(draw_arrow(r3_x, ry, c1_x, cy1, color=LINE))  # child pointer
    f.append(draw_arrow(c1_x, cy1, c2_x, cy1, color=NEG))  # sibling
    f.append(draw_arrow(c2_x, cy1, c3_x, cy1, color=NEG))  # sibling

    f.append(draw_node(c1_x, cy1, 15))
    f.append(draw_node(c2_x, cy1, 20))
    f.append(draw_node(c3_x, cy1, 30))

    # Діти 15: 22 (B_1) та 45 (B_0)
    cy2 = cy1 + 80
    f.append(draw_arrow(c1_x, cy1, c1_x - 40, cy2, color=LINE))
    f.append(draw_arrow(c1_x - 40, cy2, c1_x + 40, cy2, color=NEG))
    f.append(draw_node(c1_x - 40, cy2, 22))
    f.append(draw_node(c1_x + 40, cy2, 45))

    # Дитина 22: 50
    cy3 = cy2 + 70
    f.append(draw_arrow(c1_x - 40, cy2, c1_x - 40, cy3, color=LINE))
    f.append(draw_node(c1_x - 40, cy3, 50))

    # Дитина 20: 28
    f.append(draw_arrow(c2_x, cy1, c2_x, cy2, color=LINE))
    f.append(draw_node(c2_x, cy2, 28))

    # Пояснення типів зв'язків
    f.append(rect(40, H - 75, 300, 60, fill="#f4f6f8", stroke=LINE, rx=6))
    f.append(arrow(55, H - 55, 95, H - 55, color=NEG, sw=2))
    f.append(text(195, H - 51, "sibling (брат / кореневий список)", size=12, color=INK))
    f.append(arrow(55, H - 30, 95, H - 30, color=LINE, sw=1.8))
    f.append(text(195, H - 26, "child (найлівіша дитина)", size=12, color=INK))

    body = "".join(f)
    vw_x, vw_y, vw_w, vw_h = _fit_viewbox(body, W, H, margin=15)
    full_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%d" height="%d">\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s"/></marker></defs>\n%s\n</svg>'
                % (vw_x, vw_y, vw_w, vw_h, int(vw_w), int(vw_h), LINE, body))
    with open(os.path.join(OUT, "heap-structure.svg"), "w", encoding="utf-8") as out_f:
        out_f.write(full_svg)


# ── Фігура 3: Злиття двох біноміальних дерев B_k однакового степеня ─────────
def fig_merge_operation():
    W, H = 820, 320
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    f.append(text(W / 2, 26, "Атомарна операція злиття (linking) двох дерев B₁ у дерево B₂", size=17, bold=True))

    # Дерево 1 (корінь 12)
    x1, y1 = 120, 80
    f.append(draw_edge(x1, y1, x1, y1 + 70))
    f.append(draw_node(x1, y1, 12, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(draw_node(x1, y1 + 70, 20))
    f.append(text(x1, y1 + 140, "Перше B₁ (key=12)", size=14, color=NEG, bold=True))

    # Знак плюс
    f.append(plus(230, y1 + 35, r=14))

    # Дерево 2 (корінь 15)
    x2, y2 = 340, 80
    f.append(draw_edge(x2, y2, x2, y2 + 70))
    f.append(draw_node(x2, y2, 15, fill="#fdecea", stroke=POS, sw=2))
    f.append(draw_node(x2, y2 + 70, 35))
    f.append(text(x2, y2 + 140, "Друге B₁ (key=15)", size=14, color=POS, bold=True))

    # Стрілка переходу з порівнянням
    f.append(arrow(430, y1 + 35, 520, y1 + 35, color=LINE, sw=2.5))
    f.append(text(475, y1 + 12, "12 < 15", size=13, color=FIELD, bold=True))
    f.append(text(475, y1 + 60, "15 стає дитиною 12", size=12, color=MUTED))

    # Результат B_2 (корінь 12)
    x3, y3 = 680, 80
    f.append(draw_edge(x3, y3, x3 - 55, y3 + 70))
    f.append(draw_edge(x3, y3, x3 + 55, y3 + 70))
    f.append(draw_edge(x3 - 55, y3 + 70, x3 - 55, y3 + 140))
    f.append(draw_edge(x3 + 55, y3 + 70, x3 + 55, y3 + 140))

    f.append(draw_node(x3, y3, 12, fill="#eaf0fd", stroke=NEG, sw=2.2))
    f.append(draw_node(x3 - 55, y3 + 70, 15, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(draw_node(x3 + 55, y3 + 70, 20))

    f.append(draw_node(x3 - 55, y3 + 140, 35))

    f.append(text(x3, y3 + 200, "Результат: дерево B₂", size=15, color=FIELD, bold=True))

    body = "".join(f)
    vw_x, vw_y, vw_w, vw_h = _fit_viewbox(body, W, H, margin=15)
    full_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%d" height="%d">\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s"/></marker></defs>\n%s\n</svg>'
                % (vw_x, vw_y, vw_w, vw_h, int(vw_w), int(vw_h), LINE, body))
    with open(os.path.join(OUT, "merge-operation.svg"), "w", encoding="utf-8") as out_f:
        out_f.write(full_svg)


if __name__ == "__main__":
    fig_binomial_trees()
    fig_heap_structure()
    fig_merge_operation()
    print("Figures successfully generated in ./img/")
