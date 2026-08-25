# -*- coding: utf-8 -*-
"""Фігури до теми «Іоносферна затримка радіосигналу».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і примітиви — зі спільного svgkit.
"""
import sys, os
import math

# Підключаємо scripts/ з кореня репо (4 рівні вгору від book/physics/electromagnetism/ionospheric-delay)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT  = "#16a34a"  # Зелений
DARK    = "#0f172a"  # Темний
BLUE    = "#2563eb"  # Синій
RED     = "#dc2626"  # Червоний
AMBER   = "#d97706"  # Янтарний
PURPLE  = "#9333ea"  # Фіолетовий
GREY    = "#64748b"  # Сірий
LIGHT_BG= "#f8fafc"  # Світле тло
WHITE   = "#ffffff"

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


# ── 1. Будова іоносферних шарів та профіль N_e(h) ─────────────────────────────
def fig_ionosphere_layers():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=WHITE, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Будова іоносфери Землі та профіль електронної густини", size=16, bold=True, color=DARK))

    ax_x = 95
    ax_w = 340
    
    def h2y(h):
        return 410 - (h / 600.0) * 340.0

    f.append(rect(ax_x, h2y(50), ax_w, h2y(0) - h2y(50), fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(25), "Нейтральна атмосфера (0–50 км)", size=11, color=GREY, anchor="start"))

    f.append(rect(ax_x, h2y(90), ax_w, h2y(60) - h2y(90), fill="#fef3c7", stroke="#fde047", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(75), "D-шар (60–90 км): зникає вночі", size=11, color=AMBER, anchor="start", bold=True))

    f.append(rect(ax_x, h2y(150), ax_w, h2y(90) - h2y(150), fill="#fed7aa", stroke="#f97316", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(120), "E-шар (90–150 км): рекомбінація вночі", size=11, color="#c2410c", anchor="start", bold=True))

    f.append(rect(ax_x, h2y(210), ax_w, h2y(150) - h2y(210), fill="#e0e7ff", stroke="#818cf8", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(180), "F1-шар (150–210 км): денний шар", size=11, color=BLUE, anchor="start", bold=True))

    f.append(rect(ax_x, h2y(450), ax_w, h2y(210) - h2y(450), fill="#dcfce7", stroke="#4ade80", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(330), "F2-шар (210–450 км): максимум Ne", size=12, color=ACCENT, anchor="start", bold=True))
    f.append(text(ax_x + 15, h2y(305), "Головний внесок у TEC і затримку", size=11, color=DARK, anchor="start", italic=True))

    f.append(rect(ax_x, h2y(600), ax_w, h2y(450) - h2y(600), fill="#fae8ff", stroke="#e879f9", sw=1, rx=0))
    f.append(text(ax_x + 15, h2y(525), "Зовнішня іоносфера / плазмасфера (>450 км)", size=11, color=PURPLE, anchor="start"))

    f.append(line(ax_x - 10, h2y(0), ax_x + ax_w + 10, h2y(0), color=DARK, sw=3))
    f.append(text(ax_x + ax_w / 2, h2y(0) + 20, "Поверхня Землі (h = 0 км)", size=12, bold=True, color=DARK))

    f.append(line(ax_x, h2y(0), ax_x, h2y(600), color=DARK, sw=1.5))
    for h in [0, 100, 200, 300, 400, 500, 600]:
        y_p = h2y(h)
        f.append(line(ax_x - 5, y_p, ax_x, y_p, color=DARK, sw=1.5))
        f.append(text(ax_x - 8, y_p + 4, "%d" % h, size=11, color=DARK, anchor="end"))
    f.append(text(ax_x - 55, h2y(300), "Висота h (км)", size=12, bold=True, color=DARK, anchor="middle"))

    prof_x = 490
    prof_w = 310
    f.append(rect(prof_x, 60, prof_w, 350, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    f.append(text(prof_x + prof_w / 2, 82, "Концентрація електронів Ne(h)", size=13, bold=True, color=DARK))

    gx0 = prof_x + 40
    gy0 = 380
    gx_w = prof_w - 65
    gy_h = 270

    f.append(arrow(gx0, gy0, gx0 + gx_w + 10, gy0, color=DARK, sw=1.5))
    f.append(arrow(gx0, gy0, gx0, gy0 - gy_h - 10, color=DARK, sw=1.5))
    f.append(text(gx0 + gx_w / 2, gy0 + 25, "Електронна густина Ne (10¹² м⁻³)", size=11, color=DARK))
    f.append(text(gx0 - 10, gy0 - gy_h, "h (км)", size=11, color=DARK, anchor="end"))

    y_max = gy0 - (350.0 / 600.0) * gy_h
    f.append(line(gx0, y_max, gx0 + gx_w, y_max, color=ACCENT, sw=1.2, dash="4,4"))
    f.append(text(gx0 + gx_w - 5, y_max - 8, "hmF2 ≈ 300–350 км", size=10, color=ACCENT, bold=True, anchor="end"))

    pts_day = []
    pts_night = []
    for step in range(61):
        h_val = step * 10.0
        y_val = gy0 - (h_val / 600.0) * gy_h
        
        ne_day = 1.2 * math.exp(1.0 - (h_val - 320.0)/80.0 - math.exp(-(h_val - 320.0)/80.0))
        if h_val < 200:
            ne_day += 0.15 * math.exp(-((h_val - 110.0)/25.0)**2)
        x_day = gx0 + (ne_day / 1.4) * gx_w
        pts_day.append("%.1f,%.1f" % (x_day, y_val))

        ne_night = 0.3 * math.exp(1.0 - (h_val - 350.0)/70.0 - math.exp(-(h_val - 350.0)/70.0))
        x_night = gx0 + (ne_night / 1.4) * gx_w
        pts_night.append("%.1f,%.1f" % (x_night, y_val))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_day), ACCENT))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' % (" ".join(pts_night), BLUE))

    f.append(line(gx0 + 20, 115, gx0 + 50, 115, color=ACCENT, sw=2.5))
    f.append(text(gx0 + 55, 119, "День (Ne_max ≈ 1.2·10¹²)", size=11, color=DARK, anchor="start"))

    f.append(line(gx0 + 20, 135, gx0 + 50, 135, color=BLUE, sw=2, dash="5,4"))
    f.append(text(gx0 + 55, 139, "Ніч (Ne_max ≈ 0.3·10¹²)", size=11, color=DARK, anchor="start"))

    f.append(circle(ax_x + ax_w - 30, 45, 16, fill="#fef08a", stroke=AMBER, sw=1.5))
    f.append(text(ax_x + ax_w - 30, 49, "УФ", size=10, bold=True, color="#b45309"))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % DARK)
    out.extend(f)
    out.append(' </svg>')
    
    with open(os.path.join(OUT_DIR, 'ionosphere-layers.svg'), 'w', encoding='utf-8') as file:
        file.write("\n".join(out))


# ── 2. Фазова швидкість проти групової затримки ─────────────────────────────
def fig_phase_vs_group_delay():
    W, H = 820, 430
    f = [rect(0, 0, W, H, fill=WHITE, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Дисперсійний парадокс плазми: фазове прискорення та групова затримка", size=15, bold=True, color=DARK))

    box1_y = 55
    f.append(rect(30, box1_y, 760, 145, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(50, box1_y + 22, "1. Вакуум (n = 1): ненапрямлене середовище без дисперсії", size=13, bold=True, color=DARK, anchor="start"))

    wav_y1 = box1_y + 80
    f.append(line(60, wav_y1, 600, wav_y1, color="#94a3b8", sw=1, dash="3,3"))

    pts_env1 = []
    pts_carrier1 = []
    for x_p in range(60, 601):
        x_rel = (x_p - 280) / 65.0
        env = 35.0 * math.exp(-x_rel**2)
        carrier = env * math.cos(0.18 * (x_p - 60))
        pts_env1.append("%.1f,%.1f" % (x_p, wav_y1 - env))
        pts_carrier1.append("%.1f,%.1f" % (x_p, wav_y1 - carrier))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (" ".join(pts_env1), GREY))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_carrier1), BLUE))

    f.append(textbox(700, wav_y1, "v_p = c\nv_g = c\nΔR = 0", size=11, fill=WHITE, stroke=BLUE, color=DARK)[0])

    box2_y = 215
    f.append(rect(30, box2_y, 760, 195, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    f.append(text(50, box2_y + 22, "2. Плазма іоносфери (n_p < 1, n_g > 1): дисперсійне середовище", size=13, bold=True, color=DARK, anchor="start"))

    wav_y2 = box2_y + 95
    f.append(line(60, wav_y2, 600, wav_y2, color="#94a3b8", sw=1, dash="3,3"))

    pts_env2 = []
    pts_carrier2 = []
    for x_p in range(60, 601):
        x_rel_g = (x_p - (280 - 45)) / 65.0
        env = 35.0 * math.exp(-x_rel_g**2)
        carrier = env * math.cos(0.18 * (x_p - 60 - 35))
        pts_env2.append("%.1f,%.1f" % (x_p, wav_y2 - env))
        pts_carrier2.append("%.1f,%.1f" % (x_p, wav_y2 - carrier))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' % (" ".join(pts_env2), RED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_carrier2), ACCENT))

    f.append(arrow(280, wav_y2 - 42, 280 - 45, wav_y2 - 42, color=RED, sw=2))
    f.append(text(280 - 22, wav_y2 - 50, "Групова затримка коду (v_g < c)", size=11, bold=True, color=RED))

    f.append(arrow(280, wav_y2 + 42, 280 + 35, wav_y2 + 42, color=ACCENT, sw=2))
    f.append(text(280 + 18, wav_y2 + 56, "Фазове прискорення несучої (v_p > c)", size=11, bold=True, color=ACCENT))

    f.append(textbox(700, wav_y2 - 45, "Код PRN (обвідна):\nv_g = c / n_g < c\nΔR_g = + (40.3/f²) TEC", size=10, fill=WHITE, stroke=RED, color=DARK)[0])
    f.append(textbox(700, wav_y2 + 40, "Фаза несучої:\nv_p = c / n_p > c\nΔR_p = − (40.3/f²) TEC", size=10, fill=WHITE, stroke=ACCENT, color=DARK)[0])

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % DARK)
    out.extend(f)
    out.append(' </svg>')
    
    with open(os.path.join(OUT_DIR, 'phase-vs-group-delay.svg'), 'w', encoding='utf-8') as file:
        file.write("\n".join(out))


# ── 3. Двочастотна дисперсія радіохвиль ─────────────────────────────────────
def fig_dual_frequency_dispersion():
    W, H = 860, 420
    f = [rect(0, 0, W, H, fill=WHITE, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Принцип двочастотної компенсації іоносферної затримки (L1 / L2)", size=15, bold=True, color=DARK))

    sat_x, sat_y = 430, 65
    f.append(rect(sat_x - 30, sat_y - 12, 60, 24, fill="#334155", stroke=DARK, sw=1.5, rx=4))
    f.append(line(sat_x - 60, sat_y, sat_x - 30, sat_y, color=BLUE, sw=3))
    f.append(line(sat_x + 30, sat_y, sat_x + 60, sat_y, color=BLUE, sw=3))
    f.append(text(sat_x, sat_y + 4, "GNSS", size=10, bold=True, color=WHITE))
    f.append(text(sat_x, sat_y - 20, "Супутник (передає L1 та L2 одночасно)", size=11, bold=True, color=DARK))

    iono_y1, iono_y2 = 160, 240
    f.append(rect(60, iono_y1, 740, iono_y2 - iono_y1, fill="#dcfce7", stroke="#4ade80", sw=1.5, rx=6))
    f.append(text(80, iono_y1 + 25, "Іоносфера (плазма, TEC)", size=12, bold=True, color=ACCENT, anchor="start"))
    f.append(text(80, iono_y1 + 45, "Затримка ΔR ~ 1 / f²", size=11, color=DARK, anchor="start"))

    rx_x, rx_y = 430, 360
    f.append(circle(rx_x, rx_y, 14, fill=AMBER, stroke=DARK, sw=1.5))
    f.append(line(rx_x, rx_y + 14, rx_x, rx_y + 30, color=DARK, sw=2))
    f.append(line(rx_x - 20, rx_y + 30, rx_x + 20, rx_y + 30, color=DARK, sw=3))
    f.append(text(rx_x, rx_y + 48, "Приймач на Землі", size=12, bold=True, color=DARK))

    f.append(line(sat_x - 5, sat_y + 12, sat_x - 15, iono_y1, color=BLUE, sw=2))
    f.append(line(sat_x + 5, sat_y + 12, sat_x + 15, iono_y1, color=RED, sw=2))

    f.append(line(sat_x - 15, iono_y1, sat_x - 40, iono_y2, color=BLUE, sw=2.5))
    f.append(line(sat_x + 15, iono_y1, sat_x + 40, iono_y2, color=RED, sw=2.5))

    f.append(arrow(sat_x - 40, iono_y2, rx_x - 12, rx_y - 14, color=BLUE, sw=2.5))
    f.append(arrow(sat_x + 40, iono_y2, rx_x + 12, rx_y - 14, color=RED, sw=2.5))

    f.append(text(70, 270, "L1 (1575.42 МГц):\nΔR1 = 40.3·TEC / f1²\n(наприклад, 5.0 м)", size=11, color=BLUE, anchor="start"))
    f.append(text(500, 270, "L2 (1227.60 МГц):\nΔR2 = 40.3·TEC / f2²\n(наприклад, 8.23 м)", size=11, color=RED, anchor="start"))

    f.append(textbox(160, 350, "Різниця вимірів:\nΔR2 − ΔR1 ~ TEC · (1/f2² − 1/f1²)\n⇒ Прямий розрахунок TEC", size=11, fill="#f8fafc", stroke=GREY, color=DARK)[0])
    f.append(textbox(700, 350, "Безіоносферна комбінація (IF):\nP_IF = 2.546·P1 − 1.546·P2\nУсуває ~99% затримки!", size=11, fill="#f0fdf4", stroke=ACCENT, color=DARK)[0])

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % DARK)
    out.extend(f)
    out.append(' </svg>')
    
    with open(os.path.join(OUT_DIR, 'dual-frequency-dispersion.svg'), 'w', encoding='utf-8') as file:
        file.write("\n".join(out))


# ── 4. Модель Клобучара: добовий хід затримки ──────────────────────────────
def fig_klobuchar_diurnal_model():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=WHITE, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Модель Клобучара: апроксимація добового ходу іоносферної затримки", size=15, bold=True, color=DARK))

    ox0, oy0 = 120, 350
    gx_w, gy_h = 580, 260

    f.append(arrow(ox0, oy0, ox0 + gx_w + 20, oy0, color=DARK, sw=1.5))
    f.append(arrow(ox0, oy0, ox0, oy0 - gy_h - 15, color=DARK, sw=1.5))

    f.append(text(ox0 + gx_w / 2, oy0 + 35, "Місцевий сонячний час t (години доби)", size=12, bold=True, color=DARK))
    f.append(text(ox0 + 10, oy0 - gy_h - 10, "Затримка I (нс / м)", size=11, bold=True, color=DARK, anchor="start"))

    hours = [0, 6, 12, 14, 18, 24]
    for hr in hours:
        xp = ox0 + (hr / 24.0) * gx_w
        f.append(line(xp, oy0, xp, oy0 + 5, color=DARK, sw=1.5))
        lbl = "%02d:00" % hr
        if hr == 14:
            lbl += " (пік)"
            f.append(text(xp, oy0 + 18, lbl, size=10, bold=True, color=RED))
        else:
            f.append(text(xp, oy0 + 18, lbl, size=10, color=DARK))
        f.append(line(xp, oy0, xp, oy0 - gy_h, color="#f1f5f9", sw=1, dash="2,2"))

    y_night = oy0 - 35
    f.append(line(ox0, y_night, ox0 + gx_w, y_night, color=BLUE, sw=1.5, dash="4,4"))
    f.append(text(ox0 + 10, y_night - 8, "Нічний постійний поріг = 5 нс (≈1.5 м)", size=11, bold=True, color=BLUE, anchor="start"))

    pts_klob = []
    t_peak = 14.0
    period_hr = 12.0
    amp_ns = 140.0

    for step in range(241):
        t_hr = step / 10.0
        xp = ox0 + (t_hr / 24.0) * gx_w
        
        dt = t_hr - t_peak
        if abs(dt) < (period_hr / 4.0):
            x_phase = (2.0 * math.pi * dt) / period_hr
            val_ns = 5.0 + amp_ns * math.cos(x_phase)
        else:
            val_ns = 5.0
        
        yp = oy0 - (val_ns / 180.0) * gy_h
        pts_klob.append("%.1f,%.1f" % (xp, yp))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_klob), RED))

    xp_peak = ox0 + (14.0 / 24.0) * gx_w
    yp_peak = oy0 - ((5.0 + amp_ns) / 180.0) * gy_h

    f.append(line(xp_peak, y_night, xp_peak, yp_peak, color=AMBER, sw=2, dash="3,3"))
    f.append(text(xp_peak + 15, (y_night + yp_peak) / 2, "Амплітуда A (α0..α3)", size=11, bold=True, color=AMBER, anchor="start"))

    xp_start = ox0 + ((14.0 - period_hr/4.0) / 24.0) * gx_w
    xp_end = ox0 + ((14.0 + period_hr/4.0) / 24.0) * gx_w
    f.append(line(xp_start, y_night + 15, xp_end, y_night + 15, color=ACCENT, sw=2))
    f.append(arrow(xp_start + 40, y_night + 15, xp_start, y_night + 15, color=ACCENT, sw=1.5))
    f.append(arrow(xp_end - 40, y_night + 15, xp_end, y_night + 15, color=ACCENT, sw=1.5))
    f.append(text(xp_peak, y_night + 30, "Період P (β0..β3)", size=11, bold=True, color=ACCENT))

    f.append(textbox(620, 100, "Параметри альфа (α0..α3) — амплітуда A(φm)\nПараметри бета (β0..β3) — період P(φm)\nУсуває ~50% среднеквадратичної помилки", size=11, fill="#fffbe7", stroke=AMBER, color=DARK)[0])

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % DARK)
    out.extend(f)
    out.append(' </svg>')
    
    with open(os.path.join(OUT_DIR, 'klobuchar-diurnal-model.svg'), 'w', encoding='utf-8') as file:
        file.write("\n".join(out))


# ── 5. Геометрія пробійної точки іоносфери (IPP) та картографічна функція ──
def fig_ipp_mapping_geometry():
    W, H = 840, 450
    f = [rect(0, 0, W, H, fill=WHITE, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Геометрія проходження радіопроменя крізь тонкий шар іоносфери (IPP)", size=15, bold=True, color=DARK))

    cx, cy = 330, 1050
    r_earth = 760
    h_shell = 110
    r_shell = r_earth + h_shell

    # Обрізаємо дугу поверхні Землі так, щоб вона закінчувалася біля x = 450, НЕ заходячи під картку праворуч
    f.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' % (cx - 300, cy - r_earth + 60, r_earth, r_earth, cx + 130, cy - r_earth + 12, DARK))
    f.append(text(cx - 150, cy - r_earth + 65, "Поверхня Землі (R_E ≈ 6371 км)", size=12, bold=True, color=DARK))

    rx_x = cx - 100
    rx_y = cy - r_earth + 12
    f.append(circle(rx_x, rx_y, 7, fill=RED, stroke=DARK, sw=1.5))
    f.append(text(rx_x - 15, rx_y + 20, "Приймач (Rx)", size=11, bold=True, color=RED, anchor="end"))

    # Дуга іоносфери теж закінчується до картки (x = cx + 150)
    f.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' % (cx - 300, cy - r_shell + 60, r_shell, r_shell, cx + 150, cy - r_shell + 10, ACCENT))
    f.append(text(cx + 100, cy - r_shell + 35, "Тонкий шар іоносфери (hm = 350 км)", size=11, bold=True, color=ACCENT, anchor="start"))

    sat_x, sat_y = cx + 280, 75
    f.append(rect(sat_x - 20, sat_y - 10, 40, 20, fill="#334155", stroke=DARK, sw=1, rx=3))
    f.append(text(sat_x, sat_y - 15, "Супутник (Sat)", size=11, bold=True, color=DARK))

    f.append(line(sat_x, sat_y, rx_x, rx_y, color=BLUE, sw=2))

    ipp_x = rx_x + 0.58 * (sat_x - rx_x)
    ipp_y = rx_y + 0.58 * (sat_y - rx_y)
    f.append(circle(ipp_x, ipp_y, 6, fill=AMBER, stroke=DARK, sw=1.5))
    f.append(text(ipp_x + 12, ipp_y - 12, "IPP (пробійна точка)", size=12, bold=True, color=AMBER, anchor="start"))

    f.append(line(ipp_x, ipp_y - 45, ipp_x, ipp_y + 55, color=GREY, sw=1.2, dash="3,3"))
    f.append(text(ipp_x - 10, ipp_y + 40, "VTEC (зенитний)", size=11, bold=True, color=ACCENT, anchor="end"))

    f.append(line(rx_x, rx_y - 80, rx_x, rx_y + 20, color=GREY, sw=1.2, dash="3,3"))
    f.append(text(rx_x - 10, rx_y - 65, "Зенит", size=11, color=GREY, anchor="end"))

    f.append(text(rx_x + 75, rx_y - 5, "e (елевація)", size=11, bold=True, color=BLUE))
    f.append(text(rx_x + 15, rx_y - 50, "z", size=11, bold=True, color=DARK))

    f.append(textbox(640, 365, "Похилий промінь: STEC = F(e) · VTEC\n\nКартографічний фактор F(e):\nF(e) = 1 / sqrt(1 − (R_E·cos(e) / (R_E + hm))²)\nЗростає від 1.0 (зенит) до ~3.0 (горизонт)", size=11, fill="#f8fafc", stroke=BLUE, color=DARK)[0])

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % DARK)
    out.extend(f)
    out.append(' </svg>')
    
    with open(os.path.join(OUT_DIR, 'ipp-mapping-geometry.svg'), 'w', encoding='utf-8') as file:
        file.write("\n".join(out))


if __name__ == '__main__':
    fig_ionosphere_layers()
    fig_phase_vs_group_delay()
    fig_dual_frequency_dispersion()
    fig_klobuchar_diurnal_model()
    fig_ipp_mapping_geometry()
    print("Усі 5 фігур успішно згенеровано у ./img/")
