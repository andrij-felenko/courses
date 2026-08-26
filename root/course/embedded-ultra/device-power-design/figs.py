# -*- coding: utf-8 -*-
"""Фігури до теми «Живлення апарата як ціле».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ієрархічне дерево живлення безпілотного апарата ───────────────────────
def fig_power_tree():
    W, H = 940, 580
    f = [text(W / 2, 28, "Ієрархія шин живлення безпілотного апарата: розв'язка силових і чутливих споживачів",
              size=15, bold=True)]

    # 1. Джерело (Батарея) ліворуч
    bx, by, bw, bh = 30, 200, 150, 140
    f.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(bx + bw / 2, by + 28, "LiPo Батарея", size=13, bold=True, color=POS))
    f.append(text(bx + bw / 2, by + 52, "6S (22.2 В – 25.2 В)", size=10.5, color=INK))
    f.append(text(bx + bw / 2, by + 74, "Струм: 0.5 А .. 120 А", size=10, color=MUTED))
    f.append(text(bx + bw / 2, by + 98, "Джерело енергії", size=10, italic=True, color=MUTED))
    f.append(text(bx + bw / 2, by + 120, "та імпульсних шумів", size=9.5, italic=True, color=POS))

    # Вузол захисту та шунта (PDB / Power Module)
    px, py, pw, ph = 220, 200, 160, 140
    f.append(rect(px, py, pw, ph, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=8))
    f.append(text(px + pw / 2, py + 24, "PDB / Монітор", size=12, bold=True, color=INK))
    f.append(text(px + pw / 2, py + 46, "Шунт струму 0.5 мОм", size=10, color=INK))
    f.append(text(px + pw / 2, py + 68, "TVS-супресор (33 В)", size=10, color=POS))
    f.append(text(px + pw / 2, py + 90, "Bulk Low-ESR 1000 мкФ", size=10, color=NEG))
    f.append(text(px + pw / 2, py + 118, "I_sense & V_sense → MCU", size=9.5, italic=True, color=FIELD))

    # Стрілка Батарея -> PDB
    f.append(arrow(bx + bw, by + 70, px, py + 70, color=POS, sw=3))
    f.append(text((bx + bw + px) / 2, by + 58, "VBAT", size=10.5, bold=True, color=POS))

    # Розгалуження на 3 головні гілки
    # Гілка 1: Силова шина ходових двигунів (вгорі праворуч)
    m1x, m1y, m1w, m1h = 440, 60, 200, 100
    f.append(rect(m1x, m1y, m1w, m1h, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(m1x + m1w / 2, m1y + 24, "Силові ESC (4-8 шт)", size=12, bold=True, color=POS))
    f.append(text(m1x + m1w / 2, m1y + 48, "Пряма шина VBAT (24 В)", size=10.5, color=INK))
    f.append(text(m1x + m1w / 2, m1y + 70, "BLDC мотори (до 100 А)", size=10, color=INK))
    f.append(text(m1x + m1w / 2, m1y + 88, "Комутаційний шум 24-48 кГц", size=9, italic=True, color=POS))

    # Гілка 2: Бортова електроніка польотного контролера (посередині)
    b2x, b2y, b2w, b2h = 440, 205, 190, 130
    f.append(rect(b2x, b2y, b2w, b2h, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(b2x + b2w / 2, b2y + 24, "Step-Down BEC (5.3 В)", size=12, bold=True, color=NEG))
    f.append(text(b2x + b2w / 2, b2y + 48, "Синхронний Buck, 3 А", size=10.5, color=INK))
    f.append(text(b2x + b2w / 2, b2y + 70, "Вбудований LC π-фільтр", size=10, color=FIELD))
    f.append(text(b2x + b2w / 2, b2y + 94, "ККД ~92%, стабільна шина", size=9.5, color=INK))
    f.append(text(b2x + b2w / 2, b2y + 114, "Живлення польотного ядра", size=9, italic=True, color=NEG))

    # Гілка 3: Допоміжні споживачі / Сервоприводи / Відео (внизу праворуч)
    b3x, b3y, b3w, b3h = 440, 390, 190, 120
    f.append(rect(b3x, b3y, b3w, b3h, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(b3x + b3w / 2, b3y + 24, "AUX BEC (5.0 В / 12 В)", size=12, bold=True, color=FIELD))
    f.append(text(b3x + b3w / 2, b3y + 48, "Ізольований Buck, 5 А", size=10.5, color=INK))
    f.append(text(b3x + b3w / 2, b3y + 72, "Сервоприводи (кидки струму)", size=9.5, color=INK))
    f.append(text(b3x + b3w / 2, b3y + 92, "FPV-передавач (VTX) та CAM", size=9.5, color=INK))
    f.append(text(b3x + b3w / 2, b3y + 108, "Телеметрія радіо (ELRS/LoRa)", size=9, italic=True, color=MUTED))

    # З'єднання від PDB до 3 гілок
    # До ESC
    f.append(line(px + pw, py + 40, 410, py + 40, color=POS, sw=2.5))
    f.append(line(410, py + 40, 410, m1y + 50, color=POS, sw=2.5))
    f.append(arrow(410, m1y + 50, m1x, m1y + 50, color=POS, sw=2.5))

    # До BEC FC
    f.append(arrow(px + pw, py + 70, b2x, py + 70, color=POS, sw=2))

    # До AUX BEC
    f.append(line(px + pw, py + 100, 410, py + 100, color=POS, sw=2))
    f.append(line(410, py + 100, 410, b3y + 60, color=POS, sw=2))
    f.append(arrow(410, b3y + 60, b3x, b3y + 60, color=POS, sw=2))

    # Кінцеві споживачі від гілки 2 (FC)
    fcx, fcy, fcw, fch = 690, 160, 220, 100
    f.append(rect(fcx, fcy, fcw, fch, fill="#fdf0e6", stroke=LINE, sw=1.6, rx=8))
    f.append(text(fcx + fcw / 2, fcy + 22, "Польотний контролер (FC)", size=11.5, bold=True))
    f.append(text(fcx + fcw / 2, fcy + 44, "MCU STM32H7 (3.3 В LDO)", size=10, color=INK))
    f.append(text(fcx + fcw / 2, fcy + 64, "Flash пам'ять, Барометр", size=10, color=INK))
    f.append(text(fcx + fcw / 2, fcy + 86, "Споживання: ~350 мА", size=9.5, color=MUTED))

    # Окремий прецизійний LDO для IMU / Сенсорів
    imx, imy, imw, imh = 690, 280, 220, 100
    f.append(rect(imx, imy, imw, imh, fill="#fafbfc", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(imx + imw / 2, imy + 22, "Чутливі сенсори (IMU/GNSS)", size=11.5, bold=True, color=FIELD))
    f.append(text(imx + imw / 2, imy + 44, "Ultra-Low-Noise LDO (3.3 В)", size=10, color=INK))
    f.append(text(imx + imw / 2, imy + 64, "MEMS гіроскопи ICM-42688", size=10, color=INK))
    f.append(text(imx + imw / 2, imy + 86, "Шум < 5 мкВ_rms, PSRR > 75 дБ", size=9.5, color=FIELD))

    # Стрілки від BEC до FC та IMU
    f.append(line(b2x + b2w, b2y + 65, 660, b2y + 65, color=NEG, sw=2))
    f.append(line(660, b2y + 65, 660, fcy + 50, color=NEG, sw=2))
    f.append(arrow(660, fcy + 50, fcx, fcy + 50, color=NEG, sw=2))

    f.append(line(660, b2y + 65, 660, imy + 50, color=FIELD, sw=2))
    f.append(arrow(660, imy + 50, imx, imy + 50, color=FIELD, sw=2))

    # Підсумкова плашка
    b, _, _ = textbox(W / 2, H - 32,
                      "Правило побудови: силова шина моторів розв'язана від цифрової логіки через окремі імпульсні ступені (BEC),\n"
                      "а прецизійні аналогові сенсори живляться через каскадні LC-фільтри та Low-Noise LDO.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "power-tree-topology.svg"), W, H, *f)


# ── 2. Проблема зміщення потенціалу землі та зіркова земля ───────────────────
def fig_ground_loop_bounce():
    W, H = 940, 530
    f = [text(W / 2, 28, "Зміщення потенціалу землі (Ground Bounce) та топологія «Зіркова земля»",
              size=15, bold=True)]

    # Ліва половина: Спільна земля (Помилка)
    lx, ly, lw, lh = 30, 56, 420, 410
    f.append(rect(lx, ly, lw, lh, fill="#fff8f8", stroke=POS, sw=1.6, rx=10))
    f.append(text(lx + lw / 2, ly + 24, "НЕПРАВИЛЬНО: спільний провідник землі", size=12.5, bold=True, color=POS))

    # Батарея
    f.append(rect(lx + 20, ly + 50, 80, 65, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(lx + 60, ly + 76, "LiPo", size=11, bold=True))
    f.append(text(lx + 60, ly + 96, "−  GND", size=10, color=NEG))

    # Силовий ESC мотор
    f.append(rect(lx + 290, ly + 50, 100, 65, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(lx + 340, ly + 76, "ESC Мотор", size=11, bold=True))
    f.append(text(lx + 340, ly + 96, "50 А імпульс", size=9.5, color=POS))

    # FC в середині
    f.append(rect(lx + 140, ly + 200, 140, 75, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(lx + 210, ly + 226, "Польотний MCU", size=11, bold=True))
    f.append(text(lx + 210, ly + 246, "GND_mcu", size=10, color=NEG))
    f.append(text(lx + 210, ly + 262, "3.3 В логіка", size=9.5, color=MUTED))

    # Довгий спільний провідник землі зі зворотним струмом (внизу)
    f.append(line(lx + 60, ly + 115, lx + 60, ly + 345, color=NEG, sw=2.5))
    f.append(line(lx + 60, ly + 345, lx + 340, ly + 345, color=NEG, sw=2.5))
    f.append(line(lx + 340, ly + 345, lx + 340, ly + 115, color=NEG, sw=2.5))
    f.append(text(lx + 200, ly + 368, "R_gnd = 15 мОм, L_gnd = 20 нГн", size=9.5, bold=True, color=POS))

    # З'єднання MCU до цієї землі (пряма лінія праворуч від тексту)
    f.append(line(lx + 260, ly + 275, lx + 260, ly + 345, color=NEG, sw=1.8))

    # Стрілка паразитного струму над нижнім дротом
    f.append(arrow(lx + 230, ly + 332, lx + 90, ly + 332, color=POS, sw=2.2))
    f.append(text(lx + 155, ly + 320, "I_motor = 50 А", size=9.5, bold=True, color=POS))

    # Наслідок: зміщення GND
    f.append(text(lx + lw / 2, ly + 145, "ΔV_gnd = I·R + L·(di/dt) ≈ 0.75 В + 2.0 В = 2.75 В!", size=10, bold=True, color=POS))
    f.append(text(lx + lw / 2, ly + 168, "Зсув землі перекидає цифрові рівні 3.3 В та зависає MCU", size=9.5, color=INK))


    # Права половина: Зіркова земля (Правильно)
    rx, ry, rw, rh = 490, 56, 420, 410
    f.append(rect(rx, ry, rw, rh, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(rx + rw / 2, ry + 24, "ПРАВИЛЬНО: топологія «Зіркова земля»", size=12.5, bold=True, color=FIELD))

    # Батарея
    f.append(rect(rx + 20, ry + 50, 80, 65, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(rx + 60, ry + 76, "LiPo", size=11, bold=True))
    f.append(text(rx + 60, ry + 96, "−  GND", size=10, color=NEG))

    # Зіркова точка (Star Point на PDB шунті)
    spx, spy = rx + 160, ry + 180
    f.append(circle(spx, spy, 14, fill="#27ae60", stroke=LINE, sw=2))
    f.append(text(spx, spy + 4, "★", size=14, color=BG, bold=True))
    f.append(text(spx, spy - 20, "Зіркова точка (Star GND)", size=10.5, bold=True, color=FIELD))

    # Силовий ESC мотор праворуч
    f.append(rect(rx + 290, ry + 50, 100, 65, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(rx + 340, ry + 76, "ESC Мотор", size=11, bold=True))
    f.append(text(rx + 340, ry + 96, "50 А імпульс", size=9.5, color=POS))

    # Окремий контур повернення для силовиків
    f.append(line(rx + 60, ry + 115, rx + 60, spy, color=NEG, sw=3))
    f.append(arrow(rx + 60, spy, spx - 14, spy, color=NEG, sw=3))

    f.append(line(spx + 14, spy, rx + 340, spy, color=POS, sw=2.8))
    f.append(line(rx + 340, spy, rx + 340, ry + 115, color=POS, sw=2.8))
    f.append(text(rx + 250, spy - 10, "Силовий зворот (PGND)", size=9.5, bold=True, color=POS))

    # FC внизу
    f.append(rect(rx + 270, ry + 250, 130, 75, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(rx + 335, ry + 276, "Польотний MCU", size=11, bold=True))
    f.append(text(rx + 335, ry + 296, "Чиста сигнальна GND", size=9.5, color=NEG))
    f.append(text(rx + 335, ry + 312, "I_gnd < 50 мА", size=9, color=MUTED))

    # Окремий сигнальний дріт GND від зіркової точки
    f.append(line(spx, spy + 14, spx, ry + 285, color=FIELD, sw=2))
    f.append(arrow(spx, ry + 285, rx + 270, ry + 285, color=FIELD, sw=2))
    f.append(text(spx + 55, ry + 270, "Сигнальний GND (AGND/DGND)", size=9, bold=True, color=FIELD))

    # Результат
    f.append(text(rx + rw / 2, ry + 375, "Силові імпульси замикаються суто по PGND і не чіпають MCU", size=10, bold=True, color=FIELD))

    # Підсумкова плашка
    b, _, _ = textbox(W / 2, H - 28,
                      "Зіркова топологія зводить силові повернення моторів (PGND) та сигнальні повернення чутливої логіки (DGND/AGND)\n"
                      "в єдину фізичну точку біля мінуса батареї, усуваючи паразитні зсуви напруги.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "ground-loop-bounce.svg"), W, H, *f)


# ── 3. Графік просідання напруги батареї (Sag) та компенсація ────────────────
def fig_voltage_sag_and_filter():
    W, H = 940, 520
    f = [text(W / 2, 28, "Просідання напруги (Battery Sag) під навантаженням та динамічна компенсація",
              size=15, bold=True)]

    # Вісь часу
    gx, gy, gw, gh = 80, 70, 780, 360
    f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))

    # Горизонтальні лінії сітки (рівні напруги)
    levels = [
        (gy + 35, "4.2 В/ком (Повний заряд)", MUTED),
        (gy + 90, "3.8 В/ком (Поточна OCV)", FIELD),
        (gy + 200, "3.3 В/ком (Поріг Low-Battery)", POS),
        (gy + 280, "3.0 В/ком (Критичний Brownout)", POS),
    ]
    for y_pos, label, col in levels:
        f.append(line(gx, y_pos, gx + gw, y_pos, color=col, sw=1, dash="4 4"))
        f.append(text(gx + 12, y_pos - 6, label, size=9.5, color=col, anchor="start", bold=True))

    # Струм мотора (синій імпульс унизу)
    cur_y_base = gy + gh - 20
    f.append(text(gx + 14, cur_y_base - 50, "Струм моторів I_load (А):", size=10, bold=True, color=NEG, anchor="start"))

    # Полілінія струму
    c_pts = [
        (gx + 40, cur_y_base - 10),
        (gx + 180, cur_y_base - 10),
        (gx + 195, cur_y_base - 65),
        (gx + 480, cur_y_base - 65),
        (gx + 500, cur_y_base - 25),
        (gx + 740, cur_y_base - 25),
    ]
    for i in range(len(c_pts) - 1):
        f.append(line(c_pts[i][0], c_pts[i][1], c_pts[i+1][0], c_pts[i+1][1], color=NEG, sw=2.2))
    f.append(text(gx + 110, cur_y_base - 16, "5 А (круїз)", size=9, color=NEG))
    f.append(text(gx + 330, cur_y_base - 72, "80 А (максимальний газ)", size=10, bold=True, color=NEG))
    f.append(text(gx + 620, cur_y_base - 31, "20 А", size=9, color=NEG))

    # 1. Сирий вимір на клемах з шумом (червона ламана крива)
    raw_pts = [
        (gx + 40, gy + 94), (gx + 80, gy + 96), (gx + 120, gy + 93), (gx + 160, gy + 95), (gx + 180, gy + 96),
        (gx + 195, gy + 225), (gx + 220, gy + 240), (gx + 250, gy + 215), (gx + 280, gy + 245),
        (gx + 320, gy + 210), (gx + 360, gy + 242), (gx + 400, gy + 212), (gx + 440, gy + 238), (gx + 480, gy + 220),
        (gx + 500, gy + 122), (gx + 550, gy + 126), (gx + 600, gy + 121), (gx + 660, gy + 125), (gx + 740, gy + 123)
    ]
    for i in range(len(raw_pts) - 1):
        f.append(line(raw_pts[i][0], raw_pts[i][1], raw_pts[i+1][0], raw_pts[i+1][1], color=POS, sw=1.5))
    f.append(text(gx + 330, gy + 260, "Сира напруга клем (провалюється під поріг 3.3 В)", size=9.5, bold=True, color=POS))

    # 2. Фільтрована напруга EMA (помаранчева плавна крива)
    ema_pts = [
        (gx + 40, gy + 95), (gx + 180, gy + 95),
        (gx + 205, gy + 228), (gx + 480, gy + 228),
        (gx + 505, gy + 124), (gx + 740, gy + 124)
    ]
    for i in range(len(ema_pts) - 1):
        f.append(line(ema_pts[i][0], ema_pts[i][1], ema_pts[i+1][0], ema_pts[i+1][1], color="#e67e22", sw=2.2, dash="5 3"))

    # 3. Динамічно скомпенсована OCV (зелена стабільна крива)
    ocv_pts = [
        (gx + 40, gy + 92), (gx + 180, gy + 92),
        (gx + 210, gy + 98), (gx + 480, gy + 104),
        (gx + 510, gy + 108), (gx + 740, gy + 112)
    ]
    for i in range(len(ocv_pts) - 1):
        f.append(line(ocv_pts[i][0], ocv_pts[i][1], ocv_pts[i+1][0], ocv_pts[i+1][1], color=FIELD, sw=2.8))
    f.append(text(gx + 330, gy + 82, "Скомпенсована напруга OCV = V_meas + I·R_int (істинний заряд)", size=10, bold=True, color=FIELD))

    # Підсумкова плашка
    b, _, _ = textbox(W / 2, H - 30,
                      "Без компенсації просідання I·R_int різкий маневр викликає фальшиве спрацьовування захисту Low-Battery;\n"
                      "алгоритмічна оцінка OCV дозволяє відрізнити реальне виснаження батареї від тимчасового імпульсного навантаження.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "voltage-sag-and-filter.svg"), W, H, *f)


# ── 4. Каскад триступеневої фільтрації шумів ─────────────────────────────────
def fig_cascade_filtering():
    W, H = 940, 520
    f = [text(W / 2, 28, "Триступенева фільтрація завад: від силової шини до прецизійного сенсора",
              size=15, bold=True)]

    # Ступінь 1: Вхідний демпфер (Bulk Cap + TVS)
    s1x, s1y, s1w, s1h = 40, 70, 260, 200
    f.append(rect(s1x, s1y, s1w, s1h, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(s1x + s1w / 2, s1y + 24, "Ступінь 1: Силовий демпфер", size=12, bold=True, color=POS))
    f.append(text(s1x + s1w / 2, s1y + 50, "Вхідна шина VBAT (24 В)", size=10.5, color=INK))
    f.append(text(s1x + s1w / 2, s1y + 74, "1. Low-ESR 1000 мкФ 50 В", size=10, color=INK))
    f.append(text(s1x + s1w / 2, s1y + 96, "2. TVS-діод SMAJ33A (33 В)", size=10, color=INK))
    f.append(text(s1x + s1w / 2, s1y + 122, "Гасить індуктивні викиди", size=9.5, italic=True, color=MUTED))
    f.append(text(s1x + s1w / 2, s1y + 140, "від гальмування моторів (>35 В)", size=9.5, italic=True, color=POS))
    f.append(text(s1x + s1w / 2, s1y + 175, "Залишкові пульсації: ~1.5 В", size=10, bold=True, color=POS))

    # Ступінь 2: Імпульсний Step-Down (BEC)
    s2x, s2y, s2w, s2h = 340, 70, 260, 200
    f.append(rect(s2x, s2y, s2w, s2h, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(s2x + s2w / 2, s2y + 24, "Ступінь 2: Синхронний Buck", size=12, bold=True, color=NEG))
    f.append(text(s2x + s2w / 2, s2y + 50, "Проміжна шина 5.3 В (3 А)", size=10.5, color=INK))
    f.append(text(s2x + s2w / 2, s2y + 74, "1. Екранований дросель 4.7 мкГн", size=10, color=INK))
    f.append(text(s2x + s2w / 2, s2y + 96, "2. MLCC кераміка 2×22 мкФ", size=10, color=INK))
    f.append(text(s2x + s2w / 2, s2y + 122, "Високий ККД перетворення 92%", size=9.5, italic=True, color=MUTED))
    f.append(text(s2x + s2w / 2, s2y + 140, "Частота комутації 500 кГц", size=9.5, italic=True, color=NEG))
    f.append(text(s2x + s2w / 2, s2y + 175, "Пульсації комутації: ~30 мВ", size=10, bold=True, color=NEG))

    # Ступінь 3: LC π-фільтр + Ultra-Low-Noise LDO
    s3x, s3y, s3w, s3h = 640, 70, 260, 200
    f.append(rect(s3x, s3y, s3w, s3h, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(s3x + s3w / 2, s3y + 24, "Ступінь 3: LC-фільтр + LDO", size=12, bold=True, color=FIELD))
    f.append(text(s3x + s3w / 2, s3y + 50, "Аналогова шина VDDA (3.3 В)", size=10.5, color=INK))
    f.append(text(s3x + s3w / 2, s3y + 74, "1. Феритова намистина 600 Ом", size=10, color=INK))
    f.append(text(s3x + s3w / 2, s3y + 96, "2. LDO TPS7A20 (PSRR 85 дБ)", size=10, color=INK))
    f.append(text(s3x + s3w / 2, s3y + 122, "Зрізає високочастотний дзвон", size=9.5, italic=True, color=MUTED))
    f.append(text(s3x + s3w / 2, s3y + 140, "Живить IMU гіроскопи та АЦП", size=9.5, italic=True, color=FIELD))
    f.append(text(s3x + s3w / 2, s3y + 175, "Залишковий шум: < 5 мкВ_rms", size=10, bold=True, color=FIELD))

    # Стрілки передачі між ступенями
    f.append(arrow(s1x + s1w, s1y + 100, s2x, s2y + 100, color=INK, sw=2.2))
    f.append(arrow(s2x + s2w, s2y + 100, s3x, s3y + 100, color=INK, sw=2.2))

    # Спектральні ілюстрації внизу
    sp_y = 300
    f.append(rect(40, sp_y, 860, 140, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, sp_y + 24, "Спектр шуму на кожному етапі фільтрації", size=12, bold=True, color=INK))

    # Ділянка 1
    f.append(text(170, sp_y + 54, "Шина VBAT: сплески ±5 В", size=10, bold=True, color=POS))
    f.append(text(170, sp_y + 74, "Широкосмуговий індуктивний шум,", size=9.5, color=INK))
    f.append(text(170, sp_y + 92, "гармоніки ШІМ 24-48 кГц", size=9.5, color=MUTED))
    f.append(text(170, sp_y + 114, "Рівень шуму: ВЕЛИКИЙ", size=9.5, bold=True, color=POS))

    # Ділянка 2
    f.append(text(470, sp_y + 54, "Шина 5.3 В: пульсації ~30 мВ", size=10, bold=True, color=NEG))
    f.append(text(470, sp_y + 74, "Вузький пік комутації на 500 кГц,", size=9.5, color=INK))
    f.append(text(470, sp_y + 92, "низькочастотний дрейф відфільтровано", size=9.5, color=MUTED))
    f.append(text(470, sp_y + 114, "Рівень шуму: ПОМІРНИЙ", size=9.5, bold=True, color=NEG))

    # Ділянка 3
    f.append(text(770, sp_y + 54, "Шина 3.3 В: шум < 5 мкВ", size=10, bold=True, color=FIELD))
    f.append(text(770, sp_y + 74, "Ідеально гладка постійна напруга,", size=9.5, color=INK))
    f.append(text(770, sp_y + 92, "відсутність фальшивих кутових швидкостей", size=9.5, color=MUTED))
    f.append(text(770, sp_y + 114, "Рівень шуму: УЛЬТРАЧИСТИЙ", size=9.5, bold=True, color=FIELD))

    # Підсумкова плашка
    b, _, _ = textbox(W / 2, H - 28,
                      "Послідовне каскадування «Демпфер → Buck → LC-фільтр → LDO» знижує амплітуду завад на 120 дБ (у мільйон разів),\n"
                      "гарантуючи стабільність навігаційних гіроскопів навіть при максимальній тязі двигунів.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "cascade-filtering-stages.svg"), W, H, *f)


if __name__ == "__main__":
    fig_power_tree()
    fig_ground_loop_bounce()
    fig_voltage_sag_and_filter()
    fig_cascade_filtering()
    print("All figures generated successfully.")
