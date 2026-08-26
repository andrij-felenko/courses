# -*- coding: utf-8 -*-
"""Фігури для статті tsina-probudzhennia («Ціна пробудження»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. wakeup-timeline-phases: Хронограма мікросекундних фаз пробудження ──────
def fig_wakeup_timeline():
    W, H = 880, 460
    ox, oy = 80, 40
    tw = 720
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Фази по осі часу (тло лише у верхній зоні до oy + 210)
    phases = [
        (ox, 90, "#eef2f7", "#3b82f6", "1. LDO / Bandgap", "0–20 мкс"),
        (ox + 90, 90, "#fef3c7", "#d97706", "2. Старт RC", "20–25 мкс"),
        (ox + 180, 140, "#e0e7ff", "#4f46e5", "3. Старт ядра й RAM", "25–80 мкс"),
        (ox + 320, 170, "#fee2e2", "#dc2626", "4. Живлення шини й VREF", "80–220 мкс"),
        (ox + 490, 140, "#dcfce7", "#16a34a", "5. Вибірка АЦП", "220–300 мкс"),
        (ox + 630, 90, "#f3e8ff", "#9333ea", "6. Сон", "300–330 мкс"),
    ]

    for px, pw, pbg, pborder, plbl, ptime in phases:
        p.append(rect(px, oy, pw, 210, fill=pbg, stroke="none"))
        p.append(line(px, oy, px, oy + 320, color=MUTED, sw=1.0, dash="3 3"))
        p.append(text(px + pw / 2, oy + 20, plbl, size=11, color=INK, bold=True))
        p.append(text(px + pw / 2, oy + 36, ptime, size=10, color=MUTED, italic=True))

    p.append(line(ox + tw, oy, ox + tw, oy + 320, color=MUTED, sw=1.0, dash="3 3"))

    # Графік струму I(t)
    cur_y = 190
    p.append(text(ox - 12, cur_y - 45, "I (мА)", size=12, color=POS, bold=True, anchor="end"))
    p.append(arrow(ox - 6, cur_y + 35, ox - 6, cur_y - 55, color=POS, sw=1.5))

    scale_i = 6.5  # px per mA
    pts_i = [
        (ox, cur_y),
        (ox + 10, cur_y - 0.8 * scale_i),
        (ox + 90, cur_y - 0.8 * scale_i),
        (ox + 95, cur_y - 1.8 * scale_i),
        (ox + 180, cur_y - 1.8 * scale_i),
        (ox + 185, cur_y - 4.5 * scale_i),
        (ox + 320, cur_y - 4.5 * scale_i),
        # Inrush spike
        (ox + 325, cur_y - 11.0 * scale_i),
        (ox + 345, cur_y - 4.0 * scale_i),
        (ox + 490, cur_y - 4.0 * scale_i),
        # ADC sampling
        (ox + 495, cur_y - 6.0 * scale_i),
        (ox + 630, cur_y - 6.0 * scale_i),
        # Shutdown
        (ox + 635, cur_y - 1.2 * scale_i),
        (ox + 710, cur_y - 1.2 * scale_i),
        (ox + 720, cur_y),
    ]
    poly_pts = " ".join("%.1f,%.1f" % pt for pt in pts_i)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round"/>' % (poly_pts, POS))

    # Сплеск inrush
    p.append(text(ox + 340, cur_y - 11.0 * scale_i - 6, "кидок заряду C (11 мА)", size=10, color=POS, bold=True))

    # Логічні стани знизу (на білому тлі без перетину блоків)
    sig_y = 280
    p.append(line(ox, sig_y, ox + tw, sig_y, color=LINE, sw=1.0))
    p.append(text(ox - 12, sig_y + 14, "Такти CPU", size=11, color=INK, anchor="end"))
    p.append(rect(ox + 180, sig_y + 3, 450, 18, fill="#e0e7ff", stroke="#4f46e5", sw=1.0, rx=2))
    p.append(text(ox + 405, sig_y + 16, "MSI / HSI 16 МГц (активне виконання коду)", size=10, color="#4f46e5", bold=True))

    sig2_y = 320
    p.append(line(ox, sig2_y, ox + tw, sig2_y, color=LINE, sw=1.0))
    p.append(text(ox - 12, sig2_y + 14, "Шина VDD", size=11, color=INK, anchor="end"))
    p.append(rect(ox + 320, sig2_y + 3, 310, 18, fill="#fee2e2", stroke="#dc2626", sw=1.0, rx=2))
    p.append(text(ox + 475, sig2_y + 16, "Ключ живлення датчика увімкнено", size=10, color="#dc2626", bold=True))

    # Вісь часу
    time_y = 380
    p.append(arrow(ox, time_y, ox + tw + 25, time_y, color=INK, sw=1.6))
    p.append(text(ox + tw + 30, time_y + 4, "t (мкс)", size=12, color=INK, bold=True, italic=True))

    ticks = [(0, "0"), (90, "20"), (180, "25"), (320, "80"), (490, "220"), (630, "300"), (720, "330")]
    for dt, lbl in ticks:
        p.append(line(ox + dt, time_y - 4, ox + dt, time_y + 4, color=INK, sw=1.2))
        p.append(text(ox + dt, time_y + 18, lbl, size=11, color=INK))

    render(os.path.join(OUT, "wakeup-timeline-phases.svg"), W, H, *p)


# ── 2. crystal-oscillator-buildup: Розгойдування кварцу проти RC ──────────────
def fig_crystal_buildup():
    W, H = 860, 400
    ox, oy = 90, 45
    aw = 700
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Секція А: Кварцовий резонатор HSE
    p.append(text(ox, oy + 10, "Зовнішній кварц HSE (8–32 МГц, висока добротність Q ≈ 50 000)", size=13, color=INK, bold=True, anchor="start"))
    
    hse_y = oy + 90
    p.append(arrow(ox, hse_y, ox + aw + 20, hse_y, color=INK, sw=1.4))
    p.append(arrow(ox, hse_y + 55, ox, hse_y - 65, color=INK, sw=1.4))
    p.append(text(ox - 10, hse_y - 50, "U_osc", size=11, color=INK, bold=True, italic=True, anchor="end"))

    pts_top = []
    pts_bot = []
    pts_wave = []
    for i in range(0, 521):
        x = ox + i * (aw / 520.0)
        t_norm = i / 380.0
        if t_norm < 1.0:
            env = 2.0 + 46.0 * (math.exp(3.2 * t_norm) - 1.0) / (math.exp(3.2) - 1.0)
        else:
            env = 48.0
        pts_top.append("%.1f,%.1f" % (x, hse_y - env))
        pts_bot.append("%.1f,%.1f" % (x, hse_y + env))
        freq = 0.85
        wave = env * math.sin(i * freq)
        pts_wave.append("%.1f,%.1f" % (x, hse_y - wave))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (" ".join(pts_top), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (" ".join(pts_bot), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.0"/>' % (" ".join(pts_wave), "#2563eb"))

    # Маркування зон розгону кварцу
    p.append(line(ox + 380 * (aw / 520.0), hse_y - 60, ox + 380 * (aw / 520.0), hse_y + 60, color=MUTED, sw=1.0, dash="3 3"))
    
    b1, bw1, bh1 = textbox(ox + 180, hse_y + 55, "Зона розгойдування (1.5–3 мс): струм інвертора 1.5–3 мА, тактувати CPU ще не можна!",
                           size=10, color=POS, bold=True, fill="#fff1f2", stroke=POS, sw=1.0)
    p.append(b1)

    b2, bw2, bh2 = textbox(ox + 450 * (aw / 520.0), hse_y - 45, "HSERDY = 1 (стабільна амплітуда)",
                           size=10, color=FIELD, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.0)
    p.append(b2)

    # Секція Б: Внутрішній RC-генератор
    rc_y = oy + 260
    p.append(text(ox, rc_y - 45, "Внутрішній RC-генератор MSI / HSI (низька добротність Q ≈ 10–50)", size=13, color=INK, bold=True, anchor="start"))
    p.append(arrow(ox, rc_y, ox + aw + 20, rc_y, color=INK, sw=1.4))
    p.append(arrow(ox, rc_y + 40, ox, rc_y - 45, color=INK, sw=1.4))
    p.append(text(ox - 10, rc_y - 35, "U_rc", size=11, color=INK, bold=True, italic=True, anchor="end"))

    pts_rc = []
    for i in range(0, 521):
        x = ox + i * (aw / 520.0)
        t_norm = i / 10.0
        if t_norm < 1.0:
            env = 32.0 * t_norm
        else:
            env = 32.0
        wave = env * math.sin(i * 0.85)
        pts_rc.append("%.1f,%.1f" % (x, rc_y - wave))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (" ".join(pts_rc), FIELD))
    
    b3, bw3, bh3 = textbox(ox + 180, rc_y + 35, "Старт за 1–3 мкс: миттєва готовність до виконання коду",
                           size=10, color=FIELD, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.0)
    p.append(b3)

    p.append(text(ox + aw + 25, rc_y + 4, "час", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "crystal-oscillator-buildup.svg"), W, H, *p)


# ── 3. power-switched-sensor-timing: Комутація живлення датчика ───────────────
def fig_sensor_timing():
    W, H = 840, 390
    ox, oy = 80, 50
    aw = 700
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Сигнал 1: Керування ключем навантаження (PWR_EN)
    y1 = oy + 30
    p.append(text(ox - 10, y1 - 8, "PWR_EN (GPIO)", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(ox, y1 + 15, ox + 100, y1 + 15, color="#4f46e5", sw=2.0))
    p.append(line(ox + 100, y1 + 15, ox + 105, y1 - 15, color="#4f46e5", sw=2.0))
    p.append(line(ox + 105, y1 - 15, ox + 560, y1 - 15, color="#4f46e5", sw=2.0))
    p.append(line(ox + 560, y1 - 15, ox + 565, y1 + 15, color="#4f46e5", sw=2.0))
    p.append(line(ox + 565, y1 + 15, ox + aw, y1 + 15, color="#4f46e5", sw=2.0))

    # Сигнал 2: Напруга на шині датчика V_SENS
    y2 = oy + 105
    p.append(text(ox - 10, y2 - 8, "V_sensor (3.3 В)", size=11, color=INK, bold=True, anchor="end"))
    pts_v = [
        (ox, y2 + 15),
        (ox + 105, y2 + 15),
        (ox + 140, y2 - 15),
        (ox + 560, y2 - 15),
        (ox + 590, y2 + 15),
        (ox + aw, y2 + 15),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_v), "#059669"))

    # Сигнал 3: Струм шини I_SENS (зі сплеском inrush)
    y3 = oy + 185
    p.append(text(ox - 10, y3 - 8, "I_sensor (струм)", size=11, color=POS, bold=True, anchor="end"))
    pts_isens = [
        (ox, y3 + 15),
        (ox + 105, y3 + 15),
        (ox + 115, y3 - 35),
        (ox + 145, y3 - 5),
        (ox + 560, y3 - 5),
        (ox + 565, y3 + 15),
        (ox + aw, y3 + 15),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_isens), POS))
    p.append(text(ox + 125, y3 - 42, "I_inrush = C·(dV/dt)", size=10, color=POS, bold=True))

    # Зони стабілізації та вимірювання
    p.append(rect(ox + 105, oy + 230, 260, 45, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=3))
    p.append(text(ox + 235, oy + 250, "Прогрів / Встановлення (Settling Time)", size=11, color="#b91c1c", bold=True))
    p.append(text(ox + 235, oy + 266, "Аналоговий тракт нестабільний (помилка виміру)", size=10, color="#b91c1c", italic=True))

    p.append(rect(ox + 375, oy + 230, 185, 45, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=3))
    p.append(text(ox + 467, oy + 250, "Вікно вимірювання", size=11, color="#15803d", bold=True))
    p.append(text(ox + 467, oy + 266, "Вибірка АЦП / зчитування I²C", size=10, color="#15803d", italic=True))

    # Вертикальні лінії прив'язки
    p.append(line(ox + 105, oy, ox + 105, oy + 230, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(ox + 375, oy, ox + 375, oy + 230, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(ox + 560, oy, ox + 560, oy + 230, color=MUTED, sw=1.0, dash="3 3"))

    # Вісь часу
    time_y = oy + 300
    p.append(arrow(ox, time_y, ox + aw + 20, time_y, color=INK, sw=1.4))
    p.append(text(ox + aw + 25, time_y + 4, "t", size=12, color=INK, bold=True, italic=True))

    render(os.path.join(OUT, "power-switched-sensor-timing.svg"), W, H, *p)


# ── 4. energy-tradeoff-rc-vs-hse: Порівняння енергетичного балансу RC vs HSE ──
def fig_energy_tradeoff():
    W, H = 860, 430
    ox, oy = 80, 45
    aw = 720
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Графік 1: Стратегія HSE (anchor="start" щоб не вилазило за вісь)
    p.append(text(ox + 10, oy + 10, "Стратегія А: Запуск кварцу HSE (80 МГц) для вибірки АЦП (50 мкс)", size=12, color=POS, bold=True, anchor="start"))
    
    y_hse = oy + 95
    p.append(arrow(ox, y_hse, ox + aw + 20, y_hse, color=INK, sw=1.4))
    p.append(arrow(ox, y_hse + 20, ox, y_hse - 60, color=INK, sw=1.4))
    p.append(text(ox - 10, y_hse - 50, "I (мА)", size=11, color=INK, bold=True, anchor="end"))

    # Полігон площі розгону
    pts_hse_area = [
        (ox, y_hse),
        (ox, y_hse - 25),
        (ox + 300, y_hse - 25),
        (ox + 300, y_hse - 55),
        (ox + 325, y_hse - 55),
        (ox + 325, y_hse),
    ]
    p.append('<polygon points="%s" fill="#fee2e2" stroke="%s" stroke-width="1.8"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_hse_area), POS))
    
    p.append(text(ox + 150, y_hse - 10, "Розгін кварцу (2.0 мс @ 2.5 мА)", size=10, color=POS, bold=True))
    p.append(text(ox + 335, y_hse - 45, "Вимір (8 мА)", size=10, color=POS, bold=True, anchor="start"))

    b_hse, _, _ = textbox(ox + 540, y_hse - 30, "Q_hse ≈ 5.16 мкКл (17.0 мкДж)", size=11, color=POS, bold=True, fill="#fff1f2", stroke=POS, sw=1.2)
    p.append(b_hse)

    # Графік 2: Стратегія RC (MSI/HSI)
    y_rc = oy + 235
    p.append(text(ox + 10, y_rc - 45, "Стратегія Б: Виконання на швидкому RC-генераторі (16 МГц, старт 2 мкс)", size=12, color=FIELD, bold=True, anchor="start"))
    
    p.append(arrow(ox, y_rc, ox + aw + 20, y_rc, color=INK, sw=1.4))
    p.append(arrow(ox, y_rc + 20, ox, y_rc - 60, color=INK, sw=1.4))
    p.append(text(ox - 10, y_rc - 50, "I (мА)", size=11, color=INK, bold=True, anchor="end"))

    # Полігон площі RC
    pts_rc_area = [
        (ox, y_rc),
        (ox, y_rc - 15),
        (ox + 10, y_rc - 15),
        (ox + 10, y_rc - 32),
        (ox + 45, y_rc - 32),
        (ox + 45, y_rc),
    ]
    p.append('<polygon points="%s" fill="#dcfce7" stroke="%s" stroke-width="1.8"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_rc_area), FIELD))
    
    p.append(text(ox + 58, y_rc - 18, "Старт RC (2 мкс) + Вимір (100 мкс @ 3 мА)", size=10, color=FIELD, bold=True, anchor="start"))

    b_rc, _, _ = textbox(ox + 540, y_rc - 30, "Q_rc ≈ 0.30 мкКл (0.99 мкДж)", size=11, color=FIELD, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.2)
    p.append(b_rc)

    # Підсумок порівняння знизу
    comp_y = oy + 325
    b_sum, _, _ = textbox(ox + aw / 2, comp_y, "Висновок: Для коротких періодичних дій швидкий RC-генератор виграє в 17 разів за енергією!",
                          size=12, color=INK, bold=True, fill="#f8fafc", stroke=LINE, sw=1.5)
    p.append(b_sum)

    render(os.path.join(OUT, "energy-tradeoff-rc-vs-hse.svg"), W, H, *p)


if __name__ == "__main__":
    fig_wakeup_timeline()
    fig_crystal_buildup()
    fig_sensor_timing()
    fig_energy_tradeoff()
    print("All 4 figures generated successfully in ./img/")
