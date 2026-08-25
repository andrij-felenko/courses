# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C_TREE = "#1e824c"       # Зелений: ребра кістяка (MST)
C_REJECT = "#c0392b"     # Червоний: відхилені ребра (цикли)
C_EXAMINE = "#2457d6"    # Синій: ребро на розгляді
C_UNVISITED = "#95a5a6"  # Сірий: нерозглянуті ребра
C_NODE_FILL = "#ffffff"
C_NODE_STROKE = "#2c3e50"
C_PANEL_BG = "#f8fafc"
C_ACCENT_BG = "#edf7ed"

# ── Фігура 1: Покрокова побудова кістяка алгоритмом Краскала ──────────────────
def fig_kruskal_step_by_step():
    W, H = 980, 580
    parts = []

    # Тло
    parts.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    parts.append(text(W / 2, 28, "Покрокова робота алгоритму Краскала на графі з 6 вершин", size=16, bold=True))

    # Координати 4 підпанелей (2x2)
    panels = [
        {"x": 15, "y": 45, "w": 465, "h": 250, "step": "Крок 1: Сортування ребер і старт", "sub": "Всі 6 вершин у власних компонентах; список 9 ребер відсортовано."},
        {"x": 500, "y": 45, "w": 465, "h": 250, "step": "Крок 2: Додавання безпечних ребер", "sub": "Додано (A,B:1), (D,E:2), (B,C:3), (A,D:4). Лишилось 2 компоненти."},
        {"x": 15, "y": 310, "w": 465, "h": 250, "step": "Крок 3: Виявлення та відхилення циклів", "sub": "Ребра (B,E:5) та (C,E:6) утворюють цикли в {A,B,C,D,E} — ВІДХИЛЕНО."},
        {"x": 500, "y": 310, "w": 465, "h": 250, "step": "Крок 4: Завершення кістякового дерева", "sub": "Ребро (C,F:7) об'єднує компоненти. MST містить 5 ребер, вага = 17."},
    ]

    # Базові позиції вершин всередині кожної підпанелі
    # A, B, C (верхній ряд), D, E, F (нижній ряд)
    node_rel = {
        "A": (60, 85),
        "B": (155, 65),
        "C": (250, 85),
        "D": (60, 185),
        "E": (155, 205),
        "F": (250, 185),
    }

    # Ребра: (u, v, weight, label_dx, label_dy)
    edges = [
        ("A", "B", 1, 0, -12),
        ("D", "E", 2, 0, 14),
        ("B", "C", 3, 0, -12),
        ("A", "D", 4, -14, 0),
        ("B", "E", 5, 12, 0),
        ("C", "E", 6, -10, 8),
        ("C", "F", 7, 14, 0),
        ("E", "F", 8, 0, 14),
        ("A", "C", 9, 0, -22),
    ]

    for idx, pnl in enumerate(panels):
        px, py, pw, ph = pnl["x"], pnl["y"], pnl["w"], pnl["h"]
        # Рамка панелі
        parts.append(rect(px, py, pw, ph, fill=C_PANEL_BG, stroke="#cbd5e1", sw=1.2, rx=8))
        parts.append(text(px + 14, py + 22, pnl["step"], size=13, bold=True, anchor="start", color="#1e293b"))
        parts.append(text(px + 14, py + 38, pnl["sub"], size=10.5, color="#64748b", anchor="start"))

        # Визначаємо статус кожного ребра для даного кроку
        # 'tree', 'reject', 'examine', 'unvisited'
        edge_status = {}
        for u, v, w, _, _ in edges:
            key = (u, v)
            if idx == 0:
                edge_status[key] = "unvisited"
            elif idx == 1:
                if w in [1, 2, 3, 4]:
                    edge_status[key] = "tree"
                else:
                    edge_status[key] = "unvisited"
            elif idx == 2:
                if w in [1, 2, 3, 4]:
                    edge_status[key] = "tree"
                elif w in [5, 6]:
                    edge_status[key] = "reject"
                else:
                    edge_status[key] = "unvisited"
            elif idx == 3:
                if w in [1, 2, 3, 4, 7]:
                    edge_status[key] = "tree"
                elif w in [5, 6]:
                    edge_status[key] = "reject"
                else:
                    edge_status[key] = "unvisited"

        # Малювання ребер
        for u, v, w, ldx, ldy in edges:
            x1, y1 = px + node_rel[u][0], py + node_rel[u][1]
            x2, y2 = px + node_rel[v][0], py + node_rel[v][1]
            st = edge_status.get((u, v), "unvisited")

            if (u, v) == ("A", "C"):
                # Дугове ребро зверху, щоб не перетинати B
                mx, my = (x1 + x2) / 2, min(y1, y2) - 30
                d = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x1, y1, mx, my, x2, y2)
                col = C_TREE if st == "tree" else (C_REJECT if st == "reject" else "#cbd5e1")
                sw = 2.8 if st == "tree" else (2.0 if st == "reject" else 1.2)
                dash = "4 3" if st == "reject" else None
                d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
                parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, d_attr))
                parts.append(text(mx, my - 4, str(w), size=11, bold=True, color="#64748b"))
            else:
                col = C_TREE if st == "tree" else (C_REJECT if st == "reject" else "#cbd5e1")
                sw = 2.8 if st == "tree" else (2.0 if st == "reject" else 1.2)
                dash = "4 3" if st == "reject" else None
                parts.append(line(x1, y1, x2, y2, color=col, sw=sw, dash=dash))
                mx, my = (x1 + x2) / 2 + ldx, (y1 + y2) / 2 + ldy
                parts.append(text(mx, my + 3, str(w), size=11, bold=True, color=(C_TREE if st == "tree" else (C_REJECT if st == "reject" else "#64748b"))))

        # Малювання вершин
        for name, (rx_pos, ry_pos) in node_rel.items():
            cx, cy = px + rx_pos, py + ry_pos
            parts.append(circle(cx, cy, 14, fill=C_NODE_FILL, stroke=C_NODE_STROKE, sw=1.8))
            parts.append(text(cx, cy + 4.5, name, size=12, bold=True, color="#0f172a"))

        # Інформаційний блок праворуч усередині панелі
        ix, iy = px + 295, py + 65
        parts.append(rect(ix, iy, 155, 170, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=6))
        parts.append(text(ix + 77, iy + 18, "Стан DSU / Стек", size=11, bold=True, color="#334155"))

        if idx == 0:
            lines = ["{A}, {B}, {C},", "{D}, {E}, {F}", "Компонент: 6", "Ребер у MST: 0/5", "Черга:", "1,2,3,4,5,6,7,8,9"]
        elif idx == 1:
            lines = ["Об'єднано:", "{A, B, C, D, E},", "{F}", "Компонент: 2", "Ребер у MST: 4/5", "Вага: 1+2+3+4 = 10"]
        elif idx == 2:
            lines = ["Перевірка:", "(B,E:5) -> Цикл!", "(C,E:6) -> Цикл!", "find(B)==find(E)", "Компонент: 2", "Ребер у MST: 4/5"]
        elif idx == 3:
            lines = ["Додано (C,F:7)", "MST побудовано!", "Всі вузли зв'язані", "Компонент: 1", "Ребер у MST: 5/5", "Загальна вага: 17"]

        for l_idx, ln in enumerate(lines):
            parts.append(text(ix + 10, iy + 40 + l_idx * 21, ln, size=10.5, color="#1e293b", anchor="start"))

    render(os.path.join(OUT, "kruskal-step-by-step.svg"), W, H, *parts)


# ── Фігура 2: Властивості розрізу та циклу ─────────────────────────────────────
def fig_cut_and_cycle_rule():
    W, H = 940, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    parts.append(text(W / 2, 28, "Фундаментальні властивості розрізу та циклу в мінімальних кістяках", size=16, bold=True))

    # Ліва панель: Властивість розрізу (Cut Property)
    lx, ly, lw, lh = 20, 50, 435, 345
    parts.append(rect(lx, ly, lw, lh, fill=C_PANEL_BG, stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(lx + lw / 2, ly + 24, "Властивість розрізу (Cut Property)", size=13.5, bold=True, color="#0f172a"))
    parts.append(text(lx + lw / 2, ly + 42, "Найлегше ребро перетину розрізу (S, V \\ S) безпечне для MST", size=10.5, color="#64748b"))

    # Множина S (лівий еліпс)
    parts.append('<ellipse cx="%d" cy="%d" rx="75" ry="110" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4 3"/>' % (lx + 100, ly + 180))
    parts.append(text(lx + 60, ly + 100, "Підмножина S", size=11, bold=True, color="#1d4ed8"))

    # Множина V \ S (правий еліпс)
    parts.append('<ellipse cx="%d" cy="%d" rx="75" ry="110" fill="#f0fdf4" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4 3"/>' % (lx + 335, ly + 180))
    parts.append(text(lx + 355, ly + 100, "V \\ S", size=11, bold=True, color="#15803d"))

    # Вузли в S: s1, s2, s3
    s_nodes = {"s1": (lx + 90, ly + 130), "s2": (lx + 110, ly + 185), "s3": (lx + 85, ly + 245)}
    # Вузли в V \ S: t1, t2, t3
    t_nodes = {"t1": (lx + 320, ly + 130), "t2": (lx + 345, ly + 185), "t3": (lx + 325, ly + 245)}

    # Ребра перетину розрізу
    # s1 - t1 (вага 9)
    parts.append(line(s_nodes["s1"][0], s_nodes["s1"][1], t_nodes["t1"][0], t_nodes["t1"][1], color="#94a3b8", sw=1.5))
    parts.append(text(lx + 205, ly + 120, "вага 9", size=10.5, color="#64748b"))

    # s2 - t2 (вага 3) -> МІНІМАЛЬНЕ БЕЗПЕЧНЕ РЕБРО (Cut-Edge)
    parts.append(line(s_nodes["s2"][0], s_nodes["s2"][1], t_nodes["t2"][0], t_nodes["t2"][1], color=C_TREE, sw=3.2))
    parts.append(text(lx + 205, ly + 175, "вага 3 (e*)", size=12, bold=True, color=C_TREE))

    # s3 - t3 (вага 7)
    parts.append(line(s_nodes["s3"][0], s_nodes["s3"][1], t_nodes["t3"][0], t_nodes["t3"][1], color="#94a3b8", sw=1.5))
    parts.append(text(lx + 205, ly + 240, "вага 7", size=10.5, color="#64748b"))

    # Відмалювання вузлів
    for name, (nx, ny) in list(s_nodes.items()) + list(t_nodes.items()):
        parts.append(circle(nx, ny, 12, fill="#ffffff", stroke="#334155", sw=1.6))
        parts.append(text(nx, ny + 4, name, size=10.5, bold=True, color="#0f172a"))

    parts.append(textbox(lx + lw / 2, ly + 310, "Мінімальне ребро e* гарантовано\nналежить певному MST графа", size=11, pad=6, fill="#f8fafc", stroke=C_TREE)[0])


    # Права панель: Властивість циклу (Cycle Property)
    rx_p, ry_p, rw, rh = 485, 50, 435, 345
    parts.append(rect(rx_p, ry_p, rw, rh, fill=C_PANEL_BG, stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(rx_p + rw / 2, ry_p + 24, "Властивість циклу (Cycle Property)", size=13.5, bold=True, color="#0f172a"))
    parts.append(text(rx_p + rw / 2, ry_p + 42, "Найважче ребро будь-якого циклу НЕ належить унікальному MST", size=10.5, color="#64748b"))

    # Вузли циклу C: c1, c2, c3, c4, c5
    c_nodes = {
        "c1": (rx_p + 120, ry_p + 120),
        "c2": (rx_p + 310, ry_p + 120),
        "c3": (rx_p + 360, ry_p + 205),
        "c4": (rx_p + 215, ry_p + 265),
        "c5": (rx_p + 75, ry_p + 205),
    }

    # Ребра циклу
    # c1 - c2: вага 14 -> НАЙВАЖЧЕ (ВІДХИЛЯЄТЬСЯ)
    parts.append(line(c_nodes["c1"][0], c_nodes["c1"][1], c_nodes["c2"][0], c_nodes["c2"][1], color=C_REJECT, sw=2.5, dash="4 3"))
    parts.append(text(rx_p + 215, ry_p + 110, "вага 14 (e_max)", size=11.5, bold=True, color=C_REJECT))

    # c2 - c3: вага 4
    parts.append(line(c_nodes["c2"][0], c_nodes["c2"][1], c_nodes["c3"][0], c_nodes["c3"][1], color=C_TREE, sw=2.5))
    parts.append(text(rx_p + 355, ry_p + 160, "4", size=11, bold=True, color=C_TREE))

    # c3 - c4: вага 6
    parts.append(line(c_nodes["c3"][0], c_nodes["c3"][1], c_nodes["c4"][0], c_nodes["c4"][1], color=C_TREE, sw=2.5))
    parts.append(text(rx_p + 300, ry_p + 250, "6", size=11, bold=True, color=C_TREE))

    # c4 - c5: вага 2
    parts.append(line(c_nodes["c4"][0], c_nodes["c4"][1], c_nodes["c5"][0], c_nodes["c5"][1], color=C_TREE, sw=2.5))
    parts.append(text(rx_p + 135, ry_p + 250, "2", size=11, bold=True, color=C_TREE))

    # c5 - c1: вага 5
    parts.append(line(c_nodes["c5"][0], c_nodes["c5"][1], c_nodes["c1"][0], c_nodes["c1"][1], color=C_TREE, sw=2.5))
    parts.append(text(rx_p + 80, ry_p + 160, "5", size=11, bold=True, color=C_TREE))

    for name, (nx, ny) in c_nodes.items():
        parts.append(circle(nx, ny, 12, fill="#ffffff", stroke="#334155", sw=1.6))
        parts.append(text(nx, ny + 4, name, size=10.5, bold=True, color="#0f172a"))

    parts.append(textbox(rx_p + rw / 2, ry_p + 310, "Ребро e_max можна безпечно відкинути:\nшлях через решту циклу дешевший", size=11, pad=6, fill="#f8fafc", stroke=C_REJECT)[0])

    render(os.path.join(OUT, "cut-and-cycle-rule.svg"), W, H, *parts)


# ── Фігура 3: Еволюція лісу компонент у DSU ───────────────────────────────────
def fig_dsu_forest_growth():
    W, H = 940, 400
    parts = []

    parts.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    parts.append(text(W / 2, 26, "Еволюція структури DSU (Union-Find) під час виконання алгоритму Краскала", size=16, bold=True))

    steps = [
        {"x": 15, "w": 215, "title": "1. Старт (Make-Set)", "desc": "6 ізольованих коренів\nparent[i] = i, rank = 0"},
        {"x": 245, "w": 215, "title": "2. union(A,B), union(D,E)", "desc": "2 дерева глибини 1\nrank[A]=1, rank[D]=1"},
        {"x": 475, "w": 215, "title": "3. union(A,D), union(B,C)", "desc": "Об'єднання за рангом\nrank[A]=2 (корінь лісу)"},
        {"x": 705, "w": 220, "title": "4. find(E) + Compression", "desc": "Стиснення шляху:\nE вказує напряму на A"},
    ]

    for s in steps:
        sx, sw = s["x"], s["w"]
        parts.append(rect(sx, 48, sw, 335, fill=C_PANEL_BG, stroke="#cbd5e1", sw=1.2, rx=8))
        parts.append(text(sx + sw / 2, 70, s["title"], size=12.5, bold=True, color="#0f172a"))
        parts.append(mtext(sx + sw / 2, 90, s["desc"], size=10.5, color="#64748b"))

    # Стан 1: 6 ізольованих вузлів
    s1_x = 15 + 107
    for i, name in enumerate(["A", "B", "C", "D", "E", "F"]):
        ny = 145 + i * 36
        parts.append(circle(s1_x, ny, 11, fill="#ffffff", stroke="#3b82f6", sw=1.6))
        parts.append(text(s1_x, ny + 3.5, name, size=10.5, bold=True, color="#0f172a"))
        parts.append(text(s1_x + 35, ny + 3.5, "p=" + name, size=9.5, color="#64748b"))

    # Стан 2: Дерева A<-B, D<-E, та окремі C, F
    s2_x = 245 + 107
    # Дерево 1: A (корінь) <- B
    parts.append(circle(s2_x - 40, 150, 12, fill="#eff6ff", stroke="#3b82f6", sw=1.8))
    parts.append(text(s2_x - 40, 154, "A", size=11, bold=True, color="#1d4ed8"))
    parts.append(circle(s2_x - 40, 205, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s2_x - 40, 209, "B", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s2_x - 40, 194, s2_x - 40, 163, color="#3b82f6", sw=1.5))

    # Дерево 2: D (корінь) <- E
    parts.append(circle(s2_x + 40, 150, 12, fill="#eff6ff", stroke="#3b82f6", sw=1.8))
    parts.append(text(s2_x + 40, 154, "D", size=11, bold=True, color="#1d4ed8"))
    parts.append(circle(s2_x + 40, 205, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s2_x + 40, 209, "E", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s2_x + 40, 194, s2_x + 40, 163, color="#3b82f6", sw=1.5))

    # Окремі C, F
    parts.append(circle(s2_x - 30, 275, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s2_x - 30, 279, "C", size=10.5, bold=True, color="#0f172a"))
    parts.append(circle(s2_x + 30, 275, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s2_x + 30, 279, "F", size=10.5, bold=True, color="#0f172a"))

    # Стан 3: Корінь A, до нього D і B, під D висить E, під B висить C
    s3_x = 475 + 107
    parts.append(circle(s3_x, 140, 13, fill="#dcfce7", stroke="#15803d", sw=2.0))
    parts.append(text(s3_x, 144.5, "A", size=12, bold=True, color="#15803d"))

    # Рівень 1: B (ліворуч) та D (праворуч)
    parts.append(circle(s3_x - 45, 200, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s3_x - 45, 204, "B", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s3_x - 40, 190, s3_x - 10, 150, color="#64748b", sw=1.5))

    parts.append(circle(s3_x + 45, 200, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s3_x + 45, 204, "D", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s3_x + 40, 190, s3_x + 10, 150, color="#64748b", sw=1.5))

    # Рівень 2: C (під B) та E (під D)
    parts.append(circle(s3_x - 45, 265, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s3_x - 45, 269, "C", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s3_x - 45, 254, s3_x - 45, 212, color="#64748b", sw=1.5))

    parts.append(circle(s3_x + 45, 265, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s3_x + 45, 269, "E", size=10.5, bold=True, color="#0f172a"))
    parts.append(arrow(s3_x + 45, 254, s3_x + 45, 212, color="#64748b", sw=1.5))

    parts.append(circle(s3_x, 320, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s3_x, 324, "F", size=10.5, bold=True, color="#0f172a"))

    # Стан 4: Стиснення шляхів — E перемикається прямо на A!
    s4_x = 705 + 110
    parts.append(circle(s4_x, 140, 13, fill="#dcfce7", stroke="#15803d", sw=2.0))
    parts.append(text(s4_x, 144.5, "A", size=12, bold=True, color="#15803d"))

    # Вузли на плоському рівні 1 під A: B, C, D, E
    nodes_s4 = [("B", -60), ("C", -20), ("D", 20), ("E", 60)]
    for name, offset in nodes_s4:
        nx, ny = s4_x + offset, 215
        parts.append(circle(nx, ny, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
        parts.append(text(nx, ny + 4, name, size=10.5, bold=True, color="#0f172a"))
        col = "#16a34a" if name in ["C", "E"] else "#64748b"
        sw_a = 1.8 if name in ["C", "E"] else 1.2
        parts.append(arrow(nx, ny - 11, s4_x + offset * 0.2, 153, color=col, sw=sw_a))

    parts.append(circle(s4_x, 285, 11, fill="#ffffff", stroke="#64748b", sw=1.5))
    parts.append(text(s4_x, 289, "F", size=10.5, bold=True, color="#0f172a"))

    parts.append(text(s4_x, 345, "Глибина дерева -> O(1)", size=11, bold=True, color="#15803d"))

    render(os.path.join(OUT, "dsu-forest-growth.svg"), W, H, *parts)


# ── Фігура 4: Порівняння алгоритмів Краскала та Прима ─────────────────────────
def fig_density_tradeoff():
    W, H = 940, 460
    parts = []

    parts.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    parts.append(text(W / 2, 28, "Порівняння алгоритмів кістякових дерев залежно від щільності графа", size=16, bold=True))

    ox, oy = 90.0, 390.0
    pw, ph = 530.0, 310.0

    # Осі координат
    parts.append(line(ox, oy, ox + pw + 25, oy, color=INK, sw=1.5))
    parts.append(line(ox, oy, ox, oy - ph - 15, color=INK, sw=1.5))
    parts.append(text(ox + pw / 2, oy + 42, "Щільність графа: відношення кількості ребер |E| до |V|  ->", size=13, color=INK, bold=True))
    parts.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" font-size="13" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
                 % (ox - 55, oy - ph / 2, FONT, INK, esc("Час виконання T(V, E)  ->")))

    # Позначки по осі X
    x_ticks = [
        (ox, "E = V (дерево)"),
        (ox + pw * 0.33, "E = 4V (розріджений)"),
        (ox + pw * 0.66, "E = V^1.5 (середній)"),
        (ox + pw, "E = V^2 / 2 (повний)"),
    ]
    for xt, label in x_ticks:
        parts.append(line(xt, oy, xt, oy + 6, color=INK, sw=1.2))
        parts.append(text(xt, oy + 22, label, size=10.5, color="#334155"))
        if xt > ox:
            parts.append(line(xt, oy, xt, oy - ph, color="#e2e8f0", sw=1.0, dash="3 3"))

    # Позначки по осі Y
    y_ticks = [
        (oy, "O(V)"),
        (oy - ph * 0.33, "O(V log V)"),
        (oy - ph * 0.66, "O(E log V)"),
        (oy - ph * 0.95, "O(V^2 log V)"),
    ]
    for yt, label in y_ticks:
        parts.append(line(ox - 6, yt, ox, yt, color=INK, sw=1.2))
        parts.append(text(ox - 12, yt + 4, label, size=10.5, color="#334155", anchor="end"))

    # Крива 1: Алгоритм Краскала O(E log V)
    # Зростає швидше на щільних графах (де E -> V^2)
    pts_kruskal = []
    for step in range(101):
        t = step / 100.0
        x_val = ox + pw * t
        # На початку низький, в кінці високий
        y_val = oy - ph * (0.15 + 0.80 * (t ** 1.6))
        pts_kruskal.append((x_val, y_val))
    poly_k = " ".join("%.1f,%.1f" % pt for pt in pts_kruskal)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_k, "#2563eb"))

    # Крива 2: Алгоритм Прима з двійковою купою O(E log V)
    pts_prim_heap = []
    for step in range(101):
        t = step / 100.0
        x_val = ox + pw * t
        y_val = oy - ph * (0.22 + 0.75 * (t ** 1.6))
        pts_prim_heap.append((x_val, y_val))
    poly_ph = " ".join("%.1f,%.1f" % pt for pt in pts_prim_heap)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % (poly_ph, "#f59e0b"))

    # Крива 3: Алгоритм Прима на матриці суміжності O(V^2) (константний від E)
    pts_prim_mat = []
    for step in range(101):
        t = step / 100.0
        x_val = ox + pw * t
        y_val = oy - ph * (0.60 + 0.05 * t)
        pts_prim_mat.append((x_val, y_val))
    poly_pm = " ".join("%.1f,%.1f" % pt for pt in pts_prim_mat)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_pm, "#10b981"))

    # Легенда та висновки праворуч
    lx, ly = ox + pw + 25, 75
    parts.append(rect(lx, ly, 280, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(lx + 140, ly + 24, "Рекомендації вибору", size=13, bold=True, color="#0f172a"))

    # Легенда
    parts.append(line(lx + 15, ly + 55, lx + 45, ly + 55, color="#2563eb", sw=2.8))
    parts.append(text(lx + 52, ly + 59, "Краскал: O(E log V)", size=11, bold=True, anchor="start", color="#1e40af"))
    parts.append(mtext(lx + 52, ly + 76, "Найкращий для розріджених\nграфів (E <= V log V), простий у кеші.", size=10, color="#475569"))

    parts.append(line(lx + 15, ly + 125, lx + 45, ly + 125, color="#f59e0b", sw=2.2, dash="5 3"))
    parts.append(text(lx + 52, ly + 129, "Прим (двійкова купа): O(E log V)", size=11, bold=True, anchor="start", color="#b45309"))
    parts.append(mtext(lx + 52, ly + 146, "Зручний при списковому\nпредставленні та динамічному графі.", size=10, color="#475569"))

    parts.append(line(lx + 15, ly + 195, lx + 45, ly + 195, color="#10b981", sw=2.6))
    parts.append(text(lx + 52, ly + 199, "Прим (матриця): O(V^2)", size=11, bold=True, anchor="start", color="#047857"))
    parts.append(mtext(lx + 52, ly + 216, "Неперевершений на надщільних\nграфах (E ≈ V^2), без сортування.", size=10, color="#475569"))

    # Підсумок
    parts.append(textbox(lx + 140, ly + 280, "Краскал виграє всюди, де граф\nне є екстремально щільним.", size=10.5, pad=6, fill="#eff6ff", stroke="#3b82f6")[0])

    render(os.path.join(OUT, "density-tradeoff.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_kruskal_step_by_step()
    fig_cut_and_cycle_rule()
    fig_dsu_forest_growth()
    fig_density_tradeoff()
    print("All figures successfully generated in %s" % OUT)
