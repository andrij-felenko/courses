# -*- coding: utf-8 -*-
"""Фігури до теми «PAL і NTSC: колірна квадратура і фазовий маятник».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def svg_path(d, fill="none", stroke=INK, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def polyline(pts, color=INK, sw=2.2):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


def hline(x1, x2, y, color=MUTED, sw=1.0, dash="4,4"):
    return line(x1, y, x2, y, color=color, sw=sw, dash=dash)


def vline(x, y1, y2, color=MUTED, sw=1.0, dash="4,4"):
    return line(x, y1, x, y2, color=color, sw=sw, dash=dash)


# ── фіг. 1: Квадратурне сузір'я PAL та фазовий маятник +V / -V ─────────────
def fig_pal_qam_constellation():
    W, H = 800, 480
    cx, cy = 400, 240
    r_axis = 180

    # Тестовий колірний вектор (Червоний): U ≈ 0.49 * (R-Y), V ≈ 0.88 * (R-Y)
    # Рядок N (+V): кут ~62° (вгору-праворуч), Рядок N+1 (-V): кут ~-62° (вниз-праворуч)
    vx_u = 65
    vy_v = 120

    parts = [
        # Тло та коло насиченості
        circle(cx, cy, 140, fill="#f8f9fa", stroke="#e9ecef", sw=1.5),
        circle(cx, cy, 90, fill="none", stroke="#e9ecef", sw=1.0),

        # Осі U (U = B - Y) та V (V = R - Y)
        line(cx - r_axis, cy, cx + r_axis, cy, color=INK, sw=1.8),
        line(cx, cy - r_axis, cx, cy + r_axis, color=INK, sw=1.8),

        # Підписи осей
        text(cx + r_axis + 15, cy + 5, "+U (B-Y)", size=13, color=INK, bold=True),
        text(cx - r_axis - 60, cy + 5, "-U (Color Burst NTSC)", size=11, color=MUTED),
        text(cx + 8, cy - r_axis - 10, "+V (R-Y) [Рядок N]", size=12, color=POS, bold=True),
        text(cx + 8, cy + r_axis + 18, "-V (R-Y) [Рядок N+1]", size=12, color=NEG, bold=True),

        # Вектори спалаху колірності Bruch Burst (135 deg та 225 deg у PAL)
        line(cx, cy, cx - 70, cy - 70, color="#9c27b0", sw=2.0, dash="4,2"),
        line(cx, cy, cx - 70, cy + 70, color="#9c27b0", sw=2.0, dash="4,2"),
        circle(cx - 70, cy - 70, 4, fill="#9c27b0", stroke="none"),
        circle(cx - 70, cy + 70, 4, fill="#9c27b0", stroke="none"),
        text(cx - 145, cy - 75, "Burst +135° (Рядок N)", size=10, color="#9c27b0"),
        text(cx - 145, cy + 82, "Burst +225° (Рядок N+1)", size=10, color="#9c27b0"),

        # Вектор N (+V)
        line(cx, cy, cx + vx_u, cy - vy_v, color=POS, sw=2.8),
        circle(cx + vx_u, cy - vy_v, 5, fill=POS, stroke="none"),
        text(cx + vx_u + 12, cy - vy_v, "C_N = U·sin + V·cos (Рядок N)", size=11, color=POS, bold=True),

        # Вектор N+1 (-V)
        line(cx, cy, cx + vx_u, cy + vy_v, color=NEG, sw=2.8),
        circle(cx + vx_u, cy + vy_v, 5, fill=NEG, stroke="none"),
        text(cx + vx_u + 12, cy + vy_v + 10, "C_{N+1} = U·sin - V·cos (Рядок N+1)", size=11, color=NEG, bold=True),

        # Проекції на осі U та V
        line(cx + vx_u, cy - vy_v, cx + vx_u, cy, color=MUTED, sw=1.0, dash="3,3"),
        line(cx + vx_u, cy - vy_v, cx, cy - vy_v, color=MUTED, sw=1.0, dash="3,3"),
        line(cx + vx_u, cy + vy_v, cx + vx_u, cy, color=MUTED, sw=1.0, dash="3,3"),
        line(cx + vx_u, cy + vy_v, cx, cy + vy_v, color=MUTED, sw=1.0, dash="3,3"),

        # Кути фази θ та -θ
        svg_path(f"M {cx+35} {cy} A 35 35 0 0 0 {cx+24} {cy-25}", fill="none", stroke=POS, sw=1.5),
        text(cx + 42, cy - 12, "+θ", size=11, color=POS),

        svg_path(f"M {cx+35} {cy} A 35 35 0 0 1 {cx+24} {cy+25}", fill="none", stroke=NEG, sw=1.5),
        text(cx + 42, cy + 18, "-θ", size=11, color=NEG),

        # Заголовок та пояснення на фігурі
        text(W // 2, 455, "Компонента U (синя) зберігає фазу, а компонента V (червона) змінює знак кожен рядок.", size=11, color=MUTED, anchor="middle"),
    ]

    render(os.path.join(IMG, 'pal-qam-constellation.svg'), W, H, *parts, title="Квадратурна фазова площина PAL: дзеркальне перевертання компоненти V")


# ── фіг. 2: Схема декодера PAL з 1H ультразвуковою лінією затримки ─────────
def fig_pal_delay_line_decoder():
    W, H = 840, 420
    parts = [
        # Вхідний сигнал CVBS / Chroma
        rect(40, 180, 110, 50, fill="#e3f2fd", stroke="#1e88e5", sw=1.8, rx=4),
        text(95, 202, "Вхід Chroma C(t)", size=11, color=INK, anchor="middle", bold=True),
        text(95, 218, "Зі смугового фільтра", size=9, color=MUTED, anchor="middle"),

        # Розгалуження на прямий шлях та лінію затримки
        line(150, 205, 190, 205, color=INK, sw=2.0),
        circle(190, 205, 4, fill=INK, stroke="none"),

        # Гілка 1: Лінія затримки 1H (64 мкс)
        line(190, 205, 190, 140, color=INK, sw=2.0),
        line(190, 140, 230, 140, color=INK, sw=2.0),
        rect(230, 115, 140, 50, fill="#fff3e0", stroke="#fb8c00", sw=1.8, rx=4),
        text(300, 137, "Лінія затримки 1H", size=11, color=INK, anchor="middle", bold=True),
        text(300, 153, "64.0 мкс (ультразвук)", size=9, color="#e65100", anchor="middle"),

        # Гілка 2: Прямий канал (без затримки)
        line(190, 205, 190, 270, color=INK, sw=2.0),
        line(190, 270, 370, 270, color=INK, sw=2.0),
        text(280, 285, "Прямий сигнал C_N(t)", size=10, color=MUTED, anchor="middle"),

        # Сигнал із лінії затримки
        line(370, 140, 370, 180, color=INK, sw=2.0),
        line(370, 140, 370, 230, color=INK, sw=2.0),
        text(300, 125, "Затриманий сигнал C_{N-1}(t)", size=10, color=MUTED, anchor="middle"),

        # Матричний суматор (+) для виділення U
        circle(430, 150, 22, fill="#e8f5e9", stroke=POS, sw=2.0),
        text(430, 156, "+", size=20, color=POS, anchor="middle", bold=True),
        line(370, 140, 408, 140, color=INK, sw=2.0),
        line(190, 270, 430, 270, color=INK, sw=2.0),
        line(430, 270, 430, 172, color=INK, sw=2.0),

        # Матричний віднімач (-) для виділення V
        circle(430, 270, 22, fill="#ffebee", stroke=NEG, sw=2.0),
        text(430, 276, "−", size=22, color=NEG, anchor="middle", bold=True),
        line(370, 230, 430, 230, color=INK, sw=2.0),
        line(430, 230, 430, 248, color=INK, sw=2.0),

        # Виходи суматора/віднімача
        line(452, 150, 500, 150, color=POS, sw=2.2),
        text(476, 140, "2U sin(ωt)", size=10, color=POS, anchor="middle", bold=True),

        line(452, 270, 500, 270, color=NEG, sw=2.2),
        text(476, 260, "2V cos(ωt)", size=10, color=NEG, anchor="middle", bold=True),

        # Синхронні демодулятори (QAM)
        rect(500, 125, 130, 50, fill="#f3e5f5", stroke="#ab47bc", sw=1.8, rx=4),
        text(565, 147, "Демодулятор U", size=11, color=INK, anchor="middle", bold=True),
        text(565, 163, "× sin(ω_sc t)", size=10, color="#7b1fa2", anchor="middle"),

        rect(500, 245, 130, 50, fill="#f3e5f5", stroke="#ab47bc", sw=1.8, rx=4),
        text(565, 267, "Демодулятор V", size=11, color=INK, anchor="middle", bold=True),
        text(565, 283, "× ±cos(ω_sc t) [PAL switch]", size=9, color="#7b1fa2", anchor="middle"),

        # Опорний генератор піднесучої та PLL (Bruch Burst detector)
        rect(500, 330, 130, 45, fill="#eceff1", stroke="#607d8b", sw=1.5, rx=4),
        text(565, 350, "ФАПЧ / Кварц 4.43 МГц", size=10, color=INK, anchor="middle", bold=True),
        text(565, 364, "Детектор спалаху PAL", size=9, color=MUTED, anchor="middle"),

        line(565, 330, 565, 295, color="#607d8b", sw=1.5, dash="3,3"),
        line(565, 245, 565, 175, color="#607d8b", sw=1.5, dash="3,3"),

        # Вихідні колірно-різницеві сигнали U та V
        line(630, 150, 700, 150, color=POS, sw=2.5),
        circle(700, 150, 4, fill=POS, stroke="none"),
        text(710, 154, "U (B - Y)", size=12, color=POS, anchor="start", bold=True),

        line(630, 270, 700, 270, color=NEG, sw=2.5),
        circle(700, 270, 4, fill=NEG, stroke="none"),
        text(710, 274, "V (R - Y)", size=12, color=NEG, anchor="start", bold=True),

        # Матриця RGB
        rect(700, 185, 100, 50, fill="#e0f7fa", stroke="#00acc1", sw=1.8, rx=4),
        text(750, 207, "Матриця RGB", size=11, color=INK, anchor="middle", bold=True),
        text(750, 222, "Y, U, V → R,G,B", size=9, color=MUTED, anchor="middle"),

        line(735, 150, 750, 150, color=POS, sw=1.5),
        line(750, 150, 750, 185, color=POS, sw=1.5),
        line(735, 270, 750, 270, color=NEG, sw=1.5),
        line(750, 270, 750, 235, color=NEG, sw=1.5),

        text(W // 2, 405, "Додавання двох сусідніх рядків взаємно знищує дзеркальну компоненту V і виділяє 2U. Віднімання виділяє 2V.", size=11, color=MUTED, anchor="middle"),
    ]

    render(os.path.join(IMG, 'pal-delay-line-decoder.svg'), W, H, *parts, title="Структурна схема декодера PAL з 1H ультразвуковою лінією затримки 64 мкс")


# ── фіг. 3: Геометричне скасування фазової помилки Δφ ─────────────────────
def fig_phase_error_cancellation():
    W, H = 820, 440
    cx, cy = 230, 250
    scale = 0.85

    # Початковий вектор C_0: U = 80, V = 100
    u0, v0 = 80 * scale, 100 * scale

    # Фазова помилка Δφ = 20 градусів (для наочності)
    dphi = math.radians(20)

    # Рядок N (+V з помилкою Δφ): повернутий на +Δφ
    # C_N = (U cos Δφ - V sin Δφ, U sin Δφ + V cos Δφ)
    cn_x = u0 * math.cos(dphi) - v0 * math.sin(dphi)
    cn_y = u0 * math.sin(dphi) + v0 * math.cos(dphi)

    # Рядок N+1 (-V з помилкою Δφ, після інверсії V у декодері): повернутий на -Δφ
    # C_{N+1} = (U cos Δφ + V sin Δφ, -U sin Δφ + V cos Δφ) -> з інверсованим V:
    cn1_x = u0 * math.cos(dphi) + v0 * math.sin(dphi)
    cn1_y = -u0 * math.sin(dphi) + v0 * math.cos(dphi)

    # Середнє векторне значення C_avg = (C_N + C_{N+1}) / 2
    cavg_x = (cn_x + cn1_x) / 2
    cavg_y = (cn_y + cn1_y) / 2

    parts = [
        # Осі координат U та V
        line(cx - 40, cy, cx + 220, cy, color=INK, sw=1.5),
        line(cx, cy + 40, cx, cy - 170, color=INK, sw=1.5),
        text(cx + 230, cy + 4, "+U", size=12, color=INK, bold=True),
        text(cx - 4, cy - 178, "+V", size=12, color=INK, bold=True),

        # Ідеальний вектор C_0 (без помилки)
        line(cx, cy, cx + u0, cy - v0, color=MUTED, sw=1.5, dash="4,4"),
        circle(cx + u0, cy - v0, 4, fill=MUTED, stroke="none"),
        text(cx + u0 + 10, cy - v0 - 5, "Ідеальний вектор C_0 (θ)", size=10, color=MUTED, anchor="start"),

        # Вектор рядка N (повернутий на +Δφ)
        line(cx, cy, cx + cn_x, cy - cn_y, color=POS, sw=2.5),
        circle(cx + cn_x, cy - cn_y, 5, fill=POS, stroke="none"),
        text(cx + cn_x + 8, cy - cn_y - 8, "C_N (зсув +Δφ)", size=11, color=POS, anchor="start", bold=True),

        # Вектор рядка N+1 після інверсії V (повернутий на -Δφ)
        line(cx, cy, cx + cn1_x, cy - cn1_y, color=NEG, sw=2.5),
        circle(cx + cn1_x, cy - cn1_y, 5, fill=NEG, stroke="none"),
        text(cx + cn1_x + 8, cy - cn1_y + 12, "C_{N+1}' (зсув -Δφ)", size=11, color=NEG, anchor="start", bold=True),

        # Паралелограм додавання векторів C_N та C_{N+1}'
        line(cx + cn_x, cy - cn_y, cx + cn_x + cn1_x, cy - (cn_y + cn1_y), color="#9e9e9e", sw=1.2, dash="3,3"),
        line(cx + cn1_x, cy - cn1_y, cx + cn_x + cn1_x, cy - (cn_y + cn1_y), color="#9e9e9e", sw=1.2, dash="3,3"),

        # Сумарний вектор додавання (C_N + C_{N+1}) / 2
        line(cx, cy, cx + cavg_x, cy - cavg_y, color="#2e7d32", sw=3.0),
        circle(cx + cavg_x, cy - cavg_y, 6, fill="#2e7d32", stroke="none"),
        text(cx + cavg_x + 12, cy - cavg_y + 4, "C_avg = C_0 · cos(Δφ)", size=12, color="#2e7d32", anchor="start", bold=True),

        # Пояснювальні блоки праворуч
        rect(530, 80, 265, 300, fill="#f8f9fa", stroke="#dee2e6", sw=1.5, rx=6),
        text(545, 105, "Результат компенсації:", size=13, color=INK, anchor="start", bold=True),

        text(545, 135, "1. Напрямок фази (Hue):", size=11, color=INK, anchor="start", bold=True),
        text(560, 155, "θ_avg = θ (абсолютно точний!)", size=11, color="#2e7d32", anchor="start", bold=True),
        text(560, 172, "Зсув тону відсутній.", size=10, color=MUTED, anchor="start"),

        text(545, 205, "2. Амплітуда (Saturation):", size=11, color=INK, anchor="start", bold=True),
        text(560, 225, "A_avg = A_0 · cos(Δφ)", size=11, color=POS, anchor="start", bold=True),
        text(560, 242, "При Δφ = 10°: cos(10°) = 0.985", size=10, color=MUTED, anchor="start"),
        text(560, 258, "Втрата насиченості всього 1.5%", size=10, color=MUTED, anchor="start"),

        text(545, 290, "3. Порівняння з NTSC:", size=11, color=INK, anchor="start", bold=True),
        text(560, 310, "NTSC: Δφ = 10° зміщує колір шкіри", size=10, color=NEG, anchor="start"),
        text(560, 325, "з рожевого на зеленуватий.", size=10, color=NEG, anchor="start"),
        text(560, 345, "PAL: Δφ перетворюється на", size=10, color="#2e7d32", anchor="start"),
        text(560, 360, "непомітне зниження яскравості.", size=10, color="#2e7d32", anchor="start"),

        text(W // 2, 415, "Фазове відхилення Δφ розкладається на дві симетричні компоненти. Бічна помилка скасовується повністю.", size=11, color=MUTED, anchor="middle"),
    ]

    render(os.path.join(IMG, 'phase-error-cancellation.svg'), W, H, *parts, title="Геометричний механізм скасування фазової помилки Δφ у лінії затримки PAL")


if __name__ == '__main__':
    fig_pal_qam_constellation()
    fig_pal_delay_line_decoder()
    fig_phase_error_cancellation()
    print("Фігури PAL/NTSC успішно згенеровано у ./img/")
