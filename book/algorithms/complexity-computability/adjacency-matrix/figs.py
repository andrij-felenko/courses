# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Граф та відповідна йому матриця суміжності ─────────────────────────
# Наочне зіставлення: орієнтований/неорієнтований граф із 4 вершинами
# та 4x4 матриця суміжності A[i][j], де підсвічено рядок i (виходи) й стовпчик j (входи).
def fig_matrix_graph_correspondence():
    W, H = 920, 480
    p = []

    # Ліва панель: граф
    px1, py1, pw1, ph1 = 30.0, 50.0, 380.0, 390.0
    p.append(rect(px1, py1, pw1, ph1, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(px1 + pw1 / 2, py1 + 30, "Орієнтований граф G = (V, E)", size=14, color=INK, bold=True))

    # Координати вершин графа (4 вершини: 0, 1, 2, 3)
    nodes = {
        0: (px1 + 100.0, py1 + 120.0),
        1: (px1 + 280.0, py1 + 120.0),
        2: (px1 + 280.0, py1 + 290.0),
        3: (px1 + 100.0, py1 + 290.0),
    }

    # Ребра: (0->1), (0->3), (1->2), (2->0), (2->3)
    edges = [(0, 1), (0, 3), (1, 2), (2, 0), (2, 3)]

    for u, v in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        if dist > 0:
            nx, ny = dx / dist, dy / dist
            sx, sy = x1 + nx * 24, y1 + ny * 24
            ex, ey = x2 - nx * 24, y2 - ny * 24
            p.append(arrow(sx, sy, ex, ey, color=NEG, sw=2.0))

    # Намалюємо вузли
    for node_id, (nx, ny) in nodes.items():
        p.append(circle(nx, ny, 22.0, fill="#eaf0fd", stroke=NEG, sw=2.0))
        p.append(text(nx, ny + 5, str(node_id), size=15, color=INK, bold=True))

    p.append(fitbox(px1 + 20, py1 + ph1 - 45, pw1 - 40, 30,
                    "Вузол 0 має виходи в 1 та 3  ⟹  Рядок 0 має одиниці в col 1 та col 3",
                    size=11.5, fill="#eef7f0", stroke=FIELD, color=INK))

    # Права панель: Матриця A [4x4]
    px2, py2, pw2, ph2 = 440.0, 50.0, 450.0, 390.0
    p.append(rect(px2, py2, pw2, ph2, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(px2 + pw2 / 2, py2 + 30, "Матриця суміжності A (4 × 4)", size=14, color=INK, bold=True))

    matrix_val = [
        [0, 1, 0, 1],  # 0
        [0, 0, 1, 0],  # 1
        [1, 0, 0, 1],  # 2
        [0, 0, 0, 0]   # 3
    ]

    cell_size = 50.0
    grid_x0 = px2 + 120.0
    grid_y0 = py2 + 100.0

    # Заголовки стовпчиків (входи, col j)
    p.append(text(grid_x0 + 2 * cell_size, grid_y0 - 32, "Стовпчики j (вхідні)", size=12, color=MUTED, bold=True))
    for j in range(4):
        p.append(text(grid_x0 + j * cell_size + cell_size / 2, grid_y0 - 10, f"j={j}", size=12.5, color=INK, bold=True))

    # Заголовки рядків (виходи, row i)
    p.append(text(grid_x0 - 75, grid_y0 + 2 * cell_size, "Рядки i\n(виходи)", size=12, color=MUTED, bold=True))
    for i in range(4):
        p.append(text(grid_x0 - 20, grid_y0 + i * cell_size + cell_size / 2 + 4, f"i={i}", size=12.5, color=INK, bold=True))

    # Підсвічення рядка i=0 (виходи з 0)
    p.append(rect(grid_x0 - 5, grid_y0 + 0 * cell_size + 2, 4 * cell_size + 10, cell_size - 4,
                  fill="#fdecea", stroke=POS, sw=1.5, rx=4))

    for i in range(4):
        for j in range(4):
            cx = grid_x0 + j * cell_size
            cy = grid_y0 + i * cell_size
            val = matrix_val[i][j]
            bg_col = "#ffffff"
            strk_col = "#cdd6e0"
            txt_col = INK
            is_bold = False

            if val == 1:
                bg_col = "#eaf0fd"
                strk_col = NEG
                txt_col = NEG
                is_bold = True

            p.append(rect(cx + 3, cy + 3, cell_size - 6, cell_size - 6, fill=bg_col, stroke=strk_col, sw=1.2, rx=4))
            p.append(text(cx + cell_size / 2, cy + cell_size / 2 + 5, str(val), size=15, color=txt_col, bold=is_bold))

    p.append(fitbox(px2 + 20, py2 + ph2 - 45, pw2 - 40, 30,
                    "A[i][j] = 1 означає наявність ребра i → j; перевірка O(1) за індексами",
                    size=11.5, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "matrix-graph-correspondence.svg"), W, H, *p,
           title="Зіставлення графа та матриці суміжності")


# ── Фіг. 2: Розташування у пам'яті: Плоский масив проти масиву вказівників ───
def fig_memory_layout_flat_vs_nested():
    W, H = 920, 480
    p = []

    # Верхня панель: Неперервний плоский масив (Flat 1D)
    px1, py1, pw1, ph1 = 30.0, 40.0, 860.0, 190.0
    p.append(rect(px1, py1, pw1, ph1, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(px1 + 30, py1 + 26, "1. Неперервний буфер у пам'яті (Flat 1D Array): A[i * N + j]", size=13.5, color=FIELD, bold=True, anchor="start"))

    bx0 = px1 + 40.0
    by0 = py1 + 55.0
    cell_w, cell_h = 46.0, 40.0

    # Клітинки пам'яті для N=4 (16 елементів підряд)
    for idx in range(16):
        i = idx // 4
        j = idx % 4
        cx = bx0 + idx * cell_w
        cy = by0
        fill_c = "#eef7f0" if i % 2 == 0 else "#eaf0fd"
        p.append(rect(cx, cy, cell_w - 2, cell_h, fill=fill_c, stroke="#aab4c0", sw=1.1, rx=3))
        p.append(text(cx + cell_w / 2 - 1, cy + cell_h / 2 + 4, f"[{i}][{j}]", size=10, color=INK))

    # CPU Cache line bracket
    p.append(line(bx0, by0 + cell_h + 10, bx0 + 8 * cell_w - 2, by0 + cell_h + 10, color=FIELD, sw=2.0))
    p.append(text(bx0 + 4 * cell_w, by0 + cell_h + 26, "Одна лінія кешу CPU (64 байти) завантажує одразу кілька рядків", size=11, color=FIELD, bold=True))

    p.append(fitbox(px1 + 30, py1 + ph1 - 35, pw1 - 60, 26,
                    "Плюси: 1 виділення пам'яті, ідеальний prefetching при послідовному обході, 0 pointer-chasing",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK))

    # Нижня панель: Вкладені масиви вказівників (Pointer Array / Vector of Vectors)
    px2, py2, pw2, ph2 = 30.0, 250.0, 860.0, 200.0
    p.append(rect(px2, py2, pw2, ph2, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(px2 + 30, py2 + 26, "2. Масив вказівників (Array of Pointers / std::vector<std::vector<T>>)", size=13.5, color=POS, bold=True, anchor="start"))

    # Масив вказівників (вертикальний або горизонтальний)
    ptr_x = px2 + 40.0
    ptr_y = py2 + 55.0
    for r in range(4):
        cy = ptr_y + r * 26.0
        p.append(rect(ptr_x, cy, 70.0, 22.0, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        p.append(text(ptr_x + 35, cy + 15, f"ptr[{r}]", size=10.5, color=POS, bold=True))

        # Стрілка до розкиданого блоку в купі
        target_x = ptr_x + 140.0 + (r * 35.0)
        target_y = cy
        p.append(arrow(ptr_x + 72.0, cy + 11.0, target_x - 5.0, target_y + 11.0, color=POS, sw=1.4))

        # Блок рядка r
        for c in range(4):
            cx = target_x + c * 36.0
            p.append(rect(cx, target_y, 34.0, 22.0, fill="#fff6e6", stroke="#e08a1e", sw=1.0, rx=2))
            p.append(text(cx + 17, target_y + 15, f"r{r}c{c}", size=9.5, color=INK))

    p.append(fitbox(px2 + 30, py2 + ph2 - 35, pw2 - 60, 26,
                    "Мінуси: N+1 виділень у купі, фрагментація пам'яті, Cache Miss при переході між рядками",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(OUT, "memory-layout-flat-vs-nested.svg"), W, H, *p,
           title="Порівняння схем розташування матриці суміжності у пам'яті")


# ── Фіг. 3: Множення матриць та кількість шляхів A^k ─────────────────────────
def fig_matrix_power_walks():
    W, H = 900, 460
    p = []

    # Формула піднесення до степеня
    p.append(fitbox(40, 20, W - 80, 45,
                    "Алгебраїчна властивість: (Aᵏ)[i][j] = кількість шляхів довжини k від вершини i до j",
                    size=13.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    # Схема A^1, A^2, A^3 для граф-трикутника
    m_data = [
        ("Матриця A (k=1)\nШляхи довжини 1", [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ], "#eaf0fd", NEG),
        ("Матриця A² (k=2)\nШляхи довжини 2", [
            [2, 1, 1],
            [1, 2, 1],
            [1, 1, 2]
        ], "#fdf0dc", "#e08a1e"),
        ("Матриця A³ (k=3)\nШляхи довжини 3", [
            [2, 3, 3],
            [3, 2, 3],
            [3, 3, 2]
        ], "#eef7f0", FIELD)
    ]

    mw, mh = 250.0, 260.0
    for idx, (title_str, mat, bg_c, border_c) in enumerate(m_data):
        mx = 40.0 + idx * 285.0
        my = 85.0
        p.append(rect(mx, my, mw, mh, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))

        # Заголовок
        lines = title_str.split("\n")
        p.append(text(mx + mw / 2, my + 25, lines[0], size=13, color=border_c, bold=True))
        p.append(text(mx + mw / 2, my + 42, lines[1], size=11, color=MUTED))

        # Сітка 3х3
        cs = 44.0
        gx0 = mx + (mw - 3 * cs) / 2
        gy0 = my + 70.0

        for r in range(3):
            for c in range(3):
                cx = gx0 + c * cs
                cy = gy0 + r * cs
                v = mat[r][c]
                is_diag = (r == c)
                cell_bg = bg_c if is_diag else "#ffffff"
                p.append(rect(cx + 2, cy + 2, cs - 4, cs - 4, fill=cell_bg, stroke=border_c, sw=1.1, rx=4))
                p.append(text(cx + cs / 2, cy + cs / 2 + 5, str(v), size=14, color=INK, bold=True))

        p.append(text(mx + mw / 2, gy0 + 3 * cs + 25,
                      f"Tr(A³) / 6 = ({mat[0][0]}+{mat[1][1]}+{mat[2][2]}) / 6 = 1 трикутник" if idx == 2
                      else f"Діагональ: {mat[0][0]} замкнених ротацій",
                      size=10.5, color=border_c, bold=True))

    p.append(fitbox(40, 370, W - 80, 65,
                    "Для k=3 діагональні елементи (A³)ᵢᵢ вказують на кількість замкнених циклів довжини 3.\nСлід Tr(A³) = ∑ (A³)ᵢᵢ дає рівно 6 × (кількість трикутників у графі).",
                    size=12, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "matrix-power-walks.svg"), W, H, *p,
           title="Піднесення матриці суміжності до степеня та обчислення кількості шляхів")


# ── Фіг. 4: Порівняльне витрачання пам'яті: Матриця vs Список суміжності ────
def fig_density_tradeoff():
    W, H = 880, 480
    p = []

    px, py, pw, ph = 50.0, 40.0, 780.0, 360.0
    p.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))

    # Вісі координат
    ax0 = px + 80.0
    ay0 = py + ph - 60.0
    gw = pw - 120.0
    gh = ph - 100.0

    p.append(line(ax0, ay0, ax0 + gw, ay0, color=INK, sw=1.5))  # X: Щільність ребер
    p.append(line(ax0, ay0, ax0, ay0 - gh, color=INK, sw=1.5))  # Y: Пам'ять (байти)

    p.append(text(ax0 + gw / 2, ay0 + 36, "Щільність графа ρ = M / N²  (0 = розріджений, 1 = повний) →", size=12.5, color=INK, bold=True))
    p.append(text(ax0 - 45, ay0 - gh / 2, "Пам'ять\n(байти)", size=12, color=INK, bold=True, anchor="end"))

    # Лінія Матриці суміжності (Flat bool): Стала O(N²) незалежно від кількості ребер M
    y_mat = ay0 - gh * 0.45
    p.append(line(ax0, y_mat, ax0 + gw, y_mat, color=NEG, sw=2.5))
    p.append(text(ax0 + gw + 10, y_mat + 4, "Матриця O(N²)", size=12, color=NEG, bold=True, anchor="start"))

    # Лінія Списку суміжності: O(N + M) — зростає від низьких значень до високих
    y_list_start = ay0 - gh * 0.12
    y_list_end = ay0 - gh * 0.85
    p.append(line(ax0, y_list_start, ax0 + gw, y_list_end, color=POS, sw=2.5))
    p.append(text(ax0 + gw + 10, y_list_end + 4, "Список O(N + M)", size=12, color=POS, bold=True, anchor="start"))

    # Точка перетину (поріг вигідності)
    t_ratio = (y_mat - y_list_start) / (y_list_end - y_list_start)
    cx_cross = ax0 + gw * t_ratio
    cy_cross = y_mat

    p.append(circle(cx_cross, cy_cross, 6.0, fill="#ffffff", stroke="#e08a1e", sw=2.5))
    p.append(line(cx_cross, cy_cross, cx_cross, ay0, color="#e08a1e", sw=1.3, dash="4 4"))
    p.append(text(cx_cross, ay0 + 18, "ρ ≈ 12-15%", size=11, color="#e08a1e", bold=True))

    p.append(fitbox(px + 40, py + ph + 12, pw - 80, 45,
                    "Для розріджених графів (ρ < 10%) список суміжності значно економніший за пам'яттю.\nДля щільних графів (ρ > 20%) матриця суміжності виграє за рахунок відсутності оверхеду вказівників.",
                    size=12, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "density-tradeoff.svg"), W, H, *p,
           title="Залежність витрат пам'яті від щільності графа")


if __name__ == "__main__":
    fig_matrix_graph_correspondence()
    fig_memory_layout_flat_vs_nested()
    fig_matrix_power_walks()
    fig_density_tradeoff()
    print("OK figs for adjacency-matrix")
