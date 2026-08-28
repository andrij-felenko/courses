# -*- coding: utf-8 -*-
"""Фігури до теми «Поріг і ціна помилки: хибне спрацювання проти пропуску»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── Фігура 1: Графік очікуваних втрат залежно від порогу класифікації T ──────
def fig_expected_cost_vs_threshold():
    W, H = 880, 520
    frags = []

    # Заголовок
    frags.append(text(W / 2, 26, "Очікувані втрати залежно від порогу класифікації T", size=16, bold=True))

    # Область графіка
    gx, gy, gw, gh = 85, 65, 520, 370
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d5d9e0", sw=1.2, rx=4))

    # Горизонтальні лінії сітки
    for i in range(1, 5):
        y_grid = gy + gh - i * (gh / 5)
        frags.append(line(gx, y_grid, gx + gw, y_grid, color="#f0f2f5", sw=1.0))
        val_label = "%d" % (i * 20)
        frags.append(text(gx - 10, y_grid + 4, val_label, size=11, color=MUTED, anchor="end"))
    frags.append(text(gx - 10, gy + gh + 4, "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx - 45, gy + gh / 2, "Очікувані втрати E[Cost], ум. од.", size=12, color=INK, anchor="middle"))

    # Вертикальні лінії сітки (T від 0.0 до 1.0)
    for i in range(11):
        x_grid = gx + i * (gw / 10)
        frags.append(line(x_grid, gy, x_grid, gy + gh, color="#f0f2f5", sw=1.0))
        t_label = "%.1f" % (i * 0.1)
        frags.append(text(x_grid, gy + gh + 20, t_label, size=11, color=MUTED, anchor="middle"))
    frags.append(text(gx + gw / 2, gy + gh + 44, "Поріг класифікації T", size=13, color=INK, anchor="middle", bold=True))

    def cost_fp(t):
        return 9.5 * ((1.0 - t) ** 2.8) * 7.5

    def cost_fn(t):
        return 5.0 * (t ** 1.8) * 16.5

    def total_cost(t):
        return cost_fp(t) + cost_fn(t)

    # Генерація точок кривих
    pts_fp = []
    pts_fn = []
    pts_tot = []
    n_pts = 100
    for step in range(n_pts + 1):
        t = step / float(n_pts)
        px = gx + t * gw
        y_fp = gy + gh - (cost_fp(t) / 100.0) * gh
        y_fn = gy + gh - (cost_fn(t) / 100.0) * gh
        y_tot = gy + gh - (total_cost(t) / 100.0) * gh
        pts_fp.append((px, y_fp))
        pts_fn.append((px, y_fn))
        pts_tot.append((px, y_tot))

    # Малювання кривих
    frags.append(polyline(pts_fp, color=POS, sw=2.0, dash="6 4"))
    frags.append(polyline(pts_fn, color=NEG, sw=2.0, dash="6 4"))
    frags.append(polyline(pts_tot, color=FIELD, sw=3.2))

    # Оптимальний поріг T* (знайдемо чисельно мінімум total_cost)
    best_t = 0.0
    min_c = 1e9
    for step in range(1, n_pts):
        t = step / float(n_pts)
        c = total_cost(t)
        if c < min_c:
            min_c = c
            best_t = t

    opt_x = gx + best_t * gw
    opt_y = gy + gh - (min_c / 100.0) * gh

    # Лінія оптимального порогу T*
    frags.append(line(opt_x, gy, opt_x, gy + gh, color=FIELD, sw=1.8, dash="4 4"))
    frags.append(circle(opt_x, opt_y, 6.0, fill="#ffffff", stroke=FIELD, sw=2.5))

    # Дефолтний поріг T = 0.5
    def_x = gx + 0.5 * gw
    def_c = total_cost(0.5)
    def_y = gy + gh - (def_c / 100.0) * gh
    frags.append(line(def_x, gy, def_x, gy + gh, color=POS, sw=1.8, dash="4 4"))
    frags.append(circle(def_x, def_y, 6.0, fill="#ffffff", stroke=POS, sw=2.5))

    # Стрілка надлишкових втрат (дельта ризику)
    frags.append(line(def_x + 16, opt_y, def_x + 16, def_y, color=POS, sw=1.6))
    frags.append(line(def_x + 10, opt_y, def_x + 22, opt_y, color=POS, sw=1.4))
    frags.append(line(def_x + 10, def_y, def_x + 22, def_y, color=POS, sw=1.4))

    # Права панель для легенди та пояснень (поза графіком, щоб жодна лінія не перетинала написи)
    px_panel = gx + gw + 25
    pw_panel = W - px_panel - 20

    # Блок 1: Легенда
    frags.append(rect(px_panel, gy, pw_panel, 120, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(px_panel + pw_panel / 2, gy + 22, "Криві очікуваних втрат", size=12, color=INK, anchor="middle", bold=True))

    frags.append(line(px_panel + 15, gy + 48, px_panel + 45, gy + 48, color=FIELD, sw=3.0))
    frags.append(text(px_panel + 55, gy + 52, "Сумарний ризик R(T)", size=11, color=INK, anchor="start", bold=True))

    frags.append(line(px_panel + 15, gy + 74, px_panel + 45, gy + 74, color=POS, sw=2.0, dash="6 4"))
    frags.append(text(px_panel + 55, gy + 78, "Втрати від FP (Cost FP)", size=11, color=INK, anchor="start"))

    frags.append(line(px_panel + 15, gy + 100, px_panel + 45, gy + 100, color=NEG, sw=2.0, dash="6 4"))
    frags.append(text(px_panel + 55, gy + 104, "Втрати від FN (Cost FN)", size=11, color=INK, anchor="start"))

    # Блок 2: Оптимум T*
    frags.append(fitbox(px_panel, gy + 135, pw_panel, 105,
                        "Оптимальний поріг T* ≈ 0.16\n\nМінімум сумарного ризику R(T)\nвраховує асиметрію витрат:\nC_FN >> C_FP",
                        size=11, bold=False, fill="#e8f8f0", stroke=FIELD))

    # Блок 3: Дефолт T = 0.50
    frags.append(fitbox(px_panel, gy + 255, pw_panel, 115,
                        "Дефолтний поріг T = 0.50\n\nНадлишкові втрати ΔR\nвиникають через часті пропуски\nкритичних дефектів/цілей",
                        size=11, bold=False, fill="#fdecea", stroke=POS))

    # Рендеринг SVG
    render(os.path.join(OUT, "ochikuvani-vtraty-porih.svg"), W, H, *frags)


# ── Фігура 2: Схема динамічного контуру адаптації порогу ─────────────────────
def fig_adaptive_threshold_loop():
    W, H = 860, 480
    frags = []

    frags.append(text(W / 2, 26, "Контур динамічної адаптації робочого порогу", size=16, bold=True))

    # Стовпець 1 (ліворуч): Фактори контексту середовища
    frags.append(fitbox(35, 65, 215, 68, "Оптичні та сенсорні завади\n(туман, відблиски, шум)", size=12, fill="#f4f6f8", stroke="#6b7280"))
    frags.append(fitbox(35, 150, 215, 68, "Енергетичний стан платформи\n(заряд батареї, запас ходу)", size=12, fill="#f4f6f8", stroke="#6b7280"))
    frags.append(fitbox(35, 235, 215, 68, "Динаміка та висота руху\n(швидкість, дистанція реакції)", size=12, fill="#f4f6f8", stroke="#6b7280"))
    frags.append(fitbox(35, 320, 215, 68, "Навантаження оператора\n(довжина черги верифікації)", size=12, fill="#f4f6f8", stroke="#6b7280"))

    # Стовпець 2 (по центру): Адаптація вартостей та Байєсівський оптимізатор
    frags.append(fitbox(310, 95, 235, 95, "Оцінювач матриці втрат\nРозрахунок C_FP(t) та C_FN(t)\nз урахуванням контексту", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    frags.append(fitbox(310, 250, 235, 95, "Байєсівський оптимізатор\nПерерахунок порогу T*(t)\nза матрицею та пріорами", size=12, bold=True, fill="#e8f8f0", stroke=FIELD))

    # Стовпець 3 (праворуч): Класифікатор і виконавчий контур
    frags.append(fitbox(610, 95, 215, 95, "ML-модель (вивід)\nОцінка ймовірності p(x)\nі калібрування впевненості", size=12, bold=True, fill="#f4f6f8", stroke="#333333"))

    frags.append(fitbox(610, 250, 215, 95, "Динамічний компаратор\nПорівняння p(x) ≥ T*(t)\nі тривожне сповіщення", size=12, bold=True, fill="#fdecea", stroke=POS))

    # Стрілки зв'язків
    frags.append(arrow(250, 99, 310, 125, color=NEG, sw=1.6))
    frags.append(arrow(250, 184, 310, 145, color=NEG, sw=1.6))
    frags.append(arrow(250, 269, 310, 160, color=NEG, sw=1.6))
    frags.append(arrow(250, 354, 310, 175, color=NEG, sw=1.6))

    # Від оцінювача вартостей до Байєсівського оптимізатора
    frags.append(arrow(427, 190, 427, 250, color=NEG, sw=2.0))
    frags.append(text(437, 222, "C_FP, C_FN", size=11, color=NEG, anchor="start", bold=True))

    # Від ML-моделі до компаратора
    frags.append(arrow(717, 190, 717, 250, color="#333333", sw=2.0))
    frags.append(text(727, 222, "ймовірність p(x)", size=11, color=INK, anchor="start"))

    # Від оптимізатора до компаратора
    frags.append(arrow(545, 297, 610, 297, color=FIELD, sw=2.2))
    frags.append(text(577, 287, "поріг T*(t)", size=11, color=FIELD, anchor="middle", bold=True))

    # Зворотний зв'язок: знизу вгору від компаратора до адаптера вартостей
    pts_fb = [(717, 345), (717, 415), (427, 415), (427, 345)]
    frags.append(polyline(pts_fb, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(text(572, 432, "Телеметрія частоти спрацювань і зворотний зв'язок оператора", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "adaptyvne-zmishchennia-porohu.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_expected_cost_vs_threshold()
    fig_adaptive_threshold_loop()
    print("Фігури згенеровано успішно.")
