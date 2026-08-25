# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Хімічний потенціал'."""
import os
import sys

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')

def make_thermo_potentials_cube():
    """Фігура 1: Схема термодинамічних потенціалів та зв'язок з хімічним потенціалом."""
    w, h = 780, 430
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    out.append(text(w / 2, 28, "Термодинамічні потенціали та часткові похідні по числу частинок N", size=16, bold=True))

    cards = [
        ("Внутрішня енергия U(S, V, N)", 40, 60, 330, 145, "dU = T·dS - P·dV + μ·dN", "(∂U / ∂N)_(S, V) = μ", POS),
        ("Вільна енергія Гельмгольца F(T, V, N)", 410, 60, 330, 145, "dF = -S·dT - P·dV + μ·dN", "(∂F / ∂N)_(T, V) = μ", NEG),
        ("Ентальпія H(S, P, N)", 40, 235, 330, 145, "dH = T·dS + V·dP + μ·dN", "(∂H / ∂N)_(S, P) = μ", FIELD),
        ("Енергія Гіббса G(T, P, N)", 410, 235, 330, 145, "dG = -S·dT + V·dP + μ·dN", "(∂G / ∂N)_(T, P) = μ", "#8e44ad")
    ]

    for title_txt, x, y, cw, ch, diff_txt, deriv_txt, accent_col in cards:
        out.append(rect(x, y, cw, ch, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        out.append(rect(x, y, cw, 34, fill=accent_col, stroke=LINE, sw=1.5, rx=8))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="12" fill="%s" stroke="none"/>' % (x, y + 23, cw, accent_col))
        out.append(text(x + cw / 2, y + 22, title_txt, size=13, color="#ffffff", bold=True))
        
        out.append(text(x + cw / 2, y + 66, diff_txt, size=13, color=INK, bold=False))
        
        tb, tw_b, th_b = textbox(x + cw / 2, y + 110, deriv_txt, size=13, pad=6, fill="#ffffff", stroke=accent_col, sw=1.5, color=INK, bold=True)
        out.append(tb)

    out.append(text(w / 2, 408, "Для однокомпонентної системи: G(T, P, N) = N · μ(T, P)  ⇒  μ = g(T, P) (молярна/питома енергія Гіббса)", size=13, color=MUTED, italic=True))

    out.append('</svg>')
    return "\n".join(out)

def make_phase_equilibrium_mu():
    """Фігура 2: Фазова рівновага та напрямок дифузійного потоку частинок."""
    w, h = 780, 390
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    out.append(text(w / 2, 26, "Градієнт хімічного потенціалу Δμ як рушійна сила перенесення маси", size=16, bold=True))

    # Ліва система (Нерівновага: μ1 > μ2)
    out.append(rect(40, 60, 330, 270, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(205, 85, "Нерівноважний стан (μ₁ > μ₂)", size=14, color=POS, bold=True))

    out.append(rect(60, 110, 130, 150, fill="#eef6ff", stroke=NEG, sw=1.5, rx=6))
    out.append(text(125, 135, "Фаза 1 (Рідина)", size=13, color=NEG, bold=True))
    out.append(text(125, 170, "μ₁ (високий)", size=13, color=INK, bold=True))
    out.append(text(125, 215, "Високий тиск / N₁", size=11, color=MUTED))

    out.append(arrow(200, 185, 250, 185, color=POS, sw=2.5))
    out.append(text(225, 168, "Потік J_N", size=12, color=POS, bold=True))

    out.append(rect(260, 110, 95, 150, fill="#fff6ee", stroke=POS, sw=1.5, rx=6))
    out.append(text(307, 135, "Фаза 2 (Пара)", size=13, color=POS, bold=True))
    out.append(text(307, 170, "μ₂ (низький)", size=13, color=INK, bold=True))
    out.append(text(307, 215, "Пара розріджена", size=11, color=MUTED))

    out.append(text(205, 300, "Маса самовільно тече від вищого μ₁ до нижчого μ₂", size=12, color=INK, italic=True))

    # Права система (Рівновага: μ1 = μ2)
    out.append(rect(410, 60, 330, 270, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    out.append(text(575, 85, "Термодинамічна рівновага (μ₁ = μ₂)", size=14, color=FIELD, bold=True))

    out.append(rect(425, 110, 120, 150, fill="#eef9f2", stroke=FIELD, sw=1.5, rx=6))
    out.append(text(485, 135, "Фаза 1 (Рідина)", size=13, color=FIELD, bold=True))
    out.append(text(485, 170, "μ₁ = μ_рівн", size=13, color=INK, bold=True))
    out.append(text(485, 215, "Насичений стан", size=11, color=MUTED))

    # Двостороння стрілка рівноваги - розведемо стрілки та напис
    out.append(text(575, 145, "J_ввип = J_конд", size=11, color=FIELD, bold=True))
    out.append(arrow(550, 175, 600, 175, color=FIELD, sw=1.8))
    out.append(arrow(600, 195, 550, 195, color=FIELD, sw=1.8))

    out.append(rect(605, 110, 120, 150, fill="#eef9f2", stroke=FIELD, sw=1.5, rx=6))
    out.append(text(665, 135, "Фаза 2 (Пара)", size=13, color=FIELD, bold=True))
    out.append(text(665, 170, "μ₂ = μ_рівн", size=13, color=INK, bold=True))
    out.append(text(665, 215, "Насичена пара P_sat", size=11, color=MUTED))

    out.append(text(575, 300, "Випар і конденсація збалансовані: Δμ = 0", size=12, color=INK, italic=True))

    out.append(text(w / 2, 365, "Умова рівноваги фаз: T₁ = T₂,  P₁ = P₂,  μ₁(T, P) = μ₂(T, P)", size=13, color=MUTED, bold=True))

    out.append('</svg>')
    return "\n".join(out)

def make_quantum_mu_temperature():
    """Фігура 3: Температурна залежність хімічного потенціалу μ(T) для квантових та класичних газів."""
    w, h = 780, 430
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    out.append(text(w / 2, 26, "Залежність хімічного потенціалу μ від температури T для різних квантових статистик", size=15, bold=True))

    x0, y0 = 90, 230
    out.append(line(x0, 40, x0, 370, color=LINE, sw=2))
    out.append(line(x0, y0, 720, y0, color=LINE, sw=1.5, dash="4,4"))
    out.append(arrow(x0, y0, 735, y0, color=LINE, sw=2))

    out.append(text(x0 - 20, 50, "μ", size=16, color=INK, bold=True))
    out.append(text(735, y0 + 25, "Температура T", size=13, color=INK, anchor="end", bold=True))
    out.append(text(x0 - 25, y0 + 5, "0", size=13, color=MUTED))

    y_EF = 80
    out.append(circle(x0, y_EF, 4, fill=POS, stroke=POS))
    out.append(text(x0 - 35, y_EF + 5, "E_F", size=14, color=POS, bold=True))

    # Фермі-газ
    path_fermi = [
        (x0, y_EF),
        (160, 85),
        (250, 105),
        (360, 150),
        (460, y0),
        (560, 280),
        (670, 350)
    ]
    pts_f = " ".join(["%.1f,%.1f" % (px, py) for px, py in path_fermi])
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_f, POS))
    out.append(text(340, 85, "Фермі-газ (електрони в металі)", size=13, color=POS, bold=True))

    # Бозе-газ
    x_Tc = 280
    path_bose = [
        (x0, y0),
        (x_Tc, y0),
        (380, 255),
        (500, 295),
        (660, 345)
    ]
    pts_b = " ".join(["%.1f,%.1f" % (px, py) for px, py in path_bose])
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_b, FIELD))
    out.append(circle(x_Tc, y0, 4, fill=FIELD, stroke=FIELD))
    out.append(text(x_Tc, y0 - 14, "T_c (БКЕ)", size=13, color=FIELD, bold=True))
    out.append(text(190, y0 - 14, "μ = 0 (конденсат)", size=12, color=FIELD))
    out.append(text(410, 240, "Бозе-газ (гелій-4, атоми)", size=13, color=FIELD, bold=True))

    # Класичний газ
    path_class = [
        (x0 + 10, 248),
        (200, 265),
        (350, 290),
        (500, 320),
        (670, 355)
    ]
    pts_c = " ".join(["%.1f,%.1f" % (px, py) for px, py in path_class])
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (pts_c, NEG))
    out.append(text(470, 340, "Класичний ідеальний газ: μ = k_B T ln(n λ_dB³)", size=12, color=NEG, bold=True))

    out.append(text(w / 2, 405, "Високі T або низька густина: усі квантові статистики асимптотично прямують до класичної межі (μ < 0)", size=12, color=MUTED, italic=True))

    out.append('</svg>')
    return "\n".join(out)

def make_chemical_reaction_equilibrium():
    """Фігура 4: Баланс хімічних потенціалів у реакціях та умова рівноваги."""
    w, h = 780, 370
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    out.append(text(w / 2, 26, "Термодинаміка хімічної реакції: ν_A A + ν_B B ⇌ ν_C C + ν_D D", size=15, bold=True))

    out.append(rect(40, 70, 265, 160, fill="#eef6ff", stroke=NEG, sw=1.5, rx=8))
    out.append(text(172, 95, "Реагенти (A + B)", size=14, color=NEG, bold=True))
    out.append(text(172, 130, "Сумарний хімічний потенціал:", size=12, color=INK))
    out.append(text(172, 155, "μ_вхід = ν_A·μ_A + ν_B·μ_B", size=13, color=NEG, bold=True))
    out.append(text(172, 195, "При хімічному зсуві знижується G", size=11, color=MUTED))

    out.append(rect(335, 90, 110, 120, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    out.append(arrow(350, 135, 430, 135, color=POS, sw=2))
    out.append(arrow(430, 165, 350, 165, color=FIELD, sw=2))
    out.append(text(390, 120, "Пряма", size=11, color=POS, bold=True))
    out.append(text(390, 185, "Зворотна", size=11, color=FIELD, bold=True))

    out.append(rect(475, 70, 265, 160, fill="#eef9f2", stroke=FIELD, sw=1.5, rx=8))
    out.append(text(607, 95, "Продукти (C + D)", size=14, color=FIELD, bold=True))
    out.append(text(607, 130, "Сумарний хімічний потенціал:", size=12, color=INK))
    out.append(text(607, 155, "μ_вихід = ν_C·μ_C + ν_D·μ_D", size=13, color=FIELD, bold=True))
    out.append(text(607, 195, "Накопичення продуктів росте μ_вихід", size=11, color=MUTED))

    tb, tw_b, th_b = textbox(w / 2, 285, "Спорідненість реакції: ΔG_r = ∑ ν_i · μ_i\nУмова хімічної рівноваги: ΔG_r = 0  ⇒  ν_A·μ_A + ν_B·μ_B = ν_C·μ_C + ν_D·μ_D", size=13, pad=10, fill="#ffffff", stroke=POS, sw=2, color=INK, bold=True)
    out.append(tb)

    out.append(text(w / 2, 350, "При рівновазі сума хімічних потенціалів реагентів точно дорівнює сумі потенціалів продуктів", size=12, color=MUTED, italic=True))

    out.append('</svg>')
    return "\n".join(out)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    files = {
        'thermo-potentials-cube.svg': make_thermo_potentials_cube(),
        'phase-equilibrium-mu.svg': make_phase_equilibrium_mu(),
        'quantum-mu-temperature.svg': make_quantum_mu_temperature(),
        'chemical-reaction-equilibrium.svg': make_chemical_reaction_equilibrium(),
    }
    
    for filename, content in files.items():
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Згенеровано: %s" % filepath)

if __name__ == '__main__':
    main()
