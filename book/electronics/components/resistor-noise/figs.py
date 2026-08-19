# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e0a32e"
AMBERBG = "#fff3e0"
REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"


# ── 1. johnson-nyquist-model: фізика та еквівалентні схеми ───────────────────
def fig_johnson_nyquist_model():
    W, H = 820, 360
    p = []

    # Блок 1: Фізичний механізм (ліворуч)
    p.append(rect(30, 48, 240, 280, fill=BLUEBG, stroke=NEG, sw=1.6, rx=8))
    p.append(text(150, 72, "ФІЗИЧНИЙ МЕХАНІЗМ", size=12, color=NEG, bold=True))
    p.append(text(150, 90, "Тепловий рух носіїв", size=10, color=MUTED))

    # Кристалічна ґратка з іонами (+) та електронами (e−)
    p.append(rect(45, 105, 210, 150, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    # Іони ґратки
    for ix in [75, 125, 175, 225]:
        for iy in [130, 175, 220]:
            p.append(circle(ix, iy, 8, fill="#fee2e2", stroke=POS, sw=1.2))
            p.append(text(ix, iy + 3.5, "+", size=10, color=POS, bold=True))
    # Хаотичні вектори електронів
    e_pos = [(95, 145, 115, 135), (150, 140, 140, 165), (200, 155, 215, 180),
             (100, 195, 80, 210), (160, 205, 185, 200)]
    for x1, y1, x2, y2 in e_pos:
        p.append(circle(x1, y1, 4, fill=NEG, stroke=NEG, sw=1))
        p.append(arrow(x1, y1, x2, y2, color=NEG, sw=1.3))

    p.append(text(150, 275, "E_тепл = k_B · T", size=11, color=INK, bold=True))
    p.append(text(150, 295, "Броунівські флуктуації заряду", size=9, color=MUTED))
    p.append(text(150, 312, "<V(t)> = 0, але <V²(t)> ≠ 0", size=9.5, color=NEG, bold=True))

    # Блок 2: Модель Тевеніна (посередині)
    p.append(rect(290, 48, 240, 280, fill=GRNBG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(410, 72, "МОДЕЛЬ ТЕВЕНІНА", size=12, color=FIELD, bold=True))
    p.append(text(410, 90, "Послідовне джерело напруги", size=10, color=MUTED))

    # Схема Тевеніна
    # Провідники
    p.append(line(320, 130, 360, 130, color=LINE, sw=1.8))
    p.append(line(460, 130, 500, 130, color=LINE, sw=1.8))
    p.append(line(320, 220, 500, 220, color=LINE, sw=1.8))
    # Клеми
    p.append(circle(320, 130, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(500, 130, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(320, 220, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(500, 220, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    # Генератор шуму e_n
    p.append(circle(380, 130, 18, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(380, 134, "~", size=18, color=FIELD, bold=True))
    p.append(text(380, 102, "e_n", size=12, color=FIELD, bold=True))
    p.append(line(398, 130, 420, 130, color=LINE, sw=1.8))
    # Безшумний резистор R
    p.append(rect(420, 120, 40, 20, fill="#ffffff", stroke=LINE, sw=1.8, rx=2))
    p.append(text(440, 102, "R (без шуму)", size=10, color=INK, bold=True))

    p.append(text(410, 255, "e_n = √(4·k_B·T·R·Δf)", size=11, color=FIELD, bold=True))
    p.append(text(410, 278, "Спектральна густина:", size=9, color=MUTED))
    p.append(text(410, 296, "e_n / √Δf ≈ 4 нВ/√Гц (1 кОм)", size=9.5, color=INK, bold=True))
    p.append(text(410, 314, "при кімнатній T = 290–300 K", size=9, color=MUTED))

    # Блок 3: Модель Нортона (праворуч)
    p.append(rect(550, 48, 240, 280, fill=AMBERBG, stroke=AMBER, sw=1.6, rx=8))
    p.append(text(670, 72, "МОДЕЛЬ НОРТОНА", size=12, color=AMBER, bold=True))
    p.append(text(670, 90, "Паралельне джерело струму", size=10, color=MUTED))

    # Схема Нортона
    p.append(line(575, 120, 765, 120, color=LINE, sw=1.8))
    p.append(line(575, 225, 765, 225, color=LINE, sw=1.8))
    # Клеми
    p.append(circle(575, 120, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(765, 120, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(575, 225, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(circle(765, 225, 3.5, fill="#ffffff", stroke=LINE, sw=1.8))
    # Вертикальні гілки
    # Гілка джерела струму i_n
    p.append(line(630, 120, 630, 155, color=LINE, sw=1.8))
    p.append(circle(630, 172, 18, fill="#ffffff", stroke=AMBER, sw=1.8))
    p.append(arrow(630, 182, 630, 162, color=AMBER, sw=1.8))
    p.append(text(600, 176, "i_n", size=12, color=AMBER, bold=True))
    p.append(line(630, 190, 630, 225, color=LINE, sw=1.8))
    # Гілка резистора R
    p.append(line(710, 120, 710, 152, color=LINE, sw=1.8))
    p.append(rect(700, 152, 20, 40, fill="#ffffff", stroke=LINE, sw=1.8, rx=2))
    p.append(text(740, 176, "R", size=11, color=INK, bold=True))
    p.append(line(710, 192, 710, 225, color=LINE, sw=1.8))

    p.append(text(670, 255, "i_n = √(4·k_B·T·Δf / R)", size=11, color=AMBER, bold=True))
    p.append(text(670, 278, "Спектральна густина:", size=9, color=MUTED))
    p.append(text(670, 296, "i_n / √Δf ≈ 4 пА/√Гц (1 кОм)", size=9.5, color=INK, bold=True))
    p.append(text(670, 314, "i_n = e_n / R (двоїстість)", size=9, color=MUTED))

    render(os.path.join(OUT, "johnson-nyquist-model.svg"), W, H, *p,
           title="Моделі теплового шуму резистора")


# ── 2. noise-spectrum-combined: повний спектральний профіль ──────────────────
def fig_noise_spectrum():
    W, H = 760, 360
    p = []

    # Осі
    ox, oy = 100, 280
    w_axis, h_axis = 610, 220
    p.append(line(ox, oy, ox + w_axis, oy, color=LINE, sw=2))
    p.append(line(ox, oy, ox, oy - h_axis, color=LINE, sw=2))
    p.append(arrow(ox + w_axis - 10, oy, ox + w_axis + 10, oy, color=LINE, sw=2))
    p.append(arrow(ox, oy - h_axis + 10, ox, oy - h_axis - 10, color=LINE, sw=2))

    p.append(text(ox + w_axis - 20, oy + 32, "Частота f (Гц, логарифмічна шкала)", size=11, color=INK, bold=True))
    p.append(text(ox - 15, oy - h_axis - 2, "Густина e_n (нВ/√Гц)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки частоти
    freqs = [(150, "1 Гц"), (240, "10 Гц"), (330, "100 Гц"), (420, "1 кГц"),
             (510, "10 кГц"), (600, "100 кГц"), (680, "1 МГц")]
    for fx, flab in freqs:
        p.append(line(fx, oy, fx, oy + 5, color=LINE, sw=1.2))
        p.append(text(fx, oy + 18, flab, size=9.5, color=MUTED))
        p.append(line(fx, oy, fx, oy - h_axis + 10, color="#f1f5f9", sw=1, dash="3,3"))

    # Рівні шуму
    # Білий шум (горизонтальна лінія)
    white_y = 200
    p.append(line(ox, white_y, ox + w_axis - 40, white_y, color=NEG, sw=1.5, dash="4,4"))
    p.append(text(ox - 10, white_y + 4, "e_білий", size=10, color=NEG, anchor="end", bold=True))

    # Спектр при наявності DC-струму (1/f + білий)
    pts = []
    for step in range(0, 560, 5):
        cur_x = ox + step
        flicker = 140.0 / ((step / 35.0) + 1.2) ** 0.95
        cur_y = white_y - flicker
        pts.append((cur_x, cur_y))

    path_d = ["M %.1f,%.1f" % pts[0]]
    for px, py in pts[1:]:
        path_d.append("L %.1f,%.1f" % (px, py))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path_d), POS))

    # Кутова частота f_c (corner frequency)
    fc_x = 350
    p.append(circle(fc_x, white_y - 12, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(line(fc_x, oy, fc_x, white_y - 12, color=AMBER, sw=1.5, dash="3,3"))
    p.append(text(fc_x, oy + 32, "f_c (кутова частота)", size=10, color=AMBER, bold=True))

    # Зони на графіку
    # Зона 1/f
    p.append(rect(120, 80, 180, 50, fill=REDBG, stroke=POS, sw=1.2, rx=6))
    p.append(text(210, 100, "ЗОНА 1/f (ФЛІКЕР-ШУМ)", size=10, color=POS, bold=True))
    p.append(text(210, 118, "e_ex ~ I_DC / √f (спад −10 дБ/дек)", size=9, color=INK))

    # Зона білого шуму
    p.append(rect(450, 110, 230, 56, fill=BLUEBG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(565, 130, "ЗОНА БІЛОГО ШУМУ", size=10, color=NEG, bold=True))
    p.append(text(565, 146, "e_n = √(4·k_B·T·R) (стала густина)", size=9, color=INK))
    p.append(text(565, 158, "Джонсон-Найквіст (термодинамічний)", size=9.5, color=MUTED))

    # Квантова межа (виноска праворуч)
    p.append(text(ox + w_axis - 50, white_y - 15, "Квантовий спад (f > 6 ТГц)", size=9.5, color=MUTED))

    render(os.path.join(OUT, "noise-spectrum-combined.svg"), W, H, *p,
           title="Повний спектр напруги шуму резистора: 1/f та білий шум")


# ── 3. grain-boundary-flicker: мікроструктура та флікер-шум ──────────────────
def fig_grain_boundary_flicker():
    W, H = 780, 360
    p = []

    # Ліва половина: Гранулярна товстоплівка / композит (високий флікер-шум)
    p.append(rect(30, 48, 345, 280, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(202, 72, "ТОВСТОПЛІВКА / КОМПОЗИТ", size=12, color=POS, bold=True))
    p.append(text(202, 90, "Гранулярна мікроструктура (NI: −10…+10 дБ)", size=9.5, color=MUTED))

    # Матриця зі склом/полімером та гранулами
    p.append(rect(48, 105, 309, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))

    # Скляна зв'язка (фон)
    p.append(text(75, 122, "Діелектрик", size=9.5, color="#94a3b8"))

    # Провідні гранули RuO2 або сажі
    grains = [
        (85, 160, 16), (120, 145, 20), (165, 150, 18), (145, 190, 22),
        (205, 165, 24), (250, 150, 19), (285, 170, 17), (230, 205, 21),
        (185, 215, 18), (105, 210, 17), (320, 160, 15), (295, 210, 18)
    ]
    for gx, gy, gr in grains:
        p.append(circle(gx, gy, gr, fill="#475569", stroke="#1e293b", sw=1.4))

    # Струмові лінії перколяції з вузькими шийками
    p.append(arrow(40, 160, 68, 160, color=POS, sw=2.2))
    p.append(arrow(101, 155, 102, 150, color=POS, sw=1.8))
    p.append(arrow(139, 147, 147, 149, color=POS, sw=1.8))
    p.append(arrow(183, 155, 185, 160, color=POS, sw=1.8))
    p.append(arrow(229, 160, 231, 155, color=POS, sw=1.8))
    p.append(arrow(269, 155, 269, 165, color=POS, sw=1.8))
    p.append(arrow(302, 165, 335, 165, color=POS, sw=2.2))

    # Пастки захоплення носіїв (дефекти на межах гранул)
    p.append(circle(142, 168, 4, fill=AMBER, stroke="#b45309", sw=1))
    p.append(circle(228, 185, 4, fill=AMBER, stroke="#b45309", sw=1))
    p.append(text(175, 180, "Пастка", size=9.5, color=AMBER, bold=True))

    p.append(text(202, 262, "Флуктуації контактного опору ΔR(t)", size=10, color=POS, bold=True))
    p.append(text(202, 282, "Струм іде через вузькі містки й тунельні бар'єри", size=9, color=INK))
    p.append(text(202, 300, "Захоплення/вивільнення носіїв → спектр 1/f", size=9, color=MUTED))

    # Права половина: Монолітна тонкоплівка / фольга (мінімальний флікер-шум)
    p.append(rect(405, 48, 345, 280, fill=GRNBG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(577, 72, "ТОНКОПЛІВКА / МЕТАЛ-ФОЛЬГА", size=12, color=FIELD, bold=True))
    p.append(text(577, 90, "Суцільна металева структура (NI: −40…−50 дБ)", size=9.5, color=MUTED))

    # Однорідний металевий шар NiCr
    p.append(rect(423, 105, 309, 140, fill="#f1f5f9", stroke=FIELD, sw=1.2, rx=6))
    p.append(rect(435, 130, 285, 90, fill="#cbd5e1", stroke="#64748b", sw=1.4, rx=4))
    p.append(text(577, 148, "Монолітний сплав NiCr / фольга Ni-Cr-Al", size=9.5, color="#334155", bold=True))

    # Рівномірний ламінарний потік струму
    for py in [165, 185, 205]:
        p.append(arrow(415, py, 735, py, color=FIELD, sw=2))

    p.append(text(577, 262, "Відсутність міжгранульних бар'єрів", size=10, color=FIELD, bold=True))
    p.append(text(577, 282, "Рівномірне розсіювання на фононах ґратки", size=9, color=INK))
    p.append(text(577, 300, "Лише фундаментальний білий шум Джонсона", size=9, color=MUTED))

    render(os.path.join(OUT, "grain-boundary-flicker.svg"), W, H, *p,
           title="Мікроструктурна природа надлишкового шуму (1/f) у резисторах")


# ── 4. opamp-noise-budget: шум схеми та шумовий опір ─────────────────────────
def fig_opamp_noise_budget():
    W, H = 820, 380
    p = []

    # Верхня частина: Електрична схема вхідного каскаду
    p.append(rect(30, 48, 760, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=8))
    p.append(text(410, 68, "ШУМОВА МОДЕЛЬ НЕІНВЕРТУЮЧОГО ПІДСИЛЮВАЧА", size=11, color=INK, bold=True))

    # Генератор сигналу з опором джерела R_s
    p.append(circle(75, 125, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(75, 129, "Vs", size=10, color=INK))
    p.append(line(75, 139, 75, 165, color=LINE, sw=1.5))
    p.append(line(65, 165, 85, 165, color=LINE, sw=1.5))  # земля
    p.append(line(89, 125, 115, 125, color=LINE, sw=1.5))

    # R_s та його шум e_ns
    p.append(rect(115, 115, 45, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(137, 106, "R_s", size=10, color=INK, bold=True))
    p.append(line(160, 125, 185, 125, color=LINE, sw=1.5))
    p.append(circle(200, 125, 12, fill="#ffffff", stroke=NEG, sw=1.5))
    p.append(text(200, 129, "~", size=14, color=NEG, bold=True))
    p.append(text(200, 104, "e_n(Rs)", size=9.5, color=NEG, bold=True))
    p.append(line(212, 125, 255, 125, color=LINE, sw=1.5))

    # Струмовий шум підсилювача i_n+
    p.append(line(235, 125, 235, 155, color=LINE, sw=1.4))
    p.append(circle(235, 165, 9, fill="#ffffff", stroke=AMBER, sw=1.4))
    p.append(arrow(235, 170, 235, 160, color=AMBER, sw=1.4))
    p.append(text(260, 168, "i_n+", size=9.5, color=AMBER, bold=True))

    # Трикутник операційного підсилювача
    p.append('<polygon points="255,95 255,165 325,130" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % LINE)
    p.append(text(268, 120, "+", size=14, color=LINE, bold=True))
    p.append(text(268, 146, "−", size=14, color=LINE, bold=True))

    # Вхідний шум напруги ОП e_na
    p.append(text(300, 100, "e_na", size=10, color=POS, bold=True))
    p.append(line(325, 130, 390, 130, color=LINE, sw=1.8))
    p.append(circle(390, 130, 3.5, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(410, 134, "V_вих", size=10, color=INK, bold=True))

    # Зворотний зв'язок (R1, R2)
    p.append(line(355, 130, 355, 170, color=LINE, sw=1.4))
    p.append(line(355, 170, 290, 170, color=LINE, sw=1.4))
    p.append(line(290, 170, 290, 146, color=LINE, sw=1.4))
    p.append(line(290, 146, 255, 146, color=LINE, sw=1.4))
    # Резистор R2 у зворотній гілці
    p.append(rect(305, 162, 35, 16, fill="#ffffff", stroke=LINE, sw=1.4, rx=2))
    p.append(text(322, 156, "R2", size=9, color=INK))
    # Резистор R1 на землю
    p.append(line(275, 146, 275, 170, color=LINE, sw=1.4))
    p.append(rect(265, 170, 20, 14, fill="#ffffff", stroke=LINE, sw=1.4, rx=2))
    p.append(text(250, 180, "R1", size=9, color=INK))

    # Формула повного шуму (праворуч у верхній рамці)
    p.append(rect(455, 75, 320, 95, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(615, 95, "e_вх,сумарний² =", size=10, color=INK, bold=True))
    p.append(text(615, 115, "e_na² + 4k_B T R_s + (i_na · R_s)² + 4k_B T (R1||R2)", size=9.5, color=POS, bold=True))
    p.append(text(615, 138, "R_opt = e_na / i_na  (точка балансу шумів)", size=9.5, color=FIELD, bold=True))
    p.append(text(615, 156, "де R_s ≪ R_opt: домінує e_na; де R_s ≫ R_opt: i_na·R_s", size=9.5, color=MUTED))

    # Нижня частина: Графік залежності шуму від опору джерела R_s
    ox, oy = 90, 345
    w_ax, h_ax = 680, 130
    p.append(line(ox, oy, ox + w_ax, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - h_ax, color=LINE, sw=1.8))
    p.append(arrow(ox + w_ax - 10, oy, ox + w_ax + 10, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - h_ax + 10, ox, oy - h_ax - 10, color=LINE, sw=1.8))

    p.append(text(ox + w_ax - 20, oy + 24, "Опір джерела R_s (Ом, логарифмічна шкала)", size=10, color=INK, bold=True))
    p.append(text(ox - 10, oy - h_ax + 4, "Шум e_вх (нВ/√Гц)", size=10, color=INK, bold=True, anchor="end"))

    # Позначки осі X
    r_pts = [(150, "10 Ом"), (270, "1 кОм"), (390, "10 кОм"), (510, "100 кОм"), (630, "1 МОм")]
    for rx_pos, rlab in r_pts:
        p.append(line(rx_pos, oy, rx_pos, oy + 4, color=LINE, sw=1.2))
        p.append(text(rx_pos, oy + 16, rlab, size=9, color=MUTED))

    # Лінії трьох компонент
    # 1. e_na (горизонтальна червона лінія)
    p.append(line(ox, 310, ox + w_ax - 30, 310, color=POS, sw=1.4, dash="4,4"))
    p.append(text(120, 305, "Шум напруги ОП (e_na)", size=9.5, color=POS, bold=True))

    # 2. Тепловий шум резистора R_s (синя похила лінія, нахил +10 дБ/дек)
    p.append(line(ox + 30, 335, ox + 550, 245, color=NEG, sw=1.4, dash="4,4"))
    p.append(text(460, 275, "Тепловий шум √(4 k_B T R_s)", size=9.5, color=NEG, bold=True))

    # 3. Шум струму ОП (i_na * R_s) (похила помаранчева лінія, нахил +20 дБ/дек)
    p.append(line(ox + 200, 340, ox + 620, 225, color=AMBER, sw=1.4, dash="4,4"))
    p.append(text(620, 240, "Шум струму (i_na · R_s)", size=9.5, color=AMBER, bold=True))

    # Сумарна крива (жирна зелена)
    sum_pts = [
        (ox + 10, 308), (ox + 100, 306), (ox + 200, 300),
        (ox + 300, 285), (ox + 400, 260), (ox + 500, 235), (ox + 600, 215)
    ]
    spath = ["M %.1f,%.1f" % sum_pts[0]]
    for sx, sy in sum_pts[1:]:
        spath.append("L %.1f,%.1f" % (sx, sy))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(spath), FIELD))

    # Точка R_opt
    p.append(circle(ox + 340, 278, 5, fill="#ffffff", stroke=FIELD, sw=2))
    p.append(text(ox + 340, 255, "R_opt", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "opamp-noise-budget.svg"), W, H, *p,
           title="Шумовий баланс схеми: вибір опорів та підсилювача")


if __name__ == "__main__":
    fig_johnson_nyquist_model()
    fig_noise_spectrum()
    fig_grain_boundary_flicker()
    fig_opamp_noise_budget()
    print("Всі фігури згенеровано успішно.")
