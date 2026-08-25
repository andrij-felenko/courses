# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# 1. fig-powers-generator-vs-non-generator.svg
def fig_powers_generator_vs_non_generator():
    W, H = 980, 460
    p = []
    
    XS = {1: 280, 2: 390, 3: 500, 4: 610, 5: 720, 6: 830}
    Y3 = 190
    Y2 = 330
    CW, CH = 84, 48

    p.append(text(W / 2, 45, "Послідовності степенів за модулем 7", size=18, bold=True))
    p.append(text(W / 2, 72, "Первісний корінь g = 3 породжує всі 6 лишків, а число a = 2 застрягає в циклі з 3 елементів", size=13, color=MUTED))

    # Смуга під кроками
    p.append(rect(200, 110, 700, 32, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    for step in range(1, 7):
        p.append(text(XS[step], 131, "степінь %d" % step, size=13, bold=True, color=MUTED))

    # Рядок для g = 3
    p.append(text(170, Y3 - 4, "g = 3", size=16, bold=True, color=FIELD, anchor="end"))
    p.append(text(170, Y3 + 15, "ord₇(3) = 6 = φ(7)", size=11, color=MUTED, anchor="end"))

    # Зелена підкладка для повного циклу g=3
    p.append(rect(XS[1] - CW/2 - 8, Y3 - CH/2 - 8, 550 + 16, CH + 16, fill="#eafaf0", stroke="none", rx=8))

    vals_3 = [3, 2, 6, 4, 5, 1]
    for s in range(1, 7):
        v = vals_3[s - 1]
        x = XS[s]
        is_one = (v == 1)
        p.append(rect(x - CW/2, Y3 - CH/2, CW, CH,
                      fill="#ffffff",
                      stroke=FIELD if is_one else "#27ae60",
                      sw=2.0 if is_one else 1.4))
        p.append(text(x, Y3 - 4, "3%s ≡ %d" % ("¹²³⁴⁵⁶"[s-1], v), size=13, bold=True, color=FIELD if is_one else INK))
        p.append(text(x, Y3 + 15, "(mod 7)", size=10, color=MUTED))
        if s < 6:
            p.append(arrow(x + CW/2 + 3, Y3, XS[s+1] - CW/2 - 3, Y3, color=FIELD, sw=1.5))

    p.append(text(XS[6] + CW/2 + 15, Y3 + 5, "Повний цикл", size=12, bold=True, color=FIELD, anchor="start"))

    # Рядок для a = 2
    p.append(text(170, Y2 - 4, "a = 2", size=16, bold=True, color=POS, anchor="end"))
    p.append(text(170, Y2 + 15, "ord₇(2) = 3 < φ(7)", size=11, color=MUTED, anchor="end"))

    # Сіра підкладка для короткого циклу a=2
    p.append(rect(XS[1] - CW/2 - 8, Y2 - CH/2 - 8, 220 + 16, CH + 16, fill="#fef2f2", stroke="none", rx=8))

    vals_2 = [2, 4, 1, 2, 4, 1]
    for s in range(1, 7):
        v = vals_2[s - 1]
        x = XS[s]
        in_first_cycle = (s <= 3)
        is_one = (v == 1)
        p.append(rect(x - CW/2, Y2 - CH/2, CW, CH,
                      fill="#ffffff",
                      stroke=POS if is_one else (LINE if in_first_cycle else "#cbd5e1"),
                      sw=2.0 if is_one else 1.2))
        p.append(text(x, Y2 - 4, "2%s ≡ %d" % ("¹²³⁴⁵⁶"[s-1], v), size=13, bold=in_first_cycle, color=POS if is_one else (INK if in_first_cycle else MUTED)))
        p.append(text(x, Y2 + 15, "(mod 7)", size=10, color=MUTED))
        if s < 6:
            p.append(arrow(x + CW/2 + 3, Y2, XS[s+1] - CW/2 - 3, Y2, color=POS if s < 3 else "#cbd5e1", sw=1.3))

    p.append(text(XS[3] + CW/2 + 15, Y2 + 5, "Повтор", size=12, bold=True, color=POS, anchor="start"))

    render(os.path.join(OUT, "fig-powers-generator-vs-non-generator.svg"), W, H, *p,
           title="Генератор і звичайний елемент за модулем 7")

# 2. fig-existence-moduli.svg
def fig_existence_moduli():
    W, H = 960, 490
    p = []

    p.append(text(W / 2, 40, "Теорема Ґаусса: які модулі n мають первісний корінь?", size=18, bold=True))
    p.append(text(W / 2, 65, "Група лишків (ℤ/nℤ)* є циклічною лише для чотирьох класів чисел", size=13, color=MUTED))

    # Зелена колонка (ІСНУЄ)
    GX = 240
    GW = 410
    p.append(rect(GX - GW/2, 95, GW, 365, fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    p.append(text(GX, 125, "Первісний корінь ІСНУЄ", size=16, bold=True, color=FIELD))
    p.append(text(GX, 145, "Група (ℤ/nℤ)* є циклічною", size=11.5, color=MUTED))

    ok_items = [
        ("n = 2", "φ(2) = 1, g = 1", "n = 2"),
        ("n = 4", "φ(4) = 2, g = 3", "n = 4"),
        ("n = pᵏ", "p — непарне просте, k ≥ 1", "n = 3, 5, 7, 9, 11, 13, 25..."),
        ("n = 2·pᵏ", "подвоєний степінь", "n = 6, 10, 14, 18, 22, 26, 50...")
    ]
    
    y_start = 170
    for i, (title_str, sub_str, ex_str) in enumerate(ok_items):
        cy = y_start + i * 64
        p.append(rect(GX - GW/2 + 15, cy, GW - 30, 54, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=6))
        p.append(text(GX - GW/2 + 28, cy + 22, title_str, size=14, bold=True, color=FIELD, anchor="start"))
        p.append(text(GX - GW/2 + 28, cy + 40, sub_str, size=11, color=INK, anchor="start"))
        p.append(text(GX + GW/2 - 28, cy + 31, ex_str, size=11, color=MUTED, anchor="end"))

    # Червона колонка (НЕ ІСНУЄ)
    RX = 720
    RW = 430
    p.append(rect(RX - RW/2, 95, RW, 365, fill="#fef2f2", stroke=POS, sw=2, rx=10))
    p.append(text(RX, 125, "Первісного кореня НЕ ІСНУЄ", size=16, bold=True, color=POS))
    p.append(text(RX, 145, "Група не циклічна, λ(n) < φ(n)", size=11.5, color=MUTED))

    fail_items = [
        ("n = 2ᵏ при k ≥ 3", "8, 16, 32, 64...", "4 корені з 1; λ(2ᵏ) = 2ᵏ⁻² = φ(2ᵏ)/2"),
        ("n = pᵏ · qᵐ · ...", "15, 21, 33, 35...", "Два непарних простих; λ(n) < φ(n)"),
        ("n = 2ᵐ · pᵏ · ... (m≥2)", "12, 20, 24, 40...", "Парний модуль з непарним множником")
    ]

    y_start_fail = 170
    for i, (title_str, sub_str, ex_str) in enumerate(fail_items):
        cy = y_start_fail + i * 86
        p.append(rect(RX - RW/2 + 15, cy, RW - 30, 74, fill="#ffffff", stroke="#fecaca", sw=1.2, rx=6))
        p.append(text(RX - RW/2 + 28, cy + 24, title_str, size=14, bold=True, color=POS, anchor="start"))
        p.append(text(RX - RW/2 + 28, cy + 44, sub_str, size=11, color=INK, anchor="start"))
        p.append(text(RX - RW/2 + 28, cy + 60, ex_str, size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fig-existence-moduli.svg"), W, H, *p,
           title="Класифікація модулів за існуванням первісного кореня")

# 3. fig-discrete-log-mapping.svg
def fig_discrete_log_mapping():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 40, "Дискретне логарифмування: додавання ↔ множення", size=18, bold=True))
    p.append(text(W / 2, 65, "Первісний корінь g = 3 переводить додавання показників у множення остач за модулем 7", size=13, color=MUTED))

    XS = [150 + i * 130 for i in range(6)]
    Y1 = 150
    Y2 = 310
    BW, BH = 90, 48

    p.append(text(80, Y1 - 6, "Показник k", size=13, bold=True, color=NEG, anchor="end"))
    p.append(text(80, Y1 + 12, "в (ℤ₆, +)", size=11, color=MUTED, anchor="end"))
    p.append(text(80, Y2 - 6, "Остача 3ᵏ", size=13, bold=True, color=FIELD, anchor="end"))
    p.append(text(80, Y2 + 12, "в ((ℤ/7ℤ)*, ·)", size=11, color=MUTED, anchor="end"))

    exponents = [0, 1, 2, 3, 4, 5]
    residues  = [1, 3, 2, 6, 4, 5]

    for i in range(6):
        k = exponents[i]
        r = residues[i]
        x = XS[i]

        p.append(rect(x - BW/2, Y1 - BH/2, BW, BH, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
        p.append(text(x, Y1 + 4, "k = %d" % k, size=14, bold=True, color=NEG))

        p.append(arrow(x, Y1 + BH/2 + 4, x, Y2 - BH/2 - 4, color=LINE, sw=1.4))
        p.append(text(x + 15, (Y1 + Y2)/2 + 4, "3%s" % ("⁰¹²³⁴⁵"[k]), size=11, color=MUTED, anchor="start"))

        p.append(rect(x - BW/2, Y2 - BH/2, BW, BH, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
        p.append(text(x, Y2 + 4, "%d" % r, size=15, bold=True, color=FIELD))

    # Горизонтальні зв'язки між елементами вгорі (додавання +1 mod 6) i внизу (множення *3 mod 7)
    for i in range(5):
        x1 = XS[i] + BW/2 + 2
        x2 = XS[i+1] - BW/2 - 2
        p.append(arrow(x1, Y1 - 10, x2, Y1 - 10, color=NEG, sw=1.2))
        p.append(arrow(x1, Y2 + 10, x2, Y2 + 10, color=FIELD, sw=1.2))

    p.append(text(W/2, Y1 - 28, "+1 (mod 6)", size=11.5, bold=True, color=NEG))
    p.append(text(W/2, Y2 + 28, "·3 (mod 7)", size=11.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "fig-discrete-log-mapping.svg"), W, H, *p,
           title="Ізоморфізм дискретного логарифма")

if __name__ == "__main__":
    fig_powers_generator_vs_non_generator()
    fig_existence_moduli()
    fig_discrete_log_mapping()
