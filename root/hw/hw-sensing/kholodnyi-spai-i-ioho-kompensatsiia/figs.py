# -*- coding: utf-8 -*-
"""Фігури до теми «Холодний спай і його компенсація».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і примітиви — з svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори для металів та термозон
CHROMEL = "#9b59b6"     # Хромель (Ni-Cr, позитивний провідник типу K)
ALUMEL  = "#d35400"     # Алюмель (Ni-Al, негативний провідник типу K)
COPPER  = "#b87333"     # Мідь (доріжки друкованої плати)
HOT_BG  = "#fdecea"     # Зона нагріву
COLD_BG = "#eaf2fd"     # Зона ізотермічного блоку
PCB_BG  = "#eef6ef"     # Друкована плата


# ── 1. Електрична схема та виникнення паразитної ЕРС на клемах ──────────────
def fig_cjc_circuit_problem():
    W, H = 820, 360
    f = [
        rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1.2, rx=8),
        text(W / 2, 32, "Фізика холодного спаю: виникнення паразитної термо-ЕРС на клемах",
             size=15, bold=True)
    ]

    # Зона гарячого спаю (зліва)
    f.append(rect(30, 60, 180, 240, fill=HOT_BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(120, 85, "Гарячий спай (T_hot)", size=12, color=POS, bold=True))
    f.append(text(120, 102, "Об'єкт вимірювання (напр. 500 °C)", size=10, color=MUTED, italic=True))

    # Спай металів A і B
    f.append(circle(60, 180, 8, fill=POS, stroke=LINE, sw=1.8))
    f.append(text(60, 184, "J₁", size=10, color="#ffffff", bold=True))
    f.append(text(60, 205, "Спай A-B", size=10.5, color=POS, bold=True))

    # Провідники термопари
    # Провідник A (Хромель, +)
    f.append(line(60, 180, 100, 140, color=CHROMEL, sw=3))
    f.append(line(100, 140, 400, 140, color=CHROMEL, sw=3))
    f.append(text(250, 130, "Провідник A (Хромель, KP)", size=11, color=CHROMEL, bold=True))

    # Провідник B (Алюмель, −)
    f.append(line(60, 180, 100, 220, color=ALUMEL, sw=3))
    f.append(line(100, 220, 400, 220, color=ALUMEL, sw=3))
    f.append(text(250, 240, "Провідник B (Алюмель, KN)", size=11, color=ALUMEL, bold=True))

    # Градієнт температури вздовж дротів
    f.append(arrow(190, 180, 350, 180, color=MUTED, sw=1.5))
    f.append(text(270, 172, "Температурний градієнт dT/dx", size=10, color=MUTED, italic=True))

    # Зона ізотермічного блоку / клемника плати (справа)
    f.append(rect(380, 60, 410, 240, fill=COLD_BG, stroke=NEG, sw=1.5, rx=6))
    f.append(text(585, 85, "Ізотермічний блок на платі (T_cjc)", size=12, color=NEG, bold=True))
    f.append(text(585, 102, "Клеми підключення до мідних доріжок (напр. 25 °C)", size=10, color=MUTED, italic=True))

    # Клема 1 (Хромель -> Мідь)
    f.append(circle(400, 140, 7, fill=NEG, stroke=LINE, sw=1.8))
    f.append(text(400, 144, "J₂", size=9, color="#ffffff", bold=True))
    f.append(text(425, 128, "Спай Хромель–Мідь", size=10.5, color=INK, bold=True))
    f.append(text(425, 143, "(T_cjc1)", size=9.5, color=MUTED))

    # Клема 2 (Алюмель -> Мідь)
    f.append(circle(400, 220, 7, fill=NEG, stroke=LINE, sw=1.8))
    f.append(text(400, 224, "J₃", size=9, color="#ffffff", bold=True))
    f.append(text(425, 235, "Спай Алюмель–Мідь", size=10.5, color=INK, bold=True))
    f.append(text(425, 250, "(T_cjc2)", size=9.5, color=MUTED))

    # Мідні доріжки до АЦП / вольтметра
    f.append(line(400, 140, 640, 140, color=COPPER, sw=2.5))
    f.append(text(520, 130, "Мідна доріжка (Cu)", size=10, color=COPPER, bold=True))

    f.append(line(400, 220, 640, 220, color=COPPER, sw=2.5))
    f.append(text(520, 212, "Мідна доріжка (Cu)", size=10, color=COPPER, bold=True))

    # Локальний сенсор температури між клемами
    tb, _, _ = textbox(490, 180, "Локальний сенсор\n(RTD / NTC / IC)\nміряє T_cjc",
                       size=10, pad=6, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    f.append(tb)
    f.append(line(490, 155, 490, 140, color=FIELD, sw=1.2, dash="2,2"))
    f.append(line(490, 205, 490, 220, color=FIELD, sw=1.2, dash="2,2"))

    # Вольтметр / АЦП
    f.append(rect(640, 120, 120, 120, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    f.append(text(700, 148, "Прецизійний", size=10, color=INK))
    f.append(text(700, 164, "АЦП / Вольтметр", size=11, color=INK, bold=True))
    f.append(circle(700, 195, 16, fill="#f8f9fa", stroke=NEG, sw=1.5))
    f.append(text(700, 200, "V", size=13, color=NEG, bold=True))

    # Результуюча формула внизу
    f.append(text(W / 2, 325,
                  "Виміряна напруга: V_meas = V(T_hot) − V(T_cjc)  →  без знання T_cjc визначити T_hot неможливо!",
                  size=12, color=POS, bold=True))

    render(os.path.join(IMG, "cjc-circuit-problem.svg"), W, H, *f)


# ── 2. Топологія друкованої плати для ізотермічного блоку ────────────────────
def fig_isothermal_block_pcb():
    W, H = 820, 380
    f = [
        rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1.2, rx=8),
        text(W / 2, 32, "Тепловий дизайн ізотермічного блоку на друкованій платі",
             size=15, bold=True)
    ]

    # Корпус плати (PCB)
    f.append(rect(30, 55, W - 60, 285, fill=PCB_BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(70, 78, "FR-4 PCB", size=11, color=FIELD, bold=True))

    # Ліва частина: джерело тепла (DC-DC / LDO / MCU)
    f.append(rect(50, 100, 180, 215, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    f.append(text(140, 125, "Гаряча зона плати", size=12, color=POS, bold=True))
    f.append(rect(80, 145, 120, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(140, 168, "DC-DC / LDO", size=11, color=INK, bold=True))
    f.append(text(140, 183, "T_board ≈ 45...60 °C", size=9.5, color=POS))

    f.append(rect(80, 215, 120, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(140, 238, "MCU / Процесор", size=11, color=INK, bold=True))
    f.append(text(140, 253, "Джерело тепла", size=9.5, color=POS))

    # Теплові хвилі вправо
    f.append(text(140, 295, "Паразитний тепловий потік →", size=10, color=POS, italic=True))

    # Теплові прорізи (Thermal relief routing slots)
    f.append(rect(255, 90, 16, 235, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(263, 210, "Фрезерований проріз (Slot) — бар'єр для тепла",
                  size=10, color=LINE, bold=True, anchor="middle"))

    # Права частина: Ізотермічний острів (Isothermal copper plane)
    f.append(rect(300, 85, 480, 245, fill="#eaf2fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(540, 110, "Ізотермічний острів (Isothermal Island)", size=13, color=NEG, bold=True))
    f.append(text(540, 126, "Суцільний мідний полігон у внутрішніх шарах + теплові перехідні отвори",
                  size=10, color=MUTED, italic=True))

    # Гвинтовий клемник (Terminal Block)
    f.append(rect(330, 145, 120, 150, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    f.append(text(390, 168, "Клемник", size=11, color=INK, bold=True))

    # Клема +
    f.append(circle(390, 195, 14, fill="#e8eaed", stroke=LINE, sw=1.5))
    f.append(text(390, 200, "+", size=15, color=POS, bold=True))
    f.append(text(340, 198, "Хромель", size=9, color=CHROMEL, anchor="end"))

    # Клема -
    f.append(circle(390, 255, 14, fill="#e8eaed", stroke=LINE, sw=1.5))
    f.append(text(390, 260, "−", size=15, color=NEG, bold=True))
    f.append(text(340, 258, "Алюмель", size=9, color=ALUMEL, anchor="end"))

    # Локальний термодатчик (розміщений впритул між клемами)
    f.append(rect(480, 205, 90, 40, fill="#ffffff", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(525, 222, "RTD / NTC", size=11, color=FIELD, bold=True))
    f.append(text(525, 236, "Сенсор T_cjc", size=9.5, color=FIELD))

    # Теплові зв'язки (vias)
    f.append(line(405, 195, 480, 220, color=NEG, sw=2, dash="3,3"))
    f.append(line(405, 255, 480, 230, color=NEG, sw=2, dash="3,3"))
    f.append(text(442, 180, "Теплове", size=9.5, color=NEG, bold=True))
    f.append(text(442, 192, "стягування", size=9.5, color=NEG, bold=True))

    # Мікросхема АЦП / фронтенд
    f.append(rect(610, 165, 150, 120, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    f.append(text(685, 190, "MAX31856 / АЦП", size=11, color=INK, bold=True))
    f.append(text(685, 208, "Диференційний", size=10, color=MUTED))
    f.append(text(685, 222, "24-біт Sigma-Delta", size=10, color=MUTED))
    f.append(text(685, 245, "I2C / SPI до MCU", size=10, color=FIELD, bold=True))

    # Доріжки сигналу від клем до АЦП
    f.append(line(405, 195, 610, 195, color=COPPER, sw=2))
    f.append(line(405, 255, 610, 255, color=COPPER, sw=2))

    # Підпис знизу
    f.append(text(W / 2, 358,
                  "Правило: мінімум теплового градієнта між клемами + максимальний тепловий контакт із сенсором T_cjc",
                  size=11, color=INK, bold=True))

    render(os.path.join(IMG, "isothermal-block-pcb.svg"), W, H, *f)


# ── 3. Порівняння алгоритмів: помилка простого додавання проти додавання ЕРС ─
def fig_cjc_math_flow():
    W, H = 820, 360
    f = [
        rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1.2, rx=8),
        text(W / 2, 30, "Алгоритм цифрової компенсації: правильний шлях проти наївної помилки",
             size=15, bold=True)
    ]

    # Ліва колонка: ФАТАЛЬНА ПОМИЛКА (наївне додавання температур)
    f.append(rect(30, 55, 360, 255, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    f.append(text(210, 80, "ХИБНИЙ ШЛЯХ (Наївне додавання)", size=13, color=POS, bold=True))
    f.append(text(210, 96, "T_hot ≠ T_meas + T_cjc через нелінійність S(T)", size=10, color=POS, italic=True))

    # Блоки хибного шляху
    tb1, _, _ = textbox(210, 130, "1. Виміряли V_meas (напр. 19.644 мВ)",
                        size=10.5, pad=6, fill="#ffffff", stroke=LINE, sw=1.2)
    f.append(tb1)
    f.append(arrow(210, 148, 210, 170, color=POS, sw=1.5))

    tb2, _, _ = textbox(210, 185, "2. Перетворили V_meas у T_meas = f⁻¹(V_meas)\n(отримали хибні 478.2 °C замість 500 °C)",
                        size=10, pad=6, fill="#ffffff", stroke=POS, sw=1.2, color=POS)
    f.append(tb2)
    f.append(arrow(210, 210, 210, 230, color=POS, sw=1.5))

    tb3, _, _ = textbox(210, 255, "3. Додали: T = T_meas + T_cjc (478.2 + 25 = 503.2 °C)\nПОХИБКА: +3.2 °C (а для типу S/B — до 15...30 °C!)",
                        size=10, pad=6, fill="#ffffff", stroke=POS, sw=1.5, color=POS, bold=True)
    f.append(tb3)

    # Права колонка: ПРАВИЛЬНИЙ ШЛЯХ (додавання ЕРС за NIST ITS-90)
    f.append(rect(430, 55, 360, 255, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(610, 80, "ПРАВИЛЬНИЙ ШЛЯХ (Додавання ЕРС)", size=13, color=FIELD, bold=True))
    f.append(text(610, 96, "Строго за стандартом NIST ITS-90", size=10, color=FIELD, italic=True))

    # Блоки правильного шляху
    tb4, _, _ = textbox(610, 125, "1. Читаємо V_meas (19.644 мВ) та T_cjc (25.0 °C)",
                        size=10.5, pad=6, fill="#ffffff", stroke=LINE, sw=1.2)
    f.append(tb4)
    f.append(arrow(610, 143, 610, 163, color=FIELD, sw=1.5))

    tb5, _, _ = textbox(610, 180, "2. Рахуємо ЕРС холодного спаю:\nV_cjc = f_NIST(T_cjc) = 1.000 мВ",
                        size=10, pad=6, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD)
    f.append(tb5)
    f.append(arrow(610, 205, 610, 225, color=FIELD, sw=1.5))

    tb6, _, _ = textbox(610, 255, "3. V_total = V_meas + V_cjc = 20.644 мВ\n4. T_hot = f_NIST⁻¹(V_total) = ТОЧНО 500.0 °C",
                        size=10.5, pad=6, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    f.append(tb6)

    # Підсумок знизу
    f.append(text(W / 2, 335,
                  "Золоте правило термометрії: додавати можна лише потенціали (ЕРС), а не температури!",
                  size=12, color=INK, bold=True))

    render(os.path.join(IMG, "cjc-math-flow.svg"), W, H, *f)


# ── 4. Графік нелінійності чутливості Зеєбека S(T) для популярних типів ───────
def fig_seebeck_coefficient_curves():
    W, H = 820, 360
    f = [
        rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1.2, rx=8),
        text(W / 2, 30, "Нелінійність коефіцієнта Зеєбека S(T) = dV/dT різних типів термопар",
             size=15, bold=True)
    ]

    # Вісь координат
    ox, oy = 90, 280
    gw, gh = 670, 210

    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1))

    # Горизонтальні лінії сітки (мкВ/°C: 0, 10, 20, 30, 40, 50, 60, 70, 80)
    for u in range(0, 90, 10):
        y = oy - (u / 80.0) * gh
        f.append(line(ox, y, ox + gw, y, color="#e1e4e8", sw=1))
        f.append(text(ox - 8, y + 4, "%d" % u, size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 35, oy - gh / 2, "S(T), мкВ/°C", size=11, color=INK, bold=True, anchor="middle"))

    # Вертикальні лінії сітки (T, °C: -200, 0, 200, 400, 600, 800, 1000, 1200)
    temps = [-200, 0, 200, 400, 600, 800, 1000, 1200]
    for t in temps:
        x = ox + ((t + 200) / 1400.0) * gw
        f.append(line(x, oy - gh, x, oy, color="#e1e4e8", sw=1))
        f.append(text(x, oy + 16, "%d °C" % t, size=9.5, color=MUTED))
    f.append(text(ox + gw / 2, oy + 36, "Температура гарячого спаю (T), °C", size=11, color=INK, bold=True))

    def map_pt(t, s):
        x = ox + ((t + 200) / 1400.0) * gw
        y = oy - (s / 80.0) * gh
        return "%.1f,%.1f" % (x, y)

    # Крива типу E (Хромель-Константан) — дуже чутлива (від 30 до 80 мкВ/°C)
    pts_e = [(-200, 25), (-100, 45), (0, 58.7), (200, 74.5), (400, 81), (600, 80), (800, 76), (900, 74)]
    f.append('<polyline points="%s" fill="none" stroke="#8e44ad" stroke-width="2.5"/>' %
             " ".join(map_pt(t, s) for t, s in pts_e))
    f.append(text(ox + ((700 + 200) / 1400.0) * gw, oy - (78 / 80.0) * gh - 8,
                  "Тип E (NiCr-CuNi)", size=10, color="#8e44ad", bold=True))

    # Крива типу K (Хромель-Алюмель) — ~39..42 мкВ/°C
    pts_k = [(-200, 15), (-100, 30), (0, 39.5), (200, 40), (400, 42), (600, 42.5), (800, 41), (1000, 39), (1200, 36)]
    f.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="2.5"/>' %
             " ".join(map_pt(t, s) for t, s in pts_k))
    f.append(text(ox + ((500 + 200) / 1400.0) * gw, oy - (43 / 80.0) * gh - 8,
                  "Тип K (NiCr-NiAl)", size=10, color="#27ae60", bold=True))

    # Крива типу J (Залізо-Константан) — ~50..56 мкВ/°C
    pts_j = [(-200, 22), (-100, 42), (0, 50.4), (200, 54), (400, 55), (600, 57), (760, 62)]
    f.append('<polyline points="%s" fill="none" stroke="#2980b9" stroke-width="2.2"/>' %
             " ".join(map_pt(t, s) for t, s in pts_j))
    f.append(text(ox + ((300 + 200) / 1400.0) * gw, oy - (57 / 80.0) * gh - 8,
                  "Тип J (Fe-CuNi)", size=10, color="#2980b9", bold=True))

    # Крива типу S/R (Платина-Родій) — ~6..12 мкВ/°C
    pts_s = [(0, 5.4), (200, 8.2), (400, 9.5), (600, 10.3), (800, 11.0), (1000, 11.5), (1200, 12.0)]
    f.append('<polyline points="%s" fill="none" stroke="#e67e22" stroke-width="2.2"/>' %
             " ".join(map_pt(t, s) for t, s in pts_s))
    f.append(text(ox + ((900 + 200) / 1400.0) * gw, oy - (12.5 / 80.0) * gh - 8,
                  "Тип S/R (PtRh-Pt)", size=10, color="#e67e22", bold=True))

    # Крива типу B (Pt30Rh-Pt6Rh) — біля 0 °C S ≈ 0!
    pts_b = [(0, 0.2), (100, 1.2), (300, 4.2), (600, 7.5), (900, 9.5), (1200, 11.2)]
    f.append('<polyline points="%s" fill="none" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="4,3"/>' %
             " ".join(map_pt(t, s) for t, s in pts_b))
    f.append(text(ox + ((250 + 200) / 1400.0) * gw, oy - (3.5 / 80.0) * gh + 14,
                  "Тип B (S ≈ 0 біля кімнатної T)", size=9.5, color="#c0392b", bold=True))

    render(os.path.join(IMG, "seebeck-coefficient-curves.svg"), W, H, *f)


# ── 5. Структурна схема прецизійного аналогового фронтенду (MAX31856 / IC) ────
def fig_thermocouple_afe_architecture():
    W, H = 820, 390
    f = [
        rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1.2, rx=8),
        text(W / 2, 30, "Архітектура прецизійного термопарного фронтенду (MAX31856 / LTC2983)",
             size=15, bold=True)
    ]

    # Зовнішнє підключення (зліва)
    f.append(rect(25, 60, 140, 300, fill="#f8f9fa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(95, 82, "Зовнішній клемник", size=11, color=INK, bold=True))

    f.append(circle(95, 120, 8, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(95, 124, "T+", size=9, color="#ffffff", bold=True))
    f.append(text(50, 124, "TC+", size=10, color=CHROMEL, bold=True, anchor="end"))

    f.append(circle(95, 200, 8, fill=NEG, stroke=LINE, sw=1.5))
    f.append(text(95, 204, "T−", size=9, color="#ffffff", bold=True))
    f.append(text(50, 204, "TC−", size=10, color=ALUMEL, bold=True, anchor="end"))

    f.append(circle(95, 280, 8, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(text(95, 284, "GND", size=9.5, color="#ffffff", bold=True))
    f.append(text(50, 284, "Shield", size=10, color=MUTED, italic=True, anchor="end"))

    # Фільтрація RC та захист ESD (між клемником та IC)
    f.append(rect(180, 60, 110, 300, fill="#fffaf0", stroke="#e67e22", sw=1.2, rx=6))
    f.append(text(235, 82, "EMI/ESD фільтр", size=11, color="#e67e22", bold=True))

    # Резистори фільтра
    f.append(rect(205, 110, 30, 20, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(220, 124, "R₁", size=10, color=INK))
    f.append(rect(205, 190, 30, 20, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(220, 204, "R₂", size=10, color=INK))

    # Конденсатори
    f.append(line(260, 120, 260, 200, color="#2980b9", sw=1.5))
    f.append(text(275, 160, "C_diff", size=9.5, color="#2980b9", bold=True))
    f.append(text(275, 173, "100 нФ", size=9, color=MUTED))

    f.append(line(245, 120, 245, 270, color=MUTED, sw=1, dash="2,2"))
    f.append(line(245, 200, 245, 270, color=MUTED, sw=1, dash="2,2"))
    f.append(text(235, 285, "C_cm (10 нФ)", size=9, color=MUTED))

    # Лінії зв'язку від клем до фільтра
    f.append(line(103, 120, 205, 120, color=CHROMEL, sw=2))
    f.append(line(103, 200, 205, 200, color=ALUMEL, sw=2))

    # Велика мікросхема IC (MAX31856)
    f.append(rect(310, 60, 480, 300, fill="#f4f7fb", stroke=NEG, sw=1.8, rx=6))
    f.append(text(550, 85, "Інтегральний контролер термопари (напр. MAX31856)",
                  size=12, color=NEG, bold=True))

    # Вхідний комутатор та захист від обриву
    f.append(rect(325, 110, 85, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(367, 135, "Вхідний MUX", size=10, color=INK, bold=True))
    f.append(text(367, 152, "& Струмові", size=9.5, color=MUTED))
    f.append(text(367, 166, "джерела", size=9.5, color=MUTED))
    f.append(text(367, 180, "детекції обриву", size=9, color=POS))

    f.append(line(235, 120, 325, 120, color=LINE, sw=1.5))
    f.append(line(235, 200, 325, 200, color=LINE, sw=1.5))

    # PGA (Підсилювач з програмованим підсиленням)
    f.append(rect(425, 120, 60, 90, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(455, 155, "PGA", size=11, color=INK, bold=True))
    f.append(text(455, 172, "Gain: 1..32", size=9.5, color=MUTED))
    f.append(line(410, 165, 425, 165, color=LINE, sw=1.5))

    # Прецизійний Delta-Sigma АЦП (19...24 біти)
    f.append(rect(500, 115, 80, 100, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(540, 145, "19-біт / 24-біт", size=9.5, color=FIELD, bold=True))
    f.append(text(540, 160, "ΔΣ АЦП", size=12, color=FIELD, bold=True))
    f.append(text(540, 178, "Фільтр 50/60Hz", size=9, color=MUTED))
    f.append(line(485, 165, 500, 165, color=LINE, sw=1.5))

    # Локальний сенсор температури кристала (CJC Sensor)
    f.append(rect(340, 245, 140, 85, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(410, 268, "Вбудований CJC", size=10.5, color=NEG, bold=True))
    f.append(text(410, 285, "Датчик T_кристала", size=9.5, color=INK))
    f.append(text(410, 302, "(точність ±0.7 °C)", size=9, color=MUTED))

    # DSP процесор лінеаризації (LUT / ITS-90 engine)
    f.append(rect(600, 115, 95, 215, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(647, 145, "DSP ЯДРО", size=11, color=INK, bold=True))
    f.append(text(647, 165, "Таблиці NIST", size=9.5, color=FIELD, bold=True))
    f.append(text(647, 180, "Типи: K, J, N,", size=9.5, color=MUTED))
    f.append(text(647, 195, "R, S, T, E, B", size=9.5, color=MUTED))
    f.append(text(647, 225, "Компенсація", size=9.5, color=NEG, bold=True))
    f.append(text(647, 240, "V_tot = V_tc + V_cjc", size=9, color=NEG))
    f.append(text(647, 260, "Діагностика:", size=9.5, color=POS, bold=True))
    f.append(text(647, 276, "Open/Short Fault", size=9, color=POS))

    f.append(line(580, 165, 600, 165, color=LINE, sw=1.5))
    f.append(line(480, 287, 600, 287, color=NEG, sw=1.5))

    # Інтерфейс SPI / I2C на виході
    f.append(rect(715, 160, 65, 120, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(747, 195, "SPI / I2C", size=10.5, color=FIELD, bold=True))
    f.append(text(747, 215, "Регістри", size=9.5, color=MUTED))
    f.append(text(747, 235, "T_hot (°C)", size=9, color=POS, bold=True))
    f.append(text(747, 250, "T_cjc (°C)", size=9, color=NEG, bold=True))
    f.append(line(695, 220, 715, 220, color=LINE, sw=1.5))

    # Вихідна стрілка до MCU
    f.append(arrow(780, 220, 805, 220, color=FIELD, sw=2))

    render(os.path.join(IMG, "thermocouple-afe-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cjc_circuit_problem()
    fig_isothermal_block_pcb()
    fig_cjc_math_flow()
    fig_seebeck_coefficient_curves()
    fig_thermocouple_afe_architecture()
    print("All 5 figures generated successfully.")
