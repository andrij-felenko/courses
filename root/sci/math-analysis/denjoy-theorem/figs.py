# -*- coding: utf-8 -*-
"""Фігури до статті «Теорема Данжуа про гладкість кругових відображень».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#8e44ad"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Fig 1: Топологічна спряженість кругового диффеоморфізму та жорсткого повороту ──
def fig_circle_diffeomorphism_conjugacy():
    W, H = 900, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Топологічна спряженість h ∘ f = R_α ∘ h кругового відображення", size=16, bold=True))

    PW, PH = 320, 320
    PT = 75
    PL1 = 70
    PL2 = 510

    # Panel 1: Diffeomorphism f on S^1
    f.append(rect(PL1, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))
    f.append(text(PL1 + PW / 2, PT - 12, "Гладкий диффеоморфізм f: S¹ → S¹", size=13, color=INK, anchor="middle", bold=True))

    # Panel 2: Rigid rotation R_alpha on S^1
    f.append(rect(PL2, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))
    f.append(text(PL2 + PW / 2, PT - 12, "Жорсткий поворот R_α(θ) = θ + α (mod 1)", size=13, color=POS, anchor="middle", bold=True))

    # Diagonal reference lines (identity)
    f.append(line(PL1, PT + PH, PL1 + PW, PT, color="#cbd5e1", sw=1.2, dash="4,4"))
    f.append(line(PL2, PT + PH, PL2 + PW, PT, color="#cbd5e1", sw=1.2, dash="4,4"))

    alpha = 0.38196601125
    N = 200

    def X1(x): return PL1 + x * PW
    def Y1(y): return PT + PH - y * PH
    def X2(x): return PL2 + x * PW
    def Y2(y): return PT + PH - y * PH

    pts1_cont = []
    for i in range(N + 1):
        x = i / N
        fx = (x + alpha + 0.08 * math.sin(2 * math.pi * x)) % 1.0
        if i > 0 and abs(fx - ( ( (i-1)/N + alpha + 0.08 * math.sin(2 * math.pi * (i-1)/N) ) % 1.0 )) > 0.5:
            pts1_cont.append("CUT")
        pts1_cont.append("%.1f,%.1f" % (X1(x), Y1(fx)))

    current_poly = []
    for p in pts1_cont:
        if p == "CUT":
            if current_poly:
                f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(current_poly), NEG))
                current_poly = []
        else:
            current_poly.append(p)
    if current_poly:
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(current_poly), NEG))

    pts2_cont = []
    for i in range(N + 1):
        x = i / N
        rx = (x + alpha) % 1.0
        if i > 0 and abs(rx - (((i-1)/N + alpha) % 1.0)) > 0.5:
            pts2_cont.append("CUT")
        pts2_cont.append("%.1f,%.1f" % (X2(x), Y2(rx)))

    current_poly = []
    for p in pts2_cont:
        if p == "CUT":
            if current_poly:
                f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(current_poly), POS))
                current_poly = []
        else:
            current_poly.append(p)
    if current_poly:
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(current_poly), POS))

    # Arrow connecting panels
    f.append(arrow(PL1 + PW + 10, PT + PH / 2, PL2 - 10, PT + PH / 2, color=ACCENT, sw=2.5))
    f.append(text(PL1 + PW + 60, PT + PH / 2 - 28, "Гомеоморфізм h", size=12, color=ACCENT, anchor="middle", bold=True))
    f.append(text(PL1 + PW + 60, PT + PH / 2 - 10, "h ∘ f = R_α ∘ h", size=12, color=ACCENT, anchor="middle", bold=True))

    for PL, name in [(PL1, "f(x)"), (PL2, "R_α(x)")]:
        f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=1.8))
        f.append(line(PL, PT, PL, PT + PH, color=INK, sw=1.8))
        f.append(text(PL + PW / 2, PT + PH + 32, "Аргумент x ∈ [0, 1)", size=12, color=INK, anchor="middle", bold=True))
        f.append(text(PL - 12, PT + PH / 2, name, size=12, color=INK, anchor="end", bold=True))

    render(os.path.join(IMG, 'circle-diffeomorphism-conjugacy.svg'), W, H, *f)

# ── Fig 2: Конструкція контрприкладу Данжуа з блукаючим інтервалом та множиною Кантора ──
def fig_denjoy_counterexample_cantor():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Контрприклад Данжуа: блукаючі інтервали I_n та канторів атрактор K", size=16, bold=True))

    PL, PW = 70, 720
    PT = 70

    # Top panel
    f.append(text(PL + PW / 2, PT + 15, "Розгортка кола S¹ = K ∪ (⋃ I_n): вклеювання блукаючих інтервалів I_n", size=13, color=INK, anchor="middle", bold=True))

    Ybase = PT + 90
    f.append(line(PL + 30, Ybase, PL + PW - 30, Ybase, color=INK, sw=2.0))

    intervals = [
        (0.18, 0.28, "I_0", POS),
        (0.42, 0.49, "I_1", ACCENT),
        (0.68, 0.73, "I_2", ACCENT),
        (0.05, 0.10, "I_-1", FIELD),
        (0.85, 0.88, "I_-2", FIELD),
    ]

    for x_start, x_end, lbl, col in intervals:
        px1 = PL + 30 + x_start * (PW - 60)
        px2 = PL + 30 + x_end * (PW - 60)
        f.append(rect(px1, Ybase - 12, px2 - px1, 24, fill=col, stroke=INK, sw=1.2, rx=2))
        f.append(text((px1 + px2) / 2, Ybase - 18, lbl, size=11, color=INK, anchor="middle", bold=True))

    f.append(text(PL + 30 + 0.35 * (PW - 60), Ybase + 38, "Множина Кантора K (доскональна, ніде не щільна)", size=12, color=NEG, anchor="middle", bold=True))
    f.append(line(PL + 30 + 0.30 * (PW - 60), Ybase + 18, PL + 30 + 0.40 * (PW - 60), Ybase + 18, color=NEG, sw=3.0))

    # Bottom section
    PT2 = 230
    f.append(text(PL + PW / 2, PT2 + 20, "Властивості мінімальної множини K та блукаючого інтервалу I_0", size=13, color=INK, anchor="middle", bold=True))

    box1_x, box1_w = PL + 20, 210
    box2_x, box2_w = PL + 255, 210
    box3_x, box3_w = PL + 490, 210

    f.append(rect(box1_x, PT2 + 45, box1_w, 100, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(box1_x + box1_w / 2, PT2 + 70, "1. Dіз'юнктність", size=12, color=INK, anchor="middle", bold=True))
    f.append(text(box1_x + box1_w / 2, PT2 + 95, "fⁿ(I_0) ∩ fᵐ(I_0) = ∅", size=11, color=INK, anchor="middle"))
    f.append(text(box1_x + box1_w / 2, PT2 + 115, "при n ≠ m", size=11, color=INK, anchor="middle"))

    f.append(rect(box2_x, PT2 + 45, box2_w, 100, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(box2_x + box2_w / 2, PT2 + 70, "2. Збіжність довжин", size=12, color=INK, anchor="middle", bold=True))
    f.append(text(box2_x + box2_w / 2, PT2 + 95, "∑ |fⁿ(I_0)| ≤ 1 < ∞", size=11, color=INK, anchor="middle"))
    f.append(text(box2_x + box2_w / 2, PT2 + 115, "сума довжин обмежена", size=11, color=INK, anchor="middle"))

    f.append(rect(box3_x, PT2 + 45, box3_w, 100, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    f.append(text(box3_x + box3_w / 2, PT2 + 70, "3. Локальна щільність", size=12, color=INK, anchor="middle", bold=True))
    f.append(text(box3_x + box3_w / 2, PT2 + 95, "Орбіти щільні в K,", size=11, color=INK, anchor="middle"))
    f.append(text(box3_x + box3_w / 2, PT2 + 115, "але НЕ щільні на S¹", size=11, color=INK, anchor="middle"))

    f.append(rect(PL + 60, PT2 + 170, PW - 120, 60, fill="#fee2e2", stroke=NEG, sw=1.2, rx=4))
    f.append(text(PL + PW / 2, PT2 + 195, "Умови виникнення: f ∈ C¹(S¹), але log f' НЕ має обмеженої варіації", size=12, color=NEG, anchor="middle", bold=True))
    f.append(text(PL + PW / 2, PT2 + 215, "Var(log f') = ∞ (відсутність $C^{1+\\alpha}$ гладкості)", size=11, color=NEG, anchor="middle"))

    render(os.path.join(IMG, 'denjoy-counterexample-cantor.svg'), W, H, *f)

# ── Fig 3: Оцінка росту похідних вздовж орбіт та нерівність Данжуа ──
def fig_denjoy_derivative_growth():
    W, H = 840, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Обмеження спотворення похідних (Denjoy Distortion Lemma)", size=16, bold=True))

    PL, PW = 80, 680
    PT, PH = 70, 370

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=4))

    def X(x): return PL + x * PW
    def Y(y): return PT + PH - y * PH

    f.append(line(PL, Y(0.5), PL + PW, Y(0.5), color="#94a3b8", sw=1.2, dash="4,4"))

    N = 250
    pts_c2, pts_c1 = [], []
    for i in range(N + 1):
        x = i / N
        y_c2 = 0.5 + 0.18 * math.sin(4 * math.pi * x) + 0.05 * math.cos(8 * math.pi * x)
        y_c1 = 0.5 + 0.24 * math.sin(10 * math.pi * x) * math.exp(-0.3 * abs(x - 0.5))
        pts_c2.append("%.1f,%.1f" % (X(x), Y(y_c2)))
        pts_c1.append("%.1f,%.1f" % (X(x), Y(y_c1)))

    f.append(line(PL, Y(0.78), PL + PW, Y(0.78), color=POS, sw=1.5, dash="6,3"))
    f.append(line(PL, Y(0.22), PL + PW, Y(0.22), color=POS, sw=1.5, dash="6,3"))
    f.append(text(PL + 12, Y(0.78) - 22, "+ Var(log f') [Верхня межа C²]", size=11, color=POS, anchor="start", bold=True))
    f.append(text(PL + 12, Y(0.22) + 24, "- Var(log f') [Нижня межа C²]", size=11, color=POS, anchor="start", bold=True))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_c2), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" opacity="0.6"/>' % (" ".join(pts_c1), NEG))

    f.append(line(PL, PT + PH, PL + PW, PT + PH, color=INK, sw=1.8))
    f.append(line(PL, PT, PL, PT + PH, color=INK, sw=1.8))
    f.append(text(PL + PW / 2, PT + PH + 34, "Початкова точка x ∈ S¹", size=13, color=INK, anchor="middle", bold=True))
    f.append(text(PL - 12, PT + PH / 2, "log (f^{q_n}')(x)", size=13, color=INK, anchor="end", bold=True))

    # Note text without overlapping rect
    f.append(text(PL + 40, PT + 25, "Зелена крива (C²): Var(log f') < ∞ ⇒ exp(-V) ≤ (f^{q_n}')(x) ≤ exp(V)", size=11, color=POS, anchor="start", bold=True))
    f.append(text(PL + 40, PT + 42, "Червона крива (C¹ без обмеженої варіації): росте до ∞ при q_n → ∞", size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(IMG, 'denjoy-derivative-growth.svg'), W, H, *f)

# ── Fig 4: Спектр чисел обертання та межа застосовності теореми Данжуа ──
def fig_rotation_number_properties():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Класифікація динаміки кругових відображень за гладкістю та α", size=16, bold=True))

    PL, PW = 70, 700
    PT, PH = 70, 360

    col1_x = PL + 20
    col1_w = 320
    col2_x = PL + 360
    col2_w = 320

    # Column 1: Rational
    f.append(rect(col1_x, PT + 20, col1_w, 300, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    f.append(text(col1_x + col1_w / 2, PT + 46, "Раціональне число обертання α = p/q", size=13, color="#1e40af", anchor="middle", bold=True))

    f.append(text(col1_x + 20, PT + 85, "• Наявність періодичних орбіт", size=11, color=INK, anchor="start"))
    f.append(text(col1_x + 20, PT + 110, "• Період усіх замкнених орбіт = q", size=11, color=INK, anchor="start"))
    f.append(text(col1_x + 20, PT + 135, "• Фазове захоплення (lock-in)", size=11, color=INK, anchor="start"))
    f.append(text(col1_x + 20, PT + 160, "• Структурна стійкість (Арнольд)", size=11, color=INK, anchor="start"))

    f.append(rect(col1_x + 15, PT + 195, col1_w - 30, 80, fill="#dbeafe", stroke="#3b82f6", sw=1.0, rx=4))
    f.append(text(col1_x + col1_w / 2, PT + 225, "Динамічний висновок:", size=11, color="#1e40af", anchor="middle", bold=True))
    f.append(text(col1_x + col1_w / 2, PT + 245, "Орбіти прямують до циклів.", size=11, color="#1e40af", anchor="middle"))
    f.append(text(col1_x + col1_w / 2, PT + 260, "Режим є неергодичним.", size=11, color="#1e40af", anchor="middle"))

    # Column 2: Irrational
    f.append(rect(col2_x, PT + 20, col2_w, 300, fill="#f0fdf4", stroke=POS, sw=1.5, rx=4))
    f.append(text(col2_x + col2_w / 2, PT + 46, "Ірраціональне число обертання α ∉ ℚ", size=13, color=POS, anchor="middle", bold=True))

    f.append(text(col2_x + 20, PT + 85, "1) f ∈ C² (або C¹⁺ˡⁱᵖ): Теорема Данжуа", size=11, color=POS, anchor="start", bold=True))
    f.append(text(col2_x + 35, PT + 108, "→ Траєкторії всюди щільні", size=11, color=INK, anchor="start"))
    f.append(text(col2_x + 35, PT + 128, "→ Строга ергодичність", size=11, color=INK, anchor="start"))
    f.append(text(col2_x + 35, PT + 148, "→ Немає блукаючих інтервалів", size=11, color=INK, anchor="start"))

    f.append(text(col2_x + 20, PT + 185, "2) f ∈ C¹ (Var(log f') = ∞):", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(col2_x + 35, PT + 208, "→ Контрприклад Данжуа", size=11, color=INK, anchor="start"))
    f.append(text(col2_x + 35, PT + 228, "→ Блукаючі інтервали I_n", size=11, color=INK, anchor="start"))
    f.append(text(col2_x + 35, PT + 248, "→ Канторів мінімальний атрактор", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'rotation-number-properties.svg'), W, H, *f)

if __name__ == "__main__":
    fig_circle_diffeomorphism_conjugacy()
    fig_denjoy_counterexample_cantor()
    fig_denjoy_derivative_growth()
    fig_rotation_number_properties()
    print("Всі 4 фігури успішно згенеровано.")
