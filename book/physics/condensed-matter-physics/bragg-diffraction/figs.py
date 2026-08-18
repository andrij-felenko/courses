# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Геометрія Бреґґа та різниця ходу
# ════════════════════════════════════════════════════════════════════════════
def fig_bragg_law_geometry():
    W, H = 840, 460
    f = []

    f.append(text(420, 25, "Геометрія дифракційного відображення Бреґґа від атомних площин", size=15, bold=True, color=INK))

    y1 = 160  # Верхня площина
    y2 = 290  # Нижня площина
    d_val = y2 - y1  # 130 px

    # Позначення міжплощинної відстані d
    f.append(line(80, y1, 80, y2, color=NEG, sw=1.5))
    f.append(line(73, y1, 87, y1, color=NEG, sw=1.5))
    f.append(line(73, y2, 87, y2, color=NEG, sw=1.5))
    f.append(text(60, (y1 + y2) / 2 + 5, "d", size=15, bold=True, color=NEG))

    # Штрихові паралельні площини
    f.append(line(100, y1, 760, y1, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(100, y2, 760, y2, color=MUTED, sw=1.2, dash="4 4"))

    # Атоми верхньої площини
    atom_xs = [160, 260, 360, 460, 560, 660]
    for ax in atom_xs:
        f.append(circle(ax, y1, 9, fill="#ebf5fb", stroke=NEG, sw=2))
        f.append(circle(ax, y1, 3, fill=NEG, stroke="none"))

    # Атоми нижньої площини
    for ax in atom_xs:
        f.append(circle(ax, y2, 9, fill="#ebf5fb", stroke=NEG, sw=2))
        f.append(circle(ax, y2, 3, fill=NEG, stroke="none"))

    # Точки розсіювання: A на верхній (x=360, y=160), B на нижній (x=460, y=290)
    Ax, Ay = 360, y1
    Bx, By = 460, y2

    # Кут ковзання theta = 30 deg
    ray1_in_x = Ax - 220
    ray1_in_y = Ay - 127
    f.append(arrow(ray1_in_x, ray1_in_y, Ax - 10, Ay - 5.8, color=POS, sw=2.2))
    f.append(arrow(Ax, Ay, Ax + 220, Ay - 127, color=POS, sw=2.2))

    # Промінь 2
    ray2_in_x = Bx - 220
    ray2_in_y = By - 127
    f.append(arrow(ray2_in_x, ray2_in_y, Bx - 10, By - 5.8, color=POS, sw=2.2))
    f.append(arrow(Bx, By, Bx + 220, By - 127, color=POS, sw=2.2))

    # Кут ковзання theta
    f.append(text(210, y1 - 12, "θ", size=13, bold=True, color=POS))
    f.append(text(510, y1 - 12, "θ", size=13, bold=True, color=POS))

    # Перпендикуляри C та D
    Cx, Cy = 403.7, 257.5
    Dx, Dy = 516.3, 257.5

    f.append(line(Ax, Ay, Cx, Cy, color="#c0392b", sw=1.8, dash="3 3"))
    f.append(line(Ax, Ay, Dx, Dy, color="#c0392b", sw=1.8, dash="3 3"))

    f.append(circle(Cx, Cy, 3, fill="#c0392b", stroke="none"))
    f.append(circle(Dx, Dy, 3, fill="#c0392b", stroke="none"))

    # Додаткова різниця ходу CB та BD
    f.append(line(Cx, Cy, Bx, By, color="#c0392b", sw=3.0))
    f.append(line(Bx, By, Dx, Dy, color="#c0392b", sw=3.0))

    f.append(text(415, 290, "C", size=12, bold=True, color="#c0392b"))
    f.append(text(460, 312, "B", size=12, bold=True, color=INK))
    f.append(text(510, 290, "D", size=12, bold=True, color="#c0392b"))
    f.append(text(360, y1 - 15, "A", size=12, bold=True, color=INK))

    # Підписи додаткової довжини
    f.append(text(410, 345, "CB = d·sin θ", size=11, bold=True, color="#c0392b"))
    f.append(text(515, 345, "BD = d·sin θ", size=11, bold=True, color="#c0392b"))

    # Пояснювальний плашка з формулою
    f.append(rect(180, 380, 480, 55, fill="#fdfefe", stroke=POS, sw=1.8, rx=8))
    f.append(text(420, 403, "Повна різниця ходу:  Δ = CB + BD = 2d·sin θ", size=13, bold=True, color=INK))
    f.append(text(420, 424, "Умова конструктивної інтерференції:  2d·sin θ = nλ", size=13, bold=True, color=POS))

    render(os.path.join(OUT, "bragg-law-geometry.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Сфера Евальда та векторні умови Лауе
# ════════════════════════════════════════════════════════════════════════════
def fig_reciprocal_lattice_laue():
    W, H = 840, 480
    f = []

    f.append(text(420, 25, "Конструкція сфери Евальда та умова Лауе: k - k₀ = G", size=15, bold=True, color=INK))

    Ox, Oy = 480, 260
    grid_step = 70

    for ix in range(-4, 5):
        for iy in range(-3, 4):
            nx = Ox + ix * grid_step
            ny = Oy + iy * grid_step
            if 60 <= nx <= 780 and 60 <= ny <= 440:
                is_origin = (ix == 0 and iy == 0)
                is_target = (ix == -2 and iy == -2)
                if is_origin:
                    f.append(circle(nx, ny, 6, fill=INK, stroke=INK, sw=1.5))
                    f.append(text(nx + 15, ny + 15, "O (0,0,0)", size=11, bold=True, color=INK))
                elif is_target:
                    f.append(circle(nx, ny, 7, fill=POS, stroke=POS, sw=2))
                    f.append(text(nx - 35, ny - 12, "G (h,k,l)", size=12, bold=True, color=POS))
                else:
                    f.append(circle(nx, ny, 3.5, fill=MUTED, stroke="none"))

    Gx, Gy = Ox - 2 * grid_step, Oy - 2 * grid_step

    Cx, Cy = 250, 350
    R = 247.0

    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>' % (Cx, Cy, R, NEG))
    f.append(circle(Cx, Cy, 4, fill=NEG, stroke="none"))
    f.append(text(Cx - 20, Cy + 20, "Центр C", size=11, bold=True, color=NEG))

    f.append(arrow(Cx, Cy, Ox - 5, Oy + 2, color=NEG, sw=2.2))
    f.append(text(340, 325, "k₀ (|k₀| = 2π/λ)", size=12, bold=True, color=NEG))

    f.append(arrow(Cx, Cy, Gx - 4, Gy + 9, color=NEG, sw=2.2))
    f.append(text(260, 220, "k (|k| = 2π/λ)", size=12, bold=True, color=NEG))

    f.append(arrow(Ox, Oy, Gx + 7, Gy + 7, color=POS, sw=2.5))
    f.append(text(430, 180, "G = h·b₁ + k·b₂ + l·b₃", size=12, bold=True, color=POS))

    f.append(text(120, 100, "Сфера Евальда (радіус R = 2π/λ)", size=12, bold=True, color=NEG))

    f.append(rect(460, 360, 340, 80, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    f.append(text(630, 385, "Умова дифракції:", size=12, bold=True, color=INK))
    f.append(text(630, 408, "Δk = k - k₀ = G", size=13, bold=True, color=POS))
    f.append(text(630, 428, "Вузол G лежить НА поверхні сфери", size=11, color=MUTED))

    render(os.path.join(OUT, "reciprocal-lattice-laue.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Експериментальні методи: Лауе та Дебая — Шеррера
# ════════════════════════════════════════════════════════════════════════════
def fig_diffraction_methods():
    W, H = 840, 440
    f = []

    f.append(text(420, 25, "Основні експериментальні методи рентгеноструктурного аналізу", size=15, bold=True, color=INK))

    # ── Панель 1: Метод Лауе ──
    f.append(text(210, 60, "1. Метод Лауе (біле випромінювання)", size=13, bold=True, color=INK))
    f.append(rect(30, 75, 360, 340, fill="#fafafa", stroke=MUTED, sw=1.0, rx=6))

    f.append(rect(50, 210, 50, 40, fill="#eaeded", stroke=LINE, sw=1.5))
    f.append(text(75, 235, "РТ", size=11, bold=True, color=INK))

    f.append(line(100, 230, 170, 230, color=POS, sw=2.0))
    f.append(text(125, 215, "Біле пучок λ", size=10, color=POS))

    f.append(rect(180, 220, 20, 20, fill="#ebf5fb", stroke=NEG, sw=1.5))
    f.append(text(190, 260, "Монокристал", size=10, bold=True, color=NEG))

    f.append(line(190, 230, 330, 130, color=POS, sw=1.2, dash="3 3"))
    f.append(line(190, 230, 330, 170, color=POS, sw=1.2, dash="3 3"))
    f.append(line(190, 230, 330, 230, color=POS, sw=1.5))
    f.append(line(190, 230, 330, 290, color=POS, sw=1.2, dash="3 3"))
    f.append(line(190, 230, 330, 330, color=POS, sw=1.2, dash="3 3"))

    f.append(line(330, 110, 330, 350, color=LINE, sw=2.5))
    f.append(text(340, 105, "Фотоплівка", size=10, color=INK))

    laue_ys = [130, 170, 230, 290, 330]
    for ly in laue_ys:
        f.append(circle(330, ly, 4, fill=POS, stroke="none"))

    f.append(text(210, 375, "Фіксований монокристал", size=11, color=INK))
    f.append(text(210, 395, "Оцінка симетрії кристала", size=11, bold=True, color=POS))

    # ── Панель 2: Порошковий метод Дебая — Шеррера ──
    f.append(text(630, 60, "2. Метод Дебая — Шеррера (монохроматичне)", size=13, bold=True, color=INK))
    f.append(rect(450, 75, 360, 340, fill="#fafafa", stroke=MUTED, sw=1.0, rx=6))

    f.append(rect(470, 210, 40, 40, fill="#eaeded", stroke=LINE, sw=1.5))
    f.append(line(510, 230, 580, 230, color=NEG, sw=2.0))
    f.append(text(545, 215, "λ₀ = const", size=10, bold=True, color=NEG))

    f.append(circle(600, 230, 8, fill="#e8f8f5", stroke=FIELD, sw=2))
    f.append(text(600, 260, "Порошок", size=10, bold=True, color=FIELD))

    f.append(line(600, 230, 750, 150, color=NEG, sw=1.5))
    f.append(line(600, 230, 750, 310, color=NEG, sw=1.5))
    f.append(line(600, 230, 750, 110, color=NEG, sw=1.2, dash="4 3"))
    f.append(line(600, 230, 750, 350, color=NEG, sw=1.2, dash="4 3"))

    f.append(line(750, 90, 750, 370, color=LINE, sw=2.5))
    f.append(circle(750, 150, 3.5, fill=NEG, stroke="none"))
    f.append(circle(750, 310, 3.5, fill=NEG, stroke="none"))
    f.append(circle(750, 110, 3.5, fill=NEG, stroke="none"))
    f.append(circle(750, 350, 3.5, fill=NEG, stroke="none"))

    f.append(text(670, 215, "2θ", size=11, bold=True, color=NEG))

    f.append(text(630, 375, "Хаотично орієнтовані мікрокристали", size=11, color=INK))
    f.append(text(630, 395, "Фазовий аналіз матеріалів", size=11, bold=True, color=NEG))

    render(os.path.join(OUT, "diffraction-methods.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Систематичні згасання рефлексів у кристалах
# ════════════════════════════════════════════════════════════════════════════
def fig_structure_factor_absences():
    W, H = 840, 440
    f = []

    f.append(text(420, 25, "Вплив типу ґратки на геометричний структурний фактор S(h,k,l)", size=15, bold=True, color=INK))

    # ── Панель 1: Проста кубічна ґратка (SC) ──
    f.append(text(140, 65, "Проста кубічна (SC)", size=13, bold=True, color=INK))
    f.append(rect(30, 80, 230, 330, fill="#fafafa", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(145, 105, "S(h,k,l) = 1", size=11, bold=True, color=POS))
    f.append(text(145, 125, "Усі рефлекси дозволені", size=10, color=MUTED))

    sc_peaks = [
        ("(100)", True),
        ("(110)", True),
        ("(111)", True),
        ("(200)", True),
        ("(210)", True),
        ("(211)", True)
    ]
    for idx, (hkl, ok) in enumerate(sc_peaks):
        py = 160 + idx * 40
        f.append(rect(50, py, 190, 30, fill="#e8f8f5", stroke=FIELD, sw=1.2))
        f.append(text(100, py + 20, hkl, size=12, bold=True, color=INK))
        f.append(text(180, py + 20, "Дозволено", size=10, bold=True, color=FIELD))

    # ── Панель 2: Об'ємноцентрована (BCC) ──
    f.append(text(420, 65, "Об'ємноцентрована (BCC)", size=13, bold=True, color=INK))
    f.append(rect(305, 80, 230, 330, fill="#fafafa", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(420, 105, "h + k + l = парне", size=11, bold=True, color=POS))
    f.append(text(420, 125, "Непарна сума — погасає", size=10, color=MUTED))

    bcc_peaks = [
        ("(100)", False),
        ("(110)", True),
        ("(111)", False),
        ("(200)", True),
        ("(210)", False),
        ("(211)", True)
    ]
    for idx, (hkl, ok) in enumerate(bcc_peaks):
        py = 160 + idx * 40
        bg_c = "#e8f8f5" if ok else "#fdedec"
        st_c = FIELD if ok else POS
        f.append(rect(325, py, 190, 30, fill=bg_c, stroke=st_c, sw=1.2))
        f.append(text(375, py + 20, hkl, size=12, bold=True, color=INK))
        txt_res = "Дозволено" if ok else "Згасає"
        f.append(text(455, py + 20, txt_res, size=10, bold=True, color=st_c))

    # ── Панель 3: Гранецентрована (FCC) ──
    f.append(text(700, 65, "Гранецентрована (FCC)", size=13, bold=True, color=INK))
    f.append(rect(580, 80, 230, 330, fill="#fafafa", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(695, 105, "h, k, l однієї парності", size=11, bold=True, color=POS))
    f.append(text(695, 125, "Змішана парність — погасає", size=10, color=MUTED))

    fcc_peaks = [
        ("(100)", False),
        ("(110)", False),
        ("(111)", True),
        ("(200)", True),
        ("(210)", False),
        ("(220)", True)
    ]
    for idx, (hkl, ok) in enumerate(fcc_peaks):
        py = 160 + idx * 40
        bg_c = "#e8f8f5" if ok else "#fdedec"
        st_c = FIELD if ok else POS
        f.append(rect(600, py, 190, 30, fill=bg_c, stroke=st_c, sw=1.2))
        f.append(text(650, py + 20, hkl, size=12, bold=True, color=INK))
        txt_res = "Дозволено" if ok else "Згасає"
        f.append(text(730, py + 20, txt_res, size=10, bold=True, color=st_c))

    render(os.path.join(OUT, "structure-factor-absences.svg"), W, H, *f)

if __name__ == "__main__":
    fig_bragg_law_geometry()
    fig_reciprocal_lattice_laue()
    fig_diffraction_methods()
    fig_structure_factor_absences()
    print("All Bragg diffraction figures generated successfully.")
