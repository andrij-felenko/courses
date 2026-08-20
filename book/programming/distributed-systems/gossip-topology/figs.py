# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Топології пліток (повний граф, випадковий, ієрархічний)'."""

import sys
import os
import math

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_topology_comparison():
    """Фігура 1: Порівняння трьох топологій пліток — повний граф, випадковий оверлей та ієрархія."""
    w, h = 880, 390
    frags = []

    frags.append(text(w / 2, 28, "Порівняння топологій поширення пліток у розподілених системах", size=16, bold=True))

    # Панель 1: Повний граф (Full Mesh)
    frags.append(rect(20, 50, 265, 320, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(152, 75, "1. Повний граф (Full Mesh)", size=13, bold=True, color=INK))

    cx1, cy1 = 152, 175
    poly1 = []
    for k in range(6):
        ang = k * 2 * math.pi / 6 - math.pi / 2
        px = cx1 + 60 * math.cos(ang)
        py = cy1 + 60 * math.sin(ang)
        poly1.append((px, py))

    # Усі можливі зв'язки
    for i in range(6):
        for j in range(i + 1, 6):
            frags.append(line(poly1[i][0], poly1[i][1], poly1[j][0], poly1[j][1], color="#cbd5e1", sw=1, dash="2,2"))

    # Активні плітки
    active_mesh = [(0, 3), (1, 4), (2, 5)]
    for i, j in active_mesh:
        x1, y1 = poly1[i]
        x2, y2 = poly1[j]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        frags.append(arrow(x1 + ux * 16, y1 + uy * 16, x2 - ux * 16, y2 - uy * 16, color=POS, sw=1.5))

    for i, (px, py) in enumerate(poly1):
        frags.append(circle(px, py, 16, fill="#fdecea", stroke=POS, sw=1.5))
        frags.append(text(px, py + 4, "N%d" % (i + 1), size=10, bold=True, color=POS))

    frags.append(rect(32, 268, 241, 90, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(152, 288, "Огляд: Повний перелік O(N)", size=11, bold=True, color=POS))
    frags.append(text(152, 305, "Швидкість: O(log N) раундів", size=10, color=INK))
    frags.append(text(152, 321, "Пам'ять вузла: O(N) записів", size=10, color=MUTED))
    frags.append(text(152, 337, "Масштаб: до 2 000 серверів", size=10, color=MUTED))

    # Панель 2: Випадковий граф-експандер (Random Expander)
    frags.append(rect(305, 50, 265, 320, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(437, 75, "2. Випадковий оверлей (Expander)", size=13, bold=True, color=INK))

    cx2, cy2 = 437, 175
    poly2 = []
    for k in range(6):
        ang = k * 2 * math.pi / 6 - math.pi / 2
        px = cx2 + 60 * math.cos(ang)
        py = cy2 + 60 * math.sin(ang)
        poly2.append((px, py))

    # Тільки локальні випадкові ребра (d-регулярний оверлей)
    exp_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 3), (1, 4)]
    for i, j in exp_edges:
        frags.append(line(poly2[i][0], poly2[i][1], poly2[j][0], poly2[j][1], color="#93c5fd", sw=1.5))

    active_exp = [(0, 1), (2, 3), (4, 5)]
    for i, j in active_exp:
        x1, y1 = poly2[i]
        x2, y2 = poly2[j]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        frags.append(arrow(x1 + ux * 16, y1 + uy * 16, x2 - ux * 16, y2 - uy * 16, color=NEG, sw=1.5))

    for i, (px, py) in enumerate(poly2):
        frags.append(circle(px, py, 16, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(px, py + 4, "N%d" % (i + 1), size=10, bold=True, color=NEG))

    frags.append(rect(317, 268, 241, 90, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(437, 288, "Огляд: Частковий view O(log N)", size=11, bold=True, color=NEG))
    frags.append(text(437, 305, "Швидкість: O(log N) раундів", size=10, color=INK))
    frags.append(text(437, 321, "Пам'ять вузла: O(1) фіксована", size=10, color=MUTED))
    frags.append(text(437, 337, "Масштаб: 100 000+ (P2P/SWIM)", size=10, color=MUTED))

    # Панель 3: Ієрархічна топологія (Hierarchical Multi-DC)
    frags.append(rect(590, 50, 270, 320, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(725, 75, "3. Ієрархічна топологія (Multi-DC)", size=13, bold=True, color=INK))

    # Кластер DC 1 (LAN)
    frags.append(rect(605, 105, 115, 145, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(662, 122, "DC 1 (LAN)", size=10, bold=True, color=FIELD))
    dc1_nodes = [(635, 155), (690, 155), (635, 215), (690, 215)]
    for i, (px, py) in enumerate(dc1_nodes):
        frags.append(circle(px, py, 14, fill="#ffffff", stroke=FIELD, sw=1.5))
        frags.append(text(px, py + 4, "A%d" % (i + 1), size=9, bold=True, color=FIELD))
    frags.append(line(635, 155, 690, 155, color=FIELD, sw=1.2))
    frags.append(line(635, 215, 690, 215, color=FIELD, sw=1.2))
    frags.append(line(635, 155, 635, 215, color=FIELD, sw=1.2))

    # Кластер DC 2 (LAN)
    frags.append(rect(735, 105, 115, 145, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(792, 122, "DC 2 (LAN)", size=10, bold=True, color=FIELD))
    dc2_nodes = [(765, 155), (820, 155), (765, 215), (820, 215)]
    for i, (px, py) in enumerate(dc2_nodes):
        frags.append(circle(px, py, 14, fill="#ffffff", stroke=FIELD, sw=1.5))
        frags.append(text(px, py + 4, "B%d" % (i + 1), size=9, bold=True, color=FIELD))
    frags.append(line(765, 155, 820, 155, color=FIELD, sw=1.2))
    frags.append(line(765, 215, 820, 215, color=FIELD, sw=1.2))
    frags.append(line(820, 155, 820, 215, color=FIELD, sw=1.2))

    # WAN-міст між DC
    frags.append(line(690, 155, 765, 155, color=POS, sw=2, dash="4,3"))
    frags.append(text(727, 148, "WAN", size=9, bold=True, color=POS))
    frags.append(text(727, 170, "p=0.05", size=9, color=MUTED))

    frags.append(rect(602, 268, 246, 90, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(725, 288, "Огляд: Багаторівневий (LAN/WAN)", size=11, bold=True, color=FIELD))
    frags.append(text(725, 305, "Економія: -90% трафіку WAN", size=10, color=INK))
    frags.append(text(725, 321, "Швидкість LAN: суб-мілісекунди", size=10, color=MUTED))
    frags.append(text(725, 337, "Застосування: Cassandra / Consul", size=10, color=MUTED))

    render(os.path.join(OUT, "topology-comparison.svg"), w, h, *frags)


def fig_hierarchical_dissemination_flow():
    """Фігура 2: Поширення оновлення в ієрархічній топології між стійками та регіонами."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Ієрархічне поширення стану: локальні пули та міжрегіональні мости", size=16, bold=True))

    # Регіон 1: US-East (Virginia)
    frags.append(rect(25, 55, 395, 345, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(222, 78, "РЕГІОН 1: DC-East (Затримка RTT &lt; 0.5 мс)", size=12, bold=True, color=INK))

    # Стійка Rack 1-A
    frags.append(rect(40, 95, 175, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(127, 115, "Стійка Rack 1-A (ToR)", size=11, bold=True, color=FIELD))

    frags.append(circle(80, 160, 20, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(80, 164, "Джерело", size=9, bold=True, color=POS))
    frags.append(text(80, 195, "Оновлення v2", size=9, color=POS))

    frags.append(circle(170, 160, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(170, 164, "N1", size=10, bold=True, color=FIELD))

    frags.append(circle(127, 230, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(127, 234, "N2", size=10, bold=True, color=FIELD))

    # Швидкий локальний gossip всередині стійки
    frags.append(arrow(100, 160, 154, 160, color=FIELD, sw=1.8))
    frags.append(text(127, 150, "p=0.90", size=9, bold=True, color=FIELD))
    frags.append(arrow(93, 176, 116, 216, color=FIELD, sw=1.8))

    # Стійка Rack 1-B
    frags.append(rect(230, 95, 175, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(317, 115, "Стійка Rack 1-B (ToR)", size=11, bold=True, color=FIELD))

    frags.append(circle(270, 160, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(270, 164, "N3", size=10, bold=True, color=FIELD))

    frags.append(circle(360, 160, 18, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(360, 164, "Міст 1", size=9, bold=True, color=NEG))

    frags.append(circle(317, 230, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(317, 234, "N4", size=10, bold=True, color=FIELD))

    # Міжстійковий зв'язок всередині ДЦ
    frags.append(arrow(186, 160, 254, 160, color=FIELD, sw=1.5))
    frags.append(text(220, 150, "p=0.40", size=9, color=FIELD))
    frags.append(arrow(286, 160, 342, 160, color=FIELD, sw=1.5))

    # Пояснення DC-East
    frags.append(rect(40, 285, 365, 100, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(222, 305, "Локальна конвергенція LAN", size=11, bold=True, color=FIELD))
    frags.append(text(222, 325, "• Внутрішньостійковий RTT: 0.05–0.1 мс (100 Gbps ToR)", size=10, color=INK))
    frags.append(text(222, 343, "• Висока ймовірність (p=0.9) насичує 99% вузлів за 3–4 раунди", size=10, color=MUTED))
    frags.append(text(222, 361, "• Безкоштовний необмежений локальний трафік", size=10, color=MUTED))

    # Регіон 2: EU-West (Frankfurt)
    frags.append(rect(460, 55, 395, 345, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(657, 78, "РЕГІОН 2: DC-West (Затримка RTT &lt; 0.5 мс)", size=12, bold=True, color=INK))

    # Стійка Rack 2-A
    frags.append(rect(475, 95, 175, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(562, 115, "Стійка Rack 2-A (ToR)", size=11, bold=True, color=FIELD))

    frags.append(circle(520, 160, 18, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(520, 164, "Міст 2", size=9, bold=True, color=NEG))

    frags.append(circle(610, 160, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(610, 164, "N5", size=10, bold=True, color=FIELD))

    frags.append(circle(562, 230, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(562, 234, "N6", size=10, bold=True, color=FIELD))

    frags.append(arrow(538, 160, 594, 160, color=FIELD, sw=1.8))
    frags.append(arrow(532, 174, 550, 216, color=FIELD, sw=1.8))

    # Стійка Rack 2-B
    frags.append(rect(665, 95, 175, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(752, 115, "Стійка Rack 2-B (ToR)", size=11, bold=True, color=FIELD))

    frags.append(circle(710, 160, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(710, 164, "N7", size=10, bold=True, color=FIELD))

    frags.append(circle(800, 160, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(800, 164, "N8", size=10, bold=True, color=FIELD))

    frags.append(circle(752, 230, 16, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(752, 234, "N9", size=10, bold=True, color=FIELD))

    frags.append(arrow(626, 160, 694, 160, color=FIELD, sw=1.5))
    frags.append(arrow(726, 160, 784, 160, color=FIELD, sw=1.8))

    # Пояснення DC-West
    frags.append(rect(475, 285, 365, 100, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(657, 305, "Трансатлантичний WAN-тунель", size=11, bold=True, color=POS))
    frags.append(text(657, 325, "• Міжрегіональний RTT: 75–110 мс (платний транзитний трафік)", size=10, color=INK))
    frags.append(text(657, 343, "• Дроселювання пліток (p=0.05) через делегати / мости", size=10, color=MUTED))
    frags.append(text(657, 361, "• Захист оптоволоконних каналів від широкомовних штормів", size=10, color=MUTED))

    # Міжрегіональний міст між Міст 1 і Міст 2
    frags.append(arrow(378, 160, 502, 160, color=POS, sw=2.2))
    frags.append(rect(415, 135, 50, 24, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    frags.append(text(440, 151, "WAN", size=9, bold=True, color=POS))

    render(os.path.join(OUT, "hierarchical-dissemination-flow.svg"), w, h, *frags)


def fig_spectral_expander_mixing():
    """Фігура 3: Властивості графа-експандера та спектральний розрив у випадкових плітках."""
    w, h = 880, 380
    frags = []

    frags.append(text(w / 2, 28, "Спектральне розширення та межа Чеєгера у випадкових плітках", size=16, bold=True))

    # Ліва панель: Bipartition cut (S проти V \ S)
    frags.append(rect(25, 55, 400, 305, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 80, "Розріз графа та константа Чеєгера h(G)", size=13, bold=True, color=INK))

    # Підмножина S (інфіковані вузли)
    frags.append(rect(45, 105, 165, 165, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(127, 125, "Підмножина S (Інфіковані)", size=10, bold=True, color=POS))
    s_nodes = [(80, 165), (150, 155), (105, 220), (160, 220)]
    for i, (px, py) in enumerate(s_nodes):
        frags.append(circle(px, py, 14, fill="#ffffff", stroke=POS, sw=1.5))
        frags.append(text(px, py + 4, "S%d" % (i + 1), size=9, bold=True, color=POS))
    frags.append(line(80, 165, 150, 155, color=POS, sw=1.2))
    frags.append(line(80, 165, 105, 220, color=POS, sw=1.2))
    frags.append(line(150, 155, 160, 220, color=POS, sw=1.2))

    # Підмножина V \ S (неінфіковані вузли)
    frags.append(rect(240, 105, 165, 165, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(322, 125, "Підмножина V \\ S (Сприйнятливі)", size=10, bold=True, color=NEG))
    v_nodes = [(270, 165), (340, 155), (295, 220), (360, 220)]
    for i, (px, py) in enumerate(v_nodes):
        frags.append(circle(px, py, 14, fill="#ffffff", stroke=NEG, sw=1.5))
        frags.append(text(px, py + 4, "U%d" % (i + 1), size=9, bold=True, color=NEG))
    frags.append(line(270, 165, 340, 155, color=NEG, sw=1.2))
    frags.append(line(270, 165, 295, 220, color=NEG, sw=1.2))
    frags.append(line(340, 155, 360, 220, color=NEG, sw=1.2))

    # Ребра розрізу e(S, V \ S)
    frags.append(arrow(150, 155, 270, 165, color=FIELD, sw=2))
    frags.append(arrow(160, 220, 295, 220, color=FIELD, sw=2))
    frags.append(arrow(150, 155, 295, 220, color=FIELD, sw=1.5))

    frags.append(rect(45, 280, 360, 65, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(225, 298, "Розширюваність межі: e(S, V \\ S) &ge; h(G) · |S|", size=10, bold=True, color=FIELD))
    frags.append(text(225, 316, "Спектральний розрив гарантує швидкий вихід пліток", size=9, color=MUTED))
    frags.append(text(225, 330, "із будь-якого локального кластера за O(log N) кроків", size=9, color=MUTED))

    # Права панель: Спектральний аналіз матриці переходу (Eigenvalues)
    frags.append(rect(455, 55, 400, 305, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 80, "Спектр матриці переходу оверлею", size=13, bold=True, color=INK))

    # Вісь власних значень від -1 до +1
    frags.append(line(490, 170, 820, 170, color=LINE, sw=2))
    frags.append(line(490, 160, 490, 180, color=LINE, sw=1.5))
    frags.append(line(655, 163, 655, 177, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(820, 160, 820, 180, color=LINE, sw=1.5))

    frags.append(text(490, 195, "-1", size=11, bold=True, color=INK))
    frags.append(text(655, 195, "0", size=11, color=MUTED))
    frags.append(text(820, 195, "&lambda;₁ = 1", size=11, bold=True, color=POS))

    # Власне значення lambda_2
    l2_x = 740
    frags.append(circle(l2_x, 170, 6, fill=NEG, stroke=NEG, sw=1.5))
    frags.append(text(l2_x, 150, "&lambda;₂ (друге число)", size=10, bold=True, color=NEG))
    frags.append(text(l2_x, 195, "&lambda;₂ &le; 2&radic;(d-1)/d", size=9, color=NEG))

    # Спектральний розрив gamma
    frags.append(line(l2_x, 130, 820, 130, color=FIELD, sw=2))
    frags.append(line(l2_x, 125, l2_x, 135, color=FIELD, sw=1.5))
    frags.append(line(820, 125, 820, 135, color=FIELD, sw=1.5))
    frags.append(text((l2_x + 820) / 2, 120, "Спектральний розрив &gamma; = 1 - &lambda;₂", size=10, bold=True, color=FIELD))

    frags.append(rect(475, 230, 360, 115, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(655, 250, "Зв'язок спектра з часом змішування (Mixing Time)", size=10, bold=True, color=INK))
    frags.append(text(655, 270, "• Нерівність Алона-Мілмана: &gamma;/2 &le; h(G) &le; &radic;(2&gamma;)", size=9, color=FIELD))
    frags.append(text(655, 290, "• Час збіжності: T_mix = O( (1 / &gamma;) · log N )", size=9, color=POS))
    frags.append(text(655, 310, "• Для графа Рамануджана &gamma; &ge; 1 - 2/&radic;d (ідеальний експандер)", size=9, color=MUTED))
    frags.append(text(655, 330, "• Забезпечує стійкість до відмов 50% випадкових вузлів", size=9, color=MUTED))

    render(os.path.join(OUT, "spectral-expander-mixing.svg"), w, h, *frags)


def fig_wan_tradeoff():
    """Фігура 4: Крива компромісу між затримкою збіжності та навантаженням на канали WAN."""
    w, h = 880, 390
    frags = []

    frags.append(text(w / 2, 28, "Компроміс між затримкою поширення та навантаженням на WAN", size=16, bold=True))

    # Вісь X та Y
    ox, oy = 110, 310
    gw, gh = 640, 230

    # Сітка та осі
    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=6))

    # Оптимальна інженерна зона (p_remote між 0.05 та 0.20)
    frags.append(rect(ox + int(gw * 0.05), oy - gh + 5, int(gw * 0.18), gh - 10, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(ox + int(gw * 0.14), oy - gh + 30, "Оптимальна зона", size=11, bold=True, color=FIELD))
    frags.append(text(ox + int(gw * 0.14), oy - gh + 48, "p_remote &isin; [0.05, 0.20]", size=9, color=FIELD))

    # Крива 1: Затримка повної збіжності T_conv (червона, спадає)
    pts_lat = []
    for step in range(50):
        t = step / 49.0
        px = ox + t * gw
        val = 0.15 + 0.80 / (1.0 + 20.0 * t)
        py = oy - val * gh
        pts_lat.append((px, py))

    for i in range(len(pts_lat) - 1):
        frags.append(line(pts_lat[i][0], pts_lat[i][1], pts_lat[i+1][0], pts_lat[i+1][1], color=POS, sw=2.5))

    # Крива 2: WAN Egress трафік (синя, зростає лінійно)
    pts_traf = []
    for step in range(50):
        t = step / 49.0
        px = ox + t * gw
        val = 0.05 + 0.90 * t
        py = oy - val * gh
        pts_traf.append((px, py))

    for i in range(len(pts_traf) - 1):
        frags.append(line(pts_traf[i][0], pts_traf[i][1], pts_traf[i+1][0], pts_traf[i+1][1], color=NEG, sw=2.5))

    # Підписи осей
    frags.append(text(ox + gw / 2, oy + 35, "Ймовірність вибору віддаленого вузла p_remote (0.0 &rarr; 1.0)", size=12, bold=True, color=INK))

    # Ліва вісь: Затримка збіжності
    frags.append(text(ox - 15, oy - gh / 2, "Затримка P99 (с)", size=11, bold=True, color=POS, anchor="end"))
    frags.append(text(ox - 15, oy - gh + 20, "60 с", size=10, color=POS, anchor="end"))
    frags.append(text(ox - 15, oy - 10, "5 с", size=10, color=POS, anchor="end"))

    # Права вісь: Трафік WAN
    frags.append(text(ox + gw + 15, oy - gh / 2, "WAN Трафік (МБ/с)", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(text(ox + gw + 15, oy - gh + 20, "250 МБ/с", size=10, color=NEG, anchor="start"))
    frags.append(text(ox + gw + 15, oy - 10, "5 МБ/с", size=10, color=NEG, anchor="start"))

    # Позначки на графіку
    frags.append(circle(ox + int(gw * 0.01), pts_lat[0][1], 5, fill=POS, stroke=POS, sw=1.5))
    frags.append(text(ox + 50, pts_lat[0][1] - 12, "Штраф затримки", size=9, bold=True, color=POS))

    frags.append(circle(ox + gw, pts_traf[-1][1], 5, fill=NEG, stroke=NEG, sw=1.5))
    frags.append(text(ox + gw - 45, pts_traf[-1][1] - 12, "Перевантаження WAN", size=9, bold=True, color=NEG))

    # Легенда внизу
    frags.append(line(ox + 40, oy + 55, ox + 80, oy + 55, color=POS, sw=2.5))
    frags.append(text(ox + 90, oy + 59, "Затримка збіжності T_conv", size=10, color=POS, anchor="start"))

    frags.append(line(ox + 300, oy + 55, ox + 340, oy + 55, color=NEG, sw=2.5))
    frags.append(text(ox + 350, oy + 59, "Трафік між дата-центрами (WAN Egress)", size=10, color=NEG, anchor="start"))

    frags.append(rect(ox + 570, oy + 48, 16, 14, fill="#dcfce7", stroke=FIELD, sw=1))
    frags.append(text(ox + 595, oy + 59, "Економічний баланс", size=10, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "wan-bandwidth-latency-tradeoff.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_topology_comparison()
    fig_hierarchical_dissemination_flow()
    fig_spectral_expander_mixing()
    fig_wan_tradeoff()
    print("Всі SVG-фігури згенеровано успішно.")
