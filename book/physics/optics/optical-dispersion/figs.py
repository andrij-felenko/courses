# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw))

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Геометрія дисперсії світла в трикутній призмі
# ═══════════════════════════════════════════════════════════════════════════
def fig_prism_dispersion_geometry():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Розщеплення білого світла в оптичній призмі', 16, INK, 'middle', bold=True))

    px1, py1 = 300, 75
    px2, py2 = 180, 290
    px3, py3 = 420, 290
    f.append(polygon([(px1, py1), (px2, py2), (px3, py3)], fill='#eaf2fb', stroke=INK, sw=2))
    f.append(text(px1, py1 - 12, 'A (заломлювальний кут)', 11, INK, 'middle'))
    f.append(text((px2 + px3) / 2, py2 + 18, 'основа призми', 10, MUTED, 'middle'))

    in_x1, in_y1 = 50, 230
    in_x2, in_y2 = 230, 200
    f.append(line(in_x1, in_y1, in_x2, in_y2, color='#475569', sw=3.5))
    f.append(arrow(in_x1, in_y1, in_x2, in_y2, color='#0f172a', sw=3.5))
    f.append(text(in_x1 + 10, in_y1 - 12, 'біле світло', 12, INK, 'start', bold=True))

    norm1_x1, norm1_y1 = 185, 140
    norm1_x2, norm1_y2 = 275, 260
    f.append(line(norm1_x1, norm1_y1, norm1_x2, norm1_y2, color=MUTED, sw=1, dash='4,3'))
    f.append(text(norm1_x1 - 15, norm1_y1 - 5, 'нормаль 1', 9, MUTED, 'end'))

    red_in_x, red_in_y = 230, 200
    red_out_x, red_out_y = 350, 215
    f.append(line(red_in_x, red_in_y, red_out_x, red_out_y, color='#dc2626', sw=2.2))

    blue_in_x, blue_in_y = 230, 200
    blue_out_x, blue_out_y = 360, 230
    f.append(line(blue_in_x, blue_in_y, blue_out_x, blue_out_y, color='#2563eb', sw=2.2))

    red_end_x, red_end_y = 560, 240
    f.append(arrow(red_out_x, red_out_y, red_end_x, red_end_y, color='#dc2626', sw=2.5))
    f.append(text(red_end_x + 10, red_end_y + 4, 'червоний (λ = 700 нм, n - менше)', 11, '#dc2626', 'start', bold=True))

    green_end_x, green_end_y = 560, 265
    f.append(arrow((red_out_x + blue_out_x) / 2, (red_out_y + blue_out_y) / 2, green_end_x, green_end_y, color='#16a34a', sw=2.0))
    f.append(text(green_end_x + 10, green_end_y + 4, 'зелений (λ = 546 нм)', 11, '#16a34a', 'start'))

    blue_end_x, blue_end_y = 560, 290
    f.append(arrow(blue_out_x, blue_out_y, blue_end_x, blue_end_y, color='#2563eb', sw=2.5))
    f.append(text(blue_end_x + 10, blue_end_y + 4, 'фіолетовий (λ = 400 нм, n - більше)', 11, '#2563eb', 'start', bold=True))

    f.append(line(in_x2, in_y2, 540, 153, color=MUTED, sw=1.2, dash='3,3'))
    f.append(text(545, 150, 'початковий напрямок', 10, MUTED, 'start'))

    f.append(text(460, 195, 'кутова дисперсія dδ/dλ', 11, INK, 'middle', italic=True))

    f.append(fitbox(55, 55, 140, 115,
                    'Оптична скляна призма:\nn(фіолетовий) > n(червоний)\n\nКоротші хвилі (сині)\nзазнають сильнішого\nзаломлення, ніж довші (червоні).',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'prism-dispersion-geometry.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Нормальна та аномальна дисперсія (залежність n(λ) біля резонансу)
# ═══════════════════════════════════════════════════════════════════════════
def fig_normal_vs_anomalous_dispersion():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Залежність показника заломлення n(λ) та аномальна дисперсія', 16, INK, 'middle', bold=True))

    ox, oy = 75, 310
    gw, gh = 440, 240

    # Сітка та рамка
    f.append(rect(ox, oy - gh, gw, gh, fill='#fafbfc', stroke=MUTED, sw=1))

    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.5))
    f.append(text(ox + gw / 2, oy + 38, 'Довжина хвилі λ (частота ω спадає ➔)', 12, INK, 'middle', bold=True))
    f.append(text(ox - 45, oy - gh / 2, 'Показник заломлення n(λ)', 12, INK, 'middle', bold=True))

    # Смуга резонансного поглинання (зона аномальної дисперсії)
    res_x1 = ox + 180
    res_x2 = ox + 260
    f.append(rect(res_x1, oy - gh, res_x2 - res_x1, gh, fill='#fee2e2', stroke='none', sw=0))
    f.append(line(res_x1, oy - gh, res_x1, oy, color=NEG, sw=1, dash='4,3'))
    f.append(line(res_x2, oy - gh, res_x2, oy, color=NEG, sw=1, dash='4,3'))
    f.append(text((res_x1 + res_x2) / 2, oy - gh + 18, 'Смуга поглинання (λ₀)', 10, NEG, 'middle', bold=True))

    # Крива кривої n(λ)
    pts = []
    steps = 100
    for i in range(steps + 1):
        x_rel = i / float(steps)
        x_px = ox + x_rel * gw

        dx = (x_rel - 0.5) * 10.0
        n_val = 1.48 - 0.08 * x_rel - 0.22 * dx / (dx * dx + 0.9)
        y_px = oy - (n_val - 1.25) / 0.5 * gh

        y_px = max(oy - gh + 8, min(oy - 8, y_px))
        pts.append((x_px, y_px))

    pts_norm1 = [p for p in pts if p[0] < res_x1]
    pts_anom  = [p for p in pts if res_x1 <= p[0] <= res_x2]
    pts_norm2 = [p for p in pts if p[0] > res_x2]

    d_n1 = "M " + " L ".join("%.1f %.1f" % p for p in pts_norm1)
    d_an = "M " + " L ".join("%.1f %.1f" % p for p in pts_anom)
    d_n2 = "M " + " L ".join("%.1f %.1f" % p for p in pts_norm2)

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_n1, POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_an, NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_n2, POS))

    # Підписи областей (розміщені у вільних місцях графіку, де немає перетину ліній)
    f.append(text(ox + 85, oy - 200, 'Нормальна дисперсія\ndn/dλ < 0', 10, POS, 'middle', bold=True))
    f.append(text((res_x1 + res_x2) / 2, oy - 45, 'Аномальна\ndn/dλ > 0', 10, NEG, 'middle', bold=True))
    f.append(text(ox + 350, oy - 200, 'Нормальна дисперсія\ndn/dλ < 0', 10, POS, 'middle', bold=True))

    # Позначки осі Y (значення n)
    for n_val in [1.3, 1.4, 1.5, 1.6, 1.7]:
        y_px = oy - (n_val - 1.25) / 0.5 * gh
        f.append(line(ox - 4, y_px, ox, y_px, color=INK, sw=1))
        f.append(text(ox - 8, y_px + 4, '%.1f' % n_val, 10, MUTED, 'end'))

    # Правий інформаційний блок
    f.append(fitbox(535, 75, 165, 140,
                    'Нормальна дисперсія:\nз ростом довжини хвилі λ\nпоказник n спадає (dn/dλ < 0).\n\nАномальна дисперсія:\nспостерігається всередині\nсмуги резонансного\nпоглинання (dn/dλ > 0).',
                    size=10, color=INK, fill='#ffffff', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'normal-vs-anomalous-dispersion.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Хроматичне розширення світлового імпульсу у волокні (GVD)
# ═══════════════════════════════════════════════════════════════════════════
def fig_pulse_chromatic_broadening():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Хроматичне розширення імпульсу (дисперсія групової швидкості)', 16, INK, 'middle', bold=True))

    # Оптичне волокно / середовище
    fx, fy, fw, fh = 180, 130, 360, 100
    f.append(rect(fx, fy, fw, fh, fill='#f1f5f9', stroke='#94a3b8', sw=1.5, rx=6))
    f.append(line(fx, fy + fh / 2, fx + fw, fy + fh / 2, color='#cbd5e1', sw=1.2, dash='6,4'))
    f.append(text(fx + fw / 2, fy + fh - 12, 'оптичне середовище / волокно (довжина L)', 11, MUTED, 'middle'))

    # Вхідний вузький імпульс (ліворуч від волокна)
    in_cx = 100
    f.append(text(in_cx, fy - 18, 'Вхідний імпульс τ₀', 12, INK, 'middle', bold=True))
    pts_in = []
    for i in range(-30, 31):
        x = in_cx + i
        y = fy + fh / 2 - 40 * math.exp(- (i / 10.0)**2)
        pts_in.append((x, y))
    d_in = "M " + " L ".join("%.1f %.1f" % p for p in pts_in)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_in, POS))

    f.append(circle(in_cx, fy + fh / 2 - 15, 4, fill='#dc2626', stroke='none'))
    f.append(circle(in_cx - 4, fy + fh / 2 - 15, 4, fill='#16a34a', stroke='none'))
    f.append(circle(in_cx + 4, fy + fh / 2 - 15, 4, fill='#2563eb', stroke='none'))
    f.append(text(in_cx, fy + fh + 25, 'суміш довжин хвиль\n(вузький у часі)', 10, MUTED, 'middle'))

    # Стрілка проходження через волокно
    f.append(arrow(fx + 20, fy + fh / 2, fx + fw - 20, fy + fh / 2, color=FIELD, sw=2))

    # Вихідний розширений імпульс (праворуч від волокна)
    out_cx = 620
    f.append(text(out_cx, fy - 18, 'Вихідний імпульс τ(L) > τ₀', 12, INK, 'middle', bold=True))
    pts_out = []
    for i in range(-55, 56):
        x = out_cx + i
        y = fy + fh / 2 - 22 * math.exp(- (i / 25.0)**2)
        pts_out.append((x, y))
    d_out = "M " + " L ".join("%.1f %.1f" % p for p in pts_out)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_out, NEG))

    f.append(circle(out_cx + 25, fy + fh / 2 - 10, 5, fill='#dc2626', stroke='none'))
    f.append(text(out_cx + 25, fy + fh / 2 - 22, 'λ_червоний (швидше)', 9, '#dc2626', 'middle', bold=True))

    f.append(circle(out_cx, fy + fh / 2 - 10, 5, fill='#16a34a', stroke='none'))
    f.append(text(out_cx, fy + fh / 2 - 22, 'λ_зелений', 9, '#16a34a', 'middle'))

    f.append(circle(out_cx - 25, fy + fh / 2 - 10, 5, fill='#2563eb', stroke='none'))
    f.append(text(out_cx - 25, fy + fh / 2 - 22, 'λ_синій (повільніше)', 9, '#2563eb', 'middle', bold=True))

    f.append(text(out_cx, fy + fh + 25, 'часове розширення Δτ\nчерез v_g(λ) ≠ const', 10, NEG, 'middle', bold=True))

    # Нижній пояснювальний блок
    f.append(fitbox(180, 270, 360, 70,
                    'Різні спектральні складові імпульсу рухаються з різною груповою швидкістю v_g(λ).\nУ результаті імпульс розмивається у часі, обмежуючи швидкість передачі даних у зв\'язку.',
                    size=10, color=INK, fill='#ffffff', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'pulse-chromatic-broadening.svg'), W, H, *f)


if __name__ == '__main__':
    fig_prism_dispersion_geometry()
    fig_normal_vs_anomalous_dispersion()
    fig_pulse_chromatic_broadening()
    print("Figures generated successfully.")
