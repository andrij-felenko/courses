# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Хроматична діаграма CIE 1931 (проекція X,Y,Z -> x,y)
# ═══════════════════════════════════════════════════════════════════════════
def fig_cie1931():
    W, H = 720, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Проекція 3D-простору XYZ на хроматичну площину (x, y)',
                  16, INK, 'middle', bold=True))

    # Схема зліва: 3D координати (X, Y, Z) і площина X + Y + Z = 1
    ox, oy = 140, 260
    # Осі 3D
    f.append(arrow(ox, oy, ox + 110, oy, color=MUTED, sw=1.5))
    f.append(text(ox + 120, oy + 4, 'X', 12, MUTED, 'start', bold=True))
    f.append(arrow(ox, oy, ox, oy - 120, color=MUTED, sw=1.5))
    f.append(text(ox, oy - 130, 'Y (яскравість)', 12, MUTED, 'middle', bold=True))
    f.append(arrow(ox, oy, ox - 70, oy + 70, color=MUTED, sw=1.5))
    f.append(text(ox - 82, oy + 82, 'Z', 12, MUTED, 'end', bold=True))

    # Похила площина X + Y + Z = 1
    p1 = (ox + 80, oy)
    p2 = (ox, oy - 90)
    p3 = (ox - 50, oy + 50)
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="#eaf2fb" stroke="%s" stroke-width="1.5" opacity="0.7"/>' %
             (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], NEG))
    f.append(text(ox + 45, oy - 55, 'X + Y + Z = 1', 11, NEG, 'start', italic=True))

    # Вектор кольору C = (X, Y, Z)
    cx, cy = ox + 65, oy - 75
    f.append(arrow(ox, oy, cx, cy, color=POS, sw=2.2))
    f.append(circle(cx, cy, 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(cx + 8, cy - 4, 'C(X,Y,Z)', 11, POS, 'start', bold=True))

    # Точка перетину з площиною x = X / (X+Y+Z)
    px, py = ox + 38, oy - 44
    f.append(circle(px, py, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px - 10, py - 8, 'c(x,y)', 11, FIELD, 'end', bold=True))

    # Стрілка переносу до 2D діаграми
    f.append(arrow(260, 210, 310, 210, color=LINE, sw=1.8))
    f.append(text(285, 195, 'нормування', 10, MUTED, 'middle'))
    f.append(text(285, 225, 'x+y+z = 1', 10, MUTED, 'middle'))

    # Справа: 2D графік (x, y)
    gx0, gy0 = 360, 420
    gw, gh = 320, 360

    # Сітка та осі 2D
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.8))
    f.append(text(gx0 + gw + 10, gy0 + 4, 'x', 14, INK, 'start', bold=True))
    f.append(text(gx0 - 10, gy0 - gh, 'y', 14, INK, 'end', bold=True))

    # Позначки шкали
    for i in range(1, 9):
        v = i * 0.1
        xx = gx0 + (v / 0.8) * (gw - 20)
        yy = gy0 - (v / 0.9) * (gh - 20)
        f.append(line(xx, gy0, xx, gy0 + 4, color=MUTED, sw=1))
        f.append(text(xx, gy0 + 16, '%.1f' % v, 10, MUTED, 'middle'))
        f.append(line(gx0 - 4, yy, gx0, yy, color=MUTED, sw=1))
        f.append(text(gx0 - 8, yy + 3, '%.1f' % v, 10, MUTED, 'end'))

    # Спектральний локус (приблизний контур спектральних кольорів від 380 до 700 нм в xy)
    raw_locus = [
        (0.174, 0.005), (0.144, 0.030), (0.091, 0.133), (0.008, 0.538),
        (0.074, 0.834), (0.229, 0.754), (0.357, 0.636), (0.444, 0.555),
        (0.528, 0.470), (0.627, 0.372), (0.735, 0.265)
    ]
    def map_xy(x_val, y_val):
        return (gx0 + (x_val / 0.8) * (gw - 20), gy0 - (y_val / 0.9) * (gh - 20))

    pts = [map_xy(xv, yv) for xv, yv in raw_locus]
    # Пурпурна лінія (від 700 нм до 380 нм)
    path_d = ["M %.1f %.1f" % pts[0]]
    for px_i, py_i in pts[1:]:
        path_d.append("L %.1f %.1f" % (px_i, py_i))
    path_d.append("Z")

    f.append('<path d="%s" fill="#f0f7ed" stroke="%s" stroke-width="2"/>' % (" ".join(path_d), FIELD))

    p_start = pts[-1]
    p_end = pts[0]
    f.append(line(p_start[0], p_start[1], p_end[0], p_end[1], color=POS, sw=1.8, dash='4,3'))
    f.append(text((p_start[0] + p_end[0]) / 2 + 25, (p_start[1] + p_end[1]) / 2 + 15,
                  'пурпурна лінія', 10, POS, 'middle', italic=True))

    wl_marks = [
        (0, '380 нм', 'start'), (3, '500 нм', 'end'), (4, '520 нм', 'middle'),
        (7, '570 нм', 'start'), (10, '700 нм', 'start')
    ]
    for idx, label, align in wl_marks:
        lx, ly = pts[idx]
        f.append(circle(lx, ly, 3, fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(lx + (10 if align == 'start' else (-10 if align == 'end' else 0)),
                      ly + (-8 if idx == 4 else 4), label, 10, INK, align))

    # Точка білого D65 (0.3127, 0.3290)
    wx, wy = map_xy(0.3127, 0.3290)
    f.append(circle(wx, wy, 4, fill=BG, stroke=INK, sw=1.8))
    f.append(text(wx + 8, wy - 6, 'D65 (біле)', 11, INK, 'start', bold=True))

    f.append(text(W / 2, H - 12,
                  'Хроматичність (x, y) описує колірний тон і насиченість незалежно від яскравості Y',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'cie1931-chromaticity.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Порівняння колірних охоплень (sRGB, Adobe RGB, Rec. 2020)
# ═══════════════════════════════════════════════════════════════════════════
def fig_gamuts():
    W, H = 720, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Колірні охоплення стандартних систем у просторі CIE 1931 xy',
                  16, INK, 'middle', bold=True))

    gx0, gy0 = 80, 440
    gw, gh = 380, 390

    def map_xy(x_val, y_val):
        return (gx0 + (x_val / 0.8) * (gw - 20), gy0 - (y_val / 0.9) * (gh - 20))

    f.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.8))
    f.append(text(gx0 + gw + 10, gy0 + 4, 'x', 14, INK, 'start', bold=True))
    f.append(text(gx0 - 10, gy0 - gh, 'y', 14, INK, 'end', bold=True))

    for i in range(1, 9):
        v = i * 0.1
        xx = gx0 + (v / 0.8) * (gw - 20)
        yy = gy0 - (v / 0.9) * (gh - 20)
        f.append(line(xx, gy0, xx, gy0 + 4, color=MUTED, sw=1))
        f.append(text(xx, gy0 + 16, '%.1f' % v, 10, MUTED, 'middle'))
        f.append(line(gx0 - 4, yy, gx0, yy, color=MUTED, sw=1))
        f.append(text(gx0 - 8, yy + 3, '%.1f' % v, 10, MUTED, 'end'))

    raw_locus = [
        (0.174, 0.005), (0.144, 0.030), (0.091, 0.133), (0.008, 0.538),
        (0.074, 0.834), (0.229, 0.754), (0.357, 0.636), (0.444, 0.555),
        (0.528, 0.470), (0.627, 0.372), (0.735, 0.265)
    ]
    pts = [map_xy(xv, yv) for xv, yv in raw_locus]
    path_d = ["M %.1f %.1f" % pts[0]] + ["L %.1f %.1f" % p for p in pts[1:]] + ["Z"]
    f.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="1.8"/>' % (" ".join(path_d), MUTED))

    # 1. sRGB трикутник
    srgb_prim = [(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)]
    spts = [map_xy(x, y) for x, y in srgb_prim]
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2457d6" fill-opacity="0.15" stroke="#2457d6" stroke-width="2"/>' %
             (spts[0][0], spts[0][1], spts[1][0], spts[1][1], spts[2][0], spts[2][1]))

    # 2. Adobe RGB трикутник
    adobe_prim = [(0.64, 0.33), (0.21, 0.71), (0.15, 0.06)]
    apts = [map_xy(x, y) for x, y in adobe_prim]
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#27ae60" fill-opacity="0.12" stroke="#27ae60" stroke-width="2" stroke-dasharray="6,4"/>' %
             (apts[0][0], apts[0][1], apts[1][0], apts[1][1], apts[2][0], apts[2][1]))

    # 3. Rec. 2020 трикутник
    rec_prim = [(0.708, 0.292), (0.170, 0.797), (0.131, 0.046)]
    rpts = [map_xy(x, y) for x, y in rec_prim]
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#c0392b" fill-opacity="0.08" stroke="#c0392b" stroke-width="2" stroke-dasharray="3,3"/>' %
             (rpts[0][0], rpts[0][1], rpts[1][0], rpts[1][1], rpts[2][0], rpts[2][1]))

    unreach_x, unreach_y = map_xy(0.08, 0.65)
    f.append(circle(unreach_x, unreach_y, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(unreach_x + 8, unreach_y, 'недосяжні хроматичності', 10, POS, 'start', bold=True))

    lx0, ly0 = 480, 100
    f.append(rect(lx0, ly0, 220, 270, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    f.append(text(lx0 + 110, ly0 + 24, 'Порівняння охоплень:', 13, INK, 'middle', bold=True))

    f.append(line(lx0 + 16, ly0 + 55, lx0 + 46, ly0 + 55, color='#2457d6', sw=2.5))
    f.append(text(lx0 + 54, ly0 + 59, 'sRGB (~35% CIE)', 12, INK, 'start', bold=True))
    f.append(text(lx0 + 54, ly0 + 74, 'стандарт моніторів та Web', 10, MUTED, 'start'))

    f.append(line(lx0 + 16, ly0 + 105, lx0 + 46, ly0 + 105, color='#27ae60', sw=2.5, dash='6,4'))
    f.append(text(lx0 + 54, ly0 + 109, 'Adobe RGB (~52% CIE)', 12, INK, 'start', bold=True))
    f.append(text(lx0 + 54, ly0 + 124, 'розширені зелені (поліграфія)', 10, MUTED, 'start'))

    f.append(line(lx0 + 16, ly0 + 155, lx0 + 46, ly0 + 155, color='#c0392b', sw=2.5, dash='3,3'))
    f.append(text(lx0 + 54, ly0 + 159, 'Rec. 2020 (~75% CIE)', 12, INK, 'start', bold=True))
    f.append(text(lx0 + 54, ly0 + 174, 'UHDTV / лазерні первинні', 10, MUTED, 'start'))

    f.append(line(lx0 + 16, ly0 + 195, lx0 + 204, ly0 + 195, color=MUTED, sw=1, dash='2,2'))
    f.append(mtext(lx0 + 110, ly0 + 215,
                   'Чому 3 первинні кольори\nне покривають 100%:\nспектральний локус є опуклим,\nа трикутник завжди лишає\nсегменти ззовні.',
                   size=11, color=INK, anchor='middle'))

    f.append(text(W / 2, H - 12,
                  'Жоден трикутник реальних фізичних джерел не може охопити весь локус підкови',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'gamut-triangles.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Правило змішування Ґрассмана та колірне картування (Gamut Mapping)
# ═══════════════════════════════════════════════════════════════════════════
def fig_mixing_mapping():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Правило відрізка Ґрассмана та компресія охоплення (Gamut Mapping)',
                  16, INK, 'middle', bold=True))

    pA = (70, 240)
    pB = (220, 100)
    pC = (250, 260)

    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#eaf2fb" stroke="%s" stroke-width="1.8"/>' %
             (pA[0], pA[1], pB[0], pB[1], pC[0], pC[1], NEG))
    f.append(circle(pA[0], pA[1], 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(pA[0] - 10, pA[1] + 14, 'R (первинний 1)', 11, NEG, 'end', bold=True))
    f.append(circle(pB[0], pB[1], 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(pB[0], pB[1] - 10, 'G (первинний 2)', 11, FIELD, 'middle', bold=True))
    f.append(circle(pC[0], pC[1], 4, fill=POS, stroke=POS, sw=1))
    f.append(text(pC[0] + 10, pC[1] + 14, 'B (первинний 3)', 11, POS, 'start', bold=True))

    mx = pA[0] * 0.4 + pB[0] * 0.6
    my = pA[1] * 0.4 + pB[1] * 0.6
    f.append(circle(mx, my, 4, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(line(pA[0], pA[1], pB[0], pB[1], color=FIELD, sw=2))
    f.append(text(mx - 14, my - 8, 'M (суміш R+G)', 11, INK, 'end', bold=True))

    bx = (pA[0] + pB[0] + pC[0]) / 3
    by = (pA[1] + pB[1] + pC[1]) / 3
    f.append(circle(bx, by, 4, fill=BG, stroke=INK, sw=2))
    f.append(text(bx, by + 16, 'W (білий)', 10, INK, 'middle', bold=True))

    f.append(line(310, 60, 310, 310, color=MUTED, sw=1, dash='4,4'))

    gpA = (400, 240)
    gpB = (530, 100)
    gpC = (560, 260)
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#f4f6f8" stroke="%s" stroke-width="1.8"/>' %
             (gpA[0], gpA[1], gpB[0], gpB[1], gpC[0], gpC[1], LINE))
    f.append(text(540, 230, 'Охоплення дисплея', 11, MUTED, 'middle', italic=True))

    px, py = 580, 120
    f.append(circle(px, py, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(px + 8, py - 4, 'P (поза охопленням)', 11, POS, 'start', bold=True))

    clip_x, clip_y = 521, 110
    f.append(arrow(px, py, clip_x, clip_y, color=POS, sw=1.8))
    f.append(circle(clip_x, clip_y, 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(clip_x - 10, clip_y - 8, 'Кліпінг', 10, POS, 'end', bold=True))

    g_white_x = (gpA[0] + gpB[0] + gpC[0]) / 3
    g_white_y = (gpA[1] + gpB[1] + gpC[1]) / 3
    f.append(circle(g_white_x, g_white_y, 3.5, fill=BG, stroke=INK, sw=1.5))

    f.append(line(px, py, g_white_x, g_white_y, color=NEG, sw=1.5, dash='4,3'))
    perc_x = g_white_x + (px - g_white_x) * 0.72
    perc_y = g_white_y + (py - g_white_y) * 0.72
    f.append(arrow(px, py, perc_x, perc_y, color=NEG, sw=1.8))
    f.append(circle(perc_x, perc_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(perc_x - 6, perc_y + 14, 'Перцептивний зсув', 10, NEG, 'end', bold=True))

    f.append(text(180, H - 24, 'Аддитивне змішування: суміш лежить на відрізку між вихідними кольорами', 11, MUTED, 'middle'))
    f.append(text(500, H - 24, 'Gamut mapping: проекція (clipping) або масштабування (perceptual)', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'additive-mixing.svg'), W, H, *f)


fig_cie1931()
fig_gamuts()
fig_mixing_mapping()
print('Figures created successfully.')
