# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Ома у диференціальній формі».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_microscopic_drift_drude():
    """Фігура 1: Хаотичний тепловий рух та дрейф електронів у моделі Друде під дією поля E."""
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Мікроскопічний механізм струму: хаотичний рух та дрейф у полі", size=15, bold=True))

    # Ліва панель: E = 0 (тільки хаос)
    f.append(rect(20, 50, 360, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(200, 75, "Без електричного поля (E = 0)", size=13, bold=True, color=INK))
    f.append(text(200, 95, "v_th ~ 10⁶ м/с, дрейф <v> = 0", size=11, color=MUTED))

    # Іони ґратки (позитивні вузли)
    ions_left = [(70, 140), (150, 140), (230, 140), (310, 140),
                 (70, 210), (150, 210), (230, 210), (310, 210),
                 (70, 280), (150, 280), (230, 280), (310, 280)]
    for ix, iy in ions_left:
        f.append(plus(ix, iy, r=10))

    # Траєкторія без поля (замкнена / випадкова, повернення поруч)
    pts_e0 = [(90, 160), (145, 145), (225, 205), (155, 275), (75, 215), (92, 162)]
    for i in range(len(pts_e0) - 1):
        x1, y1 = pts_e0[i]
        x2, y2 = pts_e0[i+1]
        f.append(line(x1, y1, x2, y2, color="#64748b", sw=1.8, dash="3,2"))
        f.append(arrow(x1, y1, (x1 + x2)/2, (y1 + y2)/2, color="#475569", sw=1.6))

    f.append(circle(90, 160, 5, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
    f.append(text(90, 145, "e⁻", size=10, bold=True, color="#1d4ed8"))
    f.append(text(200, 318, "Сумарне зміщення заряду Δr = 0", size=11, bold=True, color="#475569"))

    # Права панель: E > 0 (хаос + напрямлений дрейф)
    f.append(rect(400, 50, 360, 280, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    f.append(text(580, 75, "Під дією поля (E > 0, вправо)", size=13, bold=True, color="#1e40af"))
    f.append(text(580, 95, "Сила F = -e·E (вліво) → дрейф v_d", size=11, color="#2563eb"))

    # Стрілка напруженості поля E
    f.append(arrow(430, 115, 520, 115, color="#dc2626", sw=2.5))
    f.append(text(535, 118, "E", size=13, bold=True, color="#dc2626", anchor="start"))

    # Стрілка густини струму j
    f.append(arrow(600, 115, 690, 115, color="#16a34a", sw=2.5))
    f.append(text(705, 118, "j = σ·E", size=13, bold=True, color="#16a34a", anchor="start"))

    # Іони ґратки
    ions_right = [(450, 160), (530, 160), (610, 160), (690, 160),
                  (450, 230), (530, 230), (610, 230), (690, 230),
                  (450, 300), (530, 300), (610, 300), (690, 300)]
    for ix, iy in ions_right:
        f.append(plus(ix, iy, r=10))

    # Траєкторія з полем: викривлення параболами вліво
    pts_e1 = [(670, 175), (605, 165), (525, 225), (455, 295), (430, 235)]
    for i in range(len(pts_e1) - 1):
        x1, y1 = pts_e1[i]
        x2, y2 = pts_e1[i+1]
        f.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.0))
        f.append(arrow(x1, y1, (x1 + x2)/2, (y1 + y2)/2, color="#1d4ed8", sw=1.8))

    # Початкова і кінцева точки
    f.append(circle(670, 175, 5, fill="#94a3b8", stroke="#475569", sw=1.2))
    f.append(text(670, 160, "старт", size=9, color=MUTED))
    f.append(circle(430, 235, 5, fill="#2563eb", stroke="#1e40af", sw=1.5))
    f.append(text(430, 220, "e⁻", size=10, bold=True, color="#1e40af"))

    # Вектор сумарного дрейфу електрона (вліво)
    f.append(arrow(670, 260, 440, 260, color="#2563eb", sw=2.2))
    f.append(text(555, 252, "Дрейф електронів v_d (вліво)", size=11, bold=True, color="#1e40af"))
    f.append(text(580, 318, "Струм j напрямлений вздовж E (вправо)", size=11, bold=True, color="#15803d"))

    return render(os.path.join(IMG, "microscopic-drift-drude.svg"), W, H, *f)


def fig_differential_volume_element():
    """Фігура 2: Перехід від інтегрального закону (провідник L, A) до диференціального (елемент dV)."""
    W, H = 780, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Перехід від інтегрального закону Ома до диференціального", size=15, bold=True))

    # Лівий блок: Макроскопічний однорідний провідник
    f.append(rect(20, 46, 360, 274, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(200, 70, "Макроскопічний рівень (коло)", size=13, bold=True, color=INK))

    # Циліндр провідника
    f.append(rect(80, 110, 200, 70, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=4))
    # Переріз зліва (еліпс)
    f.append(circle(80, 145, 35, fill="#fde68a", stroke="#d97706", sw=1.5))
    f.append(text(65, 149, "A", size=12, bold=True, color="#92400e"))

    # Довжина L
    f.append(line(80, 195, 280, 195, color="#475569", sw=1.5))
    f.append(line(80, 190, 80, 200, color="#475569", sw=1.5))
    f.append(line(280, 190, 280, 200, color="#475569", sw=1.5))
    f.append(text(180, 210, "довжина L", size=11, bold=True, color="#475569"))

    # Напруга та струм
    f.append(arrow(40, 145, 75, 145, color="#16a34a", sw=2.2))
    f.append(text(40, 130, "I", size=13, bold=True, color="#16a34a"))
    f.append(text(180, 100, "U = V₁ - V₂", size=12, bold=True, color="#dc2626"))

    # Формули макро
    f.append(textbox(200, 260, "R = ρ · L / A\nI = U / R = (U · A) / (ρ · L)", size=12, bold=True, fill="#fffbeb", stroke="#f59e0b")[0])

    # Центральна стрілка переходу
    f.append(arrow(383, 170, 407, 170, color="#2563eb", sw=2.5))
    f.append(text(395, 155, "dV→0", size=10, bold=True, color="#2563eb"))

    # Правий блок: Диференціальний елемент об'єму dV
    f.append(rect(410, 46, 350, 274, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    f.append(text(585, 70, "Диференціальний рівень (точка)", size=13, bold=True, color="#166534"))

    # Кубик dx dy dz
    f.append(rect(520, 110, 80, 65, fill="#dcfce7", stroke="#16a34a", sw=1.8, rx=3))
    f.append(text(560, 146, "dV", size=12, bold=True, color="#15803d"))

    # Вектори E та j у точці
    f.append(arrow(460, 142, 515, 142, color="#dc2626", sw=2.2))
    f.append(text(485, 132, "E(r)", size=12, bold=True, color="#dc2626"))

    f.append(arrow(605, 142, 675, 142, color="#16a34a", sw=2.5))
    f.append(text(645, 132, "j(r)", size=12, bold=True, color="#16a34a"))

    f.append(text(560, 190, "j = I / A,  E = U / L", size=11, bold=True, color="#334155"))

    # Локальний закон Ома
    f.append(textbox(585, 255, "j = σ · E   або   E = ρ · j\nσ = 1 / ρ  [См/м]", size=13, bold=True, fill="#ffffff", stroke="#16a34a")[0])

    return render(os.path.join(IMG, "differential-volume-element.svg"), W, H, *f)


def fig_temperature_dependence():
    """Фігура 3: Порівняння температурної залежності питомого опору металів і напівпровідників."""
    W, H = 780, 330
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Температурна залежність питомого опору: метали проти напівпровідників", size=15, bold=True))

    # Лівий графік: Метал
    f.append(rect(20, 46, 360, 264, fill="#fafbfc", stroke="#e2e8f0", sw=1.5, rx=8))
    f.append(text(200, 68, "Метали (ρ зростає з T)", size=13, bold=True, color="#1e293b"))

    # Осі
    f.append(arrow(60, 250, 350, 250, color=LINE, sw=1.5))
    f.append(text(340, 268, "T [K]", size=11, bold=True, color=INK))
    f.append(arrow(60, 250, 60, 90, color=LINE, sw=1.5))
    f.append(text(45, 95, "ρ", size=13, bold=True, color=INK))

    # Крива металу (залишковий опір при T=0 + лінійне зростання)
    f.append(line(60, 215, 120, 210, color="#dc2626", sw=2.5))
    f.append(line(120, 210, 330, 110, color="#dc2626", sw=2.5))
    f.append(circle(60, 215, 3.5, fill="#dc2626", stroke="#991b1b", sw=1.2))
    f.append(text(75, 230, "ρ_залишк", size=10, bold=True, color="#991b1b"))

    f.append(text(230, 125, "ρ(T) = ρ₀(1 + αΔT)", size=11, bold=True, color="#dc2626"))
    f.append(text(200, 285, "n = const, розсіювання на фононах зростає", size=10, color=MUTED))

    # Правий графік: Напівпровідник
    f.append(rect(400, 46, 360, 264, fill="#fafbfc", stroke="#e2e8f0", sw=1.5, rx=8))
    f.append(text(580, 68, "Напівпровідники (ρ спадає з T)", size=13, bold=True, color="#1e293b"))

    # Осі
    f.append(arrow(440, 250, 730, 250, color=LINE, sw=1.5))
    f.append(text(720, 268, "T [K]", size=11, bold=True, color=INK))
    f.append(arrow(440, 250, 440, 90, color=LINE, sw=1.5))
    f.append(text(425, 95, "ρ", size=13, bold=True, color=INK))

    # Крива напівпровідника (експоненційний спад)
    pts_semi = [(450, 105), (470, 125), (500, 165), (540, 205), (600, 230), (710, 242)]
    for i in range(len(pts_semi) - 1):
        x1, y1 = pts_semi[i]
        x2, y2 = pts_semi[i+1]
        f.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.5))

    f.append(text(610, 135, "ρ(T) ∝ exp(E_g / 2kT)", size=11, bold=True, color="#2563eb"))
    f.append(text(580, 285, "n(T) експоненційно зростає (термогенерація)", size=10, color=MUTED))

    return render(os.path.join(IMG, "temperature-dependence.svg"), W, H, *f)


def fig_tensor_conductivity_hall():
    """Фігура 4: Анізотропія та тензор провідності в магнітному полі (ефект Холла)."""
    W, H = 780, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Анізотропія закону Ома у магнітному полі: кут Холла та недіагональна провідність", size=15, bold=True))

    # Ліва частина: Векторна діаграма
    f.append(rect(20, 46, 360, 254, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(200, 68, "Векторне відхилення j від E", size=13, bold=True, color=INK))

    # Початковий центр
    cx, cy = 90, 220

    # Вектор E (під кутом вгору-вправо)
    f.append(arrow(cx, cy, cx + 220, cy - 80, color="#dc2626", sw=2.5))
    f.append(text(cx + 235, cy - 85, "E", size=14, bold=True, color="#dc2626"))

    # Вектор j (відхилений від E)
    f.append(arrow(cx, cy, cx + 210, cy, color="#16a34a", sw=2.5))
    f.append(text(cx + 225, cy + 5, "j", size=14, bold=True, color="#16a34a"))

    # Кут Холла theta_H
    f.append(text(cx + 120, cy - 20, "θ_H", size=13, bold=True, color="#2563eb"))

    # Магнітне поле B (перпендикулярно площині, на нас)
    f.append(circle(80, 95, 12, fill="#eff6ff", stroke="#2563eb", sw=1.8))
    f.append(circle(80, 95, 3, fill="#2563eb", stroke="#2563eb", sw=1))
    f.append(text(105, 100, "B ⊙ (перпендикулярно)", size=12, bold=True, color="#2563eb"))

    f.append(text(200, 275, "Сила Лоренца F_L = q(v_d × B) розвертає j", size=11, bold=True, color="#334155"))

    # Права частина: Матричний / тензорний запис
    f.append(rect(400, 46, 360, 254, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(580, 68, "Тензорний закон Ома: j_i = ∑ σ_ik E_k", size=13, bold=True, color=INK))

    f.append(textbox(580, 140, "┌ j_x ┐   ┌  σ_xx   σ_xy  0 ┐ ┌ E_x ┐\n│ j_y │ = │ -σ_xy   σ_xx  0 │ │ E_y │\n└ j_z ┘   └   0       0   σ ┘ └ E_z ┘", size=12, bold=True, fill="#ffffff", stroke="#94a3b8")[0])

    f.append(textbox(580, 240, "σ_xx = σ₀ / (1 + (ω_c · τ)²)\nσ_xy = σ₀ · (ω_c · τ) / (1 + (ω_c · τ)²)", size=12, bold=True, fill="#eff6ff", stroke="#3b82f6")[0])

    return render(os.path.join(IMG, "tensor-conductivity-hall.svg"), W, H, *f)


if __name__ == '__main__':
    fig_microscopic_drift_drude()
    fig_differential_volume_element()
    fig_temperature_dependence()
    fig_tensor_conductivity_hall()
    print("All figures generated successfully.")
