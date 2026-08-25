# -*- coding: utf-8 -*-
"""
Фігури до статті «Косинусна відстань».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=LINE, sw=1.5):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def fig_cosine_geometry():
    W, H = 840, 420
    parts = []

    # Фон та заголовок
    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Геометричний зміст косинусної відстані та кута між векторами", size=16, bold=True))

    # Ліва панель: Вектори у 2D просторі та кут θ
    bx1, by1, bw1, bh1 = 30, 50, 370, 330
    parts.append(rect(bx1, by1, bw1, bh1, fill="#fafafa", stroke="#d0d0d0", sw=1, rx=6))
    parts.append(text(bx1 + bw1 / 2, by1 + 22, "Вектори u та v і кут θ", size=13, bold=True, color=INK))

    # Вісі координат
    ox, oy = bx1 + 60, by1 + 270
    parts.append(arrow(ox - 20, oy, ox + 270, oy, color="#b0b0b0", sw=1.2))
    parts.append(arrow(ox, oy + 20, ox, oy - 220, color="#b0b0b0", sw=1.2))
    parts.append(text(ox + 275, oy + 4, "X", size=11, color=MUTED, bold=True))
    parts.append(text(ox - 10, oy - 225, "Y", size=11, color=MUTED, bold=True))
    parts.append(text(ox - 12, oy + 15, "O", size=10, color=MUTED))

    # Одиничне коло (радіус R = 150)
    R = 150
    parts.append('<path d="M %d %d A %d %d 0 0 0 %d %d" fill="none" stroke="#d5d5d5" stroke-width="1.2" stroke-dasharray="4,4"/>' % (ox + R, oy, R, R, ox, oy - R))
    parts.append(text(ox + R - 35, oy + 18, "R = 1 (Одинична сфера)", size=10, color=MUTED, italic=True))

    # Вектор u (кут 20 градусів, довжина 210)
    ang_u = math.radians(20)
    ux = ox + 210 * math.cos(ang_u)
    uy = oy - 210 * math.sin(ang_u)
    parts.append(arrow(ox, oy, ux, uy, color=FIELD, sw=2.5))
    parts.append(text(ux + 12, uy - 5, "u (довжина ||u||)", size=12, bold=True, color=FIELD))

    # Вектор v (кут 65 градусів, довжина 170)
    ang_v = math.radians(65)
    vx = ox + 170 * math.cos(ang_v)
    vy = oy - 170 * math.sin(ang_v)
    parts.append(arrow(ox, oy, vx, vy, color=POS, sw=2.5))
    parts.append(text(vx - 5, vy - 12, "v (довжина ||v||)", size=12, bold=True, color=POS))

    # Дуга кута θ між векторами (радіус r_arc = 60)
    r_arc = 60
    ax1 = ox + r_arc * math.cos(ang_u)
    ay1 = oy - r_arc * math.sin(ang_u)
    ax2 = ox + r_arc * math.cos(ang_v)
    ay2 = oy - r_arc * math.sin(ang_v)
    parts.append('<path d="M %.1f %.1f A %d %d 0 0 0 %.1f %.1f" fill="none" stroke="#d97706" stroke-width="2"/>' % (ax1, ay1, r_arc, r_arc, ax2, ay2))
    parts.append(text(ox + 80 * math.cos(math.radians(42.5)), oy - 80 * math.sin(math.radians(42.5)), "θ", size=14, bold=True, color="#d97706"))

    # Пунктир проєкції v на u
    proj_len = 170 * math.cos(ang_v - ang_u)
    px = ox + proj_len * math.cos(ang_u)
    py = oy - proj_len * math.sin(ang_u)
    parts.append(line(vx, vy, px, py, color="#888888", sw=1.2, dash="3,3"))
    parts.append(circle(px, py, 3, fill="#888888", stroke="none"))
    parts.append(text(px + 5, py + 18, "Проєкція: ||v||·cos(θ)", size=10, color=MUTED, italic=True))

    # Права панель: Нормалізація на гіперсферу
    bx2, by2, bw2, bh2 = 430, 50, 380, 330
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(bx2 + bw2 / 2, by2 + 22, "Проєкція на одиничну гіперсферу", size=13, bold=True, color=FIELD))

    ox2, oy2 = bx2 + 190, by2 + 185
    R2 = 110
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (ox2, oy2, R2, FIELD))

    # Нормалізовані вектори u_hat та v_hat
    u_hat_x = ox2 + R2 * math.cos(ang_u)
    u_hat_y = oy2 - R2 * math.sin(ang_u)
    v_hat_x = ox2 + R2 * math.cos(ang_v)
    v_hat_y = oy2 - R2 * math.sin(ang_v)

    # Продовження початкових векторів пунктиром
    parts.append(line(ox2, oy2, ox2 + 160 * math.cos(ang_u), oy2 - 160 * math.sin(ang_u), color="#cccccc", sw=1.2, dash="3,3"))
    parts.append(line(ox2, oy2, ox2 + 150 * math.cos(ang_v), oy2 - 150 * math.sin(ang_v), color="#cccccc", sw=1.2, dash="3,3"))

    # Одиничні вектори
    parts.append(arrow(ox2, oy2, u_hat_x, u_hat_y, color=FIELD, sw=2.5))
    parts.append(arrow(ox2, oy2, v_hat_x, v_hat_y, color=POS, sw=2.5))
    parts.append(circle(u_hat_x, u_hat_y, 4, fill=FIELD, stroke="none"))
    parts.append(circle(v_hat_x, v_hat_y, 4, fill=POS, stroke="none"))

    parts.append(text(u_hat_x + 12, u_hat_y + 4, "ū = u / ||u||", size=11, bold=True, color=FIELD))
    parts.append(text(v_hat_x - 10, v_hat_y - 12, "v̄ = v / ||v||", size=11, bold=True, color=POS))

    # Хорда між нормалізованими точками (Евклідова відстань d_E на сфері)
    parts.append(line(u_hat_x, u_hat_y, v_hat_x, v_hat_y, color=POS, sw=2, dash="2,2"))
    mid_chord_x = (u_hat_x + v_hat_x) / 2
    mid_chord_y = (u_hat_y + v_hat_y) / 2
    parts.append(text(mid_chord_x + 15, mid_chord_y - 5, "d_E² = 2(1 - cos θ)", size=10.5, bold=True, color=POS))

    # Формули внизу правої панелі
    parts.append(rect(bx2 + 20, by2 + 250, bw2 - 40, 65, fill="#ffffff", stroke="#c8e6c9", sw=1, rx=4))
    parts.append(text(bx2 + bw2 / 2, by2 + 270, "cos(θ) = (u · v) / (||u|| · ||v||)", size=11.5, bold=True, color=INK))
    parts.append(text(bx2 + bw2 / 2, by2 + 295, "d_cos(u, v) = 1 - cos(θ) ∈ [0, 2]", size=11.5, bold=True, color=FIELD))

    # Підпис під фігурою
    parts.append(text(W / 2, H - 10, "Скалярний добуток задає проєкцію вектора, а нормалізація зводить косинусну відстань до скалярного добутку на одиничній сфері.", size=11.5, italic=True, color=MUTED))

    return "\n".join(parts), W, H


def fig_euclidean_vs_cosine():
    W, H = 840, 390
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 26, "Порівняння Евклідової та Косинусної відстані при зміні масштабу", size=16, bold=True))

    # Ліва панель: Однакові напрямки, різний масштаб
    bx1, by1, bw1, bh1 = 30, 52, 375, 305
    parts.append(rect(bx1, by1, bw1, bh1, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    parts.append(text(bx1 + bw1 / 2, by1 + 22, "Випадок A: Співнапрямлені вектори (θ = 0°)", size=13, bold=True, color=POS))

    ox1, oy1 = bx1 + 50, by1 + 170
    parts.append(arrow(ox1 - 10, oy1, ox1 + 290, oy1, color="#b0b0b0", sw=1))
    parts.append(arrow(ox1, oy1 + 10, ox1, oy1 - 105, color="#b0b0b0", sw=1))

    # Вектор u = (2, 2) в пікселях (55, -55)
    ux1, uy1 = ox1 + 55, oy1 - 55
    parts.append(arrow(ox1, oy1, ux1, uy1, color=FIELD, sw=2.5))
    parts.append(text(ux1 - 15, uy1 - 10, "u = [2, 2]", size=11, bold=True, color=FIELD))

    # Вектор v = (5, 5) в пікселях (140, -140)
    vx1, vy1 = ox1 + 140, oy1 - 140
    parts.append(arrow(ox1, oy1, vx1, vy1, color=POS, sw=2.5))
    parts.append(text(vx1 + 15, vy1 + 15, "v = [5, 5]", size=11, bold=True, color=POS))

    # Лінія евклідової відстані між кінцями u та v
    parts.append(line(ux1, uy1, vx1, vy1, color=POS, sw=2, dash="3,3"))
    parts.append(text((ux1 + vx1) / 2 - 35, (uy1 + vy1) / 2 - 10, "d_E = 4.24", size=11, bold=True, color=POS))

    # Результати метрик для випадку A
    parts.append(rect(bx1 + 20, by1 + 195, bw1 - 40, 95, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(bx1 + bw1 / 2, by1 + 218, "• Евклідова відстань d_E(u, v) = 4.24 (велика)", size=10.5, color=INK))
    parts.append(text(bx1 + bw1 / 2, by1 + 243, "• Косинусна схожість cos(θ) = 1.0 (збіг)", size=10.5, bold=True, color=FIELD))
    parts.append(text(bx1 + bw1 / 2, by1 + 268, "• Косинусна відстань d_cos(u, v) = 0.0 (збіг)", size=10.5, bold=True, color=FIELD))

    # Права панель: Ортогональні вектори
    bx2, by2, bw2, bh2 = 435, 52, 375, 305
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(bx2 + bw2 / 2, by2 + 22, "Випадок B: Ортогональні вектори (θ = 90°)", size=13, bold=True, color=FIELD))

    ox2, oy2 = bx2 + 90, by2 + 165
    parts.append(arrow(ox2 - 30, oy2, ox2 + 250, oy2, color="#b0b0b0", sw=1))
    parts.append(arrow(ox2, oy2 + 20, ox2, oy2 - 100, color="#b0b0b0", sw=1))

    # Вектор u = (3, 1)
    ux2, uy2 = ox2 + 120, oy2 - 40
    parts.append(arrow(ox2, oy2, ux2, uy2, color=FIELD, sw=2.5))
    parts.append(text(ux2 + 8, uy2 + 4, "u = [3, 1]", size=11, bold=True, color=FIELD))

    # Вектор w = (-1, 3) - перпендикулярний
    wx2, wy2 = ox2 - 30, oy2 - 90
    parts.append(arrow(ox2, oy2, wx2, wy2, color=POS, sw=2.5))
    parts.append(text(wx2 - 5, wy2 - 8, "w = [-1, 3]", size=11, bold=True, color=POS))

    # Квадратик прямого кута
    parts.append(polyline([(ox2 + 15 * 0.948, oy2 - 15 * 0.316),
                           (ox2 + 15 * 0.948 - 15 * 0.316, oy2 - 15 * 0.316 - 15 * 0.948),
                           (ox2 - 15 * 0.316, oy2 - 15 * 0.948)], color="#d97706", sw=1.5))
    parts.append(text(ox2 + 15, oy2 - 25, "90°", size=10, bold=True, color="#d97706"))

    # Результати метрик для випадку B
    parts.append(rect(bx2 + 20, by2 + 195, bw2 - 40, 95, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    parts.append(text(bx2 + bw2 / 2, by2 + 218, "• Евклідова відстань d_E(u, w) = 4.47", size=10.5, color=INK))
    parts.append(text(bx2 + bw2 / 2, by2 + 243, "• Косинусна схожість cos(θ) = 0.0 (немає зв'язку)", size=10.5, bold=True, color=POS))
    parts.append(text(bx2 + bw2 / 2, by2 + 268, "• Косинусна відстань d_cos(u, w) = 1.0 (ортогонально)", size=10.5, bold=True, color=POS))

    # Підпис під фігурою
    parts.append(text(W / 2, H - 10, "Евклідова відстань чутлива до абсолютного розміру об'єкта, тоді як косинусна оцінює лише семантичний напрямок.", size=11.5, italic=True, color=MUTED))

    return "\n".join(parts), W, H


def fig_simd_pipeline():
    W, H = 840, 360
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 26, "Апаратна конвеєризація SIMD (AVX2/FMA) для обчислення косинусної відстані", size=16, bold=True))

    # Схема регістрів
    # Блок 1: Вхідні вектори в регістри YMM (256 біт = 8 float)
    y1 = 55
    parts.append(rect(40, y1, 760, 65, fill="#fafafa", stroke="#b0b0b0", sw=1, rx=6))
    parts.append(text(110, y1 + 22, "Регістр YMM0 (u):", size=11, bold=True, color=FIELD))
    parts.append(text(110, y1 + 48, "Регістр YMM1 (v):", size=11, bold=True, color=POS))

    for i in range(8):
        rx = 180 + i * 72
        parts.append(rect(rx, y1 + 8, 66, 22, fill="#e8f4f8", stroke=FIELD, sw=1, rx=3))
        parts.append(text(rx + 33, y1 + 23, "u[%d]" % i, size=10, color=FIELD, bold=True))

        parts.append(rect(rx, y1 + 34, 66, 22, fill="#eefbe8", stroke=POS, sw=1, rx=3))
        parts.append(text(rx + 33, y1 + 49, "v[%d]" % i, size=10, color=POS, bold=True))

    # Блок 2: Паралельні FMA операції (Fused Multiply-Add)
    y2 = 148
    parts.append(rect(40, y2, 760, 75, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(W / 2, y2 + 20, "Паралельне сумування у 3-х SIMD-акумуляторах (vfmadd231ps):", size=12, bold=True, color=INK))

    # 3 паралельних векторних акумулятори
    acc_box_w = 230
    parts.append(rect(60, y2 + 32, acc_box_w, 32, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    parts.append(text(60 + acc_box_w / 2, y2 + 52, "acc_dot += u[i:i+7] * v[i:i+7]", size=10.5, bold=True, color=FIELD))

    parts.append(rect(305, y2 + 32, acc_box_w, 32, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(305 + acc_box_w / 2, y2 + 52, "acc_sq_u += u[i:i+7] * u[i:i+7]", size=10.5, bold=True, color=POS))

    parts.append(rect(550, y2 + 32, acc_box_w, 32, fill="#ffffff", stroke="#d97706", sw=1, rx=4))
    parts.append(text(550 + acc_box_w / 2, y2 + 52, "acc_sq_v += v[i:i+7] * v[i:i+7]", size=10.5, bold=True, color="#d97706"))

    # Стрілка від входу до FMA (з-під блоку 1 до блоку 2)
    parts.append(arrow(420, y1 + 65, 420, y2, color=FIELD, sw=1.5))

    # Блок 3: Горизонтальне згортання та скалярна фіналізація
    y3 = 248
    parts.append(rect(40, y3, 760, 75, fill="#fffaf0", stroke="#d97706", sw=1.5, rx=6))
    parts.append(text(W / 2, y3 + 20, "Горизонтальна редукція та скалярна фіналізація (CPU/ALU):", size=12, bold=True, color=INK))

    parts.append(rect(60, y3 + 32, 210, 32, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    parts.append(text(165, y3 + 52, "dot = hsum(acc_dot)", size=11, bold=True, color=FIELD))

    parts.append(rect(290, y3 + 32, 220, 32, fill="#ffffff", stroke=POS, sw=1, rx=4))
    parts.append(text(400, y3 + 52, "norm_u = sqrt(hsum(acc_sq_u))", size=10.5, bold=True, color=POS))

    parts.append(rect(530, y3 + 32, 250, 32, fill="#ffffff", stroke="#d97706", sw=1, rx=4))
    parts.append(text(655, y3 + 52, "d_cos = 1.0 - dot / (norm_u * norm_v)", size=10.5, bold=True, color="#d97706"))

    # Стрілки від FMA (знизу блоку 2) до редукції (згори блоку 3)
    parts.append(arrow(175, y2 + 64, 165, y3, color=FIELD, sw=1.5))
    parts.append(arrow(420, y2 + 64, 400, y3, color=POS, sw=1.5))
    parts.append(arrow(665, y2 + 64, 655, y3, color="#d97706", sw=1.5))

    # Підпис під фігурою
    parts.append(text(W / 2, H - 10, "Обчислення скалярного добутку та двох норм виконується в один прохід по пам'яті через 8-елементні векторні регістри.", size=11.5, italic=True, color=MUTED))

    return "\n".join(parts), W, H


def main():
    figs = [
        ("cosine-geometry.svg", fig_cosine_geometry),
        ("euclidean-vs-cosine.svg", fig_euclidean_vs_cosine),
        ("simd-pipeline.svg", fig_simd_pipeline),
    ]

    for fname, func in figs:
        path = os.path.join(IMG, fname)
        body, w, h = func()
        render(path, w, h, body)
        print("Згенеровано через render(): %s" % path)


if __name__ == "__main__":
    main()
