# -*- coding: utf-8 -*-
"""Фігури до теми «Сила Лоренца».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"


# ── Фігура 1: Напрям сили Лоренца для позитивного і негативного заряду ────────
def fig_lorentz_direction():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    midx = W / 2
    f.append(line(midx, 45, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- Ліва частина: Позитивний заряд (+q) ---
    f.append(fitbox(20, 48, midx - 40, 26, "Позитивний заряд (+q)", size=13, bold=True, color=COLOR_BLUE, fill="#eef6ff", stroke=COLOR_BLUE))

    # Магнітне поле B (спрямоване від нас у дошку, хрестики)
    f.append(text(190, 95, "Магнітне поле B (від нас)", size=11, color="#7f8c8d", anchor="middle"))
    for row in range(3):
        for col in range(4):
            cx = 70 + col * 80
            cy = 120 + row * 55
            f.append(circle(cx, cy, 9, fill="none", stroke="#bdc3c7", sw=1.2))
            f.append(line(cx - 4, cy - 4, cx + 4, cy + 4, color="#7f8c8d", sw=1.4))
            f.append(line(cx - 4, cy + 4, cx + 4, cy - 4, color="#7f8c8d", sw=1.4))

    # Заряд +q у центрі
    px, py = 190, 175
    f.append(circle(px, py, 16, fill="#e8f8f5", stroke=COLOR_GREEN, sw=2))
    f.append(text(px, py + 4, "+q", size=13, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Вектор швидкості v (праворуч)
    f.append(arrow(px + 16, py, px + 105, py, color=COLOR_BLUE, sw=2.5))
    f.append(text(px + 60, py - 10, "v (швидкість)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Вектор сили F (вгору)
    f.append(arrow(px, py - 16, px, py - 95, color=COLOR_RED, sw=2.5))
    f.append(text(px + 10, py - 55, "F = +q·(v × B)", size=11, bold=True, color=COLOR_RED, anchor="start"))

    # Підпис правила правої руки
    f.append(fitbox(25, 280, midx - 50, 55, "Правило правої руки: долоня проти B,\nпальці за v → великий палець показує F", size=11, color=COLOR_DARK, fill="#fff8e7", stroke="#f39c12"))

    # --- Права частина: Негативний заряд (-e, електрон) ---
    f.append(fitbox(midx + 20, 48, midx - 40, 26, "Негативний заряд (-e, електрон)", size=13, bold=True, color=COLOR_RED, fill="#fdeea9", stroke=COLOR_ORANGE))

    # Магнітне поле B (ті ж хрестики)
    f.append(text(midx + 190, 95, "Магнітне поле B (від нас)", size=11, color="#7f8c8d", anchor="middle"))
    for row in range(3):
        for col in range(4):
            cx = midx + 70 + col * 80
            cy = 120 + row * 55
            f.append(circle(cx, cy, 9, fill="none", stroke="#bdc3c7", sw=1.2))
            f.append(line(cx - 4, cy - 4, cx + 4, cy + 4, color="#7f8c8d", sw=1.4))
            f.append(line(cx - 4, cy + 4, cx + 4, cy - 4, color="#7f8c8d", sw=1.4))

    # Електрон -e
    ex, ey = midx + 190, 175
    f.append(circle(ex, ey, 16, fill="#fadbd8", stroke=COLOR_RED, sw=2))
    f.append(text(ex, ey + 4, "-e", size=13, bold=True, color=COLOR_RED, anchor="middle"))

    # Вектор швидкості v (праворуч)
    f.append(arrow(ex + 16, ey, ex + 105, ey, color=COLOR_BLUE, sw=2.5))
    f.append(text(ex + 60, ey - 10, "v (швидкість)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Вектор сили F (вниз, оскільки q < 0!)
    f.append(arrow(ex, ey + 16, ex, ey + 95, color=COLOR_PURPLE, sw=2.5))
    f.append(text(ex + 10, ey + 55, "F = -e·(v × B)", size=11, bold=True, color=COLOR_PURPLE, anchor="start"))

    # Пояснення інверсії напряму
    f.append(fitbox(midx + 25, 280, midx - 50, 55, "Через знак мінус (q = -e) сила\nспрямована ПРОТИЛЕЖНО до (v × B)", size=11, color=COLOR_DARK, fill="#fcedec", stroke=COLOR_RED))

    render(os.path.join(IMG, "lorentz-direction.svg"), W, H, *f, title="Напрям сили Лоренца: F = q · (v × B)")


# ── Фігура 2: Рух у магнітному полі: коло та спіраль ──────────────────────────
def fig_cyclotron_helical():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    midx = W / 2
    f.append(line(midx, 45, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- Ліва частина: Кругова орбіта (v ⊥ B) ---
    f.append(fitbox(20, 48, midx - 40, 26, "Перпендикулярне поле (v ⊥ B) → Коло", size=12, bold=True, color=COLOR_BLUE, fill="#eef6ff", stroke=COLOR_BLUE))

    # Поле B від нас
    for row in range(3):
        for col in range(3):
            cx = 75 + col * 115
            cy = 110 + row * 65
            f.append(circle(cx, cy, 8, fill="none", stroke="#cbd5e1", sw=1.2))
            f.append(line(cx - 4, cy - 4, cx + 4, cy + 4, color="#94a3b8", sw=1.2))
            f.append(line(cx - 4, cy + 4, cx + 4, cy - 4, color="#94a3b8", sw=1.2))

    # Кругова траєкторія
    ox, oy = 190, 175
    r_orbit = 60
    f.append(f'<circle cx="{ox}" cy="{oy}" r="{r_orbit}" fill="none" stroke="{COLOR_BLUE}" stroke-width="2" stroke-dasharray="4,3" />')

    # Заряд на колі
    qx = ox + r_orbit
    qy = oy
    f.append(circle(qx, qy, 10, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.8))
    f.append(text(qx, qy + 3, "+q", size=10, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Вектор швидкості v (вгору)
    f.append(arrow(qx, qy, qx, qy - 42, color=COLOR_BLUE, sw=2))
    f.append(text(qx + 8, qy - 20, "v", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    # Доцентрова сила F (до центру орбіти)
    f.append(arrow(qx, qy, qx - 42, qy, color=COLOR_RED, sw=2))
    f.append(text(qx - 25, qy - 10, "F", size=11, bold=True, color=COLOR_RED, anchor="middle"))

    # Радіус r_c
    f.append(line(ox, oy, ox + r_orbit, oy, color=COLOR_DARK, sw=1.2, dash="2,2"))
    f.append(text(ox + 25, oy + 14, "r = m·v / (q·B)", size=10, bold=True, color=COLOR_DARK, anchor="middle"))

    f.append(fitbox(20, 268, midx - 40, 68, "Сила Лоренца виконує роль доцентрової сили:\nq·v·B = m·v² / r  ⇒  r = m·v / (q·B)\nЧастота обертання: ω = q·B / m", size=11, color=COLOR_DARK, fill="#f8fafc", stroke="#cbd5e1"))

    # --- Права частина: Спіральний рух (v під кутом до B) ---
    f.append(fitbox(midx + 20, 48, midx - 40, 26, "Косий рух (v під кутом θ) → Спіраль", size=12, bold=True, color=COLOR_PURPLE, fill="#f5f0bb", stroke=COLOR_PURPLE))

    # Силові лінії поля B (горизонтальні праворуч)
    f.append(arrow(midx + 35, 110, midx + 330, 110, color="#94a3b8", sw=1.5))
    f.append(arrow(midx + 35, 175, midx + 330, 175, color="#94a3b8", sw=1.5))
    f.append(arrow(midx + 35, 240, midx + 330, 240, color="#94a3b8", sw=1.5))
    f.append(text(midx + 335, 175, "B", size=13, bold=True, color="#64748b", anchor="start"))

    # Спіральна крива
    pts = []
    for t in range(0, 260, 5):
        x = midx + 45 + t
        y = 175 + 40 * float(math.sin(t * 0.1))
        pts.append((x, y))

    path_str = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join([f"L {p[0]:.1f} {p[1]:.1f}" for p in pts[1:]])
    f.append(f'<path d="{path_str}" fill="none" stroke="{COLOR_PURPLE}" stroke-width="2.5" />')

    # Заряд на спіралі
    zx, zy = pts[25][0], pts[25][1]
    f.append(circle(zx, zy, 9, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.8))
    f.append(text(zx, zy + 3, "+q", size=9, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Розкладання швидкості
    f.append(arrow(zx, zy, zx + 35, zy - 25, color=COLOR_BLUE, sw=2))
    f.append(text(zx + 22, zy - 27, "v", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    f.append(fitbox(midx + 20, 268, midx - 40, 68, "Поздовжня v∥ зберігається (сила = 0),\nпоперечна v⊥ змушує кружляти.\nРезультат — спіральна траєкторія (гвинтова лінія)", size=11, color=COLOR_DARK, fill="#f8fafc", stroke="#cbd5e1"))

    render(os.path.join(IMG, "cyclotron-helical.svg"), W, H, *f, title="Рух заряду у магнітному полі: циклотронний кругообіг та спіраль")


# ── Фігура 3: Ефект Холла у провіднику / напівпровіднику ─────────────────────
def fig_hall_effect():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Пластина (провідний брусок)
    bx, by, bw, bh = 140, 100, 460, 140
    f.append(rect(bx, by, bw, bh, fill="#f1f5f9", stroke="#64748b", sw=2, rx=6))
    f.append(text(bx + 15, by + 20, "Пластина з носіями заряду", size=11, color="#64748b", anchor="start"))

    # Зовнішній струм I (зліва направо)
    f.append(arrow(40, by + bh / 2, bx - 10, by + bh / 2, color=COLOR_BLUE, sw=3))
    f.append(text(75, by + bh / 2 - 12, "Струм I", size=12, bold=True, color=COLOR_BLUE, anchor="middle"))

    f.append(arrow(bx + bw + 10, by + bh / 2, bx + bw + 70, by + bh / 2, color=COLOR_BLUE, sw=3))
    f.append(text(bx + bw + 40, by + bh / 2 - 12, "Струм I", size=12, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Магнітне поле B (від нас, хрестики)
    for cx in range(bx + 60, bx + bw - 40, 70):
        for cy in (by + 45, by + 95):
            f.append(circle(cx, cy, 7, fill="none", stroke="#cbd5e1", sw=1))
            f.append(line(cx - 3, cy - 3, cx + 3, cy + 3, color="#94a3b8", sw=1))
            f.append(line(cx - 3, cy + 3, cx + 3, cy - 3, color="#94a3b8", sw=1))
    f.append(text(bx + bw / 2, by + 22, "Магнітне поле B (від нас)", size=11, color="#7f8c8d", anchor="middle"))

    # Негативний заряд на нижній грані:
    for ex in range(bx + 70, bx + bw - 50, 60):
        f.append(circle(ex, by + bh - 18, 9, fill="#fadbd8", stroke=COLOR_RED, sw=1.5))
        f.append(text(ex, by + bh - 15, "-", size=13, bold=True, color=COLOR_RED, anchor="middle"))

    # Позитивний заряд на верхній грані:
    for px in range(bx + 70, bx + bw - 50, 60):
        f.append(circle(px, by + 42, 9, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5))
        f.append(text(px, by + 45, "+", size=11, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Рухомий електрон у центрі
    mex, mey = bx + bw / 2, by + bh / 2 + 5
    f.append(circle(mex, mey, 12, fill="#fadbd8", stroke=COLOR_RED, sw=1.8))
    f.append(text(mex, mey + 4, "-e", size=10, bold=True, color=COLOR_RED, anchor="middle"))

    # Вектор дрейфу v_d (вліво)
    f.append(arrow(mex - 12, mey, mex - 60, mey, color=COLOR_BLUE, sw=2))
    f.append(text(mex - 45, mey - 10, "v_дрейфу", size=10, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Сила магнітна F_M (вниз)
    f.append(arrow(mex, mey + 12, mex, mey + 42, color=COLOR_PURPLE, sw=2))
    f.append(text(mex + 10, mey + 30, "F_магн", size=10, bold=True, color=COLOR_PURPLE, anchor="start"))

    # Поперечне електричне поле E_H та сила F_E (вгору)
    f.append(arrow(mex, mey - 12, mex, mey - 42, color=COLOR_GREEN, sw=2))
    f.append(text(mex + 10, mey - 25, "F_ел = e·E_H", size=10, bold=True, color=COLOR_GREEN, anchor="start"))

    f.append(fitbox(20, 275, W - 40, 65, "Напруга Холла: V_H = (I · B) / (n · q · d)\nСила Лоренца зносить носії вбік, поки виникле поперечне поле E_H не зрівноважить її (F_ел = F_магн).\nВеличина V_H прямо пропорційна індукції поля B і струму I.", size=11, color=COLOR_DARK, fill="#fff8e7", stroke="#f39c12"))

    render(os.path.join(IMG, "hall-effect.svg"), W, H, *f, title="Механізм ефекту Холла: розділення зарядів силою Лоренца")


# ── Фігура 4: Селектор швидкостей у схрещених полях E та B ─────────────────────
def fig_velocity_selector():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Обкладки конденсатора (поперечне Е-поле)
    f.append(rect(140, 65, 480, 22, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    f.append(text(380, 80, "Верхня пластина (+)", size=11, bold=True, color=COLOR_RED, anchor="middle"))

    f.append(rect(140, 225, 480, 22, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    f.append(text(380, 240, "Нижня пластина (-)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Силові лінії електричного поля E (згори вниз)
    for ex in range(180, 600, 80):
        f.append(arrow(ex, 90, ex, 220, color="#cbd5e1", sw=1.2))
    f.append(text(610, 140, "Електричне поле E", size=11, color="#64748b", anchor="start"))

    # Магнітне поле B (від нас, хрестики)
    for bx in range(200, 580, 90):
        for by in (120, 185):
            f.append(circle(bx, by, 7, fill="none", stroke="#e2e8f0", sw=1))
            f.append(line(bx - 3, by - 3, bx + 3, by + 3, color="#94a3b8", sw=1))
            f.append(line(bx - 3, by + 3, bx + 3, by - 3, color="#94a3b8", sw=1))
    f.append(text(610, 185, "Магнітне поле B (від нас)", size=11, color="#7f8c8d", anchor="start"))

    # Вхідна коліматорна щілина
    f.append(rect(60, 50, 18, 90, fill="#475569", stroke="none", sw=0))
    f.append(rect(60, 170, 18, 90, fill="#475569", stroke="none", sw=0))

    # Вихідна коліматорна щілина
    f.append(rect(680, 50, 18, 90, fill="#475569", stroke="none", sw=0))
    f.append(rect(680, 170, 18, 90, fill="#475569", stroke="none", sw=0))

    # Траєкторія прямолінійного прольоту (v = E/B)
    f.append(line(78, 155, 680, 155, color=COLOR_GREEN, sw=2.5, dash="6,3"))

    # Частка з влучною швидкістю v = E/B
    qx, qy = 380, 155
    f.append(circle(qx, qy, 13, fill="#e8f8f5", stroke=COLOR_GREEN, sw=2))
    f.append(text(qx, qy + 4, "+q", size=11, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Сила електрична F_E (вниз, до мінусової пластини)
    f.append(arrow(qx, qy + 13, qx, qy + 55, color=COLOR_BLUE, sw=2.2))
    f.append(text(qx + 10, qy + 38, "F_E = q·E", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    # Сила магнітна F_B (вгору)
    f.append(arrow(qx, qy - 13, qx, qy - 55, color=COLOR_RED, sw=2.2))
    f.append(text(qx + 10, qy - 38, "F_B = q·v·B", size=11, bold=True, color=COLOR_RED, anchor="start"))

    f.append(fitbox(20, 275, W - 40, 65, "Умова прямолінійного прольоту без відхилення:\nF_B = F_E  ⇒  q · v · B = q · E  ⇒  v = E / B\nПріоритет: проходять ЛИШЕ частинки з точною швидкістю v = E/B, незалежно від їхньої маси та заряду!", size=11, color=COLOR_DARK, fill="#f8fafc", stroke="#cbd5e1"))

    render(os.path.join(IMG, "velocity-selector.svg"), W, H, *f, title="Селектор швидкостей Віна: рівновага сил q·E = q·v·B")


if __name__ == "__main__":
    print("Генерація SVG фігур для теми 'Сила Лоренца'...")
    fig_lorentz_direction()
    fig_cyclotron_helical()
    fig_hall_effect()
    fig_velocity_selector()
    print("Успішно згенеровано 4 фігури в ./img/")
