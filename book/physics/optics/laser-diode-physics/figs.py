# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path_shape(d, fill='none', stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def ellipse_shape(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d}/>'

def polygon_shape(pts, fill=FILL, stroke=LINE, sw=1.5):
    s = stroke if stroke else 'none'
    return f'<polygon points="{pts}" fill="{fill}" stroke="{s}" stroke-width="{sw:.1f}"/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Подвійна гетероструктура: зонна діаграма та хвилевідний ефект
# ═══════════════════════════════════════════════════════════════════════════
def fig_heterostructure_band():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Подвійна гетероструктура: зонна діаграма та хвилевідний ефект', 16, INK, 'middle', bold=True))

    x1, x2, x3, x4 = 60, 240, 480, 660
    
    y_top = 50
    h_top = 200
    
    f.append(rect(x1, y_top, x2 - x1, h_top, fill='#f1f5f9', stroke='none'))
    f.append(rect(x2, y_top, x3 - x2, h_top, fill='#e0f2fe', stroke='none'))
    f.append(rect(x3, y_top, x4 - x3, h_top, fill='#f1f5f9', stroke='none'))
    
    f.append(line(x2, y_top, x2, y_top + h_top, color=MUTED, sw=1.5, dash='4,3'))
    f.append(line(x3, y_top, x3, y_top + h_top, color=MUTED, sw=1.5, dash='4,3'))
    
    ec_p = y_top + 40
    ec_act = y_top + 90
    ec_n = y_top + 60
    f.append(line(x1, ec_p, x2, ec_p, color=NEG, sw=2.5))
    f.append(line(x2, ec_p, x2, ec_act, color=NEG, sw=2.5))
    f.append(line(x2, ec_act, x3, ec_act, color=NEG, sw=2.5))
    f.append(line(x3, ec_act, x3, ec_n, color=NEG, sw=2.5))
    f.append(line(x3, ec_n, x4, ec_n, color=NEG, sw=2.5))
    f.append(text(x1 + 10, ec_p - 8, 'Зона провідності E_c', 11, NEG, 'start', bold=True))
    
    ev_p = y_top + 170
    ev_act = y_top + 150
    ev_n = y_top + 190
    f.append(line(x1, ev_p, x2, ev_p, color=POS, sw=2.5))
    f.append(line(x2, ev_p, x2, ev_act, color=POS, sw=2.5))
    f.append(line(x2, ev_act, x3, ev_act, color=POS, sw=2.5))
    f.append(line(x3, ev_act, x3, ev_n, color=POS, sw=2.5))
    f.append(line(x3, ev_n, x4, ev_n, color=POS, sw=2.5))
    f.append(text(x1 + 10, ev_p + 16, 'Валентна зона E_v', 11, POS, 'start', bold=True))
    
    for ex in [270, 310, 350, 390, 430]:
        f.append(circle(ex, ec_act + 12, 5, fill=NEG, stroke='none'))
    f.append(text(350, ec_act + 28, 'Електрони e⁻ (накопичення)', 10, NEG, 'middle'))

    for hx in [280, 320, 360, 400, 440]:
        f.append(circle(hx, ev_act - 12, 5, fill='#ffffff', stroke=POS, sw=2))
    f.append(text(360, ev_act - 24, 'Дірки h⁺ (накопичення)', 10, POS, 'middle'))

    f.append(arrow(360, ec_act + 34, 360, ev_act - 32, color=FIELD, sw=2))
    f.append(text(375, (ec_act + ev_act) / 2, 'h·ν', 12, FIELD, 'start', bold=True, italic=True))

    f.append(text((x1 + x2) / 2, y_top + 18, 'P-Al₀.₃Ga₀.₇As', 12, INK, 'middle', bold=True))
    f.append(text((x2 + x3) / 2, y_top + 18, 'p-GaAs (активний шар ~0.1 мкм)', 12, FIELD, 'middle', bold=True))
    f.append(text((x3 + x4) / 2, y_top + 18, 'N-Al₀.₃Ga₀.₇As', 12, INK, 'middle', bold=True))

    y_bot = 280
    h_bot = 110
    
    f.append(line(x1 - 20, y_bot + h_bot, x4 + 20, y_bot + h_bot, color=MUTED, sw=1))
    
    n_cladd = y_bot + 75
    n_act = y_bot + 25
    f.append(line(x1, n_cladd, x2, n_cladd, color=MUTED, sw=2))
    f.append(line(x2, n_cladd, x2, n_act, color=MUTED, sw=2))
    f.append(line(x2, n_act, x3, n_act, color=MUTED, sw=2))
    f.append(line(x3, n_act, x3, n_cladd, color=MUTED, sw=2))
    f.append(line(x3, n_cladd, x4, n_cladd, color=MUTED, sw=2))
    f.append(text(x1 + 10, n_cladd - 8, 'n = 3.4 (обкладка)', 10, MUTED, 'start'))
    f.append(text((x2 + x3) / 2, n_act - 8, 'n = 3.6 (активна зона)', 11, MUTED, 'middle', bold=True))

    pts = []
    for x in range(int(x1), int(x4) + 1):
        xc = (x2 + x3) / 2
        sigma = 60
        amp = 55
        y = (y_bot + h_bot) - amp * math.exp(-((x - xc) ** 2) / (2 * sigma ** 2))
        pts.append((x, y))
    
    path_d = f"M {pts[0][0]},{pts[0][1]:.1f} " + " ".join(f"L {px},{py:.1f}" for px, py in pts[1:])
    f.append(path_shape(path_d, fill='none', stroke=FIELD, sw=2.5))
    f.append(text(x3 + 40, y_bot + 45, 'Профіль моди I(x)', 11, FIELD, 'start', bold=True))

    render(os.path.join(IMG, 'heterostructure-band.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Резонатор Фабрі-Перо та поздовжні моди лазерного діода
# ═══════════════════════════════════════════════════════════════════════════
def fig_cavity_modes():
    W, H = 720, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Резонатор Фабрі-Перо та поздовжні моди лазерного діода', 16, INK, 'middle', bold=True))

    cx1, cx2 = 120, 560
    cy = 60
    ch = 90
    
    f.append(rect(cx1, cy, cx2 - cx1, ch, fill='#e2e8f0', stroke=MUTED, sw=2, rx=4))
    f.append(rect(cx1, cy + 35, cx2 - cx1, 20, fill='#38bdf8', stroke='none'))
    f.append(text((cx1 + cx2) / 2, cy + 49, 'Активна зона (підсилююче середовище)', 11, INK, 'middle', bold=True))
    
    f.append(rect(cx1 - 6, cy - 5, 6, ch + 10, fill='#94a3b8', stroke=MUTED, sw=1.5))
    f.append(rect(cx2, cy - 5, 6, ch + 10, fill='#94a3b8', stroke=MUTED, sw=1.5))
    f.append(text(cx1 - 10, cy + ch + 18, 'Дзеркало R₁ ≈ 0.32', 10, MUTED, 'middle'))
    f.append(text(cx2 + 10, cy + ch + 18, 'Дзеркало R₂ ≈ 0.32', 10, MUTED, 'middle'))
    
    f.append(line(cx1, cy + ch + 30, cx2, cy + ch + 30, color=INK, sw=1.5))
    f.append(line(cx1, cy + ch + 24, cx1, cy + ch + 36, color=INK, sw=1.5))
    f.append(line(cx2, cy + ch + 24, cx2, cy + ch + 36, color=INK, sw=1.5))
    f.append(text((cx1 + cx2) / 2, cy + ch + 44, 'Довжина резонатора L (250–500 мкм)', 11, INK, 'middle', bold=True))
    
    f.append(arrow(cx2 + 8, cy + 45, cx2 + 100, cy + 45, color=POS, sw=3))
    f.append(text(cx2 + 55, cy + 32, 'Лазерний промінь', 11, POS, 'middle', bold=True))

    gx = 100
    gy = 340
    gw = 540
    gh = 120
    
    f.append(line(gx, gy, gx + gw, gy, color=MUTED, sw=1.5))
    f.append(line(gx, gy, gx, gy - gh, color=MUTED, sw=1.5))
    f.append(text(gx + gw + 10, gy + 4, 'Довжина хвилі λ', 11, INK, 'start'))
    f.append(text(gx - 10, gy - gh - 6, 'Підсилення g(λ) / Інтенсивність', 11, INK, 'end'))

    y_th = gy - 75
    f.append(line(gx, y_th, gx + gw, y_th, color=NEG, sw=1.5, dash='5,3'))
    f.append(text(gx + gw - 10, y_th - 8, 'Порогові втрати g_th', 10, NEG, 'end', bold=True))

    gain_pts = []
    for i in range(gw + 1):
        x = gx + i
        x_center = gx + gw * 0.48
        sigma = 90
        val = 110 * math.exp(-((x - x_center) ** 2) / (2 * sigma ** 2))
        gain_pts.append((x, gy - val))
    
    g_path = f"M {gain_pts[0][0]},{gain_pts[0][1]:.1f} " + " ".join(f"L {px},{py:.1f}" for px, py in gain_pts[1:])
    f.append(path_shape(g_path, fill='none', stroke=FIELD, sw=2.5))
    f.append(text(gx + gw * 0.48, gy - 118, 'Контур підсилення напівпровідника g(λ)', 11, FIELD, 'middle', bold=True))

    mode_spacing = 28
    for m_idx in range(1, 18):
        mx = gx + 40 + m_idx * mode_spacing
        if mx < gx + gw - 20:
            x_center = gx + gw * 0.48
            sigma = 90
            g_val = 110 * math.exp(-((mx - x_center) ** 2) / (2 * sigma ** 2))
            if g_val > 75:
                m_h = (g_val - 75) * 2.2 + 10
                f.append(line(mx, gy, mx, gy - m_h, color=POS, sw=2.5))
            else:
                f.append(line(mx, gy, mx, gy - 8, color=MUTED, sw=1.2))

    m1 = gx + 40 + 7 * mode_spacing
    m2 = gx + 40 + 8 * mode_spacing
    f.append(line(m1, gy - 85, m2, gy - 85, color=INK, sw=1.2))
    f.append(line(m1, gy - 80, m1, gy - 90, color=INK, sw=1.2))
    f.append(line(m2, gy - 80, m2, gy - 90, color=INK, sw=1.2))
    f.append(text((m1 + m2) / 2, gy - 94, 'Δλ', 11, INK, 'middle', bold=True, italic=True))

    render(os.path.join(IMG, 'cavity-modes.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Ват-амперна характеристика (L-I) та звуження спектра
# ═══════════════════════════════════════════════════════════════════════════
def fig_light_current_characteristic():
    W, H = 700, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Ват-амперна характеристика (L-I) та генераційні режими', 16, INK, 'middle', bold=True))

    ox, oy = 80, 320
    gw, gh = 320, 240
    
    f.append(line(ox, oy, ox + gw, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=MUTED, sw=1.5))
    f.append(text(ox + gw + 10, oy + 4, 'Струм інжекції I (мА)', 11, INK, 'start'))
    f.append(text(ox - 10, oy - gh - 6, 'Оптична потужність P (мВт)', 11, INK, 'end'))

    i_th_x = ox + 110
    f.append(line(i_th_x, oy, i_th_x, oy - gh, color=MUTED, sw=1.2, dash='4,3'))
    f.append(text(i_th_x, oy + 18, 'I_th', 11, MUTED, 'middle', bold=True, italic=True))

    f.append(line(ox, oy, i_th_x, oy - 12, color=MUTED, sw=2.5))
    p_max_x = ox + 290
    p_max_y = oy - 220
    f.append(line(i_th_x, oy - 12, p_max_x, p_max_y, color=POS, sw=3))
    
    f.append(circle(i_th_x, oy - 12, 5, fill=BG, stroke=NEG, sw=2))

    f.append(text(ox + 45, oy - 35, 'Спонтанне\nвипромінювання\n(режим LED)', 10, MUTED, 'middle'))
    f.append(text(ox + 210, oy - 150, 'Вимушене випромінювання\n(лазерна генерація)', 11, POS, 'middle', bold=True))
    
    f.append(text(ox + 265, oy - 90, 'Нахил η_ext = dP/dI', 10, FIELD, 'start', bold=True))

    box_x = 440
    
    sy1 = 65
    f.append(rect(box_x, sy1, 230, 110, fill='#f8fafc', stroke=MUTED, sw=1.2, rx=4))
    f.append(text(box_x + 115, sy1 + 18, 'Спектр при I < I_th (широкий, Δλ ~ 30 нм)', 10, MUTED, 'middle', bold=True))
    s_pts1 = []
    for px in range(190):
        val = 45 * math.exp(-((px - 95) ** 2) / (2 * 35 ** 2))
        s_pts1.append((box_x + 20 + px, sy1 + 95 - val))
    sp_path1 = f"M {s_pts1[0][0]},{s_pts1[0][1]:.1f} " + " ".join(f"L {x},{y:.1f}" for x, y in s_pts1[1:])
    f.append(path_shape(sp_path1, fill='none', stroke=MUTED, sw=2))

    sy2 = 205
    f.append(rect(box_x, sy2, 230, 110, fill='#f0fdf4', stroke=MUTED, sw=1.2, rx=4))
    f.append(text(box_x + 115, sy2 + 18, 'Спектр при I > I_th (вузький, Δλ < 0.1 нм)', 10, POS, 'middle', bold=True))
    s_pts2 = []
    for px in range(190):
        val = 70 * math.exp(-((px - 95) ** 2) / (2 * 3 ** 2))
        s_pts2.append((box_x + 20 + px, sy2 + 95 - val))
    sp_path2 = f"M {s_pts2[0][0]},{s_pts2[0][1]:.1f} " + " ".join(f"L {x},{y:.1f}" for x, y in s_pts2[1:])
    f.append(path_shape(sp_path2, fill='none', stroke=POS, sw=2.2))

    render(os.path.join(IMG, 'light-current-characteristic.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Просторова асиметрія та дифракційна розбіжність променя
# ═══════════════════════════════════════════════════════════════════════════
def fig_beam_divergence_diffraction():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Просторова асиметрія та дифракційна розбіжність променя', 16, INK, 'middle', bold=True))

    bx, by = 60, 140
    bw, bh = 140, 100
    
    f.append(rect(bx, by, bw, bh, fill='#cbd5e1', stroke=MUTED, sw=2, rx=2))
    ap_w, ap_h = 4, 30
    ap_x = bx + bw
    ap_y = by + (bh - ap_h) / 2
    f.append(rect(ap_x - 2, ap_y, 4, ap_h, fill='#ef4444', stroke='none'))
    
    f.append(text(bx + bw / 2, by + 30, 'Кристал\nнапівпровідника', 11, INK, 'middle', bold=True))
    f.append(text(bx + bw / 2, by + bh - 15, 'p-n перехід', 10, MUTED, 'middle'))

    f.append(text(ap_x + 10, ap_y - 12, 'Товщина d ~ 0.1–0.2 мкм', 10, NEG, 'start', bold=True))
    f.append(text(ap_x + 10, ap_y + ap_h + 18, 'Ширина w ~ 3–5 мкм', 10, FIELD, 'start', bold=True))

    apex_x = ap_x
    apex_y = by + bh / 2
    
    top_y = apex_y - 100
    bot_y = apex_y + 100
    end_x = apex_x + 360
    
    poly_pts = f"{apex_x:.1f},{apex_y:.1f} {end_x:.1f},{top_y:.1f} {end_x:.1f},{bot_y:.1f}"
    f.append(polygon_shape(poly_pts, fill='#fef08a', stroke='none'))
    
    f.append(line(apex_x, apex_y, end_x, top_y, color=POS, sw=2))
    f.append(line(apex_x, apex_y, end_x, bot_y, color=POS, sw=2))
    
    f.append(ellipse_shape(end_x, apex_y, 25, 100, fill='#fde047', stroke=POS, sw=2))
    
    # Розміщуємо текстові блоки збоку, де немає перетинів із лініями конуса
    f.append(text(end_x + 35, apex_y - 45, 'Швидка вісь (Fast Axis):\nдифракція на вузькій d\nθ_⟂ ≈ 30° – 40°', 11, NEG, 'start', bold=True))
    f.append(text(end_x + 35, apex_y + 45, 'Повільна вісь (Slow Axis):\nдифракція на ширшій w\nθ_∥ ≈ 8° – 12°', 11, FIELD, 'start', bold=True))

    f.append(fitbox(60, 320, 640, 75,
                    'Дифракційне правило: чим вужча випромінююча апертура, тим більша кутова розбіжність випромінювання.\nЧерез d ≪ w пучок лазерного діода завжди має виражений еліптичний переріз та астигматизм.',
                    size=10, color=INK, fill='#f8fafc', stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'beam-divergence-diffraction.svg'), W, H, *f)


if __name__ == '__main__':
    fig_heterostructure_band()
    fig_cavity_modes()
    fig_light_current_characteristic()
    fig_beam_divergence_diffraction()
    print("All figures successfully generated.")
