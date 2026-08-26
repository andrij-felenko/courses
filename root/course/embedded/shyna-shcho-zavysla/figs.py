# -*- coding: utf-8 -*-
"""Фігури для статті shyna-shcho-zavysla («Шина, що зависла»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. i2c-stuck-recovery: зависання SDA та процедура відновлення 9 тактами ──
def fig_i2c_stuck_recovery():
    W, H = 840, 440
    p = []

    # Заголовок / фонові зони
    p.append(rect(15, 15, 810, 410, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    
    # Зона 1: Аварійний розрив
    p.append(rect(30, 35, 230, 375, fill="#fff5f5", stroke=POS, sw=1.0, rx=6))
    b1, _, _ = textbox(145, 55, "1. Збій посеред читання", size=12, color=POS, bold=True, fill="#ffe3e3", stroke=POS)
    p.append(b1)
    
    # Зона 2: Генерація 9 тактів SCL
    p.append(rect(275, 35, 335, 375, fill="#f4f9f4", stroke=FIELD, sw=1.0, rx=6))
    b2, _, _ = textbox(442, 55, "2. Відновлення 9 тактами SCL (GPIO)", size=12, color=FIELD, bold=True, fill="#d6f0df", stroke=FIELD)
    p.append(b2)

    # Зона 3: Умова STOP та звільнення
    p.append(rect(625, 35, 185, 375, fill="#f0f4fc", stroke=NEG, sw=1.0, rx=6))
    b3, _, _ = textbox(717, 55, "3. Формування STOP", size=12, color=NEG, bold=True, fill="#dce6fa", stroke=NEG)
    p.append(b3)

    # Лінії сигналів: SCL і SDA
    y_scl = 150
    y_sda = 270

    p.append(text(45, y_scl - 18, "SCL (Master)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(45, y_sda - 18, "SDA (Slave)", size=12, color=INK, bold=True, anchor="start"))

    # Базові лінії нуля і одиниці
    p.append(line(45, y_scl, 795, y_scl, color=MUTED, sw=0.8, dash="3 3"))
    p.append(line(45, y_scl - 35, 795, y_scl - 35, color=MUTED, sw=0.8, dash="3 3"))
    p.append(line(45, y_sda, 795, y_sda, color=MUTED, sw=0.8, dash="3 3"))
    p.append(line(45, y_sda - 35, 795, y_sda - 35, color=MUTED, sw=0.8, dash="3 3"))

    p.append(text(38, y_scl - 35, "3.3V", size=9, color=MUTED, anchor="end"))
    p.append(text(38, y_scl, "0V", size=9, color=MUTED, anchor="end"))
    p.append(text(38, y_sda - 35, "3.3V", size=9, color=MUTED, anchor="end"))
    p.append(text(38, y_sda, "0V", size=9, color=MUTED, anchor="end"))

    # Хвильова форма SCL:
    # 1. Збій: Master дає кілька тактів і падає в 1
    scl_pts_1 = [
        (45, y_scl), (70, y_scl), (70, y_scl - 35), (95, y_scl - 35), (95, y_scl),
        (120, y_scl), (120, y_scl - 35), (145, y_scl - 35), (145, y_scl),
        (170, y_scl), (170, y_scl - 35), (250, y_scl - 35)
    ]
    scl_str1 = " ".join("%.1f,%.1f" % pt for pt in scl_pts_1)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (scl_str1, LINE))

    # Збійний момент на SCL
    p.append(line(170, 85, 170, 135, color=POS, sw=1.5, dash="4 3"))
    p.append(line(170, 165, 170, 370, color=POS, sw=1.5, dash="4 3"))
    bt1, _, _ = textbox(170, 95, "MCU ресет / завада", size=10, color=POS, bold=True, fill="#ffffff", stroke=POS)
    p.append(bt1)

    # Хвильова форма SDA у зоні 1: Slave тримає 0, очікуючи продовження тактування
    sda_pts_1 = [
        (45, y_sda - 35), (60, y_sda - 35), (60, y_sda), (250, y_sda)
    ]
    sda_str1 = " ".join("%.1f,%.1f" % pt for pt in sda_pts_1)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (sda_str1, POS))
    p.append(text(155, y_sda + 22, "Slave тримає SDA=0 (Open-Drain затиснуто)", size=10, color=POS, bold=True))

    # Хвильова форма SCL у зоні 2: Master генерує 9 тактів через GPIO
    scl_pts_2 = [(280, y_scl - 35)]
    cur_x = 290
    for i in range(1, 10):
        scl_pts_2.extend([
            (cur_x, y_scl - 35), (cur_x, y_scl),
            (cur_x + 15, y_scl), (cur_x + 15, y_scl - 35),
            (cur_x + 30, y_scl - 35)
        ])
        p.append(text(cur_x + 7.5, y_scl - 42, str(i), size=10, color=FIELD, bold=True))
        cur_x += 32
    scl_str2 = " ".join("%.1f,%.1f" % pt for pt in scl_pts_2)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (scl_str2, FIELD))

    # Хвильова форма SDA у зоні 2: Slave докручує біти і на 8-му такті відпускає лінію (підтяжка піднімає в 1)
    release_x = 290 + 7 * 32 + 15
    sda_pts_2 = [
        (280, y_sda), (release_x, y_sda), (release_x + 8, y_sda - 35), (595, y_sda - 35)
    ]
    sda_str2 = " ".join("%.1f,%.1f" % pt for pt in sda_pts_2)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (sda_str2, FIELD))
    
    p.append(line(release_x + 4, 110, release_x + 4, 255, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(release_x + 4, 345, "Slave відпустив SDA -> Pull-Up до 3.3V", size=10, color=FIELD, bold=True))

    # Хвильова форма SCL і SDA у зоні 3: STOP умова (SCL=1, SDA: 0 -> 1)
    scl_pts_3 = [
        (630, y_scl - 35), (640, y_scl), (660, y_scl), (660, y_scl - 35), (785, y_scl - 35)
    ]
    scl_str3 = " ".join("%.1f,%.1f" % pt for pt in scl_pts_3)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (scl_str3, NEG))

    sda_pts_3 = [
        (630, y_sda - 35), (645, y_sda - 35), (645, y_sda), (700, y_sda), (720, y_sda - 35), (785, y_sda - 35)
    ]
    sda_str3 = " ".join("%.1f,%.1f" % pt for pt in sda_pts_3)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (sda_str3, NEG))

    p.append(arrow(710, y_sda + 25, 710, y_sda - 5, color=NEG, sw=1.5))
    p.append(text(717, 360, "STOP: SDA 0->1 при SCL=1", size=10, color=NEG, bold=True))

    # Пояснювальний підсумок знизу
    p.append(text(420, 405, "Результат: обидві лінії повертаються в High (3.3V), апаратний периферійний модуль I2C розблоковано", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "i2c-stuck-recovery.svg"), W, H, *p)


# ── 2. can-error-states: автомат станів обробки помилок CAN (ISO 11898) ──────
def fig_can_error_states():
    W, H = 880, 430
    p = []

    # Загальна рамка
    p.append(rect(15, 15, 850, 400, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # Стан 1: Error Active
    b1_x, b1_y = 140, 185
    b1_box = rect(b1_x - 105, b1_y - 75, 210, 150, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=8)
    p.append(b1_box)
    p.append(text(b1_x, b1_y - 45, "ERROR ACTIVE", size=13, color=FIELD, bold=True))
    p.append(text(b1_x, b1_y - 20, "Повноправна робота", size=11, color=INK, bold=True))
    p.append(text(b1_x, b1_y + 5, "TEC < 128  |  REC < 128", size=10, color=FIELD, bold=True))
    p.append(text(b1_x, b1_y + 30, "Шле: Active Error Flag", size=10, color=INK))
    p.append(text(b1_x, b1_y + 50, "(6 домінантних бітів '0')", size=9, color=MUTED))

    # Стан 2: Error Passive
    b2_x, b2_y = 445, 185
    b2_box = rect(b2_x - 105, b2_y - 75, 210, 150, fill="#fffbf0", stroke="#d97706", sw=2.0, rx=8)
    p.append(b2_box)
    p.append(text(b2_x, b2_y - 45, "ERROR PASSIVE", size=13, color="#d97706", bold=True))
    p.append(text(b2_x, b2_y - 20, "Обмежена передача", size=11, color=INK, bold=True))
    p.append(text(b2_x, b2_y + 5, "TEC >= 128 / REC >= 128", size=10, color="#d97706", bold=True))
    p.append(text(b2_x, b2_y + 30, "Шле: Passive Error Flag (6 '1')", size=10, color=INK))
    p.append(text(b2_x, b2_y + 50, "+ Suspend Transmission (8 '1')", size=9, color=MUTED))

    # Стан 3: Bus-Off
    b3_x, b3_y = 735, 185
    b3_box = rect(b3_x - 90, b3_y - 75, 180, 150, fill="#fdf2f2", stroke=POS, sw=2.0, rx=8)
    p.append(b3_box)
    p.append(text(b3_x, b3_y - 45, "BUS-OFF", size=13, color=POS, bold=True))
    p.append(text(b3_x, b3_y - 20, "Вузол ізольовано", size=11, color=INK, bold=True))
    p.append(text(b3_x, b3_y + 5, "TEC > 255", size=11, color=POS, bold=True))
    p.append(text(b3_x, b3_y + 30, "Трансивер відключено", size=10, color=POS))
    p.append(text(b3_x, b3_y + 50, "Лінія не блокується", size=9, color=MUTED))

    # Переходи: Active -> Passive
    p.append(arrow(b1_x + 105, b1_y - 25, b2_x - 105, b2_y - 25, color="#d97706", sw=1.8))
    p.append(text((b1_x + b2_x) / 2, b1_y - 33, "TEC/REC >= 128", size=9, color="#d97706", bold=True))

    # Переходи: Passive -> Active
    p.append(arrow(b2_x - 105, b2_y + 25, b1_x + 105, b1_y + 25, color=FIELD, sw=1.8))
    p.append(text((b1_x + b2_x) / 2, b2_y + 37, "Успіх: TEC & REC <= 127", size=9, color=FIELD, bold=True))

    # Переходи: Passive -> Bus-Off
    p.append(arrow(b2_x + 105, b2_y - 20, b3_x - 90, b3_y - 20, color=POS, sw=2.0))
    p.append(text((b2_x + b3_x) / 2, b2_y - 28, "TEC > 255 (аварія TX)", size=9, color=POS, bold=True))

    # Відновлення: Bus-Off -> Active (128 послідовностей по 11 рецесивних бітів)
    rec_path = [
        (b3_x, b3_y + 75), (b3_x, 345), (b1_x, 345), (b1_x, b1_y + 75)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % 
             (" ".join("%.1f,%.1f" % pt for pt in rec_path), NEG))
    p.append(arrow(b1_x, 345, b1_x, b1_y + 75, color=NEG, sw=2.0))
    
    t4, _, _ = textbox(445, 345, "Відновлення: скидання + очікування 128 × 11 рецесивних бітів '1' (Bus Free)", 
                       size=11, color=NEG, bold=True, fill="#ffffff", stroke=NEG)
    p.append(t4)

    # Інформаційна плашка зверху
    p.append(text(440, 45, "Правила зміни лічильників: Помилка TX -> TEC +8  |  Помилка RX -> REC +1  |  Успішний кадр -> TEC -1, REC -1", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "can-error-states.svg"), W, H, *p)


# ── 3. rs485-reflections-failsafe: узгодження ліній 120 Ом та Fail-Safe зміщення
def fig_rs485_reflections_failsafe():
    W, H = 840, 520
    p = []

    # Загальна рамка
    p.append(rect(15, 15, 810, 490, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # ── Блок А: Хвильовий дзвін без термінатора 120 Ом ─────────────────────────
    p.append(rect(30, 30, 780, 215, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    p.append(text(45, 55, "А. Вплив термінального резистора 120 Ом (відбиття сигналу)", size=13, color=INK, bold=True, anchor="start"))

    # Осцилограма без термінатора (дзвін, перетин порогів)
    ox1, oy1 = 70, 165
    p.append(line(ox1, oy1, ox1 + 320, oy1, color=MUTED, sw=0.8, dash="3 3"))
    p.append(line(ox1, oy1 - 50, ox1 + 320, oy1 - 50, color=MUTED, sw=0.8, dash="3 3"))
    p.append(line(ox1, oy1 + 50, ox1 + 320, oy1 + 50, color=MUTED, sw=0.8, dash="3 3"))

    # Зона порогів спрацьовування компаратора (+200mV / -200mV)
    p.append(rect(ox1, oy1 - 15, 320, 30, fill="#fdf2f2", stroke="none"))
    p.append(line(ox1, oy1 - 15, ox1 + 320, oy1 - 15, color=POS, sw=1.0, dash="2 2"))
    p.append(line(ox1, oy1 + 15, ox1 + 320, oy1 + 15, color=POS, sw=1.0, dash="2 2"))
    p.append(text(ox1 - 8, oy1 - 15, "+200mV", size=9, color=POS, anchor="end"))
    p.append(text(ox1 - 8, oy1 + 15, "-200mV", size=9, color=POS, anchor="end"))
    p.append(text(ox1 - 8, oy1, "0V", size=9, color=MUTED, anchor="end"))

    # Крива з дзвоном (обрив термінатора)
    ring_pts = [
        (ox1, oy1 + 45), (ox1 + 30, oy1 + 45), (ox1 + 45, oy1 - 70), (ox1 + 60, oy1 + 30),
        (ox1 + 75, oy1 - 60), (ox1 + 90, oy1 + 20), (ox1 + 105, oy1 - 55), (ox1 + 120, oy1 - 48),
        (ox1 + 200, oy1 - 48), (ox1 + 215, oy1 + 65), (ox1 + 230, oy1 - 25), (ox1 + 245, oy1 + 55),
        (ox1 + 260, oy1 - 15), (ox1 + 275, oy1 + 48), (ox1 + 320, oy1 + 48)
    ]
    ring_str = " ".join("%.1f,%.1f" % pt for pt in ring_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (ring_str, POS))
    p.append(text(ox1 + 160, 75, "БЕЗ термінатора: Gamma = +1 (дзвін перетинає поріг)", size=11, color=POS, bold=True))

    # Осцилограма з термінатором 120 Ом (чистий фронт)
    ox2, oy2 = 450, 165
    p.append(line(ox2, oy2, ox2 + 320, oy2, color=MUTED, sw=0.8, dash="3 3"))
    p.append(rect(ox2, oy2 - 15, 320, 30, fill="#eafaf0", stroke="none"))
    p.append(line(ox2, oy2 - 15, ox2 + 320, oy2 - 15, color=FIELD, sw=1.0, dash="2 2"))
    p.append(line(ox2, oy2 + 15, ox2 + 320, oy2 + 15, color=FIELD, sw=1.0, dash="2 2"))

    clean_pts = [
        (ox2, oy2 + 45), (ox2 + 40, oy2 + 45), (ox2 + 55, oy2 - 48), (ox2 + 200, oy2 - 48),
        (ox2 + 215, oy2 + 48), (ox2 + 320, oy2 + 48)
    ]
    clean_str = " ".join("%.1f,%.1f" % pt for pt in clean_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (clean_str, FIELD))
    p.append(text(ox2 + 160, 75, "З термінатором 120 Ом: чистий фронт без хибних бітів", size=11, color=FIELD, bold=True))

    # ── Блок Б: Fail-Safe зміщення шини ───────────────────────────────────────
    p.append(rect(30, 260, 780, 230, fill="#fafbfc", stroke=LINE, sw=1.0, rx=6))
    p.append(text(45, 285, "Б. Схема захисного зміщення (Fail-Safe Biasing) для усунення плаваючої шини", size=13, color=INK, bold=True, anchor="start"))

    # Схема підтяжок: VCC -> R_pullup -> Лінія A -> R_term -> Лінія B -> R_pulldown -> GND
    cx = 420
    # Шини живлення VCC і GND
    p.append(line(100, 320, 740, 320, color=POS, sw=1.8))  # VCC 5V / 3.3V
    p.append(text(85, 320, "VCC", size=11, color=POS, bold=True, anchor="end"))

    p.append(line(100, 460, 740, 460, color=INK, sw=1.8))  # GND
    p.append(text(85, 460, "GND", size=11, color=INK, bold=True, anchor="end"))

    # Лінії A і B
    p.append(line(100, 370, 740, 370, color=FIELD, sw=2.2))  # Лінія A (+)
    p.append(text(85, 370, "Line A (+)", size=11, color=FIELD, bold=True, anchor="end"))

    p.append(line(100, 410, 740, 410, color=NEG, sw=2.2))    # Лінія B (-)
    p.append(text(85, 410, "Line B (-)", size=11, color=NEG, bold=True, anchor="end"))

    # Резистор R_pullup (VCC -> A)
    r_up_x = 220
    b_rup, bw_up, bh_up = textbox(r_up_x, 345, "R_bias (Pull-Up)\n560-680 Ом", size=9, color=POS, bold=True, fill="#ffffff", stroke=POS)
    p.append(line(r_up_x, 320, r_up_x, 345 - bh_up / 2, color=POS, sw=1.5))
    p.append(b_rup)
    p.append(line(r_up_x, 345 + bh_up / 2, r_up_x, 370, color=POS, sw=1.5))

    # Резистор термінатора R_term (A -> B)
    r_t_x = 420
    b_rt, bw_t, bh_t = textbox(r_t_x, 390, "R_term 120 Ом", size=9, color=INK, bold=True, fill="#ffffff", stroke=LINE)
    p.append(line(r_t_x, 370, r_t_x, 390 - bh_t / 2, color=INK, sw=1.5))
    p.append(b_rt)
    p.append(line(r_t_x, 390 + bh_t / 2, r_t_x, 410, color=INK, sw=1.5))

    # Резистор R_pulldown (B -> GND)
    r_dn_x = 620
    b_rdn, bw_dn, bh_dn = textbox(r_dn_x, 435, "R_bias (Pull-Down)\n560-680 Ом", size=9, color=NEG, bold=True, fill="#ffffff", stroke=NEG)
    p.append(line(r_dn_x, 410, r_dn_x, 435 - bh_dn / 2, color=NEG, sw=1.5))
    p.append(b_rdn)
    p.append(line(r_dn_x, 435 + bh_dn / 2, r_dn_x, 460, color=NEG, sw=1.5))

    # Пояснення напруги зміщення
    p.append(text(cx, 480, "У стані спокою (всі TX у High-Z): V_AB = V_A - V_B >= +200 мВ -> UART приймач бачить стабільний рівень Mark (Idle 1)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "rs485-reflections-failsafe.svg"), W, H, *p)


if __name__ == "__main__":
    fig_i2c_stuck_recovery()
    fig_can_error_states()
    fig_rs485_reflections_failsafe()
    print("All figures generated successfully.")
