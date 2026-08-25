# -*- coding: utf-8 -*-
"""Фігури для теми forced-commutation (примусова комутація тиристора).
svgkit імпортуємо зі scripts/, вивід у ./img/.

    python figs.py
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

COILC = "#8a6d1f"


def fig_parallel_capacitor():
    """Паралельна ємнісна комутація: принципова схема та часова діаграма напруги на аноді T1."""
    W, H = 880, 420
    f = []

    # Ліва половина — принципова схема
    x_sch = 30
    w_sch = 380
    f.append(rect(x_sch, 45, w_sch, 355, fill="#fdfdfd", stroke=MUTED, sw=1.2))
    f.append(text(x_sch + w_sch / 2, 70, "Паралельна ємнісна схема", size=15, color=INK, bold=True))

    # Шини живлення схеми
    v_top = 110
    v_bot = 350
    f.append(line(x_sch + 30, v_top, x_sch + w_sch - 30, v_top, color=POS, sw=2.2))
    f.append(text(x_sch + 40, v_top - 10, "+Vs (DC)", size=12, color=POS, bold=True, anchor="start"))

    f.append(line(x_sch + 30, v_bot, x_sch + w_sch - 30, v_bot, color=NEG, sw=2.2))
    f.append(text(x_sch + 40, v_bot + 20, "0 В (GND)", size=12, color=NEG, bold=True, anchor="start"))

    # Гілка 1: Навантаження R_L + Головний тиристор T1
    x_g1 = x_sch + 110
    f.append(line(x_g1, v_top, x_g1, v_top + 30, color=LINE, sw=1.8))
    # Резистор навантаження
    f.append(rect(x_g1 - 16, v_top + 30, 32, 45, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x_g1, v_top + 57, "RL", size=12, bold=True))
    f.append(text(x_g1 - 24, v_top + 57, "IL", size=11, color=POS, anchor="end"))
    f.append(arrow(x_g1 - 6, v_top + 20, x_g1 - 6, v_top + 28, color=POS, sw=1.5))

    node_a1_y = v_top + 115
    f.append(line(x_g1, v_top + 75, x_g1, node_a1_y, color=LINE, sw=1.8))
    f.append(circle(x_g1, node_a1_y, 4, fill=LINE, stroke=LINE))
    f.append(text(x_g1 - 10, node_a1_y - 8, "A1", size=12, bold=True, anchor="end"))

    # Тиристор T1 (символ у блоку)
    t1_box = fitbox(x_g1 - 25, node_a1_y + 15, 50, 50, "T1\n(головний)", size=11, bold=True, fill="#eef2f7", stroke=LINE)
    f.append(t1_box)
    f.append(line(x_g1, node_a1_y, x_g1, node_a1_y + 15, color=LINE, sw=1.8))
    f.append(line(x_g1, node_a1_y + 65, x_g1, v_bot, color=LINE, sw=1.8))

    # Гілка 2: Зарядний резистор Rc + Допоміжний тиристор T2
    x_g2 = x_sch + 270
    f.append(line(x_g2, v_top, x_g2, v_top + 30, color=LINE, sw=1.8))
    f.append(rect(x_g2 - 16, v_top + 30, 32, 45, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x_g2, v_top + 57, "Rc", size=12, bold=True))

    node_a2_y = node_a1_y
    f.append(line(x_g2, v_top + 75, x_g2, node_a2_y, color=LINE, sw=1.8))
    f.append(circle(x_g2, node_a2_y, 4, fill=LINE, stroke=LINE))
    f.append(text(x_g2 + 10, node_a2_y - 8, "A2", size=12, bold=True, anchor="start"))

    # Допоміжний тиристор T2
    t2_box = fitbox(x_g2 - 25, node_a2_y + 15, 50, 50, "T2\n(допоміж.)", size=10, bold=True, fill="#fff4e6", stroke=LINE)
    f.append(t2_box)
    f.append(line(x_g2, node_a2_y, x_g2, node_a2_y + 15, color=LINE, sw=1.8))
    f.append(line(x_g2, node_a2_y + 65, x_g2, v_bot, color=LINE, sw=1.8))

    # Комутуючий конденсатор C між A1 та A2
    f.append(line(x_g1, node_a1_y, x_g1 + 55, node_a1_y, color=LINE, sw=1.8))
    f.append(line(x_g2, node_a2_y, x_g2 - 55, node_a2_y, color=LINE, sw=1.8))
    # пластини конденсатора
    c_mid_x = (x_g1 + x_g2) / 2
    f.append(line(c_mid_x - 5, node_a1_y - 16, c_mid_x - 5, node_a1_y + 16, color=LINE, sw=2.4))
    f.append(line(c_mid_x + 5, node_a2_y - 16, c_mid_x + 5, node_a2_y + 16, color=LINE, sw=2.4))
    f.append(text(c_mid_x, node_a1_y - 24, "C", size=13, bold=True))
    f.append(text(c_mid_x - 14, node_a1_y - 6, "−", size=14, color=NEG, bold=True))
    f.append(text(c_mid_x + 14, node_a2_y - 6, "+", size=14, color=POS, bold=True))

    # Права половина — часові діаграми напруги v_A1(t)
    x_dia = 440
    w_dia = 410
    f.append(rect(x_dia, 45, w_dia, 355, fill="#fdfdfd", stroke=MUTED, sw=1.2))
    f.append(text(x_dia + w_dia / 2, 70, "Напруга на головному тиристорі v_A1(t)", size=15, color=INK, bold=True))

    ax_l = x_dia + 45
    ax_r = x_dia + w_dia - 25
    ax_zero_y = 230
    f.append(line(ax_l, 100, ax_l, 360, color=LINE, sw=1.6))
    f.append(line(ax_l, ax_zero_y, ax_r, ax_zero_y, color=LINE, sw=1.6))
    f.append(text(ax_r, ax_zero_y + 18, "t", size=13, color=INK, bold=True))
    f.append(text(ax_l - 8, ax_zero_y + 5, "0", size=11, color=MUTED, anchor="end"))

    # Рівні напруги
    y_vs = ax_zero_y - 95
    y_mvs = ax_zero_y + 95
    f.append(line(ax_l - 4, y_vs, ax_r, y_vs, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ax_l - 8, y_vs + 4, "+Vs", size=11, color=POS, bold=True, anchor="end"))

    f.append(line(ax_l - 4, y_mvs, ax_r, y_mvs, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ax_l - 8, y_mvs + 4, "−Vs", size=11, color=NEG, bold=True, anchor="end"))

    # Момент комутації t0 (вмикання T2)
    t0_x = ax_l + 60
    f.append(line(t0_x, 100, t0_x, 360, color=MUTED, sw=1, dash="4 4"))
    f.append(text(t0_x, 375, "t0 (пуск T2)", size=11, color=INK, bold=True))

    # Точка переходу через нуль t1
    t1_x = t0_x + 95
    f.append(line(t1_x, 100, t1_x, ax_zero_y, color=FIELD, sw=1.2, dash="3 3"))
    f.append(text(t1_x, ax_zero_y - 8, "t1", size=11, color=FIELD, bold=True))

    # Зона від'ємної напруги t_c
    f.append(rect(t0_x, ax_zero_y, t1_x - t0_x, 95, fill="#eaf0fd", stroke="none"))
    f.append(text((t0_x + t1_x) / 2, ax_zero_y + 50, "tc (V < 0)", size=12, color=NEG, bold=True))
    f.append(text((t0_x + t1_x) / 2, ax_zero_y + 70, "tc ≥ 1.5·tq", size=11, color=NEG))

    # Крива напруги v_A1
    pts = []
    pts.append("%.1f,%.1f" % (ax_l, ax_zero_y - 2))
    pts.append("%.1f,%.1f" % (t0_x, ax_zero_y - 2))
    pts.append("%.1f,%.1f" % (t0_x, y_mvs))

    # Експоненційне відновлення: v(t) = Vs - 2*Vs*exp(-t / tau)
    # при t=0 -> -Vs, при t = tc = ln(2)*tau -> 0, при t -> infty -> +Vs
    for step in range(0, 31):
        rel_t = step / 30.0
        cur_x = t0_x + rel_t * 190
        # нормалізована крива: від -1 до +1
        val = 1.0 - 2.0 * math.exp(-rel_t * 1.8)
        cur_y = ax_zero_y - val * 95
        pts.append("%.1f,%.1f" % (cur_x, cur_y))
    pts.append("%.1f,%.1f" % (ax_r, y_vs))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))
    f.append(text(t1_x + 55, y_vs + 28, "v_A1(t)", size=13, color=POS, bold=True))

    return render(os.path.join(IMG, "parallel-capacitor-commutation.svg"), W, H, *f)


def fig_charge_recovery():
    """Фізика відновлення запірних властивостей: t_rr (зовнішні переходи) та t_gr (рекомбінація в n-базі)."""
    W, H = 880, 400
    f = []

    # Загальна рамка
    f.append(rect(30, 45, 820, 335, fill="#fdfdfd", stroke=MUTED, sw=1.2))
    f.append(text(W / 2, 70, "Розсмоктування носіїв у структурі p-n-p-n при вимиканні", size=15, color=INK, bold=True))

    # Ліва колонка: фаза 1 (Зворотне відновлення t_rr)
    x1 = 60
    w_col = 360
    f.append(rect(x1, 95, w_col, 265, fill="#fafbfc", stroke=MUTED, sw=1.0))
    f.append(text(x1 + w_col / 2, 120, "1. Зворотне відновлення (t_rr)", size=13, color=NEG, bold=True))
    f.append(text(x1 + w_col / 2, 138, "Винесення носіїв зворотним струмом Irr", size=11, color=MUTED))

    # 4 шари тиристора для фази 1
    ly_top = 160
    l_h = 36
    layers = [("P1 (Анод)", "#fde8e7", POS), ("N1 (Широка база)", "#e3f2fd", NEG),
              ("P2 (Керування)", "#fde8e7", POS), ("N2 (Катод)", "#e3f2fd", NEG)]

    for idx, (lname, bg_col, txt_col) in enumerate(layers):
        cy = ly_top + idx * l_h
        f.append(rect(x1 + 30, cy, w_col - 60, l_h, fill=bg_col, stroke=LINE, sw=1.2, rx=0))
        f.append(text(x1 + 85, cy + 22, lname, size=11, color=txt_col, bold=True, anchor="start"))
        if idx == 0:
            f.append(text(x1 + w_col - 45, cy + 22, "J1 (блокує)", size=10, color=FIELD, bold=True, anchor="end"))
        elif idx == 1:
            f.append(text(x1 + w_col - 45, cy + 22, "J2 (прямий)", size=10, color=MUTED, anchor="end"))
        elif idx == 2:
            f.append(text(x1 + w_col - 45, cy + 22, "J3 (блокує)", size=10, color=FIELD, bold=True, anchor="end"))

    # Пояснення під шарами 1
    f.append(text(x1 + w_col / 2, 322, "Зовнішні переходи J1 і J3 вільні від носіїв.", size=11, color=INK))
    f.append(text(x1 + w_col / 2, 342, "Тиристор здатний тримати зворотну напругу.", size=11, color=NEG, bold=True))

    # Права колонка: фаза 2 (Рекомбінація в n-базі t_gr)
    x2 = 460
    f.append(rect(x2, 95, w_col, 265, fill="#fafbfc", stroke=MUTED, sw=1.0))
    f.append(text(x2 + w_col / 2, 120, "2. Рекомбінація в базі (t_gr)", size=13, color=POS, bold=True))
    f.append(text(x2 + w_col / 2, 138, "Природне згасання заряду в товщі N1", size=11, color=MUTED))

    # 4 шари тиристора для фази 2
    for idx, (lname, bg_col, txt_col) in enumerate(layers):
        cy = ly_top + idx * l_h
        f.append(rect(x2 + 30, cy, w_col - 60, l_h, fill=bg_col, stroke=LINE, sw=1.2, rx=0))
        f.append(text(x2 + 85, cy + 22, lname, size=11, color=txt_col, bold=True, anchor="start"))
        if idx == 1:
            # Виділення замкненого заряду в N1
            f.append(rect(x2 + 190, cy + 6, 95, 24, fill="#fff3cd", stroke=POS, sw=1.2, rx=4))
            f.append(text(x2 + 237, cy + 22, "Заряд Qf (τ)", size=10, color=POS, bold=True))
        elif idx == 0:
            f.append(text(x2 + w_col - 45, cy + 22, "J1", size=10, color=MUTED, anchor="end"))
        elif idx == 2:
            f.append(text(x2 + w_col - 45, cy + 22, "J3", size=10, color=MUTED, anchor="end"))

    # Пояснення під шарами 2
    f.append(text(x2 + w_col / 2, 322, "Носії в N1 не витягуються полем — вони рекомбінують.", size=11, color=INK))
    f.append(text(x2 + w_col / 2, 342, "Повна готовність блокувати пряму напругу: tq = trr + tgr", size=11, color=POS, bold=True))

    return render(os.path.join(IMG, "turn-off-charge-recovery.svg"), W, H, *f)


def fig_mcmurray_circuit():
    """Схема та структура контуру комутації Мак-Мюррея."""
    W, H = 880, 420
    f = []

    f.append(rect(30, 40, 820, 360, fill="#fdfdfd", stroke=MUTED, sw=1.2))
    f.append(text(W / 2, 65, "Резонансний комутатор струму Мак-Мюррея", size=15, color=INK, bold=True))

    # Лінії живлення
    v_top = 100
    v_bot = 360
    f.append(line(60, v_top, 820, v_top, color=POS, sw=2.2))
    f.append(text(75, v_top - 10, "+Vs (DC шина)", size=12, color=POS, bold=True, anchor="start"))

    f.append(line(60, v_bot, 820, v_bot, color=NEG, sw=2.2))
    f.append(text(75, v_bot + 20, "−Vs / 0 В", size=12, color=NEG, bold=True, anchor="start"))

    # Вузол навантаження
    x_main = 260
    f.append(line(x_main, v_top, x_main, 140, color=LINE, sw=2.0))

    # Головний тиристор T1
    t1_box = fitbox(x_main - 40, 140, 80, 50, "T1\n(головний)", size=11, bold=True, fill="#eef2f7", stroke=LINE)
    f.append(t1_box)

    # Зворотний діод D1 зустрічно-паралельно до T1
    x_d1 = x_main + 110
    f.append(line(x_main, 140, x_d1, 140, color=LINE, sw=1.8))
    f.append(line(x_main, 190, x_d1, 190, color=LINE, sw=1.8))
    d1_box = fitbox(x_d1 - 35, 140, 70, 50, "D1\n(зворотний)", size=10, bold=True, fill="#e8f5e9", stroke=FIELD)
    f.append(d1_box)

    # Вихід на навантаження
    node_out_y = 230
    f.append(line(x_main, 190, x_main, node_out_y, color=LINE, sw=2.0))
    f.append(circle(x_main, node_out_y, 4, fill=LINE, stroke=LINE))
    f.append(line(x_main, node_out_y, 460, node_out_y, color=LINE, sw=2.0))

    # Індуктивне навантаження
    f.append(rect(460, node_out_y - 20, 80, 40, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(500, node_out_y + 5, "I0 (Load)", size=12, bold=True))
    f.append(arrow(470, node_out_y + 26, 530, node_out_y + 26, color=POS, sw=1.6))
    f.append(line(540, node_out_y, 580, node_out_y, color=LINE, sw=1.8))
    f.append(line(580, node_out_y, 580, v_bot, color=LINE, sw=1.8))

    # Резонансний контур комутації: TA1 + Lc + Cc
    x_aux = 680
    f.append(line(x_main, 140, x_aux, 140, color=LINE, sw=1.8))
    ta_box = fitbox(x_aux - 40, 140, 80, 45, "TA1\n(допоміж.)", size=10, bold=True, fill="#fff4e6", stroke=LINE)
    f.append(ta_box)

    f.append(line(x_aux, 185, x_aux, 220, color=LINE, sw=1.8))

    # Котушка Lc
    f.append(rect(x_aux - 30, 220, 60, 35, fill="#ffffff", stroke=COILC, sw=1.8))
    f.append(text(x_aux, 242, "Lc", size=12, color=COILC, bold=True))

    f.append(line(x_aux, 255, x_aux, 280, color=LINE, sw=1.8))

    # Конденсатор Cc
    f.append(line(x_aux - 20, 280, x_aux + 20, 280, color=LINE, sw=2.4))
    f.append(line(x_aux - 20, 288, x_aux + 20, 288, color=LINE, sw=2.4))
    f.append(text(x_aux + 32, 286, "Cc", size=12, bold=True, anchor="start"))

    f.append(line(x_aux, 288, x_aux, 330, color=LINE, sw=1.8))
    f.append(line(x_aux, 330, x_main, 330, color=LINE, sw=1.8))
    f.append(line(x_main, 330, x_main, node_out_y, color=LINE, sw=1.8))

    # Текстові пояснення до контуру
    info_box = fitbox(60, 270, 180, 75, "Резонансний імпульс ic:\n• амплітуда Ip = Vc0/Z0\n• Z0 = √(Lc/Cc)\n• протидіє струму I0 в T1", size=10, fill="#f4f6f8", stroke=MUTED)
    f.append(info_box)

    return render(os.path.join(IMG, "mcmurray-circuit-stages.svg"), W, H, *f)


def fig_current_commutation_waveforms():
    """Часові діаграми струму комутації Мак-Мюррея: струм тиристора, діода та напруга V_AK."""
    W, H = 880, 440
    f = []

    f.append(rect(30, 40, 820, 380, fill="#fdfdfd", stroke=MUTED, sw=1.2))
    f.append(text(W / 2, 65, "Діаграми струмів та напруги при резонансній комутації Мак-Мюррея", size=15, color=INK, bold=True))

    # Графік 1: СТРУМИ (ic, iT1, iD1)
    ax_l = 80
    ax_r = 810
    y1_base = 210
    f.append(line(ax_l, 90, ax_l, y1_base + 15, color=LINE, sw=1.6))
    f.append(line(ax_l, y1_base, ax_r, y1_base, color=LINE, sw=1.6))
    f.append(text(ax_r, y1_base + 16, "t", size=12, color=INK, bold=True))
    f.append(text(ax_l - 10, y1_base + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(ax_l - 10, 105, "I (струм)", size=11, color=INK, bold=True, anchor="end"))

    # Рівень струму навантаження I0
    y_i0 = y1_base - 50
    f.append(line(ax_l, y_i0, ax_r, y_i0, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ax_l - 10, y_i0 + 4, "I0", size=11, color=INK, bold=True, anchor="end"))

    # Пік резонансного струму Ip
    y_ip = y1_base - 95
    f.append(line(ax_l, y_ip, ax_r, y_ip, color=MUTED, sw=1, dash="2 2"))
    f.append(text(ax_l - 10, y_ip + 4, "Ip = m·I0", size=10, color=POS, bold=True, anchor="end"))

    t0_x = 180   # пуск TA1
    t1_x = 280   # i_c = I0 (T1 вимикається, D1 вмикається)
    t2_x = 420   # пік i_c
    t3_x = 560   # i_c знову = I0 (D1 вимикається)

    # Вертикальні мітки
    for tx, lbl in [(t0_x, "t0"), (t1_x, "t1"), (t3_x, "t2")]:
        f.append(line(tx, 90, tx, 390, color=MUTED, sw=1, dash="3 3"))

    f.append(text(t0_x, y1_base + 16, "t0 (пуск TA)", size=10, color=MUTED))
    f.append(text(t1_x, y1_base + 16, "t1 (iT=0)", size=10, color=MUTED))
    f.append(text(t3_x, y1_base + 16, "t2 (iD=0)", size=10, color=MUTED))

    # Зона провідності діода D1 = час вимикання tc
    f.append(rect(t1_x, y_ip, t3_x - t1_x, y1_base - y_ip, fill="#e8f5e9", stroke="none"))
    f.append(text((t1_x + t3_x) / 2, y_i0 - 24, "iD1 = ic − I0", size=11, color=FIELD, bold=True))
    f.append(text((t1_x + t3_x) / 2, y_i0 - 8, "Провідність D1", size=10, color=FIELD))

    # Синусоїда резонансного струму ic(t)
    ic_pts = ["%.1f,%.1f" % (ax_l, y1_base), "%.1f,%.1f" % (t0_x, y1_base)]
    for s in range(0, 41):
        rel = s / 40.0
        cx = t0_x + rel * (t3_x - t0_x + 120)
        # sin від 0 до pi
        val = math.sin(rel * math.pi)
        cy = y1_base - val * 95
        ic_pts.append("%.1f,%.1f" % (cx, cy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 3"/>' % (" ".join(ic_pts), POS))
    f.append(text(t2_x, y_ip - 8, "ic(t) резонанс", size=11, color=POS, bold=True))

    # Струм тиристора i_T1(t) = I0 - ic(t) до 0, потім малий сплеск Irr
    it_pts = ["%.1f,%.1f" % (ax_l, y_i0), "%.1f,%.1f" % (t0_x, y_i0)]
    # спад струму
    it_pts.append("%.1f,%.1f" % (t1_x - 15, y1_base - 10))
    it_pts.append("%.1f,%.1f" % (t1_x, y1_base))
    it_pts.append("%.1f,%.1f" % (t1_x + 10, y1_base + 8))   # Irr
    it_pts.append("%.1f,%.1f" % (t1_x + 25, y1_base))
    it_pts.append("%.1f,%.1f" % (ax_r, y1_base))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(it_pts), NEG))
    f.append(text(t0_x + 40, y_i0 - 10, "i_T1(t)", size=12, color=NEG, bold=True))

    # Графік 2: НАПРУГА V_AK на тиристорі T1
    y2_base = 340
    f.append(line(ax_l, 255, ax_l, 395, color=LINE, sw=1.6))
    f.append(line(ax_l, y2_base, ax_r, y2_base, color=LINE, sw=1.6))
    f.append(text(ax_r, y2_base + 16, "t", size=12, color=INK, bold=True))
    f.append(text(ax_l - 10, y2_base + 4, "0 В", size=11, color=MUTED, anchor="end"))
    f.append(text(ax_l - 10, 265, "V_AK", size=11, color=INK, bold=True, anchor="end"))

    # Рівні напруги: -1В (VD) та +Vs
    y_vd = y2_base + 12
    y_vs2 = y2_base - 65
    f.append(line(ax_l, y_vs2, ax_r, y_vs2, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ax_l - 10, y_vs2 + 4, "+Vs", size=10, color=POS, anchor="end"))
    f.append(text(ax_l - 10, y_vd + 4, "−1 В", size=10, color=FIELD, anchor="end"))

    # Зона захисного зворотного зміщення tc
    f.append(rect(t1_x, y2_base, t3_x - t1_x, 12, fill="#eaf0fd", stroke=FIELD, sw=1.2))
    f.append(text((t1_x + t3_x) / 2, y2_base + 30, "tc (V_AK = −VD1 ≈ −1 В) ≥ 1.5·tq", size=11, color=NEG, bold=True))

    # Крива V_AK
    vak_pts = [
        "%.1f,%.1f" % (ax_l, y2_base - 3),
        "%.1f,%.1f" % (t1_x, y2_base - 3),
        "%.1f,%.1f" % (t1_x, y_vd),
        "%.1f,%.1f" % (t3_x, y_vd),
        "%.1f,%.1f" % (t3_x + 50, y_vs2),
        "%.1f,%.1f" % (ax_r, y_vs2)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(vak_pts), POS))
    f.append(text(t3_x + 70, y_vs2 + 18, "dv/dt (наростання)", size=11, color=POS, bold=True))

    return render(os.path.join(IMG, "current-commutation-waveforms.svg"), W, H, *f)


if __name__ == "__main__":
    fig_parallel_capacitor()
    fig_charge_recovery()
    fig_mcmurray_circuit()
    fig_current_commutation_waveforms()
    print("Всі фігури згенеровано у ./img/")
