# -*- coding: utf-8 -*-
"""Фігури до статті «PFM і burst-mode: режими легкого навантаження».
Запуск із теки теми:  python figs.py   →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

CLR_PWM = "#c0392b"    # червоний - жорстка ШІМ
CLR_PFM = "#2457d6"    # синій - ЧІМ / PFM
CLR_BURST = "#27ae60"  # зелений - Burst Mode
CLR_SLEEP = "#8e44ad"  # фіолетовий - режим сну / струм спокою
CLR_GRID = "#e6e8ec"


# ── Фігура 1: Криві ККД і баланс втрат (ШІМ проти PFM/Burst) ─────────────────
def fig_loss_breakdown():
    W, H = 820, 520
    x0, x1, y0, y1 = 100, 750, 60, 400

    s = []
    # Сітка по осі ККД (%)
    for e in range(0, 101, 20):
        y = y1 - (e / 100.0) * (y1 - y0)
        s.append(line(x0, y, x1, y, color=CLR_GRID, sw=1.0))
        s.append(text(x0 - 15, y + 4, "%d%%" % e, size=12, color=MUTED, anchor="end"))

    # Осі
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.8))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.8))
    s.append(text(x0 - 45, (y0 + y1) / 2, "ККД (η), %", size=13, color=INK, bold=True))

    # Логарифмічна шкала по струму: від 10 мкА (1e-5) до 3 А (3.0)
    Imin, Imax = 1e-5, 3.0
    def X(I):
        return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(e):
        return y1 - (e / 100.0) * (y1 - y0)

    ticks = [(1e-5, "10 мкА"), (1e-4, "100 мкА"), (1e-3, "1 мА"), (1e-2, "10 мА"), (1e-1, "100 мА"), (1.0, "1 А"), (3.0, "3 А")]
    for I, lab in ticks:
        xi = X(I)
        s.append(line(xi, y1, xi, y1 + 6, color=INK, sw=1.4))
        s.append(text(xi, y1 + 22, lab, size=11, color=MUTED))
    s.append(text((x0 + x1) / 2, y1 + 46, "Струм навантаження Івих (логарифмічна шкала)", size=13, color=INK, bold=True))

    # Модель ККД
    def eff_pwm(I):
        pout = 3.3 * I
        ploss = 0.035 + 0.04 * I + 0.08 * I * I
        return max(0.0, min(96.0, 100.0 * pout / (pout + ploss)))

    def eff_pfm(I):
        pout = 3.3 * I
        ploss = 0.0003 + 0.06 * I + 0.08 * I * I
        return max(0.0, min(95.0, 100.0 * pout / (pout + ploss)))

    def eff_burst(I):
        pout = 3.3 * I
        ploss = 0.00004 + 0.045 * I + 0.08 * I * I
        return max(0.0, min(94.0, 100.0 * pout / (pout + ploss)))

    def pts_curve(fn):
        pts = []
        for i in range(120):
            val = math.pow(10, math.log10(Imin) + i * (math.log10(Imax) - math.log10(Imin)) / 119.0)
            pts.append((X(val), Y(fn(val))))
        return " ".join("%.2f,%.2f" % (x, y) for x, y in pts)

    # Криві
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (pts_curve(eff_burst), CLR_BURST))
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 3"/>' % (pts_curve(eff_pfm), CLR_PFM))
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts_curve(eff_pwm), CLR_PWM))

    # Позначки на кривих
    s.append(text(X(0.0003), Y(eff_pwm(0.0003)) - 14, "Фіксована ШІМ (катастрофа ККД)", size=11, color=CLR_PWM, bold=True))
    s.append(text(X(0.0001), Y(eff_burst(0.0001)) - 14, "Burst Mode (глибокий сон)", size=11, color=CLR_BURST, bold=True))
    s.append(text(X(0.004), Y(eff_pfm(0.004)) + 18, "PFM (ЧІМ)", size=11, color=CLR_PFM, bold=True))

    # Виділення зони легкого навантаження
    s.append(rect(x0 + 2, y0 + 2, X(0.01) - x0 - 2, y1 - y0 - 4, fill="#fff8e7", stroke="#f39c12", sw=1.2, rx=4))
    s.append(text((x0 + X(0.01)) / 2, y0 + 24, "Зона легкого навантаження (< 10 мА)", size=11, color="#b7791f", bold=True))
    s.append(text((x0 + X(0.01)) / 2, y0 + 40, "P_gate + P_coss + P_q домінують", size=10, color=MUTED))

    # Легенда внизу
    tb1, _, _ = textbox(180, 485, "Фіксована ШІМ (f=const)", size=12, fill="#fdedeb", stroke=CLR_PWM, color=CLR_PWM, bold=True)
    tb2, _, _ = textbox(410, 485, "ЧІМ / PFM (f ∝ Івих)", size=12, fill="#ebf3fd", stroke=CLR_PFM, color=CLR_PFM, bold=True)
    tb3, _, _ = textbox(640, 485, "Burst Mode (пачки + сон)", size=12, fill="#ebf9f0", stroke=CLR_BURST, color=CLR_BURST, bold=True)
    s.extend([tb1, tb2, tb3])

    render(os.path.join(OUT, 'loss-breakdown-pwm.svg'), W, H, *s,
           title="Криві ККД перетворювача в режимах ШІМ, PFM та Burst Mode")


# ── Фігура 2: Часові діаграми струмів і напруг у 4 режимах ───────────────────
def fig_waveforms():
    W, H = 840, 560
    s = []

    row_h = 105
    y_start = 45

    modes = [
        ("1. Фіксована ШІМ у CCM (важке навантаження)", CLR_PWM, "Неперервний струм котушки, фіксований період T_sw, високі втрати на холостому ході"),
        ("2. Діодна емуляція DEM / DCM (блокування зворотного струму)", "#d35400", "Нижній ключ вимикається при I_L=0, котушка розмикається (дзвін Hi-Z)"),
        ("3. ЧІМ / COT-PFM (фіксований t_on, змінна пауза)", CLR_PFM, "Одиничні імпульси фіксованої тривалості t_on, частота падає пропорційно навантаженню"),
        ("4. Режим пачки / Burst Mode (серія імпульсів + глибокий сон)", CLR_BURST, "Пачка з 5-15 імпульсів підзаряджає C_out, далі контролер засинає на мілісекунди (I_q = 2 мкА)")
    ]

    for idx, (title_text, col, desc) in enumerate(modes):
        yb = y_start + idx * (row_h + 20)
        s.append(rect(20, yb, 800, row_h + 10, fill="#fcfdfe", stroke="#d0d5dd", sw=1.2, rx=6))
        s.append(text(35, yb + 18, title_text, size=12, color=col, anchor="start", bold=True))
        s.append(text(785, yb + 18, desc, size=10, color=MUTED, anchor="end"))

        y_zero = yb + 68
        s.append(line(80, y_zero, 780, y_zero, color="#94a3b8", sw=1.0, dash="3 3"))
        s.append(text(65, y_zero + 4, "0 A", size=10, color=MUTED, anchor="end"))
        s.append(text(790, y_zero + 4, "I_L", size=11, color=INK, anchor="start", bold=True))

        if idx == 0:
            pts = []
            for k in range(6):
                x_k = 100 + k * 110
                pts.extend([(x_k, y_zero - 12), (x_k + 45, y_zero - 36), (x_k + 110, y_zero - 12)])
            p_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
            s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (p_str, col))
            s.append(text(220, y_zero - 42, "Струм завжди вище нуля (CCM)", size=10, color=col))

        elif idx == 1:
            pts = []
            for k in range(4):
                x_k = 100 + k * 165
                pts.extend([(x_k, y_zero), (x_k + 40, y_zero - 34), (x_k + 90, y_zero)])
                pts.extend([(x_k + 165, y_zero)])
            p_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
            s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (p_str, col))
            s.append(text(215, y_zero - 12, "Hi-Z (діод вимкнено)", size=10, color="#d35400"))

        elif idx == 2:
            for k, x_k in enumerate([100, 310, 520, 730]):
                pts = [(x_k, y_zero), (x_k + 30, y_zero - 38), (x_k + 70, y_zero)]
                p_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
                s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (p_str, col))
            s.append(text(210, y_zero - 12, "← Змінний період T_sw(Івих) →", size=10, color=col))
            s.append(text(115, y_zero - 42, "t_on=const", size=10, color=col, bold=True))

        elif idx == 3:
            pts = []
            x_b = 100
            for p in range(5):
                xp = x_b + p * 24
                pts.extend([(xp, y_zero), (xp + 10, y_zero - 36), (xp + 24, y_zero)])
            p_str1 = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
            s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_str1, col))

            pts2 = []
            x_b2 = 540
            for p in range(5):
                xp = x_b2 + p * 24
                pts2.extend([(xp, y_zero), (xp + 10, y_zero - 36), (xp + 24, y_zero)])
            p_str2 = " ".join("%.1f,%.1f" % (x, y) for x, y in pts2)
            s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_str2, col))

            s.append(rect(230, y_zero - 44, 300, 48, fill="#f3e8ff", stroke=CLR_SLEEP, sw=1.2, rx=4))
            s.append(text(380, y_zero - 28, "Режим глибокого сну (Sleep Window)", size=11, color=CLR_SLEEP, bold=True))
            s.append(text(380, y_zero - 12, "Ключі вимкнено, I_q = 1..5 мкА, розряд C_out", size=10, color=MUTED))

    render(os.path.join(OUT, 'pfm-vs-burst-waveforms.svg'), W, H, *s,
           title="Порівняння часових форм струму в режимах ШІМ, DCM, PFM та Burst Mode")


# ── Фігура 3: Гістерезисний цикл і робота Burst Mode ────────────────────────
def fig_burst_hysteresis():
    W, H = 820, 500
    s = []

    s.append(rect(20, 20, 780, 460, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))

    gx0, gx1 = 80, 750
    v_nom = 135
    v_high = 95
    v_low = 175

    s.append(line(gx0, v_high, gx1, v_high, color="#e74c3c", sw=1.4, dash="4 4"))
    s.append(text(gx0 - 10, v_high + 4, "V_high (V_ном + ΔV)", size=11, color="#e74c3c", anchor="end", bold=True))

    s.append(line(gx0, v_nom, gx1, v_nom, color="#94a3b8", sw=1.0, dash="2 2"))
    s.append(text(gx0 - 10, v_nom + 4, "V_ном", size=11, color=MUTED, anchor="end"))

    s.append(line(gx0, v_low, gx1, v_low, color="#2980b9", sw=1.4, dash="4 4"))
    s.append(text(gx0 - 10, v_low + 4, "V_low (V_ном − ΔV)", size=11, color="#2980b9", anchor="end", bold=True))

    v_pts = [
        (80, v_nom + 10), (120, v_low),
        (220, v_high),
        (500, v_low),
        (600, v_high),
        (750, v_nom + 5)
    ]
    vp_str = " ".join("%.1f,%.1f" % (x, y) for x, y in v_pts)
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (vp_str, INK))

    s.append(line(515, v_high, 515, v_low, color="#8e44ad", sw=1.8))
    s.append(text(525, (v_high + v_low) / 2 + 4, "Пульсація ΔV_burst (20..100 мВ)", size=11, color="#8e44ad", anchor="start", bold=True))

    gy2_bot = 420
    s.append(line(gx0, gy2_bot, gx1, gy2_bot, color=INK, sw=1.5))
    s.append(text(gx0 - 10, gy2_bot - 20, "Струм котушки I_L", size=11, color=INK, anchor="end", bold=True))

    s.append(rect(120, 260, 100, 160, fill="#e8f8f5", stroke=CLR_BURST, sw=1.4, rx=4))
    s.append(text(170, 280, "АКТИВНА ПАЧКА", size=11, color=CLR_BURST, bold=True))
    s.append(text(170, 295, "5..15 імпульсів", size=10, color=CLR_BURST))

    for p in range(6):
        xp = 125 + p * 15
        s.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.2"/>' %
                 (xp, gy2_bot, xp + 6, gy2_bot - 80, xp + 14, gy2_bot, "#a3e4d7", CLR_BURST))

    s.append(rect(220, 260, 280, 160, fill="#fbf0ff", stroke=CLR_SLEEP, sw=1.4, rx=4))
    s.append(text(360, 285, "РЕЖИМ ГЛИБОКОГО СНУ (SLEEP)", size=12, color=CLR_SLEEP, bold=True))
    s.append(text(360, 310, "• Силові ключі повністю зачинені (Hi-Z)", size=11, color=INK))
    s.append(text(360, 330, "• Генератор і підсилювач помилки вимкнені", size=11, color=INK))
    s.append(text(360, 350, "• Струм спокою контролера: I_q ≈ 1..5 мкА", size=11, color=CLR_SLEEP, bold=True))
    s.append(text(360, 370, "• Навантаження живиться від енергії C_out", size=11, color=MUTED))
    s.append(text(360, 395, "t_сон = C_out · 2ΔV / I_вих (до десятків мс)", size=11, color="#2c3e50", italic=True))

    s.append(rect(500, 260, 100, 160, fill="#e8f8f5", stroke=CLR_BURST, sw=1.4, rx=4))
    s.append(text(550, 280, "АКТИВНА ПАЧКА", size=11, color=CLR_BURST, bold=True))
    for p in range(6):
        xp = 505 + p * 15
        s.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.2"/>' %
                 (xp, gy2_bot, xp + 6, gy2_bot - 80, xp + 14, gy2_bot, "#a3e4d7", CLR_BURST))

    s.append(rect(600, 260, 140, 160, fill="#fbf0ff", stroke=CLR_SLEEP, sw=1.4, rx=4))
    s.append(text(670, 340, "Сон (I_q = 2 мкА)", size=11, color=CLR_SLEEP, bold=True))

    render(os.path.join(OUT, 'burst-hysteresis-sleep.svg'), W, H, *s,
           title="Гістерезисний контроль напруги та фази роботи в Burst Mode")


# ── Фігура 4: Акустичний шум керамічних конденсаторів (п'єзоефект) ───────────
def fig_acoustic_noise():
    W, H = 820, 480
    s = []

    s.append(rect(20, 20, 780, 440, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))

    box_w = 230
    box_h = 360
    y_b = 60

    # Блок 1
    s.append(rect(40, y_b, box_w, box_h, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))
    s.append(text(40 + box_w / 2, y_b + 25, "1. Субгармонійна пульсація", size=12, color=INK, bold=True))
    s.append(text(40 + box_w / 2, y_b + 42, "Частота пачок f_burst ∈ 1..20 кГц", size=11, color="#e74c3c", bold=True))

    pts1 = []
    for i in range(120):
        t = i / 119.0
        x = 55 + t * (box_w - 30)
        y = y_b + 110 + 25 * math.sin(t * 4 * math.pi)
        pts1.append((x, y))
    p1_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts1)
    s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p1_str, "#e74c3c"))
    s.append(text(40 + box_w / 2, y_b + 160, "ΔV_burst = 30..150 мВ", size=11, color=INK))
    s.append(text(40 + box_w / 2, y_b + 180, "Період пачок T_burst потрапляє", size=10, color=MUTED))
    s.append(text(40 + box_w / 2, y_b + 195, "в діапазон людського слуху", size=10, color=MUTED))

    s.append(text(40 + box_w / 2, y_b + 240, "Джерело:", size=11, color=INK, bold=True))
    s.append(text(40 + box_w / 2, y_b + 260, "Періодичний розряд C_out", size=10, color=INK))
    s.append(text(40 + box_w / 2, y_b + 278, "струмом навантаження", size=10, color=INK))
    s.append(text(40 + box_w / 2, y_b + 296, "з наступним різким зарядом", size=10, color=INK))

    s.append(arrow(275, y_b + box_h / 2, 295, y_b + box_h / 2, color=INK, sw=2.0))

    # Блок 2
    s.append(rect(300, y_b, box_w, box_h, fill="#fffaf0", stroke="#d97706", sw=1.4, rx=6))
    s.append(text(300 + box_w / 2, y_b + 25, "2. Зворотний п'єзоефект", size=12, color=INK, bold=True))
    s.append(text(300 + box_w / 2, y_b + 42, "Кераміка Class II (X5R / X7R)", size=11, color="#d97706", bold=True))

    cx_cap = 300 + box_w / 2
    cy_cap = y_b + 110
    s.append(rect(cx_cap - 55, cy_cap - 25, 20, 50, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))
    s.append(rect(cx_cap + 35, cy_cap - 25, 20, 50, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))
    s.append(rect(cx_cap - 35, cy_cap - 22, 70, 44, fill="#fed7aa", stroke="#ea580c", sw=1.4, rx=2))
    s.append(text(cx_cap, cy_cap + 4, "BaTiO₃", size=11, color="#9a3412", bold=True))

    s.append(line(cx_cap, cy_cap - 28, cx_cap, cy_cap - 38, color="#dc2626", sw=1.6))
    s.append(line(cx_cap, cy_cap + 28, cx_cap, cy_cap + 38, color="#dc2626", sw=1.6))
    s.append(text(cx_cap, cy_cap - 42, "Δz (стиск/розтяг)", size=10, color="#dc2626", bold=True))

    s.append(text(300 + box_w / 2, y_b + 185, "Титанат барію деформується", size=11, color=INK))
    s.append(text(300 + box_w / 2, y_b + 203, "пропорційно напрузі V(t).", size=11, color=INK))
    s.append(text(300 + box_w / 2, y_b + 225, "Змінна складова ΔV породжує", size=10, color=MUTED))
    s.append(text(300 + box_w / 2, y_b + 240, "механічну вібрацію кристалічної", size=10, color=MUTED))
    s.append(text(300 + box_w / 2, y_b + 255, "ґратки на частоті пачок f_burst", size=10, color=MUTED))

    s.append(arrow(535, y_b + box_h / 2, 555, y_b + box_h / 2, color=INK, sw=2.0))

    # Блок 3
    s.append(rect(560, y_b, box_w, box_h, fill="#fdf2f8", stroke="#db2777", sw=1.4, rx=6))
    s.append(text(560 + box_w / 2, y_b + 25, "3. Акустичний свист плати", size=12, color=INK, bold=True))
    s.append(text(560 + box_w / 2, y_b + 42, "Плата як динамік (мембрана)", size=11, color="#db2777", bold=True))

    cx_pcb = 560 + box_w / 2
    cy_pcb = y_b + 110
    s.append(rect(cx_pcb - 80, cy_pcb + 15, 160, 14, fill="#86efac", stroke="#15803d", sw=1.4, rx=2))
    s.append(text(cx_pcb, cy_pcb + 26, "Текстоліт FR-4", size=10, color="#14532d", bold=True))

    s.append(rect(cx_pcb - 25, cy_pcb - 10, 50, 25, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=2))
    for r_wave in [20, 35, 50]:
        s.append('<path d="M %.1f,%.1f A %.1f %.1f 0 0 1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8"/>' %
                 (cx_pcb - r_wave, cy_pcb - 15 - r_wave*0.4, r_wave, r_wave, cx_pcb + r_wave, cy_pcb - 15 - r_wave*0.4, "#db2777"))

    s.append(text(560 + box_w / 2, cy_pcb - 45, "Звукова хвиля (1..20 кГц)", size=10, color="#db2777", bold=True))

    s.append(text(560 + box_w / 2, y_b + 185, "Припаяні контакти передають", size=11, color=INK))
    s.append(text(560 + box_w / 2, y_b + 203, "вібрацію на склотекстоліт.", size=11, color=INK))
    s.append(text(560 + box_w / 2, y_b + 225, "Шляхи подолання:", size=11, color=INK, bold=True))
    s.append(text(560 + box_w / 2, y_b + 245, "• Ультразвуковий затиск (>25 кГц)", size=10, color="#15803d"))
    s.append(text(560 + box_w / 2, y_b + 263, "• Танталові / полімерні конденсатори", size=10, color="#15803d"))
    s.append(text(560 + box_w / 2, y_b + 281, "• Зустрічне розміщення пар MLCC", size=10, color="#15803d"))
    s.append(text(560 + box_w / 2, y_b + 299, "• Прорізи в платі під компонентом", size=10, color="#15803d"))

    render(os.path.join(OUT, 'piezoelectric-acoustic-noise.svg'), W, H, *s,
           title="Механізм виникнення акустичного шуму керамічних конденсаторів у режимі пачки")


if __name__ == '__main__':
    fig_loss_breakdown()
    fig_waveforms()
    fig_burst_hysteresis()
    fig_acoustic_noise()
    print("Всі фігури згенеровано успішно.")
