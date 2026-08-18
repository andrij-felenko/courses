# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AIR   = "#ffffff"   # середовище 1 (менш щільне)
GLASS = "#eaf2fb"   # середовище 2 (більш щільне)

def ang(a):
    return math.radians(a)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрія закону Снелла (заломлення на межі двох середовищ)
# ═══════════════════════════════════════════════════════════════════════════
def fig_snell_geometry():
    W, H = 680, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Заломлення світлового променя на межі ефір/скло', 16, INK, 'middle', bold=True))

    py = 190          # рівень плоскої межі
    cx = 320          # точка падіння

    # Нижня частина (середовище 2, оптично більш щільне)
    f.append(rect(20, py, W - 40, H - py - 50, fill=GLASS, stroke='none', sw=0, rx=0))

    # Межа розділу середовищ
    f.append(line(20, py, W - 40, py, color=INK, sw=2))

    # Нормаль до межі (перпендикуляр)
    f.append(line(cx, py - 130, cx, py + 130, color=MUTED, sw=1.5, dash='5,4'))

    # Кути: n1 = 1.0 (повітря), n2 = 1.5 (скло), theta1 = 50°
    theta1_deg = 50.0
    n1, n2 = 1.0, 1.5
    ti = ang(theta1_deg)
    tr = math.asin((n1 / n2) * math.sin(ti))
    theta2_deg = math.degrees(tr)   # ≈ 30.7°

    L1 = 120
    L2 = 120

    # Падаючий промінь (у середовищі 1)
    ix = cx - L1 * math.sin(ti)
    iy = py - L1 * math.cos(ti)
    f.append(arrow(ix, iy, cx, py, color=POS, sw=2.5))

    # Заломлений промінь (у середовищі 2, відхиляється БЛИЖЧЕ до нормалі)
    tx = cx + L2 * math.sin(tr)
    ty = py + L2 * math.cos(tr)
    f.append(arrow(cx, py, tx, ty, color=FIELD, sw=2.5))

    # Відбитий промінь (часткове відбиття)
    rx = cx + L1 * math.sin(ti)
    ry = py - L1 * math.cos(ti)
    f.append(arrow(cx, py, rx, ry, color=MUTED, sw=1.2))

    # Підписи променів
    f.append(text(ix - 15, iy - 5, 'Падаючий промінь', 12, POS, 'end', bold=True))
    f.append(text(tx + 15, ty + 10, 'Заломлений промінь', 12, FIELD, 'start', bold=True))
    f.append(text(rx + 10, ry - 5, 'Частково відбитий промінь', 10, MUTED, 'start'))

    # Позначки кутів
    # Кут падіння theta1
    f.append(text(cx - 24, py - 45, 'θ₁ = 50°', 12, POS, 'middle', bold=True))
    # Кут заломлення theta2
    f.append(text(cx + 26, py + 45, 'θ₂ = 30.7°', 12, FIELD, 'middle', bold=True))

    # Позначки нормалі та середовищ
    f.append(text(cx + 8, py - 120, 'Нормаль N', 11, MUTED, 'start'))
    f.append(text(40, py - 20, 'Середовище 1: n₁ (повітря, v₁ = c/n₁)', 12, INK, 'start'))
    f.append(text(40, py + 25, 'Середовище 2: n₂ > n₁ (скло, v₂ = c/n₂ < v₁)', 12, INK, 'start'))

    # Формула закону Снелла внизу
    f.append(text(W / 2, H - 20, 'Закон Снелла:  n₁ · sin(θ₁) = n₂ · sin(θ₂)', 14, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'snell-geometry.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Векторна форма заломлення у 3D-просторі (для Ray Tracing)
# ═══════════════════════════════════════════════════════════════════════════
def fig_vector_refraction():
    W, H = 680, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Векторне розкладання заломленого променя (3D Ray Tracing)', 16, INK, 'middle', bold=True))

    py = 170
    cx = 320

    # Нижня частина (середовище 2)
    f.append(rect(20, py, W - 40, H - py - 50, fill=GLASS, stroke='none', sw=0, rx=0))

    # Межа
    f.append(line(20, py, W - 40, py, color=INK, sw=2))

    # Вектор нормалі N (напрямлений ВГОРУ проти падіння)
    f.append(arrow(cx, py, cx, py - 110, color=NEG, sw=2.5))
    f.append(text(cx + 10, py - 95, 'Нормаль N', 12, NEG, 'start', bold=True))

    # Вектор падаючого променя I (напрямлений ДО точки падіння)
    theta1_deg = 45.0
    ti = ang(theta1_deg)
    L = 110
    ix = cx - L * math.sin(ti)
    iy = py - L * math.cos(ti)
    f.append(arrow(ix, iy, cx, py, color=POS, sw=2.5))
    f.append(text(ix - 10, iy - 5, 'Вектор падіння I', 12, POS, 'end', bold=True))

    # Заломлений вектор T
    n1, n2 = 1.0, 1.4
    eta = n1 / n2
    cos_i = math.cos(ti)
    sin_t2 = (eta**2) * (1.0 - cos_i**2)
    cos_t = math.sqrt(1.0 - sin_t2)

    tr = math.asin(eta * math.sin(ti))
    tx = cx + L * math.sin(tr)
    ty = py + L * math.cos(tr)

    # Паралельна до поверхні складова T_parallel
    f.append(arrow(cx, py, tx, py, color=MUTED, sw=1.5))
    f.append(text(cx + (tx - cx)/2, py - 8, 'η · (I + cos(θ₁)·N)', 10, MUTED, 'middle'))

    # Нормальна складова T_perpendicular
    f.append(arrow(tx, py, tx, ty, color=MUTED, sw=1.5))
    f.append(text(tx + 8, py + (ty - py)/2, '-cos(θ₂)·N', 10, MUTED, 'start'))

    # Результуючий вектор T
    f.append(arrow(cx, py, tx, ty, color=FIELD, sw=2.8))
    f.append(text(tx + 12, ty + 12, 'Заломлений вектор T', 12, FIELD, 'start', bold=True))

    # Головна формула під супровід
    f.append(text(W / 2, H - 22, 'T = η·I + (η·cos(θ₁) - cos(θ₂))·N,   де η = n₁ / n₂', 13, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'vector-refraction.svg'), W, H, *f)


if __name__ == '__main__':
    fig_snell_geometry()
    fig_vector_refraction()
    print("Figures generated successfully!")
