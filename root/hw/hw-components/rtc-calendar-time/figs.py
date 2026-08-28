# -*- coding: utf-8 -*-
"""Фігури до статті «Годинник і мітки часу: RTC, дрейф, монотонність».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s stroke-linejoin="round"/>' % (p, color, sw, d)

# ── 1. Внутрішня будова RTC: прескалер, BCD-лічильники та тіньовий буфер ────
def fig_prescaler_bcd():
    W, H = 960, 520
    f = [
        text(W / 2, 28, "Внутрішня архітектура RTC: подвійний прескалер та BCD-календар", size=16, bold=True),
        text(W / 2, 48, "перетворення 32768 Гц на секундний строб, калібрування, субсекундний лічильник та фіксація читання",
             size=12, color=MUTED, italic=True)
    ]

    # Верхній блок: Генератор -> Асинхронний дільник -> Синхронний дільник -> Калібрування
    # 1. Генератор 32.768 кГц
    tb1, _, _ = textbox(110, 110, "Генератор П'єрса\n32 768 Гц\n(LSE / XTAL)", size=12, fill="#eef2f7", stroke=INK, sw=1.5)
    f.append(tb1)

    f.append(arrow(180, 110, 230, 110, color=INK, sw=1.6))
    f.append(text(205, 100, "32 кГц", size=10, color=MUTED))

    # 2. Асинхронний прескалер
    tb2, _, _ = textbox(310, 110, "Асинхронний\nпрескалер (÷128)\nPREDIV_A (7-біт)", size=12, fill="#e8f4fd", stroke=NEG, sw=1.6)
    f.append(tb2)

    f.append(arrow(390, 110, 440, 110, color=INK, sw=1.6))
    f.append(text(415, 100, "256 Гц", size=10, color=MUTED))

    # 3. Синхронний прескалер + Субсекундний лічильник SSR
    tb3, _, _ = textbox(530, 110, "Синхронний прескалер\n(÷256) PREDIV_S\nЛічильник SSR (255..0)", size=12, fill="#e8f4fd", stroke=NEG, sw=1.6)
    f.append(tb3)

    # Відгалуження на Sub-second register униз
    f.append(arrow(530, 145, 530, 185, color=NEG, sw=1.5))
    tb_ssr, _, _ = textbox(530, 215, "Субсекундний регістр SSR\n(Частка секунди: t = SSR/256 с)\nроздільність ~3.9 мс", size=11, fill="#fdfefe", stroke=NEG, sw=1.3)
    f.append(tb_ssr)

    # 4. Блок цифрового калібрування
    f.append(arrow(620, 110, 670, 110, color=INK, sw=1.6))
    f.append(text(645, 100, "1 Гц*", size=10, color=MUTED))

    tb4, _, _ = textbox(760, 110, "Блок цифрового\nкалібрування (CALM/CALP)\nвставка/маскування тактів", size=12, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(tb4)

    f.append(arrow(850, 110, 890, 110, color=FIELD, sw=1.8))
    f.append(line(890, 110, 890, 300, color=FIELD, sw=1.8))
    f.append(arrow(890, 300, 840, 300, color=FIELD, sw=1.8))
    f.append(text(890, 205, "Точний строб 1.000000 Гц", size=11, color=FIELD, bold=True, anchor="middle"))

    # Нижній блок: BCD Лічильники календаря
    f.append(rect(40, 270, 810, 105, fill="none", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(445, 290, "Ланцюжок BCD-лічильників календаря (Binary-Coded Decimal)", size=13, bold=True, color=INK))

    # Каскад: Секунди -> Хвилини -> Години -> День/Дата -> Місяць -> Рік
    b_w = 95
    b_h = 50
    labels = [
        ("Секунди", "00..59\n(BCD: 7-біт)"),
        ("Хвилини", "00..59\n(BCD: 7-біт)"),
        ("Години", "00..23\n(BCD: 6-біт)"),
        ("Дата", "01..31\n(BCD: 6-біт)"),
        ("Місяць", "01..12\n(BCD: 5-біт)"),
        ("Рік", "00..99\n(+високосний)")
    ]

    for i, (name, sub) in enumerate(labels):
        bx = 70 + i * 125
        by = 335
        f.append(rect(bx - b_w/2, by - b_h/2, b_w, b_h, fill="#ffffff", stroke=INK, sw=1.4, rx=5))
        f.append(text(bx, by - 8, name, size=11.5, bold=True, color=INK))
        f.append(text(bx, by + 12, sub, size=9.5, color=MUTED))
        if i < len(labels) - 1:
            f.append(arrow(bx + b_w/2, by, bx + 125 - b_w/2, by, color=INK, sw=1.3))

    # Тіньовий регістровий буфер (Shadow Latches) на шині читання
    f.append(arrow(445, 375, 445, 415, color=POS, sw=1.6))
    f.append(text(540, 395, "Атомарне копіювання при читанні (Time-Hold / RSF)", size=11, color=POS, bold=True))

    tb_shad, _, _ = textbox(445, 455, "Тіньові регістри-засувки (Shadow Registers) & Інтерфейс APB / I²C / SPI\nЗапобігання розриву даних при переході 23:59:59 → 00:00:00 під час читання процесором",
                            size=12, fill="#fdf3f2", stroke=POS, sw=1.5, min_w=780)
    f.append(tb_shad)

    render(os.path.join(IMG, "rtc-prescaler-bcd-chain.svg"), W, H, *f)


# ── 2. Фізика дрейфу: Парабола температури та ємнісне підтягування ──────────
def fig_crystal_drift():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Джерела похибок ходу кварцу: температурна парабола та навантажувальна ємність", size=16, bold=True),
        text(W / 2, 48, "параболічне падіння частоти камертонного зрізу XY та чутливість точки резонансу до ємності C_L",
             size=12, color=MUTED, italic=True)
    ]

    # Ліва панель: Температурна парабола
    L1, R1, T1, B1 = 70, 450, 115, 420
    f.append(text((L1 + R1) / 2, T1 - 32, "Температурний дрейф: Δf/f₀ = −k·(T − T₀)²", size=13, bold=True))

    def tx(temp):
        return L1 + (temp - (-40)) / (85 - (-40)) * (R1 - L1)

    def ty(ppm):
        return T1 + (-ppm) / 140.0 * (B1 - T1)

    # Зелена смуга TCXO (±2 ppm) як фонова підкладка без контуру
    f.append(rect(L1, ty(2), R1 - L1, ty(-2) - ty(2), fill="#d4efdf", stroke="none", rx=0))
    tb_tcxo, _, _ = textbox((L1 + R1)/2, T1 - 12, "Зелена зона: коридор TCXO (DS3231) ±2 ppm", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2, pad=4)
    f.append(tb_tcxo)

    # Осі
    f.append(line(L1, T1, L1, B1, color=INK, sw=1.5))
    f.append(line(L1, B1, R1, B1, color=INK, sw=1.5))
    f.append(text(L1 - 8, T1 + 5, "Δf/f (ppm)", size=11, bold=True, anchor="end"))
    f.append(text(R1 + 5, B1 + 18, "Температура T (°C) →", size=11, color=MUTED, anchor="end"))

    # Горизонтальні лінії сітки: -20, -50, -100, -140 ppm
    for p in [0, -20, -50, -100, -140]:
        y_pos = ty(p)
        f.append(line(L1, y_pos, R1, y_pos, color="#e5e7eb", sw=1.0, dash="3 3"))
        f.append(text(L1 - 6, y_pos + 4, str(p), size=10, color=MUTED, anchor="end"))

    # Вертикальні мітки: -40, -20, 0, 25, 50, 70, 85
    for temp in [-40, -20, 0, 25, 50, 70, 85]:
        x_pos = tx(temp)
        f.append(line(x_pos, T1, x_pos, B1, color="#e5e7eb", sw=1.0, dash="3 3"))
        f.append(text(x_pos, B1 + 16, str(temp), size=10, color=MUTED))

    # Побудова параболи: k = 0.035 ppm/°C^2
    pts_parabola = []
    for step in range(-40, 86, 2):
        ppm_val = -0.035 * ((step - 25) ** 2)
        pts_parabola.append((tx(step), ty(ppm_val)))

    f.append(polyline(pts_parabola, color=POS, sw=2.6))

    # Виділення точки T0 = 25 °C (0 ppm)
    f.append(circle(tx(25), ty(0), 4.5, fill=BG, stroke=POS, sw=2.0))
    f.append(text(tx(25) + 12, ty(0) - 10, "T₀ = +25 °C", size=11, bold=True, color=POS, anchor="start"))

    # Точка -20 °C (-70.9 ppm) -> ~ -3.1 хв/місяць
    f.append(circle(tx(-20), ty(-70.875), 4.0, fill=POS, stroke=POS, sw=1.5))
    f.append(text(tx(-20) - 8, ty(-70.875) - 8, "−20 °C: −71 ppm", size=10, bold=True, color=POS, anchor="end"))
    f.append(text(tx(-20) - 8, ty(-70.875) + 6, "(−3.1 хв/місяць)", size=9.5, color=MUTED, anchor="end"))

    # Точка +85 °C (-126 ppm) -> ~ -5.5 хв/місяць
    f.append(circle(tx(85), ty(-126), 4.0, fill=POS, stroke=POS, sw=1.5))
    f.append(text(tx(85) - 10, ty(-126) - 8, "+85 °C: −126 ppm", size=10, bold=True, color=POS, anchor="end"))

    # Зелена смуга TCXO (±2 ppm)
    f.append(rect(L1, ty(2), R1 - L1, ty(-2) - ty(2), fill="#d4efdf", stroke=FIELD, sw=1.2))
    f.append(text((L1 + R1)/2, ty(0) + 4, "Коридор TCXO (DS3231): ±2 ppm (−40..+85 °C)", size=10.5, color=FIELD, bold=True))

    # Права панель: Ємнісне підтягування частоти (Frequency Pulling)
    L2, R2, T2, B2 = 530, 900, 95, 420
    f.append(text((L2 + R2) / 2, T1 - 15, "Ємнісне зміщення: f_L = f_s · [1 + C_m / 2(C₀ + C_L)]", size=13, bold=True))

    f.append(line(L2, T2, L2, B2, color=INK, sw=1.5))
    f.append(line(L2, B2, R2, B2, color=INK, sw=1.5))
    f.append(text(L2 - 8, T2 + 5, "Зсув частоти (ppm)", size=11, bold=True, anchor="end"))
    f.append(text(R2 + 5, B2 + 18, "Ємність C_L (пФ) →", size=11, color=MUTED, anchor="end"))

    def cx(cl):
        return L2 + (cl - 4) / (20 - 4) * (R2 - L2)

    def cy(shift):
        return T2 + (60 - shift) / 120.0 * (B2 - T2)

    # Горизонтальні мітки: +40, +20, 0, -20, -40
    for s in [40, 20, 0, -20, -40]:
        y_pos = cy(s)
        f.append(line(L2, y_pos, R2, y_pos, color="#e5e7eb", sw=1.0, dash="3 3"))
        f.append(text(L2 - 6, y_pos + 4, ("+" if s > 0 else "") + str(s), size=10, color=MUTED, anchor="end"))

    # Вертикальні мітки: 6, 9, 12.5, 16, 20 пФ
    for cl_val in [6, 9, 12.5, 16, 20]:
        x_pos = cx(cl_val)
        f.append(line(x_pos, T2, x_pos, B2, color="#e5e7eb", sw=1.0, dash="3 3"))
        f.append(text(x_pos, B2 + 16, str(cl_val), size=10, color=MUTED))

    def pull_ppm(cl):
        c0 = 1.2
        cm = 0.0025
        base = cm / (2.0 * (c0 + 12.5))
        curr = cm / (2.0 * (c0 + cl))
        return (curr - base) * 1e6

    pts_cl = []
    for c_step in range(40, 201, 2):
        cl = c_step / 10.0
        p_val = pull_ppm(cl)
        pts_cl.append((cx(cl), cy(p_val)))

    f.append(polyline(pts_cl, color=NEG, sw=2.6))

    # Точка номіналу 12.5 пФ
    f.append(circle(cx(12.5), cy(0), 4.5, fill=BG, stroke=NEG, sw=2.0))
    f.append(text(cx(12.5) + 12, cy(0) - 8, "Номінал C_L = 12.5 пФ (0 ppm)", size=10.5, bold=True, color=NEG, anchor="start"))

    # Похибка при паразитах: CL = 9 пФ -> +22 ppm
    f.append(circle(cx(9), cy(pull_ppm(9)), 4.0, fill=NEG, stroke=NEG, sw=1.5))
    f.append(text(cx(9) - 8, cy(pull_ppm(9)) - 8, "C_L = 9 пФ: +22 ppm", size=10, bold=True, color=NEG, anchor="end"))
    f.append(text(cx(9) - 8, cy(pull_ppm(9)) + 6, "(недостатня ємність)", size=9, color=MUTED, anchor="end"))

    # Похибка при надлишкових паразитах: CL = 16 пФ -> -17 ppm
    f.append(circle(cx(16), cy(pull_ppm(16)), 4.0, fill=NEG, stroke=NEG, sw=1.5))
    f.append(text(cx(16) + 10, cy(pull_ppm(16)) + 12, "C_L = 16 пФ: −17 ppm (паразитні ємності PCB)", size=10, bold=True, color=NEG, anchor="start"))

    render(os.path.join(IMG, "crystal-parabola-and-load-capacitance.svg"), W, H, *f)


# ── 3. Плавне цифрове калібрування (Smooth Digital Calibration) ─────────────
def fig_smooth_calibration():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Принцип плавного цифрового калібрування (Smooth Digital Calibration)", size=16, bold=True),
        text(W / 2, 48, "рівномірне маскування або додавання тактів у вікні 2²⁰ (32 с) для корекції ходу з роздільністю 0.954 ppm",
             size=12, color=MUTED, italic=True)
    ]

    # Шкала вікна вимірювання 32 секунди (2^20 тактів)
    f.append(rect(60, 90, 820, 70, fill="#f8fafc", stroke=INK, sw=1.4, rx=6))
    f.append(text(470, 115, "Вікно калібрування: T_cal = 2²⁰ тактів = 1 048 576 імпульсів (~32 секунди)", size=13, bold=True, color=INK))
    f.append(text(470, 140, "Роздільність регулювання: 1 такт на вікно = 1 / 2²⁰ ≈ 0.9537 ppm (або ~0.082 с/добу)", size=11, color=MUTED))

    # Панель 1: Маскування імпульсів (Кварц поспішає, CALM > 0)
    f.append(rect(60, 185, 820, 115, fill="#fdfefe", stroke=POS, sw=1.4, rx=6))
    f.append(text(80, 210, "Режим маскування (CALM[8:0]): прискорений кварц (+Δf) уповільнюється вилученням тактів", size=12.5, bold=True, color=POS, anchor="start"))

    base_y = 265
    f.append(text(75, base_y - 12, "Вхідний потік 32 кГц:", size=10, color=MUTED, anchor="start"))

    for k in range(12):
        ix = 230 + k * 45
        f.append(rect(ix, base_y - 20, 20, 20, fill="#e8f4fd" if k != 5 else "#fadbd8", stroke=NEG if k != 5 else POS, sw=1.2, rx=2))
        f.append(text(ix + 10, base_y - 6, str(k + 1), size=9, color=INK))

    # Хрестик над вилученим
    f.append(line(230 + 5*45 - 2, base_y - 22, 230 + 5*45 + 22, base_y + 2, color=POS, sw=2.2))
    f.append(line(230 + 5*45 + 22, base_y - 22, 230 + 5*45 - 2, base_y + 2, color=POS, sw=2.2))
    f.append(text(230 + 5*45 + 10, base_y - 26, "ВИЛУЧЕНО (CALM)", size=9.5, bold=True, color=POS))
    f.append(text(780, base_y - 6, "Діапазон: 0..511 тактів\n(до −487.1 ppm)", size=10.5, color=POS, bold=True))

    # Панель 2: Додавання імпульсів (Кварц відстає, CALP = 1)
    f.append(rect(60, 320, 820, 115, fill="#fdfefe", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(80, 345, "Режим додавання (CALP = 1): уповільнений кварц (−Δf) прискорюється вставкою 1 такту що 2048 циклів", size=12.5, bold=True, color=FIELD, anchor="start"))

    base_y2 = 400
    f.append(text(75, base_y2 - 12, "Вхідний потік 32 кГц:", size=10, color=MUTED, anchor="start"))

    for k in range(12):
        ix = 230 + k * 45
        if k == 5:
            f.append(rect(ix, base_y2 - 20, 20, 20, fill="#d4efdf", stroke=FIELD, sw=1.8, rx=2))
            f.append(text(ix + 10, base_y2 - 6, "+1", size=10, bold=True, color=FIELD))
            f.append(text(ix + 10, base_y2 - 26, "ВСТАВКА (CALP)", size=9.5, bold=True, color=FIELD))
        else:
            f.append(rect(ix, base_y2 - 20, 20, 20, fill="#e8f4fd", stroke=NEG, sw=1.2, rx=2))
            f.append(text(ix + 10, base_y2 - 6, str(k + 1 if k < 5 else k), size=9, color=INK))

    f.append(text(780, base_y2 - 6, "Фіксований крок:\n+512 тактів (+488.3 ppm)", size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "smooth-digital-calibration.svg"), W, H, *f)


# ── 4. Монотонний час проти календарного часу (Timeline) ─────────────────────
def fig_monotonic_vs_wall():
    W, H = 940, 500
    f = [
        text(W / 2, 28, "Монотонний час (CLOCK_MONOTONIC) проти календарного (CLOCK_REALTIME)", size=16, bold=True),
        text(W / 2, 48, "поведінка міток часу при мережевій синхронізації NTP / GNSS: стрибок назад проти неперервного зростання",
             size=12, color=MUTED, italic=True)
    ]

    L, R = 80, 880

    # 1. Верхня шкала: Календарний час
    T_w = 110
    f.append(text(L, T_w - 20, "Календарний час t_wall (Астрономічний UTC / Годинник на стіні)", size=13, bold=True, color=POS, anchor="start"))
    f.append(arrow(L, T_w + 30, R, T_w + 30, color=POS, sw=2.0))
    f.append(text(R, T_w + 50, "Фізичний час перебігу подій →", size=10.5, color=MUTED, anchor="end"))

    # Подія 1: 12:00:00
    f.append(line(160, T_w + 20, 160, T_w + 40, color=POS, sw=2.0))
    f.append(text(160, T_w + 12, "12:00:00", size=11, bold=True, color=INK))
    f.append(text(160, T_w + 55, "Подія A", size=10, color=MUTED))

    # Подія 2: 12:00:10
    f.append(line(360, T_w + 20, 360, T_w + 40, color=POS, sw=2.0))
    f.append(text(360, T_w + 12, "12:00:10", size=11, bold=True, color=INK))
    f.append(text(360, T_w + 55, "Подія B", size=10, color=MUTED))

    # Стрибок NTP Step назад (-15 секунд)
    f.append(line(520, T_w + 10, 520, T_w + 50, color=POS, sw=2.2, dash="4 3"))
    f.append(text(520, T_w - 5, "NTP Step: корекція −15 с", size=11, bold=True, color=POS))

    # Дуга повернення часу назад
    f.append('<path d="M 520 %d Q 440 %d 360 %d" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="3 3" marker-end="url(#arrow)"/>' % (T_w + 30, T_w - 20, T_w + 20, POS))

    # Подія 3: 11:59:58
    f.append(line(680, T_w + 20, 680, T_w + 40, color=POS, sw=2.0))
    f.append(text(680, T_w + 12, "11:59:58", size=11, bold=True, color=POS))
    f.append(text(680, T_w + 55, "Подія C (t_C < t_B!)", size=10, bold=True, color=POS))

    # Червоне попередження
    tb_err, _, _ = textbox(520, T_w + 100, "КАТАСТРОФА ОБЧИСЛЕННЯ ТРИВАЛОСТІ: Δt = t_C − t_B = −12 с < 0 !\nПереповнення unsigned 64-біт, зависання тайм-аутів у while(now < deadline), інверсія логів",
                           size=11, fill="#fdf3f2", stroke=POS, sw=1.3, min_w=780)
    f.append(tb_err)

    # 2. Нижня шкала: Монотонний час (CLOCK_MONOTONIC)
    T_m = 320
    f.append(text(L, T_m - 20, "Монотонний час t_mono (Строго зростаючий лічильник тактів від старту)", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(L, T_m + 30, R, T_m + 30, color=FIELD, sw=2.0))

    # Подія 1: 100.000 с
    f.append(line(160, T_m + 20, 160, T_m + 40, color=FIELD, sw=2.0))
    f.append(text(160, T_m + 12, "100.000 с", size=11, bold=True, color=INK))
    f.append(text(160, T_m + 55, "t_mono_A", size=10, color=MUTED))

    # Подія 2: 110.000 с
    f.append(line(360, T_m + 20, 360, T_m + 40, color=FIELD, sw=2.0))
    f.append(text(360, T_m + 12, "110.000 с", size=11, bold=True, color=INK))
    f.append(text(360, T_m + 55, "t_mono_B", size=10, color=MUTED))

    # Момент NTP-синхронізації
    f.append(line(520, T_m + 10, 520, T_m + 50, color=FIELD, sw=2.0, dash="4 3"))
    f.append(text(520, T_m - 5, "NTP: оновлення base_offset (t_mono незмінний)", size=11, bold=True, color=FIELD))

    # Подія 3: 118.000 с
    f.append(line(680, T_m + 20, 680, T_m + 40, color=FIELD, sw=2.0))
    f.append(text(680, T_m + 12, "118.000 с", size=11, bold=True, color=FIELD))
    f.append(text(680, T_m + 55, "t_mono_C", size=10, bold=True, color=FIELD))

    tb_ok, _, _ = textbox(520, T_m + 105, "ГАРАНТІЯ МОНОТОННОСТІ: Δt = t_mono_C − t_mono_B = +8.000 с > 0 завжди!\nКалендарний час обчислюється як t_wall = t_mono + base_offset. Монотонний лічильник ніколи не йде назад.",
                          size=11, fill="#eafaf1", stroke=FIELD, sw=1.3, min_w=780)
    f.append(tb_ok)

    render(os.path.join(IMG, "monotonic-vs-wall-timeline.svg"), W, H, *f)


def main():
    fig_prescaler_bcd()
    fig_crystal_drift()
    fig_smooth_calibration()
    fig_monotonic_vs_wall()
    print("Всі 4 фігури згенеровано в %s" % IMG)

if __name__ == "__main__":
    main()
