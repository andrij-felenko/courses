# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 «MOSFET-модуль для ШІМ-навантажень» (до теми 4.7.5c).
fig-25-5c-1-mosfet-module.svg   → Рис. 4.7.5c.1  (блок-схема модуля)
fig-25-5c-2-gate-threshold.svg  → Рис. 4.7.5c.2  (поріг затвора)

Імпортує спільний kit; примітиви з svgkit — НЕ переписуються тут.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── локальні кольори ──────────────────────────────────────────────────────────
LRED   = "#fbecec"
LBLUE  = "#e9eefb"
LGRN   = "#eef6ef"
LAMB   = "#fff6e0"
GOLD   = "#caa24a"
RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
GREY   = "#8a8a8a"
ORANGE = "#e07b00"
LORANGE= "#fff3e0"
PURPLE = "#7b2fa8"
LPURP  = "#f3eafa"


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.5c.1 — Блок-схема MOSFET-модуля
# ═════════════════════════════════════════════════════════════════════════════
def fig_mosfet_module():
    W, H = 960, 500
    path = os.path.join(OUT, "fig-25-5c-1-mosfet-module.svg")

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 30, "Блок-схема MOSFET-модуля: що між ніжкою і навантаженням",
                      size=16, color=INK, anchor="middle", bold=True))

    # ── Дві зони: логічна і силова ──────────────────────────────────────────
    # Логічна зона (ліва): x=30..540, y=60..370
    frags.append(rect(30, 58, 510, 315, fill=LBLUE, stroke=BLUE, sw=2, rx=14))
    frags.append(text(285, 82, "ЛОГІЧНИЙ БІК  (мікроампери до затвора)",
                      size=12, color=BLUE, anchor="middle", bold=True))

    # Силова зона (права): x=550..930, y=60..370
    frags.append(rect(548, 58, 382, 315, fill=LRED, stroke=RED, sw=2, rx=14))
    frags.append(text(739, 82, "СИЛОВИЙ БІК  (повний струм навантаження)",
                      size=12, color=RED, anchor="middle", bold=True))

    # ── Блок: ніжка МК / IN ──────────────────────────────────────────────────
    box_mcu, bw_mcu, bh_mcu = textbox(100, 200, "ніжка МК\nШІМ-сигнал", size=13,
                                       fill=LAMB, stroke=GOLD, bold=True, min_w=110)
    frags.append(box_mcu)
    frags.append(text(100, 200 + bh_mcu / 2 + 16, "IN / SIG", size=10, color=GREY,
                       anchor="middle"))

    # ── Затворний резистор Rg ───────────────────────────────────────────────
    rg_cx = 230
    rg_cy = 200
    rg_w, rg_h = 78, 36
    frags.append(rect(rg_cx - rg_w / 2, rg_cy - rg_h / 2, rg_w, rg_h,
                      fill=LGRN, stroke=GREEN, sw=2, rx=6))
    frags.append(text(rg_cx, rg_cy - 2, "Rg", size=14, color=GREEN, anchor="middle", bold=True))
    frags.append(text(rg_cx, rg_cy + 14, "47 … 220 Ω", size=9, color=GREEN, anchor="middle"))
    frags.append(text(rg_cx, rg_cy + rg_h / 2 + 16,
                      "обмежує піковий\nструм фронту", size=9, color=GREY, anchor="middle"))

    # ── Підтяжка Rgs (від затвора до GND) ───────────────────────────────────
    # вертикально під лінією затвора
    rgs_cx = 340
    rgs_cy = 280
    rgs_w, rgs_h = 80, 34
    frags.append(rect(rgs_cx - rgs_w / 2, rgs_cy - rgs_h / 2, rgs_w, rgs_h,
                      fill=LORANGE, stroke=ORANGE, sw=2, rx=6))
    frags.append(text(rgs_cx, rgs_cy - 2, "Rgs", size=14, color=ORANGE,
                      anchor="middle", bold=True))
    frags.append(text(rgs_cx, rgs_cy + 14, "~10 kΩ", size=9, color=ORANGE, anchor="middle"))
    frags.append(text(rgs_cx, rgs_cy + rgs_h / 2 + 16,
                      "тримає ключ закритим\nпри старті / Z-стані", size=9,
                      color=GREY, anchor="middle"))

    # ── MOSFET (в центрі межі між зонами) ───────────────────────────────────
    mos_cx = 549
    mos_cy = 200
    mos_w, mos_h = 90, 72
    frags.append(rect(mos_cx - mos_w / 2, mos_cy - mos_h / 2, mos_w, mos_h,
                      fill=LPURP, stroke=PURPLE, sw=2.5, rx=10))
    frags.append(text(mos_cx, mos_cy - 10, "MOSFET", size=13, color=PURPLE,
                      anchor="middle", bold=True))
    frags.append(text(mos_cx, mos_cy + 8, "N-канальний", size=10, color=PURPLE,
                      anchor="middle"))
    frags.append(text(mos_cx, mos_cy + 22, "логічний", size=10, color=PURPLE,
                      anchor="middle"))
    # стрілка «G» (затвор)
    frags.append(text(mos_cx - mos_w / 2 - 14, mos_cy + 5, "G", size=11,
                      color=GREEN, anchor="middle", bold=True))
    # стрілки D/S
    frags.append(text(mos_cx, mos_cy - mos_h / 2 - 12, "D (стік)", size=10,
                      color=RED, anchor="middle"))
    frags.append(text(mos_cx, mos_cy + mos_h / 2 + 14, "S (витік) → GND сили",
                      size=10, color=RED, anchor="middle"))

    # ── Навантаження ─────────────────────────────────────────────────────────
    nav_cx = 730
    nav_cy = 200
    nav_box, nav_bw, nav_bh = textbox(nav_cx, nav_cy, "НАВАНТАЖЕННЯ\n(мотор / LED /\nсоленоїд)",
                                       size=13, fill=LRED, stroke=RED, bold=False, min_w=140)
    frags.append(nav_box)

    # ── Клема V+ (живлення сили) ─────────────────────────────────────────────
    vp_cx = 860
    vp_cy = 120
    vp_box, vp_bw, vp_bh = textbox(vp_cx, vp_cy, "V+\nживлення\nсили", size=12,
                                    fill="#fdecea", stroke=RED, bold=True, min_w=80)
    frags.append(vp_box)

    # ── GND спільна (внизу) ──────────────────────────────────────────────────
    gnd_cx = 549
    gnd_cy = 420
    gnd_box, gnd_bw, gnd_bh = textbox(gnd_cx, gnd_cy,
                                       "GND  (спільна — логіки + сили!)", size=12,
                                       fill="#e8f5e9", stroke=GREEN, bold=True, min_w=280)
    frags.append(gnd_box)

    # ── З'єднувальні лінії ───────────────────────────────────────────────────

    # ніжка → Rg
    frags.append(line(100 + bw_mcu / 2, 200, rg_cx - rg_w / 2, 200, color=GOLD, sw=2.5))
    # Rg → MOSFET G
    frags.append(line(rg_cx + rg_w / 2, 200, mos_cx - mos_w / 2, 200, color=GREEN, sw=2.5))

    # Rgs: від точки між Rg та затвором, вниз до GND-рамки
    rgs_x_attach = 340
    frags.append(line(rgs_x_attach, 200, rgs_x_attach, rgs_cy - rgs_h / 2, color=ORANGE, sw=2))
    frags.append(line(rgs_x_attach, rgs_cy + rgs_h / 2, rgs_x_attach, gnd_cy - gnd_bh / 2,
                      color=ORANGE, sw=2, dash="5,4"))

    # V+ → навантаження (зверху)
    frags.append(line(vp_cx, vp_cy + vp_bh / 2, vp_cx, nav_cy - nav_bh / 2,
                      color=RED, sw=2.5))
    frags.append(line(nav_cx + nav_bw / 2, nav_cy, vp_cx, nav_cy, color=RED, sw=2))

    # навантаження → MOSFET D (зверху)
    frags.append(line(nav_cx - nav_bw / 2, nav_cy, mos_cx, nav_cy, color=RED, sw=2.5))
    frags.append(line(mos_cx, nav_cy, mos_cx, mos_cy - mos_h / 2, color=RED, sw=2.5))

    # MOSFET S → GND
    frags.append(line(mos_cx, mos_cy + mos_h / 2, mos_cx, gnd_cy - gnd_bh / 2,
                      color=RED, sw=2.5))

    # ── Підписи потоку ────────────────────────────────────────────────────────
    frags.append(text(165, 185, "ШІМ-сигнал", size=9, color=GOLD, anchor="middle"))
    frags.append(text(430, 185, "V_GS — заряджає\nємність затвора", size=9,
                      color=GREEN, anchor="middle"))
    frags.append(text(730, 145, "I_load", size=11, color=RED, anchor="middle", bold=True))

    # ── Підказка-рамка внизу ─────────────────────────────────────────────────
    note_box, nw, nh = textbox(W // 2, 468,
        "Ніжка МК лише заряджає ємність затвора (мікроампери при фронті); "
        "весь струм навантаження тягнуть силові клеми з окремого живлення (§4.7.5).",
        size=11, fill=LAMB, stroke=GOLD, color=INK, min_w=860)
    frags.append(note_box)

    render(path, W, H, *frags)
    print("wrote", os.path.basename(path))


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.5c.2 — Чому потрібен «логічний» MOSFET (поріг затвора)
# ═════════════════════════════════════════════════════════════════════════════
def fig_gate_threshold():
    W, H = 860, 440
    path = os.path.join(OUT, "fig-25-5c-2-gate-threshold.svg")

    frags = []

    # Заголовок
    frags.append(text(W // 2, 28, "Чому потрібен «логічний» MOSFET: поріг затвора V_GS(th)",
                      size=15, color=INK, anchor="middle", bold=True))

    # ── Вісі графіка ─────────────────────────────────────────────────────────
    PX, PY = 80, 58
    PW, PH = 640, 310

    # фон
    frags.append(rect(PX, PY, PW, PH, fill="#f9f9f9", stroke=LINE, sw=1.2, rx=6))

    # вісь X
    frags.append(f'<line x1="{PX}" y1="{PY+PH}" x2="{PX+PW+18}" y2="{PY+PH}" '
                 f'stroke="{LINE}" stroke-width="2" marker-end="url(#arrow)"/>')
    frags.append(text(PX + PW + 24, PY + PH + 5, "V_GS, В", size=12, color=INK,
                       anchor="start", bold=True))

    # вісь Y
    frags.append(f'<line x1="{PX}" y1="{PY+PH}" x2="{PX}" y2="{PY-18}" '
                 f'stroke="{LINE}" stroke-width="2" marker-end="url(#arrow)"/>')
    frags.append(text(PX, PY - 22, "I_D, А", size=12, color=INK, anchor="middle", bold=True))

    # ── Маштаб: X від 0 до 12 В; Y від 0 до I_max ────────────────────────────
    VGS_MAX = 12.0
    I_MAX = 10.0   # умовна шкала (відносна)

    def mx(v):
        return PX + (v / VGS_MAX) * PW

    def my(i):
        return PY + PH - (i / I_MAX) * PH

    # ── Крива звичайного MOSFET (поріг ~4 В, повне відкриття ~10–12 В) ───────
    # Апроксимація: I_D = 0 при V < 4; квадратична від 4 до 12
    def i_normal(v):
        th = 4.0
        if v < th:
            return 0.0
        return min(I_MAX, ((v - th) / (10.0 - th)) ** 1.6 * I_MAX)

    pts_norm = []
    for vv in [i * 0.1 for i in range(0, 121)]:
        pts_norm.append((mx(vv), my(i_normal(vv))))
    poly_norm = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_norm)
    frags.append(f'<polyline points="{poly_norm}" fill="none" stroke="{RED}" '
                 f'stroke-width="2.5" stroke-linejoin="round"/>')

    # ── Крива логічного MOSFET (поріг ~1.5 В, повне відкриття ~3–4.5 В) ─────
    def i_logic(v):
        th = 1.5
        if v < th:
            return 0.0
        return min(I_MAX, ((v - th) / (3.5 - th)) ** 1.6 * I_MAX)

    pts_log = []
    for vv in [i * 0.1 for i in range(0, 121)]:
        pts_log.append((mx(vv), my(i_logic(vv))))
    poly_log = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_log)
    frags.append(f'<polyline points="{poly_log}" fill="none" stroke="{BLUE}" '
                 f'stroke-width="2.5" stroke-linejoin="round"/>')

    # ── Вертикаль 3.3 В (ESP32) ──────────────────────────────────────────────
    x33 = mx(3.3)
    frags.append(line(x33, PY, x33, PY + PH, color=GREEN, sw=2, dash="6,4"))
    frags.append(text(x33, PY - 10, "3.3 В (ESP32)", size=10, color=GREEN, anchor="middle", bold=True))

    # ── Вертикаль 10 В (звичайний) ───────────────────────────────────────────
    x10 = mx(10.0)
    frags.append(line(x10, PY, x10, PY + PH, color=RED, sw=1.5, dash="4,4"))
    frags.append(text(x10, PY - 10, "10 В", size=10, color=RED, anchor="middle"))

    # ── Точки @ 3.3 В ────────────────────────────────────────────────────────
    i_log_33 = i_logic(3.3)
    i_nor_33 = i_normal(3.3)

    y_log33 = my(i_log_33)
    y_nor33 = my(i_nor_33)

    frags.append(circle(x33, y_log33, 7, fill=LBLUE, stroke=BLUE, sw=2))
    frags.append(circle(x33, y_nor33, 7, fill=LRED, stroke=RED, sw=2))

    # Підписи точок
    frags.append(text(x33 + 50, y_log33 - 8,
                      f"логічний @ 3.3 В → повне відкриття", size=10, color=BLUE, anchor="start"))
    frags.append(text(x33 + 50, y_nor33 + 14,
                      f"звичайний @ 3.3 В → майже закритий (великий R_DS!)", size=10,
                      color=RED, anchor="start"))

    # ── Позначки осі X ───────────────────────────────────────────────────────
    for v, lbl in [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10"), (12, "12")]:
        xv = mx(v)
        frags.append(line(xv, PY + PH, xv, PY + PH + 5, color=GREY, sw=1))
        frags.append(text(xv, PY + PH + 17, lbl, size=10, color=GREY, anchor="middle"))

    # ── Легенда ───────────────────────────────────────────────────────────────
    leg_x, leg_y = PX + PW - 310, PY + PH - 130
    frags.append(rect(leg_x, leg_y, 310, 70, fill=BG, stroke=LINE, sw=1, rx=6))
    frags.append(line(leg_x + 14, leg_y + 20, leg_x + 44, leg_y + 20, color=BLUE, sw=2.5))
    frags.append(text(leg_x + 54, leg_y + 24, "Логічний MOSFET (IRLZ44 / AOD-клас)",
                      size=10, color=BLUE, anchor="start"))
    frags.append(line(leg_x + 14, leg_y + 46, leg_x + 44, leg_y + 46, color=RED, sw=2.5))
    frags.append(text(leg_x + 54, leg_y + 50, "Звичайний MOSFET (IRF520-клас)",
                      size=10, color=RED, anchor="start"))

    # ── Підказка-рамка внизу ─────────────────────────────────────────────────
    note_box, nw, nh = textbox(W // 2, H - 32,
        "При 3.3 В ESP32 звичайний MOSFET ледь відкритий → великий R_DS(on) → перегрів (§1.3.6).\n"
        "Логічний (logic-level) повністю відкритий від 3.3–4.5 В — холодний ключ прямо з ніжки.",
        size=11, fill=LAMB, stroke=GOLD, color=INK, min_w=800)
    frags.append(note_box)

    render(path, W, H, *frags)
    print("wrote", os.path.basename(path))


# ─── main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_mosfet_module()
    fig_gate_threshold()
    print("Done.")
