# -*- coding: utf-8 -*-
"""
Фігури для вставки 🧮 «Спектр ШІМ: чому «середнє» працює і звідки береться писк»
(математична вставка до теми §4.7.1 «ШІМ: „вдавати" аналог цифровою ніжкою»).

fig-25-1m-1-pwm-spectrum.svg     → Рис. 4.7.1m.1
fig-25-1m-2-harmonics-vs-duty.svg → Рис. 4.7.1m.2

Імпортує спільний kit; примітиви з svgkit — НЕ переписуються тут.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── локальні кольори ──────────────────────────────────────────────────────────
RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
GREY   = "#8a8a8a"
LRED   = "#fbecec"
LBLUE  = "#e9eefb"
LGRN   = "#eef6ef"
LAMB   = "#fff6e0"
GOLD   = "#caa24a"
FAINT  = "#e4e4e4"
ORANGE = "#e07b00"
LORANGE = "#fff3e0"
PURPLE  = "#7c3aed"
LPURPLE = "#f5f0ff"


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.1m.1 — Амплітудний спектр ШІМ: DC + гребінка гармонік
# fig-25-1m-1-pwm-spectrum.svg
# ═══════════════════════════════════════════════════════════════════════════════
def fig_1m1_pwm_spectrum():
    W, H = 760, 400
    path = os.path.join(OUT, "fig-25-1m-1-pwm-spectrum.svg")

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Амплітудний спектр ШІМ: DC-лінія + гребінка гармонік",
                      size=15, color=INK, anchor="middle", bold=True))

    # ── Параметри осей ────────────────────────────────────────────────────────
    ox = 70       # початок осі X
    oy = 310      # нульова лінія Y (вісь X)
    aw = 620      # довжина осі X
    ah = 230      # висота осі Y (від oy вгору)

    # вісь X
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    # стрілка осі X
    frags.append(f'<line x1="{ox + aw - 1:.1f}" y1="{oy:.1f}" x2="{ox + aw + 14:.1f}" y2="{oy:.1f}" '
                 f'stroke="{INK}" stroke-width="1.8" marker-end="url(#arrow)"/>')

    # вісь Y
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    frags.append(f'<line x1="{ox:.1f}" y1="{oy - ah + 1:.1f}" x2="{ox:.1f}" y2="{oy - ah - 14:.1f}" '
                 f'stroke="{INK}" stroke-width="1.8" marker-end="url(#arrow)"/>')

    # підпис осей
    frags.append(text(ox + aw + 22, oy + 4, "f", size=14, color=INK, anchor="middle", italic=True))
    frags.append(text(ox - 12, oy - ah - 18, "A", size=14, color=INK, anchor="middle", italic=True))

    # ── Мітки частот на осі X ─────────────────────────────────────────────────
    # Відстані від ox: 0 Гц, f, 2f, 3f, 4f, 5f, 6f
    freq_labels = ["0", "f", "2f", "3f", "4f", "5f", "6f"]
    freq_xs = [ox + 0, ox + 90, ox + 180, ox + 270, ox + 360, ox + 450, ox + 540]

    for lbl, fx in zip(freq_labels, freq_xs):
        frags.append(line(fx, oy - 5, fx, oy + 5, color=GREY, sw=1.2))
        frags.append(text(fx, oy + 18, lbl, size=12, color=INK, anchor="middle"))

    # ── Шпаруватість d=0.6, U=1 → a0 = 0.6 → амплітуди гармонік ────────────
    d = 0.6
    U = 1.0
    max_bar_h = ah - 30  # максимальна висота стовпчика (DC)

    # DC-стовпчик (a0 = d·U)
    dc_amp = d * U          # 0.6
    dc_h = dc_amp * max_bar_h  # висота відносно max
    dc_x = freq_xs[0]
    bar_w = 28

    # DC-лінія — виразна, в кольорі GREEN, заповнена
    frags.append(
        f'<rect x="{dc_x - bar_w / 2:.1f}" y="{oy - dc_h:.1f}" '
        f'width="{bar_w:.1f}" height="{dc_h:.1f}" '
        f'fill="{GREEN}" fill-opacity="0.85" stroke="{GREEN}" stroke-width="1.5"/>'
    )
    # підпис DC-лінії: d·U
    frags.append(text(dc_x, oy - dc_h - 10, "d·U", size=12, color=GREEN, anchor="middle", bold=True))
    frags.append(text(dc_x, oy - dc_h - 24, "= середнє", size=10, color=GREEN, anchor="middle"))

    # горизонтальна пунктирна лінія від вершини DC-стовпчика
    frags.append(line(dc_x + bar_w / 2, oy - dc_h, ox + aw - 30, oy - dc_h,
                      color=GREEN, sw=1.0, dash="5,5"))

    # Гармоніки n=1..6: A_n = (2U/π·n)·|sin(π·n·d)|
    harmonic_colors = [RED, RED, RED, RED, RED, RED]
    harmonic_xs = freq_xs[1:]  # f,2f,3f,4f,5f,6f

    for i, (n, fx) in enumerate(zip(range(1, 7), harmonic_xs)):
        amp_n = (2 * U / (math.pi * n)) * abs(math.sin(math.pi * n * d))
        # нормуємо відносно максимально можливої (n=1, d=0.5 → 2U/π ≈ 0.637)
        norm_max = 2 * U / math.pi
        bar_h_n = (amp_n / norm_max) * max_bar_h

        if bar_h_n > 2:
            frags.append(
                f'<rect x="{fx - bar_w / 2:.1f}" y="{oy - bar_h_n:.1f}" '
                f'width="{bar_w:.1f}" height="{bar_h_n:.1f}" '
                f'fill="{RED}" fill-opacity="{0.8 - i * 0.07:.2f}" '
                f'stroke="{RED}" stroke-width="1.5"/>'
            )
            # мітка амплітуди (лише n=1 і n=3 щоб не товпитись)
            if n <= 3:
                lbl_amp = f"A₁" if n == 1 else (f"A₂" if n == 2 else f"A₃")
                frags.append(text(fx, oy - bar_h_n - 9, lbl_amp, size=11, color=RED, anchor="middle", bold=(n == 1)))

    # ── Підпис спаду ~1/n ────────────────────────────────────────────────────
    frags.append(text(freq_xs[3], oy - 85, "спад ~1/n", size=11, color=RED, anchor="middle", italic=True))
    # крива-обвідна (пунктир по вершинах гармонік)
    pts_obv = []
    for n in range(1, 7):
        amp_n = (2 * U / (math.pi * n)) * abs(math.sin(math.pi * n * d))
        norm_max = 2 * U / math.pi
        bar_h_n = (amp_n / norm_max) * max_bar_h
        pts_obv.append((freq_xs[n], oy - bar_h_n))

    pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_obv)
    frags.append(f'<polyline points="{pts_str}" fill="none" stroke="{RED}" '
                 f'stroke-width="1.2" stroke-dasharray="4,3" opacity="0.5"/>')

    # ── Стрілка «підняти f → гребінка їде вправо» ───────────────────────────
    arrow_y = oy - 50
    ax1 = freq_xs[1] + 20
    ax2 = freq_xs[2] + 50
    frags.append(
        f'<line x1="{ax1:.1f}" y1="{arrow_y:.1f}" x2="{ax2:.1f}" y2="{arrow_y:.1f}" '
        f'stroke="{ORANGE}" stroke-width="2.0" marker-end="url(#arrow)"/>'
    )
    note_box, _, _ = textbox((ax1 + ax2) / 2, arrow_y - 30,
                              "↑ f ШІМ → гребінка\nіде вправо, далі\nвід смуги навантаження",
                              size=9, fill=LORANGE, stroke=ORANGE, color=ORANGE, pad=6)
    frags.append(note_box)

    # ── Рамка-підсумок внизу ─────────────────────────────────────────────────
    summary, _, _ = textbox(W / 2, H - 28,
                             "DC (0 Гц) = d·U = «середнє» — проходить через інерційне навантаження.\n"
                             "Гармоніки на f, 2f, 3f… — навантаження їх гасить. Між лініями — порожньо.",
                             size=10, fill=LGRN, stroke=GREEN, color=INK, pad=8)
    frags.append(summary)

    # ── defs для стрілки (потрібно для marker-end) ────────────────────────────
    defs = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % INK)

    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>' % (W, H, FONT, W, H, BG))

    import io
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(head + "\n" + defs + "\n" + "\n".join(frags) + "\n</svg>")

    print("wrote", os.path.basename(path))


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.1m.2 — Амплітуди гармонік залежать від шпаруватості (2 панелі)
# fig-25-1m-2-harmonics-vs-duty.svg
# ═══════════════════════════════════════════════════════════════════════════════
def fig_1m2_harmonics_vs_duty():
    W, H = 820, 400
    path = os.path.join(OUT, "fig-25-1m-2-harmonics-vs-duty.svg")

    frags = []

    U = 1.0

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Амплітуди гармонік і шпаруватість: два погляди",
                      size=15, color=INK, anchor="middle", bold=True))

    # вертикальний роздільник
    frags.append(line(W / 2, 44, W / 2, H - 44, color=FAINT, sw=1.5))

    # ══════════════════════════════════════════════════════════════════════════
    # ЛІВА ПАНЕЛЬ: бар-чарт A₁…A₅ для двох шпаруватостей
    # ══════════════════════════════════════════════════════════════════════════
    lox = 55     # початок лівої осі X
    loy = 310    # нульова лінія Y
    lw  = 330    # ширина лівої панелі (до W/2)
    lah = 220    # висота осі Y

    frags.append(text(lox + lw / 2, 50, "Стовпчики A₁…A₅ для d=50% і d=25%",
                      size=12, color=INK, anchor="middle", bold=True))

    # осі лівої панелі
    frags.append(line(lox, loy, lox + lw - 10, loy, color=INK, sw=1.5))
    frags.append(line(lox, loy, lox, loy - lah, color=INK, sw=1.5))

    # підпис осей
    frags.append(text(lox - 10, loy - lah - 12, "A", size=13, color=INK, anchor="middle", italic=True))
    frags.append(text(lox + lw - 4, loy + 14, "n", size=13, color=INK, anchor="middle", italic=True))

    # нормування: A_max = (2U/π) (при d=0.5, n=1)
    norm_max = 2 * U / math.pi

    duties = [0.5, 0.25]
    d_colors = [BLUE, RED]
    d_labels = ["d=50%", "d=25%"]
    group_xs = [lox + 44, lox + 108, lox + 172, lox + 236, lox + 300]  # позиції груп (n=1..5)
    n_labels = ["1·f", "2·f", "3·f", "4·f", "5·f"]
    bar_w_each = 18
    bar_gap = 4

    for gi, (gx, nl) in enumerate(zip(group_xs, n_labels)):
        n = gi + 1
        # мітка n
        frags.append(text(gx, loy + 16, nl, size=10, color=GREY, anchor="middle"))

        for di, (d, col) in enumerate(zip(duties, d_colors)):
            amp = (2 * U / (math.pi * n)) * abs(math.sin(math.pi * n * d))
            bh = (amp / norm_max) * (lah - 20)
            # зміщення: лівий бар → di=0 зліва, правий → di=1 справа
            bx = gx - bar_w_each - bar_gap / 2 + di * (bar_w_each + bar_gap)
            if bh > 1.5:
                frags.append(
                    f'<rect x="{bx:.1f}" y="{loy - bh:.1f}" '
                    f'width="{bar_w_each:.1f}" height="{bh:.1f}" '
                    f'fill="{col}" fill-opacity="0.75" stroke="{col}" stroke-width="1.2"/>'
                )
            else:
                # нульова або майже нульова — маленька мітка
                frags.append(text(bx + bar_w_each / 2, loy - 6, "≈0",
                                  size=8, color=col, anchor="middle"))

    # легенда лівої панелі
    leg_x = lox + 20
    leg_y = loy - lah + 20
    for di, (col, lbl) in enumerate(zip(d_colors, d_labels)):
        frags.append(
            f'<rect x="{leg_x:.1f}" y="{leg_y + di * 20:.1f}" '
            f'width="14" height="12" fill="{col}" fill-opacity="0.75" stroke="{col}" stroke-width="1"/>'
        )
        frags.append(text(leg_x + 20, leg_y + di * 20 + 10, lbl, size=11, color=col, anchor="start"))

    # підпис-висновок лівої панелі
    note_l, _, _ = textbox(lox + lw / 2, loy + 58,
                            "d=50%: парні гармоніки ≈0\n(меандр — лише 1·f, 3·f, 5·f…)\nСпад ~1/n: A₁ найбільша",
                            size=10, fill=LBLUE, stroke=BLUE, color=INK, pad=7)
    frags.append(note_l)

    # ══════════════════════════════════════════════════════════════════════════
    # ПРАВА ПАНЕЛЬ: крива A₁(d) = (2U/π)·sin(πd)
    # ══════════════════════════════════════════════════════════════════════════
    rox = W / 2 + 30   # початок правої осі X
    roy = 310           # нульова лінія Y
    rw  = 340           # ширина правої панелі
    rah = 220           # висота осі Y

    frags.append(text(rox + rw / 2, 50, "A₁(d) = (2U/π)·sin(πd) — перша (найбільша) гармоніка",
                      size=12, color=INK, anchor="middle", bold=True))

    # осі
    frags.append(line(rox, roy, rox + rw, roy, color=INK, sw=1.5))
    frags.append(line(rox, roy, rox, roy - rah, color=INK, sw=1.5))

    # підпис осей
    frags.append(text(rox - 10, roy - rah - 12, "A₁", size=13, color=INK, anchor="middle", bold=True, italic=True))
    frags.append(text(rox + rw + 10, roy + 4, "d", size=13, color=INK, anchor="middle", italic=True))

    # мітки осі X: 0, 0.25, 0.5, 0.75, 1.0
    d_ticks = [0, 0.25, 0.5, 0.75, 1.0]
    d_tick_lbls = ["0", "0.25", "0.5", "0.75", "1"]
    for dtk, dlbl in zip(d_ticks, d_tick_lbls):
        fx = rox + dtk * rw
        frags.append(line(fx, roy - 4, fx, roy + 4, color=GREY, sw=1.2))
        frags.append(text(fx, roy + 16, dlbl, size=10, color=GREY, anchor="middle"))

    # крива A₁(d)
    curve_pts = []
    steps = 80
    for i in range(steps + 1):
        d_val = i / steps
        a1 = (2 * U / math.pi) * math.sin(math.pi * d_val)
        cx_pt = rox + d_val * rw
        cy_pt = roy - (a1 / norm_max) * (rah - 20)
        curve_pts.append((cx_pt, cy_pt))

    pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in curve_pts)
    frags.append(f'<polyline points="{pts_str}" fill="none" stroke="{RED}" '
                 f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')

    # заповнення під кривою (область)
    area_pts = [(rox, roy)] + curve_pts + [(rox + rw, roy)]
    area_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in area_pts)
    frags.append(f'<polygon points="{area_str}" fill="{RED}" fill-opacity="0.1" stroke="none"/>')

    # горб на d=0.5 — маркер
    d_max = 0.5
    a1_max = (2 * U / math.pi) * math.sin(math.pi * d_max)
    mx = rox + d_max * rw
    my = roy - (a1_max / norm_max) * (rah - 20)
    frags.append(circle(mx, my, 5, fill=RED, stroke=RED, sw=1.5))

    # підпис горба
    note_top, _, _ = textbox(mx + 65, my - 20,
                              "максимум\nна d=50%",
                              size=10, fill=LRED, stroke=RED, color=RED, pad=6)
    frags.append(note_top)
    frags.append(line(mx + 5, my, mx + 65 - 35, my - 16, color=RED, sw=1.0, dash="4,3"))

    # мітка горизонтальна пунктирна до осі Y
    a1_norm_h = (a1_max / norm_max) * (rah - 20)
    frags.append(line(rox, roy - a1_norm_h, mx, roy - a1_norm_h, color=GREY, sw=1.0, dash="4,3"))
    frags.append(text(rox - 6, roy - a1_norm_h + 4, "2U/π", size=10, color=RED, anchor="end"))

    # нулі на краях — позначки
    frags.append(text(rox, roy - 16, "0", size=10, color=GREY, anchor="middle"))
    frags.append(text(rox + rw, roy - 16, "0", size=10, color=GREY, anchor="middle"))

    # підпис-висновок правої панелі
    note_r, _, _ = textbox(rox + rw / 2, roy + 58,
                            "Найгірші брижі і писк — біля d=50%\n(A₁ максимальна).\nНа d→0 і d→1 сигнал майже сталий — брижів мало.",
                            size=10, fill=LRED, stroke=RED, color=INK, pad=7)
    frags.append(note_r)

    # ── defs + render ─────────────────────────────────────────────────────────
    defs = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % INK)

    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>' % (W, H, FONT, W, H, BG))

    import io
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(head + "\n" + defs + "\n" + "\n".join(frags) + "\n</svg>")

    print("wrote", os.path.basename(path))


# ─── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_1m1_pwm_spectrum()
    fig_1m2_harmonics_vs_duty()
    print("Done.")
