# -*- coding: utf-8 -*-
"""Фігури до статті «Поворот дерева (Tree Rotation)».
Усі фігури генеруються чистою мовою Python без сторонніх залежностей через svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама
GRN_F = "#eafaf0"   # Заливка нових коренів / піднятих вузлів
GRN_S = FIELD       # Зелена рамка (#2b8a3e)
RED_F = "#fdecea"   # Заливка опущених вузлів
RED_S = POS         # Червона/помаранчева рамка
BAND  = "#eef6ff"   # Світло-синій фон піддерев
BAND_S = "#9db8de"  # Контур трикутника піддерева

def poly(pts, fill, stroke=BAND_S, opacity=1.0):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    op = ' fill-opacity="%.2f"' % opacity if opacity < 1 else ''
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4"%s/>' % (d, fill, stroke, op)

# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — Поодинокі повороти (Right Rotation & Left Rotation)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rotation_left_right():
    W, H = 860, 440
    p = []
    
    # Ліва частина: стан ДО правого повороту (після лівого)
    # Корінь Y (cx=220, cy=100), Лівий син X (cx=130, cy=180)
    # Піддерева: A під X (cx=70, cy=270), B під X (cx=190, cy=270), C під Y (cx=310, cy=270)
    
    # Піддерева трикутники
    p.append(poly([(70, 260), (35, 330), (105, 330)], BAND))
    p.append(text(70, 305, "A", size=16, color=INK, bold=True))
    
    p.append(poly([(190, 260), (155, 330), (225, 330)], BAND))
    p.append(text(190, 305, "B", size=16, color=INK, bold=True))
    
    p.append(poly([(310, 260), (275, 330), (345, 330)], BAND))
    p.append(text(310, 305, "C", size=16, color=INK, bold=True))
    
    # Ребра лівого стану
    p.append(line(220, 100, 130, 180, color=INK, sw=2.0))
    p.append(line(220, 100, 310, 260, color=INK, sw=2.0))
    p.append(line(130, 180, 70, 260, color=INK, sw=2.0))
    p.append(line(130, 180, 190, 260, color=INK, sw=2.0))
    
    # Вузли лівого стану
    p.append(circle(220, 100, 22, fill=RED_F, stroke=RED_S, sw=2.2))
    p.append(text(220, 106, "Y", size=17, color=INK, bold=True))
    
    p.append(circle(130, 180, 22, fill=GRN_F, stroke=GRN_S, sw=2.2))
    p.append(text(130, 186, "X", size=17, color=INK, bold=True))
    
    # Заголовок лівого стану
    p.append(text(190, 50, "Лівоважка конфігурація", size=14, color=MUTED, bold=True))
    
    # ── Центр: Двобічні стрілки переходу ──
    p.append(arrow(375, 175, 475, 175, color=FIELD, sw=2.6))
    p.append(text(425, 155, "Правий поворот", size=13.5, color=FIELD, bold=True))
    
    p.append(arrow(475, 215, 375, 215, color=POS, sw=2.6))
    p.append(text(425, 238, "Лівий поворот", size=13.5, color=POS, bold=True))
    
    # Права частина: стан ПІСЛЯ правого повороту
    # Корінь X (cx=640, cy=100), Правий син Y (cx=730, cy=180)
    # Піддерева: A під X (cx=550, cy=270), B під Y (cx=670, cy=270), C під Y (cx=790, cy=270)
    
    p.append(poly([(550, 260), (515, 330), (585, 330)], BAND))
    p.append(text(550, 305, "A", size=16, color=INK, bold=True))
    
    p.append(poly([(670, 260), (635, 330), (705, 330)], BAND))
    p.append(text(670, 305, "B", size=16, color=INK, bold=True))
    
    p.append(poly([(790, 260), (755, 330), (825, 330)], BAND))
    p.append(text(790, 305, "C", size=16, color=INK, bold=True))
    
    # Ребра правого стану
    p.append(line(640, 100, 550, 260, color=INK, sw=2.0))
    p.append(line(640, 100, 730, 180, color=INK, sw=2.0))
    p.append(line(730, 180, 670, 260, color=INK, sw=2.0))
    p.append(line(730, 180, 790, 260, color=INK, sw=2.0))
    
    # Вузли правого стану
    p.append(circle(640, 100, 22, fill=GRN_F, stroke=GRN_S, sw=2.2))
    p.append(text(640, 106, "X", size=17, color=INK, bold=True))
    
    p.append(circle(730, 180, 22, fill=RED_F, stroke=RED_S, sw=2.2))
    p.append(text(730, 186, "Y", size=17, color=INK, bold=True))
    
    # Заголовок правого стану
    p.append(text(670, 50, "Правоважка конфігурація", size=14, color=MUTED, bold=True))
    
    # Інваріант впорядкованості внизу
    p.append(line(50, 380, 810, 380, color="#d0d4da", sw=1.2, dash="4,4"))
    p.append(text(430, 410, "Інваріант центрового обходу в обох станах однаковий:  A < X < B < Y < C", 
                  size=14, color=INK, bold=True))
    
    render(os.path.join(OUT, "rotation-left-right.svg"), W, H, *p,
           title="Поодинокі повороти дерева: збереження центрового порядку")

# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — Подвійний поворот (Left-Right / LR Rotation)
# ─────────────────────────────────────────────────────────────────────────────
def fig_double_rotation():
    W, H = 960, 420
    p = []
    
    # 3 стани: Крок 0 (LR-дисбаланс) -> Крок 1 (після Left(X)) -> Крок 2 (після Right(Z))
    
    # --- Стан 1: Z(X(A, Y(B,C)), D) ---
    # Z at (140, 90), X at (80, 160), Y at (120, 230)
    p.append(line(140, 90, 80, 160, color=INK, sw=1.8))
    p.append(line(140, 90, 200, 160, color=INK, sw=1.8)) # D
    p.append(line(80, 160, 45, 230, color=INK, sw=1.8))  # A
    p.append(line(80, 160, 120, 230, color=INK, sw=1.8)) # Y
    p.append(line(120, 230, 95, 290, color=INK, sw=1.8)) # B
    p.append(line(120, 230, 145, 290, color=INK, sw=1.8)) # C
    
    p.append(poly([(45, 230), (25, 280), (65, 280)], BAND))
    p.append(text(45, 260, "A", size=13, color=INK))
    p.append(poly([(95, 290), (80, 335), (110, 335)], BAND))
    p.append(text(95, 317, "B", size=12, color=INK))
    p.append(poly([(145, 290), (130, 335), (160, 335)], BAND))
    p.append(text(145, 317, "C", size=12, color=INK))
    p.append(poly([(200, 160), (180, 220), (220, 220)], BAND))
    p.append(text(200, 195, "D", size=13, color=INK))
    
    p.append(circle(140, 90, 18, fill=RED_F, stroke=RED_S, sw=2.0))
    p.append(text(140, 95, "Z", size=15, color=INK, bold=True))
    p.append(circle(80, 160, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(80, 165, "X", size=15, color=INK, bold=True))
    p.append(circle(120, 230, 18, fill=GRN_F, stroke=GRN_S, sw=2.0))
    p.append(text(120, 235, "Y", size=15, color=INK, bold=True))
    
    p.append(text(120, 45, "1. Зигзаг (LR)", size=13.5, color=POS, bold=True))
    
    # Стрілка 1
    p.append(arrow(225, 180, 285, 180, color=INK, sw=2.0))
    p.append(text(255, 165, "Лівий (X)", size=12, color=INK, bold=True))
    
    # --- Стан 2: Z(Y(X(A,B), C), D) ---
    # Z at (440, 90), Y at (380, 160), X at (330, 230)
    p.append(line(440, 90, 380, 160, color=INK, sw=1.8))
    p.append(line(440, 90, 500, 160, color=INK, sw=1.8)) # D
    p.append(line(380, 160, 330, 230, color=INK, sw=1.8)) # X
    p.append(line(380, 160, 430, 230, color=INK, sw=1.8)) # C
    p.append(line(330, 230, 305, 290, color=INK, sw=1.8)) # A
    p.append(line(330, 230, 355, 290, color=INK, sw=1.8)) # B
    
    p.append(poly([(305, 290), (290, 335), (320, 335)], BAND))
    p.append(text(305, 317, "A", size=12, color=INK))
    p.append(poly([(355, 290), (340, 335), (370, 335)], BAND))
    p.append(text(355, 317, "B", size=12, color=INK))
    p.append(poly([(430, 230), (415, 280), (445, 280)], BAND))
    p.append(text(430, 260, "C", size=12, color=INK))
    p.append(poly([(500, 160), (480, 220), (520, 220)], BAND))
    p.append(text(500, 195, "D", size=13, color=INK))
    
    p.append(circle(440, 90, 18, fill=RED_F, stroke=RED_S, sw=2.0))
    p.append(text(440, 95, "Z", size=15, color=INK, bold=True))
    p.append(circle(380, 160, 18, fill=GRN_F, stroke=GRN_S, sw=2.0))
    p.append(text(380, 165, "Y", size=15, color=INK, bold=True))
    p.append(circle(330, 230, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(330, 235, "X", size=15, color=INK, bold=True))
    
    p.append(text(420, 45, "2. Лівоважка (LL)", size=13.5, color=MUTED, bold=True))
    
    # Стрілка 2
    p.append(arrow(525, 180, 585, 180, color=INK, sw=2.0))
    p.append(text(555, 165, "Правий (Z)", size=12, color=INK, bold=True))
    
    # --- Стан 3: Y(X(A,B), Z(C,D)) ---
    # Y at (760, 90), X at (690, 170), Z at (830, 170)
    p.append(line(760, 90, 690, 170, color=INK, sw=1.8))
    p.append(line(760, 90, 830, 170, color=INK, sw=1.8))
    p.append(line(690, 170, 655, 250, color=INK, sw=1.8)) # A
    p.append(line(690, 170, 725, 250, color=INK, sw=1.8)) # B
    p.append(line(830, 170, 795, 250, color=INK, sw=1.8)) # C
    p.append(line(830, 170, 865, 250, color=INK, sw=1.8)) # D
    
    p.append(poly([(655, 250), (635, 305), (675, 305)], BAND))
    p.append(text(655, 282, "A", size=13, color=INK))
    p.append(poly([(725, 250), (705, 305), (745, 305)], BAND))
    p.append(text(725, 282, "B", size=13, color=INK))
    p.append(poly([(795, 250), (775, 305), (815, 305)], BAND))
    p.append(text(795, 282, "C", size=13, color=INK))
    p.append(poly([(865, 250), (845, 305), (885, 305)], BAND))
    p.append(text(865, 282, "D", size=13, color=INK))
    
    p.append(circle(760, 90, 20, fill=GRN_F, stroke=GRN_S, sw=2.4))
    p.append(text(760, 96, "Y", size=16, color=INK, bold=True))
    p.append(circle(690, 170, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(690, 175, "X", size=15, color=INK, bold=True))
    p.append(circle(830, 170, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(830, 175, "Z", size=15, color=INK, bold=True))
    
    p.append(text(760, 45, "3. Збалансовано ✓", size=13.5, color=FIELD, bold=True))
    
    p.append(line(40, 365, 920, 365, color="#d0d4da", sw=1.2, dash="4,4"))
    p.append(text(480, 395, "Подвійний поворот LR спирається на два кроки: спрощення зигзага до лівоважкої форми, потім відновлення балансу", 
                  size=13.5, color=INK, bold=True))
    
    render(os.path.join(OUT, "double-rotation.svg"), W, H, *p,
           title="Подвійний поворот (LR-rotation): виправлення внутрішньої важкості")

# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — Алгоритм Day-Stout-Warren (DSW): Vine -> Balanced Tree
# ─────────────────────────────────────────────────────────────────────────────
def fig_dsw_algorithm():
    W, H = 880, 380
    p = []
    
    # Етап 1: Незбалансоване дерево (або список-виноградність vine)
    # 1 -> 2 -> 3 -> 4 -> 5 (усі вправо)
    p.append(text(160, 45, "Етап 1: Виноградна лоза (Vine)", size=14, color=POS, bold=True))
    p.append(text(160, 68, "Праві повороти утворюють список", size=12, color=MUTED))
    
    v_nodes = [1, 2, 3, 4, 5, 6, 7]
    vy0 = 100
    for i, val in enumerate(v_nodes):
        vx = 60 + i * 32
        vy = vy0 + i * 32
        if i < len(v_nodes) - 1:
            p.append(line(vx, vy, vx + 32, vy + 32, color=INK, sw=1.6))
        p.append(circle(vx, vy, 13, fill=RED_F, stroke=RED_S, sw=1.6))
        p.append(text(vx, vy + 4, str(val), size=12, color=INK, bold=True))
        
    p.append(text(160, 340, "Висота h = n = 7 (O(n))", size=12.5, color=POS, bold=True))
    
    # Перехідні стрілки в центрі
    p.append(arrow(310, 190, 430, 190, color=FIELD, sw=2.6))
    p.append(text(370, 170, "Ліві повороти", size=13, color=FIELD, bold=True))
    p.append(text(370, 212, "Серія згортань", size=12, color=MUTED))
    
    # Етап 2: Ідеально збалансоване двійкове дерево
    # Корінь 4 (cx=660, cy=110)
    # Лівий 2 (560, 180), Права 6 (760, 180)
    # Листки 1, 3, 5, 7
    p.append(text(660, 45, "Етап 2: Ідеальний баланс", size=14, color=FIELD, bold=True))
    p.append(text(660, 68, "Після O(n) повертань", size=12, color=MUTED))
    
    b_edges = [(660, 110, 560, 180), (660, 110, 760, 180),
               (560, 180, 510, 250), (560, 180, 610, 250),
               (760, 180, 710, 250), (760, 180, 810, 250)]
    for x1, y1, x2, y2 in b_edges:
        p.append(line(x1, y1, x2, y2, color=INK, sw=1.8))
        
    b_nodes = [(660, 110, "4", True),
               (560, 180, "2", False), (760, 180, "6", False),
               (510, 250, "1", False), (610, 250, "3", False),
               (710, 250, "5", False), (810, 250, "7", False)]
    for bx, by, val, is_r in b_nodes:
        f = GRN_F if is_r else FILL
        s = GRN_S if is_r else LINE
        p.append(circle(bx, by, 16, fill=f, stroke=s, sw=2.0))
        p.append(text(bx, by + 5, val, size=14, color=INK, bold=True))
        
    p.append(text(660, 340, "Висота h = ⌊log₂ n⌋ = 2 (O(log n))", size=12.5, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "dsw-algorithm.svg"), W, H, *p,
           title="Алгоритм Дей-Стоута-Воррена: відновлення балансу повертаннями")

# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — Перепідключення вказівників при лівому повороті (Pointer Re-linking)
# ─────────────────────────────────────────────────────────────────────────────
def fig_rotation_pointers():
    W, H = 840, 460
    p = []
    
    # Показуємо детальний процес повороту вказівників для rotate_left(X)
    # P (Parent) -> X (Left node) -> Y (Right node), B (Y's left child)
    
    # ── Ліва панель: Вказівники ДО повороту ──
    p.append(text(210, 45, "1. Стан вказівників ДО лівого повороту", size=13.5, color=INK, bold=True))
    
    # P (210, 90)
    p.append(circle(210, 90, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(210, 95, "P", size=15, color=INK, bold=True))
    p.append(text(210, 65, "Parent", size=11, color=MUTED))
    
    # X (150, 180)
    p.append(line(210, 90, 150, 180, color=INK, sw=1.8))
    p.append(circle(150, 180, 20, fill=RED_F, stroke=RED_S, sw=2.2))
    p.append(text(150, 185, "X", size=16, color=INK, bold=True))
    
    # Y (270, 250)
    p.append(line(150, 180, 270, 250, color=POS, sw=2.4))
    p.append(circle(270, 250, 20, fill=GRN_F, stroke=GRN_S, sw=2.2))
    p.append(text(270, 255, "Y", size=16, color=INK, bold=True))
    
    # B (210, 320)
    p.append(line(270, 250, 210, 320, color=FIELD, sw=2.2))
    p.append(poly([(210, 310), (185, 360), (235, 360)], BAND))
    p.append(text(210, 340, "B", size=14, color=INK, bold=True))
    p.append(text(250, 315, "Y->left", size=11, color=FIELD, bold=True))
    p.append(text(215, 210, "X->right", size=11, color=POS, bold=True))
    
    # ── Вертикальний роздільник ──
    p.append(line(420, 40, 420, 420, color="#d0d4da", sw=1.2, dash="4,4"))
    
    # ── Права панель: Вказівники ПІСЛЯ повороту ──
    p.append(text(630, 45, "2. Стан вказівників ПІСЛЯ лівого повороту", size=13.5, color=INK, bold=True))
    
    # P (630, 90)
    p.append(circle(630, 90, 18, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(630, 95, "P", size=15, color=INK, bold=True))
    
    # Y (630, 170) — новий корінь піддерева
    p.append(line(630, 90, 630, 170, color=GRN_S, sw=2.4))
    p.append(circle(630, 170, 20, fill=GRN_F, stroke=GRN_S, sw=2.2))
    p.append(text(630, 175, "Y", size=16, color=INK, bold=True))
    p.append(text(675, 130, "P->left = Y", size=11, color=GRN_S, bold=True))
    
    # X (550, 250) — новий лівий син Y
    p.append(line(630, 170, 550, 250, color=GRN_S, sw=2.4))
    p.append(circle(550, 250, 20, fill=RED_F, stroke=RED_S, sw=2.2))
    p.append(text(550, 255, "X", size=16, color=INK, bold=True))
    p.append(text(555, 200, "Y->left = X", size=11, color=GRN_S, bold=True))
    
    # B (610, 330) — тепер правий син X!
    p.append(line(550, 250, 610, 330, color=FIELD, sw=2.4))
    p.append(poly([(610, 320), (585, 370), (635, 370)], BAND))
    p.append(text(610, 350, "B", size=14, color=INK, bold=True))
    p.append(text(620, 280, "X->right = B", size=11, color=FIELD, bold=True))
    
    # Покроковий перелік операцій у кутку
    p.append(rect(450, 385, 360, 55, fill="#f8f9fa", stroke="#d0d4da", sw=1.0, rx=6))
    p.append(text(630, 403, "Кроки: 1) X->right = B  2) Y->left = X", size=12, color=INK, bold=True))
    p.append(text(630, 423, "3) P->link = Y  4) Оновлення parent-вказівників", size=12, color=MUTED))
    
    render(os.path.join(OUT, "rotation-pointers.svg"), W, H, *p,
           title="Перепідключення вказівників при лівому повороті дерева")

if __name__ == "__main__":
    fig_rotation_left_right()
    fig_double_rotation()
    fig_dsw_algorithm()
    fig_rotation_pointers()
    print("Tree rotation figures generated successfully in", OUT)
