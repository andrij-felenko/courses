# -*- coding: utf-8 -*-
"""Фігури для теми «Нерівність Чернова» (book/algorithms/complexity-computability/chernoff-bound)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fee2e2", "#dc2626"

def path(d_str, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

def fig_tail_comparison():
    """fig1-tail-comparison.svg: Порівняння швидкості згасання хвостів розподілу (Марков vs Чебишов vs Чернов)."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Порівняння меж верхнього хвоста ймовірності Pr[X ≥ (1 + δ)μ]", size=16, bold=True, color="#1e293b"))

    # Графічна сітка (осі)
    ox, oy = 90, 370
    pw, ph = 460, 290
    frags.append(rect(ox, oy - ph, pw, ph, fill="#ffffff", stroke="#e2e8f0", sw=1))

    # Лінії сітки
    for i in range(1, 5):
        y_val = oy - i * (ph / 4)
        frags.append(line(ox, y_val, ox + pw, y_val, color="#f1f5f9", sw=1, dash="4,4"))
    for i in range(1, 5):
        x_val = ox + i * (pw / 4)
        frags.append(line(x_val, oy - ph, x_val, oy, color="#f1f5f9", sw=1, dash="4,4"))

    # Осі X та Y
    frags.append(arrow(ox, oy, ox + pw + 25, oy, color="#475569", sw=2))
    frags.append(arrow(ox, oy, ox, oy - ph - 20, color="#475569", sw=2))
    frags.append(text(ox + pw + 35, oy + 4, "δ (відхилення)", size=12, bold=True, color="#334155"))
    frags.append(text(ox - 30, oy - ph - 25, "Верхня межа Pr[X ≥ (1+δ)μ]", size=11, bold=True, color="#334155"))

    # Позначки на осях
    frags.append(text(ox, oy + 20, "0", size=11, color="#64748b"))
    frags.append(text(ox + pw * 0.25, oy + 20, "0.5", size=11, color="#64748b"))
    frags.append(text(ox + pw * 0.5, oy + 20, "1.0", size=11, color="#64748b"))
    frags.append(text(ox + pw * 0.75, oy + 20, "1.5", size=11, color="#64748b"))
    frags.append(text(ox + pw, oy + 20, "2.0", size=11, color="#64748b"))

    frags.append(text(ox - 25, oy, "0.0", size=11, color="#64748b"))
    frags.append(text(ox - 25, oy - ph * 0.25, "0.25", size=11, color="#64748b"))
    frags.append(text(ox - 25, oy - ph * 0.5, "0.50", size=11, color="#64748b"))
    frags.append(text(ox - 25, oy - ph * 0.75, "0.75", size=11, color="#64748b"))
    frags.append(text(ox - 25, oy - ph, "1.00", size=11, color="#64748b"))

    # Побудова кривих
    pts_markov = []
    pts_cheby = []
    pts_chernoff = []

    steps = 50
    for i in range(steps + 1):
        delta = (i / steps) * 2.0
        x_px = ox + (delta / 2.0) * pw

        # Markov
        m_val = min(1.0, 1.0 / (1.0 + delta))
        y_m = oy - m_val * ph
        pts_markov.append((x_px, y_m))

        # Chebyshev
        c_val = 1.0 if delta < 0.1 else min(1.0, 1.0 / (10.0 * delta * delta))
        y_c = oy - c_val * ph
        pts_cheby.append((x_px, y_c))

        # Chernoff
        ch_val = min(1.0, math.exp(-20.0 * delta * delta / 3.0))
        y_ch = oy - ch_val * ph
        pts_chernoff.append((x_px, y_ch))

    # Перетворення у шлях
    path_m = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_markov)
    path_c = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_cheby)
    path_ch = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_chernoff)

    frags.append(path(path_m, stroke=RED_S, sw=2.5, fill="none"))
    frags.append(path(path_c, stroke=AMBER_S, sw=2.5, fill="none", dash="6,3"))
    frags.append(path(path_ch, stroke=GREEN_S, sw=3, fill="none"))

    # Легенда збоку
    lx, ly = 580, 100
    frags.append(rect(lx, ly, 270, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 135, ly + 25, "Порівняльний аналіз меж", size=13, bold=True, color="#1e293b"))

    # Межа Маркова
    frags.append(line(lx + 20, ly + 65, lx + 50, ly + 65, color=RED_S, sw=2.5))
    frags.append(text(lx + 60, ly + 60, "Нерівність Маркова", size=12, bold=True, color=RED_S))
    frags.append(text(lx + 60, ly + 78, "O(1/δ) — лінійне спадання", size=11, color="#64748b"))

    # Межа Чебишова
    frags.append(line(lx + 20, ly + 135, lx + 50, ly + 135, color=AMBER_S, sw=2.5, dash="6,3"))
    frags.append(text(lx + 60, ly + 130, "Нерівність Чебишова", size=12, bold=True, color=AMBER_S))
    frags.append(text(lx + 60, ly + 148, "O(1/δ²) — степеневе спадання", size=11, color="#64748b"))

    # Межа Чернова
    frags.append(line(lx + 20, ly + 205, lx + 50, ly + 205, color=GREEN_S, sw=3))
    frags.append(text(lx + 60, ly + 200, "Нерівність Чернова", size=12, bold=True, color=GREEN_S))
    frags.append(text(lx + 60, ly + 218, "exp(-μδ²/3) — експоненціальне!", size=11, bold=True, color=GREEN_S))

    # Пояснювальний блок
    b_note, _, _ = textbox(lx + 135, ly + 265, "Чернов дає експоненціально\nточнішу межу для сум\nнезалежних величин", size=11, fill=TEAL_F, stroke=TEAL_S, pad=6)
    frags.append(b_note)

    render(os.path.join(IMG, "fig1-tail-comparison.svg"), W, H, *frags)


def fig_mgf_derivation():
    """fig2-mgf-derivation.svg: Схема методу Чернова (перетворення MGF та мінімізація t)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Логічний ланцюг трюку Чернова (Moment-Generating Function Method)", size=16, bold=True, color="#1e293b"))

    # Крок 1: Вхідна сума
    b1, _, _ = textbox(150, 120, "1. Сума випадкових величин\nX = ∑ Xᵢ (незалежні)", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S, pad=10)
    
    # Крок 2: Експоненціальне перетворення
    b2, _, _ = textbox(440, 120, "2. Монотонне перетворення t > 0\nPr[X ≥ a] = Pr[eᵗˣ ≥ eᵗᵃ]", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S, pad=10)

    # Крок 3: Нерівність Маркова
    b3, _, _ = textbox(730, 120, "3. Межа Маркова для eᵗˣ\nPr[eᵗˣ ≥ eᵗᵃ] ≤ E[eᵗˣ] / eᵗᵃ", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S, pad=10)

    # Крок 4: Факторизація незалежності
    b4, _, _ = textbox(295, 270, "4. Незалежність → добуток моментів\nE[eᵗˣ] = ∏ E[eᵗˣⁱ] ≤ eᵐ⁽ᵉᵗ⁻¹⁾", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S, pad=10)

    # Крок 5: Мінімізація за t
    b5, _, _ = textbox(615, 270, "5. Мінімізація за параметром t > 0\nt* = ln(1 + δ) → exp(-μδ²/3)", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S, pad=10)

    frags += [b1, b2, b3, b4, b5]

    # Стрілки зв'язку
    frags.append(arrow(260, 120, 325, 120, color=BLUE_S, sw=2))
    frags.append(arrow(555, 120, 620, 120, color=PURPLE_S, sw=2))
    frags.append(arrow(730, 160, 420, 230, color=AMBER_S, sw=2))
    frags.append(arrow(435, 270, 480, 270, color=TEAL_S, sw=2))

    # Висновкова рамка
    frags.append(rect(140, 345, 600, 45, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(440, 368, "Результат: Експоненціально гостра межа концентрації навколо E[X]", size=13, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig2-mgf-derivation.svg"), W, H, *frags)


def fig_load_balancing():
    """fig3-load-balancing.svg: Концентрація максимального навантаження в задачі про кульки та кошики."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Розподіл n кульок у n кошиків (Balls & Bins Load Balancing)", size=16, bold=True, color="#1e293b"))

    # 5 кошиків на схемі
    bins_x = [100, 240, 380, 520, 660]
    bin_w = 90
    bin_h = 180
    base_y = 310

    counts = [2, 6, 3, 1, 2] # Один кошик має спайк = 6
    mean_val = 2.8

    for i, bx in enumerate(bins_x):
        # Малювання кошика
        frags.append(rect(bx, base_y - bin_h, bin_w, bin_h, fill="#ffffff", stroke="#94a3b8", sw=2, rx=4))
        frags.append(text(bx + bin_w/2, base_y + 22, f"Кошик {i+1}", size=12, bold=True, color="#475569"))

        # Кульки всередині
        cnt = counts[i]
        for c in range(cnt):
            cy = base_y - 18 - c * 24
            cx = bx + bin_w/2
            color_f = RED_F if cnt > 4 else BLUE_F
            color_s = RED_S if cnt > 4 else BLUE_S
            frags.append(circle(cx, cy, 10, fill=color_f, stroke=color_s, sw=1.5))

    # Пунктирна лінія середнього значення (Mean)
    mean_y = base_y - mean_val * 24
    frags.append(line(70, mean_y, 770, mean_y, color=AMBER_S, sw=2, dash="6,4"))
    frags.append(text(795, mean_y + 4, "Середнє μ = 1", size=11, bold=True, color=AMBER_S))

    # Позначення пікового навантаження (Max Load)
    peak_y = base_y - 6 * 24
    frags.append(line(70, peak_y - 12, 770, peak_y - 12, color=RED_S, sw=1.5, dash="3,3"))
    frags.append(text(795, peak_y - 8, "Макс O(log n / log log n)", size=11, bold=True, color=RED_S))

    # Пояснювальний блок знизу
    b_exp, _, _ = textbox(440, 375, "Нерівність Чернова гарантує, що з ймовірністю ≥ 1 - 1/n жоден з n кошиків\nне перевищить навантаження O(log n / log log n) при рівномірному хешуванні.", size=12, fill=GREEN_F, stroke=GREEN_S, pad=10)
    frags.append(b_exp)

    render(os.path.join(IMG, "fig3-load-balancing.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_tail_comparison()
    fig_mgf_derivation()
    fig_load_balancing()
    print("Всі фігури успішно згенеровано.")
