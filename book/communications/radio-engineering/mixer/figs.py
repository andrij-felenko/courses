# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори
RF_COLOR = "#8e44ad"   # ВЧ-сигнал (фіолетовий)
LO_COLOR = FIELD       # Гетеродин (зелений)
IF_COLOR = POS         # Проміжна частота (червоний)
SPUR_COL = MUTED       # Побічні комбінаційні частоти (сірий)


def poly(pts_list, fill="none", stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_list)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)


def tri(cx, base_y, half_w, h, color, sw=2.0, fill=None):

    """Трикутний пік спектра з центром cx, основою на base_y."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - half_w, base_y, cx, base_y - h, cx + half_w, base_y)
    f = fill if fill else "none"
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (pts, f, color, sw))


def tick(x, base_y, lbl, color=MUTED, up=False):
    dy = -8 if up else 18
    return (line(x, base_y - 4, x, base_y + 4, color=MUTED, sw=1.2) +
            text(x, base_y + dy, lbl, size=12, color=color))


# ── Фігура 1: Принцип змішування (перемноження сигналів та спектр) ───────────

def fig_mixing_principle():
    W, H = 740, 360
    p = []
    
    # Схема перемноження (ліва частина)
    bx, by = 60, 60
    p.append(rect(bx, by, 220, 260, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(bx + 110, by + 24, "Часова область", size=13, color=INK, bold=True))
    
    # Джерела сигналів
    p.append(textbox(bx + 40, by + 75, "f_RF", size=13, color=RF_COLOR, bold=True, min_w=55)[0])
    p.append(textbox(bx + 40, by + 195, "f_LO", size=13, color=LO_COLOR, bold=True, min_w=55)[0])
    
    # Змішувач (перемножувач ×)
    mx, my = bx + 150, by + 135
    p.append(circle(mx, my, 22, fill="#ffffff", stroke=INK, sw=2.0))
    p.append(text(mx, my + 6, "×", size=20, color=INK, bold=True))
    
    # Лінії входу і виходу
    p.append(line(bx + 70, by + 75, mx - 22, my - 10, color=RF_COLOR, sw=1.8))
    p.append(arrow(mx - 32, my - 14, mx - 22, my - 10, color=RF_COLOR, sw=1.8))
    
    p.append(line(bx + 70, by + 195, mx - 22, my + 10, color=LO_COLOR, sw=1.8))
    p.append(arrow(mx - 32, my + 14, mx - 22, my + 10, color=LO_COLOR, sw=1.8))
    
    p.append(line(mx + 22, my, bx + 210, my, color=IF_COLOR, sw=2.0))
    p.append(arrow(bx + 195, my, bx + 210, my, color=IF_COLOR, sw=2.0))
    p.append(text(bx + 180, my - 12, "f_IF", size=12, color=IF_COLOR, bold=True))
    
    # Спектральна область (права частина)
    ax, ay = 320, 260
    axw = 380
    p.append(text(ax + 190, by + 24, "Частотна область (Спектр)", size=13, color=INK, bold=True))
    
    # Вісь частоти
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 18, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 10, ay + 4, "f", size=14, color=INK, italic=True, anchor="start"))
    
    # Спектральні піки
    f_if = ax + 70
    f_lo = ax + 200
    f_rf = ax + 260
    f_sum = ax + 340
    
    # Вхідний ВЧ сигнал
    p.append(tri(f_rf, ay, 18, 55, RF_COLOR, fill="#f3e8fb"))
    p.append(tick(f_rf, ay, "f_RF", color=RF_COLOR))
    p.append(text(f_rf, ay - 68, "ВЧ вхід", size=11, color=RF_COLOR, bold=True))
    
    # Гетеродин
    p.append(line(f_lo, ay, f_lo, ay - 75, color=LO_COLOR, sw=2.5))
    p.append(arrow(f_lo, ay - 65, f_lo, ay - 77, color=LO_COLOR, sw=2.5))
    p.append(tick(f_lo, ay, "f_LO", color=LO_COLOR))
    p.append(text(f_lo, ay - 85, "Гетеродин", size=11, color=LO_COLOR, bold=True))
    
    # Різницева частота (ПЧ / IF)
    p.append(tri(f_if, ay, 18, 55, IF_COLOR, fill="#fdecea"))
    p.append(tick(f_if, ay, "f_LO − f_RF", color=IF_COLOR))
    p.append(text(f_if, ay - 68, "Різниця (ПЧ)", size=11, color=IF_COLOR, bold=True))
    
    # Сумарна частота (f_RF + f_LO)
    p.append(tri(f_sum, ay, 18, 40, SPUR_COL, fill="#eef0f2"))
    p.append(tick(f_sum, ay, "f_RF + f_LO", color=SPUR_COL))
    p.append(text(f_sum, ay - 52, "Сума (відфільтровується)", size=10, color=SPUR_COL))
    
    # Формула внизу
    b, bw, bh = textbox(ax + 190, ay + 65, "cos(ω_RF·t) · cos(ω_LO·t) = ½ cos((ω_RF − ω_LO)t) + ½ cos((ω_RF + ω_LO)t)",
                        size=12, color=INK, fill="#f8fafc", stroke=MUTED, min_w=370)
    p.append(b)

    render(os.path.join(OUT, "mixing-principle.svg"), W, H, *p,
           title="Принцип змішування частот: перемноження та спектральне перенесення")


# ── Фігура 2: Трипортова модель змішувача та розв'язка ────────────────────────

def fig_mixer_ports():
    W, H = 740, 340
    p = []
    
    cx, cy = 370, 150
    mw, mh = 160, 110
    
    # Центральний блок змішувача
    p.append(rect(cx - mw/2, cy - mh/2, mw, mh, fill="#ffffff", stroke=INK, sw=2.2, rx=8))
    p.append(circle(cx, cy - 10, 24, fill="#f8fafc", stroke=INK, sw=1.8))
    p.append(text(cx, cy - 4, "×", size=20, color=INK, bold=True))
    p.append(text(cx, cy + 32, "ЗМІШУВАЧ", size=13, color=INK, bold=True))
    
    # Порт RF (ліворуч)
    px_rf = cx - mw/2
    p.append(line(100, cy - 10, px_rf, cy - 10, color=RF_COLOR, sw=2.2))
    p.append(arrow(px_rf - 15, cy - 10, px_rf, cy - 10, color=RF_COLOR, sw=2.2))
    p.append(textbox(120, cy - 40, "Порт RF (ВЧ вхід)\nЧастота: f_RF\nПотужність: P_RF", size=11, color=RF_COLOR, bold=True, min_w=150)[0])
    
    # Порт LO (знизу)
    py_lo = cy + mh/2
    p.append(line(cx, 280, cx, py_lo, color=LO_COLOR, sw=2.2))
    p.append(arrow(cx, py_lo + 15, cx, py_lo, color=LO_COLOR, sw=2.2))
    p.append(textbox(cx, 305, "Порт LO (Гетеродин)\nЧастота: f_LO | Потужність: P_LO", size=11, color=LO_COLOR, bold=True, min_w=240)[0])
    
    # Порт IF (праворуч)
    px_if = cx + mw/2
    p.append(line(px_if, cy - 10, 640, cy - 10, color=IF_COLOR, sw=2.2))
    p.append(arrow(625, cy - 10, 640, cy - 10, color=IF_COLOR, sw=2.2))
    p.append(textbox(620, cy - 40, "Порт IF (ПЧ вихід)\nЧастота: f_IF = |f_RF ± f_LO|\nПотужність: P_IF", size=11, color=IF_COLOR, bold=True, min_w=170)[0])
    
    # Параметри та розв'язка (витоки)
    # LO -> RF розв'язка (пунктир)
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#arrow)"/>'
             % (cx - 20, cy + 30, cx - 70, cy + 30, cx - 70, cy + 5, SPUR_COL))
    p.append(text(cx - 105, cy + 35, "Витік LO→RF", size=10, color=SPUR_COL, bold=True))
    
    # LO -> IF розв'язка (пунктир)
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#arrow)"/>'
             % (cx + 20, cy + 30, cx + 70, cy + 30, cx + 70, cy + 5, SPUR_COL))
    p.append(text(cx + 105, cy + 35, "Витік LO→IF", size=10, color=SPUR_COL, bold=True))
    
    # Коефіцієнт перетворення вгорі
    p.append(textbox(cx, 35, "Коефіцієнт перетворення: G_c = P_IF / P_RF (дБ)\nПасивні: втрати (-6...-9 дБ)  |  Активні: підсилення (+5...+15 дБ)",
                     size=11.5, color=INK, fill="#f4f6f8", stroke=MUTED, min_w=460)[0])

    render(os.path.join(OUT, "mixer-ports.svg"), W, H, *p,
           title="Трипортова модель змішувача: сигнали, втрати та витоки між портами")


# ── Фігура 3: Подвійно-балансний діодний змішувач ────────────────────────────

def fig_diode_ring_mixer():
    W, H = 740, 360
    p = []
    
    # Описи та заголовки по боках
    p.append(text(100, 30, "Вхід RF (ВЧ)", size=13, color=RF_COLOR, bold=True))
    p.append(text(640, 30, "Вхід LO (Гетеродин)", size=13, color=LO_COLOR, bold=True))
    p.append(text(370, 340, "Вихід IF (ПЧ) з середніх точок трансформаторів", size=12, color=IF_COLOR, bold=True))
    
    # Трансформатор T1 (ліворуч, RF)
    tx1 = 180
    p.append(line(60, 110, tx1 - 30, 110, color=RF_COLOR, sw=2.0))
    p.append(line(60, 210, tx1 - 30, 210, color=RF_COLOR, sw=2.0))
    p.append(textbox(80, 160, "RF IN", size=12, color=RF_COLOR, bold=True, min_w=60)[0])
    
    # Первинна обмотка T1
    p.append(line(tx1 - 30, 110, tx1 - 30, 210, color=RF_COLOR, sw=2.0))
    # Ферритове осердя T1
    p.append(line(tx1 - 10, 100, tx1 - 10, 220, color=MUTED, sw=2.0, dash="4 2"))
    p.append(line(tx1 - 5, 100, tx1 - 5, 220, color=MUTED, sw=2.0, dash="4 2"))
    # Вторинна обмотка T1 (з середньою точкою)
    p.append(line(tx1 + 15, 100, tx1 + 15, 220, color=INK, sw=2.0))
    # Середня точка T1
    p.append(circle(tx1 + 15, 160, 3, fill=INK, stroke=INK))
    p.append(line(tx1 + 15, 160, 370, 160, color=IF_COLOR, sw=1.8, dash="5 3"))
    
    # Трансформатор T2 (праворуч, LO)
    tx2 = 560
    p.append(line(680, 110, tx2 + 30, 110, color=LO_COLOR, sw=2.0))
    p.append(line(680, 210, tx2 + 30, 210, color=LO_COLOR, sw=2.0))
    p.append(textbox(660, 160, "LO IN", size=12, color=LO_COLOR, bold=True, min_w=60)[0])
    
    # Первинна обмотка T2
    p.append(line(tx2 + 30, 110, tx2 + 30, 210, color=LO_COLOR, sw=2.0))
    # Осердя T2
    p.append(line(tx2 + 10, 100, tx2 + 10, 220, color=MUTED, sw=2.0, dash="4 2"))
    p.append(line(tx2 + 5, 100, tx2 + 5, 220, color=MUTED, sw=2.0, dash="4 2"))
    # Вторинна обмотка T2
    p.append(line(tx2 - 15, 100, tx2 - 15, 220, color=INK, sw=2.0))
    # Середня точка T2
    p.append(circle(tx2 - 15, 160, 3, fill=INK, stroke=INK))
    p.append(line(tx2 - 15, 160, 370, 160, color=IF_COLOR, sw=1.8, dash="5 3"))
    
    # Лінія IF виходу донизу
    p.append(line(370, 160, 370, 315, color=IF_COLOR, sw=2.2))
    p.append(arrow(370, 300, 370, 315, color=IF_COLOR, sw=2.2))
    p.append(circle(370, 160, 4, fill=IF_COLOR, stroke=IF_COLOR))
    
    # Діодне кільце в центрі (квадрат з 4 діодів Шотткі)
    # Вершини кільця: Top(370, 90), Bottom(370, 230), Left(290, 160), Right(450, 160)
    rx_l, rx_r = 290, 450
    ry_t, ry_b = 90, 230
    
    # З'єднання трансформаторів з кільцем
    p.append(line(tx1 + 15, 100, rx_l, ry_t, color=INK, sw=1.8))
    p.append(line(tx1 + 15, 220, rx_l, ry_b, color=INK, sw=1.8))
    
    p.append(line(tx2 - 15, 100, rx_r, ry_t, color=INK, sw=1.8))
    p.append(line(tx2 - 15, 220, rx_r, ry_b, color=INK, sw=1.8))
    
    # Контур кільця та діоди (D1-D4)
    # D1: Top -> Right
    p.append(line(rx_l, ry_t, rx_r, ry_t, color=INK, sw=1.5))
    p.append(line(rx_r, ry_t, rx_r, ry_b, color=INK, sw=1.5))
    p.append(line(rx_r, ry_b, rx_l, ry_b, color=INK, sw=1.5))
    p.append(line(rx_l, ry_b, rx_l, ry_t, color=INK, sw=1.5))
    
    # Позначки діодів на ребрах
    # D1 (верх)
    p.append(poly([(360, 83), (360, 97), (378, 90)], fill="#ffffff", stroke=POS, sw=1.5))
    p.append(line(378, 83, 378, 97, color=POS, sw=2.0))
    p.append(text(370, 72, "D1 (Шотткі)", size=10.5, color=INK, bold=True))
    
    # D2 (праворуч)
    p.append(poly([(443, 150), (457, 150), (450, 168)], fill="#ffffff", stroke=POS, sw=1.5))
    p.append(line(443, 168, 457, 168, color=POS, sw=2.0))
    p.append(text(480, 160, "D2", size=10.5, color=INK, bold=True))
    
    # D3 (низ)
    p.append(poly([(380, 223), (380, 237), (362, 230)], fill="#ffffff", stroke=POS, sw=1.5))
    p.append(line(362, 223, 362, 237, color=POS, sw=2.0))
    p.append(text(370, 250, "D3", size=10.5, color=INK, bold=True))
    
    # D4 (ліворуч)
    p.append(poly([(283, 170), (297, 170), (290, 152)], fill="#ffffff", stroke=POS, sw=1.5))

    p.append(line(283, 152, 297, 152, color=POS, sw=2.0))
    p.append(text(265, 160, "D4", size=10.5, color=INK, bold=True))
    
    # Вузол у центрі (без замикання IF на кільце!)
    p.append(circle(rx_l, ry_t, 3, fill=INK, stroke=INK))
    p.append(circle(rx_l, ry_b, 3, fill=INK, stroke=INK))
    p.append(circle(rx_r, ry_t, 3, fill=INK, stroke=INK))
    p.append(circle(rx_r, ry_b, 3, fill=INK, stroke=INK))

    render(os.path.join(OUT, "diode-ring-mixer.svg"), W, H, *p,
           title="Схема подвійно-балансного діодного змішувача (діодне кільце)")


# ── Фігура 4: Активний змішувач на комірці Гілберта ─────────────────────────

def fig_gilbert_cell():
    W, H = 740, 380
    p = []
    
    # Живлення VCC вгорі
    p.append(line(240, 40, 500, 40, color=POS, sw=2.0))
    p.append(text(370, 25, "+V_CC (Живлення)", size=12, color=POS, bold=True))
    
    # Навантажувальні резистори R_L1, R_L2
    p.append(line(300, 40, 300, 70, color=POS, sw=1.8))
    p.append(rect(290, 70, 20, 40, fill="#ffffff", stroke=INK, sw=1.5))
    p.append(text(270, 90, "R_L", size=11, color=INK, bold=True))
    p.append(line(300, 110, 300, 130, color=INK, sw=1.8))
    
    p.append(line(440, 40, 440, 70, color=POS, sw=1.8))
    p.append(rect(430, 70, 20, 40, fill="#ffffff", stroke=INK, sw=1.5))
    p.append(text(465, 90, "R_L", size=11, color=INK, bold=True))
    p.append(line(440, 110, 440, 130, color=INK, sw=1.8))
    
    # Виходи IF+ та IF-
    p.append(line(300, 120, 230, 120, color=IF_COLOR, sw=2.0))
    p.append(arrow(245, 120, 230, 120, color=IF_COLOR, sw=2.0))
    p.append(text(195, 124, "IF− Вихід", size=12, color=IF_COLOR, bold=True))
    
    p.append(line(440, 120, 510, 120, color=IF_COLOR, sw=2.0))
    p.append(arrow(495, 120, 510, 120, color=IF_COLOR, sw=2.0))
    p.append(text(545, 124, "IF+ Вихід", size=12, color=IF_COLOR, bold=True))
    
    # Перемикальна квадропа (Switching Quad: Q3, Q4, Q5, Q6) на рівні Y=150..200
    # Блок перемикання LO
    p.append(rect(250, 140, 240, 75, fill="#eafaf0", stroke=LO_COLOR, sw=1.8, rx=6))
    p.append(text(370, 160, "Перемикальна квадропа (LO)", size=12, color=LO_COLOR, bold=True))
    p.append(text(370, 180, "Транзистори Q3, Q4, Q5, Q6", size=11, color=INK))
    p.append(text(370, 198, "Керування гетеродином V_LO+ / V_LO−", size=10.5, color=MUTED))
    
    # Входи LO збоку
    p.append(line(120, 177, 250, 177, color=LO_COLOR, sw=2.0))
    p.append(arrow(235, 177, 250, 177, color=LO_COLOR, sw=2.0))
    p.append(text(80, 181, "LO Вхід (±)", size=12, color=LO_COLOR, bold=True))
    
    # Вхідна диференційна пара (V-I transconductance: Q1, Q2) на рівні Y=240..295
    p.append(rect(270, 235, 200, 70, fill="#f3e8fb", stroke=RF_COLOR, sw=1.8, rx=6))
    p.append(text(370, 258, "Вхідний каскад V-I (RF)", size=12, color=RF_COLOR, bold=True))
    p.append(text(370, 278, "Диференційна пара Q1-Q2", size=11, color=INK))
    p.append(text(370, 294, "Перетворює V_RF у струм I_RF", size=10.5, color=MUTED))
    
    # Входи RF збоку
    p.append(line(120, 270, 270, 270, color=RF_COLOR, sw=2.0))
    p.append(arrow(255, 270, 270, 270, color=RF_COLOR, sw=2.0))
    p.append(text(80, 274, "RF Вхід (±)", size=12, color=RF_COLOR, bold=True))
    
    # З'єднання між перемикачами та V-I каскадом
    p.append(line(320, 215, 320, 235, color=INK, sw=1.8))
    p.append(line(420, 215, 420, 235, color=INK, sw=1.8))
    p.append(line(300, 130, 300, 140, color=INK, sw=1.8))
    p.append(line(440, 130, 440, 140, color=INK, sw=1.8))
    
    # Генератор струму внизу (Tail Current Source I_bias)
    p.append(line(370, 305, 370, 330, color=INK, sw=1.8))
    p.append(circle(370, 342, 12, fill="#ffffff", stroke=INK, sw=1.5))
    p.append(text(370, 346, "I", size=13, color=INK, bold=True))
    p.append(line(370, 354, 370, 365, color=INK, sw=1.8))
    p.append(line(340, 365, 400, 365, color=INK, sw=2.0))
    p.append(text(440, 345, "Генератор струму I_bias", size=11, color=MUTED))

    render(os.path.join(OUT, "gilbert-cell.svg"), W, H, *p,
           title="Схема активного змішувача на транзисторній комірці Гілберта")


# ── Фігура 5: Динамічний діапазон: P1dB та IIP3 ──────────────────────────────

def fig_iip3_compression():
    W, H = 740, 360
    p = []
    
    ax, ay = 90, 290
    axw, ayh = 560, 230
    
    # Осі координат
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.8))
    p.append(arrow(ax + axw - 18, ay, ax + axw, ay, color=INK, sw=1.8))
    p.append(text(ax + axw - 40, ay + 22, "Вхідна потужність P_in (дБм)", size=12, color=INK, bold=True))
    
    p.append(line(ax, ay, ax, ay - ayh, color=INK, sw=1.8))
    p.append(arrow(ax, ay - ayh + 18, ax, ay - ayh, color=INK, sw=1.8))
    p.append(text(ax - 50, ay - ayh + 10, "P_out (дБм)", size=12, color=INK, bold=True))
    
    # Лінія основної частоти (Slope 1:1)
    # Точки: start(110, 260), linear_end(380, 115), compressed_end(480, 85)
    p.append(line(110, 260, 380, 115, color=RF_COLOR, sw=2.2))
    # Реальна крива з компресією
    p.append('<path d="M 380 115 Q 430 90 500 85" fill="none" stroke="%s" stroke-width="2.2"/>' % RF_COLOR)
    # Екстраполяція (пунктир)
    p.append(line(380, 115, 520, 40, color=RF_COLOR, sw=1.6, dash="5 3"))
    p.append(text(240, 170, "Основна складова (Slope 1:1)", size=11.5, color=RF_COLOR, bold=True))
    
    # Лінія інтермодуляції 3-го порядку IMD3 (Slope 3:1)
    # Точки: start(250, 270), intersect(520, 40)
    p.append(line(250, 270, 430, 120, color=POS, sw=2.0))
    p.append(line(430, 120, 520, 40, color=POS, sw=1.6, dash="5 3"))
    p.append(text(350, 220, "Продукти IMD3 (Slope 3:1)", size=11.5, color=POS, bold=True))
    
    # Точка IIP3 (перетин екстраполяцій)
    p.append(circle(520, 40, 5, fill=POS, stroke=POS))
    p.append(line(520, 40, 520, ay, color=POS, sw=1.2, dash="3 3"))
    p.append(tick(520, ay, "IIP3", color=POS))
    p.append(text(525, 28, "Точка перехоплення IP3", size=11.5, color=POS, bold=True, anchor="end"))
    
    # Точка компресії P1dB
    p.append(circle(440, 93, 4, fill=FIELD, stroke=FIELD))
    p.append(line(440, 93, 440, ay, color=FIELD, sw=1.2, dash="3 3"))
    p.append(tick(440, ay, "P_1dB", color=FIELD))
    p.append(text(435, 75, "Компресія 1 дБ", size=11, color=FIELD, bold=True, anchor="end"))
    
    # Рівень шумів (Noise Floor)
    p.append(line(ax, 260, ax + axw - 50, 260, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(ax + 15, 252, "Рівень шумів (Noise Floor N_0)", size=10.5, color=MUTED))
    
    # SFDR (Динамічний діапазон, вільний від побічних складових)
    p.append(rect(140, 40, 210, 45, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(245, 58, "SFDR = ⅔ (IIP3 − N_0)", size=12, color=INK, bold=True))
    p.append(text(245, 74, "Вільний від інтермодуляції діапазон", size=10, color=MUTED))

    render(os.path.join(OUT, "iip3-compression.svg"), W, H, *p,
           title="Нелінійність змішувача: точка компресії P1dB та перехоплення IP3")


if __name__ == "__main__":
    fig_mixing_principle()
    fig_mixer_ports()
    fig_diode_ring_mixer()
    fig_gilbert_cell()
    fig_iip3_compression()
    print("OK: 5 mixer figures written to", OUT)
