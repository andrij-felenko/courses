# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PHI = (1 + 5 ** 0.5) / 2
GOLD = "#d98a1e"

# ── Фігура 1: Геометрія золотого перетину та прямокутника ────────────────────
def fig_golden_rectangle():
    W, H = 820, 360
    parts = []

    # Частина А: Поділ відрізка в крайньому та середньому відношенні
    x0, y0 = 60, 90
    L = 340.0
    a = L / PHI
    b = L - a
    x1 = x0 + a
    x2 = x0 + L

    parts.append(text(x0, y0 - 45, "А. Поділ відрізка на частини a та b:", 14, INK, "start", bold=True))

    # Лінії відрізків
    parts.append(line(x0, y0, x1, y0, color=GOLD, sw=4))
    parts.append(line(x1, y0, x2, y0, color=NEG, sw=4))

    # Засічки
    parts.append(line(x0, y0 - 8, x0, y0 + 8, color=INK, sw=2))
    parts.append(line(x1, y0 - 8, x1, y0 + 8, color=INK, sw=2))
    parts.append(line(x2, y0 - 8, x2, y0 + 8, color=INK, sw=2))

    # Підписи підрізків
    parts.append(text(x0 + a / 2, y0 + 24, "більша частина a", 13, GOLD, "middle", bold=True))
    parts.append(text(x1 + b / 2, y0 + 24, "менша b", 13, NEG, "middle", bold=True))

    # Загальний розмір зверху
    parts.append(line(x0, y0 - 20, x2, y0 - 20, color=MUTED, sw=1.2))
    parts.append(line(x0, y0 - 25, x0, y0 - 15, color=MUTED, sw=1.2))
    parts.append(line(x2, y0 - 25, x2, y0 - 15, color=MUTED, sw=1.2))
    parts.append(text(x0 + L / 2, y0 - 26, "ціле (a + b)", 12, MUTED, "middle"))

    # Формула відношення
    parts.append(fitbox(x0, y0 + 55, L, 45, "(a + b) / a  =  a / b  =  φ  ≈  1.618034", size=13, bold=True, fill="#f8fafc", stroke="#cbd5e1"))

    # Частина Б: Золотий прямокутник з квадратним висіком
    rx0, ry0 = 470, 45
    rect_w = 290.0
    rect_h = rect_w / PHI  # ≈ 179.23
    sq_w = rect_h          # Квадрат 179.23 x 179.23

    parts.append(text(rx0, ry0 - 10, "Б. Золотий прямокутник і квадрат:", 14, INK, "start", bold=True))

    # Зовнішній прямокутник
    parts.append(rect(rx0, ry0, rect_w, rect_h, fill="#ffffff", stroke=GOLD, sw=2.5))
    # Заповнення квадрата
    parts.append(rect(rx0, ry0, sq_w, rect_h, fill="#fef3c7", stroke=INK, sw=1.5))

    # Підписи сторін квадрата та залишкового прямокутника
    parts.append(text(rx0 + sq_w / 2, ry0 + rect_h / 2, "Квадрат\na × a", 13, POS, "middle", bold=True))
    parts.append(text(rx0 + sq_w + (rect_w - sq_w) / 2, ry0 + rect_h / 2, "Подібний\nзолотий\nпрямокутник", 11, NEG, "middle"))

    # Розміри прямокутника
    parts.append(text(rx0 + rect_w / 2, ry0 + rect_h + 20, "сторона a", 12, INK, "middle"))
    parts.append(text(rx0 + rect_w + 15, ry0 + rect_h / 2, "b", 12, INK, "start"))

    render(os.path.join(IMG, 'golden-rectangle.svg'), W, H, *parts,
           title='Геометрія золотого перетину: відрізок і прямокутник')


# ── Фігура 2: Похибка наближення ланцюговими дробами ──────────────────────────
def fig_continued_fraction_convergence():
    W, H = 820, 420
    ox, x_right = 90, 760
    y_top, y_bot = 80, 360

    parts = []

    parts.append(text(W / 2, 35, "Швидкість наближення раціональними підхідними дробами", 16, INK, "middle", bold=True))
    parts.append(text(W / 2, 55, "Нормована похибка |x - pₙ/qₙ| · qₙ² для різних ірраціональностей", 12, MUTED, "middle"))

    # Осі
    parts.append(arrow(ox, y_bot, x_right + 20, y_bot, color=INK, sw=1.8))
    parts.append(arrow(ox, y_bot, ox, y_top - 20, color=INK, sw=1.8))
    parts.append(text(x_right + 22, y_bot + 4, "n", 13, INK, "start", italic=True))
    parts.append(text(ox - 10, y_top - 22, "|x - pₙ/qₙ| · qₙ²", 12, INK, "start", bold=True))

    # Границя Гурвіца 1/√5 ≈ 0.4472
    hurwitz = 1.0 / (5 ** 0.5)
    def Y(val):
        return y_bot - (val / 0.6) * (y_bot - y_top)

    def X(n):
        return ox + (n - 1) / 9.0 * (x_right - ox)

    y_hurw = Y(hurwitz)
    parts.append(line(ox, y_hurw, x_right, y_hurw, color=POS, sw=1.8, dash="6 4"))
    parts.append(text(x_right - 10, y_hurw - 8, "Межа Гурвіца 1/√5 ≈ 0.4472", 12, POS, "end", bold=True))

    # Сітка Y
    for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
        yy = Y(v)
        parts.append(line(ox, yy, x_right, yy, color="#f1f5f9", sw=1.0))
        parts.append(text(ox - 10, yy + 4, "%.1f" % v, 11, MUTED, "end"))

    # Позначки n
    for n in range(1, 11):
        parts.append(text(X(n), y_bot + 20, str(n), 11, MUTED, "middle"))

    # Значення похибок |x - p_n/q_n| * q_n^2
    phi_errs = [0.38196, 0.44721, 0.44721, 0.44721, 0.44721, 0.44721, 0.44721, 0.44721, 0.44721, 0.44721]
    sqrt2_errs = [0.4142, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535, 0.3535]
    e_errs = [0.2817, 0.165, 0.38, 0.08, 0.21, 0.03, 0.14, 0.015, 0.09, 0.008]

    # Малювання ліній
    pts_phi = ' '.join('%.1f,%.1f' % (X(i + 1), Y(phi_errs[i])) for i in range(10))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_phi, GOLD))

    pts_sqrt2 = ' '.join('%.1f,%.1f' % (X(i + 1), Y(sqrt2_errs[i])) for i in range(10))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts_sqrt2, NEG))

    pts_e = ' '.join('%.1f,%.1f' % (X(i + 1), Y(e_errs[i])) for i in range(10))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3"/>' % (pts_e, FIELD))

    # Точки
    for i in range(10):
        parts.append(circle(X(i + 1), Y(phi_errs[i]), 4, fill=GOLD, stroke="#ffffff", sw=1))
        parts.append(circle(X(i + 1), Y(sqrt2_errs[i]), 3.5, fill=NEG, stroke="#ffffff", sw=1))
        parts.append(circle(X(i + 1), Y(e_errs[i]), 3.5, fill=FIELD, stroke="#ffffff", sw=1))

    # Легенда
    parts.append(rect(ox + 20, y_top + 10, 240, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(line(ox + 35, y_top + 30, ox + 65, y_top + 30, color=GOLD, sw=2.5))
    parts.append(circle(ox + 50, y_top + 30, 4, fill=GOLD))
    parts.append(text(ox + 75, y_top + 34, "φ (золотий перетин) — найповільніше", 11, INK, "start", bold=True))

    parts.append(line(ox + 35, y_top + 50, ox + 65, y_top + 50, color=NEG, sw=2))
    parts.append(circle(ox + 50, y_top + 50, 3.5, fill=NEG))
    parts.append(text(ox + 75, y_top + 54, "√2 — середня швидкість", 11, INK, "start"))

    parts.append(line(ox + 35, y_top + 70, ox + 65, y_top + 70, color=FIELD, sw=2, dash="4 3"))
    parts.append(circle(ox + 50, y_top + 70, 3.5, fill=FIELD))
    parts.append(text(ox + 75, y_top + 74, "e (число Ейлера) — стрімкі стрибки", 11, INK, "start"))

    render(os.path.join(IMG, 'continued-fraction-convergence.svg'), W, H, *parts,
           title='Порівняння похибки наближення ірраціональних чисел дробами')


# ── Фігура 3: Метод золотого перетину для одномірної оптимізації ──────────────
def fig_golden_search_brackets():
    W, H = 820, 360
    ox = 60
    L = 700.0
    y_axis = 140

    parts = []

    parts.append(text(W / 2, 35, "Схема розбиття інтервалу в пошуку золотого перетину", 16, INK, "middle", bold=True))

    a_x = ox
    b_x = ox + L

    inv_phi = 1.0 / PHI
    inv_phi2 = 1.0 / (PHI * PHI)

    x1_x = a_x + inv_phi2 * L
    x2_x = a_x + inv_phi * L

    # Основна вісь
    parts.append(line(a_x, y_axis, b_x, y_axis, color=INK, sw=3))

    # Вертикальні засічки точок
    parts.append(line(a_x, y_axis - 15, a_x, y_axis + 15, color=INK, sw=2.5))
    parts.append(line(b_x, y_axis - 15, b_x, y_axis + 15, color=INK, sw=2.5))
    parts.append(line(x1_x, y_axis - 25, x1_x, y_axis + 25, color=POS, sw=2.5))
    parts.append(line(x2_x, y_axis - 25, x2_x, y_axis + 25, color=NEG, sw=2.5))

    # Підписи точок
    parts.append(text(a_x, y_axis + 40, "a", 15, INK, "middle", bold=True))
    parts.append(text(x1_x, y_axis + 40, "x₁", 15, POS, "middle", bold=True))
    parts.append(text(x2_x, y_axis + 40, "x₂", 15, NEG, "middle", bold=True))
    parts.append(text(b_x, y_axis + 40, "b", 15, INK, "middle", bold=True))

    # Відношення відстаней зверху
    parts.append(line(a_x, y_axis - 45, x2_x, y_axis - 45, color=GOLD, sw=1.5))
    parts.append(text(a_x + (x2_x - a_x) / 2, y_axis - 52, "відстань = 0.618 · (b − a)", 12, GOLD, "middle", bold=True))

    parts.append(line(x1_x, y_axis - 75, b_x, y_axis - 75, color=GOLD, sw=1.5))
    parts.append(text(x1_x + (b_x - x1_x) / 2, y_axis - 82, "відстань = 0.618 · (b − a)", 12, GOLD, "middle", bold=True))

    # Пояснення повторного використання
    msg = "Якщо f(x₁) < f(x₂), новий інтервал [a, x₂]. Точка x₁ стає новою x₂ у [a, x₂].\nПотрібне лише одне нове обчислення функції за крок."
    parts.append(fitbox(ox + 40, y_axis + 80, L - 80, 85, msg, size=12, fill="#f8fafc", stroke="#cbd5e1"))

    render(os.path.join(IMG, 'golden-search-brackets.svg'), W, H, *parts,
           title='Схема розбиття інтервалу в алгоритмі золотого перетину')


if __name__ == '__main__':
    fig_golden_rectangle()
    fig_continued_fraction_convergence()
    fig_golden_search_brackets()
    print("All figures successfully generated!")
