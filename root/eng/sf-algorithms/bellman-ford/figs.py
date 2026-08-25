# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"   # зелений — збігся / сфокусований
FRONT   = "#e08a1e"   # помаранчевий — оновлений на кроці
FAR     = "#9aa3af"   # сірий — початкова недосяжність
ALERT   = "#c0392b"   # червоний — від'ємна вага / від'ємний цикл
EDGEC   = "#64748b"   # колір ребер

def node(cx, cy, name, dist, fill=FILL, stroke=LINE, r=22):
    """Вузол-кружок із іменем усередині й підписом-відстанню зверху."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, name, size=15, color=INK, bold=True)
    out += text(cx, cy - r - 7, dist, size=12, color=stroke if stroke != LINE else MUTED, bold=True)
    return out

def directed_edge(x1, y1, x2, y2, w, r1=22, r2=22, col=EDGEC, sw=2.0, dash=None, label_side="top"):
    """Орієнтоване ребро зі стрілкою та вагою."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    
    out = line(ax, ay, bx, by, color=col, sw=sw, dash=dash)
    
    # Стрілка на кінці
    ah_len = 10.0
    ah_w = 4.0
    px, py = -uy, ux
    arrow_p1_x = bx - ux * ah_len + px * ah_w
    arrow_p1_y = by - uy * ah_len + py * ah_w
    arrow_p2_x = bx - ux * ah_len - px * ah_w
    arrow_p2_y = by - uy * ah_len - py * ah_w
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none"/>' % 
            (bx, by, arrow_p1_x, arrow_p1_y, arrow_p2_x, arrow_p2_y, col))

    # Підпис ваги
    mx, my = (ax + bx) / 2, (ay + by) / 2
    offset = 14 if label_side == "top" else -14
    lx, ly = mx + px * offset, my + py * offset
    
    w_str = str(w)
    is_neg = isinstance(w, (int, float)) and w < 0
    w_col = ALERT if is_neg else INK
    
    out += circle(lx, ly, 11, fill=BG, stroke="none", sw=0)
    out += text(lx, ly + 4, w_str, size=12, color=w_col, bold=True)
    return out

# ── ФІГ.1 Крок послаблення орієнтованого ребра ────────────────────────────────
def fig_relax_edge():
    W, H = 720, 270
    p = []
    ux, uy = 140.0, 130.0
    vx, vy = 580.0, 130.0

    p.append(directed_edge(ux, uy, vx, vy, -3, col=ALERT, sw=2.5))

    p.append(node(ux, uy, "u", "d[u] = 5", fill="#eaf7ee", stroke=SETTLED))
    p.append(node(vx, vy, "v", "d[v] = 8", fill="#fff7ee", stroke=FRONT))

    p.append(text((ux + vx) / 2, uy - 32, "орієнтоване ребро з від'ємною вагою w = −3", size=12.5, color=MUTED))

    b, bw, bh = textbox((ux + vx) / 2, 215,
                        "перевірка послаблення:  d[u] + w = 5 + (−3) = 2\n2 < 8  →  оновлюємо d[v] := 2",
                        size=13, bold=True, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "relax-edge.svg"), W, H, *p,
           title="Послаблення ребра з від'ємною вагою")

# ── ФІГ.2 Покрокове поширення хвилі послаблень по раундах ─────────────────────
def fig_rounds_trace():
    W, H = 780, 420
    p = []

    # Позиції вершин графа
    sx, sy = 80.0, 150.0
    ax, ay = 250.0, 70.0
    bx, by = 250.0, 230.0
    cx, cy = 420.0, 70.0
    dx, dy = 420.0, 230.0

    # Ребра
    p.append(directed_edge(sx, sy, ax, ay, 4, label_side="top"))
    p.append(directed_edge(sx, sy, bx, by, 5, label_side="bottom"))
    p.append(directed_edge(ax, ay, cx, cy, -2, col=ALERT, label_side="top"))
    p.append(directed_edge(bx, by, ax, ay, -1, col=ALERT, label_side="top"))
    p.append(directed_edge(bx, by, dx, dy, 3, label_side="bottom"))
    p.append(directed_edge(cx, cy, dx, dy, 1, label_side="top"))

    # Вузли
    p.append(node(sx, sy, "S", "0", fill="#eaf7ee", stroke=SETTLED))
    p.append(node(ax, ay, "A", "d[A]=4", fill="#fff7ee", stroke=FRONT))
    p.append(node(bx, by, "B", "d[B]=5", fill="#fff7ee", stroke=FRONT))
    p.append(node(cx, cy, "C", "d[C]=2", fill="#eaf7ee", stroke=SETTLED))
    p.append(node(dx, dy, "D", "d[D]=3", fill="#eaf7ee", stroke=SETTLED))

    # Таблиця раундів праворуч
    tb_x = 640.0
    tbox, tw, th = textbox(tb_x, 175,
                           "Стан d[] по раундах:\n"
                           "k=0: S:0  A:∞  B:∞  C:∞  D:∞\n"
                           "k=1: S:0  A:4  B:5  C:∞  D:8\n"
                           "k=2: S:0  A:4  B:5  C:2  D:3\n"
                           "k=3: S:0  A:4  B:5  C:2  D:3  (збігся!)",
                           size=12, fill="#f8fafc", stroke=EDGEC)
    p.append(tbox)

    render(os.path.join(OUT, "rounds-trace.svg"), W, H, *p,
           title="Поширення оцінок відстаней за раундами в алгоритмі Беллмана-Форда")

# ── ФІГ.3 Детекція від'ємного циклу на V-му раунді ────────────────────────────
def fig_neg_cycle():
    W, H = 760, 360
    p = []

    # Джерело S -> A
    sx, sy = 90.0, 160.0
    p.append(node(sx, sy, "S", "0", fill="#eaf7ee", stroke=SETTLED))

    # Вершини циклу A, B, C
    ax, ay = 270.0, 80.0
    bx, by = 470.0, 80.0
    cx, cy = 370.0, 230.0

    # Ребро S -> A
    p.append(directed_edge(sx, sy, ax, ay, 2, label_side="top"))

    # Цикл A -> B -> C -> A з від'ємною сумою (3 + (-6) + 1 = -2)
    p.append(directed_edge(ax, ay, bx, by, 3, col=ALERT, label_side="top"))
    p.append(directed_edge(bx, by, cx, cy, -6, col=ALERT, label_side="top"))
    p.append(directed_edge(cx, cy, ax, ay, 1, col=ALERT, label_side="bottom"))

    p.append(node(ax, ay, "A", "d=2↓", fill="#fde8e8", stroke=ALERT))
    p.append(node(bx, by, "B", "d=5↓", fill="#fde8e8", stroke=ALERT))
    p.append(node(cx, cy, "C", "d=-1↓", fill="#fde8e8", stroke=ALERT))

    # Вихідний вузол D від C
    dx, dy = 650.0, 230.0
    p.append(directed_edge(cx, cy, dx, dy, 4, col=EDGEC, label_side="bottom"))
    p.append(node(dx, dy, "D", "-∞", fill="#fde8e8", stroke=ALERT))

    # Текстова вставка-пояснення
    b, bw, bh = textbox(400, 310,
                        "Сума ваг циклу: 3 + (−6) + 1 = −2 < 0\n"
                        "На раунді V оцінки продовжують падати: d[C] + w(C→A) = −1 + 1 = 0 < 2 = d[A]  ⇒  виявлено від'ємний цикл!",
                        size=12, bold=True, fill="#fde8e8", stroke=ALERT)
    p.append(b)

    render(os.path.join(OUT, "neg-cycle.svg"), W, H, *p,
           title="Виявлення від'ємного циклу на раунді V")

if __name__ == "__main__":
    fig_relax_edge()
    fig_rounds_trace()
    fig_neg_cycle()
    print("All figures generated successfully.")
