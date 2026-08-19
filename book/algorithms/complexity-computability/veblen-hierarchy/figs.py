# -*- coding: utf-8 -*-
"""Фігури для теми «Ієрархія Веблена» (book/algorithms/complexity-computability/veblen-hierarchy)."""
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

def fig1_veblen_fixed_points():
    """fig1-veblen-fixed-points.svg: Драбина похідних функцій та нерухомих точок."""
    W, H = 880, 520
    frags = []

    frags.append(rect(10, 10, 860, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Драбина похідних функцій Веблена φ_α(β) та їхні нерухомі точки", size=16, bold=True, color="#1e293b"))

    levels = [
        ("φ₀(β) = ω^β", "Базова функція", "Експоненціювання з основою ω (φ₀(0)=1, φ₀(1)=ω, φ₀(ω)=ω^ω)", BLUE_F, BLUE_S),
        ("φ₁(β) = ε_β", "Нерухомі точки φ₀", "Розв'язки рівняння ω^γ = γ (φ₁(0)=ε₀, φ₁(1)=ε₁, φ₁(ω)=ε_ω)", TEAL_F, TEAL_S),
        ("φ₂(β) = ζ_β", "Нерухомі точки φ₁", "Розв'язки рівняння ε_γ = γ (φ₂(0)=ζ₀, де ε_{ζ₀} = ζ₀)", AMBER_F, AMBER_S),
        ("φ₃(β) = η_β", "Нерухомі точки φ₂", "Розв'язки рівняння ζ_γ = γ (φ₃(0)=η₀, де ζ_{η₀} = η₀)", PURPLE_F, PURPLE_S),
        ("φ_ω(0)", "Граничний ординал", "Супремум послідовності φ₁(0), φ₂(0), φ₃(0), ... = sup {ε₀, ζ₀, η₀, ...}", GREEN_F, GREEN_S),
        ("φ_{ω+1}(0)", "Нерухомі точки φ_ω", "Перша спільна нерухома точка для всіх функцій φ_n (n < ω)", GREEN_F, GREEN_S),
    ]

    y_start = 70
    dy = 65

    for idx, (formula, role, desc, fill_c, stroke_c) in enumerate(levels):
        y = y_start + idx * dy

        if idx < len(levels) - 1:
            frags.append(arrow(60, y + 25, 60, y + dy - 5, color="#94a3b8", sw=2))
            frags.append(text(90, y + dy / 2 + 10, "похідна (фікс-точки)", size=10, italic=True, color="#64748b"))

        b_form, _, _ = textbox(190, y, formula, size=12, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_form)

        b_role, _, _ = textbox(360, y, role, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_role)

        b_desc, _, _ = textbox(635, y, desc, size=11, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_desc)

    y_lim = y_start + 6 * dy - 15
    frags.append(line(25, y_lim, 855, y_lim, color=RED_S, sw=1.5, dash="6 4"))
    frags.append(text(440, y_lim + 18, "Межа бінарної функції φ(α, β): перша нерухома точка діагоналі φ(α, 0) = α дає ординал Γ₀", size=11, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig1-veblen-fixed-points.svg"), W, H, *frags)

def fig2_gamma_zero_limit():
    """fig2-gamma-zero-limit.svg: Діагоналізація та ординал Фефермана — Шютте Γ₀."""
    W, H = 880, 480
    frags = []

    frags.append(rect(10, 10, 860, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Процес діагоналізації та граничний перехід до ординалу Γ₀", size=16, bold=True, color="#1e293b"))

    steps = [
        ("α₀ = 0", "Стартова точка", "Нульовий ординал", BLUE_F, BLUE_S),
        ("α₁ = φ(0, 0) = 1", "Крок 1", "Значення функції ω^0 = 1", BLUE_F, BLUE_S),
        ("α₂ = φ(1, 0) = ε₀", "Крок 2", "Найменша нерухома точка експоненти", TEAL_F, TEAL_S),
        ("α₃ = φ(ε₀, 0)", "Крок 3", "Індекс ординала підноситься у власний перший аргумент", AMBER_F, AMBER_S),
        ("α₄ = φ(φ(ε₀, 0), 0)", "Крок 4", "Багаторазове діагональне самозастосування", PURPLE_F, PURPLE_S),
    ]

    x_c = 440
    y_start = 70
    dy = 56

    for idx, (term, label, note, fill_c, stroke_c) in enumerate(steps):
        y = y_start + idx * dy
        b_term, _, _ = textbox(x_c - 160, y, term, size=12, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_term)

        b_lbl, _, _ = textbox(x_c + 20, y, label, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_lbl)

        b_note, _, _ = textbox(x_c + 240, y, note, size=10, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_note)

        if idx < len(steps) - 1:
            frags.append(arrow(x_c - 160, y + 20, x_c - 160, y + dy - 4, color="#94a3b8", sw=2))

    y_dots = y_start + len(steps) * dy - 15
    frags.append(text(x_c - 160, y_dots + 14, "⋮ (трансфінітна ітерація α_{n+1} = φ(α_n, 0))", size=11, bold=True, color="#64748b"))

    y_res = y_dots + 52
    b_gamma, _, _ = textbox(x_c, y_res, "Γ₀ = sup { α₀, α₁, α₂, α₃, ... } = min { α | φ(α, 0) = α }", size=13, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_gamma)

    frags.append(text(440, y_res + 38, "Ординал Фефермана — Шютте: межа предикативного аналізу та систем переписування термів", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig2-gamma-zero-limit.svg"), W, H, *frags)

def fig3_ordinal_notation_tree():
    """fig3-ordinal-notation-tree.svg: Синтаксичне дерево нормальної форми Веблена."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Синтаксичне дерево ординалу в нормальній формі: φ(1, φ(2, 0)) + φ(0, 1)", size=16, bold=True, color="#1e293b"))

    # Root: ADD
    b_root, _, _ = textbox(440, 75, "ORD_ADD (+)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_root)

    # Left Child: φ(1, φ(2, 0))
    # Right Child: φ(0, 1) = ω
    frags.append(arrow(410, 95, 260, 145, color="#64748b", sw=1.5))
    frags.append(arrow(470, 95, 620, 145, color="#64748b", sw=1.5))

    b_left, _, _ = textbox(260, 155, "ORD_VEBLEN φ(γ, β)", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_left)

    b_right, _, _ = textbox(620, 155, "ORD_VEBLEN φ(0, 1) = ω", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_right)

    # Subtrees of left: γ = 1, β = φ(2, 0) = ζ₀
    frags.append(arrow(220, 175, 140, 235, color="#64748b", sw=1.5))
    frags.append(arrow(300, 175, 380, 235, color="#64748b", sw=1.5))

    b_l_gamma, _, _ = textbox(140, 245, "γ = ORD_FINITE(1)", size=11, bold=True, fill="#ffffff", stroke="#64748b")
    frags.append(b_l_gamma)

    b_l_beta, _, _ = textbox(380, 245, "β = ORD_VEBLEN φ(2, 0) [ζ₀]", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_l_beta)

    # Subtrees of β: γ=2, β=0
    frags.append(arrow(340, 265, 300, 325, color="#64748b", sw=1.5))
    frags.append(arrow(420, 265, 460, 325, color="#64748b", sw=1.5))

    b_sub_g, _, _ = textbox(300, 335, "γ = 2", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_sub_g)

    b_sub_b, _, _ = textbox(460, 335, "β = 0", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_sub_b)

    # Subtrees of right: γ=0, β=1
    frags.append(arrow(580, 175, 540, 235, color="#64748b", sw=1.5))
    frags.append(arrow(660, 175, 700, 235, color="#64748b", sw=1.5))

    b_r_gamma, _, _ = textbox(540, 245, "γ = 0", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_r_gamma)

    b_r_beta, _, _ = textbox(700, 245, "β = 1", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_r_beta)

    # Invariant rule box at bottom
    b_inv, _, _ = textbox(440, 405, "Інваріант нормальної форми Веблена: для φ(γ, β) вимагається γ, β < φ(γ, β), а доданки впорядковані за спаданням", size=11, bold=False, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_inv)

    render(os.path.join(IMG, "fig3-ordinal-notation-tree.svg"), W, H, *frags)

def fig4_proof_theoretic_strength():
    """fig4-proof-theoretic-strength.svg: Доказова сила формальних теорій та ординали Веблена."""
    W, H = 880, 500
    frags = []

    frags.append(rect(10, 10, 860, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Шкала доказової сили логічних теорій та їхні теоретико-доказові ординали", size=16, bold=True, color="#1e293b"))

    systems = [
        ("EFA (Elementary Function Arithmetic)", "ω³", "Поліноміальні та експоненціальні алгоритми, елементарні функції", BLUE_F, BLUE_S),
        ("PRA (Primitive Recursive Arithmetic)", "ω^ω", "Усі примітивно-рекурсивні алгоритми, функції без необмеженої рекурсії", BLUE_F, BLUE_S),
        ("PA (Арифметика Пеано) / ACA₀", "ε₀ = φ(1, 0)", "Теорема Ґудстейна, завершуваність стандартних систем переписування", TEAL_F, TEAL_S),
        ("ID₁ (1-індуктивні дефініції)", "φ(ε₀, 0)", "Ітеровані індуктивні визначення, нетривіальні порядки переписування", AMBER_F, AMBER_S),
        ("ATR₀ (Арифметична трансфінітна рекурсія)", "Γ₀ = φ(1, 0, 0)", "Предикативний аналіз, комбінаторика маркованих дерев, складні TRS", PURPLE_F, PURPLE_S),
        ("SVO (Малий ординал Веблена)", "φ(1, 0, 0, 0)", "Межа скінченно-аргументних функцій Веблена, розширена гра в Гідру", RED_F, RED_S),
    ]

    y_start = 70
    dy = 65

    for idx, (theory, ord_val, scope, fill_c, stroke_c) in enumerate(systems):
        y = y_start + idx * dy

        if idx < len(systems) - 1:
            frags.append(arrow(60, y + 25, 60, y + dy - 5, color="#94a3b8", sw=2))

        b_th, _, _ = textbox(190, y, theory, size=11, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b_th)

        b_ord, _, _ = textbox(410, y, ord_val, size=11, bold=True, fill="#ffffff", stroke="#64748b")
        frags.append(b_ord)

        b_sc, _, _ = textbox(655, y, scope, size=10, fill="#f1f5f9", stroke="#94a3b8")
        frags.append(b_sc)

    y_pred = y_start + 4 * dy + 32
    frags.append(line(25, y_pred, 855, y_pred, color=PURPLE_S, sw=1.5, dash="6 4"))
    frags.append(text(730, y_pred - 6, "Межа предикативності (Γ₀)", size=10, bold=True, color=PURPLE_S))

    render(os.path.join(IMG, "fig4-proof-theoretic-strength.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_veblen_fixed_points()
    fig2_gamma_zero_limit()
    fig3_ordinal_notation_tree()
    fig4_proof_theoretic_strength()
    print("All figures generated successfully in", IMG)
