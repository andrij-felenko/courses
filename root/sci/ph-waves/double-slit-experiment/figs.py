# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Оптична схема двощілинного досліду Юнга
# ═══════════════════════════════════════════════════════════════════════════
def fig_double_slit_setup():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптична схема двощілинного досліду Юнга', 16, INK, 'middle', bold=True))

    # Джерело світла та первинна щелина (ліворуч)
    sx, sy = 60, 190
    f.append(circle(sx - 20, sy, 12, fill='#fef08a', stroke='#eab308', sw=2))
    f.append(text(sx - 20, sy - 20, 'Джерело світла', 10, INK, 'middle', bold=True))

    # Двощілинна ширма
    bx = 220
    gap = 40  # d
    s1_y = sy - gap / 2  # 170
    s2_y = sy + gap / 2  # 210
    slit_w = 6

    # Ширма верхня, середня, нижня
    f.append(rect(bx - 3, 40, slit_w, s1_y - 50, fill=INK, stroke='none', sw=0))
    f.append(rect(bx - 3, s1_y + 6, slit_w, (s2_y - 6) - (s1_y + 6), fill=INK, stroke='none', sw=0))
    f.append(rect(bx - 3, s2_y + 6, slit_w, H - 40 - (s2_y + 6), fill=INK, stroke='none', sw=0))

    f.append(text(bx, 48, 'Ширма з двома щілинами', 10, INK, 'middle', bold=True))
    f.append(text(bx - 14, s1_y + 3, 'S₁', 11, POS, 'end', bold=True))
    f.append(text(bx - 14, s2_y + 3, 'S₂', 11, POS, 'end', bold=True))

    # Позначка відстані d між щілинами
    f.append(line(bx + 15, s1_y, bx + 15, s2_y, color=NEG, sw=1.5))
    f.append(line(bx + 10, s1_y, bx + 20, s1_y, color=NEG, sw=1))
    f.append(line(bx + 10, s2_y, bx + 20, s2_y, color=NEG, sw=1))
    f.append(text(bx + 26, sy + 4, 'd', 12, NEG, 'start', bold=True, italic=True))

    # Екран (праворуч)
    ex = 620
    f.append(rect(ex - 4, 40, 8, H - 80, fill='#cbd5e1', stroke=INK, sw=1.5))
    f.append(text(ex + 14, 52, 'Екран', 11, INK, 'start', bold=True))

    # Оптична вісь (пунктир)
    f.append(line(bx, sy, ex, sy, color=MUTED, sw=1.2, dash='6,4'))
    f.append(text(ex - 80, sy + 16, 'Оптична вісь', 10, MUTED, 'middle'))
    f.append(circle(ex, sy, 3, fill=POS, stroke=POS, sw=1))
    f.append(text(ex + 14, sy + 4, 'y = 0 (O)', 10, POS, 'start', bold=True))

    # Точка P на екрані на висоті y
    py = sy - 110  # y = 110 px вгору
    f.append(circle(ex, py, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(ex + 14, py + 4, 'P(y)', 11, NEG, 'start', bold=True))

    # Промені від S1 та S2 до точок P
    f.append(line(bx, s1_y, ex, py, color=POS, sw=2))
    f.append(line(bx, s2_y, ex, py, color=FIELD, sw=2))
    f.append(text(bx + 160, (s1_y + py) / 2 - 10, 'r₁', 11, POS, 'middle', bold=True, italic=True))
    f.append(text(bx + 160, (s2_y + py) / 2 + 14, 'r₂', 11, FIELD, 'middle', bold=True, italic=True))

    # Перпендикуляр для визначення різниці ходу Δs
    dx_p = ex - bx
    dy_p = py - s2_y
    angle_rad = math.atan2(dy_p, dx_p)
    
    proj_len = gap * math.sin(-angle_rad)
    px_perp = bx + proj_len * math.cos(angle_rad)
    py_perp = s2_y + proj_len * math.sin(angle_rad)
    
    f.append(line(bx, s1_y, px_perp, py_perp, color=NEG, sw=1.2, dash='3,3'))
    f.append(line(bx, s2_y, px_perp, py_perp, color=NEG, sw=2.5))
    f.append(text(bx + 30, s2_y - 6, 'Δs', 11, NEG, 'start', bold=True))

    # Позначка відстані L від ширми до екрана
    f.append(line(bx, H - 35, ex, H - 35, color=INK, sw=1.5))
    f.append(line(bx, H - 40, bx, H - 30, color=INK, sw=1))
    f.append(line(ex, H - 40, ex, H - 30, color=INK, sw=1))
    f.append(text((bx + ex) / 2, H - 42, 'L (L ≫ d)', 12, INK, 'middle', bold=True, italic=True))

    # Позначка висоти y на екрані
    f.append(line(ex - 25, sy, ex - 25, py, color=NEG, sw=1.2))
    f.append(line(ex - 30, sy, ex - 20, sy, color=NEG, sw=1))
    f.append(line(ex - 30, py, ex - 20, py, color=NEG, sw=1))
    f.append(text(ex - 34, (sy + py) / 2 + 4, 'y', 12, NEG, 'end', bold=True, italic=True))

    # Позначка кута θ
    f.append(text(bx + 70, sy - 14, 'θ', 11, INK, 'middle', bold=True, italic=True))

    # Пояснювальний бокс
    f.append(fitbox(310, 50, 230, 80,
                    'Умова максимуму: Δs = d · sin θ ≈ d · y / L = m · λ\n'
                    'Умова мінімуму: Δs = (m + ½) · λ\n'
                    'Ширина смуги: Δy = λ · L / d',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'double-slit-setup.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Розподіл інтенсивності з урахуванням дифракції (sinc^2 * cos^2)
# ═══════════════════════════════════════════════════════════════════════════
def fig_intensity_pattern():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Розподіл інтенсивності з урахуванням дифракції на щілинах', 16, INK, 'middle', bold=True))

    ox, oy = 80, 290
    gw, gh = 580, 220

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill='#fafbfc', stroke=MUTED, sw=1))

    # Горизонтальна вісь (позиція y на екрані або кут θ)
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.5))
    f.append(line(ox + gw / 2, oy - gh, ox + gw / 2, oy, color=MUTED, sw=1, dash='4,4'))

    # Позначки шкали y / (λL/d)
    for m in range(-4, 5):
        x = ox + gw / 2 + m * (gw / 10.0)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1))
        label = '%d' % m if m != 0 else '0'
        f.append(text(x, oy + 18, label, 10, MUTED, 'middle'))

    f.append(text(ox + gw / 2, oy + 36, 'Порядок інтерференційного максимуму m = y / (λL / d)', 11, INK, 'middle', bold=True))
    f.append(text(ox - 35, oy - gh / 2, 'I / I₀', 12, INK, 'middle', bold=True))

    # Позначки I/I0 = 0, 0.5, 1.0
    for val in [0.0, 0.5, 1.0]:
        y = oy - val * (gh - 20)
        f.append(line(ox, y, ox + gw, y, color='#e2e8f0', sw=1))
        f.append(text(ox - 8, y + 4, '%.1f' % val, 10, MUTED, 'end'))

    pts_int = []  # повна інтенсивність I(y)
    pts_env = []  # дифракційна огинаюча sinc^2

    steps = 400
    for i in range(steps + 1):
        u = (i / float(steps) - 0.5) * 10.0 * math.pi
        x = ox + (i / float(steps)) * gw

        beta = u / 4.0

        cos_term = math.cos(u) ** 2
        sinc_term = (math.sin(beta) / beta) ** 2 if abs(beta) > 1e-5 else 1.0

        I_total = cos_term * sinc_term

        y_val = oy - I_total * (gh - 20)
        y_env = oy - sinc_term * (gh - 20)

        pts_int.append((x, y_val))
        pts_env.append((x, y_env))

    d_int = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_int)
    d_env = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_env)

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (d_env, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_int, POS))

    x_m4 = ox + gw / 2 + 4 * (gw / 10.0)
    f.append(circle(x_m4, oy, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(x_m4, oy - 25, 'Зниклий максимум\n(m = 4, d/a = 4)', 9, NEG, 'middle', bold=True))

    f.append(line(ox + 20, oy - gh + 20, ox + 50, oy - gh + 20, color=POS, sw=2.2))
    f.append(text(ox + 56, oy - gh + 24, 'Повна інтенсивність I(y) = I₀ · cos²(α) · sinc²(β)', 10, POS, 'start', bold=True))

    f.append(line(ox + 20, oy - gh + 40, ox + 50, oy - gh + 40, color=NEG, sw=1.8, dash='5,4'))
    f.append(text(ox + 56, oy - gh + 44, 'Дифракційна огинаюча sinc²(β) від однієї щілини', 10, NEG, 'start', bold=True))

    render(os.path.join(IMG, 'intensity-pattern.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Геометрія просторової когерентності та розмір джерела
# ═══════════════════════════════════════════════════════════════════════════
def fig_coherence_geometry():
    W, H = 700, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Просторова когерентність: вплив розміру джерела світла', 16, INK, 'middle', bold=True))

    sx = 80
    sy = 175
    b_size = 70
    f.append(rect(sx - 8, sy - b_size / 2, 16, b_size, fill='#fde047', stroke='#ca8a04', sw=2, rx=3))
    f.append(text(sx - 18, sy + 4, 'b', 12, INK, 'end', bold=True, italic=True))
    f.append(text(sx, sy - b_size / 2 - 14, 'Простяжне\nджерело', 10, INK, 'middle', bold=True))

    top_src_y = sy - b_size / 2
    bot_src_y = sy + b_size / 2

    bx = 360
    d_size = 50
    s1_y = sy - d_size / 2
    s2_y = sy + d_size / 2
    slit_w = 6

    f.append(rect(bx - 3, 40, slit_w, s1_y - 40, fill=INK, stroke='none', sw=0))
    f.append(rect(bx - 3, s1_y + 6, slit_w, (s2_y - 6) - (s1_y + 6), fill=INK, stroke='none', sw=0))
    f.append(rect(bx - 3, s2_y + 6, slit_w, H - 40 - (s2_y + 6), fill=INK, stroke='none', sw=0))

    f.append(text(bx - 14, s1_y + 3, 'S₁', 11, POS, 'end', bold=True))
    f.append(text(bx - 14, s2_y + 3, 'S₂', 11, POS, 'end', bold=True))
    f.append(text(bx + 14, sy + 4, 'd', 11, NEG, 'start', bold=True, italic=True))

    f.append(line(sx, top_src_y, bx, s1_y, color=POS, sw=1.5))
    f.append(line(sx, top_src_y, bx, s2_y, color=POS, sw=1.5, dash='4,3'))

    f.append(line(sx, bot_src_y, bx, s1_y, color=NEG, sw=1.5, dash='4,3'))
    f.append(line(sx, bot_src_y, bx, s2_y, color=NEG, sw=1.5))

    f.append(line(sx, H - 35, bx, H - 35, color=INK, sw=1.5))
    f.append(line(sx, H - 40, sx, H - 30, color=INK, sw=1))
    f.append(line(bx, H - 40, bx, H - 30, color=INK, sw=1))
    f.append(text((sx + bx) / 2, H - 42, 'Відстань Lₛ', 11, INK, 'middle', bold=True))

    f.append(fitbox(410, 80, 270, 190,
                    'Умова збереження когерентності:\n'
                    'b · d / Lₛ < λ / 2\n\n'
                    '• Мале джерело (b → 0):\n'
                    '  Хвильовий фронт когерентний,\n'
                    '  висока контрастність смуг (V ≈ 1).\n\n'
                    '• Велике джерело (b · d / Lₛ > λ):\n'
                    '  Незалежні точки джерела дають\n'
                    '  зсунуті картини → змивання смуг (V → 0).',
                    size=10, color=INK, fill='#fdfbf7', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'coherence-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Квантове накопичення картини від поодиноких частинок
# ═══════════════════════════════════════════════════════════════════════════
def fig_quantum_buildup():
    W, H = 720, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, 'Квантове накопичення інтерференційної картини від поодиноких фотонів', 15, INK, 'middle', bold=True))

    pw, ph = 150, 220
    top_y = 55
    panels_x = [30, 200, 370, 540]
    titles = ['а) 50 фотонів', 'б) 500 фотонів', 'в) 5000 фотонів', 'г) Хвильовий розподіл']

    import random
    random.seed(42)

    def gen_points(n):
        pts = []
        while len(pts) < n:
            y_norm = random.uniform(-1, 1)
            prob = math.cos(math.pi * 2.5 * y_norm) ** 2
            if random.random() < prob:
                x_norm = random.uniform(-0.8, 0.8)
                pts.append((x_norm, y_norm))
        return pts

    pts_50 = gen_points(50)
    pts_500 = gen_points(500)
    pts_5000 = gen_points(2500)

    counts = [pts_50, pts_500, pts_5000]

    for idx in range(3):
        px = panels_x[idx]
        f.append(rect(px, top_y, pw, ph, fill='#0f172a', stroke=INK, sw=1.2, rx=4))
        f.append(text(px + pw / 2, top_y - 8, titles[idx], 11, INK, 'middle', bold=True))

        for (xn, yn) in counts[idx]:
            pt_x = px + pw / 2 + xn * (pw * 0.4)
            pt_y = top_y + ph / 2 + yn * (ph * 0.42)
            f.append(circle(pt_x, pt_y, 1.2, fill='#38bdf8', stroke='none', sw=0))

    px = panels_x[3]
    f.append(rect(px, top_y, pw, ph, fill='#fafbfc', stroke=INK, sw=1.2, rx=4))
    f.append(text(px + pw / 2, top_y - 8, titles[3], 11, INK, 'middle', bold=True))

    pts_wave = []
    steps = 150
    for i in range(steps + 1):
        yn = (i / float(steps) - 0.5) * 2.0
        prob = math.cos(math.pi * 2.5 * yn) ** 2
        pt_y = top_y + ph / 2 + yn * (ph * 0.42)
        pt_x = px + 15 + prob * (pw - 30)
        pts_wave.append((pt_x, pt_y))

    d_wave = "M " + " L ".join("%.1f %.1f" % pt for pt in pts_wave)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_wave, POS))
    f.append(line(px + 15, top_y + 10, px + 15, top_y + ph - 10, color=MUTED, sw=1, dash='3,3'))

    f.append(text(W / 2, H - 12, 'Поодинокі квантові події реєструються як точкові влучання; їхня статистика дає інтерференцію.', 11, MUTED, 'middle', italic=True))

    render(os.path.join(IMG, 'quantum-buildup.svg'), W, H, *f)

if __name__ == '__main__':
    fig_double_slit_setup()
    fig_intensity_pattern()
    fig_coherence_geometry()
    fig_quantum_buildup()
    print("All double-slit experiment figures generated successfully!")
