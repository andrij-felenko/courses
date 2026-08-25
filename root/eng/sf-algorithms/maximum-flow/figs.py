# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Залишкова мережа та механізм перенаправлення потоку ───────────────
def fig_residual_graph():
    W, H = 940, 480
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Концепція залишкової мережі: прямі та зворотні дуги як механізм скасування", size=15, color=INK, bold=True))

    # Ліва панель: Поточний стан мережі з потоком
    p.append(rect(35, 65, 420, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(245, 90, "1. Поточний потік f(e) / c(e) у вихідній мережі G", size=12.5, color=INK, bold=True))

    n1 = {
        's': (80.0, 220.0),
        'u': (200.0, 150.0),
        'v': (200.0, 290.0),
        't': (380.0, 220.0)
    }

    # Ребра мережі з потоком/місткістю
    edges1 = [
        ('s', 'u', "f=3 / c=4", True),
        ('s', 'v', "f=1 / c=3", True),
        ('u', 'v', "f=2 / c=2", True),
        ('u', 't', "f=1 / c=3", True),
        ('v', 't', "f=3 / c=5", True),
    ]

    for u, v, lbl, is_active in edges1:
        x1, y1 = n1[u]
        x2, y2 = n1[v]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        sx, sy = x1 + (dx/dist)*18, y1 + (dy/dist)*18
        ex, ey = x2 - (dx/dist)*18, y2 - (dy/dist)*18
        p.append(arrow(sx, sy, ex, ey, color=FIELD if "f=2 / c=2" in lbl else LINE, sw=2.2 if "f=2 / c=2" in lbl else 1.8))
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        off_y = -12 if (u, v) in [('s', 'u'), ('u', 't')] else (14 if (u, v) in [('s', 'v'), ('v', 't')] else 0)
        off_x = 42 if (u, v) == ('u', 'v') else 0
        p.append(text(mx + off_x, my + off_y, lbl, size=10.5, color=FIELD if "f=2 / c=2" in lbl else INK, bold=True))

    for k, (x, y) in n1.items():
        col = NEG if k == 's' else (POS if k == 't' else LINE)
        p.append(circle(x, y, 17.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4.5, k, size=13, color=INK, bold=True))

    p.append(fitbox(45, 335, 400, 55,
                    "Ребро u→v повністю насичене потоком 2/2.\nПрямий залишок вичерпано, але потік можна повернути назад.",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    # Права панель: Залишкова мережа G_f
    p.append(rect(485, 65, 420, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(695, 90, "2. Залишкова мережа G_f із залишковими місткостями c_f", size=12.5, color=INK, bold=True))

    n2 = {
        's': (530.0, 220.0),
        'u': (650.0, 150.0),
        'v': (650.0, 290.0),
        't': (830.0, 220.0)
    }

    # Залишкові ребра: (u, v, label, color, dash, offset_x, offset_y)
    res_edges = [
        ('s', 'u', "c_f=1 (4-3)", NEG, None, 0, -12),
        ('u', 's', "c_f=3 (повернення)", POS, "3,3", 0, 12),
        ('s', 'v', "c_f=2 (3-1)", NEG, None, 0, 12),
        ('v', 's', "c_f=1", POS, "3,3", 0, -12),
        ('v', 'u', "c_f=2 (скасування f(u,v))", FIELD, None, -65, 0),
        ('u', 't', "c_f=2 (3-1)", NEG, None, 0, -12),
        ('t', 'u', "c_f=1", POS, "3,3", 0, 12),
        ('v', 't', "c_f=2 (5-3)", NEG, None, 0, 12),
        ('t', 'v', "c_f=3", POS, "3,3", 0, -12),
    ]

    for u, v, lbl, col, dsh, ox, oy in res_edges:
        x1, y1 = n2[u]
        x2, y2 = n2[v]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        # Зсув паралельних прямих і зворотних ребер
        nx, ny = -dy / dist, dx / dist
        shift = 4.5 if (u, v) in [('s', 'u'), ('u', 't'), ('s', 'v'), ('v', 't')] else (-4.5 if (u, v) in [('u', 's'), ('t', 'u'), ('v', 's'), ('t', 'v')] else 0)
        sx, sy = x1 + (dx/dist)*18 + nx*shift, y1 + (dy/dist)*18 + ny*shift
        ex, ey = x2 - (dx/dist)*18 + nx*shift, y2 - (dy/dist)*18 + ny*shift
        p.append(line(sx, sy, ex, ey, color=col, sw=1.8, dash=dsh))
        p.append(arrow(ex - (dx/dist)*2, ey - (dy/dist)*2, ex, ey, color=col, sw=1.8))
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        p.append(text(mx + ox, my + oy, lbl, size=9.5, color=col, bold=True))

    for k, (x, y) in n2.items():
        col = NEG if k == 's' else (POS if k == 't' else LINE)
        p.append(circle(x, y, 17.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4.5, k, size=13, color=INK, bold=True))

    p.append(fitbox(495, 335, 400, 55,
                    "Зворотна дуга v→u з місткістю c_f(v, u) = f(u, v) = 2 дозволяє\nновому шляху зменшити потік на u→v і перенаправити його.",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK))

    p.append(rect(35, 415, W - 70, 45, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 442, "Залишкова мережа G_f формалізує простір усіх допустимих коригувань потоку без порушення законів Кірхгофа.", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "residual-graph-concept.svg"), W, H, *p)


# ── Фіг. 2: Теорема про максимальний потік і мінімальний розріз ────────────────
def fig_max_flow_min_cut():
    W, H = 940, 480
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Теорема Форда — Фалкерсона: рівність максимального потоку та мінімального розрізу", size=15, color=INK, bold=True))

    # Зона S (ліворуч, блакитна)
    p.append(rect(40, 70, 390, 310, fill="#edf4fc", stroke="#a8c5e8", sw=1.5, rx=8))
    p.append(text(235, 98, "Множина S (вершини, досяжні з s у G_f)", size=13, color=NEG, bold=True))

    # Зона T (праворуч, рожева)
    p.append(rect(510, 70, 390, 310, fill="#fdf0ed", stroke="#f2b5a7", sw=1.5, rx=8))
    p.append(text(705, 98, "Множина T = V \\ S (вершини, недосяжні з s)", size=13, color=POS, bold=True))

    # Лінія розрізу (зелений пунктир посередині)
    p.append(line(470, 65, 470, 390, color=FIELD, sw=2.5, dash="6,4"))
    p.append(text(470, 56, "Розріз (S, T)", size=12, color=FIELD, bold=True))

    nodes = {
        's':  (110.0, 230.0, "#ffffff", NEG),
        'u1': (260.0, 160.0, "#ffffff", INK),
        'u2': (260.0, 300.0, "#ffffff", INK),
        'v1': (680.0, 160.0, "#ffffff", INK),
        'v2': (680.0, 300.0, "#ffffff", INK),
        't':  (830.0, 230.0, "#ffffff", POS),
    }

    # Внутрішні ребра в S
    p.append(arrow(128, 220, 242, 170, color=LINE, sw=1.8))
    p.append(text(180, 185, "10/10", size=10.5, color=INK))
    p.append(arrow(128, 240, 242, 290, color=LINE, sw=1.8))
    p.append(text(180, 280, "8/10", size=10.5, color=INK))
    p.append(arrow(260, 180, 260, 280, color=LINE, sw=1.8))
    p.append(text(285, 230, "2/5", size=10.5, color=INK))

    # Прямі ребра, що перетинають розріз S -> T (НАСИЧЕНІ)
    cut_edges = [
        ('u1', 'v1', "c=7 (f=7)", "Повністю насичене (7/7)"),
        ('u1', 'v2', "c=3 (f=3)", "Повністю насичене (3/3)"),
        ('u2', 'v2', "c=8 (f=8)", "Повністю насичене (8/8)"),
    ]

    for (u, v, cap_lbl, note) in cut_edges:
        x1, y1 = nodes[u][0], nodes[u][1]
        x2, y2 = nodes[v][0], nodes[v][1]
        p.append(arrow(x1+20, y1, x2-20, y2, color=POS, sw=2.5))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        off_y = -12 if u == 'u1' and v == 'v1' else (14 if u == 'u2' and v == 'v2' else -10)
        p.append(text(mx, my + off_y, cap_lbl, size=11, color=POS, bold=True))

    # Зворотне ребро T -> S (потік f = 0)
    p.append(line(660, 200, 280, 200, color="#95a5a6", sw=1.8, dash="4,4"))
    p.append(arrow(300, 200, 280, 200, color="#95a5a6", sw=1.8))
    p.append(text(470, 190, "f=0 (зворотний потік відсутній)", size=10.5, color="#7f8c8d", italic=True))

    # Внутрішні ребра в T
    p.append(arrow(700, 170, 812, 220, color=LINE, sw=1.8))
    p.append(text(760, 185, "7/10", size=10.5, color=INK))
    p.append(arrow(700, 290, 812, 240, color=LINE, sw=1.8))
    p.append(text(760, 280, "11/12", size=10.5, color=INK))

    for nid, (nx, ny, fill_col, strk_col) in nodes.items():
        p.append(circle(nx, ny, 19.0, fill=fill_col, stroke=strk_col, sw=2.0))
        p.append(text(nx, ny + 5, nid, size=13.5, color=INK, bold=True))

    # Підсумкова плашка
    p.append(rect(40, 395, W - 80, 55, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 420, "Пропускна спроможність розрізу c(S, T) = 7 + 3 + 8 = 18. Сумарний потік |f| = 18.", size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 440, "Усі прямі дуги S→T вичерпані (c_f = 0), усі зворотні T→S порожні (f = 0) ⇒ потік максимальний.", size=11, color=FIELD))

    render(os.path.join(OUT, "max-flow-min-cut.svg"), W, H, *p)


# ── Фіг. 3: Алгоритм Едмондса — Карпа та вибір найкоротшого шляху BFS ─────────
def fig_edmonds_karp_bfs():
    W, H = 940, 480
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Алгоритм Едмондса — Карпа: пошук найкоротшого розширювального шляху за ребрами", size=15, color=INK, bold=True))

    # Ліва частина: Вибір шляху BFS
    p.append(rect(35, 65, 420, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(245, 90, "Крок ітерації: BFS знаходить шлях s → u1 → t", size=12.5, color=INK, bold=True))

    n1 = {
        's':  (80.0, 220.0),
        'u1': (245.0, 145.0),
        'u2': (245.0, 295.0),
        't':  (410.0, 220.0)
    }

    # Активний шлях s -> u1 -> t (зелений)
    p.append(arrow(98, 212, 228, 152, color=FIELD, sw=2.5))
    p.append(text(150, 168, "c_f = 10", size=11, color=FIELD, bold=True))
    p.append(arrow(262, 152, 392, 212, color=FIELD, sw=2.5))
    p.append(text(340, 168, "c_f = 4 [вузьке місце]", size=11, color=POS, bold=True))

    # Альтернативні ребра (сірий пунктир)
    p.append(line(98, 228, 228, 288, color="#95a5a6", sw=1.5, dash="3,3"))
    p.append(arrow(210, 279, 228, 288, color="#95a5a6", sw=1.5))
    p.append(text(150, 275, "c_f = 10", size=10, color=MUTED))
    p.append(line(245, 165, 245, 275, color="#95a5a6", sw=1.5, dash="3,3"))
    p.append(arrow(245, 260, 245, 275, color="#95a5a6", sw=1.5))
    p.append(text(275, 220, "c_f = 2", size=10, color=MUTED))
    p.append(line(262, 288, 392, 228, color="#95a5a6", sw=1.5, dash="3,3"))
    p.append(arrow(375, 236, 392, 228, color="#95a5a6", sw=1.5))
    p.append(text(340, 275, "c_f = 10", size=10, color=MUTED))

    for k, (x, y) in n1.items():
        col = FIELD if k in ['s', 'u1', 't'] else MUTED
        p.append(circle(x, y, 17.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4.5, k, size=13, color=INK, bold=True))

    p.append(fitbox(45, 335, 400, 55,
                    "BFS обирає шлях довжини 2 ребра (s→u1→t).\n"
                    "Пляшкове горло Δ = min(10, 4) = 4 проштовхується по всьому шляху.",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    # Права частина: Оновлення залишкових місткостей
    p.append(rect(485, 65, 420, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(695, 90, "Оновлення G_f: пряме ребро u1→t насичене (c_f = 0)", size=12.5, color=INK, bold=True))

    n2 = {
        's':  (530.0, 220.0),
        'u1': (695.0, 145.0),
        'u2': (695.0, 295.0),
        't':  (860.0, 220.0)
    }

    # s -> u1 (залишок зменшився до 6, з'явився зворотний 4)
    p.append(arrow(548, 210, 678, 143, color=LINE, sw=1.8))
    p.append(text(600, 165, "c_f = 6 (10-4)", size=10.5, color=INK, bold=True))
    p.append(line(678, 153, 548, 220, color=POS, sw=1.5, dash="3,3"))
    p.append(arrow(565, 211, 548, 220, color=POS, sw=1.5))
    p.append(text(620, 195, "c_f(зворотне) = 4", size=9.5, color=POS))

    # u1 -> t насичене (прямого немає, тільки зворотне c_f = 4)
    p.append(line(712, 145, 842, 210, color=POS, sw=1.5, dash="3,3"))
    p.append(arrow(842, 220, 712, 155, color=POS, sw=1.8))
    p.append(text(785, 175, "u1→t насичено!", size=10.5, color=POS, bold=True))
    p.append(text(785, 192, "c_f(t→u1) = 4", size=9.5, color=POS))

    # Решта ребер
    p.append(arrow(548, 228, 678, 288, color=LINE, sw=1.5))
    p.append(text(600, 275, "c_f = 10", size=10, color=MUTED))
    p.append(arrow(695, 165, 695, 275, color=LINE, sw=1.5))
    p.append(arrow(712, 288, 842, 228, color=LINE, sw=1.5))
    p.append(text(785, 275, "c_f = 10", size=10, color=MUTED))

    for k, (x, y) in n2.items():
        col = NEG if k == 's' else (POS if k == 't' else LINE)
        p.append(circle(x, y, 17.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4.5, k, size=13, color=INK, bold=True))

    p.append(fitbox(495, 335, 400, 55,
                    "Критичне ребро u1→t зникає з G_f.\n"
                    "Наступний шлях змушений іти в обхід через u2, збільшуючи довжину.",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK))

    p.append(rect(35, 415, W - 70, 45, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 442, "Монотонність найкоротших шляхів BFS гарантує не більше O(V · E) аугментацій та складність O(V · E²).", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "edmonds-karp-bfs.svg"), W, H, *p)


# ── Фіг. 4: Моделювання та зведення прикладних задач до максимального потоку ───
def fig_reductions_gadgets():
    W, H = 940, 480
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Канонічні зведення задач до максимального потоку (Reductions & Gadgets)", size=15, color=INK, bold=True))

    # Блок 1: Обмеження на вершини (Node Splitting)
    p.append(rect(35, 65, 275, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(172, 88, "1. Пропускна спроможність вершин", size=11.5, color=INK, bold=True))

    # Схема розщеплення v -> v_in -> v_out
    p.append(circle(95, 160, 16.0, fill="#ffffff", stroke=MUTED, sw=1.5))
    p.append(text(95, 164, "u", size=11, color=INK))
    p.append(arrow(111, 160, 144, 160, color=LINE, sw=1.5))

    p.append(circle(160, 160, 16.0, fill="#eaf0fd", stroke=NEG, sw=1.8))
    p.append(text(160, 164, "v_in", size=10, color=NEG, bold=True))

    p.append(arrow(176, 160, 209, 160, color=POS, sw=2.2))
    p.append(text(192, 142, "c(v)", size=10.5, color=POS, bold=True))

    p.append(circle(225, 160, 16.0, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(225, 164, "v_out", size=9.5, color=POS, bold=True))

    p.append(arrow(241, 160, 274, 160, color=LINE, sw=1.5))
    p.append(circle(290, 160, 16.0, fill="#ffffff", stroke=MUTED, sw=1.5))
    p.append(text(290, 164, "w", size=11, color=INK))

    p.append(fitbox(45, 220, 255, 165,
                    "Розщеплення вузла v:\n"
                    "• Вершина v замінюється парою (v_in, v_out).\n"
                    "• Внутрішнє ребро (v_in, v_out) отримує місткість c(v).\n"
                    "• Усі вхідні дуги ведуть у v_in, вихідні — з v_out.\n"
                    "Гарантує обмеження наскрізного трафіку через вузол.",
                    size=10.5, fill="#ffffff", stroke="#d0d7de", color=INK))

    # Блок 2: Декілька джерел і стоків (Super-source & Super-sink)
    p.append(rect(330, 65, 275, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(467, 88, "2. Кілька джерел і стоків", size=11.5, color=INK, bold=True))

    # S* з'єднується з s1, s2; t1, t2 з'єднуються з T*
    p.append(circle(365, 160, 16.0, fill="#eaf0fd", stroke=NEG, sw=2.0))
    p.append(text(365, 164, "S*", size=11, color=NEG, bold=True))

    p.append(arrow(381, 155, 414, 135, color=NEG, sw=1.8))
    p.append(text(395, 135, "S1", size=9.5, color=NEG))
    p.append(arrow(381, 165, 414, 185, color=NEG, sw=1.8))
    p.append(text(395, 192, "S2", size=9.5, color=NEG))

    p.append(circle(430, 130, 14.0, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(430, 134, "s1", size=10, color=INK))
    p.append(circle(430, 190, 14.0, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(430, 194, "s2", size=10, color=INK))

    p.append(circle(510, 130, 14.0, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(510, 134, "t1", size=10, color=INK))
    p.append(circle(510, 190, 14.0, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(510, 194, "t2", size=10, color=INK))

    p.append(arrow(524, 135, 557, 155, color=POS, sw=1.8))
    p.append(text(545, 135, "T1", size=9.5, color=POS))
    p.append(arrow(524, 185, 557, 165, color=POS, sw=1.8))
    p.append(text(545, 192, "T2", size=9.5, color=POS))

    p.append(circle(575, 160, 16.0, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(text(575, 164, "T*", size=11, color=POS, bold=True))

    p.append(fitbox(340, 220, 255, 165,
                    "Суперджерело та суперстік:\n"
                    "• Вводиться спільний витік S* та стік T*.\n"
                    "• Ребра (S*, s_i) мають місткості генерації S_i.\n"
                    "• Ребра (t_j, T*) мають місткості споживання T_j.\n"
                    "Зводить задачу багатьох терміналів до класичного s-t потоку.",
                    size=10.5, fill="#ffffff", stroke="#d0d7de", color=INK))

    # Блок 3: Двочасткове паросполучення (Bipartite Matching)
    p.append(rect(625, 65, 280, 335, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(765, 88, "3. Двочасткове паросполучення", size=11.5, color=INK, bold=True))

    p.append(circle(655, 160, 16.0, fill="#eaf0fd", stroke=NEG, sw=2.0))
    p.append(text(655, 164, "s", size=12, color=NEG, bold=True))

    l_nodes = [(720, 125, "L1"), (720, 160, "L2"), (720, 195, "L3")]
    r_nodes = [(810, 125, "R1"), (810, 160, "R2"), (810, 195, "R3")]

    for lx, ly, name in l_nodes:
        p.append(arrow(671, 160, lx-14, ly, color=NEG, sw=1.4))
        p.append(circle(lx, ly, 13.0, fill="#ffffff", stroke=LINE, sw=1.4))
        p.append(text(lx, ly + 3.5, name, size=9.5, color=INK))

    # Двочасткові ребра (c = 1)
    bip_edges = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
    for li, ri in bip_edges:
        p.append(arrow(l_nodes[li][0]+13, l_nodes[li][1], r_nodes[ri][0]-13, r_nodes[ri][1], color=FIELD, sw=1.4))

    for rx, ry, name in r_nodes:
        p.append(circle(rx, ry, 13.0, fill="#ffffff", stroke=LINE, sw=1.4))
        p.append(text(rx, ry + 3.5, name, size=9.5, color=INK))
        p.append(arrow(rx+13, ry, 860, 160, color=POS, sw=1.4))

    p.append(circle(875, 160, 16.0, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(text(875, 164, "t", size=12, color=POS, bold=True))

    p.append(fitbox(635, 220, 260, 165,
                    "Зведення паросполучення:\n"
                    "• Всі ребра отримують одиничну місткість c=1.\n"
                    "• Цілочисельність гарантує f(e) ∈ {0, 1}.\n"
                    "• Насичені дуги між L та R утворюють максимальне незалежне паросполучення.",
                    size=10.5, fill="#ffffff", stroke="#d0d7de", color=INK))

    p.append(rect(35, 415, W - 70, 45, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 442, "Конструктивні зведення дозволяють розв'язувати десятки прикладних задач дискретної оптимізації через єдиний розв'язувач потоку.", size=11.5, color=INK, bold=True))

    render(os.path.join(OUT, "reductions-gadgets.svg"), W, H, *p)


if __name__ == "__main__":
    fig_residual_graph()
    fig_max_flow_min_cut()
    fig_edmonds_karp_bfs()
    fig_reductions_gadgets()
    print("Всі 4 фігури для maximum-flow успішно згенеровано.")
