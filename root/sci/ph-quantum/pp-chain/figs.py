# -*- coding: utf-8 -*-
import sys, os
import math

# sys.path for svgkit (4 levels up from topic folder to scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def draw_pp_chain_branches(path):
    w, h = 960, 620
    frags = []

    # Background card
    frags.append(rect(15, 15, 930, 590, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Схема гілкування протон-протонного ланцюжка (pp-chain)", size=17, bold=True, color=INK))

    # Phase 1: Initiation
    box1, w1, h1 = textbox(w/2, 100, "1. Стадія ініціації (утворення дейтерію)\np + p → ²H + e⁺ + νₑ  (99.77%, Q = 1.442 МЕв)\np + e⁻ + p → ²H + νₑ  (pep, 0.23%, Q = 1.442 МЕв)", size=12, fill="#e0f2fe", stroke="#0284c7", sw=1.5)
    frags.append(box1)

    # Arrow down
    frags.append(arrow(w/2, 135, w/2, 165, color="#0284c7", sw=2))

    # Phase 2: Helium-3 formation
    box2, w2, h2 = textbox(w/2, 195, "2. Утворення гелію-3\n²H + p → ³He + γ  (100%, Q = 5.49 МЕв, τ ~ 1 сек)", size=12, fill="#fef3c7", stroke="#d97706", sw=1.5)
    frags.append(box2)

    # Arrow down to branching
    frags.append(arrow(w/2, 225, w/2, 265, color="#d97706", sw=2))

    # Branching label
    frags.append(text(w/2, 260, "Конкурентні шляхи утилізації ³He (у ядрі Сонця)", size=11, bold=True, color=MUTED))

    # Branch coordinates
    x_pp1 = 140
    x_pp2 = 380
    x_pp3 = 620
    x_pp4 = 830
    y_branch = 310

    # Branch split lines
    frags.append(line(w/2, 268, x_pp1, y_branch, color=LINE, sw=1.5))
    frags.append(line(w/2, 268, x_pp2, y_branch, color=LINE, sw=1.5))
    frags.append(line(w/2, 268, x_pp3, y_branch, color=LINE, sw=1.5))
    frags.append(line(w/2, 268, x_pp4, y_branch, color=LINE, sw=1.5))

    # pp-I Branch
    b1_text = "pp-I гілка (~85.8%)\n\n³He + ³He → ⁴He + 2p\n\nQ_eff = 26.20 МЕв\n⟨E_ν⟩ = 0.265 МЕв"
    frags.append(fitbox(x_pp1 - 105, y_branch + 5, 210, 190, b1_text, size=11, fill="#dcfce7", stroke="#16a34a", sw=1.5))

    # pp-II Branch
    b2_text = "pp-II гілка (~14.1%)\n\n³He + ⁴He → ⁷Be + γ\n⁷Be + e⁻ → ⁷Li + νₑ\n⁷Li + p → 2 ⁴He\n\nQ_eff = 25.66 МЕв\nE_ν = 0.862 МЕв"
    frags.append(fitbox(x_pp2 - 105, y_branch + 5, 210, 190, b2_text, size=11, fill="#fef9c3", stroke="#ca8a04", sw=1.5))

    # pp-III Branch
    b3_text = "pp-III гілка (~0.02%)\n\n³He + ⁴He → ⁷Be + γ\n⁷Be + p → ⁸B + γ\n⁸B → ⁸Be* + e⁺ + νₑ\n⁸Be* → 2 ⁴He\n\nQ_eff = 19.72 МЕв\n⟨E_ν⟩ ≈ 6.7 МЕв"
    frags.append(fitbox(x_pp3 - 105, y_branch + 5, 210, 190, b3_text, size=11, fill="#fee2e2", stroke="#dc2626", sw=1.5))

    # pp-IV (hep) Branch
    b4_text = "pp-IV / hep (~2·10⁻⁵%)\n\n³He + p → ⁴He + e⁺ + νₑ\n\nQ_eff = 18.77 МЕв\nE_ν_max = 18.77 МЕв"
    frags.append(fitbox(x_pp4 - 85, y_branch + 5, 170, 190, b4_text, size=10, fill="#f3e8ff", stroke="#9333ea", sw=1.5))

    # Convergence arrows to bottom
    y_conv = 530
    frags.append(arrow(x_pp1, y_branch + 195, w/2 - 150, y_conv, color="#16a34a", sw=1.5))
    frags.append(arrow(x_pp2, y_branch + 195, w/2 - 50, y_conv, color="#ca8a04", sw=1.5))
    frags.append(arrow(x_pp3, y_branch + 195, w/2 + 50, y_conv, color="#dc2626", sw=1.5))
    frags.append(arrow(x_pp4, y_branch + 195, w/2 + 150, y_conv, color="#9333ea", sw=1.5))

    # Final summary box
    box_sum, ws, hs = textbox(w/2, y_conv + 35, "Підсумковий енергетичний баланс усіх гілок:\n4 p → ⁴He + 2 e⁺ + 2 νₑ + 26.73 МЕв", size=13, bold=True, fill="#f3f4f6", stroke=INK, sw=1.8)
    frags.append(box_sum)

    return render(path, w, h, *frags)

def draw_gamow_peak_pp(path):
    w, h = 820, 520
    frags = []

    frags.append(rect(15, 15, 790, 490, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 45, "Пік Ґамова для протон-протонного синтезу при T = 15.7 МК", size=16, bold=True, color=INK))

    # Graph Area
    gx0, gy0 = 90, 430
    gw, gh = 670, 330

    # Axes
    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.8))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.8))

    frags.append(text(gx0 + gw/2, gy0 + 38, "Кінетична енергія E (кЕв)", size=12, bold=True, color=INK))
    frags.append(text(gx0 + 10, gy0 - gh - 10, "Ймовірність / Густина стану (відн. од.)", size=11, bold=True, color=INK, anchor="start"))

    def e2x(e):
        return gx0 + (e / 25.0) * gw

    def y2py(v):
        return gy0 - v * (gh - 40)

    # Grid & Ticks (stop grid lines before legend box y = 240)
    for e in range(0, 26, 5):
        x = e2x(e)
        frags.append(line(x, gy0, x, gy0 + 5, color=INK, sw=1))
        frags.append(text(x, gy0 + 20, str(e), size=11, color=INK))
        if e > 0:
            grid_top = gy0 - gh + 140 if x > gx0 + gw - 280 else gy0 - gh
            frags.append(line(x, gy0, x, grid_top, color="#f3f4f6", sw=1))

    kT = 1.353
    b = 31.28

    e_step = 0.2
    steps = int(25.0 / e_step) + 1

    raw_mb = []
    raw_tun = []
    raw_gam = []

    for i in range(steps):
        e = i * e_step
        if e < 0.1:
            mb = 0
            tun = 0
            gam = 0
        else:
            mb = e * math.exp(-e / kT)
            tun = math.exp(-b / math.sqrt(e))
            gam = mb * tun
        raw_mb.append((e, mb))
        raw_tun.append((e, tun))
        raw_gam.append((e, gam))

    max_mb = max(v for _, v in raw_mb)
    max_gam = max(v for _, v in raw_gam)

    path_mb = []
    path_tun = []
    path_gam = []
    poly_gam = [(e2x(0), gy0)]

    for i in range(steps):
        e, mb = raw_mb[i]
        _, tun = raw_tun[i]
        _, gam = raw_gam[i]

        x = e2x(e)
        y_mb = y2py(mb / max_mb * 0.75)
        tun_val = math.exp(-b / math.sqrt(max(0.1, e))) / math.exp(-b / math.sqrt(25.0))
        y_tun = y2py(tun_val * 0.40)
        y_gam = y2py(gam / max_gam * 0.90)

        path_mb.append("%.1f,%.1f" % (x, y_mb))
        path_tun.append("%.1f,%.1f" % (x, y_tun))
        path_gam.append("%.1f,%.1f" % (x, y_gam))
        poly_gam.append((x, y_gam))

    poly_gam.append((e2x(25), gy0))

    # Shaded Gamow Peak area
    poly_str = " ".join("%.1f,%.1f" % pt for pt in poly_gam)
    frags.append('<polygon points="%s" fill="#dcfce7" stroke="none"/>' % poly_str)

    # Draw curves
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_mb), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_tun), NEG))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_gam), FIELD))

    # Key Markers
    x_kt = e2x(1.35)
    frags.append(line(x_kt, gy0, x_kt, gy0 - gh + 60, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(x_kt, gy0 - gh + 45, "k_B T = 1.35 кЕв", size=10, bold=True, color=POS))

    x_e0 = e2x(5.9)
    frags.append(line(x_e0, gy0, x_e0, gy0 - gh + 20, color=FIELD, sw=2, dash="3,3"))
    frags.append(text(x_e0, gy0 - gh + 10, "E₀ ≈ 5.9 кЕв (Пік Ґамова)", size=11, bold=True, color=FIELD))

    # Legend box placed in top right (x: 480..740, y: 110..220)
    leg_box = fitbox(gx0 + gw - 270, gy0 - gh + 20, 260, 110,
                     "Легенда:\n— Максвелл-Больцман f(E)\n— Проникність бар'єра P(E)\n— Вікно Ґамова I(E) = f(E)·P(E)",
                     size=11, fill="#ffffff", stroke="#9ca3af")
    frags.append(leg_box)

    return render(path, w, h, *frags)

def draw_solar_neutrino_spectrum(path):
    w, h = 900, 540
    frags = []

    frags.append(rect(15, 15, 870, 510, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Енергетичний спектр сонячних нейтрино та пороги детекторів", size=16, bold=True, color=INK))

    gx0, gy0 = 90, 440
    gw, gh = 760, 340

    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.8))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.8))

    frags.append(text(gx0 + gw/2, gy0 + 40, "Енергія нейтрино E_ν (МЕв)", size=12, bold=True, color=INK))
    frags.append(text(gx0 + 10, gy0 - gh - 10, "Потік нейтрино (см⁻² с⁻¹ МЕв⁻¹)", size=11, bold=True, color=INK, anchor="start"))

    def e2x(e):
        if e <= 1.0:
            return gx0 + (e / 1.0) * 220
        elif e <= 10.0:
            return gx0 + 220 + ((e - 1.0) / 9.0) * 350
        else:
            return gx0 + 570 + ((e - 10.0) / 10.0) * 180

    ticks = [0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0]
    for t in ticks:
        x = e2x(t)
        frags.append(line(x, gy0, x, gy0 + 5, color=INK, sw=1))
        frags.append(text(x, gy0 + 20, str(t), size=10, color=INK))
        frags.append(line(x, gy0, x, gy0 - gh + 50, color="#f3f4f6", sw=1))

    # Curve starts at gy0 - 250
    x_pp_max = e2x(0.42)
    frags.append(line(gx0, gy0 - 250, x_pp_max, gy0, color="#2563eb", sw=2.5))
    # Box placed above at gy0 - 305 (y: 135) where line does not pass
    frags.append(fitbox(gx0 + 10, gy0 - 305, 90, 35, "pp нейтрино\n(≤0.42 МЕв)", size=9, fill="#dbeafe", stroke="#2563eb"))

    x_8b_start = e2x(1.5)
    x_8b_peak = e2x(6.0)
    x_8b_end = e2x(15.0)
    frags.append(line(x_8b_start, gy0 - 40, x_8b_peak, gy0 - 180, color="#dc2626", sw=2.5))
    frags.append(line(x_8b_peak, gy0 - 180, x_8b_end, gy0, color="#dc2626", sw=2.5))
    frags.append(fitbox(x_8b_peak - 45, gy0 - 215, 110, 35, "⁸B нейтрино\n(E ≤ 15 МЕв)", size=10, fill="#fee2e2", stroke="#dc2626"))

    x_hep_end = e2x(18.77)
    frags.append(line(e2x(5.0), gy0 - 20, x_hep_end, gy0, color="#9333ea", sw=2))
    frags.append(text(x_hep_end - 40, gy0 - 35, "hep (до 18.77 МЕв)", size=10, color="#9333ea", bold=True))

    x_7be1 = e2x(0.384)
    frags.append(arrow(x_7be1, gy0, x_7be1, gy0 - 230, color="#d97706", sw=2.5))
    frags.append(text(x_7be1 - 10, gy0 - 240, "⁷Be (0.38 МЕв)", size=9, color="#d97706", bold=True))

    x_7be2 = e2x(0.862)
    frags.append(arrow(x_7be2, gy0, x_7be2, gy0 - 260, color="#d97706", sw=2.5))
    frags.append(text(x_7be2 + 25, gy0 - 265, "⁷Be (0.86 МЕв)", size=10, color="#d97706", bold=True))

    x_pep = e2x(1.44)
    frags.append(arrow(x_pep, gy0, x_pep, gy0 - 180, color="#059669", sw=2.5))
    frags.append(text(x_pep + 25, gy0 - 185, "pep (1.44 МЕв)", size=10, color="#059669", bold=True))

    x_gal = e2x(0.233)
    frags.append(line(x_gal, gy0, x_gal, gy0 - gh + 50, color="#6b7280", sw=1.5, dash="4,4"))
    frags.append(text(x_gal, gy0 - gh + 35, "GALLEX/SAGE (0.23 МЕв)", size=9, bold=True, color="#374151"))

    x_hom = e2x(0.814)
    frags.append(line(x_hom, gy0, x_hom, gy0 - gh + 50, color="#6b7280", sw=1.5, dash="4,4"))
    frags.append(text(x_hom, gy0 - gh + 35, "Homestake (0.81 МЕв)", size=9, bold=True, color="#374151"))

    x_sno = e2x(5.0)
    frags.append(line(x_sno, gy0, x_sno, gy0 - gh + 50, color="#6b7280", sw=1.5, dash="4,4"))
    frags.append(text(x_sno, gy0 - gh + 35, "Super-K / SNO (~5 МЕв)", size=9, bold=True, color="#374151"))

    return render(path, w, h, *frags)

def main():
    img_dir = make_img_dir()
    draw_pp_chain_branches(os.path.join(img_dir, "pp-chain-branches.svg"))
    draw_gamow_peak_pp(os.path.join(img_dir, "gamow-peak-pp.svg"))
    draw_solar_neutrino_spectrum(os.path.join(img_dir, "solar-neutrino-spectrum.svg"))
    print("Generated 3 SVG figures in", img_dir)

if __name__ == "__main__":
    main()
