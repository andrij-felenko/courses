# -*- coding: utf-8 -*-
"""Фігури для теми «Квантове тунелювання» (book/physics/quantum-mechanics/quantum-tunnelling)."""
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


def fig_barrier_penetration():
    """fig1-barrier-penetration.svg: Схема проникнення хвильової функції крізь потенціальний бар'єр."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Квантове тунелювання крізь прямокутний потенціальний бар'єр", size=16, bold=True, color="#1e293b"))

    # Базові осі X та V(x)
    frags.append(arrow(60, 340, 820, 340, color="#475569", sw=1.8))
    frags.append(text(830, 345, "x", size=14, bold=True, color="#475569"))

    frags.append(arrow(100, 360, 100, 60, color="#475569", sw=1.8))
    frags.append(text(85, 70, "E, V(x)", size=14, bold=True, color="#475569"))

    # Прямокутний потенціальний бар'єр V_0
    frags.append(rect(300, 120, 240, 220, fill="#f1f5f9", stroke="#64748b", sw=2.0, rx=2))
    frags.append(line(300, 120, 300, 340, color="#334155", sw=2.0))
    frags.append(line(540, 120, 540, 340, color="#334155", sw=2.0))

    # Рівень потенціалу V_0 та енергії E
    frags.append(line(80, 120, 300, 120, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(text(75, 125, "V₀", size=14, bold=True, color="#dc2626", anchor="end"))

    frags.append(line(80, 210, 800, 210, color=BLUE_S, sw=1.5, dash="6,4"))
    frags.append(text(75, 215, "E (E < V₀)", size=13, bold=True, color=BLUE_S, anchor="end"))

    # Межі областей x = 0 та x = a
    frags.append(text(300, 360, "x = 0", size=13, color="#334155"))
    frags.append(text(540, 360, "x = a", size=13, color="#334155"))

    # Позначення областей
    frags.append(text(200, 90, "Область I (x < 0)\nV(x) = 0", size=12, color="#475569"))
    frags.append(text(420, 90, "Область II (0 ≤ x ≤ a)\nV(x) = V₀", size=12, color="#dc2626"))
    frags.append(text(660, 90, "Область III (x > a)\nV(x) = 0", size=12, color="#475569"))

    # Хвильова функція
    pts_I = []
    for x_px in range(100, 301, 2):
        x_rel = x_px - 100
        y_val = 210 - 45 * math.cos(0.08 * x_rel)
        pts_I.append(f"{x_px:.1f},{y_val:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_I), fill="none", stroke=BLUE_S, sw=2.5))

    pts_II = []
    for x_px in range(300, 541, 2):
        dx = (x_px - 300) / 240.0
        amp = 45.0 * math.exp(-2.5 * dx)
        y_val = 210 - amp * math.cos(0.08 * 200 + 0.5 * dx)
        pts_II.append(f"{x_px:.1f},{y_val:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_II), fill="none", stroke=PURPLE_S, sw=2.5))

    pts_III = []
    y_end_amp = 45.0 * math.exp(-2.5)
    for x_px in range(540, 801, 2):
        x_rel = x_px - 540
        y_val = 210 - y_end_amp * math.cos(0.08 * 200 + 0.5 + 0.08 * x_rel)
        pts_III.append(f"{x_px:.1f},{y_val:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_III), fill="none", stroke=TEAL_S, sw=2.5))

    # Підписи амплітуд та формул
    b1, _, _ = textbox(190, 270, "Падаюча та відбита хвиля\nψ_I = A e^{ikx} + B e^{-ikx}", size=11, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b1)

    b2, _, _ = textbox(420, 270, "Експоненціальне згасання\nψ_II = C e^{-κx} + D e^{+κx}", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b2)

    b3, _, _ = textbox(670, 270, "Пройдена хвиля (тунельована)\nψ_III = F e^{ikx} (амплітуда |F| < |A|)", size=11, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b3)

    # Ширина бар'єра a
    frags.append(arrow(300, 385, 540, 385, color="#334155", sw=1.5))
    frags.append(arrow(540, 385, 300, 385, color="#334155", sw=1.5))
    frags.append(text(420, 380, "ширина бар'єра a", size=12, bold=True, color="#334155"))

    render(os.path.join(IMG, "fig1-barrier-penetration.svg"), W, H, *frags)


def fig_transmission_vs_width():
    """fig2-transmission-vs-width.svg: Залежність коефіцієнта прозорості від ширини бар'єра та маси частинки."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Залежність коефіцієнта прозорості T від ширини бар'єра a (логарифмічний масштаб)", size=16, bold=True, color="#1e293b"))

    x_min, x_max = 120, 780
    y_min, y_max = 85, 340
    y_plot_top, y_plot_bot = 95, 330

    frags.append(rect(x_min, y_min, x_max - x_min, y_max - y_min, fill="#ffffff", stroke="#cbd5e1", sw=1.5))

    logs = [0, -3, -6, -9, -12]
    for l in logs:
        y_p = y_plot_top + (0 - l) / 12.0 * (y_plot_bot - y_plot_top)
        frags.append(line(x_min, y_p, x_max, y_p, color="#f1f5f9", sw=1.2))
        lbl = "1" if l == 0 else f"10^{l}"
        frags.append(text(x_min - 10, y_p + 4, lbl, size=11, color="#475569", anchor="end"))

    a_vals = [0.2, 0.5, 1.0, 1.5, 2.0]
    for a in a_vals:
        x_p = x_min + (a / 2.0) * (x_max - x_min)
        frags.append(line(x_p, y_min, x_p, y_max, color="#f1f5f9", sw=1.2))
        frags.append(text(x_p, y_max + 20, f"{a:.1f}", size=11, color="#475569"))

    frags.append(text(450, y_max + 42, "Ширина бар'єра a (нм)", size=13, bold=True, color="#1e293b"))
    frags.append(text(45, 210, "Коефіцієнт прозорості T", size=13, bold=True, color="#1e293b", anchor="middle"))

    pts_e = []
    for step in range(101):
        a = step * 2.0 / 100.0
        log_T = -6.29 * a
        if log_T < -12:
            log_T = -12
        x_p = x_min + (a / 2.0) * (x_max - x_min)
        y_p = y_plot_top + (0 - log_T) / 12.0 * (y_plot_bot - y_plot_top)
        pts_e.append(f"{x_p:.1f},{y_p:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_e), fill="none", stroke=BLUE_S, sw=3.0))

    pts_p = []
    for step in range(101):
        a = step * 2.0 / 100.0
        log_T = -6.29 * math.sqrt(10.0) * a
        if log_T < -12:
            log_T = -12
        x_p = x_min + (a / 2.0) * (x_max - x_min)
        y_p = y_plot_top + (0 - log_T) / 12.0 * (y_plot_bot - y_plot_top)
        pts_p.append(f"{x_p:.1f},{y_p:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_p), fill="none", stroke=PURPLE_S, sw=2.5, dash="6,3"))

    pts_alpha = []
    for step in range(101):
        a = step * 2.0 / 100.0
        log_T = -6.29 * math.sqrt(100.0) * a
        if log_T < -12:
            log_T = -12
        x_p = x_min + (a / 2.0) * (x_max - x_min)
        y_p = y_plot_top + (0 - log_T) / 12.0 * (y_plot_bot - y_plot_top)
        pts_alpha.append(f"{x_p:.1f},{y_p:.1f}")
    frags.append(path_svg("M " + " L ".join(pts_alpha), fill="none", stroke=RED_S, sw=2.5, dash="2,2"))

    # Прямі підписи кривих
    frags.append(text(300, 145, "Електрон (m = m_e)", size=12, bold=True, color=BLUE_S))
    frags.append(text(210, 180, "Важка частинка (m = 10 m_e)", size=11, bold=True, color=PURPLE_S))
    frags.append(text(150, 240, "Іон / Альфа (m = 100 m_e)", size=11, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig2-transmission-vs-width.svg"), W, H, *frags)


def fig_stm_principle():
    """fig3-stm-principle.svg: Принцип роботи скануючого тунельного мікроскопа (СТМ)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Принцип дії скануючого тунельного мікроскопа (СТМ)", size=16, bold=True, color="#1e293b"))

    frags.append(rect(120, 70, 160, 60, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8, rx=6))
    frags.append(mtext(200, 95, "П'єзоелектричний\nсканер (XYZ)", size=12, bold=True, color=PURPLE_S))

    frags.append(path_svg("M 180 130 L 220 130 L 205 240 L 195 240 Z", fill="#94a3b8", stroke="#334155", sw=1.8))
    frags.append(circle(200, 245, 6, fill=AMBER_S, stroke="#b45309", sw=1.5))
    frags.append(text(120, 220, "Атомарне вістря\n(Pt-Ir / W)", size=11, color="#475569"))

    frags.append(rect(60, 290, 760, 80, fill="#e2e8f0", stroke="#475569", sw=2.0, rx=4))
    frags.append(text(440, 355, "Провідна поверхня зразка (кристалічна ґратка)", size=13, bold=True, color="#1e293b"))

    for i, x_a in enumerate(range(100, 780, 50)):
        y_a = 290
        r_a = 18
        frags.append(circle(x_a, y_a, r_a, fill=BLUE_F, stroke=BLUE_S, sw=1.5))
        frags.append(circle(x_a, y_a, 4, fill=BLUE_S, stroke=BLUE_S))

    frags.append(line(230, 245, 230, 272, color=RED_S, sw=1.5, dash="3,3"))
    frags.append(arrow(230, 245, 230, 272, color=RED_S, sw=1.2))
    frags.append(arrow(230, 272, 230, 245, color=RED_S, sw=1.2))
    frags.append(text(285, 262, "Зазор d ≈ 0.5–1.0 нм", size=12, bold=True, color=RED_S))

    frags.append(path_svg("M 200 251 C 195 260 205 265 200 272", fill="none", stroke=RED_S, sw=2.5))
    frags.append(arrow(200, 268, 200, 274, color=RED_S, sw=2.0))
    frags.append(text(140, 270, "I_тунельне ∝ e^{-2κd}", size=12, bold=True, color=RED_S))

    frags.append(rect(480, 80, 220, 110, fill=GREEN_F, stroke=GREEN_S, sw=1.8, rx=6))
    frags.append(mtext(590, 105, "Система зворотного зв'язку\nта вимірювання струму", size=12, bold=True, color=GREEN_S))
    frags.append(text(590, 145, "Підтримка I_tunnel = const\n⇒ Вимірювання z(x,y)", size=11, color="#166534"))

    frags.append(arrow(220, 100, 480, 100, color=PURPLE_S, sw=1.5))
    frags.append(text(350, 90, "Керування Z(t)", size=11, color=PURPLE_S))

    frags.append(arrow(205, 240, 480, 150, color=RED_S, sw=1.5))
    frags.append(text(340, 180, "Сигнал струму I(t)", size=11, color=RED_S))

    render(os.path.join(IMG, "fig3-stm-principle.svg"), W, H, *frags)


def fig_transistor_gate_leakage():
    """fig4-transistor-gate-leakage.svg: Порівняння витіку струму крізь SiO2 та High-k діелектрик."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Тунельний витік у транзисторах: класичний SiO₂ проти High-k діелектрика", size=16, bold=True, color="#1e293b"))

    # Ліва частина: тонкий диоксид кремнію SiO2
    frags.append(rect(40, 60, 380, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(230, 85, "Традиційний SiO₂ (k ≈ 3.9)", size=14, bold=True, color=RED_S))

    frags.append(rect(80, 105, 300, 35, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=4))
    frags.append(text(230, 127, "Металевий затвор (Gate)", size=12, bold=True, color=AMBER_S))

    frags.append(rect(80, 150, 300, 25, fill=RED_F, stroke=RED_S, sw=1.8, rx=2))
    frags.append(text(230, 167, "SiO₂ (d_phys = 1.2 нм) — ДУЖЕ ТОНКИЙ!", size=11, bold=True, color=RED_S))

    frags.append(rect(80, 185, 300, 50, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=4))
    frags.append(text(230, 215, "Кремнієвий канал (Silicon Channel)", size=12, bold=True, color=BLUE_S))

    # Стрілки витіку з боків від тексту, щоб не перетинати рамку та текст
    for x_e in [95, 120, 340, 365]:
        frags.append(arrow(x_e, 142, x_e, 183, color=RED_S, sw=2.0))
    frags.append(text(230, 270, "Високий тунельний витік I_leak!\n(Експоненціальні втрати енергії)", size=12, bold=True, color=RED_S))

    # Права частина: High-k діелектрик HfO2
    frags.append(rect(460, 60, 380, 300, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(650, 85, "High-k діелектрик HfO₂ (k ≈ 25)", size=14, bold=True, color=GREEN_S))

    frags.append(rect(500, 105, 300, 35, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=4))
    frags.append(text(650, 127, "Металевий затвор (Gate)", size=12, bold=True, color=AMBER_S))

    frags.append(rect(500, 150, 300, 55, fill=GREEN_F, stroke=GREEN_S, sw=1.8, rx=2))
    frags.append(mtext(650, 172, "HfO₂ (d_phys = 3.0 нм, EOT = 1.2 нм)\nФІЗИЧНО ТОВСТИЙ БАР'ЄР", size=11, bold=True, color=GREEN_S))

    frags.append(rect(500, 215, 300, 50, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=4))
    frags.append(text(650, 245, "Кремнієвий канал (Silicon Channel)", size=12, bold=True, color=BLUE_S))

    for x_e in [515, 540, 760, 785]:
        frags.append(line(x_e, 142, x_e, 165, color=GREEN_S, sw=1.5))
        frags.append(line(x_e, 165, x_e, 175, color=GREEN_S, sw=1.5, dash="2,2"))
        frags.append(circle(x_e, 175, 3, fill=GREEN_S, stroke=GREEN_S))
    frags.append(text(650, 300, "Тунелювання пригнічено в >100 разів!\n(Збереження ємності затвора)", size=12, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig4-transistor-gate-leakage.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_barrier_penetration()
    fig_transmission_vs_width()
    fig_stm_principle()
    fig_transistor_gate_leakage()
    print("Фігури успішно згенеровано у", IMG)
