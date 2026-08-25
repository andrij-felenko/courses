# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми «Тріангуляція Делоне».
Використовує спільну бібліотеку svgkit із scripts/."""

import sys
import os
import math

# Підключення svgkit із scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig1_empty_circumcircle():
    """Фігура 1: Критерій порожнього описаного кола та максимізація мінімального кута."""
    w, h = 940, 480
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Критерій Делоне: порожнє описане коло та максимізація мінімальних кутів", size=16, color=INK, bold=True))

    # Ліва панель: Не-Делоне (нелегальне ребро, вузькі трикутники)
    frags.append(rect(30, 70, 425, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(242, 98, "1. Не-Делоне тріангуляція (нелегальне ребро AB)", size=13.5, color=POS, bold=True))

    pA_1 = (242, 140)
    pB_1 = (242, 330)
    pC_1 = (120, 235)
    pD_1 = (300, 235)

    # Заливка трикутників
    frags.append(f'<polygon points="{pA_1[0]},{pA_1[1]} {pB_1[0]},{pB_1[1]} {pC_1[0]},{pC_1[1]}" fill="#fee2e2" stroke="none"/>')
    frags.append(f'<polygon points="{pA_1[0]},{pA_1[1]} {pB_1[0]},{pB_1[1]} {pD_1[0]},{pD_1[1]}" fill="#fee2e2" stroke="none"/>')

    # Описане коло ΔABC (червоне пунктирне)
    frags.append('<circle cx="218.0" cy="235.0" r="98.0" fill="none" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="5 3"/>')

    # Ребра чотирикутника
    edges_left = [
        (pA_1, pC_1), (pC_1, pB_1), (pB_1, pD_1), (pD_1, pA_1)
    ]
    for (x1, y1), (x2, y2) in edges_left:
        frags.append(line(x1, y1, x2, y2, color=INK, sw=1.8))

    # Нелегальна діагональ AB
    frags.append(line(pA_1[0], pA_1[1], pB_1[0], pB_1[1], color=POS, sw=2.5))

    # Гострий кут α
    frags.append('<path d="M 242 165 A 25 25 0 0 1 230 156" fill="none" stroke="#dc2626" stroke-width="2"/>')
    frags.append(text(215, 172, "α (малий)", size=11, color=POS, bold=True))

    # Вершини
    for pt, lab, pos_off in [(pA_1, "A", (0, -12)), (pB_1, "B", (0, 18)), (pC_1, "C", (-14, 4)), (pD_1, "D (всередині кола!)", (16, 4))]:
        frags.append(circle(pt[0], pt[1], 5.5, fill="#0284c7" if "D" not in lab else POS, stroke="#ffffff", sw=2))
        frags.append(text(pt[0] + pos_off[0], pt[1] + pos_off[1], lab, size=12, color=INK if "D" not in lab else POS, bold=True))

    frags.append(text(242, 375, "D потрапляє у відкритий круг ΔABC", size=12, color=POS, bold=True))
    frags.append(text(242, 395, "Ребро AB не є легальним (порушено критерій Делоне)", size=11, color=MUTED))


    # Права панель: Делоне після перекидання ребра (фліп CD)
    frags.append(rect(485, 70, 425, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(697, 98, "2. Тріангуляція Делоне (після фліпу: ребро CD)", size=13.5, color="#166534", bold=True))

    pA_2 = (697, 140)
    pB_2 = (697, 330)
    pC_2 = (575, 235)
    pD_2 = (755, 235)

    # Заливка трикутників
    frags.append(f'<polygon points="{pC_2[0]},{pC_2[1]} {pD_2[0]},{pD_2[1]} {pA_2[0]},{pA_2[1]}" fill="#dcfce7" stroke="none"/>')
    frags.append(f'<polygon points="{pC_2[0]},{pC_2[1]} {pD_2[0]},{pD_2[1]} {pB_2[0]},{pB_2[1]}" fill="#dcfce7" stroke="none"/>')

    # Описане коло ΔACD
    frags.append('<circle cx="665.0" cy="224.7" r="90.6" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="5 3"/>')

    # Описане коло ΔBCD
    frags.append('<circle cx="665.0" cy="245.3" r="90.6" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="5 3"/>')

    # Ребра чотирикутника
    edges_right = [
        (pA_2, pC_2), (pC_2, pB_2), (pB_2, pD_2), (pD_2, pA_2)
    ]
    for (x1, y1), (x2, y2) in edges_right:
        frags.append(line(x1, y1, x2, y2, color=INK, sw=1.8))

    # Легальна діагональ CD (зелена)
    frags.append(line(pC_2[0], pC_2[1], pD_2[0], pD_2[1], color="#16a34a", sw=2.5))

    # Більший кут β
    frags.append('<path d="M 605 235 A 30 30 0 0 1 596 210" fill="none" stroke="#16a34a" stroke-width="2"/>')
    frags.append(text(625, 218, "β > α", size=11, color="#166534", bold=True))

    # Вершини
    for pt, lab, pos_off in [(pA_2, "A", (0, -12)), (pB_2, "B", (0, 18)), (pC_2, "C", (-14, 4)), (pD_2, "D", (14, 4))]:
        frags.append(circle(pt[0], pt[1], 5.5, fill="#16a34a", stroke="#ffffff", sw=2))
        frags.append(text(pt[0] + pos_off[0], pt[1] + pos_off[1], lab, size=12, color=INK, bold=True))

    frags.append(text(697, 375, "Обидва описані кола є порожніми", size=12, color="#166534", bold=True))
    frags.append(text(697, 395, "Мінімальний внутрішній кут максимізовано (β > α)", size=11, color=MUTED))

    # Пояснювальна плашка внизу
    frags.append(rect(40, 428, 860, 40, fill="#f0fdf4", stroke="#86efac", sw=1, rx=5))
    frags.append(text(w / 2, 452, "Лема Лоусона: перекидання нелегального ребра строго збільшує вектор відсортованих кутів у лексикографічному порядку", size=11.5, color="#166534", bold=True))

    render(os.path.join(OUT, "delaunay-empty-circumcircle.svg"), w, h, *frags)


def fig2_paraboloid_lifting():
    """Фігура 2: Геометричне відображення на 3D-параболоїд z = x² + y² та предикат InCircle."""
    w, h = 920, 500
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Зв'язок із 3D-простором: відображення на параболоїд z = x² + y²", size=16, color=INK, bold=True))

    # Ліва частина: 2D площина
    frags.append(rect(35, 75, 380, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(225, 102, "2D-площина: описане коло ΔABC", size=13.5, color="#1e40af", bold=True))

    # Осі 2D
    frags.append(line(70, 420, 380, 420, color="#94a3b8", sw=1.2))
    frags.append(line(80, 430, 80, 130, color="#94a3b8", sw=1.2))
    frags.append(text(375, 435, "X", size=11, color=MUTED, bold=True))
    frags.append(text(68, 135, "Y", size=11, color=MUTED, bold=True))

    # Точки 2D
    pA2 = (160, 310)
    pB2 = (300, 340)
    pC2 = (240, 200)
    pD2_in = (220, 280)    # всередині кола
    pE2_out = (330, 220)   # зовні кола

    # Коло ABC: центр (228.6, 284.3), R = 73.1
    c2_x, c2_y, c2_r = 228.6, 284.3, 73.1
    frags.append(f'<circle cx="{c2_x:.1f}" cy="{c2_y:.1f}" r="{c2_r:.1f}" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8" stroke-dasharray="4 3"/>')

    # Трикутник ABC
    frags.append(f'<polygon points="{pA2[0]},{pA2[1]} {pB2[0]},{pB2[1]} {pC2[0]},{pC2[1]}" fill="#dbeafe" stroke="#1d4ed8" stroke-width="1.6"/>')

    for pt, lab, col, off in [(pA2, "A", "#1d4ed8", (-12, 14)), (pB2, "B", "#1d4ed8", (12, 14)), (pC2, "C", "#1d4ed8", (0, -12)), (pD2_in, "D (всередині)", POS, (14, -6)), (pE2_out, "E (зовні)", "#059669", (14, 0))]:
        frags.append(circle(pt[0], pt[1], 5, fill=col, stroke="#ffffff", sw=1.8))
        frags.append(text(pt[0] + off[0], pt[1] + off[1], lab, size=11.5, color=col, bold=True))

    frags.append(text(225, 452, "Коло: (x−xc)² + (y−yc)² = R²", size=11.5, color="#1e40af", bold=True))


    # Стрілка відображення 2D -> 3D
    frags.append(arrow(425, 260, 485, 260, color="#7c3aed", sw=2.5))
    frags.append(text(455, 245, "z = x²+y²", size=12, color="#7c3aed", bold=True))
    frags.append(text(455, 280, "підняття", size=11, color=MUTED))


    # Права частина: 3D Параболоїд
    frags.append(rect(495, 75, 390, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(690, 102, "3D: Перетин параболоїда площиною H(A,B,C)", size=13.5, color="#7c3aed", bold=True))

    # Схематичний 3D-параболоїд
    frags.append('<path d="M 540 180 Q 690 420 840 180" fill="none" stroke="#cbd5e1" stroke-width="2"/>')
    frags.append('<ellipse cx="690" cy="180" rx="150" ry="30" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3 3"/>')

    # Січна площина H через підняті точки A', B', C'
    frags.append('<path d="M 570 240 L 810 210 L 780 320 L 540 350 Z" fill="#ede9fe" fill-opacity="0.7" stroke="#8b5cf6" stroke-width="1.6"/>')
    frags.append(text(575, 230, "Площина H", size=11.5, color="#7c3aed", bold=True))

    # Підняті точки
    pA3 = (610, 315)
    pB3 = (760, 275)
    pC3 = (670, 230)
    pD3_in = (680, 345)   # лежить на параболоїді НИЖЧЕ площини H
    pE3_out = (770, 205)  # лежить на параболоїді ВИЩЕ площини H

    # Трикутник A'B'C' на площині
    frags.append(f'<polygon points="{pA3[0]},{pA3[1]} {pB3[0]},{pB3[1]} {pC3[0]},{pC3[1]}" fill="#c4b5fd" fill-opacity="0.5" stroke="#6d28d9" stroke-width="1.8"/>')

    for pt, lab, col, off in [(pA3, "A'", "#6d28d9", (-12, 12)), (pB3, "B'", "#6d28d9", (12, 10)), (pC3, "C'", "#6d28d9", (0, -12)), (pD3_in, "D' (під площиною H)", POS, (14, 14)), (pE3_out, "E' (над площиною H)", "#059669", (14, -8))]:
        frags.append(circle(pt[0], pt[1], 5, fill=col, stroke="#ffffff", sw=1.8))
        frags.append(text(pt[0] + off[0], pt[1] + off[1], lab, size=11.5, color=col, bold=True))

    # Пунктир від D' до площини (показати, що точка нижче)
    frags.append(line(pD3_in[0], pD3_in[1], pD3_in[0], 285, color=POS, sw=1.4, dash="3 2"))

    frags.append(text(690, 420, "D всередині кола ⇔ D' лежить НИЖЧЕ площини H", size=11.5, color=POS, bold=True))
    frags.append(text(690, 445, "Нижні грані 3D-опуклої оболонки = тріангуляція Делоне", size=11, color=INK))

    render(os.path.join(OUT, "delaunay-paraboloid-lifting.svg"), w, h, *frags)


def fig3_bowyer_watson_cavity():
    """Фігура 3: Інкрементний алгоритм Бойєра-Ватсона — видалення трикутників та утворення зірчастої каверни."""
    w, h = 940, 490
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Алгоритм Бойєра–Ватсона: вставка точки P та утворення зірчастої каверни", size=16, color=INK, bold=True))

    pw = 275
    ph = 380

    P = (137, 240)
    v1 = (60, 160)
    v2 = (140, 140)
    v3 = (215, 175)
    v4 = (210, 310)
    v5 = (120, 330)
    v6 = (55, 270)
    c_mid = (135, 235)

    # Панель 1: Виявлення "поганих" трикутників (Bad Triangles)
    frags.append(rect(30, 75, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(30 + pw / 2, 102, "Крок 1: Точка P у колах", size=13, color="#1e40af", bold=True))

    bad_tris_1 = [
        f'<polygon points="{v1[0]},{v1[1]} {v2[0]},{v2[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
        f'<polygon points="{v2[0]},{v2[1]} {v3[0]},{v3[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
        f'<polygon points="{v3[0]},{v3[1]} {v4[0]},{v4[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
        f'<polygon points="{v4[0]},{v4[1]} {v5[0]},{v5[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
        f'<polygon points="{v5[0]},{v5[1]} {v6[0]},{v6[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
        f'<polygon points="{v6[0]},{v6[1]} {v1[0]},{v1[1]} {c_mid[0]},{c_mid[1]}" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>',
    ]
    frags.extend(bad_tris_1)

    frags.append(f'<circle cx="{c_mid[0]}" cy="{c_mid[1]}" r="82" fill="none" stroke="#dc2626" stroke-width="1.4" stroke-dasharray="4 3"/>')

    frags.append(circle(P[0], P[1], 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(P[0] + 14, P[1] - 8, "P (нова)", size=12, color=POS, bold=True))

    frags.append(text(30 + pw / 2, 390, "Знаходимо всі трикутники,", size=11.5, color=INK, bold=True))
    frags.append(text(30 + pw / 2, 410, "чиє коло містить P (InCircle > 0)", size=11, color=POS))
    frags.append(text(30 + pw / 2, 430, "Вони більше не є Делоне", size=10.5, color=MUTED))


    # Панель 2: Видалення та межа каверни
    shift2 = 305
    frags.append(rect(30 + shift2, 75, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(30 + shift2 + pw / 2, 102, "Крок 2: Порожнина (каверна)", size=13, color="#d97706", bold=True))

    P2 = (P[0] + shift2, P[1])
    poly2 = [(v[0] + shift2, v[1]) for v in [v1, v2, v3, v4, v5, v6]]

    poly_pts2 = " ".join(f"{x},{y}" for x, y in poly2)
    frags.append(f'<polygon points="{poly_pts2}" fill="#fef3c7" stroke="none"/>')

    for i in range(len(poly2)):
        p_curr = poly2[i]
        p_next = poly2[(i + 1) % len(poly2)]
        frags.append(line(p_curr[0], p_curr[1], p_next[0], p_next[1], color="#d97706", sw=2.5))

    c2 = (c_mid[0] + shift2, c_mid[1])
    for pt in poly2:
        frags.append(line(c2[0], c2[1], pt[0], pt[1], color="#cbd5e1", sw=1.2, dash="3 3"))

    frags.append(circle(P2[0], P2[1], 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(P2[0] + 14, P2[1] - 8, "P", size=12, color=POS, bold=True))

    frags.append(text(30 + shift2 + pw / 2, 390, "Видаляємо недійсні грані", size=11.5, color=INK, bold=True))
    frags.append(text(30 + shift2 + pw / 2, 410, "Зберігаємо межові ребра,", size=11, color="#d97706", bold=True))
    frags.append(text(30 + shift2 + pw / 2, 430, "що належали лише одному трикутнику", size=10.5, color=MUTED))


    # Панель 3: Повторна тріангуляція зірчастої каверни
    shift3 = 610
    frags.append(rect(30 + shift3, 75, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(30 + shift3 + pw / 2, 102, "Крок 3: Нові трикутники", size=13, color="#166534", bold=True))

    P3 = (P[0] + shift3, P[1])
    poly3 = [(v[0] + shift3, v[1]) for v in [v1, v2, v3, v4, v5, v6]]

    for i in range(len(poly3)):
        p_curr = poly3[i]
        p_next = poly3[(i + 1) % len(poly3)]
        frags.append(f'<polygon points="{P3[0]},{P3[1]} {p_curr[0]},{p_curr[1]} {p_next[0]},{p_next[1]}" fill="#dcfce7" stroke="#16a34a" stroke-width="1.6"/>')

    for i in range(len(poly3)):
        p_curr = poly3[i]
        p_next = poly3[(i + 1) % len(poly3)]
        frags.append(line(p_curr[0], p_curr[1], p_next[0], p_next[1], color=INK, sw=1.8))

    frags.append(circle(P3[0], P3[1], 6, fill="#16a34a", stroke="#ffffff", sw=2))
    frags.append(text(P3[0] + 14, P3[1] - 8, "P", size=12, color="#166534", bold=True))

    frags.append(text(30 + shift3 + pw / 2, 390, "З'єднуємо P з кожним ребром", size=11.5, color=INK, bold=True))
    frags.append(text(30 + shift3 + pw / 2, 410, "Каверна зірчаста відносно P,", size=11, color="#166534", bold=True))
    frags.append(text(30 + shift3 + pw / 2, 430, "тому нові трикутники не перетинаються", size=10.5, color=MUTED))

    render(os.path.join(OUT, "bowyer-watson-cavity.svg"), w, h, *frags)


def fig4_lawson_flip():
    """Фігура 4: Локальне перекидання ребер Лоусона (Lawson Edge Flip) та рекурсивне поширення."""
    w, h = 920, 460
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Алгоритм Лоусона: перекидання ребра (Edge Flip) та рекурсивне оновлення", size=16, color=INK, bold=True))

    pA = (220, 120)
    pB = (220, 320)
    pC = (90, 220)
    pD = (350, 220)

    # Лівий блок: до фліпу
    frags.append(rect(35, 75, 380, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(225, 102, "До фліпу: нелегальне спільне ребро e = AB", size=13, color=POS, bold=True))

    frags.append(f'<polygon points="{pA[0]},{pA[1]} {pB[0]},{pB[1]} {pC[0]},{pC[1]}" fill="#fee2e2" stroke="none"/>')
    frags.append(f'<polygon points="{pA[0]},{pA[1]} {pB[0]},{pB[1]} {pD[0]},{pD[1]}" fill="#fee2e2" stroke="none"/>')

    for (x1, y1), (x2, y2) in [(pA, pC), (pC, pB), (pB, pD), (pD, pA)]:
        frags.append(line(x1, y1, x2, y2, color=INK, sw=1.8))

    frags.append(line(pA[0], pA[1], pB[0], pB[1], color=POS, sw=2.5))
    frags.append(text(200, 220, "e (нелегальне)", size=11, color=POS, bold=True))

    for pt, lab, off in [(pA, "A", (0, -12)), (pB, "B", (0, 16)), (pC, "C", (-12, 4)), (pD, "D (нова точка)", (14, 4))]:
        frags.append(circle(pt[0], pt[1], 5.5, fill="#0284c7" if "D" not in lab else POS, stroke="#ffffff", sw=2))
        frags.append(text(pt[0] + off[0], pt[1] + off[1], lab, size=12, color=INK if "D" not in lab else POS, bold=True))

    frags.append(text(225, 365, "InCircle(A, B, C, D) > 0", size=12, color=POS, bold=True))
    frags.append(text(225, 390, "Ребро AB ділить опуклий 4-кутник ACBD", size=11, color=MUTED))


    # Стрілка перетворення
    frags.append(arrow(430, 230, 480, 230, color="#2563eb", sw=2.5))
    frags.append(text(455, 215, "FLIP", size=12, color="#2563eb", bold=True))


    # Правий блок: після фліпу
    shiftR = 465
    pAr = (pA[0] + shiftR, pA[1])
    pBr = (pB[0] + shiftR, pB[1])
    pCr = (pC[0] + shiftR, pC[1])
    pDr = (pD[0] + shiftR, pD[1])

    frags.append(rect(500, 75, 385, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(692, 102, "Після фліпу: нова діагональ e' = CD", size=13, color="#166534", bold=True))

    frags.append(f'<polygon points="{pCr[0]},{pCr[1]} {pDr[0]},{pDr[1]} {pAr[0]},{pAr[1]}" fill="#dcfce7" stroke="none"/>')
    frags.append(f'<polygon points="{pCr[0]},{pCr[1]} {pDr[0]},{pDr[1]} {pBr[0]},{pBr[1]}" fill="#dcfce7" stroke="none"/>')

    for (x1, y1), (x2, y2) in [(pAr, pCr), (pCr, pBr), (pBr, pDr), (pDr, pAr)]:
        frags.append(line(x1, y1, x2, y2, color=INK, sw=1.8))

    frags.append(line(pCr[0], pCr[1], pDr[0], pDr[1], color="#16a34a", sw=2.5))
    frags.append(text(692, 205, "e' (легальне)", size=11, color="#166534", bold=True))

    for pt, lab, off in [(pAr, "A", (0, -12)), (pBr, "B", (0, 16)), (pCr, "C", (-12, 4)), (pDr, "D", (14, 4))]:
        frags.append(circle(pt[0], pt[1], 5.5, fill="#16a34a", stroke="#ffffff", sw=2))
        frags.append(text(pt[0] + off[0], pt[1] + off[1], lab, size=12, color=INK, bold=True))

    frags.append(text(692, 365, "Рекурсивна перевірка 4 зовнішніх ребер:", size=12, color="#166534", bold=True))
    frags.append(text(692, 390, "legalize_edge(AC), legalize_edge(BC), AD, BD", size=11, color=INK))

    render(os.path.join(OUT, "delaunay-lawson-flip.svg"), w, h, *frags)


if __name__ == '__main__':
    fig1_empty_circumcircle()
    fig2_paraboloid_lifting()
    fig3_bowyer_watson_cavity()
    fig4_lawson_flip()
    print("Всі 4 фігури для тріангуляції Делоне успішно згенеровано!")
