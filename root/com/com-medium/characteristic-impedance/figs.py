# -*- coding: utf-8 -*-
"""Фігури до теми «Характеристичний імпеданс».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_lumped_model():
    """Фігура 1: Нескінченно малий елемент лінії передачі dx (модель Телеграфіста)."""
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Модель лінії передачі: нескінченно малий елемент dx", size=16, bold=True))

    # Рамка для схеми
    f.append(rect(20, 48, W - 40, H - 76, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Основний верхній провідник (лінія сигнальна)
    f.append(line(50, 100, 150, 100, color=LINE, sw=2))
    
    # Послідовний опір R dx
    f.append(rect(150, 85, 70, 30, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(185, 105, "R·dx", size=12, bold=True))

    f.append(line(220, 100, 270, 100, color=LINE, sw=2))

    # Послідовна індуктивність L dx
    f.append(rect(270, 85, 70, 30, fill="#eef4ff", stroke="#2563eb", sw=1.8, rx=4))
    f.append(text(305, 105, "L·dx", size=12, bold=True, color="#1e40af"))

    f.append(line(340, 100, 500, 100, color=LINE, sw=2))

    # Поперечна паралельна гілка у вузлі x = 440
    f.append(circle(440, 100, 4, fill=INK, stroke='none'))

    # Паралельна провідність G dx
    f.append(line(440, 100, 440, 130, color=LINE, sw=2))
    f.append(rect(410, 130, 60, 30, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(440, 150, "G·dx", size=12, bold=True))
    f.append(line(440, 160, 440, 180, color=LINE, sw=2))

    # Вузол між G та C
    f.append(line(440, 180, 440, 195, color=LINE, sw=2))

    # Паралельна ємність C dx
    f.append(line(415, 195, 465, 195, color=LINE, sw=2.5))
    f.append(line(415, 205, 465, 205, color=LINE, sw=2.5))
    f.append(text(490, 203, "C·dx", size=12, bold=True, color="#059669"))
    f.append(line(440, 205, 440, 240, color=LINE, sw=2))

    # Нижній провідник (земля / зворотний шлях)
    f.append(line(50, 240, 700, 240, color=LINE, sw=2))
    f.append(circle(440, 240, 4, fill=INK, stroke='none'))

    # Стрілки та напруги/струми
    f.append(arrow(70, 75, 120, 75, color="#2563eb", sw=2))
    f.append(text(95, 62, "I(x, t)", size=12, bold=True, color="#2563eb"))

    f.append(arrow(60, 115, 60, 225, color="#dc2626", sw=1.6))
    f.append(text(15, 170, "V(x, t)", size=12, bold=True, color="#dc2626", anchor="start"))

    # Вихідні V(x+dx,t), I(x+dx,t)
    f.append(arrow(530, 75, 590, 75, color="#2563eb", sw=2))
    f.append(text(560, 62, "I(x+dx, t)", size=12, bold=True, color="#2563eb"))

    f.append(arrow(680, 115, 680, 225, color="#dc2626", sw=1.6))
    f.append(text(690, 170, "V(x+dx, t)", size=12, bold=True, color="#dc2626", anchor="start"))

    # Позначка довжини dx
    f.append(line(150, 265, 500, 265, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(325, 280, "довжина сегмента = dx", size=12, color=MUTED))

    return render(os.path.join(IMG, "tline-lumped-model.svg"), W, H, *f)


def fig_reflection_waveforms():
    """Фігура 2: Хвилі відбиття при різних типах навантаження Z_L."""
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Напруга на кінці лінії при різних навантаженнях Z_L", size=16, bold=True))

    cases = [
        ("Узгоджене: Z_L = Z_0 (Γ = 0)", "Немає відбиття: напруга дорівнює V₀", "#16a34a", 1),
        ("Холостий хід: Z_L = ∞ (Γ = +1)", "Повне відбиття у фазі: напруга подвоюється 2V₀", "#2563eb", 2),
        ("Коротке замикання: Z_L = 0 (Γ = −1)", "Відбиття в протифазі: напруга падає до 0", "#dc2626", 3),
        ("Ємнісне: Z_L = 1 / (j ω C)", "Експоненційне наростання заряду ємності", "#d97706", 4)
    ]

    panel_w = 340
    panel_h = 140
    coords = [(30, 48), (390, 48), (30, 215), (390, 215)]

    for idx, (title, desc, accent_clr, c_type) in enumerate(cases):
        x, y = coords[idx]
        f.append(rect(x, y, panel_w, panel_h, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
        f.append(text(x + 12, y + 20, title, size=12, bold=True, color=INK, anchor="start"))

        # Осі координат
        ox, oy = x + 35, y + panel_h - 28
        ax_w, ax_h = panel_w - 55, panel_h - 55
        f.append(line(ox, oy, ox + ax_w, oy, color=MUTED, sw=1.2))
        f.append(line(ox, oy, ox, y + 30, color=MUTED, sw=1.2))
        f.append(text(ox + ax_w, oy + 14, "t", size=11, color=MUTED))
        f.append(text(ox - 10, y + 35, "V", size=11, color=MUTED))

        # Рівень падаючої хвилі V0
        v0_y = oy - ax_h * 0.45
        f.append(line(ox, v0_y, ox + ax_w, v0_y, color="#cbd5e1", sw=1, dash="2,2"))
        f.append(text(ox - 14, v0_y + 4, "V₀", size=10, color=MUTED))

        # Час приходу хвилі t_delay
        td_x = ox + ax_w * 0.35
        f.append(line(td_x, oy, td_x, y + 30, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(td_x, oy + 14, "t_d", size=10, color=MUTED))

        # Форма хвилі
        pts = []
        if c_type == 1:
            pts = [(ox, oy), (td_x, oy), (td_x, v0_y), (ox + ax_w, v0_y)]
        elif c_type == 2:
            v2_y = oy - ax_h * 0.85
            pts = [(ox, oy), (td_x, oy), (td_x, v0_y), (td_x, v2_y), (ox + ax_w, v2_y)]
            f.append(text(ox - 16, v2_y + 4, "2V₀", size=10, color=MUTED))
        elif c_type == 3:
            pts = [(ox, oy), (td_x, oy), (td_x, v0_y), (td_x, oy), (ox + ax_w, oy)]
        elif c_type == 4:
            v2_y = oy - ax_h * 0.85
            pts = [(ox, oy), (td_x, oy), (td_x, v0_y)]
            n_steps = 15
            for s in range(n_steps + 1):
                frac = s / n_steps
                cx = td_x + frac * (ax_w * 0.6)
                cy = v0_y - (v2_y - v0_y) * (1 - 2.718 ** (-3 * frac))
                pts.append((cx, cy))

        for i in range(len(pts) - 1):
            f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=accent_clr, sw=2.2))

        f.append(text(x + 12, y + panel_h - 10, desc, size=10, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "reflection-waveforms.svg"), W, H, *f)


def fig_geometries_cross_section():
    """Фігура 3: Поперечні перерізи ліній передачі (Коаксіал, Мікросмужка, Скручена пара)."""
    W, H = 760, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Геометрія провідників та характерний імпеданс Z₀", size=16, bold=True))

    # Колонка 1: Коаксіальний кабель
    cx1, cy = 135, 165
    f.append(rect(20, 50, 230, 240, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(cx1, 72, "Коаксіальний кабель", size=13, bold=True, color=INK))

    f.append(circle(cx1, cy, 65, fill="#e2e8f0", stroke=LINE, sw=2))
    f.append(circle(cx1, cy, 63, fill="#f1f5f9", stroke='none'))
    f.append(circle(cx1, cy, 22, fill="#fde047", stroke="#d97706", sw=2))

    f.append(line(cx1 - 22, cy, cx1 + 22, cy, color="#b45309", sw=1.5))
    f.append(text(cx1, cy - 8, "d", size=11, bold=True, color="#b45309"))

    f.append(line(cx1 - 63, cy + 30, cx1 + 63, cy + 30, color=MUTED, sw=1.2, dash="2,2"))
    f.append(text(cx1, cy + 45, "D", size=11, bold=True, color=INK))

    f.append(text(cx1, 260, "Z₀ ≈ (60/√εᵣ)·ln(D/d)", size=11, bold=True, color="#1e40af"))

    # Колонка 2: Мікросмужкова лінія (Microstrip)
    cx2 = 380
    f.append(rect(265, 50, 230, 240, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(cx2, 72, "Мікросмужка (PCB)", size=13, bold=True, color=INK))

    f.append(rect(cx2 - 90, cy - 10, 180, 50, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    f.append(text(cx2 + 55, cy + 18, "εᵣ", size=12, bold=True, color="#15803d"))

    f.append(rect(cx2 - 30, cy - 25, 60, 15, fill="#fde047", stroke="#d97706", sw=1.8))
    f.append(text(cx2, cy - 32, "W", size=11, bold=True, color="#b45309"))

    f.append(rect(cx2 - 95, cy + 40, 190, 12, fill="#94a3b8", stroke=LINE, sw=1.5))
    f.append(text(cx2, cy + 68, "Ground Plane", size=10, color=MUTED))

    f.append(line(cx2 - 102, cy - 10, cx2 - 102, cy + 40, color=MUTED, sw=1.2))
    f.append(text(cx2 - 110, cy + 18, "h", size=11, bold=True))

    f.append(text(cx2, 260, "Z₀ ≈ (87/√[εᵣ+1.41])·ln[5.98h/(0.8W+t)]", size=9, bold=True, color="#1e40af"))

    # Колонка 3: Скручена пара (Twisted Pair)
    cx3 = 625
    f.append(rect(510, 50, 230, 240, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(cx3, 72, "Симетрична пара", size=13, bold=True, color=INK))

    r_wire = 22
    dist = 70
    f.append(circle(cx3 - dist/2, cy, r_wire + 8, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    f.append(circle(cx3 - dist/2, cy, r_wire, fill="#fde047", stroke="#d97706", sw=1.8))

    f.append(circle(cx3 + dist/2, cy, r_wire + 8, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    f.append(circle(cx3 + dist/2, cy, r_wire, fill="#fde047", stroke="#d97706", sw=1.8))

    f.append(line(cx3 - dist/2, cy, cx3 + dist/2, cy, color=MUTED, sw=1.2, dash="2,2"))
    f.append(text(cx3, cy - 10, "D", size=11, bold=True))

    f.append(text(cx3 - dist/2, cy + 4, "d", size=10, bold=True, color="#b45309"))
    f.append(text(cx3 + dist/2, cy + 4, "d", size=10, bold=True, color="#b45309"))

    f.append(text(cx3, 260, "Z₀ ≈ (120/√εᵣ)·cosh⁻¹(D/d)", size=11, bold=True, color="#1e40af"))

    return render(os.path.join(IMG, "geometries-cross-section.svg"), W, H, *f)


def fig_tdr_pulse_response():
    """Фігура 4: Сигнал часової рефлектометрії (TDR) при локальних неоднорідностях імпедансу."""
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Часова рефлектометрія (TDR): локалізація неоднорідностей", size=16, bold=True))

    f.append(rect(20, 50, W - 40, H - 75, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))

    ox, oy = 70, 240
    ax_w, ax_h = W - 120, 160

    f.append(line(ox, oy, ox + ax_w, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, oy - ax_h, color=MUTED, sw=1.4))

    f.append(text(ox + ax_w + 15, oy + 4, "t", size=12, bold=True, color=MUTED))
    f.append(text(ox - 15, oy - ax_h + 10, "V", size=12, bold=True, color=MUTED))

    v0_y = oy - 60
    f.append(line(ox, v0_y, ox + ax_w, v0_y, color="#e2e8f0", sw=1, dash="2,2"))
    f.append(text(ox - 25, v0_y + 4, "V₀ (Z₀)", size=11, color=MUTED))

    t0 = ox + 40
    t1 = ox + 190
    t2 = ox + 350
    t3 = ox + 520

    path_pts = [
        (ox, oy), (t0, oy), (t0, v0_y), (t1, v0_y),
        (t1 + 20, v0_y + 35), (t1 + 40, v0_y), (t2, v0_y),
        (t2 + 20, v0_y - 35), (t2 + 40, v0_y), (t3, v0_y),
        (t3, v0_y - 60), (ox + ax_w, v0_y - 60)
    ]

    for i in range(len(path_pts) - 1):
        f.append(line(path_pts[i][0], path_pts[i][1], path_pts[i+1][0], path_pts[i+1][1], color="#2563eb", sw=2.4))

    f.append(circle(t0, v0_y, 4, fill="#2563eb", stroke='none'))
    f.append(text(t0, oy + 18, "t₀: Вхідний імпульс", size=10, color=INK))

    f.append(circle(t1 + 20, v0_y + 35, 4, fill="#dc2626", stroke='none'))
    f.append(text(t1 + 20, v0_y + 55, "Ємність роз'єму (Z < Z₀)", size=10, bold=True, color="#dc2626"))

    f.append(circle(t2 + 20, v0_y - 35, 4, fill="#d97706", stroke='none'))
    f.append(text(t2 + 20, v0_y - 50, "Індуктивний вигин (Z > Z₀)", size=10, bold=True, color="#d97706"))

    f.append(circle(t3, v0_y - 60, 4, fill="#16a34a", stroke='none'))
    f.append(text(t3 + 45, v0_y - 75, "Обрив лінії (Z = ∞)", size=10, bold=True, color="#16a34a"))

    return render(os.path.join(IMG, "tdr-pulse-response.svg"), W, H, *f)


if __name__ == '__main__':
    fig_lumped_model()
    fig_reflection_waveforms()
    fig_geometries_cross_section()
    fig_tdr_pulse_response()
    print("Всі 4 фігури успішно згенеровано у ./img/")
