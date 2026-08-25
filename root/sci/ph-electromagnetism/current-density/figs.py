# -*- coding: utf-8 -*-
"""Фігури до теми «Щільність струму».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_vector_current_density():
    """Фігура 1: Вектор щільності струму J через елементарну площадку dA."""
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Вектор щільності струму J та потік через поверхню S", size=16, bold=True))

    # Ліва частина: Поверховий елемент dA та кут theta
    f.append(rect(20, 48, 350, 250, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(195, 70, "Елементарний потік струму", size=13, bold=True, color=INK))

    # Лінії струму (паралельні під кутом)
    for y_off in [120, 150, 180, 210, 240]:
        f.append(line(40, y_off, 280, y_off - 30, color="#3b82f6", sw=1.8, dash="4,3"))
        f.append(arrow(40, y_off, 200, y_off - 20, color="#2563eb", sw=2))

    # Площадка dA (похилий еліпс / паралелограм)
    f.append(line(210, 110, 240, 250, color=INK, sw=2.5))
    f.append(line(190, 120, 220, 260, color=INK, sw=2.5))
    f.append(line(190, 120, 210, 110, color=INK, sw=1.5))
    f.append(line(220, 260, 240, 250, color=INK, sw=1.5))
    f.append(rect(195, 155, 40, 60, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=4))
    f.append(text(215, 190, "dA", size=12, bold=True, color="#854d0e"))

    # Вектор нормалі n
    f.append(arrow(215, 185, 310, 155, color="#dc2626", sw=2.2))
    f.append(text(320, 150, "n̂ (нормаль)", size=12, bold=True, color="#dc2626"))

    # Вектор J
    f.append(arrow(215, 185, 300, 185, color="#2563eb", sw=2.5))
    f.append(text(310, 190, "J (вектор струму)", size=12, bold=True, color="#2563eb"))

    # Дуга кута theta
    f.append(text(275, 172, "θ", size=13, bold=True, color="#1e1b4b"))

    # Права частина: Інтеграл потоку струму
    f.append(rect(390, 48, 350, 250, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(565, 70, "Макроскопічний струм I", size=13, bold=True, color=INK))

    f.append(textbox(565, 125, "dI = J · dA · cos(θ)\ndI = J · dA", size=13, bold=True, fill="#eff6ff", stroke="#3b82f6")[0])
    f.append(textbox(565, 210, "I = ∬_S J · dA\n[Одиниця вимірювання J: А/м²]", size=13, bold=True, fill="#f0fdf4", stroke="#22c55e")[0])

    return render(os.path.join(IMG, "vector-current-density.svg"), W, H, *f)


def fig_conductor_constriction():
    """Фігура 2: Концентрація щільності струму у звуженні провідника (ефект стягування)."""
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Розподіл лінії струму та локальне тепловиділення у звуженні", size=16, bold=True))

    f.append(rect(20, 48, W - 40, H - 75, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))

    # Контур провідника зі звуженням у центрі
    f.append(line(50, 90, 220, 90, color=LINE, sw=2.2))
    f.append(line(220, 90, 340, 145, color=LINE, sw=2.2))
    f.append(line(340, 145, 420, 145, color=LINE, sw=2.2))
    f.append(line(420, 145, 540, 90, color=LINE, sw=2.2))
    f.append(line(540, 90, 710, 90, color=LINE, sw=2.2))

    f.append(line(50, 270, 220, 270, color=LINE, sw=2.2))
    f.append(line(220, 270, 340, 215, color=LINE, sw=2.2))
    f.append(line(340, 215, 420, 215, color=LINE, sw=2.2))
    f.append(line(420, 215, 540, 270, color=LINE, sw=2.2))
    f.append(line(540, 270, 710, 270, color=LINE, sw=2.2))

    y_starts = [105, 135, 165, 195, 225, 255]
    y_mids   = [152, 163, 174, 186, 197, 208]
    
    for ys, ym in zip(y_starts, y_mids):
        f.append(line(50, ys, 220, ys, color="#2563eb", sw=1.6))
        f.append(line(220, ys, 340, ym, color="#2563eb", sw=1.8))
        f.append(line(340, ym, 420, ym, color="#dc2626", sw=2.4))
        f.append(line(420, ym, 540, ys, color="#2563eb", sw=1.8))
        f.append(line(540, ys, 710, ys, color="#2563eb", sw=1.6))
        f.append(arrow(120, ys, 170, ys, color="#2563eb", sw=1.8))
        f.append(arrow(360, ym, 400, ym, color="#dc2626", sw=2.2))

    f.append(rect(335, 140, 90, 80, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=6))
    f.append(text(380, 128, "Зона перегріву (Hotspot)", size=11, bold=True, color="#dc2626"))
    f.append(text(380, 238, "w = J² / σ [Вт/м³]", size=11, bold=True, color="#b91c1c"))

    f.append(line(130, 90, 130, 270, color=MUTED, sw=1.2, dash="2,2"))
    f.append(text(130, 78, "Площа A₁ (низька J₁)", size=11, bold=True, color=INK))

    f.append(line(380, 145, 380, 215, color=MUTED, sw=1.2, dash="2,2"))
    f.append(text(380, 290, "Площа A₂ << A₁ ⇒ J₂ >> J₁", size=12, bold=True, color="#dc2626"))

    return render(os.path.join(IMG, "conductor-constriction.svg"), W, H, *f)


def fig_skin_effect_profile():
    """Фігура 3: Скіновий ефект — розподіл щільності струму по перерізу провідника при AC."""
    W, H = 760, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Виштовхування струму на поверхню провідника (Скіновий ефект)", size=16, bold=True))

    f.append(rect(20, 48, 330, 280, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(185, 70, "Переріз провідника", size=13, bold=True, color=INK))

    cx, cy = 185, 185
    r_outer = 90
    r_inner = 55

    f.append(circle(cx, cy, r_outer, fill="#fef3c7", stroke="#d97706", sw=2))
    f.append(circle(cx, cy, r_outer, fill="#3b82f6", stroke="#1d4ed8", sw=2))
    f.append(circle(cx, cy, r_inner, fill="#f8fafc", stroke="#94a3b8", sw=1.8))

    f.append(text(cx, cy - 16, "Ядро:", size=11, bold=True, color=MUTED))
    f.append(text(cx, cy + 12, "J ≈ 0", size=12, bold=True, color=MUTED))

    f.append(line(cx + 25, cy, cx + r_outer, cy, color=INK, sw=1.2))
    f.append(text(cx + 30, cy - 8, "R", size=11, bold=True))

    f.append(line(cx + r_inner, cy + 30, cx + r_outer, cy + 30, color="#dc2626", sw=2))
    f.append(text(cx + (r_inner + r_outer) / 2, cy + 48, "δ (скіношар)", size=11, bold=True, color="#dc2626"))

    f.append(rect(370, 48, 370, 280, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(555, 70, "Профіль щільності струму J(r)", size=13, bold=True, color=INK))

    ox, oy = 410, 270
    ax_w, ax_h = 300, 180

    f.append(line(ox, oy, ox + ax_w, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, oy - ax_h, color=MUTED, sw=1.4))
    f.append(text(ox + ax_w + 10, oy + 4, "r", size=12, bold=True, color=MUTED))
    f.append(text(ox - 15, oy - ax_h + 10, "J", size=12, bold=True, color=MUTED))

    r0_x = ox + ax_w / 2
    f.append(line(r0_x, oy, r0_x, oy - ax_h, color="#cbd5e1", sw=1, dash="2,2"))
    f.append(text(r0_x, oy + 16, "r=0 (центр)", size=10, color=MUTED))

    rm_x = ox + 30
    rp_x = ox + ax_w - 30
    f.append(line(rm_x, oy, rm_x, oy - ax_h, color="#e2e8f0", sw=1, dash="2,2"))
    f.append(line(rp_x, oy, rp_x, oy - ax_h, color="#e2e8f0", sw=1, dash="2,2"))
    f.append(text(rm_x, oy + 16, "-R", size=10, bold=True))
    f.append(text(rp_x, oy + 16, "+R", size=10, bold=True))

    pts = []
    n_pts = 40
    j_max_y = oy - ax_h + 20

    for i in range(n_pts + 1):
        frac = i / n_pts
        rx = rm_x + frac * (rp_x - rm_x)
        dist_surf = min(frac, 1.0 - frac) * 2.0
        val = 2.718 ** (-3.5 * dist_surf)
        jy = oy - (val * (ax_h - 40) + 15)
        pts.append((rx, jy))

    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color="#2563eb", sw=2.5))

    f.append(text(rp_x - 15, j_max_y - 8, "J₀ (поверхня)", size=11, bold=True, color="#2563eb"))

    f.append(textbox(555, 305, "δ = √( ρ / [π · f · μ] )", size=11, bold=True, fill="#f0f9ff", stroke="#0284c7")[0])

    return render(os.path.join(IMG, "skin-effect-profile.svg"), W, H, *f)


def fig_electromigration_voids():
    """Фігура 4: Мікроскопічний механізм електроміграції в кристалічній ґратці."""
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Фізика електроміграції: електронний вітер та деградація провідника", size=16, bold=True))

    f.append(rect(20, 48, W - 40, H - 75, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))

    f.append(rect(40, 70, 680, 40, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    f.append(arrow(60, 90, 640, 90, color="#2563eb", sw=2.5))
    f.append(text(350, 82, "Потік електронного вітру (High Current Density J > 10⁵ А/см²)", size=12, bold=True, color="#1e40af"))

    f.append(rect(40, 125, 680, 120, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

    f.append(rect(210, 145, 80, 80, fill="#fef2f2", stroke="#ef4444", sw=2, rx=4))
    f.append(text(250, 185, "Порожнина\n(Void)", size=10, bold=True, color="#dc2626"))

    f.append(rect(495, 135, 80, 100, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=4))
    f.append(text(535, 185, "Пагорб\n(Hillock)", size=10, bold=True, color="#15803d"))

    grid_x = [70, 120, 170, 310, 360, 410, 460, 610, 660]
    grid_y = [150, 185, 220]

    for gx in grid_x:
        for gy in grid_y:
            f.append(circle(gx, gy, 10, fill="#fde047", stroke="#d97706", sw=1.5))
            f.append(text(gx, gy + 3.5, "M⁺", size=9, bold=True, color="#78350f"))

    f.append(arrow(290, 116, 480, 116, color="#d97706", sw=2.2))
    f.append(text(385, 112, "Перенос іонів металу", size=11, bold=True, color="#b45309"))

    f.append(text(W / 2, 298, "Формула Блека: MTTF = (A / Jⁿ) · exp(Eₐ / [k_B · T]), де n ≈ 1...2", size=12, bold=True, color=INK))

    return render(os.path.join(IMG, "electromigration-voids.svg"), W, H, *f)


if __name__ == '__main__':
    fig_vector_current_density()
    fig_conductor_constriction()
    fig_skin_effect_profile()
    fig_electromigration_voids()
    print("Всі 4 фігури успішно згенеровано у ./img/")
