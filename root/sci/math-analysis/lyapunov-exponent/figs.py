# -*- coding: utf-8 -*-
"""Фігури для теми «Показники Ляпунова» (book/physics/mechanics/lyapunov-exponent)."""
import sys, os
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

def ellipse(cx, cy, rx, ry, fill="#ffffff", stroke="#000000", sw=1.5):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" />'

def fig_ellipsoid_evolution():
    """fig1-ellipsoid-evolution.svg: Деформація початкової сфери фазового об'єму в еліпсоїд вздовж головних осей."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Деформація фазового елемента та показники Ляпунова", size=16, bold=True, color="#1e293b"))

    # Початковий стан t = 0 (Сфера)
    frags.append(rect(30, 60, 380, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(220, 85, "Початковий момент часу t = 0", size=14, bold=True, color=BLUE_S))
    
    # Мала сфера в центрі
    frags.append(circle(220, 200, 50, fill="#ffffff", stroke=BLUE_S, sw=2))
    
    # Осі сфери r0
    frags.append(arrow(220, 200, 270, 200, color=RED_S, sw=2))
    frags.append(arrow(220, 200, 220, 150, color=GREEN_S, sw=2))
    frags.append(arrow(220, 200, 185, 235, color=PURPLE_S, sw=2))
    
    frags.append(text(285, 195, "δx₁(0)", size=11, bold=True, color=RED_S, anchor="start"))
    frags.append(text(220, 140, "δx₂(0)", size=11, bold=True, color=GREEN_S, anchor="middle"))
    frags.append(text(170, 245, "δx₃(0)", size=11, bold=True, color=PURPLE_S, anchor="end"))

    txt_spher = ["Початковий об'єм: V(0) = (4/3)π r₀³", "Ізотропний інфінітезимальний шар", "Радіус-вектор: ||δx(0)|| = ε"]
    frags.append(mtext(220, 300, txt_spher, size=11, color=BLUE_S, anchor="middle", lh=1.4))

    # Перехідне розтягнення (Стрілка)
    frags.append(arrow(420, 200, 470, 200, color=AMBER_S, sw=3))
    frags.append(text(445, 175, "Еволюція t > 0", size=11, bold=True, color=AMBER_S, anchor="middle"))
    frags.append(text(445, 190, "e^{J t}", size=10, italic=True, color=AMBER_S, anchor="middle"))

    # Кінцевий стан t > 0 (Еліпсоїд)
    frags.append(rect(480, 60, 370, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(665, 85, "Деформований еліпсоїд t > 0", size=14, bold=True, color=RED_S))

    # Еліпс розтягнутий
    frags.append(ellipse(665, 200, 120, 35, fill="#ffffff", stroke=RED_S, sw=2))

    # Осі еліпсоїда
    frags.append(arrow(665, 200, 785, 200, color=RED_S, sw=2))
    frags.append(arrow(665, 200, 665, 165, color=GREEN_S, sw=2))
    frags.append(arrow(665, 200, 640, 220, color=PURPLE_S, sw=2))

    frags.append(text(800, 195, "e^{λ₁t} δx₁(0)", size=10, bold=True, color=RED_S, anchor="start"))
    frags.append(text(665, 155, "e^{λ₂t} δx₂(0)", size=10, bold=True, color=GREEN_S, anchor="middle"))
    frags.append(text(630, 235, "e^{λ₃t} δx₃(0)", size=10, bold=True, color=PURPLE_S, anchor="end"))

    txt_ellip = ["Головні осі: δxᵢ(t) ~ exp(λᵢ t) δxᵢ(0)", "Об'єм: V(t) = V(0) exp((λ₁ + λ₂ + λ₃) t)", "λ₁ > 0: розтягнення (хаос)", "λ₂ = 0: вздовж траєкторії", "λ₃ < 0: стискання фазового об'єму"]
    frags.append(mtext(665, 290, txt_ellip, size=10, color=RED_S, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "fig1-ellipsoid-evolution.svg"), W, H, *frags)


def fig_attractor_signatures():
    """fig2-attractor-signatures.svg: Класифікація типів атракторів за сигнатурою спектра Ляпунова."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Сигнатура спектра показників Ляпунова та класифікація атракторів", size=16, bold=True, color="#1e293b"))

    # Блок 1: Стійка точка спокою
    frags.append(rect(30, 60, 195, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(127, 85, "Точка спокою", size=13, bold=True, color=GREEN_S))
    frags.append(circle(127, 150, 8, fill=GREEN_S, stroke=GREEN_S))
    
    frags.append(arrow(70, 150, 105, 150, color=GREEN_S, sw=1.5))
    frags.append(arrow(184, 150, 149, 150, color=GREEN_S, sw=1.5))
    frags.append(arrow(127, 105, 127, 138, color=GREEN_S, sw=1.5))
    frags.append(arrow(127, 195, 127, 162, color=GREEN_S, sw=1.5))

    txt_p1 = ["Сигнатура: (-, -, -)", "", "• Усі λᵢ < 0", "• Фазовий об'єм стрімко", "  стискається в точку", "• Повна стійкість"]
    frags.append(mtext(127, 230, txt_p1, size=11, color=GREEN_S, anchor="middle", lh=1.35))

    # Блок 2: Граничний цикл
    frags.append(rect(240, 60, 195, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(337, 85, "Граничний цикл", size=13, bold=True, color=BLUE_S))
    frags.append(ellipse(337, 150, 50, 30, fill="none", stroke=BLUE_S, sw=2))
    frags.append(arrow(380, 160, 385, 150, color=BLUE_S, sw=2))

    txt_p2 = ["Сигнатура: (0, -, -)", "", "• λ₁ = 0 (вздовж орбіти)", "• λ₂, λ₃ < 0 (притягання)", "• Періодичний рух"]
    frags.append(mtext(337, 230, txt_p2, size=11, color=BLUE_S, anchor="middle", lh=1.35))

    # Блок 3: Двовимірний тор (2-Torus)
    frags.append(rect(450, 60, 195, 330, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(547, 85, "Квазіперіод. Тор", size=13, bold=True, color=PURPLE_S))
    frags.append(ellipse(547, 150, 60, 35, fill="none", stroke=PURPLE_S, sw=2))
    frags.append(ellipse(547, 150, 30, 15, fill="none", stroke=PURPLE_S, sw=1.5))

    txt_p3 = ["Сигнатура: (0, 0, -)", "", "• λ₁ = λ₂ = 0 (2 частоти)", "• λ₃ < 0", "• Квазіперіодичний рух"]
    frags.append(mtext(547, 230, txt_p3, size=11, color=PURPLE_S, anchor="middle", lh=1.35))

    # Блок 4: Хаотичний атрактор
    frags.append(rect(660, 60, 190, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(755, 85, "Дивний атрактор", size=13, bold=True, color=RED_S))
    
    frags.append(ellipse(730, 145, 25, 20, fill="none", stroke=RED_S, sw=1.5))
    frags.append(ellipse(775, 145, 25, 20, fill="none", stroke=RED_S, sw=1.5))

    txt_p4 = ["Сигнатура: (+, 0, -)", "", "• λ₁ > 0 (розходження)", "• λ₂ = 0 (потік)", "• λ₃ < 0 (дисипація)", "• ∑ λᵢ < 0 (хаос)"]
    frags.append(mtext(755, 230, txt_p4, size=11, color=RED_S, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "fig2-attractor-signatures.svg"), W, H, *frags)


def fig_qr_renormalization():
    """fig3-qr-renormalization.svg: Схема алгоритму реортогоналізації та ренормалізації QR (алгоритм Бенеттіна/Вольфа)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгоритм Бенеттіна-Вольфа: ортогоналізація Грама-Шмідта / QR-розклад", size=16, bold=True, color="#1e293b"))

    # Крок 1: Початкові ортонормовані базисні вектори Q(t_k)
    frags.append(rect(30, 60, 240, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(150, 85, "1. Орт-базис Q(tₖ)", size=13, bold=True, color=BLUE_S))
    
    frags.append(arrow(150, 180, 210, 180, color=BLUE_S, sw=2))
    frags.append(arrow(150, 180, 150, 120, color=BLUE_S, sw=2))
    frags.append(text(215, 175, "q₁", size=11, bold=True, color=BLUE_S, anchor="start"))
    frags.append(text(150, 110, "q₂", size=11, bold=True, color=BLUE_S, anchor="middle"))

    txt_s1 = ["• Вектори qᵢ ортогональні", "• Одинична довжина: ||qᵢ|| = 1", "• Базис у дотичному просторі"]
    frags.append(mtext(150, 260, txt_s1, size=11, color=BLUE_S, anchor="middle", lh=1.4))

    # Стрілка інтегрування
    frags.append(arrow(275, 180, 315, 180, color=AMBER_S, sw=2.5))
    frags.append(text(295, 155, "Інтегрування Δt", size=10, bold=True, color=AMBER_S, anchor="middle"))
    frags.append(text(295, 170, "в Якобіані J", size=9, italic=True, color=AMBER_S, anchor="middle"))

    # Крок 2: Спотворення та колінеаризація Y(t_{k+1})
    frags.append(rect(320, 60, 240, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(440, 85, "2. Спотворення Y(tₖ₊₁)", size=13, bold=True, color=RED_S))

    frags.append(arrow(440, 180, 540, 150, color=RED_S, sw=2.5))
    frags.append(arrow(440, 180, 510, 160, color=AMBER_S, sw=2))
    frags.append(text(545, 145, "y₁ (величезний)", size=10, bold=True, color=RED_S, anchor="start"))
    frags.append(text(515, 175, "y₂ (колапс до y₁)", size=10, bold=True, color=AMBER_S, anchor="start"))

    txt_s2 = ["• y₁ неконтрольовано зростає", "• y₂ нахиляється до напрямку y₁", "• Загроза переповнення та", "  втрати базісного кута"]
    frags.append(mtext(440, 260, txt_s2, size=11, color=RED_S, anchor="middle", lh=1.35))

    # Стрілка QR-розкладу
    frags.append(arrow(565, 180, 605, 180, color=GREEN_S, sw=2.5))
    frags.append(text(585, 155, "QR-розклад", size=10, bold=True, color=GREEN_S, anchor="middle"))
    frags.append(text(585, 170, "Gram-Schmidt", size=9, italic=True, color=GREEN_S, anchor="middle"))

    # Крок 3: Реортогоналізовані q_{k+1} та діагональ R_{ii}
    frags.append(rect(610, 60, 240, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(730, 85, "3. Ренормалізація Q(tₖ₊₁)", size=13, bold=True, color=GREEN_S))

    frags.append(arrow(730, 180, 790, 180, color=GREEN_S, sw=2))
    frags.append(arrow(730, 180, 730, 120, color=GREEN_S, sw=2))
    frags.append(text(795, 175, "q₁'", size=11, bold=True, color=GREEN_S, anchor="start"))
    frags.append(text(730, 110, "q₂'", size=11, bold=True, color=GREEN_S, anchor="middle"))

    txt_s3 = ["• Норма Rᵢᵢ = ||yᵢ'||", "• Сумування: ∑ ln(Rᵢᵢ)", "• λᵢ = (1/T) ∑ ln(Rᵢᵢ)", "• Новий орт-базис готовий"]
    frags.append(mtext(730, 260, txt_s3, size=11, color=GREEN_S, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "fig3-qr-renormalization.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_ellipsoid_evolution()
    fig_attractor_signatures()
    fig_qr_renormalization()
    print("Lyapunov exponent figures generated successfully.")
