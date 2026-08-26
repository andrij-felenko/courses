# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. topologies-overview: Порівняння чотирьох топологій ────────────────────
def fig_topologies_overview():
    W, H = 940, 480
    p = []

    cards = [
        ("Зірка (Star)", "LoRaWAN, BLE, Wi-Fi", 40, 40, 200, 410, "#eef4fb", NEG),
        ("Кластерне дерево", "Zigbee Tree, WirelessHART", 260, 40, 200, 410, "#eef8f2", FIELD),
        ("Чарунка (Mesh)", "Thread, BLE Mesh, ESP-MESH", 480, 40, 200, 410, "#fdf6ec", "#d97706"),
        ("Однорангова (P2P)", "ESP-NOW, Wi-Fi Direct", 700, 40, 200, 410, "#fbf0f4", POS),
    ]

    for title, sub, x, y, w, h, fill, stroke in cards:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + w / 2, y + 26, title, size=13, color=stroke, bold=True))
        p.append(text(x + w / 2, y + 44, sub, size=10, color=MUTED))

    # --- 1. Star ---
    cx1, cy1 = 140, 160
    # Center Hub
    p.append(circle(cx1, cy1, 18, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(cx1, cy1 + 4, "Хаб", size=10, color=NEG, bold=True))
    # Nodes
    star_nodes = [
        (cx1 - 55, cy1 - 45, "Д1"),
        (cx1 + 55, cy1 - 45, "Д2"),
        (cx1 - 60, cy1 + 35, "Д3"),
        (cx1 + 60, cy1 + 35, "Д4"),
        (cx1, cy1 + 65, "Д5")
    ]
    for nx, ny, lbl in star_nodes:
        p.append(line(cx1, cy1, nx, ny, color=NEG, sw=1.5))
        p.append(circle(nx, ny, 12, fill="#ffffff", stroke=LINE, sw=1.5))
        p.append(text(nx, ny + 3.5, lbl, size=9.5, color=INK, bold=True))
    
    # Star annotations
    p.append(rect(52, 280, 176, 155, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
    p.append(text(140, 302, "Особливості Зірки:", size=10.5, color=INK, bold=True))
    p.append(text(60, 324, "• Прямий лінк (1 хоп)", size=9.5, color=INK, anchor="start"))
    p.append(text(60, 344, "• Давачі сплять 99.9%", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(60, 364, "• Маршрутизація = 0", size=9.5, color=INK, anchor="start"))
    p.append(text(60, 384, "• Слабке місце: Хаб", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(60, 404, "  (єдина точка відмови)", size=9.5, color=MUTED, anchor="start"))

    # --- 2. Tree ---
    cx2, cy2 = 360, 100
    # Root
    p.append(circle(cx2, cy2, 16, fill="#ffffff", stroke=FIELD, sw=2))
    p.append(text(cx2, cy2 + 4, "Корінь", size=9.5, color=FIELD, bold=True))
    # Routers (level 1)
    r1x, r1y = cx2 - 50, cy2 + 55
    r2x, r2y = cx2 + 50, cy2 + 55
    p.append(line(cx2, cy2, r1x, r1y, color=FIELD, sw=1.5))
    p.append(line(cx2, cy2, r2x, r2y, color=FIELD, sw=1.5))
    p.append(circle(r1x, r1y, 14, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(r1x, r1y + 3.5, "Р1", size=9.5, color=FIELD, bold=True))
    p.append(circle(r2x, r2y, 14, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(r2x, r2y + 3.5, "Р2", size=9.5, color=FIELD, bold=True))
    # End devices (level 2)
    tree_leaves = [
        (r1x - 30, r1y + 55, r1x, r1y, "Д1"),
        (r1x + 25, r1y + 55, r1x, r1y, "Д2"),
        (r2x - 25, r2y + 55, r2x, r2y, "Д3"),
        (r2x + 30, r2y + 55, r2x, r2y, "Д4")
    ]
    for lx, ly, px, py, lbl in tree_leaves:
        p.append(line(px, py, lx, ly, color=FIELD, sw=1.3))
        p.append(circle(lx, ly, 11, fill="#ffffff", stroke=LINE, sw=1.3))
        p.append(text(lx, ly + 3.5, lbl, size=9.5, color=INK, bold=True))

    # Tree annotations
    p.append(rect(272, 280, 176, 155, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
    p.append(text(360, 302, "Особливості Дерева:", size=10.5, color=INK, bold=True))
    p.append(text(280, 324, "• Ієрархічні адреси", size=9.5, color=INK, anchor="start"))
    p.append(text(280, 344, "• Розширення радіуса", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(280, 364, "• Роутери не сплять", size=9.5, color=MUTED, anchor="start"))
    p.append(text(280, 384, "• Обрив гілки ізолює", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(280, 404, "  усіх її нащадків", size=9.5, color=MUTED, anchor="start"))

    # --- 3. Mesh ---
    cx3, cy3 = 580, 160
    mesh_routers = [
        (cx3 - 45, cy3 - 40, "Р1"),
        (cx3 + 45, cy3 - 40, "Р2"),
        (cx3 - 45, cy3 + 35, "Р3"),
        (cx3 + 45, cy3 + 35, "Р4"),
    ]
    # Mesh interconnects
    for i in range(len(mesh_routers)):
        for j in range(i + 1, len(mesh_routers)):
            p.append(line(mesh_routers[i][0], mesh_routers[i][1],
                          mesh_routers[j][0], mesh_routers[j][1],
                          color="#d97706", sw=1.4))
    # Routers
    for rx, ry, lbl in mesh_routers:
        p.append(circle(rx, ry, 14, fill="#ffffff", stroke="#d97706", sw=2))
        p.append(text(rx, ry + 3.5, lbl, size=9.5, color="#d97706", bold=True))
    # Mesh leaves
    p.append(line(cx3 - 45, cy3 - 40, cx3 - 75, cy3 - 65, color="#d97706", sw=1.2))
    p.append(circle(cx3 - 75, cy3 - 65, 11, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(cx3 - 75, cy3 - 62, "Д1", size=9, color=INK, bold=True))

    p.append(line(cx3 + 45, cy3 + 35, cx3 + 75, cy3 + 60, color="#d97706", sw=1.2))
    p.append(circle(cx3 + 75, cy3 + 60, 11, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(cx3 + 75, cy3 + 63, "Д2", size=9, color=INK, bold=True))

    # Mesh annotations
    p.append(rect(492, 280, 176, 155, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
    p.append(text(580, 302, "Особливості Чарунки:", size=10.5, color=INK, bold=True))
    p.append(text(500, 324, "• Самовідновлення", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(500, 344, "• Багато шляхів обходу", size=9.5, color=INK, anchor="start"))
    p.append(text(500, 364, "• Складний стек (RAM)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(500, 384, "• Роутери під струмом", size=9.5, color=MUTED, anchor="start"))
    p.append(text(500, 404, "• Накладні байти в кадрах", size=9.5, color=MUTED, anchor="start"))

    # --- 4. P2P ---
    cx4, cy4 = 800, 160
    # Group 1
    p.append(line(cx4 - 45, cy4 - 35, cx4 + 45, cy4 - 35, color=POS, sw=1.8, dash="4,3"))
    p.append(circle(cx4 - 45, cy4 - 35, 14, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(cx4 - 45, cy4 - 31.5, "В1", size=9.5, color=POS, bold=True))
    p.append(circle(cx4 + 45, cy4 - 35, 14, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(cx4 + 45, cy4 - 31.5, "В2", size=9.5, color=POS, bold=True))
    p.append(text(cx4, cy4 - 42, "direct link", size=9.5, color=MUTED))

    # Group 2
    p.append(line(cx4 - 45, cy4 + 40, cx4 + 45, cy4 + 40, color=POS, sw=1.8, dash="4,3"))
    p.append(circle(cx4 - 45, cy4 + 40, 14, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(cx4 - 45, cy4 + 43.5, "В3", size=9.5, color=POS, bold=True))
    p.append(circle(cx4 + 45, cy4 + 40, 14, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(cx4 + 45, cy4 + 43.5, "В4", size=9.5, color=POS, bold=True))
    p.append(text(cx4, cy4 + 31, "direct link", size=9.5, color=MUTED))

    # P2P annotations
    p.append(rect(712, 280, 176, 155, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
    p.append(text(800, 302, "Особливості P2P:", size=10.5, color=INK, bold=True))
    p.append(text(720, 324, "• Без координатора", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(720, 344, "• Затримка < 2–5 мс", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(720, 364, "• Тільки 1 прямий хоп", size=9.5, color=INK, anchor="start"))
    p.append(text(720, 384, "• Обмежена к-ть пар", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(720, 404, "  (до 20 пірів у MAC)", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "topologies-overview.svg"), W, H, *p,
           title="Чотири фундаментальні топології бездротових зв'язаних систем")


# ── 2. star-spof-bottleneck: Механізми та вразливості Зірки ─────────────────
def fig_star_spof_bottleneck():
    W, H = 920, 420
    p = []

    # Left panel: SPOF
    p.append(rect(30, 40, 410, 350, fill="#fdf2f2", stroke=POS, sw=1.6, rx=8))
    p.append(text(235, 68, "1. Єдина точка відмови (SPOF)", size=13, color=POS, bold=True))
    
    # Hub dead
    p.append(circle(235, 170, 24, fill="#fee2e2", stroke=POS, sw=2.2))
    p.append(text(235, 166, "ХАБ", size=11, color=POS, bold=True))
    p.append(text(235, 180, "DEAD", size=9.5, color=POS, bold=True))
    p.append(line(215, 150, 255, 190, color=POS, sw=2.5))
    p.append(line(215, 190, 255, 150, color=POS, sw=2.5))

    spof_nodes = [
        (100, 110, "Давач 1"),
        (370, 110, "Давач 2"),
        (100, 240, "Давач 3"),
        (370, 240, "Давач 4"),
    ]
    for nx, ny, lbl in spof_nodes:
        p.append(line(nx, ny, 235, 170, color="#f87171", sw=1.5, dash="4,4"))
        p.append(circle(nx, ny, 16, fill="#ffffff", stroke=LINE, sw=1.5))
        p.append(text(nx, ny + 4, lbl, size=9.5, color=INK, bold=True))
        p.append(text(nx, ny + 28, "Ізольовано!", size=9.5, color=POS, bold=True))

    p.append(rect(50, 295, 370, 80, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    p.append(text(235, 318, "Наслідок падіння центрального концентратора:", size=10, color=POS, bold=True))
    p.append(text(235, 338, "100% периферійних вузлів втрачають зв'язок,", size=9.5, color=INK))
    p.append(text(235, 356, "навіть якщо вони розташовані впритул один до одного.", size=9.5, color=INK))

    # Right panel: Hidden Node Problem & Bottleneck
    p.append(rect(480, 40, 410, 350, fill="#eef6fc", stroke=NEG, sw=1.6, rx=8))
    p.append(text(685, 68, "2. Проблема прихованого вузла на хабі", size=13, color=NEG, bold=True))

    # Hub in center
    p.append(circle(685, 170, 22, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(685, 174, "Хаб", size=11, color=NEG, bold=True))

    # Node A (left)
    p.append(circle(550, 170, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(550, 174, "Вузол A", size=9.5, color=INK, bold=True))
    # Node B (right)
    p.append(circle(820, 170, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(820, 174, "Вузол B", size=9.5, color=INK, bold=True))

    # Transmissions to Hub
    p.append(arrow(570, 170, 655, 170, color=FIELD, sw=2))
    p.append(text(612, 160, "TX кадру", size=9.5, color=FIELD, bold=True))
    p.append(arrow(800, 170, 715, 170, color=FIELD, sw=2))
    p.append(text(758, 160, "TX кадру", size=9.5, color=FIELD, bold=True))

    # Collision starburst at Hub
    p.append('<circle cx="685.0" cy="170.0" r="30.0" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % POS)
    p.append(text(685, 130, "КОЛІЗІЯ В ЕФІРІ!", size=10, color=POS, bold=True))

    # Barrier / distance between A and B
    p.append(line(550, 210, 820, 210, color=MUTED, sw=1, dash="3,3"))
    p.append(line(685, 205, 685, 215, color=MUTED, sw=1))
    p.append(text(685, 228, "Вузол A не чує передачу Вузла B (поза зоною досяжності)", size=9.5, color=MUTED))

    p.append(rect(500, 295, 370, 80, fill="#ffffff", stroke="#bfdbfe", sw=1, rx=6))
    p.append(text(685, 318, "Колізійне пляшкове горло шлюзу:", size=10, color=NEG, bold=True))
    p.append(text(685, 338, "CSMA/CA не захищає від одночасної передачі.", size=9.5, color=INK))
    p.append(text(685, 356, "При зростанні кількості вузлів корисна смуга стрімко деградує.", size=9.5, color=INK))

    render(os.path.join(OUT, "star-spof-bottleneck.svg"), W, H, *p,
           title="Архітектурні межі Зірки: єдина точка відмови та колізійний бар'єр")


# ── 3. cluster-tree-routing: Маршрутизація Cskip та обрив піддерева ───────────
def fig_cluster_tree_routing():
    W, H = 940, 450
    p = []

    # Root
    p.append(rect(400, 45, 140, 44, fill="#e8f5e9", stroke=FIELD, sw=2, rx=6))
    p.append(text(470, 64, "Корінь (0x0000)", size=11, color=FIELD, bold=True))
    p.append(text(470, 80, "Діапазон: [0x0001 .. 0xFFFF]", size=9.5, color=MUTED))

    # Level 1 Routers
    # Router 1
    p.append(line(430, 89, 230, 145, color=FIELD, sw=1.8))
    p.append(rect(150, 145, 160, 48, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(230, 165, "Роутер R1 (0x0001)", size=10.5, color=FIELD, bold=True))
    p.append(text(230, 182, "Піддерево: [0x0002 .. 0x2A00]", size=9.5, color=MUTED))

    # Router 2
    p.append(line(510, 89, 710, 145, color=FIELD, sw=1.8))
    p.append(rect(630, 145, 160, 48, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(710, 165, "Роутер R2 (0x2A01)", size=10.5, color=FIELD, bold=True))
    p.append(text(710, 182, "Піддерево: [0x2A02 .. 0x5400]", size=9.5, color=MUTED))

    # Level 2 Children of R1
    # Leaf D1
    p.append(line(190, 193, 120, 255, color=FIELD, sw=1.4))
    p.append(circle(120, 265, 16, fill="#ffffff", stroke=LINE, sw=1.4))
    p.append(text(120, 268, "0x0002", size=9.5, color=INK, bold=True))
    p.append(text(120, 294, "Давач D1", size=9.5, color=MUTED))

    # Leaf D2
    p.append(line(270, 193, 270, 255, color=FIELD, sw=1.4))
    p.append(circle(270, 265, 16, fill="#ffffff", stroke=LINE, sw=1.4))
    p.append(text(270, 268, "0x0003", size=9.5, color=INK, bold=True))
    p.append(text(270, 294, "Давач D2", size=9.5, color=MUTED))

    # Level 2 Children of R2
    # Leaf D3
    p.append(line(670, 193, 670, 255, color=FIELD, sw=1.4))
    p.append(circle(670, 265, 16, fill="#ffffff", stroke=LINE, sw=1.4))
    p.append(text(670, 268, "0x2A02", size=9.5, color=INK, bold=True))
    p.append(text(670, 294, "Давач D3", size=9.5, color=MUTED))

    # Leaf D4
    p.append(line(750, 193, 820, 255, color=FIELD, sw=1.4))
    p.append(circle(820, 265, 16, fill="#ffffff", stroke=LINE, sw=1.4))
    p.append(text(820, 268, "0x2A03", size=9.5, color=INK, bold=True))
    p.append(text(820, 294, "Давач D4", size=9.5, color=MUTED))

    # Packet Path: D1 -> D4 (Tree Stretch)
    p.append(arrow(135, 255, 210, 193, color=POS, sw=2))
    p.append(arrow(240, 145, 420, 89, color=POS, sw=2))
    p.append(arrow(520, 89, 690, 145, color=POS, sw=2))
    p.append(arrow(725, 193, 810, 252, color=POS, sw=2))

    p.append(rect(320, 155, 300, 75, fill="#fdf0ed", stroke=POS, sw=1.4, rx=6))
    p.append(text(470, 175, "Траєкторія Tree Routing Stretch (4 хопи):", size=10, color=POS, bold=True))
    p.append(text(470, 193, "D1 → R1 → Корінь → R2 → D4", size=10, color=POS, bold=True))
    p.append(text(470, 212, "Маршрут через спільного предка (навіть якщо D2 і D3 поруч)", size=9, color=MUTED))

    # Explanatory bottom cards
    # Left: Zero-RAM routing logic
    p.append(rect(40, 325, 410, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(245, 347, "Арифметична маршрутизація Cskip (Без таблиць):", size=10, color=FIELD, bold=True))
    p.append(text(55, 368, "• Якщо Target ∈ [Child_Min .. Child_Max] → шлемо ВНИЗ дитині", size=9.5, color=INK, anchor="start"))
    p.append(text(55, 388, "• Якщо Target ∉ моєму піддереву → шлемо ВГОРУ батькові", size=9.5, color=INK, anchor="start"))
    p.append(text(55, 408, "• Ціна в пам'яті: O(1) RAM — обчислення формулою на льоту", size=9.5, color=FIELD, anchor="start", bold=True))

    # Right: Tree failure mode
    p.append(rect(490, 325, 410, 105, fill="#fdf2f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(695, 347, "Вразливість деревоподібної структури:", size=10, color=POS, bold=True))
    p.append(text(505, 368, "• Падіння роутера R1 миттєво відрізає D1 та D2 від мережі", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(505, 388, "• Нащадки переходять у стан Orphan (сирота) і шукають батька", size=9.5, color=INK, anchor="start"))
    p.append(text(505, 408, "• Re-association займає сотні мілісекунд або секунди", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "cluster-tree-routing.svg"), W, H, *p,
           title="Кластерне дерево: префіксна маршрутизація та проблема неоптимального шляху")


# ── 4. mesh-rpl-dodag: Граф DODAG у RPL та локальне самовідновлення ──────────
def fig_mesh_rpl_dodag():
    W, H = 940, 450
    p = []

    # DAG Root
    p.append(circle(470, 65, 24, fill="#e8f5e9", stroke=FIELD, sw=2.2))
    p.append(text(470, 62, "DODAG", size=10, color=FIELD, bold=True))
    p.append(text(470, 75, "Root", size=9.5, color=FIELD, bold=True))
    p.append(text(470, 24, "Ранг 1.0 (Корінь)", size=10, color=FIELD, bold=True))

    # Rank 2 Routers
    # R1
    r1x, r1y = 280, 170
    p.append(circle(r1x, r1y, 20, fill="#ffffff", stroke="#d97706", sw=2))
    p.append(text(r1x, r1y + 4, "R1", size=10.5, color="#d97706", bold=True))
    p.append(text(r1x - 55, r1y + 4, "Ранг 2.0", size=9.5, color=MUTED))

    # R2
    r2x, r2y = 660, 170
    p.append(circle(r2x, r2y, 20, fill="#ffffff", stroke="#d97706", sw=2))
    p.append(text(r2x, r2y + 4, "R2", size=10.5, color="#d97706", bold=True))
    p.append(text(r2x + 55, r2y + 4, "Ранг 2.0", size=9.5, color=MUTED))

    # Upward primary links to Root
    p.append(arrow(r1x + 15, r1y - 15, 450, 80, color=FIELD, sw=2))
    p.append(arrow(r2x - 15, r1y - 15, 490, 80, color=FIELD, sw=2))

    # Horizontal mesh link between R1 and R2
    p.append(line(r1x + 22, r1y, r2x - 22, r2y, color="#d97706", sw=1.5, dash="4,3"))
    p.append(text(470, 160, "Sibling link (той самий ранг)", size=9.5, color=MUTED))

    # Rank 3 Router R3 (experiencing failover)
    r3x, r3y = 470, 275
    p.append(circle(r3x, r3y, 20, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(r3x, r3y + 4, "R3", size=10.5, color=NEG, bold=True))
    p.append(text(r3x + 55, r3y + 4, "Ранг 3.0", size=9.5, color=MUTED))

    # Broken link to Primary Parent R1
    p.append(line(r3x - 15, r3y - 15, r1x + 15, r1y + 15, color=POS, sw=2, dash="4,3"))
    # Cross on broken link
    bx, by = (r3x - 15 + r1x + 15) / 2, (r3y - 15 + r1y + 15) / 2
    p.append(circle(bx, by, 10, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(line(bx - 6, by - 6, bx + 6, by + 6, color=POS, sw=2))
    p.append(line(bx - 6, by + 6, bx + 6, by - 6, color=POS, sw=2))
    p.append(text(bx - 40, by - 14, "Обрив лінку!", size=9.5, color=POS, bold=True))

    # Dynamic Reroute / Alternate Parent to R2
    p.append(arrow(r3x + 15, r3y - 15, r2x - 15, r2y + 15, color=FIELD, sw=2.5))
    p.append(text(585, 235, "Резервний батько (Local Repair)", size=9.5, color=FIELD, bold=True))

    # End Leaf Sensor
    lx, ly = 470, 370
    p.append(circle(lx, ly, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(lx, ly + 3.5, "Давач", size=9.5, color=INK, bold=True))
    p.append(arrow(lx, ly - 16, r3x, r3y + 22, color=LINE, sw=1.5))

    # Left note: RPL DODAG rules
    p.append(rect(40, 240, 210, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(145, 260, "Правила RPL DODAG:", size=10, color=FIELD, bold=True))
    p.append(text(50, 282, "1. Ранг строго монотонний:", size=9.5, color=INK, anchor="start", bold=True))
    p.append(text(50, 298, "   Rank(Child) > Rank(Parent)", size=9, color=MUTED, anchor="start"))
    p.append(text(50, 318, "2. Захист від петель:", size=9.5, color=INK, anchor="start", bold=True))
    p.append(text(50, 334, "   Заборонено слати вузлу", size=9, color=MUTED, anchor="start"))
    p.append(text(50, 348, "   із вищим/рівним рангом", size=9, color=MUTED, anchor="start"))
    p.append(text(50, 368, "3. Метрика OF (ETX):", size=9.5, color=INK, anchor="start", bold=True))
    p.append(text(50, 384, "   Враховує якість зв'язку", size=9, color=MUTED, anchor="start"))

    # Right note: Self-healing mechanics
    p.append(rect(690, 240, 210, 175, fill="#fdf8f0", stroke="#fde68a", sw=1.2, rx=6))
    p.append(text(795, 260, "Механізм Самовідновлення:", size=10, color="#d97706", bold=True))
    p.append(text(700, 282, "• Відсутність MAC ACK →", size=9.5, color=INK, anchor="start"))
    p.append(text(700, 298, "  вузол R3 фіксує аварію лінку", size=9, color=MUTED, anchor="start"))
    p.append(text(700, 320, "• Миттєве перемикання на", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(700, 336, "  Alternative Parent R2", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(700, 358, "• Трафік іде без затримок,", size=9.5, color=INK, anchor="start"))
    p.append(text(700, 374, "  мережа не перебудовується", size=9, color=MUTED, anchor="start"))
    p.append(text(700, 388, "  повністю (Local Repair)", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "mesh-rpl-dodag.svg"), W, H, *p,
           title="Чарункова мережа RPL: дерево DODAG, розрахунок рангу та локальне самовідновлення")


# ── 5. topology-decision-tree: Інженерна матриця вибору топології ─────────────
def fig_topology_decision_tree():
    W, H = 940, 460
    p = []

    # Question 1: Infrastructure / P2P
    p.append(rect(340, 35, 260, 45, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6))
    p.append(text(470, 54, "Чи потрібен хаб/інтернет,", size=10.5, color=INK, bold=True))
    p.append(text(470, 70, "чи обмін суто автономний між парою?", size=9.5, color=MUTED))

    # P2P branch (Right)
    p.append(arrow(600, 57, 720, 57, color=POS, sw=1.8))
    p.append(text(660, 48, "Суто між парою", size=9.5, color=POS, bold=True))

    p.append(rect(720, 35, 180, 50, fill="#fdf2f4", stroke=POS, sw=2, rx=6))
    p.append(text(810, 56, "Однорангова (P2P)", size=11, color=POS, bold=True))
    p.append(text(810, 72, "ESP-NOW, Wi-Fi Direct", size=9.5, color=MUTED))

    # Down branch: Hub/System required
    p.append(arrow(470, 80, 470, 130, color=LINE, sw=1.8))
    p.append(text(480, 108, "Зв'язана система", size=9.5, color=FIELD, anchor="start", bold=True))

    # Question 2: Physical Span / Multi-hop
    p.append(rect(320, 130, 300, 45, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6))
    p.append(text(470, 149, "Чи покриває прямий радіолінк", size=10.5, color=INK, bold=True))
    p.append(text(470, 165, "усі вузли від одного хаба?", size=9.5, color=MUTED))

    # Star branch (Left)
    p.append(arrow(320, 152, 190, 152, color=NEG, sw=1.8))
    p.append(text(250, 142, "Так, 1 хоп (пряма видимість)", size=9.5, color=NEG, bold=True))

    p.append(rect(40, 130, 150, 95, fill="#eef4fb", stroke=NEG, sw=2, rx=6))
    p.append(text(115, 154, "Зірка (Star)", size=12, color=NEG, bold=True))
    p.append(text(115, 172, "LoRaWAN / BLE / Wi-Fi", size=9.5, color=MUTED))
    p.append(text(115, 194, "• Батарея на 5–10 років", size=9.5, color=FIELD, bold=True))
    p.append(text(115, 210, "• Проста прошивка", size=9.5, color=INK))

    # Multi-hop required (Down)
    p.append(arrow(470, 175, 470, 225, color=LINE, sw=1.8))
    p.append(text(480, 202, "Ні, потрібна естафета (Multi-hop)", size=9.5, color=POS, anchor="start", bold=True))

    # Question 3: Power & Reliability vs RAM
    p.append(rect(310, 225, 320, 50, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6))
    p.append(text(470, 245, "Чи є живлення 230 В на роутерах", size=10.5, color=INK, bold=True))
    p.append(text(470, 262, "і чи критичне самовідновлення?", size=9.5, color=MUTED))

    # Tree branch (Left-Down)
    p.append(arrow(350, 275, 230, 330, color=FIELD, sw=1.8))
    p.append(text(250, 300, "Фіксована ієрархія,\nмало RAM на МК", size=9.5, color=FIELD, bold=True))

    p.append(rect(100, 330, 230, 95, fill="#eef8f2", stroke=FIELD, sw=2, rx=6))
    p.append(text(215, 355, "Кластерне дерево", size=12, color=FIELD, bold=True))
    p.append(text(215, 373, "Zigbee Tree / WirelessHART", size=9.5, color=MUTED))
    p.append(text(215, 395, "• Детермінований розклад", size=9.5, color=INK))
    p.append(text(215, 411, "• Арифметика адрес без RAM", size=9.5, color=FIELD, bold=True))

    # Mesh branch (Right-Down)
    p.append(arrow(590, 275, 710, 330, color="#d97706", sw=1.8))
    p.append(text(680, 300, "Динамічне відновлення,\nє живлення роутерів", size=9.5, color="#d97706", bold=True))

    p.append(rect(610, 330, 230, 95, fill="#fdf6ec", stroke="#d97706", sw=2, rx=6))
    p.append(text(725, 355, "Чарунка (Mesh)", size=12, color="#d97706", bold=True))
    p.append(text(725, 373, "Thread / BLE Mesh / ESP-MESH", size=9.5, color=MUTED))
    p.append(text(725, 395, "• Надійність без SPOF", size=9.5, color=FIELD, bold=True))
    p.append(text(725, 411, "• Багатоальтернативні шляхи", size=9.5, color=INK))

    render(os.path.join(OUT, "topology-decision-tree.svg"), W, H, *p,
           title="Дерево рішень: вибір мережевої топології під інженерні вимоги системи")


if __name__ == "__main__":
    fig_topologies_overview()
    fig_star_spof_bottleneck()
    fig_cluster_tree_routing()
    fig_mesh_rpl_dodag()
    fig_topology_decision_tree()
    print("All 5 figures generated successfully.")
