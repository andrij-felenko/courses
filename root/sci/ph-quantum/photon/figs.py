# -*- coding: utf-8 -*-
"""Фігури для теми «Фотон» (book/physics/quantum-mechanics/photon)."""
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


def fig_photoelectric_compton():
    """photoelectric-compton.svg: Фотоелектричний ефект та комптонівське розсіювання."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Корпускулярний вияв фотона: передача енергії та імпульсу", size=16, bold=True, color="#1e293b"))

    # Дві панелі
    # Ліва: Фотоелектричний ефект
    frags.append(rect(25, 55, 405, 340, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(227, 80, "а) Фотоелектричний ефект (передача енергії)", size=13, bold=True, color="#1e293b"))

    # Метал (катод)
    frags.append(rect(45, 230, 140, 140, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(115, 290, "Катод (метал)", size=12, bold=True, color="#334155"))
    frags.append(text(115, 315, "Робота виходу W_out", size=11, color="#64748b"))

    # Фотони, що налітають
    frags.append(path_svg("M 45 130 Q 65 110 85 130 T 125 130 T 165 130", fill="none", stroke=AMBER_S, sw=2.2))
    frags.append(arrow(155, 130, 175, 145, color=AMBER_S, sw=2.0))
    b_photon, _, _ = textbox(110, 105, "Фотон\nE = h · ν", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_photon)

    # Вибитий фотоелектрон
    frags.append(arrow(150, 240, 370, 130, color=BLUE_S, sw=2.2))
    frags.append(circle(150, 240, 6, fill=BLUE_S, stroke="#ffffff", sw=1.2))
    b_electron, _, _ = textbox(300, 140, "Фотоелектрон\nE_k = h·ν - W_out", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_electron)

    # Формула Айнштайна
    b_eq1, _, _ = textbox(227, 360, "h · ν = W_out + E_k", size=12, bold=True, fill="#f1f5f9", stroke="#94a3b8")
    frags.append(b_eq1)

    # Права: Ефект Комптона
    frags.append(rect(450, 55, 405, 340, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(652, 80, "б) Ефект Комптона (передача імпульсу)", size=13, bold=True, color="#1e293b"))

    # Початковий електрон
    frags.append(circle(590, 220, 9, fill=BLUE_S, stroke="#ffffff", sw=1.5))
    frags.append(text(590, 245, "e⁻ (спокій)", size=11, bold=True, color=BLUE_S))

    # Налітаючий рентгенівський фотон
    frags.append(path_svg("M 465 220 Q 485 200 505 220 T 545 220 T 580 220", fill="none", stroke=RED_S, sw=2.2))
    frags.append(arrow(570, 220, 585, 220, color=RED_S, sw=2.0))
    frags.append(text(510, 195, "Фотон (λ, p = h/λ)", size=11, bold=True, color=RED_S))

    # Розсіяний фотон під кутом θ
    frags.append(path_svg("M 590 220 Q 640 160 690 140 T 780 100", fill="none", stroke=AMBER_S, sw=2.0))
    frags.append(arrow(760, 105, 790, 95, color=AMBER_S, sw=2.0))
    b_scat, _, _ = textbox(770, 140, "Розсіяний фотон\nλ' > λ (менша E')", size=10, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_scat)

    # Електрон віддачі
    frags.append(arrow(590, 220, 750, 310, color=BLUE_S, sw=2.2))
    frags.append(circle(750, 310, 8, fill=BLUE_S, stroke="#ffffff", sw=1.5))
    frags.append(text(765, 335, "Електрон віддачі p_e", size=11, bold=True, color=BLUE_S))

    # Кут θ
    frags.append(line(590, 220, 720, 220, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(path_svg("M 640 220 A 50 50 0 0 0 630 190", fill="none", stroke="#475569", sw=1.5))
    frags.append(text(650, 200, "θ", size=13, bold=True, color="#1e293b"))

    # Формула зсуву довжини хвилі
    b_eq2, _, _ = textbox(652, 360, "Δλ = λ' - λ = λ_C · (1 - cos θ)", size=12, bold=True, fill="#f1f5f9", stroke="#94a3b8")
    frags.append(b_eq2)

    render(os.path.join(IMG, "photoelectric-compton.svg"), W, H, *frags)


def fig_field_quantization_fock():
    """field-quantization-fock.svg: Квантування коливальних мод та фоківські стани."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Квантовий осцилятор поля: енергетичний спектр та фоківські стани |n⟩", size=16, bold=True, color="#1e293b"))

    # Параболічна потенціальна яма V(q)
    # Координати центру (440, 330)
    pts = []
    for x_val in range(-240, 245, 5):
        y_val = 330 - 0.0038 * (x_val ** 2)
        pts.append(f"{440 + x_val:.1f},{y_val:.1f}")
    frags.append(path_svg("M " + " L ".join(pts), fill="none", stroke="#94a3b8", sw=2.0))
    frags.append(text(690, 120, "V(q) = (1/2) m ω² q²", size=12, bold=True, color="#64748b"))

    # Рівні енергії E_n
    levels = [
        (0, 310, "|0⟩ (вакуум)", "E_0 = (1/2) ℏω"),
        (1, 260, "|1⟩ (1 фотон)", "E_1 = (3/2) ℏω"),
        (2, 210, "|2⟩ (2 фотони)", "E_2 = (5/2) ℏω"),
        (3, 160, "|3⟩ (3 фотони)", "E_3 = (7/2) ℏω"),
        (4, 110, "|n⟩ (n фотонів)", "E_n = ℏω (n + 1/2)")
    ]

    colors = [GRAY_S, TEAL_S, BLUE_S, PURPLE_S, RED_S]
    fills = [GRAY_F, TEAL_F, BLUE_F, PURPLE_F, RED_F]

    for idx, (n, y_pos, state_str, energy_str) in enumerate(levels):
        w_span = 140 + idx * 35
        frags.append(line(440 - w_span, y_pos, 440 + w_span, y_pos, color=colors[idx], sw=2.2))
        frags.append(text(440 - w_span - 70, y_pos + 4, state_str, size=12, bold=True, color=colors[idx]))
        frags.append(text(440 + w_span + 75, y_pos + 4, energy_str, size=11, color="#475569"))

    # Оператори народження та знищення
    # a^+ (народження)
    frags.append(arrow(320, 255, 320, 165, color=GREEN_S, sw=2.5))
    b_ap, _, _ = textbox(280, 210, "Народження a⁺\n|n⟩ → |n+1⟩", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_ap)

    # a (знищення)
    frags.append(arrow(560, 165, 560, 255, color=RED_S, sw=2.5))
    b_am, _, _ = textbox(605, 210, "Знищення a\n|n⟩ → |n-1⟩", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_am)

    # Відстань між рівнями ΔE = ℏω
    frags.append(line(440, 260, 440, 210, color=AMBER_S, sw=1.8, dash="3,3"))
    b_step, _, _ = textbox(440, 235, "ΔE = ℏω", size=10, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_step)

    render(os.path.join(IMG, "field-quantization-fock.svg"), W, H, *frags)


def fig_spad_avalanche_breakdown():
    """spad-avalanche-breakdown.svg: Детектування поодиноких фотонів у SPAD."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Однофотонний лавинний фотодіод (SPAD): Ґейгерівський режим та гасіння", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Структура p-n переходу під понаднапругою
    frags.append(rect(25, 55, 410, 340, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(230, 80, "а) Лавинне помноження носіїв (Geiger-mode)", size=13, bold=True, color="#1e293b"))

    # Зона збіднення p-n переходу
    frags.append(rect(50, 110, 360, 210, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(80, 130, "p⁺ шаруватості", size=11, bold=True, color="#475569"))
    frags.append(text(360, 130, "n⁺ контакт", size=11, bold=True, color="#475569"))

    # Високе електричне поле E > 3*10^5 V/cm
    frags.append(rect(140, 150, 180, 150, fill="#fee2e2", stroke=RED_S, sw=1.5, rx=4))
    frags.append(text(230, 170, "Область високого поля E", size=11, bold=True, color=RED_S))

    # Первинний фотон
    frags.append(path_svg("M 40 220 Q 60 200 80 220 T 120 220", fill="none", stroke=AMBER_S, sw=2.2))
    frags.append(arrow(110, 220, 130, 220, color=AMBER_S, sw=2.0))
    frags.append(text(80, 200, "Фотон hν", size=11, bold=True, color=AMBER_S))

    # Первинна e-h пара
    frags.append(circle(145, 220, 6, fill=BLUE_S, stroke="#ffffff", sw=1.2)) # e-
    frags.append(circle(145, 240, 6, fill=RED_S, stroke="#ffffff", sw=1.2))  # h+

    # Лавина ударної іонізації (розгалуження)
    frags.append(arrow(145, 220, 220, 190, color=BLUE_S, sw=1.8))
    frags.append(arrow(145, 240, 220, 270, color=RED_S, sw=1.8))

    # Вторинні пари
    for y_p in [180, 200, 260, 280]:
        frags.append(circle(220, y_p, 5, fill=BLUE_S if y_p < 230 else RED_S, stroke="#ffffff", sw=1.0))
        frags.append(arrow(220, y_p, 300, y_p + (-15 if y_p % 40 == 0 else 15), color=BLUE_S if y_p < 230 else RED_S, sw=1.5))

    for y_p2 in [165, 185, 205, 255, 275, 295]:
        frags.append(circle(300, y_p2, 4, fill=RED_S if y_p2 > 230 else BLUE_S, stroke="#ffffff", sw=1.0))

    b_av, _, _ = textbox(230, 345, "Струм лавини I_av ≈ 1-10 mA\n(коефіцієнт підсилення M > 10⁶)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_av)

    # Права панель: Цикл напруги V(t) та гасіння
    frags.append(rect(445, 55, 410, 340, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(650, 80, "б) Динаміка напруги V(t) та схеми гасіння", size=13, bold=True, color="#1e293b"))

    # Осі графіку V(t)
    frags.append(arrow(480, 320, 830, 320, color="#475569", sw=1.5)) # t
    frags.append(text(835, 320, "t", size=12, bold=True, color="#475569"))
    frags.append(arrow(480, 320, 480, 110, color="#475569", sw=1.5)) # V
    frags.append(text(480, 95, "V_bias", size=12, bold=True, color="#475569"))

    # Рівні V_BR та V_bias
    frags.append(line(480, 200, 820, 200, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(text(450, 200, "V_BR", size=11, bold=True, color="#64748b"))

    frags.append(line(480, 130, 820, 130, color=RED_S, sw=1.2, dash="4,4"))
    frags.append(text(445, 130, "V_bias", size=11, bold=True, color=RED_S))

    # Дельта V_over
    frags.append(line(810, 130, 810, 200, color=PURPLE_S, sw=1.5))
    frags.append(text(825, 165, "V_over", size=10, bold=True, color=PURPLE_S))

    # Крива V(t)
    # t0: чекання на V_bias; t1: прихід фотона, лавина; t2: гасіння до V_BR; t3: відновлення (reset)
    vt_path = "M 480 130 L 560 130 L 570 210 L 640 210 L 730 130 L 800 130"
    frags.append(path_svg(vt_path, fill="none", stroke=BLUE_S, sw=2.5))

    # Позначки подій
    frags.append(circle(560, 130, 4, fill=AMBER_S, stroke=AMBER_S))
    frags.append(text(560, 115, "hν", size=10, bold=True, color=AMBER_S))

    frags.append(text(605, 230, "Гасіння (Quenching)", size=10, bold=True, color=RED_S))
    frags.append(text(685, 160, "Відновлення (Reset)", size=10, bold=True, color=GREEN_S))

    b_dead, _, _ = textbox(650, 360, "Мертвий час (Dead time) τ_dead ≈ 10-50 ns", size=11, bold=True, fill="#f1f5f9", stroke="#94a3b8")
    frags.append(b_dead)

    render(os.path.join(IMG, "spad-avalanche-breakdown.svg"), W, H, *frags)


def fig_photon_helicity_spin():
    """photon-helicity-spin.svg: Геліцитність та поляризаційні стани фотона."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Спін та геліцитність фотона: двохкомпонентна спіральність λ = ±1", size=16, bold=True, color="#1e293b"))

    # Ліва панель: λ = +1 (права колова поляризація)
    frags.append(rect(25, 55, 405, 300, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(227, 80, "а) Права колова поляризація (λ = +1)", size=13, bold=True, color="#1e293b"))

    # Вісь поширення k (Z)
    frags.append(arrow(60, 200, 380, 200, color="#475569", sw=2.0))
    frags.append(text(385, 200, "k (Z)", size=12, bold=True, color="#475569"))

    # Спіральна лінія електромагнітного поля E(z)
    spiral1 = []
    for step in range(0, 260, 5):
        z = 70 + step
        ang = step * 0.08
        x_p = z
        y_p = 200 - 45 * math.sin(ang)
        spiral1.append(f"{x_p:.1f},{y_p:.1f}")
    frags.append(path_svg("M " + " L ".join(spiral1), fill="none", stroke=RED_S, sw=2.2))

    # Спін S за напрямком k
    frags.append(arrow(200, 200, 270, 200, color=GREEN_S, sw=3.0))
    frags.append(text(235, 180, "S (спін)", size=12, bold=True, color=GREEN_S))

    b_h1, _, _ = textbox(227, 315, "Геліцитність λ = (S · k) / |k| = +1\nСтан |λ = +1⟩", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_h1)

    # Права панель: λ = -1 (ліва колова поляризація)
    frags.append(rect(450, 55, 405, 300, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))
    frags.append(text(652, 80, "б) Ліва колова поляризація (λ = -1)", size=13, bold=True, color="#1e293b"))

    # Вісь поширення k (Z)
    frags.append(arrow(485, 200, 805, 200, color="#475569", sw=2.0))
    frags.append(text(810, 200, "k (Z)", size=12, bold=True, color="#475569"))

    # Спіральна лінія протилежного обертання
    spiral2 = []
    for step in range(0, 260, 5):
        z = 495 + step
        ang = step * 0.08
        x_p = z
        y_p = 200 + 45 * math.sin(ang)
        spiral2.append(f"{x_p:.1f},{y_p:.1f}")
    frags.append(path_svg("M " + " L ".join(spiral2), fill="none", stroke=BLUE_S, sw=2.2))

    # Спін S проти напрямку k
    frags.append(arrow(660, 200, 590, 200, color=GREEN_S, sw=3.0))
    frags.append(text(625, 180, "S (спін)", size=12, bold=True, color=GREEN_S))

    b_h2, _, _ = textbox(652, 315, "Геліцитність λ = (S · k) / |k| = -1\nСтан |λ = -1⟩", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_h2)

    render(os.path.join(IMG, "photon-helicity-spin.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_photoelectric_compton()
    fig_field_quantization_fock()
    fig_spad_avalanche_breakdown()
    fig_photon_helicity_spin()
    print("Всі фігури для фотона успішно згенеровано у img/!")
