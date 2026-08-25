# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

DARK = INK

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Ефект Мейснера — Оксенфельда: Нормальний стан vs Надпровідний стан
# ════════════════════════════════════════════════════════════════════════════
def fig_meissner():
    W, H = 840, 420
    f = []

    # Розділювальна лінія між панелями
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Нормальний стан (T > Tc) ──
    f.append(text(210, 45, "Нормальний стан (T > T_c)", size=14, bold=True, color=INK))
    f.append(text(210, 65, "Магнітне поле проникає в товщу (B = B_ext)", size=12, color=MUTED))

    # Зразок у нормальному стані
    f.append(rect(130, 160, 160, 160, fill="#e8ecef", stroke=MUTED, sw=2, rx=12))
    f.append(text(210, 230, "Метал (звичайна", size=13, color=MUTED, bold=True))
    f.append(text(210, 250, "провідність)", size=13, color=MUTED, bold=True))

    # Лінії магнітного поля B_ext (прямі крізь зразок)
    y_lines = [120, 150, 180, 210, 240, 270, 300, 330, 360]
    for y in y_lines:
        f.append(line(30, y, 390, y, color=NEG, sw=2))
        f.append(polygon([(375, y - 4), (385, y), (375, y + 4)], fill=NEG))
    f.append(text(60, 105, "B_ext", size=12, bold=True, color=NEG))

    # ── Права панель: Надпровідний стан (T < Tc) ──
    f.append(text(630, 45, "Надпровідний стан (T < T_c)", size=14, bold=True, color=INK))
    f.append(text(630, 65, "Ефект Мейснера: повне виштовхування поля (B = 0)", size=12, color=MUTED))

    # Зразок у надпровідному стані
    f.append(rect(550, 160, 160, 160, fill="#eaf2f8", stroke="#2980b9", sw=2.5, rx=12))
    f.append(text(630, 225, "Надпровідник", size=14, color="#1b4f72", bold=True))
    f.append(text(630, 245, "B = 0 в об'ємі", size=12, color=POS, bold=True))

    # Лінії поля, що огинають надпровідний зразок
    f.append(svg_path("M 450 120 L 810 120", stroke=NEG, sw=2))
    f.append(polygon([(795, 116), (805, 120), (795, 124)], fill=NEG))

    f.append(svg_path("M 450 150 C 520 150 530 135 630 135 C 730 135 740 150 810 150", stroke=NEG, sw=2))
    f.append(polygon([(795, 146), (805, 150), (795, 154)], fill=NEG))

    f.append(svg_path("M 450 180 C 510 180 520 145 630 145 C 740 145 750 180 810 180", stroke=NEG, sw=2))
    f.append(polygon([(795, 176), (805, 180), (795, 184)], fill=NEG))

    # Захисні поверхневі струми j_s
    f.append(circle(560, 180, 7, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(560, 183.5, "⊙", size=12, bold=True, color=POS))
    f.append(circle(560, 300, 7, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(560, 303.5, "⊗", size=12, bold=True, color=NEG))

    f.append(circle(700, 180, 7, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(700, 183.5, "⊙", size=12, bold=True, color=POS))
    f.append(circle(700, 300, 7, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(700, 303.5, "⊗", size=12, bold=True, color=NEG))

    f.append(text(630, 175, "Екрануючі струми j_s", size=11, bold=True, color=POS))

    f.append(svg_path("M 450 330 C 510 330 520 365 630 365 C 740 365 750 330 810 330", stroke=NEG, sw=2))
    f.append(polygon([(795, 326), (805, 330), (795, 334)], fill=NEG))

    f.append(svg_path("M 450 360 C 520 360 530 375 630 375 C 730 375 740 360 810 360", stroke=NEG, sw=2))
    f.append(polygon([(795, 356), (805, 360), (795, 364)], fill=NEG))

    f.append(svg_path("M 450 390 L 810 390", stroke=NEG, sw=2))
    f.append(polygon([(795, 386), (805, 390), (795, 394)], fill=NEG))

    render(os.path.join(OUT, "meissner-effect.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Надпровідники I та II роду: Фазові діаграми H(T) і криві намагніченості -M(H)
# ════════════════════════════════════════════════════════════════════════════
def fig_type1_vs_type2():
    W, H = 840, 440
    f = []

    f.append(line(420, 25, 420, 415, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Надпровідники I роду (κ < 1/√2) ──
    f.append(text(210, 45, "Надпровідники I роду (κ < 1/√2)", size=14, bold=True, color=INK))
    f.append(text(210, 65, "Одне критичне поле H_c(T)", size=12, color=MUTED))

    # Фазова діаграма H-T
    cx1, cy1 = 60, 220
    f.append(line(cx1, cy1, cx1 + 140, cy1, color=DARK, sw=1.5))
    f.append(line(cx1, cy1, cx1, cy1 - 120, color=DARK, sw=1.5))
    f.append(polygon([(cx1 + 140, cy1 - 3), (140 + cx1 + 8, cy1), (cx1 + 140, cy1 + 3)], fill=DARK))
    f.append(polygon([(cx1 - 3, cy1 - 120), (cx1, cy1 - 128), (cx1 + 3, cy1 - 120)], fill=DARK))
    f.append(text(cx1 + 145, cy1 + 18, "T", size=12, bold=True, color=DARK))
    f.append(text(cx1 - 15, cy1 - 120, "H", size=12, bold=True, color=DARK))

    # Крива H_c(T)
    f.append(svg_path("M 60 120 Q 130 130 180 220", stroke=POS, sw=2.5, fill="none"))
    f.append(text(120, 185, "Надпровідний", size=11, bold=True, color="#922b21"))
    f.append(text(120, 200, "стан (S)", size=11, color="#922b21"))
    f.append(text(140, 135, "Нормальний (N)", size=11, bold=True, color=MUTED))
    f.append(text(175, 235, "T_c", size=11, bold=True, color=DARK))
    f.append(text(42, 120, "H_c(0)", size=11, bold=True, color=DARK))

    # Крива -M(H) для I роду
    cx1m, cy1m = 250, 380
    f.append(line(cx1m, cy1m, cx1m + 130, cy1m, color=DARK, sw=1.5))
    f.append(line(cx1m, cy1m, cx1m, cy1m - 120, color=DARK, sw=1.5))
    f.append(polygon([(cx1m + 130, cy1m - 3), (cx1m + 138, cy1m), (cx1m + 130, cy1m + 3)], fill=DARK))
    f.append(polygon([(cx1m - 3, cy1m - 120), (cx1m, cy1m - 128), (cx1m + 3, cy1m - 120)], fill=DARK))
    f.append(text(cx1m + 135, cy1m + 18, "H", size=12, bold=True, color=DARK))
    f.append(text(cx1m - 20, cy1m - 120, "-M", size=12, bold=True, color=DARK))

    f.append(line(cx1m, cy1m, cx1m + 70, cy1m - 100, color=POS, sw=2.5))
    f.append(line(cx1m + 70, cy1m - 100, cx1m + 70, cy1m, color=POS, sw=2.5, dash="2 2"))
    f.append(line(cx1m + 70, cy1m, cx1m + 120, cy1m, color=POS, sw=2.5))
    f.append(text(cx1m + 70, cy1m + 18, "H_c", size=11, bold=True, color=DARK))
    f.append(text(cx1m + 25, cy1m - 60, "Повний", size=11, bold=True, color=POS))
    f.append(text(cx1m + 20, cy1m - 45, "діамагнетизм", size=10, color=POS))

    # ── Права панель: Надпровідники II роду (κ > 1/√2) ──
    f.append(text(630, 45, "Надпровідники II роду (κ > 1/√2)", size=14, bold=True, color=INK))
    f.append(text(630, 65, "Два критичні поля H_c1 та H_c2, змішаний стан", size=12, color=MUTED))

    # Фазова діаграма H-T для II роду
    cx2, cy2 = 480, 220
    f.append(line(cx2, cy2, cx2 + 140, cy2, color=DARK, sw=1.5))
    f.append(line(cx2, cy2, cx2, cy2 - 130, color=DARK, sw=1.5))
    f.append(polygon([(cx2 + 140, cy2 - 3), (cx2 + 148, cy2), (cx2 + 140, cy2 + 3)], fill=DARK))
    f.append(polygon([(cx2 - 3, cy2 - 130), (cx2, cy2 - 138), (cx2 + 3, cy2 - 130)], fill=DARK))
    f.append(text(cx2 + 145, cy2 + 18, "T", size=12, bold=True, color=DARK))
    f.append(text(cx2 - 15, cy2 - 130, "H", size=12, bold=True, color=DARK))

    f.append(svg_path("M 480 180 Q 550 190 600 220", stroke=NEG, sw=2, fill="none"))
    f.append(svg_path("M 480 100 Q 550 130 600 220", stroke=POS, sw=2.5, fill="none"))

    f.append(text(515, 205, "Meissner (S)", size=10, bold=True, color=NEG))
    f.append(text(540, 155, "Змішаний стан", size=11, bold=True, color="#8e44ad"))
    f.append(text(540, 170, "(вихори Абрикосова)", size=10, color="#8e44ad"))
    f.append(text(560, 110, "Нормальний (N)", size=10, bold=True, color=MUTED))
    f.append(text(595, 235, "T_c", size=11, bold=True, color=DARK))
    f.append(text(452, 180, "H_c1", size=10, bold=True, color=NEG))
    f.append(text(452, 100, "H_c2", size=10, bold=True, color=POS))

    # Крива -M(H) для II роду
    cx2m, cy2m = 670, 380
    f.append(line(cx2m, cy2m, cx2m + 140, cy2m, color=DARK, sw=1.5))
    f.append(line(cx2m, cy2m, cx2m, cy2m - 120, color=DARK, sw=1.5))
    f.append(polygon([(cx2m + 140, cy2m - 3), (cx2m + 148, cy2m), (cx2m + 140, cy2m + 3)], fill=DARK))
    f.append(polygon([(cx2m - 3, cy2m - 120), (cx2m, cy2m - 128), (cx2m + 3, cy2m - 120)], fill=DARK))
    f.append(text(cx2m + 145, cy2m + 18, "H", size=12, bold=True, color=DARK))
    f.append(text(cx2m - 20, cy2m - 120, "-M", size=12, bold=True, color=DARK))

    f.append(svg_path("M 670 380 L 695 310 Q 730 350 790 380 L 805 380", stroke="#8e44ad", sw=2.5, fill="none"))
    f.append(line(695, 380, 695, 310, color=NEG, sw=1, dash="2 2"))
    f.append(line(790, 380, 790, 310, color=POS, sw=1, dash="2 2"))
    f.append(text(695, 395, "H_c1", size=11, bold=True, color=NEG))
    f.append(text(790, 395, "H_c2", size=11, bold=True, color=POS))
    f.append(text(735, 335, "Плавне проникнення", size=10, bold=True, color="#8e44ad"))
    f.append(text(735, 348, "потоку Φ_0", size=10, color="#8e44ad"))

    render(os.path.join(OUT, "type1-vs-type2.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Структура вихору Абрикосова: Профіль параметра порядку |Ψ|² та магнітного поля B
# ════════════════════════════════════════════════════════════════════════════
def fig_abrikosov_vortex():
    W, H = 820, 420
    f = []

    cx, cy = 410, 320
    f.append(line(80, cy, 740, cy, color=DARK, sw=1.5))
    f.append(line(cx, cy + 40, cx, 40, color=DARK, sw=1.5))
    f.append(polygon([(740, cy - 4), (750, cy), (740, cy + 4)], fill=DARK))
    f.append(polygon([(cx - 4, 40), (cx, 30), (cx + 4, 40)], fill=DARK))

    f.append(text(730, cy + 25, "Відстань від центру вихору r", size=12, bold=True, color=DARK))
    f.append(text(cx + 15, 35, "|Ψ(r)|²  та  B(r)", size=12, bold=True, color=DARK))

    f.append(rect(cx - 50, cy - 230, 100, 230, fill="#fdecea", stroke="none"))
    f.append(line(cx - 50, cy + 5, cx - 50, cy - 230, color=POS, sw=1.2, dash="3 3"))
    f.append(line(cx + 50, cy + 5, cx + 50, cy - 230, color=POS, sw=1.2, dash="3 3"))
    f.append(text(cx, cy + 22, "Нормальне ядро (r ≤ ξ)", size=11, bold=True, color=POS))
    f.append(line(cx - 50, cy + 12, cx + 50, cy + 12, color=POS, sw=1.5))

    f.append(line(cx - 220, cy + 5, cx - 220, cy - 230, color=NEG, sw=1.2, dash="3 3"))
    f.append(line(cx + 220, cy + 5, cx + 220, cy - 230, color=NEG, sw=1.2, dash="3 3"))
    f.append(text(cx + 140, cy + 22, "Область поля λ", size=11, bold=True, color=NEG))
    f.append(line(cx, cy + 12, cx + 220, cy + 12, color=NEG, sw=1.5))

    f.append(svg_path("M 100 80 Q 250 80 360 320", stroke=POS, sw=2.5, fill="none"))
    f.append(svg_path("M 460 320 Q 570 80 720 80", stroke=POS, sw=2.5, fill="none"))
    f.append(circle(cx, cy, 6, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(text(620, 68, "Густина надпровідних пар |Ψ(r)|²", size=12, bold=True, color=POS))

    f.append(svg_path("M 100 315 Q 260 300 410 70", stroke=NEG, sw=2.5, fill="none"))
    f.append(svg_path("M 410 70 Q 560 300 720 315", stroke=NEG, sw=2.5, fill="none"))
    f.append(circle(cx, 70, 6, fill=NEG, stroke="#1b4f72", sw=1.5))
    f.append(text(210, 260, "Магнітне поле B(r)", size=12, bold=True, color=NEG))
    f.append(text(cx + 15, 75, "B_0 = Φ_0 / (2π λ²)", size=11, bold=True, color=NEG))

    f.append(text(cx, 375, "Квант потоку Φ_0 = h / (2e) проходить крізь нормальне ядро", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "abrikosov-vortex.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Мікроскопічний механізм: Куперівська пара та фононне притягання
# ════════════════════════════════════════════════════════════════════════════
def fig_cooper_pair_phonon():
    W, H = 840, 420
    f = []

    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Обмін фононами ──
    f.append(text(210, 45, "Електрон-фононна взаємодія", size=14, bold=True, color=INK))
    f.append(text(210, 65, "Деформація ґратки створює надлишок позитивного заряду", size=11.5, color=MUTED))

    grid_x = [70, 140, 210, 280, 350]
    grid_y = [130, 210, 290, 370]

    for y in grid_y:
        for x in grid_x:
            dx = 0
            dy = 0
            if x in [140, 280] and y == 210:
                dx = 18 if x == 140 else -18
            f.append(circle(x + dx, y + dy, 12, fill="#fdecea", stroke=POS, sw=1.5))
            f.append(text(x + dx, y + dy + 4.5, "+", size=13, color=POS, bold=True))

    f.append(circle(110, 210, 9, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(110, 213, "e₁⁻", size=11, color=NEG, bold=True))
    f.append(line(110, 210, 60, 210, color=NEG, sw=2, dash="3 3"))
    f.append(polygon([(60, 206), (50, 210), (60, 214)], fill=NEG))
    f.append(text(85, 195, "k, ↑", size=11, bold=True, color=NEG))

    f.append(circle(210, 210, 35, fill="none", stroke="#f1c40f", sw=2))
    f.append(text(210, 160, "Позитивна трек-поляризація", size=10.5, bold=True, color="#d4ac0d"))

    f.append(circle(310, 210, 9, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(310, 213, "e₂⁻", size=11, color=NEG, bold=True))
    f.append(line(310, 210, 240, 210, color=NEG, sw=2, dash="3 3"))
    f.append(polygon([(240, 206), (230, 210), (240, 214)], fill=NEG))
    f.append(text(285, 195, "-k, ↓", size=11, bold=True, color=NEG))

    # ── Права панель: Енергетична щілина Δ у сфері Фермі ──
    f.append(text(630, 45, "Квантовий стан БКШ та енергетична щілина", size=14, bold=True, color=INK))
    f.append(text(630, 65, "Зв'язані бозе-пари над поверхнею Фермі", size=11.5, color=MUTED))

    cx_f, cy_f = 630, 240
    f.append(circle(cx_f, cy_f, 100, fill="#ebf5fb", stroke="#2980b9", sw=2))
    f.append(text(cx_f, cy_f - 112, "Поверхня Фермі E_F", size=12, bold=True, color="#2980b9"))

    f.append(circle(cx_f, cy_f, 115, fill="none", stroke=POS, sw=2))
    f.append(text(cx_f + 130, cy_f - 60, "Енергетична щілина 2Δ", size=12, bold=True, color=POS))
    f.append(text(cx_f + 130, cy_f - 42, "E_gap = 2·Δ(T)", size=11, color=POS))

    f.append(line(cx_f - 75, cy_f, cx_f + 75, cy_f, color="#8e44ad", sw=2, dash="3 3"))

    f.append(circle(cx_f - 75, cy_f, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(cx_f - 75, cy_f + 3, "e⁻", size=10, color=NEG, bold=True))
    f.append(text(cx_f - 75, cy_f - 15, "(k, ↑)", size=11, bold=True, color=NEG))

    f.append(circle(cx_f + 75, cy_f, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(cx_f + 75, cy_f + 3, "e⁻", size=10, color=NEG, bold=True))
    f.append(text(cx_f + 75, cy_f - 15, "(-k, ↓)", size=11, bold=True, color=NEG))

    f.append(text(cx_f, cy_f + 35, "Куперівська пара", size=13, bold=True, color="#8e44ad"))
    f.append(text(cx_f, cy_f + 55, "Сумарний імпульс K = 0", size=11, color=DARK))
    f.append(text(cx_f, cy_f + 72, "Сумарний спін S = 0 (бозон)", size=11, color=DARK))

    render(os.path.join(OUT, "cooper-pair-phonon.svg"), W, H, *f)


if __name__ == '__main__':
    fig_meissner()
    fig_type1_vs_type2()
    fig_abrikosov_vortex()
    fig_cooper_pair_phonon()
    print("All superconductivity figures generated successfully.")
