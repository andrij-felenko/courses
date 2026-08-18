# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Типи зонного вирівнювання (Тип I, Тип II, Тип II розірвана)
# ════════════════════════════════════════════════════════════════════════════
def fig_superlattice_types():
    W, H = 840, 420
    f = []

    f.append(text(420, 25, "Типи зонного вирівнювання у гетероструктурах та суперґратках", size=15, bold=True, color=INK))

    # Вертикальні роздільники
    f.append(line(280, 55, 280, 395, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(560, 55, 560, 395, color=MUTED, sw=1.2, dash="4 4"))

    # ── Панель 1: Тип I (Вкладена / GaAs/AlGaAs) ──
    f.append(text(140, 60, "Тип I (Вкладена)", size=14, bold=True, color=INK))
    f.append(text(140, 78, "наприклад, GaAs / AlGaAs", size=11, color=MUTED))

    ec1 = [(30, 130), (95, 130), (95, 190), (185, 190), (185, 130), (250, 130)]
    ev1 = [(30, 330), (95, 330), (95, 270), (185, 270), (185, 330), (250, 330)]

    path_ec1 = "M " + " L ".join("%.1f %.1f" % p for p in ec1)
    path_ev1 = "M " + " L ".join("%.1f %.1f" % p for p in ev1)

    f.append(rect(95, 190, 90, 80, fill="#eaf2f8", stroke="none"))
    f.append(svg_path(path_ec1, stroke=POS, sw=2.5))
    f.append(svg_path(path_ev1, stroke=NEG, sw=2.5))

    f.append(text(40, 120, "E_c", size=12, bold=True, color=POS))
    f.append(text(40, 345, "E_v", size=12, bold=True, color=NEG))

    f.append(circle(140, 215, 6, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(text(140, 212, "e⁻", size=10, color="#ffffff", bold=True))
    f.append(circle(140, 245, 6, fill=NEG, stroke="#1b4f72", sw=1.5))
    f.append(text(140, 243, "h⁺", size=10, color="#ffffff", bold=True))

    f.append(text(140, 375, "Обидва носії в одного матеріалі", size=11, color=INK))

    # ── Панель 2: Тип II (Зсунута / AlSb/InAs) ──
    f.append(text(420, 60, "Тип II (Зсунута)", size=14, bold=True, color=INK))
    f.append(text(420, 78, "наприклад, AlSb / InAs", size=11, color=MUTED))

    ec2 = [(310, 140), (375, 140), (375, 210), (465, 210), (465, 140), (530, 140)]
    ev2 = [(310, 260), (375, 260), (375, 340), (465, 340), (465, 260), (530, 260)]

    path_ec2 = "M " + " L ".join("%.1f %.1f" % p for p in ec2)
    path_ev2 = "M " + " L ".join("%.1f %.1f" % p for p in ev2)

    f.append(svg_path(path_ec2, stroke=POS, sw=2.5))
    f.append(svg_path(path_ev2, stroke=NEG, sw=2.5))

    f.append(circle(420, 230, 6, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(text(420, 227, "e⁻", size=10, color="#ffffff", bold=True))
    f.append(circle(345, 280, 6, fill=NEG, stroke="#1b4f72", sw=1.5))
    f.append(text(345, 278, "h⁺", size=10, color="#ffffff", bold=True))

    f.append(text(420, 375, "Просторова сепарація носіїв", size=11, color=INK))

    # ── Панель 3: Тип II Розірвана (Broken-gap / InAs/GaSb) ──
    f.append(text(700, 60, "Тип II (Розірвана)", size=14, bold=True, color=INK))
    f.append(text(700, 78, "наприклад, InAs / GaSb", size=11, color=MUTED))

    ec3 = [(590, 160), (655, 160), (655, 250), (745, 250), (745, 160), (810, 160)]
    ev3 = [(590, 210), (655, 210), (655, 330), (745, 330), (745, 210), (810, 210)]

    path_ec3 = "M " + " L ".join("%.1f %.1f" % p for p in ec3)
    path_ev3 = "M " + " L ".join("%.1f %.1f" % p for p in ev3)

    f.append(rect(655, 210, 90, 40, fill="#fadbd8", stroke="none"))
    f.append(svg_path(path_ec3, stroke=POS, sw=2.5))
    f.append(svg_path(path_ev3, stroke=NEG, sw=2.5))

    f.append(text(700, 232, "Перекриття E_c < E_v", size=10, bold=True, color="#78281f"))
    f.append(text(700, 375, "Самодопінг та напівметалевість", size=11, color=INK))

    render(os.path.join(OUT, "superlattice-types.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Утворення мінізон та мініщілин (Miniband formation)
# ════════════════════════════════════════════════════════════════════════════
def fig_miniband_formation():
    W, H = 840, 420
    f = []

    f.append(text(420, 25, "Формування мінізон та мініщілин у періодичному потенціалі", size=15, bold=True, color=INK))

    f.append(text(210, 60, "Ізольовані товсті ями (d₂ >> λ_dB)", size=13, bold=True, color=INK))

    pot1 = [(40, 100), (80, 100), (80, 300), (130, 300), (130, 100),
            (190, 100), (190, 300), (240, 300), (240, 100),
            (300, 100), (300, 300), (350, 300), (350, 100), (380, 100)]
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pot1), stroke=LINE, sw=2.0))

    for xw in [80, 190, 300]:
        f.append(line(xw, 250, xw + 50, 250, color=POS, sw=1.8, dash="3 2"))
        f.append(line(xw, 180, xw + 50, 180, color=POS, sw=1.8, dash="3 2"))

    f.append(text(50, 253, "E₁", size=11, bold=True, color=POS))
    f.append(text(50, 183, "E₂", size=11, bold=True, color=POS))
    f.append(text(210, 335, "Дискретні локалізовані рівні", size=11, color=MUTED))

    f.append(line(395, 200, 435, 200, color=FIELD, sw=2.5))
    f.append(polygon([(435, 195), (445, 200), (435, 205)], fill=FIELD))
    f.append(text(420, 180, "Тунелювання", size=11, bold=True, color=FIELD))
    f.append(text(420, 220, "d₂ ~ 2–5 нм", size=11, color=MUTED))

    f.append(text(640, 60, "Суперґратка: тунельне розщеплення в мінізони", size=13, bold=True, color=INK))

    pot2 = [(460, 100), (490, 100), (490, 300), (530, 300), (530, 100),
            (560, 100), (560, 300), (600, 300), (600, 100),
            (630, 100), (630, 300), (670, 300), (670, 100),
            (700, 100), (700, 300), (740, 300), (740, 100), (770, 100)]
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pot2), stroke=LINE, sw=2.0))

    f.append(rect(490, 240, 250, 25, fill="#d4efdf", stroke=FIELD, sw=1.5))
    f.append(text(615, 257, "Перша мінізона Δ₁", size=11, bold=True, color="#196f3d"))

    f.append(rect(490, 165, 250, 35, fill="#d4efdf", stroke=FIELD, sw=1.5))
    f.append(text(615, 187, "Друга мінізона Δ₂", size=11, bold=True, color="#196f3d"))

    f.append(line(750, 200, 750, 240, color=POS, sw=1.5))
    f.append(polygon([(747, 205), (750, 197), (753, 205)], fill=POS))
    f.append(polygon([(747, 235), (750, 243), (753, 235)], fill=POS))
    f.append(text(790, 223, "Мініщілина E_mg", size=11, bold=True, color=POS))

    f.append(line(490, 320, 560, 320, color=INK, sw=1.5))
    f.append(line(490, 315, 490, 325, color=INK, sw=1.5))
    f.append(line(560, 315, 560, 325, color=INK, sw=1.5))
    f.append(text(525, 340, "Період d = d₁ + d₂", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "miniband-formation.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Блохівські осциляції та Ванньє-Штарківська драбина
# ════════════════════════════════════════════════════════════════════════════
def fig_bloch_wannier_stark():
    W, H = 840, 420
    f = []

    f.append(text(420, 25, "Електрокондуктивність у сильному полі: Блохівські осциляції та Ванньє — Штарк", size=15, bold=True, color=INK))
    f.append(line(420, 55, 420, 395, color=MUTED, sw=1.2, dash="4 4"))

    f.append(text(210, 60, "Блохівські осциляції (k-простір)", size=14, bold=True, color=INK))

    pts_disp = []
    for deg in range(-180, 181, 5):
        rad = math.radians(deg)
        kx = 210 + (deg / 180.0) * 140
        ey = 200 - 60 * math.cos(rad)
        pts_disp.append((kx, ey))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_disp), stroke="#8e44ad", sw=2.5))

    f.append(line(70, 120, 70, 280, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(350, 120, 350, 280, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(70, 295, "−π/d", size=12, bold=True, color=MUTED))
    f.append(text(350, 295, "+π/d", size=12, bold=True, color=MUTED))

    f.append(arrow(140, 240, 280, 160, color=POS, sw=2.2))
    f.append(text(210, 150, "ħ (dk_z/dt) = −eF", size=11, bold=True, color=POS))
    f.append(text(210, 335, "Бреґґівське відбиття від межі зони", size=11, color=INK))
    f.append(text(210, 355, "Частота осциляцій ω_B = e F d / ħ", size=12, bold=True, color="#8e44ad"))

    f.append(text(630, 60, "Драбина Ванньє — Штарка (Реальний простір)", size=14, bold=True, color=INK))

    pot_tilt = [(450, 130), (480, 140), (480, 220), (520, 230), (520, 160),
                (550, 170), (550, 250), (590, 260), (590, 190),
                (620, 200), (620, 280), (660, 290), (660, 220),
                (690, 230), (690, 310), (730, 320), (730, 250), (760, 260)]
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pot_tilt), stroke=LINE, sw=1.8))

    levels = [(500, 190, "n = +1"), (570, 220, "n = 0"), (640, 250, "n = −1"), (710, 280, "n = −2")]
    for lx, ly, lbl in levels:
        f.append(line(lx - 30, ly, lx + 30, ly, color=POS, sw=2.0))
        f.append(text(lx, ly - 7, lbl, size=10, bold=True, color=POS))

    f.append(line(780, 220, 780, 250, color=NEG, sw=1.5))
    f.append(polygon([(777, 225), (780, 217), (783, 225)], fill=NEG))
    f.append(polygon([(777, 245), (780, 253), (783, 245)], fill=NEG))
    f.append(text(805, 238, "ΔE = e F d", size=11, bold=True, color=NEG))

    f.append(text(630, 355, "Локалізація хвильових функцій L_B = Δ / (eF)", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "bloch-wannier-stark.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — ВАХ та Негативний диференціальний опір (Esaki-Tsu IV Curve)
# ════════════════════════════════════════════════════════════════════════════
def fig_esaki_tsu_iv():
    W, H = 840, 380
    f = []

    f.append(text(420, 25, "Залежність дрейфової швидкості від електричного поля (Модель Есакі — Цо)", size=15, bold=True, color=INK))

    ox, oy = 90, 310
    f.append(line(ox, oy, 780, oy, color=INK, sw=2.0))  # Поле F
    f.append(line(ox, oy, ox, 60, color=INK, sw=2.0))   # Швидкість v_d

    f.append(polygon([(780, oy - 4), (790, oy), (780, oy + 4)], fill=INK))
    f.append(polygon([(ox - 4, 60), (ox, 50), (ox + 4, 60)], fill=INK))

    f.append(text(790, oy + 25, "Електричне поле F", size=12, bold=True, color=INK))
    f.append(text(ox - 10, 45, "Дрейфова швидкість v_d", size=12, bold=True, color=INK, anchor="end"))

    pts_iv = []
    fc_x = 270
    vmax_y = 120
    h_y = oy - vmax_y

    for px in range(ox, 760, 5):
        ff = (px - ox) / (fc_x - ox)
        vv = (2.0 * ff) / (1.0 + ff * ff)
        py = oy - h_y * vv
        pts_iv.append((px, py))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_iv), stroke=POS, sw=3.0))

    f.append(line(fc_x, oy, fc_x, oy - h_y, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(ox, oy - h_y, fc_x, oy - h_y, color=MUTED, sw=1.5, dash="4 4"))

    f.append(circle(fc_x, oy - h_y, 5, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(text(fc_x, oy + 20, "F_c = ħ / (e·d·τ)", size=12, bold=True, color=INK))
    f.append(text(ox - 15, oy - h_y + 4, "v_max", size=12, bold=True, color=POS, anchor="end"))

    f.append(rect(ox + 10, 270, 150, 30, fill="#eaf2f8", stroke="none"))
    f.append(text(ox + 85, 290, "Закон Ома (v_d = μ F)", size=11, bold=True, color=NEG))

    f.append(rect(380, 110, 320, 45, fill="#fadbd8", stroke=POS, sw=1.5))
    f.append(text(540, 130, "Область негативного диференціального опору (НДО)", size=12, bold=True, color="#78281f"))
    f.append(text(540, 147, "dv_d / dF < 0 (електрони у верхній частині мінізони)", size=11, color="#78281f"))

    f.append(line(430, 175, 550, 225, color="#78281f", sw=2.0, dash="3 2"))
    f.append(text(575, 205, "Негативний нахил", size=11, bold=True, color="#78281f"))

    render(os.path.join(OUT, "esaki-tsu-iv.svg"), W, H, *f)

if __name__ == "__main__":
    fig_superlattice_types()
    fig_miniband_formation()
    fig_bloch_wannier_stark()
    fig_esaki_tsu_iv()
    print("Усі 4 фігури успішно згенеровано у теці img/")
