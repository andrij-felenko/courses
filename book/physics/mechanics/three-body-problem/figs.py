# -*- coding: utf-8 -*-
"""Фігури до теми «Задача трьох тіл».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_M1 = "#2457d6"   # Масивне тіло M1 (напр. Земля / Сонце)
COLOR_M2 = "#c0392b"   # Друге тіло M2 (напр. Місяць / планета)
COLOR_L  = "#27ae60"   # Точки Лагранжа
COLOR_ORB = "#8e44ad"  # Траєкторія / орбіта
COLOR_CHAOS = "#e67e22" # Хаотична траєкторія

# ── Фігура 1: Точки Лагранжа в обертовій системі відліку ─────────────────────
def fig_lagrange_points():
    W, H = 840, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "П'ять точок Лагранжа в обертовій системі відліку", size=16, bold=True))
    f.append(text(W / 2, 54, "система обертається з кутовою швидкістю ω навколо спільного центра мас O", size=12, color=MUTED))

    # Центр мас та вісь
    cx, cy = 400, 280
    f.append(line(60, cy, 780, cy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(775, cy - 10, "x", size=13, italic=True, color=MUTED, anchor="start"))
    f.append(line(cx, 80, cx, 470, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx + 10, 88, "y", size=13, italic=True, color=MUTED, anchor="start"))

    # Центр мас O
    f.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx + 8, cy + 18, "O (центр мас)", size=11, color=MUTED, anchor="start"))

    # Тіла M1 та M2
    x1, y1 = cx - 110, cy
    x2, y2 = cx + 210, cy

    # Рівносторонні трикутники до L4 і L5 від M1 і M2
    lx = (x1 + x2) / 2
    ly_offset = 320 * math.sqrt(3) / 2
    l4x, l4y = lx, cy - ly_offset + 50
    l5x, l5y = lx, cy + ly_offset - 50

    f.append(line(x1, y1, l4x, l4y, color="#27ae60", sw=1.3, dash="3,3"))
    f.append(line(x2, y2, l4x, l4y, color="#27ae60", sw=1.3, dash="3,3"))
    f.append(line(x1, y1, l5x, l5y, color="#27ae60", sw=1.3, dash="3,3"))
    f.append(line(x2, y2, l5x, l5y, color="#27ae60", sw=1.3, dash="3,3"))

    # Тіла
    f.append(circle(x1, y1, 22, fill="#d6e4ff", stroke=COLOR_M1, sw=2.5))
    f.append(text(x1, y1 + 4, "M₁", size=14, bold=True, color=COLOR_M1, anchor="middle"))
    
    f.append(circle(x2, y2, 14, fill="#ffd6d6", stroke=COLOR_M2, sw=2.2))
    f.append(text(x2, y2 + 4, "M₂", size=12, bold=True, color=COLOR_M2, anchor="middle"))

    # Точки Лагранжа L1, L2, L3
    l1x = cx + 130
    l2x = cx + 290
    l3x = cx - 270

    f.append(circle(l1x, cy, 7, fill="#e8f8f0", stroke=COLOR_L, sw=2))
    f.append(text(l1x, cy - 14, "L₁", size=13, bold=True, color=COLOR_L, anchor="middle"))

    f.append(circle(l2x, cy, 7, fill="#e8f8f0", stroke=COLOR_L, sw=2))
    f.append(text(l2x, cy - 14, "L₂", size=13, bold=True, color=COLOR_L, anchor="middle"))

    f.append(circle(l3x, cy, 7, fill="#e8f8f0", stroke=COLOR_L, sw=2))
    f.append(text(l3x, cy - 14, "L₃", size=13, bold=True, color=COLOR_L, anchor="middle"))

    f.append(circle(l4x, l4y, 8, fill="#e8f8f0", stroke=COLOR_L, sw=2.2))
    f.append(text(l4x, l4y - 14, "L₄ (троянська)", size=13, bold=True, color=COLOR_L, anchor="middle"))

    f.append(circle(l5x, l5y, 8, fill="#e8f8f0", stroke=COLOR_L, sw=2.2))
    f.append(text(l5x, l5y + 24, "L₅ (грецька)", size=13, bold=True, color=COLOR_L, anchor="middle"))

    tb1, _, _ = textbox(150, 110, "Колінеарні (нестійкі):\nL₁, L₂, L₃ — сідлові точки\nефективного потенціалу", size=12, pad=8, fill="#f9fafb", stroke=MUTED)
    f.append(tb1)

    tb2, _, _ = textbox(690, 110, "Трикутні (стійкі при μ < 0.0385):\nL₄, L₅ — рівносторонні\nтрикутники з M₁ та M₂", size=12, pad=8, fill="#eef9f2", stroke=COLOR_L)
    f.append(tb2)

    f.append(arrow(cx + 40, 140, cx + 80, 140, color=COLOR_ORB, sw=2))
    f.append(text(cx + 60, 125, "обертання ω", size=12, bold=True, color=COLOR_ORB, anchor="middle"))

    return render(os.path.join(IMG, "lagrange-points.svg"), W, H, *f)


# ── Фігура 2: Поверхні нульової швидкості та області Гілла ───────────────────
def fig_zero_velocity_curves():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Поверхні нульової швидкості (області Гілла) при різних значеннях C", size=16, bold=True))
    f.append(text(W / 2, 54, "значення константи Якобі C визначає дозволені області руху для третього тіла", size=12, color=MUTED))

    panels = [
        ("а) Високе C (C > C_L1): Рух замкнений біля M₁ або M₂", 40, 80, 360, 180),
        ("б) C_L2 < C < C_L1: Відкрито перехід L₁ між M₁ та M₂", 440, 80, 360, 180),
        ("в) C_L3 < C < C_L2: Відкрито вихід через L₂ у зовнішній простір", 40, 280, 360, 180),
        ("г) Низьке C (C < C_L5): Заборонених областей немає, рух хаотичний", 440, 280, 360, 180),
    ]

    for title, px, py, pw, ph in panels:
        f.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
        f.append(text(px + pw / 2, py + 22, title, size=11, bold=True, color=INK, anchor="middle"))
        
        m1x = px + pw * 0.35
        m2x = px + pw * 0.70
        my = py + ph * 0.55

        if "а)" in title:
            f.append('<path d="M %f %f Q %f %f %f %f Q %f %f %f %f Z" fill="#fee2e2" stroke="%s" stroke-width="1.2" opacity="0.6"/>' %
                     (px+20, py+40, px+pw/2, py+ph/2-10, px+pw-20, py+40, px+pw/2, py+ph-10, px+20, py+40, COLOR_M2))
            f.append(circle(m1x, my, 35, fill="#ffffff", stroke=COLOR_M1, sw=1.5))
            f.append(circle(m2x, my, 20, fill="#ffffff", stroke=COLOR_M2, sw=1.5))
        elif "б)" in title:
            f.append('<path d="M %f %f C %f %f %f %f %f %f Z" fill="#fee2e2" stroke="%s" stroke-width="1.2" opacity="0.6"/>' %
                     (px+20, py+40, px+pw/2, py+45, px+pw-20, py+40, px+20, py+40, COLOR_M2))
            f.append('<path d="M %f %f Q %f %f %f %f Z" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' %
                     (m1x-30, my-25, (m1x+m2x)/2, my, m2x+20, my+25, COLOR_ORB))
            f.append('<path d="M %f %f Q %f %f %f %f Z" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' %
                     (m1x-30, my+25, (m1x+m2x)/2, my, m2x+20, my-25, COLOR_ORB))
            f.append(circle((m1x+m2x)/2, my, 4, fill=COLOR_L, stroke=COLOR_L, sw=1))
            f.append(text((m1x+m2x)/2, my - 8, "L₁ шлюз", size=9, bold=True, color=COLOR_L, anchor="middle"))
        elif "в)" in title:
            f.append(circle(m1x, my, 12, fill=COLOR_M1, stroke=COLOR_M1, sw=1))
            f.append(circle(m2x, my, 8, fill=COLOR_M2, stroke=COLOR_M2, sw=1))
            f.append(circle(m2x + 35, my, 4, fill=COLOR_L, stroke=COLOR_L, sw=1))
            f.append(text(m2x + 35, my - 8, "L₂ шлюз", size=9, bold=True, color=COLOR_L, anchor="middle"))
            f.append(arrow(m1x, my, m2x + 60, my - 20, color=COLOR_CHAOS, sw=1.5))
        else:
            f.append(circle(m1x, my, 12, fill=COLOR_M1, stroke=COLOR_M1, sw=1))
            f.append(circle(m2x, my, 8, fill=COLOR_M2, stroke=COLOR_M2, sw=1))
            f.append('<path d="M %f %f Q %f %f %f %f T %f %f T %f %f" fill="none" stroke="%s" stroke-width="1.5"/>' %
                     (px+30, my-40, m1x, my+30, m2x, my-30, px+pw-30, my+20, px+pw-50, my-50, COLOR_CHAOS))

        f.append(circle(m1x, my, 8, fill=COLOR_M1, stroke=COLOR_M1, sw=1))
        f.append(text(m1x, my + 16, "M₁", size=10, bold=True, color=COLOR_M1, anchor="middle"))
        f.append(circle(m2x, my, 5, fill=COLOR_M2, stroke=COLOR_M2, sw=1))
        f.append(text(m2x, my + 14, "M₂", size=10, bold=True, color=COLOR_M2, anchor="middle"))

    return render(os.path.join(IMG, "zero-velocity-curves.svg"), W, H, *f)


# ── Фігура 3: Детермінований хаос і чутливість до початкових умов ─────────────
def fig_chaos_sensitivity():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Експоненціальна розбіжність близьких траєкторій (показник Ляпунова)", size=16, bold=True))
    f.append(text(W / 2, 54, "початкова різниця у швидкості Δv₀ = 10⁻⁸ призводить до повної розбіжності за час t", size=12, color=MUTED))

    gx, gy, gw, gh = 70, 100, 330, 320
    f.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(gx + gw / 2, gy + 24, "Відстань між траєкторіями Δr(t)", size=13, bold=True, color=INK, anchor="middle"))

    f.append(arrow(gx + 40, gy + gh - 40, gx + gw - 20, gy + gh - 40, color=INK, sw=1.5))
    f.append(text(gx + gw - 15, gy + gh - 25, "час t", size=12, italic=True, anchor="start"))
    f.append(arrow(gx + 40, gy + gh - 40, gx + 40, gy + 40, color=INK, sw=1.5))
    f.append(text(gx + 25, gy + 35, "lg Δr", size=12, italic=True, anchor="middle"))

    f.append(line(gx + 40, gy + gh - 50, gx + 230, gy + 110, color=COLOR_CHAOS, sw=2.5))
    f.append(text(gx + 135, gy + gh - 150, "експоненціальне зростання ~ e^{λ·t}", size=11, bold=True, color=COLOR_CHAOS, anchor="start"))

    f.append(line(gx + 230, gy + 110, gx + gw - 30, gy + 115, color=COLOR_CHAOS, sw=2, dash="4,4"))
    f.append(text(gx + 250, gy + 95, "насичення (розмір системи)", size=10, color=MUTED, anchor="start"))

    f.append(circle(gx + 40, gy + gh - 50, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(gx + 50, gy + gh - 50, "Δr₀ = 10⁻⁸", size=10, bold=True, color=POS, anchor="start"))

    px, py, pw, ph = 450, 100, 330, 320
    f.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(px + pw / 2, py + 24, "Траєкторії у координатному просторі", size=13, bold=True, color=INK, anchor="middle"))

    sx, sy = px + 60, py + ph / 2
    f.append(circle(sx, sy, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(sx - 10, sy - 12, "старт S₀", size=11, bold=True, anchor="end"))

    f.append('<path d="M %f %f Q %f %f %f %f T %f %f T %f %f" fill="none" stroke="%s" stroke-width="2"/>' %
             (sx, sy, px+140, py+80, px+200, py+180, px+270, py+100, px+300, py+240, COLOR_M1))
    f.append(text(px + 295, py + 255, "Траєкторія A", size=11, bold=True, color=COLOR_M1, anchor="middle"))

    f.append('<path d="M %f %f Q %f %f %f %f T %f %f T %f %f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,2"/>' %
             (sx, sy, px+140, py+82, px+195, py+170, px+240, py+260, px+290, py+80, COLOR_M2))
    f.append(text(px + 295, py + 70, "Траєкторія B (v₀ + Δv₀)", size=11, bold=True, color=COLOR_M2, anchor="middle"))

    f.append(circle(px + 198, py + 175, 5, fill=COLOR_CHAOS, stroke=COLOR_CHAOS, sw=1))
    f.append(line(px + 198, py + 175, px + 198, py + ph - 25, color=MUTED, sw=1.2, dash="2,2"))
    f.append(text(px + 198, py + ph - 10, "горизонт передбачуваності t_h", size=10, bold=True, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, "chaos-sensitivity.svg"), W, H, *f)


# ── Фігура 4: Періодична орбіта-вісімка (хореографія трьох однакових мас) ───────
def fig_figure_eight_orbit():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Періодична орбіта «вісімка» (хореографія Шенсіне–Монтгомері)", size=16, bold=True))
    f.append(text(W / 2, 54, "три однакові маси m₁ = m₂ = m₃ рухаються по одній плоскій траєкторії з фазовим зсувом T/3", size=12, color=MUTED))

    cx, cy = 420, 270

    pts = []
    for i in range(101):
        t = i * 2 * math.pi / 100
        scale_x = 320
        scale_y = 150
        x = cx + scale_x * math.sin(t)
        y = cy + scale_y * math.sin(2 * t)
        pts.append((x, y))

    path_str = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts) + " Z"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_str, COLOR_ORB))

    t1 = 0.5
    t2 = 0.5 + 2 * math.pi / 3
    t3 = 0.5 + 4 * math.pi / 3

    m1_x = cx + 320 * math.sin(t1)
    m1_y = cy + 150 * math.sin(2 * t1)

    m2_x = cx + 320 * math.sin(t2)
    m2_y = cy + 150 * math.sin(2 * t2)

    m3_x = cx + 320 * math.sin(t3)
    m3_y = cy + 150 * math.sin(2 * t3)

    v_scale = 0.25
    v1_x = 320 * math.cos(t1) * v_scale
    v1_y = 300 * math.cos(2 * t1) * v_scale

    v2_x = 320 * math.cos(t2) * v_scale
    v2_y = 300 * math.cos(2 * t2) * v_scale

    v3_x = 320 * math.cos(t3) * v_scale
    v3_y = 300 * math.cos(2 * t3) * v_scale

    f.append(arrow(m1_x, m1_y, m1_x + v1_x, m1_y + v1_y, color=COLOR_M1, sw=2))
    f.append(arrow(m2_x, m2_y, m2_x + v2_x, m2_y + v2_y, color=COLOR_M2, sw=2))
    f.append(arrow(m3_x, m3_y, m3_x + v3_x, m3_y + v3_y, color=COLOR_L, sw=2))

    f.append(circle(m1_x, m1_y, 14, fill="#d6e4ff", stroke=COLOR_M1, sw=2.2))
    f.append(text(m1_x, m1_y + 4, "m₁", size=12, bold=True, color=COLOR_M1, anchor="middle"))

    f.append(circle(m2_x, m2_y, 14, fill="#ffd6d6", stroke=COLOR_M2, sw=2.2))
    f.append(text(m2_x, m2_y + 4, "m₂", size=12, bold=True, color=COLOR_M2, anchor="middle"))

    f.append(circle(m3_x, m3_y, 14, fill="#e8f8f0", stroke=COLOR_L, sw=2.2))
    f.append(text(m3_x, m3_y + 4, "m₃", size=12, bold=True, color=COLOR_L, anchor="middle"))

    f.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 20, "O (центр мас)", size=11, color=MUTED, anchor="middle"))

    tb, _, _ = textbox(150, 420, "Сумарний момент імпульсу L = 0\nПовна енергія E < 0\nСтрого періодичний розв'язок", size=12, pad=8, fill="#f4f6f8", stroke=COLOR_ORB)
    f.append(tb)

    return render(os.path.join(IMG, "figure-eight-orbit.svg"), W, H, *f)


# ── Фігура 5: Околова гало-орбіта апарата біля точки L2 ──────────────────────
def fig_halo_orbit_earth_moon():
    W, H = 840, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Гало-орбіта космічного апарата навколо точки L₂", size=16, bold=True))
    f.append(text(W / 2, 54, "система Земля–Місяць: тривимірна орбіта обльоту точки рівноваги L₂", size=12, color=MUTED))

    ex, ey = 140, 260
    mx, my = 520, 260
    l2x, l2y = 680, 260

    f.append(line(80, ey, 780, ey, color=MUTED, sw=1.2, dash="4,4"))

    f.append(circle(ex, ey, 32, fill="#d6e4ff", stroke=COLOR_M1, sw=2.5))
    f.append(text(ex, ey + 5, "Земля", size=13, bold=True, color=COLOR_M1, anchor="middle"))

    f.append(circle(mx, my, 16, fill="#e2e8f0", stroke="#475569", sw=2.2))
    f.append(text(mx, my + 4, "Місяць", size=11, bold=True, color="#475569", anchor="middle"))

    f.append(circle(l2x, l2y, 6, fill=COLOR_L, stroke=COLOR_L, sw=1))
    f.append(text(l2x, l2y - 15, "L₂", size=13, bold=True, color=COLOR_L, anchor="middle"))

    f.append('<ellipse cx="%.1f" cy="%.1f" rx="55" ry="85" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (l2x, l2y, COLOR_ORB))
    f.append(text(l2x, l2y + 110, "Гало-орбіта (Halo Orbit)", size=12, bold=True, color=COLOR_ORB, anchor="middle"))

    f.append('<path d="M %f %f C %f %f %f %f %f %f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5,3"/>' %
             (ex + 35, ey - 20, 300, 140, 500, 160, l2x - 30, l2y - 65, COLOR_CHAOS))
    f.append(arrow(l2x - 35, l2y - 68, l2x - 20, l2y - 55, color=COLOR_CHAOS, sw=2))
    f.append(text(380, 145, "траєкторія перельоту (міліграм палива)", size=11, bold=True, color=COLOR_CHAOS, anchor="middle"))

    scx, scy = l2x + 40, l2y - 55
    f.append(circle(scx, scy, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(scx + 12, scy - 5, "КА (наприклад, James Webb)", size=11, bold=True, color=POS, anchor="start"))

    tb, _, _ = textbox(240, 410, "Гало-орбіти утримуються мікроімпульсами двигунів\nзавдяки орбітальній стійкості інваріантних многовидів", size=11, pad=8, fill="#f8fafc", stroke=MUTED)
    f.append(tb)

    return render(os.path.join(IMG, "halo-orbit-earth-moon.svg"), W, H, *f)


def main():
    fig_lagrange_points()
    fig_zero_velocity_curves()
    fig_chaos_sensitivity()
    fig_figure_eight_orbit()
    fig_halo_orbit_earth_moon()
    print("Всі 5 фігур успішно згенеровано у ./img/")

if __name__ == "__main__":
    main()
