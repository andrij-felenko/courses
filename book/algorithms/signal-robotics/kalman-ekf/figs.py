# -*- coding: utf-8 -*-
"""Фігури до теми «Розширений фільтр Калмана (EKF)».
Вага — на коваріації-матриці, крос-кореляції та лінеаризації EKF
(базовий цикл predict/update розібрано в темі kalman-filter, тут його не повторюємо).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

BLUE  = NEG          # передбачення / модель
RED   = POS          # вимір
GREEN = FIELD        # оцінка / правда


def _ellipse(cx, cy, rx, ry, angle_deg, color, fill_op=0.12, sw=2.4, dash=None):
    """Повернений еліпс довкола (cx,cy) через group-transform."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<g transform="translate(%.1f %.1f) rotate(%.1f)">'
            '<ellipse cx="0" cy="0" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="%.2f" '
            'stroke="%s" stroke-width="%.1f"%s/></g>'
            % (cx, cy, angle_deg, rx, ry, color, fill_op, color, sw, d))


# ── 1. coваріація: оцінка = точка + хмара (розмір і форма) ────────────────────
def fig_covariance_shape():
    """Поряд із точкою-оцінкою фільтр веде КОВАРІАЦІЮ — формальний розмір і
    форму хмари невпевненості. Мала хмара — довіряй; велика — оцінка розмита.
    Хмара не додаток, а рівноправна половина оцінки."""
    W, H = 760, 340
    f = [text(W / 2, 30, "Оцінка — це точка ПЛЮС її коваріація (хмара)", size=17, bold=True)]

    # ліворуч: мала хмара — певно
    cx1, cy1 = 230, 195
    f.append(_ellipse(cx1, cy1, 52, 38, -18, GREEN, fill_op=0.16))
    f.append(circle(cx1, cy1, 4, fill=GREEN, stroke=GREEN, sw=2))
    f.append(text(cx1, cy1 + 78, "мала коваріація", size=13, bold=True, color=GREEN))
    f.append(text(cx1, cy1 + 96, "оцінці можна вірити", size=11, color=MUTED))

    # праворуч: велика хмара — непевно
    cx2, cy2 = 545, 195
    f.append(_ellipse(cx2, cy2, 105, 78, -18, POS, fill_op=0.10))
    f.append(circle(cx2, cy2, 4, fill=POS, stroke=POS, sw=2))
    f.append(text(cx2, cy2 + 100, "велика коваріація", size=13, bold=True, color=POS))
    f.append(text(cx2, cy2 + 118, "оцінка розмита", size=11, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "фільтр завжди знає не лише «де я», а й «наскільки я певен»",
                  size=12, color=INK))
    return render(os.path.join(IMG, "covariance-shape.svg"), W, H, *f)


# ── 2. крос-кореляція: вимір однієї змінної править пов'язану ─────────────────
def fig_cross_correlation():
    """Коваліація зберігає не лише розмір невпевненості, а й ЗВ'ЯЗКИ між
    змінними — як нахил хмари. Тоді вимір самого лише положення зсуває оцінку
    вздовж нахилу, підправляючи Й швидкість, якої ніхто не міряв."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Крос-кореляція: один вимір лікує всі пов'язані змінні", size=17, bold=True)]

    ox, oy = 110, 320       # початок осей
    aw, ah = 560, 250
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(text(ox + aw - 6, oy + 22, "положення", size=12, color=INK, italic=True, anchor="end"))
    f.append(text(ox - 14, oy - ah + 4, "швидкість", size=12, color=INK, italic=True, anchor="end"))

    cx, cy = ox + 0.46 * aw, oy - 0.50 * ah
    # нахилений еліпс — положення й швидкість корельовані
    f.append(_ellipse(cx, cy, 150, 56, -34, BLUE, fill_op=0.12, sw=2.6))
    f.append(text(cx + 120, cy - 70, "хмара нахилена:\nположення ↔ швидкість пов'язані",
                  size=11, color=BLUE, anchor="middle"))

    # вертикальна лінія виміру самого лише положення
    mx = ox + 0.66 * aw
    f.append(line(mx, oy, mx, oy - ah + 20, color=RED, sw=2.2, dash="6 5"))
    f.append(text(mx, oy - ah + 8, "вимір лише положення", size=11, bold=True, color=RED))

    # стрілка: оцінка зсувається вздовж нахилу — й по швидкості теж
    f.append(arrow(cx, cy, mx, cy - 0.50 * (mx - cx), color=GREEN, sw=2.6))
    f.append(circle(mx, cy - 0.50 * (mx - cx), 4, fill=GREEN, stroke=GREEN, sw=2))
    f.append(text(mx + 8, cy - 0.50 * (mx - cx) - 12,
                  "оцінка зсунулась і по ШВИДКОСТІ —\nхоч її ніхто не міряв",
                  size=11, bold=True, color=GREEN, anchor="start"))

    return render(os.path.join(IMG, "cross-correlation.svg"), W, H, *f)


# ── 3. лінеаризація: EKF підставляє дотичну до кривої в точці оцінки ──────────
def fig_ekf_linearize():
    """Класичний Калман любить прямі, а реальна модель крива. EKF бере ДОТИЧНУ
    до кривої в точці теперішньої оцінки й удає, що поблизу все лінійне.
    Працює, поки оцінка близька до правди; далеко дотична вже бреше."""
    W, H = 760, 360
    f = [text(W / 2, 30, "EKF: випрями криву дотичною в точці оцінки", size=17, bold=True)]

    ox, oy = 90, 300
    aw, ah = 580, 230
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(text(ox + aw - 6, oy + 22, "стан x", size=12, color=INK, italic=True, anchor="end"))
    f.append(text(ox - 14, oy - ah + 4, "f(x)", size=12, color=INK, italic=True, anchor="end"))

    # нелінійна крива f(x)
    def fx(t):  # t у 0..1 → значення 0..1
        return 0.12 + 0.80 / (1.0 + math.exp(-7.0 * (t - 0.52)))
    pts = []
    for i in range(0, 241):
        t = i / 240.0
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - fx(t) * ah))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), BLUE))
    f.append(text(ox + 0.86 * aw, oy - fx(0.86) * ah - 16, "справжня модель (крива)",
                  size=11, bold=True, color=BLUE, anchor="middle"))

    # точка оцінки й дотична
    t0 = 0.52
    x0 = ox + t0 * aw
    y0 = oy - fx(t0) * ah
    h = 1e-3
    slope = (fx(t0 + h) - fx(t0 - h)) / (2 * h) * ah / aw   # dпіксель/dпіксель
    dx = 150
    f.append(line(x0 - dx, y0 + slope * dx, x0 + dx, y0 - slope * dx, color=RED, sw=2.6))
    f.append(circle(x0, y0, 5, fill=GREEN, stroke=GREEN, sw=2))
    f.append(text(x0, y0 + 26, "точка оцінки", size=11, bold=True, color=GREEN))
    f.append(text(x0 + dx, y0 - slope * dx - 12, "дотична = лінійне\nнаближення «тут»",
                  size=11, bold=True, color=RED, anchor="middle"))
    f.append(text(x0 + dx + 70, y0 - slope * dx + 40, "далеко дотична\nвже бреше →",
                  size=10, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, "ekf-linearize.svg"), W, H, *f)


# ── 4. якобіан: матриця нахилів — як EKF переносить хмару крізь нелінійність ──
def fig_jacobian():
    """Серце EKF: на кожному кроці модель і вимір замінюють їхнім ЯКОБІАНОМ —
    матрицею частинних похідних у точці оцінки. Цей лінійний «нахил» і переносить
    коваріацію крізь нелінійність — за тими самими формулами, що й лінійний Калман."""
    W, H = 820, 330
    f = [text(W / 2, 30, "Якобіан — це матриця нахилів, нею EKF несе хмару крізь криву", size=16, bold=True)]

    cy = 175
    # ліворуч: нелінійна функція
    a = fitbox(40, cy - 50, 180, 100, "нелінійна модель\nx' = f(x)\nz = h(x)",
               size=12, bold=True, fill="#eef2fc", stroke=BLUE, color=BLUE)
    f.append(a)

    # центр: беремо похідні в точці оцінки
    f.append(arrow(220, cy, 300, cy))
    b = fitbox(302, cy - 50, 196, 100,
               "у точці оцінки беремо\nЧАСТИННІ ПОХІДНІ\n(матриці F, H)",
               size=12, bold=True, fill="#fdeeec", stroke=POS, color=POS)
    f.append(b)

    # праворуч: лінійний Калман по цих матрицях
    f.append(arrow(498, cy, 578, cy))
    c = fitbox(580, cy - 50, 200, 100,
               "далі — звичайний Калман:\nF·P·Fᵀ переносить хмару,\nH дає підсилення K",
               size=12, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD)
    f.append(c)

    f.append(text(W / 2, H - 16,
                  "F, H перелічують щокроку заново — бо нахил кривої свій у кожній точці",
                  size=12, color=INK))
    return render(os.path.join(IMG, "jacobian.svg"), W, H, *f)


if __name__ == "__main__":
    fig_covariance_shape()
    fig_cross_correlation()
    fig_ekf_linearize()
    fig_jacobian()
    print("OK: 4 фігури у", IMG)
