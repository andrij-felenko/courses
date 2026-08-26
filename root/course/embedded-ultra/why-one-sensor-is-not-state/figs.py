# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. apparent-gravity-flight: Вектор питомої сили в польоті ──────────────────
def fig_apparent_gravity():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 32, "Питома сила акселерометра в польоті: статичне зависання проти лінійного прискорення", size=15, color=INK, bold=True))

    # Ліва колонка: Статичне зависання
    lx, ly, lw, lh = 50, 60, 410, 390
    p.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Статика / Рівномірний рух (a = 0)", size=14, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, ly + 46, "Акселерометр вимірює реакцію опори f = -g", size=11, color=MUTED))

    # Схема дрона в статиці
    dcx, dcy = lx + lw / 2, ly + 150
    # Пропелери та промені
    p.append(line(dcx - 90, dcy, dcx + 90, dcy, color=LINE, sw=3))
    p.append(rect(dcx - 30, dcy - 15, 60, 30, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    p.append(text(dcx, dcy + 4, "IMU", size=11, color=INK, bold=True))
    p.append(line(dcx - 90, dcy - 12, dcx - 50, dcy - 12, color=FIELD, sw=2))
    p.append(line(dcx + 50, dcy - 12, dcx + 90, dcy - 12, color=FIELD, sw=2))

    # Вектори в статиці
    # Гравітація вниз
    p.append(arrow(dcx, dcy + 15, dcx, dcy + 105, color=NEG, sw=2.5))
    p.append(text(dcx + 12, dcy + 65, "g (9.81 м/с²)", size=12, color=NEG, bold=True, anchor="start"))
    # Питома сила вгору (реакція опори)
    p.append(arrow(dcx, dcy - 15, dcx, dcy - 95, color=FIELD, sw=2.5))
    p.append(text(dcx + 12, dcy - 55, "f_meas = -g (вгору)", size=12, color=FIELD, bold=True, anchor="start"))

    # Пояснення статики
    p.append(rect(lx + 20, ly + 270, lw - 40, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(lx + 32, ly + 295, "Розрахунок кута нахилу (Pitch/Roll):", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(lx + 32, ly + 318, "• a_x = 0, a_y = 0, a_z = +1.0 g", size=11, color=FIELD, anchor="start"))
    p.append(text(lx + 32, ly + 338, "• pitch = atan2(-a_x, a_z) = 0.0°", size=11, color=INK, anchor="start"))
    p.append(text(lx + 32, ly + 358, "✓ Оцінка кута абсолютно точна", size=11, color=FIELD, bold=True, anchor="start"))

    # Права колонка: Лінійне прискорення в польоті
    rx_col, ry_col, rw_col, rh_col = 500, 60, 410, 390
    p.append(rect(rx_col, ry_col, rw_col, rh_col, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    p.append(text(rx_col + rw_col / 2, ry_col + 28, "Динаміка: Розгін уперед (a_lin = 5 м/с²)", size=14, color=POS, bold=True))
    p.append(text(rx_col + rw_col / 2, ry_col + 46, "Питома сила f = a_lin - g спотворює вертикаль", size=11, color=MUTED))

    # Схема дрона при розгоні
    rcx, rcy = rx_col + rw_col / 2 - 30, ry_col + 150
    # Пропелери та промені
    p.append(line(rcx - 90, rcy, rcx + 90, rcy, color=LINE, sw=3))
    p.append(rect(rcx - 30, rcy - 15, 60, 30, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    p.append(text(rcx, rcy + 4, "IMU", size=11, color=INK, bold=True))
    p.append(line(rcx - 90, rcy - 12, rcx - 50, rcy - 12, color=POS, sw=2))
    p.append(line(rcx + 50, rcy - 12, rcx + 90, rcy - 12, color=POS, sw=2))

    # Вектори в динаміці
    # 1. Прискорення вперед
    p.append(arrow(rcx + 30, rcy, rcx + 110, rcy, color=POS, sw=2.2))
    p.append(text(rcx + 70, rcy - 10, "a_lin (5 м/с²)", size=11, color=POS, bold=True, anchor="middle"))

    # 2. Реакція опори -g вгору
    p.append(line(rcx, rcy, rcx, rcy - 75, color=MUTED, sw=1.5, dash="4,4"))
    p.append(text(rcx - 10, rcy - 45, "-g", size=10.5, color=MUTED, anchor="end"))

    # 3. Результуючий вектор f_meas (нахилений назад)
    p.append(arrow(rcx, rcy, rcx + 80, rcy - 75, color=POS, sw=2.8))
    p.append(text(rcx + 88, rcy - 82, "f_meas (вектор питомої сили)", size=12, color=POS, bold=True, anchor="start"))

    # Дуга кутової помилки
    p.append(text(rcx + 35, rcy - 50, "θ = 27.0°", size=11, color=POS, bold=True))

    # Пояснення помилки
    p.append(rect(rx_col + 20, ry_col + 270, rw_col - 40, 100, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(rx_col + 32, ly + 295, "Хибний розрахунок кута автопілотом:", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(rx_col + 32, ly + 318, "• a_x = +5.0 м/с², a_z = +9.81 м/с²", size=11, color=INK, anchor="start"))
    p.append(text(rx_col + 32, ly + 338, "• pitch = atan2(-5.0, 9.81) = -27.0° (хибний тангаж)", size=11, color=POS, anchor="start"))
    p.append(text(rx_col + 32, ly + 358, "✗ Давач «бачить» нахил, якого фізично не існує", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "apparent-gravity-flight.svg"), W, H, *p,
           title="Питома сила акселерометра в польоті")


# ── 2. sensor-spectral-complementarity: Спектральна комплементарність ─────────
def fig_spectral_complementarity():
    W, H = 960, 500
    p = []

    p.append(text(W / 2, 30, "Спектральний дуалізм шумів IMU: принцип комплементарного розділення частот", size=15, color=INK, bold=True))

    # Рамка графіка
    gx, gy, gw, gh = 80, 60, 800, 330
    p.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # Осі
    p.append(arrow(gx + 60, gy + gh - 35, gx + gw - 40, gy + gh - 35, color=LINE, sw=2))
    p.append(text(gx + gw - 35, gy + gh - 30, "Частота f (Гц) →", size=12, color=INK, bold=True, anchor="start"))

    p.append(arrow(gx + 60, gy + gh - 35, gx + 60, gy + 25, color=LINE, sw=2))
    p.append(text(gx + 55, gy + 20, "Спектральна густина похибки / Довіра до сигналу", size=12, color=INK, bold=True, anchor="start"))

    # Вертикальна лінія частоти зрізу f_c
    fc_x = gx + 400
    p.append(line(fc_x, gy + 35, fc_x, gy + gh - 35, color=FIELD, sw=2, dash="5,5"))
    p.append(rect(fc_x - 75, gy + 40, 150, 26, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(fc_x, gy + 57, "f_c = 1 / (2π τ) ≈ 0.5 Гц", size=11, color=FIELD, bold=True))

    # Зона низьких частот (під віссю)
    p.append(rect(gx + 65, gy + gh - 30, fc_x - gx - 70, 20, fill="#e0f2fe", stroke="none"))
    p.append(text((gx + 65 + fc_x) / 2, gy + gh - 16, "Низькі частоти (повільні зміни, DC)", size=10, color=NEG, bold=True))

    # Зона високих частот (під віссю)
    p.append(rect(fc_x + 5, gy + gh - 30, gx + gw - 45 - fc_x, 20, fill="#fef3c7", stroke="none"))
    p.append(text((fc_x + gx + gw - 40) / 2, gy + gh - 16, "Високі частоти (динаміка, вібрації)", size=10, color="#d97706", bold=True))

    # Крива 1: Похибка гіроскопа
    p.append(line(gx + 70, gy + 65, gx + 200, gy + 90, color=POS, sw=3))
    p.append(line(gx + 200, gy + 90, fc_x, gy + 160, color=POS, sw=3))
    p.append(line(fc_x, gy + 160, gx + 600, gy + 240, color=POS, sw=3))
    p.append(line(gx + 600, gy + 240, gx + gw - 60, gy + 260, color=POS, sw=3))

    p.append(rect(gx + 90, gy + 75, 230, 46, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(gx + 100, gy + 94, "Похибка гіроскопа (дрейф bias)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(gx + 100, gy + 110, "Інтегрування накопичує похибку на DC", size=9.5, color=INK, anchor="start"))

    # Крива 2: Похибка акселерометра
    p.append(line(gx + 70, gy + 260, gx + 200, gy + 245, color=NEG, sw=3))
    p.append(line(gx + 200, gy + 245, fc_x, gy + 160, color=NEG, sw=3))
    p.append(line(fc_x, gy + 160, gx + 600, gy + 90, color=NEG, sw=3))
    p.append(line(gx + 600, gy + 90, gx + gw - 60, gy + 65, color=NEG, sw=3))

    p.append(rect(gx + gw - 330, gy + 75, 250, 46, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(gx + gw - 320, gy + 94, "Похибка акселерометра (шум/динаміка)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(gx + gw - 320, gy + 110, "Вібрації та лінійні прискорення спотворюють f", size=9.5, color=INK, anchor="start"))

    # Комплементарний висновок внизу (окремий блок нижче графіка)
    p.append(rect(gx, 410, gw, 65, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(gx + gw / 2, 435, "Злиття: HPF(Гіроскоп) + LPF(Акселерометр) = 1.0 (Ідеальний стан на всіх частотах)", size=12, color=FIELD, bold=True))
    p.append(text(gx + gw / 2, 458, "Гіроскоп відповідає за швидкі маневри; акселерометр утримує довготривалу горизонталь", size=10.5, color=INK))

    render(os.path.join(OUT, "sensor-spectral-complementarity.svg"), W, H, *p,
           title="Спектральна комплементарність сигналів IMU")


# ── 3. magnetic-distortion-sources: Джерела магнітних спотворень ─────────────
def fig_magnetic_distortions():
    W, H = 960, 460
    p = []

    p.append(text(W / 2, 30, "Магнітні збурення на борту: Hard-Iron, Soft-Iron та струми силових ліній", size=15, color=INK, bold=True))

    # Блок 1: Hard-Iron (Тверде залізо)
    bx1, by1, bw, bh = 40, 60, 275, 375
    p.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx1 + bw / 2, by1 + 24, "Hard-Iron (Тверде залізо)", size=13, color=INK, bold=True))
    p.append(text(bx1 + bw / 2, by1 + 42, "Постійне зміщення центру сфери", size=10.5, color=MUTED))

    # Схема Hard Iron
    cx1, cy1 = bx1 + bw / 2, by1 + 140
    p.append('<circle cx="%.1f" cy="%.1f" r="55" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx1, cy1)) # Ідеальне коло
    p.append(circle(cx1 + 24, cy1 - 18, 55, fill="#fee2e2", stroke=POS, sw=2)) # Зсунуте коло
    p.append(line(cx1, cy1, cx1 + 24, cy1 - 18, color=POS, sw=2))
    p.append(circle(cx1 + 24, cy1 - 18, 3, fill=POS, stroke=POS))
    p.append(text(cx1 + 32, cy1 - 24, "V_bias", size=10.5, color=POS, bold=True))

    # Опис Hard Iron
    p.append(rect(bx1 + 12, by1 + 225, bw - 24, 135, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(bx1 + 20, by1 + 245, "Джерело:", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(bx1 + 20, by1 + 263, "• Постійні магніти моторів", size=10, color=INK, anchor="start"))
    p.append(text(bx1 + 20, by1 + 280, "• Намагнічені сталеві гвинти", size=10, color=INK, anchor="start"))
    p.append(text(bx1 + 20, by1 + 297, "• Зумер / динамік", size=10, color=INK, anchor="start"))
    p.append(text(bx1 + 20, by1 + 318, "Математична корекція:", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx1 + 20, by1 + 338, "B_cal = B_raw - V_bias", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Блок 2: Soft-Iron (М'яке залізо)
    bx2, by2 = 342, 60
    p.append(rect(bx2, by2, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx2 + bw / 2, by2 + 24, "Soft-Iron (М'яке залізо)", size=13, color=INK, bold=True))
    p.append(text(bx2 + bw / 2, by2 + 42, "Деформація сфери в еліпсоїд", size=10.5, color=MUTED))

    # Схема Soft Iron
    cx2, cy2 = bx2 + bw / 2, by2 + 140
    p.append('<circle cx="%.1f" cy="%.1f" r="55" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx2, cy2)) # Ідеальне коло
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="68" ry="38" transform="rotate(-30 %.1f %.1f)" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>' % (cx2, cy2, cx2, cy2))
    p.append(circle(cx2, cy2, 3, fill="#d97706", stroke="#d97706"))

    # Опис Soft Iron
    p.append(rect(bx2 + 12, by2 + 225, bw - 24, 135, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    p.append(text(bx2 + 20, by2 + 245, "Джерело:", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(bx2 + 20, by2 + 263, "• Феромагнітні деталі рами", size=10, color=INK, anchor="start"))
    p.append(text(bx2 + 20, by2 + 280, "• Нікелеві виводи акумулятора", size=10, color=INK, anchor="start"))
    p.append(text(bx2 + 20, by2 + 297, "• Екрани роз'ємів і плат", size=10, color=INK, anchor="start"))
    p.append(text(bx2 + 20, by2 + 318, "Математична корекція:", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx2 + 20, by2 + 338, "B_cal = W_matrix · (B_raw - V)", size=10, color=FIELD, bold=True, anchor="start"))

    # Блок 3: Динамічні струми силових ліній (ESC / BLDC)
    bx3, by3 = 644, 60
    p.append(rect(bx3, by3, bw, bh, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    p.append(text(bx3 + bw / 2, by3 + 24, "Динамічний струм (ESC / Мотори)", size=13, color=POS, bold=True))
    p.append(text(bx3 + bw / 2, by3 + 42, "Поле струму перекриває геомагнітне", size=10.5, color=MUTED))

    # Схема струму та поля Біо-Савара
    cx3, cy3 = bx3 + bw / 2, by3 + 140
    # Провідник зі струмом
    p.append(circle(cx3 - 35, cy3, 14, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(cx3 - 35, cy3 + 4, "I", size=12, color=POS, bold=True))
    p.append(text(cx3 - 35, cy3 - 20, "40–100 А", size=10, color=POS, bold=True))

    # Магнітні силові лінії навколо дроту
    p.append('<circle cx="%.1f" cy="%.1f" r="40" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (cx3 - 35, cy3, POS))
    p.append(arrow(cx3 - 35 + 40, cy3 - 5, cx3 - 35 + 40, cy3 + 15, color=POS, sw=2))

    # Вектори на датчику
    p.append(rect(cx3 + 25, cy3 - 15, 45, 30, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=3))
    p.append(text(cx3 + 47, cy3 + 4, "Mag", size=10, color=INK, bold=True))

    p.append(arrow(cx3 + 47, cy3 + 15, cx3 + 47, cy3 + 48, color=POS, sw=2.5))
    p.append(text(cx3 + 55, cy3 + 35, "B_I = 160 мкТл", size=9.5, color=POS, bold=True, anchor="start"))

    p.append(arrow(cx3 + 47, cy3 - 15, cx3 + 47, cy3 - 38, color=FIELD, sw=2))
    p.append(text(cx3 + 55, cy3 - 25, "B_землі = 45 мкТл", size=9.5, color=FIELD, bold=True, anchor="start"))

    # Опис динамічного струму
    p.append(rect(bx3 + 12, by3 + 225, bw - 24, 135, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(bx3 + 20, by3 + 245, "Наслідок для польоту:", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(bx3 + 20, by3 + 263, "• B_струму в 3–5 разів > B_землі", size=10, color=POS, anchor="start"))
    p.append(text(bx3 + 20, by3 + 280, "• При дачі газу курс стрибає на 90°", size=10, color=POS, anchor="start"))
    p.append(text(bx3 + 20, by3 + 297, "• Автопілот входить у розкачку курсу", size=10, color=POS, anchor="start"))
    p.append(text(bx3 + 20, by3 + 318, "Рішення: виніс на щоглу / EKF", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx3 + 20, by3 + 338, "та динамічна компенсація I·k", size=10, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "magnetic-distortion-sources.svg"), W, H, *p,
           title="Джерела магнітних спотворень на борту")


# ── 4. sensor-fusion-architecture: Архітектура оцінювача стану IMU ───────────
def fig_fusion_architecture():
    W, H = 960, 500
    p = []

    p.append(text(W / 2, 30, "Архітектура орієнтаційного фільтра IMU: замкнений контур злиття Махоні / EKF", size=15, color=INK, bold=True))

    # Ліва колонка: Давачі
    sx, sy, sw, sh = 40, 65, 160, 400
    p.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(sx + sw / 2, sy + 24, "Первинні давачі", size=13, color=INK, bold=True))

    sensors = [
        ("Гіроскоп (ω)", "3-осьова кутова швидкість [рад/с]", "#ede9fe", "#7c3aed", 80),
        ("Акселерометр (a)", "3-осьова питома сила [g / м/с²]", "#e0f2fe", NEG, 80),
        ("Магнітометр (m)", "3-осьовий вектор поля [мкТл]", "#fef3c7", "#d97706", 80),
        ("Барометр / GNSS", "Висота й позиція (для EKF)", "#f1f5f9", MUTED, 65),
    ]
    cur_y = sy + 40
    for title_s, sub_s, fill_c, strk_c, bh in sensors:
        p.append(rect(sx + 10, cur_y, sw - 20, bh, fill=fill_c, stroke=strk_c, sw=1.2, rx=5))
        p.append(text(sx + sw / 2, cur_y + 22, title_s, size=11.5, color=strk_c, bold=True))
        p.append(text(sx + sw / 2, cur_y + 42, sub_s, size=9.5, color=INK))
        cur_y += bh + 12

    # Центральна секція: Контур фільтра Махоні
    cx, cy, cw, ch = 240, 65, 460, 400
    p.append(rect(cx, cy, cw, ch, fill="#ffffff", stroke=FIELD, sw=2, rx=8))
    p.append(text(cx + cw / 2, cy + 24, "Орієнтаційний фільтр (Mahony Attitude Observer)", size=14, color=FIELD, bold=True))

    # Блоки всередині фільтра
    # Блок 1: Розрахунок похибки reference vs measured
    p.append(rect(cx + 20, cy + 45, cw - 40, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(cx + cw / 2, cy + 68, "1. Розрахунок вектора просторової похибки e", size=12, color=FIELD, bold=True))
    p.append(text(cx + cw / 2, cy + 88, "e = (a_meas × v_gravity_body) + (m_meas × v_mag_body)", size=11, color=INK, bold=True))
    p.append(text(cx + cw / 2, cy + 106, "Векторний добуток виміряного та очікованого векторів", size=10, color=MUTED))

    # Блок 2: ПІ-корекція гіроскопа
    p.append(rect(cx + 20, cy + 135, cw - 40, 80, fill="#ede9fe", stroke="#7c3aed", sw=1.2, rx=6))
    p.append(text(cx + cw / 2, cy + 158, "2. ПІ-компенсація зміщення гіроскопа (Bias Tracking)", size=12, color="#7c3aed", bold=True))
    p.append(text(cx + cw / 2, cy + 178, "b_gyro += Ki · e · dt   (інтегратор накопичує дрейф нуля)", size=10.5, color=INK))
    p.append(text(cx + cw / 2, cy + 198, "ω_corr = ω_raw - b_gyro + Kp · e   (виправлена кутова швидкість)", size=10.5, color=INK, bold=True))

    # Блок 3: Кватерніонна кінематика
    p.append(rect(cx + 20, cy + 230, cw - 40, 80, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(cx + cw / 2, cy + 253, "3. Чисельне інтегрування кватерніона орієнтації", size=12, color="#d97706", bold=True))
    p.append(text(cx + cw / 2, cy + 273, "q_dot = 0.5 · q ⊗ [0, ω_corr]   →   q_new = q + q_dot · dt", size=10.5, color=INK, bold=True))
    p.append(text(cx + cw / 2, cy + 293, "q = q / ||q||   (обов'язкова унітарна нормалізація)", size=10.5, color=INK))

    # Блок 4: Зворотний зв'язок очікуваних векторів
    p.append(rect(cx + 20, cy + 325, cw - 40, 60, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(cx + cw / 2, cy + 348, "4. Розрахунок очікуваних векторів у системі апарата", size=11.5, color=INK, bold=True))
    p.append(text(cx + cw / 2, cy + 368, "v_gravity_body = R(q)^T · [0, 0, 1]^T  →  передається у блок 1", size=10, color=MUTED))

    # Стрілки зліва направо
    # Гіроскоп -> Блок 2
    p.append(arrow(sx + sw - 10, sy + 75, cx + 20, cy + 175, color="#7c3aed", sw=2))
    # Акселерометр -> Блок 1
    p.append(arrow(sx + sw - 10, sy + 165, cx + 20, cy + 80, color=NEG, sw=2))
    # Магнітометр -> Блок 1
    p.append(arrow(sx + sw - 10, sy + 255, cx + 20, cy + 95, color="#d97706", sw=2))

    # Права колонка: Оцінений вектор стану
    ox, oy, ow, oh = 740, 65, 180, 400
    p.append(rect(ox, oy, ow, oh, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(ox + ow / 2, oy + 24, "Оцінений стан (State)", size=13, color=FIELD, bold=True))

    out_blocks = [
        ("Кватерніон q", "[q0, q1, q2, q3]\nБез Gimbal Lock", FIELD, 60),
        ("Кути Ейлера", "Roll, Pitch, Yaw\n(для телеметрії)", INK, 60),
        ("Кутова швидкість", "ω_corr (чиста від bias)\nдля ПІД-регулятора", "#7c3aed", 65),
        ("Оцінене зміщення", "b_gyro (компенсований\nдрейф нуля)", POS, 65),
    ]
    cur_oy = oy + 45
    for ot, od, col, obh in out_blocks:
        p.append(rect(ox + 10, cur_oy, ow - 20, obh, fill="#ffffff", stroke=col, sw=1.2, rx=5))
        p.append(text(ox + ow / 2, cur_oy + 20, ot, size=11, color=col, bold=True))
        lines = od.split("\n")
        for i, l in enumerate(lines):
            p.append(text(ox + ow / 2, cur_oy + 38 + i * 14, l, size=9.5, color=MUTED))
        cur_oy += obh + 10

    # Стрілка з фільтра у вихідний стан
    p.append(arrow(cx + cw - 20, cy + 270, ox + 10, oy + 75, color=FIELD, sw=2.5))
    p.append(arrow(cx + cw - 20, cy + 175, ox + 10, oy + 215, color="#7c3aed", sw=2))

    render(os.path.join(OUT, "sensor-fusion-architecture.svg"), W, H, *p,
           title="Архітектура орієнтаційного фільтра IMU")


def main():
    fig_apparent_gravity()
    fig_spectral_complementarity()
    fig_magnetic_distortions()
    fig_fusion_architecture()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
