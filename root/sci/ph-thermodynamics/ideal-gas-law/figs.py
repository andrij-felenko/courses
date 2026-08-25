# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння стану ідеального газу Клапейрона — Менделєєва».
Запуск із теки теми: python figs.py -> SVG у ./img/
"""
import sys, os, math

# Чотири рівні вгору від book/physics/thermodynamics/ideal-gas-law до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Колірна палітра
BLUE_PRIMARY = "#2563eb"
BLUE_LIGHT   = "#eff6ff"
RED_PRIMARY  = "#dc2626"
RED_LIGHT    = "#fef2f2"
GREEN_OK     = "#16a34a"
GREEN_BG     = "#f0fdf4"
ORANGE       = "#d97706"
MUTED_GRAY   = "#4b5563"
BORDER_GRAY  = "#d1d5db"
FILL_BG      = "#f9fafb"
PURPLE       = "#7c3aed"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=FILL_BG, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


# ── Фігура 1: P-V ізотерми ідеального газу та відхилення реального газу ─────
def fig_pv_isotherms():
    W, H = 840, 540
    frags = []

    ox, oy = 90, 450
    gw, gh = 700, 380

    # Осі координат
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    # Стрілки осей
    frags.append(arrow(ox + gw - 20, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy - gh + 20, ox, oy - gh, color=LINE, sw=2))

    frags.append(text(ox + gw / 2, oy + 45, "Об'єм V (м³)", size=14, bold=True))
    frags.append(text(ox - 55, oy - gh / 2, "Тиск P (Па)", size=14, bold=True, anchor="middle"))

    # Ідеальні ізотерми P = C / V
    v_min, v_max = 0.8, 8.0
    
    colors_iso = [(BLUE_PRIMARY, "T₁ (низька T)"), (ORANGE, "T₂ (середня T)"), (RED_PRIMARY, "T₃ (висока T)")]
    constants = [1.8, 3.2, 5.0]

    for idx, (C, (col, label)) in enumerate(zip(constants, colors_iso)):
        pts = []
        for i in range(101):
            v = v_min + (i / 100.0) * (v_max - v_min)
            p = C / v
            cx = ox + ((v - v_min) / (v_max - v_min)) * (gw - 60)
            cy = oy - (p / 6.0) * (gh - 40)
            pts.append((cx, cy))
        
        frags.append(polyline(pts, color=col, sw=2.5))
        # Напис біля кінця ізотерми
        lx, ly = pts[-15]
        frags.append(text(lx + 15, ly - 8, label, size=12, color=col, bold=True))

    # Купол фазового переходу реального газу (газ-рідина)
    dome_pts = []
    for i in range(101):
        t = i / 100.0
        v = 1.5 + 4.5 * t
        # Параболічна баня реального газу
        p = 2.2 - 1.8 * ((v - 3.75) / 2.25) ** 2
        if p < 0.2:
            p = 0.2
        cx = ox + ((v - v_min) / (v_max - v_min)) * (gw - 60)
        cy = oy - (p / 6.0) * (gh - 40)
        dome_pts.append((cx, cy))

    dome_poly = [(ox + ((1.5 - v_min) / (v_max - v_min)) * (gw - 60), oy)] + dome_pts + [(ox + ((6.0 - v_min) / (v_max - v_min)) * (gw - 60), oy)]
    frags.append(polygon(dome_poly, fill="#f3f4f6", stroke=BORDER_GRAY, sw=1.5))
    frags.append(polyline(dome_pts, color=MUTED_GRAY, sw=2.0, dash="5,5"))

    # Пояснювальний текстовий блок
    b_info, _, _ = textbox(ox + 420, oy - 300, 
                           "Ідеальний газ: P = nRT / V (гіперболи)\n"
                           "• Молекули — матеріальні точки без об'єму\n"
                           "• Сили міжмолекулярного притягання відсутні\n\n"
                           "Реальний газ (сіра зона при низьких T та високих P):\n"
                           "• Зрідження та двофазна область (рідина + пара)\n"
                           "• Описується рівнянням Ван-дер-Ваальса",
                           size=12, fill=FILL_BG, stroke=BLUE_PRIMARY, pad=10)
    frags.append(b_info)

    render(os.path.join(IMG, "pv-isotherms.svg"), W, H, *frags, title="Ізотерми ідеального та реального газу на P-V діаграмі")


# ── Фігура 2: Мікроскопічна модель зіткнень молекул зі стінкою ─────────────
def fig_molecular_collisions():
    W, H = 840, 500
    frags = []

    # Контейнер газу (ліворуч)
    bx, by = 60, 80
    bw, bh = 320, 320
    frags.append(rect(bx, by, bw, bh, fill=FILL_BG, stroke=LINE, sw=2, rx=6))
    frags.append(text(bx + bw / 2, by - 20, "Хаотичний рух N молекул у кубі V", size=14, bold=True))

    # Хаотичні молекули в баку
    mol_coords = [
        (bx + 50, by + 60, 12, -8),
        (bx + 120, by + 180, -10, 14),
        (bx + 200, by + 90, 15, 5),
        (bx + 80, by + 240, 6, -15),
        (bx + 260, by + 220, -14, -10),
        (bx + 150, by + 280, 11, 7),
        (bx + 280, by + 120, -8, 12)
    ]
    for mx, my, vx, vy in mol_coords:
        frags.append(circle(mx, my, 7, fill=BLUE_PRIMARY, stroke=INK, sw=1.2))
        frags.append(arrow(mx, my, mx + vx * 2, my + vy * 2, color=RED_PRIMARY, sw=1.5))

    # Пружне зіткнення зі стінкою (правою стінкою баку)
    impact_y = by + 160
    frags.append(circle(bx + bw, impact_y, 9, fill=RED_PRIMARY, stroke=INK, sw=1.5))
    frags.append(arrow(bx + bw - 50, impact_y - 25, bx + bw, impact_y, color=BLUE_PRIMARY, sw=2))
    frags.append(arrow(bx + bw, impact_y, bx + bw - 50, impact_y + 25, color=RED_PRIMARY, sw=2))

    # Збільшена деталь зіткнення (праворуч)
    zx, zy = 450, 80
    zw, zh = 350, 240
    frags.append(rect(zx, zy, zw, zh, fill=BLUE_LIGHT, stroke=BLUE_PRIMARY, sw=2, rx=8))
    frags.append(text(zx + zw / 2, zy + 25, "Пружний відбиток від стінки A", size=14, bold=True, color=BLUE_PRIMARY))

    # Стінка посудини
    wall_x = zx + zw - 40
    frags.append(rect(wall_x, zy + 40, 20, zh - 60, fill="#9ca3af", stroke=INK, sw=1.5))

    # Вхідна і вихідна молекула
    cy = zy + zh / 2
    frags.append(circle(wall_x - 70, cy - 35, 10, fill=BLUE_PRIMARY, stroke=INK, sw=1.5))
    frags.append(arrow(wall_x - 70, cy - 35, wall_x - 10, cy - 5, color=BLUE_PRIMARY, sw=2.5))
    frags.append(text(wall_x - 130, cy - 45, "p_x = +m·v_x", size=12, color=BLUE_PRIMARY, bold=True))

    frags.append(circle(wall_x - 70, cy + 35, 10, fill=RED_PRIMARY, stroke=INK, sw=1.5))
    frags.append(arrow(wall_x - 10, cy + 5, wall_x - 70, cy + 35, color=RED_PRIMARY, sw=2.5))
    frags.append(text(wall_x - 140, cy + 45, "p_x' = −m·v_x", size=12, color=RED_PRIMARY, bold=True))

    # Текстове роз'яснення імпульсу
    b_imp, _, _ = textbox(zx + zw / 2, zy + zh + 70,
                          "Переданий імпульс стінці за 1 зіткнення:\n"
                          "Δp = p_x − p_x' = m·v_x − (−m·v_x) = 2·m·v_x\n\n"
                          "Макроскопічний тиск P = F / A:\n"
                          "Усереднення по N молекулах у 3D просторі:\n"
                          "P = (1/3) · n · m · <v²> = (2/3) · n · <E_k>",
                          size=12, fill=GREEN_BG, stroke=GREEN_OK, pad=10)
    frags.append(b_imp)

    render(os.path.join(IMG, "molecular-collisions.svg"), W, H, *frags, title="Молекулярний механізм виникнення тиску газу при зіткненнях зі стінкою")


# ── Фігура 3: Термодинамічні параметри стану ─────────────────────────────
def fig_state_variables_cube():
    W, H = 840, 480
    frags = []

    # Ілюстрація 3D куба
    cx, cy = 180, 140
    size = 180
    dx, dy = 60, -40

    # Задня грань
    frags.append(polygon([(cx + dx, cy + dy), (cx + size + dx, cy + dy), 
                          (cx + size + dx, cy + size + dy), (cx + dx, cy + size + dy)],
                         fill="#e5e7eb", stroke=BORDER_GRAY, sw=1.5))

    # Передня грань
    frags.append(polygon([(cx, cy), (cx + size, cy), (cx + size, cy + size), (cx, cy + size)],
                         fill="#eff6ff", stroke=BLUE_PRIMARY, sw=2))

    # З'єднувальні ребра
    frags.append(line(cx, cy, cx + dx, cy + dy, color=BLUE_PRIMARY, sw=1.5))
    frags.append(line(cx + size, cy, cx + size + dx, cy + dy, color=BLUE_PRIMARY, sw=1.5))
    frags.append(line(cx + size, cy + size, cx + size + dx, cy + size + dy, color=BORDER_GRAY, sw=1.5))
    frags.append(line(cx, cy + size, cx + dx, cy + size + dy, color=BORDER_GRAY, sw=1.5))

    # Молекули всередині куба
    m_pts = [(cx + 40, cy + 50), (cx + 120, cy + 40), (cx + 80, cy + 110), 
             (cx + 140, cy + 120), (cx + 60, cy + 150), (cx + 160, cy + 70)]
    for px, py in m_pts:
        frags.append(circle(px, py, 6, fill=RED_PRIMARY, stroke=INK, sw=1))

    # Стрілки тиску на стінки
    frags.append(arrow(cx + size / 2, cy, cx + size / 2, cy - 30, color=RED_PRIMARY, sw=2))
    frags.append(text(cx + size / 2, cy - 40, "Тиск P", size=13, color=RED_PRIMARY, bold=True))

    frags.append(arrow(cx + size, cy + size / 2, cx + size + 35, cy + size / 2, color=RED_PRIMARY, sw=2))
    frags.append(text(cx + size + 70, cy + size / 2 + 4, "Площа A", size=13, color=MUTED_GRAY, bold=True))

    # Розміри куба (Об'єм V)
    frags.append(text(cx + size / 2, cy + size + 30, "Об'єм V = L³", size=13, color=BLUE_PRIMARY, bold=True))

    # Права частина: Чотири стовпи параметрів стану
    px_base = 480
    py_base = 80

    params = [
        ("Тиск P (Па)", "Скалярна міра нормальної сили ударів молекул на одиницю площі стінки", RED_PRIMARY, RED_LIGHT),
        ("Об'єм V (м³)", "Простір, доступний для вільного хаотичного руху молекул газу", BLUE_PRIMARY, BLUE_LIGHT),
        ("Температура T (К)", "Абсолютна термодинамічна температура: T ~ <E_k> = (3/2)·k_B·T", ORANGE, "#fffbeb"),
        ("Кількість речовини ν (моль)", "Число молекул N у частках числа Авогадро: ν = N / N_A = m / M", PURPLE, "#f3e8ff")
    ]

    for idx, (title_str, desc_str, col, bg_col) in enumerate(params):
        y_pos = py_base + idx * 85
        b_box, _, _ = textbox(px_base + 160, y_pos + 25, 
                              "%s\n%s" % (title_str, desc_str), 
                              size=12, fill=bg_col, stroke=col, pad=8)
        frags.append(b_box)

    b_eq, _, _ = textbox(W / 2, H - 35,
                         "Зв'язок параметрів стану (Рівняння Клапейрона — Менделєєва):\n"
                         "P · V = (m / M) · R · T   або   P · V = N · k_B · T",
                         size=13, fill=GREEN_BG, stroke=GREEN_OK, pad=8)
    frags.append(b_eq)

    render(os.path.join(IMG, "state-variables-cube.svg"), W, H, *frags, title="Макроскопічні змінні стану ідеального газу в об'ємі")


# ── Фігура 4: Історична інтеграція емпіричних газових законів ───────────────
def fig_clapeyron_mendeleev_unification():
    W, H = 860, 520
    frags = []

    # Чотири вихідні емпіричні закони (ліворуч)
    laws = [
        ("Закон Бойля — Маріотта (1662)", "P · V = const  (при T, N = const)", BLUE_PRIMARY, BLUE_LIGHT),
        ("Закон Шарля (1787)", "V / T = const  (при P, N = const)", ORANGE, "#fffbeb"),
        ("Закон Ґей-Люссака (1802)", "P / T = const  (при V, N = const)", RED_PRIMARY, RED_LIGHT),
        ("Закон Авогадро (1811)", "V / N = const  (при P, T = const)", PURPLE, "#f3e8ff")
    ]

    lx = 170
    for idx, (t_str, f_str, col, bg_col) in enumerate(laws):
        ly = 60 + idx * 95
        b_box, _, _ = textbox(lx, ly, "%s\n%s" % (t_str, f_str), size=12, fill=bg_col, stroke=col, pad=8)
        frags.append(b_box)

        # Стрілки зведення до Клапейрона
        frags.append(arrow(lx + 130, ly, 450, 220, color=col, sw=2))

    # Вузол Еміля Клапейрона (1834)
    cx, cy = 540, 220
    b_clap, _, _ = textbox(cx, cy, 
                           "Рівняння Клапейрона (1834)\n"
                           "(P · V) / T = B_m\n"
                           "Об'єднав часткові закони для сталого маси газу",
                           size=13, fill=GREEN_BG, stroke=GREEN_OK, pad=10)
    frags.append(b_clap)

    # Стрілка від Клапейрона до Менделєєва
    frags.append(arrow(cx, cy + 50, cx, cy + 110, color=GREEN_OK, sw=3))

    # Вузол Дмитра Менделєєва (1874)
    mx, my = 540, 400
    b_mend, _, _ = textbox(mx, my,
                           "Рівняння Клапейрона — Менделєєва (1874)\n"
                           "P · V = (m / M) · R · T\n"
                           "Ввів універсальну газову сталу R = 8.314 Дж/(моль·К)\n"
                           "і молярну масу M для довільної маси газу m",
                           size=13, fill="#fef3c7", stroke=ORANGE, pad=10)
    frags.append(b_mend)

    render(os.path.join(IMG, "clapeyron-mendeleev-unification.svg"), W, H, *frags, title="Еволюція та об'єднання газових законів у рівняння Клапейрона — Менделєєва")


if __name__ == "__main__":
    fig_pv_isotherms()
    fig_molecular_collisions()
    fig_state_variables_cube()
    fig_clapeyron_mendeleev_unification()
    print("Фігури успішно згенеровано у ./img/")
