# -*- coding: utf-8 -*-
"""Фігури до теми «Крива Z-порядку (Morton Order)»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def dot(x, y, r=3.0, c=INK):
    return circle(x, y, r, fill=c, stroke=c, sw=0.5)


def polyline(pts, c=POS, sw=2.2):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, c, sw))


# ── 1. Сітка Z-кривої 4x4 з розбиттям та Morton-кодами ───────────────────────
def fig_morton_grid_2d():
    W, H = 760, 440
    X0, Y0, S = 70, 70, 320
    N = 4
    step = S / N

    frags = []
    
    # Сітка
    for i in range(N + 1):
        frags.append(line(X0 + i * step, Y0, X0 + i * step, Y0 + S, color=LINE, sw=1.0))
        frags.append(line(X0, Y0 + i * step, X0 + S, Y0 + i * step, color=LINE, sw=1.0))

    # Жирніші лінії квадрантів (посередині)
    frags.append(line(X0 + 2 * step, Y0, X0 + 2 * step, Y0 + S, color=LINE, sw=2.2))
    frags.append(line(X0, Y0 + 2 * step, X0 + S, Y0 + 2 * step, color=LINE, sw=2.2))

    # Координати осей
    for x in range(N):
        frags.append(text(X0 + (x + 0.5) * step, Y0 - 12, "x=%d (%s₂)" % (x, bin(x)[2:].zfill(2)), size=12, color=MUTED))
    for y in range(N):
        frags.append(text(X0 - 32, Y0 + (y + 0.5) * step + 4, "y=%d (%s₂)" % (y, bin(y)[2:].zfill(2)), size=12, color=MUTED))

    pts = []
    z_coords = []
    for z in range(N * N):
        x, y = 0, 0
        for bit in range(2):
            x |= ((z >> (2 * bit)) & 1) << bit
            y |= ((z >> (2 * bit + 1)) & 1) << bit
        cx = X0 + (x + 0.5) * step
        cy = Y0 + (y + 0.5) * step
        pts.append((cx, cy))
        z_coords.append((z, x, y, cx, cy))

    frags.append(polyline(pts, c=POS, sw=2.5))

    for z, x, y, cx, cy in z_coords:
        frags.append(dot(cx, cy, r=4.0, c=POS))
        z_bin = bin(z)[2:].zfill(4)
        lbl = "%d (%s)" % (z, z_bin)
        frags.append(text(cx, cy + 18, lbl, size=11, bold=True, color=INK))

    RX = 430
    frags.append(rect(RX, Y0, 300, S, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    
    body1, _, _ = textbox(RX + 150, Y0 + 40, "Правило створення Z-коду", size=15, bold=True, color=INK)
    frags.append(body1)

    body2, _, _ = textbox(RX + 150, Y0 + 150,
                          "1. Беремо біти координат x та y:\n"
                          "   x = x₁ x₀,  y = y₁ y₀\n\n"
                          "2. Переплітаємо біти (y під парні,\n"
                          "   x під непарні позиції):\n"
                          "   z = y₁ x₁ y₀ x₀\n\n"
                          "3. Порядок Z фрактально повторюється\n"
                          "   у кожному квадранті 2×2.",
                          size=13, color=INK)
    frags.append(body2)

    render(os.path.join(OUT, 'morton-grid-2d.svg'), W, H, *frags)


# ── 2. Схема побітового переплетення (Bit Interleaving) ─────────────────────
def fig_bit_interleaving():
    W, H = 760, 360
    frags = []

    Y_X = 60
    Y_Y = 130
    Y_Z = 240

    x_bits = [1, 0, 1, 1]  # x3 x2 x1 x0
    y_bits = [0, 1, 0, 1]  # y3 y2 y1 y0

    frags.append(text(80, Y_X + 20, "x = 11 (1011₂):", size=14, bold=True, color=NEG))
    for i in range(4):
        bx = 200 + i * 45
        frags.append(rect(bx, Y_X, 38, 32, fill="#fef2f2", stroke=NEG, sw=1.5, rx=4))
        frags.append(text(bx + 19, Y_X + 20, str(x_bits[i]), size=14, bold=True, color=NEG))
        frags.append(text(bx + 19, Y_X - 8, "x%d" % (3 - i), size=11, color=MUTED))

    frags.append(text(80, Y_Y + 20, "y = 5  (0101₂):", size=14, bold=True, color=POS))
    for i in range(4):
        bx = 200 + i * 45
        frags.append(rect(bx, Y_Y, 38, 32, fill="#eff6ff", stroke=POS, sw=1.5, rx=4))
        frags.append(text(bx + 19, Y_Y + 20, str(y_bits[i]), size=14, bold=True, color=POS))
        frags.append(text(bx + 19, Y_Y - 8, "y%d" % (3 - i), size=11, color=MUTED))

    z_bits = [
        ('y', 0, y_bits[0]), ('x', 0, x_bits[0]),
        ('y', 1, y_bits[1]), ('x', 1, x_bits[1]),
        ('y', 2, y_bits[2]), ('x', 2, x_bits[2]),
        ('y', 3, y_bits[3]), ('x', 3, x_bits[3])
    ]

    frags.append(text(80, Y_Z + 20, "z (Morton Key):", size=14, bold=True, color=FIELD))

    for i, (var, orig_idx, val) in enumerate(z_bits):
        bx = 200 + i * 36
        bg_col = "#eff6ff" if var == 'y' else "#fef2f2"
        bd_col = POS if var == 'y' else NEG
        frags.append(rect(bx, Y_Z, 32, 32, fill=bg_col, stroke=bd_col, sw=1.5, rx=4))
        frags.append(text(bx + 16, Y_Z + 20, str(val), size=14, bold=True, color=bd_col))
        bit_name = "%s%d" % (var, 3 - orig_idx)
        frags.append(text(bx + 16, Y_Z + 46, bit_name, size=11, color=bd_col))

        src_y = Y_Y + 32 if var == 'y' else Y_X + 32
        src_x = 200 + orig_idx * 45 + 19
        dst_x = bx + 16
        frags.append(line(src_x, src_y + 4, dst_x, Y_Z - 4, color=bd_col, sw=1.0))

    frags.append(text(530, Y_Z + 20, "= 103 (01100111₂)", size=14, bold=True, color=INK))

    render(os.path.join(OUT, 'bit-interleaving.svg'), W, H, *frags)


# ── 3. Розрив (Discontinuity) та порівняння з кривою Гільберта ──────────────
def fig_z_jump_discontinuity():
    W, H = 760, 380
    frags = []

    X1, Y0, S = 50, 60, 240
    frags.append(rect(X1, Y0, S, S, fill="#fafafa", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(X1 + S / 2, Y0 - 16, "Крива Z-порядку (скачки на межах)", size=14, bold=True, color=INK))

    step = S / 2
    pts_z = [
        (X1 + 0.5 * step, Y0 + 0.5 * step),
        (X1 + 1.5 * step, Y0 + 0.5 * step),
        (X1 + 0.5 * step, Y0 + 1.5 * step),
        (X1 + 1.5 * step, Y0 + 1.5 * step),
    ]
    
    frags.append(polyline(pts_z, c=POS, sw=2.5))
    
    A_pt = (X1 + step - 10, Y0 + 0.5 * step)
    B_pt = (X1 + step + 10, Y0 + 0.5 * step)
    frags.append(dot(A_pt[0], A_pt[1], r=5.0, c=NEG))
    frags.append(dot(B_pt[0], B_pt[1], r=5.0, c=NEG))
    
    frags.append(line(A_pt[0], A_pt[1], B_pt[0], B_pt[1], color=NEG, sw=2.0))
    
    tb1, _, _ = textbox(X1 + S / 2, Y0 + S + 45,
                        "Точки поруч на площині,\nале Morton index стрибає\nчерез увесь простір!",
                        size=12, color=NEG)
    frags.append(tb1)

    X2 = 430
    frags.append(rect(X2, Y0, S, S, fill="#fafafa", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(X2 + S / 2, Y0 - 16, "Крива Гільберта (неперервна)", size=14, bold=True, color=INK))

    pts_h = [
        (X2 + 0.5 * step, Y0 + 1.5 * step),
        (X2 + 0.5 * step, Y0 + 0.5 * step),
        (X2 + 1.5 * step, Y0 + 0.5 * step),
        (X2 + 1.5 * step, Y0 + 1.5 * step),
    ]
    frags.append(polyline(pts_h, c=FIELD, sw=2.5))

    for px, py in pts_h:
        frags.append(dot(px, py, r=4.0, c=FIELD))

    tb2, _, _ = textbox(X2 + S / 2, Y0 + S + 45,
                        "Крива повертається та зберігає\nсуміжність сусідніх осередків\nбез великих скачків.",
                        size=12, color=FIELD)
    frags.append(tb2)

    render(os.path.join(OUT, 'z-jump-discontinuity.svg'), W, H, *frags)


# ── 4. Пошук у вікні (Range Query) та пропуск чужих кодів BIGMIN ────────────
def fig_range_query_bigmin():
    W, H = 760, 420
    X0, Y0, S = 60, 60, 300
    step = S / 4

    frags = []

    for i in range(5):
        frags.append(line(X0 + i * step, Y0, X0 + i * step, Y0 + S, color=LINE, sw=1.0))
        frags.append(line(X0, Y0 + i * step, X0 + S, Y0 + i * step, color=LINE, sw=1.0))

    pts = []
    for z in range(16):
        x, y = 0, 0
        for bit in range(2):
            x |= ((z >> (2 * bit)) & 1) << bit
            y |= ((z >> (2 * bit + 1)) & 1) << bit
        pts.append((X0 + (x + 0.5) * step, Y0 + (y + 0.5) * step))
    frags.append(polyline(pts, c="#cbd5e1", sw=1.8))

    WX = X0 + 1 * step
    WY = Y0 + 1 * step
    WW = 2 * step
    WH = 2 * step
    frags.append(rect(WX, WY, WW, WH, fill="#e6f7ec", stroke=FIELD, sw=2.5, rx=0))
    frags.append(text(WX + WW - 25, WY + 20, "Вікно Q", size=13, bold=True, color=FIELD))

    for z in range(16):
        x, y = 0, 0
        for bit in range(2):
            x |= ((z >> (2 * bit)) & 1) << bit
            y |= ((z >> (2 * bit + 1)) & 1) << bit
        cx = X0 + (x + 0.5) * step
        cy = Y0 + (y + 0.5) * step

        in_rect = (1 <= x <= 2) and (1 <= y <= 2)
        col = FIELD if in_rect else MUTED
        r_size = 4.5 if in_rect else 3.0
        frags.append(dot(cx, cy, r=r_size, c=col))
        frags.append(text(cx, cy + 15, str(z), size=11, bold=True, color=col))

    RX = 400
    frags.append(rect(RX, Y0, 320, S, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    
    body1, _, _ = textbox(RX + 160, Y0 + 40, "Проблема 1D діапазону", size=15, bold=True, color=INK)
    frags.append(body1)

    body2, _, _ = textbox(RX + 160, Y0 + 160,
                          "Мінімальний Z у вікні: z_min = 5 (0101₂)\n"
                          "Максимальний Z у вікні: z_max = 15 (1111₂)\n\n"
                          "Але діапазон [5..15] містить чужі точки:\n"
                          "  • z = 8, 9, 10, 11 (поза вікном!)\n\n"
                          "Алгоритм BIGMIN / LITMAX:\n"
                          "  Виявляє вихід за межі вікна та\n"
                          "  перестрибує одразу з z=7 на z=12,\n"
                          "  обминаючи перебір чужих точок.",
                          size=12, color=INK)
    frags.append(body2)

    render(os.path.join(OUT, 'range-query-bigmin.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_morton_grid_2d()
    fig_bit_interleaving()
    fig_z_jump_discontinuity()
    fig_range_query_bigmin()
    print("Успішно згенеровано 4 фігури в directory img/")
