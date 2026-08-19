# -*- coding: utf-8 -*-
"""Фігури для теми 'Вбудований DC-DC в мікроконтролерах' (integrated-dc-dc).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_mcu_architecture():
    """Схемотехнічний поділ живлення мікроконтролера: кристал (on-chip) та зовнішні компоненти (off-chip)."""
    W, H = 840, 520
    frags = []

    # Фон і загальна розмітка
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Зовнішня рамка — плата (PCB)
    frags.append(rect(20, 20, 800, 480, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 45, "Друкована плата (PCB)", size=13, color=MUTED, bold=True, anchor="start"))

    # Джерело живлення зліва (Батарея / 3.3 В)
    box_pwr, _, _ = textbox(90, 210, ["Батарея / VDD", "3.0 В ... 3.6 В"], size=12, fill="#eef2ff", stroke=NEG, bold=True)
    frags.append(box_pwr)

    # Вхідний блокувальний конденсатор Cin (Off-chip)
    frags.append(rect(165, 140, 36, 60, fill="#f8fafc", stroke=INK, sw=1.5, rx=3))
    frags.append(text(183, 175, "Cin", size=11, color=INK, bold=True))
    frags.append(text(183, 215, "1...4.7 мкФ", size=10, color=MUTED))
    frags.append(line(183, 110, 183, 140, color=INK, sw=1.5))
    frags.append(line(183, 200, 183, 240, color=INK, sw=1.5))
    frags.append(line(170, 240, 196, 240, color=INK, sw=1.5))

    # Лінія живлення від батареї до MCU
    frags.append(line(130, 210, 150, 210, color=POS, sw=2))
    frags.append(line(150, 210, 150, 110, color=POS, sw=2))
    frags.append(arrow(150, 110, 240, 110, color=POS, sw=2))
    frags.append(arrow(150, 210, 240, 210, color=POS, sw=2))
    frags.append(line(150, 210, 150, 310, color=POS, sw=2))
    frags.append(arrow(150, 310, 240, 310, color=POS, sw=2))

    # Кристал мікроконтролера (Silicon Die / On-Chip)
    frags.append(rect(240, 60, 360, 420, fill="#f1f5f9", stroke="#475569", sw=2, rx=6))
    frags.append(text(420, 85, "Кристал мікроконтролера (On-Chip)", size=14, color=INK, bold=True))

    # Піни на межі кристала (зліва)
    frags.append(circle(240, 110, 4, fill=POS, stroke=INK))
    frags.append(text(248, 105, "VDD_DCDC", size=10, color=INK, anchor="start"))
    frags.append(circle(240, 210, 4, fill=POS, stroke=INK))
    frags.append(text(248, 205, "VDD_MAIN", size=10, color=INK, anchor="start"))
    frags.append(circle(240, 310, 4, fill=POS, stroke=INK))
    frags.append(text(248, 305, "VDD_LDO", size=10, color=INK, anchor="start"))

    # Блок DC-DC (SMPS) на кристалі
    frags.append(rect(260, 100, 180, 125, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=4))
    frags.append(text(350, 118, "Вбудований DC-DC (Buck)", size=11, color="#c2410c", bold=True))
    frags.append(rect(270, 130, 80, 40, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=3))
    frags.append(text(310, 153, "ШІМ/PFM Контролер", size=9, color=INK, bold=True))
    # Силові ключі (MOSFETs)
    frags.append(rect(365, 130, 65, 20, fill="#ffedd5", stroke=POS, sw=1.2, rx=2))
    frags.append(text(397, 144, "HS-PMOS", size=9, color=POS, bold=True))
    frags.append(rect(365, 155, 65, 20, fill="#ffedd5", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(397, 169, "LS-NMOS", size=9, color=NEG, bold=True))
    frags.append(text(350, 215, "Частота 4...8 МГц", size=10, color=MUTED))

    # Вивід комутації SW (з права назовні)
    frags.append(line(430, 148, 600, 148, color=POS, sw=2))
    frags.append(circle(600, 148, 4, fill=POS, stroke=INK))
    frags.append(text(592, 140, "SW / LX", size=10, color=INK, anchor="end"))

    # Блок лінійного регулятора (LDO / ULP-LDO)
    frags.append(rect(260, 245, 180, 85, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(350, 263, "Вбудовані LDO", size=11, color="#15803d", bold=True))
    frags.append(rect(270, 275, 75, 45, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(307, 293, "Головний LDO", size=9, color=INK, bold=True))
    frags.append(text(307, 309, "Iq ≈ 20 мкА", size=10, color=MUTED))
    frags.append(rect(355, 275, 75, 45, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(392, 293, "ULP-LDO", size=9, color=INK, bold=True))
    frags.append(text(392, 309, "Iq ≈ 150 нА", size=10, color=MUTED))

    # Перемикач режимів живлення (Power Switch / MUX)
    frags.append(rect(460, 175, 55, 140, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(487, 235, "Селектор", size=10, color=INK, bold=True))
    frags.append(text(487, 250, "режимів", size=10, color=INK, bold=True))
    frags.append(text(487, 265, "живлення", size=9, color=MUTED))

    # З'єднання LDO з селектором
    frags.append(arrow(440, 290, 460, 290, color=FIELD, sw=1.8))

    # Цифрове ядро (Digital Core Vcore = 1.1 В)
    frags.append(rect(530, 200, 60, 180, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(560, 230, "Ядро", size=11, color=NEG, bold=True))
    frags.append(text(560, 250, "CPU", size=10, color=INK, bold=True))
    frags.append(text(560, 275, "SRAM", size=10, color=INK))
    frags.append(text(560, 300, "Flash", size=10, color=INK))
    frags.append(text(560, 325, "RF-логіка", size=10, color=INK))
    frags.append(text(560, 360, "1.1 В", size=11, color=NEG, bold=True))

    frags.append(arrow(515, 245, 530, 245, color=INK, sw=2))

    # Зворотний вхід для живлення ядра від зовнішнього LC фільтра (VCORE pin)
    frags.append(circle(600, 210, 4, fill=FIELD, stroke=INK))
    frags.append(text(592, 202, "VCORE", size=10, color=INK, anchor="end"))
    frags.append(arrow(600, 210, 515, 210, color=FIELD, sw=2))

    # Зовнішній LC-фільтр (Off-Chip компоненти праворуч)
    # Котушка індуктивності L
    frags.append(line(600, 148, 640, 148, color=POS, sw=2))
    frags.append(rect(640, 133, 60, 30, fill="#fff1f2", stroke="#e11d48", sw=1.8, rx=4))
    frags.append(text(670, 152, "L (зовні)", size=10, color="#be123c", bold=True))
    frags.append(text(670, 180, "0.47...4.7 мкГн", size=10, color=MUTED))

    # З'єднання котушки з виходом і конденсатором Cout
    frags.append(line(700, 148, 750, 148, color=POS, sw=2))
    frags.append(line(750, 148, 750, 210, color=FIELD, sw=2))
    frags.append(arrow(750, 210, 600, 210, color=FIELD, sw=2))

    # Вихідний конденсатор Cout (Off-chip)
    frags.append(line(750, 210, 750, 250, color=FIELD, sw=1.5))
    frags.append(rect(732, 250, 36, 60, fill="#f8fafc", stroke=INK, sw=1.5, rx=3))
    frags.append(text(750, 285, "Cout", size=11, color=INK, bold=True))
    frags.append(text(750, 325, "2.2...10 мкФ", size=10, color=MUTED))
    frags.append(line(750, 310, 750, 350, color=INK, sw=1.5))
    frags.append(line(735, 350, 765, 350, color=INK, sw=1.5))

    # Позначення зон
    frags.append(text(160, 480, "Зовнішні пасивні компоненти", size=12, color=MUTED, bold=True))
    frags.append(text(710, 480, "Зовнішній LC-фільтр SMPS", size=12, color="#be123c", bold=True))

    render(os.path.join(OUT, "dcdc-mcu-architecture.svg"), W, H, *frags,
           title="Архітектура вбудованого DC-DC регулятора в мікроконтролері")


def fig_efficiency_curve():
    """Крива ККД вбудованого DC-DC та LDO залежно від струму навантаження ядра."""
    W, H = 760, 460
    L, R = 90, 700
    T, B = 60, 370

    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Осі
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))

    # Вісь Y: ККД (%)
    for y_val in range(0, 101, 20):
        y_pos = B - (y_val / 100.0) * (B - T)
        frags.append(line(L - 5, y_pos, L, y_pos, color=INK, sw=1.2))
        frags.append(line(L, y_pos, R, y_pos, color="#e2e8f0", sw=1, dash="3,3"))
        frags.append(text(L - 12, y_pos + 4, "%d%%" % y_val, size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 45, (T + B) / 2, "ККД (η), %", size=13, color=INK, bold=True))

    # Вісь X: Струм навантаження (логарифмічна шкала від 100 нА до 100 мА = 6 декад)
    labels = ["100 нА", "1 мкА", "10 мкА", "100 мкА", "1 мА", "10 мА", "100 мА"]
    for i, lbl in enumerate(labels):
        x_pos = L + (i / 6.0) * (R - L)
        frags.append(line(x_pos, B, x_pos, B + 5, color=INK, sw=1.2))
        frags.append(text(x_pos, B + 22, lbl, size=11, color=MUTED))
    frags.append(text((L + R) / 2, B + 45, "Струм навантаження ядра (Icore)", size=13, color=INK, bold=True))

    # Зона 1: Низьке споживання (Deep Sleep) - перемагає LDO
    x_split = L + (3.2 / 6.0) * (R - L) # ~150 мкА
    frags.append(rect(L, T, x_split - L, B - T, fill="#f0fdf4", stroke="none"))
    frags.append(text(L + (x_split - L)/2, T + 20, "Зона сну (ULP-LDO)", size=11, color=FIELD, bold=True))
    frags.append(text(L + (x_split - L)/2, T + 36, "Втрати комутації DC-DC зависокі", size=9, color=MUTED))

    # Зона 2: Активний режим - перемагає DC-DC
    frags.append(rect(x_split, T, R - x_split, B - T, fill="#fff7ed", stroke="none"))
    frags.append(text(x_split + (R - x_split)/2, B - 55, "Зона активної роботи (DC-DC)", size=11, color="#ea580c", bold=True))
    frags.append(text(x_split + (R - x_split)/2, B - 40, "ККД 85-90% (струм менший у 2.6 рази)", size=9, color=MUTED))

    # Лінія розділу режимів
    frags.append(line(x_split, T, x_split, B, color="#94a3b8", sw=1.8, dash="4,4"))
    frags.append(text(x_split, B - 15, "Межа перемикання (~100..200 мкА)", size=10, color="#64748b", bold=True))

    # Крива LDO
    ldo_pts = []
    pts_ldo_raw = [(0, 20), (0.5, 28), (1.0, 32), (2.0, 33.3), (3.0, 33.3), (4.0, 33.3), (5.0, 33.3), (6.0, 33.3)]
    for x_idx, eff in pts_ldo_raw:
        px = L + (x_idx / 6.0) * (R - L)
        py = B - (eff / 100.0) * (B - T)
        ldo_pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(ldo_pts), FIELD))
    frags.append(text(R - 40, B - (33.3 / 100.0) * (B - T) + 20, "LDO (η ≈ 33%)", size=12, color=FIELD, bold=True))

    # Крива DC-DC (Buck)
    pts_dcdc_raw = [(0, 1), (1.0, 4), (2.0, 18), (2.8, 33.3), (3.2, 55), (3.8, 78), (4.5, 88), (5.2, 89), (6.0, 84)]
    dcdc_pts = []
    for x_idx, eff in pts_dcdc_raw:
        px = L + (x_idx / 6.0) * (R - L)
        py = B - (eff / 100.0) * (B - T)
        dcdc_pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(dcdc_pts), POS))
    frags.append(text(R - 40, B - (85.0 / 100.0) * (B - T) - 15, "DC-DC (η ≈ 88%)", size=12, color=POS, bold=True))

    # Точка перетину кривих (Crossover Point)
    cross_x = L + (2.8 / 6.0) * (R - L)
    cross_y = B - (33.3 / 100.0) * (B - T)
    frags.append(circle(cross_x, cross_y, 5, fill="#f59e0b", stroke=INK, sw=1.5))
    frags.append(text(cross_x - 10, cross_y - 14, "Точка паритету ККД", size=11, color="#b45309", bold=True, anchor="end"))

    render(os.path.join(OUT, "efficiency-vs-load.svg"), W, H, *frags,
           title="ККД живлення ядра MCU: DC-DC проти LDO")


def fig_transient_handover():
    """Динамічне перемикання режимів живлення DCDC <-> LDO при переході в сон і пробудженні."""
    W, H = 820, 480
    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    L, R = 150, 780
    T = 40

    # 4 фази: RUN (DCDC) -> ENTER SLEEP -> DEEP SLEEP (ULP-LDO) -> WAKEUP -> RUN (DCDC)
    x0 = L
    x1 = L + 160   # Початок переходу в сон
    x2 = L + 250   # Завершення переходу, вхід у Deep Sleep
    x3 = L + 470   # Сигнал пробудження
    x4 = L + 560   # Стабілізація DCDC, перемикання назад на DCDC
    x5 = R

    # Фонове виділення фаз
    frags.append(rect(x0, T, x1 - x0, 400, fill="#fff7ed", stroke="none"))
    frags.append(rect(x1, T, x2 - x1, 400, fill="#fef3c7", stroke="none"))
    frags.append(rect(x2, T, x3 - x2, 400, fill="#f0fdf4", stroke="none"))
    frags.append(rect(x3, T, x4 - x3, 400, fill="#fef3c7", stroke="none"))
    frags.append(rect(x4, T, x5 - x4, 400, fill="#fff7ed", stroke="none"))

    # Підписи фаз зверху
    frags.append(text((x0 + x1)/2, T + 18, "Активний (RUN)", size=11, color="#c2410c", bold=True))
    frags.append(text((x1 + x2)/2, T + 18, "Перехід", size=10, color="#b45309", bold=True))
    frags.append(text((x2 + x3)/2, T + 18, "Глибокий сон (STOP / STANDBY)", size=11, color=FIELD, bold=True))
    frags.append(text((x3 + x4)/2, T + 18, "Пробудження", size=10, color="#b45309", bold=True))
    frags.append(text((x4 + x5)/2, T + 18, "Активний (RUN)", size=11, color="#c2410c", bold=True))

    # Розділові вертикальні лінії
    for x in [x1, x2, x3, x4]:
        frags.append(line(x, T + 30, x, T + 400, color="#cbd5e1", sw=1.2, dash="3,3"))

    # Сигнал 1: Стан процесора (CPU Activity)
    y1 = T + 70
    frags.append(text(20, y1 + 10, "Режим процесора", size=11, color=INK, bold=True, anchor="start"))
    frags.append(rect(x0 + 5, y1, x1 - x0 - 10, 20, fill="#fed7aa", stroke="#ea580c", rx=3))
    frags.append(text((x0 + x1)/2, y1 + 14, "Обчислення / Радіо", size=10, color=INK))
    frags.append(rect(x1 + 5, y1, x2 - x1 - 10, 20, fill="#fde68a", stroke="#d97706", rx=3))
    frags.append(text((x1 + x2)/2, y1 + 14, "WFI / Підготовка", size=9, color=INK))
    frags.append(rect(x2 + 5, y1, x3 - x2 - 10, 20, fill="#bbf7d0", stroke=FIELD, rx=3))
    frags.append(text((x2 + x3)/2, y1 + 14, "Ядро зупинене, тактування вимкнено", size=10, color=FIELD, bold=True))
    frags.append(rect(x3 + 5, y1, x4 - x3 - 10, 20, fill="#fde68a", stroke="#d97706", rx=3))
    frags.append(text((x3 + x4)/2, y1 + 14, "Старт PLL", size=9, color=INK))
    frags.append(rect(x4 + 5, y1, x5 - x4 - 10, 20, fill="#fed7aa", stroke="#ea580c", rx=3))
    frags.append(text((x4 + x5)/2, y1 + 14, "Обробка переривання", size=10, color=INK))

    # Сигнал 2: Стан DC-DC (SMPS)
    y2 = T + 140
    frags.append(text(20, y2 + 10, "Стан DC-DC", size=11, color=POS, bold=True, anchor="start"))
    frags.append(line(x0, y2 + 20, x1, y2 + 20, color=POS, sw=1.5))
    for px in range(x0 + 10, x1 - 10, 8):
        frags.append(line(px, y2 + 20, px, y2, color=POS, sw=1.5))
        frags.append(line(px + 4, y2, px + 4, y2 + 20, color=POS, sw=1.5))
    frags.append(text((x0 + x1)/2, y2 - 6, "ШІМ комутація 4 МГц", size=9, color=POS))
    frags.append(line(x1, y2 + 20, x2, y2 + 20, color=POS, sw=2))
    frags.append(text((x1 + x2)/2, y2 + 12, "Soft-Stop", size=9, color=MUTED))
    frags.append(line(x2, y2 + 20, x3, y2 + 20, color="#94a3b8", sw=2))
    frags.append(text((x2 + x3)/2, y2 + 12, "Вимкнено (0 мА втрат)", size=10, color=MUTED))
    frags.append(line(x3, y2 + 20, x4, y2 + 20, color=POS, sw=2))
    frags.append(text((x3 + x4)/2, y2 + 12, "Soft-Start", size=9, color=POS))
    frags.append(line(x4, y2 + 20, x5, y2 + 20, color=POS, sw=1.5))
    for px in range(x4 + 10, x5 - 10, 8):
        frags.append(line(px, y2 + 20, px, y2, color=POS, sw=1.5))
        frags.append(line(px + 4, y2, px + 4, y2 + 20, color=POS, sw=1.5))

    # Сигнал 3: Стан LDO / ULP-LDO
    y3 = T + 210
    frags.append(text(20, y3 + 10, "Стан LDO", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(line(x0, y3 + 20, x1, y3 + 20, color="#94a3b8", sw=2))
    frags.append(text((x0 + x1)/2, y3 + 12, "Вимкнено / Очікування", size=9, color=MUTED))
    frags.append(line(x1, y3 + 20, x1 + 30, y3, color=FIELD, sw=2))
    frags.append(line(x1 + 30, y3, x4, y3, color=FIELD, sw=2))
    frags.append(text((x2 + x3)/2, y3 - 6, "ULP-LDO активний (тримає пам'ять SRAM)", size=10, color=FIELD, bold=True))
    frags.append(line(x4, y3, x4 + 30, y3 + 20, color=FIELD, sw=2))
    frags.append(line(x4 + 30, y3 + 20, x5, y3 + 20, color="#94a3b8", sw=2))

    # Сигнал 4: Напруга Vcore
    y4 = T + 285
    frags.append(text(20, y4 + 10, "Напруга ядра Vcore", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(line(x0, y4, x1, y4, color=NEG, sw=2.2))
    frags.append(line(x1, y4, x1 + 40, y4 + 6, color=NEG, sw=2.2))
    frags.append(line(x1 + 40, y4 + 6, x2, y4, color=NEG, sw=2.2))
    frags.append(line(x2, y4, x3, y4, color=NEG, sw=2.2))
    frags.append(line(x3, y4, x3 + 40, y4 - 4, color=NEG, sw=2.2))
    frags.append(line(x3 + 40, y4 - 4, x4, y4, color=NEG, sw=2.2))
    frags.append(line(x4, y4, x5, y4, color=NEG, sw=2.2))
    frags.append(text(x0 + 40, y4 - 8, "1.10 В", size=10, color=NEG, bold=True))
    frags.append(text((x2 + x3)/2, y4 - 8, "1.10 В (стабільно)", size=10, color=NEG))
    frags.append(line(x0, y4 + 30, x5, y4 + 30, color="#ef4444", sw=1.2, dash="4,3"))
    frags.append(text(x5 - 10, y4 + 42, "Поріг аварійного скидання (BOR ≈ 0.95 В)", size=9, color="#ef4444", anchor="end"))

    # Сигнал 5: Струм від батареї (I_bat)
    y5 = T + 360
    frags.append(text(20, y5 + 10, "Струм від батареї", size=11, color=INK, bold=True, anchor="start"))
    frags.append(line(x0, y5, x1, y5, color=INK, sw=2.2))
    frags.append(text(x0 + 40, y5 - 8, "≈ 11.5 мА (активно)", size=10, color=INK, bold=True))
    frags.append(line(x1, y5, x2, y5 + 25, color=INK, sw=2.2))
    frags.append(line(x2, y5 + 25, x3, y5 + 25, color=INK, sw=2.2))
    frags.append(text((x2 + x3)/2, y5 + 16, "≈ 1.5 мкА (глибокий сон)", size=10, color=FIELD, bold=True))
    frags.append(line(x3, y5 + 25, x4, y5, color=INK, sw=2.2))
    frags.append(line(x4, y5, x5, y5, color=INK, sw=2.2))

    render(os.path.join(OUT, "transient-handover.svg"), W, H, *frags,
           title="Динамічне перемикання DC-DC та LDO при зміні режимів сну")


def fig_pcb_layout():
    """Трасування комутаційної петлі на платі та захист RF-тракту від завад EMI."""
    W, H = 800, 480
    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Плата
    frags.append(rect(20, 20, 760, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(40, 45, "Топологія друкованої плати (PCB Top Layer)", size=13, color=MUTED, bold=True, anchor="start"))

    # Корпус мікроконтролера (QFN / BGA) - x: 60..260, y: 100..360
    frags.append(rect(60, 100, 200, 260, fill="#1e293b", stroke="#0f172a", sw=2, rx=6))
    frags.append(text(160, 130, "Мікроконтролер", size=14, color="#f8fafc", bold=True))
    frags.append(text(160, 150, "STM32 / nRF52 / ESP32", size=11, color="#94a3b8"))

    # Виводи MCU (праворуч від мікросхеми, x=260..280)
    # Pin 1: VDD_DCDC
    frags.append(rect(260, 180, 20, 16, fill="#f59e0b", stroke=INK, rx=2))
    frags.append(text(245, 192, "VDD", size=10, color="#f8fafc", anchor="end"))
    # Pin 2: DCC_SW
    frags.append(rect(260, 220, 20, 16, fill=POS, stroke=INK, rx=2))
    frags.append(text(245, 232, "DCDC_SW", size=10, color="#f8fafc", anchor="end"))
    # Pin 3: VSS_SMPS
    frags.append(rect(260, 260, 20, 16, fill=NEG, stroke=INK, rx=2))
    frags.append(text(245, 272, "VSS_SMPS", size=10, color="#f8fafc", anchor="end"))
    # Pin 4: VCORE
    frags.append(rect(260, 300, 20, 16, fill=FIELD, stroke=INK, rx=2))
    frags.append(text(245, 312, "VCORE", size=10, color="#f8fafc", anchor="end"))

    # Вхідний конденсатор Cin поруч із VDD та VSS
    frags.append(rect(310, 160, 35, 45, fill="#e2e8f0", stroke=INK, sw=1.5, rx=3))
    frags.append(text(327, 186, "Cin", size=10, color=INK, bold=True))
    frags.append(line(280, 188, 310, 188, color="#f59e0b", sw=3))

    # Котушка L (SMD 0805 / 0603)
    frags.append(rect(320, 215, 60, 35, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    frags.append(text(350, 237, "L 2.2 мкГн", size=10, color=POS, bold=True))
    frags.append(line(280, 228, 320, 228, color=POS, sw=4))
    frags.append(text(298, 220, "SW", size=9, color=POS, bold=True))

    # Вихідний конденсатор Cout
    frags.append(rect(420, 215, 35, 45, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=3))
    frags.append(text(437, 241, "Cout", size=10, color=FIELD, bold=True))
    frags.append(line(380, 228, 420, 228, color=FIELD, sw=3))

    # Зворотний зв'язок на VCORE
    frags.append(line(437, 215, 437, 308, color=FIELD, sw=2))
    frags.append(arrow(437, 308, 280, 308, color=FIELD, sw=2))

    # Земляний полігон повернення струму (GND Return)
    frags.append(line(437, 260, 437, 275, color=NEG, sw=2))
    frags.append(line(437, 275, 327, 275, color=NEG, sw=3))
    frags.append(line(327, 275, 327, 205, color=NEG, sw=2))
    frags.append(arrow(327, 275, 280, 268, color=NEG, sw=3))

    # Гаряча високочастотна петля комутації (Штрихована червона зона)
    frags.append('<rect x="290.0" y="210.0" width="160.0" height="80.0" rx="6" fill="none" stroke="#dc2626" stroke-width="2.0" stroke-dasharray="4,4"/>')
    frags.append(text(370, 305, "Мінімальна площа петлі dI/dt", size=10, color="#dc2626", bold=True))

    # Перехідні отвори на шар заземлення (GND Vias)
    for vx in [327, 360, 400, 437]:
        frags.append(circle(vx, 275, 3.5, fill="#64748b", stroke=INK, sw=1))
    frags.append(text(380, 263, "GND Vias", size=9, color="#64748b"))

    # RF-тракт праворуч (Антена + Узгодження 2.4 ГГц / LoRa)
    frags.append(rect(540, 100, 220, 260, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(650, 130, "RF-тракт (2.4 ГГц / Sub-GHz)", size=12, color="#0369a1", bold=True))

    # Антена
    frags.append(rect(710, 160, 30, 120, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(725, 225, "PCB Антена", size=10, color="#0369a1", bold=True))

    # Балун / Узгоджувальне коло (Matching Network)
    frags.append(rect(560, 180, 80, 70, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=3))
    frags.append(text(600, 210, "RF Балун і", size=10, color=INK, bold=True))
    frags.append(text(600, 225, "фільтр 50 Ом", size=10, color=INK))
    frags.append(line(640, 215, 710, 215, color="#0284c7", sw=2))

    # Екран / Захисний земляний бар'єр (GND Guard Ring / Vias Fence)
    frags.append(line(505, 80, 505, 400, color="#64748b", sw=3, dash="6,6"))
    frags.append(text(505, 420, "Земляний бар'єр", size=10, color="#475569", bold=True))
    frags.append(text(505, 435, "ізоляції від шуму SMPS", size=9, color=MUTED))

    # Кварцовий резонатор (HSE 32 МГц) знизу
    frags.append(rect(100, 390, 80, 45, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(140, 412, "Кварц HSE", size=10, color="#a16207", bold=True))
    frags.append(text(140, 425, "32 МГц", size=9, color=MUTED))
    frags.append(line(140, 390, 140, 360, color="#ca8a04", sw=1.5))

    render(os.path.join(OUT, "pcb-switching-loop.svg"), W, H, *frags,
           title="Трасування комутаційного контуру DC-DC на платі мікроконтролера")


if __name__ == "__main__":
    fig_mcu_architecture()
    fig_efficiency_curve()
    fig_transient_handover()
    fig_pcb_layout()
    print("ok figs")
