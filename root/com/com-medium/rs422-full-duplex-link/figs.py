# -*- coding: utf-8 -*-
"""Фігури до теми «RS-422».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── 1. Диференційні рівні RS-422: напруги A, B, різниця V_ID та пороги ±200 мВ ─
def fig_differential_levels():
    W, H = 760, 430
    f = [text(W / 2, 26, "Електричні рівні RS-422: парафазні сигнали та порогова чутливість ±200 мВ",
              size=14, bold=True)]

    ox = 80
    span = 460
    base_a = 105   # вісь лінії A (TX+ / Неінвертована)
    base_b = 205   # вісь лінії B (TX- / Інвертована)
    base_d = 330   # вісь різниці V_ID = V_A - V_B

    # Позначення логічних станів у часі: 4 біти (Mark/1, Space/0, Mark/1, Mark/1)
    bit_labels = [("Mark (1)", 0.0, 0.25), ("Space (0)", 0.25, 0.5), ("Mark (1)", 0.5, 0.75), ("Mark (1)", 0.75, 1.0)]
    for lbl, t0, t1 in bit_labels:
        cx = ox + ((t0 + t1) / 2.0) * span
        f.append(text(cx, 55, lbl, size=11, bold=True, color=MUTED))
        f.append(line(ox + t0 * span, 62, ox + t0 * span, 385, color="#e2e8f0", sw=1.0, dash="3,3"))
    f.append(line(ox + span, 62, ox + span, 385, color="#e2e8f0", sw=1.0, dash="3,3"))

    # Сигнал A (TX+): Mark -> +3.8V, Space -> +0.8V
    # Сигнал B (TX-): Mark -> +0.8V, Space -> +3.8V
    # V_ID = A - B: Mark -> +3.0V, Space -> -3.0V
    def make_wave(is_b=False):
        pts = []
        for i in range(241):
            t = i / 240.0
            # Стан біта
            if t < 0.25:
                val = 0.8 if is_b else 3.8
            elif t < 0.50:
                val = 3.8 if is_b else 0.8
            else:
                val = 0.8 if is_b else 3.8
            
            # Згладжування фронтів
            if 0.23 <= t <= 0.27:
                k = (t - 0.23) / 0.04
                v_from = 0.8 if is_b else 3.8
                v_to = 3.8 if is_b else 0.8
                val = v_from + (v_to - v_from) * (0.5 - 0.5 * math.cos(k * math.pi))
            elif 0.48 <= t <= 0.52:
                k = (t - 0.48) / 0.04
                v_from = 3.8 if is_b else 0.8
                v_to = 0.8 if is_b else 3.8
                val = v_from + (v_to - v_from) * (0.5 - 0.5 * math.cos(k * math.pi))

            base = base_b if is_b else base_a
            # масштаб: 1V = 16px
            y = base - (val - 2.0) * 16
            pts.append("%.1f,%.1f" % (ox + t * span, y))
        return " ".join(pts)

    # Осі й рівні A
    f.append(line(ox, base_a, ox + span, base_a, color="#cbd5e1", sw=1.0))
    f.append(text(ox - 12, base_a + 4, "V_A (TX+)", size=11, bold=True, color=POS, anchor="end"))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (make_wave(False), POS))
    f.append(text(ox + span + 10, base_a - 28, "≈ +3.8 В", size=10, color=POS, anchor="start"))
    f.append(text(ox + span + 10, base_a + 22, "≈ +0.8 В", size=10, color=POS, anchor="start"))

    # Осі й рівні B
    f.append(line(ox, base_b, ox + span, base_b, color="#cbd5e1", sw=1.0))
    f.append(text(ox - 12, base_b + 4, "V_B (TX−)", size=11, bold=True, color=NEG, anchor="end"))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (make_wave(True), NEG))
    f.append(text(ox + span + 10, base_b - 28, "≈ +3.8 В", size=10, color=NEG, anchor="start"))
    f.append(text(ox + span + 10, base_b + 22, "≈ +0.8 В", size=10, color=NEG, anchor="start"))

    # Роздільник
    f.append(line(35, 255, W - 35, 255, color="#e2e8f0", sw=1.0, dash="5,4"))

    # Диференційна напруга V_ID = V_A - V_B
    f.append(line(ox, base_d, ox + span, base_d, color=LINE, sw=1.2))
    f.append(text(ox - 12, base_d + 4, "V_ID (A−B)", size=11, bold=True, color=FIELD, anchor="end"))

    # Порогові зони ±200 мВ
    # Масштаб V_ID: 1V = 18px -> 0.2V = 3.6px
    th_pos = base_d - 0.2 * 18
    th_neg = base_d + 0.2 * 18
    f.append(rect(ox, th_pos, span, th_neg - th_pos, fill="#fee2e2", stroke="none"))
    f.append(line(ox, th_pos, ox + span, th_pos, color=POS, sw=1.0, dash="2,2"))
    f.append(line(ox, th_neg, ox + span, th_neg, color=NEG, sw=1.0, dash="2,2"))
    f.append(text(ox + span + 10, th_pos - 4, "+0.2 В (Поріг Mark)", size=10, color=POS, anchor="start"))
    f.append(text(ox + span + 10, th_neg + 11, "−0.2 В (Поріг Space)", size=10, color=NEG, anchor="start"))
    f.append(text(ox + span + 10, base_d + 3, "0 В (Невизначеність)", size=9, color=MUTED, anchor="start"))

    # Хвиля V_ID
    pts_d = []
    for i in range(241):
        t = i / 240.0
        if t < 0.25:
            val = 3.0
        elif t < 0.50:
            val = -3.0
        else:
            val = 3.0
        if 0.23 <= t <= 0.27:
            k = (t - 0.23) / 0.04
            val = 3.0 - 6.0 * (0.5 - 0.5 * math.cos(k * math.pi))
        elif 0.48 <= t <= 0.52:
            k = (t - 0.48) / 0.04
            val = -3.0 + 6.0 * (0.5 - 0.5 * math.cos(k * math.pi))
        y = base_d - val * 18
        pts_d.append("%.1f,%.1f" % (ox + t * span, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_d), FIELD))

    f.append(text(ox + 0.125 * span, base_d - 60, "Mark: V_ID > +0.2 В  (TX = 1)", size=10.5, color=FIELD, bold=True))
    f.append(text(ox + 0.375 * span, base_d + 68, "Space: V_ID < −0.2 В  (TX = 0)", size=10.5, color=POS, bold=True))

    b, _, _ = textbox(W / 2, 412,
                      "Приймач визначає логічний стан за знаком різниці V_A − V_B; діапазон від −200 мВ до +200 мВ є зоною перемикання",
                      size=11, fill="#f8fafc", stroke="#94a3b8")
    f.append(b)

    render(os.path.join(IMG, "differential-levels.svg"), W, H, *f)


# ── 2. Повнодуплексна 4-провідна топологія з 5-м проводом GND ─────────────────
def fig_four_wire_full_duplex():
    W, H = 760, 420
    f = [text(W / 2, 26, "Повнодуплексний зв'язок RS-422: дві виті пари та спільний провід заземлення",
              size=14, bold=True)]

    # Вузол 1 (Master / DTE) ліворуч
    m_x, m_w, m_h = 45, 175, 270
    m_y = 65
    f.append(rect(m_x, m_y, m_w, m_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(m_x + m_w / 2, m_y + 24, "Вузол 1 (Ведучий)", size=13, bold=True, color=FIELD))

    # Передавач TX1
    f.append(rect(m_x + 95, m_y + 55, 65, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(m_x + 127, m_y + 85, "TX (D)", size=11.5, bold=True, color=POS))
    f.append(text(m_x + 40, m_y + 85, "UART TX", size=10, color=INK))
    f.append(arrow(m_x + 70, m_y + 80, m_x + 95, m_y + 80, color=LINE, sw=1.2))

    # Приймач RX1
    f.append(rect(m_x + 95, m_y + 165, 65, 50, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(m_x + 127, m_y + 195, "RX (R)", size=11.5, bold=True, color=NEG))
    f.append(text(m_x + 40, m_y + 195, "UART RX", size=10, color=INK))
    f.append(arrow(m_x + 95, m_y + 190, m_x + 70, m_y + 190, color=LINE, sw=1.2))

    # Земля Вузла 1
    f.append(line(m_x + 30, m_y + 245, m_x + 145, m_y + 245, color="#64748b", sw=1.5))
    f.append(text(m_x + 87, m_y + 260, "Земля GND1", size=10, color="#64748b", bold=True))

    # Вузол 2 (Slave / DCE) праворуч
    s_x, s_w, s_h = W - 220, 175, 270
    s_y = 65
    f.append(rect(s_x, s_y, s_w, s_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(s_x + s_w / 2, s_y + 24, "Вузол 2 (Ведений)", size=13, bold=True, color=NEG))

    # Приймач RX2
    f.append(rect(s_x + 15, s_y + 55, 65, 50, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(s_x + 47, s_y + 85, "RX (R)", size=11.5, bold=True, color=NEG))
    f.append(text(s_x + 135, s_y + 85, "UART RX", size=10, color=INK))
    f.append(arrow(s_x + 80, s_y + 80, s_x + 105, s_y + 80, color=LINE, sw=1.2))

    # Передавач TX2
    f.append(rect(s_x + 15, s_y + 165, 65, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(s_x + 47, s_y + 195, "TX (D)", size=11.5, bold=True, color=POS))
    f.append(text(s_x + 135, s_y + 195, "UART TX", size=10, color=INK))
    f.append(arrow(s_x + 105, s_y + 190, s_x + 80, s_y + 190, color=LINE, sw=1.2))

    # Земля Вузла 2
    f.append(line(s_x + 30, s_y + 245, s_x + 145, s_y + 245, color="#64748b", sw=1.5))
    f.append(text(s_x + 87, s_y + 260, "Земля GND2", size=10, color="#64748b", bold=True))

    # Лінії передачі (Вита пара 1: Master TX -> Slave RX)
    y_tx_a = m_y + 70
    y_tx_b = m_y + 90
    f.append(line(m_x + 160, y_tx_a, s_x + 15, y_tx_a, color=POS, sw=1.8))
    f.append(line(m_x + 160, y_tx_b, s_x + 15, y_tx_b, color=NEG, sw=1.8))
    f.append(arrow(s_x - 30, y_tx_a, s_x + 10, y_tx_a, color=POS, sw=1.8))
    f.append(arrow(s_x - 30, y_tx_b, s_x + 10, y_tx_b, color=NEG, sw=1.8))

    # Термінатор RT1 на приймачі Slave (перед входом RX2)
    f.append(rect(s_x - 42, y_tx_a + 2, 28, 16, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    f.append(text(s_x - 28, y_tx_a - 5, "RT=120Ω", size=9, bold=True, color="#d97706"))

    f.append(text(W / 2, y_tx_a - 12, "Вита пара 1 (Канал передачі TX+ / TX−)", size=10.5, bold=True, color=POS))

    # Лінії передачі (Вита пара 2: Slave TX -> Master RX)
    y_rx_a = m_y + 180
    y_rx_b = m_y + 200
    f.append(line(s_x + 15, y_rx_a, m_x + 160, y_rx_a, color=POS, sw=1.8))
    f.append(line(s_x + 15, y_rx_b, m_x + 160, y_rx_b, color=NEG, sw=1.8))
    f.append(arrow(m_x + 205, y_rx_a, m_x + 165, y_rx_a, color=POS, sw=1.8))
    f.append(arrow(m_x + 205, y_rx_b, m_x + 165, y_rx_b, color=NEG, sw=1.8))

    # Термінатор RT2 на приймачі Master (перед входом RX1)
    f.append(rect(m_x + 185, y_rx_a + 2, 28, 16, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    f.append(text(m_x + 199, y_rx_a - 5, "RT=120Ω", size=9, bold=True, color="#d97706"))

    f.append(text(W / 2, y_rx_a - 12, "Вита пара 2 (Канал прийому RX+ / RX−)", size=10.5, bold=True, color=NEG))

    # 5-й провід землі (GND)
    y_gnd = m_y + 245
    f.append(line(m_x + 145, y_gnd, s_x + 30, y_gnd, color="#64748b", sw=1.8, dash="6,4"))
    f.append(text(W / 2, y_gnd - 8, "5-й провід: Спільний сигнальний GND (вирівнює потенціали V_cm в межах ±7 В)",
                  size=10, bold=True, color="#475569"))

    b, _, _ = textbox(W / 2, 385,
                      "4 сигнальні проводи забезпечують одночасний двосторонній потік (Full-Duplex); 5-й дріт заземлення обмежує синфазний зсув",
                      size=11, fill="#f8fafc", stroke="#94a3b8")
    f.append(b)

    render(os.path.join(IMG, "four-wire-full-duplex.svg"), W, H, *f)


# ── 3. Багатоточкова симплексна топологія (Multidrop: 1 TX -> до 10 RX) ───────
def fig_multidrop_topology():
    W, H = 760, 410
    f = [text(W / 2, 26, "Топологія Multidrop в RS-422: один передавач (Generator) транслює до 10 приймачів",
              size=14, bold=True)]

    # Головний передавач ліворуч
    gen_x, gen_y = 45, 90
    f.append(rect(gen_x, gen_y, 110, 150, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(gen_x + 55, gen_y + 24, "Передавач", size=12, bold=True, color=FIELD))
    f.append(text(gen_x + 55, gen_y + 40, "(Generator)", size=10, color=MUTED))
    f.append(rect(gen_x + 30, gen_y + 65, 55, 45, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(gen_x + 57, gen_y + 92, "TX (D)", size=11, bold=True, color=POS))
    f.append(text(gen_x + 55, gen_y + 135, "1 пристрій", size=10, bold=True, color=INK))

    # Магістральна лінія (Trunk bus)
    bus_x0 = gen_x + 85
    bus_x1 = W - 60
    line_a = gen_y + 75
    line_b = gen_y + 100

    f.append(line(bus_x0, line_a, bus_x1, line_a, color=POS, sw=2.2))
    f.append(line(bus_x0, line_b, bus_x1, line_b, color=NEG, sw=2.2))
    f.append(text(bus_x0 + 15, line_a - 6, "TX+ (A)", size=10, bold=True, color=POS))
    f.append(text(bus_x0 + 15, line_b + 14, "TX− (B)", size=10, bold=True, color=NEG))

    # 3 приймачі (вузли на шині)
    rx_nodes = [
        ("Приймач 1", 240, False),
        ("Приймач 2", 410, False),
        ("Приймач 10 (Останній)", 600, True)
    ]

    for name, nx, is_last in rx_nodes:
        # Відгалуження (stub)
        f.append(circle(nx, line_a, 3.5, fill=POS, stroke=POS))
        f.append(circle(nx, line_b, 3.5, fill=NEG, stroke=NEG))
        f.append(line(nx - 8, line_a, nx - 8, line_a + 90, color=POS, sw=1.4))
        f.append(line(nx + 8, line_b, nx + 8, line_a + 90, color=NEG, sw=1.4))

        # Корпус приймача
        f.append(rect(nx - 55, line_a + 90, 110, 110, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
        f.append(text(nx, line_a + 112, name, size=11, bold=True, color=NEG))
        f.append(rect(nx - 25, line_a + 125, 50, 40, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
        f.append(text(nx, line_a + 150, "RX (R)", size=10.5, bold=True, color=NEG))
        f.append(text(nx, line_a + 185, "R_in ≥ 4 кΩ", size=9.5, color=MUTED))

        if is_last:
            # Термінатор на кінці шини
            f.append(rect(bus_x1 - 10, line_a + 4, 18, 17, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=2))
            f.append(text(bus_x1 - 1, line_a - 8, "RT = 100..120 Ω", size=9.5, bold=True, color="#d97706"))
            f.append(text(bus_x1 - 1, line_b + 22, "(Лише на дальньому кінці!)", size=9, italic=True, color="#d97706"))

    # Пояснення відводів
    f.append(text(325, line_a - 14, "Магістральна вита пара (Z₀ ≈ 100..120 Ω)", size=11, bold=True, color=LINE))
    f.append(text(325, line_a + 45, "Короткі відгалуження (stub < 0.3 м)", size=9.5, italic=True, color="#dc2626"))

    b, _, _ = textbox(W / 2, 365,
                      "RS-422 допускає лише 1 передавач на парі та до 10 паралельних приймачів (сумарне навантаження ≥ 400 Ω). Термінатор ставиться виключно на кінці лінії.",
                      size=11, fill="#f8fafc", stroke="#94a3b8")
    f.append(b)

    render(os.path.join(IMG, "multidrop-topology.svg"), W, H, *f)


# ── 4. Крива швидкості проти відстані за TIA/EIA-422 ───────────────────────────
def fig_speed_vs_distance():
    W, H = 760, 430
    f = [text(W / 2, 26, "Залежність швидкості передачі від довжини кабелю за стандартом TIA/EIA-422",
              size=14, bold=True)]

    # Логарифмічний графік
    # X: Довжина кабелю (1 м ... 1200 м)
    # Y: Швидкість (10 кбіт/с ... 10 Мбіт/с)
    gx, gy, gw, gh = 90, 60, 580, 270
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=0))

    # Координатна сітка
    # X мітки: 1 м, 10 м, 12 м (перегин), 100 м, 1200 м
    # log10(1) = 0, log10(1200) ≈ 3.08
    def x_coord(dist_m):
        log_d = math.log10(max(1.0, dist_m))
        return gx + (log_d / 3.1) * gw

    # Y мітки: 10 кбіт/с (10^4), 100 кбіт/с (10^5), 1 Мбіт/с (10^6), 10 Мбіт/с (10^7)
    # log10(10k) = 4, log10(10M) = 7 -> span = 3
    def y_coord(bps):
        log_s = math.log10(max(10000.0, bps))
        return gy + gh - ((log_s - 4.0) / 3.0) * gh

    # Горизонтальні лінії сітки
    speeds = [(10000, "10 кбіт/с"), (100000, "100 кбіт/с"), (1000000, "1 Мбіт/с"), (10000000, "10 Мбіт/с")]
    for s, lbl in speeds:
        y = y_coord(s)
        f.append(line(gx, y, gx + gw, y, color="#e2e8f0", sw=1.0, dash="3,3"))
        f.append(text(gx - 8, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # Вертикальні лінії сітки
    dists = [(1, "1 м"), (10, "10 м"), (12, "12 м"), (100, "100 м"), (1200, "1200 м")]
    for d, lbl in dists:
        x = x_coord(d)
        f.append(line(x, gy, x, gy + gh, color="#e2e8f0", sw=1.0, dash="3,3"))
        f.append(text(x, gy + gh + 16, lbl, size=10, color=MUTED, anchor="middle"))

    # Область безпечної роботи (Заливка)
    # 1м..12м: 10 Mbps
    # 12м..1200м: спад від 10 Mbps до 100 kbps (крива R·C / затухання)
    poly_pts = [
        "%.1f,%.1f" % (x_coord(1), y_coord(10000)),
        "%.1f,%.1f" % (x_coord(1), y_coord(10000000)),
        "%.1f,%.1f" % (x_coord(12), y_coord(10000000)),
        "%.1f,%.1f" % (x_coord(1200), y_coord(100000)),
        "%.1f,%.1f" % (x_coord(1200), y_coord(10000))
    ]
    f.append('<polygon points="%s" fill="#ecfdf5" opacity="0.8"/>' % " ".join(poly_pts))

    # Сама крива TIA/EIA-422
    line_pts = [
        "%.1f,%.1f" % (x_coord(1), y_coord(10000000)),
        "%.1f,%.1f" % (x_coord(12), y_coord(10000000)),
        "%.1f,%.1f" % (x_coord(1200), y_coord(100000))
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (" ".join(line_pts), FIELD))

    # Точки перегину
    p1_x, p1_y = x_coord(12), y_coord(10000000)
    p2_x, p2_y = x_coord(1200), y_coord(100000)
    f.append(circle(p1_x, p1_y, 5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(circle(p2_x, p2_y, 5, fill=POS, stroke="#ffffff", sw=1.5))

    f.append(text(p1_x + 10, p1_y - 12, "Макс. 10 Мбіт/с (до 12 м / 40 ft)", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(p2_x - 10, p2_y - 12, "Макс. 1200 м (100 кбіт/с)", size=10.5, bold=True, color=POS, anchor="end"))

    # Пояснення зон
    f.append(text(gx + 120, gy + 85, "Зона 1: Обмеження трансивера", size=10.5, bold=True, color=LINE))
    f.append(text(gx + 120, gy + 100, "(швидкість наростання фронтів dV/dt)", size=9.5, color=MUTED))

    f.append(text(gx + 340, gy + 155, "Зона 2: Обмеження кабелю (RC та ISI)", size=10.5, bold=True, color=LINE))
    f.append(text(gx + 340, gy + 170, "Довжина × Швидкість ≈ 10⁸ (біт·м/с)", size=9.5, color=MUTED))

    f.append(text(gx + 460, gy + 240, "Зона 3: Обмеження затухання", size=10.5, bold=True, color=LINE))
    f.append(text(gx + 460, gy + 255, "(макс. дальність 1.2 км через опір міді)", size=9.5, color=MUTED))

    f.append(text(gx + gw / 2, gy + gh + 34, "Довжина лінії передачі (метри, логарифмічна шкала)", size=11, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 408,
                      "На коротких дистанціях (<12 м) швидкість обмежена драйвером (10 Мбіт/с), далі діє спад через дисперсію та ємність лінії до 1.2 км",
                      size=10.5, fill="#f8fafc", stroke="#94a3b8")
    f.append(b)

    render(os.path.join(IMG, "speed-vs-distance.svg"), W, H, *f)


# ── 5. Схема Failsafe зміщення (Захист від обриву та пасивного стану) ───────────
def fig_failsafe_biasing():
    W, H = 760, 420
    f = [text(W / 2, 26, "Схема Failsafe-зміщення лінії RS-422 для запобігання хибному прийому",
              size=14, bold=True)]

    # Живлення VCC (+5V) угорі, GND унизу
    vcc_y = 65
    gnd_y = 285
    f.append(line(80, vcc_y, 400, vcc_y, color=POS, sw=2.0))
    f.append(text(65, vcc_y + 4, "VCC (+5В)", size=11, bold=True, color=POS, anchor="end"))

    f.append(line(80, gnd_y, 400, gnd_y, color=LINE, sw=2.0))
    f.append(text(65, gnd_y + 4, "GND (0В)", size=11, bold=True, color=LINE, anchor="end"))

    # Дільник зміщення
    # R_PU (Pull-Up на лінію A)
    # R_T (Термінатор між A і B)
    # R_PD (Pull-Down на лінію B)
    bx = 200
    y_a = 135
    y_b = 215

    # Лінії A і B
    f.append(line(120, y_a, 500, y_a, color=POS, sw=2.0))
    f.append(text(105, y_a + 4, "Лінія A (RX+)", size=11, bold=True, color=POS, anchor="end"))

    f.append(line(120, y_b, 500, y_b, color=NEG, sw=2.0))
    f.append(text(105, y_b + 4, "Лінія B (RX−)", size=11, bold=True, color=NEG, anchor="end"))

    # Резистор Pull-up (R_PU)
    f.append(line(bx, vcc_y, bx, y_a - 20, color=POS, sw=1.5))
    f.append(rect(bx - 12, y_a - 45, 24, 30, fill="#ffffff", stroke=POS, sw=1.5, rx=2))
    f.append(text(bx + 20, y_a - 30, "R_PU ≈ 560..1000 Ω", size=10, bold=True, color=POS, anchor="start"))
    f.append(line(bx, y_a - 15, bx, y_a, color=POS, sw=1.5))
    f.append(circle(bx, y_a, 3.5, fill=POS, stroke=POS))

    # Резистор термінування (R_T)
    f.append(line(bx, y_a, bx, y_a + 22, color=LINE, sw=1.5))
    f.append(rect(bx - 12, y_a + 22, 24, 35, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=2))
    f.append(text(bx + 20, y_a + 42, "R_T ≈ 120 Ω", size=10, bold=True, color="#d97706", anchor="start"))
    f.append(line(bx, y_a + 57, bx, y_b, color=LINE, sw=1.5))
    f.append(circle(bx, y_b, 3.5, fill=NEG, stroke=NEG))

    # Резистор Pull-down (R_PD)
    f.append(line(bx, y_b, bx, y_b + 20, color=NEG, sw=1.5))
    f.append(rect(bx - 12, y_b + 20, 24, 30, fill="#ffffff", stroke=NEG, sw=1.5, rx=2))
    f.append(text(bx + 20, y_b + 35, "R_PD ≈ 560..1000 Ω", size=10, bold=True, color=NEG, anchor="start"))
    f.append(line(bx, y_b + 50, bx, gnd_y, color=NEG, sw=1.5))

    # Приймач праворуч
    rx_x = 520
    f.append(rect(rx_x, 120, 160, 110, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    f.append(text(rx_x + 80, 142, "Диференційний", size=11, bold=True, color=NEG))
    f.append(text(rx_x + 80, 157, "приймач (RX)", size=11, bold=True, color=NEG))
    f.append(line(500, y_a, rx_x + 20, y_a, color=POS, sw=1.8))
    f.append(line(500, y_b, rx_x + 20, y_b, color=NEG, sw=1.8))

    # Вихід UART RX
    f.append(arrow(rx_x + 130, 175, rx_x + 175, 175, color=FIELD, sw=2.0))
    f.append(text(rx_x + 180, 179, "UART RX = 1 (Mark)", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(rx_x + 80, 205, "V_A − V_B ≥ +200 мВ", size=10, bold=True, color=FIELD))

    # Пояснення станів аварії
    f.append(rect(370, 260, 340, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(540, 280, "Результат Failsafe при обриві або IDLE:", size=10.5, bold=True, color=FIELD))
    f.append(text(540, 298, "• V_A утримується вище за V_B на ~200..300 мВ", size=9.5, color=INK))
    f.append(text(540, 314, "• Приймач надійно видає '1' (немає хибних старт-бітів)", size=9.5, color=INK))

    b, _, _ = textbox(W / 2, 385,
                      "Резистивний дільник R_PU / R_T / R_PD створює захисне зміщення > +200 мВ при відключеному драйвері, запобігаючи генерації сміття від наведеного шуму",
                      size=10.5, fill="#f8fafc", stroke="#94a3b8")
    f.append(b)

    render(os.path.join(IMG, "failsafe-biasing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_differential_levels()
    fig_four_wire_full_duplex()
    fig_multidrop_topology()
    fig_speed_vs_distance()
    fig_failsafe_biasing()
    print("OK: generated 5 RS-422 figures.")
