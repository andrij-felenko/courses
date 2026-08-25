# -*- coding: utf-8 -*-
"""Фігури до статті «Декартове дерево (Treap)».
Генерує SVG-діаграми у теці img/:
1. treap-structure.svg — Анатомія вузла Treap і подвійний інваріант (BST за ключем, купа за пріоритетом).
2. treap-split.svg — Операція розрізання дерева split(T, k, L, R).
3. treap-merge.svg — Операція злиття двох дерев merge(T, L, R).
4. implicit-treap.svg — Неявне декартове дерево з розмірами піддерев sz[v].
5. lazy-reverse.svg — Ліниве проштовхування мітки реверсу підвідрізка (lazy propagation).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
GRN_F = "#eafaf0"
GRN_S = FIELD
RED_F = "#fdecea"
RED_S = POS
BLUE_F = "#eef6ff"
BLUE_S = NEG
FILL_GRAY = "#f4f6f8"

def draw_treap_node(cx, cy, key_text, prio_text, r=26, fill="#ffffff", stroke=LINE, sz_text=None):
    """Малює круглий або овальний вузол з ключем (вгорі) та пріоритетом (внизу)."""
    body = circle(cx, cy, r, fill=fill, stroke=stroke, sw=1.8)
    body += line(cx - r + 3, cy, cx + r - 3, cy, color=stroke, sw=1.0)
    body += text(cx, cy - 7, key_text, size=13, color=INK, bold=True)
    body += text(cx, cy + 13, prio_text, size=11, color=MUTED, bold=False)
    if sz_text is not None:
        body += text(cx + r + 14, cy - 10, f"sz={sz_text}", size=11, color=BLUE_S, bold=True, anchor="start")
    return body

# ==============================================================================
# Фігура 1: treap-structure.svg
# ==============================================================================
def fig_treap_structure():
    w, h = 860, 440
    frags = []

    # Ліва панель: Координатна площина (X = Key, Y = Priority)
    frags.append(rect(20, 20, 390, 390, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(215, 48, "Декартова площина (X = Ключ, Y = Пріоритет)", size=13, bold=True))

    # Осі
    frags.append(arrow(60, 370, 380, 370, color=LINE, sw=1.5)) # X axis
    frags.append(arrow(60, 370, 60, 70, color=LINE, sw=1.5))   # Y axis
    frags.append(text(385, 388, "X (Ключ)", size=12, bold=True, anchor="end"))
    frags.append(text(45, 75, "Y (Пріоритет)", size=12, bold=True, anchor="middle"))

    pts = [
        ("A", 100, 260, "A(3, 45)", 3, 45),
        ("B", 150, 130, "B(7, 92)", 7, 92),
        ("C", 220, 290, "C(12, 33)", 12, 33),
        ("D", 280, 190, "D(16, 78)", 16, 78),
        ("E", 340, 330, "E(22, 19)", 22, 19),
    ]

    # Сітка та точки
    for name, px, py, label, k, p in pts:
        frags.append(line(px, 370, px, py, color="#e1e4e8", sw=1.0, dash="3,3"))
        frags.append(line(60, py, px, py, color="#e1e4e8", sw=1.0, dash="3,3"))
        frags.append(circle(px, py, 6, fill=POS, stroke="#ffffff", sw=1.5))
        frags.append(text(px, py - 12, label, size=11, bold=True, color=INK))

    # Права панель: Відповідне декартове дерево
    frags.append(rect(430, 20, 410, 390, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(635, 48, "Отримане унікальне дерево (Treap)", size=13, bold=True))

    # Дерево: B(7,92) корінь; зліва A(3,45); справа D(16,78); у D зліва C(12,33), справа E(22,19)
    # Зв'язки
    frags.append(line(635, 110, 530, 190, color=LINE, sw=1.6))
    frags.append(line(635, 110, 740, 190, color=LINE, sw=1.6))
    frags.append(line(740, 190, 680, 280, color=LINE, sw=1.6))
    frags.append(line(740, 190, 800, 280, color=LINE, sw=1.6))

    # Вузли
    frags.append(draw_treap_node(635, 110, "k=7", "p=92", r=26, fill=RED_F, stroke=POS))
    frags.append(draw_treap_node(530, 190, "k=3", "p=45", r=26, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(740, 190, "k=16", "p=78", r=26, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(680, 280, "k=12", "p=33", r=24, fill="#ffffff", stroke=LINE))
    frags.append(draw_treap_node(800, 280, "k=22", "p=19", r=24, fill="#ffffff", stroke=LINE))

    # Пояснювальні підписи знизу правої панелі
    frags.append(rect(450, 335, 370, 58, fill=FILL_GRAY, stroke="#d0d7de", sw=1.0, rx=6))
    frags.append(text(635, 355, "Інваріант BST: 3 < 7 < 12 < 16 < 22", size=12, bold=True, color=FIELD))
    frags.append(text(635, 375, "Інваріант Max-Heap: p(7)=92 >= p(нащадків)", size=12, bold=True, color=POS))

    render(os.path.join(OUT, "treap-structure.svg"), w, h, *frags)

# ==============================================================================
# Фігура 2: treap-split.svg
# ==============================================================================
def fig_treap_split():
    w, h = 900, 420
    frags = []

    # Заголовок зверху
    frags.append(text(450, 28, "Розрізання дерева: split(T, key = 10, L, R)", size=16, bold=True))

    # Ліва частина: Початкове дерево T
    frags.append(rect(20, 50, 360, 350, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(200, 78, "Початкове дерево T", size=14, bold=True))

    # Вузли T: Корінь k=7, p=90; ліворуч k=3, p=60; праворуч k=14, p=80.
    # У k=14 ліворуч k=9, p=50; праворуч k=18, p=40.
    frags.append(line(200, 130, 110, 210, color=LINE, sw=1.6))
    frags.append(line(200, 130, 290, 210, color=LINE, sw=1.6))
    frags.append(line(290, 210, 230, 290, color=LINE, sw=1.6))
    frags.append(line(290, 210, 340, 290, color=LINE, sw=1.6))

    # Лінія розрізу пунктиром
    frags.append(line(220, 160, 280, 340, color=POS, sw=2.0, dash="5,4"))
    frags.append(text(300, 340, "Розріз k <= 10", size=11, color=POS, bold=True, anchor="start"))

    frags.append(draw_treap_node(200, 130, "7", "p:90", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(110, 210, "3", "p:60", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(290, 210, "14", "p:80", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(230, 290, "9", "p:50", r=22, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(340, 290, "18", "p:40", r=22, fill=BLUE_F, stroke=BLUE_S))

    # Стрілка переходу
    frags.append(arrow(395, 220, 445, 220, color=POS, sw=2.5))
    frags.append(text(420, 205, "split", size=13, color=POS, bold=True))

    # Права частина: Результат L і R
    frags.append(rect(460, 50, 420, 350, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))

    # Піддерево L (keys <= 10): 7 (корінь), ліворуч 3, праворуч 9
    frags.append(text(560, 78, "Дерево L (ключі <= 10)", size=13, color=FIELD, bold=True))
    frags.append(line(560, 130, 500, 210, color=LINE, sw=1.6))
    frags.append(line(560, 130, 620, 210, color=LINE, sw=1.6))
    frags.append(draw_treap_node(560, 130, "7", "p:90", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(500, 210, "3", "p:60", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(620, 210, "9", "p:50", r=24, fill=GRN_F, stroke=FIELD))

    # Піддерево R (keys > 10): 14 (корінь), праворуч 18, лівий син тепер NULL
    frags.append(text(770, 78, "Дерево R (ключі > 10)", size=13, color=BLUE_S, bold=True))
    frags.append(line(770, 130, 830, 210, color=LINE, sw=1.6))
    frags.append(draw_treap_node(770, 130, "14", "p:80", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(830, 210, "18", "p:40", r=24, fill=BLUE_F, stroke=BLUE_S))

    # Підсумок знизу
    frags.append(rect(480, 335, 380, 50, fill=FILL_GRAY, stroke="#d0d7de", sw=1.0, rx=6))
    frags.append(text(670, 365, "Обидва дерева L та R зберігають BST і Heap", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "treap-split.svg"), w, h, *frags)

# ==============================================================================
# Фігура 3: treap-merge.svg
# ==============================================================================
def fig_treap_merge():
    w, h = 900, 420
    frags = []

    frags.append(text(450, 28, "Злиття дерев: merge(T, L, R) за умови max_key(L) < min_key(R)", size=16, bold=True))

    # Ліва частина: Вхідні дерева L і R
    frags.append(rect(20, 50, 400, 350, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(120, 78, "Дерево L (keys <= 6)", size=13, color=FIELD, bold=True))
    frags.append(text(300, 78, "Дерево R (keys >= 10)", size=13, color=BLUE_S, bold=True))

    # Дерево L: корінь 4 (p:85), ліворуч 2 (p:40), праворуч 6 (p:60)
    frags.append(line(120, 130, 70, 210, color=LINE, sw=1.6))
    frags.append(line(120, 130, 170, 210, color=LINE, sw=1.6))
    frags.append(draw_treap_node(120, 130, "4", "p:85", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(70, 210, "2", "p:40", r=22, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(170, 210, "6", "p:60", r=22, fill=GRN_F, stroke=FIELD))

    # Дерево R: корінь 12 (p:70), праворуч 15 (p:55)
    frags.append(line(300, 140, 360, 220, color=LINE, sw=1.6))
    frags.append(draw_treap_node(300, 140, "12", "p:70", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(360, 220, "15", "p:55", r=22, fill=BLUE_F, stroke=BLUE_S))

    # Порівняння пріоритетів коренів
    frags.append(rect(40, 320, 360, 60, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(220, 342, "Порівняння: p(L.root)=85 > p(R.root)=70", size=12, bold=True, color=POS))
    frags.append(text(220, 364, "Вузол 4 стає новим коренем, а R зливається з L.right", size=11, color=INK))

    # Стрілка merge
    frags.append(arrow(430, 210, 480, 210, color=FIELD, sw=2.5))
    frags.append(text(455, 195, "merge", size=13, color=FIELD, bold=True))

    # Права частина: Результуюче дерево T
    frags.append(rect(495, 50, 385, 350, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(685, 78, "Результуюче дерево T = merge(L, R)", size=13, bold=True))

    # Вузли T: 4 (корінь); ліворуч 2; праворуч результат merge(6, R) -> 12 (бо 70 > 60);
    # у 12 ліворуч 6 (p:60), праворуч 15 (p:55).
    frags.append(line(685, 120, 580, 200, color=LINE, sw=1.6))
    frags.append(line(685, 120, 770, 200, color=LINE, sw=1.6))
    frags.append(line(770, 200, 720, 280, color=LINE, sw=1.6))
    frags.append(line(770, 200, 830, 280, color=LINE, sw=1.6))

    frags.append(draw_treap_node(685, 120, "4", "p:85", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(580, 200, "2", "p:40", r=22, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(770, 200, "12", "p:70", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(720, 280, "6", "p:60", r=22, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(830, 280, "15", "p:55", r=22, fill=BLUE_F, stroke=BLUE_S))

    frags.append(rect(520, 340, 340, 45, fill=FILL_GRAY, stroke="#d0d7de", sw=1.0, rx=6))
    frags.append(text(690, 367, "Ключі впорядковані: 2, 4, 6, 12, 15", size=12, bold=True, color=FIELD))

    render(os.path.join(OUT, "treap-merge.svg"), w, h, *frags)

# ==============================================================================
# Фігура 4: implicit-treap.svg
# ==============================================================================
def fig_implicit_treap():
    w, h = 880, 450
    frags = []

    frags.append(text(440, 28, "Неявне декартове дерево: динамічний масив [A, B, C, D, E, F]", size=16, bold=True))

    # Верхня частина: Логічний масив з 1-based індексами
    frags.append(rect(140, 55, 600, 60, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=6))
    items = [("1", "A"), ("2", "B"), ("3", "C"), ("4", "D"), ("5", "E"), ("6", "F")]
    for i, (idx, val) in enumerate(items):
        bx = 170 + i * 95
        frags.append(rect(bx, 65, 80, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(bx + 40, 83, f"val: {val}", size=12, bold=True))
        frags.append(text(bx + 40, 100, f"idx: {idx}", size=10, color=MUTED))

    # Дерево для масиву:
    # Корінь: D (idx 4, sz=6, p=95)
    # Лівий син D: B (idx 2, sz=3, p=75) -> лівий син A (idx 1, sz=1, p=40), правий син C (idx 3, sz=1, p=50)
    # Правий син D: E (idx 5, sz=2, p=80) -> правий син F (idx 6, sz=1, p=30)

    # Зв'язки
    frags.append(line(440, 180, 280, 260, color=LINE, sw=1.6))
    frags.append(line(440, 180, 620, 260, color=LINE, sw=1.6))
    frags.append(line(280, 260, 200, 340, color=LINE, sw=1.6))
    frags.append(line(280, 260, 360, 340, color=LINE, sw=1.6))
    frags.append(line(620, 260, 710, 340, color=LINE, sw=1.6))

    # Вузли з sz
    frags.append(draw_treap_node(440, 180, "val: 'D'", "p:95", r=28, fill=RED_F, stroke=POS, sz_text="6"))
    frags.append(draw_treap_node(280, 260, "val: 'B'", "p:75", r=26, fill=GRN_F, stroke=FIELD, sz_text="3"))
    frags.append(draw_treap_node(620, 260, "val: 'E'", "p:80", r=26, fill=BLUE_F, stroke=BLUE_S, sz_text="2"))

    frags.append(draw_treap_node(200, 340, "val: 'A'", "p:40", r=24, fill="#ffffff", stroke=LINE, sz_text="1"))
    frags.append(draw_treap_node(360, 340, "val: 'C'", "p:50", r=24, fill="#ffffff", stroke=LINE, sz_text="1"))
    frags.append(draw_treap_node(710, 340, "val: 'F'", "p:30", r=24, fill="#ffffff", stroke=LINE, sz_text="1"))

    # Пояснення обчислення позиції
    frags.append(rect(40, 395, 800, 42, fill=FILL_GRAY, stroke="#d0d7de", sw=1.0, rx=6))
    frags.append(text(440, 420, "Індекс вузла в поточному піддереві = sz[left] + 1. Наприклад, для D: sz[left] = sz[B] = 3 => позиція D = 4", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "implicit-treap.svg"), w, h, *frags)

# ==============================================================================
# Фігура 5: lazy-reverse.svg
# ==============================================================================
def fig_lazy_reverse():
    w, h = 900, 430
    frags = []

    frags.append(text(450, 28, "Ліниве проштовхування мітки реверсу (Lazy Reverse)", size=16, bold=True))

    # Ліва частина: Встановлення прапорця rev=true на корені підвідрізка
    frags.append(rect(20, 50, 400, 360, fill="#fafbfc", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(220, 78, "1. Накладання мітки rev=true", size=13, color=POS, bold=True))

    frags.append(line(220, 140, 140, 230, color=LINE, sw=1.6))
    frags.append(line(220, 140, 300, 230, color=LINE, sw=1.6))
    frags.append(line(140, 230, 90, 310, color=LINE, sw=1.6))
    frags.append(line(140, 230, 180, 310, color=LINE, sw=1.6))

    # Корінь із rev = 1
    frags.append(draw_treap_node(220, 140, "X", "p:90", r=26, fill=RED_F, stroke=POS))
    frags.append(rect(255, 120, 65, 22, fill=POS, stroke=POS, sw=1.0, rx=4))
    frags.append(text(287, 136, "rev=1", size=11, color="#ffffff", bold=True))

    frags.append(draw_treap_node(140, 230, "L", "p:70", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(300, 230, "R", "p:60", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(90, 310, "L.l", "p:30", r=20, fill="#ffffff", stroke=LINE))
    frags.append(draw_treap_node(180, 310, "L.r", "p:40", r=20, fill="#ffffff", stroke=LINE))

    frags.append(text(220, 375, "Реверс позначено за O(1) без обходу піддерева", size=11, bold=True, color=MUTED))

    # Стрілка проштовхування
    frags.append(arrow(430, 210, 480, 210, color=POS, sw=2.5))
    frags.append(text(455, 195, "push_down", size=12, color=POS, bold=True))

    # Права частина: Результат після push_down(X)
    frags.append(rect(495, 50, 385, 360, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=8))
    frags.append(text(685, 78, "2. Після спуску push_down(X)", size=13, color=FIELD, bold=True))

    frags.append(line(685, 140, 605, 230, color=LINE, sw=1.6))
    frags.append(line(685, 140, 765, 230, color=LINE, sw=1.6))
    frags.append(line(765, 230, 720, 310, color=LINE, sw=1.6))
    frags.append(line(765, 230, 810, 310, color=LINE, sw=1.6))

    # Корінь тепер rev=0, але сини поміняні місцями: ліворуч став R, праворуч став L
    frags.append(draw_treap_node(685, 140, "X", "p:90", r=26, fill="#ffffff", stroke=LINE))
    frags.append(rect(720, 120, 65, 22, fill=FILL_GRAY, stroke="#d0d7de", sw=1.0, rx=4))
    frags.append(text(752, 136, "rev=0", size=11, color=MUTED, bold=False))

    frags.append(draw_treap_node(605, 230, "R", "p:60", r=24, fill=BLUE_F, stroke=BLUE_S))
    frags.append(draw_treap_node(765, 230, "L", "p:70", r=24, fill=GRN_F, stroke=FIELD))
    frags.append(draw_treap_node(720, 310, "L.l", "p:30", r=20, fill="#ffffff", stroke=LINE))
    frags.append(draw_treap_node(810, 310, "L.r", "p:40", r=20, fill="#ffffff", stroke=LINE))

    # Позначки передачі прапорця
    frags.append(text(605, 275, "rev^=1", size=11, color=POS, bold=True))
    frags.append(text(765, 275, "rev^=1", size=11, color=POS, bold=True))

    frags.append(text(685, 375, "Сини поміняні місцями: R тепер лівий, L — правий", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "lazy-reverse.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_treap_structure()
    fig_treap_split()
    fig_treap_merge()
    fig_implicit_treap()
    fig_lazy_reverse()
    print("All Treap figures successfully generated.")
