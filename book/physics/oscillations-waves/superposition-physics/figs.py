# -*- coding: utf-8 -*-
"""Фігури до теми «Суперпозиція у фізиці».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_PRIMARY = "#2457d6"
C_SECONDARY = "#c0392b"
C_GREEN = "#1e8449"
C_PURPLE = "#7d3c98"
C_DARK = "#1a1a1a"
C_GRID = "#e6e9ee"
C_BG_BOX = "#f8f9fa"

def poly(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)

# ── Фігура 1: Схема визначення лінійного оператора ─────────────────────────────
def fig_linearity_definition():
    W, H = 840, 440
    tb1, _, _ = textbox(280, 90, "Оператор L", size=14, fill="#eef3fd", stroke=C_PRIMARY, bold=True)
    tb2, _, _ = textbox(280, 190, "Оператор L", size=14, fill="#fdeded", stroke=C_SECONDARY, bold=True)
    tb3, _, _ = textbox(280, 330, "Оператор L", size=14, fill="#f5eeef", stroke=C_PURPLE, bold=True)
    tb4, _, _ = textbox(650, 355, "Сума окремих\nвідгуків", size=13, fill="#eafaf1", stroke=C_GREEN)
    
    f = [
        text(W / 2, 25, "Визначення лінійного оператора: адитивність та однорідність", size=16, bold=True),
        # Канал 1
        arrow(60, 90, 220, 90, color=C_PRIMARY, sw=2.0),
        text(140, 75, "x₁", color=C_PRIMARY, size=15, bold=True),
        tb1,
        arrow(340, 90, 500, 90, color=C_PRIMARY, sw=2.0),
        text(420, 75, "y₁ = L(x₁)", color=C_PRIMARY, size=15, bold=True),

        # Канал 2
        arrow(60, 190, 220, 190, color=C_SECONDARY, sw=2.0),
        text(140, 175, "x₂", color=C_SECONDARY, size=15, bold=True),
        tb2,
        arrow(340, 190, 500, 190, color=C_SECONDARY, sw=2.0),
        text(420, 175, "y₂ = L(x₂)", color=C_SECONDARY, size=15, bold=True),

        # Лінія роздільника
        line(50, 240, 790, 240, color=C_GRID, sw=1.5, dash="4 4"),

        # Канал лінійної комбінації
        arrow(60, 330, 220, 330, color=C_PURPLE, sw=2.5),
        text(140, 310, "c₁ x₁ + c₂ x₂", color=C_PURPLE, size=15, bold=True),
        tb3,
        arrow(340, 330, 500, 330, color=C_PURPLE, sw=2.5),
        text(420, 310, "L(c₁ x₁ + c₂ x₂)", color=C_PURPLE, size=15, bold=True),

        # Двостороння стрілка доводу тотожності
        text(530, 335, "=", color=C_DARK, size=22, bold=True),
        text(650, 310, "c₁ y₁ + c₂ y₂", color=C_GREEN, size=16, bold=True),
        tb4
    ]
    render(os.path.join(IMG, "linearity-definition.svg"), W, H, *f)

# ── Фігура 2: Векторна суперпозиція полів у точці ──────────────────────────────
def fig_field_superposition():
    W, H = 760, 480
    tb, _, _ = textbox(200, 435, "Скалярні потенціали просто додаються:  V_tot = V₁ + V₂ + V₃", size=13, fill=C_BG_BOX, stroke="#bdc3c7")
    f = [
        text(W / 2, 25, "Векторне додавання полів (гравітаційних / електричних) у точці P", size=16, bold=True),
        # Джерела заряду / маси
        circle(120, 360, 18, fill="#eef3fd", stroke=C_PRIMARY, sw=2.5),
        text(120, 365, "q₁", color=C_PRIMARY, size=14, bold=True),

        circle(180, 100, 18, fill="#fdeded", stroke=C_SECONDARY, sw=2.5),
        text(180, 105, "q₂", color=C_SECONDARY, size=14, bold=True),

        circle(560, 400, 18, fill="#eafaf1", stroke=C_GREEN, sw=2.5),
        text(560, 405, "q₃", color=C_GREEN, size=14, bold=True),

        # Точка розрахунку P
        circle(420, 220, 7, fill=C_DARK, stroke="none"),
        text(400, 205, "Точка P", color=C_DARK, size=14, bold=True),

        # Лінії дії (пунктир)
        line(120, 360, 420, 220, color="#bdc3c7", sw=1.2, dash="3 3"),
        line(180, 100, 420, 220, color="#bdc3c7", sw=1.2, dash="3 3"),
        line(560, 400, 420, 220, color="#bdc3c7", sw=1.2, dash="3 3"),

        # Вектори складових полів від точки P
        arrow(420, 220, 540, 164, color=C_PRIMARY, sw=2.2),
        text(550, 155, "E₁", color=C_PRIMARY, size=14, bold=True),

        arrow(420, 220, 520, 270, color=C_SECONDARY, sw=2.2),
        text(525, 285, "E₂", color=C_SECONDARY, size=14, bold=True),

        arrow(420, 220, 364, 148, color=C_GREEN, sw=2.2),
        text(340, 140, "E₃", color=C_GREEN, size=14, bold=True),

        # Результуючий вектор E_total = E1 + E2 + E3
        arrow(420, 220, 584, 142, color=C_PURPLE, sw=3.5),
        text(620, 135, "E_tot = ∑ Eᵢ", color=C_PURPLE, size=16, bold=True),

        tb
    ]
    render(os.path.join(IMG, "field-superposition.svg"), W, H, *f)

# ── Фігура 3: Розрахунок кола за теоремою суперпозиції ─────────────────────────
def fig_circuit_superposition():
    W, H = 840, 420
    f = [
        text(W / 2, 25, "Теорема суперпозиції в електричних колах: активація джерел по черзі", size=16, bold=True),
        
        # (a) Повне коло
        rect(20, 55, 240, 320, fill="#ffffff", stroke="#bdc3c7", rx=6),
        text(140, 80, "а) Повне коло", size=14, bold=True),
        # Джерело V1
        circle(60, 200, 16, fill="#eef3fd", stroke=C_PRIMARY, sw=2.0),
        text(60, 204, "V₁", color=C_PRIMARY, size=12, bold=True),
        line(60, 120, 60, 184, color=C_DARK, sw=1.8),
        line(60, 216, 60, 280, color=C_DARK, sw=1.8),
        # Резистор R1
        line(60, 120, 120, 120, color=C_DARK, sw=1.8),
        rect(120, 110, 40, 20, fill="#ffffff", stroke=C_DARK, sw=1.8),
        text(140, 102, "R₁", size=11),
        line(160, 120, 220, 120, color=C_DARK, sw=1.8),
        # Резистор R2 вертикальний
        line(160, 120, 160, 170, color=C_DARK, sw=1.8),
        rect(150, 170, 20, 40, fill="#ffffff", stroke=C_DARK, sw=1.8),
        text(182, 192, "R₂", size=11),
        line(160, 210, 160, 280, color=C_DARK, sw=1.8),
        # Джерело V2
        circle(220, 200, 16, fill="#fdeded", stroke=C_SECONDARY, sw=2.0),
        text(220, 204, "V₂", color=C_SECONDARY, size=12, bold=True),
        line(220, 120, 220, 184, color=C_DARK, sw=1.8),
        line(220, 216, 220, 280, color=C_DARK, sw=1.8),
        # Нижній дріт
        line(60, 280, 220, 280, color=C_DARK, sw=1.8),
        # Струм I
        arrow(160, 140, 160, 165, color=C_PURPLE, sw=2.0),
        text(142, 155, "I", color=C_PURPLE, size=12, bold=True),

        # (b) Коло лише з V1 (V2 закорочено)
        rect(290, 55, 240, 320, fill="#ffffff", stroke="#bdc3c7", rx=6),
        text(410, 80, "б) Дійсне лише V₁", size=14, bold=True),
        circle(330, 200, 16, fill="#eef3fd", stroke=C_PRIMARY, sw=2.0),
        text(330, 204, "V₁", color=C_PRIMARY, size=12, bold=True),
        line(330, 120, 330, 184, color=C_DARK, sw=1.8),
        line(330, 216, 330, 280, color=C_DARK, sw=1.8),
        line(330, 120, 390, 120, color=C_DARK, sw=1.8),
        rect(390, 110, 40, 20, fill="#ffffff", stroke=C_DARK, sw=1.8),
        line(430, 120, 490, 120, color=C_DARK, sw=1.8),
        line(430, 120, 430, 170, color=C_DARK, sw=1.8),
        rect(420, 170, 20, 40, fill="#ffffff", stroke=C_DARK, sw=1.8),
        line(430, 210, 430, 280, color=C_DARK, sw=1.8),
        # V2 закорочено прямим дротом
        line(490, 120, 490, 280, color=C_DARK, sw=1.8),
        line(330, 280, 490, 280, color=C_DARK, sw=1.8),
        # Струм I^(1)
        arrow(430, 140, 430, 165, color=C_PRIMARY, sw=2.0),
        text(442, 155, "I⁽¹⁾", color=C_PRIMARY, size=12, bold=True),

        # (c) Коло лише з V2 (V1 закорочено)
        rect(560, 55, 240, 320, fill="#ffffff", stroke="#bdc3c7", rx=6),
        text(680, 80, "в) Дійсне лише V₂", size=14, bold=True),
        # V1 закорочено
        line(600, 120, 600, 280, color=C_DARK, sw=1.8),
        line(600, 120, 660, 120, color=C_DARK, sw=1.8),
        rect(660, 110, 40, 20, fill="#ffffff", stroke=C_DARK, sw=1.8),
        line(700, 120, 760, 120, color=C_DARK, sw=1.8),
        line(700, 120, 700, 170, color=C_DARK, sw=1.8),
        rect(690, 170, 20, 40, fill="#ffffff", stroke=C_DARK, sw=1.8),
        line(700, 210, 700, 280, color=C_DARK, sw=1.8),
        # V2
        circle(760, 200, 16, fill="#fdeded", stroke=C_SECONDARY, sw=2.0),
        text(760, 204, "V₂", color=C_SECONDARY, size=12, bold=True),
        line(760, 120, 760, 184, color=C_DARK, sw=1.8),
        line(760, 216, 760, 280, color=C_DARK, sw=1.8),
        line(600, 280, 760, 280, color=C_DARK, sw=1.8),
        # Струм I^(2)
        arrow(700, 140, 700, 165, color=C_SECONDARY, sw=2.0),
        text(712, 155, "I⁽²⁾", color=C_SECONDARY, size=12, bold=True),

        # Формула підсумку
        text(W / 2, 395, "Повний струм:  I = I⁽¹⁾ + I⁽²⁾  (для напруг і струмів, але НЕ для потужності!)", color=C_PURPLE, size=15, bold=True)
    ]
    render(os.path.join(IMG, "circuit-superposition.svg"), W, H, *f)

# ── Фігура 4: Класична проти Квантової Суперпозиції ────────────────────────────
def fig_quantum_vs_classical():
    W, H = 820, 460
    tb1, _, _ = textbox(215, 140, "Додаються безпосередні\nфізичні величини (сили, поля)", size=13, fill="#eef3fd", stroke=C_PRIMARY)
    tb2, _, _ = textbox(215, 360, "Особливості:\n• Вимірювання не змінює стан\n• Означена траєкторія й стан\n• Відсутній зворотний вплив спостерігача", size=12, fill=C_BG_BOX, stroke="#bdc3c7")
    tb3, _, _ = textbox(605, 140, "Додаються вектори станів\n(амплітуди ймовірностей cᵢ ∈ ℂ)", size=13, fill="#f5eeef", stroke=C_PURPLE)
    tb4, _, _ = textbox(605, 360, "Особливості:\n• Вимірювання викликає редукцію (колапс)\n• Квантова інтерференція через 2 Re(c₁* c₂)\n• Руйнується декогеренцією з довкіллям", size=12, fill=C_BG_BOX, stroke="#bdc3c7")

    f = [
        text(W / 2, 25, "Класична проти квантової суперпозиції: що саме додається", size=16, bold=True),
        
        # Ліва панель - Класика
        rect(40, 60, 350, 370, fill="#ffffff", stroke=C_PRIMARY, rx=6),
        text(215, 90, "Класична суперпозиція", color=C_PRIMARY, size=16, bold=True),
        tb1,
        text(215, 190, "Векторне / скалярне поле:", size=13, bold=True),
        text(215, 215, "E = E₁ + E₂", color=C_PRIMARY, size=16, bold=True),
        text(215, 250, "Густина енергії / інтенсивність:", size=13, bold=True),
        text(215, 275, "I ∝ |E₁ + E₂|²", color=C_DARK, size=15, bold=True),
        tb2,

        # Права панель - Квантова
        rect(430, 60, 350, 370, fill="#ffffff", stroke=C_PURPLE, rx=6),
        text(605, 90, "Квантова суперпозиція", color=C_PURPLE, size=16, bold=True),
        tb3,
        text(605, 190, "Вектор стану в Гільбертовому просторі:", size=13, bold=True),
        text(605, 215, "|Ψ⟩ = c₁ |ϕ₁⟩ + c₂ |ϕ₂⟩", color=C_PURPLE, size=16, bold=True),
        text(605, 250, "Імовірність виявлення стану:", size=13, bold=True),
        text(605, 275, "P = |c₁|² + |c₂|² + 2 Re(c₁* c₂)", color=C_SECONDARY, size=15, bold=True),
        tb4
    ]
    render(os.path.join(IMG, "quantum-vs-classical.svg"), W, H, *f)

# ── Фігура 5: Метод функцій Гріна та згортка ───────────────────────────
def fig_green_function_convolution():
    W, H = 820, 440
    tb1, _, _ = textbox(475, 140, "Оператор L\nG(t, t')", size=13, fill="#eef3fd", stroke=C_PRIMARY)
    tb2, _, _ = textbox(410, 365, "Будь-який складний процес виражається через суму (інтеграл) відгуків\nсистеми на елементарні збурення в кожен попередній момент часу", size=12, fill="#ffffff", stroke="#bdc3c7")

    f = [
        text(W / 2, 25, "Метод функцій Гріна: неперервна суперпозиція імпульсних відгуків", size=16, bold=True),
        
        # Вхідний сигнал - розклад на імпульси
        rect(30, 60, 360, 160, fill="#ffffff", stroke="#bdc3c7", rx=6),
        text(210, 80, "1. Декомпозиція вхідного сигналу f(t')", size=13, bold=True),
        line(50, 180, 370, 180, color=C_DARK, sw=1.5), # вісь t'
        line(50, 180, 50, 95, color=C_DARK, sw=1.5),
        # Крива f(t')
        poly([(50,160), (100,140), (160,110), (220,120), (280,150), (350,175)], color=C_PRIMARY, sw=2.0),
        # Стовпчики дельта-імпульсів
        line(160, 180, 160, 110, color=C_SECONDARY, sw=2.5),
        circle(160, 110, 4, fill=C_SECONDARY, stroke="none"),
        text(160, 198, "t'", color=C_SECONDARY, size=11, bold=True),
        text(250, 105, "f(t') dt'", color=C_PRIMARY, size=12),

        # Оператор системи (функція Гріна)
        tb1,
        arrow(390, 140, 420, 140, color=C_DARK, sw=1.8),
        arrow(530, 140, 560, 140, color=C_DARK, sw=1.8),

        # Відгук на один імпульс G(t, t')
        rect(560, 60, 230, 160, fill="#ffffff", stroke="#bdc3c7", rx=6),
        text(675, 80, "2. Відгук на один імпульс", size=13, bold=True),
        line(575, 180, 775, 180, color=C_DARK, sw=1.5),
        line(575, 180, 575, 95, color=C_DARK, sw=1.5),
        # Загасаюча синусоїда від t'
        poly([(575,180), (620,180), (630,120), (650,200), (680,170), (720,185), (760,180)], color=C_GREEN, sw=2.0),
        text(675, 105, "G(t, t') f(t') dt'", color=C_GREEN, size=11, bold=True),

        # Нижній підсумок: інтегрування (неперервна суперпозиція)
        rect(30, 240, 760, 170, fill="#f8f9fa", stroke=C_PURPLE, rx=6),
        text(410, 265, "3. Неперервна суперпозиція (Інтеграл згортки)", color=C_PURPLE, size=15, bold=True),
        text(410, 310, "u(t) = ∫ G(t, t') f(t') dt'", color=C_DARK, size=20, bold=True),
        tb2
    ]
    render(os.path.join(IMG, "green-function-convolution.svg"), W, H, *f)


if __name__ == '__main__':
    fig_linearity_definition()
    fig_field_superposition()
    fig_circuit_superposition()
    fig_quantum_vs_classical()
    fig_green_function_convolution()
    print("Всі 5 фігур успішно згенеровано у ./img/")
