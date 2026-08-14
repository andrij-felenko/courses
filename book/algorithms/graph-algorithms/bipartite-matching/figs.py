# -*- coding: utf-8 -*-
import sys, os
# Add scripts directory (4 levels up from topic folder: book/algorithms/graph-algorithms/bipartite-matching)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"   # зелений — паросполучення / зафіксоване
FRONT   = "#e08a1e"   # помаранчевий — поточний шлях / кандидат
POS     = "#c0392b"   # червоний — вершинне покриття
FAR     = "#94a3b8"   # сірий — звичайні ребра
LINE_C  = "#1a1a1a"   # темний для ліній
FILL_U  = "#eaf2fd"   # блакитна заливка для множини U
FILL_V  = "#fef3e6"   # бежева заливка для множини V


def vnode(cx, cy, name, fill=FILL, stroke=LINE, r=20):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, name, size=14, color=INK, bold=True)
    return out


def edge(x1, y1, x2, y2, color=FAR, sw=1.8, dash=None, r1=20, r2=20):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    return line(ax, ay, bx, by, color=color, sw=sw, dash=dash)


# ── ФІГ.1 Структура дводольного графа та паросполучення ────────────────────────
def fig_bipartite_concept():
    W, H = 760, 420
    p = []

    # Колони U та V
    ux = 220.0
    vx = 540.0
    u_ys = [90.0, 170.0, 250.0, 330.0]
    v_ys = [90.0, 170.0, 250.0, 330.0]

    u_names = ["u₁", "u₂", "u₃", "u₄"]
    v_names = ["v₁", "v₂", "v₃", "v₄"]

    # Заголовочні позначення множин
    p.append(textbox(ux, 35, "Множина U (виконавці / заходи)", size=13, bold=True, fill=FILL_U, stroke=NEG)[0])
    p.append(textbox(vx, 35, "Множина V (задачі / ресурси)", size=13, bold=True, fill=FILL_V, stroke=FRONT)[0])

    # Усі ребра E (сірі пунктирні або тонкі)
    all_edges = [
        (0, 0), (0, 1),
        (1, 1), (1, 2),
        (2, 0), (2, 2), (2, 3),
        (3, 2), (3, 3)
    ]
    # Паросполучення M (жирні зелені): (0,1), (1,2), (2,0), (3,3)
    matching = {(0, 1), (1, 2), (2, 0), (3, 3)}

    for ui, vi in all_edges:
        is_m = (ui, vi) in matching
        col = SETTLED if is_m else FAR
        sw = 3.2 if is_m else 1.5
        dash = None if is_m else "4 4"
        p.append(edge(ux, u_ys[ui], vx, v_ys[vi], color=col, sw=sw, dash=dash))

    # Вузли U
    for i, (y, name) in enumerate(zip(u_ys, u_names)):
        p.append(vnode(ux, y, name, fill=FILL_U, stroke=NEG))

    # Вузли V
    for i, (y, name) in enumerate(zip(v_ys, v_names)):
        p.append(vnode(vx, y, name, fill=FILL_V, stroke=FRONT))

    # Підпис пояснення
    b, bw, bh = textbox(W / 2, 390,
                        "Паросполучення M (зелені суцільні ребра) — множина ребер без спільних вершин.\n"
                        "Жодна вершина з U чи V не належить понад одному зеленому ребру.",
                        size=12, bold=False, fill="#eaf7ee", stroke=SETTLED)
    p.append(b)

    render(os.path.join(OUT, "bipartite-graph-concept.svg"), W, H, *p,
           title="Дводольний граф і максимальне паросполучення")


# ── ФІГ.2 Змінний та доповнюючий шлях ──────────────────────────────────────────
def fig_augmenting_path():
    W, H = 780, 440
    p = []

    # Вузли вздовж шляху u1 - v1 = u2 - v2
    # Непокритий u1, покрите ребро v1-u2, непокрите u2-v2
    xs = [100.0, 240.0, 380.0, 520.0, 660.0]
    y = 150.0

    nodes_info = [
        ("u₁", "вільна в U", FILL_U, NEG),
        ("v₁", "покрита в V", FILL_V, FRONT),
        ("u₂", "покрита в U", FILL_U, NEG),
        ("v₂", "покрита в V", FILL_V, FRONT),
        ("u₃", "вільна в U", FILL_U, NEG)
    ]

    # Ребра шляху: alternated non-matched / matched
    path_edges = [
        (0, 1, False, "не в M"),
        (1, 2, True, "в M (зелене)"),
        (2, 3, False, "не в M"),
        (3, 4, True, "в M (зелене)")
    ]

    for i1, i2, in_m, lbl in path_edges:
        x1, x2 = xs[i1], xs[i2]
        col = SETTLED if in_m else FRONT
        sw = 3.5 if in_m else 2.2
        dash = None if in_m else "5 4"
        p.append(edge(x1, y, x2, y, color=col, sw=sw, dash=dash))
        p.append(text((x1 + x2) / 2, y - 28, lbl, size=11, color=col, bold=True))

    for i, (name, status, fill_c, strk_c) in enumerate(nodes_info):
        cx = xs[i]
        p.append(vnode(cx, y, name, fill=fill_c, stroke=strk_c, r=22))
        p.append(text(cx, y + 38, status, size=11, color=MUTED))

    # Інверсія M = M XOR P
    b, bw, bh = textbox(W / 2, 340,
                        "Доповнюючий шлях P почергово містить ребра поза M та з M, починаючись і кінчаючись у вільних вершинах.\n"
                        "Операція симетричної різниці M' = M ⊕ P міняє роли ребер і збільшує розмір |M'| = |M| + 1.",
                        size=12, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "augmenting-path.svg"), W, H, *p,
           title="Змінний та доповнюючий шлях (Augmenting Path)")


# ── ФІГ.3 Зведення до максимального потоку ────────────────────────────────────
def fig_flow_reduction():
    W, H = 820, 420
    p = []

    sx = 90.0
    ux = 300.0
    vx = 520.0
    tx = 730.0

    sy = 210.0
    ty = 210.0

    u_ys = [110.0, 210.0, 310.0]
    v_ys = [110.0, 210.0, 310.0]

    # Джерело s та Сток t
    p.append(vnode(sx, sy, "s", fill="#e8f8f5", stroke=SETTLED, r=24))
    p.append(text(sx, sy + 40, "джерело", size=11, color=SETTLED, bold=True))

    p.append(vnode(tx, ty, "t", fill="#fdedec", stroke=POS, r=24))
    p.append(text(tx, ty + 40, "сток", size=11, color=POS, bold=True))

    # Вершини U
    for i, y in enumerate(u_ys):
        p.append(vnode(ux, y, f"u_{i+1}", fill=FILL_U, stroke=NEG, r=20))
        # Стрілки s -> u_i
        p.append(arrow(sx + 24, sy, ux - 20, y, color=SETTLED, sw=2.0))
        p.append(text((sx + ux) / 2 - 15, (sy + y) / 2 - 8, "c=1", size=11, color=SETTLED, bold=True))

    # Вершини V
    for j, y in enumerate(v_ys):
        p.append(vnode(vx, y, f"v_{j+1}", fill=FILL_V, stroke=FRONT, r=20))
        # Стрілки v_j -> t
        p.append(arrow(vx + 20, y, tx - 24, ty, color=POS, sw=2.0))
        p.append(text((vx + tx) / 2 + 15, (y + ty) / 2 - 8, "c=1", size=11, color=POS, bold=True))

    # Внутрішні орієнтовані ребра U -> V з c=1 або c=∞
    internal_edges = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 2)]
    for ui, vi in internal_edges:
        y1, y2 = u_ys[ui], v_ys[vi]
        p.append(arrow(ux + 20, y1, vx - 20, y2, color=FAR, sw=1.6))

    b, bw, bh = textbox(W / 2, 385,
                        "Всі ребра мають пропускну здатність c = 1. Цілочисельний максимальний потік величини F\n"
                        "відповідає максимальному паросполученню розміру |M| = F у дводольному графі.",
                        size=12, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "flow-reduction.svg"), W, H, *p,
           title="Зведення дводольного паросполучення до задачі про максимальний потік")


# ── ФІГ.4 Теорема Кеніга: паросполучення та вершинне покриття ──────────────────
def fig_konig_cover():
    W, H = 760, 420
    p = []

    ux, vx = 220.0, 540.0
    u_ys = [90.0, 190.0, 290.0]
    v_ys = [90.0, 190.0, 290.0]

    # Ребра
    edges_list = [
        (0, 0, True),   # M
        (0, 1, False),
        (1, 1, True),   # M
        (2, 1, False),
        (2, 2, True)    # M
    ]

    for ui, vi, is_m in edges_list:
        col = SETTLED if is_m else FAR
        sw = 3.2 if is_m else 1.5
        dash = None if is_m else "4 4"
        p.append(edge(ux, u_ys[ui], vx, v_ys[vi], color=col, sw=sw, dash=dash))

    # Вершинне покриття C: u1 (в покритті), v2 (в покритті), u3 (в покритті)
    u_in_cover = [True, False, True]
    v_in_cover = [False, True, False]

    for i, y in enumerate(u_ys):
        inc = u_in_cover[i]
        stroke_c = POS if inc else NEG
        fill_c = "#fadbd8" if inc else FILL_U
        p.append(vnode(ux, y, f"u_{i+1}", fill=fill_c, stroke=stroke_c, r=22))
        if inc:
            p.append(text(ux - 65, y + 4, "C ∈ C_min", size=11, color=POS, bold=True))

    for j, y in enumerate(v_ys):
        inc = v_in_cover[j]
        stroke_c = POS if inc else FRONT
        fill_c = "#fadbd8" if inc else FILL_V
        p.append(vnode(vx, y, f"v_{j+1}", fill=fill_c, stroke=stroke_c, r=22))
        if inc:
            p.append(text(vx + 65, y + 4, "C ∈ C_min", size=11, color=POS, bold=True))

    b, bw, bh = textbox(W / 2, 375,
                        "Теорема Кеніга: |M_max| = |C_min| = 3.\n"
                        "Зелені ребра — максимальне паросполучення. Червоні вершини — мінімальне вершинне покриття,\n"
                        "яке блокує всі ребра графа (кожне ребро має принаймні один червоний кінець).",
                        size=12, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "konig-cover.svg"), W, H, *p,
           title="Теорема Кеніга: максимальне паросполучення = мінімальне вершинне покриття")


# ── ФІГ.5 Покроковий прогін алгоритму Куна ─────────────────────────────────────
def fig_kuhn_step():
    W, H = 800, 440
    p = []

    # Ліва частина — стан паросполучення під час DFS для u3
    ux, vx = 180.0, 420.0
    u_ys = [100.0, 200.0, 300.0]
    v_ys = [100.0, 200.0, 300.0]

    edges = [
        (0, 0, True),
        (1, 1, True),
        (2, 0, False),
        (2, 1, False),
        (1, 2, False)
    ]

    for ui, vi, is_m in edges:
        col = FRONT if (ui == 2 and vi == 0) else (SETTLED if is_m else FAR)
        sw = 3.2 if (is_m or (ui == 2 and vi == 0)) else 1.5
        dash = "5 4" if not is_m and not (ui == 2 and vi == 0) else None
        p.append(edge(ux, u_ys[ui], vx, v_ys[vi], color=col, sw=sw, dash=dash))

    for i, y in enumerate(u_ys):
        fill_c = "#fdebd0" if i == 2 else FILL_U
        strk_c = FRONT if i == 2 else NEG
        p.append(vnode(ux, y, f"u_{i+1}", fill=fill_c, stroke=strk_c, r=20))

    for j, y in enumerate(v_ys):
        p.append(vnode(vx, y, f"v_{j+1}", fill=FILL_V, stroke=FRONT, r=20))

    # Права частина — масиви match[] та used[]
    tbl_x = 640.0
    p.append(text(tbl_x, 75, "Масив match[] (для V)", size=13, color=INK, bold=True))
    p.append(textbox(tbl_x, 115, "match[v₁] = u₁\nmatch[v₂] = u₂\nmatch[v₃] = ∅", size=12, fill=BG, stroke=LINE)[0])

    p.append(text(tbl_x, 215, "Хід DFS(u₃)", size=13, color=FRONT, bold=True))
    p.append(textbox(tbl_x, 275, "1. u₃ бачить v₁ (зайнята u₁)\n2. DFS іде до u₁ = match[v₁]\n3. u₁ перенаправляється на v₂\n4. v₂ зайнята u₂ -> u₂ іде на v₃\n5. v₃ вільна! Успіх!", size=11.5, fill="#fff7ee", stroke=FRONT)[0])

    b, bw, bh = textbox(W / 2, 400,
                        "Алгоритм Куна для кожної вершини u ∈ U шукає доповнюючий шлях через DFS.\n"
                        "Якщо сусід v ∈ V уже зайнятий, DFS рекурсивно намагається перенаправити match[v] на іншу вершину.",
                        size=12, bold=False, fill="#eaf7ee", stroke=SETTLED)
    p.append(b)

    render(os.path.join(OUT, "kuhn-step.svg"), W, H, *p,
           title="Покроковий пошук доповнюючого шляху в алгоритмі Куна")


if __name__ == "__main__":
    fig_bipartite_concept()
    fig_augmenting_path()
    fig_flow_reduction()
    fig_konig_cover()
    fig_kuhn_step()
    print("OK figs for bipartite-matching")
