# -*- coding: utf-8 -*-
"""Фігури до статті «Атмосферна електрика».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_global_circuit():
    """Фігура 1: Глобальне електричне коло Землі (GEC)."""
    W, H = 840, 520
    f = [text(W / 2, 28, "Глобальне електричне коло Землі (Global Electric Circuit)", size=15, bold=True)]

    # Фон атмосфери
    f.append(rect(40, 60, 760, 410, fill="#F8FAFC", stroke="#CBD5E1", sw=1.5, rx=8))

    # Іоносфера (верхня провідна обкладинка)
    f.append(rect(40, 60, 760, 45, fill="#EFF6FF", stroke="#3B82F6", sw=2, rx=4))
    f.append(text(W / 2, 88, "Іоносфера (висока провідність, потенціал V_ion ≈ +250 кВ)", size=12, bold=True, color="#1E40AF"))

    # Поверхня Землі (нижня провідна обкладинка)
    f.append(rect(40, 425, 760, 45, fill="#ECFDF5", stroke="#10B981", sw=2, rx=4))
    f.append(text(W / 2, 453, "Поверхня Землі (заряд Q_earth ≈ −500 кКл, потенціал V = 0 В)", size=12, bold=True, color="#065F46"))

    # Зона 1: Зона гарної погоди (Fair-weather region)
    f.append(rect(55, 115, 345, 295, fill="#FFFFFF", stroke="#93C5FD", sw=1.2, rx=6))
    f.append(text(227, 138, "Область гарної погоди (~99% поверхні)", size=11.5, bold=True, color="#1D4ED8"))

    # Струм гарної погоди (вертикальний струм витоку J_z) — лінії ліворуч і праворуч від тексту
    for x_arr in [75, 380]:
        f.append(line(x_arr, 155, x_arr, 395, color="#2563EB", sw=2, dash="3 3"))
        f.append(line(x_arr - 6, 385, x_arr, 395, color="#2563EB", sw=2))
        f.append(line(x_arr + 6, 385, x_arr, 395, color="#2563EB", sw=2))

    t_fw = ("Струм витоку (дрейф іонів):\n"
            "• J_z ≈ 2–3 пА/м² (вниз)\n"
            "• Поле E_z ≈ 130 В/м\n"
            "• Опір R_col ≈ 1.3·10¹⁷ Ом·м²\n"
            "• Загальний струм I ≈ 1000–1800 А")
    f.append(mtext(227, 180, t_fw, size=10, color="#1E3A8A", anchor="middle"))

    # Зона 2: Грозовий генератор (Thunderstorm generator)
    f.append(rect(420, 115, 370, 295, fill="#FFFFFF", stroke="#FCA5A5", sw=1.2, rx=6))
    f.append(text(605, 138, "Грозові генератори (~2000 хмар одночасно)", size=10, bold=True, color="#B91C1C"))

    # Грозова хмара Cumulonimbus
    f.append(rect(455, 160, 300, 110, fill="#FEF2F2", stroke="#EF4444", sw=1.5, rx=12))
    f.append(text(605, 180, "Грозова хмара (Cumulonimbus)", size=11, bold=True, color="#991B1B"))

    # Заряд хмари: верх +, низ -
    f.append(text(605, 205, "+ + + + + (Верхня додатна область, +40 Кл)", size=9.5, bold=True, color="#DC2626"))
    f.append(text(605, 250, "− − − − − (Нижня від'ємна область, −40 Кл)", size=9.5, bold=True, color="#2563EB"))

    # Струм вгору до іоносфери від верхівки хмари
    f.append(line(730, 160, 730, 108, color="#DC2626", sw=2.2))
    f.append(line(724, 118, 730, 108, color="#DC2626", sw=2.2))
    f.append(line(736, 118, 730, 108, color="#DC2626", sw=2.2))
    f.append(text(742, 130, "I_up (+ в іоносферу)", size=9.5, bold=True, color="#DC2626", anchor="start"))

    # Процеси заряду хмара-земля
    # 1. Блискавки
    f.append(line(490, 270, 480, 320, color="#D97706", sw=2.5))
    f.append(line(480, 320, 500, 355, color="#D97706", sw=2.5))
    f.append(line(500, 355, 490, 425, color="#D97706", sw=2.5))
    f.append(text(490, 345, "Блискавки (I_l)", size=9, bold=True, color="#B45309"))

    # 2. Коронний розряд вістрів
    f.append(line(605, 425, 605, 335, color="#7C3AED", sw=1.8, dash="2 2"))
    f.append(line(599, 345, 605, 335, color="#7C3AED", sw=1.8))
    f.append(line(611, 345, 605, 335, color="#7C3AED", sw=1.8))
    f.append(text(605, 360, "Корона вістрів", size=9, bold=True, color="#6D28D9"))

    # 3. Струм опадів
    f.append(line(720, 270, 720, 425, color="#2563EB", sw=1.8, dash="3 3"))
    f.append(line(714, 415, 720, 425, color="#2563EB", sw=1.8))
    f.append(line(726, 415, 720, 425, color="#2563EB", sw=1.8))
    f.append(text(720, 345, "Струм опадів", size=9, bold=True, color="#1D4ED8"))

    # Загальний замикаючий контур
    f.append(text(W / 2, 495, "Зарядний струм гроз компенсує струм витоку гарної погоди (I_gen = I_leak)", size=10, italic=True, color="#475569"))

    render(os.path.join(IMG_DIR, "global-circuit.svg"), W, H, *f)


def fig_atmospheric_profile():
    """Фігура 2: Профілі провідності σ(z) та електричного поля E(z)."""
    W, H = 840, 480
    f = [text(W / 2, 28, "Вертикальні профілі провідності σ(z) та електричного поля E(z)", size=15, bold=True)]

    ox, oy = 120, 410
    h_graph = 330
    w_graph = 640
    top = oy - h_graph
    right = ox + w_graph

    # Осі
    f.append(line(ox, oy, right, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))
    f.append(text(ox - 15, top - 5, "Висота z (км)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки висоти z: 0, 10, 20, 30, 40, 50, 60 км
    for z_km in range(0, 61, 10):
        py = oy - (z_km / 60.0) * h_graph
        f.append(line(ox - 5, py, ox, py, color=MUTED, sw=1.2))
        f.append(text(ox - 12, py + 4, str(z_km), size=10, color=MUTED, anchor="end"))

    # Нижня вісь
    f.append(text(ox + 160, oy + 28, "Провідність σ(z) (См/м) → [зелена крива]", size=10.5, color="#059669", bold=True))
    f.append(text(right - 160, oy + 28, "Електричне поле E_z(z) (В/м) → [синя крива]", size=10.5, color="#2563EB", bold=True))

    pts_sigma = []
    pts_field = []
    for z_km in range(0, 61):
        py = oy - (z_km / 60.0) * h_graph
        log_sigma = -14.0 + (z_km / 60.0) * 7.0
        px_sigma = ox + ((log_sigma - (-14.0)) / 7.0) * (w_graph * 0.45)
        pts_sigma.append((px_sigma, py))

        log_E = math.log10(130.0) - (z_km / 60.0) * 3.5
        px_field = ox + w_graph - ((math.log10(130.0) - log_E) / 3.5) * (w_graph * 0.45)
        pts_field.append((px_field, py))

    path_s = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_sigma)
    path_e = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_field)

    f.append(f'<path d="{path_s}" fill="none" stroke="#10B981" stroke-width="2.8"/>')
    f.append(f'<path d="{path_e}" fill="none" stroke="#2563EB" stroke-width="2.8"/>')

    # Умова стаціонарності
    f.append(line(ox, oy - 0.5 * h_graph, right, oy - 0.5 * h_graph, color="#94A3B8", sw=1.0, dash="3 3"))
    f.append(text(ox + 320, oy - 0.5 * h_graph - 8, "Умова стаціонарності: J_z = σ(z) · E_z(z) = const ≈ 2.5 пА/м²", size=9.5, color="#475569", bold=True))

    # Виносні блоки джерел іонізації
    b_radon = fitbox(ox + 220, oy - 40, 200, 50, "Радон-222 та γ-радіація ґрунту\n(іонізація тропосфери 0–2 км)", size=9, fill="#F0FDF4", stroke="#86EFAC", color="#166534")
    f.append(b_radon)

    b_cosmic = fitbox(ox + 250, oy - 150, 230, 55, "Галактичні космічні промені (GCR)\nМаксимум Пфотцера (15–20 км):\nголовне джерело іонізації", size=9, fill="#EFF6FF", stroke="#93C5FD", color="#1E40AF")
    f.append(b_cosmic)

    b_ionosphere = fitbox(ox + 280, oy - 300, 220, 50, "Іоносферний шар D (>60 км):\nУФ сонячне випромінювання,\nплазмовий провідний шар", size=9, fill="#FAF5FF", stroke="#E9D5FF", color="#6B21A8")
    f.append(b_ionosphere)

    render(os.path.join(IMG_DIR, "atmospheric-profile.svg"), W, H, *f)


def fig_carnegie_curve():
    """Фігура 3: Добова крива Карнегі (Carnegie curve)."""
    W, H = 840, 470
    f = [text(W / 2, 28, "Добова крива Карнегі: глобальні коливання електричного поля (UTC)", size=15, bold=True)]

    ox, oy = 90, 390
    w_graph = 700
    h_graph = 280
    top = oy - h_graph

    # Сітка та осі
    f.append(line(ox, oy, ox + w_graph, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))
    f.append(text(ox + w_graph, oy + 32, "Час UTC (години) →", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, top - 5, "Відносне поле E_z (%)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки Y
    for pct in range(70, 131, 10):
        py = oy - ((pct - 70) / 60.0) * h_graph
        f.append(line(ox - 5, py, ox + w_graph, py, color="#E2E8F0" if pct != 100 else "#94A3B8", sw=1.0 if pct != 100 else 1.5, dash=None if pct == 100 else "2 2"))
        f.append(text(ox - 10, py + 4, f"{pct}%", size=10, color=MUTED, anchor="end"))

    # Позначки X
    for hr in range(0, 25, 4):
        px = ox + (hr / 24.0) * w_graph
        f.append(line(px, oy, px, oy + 5, color=MUTED, sw=1.2))
        f.append(text(px, oy + 20, f"{hr:02d}:00", size=10, color=MUTED, anchor="middle"))

    carnegie_data = [
        (0, 92), (1, 85), (2, 80), (3, 78), (4, 80), (5, 83), (6, 86),
        (7, 90), (8, 93), (9, 95), (10, 96), (11, 98), (12, 102),
        (13, 106), (14, 110), (15, 114), (16, 118), (17, 120), (18, 122),
        (19, 123), (20, 121), (21, 116), (22, 108), (23, 98), (24, 92)
    ]

    pts = []
    for hr, val in carnegie_data:
        px = ox + (hr / 24.0) * w_graph
        py = oy - ((val - 70) / 60.0) * h_graph
        pts.append((px, py))

    path_c = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    f.append(f'<path d="{path_c}" fill="none" stroke="#DC2626" stroke-width="3"/>')

    # Мінімум і максимум
    px_min, py_min = pts[3]
    px_max, py_max = pts[19]

    f.append(circle(px_min, py_min, 5, fill="#DC2626", stroke="#FFFFFF", sw=1.5))
    f.append(circle(px_max, py_max, 5, fill="#DC2626", stroke="#FFFFFF", sw=1.5))

    b_min = fitbox(px_min + 90, py_min + 45, 175, 50, "Мінімум ~03:00 UTC (78%)\nСлабкі грози над\nТихим океаном", size=9, fill="#FEF2F2", stroke="#FCA5A5", color="#991B1B")
    f.append(b_min)

    b_max = fitbox(px_max - 90, py_max - 45, 185, 50, "Максимум ~19:00 UTC (123%)\nПік гроз у Пд. Америці\nта Африці одночасно", size=9, fill="#FEF2F2", stroke="#FCA5A5", color="#991B1B")
    f.append(b_max)

    # Регіональні грозові осередки
    b_asia = fitbox(ox + (8 / 24.0) * w_graph, oy - 95, 140, 45, "Грози в Азії та\nАвстралії (~08 UTC)", size=9, fill="#F0FDF4", stroke="#86EFAC", color="#166534")
    f.append(b_asia)

    b_africa = fitbox(ox + (14 / 24.0) * w_graph, oy - 155, 140, 45, "Пік гроз в\nАфриці (~14 UTC)", size=9, fill="#EFF6FF", stroke="#93C5FD", color="#1E40AF")
    f.append(b_africa)

    render(os.path.join(IMG_DIR, "carnegie-curve.svg"), W, H, *f)


def fig_schumann_resonances():
    """Фігура 4: Електромагнітні резонанси Шумана (Schumann resonances)."""
    W, H = 840, 480
    f = [text(W / 2, 28, "Спектр геоелектромагнітних резонансів Шумана в резонаторі Земля-Іоносфера", size=15, bold=True)]

    ox, oy = 90, 400
    w_graph = 430
    h_graph = 310
    top = oy - h_graph

    # Ліва частина: Спектр частот
    f.append(line(ox, oy, ox + w_graph, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))
    f.append(text(ox + w_graph, oy + 30, "Частота f (Гц) →", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 15, top - 5, "Спектральна густина потужності", size=10.5, color=INK, bold=True, anchor="end"))

    # Позначки частоти f (0 до 40 Гц)
    for freq in range(0, 41, 10):
        px = ox + (freq / 40.0) * w_graph
        f.append(line(px, oy, px, oy + 5, color=MUTED, sw=1.2))
        f.append(text(px, oy + 20, str(freq), size=10, color=MUTED, anchor="middle"))

    peaks = [
        (7.83, 270, "n=1 (7.83 Гц)"),
        (14.3, 190, "n=2 (14.3 Гц)"),
        (20.8, 130, "n=3 (20.8 Гц)"),
        (27.3, 85, "n=4 (27.3 Гц)"),
        (33.8, 55, "n=5 (33.8 Гц)")
    ]

    pts_spec = []
    for f_val in [f_i * 0.2 for f_i in range(0, 201)]:
        amp = 15.0
        for f_p, h_p, _ in peaks:
            amp += h_p / (1.0 + ((f_val - f_p) / 0.9) ** 2)
        px = ox + (f_val / 40.0) * w_graph
        py = oy - (amp / 300.0) * h_graph
        pts_spec.append((px, py))

    path_sp = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_spec)
    f.append(f'<path d="{path_sp}" fill="none" stroke="#7C3AED" stroke-width="2.5"/>')

    # Підписи під піками
    for f_p, h_p, label in peaks:
        px = ox + (f_p / 40.0) * w_graph
        py = oy - (h_p / 300.0) * h_graph
        f.append(circle(px, py, 4, fill="#7C3AED", stroke="#FFFFFF", sw=1.2))
        f.append(text(px, py - 10, label, size=9, bold=True, color="#5B21B6", anchor="middle"))

    # Права частина: Схема сферичного резонатора
    cx_cav, cy_cav = 675, 200
    r_earth = 60
    r_ion = 90

    f.append(rect(545, 60, 260, 390, fill="#F8FAFC", stroke="#CBD5E1", sw=1.5, rx=8))
    f.append(text(675, 85, "Резонатор Земля-Іоносфера", size=11, bold=True, color="#1E293B", anchor="middle"))

    # Земне ядро / поверхня
    f.append(circle(cx_cav, cy_cav, r_earth, fill="#D1FAE5", stroke="#059669", sw=2))
    f.append(text(cx_cav, cy_cav + 4, "Земля (r = R_E)", size=9.5, bold=True, color="#065F46", anchor="middle"))

    # Сферична обкладинка іоносфери
    f.append(f'<circle cx="{cx_cav}" cy="{cy_cav}" r="{r_ion}" fill="none" stroke="#3B82F6" stroke-width="2.5" stroke-dasharray="4 3"/>')
    f.append(text(cx_cav, cy_cav - r_ion - 10, "Іоносфера (h ≈ 60–90 км)", size=9.5, bold=True, color="#1E40AF", anchor="middle"))

    # Стояча ЕМ-хвиля у порожнині
    f.append(f'<circle cx="{cx_cav}" cy="{cy_cav}" r="75" fill="none" stroke="#7C3AED" stroke-width="1.8" stroke-dasharray="2 2"/>')

    t_cav = ("Стоячі ЕМ-хвилі (ELF)\n"
             "Частота λ_n ≈ 2πR_E / √(n(n+1))\n"
             "Збудження: ~100 розрядів гроз/с")
    f.append(mtext(675, 320, t_cav, size=9.5, color="#4C1D95", anchor="middle"))

    render(os.path.join(IMG_DIR, "schumann-resonances.svg"), W, H, *f)


if __name__ == "__main__":
    fig_global_circuit()
    fig_atmospheric_profile()
    fig_carnegie_curve()
    fig_schumann_resonances()
    print("Figures generated successfully in img/")
