# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Розповсюдження інформації через плітки (anti-entropy / rumor-mongering)'."""

import sys
import os
import math

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_rumor_vs_anti_entropy():
    """Фігура 1: Порівняння Rumor Mongering (плітки) та Anti-Entropy (анти-ентропія)."""
    w, h = 880, 390
    frags = []

    frags.append(text(w / 2, 28, "Порівняння двох парадигм епідемічного розповсюдження", size=16, bold=True))

    # Секція 1: Rumor Mongering (Hot broadcast)
    frags.append(rect(25, 52, 400, 318, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 78, "1. Rumor Mongering (Поширення чуток)", size=14, bold=True, color=INK))

    # Візуалізація: вузол-джерело інфікує сусідів
    cx, cy = 110, 155
    frags.append(circle(cx, cy, 24, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(cx, cy + 4, "Джерело", size=10, bold=True, color=POS))

    # 3 цільові вузли
    targets = [(230, 115), (230, 155), (230, 195)]
    for i, (tx, ty) in enumerate(targets):
        frags.append(circle(tx, ty, 18, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(tx, ty + 4, "N%d" % (i + 1), size=10, bold=True, color=NEG))
        frags.append(arrow(cx + 25, cy + (ty - cy) * 0.4, tx - 19, ty, color=POS, sw=1.5))

    # Подальша ретрансляція
    sub_targets = [(335, 100), (335, 135), (335, 175), (335, 210)]
    for j, (sx, sy) in enumerate(sub_targets):
        frags.append(circle(sx, sy, 14, fill="#f0fdf4", stroke=FIELD, sw=1.5))
        frags.append(text(sx, sy + 3, "N%d" % (j + 4), size=9, bold=True, color=FIELD))

    frags.append(arrow(248, 115, 321, 103, color=NEG, sw=1.2))
    frags.append(arrow(248, 115, 321, 133, color=NEG, sw=1.2))
    frags.append(arrow(248, 195, 321, 177, color=NEG, sw=1.2))
    frags.append(arrow(248, 195, 321, 207, color=NEG, sw=1.2))

    # Властивості
    frags.append(rect(40, 240, 370, 115, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(225, 260, "Властивості Rumor Mongering:", size=11, bold=True, color=INK))
    frags.append(text(225, 278, "• Затримка: O(log N) раундів (надшвидкий розліт)", size=10, color=MUTED))
    frags.append(text(225, 296, "• Трафік: O(k · N) невеликих UDP дейтаграм", size=10, color=MUTED))
    frags.append(text(225, 314, "• Зупинка: лічильник дублікатів k або монета 1/k", size=10, color=MUTED))
    frags.append(text(225, 332, "• Гарантія: імовірнісна (залишок неінфікованих ~ e^(-k))", size=10, color=POS))

    # Секція 2: Anti-Entropy (State reconciliation)
    frags.append(rect(455, 52, 400, 318, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 78, "2. Anti-Entropy (Фонова анти-ентропія)", size=14, bold=True, color=INK))

    # Візуалізація: попарне звіряння станів двох вузлів
    n1_x, n1_y = 540, 155
    n2_x, n2_y = 770, 155
    frags.append(circle(n1_x, n1_y, 28, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(n1_x, n1_y + 4, "Вузол A", size=11, bold=True, color=NEG))

    frags.append(circle(n2_x, n2_y, 28, fill="#f0fdf4", stroke=FIELD, sw=2))
    frags.append(text(n2_x, n2_y + 4, "Вузол B", size=11, bold=True, color=FIELD))

    # Стрілки обміну дайджестами
    frags.append(arrow(n1_x + 30, n1_y - 18, n2_x - 30, n2_y - 18, color=NEG, sw=1.6))
    frags.append(text((n1_x + n2_x) / 2, n1_y - 26, "1. Версійний дайджест A", size=10, bold=True, color=NEG))

    frags.append(arrow(n2_x - 30, n2_y + 18, n1_x + 30, n1_y + 18, color=FIELD, sw=1.6))
    frags.append(text((n1_x + n2_x) / 2, n1_y + 34, "2. Дельти розбіжностей B", size=10, bold=True, color=FIELD))

    # Властивості
    frags.append(rect(470, 240, 370, 115, fill="#ffffff", stroke="#94a3b8", sw=1, rx=6))
    frags.append(text(655, 260, "Властивості Anti-Entropy:", size=11, bold=True, color=INK))
    frags.append(text(655, 278, "• Затримка: фонова періодична (секунди / хвилини)", size=10, color=MUTED))
    frags.append(text(655, 296, "• Трафік: TCP / дайджести версій та відсутні дельти", size=10, color=MUTED))
    frags.append(text(655, 314, "• Механізм: Scuttlebutt, дерева Меркла або вектори", size=10, color=MUTED))
    frags.append(text(655, 332, "• Гарантія: 100% детермінована кінцева узгодженість", size=10, color=FIELD))

    render(os.path.join(OUT, "rumor-vs-anti-entropy.svg"), w, h, *frags)


def fig_push_pull_dynamics():
    """Фігура 2: Динаміка поширення інфекції — Push, Pull та Push-Pull."""
    w, h = 860, 370
    frags = []

    frags.append(text(w / 2, 28, "Динаміка епідемічного поширення: Push проти Pull та Push-Pull", size=16, bold=True))

    # Вісь координат графіка
    ox, oy = 80, 280
    gw, gh = 420, 210
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))

    # Стрілки на осях
    frags.append(arrow(ox + gw, oy, ox + gw + 15, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy - gh, ox, oy - gh - 15, color=LINE, sw=1.5))

    frags.append(text(ox + gw + 20, oy + 4, "Раунди t", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(ox - 10, oy - gh - 8, "% інфікованих вузлів", size=11, bold=True, color=INK, anchor="end"))

    # Позначки на осі Y (0%, 50%, 100%)
    frags.append(line(ox - 4, oy, ox, oy, color=LINE, sw=1))
    frags.append(text(ox - 8, oy + 4, "0%", size=10, color=MUTED, anchor="end"))

    frags.append(line(ox - 4, oy - gh / 2, ox, oy - gh / 2, color=LINE, sw=1))
    frags.append(line(ox, oy - gh / 2, ox + gw, oy - gh / 2, color="#e2e8f0", sw=1, dash="3,3"))
    frags.append(text(ox - 8, oy - gh / 2 + 4, "50%", size=10, color=MUTED, anchor="end"))

    frags.append(line(ox - 4, oy - gh, ox, oy - gh, color=LINE, sw=1))
    frags.append(line(ox, oy - gh, ox + gw, oy - gh, color="#e2e8f0", sw=1, dash="3,3"))
    frags.append(text(ox - 8, oy - gh + 4, "100%", size=10, color=MUTED, anchor="end"))

    # Крива 1: Push (швидкий старт, повільний хвіст)
    pts_push = []
    for step in range(21):
        x = ox + step * (gw / 20)
        t_norm = step / 20.0
        if t_norm < 0.4:
            val = (math.exp(t_norm * 5) - 1) / (math.exp(2.0) - 1) * 0.7
        else:
            val = 0.7 + 0.28 * (1 - math.exp(-(t_norm - 0.4) * 4))
        y = oy - min(val, 0.98) * gh
        pts_push.append((x, y))

    for i in range(len(pts_push) - 1):
        x1, y1 = pts_push[i]
        x2, y2 = pts_push[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Крива 2: Pull (повільний старт, надшвидкий хвіст)
    pts_pull = []
    for step in range(21):
        x = ox + step * (gw / 20)
        t_norm = step / 20.0
        if t_norm < 0.5:
            val = 0.25 * (t_norm / 0.5) ** 2
        else:
            val = 0.25 + 0.75 * (1 - (1 - (t_norm - 0.5) / 0.5) ** 3)
        y = oy - min(val, 1.0) * gh
        pts_pull.append((x, y))

    for i in range(len(pts_pull) - 1):
        x1, y1 = pts_pull[i]
        x2, y2 = pts_pull[i + 1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2.5, dash="4,2"))

    # Крива 3: Push-Pull (найкраще з двох)
    pts_pushpull = []
    for step in range(15):
        x = ox + step * (gw / 20)
        t_norm = step / 14.0
        val = 1.0 / (1.0 + math.exp(-8.0 * (t_norm - 0.4)))
        y = oy - val * gh
        pts_pushpull.append((x, y))

    for i in range(len(pts_pushpull) - 1):
        x1, y1 = pts_pushpull[i]
        x2, y2 = pts_pushpull[i + 1]
        frags.append(line(x1, y1, x2, y2, color=FIELD, sw=3))

    # Легенда та опис праворуч
    lx, ly = 540, 75
    frags.append(rect(lx, ly, 295, 235, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 147, ly + 25, "Порівняння швидкості фаз", size=13, bold=True, color=INK))

    # Push
    frags.append(line(lx + 20, ly + 58, lx + 50, ly + 58, color=POS, sw=2.5))
    frags.append(text(lx + 60, ly + 62, "Стратегія Push", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(lx + 20, ly + 80, "Старт: (1+k)^t (експоненційний)", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 20, ly + 95, "Фініш: повільний (купони колекціонера)", size=10, color=MUTED, anchor="start"))

    # Pull
    frags.append(line(lx + 20, ly + 125, lx + 50, ly + 125, color=NEG, sw=2.5, dash="4,2"))
    frags.append(text(lx + 60, ly + 129, "Стратегія Pull", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(text(lx + 20, ly + 147, "Старт: повільний (ймовірність 1/N)", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 20, ly + 162, "Фініш: s_{t+1} = s_t^(k+1) (квадратичний)", size=10, color=MUTED, anchor="start"))

    # Push-Pull
    frags.append(line(lx + 20, ly + 192, lx + 50, ly + 192, color=FIELD, sw=3))
    frags.append(text(lx + 60, ly + 196, "Стратегія Push-Pull", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(lx + 20, ly + 214, "Поєднує швидкий старт і різкий фініш", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 20, ly + 228, "Збіжність за O(log N) раундів", size=10, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "push-pull-dynamics.svg"), w, h, *frags)


def fig_scuttlebutt_handshake():
    """Фігура 3: Трифазний протокол узгодження Scuttlebutt (DigestSyn -> DigestAck -> DigestAck2)."""
    w, h = 880, 410
    frags = []

    frags.append(text(w / 2, 26, "Трифазне узгодження Scuttlebutt: синхронізація дельт за 1.5 RTT", size=15, bold=True))

    # Стовпчики вузлів A та B
    ax, bx = 160, 720
    top_y, bot_y = 60, 385

    # Лінії життя (lifelines)
    frags.append(line(ax, top_y + 35, ax, bot_y, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(line(bx, top_y + 35, bx, bot_y, color="#94a3b8", sw=1.5, dash="4,4"))

    # Шапки вузлів
    frags.append(rect(ax - 70, top_y, 140, 35, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(ax, top_y + 22, "Вузол A (Ініціатор)", size=11, bold=True, color=NEG))

    frags.append(rect(bx - 70, top_y, 140, 35, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(bx, top_y + 22, "Вузол B (Партнер)", size=11, bold=True, color=FIELD))

    # Крок 1: DigestSyn від A до B
    y1 = 125
    frags.append(arrow(ax, y1, bx, y1 + 30, color=NEG, sw=2))
    frags.append(rect(300, y1 - 12, 280, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=5))
    frags.append(text(440, y1 + 6, "1. GOSSIP_DIGEST_SYN", size=11, bold=True, color=NEG))
    frags.append(text(440, y1 + 22, "Дайджест: {Вузол1: v10, Вузол2: v4, Вузол3: v1}", size=9, color=MUTED))

    # Обчислення на B
    y_calc_b = 185
    frags.append(rect(bx - 110, y_calc_b - 16, 220, 32, fill="#f8fafc", stroke="#64748b", sw=1, rx=4))
    frags.append(text(bx, y_calc_b + 4, "B порівнює дайджест зі своїм станом", size=9, color=MUTED))

    # Крок 2: DigestAck від B до A
    y2 = 235
    frags.append(arrow(bx, y2, ax, y2 + 35, color=FIELD, sw=2))
    frags.append(rect(290, y2 - 6, 300, 48, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    frags.append(text(440, y2 + 12, "2. GOSSIP_DIGEST_ACK", size=11, bold=True, color=FIELD))
    frags.append(text(440, y2 + 26, "• Дельти для A: {Вузол2: v5, v6}", size=9, color=FIELD))
    frags.append(text(440, y2 + 38, "• Запит до A: {Вузол1 потрібні версії > v8}", size=9, color=POS))

    # Застосування та обчислення на A
    y_calc_a = 295
    frags.append(rect(ax - 110, y_calc_a - 16, 220, 32, fill="#f8fafc", stroke="#64748b", sw=1, rx=4))
    frags.append(text(ax, y_calc_a + 4, "A застосовує дельти та формує відповідь", size=9, color=MUTED))

    # Крок 3: DigestAck2 від A до B
    y3 = 345
    frags.append(arrow(ax, y3, bx, y3 + 25, color=POS, sw=2))
    frags.append(rect(300, y3 - 10, 280, 42, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    frags.append(text(440, y3 + 8, "3. GOSSIP_DIGEST_ACK2", size=11, bold=True, color=POS))
    frags.append(text(440, y3 + 24, "Дельти для B: {Вузол1: v9, v10}", size=9, color=POS))

    render(os.path.join(OUT, "scuttlebutt-handshake.svg"), w, h, *frags)


def fig_hierarchical_gossip_topology():
    """Фігура 4: Ієрархічна топологія розповсюдження для георозподілених дата-центрів (WAN vs LAN)."""
    w, h = 880, 370
    frags = []

    frags.append(text(w / 2, 26, "Ієрархічний Gossip: захист міжрегіональних каналів WAN", size=15, bold=True))

    # Дата-центр 1 (Регіон Європа)
    dc1_x, dc1_y = 35, 52
    dc_w, dc_h = 370, 300
    frags.append(rect(dc1_x, dc1_y, dc_w, dc_h, fill="#fafbfc", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(dc1_x + dc_w / 2, dc1_y + 24, "Дата-центр 1 (Регіон EU-West)", size=13, bold=True, color=NEG))
    frags.append(text(dc1_x + dc_w / 2, dc1_y + 40, "Високочастотний локальний LAN Gossip (100–200 мс)", size=9, color=MUTED))

    # Вузли DC1
    eu_nodes = [
        (dc1_x + 65, dc1_y + 100),
        (dc1_x + 165, dc1_y + 90),
        (dc1_x + 85, dc1_y + 190),
        (dc1_x + 185, dc1_y + 210),
    ]
    for i, (nx, ny) in enumerate(eu_nodes):
        frags.append(circle(nx, ny, 18, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(nx, ny + 4, "EU-%d" % (i + 1), size=9, bold=True, color=NEG))

    # Локальні зв'язки LAN DC1
    frags.append(arrow(eu_nodes[0][0] + 16, eu_nodes[0][1], eu_nodes[1][0] - 16, eu_nodes[1][1], color=NEG, sw=1.2))
    frags.append(arrow(eu_nodes[0][0], eu_nodes[0][1] + 16, eu_nodes[2][0], eu_nodes[2][1] - 16, color=NEG, sw=1.2))
    frags.append(arrow(eu_nodes[1][0], eu_nodes[1][1] + 16, eu_nodes[3][0], eu_nodes[3][1] - 16, color=NEG, sw=1.2))
    frags.append(arrow(eu_nodes[2][0] + 16, eu_nodes[2][1], eu_nodes[3][0] - 16, eu_nodes[3][1], color=NEG, sw=1.2))

    # Міжрегіональний міст (Bridge Gateway) DC1
    b1_x, b1_y = dc1_x + 295, dc1_y + 150
    frags.append(circle(b1_x, b1_y, 25, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(b1_x, b1_y - 3, "Шлюз", size=10, bold=True, color=POS))
    frags.append(text(b1_x, b1_y + 10, "Bridge-1", size=9, color=MUTED))

    # Зв'язки від внутрішніх вузлів до шлюзу
    frags.append(arrow(eu_nodes[1][0] + 16, eu_nodes[1][1] + 10, b1_x - 22, b1_y - 12, color="#94a3b8", sw=1.2))
    frags.append(arrow(eu_nodes[3][0] + 16, eu_nodes[3][1] - 10, b1_x - 22, b1_y + 12, color="#94a3b8", sw=1.2))

    # Дата-центр 2 (Регіон США)
    dc2_x, dc2_y = 475, 52
    frags.append(rect(dc2_x, dc2_y, dc_w, dc_h, fill="#fafbfc", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(dc2_x + dc_w / 2, dc2_y + 24, "Дата-центр 2 (Регіон US-East)", size=13, bold=True, color=FIELD))
    frags.append(text(dc2_x + dc_w / 2, dc2_y + 40, "Високочастотний локальний LAN Gossip (100–200 мс)", size=9, color=MUTED))

    # Міжрегіональний міст DC2
    b2_x, b2_y = dc2_x + 75, dc2_y + 150
    frags.append(circle(b2_x, b2_y, 25, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(b2_x, b2_y - 3, "Шлюз", size=10, bold=True, color=POS))
    frags.append(text(b2_x, b2_y + 10, "Bridge-2", size=9, color=MUTED))

    # Вузли DC2
    us_nodes = [
        (dc2_x + 205, dc2_y + 90),
        (dc2_x + 305, dc2_y + 100),
        (dc2_x + 185, dc2_y + 210),
        (dc2_x + 285, dc2_y + 190),
    ]
    for i, (nx, ny) in enumerate(us_nodes):
        frags.append(circle(nx, ny, 18, fill="#f0fdf4", stroke=FIELD, sw=1.5))
        frags.append(text(nx, ny + 4, "US-%d" % (i + 1), size=9, bold=True, color=FIELD))

    # Локальні зв'язки LAN DC2
    frags.append(arrow(us_nodes[0][0] + 16, us_nodes[0][1], us_nodes[1][0] - 16, us_nodes[1][1], color=FIELD, sw=1.2))
    frags.append(arrow(us_nodes[0][0], us_nodes[0][1] + 16, us_nodes[2][0], us_nodes[2][1] - 16, color=FIELD, sw=1.2))
    frags.append(arrow(us_nodes[1][0], us_nodes[1][1] + 16, us_nodes[3][0], us_nodes[3][1] - 16, color=FIELD, sw=1.2))
    frags.append(arrow(us_nodes[2][0] + 16, us_nodes[2][1], us_nodes[3][0] - 16, us_nodes[3][1], color=FIELD, sw=1.2))

    # Зв'язки від шлюзу до внутрішніх вузлів DC2
    frags.append(arrow(b2_x + 22, b2_y - 12, us_nodes[0][0] - 16, us_nodes[0][1] + 10, color="#94a3b8", sw=1.2))
    frags.append(arrow(b2_x + 22, b2_y + 12, us_nodes[2][0] - 16, us_nodes[2][1] - 10, color="#94a3b8", sw=1.2))

    # Міжрегіональний WAN зв'язок між шлюзами
    frags.append(arrow(b1_x + 25, b1_y - 8, b2_x - 25, b2_y - 8, color=POS, sw=2.5))
    frags.append(arrow(b2_x - 25, b2_y + 8, b1_x + 25, b1_y + 8, color=POS, sw=2.5))

    # Підпис WAN
    frags.append(rect(380, b1_y - 36, 120, 24, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(440, b1_y - 20, "WAN (1-5 с, TCP)", size=9, bold=True, color=POS))
    frags.append(text(440, b1_y + 26, "Агреговані дайджести", size=9, color=MUTED))

    # Нижній пояснювальний блок
    frags.append(rect(dc1_x + 10, dc1_y + 245, dc_w - 20, 45, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(dc1_x + dc_w / 2, dc1_y + 263, "Внутрішній LAN: швидкий розліт UDP", size=10, bold=True, color=INK))
    frags.append(text(dc1_x + dc_w / 2, dc1_y + 278, "Шлюз агрегує зміни для трансляції назовні", size=9, color=MUTED))

    frags.append(rect(dc2_x + 10, dc2_y + 245, dc_w - 20, 45, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(dc2_x + dc_w / 2, dc2_y + 263, "Внутрішній LAN: швидкий розліт UDP", size=10, bold=True, color=INK))
    frags.append(text(dc2_x + dc_w / 2, dc2_y + 278, "Шлюз агрегує зміни для трансляції назовні", size=9, color=MUTED))

    render(os.path.join(OUT, "hierarchical-gossip-topology.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_rumor_vs_anti_entropy()
    fig_push_pull_dynamics()
    fig_scuttlebutt_handshake()
    fig_hierarchical_gossip_topology()
    print("Всі 4 SVG фігури успішно згенеровано у %s" % OUT)
