# -*- coding: utf-8 -*-
"""Фігури до теми «Апарат у зборі» (vehicle-fully-assembled).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Взаємодія підсистем зібраного апарата та джерела системних конфліктів ──
def fig_subsystems_interaction():
    W, H = 1060, 520
    f = [text(W / 2, 28, "Системні зв'язки та фізичні взаємовпливи зібраного апарата", size=15, bold=True)]

    # 1. Силова підсистема (ліворуч зверху)
    px, py, pw, ph = 40, 60, 290, 190
    f.append(rect(px, py, pw, ph, fill="#fdf7f7", stroke=POS, sw=1.8, rx=8))
    f.append(text(px + pw / 2, py + 24, "Силова підсистема", size=13, bold=True, color=POS))
    f.append(text(px + 20, py + 55, "• LiPo батарея: струми 20–150 А", size=11, color=INK, anchor="start"))
    f.append(text(px + 20, py + 80, "• ESC регулятори: ШІМ комутація 24–48 кГц", size=11, color=INK, anchor="start"))
    f.append(text(px + 20, py + 105, "• Силові дроти: сильне магнітне поле B(I)", size=11, color=INK, anchor="start"))
    f.append(text(px + 20, py + 130, "• Пульсації напруги та просідання шини", size=11, color=INK, anchor="start"))
    f.append(text(px + 20, py + 155, "• Датчик струму й напруги (Power Module)", size=11, color=INK, anchor="start"))

    # 2. Механіка та мотори (праворуч зверху)
    mx, my, mw, mh = 730, 60, 290, 190
    f.append(rect(mx, my, mw, mh, fill="#f4f8fa", stroke=NEG, sw=1.8, rx=8))
    f.append(text(mx + mw / 2, my + 24, "Механіка та приводи", size=13, bold=True, color=NEG))
    f.append(text(mx + 20, my + 55, "• 4 безколекторні мотори (BLDC)", size=11, color=INK, anchor="start"))
    f.append(text(mx + 20, my + 80, "• Пропелери: дисбаланс мас m_imb", size=11, color=INK, anchor="start"))
    f.append(text(mx + 20, my + 105, "• Акустичні й структурні вібрації 100–500 Гц", size=11, color=INK, anchor="start"))
    f.append(text(mx + 20, my + 130, "• Центр мас CoG відносно центру тяги", size=11, color=INK, anchor="start"))
    f.append(text(mx + 20, my + 155, "• Жорсткість променів та рами", size=11, color=INK, anchor="start"))

    # 3. Польотний контролер і сенсори (посередині внизу)
    cx, cy, cw, ch = 360, 180, 340, 280
    f.append(rect(cx, cy, cw, ch, fill="#f9fbfd", stroke=FIELD, sw=2, rx=10))
    f.append(text(cx + cw / 2, cy + 24, "Польотний контролер (FCU)", size=13, bold=True, color=FIELD))
    f.append(rect(cx + 20, cy + 45, 300, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(cx + 150, cy + 64, "IMU: 3-осьовий Accel + 3-осьовий Gyro", size=11, bold=True))
    f.append(text(cx + 150, cy + 80, "демпфування силіконом, низькочастотні LPF", size=9.5, color=MUTED))

    f.append(rect(cx + 20, cy + 95, 300, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(cx + 150, cy + 114, "Магнітометр (компас)", size=11, bold=True))
    f.append(text(cx + 150, cy + 130, "винос на щоглу, компенсація струму", size=9.5, color=MUTED))

    f.append(rect(cx + 20, cy + 145, 300, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(cx + 150, cy + 164, "Барометр MS5611 / BMP280", size=11, bold=True))
    f.append(text(cx + 150, cy + 180, "захист поролоном від світла й тиску гвинтів", size=9.5, color=MUTED))

    f.append(rect(cx + 20, cy + 195, 300, 65, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(cx + 150, cy + 215, "Модуль перевірок Pre-Arm & EKF", size=11, bold=True, color=FIELD))
    f.append(text(cx + 150, cy + 233, "перевірка сенсорів, живлення, RC, EKF", size=9.5, color=INK))
    f.append(text(cx + 150, cy + 249, "блокування активації вихідних ШІМ-таймерів", size=9.5, color=POS, bold=True))

    # 4. Зовнішній інтерфейс і безпека (ліворуч знизу)
    sx, sy, sw, sh = 40, 310, 290, 150
    f.append(rect(sx, sy, sw, sh, fill="#fafbfc", stroke=INK, sw=1.5, rx=8))
    f.append(text(sx + sw / 2, sy + 24, "Безпека та оператор", size=12.5, bold=True))
    f.append(text(sx + 20, sy + 55, "• RC-радіолінк: стік газу в нулі", size=11, color=INK, anchor="start"))
    f.append(text(sx + 20, sy + 80, "• Фізичний перемикач Safety Switch", size=11, color=INK, anchor="start"))
    f.append(text(sx + 20, sy + 105, "• GNSS антена: 3D Fix + HDOP < 1.4", size=11, color=INK, anchor="start"))
    f.append(text(sx + 20, sy + 130, "• Телеметрія MAVLink до наземної GCS", size=11, color=INK, anchor="start"))

    # Стрілки взаємодій і завад
    # Сила -> FCU (магнітні наводки)
    f.append(arrow(px + pw, py + 120, cx, cy + 115, color=POS, sw=2))
    f.append(text(345, 155, "Магнітна завада B(I)", size=10, bold=True, color=POS, anchor="end"))

    # Мотори -> FCU (вібрації)
    f.append(arrow(mx, my + 120, cx + cw, cy + 65, color=NEG, sw=2))
    f.append(text(715, 155, "Механічні вібрації a_vib", size=10, bold=True, color=NEG, anchor="start"))

    # Безпека -> FCU (дозволи)
    f.append(arrow(sx + sw, sy + 75, cx, cy + 220, color=FIELD, sw=2))
    f.append(text(345, 370, "Апаратний дозвіл", size=10, bold=True, color=FIELD, anchor="end"))

    # FCU -> Мотори (керування)
    f.append(arrow(cx + cw, cy + 220, mx + 50, my + mh, color=INK, sw=2))
    f.append(text(725, 340, "DShot / PWM сигнали", size=10, bold=True, color=INK, anchor="start"))

    render(os.path.join(IMG, 'vehicle-subsystems-interaction.svg'), W, H, *f)


# ── 2. Схема 6-позиційного калібрування акселерометра (6-point tumble) ─────────
def fig_six_point_tumble_calibration():
    W, H = 1060, 460
    f = [text(W / 2, 28, "6-позиційне калібрування акселерометра (вимірювання вектора 1g по 6 гранях)", size=15, bold=True)]

    # 6 комірок: 3 зверху, 3 знизу
    positions = [
        ("Позиція 1: Горизонт (Level)", "Z = +1.0g, X = 0, Y = 0", "Горизонтальне положення на лапах", 50, 60),
        ("Позиція 2: Ніс униз (Nose Down)", "X = +1.0g, Y = 0, Z = 0", "Вертикально носом донизу", 380, 60),
        ("Позиція 3: Ніс угору (Nose Up)", "X = -1.0g, Y = 0, Z = 0", "Вертикально носом догори", 710, 60),
        ("Позиція 4: Лівий бік (Left Side)", "Y = -1.0g, X = 0, Z = 0", "Нахил 90° на лівий промінь", 50, 250),
        ("Позиція 5: Правий бік (Right Side)", "Y = +1.0g, X = 0, Z = 0", "Нахил 90° на правий промінь", 380, 250),
        ("Позиція 6: Догори дном (Back)", "Z = -1.0g, X = 0, Y = 0", "Повний переворот на спину 180°", 710, 250),
    ]

    for title_s, math_s, desc_s, bx, by in positions:
        bw, bh = 300, 165
        f.append(rect(bx, by, bw, bh, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=6))
        f.append(rect(bx, by, bw, 32, fill="#edf2f7", stroke=LINE, sw=1.2, rx=6))
        f.append(text(bx + bw / 2, by + 21, title_s, size=11.5, bold=True))

        # Міні-іконка орієнтації
        cx, cy = bx + 55, by + 95
        f.append(rect(cx - 35, cy - 25, 70, 50, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
        # Стрілка вектора тяжіння g
        f.append(arrow(cx, cy - 15, cx, cy + 18, color=POS, sw=2))
        f.append(text(cx + 12, cy + 5, "g", size=11, bold=True, color=POS))

        # Текстовий блок праворуч
        f.append(text(bx + 105, by + 68, math_s, size=11, bold=True, color=NEG, anchor="start"))
        f.append(text(bx + 105, by + 95, desc_s, size=10, color=INK, anchor="start"))
        f.append(text(bx + 105, by + 120, "Збір 500–1000 відліків", size=9.5, color=MUTED, anchor="start"))
        f.append(text(bx + 105, by + 140, "без вібрацій і рухів", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'six-point-tumble-calibration.svg'), W, H, *f)


# ── 3. Схема конфігурації моторів Quad-X та мікшер тяги ───────────────────────
def fig_motor_direction_and_mixing():
    W, H = 1060, 480
    f = [text(W / 2, 28, "Конфігурація моторів Quad-X: нумерація, напрямки обертання та реактивний момент", size=15, bold=True)]

    # Центральний рисунок рами квадрокоптера
    cx, cy = 300, 250
    # Промені (хрест X)
    f.append(line(cx - 150, cy - 130, cx + 150, cy + 130, color=INK, sw=4))
    f.append(line(cx - 150, cy + 130, cx + 150, cy - 130, color=INK, sw=4))

    # Центральний фюзеляж (FCU)
    f.append(rect(cx - 45, cy - 45, 90, 90, fill="#edf7ed", stroke=FIELD, sw=2, rx=8))
    f.append(text(cx, cy - 8, "Польотний", size=11, bold=True, color=FIELD))
    f.append(text(cx, cy + 10, "контролер", size=11, bold=True, color=FIELD))
    # Стрілка напрямку носа
    f.append(arrow(cx, cy - 45, cx, cy - 85, color=POS, sw=2.5))
    f.append(text(cx, cy - 95, "НІС (Forward +X)", size=11, bold=True, color=POS))

    # Мотори на кінцях променів
    motors = [
        ("M1 (Задній правий)", cx + 150, cy + 130, "CCW", NEG, "−Yaw"),
        ("M2 (Передній правий)", cx + 150, cy - 130, "CW", POS, "+Yaw"),
        ("M3 (Задній лівий)", cx - 150, cy + 130, "CW", POS, "+Yaw"),
        ("M4 (Передній лівий)", cx - 150, cy - 130, "CCW", NEG, "−Yaw"),
    ]

    for name_s, mx, my, rot_dir, color_c, yaw_s in motors:
        f.append(circle(mx, my, 36, fill="#ffffff", stroke=color_c, sw=2.2))
        f.append(text(mx, my - 8, name_s.split(" ")[0], size=13, bold=True, color=color_c))
        f.append(text(mx, my + 10, rot_dir, size=11, bold=True, color=color_c))
        f.append(text(mx, my + 25, yaw_s, size=9.5, color=MUTED))
        f.append(text(mx, my + 50 if my > cy else my - 50, name_s.split(" ", 1)[1], size=10, bold=True))

    # Таблиця матриці мікшування праворуч
    tx, ty, tw, th = 560, 80, 460, 360
    f.append(rect(tx, ty, tw, th, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(tx + tw / 2, ty + 26, "Матриця лінійного мікшера тяги (Motor Mixer)", size=13, bold=True))
    f.append(text(tx + tw / 2, ty + 48, "Формула вихідного сигналу: PWM_i = Throttle ± Roll ± Pitch ± Yaw", size=10, color=MUTED))

    # Заголовок таблиці
    headers = ["Мотор", "Throttle", "Roll (Крен)", "Pitch (Тангаж)", "Yaw (Рискання)"]
    col_w = [90, 85, 95, 100, 90]
    hx = tx + 10
    hy = ty + 70
    f.append(rect(hx, hy, tw - 20, 28, fill="#e2e8f0", stroke=LINE, sw=1, rx=4))
    cur_x = hx
    for i, h_text in enumerate(headers):
        f.append(text(cur_x + col_w[i] / 2, hy + 18, h_text, size=10.5, bold=True))
        cur_x += col_w[i]

    # Рядки таблиці
    rows = [
        ("M1 (Rear-R)", "+1.0", "−0.5 (ліво)", "+0.5 (ніс)", "−1.0 (CCW)"),
        ("M2 (Front-R)", "+1.0", "−0.5 (ліво)", "−0.5 (хвіст)", "+1.0 (CW)"),
        ("M3 (Rear-L)", "+1.0", "+0.5 (право)", "+0.5 (ніс)", "+1.0 (CW)"),
        ("M4 (Front-L)", "+1.0", "+0.5 (право)", "−0.5 (хвіст)", "−1.0 (CCW)"),
    ]

    r_y = hy + 28
    for r_idx, r_data in enumerate(rows):
        bg_c = "#ffffff" if r_idx % 2 == 0 else "#f1f5f9"
        f.append(rect(hx, r_y, tw - 20, 34, fill=bg_c, stroke="#cbd5e1", sw=0.8, rx=2))
        cur_x = hx
        for c_idx, val in enumerate(r_data):
            f.append(text(cur_x + col_w[c_idx] / 2, r_y + 21, val, size=10, bold=(c_idx == 0)))
            cur_x += col_w[c_idx]
        r_y += 34

    # Примітка під таблицею
    f.append(rect(tx + 20, ty + 240, tw - 40, 95, fill="#fdf2f2", stroke=POS, sw=1.2, rx=6))
    f.append(text(tx + tw / 2, ty + 260, "Критична небезпека перевернутого мікшера:", size=11, bold=True, color=POS))
    f.append(text(tx + 30, ty + 282, "Якщо переплутано виводи M1 та M2 або реверсовано гіроскоп,", size=10, color=INK, anchor="start"))
    f.append(text(tx + 30, ty + 302, "контур зворотного зв'язку стає ПОЗИТИВНИМ: замість стабілізації", size=10, color=INK, anchor="start"))
    f.append(text(tx + 30, ty + 322, "контролер миттєво перекидає дрон за 50–100 мс (Flip of Death).", size=10, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, 'motor-direction-and-mixing.svg'), W, H, *f)


# ── 4. Схема автомата станів безпеки Pre-Arm та блокування ─────────────────────
def fig_prearm_state_machine():
    W, H = 1060, 480
    f = [text(W / 2, 28, "Автомат передпольотних перевірок безпеки та контур блокування моторів", size=15, bold=True)]

    # Стан 1: DISARMED (Заблоковано)
    s1x, s1y, s1w, s1h = 50, 160, 240, 180
    f.append(rect(s1x, s1y, s1w, s1h, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(rect(s1x, s1y, s1w, 36, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=8))
    f.append(text(s1x + s1w / 2, s1y + 24, "1. СТАН DISARMED", size=12.5, bold=True))
    f.append(text(s1x + 15, s1y + 60, "• Силові ШІМ-виходи заглушені", size=10.5, color=INK, anchor="start"))
    f.append(text(s1x + 15, s1y + 82, "• Апаратний запобіжник розімкнено", size=10.5, color=INK, anchor="start"))
    f.append(text(s1x + 15, s1y + 104, "• Фоновий моніторинг датчиків", size=10.5, color=INK, anchor="start"))
    f.append(text(s1x + 15, s1y + 126, "• Перевірка бітової маски Pre-Arm", size=10.5, color=INK, anchor="start"))
    f.append(text(s1x + 15, s1y + 152, "Швидкість моторів = 0 об/хв", size=10.5, bold=True, color=POS, anchor="start"))

    # Стан 2: PREARM CHECK ENGINE (Оцінка готовності)
    s2x, s2y, s2w, s2h = 390, 80, 280, 340
    f.append(rect(s2x, s2y, s2w, s2h, fill="#f9fbfd", stroke=FIELD, sw=2, rx=8))
    f.append(rect(s2x, s2y, s2w, 36, fill="#e6f4ea", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(s2x + s2w / 2, s2y + 24, "2. PRE-ARM SAFETY MATRIX", size=12.5, bold=True, color=FIELD))

    checks = [
        ("IMU Health & Calibrated", "Зміщення в нормі, 6 граней ок"),
        ("Compass Consistency", "Без сильних магнітних аномалій"),
        ("Barometer Healthy", "Дрейф тиску < 0.5 м/с"),
        ("Battery Voltage & Capacity", "Напруга > 3.7 В/елемент"),
        ("RC Link & Throttle Zero", "Зв'язок є, стік у нижній точці"),
        ("EKF Navigation State", "Дисперсії швидкості/позиції низькі"),
        ("Hardware Safety Switch", "Кнопку на апараті активовано"),
    ]

    cy_chk = s2y + 55
    for chk_title, chk_desc in checks:
        f.append(circle(s2x + 22, cy_chk + 12, 8, fill="#edf7ed", stroke=FIELD, sw=1.5))
        f.append(text(s2x + 22, cy_chk + 15, "✓", size=10, bold=True, color=FIELD))
        f.append(text(s2x + 38, cy_chk + 10, chk_title, size=10.5, bold=True, color=INK, anchor="start"))
        f.append(text(s2x + 38, cy_chk + 25, chk_desc, size=9, color=MUTED, anchor="start"))
        cy_chk += 39

    # Стан 3: ARMED (Озброєно / Готовий до польоту)
    s3x, s3y, s3w, s3h = 770, 160, 240, 180
    f.append(rect(s3x, s3y, s3w, s3h, fill="#fdfbf7", stroke=POS, sw=2, rx=8))
    f.append(rect(s3x, s3y, s3w, 36, fill="#fef3e6", stroke=POS, sw=1.5, rx=8))
    f.append(text(s3x + s3w / 2, s3y + 24, "3. СТАН ARMED", size=12.5, bold=True, color=POS))
    f.append(text(s3x + 15, s3y + 60, "• ШІМ-таймери активовано", size=10.5, color=INK, anchor="start"))
    f.append(text(s3x + 15, s3y + 82, "• Мотори на холостих (Idle Spin)", size=10.5, color=INK, anchor="start"))
    f.append(text(s3x + 15, s3y + 104, "• PID-регулятори активні", size=10.5, color=INK, anchor="start"))
    f.append(text(s3x + 15, s3y + 126, "• Логування на SD-карту", size=10.5, color=INK, anchor="start"))
    f.append(text(s3x + 15, s3y + 152, "УВАГА: обертання гвинтів!", size=10.5, bold=True, color=POS, anchor="start"))

    # Стрілки переходів
    # DISARMED -> PRE-ARM
    f.append(arrow(s1x + s1w, s1y + 90, s2x, s1y + 90, color=FIELD, sw=2))
    f.append(text(340, s1y + 80, "Команда Arming", size=10, bold=True, color=FIELD))

    # PRE-ARM -> ARMED (якщо всі ОК)
    f.append(arrow(s2x + s2w, s1y + 90, s3x, s1y + 90, color=FIELD, sw=2))
    f.append(text(720, s1y + 80, "Усі перевірки ОК", size=10, bold=True, color=FIELD))

    # PRE-ARM -> DISARMED (якщо хоч 1 збій)
    f.append(line(s2x, s1y + 130, s1x + s1w, s1y + 130, color=POS, sw=1.8, dash="4,3"))
    f.append(arrow(s1x + s1w + 10, s1y + 130, s1x + s1w, s1y + 130, color=POS, sw=1.8))
    f.append(text(340, s1y + 148, "Хоч 1 біт = 0 (ВІДМОВА)", size=9.5, bold=True, color=POS))

    # ARMED -> DISARMED (Disarm або Failsafe)
    f.append(line(s3x + s3w / 2, s3y + s3h, s3x + s3w / 2, 440, color=INK, sw=1.8))
    f.append(line(s3x + s3w / 2, 440, s1x + s1w / 2, 440, color=INK, sw=1.8))
    f.append(arrow(s1x + s1w / 2, 440, s1x + s1w / 2, s1y + s1h, color=INK, sw=1.8))
    f.append(text(W / 2, 430, "Команда Disarm / Спрацювання Failsafe / Аварійне вимкнення Kill Switch", size=10, bold=True, color=INK))

    render(os.path.join(IMG, 'prearm-state-machine.svg'), W, H, *f)


if __name__ == '__main__':
    fig_subsystems_interaction()
    fig_six_point_tumble_calibration()
    fig_motor_direction_and_mixing()
    fig_prearm_state_machine()
    print("All figures generated successfully.")
