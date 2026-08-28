# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Статичний зсув центру мас (CG) відносно центру тяги (CoT)
# ════════════════════════════════════════════════════════════════════════════
def fig_cg_cot_offset():
    W, H = 840, 400
    body = ""

    # Ліва панель — Геометрія рами й сил
    body += rect(20, 20, 420, 360, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(230, 48, "Розподіл сил при статичному зміщенні CG", size=15, bold=True)

    # Рама дрона (Х-подібна)
    cx, cy = 230, 195
    # Промені
    body += line(cx - 110, cy - 80, cx + 110, cy + 80, color="#9ca3af", sw=5)
    body += line(cx - 110, cy + 80, cx + 110, cy - 80, color="#9ca3af", sw=5)
    # Корпус
    body += circle(cx, cy, 32, fill="#e5e7eb", stroke=LINE, sw=2)

    # Центр тяги CoT (0, 0)
    body += circle(cx, cy, 7, fill=NEG, stroke="#ffffff", sw=1.5)
    body += text(cx - 16, cy - 14, "CoT", size=12, color=NEG, bold=True, anchor="end")
    body += text(cx - 16, cy + 2, "(Центр тяги)", size=10, color=MUTED, anchor="end")

    # Зміщений центр мас CG
    cg_x = cx + 45
    cg_y = cy + 30
    body += line(cx, cy, cg_x, cg_y, color=POS, sw=2, dash="3 3")
    body += circle(cg_x, cg_y, 7, fill=POS, stroke="#ffffff", sw=1.5)
    body += text(cg_x + 16, cg_y + 4, "CG", size=12, color=POS, bold=True, anchor="start")
    body += text(cg_x + 16, cg_y + 18, "(Центр мас)", size=10, color=MUTED, anchor="start")

    # Вектор важеля зміщення Δr
    body += text(cx + 28, cy + 8, "Δr", size=12, color=POS, bold=True)

    # Мотори та вектори тяги
    # Мотор 1 (передній лівий) - слабкий
    m1x, m1y = cx - 110, cy - 80
    body += circle(m1x, m1y, 18, fill="#ffffff", stroke=LINE, sw=1.5)
    body += text(m1x, m1y + 4, "M1", size=10, bold=True)
    body += arrow(m1x, m1y - 20, m1x, m1y - 50, color=LINE, sw=2)
    body += text(m1x - 8, m1y - 56, "T₁=25%", size=11, color=MUTED, anchor="end")

    # Мотор 4 (передній правий) - слабкий
    m4x, m4y = cx + 110, cy - 80
    body += circle(m4x, m4y, 18, fill="#ffffff", stroke=LINE, sw=1.5)
    body += text(m4x, m4y + 4, "M4", size=10, bold=True)
    body += arrow(m4x, m4y - 20, m4x, m4y - 50, color=LINE, sw=2)
    body += text(m4x + 8, m4y - 56, "T₄=25%", size=11, color=MUTED, anchor="start")

    # Мотор 2 (задній лівий) - перевантажений
    m2x, m2y = cx - 110, cy + 80
    body += circle(m2x, m2y, 18, fill="#fee2e2", stroke=POS, sw=2)
    body += text(m2x, m2y + 4, "M2", size=10, color=POS, bold=True)
    body += arrow(m2x, m2y - 20, m2x, m2y - 95, color=POS, sw=3.5)
    body += text(m2x - 8, m2y - 100, "T₂=75%", size=11, color=POS, bold=True, anchor="end")

    # Мотор 3 (задній правий) - перевантажений
    m3x, m3y = cx + 110, cy + 80
    body += circle(m3x, m3y, 18, fill="#fee2e2", stroke=POS, sw=2)
    body += text(m3x, m3y + 4, "M3", size=10, color=POS, bold=True)
    body += arrow(m3x, m3y - 20, m3x, m3y - 95, color=POS, sw=3.5)
    body += text(m3x + 8, m3y - 100, "T₃=75%", size=11, color=POS, bold=True, anchor="start")

    # Підпис балансу внизу
    body += text(230, 345, "Баланс моментів: T_задні · L_задні = T_передні · L_передні", size=11, color=INK)
    body += text(230, 362, "Постійний перекошувальний момент: M_offset = Δr × (m · g)", size=10, color=MUTED)

    # Права панель — Втрата запасу динамічного керування
    body += rect(460, 20, 360, 360, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(640, 48, "Втрата динамічного запасу (Headroom)", size=15, bold=True)

    # Графік смуг тяги для ідеального та зміщеного випадку
    # Ідеальний дрон
    body += text(540, 80, "Ідеальний баланс (CG = CoT)", size=12, bold=True)
    body += rect(500, 95, 80, 220, fill="#ffffff", stroke="#9ca3af", sw=1.5)
    # 0% - 100%
    body += rect(500, 195, 80, 20, fill="#e0e7ff", stroke=NEG, sw=1.5)
    body += text(540, 209, "Зависання 50%", size=10, color=NEG, bold=True)
    body += arrow(540, 190, 540, 100, color=FIELD, sw=2)
    body += text(540, 145, "+50% вгору", size=10, color=FIELD, bold=True)
    body += arrow(540, 220, 540, 310, color=FIELD, sw=2)
    body += text(540, 270, "−50% вниз", size=10, color=FIELD, bold=True)

    # Зміщений дрон (Задній мотор)
    body += text(720, 80, "Зсув CG (Задній мотор)", size=12, color=POS, bold=True)
    body += rect(680, 95, 80, 220, fill="#ffffff", stroke="#9ca3af", sw=1.5)
    # Насичення 75%
    body += rect(680, 140, 80, 20, fill="#fee2e2", stroke=POS, sw=1.5)
    body += text(720, 154, "Зависання 75%", size=10, color=POS, bold=True)
    body += arrow(720, 135, 720, 100, color=POS, sw=2)
    body += text(720, 120, "Лише +25%!", size=10, color=POS, bold=True)
    body += arrow(720, 165, 720, 310, color=MUTED, sw=1.5)
    body += text(720, 240, "−75% вниз", size=10, color=MUTED)

    # Пояснення деградації
    body += rect(480, 325, 320, 42, fill="#fef2f2", stroke=POS, sw=1, rx=4)
    body += text(640, 342, "Запас на парирування збурень падає у 2 рази", size=11, color=POS, bold=True)
    body += text(640, 358, "Швидке насичення (100%) викликає крен/перекид", size=10, color=MUTED)

    return render(os.path.join(OUT, "cg-cot-offset.svg"), W, H, body)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Рухома маса: підвіс, маніпулятор та реактивні моменти
# ════════════════════════════════════════════════════════════════════════════
def fig_moving_mass_dynamics():
    W, H = 840, 380
    body = ""

    # Ліва секція — Кінематика підвісу та реактивний момент
    body += rect(20, 20, 390, 340, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(215, 48, "Кінематика маніпулятора та реакція", size=15, bold=True)

    # Дрон база
    bx, by = 215, 120
    body += rect(bx - 90, by - 15, 180, 30, fill="#e5e7eb", stroke=LINE, sw=2, rx=4)
    body += text(bx, by + 5, "Корпус апарата (m_frame)", size=11, bold=True)

    # Шарнір підвісу
    hx, hy = bx, by + 15
    body += circle(hx, hy, 8, fill="#9ca3af", stroke=LINE, sw=1.5)

    # Рука маніпулятора у відхиленому стані
    arm_len = 100
    angle_deg = 35
    rad = math.radians(angle_deg)
    px = hx + arm_len * math.sin(rad)
    py = hy + arm_len * math.cos(rad)

    # Промінь руки
    body += line(hx, hy, px, py, color=LINE, sw=4)
    # Маса вантажу на кінці
    body += circle(px, py, 22, fill="#fde68a", stroke="#d97706", sw=2)
    body += text(px, py + 4, "m_p", size=12, bold=True, color="#92400e")

    # Стрілка кутового прискорення руки
    body += arrow(hx + 35, hy + 50, hx + 55, hy + 40, color=NEG, sw=2)
    body += text(hx + 75, hy + 48, "+α_arm", size=11, color=NEG, bold=True)

    # Стрілка реактивного моменту на корпус
    body += arrow(bx - 30, by - 30, bx - 60, by - 30, color=POS, sw=2.5)
    body += text(bx - 45, by - 40, "M_react = −I_arm · α_arm", size=11, color=POS, bold=True)

    # Коріолісові сили
    body += text(215, 275, "Динамічні збурення при русі:", size=12, bold=True)
    body += text(215, 298, "• Реактивний крутний момент: M_react = −I_p · α_p", size=11, color=INK)
    body += text(215, 318, "• Коріолісові сили: F_cor = 2 · m_p · (ω_body × v_rel)", size=11, color=INK)
    body += text(215, 338, "• Зсув миттєвого центру мас: r_cg(t)", size=11, color=POS)

    # Права секція — Зміна тензора інерції та перехресний зв'язок осей
    body += rect(430, 20, 390, 340, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(625, 48, "Деформація тензора інерції I(t)", size=15, bold=True)

    # Відображення матриці інерції
    body += rect(460, 75, 330, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6)
    body += text(485, 105, "I(t) =", size=14, bold=True)
    body += text(565, 105, "I_xx(t)   −I_xy(t)   −I_xz(t)", size=12, bold=True, color=POS)
    body += text(565, 130, "−I_yx(t)   I_yy(t)   −I_yz(t)", size=12, bold=True, color=POS)
    body += text(565, 155, "−I_zx(t)   −I_zy(t)   I_zz(t)", size=12, bold=True, color=POS)

    # Блоки наслідків для PID
    body += rect(450, 205, 350, 65, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=6)
    body += text(625, 225, "1. Поява недіагональних членів (I_xy, I_xz ≠ 0)", size=11, bold=True, color=INK)
    body += text(625, 245, "Обертання по крену генерує паразитний тангаж і рискання", size=10, color=MUTED)
    body += text(625, 260, "(динамічне перехресне зв'язування каналів)", size=10, color=MUTED)

    body += rect(450, 280, 350, 65, fill="#fef2f2", stroke=POS, sw=1, rx=6)
    body += text(625, 300, "2. Зміна власної частоти контуру керування", size=11, bold=True, color=POS)
    body += text(625, 320, "При висуванні руки I_yy зростає в 2–3 рази →", size=10, color=INK)
    body += text(625, 335, "PID-регулятор втрачає жорсткість (перерегулювання)", size=10, color=POS)

    return render(os.path.join(OUT, "moving-mass-dynamics.svg"), W, H, body)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Плескання рідини (Liquid Sloshing) та маятниковий еквівалент
# ════════════════════════════════════════════════════════════════════════════
def fig_liquid_sloshing_modes():
    W, H = 840, 390
    body = ""

    # Ліва колонка — Фізичний бак без перегородок (Вільна поверхня)
    body += rect(20, 20, 255, 350, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(147, 48, "1. Вільна поверхня", size=14, bold=True)
    body += text(147, 66, "(Бак без перегородок)", size=11, color=MUTED)

    # Контур бака
    tx, ty, tw, th = 55, 85, 185, 150
    body += rect(tx, ty, tw, th, fill="#f1f5f9", stroke=LINE, sw=2, rx=8)

    # Хвиля рідини при нахилі/прискоренні
    # Полігон води з похилою синусоїдною поверхнею
    body += ('<path d="M %d %d Q %d %d %d %d L %d %d L %d %d Z" '
             'fill="#93c5fd" stroke="#2563eb" stroke-width="2"/>' %
             (tx, ty + 100, tx + tw/2, ty + 55, tx + tw, ty + 30, tx + tw, ty + th, tx, ty + th))

    # Зміщений центр мас рідини CG_fluid
    body += circle(tx + 130, ty + 95, 6, fill=POS, stroke="#ffffff", sw=1.5)
    body += text(tx + 130, ty + 118, "CG_fluid", size=10, color=POS, bold=True)

    # Стрілка динамічної хвилі
    body += arrow(tx + 30, ty + 115, tx + 140, ty + 45, color=NEG, sw=2)
    body += text(tx + 85, ty + 65, "Перетікання", size=10, color=NEG, bold=True)

    body += text(147, 260, "Хвиля відстає за фазою", size=11, bold=True, color=POS)
    body += text(147, 278, "Фазовий зсув: Δφ ≈ 90°–180°", size=10, color=INK)
    body += text(147, 296, "Резонансна частота:", size=10, color=MUTED)
    body += text(147, 314, "ω_s = √( (g/R) · tanh(h/R) )", size=10, bold=True, color=INK)
    body += text(147, 335, "Ризик: розгойдування (PIO)", size=10, color=POS, bold=True)

    # Середня колонка — Механічний маятниковий еквівалент
    body += rect(290, 20, 260, 350, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(420, 48, "2. Маятниковий еквівалент", size=14, bold=True)
    body += text(420, 66, "(Модель для симуляції)", size=11, color=MUTED)

    # Бак пунктиром
    body += rect(325, 85, 190, 150, fill="#ffffff", stroke="#9ca3af", sw=1.5, rx=8)

    # Фіксована маса рідини m0
    body += circle(420, 185, 14, fill="#cbd5e1", stroke=LINE, sw=1.5)
    body += text(420, 189, "m₀", size=11, bold=True)
    body += text(420, 210, "Нерухома маса", size=9, color=MUTED)

    # Шарнір підвісу маятника
    hx, hy = 420, 95
    body += circle(hx, hy, 5, fill=LINE, stroke="#ffffff", sw=1)
    body += text(hx + 15, hy + 4, "Шарнір h_p", size=9, color=MUTED)

    # Маятник коливної маси m1
    pend_x = hx + 50
    pend_y = hy + 65
    body += line(hx, hy, pend_x, pend_y, color=POS, sw=2)
    # Демпфер поруч
    body += line(hx - 20, hy + 30, pend_x - 20, pend_y, color=NEG, sw=1.5, dash="2 2")
    body += text(365, hy + 40, "c_slosh", size=9, color=NEG)

    body += circle(pend_x, pend_y, 14, fill="#fca5a5", stroke=POS, sw=1.5)
    body += text(pend_x, pend_y + 4, "m₁", size=11, bold=True, color=POS)
    body += text(pend_x + 22, pend_y + 4, "L_p", size=10, color=POS)

    body += text(420, 260, "Параметри еквівалента:", size=11, bold=True, color=INK)
    body += text(420, 280, "• m₁: коливна частка рідини", size=10, color=INK)
    body += text(420, 298, "• m₀: жорстко зв'язана частка", size=10, color=INK)
    body += text(420, 316, "• L_p: довжина еквівалента", size=10, color=INK)
    body += text(420, 335, "• c_slosh: гідродинамічне тертя", size=10, color=NEG)

    # Права колонка — Механічне гасіння (Перегородки / Baffles)
    body += rect(565, 20, 255, 350, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(692, 48, "3. Бак із хвилерізами", size=14, bold=True)
    body += text(692, 66, "(Гасіння коливань)", size=11, color=FIELD)

    # Контур бака з перегородками
    bx2, by2, bw2, bh2 = 600, 85, 185, 150
    body += rect(bx2, by2, bw2, bh2, fill="#f1f5f9", stroke=LINE, sw=2, rx=8)

    # Рівень рідини (розбитий на відсіки)
    body += rect(bx2, by2 + 65, bw2, bh2 - 65, fill="#bfdbfe", stroke="#3b82f6", sw=1, rx=4)

    # Перфоровані перегородки (Baffles)
    b1_x = bx2 + 60
    b2_x = bx2 + 125
    body += line(b1_x, by2 + 10, b1_x, by2 + bh2, color=LINE, sw=3)
    body += line(b2_x, by2 + 10, b2_x, by2 + bh2, color=LINE, sw=3)
    # Отвори перфорації
    for oy in [by2 + 80, by2 + 105, by2 + 130]:
        body += circle(b1_x, oy, 4, fill="#ffffff", stroke=LINE, sw=1)
        body += circle(b2_x, oy, 4, fill="#ffffff", stroke=LINE, sw=1)

    body += text(bx2 + 92, by2 + 40, "Перегородки", size=10, bold=True, color=INK)

    body += text(692, 260, "Результат захисту:", size=11, bold=True, color=FIELD)
    body += text(692, 280, "• Зсув частоти у ВЧ-зону (>10 Гц)", size=10, color=INK)
    body += text(692, 298, "• Дроблення макрохвилі на вихори", size=10, color=INK)
    body += text(692, 316, "• Демпфування зростає у 5–8 разів", size=10, color=FIELD, bold=True)
    body += text(692, 335, "• Стійкість польоту збережено", size=10, color=FIELD)

    return render(os.path.join(OUT, "liquid-sloshing-modes.svg"), W, H, body)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Архітектура компенсації: оцінювач CG та динамічний мікшер
# ════════════════════════════════════════════════════════════════════════════
def fig_adaptive_mixer_estimator():
    W, H = 840, 360
    body = ""

    # Загальна підкладка
    body += rect(15, 15, 810, 330, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8)
    body += text(420, 42, "Контур адаптивної компенсації зміщення центру мас", size=16, bold=True)

    # 1. Сенсорний вхід
    body += rect(35, 75, 155, 105, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6)
    body += text(112, 98, "Джерела даних", size=12, bold=True, color=INK)
    body += text(112, 120, "• IMU (акселерометр)", size=10, color=MUTED)
    body += text(112, 138, "• Енкодери підвісу (θ_g)", size=10, color=MUTED)
    body += text(112, 156, "• Струм/оберти ESC", size=10, color=MUTED)

    # Стрілка до оцінювача
    body += arrow(190, 127, 235, 127, color=LINE, sw=2)

    # 2. Блок оцінювача CG (Center of Mass Estimator / EKF)
    body += rect(235, 75, 175, 105, fill="#eff6ff", stroke=NEG, sw=2, rx=6)
    body += text(322, 98, "Оцінювач CG (EKF)", size=13, bold=True, color=NEG)
    body += text(322, 122, "Низькочастотний", size=10, color=INK)
    body += text(322, 138, "аналіз I-терму моторів", size=10, color=INK)
    body += text(322, 158, "Вихід: вектор Δr_cg(t)", size=10, bold=True, color=POS)

    # Стрілка до динамічного мікшера
    body += arrow(410, 127, 465, 127, color=POS, sw=2.5)
    body += text(437, 117, "Δr_cg", size=11, bold=True, color=POS)

    # 3. Блок прямого зв'язку (Feedforward)
    body += rect(235, 215, 175, 95, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6)
    body += text(322, 238, "Прямий зв'язок (FF)", size=12, bold=True, color="#854d0e")
    body += text(322, 260, "M_ff = −I_g · α_g", size=11, bold=True, color=POS)
    body += text(322, 282, "Швидка реакція на рух", size=10, color=MUTED)

    # Стрілка з сенсорів до FF
    body += ('<path d="M 112 180 L 112 262 L 235 262" fill="none" stroke="#94a3b8" '
             'stroke-width="1.5" stroke-dasharray="3 3" marker-end="url(#arrow)"/>')

    # Стрілка від FF до суматора
    body += ('<path d="M 410 262 L 555 262 L 555 200" fill="none" stroke="#ca8a04" '
             'stroke-width="2" marker-end="url(#arrow)"/>')
    body += text(500, 252, "+M_ff (момент)", size=10, bold=True, color="#854d0e")

    # 4. Динамічний мікшер (Dynamic Mixer Matrix)
    body += rect(465, 75, 180, 105, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6)
    body += text(555, 98, "Динамічний мікшер", size=13, bold=True, color=FIELD)
    body += text(555, 122, "l_i(t) = p_i − Δr_cg(t)", size=11, bold=True, color=INK)
    body += text(555, 142, "Матриця B(r_cg)⁻¹", size=10, color=MUTED)
    body += text(555, 160, "Анти-насичення осей", size=10, color=MUTED)

    # Стрілка до виходу на мотори
    body += arrow(645, 127, 690, 127, color=FIELD, sw=2.5)

    # 5. Виконавці ESC / Мотори
    body += rect(690, 75, 115, 105, fill="#ffffff", stroke=LINE, sw=1.5, rx=6)
    body += text(747, 98, "Виходи ESC", size=12, bold=True, color=INK)
    body += text(747, 122, "Мотор 1..4", size=11, color=INK)
    body += text(747, 142, "DShot600", size=10, color=MUTED)
    body += text(747, 160, "Лінійна тяга", size=10, color=FIELD, bold=True)

    # Підсумковий статус внизу
    body += rect(35, 305, 770, 30, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4)
    body += text(420, 325, "Результат: ортогональне керування, усунення перерегулювання й захист від перекидання", size=11, color=INK, bold=True)

    return render(os.path.join(OUT, "adaptive-mixer-estimator.svg"), W, H, body)


if __name__ == "__main__":
    fig_cg_cot_offset()
    fig_moving_mass_dynamics()
    fig_liquid_sloshing_modes()
    fig_adaptive_mixer_estimator()
    print("All figures generated successfully.")
