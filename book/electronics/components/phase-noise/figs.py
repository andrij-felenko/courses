# -*- coding: utf-8 -*-
"""Фігури до статті «Фазовий шум генераторів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e67e22"
PURPLE = "#8e44ad"

def polyline(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s stroke-linejoin="round"/>' % (p, color, sw, d)

# ── 1. Спектральне розширення: ідеальна дельта проти реальної спідниці ────────
def fig_spectral_broadening():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Спектр коливань: ідеальна дельта-функція проти реального генератора", size=16, bold=True),
        text(W / 2, 48, "через неминучі флуктуації фази дискретна лінія розмивається в неперервну «спідницю»", size=12, color=MUTED, italic=True)
    ]

    # ЛІВА ПАНЕЛЬ: Ідеальний генератор
    L1, R1, T1, B1 = 70, 430, 95, 390
    f.append(rect(L1 - 10, T1 - 25, (R1 - L1) + 20, (B1 - T1) + 60, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L1 + R1) / 2, T1 - 8, "Ідеальне гармонічне коливання", size=13, bold=True))
    f.append(line(L1, B1, R1, B1, color=INK, sw=1.5))
    f.append(line(L1, B1, L1, T1, color=INK, sw=1.5))
    f.append(text(R1 - 5, B1 + 20, "Частота f →", size=11, color=MUTED, anchor="end"))
    f.append(text(L1 - 8, T1 + 10, "S_v(f)", size=11, bold=True, anchor="end"))

    # Дельта-функція
    f0_x1 = L1 + (R1 - L1) * 0.5
    f.append(arrow(f0_x1, B1, f0_x1, T1 + 25, color=NEG, sw=3.0))
    f.append(circle(f0_x1, T1 + 25, 4.0, fill=NEG, stroke=NEG))
    f.append(text(f0_x1, B1 + 18, "f₀", size=13, bold=True))
    f.append(line(f0_x1, B1, f0_x1, B1 + 5, color=INK, sw=1.5))

    # Виноска для лівої панелі
    f.append(fitbox(L1 + 15, T1 + 40, 160, 50, "v(t) = A₀·cos(2πf₀t)\nφ(t) = 0 (стала фаза)", size=11, fill="#edf2fa", stroke=NEG))
    f.append(fitbox(f0_x1 + 25, T1 + 100, 150, 60, "Спектр: дельта Дірака\nШирина смуги = 0 Гц\nВся потужність у f₀", size=11, fill=BG, stroke=LINE))

    # ПРАВА ПАНЕЛЬ: Реальний генератор
    L2, R2, T2, B2 = 510, 870, 95, 390
    f.append(rect(L2 - 10, T2 - 25, (R2 - L2) + 20, (B2 - T2) + 60, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L2 + R2) / 2, T2 - 8, "Реальний автогенератор із шумом", size=13, bold=True))
    f.append(line(L2, B2, R2, B2, color=INK, sw=1.5))
    f.append(line(L2, B2, L2, T2, color=INK, sw=1.5))
    f.append(text(R2 - 5, B2 + 20, "Частота f →", size=11, color=MUTED, anchor="end"))
    f.append(text(L2 - 8, T2 + 10, "S_v(f)", size=11, bold=True, anchor="end"))

    # Крива з розмитою спідницею
    f0_x2 = L2 + (R2 - L2) * 0.5
    curve_pts = []
    for i in range(161):
        x = L2 + (R2 - L2) * (i / 160.0)
        dx = (x - f0_x2) / 18.0
        # Модель Лоренца з поличкою
        y_val = 1.0 / (1.0 + dx**2 * (1.0 + 0.1 * abs(dx)))
        y_px = B2 - (B2 - T1 - 35) * y_val - 8
        curve_pts.append((x, y_px))

    # Заливка під спідницею
    poly_d = "M %.1f,%.1f " % (L2, B2) + " ".join("L %.1f,%.1f" % pt for pt in curve_pts) + " L %.1f,%.1f Z" % (R2, B2)
    f.append('<path d="%s" fill="#fdecea" opacity="0.65"/>' % poly_d)
    f.append(polyline(curve_pts, POS, sw=2.5))
    f.append(text(f0_x2, B2 + 18, "f₀", size=13, bold=True))
    f.append(line(f0_x2, B2, f0_x2, B2 + 5, color=INK, sw=1.5))

    # Виносні стрілки фазового шуму
    f.append(line(f0_x2 + 40, B2 - 50, f0_x2 + 75, B2 - 100, color=POS, sw=1.5))
    f.append(fitbox(f0_x2 + 25, B2 - 165, 145, 54, "«Спідниця» шуму\nL(f_m) у дБн/Гц\nна відступі f_m від f₀", size=11, fill=BG, stroke=POS))

    f.append(fitbox(L2 + 15, T2 + 30, 150, 50, "v(t) = A(t)·cos(2πf₀t + φ(t))\nφ(t) — випадковий дрейф", size=11, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, "spectral-broadening.svg"), W, H, *f)

# ── 2. Спектр Лісона: 4 фізичні ділянки та характерні нахили ────────────────
def fig_leeson_slopes():
    W, H = 940, 520
    f = [
        text(W / 2, 28, "Спектральна густина фазового шуму L(f_m): модель Лісона", size=16, bold=True),
        text(W / 2, 48, "чотири фізичні зони у подвійному логарифмічному масштабі та їхні механізми", size=12, color=MUTED, italic=True)
    ]

    L, R, T, B = 90, 880, 85, 430

    # Сітка та осі
    f.append(rect(L, T, R - L, B - T, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))

    # Логарифмічні позначки на осі X (зсув частоти f_m)
    # Зони: 10 Гц (1/f^3), 1 кГц (кутова флікеру f_c), 100 кГц (f_0 / 2Q_L), 10 МГц (шумовий поріг)
    x_fc = L + (R - L) * 0.32
    x_fhalf = L + (R - L) * 0.65

    # Вертикальні лінії меж зон
    f.append(line(x_fc, T, x_fc, B, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(x_fhalf, T, x_fhalf, B, color=MUTED, sw=1.2, dash="4 4"))

    # Підписи характерних частот
    f.append(text(x_fc, B + 18, "f_c (флікер-злам)", size=12, bold=True, color=PURPLE))
    f.append(text(x_fhalf, B + 18, "f₀ / (2·Q_L) (смуга контуру)", size=12, bold=True, color=FIELD))

    # Точки кривої Лісона
    p1 = (L + 20, T + 30)
    p2 = (x_fc, T + 130)
    p3 = (x_fhalf, T + 270)
    p4 = (R - 100, T + 310)
    p5 = (R - 20, T + 310)

    curve = [p1, p2, p3, p4, p5]
    f.append(polyline(curve, POS, sw=3.2))

    # Маркери на точках зламу
    f.append(circle(p2[0], p2[1], 5.0, fill=PURPLE, stroke=INK, sw=1.5))
    f.append(circle(p3[0], p3[1], 5.0, fill=FIELD, stroke=INK, sw=1.5))

    # Текстові плашки над ділянками
    # Зона 1: 1/f^3
    f.append(fitbox(L + 15, T + 150, 160, 68, "Зона 1: 1/f³\nНахил −30 дБ/дек\nФлікер-шум транзистора,\nзмішаний на несучу", size=11, fill="#fdf2e9", stroke=ORANGE))

    # Зона 2: 1/f^2
    f.append(fitbox((x_fc + x_fhalf) / 2 - 80, T + 70, 165, 68, "Зона 2: 1/f²\nНахил −20 дБ/дек\nТепловий білий шум,\nінтегрований резонатором", size=11, fill="#eafaf1", stroke=FIELD))

    # Зона 3: 1/f (буфер)
    f.append(fitbox(x_fhalf + 25, T + 180, 140, 56, "Зона 3: 1/f\nНахил −10 дБ/дек\nФлікер вихідного\nпідсилювача-буфера", size=11, fill="#f4ecf7", stroke=PURPLE))

    # Зона 4: Білий поріг
    f.append(fitbox(R - 180, T + 230, 165, 58, "Зона 4: Шумовий поріг\nНахил 0 дБ/дек (константа)\nL_floor = F·k_B·T / P_s", size=11, fill="#ebf5fb", stroke=NEG))

    # Підписи осей
    f.append(text(L - 10, T + 15, "L(f_m) [дБн/Гц]", size=12, bold=True, anchor="end"))
    f.append(text(R - 10, B + 35, "Зсув від несучої f_m [Гц] (log) →", size=12, color=MUTED, anchor="end"))

    # Рівні дБн/Гц для масштабу
    f.append(text(L - 10, T + 35, "−50", size=11, color=MUTED, anchor="end"))
    f.append(text(L - 10, T + 135, "−90", size=11, color=MUTED, anchor="end"))
    f.append(text(L - 10, T + 275, "−140", size=11, color=MUTED, anchor="end"))
    f.append(text(L - 10, T + 315, "−165", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "leeson-spectrum-slopes.svg"), W, H, *f)

# ── 3. Взаємне змішування (Reciprocal Mixing) ────────────────────────────────
def fig_reciprocal_mixing():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Взаємне змішування (Reciprocal Mixing) у супергетеродинному приймачі", size=16, bold=True),
        text(W / 2, 48, "фазовий шум гетеродина переносить енергію потужної сусідньої завади просто у смугу ПЧ", size=12, color=MUTED, italic=True)
    ]

    # ЛІВА ПАНЕЛЬ: Вхідний RF спектр
    L1, R1, T1, B1 = 60, 430, 95, 380
    f.append(rect(L1 - 10, T1 - 25, (R1 - L1) + 20, (B1 - T1) + 55, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L1 + R1) / 2, T1 - 8, "Вхідний RF-спектр на антені", size=13, bold=True))
    f.append(line(L1, B1, R1, B1, color=INK, sw=1.5))
    f.append(line(L1, B1, L1, T1, color=INK, sw=1.5))
    f.append(text(R1 - 5, B1 + 18, "Частота f →", size=11, color=MUTED, anchor="end"))
    f.append(text(L1 - 8, T1 + 10, "P_in", size=11, bold=True, anchor="end"))

    # Слабкий корисний сигнал f_RF
    x_rf = L1 + 90
    f.append(arrow(x_rf, B1, x_rf, B1 - 65, color=FIELD, sw=2.5))
    f.append(text(x_rf, B1 + 16, "f_корисна", size=11, bold=True, color=FIELD))
    f.append(text(x_rf, B1 - 75, "−110 дБм\n(слабкий)", size=10, bold=True, color=FIELD))

    # Потужний блокер (завада на сусідньому каналі)
    x_block = L1 + 250
    f.append(arrow(x_block, B1, x_block, T1 + 30, color=POS, sw=3.5))
    f.append(text(x_block, B1 + 16, "f_завади", size=11, bold=True, color=POS))
    f.append(text(x_block, T1 + 18, "−20 дБм (блокер)", size=11, bold=True, color=POS))

    # Відстань між каналами
    f.append(line(x_rf, B1 - 120, x_block, B1 - 120, color=MUTED, sw=1.2))
    f.append(text((x_rf + x_block) / 2, B1 - 128, "Δf (відступ каналу)", size=10, color=MUTED))

    # ПРАВА ПАНЕЛЬ: Вихід після змішувача (Спектр ПЧ)
    L2, R2, T2, B2 = 500, 880, 95, 380
    f.append(rect(L2 - 10, T2 - 25, (R2 - L2) + 20, (B2 - T2) + 55, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L2 + R2) / 2, T2 - 8, "Спектр після змішувача на проміжній частоті (ПЧ)", size=13, bold=True))
    f.append(line(L2, B2, R2, B2, color=INK, sw=1.5))
    f.append(line(L2, B2, L2, T2, color=INK, sw=1.5))
    f.append(text(R2 - 5, B2 + 18, "Частота f →", size=11, color=MUTED, anchor="end"))
    f.append(text(L2 - 8, T2 + 10, "P_IF", size=11, bold=True, anchor="end"))

    # Смуга фільтра ПЧ (зелена рамка)
    x_if = L2 + 100
    f.append(rect(x_if - 35, T1 + 40, 70, B2 - T1 - 40, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(x_if, T1 + 30, "Смуга фільтра ПЧ", size=11, color=FIELD, bold=True))

    # Корисний сигнал перенесений на ПЧ
    f.append(arrow(x_if, B2, x_if, B2 - 65, color=FIELD, sw=2.5))
    f.append(text(x_if, B2 + 16, "f_ПЧ", size=11, bold=True, color=FIELD))

    # Перенесена завада зі спідницею фазового шуму гетеродина
    x_if_block = x_if + 160
    f.append(arrow(x_if_block, B2, x_if_block, T2 + 30, color=POS, sw=3.5))
    f.append(text(x_if_block, B2 + 16, "f_ПЧ + Δf", size=11, bold=True, color=POS))

    # Спідниця шуму гетеродина, що розповзається від завади у смугу ПЧ
    skirt_pts = []
    for i in range(121):
        x = x_if_block - 180 + i * 1.5
        dist = abs(x - x_if_block) / 25.0
        y_val = 1.0 / (1.0 + dist**1.8)
        y_px = B2 - (B2 - T2 - 40) * y_val * 0.95
        skirt_pts.append((x, y_px))
    f.append(polyline(skirt_pts, POS, sw=2.0, dash="3 3"))

    # Підсвітка шуму в смузі ПЧ
    f.append(rect(x_if - 30, B2 - 85, 60, 80, fill="#fadbd8", stroke=POS, sw=1.2))
    f.append(text(x_if, B2 - 95, "Шум гетеродина забив сигнал!", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "reciprocal-mixing.svg"), W, H, *f)

# ── 4. Апертурний джитер АЦП: похибка напруги та деградація SNR ──────────────
def fig_aperture_jitter():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Вплив джитеру такту на АЦП: апертурна похибка та обмеження SNR", size=16, bold=True),
        text(W / 2, 48, "чим вища частота вхідного сигналу, тим крутіший його схил і більша похибка напруги ΔV", size=12, color=MUTED, italic=True)
    ]

    # ЛІВА ПАНЕЛЬ: Крутий схил синусоїди та розкид моменту вибірки
    L1, R1, T1, B1 = 60, 430, 95, 390
    f.append(rect(L1 - 10, T1 - 25, (R1 - L1) + 20, (B1 - T1) + 55, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L1 + R1) / 2, T1 - 8, "Механізм виникнення напругової похибки", size=13, bold=True))
    f.append(line(L1, B1, R1, B1, color=INK, sw=1.5))
    f.append(line(L1, B1, L1, T1, color=INK, sw=1.5))
    f.append(text(R1 - 5, B1 + 18, "Час t →", size=11, color=MUTED, anchor="end"))
    f.append(text(L1 - 8, T1 + 10, "V(t)", size=11, bold=True, anchor="end"))

    # Схил сигналу (крута синусоїда)
    pts_sine = []
    for i in range(101):
        x = L1 + 30 + i * 3.0
        y = (B1 + T1) / 2 - 120 * math.sin((i - 50) / 30.0)
        pts_sine.append((x, y))
    f.append(polyline(pts_sine, INK, sw=2.5))

    # Ідеальний і зсунутий тактовий фронт
    t0_x = L1 + 180
    t1_x = t0_x + 35

    y_ideal = (B1 + T1) / 2 - 120 * math.sin((50 - 50) / 30.0)  # центр
    y_actual = (B1 + T1) / 2 - 120 * math.sin(((50 + 11.6) - 50) / 30.0)

    # Вертикальні лінії моментів такту
    f.append(line(t0_x, B1, t0_x, y_ideal, color=FIELD, sw=1.8, dash="3 3"))
    f.append(line(t1_x, B1, t1_x, y_actual, color=POS, sw=1.8, dash="3 3"))

    f.append(circle(t0_x, y_ideal, 4.0, fill=FIELD, stroke=FIELD))
    f.append(circle(t1_x, y_actual, 4.0, fill=POS, stroke=POS))

    # Горизонтальні лінії напруг
    f.append(line(L1, y_ideal, t0_x, y_ideal, color=FIELD, sw=1.2, dash="2 2"))
    f.append(line(L1, y_actual, t1_x, y_actual, color=POS, sw=1.2, dash="2 2"))

    # Позначки Δt (джитер) та ΔV (похибка напруги)
    f.append(line(t0_x, B1 - 15, t1_x, B1 - 15, color=POS, sw=2.0))
    f.append(text((t0_x + t1_x) / 2, B1 - 25, "Δt (джитер)", size=10, bold=True, color=POS))

    f.append(line(L1 + 15, y_ideal, L1 + 15, y_actual, color=POS, sw=2.0))
    f.append(text(L1 + 25, (y_ideal + y_actual) / 2 + 4, "ΔV = (dV/dt)·Δt", size=10, bold=True, color=POS, anchor="start"))

    # ПРАВА ПАНЕЛЬ: Крива стелі SNR від вхідної частоти
    L2, R2, T2, B2 = 500, 880, 95, 390
    f.append(rect(L2 - 10, T2 - 25, (R2 - L2) + 20, (B2 - T2) + 55, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    f.append(text((L2 + R2) / 2, T2 - 8, "Теоретична стеля SNR = −20·log₁₀(2π·f_in·σ_t)", size=13, bold=True))
    f.append(line(L2, B2, R2, B2, color=INK, sw=1.5))
    f.append(line(L2, B2, L2, T2, color=INK, sw=1.5))
    f.append(text(R2 - 5, B2 + 18, "Вхідна частота f_in (log) →", size=11, color=MUTED, anchor="end"))
    f.append(text(L2 - 8, T2 + 10, "SNR [дБ]", size=11, bold=True, anchor="end"))

    # Три криві для σ_t = 100 фс, 1 пс, 10 пс
    # 100 фс (зелена)
    c1 = [(L2 + 20, T2 + 30), (R2 - 20, T2 + 190)]
    f.append(polyline(c1, FIELD, sw=2.4))
    f.append(text(R2 - 30, T2 + 175, "σ_t = 100 фс", size=11, bold=True, color=FIELD, anchor="end"))

    # 1 пс (синя)
    c2 = [(L2 + 20, T2 + 90), (R2 - 20, T2 + 250)]
    f.append(polyline(c2, NEG, sw=2.4))
    f.append(text(R2 - 30, T2 + 235, "σ_t = 1 пс", size=11, bold=True, color=NEG, anchor="end"))

    # 10 пс (червона)
    c3 = [(L2 + 20, T2 + 150), (R2 - 20, T2 + 310)]
    f.append(polyline(c3, POS, sw=2.4))
    f.append(text(R2 - 30, T2 + 295, "σ_t = 10 пс", size=11, bold=True, color=POS, anchor="end"))

    # Позначка нахилу 20 дБ/декаду
    f.append(fitbox(L2 + 25, T2 + 210, 180, 52, "Спад −20 дБ на декаду:\nподвоєння f_in відбирає\n6 дБ SNR (1 біт ENOB!)", size=11, fill="#fef9e7", stroke=ORANGE))

    render(os.path.join(IMG, "aperture-jitter-adc.svg"), W, H, *f)

if __name__ == "__main__":
    fig_spectral_broadening()
    fig_leeson_slopes()
    fig_reciprocal_mixing()
    fig_aperture_jitter()
    print("OK: all figures generated")
