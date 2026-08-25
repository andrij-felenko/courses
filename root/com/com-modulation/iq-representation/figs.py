# -*- coding: utf-8 -*-
"""Фігури до теми «Квадратурна форма (IQ)» (iq-representation).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

AMB = "#b08900"


# ── 1. Векторне подання на комплексній IQ-площині ──────────────────────────
def make_iq_decomposition():
    w, h = 680, 420
    out = []

    # Осі координат
    ox, oy = 220, 310
    length = 260
    height_axis = 250

    # Сітка та осі
    out.append(line(ox - 40, oy, ox + length + 40, oy, color=MUTED, sw=1.2))
    out.append(line(ox, oy + 40, ox, oy - height_axis - 20, color=MUTED, sw=1.2))

    out.append(text(ox + length + 50, oy + 5, "I (Синфазна вісь)", size=13, color=INK, anchor="start", bold=True))
    out.append(text(ox, oy - height_axis - 30, "Q (Квадратурна вісь)", size=13, color=INK, anchor="middle", bold=True))

    # Точка сигналу A, phi
    vx, vy = ox + 200, oy - 180

    # Проекції I та Q
    out.append(line(vx, oy, vx, vy, color=MUTED, sw=1.5, dash="4,4"))
    out.append(line(ox, vy, vx, vy, color=MUTED, sw=1.5, dash="4,4"))

    # Стрілки точок I та Q вздовж осей
    out.append(line(ox, oy, vx, oy, color=NEG, sw=3.0))
    out.append(line(ox, oy, ox, vy, color=POS, sw=3.0))

    # Проекція на осі - позначки
    out.append(circle(vx, oy, 4, fill=NEG, stroke=NEG))
    out.append(circle(ox, vy, 4, fill=POS, stroke=POS))

    out.append(text(vx / 2 + ox / 2, oy + 25, "I = A · cos(φ)", size=14, color=NEG, anchor="middle", bold=True))
    out.append(text(ox - 65, vy / 2 + oy / 2, "Q = A · sin(φ)", size=14, color=POS, anchor="end", bold=True))

    # Дуга кута phi
    r_arc = 50
    arc_pts = []
    angle_rad = math.atan2(oy - vy, vx - ox)
    for i in range(21):
        a = angle_rad * (i / 20.0)
        ax = ox + r_arc * math.cos(a)
        ay = oy - r_arc * math.sin(a)
        arc_pts.append("%.1f,%.1f" % (ax, ay))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(arc_pts), AMB))
    out.append(text(ox + r_arc + 15, oy - 15, "φ (фаза)", size=13, color=AMB, anchor="start", bold=True))

    # Головний вектор сигналу (амплітуда A)
    out.append(line(ox, oy, vx, vy, color=FIELD, sw=3.5))
    out.append(circle(vx, vy, 6, fill=FIELD, stroke=INK, sw=1.5))

    # Підпис вектора
    out.append(text(vx / 2 + ox / 2 - 15, vy / 2 + oy / 2 - 10, "A (амплітуда)", size=14, color=FIELD, anchor="end", bold=True))

    # Виносна картка з тотожністю
    box_s, _, _ = textbox(530, 140, "Комплексне огинаюче:\nz(t) = I(t) + j·Q(t)\n\ns(t) = Re{ z(t) · e^(jω_c t) }\n     = I(t)·cos(ω_c t) - Q(t)·sin(ω_c t)", size=13, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(box_s)

    render(os.path.join(IMG, "iq-decomposition.svg"), w, h, *out, title="Розкладання сигналу на квадратурні складові I та Q")


# ── 2. Структурна схема IQ модулятора та демодулятора ───────────────────────
def make_quadrature_architecture():
    w, h = 760, 480
    out = []

    # Заголовок блоків
    out.append(text(200, 50, "Квадратурний модулятор (Передавач)", size=15, color=INK, anchor="middle", bold=True))
    out.append(text(580, 50, "Квадратурний демодулятор (Приймач)", size=15, color=INK, anchor="middle", bold=True))

    # Передавач (Ліва частина)
    # ЦАП I та ЦАП Q
    b_dac_i, _, _ = textbox(70, 90, "ЦАП I", size=13, pad=8, fill=FILL, stroke=NEG)
    b_dac_q, _, _ = textbox(70, 210, "ЦАП Q", size=13, pad=8, fill=FILL, stroke=POS)
    out.append(b_dac_i)
    out.append(b_dac_q)

    # Змішувачі TX
    out.append(circle(180, 90, 16, fill=BG, stroke=LINE, sw=2.0))
    out.append(text(180, 95, "×", size=20, color=INK, anchor="middle", bold=True))
    out.append(circle(180, 210, 16, fill=BG, stroke=LINE, sw=2.0))
    out.append(text(180, 215, "×", size=20, color=INK, anchor="middle", bold=True))

    out.append(line(110, 90, 164, 90, color=NEG, sw=2.0))
    out.append(text(137, 80, "I(t)", size=12, color=NEG, anchor="middle", bold=True))

    out.append(line(110, 210, 164, 210, color=POS, sw=2.0))
    out.append(text(137, 200, "Q(t)", size=12, color=POS, anchor="middle", bold=True))

    # Гетеродин TX та фазообертач 90°
    b_lo_tx, _, _ = textbox(180, 150, "LO (f_c)", size=12, pad=6, fill=BG, stroke=AMB)
    out.append(b_lo_tx)
    out.append(line(180, 130, 180, 106, color=AMB, sw=1.8))
    out.append(text(195, 120, "cos(ω_c t)", size=11, color=AMB, anchor="start"))

    out.append(line(180, 170, 180, 194, color=AMB, sw=1.8))
    out.append(text(195, 185, "-sin(ω_c t)", size=11, color=AMB, anchor="start"))

    # Суматор TX
    out.append(circle(270, 150, 18, fill=BG, stroke=FIELD, sw=2.0))
    out.append(text(270, 155, "+", size=22, color=FIELD, anchor="middle", bold=True))

    out.append(line(196, 90, 270, 90, color=LINE, sw=1.8))
    out.append(line(270, 90, 270, 132, color=LINE, sw=1.8))

    out.append(line(196, 210, 270, 210, color=LINE, sw=1.8))
    out.append(line(270, 210, 270, 168, color=LINE, sw=1.8))

    # Вихід радіосигналу s(t)
    out.append(line(288, 150, 360, 150, color=FIELD, sw=2.5))
    out.append(text(324, 140, "s(t) [RF]", size=13, color=FIELD, anchor="middle", bold=True))

    # Межа між TX і RX (Антена / Радіоканал) — коротка лінія
    out.append(line(375, 65, 375, 245, color=MUTED, sw=1.5, dash="6,6"))
    out.append(text(375, 260, "Ефір / Радіоканал", size=12, color=MUTED, anchor="middle", italic=True))

    # Приймач (Права частина)
    out.append(line(390, 150, 450, 150, color=FIELD, sw=2.5))

    # Розгалуження на змішувачі RX
    out.append(circle(450, 150, 4, fill=FIELD, stroke=FIELD))
    out.append(line(450, 150, 450, 90, color=FIELD, sw=1.8))
    out.append(line(450, 150, 450, 210, color=FIELD, sw=1.8))

    out.append(line(450, 90, 484, 90, color=FIELD, sw=1.8))
    out.append(line(450, 210, 484, 210, color=FIELD, sw=1.8))

    # Змішувачі RX
    out.append(circle(500, 90, 16, fill=BG, stroke=LINE, sw=2.0))
    out.append(text(500, 95, "×", size=20, color=INK, anchor="middle", bold=True))
    out.append(circle(500, 210, 16, fill=BG, stroke=LINE, sw=2.0))
    out.append(text(500, 215, "×", size=20, color=INK, anchor="middle", bold=True))

    # Гетеродин RX
    b_lo_rx, _, _ = textbox(500, 150, "LO (f_c)", size=12, pad=6, fill=BG, stroke=AMB)
    out.append(b_lo_rx)
    out.append(line(500, 130, 500, 106, color=AMB, sw=1.8))
    out.append(line(500, 170, 500, 194, color=AMB, sw=1.8))

    # ФНЧ (Low Pass Filters)
    b_lpf_i, _, _ = textbox(590, 90, "ФНЧ I", size=13, pad=8, fill=FILL, stroke=NEG)
    b_lpf_q, _, _ = textbox(590, 210, "ФНЧ Q", size=13, pad=8, fill=FILL, stroke=POS)
    out.append(b_lpf_i)
    out.append(b_lpf_q)

    out.append(line(516, 90, 552, 90, color=LINE, sw=1.8))
    out.append(line(516, 210, 552, 210, color=LINE, sw=1.8))

    # АЦП RX
    b_adc_i, _, _ = textbox(690, 90, "АЦП I", size=13, pad=8, fill=FILL, stroke=NEG)
    b_adc_q, _, _ = textbox(690, 210, "АЦП Q", size=13, pad=8, fill=FILL, stroke=POS)
    out.append(b_adc_i)
    out.append(b_adc_q)

    out.append(line(628, 90, 652, 90, color=NEG, sw=2.0))
    out.append(text(640, 80, "I'(t)", size=12, color=NEG, anchor="middle", bold=True))

    out.append(line(628, 210, 652, 210, color=POS, sw=2.0))
    out.append(text(640, 200, "Q'(t)", size=12, color=POS, anchor="middle", bold=True))

    # Пояснення внизу
    b_expl, _, _ = textbox(380, 370, "Принцип роботи:\n1. Модулятор формує радіосигнал s(t) з двох незалежних сигналів I(t) та Q(t).\n2. Демодулятор перемножує s(t) на ортогональні несучі та відфільтровує частоту 2f_c за допомогою ФНЧ.\n3. Вихід ФНЧ — точно відновлені складові I'(t) = I(t)/2 та Q'(t) = Q(t)/2.", size=12, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(b_expl)

    render(os.path.join(IMG, "quadrature-architecture.svg"), w, h, *out, title="Апаратурна техніка квадратурного модулятора та демодулятора")


# ── 3. Комплексний спектр базової смуги та його зсув на несучу ───────────────
def make_iq_spectrum_shift():
    w, h = 720, 380
    out = []

    # Графік 1: Базова смуга (Комплексний спектр z(t))
    ox1, oy1 = 200, 160
    out.append(text(ox1, 50, "1. Спектр базової смуги Z(f) = I(f) + j·Q(f)", size=13, color=INK, anchor="middle", bold=True))
    out.append(line(ox1 - 150, oy1, ox1 + 150, oy1, color=MUTED, sw=1.5))
    out.append(line(ox1, oy1 + 30, ox1, oy1 - 100, color=MUTED, sw=1.5))
    out.append(text(ox1 + 160, oy1 + 4, "f (базова)", size=12, color=INK, anchor="start"))

    # Несиметрична форма спектра базової смуги
    spec1_pts = [
        "%.1f,%.1f" % (ox1 - 110, oy1),
        "%.1f,%.1f" % (ox1 - 70, oy1 - 40),
        "%.1f,%.1f" % (ox1 - 20, oy1 - 25),
        "%.1f,%.1f" % (ox1, oy1 - 70),
        "%.1f,%.1f" % (ox1 + 50, oy1 - 90),
        "%.1f,%.1f" % (ox1 + 100, oy1)
    ]
    out.append('<polygon points="%s" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2.0"/>' %
               (" ".join(spec1_pts), FIELD, FIELD))

    out.append(text(ox1 - 65, oy1 + 20, "-B (від'ємні f)", size=11, color=POS, anchor="middle"))
    out.append(text(ox1 + 65, oy1 + 20, "+B (додатні f)", size=11, color=NEG, anchor="middle"))
    out.append(text(ox1, oy1 + 20, "0", size=11, color=INK, anchor="middle"))

    # Стрілка переносу
    out.append(line(370, 120, 420, 120, color=AMB, sw=2.5))
    out.append(line(410, 114, 420, 120, color=AMB, sw=2.5))
    out.append(line(410, 126, 420, 120, color=AMB, sw=2.5))
    out.append(text(395, 105, "Перенесення на f_c", size=11, color=AMB, anchor="middle", bold=True))

    # Графік 2: Радіочастотний спектр S(f)
    ox2, oy2 = 560, 160
    out.append(text(ox2, 50, "2. Спектр RF сигналу s(t) навколо f_c", size=13, color=INK, anchor="middle", bold=True))
    out.append(line(ox2 - 130, oy2, ox2 + 130, oy2, color=MUTED, sw=1.5))
    out.append(line(ox2, oy2 + 30, ox2, oy2 - 100, color=MUTED, sw=1.5))
    out.append(text(ox2 + 140, oy2 + 4, "f (радіо)", size=12, color=INK, anchor="start"))

    # Перенесена несиметрична форма
    spec2_pts = [
        "%.1f,%.1f" % (ox2 - 90, oy2),
        "%.1f,%.1f" % (ox2 - 55, oy2 - 40),
        "%.1f,%.1f" % (ox2 - 15, oy2 - 25),
        "%.1f,%.1f" % (ox2, oy2 - 70),
        "%.1f,%.1f" % (ox2 + 40, oy2 - 90),
        "%.1f,%.1f" % (ox2 + 80, oy2)
    ]
    out.append('<polygon points="%s" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2.0"/>' %
               (" ".join(spec2_pts), FIELD, FIELD))

    out.append(text(ox2, oy2 + 20, "f_c", size=12, color=AMB, anchor="middle", bold=True))
    out.append(text(ox2 - 55, oy2 + 20, "f_c - B (LSB)", size=11, color=POS, anchor="middle"))
    out.append(text(ox2 + 55, oy2 + 20, "f_c + B (USB)", size=11, color=NEG, anchor="middle"))

    # Пояснення переносу частот
    b_note, _, _ = textbox(360, 290, "Головний висновок комплексного спектра:\n• Від'ємні частоти комплексного сигналу (f < 0) відповідають нижній бічній смузі (LSB, f_c - |f|).\n• Додатні частоти (f > 0) відповідають верхній бічній смузі (USB, f_c + f).\n• Це дає змогу легко формувати будь-яку асиметрію спектра та односмугову модуляцію (SSB).", size=12, pad=12, fill=FILL, stroke=LINE, sw=1.5)
    out.append(b_note)

    render(os.path.join(IMG, "iq-spectrum-shift.svg"), w, h, *out, title="Зв'язок комплексного спектра базової смуги та радіоспектра навколо f_c")


# ── 4. Апаратурні спотворення (IQ Imbalance & DC offset) ───────────────────
def make_iq_imbalance():
    w, h = 740, 360
    out = []

    # 1. Ідеальна сітка (QPSK)
    cx1, cy1 = 130, 160
    out.append(text(cx1, 50, "Ідеальне сузір'я", size=13, color=INK, anchor="middle", bold=True))
    out.append(line(cx1 - 80, cy1, cx1 + 80, cy1, color=MUTED, sw=1.2))
    out.append(line(cx1, cy1 - 80, cx1, cy1 + 80, color=MUTED, sw=1.2))

    pts1 = [(cx1 - 45, cy1 - 45), (cx1 + 45, cy1 - 45), (cx1 - 45, cy1 + 45), (cx1 + 45, cy1 + 45)]
    for px, py in pts1:
        out.append(circle(px, py, 6, fill=FIELD, stroke=INK, sw=1.5))

    out.append(text(cx1, cy1 + 110, "Квадрат 1:1\nЦентр у точці (0,0)", size=11, color=MUTED, anchor="middle"))

    # 2. Витік несучої (DC Offset)
    cx2, cy2 = 320, 160
    out.append(text(cx2, 50, "Зсув постійної складової (DC)", size=13, color=INK, anchor="middle", bold=True))
    out.append(line(cx2 - 80, cy2, cx2 + 80, cy2, color=MUTED, sw=1.2))
    out.append(line(cx2, cy2 - 80, cx2, cy2 + 80, color=MUTED, sw=1.2))

    # Зміщений центр
    off_x, off_y = 25, -20
    pts2 = [(cx2 - 45 + off_x, cy2 - 45 + off_y), (cx2 + 45 + off_x, cy2 - 45 + off_y),
            (cx2 - 45 + off_x, cy2 + 45 + off_y), (cx2 + 45 + off_x, cy2 + 45 + off_y)]
    for px, py in pts2:
        out.append(circle(px, py, 6, fill=POS, stroke=INK, sw=1.5))

    out.append(line(cx2, cy2, cx2 + off_x, cy2 + off_y, color=POS, sw=1.5, dash="3,3"))
    out.append(text(cx2, cy2 + 110, "Усе сузір'я зсунуте\nВитік несучої на f_c", size=11, color=POS, anchor="middle"))

    # 3. Амплітудна та фазова несиметрія (Gain & Phase Imbalance)
    cx3, cy3 = 580, 160
    out.append(text(cx3, 50, "Амплітудний та фазовий дисбаланс", size=13, color=INK, anchor="middle", bold=True))
    out.append(line(cx3 - 100, cy3, cx3 + 100, cy3, color=MUTED, sw=1.2))
    out.append(line(cx3, cy3 - 90, cx3, cy3 + 90, color=MUTED, sw=1.2))

    # Перекривлені точки (паралелограм замість квадрата)
    pts3 = [(cx3 - 60, cy3 - 35), (cx3 + 40, cy3 - 50),
            (cx3 - 40, cy3 + 50), (cx3 + 60, cy3 + 35)]

    # З'єднувальний паралелограм
    poly_pts = ["%.1f,%.1f" % p for p in [pts3[0], pts3[1], pts3[3], pts3[2]]]
    out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' %
               (" ".join(poly_pts), AMB))

    for px, py in pts3:
        out.append(circle(px, py, 6, fill=AMB, stroke=INK, sw=1.5))

    out.append(text(cx3, cy3 + 110, "Перекос у паралелограм\nПоява дзеркальної завади", size=11, color=AMB, anchor="middle"))

    render(os.path.join(IMG, "iq-imbalance.svg"), w, h, *out, title="Вплив апаратурних недосконалостей на сузір'я сигналу")


if __name__ == "__main__":
    make_iq_decomposition()
    make_quadrature_architecture()
    make_iq_spectrum_shift()
    make_iq_imbalance()
    print("Фігури IQ успішно згенеровано.")
