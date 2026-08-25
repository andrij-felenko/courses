# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Побудова зон Френеля для сферичної хвилі
# ═══════════════════════════════════════════════════════════════════════════
def fig_fresnel_zones_geometry():
    W, H = 740, 420
    f = []

    # Джерело S та точка спостереження P
    sx, sy = 80, 210
    px, py = 660, 210
    
    # Хвильовий фронт Sigma (дуга кола з центром в S)
    r_wave = 220
    fx = sx + r_wave # X координата вершини хвильового фронту (300)
    
    f.append(line(sx - 30, sy, px + 30, py, color=MUTED, sw=1.2, dash='6,4')) # оптична вісь Z
    f.append(text(px + 35, py + 4, 'Z', 12, MUTED, 'start', bold=True, italic=True))

    # Джерело S
    f.append(circle(sx, sy, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(text(sx, sy - 14, 'S (Джерело)', 12, POS, 'middle', bold=True))

    # Точка спостереження P
    f.append(circle(px, py, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(px, py - 14, 'P (Точка спостереження)', 12, NEG, 'middle', bold=True))

    # Вторинні сферичні зони на хвильовій поверхні (дуги з точки S)
    # Зони M0, M1, M2, M3
    angles = [0, 16, 28, 38]
    colors = [INK, POS, FIELD, NEG]
    
    # Дуга хвильового фронту
    arc_pts = []
    for deg in range(-45, 46):
        rad = math.radians(deg)
        x = sx + r_wave * math.cos(rad)
        y = sy + r_wave * math.sin(rad)
        arc_pts.append((x, y))
    
    # Малюємо хвильовий фронт (дугу)
    path_d = ["M %.1f %.1f" % arc_pts[0]]
    for x, y in arc_pts[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), INK))
    f.append(text(fx - 15, sy - r_wave * math.sin(math.radians(45)) - 10, 'Хвильовий фронт Σ', 12, INK, 'end', bold=True))

    # Лінії відстаней від точок зон Mk до точки P
    # Відстань b від вершини O (fx, sy) до P
    b_dist = px - fx # 360 px
    f.append(line(fx, sy, px, py, color=INK, sw=2))
    f.append(text((fx + px) / 2, sy + 18, 'b', 13, INK, 'middle', bold=True, italic=True))

    # Точки на фронті і промені до P
    for i, deg in enumerate(angles[1:], 1):
        rad = math.radians(deg)
        mx = sx + r_wave * math.cos(rad)
        my = sy + r_wave * math.sin(rad)

        # Симетричні точки внизу і вгорі
        f.append(circle(mx, my, 4, fill=colors[i], stroke=INK, sw=1))
        f.append(line(mx, my, px, py, color=colors[i], sw=1.5, dash='4,3'))
        
        # Позначка зони Mk
        label_k = 'M%d' % i
        f.append(text(mx - 14, my - 6, label_k, 11, colors[i], 'end', bold=True))

        # Текст відстані
        dist_text = 'b + %d·λ/2' % i if i > 1 else 'b + λ/2'
        tx = (mx + px) / 2 + 10
        ty = (my + py) / 2 - 6 * i
        f.append(text(tx, ty, dist_text, 10, colors[i], 'start', bold=True))

    # Розміри a та b
    f.append(line(sx, sy + 140, fx, sy + 140, color=MUTED, sw=1.2))
    f.append(line(sx, sy + 135, sx, sy + 145, color=MUTED, sw=1.2))
    f.append(line(fx, sy + 135, fx, sy + 145, color=MUTED, sw=1.2))
    f.append(text((sx + fx) / 2, sy + 158, 'a (відстань від джерела)', 11, MUTED, 'middle'))

    f.append(line(fx, sy + 140, px, sy + 140, color=MUTED, sw=1.2))
    f.append(line(px, sy + 135, px, sy + 145, color=MUTED, sw=1.2))
    f.append(text((fx + px) / 2, sy + 158, 'b (відстань до екрана)', 11, MUTED, 'middle'))

    # Пояснення різниці ходу
    f.append(textbox(370, 385, 'Сусідні зони Френеля створюють у точці P коливання у протифазі (різниця ходу Δ = λ/2)', size=12, pad=8, fill=FILL, stroke=LINE, bold=False)[0])

    render(os.path.join(IMG, 'fresnel-zones-geometry.svg'), W, H, *f, title='Побудова зон Френеля для сферичної хвилі')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Формування центральної світлої плями Араґо (Пуассона)
# ═══════════════════════════════════════════════════════════════════════════
def fig_arago_spot_formation():
    W, H = 740, 400
    f = []

    # Вхідний плоский хвильовий фронт
    wx = 80
    f.append(line(wx, 50, wx, 350, color=NEG, sw=2))
    f.append(text(wx - 10, 65, 'Плоска хвиля', 12, NEG, 'end', bold=True))
    for y in range(80, 330, 40):
        f.append(arrow(wx - 40, y, wx, y, color=NEG, sw=1.5))

    # Круглий непрозорий диск (перешкода)
    dx = 240
    dy = 200
    r_disk = 60
    f.append(line(dx, dy - r_disk, dx, dy + r_disk, color=INK, sw=7)) # Непрозорий екран-диск
    f.append(circle(dx, dy - r_disk, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(dx, dy + r_disk, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(dx - 12, dy, 'Непрозорий\nдиск (R)', 11, INK, 'end', bold=True))

    # Конус геометричної тіні за диском
    ex = 620 # Екран
    f.append(line(ex, 40, ex, 360, color=LINE, sw=2))
    f.append(text(ex + 10, 55, 'Екран', 12, INK, 'start', bold=True))

    # Межі геометричної тіні (прямі лінії від диска)
    f.append(line(dx, dy - r_disk, ex, dy - r_disk, color=MUTED, sw=1.2, dash='5,4'))
    f.append(line(dx, dy + r_disk, ex, dy + r_disk, color=MUTED, sw=1.2, dash='5,4'))
    
    # Затінена область
    f.append(rect(dx, dy - r_disk, ex - dx, 2 * r_disk, fill='#eaeded', stroke='none'))

    # Оптична вісь Z
    f.append(line(dx - 60, dy, ex + 30, dy, color=MUTED, sw=1.2, dash='6,4'))
    f.append(text(ex + 35, dy + 4, 'Z', 12, MUTED, 'start', bold=True, italic=True))

    # Дифраговані хвилі від країв диска до центральної точки на екрані P0
    f.append(arrow(dx, dy - r_disk, ex, dy, color=POS, sw=2))
    f.append(arrow(dx, dy + r_disk, ex, dy, color=POS, sw=2))

    # Пляма Араґо у центрі тіні
    f.append(circle(ex, dy, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(text(ex - 15, dy - 15, 'Світла пляма Араґо (P₀)', 12, POS, 'end', bold=True))

    # Графік інтенсивності на екрані
    # Намалюємо криву інтенсивності з центральним піком прямо поверх екрана
    curve_pts = []
    for y_pos in range(60, 341, 5):
        y_rel = y_pos - dy
        # Інтенсивність з піком в центрі y_rel = 0 та дифракційними кільцями
        if abs(y_rel) < 8:
            I_val = 60 # Яскравий центральний пік
        elif abs(y_rel) < 60:
            I_val = 10 * math.exp(- (abs(y_rel) - 30)**2 / 200) # Тінь з загасанням
        else:
            I_val = 40 + 10 * math.cos(abs(y_rel) / 8) # Зовнішнє поле
        x_val = ex + I_val
        curve_pts.append((x_val, y_pos))

    path_i = ["M %.1f %.1f" % curve_pts[0]]
    for x, y in curve_pts[1:]:
        path_i.append("L %.1f %.1f" % (x, y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(path_i), POS))
    f.append(text(ex + 75, dy + 45, 'Профіль\nінтенсивності I(y)', 11, POS, 'start', bold=True))

    # Пояснювальний блок
    f.append(textbox(380, 365, 'Вторинні хвилі від усіх точок круглого краю диска долають ОДНАКОВУ відстань до осі Z\nі додаються в точці P₀ строго в ОДНАКОВІЙ фазі, утворюючи яскраву світлу пляму.', size=11, pad=8, fill=FILL, stroke=LINE)[0])

    render(os.path.join(IMG, 'arago-spot-formation.svg'), W, H, *f, title='Формування центральної світлої плями Араґо (Пуассона)')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Дифракція Фраунгофера на одній щілині
# ═══════════════════════════════════════════════════════════════════════════
def fig_single_slit_diffraction():
    W, H = 740, 420
    f = []

    # Щілина шириною a
    sx = 160
    sy = 190
    a_h = 70 # висота щілини
    
    # Верхня і нижня непрозорі частини екрана
    f.append(rect(sx - 5, 40, 10, sy - a_h / 2 - 40, fill=INK, stroke='none'))
    f.append(rect(sx - 5, sy + a_h / 2, 10, H - 40 - (sy + a_h / 2), fill=INK, stroke='none'))

    # Позначення ширини щілини a
    f.append(line(sx - 20, sy - a_h / 2, sx - 20, sy + a_h / 2, color=POS, sw=1.5))
    f.append(line(sx - 25, sy - a_h / 2, sx - 15, sy - a_h / 2, color=POS, sw=1.5))
    f.append(line(sx - 25, sy + a_h / 2, sx - 15, sy + a_h / 2, color=POS, sw=1.5))
    f.append(text(sx - 30, sy + 4, 'a', 13, POS, 'end', bold=True, italic=True))

    # Вхідні паралельні промені
    for y in range(sy - 30, sy + 31, 20):
        f.append(arrow(sx - 90, y, sx - 5, y, color=NEG, sw=1.5))
    f.append(text(sx - 95, sy - 50, 'Плоска хвиля (λ)', 11, NEG, 'end', bold=True))

    # Оптична вісь Z
    ex = 540 # Позиція екрана
    f.append(line(sx - 40, sy, ex + 140, sy, color=MUTED, sw=1.2, dash='6,4'))
    f.append(text(ex + 145, sy + 4, 'Z', 12, MUTED, 'start', bold=True, italic=True))

    # Дифраговані промені під кутом θ
    theta_deg = 22.0
    t_rad = math.radians(theta_deg)
    
    # Крайні та центральний промені під кутом θ
    y_top = sy - a_h / 2
    y_bot = sy + a_h / 2
    
    f.append(arrow(sx, y_top, sx + 220, y_top + 220 * math.tan(t_rad), color=FIELD, sw=1.5))
    f.append(arrow(sx, sy, sx + 220, sy + 220 * math.tan(t_rad), color=FIELD, sw=1.5))
    f.append(arrow(sx, y_bot, sx + 220, y_bot + 220 * math.tan(t_rad), color=FIELD, sw=1.5))

    # Перпендикуляр різниці ходу ΔL = a·sin θ
    px_perp = sx + a_h * math.sin(t_rad)
    py_perp = y_bot
    f.append(line(sx, y_top, px_perp, py_perp, color=POS, sw=2, dash='4,3'))
    f.append(text(sx + 35, y_bot + 12, 'ΔL = a·sin θ', 11, POS, 'start', bold=True))

    # Екран та крива інтенсивності
    f.append(line(ex, 40, ex, H - 40, color=LINE, sw=2))
    f.append(text(ex - 15, 55, 'Екран', 12, INK, 'end', bold=True))

    # Профіль інтенсивності I(θ) = I0 * (sin(β)/β)^2
    intensity_pts = []
    for y_pos in range(50, H - 40, 2):
        y_rel = (y_pos - sy) / 25.0 # масштабований кут
        if abs(y_rel) < 1e-4:
            val = 1.0
        else:
            beta = math.pi * y_rel
            val = (math.sin(beta) / beta) ** 2
        
        x_val = ex + val * 110 # амплітуда графіку 110px
        intensity_pts.append((x_val, y_pos))

    path_i = ["M %.1f %.1f" % intensity_pts[0]]
    for x, y in intensity_pts[1:]:
        path_i.append("L %.1f %.1f" % (x, y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_i), POS))

    # Позначення максимумів та мінімумів
    f.append(circle(ex + 110, sy, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(ex + 120, sy + 4, 'Головний максимум (I₀)', 11, POS, 'start', bold=True))

    y_min1_up = sy - 25.0
    y_min1_dn = sy + 25.0
    f.append(line(ex - 5, y_min1_up, ex + 25, y_min1_up, color=NEG, sw=1.5))
    f.append(text(ex + 30, y_min1_up + 4, 'Мінімум: sin θ = λ/a', 10, NEG, 'start', bold=True))
    
    f.append(line(ex - 5, y_min1_dn, ex + 25, y_min1_dn, color=NEG, sw=1.5))
    f.append(text(ex + 30, y_min1_dn + 4, 'Мінімум: sin θ = -λ/a', 10, NEG, 'start', bold=True))

    f.append(textbox(370, 390, 'Розподіл інтенсивності: I(θ) = I₀ · (sin β / β)²,  де β = (π · a · sin θ) / λ', size=12, pad=8, fill=FILL, stroke=LINE)[0])

    render(os.path.join(IMG, 'single-slit-diffraction.svg'), W, H, *f, title='Дифракція Фраунгофера на одній щілині')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Пляма Ейрі та критерій роздільної здатності Релея
# ═══════════════════════════════════════════════════════════════════════════
def fig_airy_disk_rayleigh():
    W, H = 740, 420
    f = []

    # Ліва частина: 2D пляма Ейрі (концентричні кола)
    cx, cy = 160, 190
    
    # Кільця Ейрі
    f.append(circle(cx, cy, 110, fill='#f8f9fa', stroke=MUTED, sw=1))
    f.append(circle(cx, cy, 75, fill='#e5e7eb', stroke=MUTED, sw=1))
    f.append(circle(cx, cy, 50, fill='#f8f9fa', stroke=MUTED, sw=1))
    f.append(circle(cx, cy, 32, fill=POS, stroke=INK, sw=1.5)) # Центральний диск Ейрі

    f.append(text(cx, cy + 4, 'I₀', 14, BG, 'middle', bold=True))
    f.append(text(cx, cy - 130, 'Пляма Ейрі (2D)', 13, INK, 'middle', bold=True))

    # Радіус першого темного кільця r_Airy = 1.22 lambda f / D
    f.append(line(cx, cy, cx + 50, cy, color=NEG, sw=1.8))
    f.append(line(cx + 50, cy - 5, cx + 50, cy + 5, color=NEG, sw=1.8))
    f.append(text(cx + 25, cy - 8, 'θ₁ = 1.22 λ/D', 11, NEG, 'middle', bold=True))

    # Права частина: Критерій Релея (три випадки A, B, C)
    rx = 360
    
    # Випадок A: Розділені (Δθ > 1.22 λ/D)
    y_A = 90
    f.append(text(rx, y_A, 'A. Розділені джерела (Δθ > 1.22 λ/D)', 11, INK, 'start', bold=True))
    # Малюємо дві окремі криві з виразним провалом
    pts_a1, pts_a2, pts_sum = [], [], []
    for x in range(rx + 160, rx + 360, 2):
        x_rel1 = (x - (rx + 220)) / 15.0
        x_rel2 = (x - (rx + 300)) / 15.0
        val1 = math.exp(- x_rel1**2) * 35
        val2 = math.exp(- x_rel2**2) * 35
        pts_a1.append((x, y_A + 55 - val1))
        pts_a2.append((x, y_A + 55 - val2))
        pts_sum.append((x, y_A + 55 - (val1 + val2)))

    f.append(line(rx + 150, y_A + 55, rx + 370, y_A + 55, color=MUTED, sw=1))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_a1]), NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_a2]), FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_sum]), POS))
    f.append(text(rx + 340, y_A + 20, 'Провал > 19%', 10, POS, 'end', bold=True))

    # Випадок B: Границя Релея (Δθ = 1.22 λ/D)
    y_B = 190
    f.append(text(rx, y_B, 'B. Границя Релея (Δθ = 1.22 λ/D)', 11, INK, 'start', bold=True))
    pts_b1, pts_b2, pts_sum_b = [], [], []
    for x in range(rx + 160, rx + 360, 2):
        x_rel1 = (x - (rx + 235)) / 15.0
        x_rel2 = (x - (rx + 285)) / 15.0
        val1 = math.exp(- x_rel1**2) * 35
        val2 = math.exp(- x_rel2**2) * 35
        pts_b1.append((x, y_B + 55 - val1))
        pts_b2.append((x, y_B + 55 - val2))
        pts_sum_b.append((x, y_B + 55 - (val1 + val2)))

    f.append(line(rx + 150, y_B + 55, rx + 370, y_B + 55, color=MUTED, sw=1))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_b1]), NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_b2]), FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_sum_b]), POS))
    f.append(text(rx + 340, y_B + 22, 'Провал = 19% (81% I_max)', 10, POS, 'end', bold=True))

    # Випадок C: Нерозділені (Δθ < 1.22 λ/D)
    y_C = 290
    f.append(text(rx, y_C, 'C. Нерозділені джерела (Δθ < 1.22 λ/D)', 11, INK, 'start', bold=True))
    pts_c1, pts_c2, pts_sum_c = [], [], []
    for x in range(rx + 160, rx + 360, 2):
        x_rel1 = (x - (rx + 250)) / 15.0
        x_rel2 = (x - (rx + 270)) / 15.0
        val1 = math.exp(- x_rel1**2) * 35
        val2 = math.exp(- x_rel2**2) * 35
        pts_c1.append((x, y_C + 55 - val1))
        pts_c2.append((x, y_C + 55 - val2))
        pts_sum_c.append((x, y_C + 55 - (val1 + val2)))

    f.append(line(rx + 150, y_C + 55, rx + 370, y_C + 55, color=MUTED, sw=1))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(["M %.1f %.1f" % p for p in pts_sum_c]), POS))
    f.append(text(rx + 340, y_C + 20, 'Один розмитий пік', 10, POS, 'end', bold=True))

    f.append(textbox(370, 395, 'Критерій Релея: дві деталі оптично розділені, якщо центральний максимум однієї плями Ейрі\nзбігається з першим мінімумом другої плями (кутова відстань θ_min = 1.22 · λ / D).', size=11, pad=8, fill=FILL, stroke=LINE)[0])

    render(os.path.join(IMG, 'airy-disk-rayleigh.svg'), W, H, *f, title='Пляма Ейрі та критерій роздільної здатності Релея')

if __name__ == '__main__':
    fig_fresnel_zones_geometry()
    fig_arago_spot_formation()
    fig_single_slit_diffraction()
    fig_airy_disk_rayleigh()
    print("Figures generated successfully.")
