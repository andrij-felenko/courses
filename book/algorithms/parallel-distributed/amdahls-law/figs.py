# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори для кривих прискорення
C_IDEAL = "#16a085"      # Ідеальне лінійне
C_P99   = FIELD          # p = 99% (зелений)
C_P95   = "#2457d6"      # p = 95% (синій)
C_P90   = "#8e44ad"      # p = 90% (фіолетовий)
C_P75   = "#e08a1e"      # p = 75% (помаранчевий)
C_P50   = POS            # p = 50% (червоний)


# ── Фігура 1: Криві прискорення закону Амдала ──────────────────────────────────
def fig_amdahl_speedup_curves():
    W, H = 940, 520
    p = []
    ox, oy = 85.0, 440.0
    pw, ph = 540.0, 360.0
    N_max = 64.0
    S_max = 32.0

    def X(n):
        return ox + pw * (n - 1.0) / (N_max - 1.0)

    def Y(s):
        return oy - ph * min(s, S_max) / S_max

    # Осі
    p.append(line(ox, oy, ox + pw + 15, oy, color=INK, sw=1.5))
    p.append(line(ox, oy, ox, oy - ph - 15, color=INK, sw=1.5))
    p.append(text(ox + pw / 2, oy + 42, "кількість ядер / процесорів  (N)  →", size=13, color=INK, bold=True))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="13" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 55, oy - ph / 2, FONT, INK, esc("теоретичне прискорення  S(N)  →")))

    # Позначки по осі X
    for n_val in [1, 8, 16, 24, 32, 40, 48, 56, 64]:
        x_pos = X(n_val)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=INK, sw=1.2))
        p.append(text(x_pos, oy + 20, str(n_val), size=11.5, color=INK))
        if n_val > 1:
            p.append(line(x_pos, oy, x_pos, oy - ph, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Позначки по осі Y
    for s_val in [1, 4, 8, 12, 16, 20, 24, 28, 32]:
        y_pos = Y(s_val)
        p.append(line(ox - 5, y_pos, ox, y_pos, color=INK, sw=1.2))
        p.append(text(ox - 12, y_pos + 4, "%d×" % s_val, size=11.5, color=INK, anchor="end"))
        if s_val > 1:
            p.append(line(ox, y_pos, ox + pw, y_pos, color="#e5e7eb", sw=1.0, dash="3 3"))

    # Функція побудови кривої Амдала
    def plot_amdahl(par_frac, color, dash=None):
        pts = []
        n = 1.0
        while n <= N_max + 1e-6:
            s_val = 1.0 / ((1.0 - par_frac) + par_frac / n)
            pts.append((X(n), Y(s_val)))
            n += 0.5
        poly = " ".join("%.1f,%.1f" % (x_pt, y_pt) for x_pt, y_pt in pts)
        d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>' % (poly, color, d_attr))

    # Побудова кривих
    plot_amdahl(0.50, C_P50)
    plot_amdahl(0.75, C_P75)
    plot_amdahl(0.90, C_P90)
    plot_amdahl(0.95, C_P95)
    plot_amdahl(0.99, C_P99)

    # Асимптотичні стелі
    for par_frac, col, label_txt in [
        (0.50, C_P50, "стеля 2× (p = 50%)"),
        (0.75, C_P75, "стеля 4× (p = 75%)"),
        (0.90, C_P90, "стеля 10× (p = 90%)"),
        (0.95, C_P95, "стеля 20× (p = 95%)"),
    ]:
        asymptote = 1.0 / (1.0 - par_frac)
        y_as = Y(asymptote)
        p.append(line(ox, y_as, ox + pw, y_as, color=col, sw=1.2, dash="5 4"))

    # Ідеальна лінія (N)
    pts_ideal = []
    n = 1.0
    while n <= N_max:
        s_val = n
        if s_val > S_max:
            t = (S_max - (n - 1)) / 1.0
            pts_ideal.append((X(n - 1 + t), Y(S_max)))
            break
        pts_ideal.append((X(n), Y(s_val)))
        n += 1.0
    poly_id = " ".join("%.1f,%.1f" % (x_pt, y_pt) for x_pt, y_pt in pts_ideal)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4 3"/>' % (poly_id, C_IDEAL))
    p.append(text(X(32) + 5, Y(32) - 10, "ідеальне лінійне S=N", size=11, color=C_IDEAL, bold=True, anchor="start"))

    # Легенда
    lx, ly, lw, lh = 660.0, 75.0, 255.0, 365.0
    p.append(rect(lx, ly, lw, lh, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "паралельна частка (p)", size=13, color=INK, bold=True))

    rows = [
        (C_P99, "p = 99%  (s = 1%)",  "макс. 100× (на N=64: 39.3×)"),
        (C_P95, "p = 95%  (s = 5%)",  "макс. 20×  (на N=64: 15.4×)"),
        (C_P90, "p = 90%  (s = 10%)", "макс. 10×  (на N=64: 8.7×)"),
        (C_P75, "p = 75%  (s = 25%)", "макс. 4×   (на N=64: 3.8×)"),
        (C_P50, "p = 50%  (s = 50%)", "макс. 2×   (на N=64: 1.97×)"),
        (C_IDEAL, "p = 100% (s = 0%)", "ідеальне: S = N (без меж)"),
    ]
    ry = ly + 56
    for col, name, note in rows:
        p.append(line(lx + 16, ry + 3, lx + 44, ry + 3, color=col, sw=3.2))
        p.append(text(lx + 52, ry - 3, name, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 52, ry + 15, note, size=10.5, color=MUTED, anchor="start"))
        ry += 46

    # Нижнє підсумкове повідомлення
    box_s, _, _ = textbox(lx + lw / 2, ly + lh - 25, "S_max = 1 / (1 − p) = 1 / s", size=11.5,
                          pad=6, fill="#edf2f7", stroke="#cbd5e1", bold=True)
    p.append(box_s)

    render(os.path.join(OUT, "amdahl-speedup-curves.svg"), W, H, *p,
           title="Закон Амдала: прискорення S(N) та асимптотична стеля для різних p")


# ── Фігура 2: Структура часу виконання (декомпозиція) ────────────────────────
def fig_execution_time_breakdown():
    W, H = 940, 490
    p = []

    start_x = 130.0
    scale_w = 5.2    # 100 од. * 5.2 = 520 px
    start_y = 80.0
    row_h = 42.0
    row_gap = 20.0

    # Фонова шкала часу
    p.append(line(start_x, start_y + 6 * (row_h + row_gap) - 5, start_x + 100 * scale_w, start_y + 6 * (row_h + row_gap) - 5, color=LINE, sw=1.5))
    for t_mark in [0, 20, 40, 60, 80, 100]:
        mx = start_x + t_mark * scale_w
        p.append(line(mx, start_y - 10, mx, start_y + 6 * (row_h + row_gap) - 5, color="#f1f5f9", sw=1.0, dash="3 3"))
        p.append(text(mx, start_y + 6 * (row_h + row_gap) + 16, "%d%%" % t_mark, size=11.5, color=MUTED))
    p.append(text(start_x + 50 * scale_w, start_y + 6 * (row_h + row_gap) + 36, "загальний час виконання (від початкового T₁) →", size=12, color=INK, bold=True))

    runs = [
        ("N = 1 ядро",   20.0, 80.0, "100.0%  (1.00×)", False),
        ("N = 2 ядра",   20.0, 40.0, "60.0%   (1.67×)", False),
        ("N = 4 ядра",   20.0, 20.0, "40.0%   (2.50×)", False),
        ("N = 8 ядер",   20.0, 10.0, "30.0%   (3.33×)", False),
        ("N = 16 ядер",  20.0,  5.0, "25.0%   (4.00×)", False),
        ("N → ∞ ядер",   20.0,  0.0, "20.0%   (5.00× стеля)", True),
    ]

    for idx, (label_txt, s_len, p_len, res_txt, is_limit) in enumerate(runs):
        cy = start_y + idx * (row_h + row_gap)
        p.append(text(start_x - 14, cy + row_h / 2 + 4, label_txt, size=12.5, color=INK, bold=True, anchor="end"))

        # Послідовна частина
        sx = start_x
        sw = s_len * scale_w
        p.append(rect(sx, cy, sw, row_h, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
        p.append(text(sx + sw / 2, cy + row_h / 2 + 4, "Ts (20%)", size=11, color=POS, bold=True))

        # Паралельна частина
        if p_len > 0:
            px = sx + sw
            pw = p_len * scale_w
            p.append(rect(px, cy, pw, row_h, fill="#dbeafe", stroke=NEG, sw=1.8, rx=4))
            if p_len >= 15:
                p.append(text(px + pw / 2, cy + row_h / 2 + 4, "паралельна (%.0f%%)" % p_len, size=11, color=NEG, bold=True))
            elif p_len >= 8:
                p.append(text(px + pw / 2, cy + row_h / 2 + 4, "%.0f%%" % p_len, size=10, color=NEG, bold=True))

        # Результат
        total_w = (s_len + p_len) * scale_w
        res_color = POS if is_limit else INK
        p.append(text(start_x + total_w + 14, cy + row_h / 2 + 4, res_txt, size=12, color=res_color, bold=True, anchor="start"))

    # Позначення незнищенного порогу зверху
    line_x = start_x + 20.0 * scale_w
    p.append(line(line_x, start_y - 8, line_x, start_y + 6 * (row_h + row_gap) - 8, color=POS, sw=1.5, dash="4 4"))
    p.append(text(line_x, start_y - 18, "послідовний поріг Ts = 20%", size=11, color=POS, bold=True, anchor="middle"))

    rx_box, ry_box, rw_box, rh_box = 705.0, 75.0, 220.0, 350.0
    p.append(rect(rx_box, ry_box, rw_box, rh_box, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=8))
    p.append(text(rx_box + rw_box / 2, ry_box + 22, "Ключовий висновок", size=12.5, color=INK, bold=True))

    notes = [
        "1. Послідовна частка s",
        "не зменшується",
        "зі збільшенням ядер.",
        "",
        "2. Навіть якщо паралельна",
        "частина стискається до 0,",
        "час виконання ніколи",
        "не впаде нижче Ts.",
        "",
        "3. При 20% послідовного коду",
        "максимальне прискорення",
        "дорівнює рівно 5×.",
    ]
    ny = ry_box + 48
    for n_line in notes:
        bold_flag = n_line.startswith("1.") or n_line.startswith("2.") or n_line.startswith("3.")
        col = POS if "5×" in n_line or "нижче Ts" in n_line else INK
        p.append(text(rx_box + 12, ny, n_line, size=11, color=col, bold=bold_flag, anchor="start"))
        ny += 21

    render(os.path.join(OUT, "execution-time-breakdown.svg"), W, H, *p,
           title="Декомпозиція часу виконання при зростанні кількості ядер (s = 20%, p = 80%)")


# ── Фігура 3: Порівняння моделей масштабування (Амдал, Густафсон, USL) ─────────
def fig_scaling_models_comparison():
    W, H = 940, 520
    p = []
    ox, oy = 85.0, 440.0
    pw, ph = 540.0, 360.0
    N_max = 64.0
    S_max = 36.0

    def X(n):
        return ox + pw * (n - 1.0) / (N_max - 1.0)

    def Y(s):
        return oy - ph * min(max(s, 0.0), S_max) / S_max

    p.append(line(ox, oy, ox + pw + 15, oy, color=INK, sw=1.5))
    p.append(line(ox, oy, ox, oy - ph - 15, color=INK, sw=1.5))
    p.append(text(ox + pw / 2, oy + 42, "кількість вузлів / процесорів  (N)  →", size=13, color=INK, bold=True))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="13" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 55, oy - ph / 2, FONT, INK, esc("ефективне прискорення  S(N)  →")))

    for n_val in [1, 8, 16, 24, 32, 40, 48, 56, 64]:
        x_pos = X(n_val)
        p.append(line(x_pos, oy, x_pos, oy + 5, color=INK, sw=1.2))
        p.append(text(x_pos, oy + 20, str(n_val), size=11.5, color=INK))
        if n_val > 1:
            p.append(line(x_pos, oy, x_pos, oy - ph, color="#f1f5f9", sw=1.0, dash="3 3"))

    for s_val in [1, 6, 12, 18, 24, 30, 36]:
        y_pos = Y(s_val)
        p.append(line(ox - 5, y_pos, ox, y_pos, color=INK, sw=1.2))
        p.append(text(ox - 12, y_pos + 4, "%d×" % s_val, size=11.5, color=INK, anchor="end"))
        if s_val > 1:
            p.append(line(ox, y_pos, ox + pw, y_pos, color="#f1f5f9", sw=1.0, dash="3 3"))

    pts_ideal = [(X(1), Y(1)), (X(36), Y(36))]
    poly_id = " ".join("%.1f,%.1f" % pt for pt in pts_ideal)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' % (poly_id, "#94a3b8"))
    p.append(text(X(22), Y(28), "ідеальне (S = N)", size=11, color="#64748b", bold=True, anchor="end"))

    pts_gust = []
    n = 1.0
    while n <= N_max:
        s_val = 0.10 + 0.90 * n
        if s_val > S_max:
            t = (S_max - (0.10 + 0.90 * (n - 1))) / 0.90
            pts_gust.append((X(n - 1 + t), Y(S_max)))
            break
        pts_gust.append((X(n), Y(s_val)))
        n += 1.0
    poly_gu = " ".join("%.1f,%.1f" % pt for pt in pts_gust)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_gu, FIELD))

    pts_amd = []
    n = 1.0
    while n <= N_max:
        s_val = 1.0 / (0.10 + 0.90 / n)
        pts_amd.append((X(n), Y(s_val)))
        n += 0.5
    poly_am = " ".join("%.1f,%.1f" % pt for pt in pts_amd)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_am, NEG))

    p.append(line(ox, Y(10.0), ox + pw, Y(10.0), color=NEG, sw=1.2, dash="5 4"))
    p.append(text(ox + pw - 8, Y(10.0) - 8, "стеля Амдала: 10× (s = 10%)", size=11, color=NEG, anchor="end", bold=True))

    pts_usl = []
    sigma, kappa = 0.05, 0.0018
    n = 1.0
    while n <= N_max:
        s_val = n / (1.0 + sigma * (n - 1.0) + kappa * n * (n - 1.0))
        pts_usl.append((X(n), Y(s_val)))
        n += 0.5
    poly_us = " ".join("%.1f,%.1f" % pt for pt in pts_usl)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_us, POS))

    n_peak = math.sqrt((1.0 - sigma) / kappa) if kappa > 0 else 0
    s_peak = n_peak / (1.0 + sigma * (n_peak - 1.0) + kappa * n_peak * (n_peak - 1.0))
    p.append(circle(X(n_peak), Y(s_peak), 4.5, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(X(n_peak), Y(s_peak) - 14, "пік USL (N ≈ 22)", size=11, color=POS, bold=True, anchor="middle"))
    p.append(arrow(X(30), Y(s_peak) - 30, X(38), Y(s_peak) - 10, color=POS, sw=1.5))
    p.append(text(X(28), Y(s_peak) - 34, "ретроградне падіння (USL)", size=10.5, color=POS, bold=True, anchor="middle"))

    lx, ly, lw, lh = 660.0, 75.0, 255.0, 365.0
    p.append(rect(lx, ly, lw, lh, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "Порівняння моделей", size=13, color=INK, bold=True))

    rows_models = [
        (FIELD, "Густафсон (Weak Scaling)", "Збільшуємо задачу разом із N;\nлінійне прискорення S ≈ s + N·p"),
        (NEG,   "Амдал (Strong Scaling)",   "Фіксований обсяг задачі;\nвпирається в стелю S ≤ 1/s"),
        (POS,   "USL Ґюнтера (Реальне)",    "Враховує когерентність κ;\nпісля піка швидкість падає!"),
    ]
    ry = ly + 58
    for col, name, note in rows_models:
        p.append(line(lx + 16, ry + 4, lx + 44, ry + 4, color=col, sw=3.4))
        p.append(text(lx + 52, ry - 3, name, size=11.5, color=INK, bold=True, anchor="start"))
        lines_note = note.split("\n")
        p.append(text(lx + 52, ry + 15, lines_note[0], size=10.5, color=MUTED, anchor="start"))
        p.append(text(lx + 52, ry + 29, lines_note[1], size=10.5, color=MUTED, anchor="start"))
        ry += 60

    box_usl, _, _ = textbox(lx + lw / 2, ly + lh - 25, "Реальність: замки + кеш-трафік", size=11.5,
                            pad=6, fill="#fef2f2", stroke="#fca5a5", color=POS, bold=True)
    p.append(box_usl)

    render(os.path.join(OUT, "scaling-models-comparison.svg"), W, H, *p,
           title="Порівняння законів масштабування: Амдал vs Густафсон vs USL Ґюнтера")


# ── Фігура 4: Гетерогенна архітектура чіпа (модель Гілла і Марті) ──────────────
def fig_multicore_chip_heterogeneous():
    W, H = 940, 480
    p = []

    col_w = 420.0
    col_h = 380.0
    cy_top = 65.0

    # 1. Симетричний чип (SMP)
    lx1 = 35.0
    p.append(rect(lx1, cy_top, col_w, col_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    p.append(text(lx1 + col_w / 2, cy_top + 28, "Симетричний мультипроцесор (SMP)", size=13.5, color=INK, bold=True))
    p.append(text(lx1 + col_w / 2, cy_top + 48, "16 однакових базових ядер (16 BCE бюджету)", size=11, color=MUTED))

    grid_start_x = lx1 + 55.0
    grid_start_y = cy_top + 70.0
    cell_s = 65.0
    cell_gap = 14.0

    for r in range(4):
        for c in range(4):
            cx = grid_start_x + c * (cell_s + cell_gap)
            cy = grid_start_y + r * (cell_s + cell_gap)
            is_active_serial = (r == 0 and c == 0)
            fill_c = "#fee2e2" if is_active_serial else "#f1f5f9"
            stroke_c = POS if is_active_serial else "#94a3b8"
            p.append(rect(cx, cy, cell_s, cell_s, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
            if is_active_serial:
                p.append(text(cx + cell_s / 2, cy + cell_s / 2 - 6, "Ядро 0", size=11, color=POS, bold=True))
                p.append(text(cx + cell_s / 2, cy + cell_s / 2 + 10, "послідовно", size=9.5, color=POS))
            else:
                p.append(text(cx + cell_s / 2, cy + cell_s / 2 - 6, "Ядро %d" % (r * 4 + c), size=10.5, color=MUTED))
                p.append(text(cx + cell_s / 2, cy + cell_s / 2 + 10, "простій (IDLE)", size=9, color="#94a3b8"))

    p.append(text(lx1 + col_w / 2, cy_top + col_h - 18, "⚠️ У послідовній фазі 15 ядер із 16 гріють повітря!", size=11, color=POS, bold=True))

    # 2. Асиметричний чип (AMP)
    lx2 = 485.0
    p.append(rect(lx2, cy_top, col_w, col_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    p.append(text(lx2 + col_w / 2, cy_top + 28, "Асиметричний чіп (AMP / big.LITTLE)", size=13.5, color=INK, bold=True))
    p.append(text(lx2 + col_w / 2, cy_top + 48, "1 велике ядро (4 BCE) + 12 малих ядер (12 BCE)", size=11, color=MUTED))

    big_w = cell_s * 2 + cell_gap
    big_h = cell_s * 2 + cell_gap
    bx = lx2 + 55.0
    by = cy_top + 70.0
    p.append(rect(bx, by, big_w, big_h, fill="#dcfce7", stroke=FIELD, sw=2.2, rx=8))
    p.append(text(bx + big_w / 2, by + big_h / 2 - 14, "ВЕЛИКЕ ЯДРО (4 BCE)", size=12.5, color=FIELD, bold=True))
    p.append(text(bx + big_w / 2, by + big_h / 2 + 4, "Глибокий Out-of-Order, великий L2", size=10, color=INK))
    p.append(text(bx + big_w / 2, by + big_h / 2 + 20, "2.5× швидкість Ts у послідовній фазі", size=10, color=FIELD, bold=True))

    small_coords = [
        (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ]

    for idx, (r, c) in enumerate(small_coords):
        cx = lx2 + 55.0 + c * (cell_s + cell_gap)
        cy = cy_top + 70.0 + r * (cell_s + cell_gap)
        p.append(rect(cx, cy, cell_s, cell_s, fill="#eff6ff", stroke=NEG, sw=1.4, rx=6))
        p.append(text(cx + cell_s / 2, cy + cell_s / 2 - 6, "Мале %d" % (idx + 1), size=10, color=NEG, bold=True))
        p.append(text(cx + cell_s / 2, cy + cell_s / 2 + 10, "1 BCE", size=9, color=MUTED))

    p.append(text(lx2 + col_w / 2, cy_top + col_h - 18, "✓ Послідовна фаза прискорена в 2.5×, паралельна — на всіх 13 ядрах", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "multicore-chip-heterogeneous.svg"), W, H, *p,
           title="Закон Амдала для мультиядерних систем: симетричний (SMP) vs асиметричний (AMP) чіп")


if __name__ == "__main__":
    fig_amdahl_speedup_curves()
    fig_execution_time_breakdown()
    fig_scaling_models_comparison()
    fig_multicore_chip_heterogeneous()
    print("Всі 4 фігури успішно згенеровано у %s" % OUT)
