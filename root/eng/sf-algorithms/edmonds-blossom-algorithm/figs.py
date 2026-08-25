# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"   # зелений — ребро паросполучення (M)
UNMATCH = "#2457d6"   # синій — вільне ребро (не в M)
ACCENT  = "#c0392b"   # червоний — конфлікт парності / виділення
ORANGE  = "#e67e22"   # помаранчевий — квітка / супервершина
FILL_S  = "#eaf2fd"   # світло-синій (S / парна вершина)
FILL_T  = "#fef3e6"   # світло-бежевий (T / непарна вершина)
FILL_B  = "#fdf2e9"   # заливка супервершини

def vnode(cx, cy, label, sub=None, fill=FILL_S, stroke=LINE, r=20):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    if sub:
        out += text(cx, cy - 2, label, size=13, color=INK, bold=True)
        out += text(cx, cy + 12, sub, size=9, color=MUTED, bold=False)
    else:
        out += text(cx, cy + 5, label, size=13, color=INK, bold=True)
    return out

def edge(x1, y1, x2, y2, color=LINE, sw=2.0, dash=None, r1=20, r2=20):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    return line(ax, ay, bx, by, color=color, sw=sw, dash=dash)

# ── ФІГ.1 Двочастковий обхід проти непарного циклу у загальному графі ─────────
def fig_bipartite_vs_blossom():
    W, H = 840, 420
    p = []

    # Ліва панель: Двочастковий граф (чітка парність)
    p.append(rect(20, 20, 380, 380, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(210, 45, "Двочастковий граф: однозначна парність", size=13, bold=True, fill="#f8fafc", stroke="#94a3b8")[0])

    # Вузли двочасткового графа
    b_nodes = [
        (90, 110, "r", "парна (0)", FILL_S, NEG),
        (210, 110, "v₁", "непарна (1)", FILL_T, ORANGE),
        (330, 110, "v₂", "парна (2)", FILL_S, NEG),
        (210, 230, "v₃", "непарна (3)", FILL_T, ORANGE),
        (330, 230, "v₄", "парна (4)", FILL_S, NEG),
    ]

    p.append(edge(90, 110, 210, 110, color=UNMATCH, sw=2.5))
    p.append(edge(210, 110, 330, 110, color=SETTLED, sw=3.5))
    p.append(edge(330, 110, 210, 230, color=UNMATCH, sw=2.5))
    p.append(edge(210, 230, 330, 230, color=SETTLED, sw=3.5))

    for x, y, name, sub, fcol, scol in b_nodes:
        p.append(vnode(x, y, name, sub, fill=fcol, stroke=scol, r=22))

    p.append(textbox(210, 335, "Відстані строго чергуються: S (0, 2, 4) та T (1, 3).\nНемає непарних циклів — парність кожної вершини фіксована.", size=11, bold=False, fill="#f1f5f9", stroke="#cbd5e1")[0])

    # Права панель: Загальний граф із непарним циклом C5
    p.append(rect(440, 20, 380, 380, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(630, 45, "Загальний граф: конфлікт парності (квітка C₅)", size=13, bold=True, fill="#fef2f2", stroke=ACCENT)[0])

    cx, cy, R = 630, 170, 75
    coords = []
    for i in range(5):
        ang = math.radians(-90 + i * 72)
        coords.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))

    c_edges = [
        (0, 1, UNMATCH, 2.5, None),
        (1, 2, SETTLED, 3.5, None),
        (2, 3, UNMATCH, 2.5, "4 3"),
        (3, 4, SETTLED, 3.5, None),
        (4, 0, UNMATCH, 2.5, None)
    ]
    for u, v, col, sw, dash in c_edges:
        p.append(edge(coords[u][0], coords[u][1], coords[v][0], coords[v][1], color=col, sw=sw, dash=dash))

    c_labels = [
        ("r", "корінь (0)", FILL_S, NEG),
        ("1", "непарна (1)", FILL_T, ORANGE),
        ("2", "парна 2 / непарна 3", "#fef2f2", ACCENT),
        ("3", "парна 2 / непарна 3", "#fef2f2", ACCENT),
        ("4", "непарна (1)", FILL_T, ORANGE)
    ]

    for (x, y), (name, sub, fcol, scol) in zip(coords, c_labels):
        p.append(vnode(x, y, name, sub, fill=fcol, stroke=scol, r=22))

    p.append(textbox(630, 335, "Ребро (2, 3) замикає непарний цикл: вершини 2 і 3\nодночасно парні й непарні. BFS застрягає в пастці.", size=11, bold=False, fill="#fef2f2", stroke=ACCENT)[0])

    render(os.path.join(OUT, "fig1-bipartite-vs-blossom-parity.svg"), W, H, *p)

# ── ФІГ.2 Анатомія квітки та стебла: два чергувальні шляхи ─────────────────────
def fig_blossom_structure():
    W, H = 840, 450
    p = []

    # Верхня рамка заголовка
    p.append(textbox(420, 30, "Анатомія квітки та стебла: два чергувальні рукави від основи", size=13, bold=True, fill="#f8fafc", stroke="#94a3b8")[0])

    # Панель стебла (ліворуч)
    p.append(rect(20, 60, 350, 290, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(195, 85, "Стебло P (парна довжина: 3 ребра)", size=12, bold=True, fill="#eff6ff", stroke=NEG)[0])

    # Стебло зліва: r(вільна) -> s1 = s2 -> b(основа)
    p.append(edge(60, 200, 140, 200, color=UNMATCH, sw=2.5))
    p.append(edge(140, 200, 220, 200, color=SETTLED, sw=3.5))
    p.append(edge(220, 200, 310, 200, color=UNMATCH, sw=2.5))

    p.append(vnode(60, 200, "r", "корінь", fill=FILL_S, stroke=NEG, r=20))
    p.append(vnode(140, 200, "s₁", "непарна", fill=FILL_T, stroke=ORANGE, r=18))
    p.append(vnode(220, 200, "s₂", "парна", fill=FILL_S, stroke=NEG, r=18))
    p.append(vnode(310, 200, "b", "основа", fill="#dcfce7", stroke=SETTLED, r=22))

    p.append(textbox(195, 295, "Стебло з'єднує вільний корінь r\nіз базою квітки b чергувальним ланцюгом.", size=10, bold=False, fill="#f8fafc", stroke="#cbd5e1")[0])

    # Панель квітки (праворуч)
    p.append(rect(390, 60, 430, 290, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(605, 85, "Квітка B: непарний цикл (5 вершин, 2 ребра M)", size=12, bold=True, fill="#fff7ed", stroke=ORANGE)[0])

    bx, by = 450, 200
    u1x, u1y = 540, 140
    u2x, u2y = 660, 140
    v2x, v2y = 660, 260
    v1x, v1y = 540, 260

    p.append(edge(bx, by, u1x, u1y, color=UNMATCH, sw=2.5))
    p.append(edge(u1x, u1y, u2x, u2y, color=SETTLED, sw=3.8))
    p.append(edge(u2x, u2y, v2x, v2y, color=UNMATCH, sw=2.5))
    p.append(edge(v2x, v2y, v1x, v1y, color=SETTLED, sw=3.8))
    p.append(edge(v1x, v1y, bx, by, color=UNMATCH, sw=2.5))

    p.append(vnode(bx, by, "b", "основа", fill="#dcfce7", stroke=SETTLED, r=22))
    p.append(vnode(u1x, u1y, "u₁", None, fill=FILL_T, stroke=ORANGE, r=18))
    p.append(vnode(u2x, u2y, "u₂", None, fill=FILL_S, stroke=NEG, r=18))
    p.append(vnode(v2x, v2y, "v₂", None, fill=FILL_S, stroke=NEG, r=18))
    p.append(vnode(v1x, v1y, "v₁", None, fill=FILL_T, stroke=ORANGE, r=18))

    # Нижній висновок
    p.append(textbox(420, 395, "До будь-якої вершини (напр. v₂) існують ДВА шляхи від b:\nПарний Q₁: b → v₁ = v₂ (довжина 2) та Непарний Q₂: b → u₁ = u₂ → v₂ (довжина 3).\nЗавдяки цьому квітка діє як єдиний парний вузол!", size=11, bold=False, fill="#f8fafc", stroke="#94a3b8")[0])

    render(os.path.join(OUT, "fig2-blossom-structure-and-paths.svg"), W, H, *p)

# ── ФІГ.3 Стиснення квітки та розгортання доповняльного шляху ──────────────────
def fig_blossom_contraction():
    W, H = 840, 430
    p = []

    # Ліва частина: Стиснення у супервершину
    p.append(rect(20, 20, 385, 390, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(212, 45, "1. Стиснення: граф G → G/B", size=13, bold=True, fill="#eff6ff", stroke=NEG)[0])

    p.append(vnode(70, 160, "r", "корінь", fill=FILL_S, stroke=NEG, r=20))
    p.append(edge(70, 160, 170, 160, color=UNMATCH, sw=2.5))
    p.append(vnode(170, 160, "B", "супервузол", fill="#fed7aa", stroke=ORANGE, r=26))
    p.append(edge(170, 160, 270, 160, color=SETTLED, sw=3.5))
    p.append(vnode(270, 160, "x", "непарна", fill=FILL_T, stroke=ORANGE, r=20))
    p.append(edge(270, 160, 360, 160, color=UNMATCH, sw=2.5))
    p.append(vnode(360, 160, "y", "вільна!", fill="#dcfce7", stroke=SETTLED, r=20))

    p.append(textbox(212, 280, "Шлях у G/B знайдено:\n r → B = x → y\nКвітка B виступає як звичайна парна вершина,\nдозволяючи продовжити BFS через ребро паросполучення.", size=11, bold=False, fill="#f8fafc", stroke="#cbd5e1")[0])

    # Права частина: Розгортання шляху всередині квітки
    p.append(rect(435, 20, 385, 390, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(textbox(627, 45, "2. Розгортання: підйом шляху у граф G", size=13, bold=True, fill="#f0fdf4", stroke=SETTLED)[0])

    rx, ry = 475, 160
    bx, by = 550, 160
    u1x, u1y = 610, 105
    u2x, u2y = 680, 105
    v2x, v2y = 680, 215
    v1x, v1y = 610, 215
    xx, xy = 760, 160
    yx, yy = 760, 260

    p.append(edge(rx, ry, bx, by, color=UNMATCH, sw=3.0))
    p.append(edge(bx, by, u1x, u1y, color=UNMATCH, sw=3.0))
    p.append(edge(u1x, u1y, u2x, u2y, color=SETTLED, sw=4.0))
    p.append(edge(u2x, u2y, v2x, v2y, color=UNMATCH, sw=3.0))
    p.append(edge(v2x, v2y, v1x, v1y, color=SETTLED, sw=1.5, dash="3 3"))
    p.append(edge(v1x, v1y, bx, by, color=UNMATCH, sw=1.5, dash="3 3"))
    p.append(edge(v2x, v2y, xx, xy, color=SETTLED, sw=4.0))
    p.append(edge(xx, xy, yx, yy, color=UNMATCH, sw=3.0))

    p.append(vnode(rx, ry, "r", None, fill=FILL_S, stroke=NEG, r=18))
    p.append(vnode(bx, by, "b", None, fill="#dcfce7", stroke=SETTLED, r=18))
    p.append(vnode(u1x, u1y, "u₁", None, fill=FILL_T, stroke=ORANGE, r=16))
    p.append(vnode(u2x, u2y, "u₂", None, fill=FILL_S, stroke=NEG, r=16))
    p.append(vnode(v2x, v2y, "v₂", None, fill=FILL_S, stroke=NEG, r=16))
    p.append(vnode(v1x, v1y, "v₁", None, fill=FILL_T, stroke=ORANGE, r=16))
    p.append(vnode(xx, xy, "x", None, fill=FILL_T, stroke=ORANGE, r=18))
    p.append(vnode(yx, yy, "y", None, fill="#dcfce7", stroke=SETTLED, r=18))

    p.append(textbox(627, 340, "Розгорнутий доповняльний шлях у G:\n r → b → u₁ = u₂ → v₂ = x → y\nСтроге чергування збережено! Інвертуємо ребра,\nі розмір паросполучення зростає на 1.", size=11, bold=False, fill="#f0fdf4", stroke=SETTLED)[0])

    render(os.path.join(OUT, "fig3-blossom-contraction-and-lifting.svg"), W, H, *p)

# ── ФІГ.4 Класифікація станів BFS та стиснення за LCA ─────────────────────────
def fig_bfs_forest_lca():
    W, H = 820, 420
    p = []

    p.append(textbox(410, 35, "Чергувальний ліс BFS: виявлення квітки через ребро між двома S-вершинами", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")[0])

    rx, ry = 410, 95
    t1x, t1y = 280, 165
    s1x, s1y = 200, 235
    t2x, t2y = 150, 305
    s2x, s2y = 250, 335

    t3x, t3y = 540, 165
    s3x, s3y = 590, 275

    p.append(edge(rx, ry, t1x, t1y, color=UNMATCH, sw=2.5))
    p.append(edge(t1x, t1y, s1x, s1y, color=SETTLED, sw=3.8))
    p.append(edge(s1x, s1y, t2x, t2y, color=UNMATCH, sw=2.5))
    p.append(edge(t2x, t2y, s2x, s2y, color=SETTLED, sw=3.8))

    p.append(edge(rx, ry, t3x, t3y, color=UNMATCH, sw=2.5))
    p.append(edge(t3x, t3y, s3x, s3y, color=SETTLED, sw=3.8))

    p.append(edge(s2x, s2y, s3x, s3y, color=ACCENT, sw=3.0, dash="5 4"))

    p.append(vnode(rx, ry, "r", "LCA / основа", fill="#dcfce7", stroke=SETTLED, r=22))
    p.append(vnode(t1x, t1y, "t₁", "Inner (T)", fill=FILL_T, stroke=ORANGE, r=19))
    p.append(vnode(s1x, s1y, "s₁", "Outer (S)", fill=FILL_S, stroke=NEG, r=19))
    p.append(vnode(t2x, t2y, "t₂", "Inner (T)", fill=FILL_T, stroke=ORANGE, r=19))
    p.append(vnode(s2x, s2y, "s₂", "Outer (S)", fill=FILL_S, stroke=NEG, r=19))

    p.append(vnode(t3x, t3y, "t₃", "Inner (T)", fill=FILL_T, stroke=ORANGE, r=19))
    p.append(vnode(s3x, s3y, "s₃", "Outer (S)", fill=FILL_S, stroke=NEG, r=19))

    p.append(textbox(410, 225, "Ребро (s₂, s₃) з'єднує дві S-вершини!\nLCA(s₂, s₃) = r визначає основу квітки b = r.", size=11, bold=True, fill="#fff1f2", stroke=ACCENT)[0])

    p.append(textbox(410, 385, "Дія алгоритму: стягнути цикл (s₂-t₂-s₁-t₁-r-t₃-s₃-s₂) у базу r через DSU.\nВсі проміжні T-вершини (t₁, t₂, t₃) стають S-вершинами і додаються в чергу BFS!", size=11, bold=False, fill="#f8fafc", stroke="#94a3b8")[0])

    render(os.path.join(OUT, "fig4-alternating-forest-classification.svg"), W, H, *p)

if __name__ == "__main__":
    fig_bipartite_vs_blossom()
    fig_blossom_structure()
    fig_blossom_contraction()
    fig_bfs_forest_lca()
    print("All figures generated successfully.")
