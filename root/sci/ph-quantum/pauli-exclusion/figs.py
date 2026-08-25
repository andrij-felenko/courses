# -*- coding: utf-8 -*-
"""Фігури для теми «Принцип заборони Паулі» (book/physics/quantum-mechanics/pauli-exclusion)."""
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


def circle_svg(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def fig_fermion_vs_boson():
    """fig1-fermion-vs-boson.svg: Симетрична та антисиметрична хвильові функції (бозони vs ферміони)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Квантова тотожність: бозонне групування та ферміонне відчуження", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Бозони (Симетричний стан)
    frags.append(rect(30, 55, 400, 340, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(230, 80, "Бозони: симетрична функція Ψ_S", size=14, bold=True, color=GREEN_S))
    frags.append(text(230, 100, "Ψ(r₁, r₂) = + Ψ(r₂, r₁)", size=12, bold=True, color="#15803d"))

    # Осі для бозонів
    frags.append(line(70, 320, 390, 320, color="#64748b", sw=1.5))
    frags.append(line(70, 320, 70, 130, color="#64748b", sw=1.5))
    frags.append(text(385, 340, "r₁ - r₂", size=11, color="#475569"))
    frags.append(text(50, 125, "|Ψ|²", size=11, bold=True, color="#475569"))

    # Крива бозонної піковості (конструктивна інтерференція)
    b_pts = []
    for x_i in range(70, 391, 5):
        dx = (x_i - 230) / 45.0
        val = math.exp(- dx * dx) + 0.35 * math.exp(- dx * dx * 0.2)
        y_i = 320 - val * 110
        b_pts.append(f"{x_i:.1f},{y_i:.1f}")
    frags.append(f'<polyline points="{" ".join(b_pts)}" fill="none" stroke="{GREEN_S}" stroke-width="2.8"/>')

    # Пунктир класичного розподілу
    c_pts1 = []
    for x_i in range(70, 391, 5):
        dx = (x_i - 230) / 45.0
        val = 0.6 * math.exp(- dx * dx * 0.3)
        y_i = 320 - val * 110
        c_pts1.append(f"{x_i:.1f},{y_i:.1f}")
    frags.append(f'<polyline points="{" ".join(c_pts1)}" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Пояснення бозонів
    frags.append(circle_svg(230, 320, 4, fill=GREEN_S, stroke=GREEN_S))
    b_bos, _, _ = textbox(230, 210, "Максимум імовірності\nпри r₁ = r₂ (Бозе-конденсація)", size=11, bold=True, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_bos)

    # Права частина: Ферміони (Антисиметричний стан)
    frags.append(rect(450, 55, 400, 340, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(650, 80, "Ферміони: антисиметрична функція Ψ_A", size=14, bold=True, color=RED_S))
    frags.append(text(650, 100, "Ψ(r₁, r₂) = - Ψ(r₂, r₁)", size=12, bold=True, color="#b91c1c"))

    # Осі для ферміонів
    frags.append(line(490, 320, 810, 320, color="#64748b", sw=1.5))
    frags.append(line(490, 320, 490, 130, color="#64748b", sw=1.5))
    frags.append(text(805, 340, "r₁ - r₂", size=11, color="#475569"))
    frags.append(text(470, 125, "|Ψ|²", size=11, bold=True, color="#475569"))

    # Крива ферміонного занулення (Фермі-дірка)
    f_pts = []
    for x_i in range(490, 811, 5):
        dx = (x_i - 650) / 45.0
        val = (dx * dx) * math.exp(- dx * dx * 0.4)
        y_i = 320 - val * 130
        f_pts.append(f"{x_i:.1f},{y_i:.1f}")
    frags.append(f'<polyline points="{" ".join(f_pts)}" fill="none" stroke="{RED_S}" stroke-width="2.8"/>')

    # Пунктир класичного розподілу
    c_pts2 = []
    for x_i in range(490, 811, 5):
        dx = (x_i - 650) / 45.0
        val = 0.6 * math.exp(- dx * dx * 0.3)
        y_i = 320 - val * 110
        c_pts2.append(f"{x_i:.1f},{y_i:.1f}")
    frags.append(f'<polyline points="{" ".join(c_pts2)}" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Точка занулення та Фермі-дірка
    frags.append(circle_svg(650, 320, 5, fill="#ffffff", stroke=RED_S, sw=2.0))
    b_fer, _, _ = textbox(650, 240, "Строге занулення |Ψ|² = 0\nпри r₁ = r₂ (Фермі-дірка)", size=11, bold=True, fill="#ffffff", stroke=RED_S)
    frags.append(b_fer)

    render(os.path.join(IMG, "fig1-fermion-vs-boson.svg"), W, H, *frags)


def fig_slater_determinant():
    """fig2-slater-determinant.svg: Структура детермінанта Слейтера та заборона однакових станів."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Конструкція детермінанта Слейтера для N ферміонів", size=16, bold=True, color="#1e293b"))

    # Множник 1/sqrt(N!)
    frags.append(rect(30, 70, 100, 320, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8, rx=6))
    frags.append(text(80, 210, "Множник", size=12, color="#6b21a8"))
    frags.append(text(80, 235, "1 / √(N!)", size=16, bold=True, color=PURPLE_S))
    frags.append(text(80, 260, "Нормування", size=11, color="#6b21a8"))

    # Великий детермінант (дужки матриці)
    frags.append(path_svg("M 150 70 L 140 70 L 140 390 L 150 390", stroke="#334155", sw=3.0))
    frags.append(path_svg("M 730 70 L 740 70 L 740 390 L 750 390", stroke="#334155", sw=3.0))

    # Стовпчик 1: Орбіталь φ1
    frags.append(rect(160, 85, 160, 290, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=6))
    frags.append(text(240, 110, "Стан φ₁ (n₁, l₁, m₁, s₁)", size=12, bold=True, color=BLUE_S))
    frags.append(text(240, 160, "φ₁(x₁)", size=14, color="#1e3a8a"))
    frags.append(text(240, 220, "φ₁(x₂)", size=14, color="#1e3a8a"))
    frags.append(text(240, 280, "⋮", size=16, color="#1e3a8a"))
    frags.append(text(240, 340, "φ₁(x_N)", size=14, color="#1e3a8a"))

    # Стовпчик 2: Орбіталь φ2
    frags.append(rect(340, 85, 160, 290, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=6))
    frags.append(text(420, 110, "Стан φ₂ (n₂, l₂, m₂, s₂)", size=12, bold=True, color=AMBER_S))
    frags.append(text(420, 160, "φ₂(x₁)", size=14, color="#b45309"))
    frags.append(text(420, 220, "φ₂(x₂)", size=14, color="#b45309"))
    frags.append(text(420, 280, "⋮", size=16, color="#b45309"))
    frags.append(text(420, 340, "φ₂(x_N)", size=14, color="#b45309"))

    # Стовпчик N: Орбіталь φN
    frags.append(rect(550, 85, 170, 290, fill=TEAL_F, stroke=TEAL_S, sw=1.5, rx=6))
    frags.append(text(635, 110, "Стан φ_N (n_N, l_N, ...)", size=12, bold=True, color=TEAL_S))
    frags.append(text(635, 160, "φ_N(x₁)", size=14, color="#0f766e"))
    frags.append(text(635, 220, "φ_N(x₂)", size=14, color="#0f766e"))
    frags.append(text(635, 280, "⋮", size=16, color="#0f766e"))
    frags.append(text(635, 340, "φ_N(x_N)", size=14, color="#0f766e"))

    # Три крапки між стовпчиками
    frags.append(text(515, 220, "⋯", size=22, bold=True, color="#64748b"))

    # Пояснення праворуч: Результат при збігу станів
    b_rule, _, _ = textbox(770, 230, "Якщо φ₁ = φ₂:\nДва однакові стовпчики\n⇒ Det = 0!\n(Принцип Паулі)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_rule)

    render(os.path.join(IMG, "fig2-slater-determinant.svg"), W, H, *frags)


def fig_atomic_shells():
    """fig3-atomic-shells.svg: Заповнення атомних оболон (1s, 2s, 2p, 3s) та принцип Паулі."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Атомні рівні енергії та заповнення оболонок за принципом Паулі", size=16, bold=True, color="#1e293b"))

    # Вісь енергії
    frags.append(line(60, 390, 60, 60, color="#334155", sw=2.0))
    frags.append(path_svg("M 55 70 L 60 55 L 65 70 Z", fill="#334155", stroke="#334155"))
    frags.append(text(45, 60, "E", size=14, bold=True, color="#1e293b"))

    # Рівень 1s
    frags.append(line(100, 350, 280, 350, color="#64748b", sw=2.0))
    frags.append(text(190, 385, "1s (n=1, l=0): max 2 e⁻", size=12, bold=True, color="#475569"))
    # Електрони в 1s (прямокутник 70x54)
    frags.append(rect(155, 286, 70, 54, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=4))
    frags.append(line(178, 330, 178, 302, color=BLUE_S, sw=2.8)) # spin up line
    frags.append(line(202, 298, 202, 326, color=RED_S, sw=2.8))  # spin down line
    frags.append(text(178, 296, "↑", size=13, bold=True, color=BLUE_S))
    frags.append(text(202, 334, "↓", size=13, bold=True, color=RED_S))

    # Рівень 2s
    frags.append(line(100, 260, 280, 260, color="#64748b", sw=2.0))
    frags.append(text(190, 282, "2s (n=2, l=0): max 2 e⁻", size=12, bold=True, color="#475569"))
    # Електрони в 2s
    frags.append(rect(155, 196, 70, 54, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=4))
    frags.append(line(178, 240, 178, 212, color=BLUE_S, sw=2.8))
    frags.append(line(202, 208, 202, 236, color=RED_S, sw=2.8))
    frags.append(text(178, 206, "↑", size=13, bold=True, color=BLUE_S))
    frags.append(text(202, 244, "↓", size=13, bold=True, color=RED_S))

    # Рівень 2p (3 комірки)
    frags.append(line(340, 190, 620, 190, color="#64748b", sw=2.0))
    frags.append(text(480, 215, "2p (n=2, l=1): 3 орбіталі, max 6 e⁻", size=12, bold=True, color="#475569"))
    
    # 3 комірки p-орбіталі
    for idx in range(3):
        cx = 360 + idx * 85
        frags.append(rect(cx, 126, 70, 54, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=4))
        frags.append(line(cx + 23, 170, cx + 23, 142, color=BLUE_S, sw=2.8))
        frags.append(line(cx + 47, 138, cx + 47, 166, color=RED_S, sw=2.8))
        frags.append(text(cx + 23, 136, "↑", size=13, bold=True, color=BLUE_S))
        frags.append(text(cx + 47, 174, "↓", size=13, bold=True, color=RED_S))

    # Рівень 3s
    frags.append(line(650, 130, 830, 130, color="#64748b", sw=2.0))
    frags.append(text(740, 150, "3s (n=3, l=0): max 2 e⁻", size=12, bold=True, color="#475569"))
    frags.append(rect(705, 66, 70, 54, fill=TEAL_F, stroke=TEAL_S, sw=1.5, rx=4))
    frags.append(line(740, 110, 740, 82, color=BLUE_S, sw=2.8))
    frags.append(text(740, 76, "↑", size=13, bold=True, color=BLUE_S))

    # Інформаційна картка про квантові числа
    b_qnum, _, _ = textbox(440, 340, "Квантовий стан електрона: (n, l, m_l, m_s)\nЗа принципом Паулі: одна комірка містить не більше двох електронів\nз протилежними спінами (m_s = +1/2 та m_s = -1/2).", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_qnum)

    render(os.path.join(IMG, "fig3-atomic-shells.svg"), W, H, *frags)


def fig_fermi_degeneracy():
    """fig4-fermi-degeneracy.svg: Сфера Фермі та тиск виродженого електронного газу."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Сфера Фермі в імпульсному просторі та тиск виродження", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Сфера Фермі
    frags.append(rect(30, 60, 390, 340, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Сфера Фермі (T = 0 K)", size=14, bold=True, color=BLUE_S))

    # Осі p_x, p_y
    frags.append(line(225, 240, 370, 240, color="#64748b", sw=1.5))
    frags.append(line(225, 240, 225, 95, color="#64748b", sw=1.5))
    frags.append(line(225, 240, 110, 330, color="#64748b", sw=1.5))
    frags.append(text(360, 260, "p_x", size=11, bold=True, color="#475569"))
    frags.append(text(210, 105, "p_z", size=11, bold=True, color="#475569"))
    frags.append(text(100, 345, "p_y", size=11, bold=True, color="#475569"))

    # Заповнене коло Сфери Фермі
    frags.append(circle_svg(225, 240, 95, fill="#93c5fd", stroke=BLUE_S, sw=2.0))
    frags.append(line(225, 240, 305, 185, color=RED_S, sw=2.0))
    frags.append(circle_svg(305, 185, 3.5, fill=RED_S, stroke=RED_S))
    frags.append(text(285, 220, "p_F", size=13, bold=True, color=RED_S))

    b_sp, _, _ = textbox(225, 360, "Усі квантові стани з p ≤ p_F\nповністю заповнені (n = 1)", size=11, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_sp)

    # Права частина: Густина станів g(E) та розподіл заповнення
    frags.append(rect(440, 60, 410, 340, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(645, 85, "Розподіл Фермі — Дірака f(E)", size=14, bold=True, color=AMBER_S))

    # Осі для графіку
    frags.append(line(480, 330, 820, 330, color="#64748b", sw=1.5))
    frags.append(line(480, 330, 480, 110, color="#64748b", sw=1.5))
    frags.append(text(810, 350, "Енергія E", size=11, bold=True, color="#475569"))
    frags.append(text(460, 115, "f(E)", size=11, bold=True, color="#475569"))

    # Сходинка при T = 0 K
    frags.append(line(480, 150, 630, 150, color=BLUE_S, sw=2.8))
    frags.append(line(630, 150, 630, 330, color=BLUE_S, sw=2.8))
    frags.append(line(630, 330, 810, 330, color=BLUE_S, sw=2.8))

    # Пунктирна вертикаль E_F
    frags.append(line(630, 110, 630, 330, color=RED_S, sw=1.5, dash="4,4"))
    frags.append(text(630, 355, "E_F", size=13, bold=True, color=RED_S))

    # Розмиття при T > 0 K
    t_pts = []
    for x_i in range(480, 811, 5):
        energy = (x_i - 630) / 25.0
        val = 1.0 / (1.0 + math.exp(energy))
        y_i = 330 - val * 180
        t_pts.append(f"{x_i:.1f},{y_i:.1f}")
    frags.append(f'<polyline points="{" ".join(t_pts)}" fill="none" stroke="{AMBER_S}" stroke-width="2.0" stroke-dasharray="6,3"/>')

    # Розміщуємо роз'яснення вище лінії, у порожній верхній правому кутку (730, 170)
    b_deg, _, _ = textbox(730, 170, "Тиск виродження P_deg ∝ n_e^(5/3)\nНе залежить від T при T ≪ T_F!", size=10, bold=True, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_deg)

    render(os.path.join(IMG, "fig3-atomic-shells.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_fermion_vs_boson()
    fig_slater_determinant()
    fig_atomic_shells()
    fig_fermi_degeneracy()
    print("Всі фігури успішно згенеровано.")
