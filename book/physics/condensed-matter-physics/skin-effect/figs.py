# -*- coding: utf-8 -*-
"""Фігури до теми «Скін-ефект».
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


# ── Фігура 1: Розподіл густини струму та глибина скін-шару ──────────────────────
def fig_skin_depth_distribution():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Розподіл густини струму та глибина скін-шару δ", size=16, bold=True, color=INK))

    # Ліва панель: поперечний переріз провідника
    f.append(rect(20, 45, 360, 355, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(200, 68, "Поперечний переріз провідника", size=13, bold=True, color=INK))

    # Круглий провідник радіуса R
    cx, cy, R = 200, 220, 110
    f.append(circle(cx, cy, R, fill="#e2e8f0", stroke="#64748b", sw=2))

    # Скін-шар товщиною delta
    delta = 32
    f.append(circle(cx, cy, R - delta, fill="#0f172a", stroke="#334155", sw=1.5))
    f.append(circle(cx, cy, R, fill="none", stroke=POS, sw=3))

    # Тіньове виділення скін-шару
    f.append(ellipse(cx, cy, R, R, fill="none", stroke="#2563eb", sw=12))

    # Позначення глибини delta
    f.append(line(cx + R - delta, cy, cx + R, cy, color=NEG, sw=2))
    f.append(line(cx + R - delta, cy - 8, cx + R - delta, cy + 8, color=NEG, sw=1.5))
    f.append(line(cx + R, cy - 8, cx + R, cy + 8, color=NEG, sw=1.5))
    f.append(text(cx + R - delta / 2, cy - 14, "δ", size=14, bold=True, color=NEG))

    # Внутрішня зона без струму
    f.append(text(cx, cy - 15, "Центральне ядро:", size=11, bold=True, color="#64748b"))
    f.append(text(cx, cy + 5, "j(r) ≈ 0", size=13, bold=True, color="#475569"))
    f.append(text(cx, cy + 25, "(виштовхування струму)", size=10, italic=True, color="#64748b"))

    # Поверхнева зона струму
    f.append(text(cx + 45, cy - 80, "Скін-шар: j ≈ j_0", size=11, bold=True, color=POS))

    # Радіус R
    f.append(line(cx, cy, cx - R * 0.707, cy + R * 0.707, color="#64748b", sw=1.5, dash="3,3"))
    f.append(text(cx - 35, cy + 40, "Радіус R", size=11, bold=True, color="#475569"))

    # Права панель: графік експоненційного згасання j(x)
    f.append(rect(400, 45, 360, 355, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(580, 68, "Згасання густини струму j(x)", size=13, bold=True, color=INK))

    gx0, gy0 = 440, 340
    gw, gh = 300, 230

    # Осі
    f.append(arrow(gx0, gy0, gx0 + gw + 10, gy0, color=INK, sw=1.5))
    f.append(arrow(gx0, gy0, gx0, gy0 - gh - 10, color=INK, sw=1.5))
    f.append(text(gx0 + gw - 10, gy0 + 20, "Глибина x", size=11, bold=True, color=INK))
    f.append(text(gx0 - 25, gy0 - gh, "j(x)", size=11, bold=True, color=INK))

    # Лінія y = 1/e (36.8%)
    y_e = gy0 - gh * 0.368
    f.append(line(gx0, y_e, gx0 + gw, y_e, color="#94a3b8", sw=1, dash="4,4"))
    f.append(text(gx0 - 20, y_e + 4, "j_0/e", size=10, bold=True, color="#64748b"))
    f.append(text(gx0 - 25, y_e + 16, "(36.8%)", size=9, color="#64748b"))

    # Позначка x = delta, 2delta, 3delta
    x_d1 = gx0 + gw * 0.3
    x_d2 = gx0 + gw * 0.6
    x_d3 = gx0 + gw * 0.9

    f.append(line(x_d1, gy0, x_d1, gy0 - gh, color="#94a3b8", sw=1, dash="4,4"))
    f.append(line(x_d2, gy0, x_d2, gy0 - gh, color="#94a3b8", sw=1, dash="4,4"))
    f.append(line(x_d3, gy0, x_d3, gy0 - gh, color="#94a3b8", sw=1, dash="4,4"))

    f.append(text(x_d1, gy0 + 15, "1δ", size=11, bold=True, color=NEG))
    f.append(text(x_d2, gy0 + 15, "2δ", size=11, bold=True, color=INK))
    f.append(text(x_d3, gy0 + 15, "3δ", size=11, bold=True, color=INK))

    # Кріва амплітуди e^(-x/delta)
    pts_amp = []
    pts_wave = []
    for i in range(101):
        x_rel = i / 100.0 * 3.0  # 0 to 3 delta
        px = gx0 + (x_rel / 3.0) * gw
        val_amp = math.exp(-x_rel)
        py_amp = gy0 - val_amp * gh
        pts_amp.append(f"{px:.1f},{py_amp:.1f}")

        # Хвиля з фазовим зсувом cos(x/delta)
        val_wave = math.exp(-x_rel) * math.cos(x_rel)
        py_wave = gy0 - val_wave * gh
        pts_wave.append(f"{px:.1f},{py_wave:.1f}")

    # Огинайне експоненційне загасання
    f.append(f'<polyline points="{" ".join(pts_amp)}" fill="none" stroke="{NEG}" stroke-width="1.5" stroke-dasharray="3,3"/>')

    # Миттєвий розподіл j(x) = j0 e^(-x/delta) cos(omega t - x/delta)
    f.append(f'<polyline points="{" ".join(pts_wave)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Легенда
    f.append(line(570, 95, 600, 95, color=POS, sw=2.5))
    f.append(text(605, 99, "j(x, t) миттєвий", size=10, bold=True, color=INK, anchor="start"))
    f.append(line(570, 115, 600, 115, color=NEG, sw=1.5, dash="3,3"))
    f.append(text(605, 119, "Амплітуда e^(-x/δ)", size=10, bold=True, color=INK, anchor="start"))

    # Позначка 86% струму в межах 1delta
    f.append(text(x_d1 + 45, gy0 - gh * 0.7, "86% струму у межах 1δ", size=10, bold=True, color=POS))
    f.append(text(x_d1 + 45, gy0 - gh * 0.55, "98% тепла у межах 3δ", size=10, bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "skin-depth-distribution.svg"), W, H, *f)


# ── Фігура 2: Класичний vs Аномальний скін-ефект ──────────────────────────────
def fig_classic_vs_anomalous():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Нормальний (класичний) та аномальний скін-ефект", size=16, bold=True, color=INK))

    # Ліва панель: Класичний скін-ефект (l << delta)
    f.append(rect(20, 45, 360, 355, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(200, 68, "Нормальний скін-ефект (l ≪ δ)", size=13, bold=True, color=INK))

    # Скін-шар товстий порівняно з пробігом l
    f.append(rect(40, 90, 110, 290, fill="#dbeafe", stroke="#3b82f6", sw=1.5))
    f.append(rect(150, 90, 210, 290, fill="#f1f5f9", stroke="#94a3b8", sw=1))

    f.append(text(95, 115, "Скін-шар δ", size=12, bold=True, color=POS))

    # Траєкторії електронів (короткі зиґзаґи l << delta)
    for y_pos in [160, 220, 280, 340]:
        x0 = 60
        d_path = f"M {x0} {y_pos} L {x0+15} {y_pos-10} L {x0+28} {y_pos+8} L {x0+40} {y_pos-5}"
        f.append(path_svg(d_path, stroke=NEG, sw=1.5))
        f.append(circle(x0+40, y_pos-5, 3, fill=NEG, stroke="none"))
        if y_pos == 160:
            f.append(line(x0, y_pos+18, x0+15, y_pos+18, color=INK, sw=1.5))
            f.append(text(x0+8, y_pos+30, "l", size=11, bold=True, color=INK))

    # Локальний закон Ома j(r) = sigma * E(r)
    f.append(rect(170, 140, 175, 75, fill="#ffffff", stroke=BORDER, rx=6))
    f.append(text(257, 160, "Локальний зв'язок:", size=11, bold=True, color=INK))
    f.append(text(257, 182, "j(r) = σ · E(r)", size=13, bold=True, color=POS))
    f.append(text(257, 202, "Електрон відчуває E = const", size=10, italic=True, color="#475569"))

    f.append(text(257, 260, "Високі температури (T ≈ 300 K)", size=11, bold=True, color="#334155"))
    f.append(text(257, 280, "Короткий пробіг l ≈ 10⁻⁸ м", size=10, color="#475569"))
    f.append(text(257, 300, "Опір R_s ∝ √f", size=11, bold=True, color=POS))

    # Права панель: Аномальний скін-ефект (l >> delta)
    f.append(rect(400, 45, 360, 355, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(580, 68, "Аномальний скін-ефект (l ≫ δ)", size=13, bold=True, color=INK))

    # Скін-шар дуже тонкий порівняно з l
    f.append(rect(420, 90, 35, 290, fill="#fee2e2", stroke=NEG, sw=1.5))
    f.append(rect(455, 90, 285, 290, fill="#f1f5f9", stroke="#94a3b8", sw=1))

    f.append(text(437, 115, "δ", size=12, bold=True, color=NEG))

    # Траєкторії електронів
    path1 = "M 428 140 L 432 240 L 429 340"
    f.append(path_svg(path1, stroke=POS, sw=2))
    f.append(circle(429, 340, 3, fill=POS, stroke="none"))
    f.append(text(465, 145, "Ковзаючі електрони", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(465, 160, "(ефективно взаємодіють)", size=9, color=POS, anchor="start"))

    path2 = "M 425 210 L 580 235"
    f.append(path_svg(path2, stroke=NEG, sw=1.5, dash="3,3"))
    f.append(circle(580, 235, 3, fill=NEG, stroke="none"))
    f.append(text(500, 220, "Пролітні електрони (неефективні)", size=10, color=NEG, anchor="start"))

    # Довжина пробігу l
    f.append(line(428, 360, 680, 360, color=INK, sw=1.5))
    f.append(line(428, 354, 428, 366, color=INK, sw=1.5))
    f.append(line(680, 354, 680, 366, color=INK, sw=1.5))
    f.append(text(554, 375, "Довжина пробігу l ≫ δ (до 10⁻⁴ м)", size=11, bold=True, color=INK))

    # Нелокальний зв'язок j(r) != sigma * E(r) (використовуємо textbox без прямокутного перекриття)
    tb = mtext(642, 268, ["Нелокальний зв'язок:", "j(r) = ∫ K(r,r') E(r') dr'", "Низькі T (4.2 K), ВЧ (ВЧ/СВЧ)", "Опір R_s ∝ f^(2/3) (не залежить від σ)"], size=10, color=INK, bold=True)
    f.append(tb)

    render(os.path.join(IMG_DIR, "classic-vs-anomalous.svg"), W, H, *f)


# ── Фігура 3: Еквівалентне коло поверхневого імпедансу та фази ────────────────
def fig_surface_impedance_circuit():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 25, "Поверхневий імпеданс провідника Z_s = R_s + i · X_s", size=16, bold=True, color=INK))

    # Ліва панель: Поверхневе еквівалентне коло
    f.append(rect(20, 45, 360, 315, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(200, 68, "Еквівалентна схема скін-шару", size=13, bold=True, color=INK))

    # Вхідний електричний та магнітний вектор поля
    f.append(arrow(40, 180, 110, 180, color=POS, sw=2.5))
    f.append(text(75, 168, "Поле E_s", size=11, bold=True, color=POS))

    # Блок імпедансу Z_s
    f.append(rect(110, 130, 180, 100, fill="#ffffff", stroke="#475569", sw=2, rx=6))
    f.append(text(200, 155, "Z_s = R_s + i · X_s", size=13, bold=True, color=INK))

    # Послідовне з'єднання R_s та L_s
    f.append(rect(130, 180, 50, 30, fill="#dbeafe", stroke=POS, sw=1.5))
    f.append(text(155, 199, "R_s", size=11, bold=True, color=POS))

    f.append(text(195, 199, "+", size=14, bold=True, color=INK))

    # Індуктивність X_s
    f.append(circle(225, 195, 12, fill="#fee2e2", stroke=NEG, sw=1.5))
    f.append(text(225, 199, "X_s", size=11, bold=True, color=NEG))

    f.append(text(200, 248, "R_s = 1 / (σ · δ)", size=11, bold=True, color=POS))
    f.append(text(200, 270, "X_s = ω · L_s = 1 / (σ · δ)", size=11, bold=True, color=NEG))

    f.append(text(200, 310, "Активні втрати = Реактивна енергія", size=11, bold=True, color="#334155"))
    f.append(text(200, 330, "(Рівність активного й індуктивного опорів)", size=10, italic=True, color="#64748b"))

    # Права панель: Фазова діаграма вектора Пойнтінга та полів
    f.append(rect(400, 45, 360, 315, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(580, 68, "Фазове співвідношення полів (45°)", size=13, bold=True, color=INK))

    cx, cy = 520, 230

    # Комплексна площина (Re, Im)
    f.append(arrow(cx - 80, cy, cx + 180, cy, color=INK, sw=1.5))
    f.append(arrow(cx, cy + 80, cx, cy - 130, color=INK, sw=1.5))
    f.append(text(cx + 170, cy + 18, "Re", size=11, bold=True, color=INK))
    f.append(text(cx - 18, cy - 120, "Im", size=11, bold=True, color=INK))

    # Вектор R_s уздовж Re
    f.append(arrow(cx, cy, cx + 110, cy, color=POS, sw=3))
    f.append(text(cx + 55, cy + 20, "R_s", size=12, bold=True, color=POS))

    # Вектор X_s уздовж Im
    f.append(arrow(cx + 110, cy, cx + 110, cy - 110, color=NEG, sw=2))
    f.append(text(cx + 130, cy - 55, "i · X_s", size=12, bold=True, color=NEG, anchor="start"))

    # Результуючий вектор імпедансу Z_s під кутом 45 град (pi/4)
    f.append(arrow(cx, cy, cx + 110, cy - 110, color="#8b5cf6", sw=3))
    f.append(text(cx + 20, cy - 115, "Z_s = R_s · √2 e^(i π/4)", size=11, bold=True, color="#8b5cf6", anchor="start"))

    # Дуга кута 45 градусів
    path_arc = f"M {cx+40} {cy} A 40 40 0 0 0 {cx+28} {cy-28}"
    f.append(path_svg(path_arc, stroke="#8b5cf6", sw=1.5))
    f.append(text(cx + 50, cy - 15, "φ = 45° (π/4)", size=10, bold=True, color="#8b5cf6"))

    # Коментар про фазовий зсув
    f.append(text(580, 310, "Струм запізнюється відносно напруженості", size=10, bold=True, color="#334155"))
    f.append(text(580, 330, "електричного поля точно на 45° (π/4)", size=10, bold=True, color="#334155"))

    render(os.path.join(IMG_DIR, "surface-impedance-circuit.svg"), W, H, *f)


# ── Фігура 4: Конструкція літцендрату та зниження скін-втрат ──────────────────
def fig_litz_wire_principle():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 25, "Зниження втрат від скін-ефекту: суцільний провідник vs літцендрат", size=16, bold=True, color=INK))

    # Ліва панель: Суцільний провідник на ВЧ
    f.append(rect(20, 45, 360, 315, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(200, 68, "Суцільний провідник на ВЧ", size=13, bold=True, color=INK))

    # Велике коло провідника
    cx1, cy1, R1 = 200, 185, 80
    f.append(circle(cx1, cy1, R1, fill="#e2e8f0", stroke="#64748b", sw=2))

    # Кільце струму (лише по краю)
    f.append(ellipse(cx1, cy1, R1, R1, fill="none", stroke=POS, sw=16))
    f.append(circle(cx1, cy1, R1 - 10, fill="#f8fafc", stroke="#64748b", sw=1))

    f.append(text(cx1, cy1 - 10, "Невикористаний", size=11, bold=True, color=NEG))
    f.append(text(cx1, cy1 + 10, "об'єм металу", size=11, bold=True, color=NEG))

    f.append(text(cx1 + 55, cy1 - 70, "Струм протікає", size=10, bold=True, color=POS))
    f.append(text(cx1 + 55, cy1 - 55, "лише тонким кільцем", size=10, bold=True, color=POS))

    f.append(text(200, 290, "Високий ефективний опір R_AC ≫ R_DC", size=11, bold=True, color=NEG))
    f.append(text(200, 315, "Великі джоулеві втрати, падіння добротності Q", size=10, color="#475569"))

    # Права панель: Літцендрат (Litz wire)
    f.append(rect(400, 45, 360, 315, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(580, 68, "Багатожильний літцендрат (Litz wire)", size=13, bold=True, color=INK))

    cx2, cy2, R2 = 580, 185, 80
    # Зовнішня ізолююча оболонка
    f.append(circle(cx2, cy2, R2, fill="#f1f5f9", stroke="#475569", sw=1.5))

    # Упаковка дрібних ізольованих жилок
    r_strand = 11
    offsets = [
        (0, 0),
        (24, 0), (-24, 0), (0, 24), (0, -24),
        (17, 17), (-17, 17), (17, -17), (-17, -17),
        (44, 0), (-44, 0), (0, 44), (0, -44),
        (32, 32), (-32, 32), (32, -32), (-32, -32),
        (46, 20), (-46, 20), (46, -20), (-46, -20)
    ]

    for dx, dy in offsets:
        px, py = cx2 + dx, cy2 + dy
        if math.hypot(dx, dy) + r_strand <= R2 - 2:
            f.append(circle(px, py, r_strand, fill="#dbeafe", stroke=POS, sw=1.5))
            f.append(circle(px, py, r_strand - 2, fill=POS, stroke="none"))

    f.append(text(580, 290, "Кожна жилка має діаметр d < δ", size=11, bold=True, color=POS))
    f.append(text(580, 315, "Рівномірний розподіл струму по всьому перерізу", size=10, bold=True, color=POS))
    f.append(text(580, 335, "Спеціальне переплетення змінює позицію жилок", size=10, italic=True, color="#475569"))

    render(os.path.join(IMG_DIR, "litz-wire-principle.svg"), W, H, *f)


def main():
    print("Генерація SVG-фігур для скін-ефекту...")
    fig_skin_depth_distribution()
    fig_classic_vs_anomalous()
    fig_surface_impedance_circuit()
    fig_litz_wire_principle()
    print("Успішно згенеровано 4 фігури в ./img/")

if __name__ == "__main__":
    main()
