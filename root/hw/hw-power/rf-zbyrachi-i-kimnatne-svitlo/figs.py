# -*- coding: utf-8 -*-
"""Фігури до теми «RF-збирачі й кімнатне світло» (мікрозбирачі енергії).

Фігури:
  indoor-vs-outdoor-spectrum.svg — спектральний розподіл сонця AM1.5 проти штучного освітлення (LED, люмінесцентна лампа) та смуги поглинання c-Si, a-Si й перовскіту.
  rf-rectenna-architecture.svg   — функціональна схема RF-збирача: антена, узгоджувальний LC-контур, помножувач Діксона на діодах Шотткі, накопичувач і PMIC.
  rf-power-vs-efficiency.svg     — графік ККД випрямлення (PCE) та вихідної напруги від вхідної RF-потужності (-35...+10 dBm) з позначенням порогових зон.
  power-cycle-hysteresis.svg     — часова діаграма гістерезисного циклу безбатарейного живлення: накопичення мікроенергії, активний імпульс та повернення в сон.

Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. indoor-vs-outdoor-spectrum.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_spectrum():
    W, H = 880, 370
    p = []

    ox, oy = 80, 300
    gw, gh = 740, 230
    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=4))

    def l2x(wl):
        return ox + (wl - 350) / 800.0 * gw

    for y_val, lbl in [(0.25, "25%"), (0.50, "50%"), (0.75, "75%"), (1.00, "100%")]:
        y_pos = oy - y_val * gh
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#eaedf0", sw=1.0, dash="3 3"))
        p.append(text(ox - 10, y_pos + 4, lbl, size=11, color=MUTED, anchor="end"))

    for wl in [400, 500, 600, 700, 800, 900, 1000, 1100]:
        x_pos = l2x(wl)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=LINE, sw=1.2))
        p.append(text(x_pos, oy + 18, "%d" % wl, size=11, color=INK, anchor="middle"))

    p.append(line(ox, oy, ox + gw + 10, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy, ox, oy - gh - 10, color=LINE, sw=1.6))
    p.append(text(ox + gw / 2, oy + 38, "Довжина хвилі світла λ (нм)", size=13, color=INK, bold=True))
    p.append(text(ox - 48, oy - gh / 2, "Відносна густина", size=12, color=INK, bold=True))

    vx1, vx2 = l2x(400), l2x(700)
    p.append(line(vx1, oy, vx1, oy - gh, color="#b45309", sw=1.0, dash="2 2"))
    p.append(line(vx2, oy, vx2, oy - gh, color="#b45309", sw=1.0, dash="2 2"))
    p.append(text((vx1 + vx2) / 2, oy - gh + 18, "Видиме світло (400–700 нм)", size=11, color="#b45309", bold=True))

    # Сонце AM1.5
    sun_pts = []
    for wl in range(350, 1151, 10):
        x = l2x(wl)
        rel = math.exp(-((wl - 500) / 260.0)**2) * 0.95 + 0.05
        if wl > 700:
            rel *= (1.0 - (wl - 700) * 0.0006)
        y = oy - rel * gh
        sun_pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#d97706" stroke-width="2.2" stroke-dasharray="6 3"/>' % " ".join(sun_pts))

    # LED 4000K
    led_pts = []
    for wl in range(380, 751, 5):
        x = l2x(wl)
        p_blue = 0.90 * math.exp(-((wl - 450) / 18.0)**2)
        p_phos = 0.72 * math.exp(-((wl - 570) / 65.0)**2)
        rel = min(1.0, p_blue + p_phos)
        y = oy - rel * gh
        led_pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.6"/>' % " ".join(led_pts))

    # Межі забороненої зони напівпровідників
    bands = [
        (688, "a-Si (1.8 еВ)", "#059669", oy - gh + 42, 0),
        (775, "Перовскіт (1.6 еВ)", "#7c3aed", oy - gh + 68, 0),
        (1107, "c-Si (1.1 еВ)", "#dc2626", oy - gh + 42, -50)
    ]
    for wl, name, col, y_lbl, dx in bands:
        x_m = l2x(wl)
        p.append(line(x_m, oy, x_m, oy - gh + 80, color=col, sw=1.5, dash="4 4"))
        p.append(rect(x_m - 50 + dx, y_lbl - 11, 100, 20, fill="#ffffff", stroke=col, sw=1.2, rx=3))
        p.append(text(x_m + dx, y_lbl + 3, name, size=10, color=col, bold=True))

    # Легенда розміщена вгорі праворуч
    lx, ly = ox + gw - 220, oy - gh + 140
    p.append(rect(lx, ly, 210, 68, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(line(lx + 10, ly + 16, lx + 38, ly + 16, color="#d97706", sw=2.2, dash="6 3"))
    p.append(text(lx + 45, ly + 20, "Сонце AM1.5", size=10, color=INK, anchor="start"))
    p.append(line(lx + 10, ly + 36, lx + 38, ly + 36, color="#2563eb", sw=2.6))
    p.append(text(lx + 45, ly + 40, "LED 4000K", size=10, color=INK, anchor="start"))
    p.append(line(lx + 10, ly + 54, lx + 38, ly + 54, color="#7c3aed", sw=1.6, dash="4 4"))
    p.append(text(lx + 45, ly + 58, "Межа поглинання", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, 'indoor-vs-outdoor-spectrum.svg'), W, H, *p,
           title="Спектральне узгодження кімнатного освітлення з фотоматеріалами")


# ─────────────────────────────────────────────────────────────────────────────
# 2. rf-rectenna-architecture.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_rectenna():
    W, H = 900, 310
    p = []

    # 1. Антена
    p.append(rect(30, 70, 110, 150, fill="#f1f5f9", stroke="#475569", sw=1.6, rx=6))
    p.append(line(85, 95, 85, 135, color=POS, sw=3.0))
    p.append(circle(85, 95, 4, fill=POS, stroke=POS))
    p.append(line(85, 155, 85, 195, color=NEG, sw=3.0))
    p.append(circle(85, 195, 4, fill=NEG, stroke=NEG))
    p.append(text(85, 148, "RF-хвиля", size=10, color=MUTED, bold=True))
    p.append(text(85, 210, "Антена (50 Ом)", size=11, color=INK, bold=True))

    # Стрілка 1 -> 2
    p.append(arrow(140, 145, 170, 145, color=LINE, sw=2.0))
    p.append(text(155, 135, "V_rf", size=10, color=MUTED, italic=True))

    # 2. Узгоджувальний контур
    p.append(rect(170, 70, 140, 150, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=6))
    p.append(text(240, 95, "LC-узгодження", size=12, color="#0369a1", bold=True))
    p.append(text(240, 113, "(Matching Network)", size=10, color="#0369a1"))
    p.append(line(185, 145, 210, 145, color=LINE, sw=1.5))
    p.append(rect(210, 138, 25, 14, fill="#ffffff", stroke=LINE, sw=1.4, rx=2))
    p.append(text(222, 149, "L", size=10, color=INK, bold=True))
    p.append(line(235, 145, 260, 145, color=LINE, sw=1.5))
    p.append(line(260, 145, 260, 158, color=LINE, sw=1.5))
    p.append(line(252, 158, 268, 158, color=LINE, sw=1.6))
    p.append(line(252, 163, 268, 163, color=LINE, sw=1.6))
    p.append(line(260, 163, 260, 175, color=LINE, sw=1.5))
    p.append(line(252, 175, 268, 175, color=LINE, sw=1.5))  # земля
    p.append(line(260, 145, 295, 145, color=LINE, sw=1.5))
    p.append(text(240, 205, "Q-трансформація V", size=10, color="#0369a1", bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(310, 145, 340, 145, color=LINE, sw=2.0))
    p.append(text(325, 135, "Q·V_rf", size=10, color=POS, bold=True))

    # 3. Помножувач Діксона
    p.append(rect(340, 70, 200, 150, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(440, 95, "Помножувач Діксона", size=12, color="#92400e", bold=True))
    p.append(text(440, 113, "Діоди Шотткі (HSMS/SMS)", size=10, color="#92400e"))
    p.append(line(355, 145, 375, 145, color=LINE, sw=1.4))
    # C1
    p.append(line(375, 138, 375, 152, color=LINE, sw=1.5))
    p.append(line(379, 138, 379, 152, color=LINE, sw=1.5))
    p.append(line(379, 145, 410, 145, color=LINE, sw=1.4))
    # D1 (вертикально на землю)
    p.append(line(410, 145, 410, 158, color=LINE, sw=1.4))
    p.append('<polygon points="405,158 415,158 410,168" fill="#d97706" stroke="#92400e" stroke-width="1.2"/>')
    p.append(line(405, 168, 415, 168, color="#92400e", sw=1.4))
    p.append(line(410, 168, 410, 175, color=LINE, sw=1.4))
    p.append(line(403, 175, 417, 175, color=LINE, sw=1.4))
    # D2 (горизонтально вперед)
    p.append(line(410, 145, 435, 145, color=LINE, sw=1.4))
    p.append('<polygon points="435,140 435,150 445,145" fill="#d97706" stroke="#92400e" stroke-width="1.2"/>')
    p.append(line(445, 140, 445, 150, color="#92400e", sw=1.4))
    p.append(line(445, 145, 475, 145, color=LINE, sw=1.4))
    # Точки N-каскадів
    p.append(circle(485, 145, 2, fill=LINE, stroke="none"))
    p.append(circle(495, 145, 2, fill=LINE, stroke="none"))
    p.append(line(505, 145, 525, 145, color=LINE, sw=1.4))
    p.append(text(440, 205, "N каскадів (V_out ≈ 2N·V)", size=10, color="#92400e", bold=True))

    # Стрілка 3 -> 4
    p.append(arrow(540, 145, 570, 145, color=LINE, sw=2.0))
    p.append(text(555, 135, "V_dc", size=10, color=MUTED))

    # 4. Накопичувач
    p.append(rect(570, 70, 115, 150, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(627, 95, "Накопичувач", size=12, color="#065f46", bold=True))
    p.append(text(627, 113, "C_store", size=10, color="#065f46"))
    p.append(line(585, 145, 627, 145, color=LINE, sw=1.4))
    p.append(line(627, 145, 627, 155, color=LINE, sw=1.4))
    p.append(line(617, 155, 637, 155, color="#059669", sw=2.2))
    p.append(line(617, 161, 637, 161, color="#059669", sw=2.2))
    p.append(line(627, 161, 627, 175, color=LINE, sw=1.4))
    p.append(line(619, 175, 635, 175, color=LINE, sw=1.4))
    p.append(line(627, 145, 665, 145, color=LINE, sw=1.4))
    p.append(text(627, 200, "100–1000 мкФ", size=10, color="#065f46", bold=True))

    # Стрілка 4 -> 5
    p.append(arrow(685, 145, 715, 145, color=LINE, sw=2.0))

    # 5. PMIC та навантаження
    p.append(rect(715, 70, 155, 150, fill="#fdf2f8", stroke="#db2777", sw=1.6, rx=6))
    p.append(text(792, 95, "PMIC збирача", size=12, color="#9d174d", bold=True))
    p.append(text(792, 113, "(AEM / BQ25570)", size=10, color="#9d174d"))
    p.append(rect(730, 126, 125, 34, fill="#ffffff", stroke="#db2777", sw=1.0, rx=3))
    p.append(text(792, 144, "MPPT + Cold-Start", size=10, color=INK, bold=True))
    p.append(rect(730, 166, 125, 42, fill="#ffffff", stroke="#db2777", sw=1.0, rx=3))
    p.append(text(792, 182, "Безбатарейний вузол", size=10, color=POS, bold=True))
    p.append(text(792, 198, "MCU + BLE / LoRa", size=9, color=MUTED))

    # Нижня стрічка пояснення
    p.append(rect(30, 240, 840, 50, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=5))
    p.append(text(450, 260, "Тракт: Антена (-20 dBm) -> Резонансний підйом напруги -> Багатокаскадне випрямлення -> Живлення MCU", size=11, color=INK))
    p.append(text(450, 278, "Сумарний ККД тракту (PCE) критично залежить від вхідної потужності та порогової напруги діодів", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, 'rf-rectenna-architecture.svg'), W, H, *p,
           title="Архітектура RF-ректени: від антени до безбатарейного мікроконтролера")


# ─────────────────────────────────────────────────────────────────────────────
# 3. rf-power-vs-efficiency.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_rf_curve():
    W, H = 880, 370
    p = []

    ox, oy = 85, 300
    gw, gh = 720, 230
    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=4))

    def db2x(db):
        return ox + (db - (-35)) / 45.0 * gw

    for pce, lbl in [(0.2, "20%"), (0.4, "40%"), (0.6, "60%"), (0.8, "80%")]:
        y_pos = oy - (pce / 0.8) * gh
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#eaedf0", sw=1.0, dash="3 3"))
        p.append(text(ox - 10, y_pos + 4, lbl, size=11, color=MUTED, anchor="end"))

    for db in [-35, -30, -25, -20, -15, -10, -5, 0, 5, 10]:
        x_pos = db2x(db)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=LINE, sw=1.2))
        p.append(text(x_pos, oy + 18, "%d" % db, size=11, color=INK, anchor="middle"))

    p.append(line(ox, oy, ox + gw + 10, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy, ox, oy - gh - 10, color=LINE, sw=1.6))
    p.append(text(ox + gw / 2, oy + 38, "Вхідна потужність RF-сигналу P_in (dBm)", size=13, color=INK, bold=True))
    p.append(text(ox - 48, oy - gh / 2, "ККД (PCE)", size=12, color=INK, bold=True))

    # Зони (через вертикальні розділювачі)
    z1_x = db2x(-25)
    z2_x = db2x(-5)
    p.append(line(z1_x, oy, z1_x, oy - gh + 50, color="#b91c1c", sw=1.2, dash="3 3"))
    p.append(line(z2_x, oy, z2_x, oy - gh + 50, color="#15803d", sw=1.2, dash="3 3"))

    p.append(text((ox + z1_x) / 2, oy - gh + 18, "Мертва зона", size=11, color="#b91c1c", bold=True))
    p.append(text((ox + z1_x) / 2, oy - gh + 34, "PCE < 2%", size=10, color="#b91c1c"))

    p.append(text((z1_x + z2_x) / 2, oy - gh + 18, "Розсіяний фон (Wi-Fi / GSM)", size=11, color="#854d0e", bold=True))
    p.append(text((z1_x + z2_x) / 2, oy - gh + 34, "PCE 5%..45%", size=10, color="#854d0e"))

    p.append(text((z2_x + ox + gw) / 2, oy - gh + 18, "Виділений передавач (WPT)", size=11, color="#15803d", bold=True))
    p.append(text((z2_x + ox + gw) / 2, oy - gh + 34, "PCE 60–75%", size=10, color="#15803d"))

    # Крива 1: Шотткі
    sch_pts = []
    for db_i in range(-350, 101, 5):
        db = db_i / 10.0
        x = db2x(db)
        val = 0.72 / (1.0 + math.exp(-(db - (-12)) / 5.5))
        if db > 2:
            val *= (1.0 - (db - 2) * 0.02)
        y = oy - (val / 0.8) * gh
        sch_pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="3.0"/>' % " ".join(sch_pts))

    # Крива 2: Стандартний діод
    std_pts = []
    for db_i in range(-350, 101, 5):
        db = db_i / 10.0
        x = db2x(db)
        val = 0.65 / (1.0 + math.exp(-(db - (-3)) / 5.0))
        if db > 5:
            val *= (1.0 - (db - 5) * 0.015)
        y = oy - (val / 0.8) * gh
        std_pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#dc2626" stroke-width="2.0" stroke-dasharray="5 4"/>' % " ".join(std_pts))

    # Легенда розміщена внизу праворуч
    lx, ly = ox + gw - 280, oy - 70
    p.append(rect(lx, ly, 270, 56, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(line(lx + 10, ly + 16, lx + 40, ly + 16, color="#2563eb", sw=3.0))
    p.append(text(lx + 48, ly + 20, "Детекторний Шотткі (SMS7630)", size=10, color=INK, anchor="start", bold=True))
    p.append(line(lx + 10, ly + 38, lx + 40, ly + 38, color="#dc2626", sw=2.0, dash="5 4"))
    p.append(text(lx + 48, ly + 42, "Звичайний випрямний діод", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, 'rf-power-vs-efficiency.svg'), W, H, *p,
           title="Крива енергетичної ефективності (PCE) ректени від рівня вхідного RF-сигналу")


# ─────────────────────────────────────────────────────────────────────────────
# 4. power-cycle-hysteresis.svg
# ─────────────────────────────────────────────────────────────────────────────
def fig_hysteresis():
    W, H = 880, 370
    p = []

    ox, oy = 85, 300
    gw, gh = 720, 230
    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=4))

    def v2y(v):
        return oy - (v / 4.0) * gh

    y_chg = v2y(3.3)
    y_dis = v2y(2.0)

    p.append(line(ox, y_chg, ox + gw, y_chg, color="#059669", sw=1.4, dash="5 4"))
    p.append(text(ox - 10, y_chg + 4, "V_chg (3.3 В)", size=11, color="#059669", bold=True, anchor="end"))

    p.append(line(ox, y_dis, ox + gw, y_dis, color="#dc2626", sw=1.4, dash="5 4"))
    p.append(text(ox - 10, y_dis + 4, "V_dis (2.0 В)", size=11, color="#dc2626", bold=True, anchor="end"))

    p.append(line(ox, oy, ox + gw + 10, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy, ox, oy - gh - 10, color=LINE, sw=1.6))
    p.append(text(ox + gw / 2, oy + 38, "Час t (секунди / хвилини)", size=13, color=INK, bold=True))
    p.append(text(ox - 48, oy - gh / 2, "Напруга V_cap", size=12, color=INK, bold=True))

    pts = []
    for x_i in range(0, 121, 5):
        t_n = x_i / 120.0
        v = 3.3 * (1.0 - math.exp(-2.8 * t_n))
        pts.append("%.1f,%.1f" % (ox + x_i, v2y(v)))

    pts.append("%.1f,%.1f" % (ox + 120, v2y(3.3)))
    pts.append("%.1f,%.1f" % (ox + 140, v2y(2.45)))

    for x_i in range(140, 381, 10):
        t_n = (x_i - 140) / 240.0
        v = 2.45 + (3.3 - 2.45) * (1.0 - math.exp(-2.5 * t_n)) / (1.0 - math.exp(-2.5))
        pts.append("%.1f,%.1f" % (ox + x_i, v2y(v)))

    pts.append("%.1f,%.1f" % (ox + 380, v2y(3.3)))
    pts.append("%.1f,%.1f" % (ox + 400, v2y(2.45)))

    for x_i in range(400, 641, 10):
        t_n = (x_i - 400) / 240.0
        v = 2.45 + (3.3 - 2.45) * (1.0 - math.exp(-2.5 * t_n)) / (1.0 - math.exp(-2.5))
        pts.append("%.1f,%.1f" % (ox + x_i, v2y(v)))

    pts.append("%.1f,%.1f" % (ox + 640, v2y(3.3)))
    pts.append("%.1f,%.1f" % (ox + 660, v2y(2.45)))

    for x_i in range(660, 711, 10):
        t_n = (x_i - 660) / 240.0
        v = 2.45 + (3.3 - 2.45) * (1.0 - math.exp(-2.5 * t_n)) / (1.0 - math.exp(-2.5))
        pts.append("%.1f,%.1f" % (ox + x_i, v2y(v)))

    p.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.8"/>' % " ".join(pts))

    # Маленькі мітки TX вгорі
    p.append(rect(ox + 120, oy - gh + 5, 20, 20, fill="#fecaca", stroke="#ef4444", sw=1.0, rx=2))
    p.append(text(ox + 130, oy - gh + 19, "TX", size=9, color="#991b1b", bold=True))

    p.append(rect(ox + 380, oy - gh + 5, 20, 20, fill="#fecaca", stroke="#ef4444", sw=1.0, rx=2))
    p.append(text(ox + 390, oy - gh + 19, "TX", size=9, color="#991b1b", bold=True))

    p.append(rect(ox + 640, oy - gh + 5, 20, 20, fill="#fecaca", stroke="#ef4444", sw=1.0, rx=2))
    p.append(text(ox + 650, oy - gh + 19, "TX", size=9, color="#991b1b", bold=True))

    p.append(text(ox + 60, v2y(0.7), "Холодний старт", size=10, color=MUTED, bold=True))
    p.append(text(ox + 260, v2y(1.5), "Повільне накопичення (I_sleep < 1 мкА)", size=10, color="#1e40af", bold=True))
    p.append(text(ox + 520, v2y(1.5), "Повільне накопичення (I_in ≈ 20 мкА)", size=10, color="#1e40af", bold=True))

    # Пояснювальний блок вгорі посередині
    p.append(rect(ox + 160, oy - gh + 15, 200, 52, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(ox + 260, oy - gh + 34, "ΔE = 0.5 · C · (V_chg² − V_dis²)", size=10, color=INK, bold=True))
    p.append(text(ox + 260, oy - gh + 52, "Робочий діапазон: 3.3 В -> 2.45 В", size=9, color="#059669", bold=True))

    render(os.path.join(OUT, 'power-cycle-hysteresis.svg'), W, H, *p,
           title="Гістерезисний цикл безбатарейного живлення: накопичення та імпульсна активність")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig_spectrum()
    fig_rectenna()
    fig_rf_curve()
    fig_hysteresis()
    print("Згенеровано 4 фігури у", OUT)
