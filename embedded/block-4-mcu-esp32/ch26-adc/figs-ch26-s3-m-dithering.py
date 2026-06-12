# -*- coding: utf-8 -*-
"""
Фігури до математичної вставки «Дизеринг і передискретизація» (ch26-s3-m-dithering.md).
Дві фігури:
  fig-26-3m-1-dither.svg  — механізм дизерингу (без шуму / з шумом)
  fig-26-3m-2-sqrtn.svg   — крива σ/√N і сходи ENOB

Залежності: тільки стандартна бібліотека Python + спільний svgkit.
Запуск: python figs-ch26-s3-m-dithering.py
Вивід: ./img/
"""

import sys, os, math, random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

random.seed(42)


def save_svg(name, w, h, *frags, title=None):
    path = os.path.join(OUT, name)
    render(path, w, h, *frags, title=title)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.3m.1 — Механізм дизерингу
# ═══════════════════════════════════════════════════════════════════════════════

def fig_m83_1_dither():
    """
    Дві панелі.
    ЛІВА «без шуму»: вхід застряг на 0.3 LSB над щаблем k — всі відліки = k.
    ПРАВА «з дизерингом ~1 LSB»: частина відліків стрибає на k+1;
      гістограма ≈70 % / 30 % → середнє ≈ k+0.30.
    """
    W, H = 820, 440
    frags = []

    # ── спільні константи ───────────────────────────────────────────────────
    STEP = 90          # піксель = 1 LSB
    k_y  = 200         # y-координата рівня k (верхня межа щабля k)
    k1_y = k_y - STEP  # рівень k+1

    # ── ЛІВА ПАНЕЛЬ (без шуму) ──────────────────────────────────────────────
    # рамка панелі
    frags.append(rect(20, 30, 370, 400, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=10))
    panel_title_L, _, _ = textbox(205, 52, "Без шуму (ідеальний АЦП)", size=13, bold=True,
                                   fill=FILL, stroke=INK)
    frags.append(panel_title_L)

    # вертикальна вісь (рівні k та k+1)
    ax_x = 80
    frags.append(line(ax_x, k1_y - 30, ax_x, k_y + STEP + 10, color=INK, sw=1.6))
    # рівні-сходинки
    step_w = 220
    # щабель k+1 (верхній)
    frags.append(line(ax_x, k1_y, ax_x + step_w, k1_y, color=INK, sw=2.0))
    # щабель k (нижній)
    frags.append(line(ax_x, k_y, ax_x + step_w, k_y, color=INK, sw=2.0))
    # вертикальна лінія між щаблями
    frags.append(line(ax_x + step_w, k_y, ax_x + step_w, k1_y, color=INK, sw=2.0))

    # підписи рівнів
    frags.append(text(ax_x - 8, k1_y + 5, "k+1", size=12, color=INK, anchor="end"))
    frags.append(text(ax_x - 8, k_y + 5, "k", size=12, color=INK, anchor="end"))

    # вхідний сигнал: горизонтальна лінія на 0.3 LSB над щаблем k
    inp_y = k_y - int(STEP * 0.30)   # 0.30 LSB
    inp_x0, inp_x1 = ax_x + 10, ax_x + step_w - 10
    frags.append(line(inp_x0, inp_y, inp_x1, inp_y, color=POS, sw=2.4, dash="6,3"))
    # підпис входу
    tb_inp, _, _ = textbox(inp_x0 + (inp_x1 - inp_x0) // 2, inp_y - 14,
                            "вхід: +0.30 LSB", size=11, fill="#fff5f5", stroke=POS)
    frags.append(tb_inp)

    # стрілки відліків (5 штук, усі падають на k)
    arrow_xs = [110, 145, 180, 215, 250]
    for xp_a in arrow_xs:
        frags.append(arrow(xp_a, inp_y, xp_a, k_y + 6, color=NEG, sw=1.8))
    # крапки на рівні k
    for xp_a in arrow_xs:
        frags.append(circle(xp_a, k_y + 4, 5, fill=NEG, stroke=NEG, sw=1))

    # підпис-висновок лівої панелі
    tb_res_L, _, _ = textbox(205, 360,
                              "середнє = k\nдробова 0.30 LSB — втрачена",
                              size=12, fill="#eaf0fd", stroke=NEG)
    frags.append(tb_res_L)

    # ── ПРАВА ПАНЕЛЬ (з дизерингом) ─────────────────────────────────────────
    ox_R = 430
    frags.append(rect(ox_R - 10, 30, 375, 400, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=10))
    panel_title_R, _, _ = textbox(ox_R + 175, 52, "З дизерингом (~1 LSB)", size=13, bold=True,
                                   fill=FILL, stroke=INK)
    frags.append(panel_title_R)

    # осі та щаблі (так само)
    ax_xR = ox_R + 60
    frags.append(line(ax_xR, k1_y - 30, ax_xR, k_y + STEP + 10, color=INK, sw=1.6))
    frags.append(line(ax_xR, k1_y, ax_xR + step_w, k1_y, color=INK, sw=2.0))
    frags.append(line(ax_xR, k_y, ax_xR + step_w, k_y, color=INK, sw=2.0))
    frags.append(line(ax_xR + step_w, k_y, ax_xR + step_w, k1_y, color=INK, sw=2.0))
    frags.append(text(ax_xR - 8, k1_y + 5, "k+1", size=12, color=INK, anchor="end"))
    frags.append(text(ax_xR - 8, k_y + 5, "k", size=12, color=INK, anchor="end"))

    # вхід (та сама лінія)
    frags.append(line(ax_xR + 10, inp_y, ax_xR + step_w - 10, inp_y,
                      color=POS, sw=2.4, dash="6,3"))
    tb_inp2, _, _ = textbox(ax_xR + (step_w) // 2, inp_y - 14,
                             "вхід: +0.30 LSB", size=11, fill="#fff5f5", stroke=POS)
    frags.append(tb_inp2)

    # хмарка точок (відліки з шумом ~1 LSB): 20 точок
    scatter_xs = [110, 130, 150, 168, 188, 205, 222, 240, 258, 275,
                  118, 140, 160, 178, 196, 214, 232, 248, 265, 282]
    n_k1 = 6    # 30 % підстрибують на k+1
    for i, xp_s in enumerate(scatter_xs):
        noise = (random.random() - 0.5) * STEP * 0.8
        yp_s = inp_y + noise
        frags.append(circle(ax_xR + xp_s - ax_x, yp_s, 3.5,
                             fill=MUTED, stroke=MUTED, sw=0.8))

    # стрілки: 30 % на k+1, 70 % на k
    arr_xs_R = [ax_xR + 120, ax_xR + 148, ax_xR + 176, ax_xR + 204,
                ax_xR + 232, ax_xR + 258]
    for idx, xp_a in enumerate(arr_xs_R):
        if idx < 2:   # 2/6 ≈ 33 % — стрибок на k+1
            tgt_y = k1_y + 4
            col_a = POS
        else:
            tgt_y = k_y + 4
            col_a = NEG
        frags.append(arrow(xp_a, inp_y, xp_a, tgt_y + 6, color=col_a, sw=1.8))
        frags.append(circle(xp_a, tgt_y + 4, 5, fill=col_a, stroke=col_a, sw=1))

    # міні-гістограма (стовпчики)
    bar_x0 = ax_xR + 295
    bar_w  = 28
    bar_max = 60   # максимальна висота стовпця
    # k: 70 %, k+1: 30 %
    for bar_lbl, bar_frac, bar_ybot, bar_col in [
        ("k",   0.70, k_y,  NEG),
        ("k+1", 0.30, k1_y, POS),
    ]:
        bh = int(bar_max * bar_frac)
        bx = bar_x0
        by = bar_ybot - bh
        frags.append(rect(bx, by, bar_w, bh, fill=bar_col, stroke=bar_col, sw=0.8, rx=3))
        frags.append(text(bx + bar_w // 2, by - 8, "%d%%" % int(bar_frac * 100),
                          size=10, color=bar_col, anchor="middle", bold=True))
        frags.append(text(bx + bar_w // 2, bar_ybot + 14, bar_lbl,
                          size=10, color=INK, anchor="middle"))

    # підпис-висновок правої панелі
    tb_res_R, _, _ = textbox(ox_R + 175, 360,
                              "середнє ≈ k + 0.30\nпозицію відновлено!",
                              size=12, fill="#edfbf0", stroke=FIELD)
    frags.append(tb_res_R)

    # ── ключова фраза внизу ─────────────────────────────────────────────────
    tb_key, _, _ = textbox(W // 2, 420,
                            "Шум не псує — він голосує. Підпорогова інформація переходить у статистику серії.",
                            size=12, bold=True, fill=FILL, stroke=INK)
    frags.append(tb_key)

    save_svg("fig-26-3m-1-dither.svg", W, H, *frags)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.3m.2 — Крива σ/√N і сходи ефективних бітів
# ═══════════════════════════════════════════════════════════════════════════════

def fig_m83_2_sqrtn():
    """
    Дві криві на спільній логарифмічній осі N = 1, 4, 16, 64, 256.
    А (синя, спадна): σ_avg = σ/√N — відносний шум.
    Б (зелені сходи): ΔENOB = ½·log₂N — додані ефективні біти.
    Пунктирна стеля — поріг систематичної похибки.
    """
    W, H = 780, 430
    frags = []

    # ── Осьові параметри ────────────────────────────────────────────────────
    ox, oy = 80, 370     # нижній-лівий кут
    aw = 600             # ширина осі X (логарифмічна)
    ah = 290             # висота осі Y

    N_vals = [1, 4, 16, 64, 256]
    log_N  = [math.log2(n) for n in N_vals]   # 0, 2, 4, 6, 8

    def xp(n):
        """x-позиція для N (лог-крок 0..8)"""
        return ox + math.log2(n) / 8 * aw

    # σ/√N нормовано: при N=1 → 1.0, при N=256 → 1/16
    sigma_at = {n: 1.0 / math.sqrt(n) for n in N_vals}
    # ENOB при N=1 → 0 біт, N=4 → 1, N=16 → 2, N=64 → 3, N=256 → 4
    enob_at  = {n: 0.5 * math.log2(n) for n in N_vals}

    # нормуємо sigma (1.0 → висота ah), ENOB (4 → висота ah)
    def yp_sigma(s):
        return oy - s * ah

    def yp_enob(e):
        return oy - (e / 4) * ah

    # ── Сітка ───────────────────────────────────────────────────────────────
    for n in N_vals:
        xi = xp(n)
        frags.append(line(xi, oy, xi, oy - ah - 10, color=MUTED, sw=0.8, dash="3,4"))

    for ei in [0, 1, 2, 3, 4]:
        yi = yp_enob(ei)
        frags.append(line(ox, yi, ox + aw, yi, color=MUTED, sw=0.8, dash="3,4"))

    # ── Вісь X ──────────────────────────────────────────────────────────────
    frags.append(line(ox, oy, ox + aw + 20, oy, color=INK, sw=1.8))
    frags.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.8))

    for n in N_vals:
        xi = xp(n)
        frags.append(line(xi, oy - 5, xi, oy + 5, color=INK, sw=1.4))
        frags.append(text(xi, oy + 18, str(n), size=12, color=INK, anchor="middle"))

    frags.append(text(ox + aw + 28, oy + 4, "N", size=14, color=INK, anchor="start",
                      italic=True))
    frags.append(text(ox + aw / 2, oy + 34, "кількість відліків для усереднення (OSR)",
                      size=11, color=MUTED, anchor="middle"))

    # ── Вісь Y (ліва: відносний шум σ/σ₀) ─────────────────────────────────
    frags.append(line(ox, oy, ox, oy - ah - 20, color=INK, sw=1.8))
    frags.append(arrow(ox, oy - ah - 5, ox, oy - ah - 20, color=INK, sw=1.8))

    sigma_ticks = {1.0: "1.0 (σ₀)", 0.5: "0.5", 0.25: "0.25", 0.125: "0.125", 0.0625: "0.0625"}
    for sv, slbl in sigma_ticks.items():
        yi = yp_sigma(sv)
        if yi > oy - ah - 5:
            frags.append(line(ox - 5, yi, ox + 5, yi, color=INK, sw=1.4))
            frags.append(text(ox - 8, yi + 4, slbl, size=10, color=NEG, anchor="end"))

    frags.append(text(ox - 50, oy - ah / 2, "σ/σ₀\n(шум)",
                      size=11, color=NEG, anchor="middle", bold=True))

    # ── Вісь Y (права: ENOB) ───────────────────────────────────────────────
    ax_right = ox + aw
    frags.append(line(ax_right, oy, ax_right, oy - ah - 20, color=INK, sw=1.8))
    frags.append(arrow(ax_right, oy - ah - 5, ax_right, oy - ah - 20, color=INK, sw=1.8))

    for ei in [0, 1, 2, 3, 4]:
        yi = yp_enob(ei)
        frags.append(line(ax_right - 5, yi, ax_right + 5, yi, color=INK, sw=1.4))
        frags.append(text(ax_right + 8, yi + 4, "+%d біт" % ei,
                          size=10, color=FIELD, anchor="start"))

    frags.append(text(ax_right + 55, oy - ah / 2, "ΔENOB\n(нові біти)",
                      size=11, color=FIELD, anchor="middle", bold=True))

    # ── Крива А: σ_avg (синя, спадна) ──────────────────────────────────────
    # Будуємо рівномірно по логарифмічній осі
    sigma_pts = []
    n_steps = 80
    for i in range(n_steps + 1):
        n = 2 ** (8 * i / n_steps)   # 1..256 лог
        s = 1.0 / math.sqrt(n)
        xi = ox + (8 * i / n_steps) / 8 * aw
        yi = yp_sigma(s)
        if yi >= oy - ah - 5:
            sigma_pts.append((xi, yi))

    pts_str = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in sigma_pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" '
                 'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>'
                 % (pts_str, NEG))

    # позначки /2, /4, /8, /16 на кривій
    divisors = {4: "/2", 16: "/4", 64: "/8", 256: "/16"}
    for n, lbl in divisors.items():
        xi = xp(n)
        yi = yp_sigma(sigma_at[n])
        frags.append(circle(xi, yi, 5, fill=NEG, stroke=NEG, sw=1))
        frags.append(text(xi + 10, yi - 8, lbl, size=11, color=NEG, anchor="start", bold=True))

    # ── Крива Б: ENOB (зелені сходи) ───────────────────────────────────────
    # Сходинки: від N_i до N_{i+1} на рівні enob(N_i), потім вертикаль
    for i in range(len(N_vals) - 1):
        n0, n1 = N_vals[i], N_vals[i + 1]
        x0, x1 = xp(n0), xp(n1)
        y0 = yp_enob(enob_at[n0])
        y1 = yp_enob(enob_at[n1])
        # горизонтальна сходинка
        frags.append(line(x0, y0, x1, y0, color=FIELD, sw=2.6))
        # вертикальна підйом
        frags.append(line(x1, y0, x1, y1, color=FIELD, sw=2.6))
        # підпис +1 біт на вертикалі
        frags.append(text(x1 + 6, (y0 + y1) / 2 + 4, "+1 біт",
                          size=10, color=FIELD, anchor="start", bold=True))

    # остання горизонтальна до кінця осі
    x_last = xp(N_vals[-1])
    y_last = yp_enob(enob_at[N_vals[-1]])
    frags.append(line(x_last, y_last, ox + aw, y_last, color=FIELD, sw=2.6))

    # крапки на сходах
    for n in N_vals:
        xi = xp(n)
        yi = yp_enob(enob_at[n])
        frags.append(circle(xi, yi, 5, fill=FIELD, stroke=FIELD, sw=1))

    # ── Пунктирна стеля (систематична похибка) ─────────────────────────────
    # Проведемо на рівні σ = 0.10 (умовний поріг)
    ceil_s = 0.10
    yi_ceil = yp_sigma(ceil_s)
    frags.append(line(ox, yi_ceil, ox + aw, yi_ceil,
                      color=POS, sw=2.0, dash="8,5"))
    tb_ceil, _, _ = textbox(ox + 420, yi_ceil - 18,
                             "поріг систематичної похибки\n(зсув / нелінійність §4.8.6)",
                             size=10, fill="#fff5f5", stroke=POS)
    frags.append(tb_ceil)

    # маленька стрілка "крива впирається"
    frags.append(text(ox + 20, yi_ceil - 8, "крива А впирається — нижче не йде",
                      size=10, color=POS, anchor="start"))

    # ── Пояснення — потрібен дизеринг ──────────────────────────────────────
    tb_need, _, _ = textbox(ox + 200, oy - ah - 18,
                             "потрібен дизеринг ≥ ~1 LSB",
                             size=11, bold=True, fill=FILL, stroke=INK)
    frags.append(tb_need)

    # ── Легенда ─────────────────────────────────────────────────────────────
    leg_x, leg_y = ox + 340, oy - ah + 10
    frags.append(rect(leg_x, leg_y, 210, 64, fill=BG, stroke=MUTED, sw=1.0, rx=6))
    frags.append(line(leg_x + 12, leg_y + 20, leg_x + 40, leg_y + 20, color=NEG, sw=2.5))
    frags.append(text(leg_x + 48, leg_y + 24, "σ/√N — відносний шум (ліва вісь)",
                      size=10, color=INK, anchor="start"))
    frags.append(line(leg_x + 12, leg_y + 44, leg_x + 40, leg_y + 44, color=FIELD, sw=2.5))
    frags.append(text(leg_x + 48, leg_y + 48, "ΔENOB — додані біти (права вісь)",
                      size=10, color=INK, anchor="start"))

    # ── Заголовок ────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 24, "Усереднення N відліків: σ/√N спадає, ENOB зростає",
                      size=16, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 43, "кожне ×4 за N додає рівно один ефективний біт; стеля — систематична похибка",
                      size=11, color=MUTED, anchor="middle"))

    save_svg("fig-26-3m-2-sqrtn.svg", W, H, *frags)


# ── Точка входу ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_m83_1_dither()
    fig_m83_2_sqrtn()
    print("done.")
