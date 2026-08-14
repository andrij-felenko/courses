# -*- coding: utf-8 -*-
"""Фігури до статті «AVL-дерево».
Генерує SVG-діаграми у теці img/:
1. invariant.svg — Фактор балансу та інваріант AVL-дерева (|BF| <= 1).
2. single-rotation.svg — Малі (поодинокі) обертання: праве (LL) та ліве (RR).
3. double-rotation.svg — Великі (подвійні) обертання: ліво-праве (LR) та право-ліве (RL).
4. insertion-rebalance.svg — Покрокова вставка та відновлення балансу.
5. deletion-rebalance.svg — Видалення та каскадне балансування вгору за стеком.
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

class TN:
    __slots__ = ("key", "bf", "left", "right")
    def __init__(self, key, bf=0, left=None, right=None):
        self.key, self.bf = key, bf
        self.left, self.right = left, right

def assign_pos(root):
    pos, c = {}, [0]
    def walk(n, d):
        if n is None: return
        walk(n.left, d + 1)
        pos[n] = (c[0], d)
        c[0] += 1
        walk(n.right, d + 1)
    walk(root, 0)
    return pos

def collect_nodes(root):
    out = []
    def walk(n):
        if n is None: return
        walk(n.left)
        out.append(n)
        walk(n.right)
    walk(root)
    return out

def draw_tree(parts, root, X0, Y0, COL, ROW, r=22, fs=14, mark=None):
    mark = mark or {}
    pos = assign_pos(root)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}
    # Edges
    for n in collect_nodes(root):
        for ch in (n.left, n.right):
            if ch is not None:
                a, b = ctr[n], ctr[ch]
                parts.append(line(a[0], a[1], b[0], b[1], color="#94a3b8", sw=2.0))
    # Nodes
    for n in collect_nodes(root):
        cx, cy = ctr[n]
        if n.key in mark:
            f, s, t = mark[n.key]
            parts.append(circle(cx, cy, r, fill=f, stroke=s, sw=2.5))
            parts.append(text(cx, cy - 2, str(n.key), size=fs, color=t, bold=True))
            bf_str = f"bf={n.bf:+d}" if n.bf != 0 else "bf=0"
            parts.append(text(cx, cy + 13, bf_str, size=10, color=s, bold=True))
        else:
            parts.append(circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.8))
            parts.append(text(cx, cy - 2, str(n.key), size=fs, color=INK, bold=True))
            bf_str = f"bf={n.bf:+d}" if n.bf != 0 else "bf=0"
            parts.append(text(cx, cy + 13, bf_str, size=11, color=MUTED))
    return ctr

# ─────────────────────────────────────────────────────────────────────────────
# 1. invariant.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_invariant():
    W, H = 840, 420
    p = []
    
    p.append(text(W/2, 30, "Інваріант AVL-дерева: фактор балансу BF = h(R) - h(L) ∈ {-1, 0, +1}", size=16, bold=True, color=INK))

    # Left tree: Balanced AVL
    t_bal = TN(40, 0,
               TN(20, 1, None, TN(30, 0)),
               TN(60, 0, TN(50, 0), TN(70, 0)))
    
    p.append(rect(30, 60, 375, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(217, 90, "Сбалансоване AVL-дерево", size=15, bold=True, color=FIELD))
    p.append(text(217, 110, "Усі вузли мають |BF| ≤ 1", size=12, color=MUTED))
    draw_tree(p, t_bal, X0=65, Y0=160, COL=50, ROW=65, r=20, fs=13,
              mark={40: (GRN_F, GRN_S, INK), 20: (GRN_F, GRN_S, INK), 30: (GRN_F, GRN_S, INK),
                    60: (GRN_F, GRN_S, INK), 50: (GRN_F, GRN_S, INK), 70: (GRN_F, GRN_S, INK)})

    # Right tree: Unbalanced BST
    t_unbal = TN(40, -2,
                 TN(20, -2,
                    TN(10, -1, TN(5, 0), None),
                    None),
                 TN(60, 0))
    
    p.append(rect(435, 60, 375, 330, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(622, 90, "Незбалансоване дерево (BST)", size=15, bold=True, color=POS))
    p.append(text(622, 110, "Вузол 40 має BF = -2 (перекіс ліворуч)", size=12, color=POS))
    draw_tree(p, t_unbal, X0=465, Y0=150, COL=55, ROW=60, r=20, fs=13,
              mark={40: (RED_F, RED_S, POS), 20: (RED_F, RED_S, POS), 10: (GRN_F, GRN_S, INK), 5: (GRN_F, GRN_S, INK), 60: (GRN_F, GRN_S, INK)})

    render(os.path.join(OUT, "invariant.svg"), W, H, *p, title="Інваріант AVL-дерева")

# ─────────────────────────────────────────────────────────────────────────────
# 2. single-rotation.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_single_rotation():
    W, H = 840, 440
    p = []

    p.append(text(W/2, 28, "Малі (поодинокі) обертання: усунення перекосу LL та RR", size=16, bold=True, color=INK))

    # Left Half: Right Rotation (LL imbalance)
    p.append(rect(20, 50, 390, 370, fill="#fafafa", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(215, 75, "Праве обертання (LL-перекіс)", size=15, bold=True, color=NEG))
    p.append(text(215, 95, "Вставка в ліве піддерево лівого сина", size=12, color=MUTED))

    # Before LL
    t_ll_before = TN(30, -2, TN(20, -1, TN(10, 0), None), TN(40, 0))
    draw_tree(p, t_ll_before, X0=40, Y0=140, COL=38, ROW=55, r=18, fs=12,
              mark={30: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})
    p.append(text(105, 335, "До: BF(30) = -2", size=12, bold=True, color=POS))

    # Arrow
    p.append(arrow(180, 210, 230, 210, color=NEG, sw=2.5))
    p.append(text(205, 195, "RotateRight(30)", size=11, bold=True, color=NEG))

    # After LL
    t_ll_after = TN(20, 0, TN(10, 0), TN(30, 0, None, TN(40, 0)))
    draw_tree(p, t_ll_after, X0=250, Y0=140, COL=38, ROW=55, r=18, fs=12,
              mark={20: (GRN_F, GRN_S, INK), 10: (GRN_F, GRN_S, INK), 30: (GRN_F, GRN_S, INK), 40: (GRN_F, GRN_S, INK)})
    p.append(text(320, 335, "Після: BF(20) = 0", size=12, bold=True, color=FIELD))

    # Right Half: Left Rotation (RR imbalance)
    p.append(rect(430, 50, 390, 370, fill="#fafafa", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(625, 75, "Ліве обертання (RR-перекіс)", size=15, bold=True, color=NEG))
    p.append(text(625, 95, "Вставка в праве піддерево правого сина", size=12, color=MUTED))

    # Before RR
    t_rr_before = TN(10, 2, TN(5, 0), TN(20, 1, None, TN(30, 0)))
    draw_tree(p, t_rr_before, X0=450, Y0=140, COL=38, ROW=55, r=18, fs=12,
              mark={10: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})
    p.append(text(515, 335, "До: BF(10) = +2", size=12, bold=True, color=POS))

    # Arrow
    p.append(arrow(590, 210, 640, 210, color=NEG, sw=2.5))
    p.append(text(615, 195, "RotateLeft(10)", size=11, bold=True, color=NEG))

    # After RR
    t_rr_after = TN(20, 0, TN(10, 0, TN(5, 0), None), TN(30, 0))
    draw_tree(p, t_rr_after, X0=660, Y0=140, COL=38, ROW=55, r=18, fs=12,
              mark={20: (GRN_F, GRN_S, INK), 10: (GRN_F, GRN_S, INK), 30: (GRN_F, GRN_S, INK), 5: (GRN_F, GRN_S, INK)})
    p.append(text(730, 335, "Після: BF(20) = 0", size=12, bold=True, color=FIELD))

    render(os.path.join(OUT, "single-rotation.svg"), W, H, *p, title="Малі обертання")

# ─────────────────────────────────────────────────────────────────────────────
# 3. double-rotation.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_double_rotation():
    W, H = 840, 460
    p = []

    p.append(text(W/2, 28, "Великі (подвійні) обертання: усунення зигзагоподібного перекосу LR та RL", size=16, bold=True, color=INK))

    # Left panel: LR Rotation
    p.append(rect(20, 50, 390, 390, fill="#fcfcfc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(215, 75, "Ліво-праве обертання (LR)", size=15, bold=True, color=POS))
    p.append(text(215, 95, "1) RotateLeft(лівий син) → 2) RotateRight(корінь)", size=12, color=MUTED))

    # Step 1: Initial LR imbalance
    t_lr1 = TN(30, -2, TN(10, 1, None, TN(20, 0)), TN(40, 0))
    draw_tree(p, t_lr1, X0=35, Y0=130, COL=32, ROW=50, r=16, fs=11,
              mark={30: (RED_F, RED_S, POS), 10: (BLUE_F, BLUE_S, INK), 20: (GRN_F, GRN_S, INK)})
    p.append(text(90, 305, "1. Зигзаг: BF(30)=-2, BF(10)=+1", size=10, bold=True, color=POS))

    # Arrow 1
    p.append(arrow(145, 200, 175, 200, color=NEG, sw=2.0))
    p.append(text(160, 185, "L(10)", size=10, bold=True, color=NEG))

    # Step 2: After Left rotation on left child
    t_lr2 = TN(30, -2, TN(20, -1, TN(10, 0), None), TN(40, 0))
    draw_tree(p, t_lr2, X0=175, Y0=130, COL=32, ROW=50, r=16, fs=11,
              mark={30: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})
    p.append(text(230, 305, "2. Пряма лінія (LL)", size=10, bold=True, color=NEG))

    # Arrow 2
    p.append(arrow(285, 200, 315, 200, color=NEG, sw=2.0))
    p.append(text(300, 185, "R(30)", size=10, bold=True, color=NEG))

    # Step 3: Balanced
    t_lr3 = TN(20, 0, TN(10, 0), TN(30, 0, None, TN(40, 0)))
    draw_tree(p, t_lr3, X0=300, Y0=130, COL=30, ROW=50, r=16, fs=11,
              mark={20: (GRN_F, GRN_S, INK)})
    p.append(text(345, 305, "3. Збалансовано", size=10, bold=True, color=FIELD))

    # Right panel: RL Rotation
    p.append(rect(430, 50, 390, 390, fill="#fcfcfc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(625, 75, "Право-ліве обертання (RL)", size=15, bold=True, color=POS))
    p.append(text(625, 95, "1) RotateRight(правий син) → 2) RotateLeft(корінь)", size=12, color=MUTED))

    # Step 1: Initial RL imbalance
    t_rl1 = TN(10, 2, TN(5, 0), TN(30, -1, TN(20, 0), None))
    draw_tree(p, t_rl1, X0=445, Y0=130, COL=32, ROW=50, r=16, fs=11,
              mark={10: (RED_F, RED_S, POS), 30: (BLUE_F, BLUE_S, INK), 20: (GRN_F, GRN_S, INK)})
    p.append(text(500, 305, "1. Зигзаг: BF(10)=+2, BF(30)=-1", size=10, bold=True, color=POS))

    # Arrow 1
    p.append(arrow(555, 200, 585, 200, color=NEG, sw=2.0))
    p.append(text(570, 185, "R(30)", size=10, bold=True, color=NEG))

    # Step 2: After Right rotation on right child
    t_rl2 = TN(10, 2, TN(5, 0), TN(20, 1, None, TN(30, 0)))
    draw_tree(p, t_rl2, X0=585, Y0=130, COL=32, ROW=50, r=16, fs=11,
              mark={10: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})
    p.append(text(640, 305, "2. Пряма лінія (RR)", size=10, bold=True, color=NEG))

    # Arrow 2
    p.append(arrow(695, 200, 725, 200, color=NEG, sw=2.0))
    p.append(text(710, 185, "L(10)", size=10, bold=True, color=NEG))

    # Step 3: Balanced
    t_rl3 = TN(20, 0, TN(10, 0, TN(5, 0), None), TN(30, 0))
    draw_tree(p, t_rl3, X0=710, Y0=130, COL=30, ROW=50, r=16, fs=11,
              mark={20: (GRN_F, GRN_S, INK)})
    p.append(text(755, 305, "3. Збалансовано", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "double-rotation.svg"), W, H, *p, title="Великі обертання")

# ─────────────────────────────────────────────────────────────────────────────
# 4. insertion-rebalance.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_insertion_rebalance():
    W, H = 840, 420
    p = []

    p.append(text(W/2, 28, "Процес вставки в AVL-дерево: спуск до листка → повернення стеком → одне обертання", size=15, bold=True, color=INK))

    # Stage 1: Insert 25
    p.append(rect(20, 55, 255, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(147, 80, "Крок 1. Звичайна BST-вставка", size=13, bold=True, color=INK))
    p.append(text(147, 98, "Ключ 25 додано як листок", size=11, color=MUTED))
    t1 = TN(30, -1, TN(10, 1, None, TN(20, 1, None, TN(25, 0))), TN(40, 0))
    draw_tree(p, t1, X0=30, Y0=130, COL=25, ROW=48, r=15, fs=11, mark={25: (GRN_F, GRN_S, INK)})

    # Arrow 1
    p.append(arrow(280, 220, 305, 220, color=LINE, sw=2.0))

    # Stage 2: Imbalance detected
    p.append(rect(310, 55, 255, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(437, 80, "Крок 2. Перерахунок BF", size=13, bold=True, color=POS))
    p.append(text(437, 98, "Виявлено BF(10) = +2, BF(20) = +1", size=11, color=POS))
    t2 = TN(30, -2, TN(10, 2, None, TN(20, 1, None, TN(25, 0))), TN(40, 0))
    draw_tree(p, t2, X0=320, Y0=130, COL=25, ROW=48, r=15, fs=11, mark={10: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})

    # Arrow 2
    p.append(arrow(570, 220, 595, 220, color=FIELD, sw=2.0))

    # Stage 3: Rebalanced with Left Rotation at 10
    p.append(rect(600, 55, 220, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(710, 80, "Крок 3. RotateLeft(10)", size=13, bold=True, color=FIELD))
    p.append(text(710, 98, "Дерево знову збалансоване", size=11, color=FIELD))
    t3 = TN(30, -1, TN(20, 0, TN(10, 0), TN(25, 0)), TN(40, 0))
    draw_tree(p, t3, X0=608, Y0=130, COL=27, ROW=48, r=15, fs=11, mark={20: (GRN_F, GRN_S, INK), 10: (GRN_F, GRN_S, INK), 25: (GRN_F, GRN_S, INK)})

    render(os.path.join(OUT, "insertion-rebalance.svg"), W, H, *p, title="Вставка та балансування")

# ─────────────────────────────────────────────────────────────────────────────
# 5. deletion-rebalance.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_deletion_rebalance():
    W, H = 840, 420
    p = []

    p.append(text(W/2, 28, "Видалення з AVL-дерева: заміщення наступником та каскадне балансування вгору", size=15, bold=True, color=INK))

    # Panel 1: Tree before deletion
    p.append(rect(20, 55, 255, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(147, 80, "1. Видаляємо вузол 40", size=13, bold=True, color=POS))
    p.append(text(147, 98, "Заміщуємо наступником 50", size=11, color=MUTED))
    t1 = TN(30, 1, TN(20, 0, TN(10, 0), None), TN(40, 1, None, TN(50, 0)))
    draw_tree(p, t1, X0=30, Y0=130, COL=28, ROW=48, r=15, fs=11, mark={40: (RED_F, RED_S, POS), 50: (GRN_F, GRN_S, INK)})

    # Arrow 1
    p.append(arrow(280, 220, 305, 220, color=LINE, sw=2.0))

    # Panel 2: After removal of 40 & node replacement, balance factor check
    p.append(rect(310, 55, 255, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(437, 80, "2. Зсув висоти вгору", size=13, bold=True, color=POS))
    p.append(text(437, 98, "Виникає перекіс BF(30) = -2", size=11, color=POS))
    t2 = TN(30, -2, TN(20, -1, TN(10, 0), None), TN(50, 0))
    draw_tree(p, t2, X0=320, Y0=130, COL=28, ROW=48, r=15, fs=11, mark={30: (RED_F, RED_S, POS), 20: (BLUE_F, BLUE_S, INK)})

    # Arrow 2
    p.append(arrow(570, 220, 595, 220, color=FIELD, sw=2.0))

    # Panel 3: After RotateRight(30)
    p.append(rect(600, 55, 220, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(710, 80, "3. RotateRight(30)", size=13, bold=True, color=FIELD))
    p.append(text(710, 98, "Баланс відновлено до кореня", size=11, color=FIELD))
    t3 = TN(20, 0, TN(10, 0), TN(30, 0, None, TN(50, 0)))
    draw_tree(p, t3, X0=608, Y0=130, COL=26, ROW=48, r=15, fs=11, mark={20: (GRN_F, GRN_S, INK), 30: (GRN_F, GRN_S, INK)})

    render(os.path.join(OUT, "deletion-rebalance.svg"), W, H, *p, title="Видалення та каскадне балансування")

if __name__ == "__main__":
    fig_invariant()
    fig_single_rotation()
    fig_double_rotation()
    fig_insertion_rebalance()
    fig_deletion_rebalance()
    print("Всі 5 фігур AVL-дерева успішно згенеровано у теці img/")
