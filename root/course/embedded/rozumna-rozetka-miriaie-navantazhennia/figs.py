# -*- coding: utf-8 -*-
"""Фігури для статті rozumna-rozetka-miriaie-navantazhennia («Розумна розетка міряє навантаження»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. smart-plug-architecture: Загальна архітектура вимірювального тракту ───
def fig_smart_plug_architecture():
    W, H = 860, 440
    p = []

    # Заголовок та фон
    p.append(rect(20, 20, 820, 400, fill=FILL, stroke=LINE, sw=1.2, rx=6))

    # Секція високої напруги (230 В)
    p.append(rect(40, 50, 430, 350, fill="#fff5f5", stroke=POS, sw=1.6, rx=4))
    p.append(text(255, 75, "ВИСОКОВОЛЬТНА ЗОНА (МЕРЕЖА 230 В AC)", size=13, color=POS, bold=True))

    # Вхід мережі L і N
    p.append(line(50, 120, 110, 120, color=POS, sw=3))
    p.append(text(75, 110, "L (Фаза)", size=11, color=POS, bold=True))
    p.append(line(50, 320, 110, 320, color=NEG, sw=3))
    p.append(text(75, 340, "N (Нейтраль)", size=11, color=NEG, bold=True))

    # Реле комутації
    p.append(rect(110, 100, 60, 40, fill=BG, stroke=LINE, sw=1.5, rx=3))
    p.append(text(140, 125, "Реле", size=11, color=INK, bold=True))
    p.append(line(170, 120, 230, 120, color=POS, sw=3))

    # Манганіновий шунт (1 мОм)
    p.append(rect(230, 110, 60, 20, fill="#ffeaa7", stroke=POS, sw=1.8, rx=2))
    p.append(text(260, 124, "1 мОм", size=10, color=POS, bold=True))
    p.append(text(260, 98, "Шунт", size=11, color=POS, bold=True))
    p.append(line(290, 120, 390, 120, color=POS, sw=3))

    # Розетка / Навантаження
    p.append(rect(390, 100, 65, 240, fill=BG, stroke=LINE, sw=2, rx=4))
    p.append(text(422, 220, "НАВАНТАЖЕННЯ", size=10, color=INK, bold=True))
    p.append(line(110, 320, 390, 320, color=NEG, sw=3))

    # Дільник напруги (ланцюг 4x470 кОм)
    p.append(line(190, 120, 190, 180, color=POS, sw=1.4))
    p.append(rect(170, 180, 40, 70, fill="#f8efd6", stroke="#b8860b", sw=1.4, rx=2))
    p.append(text(190, 215, "4×470k", size=10, color="#b8860b", bold=True))
    p.append(text(190, 232, "+ 1k", size=10, color="#b8860b"))
    p.append(line(190, 250, 190, 290, color="#b8860b", sw=1.4))
    p.append(line(190, 290, 220, 290, color="#b8860b", sw=1.4))

    # Кельвінівські відводи від шунта
    p.append(line(240, 130, 240, 165, color=POS, sw=1.2, dash="3 2"))
    p.append(line(280, 130, 280, 165, color=POS, sw=1.2, dash="3 2"))
    p.append(line(240, 165, 270, 165, color=POS, sw=1.2))
    p.append(line(280, 165, 270, 175, color=POS, sw=1.2))

    # Вимірювальна мікросхема (HLW8032 / BL0942)
    p.append(rect(220, 260, 120, 90, fill="#e8f4f8", stroke="#2980b9", sw=1.8, rx=4))
    p.append(text(280, 285, "HLW8032 /", size=11, color="#2980b9", bold=True))
    p.append(text(280, 302, "BL0942", size=11, color="#2980b9", bold=True))
    p.append(text(280, 325, "ΣΔ АЦП + DSP", size=10, color=MUTED))

    # З'єднання шунта та дільника з мікросхемою
    p.append(line(270, 175, 270, 260, color=POS, sw=1.4))
    p.append(text(290, 215, "I_sense", size=10, color=POS))
    p.append(text(205, 275, "V_sense", size=10, color="#b8860b"))

    # Гальванічний бар'єр / Опторозв'язка
    p.append(line(490, 50, 490, 400, color=MUTED, sw=2, dash="6 4"))
    p.append(text(490, 40, "БАР'ЄР ІЗОЛЯЦІЇ (ОПТОРОЗВ'ЯЗКА)", size=11, color=MUTED, bold=True))

    # Оптопара
    p.append(rect(465, 280, 50, 45, fill=BG, stroke=FIELD, sw=1.5, rx=3))
    p.append(text(490, 305, "Оптопара", size=10, color=FIELD, bold=True))
    p.append(line(340, 300, 465, 300, color=FIELD, sw=1.5))
    p.append(text(400, 292, "UART TX", size=10, color=FIELD))

    # Низьковольтна безпечна зона (МК / Wi-Fi)
    p.append(rect(540, 50, 280, 350, fill="#f0fff4", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(680, 75, "БЕЗПЕЧНА ЗОНА (3.3 В DC)", size=13, color=FIELD, bold=True))

    # Мікроконтролер (ESP32)
    p.append(rect(570, 160, 120, 160, fill=BG, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(630, 190, "ESP32 / МК", size=13, color=FIELD, bold=True))
    p.append(text(630, 215, "Драйвер UART", size=10, color=INK))
    p.append(text(630, 235, "Облік кВт·год", size=10, color=INK))
    p.append(text(630, 255, "Wi-Fi / MQTT", size=10, color=INK))

    p.append(line(515, 300, 570, 300, color=FIELD, sw=1.5))
    p.append(text(542, 292, "RXD", size=10, color=FIELD))

    # Керування реле через оптопару
    p.append(line(570, 130, 490, 130, color=FIELD, sw=1.4))
    p.append(line(490, 130, 170, 130, color=FIELD, sw=1.4))
    p.append(text(525, 122, "Керування реле", size=10, color=FIELD))

    # Блок живлення (Flyback / Buck)
    p.append(rect(710, 280, 85, 70, fill=BG, stroke=LINE, sw=1.4, rx=3))
    p.append(text(752, 310, "AC-DC", size=11, color=INK, bold=True))
    p.append(text(752, 328, "3.3 В", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "smart-plug-architecture.svg"), W, H, *p,
           title="Архітектура вимірювального тракту розумної розетки")


# ── 2. shunt-vs-ct: Шунт проти трансформатора струму ──────────────────────────
def fig_shunt_vs_ct():
    W, H = 840, 400
    p = []

    # Ліва колонка: Резистивний шунт
    p.append(rect(30, 30, 370, 340, fill="#fffaf0", stroke="#b8860b", sw=1.6, rx=5))
    p.append(text(215, 60, "РЕЗИСТИВНИЙ ШУНТ (МАНГАНІН)", size=13, color="#b8860b", bold=True))

    # Силовий дріт і шунт
    p.append(line(50, 130, 130, 130, color=POS, sw=4))
    p.append(rect(130, 118, 70, 24, fill="#ffeaa7", stroke=POS, sw=2, rx=2))
    p.append(text(165, 134, "1–2 мОм", size=11, color=POS, bold=True))
    p.append(line(200, 130, 280, 130, color=POS, sw=4))
    p.append(text(260, 115, "I_нав (до 16 А)", size=10, color=POS))

    # Кельвінівські виводи
    p.append(line(140, 142, 140, 190, color="#b8860b", sw=1.5))
    p.append(line(190, 142, 190, 190, color="#b8860b", sw=1.5))
    p.append(circle(140, 190, 3, fill="#b8860b", stroke="#b8860b", sw=1))
    p.append(circle(190, 190, 3, fill="#b8860b", stroke="#b8860b", sw=1))
    p.append(text(165, 210, "U = I · R_shunt (±16–32 мВ)", size=10, color="#b8860b", bold=True))

    # Переваги та вади шунта
    b1, _, _ = textbox(215, 260, "Переваги:\n• Компактний SMD-розмір (2512/3920)\n• Немає фазового зсуву та насичення\n• Низька ціна ($0.05–0.15)",
                       size=10, color=INK, fill=BG, stroke="#b8860b", sw=1.2, min_w=330)
    p.append(b1)
    b2, _, _ = textbox(215, 335, "Вади: Немає ізоляції (потенціал 230 В),\nтеплові втрати P = I²·R (до 0.5 Вт при 16 А)",
                       size=10, color=POS, fill="#fff0f0", stroke=POS, sw=1.2, min_w=330)
    p.append(b2)

    # Права колонка: Трансформатор струму (CT)
    p.append(rect(440, 30, 370, 340, fill="#f0f7ff", stroke=NEG, sw=1.6, rx=5))
    p.append(text(625, 60, "ТРАНСФОРМАТОР СТРУМУ (CT)", size=13, color=NEG, bold=True))

    # Тороїдальне осердя та первинний провідник
    p.append(circle(550, 135, 38, fill="none", stroke="#555555", sw=10))
    p.append(circle(550, 135, 25, fill=BG, stroke=LINE, sw=1))
    p.append(circle(550, 135, 6, fill=POS, stroke=POS, sw=1))
    p.append(text(550, 105, "1 виток (L)", size=10, color=POS, bold=True))

    # Вторинна обмотка та навантажувальний резистор
    p.append(line(585, 125, 640, 125, color=NEG, sw=1.5))
    p.append(line(585, 145, 640, 145, color=NEG, sw=1.5))
    p.append(rect(640, 115, 25, 40, fill=BG, stroke=NEG, sw=1.5, rx=2))
    p.append(text(652, 138, "R_b", size=10, color=NEG, bold=True))
    p.append(text(690, 138, "N = 1:1000", size=10, color=NEG))

    # Небезпека розриву вторинної обмотки
    p.append(text(625, 200, "УВАГА: ОБРИВ R_b ПРИЗВОДИТЬ ДО ПРОБОЮ!", size=10, color=POS, bold=True))

    # Переваги та вади CT
    b3, _, _ = textbox(625, 260, "Переваги:\n• Повна гальванічна ізоляція (>2.5 кВ)\n• Мізерні теплові втрати на первинній лінії\n• Висока чутливість на малих струмах",
                       size=10, color=INK, fill=BG, stroke=NEG, sw=1.2, min_w=330)
    p.append(b3)
    b4, _, _ = textbox(625, 335, "Вади: Габарити осердя, фазовий зсув (1–3°),\nризик смертельної напруги при обриві R_b",
                       size=10, color=POS, fill="#fff0f0", stroke=POS, sw=1.2, min_w=330)
    p.append(b4)

    render(os.path.join(OUT, "shunt-vs-ct.svg"), W, H, *p,
           title="Порівняння первинних перетворювачів струму: резистивний шунт проти трансформатора струму")


# ── 3. voltage-divider-chain: Дільник напруги та безпека ─────────────────────
def fig_voltage_divider_chain():
    W, H = 840, 360
    p = []

    # Небезпечна схема: один резистор
    p.append(rect(30, 30, 370, 300, fill="#fff0f0", stroke=POS, sw=1.6, rx=4))
    p.append(text(215, 60, "ОДИН РЕЗИСТОР (НЕБЕЗПЕЧНО / ЗАБОРОНЕНО)", size=11, color=POS, bold=True))

    p.append(line(80, 110, 130, 110, color=POS, sw=2))
    p.append(text(105, 100, "230 В AC", size=10, color=POS, bold=True))
    p.append(rect(130, 95, 65, 30, fill=BG, stroke=POS, sw=1.8, rx=2))
    p.append(text(162, 114, "1 МОм", size=10, color=POS, bold=True))
    p.append(line(195, 110, 245, 110, color=POS, sw=2))

    # Іскра / Пробій
    p.append(line(140, 90, 180, 135, color=POS, sw=2, dash="3 2"))
    p.append(text(162, 80, "⚡ ПРОБІЙ ⚡", size=11, color=POS, bold=True))

    b_bad, _, _ = textbox(215, 210, "Чому 1 резистор (0805/1206) не підходить:\n• Робоча напруга 0805 — лише 150 В (пік мережі 325 В)\n• Імпульсні перенапруги CAT II (2.5 кВ) дають дугу\n• Пил та волога перекривають малий зазор 1.5 мм",
                          size=10, color=INK, fill=BG, stroke=POS, sw=1.2, min_w=330)
    p.append(b_bad)

    # Безпечна схема: ланцюг резисторів
    p.append(rect(430, 30, 380, 300, fill="#f0fff4", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(620, 60, "ПОСЛІДОВНИЙ ЛАНЦЮГ (НОРМА ДЛЯ CAT II)", size=11, color=FIELD, bold=True))

    p.append(line(455, 110, 475, 110, color=POS, sw=2))
    resistors = ["470k", "470k", "470k", "470k"]
    rx = 475
    for r_val in resistors:
        p.append(rect(rx, 98, 36, 24, fill=BG, stroke=FIELD, sw=1.4, rx=2))
        p.append(text(rx + 18, 114, r_val, size=9, color=FIELD, bold=True))
        p.append(line(rx + 36, 110, rx + 48, 110, color=FIELD, sw=1.4))
        rx += 48

    # Нижнє плече дільника
    p.append(line(rx, 110, rx + 15, 110, color=FIELD, sw=1.4))
    p.append(circle(rx + 15, 110, 3, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(rx + 15, 110, rx + 15, 140, color=FIELD, sw=1.4))
    p.append(rect(rx + 5, 140, 20, 26, fill=BG, stroke=FIELD, sw=1.4, rx=2))
    p.append(text(rx + 15, 156, "1k", size=9, color=FIELD, bold=True))
    p.append(line(rx + 15, 166, rx + 15, 185, color=NEG, sw=1.4))
    p.append(text(rx + 15, 198, "GND (N)", size=10, color=NEG, bold=True))

    p.append(line(rx + 15, 110, 755, 110, color=FIELD, sw=1.4))
    p.append(text(775, 114, "До АЦП", size=10, color=FIELD, bold=True))
    p.append(text(775, 128, "(±170 мВ)", size=9, color=MUTED))

    b_good, _, _ = textbox(620, 245, "Переваги ланцюга 4×470 кОм:\n• На кожному резисторі лише 80 В піку (безпечно)\n• Сумарний зазор по платі > 10 мм (захист від пробою)\n• Ослаблення 1:1881 перетворює 325 В у 172 мВ",
                           size=10, color=INK, fill=BG, stroke=FIELD, sw=1.2, min_w=340)
    p.append(b_good)

    render(os.path.join(OUT, "voltage-divider-chain.svg"), W, H, *p,
           title="Схемотехніка високовольтного дільника напруги мережі")


# ── 4. ac-power-components: Складові потужності та форми сигналів ─────────────
def fig_ac_power_components():
    W, H = 840, 420
    p = []

    # 1. Активне навантаження (Резистор, PF = 1.0)
    p.append(rect(30, 30, 240, 360, fill=BG, stroke="#c9d3dc", sw=1.4, rx=4))
    p.append(text(150, 55, "АКТИВНЕ (PF = 1.0)", size=12, color=FIELD, bold=True))
    p.append(text(150, 72, "Нагрівач, лампа розжарення", size=9, color=MUTED))

    ox1, oy1 = 50, 150
    p.append(line(ox1, oy1, ox1 + 200, oy1, color=MUTED, sw=1))
    pts_v, pts_i, pts_p = [], [], []
    for i in range(0, 101):
        t = i / 100.0 * 2 * math.pi
        v = math.sin(t)
        p_val = v * v  # p = v * i
        pts_v.append("%.1f,%.1f" % (ox1 + i * 2, oy1 - v * 40))
        pts_i.append("%.1f,%.1f" % (ox1 + i * 2, oy1 - v * 28))
        pts_p.append("%.1f,%.1f" % (ox1 + i * 2, oy1 - p_val * 40))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 2"/>' % (" ".join(pts_v), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"/>' % (" ".join(pts_i), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_p), FIELD))

    b_act, _, _ = textbox(150, 290, "• Струм у фазі з напругою (φ = 0)\n• Миттєва потужність завжди ≥ 0\n• Активна потужність P = V · I\n• Реактивна потужність Q = 0",
                          size=9, color=INK, fill="#f4faf6", stroke=FIELD, sw=1.0, min_w=210)
    p.append(b_act)

    # 2. Індуктивне навантаження (Двигун, PF = 0.7)
    p.append(rect(300, 30, 240, 360, fill=BG, stroke="#c9d3dc", sw=1.4, rx=4))
    p.append(text(420, 55, "ІНДУКТИВНЕ (PF = 0.7)", size=12, color="#b8860b", bold=True))
    p.append(text(420, 72, "Двигун, компресор, насос", size=9, color=MUTED))

    ox2, oy2 = 320, 150
    p.append(line(ox2, oy2, ox2 + 200, oy2, color=MUTED, sw=1))
    pts_v2, pts_i2, pts_p2 = [], [], []
    phi = math.pi / 4  # 45 deg
    for i in range(0, 101):
        t = i / 100.0 * 2 * math.pi
        v = math.sin(t)
        cur = math.sin(t - phi)
        p_val = v * cur
        pts_v2.append("%.1f,%.1f" % (ox2 + i * 2, oy2 - v * 40))
        pts_i2.append("%.1f,%.1f" % (ox2 + i * 2, oy2 - cur * 28))
        pts_p2.append("%.1f,%.1f" % (ox2 + i * 2, oy2 - p_val * 40))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 2"/>' % (" ".join(pts_v2), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"/>' % (" ".join(pts_i2), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_p2), "#b8860b"))

    b_ind, _, _ = textbox(420, 290, "• Струм відстає за фазою на кут φ\n• Частину періоду потужність < 0\n  (енергія повертається в мережу)\n• P = V·I·cos φ, Q = V·I·sin φ",
                          size=9, color=INK, fill="#fdfbf5", stroke="#b8860b", sw=1.0, min_w=210)
    p.append(b_ind)

    # 3. Нелінійне навантаження (Імпульсний БЖ, PF = 0.55)
    p.append(rect(570, 30, 240, 360, fill=BG, stroke="#c9d3dc", sw=1.4, rx=4))
    p.append(text(690, 55, "НЕЛІНІЙНЕ (PF = 0.55)", size=12, color=POS, bold=True))
    p.append(text(690, 72, "Імпульсний БЖ, LED-лампа", size=9, color=MUTED))

    ox3, oy3 = 590, 150
    p.append(line(ox3, oy3, ox3 + 200, oy3, color=MUTED, sw=1))
    pts_v3, pts_i3, pts_p3 = [], [], []
    for i in range(0, 101):
        t = i / 100.0 * 2 * math.pi
        v = math.sin(t)
        # Вузькі піки струму на вершинах напруги
        cur = math.pow(math.sin(t), 9) if abs(v) > 0.6 else 0
        p_val = v * cur
        pts_v3.append("%.1f,%.1f" % (ox3 + i * 2, oy3 - v * 40))
        pts_i3.append("%.1f,%.1f" % (ox3 + i * 2, oy3 - cur * 35))
        pts_p3.append("%.1f,%.1f" % (ox3 + i * 2, oy3 - p_val * 40))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 2"/>' % (" ".join(pts_v3), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_i3), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_p3), POS))

    b_non, _, _ = textbox(690, 290, "• Струм тече вузькими піками (діоди)\n• Фазового зсуву майже немає (cos φ ≈ 1),\n  але високі гармоніки (THD > 100%)\n• Повна потужність S² = P² + Q² + D²",
                          size=9, color=INK, fill="#fdf5f5", stroke=POS, sw=1.0, min_w=210)
    p.append(b_non)

    render(os.path.join(OUT, "ac-power-components.svg"), W, H, *p,
           title="Форми напруги, струму та миттєвої потужності при різних типах навантаження")


# ── 5. hlw8032-packet-flow: Формат кадру та обробка HLW8032 ──────────────────
def fig_hlw8032_packet_flow():
    W, H = 960, 390
    p = []

    # Структура 24-байтного кадру UART (4800 baud)
    p.append(rect(20, 20, 920, 165, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    p.append(text(480, 45, "СТРУКТУРА 24-БАЙТНОГО TELEMETRY-КАДРУ HLW8032 (UART 4800, 8E1)", size=12, color=INK, bold=True))

    fields = [
        ("0x55", "Синхро 1", POS, 52),
        ("0x5A", "Синхро 2", POS, 52),
        ("V_PARAM\n(3 байти)", "Опорна U", "#b8860b", 78),
        ("V_DATA\n(3 байти)", "Регістр U", "#b8860b", 78),
        ("I_PARAM\n(3 байти)", "Опорний I", NEG, 78),
        ("I_DATA\n(3 байти)", "Регістр I", NEG, 78),
        ("P_PARAM\n(3 байти)", "Опорна P", FIELD, 80),
        ("P_DATA\n(3 байти)", "Регістр P", FIELD, 80),
        ("STATUS\n(1 байт)", "Статус", MUTED, 64),
        ("PULSES\n(2 байти)", "Імпульси", MUTED, 70),
        ("CHKSUM\n(1 байт)", "Контроль", POS, 70),
    ]

    cur_x = 35
    for name, desc, col, width in fields:
        p.append(rect(cur_x, 70, width, 45, fill=BG, stroke=col, sw=1.4, rx=2))
        p.append(mtext(cur_x + width / 2, 88, name, size=9, color=col, bold=True, lh=1.1))
        p.append(text(cur_x + width / 2, 134, desc, size=9, color=MUTED))
        cur_x += width + 6

    # Формули перерахунку фізичних величин
    p.append(rect(20, 205, 920, 165, fill=BG, stroke="#c9d3dc", sw=1.4, rx=4))
    p.append(text(480, 228, "АЛГОРИТМ ОБЧИСЛЕННЯ ФІЗИЧНИХ ВЕЛИЧИН У ДРАЙВЕРІ", size=12, color=INK, bold=True))

    b_u, _, _ = textbox(180, 295, "НАПРУГА U_rms:\nU = (V_PARAM / V_DATA) · K_u\n(K_u ≈ 1.881 — коеф. дільника)",
                        size=10, color=INK, fill="#fdfbf5", stroke="#b8860b", sw=1.2, min_w=250)
    p.append(b_u)

    b_i, _, _ = textbox(480, 295, "СТРУМ I_rms:\nI = (I_PARAM / I_DATA) · K_i\n(K_i ≈ 1.0 / R_shunt)",
                        size=10, color=INK, fill="#f0f7ff", stroke=NEG, sw=1.2, min_w=250)
    p.append(b_i)

    b_p, _, _ = textbox(780, 295, "ПОТУЖНІСТЬ P_act:\nP = (P_PARAM / P_DATA) · K_u · K_i\n(Оновлення кожні 50 мс)",
                        size=10, color=INK, fill="#f4faf6", stroke=FIELD, sw=1.2, min_w=250)
    p.append(b_p)

    render(os.path.join(OUT, "hlw8032-packet-flow.svg"), W, H, *p,
           title="Формат кадру UART та формули перерахунку мікросхеми HLW8032")


# ── 6. calibration-curve: Двоточкове калібрування ─────────────────────────────
def fig_calibration_curve():
    W, H = 820, 360
    p = []

    # Графік калібрувальної кривої
    ox, oy = 90, 280
    aw, ah = 360, 200

    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.6))
    p.append(text(ox + aw + 10, oy + 20, "Еталонне значення (В, А, Вт)", size=10, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 10, oy - ah - 10, "Показники АЦП / Регістрів", size=10, color=INK, bold=True, anchor="end"))

    # Некалібрована лінія (зміщення + похибка нахилу)
    p.append(line(ox, oy - 20, ox + aw, oy - ah + 20, color=POS, sw=1.8, dash="5 3"))
    p.append(text(ox + aw - 10, oy - ah + 10, "Сира крива (похибка ±5%)", size=9, color=POS, bold=True))

    # Калібрована лінія (ідеальна пряма)
    p.append(line(ox, oy, ox + aw, oy - ah, color=FIELD, sw=2.2))
    p.append(text(ox + aw - 10, oy - ah - 10, "Калібрована характеристика", size=9, color=FIELD, bold=True))

    # Точка 1: Нульове навантаження (Offset)
    p.append(circle(ox, oy - 20, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(ox + 45, oy - 12, "Точка 1 (Offset)", size=9, color=POS, bold=True))

    # Точка 2: Опорне навантаження (Gain)
    tx2, ty2 = ox + aw * 0.75, oy - ah * 0.75 - 10
    p.append(circle(tx2, ty2, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(tx2 + 10, ty2 + 15, "Точка 2 (Еталон 1000 Вт)", size=9, color=POS, bold=True))

    # Пояснювальний блок праворуч
    b_cal, _, _ = textbox(625, 180, "ЕТАПИ КАЛІБРУВАННЯ РОЗЕТКИ:\n\n1. Калібрування зміщення (Offset):\n   • Без навантаження (I = 0 А)\n   • Відтинання шумової «полиці» АЦП\n\n2. Калібрування масштабу (Gain):\n   • Підключення еталонного нагрівача (1000 Вт)\n   • Розрахунок коефіцієнтів K_v, K_i, K_p\n\n3. Фазове калібрування (Phase Lag):\n   • Індуктивне навантаження (PF = 0.5)\n   • Компенсація зсуву фази в регістрі DSP",
                          size=10, color=INK, fill=FILL, stroke=LINE, sw=1.4, min_w=320)
    p.append(b_cal)

    render(os.path.join(OUT, "calibration-curve.svg"), W, H, *p,
           title="Методика двоточкового калібрування енергомонітора")


def main():
    fig_smart_plug_architecture()
    fig_shunt_vs_ct()
    fig_voltage_divider_chain()
    fig_ac_power_components()
    fig_hlw8032_packet_flow()
    fig_calibration_curve()
    print("Всі 6 фігур успішно згенеровано у ./img/")

if __name__ == "__main__":
    main()
