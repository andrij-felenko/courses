# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Побудова рівневого графа (Layered Graph) ─────────────────────────
# Показує розбиття вершин на рівні d(v) від s до t за допомогою BFS.
# Виділено допустимі ребра (d(v) = d(u) + 1) та відкинуті ребра (поперечні, зворотні, нульові).
def fig_layered_graph():
    W, H = 940, 480
    p = []

    # Заголовок та підкладка
    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Побудова рівневого графа G_L за відстанями BFS від джерела s", size=15, color=INK, bold=True))

    # Стовпчики рівнів
    layers = [
        ("Рівень 0\nd(s) = 0", 110.0),
        ("Рівень 1\nd = 1", 330.0),
        ("Рівень 2\nd = 2", 570.0),
        ("Рівень 3\nd(t) = 3", 810.0)
    ]

    for label, cx in layers:
        p.append(rect(cx - 85, 75, 170, 310, fill="#f6f8fa", stroke="#e1e4e8", sw=1.2, rx=6))
        p.append(mtext(cx, 100, label, size=13, color=MUTED, bold=True, lh=1.25))

    # Координати вершин
    nodes = {
        's':  (110.0, 230.0, "s", "#eaf0fd", NEG),
        'v1': (330.0, 160.0, "v1", "#ffffff", INK),
        'v2': (330.0, 300.0, "v2", "#ffffff", INK),
        'v3': (570.0, 160.0, "v3", "#ffffff", INK),
        'v4': (570.0, 300.0, "v4", "#ffffff", INK),
        't':  (810.0, 230.0, "t", "#fdecea", POS)
    }

    # Ребра: (u, v, cap_label, type)
    # type: 'admissible' (зелений/активний), 'cross' (пунктир сірий), 'backward' (пунктир червоний)
    edges = [
        # Рівень 0 -> Рівень 1
        ('s', 'v1', "c=10", 'admissible'),
        ('s', 'v2', "c=10", 'admissible'),
        # Рівень 1 -> Рівень 1 (внутрішнє / поперечне)
        ('v1', 'v2', "c=2 (поперечне, d=1→1)", 'cross'),
        # Рівень 1 -> Рівень 2
        ('v1', 'v3', "c=4", 'admissible'),
        ('v1', 'v4', "c=8", 'admissible'),
        ('v2', 'v4', "c=9", 'admissible'),
        # Рівень 2 -> Рівень 1 (зворотне)
        ('v3', 'v2', "c=3 (зворотне, d=2→1)", 'backward'),
        # Рівень 2 -> Рівень 3
        ('v3', 't', "c=10", 'admissible'),
        ('v4', 't', "c=10", 'admissible'),
    ]

    # Малюємо ребра
    for u, v, lbl, etype in edges:
        x1, y1 = nodes[u][0], nodes[u][1]
        x2, y2 = nodes[v][0], nodes[v][1]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx*dx + dy*dy)**0.5
        nx, ny = dx / dist, dy / dist
        sx, sy = x1 + nx * 22, y1 + ny * 22
        ex, ey = x2 - nx * 22, y2 - ny * 22

        if etype == 'admissible':
            p.append(arrow(sx, sy, ex, ey, color=FIELD, sw=2.2))
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            offset_y = -10 if y1 == y2 or (u == 's' and v == 'v1') or (u == 'v3' and v == 't') else 12
            p.append(text(mx, my + offset_y, lbl, size=11, color=FIELD, bold=True))
        elif etype == 'cross':
            p.append(line(sx, sy, ex, ey, color="#95a5a6", sw=1.5, dash="4,4"))
            p.append(text((sx + ex) / 2 + 75, (sy + ey) / 2, lbl, size=10.5, color="#7f8c8d", italic=True))
        elif etype == 'backward':
            p.append(line(sx, sy, ex, ey, color="#e74c3c", sw=1.5, dash="4,4"))
            p.append(text((sx + ex) / 2 - 40, (sy + ey) / 2 + 16, lbl, size=10.5, color="#c0392b", italic=True))

    # Малюємо вершини
    for nid, (nx, ny, name, fill_col, strk_col) in nodes.items():
        p.append(circle(nx, ny, 20.0, fill=fill_col, stroke=strk_col, sw=2.0))
        p.append(text(nx, ny + 5, name, size=14, color=INK, bold=True))

    # Легенда внизу
    p.append(rect(40, 400, W - 80, 55, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(line(60, 427, 95, 427, color=FIELD, sw=2.5))
    p.append(text(190, 431, "Допустимі ребра G_L (d(v) = d(u) + 1)", size=11.5, color=INK, bold=True))

    p.append(line(370, 427, 405, 427, color="#95a5a6", sw=1.5, dash="4,4"))
    p.append(text(500, 431, "Відкинуті: d(v) ≤ d(u) (поперечні/в межах шару)", size=11.5, color=MUTED))

    p.append(line(670, 427, 705, 427, color="#e74c3c", sw=1.5, dash="4,4"))
    p.append(text(790, 431, "Відкинуті: d(v) < d(u) (зворотні ребра)", size=11.5, color=MUTED))

    render(os.path.join(OUT, "layered-graph.svg"), W, H, *p)


# ── Фіг. 2: Проштовхування блокуючого потоку через DFS з оптимізацією ptr ────
def fig_blocking_flow_push():
    W, H = 940, 480
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Пошук блокуючого потоку в G_L: насичення вузьких місць та видалення глухих кутів", size=15, color=INK, bold=True))

    # Ліва частина: Шлях 1 насичує вузьке місце
    p.append(rect(35, 65, 420, 340, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(245, 90, "Крок 1: Проштовхування вздовж s → v1 → v3 → t", size=12.5, color=INK, bold=True))

    n1 = {
        's':  (80.0, 230.0),
        'v1': (180.0, 150.0),
        'v2': (180.0, 310.0),
        'v3': (310.0, 150.0),
        'v4': (310.0, 310.0),
        't':  (410.0, 230.0)
    }

    # Малюємо активний шлях (s->v1->v3->t з потоком 4)
    path1_edges = [('s', 'v1', "10 [потік 4]"), ('v1', 'v3', "4 [насичено 4/4!]"), ('v3', 't', "10 [потік 4]")]
    for u, v, lbl in path1_edges:
        x1, y1 = n1[u]
        x2, y2 = n1[v]
        p.append(arrow(x1+15, y1, x2-15, y2, color=NEG, sw=2.5))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 12
        p.append(text(mx, my, lbl, size=10, color=NEG, bold=True))

    # Інші ребра сірим
    other1 = [('s', 'v2'), ('v1', 'v4'), ('v2', 'v4'), ('v4', 't')]
    for u, v in other1:
        x1, y1 = n1[u]
        x2, y2 = n1[v]
        p.append(arrow(x1+15, y1, x2-15, y2, color="#bdc3c7", sw=1.2))

    for k, (x, y) in n1.items():
        col = NEG if k in ['s', 'v1', 'v3', 't'] else MUTED
        p.append(circle(x, y, 16.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4, k, size=12, color=INK, bold=True))

    p.append(fitbox(45, 335, 400, 55,
                    "Вузьке місце v1→v3 повністю вичерпано (4/4).\nРебро насичене й вилучається з G_L.",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    # Права частина: Шлях 2 та відсікання тупиків вказівником ptr
    p.append(rect(485, 65, 420, 340, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(695, 90, "Крок 2: Оптимізація ptr[v1] пропускає v1→v3", size=12.5, color=INK, bold=True))

    n2 = {
        's':  (530.0, 230.0),
        'v1': (630.0, 150.0),
        'v2': (630.0, 310.0),
        'v3': (760.0, 150.0),
        'v4': (760.0, 310.0),
        't':  (860.0, 230.0)
    }

    # v1->v3 перекреслено
    p.append(line(n2['v1'][0]+15, n2['v1'][1], n2['v3'][0]-15, n2['v3'][1], color="#e74c3c", sw=1.5, dash="3,3"))
    p.append(text(695, 140, "ptr[v1]++ (пропуск)", size=10.5, color=POS, bold=True))

    # Новий активний шлях s->v1->v4->t (потік 6)
    path2_edges = [('s', 'v1', "залишок 6 [потік 6]"), ('v1', 'v4', "8 [потік 6]"), ('v4', 't', "10 [потік 6]")]
    for u, v, lbl in path2_edges:
        x1, y1 = n2[u]
        x2, y2 = n2[v]
        p.append(arrow(x1+15, y1, x2-15, y2, color=FIELD, sw=2.5))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        offset = -12 if u == 's' or v == 't' else 12
        p.append(text(mx, my + offset, lbl, size=10, color=FIELD, bold=True))

    # Ребро s->v2 та v2->v4
    p.append(arrow(n2['s'][0]+15, n2['s'][1], n2['v2'][0]-15, n2['v2'][1], color="#bdc3c7", sw=1.2))
    p.append(arrow(n2['v2'][0]+15, n2['v2'][1], n2['v4'][0]-15, n2['v4'][1], color="#bdc3c7", sw=1.2))

    for k, (x, y) in n2.items():
        col = FIELD if k in ['s', 'v1', 'v4', 't'] else MUTED
        p.append(circle(x, y, 16.0, fill="#ffffff", stroke=col, sw=2.0))
        p.append(text(x, y + 4, k, size=12, color=INK, bold=True))

    p.append(fitbox(495, 335, 400, 55,
                    "ptr[u] запам'ятовує останнє перевірене ребро.\nDFS ніколи не сканує насичені ребра повторно.",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK))

    p.append(rect(35, 420, W - 70, 40, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 444, "Сумарний блокуючий потік фази = 4 + 6 + 4 = 14. Шляхів довжини 3 більше немає.", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "blocking-flow-push.svg"), W, H, *p)


# ── Фіг. 3: Суворе зростання відстані між фазами (Level Monotonicity) ─────────
def fig_phase_growth():
    W, H = 940, 460
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Монотонність відстаней: руйнування найкоротших шляхів та зростання d(s, t)", size=15, color=INK, bold=True))

    # Фаза k (довжина 3)
    p.append(rect(40, 70, 410, 310, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(245, 95, "Фаза k: відстань d_k(s, t) = 3", size=13, color=INK, bold=True))

    # Спрощена схема ланцюжка
    pk_nodes = [
        (80.0, 200.0, "s"),
        (180.0, 200.0, "u"),
        (290.0, 200.0, "v"),
        (390.0, 200.0, "t")
    ]
    for i in range(len(pk_nodes) - 1):
        x1, y1, _ = pk_nodes[i]
        x2, y2, _ = pk_nodes[i+1]
        col = POS if i == 1 else FIELD
        lbl = "насичується!" if i == 1 else "потік"
        p.append(arrow(x1+16, y1, x2-16, y2, color=col, sw=2.5))
        p.append(text((x1+x2)/2, y1 - 12, lbl, size=10.5, color=col, bold=True))

    for x, y, name in pk_nodes:
        p.append(circle(x, y, 16.0, fill="#ffffff", stroke=LINE, sw=1.8))
        p.append(text(x, y + 4, name, size=12, color=INK, bold=True))

    p.append(fitbox(55, 270, 380, 95,
                    "Усі шляхи довжини 3 містять хоча б одне насичене ребро.\n"
                    "Пряме ребро u→v вилучається з залишкової мережі.\n"
                    "З'являється лише зворотне ребро v→u, яке веде назад (d=2→1).",
                    size=11, fill="#ffffff", stroke="#dfe4ea", color=INK))

    # Фаза k+1 (довжина ≥ 4)
    p.append(rect(490, 70, 410, 310, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(695, 95, "Фаза k+1: відстань d_{k+1}(s, t) ≥ 4", size=13, color=INK, bold=True))

    pk1_nodes = [
        (530.0, 240.0, "s"),
        (620.0, 160.0, "u"),
        (710.0, 160.0, "w"),
        (800.0, 240.0, "v"),
        (860.0, 240.0, "t")
    ]
    # Обхідний довший шлях
    p.append(arrow(530+14, 240-10, 620-10, 160+10, color=NEG, sw=2.0))
    p.append(arrow(620+16, 160, 710-16, 160, color=NEG, sw=2.0))
    p.append(arrow(710+10, 160+10, 800-10, 240-10, color=NEG, sw=2.0))
    p.append(arrow(800+16, 240, 860-16, 240, color=NEG, sw=2.0))

    # Перекреслене пряме ребро u->v
    p.append(line(620+14, 160+14, 800-14, 240-14, color=POS, sw=1.8, dash="3,3"))
    p.append(text(710, 220, "u→v насичено", size=10.5, color=POS, bold=True))

    for x, y, name in pk1_nodes:
        p.append(circle(x, y, 15.0, fill="#ffffff", stroke=NEG, sw=1.8))
        p.append(text(x, y + 4, name, size=11.5, color=INK, bold=True))

    p.append(fitbox(505, 270, 380, 95,
                    "Новий найкоротший шлях змушений робити обхід (s→u→w→v→t).\n"
                    "Його довжина суворо більша: d_{k+1} ≥ d_k + 1.\n"
                    "Кількість фаз не може перевищувати |V| - 1.",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    p.append(rect(40, 395, W - 80, 45, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=5))
    p.append(text(W / 2, 422, "Лема монотонності гарантує: максимум |V| - 1 фаз до досягнення максимального потоку.", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "phase-growth.svg"), W, H, *p)


# ── Фіг. 4: Мережі одиничної пропускної спроможності та паросполучення ────────
def fig_unit_network_bound():
    W, H = 940, 460
    p = []

    p.append(rect(15, 15, W - 30, H - 30, fill="#fcfdfe", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 42, "Одиничні мережі: доведення складності O(E · √V) для двочасткового паросполучення", size=15, color=INK, bold=True))

    # Схема двочасткового графа з s та t
    px, py = 50.0, 75.0

    # s
    p.append(circle(px + 40, py + 140, 20.0, fill="#eaf0fd", stroke=NEG, sw=2.0))
    p.append(text(px + 40, py + 145, "s", size=14, color=INK, bold=True))

    # Частка L (вершини 1, 2, 3)
    l_nodes = [(px + 200, py + 60, "L1"), (px + 200, py + 140, "L2"), (px + 200, py + 220, "L3")]
    # Частка R (вершини 1, 2, 3)
    r_nodes = [(px + 420, py + 60, "R1"), (px + 420, py + 140, "R2"), (px + 420, py + 220, "R3")]

    # t
    p.append(circle(px + 580, py + 140, 20.0, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(text(px + 580, py + 145, "t", size=14, color=INK, bold=True))

    # Ребра від s до L (c = 1)
    for lx, ly, name in l_nodes:
        p.append(arrow(px + 60, py + 140, lx - 18, ly, color=FIELD, sw=1.8))
        p.append(circle(lx, ly, 18.0, fill="#ffffff", stroke=INK, sw=1.5))
        p.append(text(lx, ly + 4, name, size=11.5, color=INK, bold=True))

    # Ребра між L та R (c = 1)
    matching_edges = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)]
    for li, ri in matching_edges:
        lx, ly, _ = l_nodes[li]
        rx, ry, _ = r_nodes[ri]
        p.append(arrow(lx + 18, ly, rx - 18, ry, color=FIELD, sw=1.8))

    # Ребра від R до t (c = 1)
    for rx, ry, name in r_nodes:
        p.append(circle(rx, ry, 18.0, fill="#ffffff", stroke=INK, sw=1.5))
        p.append(text(rx, ry + 4, name, size=11.5, color=INK, bold=True))
        p.append(arrow(rx + 18, ry, px + 560, py + 140, color=FIELD, sw=1.8))

    # Пояснювальна панель праворуч
    bx, by, bw, bh = 680.0, 75.0, 220.0, 290.0
    p.append(rect(bx, by, bw, bh, fill="#f6f8fa", stroke="#dfe4ea", sw=1.2, rx=6))
    p.append(text(bx + bw / 2, by + 25, "Властивості мережі", size=12.5, color=INK, bold=True))

    bullets = [
        "1. Кожна вершина v ∈ L∪R",
        "   має deg_in=1 або deg_out=1.",
        "2. Шляхи в залишковій",
        "   мережі вершинно-неперетинні.",
        "3. Після √V фаз довжина",
        "   шляхів > √V.",
        "4. Залишковий потік містить",
        "   ≤ V / √V = √V шляхів.",
        "5. Загалом ≤ 2√V фаз."
    ]
    for idx, b in enumerate(bullets):
        p.append(text(bx + 15, by + 55 + idx * 24, b, size=10.5, color=INK, anchor="start"))

    p.append(fitbox(40, 380, W - 80, 55,
                    "Для одиничних мереж кожна фаза виконується за O(E), а кількість фаз обмежена 2√V.\n"
                    "Це дає точний час O(E · √V) — алгоритм Гопкрофта — Карпа є окремим випадком алгоритму Дініца.",
                    size=11.5, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "unit-network-bound.svg"), W, H, *p)


if __name__ == "__main__":
    fig_layered_graph()
    fig_blocking_flow_push()
    fig_phase_growth()
    fig_unit_network_bound()
    print("Всі фігури успішно згенеровано.")
