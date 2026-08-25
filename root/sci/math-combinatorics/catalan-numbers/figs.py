# -*- coding: utf-8 -*-
"""Фігури до статті «Числа Каталана (Catalan Numbers)».
Генерує 4 SVG-діаграми:
1. dyck-paths.svg — Шляхи Дюка та принцип віддзеркалення Андре.
2. binary-trees-n3.svg — Усі 5 топологій двійкових дерев для n=3.
3. polygon-triangulation.svg — Триангуляція опуклого багатокутника (Ейлер).
4. stack-sortable.svg — Сортування перестановок через стек (Кнут, 231-заборона).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Шляхи Дюка та Принцип віддзеркалення Андре ──────────────────────
def fig_dyck_paths():
    W, H = 820, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(210, 35, "Правильний шлях Дюка (y ≤ x)", size=16, color=INK, bold=True, anchor="middle"))
    
    OX1, OY1 = 80, 380
    CELL = 75
    
    for i in range(4):
        p.append(line(OX1 + i * CELL, OY1, OX1 + i * CELL, OY1 - 3 * CELL, color="#e2e8f0", sw=1.5))
        p.append(line(OX1, OY1 - i * CELL, OX1 + 3 * CELL, OY1 - i * CELL, color="#e2e8f0", sw=1.5))
        p.append(text(OX1 + i * CELL, OY1 + 22, str(i), size=12, color=MUTED, anchor="middle"))
        p.append(text(OX1 - 18, OY1 - i * CELL + 4, str(i), size=12, color=MUTED, anchor="end"))
        
    p.append(line(OX1, OY1, OX1 + 3 * CELL, OY1 - 3 * CELL, color="#94a3b8", sw=2.0, dash="5,5"))
    p.append(text(OX1 + 3 * CELL + 8, OY1 - 3 * CELL - 4, "y = x", size=12, color=MUTED, anchor="start", italic=True))

    path_pts = [(0,0), (1,0), (2,0), (2,1), (2,2), (3,2), (3,3)]
    for k in range(len(path_pts) - 1):
        x1, y1 = OX1 + path_pts[k][0]*CELL, OY1 - path_pts[k][1]*CELL
        x2, y2 = OX1 + path_pts[k+1][0]*CELL, OY1 - path_pts[k+1][1]*CELL
        p.append(line(x1, y1, x2, y2, color="#10b981", sw=4.0))
        
    for x, y in path_pts:
        p.append(circle(OX1 + x*CELL, OY1 - y*CELL, 5, fill="#10b981", stroke="#ffffff", sw=1.5))
        
    p.append(text(210, 425, "Шлях не перетинає діагональ y = x", size=13, color=MUTED, anchor="middle", italic=True))
    p.append(text(210, 445, "Кількість валідних шляхів: C₃ = 5", size=14, color="#10b981", bold=True, anchor="middle"))

    p.append(line(420, 30, 420, 450, color="#cbd5e1", sw=1.5, dash="4,4"))

    p.append(text(620, 35, "Принцип віддзеркалення Андре", size=16, color=INK, bold=True, anchor="middle"))
    
    OX2, OY2 = 490, 380
    
    for i in range(4):
        p.append(line(OX2 + i * CELL, OY2, OX2 + i * CELL, OY2 - 3 * CELL, color="#e2e8f0", sw=1.5))
        p.append(line(OX2, OY2 - i * CELL, OX2 + 3 * CELL, OY2 - i * CELL, color="#e2e8f0", sw=1.5))
        p.append(text(OX2 + i * CELL, OY2 + 22, str(i), size=12, color=MUTED, anchor="middle"))
        p.append(text(OX2 - 18, OY2 - i * CELL + 4, str(i), size=12, color=MUTED, anchor="end"))

    p.append(line(OX2, OY2, OX2 + 3 * CELL, OY2 - 3 * CELL, color="#94a3b8", sw=1.5, dash="4,4"))
    p.append(line(OX2, OY2 - CELL, OX2 + 2 * CELL, OY2 - 3 * CELL, color="#ef4444", sw=2.0, dash="5,5"))
    p.append(text(OX2 + 2 * CELL + 8, OY2 - 3 * CELL - 4, "y = x + 1", size=12, color="#ef4444", anchor="start", italic=True))

    p.append(line(OX2, OY2, OX2, OY2 - CELL, color="#ef4444", sw=3.5))
    p.append(circle(OX2, OY2 - CELL, 6, fill="#ef4444", stroke="#ffffff", sw=1.5))
    
    refl_pts = [(0,1), (1,1), (1,2), (1,3), (2,3)]
    for k in range(len(refl_pts) - 1):
        x1, y1 = OX2 + refl_pts[k][0]*CELL, OY2 - refl_pts[k][1]*CELL
        x2, y2 = OX2 + refl_pts[k+1][0]*CELL, OY2 - refl_pts[k+1][1]*CELL
        p.append(line(x1, y1, x2, y2, color="#3b82f6", sw=3.0, dash="4,3"))
        p.append(circle(x2, y2, 4, fill="#3b82f6", stroke="#ffffff", sw=1.0))

    p.append(text(620, 425, "Погані шляхи ↔ Шляхи до (n-1, n+1)", size=13, color=MUTED, anchor="middle", italic=True))
    p.append(text(620, 445, "Cₙ = (2n \\ n) - (2n \\ n-1)", size=14, color="#3b82f6", bold=True, anchor="middle"))

    render(os.path.join(OUT, "dyck-paths.svg"), W, H, *p)


# ── Фігура 2: 5 топологій двійкових дерев для n=3 ───────────────────────────
def fig_binary_trees_n3():
    W, H = 840, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W // 2, 35, "Усі 5 структурних топологій двійкового дерева для n = 3 вузлів (C₃ = 5)", size=16, color=INK, bold=True, anchor="middle"))

    trees_data = [
        [ (0,0), (-30,40), (-55,80) ],
        [ (0,0), (-35,40), (-15,80) ],
        [ (0,0), (-35,45), (35,45) ],
        [ (0,0), (35,40), (15,80) ],
        [ (0,0), (30,40), (55,80) ]
    ]

    edges_data = [
        [ (0,1), (1,2) ],
        [ (0,1), (1,2) ],
        [ (0,1), (0,2) ],
        [ (0,1), (1,2) ],
        [ (0,1), (1,2) ]
    ]

    labels = [
        "C₀ · C₂ = 1·2",
        "C₀ · C₂ = 1·2",
        "C₁ · C₁ = 1·1",
        "C₂ · C₀ = 2·1",
        "C₂ · C₀ = 2·1"
    ]

    sub_labels = [
        "T₁: Ліва ланцюгова",
        "T₂: Зигзаг лівий",
        "T₃: Збалансована",
        "T₄: Зигзаг правий",
        "T₅: Права ланцюгова"
    ]

    centers_x = [100, 250, 420, 590, 740]
    CY = 100
    R = 14

    for idx in range(5):
        cx = centers_x[idx]
        pts = trees_data[idx]
        edg = edges_data[idx]

        for u, v in edg:
            x1, y1 = cx + pts[u][0], CY + pts[u][1]
            x2, y2 = cx + pts[v][0], CY + pts[v][1]
            p.append(line(x1, y1, x2, y2, color=LINE, sw=2.0))

        for i, (dx, dy) in enumerate(pts):
            nx, ny = cx + dx, CY + dy
            fill_color = FIELD if i == 0 else "#3b82f6"
            p.append(circle(nx, ny, R, fill=fill_color, stroke="#ffffff", sw=1.5))
            p.append(text(nx, ny + 4, str(i+1), size=11, color="#ffffff", bold=True, anchor="middle"))

        p.append(text(cx, CY + 140, sub_labels[idx], size=13, color=INK, bold=True, anchor="middle"))
        p.append(text(cx, CY + 162, labels[idx], size=12, color=MUTED, anchor="middle", italic=True))

    p.append(line(50, 290, W - 50, 290, color="#e2e8f0", sw=1.5))
    p.append(text(W // 2, 325, "Рекурентна сума: C₃ = C₀C₂ + C₁C₁ + C₂C₀ = 2 + 1 + 2 = 5", size=15, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "binary-trees-n3.svg"), W, H, *p)


# ── Фігура 3: Триангуляція опуклого багатокутника (Ейлер) ───────────────────
def fig_polygon_triangulation():
    W, H = 820, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W // 2, 35, "Розбиття опуклого багатокутника на трикутники (Задача Ейлера)", size=16, color=INK, bold=True, anchor="middle"))

    CX1, CY1, R1 = 220, 210, 110

    verts1 = []
    for i in range(6):
        angle = math.pi / 6 + i * (2 * math.pi / 6)
        vx = CX1 + R1 * math.cos(angle)
        vy = CY1 - R1 * math.sin(angle)
        verts1.append((vx, vy))

    for i in range(6):
        x1, y1 = verts1[i]
        x2, y2 = verts1[(i+1)%6]
        p.append(line(x1, y1, x2, y2, color=LINE, sw=2.5))

    diags = [(0, 2), (0, 3), (0, 4)]
    for u, v in diags:
        x1, y1 = verts1[u]
        x2, y2 = verts1[v]
        p.append(line(x1, y1, x2, y2, color="#3b82f6", sw=2.0, dash="4,3"))

    labels_v = ["v₁", "v₂", "v₃", "v₄", "v₅", "v₆"]
    for i in range(6):
        vx, vy = verts1[i]
        dx = 18 * math.cos(math.pi / 6 + i * (2 * math.pi / 6))
        dy = -18 * math.sin(math.pi / 6 + i * (2 * math.pi / 6))
        p.append(circle(vx, vy, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
        p.append(text(vx + dx, vy + dy + 4, labels_v[i], size=13, color=INK, bold=True, anchor="middle"))

    p.append(text(CX1, CY1 + 145, "Шестикутник (n=4): C₄ = 14 варіантів", size=14, color=INK, bold=True, anchor="middle"))

    p.append(line(420, 60, 420, 370, color="#cbd5e1", sw=1.5, dash="4,4"))

    CX2, CY2, R2 = 620, 210, 110
    verts2 = []
    for i in range(6):
        angle = math.pi / 6 + i * (2 * math.pi / 6)
        vx = CX2 + R2 * math.cos(angle)
        vy = CY2 - R2 * math.sin(angle)
        verts2.append((vx, vy))

    p.append(line(verts2[0][0], verts2[0][1], verts2[5][0], verts2[5][1], color="#ef4444", sw=4.0))

    tri_pts = f"{verts2[0][0]},{verts2[0][1]} {verts2[3][0]},{verts2[3][1]} {verts2[5][0]},{verts2[5][1]}"
    p.append(f'<polygon points="{tri_pts}" fill="#fee2e2" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,4"/>')

    for i in range(6):
        if i == 5: continue
        x1, y1 = verts2[i]
        x2, y2 = verts2[(i+1)%6]
        p.append(line(x1, y1, x2, y2, color=LINE, sw=2.0))

    for i in range(6):
        vx, vy = verts2[i]
        fill_c = "#ef4444" if i in (0, 3, 5) else FIELD
        p.append(circle(vx, vy, 6, fill=fill_c, stroke="#ffffff", sw=1.5))

    p.append(text(verts2[0][0] + 22, verts2[0][1] + 15, "v₁", size=13, color="#ef4444", bold=True, anchor="start"))
    p.append(text(verts2[5][0] + 22, verts2[5][1] - 5, "vₙ₊₂", size=13, color="#ef4444", bold=True, anchor="start"))
    p.append(text(verts2[3][0] - 25, verts2[3][1] + 5, "v▖", size=13, color="#ef4444", bold=True, anchor="end"))

    p.append(text(CX2 - 60, CY2 - 30, "k-кутник (Cₖ₋₂)", size=12, color=MUTED, anchor="middle", italic=True))
    p.append(text(CX2 + 60, CY2 + 50, "(n-k+3)-кутник", size=12, color=MUTED, anchor="middle", italic=True))

    p.append(text(CX2, CY2 + 145, "Розбиття на підзадачі: Cₙ = ∑ C▖ · Cₙ₋₁₋▖", size=14, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "polygon-triangulation.svg"), W, H, *p)


# ── Фігура 4: Сортування перестановок через стек (Кнут) ─────────────────────
def fig_stack_sortable():
    W, H = 820, 440
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W // 2, 35, "Сортування перестановок через стек та заборонений паттерн 231", size=16, color=INK, bold=True, anchor="middle"))

    p.append(rect(50, 120, 180, 50, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(140, 150, "Вхід: [2, 3, 1]", size=14, color=INK, bold=True, anchor="middle"))
    p.append(line(230, 145, 330, 145, color=FIELD, sw=2.5))
    p.append(text(280, 135, "PUSH 2, 3", size=11, color=FIELD, bold=True, anchor="middle"))

    p.append(line(330, 100, 330, 240, color=LINE, sw=3.0))
    p.append(line(330, 240, 430, 240, color=LINE, sw=3.0))
    p.append(line(430, 240, 430, 100, color=LINE, sw=3.0))
    p.append(text(380, 85, "LIFO Стек", size=13, color=INK, bold=True, anchor="middle"))

    p.append(rect(340, 185, 80, 45, fill="#3b82f6", stroke="#ffffff", sw=1.5, rx=4))
    p.append(text(380, 212, "2", size=16, color="#ffffff", bold=True, anchor="middle"))
    p.append(rect(340, 135, 80, 45, fill="#ef4444", stroke="#ffffff", sw=1.5, rx=4))
    p.append(text(380, 162, "3", size=16, color="#ffffff", bold=True, anchor="middle"))

    p.append(line(430, 145, 530, 145, color="#10b981", sw=2.5))
    p.append(text(480, 135, "POP", size=11, color="#10b981", bold=True, anchor="middle"))
    p.append(rect(530, 120, 240, 50, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(650, 150, "Вихід: Неможливо! (1 блоковано)", size=13, color="#ef4444", bold=True, anchor="middle"))

    p.append(rect(60, 270, 700, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(410, 300, "Теорема Дональда Кнута про стекове сортування", size=14, color=INK, bold=True, anchor="middle"))
    p.append(text(80, 330, "• Перестановка посортовна одним стеком ⇔ вона НЕ містить підпослідовності типу 2-3-1.", size=13, color=MUTED, anchor="start"))
    p.append(text(80, 355, "• Для елемента 1 попереду стоїть більший елемент 3, який передує меншому 2 у виході.", size=13, color=MUTED, anchor="start"))
    p.append(text(80, 380, "• Кількість посортовних одним стеком перестановок довжини n дорівнює точно Cₙ.", size=13, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "stack-sortable.svg"), W, H, *p)


if __name__ == "__main__":
    fig_dyck_paths()
    fig_binary_trees_n3()
    fig_polygon_triangulation()
    fig_stack_sortable()
    print("Фігури успішно згенеровано в book/algorithms/data-structures/catalan-numbers/img/")
