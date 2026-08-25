# -*- coding: utf-8 -*-
"""Фігури до статті «Власна резонансна частота пасивних компонентів (SRF)»
(book/electronics/components/self-resonant-frequency).

Фігури статті та вставок:
  model-cap-ind.svg      — еквівалентні схеми реального конденсатора (ESL+ESR+C) та котушки (L+R || C_p)
  srf-cap-curve.svg      — залежність |Z(f)| та фази реального конденсатора (V-крива, мінімум на SRF, інверсія)
  srf-inductor-curve.svg — залежність |Z(f)| та фази реальної котушки (пік антирезонансу, інверсія в ємність)
  antiresonance-pdn.svg  — антирезонансний пік при паралельному з'єднанні двох конденсаторів різного номіналу
  smd-geometry-srf.svg   — геометрія корпусів SMD (0805, 0402, reverse 0306) та паразитна індуктивність монтажу

Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Схемні помічники ────────────────────────────────────────────────────────
def cap_sym(cx, cy, label=None, col=NEG, vert=False):
    g = 6
    out = []
    if not vert:
        out.append(line(cx - 20, cy, cx - g, cy, color=col, sw=1.8))
        out.append(line(cx - g, cy - 14, cx - g, cy + 14, color=col, sw=2.5))
        out.append(line(cx + g, cy - 14, cx + g, cy + 14, color=col, sw=2.5))
        out.append(line(cx + g, cy, cx + 20, cy, color=col, sw=1.8))
        if label:
            out.append(text(cx, cy - 18, label, size=12, color=col, bold=True))
    else:
        out.append(line(cx, cy - 20, cx, cy - g, color=col, sw=1.8))
        out.append(line(cx - 14, cy - g, cx + 14, cy - g, color=col, sw=2.5))
        out.append(line(cx - 14, cy + g, cx + 14, cy + g, color=col, sw=2.5))
        out.append(line(cx, cy + g, cx, cy + 20, color=col, sw=1.8))
        if label:
            out.append(text(cx + 22, cy + 4, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def res_sym(cx, cy, label=None, col=POS, vert=False):
    out = []
    if not vert:
        x0, x1 = cx - 20, cx + 20
        n = 5
        seg = (x1 - x0) / (n + 2)
        amp = 6
        out.append(line(x0, cy, x0 + seg, cy, color=col, sw=1.8))
        xx = x0 + seg
        for i in range(n):
            ny = cy + (amp if i % 2 == 0 else -amp)
            prev_y = cy if i == 0 else (cy - amp if i % 2 == 1 else cy + amp)
            out.append(line(xx, prev_y, xx + seg, ny, color=col, sw=1.8))
            xx += seg
        out.append(line(xx, cy + (amp if (n - 1) % 2 == 0 else -amp), xx + seg, cy, color=col, sw=1.8))
        out.append(line(x1 - seg, cy, x1, cy, color=col, sw=1.8))
        if label:
            out.append(text(cx, cy - 14, label, size=12, color=col, bold=True))
    else:
        y0, y1 = cy - 20, cy + 20
        n = 5
        seg = (y1 - y0) / (n + 2)
        amp = 6
        out.append(line(cx, y0, cx, y0 + seg, color=col, sw=1.8))
        yy = y0 + seg
        for i in range(n):
            nx = cx + (amp if i % 2 == 0 else -amp)
            prev_x = cx if i == 0 else (cx - amp if i % 2 == 1 else cx + amp)
            out.append(line(prev_x, yy, nx, yy + seg, color=col, sw=1.8))
            yy += seg
        out.append(line(cx + (amp if (n - 1) % 2 == 0 else -amp), yy, cx, yy + seg, color=col, sw=1.8))
        out.append(line(cx, y1 - seg, cx, y1, color=col, sw=1.8))
        if label:
            out.append(text(cx + 18, cy + 4, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def coil_sym(cx, cy, label=None, col=FIELD, vert=False):
    out = []
    if not vert:
        x0 = cx - 20
        r = 4.5
        out.append(line(x0, cy, x0 + 2, cy, color=col, sw=1.8))
        bx = x0 + 2
        for i in range(4):
            out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                       'fill="none" stroke="%s" stroke-width="1.8"/>'
                       % (bx, cy, r, r, bx + 2 * r, cy, col))
            bx += 2 * r
        out.append(line(bx, cy, cx + 20, cy, color=col, sw=1.8))
        if label:
            out.append(text(cx, cy - 14, label, size=12, color=col, bold=True))
    else:
        y0 = cy - 20
        r = 4.5
        out.append(line(cx, y0, cx, y0 + 2, color=col, sw=1.8))
        by = y0 + 2
        for i in range(4):
            out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                       'fill="none" stroke="%s" stroke-width="1.8"/>'
                       % (cx, by, r, r, cx, by + 2 * r, col))
            by += 2 * r
        out.append(line(cx, by, cx, cy + 20, color=col, sw=1.8))
        if label:
            out.append(text(cx + 18, cy + 4, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. model-cap-ind.svg — еквівалентні схеми реальних компонентів
# ════════════════════════════════════════════════════════════════════════════
def fig_model_cap_ind():
    W, H = 740, 310
    f = []

    # Ліва половина: Конденсатор
    bx1, by1, bw1, bh1 = 25, 45, 330, 240
    f.append(rect(bx1, by1, bw1, bh1, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(bx1 + bw1 / 2, by1 + 24, "Реальний конденсатор", size=15, bold=True))
    f.append(text(bx1 + bw1 / 2, by1 + 44, "Послідовна RLC-модель", size=12, color=MUTED))

    yc1 = by1 + 105
    f.append(line(45, yc1, 75, yc1, color=INK, sw=1.8))
    f.append(circle(45, yc1, 3.5, fill=INK, stroke=INK))
    f.append(text(45, yc1 + 18, "Вхід", size=11, color=MUTED))

    f.append(coil_sym(105, yc1, label="ESL", col=FIELD))
    f.append(line(125, yc1, 155, yc1, color=INK, sw=1.8))
    f.append(res_sym(185, yc1, label="ESR", col=POS))
    f.append(line(205, yc1, 235, yc1, color=INK, sw=1.8))
    f.append(cap_sym(265, yc1, label="C", col=NEG))
    f.append(line(285, yc1, 335, yc1, color=INK, sw=1.8))
    f.append(circle(335, yc1, 3.5, fill=INK, stroke=INK))
    f.append(text(335, yc1 + 18, "Вихід", size=11, color=MUTED))

    tb_c = [
        "• C: номінальна ємність",
        "• ESR: опір обкладок і втрат діелектрика",
        "• ESL: індуктивність виводів та геометрії"
    ]
    f.append(mtext(bx1 + 16, by1 + 160, tb_c, size=11, color=INK, anchor="start", lh=1.4))

    # Права половина: Котушка індуктивності
    bx2, by2, bw2, bh2 = 385, 45, 330, 240
    f.append(rect(bx2, by2, bw2, bh2, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(bx2 + bw2 / 2, by2 + 24, "Реальна котушка індуктивності", size=15, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 44, "Паралельна RLC-модель", size=12, color=MUTED))

    yc2_mid = by2 + 105
    yc2_top = yc2_mid - 32
    yc2_bot = yc2_mid + 32

    f.append(line(405, yc2_mid, 435, yc2_mid, color=INK, sw=1.8))
    f.append(circle(405, yc2_mid, 3.5, fill=INK, stroke=INK))
    f.append(text(405, yc2_mid + 18, "Вхід", size=11, color=MUTED))

    f.append(line(435, yc2_top, 435, yc2_bot, color=INK, sw=1.8))
    f.append(circle(435, yc2_mid, 2.5, fill=INK, stroke=INK))

    f.append(line(435, yc2_top, 525, yc2_top, color=INK, sw=1.8))
    f.append(cap_sym(550, yc2_top, label="C_p", col=NEG))
    f.append(line(570, yc2_top, 665, yc2_top, color=INK, sw=1.8))

    f.append(line(435, yc2_bot, 475, yc2_bot, color=INK, sw=1.8))
    f.append(coil_sym(500, yc2_bot, label="L", col=FIELD))
    f.append(line(520, yc2_bot, 570, yc2_bot, color=INK, sw=1.8))
    f.append(res_sym(595, yc2_bot, label="R_s (DCR)", col=POS))
    f.append(line(615, yc2_bot, 665, yc2_bot, color=INK, sw=1.8))

    f.append(line(665, yc2_top, 665, yc2_bot, color=INK, sw=1.8))
    f.append(circle(665, yc2_mid, 2.5, fill=INK, stroke=INK))
    f.append(line(665, yc2_mid, 695, yc2_mid, color=INK, sw=1.8))
    f.append(circle(695, yc2_mid, 3.5, fill=INK, stroke=INK))
    f.append(text(695, yc2_mid + 18, "Вихід", size=11, color=MUTED))

    tb_l = [
        "• L: номінальна індуктивність",
        "• R_s: опір проводу постійний (DCR) і змінний (ACR)",
        "• C_p: міжвиткова й міжшарова ємність"
    ]
    f.append(mtext(bx2 + 16, by2 + 160, tb_l, size=11, color=INK, anchor="start", lh=1.4))

    render(os.path.join(IMG, 'model-cap-ind.svg'), W, H, *f, title=None)


# ════════════════════════════════════════════════════════════════════════════
# 2. srf-cap-curve.svg — V-подібний імпеданс конденсатора та фаза
# ════════════════════════════════════════════════════════════════════════════
def fig_srf_cap_curve():
    W, H = 720, 390
    f = []

    f.append(text(W / 2, 24, "Частотна характеристика імпедансу конденсатора", size=16, bold=True))

    gx, gy, gw, gh = 80, 50, 580, 200
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=4))

    xs = [gx + gw * 0.2, gx + gw * 0.5, gx + gw * 0.8]
    ys = [gy + gh * 0.2, gy + gh * 0.5, gy + gh * 0.8]

    for x in xs:
        f.append(line(x, gy, x, gy + gh, color="#eef0f2", sw=1.0, dash="3 3"))
    for y in ys:
        f.append(line(gx, y, gx + gw, y, color="#eef0f2", sw=1.0, dash="3 3"))

    f.append(arrow(gx, gy + gh, gx + gw + 15, gy + gh, color=INK, sw=1.6))
    f.append(text(gx + gw + 10, gy + gh + 18, "Частота f (log)", size=12, color=INK, bold=True, anchor="end"))

    f.append(arrow(gx, gy + gh, gx, gy - 12, color=INK, sw=1.6))
    f.append(text(gx - 10, gy - 4, "|Z| (log)", size=12, color=INK, bold=True, anchor="end"))

    x_srf = gx + gw * 0.5
    y_min = gy + gh * 0.82   # ESR рівень

    # V-крива
    p_cap = "M %d %d L %d %d Q %d %d %d %d" % (gx + 30, gy + 30, x_srf - 40, y_min - 15, x_srf, y_min, x_srf + 40, y_min - 15)
    p_ind = "L %d %d" % (gx + gw - 30, gy + 30)
    f.append('<path d="%s %s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p_cap, p_ind, NEG))

    # Точка SRF
    f.append(circle(x_srf, y_min, 5, fill=POS, stroke=POS))
    f.append(line(x_srf, y_min, x_srf, gy + gh, color=POS, sw=1.4, dash="3 3"))
    f.append(text(x_srf, gy + gh + 18, "f_SRF", size=13, color=POS, bold=True))

    # Рівень ESR
    f.append(line(gx, y_min, x_srf, y_min, color=POS, sw=1.4, dash="3 3"))
    f.append(text(gx - 8, y_min + 4, "|Z| = ESR", size=11, color=POS, bold=True, anchor="end"))

    # Підписи зон на вільному місці вгорі графіка
    f.append(rect(gx + 15, gy + 15, 150, 42, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=5))
    f.append(text(gx + 90, gy + 32, "ЄМНІСНА ЗОНА", size=10, color=NEG, bold=True))
    f.append(text(gx + 90, gy + 47, "|Z| ∝ 1/f (−20 дБ/дек)", size=9, color=MUTED))

    f.append(rect(gx + gw - 165, gy + 15, 150, 42, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    f.append(text(gx + gw - 90, gy + 32, "ІНДУКТИВНА ЗОНА", size=10, color=POS, bold=True))
    f.append(text(gx + gw - 90, gy + 47, "|Z| ∝ f (+20 дБ/дек)", size=9, color=MUTED))

    # Графік фази arg(Z) знизу
    py, ph = 295, 75
    f.append(rect(gx, py, gw, ph, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=4))
    f.append(line(gx, py + ph / 2, gx + gw, py + ph / 2, color="#c0c4cc", sw=1.2))

    f.append(text(gx - 8, py + 14, "+90°", size=10, color=MUTED, anchor="end"))
    f.append(text(gx - 8, py + ph / 2 + 4, "0°", size=10, color=INK, bold=True, anchor="end"))
    f.append(text(gx - 8, py + ph - 6, "−90°", size=10, color=MUTED, anchor="end"))

    phase_d = "M %d %d C %d %d %d %d %d %d" % (
        gx + 30, py + ph - 8,
        x_srf - 30, py + ph - 8,
        x_srf - 20, py + ph / 2,
        x_srf, py + ph / 2
    )
    phase_d2 = "C %d %d %d %d %d %d" % (
        x_srf + 20, py + ph / 2,
        x_srf + 30, py + 8,
        gx + gw - 30, py + 8
    )
    f.append('<path d="%s %s" fill="none" stroke="%s" stroke-width="2.2"/>' % (phase_d, phase_d2, FIELD))
    f.append(circle(x_srf, py + ph / 2, 4, fill=POS, stroke=POS))
    f.append(line(x_srf, py, x_srf, py + ph, color=POS, sw=1.2, dash="3 3"))

    f.append(text(gx + 120, py + ph - 14, "Фаза ≈ −90° (ємність)", size=10, color=MUTED))
    f.append(text(gx + gw - 130, py + 20, "Фаза ≈ +90° (індуктивність)", size=10, color=MUTED))
    f.append(text(x_srf + 8, py + ph / 2 - 8, "Чисто активний опір (0°)", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, 'srf-cap-curve.svg'), W, H, *f, title=None)


# ════════════════════════════════════════════════════════════════════════════
# 3. srf-inductor-curve.svg — імпеданс котушки: пік антирезонансу та інверсія
# ════════════════════════════════════════════════════════════════════════════
def fig_srf_inductor_curve():
    W, H = 720, 390
    f = []

    f.append(text(W / 2, 24, "Частотна характеристика імпедансу котушки (дроселя)", size=16, bold=True))

    gx, gy, gw, gh = 80, 50, 580, 200
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=4))

    for x in [gx + gw * 0.2, gx + gw * 0.5, gx + gw * 0.8]:
        f.append(line(x, gy, x, gy + gh, color="#eef0f2", sw=1.0, dash="3 3"))
    for y in [gy + gh * 0.2, gy + gh * 0.5, gy + gh * 0.8]:
        f.append(line(gx, y, gx + gw, y, color="#eef0f2", sw=1.0, dash="3 3"))

    f.append(arrow(gx, gy + gh, gx + gw + 15, gy + gh, color=INK, sw=1.6))
    f.append(text(gx + gw + 10, gy + gh + 18, "Частота f (log)", size=12, color=INK, bold=True, anchor="end"))

    f.append(arrow(gx, gy + gh, gx, gy - 12, color=INK, sw=1.6))
    f.append(text(gx - 10, gy - 4, "|Z| (log)", size=12, color=INK, bold=True, anchor="end"))

    x_srf = gx + gw * 0.5
    y_peak = gy + 35
    y_dcr = gy + gh * 0.82

    p_ind = "M %d %d L %d %d L %d %d Q %d %d %d %d" % (
        gx + 30, y_dcr,
        gx + 90, y_dcr,
        x_srf - 40, y_peak + 20,
        x_srf, y_peak,
        x_srf + 40, y_peak + 20
    )
    p_cap = "L %d %d" % (gx + gw - 30, gy + gh * 0.82)
    f.append('<path d="%s %s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p_ind, p_cap, FIELD))

    f.append(circle(x_srf, y_peak, 5, fill=POS, stroke=POS))
    f.append(line(x_srf, y_peak, x_srf, gy + gh, color=POS, sw=1.4, dash="3 3"))
    f.append(text(x_srf, gy + gh + 18, "f_SRF", size=13, color=POS, bold=True))

    f.append(line(gx, y_peak, x_srf, y_peak, color=POS, sw=1.4, dash="3 3"))
    f.append(text(gx - 8, y_peak + 4, "|Z_max| ≈ Q·√(L/C_p)", size=11, color=POS, bold=True, anchor="end"))

    f.append(line(gx, y_dcr, gx + 90, y_dcr, color=MUTED, sw=1.4, dash="3 3"))
    f.append(text(gx - 8, y_dcr + 4, "DCR", size=11, color=MUTED, bold=True, anchor="end"))

    # Підписи зон у вільних нижніх кутах
    f.append(rect(gx + 105, gy + 120, 150, 42, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    f.append(text(gx + 180, gy + 137, "ІНДУКТИВНА ЗОНА", size=10, color=POS, bold=True))
    f.append(text(gx + 180, gy + 152, "Блокує ВЧ-струм (+20 дБ)", size=9, color=MUTED))

    f.append(rect(gx + gw - 165, gy + 120, 150, 42, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=5))
    f.append(text(gx + gw - 90, gy + 137, "ЄМНІСНА ЗОНА", size=10, color=NEG, bold=True))
    f.append(text(gx + gw - 90, gy + 152, "Завада йде крізь C_p", size=9, color=MUTED))

    # Графік фази arg(Z) знизу
    py, ph = 295, 75
    f.append(rect(gx, py, gw, ph, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=4))
    f.append(line(gx, py + ph / 2, gx + gw, py + ph / 2, color="#c0c4cc", sw=1.2))

    f.append(text(gx - 8, py + 14, "+90°", size=10, color=MUTED, anchor="end"))
    f.append(text(gx - 8, py + ph / 2 + 4, "0°", size=10, color=INK, bold=True, anchor="end"))
    f.append(text(gx - 8, py + ph - 6, "−90°", size=10, color=MUTED, anchor="end"))

    phase_d = "M %d %d C %d %d %d %d %d %d" % (
        gx + 90, py + 8,
        x_srf - 30, py + 8,
        x_srf - 20, py + ph / 2,
        x_srf, py + ph / 2
    )
    phase_d2 = "C %d %d %d %d %d %d" % (
        x_srf + 20, py + ph / 2,
        x_srf + 30, py + ph - 8,
        gx + gw - 30, py + ph - 8
    )
    f.append('<path d="%s %s" fill="none" stroke="%s" stroke-width="2.2"/>' % (phase_d, phase_d2, FIELD))
    f.append(circle(x_srf, py + ph / 2, 4, fill=POS, stroke=POS))
    f.append(line(x_srf, py, x_srf, py + ph, color=POS, sw=1.2, dash="3 3"))

    f.append(text(gx + 130, py + 20, "Фаза ≈ +90° (індуктивність)", size=10, color=MUTED))
    f.append(text(gx + gw - 130, py + ph - 14, "Фаза ≈ −90° (ємність C_p)", size=10, color=MUTED))
    f.append(text(x_srf + 8, py + ph / 2 - 8, "Антирезонанс (0°)", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, 'srf-inductor-curve.svg'), W, H, *f, title=None)


# ════════════════════════════════════════════════════════════════════════════
# 4. antiresonance-pdn.svg — антирезонансний пік при паралельному з'єднанні
# ════════════════════════════════════════════════════════════════════════════
def fig_antiresonance_pdn():
    W, H = 740, 360
    f = []

    f.append(text(W / 2, 24, "Пастка декуплінгу: антирезонанс двох паралельних конденсаторів", size=16, bold=True))

    gx, gy, gw, gh = 80, 50, 600, 260
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=4))

    f.append(arrow(gx, gy + gh, gx + gw + 15, gy + gh, color=INK, sw=1.6))
    f.append(text(gx + gw + 10, gy + gh + 18, "Частота f (log)", size=12, color=INK, bold=True, anchor="end"))

    f.append(arrow(gx, gy + gh, gx, gy - 12, color=INK, sw=1.6))
    f.append(text(gx - 10, gy - 4, "|Z_PDN| (log)", size=12, color=INK, bold=True, anchor="end"))

    x_srf1 = gx + gw * 0.28   # 80 + 168 = 248
    x_srf2 = gx + gw * 0.72   # 80 + 432 = 512
    x_anti = (x_srf1 + x_srf2) / 2 # 380

    y_bot1 = gy + gh * 0.80   # 258
    y_bot2 = gy + gh * 0.84   # 268
    y_anti_peak = gy + 55     # 105

    # Пунктир: C1 (10 мкФ) окремо
    p_c1 = "M %d %d L %d %d L %d %d" % (gx + 20, gy + 70, x_srf1, y_bot1, gx + gw - 80, gy + 30)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 4"/>' % (p_c1, MUTED))
    f.append(text(gx + 60, gy + 88, "C1 (10 мкФ)", size=11, color=MUTED))

    # Пунктир: C2 (100 нФ) окремо
    p_c2 = "M %d %d L %d %d L %d %d" % (gx + 120, gy + 30, x_srf2, y_bot2, gx + gw - 20, gy + 70)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 4"/>' % (p_c2, MUTED))
    f.append(text(gx + gw - 70, gy + 88, "C2 (100 нФ)", size=11, color=MUTED))

    # Сумарна жирна крива
    p_sum = "M %d %d L %d %d Q %d %d %d %d Q %d %d %d %d L %d %d" % (
        gx + 20, gy + 70,
        x_srf1 - 20, y_bot1 - 10,
        x_srf1, y_bot1 + 2,
        x_srf1 + 20, y_bot1 - 10,
        x_anti, y_anti_peak - 4,
        x_srf2 - 20, y_bot2 - 10,
        x_srf2 + 20, y_bot2 - 10
    )
    p_sum_end = "L %d %d" % (gx + gw - 20, gy + 70)
    f.append('<path d="%s %s" fill="none" stroke="%s" stroke-width="3.0"/>' % (p_sum, p_sum_end, POS))

    # Позначення мінімумів та піку
    f.append(circle(x_srf1, y_bot1, 4.5, fill=NEG, stroke=NEG))
    f.append(line(x_srf1, y_bot1, x_srf1, gy + gh, color=NEG, sw=1.2, dash="3 3"))
    f.append(text(x_srf1, gy + gh + 18, "SRF₁", size=12, color=NEG, bold=True))

    f.append(circle(x_srf2, y_bot2, 4.5, fill=NEG, stroke=NEG))
    f.append(line(x_srf2, y_bot2, x_srf2, gy + gh, color=NEG, sw=1.2, dash="3 3"))
    f.append(text(x_srf2, gy + gh + 18, "SRF₂", size=12, color=NEG, bold=True))

    f.append(circle(x_anti, y_anti_peak, 5.5, fill=POS, stroke=POS))
    f.append(line(x_anti, y_anti_peak, x_anti, gy + gh, color=POS, sw=1.4, dash="3 3"))
    f.append(text(x_anti, gy + gh + 18, "f_anti", size=12, color=POS, bold=True))

    # Пояснення антирезонансу — винесено зверху над піком
    f.append(rect(x_anti - 120, gy + 10, 240, 36, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    f.append(text(x_anti, gy + 26, "ПАРАЛЕЛЬНИЙ АНТИРЕЗОНАНС", size=10, color=POS, bold=True))
    f.append(text(x_anti, gy + 39, "ESL₁ резонує з C₂ → підскок |Z|!", size=9, color=POS))

    # Цільовий імпеданс Target Impedance
    y_target = gy + gh * 0.65
    f.append(line(gx, y_target, gx + gw, y_target, color=FIELD, sw=1.8, dash="6 3"))
    f.append(rect(gx + 12, y_target - 22, 175, 20, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    f.append(text(gx + 100, y_target - 8, "Цільовий імпеданс Z_target", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, 'antiresonance-pdn.svg'), W, H, *f, title=None)


# ════════════════════════════════════════════════════════════════════════════
# 5. smd-geometry-srf.svg — вплив геометрії корпусу та монтажу на ESL
# ════════════════════════════════════════════════════════════════════════════
def fig_smd_geometry_srf():
    W, H = 740, 270
    f = []

    f.append(text(W / 2, 22, "Геометрія корпусу SMD та паразитна індуктивність ESL", size=16, bold=True))

    boxes = [
        ("Стандартний 0805", "L = 2.0 мм, W = 1.25 мм", "ESL ≈ 1.0–1.2 нГн", "SRF (100 нФ) ≈ 15 МГц", 805, 40),
        ("Компактний 0402", "L = 1.0 мм, W = 0.5 мм", "ESL ≈ 0.4–0.5 нГн", "SRF (100 нФ) ≈ 25 МГц", 402, 215),
        ("Reverse-Geometry 0306", "Широкі виводи з боків", "ESL ≈ 0.15–0.2 нГн", "SRF (100 нФ) ≈ 40 МГц", 306, 390),
        ("Монтаж + Vias на платі", "Кожне перехідне +0.5 нГн", "Сумарний ESL > 2.0 нГн", "SRF падає вдвічі!", 9999, 565),
    ]

    for title_txt, sub1, esl_txt, srf_txt, code, x in boxes:
        w_box, h_box = 160, 205
        y_box = 45
        f.append(rect(x, y_box, w_box, h_box, fill="#fbfbfc", stroke="#d0d5dd", sw=1.4, rx=8))
        f.append(text(x + w_box / 2, y_box + 20, title_txt, size=12, bold=True))
        f.append(text(x + w_box / 2, y_box + 36, sub1, size=10, color=MUTED))

        # Малюнок чіпа
        cy_chip = y_box + 80
        cx_chip = x + w_box / 2

        if code == 805:
            f.append(rect(cx_chip - 35, cy_chip - 18, 70, 36, fill="#d2b48c", stroke=INK, sw=1.2, rx=3))
            f.append(rect(cx_chip - 35, cy_chip - 18, 14, 36, fill="#c0c4cc", stroke=INK, sw=1.2, rx=2))
            f.append(rect(cx_chip + 21, cy_chip - 18, 14, 36, fill="#c0c4cc", stroke=INK, sw=1.2, rx=2))
            f.append(arrow(cx_chip - 25, cy_chip, cx_chip + 25, cy_chip, color=POS, sw=1.5))
            f.append(text(cx_chip, cy_chip - 22, "довга петля струму", size=9, color=MUTED))
        elif code == 402:
            f.append(rect(cx_chip - 22, cy_chip - 12, 44, 24, fill="#d2b48c", stroke=INK, sw=1.2, rx=2))
            f.append(rect(cx_chip - 22, cy_chip - 12, 10, 24, fill="#c0c4cc", stroke=INK, sw=1.2, rx=1))
            f.append(rect(cx_chip + 12, cy_chip - 12, 10, 24, fill="#c0c4cc", stroke=INK, sw=1.2, rx=1))
            f.append(arrow(cx_chip - 15, cy_chip, cx_chip + 15, cy_chip, color=POS, sw=1.4))
            f.append(text(cx_chip, cy_chip - 16, "коротка петля", size=9, color=MUTED))
        elif code == 306:
            f.append(rect(cx_chip - 26, cy_chip - 16, 52, 32, fill="#d2b48c", stroke=INK, sw=1.2, rx=2))
            f.append(rect(cx_chip - 26, cy_chip - 16, 52, 9, fill="#c0c4cc", stroke=INK, sw=1.2, rx=1))
            f.append(rect(cx_chip - 26, cy_chip + 7, 52, 9, fill="#c0c4cc", stroke=INK, sw=1.2, rx=1))
            f.append(arrow(cx_chip, cy_chip - 10, cx_chip, cy_chip + 10, color=POS, sw=1.5))
            f.append(text(cx_chip, cy_chip - 20, "широкий фронт", size=9, color=FIELD, bold=True))
        else:
            f.append(rect(cx_chip - 25, cy_chip - 12, 50, 24, fill="#d2b48c", stroke=INK, sw=1.2, rx=2))
            f.append(line(cx_chip - 45, cy_chip, cx_chip - 25, cy_chip, color=POS, sw=1.8))
            f.append(line(cx_chip + 25, cy_chip, cx_chip + 45, cy_chip, color=POS, sw=1.8))
            f.append(circle(cx_chip - 48, cy_chip, 5, fill="#ffffff", stroke=POS, sw=1.8))
            f.append(circle(cx_chip + 48, cy_chip, 5, fill="#ffffff", stroke=POS, sw=1.8))
            f.append(text(cx_chip, cy_chip + 24, "Vias додають nH!", size=9, color=POS, bold=True))

        f.append(rect(x + 10, y_box + 122, w_box - 20, 32, fill="#ffffff", stroke="#eaecf0", sw=1.0, rx=4))
        f.append(text(x + w_box / 2, y_box + 142, esl_txt, size=11, color=POS, bold=True))

        f.append(rect(x + 10, y_box + 160, w_box - 20, 32, fill="#ffffff", stroke="#eaecf0", sw=1.0, rx=4))
        f.append(text(x + w_box / 2, y_box + 180, srf_txt, size=10, color=INK))

    render(os.path.join(IMG, 'smd-geometry-srf.svg'), W, H, *f, title=None)


if __name__ == '__main__':
    fig_model_cap_ind()
    fig_srf_cap_curve()
    fig_srf_inductor_curve()
    fig_antiresonance_pdn()
    fig_smd_geometry_srf()
    print("Всі фігури згенеровано успішно.")
