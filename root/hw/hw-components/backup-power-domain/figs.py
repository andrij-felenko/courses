# -*- coding: utf-8 -*-
"""Фігури до статті «Домен резервного живлення (VBAT)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os, math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── 1. Архітектура домену резервного живлення MCU ─────────────────────────────
def fig_vbat_architecture():
    W, H = 880, 520
    f = [
        text(W / 2, 28, "Архітектура домену резервного живлення (VBAT) у мікроконтролері", size=16, bold=True),
        text(W / 2, 48, "Ізольований острів кремнію, комутатор живлення та канали міждоменної розв'язки", size=12, color=MUTED, italic=True)
    ]

    # Зовнішня рамка кристала MCU
    f.append(rect(40, 68, 800, 430, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    f.append(text(60, 92, "Кристал мікроконтролера (MCU Die)", size=13, bold=True, color=MUTED, anchor="start"))

    # Домен основного живлення VDD (ліва область)
    f.append(rect(60, 110, 290, 365, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(205, 134, "Основний домен живлення (VDD / VCORE)", size=12.5, bold=True, color=INK))
    
    # Блоки всередині VDD
    b1, _, _ = textbox(205, 175, "Процесорне ядро (CPU)\nCortex-M / RISC-V", size=11.5, fill="#e2e8f0", stroke="#64748b", pad=8)
    b2, _, _ = textbox(205, 235, "Системна шина AHB/APB\nта контролер переривань NVIC", size=11.5, fill="#e2e8f0", stroke="#64748b", pad=8)
    b3, _, _ = textbox(205, 295, "Основна Flash-пам'ять\nта SRAM загального призначення", size=11.5, fill="#e2e8f0", stroke="#64748b", pad=8)
    b4, _, _ = textbox(205, 360, "Периферія: АЦП (ADC),\nТаймери, SPI, I2C, UART", size=11.5, fill="#e2e8f0", stroke="#64748b", pad=8)
    b5, _, _ = textbox(205, 430, "Модуль керування живленням (PWR)\nРегістри доступу DBP та PVD/BOR", size=11, fill="#e2e8f0", stroke="#64748b", pad=8)
    f.extend([b1, b2, b3, b4, b5])

    # Зона ізоляції (Ізоляційні комірки та Level Shifters)
    f.append(rect(370, 110, 90, 365, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(415, 134, "Бар'єр", size=12, bold=True, color="#b45309"))
    f.append(text(415, 150, "ізоляції", size=12, bold=True, color="#b45309"))
    
    # Елементи бар'єру
    iso1, _, _ = textbox(415, 210, "Level\nShifter", size=10, fill="#fde68a", stroke="#d97706", pad=5)
    iso2, _, _ = textbox(415, 280, "Isolation\nCells (AND)", size=10, fill="#fde68a", stroke="#d97706", pad=5)
    iso3, _, _ = textbox(415, 350, "Tamper\nFilter", size=10, fill="#fde68a", stroke="#d97706", pad=5)
    iso4, _, _ = textbox(415, 420, "DBP Write\nLock", size=10, fill="#fde68a", stroke="#d97706", pad=5)
    f.extend([iso1, iso2, iso3, iso4])

    # Домен резервного живлення VBAT (права область)
    f.append(rect(480, 110, 340, 365, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    f.append(text(650, 134, "Домен резервного живлення (Backup Domain)", size=12.5, bold=True, color=FIELD))

    # Внутрішній комутатор живлення (Power Switch)
    psw_box, _, _ = textbox(650, 185, "Апаратний комутатор живлення (Power Switch)\nКомпаратор порогу VDD/VBAT + захист від витоку", size=11, fill="#dcfce7", stroke=FIELD, pad=8)
    f.append(psw_box)

    # Функціональні блоки Backup домену
    bkp1, _, _ = textbox(570, 260, "Годинник реального часу\nRTC Core + Calendar BCD", size=11, fill="#bbf7d0", stroke=FIELD, pad=7)
    bkp2, _, _ = textbox(730, 260, "Генератор LSE 32.768 кГц\nPierce Oscillator (<150 нА)", size=11, fill="#bbf7d0", stroke=FIELD, pad=7)
    bkp3, _, _ = textbox(570, 340, "Backup SRAM (2..4 КБ)\nRetention Ultra-Low Leakage", size=11, fill="#bbf7d0", stroke=FIELD, pad=7)
    bkp4, _, _ = textbox(730, 340, "Резервні регістри (BKP)\n20..32 x 32-bit Registers", size=11, fill="#bbf7d0", stroke=FIELD, pad=7)
    bkp5, _, _ = textbox(650, 420, "Контролер Tamper / Timestamping\nМиттєве стирання ключів при відкритті корпусу", size=10.5, fill="#bbf7d0", stroke=FIELD, pad=7)
    f.extend([bkp1, bkp2, bkp3, bkp4, bkp5])

    # Зовнішні піни
    # Пін VDD
    f.append(circle(20, 200, 7, fill="#ef4444", stroke=LINE, sw=1.5))
    f.append(text(15, 185, "VDD (3.3V)", size=11, bold=True, color=POS, anchor="start"))
    f.append(arrow(27, 200, 60, 200, color=POS, sw=2))

    # Пін VBAT
    f.append(circle(860, 185, 7, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(text(865, 170, "VBAT (CR2032)", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(arrow(853, 185, 800, 185, color=FIELD, sw=2))

    # Піни OSC32_IN / OSC32_OUT
    f.append(circle(860, 260, 6, fill="#60a5fa", stroke=LINE, sw=1.5))
    f.append(text(865, 248, "OSC32_IN/OUT", size=10.5, color=NEG, anchor="end"))
    f.append(line(800, 260, 854, 260, color=NEG, sw=1.5))

    # Пін TAMPER
    f.append(circle(860, 420, 6, fill="#f59e0b", stroke=LINE, sw=1.5))
    f.append(text(865, 408, "TAMP_IN", size=10.5, color="#d97706", anchor="end"))
    f.append(line(800, 420, 854, 420, color="#d97706", sw=1.5))

    # Шина живлення від Power Switch до блоків домену
    f.append(arrow(650, 215, 650, 235, color=FIELD, sw=2))
    f.append(line(570, 235, 730, 235, color=FIELD, sw=2))
    f.append(arrow(570, 235, 570, 242, color=FIELD, sw=2))
    f.append(arrow(730, 235, 730, 242, color=FIELD, sw=2))

    render(os.path.join(IMG, 'vbat-internal-architecture.svg'), W, H, *f)


# ── 2. Схемотехніка внутрішнього комутатора Power Switch ─────────────────────
def fig_power_switch_topology():
    W, H = 880, 460
    f = [
        text(W / 2, 28, "Топологія комутатора живлення (Power Switch) із захистом від зворотного струму", size=16, bold=True),
        text(W / 2, 48, "Зустрічно-увімкнені P-MOSFET усувають провідність паразитних діодів підкладки", size=12, color=MUTED, italic=True)
    ]

    # Рамка комутатора
    f.append(rect(40, 70, 800, 365, fill="#fbfcfe", stroke="#cbd5e1", sw=1.5, rx=8))

    # Ліва шина VDD
    f.append(line(60, 150, 160, 150, color=POS, sw=2.5))
    f.append(circle(60, 150, 5, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(60, 135, "Шина VDD (3.3 В)", size=12, bold=True, color=POS, anchor="start"))

    # Права шина VBAT
    f.append(line(60, 350, 160, 350, color=FIELD, sw=2.5))
    f.append(circle(60, 350, 5, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(text(60, 335, "Пін VBAT (2.0..3.3 В)", size=12, bold=True, color=FIELD, anchor="start"))

    # Блок компаратора напруги та схеми гістерезису
    comp_box, _, _ = textbox(250, 250, "Прецизійний аналоговий\nкомпаратор + гістерезис\nΔV = 50..100 мВ\n(V_threshold ≈ POR/PVD)", size=11, fill="#f1f5f9", stroke="#64748b", pad=8)
    f.append(comp_box)

    # Зв'язки від VDD та VBAT до компаратора
    f.append(line(120, 150, 120, 225, color=POS, sw=1.5, dash="4 3"))
    f.append(arrow(120, 225, 170, 225, color=POS, sw=1.5))
    f.append(line(120, 350, 120, 275, color=FIELD, sw=1.5, dash="4 3"))
    f.append(arrow(120, 275, 170, 275, color=FIELD, sw=1.5))

    # Логіка керування комутацією (Break-Before-Make Control)
    bbm_box, _, _ = textbox(440, 250, "Логіка неперекривного\nкерування затворами\n(Break-Before-Make)\nt_dead ≈ 15..30 нс", size=11, fill="#fef3c7", stroke="#d97706", pad=8)
    f.append(bbm_box)
    f.append(arrow(330, 250, 365, 250, color=LINE, sw=2))

    # Верхня гілка комутації VDD (зустрічні P-MOSFET Q1, Q2)
    f.append(rect(540, 110, 170, 80, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    f.append(text(625, 130, "Ключ VDD (Back-to-Back)", size=10.5, bold=True, color=POS))
    f.append(text(625, 150, "P-MOSFET Q1 + Q2", size=11, bold=True, color=INK))
    f.append(text(625, 170, "Тіло-до-тіла (Body Switch)", size=9.5, color=MUTED))

    # Нижня гілка комутації VBAT (зустрічні P-MOSFET Q3, Q4)
    f.append(rect(540, 310, 170, 80, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(625, 330, "Ключ VBAT (Back-to-Back)", size=10.5, bold=True, color=FIELD))
    f.append(text(625, 350, "P-MOSFET Q3 + Q4", size=11, bold=True, color=INK))
    f.append(text(625, 370, "Блокування витоку у VDD", size=9.5, color=MUTED))

    # З'єднання від VDD/VBAT до ключів
    f.append(arrow(160, 150, 540, 150, color=POS, sw=2))
    f.append(arrow(160, 350, 540, 350, color=FIELD, sw=2))

    # З'єднання від BBM до затворів
    f.append(line(440, 210, 440, 170, color="#d97706", sw=1.5))
    f.append(arrow(440, 170, 540, 170, color="#d97706", sw=1.5))
    f.append(text(485, 160, "Gate_VDD", size=9.5, bold=True, color="#d97706"))

    f.append(line(440, 290, 440, 330, color="#d97706", sw=1.5))
    f.append(arrow(440, 330, 540, 330, color="#d97706", sw=1.5))
    f.append(text(485, 345, "Gate_VBAT", size=9.5, bold=True, color="#d97706"))

    # Вихідна шина живлення V_BACKUP
    f.append(line(710, 150, 770, 150, color=POS, sw=2))
    f.append(line(710, 350, 770, 350, color=FIELD, sw=2))
    f.append(line(770, 150, 770, 350, color=LINE, sw=2))
    f.append(circle(770, 250, 5, fill=INK, stroke=LINE, sw=1.5))
    f.append(arrow(770, 250, 820, 250, color=LINE, sw=2.5))

    f.append(text(825, 240, "Внутрішня шина", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(825, 258, "V_BACKUP", size=12.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(825, 275, "(живлення RTC/LSE/SRAM)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'power-switch-transistor-topology.svg'), W, H, *f)


# ── 3. Осцилограми перемикання VDD -> VBAT та поведінка при дребезгу ───────────
def fig_vbat_switching_waveforms():
    W, H = 880, 480
    f = [
        text(W / 2, 28, "Перехідний процес комутатора живлення: зникнення та відновлення VDD", size=16, bold=True),
        text(W / 2, 48, "Безперервність напруги V_BACKUP та тактового сигналу LSE під час аварії основного живлення", size=12, color=MUTED, italic=True)
    ]

    # Координатні осі та часова шкала
    L, R = 80, 820
    f.append(line(L, 90, L, 420, color=LINE, sw=1.5))
    f.append(line(L, 420, R, 420, color=LINE, sw=1.5))
    f.append(text(R + 5, 424, "Час (t) →", size=12, bold=True, color=INK, anchor="start"))

    # Рівні напруги
    y_3v3 = 130
    y_3v0 = 160
    y_por = 230
    y_0v0 = 280

    f.append(line(L, y_3v3, R, y_3v3, color="#e2e8f0", sw=1, dash="4 4"))
    f.append(text(L - 8, y_3v3 + 4, "3.3 В (VDD)", size=10.5, color=POS, anchor="end"))

    f.append(line(L, y_3v0, R, y_3v0, color="#e2e8f0", sw=1, dash="4 4"))
    f.append(text(L - 8, y_3v0 + 4, "3.0 В (VBAT)", size=10.5, color=FIELD, anchor="end"))

    f.append(line(L, y_por, R, y_por, color="#fed7aa", sw=1.2, dash="5 4"))
    f.append(text(L - 8, y_por + 4, "2.0 В (V_SW_TH)", size=10.5, color="#ea580c", bold=True, anchor="end"))

    f.append(line(L, y_0v0, R, y_0v0, color="#cbd5e1", sw=1))
    f.append(text(L - 8, y_0v0 + 4, "0.0 В (GND)", size=10.5, color=MUTED, anchor="end"))

    # Часові зони (вертикальні маркери)
    t_fail = 250
    t_switch = 360
    t_rec = 580
    t_swback = 670

    f.append(line(t_fail, 90, t_fail, 420, color="#cbd5e1", sw=1, dash="3 3"))
    f.append(text(t_fail, 105, "Аварія VDD", size=10, color=POS))

    f.append(line(t_switch, 90, t_switch, 420, color="#f97316", sw=1.2, dash="3 3"))
    f.append(text(t_switch, 105, "Спрацювання SW", size=10, bold=True, color="#ea580c"))

    f.append(line(t_rec, 90, t_rec, 420, color="#cbd5e1", sw=1, dash="3 3"))
    f.append(text(t_rec, 105, "Повернення VDD", size=10, color=POS))

    f.append(line(t_swback, 90, t_swback, 420, color="#10b981", sw=1.2, dash="3 3"))
    f.append(text(t_swback, 105, "Перехід на VDD", size=10, bold=True, color=FIELD))

    # Графік 1: Напруга VDD (червона лінія)
    pts_vdd = [
        (L, y_3v3), (t_fail, y_3v3), (t_switch, y_por), (440, y_0v0), (t_rec, y_0v0),
        (630, y_por), (t_swback, y_3v3 - 10), (740, y_3v3), (R, y_3v3)
    ]
    p_vdd = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_vdd)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_vdd, POS))
    f.append(text(180, y_3v3 - 8, "VDD (основне живлення)", size=11, bold=True, color=POS))

    # Графік 2: Напруга VBAT (зелена пунктирна лінія 3.0 В)
    f.append(line(L, y_3v0, R, y_3v0, color=FIELD, sw=1.8, dash="6 3"))
    f.append(text(180, y_3v0 + 15, "VBAT (батарея CR2032)", size=10.5, color=FIELD))

    # Графік 3: Внутрішня напруга V_BACKUP (жирна суцільна синя лінія)
    pts_vbk = [
        (L, y_3v3 + 1), (t_fail, y_3v3 + 1), (t_switch, y_3v0 + 4), (t_switch + 5, y_3v0),
        (t_swback, y_3v0), (t_swback + 10, y_3v3 + 1), (R, y_3v3 + 1)
    ]
    p_vbk = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_vbk)
    f.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>' % p_vbk)
    f.append(text(480, y_3v0 - 10, "V_BACKUP (внутрішня шина домену RTC)", size=11.5, bold=True, color="#2563eb"))

    # Графік 4: Тактовий сигнал LSE 32.768 кГц (нижня панель)
    y_clk_top = 340
    y_clk_bot = 380
    f.append(text(L - 8, 360, "LSE 32.768k\nCLK Output", size=10, color=INK, anchor="end"))
    f.append(line(L, y_clk_top, R, y_clk_top, color="#f1f5f9", sw=1))
    f.append(line(L, y_clk_bot, R, y_clk_bot, color="#f1f5f9", sw=1))

    # Меандр без зриву
    clk_pts = []
    step = 12
    high = True
    curr_x = L + 10
    while curr_x < R - 10:
        y_val = y_clk_top if high else y_clk_bot
        clk_pts.append((curr_x, y_val))
        curr_x += step
        clk_pts.append((curr_x, y_val))
        high = not high
    p_clk = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in clk_pts)
    f.append('<path d="%s" fill="none" stroke="#059669" stroke-width="1.8"/>' % p_clk)
    f.append(text(480, 405, "Неперервна генерація LSE: жодного втраченого такту чи скидання RTC", size=11, bold=True, color="#059669"))

    render(os.path.join(IMG, 'vbat-switching-waveforms.svg'), W, H, *f)


# ── 4. Порівняння розряду CR2032 проти Суперконденсатора ────────────────────
def fig_supercap_vs_cr2032():
    W, H = 880, 460
    f = [
        text(W / 2, 28, "Порівняння профілю розряду: батарея CR2032 проти іоністора 0.47 Ф", size=16, bold=True),
        text(W / 2, 48, "Пологе хімічне плато Li/MnO2 (роки) проти експоненційного розряду EDLC (години/дні)", size=12, color=MUTED, italic=True)
    ]

    # Координатні осі
    L, R = 90, 810
    T, B = 90, 390
    f.append(line(L, T - 10, L, B, color=LINE, sw=1.8))
    f.append(line(L, B, R + 10, B, color=LINE, sw=1.8))
    f.append(text(L - 10, T - 5, "Напруга (В)", size=12, bold=True, color=INK, anchor="end"))
    f.append(text(R + 10, B + 22, "Час автономності →", size=12, bold=True, color=INK, anchor="end"))

    # Горизонтальні лінії рівнів напруги
    def Y(v):
        return B - (v / 3.5) * (B - T)

    v_levels = [(3.3, "3.3 В (VDD max)"), (3.0, "3.0 В (Номінал Li/MnO2)"), (2.0, "2.0 В (Поріг зупинки RTC/LSE)")]
    for v, label in v_levels:
        y_val = Y(v)
        f.append(line(L, y_val, R, y_val, color="#e2e8f0", sw=1, dash="4 4"))
        f.append(text(L - 8, y_val + 4, label, size=10.5, color=MUTED if v != 2.0 else POS, bold=(v == 2.0), anchor="end"))

    # Червона зона нижче 2.0 В
    f.append(rect(L + 1, Y(2.0), R - L - 1, B - Y(2.0), fill="#fee2e2", stroke="none"))
    f.append(text(L + 160, B - 25, "Зона непрацездатності RTC та втрати даних Backup SRAM (< 2.0 В)", size=11, color=POS, bold=True))

    # Графік CR2032
    pts_cr = [
        (L, Y(3.2)), (L + 60, Y(3.0)), (L + 300, Y(2.9)), (L + 550, Y(2.8)),
        (L + 680, Y(2.7)), (L + 730, Y(2.5)), (L + 760, Y(2.0)), (L + 780, Y(1.5))
    ]
    p_cr = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_cr)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (p_cr, FIELD))
    f.append(text(L + 260, Y(2.9) - 14, "Батарея CR2032 (220 мА·год) → 10..15 РОКІВ", size=11.5, bold=True, color=FIELD))

    # Графік Суперконденсатора (EDLC 0.47 Ф)
    pts_sc = [
        (L, Y(3.3)), (L + 40, Y(3.0)), (L + 90, Y(2.7)), (L + 150, Y(2.4)),
        (L + 210, Y(2.15)), (L + 250, Y(2.0)), (L + 310, Y(1.6)), (L + 380, Y(1.0))
    ]
    p_sc = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_sc)
    f.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="6 3"/>' % p_sc)
    f.append(text(L + 130, Y(2.4) - 15, "Іоністор 0.47 Ф → 3..5 ДНІВ", size=11.5, bold=True, color="#2563eb"))

    # Пояснювальні плашки
    b_cr, _, _ = textbox(670, 140, "CR2032:\n• Питома ємність ~700 Дж\n• Саморозряд <1% / рік\n• Заборона підзарядки\n• Строк служби 8..12 років", size=9.5, fill="#f0fdf4", stroke=FIELD, pad=5)
    b_sc, _, _ = textbox(300, 310, "Суперконденсатор (EDLC):\n• Ресурс >500 000 циклів\n• Струм витоку 1..3 мкА\n• Потребує Trickle Charge\n• Автономність на дні/тижні", size=9.5, fill="#eff6ff", stroke="#2563eb", pad=5)
    f.extend([b_cr, b_sc])

    render(os.path.join(IMG, 'supercap-vs-cr2032-discharge.svg'), W, H, *f)


# ── 5. Повна принципова схема вузла VBAT на платі ───────────────────────────
def fig_vbat_complete_schematic():
    W, H = 880, 520
    f = [
        text(W / 2, 28, "Принципова схемотехніка вузла VBAT та кварцового резонатора LSE на PCB", size=16, bold=True),
        text(W / 2, 48, "Захист від зворотного струму, фільтрація завад, охоронне кільце (Guard Ring) та діагностика", size=12, color=MUTED, italic=True)
    ]

    # Корпус мікроконтролера (MCU) - права частина
    f.append(rect(480, 80, 360, 410, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    f.append(text(660, 108, "Мікроконтролер (MCU / SoC)", size=14, bold=True, color=INK))

    # Піни MCU
    # Пін 1: VBAT
    f.append(rect(480, 160, 70, 30, fill="#dcfce7", stroke=FIELD, sw=1.5))
    f.append(text(515, 180, "VBAT", size=12, bold=True, color=FIELD))

    # Пін 2: OSC32_IN
    f.append(rect(480, 260, 90, 28, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    f.append(text(525, 278, "OSC32_IN", size=11, bold=True, color="#0284c7"))

    # Пін 3: OSC32_OUT
    f.append(rect(480, 330, 95, 28, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    f.append(text(527, 348, "OSC32_OUT", size=11, bold=True, color="#0284c7"))

    # Пін 4: VDD
    f.append(rect(480, 430, 70, 30, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(515, 450, "VDD", size=12, bold=True, color=POS))

    # Внутрішній дільник АЦП у MCU
    f.append(rect(600, 150, 220, 90, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(710, 172, "Внутрішній міст АЦП", size=11, bold=True, color=INK))
    f.append(text(710, 192, "Ключ VBATEN + Дільник 1/3 (1/4)", size=10, color=MUTED))
    f.append(text(710, 212, "До вхідного каналу ADC_INx", size=10, color="#2563eb", bold=True))
    f.append(arrow(550, 175, 600, 175, color=FIELD, sw=1.8))

    # Внутрішній генератор LSE
    f.append(rect(600, 275, 220, 75, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=4))
    f.append(text(710, 300, "Pierce Inverter (LSE)", size=11, bold=True, color="#0284c7"))
    f.append(text(710, 320, "Регульований gm (<150 нА)", size=10, color=MUTED))
    f.append(line(570, 274, 600, 274, color="#0284c7", sw=1.5))
    f.append(line(575, 344, 600, 344, color="#0284c7", sw=1.5))

    # ── Зовнішнє коло живлення VBAT (Ліва верхня частина) ──────────────────────
    # Джерело: Батарея CR2032
    f.append(circle(80, 175, 24, fill="#f0fdf4", stroke=FIELD, sw=2))
    f.append(text(80, 170, "BT1", size=11, bold=True, color=FIELD))
    f.append(text(80, 186, "CR2032", size=9.5, color=INK))
    f.append(text(80, 214, "+3.0 В", size=10, bold=True, color=FIELD))
    # Земля батареї
    f.append(line(80, 199, 80, 230, color=LINE, sw=1.5))
    f.append(line(70, 230, 90, 230, color=LINE, sw=1.5))
    f.append(line(74, 234, 86, 234, color=LINE, sw=1.2))
    f.append(line(78, 238, 82, 238, color=LINE, sw=1))

    # Захисний резистор R_UL (1 кОм, UL 1642 / IEC 60065)
    f.append(line(104, 175, 140, 175, color=FIELD, sw=2))
    r_ul, _, _ = textbox(175, 175, "R1 (1 кОм)\nUL Захист", size=9.5, fill="#ffffff", stroke=LINE, pad=4)
    f.append(r_ul)

    # Блокувальний конденсатор C_vbat (100 нФ X7R біля самого піна MCU)
    f.append(line(210, 175, 380, 175, color=FIELD, sw=2))
    f.append(circle(290, 175, 3, fill=INK, stroke=LINE, sw=1))
    f.append(line(290, 175, 290, 205, color=LINE, sw=1.5))
    c_vbat, _, _ = textbox(290, 225, "C1 100 нФ\nКераміка X7R", size=9.5, fill="#ffffff", stroke=LINE, pad=4)
    f.append(c_vbat)
    f.append(line(290, 245, 290, 255, color=LINE, sw=1.5))
    f.append(line(282, 255, 298, 255, color=LINE, sw=1.5))
    f.append(line(286, 258, 294, 258, color=LINE, sw=1.2))

    # З'єднання до піна VBAT
    f.append(arrow(380, 175, 480, 175, color=FIELD, sw=2))

    # ── Зовнішнє коло кварцу LSE 32.768 кГц (Ліва середня частина) ────────────
    # Охоронне кільце (Guard Ring)
    f.append(rect(130, 275, 300, 125, fill="#f0fdfa", stroke="#0d9488", sw=1.5, rx=6))
    f.append(text(280, 292, "Охоронне кільце (GND Guard Ring) під кварцом", size=9.5, bold=True, color="#0d9488"))

    # Кварцовий резонатор Q1 32.768 кГц
    f.append(rect(240, 315, 70, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    f.append(text(275, 334, "Y1 32.768k", size=10, bold=True, color="#0284c7"))
    f.append(text(275, 348, "CL = 6..12.5 пФ", size=9.5, color=MUTED))

    # З'єднання кварцу з пінами MCU
    f.append(line(310, 325, 440, 325, color="#0284c7", sw=1.5))
    f.append(arrow(440, 325, 480, 344, color="#0284c7", sw=1.5))

    f.append(line(310, 345, 440, 345, color="#0284c7", sw=1.5))
    f.append(line(440, 345, 440, 274, color="#0284c7", sw=1.5))
    f.append(arrow(440, 274, 480, 274, color="#0284c7", sw=1.5))

    # Навантажувальні конденсатори CL1, CL2
    f.append(line(220, 325, 240, 325, color="#0284c7", sw=1.5))
    f.append(line(220, 345, 240, 345, color="#0284c7", sw=1.5))

    c_l1, _, _ = textbox(180, 325, "CL1\n10..18 пФ", size=9.5, fill="#ffffff", stroke="#0284c7", pad=3)
    c_l2, _, _ = textbox(180, 370, "CL2\n10..18 пФ", size=9.5, fill="#ffffff", stroke="#0284c7", pad=3)
    f.extend([c_l1, c_l2])

    f.append(line(220, 345, 220, 370, color="#0284c7", sw=1.5))
    f.append(line(180, 340, 180, 355, color=LINE, sw=1.2))
    f.append(line(180, 385, 180, 395, color=LINE, sw=1.2))
    # З'єднання CL до Guard GND
    f.append(circle(180, 395, 2.5, fill=LINE, stroke=LINE, sw=1))

    # Блокувальний конденсатор по шині VDD
    f.append(line(360, 445, 480, 445, color=POS, sw=2))
    c_vdd, _, _ = textbox(300, 445, "C2 100 нФ\nX7R Bypass", size=9.5, fill="#ffffff", stroke=POS, pad=4)
    f.append(c_vdd)

    render(os.path.join(IMG, 'vbat-complete-schematic.svg'), W, H, *f)


if __name__ == '__main__':
    print("Генерація SVG-фігур для backup-power-domain...")
    fig_vbat_architecture()
    fig_power_switch_topology()
    fig_vbat_switching_waveforms()
    fig_supercap_vs_cr2032()
    fig_vbat_complete_schematic()
    print("Успішно згенеровано 5 фігур у ./img/")
