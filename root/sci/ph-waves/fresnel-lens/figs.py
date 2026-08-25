# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"
GLASS_BORDER = "#3b82f6"
SHADOW = "#fee2e2"


def ang(a):
    return math.radians(a)


def path_d(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    dash_str = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash_str}/>'



# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Перехід від суцільної лінзи до зон Френеля
# ═══════════════════════════════════════════════════════════════════════════
def fig_concept():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Перехід від суцільної товстої лінзи до зон Френеля', 16, INK, 'middle', bold=True))

    # --- Ліва панель: Суцільна лінза ---
    cx1 = 190
    f.append(text(cx1, 55, 'а) Суцільна опукла лінза', 13, INK, 'middle', bold=True))
    f.append(text(cx1, 72, 'Велика товщина та маса матеріалу', 11, MUTED, 'middle'))

    # Оптична вісь
    f.append(line(cx1 - 150, 200, cx1 + 170, 200, color=MUTED, sw=1.2, dash='6,4'))
    # Фокус F
    fx1 = cx1 + 140
    f.append(circle(fx1, 200, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(fx1, 220, 'F', 12, NEG, 'middle', bold=True))

    # Профіль товстої лінзи: плоско-опукла
    lens_path = f"M {cx1-40} 80 L {cx1-40} 320 Q {cx1+35} 200 {cx1-40} 80 Z"
    f.append(path_d(lens_path, fill=GLASS, stroke=GLASS_BORDER, sw=2))

    # Штриховка / позначення зайвого матеріалу в товщі
    inner_path = f"M {cx1-40} 120 L {cx1-40} 280 Q {cx1+10} 200 {cx1-40} 120 Z"
    f.append(path_d(inner_path, fill="#dbeafe", stroke="none", sw=0))

    f.append(text(cx1 - 32, 145, 'Паразитний', 10, MUTED, 'start'))
    f.append(text(cx1 - 32, 158, 'об\'єм скломаси', 10, MUTED, 'start'))



    # Промені світла для суцільної лінзи
    for y_in in [100, 140, 260, 300]:
        f.append(arrow(cx1 - 140, y_in, cx1 - 40, y_in, color=POS, sw=1.8))
        dy = abs(y_in - 200) / 120.0
        x_surf = cx1 + 35 - 75 * (dy ** 2)
        f.append(line(cx1 - 40, y_in, x_surf, y_in, color=POS, sw=1.8))
        f.append(line(x_surf, y_in, fx1, 200, color=FIELD, sw=1.8))

    # --- Права панель: Лінза Френеля ---
    cx2 = 570
    f.append(text(cx2, 55, 'б) Лінза Френеля (кільцеві зони)', 13, INK, 'middle', bold=True))
    f.append(text(cx2, 72, 'Видалено внутрішнє скло, збережено нахили', 11, MUTED, 'middle'))

    # Оптична вісь
    f.append(line(cx2 - 150, 200, cx2 + 170, 200, color=MUTED, sw=1.2, dash='6,4'))
    # Фокус F
    fx2 = cx2 + 140
    f.append(circle(fx2, 200, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(fx2, 220, 'F', 12, NEG, 'middle', bold=True))

    # Профіль лінзи Френеля на пласкій підкладці при x = cx2 - 40
    fresnel_path = (
        f"M {cx2-48} 80 L {cx2-40} 80 "
        f"L {cx2-28} 80 L {cx2-40} 115 "
        f"L {cx2-24} 115 L {cx2-40} 150 "
        f"L {cx2-20} 150 L {cx2-40} 185 "
        f"L {cx2-16} 185 L {cx2-40} 200 "
        f"L {cx2-16} 215 L {cx2-40} 215 "
        f"L {cx2-20} 250 L {cx2-40} 250 "
        f"L {cx2-24} 285 L {cx2-40} 285 "
        f"L {cx2-28} 320 L {cx2-48} 320 Z"
    )
    f.append(path_d(fresnel_path, fill=GLASS, stroke=GLASS_BORDER, sw=1.8))


    # Промені для лінзи Френеля
    ray_ys = [100, 140, 260, 300]
    surf_xs = [cx2 - 34, cx2 - 29, cx2 - 29, cx2 - 34]
    for y_in, x_s in zip(ray_ys, surf_xs):
        f.append(arrow(cx2 - 140, y_in, cx2 - 48, y_in, color=POS, sw=1.8))
        f.append(line(cx2 - 48, y_in, x_s, y_in, color=POS, sw=1.8))
        f.append(line(x_s, y_in, fx2, 200, color=FIELD, sw=1.8))

    # Виносний підпис товщини
    f.append(line(cx2 - 48, 335, cx2 - 28, 335, color=INK, sw=1.5))
    f.append(line(cx2 - 48, 330, cx2 - 48, 340, color=INK, sw=1.5))
    f.append(line(cx2 - 28, 330, cx2 - 28, 340, color=INK, sw=1.5))
    f.append(text(cx2 - 38, 352, 'h ≪ D', 11, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'fresnel-concept.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Геометрія одного кільцевого фацету та паразитна стінка
# ═══════════════════════════════════════════════════════════════════════════
def fig_groove_geometry():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Геометрія кільцевого фацету та паразитна зона сходинки', 16, INK, 'middle', bold=True))

    x_base = 140
    y_top = 80
    y_bot = 300
    x_tip = 340
    y_step = 240

    facet_path = f"M {x_base-40} {y_top} L {x_base} {y_top} L {x_tip} {y_step} L {x_base} {y_step} L {x_base-40} {y_bot} Z"
    f.append(path_d(facet_path, fill=GLASS, stroke=GLASS_BORDER, sw=2))

    f.append(line(40, 330, 680, 330, color=MUTED, sw=1.2, dash='6,4'))
    f.append(text(60, 348, 'Оптична вісь', 11, MUTED, 'start'))

    f.append(line(x_base, y_top, x_tip, y_step, color=FIELD, sw=2.5))
    f.append(text(250, 140, 'Робочий оптичний схил α(r)', 12, FIELD, 'start', bold=True))

    f.append(line(x_base, y_top, x_tip + 40, y_top, color=MUTED, sw=1, dash='4,3'))
    f.append(text(x_base + 60, y_top + 22, 'α', 13, POS, 'start', bold=True))

    f.append(line(x_tip, y_step, x_base, y_step, color=NEG, sw=2.5))
    shadow_path = f"M {x_tip} {y_step} L {x_base} {y_step} L {x_base} {y_step-28} Z"
    f.append(path_d(shadow_path, fill=SHADOW, stroke=NEG, sw=1, dash='3,2'))

    f.append(text(x_base + 15, y_step - 8, 'Зона затінення (втрата світла)', 11, NEG, 'start', bold=True))

    f.append(line(x_base - 55, y_top, x_base - 55, y_step, color=INK, sw=1.5))
    f.append(line(x_base - 60, y_top, x_base - 50, y_top, color=INK, sw=1.5))
    f.append(line(x_base - 60, y_step, x_base - 50, y_step, color=INK, sw=1.5))
    f.append(text(x_base - 70, (y_top + y_step) / 2 + 4, 'p', 13, INK, 'end', bold=True))

    f.append(line(x_base, y_step + 30, x_tip, y_step + 30, color=INK, sw=1.5))
    f.append(line(x_base, y_step + 25, x_base, y_step + 35, color=INK, sw=1.5))
    f.append(line(x_tip, y_step + 25, x_tip, y_step + 35, color=INK, sw=1.5))
    f.append(text((x_base + x_tip) / 2, y_step + 48, 'h (глибина канавки)', 12, INK, 'middle', bold=True))

    f.append(arrow(40, 135, x_base - 40, 135, color=POS, sw=2))
    f.append(line(x_base - 40, 135, 210, 135, color=POS, sw=2))
    f.append(arrow(210, 135, 540, 310, color=FIELD, sw=2))
    f.append(text(550, 305, 'Заломлений промінь до фокуса', 11, FIELD, 'start'))

    f.append(arrow(40, y_step - 14, x_base - 40, y_step - 14, color=NEG, sw=1.8))
    f.append(line(x_base - 40, y_step - 14, x_base + 35, y_step - 14, color=NEG, sw=1.8, dash='5,3'))
    f.append(arrow(x_base + 35, y_step - 14, 300, y_step + 50, color=NEG, sw=1.8))

    f.append(text(310, y_step + 65, 'Розсіяне / паразитна світло', 11, NEG, 'start'))

    render(os.path.join(IMG, 'groove-geometry.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Катадіоптрична лінза Френеля (заломлення + TIR)
# ═══════════════════════════════════════════════════════════════════════════
def fig_tir_catadioptric():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Катадіоптрична лінза Френеля: заломлювальні й TIR-призми', 16, INK, 'middle', bold=True))

    sx = 80
    sy = 190
    f.append(circle(sx, sy, 6, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(sx, sy - 14, 'Джерело S', 12, NEG, 'middle', bold=True))
    f.append(line(sx, sy, 720, sy, color=MUTED, sw=1.2, dash='6,4'))

    cx = 290

    f.append(rect(cx, 130, 60, 120, fill=GLASS, stroke=GLASS_BORDER, sw=1.8))
    f.append(text(cx + 30, 148, 'Центральні', 10, FIELD, 'middle', bold=True))
    f.append(text(cx + 30, 161, 'заломлювальні', 10, FIELD, 'middle'))
    f.append(text(cx + 30, 174, 'елементи', 10, FIELD, 'middle'))



    for y_ray in [150, 230]:
        f.append(arrow(sx, sy, cx, y_ray, color=POS, sw=1.8))
        f.append(line(cx, y_ray, cx + 20, y_ray, color=POS, sw=1.8))
        f.append(arrow(cx + 20, y_ray, 700, y_ray, color=FIELD, sw=1.8))

    prism_top = f"M {cx} 50 L {cx+50} 50 L {cx+20} 110 L {cx} 110 Z"
    f.append(path_d(prism_top, fill=GLASS, stroke=GLASS_BORDER, sw=1.8))

    f.append(arrow(sx, sy, cx + 12, 90, color=POS, sw=2))
    f.append(line(cx + 12, 90, cx + 36, 64, color=POS, sw=2))
    f.append(circle(cx + 36, 64, 3, fill=NEG, stroke='none'))
    f.append(arrow(cx + 36, 64, 700, 64, color=FIELD, sw=2))
    f.append(text(cx + 110, 52, 'Повне внутрішнє відбиття (TIR)', 12, NEG, 'start', bold=True))

    prism_bot = f"M {cx} 270 L {cx+20} 270 L {cx+50} 330 L {cx} 330 Z"
    f.append(path_d(prism_bot, fill=GLASS, stroke=GLASS_BORDER, sw=1.8))


    f.append(arrow(sx, sy, cx + 12, 290, color=POS, sw=2))
    f.append(line(cx + 12, 290, cx + 36, 316, color=POS, sw=2))
    f.append(circle(cx + 36, 316, 3, fill=NEG, stroke='none'))
    f.append(arrow(cx + 36, 316, 700, 316, color=FIELD, sw=2))
    f.append(text(cx + 110, 332, 'Катадіоптричні кільця маяка', 12, INK, 'start', bold=True))

    f.append(line(cx - 30, 120, cx + 70, 120, color=MUTED, sw=1, dash='4,3'))
    f.append(line(cx - 30, 260, cx + 70, 260, color=MUTED, sw=1, dash='4,3'))

    render(os.path.join(IMG, 'tir-catadioptric.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Багатозональний масив лінзи Френеля для PIR-давача
# ═══════════════════════════════════════════════════════════════════════════
def fig_pir_multizone():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Багатофасетна лінза Френеля в PIR-давачі руху', 16, INK, 'middle', bold=True))

    det_x = 90
    det_y = 180
    f.append(rect(det_x - 15, det_y - 25, 30, 50, fill="#fef08a", stroke="#ca8a04", sw=2, rx=4))
    f.append(text(det_x, det_y - 4, 'PIR', 11, INK, 'middle', bold=True))
    f.append(text(det_x, det_y + 10, 'давач', 10, MUTED, 'middle'))

    cap_x = 280
    f.append(path_d(f"M {cap_x} 60 Q {cap_x+40} 180 {cap_x} 300", fill='none', stroke=GLASS_BORDER, sw=4))

    facets_y = [80, 130, 180, 230, 280]
    labels = ['Сектор 1 (+40°)', 'Сектор 2 (+20°)', 'Центр (0°)', 'Сектор 4 (-20°)', 'Сектор 5 (-40°)']

    for i, (fy, lbl) in enumerate(zip(facets_y, labels)):
        f.append(circle(cap_x + 18, fy, 8, fill=GLASS, stroke=GLASS_BORDER, sw=1.5))

        ray_color = POS if i % 2 == 0 else FIELD
        f.append(arrow(680, fy + (fy - 180) * 0.4, cap_x + 24, fy, color=ray_color, sw=1.8))
        f.append(line(cap_x + 12, fy, det_x + 15, det_y, color=ray_color, sw=1.8, dash='5,3'))

        f.append(text(690, fy + (fy - 180) * 0.4 + 4, lbl, 11, INK, 'start'))

    f.append(rect(360, 305, 340, 45, fill="#f3f4f6", stroke="#d1d5db", sw=1, rx=4))
    f.append(text(530, 323, 'Переміщення теплового об\'єкта між секторами', 11, INK, 'middle', bold=True))
    f.append(text(530, 340, 'поперемінно модулює ІЧ-потік на одному піроелементі', 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'pir-multizone.svg'), W, H, *f)


if __name__ == '__main__':
    fig_concept()
    fig_groove_geometry()
    fig_tir_catadioptric()
    fig_pir_multizone()
    print("All figures generated successfully.")
