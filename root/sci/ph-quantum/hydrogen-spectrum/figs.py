# -*- coding: utf-8 -*-
"""Фігури для теми «Спектр водню і стала Рідберга» (book/physics/quantum-mechanics/hydrogen-spectrum)."""
import sys, os
import math

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
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def path_svg(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def fig_energy_levels():
    """energy-levels.svg: Енергетичні рівні атома водню та спектральні серії (Лайман, Бальмер, Пашен, Брекет)."""
    W, H = 880, 480
    frags = []

    frags.append(rect(10, 10, 860, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Енергетичні рівні атома водню E_n = -13.606 еВ / n² та спектральні серії", size=16, bold=True, color="#1e293b"))

    # Вісь енергії E (еВ) ліворуч
    frags.append(line(70, 70, 70, 430, color="#334155", sw=2.0))
    frags.append(text(45, 65, "E (еВ)", size=12, bold=True, color="#1e293b"))

    # Рівні енергії: n = 1 (-13.6 eV), n = 2 (-3.4 eV), n = 3 (-1.51 eV), n = 4 (-0.85 eV), n = 5 (-0.54 eV), n = ∞ (0 eV)
    # Координати по Y: E=0 at Y=90, E=-13.6 at Y=410. Scale: Y = 90 + (E / -13.6) * 320
    levels = [
        (1, -13.606, 410, "#1e293b"),
        (2, -3.401, 250, "#2563eb"),
        (3, -1.512, 170, "#0d9488"),
        (4, -0.850, 130, "#7e22ce"),
        (5, -0.544, 110, "#e08a1e"),
    ]

    # Границя іонізації E = 0 еВ
    frags.append(line(70, 90, 830, 90, color="#dc2626", sw=1.8, dash="4,4"))
    frags.append(text(840, 94, "E = 0 еВ (Іонізація)", size=10, bold=True, color="#dc2626"))

    # Малювання рівнів n = 1..5
    for n, ev, y, col in levels:
        frags.append(line(70, y, 830, y, color=col, sw=2.2))
        frags.append(text(50, y + 4, f"{ev:.2f}", size=10, color="#475569"))
        frags.append(text(835, y + 4, f"n = {n}", size=11, bold=True, color=col))

    # Спектральні серії (вертикальні переходи зі стрілками вниз)
    # Серія Лаймана (переходи на n=1, УФ область) - X = 160..240
    frags.append(rect(140, 60, 120, 380, fill=PURPLE_F, stroke="none"))
    frags.append(text(200, 445, "Серія Лаймана (УФ)", size=11, bold=True, color=PURPLE_S))
    # n=2->1, n=3->1, n=4->1, n=5->1
    for i, (n_src, _, y_src, _) in enumerate(levels[1:]):
        x = 160 + i * 25
        frags.append(line(x, y_src, x, 410, color=PURPLE_S, sw=1.8))
        frags.append(path_svg(f"M {x-4} 402 L {x} 410 L {x+4} 402", fill=PURPLE_S, stroke=PURPLE_S, sw=1.0))

    # Серія Бальмера (переходи на n=2, Видима область) - X = 320..420
    frags.append(rect(300, 60, 140, 380, fill=BLUE_F, stroke="none"))
    frags.append(text(370, 445, "Серія Бальмера (Видима)", size=11, bold=True, color=BLUE_S))
    # n=3->2 (H-alpha 656nm), n=4->2 (H-beta 486nm), n=5->2 (H-gamma 434nm)
    balmer_colors = ["#dc2626", "#0284c7", "#4338ca", "#6b21a8"]
    for i, (n_src, _, y_src, _) in enumerate(levels[2:]):
        x = 320 + i * 30
        c = balmer_colors[i % len(balmer_colors)]
        frags.append(line(x, y_src, x, 250, color=c, sw=2.2))
        frags.append(path_svg(f"M {x-4} 242 L {x} 250 L {x+4} 242", fill=c, stroke=c, sw=1.0))

    # Серія Пашена (переходи на n=3, ІЧ область) - X = 490..570
    frags.append(rect(470, 60, 120, 380, fill=RED_F, stroke="none"))
    frags.append(text(530, 445, "Серія Пашена (Близька ІЧ)", size=11, bold=True, color=RED_S))
    for i, (n_src, _, y_src, _) in enumerate(levels[3:]):
        x = 490 + i * 30
        frags.append(line(x, y_src, x, 170, color=RED_S, sw=1.8))
        frags.append(path_svg(f"M {x-4} 162 L {x} 170 L {x+4} 162", fill=RED_S, stroke=RED_S, sw=1.0))

    # Серія Брекета (переходи на n=4, Далека ІЧ) - X = 630..690
    frags.append(rect(610, 60, 100, 380, fill=AMBER_F, stroke="none"))
    frags.append(text(660, 445, "Серія Брекета (ІЧ)", size=11, bold=True, color=AMBER_S))
    for i, (n_src, _, y_src, _) in enumerate(levels[4:]):
        x = 630 + i * 30
        frags.append(line(x, y_src, x, 130, color=AMBER_S, sw=1.8))
        frags.append(path_svg(f"M {x-4} 122 L {x} 130 L {x+4} 122", fill=AMBER_S, stroke=AMBER_S, sw=1.0))

    # Текстова вставка з формулою Рідберга
    b_ryd, _, _ = textbox(770, 220, "Формула Рідберга:\n1/λ = R_∞ (1/n₁² - 1/n₂²)\n\nR_∞ ≈ 1.09737 × 10⁷ м⁻¹", size=10, bold=True, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_ryd)

    render(os.path.join(IMG, "energy-levels.svg"), W, H, *frags)


def fig_balmer_series():
    """balmer-series.svg: Спектральні лінії серії Бальмера у видимому діапазоні довжин хвиль."""
    W, H = 880, 320
    frags = []

    frags.append(rect(10, 10, 860, 300, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=10))
    frags.append(text(440, 32, "Спектральні лінії серії Бальмера атома водню у видимому світлі", size=16, bold=True, color="#f8fafc"))

    # Спектральна шкала довжин хвиль λ від 350 нм до 700 нм
    x_from_wl = lambda wl: 80 + (wl - 350) / 350.0 * 720

    # Фон спектральної шкали
    frags.append(rect(70, 70, 740, 120, fill="#020617", stroke="#475569", sw=1.5))

    lines_info = [
        ("H-α (3→2)", 656.3, "#ef4444", "656.3 нм"),
        ("H-β (4→2)", 486.1, "#38bdf8", "486.1 нм"),
        ("H-γ (5→2)", 434.0, "#818cf8", "434.0 нм"),
        ("H-δ (6→2)", 410.2, "#c084fc", "410.2 нм"),
        ("Границя (∞→2)", 364.6, "#94a3b8", "364.6 нм"),
    ]

    for label, wl, color, wl_text in lines_info:
        x = x_from_wl(wl)
        frags.append(line(x, 70, x, 190, color=color, sw=3.0))
        frags.append(line(x, 190, x, 215, color=color, sw=1.0, dash="2,2"))
        frags.append(text(x, 230, label, size=11, bold=True, color=color))
        frags.append(text(x, 248, wl_text, size=10, color="#94a3b8"))

    frags.append(line(70, 270, 810, 270, color="#cbd5e1", sw=1.5))
    for wl in range(350, 750, 50):
        x = x_from_wl(wl)
        frags.append(line(x, 270, x, 276, color="#cbd5e1", sw=1.5))
        frags.append(text(x, 290, f"{wl} нм", size=10, color="#cbd5e1"))

    render(os.path.join(IMG, "balmer-series.svg"), W, H, *frags)


def fig_potential_levels():
    """potential-levels.svg: Кулонівська потенціальна яма та радіальний розподіл ймовірності станів 1s, 2s, 2p."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Кулонівський потенціал V(r) = -e²/(4πε₀r) та квантові стани атома водню", size=16, bold=True, color="#1e293b"))

    cx = 220
    cy_zero = 100

    frags.append(line(cx, cy_zero, cx, 370, color="#334155", sw=1.8))
    frags.append(line(60, cy_zero, 500, cy_zero, color="#dc2626", sw=1.5, dash="4,4"))
    frags.append(text(510, cy_zero + 4, "E = 0 (Вільний електрон)", size=10, bold=True, color="#dc2626"))

    pts_v = []
    for x_px in range(232, 490, 2):
        r_a0 = (x_px - cx) / 50.0
        v_ev = -13.606 * (1.0 / r_a0)
        y_px = cy_zero + (-v_ev / 13.606) * 180.0
        if y_px < 370:
            pts_v.append((x_px, y_px))

    if pts_v:
        path_v = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_v)
        frags.append(path_svg(path_v, fill="none", stroke="#64748b", sw=2.5))
        frags.append(text(420, 340, "V(r) = -e² / (4πε₀r)", size=12, bold=True, color="#64748b"))

    frags.append(line(cx, 280, 480, 280, color="#1e293b", sw=2.0))
    frags.append(text(cx + 15, 275, "n = 1 (1s, -13.60 еВ)", size=11, bold=True, color="#1e293b"))

    frags.append(line(cx, 145, 480, 145, color="#2563eb", sw=2.0))
    frags.append(text(cx + 15, 140, "n = 2 (2s, 2p, -3.40 еВ)", size=11, bold=True, color="#2563eb"))

    frags.append(rect(540, 60, 310, 320, fill=GRAY_F, stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(695, 85, "Радіальна ймовірність P(r) = r²|R_{nl}(r)|²", size=12, bold=True, color="#1e293b"))

    frags.append(line(570, 340, 830, 340, color="#475569", sw=1.5))
    frags.append(line(570, 100, 570, 340, color="#475569", sw=1.5))
    frags.append(text(835, 344, "r / a₀", size=11, color="#475569"))

    pts_1s = []
    for x in range(0, 240, 2):
        r = x / 30.0
        p = 4.0 * (r**2) * math.exp(-2.0 * r)
        y = 340 - p * 150
        pts_1s.append((570 + x, y))

    path_1s = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_1s)
    frags.append(path_svg(path_1s, fill="none", stroke="#1e293b", sw=2.2))

    pts_2p = []
    for x in range(0, 240, 2):
        r = x / 30.0
        p = (1.0 / 24.0) * (r**4) * math.exp(-r) * 3.5
        y = 340 - p * 120
        pts_2p.append((570 + x, y))

    path_2p = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_2p)
    frags.append(path_svg(path_2p, fill="none", stroke="#2563eb", sw=2.0, dash="4,3"))

    b_leg, _, _ = textbox(700, 130, "— 1s (максимум при r = a₀)\n- - 2p (максимум при r = 4a₀)", size=10, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b_leg)

    render(os.path.join(IMG, "potential-levels.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_energy_levels()
    fig_balmer_series()
    fig_potential_levels()
    print("Усі фігури для hydrogen-spectrum успішно згенеровано у", IMG)
