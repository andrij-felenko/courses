# -*- coding: utf-8 -*-
"""Фігури до теми «Енергія системи зарядів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Збирання системи точкових зарядів з нескінченності ──────────────
def fig_discrete_assembly():
    W, H = 680, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Покрокове збирання системи точкових зарядів з нескінченності", size=16, bold=True))

    # Схема розташування чотирьох зарядів у вузлах
    # Координати трьох вже розміщених зарядів
    q1_pos = (150, 110)
    q2_pos = (350, 110)
    q3_pos = (150, 240)
    q4_target = (350, 240)

    # Пунктирні лінії переміщення четвертого заряду з нескінченності
    inf_x, inf_y = 610, 240
    f.append(line(inf_x, inf_y, q4_target[0] + 30, q4_target[1], color=MUTED, sw=1.6, dash="4,4"))
    f.append(arrow(inf_x - 30, inf_y, q4_target[0] + 35, q4_target[1], color=POS, sw=2.0))
    f.append(text(inf_x - 20, inf_y - 12, "переміщення q₄ з ∞", size=12, bold=True, color=POS))

    # Лінії взаємодії між зарядами (кулонівські зв'язки)
    f.append(line(q1_pos[0], q1_pos[1], q2_pos[0], q2_pos[1], color=LINE, sw=1.4, dash="3,3"))
    f.append(line(q1_pos[0], q1_pos[1], q3_pos[0], q3_pos[1], color=LINE, sw=1.4, dash="3,3"))
    f.append(line(q2_pos[0], q2_pos[1], q3_pos[0], q3_pos[1], color=LINE, sw=1.4, dash="3,3"))
    f.append(line(q1_pos[0], q1_pos[1], q4_target[0], q4_target[1], color=LINE, sw=1.4, dash="3,3"))
    f.append(line(q2_pos[0], q2_pos[1], q4_target[0], q4_target[1], color=LINE, sw=1.4, dash="3,3"))
    f.append(line(q3_pos[0], q3_pos[1], q4_target[0], q4_target[1], color=LINE, sw=1.4, dash="3,3"))

    # Позначки відстаней між зарядами
    f.append(text(250, 95, "r₁₂", size=12, color=MUTED))
    f.append(text(130, 175, "r₁₃", size=12, color=MUTED, anchor="end"))
    f.append(text(250, 165, "r₂₃", size=12, color=MUTED))
    f.append(text(250, 255, "r₃₄", size=12, color=MUTED))

    # Кружки зарядів
    # q1 (+q)
    f.append(circle(q1_pos[0], q1_pos[1], 18, fill="#fdecea", stroke=POS, sw=2))
    f.append(plus(q1_pos[0], q1_pos[1], 10))
    f.append(text(q1_pos[0] - 25, q1_pos[1] - 5, "q₁", size=14, bold=True, color=POS, anchor="end"))

    # q2 (+q)
    f.append(circle(q2_pos[0], q2_pos[1], 18, fill="#fdecea", stroke=POS, sw=2))
    f.append(plus(q2_pos[0], q2_pos[1], 10))
    f.append(text(q2_pos[0] + 25, q2_pos[1] - 5, "q₂", size=14, bold=True, color=POS, anchor="start"))

    # q3 (−q)
    f.append(circle(q3_pos[0], q3_pos[1], 18, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(minus(q3_pos[0], q3_pos[1], 10))
    f.append(text(q3_pos[0] - 25, q3_pos[1] + 15, "q₃", size=14, bold=True, color=NEG, anchor="end"))

    # q4 (+q, що переміщується)
    f.append(circle(q4_target[0], q4_target[1], 18, fill="#fff5e6", stroke=POS, sw=2.2))
    f.append(plus(q4_target[0], q4_target[1], 10))
    f.append(text(q4_target[0] + 5, q4_target[1] + 32, "q₄", size=14, bold=True, color=POS))

    # Потенціал φ4 у точці розташування q4
    b1, w1, h1 = textbox(500, 110, "Потенціал у точці 4 від вже наявних зарядів:\nφ₄ = φ₁₄ + φ₂₄ + φ₃₄", size=12, pad=7, fill="#ffffff", stroke=LINE, sw=1.3, bold=True)
    f.append(b1)

    # Робота з внесення четвертого заряду
    b2, w2, h2 = textbox(500, 175, "Робота проти кулонівських сил:\nW₄ = q₄ · φ₄ = ∑ (q₄ q_j / 4πε₀ r_j₄)", size=12, pad=7, fill="#fef9e7", stroke=POS, sw=1.4, bold=True)
    f.append(b2)

    # Підсумкова формула повної енергії системи
    b3, w3, h3 = textbox(W / 2, H - 25, "Повна енергія системи:  W = ½ ∑ᵢ qᵢ φᵢ = ∑ᵢ<ⱼ (qᵢ qⱼ / 4πε₀ rᵢⱼ)", size=13, pad=8, fill="#f4f6f8", stroke=FIELD, sw=1.5, bold=True)
    f.append(b3)

    return render(os.path.join(IMG, "discrete-charge-assembly.svg"), W, H, *f)


# ── Фігура 2: Локалізація енергії в електростатичному полі ────────────────
def fig_field_energy_localization():
    W, H = 680, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Локалізація енергії в об'ємі електростатичного поля", size=16, bold=True))

    # Ліва частина: неперервний розподіл заряду в об'ємі V
    cx1, cy1 = 180, 160
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="110" ry="80" fill="#fdecea" stroke="%s" stroke-width="2"/>' % (cx1, cy1, POS))
    f.append(text(cx1 - 60, cy1 - 45, "об'єм V (заряд ρ)", size=13, bold=True, color=POS))

    # Елемент об'єму dV усередині
    dx, dy = cx1 + 20, cy1 + 10
    f.append(rect(dx - 12, dy - 12, 24, 24, fill="#f7d4d0", stroke=POS, sw=1.5))
    f.append(text(dx, dy + 4, "dV", size=11, bold=True, color=INK))

    # Потенціал φ(r) у цій точці
    f.append(arrow(dx + 12, dy, dx + 65, dy + 25, color=LINE, sw=1.4))
    f.append(text(dx + 72, dy + 30, "заряд dq = ρ dV\nпотенціал φ(r)", size=11, bold=True, color=INK, anchor="start"))

    # Сума за об'ємом
    b1, w1, h1 = textbox(cx1, H - 35, "Формулювання через джерела:\nW = ½ ∫_V ρ(r) φ(r) dV", size=12, pad=6, fill="#ffffff", stroke=POS, sw=1.4, bold=True)
    f.append(b1)

    # Стрілка переходу від джерел до поля
    f.append(arrow(320, 160, 380, 160, color=FIELD, sw=2.5))
    f.append(text(350, 142, "∇·E = ρ/ε₀", size=12, bold=True, color=FIELD))
    f.append(text(350, 180, "E = −∇φ", size=12, bold=True, color=FIELD))

    # Права частина: електростатичне поле E та густина енергії w_e
    cx2, cy2 = 520, 160
    f.append(rect(cx2 - 100, cy2 - 75, 200, 150, fill="#eefaf1", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(cx2, cy2 - 52, "простір з полем E", size=13, bold=True, color=FIELD))

    # Силові лінії поля
    for ly in (cy2 - 25, cy2, cy2 + 25):
        f.append(arrow(cx2 - 75, ly, cx2 + 75, ly, color=FIELD, sw=1.6))

    # Об'ємна густина w_e
    b2, w2, h2 = textbox(cx2, cy2 + 15, "об'ємна густина енергії:\nw_e = ½ ε₀ E²", size=12, pad=6, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True)
    f.append(b2)

    # Формулювання через поле
    b3, w3, h3 = textbox(cx2, H - 35, "Формулювання через поле:\nW = ½ ε₀ ∫_∞ E² dV", size=12, pad=6, fill="#ffffff", stroke=FIELD, sw=1.4, bold=True)
    f.append(b3)

    return render(os.path.join(IMG, "field-energy-localization.svg"), W, H, *f)


# ── Фігура 3: Енергія системи провідників та ємнісна матриця ───────────────
def fig_conductor_capacitance():
    W, H = 680, 330
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Енергія системи з N заряджених провідників", size=16, bold=True))

    # Провідник 1
    f.append('<ellipse cx="150" cy="140" rx="65" ry="45" fill="#fdecea" stroke="%s" stroke-width="2"/>' % POS)
    f.append(text(150, 130, "Провідник 1", size=13, bold=True, color=POS))
    f.append(text(150, 152, "заряд Q₁\nпотенціал V₁", size=11, color=INK))

    # Провідник 2
    f.append(rect(320, 100, 110, 85, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    f.append(text(375, 128, "Провідник 2", size=13, bold=True, color=NEG))
    f.append(text(375, 152, "заряд Q₂\nпотенціал V₂", size=11, color=INK))

    # Провідник N
    f.append('<ellipse cx="580" cy="140" rx="55" ry="55" fill="#fef9e7" stroke="%s" stroke-width="2"/>' % FIELD)
    f.append(text(580, 130, "Провідник N", size=13, bold=True, color=FIELD))
    f.append(text(580, 152, "заряд Q_N\nпотенціал V_N", size=11, color=INK))

    # Взаємні ємності та наводка (пунктир між провідниками)
    f.append(line(215, 140, 320, 140, color=LINE, sw=1.5, dash="4,3"))
    f.append(text(267, 125, "C₁₂", size=13, bold=True, color=LINE))

    f.append(line(430, 140, 525, 140, color=LINE, sw=1.5, dash="4,3"))
    f.append(text(477, 125, "C₂_N", size=13, bold=True, color=LINE))

    # Матричний зв'язок Q = C V та V = P Q
    b1, w1, h1 = textbox(240, 235, "Зв'язок зарядів і потенціалів:\nQᵢ = ∑ₖ Cᵢₖ Vₖ    або    Vᵢ = ∑ₖ Pᵢₖ Qₖ", size=12, pad=7, fill="#ffffff", stroke=LINE, sw=1.3, bold=True)
    f.append(b1)

    b2, w2, h2 = textbox(530, 235, "Теорема взаємності Гріна:\nCᵢₖ = Cₖᵢ ,  Pᵢₖ = Pₖᵢ", size=12, pad=7, fill="#ffffff", stroke=LINE, sw=1.3, bold=True)
    f.append(b2)

    # Загальна формула квадратичної форми енергії
    b3, w3, h3 = textbox(W / 2, H - 25, "Енергія системи провідників:  W = ½ ∑ᵢ Qᵢ Vᵢ = ½ Vᵀ C V = ½ Qᵀ C⁻¹ Q", size=13, pad=8, fill="#f4f6f8", stroke=POS, sw=1.5, bold=True)
    f.append(b3)

    return render(os.path.join(IMG, "conductor-capacitance-energy.svg"), W, H, *f)


# ── Фігура 4: Віртуальні переміщення та пондеромоторна сила ───────────────
def fig_ponderomotive_force():
    W, H = 700, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Віртуальні переміщення та пондеромоторні сили електростатики", size=16, bold=True))

    # Пластини конденсатора зі змінною відстанню x
    x1, x2 = 110, 330
    y_top, y_bot = 80, 190
    plate_w = 14

    # Верхня пластина (нерухома)
    f.append(rect(x1, y_top - plate_w, x2 - x1, plate_w, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append(text(x1 - 15, y_top - 2, "+Q, V₁", size=12, bold=True, color=POS, anchor="end"))

    # Нижня пластина (зміщувана на dx)
    f.append(rect(x1, y_bot, x2 - x1, plate_w, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(x1 - 15, y_bot + plate_w, "−Q, V₂", size=12, bold=True, color=NEG, anchor="end"))

    # Віртуальне зміщення dx пунктиром
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3,3"/>' % (x1, y_bot + 25, x2 - x1, plate_w, MUTED))
    f.append(arrow(x1 + 50, y_bot + plate_w, x1 + 50, y_bot + 25, color=MUTED, sw=1.5))
    f.append(text(x1 + 60, y_bot + 22, "зміщення dx", size=11, color=MUTED))

    # Сила притягання F_x
    f.append(arrow((x1 + x2) / 2, y_bot - 4, (x1 + x2) / 2, y_top + plate_w + 4, color=POS, sw=2.5))
    f.append(text((x1 + x2) / 2 + 12, (y_top + y_bot) / 2, "сила F_x", size=14, bold=True, color=POS, anchor="start"))

    # Відстань x
    f.append(line(x1 - 65, y_top, x1 - 65, y_bot, color=LINE, sw=1.4))
    f.append(line(x1 - 72, y_top, x1 - 58, y_top, color=LINE, sw=1.4))
    f.append(line(x1 - 72, y_bot, x1 - 58, y_bot, color=LINE, sw=1.4))
    f.append(text(x1 - 78, (y_top + y_bot) / 2 + 4, "x", size=14, bold=True, color=INK, anchor="end"))

    # Двома режимами обчислення сили (ізольована система vs джерело напруги)
    b1, w1, h1 = textbox(525, 105, "Режим Q = const (ізольовані пластини):\nF_x = − (∂W / ∂x)_Q\nРобота виконується за рахунок\nзменшення енергії поля W", size=11, pad=7, fill="#ffffff", stroke=POS, sw=1.3, bold=True)
    f.append(b1)

    b2, w2, h2 = textbox(525, 205, "Режим V = const (підключено джерело):\nF_x = + (∂W / ∂x)_V\nДжерело здійснює роботу dW_bat = 2 dW,\nполовина йде на механічну роботу F_x dx", size=11, pad=7, fill="#fef9e7", stroke=FIELD, sw=1.4, bold=True)
    f.append(b2)

    # Підсумкове правило
    b3, w3, h3 = textbox(W / 2, H - 25, "Пондеромоторні сили завжди прагнуть змінити конфігурацію так, щоб збільшити ємність C", size=12, pad=7, fill="#f4f6f8", stroke=LINE, sw=1.4, bold=True)
    f.append(b3)

    return render(os.path.join(IMG, "ponderomotive-force.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_discrete_assembly()
    p2 = fig_field_energy_localization()
    p3 = fig_conductor_capacitance()
    p4 = fig_ponderomotive_force()
    print("written SVG figures:")
    print("  ", p1)
    print("  ", p2)
    print("  ", p3)
    print("  ", p4)
