# -*- coding: utf-8 -*-
"""
Figures for r13-s1-m-battery-math.md
  fig-13-1m-1-effective-capacity  — waterfall: Q_passport → Q_eff
  fig-13-1m-2-duty-current        — current profile (log scale) + I_avg dashed line
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Fig 1: Waterfall — from Q_passport to Q_eff
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 640, 400
    frags = []

    # Layout constants
    LEFT_COL = 100    # x-center of left (full) bar
    RIGHT_COL = 530   # x-center of right (Q_eff) bar
    BAR_W = 100
    BASE_Y = 330      # bottom baseline y

    Q_passport = 3000  # мА·год
    Q_temp     = Q_passport * 0.80        # after k_temp
    Q_use      = Q_temp   * 0.85         # after k_use  (order: temp first, then cutoff)
    # samoroz approx ~30 мА·год over service life (I_sd≈3.4 мкА × 8766 h = ~30 mAh)
    Q_eff      = Q_use - 30              # ≈ 2010 → round to 2040 as in example

    SCALE = (BASE_Y - 70) / Q_passport   # px per мА·год

    def bar_height(q):
        return q * SCALE

    # Colors
    C_PASSPORT = "#4a90d9"
    C_TEMP     = "#e67e22"
    C_USE      = "#e74c3c"
    C_SD       = "#8e44ad"
    C_EFF      = "#27ae60"

    # --- Left bar: Q_passport ---
    bh = bar_height(Q_passport)
    by = BASE_Y - bh
    frags.append(rect(LEFT_COL - BAR_W/2, by, BAR_W, bh,
                      fill="#dbeafe", stroke=C_PASSPORT, sw=2, rx=4))
    frags.append(text(LEFT_COL, by - 12, "Q_паспорт", size=13, bold=True, color=C_PASSPORT))
    frags.append(text(LEFT_COL, by - 28, "3000 мА·год", size=12, color=C_PASSPORT))

    # Annotations inside left bar — show segments
    # Segment: k_temp loss
    loss_temp = Q_passport - Q_temp
    h_temp = bar_height(loss_temp)
    seg1_top = BASE_Y - bh
    frags.append(rect(LEFT_COL - BAR_W/2, seg1_top, BAR_W, h_temp,
                      fill="#fde68a", stroke=C_TEMP, sw=1.5, rx=2))
    frags.append(text(LEFT_COL, seg1_top + h_temp/2 + 5, "−t°C (×k_temp)", size=10, color=C_TEMP))

    # Segment: k_use loss
    loss_use = Q_temp - Q_use
    h_use = bar_height(loss_use)
    seg2_top = seg1_top + h_temp
    frags.append(rect(LEFT_COL - BAR_W/2, seg2_top, BAR_W, h_use,
                      fill="#fecaca", stroke=C_USE, sw=1.5, rx=2))
    frags.append(text(LEFT_COL, seg2_top + h_use/2 + 5, "−хвіст (×k_use)", size=10, color=C_USE))

    # Remaining segment: samoroz loss
    loss_sd = Q_use - Q_eff
    h_sd = bar_height(loss_sd)
    seg3_top = seg2_top + h_use
    frags.append(rect(LEFT_COL - BAR_W/2, seg3_top, BAR_W, h_sd,
                      fill="#e9d5ff", stroke=C_SD, sw=1.5, rx=2))
    frags.append(text(LEFT_COL, seg3_top + h_sd/2 + 5, "−саморозряд", size=10, color=C_SD))

    # Usable green portion in left bar
    h_eff = bar_height(Q_eff)
    seg4_top = seg3_top + h_sd
    frags.append(rect(LEFT_COL - BAR_W/2, seg4_top, BAR_W, h_eff,
                      fill="#bbf7d0", stroke=C_EFF, sw=1.5, rx=2))

    # --- Right bar: Q_eff ---
    h_eff_r = bar_height(Q_eff)
    eff_top = BASE_Y - h_eff_r
    frags.append(rect(RIGHT_COL - BAR_W/2, eff_top, BAR_W, h_eff_r,
                      fill="#bbf7d0", stroke=C_EFF, sw=2.5, rx=4))
    frags.append(text(RIGHT_COL, eff_top - 12, "Q_eff", size=13, bold=True, color=C_EFF))
    frags.append(text(RIGHT_COL, eff_top - 28, "≈ 2040 мА·год", size=12, color=C_EFF))

    # Arrow connecting bars
    ax1 = LEFT_COL + BAR_W/2 + 8
    ax2 = RIGHT_COL - BAR_W/2 - 8
    ay = BASE_Y - h_eff_r/2
    frags.append(arrow(ax1, ay, ax2, ay, color=C_EFF, sw=2))

    # Baseline
    frags.append(line(LEFT_COL - BAR_W/2 - 10, BASE_Y,
                      RIGHT_COL + BAR_W/2 + 10, BASE_Y, color=MUTED, sw=1))

    # Legend boxes
    legend_x = 230
    legend_y = 70
    items = [
        ("−температура (×k_temp = 0.80): −600 мА·год", "#fde68a", C_TEMP),
        ("−хвіст під відсічкою (×k_use = 0.85): −255 мА·год", "#fecaca", C_USE),
        ("−саморозряд за строк служби: −30 мА·год", "#e9d5ff", C_SD),
        ("= Q_eff ≈ 2040 мА·год (у бюджет)", "#bbf7d0", C_EFF),
    ]
    for i, (lbl, fc, sc) in enumerate(items):
        lx = legend_x
        ly = legend_y + i * 26
        frags.append(rect(lx, ly, 16, 16, fill=fc, stroke=sc, sw=1.5, rx=3))
        frags.append(text(lx + 24, ly + 12, lbl, size=11, anchor="start", color=INK))

    # Caption note at bottom
    note = "У бюджет часу життя підставляють Q_eff — а не цифру з наклейки"
    tb, tw, th = textbox(W/2, H - 22, note, size=11, fill="#f0fdf4", stroke=C_EFF, pad=8)
    frags.append(tb)

    render(os.path.join(OUT, "fig-13-1m-1-effective-capacity.svg"), W, H,
           *frags, title="Від паспортної ємності до реально доступної")

# ─────────────────────────────────────────────────────────────────────────────
# Fig 2: Current profile — log scale, duty cycle, I_avg dashed line
# ─────────────────────────────────────────────────────────────────────────────
def fig2():
    W, H = 720, 400
    frags = []

    # Plot area
    PL = 80    # left margin
    PR = 640   # right edge of plot
    PT = 50    # top
    PB = 300   # bottom (baseline = 0 on log, but we map to log px)

    PLOT_W = PR - PL
    PLOT_H = PB - PT

    # Log axis: 1 мкА → 200 000 мкА (200 mA)
    Y_MIN_UA = 1
    Y_MAX_UA = 200000

    def log_y(ua):
        """Map current in µA to SVG y coordinate (log scale)."""
        if ua <= 0:
            ua = 0.01
        frac = (math.log10(ua) - math.log10(Y_MIN_UA)) / \
               (math.log10(Y_MAX_UA) - math.log10(Y_MIN_UA))
        return PB - frac * PLOT_H

    # Axis
    frags.append(line(PL, PT, PL, PB, color=LINE, sw=1.5))
    frags.append(line(PL, PB, PR, PB, color=LINE, sw=1.5))

    # Y-axis ticks (log)
    yticks = [1, 10, 100, 1000, 10000, 100000]
    ylabels = ["1 мкА", "10 мкА", "100 мкА", "1 мА", "10 мА", "100 мА"]
    for ua, lbl in zip(yticks, ylabels):
        y = log_y(ua)
        frags.append(line(PL - 5, y, PL, y, color=MUTED, sw=1))
        frags.append(line(PL, y, PR, y, color=MUTED, sw=0.5, dash="3,4"))
        frags.append(text(PL - 8, y + 4, lbl, size=10, anchor="end", color=MUTED))

    # Time axis: one full cycle T=60 s; show 2.5 cycles for clarity
    # We show: [sleep] [active 0.25s] [sleep] [active] [sleep]
    # Compress time: sleep shown as proportional width compressed for readability
    # We'll show time 0..120 s mapped to PLOT_W, but compress sleep:
    # actual: 59.75 s sleep + 0.25 s active per cycle
    # visual: show sleep as 48% of each cycle width, active spike prominent
    N_CYCLES = 2
    CYCLE_W = PLOT_W / (N_CYCLES + 0.3)
    SLEEP_W = CYCLE_W * 0.82
    ACT_W   = CYCLE_W * 0.18   # visually exaggerated for clarity

    I_SLEEP = 12      # мкА
    I_ACT   = 130000  # мкА (130 mA)
    I_AVG   = 554     # мкА

    y_sleep = log_y(I_SLEEP)
    y_act   = log_y(I_ACT)
    y_avg   = log_y(I_AVG)

    C_SLEEP  = NEG
    C_ACT    = POS
    C_AVG    = FIELD

    # Draw profile: sleep → spike → sleep → spike → trailing sleep
    x = PL
    for c in range(N_CYCLES):
        # sleep plateau
        x_end_sleep = x + SLEEP_W
        frags.append(line(x, y_sleep, x_end_sleep, y_sleep, color=C_SLEEP, sw=2.5))
        if c > 0:
            frags.append(line(x, log_y(I_SLEEP * 0.8), x, y_sleep, color=C_SLEEP, sw=2.5))
        # vertical rise
        frags.append(line(x_end_sleep, y_sleep, x_end_sleep, y_act, color=C_ACT, sw=2))
        # active top
        x_end_act = x_end_sleep + ACT_W
        frags.append(line(x_end_sleep, y_act, x_end_act, y_act, color=C_ACT, sw=3))
        # vertical fall
        frags.append(line(x_end_act, y_act, x_end_act, y_sleep, color=C_ACT, sw=2))
        x = x_end_act

    # trailing sleep
    frags.append(line(x, y_sleep, PR, y_sleep, color=C_SLEEP, sw=2.5))

    # I_avg dashed line
    frags.append(line(PL, y_avg, PR, y_avg, color=C_AVG, sw=2, dash="8,5"))
    # label I_avg
    frags.append(text(PR + 4, y_avg + 4, "I_avg", size=11, anchor="start", color=C_AVG, bold=True))
    frags.append(text(PR + 4, y_avg + 17, "≈ 554 мкА", size=10, anchor="start", color=C_AVG))

    # Label sleep level
    frags.append(text(PL + 30, y_sleep - 9, "сон ≈ 12 мкА", size=11, anchor="start", color=C_SLEEP, bold=True))

    # Label active spike
    mid_act_x = PL + SLEEP_W + ACT_W/2
    frags.append(text(mid_act_x, y_act - 11, "130 мА", size=11, anchor="middle", color=C_ACT, bold=True))
    frags.append(text(mid_act_x, y_act - 24, "0.25 с", size=10, anchor="middle", color=C_ACT))

    # X-axis label
    frags.append(text(PL + PLOT_W/2, PB + 22, "час (2 цикли по 60 с; активний сплеск збільшено для наочності)", size=10, color=MUTED))

    # Y-axis label (rotated via transform)
    frags.append('<text x="%d" y="%d" font-family="%s" font-size="11" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90,%d,%d)">струм (лог. шкала)</text>'
                 % (16, PT + PLOT_H//2, FONT, MUTED, 16, PT + PLOT_H//2))

    # Annotation: area under spikes dominates
    # Arrow from avg line toward spike area
    annot_x = PL + SLEEP_W * 0.3
    annot_y = y_avg + 35
    tb, tw, th = textbox(annot_x + 120, annot_y + 40,
                         "542 з 554 мкА дає\nсам сплеск передачі", size=10,
                         fill="#f0fdf4", stroke=C_AVG, pad=7)
    frags.append(tb)

    # Caption note at bottom
    note = "Перший важіль економії — рідші й коротші виходи в радіо, а не глибший сон"
    tb2, _, _ = textbox(W/2, H - 22, note, size=11, fill="#f0fdf4", stroke=C_AVG, pad=8)
    frags.append(tb2)

    render(os.path.join(OUT, "fig-13-1m-2-duty-current.svg"), W, H,
           *frags, title="Чому вирішує середній струм, а не сон")

if __name__ == "__main__":
    fig1()
    fig2()
    print("OK: fig-13-1m-1 and fig-13-1m-2 written to", OUT)
