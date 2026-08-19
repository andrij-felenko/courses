# -*- coding: utf-8 -*-
"""Фігури для теми power-rail-sequencing (Секвенування шин живлення).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_latchup_mechanism():
    """Паразитна чотиришарова структура p-n-p-n у КМОН-кристалі між доменами живлення."""
    W, H = 820, 500
    frags = []

    # Заголовок блоку структури кремнію
    frags.append(rect(40, 30, 740, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # N-підкладка / N-substrate (основа)
    frags.append(rect(60, 80, 700, 190, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    frags.append(text(80, 255, "N-підкладка (N-substrate, підключена до VDD_IO = 3.3 В)", size=12, color=INK, bold=True, anchor="start"))

    # P-кишеня / P-well (для домену ядра)
    frags.append(rect(380, 80, 360, 150, fill="#fed7aa", stroke="#f97316", sw=1.5, rx=4))
    frags.append(text(400, 215, "P-кишеня (P-well, підключена до GND)", size=12, color="#9a3412", bold=True, anchor="start"))

    # Дифузійні області P+ та N+
    # Домен 3.3 В (зліва)
    frags.append(rect(90, 80, 75, 45, fill="#fca5a5", stroke=POS, sw=1.5, rx=3))
    frags.append(text(127, 108, "P+ (I/O)", size=11, color=POS, bold=True))
    frags.append(text(127, 55, "+3.3 В (I/O)", size=12, color=POS, bold=True))
    frags.append(line(127, 60, 127, 80, color=POS, sw=2))

    frags.append(rect(190, 80, 75, 45, fill="#bfdbfe", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(227, 108, "N+ (Sub)", size=11, color=NEG, bold=True))

    # Домен ядра 0.8 В (справа)
    frags.append(rect(420, 80, 75, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    frags.append(text(457, 108, "P+ (Well)", size=11, color="#ea580c", bold=True))

    frags.append(rect(520, 80, 75, 45, fill="#bfdbfe", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(557, 108, "N+ (Core)", size=11, color=NEG, bold=True))
    frags.append(text(557, 55, "GND / 0.8 В", size=12, color=NEG, bold=True))
    frags.append(line(557, 60, 557, 80, color=NEG, sw=2))

    # Схема еквівалентних паразитних транзисторів PNP та NPN поверх кристала
    # PNP транзистор (емітер P+ 3.3V, база N-sub, колектор P-well)
    frags.append(circle(270, 160, 18, fill="#fee2e2", stroke=POS, sw=1.8))
    frags.append(text(270, 165, "Q_pnp", size=11, color=POS, bold=True))
    frags.append(line(165, 125, 255, 150, color=POS, sw=1.8)) # Емітер
    frags.append(line(227, 125, 270, 142, color=POS, sw=1.5)) # База з N-sub

    # NPN транзистор (емітер N+ Core, база P-well, колектор N-sub)
    frags.append(circle(480, 160, 18, fill="#dbeafe", stroke=NEG, sw=1.8))
    frags.append(text(480, 165, "Q_npn", size=11, color=NEG, bold=True))
    frags.append(line(520, 125, 495, 150, color=NEG, sw=1.8)) # Емітер NPN
    frags.append(line(457, 125, 470, 145, color=NEG, sw=1.5)) # База з P-well

    # Перехресні зв'язки тиристора (регенеративна петля)
    frags.append(arrow(288, 160, 462, 160, color=POS, sw=2)) # Колектор PNP живить базу NPN
    frags.append(arrow(470, 175, 280, 175, color=NEG, sw=2)) # Колектор NPN тягне базу PNP

    # Текстові пояснення внизу
    box_l, _, _ = textbox(230, 395, [
        "Небезпечний стан пуску:",
        "1) Шина 3.3 В ввімкнулась першою",
        "2) Шина ядра 0.8 В ще на 0 В",
        "3) Прямий струм ESD-діодів у підкладку",
        "4) Інжекція дірок відмикає пару Q_pnp / Q_npn"
    ], size=12, fill="#fff1f2", stroke="#f43f5e", min_w=340)
    frags.append(box_l)

    box_r, _, _ = textbox(590, 395, [
        "Наслідок: Тиристорний защіп",
        "• Регенеративна умова: β1 · β2 ≥ 1",
        "• Пряме коротке замикання 3.3 В на GND",
        "• Струм крізь підкладку сягає 5–15 А",
        "• Теплове руйнування кристала чипа"
    ], size=12, fill="#fef2f2", stroke=POS, min_w=340)
    frags.append(box_r)

    render(os.path.join(OUT, "latchup-mechanism.svg"), W, H, *frags,
           title="Механізм паразитного тиристорного защіпу (Latch-up) у багатодоменному чипі")


def fig_sequencing_types():
    """Порівняння трьох фундаментальних типів секвенування пуску."""
    W, H = 840, 500
    frags = []

    # Три колонки для трьох типів
    cols = [
        {"title": "1. Послідовне (Cascade)", "cx": 150, "x0": 40, "w": 230},
        {"title": "2. Пропорційне (Ratiometric)", "cx": 420, "x0": 310, "w": 230},
        {"title": "3. Фіксований зсув (Offset)", "cx": 690, "x0": 580, "w": 230}
    ]

    for col in cols:
        frags.append(rect(col["x0"], 25, col["w"], 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(col["cx"], 50, col["title"], size=13, color=INK, bold=True))

    # --- 1. Послідовне ---
    # Графік: V1 (Core 0.85V), V2 (Aux 1.8V), V3 (IO 3.3V)
    g1_x, g1_y, g1_w, g1_h = 60, 230, 190, 140
    frags.append(line(g1_x, g1_y + g1_h, g1_x + g1_w, g1_y + g1_h, color=LINE, sw=1.5)) # вісь t
    frags.append(line(g1_x, g1_y, g1_x, g1_y + g1_h, color=LINE, sw=1.5)) # вісь V
    frags.append(text(g1_x + g1_w, g1_y + g1_h + 18, "t", size=12, color=MUTED))
    frags.append(text(g1_x - 10, g1_y + 10, "V", size=12, color=MUTED))

    # V1 (Core 0.85V) - стартує першою
    frags.append(line(g1_x, g1_y + g1_h, g1_x + 30, g1_y + g1_h, color=NEG, sw=2))
    frags.append(line(g1_x + 30, g1_y + g1_h, g1_x + 60, g1_y + g1_h - 40, color=NEG, sw=2.5))
    frags.append(line(g1_x + 60, g1_y + g1_h - 40, g1_x + g1_w, g1_y + g1_h - 40, color=NEG, sw=2.5))
    frags.append(text(g1_x + g1_w - 5, g1_y + g1_h - 46, "0.85 В", size=11, color=NEG, bold=True, anchor="end"))

    # V2 (Aux 1.8V) - стартує після PG1
    frags.append(line(g1_x, g1_y + g1_h, g1_x + 75, g1_y + g1_h, color=FIELD, sw=2))
    frags.append(line(g1_x + 75, g1_y + g1_h, g1_x + 115, g1_y + g1_h - 80, color=FIELD, sw=2.5))
    frags.append(line(g1_x + 115, g1_y + g1_h - 80, g1_x + g1_w, g1_y + g1_h - 80, color=FIELD, sw=2.5))
    frags.append(text(g1_x + g1_w - 5, g1_y + g1_h - 86, "1.8 В", size=11, color=FIELD, bold=True, anchor="end"))

    # V3 (IO 3.3V) - стартує після PG2
    frags.append(line(g1_x, g1_y + g1_h, g1_x + 130, g1_y + g1_h, color=POS, sw=2))
    frags.append(line(g1_x + 130, g1_y + g1_h, g1_x + 175, g1_y + g1_h - 130, color=POS, sw=2.5))
    frags.append(line(g1_x + 175, g1_y + g1_h - 130, g1_x + g1_w, g1_y + g1_h - 130, color=POS, sw=2.5))
    frags.append(text(g1_x + g1_w - 5, g1_y + g1_h - 134, "3.3 В", size=11, color=POS, bold=True, anchor="end"))

    box1, _, _ = textbox(155, 130, [
        "Черговий канал стартує",
        "тільки після сигналу",
        "Power Good (PG)",
        "попереднього каналу.",
        "Гарантія: Core перше"
    ], size=11, fill="#f1f5f9", stroke="#94a3b8", min_w=200)
    frags.append(box1)

    # --- 2. Пропорційне ---
    g2_x, g2_y, g2_w, g2_h = 330, 230, 190, 140
    frags.append(line(g2_x, g2_y + g2_h, g2_x + g2_w, g2_y + g2_h, color=LINE, sw=1.5))
    frags.append(line(g2_x, g2_y, g2_x, g2_y + g2_h, color=LINE, sw=1.5))
    frags.append(text(g2_x + g2_w, g2_y + g2_h + 18, "t", size=12, color=MUTED))

    # Усі стартують в t=30 і закінчують в t=150
    t_st = g2_x + 30
    t_end = g2_x + 150
    frags.append(line(g2_x, g2_y + g2_h, t_st, g2_y + g2_h, color=LINE, sw=1))
    frags.append(line(t_st, g2_y + g2_h, t_end, g2_y + g2_h - 40, color=NEG, sw=2.5)) # 0.85V
    frags.append(line(t_end, g2_y + g2_h - 40, g2_x + g2_w, g2_y + g2_h - 40, color=NEG, sw=2.5))

    frags.append(line(t_st, g2_y + g2_h, t_end, g2_y + g2_h - 80, color=FIELD, sw=2.5)) # 1.8V
    frags.append(line(t_end, g2_y + g2_h - 80, g2_x + g2_w, g2_y + g2_h - 80, color=FIELD, sw=2.5))

    frags.append(line(t_st, g2_y + g2_h, t_end, g2_y + g2_h - 130, color=POS, sw=2.5)) # 3.3V
    frags.append(line(t_end, g2_y + g2_h - 130, g2_x + g2_w, g2_y + g2_h - 130, color=POS, sw=2.5))

    box2, _, _ = textbox(425, 130, [
        "Усі шини вмикаються",
        "одночасно і досягають",
        "100% за однаковий час.",
        "Швидкість dV/dt пропор-",
        "ційна номіналу напруги"
    ], size=11, fill="#f1f5f9", stroke="#94a3b8", min_w=200)
    frags.append(box2)

    # --- 3. Фіксований зсув ---
    g3_x, g3_y, g3_w, g3_h = 600, 230, 190, 140
    frags.append(line(g3_x, g3_y + g3_h, g3_x + g3_w, g3_y + g3_h, color=LINE, sw=1.5))
    frags.append(line(g3_x, g3_y, g3_x, g3_y + g3_h, color=LINE, sw=1.5))
    frags.append(text(g3_x + g3_w, g3_y + g3_h + 18, "t", size=12, color=MUTED))

    # Усі ростуть паралельно з однаковим dV/dt і зсувом ΔV
    frags.append(line(g3_x + 20, g3_y + g3_h, g3_x + 60, g3_y + g3_h - 40, color=NEG, sw=2.5))
    frags.append(line(g3_x + 60, g3_y + g3_h - 40, g3_x + g3_w, g3_y + g3_h - 40, color=NEG, sw=2.5))

    frags.append(line(g3_x + 35, g3_y + g3_h, g3_x + 115, g3_y + g3_h - 80, color=FIELD, sw=2.5))
    frags.append(line(g3_x + 115, g3_y + g3_h - 80, g3_x + g3_w, g3_y + g3_h - 80, color=FIELD, sw=2.5))

    frags.append(line(g3_x + 50, g3_y + g3_h, g3_x + 180, g3_y + g3_h - 130, color=POS, sw=2.5))
    frags.append(line(g3_x + 180, g3_y + g3_h - 130, g3_x + g3_w, g3_y + g3_h - 130, color=POS, sw=2.5))

    # Стрілка різниці ΔV
    frags.append(line(g3_x + 70, g3_y + g3_h - 50, g3_x + 70, g3_y + g3_h - 20, color=POS, sw=1.5))
    frags.append(text(g3_x + 85, g3_y + g3_h - 35, "ΔV", size=11, color=POS, bold=True))

    box3, _, _ = textbox(695, 130, [
        "Різниця напруг ΔV",
        "суворо обмежена",
        "(наприклад, ≤ 0.4 В).",
        "Однаковий нахил dV/dt,",
        "захист переходів"
    ], size=11, fill="#f1f5f9", stroke="#94a3b8", min_w=200)
    frags.append(box3)

    # Підсумковий рядок внизу
    frags.append(rect(40, 420, 760, 50, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    frags.append(text(420, 450, "Вибір типу визначається даташитом SoC: для FPGA стандарт — послідовний або відстежуваний пуск", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "sequencing-types.svg"), W, H, *frags,
           title="Типи послідовностей секвенування шин живлення: послідовне, пропорційне, з фіксованим зсувом")


def fig_power_down_active_discharge():
    """Секвенування вимкнення: пасивний розряд проти реверсивного LIFO з активним розрядом."""
    W, H = 820, 460
    frags = []

    # Ліва половина: Пасивний неконтрольований розряд (Небезпека)
    frags.append(rect(40, 40, 360, 390, fill="#fff1f2", stroke="#fecdd3", sw=1.5, rx=6))
    frags.append(text(220, 70, "Пасивне вимкнення (Аварійний ризик)", size=13, color=POS, bold=True))

    g_l_x, g_l_y, g_l_w, g_l_h = 70, 200, 300, 140
    frags.append(line(g_l_x, g_l_y + g_l_h, g_l_x + g_l_w, g_l_y + g_l_h, color=LINE, sw=1.5))
    frags.append(line(g_l_x, g_l_y, g_l_x, g_l_y + g_l_h, color=LINE, sw=1.5))
    frags.append(text(g_l_x + g_l_w - 5, g_l_y + g_l_h + 18, "t", size=12, color=MUTED))

    # Вимикання живлення в t=40
    frags.append(line(g_l_x + 40, g_l_y, g_l_x + 40, g_l_y + g_l_h, color=POS, sw=1.5, dash="4,3"))
    frags.append(text(g_l_x + 40, g_l_y - 10, "Power Off", size=11, color=POS, bold=True))

    # Core (0.85V) падає миттєво через струм навантаження 15А
    frags.append(line(g_l_x, g_l_y + g_l_h - 40, g_l_x + 40, g_l_y + g_l_h - 40, color=NEG, sw=2.5))
    frags.append(line(g_l_x + 40, g_l_y + g_l_h - 40, g_l_x + 55, g_l_y + g_l_h, color=NEG, sw=2.5))
    frags.append(line(g_l_x + 55, g_l_y + g_l_h, g_l_x + g_l_w, g_l_y + g_l_h, color=NEG, sw=2.5))
    frags.append(text(g_l_x + 35, g_l_y + g_l_h - 46, "Core 0.85 В", size=11, color=NEG, bold=True))

    # I/O (3.3V) розряджається повільно через велику ємність Cout та малий струм спокою
    frags.append(line(g_l_x, g_l_y + g_l_h - 130, g_l_x + 40, g_l_y + g_l_h - 130, color=POS, sw=2.5))
    # експонента розряду
    pts_io = []
    for k in range(50):
        t_cur = 40 + k * 4
        v_cur = 130 * (0.95 ** k)
        pts_io.append("%.1f,%.1f" % (g_l_x + t_cur, g_l_y + g_l_h - v_cur))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_io), POS))
    frags.append(text(g_l_x + 120, g_l_y + g_l_h - 100, "I/O 3.3 В висить!", size=11, color=POS, bold=True))

    # Зона небезпеки інверсії напруг
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="rgba(239, 68, 68, 0.15)" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3" rx="4"/>' % (g_l_x + 55, g_l_y + g_l_h - 120, 160, 115, POS))
    frags.append(text(g_l_x + 135, g_l_y + g_l_h - 20, "Небезпечний перекіс: V_IO > V_CORE", size=10, color=POS, bold=True))

    box_pass, _, _ = textbox(220, 125, [
        "Без примусового розряду:",
        "Core падає за мікросекунди,",
        "а I/O тримає заряд секундами.",
        "Ризик тиристорного защіпу при вимкненні!"
    ], size=11, fill="#fff", stroke=POS, min_w=310)
    frags.append(box_pass)

    # Права половина: Реверсивне вимкнення LIFO з Active Output Discharge
    frags.append(rect(420, 40, 360, 390, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=6))
    frags.append(text(600, 70, "Активне секвенування LIFO + Discharge", size=13, color=FIELD, bold=True))

    g_r_x, g_r_y, g_r_w, g_r_h = 450, 200, 300, 140
    frags.append(line(g_r_x, g_r_y + g_r_h, g_r_x + g_r_w, g_r_y + g_r_h, color=LINE, sw=1.5))
    frags.append(line(g_r_x, g_r_y, g_r_x, g_r_y + g_r_h, color=LINE, sw=1.5))
    frags.append(text(g_r_x + g_r_w - 5, g_r_y + g_r_h + 18, "t", size=12, color=MUTED))

    frags.append(line(g_r_x + 30, g_r_y, g_r_x + 30, g_r_y + g_r_h, color=FIELD, sw=1.5, dash="4,3"))

    # I/O 3.3V вимикається першою і активно розряджається ключем NMOS R_dis
    frags.append(line(g_r_x, g_r_y + g_r_h - 130, g_r_x + 30, g_r_y + g_r_h - 130, color=POS, sw=2.5))
    frags.append(line(g_r_x + 30, g_r_y + g_r_h - 130, g_r_x + 75, g_r_y + g_r_h, color=POS, sw=2.5))
    frags.append(text(g_r_x + 95, g_r_y + g_r_h - 110, "1) Розряд I/O", size=11, color=POS, bold=True))

    # Aux 1.8V вимикається другою
    frags.append(line(g_r_x, g_r_y + g_r_h - 80, g_r_x + 80, g_r_y + g_r_h - 80, color=FIELD, sw=2.5))
    frags.append(line(g_r_x + 80, g_r_y + g_r_h - 80, g_r_x + 130, g_r_y + g_r_h, color=FIELD, sw=2.5))
    frags.append(text(g_r_x + 155, g_r_y + g_r_h - 65, "2) Розряд Aux", size=11, color=FIELD, bold=True))

    # Core 0.85V вимикається останньою
    frags.append(line(g_r_x, g_r_y + g_r_h - 40, g_r_x + 135, g_r_y + g_r_h - 40, color=NEG, sw=2.5))
    frags.append(line(g_r_x + 135, g_r_y + g_r_h - 40, g_r_x + 175, g_r_y + g_r_h, color=NEG, sw=2.5))
    frags.append(text(g_r_x + 205, g_r_y + g_r_h - 30, "3) Core вимикається останньою", size=11, color=NEG, bold=True))

    box_act, _, _ = textbox(600, 125, [
        "Керований LIFO-порядок:",
        "Шина I/O гаситься першою через",
        "активний ключ розряду R_dis (50 Ом).",
        "Core підтримується до повного зняття I/O"
    ], size=11, fill="#fff", stroke=FIELD, min_w=310)
    frags.append(box_act)

    render(os.path.join(OUT, "power-down-active-discharge.svg"), W, H, *frags,
           title="Секвенування вимкнення: пасивний розряд проти реверсивного порядку LIFO з активним розрядом")


def fig_cascade_pg_circuit():
    """Схемотехніка каскадного секвенування на базі сигналів Power Good (PG) та входу Enable (EN)."""
    W, H = 820, 420
    frags = []

    # Головна лінія живлення VIN
    frags.append(line(40, 60, 780, 60, color=POS, sw=3))
    frags.append(text(50, 50, "VIN (+12 В)", size=13, color=POS, bold=True, anchor="start"))

    # Блок 1: DC-DC Core (0.85 В)
    frags.append(rect(70, 110, 180, 180, fill="#f8fafc", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(160, 135, "DC-DC 1: Core", size=13, color=NEG, bold=True))
    frags.append(text(160, 155, "0.85 В / 25 А", size=11, color=MUTED))
    frags.append(line(160, 60, 160, 110, color=POS, sw=2)) # Вхід VIN
    frags.append(arrow(40, 200, 70, 200, color=LINE, sw=2)) # Головний EN
    frags.append(text(55, 190, "EN_MAIN", size=10, color=LINE, bold=True))
    frags.append(arrow(250, 200, 310, 200, color=FIELD, sw=2)) # Вихід PG1
    frags.append(text(280, 190, "PG1", size=11, color=FIELD, bold=True))
    frags.append(arrow(160, 290, 160, 350, color=NEG, sw=2.5)) # Вихід VOUT1
    frags.append(text(160, 370, "VCCINT (0.85 В)", size=12, color=NEG, bold=True))

    # RC-ланка затримки між PG1 та EN2
    frags.append(circle(330, 200, 4, fill=FIELD, stroke=FIELD))
    frags.append(line(330, 200, 330, 140, color=MUTED, sw=1.5))
    frags.append(rect(320, 110, 20, 30, fill="#fff", stroke=MUTED, sw=1.2)) # Pull-up R
    frags.append(text(355, 125, "R_pu", size=10, color=MUTED))
    frags.append(line(330, 110, 330, 80, color=POS, sw=1.2))
    frags.append(circle(330, 80, 3, fill=POS, stroke=POS))

    frags.append(line(330, 200, 330, 240, color=MUTED, sw=1.5))
    frags.append(line(320, 240, 340, 240, color=MUTED, sw=1.5)) # C_delay
    frags.append(line(320, 245, 340, 245, color=MUTED, sw=1.5))
    frags.append(line(330, 245, 330, 265, color=MUTED, sw=1.5)) # GND
    frags.append(text(355, 245, "C_del", size=10, color=MUTED))

    # Блок 2: DC-DC Aux (1.8 В)
    frags.append(rect(370, 110, 180, 180, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(460, 135, "DC-DC 2: Aux", size=13, color=FIELD, bold=True))
    frags.append(text(460, 155, "1.8 В / 4 А", size=11, color=MUTED))
    frags.append(line(460, 60, 460, 110, color=POS, sw=2)) # Вхід VIN
    frags.append(arrow(330, 200, 370, 200, color=FIELD, sw=2)) # Вхід EN2
    frags.append(text(385, 190, "EN2", size=10, color=FIELD, bold=True))
    frags.append(arrow(550, 200, 610, 200, color=POS, sw=2)) # Вихід PG2
    frags.append(text(580, 190, "PG2", size=11, color=POS, bold=True))
    frags.append(arrow(460, 290, 460, 350, color=FIELD, sw=2.5)) # Вихід VOUT2
    frags.append(text(460, 370, "VCCAUX (1.8 В)", size=12, color=FIELD, bold=True))

    # Блок 3: DC-DC I/O (3.3 В)
    frags.append(rect(630, 110, 160, 180, fill="#f8fafc", stroke=POS, sw=1.8, rx=6))
    frags.append(text(710, 135, "DC-DC 3: I/O", size=13, color=POS, bold=True))
    frags.append(text(710, 155, "3.3 В / 6 А", size=11, color=MUTED))
    frags.append(line(710, 60, 710, 110, color=POS, sw=2)) # Вхід VIN
    frags.append(arrow(610, 200, 630, 200, color=POS, sw=2)) # Вхід EN3
    frags.append(text(645, 190, "EN3", size=10, color=POS, bold=True))
    frags.append(arrow(710, 290, 710, 350, color=POS, sw=2.5)) # Вихід VOUT3
    frags.append(text(710, 370, "VCCO (3.3 В)", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "cascade-pg-circuit.svg"), W, H, *frags,
           title="Апаратна реалізація каскадного секвенування: ланцюг Power Good -> Enable")


if __name__ == "__main__":
    fig_latchup_mechanism()
    fig_sequencing_types()
    fig_power_down_active_discharge()
    fig_cascade_pg_circuit()
    print("ok figs")
