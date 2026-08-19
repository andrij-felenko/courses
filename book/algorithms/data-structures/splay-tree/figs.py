# -*- coding: utf-8 -*-
"""Фігури до статті «Splay-дерево».
Генерує SVG-діаграми у теці img/:
1. splay-rotations.svg — Кроки операції Splay: Zig, Zig-Zig та Zig-Zag.
2. move-to-root-vs-splay.svg — Порівняння Move-to-Root (інверсія ланцюга) та Zig-Zig (сплющення шляху).
3. split-join.svg — Операції Split та Join на базі splay.
4. potential-intuition.svg — Зміна рангу та потенціалу при обертаннях Zig-Zig.
5. working-set-locality.svg — Властивість робочої множини: переміщення гарячих вузлів до кореня.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GRN_F = "#eafaf0"
GRN_S = FIELD
RED_F = "#fdecea"
RED_S = POS
BLUE_F = "#eef6ff"
BLUE_S = NEG
YEL_F = "#fffbeb"
YEL_S = "#d97706"

class TN:
    __slots__ = ("key", "left", "right", "is_sub", "sub_w")
    def __init__(self, key, left=None, right=None, is_sub=False, sub_w=30):
        self.key = key
        self.left = left
        self.right = right
        self.is_sub = is_sub
        self.sub_w = sub_w

def assign_pos(root):
    pos = {}
    c = [0]
    def walk(n, d):
        if n is None:
            return
        walk(n.left, d + 1)
        pos[n] = (c[0], d)
        c[0] += 1
        walk(n.right, d + 1)
    walk(root, 0)
    return pos

def collect_nodes(root):
    out = []
    def walk(n):
        if n is None:
            return
        walk(n.left)
        out.append(n)
        walk(n.right)
    walk(root)
    return out

def draw_tree(parts, root, X0, Y0, COL, ROW, r=18, fs=12, mark=None):
    mark = mark or {}
    pos = assign_pos(root)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}
    # Edges
    for n in collect_nodes(root):
        for ch in (n.left, n.right):
            if ch is not None:
                a, b = ctr[n], ctr[ch]
                parts.append(line(a[0], a[1], b[0], b[1], color="#94a3b8", sw=1.8))
    # Nodes
    for n in collect_nodes(root):
        cx, cy = ctr[n]
        if n.is_sub:
            w, h = n.sub_w, 20
            parts.append(rect(cx - w/2, cy - h/2, w, h, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
            parts.append(text(cx, cy + 4, str(n.key), size=fs - 1, color=MUTED, italic=True))
        elif n.key in mark:
            f, s, t = mark[n.key]
            parts.append(circle(cx, cy, r, fill=f, stroke=s, sw=2.2))
            parts.append(text(cx, cy + 4, str(n.key), size=fs, color=t, bold=True))
        else:
            parts.append(circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5))
            parts.append(text(cx, cy + 4, str(n.key), size=fs, color=INK, bold=True))
    return ctr

# ─────────────────────────────────────────────────────────────────────────────
# 1. splay-rotations.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_splay_rotations():
    W, H = 840, 540
    p = []

    p.append(text(W/2, 26, "Фундаментальні кроки операції Splay", size=16, bold=True, color=INK))

    # Row 1: Zig step (Terminal)
    p.append(rect(20, 48, 800, 145, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(80, 72, "Крок Zig", size=14, bold=True, color=NEG))
    p.append(text(80, 90, "Батько p є коренем", size=11, color=MUTED))
    p.append(text(80, 105, "Один поворот RotateRight(p)", size=10, color=MUTED))

    t_zig_before = TN("p", TN("x", TN("A", is_sub=True), TN("B", is_sub=True)), TN("C", is_sub=True))
    draw_tree(p, t_zig_before, X0=180, Y0=80, COL=32, ROW=38, r=14, fs=11,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG)})

    p.append(arrow(380, 120, 430, 120, color=NEG, sw=2.0))
    p.append(text(405, 110, "Zig(x)", size=11, bold=True, color=NEG))

    t_zig_after = TN("x", TN("A", is_sub=True), TN("p", TN("B", is_sub=True), TN("C", is_sub=True)))
    draw_tree(p, t_zig_after, X0=460, Y0=80, COL=32, ROW=38, r=14, fs=11,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG)})

    # Row 2: Zig-Zig step (Homogeneous)
    p.append(rect(20, 205, 800, 155, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(80, 230, "Крок Zig-Zig", size=14, bold=True, color=POS))
    p.append(text(80, 248, "x і p мають один напрям", size=11, color=MUTED))
    p.append(text(80, 263, "1) Rotate(g) → 2) Rotate(p)", size=10, color=POS, bold=True))

    t_zz_before = TN("g", TN("p", TN("x", TN("A", is_sub=True), TN("B", is_sub=True)), TN("C", is_sub=True)), TN("D", is_sub=True))
    draw_tree(p, t_zz_before, X0=170, Y0=230, COL=26, ROW=32, r=13, fs=10,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    p.append(arrow(380, 280, 430, 280, color=POS, sw=2.0))
    p.append(text(405, 270, "Zig-Zig(x)", size=11, bold=True, color=POS))

    t_zz_after = TN("x", TN("A", is_sub=True), TN("p", TN("B", is_sub=True), TN("g", TN("C", is_sub=True), TN("D", is_sub=True))))
    draw_tree(p, t_zz_after, X0=460, Y0=230, COL=26, ROW=32, r=13, fs=10,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    # Row 3: Zig-Zag step (Heterogeneous)
    p.append(rect(20, 372, 800, 155, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(80, 397, "Крок Zig-Zag", size=14, bold=True, color=FIELD))
    p.append(text(80, 415, "x і p у різних напрямках", size=11, color=MUTED))
    p.append(text(80, 430, "1) Rotate(p) → 2) Rotate(g)", size=10, color=FIELD, bold=True))

    t_zg_before = TN("g", TN("p", TN("A", is_sub=True), TN("x", TN("B", is_sub=True), TN("C", is_sub=True))), TN("D", is_sub=True))
    draw_tree(p, t_zg_before, X0=170, Y0=395, COL=26, ROW=32, r=13, fs=10,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    p.append(arrow(380, 445, 430, 445, color=FIELD, sw=2.0))
    p.append(text(405, 435, "Zig-Zag(x)", size=11, bold=True, color=FIELD))

    t_zg_after = TN("x", TN("p", TN("A", is_sub=True), TN("B", is_sub=True)), TN("g", TN("C", is_sub=True), TN("D", is_sub=True)))
    draw_tree(p, t_zg_after, X0=460, Y0=395, COL=26, ROW=32, r=13, fs=10,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    render(os.path.join(OUT, "splay-rotations.svg"), W, H, *p, title="Кроки операції Splay")

# ─────────────────────────────────────────────────────────────────────────────
# 2. move-to-root-vs-splay.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_move_to_root_vs_splay():
    W, H = 840, 460
    p = []

    p.append(text(W/2, 26, "Move-to-Root проти Splay: чому одинарні повороти неефективні", size=16, bold=True, color=INK))

    # Left Panel: Move-to-root on degenerate line
    p.append(rect(20, 50, 390, 395, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(215, 75, "Наївне підтягування (Move-to-Root)", size=14, bold=True, color=POS))
    p.append(text(215, 95, "Одинарні повороти знизу вгору", size=11, color=MUTED))

    # Tree degenerate line: 5 -> 4 -> 3 -> 2 -> 1
    t_mtr_before = TN(5, TN(4, TN(3, TN(2, TN(1, None, None), None), None), None), None)
    draw_tree(p, t_mtr_before, X0=35, Y0=120, COL=18, ROW=38, r=11, fs=9, mark={1: (RED_F, RED_S, POS)})
    p.append(text(80, 340, "До: витягнутий ланцюг", size=10, bold=True, color=POS))

    p.append(arrow(150, 220, 190, 220, color=POS, sw=2.0))
    p.append(text(170, 205, "MTR(1)", size=10, bold=True, color=POS))

    # After MTR(1): tree is still a line! 1 -> 5 -> 4 -> 3 -> 2
    t_mtr_after = TN(1, None, TN(5, TN(4, TN(3, TN(2, None, None), None), None), None))
    draw_tree(p, t_mtr_after, X0=190, Y0=120, COL=18, ROW=38, r=11, fs=9, mark={1: (RED_F, RED_S, POS)})
    p.append(text(275, 340, "Після: той самий ланцюг!", size=10, bold=True, color=POS))
    p.append(text(215, 415, "Глибина решти вузлів майже не зменшилась: O(N) на запит", size=10, bold=True, color=POS))

    # Right Panel: Splay on degenerate line
    p.append(rect(430, 50, 390, 395, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(625, 75, "Splay-повороти (Zig-Zig сплющення)", size=14, bold=True, color=FIELD))
    p.append(text(625, 95, "Обертання діда перед обертанням батька", size=11, color=MUTED))

    # Tree degenerate line: 5 -> 4 -> 3 -> 2 -> 1
    t_sp_before = TN(5, TN(4, TN(3, TN(2, TN(1, None, None), None), None), None), None)
    draw_tree(p, t_sp_before, X0=445, Y0=120, COL=18, ROW=38, r=11, fs=9, mark={1: (RED_F, RED_S, POS)})
    p.append(text(490, 340, "До: довжина шляху 4", size=10, bold=True, color=MUTED))

    p.append(arrow(560, 220, 600, 220, color=FIELD, sw=2.0))
    p.append(text(580, 205, "splay(1)", size=10, bold=True, color=FIELD))

    # After splay(1): Zig-Zig(1, 2, 3), then Zig-Zig(1, 4, 5)
    # Tree becomes balanced: 1 is root, right child 3, 3's children 2 and 5, 5's left child 4
    t_sp_after = TN(1, None, TN(3, TN(2, None, None), TN(5, TN(4, None, None), None)))
    draw_tree(p, t_sp_after, X0=595, Y0=130, COL=25, ROW=42, r=12, fs=10, mark={1: (GRN_F, GRN_S, INK)})
    p.append(text(685, 340, "Після: висота зменшилась удвічі!", size=10, bold=True, color=FIELD))
    p.append(text(625, 415, "Zig-Zig сплющує дерево вздовж усього шляху доступу", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "move-to-root-vs-splay.svg"), W, H, *p, title="Move-to-Root проти Splay")

# ─────────────────────────────────────────────────────────────────────────────
# 3. split-join.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_split_join():
    W, H = 840, 480
    p = []

    p.append(text(W/2, 26, "Операції Split та Join на основі Splay", size=16, bold=True, color=INK))

    # Left Box: Split(T, k)
    p.append(rect(20, 50, 390, 410, fill="#fafafa", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(215, 75, "Розрізання: Split(T, k)", size=14, bold=True, color=NEG))
    p.append(text(215, 95, "1. splay(k) піднімає k у корінь", size=11, color=MUTED))
    p.append(text(215, 110, "2. Відсікаємо праве піддерево", size=11, color=MUTED))

    # Before split (k at root)
    t_split = TN("k", TN("T<", is_sub=True, sub_w=40), TN("T>", is_sub=True, sub_w=40))
    draw_tree(p, t_split, X0=120, Y0=160, COL=48, ROW=55, r=18, fs=13, mark={"k": (RED_F, RED_S, POS)})

    # Scissors cut indicator
    p.append(line(240, 185, 275, 205, color=POS, sw=2.0, dash="3,3"))
    p.append(text(285, 185, "Розріз", size=10, bold=True, color=POS))

    # Result trees
    p.append(arrow(215, 260, 215, 290, color=NEG, sw=2.0))
    t_left = TN("k", TN("T<", is_sub=True, sub_w=35), None)
    draw_tree(p, t_left, X0=70, Y0=330, COL=35, ROW=45, r=16, fs=12, mark={"k": (RED_F, RED_S, POS)})
    p.append(text(125, 435, "T₁ (всі ключі ≤ k)", size=11, bold=True, color=NEG))

    t_right = TN("T>", is_sub=True, sub_w=50)
    draw_tree(p, t_right, X0=290, Y0=330, COL=35, ROW=45, r=16, fs=12)
    p.append(text(290, 435, "T₂ (всі ключі > k)", size=11, bold=True, color=NEG))

    # Right Box: Join(T1, T2)
    p.append(rect(430, 50, 390, 410, fill="#fafafa", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(625, 75, "Злиття: Join(T₁, T₂)", size=14, bold=True, color=FIELD))
    p.append(text(625, 95, "Умова: всі ключі T₁ < всі ключі T₂", size=11, color=MUTED))
    p.append(text(625, 110, "1. splay(max(T₁)) → правий син порожній", size=11, color=MUTED))

    # Initial join state
    t_j1 = TN("max", TN("L₁", is_sub=True, sub_w=35), None)
    draw_tree(p, t_j1, X0=480, Y0=160, COL=35, ROW=50, r=16, fs=11, mark={"max": (BLUE_F, BLUE_S, NEG)})
    p.append(text(515, 230, "T₁ (max у корені)", size=10, color=MUTED))

    t_j2 = TN("R₂", TN("A", is_sub=True, sub_w=25), TN("B", is_sub=True, sub_w=25))
    draw_tree(p, t_j2, X0=690, Y0=160, COL=30, ROW=50, r=16, fs=11, mark={"R₂": (YEL_F, YEL_S, YEL_S)})
    p.append(text(720, 230, "T₂ (корінь R₂)", size=10, color=MUTED))

    # Join action arrow
    p.append(arrow(625, 260, 625, 290, color=FIELD, sw=2.0))
    p.append(text(625, 275, "2. Під'єднуємо T₂ як правий син max", size=10, bold=True, color=FIELD))

    # Resulting Join Tree
    t_join_res = TN("max", TN("L₁", is_sub=True, sub_w=35), TN("R₂", TN("A", is_sub=True, sub_w=25), TN("B", is_sub=True, sub_w=25)))
    draw_tree(p, t_join_res, X0=500, Y0=320, COL=26, ROW=40, r=14, fs=10,
              mark={"max": (BLUE_F, BLUE_S, NEG), "R₂": (YEL_F, YEL_S, YEL_S)})
    p.append(text(625, 435, "Об'єднане дерево: O(log N) амортизовано", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "split-join.svg"), W, H, *p, title="Операції Split та Join")

# ─────────────────────────────────────────────────────────────────────────────
# 4. potential-intuition.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_potential_intuition():
    W, H = 840, 420
    p = []

    p.append(text(W/2, 26, "Інтуїція методу потенціалів для кроку Zig-Zig", size=16, bold=True, color=INK))

    p.append(rect(20, 50, 800, 350, fill="#fcfcfc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Left: Tree before with ranks
    p.append(text(190, 75, "Стан до повороту: r(x) < r(p) < r(g)", size=13, bold=True, color=POS))
    t_before = TN("g", TN("p", TN("x", TN("A", is_sub=True), TN("B", is_sub=True)), TN("C", is_sub=True)), TN("D", is_sub=True))
    draw_tree(p, t_before, X0=50, Y0=110, COL=28, ROW=38, r=15, fs=11,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    p.append(text(190, 260, "r(g) = r'(x) [розмір всього піддерева]", size=11, color=MUTED))
    p.append(text(190, 280, "Потенціал: Φ = r(x) + r(p) + r(g)", size=11, bold=True, color=INK))

    # Middle Arrow & Math
    p.append(arrow(345, 175, 455, 175, color=POS, sw=2.5))
    p.append(text(400, 160, "Zig-Zig", size=13, bold=True, color=POS))
    p.append(text(400, 195, "ΔΦ = Φ' - Φ", size=11, bold=True, color=POS))

    # Right: Tree after with ranks
    p.append(text(610, 75, "Стан після повороту: r'(g) + r'(p) < 2r'(x)", size=13, bold=True, color=FIELD))
    t_after = TN("x", TN("A", is_sub=True), TN("p", TN("B", is_sub=True), TN("g", TN("C", is_sub=True), TN("D", is_sub=True))))
    draw_tree(p, t_after, X0=470, Y0=110, COL=28, ROW=38, r=15, fs=11,
              mark={"x": (RED_F, RED_S, POS), "p": (BLUE_F, BLUE_S, NEG), "g": (YEL_F, YEL_S, YEL_S)})

    p.append(text(610, 260, "r'(x) стає великим, але r'(g) та r'(p) суттєво менші", size=11, color=MUTED))
    p.append(text(610, 280, "Потенціал: Φ' = r'(x) + r'(p) + r'(g)", size=11, bold=True, color=INK))

    # Bottom summary box
    p.append(rect(40, 310, 760, 75, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(420, 332, "Ключова нерівність через угнутість логарифма: log(a) + log(b) ≤ 2·log((a+b)/2) = 2·log(a+b) - 2", size=11, bold=True, color=INK))
    p.append(text(420, 355, "Амортизована вартість кроку: â = 2 + ΔΦ ≤ 3·(r'(x) - r(x))", size=12, bold=True, color=POS))
    p.append(text(420, 373, "Сума за всіма кроками підйому телескопічно скорочується до 3·(r(корінь) - r(x)) + 1 = O(log N)", size=11, color=FIELD))

    render(os.path.join(OUT, "potential-intuition.svg"), W, H, *p, title="Метод потенціалів для Zig-Zig")

# ─────────────────────────────────────────────────────────────────────────────
# 5. working-set-locality.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_working_set_locality():
    W, H = 840, 420
    p = []

    p.append(text(W/2, 26, "Властивість робочої множини: самоадаптація до гарячих даних", size=16, bold=True, color=INK))

    p.append(rect(20, 50, 390, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(215, 75, "1. Початковий стан: холодні дані", size=14, bold=True, color=MUTED))
    p.append(text(215, 95, "Часто запитувані вузли [A, B] глибоко", size=11, color=MUTED))

    t_ws1 = TN(50,
               TN(25, TN(10, None, TN("A", None, None)), TN(35, None, None)),
               TN(75, TN(60, None, TN("B", None, None)), TN(90, None, None)))
    draw_tree(p, t_ws1, X0=35, Y0=120, COL=22, ROW=38, r=13, fs=10,
              mark={"A": (RED_F, RED_S, POS), "B": (RED_F, RED_S, POS)})
    p.append(text(215, 365, "Доступ до A і B вимагає глибини h = 4", size=11, color=POS, bold=True))

    p.append(arrow(415, 210, 445, 210, color=FIELD, sw=2.5))
    p.append(text(430, 195, "Серія запитів до {A, B}", size=10, bold=True, color=FIELD))

    p.append(rect(450, 50, 370, 350, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(635, 75, "2. Після самоналаштування", size=14, bold=True, color=FIELD))
    p.append(text(635, 95, "Гарячі вузли [A, B] скупчилися біля верхівки", size=11, color=MUTED))

    t_ws2 = TN("A",
               TN(10, None, TN(25, None, TN(35, None, None))),
               TN("B", TN(50, None, TN(60, None, None)), TN(75, None, TN(90, None, None))))
    draw_tree(p, t_ws2, X0=465, Y0=120, COL=21, ROW=38, r=13, fs=10,
              mark={"A": (GRN_F, GRN_S, INK), "B": (GRN_F, GRN_S, INK)})
    p.append(text(635, 365, "Тепер доступ до робочої множини: O(log k) або O(1)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "working-set-locality.svg"), W, H, *p, title="Властивість робочої множини")

if __name__ == "__main__":
    fig_splay_rotations()
    fig_move_to_root_vs_splay()
    fig_split_join()
    fig_potential_intuition()
    fig_working_set_locality()
    print("Всі 5 фігур для Splay-дерева успішно згенеровано у теці img/")
