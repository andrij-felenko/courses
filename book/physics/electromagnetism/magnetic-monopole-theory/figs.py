# -*- coding: utf-8 -*-
"""
Генерація SVG-фігур для теми "Магнітний монополь" (magnetic-monopole-theory).
Використовує svgkit з scripts/.
"""

import sys
import os

# Шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def make_maxwell_duality():
    """Фігура 1: Рівняння Максвелла у стандартній та симетричній (дуальній) формі."""
    w, h = 660, 310
    frags = []

    # Заголовок блоків
    b1_title = fitbox(20, 20, 290, 36, "Класичні рівняння (без монополів)", size=13, bold=True, fill="#eef2f7", stroke="#94a3b8")
    b2_title = fitbox(350, 20, 290, 36, "Дуальні рівняння (з монополями)", size=13, bold=True, fill="#eefaf1", stroke=FIELD)
    frags.extend([b1_title, b2_title])

    # Ліва колонка: класичні
    eqs_left = [
        "∇ · E = ρ[e] / ε₀",
        "∇ · B = 0",
        "∇ × E = -∂B / ∂t",
        "∇ × B = μ₀ J[e] + μ₀ ε₀ ∂E / ∂t"
    ]
    
    # Права колонка: дуальні
    eqs_right = [
        "∇ · E = ρ[e] / ε₀",
        "∇ · B = μ₀ ρ[m]",
        "∇ × E = -μ₀ J[m] - ∂B / ∂t",
        "∇ × B = μ₀ J[e] + μ₀ ε₀ ∂E / ∂t"
    ]

    y_start = 75
    row_h = 48

    for i in range(4):
        y = y_start + i * row_h
        # Лівий прямокутник
        box_l = fitbox(20, y, 290, 40, eqs_left[i], size=13, fill="#f8fafc", stroke="#cbd5e1")
        # Правий прямокутник
        box_r = fitbox(350, y, 290, 40, eqs_right[i], size=13, bold=(i in (1, 2)), fill="#f0fdf4" if i in (1,2) else "#f8fafc", stroke=FIELD if i in (1,2) else "#cbd5e1")
        # Стрілка дуальності між ними
        arr = arrow(315, y + 20, 345, y + 20, color=FIELD if i in (1,2) else MUTED, sw=2)
        frags.extend([box_l, box_r, arr])

    # Пояснювальний підпис унизу
    sub = fitbox(20, 272, 620, 28, "Введення ρ[m] та J[m] відновлює повну математичну симетрію поля E та B", size=12, italic=True, fill="#ffffff", stroke="#e2e8f0")
    frags.append(sub)

    render(os.path.join(IMG_DIR, "maxwell-duality.svg"), w, h, *frags)


def make_dirac_string():
    """Фігура 2: Модель струни Дірака (нескінченно тоний соленоїд, що виходить з нескінченності)."""
    w, h = 600, 320
    frags = []

    # Рамка схеми
    frame = rect(10, 10, 580, 295, fill="#ffffff", stroke="#e2e8f0", sw=1)
    frags.append(frame)

    # Точка монополя в центрі
    cx, cy = 300, 150

    # Струна Дірака (вертикальна лінія згори до монополя)
    dirac_str = line(cx, 25, cx, cy, color=POS, sw=3.5, dash="6,4")
    str_lbl = fitbox(330, 60, 230, 36, "Струна Дірака (соленоїд)\nПотік Φ = q[m] усередині", size=12, bold=True, fill="#fdecea", stroke=POS, color=POS)
    frags.extend([dirac_str, str_lbl])

    # Радіальні лінії магнітного поля B, що виходять з монополя
    import math
    angles = [0, 30, 60, 120, 150, 180, 210, 240, 300, 330]
    r_outer = 110
    for a in angles:
        rad = math.radians(a)
        x2 = cx + r_outer * math.cos(rad)
        y2 = cy + r_outer * math.sin(rad)
        b_line = arrow(cx, cy, x2, y2, color=FIELD, sw=1.8)
        frags.append(b_line)

    # Позначка полів B
    b_lbl = fitbox(440, 200, 130, 32, "Поле B = q[m] r̂ / 4πr²", size=11, bold=True, fill="#eafaf1", stroke=FIELD, color=FIELD)
    frags.append(b_lbl)

    # Монополь у центрі
    monopole_dot = circle(cx, cy, 14, fill=POS, stroke="#900c3f", sw=2)
    monopole_txt = text(cx, cy + 4, "qₘ", size=13, color="#ffffff", bold=True)
    frags.extend([monopole_dot, monopole_txt])

    # Зарядове кільце / контур навколо струни (ефект Ааронова-Бома)
    ab_ring = circle(cx, cy - 65, 30, fill="none", stroke=NEG, sw=1.5)
    ab_arr = arrow(cx + 29, cy - 66, cx + 30, cy - 60, color=NEG, sw=1.5)
    ab_lbl = fitbox(40, 60, 220, 36, "Контур електрона q[e]\nФаза Δφ = q[e] q[m] / ℏ = 2πn", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.extend([ab_ring, ab_arr, ab_lbl])

    # Пояснення внизу
    bottom_lbl = fitbox(20, 275, 560, 24, "Струна стає фізично невидимою для квантової частинки, якщо e · q[m] = 2π ℏ n", size=12, italic=True, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(bottom_lbl)

    render(os.path.join(IMG_DIR, "dirac-string.svg"), w, h, *frags)


def make_two_patches():
    """Фігура 3: Дві карти (Північна U_N та Південна U_S) векторного потенціалу на сфері."""
    w, h = 620, 310
    frags = []

    # Рамка
    frags.append(rect(10, 10, 600, 290, fill="#ffffff", stroke="#e2e8f0", sw=1))

    # Сфера Північна (ліворуч)
    cx1, cy1 = 160, 140
    r_sph = 80

    s1 = circle(cx1, cy1, r_sph, fill="#f0f7ff", stroke=NEG, sw=2)
    # Перекриття екватора
    eq1 = line(cx1 - r_sph, cy1, cx1 + r_sph, cy1, color=NEG, sw=1.5, dash="4,3")
    # Сінгулярність внизу (Південний полюс)
    sing1 = line(cx1, cy1 + r_sph, cx1, cy1 + r_sph + 25, color=POS, sw=3, dash="4,3")
    lbl1 = fitbox(40, 235, 240, 44, "Карта U[N] (Північна)\nA[N] регулярний всюди,\nокрім Південного полюса", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.extend([s1, eq1, sing1, lbl1])

    # Сфера Південна (праворуч)
    cx2, cy2 = 460, 140
    s2 = circle(cx2, cy2, r_sph, fill="#fff7f0", stroke="#d97706", sw=2)
    eq2 = line(cx2 - r_sph, cy2, cx2 + r_sph, cy2, color="#d97706", sw=1.5, dash="4,3")
    sing2 = line(cx2, cy2 - r_sph - 25, cx2, cy2 - r_sph, color=POS, sw=3, dash="4,3")
    lbl2 = fitbox(340, 235, 240, 44, "Карта U[S] (Південна)\nA[S] регулярний всюди,\nокрім Північного полюса", size=11, bold=True, fill="#fff7ed", stroke="#d97706", color="#b45309")
    frags.extend([s2, eq2, sing2, lbl2])

    # Зв'язок на екваторі у центрі
    center_arrow = arrow(250, 140, 370, 140, color=FIELD, sw=2)
    gauge_lbl = fitbox(255, 90, 150, 36, "Калібрувальний перехід\nA[S] - A[N] = ∇χ", size=11, bold=True, fill="#eafaf1", stroke=FIELD, color=FIELD)
    frags.extend([center_arrow, gauge_lbl])

    # Нижня стрічка підсумок
    footer = fitbox(20, 275, 580, 22, "Топологічно: розшарування U(1) над сферою S² з інваріантом Черна c₁ = n", size=11, italic=True, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(footer)

    render(os.path.join(IMG_DIR, "two-patches.svg"), w, h, *frags)


def make_charge_monopole_scattering():
    """Фігура 4: Траєкторія електричного заряду у полі магнітного монополя (рух по конусу)."""
    w, h = 600, 300
    frags = []

    frags.append(rect(10, 10, 580, 280, fill="#ffffff", stroke="#e2e8f0", sw=1))

    # Вершина конуса (монополь)
    cx, cy = 180, 150

    # Конус (дві похилі лінії)
    cone1 = line(cx, cy, 480, 50, color=MUTED, sw=1.5, dash="5,4")
    cone2 = line(cx, cy, 480, 250, color=MUTED, sw=1.5, dash="5,4")
    cone_base = circle(480, 150, 100, fill="none", stroke=MUTED, sw=1)
    frags.extend([cone1, cone2, cone_base])

    # Вектор збереженого моменту J уздовж осі конуса
    axis_line = arrow(cx, cy, 540, 150, color=FIELD, sw=2.5)
    j_lbl = fitbox(470, 120, 110, 26, "Момент J", size=12, bold=True, fill="#eafaf1", stroke=FIELD, color=FIELD)
    frags.extend([axis_line, j_lbl])

    # Монополь в apex
    m_dot = circle(cx, cy, 12, fill=POS, stroke="#900c3f", sw=2)
    m_txt = text(cx, cy + 4, "qₘ", size=12, color="#ffffff", bold=True)
    frags.extend([m_dot, m_txt])

    # Спіральна траєкторія заряду q_e на поверхні конуса
    import math
    points = []
    for t in range(0, 100):
        s = t / 100.0
        r = 40 + s * 260
        theta = s * 3.5 * math.pi
        y_off = (r * 0.4) * math.sin(theta)
        x_pos = cx + r * math.cos(0.3)
        y_pos = cy + y_off + (r * 0.3) * math.sin(0.3)
        points.append((x_pos, y_pos))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        t_line = line(x1, y1, x2, y2, color=NEG, sw=2)
        frags.append(t_line)

    # Початковий заряд
    q_start = circle(points[0][0], points[0][1], 7, fill=NEG, stroke="#1d4ed8", sw=1.5)
    q_lbl = fitbox(20, 180, 170, 36, "Заряд q[e] налітає\nтраєкторія є спіраллю", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.extend([q_start, q_lbl])

    # Формула моменту імпульсу
    formula_lbl = fitbox(20, 20, 340, 32, "J = r × p - (μ₀ q[e] q[m] / 4π) r̂ = const", size=11, bold=True, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(formula_lbl)

    render(os.path.join(IMG_DIR, "charge-monopole-scattering.svg"), w, h, *frags)


if __name__ == "__main__":
    make_maxwell_duality()
    make_dirac_string()
    make_two_patches()
    make_charge_monopole_scattering()
    print("Всі SVG-фігури для magnetic-monopole-theory успішно згенеровано.")
