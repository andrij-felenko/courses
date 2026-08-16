# -*- coding: utf-8 -*-
"""Фігури до теми «Зв'язані осцилятори й нормальні моди».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Допоміжні деталі ────────────────────────────────────────────────────────
def spring(x1, x2, y, coils=7, amp=12, lead=14):
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def wall(x, y1, y2, side=1):
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    step = 14
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.4))
        yy += step
    return "".join(out)


def ground(x1, x2, y):
    out = [line(x1, y, x2, y, color=INK, sw=3)]
    xx = x1 + 6
    while xx < x2:
        out.append(line(xx, y, xx - 12, y + 12, color=MUTED, sw=1.4))
        xx += 14
    return "".join(out)


# ── Фігура 1: Модель двох зв'язаних мас ──────────────────────────────────────
def fig_model_two_mass():
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    wx1 = 60
    wx2 = 720
    gy = 250
    
    f.append(wall(wx1, 80, gy, side=-1))
    f.append(wall(wx2, 80, gy, side=1))
    f.append(ground(wx1, wx2, gy))
    
    # Маси
    m1_w, m1_h = 100, 70
    m2_w, m2_h = 100, 70
    
    m1_x = 210
    m1_y = gy - m1_h
    m2_x = 470
    m2_y = gy - m2_h
    
    # Рівноважні лінії (пунктир)
    f.append(line(230, 70, 230, gy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(450, 70, 450, gy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(230, 60, "x₁ = 0", size=12, color=MUTED))
    f.append(text(450, 60, "x₂ = 0", size=12, color=MUTED))
    
    # Пружини
    f.append(spring(wx1, m1_x, m1_y + m1_h / 2, coils=6, amp=11))
    f.append(spring(m1_x + m1_w, m2_x, m1_y + m1_h / 2, coils=7, amp=11))
    f.append(spring(m2_x + m2_w, wx2, m2_y + m2_h / 2, coils=6, amp=11))
    
    # Написи пружин
    f.append(text((wx1 + m1_x) / 2, m1_y - 12, "k₁", size=15, bold=True, color=POS))
    f.append(text((m1_x + m1_w + m2_x) / 2, m1_y - 12, "k₁₂ (зв'язок)", size=15, bold=True, color=FIELD))
    f.append(text((m2_x + m2_w + wx2) / 2, m2_y - 12, "k₂", size=15, bold=True, color=POS))
    
    # Блоки мас
    f.append(rect(m1_x, m1_y, m1_w, m1_h, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    f.append(text(m1_x + m1_w / 2, m1_y + m1_h / 2 + 5, "m₁", size=18, bold=True, color=NEG))
    
    f.append(rect(m2_x, m2_y, m2_w, m2_h, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(m2_x + m2_w / 2, m2_y + m2_h / 2 + 5, "m₂", size=18, bold=True, color=POS))
    
    # Стрілки зсуву
    f.append(arrow(230, m1_y + m1_h + 20, m1_x + m1_w / 2, m1_y + m1_h + 20, color=NEG, sw=2))
    f.append(text(245, m1_y + m1_h + 38, "+x₁", size=13, color=NEG, bold=True))
    
    f.append(arrow(450, m2_y + m2_h + 20, m2_x + m2_w / 2, m2_y + m2_h + 20, color=POS, sw=2))
    f.append(text(470, m2_y + m2_h + 38, "+x₂", size=13, color=POS, bold=True))
    
    # Формули внизу
    b1, _, _ = textbox(260, 315, "m₁·ẍ₁ = −k₁·x₁ + k₁₂·(x₂ − x₁)", size=13, fill=FILL, stroke=NEG)
    b2, _, _ = textbox(520, 315, "m₂·ẍ₂ = −k₂·x₂ − k₁₂·(x₂ − x₁)", size=13, fill=FILL, stroke=POS)
    f.append(b1)
    f.append(b2)
    
    return render(os.path.join(IMG, "model-two-mass.svg"), W, H, *f,
                  title="Модель двох зв'язаних мас на пружинах")


# ── Фігура 2: Обмін енергією та перекачування (Биття) ────────────────────────
def fig_beats_energy_transfer():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    ox, oy = 70, 180
    gw, gh = 650, 110
    
    # Осі
    f.append(line(ox, oy - gh - 10, ox, oy + gh + 15, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    f.append(text(ox + gw + 25, oy + 4, "t", size=14, bold=True))
    f.append(text(ox - 30, oy - gh, "x(t)", size=14, bold=True))
    f.append(text(ox - 15, oy + 5, "0", size=12, color=MUTED))
    
    # Графіки x1(t) та x2(t) для випадку слабкого зв'язку
    pts1 = []
    pts2 = []
    env1_pos = []
    env1_neg = []
    
    steps = 400
    t_max = 4.0 * math.pi / 0.15
    for i in range(steps + 1):
        t = i * t_max / steps
        px = ox + (t / t_max) * gw
        
        env = math.cos(0.15 * t)
        env_s = math.sin(0.15 * t)
        
        v1 = env * math.cos(2.0 * t)
        v2 = env_s * math.sin(2.0 * t)
        
        py1 = oy - v1 * (gh - 10)
        py2 = oy - v2 * (gh - 10)
        
        pts1.append("%.1f %.1f" % (px, py1))
        pts2.append("%.1f %.1f" % (px, py2))
        
        env1_pos.append("%.1f %.1f" % (px, oy - abs(env) * (gh - 10)))
        env1_neg.append("%.1f %.1f" % (px, oy + abs(env) * (gh - 10)))
    
    # Обвідна e1
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' %
             (" L ".join(env1_pos), MUTED))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' %
             (" L ".join(env1_neg), MUTED))
    
    # Лінії зрушень
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" L ".join(pts1), NEG))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.0"/>' %
             (" L ".join(pts2), POS))
    
    # Позначення максимумів і вузлів
    node1_x = ox + (math.pi / (2 * 0.15) / t_max) * gw
    node2_x = ox + (math.pi / 0.15 / t_max) * gw
    
    f.append(line(node1_x, oy - gh - 5, node1_x, oy + gh + 5, color=MUTED, sw=1.0, dash="2,3"))
    f.append(line(node2_x, oy - gh - 5, node2_x, oy + gh + 5, color=MUTED, sw=1.0, dash="2,3"))
    
    # Легенда
    f.append(rect(100, 42, 270, 46, fill=FILL, stroke=LINE, sw=1))
    f.append(line(115, 54, 145, 54, color=NEG, sw=2.5))
    f.append(text(155, 58, "Маса 1: x₁(t) (старт з A)", size=12, color=INK, anchor="start"))
    f.append(line(115, 72, 145, 72, color=POS, sw=2.5))
    f.append(text(155, 76, "Маса 2: x₂(t) (старт з 0)", size=12, color=INK, anchor="start"))
    
    # Пояснювальні виноси (розведені по висоті, щоб не перекривались)
    b1, _, _ = textbox(node1_x + 10, 310, "Вся енергія в масі 2\n(маса 1 зупинилася)", size=11, fill="#fdecea", stroke=POS)
    b2, _, _ = textbox(node2_x + 35, 375, "Вся енергія повернулася\nдо маси 1", size=11, fill="#eaf0fd", stroke=NEG)
    f.append(b1)
    f.append(b2)
    
    return render(os.path.join(IMG, "beats-energy-transfer.svg"), W, H, *f,
                  title="Перекачування енергії між масами (явище биття)")


# ── Фігура 3: Форми нормальних мод (синфазна та протифазна) ───────────────────
def fig_normal_modes_shapes():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    # Верхня панель — Мода 1 (Синфазна)
    p1_y = 120
    f.append(rect(30, 45, W - 60, 160, fill="#f9fafb", stroke=LINE, sw=1.2, rx=8))
    f.append(text(50, 70, "Мода 1: Синфазне коливання (q₁ = x₁ + x₂)", size=15, bold=True, anchor="start", color=NEG))
    f.append(text(500, 70, "Частота: ω₁ = √(k/m)", size=14, bold=True, anchor="start", color=INK))
    
    wx1 = 80
    wx2 = 700
    gy1 = p1_y + 55
    
    f.append(wall(wx1, gy1 - 60, gy1 + 10, side=-1))
    f.append(wall(wx2, gy1 - 60, gy1 + 10, side=1))
    f.append(ground(wx1, wx2, gy1))
    
    # Зсунуті в один бік
    m1_x, m2_x = 240, 500
    mw, mh = 70, 50
    my = gy1 - mh
    
    f.append(spring(wx1, m1_x, my + mh/2, coils=5, amp=9))
    f.append(spring(m1_x + mw, m2_x, my + mh/2, coils=6, amp=9)) # нерозтягнута!
    f.append(spring(m2_x + mw, wx2, my + mh/2, coils=5, amp=9))
    
    f.append(rect(m1_x, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(m1_x + mw/2, my + mh/2 + 5, "m₁", size=15, bold=True))
    f.append(rect(m2_x, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(m2_x + mw/2, my + mh/2 + 5, "m₂", size=15, bold=True))
    
    f.append(arrow(m1_x + mw/2, my - 15, m1_x + mw/2 + 40, my - 15, color=NEG, sw=2.5))
    f.append(arrow(m2_x + mw/2, my - 15, m2_x + mw/2 + 40, my - 15, color=NEG, sw=2.5))
    f.append(text(385, my + mh/2 - 15, "k₁₂ не деформується!", size=12, color=MUTED))
    
    # Нижня панель — Мода 2 (Протифазна)
    p2_y = 310
    f.append(rect(30, 230, W - 60, 160, fill="#f9fafb", stroke=LINE, sw=1.2, rx=8))
    f.append(text(50, 255, "Мода 2: Протифазне коливання (q₂ = x₁ − x₂)", size=15, bold=True, anchor="start", color=POS))
    f.append(text(500, 255, "Частота: ω₂ = √((k + 2k₁₂)/m)", size=14, bold=True, anchor="start", color=INK))
    
    gy2 = p2_y + 55
    f.append(wall(wx1, gy2 - 60, gy2 + 10, side=-1))
    f.append(wall(wx2, gy2 - 60, gy2 + 10, side=1))
    f.append(ground(wx1, wx2, gy2))
    
    # Зсунуті назустріч
    m1_x2, m2_x2 = 250, 450
    my2 = gy2 - mh
    
    f.append(spring(wx1, m1_x2, my2 + mh/2, coils=6, amp=9))
    f.append(spring(m1_x2 + mw, m2_x2, my2 + mh/2, coils=8, amp=14)) # стиснута!
    f.append(spring(m2_x2 + mw, wx2, my2 + mh/2, coils=6, amp=9))
    
    f.append(rect(m1_x2, my2, mw, mh, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(m1_x2 + mw/2, my2 + mh/2 + 5, "m₁", size=15, bold=True))
    f.append(rect(m2_x2, my2, mw, mh, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(m2_x2 + mw/2, my2 + mh/2 + 5, "m₂", size=15, bold=True))
    
    f.append(arrow(m1_x2 + mw/2, my2 - 15, m1_x2 + mw/2 + 40, my2 - 15, color=POS, sw=2.5))
    f.append(arrow(m2_x2 + mw/2, my2 - 15, m2_x2 + mw/2 - 40, my2 - 15, color=POS, sw=2.5))
    f.append(text(385, my2 + mh/2 - 18, "k₁₂ сильно стискається/розтягується", size=12, color=POS, bold=True))
    
    return render(os.path.join(IMG, "normal-modes-shapes.svg"), W, H, *f,
                  title="Форми й напрямки руху двох нормальних мод")


# ── Фігура 4: Дисперсійна крива ланцюжка осциляторів ─────────────────────────
def fig_dispersion_chain():
    W, H = 780, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    ox, oy = 90, 310
    gw, gh = 620, 230
    
    # Осі
    f.append(line(ox, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh - 20, color=INK, sw=1.8))
    f.append(text(ox + gw + 25, oy + 5, "k_w (хвильове число)", size=13, bold=True))
    f.append(text(ox - 30, oy - gh - 15, "ω(k_w)", size=13, bold=True))
    
    # Пунктири границь
    pi_x = ox + gw * 0.85
    f.append(line(pi_x, oy, pi_x, oy - gh - 10, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(pi_x, oy + 20, "π / a (межа зони)", size=12, bold=True, color=INK))
    
    w_max_y = oy - gh * 0.8
    f.append(line(ox, w_max_y, pi_x + 30, w_max_y, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox - 45, w_max_y + 4, "ω_max = 2√(K/m)", size=12, bold=True, color=POS))
    
    # Синусоїдальна дисперсія ω(k) = ω_max * sin(k*a/2)
    pts = []
    steps = 300
    for i in range(steps + 1):
        kw_ratio = (i / steps) * 0.85
        px = ox + kw_ratio * gw
        w_val = math.sin(kw_ratio * math.pi / 0.85 * 0.5)
        py = oy - w_val * (gh * 0.8)
        pts.append("%.1f %.1f" % (px, py))
    
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" L ".join(pts), NEG))
    
    # Дотична лінія довгих хвиль (лінійна дисперсія ω = v_s * k_w)
    f.append(line(ox, oy, ox + gw * 0.45, oy - (gh * 0.8) * (0.45 / 0.85 * (math.pi/2)),
                  color=FIELD, sw=1.8, dash="5,4"))
    
    # Блоки підписів
    b1, _, _ = textbox(ox + 180, oy - 140, "Довгі хвилі (k_w → 0):\nлінійна дисперсія ω ≈ c_s · k_w\n(акустичний закон, суцільне середовище)", size=11, fill="#eaf0fd", stroke=NEG)
    b2, _, _ = textbox(pi_x - 70, oy - 210, "Короткі хвилі (k_w ≈ π/a):\nсильна дисперсія,\nвідбивання від ґратки", size=11, fill="#fdecea", stroke=POS)
    
    f.append(b1)
    f.append(b2)
    
    # Маленька схема ланцюжка зверху
    cx0, cy0 = 430, 60
    f.append(rect(cx0, cy0 - 25, 300, 50, fill="#f9fafb", stroke=MUTED, sw=1, rx=6))
    f.append(text(cx0 + 150, cy0 - 10, "Ланцюжок дискретних мас m і пружин K", size=11, bold=True))
    for idx in range(5):
        mx = cx0 + 30 + idx * 55
        f.append(circle(mx, cy0 + 10, 8, fill=NEG, stroke=INK, sw=1))
        if idx < 4:
            f.append(spring(mx + 8, mx + 47, cy0 + 10, coils=3, amp=5, lead=4))
    
    return render(os.path.join(IMG, "dispersion-chain.svg"), W, H, *f,
                  title="Дисперсійна крива 1D ланцюжка осциляторів")


if __name__ == '__main__':
    fig_model_two_mass()
    fig_beats_energy_transfer()
    fig_normal_modes_shapes()
    fig_dispersion_chain()
    print("Всі фігури успішно згенеровано у ./img/")
