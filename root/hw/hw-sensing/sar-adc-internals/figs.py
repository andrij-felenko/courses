# -*- coding: utf-8 -*-
"""Фігури до статті «SAR АЦП зсередини» (sar-adc-internals-d.md).
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math

# Чотири рівні вгору до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ACCENT_BLUE = "#1a56db"
ACCENT_GREEN = "#0e9f6e"
ACCENT_RED = "#e02424"
ACCENT_ORANGE = "#d97706"
ACCENT_PURPLE = "#7e3af2"
BG_PANEL = "#f9fafb"

def polyline(pts, color=LINE, sw=1.8, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (s, fill, stroke, sw)

def ground_symbol(x, y, sw=1.5, color=LINE):
    return (line(x, y, x, y + 10, color=color, sw=sw) +
            line(x - 12, y + 10, x + 12, y + 10, color=color, sw=sw) +
            line(x - 8, y + 14, x + 8, y + 14, color=color, sw=sw) +
            line(x - 4, y + 18, x + 4, y + 18, color=color, sw=sw))

def capacitor_symbol(x, y, w=20, h=10, vertical=True, color=LINE, sw=1.8):
    if vertical:
        # Вертикальний конденсатор: дві горизонтальні пластини
        p1 = line(x - w / 2, y - h / 2, x + w / 2, y - h / 2, color=color, sw=sw)
        p2 = line(x - w / 2, y + h / 2, x + w / 2, y + h / 2, color=color, sw=sw)
        return p1 + p2
    else:
        # Горизонтальний: дві вертикальні пластини
        p1 = line(x - w / 2, y - h / 2, x - w / 2, y + h / 2, color=color, sw=sw)
        p2 = line(x + w / 2, y - h / 2, x + w / 2, y + h / 2, color=color, sw=sw)
        return p1 + p2

# ── 1. Архітектура SAR АЦП ──────────────────────────────────────────────────
def fig_sar_architecture():
    W, H = 940, 480
    f = []

    # Заголовок та підзаголовок
    f.append(text(W / 2, 26, "Внутрішня архітектура SAR АЦП на базі матриці CDAC", size=17, bold=True))
    f.append(text(W / 2, 48, "Матриця бінарно зважених конденсаторів одночасно виконує роль вибірки-зберігання та ЦАП", size=12, color=MUTED, italic=True))

    # Рамка чипа АЦП
    f.append(rect(40, 70, 860, 380, fill=BG_PANEL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(60, 92, "Кристал SAR АЦП", size=13, bold=True, color=MUTED, anchor="start"))

    # Входи зліва
    # Вхід Vin
    f.append(line(10, 140, 100, 140, color=ACCENT_BLUE, sw=2.5))
    f.append(circle(10, 140, 4, fill=ACCENT_BLUE, stroke=ACCENT_BLUE))
    f.append(text(12, 126, "Vin", size=13, bold=True, color=ACCENT_BLUE, anchor="start"))

    # Вхід Vref
    f.append(line(10, 200, 100, 200, color=ACCENT_RED, sw=2.5))
    f.append(circle(10, 200, 4, fill=ACCENT_RED, stroke=ACCENT_RED))
    f.append(text(12, 186, "Vref", size=13, bold=True, color=ACCENT_RED, anchor="start"))

    # Земля GND
    f.append(line(10, 260, 100, 260, color=INK, sw=2.0))
    f.append(circle(10, 260, 4, fill=INK, stroke=INK))
    f.append(text(12, 246, "AGND", size=13, bold=True, color=INK, anchor="start"))

    # Шини комутації
    f.append(line(100, 140, 470, 140, color=ACCENT_BLUE, sw=1.8, dash="4 3"))
    f.append(text(480, 144, "Шина Vin (вибірка)", size=11, color=ACCENT_BLUE, anchor="start"))

    f.append(line(100, 200, 470, 200, color=ACCENT_RED, sw=1.8, dash="4 3"))
    f.append(text(480, 204, "Шина Vref (зважування)", size=11, color=ACCENT_RED, anchor="start"))

    f.append(line(100, 260, 470, 260, color=INK, sw=1.8, dash="4 3"))
    f.append(text(480, 264, "Шина GND", size=11, color=INK, anchor="start"))

    # Блок CDAC (матриця конденсаторів)
    caps = [
        ("MSB (8C)", 140, "b3"),
        ("4C", 220, "b2"),
        ("2C", 300, "b1"),
        ("1C", 380, "b0"),
        ("Cdummy", 450, "gnd")
    ]

    # Спільна шина верхніх обкладок (Top Plate / Вузол Vx)
    f.append(line(140, 330, 560, 330, color=ACCENT_PURPLE, sw=3.0))
    f.append(text(540, 318, "Вузол Vx (Top Plate)", size=12, bold=True, color=ACCENT_PURPLE, anchor="end"))

    # Ключ вибірки на верхній обкладці (Sample Switch)
    f.append(line(500, 330, 500, 355, color=ACCENT_PURPLE, sw=2.0))
    # Перемикач S_sample
    f.append(line(500, 355, 485, 380, color=ACCENT_PURPLE, sw=2.0))
    f.append(circle(500, 355, 3, fill=ACCENT_PURPLE, stroke=ACCENT_PURPLE))
    f.append(circle(500, 390, 3, fill=ACCENT_PURPLE, stroke=ACCENT_PURPLE))
    f.append(line(500, 390, 500, 405, color=INK, sw=2.0))
    f.append(ground_symbol(500, 405))
    f.append(text(530, 375, "Ключ S_sample", size=11, bold=True, color=ACCENT_PURPLE, anchor="start"))

    for label, cx, bit in caps:
        # Комутатор знизу (3 позиції: Vin, Vref, GND)
        f.append(line(cx, 300, cx, 322, color=ACCENT_PURPLE, sw=2.0))
        # Конденсатор
        f.append(capacitor_symbol(cx, 290, w=24, h=8, vertical=True, color=ACCENT_BLUE, sw=2.2))
        f.append(line(cx, 260, cx, 282, color=INK, sw=2.0))

        # Перемикач
        f.append(circle(cx, 255, 3, fill=LINE, stroke=LINE))
        f.append(line(cx, 255, cx - 10, 210, color=LINE, sw=1.8))
        f.append(circle(cx - 12, 200, 2.5, fill=ACCENT_RED, stroke=ACCENT_RED))
        f.append(circle(cx + 8, 140, 2.5, fill=ACCENT_BLUE, stroke=ACCENT_BLUE))
        f.append(circle(cx, 260, 2.5, fill=INK, stroke=INK))

        # Підпис ємності
        f.append(text(cx, 352, label, size=11, bold=True, color=INK))

    # Компаратор
    comp_x, comp_y = 600, 330
    pts_comp = [(comp_x, comp_y - 35), (comp_x + 60, comp_y), (comp_x, comp_y + 35)]
    f.append(polygon(pts_comp, fill="#ffffff", stroke=LINE, sw=2.0))
    f.append(text(comp_x + 12, comp_y - 12, "+", size=14, bold=True, color=POS))
    f.append(text(comp_x + 12, comp_y + 18, "−", size=14, bold=True, color=NEG))
    f.append(text(comp_x + 28, comp_y + 4, "CMP", size=11, bold=True, color=MUTED))

    # Підключення до компаратора
    f.append(line(560, 330, comp_x, comp_y - 15, color=ACCENT_PURPLE, sw=2.0)) # до (+)
    f.append(line(570, comp_y + 15, comp_x, comp_y + 15, color=INK, sw=2.0))   # до (-)
    f.append(ground_symbol(570, comp_y + 15))

    # Вихід компаратора
    f.append(arrow(comp_x + 60, comp_y, comp_x + 100, comp_y, color=LINE, sw=2.0))
    f.append(text(comp_x + 80, comp_y - 10, "D_out", size=11, bold=True, color=INK))

    # Блок SAR FSM (Логіка послідовного наближення)
    f.append(rect(710, 250, 160, 160, fill="#edf2f7", stroke=LINE, sw=2.0, rx=6))
    f.append(text(790, 275, "SAR FSM & Регістр", size=13, bold=True, color=INK))
    f.append(text(790, 295, "Алгоритм двійкового пошуку", size=10, color=MUTED))
    f.append(text(790, 315, "Такти: N кроків (MSB->LSB)", size=10, color=MUTED))

    # Тактовий сигнал
    f.append(arrow(790, 200, 790, 250, color=INK, sw=1.8))
    f.append(text(790, 190, "CLOCK", size=11, bold=True, color=INK))

    # Лінії зворотного зв'язку керування ключами CDAC
    f.append(polyline([(750, 410), (750, 440), (280, 440), (280, 370)], color=ACCENT_GREEN, sw=1.8, dash="4 3"))
    f.append(arrow(280, 370, 280, 360, color=ACCENT_GREEN, sw=1.8))
    f.append(text(460, 432, "Керування комутаторами розрядів (b_n)", size=11, bold=True, color=ACCENT_GREEN))

    # Вихідний цифровий результат
    f.append(arrow(870, 330, 925, 330, color=ACCENT_BLUE, sw=2.5))
    f.append(text(900, 318, "N-біт код", size=12, bold=True, color=ACCENT_BLUE))
    f.append(text(900, 346, "EOC (End of Conv)", size=10, color=MUTED))

    render(os.path.join(IMG, "sar-architecture.svg"), W, H, *f)

# ── 2. Три фази роботи SAR АЦП ──────────────────────────────────────────────
def fig_charge_redistribution_phases():
    W, H = 940, 380
    f = []

    f.append(text(W / 2, 24, "Фізика перерозподілу заряду в матриці CDAC у трьох фазах", size=17, bold=True))
    f.append(text(W / 2, 44, "Збереження заряду на ізольованому вузлі Top Plate перетворює зважування на зміщення потенціалу", size=12, color=MUTED, italic=True))

    pw, ph = 280, 300
    y_top = 65

    # Фаза 1: Вибірка (Sample)
    x1 = 25
    f.append(rect(x1, y_top, pw, ph, fill=BG_PANEL, stroke=ACCENT_BLUE, sw=1.5, rx=6))
    f.append(text(x1 + pw / 2, y_top + 25, "1. Фаза вибірки (Sample/Track)", size=13, bold=True, color=ACCENT_BLUE))
    f.append(text(x1 + pw / 2, y_top + 45, "Верхня обкладка -> GND, Нижні -> Vin", size=10, color=MUTED))

    # Схема 1
    # Верхня шина на замкненому ключі
    f.append(line(x1 + 40, y_top + 100, x1 + 240, y_top + 100, color=ACCENT_PURPLE, sw=2.5))
    f.append(text(x1 + 140, y_top + 88, "Top Plate (Vx = 0 В)", size=11, bold=True, color=ACCENT_PURPLE))
    f.append(line(x1 + 200, y_top + 100, x1 + 200, y_top + 130, color=INK, sw=2.0))
    f.append(ground_symbol(x1 + 200, y_top + 130))
    f.append(text(x1 + 230, y_top + 125, "S_top ЗАКРИТО", size=9, bold=True, color=ACCENT_GREEN))

    # Конденсатори C_total
    f.append(capacitor_symbol(x1 + 90, y_top + 170, w=36, h=10, color=ACCENT_BLUE, sw=2.2))
    f.append(line(x1 + 90, y_top + 100, x1 + 90, y_top + 160, color=ACCENT_PURPLE, sw=2.0))
    f.append(line(x1 + 90, y_top + 180, x1 + 90, y_top + 220, color=ACCENT_BLUE, sw=2.0))
    f.append(circle(x1 + 90, y_top + 220, 3, fill=ACCENT_BLUE, stroke=ACCENT_BLUE))
    f.append(line(x1 + 90, y_top + 220, x1 + 50, y_top + 220, color=ACCENT_BLUE, sw=2.0))
    f.append(text(x1 + 40, y_top + 224, "Vin", size=12, bold=True, color=ACCENT_BLUE, anchor="end"))
    f.append(text(x1 + 145, y_top + 175, "C_total = 2^N * C", size=11, bold=True, color=INK, anchor="start"))

    # Формула заряду
    f.append(rect(x1 + 20, y_top + 245, pw - 40, 42, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(x1 + pw / 2, y_top + 262, "Q_top = −Vin · C_total", size=12, bold=True, color=ACCENT_RED))
    f.append(text(x1 + pw / 2, y_top + 278, "Заряд зафіксовано на пластинах", size=9, color=MUTED))

    # Фаза 2: Фіксація (Hold / Invert)
    x2 = 330
    f.append(rect(x2, y_top, pw, ph, fill=BG_PANEL, stroke=ACCENT_PURPLE, sw=1.5, rx=6))
    f.append(text(x2 + pw / 2, y_top + 25, "2. Фаза фіксації (Hold/Invert)", size=13, bold=True, color=ACCENT_PURPLE))
    f.append(text(x2 + pw / 2, y_top + 45, "Верхній ключ розімкнено, Нижні -> GND", size=10, color=MUTED))

    # Схема 2
    f.append(line(x2 + 40, y_top + 100, x2 + 240, y_top + 100, color=ACCENT_PURPLE, sw=2.5))
    f.append(text(x2 + 140, y_top + 88, "Top Plate (Ізольовано!)", size=11, bold=True, color=ACCENT_PURPLE))
    # Розімкнений ключ
    f.append(line(x2 + 200, y_top + 100, x2 + 200, y_top + 115, color=INK, sw=2.0))
    f.append(line(x2 + 200, y_top + 115, x2 + 215, y_top + 128, color=INK, sw=2.0)) # розімкнено
    f.append(circle(x2 + 200, y_top + 115, 2.5, fill=INK, stroke=INK))
    f.append(circle(x2 + 200, y_top + 135, 2.5, fill=INK, stroke=INK))
    f.append(ground_symbol(x2 + 200, y_top + 135))
    f.append(text(x2 + 230, y_top + 122, "ВІДКРИТО", size=9, bold=True, color=ACCENT_RED))

    # Конденсатори C_total до GND
    f.append(capacitor_symbol(x2 + 90, y_top + 170, w=36, h=10, color=ACCENT_BLUE, sw=2.2))
    f.append(line(x2 + 90, y_top + 100, x2 + 90, y_top + 160, color=ACCENT_PURPLE, sw=2.0))
    f.append(line(x2 + 90, y_top + 180, x2 + 90, y_top + 220, color=INK, sw=2.0))
    f.append(ground_symbol(x2 + 90, y_top + 220))
    f.append(text(x2 + 145, y_top + 175, "Нижні пластини на GND", size=10, color=INK, anchor="start"))

    # Формула напруги Vx
    f.append(rect(x2 + 20, y_top + 245, pw - 40, 42, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(x2 + pw / 2, y_top + 262, "Vx = −Vin", size=13, bold=True, color=ACCENT_PURPLE))
    f.append(text(x2 + pw / 2, y_top + 278, "Потенціал інвертувався вниз", size=9, color=MUTED))

    # Фаза 3: Проба MSB (Bit Trial)
    x3 = 635
    f.append(rect(x3, y_top, pw, ph, fill=BG_PANEL, stroke=ACCENT_GREEN, sw=1.5, rx=6))
    f.append(text(x3 + pw / 2, y_top + 25, "3. Проба MSB (Бінарний тест)", size=13, bold=True, color=ACCENT_GREEN))
    f.append(text(x3 + pw / 2, y_top + 45, "C_MSB -> Vref, решта лишаються на GND", size=10, color=MUTED))

    # Схема 3: поділ на C_msb та C_rem
    f.append(line(x3 + 30, y_top + 100, x3 + 250, y_top + 100, color=ACCENT_PURPLE, sw=2.5))
    f.append(text(x3 + 140, y_top + 88, "Top Plate -> до CMP (+)", size=11, bold=True, color=ACCENT_PURPLE))

    # C_MSB (C_tot / 2) до Vref
    f.append(capacitor_symbol(x3 + 75, y_top + 170, w=28, h=10, color=ACCENT_RED, sw=2.2))
    f.append(line(x3 + 75, y_top + 100, x3 + 75, y_top + 160, color=ACCENT_PURPLE, sw=2.0))
    f.append(line(x3 + 75, y_top + 180, x3 + 75, y_top + 215, color=ACCENT_RED, sw=2.0))
    f.append(circle(x3 + 75, y_top + 215, 3, fill=ACCENT_RED, stroke=ACCENT_RED))
    f.append(text(x3 + 75, y_top + 232, "Vref", size=11, bold=True, color=ACCENT_RED))
    f.append(text(x3 + 75, y_top + 148, "C_MSB", size=10, bold=True, color=ACCENT_RED))

    # C_rem (C_tot / 2) до GND
    f.append(capacitor_symbol(x3 + 175, y_top + 170, w=28, h=10, color=INK, sw=2.2))
    f.append(line(x3 + 175, y_top + 100, x3 + 175, y_top + 160, color=ACCENT_PURPLE, sw=2.0))
    f.append(line(x3 + 175, y_top + 180, x3 + 175, y_top + 215, color=INK, sw=2.0))
    f.append(ground_symbol(x3 + 175, y_top + 215))
    f.append(text(x3 + 175, y_top + 148, "C_rest", size=10, bold=True, color=INK))

    # Формула напруги проби
    f.append(rect(x3 + 15, y_top + 245, pw - 30, 42, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(x3 + pw / 2, y_top + 262, "Vx = −Vin + 0.5 · Vref", size=12, bold=True, color=ACCENT_GREEN))
    f.append(text(x3 + pw / 2, y_top + 278, "Якщо Vx < 0 -> Vin >= Vref/2 (MSB=1)", size=9, color=MUTED))

    render(os.path.join(IMG, "charge-redistribution-phases.svg"), W, H, *f)

# ── 3. Траєкторія напруги вузла Vx ─────────────────────────────────────────
def fig_bit_trial_trajectory():
    W, H = 920, 420
    f = []

    f.append(text(W / 2, 25, "Збіжність напруги вузла Vx під час порозрядного зважування (SAR)", size=17, bold=True))
    f.append(text(W / 2, 47, "Приклад 4-бітного перетворення для Vin = 0.65 Vref (код 1010b = 10)", size=12, color=MUTED, italic=True))

    # Осі координат
    x0, y0 = 90, 220 # лінія 0 В по центру
    x_max = 840
    y_top = 80
    y_bot = 370

    # Сітка та опорні рівні
    f.append(line(x0, y0, x_max, y0, color=ACCENT_RED, sw=2.0, dash="5 3")) # лінія 0 В
    f.append(text(x0 - 10, y0 + 4, "0 В (Поріг CMP)", size=11, bold=True, color=ACCENT_RED, anchor="end"))

    f.append(line(x0, y_top, x0, y_bot, color=INK, sw=2.0))
    f.append(arrow(x0, y_top, x0, y_top - 15, color=INK, sw=2.0))
    f.append(text(x0 - 10, y_top - 5, "Напруга Vx", size=11, bold=True, color=INK, anchor="end"))

    f.append(line(x0, y_bot, x_max, y_bot, color=INK, sw=2.0))
    f.append(arrow(x_max, y_bot, x_max + 20, y_bot, color=INK, sw=2.0))
    f.append(text(x_max + 15, y_bot + 18, "Такти (Кроки SAR)", size=11, bold=True, color=INK))

    # Стовпці кроків
    steps = [
        ("Hold", 160, "−0.65 Vref", "Старт: Vx = −Vin"),
        ("Такт 1 (MSB)", 300, "−0.15 Vref", "+0.50 Vref -> Vx < 0 -> Біт 3 = 1"),
        ("Такт 2 (b2)", 440, "+0.10 Vref", "+0.25 Vref -> Vx > 0 -> Біт 2 = 0 (скид)"),
        ("Такт 3 (b1)", 580, "−0.025 Vref", "+0.125 Vref -> Vx < 0 -> Біт 1 = 1"),
        ("Такт 4 (LSB)", 720, "+0.037 Vref", "+0.0625 Vref -> Vx > 0 -> Біт 0 = 0"),
        ("Результат", 830, "0.625 Vref", "Код 1010b = 10")
    ]

    for label, sx, val_str, desc in steps:
        f.append(line(sx, y_top, sx, y_bot, color="#e5e7eb", sw=1.0, dash="3 3"))
        f.append(text(sx, y_bot + 18, label, size=10, bold=True, color=INK))

    # Траєкторія напруги
    pts_real = [
        (160, 337),
        (300, 247), # лишили MSB=1
        (440, 202), # пробували b2=1 (Vx > 0)
        (460, 247), # скинули b2=0
        (580, 224.5), # спробували b1=1 (Vx < 0), лишили
        (720, 213.25), # спробували b0=1 (Vx > 0)
        (740, 224.5), # скинули b0=0
        (830, 224.5)
    ]

    f.append(polyline(pts_real, color=ACCENT_BLUE, sw=2.8))

    # Точки та мітки рішень компаратора
    # Точка 1: Hold
    f.append(circle(160, 337, 5, fill=ACCENT_BLUE, stroke="#ffffff", sw=1.5))
    f.append(text(160, 355, "−0.65 Vref", size=10, bold=True, color=ACCENT_BLUE))

    # Точка 2: MSB trial
    f.append(circle(300, 247, 5, fill=ACCENT_GREEN, stroke="#ffffff", sw=1.5))
    f.append(text(300, 270, "Vx < 0 -> ЗБЕРЕГТИ (1)", size=10, bold=True, color=ACCENT_GREEN))

    # Точка 3: b2 trial
    f.append(circle(440, 202, 5, fill=ACCENT_RED, stroke="#ffffff", sw=1.5))
    f.append(text(440, 185, "Vx > 0 -> СКИД (0)", size=10, bold=True, color=ACCENT_RED))

    # Точка 4: b1 trial
    f.append(circle(580, 224.5, 5, fill=ACCENT_GREEN, stroke="#ffffff", sw=1.5))
    f.append(text(580, 248, "Vx < 0 -> ЗБЕРЕГТИ (1)", size=10, bold=True, color=ACCENT_GREEN))

    # Точка 5: LSB trial
    f.append(circle(720, 213.25, 5, fill=ACCENT_RED, stroke="#ffffff", sw=1.5))
    f.append(text(720, 195, "Vx > 0 -> СКИД (0)", size=10, bold=True, color=ACCENT_RED))

    # Фінальна область похибки кванта 1 LSB
    f.append(rect(800, 208, 60, 33, fill="#e1effe", stroke=ACCENT_BLUE, sw=1.2, rx=4))
    f.append(text(830, 221, "±0.5 LSB", size=10, bold=True, color=ACCENT_BLUE))
    f.append(text(830, 234, "Збіжність", size=9, color=MUTED))

    render(os.path.join(IMG, "bit-trial-trajectory.svg"), W, H, *f)

# ── 4. Експоненційне встановлення RC ────────────────────────────────────────
def fig_sampling_settling_rc():
    W, H = 920, 420
    f = []

    f.append(text(W / 2, 25, "Динаміка заряду Csample та похибка недовстановлення", size=17, bold=True))
    f.append(text(W / 2, 47, "Для N-бітної точності час вибірки t_acq мусить становити не менше (N + 1) * ln(2) сталих часу tau", size=12, color=MUTED, italic=True))

    # Схема еквівалентного кола зліва
    sx, sy = 50, 90
    f.append(rect(sx, sy, 260, 280, fill=BG_PANEL, stroke=MUTED, sw=1.5, rx=6))
    f.append(text(sx + 130, sy + 25, "Еквівалентне коло вибірки", size=12, bold=True, color=INK))

    # Джерело Vin
    f.append(circle(sx + 40, sy + 140, 16, fill="#ffffff", stroke=ACCENT_BLUE, sw=2.0))
    f.append(text(sx + 40, sy + 145, "Vin", size=11, bold=True, color=ACCENT_BLUE))
    f.append(ground_symbol(sx + 40, sy + 156))

    # Резистор R_total = R_src + R_sw
    f.append(line(sx + 56, sy + 140, sx + 90, sy + 140, color=INK, sw=2.0))
    f.append(rect(sx + 90, sy + 130, 50, 20, fill="#ffffff", stroke=INK, sw=2.0, rx=2))
    f.append(text(sx + 115, sy + 144, "R_tot", size=10, bold=True, color=INK))
    f.append(text(sx + 115, sy + 120, "Rsrc + Rsw", size=9, color=MUTED))

    # Ключ
    f.append(line(sx + 140, sy + 140, sx + 165, sy + 140, color=INK, sw=2.0))
    f.append(circle(sx + 165, sy + 140, 2.5, fill=INK, stroke=INK))
    f.append(line(sx + 165, sy + 140, sx + 185, sy + 125, color=ACCENT_GREEN, sw=2.0)) # ключ
    f.append(circle(sx + 190, sy + 140, 2.5, fill=INK, stroke=INK))
    f.append(text(sx + 175, sy + 115, "S_sample", size=9, bold=True, color=ACCENT_GREEN))

    # Конденсатор C_sample
    f.append(line(sx + 190, sy + 140, sx + 220, sy + 140, color=INK, sw=2.0))
    f.append(line(sx + 220, sy + 140, sx + 220, sy + 165, color=INK, sw=2.0))
    f.append(capacitor_symbol(sx + 220, sy + 175, w=24, h=8, vertical=True, color=ACCENT_PURPLE, sw=2.2))
    f.append(line(sx + 220, sy + 185, sx + 220, sy + 210, color=INK, sw=2.0))
    f.append(ground_symbol(sx + 220, sy + 210))
    f.append(text(sx + 220, sy + 235, "Csample", size=10, bold=True, color=ACCENT_PURPLE))

    # Формула tau
    f.append(rect(sx + 15, sy + 215, 95, 45, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(sx + 62, sy + 232, "tau = Rtot · C", size=10, bold=True, color=INK))
    f.append(text(sx + 62, sy + 248, "Стала часу RC", size=9, color=MUTED))

    # Графік кривої справа
    gx0, gy0 = 390, 340 # початок координат графіка
    gw, gh = 490, 250
    gy_top = gy0 - gh

    f.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=2.0))
    f.append(arrow(gx0 + gw, gy0, gx0 + gw + 20, gy0, color=INK, sw=2.0))
    f.append(text(gx0 + gw + 10, gy0 + 18, "Час t (в частках tau)", size=11, bold=True, color=INK))

    f.append(line(gx0, gy0, gx0, gy_top - 10, color=INK, sw=2.0))
    f.append(arrow(gx0, gy_top - 10, gx0, gy_top - 25, color=INK, sw=2.0))
    f.append(text(gx0 - 15, gy_top - 15, "Vc(t)", size=11, bold=True, color=INK, anchor="end"))

    # Лінія асимптоти Vin (100%)
    f.append(line(gx0, gy_top, gx0 + gw, gy_top, color=ACCENT_RED, sw=1.5, dash="6 4"))
    f.append(text(gx0 - 10, gy_top + 4, "Vin (100%)", size=11, bold=True, color=ACCENT_RED, anchor="end"))

    # Побудова експоненти Vc(t) = Vin * (1 - exp(-t/tau))
    pts_exp = []
    for t_step in range(0, 141):
        t_val = t_step / 10.0 # 0.0 .. 14.0
        x_pt = gx0 + (t_val / 14.0) * gw
        v_norm = 1.0 - math.exp(-t_val)
        y_pt = gy0 - v_norm * gh
        pts_exp.append((x_pt, y_pt))

    f.append(polyline(pts_exp, color=ACCENT_BLUE, sw=3.0))

    # Смуги порогів точності
    tau_milestones = [
        (7.62, "10-біт (7.6 tau)", ACCENT_ORANGE, "Похибка < 0.05%"),
        (9.01, "12-біт (9.0 tau)", ACCENT_GREEN, "Похибка < 0.012%"),
        (11.78, "16-біт (11.8 tau)", ACCENT_PURPLE, "Похибка < 0.0008%")
    ]

    for tau_k, lbl, col, err_str in tau_milestones:
        x_k = gx0 + (tau_k / 14.0) * gw
        y_k = gy0 - (1.0 - math.exp(-tau_k)) * gh
        f.append(line(x_k, gy0, x_k, gy_top, color=col, sw=1.5, dash="4 3"))
        f.append(circle(x_k, y_k, 4, fill=col, stroke="#ffffff", sw=1.5))
        f.append(text(x_k, gy0 + 16, "%.1ftau" % tau_k, size=10, bold=True, color=col))
        f.append(rect(x_k - 45, gy_top + (tau_milestones.index((tau_k, lbl, col, err_str)) * 32) + 15, 95, 26, fill="#ffffff", stroke=col, sw=1.0, rx=3))
        f.append(text(x_k + 2, gy_top + (tau_milestones.index((tau_k, lbl, col, err_str)) * 32) + 32, lbl, size=9, bold=True, color=col))

    render(os.path.join(IMG, "sampling-settling-rc.svg"), W, H, *f)

# ── 5. Вхідний драйвер та захисний RC-фільтр ────────────────────────────────
def fig_adc_input_driver_kickback():
    W, H = 940, 440
    f = []

    f.append(text(W / 2, 25, "Схемотехніка драйвера АЦП та демпфування комутаційного удару", size=17, bold=True))
    f.append(text(W / 2, 47, "Зовнішній конденсатор Cext живить імпульсний заряд Csample, а Rext ізолює підсилювач від втрати стійкості", size=12, color=MUTED, italic=True))

    # 1. Джерело сигналу
    f.append(rect(20, 80, 140, 320, fill=BG_PANEL, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(90, 105, "Джерело сигналу", size=11, bold=True, color=INK))
    f.append(circle(90, 160, 14, fill="#ffffff", stroke=ACCENT_BLUE, sw=1.8))
    f.append(text(90, 164, "Vsig", size=10, bold=True, color=ACCENT_BLUE))
    f.append(ground_symbol(90, 174))

    f.append(line(90, 146, 90, 125, color=INK, sw=1.8))
    f.append(line(90, 125, 120, 125, color=INK, sw=1.8))
    f.append(rect(120, 117, 30, 16, fill="#ffffff", stroke=INK, sw=1.5, rx=2))
    f.append(text(135, 129, "Rsrc", size=9, bold=True, color=INK))
    f.append(line(150, 125, 180, 125, color=INK, sw=1.8))
    f.append(text(90, 230, "Високий або", size=9, color=MUTED))
    f.append(text(90, 245, "невідомий опір", size=9, color=MUTED))
    f.append(text(90, 260, "давача (до 100 кОм)", size=9, color=MUTED))

    # 2. Драйвер АЦП (Операційний підсилювач)
    f.append(rect(180, 80, 200, 320, fill=BG_PANEL, stroke=ACCENT_BLUE, sw=1.5, rx=6))
    f.append(text(280, 105, "Драйвер АЦП (ОП)", size=12, bold=True, color=ACCENT_BLUE))

    # Трикутник ОП
    op_x, op_y = 240, 180
    pts_op = [(op_x, op_y - 30), (op_x + 50, op_y), (op_x, op_y + 30)]
    f.append(polygon(pts_op, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(op_x + 10, op_y - 12, "+", size=13, bold=True, color=POS))
    f.append(text(op_x + 10, op_y + 16, "−", size=13, bold=True, color=NEG))

    # З'єднання входу
    f.append(line(160, 125, 210, 125, color=INK, sw=1.8))
    f.append(line(210, 125, 210, op_y - 15, color=INK, sw=1.8))
    f.append(line(210, op_y - 15, op_x, op_y - 15, color=INK, sw=1.8))

    # Негативний зворотний зв'язок (буфер)
    f.append(line(op_x + 50, op_y, op_x + 70, op_y, color=INK, sw=1.8))
    f.append(circle(op_x + 70, op_y, 2.5, fill=INK, stroke=INK))
    f.append(polyline([(op_x + 70, op_y), (op_x + 70, op_y + 40), (op_x - 15, op_y + 40), (op_x - 15, op_y + 15), (op_x, op_y + 15)], color=INK, sw=1.8))

    f.append(text(280, 270, "Низький вихідний Zout", size=9, bold=True, color=INK))
    f.append(text(280, 285, "Швидке наростання (Slew)", size=9, color=MUTED))
    f.append(text(280, 300, "Смуга GBW > 10..50 МГц", size=9, color=MUTED))

    # 3. Зовнішній RC-ланцюг демпфування
    f.append(rect(400, 80, 200, 320, fill=BG_PANEL, stroke=ACCENT_GREEN, sw=1.5, rx=6))
    f.append(text(500, 105, "Зовнішній RC демпфер", size=12, bold=True, color=ACCENT_GREEN))

    # Резистор R_ext (ізоляція та обмеження струму)
    f.append(line(op_x + 70, op_y, 440, op_y, color=INK, sw=2.0))
    f.append(rect(440, op_y - 10, 45, 20, fill="#ffffff", stroke=ACCENT_GREEN, sw=2.0, rx=2))
    f.append(text(462, op_y + 4, "Rext", size=10, bold=True, color=ACCENT_GREEN))
    f.append(text(462, op_y - 16, "10..50 Ом", size=9, color=MUTED))

    # Конденсатор C_ext (резервуар заряду)
    f.append(line(485, op_y, 540, op_y, color=INK, sw=2.0))
    f.append(circle(540, op_y, 3, fill=INK, stroke=INK))
    f.append(line(540, op_y, 540, op_y + 35, color=INK, sw=2.0))
    f.append(capacitor_symbol(540, op_y + 45, w=28, h=8, vertical=True, color=ACCENT_GREEN, sw=2.2))
    f.append(line(540, op_y + 55, 540, op_y + 80, color=INK, sw=2.0))
    f.append(ground_symbol(540, op_y + 80))
    f.append(text(540, op_y + 105, "Cext >= 20 · Csample", size=10, bold=True, color=ACCENT_GREEN))
    f.append(text(540, op_y + 120, "(наприклад, 1 нФ NPO)", size=9, color=MUTED))

    f.append(text(500, 340, "Поглинає зарядний удар", size=9, bold=True, color=ACCENT_GREEN))
    f.append(text(500, 355, "Запобігає генерації ОП", size=9, color=MUTED))

    # 4. Внутрішня структура АЦП
    f.append(rect(620, 80, 300, 320, fill="#edf2f7", stroke=ACCENT_PURPLE, sw=1.8, rx=6))
    f.append(text(770, 105, "Кристал SAR АЦП", size=12, bold=True, color=ACCENT_PURPLE))

    # Піновий вивід (ADC_IN)
    f.append(line(540, op_y, 640, op_y, color=INK, sw=2.0))
    f.append(circle(640, op_y, 4, fill=INK, stroke=INK))
    f.append(text(640, op_y - 12, "Вивід ADC_IN", size=10, bold=True, color=INK))

    # Внутрішній перемикач R_sw / Мультиплексор
    f.append(line(640, op_y, 675, op_y, color=INK, sw=2.0))
    f.append(rect(675, op_y - 8, 35, 16, fill="#ffffff", stroke=INK, sw=1.5, rx=2))
    f.append(text(692, op_y + 4, "Rsw", size=9, bold=True, color=INK))

    # Ключ дискретизації
    f.append(line(710, op_y, 735, op_y, color=INK, sw=2.0))
    f.append(circle(735, op_y, 2.5, fill=INK, stroke=INK))
    f.append(line(735, op_y, 755, op_y - 18, color=ACCENT_RED, sw=2.0)) # перемикач
    f.append(circle(760, op_y, 2.5, fill=INK, stroke=INK))
    f.append(text(745, op_y - 25, "S_sample", size=9, bold=True, color=ACCENT_RED))

    # Конденсатор C_sample
    f.append(line(760, op_y, 790, op_y, color=INK, sw=2.0))
    f.append(line(790, op_y, 790, op_y + 35, color=INK, sw=2.0))
    f.append(capacitor_symbol(790, op_y + 45, w=24, h=8, vertical=True, color=ACCENT_PURPLE, sw=2.2))
    f.append(line(790, op_y + 55, 790, op_y + 80, color=INK, sw=2.0))
    f.append(ground_symbol(790, op_y + 80))
    f.append(text(790, op_y + 105, "Csample (~5..20 пФ)", size=10, bold=True, color=ACCENT_PURPLE))

    # Імпульс розряду (Kickback)
    f.append(rect(650, 230, 240, 50, fill="#ffffff", stroke=ACCENT_RED, sw=1.2, rx=4))
    f.append(text(770, 250, "Комутаційний удар (Kickback):", size=10, bold=True, color=ACCENT_RED))
    f.append(text(770, 268, "delta_V = Vin · Csample / (Cext + Csample)", size=9, color=INK))

    render(os.path.join(IMG, "adc-input-driver-kickback.svg"), W, H, *f)

if __name__ == "__main__":
    fig_sar_architecture()
    fig_charge_redistribution_phases()
    fig_bit_trial_trajectory()
    fig_sampling_settling_rc()
    fig_adc_input_driver_kickback()
    print("Всі фігури згенеровано успішно у ./img/")
