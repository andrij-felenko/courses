# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Gossip-протоколи'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_gossip_vs_traditional():
    """Фігура 1: Порівняння архітектур зв'язку — централізована, all-to-all та gossip."""
    w, h = 860, 390
    frags = []

    frags.append(text(w / 2, 28, "Топології виявлення збоїв та поширення стану в кластері", size=16, bold=True))

    # Секція 1: Централізований координатор
    frags.append(rect(20, 50, 260, 315, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(150, 75, "1. Централізований хаб", size=14, bold=True, color=INK))

    # Вузли навколо координатора
    cx, cy = 150, 185
    frags.append(circle(cx, cy, 32, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(cx, cy - 5, "Координатор", size=11, bold=True, color=POS))
    frags.append(text(cx, cy + 10, "(ZooKeeper/etcd)", size=9, color=MUTED))

    # 4 периферійні вузли
    nodes = [(65, 115), (235, 115), (65, 255), (235, 255)]
    for i, (nx, ny) in enumerate(nodes):
        frags.append(circle(nx, ny, 20, fill="#eaf0fd", stroke=NEG, sw=1.5))
        frags.append(text(nx, ny + 4, "N%d" % (i + 1), size=11, bold=True, color=NEG))
        # стрілки до координатора
        frags.append(arrow(nx + (14 if nx < cx else -14), ny + (14 if ny < cy else -14),
                           cx + (-20 if nx < cx else 20), cy + (-20 if ny < cy else 20), color=LINE, sw=1.2))

    frags.append(rect(35, 295, 230, 58, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(150, 315, "Навантаження: O(N) на хаб", size=11, bold=True, color=POS))
    frags.append(text(150, 332, "Єдина точка відмови (SPOF)", size=10, color=MUTED))
    frags.append(text(150, 345, "Вузьке місце масштабування", size=10, color=MUTED))

    # Секція 2: Повний зв'язок All-to-all
    frags.append(rect(300, 50, 260, 315, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(430, 75, "2. Повний зв'язок (All-to-All)", size=14, bold=True, color=INK))

    # 5 вузлів по колу
    import math
    poly_nodes = []
    for k in range(5):
        angle = k * 2 * math.pi / 5 - math.pi / 2
        px = 430 + 65 * math.cos(angle)
        py = 180 + 65 * math.sin(angle)
        poly_nodes.append((px, py))

    # Ребра між усіма парами
    for i in range(5):
        for j in range(i + 1, 5):
            x1, y1 = poly_nodes[i]
            x2, y2 = poly_nodes[j]
            frags.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=1.2, dash="3,3"))

    for i, (px, py) in enumerate(poly_nodes):
        frags.append(circle(px, py, 18, fill="#fdecea", stroke=POS, sw=1.5))
        frags.append(text(px, py + 4, "N%d" % (i + 1), size=10, bold=True, color=POS))

    frags.append(rect(315, 295, 230, 58, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(430, 315, "Трафік: O(N²) повідомлень", size=11, bold=True, color=POS))
    frags.append(text(430, 332, "Шторм пакетів у мережі", size=10, color=MUTED))
    frags.append(text(430, 345, "Колапс комутаторів при N > 100", size=10, color=MUTED))

    # Секція 3: Gossip-протокол
    frags.append(rect(580, 50, 260, 315, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(710, 75, "3. Gossip (Епідемічний)", size=14, bold=True, color=INK))

    # 5 вузлів по колу з випадковими рідкісними стрілками
    g_nodes = []
    for k in range(5):
        angle = k * 2 * math.pi / 5 - math.pi / 2
        px = 710 + 65 * math.cos(angle)
        py = 180 + 65 * math.sin(angle)
        g_nodes.append((px, py))

    # Випадкові цільові стрілки (fanout k=2)
    pairs = [(0, 2), (0, 3), (1, 4), (2, 1), (3, 4), (4, 0)]
    for i, j in pairs:
        x1, y1 = g_nodes[i]
        x2, y2 = g_nodes[j]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            frags.append(arrow(x1 + ux * 18, y1 + uy * 18, x2 - ux * 18, y2 - uy * 18, color=FIELD, sw=1.6))

    for i, (px, py) in enumerate(g_nodes):
        frags.append(circle(px, py, 18, fill="#f0fdf4", stroke=FIELD, sw=1.8))
        frags.append(text(px, py + 4, "N%d" % (i + 1), size=10, bold=True, color=FIELD))

    frags.append(rect(595, 295, 230, 58, fill="#ffffff", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(710, 315, "Трафік: O(k) на вузол (константа)", size=11, bold=True, color=FIELD))
    frags.append(text(710, 332, "Збіжність за O(log N) раундів", size=10, color=INK))
    frags.append(text(710, 345, "Стійкість до втрати 50%+ пакетів", size=10, color=MUTED))

    return render(os.path.join(OUT, "gossip-vs-traditional.svg"), w, h, *frags)


def fig_swim_protocol_flow():
    """Фігура 2: Потік детектування збоїв у SWIM — прямий зонд, непрямий ping-req, підозра та спростування."""
    w, h = 860, 410
    frags = []

    frags.append(text(w / 2, 28, "Протокол детектування збоїв SWIM: прямий зонд, непрямий запит та спростування", size=16, bold=True))

    # Фаза 1: Прямий зонд (Direct Probe)
    frags.append(rect(20, 50, 260, 335, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(150, 75, "Фаза 1: Прямий зонд", size=14, bold=True, color=INK))

    frags.append(rect(35, 95, 75, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(72, 120, "Вузол A", size=12, bold=True, color=NEG))

    frags.append(rect(190, 95, 75, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(227, 120, "Вузол B", size=12, bold=True, color=POS))

    # Стрілка прямого пінга
    frags.append(arrow(110, 115, 185, 115, color=LINE, sw=1.8))
    frags.append(text(148, 107, "Ping", size=11, bold=True, color=INK))

    # Червоний хрестик втрати відповіді
    frags.append(line(140, 140, 160, 160, color=POS, sw=2.5))
    frags.append(line(160, 140, 140, 160, color=POS, sw=2.5))
    frags.append(text(150, 175, "Втрата пакета / таймаут", size=10, color=POS, bold=True))

    frags.append(rect(35, 200, 230, 70, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(150, 222, "Таймаут відповіді (Ack):", size=11, bold=True, color=INK))
    frags.append(text(150, 240, "A не оголошує B мертвим одразу,", size=10, color=MUTED))
    frags.append(text(150, 255, "бо збій може бути асиметричним", size=10, color=MUTED))

    frags.append(rect(35, 285, 230, 85, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=5))
    frags.append(text(150, 305, "Перехід до Фази 2:", size=11, bold=True, color="#c2410c"))
    frags.append(text(150, 325, "Вибір k помічників (C, D)", size=10, color=INK))
    frags.append(text(150, 342, "для непрямого опитування B", size=10, color=INK))
    frags.append(text(150, 358, "(Indirect Probing)", size=10, italic=True, color=MUTED))

    # Фаза 2: Непрямий зонд (Indirect Ping-Req)
    frags.append(rect(295, 50, 270, 335, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(430, 75, "Фаза 2: Непрямий Ping-Req", size=14, bold=True, color=INK))

    frags.append(rect(310, 95, 65, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(342, 117, "Вузол A", size=11, bold=True, color=NEG))

    frags.append(rect(485, 95, 65, 35, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(517, 117, "Вузол B", size=11, bold=True, color=POS))

    frags.append(rect(395, 155, 75, 35, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(432, 177, "Помічник C", size=10, bold=True, color=FIELD))

    # Стрілки A -> C (ping-req) і C -> B (ping)
    frags.append(arrow(355, 130, 395, 160, color=LINE, sw=1.5))
    frags.append(text(360, 155, "Ping-Req", size=9, bold=True, color=INK))

    frags.append(arrow(470, 165, 500, 130, color=LINE, sw=1.5))
    frags.append(text(500, 155, "Ping", size=9, bold=True, color=INK))

    # C отримує Ack від B і передає A
    frags.append(rect(310, 205, 240, 75, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(430, 225, "Сценарій А: C достукався до B", size=11, bold=True, color=FIELD))
    frags.append(text(430, 242, "C пересилає Ack вузлу A", size=10, color=INK))
    frags.append(text(430, 258, "B лишається Alive (збій зв'язку A-B)", size=10, color=FIELD))
    frags.append(text(430, 272, "Хибну тривогу відвернено", size=9, color=MUTED))

    frags.append(rect(310, 290, 240, 80, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(430, 310, "Сценарій Б: Ніхто не достукався", size=11, bold=True, color=POS))
    frags.append(text(430, 328, "Таймаут непрямих відповідей", size=10, color=INK))
    frags.append(text(430, 345, "A оголошує: B = Suspect(inc=I)", size=10, bold=True, color=POS))
    frags.append(text(430, 360, "Запуск таймера підозри Tsuspect", size=9, color=MUTED))

    # Фаза 3: Підозра та Спростування
    frags.append(rect(580, 50, 260, 335, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(710, 75, "Фаза 3: Підозра й Спростування", size=14, bold=True, color=INK))

    frags.append(rect(595, 95, 230, 80, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=5))
    frags.append(text(710, 115, "Стан Suspect (Підозра):", size=11, bold=True, color="#c2410c"))
    frags.append(text(710, 132, "Плітка шириться кластером.", size=10, color=INK))
    frags.append(text(710, 148, "B ще не видаляється з таблиць,", size=10, color=INK))
    frags.append(text(710, 163, "але трафік на нього обмежується", size=9, color=MUTED))

    frags.append(rect(595, 185, 230, 85, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(710, 205, "Спростування (Refutation):", size=11, bold=True, color=FIELD))
    frags.append(text(710, 223, "B живий і чує плітку про свою смерть!", size=10, color=INK))
    frags.append(text(710, 240, "B робить: inc = inc + 1", size=10, bold=True, color=FIELD))
    frags.append(text(710, 255, "Розсилає Alive(inc+1) —", size=10, color=FIELD))
    frags.append(text(710, 268, "старша інкарнація скасовує підозру", size=9, color=MUTED))

    frags.append(rect(595, 280, 230, 90, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(710, 300, "Підтвердження смерті (Dead):", size=11, bold=True, color=POS))
    frags.append(text(710, 318, "Таймер Tsuspect вичерпано,", size=10, color=INK))
    frags.append(text(710, 334, "спростування від B не надійшло.", size=10, color=INK))
    frags.append(text(710, 350, "B = Dead -> видалення з кластера", size=10, bold=True, color=POS))
    frags.append(text(710, 364, "із фіксацією Tombstone", size=9, color=MUTED))

    return render(os.path.join(OUT, "swim-protocol-flow.svg"), w, h, *frags)


def fig_push_pull_convergence():
    """Фігура 3: Динаміка поширення даних — Push, Pull та комбінований Push-Pull."""
    w, h = 860, 400
    frags = []

    frags.append(text(w / 2, 28, "Порівняння динаміки епідемічного поширення: Push проти Pull", size=16, bold=True))

    # Ліва частина: Графік частки інфікованих вузлів від раундів
    frags.append(rect(20, 50, 420, 330, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(230, 75, "Динаміка частки охоплених вузлів (I/N)", size=13, bold=True, color=INK))

    # Осі графіка
    ox, oy = 65, 330
    gw, gh = 345, 220
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))

    # Підписи осей
    frags.append(text(ox + gw - 20, oy + 25, "Раунди (t)", size=10, color=INK, bold=True))
    frags.append(text(ox - 25, oy - gh + 15, "100%", size=10, color=INK))
    frags.append(text(ox - 25, oy - gh / 2, "50%", size=10, color=INK))
    frags.append(text(ox - 25, oy, "0%", size=10, color=INK))

    # Горизонтальні пунктирні сітки
    frags.append(line(ox, oy - gh, ox + gw, oy - gh, color="#e2e8f0", sw=1, dash="3,3"))
    frags.append(line(ox, oy - gh / 2, ox + gw, oy - gh / 2, color="#e2e8f0", sw=1, dash="3,3"))

    # Крива Push (червона / синя) — повільний хвіст
    push_pts = [
        (ox, oy),
        (ox + 40, oy - 25),
        (ox + 80, oy - 70),
        (ox + 130, oy - 140),
        (ox + 180, oy - 180),
        (ox + 240, oy - 198),
        (ox + 300, oy - 208),
        (ox + gw, oy - 212)
    ]
    for i in range(len(push_pts) - 1):
        x1, y1 = push_pts[i]
        x2, y2 = push_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.2))

    # Крива Push-Pull (зелена) — швидкий старт і експоненційний фініш
    hybrid_pts = [
        (ox, oy),
        (ox + 40, oy - 25),
        (ox + 80, oy - 75),
        (ox + 130, oy - 150),
        (ox + 180, oy - 205),
        (ox + 220, oy - 219),
        (ox + 260, oy - 220),
        (ox + gw, oy - 220)
    ]
    for i in range(len(hybrid_pts) - 1):
        x1, y1 = hybrid_pts[i]
        x2, y2 = hybrid_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=FIELD, sw=2.5))

    # Легенда на графіку
    frags.append(rect(80, 100, 175, 55, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    frags.append(line(90, 118, 120, 118, color=FIELD, sw=2.5))
    frags.append(text(125, 122, "Push-Pull (Оптимум)", size=10, bold=True, color=FIELD, anchor="start"))
    frags.append(line(90, 138, 120, 138, color=POS, sw=2.2))
    frags.append(text(125, 142, "Лише Push (Хвіст O(N))", size=10, bold=True, color=POS, anchor="start"))

    # Права частина: Порівняльна аналітика механізмів
    frags.append(rect(455, 50, 385, 330, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(647, 75, "Фазова поведінка підходів", size=13, bold=True, color=INK))

    frags.append(rect(470, 95, 355, 75, fill="#ffffff", stroke=POS, sw=1.5, rx=5))
    frags.append(text(485, 116, "1. Лише Push (Передача новим):", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(485, 133, "• Рання фаза: Вибуховий експоненційний ріст.", size=10, color=INK, anchor="start"))
    frags.append(text(485, 148, "• Пізня фаза: «Стрільба по вже заражених».", size=10, color=POS, anchor="start"))
    frags.append(text(485, 161, "  Останні вузли шукаються за O(N) надлишкових повідомлень.", size=9, color=MUTED, anchor="start"))

    frags.append(rect(470, 180, 355, 75, fill="#ffffff", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(485, 201, "2. Лише Pull (Запит у випадкових):", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(text(485, 218, "• Рання фаза: Повільний старт (мало хто знає).", size=10, color=NEG, anchor="start"))
    frags.append(text(485, 233, "• Пізня фаза: Неінфіковані вузли миттєво знаходять", size=10, color=INK, anchor="start"))
    frags.append(text(485, 246, "  інфікованих з імовірністю ~1. Квадратичне згасання залишку.", size=9, color=MUTED, anchor="start"))

    frags.append(rect(470, 265, 355, 100, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=5))
    frags.append(text(485, 287, "3. Комбінований Push-Pull (Анти-ентропія):", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(485, 305, "• Поєднує швидкий старт Push та швидкий фініш Pull.", size=10, color=INK, anchor="start"))
    frags.append(text(485, 321, "• Кількість раундів до повного охоплення: O(log N).", size=10, bold=True, color=FIELD, anchor="start"))
    frags.append(text(485, 337, "• Трафік на раунд: фіксований O(k) байтів.", size=10, color=INK, anchor="start"))
    frags.append(text(485, 352, "• Стандарт де-факто для Cassandra, Consul, Serf.", size=9, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "push-pull-convergence.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_gossip_vs_traditional()
    fig_swim_protocol_flow()
    fig_push_pull_convergence()
    print("All figures generated successfully.")
