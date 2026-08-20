# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_rtree_concept():
    # Diagram showing 2D spatial objects in MBRs on the left, and corresponding R-tree hierarchy on the right
    W, H = 960, 490
    p = []

    p.append(text(W / 2, 28, "Просторове розміщення MBR та ієрархія вузлів R-дерева", size=16, bold=True))
    p.append(text(W / 2, 52, "Геометричні об'єкти групуються в ієрархічні прямокутники без фрагментації контурів", size=13, color=MUTED))

    # Left side: 2D Spatial plane (MBRs)
    px, py, pw, ph = 40, 80, 420, 380
    p.append(rect(px, py, pw, ph, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(px + 20, py + 25, "Простір координат (2D Площина)", size=12, bold=True, color=MUTED, anchor="start"))

    # Root MBRs (R1 and R2)
    # R1: covers A, B, C
    p.append(rect(px + 25, py + 45, 175, 305, fill="#eaf2f8", stroke=NEG, sw=2, rx=4))
    p.append(text(px + 35, py + 68, "MBR R1", size=13, bold=True, color=NEG, anchor="start"))

    # R2: covers D, E, F
    p.append(rect(px + 180, py + 75, 215, 275, fill="#eafaf0", stroke=FIELD, sw=2, rx=4))
    p.append(text(px + 370, py + 98, "MBR R2", size=13, bold=True, color=FIELD, anchor="end"))

    # Sub-MBRs inside R1 (Leaf level MBRs: L1 and L2)
    # L1: contains Poly A and Poly B
    p.append(rect(px + 35, py + 85, 150, 115, fill="#ffffff", stroke="#5dade2", sw=1.5, rx=3))
    p.append(text(px + 45, py + 104, "L1", size=11, bold=True, color="#2980b9", anchor="start"))
    # Object A (polygon/box)
    p.append(rect(px + 45, py + 115, 55, 35, fill="#d4e6f1", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 72, py + 137, "Об'єкт A", size=10, bold=True))
    # Object B (polygon/box)
    p.append(rect(px + 115, py + 145, 60, 45, fill="#d4e6f1", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 145, py + 172, "Об'єкт B", size=10, bold=True))

    # L2: contains Poly C
    p.append(rect(px + 40, py + 220, 140, 115, fill="#ffffff", stroke="#5dade2", sw=1.5, rx=3))
    p.append(text(px + 50, py + 239, "L2", size=11, bold=True, color="#2980b9", anchor="start"))
    # Object C
    p.append(rect(px + 55, py + 250, 110, 65, fill="#d4e6f1", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 110, py + 287, "Об'єкт C", size=10, bold=True))

    # Sub-MBRs inside R2 (Leaf level MBRs: L3 and L4)
    # L3: contains Poly D and Poly E
    p.append(rect(px + 200, py + 115, 180, 105, fill="#ffffff", stroke="#58d68d", sw=1.5, rx=3))
    p.append(text(px + 210, py + 134, "L3", size=11, bold=True, color="#229954", anchor="start"))
    # Object D
    p.append(rect(px + 210, py + 145, 65, 55, fill="#d5f5e3", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 242, py + 177, "Об'єкт D", size=10, bold=True))
    # Object E
    p.append(rect(px + 295, py + 130, 75, 40, fill="#d5f5e3", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 332, py + 155, "Об'єкт E", size=10, bold=True))

    # L4: contains Poly F
    p.append(rect(px + 230, py + 240, 145, 95, fill="#ffffff", stroke="#58d68d", sw=1.5, rx=3))
    p.append(text(px + 240, py + 259, "L4", size=11, bold=True, color="#229954", anchor="start"))
    # Object F
    p.append(rect(px + 250, py + 270, 110, 50, fill="#d5f5e3", stroke=LINE, sw=1.2, rx=2))
    p.append(text(px + 305, py + 300, "Об'єкт F", size=10, bold=True))

    # Right side: R-tree graph hierarchy
    # Tree Root
    root_x, root_y = 700, 115
    p.append(rect(root_x - 90, root_y - 25, 180, 50, fill="#fdedec", stroke=POS, sw=2, rx=6))
    p.append(text(root_x, root_y - 5, "Корінь дерева", size=13, bold=True, color=POS))
    p.append(text(root_x, root_y + 14, "[ MBR R1 | MBR R2 ]", size=11, color=INK))

    # Level 1 Nodes (Internal Nodes R1, R2)
    r1_x, r1_y = 575, 220
    r2_x, r2_y = 825, 220

    # Edges Root -> R1, R2
    p.append(line(root_x - 45, root_y + 25, r1_x, r1_y - 25, color=LINE, sw=1.5))
    p.append(line(root_x + 45, root_y + 25, r2_x, r2_y - 25, color=LINE, sw=1.5))

    p.append(rect(r1_x - 75, r1_y - 25, 150, 50, fill="#eaf2f8", stroke=NEG, sw=1.8, rx=6))
    p.append(text(r1_x, r1_y - 5, "Вузол R1", size=13, bold=True, color=NEG))
    p.append(text(r1_x, r1_y + 14, "[ MBR L1 | MBR L2 ]", size=11, color=INK))

    p.append(rect(r2_x - 75, r2_y - 25, 150, 50, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(r2_x, r2_y - 5, "Вузол R2", size=13, bold=True, color=FIELD))
    p.append(text(r2_x, r2_y + 14, "[ MBR L3 | MBR L4 ]", size=11, color=INK))

    # Level 2 Nodes (Leaf Nodes L1, L2, L3, L4)
    l1_x, l1_y = 515, 335
    l2_x, l2_y = 635, 335
    l3_x, l3_y = 765, 335
    l4_x, l4_y = 885, 335

    # Edges R1 -> L1, L2
    p.append(line(r1_x - 35, r1_y + 25, l1_x, l1_y - 22, color=LINE, sw=1.3))
    p.append(line(r1_x + 35, r1_y + 25, l2_x, l2_y - 22, color=LINE, sw=1.3))

    # Edges R2 -> L3, L4
    p.append(line(r2_x - 35, r2_y + 25, l3_x, l3_y - 22, color=LINE, sw=1.3))
    p.append(line(r2_x + 35, r2_y + 25, l4_x, l4_y - 22, color=LINE, sw=1.3))

    p.append(rect(l1_x - 50, l1_y - 22, 100, 44, fill="#ffffff", stroke="#5dade2", sw=1.3, rx=4))
    p.append(text(l1_x, l1_y - 4, "Листок L1", size=11, bold=True, color="#2980b9"))
    p.append(text(l1_x, l1_y + 12, "[Об'єкти A, B]", size=10, color=MUTED))

    p.append(rect(l2_x - 50, l2_y - 22, 100, 44, fill="#ffffff", stroke="#5dade2", sw=1.3, rx=4))
    p.append(text(l2_x, l2_y - 4, "Листок L2", size=11, bold=True, color="#2980b9"))
    p.append(text(l2_x, l2_y + 12, "[Об'єкт C]", size=10, color=MUTED))

    p.append(rect(l3_x - 50, l3_y - 22, 100, 44, fill="#ffffff", stroke="#58d68d", sw=1.3, rx=4))
    p.append(text(l3_x, l3_y - 4, "Листок L3", size=11, bold=True, color="#229954"))
    p.append(text(l3_x, l3_y + 12, "[Об'єкти D, E]", size=10, color=MUTED))

    p.append(rect(l4_x - 50, l4_y - 22, 100, 44, fill="#ffffff", stroke="#58d68d", sw=1.3, rx=4))
    p.append(text(l4_x, l4_y - 4, "Листок L4", size=11, bold=True, color="#229954"))
    p.append(text(l4_x, l4_y + 12, "[Об'єкт F]", size=10, color=MUTED))

    # Legend / Info box at bottom right
    p.append(rect(500, 405, 420, 52, fill="#f8f9fa", stroke=LINE, sw=1.2, rx=6))
    p.append(text(710, 424, "Інваріант: кожен внутрішній вузол покриває всі MBR своїх нащадків.", size=11, bold=True, color=INK))
    p.append(text(710, 444, "Листки зберігають точні координати обмежувальних рамок та id об'єктів.", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-rtree-concept.svg"), W, H, *p)


def fig_rtree_split_algorithms():
    # Diagram comparing Quadratic split, Linear split, and R*-tree forced reinsert
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Алгоритми розщеплення переповненого вузла (Node Split)", size=16, bold=True))
    p.append(text(W / 2, 52, "Вибір стратегії розподілу M+1 елементів на два нові вузли з мінімальним перекриттям", size=13, color=MUTED))

    # Box 1: Guttman Quadratic Split
    b1_x, b1_y, b1_w, b1_h = 40, 80, 270, 375
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(b1_x, b1_y, b1_w, 36, fill="#eaf2f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(b1_x + b1_w/2, b1_y + 23, "Квадратичний поділ Гутмана", size=13, bold=True, color=NEG))

    # Schematic visual for Quadratic split
    p.append(rect(b1_x + 20, b1_y + 55, 230, 160, fill="#fdfefe", stroke=MUTED, sw=1, rx=4))
    # Seed 1 (E1)
    p.append(rect(b1_x + 30, b1_y + 65, 50, 40, fill="#d4e6f1", stroke=NEG, sw=1.5, rx=3))
    p.append(text(b1_x + 55, b1_y + 89, "E1", size=11, bold=True, color=NEG))
    # Seed 2 (E2)
    p.append(rect(b1_x + 185, b1_y + 160, 55, 45, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(b1_x + 212, b1_y + 187, "E2", size=11, bold=True, color=FIELD))
    # Other items
    p.append(rect(b1_x + 95, b1_y + 80, 45, 35, fill="#f2f3f4", stroke=LINE, sw=1.2, rx=2))
    p.append(text(b1_x + 117, b1_y + 102, "E3", size=10))
    p.append(rect(b1_x + 140, b1_y + 130, 40, 35, fill="#f2f3f4", stroke=LINE, sw=1.2, rx=2))
    p.append(text(b1_x + 160, b1_y + 152, "E4", size=10))

    p.append(text(b1_x + b1_w/2, b1_y + 240, "1. PickSeeds: пара з max мертвою", size=11, bold=True, color=INK))
    p.append(text(b1_x + b1_w/2, b1_y + 258, "площею: Area(E1∪E2) - Area(E1) - Area(E2)", size=10, color=MUTED))
    p.append(text(b1_x + b1_w/2, b1_y + 282, "2. PickNext: черговий об'єкт із max", size=11, bold=True, color=INK))
    p.append(text(b1_x + b1_w/2, b1_y + 300, "різницею переваги |ΔA1 - ΔA2|", size=10, color=MUTED))
    p.append(text(b1_x + b1_w/2, b1_y + 334, "Складність: O(M²)", size=12, bold=True, color=NEG))
    p.append(text(b1_x + b1_w/2, b1_y + 354, "Якісний розподіл простору", size=10, color=MUTED))

    # Box 2: Guttman Linear Split
    b2_x, b2_y, b2_w, b2_h = 345, 80, 270, 375
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(b2_x, b2_y, b2_w, 36, fill="#fef9e7", stroke=LINE, sw=1.5, rx=6))
    p.append(text(b2_x + b2_w/2, b2_y + 23, "Лінійний поділ Гутмана", size=13, bold=True, color="#b7950b"))

    # Schematic visual for Linear split
    p.append(rect(b2_x + 20, b2_y + 55, 230, 160, fill="#fdfefe", stroke=MUTED, sw=1, rx=4))
    # Axis projection lines
    p.append(line(b2_x + 30, b2_y + 195, b2_x + 235, b2_y + 195, color="#b7950b", sw=1.5))
    p.append(line(b2_x + 30, b2_y + 190, b2_x + 30, b2_y + 200, color="#b7950b", sw=1.5))
    p.append(line(b2_x + 235, b2_y + 190, b2_x + 235, b2_y + 200, color="#b7950b", sw=1.5))
    p.append(text(b2_x + 132, b2_y + 185, "вісь X (max розрив)", size=9, color="#7d6608"))

    # Seed Xmin
    p.append(rect(b2_x + 30, b2_y + 70, 45, 50, fill="#fef5e7", stroke="#b7950b", sw=1.5, rx=3))
    p.append(text(b2_x + 52, b2_y + 98, "S1", size=11, bold=True, color="#b7950b"))
    # Seed Xmax
    p.append(rect(b2_x + 190, b2_y + 110, 45, 55, fill="#fef5e7", stroke="#b7950b", sw=1.5, rx=3))
    p.append(text(b2_x + 212, b2_y + 141, "S2", size=11, bold=True, color="#b7950b"))

    p.append(text(b2_x + b2_w/2, b2_y + 240, "1. Знаходження крайнощів на осях:", size=11, bold=True, color=INK))
    p.append(text(b2_x + b2_w/2, b2_y + 258, "найбільша відстань між гранями MBR", size=10, color=MUTED))
    p.append(text(b2_x + b2_w/2, b2_y + 282, "2. Нормалізація за шириною осі та", size=11, bold=True, color=INK))
    p.append(text(b2_x + b2_w/2, b2_y + 300, "жадібний розподіл решти записів", size=10, color=MUTED))
    p.append(text(b2_x + b2_w/2, b2_y + 334, "Складність: O(M)", size=12, bold=True, color="#b7950b"))
    p.append(text(b2_x + b2_w/2, b2_y + 354, "Швидкий, але MBR можуть перекриватись", size=10, color=MUTED))

    # Box 3: R*-tree Forced Reinsert & Split
    b3_x, b3_y, b3_w, b3_h = 650, 80, 270, 375
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(b3_x, b3_y, b3_w, 36, fill="#eafaf0", stroke=LINE, sw=1.5, rx=6))
    p.append(text(b3_x + b3_w/2, b3_y + 23, "R*-дерево: Reinsert + Split", size=13, bold=True, color=FIELD))

    # Schematic visual for R*
    p.append(rect(b3_x + 20, b3_y + 55, 230, 160, fill="#fdfefe", stroke=MUTED, sw=1, rx=4))
    # Center cross
    p.append(line(b3_x + 135, b3_y + 125, b3_x + 135, b3_y + 145, color=MUTED, sw=1))
    p.append(line(b3_x + 125, b3_y + 135, b3_x + 145, b3_y + 135, color=MUTED, sw=1))
    p.append(text(b3_x + 135, b3_y + 115, "центр MBR", size=9, color=MUTED))

    # Central items (kept)
    p.append(rect(b3_x + 105, b3_y + 135, 60, 35, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(b3_x + 135, b3_y + 156, "Зберегти", size=9, bold=True, color=FIELD))
    # Outer items (reinserted)
    p.append(rect(b3_x + 30, b3_y + 65, 55, 35, fill="#fdedec", stroke=POS, sw=1.5, rx=3))
    p.append(text(b3_x + 57, b3_y + 86, "Reinsert", size=9, bold=True, color=POS))
    p.append(rect(b3_x + 185, b3_y + 165, 55, 35, fill="#fdedec", stroke=POS, sw=1.5, rx=3))
    p.append(text(b3_x + 212, b3_y + 186, "Reinsert", size=9, bold=True, color=POS))

    p.append(text(b3_x + b3_w/2, b3_y + 240, "1. Forced Reinsert (30% записів):", size=11, bold=True, color=INK))
    p.append(text(b3_x + b3_w/2, b3_y + 258, "вилучення найвіддаленіших і вставка з кореня", size=10, color=MUTED))
    p.append(text(b3_x + b3_w/2, b3_y + 282, "2. Split за віссю з min периметром", size=11, bold=True, color=INK))
    p.append(text(b3_x + b3_w/2, b3_y + 300, "та точкою з min перекриттям (Overlap)", size=10, color=MUTED))
    p.append(text(b3_x + b3_w/2, b3_y + 334, "Складність: O(M · log M)", size=12, bold=True, color=FIELD))
    p.append(text(b3_x + b3_w/2, b3_y + 354, "Мінімальне перекриття, найкращий пошук", size=10, color=MUTED))

    render(os.path.join(OUT, "fig-rtree-split-algorithms.svg"), W, H, *p)


def fig_rtree_search_knn():
    # Diagram illustrating Spatial Range Query pruning and k-NN search with MINDIST/MINMAXDIST
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Просторовий пошук: віконний запит та k найближчих сусідів (k-NN)", size=16, bold=True))
    p.append(text(W / 2, 52, "Геометричне відсікання гілок дерева за допомогою прямокутника запиту та метрик відстані", size=13, color=MUTED))

    # Left box: Range Query (Window Intersection)
    bx1, by1, bw1, bh1 = 40, 75, 425, 375
    p.append(rect(bx1, by1, bw1, bh1, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx1, by1, bw1, 34, fill="#eaf2f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx1 + bw1/2, by1 + 22, "Віконний запит (Range / Intersection Query)", size=13, bold=True, color=NEG))

    # Spatial plane left
    # MBR 1 (Intersecting - Must traverse)
    p.append(rect(bx1 + 30, by1 + 60, 190, 160, fill="#eafaf0", stroke=FIELD, sw=2, rx=4))
    p.append(text(bx1 + 45, by1 + 80, "MBR Node 1 (Перетин)", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(rect(bx1 + 45, by1 + 95, 60, 45, fill="#d5f5e3", stroke=LINE, sw=1.2, rx=2))
    p.append(text(bx1 + 75, by1 + 122, "Об'єкт 1", size=10))
    p.append(rect(bx1 + 130, by1 + 140, 70, 60, fill="#fdedec", stroke=POS, sw=1.5, rx=2))
    p.append(text(bx1 + 165, by1 + 175, "Об'єкт 2 ✓", size=10, bold=True, color=POS))

    # MBR 2 (Disjoint - Pruned!)
    p.append(rect(bx1 + 240, by1 + 60, 160, 130, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=4))
    p.append(text(bx1 + 255, by1 + 80, "MBR Node 2 (Поза вікном)", size=11, bold=True, color=MUTED, anchor="start"))
    p.append(rect(bx1 + 260, by1 + 100, 60, 45, fill="#f2f3f4", stroke=MUTED, sw=1.2, rx=2))
    p.append(text(bx1 + 290, by1 + 127, "Об'єкт 3 ✗", size=10, color=MUTED))
    p.append(text(bx1 + 320, by1 + 165, "Гілка ВІДСІКАЄТЬСЯ", size=10, bold=True, color=POS))

    # Query Window Q
    p.append(rect(bx1 + 100, by1 + 120, 180, 190, fill="none", stroke=POS, sw=2.5, rx=4))
    p.append(text(bx1 + 270, by1 + 300, "Вікно запиту Q", size=12, bold=True, color=POS, anchor="end"))

    # Bottom notes left
    p.append(text(bx1 + bw1/2, by1 + 338, "Правило відсікання: якщо MBR ∩ Q == ∅ → не спускатися.", size=11, bold=True, color=INK))
    p.append(text(bx1 + bw1/2, by1 + 358, "Якщо MBR ∩ Q ≠ ∅ → рекурсивно перевірити дочірні вузли.", size=10, color=MUTED))

    # Right box: k-NN Query & Distance Pruning
    bx2, by2, bw2, bh2 = 495, 75, 425, 375
    p.append(rect(bx2, by2, bw2, bh2, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx2, by2, bw2, 34, fill="#eafaf0", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx2 + bw2/2, by2 + 22, "Пошук найближчих сусідів (k-NN з чергою)", size=13, bold=True, color=FIELD))

    # Query Point P
    qx, qy = bx2 + 75, by2 + 200
    p.append(circle(qx, qy, 6, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(qx - 12, qy - 8, "Точка P", size=12, bold=True, color=POS, anchor="end"))

    # MBR A (Close)
    p.append(rect(bx2 + 180, by2 + 75, 120, 85, fill="#eaf2f8", stroke=NEG, sw=1.8, rx=4))
    p.append(text(bx2 + 240, by2 + 95, "MBR Вузла A", size=11, bold=True, color=NEG))
    # Distance line P to MBR A (MINDIST)
    p.append(line(qx, qy, bx2 + 180, by2 + 130, color=NEG, sw=1.8))
    p.append(text(bx2 + 105, by2 + 140, "MINDIST(P, A)", size=10, bold=True, color=NEG))

    # MBR B (Farther)
    p.append(rect(bx2 + 230, by2 + 220, 160, 95, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=4))
    p.append(text(bx2 + 310, by2 + 242, "MBR Вузла B", size=11, bold=True, color=MUTED))
    p.append(line(qx, qy, bx2 + 230, by2 + 245, color=MUTED, sw=1.5))
    p.append(text(bx2 + 135, by2 + 250, "MINDIST(P, B)", size=10, color=MUTED))

    # Pruning text
    p.append(text(bx2 + 190, by2 + 180, "Радіус відсікання r_k", size=10, bold=True, color=POS))

    # Priority queue table at bottom right
    p.append(rect(bx2 + 20, by2 + 330, 385, 35, fill="#fdfefe", stroke=LINE, sw=1.2, rx=4))
    p.append(text(bx2 + bw2/2, by2 + 352, "Min-Купа: [ (MINDIST(A), Node A), (MINDIST(B), Node B) ]", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "fig-rtree-search-knn.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rtree_concept()
    fig_rtree_split_algorithms()
    fig_rtree_search_knn()
    print("All figures successfully generated in img/")
