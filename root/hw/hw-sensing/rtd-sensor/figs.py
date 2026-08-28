# -*- coding: utf-8 -*-
"""Фігури до теми «RTD: платина замість оксиду».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARM = "#c0392b"
COOL = "#2457d6"
GOLD = "#d97706"
GRAY = "#4b5563"
GREEN = "#15803d"


# ── 1. Фізика провідності: метал (платина) проти напівпровідника (оксид) ─────────
def fig_conduction():
    W, H = 840, 420
    f = [text(W / 2, 28, "Механізм провідності: платина (фононне розсіювання) проти напівпровідника (вибивання носіїв)", size=15, bold=True)]

    # Ліва панель: Метал (Платина)
    lx0, ly0, pw, ph = 24, 52, 384, 348
    f.append(rect(lx0, ly0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(lx0 + pw / 2, ly0 + 26, "Платина (Pt) — метал", size=14, bold=True, color=COOL))
    f.append(text(lx0 + pw / 2, ly0 + 46, "Концентрація електронів стала (n = const)", size=11.5, color=GRAY))

    # Ілюстрація кристалічної ґратки металу
    gx0, gy0 = lx0 + 32, ly0 + 66
    f.append(rect(gx0, gy0, 320, 160, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))

    # Вузли ґратки і коливання (фонони)
    for row in range(3):
        for col in range(5):
            cx = gx0 + 36 + col * 62
            cy = gy0 + 30 + row * 50
            f.append(circle(cx, cy, 10, fill="#e2e8f0", stroke="#64748b", sw=1.4))
            f.append(text(cx, cy + 4, "Pt⁺", size=9, bold=True, color="#334155"))
            f.append(line(cx - 15, cy, cx - 12, cy - 3, color=WARM, sw=1.2))
            f.append(line(cx + 12, cy + 3, cx + 15, cy, color=WARM, sw=1.2))

    # Електрон, що розсіюється
    f.append(line(gx0 + 20, gy0 + 80, gx0 + 90, gy0 + 80, color=COOL, sw=2))
    f.append(line(gx0 + 90, gy0 + 80, gx0 + 155, gy0 + 40, color=COOL, sw=2))
    f.append(line(gx0 + 155, gy0 + 40, gx0 + 225, gy0 + 120, color=COOL, sw=2))
    f.append(arrow(gx0 + 225, gy0 + 120, gx0 + 295, gy0 + 75, color=COOL, sw=2))
    f.append(circle(gx0 + 98, gy0 + 80, 4, fill=COOL, stroke=COOL))
    f.append(text(gx0 + 160, gy0 + 22, "Розсіювання на фононах", size=10.5, bold=True, color=WARM))

    b1, _, _ = textbox(lx0 + pw / 2, ly0 + 280,
                       "Нагрів підсилює амплітуду коливань ґратки.\n"
                       "Електрони частіше зіштовхуються (довжина пробігу λ падає).\n"
                       "ОПІР ЗРОСТАЄ ЛІНІЙНО (α = +0.003851 °C⁻¹)",
                       size=11, fill="#eff6ff", stroke="#93c5fd", pad=8)
    f.append(b1)

    # Права панель: Напівпровідник (NTC)
    rx0 = 432
    f.append(rect(rx0, ly0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(rx0 + pw / 2, ly0 + 26, "Оксидна кераміка (NTC) — напівпровідник", size=14, bold=True, color=WARM))
    f.append(text(rx0 + pw / 2, ly0 + 46, "Концентрація носіїв експоненційно залежить від T", size=11.5, color=GRAY))

    # Зонна діаграма
    zx0, zy0 = rx0 + 32, ly0 + 66
    f.append(rect(zx0, zy0, 320, 160, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))

    # Зона провідності
    f.append(rect(zx0 + 20, zy0 + 16, 280, 36, fill="#fee2e2", stroke=WARM, sw=1.2, rx=4))
    f.append(text(zx0 + 160, zy0 + 38, "Зона провідності (вільні електрони e⁻)", size=11, bold=True, color=WARM))

    # Заборонена зона
    f.append(line(zx0 + 60, zy0 + 60, zx0 + 60, zy0 + 104, color=GRAY, sw=1.2))
    f.append(arrow(zx0 + 60, zy0 + 104, zx0 + 60, zy0 + 60, color=WARM, sw=1.5))
    f.append(text(zx0 + 160, zy0 + 84, "Заборонена зона Eg (термоактивація тепла)", size=10.5, color=GRAY))

    # Валентна зона
    f.append(rect(zx0 + 20, zy0 + 108, 280, 36, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    f.append(text(zx0 + 160, zy0 + 130, "Валентна зона (зв'язані електрони)", size=11, bold=True, color="#334155"))

    b2, _, _ = textbox(rx0 + pw / 2, ly0 + 280,
                       "Нагрів перекидає електрони через бар'єр Eg.\n"
                       "Кількість носіїв n(T) зростає експоненційно.\n"
                       "ОПІР КРУТО ПАДАЄ (нелінійність > 3000%, дрейф)",
                       size=11, fill="#fef2f2", stroke="#fca5a5", pad=8)
    f.append(b2)

    render(os.path.join(IMG, "conduction-metal-vs-semiconductor.svg"), W, H, *f)


# ── 2. Характеристична крива RTD (Pt100) та порівняння ──────────────────────────
def fig_rtd_curve():
    W, H = 840, 440
    f = [text(W / 2, 26, "Характеристика Pt100: висока лінійність платини та відхилення Каллендара–Ван Дюзена", size=15, bold=True)]

    # Ліва частина — графік R(T)
    ox, oy = 80, 370
    gw, gh = 430, 290

    # Сітка графіка
    for t_val in [-200, 0, 200, 400, 600, 800]:
        x = ox + (t_val + 200) / 1050 * gw
        f.append(line(x, oy - gh, x, oy, color="#f1f5f9", sw=1))
        f.append(text(x, oy + 18, f"{t_val}", size=10.5, color=GRAY))

    for r_val in [0, 100, 200, 300, 400]:
        y = oy - (r_val / 420) * gh
        f.append(line(ox, y, ox + gw, y, color="#f1f5f9", sw=1))
        f.append(text(ox - 10, y + 4, f"{r_val}", size=10.5, color=GRAY, anchor="end"))

    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.6))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.6))
    f.append(text(ox + gw / 2, oy + 38, "Температура T (°C)", size=11.5, bold=True))
    f.append(text(ox - 42, oy - gh / 2, "Опір R (Ω)", size=11.5, bold=True))

    # Точки кривої Pt100
    pts = []
    for t in range(-200, 851, 25):
        if t >= 0:
            r = 100.0 * (1.0 + 3.9083e-3 * t - 5.775e-7 * (t ** 2))
        else:
            r = 100.0 * (1.0 + 3.9083e-3 * t - 5.775e-7 * (t ** 2) - 4.183e-12 * (t - 100) * (t ** 3))
        x = ox + (t + 200) / 1050 * gw
        y = oy - (r / 420) * gh
        pts.append((x, y))

    path_d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(f"L {p[0]:.1f} {p[1]:.1f}" for p in pts[1:])
    f.append(f'<path d="{path_d}" fill="none" stroke="{COOL}" stroke-width="2.6"/>')

    # Опорні точки з чіткими кружками
    key_points = [
        (-200, 18.52),
        (0, 100.00),
        (100, 138.51),
        (600, 313.71),
        (850, 390.48),
    ]
    for t_k, r_k in key_points:
        kx = ox + (t_k + 200) / 1050 * gw
        ky = oy - (r_k / 420) * gh
        f.append(circle(kx, ky, 4.5, fill=WARM, stroke="#ffffff", sw=1.5))

    # Підписи ключових точок
    f.append(text(ox + 10, oy - (18.52 / 420) * gh - 12, "−200 °C (18.5 Ω)", size=9.5, color=COOL, bold=True))
    f.append(text(ox + (200 / 1050) * gw - 15, oy - (100 / 420) * gh - 12, "0 °C (100.0 Ω)", size=9.5, color=COOL, bold=True))
    f.append(text(ox + (300 / 1050) * gw + 35, oy - (138.51 / 420) * gh + 14, "+100 °C (138.5 Ω)", size=9.5, color=COOL, bold=True))
    f.append(text(ox + (1050 / 1050) * gw - 30, oy - (390.48 / 420) * gh - 12, "+850 °C (390.5 Ω)", size=9.5, color=COOL, bold=True))

    # Права панель — інженерне резюме
    rx0, ry0, rw, rh = 540, 56, 276, 350
    f.append(rect(rx0, ry0, rw, rh, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(rx0 + rw / 2, ry0 + 26, "Властивості Pt100 (IEC 60751)", size=13, bold=True, color=COOL))

    info_lines = [
        "Базовий опір: R₀ = 100.00 Ω (за 0 °C)",
        "Коефіцієнт: α = 0.003851 °C⁻¹",
        "Чутливість: ~0.385 Ω/°C (Pt1000: 3.85)",
        "Діапазон: від −200 °C до +850 °C",
        "Довготривалий дрейф: < 0.05 °C/рік",
        "",
        "Рівняння Каллендара–Ван Дюзена:",
        "• Для T ≥ 0 °C: R(T) = R₀·(1 + A·T + B·T²)",
        "• A = 3.9083×10⁻³ °C⁻¹",
        "• B = −5.7750×10⁻⁷ °C⁻²",
        "• C = −4.1830×10⁻¹² °C⁻⁴ (для T < 0 °C)",
        "",
        "Точність: до ±0.03 °C (Class AA)",
    ]
    for i, line_text in enumerate(info_lines):
        bold_flag = line_text.startswith("•") or line_text.startswith("Рівняння") or line_text.startswith("Базовий")
        col = COOL if line_text.startswith("Рівняння") else (WARM if line_text.startswith("Точність") else INK)
        f.append(text(rx0 + 16, ry0 + 56 + i * 21, line_text, size=10, bold=bold_flag, color=col, anchor="start"))

    render(os.path.join(IMG, "rtd-characteristic-curve.svg"), W, H, *f)


# ── 3. Схеми підключення: 2-провідна, 3-провідна, 4-провідна ────────────────────
def fig_wiring_schemes():
    W, H = 840, 520
    f = [text(W / 2, 26, "Топології підключення RTD та механізми компенсації опору ліній", size=15, bold=True)]

    # 1) Двопровідна схема (2-Wire)
    y1 = 50
    f.append(rect(20, y1, 460, 136, fill="#fef2f2", stroke="#fca5a5", sw=1.3, rx=6))
    f.append(text(34, y1 + 20, "2-Wire: пряме підключення (похибка від кабелю)", size=11.5, bold=True, color=WARM, anchor="start"))

    # Вимірювач
    f.append(rect(36, y1 + 34, 100, 86, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(86, y1 + 58, "Вимірювач", size=10.5, bold=True))
    f.append(text(86, y1 + 76, "I_EXC", size=9.5, color=GRAY))
    f.append(text(86, y1 + 96, "V_meas (АЦП)", size=9.5, color=COOL))

    # Дроти та резистори ліній
    f.append(line(136, y1 + 54, 230, y1 + 54, color=WARM, sw=1.8))
    f.append(rect(230, y1 + 46, 44, 16, fill="#fee2e2", stroke=WARM, sw=1.1, rx=2))
    f.append(text(252, y1 + 58, "RL1", size=9, bold=True, color=WARM))
    f.append(line(274, y1 + 54, 360, y1 + 54, color=WARM, sw=1.8))

    f.append(line(136, y1 + 100, 230, y1 + 100, color=WARM, sw=1.8))
    f.append(rect(230, y1 + 92, 44, 16, fill="#fee2e2", stroke=WARM, sw=1.1, rx=2))
    f.append(text(252, y1 + 104, "RL2", size=9, bold=True, color=WARM))
    f.append(line(274, y1 + 100, 360, y1 + 100, color=WARM, sw=1.8))

    # Сенсор
    f.append(rect(360, y1 + 42, 80, 70, fill="#eff6ff", stroke=COOL, sw=1.3, rx=4))
    f.append(text(400, y1 + 70, "Pt100", size=11, bold=True, color=COOL))
    f.append(text(400, y1 + 88, "R_RTD", size=9.5, color=COOL))

    # Текстова панель 2-wire праворуч
    f.append(rect(500, y1, 320, 136, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(516, y1 + 24, "Рівняння вимірювання 2-Wire:", size=11, bold=True, color=WARM, anchor="start"))
    f.append(text(516, y1 + 46, "V_meas = I_EXC · (R_RTD + RL1 + RL2)", size=10, bold=True, anchor="start"))
    f.append(text(516, y1 + 68, "• Кабель 10 м (0.5 мм²) додає 1.4 Ω", size=9.5, color=GRAY, anchor="start"))
    f.append(text(516, y1 + 88, "• Для Pt100 це фатальна похибка ΔT ≈ +3.6 °C!", size=9.5, bold=True, color=WARM, anchor="start"))
    f.append(text(516, y1 + 108, "• Температурний дрейф міді спотворює шкалу", size=9.5, color=GRAY, anchor="start"))

    # 2) Трипровідна схема (3-Wire)
    y2 = 205
    f.append(rect(20, y2, 460, 142, fill="#fffbeb", stroke="#fcd34d", sw=1.3, rx=6))
    f.append(text(34, y2 + 20, "3-Wire: подвійне джерело струму IDAC", size=11.5, bold=True, color=GOLD, anchor="start"))

    f.append(rect(36, y2 + 34, 100, 96, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(86, y2 + 54, "Подвійний IDAC", size=10, bold=True))
    f.append(text(86, y2 + 72, "I1 = I2 = I_EXC", size=9, color=GOLD))
    f.append(text(86, y2 + 94, "Диф. АЦП", size=9.5, color=COOL))
    f.append(text(86, y2 + 112, "V_A − V_B", size=9, color=COOL))

    # Дріт 1: I1
    f.append(line(136, y2 + 48, 230, y2 + 48, color=GOLD, sw=1.6))
    f.append(rect(230, y2 + 40, 44, 16, fill="#fef3c7", stroke=GOLD, sw=1.1, rx=2))
    f.append(text(252, y2 + 52, "RL1", size=9, bold=True, color=GOLD))
    f.append(line(274, y2 + 48, 360, y2 + 48, color=GOLD, sw=1.6))

    # Дріт 2: I2
    f.append(line(136, y2 + 82, 230, y2 + 82, color=GOLD, sw=1.6))
    f.append(rect(230, y2 + 74, 44, 16, fill="#fef3c7", stroke=GOLD, sw=1.1, rx=2))
    f.append(text(252, y2 + 86, "RL2", size=9, bold=True, color=GOLD))
    f.append(line(274, y2 + 82, 360, y2 + 82, color=GOLD, sw=1.6))

    # Дріт 3: I1 + I2
    f.append(line(136, y2 + 116, 230, y2 + 116, color=GRAY, sw=1.6))
    f.append(rect(230, y2 + 108, 44, 16, fill="#f1f5f9", stroke=GRAY, sw=1.1, rx=2))
    f.append(text(252, y2 + 120, "RL3", size=9, bold=True, color=GRAY))
    f.append(line(274, y2 + 116, 360, y2 + 116, color=GRAY, sw=1.6))

    # Сенсор
    f.append(rect(360, y2 + 42, 80, 50, fill="#eff6ff", stroke=COOL, sw=1.3, rx=4))
    f.append(text(400, y2 + 66, "Pt100", size=11, bold=True, color=COOL))
    f.append(line(360, y2 + 82, 400, y2 + 82, color=COOL, sw=1.4))
    f.append(line(400, y2 + 82, 400, y2 + 116, color=COOL, sw=1.4))
    f.append(line(360, y2 + 116, 400, y2 + 116, color=COOL, sw=1.4))

    # Текстова панель 3-wire праворуч
    f.append(rect(500, y2, 320, 142, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(516, y2 + 24, "Рівняння компенсації 3-Wire:", size=11, bold=True, color=GOLD, anchor="start"))
    f.append(text(516, y2 + 46, "V_A = I1·(RL1 + R_RTD) + (I1+I2)·RL3", size=9.5, anchor="start"))
    f.append(text(516, y2 + 66, "V_B = I2·RL2 + (I1+I2)·RL3", size=9.5, anchor="start"))
    f.append(text(516, y2 + 88, "ΔV = I_EXC · R_RTD + I_EXC · (RL1 − RL2)", size=10, bold=True, color=GREEN, anchor="start"))
    f.append(text(516, y2 + 110, "• Якщо RL1 = RL2, опір лінії повністю зникає!", size=9.5, bold=True, color=GREEN, anchor="start"))

    # 3) Чотирипровідна схема Кельвіна (4-Wire)
    y3 = 365
    f.append(rect(20, y3, 460, 142, fill="#f0fdf4", stroke="#86efac", sw=1.3, rx=6))
    f.append(text(34, y3 + 20, "4-Wire Kelvin: повне апаратне усунення опору дротів", size=11.5, bold=True, color=GREEN, anchor="start"))

    f.append(rect(36, y3 + 34, 100, 96, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(86, y3 + 52, "Force (струм)", size=9.5, bold=True, color=WARM))
    f.append(text(86, y3 + 68, "I_EXC", size=9, color=WARM))
    f.append(text(86, y3 + 90, "Sense (напруга)", size=9.5, bold=True, color=GREEN))
    f.append(text(86, y3 + 108, "R_in > 10 GΩ", size=9, color=COOL))

    # Струмові лінії Force
    f.append(line(136, y3 + 46, 230, y3 + 46, color=WARM, sw=1.6))
    f.append(rect(230, y3 + 38, 44, 16, fill="#fee2e2", stroke=WARM, sw=1.1, rx=2))
    f.append(text(252, y3 + 50, "RL1", size=9, bold=True, color=WARM))
    f.append(line(274, y3 + 46, 360, y3 + 46, color=WARM, sw=1.6))

    f.append(line(136, y3 + 118, 230, y3 + 118, color=WARM, sw=1.6))
    f.append(rect(230, y3 + 110, 44, 16, fill="#fee2e2", stroke=WARM, sw=1.1, rx=2))
    f.append(text(252, y3 + 122, "RL4", size=9, bold=True, color=WARM))
    f.append(line(274, y3 + 118, 360, y3 + 118, color=WARM, sw=1.6))

    # Сигнальні лінії Sense (без струму)
    f.append(line(136, y3 + 70, 230, y3 + 70, color=GREEN, sw=1.4, dash="3,2"))
    f.append(rect(230, y3 + 62, 44, 16, fill="#dcfce7", stroke=GREEN, sw=1.1, rx=2))
    f.append(text(252, y3 + 74, "RL2", size=9, bold=True, color=GREEN))
    f.append(line(274, y3 + 70, 360, y3 + 58, color=GREEN, sw=1.4, dash="3,2"))

    f.append(line(136, y3 + 94, 230, y3 + 94, color=GREEN, sw=1.4, dash="3,2"))
    f.append(rect(230, y3 + 86, 44, 16, fill="#dcfce7", stroke=GREEN, sw=1.1, rx=2))
    f.append(text(252, y3 + 98, "RL3", size=9, bold=True, color=GREEN))
    f.append(line(274, y3 + 94, 360, y3 + 106, color=GREEN, sw=1.4, dash="3,2"))

    # Сенсор
    f.append(rect(360, y3 + 44, 80, 74, fill="#eff6ff", stroke=COOL, sw=1.3, rx=4))
    f.append(text(400, y3 + 74, "Pt100", size=11, bold=True, color=COOL))
    f.append(text(400, y3 + 92, "R_RTD", size=9.5, color=COOL))

    # Текстова панель 4-wire праворуч
    f.append(rect(500, y3, 320, 142, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(516, y3 + 24, "Рівняння вимірювання 4-Wire (Kelvin):", size=11, bold=True, color=GREEN, anchor="start"))
    f.append(text(516, y3 + 46, "I_sense ≈ 0  →  ΔV(RL2) = 0, ΔV(RL3) = 0", size=9.5, anchor="start"))
    f.append(text(516, y3 + 68, "V_sense = V_RTD = I_EXC · R_RTD", size=10.5, bold=True, color=GREEN, anchor="start"))
    f.append(text(516, y3 + 90, "• Опір кабелю будь-якої довжини = 0 похибки", size=9.5, bold=True, color=GREEN, anchor="start"))
    f.append(text(516, y3 + 112, "• Стандарт прецизійної метрології та еталонів", size=9.5, color=GRAY, anchor="start"))

    render(os.path.join(IMG, "wiring-topologies-234wire.svg"), W, H, *f)


# ── 4. Раціометричний прецизійний AFE (АЦП + опорний резистор) ──────────────────
def fig_ratiometric_afe():
    W, H = 840, 430
    f = [text(W / 2, 28, "Раціометрична схема зчитування RTD: повне виключення нестабільності струму збудження", size=15, bold=True)]

    ox, oy = 40, 60

    # Джерело струму
    f.append(rect(ox + 30, oy + 20, 120, 50, fill="#eff6ff", stroke=COOL, sw=1.4, rx=6))
    f.append(text(ox + 90, oy + 42, "Джерело струму", size=11, bold=True, color=COOL))
    f.append(text(ox + 90, oy + 58, "I_EXC (100 µA..1 mA)", size=9.5, color=GRAY))

    # Лінія струму
    f.append(line(ox + 150, oy + 45, ox + 210, oy + 45, color=COOL, sw=2.2))
    f.append(arrow(ox + 150, oy + 45, ox + 190, oy + 45, color=COOL, sw=2.2))

    # Опорний резистор R_REF
    f.append(rect(ox + 210, oy + 25, 100, 40, fill="#fef3c7", stroke=GOLD, sw=1.4, rx=4))
    f.append(text(ox + 260, oy + 44, "R_REF", size=11.5, bold=True, color=GOLD))
    f.append(text(ox + 260, oy + 58, "0.05%, 5 ppm/°C", size=9, color="#92400e"))

    # Лінія між R_REF та RTD
    f.append(line(ox + 310, oy + 45, ox + 370, oy + 45, color=COOL, sw=2.2))
    f.append(arrow(ox + 310, oy + 45, ox + 350, oy + 45, color=COOL, sw=2.2))

    # Сенсор RTD (Pt100/Pt1000)
    f.append(rect(ox + 370, oy + 25, 100, 40, fill="#fee2e2", stroke=WARM, sw=1.4, rx=4))
    f.append(text(ox + 420, oy + 44, "Pt100 / Pt1000", size=11, bold=True, color=WARM))
    f.append(text(ox + 420, oy + 58, "R_RTD (сенсор)", size=9, color=WARM))

    # Лінія до GND
    f.append(line(ox + 470, oy + 45, ox + 520, oy + 45, color=LINE, sw=2.2))
    f.append(line(ox + 520, oy + 45, ox + 520, oy + 80, color=LINE, sw=2.2))
    f.append(line(ox + 505, oy + 80, ox + 535, oy + 80, color=LINE, sw=2.2))
    f.append(line(ox + 510, oy + 85, ox + 530, oy + 85, color=LINE, sw=1.8))
    f.append(line(ox + 515, oy + 90, ox + 525, oy + 90, color=LINE, sw=1.4))
    f.append(text(ox + 520, oy + 104, "GND", size=10, bold=True, color=GRAY))

    # Блок АЦП
    adc_x, adc_y, adc_w, adc_h = ox + 160, oy + 135, 360, 210
    f.append(rect(adc_x, adc_y, adc_w, adc_h, fill="#f8fafc", stroke=LINE, sw=1.6, rx=8))
    f.append(text(adc_x + adc_w / 2, adc_y + 24, "24-бітний прецизійний ΣΔ АЦП (ADS1248 / MAX31865)", size=12, bold=True, color=COOL))

    # Лінії REFP / REFN
    f.append(line(ox + 230, oy + 65, ox + 230, adc_y + 55, color=GOLD, sw=1.4, dash="3,3"))
    f.append(line(ox + 290, oy + 65, ox + 290, adc_y + 55, color=GOLD, sw=1.4, dash="3,3"))
    f.append(rect(adc_x + 20, adc_y + 45, 140, 36, fill="#fef3c7", stroke=GOLD, sw=1.2, rx=4))
    f.append(text(adc_x + 90, adc_y + 67, "REFP − REFN (V_REF)", size=9.5, bold=True, color=GOLD))

    # Лінії AINP / AINN
    f.append(line(ox + 390, oy + 65, ox + 390, adc_y + 55, color=WARM, sw=1.4, dash="3,3"))
    f.append(line(ox + 450, oy + 65, ox + 450, adc_y + 55, color=WARM, sw=1.4, dash="3,3"))
    f.append(rect(adc_x + 200, adc_y + 45, 140, 36, fill="#fee2e2", stroke=WARM, sw=1.2, rx=4))
    f.append(text(adc_x + 270, adc_y + 67, "AINP − AINN (V_RTD)", size=9.5, bold=True, color=WARM))

    # Ядро АЦП
    f.append(rect(adc_x + 20, adc_y + 105, 320, 80, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(adc_x + 160, adc_y + 128, "Ядро ділення напруг АЦП:", size=11, bold=True))
    f.append(text(adc_x + 160, adc_y + 150, "Код = (V_RTD / V_REF) · 2²³ = (R_RTD / R_REF) · 2²³", size=10.5, bold=True, color=GREEN))
    f.append(text(adc_x + 160, adc_y + 170, "Шум і температурний дрейф I_EXC повністю скорочуються!", size=9.5, color=GRAY))

    # Права бічна панель — математика раціометрії
    bx0, by0, bw, bh = ox + 550, oy + 10, 220, 340
    f.append(rect(bx0, by0, bw, bh, fill="#eff6ff", stroke="#93c5fd", sw=1.3, rx=6))
    f.append(text(bx0 + bw / 2, by0 + 24, "Математика раціометрії", size=11.5, bold=True, color=COOL))

    r_steps = [
        "1. Напруга на RTD:",
        "   V_RTD = I_EXC · R_RTD",
        "",
        "2. Опорна напруга:",
        "   V_REF = I_EXC · R_REF",
        "",
        "3. Відлік АЦП:",
        "   Code = V_RTD / V_REF",
        "   Code = R_RTD / R_REF",
        "",
        "Висновок:",
        "• Струм I_EXC скорочується",
        "• Дрейф джерела = 0 похибки",
        "• Точність залежить лише",
        "  від стабільності R_REF",
    ]
    for i, st in enumerate(r_steps):
        bold_flag = st.startswith("1.") or st.startswith("2.") or st.startswith("3.") or st.startswith("Висновок") or "Code = R_RTD" in st
        col = COOL if "Code =" in st else (GREEN if st.startswith("•") else INK)
        f.append(text(bx0 + 14, by0 + 50 + i * 19, st, size=9.5, bold=bold_flag, color=col, anchor="start"))

    render(os.path.join(IMG, "rtd-ratiometric-afe.svg"), W, H, *f)


if __name__ == "__main__":
    fig_conduction()
    fig_rtd_curve()
    fig_wiring_schemes()
    fig_ratiometric_afe()
    print("Всі фігури для RTD успішно згенеровано.")
