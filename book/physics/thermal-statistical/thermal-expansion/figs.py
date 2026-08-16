# -*- coding: utf-8 -*-
"""Фігури для теми «Теплове розширення» (book/physics/thermal-statistical/thermal-expansion)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
RED_F, RED_S = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S = "#f8fafc", "#475569"

def polyline(pts, color="#333333", sw=1.5, fill="none"):
    pts_str = " ".join("%g,%g" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, color, sw)

def fig_anharmonic_potential():
    """anharmonic-potential.svg: Гармонічний та ангармонічний міжатомні потенціали та тепловий зсув рівноважної відстані."""
    W, H = 880, 420
    frags = []

    # Загальне тло
    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Мікроскопічний механізм: Ангармонізм потенціалу та зміщення ⟨r⟩_T", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Гармонічний потенціал (немає теплового розширення)
    frags.append(rect(30, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(230, 78, "Ідеально гармонічний потенціал U(r)", size=13, bold=True, color=BLUE_S))

    # Осі лівої панелі
    frags.append(line(70, 340, 390, 340, color="#64748b", sw=1.5)) # r-axis
    frags.append(line(70, 340, 70, 95, color="#64748b", sw=1.5))   # U-axis
    frags.append(text(385, 360, "Відстань r", size=11, bold=True, color="#475569"))
    frags.append(text(45, 105, "Потенціал U(r)", size=11, bold=True, color="#475569"))

    # Симетрична парабола U = k(r - r0)^2
    r0_left = 230
    parabola_pts = []
    for x_offset in range(-120, 121, 5):
        rx = r0_left + x_offset
        ry = 320 - 0.013 * (x_offset ** 2)
        if ry >= 110:
            parabola_pts.append((rx, ry))
    frags.append(polyline(parabola_pts, color=BLUE_S, sw=2.5))

    # Рівні енергії E1, E2, E3 та середина
    frags.append(line(r0_left - 60, 273, r0_left + 60, 273, color="#93c5fd", sw=1.5, dash="4,4"))
    frags.append(text(80, 270, "E₁ (низька T)", size=10, color=BLUE_S))

    frags.append(line(r0_left - 100, 190, r0_left + 100, 190, color="#3b82f6", sw=1.5, dash="4,4"))
    frags.append(text(80, 187, "E₂ (висока T)", size=10, color=BLUE_S))

    # Вертикальна середня лінія
    frags.append(line(r0_left, 110, r0_left, 340, color="#1e293b", sw=1.5, dash="2,2"))
    frags.append(circle(r0_left, 320, 4, fill=BLUE_S, stroke="#1e293b", sw=1))
    frags.append(text(r0_left, 358, "r₀ = ⟨r⟩_T", size=11, bold=True, color=BLUE_S))

    frags.append(text(230, 382, "Симетрія: ⟨r⟩ не залежить від T → α = 0", size=11, bold=True, color="#dc2626"))

    # Права панель: Ангармонічний потенціал (Леннард-Джонса / Морзе)
    frags.append(rect(450, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(650, 78, "Реальний ангармонічний потенціал", size=13, bold=True, color=RED_S))

    # Осі правої панелі
    frags.append(line(490, 340, 830, 340, color="#64748b", sw=1.5)) # r-axis
    frags.append(line(490, 340, 490, 95, color="#64748b", sw=1.5))   # U-axis
    frags.append(text(825, 360, "Відстань r", size=11, bold=True, color="#475569"))
    frags.append(text(465, 105, "U(r)", size=11, bold=True, color="#475569"))

    # Асиметрична крива (Морзе / Леннард-Джонс)
    lj_pts = []
    for dr in range(-90, 200, 4):
        rx = 610 + dr
        if dr < 0:
            ry = 320 - 0.022 * (dr ** 2) - 0.00015 * (dr ** 3)
        else:
            ry = 320 - 0.009 * (dr ** 2) + 0.000025 * (dr ** 3)
        if 110 <= ry <= 340 and 500 <= rx <= 830:
            lj_pts.append((rx, ry))

    frags.append(polyline(lj_pts, color=RED_S, sw=2.5))

    # Мінімум потенціалу r0
    r0_right = 610
    frags.append(circle(r0_right, 320, 4, fill=RED_S, stroke="#1e293b", sw=1))
    frags.append(line(r0_right, 320, r0_right, 340, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(text(r0_right, 358, "r₀ (0 K)", size=10, bold=True, color="#475569"))

    # Рівень T1 (низька температура)
    y_t1 = 260
    x_t1_left, x_t1_right = 558, 692
    x_t1_avg = (x_t1_left + x_t1_right) / 2
    frags.append(line(x_t1_left, y_t1, x_t1_right, y_t1, color=GREEN_S, sw=1.5, dash="4,4"))
    frags.append(circle(x_t1_avg, y_t1, 4, fill=GREEN_S, stroke="#1e293b", sw=1))
    frags.append(line(x_t1_avg, y_t1, x_t1_avg, 340, color=GREEN_S, sw=1, dash="2,2"))
    frags.append(text(x_t1_avg - 15, 372, "⟨r⟩_T₁", size=10, bold=True, color=GREEN_S))

    # Рівень T2 (висока температура)
    y_t2 = 180
    x_t2_left, x_t2_right = 534, 760
    x_t2_avg = (x_t2_left + x_t2_right) / 2
    frags.append(line(x_t2_left, y_t2, x_t2_right, y_t2, color=AMBER_S, sw=1.5, dash="4,4"))
    frags.append(circle(x_t2_avg, y_t2, 4, fill=AMBER_S, stroke="#1e293b", sw=1))
    frags.append(line(x_t2_avg, y_t2, x_t2_avg, 340, color=AMBER_S, sw=1, dash="2,2"))
    frags.append(text(x_t2_avg + 5, 372, "⟨r⟩_T₂", size=10, bold=True, color=AMBER_S))

    # Стрілка зсуву ⟨r⟩
    frags.append(line(r0_right, 140, x_t2_avg, 140, color=RED_S, sw=2))
    frags.append(text((r0_right + x_t2_avg)/2, 130, "Δr > 0 при нагріванні", size=10, bold=True, color=RED_S))

    frags.append(text(650, 388, "Асиметрія: пологіший хвіст притягання зміщує середня координату ⟨r⟩_T > r₀", size=10, bold=True, color=RED_S))

    render(os.path.join(IMG, "anharmonic-potential.svg"), W, H, *frags)


def fig_linear_volumetric_expansion():
    """linear-volumetric-expansion.svg: Геометричне порівняння лінійного, поверхневого та об'ємного розширення."""
    W, H = 880, 360
    frags = []

    frags.append(rect(10, 10, 860, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Геометрія розширення: 1D (лінійне), 2D (поверхневе) та 3D (об'ємне)", size=16, bold=True, color="#1e293b"))

    # Панель 1: 1D Лінійне розширення (Стрижень)
    frags.append(rect(30, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(160, 78, "1D: Стрижень (α)", size=13, bold=True, color=BLUE_S))

    # Початковий стрижень L0
    frags.append(rect(50, 130, 160, 28, fill="#bfdbfe", stroke=BLUE_S, sw=1.5, rx=3))
    frags.append(text(130, 148, "L₀", size=11, bold=True, color=BLUE_S))

    # Розширений стрижень L0 + ΔL
    frags.append(rect(50, 190, 160, 28, fill="#bfdbfe", stroke=BLUE_S, sw=1.5, rx=3))
    frags.append(rect(210, 190, 45, 28, fill="#fca5a5", stroke=RED_S, sw=1.5, rx=3))
    frags.append(text(130, 208, "L₀", size=11, bold=True, color=BLUE_S))
    frags.append(text(232, 208, "ΔL", size=11, bold=True, color=RED_S))

    # Стрілка та формула
    frags.append(text(160, 260, "ΔL = α · L₀ · ΔT", size=12, bold=True, color="#1e293b"))
    frags.append(text(160, 290, "L(T) = L₀(1 + α ΔT)", size=11, italic=True, color="#475569"))

    # Панель 2: 2D Поверхневе розширення (Пластина)
    frags.append(rect(310, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 78, "2D: Пластина (β ≈ 2α)", size=13, bold=True, color=GREEN_S))

    # Початковий квадрат A0
    frags.append(rect(345, 120, 130, 100, fill="#dcfce7", stroke=GREEN_S, sw=1.5, rx=3))
    frags.append(text(410, 175, "A₀", size=13, bold=True, color=GREEN_S))

    # Прирости ΔA з двох боків
    frags.append(rect(475, 120, 25, 100, fill="#fca5a5", stroke=RED_S, sw=1.5, rx=2))
    frags.append(rect(345, 220, 130, 20, fill="#fca5a5", stroke=RED_S, sw=1.5, rx=2))
    frags.append(rect(475, 220, 25, 20, fill="#f87171", stroke=RED_S, sw=1.5, rx=2))

    frags.append(text(487, 175, "ΔA₁", size=9, bold=True, color=RED_S))
    frags.append(text(410, 233, "ΔA₂", size=9, bold=True, color=RED_S))

    frags.append(text(440, 260, "ΔA ≈ 2α · A₀ · ΔT", size=12, bold=True, color="#1e293b"))
    frags.append(text(440, 290, "β = 2α (для ізотропних)", size=11, italic=True, color="#475569"))

    # Панель 3: 3D Об'ємне розширення (Куб)
    frags.append(rect(590, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(720, 78, "3D: Об'єм (γ ≈ 3α)", size=13, bold=True, color=PURPLE_S))

    # Ізометричний куб V0
    frags.append(rect(630, 140, 90, 90, fill="#f3e8ff", stroke=PURPLE_S, sw=1.5))
    frags.append(polyline([(630, 140), (660, 115), (750, 115), (750, 205), (720, 230)], color=PURPLE_S, sw=1.5))
    frags.append(polyline([(720, 140), (750, 115)], color=PURPLE_S, sw=1.5))
    frags.append(polyline([(660, 115), (660, 205), (630, 230)], color=PURPLE_S, sw=1, fill="none"))
    frags.append(polyline([(660, 205), (750, 205)], color=PURPLE_S, sw=1, fill="none"))
    frags.append(text(675, 190, "V₀", size=14, bold=True, color=PURPLE_S))

    # Шари розширення ΔV
    frags.append(polyline([(720, 140), (735, 140), (765, 115), (750, 115)], color=RED_S, sw=1.5, fill="#fca5a5"))
    frags.append(polyline([(720, 230), (735, 230), (765, 205), (750, 205)], color=RED_S, sw=1.5, fill="#fca5a5"))
    frags.append(polyline([(735, 140), (735, 230), (765, 205), (765, 115)], color=RED_S, sw=1.5, fill="#fca5a5"))

    frags.append(text(720, 260, "ΔV ≈ 3α · V₀ · ΔT", size=12, bold=True, color="#1e293b"))
    frags.append(text(720, 290, "γ = 3α (для ізотропних)", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "linear-volumetric-expansion.svg"), W, H, *frags)


def fig_water_anomaly():
    """water-anomaly.svg: Графіки аномалії густини та питомого об'єму води біля 4 °C."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Термодинамічна аномалія води: максимум густини при T = 3.98 °C", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Густина ρ(T)
    frags.append(rect(30, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(230, 78, "Залежність густини води ρ(T) біля 0…12 °C", size=13, bold=True, color=BLUE_S))

    frags.append(line(70, 320, 390, 320, color="#64748b", sw=1.5))
    frags.append(line(70, 320, 70, 95, color="#64748b", sw=1.5))
    frags.append(text(385, 340, "T (°C)", size=11, bold=True, color="#475569"))
    frags.append(text(45, 105, "ρ (кг/м³)", size=11, bold=True, color="#475569"))

    frags.append(line(90, 320, 90, 325, color="#64748b", sw=1.5))
    frags.append(text(90, 340, "0°C", size=10, color="#475569"))

    frags.append(line(180, 320, 180, 325, color=RED_S, sw=2))
    frags.append(text(180, 340, "3.98°C", size=10, bold=True, color=RED_S))

    frags.append(line(315, 320, 315, 325, color="#64748b", sw=1.5))
    frags.append(text(315, 340, "10°C", size=10, color="#475569"))

    rho_pts = []
    for t_val in range(0, 12):
        tx = 90 + t_val * 22.5
        ry = 125 + 3.4 * ((t_val - 3.98) ** 2)
        rho_pts.append((tx, ry))

    frags.append(polyline(rho_pts, color=BLUE_S, sw=2.5))
    frags.append(circle(180, 125, 5, fill=RED_S, stroke="#1e293b", sw=1.5))
    frags.append(line(180, 125, 180, 320, color=RED_S, sw=1, dash="2,2"))
    frags.append(text(180, 112, "Максимум ρ = 999.97 кг/м³", size=10, bold=True, color=RED_S))

    frags.append(text(125, 240, "Аномальне розширення\n(γ < 0)", size=9, bold=True, color=RED_S))
    frags.append(text(270, 240, "Звичайне розширення\n(γ > 0)", size=9, bold=True, color=GREEN_S))

    # Права панель: Структурне пояснення
    frags.append(rect(450, 55, 400, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(650, 78, "Мікроструктурне пояснення аномалії", size=13, bold=True, color=PURPLE_S))

    frags.append(rect(470, 100, 170, 130, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(555, 118, "T < 3.98 °C", size=11, bold=True, color=BLUE_S))

    h2o_0c = [(520, 142), (590, 142), (555, 175), (510, 202), (600, 202)]
    for x, y in h2o_0c:
        frags.append(circle(x, y, 7, fill="#3b82f6", stroke="#1e293b", sw=1))
    frags.append(line(520, 142, 590, 142, color="#93c5fd", sw=1.5, dash="2,2"))
    frags.append(line(520, 142, 555, 175, color="#93c5fd", sw=1.5, dash="2,2"))
    frags.append(line(590, 142, 555, 175, color="#93c5fd", sw=1.5, dash="2,2"))
    frags.append(line(555, 175, 510, 202, color="#93c5fd", sw=1.5, dash="2,2"))
    frags.append(line(555, 175, 600, 202, color="#93c5fd", sw=1.5, dash="2,2"))

    frags.append(text(555, 218, "Пухкі кластери з порожнинами", size=9, italic=True, color="#475569"))

    frags.append(rect(660, 100, 170, 130, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(745, 118, "T > 3.98 °C", size=11, bold=True, color=AMBER_S))

    h2o_high = [(690, 138), (725, 148), (770, 133), (710, 172), (750, 180), (785, 162)]
    for x, y in h2o_high:
        frags.append(circle(x, y, 7, fill="#e08a1e", stroke="#1e293b", sw=1))

    frags.append(text(745, 218, "Зруйновані зв'язки + хаос", size=9, italic=True, color="#475569"))

    b_text, _, _ = textbox(650, 280, "При 0…4 °C руйнування пухких водневих каркасів\nстискає рідину сильніше за тепловий розхід.\nПісля 3.98 °C переважає класичний тепловий хаос.", size=10, bold=False, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_text)

    render(os.path.join(IMG, "water-anomaly.svg"), W, H, *frags)


def fig_bimetallic_strip():
    """bimetallic-strip.svg: Принцип дії біметалевої пластини при нагріванні та охолодженні."""
    W, H = 880, 360
    frags = []

    frags.append(rect(10, 10, 860, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Принцип роботи біметалевого елемента: термочутливий вигин", size=16, bold=True, color="#1e293b"))

    # Панель 1: Початковий стан T0
    frags.append(rect(30, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(160, 78, "Прямий стан при T₀", size=13, bold=True, color="#475569"))

    frags.append(rect(40, 130, 20, 100, fill="#cbd5e1", stroke="#475569", sw=1.5))
    frags.append(text(50, 180, "Кріплення", size=9, bold=True, color="#475569", anchor="middle"))

    frags.append(rect(60, 150, 200, 30, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    frags.append(text(160, 170, "Метал А (Латунь, α₁ = 19×10⁻⁶ K⁻¹)", size=10, bold=True, color="#854d0e"))

    frags.append(rect(60, 180, 200, 30, fill="#e2e8f0", stroke="#475569", sw=1.5))
    frags.append(text(160, 200, "Метал Б (Інвар, α₂ = 1.2×10⁻⁶ K⁻¹)", size=10, bold=True, color="#334155"))

    frags.append(text(160, 260, "Рівні довжини L₁(T₀) = L₂(T₀)", size=11, bold=True, color="#1e293b"))
    frags.append(text(160, 290, "Вигин відсутній (R = ∞)", size=11, italic=True, color="#475569"))

    # Панель 2: Нагрівання T > T0
    frags.append(rect(310, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 78, "Нагрівання: T > T₀", size=13, bold=True, color=RED_S))

    frags.append(rect(320, 130, 20, 100, fill="#cbd5e1", stroke="#475569", sw=1.5))

    pts_a = [(340, 150), (390, 155), (440, 170), (490, 195), (530, 230),
             (520, 245), (480, 215), (435, 190), (385, 175), (340, 170)]
    frags.append(polyline(pts_a, color="#ca8a04", sw=1.5, fill="#fef08a"))

    pts_b = [(340, 170), (385, 175), (435, 190), (480, 215), (520, 245),
             (510, 260), (470, 230), (425, 205), (380, 190), (340, 185)]
    frags.append(polyline(pts_b, color="#475569", sw=1.5, fill="#e2e8f0"))

    frags.append(text(440, 275, "ΔL₁ > ΔL₂ → вигин у бік Б", size=11, bold=True, color=RED_S))
    frags.append(text(440, 295, "Кривина 1/R ∝ (α₁ - α₂) ΔT", size=10, italic=True, color="#475569"))

    # Панель 3: Застосування
    frags.append(rect(590, 55, 260, 280, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(720, 78, "Застосування: Ключ термореле", size=13, bold=True, color=GREEN_S))

    frags.append(rect(600, 130, 20, 100, fill="#cbd5e1", stroke="#475569", sw=1.5))
    frags.append(polyline(pts_a, color="#ca8a04", sw=1.5, fill="#fef08a"))
    frags.append(polyline(pts_b, color="#475569", sw=1.5, fill="#e2e8f0"))

    frags.append(circle(530, 265, 6, fill="#e08a1e", stroke="#1e293b", sw=1.5))
    frags.append(line(530, 271, 530, 310, color="#1e293b", sw=2))
    frags.append(text(550, 290, "Розмикання", size=11, bold=True, color=RED_S))

    frags.append(line(515, 248, 525, 260, color=RED_S, sw=2, dash="2,2"))

    b_app, _, _ = textbox(720, 150, "Автоматичне відключення\nнагрівача при перевищенні\nзаданої температури T_set", size=10, bold=False, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_app)

    render(os.path.join(IMG, "bimetallic-strip.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_anharmonic_potential()
    fig_linear_volumetric_expansion()
    fig_water_anomaly()
    fig_bimetallic_strip()
    print("Figures generated successfully!")
