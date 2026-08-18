# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AIR   = "#ffffff"   # Середовище 1 (повітря, менший n)
GLASS = "#eaf2fb"   # Середовище 2 (скло/вода, більший n)

def ang(a):
    return math.radians(a)

def svg_path(d, fill='none', color=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"/>'


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Заломлення за принципом Ферма (порівняння шляхів і мінімум часу)
# ═══════════════════════════════════════════════════════════════════════════
def fig_fermat_refraction():
    W, H = 680, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Принцип Ферма для заломлення світла', 16, INK, 'middle', bold=True))

    py = 200          # межа середовищ
    cx = 310          # Точка P (реальний шлях мінімального часу)

    # Нижня частина (середовище 2)
    f.append(rect(20, py, W - 40, H - py - 50, fill=GLASS, stroke='none', sw=0, rx=0))

    # Межа розділу середовищ
    f.append(line(20, py, W - 40, py, color=INK, sw=2))

    # Точки A (у середовищі 1) і B (у середовищі 2)
    ax, ay = 120, 70
    bx, by = 500, 330

    # Пряма траєкторія (геометрично найкоротший шлях, але НЕ за часом)
    t_straight = (py - ay) / (by - ay)
    x_straight = ax + t_straight * (bx - ax)

    # Альтернативна точка P' (хибний шлях)
    px_alt = 430

    # 1. Пряма лінія (геометрична пряма, але не оптика) - сірий пунктир
    f.append(line(ax, ay, bx, by, color=MUTED, sw=1.5, dash='4,4'))

    # 2. Альтернативний шлях через P' - червонуватий пунктир
    f.append(line(ax, ay, px_alt, py, color=NEG, sw=1.5, dash='5,3'))
    f.append(line(px_alt, py, bx, by, color=NEG, sw=1.5, dash='5,3'))

    # 3. Істинний шлях принципу Ферма через P (зелений/фірмовий)
    f.append(arrow(ax, ay, cx, py, color=POS, sw=2.5))
    f.append(arrow(cx, py, bx, by, color=POS, sw=2.5))

    # Нормаль до межі в точці P
    f.append(line(cx, py - 110, cx, py + 110, color=MUTED, sw=1.2, dash='4,4'))

    # Точки
    f.append(circle(ax, ay, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(bx, by, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(cx, py, 5, fill=INK, stroke=BG, sw=1.5))
    f.append(circle(px_alt, py, 4, fill=NEG, stroke=BG, sw=1.0))

    # Підписи точок
    f.append(text(ax - 12, ay - 8, 'A', 14, INK, 'end', bold=True))
    f.append(text(bx + 12, by + 12, 'B', 14, INK, 'start', bold=True))
    f.append(text(cx - 8, py - 10, 'P (dT/dx = 0)', 12, INK, 'end', bold=True))
    f.append(text(px_alt + 8, py - 10, "P' (T > T_min)", 11, NEG, 'start'))

    # Позначки кутів
    f.append(text(cx - 25, py - 40, 'θ₁', 12, POS, 'middle', bold=True))
    f.append(text(cx + 25, py + 40, 'θ₂', 12, POS, 'middle', bold=True))

    # Назви середовищ
    f.append(text(40, py - 20, 'Середовище 1: n₁ (швидкість v₁ = c/n₁)', 12, INK, 'start'))
    f.append(text(40, py + 25, 'Середовище 2: n₂ > n₁ (швидкість v₂ = c/n₂ < v₁)', 12, INK, 'start'))

    # Легенда шляхів
    f.append(text(cx - 70, ay + 20, 'Закон Снелліуса: n₁ sin θ₁ = n₂ sin θ₂', 12, POS, 'start', bold=True))
    f.append(text(px_alt - 10, py + 40, 'Хибний шлях (більше часу)', 10, NEG, 'start'))
    f.append(text(x_straight + 10, py + 70, 'Геометрична пряма (не оптична)', 10, MUTED, 'start'))

    # Формула внизу
    f.append(text(W / 2, H - 20, 'Оптичний шлях L = n₁·s₁ + n₂·s₂  →  Час T = L / c = min', 13, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'fermat-refraction.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Відбиття: плоске дзеркало (мінімум) та увігнуте (стаціонарність)
# ═══════════════════════════════════════════════════════════════════════════
def fig_fermat_reflection():
    W, H = 680, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Принцип Ферма при відбитті світла', 16, INK, 'middle', bold=True))

    # 1. Ліва панель (x from 20 to 330)
    f.append(rect(20, 50, 305, 270, fill='#fdfdfd', stroke=MUTED, sw=1, rx=6))
    f.append(text(172, 75, 'Плоске дзеркало (Мінімум часу)', 13, INK, 'middle', bold=True))

    m_y = 260
    f.append(line(40, m_y, 300, m_y, color=INK, sw=2))  # Дзеркало
    # Заштриховка дзеркала
    for sx in range(50, 300, 20):
        f.append(line(sx, m_y, sx - 10, m_y + 12, color=MUTED, sw=1))

    fa_x, fa_y = 70, 110
    fb_x, fb_y = 270, 110
    fp_x = 170

    # Справжній шлях відбиття (альфа = бета)
    f.append(arrow(fa_x, fa_y, fp_x, m_y, color=POS, sw=2))
    f.append(arrow(fp_x, m_y, fb_x, fb_y, color=POS, sw=2))

    # Уявне джерело B'
    fb_prime_x, fb_prime_y = 270, m_y + (m_y - fb_y)
    f.append(line(fp_x, m_y, fb_prime_x, fb_prime_y, color=MUTED, sw=1.2, dash='4,4'))
    f.append(line(fa_x, fa_y, fb_prime_x, fb_prime_y, color=NEG, sw=1.2, dash='3,3'))

    f.append(circle(fa_x, fa_y, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(fb_x, fb_y, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(fp_x, m_y, 4, fill=INK, stroke=BG, sw=1))
    f.append(circle(fb_prime_x, fb_prime_y, 4, fill=MUTED, stroke=INK, sw=1))

    f.append(text(fa_x - 10, fa_y, 'A', 12, INK, 'end', bold=True))
    f.append(text(fb_x + 10, fb_y, 'B', 12, INK, 'start', bold=True))
    f.append(text(fp_x, m_y - 8, 'P', 12, INK, 'middle', bold=True))
    f.append(text(fb_prime_x + 10, fb_prime_y, "B'", 11, MUTED, 'start'))

    f.append(text(172, 305, 'Шлях APB найкоротший (пряма AB\')', 11, POS, 'middle'))


    # 2. Права панель (x from 355 to 660)
    f.append(rect(355, 50, 305, 270, fill='#fdfdfd', stroke=MUTED, sw=1, rx=6))
    f.append(text(507, 75, 'Еліптичне дзеркало (Стаціонарність)', 13, INK, 'middle', bold=True))

    svg_d = "M 380,220 Q 507,290 634,220"
    f.append(svg_path(svg_d, fill='none', color=INK, sw=2))

    e_ax, e_ay = 430, 140  # Фокус F1
    e_bx, e_by = 580, 140  # Фокус F2

    p1_x, p1_y = 460, 246
    p2_x, p2_y = 550, 248

    f.append(arrow(e_ax, e_ay, p1_x, p1_y, color=POS, sw=1.8))
    f.append(arrow(p1_x, p1_y, e_bx, e_by, color=POS, sw=1.8))

    f.append(arrow(e_ax, e_ay, p2_x, p2_y, color=FIELD, sw=1.8))
    f.append(arrow(p2_x, p2_y, e_bx, e_by, color=FIELD, sw=1.8))

    f.append(circle(e_ax, e_ay, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(e_bx, e_by, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(p1_x, p1_y, 4, fill=POS, stroke=BG, sw=1))
    f.append(circle(p2_x, p2_y, 4, fill=FIELD, stroke=BG, sw=1))

    f.append(text(e_ax - 10, e_ay, 'F₁', 12, INK, 'end', bold=True))
    f.append(text(e_bx + 10, e_by, 'F₂', 12, INK, 'start', bold=True))
    f.append(text(p1_x - 10, p1_y + 15, 'P₁', 11, POS, 'middle', bold=True))
    f.append(text(p2_x + 10, p2_y + 15, 'P₂', 11, FIELD, 'middle', bold=True))

    f.append(text(507, 305, 'Усі шляхи F₁ → Pᵢ → F₂ займають ОДНАКОВИЙ час', 11, FIELD, 'middle'))

    # Формула внизу
    f.append(text(W / 2, H - 20, 'Варіація оптичного шляху: δS = δ ∫ n ds = 0  (мінімум, максимум або плато)', 13, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'fermat-reflection.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Викривлення променя в градієнтному середовищі (міраж)
# ═══════════════════════════════════════════════════════════════════════════
def fig_fermat_grin():
    W, H = 680, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Поширення світла у градієнтному середовищі (GRIN)', 16, INK, 'middle', bold=True))

    for y_step in range(50, 300, 10):
        alpha = (y_step - 50) / 250.0
        r_c = int(230 + alpha * 25)
        g_c = int(240 + alpha * 10)
        b_c = int(255 - alpha * 35)
        hex_c = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
        f.append(rect(40, y_step, 600, 10, fill=hex_c, stroke='none', sw=0, rx=0))

    f.append(rect(40, 50, 600, 250, fill='none', stroke=MUTED, sw=1.5, rx=0))

    f.append(text(50, 75, 'Холодне повітря (n — велике, v — мала)', 12, INK, 'start', bold=True))
    f.append(text(50, 285, 'Гарячий асфальт (n — мале, v — велика)', 12, NEG, 'start', bold=True))
    f.append(arrow(620, 270, 620, 80, color=FIELD, sw=2))
    f.append(text(610, 175, 'Градієнт ∇n (вгору)', 11, FIELD, 'end', bold=True))

    ax, ay = 80, 110
    bx, by = 550, 110
    cx1, cy1 = 200, 270
    cx2, cx2_y = 430, 270

    curve_path = f"M {ax},{ay} C {cx1},{cy1} {cx2},{cx2_y} {bx},{by}"
    f.append(svg_path(curve_path, fill='none', color=POS, sw=3))

    f.append(line(ax, ay, bx, by, color=MUTED, sw=1.5, dash='4,4'))

    f.append(circle(ax, ay, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(bx, by, 5, fill=POS, stroke=INK, sw=1.5))

    f.append(text(ax - 8, ay - 8, 'Об\'єкт A', 12, INK, 'end', bold=True))
    f.append(text(bx + 8, by - 8, 'Око спостерігача B', 12, INK, 'start', bold=True))

    f.append(line(bx, by, 450, 250, color=NEG, sw=1.5, dash='3,3'))
    f.append(text(460, 260, 'Уявне зображення (міраж)', 11, NEG, 'start'))

    f.append(text(W / 2, H - 20, 'Рівняння променя: d/ds (n · dr/ds) = ∇n  →  Промінь згинається у бік більшого n', 13, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'fermat-grin.svg'), W, H, *f)

if __name__ == '__main__':
    fig_fermat_refraction()
    fig_fermat_reflection()
    fig_fermat_grin()
    print("All figures generated successfully.")
