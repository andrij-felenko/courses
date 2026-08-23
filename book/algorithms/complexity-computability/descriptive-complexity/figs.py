# -*- coding: utf-8 -*-
"""Фігури для теми «Логіка першого порядку та дескриптивна складність» (book/algorithms/complexity-computability/first-order-logic)."""
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

def fig1_descriptive_hierarchy():
    """fig1-descriptive-hierarchy.svg: Відповідність між логічними мовами та класами складності."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Ієрархія дескриптивної складності (Теорема Фагіна, Іммермана, Варді)", size=16, bold=True, color="#1e293b"))

    frags.append(text(210, 70, "Логічний вираз / Формальна мова", size=13, bold=True, color=PURPLE_S))
    frags.append(text(630, 70, "Клас складності обчислень", size=13, bold=True, color=BLUE_S))

    items = [
        ("FO (з порядку входу <)", "AC⁰ (Схеми константної глибини)", BLUE_F, BLUE_S, 100),
        ("FO + DTC (Дет. транзитивне замикання)", "L (Класна пам'ять LOGSPACE)", TEAL_F, TEAL_S, 150),
        ("FO + TC (Транзитивне замикання)", "NL (НЕДЕТ. LOGSPACE)", GREEN_F, GREEN_S, 200),
        ("FO + LFP (Найменша нерухома точка)", "P (Поліноміальний час)", AMBER_F, AMBER_S, 250),
        ("ESO / Σ¹₁ (Екзистенційна 2-го порядку)", "NP (Теорема Фагіна, 1974)", PURPLE_F, PURPLE_S, 300),
        ("FO + PFP (Часткова нерухома точка)", "PSPACE (Поліноміальна пам'ять)", RED_F, RED_S, 350),
        ("SO (Повна логіка 2-го порядку)", "PH (Поліноміальна ієрархія)", GRAY_F, GRAY_S, 400),
    ]

    for logic, comp, f_color, s_color, y in items:
        b1, w1, _ = textbox(210, y, logic, size=12, pad=8, fill=f_color, stroke=s_color, bold=True, min_w=340)
        b2, w2, _ = textbox(630, y, comp, size=12, pad=8, fill=f_color, stroke=s_color, bold=True, min_w=340)
        frags.append(b1)
        frags.append(b2)
        frags.append(arrow(210 + w1/2 + 5, y, 630 - w2/2 - 5, y, color=s_color, sw=2.0))

    frags.append(text(420, 445, "Примітка: Усі еквівалентності для L, NL, P, PSPACE вимагають наявності порядку < на вхідній структурі.", size=11, italic=True, color="#64748b"))

    render(os.path.join(IMG, "fig1-descriptive-hierarchy.svg"), W, H, *frags)

def fig2_gaifman_locality():
    """fig2-gaifman-locality.svg: Принцип локальності Гайфмана у логіці першого порядку."""
    W, H = 800, 420
    frags = []

    frags.append(rect(10, 10, 780, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(400, 34, "Принцип локальності Гайфмана (Gaifman Graph Locality)", size=16, bold=True, color="#1e293b"))

    # Гайфманів окіл
    frags.append(circle(360, 220, 140, fill="#f0f9ff", stroke=BLUE_S, sw=2.0))
    frags.append(text(360, 105, "Окіл B_r(u) радіуса r = 2ᵏ", size=12, bold=True, color=BLUE_S))

    # Центральна вершина u
    frags.append(circle(360, 220, 14, fill=BLUE_S, stroke="#1e3a8a", sw=1.5))
    frags.append(text(360, 224, "u", size=11, bold=True, color="#ffffff"))

    # Інші вершини всередині
    v_in = [(300, 180, "x₁"), (420, 170, "x₂"), (320, 270, "x₃"), (410, 260, "x₄")]
    for vx, vy, lbl in v_in:
        frags.append(circle(vx, vy, 10, fill=TEAL_F, stroke=TEAL_S, sw=1.5))
        frags.append(text(vx, vy+3, lbl, size=9, bold=True, color=TEAL_S))
        frags.append(line(360, 220, vx, vy, color="#94a3b8", sw=1.2, dash="3,3"))

    # Вершини зовні
    v_out = [(120, 140, "v"), (140, 320, "w"), (650, 150, "y"), (640, 300, "z")]
    for vx, vy, lbl in v_out:
        frags.append(circle(vx, vy, 12, fill=RED_F, stroke=RED_S, sw=1.5))
        frags.append(text(vx, vy+4, lbl, size=10, bold=True, color=RED_S))

    # Лінії зовні
    frags.append(line(120, 140, 140, 320, color="#cbd5e1", sw=1.2))
    frags.append(line(650, 150, 640, 300, color="#cbd5e1", sw=1.2))

    frags.append(text(400, 385, "Формула FO кванторної глибини k «бачить» лише радіус 2ᵏ і не здатна оцінити глобальну зв'язність.", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig2-gaifman-locality.svg"), W, H, *frags)

def fig3_ef_game_pebbles():
    """fig3-ef-game-pebbles.svg: Гра Еренфойхта — Фрессе на двох реляційних структурах."""
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Гра Еренфойхта — Фрессе (k-раундова гра з фішками)", size=16, bold=True, color="#1e293b"))

    # Структура A
    frags.append(rect(40, 70, 350, 280, fill="#ffffff", stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(215, 96, "Структура A (Граф C₆)", size=14, bold=True, color=PURPLE_S))
    pts_A = [(140, 170, "a₁"), (215, 140, "a₂"), (290, 170, "a₃"),
             (290, 260, "a₄"), (215, 290, "a₅"), (140, 260, "a₆")]
    for i in range(len(pts_A)):
        x1, y1, _ = pts_A[i]
        x2, y2, _ = pts_A[(i+1)%len(pts_A)]
        frags.append(line(x1, y1, x2, y2, color=PURPLE_S, sw=1.8))
    for x, y, lbl in pts_A:
        frags.append(circle(x, y, 14, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5))
        frags.append(text(x, y+4, lbl, size=11, bold=True, color=PURPLE_S))

    # Фішки на А
    frags.append(textbox(215, 120, "Фішка 1", size=10, fill=AMBER_F, stroke=AMBER_S, pad=4)[0])
    frags.append(textbox(290, 145, "Фішка 2", size=10, fill=AMBER_F, stroke=AMBER_S, pad=4)[0])

    # Структура B
    frags.append(rect(450, 70, 350, 280, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(625, 96, "Структура B (Два графи C₃)", size=14, bold=True, color=GREEN_S))
    pts_B1 = [(500, 170, "b₁"), (560, 130, "b₂"), (560, 210, "b₃")]
    pts_B2 = [(690, 170, "b₄"), (750, 130, "b₅"), (750, 210, "b₆")]
    for pts in [pts_B1, pts_B2]:
        for i in range(len(pts)):
            x1, y1, _ = pts[i]
            x2, y2, _ = pts[(i+1)%len(pts)]
            frags.append(line(x1, y1, x2, y2, color=GREEN_S, sw=1.8))
        for x, y, lbl in pts:
            frags.append(circle(x, y, 14, fill=GREEN_F, stroke=GREEN_S, sw=1.5))
            frags.append(text(x, y+4, lbl, size=11, bold=True, color=GREEN_S))

    # Фішки на B
    frags.append(textbox(500, 145, "Фішка 1'", size=10, fill=AMBER_F, stroke=AMBER_S, pad=4)[0])
    frags.append(textbox(560, 105, "Фішка 2'", size=10, fill=AMBER_F, stroke=AMBER_S, pad=4)[0])

    # Правило
    frags.append(text(420, 380, "Spoiler обирає вершину в A (або B), Duplicator відповідає вершиною в B (або A).", size=12, bold=True, color="#1e293b"))
    frags.append(text(420, 405, "Якщо збережено частковий ізоморфізм aᵢ ↦ bᵢ протягом k раундів, структури нерозрізнювані в FO.", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig3-ef-game-pebbles.svg"), W, H, *frags)

def fig4_lfp_fixedpoint_pipeline():
    """fig4-lfp-fixedpoint-pipeline.svg: Обчислення найменшої нерухомої точки (LFP)."""
    W, H = 820, 360
    frags = []

    frags.append(rect(10, 10, 800, 340, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(410, 34, "Обчислення найменшої нерухомої точки (LFP) для монотонного оператора", size=16, bold=True, color="#1e293b"))

    steps = [
        ("Крок 0", "R⁽⁰⁾ = ∅", "Початковий стан", GRAY_F, GRAY_S, 90),
        ("Крок 1", "R⁽¹⁾ = F(R⁽⁰⁾)", "Ребра довжиною 1", BLUE_F, BLUE_S, 250),
        ("Крок 2", "R⁽²⁾ = F(R⁽¹⁾)", "Шляхи довжиною ≤ 2", TEAL_F, TEAL_S, 410),
        ("Крок k", "R⁽ᵏ⁺¹⁾ = R⁽ᵏ⁾", "Нерухома точка R⁽∞⁾!", AMBER_F, AMBER_S, 570),
        ("Фінал", "Поліном за О(n²)", "Замикання в P", GREEN_F, GREEN_S, 730),
    ]

    for idx, (title_s, formula_s, desc_s, f_col, s_col, cx) in enumerate(steps):
        b, w, h = textbox(cx, 160, f"{title_s}\n{formula_s}\n\n{desc_s}", size=11, pad=10, fill=f_col, stroke=s_col, bold=True, min_w=135)
        frags.append(b)
        if idx < len(steps) - 1:
            next_cx = steps[idx+1][5]
            frags.append(arrow(cx + w/2 + 2, 160, next_cx - 65, 160, color=s_col, sw=1.8))

    frags.append(text(410, 290, "Монотонність забезпечує R⁽⁰⁾ ⊆ R⁽¹⁾ ⊆ R⁽²⁾ ⊆ ... ⊆ R⁽ᵏ⁾ = R⁽∞⁾ (Теорема Тарського — Кнастера).", size=12, bold=True, color="#1e293b"))
    frags.append(text(410, 315, "Кількість ітерацій k ≤ nᵏ, що гарантує обчислення за поліноміальний час у класі P.", size=11, italic=True, color="#475569"))

    render(os.path.join(IMG, "fig4-lfp-fixedpoint-pipeline.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_descriptive_hierarchy()
    fig2_gaifman_locality()
    fig3_ef_game_pebbles()
    fig4_lfp_fixedpoint_pipeline()
    print("Всі 4 SVG фігури успішно згенеровано у теці img/")
