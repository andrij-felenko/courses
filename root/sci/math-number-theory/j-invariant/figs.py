# -*- coding: utf-8 -*-
"""
Генератор фігур для теми: j-інваріант еліптичної кривої
(book/algorithms/complexity-computability/j-invariant)
"""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ROOT = os.path.dirname(__file__)
IMG = os.path.join(ROOT, "img")
os.makedirs(IMG, exist_ok=True)

def build_fig1():
    """Фігура 1: Модулярна група SL(2, Z) та фундаментальна область j-інваріанта на верхній півплощині"""
    w, h = 800, 440
    out = [
        '<defs>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % NEG,
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % POS,
        '  </marker>',
        '  <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % INK,
        '  </marker>',
        '</defs>',
    ]

    out.append(text(w / 2, 25, "Фундаментальна область 𝔽 модулярної групи SL(2, ℤ) та критичні значення j(τ)", size=15, bold=True))

    # Оси комплексної півплощини H (Im(τ) > 0)
    cx, cy = 300, 370
    out.append(line(30, cy, 570, cy, color=MUTED, sw=1.5))
    out.append(line(cx, 40, cx, 400, color=MUTED, sw=1.5))
    out.append(text(560, cy + 20, "Re(τ)", size=12, bold=True, color=MUTED))
    out.append(text(cx - 25, 55, "Im(τ)", size=12, bold=True, color=MUTED))
    out.append(text(cx - 15, cy + 18, "0", size=12, bold=True, color=MUTED))

    # Масштаб: 1 одиниця = 150 px
    u = 150
    x_left = cx - u / 2    # 225
    x_right = cx + u / 2   # 375

    # Позначки на осі Re
    out.append(line(x_left, cy - 4, x_left, cy + 4, color=MUTED, sw=1.2))
    out.append(line(x_right, cy - 4, x_right, cy + 4, color=MUTED, sw=1.2))
    out.append(text(x_left, cy + 18, "−1/2", size=11, bold=True, color=MUTED))
    out.append(text(x_right, cy + 18, "1/2", size=11, bold=True, color=MUTED))

    y_rho = cy - int(u * 0.866025)  # 370 - 130 = 240
    y_top = 70

    # Зафарбована фундаментальна область F
    path_f = (
        f'<path d="M {x_left} {y_top} L {x_left} {y_rho} '
        f'A {u} {u} 0 0 1 {x_right} {y_rho} '
        f'L {x_right} {y_top} Z" '
        f'fill="#e8f4fc" stroke="{POS}" stroke-width="2" />'
    )
    out.append(path_f)

    # Пунктирне одиничне півколо для контексту
    path_circle = f'<path d="M {cx - u} {cy} A {u} {u} 0 0 1 {cx + u} {cy}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4" />'
    out.append(path_circle)
    out.append(text(cx - u - 15, cy + 18, "−1", size=11, color=MUTED))
    out.append(text(cx + u + 15, cy + 18, "+1", size=11, color=MUTED))

    # Критичні точки на фундаментальній області:
    # 1. Точка i на одиничному колі: Re=0, Im=1 -> (cx, cy - u) = (300, 220)
    y_i = cy - u
    out.append(circle(cx, y_i, 5, fill=POS, stroke=INK, sw=1.5))
    out.append(text(cx + 8, y_i - 10, "τ = i  (j = 1728)", size=11, bold=True, color=POS, anchor="start"))

    # 2. Точка rho = e^(2pi*i/3) = -1/2 + i*sqrt(3)/2 -> (x_left, y_rho) = (225, 240)
    out.append(circle(x_left, y_rho, 5, fill=NEG, stroke=INK, sw=1.5))
    out.append(text(x_left - 10, y_rho - 8, "τ = ρ  (j = 0)", size=11, bold=True, color=NEG, anchor="end"))

    # 3. Точка rho + 1 = 1/2 + i*sqrt(3)/2 -> (x_right, y_rho) = (375, 240)
    out.append(circle(x_right, y_rho, 5, fill=NEG, stroke=INK, sw=1.5))
    out.append(text(x_right + 10, y_rho - 8, "τ = ρ + 1  (j = 0)", size=11, bold=True, color=NEG, anchor="start"))

    # 4. Касп (вістря) при Im(τ) -> +inf
    out.append('<line x1="%d" y1="95" x2="%d" y2="65" stroke="%s" stroke-width="2" marker-end="url(#arrow-dark)" />' % (cx, cx, INK))
    out.append(text(cx + 10, 80, "Касп: τ → i∞  (j → ∞, q → 0)", size=11, bold=True, color=INK, anchor="start"))

    # Підпис всередині фундаментальної області
    out.append(text(cx, 150, "Фундаментальна область 𝔽", size=13, bold=True, color=POS))
    out.append(text(cx, 170, "|τ| ≥ 1,  |Re(τ)| ≤ 1/2", size=11, color=INK))

    # Бічна панель з математичними властивостями праворуч
    tb, wtb, htb = textbox(675, 230,
        "Властивості j(τ):\n"
        "● j(Sτ) = j(−1/τ) = j(τ)\n"
        "● j(Tτ) = j(τ + 1) = j(τ)\n"
        "● Голоморфна в ℍ, простий\n"
        "  полюс у каспі q = 0\n"
        "● Бієкція: ℍ / SL(2,ℤ) ≅ ℂ\n"
        "● Кожен клас ізоморфізму\n"
        "  має рівно одне j ∈ ℂ",
        size=11, pad=10, fill="#fef3c7", stroke="#d97706")
    out.append(tb)

    render(os.path.join(IMG, "jinv-fundamental-domain.svg"), w, h, *out)


def build_fig2():
    """Фігура 2: Граф надсингулярних ізогеній над скінченним полем (Supersingular Isogeny Graph)"""
    w, h = 800, 420
    out = [
        '<defs>',
        '  <marker id="arrow-iso" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % NEG,
        '  </marker>',
        '</defs>',
    ]

    out.append(text(w / 2, 25, "Граф надсингулярних 2-ізогеній Рамануджана 𝒢₂(𝔽_p²): вершини як j-інваріанти", size=15, bold=True))

    # Схема графа ізогеній
    nodes = [
        ("j₀ = 1728", 220, 110, "#fee2e2", POS),
        ("j₁ ∈ 𝔽_p²", 100, 220, "#e8f4fc", NEG),
        ("j₂ ∈ 𝔽_p²", 340, 220, "#e8f4fc", NEG),
        ("j₃ = 0", 220, 330, "#fef3c7", "#d97706"),
        ("j₄ ∈ 𝔽_p²", 100, 340, "#e8f4fc", NEG),
        ("j₅ ∈ 𝔽_p²", 340, 340, "#e8f4fc", NEG),
    ]

    edges = [
        (220, 110, 100, 220),
        (220, 110, 340, 220),
        (100, 220, 220, 330),
        (340, 220, 220, 330),
        (100, 220, 100, 340),
        (340, 220, 340, 340),
        (100, 340, 220, 330),
        (340, 340, 220, 330),
        (100, 340, 340, 340),
    ]

    for x1, y1, x2, y2 in edges:
        out.append(line(x1, y1, x2, y2, color="#94a3b8", sw=2))

    for name, x, y, bg_col, border_col in nodes:
        out.append(circle(x, y, 32, fill=bg_col, stroke=border_col, sw=2))
        out.append(text(x, y + 4, name, size=11, bold=True, color=INK))

    out.append('<path d="M 235 135 Q 290 160 325 195" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4,4" marker-end="url(#arrow-iso)" />' % NEG)
    out.append(text(300, 155, "Φ₂(j, X) = 0", size=10, bold=True, color=NEG))

    tb1, w1, h1 = textbox(595, 130,
        "Структура графа ізогеній Pizer:\n"
        "● Вершини: класи надсингулярних\n"
        "  кривих над 𝔽_p² (за j-інваріантом).\n"
        "● Кількість вершин: ≈ ⌊p / 12⌋ + ε.\n"
        "● Ребра: ℓ-ізогенії (степінь k = ℓ + 1).\n"
        "● Рівняння ребер: Φ_ℓ(j₁, j₂) = 0.",
        size=11, pad=10, fill="#f8fafc", stroke=MUTED)
    out.append(tb1)

    tb2, w2, h2 = textbox(595, 290,
        "Криптографічне значення (CSIDH / SQISign):\n"
        "● Граф Рамануджана: зазор λ₁ ≤ 2√ℓ.\n"
        "● Швидке перемішування (O(log p) кроків).\n"
        "● Задача пошуку шляху між j_A та j_B\n"
        "  є постквантово стійкою (немає BQP).\n"
        "● j-інваріант є публічним ключем.",
        size=11, pad=10, fill="#f0fdf4", stroke=FIELD)
    out.append(tb2)

    render(os.path.join(IMG, "jinv-isogeny-graph.svg"), w, h, *out)


def build_fig3():
    """Фігура 3: Дерево класифікації еліптичних кривих за j-інваріантом та автоморфізми твістів"""
    w, h = 800, 420
    out = []

    out.append(text(w / 2, 25, "Класифікація кривих Вейєрштрасса за j-інваріантом та геометрія твістів", size=15, bold=True))

    tb_root, wr, hr = textbox(235, 75,
        "Еліптична крива E/K:  y² + a₁xy + a₃y = x³ + a₂x² + a₄x + a₆\n"
        "Дискримінант Δ ≠ 0   ⇒   j(E) = c₄³ / Δ",
        size=12, bold=True, pad=10, fill="#e8f4fc", stroke=POS)
    out.append(tb_root)

    out.append(arrow(235, 105, 110, 155, color=LINE, sw=1.8))
    out.append(arrow(235, 105, 235, 155, color=LINE, sw=1.8))
    out.append(arrow(235, 105, 360, 155, color=LINE, sw=1.8))

    tb_b1, _, _ = textbox(110, 205,
        "j = 0  (c₄ = 0, A = 0)\n"
        "y² = x³ + B\n"
        "Aut(E) ≅ ℤ / 6ℤ\n"
        "Твісти: d ∈ K* / (K*)⁶\n"
        "Шестикратний твіст",
        size=11, pad=8, fill="#fef3c7", stroke="#d97706")
    out.append(tb_b1)

    tb_b2, _, _ = textbox(235, 205,
        "j = 1728  (c₆ = 0, B = 0)\n"
        "y² = x³ + Ax\n"
        "Aut(E) ≅ ℤ / 4ℤ\n"
        "Твісти: d ∈ K* / (K*)⁴\n"
        "Чотирикратний твіст",
        size=11, pad=8, fill="#fee2e2", stroke=POS)
    out.append(tb_b2)

    tb_b3, _, _ = textbox(365, 205,
        "Загальний: j ∉ {0, 1728}\n"
        "y² = x³ + Ax + B\n"
        "Aut(E) ≅ ℤ / 2ℤ  (±1)\n"
        "Твісти: d ∈ K* / (K*)²\n"
        "Квадратичний твіст",
        size=11, pad=8, fill="#e8f4fc", stroke=NEG)
    out.append(tb_b3)

    tb_recon, _, _ = textbox(235, 345,
        "Алгоритмічне відновлення кривої за інваріантом j₀ ∈ K:\n"
        "● Якщо j₀ ∉ {0, 1728}: A = 3·j₀·(1728 − j₀),  B = 2·j₀·(1728 − j₀)²  ⇒  j(E) = j₀\n"
        "● Якщо j₀ = 0: y² = x³ + 1;   Якщо j₀ = 1728: y² = x³ + x",
        size=11, pad=10, fill="#f0fdf4", stroke=FIELD)
    out.append(tb_recon)

    tb_thm, _, _ = textbox(620, 230,
        "Головна теорема ізоморфізму:\n\n"
        "1. Над алгебраїчним замиканням K̄:\n"
        "   E₁ ≅ E₂ над K̄   ⟺   j(E₁) = j(E₂)\n\n"
        "2. Над основним полем K:\n"
        "   j(E₁) = j(E₂)   ⟺   E₂ є твістом E₁\n"
        "   (ізоморфні над розширенням K(d¹/ⁿ))\n\n"
        "3. Legendre Form: y² = x(x − 1)(x − λ)\n"
        "   j(λ) = 256 · (λ² − λ + 1)³ / (λ²(λ − 1)²)\n"
        "   Дія групи S₆ над коренями λ дає те саме j.",
        size=11, pad=10, fill="#f8fafc", stroke=MUTED)
    out.append(tb_thm)

    render(os.path.join(IMG, "jinv-weierstrass-classification.svg"), w, h, *out)


def main():
    build_fig1()
    print(f"Згенеровано: jinv-fundamental-domain.svg")
    build_fig2()
    print(f"Згенеровано: jinv-isogeny-graph.svg")
    build_fig3()
    print(f"Згенеровано: jinv-weierstrass-classification.svg")

if __name__ == "__main__":
    main()
