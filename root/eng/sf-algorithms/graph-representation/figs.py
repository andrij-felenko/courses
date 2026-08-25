# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Огляд чотирьох представлень графа ───────────────────────────────────
def fig_graph_representations_overview():
    W, H = 1040, 520
    p = []

    # Тло панелей
    pw, ph = 235.0, 440.0
    p1_x, p1_y = 20.0, 50.0
    p2_x, p2_y = 275.0, 50.0
    p3_x, p3_y = 530.0, 50.0
    p4_x, p4_y = 785.0, 50.0

    # 1. Топологія графа
    p.append(rect(p1_x, p1_y, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    p.append(text(p1_x + pw / 2, p1_y + 28, "1. Граф G = (V, E)", size=13, color=INK, bold=True))
    p.append(text(p1_x + pw / 2, p1_y + 48, "|V| = 4, |E| = 5", size=11, color=MUTED))

    nodes = {
        0: (p1_x + 65.0, p1_y + 120.0),
        1: (p1_x + 170.0, p1_y + 120.0),
        2: (p1_x + 170.0, p1_y + 260.0),
        3: (p1_x + 65.0, p1_y + 260.0),
    }
    edges = [(0, 1), (0, 2), (1, 2), (2, 0), (2, 3)]

    for u, v in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        if dist > 0:
            nx, ny = dx / dist, dy / dist
            if u == 2 and v == 0:
                sx, sy = x1 - ny * 12 + nx * 22, y1 + nx * 12 + ny * 22
                ex, ey = x2 - ny * 12 - nx * 22, y2 + nx * 12 - ny * 22
            elif u == 0 and v == 2:
                sx, sy = x1 + ny * 12 + nx * 22, y1 - nx * 12 + ny * 22
                ex, ey = x2 + ny * 12 - nx * 22, y2 - nx * 12 - ny * 22
            else:
                sx, sy = x1 + nx * 22, y1 + ny * 22
                ex, ey = x2 - nx * 22, y2 - ny * 22
            p.append(arrow(sx, sy, ex, ey, color=NEG, sw=1.8))

    for nid, (nx, ny) in nodes.items():
        p.append(circle(nx, ny, 19.0, fill="#eaf0fd", stroke=NEG, sw=2.0))
        p.append(text(nx, ny + 5, str(nid), size=14, color=INK, bold=True))

    p.append(fitbox(p1_x + 10, p1_y + ph - 110, pw - 20, 95,
                    "Вершини: {0, 1, 2, 3}\n"
                    "Орієнтовані ребра:\n"
                    "0→1, 0→2, 1→2,\n"
                    "2→0, 2→3",
                    size=11, fill="#ffffff", stroke="#cdd6e0", color=INK))

    # 2. Матриця суміжності
    p.append(rect(p2_x, p2_y, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    p.append(text(p2_x + pw / 2, p2_y + 28, "2. Матриця суміжності", size=13, color=INK, bold=True))
    p.append(text(p2_x + pw / 2, p2_y + 48, "Таблиця |V| × |V| (Θ(V²))", size=11, color=MUTED))

    mat = [
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 0, 0, 0]
    ]
    cs = 34.0
    mx0 = p2_x + 50.0
    my0 = p2_y + 110.0

    for j in range(4):
        p.append(text(mx0 + j * cs + cs / 2, my0 - 8, f"{j}", size=11.5, color=MUTED, bold=True))
    for i in range(4):
        p.append(text(mx0 - 14, my0 + i * cs + cs / 2 + 4, f"{i}", size=11.5, color=MUTED, bold=True))

    for i in range(4):
        for j in range(4):
            val = mat[i][j]
            cx = mx0 + j * cs
            cy = my0 + i * cs
            bg_c = "#eaf0fd" if val == 1 else "#ffffff"
            strk_c = NEG if val == 1 else "#dfe4ea"
            txt_c = NEG if val == 1 else "#94a3b8"
            p.append(rect(cx + 2, cy + 2, cs - 4, cs - 4, fill=bg_c, stroke=strk_c, sw=1.0, rx=3))
            p.append(text(cx + cs / 2, cy + cs / 2 + 4, str(val), size=12, color=txt_c, bold=(val == 1)))

    p.append(fitbox(p2_x + 10, p2_y + ph - 130, pw - 20, 115,
                    "Плюс: зв'язок за O(1).\n"
                    "Мінус: пам'ять Θ(V²),\n"
                    "пошук сусідів Θ(V).\n"
                    "Для розріджених\n"
                    "графів майже всі 0.",
                    size=10.5, fill="#ffffff", stroke="#cdd6e0", color=INK))

    # 3. Списки суміжності
    p.append(rect(p3_x, p3_y, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    p.append(text(p3_x + pw / 2, p3_y + 28, "3. Списки суміжності", size=13, color=INK, bold=True))
    p.append(text(p3_x + pw / 2, p3_y + 48, "Масив списків (Θ(V + E))", size=11, color=MUTED))

    adj_lists = [
        [1, 2],
        [2],
        [0, 3],
        []
    ]
    ly0 = p3_y + 80.0
    for i in range(4):
        vy = ly0 + i * 44.0
        p.append(rect(p3_x + 15, vy, 36, 32, fill="#eaf0fd", stroke=NEG, sw=1.3, rx=4))
        p.append(text(p3_x + 33, vy + 20, f"[{i}]", size=12, color=NEG, bold=True))
        p.append(arrow(p3_x + 51, vy + 16, p3_x + 72, vy + 16, color=MUTED, sw=1.3))

        items = adj_lists[i]
        if not items:
            p.append(rect(p3_x + 76, vy + 2, 45, 28, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=3))
            p.append(text(p3_x + 98, vy + 19, "null", size=11, color=MUTED, italic=True))
        else:
            for k, val in enumerate(items):
                bx = p3_x + 76 + k * 52
                p.append(rect(bx, vy + 2, 34, 28, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
                p.append(text(bx + 17, vy + 19, str(val), size=12, color=INK, bold=True))
                if k < len(items) - 1:
                    p.append(arrow(bx + 34, vy + 16, bx + 48, vy + 16, color=MUTED, sw=1.2))

    p.append(fitbox(p3_x + 10, p3_y + ph - 130, pw - 20, 115,
                    "Плюс: пам'ять O(V + E),\n"
                    "сусіди за O(deg(u)).\n"
                    "Мінус: перевірка (u, v)\n"
                    "вимагає O(deg(u)),\n"
                    "промахи кешу RAM.",
                    size=10.5, fill="#ffffff", stroke="#cdd6e0", color=INK))

    # 4. Список ребер
    p.append(rect(p4_x, p4_y, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    p.append(text(p4_x + pw / 2, p4_y + 28, "4. Список ребер", size=13, color=INK, bold=True))
    p.append(text(p4_x + pw / 2, p4_y + 48, "Масив кортежів (Θ(E))", size=11, color=MUTED))

    ey0 = p4_y + 80.0
    for idx, (u, v) in enumerate(edges):
        cy = ey0 + idx * 36.0
        p.append(rect(p4_x + 20, cy, pw - 40, 28, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(p4_x + 40, cy + 18, f"e[{idx}]:", size=11, color=MUTED))
        p.append(text(p4_x + 115, cy + 18, f"({u}  →  {v})", size=12, color=INK, bold=True))

    p.append(fitbox(p4_x + 10, p4_y + ph - 130, pw - 20, 115,
                    "Плюс: лише O(E) пам'яті,\n"
                    "зручно для сортування\n"
                    "ребер (Краскал).\n"
                    "Мінус: пошук ребра або\n"
                    "сусідів вимагає O(E).",
                    size=10.5, fill="#ffffff", stroke="#cdd6e0", color=INK))

    render(os.path.join(OUT, "graph-representations-overview.svg"), W, H, *p)


# ── Фіг. 2: Структура Compressed Sparse Row (CSR) ───────────────────────────────
def fig_csr_layout():
    W, H = 860, 440
    p = []

    # Верхній блок: Граф приклад
    p.append(rect(20, 20, W - 40, 70, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(40, 48, "Граф із 4 вершинами (|V| = 4, |E| = 5):", size=12.5, color=INK, anchor="start", bold=True))
    p.append(text(40, 68, "Сусіди 0 → {1, 2};  Сусіди 1 → {2};  Сусіди 2 → {0, 3};  Сусіди 3 → ∅",
                  size=12, color=MUTED, anchor="start"))

    # Основні масиви CSR
    bx, by = 40.0, 130.0
    p.append(text(bx, by + 18, "Масив зміщень offsets (|V| + 1 = 5 елементів):", size=13, color=INK, anchor="start", bold=True))

    offsets = [0, 2, 3, 5, 5]
    c_w = 70.0
    c_h = 38.0
    oy = by + 30.0

    for i in range(5):
        cx = bx + i * (c_w + 10)
        p.append(text(cx + c_w / 2, oy - 8, f"idx {i}", size=11, color=MUTED))
        p.append(rect(cx, oy, c_w, c_h, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
        p.append(text(cx + c_w / 2, oy + 23, str(offsets[i]), size=14, color=NEG, bold=True))

    p.append(text(bx + 5 * (c_w + 10) + 15, oy + 23, "← offsets[u+1] - offsets[u] = deg(u)", size=11.5, color=MUTED, anchor="start"))

    # 2. edges (col_indices)
    ey = oy + 90.0
    p.append(text(bx, ey - 10, "Масив ребер edges (|E| = 5 елементів):", size=13, color=INK, anchor="start", bold=True))

    edges_data = [
        (1, "з 0"),
        (2, "з 0"),
        (2, "з 1"),
        (0, "з 2"),
        (3, "з 2")
    ]
    e_w = 65.0
    e_h = 38.0

    group_colors = ["#fef3c7", "#fef3c7", "#dcfce7", "#e0e7ff", "#e0e7ff"]
    group_strokes = ["#d97706", "#d97706", "#16a34a", "#4338ca", "#4338ca"]

    for j, (dst, lbl) in enumerate(edges_data):
        cx = bx + j * (e_w + 12)
        p.append(text(cx + e_w / 2, ey + 10 - 18, f"pos {j}", size=11, color=MUTED))
        p.append(rect(cx, ey + 10, e_w, e_h, fill=group_colors[j], stroke=group_strokes[j], sw=1.5, rx=5))
        p.append(text(cx + e_w / 2, ey + 33, str(dst), size=14, color=INK, bold=True))
        p.append(text(cx + e_w / 2, ey + 60, f"({lbl})", size=10.5, color=MUTED))

    # Стрілки діапазонів
    p.append(line(bx + c_w / 2, oy + c_h, bx + 15, ey + 5, color=NEG, sw=1.4, dash="3,3"))
    p.append(line(bx + (c_w + 10) + c_w / 2, oy + c_h, bx + 2 * (e_w + 12) - 5, ey + 5, color=NEG, sw=1.4, dash="3,3"))

    p.append(fitbox(20, H - 90, W - 40, 70,
                    "Діапазон сусідів вершини u зберігається неперервно у зрізі edges[offsets[u] .. offsets[u+1]].\n"
                    "Пам'ять: рівно два пласкі масиви (4·(V+1) + 4·E байтів). Жодного вказівника, 100% кеш-локальність.",
                    size=11.5, fill="#f0fdf4", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "csr-layout.svg"), W, H, *p)


# ── Фіг. 3: Порівняння витрат пам'яті залежно від густини графа ──────────────────
def fig_density_space_tradeoff():
    W, H = 840, 460
    p = []

    gx0, gy0 = 80.0, 360.0
    gw, gh = 460.0, 280.0

    p.append(rect(20, 20, W - 40, H - 40, fill="#ffffff", stroke="#dfe4ea", sw=1.2, rx=8))
    p.append(text(W / 2, 45, "Витрати оперативної пам'яті залежно від кількості ребер |E| (для |V| = 10 000)", size=14, color=INK, bold=True))

    # Осі
    p.append(line(gx0, gy0, gx0 + gw + 20, gy0, color=LINE, sw=1.8))
    p.append(line(gx0, gy0, gx0, gy0 - gh - 20, color=LINE, sw=1.8))

    p.append(text(gx0 + gw + 25, gy0 + 4, "|E| (густина)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(gx0 - 10, gy0 - gh - 25, "Пам'ять (RAM)", size=12, color=INK, anchor="end", bold=True))

    p.append(text(gx0, gy0 + 18, "0", size=11, color=MUTED))
    p.append(text(gx0 + gw * 0.25, gy0 + 18, "25M (25%)", size=11, color=MUTED))
    p.append(text(gx0 + gw * 0.50, gy0 + 18, "50M (50%)", size=11, color=MUTED))
    p.append(text(gx0 + gw * 0.75, gy0 + 18, "75M (75%)", size=11, color=MUTED))
    p.append(text(gx0 + gw, gy0 + 18, "100M (|V|²)", size=11, color=MUTED))

    # Лінія матриці
    mat_y = gy0 - gh * 0.38
    p.append(line(gx0, mat_y, gx0 + gw, mat_y, color=NEG, sw=2.5))
    p.append(text(gx0 + gw - 80, mat_y - 10, "Матриця суміжності: Θ(V²)", size=12, color=NEG, bold=True))

    # Лінія списків суміжності
    p.append(line(gx0, gy0 - 15, gx0 + gw * 0.65, gy0 - gh, color=POS, sw=2.5))
    p.append(text(gx0 + gw * 0.45, gy0 - gh + 30, "Списки суміжності (vector): Θ(V + E)", size=12, color=POS, bold=True))

    # Лінія CSR
    p.append(line(gx0, gy0 - 8, gx0 + gw, gy0 - gh * 0.85, color=FIELD, sw=2.5, dash="4,2"))
    p.append(text(gx0 + gw - 30, gy0 - gh * 0.85 - 10, "CSR: 4V + 4E", size=12, color=FIELD, bold=True))

    # Точка перетину
    cross_x = gx0 + gw * 0.16
    p.append(circle(cross_x, mat_y, 5.0, fill=POS, stroke="#ffffff", sw=2.0))
    p.append(line(cross_x, gy0, cross_x, mat_y, color=MUTED, sw=1.0, dash="3,3"))
    p.append(text(cross_x, gy0 + 34, "Точка перетину (~2-5%)", size=11, color=POS, bold=True))

    # Права панель
    info_x = gx0 + gw + 40
    p.append(rect(info_x, 80, W - info_x - 30, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(info_x + 15, 105, "Висновки для вибору:", size=12.5, color=INK, anchor="start", bold=True))

    p.append(mtext(info_x + 15, 130,
                   "• Розріджені графи (d < 5%):\n"
                   "  Реальні мережі (дороги, web,\n"
                   "  соцмережі) мають d ≪ 1%.\n"
                   "  Списки суміжності або CSR\n"
                   "  економлять гігабайти RAM.\n\n"
                   "• Щільні графи (d > 15%):\n"
                   "  Матриця виграє за рахунок\n"
                   "  O(1) перевірки зв'язку та\n"
                   "  відсутності оверхеду вказівників.\n\n"
                   "• CSR (Packed Array):\n"
                   "  У 3-5 разів компактніший за\n"
                   "  std::vector<std::vector>.",
                   size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(OUT, "density-space-tradeoff.svg"), W, H, *p)


# ── Фіг. 4: Патерни доступу до пам'яті та кеш процесора ──────────────────────────
def fig_cache_traversal_patterns():
    W, H = 920, 480
    p = []

    p.append(rect(20, 20, W - 40, H - 40, fill="#ffffff", stroke="#dfe4ea", sw=1.2, rx=8))
    p.append(text(W / 2, 45, "Прохід сусідів вершини u: поведінка кеш-пам'яті L1/L2 CPU", size=14, color=INK, bold=True))

    col_w = 270.0
    p1_x = 35.0
    p2_x = 325.0
    p3_x = 615.0
    card_h = 370.0
    card_y = 70.0

    # 1. Linked List
    p.append(rect(p1_x, card_y, col_w, card_h, fill="#fff5f5", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(p1_x + col_w / 2, card_y + 24, "Зв'язані списки вузлів", size=12.5, color=POS, bold=True))
    p.append(text(p1_x + col_w / 2, card_y + 42, "Pointer Chasing", size=11, color=MUTED))

    p.append(rect(p1_x + 15, card_y + 60, col_w - 30, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(p1_x + 25, card_y + 78, "Купа (Heap RAM):", size=10.5, color=MUTED, anchor="start"))

    p.append(rect(p1_x + 25, card_y + 90, 50, 24, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
    p.append(text(p1_x + 50, card_y + 106, "Node A", size=10, color=POS))

    p.append(rect(p1_x + 160, card_y + 130, 50, 24, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
    p.append(text(p1_x + 185, card_y + 146, "Node B", size=10, color=POS))

    p.append(arrow(p1_x + 75, card_y + 102, p1_x + 160, card_y + 138, color=POS, sw=1.3))

    p.append(fitbox(p1_x + 12, card_y + 185, col_w - 24, 160,
                    "Вузли виділені у випадкових\n"
                    "адресах динамічної купи.\n"
                    "Кожен перехід за вказівником\n"
                    "next спричиняє промах кешу.\n"
                    "Процесор простоює сотні\n"
                    "тактів під час читання RAM.",
                    size=10.5, fill="#ffffff", stroke="#fca5a5", color=INK))

    # 2. Матриця суміжності
    p.append(rect(p2_x, card_y, col_w, card_h, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(p2_x + col_w / 2, card_y + 24, "Матриця (Рядок u)", size=12.5, color=NEG, bold=True))
    p.append(text(p2_x + col_w / 2, card_y + 42, "Strided Scan", size=11, color=MUTED))

    p.append(rect(p2_x + 15, card_y + 60, col_w - 30, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(p2_x + 25, card_y + 78, "Рядок A[u] (64 байти лінія кешу):", size=10.5, color=MUTED, anchor="start"))

    cells = [0, 0, 1, 0, 0, 0, 1, 0]
    for ci, cv in enumerate(cells):
        cx = p2_x + 22 + ci * 28
        bg_c = "#dbeafe" if cv == 1 else "#f8fafc"
        p.append(rect(cx, card_y + 95, 25, 23, fill=bg_c, stroke="#94a3b8", sw=0.8, rx=2))
        p.append(text(cx + 12.5, card_y + 111, str(cv), size=10, color=NEG if cv == 1 else MUTED))

    p.append(text(p2_x + col_w / 2, card_y + 145, "99% нулів = зайві зчитування", size=10.5, color=MUTED))

    p.append(fitbox(p2_x + 12, card_y + 185, col_w - 24, 160,
                    "Пам'ять читається послідовно\n"
                    "(добре для Prefetcher).\n"
                    "Але у розрідженому графі\n"
                    "99.9% комірок — нулі.\n"
                    "Кеш забивається непотрібними\n"
                    "даними (Cache Pollution).",
                    size=10.5, fill="#ffffff", stroke="#93c5fd", color=INK))

    # 3. CSR / Flat Array
    p.append(rect(p3_x, card_y, col_w, card_h, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(p3_x + col_w / 2, card_y + 24, "CSR / Неперервний вектор", size=12.5, color=FIELD, bold=True))
    p.append(text(p3_x + col_w / 2, card_y + 42, "Contiguous Stream", size=11, color=MUTED))

    p.append(rect(p3_x + 15, card_y + 60, col_w - 30, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(p3_x + 25, card_y + 78, "Щільний зріз edges[u]:", size=10.5, color=MUTED, anchor="start"))

    dense_nbrs = [2, 5, 8, 14, 21, 33]
    for di, dv in enumerate(dense_nbrs):
        cx = p3_x + 25 + di * 36
        p.append(rect(cx, card_y + 95, 32, 23, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=2))
        p.append(text(cx + 16, card_y + 111, str(dv), size=10.5, color=FIELD, bold=True))

    p.append(text(p3_x + col_w / 2, card_y + 145, "100% корисних даних у кеші", size=10.5, color=FIELD, bold=True))

    p.append(fitbox(p3_x + 12, card_y + 185, col_w - 24, 160,
                    "Усі сусіди лежать впритул\n"
                    "один до одного в масиві.\n"
                    "64-байтна лінія L1 кешу читає\n"
                    "одразу 16 сусідів (uint32_t).\n"
                    "Максимальна пропускна\n"
                    "здатність SIMD та Prefetcher.",
                    size=10.5, fill="#ffffff", stroke="#86efac", color=INK))

    render(os.path.join(OUT, "cache-traversal-patterns.svg"), W, H, *p)


if __name__ == "__main__":
    fig_graph_representations_overview()
    fig_csr_layout()
    fig_density_space_tradeoff()
    fig_cache_traversal_patterns()
    print("All figures generated successfully.")
