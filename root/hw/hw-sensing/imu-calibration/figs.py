# -*- coding: utf-8 -*-
"""Фігури до теми «Калібрування IMU».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREY = "#8a8a8a"
LIGHT_BLUE = "#eef4fd"
LIGHT_RED = "#fdf2f2"
LIGHT_GREEN = "#f0fdf4"


def _axes(f, ox, oy, top, right, ylab="Y", xlab="X"):
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(ox - 10, top + 8, ylab, size=12, anchor="end", bold=True))
    f.append(text(right - 6, oy + 18, xlab, size=12, bold=True))


# ── 1. Модель похибок IMU: неортогональність, масштаб і зсув нуля ─────────────
def fig_imu_error_model():
    W, H = 820, 420
    f = []

    # Ліва рамка: Геометрія осей (ідеальні ортогональні vs реальні скошені)
    f.append(rect(20, 20, 370, 380, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(205, 46, "Геометрія осей чутливості MEMS", size=13, bold=True))

    # Початок координат (зсунутий)
    ox, oy = 175, 230
    
    # Вектор зміщення нуля b (Bias) від ідеального центру
    icx, icy = 105, 290
    f.append(circle(icx, icy, 3.5, fill=INK, stroke=INK))
    f.append(text(icx, icy + 20, "Ідеальний центр (0,0,0)", size=10, color=MUTED, anchor="middle", bold=True))
    f.append(arrow(icx, icy, ox, oy, color=POS, sw=2))
    f.append(text((icx + ox)/2 + 10, (icy + oy)/2 - 5, "Зсув b", size=10.5, color=POS, anchor="start", bold=True))

    # Ідеальні осі (зелені, пунктирні)
    f.append(line(ox, oy, ox + 140, oy, color=FIELD, sw=1.8, dash="4,4"))
    f.append(text(ox + 145, oy + 4, "X_true", size=11, color=FIELD, anchor="start", bold=True))
    f.append(line(ox, oy, ox, oy - 130, color=FIELD, sw=1.8, dash="4,4"))
    f.append(text(ox, oy - 138, "Z_true", size=11, color=FIELD, anchor="middle", bold=True))
    f.append(line(ox, oy, ox - 70, oy + 60, color=FIELD, sw=1.8, dash="4,4"))
    f.append(text(ox - 75, oy + 75, "Y_true", size=11, color=FIELD, anchor="end", bold=True))

    # Реальні осі зі скосом і різним масштабом (суцільні сині)
    # Вісь X' (трохи задерта вгору)
    f.append(arrow(ox, oy, ox + 135, oy - 22, color=NEG, sw=2.2))
    f.append(text(ox + 140, oy - 25, "X_sens (s_x)", size=11, color=NEG, anchor="start", bold=True))

    # Вісь Z' (нахилена вправо)
    f.append(arrow(ox, oy, ox + 25, oy - 125, color=NEG, sw=2.2))
    f.append(text(ox + 30, oy - 130, "Z_sens (s_z)", size=11, color=NEG, anchor="start", bold=True))

    # Вісь Y' (скошена)
    f.append(arrow(ox, oy, ox - 60, oy + 70, color=NEG, sw=2.2))
    f.append(text(ox - 65, oy + 88, "Y_sens (s_y)", size=11, color=NEG, anchor="end", bold=True))

    # Дуги неортогональності
    f.append(text(ox + 80, oy - 8, "α_xy", size=10, color=POS, italic=True))
    f.append(text(ox + 10, oy - 70, "α_zx", size=10, color=POS, italic=True))

    f.append(text(205, 385, "Осі не ортогональні, масштаби не рівні 1.0", size=11, color=INK, italic=True))

    # Права рамка: Деформація вимірювального простору (сфера → еліпсоїд)
    f.append(rect(410, 20, 390, 380, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(605, 46, "Деформація годографа прискорення 1g", size=13, bold=True))

    cx, cy = 605, 230
    
    # Ідеальна сфера 1g (зелена, коло)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>' %
             (cx, cy, 90, FIELD))
    f.append(text(cx + 96, cy - 60, "Ідеальна сфера 1g", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(cx + 96, cy - 44, "||a_true|| = 1.0", size=9.5, color=FIELD, anchor="start"))

    # Реальний деформований еліпсоїд (червоний/синій, зміщений і повернутий)
    # Зміщений центр
    ecx, ecy = cx + 25, cy - 20
    f.append(circle(ecx, ecy, 3.5, fill=POS, stroke=POS))
    f.append(line(cx, cy, ecx, ecy, color=POS, sw=1.5, dash="2,2"))
    f.append(text(ecx + 8, ecy + 4, "Центр (b_x, b_y, b_z)", size=10, color=POS, anchor="start", bold=True))

    # Еліпс як контур
    f.append('<ellipse cx="%d" cy="%d" rx="115" ry="75" fill="none" stroke="%s" stroke-width="2.2" transform="rotate(-20 %d %d)"/>' %
             (ecx, ecy, NEG, ecx, ecy))
    f.append(text(ecx - 120, ecy - 45, "Реальний еліпсоїд", size=10.5, color=NEG, anchor="end", bold=True))
    f.append(text(ecx - 120, ecy - 30, "(зсув + масштаб + скіс)", size=9.5, color=NEG, anchor="end"))

    # Математична формула калібрування в рамці внизу
    bx, bw, bh = textbox(605, 350, "a_cal = (M · S)⁻¹ · (a_raw − b)", size=12, pad=8,
                         fill="#ffffff", stroke=LINE, sw=1.5, color=INK, bold=True)
    f.append(bx)

    render(os.path.join(IMG, "imu-error-model.svg"), W, H, *f,
           title="Модель похибок інерціальних давачів")


# ── 2. Статичне калібрування гіроскопа (Zero-Rate Level) ─────────────────────
def fig_gyro_zero_rate():
    W, H = 780, 380
    f = []

    # Ліва рамка: Сигнал гіроскопа в часі
    f.append(rect(20, 20, 380, 340, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(210, 46, "Сигнал нерухомого гіроскопа у часі", size=13, bold=True))

    ox, oy = 60, 260
    _axes(f, ox, oy, 70, 380, ylab="ω, °/с", xlab="Час t, с")

    # Лінія справжнього нуля (0.0 °/с)
    f.append(line(ox, oy - 40, 370, oy - 40, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(65, oy - 48, "0.0 °/с (справжній спокій)", size=10, color=FIELD, anchor="start", bold=True))

    # Лінія зміщення нуля b_gyro (+0.8 °/с)
    bias_y = oy - 120
    f.append(line(ox, bias_y, 370, bias_y, color=POS, sw=2, dash="5,3"))
    f.append(text(65, bias_y - 8, "Зсув нуля b_gyro = +0.80 °/с", size=10.5, color=POS, anchor="start", bold=True))

    # Стрілка між нулем і зміщенням
    f.append(arrow(340, oy - 40, 340, bias_y, color=POS, sw=1.5))
    f.append(text(348, (oy - 40 + bias_y)/2 + 4, "b_gyro", size=10, color=POS, anchor="start", bold=True))

    # Шумна траса навколо зміщення нуля
    pts = []
    noise_vals = [0.0, 0.15, -0.12, 0.22, -0.05, -0.28, 0.18, 0.05, -0.15, 0.25,
                  -0.20, 0.10, 0.30, -0.18, 0.02, -0.22, 0.14, -0.08, 0.19, -0.11,
                  0.05, 0.21, -0.16, -0.04, 0.12, -0.25, 0.17, 0.03, -0.19, 0.15]
    step_x = (360 - ox) / len(noise_vals)
    for i, nv in enumerate(noise_vals):
        px = ox + i * step_x
        py = bias_y - nv * 100
        pts.append((px, py))
    
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path_d, NEG))

    # Пояснення усереднення
    f.append(text(210, 330, "Швидкий шум коливається навколо зміщення", size=10.5, color=MUTED, italic=True))

    # Права рамка: Розподіл вибірок (Гаусіана) та зниження дисперсії
    f.append(rect(420, 20, 340, 340, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(590, 46, "Густина ймовірності вибірок p(ω)", size=13, bold=True))

    # Осі для гістограми/гаусіани
    gox, goy = 450, 260
    _axes(f, gox, goy, 70, 740, ylab="p(ω)", xlab="ω, °/с")

    # Гаусова крива
    gcx = gox + 130
    curve_pts = []
    for step in range(-80, 85, 5):
        kx = gcx + step
        sigma = 25.0
        val = math.exp(-0.5 * (step / sigma) ** 2)
        ky = goy - val * 150
        curve_pts.append((kx, ky))
    
    gpath_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in curve_pts)
    f.append('<path d="%s" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2.2"/>' %
             (gpath_d + (" L %.1f,%.1f Z" % (curve_pts[-1][0], goy)), LIGHT_BLUE, NEG))

    # Центральна лінія (математичне сподівання)
    f.append(line(gcx, goy, gcx, goy - 160, color=POS, sw=2, dash="4,3"))
    f.append(text(gcx, goy - 170, "Оцінка b̂ = 1/N ∑ ωᵢ", size=10.5, color=POS, anchor="middle", bold=True))

    # Позначення смуги шуму ±σ
    f.append(line(gcx - 25, goy - 90, gcx + 25, goy - 90, color=INK, sw=1.4))
    f.append(text(gcx, goy - 75, "2 · σ_шуму", size=10, color=INK, anchor="middle"))

    # Помилка оцінки спадає як 1/sqrt(N)
    bx, bw, bh = textbox(590, 320, "Похибка оцінки: σ_mean = σ / √N\nПри N=2000 шум спадає в 45 разів",
                         size=11, pad=8, fill="#ffffff", stroke=LINE, sw=1.5, color=INK, bold=False)
    f.append(bx)

    render(os.path.join(IMG, "gyro-zero-rate-distribution.svg"), W, H, *f,
           title="Калібрування нульового зміщення гіроскопа в стані спокою")


# ── 3. Калібрування акселерометра методом 6 положень ──────────────────────────
def fig_six_position_test():
    W, H = 840, 480
    f = []

    # Заголовок зверху
    f.append(rect(20, 15, 800, 450, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(420, 42, "Метод 6 статичних положень у полі гравітації 1g", size=14, bold=True))
    f.append(text(420, 62, "Послідовна орієнтація кожної осі вгору (+1g) та вниз (-1g)", size=11, color=MUTED, italic=True))

    # 6 кубів: сітка 3 x 2
    pos_data = [
        (50, 85, "Положення 1: +Z вгору", "[ 0,  0, +1 ]ᵀ g", "Z відчуває +1g, X/Y = 0g", "+Z"),
        (310, 85, "Положення 2: +Y вгору", "[ 0, +1,  0 ]ᵀ g", "Y відчуває +1g, X/Z = 0g", "+Y"),
        (570, 85, "Положення 3: +X вгору", "[ +1,  0,  0 ]ᵀ g", "X відчуває +1g, Y/Z = 0g", "+X"),
        (50, 275, "Положення 4: -Z вгору", "[ 0,  0, -1 ]ᵀ g", "Z відчуває -1g, X/Y = 0g", "-Z"),
        (310, 275, "Положення 5: -Y вгору", "[ 0, -1,  0 ]ᵀ g", "Y відчуває -1g, X/Z = 0g", "-Y"),
        (570, 275, "Положення 6: -X вгору", "[ -1,  0,  0 ]ᵀ g", "X відчуває -1g, Y/Z = 0g", "-X"),
    ]

    for px, py, title, g_vec, desc, axis_label in pos_data:
        f.append(rect(px, py, 220, 170, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
        f.append(text(px + 110, py + 22, title, size=11, color=INK, bold=True))

        cx, cy = px + 65, py + 95
        f.append(rect(cx - 30, cy - 30, 60, 60, fill=LIGHT_BLUE, stroke=LINE, sw=1.5, rx=3))
        f.append(text(cx, cy + 5, axis_label, size=14, color=NEG, bold=True))

        # Вектор сили тяжіння g
        f.append(arrow(cx + 45, cy - 25, cx + 45, cy + 25, color=FIELD, sw=2.2))
        f.append(text(cx + 52, cy + 5, "g", size=12, color=FIELD, anchor="start", bold=True))

        f.append(text(px + 150, py + 65, "a_true:", size=10, color=MUTED, bold=True))
        f.append(text(px + 150, py + 85, g_vec, size=10.5, color=FIELD, bold=True))
        f.append(text(px + 110, py + 145, desc, size=9.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "six-position-test.svg"), W, H, *f,
           title="Калібрування акселерометра методом шести положень")


# ── 4. Температурний дрейф зміщення нуля та компенсація ──────────────────────
def fig_temp_drift_compensation():
    W, H = 800, 400
    f = []

    # Загальна рамка
    f.append(rect(20, 20, 760, 360, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(400, 46, "Температурний дрейф зміщення нуля та його компенсація", size=13, bold=True))

    ox, oy = 80, 240
    _axes(f, ox, oy, 70, 740, ylab="Зсув нуля b(T), °/с", xlab="Температура T, °C")

    # Температурні позначки по осі X
    t_marks = [(-20, 140), (0, 250), (25, 380), (50, 520), (70, 640)]
    for temp, px in t_marks:
        f.append(line(px, oy - 4, px, oy + 4, color=LINE, sw=1.2))
        f.append(text(px, oy + 18, "%d" % temp, size=10, color=MUTED))

    # Нульова лінія зсуву
    f.append(line(ox, oy, 720, oy, color=LINE, sw=1, dash="2,2"))

    # Крива сирого нескомпенсованого дрейфу
    raw_pts = []
    for step in range(100, 680, 20):
        T = (step - 380) / 4.0
        b_val = -0.00008 * ((T - 10) ** 3) + 0.012 * (T - 10) + 0.8
        py = oy - b_val * 60
        raw_pts.append((step, py))

    raw_path = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in raw_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (raw_path, POS))
    f.append(text(675, 110, "Сирий дрейф b_raw(T)", size=10.5, color=POS, anchor="end", bold=True))

    # Крива полінома 3-го порядку
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6,4"/>' % (raw_path, FIELD))
    f.append(text(675, 128, "Поліном 3-го порядку b_poly(T)", size=10.5, color=FIELD, anchor="end", bold=True))

    # Точки Look-Up Table (LUT)
    for px, py in raw_pts[::3]:
        f.append(circle(px, py, 4, fill=NEG, stroke=INK, sw=1.2))
    f.append(text(460, 85, "Вузли таблиці LUT", size=10, color=NEG, anchor="start", bold=True))

    # Залишкова похибка після компенсації
    res_pts = []
    for step in range(100, 680, 20):
        T = (step - 380) / 4.0
        res_val = 0.05 * math.sin(T * 0.15)
        py = oy - res_val * 60
        res_pts.append((step, py))
    
    res_path = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in res_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (res_path, NEG))
    f.append(text(675, oy - 14, "Залишковий дрейф після компенсації (±0.05 °/с)", size=10.5, color=NEG, anchor="end", bold=True))

    # Пояснювальний блок знизу
    bx, bw, bh = textbox(400, 335, "Компенсація зменшує температурний дрейф у 15–30 разів:\n"
                                   "b(T) = c₀ + c₁·(T − T₀) + c₂·(T − T₀)² + c₃·(T − T₀)³",
                         size=11, pad=8, fill="#ffffff", stroke=LINE, sw=1.5, color=INK, bold=False)
    f.append(bx)

    render(os.path.join(IMG, "temp-drift-compensation.svg"), W, H, *f,
           title="Температурна компенсація зміщення нуля IMU")


# ── 5. Пайплайн обробки та калібрування в реальному часі ──────────────────────
def fig_calibration_pipeline():
    W, H = 840, 380
    f = []

    f.append(rect(20, 15, 800, 350, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(420, 42, "Конвеєр виправлення інерціальних вимірювань у реальному часі", size=13.5, bold=True))

    # Блок 1: Сирі дані IMU
    b1_x, b1_y = 90, 120
    f.append(rect(30, 80, 120, 90, fill="#ffffff", stroke=LINE, sw=1.5, rx=5))
    f.append(text(b1_x, b1_y - 15, "MEMS IMU", size=11.5, bold=True))
    f.append(text(b1_x, b1_y + 2, "a_raw, ω_raw", size=10.5, color=POS, bold=True))
    f.append(text(b1_x, b1_y + 18, "Температура T", size=10, color=MUTED))

    # Стрілка 1 -> 2
    f.append(arrow(150, 125, 200, 125, color=INK, sw=2))
    f.append(text(175, 115, "SPI / I2C", size=9.5, color=MUTED))

    # Блок 2: Температурна компенсація зсуву
    b2_x, b2_y = 280, 120
    f.append(rect(200, 80, 160, 90, fill=LIGHT_BLUE, stroke=LINE, sw=1.5, rx=5))
    f.append(text(b2_x, b2_y - 15, "Температурний блок", size=11, bold=True))
    f.append(text(b2_x, b2_y + 2, "b(T) = Poly(T) | LUT", size=10, color=NEG, bold=True))
    f.append(text(b2_x, b2_y + 18, "v₁ = v_raw − b(T)", size=10.5, color=INK, bold=True))

    # Стрілка 2 -> 3
    f.append(arrow(360, 125, 410, 125, color=INK, sw=2))
    f.append(text(385, 115, "v₁", size=10.5, color=INK, bold=True))

    # Блок 3: Матрична корекція неортогональності та масштабу
    b3_x, b3_y = 495, 120
    f.append(rect(410, 80, 170, 90, fill=LIGHT_GREEN, stroke=LINE, sw=1.5, rx=5))
    f.append(text(b3_x, b3_y - 15, "Матрична корекція", size=11, bold=True))
    f.append(text(b3_x, b3_y + 2, "v_cal = K · v₁", size=11, color=FIELD, bold=True))
    f.append(text(b3_x, b3_y + 18, "K = (M · S)⁻¹ (3×3)", size=10, color=INK))

    # Стрілка 3 -> 4
    f.append(arrow(580, 125, 630, 125, color=INK, sw=2))

    # Блок 4: Вихід на алгоритми орієнтації (AHRS / EKF)
    b4_x, b4_y = 705, 120
    f.append(rect(630, 80, 150, 90, fill="#ffffff", stroke=LINE, sw=1.5, rx=5))
    f.append(text(b4_x, b4_y - 15, "Очищений вихід", size=11, bold=True))
    f.append(text(b4_x, b4_y + 2, "a_cal, ω_cal (СІ)", size=10.5, color=FIELD, bold=True))
    f.append(text(b4_x, b4_y + 18, "→ EKF / AHRS", size=10, color=MUTED))

    # Нижня частина: Енергонезалежна пам'ять (Flash / EEPROM)
    f.append(rect(270, 230, 310, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=5))
    f.append(text(425, 255, "Енергонезалежна пам'ять (EEPROM / Flash)", size=11.5, bold=True))
    f.append(text(425, 275, "Збереження: Matrix K [3×3], Poly coeffs, CRC32", size=10.5, color=MUTED))
    f.append(text(425, 295, "Завантаження при старті системи (Boot)", size=10, color=POS, italic=True))

    # Стрілки між пам'яттю та обчислювальними блоками
    f.append(arrow(380, 230, 280, 170, color=POS, sw=1.8))
    f.append(arrow(470, 230, 495, 170, color=POS, sw=1.8))

    render(os.path.join(IMG, "calibration-pipeline.svg"), W, H, *f,
           title="Конвеєр калібрування та корекції даних IMU")


if __name__ == "__main__":
    fig_imu_error_model()
    fig_gyro_zero_rate()
    fig_six_position_test()
    fig_temp_drift_compensation()
    fig_calibration_pipeline()
    print("Всі 5 фігур успішно згенеровано у ./img/")
