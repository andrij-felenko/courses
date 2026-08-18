# -*- coding: utf-8 -*-
"""Фігури для теми «Корпускулярно-хвильовий дуалізм» (book/physics/quantum-mechanics/wave-particle-duality)."""
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


def ellipse_svg(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def fig_double_slit():
    """fig1-double-slit.svg: Двохщілинний експеримент для електронів з формуванням інтерференційної картини."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Двохщілинний експеримент для попоштучних електронів", size=16, bold=True, color="#1e293b"))

    # Джерело електронів (електронна гармата)
    frags.append(rect(30, 180, 100, 80, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=6))
    frags.append(text(80, 215, "Електронна", size=12, bold=True, color=AMBER_S))
    frags.append(text(80, 235, "гармата e⁻", size=12, bold=True, color=AMBER_S))

    # Виліт окремих електронів (точки-пакети)
    for (px, py) in [(140, 220), (170, 220), (200, 220)]:
        frags.append(circle(px, py, 4, fill=AMBER_S, stroke=AMBER_S))
        frags.append(ellipse_svg(px, py, 12, 6, fill="none", stroke=AMBER_S, sw=1.0, dash="2,2"))

    # Перегородка зі щілинами
    frags.append(rect(240, 60, 16, 120, fill="#334155", stroke="#1e293b"))
    frags.append(rect(240, 200, 16, 40, fill="#334155", stroke="#1e293b"))
    frags.append(rect(240, 260, 16, 120, fill="#334155", stroke="#1e293b"))

    # Підписи щілин A і B (рознесені подалі від прямокутника)
    frags.append(text(210, 190, "Щілина 1", size=11, bold=True, color="#0f172a"))
    frags.append(text(210, 250, "Щілина 2", size=11, bold=True, color="#0f172a"))

    # Хвильові фронти після щілин (дуги обрізані за радіусом 140)
    for r in range(25, 145, 30):
        # Від щілини 1 (cy = 180)
        frags.append(path_svg(f"M {256 + r*math.cos(0.5):.1f} {180 - r*math.sin(0.5):.1f} A {r} {r} 0 0 1 {256 + r*math.cos(0.5):.1f} {180 + r*math.sin(0.5):.1f}",
                              fill="none", stroke=PURPLE_S, sw=1.2, dash="3,3"))
        # Від щілини 2 (cy = 250)
        frags.append(path_svg(f"M {256 + r*math.cos(0.5):.1f} {250 - r*math.sin(0.5):.1f} A {r} {r} 0 0 1 {256 + r*math.cos(0.5):.1f} {250 + r*math.sin(0.5):.1f}",
                              fill="none", stroke=TEAL_S, sw=1.2, dash="3,3"))

    # Детекторний екран
    frags.append(rect(580, 60, 14, 320, fill="#e2e8f0", stroke="#475569", sw=2.0, rx=2))

    # Точкові влучання на детекторі (дискретність)
    dots_y = [75, 82, 115, 122, 128, 160, 165, 172, 178, 184, 210, 213, 215, 218, 220, 222, 225, 250, 255, 262, 268, 300, 305, 312, 345, 352]
    for dy in dots_y:
        frags.append(circle(587, dy, 2.5, fill=RED_S, stroke=RED_S))

    # Графік розподілу ймовірності P(y) = |ψ₁ + ψ₂|² праворуч від екрана
    curve_points = []
    cy_mid = 215
    for y_idx in range(60, 370, 2):
        dy = y_idx - cy_mid
        val = (math.cos(0.08 * dy))**2 * math.exp(- (dy/90)**2)
        px = 620 + val * 190
        curve_points.append((px, y_idx))

    d_curve = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in curve_points)
    frags.append(path_svg(d_curve, fill="none", stroke=BLUE_S, sw=2.5))
    frags.append(line(620, 60, 620, 370, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Заповнення під кривою ймовірності
    d_fill = f"M 620 60 " + " ".join(f"L {px:.1f} {py:.1f}" for px, py in curve_points) + " L 620 370 Z"
    frags.append(path_svg(d_fill, fill=BLUE_F, stroke="none"))

    # Текстові блоки пояснення (рознесені)
    b1, _, _ = textbox(630, 80, "Інтерференційні\nмаксимуми |ψ₁ + ψ₂|²", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b1)

    b2, _, _ = textbox(240, 395, "Хвильова суперпозиція: кожен електрон проходить через ОБІ щілини", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b2)

    render(os.path.join(IMG, "fig1-double-slit.svg"), W, H, *frags)


def fig_davisson_germer():
    """fig2-davisson-germer.svg: Експеримент Девіссона — Джермера з дифракції електронів на кристал монокристалічного нікелю."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Дослід Девіссона — Джермера (1927): дифракція електронів на кристалі Ni", size=16, bold=True, color="#1e293b"))

    # Кристал монокристала Нікелю (кристалічна ґратка)
    frags.append(rect(300, 260, 320, 110, fill="#e2e8f0", stroke="#475569", sw=2.0, rx=4))
    frags.append(text(460, 355, "Монокристал Нікелю (Ni, d = 0.091 nm)", size=12, bold=True, color="#1e293b"))

    # Атоми кристала (вузли)
    for row in range(3):
        for col in range(9):
            ax = 320 + col * 35
            ay = 280 + row * 25
            frags.append(circle(ax, ay, 6, fill=BLUE_S, stroke="#1e3a8a"))

    # Електронна гармата з прискорювальною напругою V = 54 V
    frags.append(rect(60, 70, 160, 90, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=6))
    frags.append(text(140, 100, "Електронна гармата", size=12, bold=True, color=AMBER_S))
    frags.append(text(140, 125, "V = 54 V  ⇒  E = 54 eV", size=11, bold=True, color="#475569"))
    frags.append(text(140, 145, "λ_dB = 0.167 nm", size=11, color=AMBER_S))

    # Перпендикулярний падаючий пучок (під кутом 90° до поверхні)
    frags.append(line(140, 160, 460, 260, color=RED_S, sw=2.8))
    frags.append(path_svg("M 452 245 L 460 260 L 442 255 Z", fill=RED_S, stroke=RED_S))
    frags.append(text(280, 185, "Падаючий пучок e⁻", size=12, bold=True, color=RED_S))

    # Розсіяний пучок під кутом ф = 50°
    phi_rad = math.radians(50)
    dx = 210 * math.sin(phi_rad)
    dy = -210 * math.cos(phi_rad)
    end_x = 460 + dx
    end_y = 260 + dy

    frags.append(line(460, 260, end_x, end_y, color=GREEN_S, sw=2.8))
    frags.append(path_svg(f"M {end_x-10:.1f} {end_y+12:.1f} L {end_x:.1f} {end_y:.1f} L {end_x-15:.1f} {end_y-2:.1f} Z", fill=GREEN_S, stroke=GREEN_S))

    # Детектор (колектор Фарадея)
    frags.append(circle(end_x, end_y, 16, fill=GREEN_F, stroke=GREEN_S, sw=2.0))
    frags.append(text(end_x, end_y + 4, "Det", size=10, bold=True, color=GREEN_S))

    # Дуга кута ф = 50°
    frags.append(path_svg(f"M 460 170 A 90 90 0 0 1 {460 + 90*math.sin(phi_rad):.1f} {260 - 90*math.cos(phi_rad):.1f}",
                          fill="none", stroke=PURPLE_S, sw=1.8, dash="3,3"))
    frags.append(text(500, 175, "ϕ = 50°", size=13, bold=True, color=PURPLE_S))

    # Полярна діаграма інтенсивності з максимумом при 50°
    b_peak, _, _ = textbox(630, 110, "Дифракційний максимум:\n2 d sin(θ) = n λ\n(Максимум Бреґґа)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_peak)

    b_exp, _, _ = textbox(60, 310, "Підтвердження:\nλ_експ = 0.165 nm\nλ_деБройля = 0.167 nm\n(Збіг з точністю 1%)", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_exp)

    render(os.path.join(IMG, "fig2-davisson-germer.svg"), W, H, *frags)


def fig_wave_packet():
    """fig3-wave-packet.svg: Структура квантового хвильового пакета, обвідна, фазова та групова швидкості."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Структура хвильового пакета: обвідна, v_phase та v_group", size=16, bold=True, color="#1e293b"))

    # Вісі x та ψ(x)
    frags.append(line(60, 210, 820, 210, color="#94a3b8", sw=1.5)) # ось X
    frags.append(line(440, 50, 440, 370, color="#cbd5e1", sw=1.2, dash="4,4")) # середина

    frags.append(text(830, 214, "x", size=14, bold=True, color="#475569"))
    frags.append(text(440, 45, "Re [ψ(x, t)]", size=12, bold=True, color="#475569"))

    # Обвідна пакета: A(x) = exp(- (x - x0)² / (2 Δx²))
    envelope_top = []
    envelope_bot = []
    wave_pts = []

    for x_px in range(80, 800, 2):
        x_val = (x_px - 440) / 75.0 # нормована координата
        env = math.exp(- (x_val**2) / 1.8)
        val = env * math.cos(4.5 * x_val)

        y_top = 210 - env * 120
        y_bot = 210 + env * 120
        y_val = 210 - val * 120

        envelope_top.append((x_px, y_top))
        envelope_bot.append((x_px, y_bot))
        wave_pts.append((x_px, y_val))

    # Малювання обвідної (пунктир)
    d_env_top = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in envelope_top)
    d_env_bot = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in envelope_bot)
    frags.append(path_svg(d_env_top, fill="none", stroke=RED_S, sw=1.8, dash="4,3"))
    frags.append(path_svg(d_env_bot, fill="none", stroke=RED_S, sw=1.8, dash="4,3"))

    # Малювання заповнення хвилі
    d_wave = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in wave_pts)
    frags.append(path_svg(d_wave, fill="none", stroke=BLUE_S, sw=2.2))

    # Відрізок ширини пакета Δx
    frags.append(line(365, 80, 515, 80, color=PURPLE_S, sw=2.0))
    frags.append(line(365, 72, 365, 88, color=PURPLE_S, sw=2.0))
    frags.append(line(515, 72, 515, 88, color=PURPLE_S, sw=2.0))
    frags.append(text(440, 72, "Просторова ширина Δx", size=11, bold=True, color=PURPLE_S))

    # Стрілка групової швидкості v_g (рух обвідної)
    frags.append(line(440, 310, 580, 310, color=RED_S, sw=2.8))
    frags.append(path_svg("M 570 304 L 580 310 L 570 316 Z", fill=RED_S, stroke=RED_S))
    frags.append(text(510, 335, "Групова швидкість v_g = dω/dk = v_частинки", size=11, bold=True, color=RED_S))

    # Стрілка фазової швидкості v_p (рух горбів)
    frags.append(line(440, 270, 510, 270, color=BLUE_S, sw=2.0))
    frags.append(path_svg("M 502 265 L 510 270 L 502 275 Z", fill=BLUE_S, stroke=BLUE_S))
    frags.append(text(475, 260, "Фазова швидкість v_p = ω/k", size=10, bold=True, color=BLUE_S))

    # Співвідношення невизначеності
    b_unc, _, _ = textbox(70, 75, "Співвідношення Гейзенберга:\nΔx · Δp ≥ ℏ / 2\n(Властивість перетворення Фур'є)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_unc)

    b_rel, _, _ = textbox(70, 300, "Для вільних частинок:\nv_g = p / m = v\nv_p = p / (2m) = v / 2", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_rel)

    render(os.path.join(IMG, "fig3-wave-packet.svg"), W, H, *frags)


def fig_complementarity():
    """fig4-complementarity.svg: Принцип доповнюваності Бора та експеримент з квантовою стирачкою."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Принцип доповнюваності Бора та детектування шляху частинки", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Детектор увімкнено -> Знаємо шлях -> Картинка корпускулярна (без інтерференції)
    frags.append(rect(30, 60, 395, 330, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(227, 85, "А: Детектор шляху УВІМКНЕНО", size=13, bold=True, color=RED_S))

    # Схема зі щілинами
    frags.append(rect(80, 140, 10, 50, fill="#334155"))
    frags.append(rect(80, 210, 10, 30, fill="#334155"))
    frags.append(rect(80, 260, 10, 50, fill="#334155"))

    # Детектор шляху (наприклад, фотонне вимірювання біля щілини 1)
    frags.append(circle(95, 195, 12, fill=RED_F, stroke=RED_S, sw=1.8))
    frags.append(text(95, 199, "Eye", size=9, bold=True, color=RED_S))

    # Траєкторії частинок (прямі корпускулярні пучки)
    frags.append(line(95, 195, 260, 160, color=RED_S, sw=1.8, dash="3,3"))
    frags.append(line(95, 250, 260, 270, color=RED_S, sw=1.8, dash="3,3"))

    # Екран та сума двох плям (без інтерференції)
    frags.append(rect(260, 120, 10, 200, fill="#e2e8f0", stroke="#475569"))

    # Графік суми інтенсивностей
    c_left = []
    for y_idx in range(120, 320, 2):
        dy = y_idx - 220
        val = math.exp(- ((dy - 30)/35)**2) + math.exp(- ((dy + 30)/35)**2)
        px = 280 + val * 90
        c_left.append((px, y_idx))

    d_cleft = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in c_left)
    frags.append(path_svg(d_cleft, fill="none", stroke=RED_S, sw=2.2))

    b_no_int, _, _ = textbox(130, 335, "Інформація про шлях Є:\nКонтрастність V = 0\n(Корпускулярний режим)", size=10, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_no_int)

    # Права частина: Детектор вимкнено / стирачка -> Хвильовий режим
    frags.append(rect(455, 60, 395, 330, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(652, 85, "Б: Детектор ВИМКНЕНО / Стирачка", size=13, bold=True, color=TEAL_S))

    frags.append(rect(505, 140, 10, 50, fill="#334155"))
    frags.append(rect(505, 210, 10, 30, fill="#334155"))
    frags.append(rect(505, 260, 10, 50, fill="#334155"))

    # Хвильове поширення
    for r in range(15, 120, 20):
        frags.append(path_svg(f"M {515 + r*math.cos(0.5):.1f} {195 - r*math.sin(0.5):.1f} A {r} {r} 0 0 1 {515 + r*math.cos(0.5):.1f} {195 + r*math.sin(0.5):.1f}", fill="none", stroke=TEAL_S, sw=1.2, dash="3,3"))
        frags.append(path_svg(f"M {515 + r*math.cos(0.5):.1f} {250 - r*math.sin(0.5):.1f} A {r} {r} 0 0 1 {515 + r*math.cos(0.5):.1f} {250 + r*math.sin(0.5):.1f}", fill="none", stroke=TEAL_S, sw=1.2, dash="3,3"))

    frags.append(rect(685, 120, 10, 200, fill="#e2e8f0", stroke="#475569"))

    # Графік інтерференції
    c_right = []
    for y_idx in range(120, 320, 2):
        dy = y_idx - 220
        val = (math.cos(0.09 * dy))**2 * math.exp(- (dy/75)**2)
        px = 705 + val * 110
        c_right.append((px, y_idx))

    d_cright = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in c_right)
    frags.append(path_svg(d_cright, fill="none", stroke=TEAL_S, sw=2.2))

    b_int, _, _ = textbox(555, 335, "Інформації про шлях НЕМАЄ:\nКонтрастність V = 1\n(Хвильовий режим)", size=10, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_int)

    render(os.path.join(IMG, "fig4-complementarity.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_double_slit()
    fig_davisson_germer()
    fig_wave_packet()
    fig_complementarity()
    print("Всі 4 фігури згенеровано успішно.")
