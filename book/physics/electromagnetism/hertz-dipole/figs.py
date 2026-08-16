# -*- coding: utf-8 -*-
"""Фігури до теми «Осцилювальний диполь Герца».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"
DARK   = "#0f172a"
LINK   = "#2563eb"
WHITE  = "#ffffff"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Зони поля диполя Герца ──────────────────────────────────────────
def fig_dipole_zones():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Структура тризонового поля осцилювального диполя", size=16, bold=True))

    cx, cy = 230, 210

    # Концентричні кола зон
    r_near = 60
    r_trans = 120
    r_far = 190

    # Ближня зона
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fdf3e7" stroke="#e67e22" stroke-width="1.5" stroke-dasharray="4,4"/>' % (cx, cy, r_near))
    # Проміжна зона
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fef9e7" stroke="#f1c40f" stroke-width="1.5" stroke-dasharray="5,5"/>' % (cx, cy, r_trans))
    # Дальня зона
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eafaf1" stroke="%s" stroke-width="1.5" stroke-dasharray="6,6"/>' % (cx, cy, r_far, ACCENT))

    # Диполь у центрі
    f.append(line(cx, cy - 25, cx, cy + 25, color=DARK, sw=4))
    f.append(circle(cx, cy - 25, 6, fill=POS, stroke=DARK, sw=1))
    f.append(circle(cx, cy + 25, 6, fill=NEG, stroke=DARK, sw=1))
    f.append(text(cx, cy - 25, "+q", size=10, color=WHITE, bold=True))
    f.append(text(cx, cy + 25, "−q", size=10, color=WHITE, bold=True))
    f.append(text(cx - 28, cy, "dl", size=12, bold=True, color=DARK))

    # Радіальні лінії межа
    f.append(line(cx, cy, cx + r_far + 20, cy, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(cx, cy, cx + r_near * math.cos(math.pi/4), cy - r_near * math.sin(math.pi/4), color="#e67e22", sw=1.2))
    f.append(line(cx, cy, cx + r_trans * math.cos(-math.pi/4), cy - r_trans * math.sin(-math.pi/4), color="#d4ac0d", sw=1.2))

    # Позначки радіусів
    f.append(text(cx + 35, cy - 14, "r ≪ λ/2π", size=11, bold=True, color="#d35400"))
    f.append(text(cx + 90, cy + 18, "r ~ λ/2π", size=11, bold=True, color="#b7950b"))
    f.append(text(cx + 155, cy - 14, "r ≫ λ/2π", size=11, bold=True, color=ACCENT))

    # Картки пояснення зон праворуч
    card_x = 450
    card_w = 285

    # 1. Ближня зона
    b1, w1, h1 = textbox(card_x + card_w/2, 90,
                         "1. Ближня зона (реактивна, kr ≪ 1)\n"
                         "• E ∝ 1/r³,  H ∝ 1/r²\n"
                         "• Зсув фаз між E та H дорівнює 90°\n"
                         "• Реактивна енергія повертається в диполь",
                         size=11, pad=8, fill="#fef5e7", stroke="#e67e22", sw=1.2)
    f.append(b1)

    # 2. Проміжна зона
    b2, w2, h2 = textbox(card_x + card_w/2, 205,
                         "2. Проміжна зона (індукції, kr ~ 1)\n"
                         "• E та H мають порівнянні компоненти\n"
                         "• Відбувається формування хвильового фронту\n"
                         "• Зародження зсуву фаз до 0°",
                         size=11, pad=8, fill="#fefde7", stroke="#f1c40f", sw=1.2)
    f.append(b2)

    # 3. Дальня зона
    b3, w3, h3 = textbox(card_x + card_w/2, 320,
                         "3. Дальня зона (випромінювання, kr ≫ 1)\n"
                         "• E, H ∝ 1/r  (поперечна хвиля TEM)\n"
                         "• Фази E та H збігаються (зсув 0°)\n"
                         "• E/H = η₀ ≈ 377 Ом  (імпеданс вакууму)",
                         size=11, pad=8, fill="#eaefea", stroke=ACCENT, sw=1.2)
    f.append(b3)

    return render(os.path.join(IMG, "dipole-zones.svg"), W, H, *f)


# Помічник для еліпсів
def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


# ── Фігура 2: Відрив силових ліній поля ───────────────────────────────────────
def fig_field_detachment():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Механізм відриву силових ліній електричного поля під час осциляції", size=16, bold=True))

    col_w = 175
    gap = 12
    x0 = 16 + col_w / 2

    phases = [
        ("t = 0 (t₁)", "Максимальний заряд +q, −q\nСилові лінії замкнені на зарядах", 1.0),
        ("t = T/4 (t₂)", "Заряд дорівнює 0, струм max\nЛінії стискаються й петельніють", 0.1),
        ("t = T/2 (t₃)", "Заряд змінює знак на протилежний\nПетлі відриваються у простір", -0.8),
        ("t = 3T/4 (t₄)", "Сформована вільна хвиля\nБіжить від диполя зі швидкістю c", 0.0)
    ]

    for i, (title, desc, q_val) in enumerate(phases):
        cx = x0 + i * (col_w + gap)
        cy = 160

        # Рамка фази
        f.append(rect(cx - col_w/2 + 2, 48, col_w - 4, 210, fill=WHITE, stroke=FIELD, sw=1.2, rx=8))
        f.append(text(cx, 68, title, size=13, bold=True, color=INK))

        # Диполь
        f.append(line(cx, cy - 20, cx, cy + 20, color=DARK, sw=3))
        if abs(q_val) > 0.3:
            top_c = POS if q_val > 0 else NEG
            bot_c = NEG if q_val > 0 else POS
            f.append(circle(cx, cy - 20, 5, fill=top_c, stroke=DARK, sw=1))
            f.append(circle(cx, cy + 20, 5, fill=bot_c, stroke=DARK, sw=1))

        # Електричні силові лінії для кожної фази
        if i == 0: # Під'єднані лінії
            for rx, ry in [(25, 25), (42, 35)]:
                f.append(ellipse_svg(cx, cy, rx, ry, fill="none", stroke=POS, sw=1.4))
        elif i == 1: # Перетяжка
            f.append(ellipse_svg(cx, cy, 22, 18, fill="none", stroke=POS, sw=1.4))
            f.append(ellipse_svg(cx, cy, 48, 38, fill="none", stroke="#e67e22", sw=1.4, dash="4,3"))
        elif i == 2: # Відрив петлі
            f.append(ellipse_svg(cx, cy, 18, 14, fill="none", stroke=NEG, sw=1.4))
            # Відірвані петлі з боків
            f.append(ellipse_svg(cx - 48, cy, 18, 32, fill="none", stroke=ACCENT, sw=1.6))
            f.append(ellipse_svg(cx + 48, cy, 18, 32, fill="none", stroke=ACCENT, sw=1.6))
        elif i == 3: # Віддалені вільні хвилі
            f.append(ellipse_svg(cx, cy, 15, 12, fill="none", stroke=POS, sw=1.2))
            f.append(ellipse_svg(cx - 62, cy, 14, 38, fill="none", stroke=ACCENT, sw=1.6))
            f.append(ellipse_svg(cx + 62, cy, 14, 38, fill="none", stroke=ACCENT, sw=1.6))
            # Стрілки поширення
            f.append(arrow(cx - 40, cy, cx - 72, cy, color=ACCENT, sw=1.4))
            f.append(arrow(cx + 40, cy, cx + 72, cy, color=ACCENT, sw=1.4))

        # Текстовий опис під фазою
        b, w, h = textbox(cx, 305, desc, size=10, pad=5, fill="#f8f9fa", stroke="none")
        f.append(b)

    return render(os.path.join(IMG, "field-detachment.svg"), W, H, *f)


# Помічник для полігонів
def polygon_svg(*pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)


# ── Фігура 3: Діаграма спрямованості ──────────────────────────────────────────
def fig_radiation_pattern():
    W, H = 720, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Діаграма спрямованості випромінювання (sin²θ) та поляризація", size=16, bold=True))

    # Сцена 1: Переріз діаграми (вісімка / тороїд)
    cx1, cy1 = 200, 185
    f.append(text(cx1, 50, "Переріз діаграми випромінювання", size=13, bold=True, color=INK))

    # Осі координат
    f.append(line(cx1 - 130, cy1, cx1 + 130, cy1, color="#cbd5e1", sw=1.2))
    f.append(line(cx1, cy1 - 120, cx1, cy1 + 120, color="#cbd5e1", sw=1.2))
    f.append(text(cx1 + 135, cy1 + 4, "x (θ = 90°)", size=11, color=MUTED, anchor="start"))
    f.append(text(cx1 + 5, cy1 - 110, "z (вісь диполя)", size=11, color=MUTED, anchor="start"))

    # Диполь на осі z
    f.append(line(cx1, cy1 - 18, cx1, cy1 + 18, color=DARK, sw=3.5))
    f.append(circle(cx1, cy1 - 18, 4, fill=POS, stroke=DARK, sw=1))
    f.append(circle(cx1, cy1 + 18, 4, fill=NEG, stroke=DARK, sw=1))

    # Пелюстки sin^2(theta)
    pts_left, pts_right = [], []
    for deg in range(-90, 91, 5):
        rad = math.radians(deg)
        r_val = 105 * (math.cos(rad) ** 2)
        x_r = cx1 + r_val * math.cos(rad)
        y_r = cy1 - r_val * math.sin(rad)
        pts_right.append((x_r, y_r))

        x_l = cx1 - r_val * math.cos(rad)
        pts_left.append((x_l, y_r))

    f.append(polygon_svg(*pts_right, fill="#eefaf1", stroke=ACCENT, sw=2))
    f.append(polygon_svg(*pts_left, fill="#eefaf1", stroke=ACCENT, sw=2))

    # Позначки нуля й максимуму
    f.append(text(cx1 + 80, cy1 - 12, "E_max (θ = 90°)", size=11, bold=True, color=ACCENT, anchor="start"))
    f.append(text(cx1 + 12, cy1 - 70, "E = 0 (θ = 0°)", size=11, bold=True, color=NEG, anchor="start"))

    # Сцена 2: Вектори полів E, H, S у дальній зоні
    cx2, cy2 = 520, 185
    f.append(text(cx2, 50, "Ортогональність векторів у дальній зоні", size=13, bold=True, color=INK))

    # Радіальний промінь r
    f.append(arrow(cx2 - 80, cy2 + 60, cx2 + 100, cy2 - 50, color=MUTED, sw=1.5))
    f.append(text(cx2 + 105, cy2 - 55, "r (напрям хвилі)", size=11, bold=True, color=MUTED, anchor="start"))

    # Точка вимірювання P
    px, py = cx2 + 10, cy2 - 5
    f.append(circle(px, py, 4, fill=DARK, stroke=DARK, sw=1))

    # Вектор E_theta (в площині меридіана)
    f.append(arrow(px, py, px - 35, py - 55, color=POS, sw=2.5))
    f.append(text(px - 40, py - 60, "E_θ", size=13, bold=True, color=POS))

    # Вектор H_phi (перпендикулярно)
    f.append(arrow(px, py, px + 55, py + 30, color="#e67e22", sw=2.5))
    f.append(text(px + 60, py + 35, "H_φ", size=13, bold=True, color="#e67e22"))

    # Вектор Пойнтінга S
    f.append(arrow(px, py, px + 65, py - 36, color=ACCENT, sw=2.5))
    f.append(text(px + 70, py - 38, "S = E × H", size=13, bold=True, color=ACCENT))

    # Пояснення імпедансу
    b, w, h = textbox(cx2, 290,
                      "Взаємні співвідношення у дальній зоні:\n"
                      "• E_θ ⊥ H_φ ⊥ r  (поперечна хвиля)\n"
                      "• |E_θ| / |H_φ| = η₀ ≈ 377 Ом\n"
                      "• Густина потоку енергії |S| = E_θ · H_φ ∝ sin²θ / r²",
                      size=11, pad=8, fill="#f8fafc", stroke=FIELD, sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "radiation-pattern.svg"), W, H, *f)


# ── Фігура 4: Потік Пойнтінга та опір випромінювання ─────────────────────────
def fig_poynting_flux():
    W, H = 700, 330
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Енергетичний баланс та еквівалентний опір випромінювання", size=16, bold=True))

    # Сфера інтегрування потоку
    cx, cy = 210, 175
    f.append(ellipse_svg(cx, cy, 120, 110, fill="#f0fdf4", stroke=ACCENT, sw=1.8, dash="5,4"))
    f.append(ellipse_svg(cx, cy, 120, 35, fill="none", stroke="#a7f3d0", sw=1.2, dash="3,3"))

    # Диполь в центрі сфери
    f.append(line(cx, cy - 16, cx, cy + 16, color=DARK, sw=3))
    f.append(circle(cx, cy - 16, 4, fill=POS, stroke=DARK, sw=1))
    f.append(circle(cx, cy + 16, 4, fill=NEG, stroke=DARK, sw=1))

    # Стрілки Пойнтінга з поверхні сфери
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    for a in angles:
        rad = math.radians(a)
        sin_th = abs(math.cos(rad))
        if sin_th < 0.15:
            continue
        sx = cx + 120 * math.cos(rad)
        sy = cy + 110 * math.sin(rad)
        ex = cx + (120 + 35 * sin_th) * math.cos(rad)
        ey = cy + (110 + 35 * sin_th) * math.sin(rad)
        f.append(arrow(sx, sy, ex, ey, color=ACCENT, sw=2))

    f.append(text(cx, cy - 125, "Сфера радіуса r (дальня зона)", size=11, color=MUTED))
    f.append(text(cx + 145, cy, "Потік S", size=12, bold=True, color=ACCENT, anchor="start"))

    # Еквівалентна схема генератор - опір випромінювання праворуч
    card_x = 510
    f.append(text(card_x, 58, "Еквівалентна електрична схема", size=13, bold=True, color=INK))

    # Контур генератора
    f.append(rect(card_x - 110, 80, 220, 115, fill=WHITE, stroke=FIELD, sw=1.4, rx=8))

    # Джерело струму / напруги
    f.append(circle(card_x - 70, 137, 16, fill="#eff6ff", stroke=LINK, sw=1.5))
    f.append(text(card_x - 70, 137, "~ I₀", size=11, bold=True, color=LINK))

    # Опір випромінювання R_rad
    rx1, ry1 = card_x + 30, 137
    f.append(rect(rx1 - 25, ry1 - 10, 50, 20, fill="#fef2f2", stroke=NEG, sw=1.5))
    f.append(text(rx1, ry1, "R_rad", size=11, bold=True, color=NEG))

    # З'єднання
    f.append(line(card_x - 54, 137, rx1 - 25, 137, color=DARK, sw=1.5))
    f.append(line(rx1 + 25, 137, card_x + 90, 137, color=DARK, sw=1.5))
    f.append(line(card_x + 90, 137, card_x + 90, 175, color=DARK, sw=1.5))
    f.append(line(card_x - 70, 153, card_x - 70, 175, color=DARK, sw=1.5))
    f.append(line(card_x - 70, 175, card_x + 90, 175, color=DARK, sw=1.5))

    # Формула R_rad
    b, w, h = textbox(card_x, 260,
                      "Опір випромінювання короткого диполя:\n"
                      "R_rad = 80 π² (dl / λ)²  [Ом]\n\n"
                      "Випромінювана потужність:\n"
                      "P_rad = ½ · I₀² · R_rad  [Ват]",
                      size=11, pad=8, fill="#fafafa", stroke=FIELD, sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "poynting-flux.svg"), W, H, *f)


# ── Фігура 5: Хронологія розвитку теорії випромінювання ───────────────────────
def fig_history_timeline():
    W, H = 740, 240
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Еволюція теорії випромінювання та модель диполя", size=16, bold=True))

    # Головна лінія часу
    y_line = 120
    f.append(line(40, y_line, W - 40, y_line, color=MUTED, sw=2.5))

    events = [
        (80, "1865", "Максвелл", "Передбачення EM-хвиль у теорії", POS),
        (250, "1867", "Лоренц", "Запізнілі потенціали A(r, t)", LINK),
        (430, "1883", "Фіцджеральд", "Ідея випромінювання контуру", "#e67e22"),
        (630, "1888", "Герц", "Модель диполя та відрив ліній", ACCENT)
    ]

    for x, year, author, desc, color in events:
        # Точка на лінії
        f.append(circle(x, y_line, 8, fill=WHITE, stroke=color, sw=2.5))
        f.append(circle(x, y_line, 4, fill=color, stroke=color, sw=1))

        # Написи вище й нижче
        f.append(text(x, y_line - 24, year, size=14, bold=True, color=INK))
        f.append(text(x, y_line - 8, author, size=12, bold=True, color=color))

        # Картка опису під лінією
        b, w, h = textbox(x, y_line + 58, desc, size=10, pad=6, fill="#fafafa", stroke=FIELD, sw=1.2)
        f.append(b)

    return render(os.path.join(IMG, "dipole-history-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_dipole_zones()
    p2 = fig_field_detachment()
    p3 = fig_radiation_pattern()
    p4 = fig_poynting_flux()
    p5 = fig_history_timeline()
    print("written:")
    for p in (p1, p2, p3, p4, p5):
        print("  ", p)
