# -*- coding: utf-8 -*-
"""Фігури до статті «Гібридне заземлення екрана» (hw-pcb/hybrid-shield-grounding).

Дві фігури:
  1. ground-loop-shield.svg — Контури заземлення в екранах кабелів та дилема заземлення (НЧ петля проти ВЧ антени)
  2. hybrid-ground-rc.svg    — Схемотехніка та топологія гібридного RC-заземлення екрана на межі шасі й плати

Запуск: python figs.py
"""
import sys, os

# 4 рівні вгору до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. ground-loop-shield.svg — Схема контуру заземлення та дилема
# ════════════════════════════════════════════════════════════════════════════
def fig_ground_loop_shield():
    W, H = 880, 520
    f = []

    f.append(text(W / 2, 28, "ДИЛЕМА ЗАЗЕМЛЕННЯ ЕКРАНА КАБЕЛЮ: НИЗЬКІ ТА ВИСОКІ ЧАСТОТИ", size=14, bold=True, color=INK))

    # ── Секція 1: Пряме заземлення з двох боків (Double-ended Direct Ground) ──
    p1_x, p1_y, p1_w, p1_h = 25, 55, 405, 215
    f.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fffaf9", stroke=POS, sw=1.2, rx=6))
    f.append(text(p1_x + p1_w / 2, p1_y + 20, "Пряме заземлення з обох кінців (Double-ended)", size=12, bold=True, color=POS))
    f.append(text(p1_x + p1_w / 2, p1_y + 36, "ВЧ захист відмінний, але виникає петля струму 50 Гц", size=10, color=MUTED))

    # Корпус А
    f.append(rect(p1_x + 15, p1_y + 50, 75, 90, fill="#f0f3f6", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p1_x + 52, p1_y + 80, "Вузол A", size=11, bold=True, color=INK))
    f.append(text(p1_x + 52, p1_y + 98, "Шасі A", size=9, color=MUTED))

    # Корпус Б
    f.append(rect(p1_x + p1_w - 90, p1_y + 50, 75, 90, fill="#f0f3f6", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p1_x + p1_w - 53, p1_y + 80, "Вузол B", size=11, bold=True, color=INK))
    f.append(text(p1_x + p1_w - 53, p1_y + 98, "Шасі B", size=9, color=MUTED))

    # Екран кабелю між корпусами
    f.append(rect(p1_x + 90, p1_y + 70, p1_w - 180, 50, fill="#e8edf2", stroke="#607d8b", sw=1.5, rx=3))
    f.append(text(p1_x + p1_w / 2, p1_y + 88, "Екран кабелю (Shield)", size=10, bold=True, color="#37474f"))
    # Сигнальні жили всередині
    f.append(line(p1_x + 90, p1_y + 102, p1_x + p1_w - 90, p1_y + 102, color=POS, sw=1.8, dash="4,3"))
    f.append(text(p1_x + p1_w / 2, p1_y + 114, "Сигнальні жили", size=9, color=POS))

    # Земляні з'єднання
    f.append(line(p1_x + 52, p1_y + 140, p1_x + 52, p1_y + 175, color=LINE, sw=1.5))
    f.append(line(p1_x + 42, p1_y + 175, p1_x + 62, p1_y + 175, color=LINE, sw=2.0))
    f.append(line(p1_x + 46, p1_y + 179, p1_x + 58, p1_y + 179, color=LINE, sw=1.5))
    f.append(line(p1_x + 49, p1_y + 183, p1_x + 55, p1_y + 183, color=LINE, sw=1.2))
    f.append(text(p1_x + 52, p1_y + 198, "PE1 (0 В)", size=9, bold=True, color=INK))

    f.append(line(p1_x + p1_w - 53, p1_y + 140, p1_x + p1_w - 53, p1_y + 175, color=LINE, sw=1.5))
    f.append(line(p1_x + p1_w - 63, p1_y + 175, p1_x + p1_w - 43, p1_y + 175, color=LINE, sw=2.0))
    f.append(line(p1_x + p1_w - 59, p1_y + 179, p1_x + p1_w - 47, p1_y + 179, color=LINE, sw=1.5))
    f.append(line(p1_x + p1_w - 56, p1_y + 183, p1_x + p1_w - 50, p1_y + 183, color=LINE, sw=1.2))
    f.append(text(p1_x + p1_w - 53, p1_y + 198, "PE2 (ΔV_gnd)", size=9, bold=True, color=POS))

    # Струм петлі по контуру
    f.append(line(p1_x + 65, p1_y + 180, p1_x + p1_w - 65, p1_y + 180, color=POS, sw=1.5, dash="3,3"))
    f.append(arrow(p1_x + p1_w / 2 - 40, p1_y + 180, p1_x + p1_w / 2 + 40, p1_y + 180, color=POS, sw=1.5))
    f.append(text(p1_x + p1_w / 2, p1_y + 168, "Земляний контур: різниця потенціалів ΔV_gnd", size=9, color=POS))

    # Струм по екрану
    f.append(arrow(p1_x + p1_w - 105, p1_y + 76, p1_x + 105, p1_y + 76, color=POS, sw=1.5))
    f.append(text(p1_x + p1_w / 2, p1_y + 64, "Струм вирівнювання I_loop (гул 50 Гц)", size=9, bold=True, color=POS))


    # ── Секція 2: Заземлення лише з одного кінця (Single-ended Ground) ──
    p2_x, p2_y, p2_w, p2_h = 450, 55, 405, 215
    f.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fcfdfe", stroke=NEG, sw=1.2, rx=6))
    f.append(text(p2_x + p2_w / 2, p2_y + 20, "Заземлення з одного кінця (Single-ended)", size=12, bold=True, color=NEG))
    f.append(text(p2_x + p2_w / 2, p2_y + 36, "Немає петлі на 50 Гц, але незаземлений кінець ловить ВЧ", size=10, color=MUTED))

    # Корпус А
    f.append(rect(p2_x + 15, p2_y + 50, 75, 90, fill="#f0f3f6", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p2_x + 52, p2_y + 80, "Вузол A", size=11, bold=True, color=INK))
    f.append(text(p2_x + 52, p2_y + 98, "Шасі A", size=9, color=MUTED))

    # Корпус Б
    f.append(rect(p2_x + p2_w - 90, p2_y + 50, 75, 90, fill="#f0f3f6", stroke=LINE, sw=1.2, rx=4))
    f.append(text(p2_x + p2_w - 53, p2_y + 80, "Вузол B", size=11, bold=True, color=INK))
    f.append(text(p2_x + p2_w - 53, p2_y + 98, "Шасі B", size=9, color=MUTED))

    # Екран кабелю: зліва підключений, справа розрив!
    f.append(rect(p2_x + 90, p2_y + 70, p2_w - 200, 50, fill="#e8edf2", stroke="#607d8b", sw=1.5, rx=3))
    f.append(text(p2_x + (p2_w - 20) / 2, p2_y + 88, "Екран кабелю", size=10, bold=True, color="#37474f"))
    # Розрив праворуч
    f.append(line(p2_x + p2_w - 110, p2_y + 70, p2_x + p2_w - 110, p2_y + 120, color=NEG, sw=2.0))
    f.append(text(p2_x + p2_w - 135, p2_y + 138, "Розрив (Open)", size=9, bold=True, color=NEG))

    # Сигнальні жили всередині
    f.append(line(p2_x + 90, p2_y + 102, p2_x + p2_w - 90, p2_y + 102, color=INK, sw=1.8, dash="4,3"))
    f.append(text(p2_x + (p2_w - 20) / 2, p2_y + 114, "Сигнальні жили", size=9, color=MUTED))

    # ВЧ наводка на антену
    f.append(arrow(p2_x + p2_w - 130, p2_y + 48, p2_x + p2_w - 130, p2_y + 68, color=POS, sw=1.4))
    f.append(text(p2_x + p2_w - 125, p2_y + 45, "ВЧ завада (RF Noise)", size=9, bold=True, color=POS))
    f.append(text(p2_x + (p2_w - 20) / 2, p2_y + 64, "I_LF = 0 (контур розірвано)", size=9, bold=True, color=FIELD))

    # Земля А
    f.append(line(p2_x + 52, p2_y + 140, p2_x + 52, p2_y + 175, color=LINE, sw=1.5))
    f.append(line(p2_x + 42, p2_y + 175, p2_x + 62, p2_y + 175, color=LINE, sw=2.0))
    f.append(line(p2_x + 46, p2_y + 179, p2_x + 58, p2_y + 179, color=LINE, sw=1.5))
    f.append(line(p2_x + 49, p2_y + 183, p2_x + 55, p2_y + 183, color=LINE, sw=1.2))
    f.append(text(p2_x + 52, p2_y + 198, "PE1", size=9, bold=True, color=INK))

    # Земля Б
    f.append(line(p2_x + p2_w - 53, p2_y + 140, p2_x + p2_w - 53, p2_y + 175, color=LINE, sw=1.5))
    f.append(line(p2_x + p2_w - 63, p2_y + 175, p2_x + p2_w - 43, p2_y + 175, color=LINE, sw=2.0))
    f.append(line(p2_x + p2_w - 59, p2_y + 179, p2_x + p2_w - 47, p2_y + 179, color=LINE, sw=1.5))
    f.append(line(p2_x + p2_w - 56, p2_y + 183, p2_x + p2_w - 50, p2_y + 183, color=LINE, sw=1.2))
    f.append(text(p2_x + p2_w - 53, p2_y + 198, "PE2", size=9, bold=True, color=INK))


    # ── Секція 3: Гібридне заземлення (Hybrid Grounding: RC + GDT) ──
    p3_x, p3_y, p3_w, p3_h = 25, 285, 830, 215
    f.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(p3_x + p3_w / 2, p3_y + 22, "ГІБРИДНЕ ЗАЗЕМЛЕННЯ (HYBRID SHIELD GROUNDING): КРАЩЕ З ОБОХ СВІТІВ", size=13, bold=True, color=FIELD))
    f.append(text(p3_x + p3_w / 2, p3_y + 38, "Пряме з'єднання з одного боку + паралельний RC-ланцюг (1 МОм || 10 нФ / 1 кВ) з іншого", size=10, color=MUTED))

    # Корпус А (Джерело / Майстер)
    f.append(rect(p3_x + 35, p3_y + 55, 120, 110, fill="#f0f3f6", stroke=LINE, sw=1.5, rx=4))
    f.append(text(p3_x + 95, p3_y + 85, "Вузол A (Джерело)", size=11, bold=True, color=INK))
    f.append(text(p3_x + 95, p3_y + 105, "Пряме заземлення", size=9, bold=True, color=FIELD))
    f.append(text(p3_x + 95, p3_y + 120, "на металеве шасі", size=9, color=MUTED))

    # Корпус Б (Приймач / Давач)
    f.append(rect(p3_x + p3_w - 225, p3_y + 55, 190, 110, fill="#f0f3f6", stroke=LINE, sw=1.5, rx=4))
    f.append(text(p3_x + p3_w - 130, p3_y + 80, "Вузол B (Приймач)", size=11, bold=True, color=INK))
    f.append(text(p3_x + p3_w - 130, p3_y + 98, "Гібридний вузол RC", size=10, bold=True, color=NEG))

    # RC блок всередині Вузла B
    rc_bx, rc_by, rc_bw, rc_bh = p3_x + p3_w - 215, p3_y + 108, 170, 48
    f.append(rect(rc_bx, rc_by, rc_bw, rc_bh, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    f.append(text(rc_bx + rc_bw / 2, rc_by + 16, "C = 10 нФ / 1–3 кВ (ВЧ шлях)", size=9, bold=True, color=NEG))
    f.append(text(rc_bx + rc_bw / 2, rc_by + 32, "R = 1 МОм (стік статики / ESD)", size=9, color=INK))

    # Екран кабелю
    f.append(rect(p3_x + 155, p3_y + 85, p3_w - 380, 50, fill="#e8edf2", stroke="#607d8b", sw=1.5, rx=3))
    f.append(text(p3_x + 155 + (p3_w - 380) / 2, p3_y + 105, "Екран кабелю: суцільне кругове з'єднання 360°", size=10, bold=True, color="#37474f"))
    # Сигнальні жили
    f.append(line(p3_x + 155, p3_y + 120, p3_x + p3_w - 225, p3_y + 120, color=POS, sw=1.8, dash="4,3"))

    # Пояснення режимів частоти
    f.append(text(p3_x + 155 + (p3_w - 380) / 2, p3_y + 70, "• На DC / 50 Гц: X_C ≈ 318 кОм → струм петлі заблоковано (I_LF ≈ 0)", size=9, bold=True, color=FIELD))
    f.append(text(p3_x + 155 + (p3_w - 380) / 2, p3_y + 150, "• На ВЧ (> 10 МГц): X_C < 1.6 Ом → екран ефективно заземлений для RF", size=9, bold=True, color=NEG))

    # Земляні з'єднання
    f.append(line(p3_x + 95, p3_y + 165, p3_x + 95, p3_y + 185, color=LINE, sw=1.5))
    f.append(line(p3_x + 85, p3_y + 185, p3_x + 105, p3_y + 185, color=LINE, sw=2.0))
    f.append(line(p3_x + 89, p3_y + 189, p3_x + 101, p3_y + 189, color=LINE, sw=1.5))
    f.append(line(p3_x + 92, p3_y + 193, p3_x + 98, p3_y + 193, color=LINE, sw=1.2))
    f.append(text(p3_x + 95, p3_y + 206, "PE1 (Шасі A)", size=9, bold=True, color=INK))

    f.append(line(p3_x + p3_w - 130, p3_y + 165, p3_x + p3_w - 130, p3_y + 185, color=LINE, sw=1.5))
    f.append(line(p3_x + p3_w - 140, p3_y + 185, p3_x + p3_w - 120, p3_y + 185, color=LINE, sw=2.0))
    f.append(line(p3_x + p3_w - 136, p3_y + 189, p3_x + p3_w - 124, p3_y + 189, color=LINE, sw=1.5))
    f.append(line(p3_x + p3_w - 133, p3_y + 193, p3_x + p3_w - 127, p3_y + 193, color=LINE, sw=1.2))
    f.append(text(p3_x + p3_w - 130, p3_y + 206, "PE2 (Шасі B)", size=9, bold=True, color=INK))

    out_file = os.path.join(IMG, "ground-loop-shield.svg")
    with open(out_file, "w", encoding="utf-8") as f_out:
        f_out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f_out.write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n' % (W, H, W, H))
        f_out.write(rect(0, 0, W, H, fill=BG, stroke="none") + "\n")
        f_out.write("\n".join(f))
        f_out.write("\n</svg>\n")
    print("Generated:", out_file)


# ════════════════════════════════════════════════════════════════════════════
# 2. hybrid-ground-rc.svg — Схемотехніка та топологія вузла на друкованій платі
# ════════════════════════════════════════════════════════════════════════════
def fig_hybrid_ground_rc():
    W, H = 880, 520
    f = []

    f.append(text(W / 2, 26, "СХЕМОТЕХНІКА ТА ТОПОЛОГІЯ ГІБРИДНОГО ЗАЗЕМЛЕННЯ НА ДРУКОВАНІЙ ПЛАТІ", size=14, bold=True, color=INK))

    # Головна плата (PCB)
    pcb_x, pcb_y, pcb_w, pcb_h = 30, 48, 820, 450
    f.append(rect(pcb_x, pcb_y, pcb_w, pcb_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # Зона 1 (Ліворуч): Металевий корпус / Шасі (Chassis / PE)
    ch_x, ch_y, ch_w, ch_h = 45, 65, 230, 415
    f.append(rect(ch_x, ch_y, ch_w, ch_h, fill="#edf2f7", stroke="#718096", sw=1.5, rx=6))
    f.append(text(ch_x + ch_w / 2, ch_y + 24, "МЕТАЛЕВЕ ШАСІ / КОРПУС", size=12, bold=True, color="#2d3748"))
    f.append(text(ch_x + ch_w / 2, ch_y + 40, "Захисне заземлення (Chassis / PE)", size=10, color=MUTED))

    # Роз'єм кабелю з 360-градусним затискачем
    f.append(rect(ch_x + 15, ch_y + 60, 200, 95, fill="#cbd5e0", stroke="#4a5568", sw=1.5, rx=4))
    f.append(text(ch_x + 115, ch_y + 82, "Кабельний роз'єм (D-Sub / M12)", size=10, bold=True, color=INK))
    f.append(rect(ch_x + 25, ch_y + 92, 180, 26, fill="#a0aec0", stroke="#2d3748", sw=1.2, rx=3))
    f.append(text(ch_x + 115, ch_y + 109, "Круговий 360° контакт екрана", size=9, bold=True, color="#1a202c"))
    f.append(text(ch_x + 115, ch_y + 140, "Ніяких тонких «хвостиків» (Pigtails)!", size=9, bold=True, color=POS))

    # Полігон Chassis Ground на платі
    f.append(rect(ch_x + 15, ch_y + 175, 200, 215, fill="#e2e8f0", stroke="#a0aec0", sw=1.2, rx=4))
    f.append(text(ch_x + 115, ch_y + 195, "Полігон шасі (Chassis Plane)", size=10, bold=True, color="#4a5568"))
    f.append(text(ch_x + 115, ch_y + 212, "Гвинти кріплення до корпусу", size=9, color=MUTED))

    # Символи гвинтів кріплення
    f.append(circle(ch_x + 55, ch_y + 260, 14, fill="#cbd5e0", stroke="#4a5568", sw=1.5))
    f.append(circle(ch_x + 55, ch_y + 260, 6, fill="#ffffff", stroke="#4a5568", sw=1.2))
    f.append(text(ch_x + 55, ch_y + 290, "GND-гвинт", size=9, color=MUTED))

    f.append(circle(ch_x + 175, ch_y + 260, 14, fill="#cbd5e0", stroke="#4a5568", sw=1.5))
    f.append(circle(ch_x + 175, ch_y + 260, 6, fill="#ffffff", stroke="#4a5568", sw=1.2))
    f.append(text(ch_x + 175, ch_y + 290, "GND-гвинт", size=9, color=MUTED))


    # Зона 2 (Посередині): Бар'єр ізоляції та RC+GDT компоненти
    bar_x, bar_y, bar_w, bar_h = 295, 65, 275, 415
    f.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(bar_x + bar_w / 2, bar_y + 24, "ГІБРИДНИЙ БАР'ЄР (RC + SURGE)", size=12, bold=True, color=NEG))
    f.append(text(bar_x + bar_w / 2, bar_y + 40, "Зазор ізоляції: Clearance ≥ 3.0 мм", size=10, color=MUTED))

    # 1. Високовольтний конденсатор C_rf
    c_box_y = bar_y + 60
    f.append(rect(bar_x + 15, c_box_y, bar_w - 30, 75, fill="#f0f7ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(bar_x + bar_w / 2, c_box_y + 20, "C_rf: 10 нФ / 1 кВ – 3 кВ (X7R / C0G)", size=10, bold=True, color=NEG))
    f.append(text(bar_x + bar_w / 2, c_box_y + 36, "• Низький імпеданс для ВЧ струмів (> 1 МГц)", size=9, color=INK))
    f.append(text(bar_x + bar_w / 2, c_box_y + 52, "• ESL < 1.5 нГн (корпус 1206 / 1812)", size=9, color=MUTED))
    f.append(text(bar_x + bar_w / 2, c_box_y + 66, "• Ізолює постійний струм і 50 Гц гул", size=9, color=FIELD))

    # 2. Резистор витоку статики R_bleed
    r_box_y = bar_y + 145
    f.append(rect(bar_x + 15, r_box_y, bar_w - 30, 75, fill="#fffaf0", stroke="#dd6b20", sw=1.2, rx=4))
    f.append(text(bar_x + bar_w / 2, r_box_y + 20, "R_bleed: 1 МОм / 0.5 Вт (High Voltage)", size=10, bold=True, color="#c05621"))
    f.append(text(bar_x + bar_w / 2, r_box_y + 36, "• Скидає трибоелектричний заряд (ESD)", size=9, color=INK))
    f.append(text(bar_x + bar_w / 2, r_box_y + 52, "• Запобігає накопиченню статичного потенціалу", size=9, color=MUTED))
    f.append(text(bar_x + bar_w / 2, r_box_y + 66, "• Опір занадто великий для струму 50 Гц", size=9, color=FIELD))

    # 3. Газорозрядник GDT / Варистор
    g_box_y = bar_y + 230
    f.append(rect(bar_x + 15, g_box_y, bar_w - 30, 75, fill="#fdf2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(bar_x + bar_w / 2, g_box_y + 20, "GDT / Варистор (Surge Protection)", size=10, bold=True, color=POS))
    f.append(text(bar_x + bar_w / 2, g_box_y + 36, "• Газорозрядник 75 В / 90 В або TVS", size=9, color=INK))
    f.append(text(bar_x + bar_w / 2, g_box_y + 52, "• Захист конденсатора від пробою сплеском", size=9, color=MUTED))
    f.append(text(bar_x + bar_w / 2, g_box_y + 66, "• Шунтує енергію блискавки в корпус", size=9, color=POS))

    # Іскровий проміжок (Spark Gap на платі)
    sg_y = bar_y + 315
    f.append(rect(bar_x + 15, sg_y, bar_w - 30, 50, fill="#f7fafc", stroke="#718096", sw=1.0, rx=4))
    f.append(text(bar_x + bar_w / 2, sg_y + 20, "PCB Spark Gap (Іскровий проміжок)", size=9, bold=True, color="#4a5568"))
    f.append(text(bar_x + bar_w / 2, sg_y + 36, "Зазор 0.3–0.5 мм (резервний пробій при >2 кВ)", size=9, color=MUTED))


    # Зона 3 (Праворуч): Сигнальна земля та схема (Signal Ground SGND)
    sg_x, sg_y_pos, sg_w, sg_h = 590, 65, 245, 415
    f.append(rect(sg_x, sg_y_pos, sg_w, sg_h, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(sg_x + sg_w / 2, sg_y_pos + 24, "ВНУТРІШНЯ СХЕМА ТА SGND", size=12, bold=True, color=FIELD))
    f.append(text(sg_x + sg_w / 2, sg_y_pos + 40, "Сигнальна земля (Signal Ground)", size=10, color=MUTED))

    # Сигнальний трансивер
    f.append(rect(sg_x + 20, sg_y_pos + 60, 205, 110, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(sg_x + 122, sg_y_pos + 85, "Трансивер інтерфейсу", size=10, bold=True, color=INK))
    f.append(text(sg_x + 122, sg_y_pos + 102, "(RS-485 / CAN / Ethernet / ADC)", size=9, color=MUTED))
    f.append(rect(sg_x + 35, sg_y_pos + 118, 175, 40, fill="#edf2f7", stroke="#a0aec0", sw=1.0, rx=3))
    f.append(text(sg_x + 122, sg_y_pos + 134, "TVS-діоди ліній на SGND", size=9, bold=True, color="#2b6cb0"))
    f.append(text(sg_x + 122, sg_y_pos + 148, "Гальванічна розв'язка (Opto/ISO)", size=9, color=MUTED))

    # Полігон сигнальної землі
    f.append(rect(sg_x + 20, sg_y_pos + 190, 205, 195, fill="#dcffe4", stroke="#68d391", sw=1.2, rx=4))
    f.append(text(sg_x + 122, sg_y_pos + 215, "Суцільний шар SGND", size=10, bold=True, color="#22543d"))
    f.append(text(sg_x + 122, sg_y_pos + 235, "Чистий опорний потенціал", size=9, color="#276749"))
    f.append(text(sg_x + 122, sg_y_pos + 252, "для цифрових та аналогових вузлів", size=9, color=MUTED))
    f.append(text(sg_x + 122, sg_y_pos + 285, "Ізольований від корпусу на DC,", size=9, color=INK))
    f.append(text(sg_x + 122, sg_y_pos + 300, "зв'язаний на ВЧ через RC-вузол", size=9, bold=True, color=FIELD))

    # З'єднувальні лінії між зонами
    # Від Chassis до RC вузла
    f.append(line(ch_x + ch_w, ch_y + 98, bar_x, bar_y + 98, color="#4a5568", sw=2.0))
    f.append(line(ch_x + ch_w, ch_y + 182, bar_x, bar_y + 182, color="#4a5568", sw=2.0))
    f.append(line(ch_x + ch_w, ch_y + 268, bar_x, bar_y + 268, color="#4a5568", sw=2.0))

    # Від RC вузла до SGND
    f.append(line(bar_x + bar_w, bar_y + 98, sg_x, sg_y_pos + 98, color=FIELD, sw=2.0))
    f.append(line(bar_x + bar_w, bar_y + 182, sg_x, sg_y_pos + 182, color=FIELD, sw=2.0))
    f.append(line(bar_x + bar_w, bar_y + 268, sg_x, sg_y_pos + 268, color=FIELD, sw=2.0))

    out_file = os.path.join(IMG, "hybrid-ground-rc.svg")
    with open(out_file, "w", encoding="utf-8") as f_out:
        f_out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f_out.write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n' % (W, H, W, H))
        f_out.write(rect(0, 0, W, H, fill=BG, stroke="none") + "\n")
        f_out.write("\n".join(f))
        f_out.write("\n</svg>\n")
    print("Generated:", out_file)


if __name__ == "__main__":
    fig_ground_loop_shield()
    fig_hybrid_ground_rc()
