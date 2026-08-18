# -*- coding: utf-8 -*-
"""Фігури до теми «Вихрові струми».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Механізм вихрових струмів ────────────────────────────────────────
def fig_eddy_current_mechanism():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Фізичний механізм виникнення вихрових струмів Фуко", size=16, bold=True, color=INK))

    # Ліва панель: фізична схема провідника
    f.append(rect(20, 50, 430, 320, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(235, 75, "Індукування замкнених вихрових контурів", size=13, bold=True, color=INK))

    # Масивна металева пластина
    f.append(rect(60, 150, 350, 160, fill="#e2e8f0", stroke="#64748b", sw=2, rx=6))

    # Зовнішнє змінне магнітне поле B_ext(t) (x=80, 235, 390)
    for bx in [80, 235, 390]:
        f.append(arrow(bx, 88, bx, 142, color=FIELD, sw=2.5))
        f.append(arrow(bx, 318, bx, 358, color=FIELD, sw=2.5))
    f.append(text(235, 108, "Змінне магнітне поле B_ext(t) (dB/dt > 0)", size=11, bold=True, color=FIELD))

    # Вихрові контури струму у провіднику (концентричні еліпси)
    f.append(ellipse(235, 235, 110, 40, fill="none", stroke=POS, sw=2.5))
    f.append(ellipse(235, 235, 60, 22, fill="none", stroke=POS, sw=2.0))

    # Стрілки напрямку струму за правилом Ленца
    f.append(arrow(330, 230, 330, 220, color=POS, sw=2.5))
    f.append(arrow(140, 240, 140, 250, color=POS, sw=2.5))
    f.append(text(235, 222, "Густина струму j = σ · E", size=11, bold=True, color=POS))
    f.append(text(235, 255, "Вихрові струми (струми Фуко)", size=11, bold=True, color=POS))
    f.append(text(235, 295, "Масивний провідник (питома провідність σ)", size=11, bold=True, color="#334155"))

    # Реакційне магнітне поле B_ind (праворуч від центру)
    f.append(arrow(300, 230, 300, 138, color=NEG, sw=2.2))
    f.append(text(308, 148, "B_ind (Ленц)", size=11, bold=True, color=NEG, anchor="start"))

    # Права панель: фізичні закони та рівняння
    f.append(rect(465, 50, 295, 320, fill="#f1f5f9", stroke=BORDER, rx=8))
    f.append(text(612, 75, "Ланцюжок причинно-наслідкового зв'язку", size=13, bold=True, color=INK))

    steps = [
        ("1. Зміна магнітного потоку", "dΦ/dt = ∫ (∂B/∂t) · dA ≠ 0", FIELD),
        ("2. Вихрове електричне поле", "∇ × E = -∂B/∂t  (Закон Фарадея)", NEG),
        ("3. Замкнені вихрові струми", "j = σ · E  (Закон Ома)", POS),
        ("4. Протидія та гальмування", "B_ind протидіє dB/dt  (Закон Ленца)", "#7c3aed"),
        ("5. Джоулів нагрів об'єму", "p = j² / σ  (Джоулеві втрати)", "#b91c1c")
    ]

    sy = 100
    for idx, (head_t, eq_t, col) in enumerate(steps):
        y0 = sy + idx * 52
        f.append(rect(480, y0, 265, 44, fill="#ffffff", stroke=col, sw=1.5, rx=5))
        f.append(text(490, y0 + 17, head_t, size=11, bold=True, color=col, anchor="start"))
        f.append(text(490, y0 + 34, eq_t, size=11, bold=False, color=INK, anchor="start"))

    f.append(text(W / 2, H - 15, "Зміна магнітного поля породжує вихрове електричне поле, що збуджує замкнені струми Фуко", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'eddy-current-mechanism.svg'), W, H, "\n".join(f))

# ── Фігура 2: Скін-ефект та глибина проникнення ───────────────────────────────
def fig_skin_effect_depth():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 28, "Скін-ефект та згасання густини вихрових струмів по глибині провідника", size=16, bold=True, color=INK))

    # Ліва панель: графік експоненційного спаду j(z)
    f.append(rect(20, 50, 440, 330, fill="#ffffff", stroke=BORDER, rx=8))
    f.append(text(240, 75, "Розподіл густини струму j(z) = j₀ · e^(-z/δ)", size=13, bold=True, color=INK))

    ox, oy = 70, 320
    gw, gh = 360, 220

    # Осі координат
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.5))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 10, oy, color=INK, sw=1.5))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 10, color=INK, sw=1.5))
    f.append(text(ox + gw, oy + 22, "Глибина z", size=12, bold=True, color=INK))
    f.append(text(ox - 15, oy - gh - 5, "j(z) / j₀", size=12, bold=True, color=INK))

    # Засічки та сітка
    delta_px = 90
    for n in range(1, 4):
        zx = ox + n * delta_px
        f.append(line(zx, oy, zx, oy - gh, color="#e2e8f0", sw=1.0, dash="3,3"))
        f.append(line(zx, oy - 4, zx, oy + 4, color=INK, sw=1.5))
        lbl = f"{n}δ" if n > 1 else "δ"
        f.append(text(zx, oy + 18, lbl, size=12, bold=True, color=NEG))

    # Засічки по y (1.0, 0.368)
    f.append(line(ox - 4, oy - gh + 20, ox + 4, oy - gh + 20, color=INK, sw=1.5))
    f.append(text(ox - 10, oy - gh + 24, "1.0", size=11, bold=True, color=INK, anchor="end"))

    y_delta = oy - (gh - 20) * 0.368
    f.append(line(ox - 4, y_delta, ox + gw, y_delta, color="#cbd5e1", sw=1.0, dash="2,2"))
    f.append(text(ox - 10, y_delta + 4, "0.368", size=11, bold=True, color=POS, anchor="end"))

    # Крива згасання j(z) = j0 * exp(-z/delta)
    pts = []
    for px in range(0, int(gw) - 30, 4):
        z_val = px / delta_px
        val = math.exp(-z_val)
        py = oy - (gh - 20) * val
        pts.append((ox + px, py))

    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    f.append(path_svg(path_d, fill="none", stroke=POS, sw=2.5))

    # Точка при z = delta
    zx_d = ox + delta_px
    f.append(circle(zx_d, y_delta, 5, fill=POS, stroke="none"))
    f.append(text(zx_d + 12, y_delta - 12, "j(δ) = j₀ / e ≈ 36.8%", size=11, bold=True, color=POS, anchor="start"))

    # Права панель: формула та порівняльні параметри
    f.append(rect(475, 50, 285, 330, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(617, 75, "Формула скін-шару δ", size=13, bold=True, color=INK))

    # Рамка з формулою
    f.append(rect(490, 95, 255, 60, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(617, 120, "δ = √( 2 / (ω · μ · σ) )", size=14, bold=True, color=NEG))
    f.append(text(617, 142, "ω = 2πf,  μ = μ₀ · μ_r", size=11, color="#334155"))

    # Таблиця скін-шару для міді та сталі
    f.append(text(617, 180, "Глибина скін-шару δ для матеріалів:", size=11, bold=True, color=INK))

    table_data = [
        ("Частота f", "Мідь (Cu)", "Сталь (Si-Fe)"),
        ("50 Гц", "9.3 мм", "0.30 мм"),
        ("1 кГц", "2.1 мм", "0.07 мм"),
        ("100 кГц", "0.21 мм", "0.007 мм"),
        ("1 МГц", "0.066 мм", "0.002 мм")
    ]

    ty0 = 195
    for r_idx, row in enumerate(table_data):
        y_r = ty0 + r_idx * 28
        bg_r = "#e2e8f0" if r_idx == 0 else ("#ffffff" if r_idx % 2 == 1 else "#f1f5f9")
        f.append(rect(490, y_r, 255, 26, fill=bg_r, stroke="#e2e8f0", sw=1.0, rx=3))
        bld = (r_idx == 0)
        c_col = INK if r_idx == 0 else "#1e293b"
        f.append(text(530, y_r + 17, row[0], size=10, bold=bld, color=c_col))
        f.append(text(615, y_r + 17, row[1], size=10, bold=bld, color=NEG if not bld else c_col))
        f.append(text(700, y_r + 17, row[2], size=10, bold=bld, color=POS if not bld else c_col))

    f.append(text(617, 355, "Висока частота та провідність", size=10, bold=True, color=MUTED))
    f.append(text(617, 368, "концентрують струм біля поверхні", size=10, bold=True, color=MUTED))

    f.append(text(W / 2, H - 15, "Густина струму спадає в e разів на глибині δ, виштовхуючи поле на поверхню провідника", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'skin-effect-depth.svg'), W, H, "\n".join(f))

# ── Фігура 3: Шихтоване виконання сердечника ──────────────────────────────────
def fig_eddy_loss_lamination():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Придушення вихрових струмів шляхом шихтування сердечника", size=16, bold=True, color=INK))

    # Ліва панель: Суцільний сердечник
    f.append(rect(20, 50, 360, 320, fill="#fff5f5", stroke="#fca5a5", rx=8))
    f.append(text(200, 75, "А: Суцільний металевий сердечник", size=13, bold=True, color="#b91c1c"))

    # Блок сердечника
    f.append(rect(60, 105, 280, 190, fill="#e2e8f0", stroke="#64748b", sw=2, rx=6))

    # Великі вихрові контури
    f.append(ellipse(200, 200, 110, 70, fill="none", stroke=POS, sw=3.0))
    f.append(ellipse(200, 200, 60, 35, fill="none", stroke=POS, sw=2.0))
    f.append(arrow(300, 190, 300, 175, color=POS, sw=2.5))
    f.append(arrow(100, 210, 100, 225, color=POS, sw=2.5))

    f.append(text(200, 195, "Великі вихрові контури", size=11, bold=True, color=POS))
    f.append(text(200, 212, "Ширина контуру D", size=11, color=INK))

    # Втрати
    f.append(rect(80, 305, 240, 50, fill="#ffffff", stroke="#fca5a5", rx=5))
    f.append(text(200, 324, "Вихрові втрати: P_e ∝ D²", size=12, bold=True, color="#b91c1c"))
    f.append(text(200, 342, "Сильний джоулів нагрів і низький ККД", size=10, color="#7f1d1d"))

    # Права панель: Шихтований сердечник
    f.append(rect(400, 50, 360, 320, fill="#f0fdf4", stroke="#86efac", rx=8))
    f.append(text(580, 75, "Б: Шихтований сердечник (N пластин)", size=13, bold=True, color="#15803d"))

    # Блок з N пластин з ізоляцією
    num_plates = 6
    pw = 280 / num_plates
    for i in range(num_plates):
        px = 440 + i * pw
        # Пластина
        f.append(rect(px, 105, pw - 3, 190, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=2))
        # Ізоляційний шар (лак/оксид)
        if i < num_plates - 1:
            f.append(rect(px + pw - 3, 105, 3, 190, fill="#f59e0b", stroke="none"))
        # Маленькі вихрові контури в кожній пластині
        cx = px + (pw - 3) / 2
        f.append(ellipse(cx, 200, pw / 2 - 3, 40, fill="none", stroke=FIELD, sw=1.5))
        f.append(arrow(cx + pw / 2 - 4, 195, cx + pw / 2 - 4, 185, color=FIELD, sw=1.2))

    f.append(text(580, 130, "Товщина пластини d = D / N", size=11, bold=True, color=FIELD))
    f.append(text(580, 145, "Ізоляційний лак (жовтий)", size=10, color="#d97706"))

    # Втрати
    f.append(rect(460, 305, 240, 50, fill="#ffffff", stroke="#86efac", rx=5))
    f.append(text(580, 324, "Втрати зменшено у N² разів!", size=12, bold=True, color="#15803d"))
    f.append(text(580, 342, "P_e ∝ d² = (D / N)² = P_0 / N²", size=11, bold=True, color=FIELD))

    f.append(text(W / 2, H - 15, "Розбиття об'єму тонкими ізольованими пластинами дрібнить вихрові контури та різко знижує втрати", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'eddy-loss-lamination.svg'), W, H, "\n".join(f))

# ── Фігура 4: Практичні застосування вихрових струмів ─────────────────────────
def fig_eddy_current_applications():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Практичне використання вихрових струмів у техніці", size=16, bold=True, color=INK))

    pw = 235
    ph = 310
    y0 = 55

    # Панель 1: Індукційне гальмування
    f.append(rect(20, y0, pw, ph, fill="#eff6ff", stroke=BORDER, rx=8))
    f.append(text(137, y0 + 22, "1. Індукційне гальмо", size=13, bold=True, color=NEG))

    # Диск що обертається
    f.append(circle(137, y0 + 130, 65, fill="#cbd5e1", stroke="#475569", sw=2))
    f.append(circle(137, y0 + 130, 8, fill=INK, stroke="none"))
    # Стрілка обертання
    f.append(path_svg("M 137,70 A 60,60 0 0,1 190,115", fill="none", stroke=INK, sw=2, dash=None))
    f.append(arrow(185, 110, 192, 120, color=INK, sw=2))
    f.append(text(137, y0 + 55, "Обертання ω", size=10, bold=True, color=INK))

    # Полюси магніту
    f.append(rect(160, y0 + 110, 40, 40, fill="#fca5a5", stroke=POS, sw=1.5, rx=3))
    f.append(text(180, y0 + 134, "N / S", size=11, bold=True, color=POS))

    # Гальмівна сила F_drag
    f.append(arrow(180, y0 + 160, 140, y0 + 175, color="#b91c1c", sw=2.5))
    f.append(text(160, y0 + 190, "Сила гальмування F", size=10, bold=True, color="#b91c1c"))

    f.append(text(137, y0 + 235, "Безконтактне сповільнення", size=11, bold=True, color=INK))
    f.append(text(137, y5 := y0 + 252, "поїздів, звалок, вагів", size=10, color=MUTED))
    f.append(text(137, y5 + 16, "Кінетична енергія → тепло", size=10, color=MUTED))

    # Панель 2: Індукційний нагрів
    f.append(rect(272, y0, pw, ph, fill="#fff7ed", stroke=BORDER, rx=8))
    f.append(text(389, y0 + 22, "2. Індукційний нагрів", size=13, bold=True, color="#c2410c"))

    # Металева деталь в центрі
    f.append(rect(354, y0 + 85, 70, 95, fill="#94a3b8", stroke="#334155", sw=2, rx=4))
    # Скін-шар гарячого нагріву
    f.append(rect(354, y0 + 85, 70, 95, fill="none", stroke="#ef4444", sw=4, rx=4))
    f.append(text(389, y0 + 135, "Скін-шар δ", size=10, bold=True, color="#ffffff"))
    f.append(text(389, y0 + 150, "(Гарячий)", size=10, bold=True, color="#ffffff"))

    # Витки індуктора (ВЧ котушка)
    for cy in [y0 + 95, y0 + 120, y0 + 145, y0 + 170]:
        f.append(ellipse(335, cy, 12, 8, fill="#f59e0b", stroke="#b45309", sw=1.5))
        f.append(ellipse(443, cy, 12, 8, fill="#f59e0b", stroke="#b45309", sw=1.5))
    f.append(text(389, y0 + 72, "ВЧ індуктор (10–400 кГц)", size=10, bold=True, color="#b45309"))

    f.append(text(389, y0 + 235, "Поверхневе гартування,", size=11, bold=True, color=INK))
    f.append(text(389, y6 := y0 + 252, "плавлення металів у вакуумі,", size=10, color=MUTED))
    f.append(text(389, y6 + 16, "побутові індукційні плити", size=10, color=MUTED))

    # Панель 3: Вихрострумова дефектоскопія (NDT)
    f.append(rect(525, y0, pw, ph, fill="#faf5ff", stroke=BORDER, rx=8))
    f.append(text(642, y0 + 22, "3. Дефектоскопія (NDT)", size=13, bold=True, color="#7e22ce"))

    # Металева деталь з тріщиною
    f.append(rect(550, y0 + 130, 185, 50, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=3))
    # Тріщина (дефект)
    f.append(path_svg(f"M 640,{y0+130} L 642,{y0+150} L 638,{y0+165}", fill="none", stroke="#b91c1c", sw=2.5))
    f.append(text(642, y0 + 175, "Тріщина (дефект)", size=10, bold=True, color="#b91c1c"))

    # Вимірювальний датчик (котушка NDT)
    f.append(rect(625, y0 + 75, 34, 45, fill="#e9d5ff", stroke="#7e22ce", sw=1.5, rx=3))
    f.append(text(642, y0 + 98, "Датчик", size=10, bold=True, color="#7e22ce"))

    # Спотворені вихрові струми
    f.append(ellipse(615, y0 + 142, 18, 8, fill="none", stroke=POS, sw=1.5))
    f.append(ellipse(670, y0 + 142, 18, 8, fill="none", stroke=POS, sw=1.5))

    f.append(text(642, y0 + 235, "Виявлення мікротріщин,", size=11, bold=True, color=INK))
    f.append(text(642, y7 := y0 + 252, "контроль товщини покриттів", size=10, color=MUTED))
    f.append(text(642, y7 + 16, "без руйнування деталі", size=10, color=MUTED))

    f.append(text(W / 2, H - 15, "Вихрові струми забезпечують безконтактне гальмування, високоточний нагрів та контроль якості", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'eddy-current-mechanism.svg'), W, H, "\n".join(f))

if __name__ == '__main__':
    fig_eddy_current_mechanism()
    fig_skin_effect_depth()
    fig_eddy_loss_lamination()
    fig_eddy_current_applications()
    print("Успішно згенеровано 4 SVG фігури у ./img/")
