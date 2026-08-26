# -*- coding: utf-8 -*-
"""Фігури до теми «Формула Лармора».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"
DARK   = "#0f172a"
LINK   = "#2563eb"
ORANGE = "#d97706"
WHITE  = "#ffffff"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# Помічник для полігонів
def polygon_svg(*pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)


# Помічник для еліпсів
def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


# ── Фігура 1: Перегин силових ліній (модель Томсона-Перселла) ────────────────
def fig_field_kink():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 25, "Геометрія перегину силових ліній прискореного заряду", size=16, bold=True))

    cx0, cy0 = 230, 220
    v_disp = 45 # зміщення заряду за час t
    cx1 = cx0 + v_disp
    cy1 = cy0

    r_outer = 160 # ct
    dr = 35       # c dt
    r_inner = r_outer - dr # c (t - dt)

    # Зовнішня сфера фронту (ct)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f8fafc" stroke="%s" stroke-width="1.8" stroke-dasharray="6,4"/>' % (cx0, cy0, r_outer, MUTED))
    # Внутрішня сфера фронту (c(t-dt))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eff6ff" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (cx1, cy1, r_inner, LINK))

    # Початкова позиція (t = 0)
    f.append(circle(cx0, cy0, 4, fill=MUTED, stroke=DARK, sw=1))
    f.append(text(cx0 - 24, cy0 + 5, "t = 0", size=11, color=MUTED, bold=True))

    # Поточна позиція заряду
    f.append(circle(cx1, cy1, 7, fill=POS, stroke=DARK, sw=1.5))
    f.append(text(cx1, cy1 + 3.5, "+q", size=9, color=WHITE, bold=True))
    f.append(text(cx1 + 26, cy1 + 5, "t = t₀", size=11, color=POS, bold=True))

    # Вектор прискорення / швидкості
    f.append(arrow(cx0 - 35, cy0 - 145, cx0 + 25, cy0 - 145, color=POS, sw=2.2))
    f.append(text(cx0 - 5, cy0 - 155, "a (прискорення)", size=11, bold=True, color=POS))

    # Силові лінії з перегином під кутами
    angles_deg = [30, 60, 120, 150, 210, 240, 300, 330]
    for deg in angles_deg:
        rad = math.radians(deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Внутрішня частина: від cx1, cy1 до r_inner
        p_in_x = cx1 + r_inner * cos_a
        p_in_y = cy1 - r_inner * sin_a
        f.append(line(cx1, cy1, p_in_x, p_in_y, color=LINK, sw=1.5))

        # Зовнішня частина: від r_outer радіально від cx0, cy0
        p_out_x = cx0 + r_outer * cos_a
        p_out_y = cy0 - r_outer * sin_a
        p_far_x = cx0 + (r_outer + 35) * cos_a
        p_far_y = cy0 - (r_outer + 35) * sin_a
        f.append(line(p_out_x, p_out_y, p_far_x, p_far_y, color=MUTED, sw=1.5))

        # Перемичка в шарі товщиною c*dt (перегин силової лінії)
        f.append(line(p_in_x, p_in_y, p_out_x, p_out_y, color=ORANGE, sw=2.5))

    # Виноска на перегин силової лінії при theta = 60°
    rad60 = math.radians(60)
    kink_x = (cx1 + r_inner * math.cos(rad60) + cx0 + r_outer * math.cos(rad60)) / 2
    kink_y = (cy1 - r_inner * math.sin(rad60) + cy0 - r_outer * math.sin(rad60)) / 2

    f.append(circle(kink_x, kink_y, 5, fill=ORANGE, stroke=DARK, sw=1.2))
    f.append(line(kink_x, kink_y, kink_x + 35, kink_y - 25, color=ORANGE, sw=1.5))

    # Текстова картка з аналітичним розбором праворуч
    card_x = 575

    b1, w1, h1 = textbox(card_x, 110,
                         "1. Геометрія розриву інформації\n"
                         "• Ззовні r > ct: поле центроване у (t=0)\n"
                         "• Всередині r < c(t-Δt): поле зміщене\n"
                         "• Шар товщиною Δr = c Δt несе злам ліній",
                         size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.2)
    f.append(b1)

    b2, w2, h2 = textbox(card_x, 225,
                         "2. Співвідношення компонент поля\n"
                         "• E_⊥ / E_r = (a · t · sin θ) / (c Δt)\n"
                         "• Оскільки t = r/c, маємо E_⊥ / E_r ∝ a·r/c²\n"
                         "• E_r ∝ 1/r²  ⇒  E_⊥ ∝ a · sin θ / (c² · r)",
                         size=11, pad=8, fill="#fef8f0", stroke=ORANGE, sw=1.4)
    f.append(b2)

    b3, w3, h3 = textbox(card_x, 345,
                         "3. Відрив випромінюваної енергії\n"
                         "• Густина потоку Пойнтінга S ∝ E_⊥² ∝ 1/r²\n"
                         "• Повний потік через сферу: ∮ S · dA = const\n"
                         "• Енергія назавжди відривається від заряду!",
                         size=11, pad=8, fill="#f0fdf4", stroke=ACCENT, sw=1.4)
    f.append(b3)

    return render(os.path.join(IMG, "field-kink.svg"), W, H, *f)


# ── Фігура 2: Діаграма спрямованості нерелятивістського випромінювання ───────
def fig_dipole_pattern():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 25, "Діаграма спрямованості та вектори полів випромінювання (sin²θ)", size=16, bold=True))

    # Сцена 1: Кутовий розподіл dP/dOmega
    cx1, cy1 = 205, 205
    f.append(text(cx1, 55, "Кутовий розподіл потужності dP/dΩ", size=13, bold=True, color=DARK))

    # Осі координат
    f.append(line(cx1 - 140, cy1, cx1 + 140, cy1, color="#cbd5e1", sw=1.2))
    f.append(line(cx1, cy1 - 135, cx1, cy1 + 135, color="#cbd5e1", sw=1.2))
    f.append(text(cx1 + 145, cy1 + 4, "x (θ = 90°)", size=11, color=MUTED, anchor="start"))
    f.append(text(cx1 + 5, cy1 - 125, "z (напрям a)", size=11, color=MUTED, anchor="start"))

    # Вектор прискорення a
    f.append(arrow(cx1, cy1 + 25, cx1, cy1 - 45, color=POS, sw=3))
    f.append(circle(cx1, cy1, 5, fill=POS, stroke=DARK, sw=1.2))
    f.append(text(cx1 - 16, cy1 - 25, "a", size=14, bold=True, color=POS))

    # Пелюстки діаграми sin^2(theta)
    pts_left, pts_right = [], []
    for deg in range(-90, 91, 4):
        rad = math.radians(deg)
        r_val = 115 * (math.cos(rad) ** 2)
        x_r = cx1 + r_val * math.cos(rad)
        y_r = cy1 - r_val * math.sin(rad)
        pts_right.append((x_r, y_r))

        x_l = cx1 - r_val * math.cos(rad)
        pts_left.append((x_l, y_r))

    f.append(polygon_svg(*pts_right, fill="#f0fdf4", stroke=ACCENT, sw=2.2))
    f.append(polygon_svg(*pts_left, fill="#f0fdf4", stroke=ACCENT, sw=2.2))

    f.append(text(cx1 + 80, cy1 - 15, "P_max (θ = 90°)", size=11, bold=True, color=ACCENT, anchor="start"))
    f.append(text(cx1 + 12, cy1 - 85, "P = 0 (θ = 0°)", size=11, bold=True, color=LINK, anchor="start"))
    f.append(text(cx1 + 12, cy1 + 85, "P = 0 (θ = 180°)", size=11, bold=True, color=LINK, anchor="start"))

    # Сцена 2: Вектори полів E, B, S у просторі
    cx2, cy2 = 530, 205
    f.append(text(cx2, 55, "Тріада векторів у хвильовій зоні", size=13, bold=True, color=DARK))

    # Промінь r під кутом theta
    th_deg = 50
    th_rad = math.radians(th_deg)
    r_len = 110
    px = cx2 + r_len * math.sin(th_rad)
    py = cy2 - r_len * math.cos(th_rad)

    f.append(arrow(cx2, cy2, px + 25 * math.sin(th_rad), py - 25 * math.cos(th_rad), color=MUTED, sw=1.5))
    f.append(circle(cx2, cy2, 5, fill=POS, stroke=DARK, sw=1.2))
    f.append(arrow(cx2, cy2 + 20, cx2, cy2 - 35, color=POS, sw=2.5))
    f.append(text(cx2 - 14, cy2 - 20, "a", size=12, bold=True, color=POS))

    # Дуга кута theta
    f.append('<path d="M %d %d A 35 35 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>' %
             (cx2, cy2 - 35, cx2 + 35 * math.sin(th_rad), cy2 - 35 * math.cos(th_rad), MUTED))
    f.append(text(cx2 + 14, cy2 - 40, "θ", size=12, bold=True, color=MUTED))

    # Точка вимірювання
    f.append(circle(px, py, 4, fill=DARK, stroke=DARK, sw=1))

    # Вектор E_rad (перпендикулярний до r, у площині (a, r))
    e_len = 50
    e_dx = - e_len * math.cos(th_rad)
    e_dy = - e_len * math.sin(th_rad)
    f.append(arrow(px, py, px + e_dx, py + e_dy, color=POS, sw=2.5))
    f.append(text(px + e_dx - 12, py + e_dy - 6, "E_рад", size=12, bold=True, color=POS))

    # Вектор B_rad (перпендикулярний до площини рисунка)
    b_len = 45
    b_dx = 30
    b_dy = 22
    f.append(arrow(px, py, px + b_dx, py + b_dy, color=ORANGE, sw=2.5))
    f.append(text(px + b_dx + 8, py + b_dy + 12, "B_рад = (1/c) n × E", size=11, bold=True, color=ORANGE))

    # Вектор Пойнтінга S = (1/mu0) E x B (радіально вздовж r)
    s_len = 65
    s_dx = s_len * math.sin(th_rad)
    s_dy = - s_len * math.cos(th_rad)
    f.append(arrow(px, py, px + s_dx, py + s_dy, color=ACCENT, sw=2.8))
    f.append(text(px + s_dx + 10, py + s_dy - 5, "S = (1/μ₀) E × B", size=12, bold=True, color=ACCENT))

    # Інформаційна картка внизу
    b, w, h = textbox(cx2, 335,
                      "Властивості випромінювання Лармора:\n"
                      "• dP/dΩ = (q² a² / 16π² ε₀ c³) · sin²θ\n"
                      "• Повна потужність: P = (q² a²) / (6π ε₀ c³)\n"
                      "• 100% лінійна поляризація в площині прискорення",
                      size=11, pad=8, fill="#f8fafc", stroke=FIELD, sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "dipole-pattern.svg"), W, H, *f)


# ── Фігура 3: Релятивістське стискання (прожекторний ефект) ───────────────────
def fig_relativistic_beaming():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 25, "Релятивістський прожекторний ефект (beaming) випромінювання", size=16, bold=True))

    # Панель 1: Нерелятивістський рух (v << c)
    cx1, cy1 = 200, 190
    f.append(text(cx1, 55, "Нерелятивістський режим (v ≪ c)", size=13, bold=True, color=DARK))

    f.append(line(cx1 - 120, cy1, cx1 + 120, cy1, color="#cbd5e1", sw=1.2))
    f.append(line(cx1, cy1 - 110, cx1, cy1 + 110, color="#cbd5e1", sw=1.2))

    f.append(circle(cx1, cy1, 5, fill=POS, stroke=DARK, sw=1.2))
    f.append(arrow(cx1, cy1, cx1 + 35, cy1, color=LINK, sw=2.2))
    f.append(text(cx1 + 45, cy1 - 10, "v ≪ c", size=11, bold=True, color=LINK))

    # Симетрична вісімка sin^2(theta)
    pts_left1, pts_right1 = [], []
    for deg in range(-90, 91, 5):
        rad = math.radians(deg)
        r_val = 80 * (math.cos(rad) ** 2)
        x_r = cx1 + r_val * math.cos(rad)
        y_r = cy1 - r_val * math.sin(rad)
        pts_right1.append((x_r, y_r))
        x_l = cx1 - r_val * math.cos(rad)
        pts_left1.append((x_l, y_r))

    f.append(polygon_svg(*pts_right1, fill="#f8fafc", stroke=MUTED, sw=1.8))
    f.append(polygon_svg(*pts_left1, fill="#f8fafc", stroke=MUTED, sw=1.8))
    f.append(text(cx1, cy1 + 105, "Симетричний тороїд sin²θ", size=11, color=MUTED))

    # Панель 2: Ультрарелятивістський рух (v ~ c, gamma >> 1)
    cx2, cy2 = 530, 190
    f.append(text(cx2, 55, "Релятивістський режим (γ ≫ 1, v → c)", size=13, bold=True, color=DARK))

    f.append(line(cx2 - 120, cy2, cx2 + 150, cy2, color="#cbd5e1", sw=1.2))
    f.append(line(cx2, cy2 - 110, cx2, cy2 + 110, color="#cbd5e1", sw=1.2))

    f.append(circle(cx2, cy2, 5, fill=POS, stroke=DARK, sw=1.2))
    f.append(arrow(cx2, cy2, cx2 + 80, cy2, color=POS, sw=3))
    f.append(text(cx2 + 90, cy2 - 10, "v ≈ c", size=12, bold=True, color=POS))

    # Сильно витягнута вперед пелюстка за формулою Льєнара
    pts_rel = [(cx2, cy2)]
    for deg in range(-75, 76, 3):
        rad = math.radians(deg)
        # Модельоване стискання кута
        beaming = math.cos(rad)**2 / ((1.0 - 0.85 * math.cos(rad)) ** 4)
        norm_r = min(140.0, 12.0 * beaming)
        xr = cx2 + norm_r * math.cos(rad)
        yr = cy2 - norm_r * math.sin(rad)
        pts_rel.append((xr, yr))
    pts_rel.append((cx2, cy2))

    f.append(polygon_svg(*pts_rel, fill="#fef2f2", stroke=POS, sw=2.2))

    # Конус кута 1/gamma
    cone_ang = 20
    cone_rad = math.radians(cone_ang)
    f.append(line(cx2, cy2, cx2 + 130 * math.cos(cone_rad), cy2 - 130 * math.sin(cone_rad), color=ORANGE, sw=1.4, dash="4,3"))
    f.append(line(cx2, cy2, cx2 + 130 * math.cos(cone_rad), cy2 + 130 * math.sin(cone_rad), color=ORANGE, sw=1.4, dash="4,3"))
    f.append(text(cx2 + 140, cy2 - 45, "Кут розкриву конуса: Δθ ~ 1/γ", size=11, bold=True, color=ORANGE, anchor="start"))

    # Підсумкова плашка внизу
    b, w, h = textbox(W / 2, 335,
                      "Релятивістське підсилення випромінювання Льєнара:\n"
                      "• Енергія фокусується у вузький прожекторний конус у напрямку руху швидкості\n"
                      "• Синхротронне випромінювання пропорційне γ⁴ = (E / mc²)⁴ (катастрофічні втрати для легких електронів)",
                      size=11, pad=8, fill="#f8fafc", stroke=FIELD, sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "relativistic-beaming.svg"), W, H, *f)


# ── Фігура 4: Класичне падіння електрона на ядро у моделі Резерфорда ─────────
def fig_rutherford_collapse():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 25, "Класична криза: радіаційне падіння електрона на ядро в атомі Резерфорда", size=16, bold=True))

    cx, cy = 230, 205

    # Ядро (протон +e)
    f.append(circle(cx, cy, 14, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, cy + 5, "+e", size=13, color=POS, bold=True))
    f.append(text(cx - 24, cy - 22, "Протон (ядро)", size=11, bold=True, color=POS))

    # Спіраль падіння електрона
    pts_spiral = []
    theta_max = 8 * math.pi
    r0 = 135
    for step in range(160):
        th = (step / 160.0) * theta_max
        r_cur = r0 * math.sqrt(max(0.02, 1.0 - (th / theta_max)))
        xs = cx + r_cur * math.cos(th)
        ys = cy - r_cur * math.sin(th)
        pts_spiral.append((xs, ys))

    for i in range(len(pts_spiral) - 1):
        x1, y1 = pts_spiral[i]
        x2, y2 = pts_spiral[i+1]
        f.append(line(x1, y1, x2, y2, color=LINK, sw=1.8))

    # Початкова орбіта (борівський радіус r0)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' % (cx, cy, r0, MUTED))
    f.append(text(cx + 85, cy + r0 - 15, "r₀ ≈ 0.53 Å (t = 0)", size=11, color=MUTED))

    # Електрон на проміжній точці спіралі
    el_idx = 45
    ex, ey = pts_spiral[el_idx]
    f.append(circle(ex, ey, 6, fill="#eaf0fd", stroke=LINK, sw=1.5))
    f.append(text(ex, ey + 3, "−e", size=9, color=LINK, bold=True))

    # Вектор швидкості v та прискорення a
    f.append(arrow(ex, ey, ex + 28, ey + 22, color=DARK, sw=2))
    f.append(text(ex + 34, ey + 28, "v", size=11, bold=True, color=DARK))
    f.append(arrow(ex, ey, ex - 28, ey + 10, color=POS, sw=2))
    f.append(text(ex - 36, ey + 14, "a_ц", size=11, bold=True, color=POS))

    # Випромінювані фотони / хвилі
    for w_ang in [0.8 * math.pi, 1.6 * math.pi, 2.4 * math.pi]:
        wx = cx + 85 * math.cos(w_ang)
        wy = cy - 85 * math.sin(w_ang)
        f.append(arrow(wx, wy, wx + 35 * math.cos(w_ang), wy - 35 * math.sin(w_ang), color=ORANGE, sw=1.8))
        f.append(text(wx + 42 * math.cos(w_ang), wy - 42 * math.sin(w_ang), "hν (P_Лармора)", size=10, bold=True, color=ORANGE))

    # Картки розрахунку праворуч
    card_x = 575

    b1, w1, h1 = textbox(card_x, 105,
                         "1. Механізм класичної катастрофи\n"
                         "• Доцентрове прискорення: a = e² / (4πε₀ m_e r²)\n"
                         "• Випромінювана потужність: P ∝ a² ∝ 1/r⁴\n"
                         "• Повна енергія орбіти: E = −e² / (8πε₀ r)",
                         size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.2)
    f.append(b1)

    b2, w2, h2 = textbox(card_x, 215,
                         "2. Темп стягування орбіти\n"
                         "• dE/dt = −P  ⇒  dr/dt = −e⁴ / (12π² ε₀² m_e² c³ r²)\n"
                         "• Час повного падіння від r₀ = 0.53 Å до r = 0:\n"
                         "  τ = (4π² ε₀² m_e² c³ r₀³) / e⁴ ≈ 1.56 · 10⁻¹¹ с",
                         size=11, pad=8, fill="#fef2f2", stroke=POS, sw=1.4)
    f.append(b2)

    b3, w3, h3 = textbox(card_x, 330,
                         "3. Висновок: народження квантової фізики\n"
                         "• Класична речовина колапсувала б за 16 пікосекунд!\n"
                         "• Стійкість атомів довела непридатність класичної\n"
                         "  електродинаміки для мікросвіту (постулати Бора)",
                         size=11, pad=8, fill="#f0fdf4", stroke=ACCENT, sw=1.4)
    f.append(b3)

    return render(os.path.join(IMG, "rutherford-collapse.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_field_kink()
    p2 = fig_dipole_pattern()
    p3 = fig_relativistic_beaming()
    p4 = fig_rutherford_collapse()
    print("written:")
    for p in (p1, p2, p3, p4):
        print("  ", p)
