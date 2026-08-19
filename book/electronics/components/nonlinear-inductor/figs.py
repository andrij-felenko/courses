# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
AMBER   = "#e0a32e"
AMBERBG = "#fff8e7"
REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"
PURPLE  = "#8e44ad"
PURPLEBG= "#f4ecf7"
CYAN    = "#00838f"


# ── 1. bh-hysteresis-saturation: петля гістерезису та насичення осердя ────────
def fig_bh_hysteresis():
    W, H = 840, 480
    p = []

    cx, cy = 390, 235
    ax_len_x = 230
    ax_len_y = 175

    # Осі
    p.append(line(cx - ax_len_x, cy, cx + ax_len_x, cy, color=LINE, sw=1.5))
    p.append(arrow(cx + ax_len_x - 1, cy, cx + ax_len_x + 10, cy, color=LINE, sw=1.8))
    p.append(text(cx + ax_len_x + 16, cy + 4, "H (А/м)", size=11, color=INK, anchor="start", bold=True))

    p.append(line(cx, cy + ax_len_y, cx, cy - ax_len_y, color=LINE, sw=1.5))
    p.append(arrow(cx, cy - ax_len_y + 1, cx, cy - ax_len_y - 10, color=LINE, sw=1.8))
    p.append(text(cx + 8, cy - ax_len_y - 8, "B (Тл)", size=11, color=INK, anchor="start", bold=True))

    # Лінії насичення +B_sat і -B_sat
    y_bsat_pos = cy - 130
    y_bsat_neg = cy + 130
    p.append(line(cx - 190, y_bsat_pos, cx + 190, y_bsat_pos, color=POS, sw=1.2, dash="4 4"))
    p.append(line(cx - 190, y_bsat_neg, cx + 190, y_bsat_neg, color=POS, sw=1.2, dash="4 4"))
    p.append(text(cx - 195, y_bsat_pos + 4, "+B_sat", size=10, color=POS, anchor="end", bold=True))
    p.append(text(cx - 195, y_bsat_neg + 4, "−B_sat", size=10, color=POS, anchor="end", bold=True))

    # Петля гістерезису
    pts_top = [
        (cx + 190, cy - 138),
        (cx + 135, cy - 130),
        (cx + 80,  cy - 120),
        (cx + 30,  cy - 95),
        (cx,       cy - 75),   # +Br
        (cx - 30,  cy - 35),
        (cx - 55,  cy),        # -Hc
        (cx - 85,  cy + 65),
        (cx - 130, cy + 120),
        (cx - 190, cy + 138)
    ]
    pts_bot = [
        (cx - 190, cy + 138),
        (cx - 135, cy + 130),
        (cx - 80,  cy + 120),
        (cx - 30,  cy + 95),
        (cx,       cy + 75),   # -Br
        (cx + 30,  cy + 35),
        (cx + 55,  cy),        # +Hc
        (cx + 85,  cy - 65),
        (cx + 130, cy - 120),
        (cx + 190, cy - 138)
    ]

    path_top = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_top)
    path_bot = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_bot)

    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_top, NEG))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_bot, NEG))

    # Початкова крива намагнічування (від нуля)
    pts_init = [
        (cx, cy),
        (cx + 25, cy - 35),
        (cx + 60, cy - 85),
        (cx + 105, cy - 118),
        (cx + 145, cy - 130),
        (cx + 190, cy - 138)
    ]
    path_init = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_init)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3 3"/>' % (path_init, FIELD))

    # Точки Br і Hc
    p.append(circle(cx, cy - 75, 4, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(cx - 10, cy - 75 - 6, "+B_r (залишкова індукція)", size=9, color=NEG, anchor="end", bold=True))

    p.append(circle(cx, cy + 75, 4, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(cx + 10, cy + 75 + 12, "−B_r", size=9, color=NEG, anchor="start", bold=True))

    p.append(circle(cx + 55, cy, 4, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(cx + 55, cy + 18, "+H_c", size=9, color=NEG, anchor="middle", bold=True))

    p.append(circle(cx - 55, cy, 4, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(cx - 55, cy + 18, "−H_c (коерцитивна сила)", size=9, color=NEG, anchor="middle", bold=True))

    # Коліно насичення (knee)
    p.append(circle(cx + 115, cy - 122, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(line(cx + 115, cy - 122, cx + 155, cy - 165, color=POS, sw=1.2))
    p.append(line(cx + 155, cy - 165, cx + 195, cy - 165, color=POS, sw=1.2))
    p.append(text(cx + 200, cy - 162, "Коліно насичення", size=10, color=POS, anchor="start", bold=True))
    p.append(text(cx + 200, cy - 148, "dB/dH стрімко падає", size=9, color=INK, anchor="start"))

    # Зона насичення (нахил dB/dH -> mu0)
    p.append(line(cx + 150, cy - 130, cx + 210, cy - 142, color=POS, sw=2))
    p.append(text(cx + 215, cy - 130, "dB/dH = μ₀", size=10, color=POS, anchor="start", bold=True))

    # Пояснювальні плашки зліва та справа
    box_l, _, _ = textbox(110, 105, "Робоча область:\n• Висока проникність μ_r\n• Накопичення енергії\n• Мінімальні спотворення",
                          size=9, pad=8, fill=GRNBG, stroke=FIELD, bold=False)
    p.append(box_l)

    box_r, _, _ = textbox(725, 105, "Зона насичення:\n• Всі домени вишикувані\n• μ_diff → μ₀ ≈ 1.26 мкГн/м\n• Індуктивність падає",
                          size=9, pad=8, fill=REDBG, stroke=POS, bold=False)
    p.append(box_r)

    # Підпис внизу
    p.append(text(W/2, 455, "Петля гістерезису B-H феромагнетика: індукція насичення B_sat, залишкова індукція B_r та коліно насичення",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "bh-hysteresis-saturation.svg"), W, H, *p,
           title="Петля гістерезису B-H і межа магнітного насичення")


# ── 2. differential-inductance-curve: колапс диференціальної індуктивності ────
def fig_diff_inductance():
    W, H = 760, 420
    p = []

    ox, oy = 90, 340
    w_ax, h_ax = 580, 270

    # Осі
    p.append(line(ox, oy, ox + w_ax, oy, color=LINE, sw=1.5))
    p.append(arrow(ox + w_ax - 1, oy, ox + w_ax + 10, oy, color=LINE, sw=1.8))
    p.append(text(ox + w_ax + 15, oy + 4, "Струм I (А)", size=11, color=INK, anchor="start", bold=True))

    p.append(line(ox, oy, ox, oy - h_ax, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - h_ax + 1, ox, oy - h_ax - 10, color=LINE, sw=1.8))
    p.append(text(ox, oy - h_ax - 15, "Індуктивність L (Гн)", size=11, color=INK, anchor="middle", bold=True))

    # Рівні на осі Y: L0 і L_air
    y_l0 = oy - 220
    y_lair = oy - 15

    p.append(line(ox - 5, y_l0, ox, y_l0, color=INK, sw=1.2))
    p.append(text(ox - 10, y_l0 + 4, "L₀ (номінал)", size=10, color=NEG, anchor="end", bold=True))

    p.append(line(ox - 5, y_lair, ox, y_lair, color=INK, sw=1.2))
    p.append(text(ox - 10, y_lair + 4, "L_air (без осердя)", size=10, color=POS, anchor="end", bold=True))

    # Струм I_sat на осі X
    x_isat = ox + 280
    p.append(line(x_isat, oy, x_isat, oy + 5, color=INK, sw=1.2))
    p.append(line(x_isat, oy, x_isat, y_l0 - 20, color=POS, sw=1.2, dash="4 4"))
    p.append(text(x_isat, oy + 20, "I_sat (струм насичення)", size=10, color=POS, anchor="middle", bold=True))

    # Крива диференціальної індуктивності L_diff(I) = dPsi/dI (червона)
    pts_diff = [
        (ox, y_l0),
        (ox + 120, y_l0),
        (ox + 200, y_l0 + 5),
        (ox + 240, y_l0 + 20),
        (ox + 270, y_l0 + 70),
        (ox + 290, y_l0 + 140),
        (ox + 320, y_lair - 15),
        (ox + 380, y_lair - 3),
        (ox + 520, y_lair)
    ]
    path_diff = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_diff)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_diff, POS))

    # Крива статичної індуктивності L_stat(I) = Psi/I (синя пунктирна)
    pts_stat = [
        (ox, y_l0),
        (ox + 140, y_l0),
        (ox + 220, y_l0 + 10),
        (ox + 270, y_l0 + 40),
        (ox + 330, y_l0 + 100),
        (ox + 400, y_l0 + 150),
        (ox + 480, y_lair - 25),
        (ox + 540, y_lair - 10)
    ]
    path_stat = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_stat)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>' % (path_stat, NEG))

    # Підписи до кривих
    p.append(text(ox + 180, y_l0 - 15, "L_diff(i) = dΨ/di (диференціальна)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(ox + 370, y_l0 + 80, "L_stat(i) = Ψ/i (статична)", size=10, color=NEG, anchor="start", bold=True))

    # Зони на графіку
    p.append(rect(ox + 10, y_l0 + 30, 160, 65, fill=GRNBG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(ox + 90, y_l0 + 52, "Лінійна зона L ≈ L₀", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(ox + 90, y_l0 + 72, "di/dt = U / L₀ (сталий нахил)", size=9, color=INK, anchor="middle"))

    p.append(rect(ox + 350, y_lair - 90, 200, 75, fill=REDBG, stroke=POS, sw=1.2, rx=6))
    p.append(text(ox + 450, y_lair - 68, "Зона глибокого насичення", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(ox + 450, y_lair - 50, "L_diff → L_air (колапс у 100–1000 разів)", size=9, color=INK, anchor="middle"))
    p.append(text(ox + 450, y_lair - 32, "di/dt = U / L_air → стрибок струму!", size=9, color=POS, anchor="middle", bold=True))

    # Стрілка показує коліно колапсу
    p.append(circle(ox + 280, y_l0 + 95, 6, fill=AMBER, stroke=INK, sw=1.5))
    p.append(text(ox + 295, y_l0 + 100, "Колапс індуктивності", size=10, color=AMBER, anchor="start", bold=True))

    # Підпис внизу
    p.append(text(W/2, 400, "Диференціальна індуктивність L_diff(i) проти струму: різкий обвал при переході за межу I_sat",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "differential-inductance-curve.svg"), W, H, *p,
           title="Диференціальна та статична індуктивність при насиченні")


# ── 3. hard-vs-soft-saturation: жорстке проти м'якого насичення матеріалів ────
def fig_hard_vs_soft():
    W, H = 760, 430
    p = []

    ox, oy = 80, 350
    w_ax, h_ax = 600, 280

    # Осі
    p.append(line(ox, oy, ox + w_ax, oy, color=LINE, sw=1.5))
    p.append(arrow(ox + w_ax - 1, oy, ox + w_ax + 10, oy, color=LINE, sw=1.8))
    p.append(text(ox + w_ax + 15, oy + 4, "Струм підмагнічування I_dc (% від номіналу)", size=10, color=INK, anchor="start", bold=True))

    p.append(line(ox, oy, ox, oy - h_ax, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - h_ax + 1, ox, oy - h_ax - 10, color=LINE, sw=1.8))
    p.append(text(ox, oy - h_ax - 15, "Індуктивність L / L₀ (%)", size=11, color=INK, anchor="middle", bold=True))

    # Розмітка осі Y (0%, 20%, 40%, 60%, 80%, 100%)
    for pct in [20, 40, 60, 80, 100]:
        y = oy - (pct / 100.0) * 230
        p.append(line(ox - 4, y, ox + w_ax - 20, y, color="#e5e7eb", sw=1))
        p.append(text(ox - 8, y + 4, "%d%%" % pct, size=9, color=MUTED, anchor="end"))

    # Розмітка осі X (0%, 50%, 100%, 150%, 200%, 250%)
    for pct in [50, 100, 150, 200, 250]:
        x = ox + (pct / 250.0) * (w_ax - 40)
        p.append(line(x, oy, x, oy + 5, color=LINE, sw=1))
        p.append(text(x, oy + 18, "%d%%" % pct, size=9, color=MUTED, anchor="middle"))

    scale_x = (w_ax - 40) / 250.0
    scale_y = 230 / 100.0

    # 1. Ферит MnZn (Hard Saturation) — червона суцільна лінія
    pts_ferrite = [
        (ox + 0 * scale_x, oy - 100 * scale_y),
        (ox + 50 * scale_x, oy - 100 * scale_y),
        (ox + 90 * scale_x, oy - 98 * scale_y),
        (ox + 105 * scale_x, oy - 92 * scale_y),
        (ox + 115 * scale_x, oy - 50 * scale_y),
        (ox + 125 * scale_x, oy - 12 * scale_y),
        (ox + 160 * scale_x, oy - 5 * scale_y),
        (ox + 240 * scale_x, oy - 3 * scale_y)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_ferrite), POS))

    # 2. Порошковий Sendust / Kool-Mu (Soft Saturation) — зелена лінія
    pts_sendust = [
        (ox + 0 * scale_x, oy - 100 * scale_y),
        (ox + 50 * scale_x, oy - 94 * scale_y),
        (ox + 100 * scale_x, oy - 80 * scale_y),
        (ox + 150 * scale_x, oy - 62 * scale_y),
        (ox + 200 * scale_x, oy - 46 * scale_y),
        (ox + 240 * scale_x, oy - 35 * scale_y)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_sendust), FIELD))

    # 3. Порошковий MPP (Molypermalloy) — фіолетова лінія
    pts_mpp = [
        (ox + 0 * scale_x, oy - 100 * scale_y),
        (ox + 50 * scale_x, oy - 97 * scale_y),
        (ox + 100 * scale_x, oy - 88 * scale_y),
        (ox + 150 * scale_x, oy - 74 * scale_y),
        (ox + 200 * scale_x, oy - 58 * scale_y),
        (ox + 240 * scale_x, oy - 45 * scale_y)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 3"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_mpp), PURPLE))

    # 4. Залізопорошкове осердя (Iron Powder -26) — бурштинова лінія
    pts_iron = [
        (ox + 0 * scale_x, oy - 100 * scale_y),
        (ox + 50 * scale_x, oy - 85 * scale_y),
        (ox + 100 * scale_x, oy - 68 * scale_y),
        (ox + 150 * scale_x, oy - 50 * scale_y),
        (ox + 200 * scale_x, oy - 36 * scale_y),
        (ox + 240 * scale_x, oy - 25 * scale_y)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3 3"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_iron), AMBER))

    # Легенда
    leg_x, leg_y = ox + 320, oy - 220
    p.append(rect(leg_x - 10, leg_y - 15, 230, 115, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))

    p.append(line(leg_x, leg_y, leg_x + 25, leg_y, color=POS, sw=3))
    p.append(text(leg_x + 32, leg_y + 4, "Ферит MnZn (Hard Saturation)", size=10, color=POS, anchor="start", bold=True))

    p.append(line(leg_x, leg_y + 25, leg_x + 25, leg_y + 25, color=PURPLE, sw=2.5, dash="6 3"))
    p.append(text(leg_x + 32, leg_y + 29, "MPP / High Flux (Soft)", size=10, color=PURPLE, anchor="start", bold=True))

    p.append(line(leg_x, leg_y + 50, leg_x + 25, leg_y + 50, color=FIELD, sw=2.5))
    p.append(text(leg_x + 32, leg_y + 54, "Kool-Mµ / Sendust (Soft)", size=10, color=FIELD, anchor="start", bold=True))

    p.append(line(leg_x, leg_y + 75, leg_x + 25, leg_y + 75, color=AMBER, sw=2, dash="3 3"))
    p.append(text(leg_x + 32, leg_y + 79, "Залізопорошок Iron Powder (Soft)", size=10, color=AMBER, anchor="start", bold=True))

    # Виноска на обрив фериту
    p.append(circle(ox + 115 * scale_x, oy - 50 * scale_y, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(text(ox + 122 * scale_x + 10, oy - 50 * scale_y - 10, "Стрімкий обрив", size=10, color=POS, anchor="start", bold=True))
    p.append(text(ox + 122 * scale_x + 10, oy - 50 * scale_y + 6, "(загроза для MOSFET)", size=9, color=INK, anchor="start"))

    # Підпис внизу
    p.append(text(W/2, 410, "Порівняння кривих спаду L(I_dc): жорстке насичення фериту проти м'якого спаду композитних порошків",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "hard-vs-soft-saturation.svg"), W, H, *p,
           title="Жорстке та м'яке насичення магнітних матеріалів")


# ── 4. converter-current-waveform: динаміка струму та сплеск «акулячий плавник» ─
def fig_converter_current():
    W, H = 780, 450
    p = []

    # Верхній графік: сигнал затвора V_gate (ON/OFF)
    ox, oy_g = 70, 100
    w_ax = 450

    p.append(line(ox, oy_g, ox + w_ax, oy_g, color=LINE, sw=1.5))
    p.append(text(ox - 10, oy_g - 20, "V_gate", size=10, color=INK, anchor="end", bold=True))

    # Імпульс керування (0..t_on..T_sw)
    t1 = ox + 40
    t2 = ox + 260   # t_on
    t3 = ox + 430   # T_sw
    p.append(line(ox, oy_g, t1, oy_g, color=NEG, sw=2))
    p.append(line(t1, oy_g, t1, oy_g - 40, color=NEG, sw=2))
    p.append(line(t1, oy_g - 40, t2, oy_g - 40, color=NEG, sw=2))
    p.append(line(t2, oy_g - 40, t2, oy_g, color=NEG, sw=2))
    p.append(line(t2, oy_g, t3, oy_g, color=NEG, sw=2))

    p.append(text((t1 + t2)/2, oy_g - 48, "t_on (MOSFET відкрито)", size=9, color=NEG, anchor="middle", bold=True))
    p.append(text((t2 + t3)/2, oy_g - 10, "t_off (закрито)", size=9, color=MUTED, anchor="middle"))

    # Нижній графік: струм дроселя i_L(t)
    oy_i = 360
    h_i = 210

    p.append(line(ox, oy_i, ox + w_ax, oy_i, color=LINE, sw=1.5))
    p.append(arrow(ox + w_ax - 1, oy_i, ox + w_ax + 10, oy_i, color=LINE, sw=1.8))
    p.append(text(ox + w_ax + 15, oy_i + 4, "Час t", size=10, color=INK, anchor="start", bold=True))

    p.append(line(ox, oy_i, ox, oy_i - h_i, color=LINE, sw=1.5))
    p.append(arrow(ox, oy_i - h_i + 1, ox, oy_i - h_i - 10, color=LINE, sw=1.8))
    p.append(text(ox, oy_i - h_i - 12, "Струм котушки i_L(t) (А)", size=10, color=INK, anchor="middle", bold=True))

    # Рівні струму
    y_imin = oy_i - 25
    y_isat = oy_i - 85
    y_inorm = oy_i - 105
    y_ispike = oy_i - 190

    p.append(line(ox, y_isat, ox + w_ax, y_isat, color=AMBER, sw=1.2, dash="4 4"))
    p.append(text(ox + w_ax + 5, y_isat + 4, "I_sat", size=9, color=AMBER, anchor="start", bold=True))

    # Нормальна форма струму (зелений пунктир)
    p.append(line(t1, y_imin, t2, y_inorm, color=FIELD, sw=2, dash="4 4"))
    p.append(line(t2, y_inorm, t3, y_imin, color=FIELD, sw=2, dash="4 4"))
    p.append(text(t2 + 8, y_inorm + 4, "Нормальний хід", size=9, color=FIELD, anchor="start", bold=True))

    # Реальна аварійна форма струму при насиченні (червона лінія)
    t_sat = t1 + (t2 - t1) * 0.55
    p.append(line(t1, y_imin, t_sat, y_isat, color=POS, sw=2.5))
    pts_spike = [
        (t_sat, y_isat),
        (t_sat + 30, y_isat - 22),
        (t_sat + 60, y_isat - 55),
        (t2, y_ispike)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_spike), POS))
    p.append(line(t2, y_ispike, t3, y_imin, color=POS, sw=2.5))

    # Виноска «Shark fin»
    p.append(circle(t2, y_ispike, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(text(t2 - 12, y_ispike - 10, "«Акулячий плавник» (Shark Fin)", size=10, color=POS, anchor="end", bold=True))
    p.append(text(t2 - 12, y_ispike + 6, "di/dt → U / L_air", size=9, color=POS, anchor="end"))

    # Пояснювальний блок праворуч
    box_fail, _, _ = textbox(655, 230, "Наслідки для MOSFET:\n• Струм перевищує I_max\n• Вихід із насичення\n• Сплеск P = V_ds · I_d\n• Тепловий пробій кристала",
                             size=9, pad=8, fill=REDBG, stroke=POS, bold=False)
    p.append(box_fail)

    # Підпис внизу
    p.append(text(W/2, 430, "Форма струму в імпульсному перетворювачі: виникнення акулячого плавника при вході дроселя в насичення",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "converter-current-waveform.svg"), W, H, *p,
           title="Динаміка струму при насиченні силового дроселя")


# ── 5. temperature-derating-bsat: температурна деградація B_sat ───────────────
def fig_temp_derating():
    W, H = 760, 420
    p = []

    ox, oy = 80, 340
    w_ax, h_ax = 580, 260

    # Осі
    p.append(line(ox, oy, ox + w_ax, oy, color=LINE, sw=1.5))
    p.append(arrow(ox + w_ax - 1, oy, ox + w_ax + 10, oy, color=LINE, sw=1.8))
    p.append(text(ox + w_ax + 15, oy + 4, "Температура осердя T (°C)", size=11, color=INK, anchor="start", bold=True))

    p.append(line(ox, oy, ox, oy - h_ax, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - h_ax + 1, ox, oy - h_ax - 10, color=LINE, sw=1.8))
    p.append(text(ox, oy - h_ax - 15, "Індукція насичення B_sat (Тл)", size=11, color=INK, anchor="middle", bold=True))

    scale_t = (w_ax - 60) / 240.0   # 0..240 °C
    scale_b = 210 / 0.6            # 0..0.6 Тл

    # Розмітка Y: 0.1, 0.2, 0.3, 0.4, 0.5 Тл
    for b in [0.1, 0.2, 0.3, 0.4, 0.5]:
        y = oy - b * scale_b
        p.append(line(ox - 4, y, ox + w_ax - 40, y, color="#f3f4f6", sw=1))
        p.append(text(ox - 8, y + 4, "%.1f" % b, size=9, color=MUTED, anchor="end"))

    # Розмітка X: 25, 60, 100, 125, 150, 200, 220 °C
    for t in [25, 60, 100, 125, 150, 200, 220]:
        x = ox + t * scale_t
        p.append(line(x, oy, x, oy + 5, color=LINE, sw=1))
        p.append(text(x, oy + 18, "%d" % t, size=9, color=MUTED, anchor="middle"))

    # Крива B_sat(T) для силового фериту MnZn
    pts_b = [
        (ox + 0 * scale_t, oy - 0.50 * scale_b),
        (ox + 25 * scale_t, oy - 0.49 * scale_b),
        (ox + 60 * scale_t, oy - 0.43 * scale_b),
        (ox + 100 * scale_t, oy - 0.36 * scale_b),
        (ox + 125 * scale_t, oy - 0.30 * scale_b),
        (ox + 160 * scale_t, oy - 0.20 * scale_b),
        (ox + 200 * scale_t, oy - 0.08 * scale_b),
        (ox + 220 * scale_t, oy - 0.00 * scale_b)
    ]
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' %
             ("M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_b), POS))

    # Точка 25 °C (паспортний B_sat)
    x_25 = ox + 25 * scale_t
    y_25 = oy - 0.49 * scale_b
    p.append(circle(x_25, y_25, 5, fill=FIELD, stroke=INK, sw=1.2))
    p.append(line(x_25, y_25, x_25, oy, color=FIELD, sw=1, dash="3 3"))
    p.append(text(x_25 + 10, y_25 - 8, "25 °C: B_sat = 0.49 Тл (холодний старт)", size=10, color=FIELD, anchor="start", bold=True))

    # Точка 100 °C (робочий нагрів у корпусі)
    x_100 = ox + 100 * scale_t
    y_100 = oy - 0.36 * scale_b
    p.append(circle(x_100, y_100, 5, fill=AMBER, stroke=INK, sw=1.2))
    p.append(line(x_100, y_100, x_100, oy, color=AMBER, sw=1, dash="3 3"))
    p.append(text(x_100 + 10, y_100 - 8, "100 °C: B_sat = 0.36 Тл (−27% запасу!)", size=10, color=AMBER, anchor="start", bold=True))

    # Точка 125 °C (максимальна температура)
    x_125 = ox + 125 * scale_t
    y_125 = oy - 0.30 * scale_b
    p.append(circle(x_125, y_125, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(line(x_125, y_125, x_125, oy, color=POS, sw=1, dash="3 3"))
    p.append(text(x_125 + 10, y_125 + 18, "125 °C: B_sat = 0.30 Тл (−39%)", size=10, color=POS, anchor="start", bold=True))

    # Точка Кюрі Tc
    x_curie = ox + 220 * scale_t
    p.append(circle(x_curie, oy, 5, fill=LINE, stroke=INK, sw=1.2))
    p.append(text(x_curie, oy - 20, "T_c (точка Кюрі ≈ 220 °C)", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(x_curie, oy - 6, "втрата феромагнетизму", size=9, color=MUTED, anchor="middle"))

    # Пояснювальний блок інженерного правила
    box_rule, _, _ = textbox(470, 110, "Золоте правило розрахунку:\n• Рахувати B_max для T = 100…125 °C\n• Закладати робочу індукцію B_pk ≤ 0.75 · B_sat(100°C)\n• Для фериту N87: B_pk_max ≤ 0.27 Тл",
                             size=9, pad=8, fill=AMBERBG, stroke=AMBER, bold=False)
    p.append(box_rule)

    # Підпис внизу
    p.append(text(W/2, 400, "Температурна залежність індукції насичення B_sat(T) фериту: спадання робочого запасу при нагріві",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "temperature-derating-bsat.svg"), W, H, *p,
           title="Температурний дератинг індукції насичення фериту")


# ── 6. pulse-tester-concept: імпульсний стенд вимірювання L(I) ───────────────
def fig_pulse_tester():
    W, H = 760, 430
    p = []

    # Схема імпульсного стенда (зліва)
    sx, sy = 40, 60

    # Банк конденсаторів (C_bank)
    p.append(rect(sx, sy, 110, 150, fill=BLUEBG, stroke=NEG, sw=1.5, rx=6))
    p.append(text(sx + 55, sy + 30, "Банк C_bank", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(sx + 55, sy + 50, "1000…4700 мкФ", size=9, color=INK, anchor="middle"))
    p.append(text(sx + 55, sy + 68, "Низький ESR", size=9, color=MUTED, anchor="middle"))
    p.append(text(sx + 55, sy + 125, "+ Напруга V_test", size=10, color=POS, anchor="middle", bold=True))

    # Дроти від C_bank до ключа і DUT
    y_top = sy + 30
    y_bot = sy + 130

    p.append(line(sx + 110, y_top, sx + 160, y_top, color=LINE, sw=2))
    p.append(line(sx + 110, y_bot, sx + 390, y_bot, color=LINE, sw=2))

    # Ключ MOSFET
    p.append(rect(sx + 160, y_top - 25, 90, 50, fill=GRNBG, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(sx + 205, y_top - 5, "MOSFET", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(sx + 205, y_top + 12, "Ключ імпульсу", size=9, color=INK, anchor="middle"))

    # Драйвер затвора
    p.append(line(sx + 205, y_top + 25, sx + 205, y_top + 60, color=LINE, sw=1.5))
    p.append(rect(sx + 155, y_top + 60, 100, 35, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    p.append(text(sx + 205, y_top + 82, "Імпульс 5…50 мкс", size=9, color=INK, anchor="middle", bold=True))

    # З'єднання від MOSFET до DUT
    p.append(line(sx + 250, y_top, sx + 300, y_top, color=LINE, sw=2))

    # Випробуваний дросель (DUT Inductor)
    p.append(rect(sx + 300, y_top - 25, 80, 50, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=6))
    p.append(text(sx + 340, y_top - 5, "DUT", size=11, color=AMBER, anchor="middle", bold=True))
    p.append(text(sx + 340, y_top + 12, "Дросель L", size=9, color=INK, anchor="middle"))

    # Зворотний діод (Freewheeling / Clamp Diode) паралельно DUT
    p.append(line(sx + 290, y_top, sx + 290, y_top + 80, color=LINE, sw=1.5))
    p.append(line(sx + 390, y_top, sx + 390, y_top + 80, color=LINE, sw=1.5))
    p.append(rect(sx + 290, y_top + 70, 100, 25, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(sx + 340, y_top + 87, "Захисний діод", size=9, color=POS, anchor="middle", bold=True))

    # Струмовий шунт R_shunt
    p.append(line(sx + 380, y_top, sx + 410, y_top, color=LINE, sw=2))
    p.append(rect(sx + 410, y_top - 15, 60, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(sx + 440, y_top + 50, "Шунт", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(sx + 440, y_top + 70, "R_sense", size=9, color=MUTED, anchor="middle"))
    p.append(text(sx + 440, y_top + 90, "10 мОм", size=9, color=INK, anchor="middle"))

    p.append(line(sx + 440, y_top + 145, sx + 440, y_bot, color=LINE, sw=2))
    p.append(line(sx + 440, y_bot, sx + 390, y_bot, color=LINE, sw=2))

    # Осцилограф / АЦП збір даних (праворуч)
    gx, gy = 540, 60
    p.append(rect(gx, gy, 190, 220, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(gx + 95, gy + 25, "Збір та розрахунок", size=11, color=INK, anchor="middle", bold=True))

    # Формули обробки всередині блоку збору
    p.append(rect(gx + 10, gy + 45, 170, 45, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    p.append(text(gx + 95, gy + 65, "i(t) = V_shunt(t) / R", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(gx + 95, gy + 80, "миттєвий струм", size=9, color=MUTED, anchor="middle"))

    p.append(rect(gx + 10, gy + 100, 170, 50, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    p.append(text(gx + 95, gy + 120, "Ψ(t) = ∫ [u(t)−i·R] dt", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(gx + 95, gy + 138, "потокозчеплення", size=9, color=MUTED, anchor="middle"))

    p.append(rect(gx + 10, gy + 160, 170, 50, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    p.append(text(gx + 95, gy + 180, "L_diff(i) = u_L / (di/dt)", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(gx + 95, gy + 198, "диференціальна крива", size=9, color=MUTED, anchor="middle"))

    # З'єднувальні стрілки вимірювання
    p.append(line(sx + 340, y_top - 25, sx + 340, gy - 20, color=AMBER, sw=1.2))
    p.append(line(sx + 340, gy - 20, gx + 40, gy - 20, color=AMBER, sw=1.2))
    p.append(arrow(gx + 40, gy - 20, gx + 40, gy, color=AMBER, sw=1.5))
    p.append(text(gx - 40, gy - 25, "Канал напруги u_L(t)", size=9, color=AMBER, anchor="end", bold=True))

    p.append(line(sx + 470, y_top + 60, gx + 40, y_top + 60, color=NEG, sw=1.2))
    p.append(arrow(gx + 20, y_top + 60, gx + 40, y_top + 60, color=NEG, sw=1.5))
    p.append(text(sx + 490, y_top + 52, "Канал струму", size=9, color=NEG, anchor="start", bold=True))

    # Нижній пояснювальний блок переваг імпульсного методу
    p.append(rect(40, 300, 690, 80, fill=GRNBG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(55, 324, "Чому саме поодинокий короткий імпульс (Single-Pulse Method):", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(55, 344, "1. Дросель НЕ встигає нагрітися постійним струмом під час тесту (виключається спад B_sat).", size=9, color=INK, anchor="start"))
    p.append(text(55, 362, "2. Знімається повна характеристика L_diff(i) від 0 до сотень ампер за один імпульс 20…50 мкс.", size=9, color=INK, anchor="start"))

    # Підпис внизу
    p.append(text(W/2, 410, "Структура вимірювального стенда для зняття кривих L(i) методом поодинокого імпульсу високого струму",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "pulse-tester-concept.svg"), W, H, *p,
           title="Імпульсний метод вимірювання нелінійної індуктивності")


if __name__ == "__main__":
    fig_bh_hysteresis()
    fig_diff_inductance()
    fig_hard_vs_soft()
    fig_converter_current()
    fig_temp_derating()
    fig_pulse_tester()
    print("All 6 figures generated successfully.")
