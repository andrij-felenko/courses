# -*- coding: utf-8 -*-
"""Фігури до теми «Векторний потенціал».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path_tag(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{dash_attr}/>'

def circle_dash(cx, cy, r, stroke=LINE, sw=1.5, dash=None, fill="none"):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{dash_attr}/>'

# ── Фігура 1: Геометрія векторного потенціалу, струму та індукції ───────────
def fig_vector_potential_geometry():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Геометричний зв'язок струму I, векторного потенціалу A та індукції B", size=15, bold=True))

    # Ліва частина: Круговий струм, векторний потенціал A та поле B
    cx, cy = 240, 230
    rx_loop, ry_loop = 140, 50

    # Задня частина контуру струму (пунктир або тьмяніша лінія)
    f.append(path_tag(f"M {cx-rx_loop} {cy} A {rx_loop} {ry_loop} 0 0 1 {cx+rx_loop} {cy}", stroke=POS, sw=3.5, dash="6,4"))

    # Центральна вісь та вектор індукції B (йде крізь центр вгору)
    f.append(line(cx, cy + 90, cx, cy - 130, color="#94a3b8", sw=1.2, dash="4,4"))
    f.append(arrow(cx, cy + 60, cx, cy - 140, color=FIELD, sw=3.0))
    f.append(text(cx + 25, cy - 125, "B = ∇ × A", size=14, bold=True, color=FIELD))

    # Силові лінії поля B (замкнені петлі навколо контуру струму)
    f.append(path_tag(f"M {cx-40} {cy} C {cx-70} {cy-100}, {cx-170} {cy-100}, {cx-170} {cy} C {cx-170} {cy+90}, {cx-70} {cy+90}, {cx-40} {cy}", stroke=FIELD, sw=1.5, dash="3,3"))
    f.append(arrow(cx - 170, cy + 10, cx - 170, cy - 10, color=FIELD, sw=1.5))

    f.append(path_tag(f"M {cx+40} {cy} C {cx+70} {cy-100}, {cx+170} {cy-100}, {cx+170} {cy} C {cx+170} {cy+90}, {cx+70} {cy+90}, {cx+40} {cy}", stroke=FIELD, sw=1.5, dash="3,3"))
    f.append(arrow(cx + 170, cy + 10, cx + 170, cy - 10, color=FIELD, sw=1.5))

    # Передня частина контуру струму (суцільна товста лінія)
    f.append(path_tag(f"M {cx-rx_loop} {cy} A {rx_loop} {ry_loop} 0 0 0 {cx+rx_loop} {cy}", stroke=POS, sw=3.5))
    # Стрілки струму I
    f.append(arrow(cx - 30, cy + ry_loop, cx + 30, cy + ry_loop, color=POS, sw=3.0))
    b_curr, _, _ = textbox(cx + 90, cy + ry_loop + 15, "Струм I (густина J)", size=11, bold=True, pad=4, fill="#fff5f5", stroke=POS)
    f.append(b_curr)

    # Лінії векторного потенціалу A (циркулюють паралельно до контуру струму)
    rx_a1, ry_a1 = 175, 68
    f.append(path_tag(f"M {cx-rx_a1} {cy} A {rx_a1} {ry_a1} 0 1 0 {cx+rx_a1} {cy}", stroke=NEG, sw=2.0, dash="5,3"))
    f.append(path_tag(f"M {cx+rx_a1} {cy} A {rx_a1} {ry_a1} 0 0 0 {cx-rx_a1} {cy}", stroke=NEG, sw=2.0))
    f.append(arrow(cx - 40, cy + ry_a1, cx + 40, cy + ry_a1, color=NEG, sw=2.2))
    b_a, _, _ = textbox(cx - 100, cy + ry_a1 + 18, "Векторний потенціал A ∥ J", size=11, bold=True, pad=4, fill="#f0f7ff", stroke=NEG)
    f.append(b_a)

    # Права частина: Аналітичний та геометричний зміст
    px = 580
    f.append(rect(410, 50, 335, 320, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(px, 75, "Теорема Стокса для потоку", size=13, bold=True, color=INK))

    b1, _, _ = textbox(px, 120, "Магнітна індукція — ротор потенціалу:\nB = ∇ × A   (бо ∇ · B = 0)", size=11, bold=True, pad=5, fill="#ffffff", stroke=FIELD)
    f.append(b1)

    b2, _, _ = textbox(px, 190, "Магнітний потік крізь поверхню S:\nΦ = ∬_S B · dS = ∮_∂S A · dl", size=11, bold=True, pad=5, fill="#ffffff", stroke=NEG)
    f.append(b2)

    b3, _, _ = textbox(px, 275, "Геометричний принцип:\n• Лінії A співнапрямлені зі струмом J\n• Ротор A створює вихрове поле B\n• Циркуляція A дає повний потік Φ", size=11, bold=False, pad=5, fill="#ffffff", stroke=LINE)
    f.append(b3)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, H - 22, "Векторний потенціал A направлений вздовж струму-джерела, а його ротор утворює індукцію B", size=12, bold=True, pad=5, fill="#eef6ef", stroke=FIELD)
    f.append(b_bot)

    return render(os.path.join(IMG, "fig1-vector-potential-geometry.svg"), W, H, *f)


# ── Фігура 2: Калібрувальна свобода та інваріантність ротора ────────────────
def fig_gauge_freedom():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Калібрувальна свобода: додавання градієнта ∇λ не змінює поле B", size=15, bold=True))

    # Ліва колонка: Чисте соленоїдальне поле A (Кулонівське калібрування)
    f.append(rect(25, 55, 335, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(192, 80, "Кулонівське калібрування (∇ · A = 0)", size=12, bold=True, color=INK))

    # Концентричні кола чистого обертання
    c1x, c1y = 192, 185
    for r_c in [30, 60, 90]:
        f.append(circle(c1x, c1y, r_c, fill="none", stroke=NEG, sw=1.8))
        f.append(arrow(c1x + r_c, c1y - 2, c1x + r_c, c1y + 6, color=NEG, sw=1.8))
        f.append(arrow(c1x - r_c, c1y + 2, c1x - r_c, c1y - 6, color=NEG, sw=1.8))

    # Центральна точка поля B
    f.append(circle(c1x, c1y, 7, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(c1x, c1y - 12, "B = ∇ × A", size=10, bold=True, color=FIELD))

    b_coul, _, _ = textbox(192, 298, "Чисто вихрове поле: ∇ · A = 0\nЛінії A утворюють замкнені кільця", size=10, bold=False, pad=4, fill="#ffffff", stroke=NEG)
    f.append(b_coul)

    # Права колонка: Деформоване калібрувальним градієнтом поле A' = A + ∇λ
    f.append(rect(400, 55, 335, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(567, 80, "Трансформоване поле (A' = A + ∇λ)", size=12, bold=True, color=INK))

    c2x, c2y = 567, 185
    # Лінії градієнта (радіальні пунктирні стрілки назовні)
    for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(ang)
        x1 = c2x + 15 * math.cos(rad)
        y1 = c2y + 15 * math.sin(rad)
        x2 = c2x + 85 * math.cos(rad)
        y2 = c2y + 85 * math.sin(rad)
        f.append(line(x1, y1, x2, y2, color=POS, sw=1.2, dash="3,3"))
        f.append(arrow(x2 - 10 * math.cos(rad), y2 - 10 * math.sin(rad), x2, y2, color=POS, sw=1.2))

    # Спіралеподібні результуючі лінії A' (вихрове + радіальне)
    for r_s in [35, 65, 95]:
        f.append(path_tag(f"M {c2x+r_s} {c2y} C {c2x+r_s} {c2y+r_s*0.9}, {c2x+r_s*0.2} {c2y+r_s*1.2}, {c2x-r_s*0.8} {c2y+r_s*0.8}", stroke="#6366f1", sw=2.0))
        f.append(arrow(c2x - r_s*0.6, c2y + r_s*0.9, c2x - r_s*0.8, c2y + r_s*0.8, color="#6366f1", sw=2.0))

    # Центральна точка поля B'
    f.append(circle(c2x, c2y, 7, fill=FIELD, stroke=INK, sw=1.2))
    f.append(text(c2x, c2y - 12, "B' = ∇ × A' = B", size=10, bold=True, color=FIELD))

    b_trans, _, _ = textbox(567, 298, "Ротор градієнта тотожно нуль: ∇ × ∇λ = 0\nФізичне магнітне поле B залишається незмінним", size=10, bold=False, pad=4, fill="#ffffff", stroke=POS)
    f.append(b_trans)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, H - 20, "Будь-яке безвихрове поле ∇λ можна додати до A без зміни сили Лоренца чи індукції B", size=12, bold=True, pad=5, fill="#f1f5f9", stroke=LINE)
    f.append(b_bot)

    return render(os.path.join(IMG, "fig2-gauge-freedom.svg"), W, H, *f)


# ── Фігура 3: Ефект Ааронова–Бома та фазовий зсув ────────────────────────────
def fig_aharonov_bohm():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Ефект Ааронова–Бома: квантовий фазовий зсув у ділянці, де B = 0", size=15, bold=True))

    # Джерело електронів (ліворуч)
    sx, sy = 60, 210
    f.append(circle(sx, sy, 8, fill=NEG, stroke=INK, sw=1.5))
    b_src, _, _ = textbox(sx, sy - 28, "Джерело e⁻", size=11, bold=True, pad=4, fill="#ffffff", stroke=NEG)
    f.append(b_src)

    # Центральний соленоїд (переріз)
    sol_x, sol_y = 350, 210
    sol_r = 45
    f.append(circle(sol_x, sol_y, sol_r, fill="#fee2e2", stroke=POS, sw=2.5))
    # Магнітне поле всередині соленоїда (напрямлене на читача — кружечки з крапками)
    for dx_s, dy_s in [(-18, -18), (18, -18), (-18, 18), (18, 18), (0, 0)]:
        f.append(circle(sol_x + dx_s, sol_y + dy_s, 4, fill=POS, stroke=POS, sw=1))
        f.append(circle(sol_x + dx_s, sol_y + dy_s, 1.5, fill="#ffffff", stroke="none", sw=0))

    b_sol, _, _ = textbox(sol_x, sol_y + sol_r + 28, "Соленоїд з потоком Φ_B\nВсередині: B ≠ 0\nЗовні: B = 0, але A ≠ 0", size=10, bold=True, pad=4, fill="#fff5f5", stroke=POS)
    f.append(b_sol)

    # Лінії векторного потенціалу навколо соленоїда (циркулюють зовні)
    for r_a in [70, 95, 120]:
        f.append(circle_dash(sol_x, sol_y, r_a, fill="none", stroke="#93c5fd", sw=1.4, dash="4,3"))
        f.append(arrow(sol_x + r_a, sol_y - 2, sol_x + r_a, sol_y + 4, color="#3b82f6", sw=1.4))

    f.append(text(sol_x + 105, sol_y - 85, "A = Φ_B / (2πr)", size=11, bold=True, color="#2563eb"))

    # Траєкторія 1 (верхній рукав)
    f.append(path_tag(f"M {sx} {sy} C 160 80, 500 80, 640 {sy-10}", stroke="#10b981", sw=2.5))
    f.append(arrow(340, 95, 360, 95, color="#10b981", sw=2.5))
    b_tr1, _, _ = textbox(350, 65, "Шлях 1: фаза φ₁ = (q/ℏ) ∫₁ A · dr", size=10, bold=True, pad=4, fill="#ecfdf5", stroke="#10b981")
    f.append(b_tr1)

    # Траєкторія 2 (нижній рукав)
    f.append(path_tag(f"M {sx} {sy} C 160 340, 500 340, 640 {sy+10}", stroke="#8b5cf6", sw=2.5))
    f.append(arrow(340, 325, 360, 325, color="#8b5cf6", sw=2.5))
    b_tr2, _, _ = textbox(350, 355, "Шлях 2: фаза φ₂ = (q/ℏ) ∫₂ A · dr", size=10, bold=True, pad=4, fill="#f5f3ff", stroke="#8b5cf6")
    f.append(b_tr2)

    # Екран детектора (праворуч)
    det_x = 650
    f.append(rect(det_x, 70, 16, 280, fill="#334155", stroke=LINE, sw=1.5, rx=2))
    f.append(text(det_x + 8, 55, "Екран", size=11, bold=True, color=INK))

    # Інтерференційні смуги на екрані (хвильова картина)
    for i in range(-5, 6):
        yy = sy + i * 20
        alpha = math.cos(i * 0.6) ** 2
        f.append(rect(det_x + 20, yy - 5, 45 * alpha, 10, fill=FIELD, stroke="none", sw=0, rx=2))

    b_phase, _, _ = textbox(det_x + 45, sy + 135, "Різниця фаз:\nΔφ = (q/ℏ) ∮ A · dl = (q/ℏ) Φ_B\nЗсув інтерференційних смуг!", size=10, bold=True, pad=5, fill="#fefce8", stroke="#ca8a04")
    f.append(b_phase)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, H - 18, "Незважаючи на відсутність сили Лоренца (B = 0 вздовж шляху), векторний потенціал A безпосередньо впливає на квантову хвилю", size=11, bold=True, pad=5, fill="#eef6ef", stroke=FIELD)
    f.append(b_bot)

    return render(os.path.join(IMG, "fig3-aharonov-bohm.svg"), W, H, *f)


if __name__ == '__main__':
    fig_vector_potential_geometry()
    fig_gauge_freedom()
    fig_aharonov_bohm()
    print("All figures generated successfully.")
