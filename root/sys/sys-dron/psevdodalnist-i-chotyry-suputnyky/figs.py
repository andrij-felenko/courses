# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Псевдодальність і чотири супутники»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_tof_pseudorange():
    """Фігура 1: Принцип Time of Flight і народження псевдодальності."""
    w, h = 860, 360
    frags = []

    # Заголовок блоків
    frags.append(text(210, 32, "Супутник (атомний годинник)", size=15, bold=True, color=INK))
    frags.append(text(650, 32, "Приймач дрона (кварцовий генератор)", size=15, bold=True, color=INK))

    # Супутник
    frags.append(rect(60, 55, 300, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(210, 82, "Випромінювання PRN-коду", size=13, bold=True, color=INK))
    frags.append(text(210, 104, "Мітка часу передачі: t_tx (GPS-час)", size=12, color=MUTED))
    frags.append(text(210, 126, "Похибка атомного годинника: δt_sat ≈ 0", size=12, color=FIELD))
    frags.append(text(210, 148, "(коригується ефемеридами до наносекунд)", size=11, color=MUTED))

    # Приймач
    frags.append(rect(500, 55, 300, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(650, 82, "Зсув кодової репліки корелятором", size=13, bold=True, color=INK))
    frags.append(text(650, 104, "Мітка часу прийому: t_rx = t_true + δt_rcv", size=12, color=POS))
    frags.append(text(650, 126, "Зсув кварцового годинника: δt_rcv", size=12, bold=True, color=POS))
    frags.append(text(650, 148, "Навіть 1 мкс зсуву дає помилку c·δt = 299.79 м!", size=11, color=POS))

    # Радіосигнал / політ
    frags.append(arrow(360, 110, 500, 110, color="#2563eb", sw=2.5))
    frags.append(text(430, 98, "Радіохвиля (c)", size=12, bold=True, color="#2563eb"))
    frags.append(text(430, 130, "Час польоту τ", size=11, color=MUTED))

    # Порівняння відстаней унизу
    # Справжня відстань r
    frags.append(rect(60, 195, 740, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(80, 220, "Справжня геометрична дальність r:", size=13, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(80, 244, "r = c · (t_rx_true − t_tx) = √[(X_sat − X)² + (Y_sat − Y)² + (Z_sat − Z)²]", size=12, color=INK, anchor="start"))

    # Псевдодальність rho
    frags.append(rect(60, 275, 740, 70, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(80, 300, "Виміряна псевдодальність ρ (Pseudorange):", size=13, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(80, 326, "ρ = c · (t_rx − t_tx) = r + c · δt_rcv − c · δt_sat + I_iono + T_trop + ε", size=13, bold=True, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "tof-pseudorange-principle.svg"), w, h, *frags)


def fig_four_satellites_intersection():
    """Фігура 2: Чому саме 4 супутники розв'язують позицію та час."""
    w, h = 860, 380
    frags = []

    # Ліва панель: 3 супутники без синхронізації
    frags.append(rect(30, 20, 380, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(220, 48, "3 супутники: годинник невідомий", size=14, bold=True, color="#b91c1c"))

    # Схематичні сфери / кола
    frags.append(circle(140, 140, 75, fill="none", stroke="#2563eb", sw=1.5))
    frags.append(circle(270, 130, 70, fill="none", stroke="#16a34a", sw=1.5))
    frags.append(circle(200, 230, 68, fill="none", stroke="#d97706", sw=1.5))

    # Позначення супутників
    frags.append(circle(140, 140, 5, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(125, 135, "Sat 1", size=11, bold=True, color="#2563eb"))
    frags.append(circle(270, 130, 5, fill="#16a34a", stroke=LINE, sw=1))
    frags.append(text(285, 125, "Sat 2", size=11, bold=True, color="#16a34a"))
    frags.append(circle(200, 230, 5, fill="#d97706", stroke=LINE, sw=1))
    frags.append(text(200, 250, "Sat 3", size=11, bold=True, color="#d97706"))

    # Область невизначеності
    frags.append(rect(180, 155, 45, 30, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(202, 174, "Δ", size=12, bold=True, color="#b91c1c"))

    frags.append(text(220, 295, "Через зсув годинника c·δt всі 3 сфери", size=12, color=INK))
    frags.append(text(220, 315, "роздуті на однакову величину і НЕ перетинаються", size=12, color=INK))
    frags.append(text(220, 335, "в одній точці. Розв'язку немає (4 невідомі, 3 рівняння).", size=11, bold=True, color="#b91c1c"))

    # Права панель: 4 супутники знаходять єдиний перетин
    frags.append(rect(450, 20, 380, 340, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(640, 48, "4 супутники: X, Y, Z + c·δt визначено", size=14, bold=True, color="#15803d"))

    # 4 сфери узгоджені
    frags.append(circle(560, 135, 65, fill="none", stroke="#2563eb", sw=1.2))
    frags.append(circle(690, 125, 68, fill="none", stroke="#16a34a", sw=1.2))
    frags.append(circle(620, 220, 62, fill="none", stroke="#d97706", sw=1.2))
    frags.append(circle(660, 180, 58, fill="none", stroke="#9333ea", sw=1.2))

    # Спільна точка перетину
    frags.append(circle(625, 160, 5, fill="#dc2626", stroke=LINE, sw=1.5))
    frags.append(text(638, 155, "Приймач (X, Y, Z)", size=11, bold=True, color="#dc2626", anchor="start"))

    frags.append(text(640, 295, "4-й супутник фіксує єдиний спільний радіус", size=12, color=INK))
    frags.append(text(640, 315, "і зсув годинника δt_rcv. Сфери сходяться в точку!", size=12, bold=True, color="#15803d"))
    frags.append(text(640, 335, "4 рівняння строго розв'язують 4 невідомі величини.", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "four-satellites-intersection.svg"), w, h, *frags)


def fig_linearization_geometry():
    """Фігура 3: Геометрія лінеаризації та ітерації Гаусса–Ньютона."""
    w, h = 860, 370
    frags = []

    # Блок супутників угорі
    frags.append(rect(40, 30, 780, 80, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(430, 52, "Сузір'я супутників у системі ECEF (відомі координати X_i, Y_i, Z_i)", size=13, bold=True, color=INK))

    sat_x = [110, 320, 540, 730]
    for i, sx in enumerate(sat_x, start=1):
        frags.append(circle(sx, 85, 12, fill="#3b82f6", stroke=LINE, sw=1.5))
        frags.append(text(sx, 89, f"S{i}", size=11, bold=True, color="#ffffff"))

    # Вектори напрямку u_i
    frags.append(arrow(110, 97, 280, 230, color="#64748b", sw=1.5))
    frags.append(text(180, 175, "u₁ = (x₀ − s₁)/r₁", size=11, color="#475569"))

    frags.append(arrow(320, 97, 300, 230, color="#64748b", sw=1.5))
    frags.append(text(325, 175, "u₂", size=11, color="#475569"))

    frags.append(arrow(540, 97, 320, 230, color="#64748b", sw=1.5))
    frags.append(text(445, 175, "u₃", size=11, color="#475569"))

    frags.append(arrow(730, 97, 335, 230, color="#64748b", sw=1.5))
    frags.append(text(555, 175, "u₄", size=11, color="#475569"))

    # Початкова точка наближення x_0
    frags.append(circle(300, 240, 8, fill="#f59e0b", stroke=LINE, sw=1.5))
    frags.append(text(255, 245, "Оцінка x₀", size=12, bold=True, color="#b45309"))

    # Крок уточнення Delta x
    frags.append(arrow(300, 240, 470, 280, color="#ef4444", sw=2.2))
    frags.append(text(380, 250, "Крок Δx = (GᵀWG)⁻¹ GᵀW Δρ", size=12, bold=True, color="#dc2626"))

    # Справжня позиція x_true
    frags.append(circle(480, 282, 8, fill="#10b981", stroke=LINE, sw=1.5))
    frags.append(text(535, 287, "Справжня позиція x*", size=12, bold=True, color="#047857"))

    # Пояснення матриці геометрії G унизу
    frags.append(rect(40, 310, 780, 48, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(430, 328, "Матриця геометрії G: рядок i містить [ (X₀ − X_i)/r_i,  (Y₀ − Y_i)/r_i,  (Z₀ − Z_i)/r_i,  1 ]", size=12, bold=True, color=INK))
    frags.append(text(430, 346, "Ітерація Гаусса–Ньютона збігається до сантиметрової точності за 3–4 кроки", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "gnss-linearization-geometry.svg"), w, h, *frags)


def fig_dop_dilution():
    """Фігура 4: Геометричне погіршення точності (DOP) — хороша та погана конфігурації."""
    w, h = 860, 360
    frags = []

    # Ліва панель: хороша геометрія (низький DOP)
    frags.append(rect(30, 20, 380, 320, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(220, 46, "Хороша геометрія (Низький DOP ≈ 1.5)", size=13, bold=True, color="#15803d"))

    # Супутники розкидані по всій півсфері
    frags.append(circle(100, 90, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(100, 76, "S1 (Захід)", size=10, color=MUTED))

    frags.append(circle(340, 90, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(340, 76, "S2 (Схід)", size=10, color=MUTED))

    frags.append(circle(220, 70, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(220, 58, "S3 (Зеніт)", size=10, color=MUTED))

    frags.append(circle(220, 140, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(220, 126, "S4 (Південь)", size=10, color=MUTED))

    # Приймач і компактна область похибки
    frags.append(circle(220, 210, 5, fill="#dc2626", stroke=LINE, sw=1.5))
    frags.append(circle(220, 210, 22, fill="#dcfce7", stroke="#22c55e", sw=1.5))
    frags.append(text(220, 214, "•", size=14, color="#dc2626"))

    frags.append(text(220, 260, "Великий об'єм тетраедра променів", size=12, bold=True, color="#15803d"))
    frags.append(text(220, 282, "Помилка псевдодальності 1 м → помилка позиції 1.5 м", size=11, color=INK))
    frags.append(text(220, 302, "Матриця (GᵀG) добре обумовлена", size=11, color=MUTED))

    # Права панель: погана геометрія (високий DOP)
    frags.append(rect(450, 20, 380, 320, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(640, 46, "Погана геометрія (Високий DOP > 8.0)", size=13, bold=True, color="#b91c1c"))

    # Супутники скупчені в одній лінії / секторі
    frags.append(circle(580, 80, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(circle(620, 85, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(circle(660, 90, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(circle(700, 95, 8, fill="#3b82f6", stroke=LINE, sw=1))
    frags.append(text(640, 115, "Супутники в одному вузькому секторі неба", size=10, color=MUTED))

    # Приймач і витягнутий еліпс похибки
    frags.append(circle(640, 210, 5, fill="#dc2626", stroke=LINE, sw=1.5))
    # Еліпс невизначеності
    frags.append('<ellipse cx="640" cy="210" rx="75" ry="14" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5" transform="rotate(-20 640 210)"/>')
    frags.append(text(640, 214, "•", size=14, color="#dc2626"))

    frags.append(text(640, 260, "Сплюснутий тетраедр, визначник GᵀG ≈ 0", size=12, bold=True, color="#b91c1c"))
    frags.append(text(640, 282, "Помилка псевдодальності 1 м → помилка позиції 10–25 м!", size=11, color=INK))
    frags.append(text(640, 302, "Міський каньйон або екранування крилом дрона", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "dop-geometric-dilution.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_tof_pseudorange()
    fig_four_satellites_intersection()
    fig_linearization_geometry()
    fig_dop_dilution()
    print("Всі фігури успішно згенеровано у", OUT_DIR)
