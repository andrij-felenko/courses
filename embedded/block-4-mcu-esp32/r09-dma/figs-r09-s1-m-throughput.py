# -*- coding: utf-8 -*-
"""
Фігури для вставки r09-s1-m-throughput.md
Рис. 4.9.1m.1 — стеля без DMA: R(макс) = f/c і де її пробивають реальні потоки
Рис. 4.9.1m.2 — чому «переривання на кожен елемент» дороге: ISR-overhead

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.1m.1 — стеля R(макс) у двох режимах, реальні потоки
# ══════════════════════════════════════════════════════════════════════════════
def fig1_ceiling():
    W, H = 740, 450
    frags = []

    # ── Геометрія зони графіка ──────────────────────────────────────────────
    ox, oy = 75, 380     # початок координат (лівий нижній)
    aw, ah = 560, 310    # ширина та висота зони

    # ── Осі ─────────────────────────────────────────────────────────────────
    frags.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=2))

    # Підпис осі X (лог-шкала: кБ/с → МБ/с)
    frags.append(text(ox + aw / 2, oy + 40, "Потік R (байти/с, логарифмічна шкала)",
                      size=12, color=INK, anchor="middle"))
    # Підпис осі Y
    frags.append(text(ox - 55, oy - ah / 2, "Частка ядра\nU = R / R(макс)",
                      size=12, color=INK, anchor="middle"))

    # ── Логарифмічна шкала X: розмітка ─────────────────────────────────────
    # 10 кБ/с ... 1000 МБ/с → log10 від 4 до 9 (5 декад)
    import math
    x_min_log = 4.0   # log10(10 kB/s) = 4 + log10(10) → 10e3 B/s
    x_max_log = 9.0   # 1 GB/s
    # Відображення log10(R) → пікселі
    def x_px(log_r):
        return ox + (log_r - x_min_log) / (x_max_log - x_min_log) * aw

    tick_labels = {
        4: "10 кБ/с",
        5: "100 кБ/с",
        6: "1 МБ/с",
        7: "10 МБ/с",
        8: "100 МБ/с",
    }
    for log_v, lbl in tick_labels.items():
        xp = x_px(log_v)
        frags.append(line(xp, oy, xp, oy + 6, color=INK, sw=1.2))
        frags.append(text(xp, oy + 18, lbl, size=10, color=MUTED, anchor="middle"))

    # ── Лінійна шкала Y: 0..120% (відображаємо до 110%) ────────────────────
    y_max_pct = 120.0
    def y_px(pct):
        return oy - pct / y_max_pct * ah

    for pct in [0, 20, 40, 60, 80, 100]:
        yp = y_px(pct)
        frags.append(line(ox - 5, yp, ox + 5, yp, color=INK, sw=1.2))
        frags.append(text(ox - 10, yp + 4, "%d%%" % pct, size=10, color=MUTED, anchor="end"))

    # ── Червона лінія U = 100% ───────────────────────────────────────────────
    y100 = y_px(100)
    frags.append(line(ox, y100, ox + aw, y100, color=POS, sw=2.0, dash="6,4"))
    frags.append(text(ox + aw + 4, y100 + 4, "100%\n(обрив)", size=10, color=POS, anchor="start"))

    # ── Дві стелі (прямі лінії U = R / R_max) ───────────────────────────────
    # Режим А: щільне копіювання — R_max_A ≈ 240 МБ/с (log10 ≈ 8.38)
    log_rmax_A = math.log10(240e6)   # 8.38
    # Режим Б: переривання на кожне слово — R_max_B ≈ 16 МБ/с (log10 ≈ 7.20)
    log_rmax_B = math.log10(16e6)    # 7.20

    # Для кожного режиму: U(R) = R / R_max → у логарифмічному просторі:
    # U = 10^(log_r) / R_max = 10^(log_r - log_rmax)
    # Прямий/кривий графік: крива, але для ілюстрації малюємо ламану по точках
    def u_pct(log_r, log_rmax):
        return 10 ** (log_r - log_rmax) * 100.0

    def draw_ceiling_line(log_rmax, color, n_pts=60):
        pts_x = [x_px(x_min_log + i * (x_max_log - x_min_log) / n_pts) for i in range(n_pts + 1)]
        pts_y = [y_px(min(u_pct(x_min_log + i * (x_max_log - x_min_log) / n_pts, log_rmax), 115))
                 for i in range(n_pts + 1)]
        path_d = "M%.1f,%.1f" % (pts_x[0], pts_y[0])
        for xi, yi in zip(pts_x[1:], pts_y[1:]):
            path_d += " L%.1f,%.1f" % (xi, yi)
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, color))

    draw_ceiling_line(log_rmax_A, NEG)
    draw_ceiling_line(log_rmax_B, POS)

    # Підписи кривих
    # Режим А — підпис лівіше від перетину з U=80%
    log_r_A_80 = log_rmax_A + math.log10(0.80)
    xA80 = x_px(log_r_A_80)
    tb_a, wa, _ = textbox(xA80 - 80, y_px(80) - 28,
                           "Режим А\n(щільний цикл, c ≈ 4 такти/слово)\nR(макс) ≈ 240 МБ/с",
                           size=10, fill="#eaf0fd", stroke=NEG)
    frags.append(tb_a)

    # Режим Б — підпис правіше
    log_r_B_60 = log_rmax_B + math.log10(0.60)
    xB60 = x_px(log_r_B_60)
    tb_b, wb, _ = textbox(xB60 + 110, y_px(60) - 30,
                           "Режим Б\n(переривання на елемент, c ≈ 60 тактів)\nR(макс) ≈ 16 МБ/с",
                           size=10, fill="#fdecea", stroke=POS)
    frags.append(tb_b)

    # ── Маркери реальних потоків на кривій режиму Б ──────────────────────────
    streams = [
        (384e3,   "I2S-аудіо\n384 кБ/с",  -55, -25, FIELD),
        (2e6,     "АЦП 1 МСемпл/с\n2 МБ/с", 10, -45, MUTED),
        (4.6e6,   "SPI-дисплей\n4.6 МБ/с",  10, -45, INK),
    ]
    for R_val, lbl, dx_lbl, dy_lbl, col in streams:
        log_r = math.log10(R_val)
        xp = x_px(log_r)
        u = min(u_pct(log_r, log_rmax_B), 115)
        yp = y_px(u)
        # Точка-маркер
        frags.append(circle(xp, yp, 5, fill=col, stroke=col))
        # Пунктир до осі X
        frags.append(line(xp, yp, xp, oy, color=col, sw=1.0, dash="4,3"))
        # Підпис
        tb_s, _, _ = textbox(xp + dx_lbl, yp + dy_lbl, lbl, size=9, fill=FILL, stroke=col, color=col)
        frags.append(tb_s)

    # ── Легенда ──────────────────────────────────────────────────────────────
    lx, ly = ox + 20, oy - ah + 15
    frags.append(line(lx, ly + 10, lx + 28, ly + 10, color=NEG, sw=2.5))
    frags.append(text(lx + 34, ly + 14, "Режим А: щільний цикл (c ≈ 4 такти/слово)", size=10, color=NEG, anchor="start"))
    frags.append(line(lx, ly + 26, lx + 28, ly + 26, color=POS, sw=2.5))
    frags.append(text(lx + 34, ly + 30, "Режим Б: переривання на елемент (c ≈ 60 тактів)", size=10, color=POS, anchor="start"))
    frags.append(line(lx, ly + 42, lx + 28, ly + 42, color=POS, sw=1.5, dash="5,3"))
    frags.append(text(lx + 34, ly + 46, "U = 100% — обрив (аналог §4.5.7m)", size=10, color=POS, anchor="start"))

    render(os.path.join(OUT, "fig-09-1m-1-ceiling.svg"), W, H, *frags,
           title="Рис. 4.9.1m.1. Стеля без DMA: R(макс) = f(такт)/c і де її пробивають реальні потоки")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.1m.2 — ціна одного перенесення у двох режимах (bar-смуги в тактах)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_isr_cost():
    W, H = 740, 320
    frags = []

    # ── Геометрія ─────────────────────────────────────────────────────────────
    bar_h = 46          # висота кожної смуги
    row_A = 110         # центр смуги Режиму А
    row_B = 220         # центр смуги Режиму Б

    bar_x0 = 180        # початок смуги (після підписів)
    total_ticks = 70    # "максимум" шкали в тактах (Режим Б: ~60 тактів)
    px_per_tick = 6.0   # пікселів на такт

    def tick_to_px(ticks):
        return bar_x0 + ticks * px_per_tick

    # ── Вісь (горизонтальна, такти) ─────────────────────────────────────────
    axis_y = row_B + bar_h // 2 + 35
    frags.append(arrow(bar_x0, axis_y, tick_to_px(total_ticks + 2), axis_y, color=INK, sw=1.8))
    frags.append(text(tick_to_px(total_ticks + 3), axis_y + 4, "Такти", size=11, color=INK, anchor="start"))

    for t in [0, 10, 20, 30, 40, 50, 60]:
        xp = tick_to_px(t)
        frags.append(line(xp, axis_y - 5, xp, axis_y + 5, color=INK, sw=1.2))
        frags.append(text(xp, axis_y + 17, str(t), size=9, color=MUTED, anchor="middle"))

    # ── Режим А: щільний цикл ≈ 4–8 тактів ──────────────────────────────────
    tA = 6   # 6 тактів (load + store + dec/cmp + branch)
    frags.append(text(bar_x0 - 12, row_A + 5,
                      "Режим А\nщільний цикл:", size=11, color=NEG, anchor="end", bold=True))

    # Смуга "load+store+лічильник"
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="5" '
                 'fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                     bar_x0, row_A - bar_h // 2,
                     tick_to_px(tA) - bar_x0, bar_h,
                     "#eaf0fd", NEG))
    frags.append(text((bar_x0 + tick_to_px(tA)) / 2, row_A + 5,
                      "load + store + лічильник\n≈ 4–8 тактів",
                      size=10, color=NEG, anchor="middle", bold=True))

    # Підпис-мітка c_A
    frags.append(line(bar_x0, row_A - bar_h // 2 - 12, tick_to_px(tA), row_A - bar_h // 2 - 12,
                      color=NEG, sw=1.2))
    frags.append(line(bar_x0, row_A - bar_h // 2 - 16, bar_x0, row_A - bar_h // 2 - 8, color=NEG, sw=1.2))
    frags.append(line(tick_to_px(tA), row_A - bar_h // 2 - 16, tick_to_px(tA), row_A - bar_h // 2 - 8,
                      color=NEG, sw=1.2))
    frags.append(text((bar_x0 + tick_to_px(tA)) / 2, row_A - bar_h // 2 - 18,
                      "c(копія) ≈ 6 тактів", size=9, color=NEG, anchor="middle"))

    # ── Режим Б: переривання на елемент ≈ 60 тактів ─────────────────────────
    tB_copy = 6    # саме копіювання (той самий код)
    tB_isr  = 54   # вхід + вихід ISR (збереження/відновлення контексту)
    tB_total = tB_copy + tB_isr   # 60

    frags.append(text(bar_x0 - 12, row_B + 5,
                      "Режим Б\nпереривання\nна елемент:", size=11, color=POS, anchor="end", bold=True))

    # Сегмент "власне копіювання"
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="0" '
                 'fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                     bar_x0, row_B - bar_h // 2,
                     tick_to_px(tB_copy) - bar_x0, bar_h,
                     "#eaf0fd", NEG))
    # (підпис лише стрілкою — надто вузько)

    # Сегмент "вхід+вихід ISR"
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="0" '
                 'fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                     tick_to_px(tB_copy), row_B - bar_h // 2,
                     tick_to_px(tB_total) - tick_to_px(tB_copy), bar_h,
                     "#fdecea", POS))
    mid_isr = (tick_to_px(tB_copy) + tick_to_px(tB_total)) / 2
    frags.append(text(mid_isr, row_B - 6,
                      "вхід + вихід ISR: збереження/відновлення контексту",
                      size=10, color=POS, anchor="middle", bold=True))
    frags.append(text(mid_isr, row_B + 12,
                      "(§4.5.2 / §4.5.7m) — десятки тактів ЩОРАЗУ",
                      size=9, color=POS, anchor="middle"))

    # Стрілка "цей сегмент платиться ЩОРАЗУ"
    arrow_y = row_B + bar_h // 2 + 14
    frags.append(arrow(mid_isr, row_B + bar_h // 2, mid_isr, arrow_y + 16, color=POS, sw=1.8))
    tb_arr, _, _ = textbox(mid_isr + 100, arrow_y + 26,
                            "цей накладний сегмент\nплатиться за КОЖЕН елемент\n→ стеля байтрейту падає в ~15 разів",
                            size=10, fill="#fdecea", stroke=POS)
    frags.append(tb_arr)
    frags.append(line(mid_isr, arrow_y + 16, mid_isr + 100 - 55, arrow_y + 26, color=POS, sw=1.0, dash="3,3"))

    # Підпис-мітка c_B
    frags.append(line(bar_x0, row_B - bar_h // 2 - 12, tick_to_px(tB_total), row_B - bar_h // 2 - 12,
                      color=POS, sw=1.2))
    frags.append(line(bar_x0, row_B - bar_h // 2 - 16, bar_x0, row_B - bar_h // 2 - 8, color=POS, sw=1.2))
    frags.append(line(tick_to_px(tB_total), row_B - bar_h // 2 - 16,
                      tick_to_px(tB_total), row_B - bar_h // 2 - 8, color=POS, sw=1.2))
    frags.append(text((bar_x0 + tick_to_px(tB_total)) / 2, row_B - bar_h // 2 - 18,
                      "c(ISR) ≈ 60 тактів — у ~10× більше!", size=9, color=POS, anchor="middle"))

    # ── Мораль внизу ─────────────────────────────────────────────────────────
    tb_moral, _, _ = textbox(W // 2, H - 24,
                              "Вихід: складай у буфер і бери пачкою — або зніми перекладання з ядра (DMA, §4.9.2)",
                              size=10, fill=FILL, stroke=MUTED, color=MUTED)
    frags.append(tb_moral)

    render(os.path.join(OUT, "fig-09-1m-2-isr-cost.svg"), W, H, *frags,
           title="Рис. 4.9.1m.2. Ціна одного перенесення: щільний цикл vs переривання на елемент")


if __name__ == "__main__":
    fig1_ceiling()
    print("OK: img/fig-09-1m-1-ceiling.svg")
    fig2_isr_cost()
    print("OK: img/fig-09-1m-2-isr-cost.svg")
