# -*- coding: utf-8 -*-
"""
Фігури для вставки ⚙️ «Гамма-корекція ШІМ» (до теми 4.7.5).
fig-25-5a-1-gamma-pipeline.svg  → Рис. 4.7.5.7
fig-25-5a-2-lut-steps.svg       → Рис. 4.7.5.8

Імпортує spільний kit; примітиви з svgkit — НЕ переписуються тут.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

GAMMA = 2.2
PWM_BITS = 12
MAX_DUTY = (1 << PWM_BITS) - 1   # 4095

# ── локальні кольори, узгоджені з палітрою figs.py розділу ──────────────────
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.5.7 — Конвеєр гамма-корекції
# ═════════════════════════════════════════════════════════════════════════════
def fig_gamma_pipeline():
    W, H = 960, 400
    path = os.path.join(OUT, "fig-25-5a-1-gamma-pipeline.svg")

    # ── блоки конвеєра ───────────────────────────────────────────────────────
    # Зони: INIT (жовта) і LOOP (зелена), розділені вертикальною пунктирною рискою
    # Блоки зліва направо:
    #   [level 0..255] → [powf / LUT-build] → [LUT 256 чисел] → [lut[level]] → [ledcWrite] → [LED]

    # координати блоків (cx, cy, label, sublabel)
    blocks = [
        (100, 200, "level", "0 … 255"),
        (270, 200, "powf(x/255,γ)·maxDuty", "рантайм-формула"),
        (470, 200, "gammaLUT[256]", "uint16_t, 512 байт"),
        (660, 200, "lut[level]", "O(1), без float"),
        (830, 200, "ledcWrite", "→ LEDC"),
    ]

    # зони
    zone_frags = []
    # INIT zone: x 30..580, y 90..310
    zone_frags.append(rect(30, 90, 560, 220, fill=LAMB, stroke=GOLD, sw=1.5, rx=14))
    zone_frags.append(text(310, 118, "INIT: один раз у setup() — float, повільно, але лише раз",
                           size=11, color="#7a5c00", anchor="middle", bold=True))
    # LOOP zone: x 600..930, y 90..310
    zone_frags.append(rect(600, 90, 330, 220, fill=LGRN, stroke=GREEN, sw=1.5, rx=14))
    zone_frags.append(text(765, 118, "LOOP: щокадру — тільки індексація",
                           size=11, color=GREEN, anchor="middle", bold=True))

    block_frags = []
    box_w_list = []
    for i, (cx, cy, lbl, sub) in enumerate(blocks):
        bw = max(130, len(lbl) * 9 + 20)
        bh = 60
        bx, by = cx - bw / 2, cy - bh / 2
        fill = LBLUE if i == 2 else FAINT
        stk = BLUE if i == 2 else LINE
        block_frags.append(rect(bx, by, bw, bh, fill=fill, stroke=stk, sw=2, rx=8))
        fs = fit_font(lbl, bw - 12, 13, bold=True)
        block_frags.append(text(cx, cy - 4, lbl, size=fs, color=INK, anchor="middle", bold=True))
        block_frags.append(text(cx, cy + 15, sub, size=10, color=GREY, anchor="middle"))
        box_w_list.append(bw)

    # стрілки між блоками
    arrow_frags = []
    centers_x = [b[0] for b in blocks]
    for i in range(len(centers_x) - 1):
        x1 = centers_x[i] + box_w_list[i] / 2
        x2 = centers_x[i + 1] - box_w_list[i + 1] / 2
        xm = (x1 + x2) / 2
        col = BLUE if i == 1 else LINE
        arrow_frags.append(line(x1, 200, x2 - 10, 200, color=col, sw=2))
        arrow_frags.append(
            f'<line x1="{x2-10:.1f}" y1="200" x2="{x2:.1f}" y2="200" '
            f'stroke="{col}" stroke-width="2.5" '
            f'marker-end="url(#arrow)"/>'
        )

    # підписи під/над стрілками
    arrow_labels = [
        (185, 180, "через цикл", "i=0..255", GREY),
        (370, 175, "duty = round(…)", "(x/255)^γ · 4095", BLUE),
        (565, 180, "lut[level]", "O(1)", GREEN),
        (745, 180, "uint16_t", "0 … 4095", GREY),
    ]
    al_frags = []
    for (ax, ay, t1, t2, col) in arrow_labels:
        al_frags.append(text(ax, ay, t1, size=9, color=col, anchor="middle", bold=True))
        al_frags.append(text(ax, ay + 13, t2, size=8.5, color=col, anchor="middle"))

    # LED-символ: кружечок з промінцями
    led_frags = []
    lcx, lcy, lr = 900, 200, 18
    led_frags.append(circle(lcx, lcy, lr, fill="#fffacc", stroke=GOLD, sw=2))
    led_frags.append(text(lcx, lcy + 5, "LED", size=10, color=INK, anchor="middle", bold=True))
    # 4 промінці
    for ang in [45, 0, -45, 90]:
        rad = math.radians(ang)
        x1 = lcx + (lr + 2) * math.cos(rad)
        y1 = lcy - (lr + 2) * math.sin(rad)
        x2 = lcx + (lr + 10) * math.cos(rad)
        y2 = lcy - (lr + 10) * math.sin(rad)
        led_frags.append(line(x1, y1, x2, y2, color=GOLD, sw=2))

    # підпис-легенда внизу
    legend = [
        (310, 335, "⟵ вартість powf сплачується наперед, лише під час ініціалізації", GREY),
        (765, 335, "⟵ рантайм безкоштовний: один доступ до масиву", GREEN),
    ]
    leg_frags = []
    for (lx, ly, lt, lc) in legend:
        leg_frags.append(text(lx, ly, lt, size=9.5, color=lc, anchor="middle"))

    # заголовок
    title_frag = text(W // 2, 55, "Конвеєр гамма-корекції: де платимо float, де отримуємо O(1)",
                      size=15, color=INK, anchor="middle", bold=True)

    frags = (zone_frags + block_frags + arrow_frags + al_frags + led_frags +
             leg_frags + [title_frag])
    render(path, W, H, *frags)
    print("wrote", os.path.basename(path))


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.5.8 — Чому ≥10 біт: кроки duty при гамма-кривій
# ═════════════════════════════════════════════════════════════════════════════
def fig_lut_steps():
    W, H = 960, 430
    path = os.path.join(OUT, "fig-25-5a-2-lut-steps.svg")

    # Вхідні рівні (рівномірний крок)
    levels_in = list(range(0, 256, 32))   # 0,32,64,...,224,256→255
    levels_in[-1] = 255

    def duty(level, bits):
        max_d = (1 << bits) - 1
        return int(round(((level / 255) ** GAMMA) * max_d))

    # Осі
    # Ліворуч — вісь виходу duty (0..4095 для 12 біт, 0..255 для 8 біт)
    # Знизу — вісь входу level (0..255)

    PLOT_X, PLOT_Y = 90, 60      # верхній лівий кут ділянки
    PLOT_W, PLOT_H = 800, 300    # розміри

    def map_x(lev):
        return PLOT_X + (lev / 255) * PLOT_W

    def map_y_12(d):
        return PLOT_Y + PLOT_H - (d / 4095) * PLOT_H

    def map_y_8(d):
        return PLOT_Y + PLOT_H - (d / 255) * PLOT_H

    frags = []

    # фон ділянки
    frags.append(rect(PLOT_X, PLOT_Y, PLOT_W, PLOT_H, fill=FAINT, stroke=LINE, sw=1, rx=4))

    # Стовпчики — 12-біт (сині, ширші) і 8-біт (червоні, тонші)
    bar_w12 = 18
    bar_w8 = 10

    for lev in levels_in:
        d12 = duty(lev, 12)
        d8 = duty(lev, 8)

        bx = map_x(lev)
        by12 = map_y_12(d12)
        by8 = map_y_8(d8)

        # 12-біт — синій стовпець
        bar_h12 = PLOT_Y + PLOT_H - by12
        if bar_h12 < 1:
            bar_h12 = 1
        frags.append(rect(bx - bar_w12 / 2, by12, bar_w12, bar_h12,
                          fill=LBLUE, stroke=BLUE, sw=1.5, rx=2))

        # 8-біт — червоний стовпець (трохи зміщений)
        bar_h8 = PLOT_Y + PLOT_H - by8
        if bar_h8 < 1:
            bar_h8 = 1
        frags.append(rect(bx + bar_w12 / 2 + 2, by8, bar_w8, bar_h8,
                          fill=LRED, stroke=RED, sw=1.2, rx=2))

        # підпис рівня внизу
        frags.append(text(bx + 3, PLOT_Y + PLOT_H + 18, str(lev),
                          size=9, color=GREY, anchor="middle"))

    # Горизонтальна мертва зона — перші кілька рівнів при 8 біт → duty=0
    dead_end_lev = 0
    for lev in levels_in:
        if duty(lev, 8) == 0 and lev > 0:
            dead_end_lev = lev
    if dead_end_lev > 0:
        dzone_x2 = map_x(dead_end_lev)
        frags.append(rect(PLOT_X, PLOT_Y, dzone_x2 - PLOT_X, PLOT_H,
                          fill="#fee2e2", stroke="none", sw=0, rx=0))
        box_frag, bw, bh = textbox(PLOT_X + (dzone_x2 - PLOT_X) / 2,
                                   PLOT_Y + PLOT_H * 0.35,
                                   "«мертва зона»\n8-біт → 0", size=10,
                                   fill="#fee2e2", stroke=RED, color=RED)
        frags.append(box_frag)

    # Осьові стрілки
    # вісь X
    frags.append(f'<line x1="{PLOT_X:.0f}" y1="{PLOT_Y+PLOT_H:.0f}" '
                 f'x2="{PLOT_X+PLOT_W+20:.0f}" y2="{PLOT_Y+PLOT_H:.0f}" '
                 f'stroke="{LINE}" stroke-width="2" marker-end="url(#arrow)"/>')
    frags.append(text(PLOT_X + PLOT_W + 24, PLOT_Y + PLOT_H + 5,
                      "level (вхід, 0…255)", size=11, color=INK, anchor="start"))
    # вісь Y
    frags.append(f'<line x1="{PLOT_X:.0f}" y1="{PLOT_Y+PLOT_H:.0f}" '
                 f'x2="{PLOT_X:.0f}" y2="{PLOT_Y-20:.0f}" '
                 f'stroke="{LINE}" stroke-width="2" marker-end="url(#arrow)"/>')
    frags.append(text(PLOT_X - 6, PLOT_Y - 24, "duty (вихід ШІМ)", size=11,
                      color=INK, anchor="middle"))

    # Мітки осі Y
    for frac, label_12, label_8 in [(0, "0", "0"), (0.25, "1023", "64"),
                                     (0.5, "2048", "128"), (0.75, "3072", "192"),
                                     (1.0, "4095", "255")]:
        yy = PLOT_Y + PLOT_H - frac * PLOT_H
        frags.append(line(PLOT_X - 5, yy, PLOT_X, yy, color=GREY, sw=1))
        frags.append(text(PLOT_X - 8, yy + 4, label_12, size=8.5, color=BLUE, anchor="end"))

    # Легенда
    leg_x, leg_y = PLOT_X + PLOT_W - 220, PLOT_Y + 14
    frags.append(rect(leg_x, leg_y, 215, 56, fill=BG, stroke=LINE, sw=1, rx=6))
    frags.append(rect(leg_x + 10, leg_y + 12, 16, 14, fill=LBLUE, stroke=BLUE, sw=1.5, rx=2))
    frags.append(text(leg_x + 32, leg_y + 23, "12-біт вихід (0…4095)",
                      size=10, color=BLUE, anchor="start"))
    frags.append(rect(leg_x + 10, leg_y + 34, 16, 14, fill=LRED, stroke=RED, sw=1.2, rx=2))
    frags.append(text(leg_x + 32, leg_y + 45, "8-біт вихід (0…255)",
                      size=10, color=RED, anchor="start"))

    # Підказка: внизу шкали кроки крихітні → потрібна висока роздільність
    note_box, nw, nh = textbox(W // 2, H - 38,
        "При однакових кроках входу (Δlevel=32) — кроки duty внизу набагато менші,\n"
        "ніж угорі. 8-біт: нижні рівні зливаються в 0 (мертва зона). 12-біт: ще розрізняються.",
        size=11, fill=LAMB, stroke=GOLD, color=INK)
    frags.append(note_box)

    # Заголовок
    title_frag = text(W // 2, 30, "Гамма-крива нерівномірно стискає діапазон: внизу — крихітні кроки",
                      size=15, color=INK, anchor="middle", bold=True)
    frags.insert(0, title_frag)

    render(path, W, H, *frags)
    print("wrote", os.path.basename(path))


# ─── main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_gamma_pipeline()
    fig_lut_steps()
    print("Done.")
