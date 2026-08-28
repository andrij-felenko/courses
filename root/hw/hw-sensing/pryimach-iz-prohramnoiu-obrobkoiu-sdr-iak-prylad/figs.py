# -*- coding: utf-8 -*-
"""Фігури до статті «Приймач із програмною обробкою (SDR) як прилад».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.

Фігури:
  1) sdr-instrument-arch.svg       — архітектура вимірювального SDR від ВЧ-входу до DSP
  2) iq-constellation-demod.svg    — площина I/Q, демодуляція амплітуди, фази, частоти та неідеальності
  3) windowing-fft-leakage.svg     — порівняння прямокутного та вікон Hann/Blackman-Harris при FFT
  4) dynamic-range-danl-sfdr.svg   — динамічний діапазон, рівень шумів DANL, 1 dB компресія та SFDR
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#caa24a"
ACCENT_BLUE = "#1d4ed8"
ACCENT_GREEN = "#15803d"
ACCENT_RED = "#b91c1c"
ACCENT_PURPLE = "#7e22ce"

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (s, fill, stroke, sw))

def dashed_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4 4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))


# ── 1. Архітектура вимірювального SDR ──────────────────────────────────────
def fig_sdr_arch():
    W, H = 1000, 480
    f = [
        text(W / 2, 28, "Тракт вимірювального SDR-приймача прямого перетворення (Zero-IF)", size=18, bold=True),
        text(W / 2, 50, "відкалібрований аналоговий ВЧ-фронтенд, квадратурний поділ, подвійний АЦП і цифрова фільтрація DDC",
             size=11, color=MUTED, italic=True)
    ]

    # Секції (фонові зони)
    f.append(rect(30, 75, 230, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(145, 96, "Аналоговий ВЧ-фронтенд (RF)", size=12, color=INK, bold=True))

    f.append(rect(280, 75, 330, 335, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=8))
    f.append(text(445, 96, "Квадратурний змішувач (IQ Downconversion)", size=12, color=ACCENT_GREEN, bold=True))

    f.append(rect(630, 75, 340, 335, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=8))
    f.append(text(800, 96, "Цифрова обробка (FPGA / DSP / Host)", size=12, color=ACCENT_BLUE, bold=True))

    # RF Вхід
    f.append(arrow(10, 150, 45, 150, color=INK, sw=2))
    f.append(text(25, 140, "RF In", size=10, bold=True))

    # Кроки RF
    f.append(fitbox(45, 125, 80, 50, "Кроковий\nатенюатор\n0..31 dB", size=10, fill="#ffffff"))
    f.append(arrow(125, 150, 155, 150, color=INK, sw=1.8))
    f.append(fitbox(155, 125, 90, 50, "Фільтр пре-\nселекції BPF\n/ LNA підсил.", size=10, fill="#ffffff", stroke=ACCENT_RED))

    # Розгалуження на I та Q
    f.append(arrow(245, 150, 300, 150, color=INK, sw=1.8))
    f.append(circle(300, 150, 3.5, fill=INK, stroke=INK, sw=0))

    # Канал I (вгорі)
    f.append(line(300, 150, 300, 180, color=INK, sw=1.8))
    f.append(arrow(300, 180, 320, 180, color=INK, sw=1.8))
    f.append(fitbox(320, 158, 65, 44, "Змішувач I\n(Mixer I)", size=10, fill="#ffffff", stroke=ACCENT_GREEN))
    f.append(arrow(385, 180, 410, 180, color=INK, sw=1.8))
    f.append(fitbox(410, 158, 75, 44, "ФНЧ (LPF)\nAnti-Alias", size=10, fill="#ffffff"))
    f.append(arrow(485, 180, 505, 180, color=INK, sw=1.8))
    f.append(fitbox(505, 158, 85, 44, "АЦП I (ADC)\n14-16 біт", size=10, fill="#ffffff", stroke=ACCENT_BLUE))

    # Канал Q (внизу)
    f.append(line(300, 150, 300, 330, color=INK, sw=1.8))
    f.append(arrow(300, 330, 320, 330, color=INK, sw=1.8))
    f.append(fitbox(320, 308, 65, 44, "Змішувач Q\n(Mixer Q)", size=10, fill="#ffffff", stroke=ACCENT_GREEN))
    f.append(arrow(385, 330, 410, 330, color=INK, sw=1.8))
    f.append(fitbox(410, 308, 75, 44, "ФНЧ (LPF)\nAnti-Alias", size=10, fill="#ffffff"))
    f.append(arrow(485, 330, 505, 330, color=INK, sw=1.8))
    f.append(fitbox(505, 308, 85, 44, "АЦП Q (ADC)\n14-16 біт", size=10, fill="#ffffff", stroke=ACCENT_BLUE))

    # Синтезатор гетеродина (LO) та зсув 90 градусів
    f.append(fitbox(315, 235, 80, 40, "Синтезатор\nLO (PLL)", size=10, fill="#fef3c7", stroke=GOLD))
    f.append(arrow(355, 235, 355, 202, color=GOLD, sw=1.8))
    f.append(text(372, 222, "0° LO", size=9, color=GOLD, bold=True))

    f.append(arrow(395, 255, 425, 255, color=GOLD, sw=1.8))
    f.append(fitbox(425, 235, 60, 40, "Фазо-\nзсув 90°", size=10, fill="#fef3c7", stroke=GOLD))
    f.append(arrow(455, 275, 355, 308, color=GOLD, sw=1.8))
    f.append(text(410, 300, "90° LO", size=9, color=GOLD, bold=True))

    # Цифрова секція: DDC і FFT
    f.append(arrow(590, 180, 650, 200, color=ACCENT_BLUE, sw=2))
    f.append(arrow(590, 330, 650, 310, color=ACCENT_BLUE, sw=2))
    f.append(text(615, 175, "I(n)", size=10, color=ACCENT_BLUE, bold=True))
    f.append(text(615, 335, "Q(n)", size=10, color=ACCENT_BLUE, bold=True))

    f.append(fitbox(650, 170, 140, 170, "FPGA / DDC\n\n• Децимація (CIC/FIR)\n• Корекція IQ дисбалансу\n• Цифровий гетеродин NCO\n• Формування IQ-потоку", size=10, fill="#ffffff", stroke=ACCENT_BLUE))

    f.append(arrow(790, 255, 825, 255, color=INK, sw=2))
    f.append(text(808, 245, "USB/PCIe", size=9, color=MUTED))

    f.append(fitbox(825, 170, 130, 170, "Host DSP / ПО\n\n• Віконні функції w[n]\n• Швидке FFT 2^N\n• Усереднення спектрів\n• Розрахунок dBm / DANL", size=10, fill="#ffffff", stroke=ACCENT_PURPLE))

    # Висновок внизу
    f.append(fitbox(40, 425, 920, 34,
                    "Квадратурне перетворення переносить смугу частот на нульову проміжну частоту без дзеркального каналу,\nзберігаючи повну амплітудну та фазову інформацію у двох потоках відліків I(n) та Q(n).",
                    size=10, bold=True, fill="#f8fafc", stroke="#64748b", sw=1.2))

    return render(os.path.join(IMG, "sdr-instrument-arch.svg"), W, H, *f)


# ── 2. IQ площина і відновлення параметрів ─────────────────────────────────
def fig_iq_demod():
    W, H = 940, 440
    f = [
        text(W / 2, 28, "Комплексна площина IQ: відновлення амплітуди, фази та неідеальності", size=18, bold=True),
        text(W / 2, 50, "миттєвий вектор s(t) = I(t) + j·Q(t), виявлення зміщення DC та амплітудно-фазової асиметрії",
             size=11, color=MUTED, italic=True)
    ]

    # Ліва панель: Ідеальний вектор IQ та тригонометрія
    cx1, cy1 = 230, 240
    R = 120

    f.append(rect(30, 75, 410, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(235, 98, "Ідеальний квадратурний вектор", size=12, color=INK, bold=True))

    # Сітка та осі
    f.append(line(cx1 - R - 20, cy1, cx1 + R + 20, cy1, color=MUTED, sw=1.2))
    f.append(line(cx1, cy1 + R + 20, cx1, cy1 - R - 20, color=MUTED, sw=1.2))
    f.append(arrow(cx1 + R + 10, cy1, cx1 + R + 30, cy1, color=INK, sw=1.5))
    f.append(arrow(cx1, cy1 - R - 10, cx1, cy1 - R - 30, color=INK, sw=1.5))
    f.append(text(cx1 + R + 35, cy1 + 4, "I", size=11, bold=True))
    f.append(text(cx1 - 10, cy1 - R - 25, "Q", size=11, bold=True))

    # Траєкторія - коло
    f.append(dashed_circle(cx1, cy1, R, fill="none", stroke="#93c5fd", sw=1.5, dash="4 4"))

    # Вектор під кутом 40 градусів
    phi_rad = math.radians(40)
    vx = cx1 + R * math.cos(phi_rad)
    vy = cy1 - R * math.sin(phi_rad)

    # Проекції на осі I та Q
    f.append(line(vx, vy, vx, cy1, color=ACCENT_GREEN, sw=1.5, dash="3 3"))
    f.append(line(vx, vy, cx1, vy, color=ACCENT_BLUE, sw=1.5, dash="3 3"))

    f.append(line(cx1, cy1, vx, cy1, color=ACCENT_GREEN, sw=3))
    f.append(text((cx1 + vx) / 2, cy1 + 18, "I(t)", size=11, color=ACCENT_GREEN, bold=True))

    f.append(line(cx1, cy1, cx1, vy, color=ACCENT_BLUE, sw=3))
    f.append(text(cx1 - 20, (cy1 + vy) / 2, "Q(t)", size=11, color=ACCENT_BLUE, bold=True))

    # Сам вектор
    f.append(arrow(cx1, cy1, vx, vy, color=ACCENT_RED, sw=2.5))
    f.append(circle(vx, vy, 4, fill=ACCENT_RED, stroke=ACCENT_RED, sw=0))
    f.append(text(vx + 15, vy - 10, "s(t)", size=12, color=ACCENT_RED, bold=True))

    # Дуга фази
    arc_pts = []
    for deg in range(0, 41, 5):
        rad = math.radians(deg)
        arc_pts.append((cx1 + 40 * math.cos(rad), cy1 - 40 * math.sin(rad)))
    f.append(polyline(arc_pts, color=GOLD, sw=2))
    f.append(text(cx1 + 52, cy1 - 16, "φ(t)", size=11, color=GOLD, bold=True))

    # Формули в рамці ліворуч
    f.append(fitbox(50, 345, 370, 52,
                    "A(t) = √(I² + Q²)   [миттєва амплітуда]\nφ(t) = atan2(Q, I)   [миттєва фаза]\nf(t) = (1 / 2π) · (dφ / dt)   [миттєва частота]",
                    size=10, bold=True, fill="#f8fafc", stroke="#94a3b8"))

    # Права панель: Апаратні спотворення (DC Offset та IQ Imbalance)
    f.append(rect(470, 75, 440, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(690, 98, "Апаратні неідеальності аналогового IQ-тракту", size=12, color=INK, bold=True))

    cx2, cy2 = 690, 240
    # Осі
    f.append(line(cx2 - R - 20, cy2, cx2 + R + 20, cy2, color=MUTED, sw=1.2))
    f.append(line(cx2, cy2 + R + 20, cx2, cy2 - R - 20, color=MUTED, sw=1.2))
    f.append(arrow(cx2 + R + 10, cy2, cx2 + R + 30, cy2, color=INK, sw=1.5))
    f.append(arrow(cx2, cy2 - R - 10, cx2, cy2 - R - 30, color=INK, sw=1.5))
    f.append(text(cx2 + R + 35, cy2 + 4, "I", size=11, bold=True))
    f.append(text(cx2 - 10, cy2 - R - 25, "Q", size=11, bold=True))

    # Ідеальне коло (сіре)
    f.append(dashed_circle(cx2, cy2, R, fill="none", stroke="#e2e8f0", sw=1.5, dash="4 4"))

    # Зміщений центр DC Offset
    dc_x, dc_y = 22, -18
    f.append(circle(cx2 + dc_x, cy2 + dc_y, 3, fill=ACCENT_RED, stroke=ACCENT_RED, sw=0))
    f.append(arrow(cx2, cy2, cx2 + dc_x, cy2 + dc_y, color=ACCENT_RED, sw=1.5))
    f.append(text(cx2 + dc_x + 10, cy2 + dc_y + 14, "DC Зсув (LO Leakage)", size=9, color=ACCENT_RED, bold=True))

    # Деформований еліпс через нерівність коефіцієнтів підсилення і фазову похибку
    ellipse_pts = []
    gain_imb = 1.15  # підсилення Q більше
    phase_imb = math.radians(12)  # не 90 градусів
    for deg in range(0, 361, 6):
        rad = math.radians(deg)
        i_val = R * math.cos(rad)
        q_val = gain_imb * R * math.sin(rad + phase_imb)
        ellipse_pts.append((cx2 + dc_x + i_val, cy2 + dc_y - q_val))
    f.append(polyline(ellipse_pts, color=ACCENT_PURPLE, sw=2.2))

    f.append(fitbox(490, 345, 400, 52,
                    "• Зсув нуля (DC Offset) → центральний пік на 0 Гц (f_LO)\n• IQ Дисбаланс амплітуд/фаз → хибний дзеркальний пік (-f_sig)\n• Програмна корекція вирівнює матрицю перетворення до ідеалу",
                    size=9, bold=True, fill="#fff1f2", stroke="#fda4af"))

    return render(os.path.join(IMG, "iq-constellation-demod.svg"), W, H, *f)


# ── 3. Віконні функції та спектральне просочування ─────────────────────────
def fig_windowing():
    W, H = 960, 430
    f = [
        text(W / 2, 28, "Віконне зважування при FFT: усунення спектрального просочування", size=18, bold=True),
        text(W / 2, 50, "прямокутне вікно дає високі бічні пелюстки (-13 dB); вікна Hann і Blackman-Harris розширюють RBW, але пригнічують завади",
             size=11, color=MUTED, italic=True)
    ]

    # Ліва панель: Часова область (вікно множиться на сигнал)
    f.append(rect(30, 75, 420, 325, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(240, 98, "Часова область: сигнал та вагові вікна", size=12, color=INK, bold=True))

    ox1, oy1 = 60, 240
    w_len = 360
    f.append(line(ox1, oy1, ox1 + w_len, oy1, color=MUTED, sw=1.2))
    f.append(line(ox1, oy1 - 100, ox1, oy1 + 100, color=MUTED, sw=1.2))
    f.append(arrow(ox1 + w_len, oy1, ox1 + w_len + 15, oy1, color=INK, sw=1.5))
    f.append(text(ox1 + w_len + 18, oy1 + 4, "t", size=11, bold=True))

    # Незперервний синус
    sin_pts = []
    for i in range(w_len + 1):
        t = i / w_len
        val = 60 * math.sin(2 * math.pi * 5.3 * t)
        sin_pts.append((ox1 + i, oy1 - val))
    f.append(polyline(sin_pts, color="#94a3b8", sw=1.2, dash="3 2"))
    f.append(text(130, 160, "Сигнал x(t)", size=9, color="#64748b"))

    # Вікно Blackman-Harris
    bh_pts = []
    for i in range(w_len + 1):
        t = i / w_len
        # a0 = 0.35875, a1 = 0.48829, a2 = 0.14128, a3 = 0.01168
        w_val = (0.35875 - 0.48829 * math.cos(2 * math.pi * t) +
                 0.14128 * math.cos(4 * math.pi * t) - 0.01168 * math.cos(6 * math.pi * t))
        bh_pts.append((ox1 + i, oy1 - 85 * w_val))
    f.append(polyline(bh_pts, color=ACCENT_RED, sw=2.2))
    f.append(text(240, 140, "Blackman-Harris w(t)", size=10, color=ACCENT_RED, bold=True))

    # Зважений сигнал
    win_sin_pts = []
    for i in range(w_len + 1):
        t = i / w_len
        w_val = (0.35875 - 0.48829 * math.cos(2 * math.pi * t) +
                 0.14128 * math.cos(4 * math.pi * t) - 0.01168 * math.cos(6 * math.pi * t))
        val = 60 * math.sin(2 * math.pi * 5.3 * t) * w_val
        win_sin_pts.append((ox1 + i, oy1 - val))
    f.append(polyline(win_sin_pts, color=ACCENT_BLUE, sw=1.8))
    f.append(text(330, 220, "x(t) · w(t)", size=10, color=ACCENT_BLUE, bold=True))

    f.append(fitbox(50, 345, 380, 42,
                    "Кінці блоку плавно сходять до нуля → розрив на межах блоку усувається.",
                    size=9.5, bold=True, fill="#eff6ff", stroke="#bfdbfe"))

    # Права панель: Частотна область (Спектр FFT)
    f.append(rect(480, 75, 450, 325, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(705, 98, "Частотна область: спектральний відгук (dB)", size=12, color=INK, bold=True))

    ox2, oy2 = 520, 320
    f.append(arrow(ox2, oy2, ox2 + 380, oy2, color=INK, sw=1.5))
    f.append(arrow(ox2, oy2, ox2, 110, color=INK, sw=1.5))
    f.append(text(ox2 + 390, oy2 + 4, "f", size=11, bold=True))
    f.append(text(ox2 - 15, 115, "dB", size=10, bold=True))

    # Спектр прямокутного вікна (Rectangular): вузький головний пік, але бічні пелюстки -13 dB
    rect_spec = []
    for x in range(360):
        fx = (x - 180) / 10.0
        if abs(fx) < 0.001:
            mag = 1.0
        else:
            mag = abs(math.sin(math.pi * fx) / (math.pi * fx))
        db = 20 * math.log10(max(mag, 1e-4))
        y_val = oy2 - (db + 80) * (180.0 / 80.0)
        y_val = max(130, min(oy2, y_val))
        rect_spec.append((ox2 + x, y_val))
    f.append(polyline(rect_spec, color="#94a3b8", sw=1.6, dash="3 3"))

    # Спектр Blackman-Harris: ширша основа, бічні пелюстки -92 dB
    bh_spec = []
    for x in range(360):
        fx = (x - 180) / 10.0
        # наближена форма відгуку вікна Blackman-Harris
        mag = 1.0 / (1.0 + (fx / 2.0)**8)
        db = 20 * math.log10(max(mag, 1e-5))
        y_val = oy2 - (db + 95) * (180.0 / 95.0)
        y_val = max(130, min(oy2, y_val))
        bh_spec.append((ox2 + x, y_val))
    f.append(polyline(bh_spec, color=ACCENT_RED, sw=2.2))

    # Легенда у вільному верхньому правому кутку
    f.append(line(750, 130, 775, 130, color="#94a3b8", sw=1.6, dash="3 3"))
    f.append(text(782, 134, "Прямокутне (-13 dB)", size=9, color="#64748b", bold=True, anchor="start"))

    f.append(line(750, 150, 775, 150, color=ACCENT_RED, sw=2.2))
    f.append(text(782, 154, "Blackman-Harris (-92 dB)", size=9, color=ACCENT_RED, bold=True, anchor="start"))

    f.append(fitbox(500, 345, 410, 42,
                    "Blackman-Harris має ENBW = 2.00 бінів (проти 1.0 у Rect), проте дозволяє бачити слабкі сигнали поруч із потужними завадами без маскування.",
                    size=9, bold=True, fill="#fef2f2", stroke="#fecaca"))

    return render(os.path.join(IMG, "windowing-fft-leakage.svg"), W, H, *f)


# ── 4. Динамічний діапазон, DANL та SFDR ────────────────────────────────────
def fig_dynamic_range():
    W, H = 960, 450
    f = [
        text(W / 2, 28, "Динамічний діапазон вимірювального SDR: шуми, нелінійність та компресія", size=18, bold=True),
        text(W / 2, 50, "рівні потужності, відображений середній шум (DANL), точка 1 dB компресії (P1dB) та SFDR",
             size=11, color=MUTED, italic=True)
    ]

    ox, oy = 100, 370
    w_field = 780
    h_field = 270

    # Осі
    f.append(arrow(ox, oy, ox + w_field + 30, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - h_field - 20, color=INK, sw=2))
    f.append(text(ox + w_field + 45, oy + 4, "f (Частота)", size=11, bold=True))
    f.append(text(ox - 35, oy - h_field - 10, "Потужність (dBm)", size=11, bold=True))

    # Горизонтальні опорні рівні
    y_fullscale = oy - 250    # 0 dBFS (+10 dBm)
    y_p1db = oy - 220         # P1dB (+0 dBm)
    y_carrier = oy - 190      # Несуча (-10 dBm)
    y_spur = oy - 90          # Інтермодуляція / шпора (-65 dBm)
    y_danl_wide = oy - 40     # DANL при RBW=100 kHz (-90 dBm)
    y_danl_narrow = oy - 15   # DANL при RBW=1 kHz (-110 dBm)

    f.append(line(ox, y_fullscale, ox + w_field, y_fullscale, color=ACCENT_RED, sw=1.4, dash="4 4"))
    f.append(text(ox - 8, y_fullscale + 4, "0 dBFS (Кліпінг АЦП)", size=9.5, color=ACCENT_RED, bold=True, anchor="end"))

    f.append(line(ox, y_p1db, ox + w_field, y_p1db, color=GOLD, sw=1.2, dash="3 3"))
    f.append(text(ox - 8, y_p1db + 4, "P1dB (Компресія)", size=9.5, color=GOLD, bold=True, anchor="end"))

    # Шумові рівні (DANL)
    f.append(rect(ox, y_danl_wide, w_field, oy - y_danl_wide, fill="#f8fafc", stroke="none", sw=0))
    f.append(line(ox, y_danl_wide, ox + w_field, y_danl_wide, color="#64748b", sw=1.4, dash="2 2"))
    f.append(text(ox + w_field - 10, y_danl_wide - 6, "DANL (RBW = 100 kHz)", size=9.5, color="#64748b", bold=True, anchor="end"))

    f.append(line(ox, y_danl_narrow, ox + w_field, y_danl_narrow, color=ACCENT_GREEN, sw=1.6))
    f.append(text(ox + w_field - 10, y_danl_narrow - 6, "DANL (RBW = 1 kHz) → шум падає на 20 dB", size=9.5, color=ACCENT_GREEN, bold=True, anchor="end"))

    # Спектральні піки
    # Основний сигнал f0
    fx0 = ox + 280
    f.append(line(fx0, oy, fx0, y_carrier, color=ACCENT_BLUE, sw=3.5))
    f.append(circle(fx0, y_carrier, 4, fill=ACCENT_BLUE, stroke=ACCENT_BLUE, sw=0))
    f.append(text(fx0, y_carrier - 10, "Основний сигнал f₀", size=10, color=ACCENT_BLUE, bold=True))

    # Дзеркальний пік (Image response)
    fx_img = ox + 460
    f.append(line(fx_img, oy, fx_img, y_spur - 15, color=ACCENT_PURPLE, sw=2))
    f.append(text(fx_img, y_spur - 22, "Дзеркало (-f₀)", size=9, color=ACCENT_PURPLE, bold=True))

    # Інтермодуляційний пік 3-го порядку (IMD3)
    fx_imd = ox + 580
    f.append(line(fx_imd, oy, fx_imd, y_spur, color=ACCENT_RED, sw=2))
    f.append(text(fx_imd, y_spur - 8, "IMD3 / Спур", size=9, color=ACCENT_RED, bold=True))

    # Двосторонні стрілки діапазонів
    # SFDR
    sfdr_x = ox + 360
    f.append(line(sfdr_x, y_carrier, sfdr_x, y_spur, color=ACCENT_PURPLE, sw=2))
    f.append(arrow(sfdr_x, (y_carrier + y_spur) / 2, sfdr_x, y_carrier, color=ACCENT_PURPLE, sw=1.8))
    f.append(arrow(sfdr_x, (y_carrier + y_spur) / 2, sfdr_x, y_spur, color=ACCENT_PURPLE, sw=1.8))
    f.append(text(sfdr_x + 10, (y_carrier + y_spur) / 2 + 4, "SFDR (Динамічний діапазон без завад)", size=10, color=ACCENT_PURPLE, bold=True, anchor="start"))

    # Динамічний діапазон до шуму (DR)
    dr_x = ox + 180
    f.append(line(dr_x, y_carrier, dr_x, y_danl_narrow, color=ACCENT_GREEN, sw=1.8))
    f.append(arrow(dr_x, (y_carrier + y_danl_narrow) / 2, dr_x, y_carrier, color=ACCENT_GREEN, sw=1.6))
    f.append(arrow(dr_x, (y_carrier + y_danl_narrow) / 2, dr_x, y_danl_narrow, color=ACCENT_GREEN, sw=1.6))
    f.append(text(dr_x - 10, (y_carrier + y_danl_narrow) / 2 + 4, "SNR / Динамічний діапазон", size=9.5, color=ACCENT_GREEN, bold=True, anchor="end"))

    # Висновок
    f.append(fitbox(ox, 395, w_field, 38,
                    "Зменшення смуги RBW у 10 разів знижує рівень шуму DANL на 10 dB: DANL = -174 dBm/Hz + NF + 10·log₁₀(RBW).\nМаксимальний корисний сигнал обмежений точкою 1 dB компресії LNA та межею 0 dBFS АЦП.",
                    size=9.5, bold=True, fill="#f8fafc", stroke="#64748b"))

    return render(os.path.join(IMG, "dynamic-range-danl-sfdr.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sdr_arch()
    fig_iq_demod()
    fig_windowing()
    fig_dynamic_range()
    print("OK: All SDR figures generated successfully in", IMG)
