# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"
GLASS_BORDER = "#2563eb"
RED_RAY = "#dc2626"
BLUE_RAY = "#2563eb"
GREEN_RAY = "#16a34a"
GOLD_RAY = "#d97706"
MUTED_LINE = "#94a3b8"

def path_d(d, fill="none", stroke=INK, sw=1.5, dash=None):
    dash_str = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash_str}/>'

def ellipse_svg(cx, cy, rx, ry, fill="none", stroke=INK, sw=1.5):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Сферична аберація та каустика
# ═══════════════════════════════════════════════════════════════════════════
def fig_spherical():
    W, H = 820, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Сферична аберація: фокальний зсув крайніх і параксіальних променів', 16, INK, 'middle', bold=True))

    cx = 200
    cy = 200
    lens_h = 270
    lens_w = 55

    # Оптична вісь
    f.append(line(30, cy, W - 30, cy, color=MUTED_LINE, sw=1.2, dash='6,4'))
    f.append(text(W - 25, cy - 8, 'Оптична вісь', 11, MUTED, 'end'))

    # Профіль сферичної двоопуклої лінзи
    lens_path = f"M {cx} {cy - lens_h/2} Q {cx + lens_w} {cy} {cx} {cy + lens_h/2} Q {cx - lens_w} {cy} {cx} {cy - lens_h/2} Z"
    f.append(path_d(lens_path, fill=GLASS, stroke=GLASS_BORDER, sw=2))

    # Вертикальна головна площина
    f.append(line(cx, cy - lens_h/2 - 10, cx, cy + lens_h/2 + 10, color=GLASS_BORDER, sw=1, dash='3,3'))

    # Фокуси
    fm_x = 520  # Крайній (маргінальний) фокус
    flc_x = 600 # Круг найменшого розмиття (Circle of Least Confusion)
    fp_x = 700  # Параксіальний фокус

    # Точки фокусів
    f.append(circle(fm_x, cy, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(fm_x - 8, cy + 18, 'F_m (крайній)', 11, NEG, 'end', bold=True))

    f.append(circle(fp_x, cy, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(fp_x + 10, cy + 18, 'F_p (параксіальний)', 11, POS, 'start', bold=True))

    # Площина найменшого розмиття
    f.append(line(flc_x, cy - 65, flc_x, cy + 65, color=GOLD_RAY, sw=1.5, dash='4,3'))
    f.append(text(flc_x, cy - 75, 'Круг найменшої плями', 11, GOLD_RAY, 'middle', bold=True))

    # Каустична крива (обвідна променів)
    caustic_top = f"M {cx} {cy - lens_h/2} Q {fm_x - 30} {cy - 12} {fp_x} {cy}"
    caustic_bot = f"M {cx} {cy + lens_h/2} Q {fm_x - 30} {cy + 12} {fp_x} {cy}"
    f.append(path_d(caustic_top, fill="none", stroke="#f59e0b", sw=1.5, dash="2,2"))
    f.append(path_d(caustic_bot, fill="none", stroke="#f59e0b", sw=1.5, dash="2,2"))

    # Промені:
    # 1. Параксіальні
    paraxial_y = [cy - 30, cy + 30]
    for y_in in paraxial_y:
        f.append(arrow(30, y_in, cx, y_in, color=POS, sw=1.8))
        f.append(line(cx, y_in, fp_x, cy, color=POS, sw=1.8))

    # 2. Проміжні промені
    mid_y = [cy - 75, cy + 75]
    mid_f = 610
    for y_in in mid_y:
        f.append(arrow(30, y_in, cx, y_in, color=FIELD, sw=1.8))
        f.append(line(cx, y_in, mid_f, cy, color=FIELD, sw=1.8))

    # 3. Маргінальні (крайові) промені
    marginal_y = [cy - 120, cy + 120]
    for y_in in marginal_y:
        f.append(arrow(30, y_in, cx, y_in, color=NEG, sw=2.0))
        f.append(line(cx, y_in, fm_x, cy, color=NEG, sw=2.0))
        dx = 190
        dy_cont = (cy - y_in) * (dx / (fm_x - cx))
        f.append(line(fm_x, cy, fm_x + dx, cy - dy_cont, color=NEG, sw=1.5))

    # Позначення поздовжньої аберації δs'
    f.append(line(fm_x, cy + 55, fp_x, cy + 55, color=INK, sw=1.5))
    f.append(line(fm_x, cy + 48, fm_x, cy + 62, color=INK, sw=1.5))
    f.append(line(fp_x, cy + 48, fp_x, cy + 62, color=INK, sw=1.5))
    f.append(text((fm_x + fp_x)/2, cy + 74, 'Поздовжня сферична аберація δs\'', 12, INK, 'middle', bold=True))

    # Позначення поперечної аберації δr'
    f.append(line(fp_x, cy - 45, fp_x, cy + 45, color=POS, sw=1.2, dash='4,2'))
    f.append(text(fp_x + 12, cy + 42, 'δr\'', 12, NEG, 'start', bold=True))

    render(os.path.join(IMG, 'spherical-aberration-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Хроматична аберація та ахроматичний дублет
# ═══════════════════════════════════════════════════════════════════════════
def fig_chromatic():
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Хроматична аберація одиночної лінзи та її компенсація ахроматичним дублетом', 16, INK, 'middle', bold=True))

    # --- Ліва панель: Одиночна лінза ---
    cx1 = 150
    cy = 220
    f.append(text(cx1 + 40, 56, 'а) Поздовжня хроматична аберація', 13, INK, 'middle', bold=True))
    f.append(text(cx1 + 40, 74, 'Дисперсія скломаси: n(синій) > n(червоний)', 11, MUTED, 'middle'))

    f.append(line(20, cy, 380, cy, color=MUTED_LINE, sw=1.2, dash='6,4'))

    # Лінза
    lens1 = f"M {cx1} {cy-120} Q {cx1+30} {cy} {cx1} {cy+120} Q {cx1-30} {cy} {cx1} {cy-120} Z"
    f.append(path_d(lens1, fill=GLASS, stroke=GLASS_BORDER, sw=1.8))

    fb_x1 = 270
    fr_x1 = 345

    f.append(circle(fb_x1, cy, 4, fill=BLUE_RAY, stroke=INK, sw=1))
    f.append(text(fb_x1, cy - 12, 'F_B (436 нм)', 10, BLUE_RAY, 'middle', bold=True))

    f.append(circle(fr_x1, cy, 4, fill=RED_RAY, stroke=INK, sw=1))
    f.append(text(fr_x1, cy - 12, 'F_R (656 нм)', 10, RED_RAY, 'middle', bold=True))

    for y_in in [cy - 90, cy + 90]:
        f.append(arrow(25, y_in, cx1, y_in, color=INK, sw=2))
        f.append(line(cx1, y_in, fb_x1, cy, color=BLUE_RAY, sw=1.8))
        f.append(line(cx1, y_in, fr_x1, cy, color=RED_RAY, sw=1.8))

    f.append(line(fb_x1, cy + 45, fr_x1, cy + 45, color=INK, sw=1.2))
    f.append(line(fb_x1, cy + 38, fb_x1, cy + 52, color=INK, sw=1.2))
    f.append(line(fr_x1, cy + 38, fr_x1, cy + 52, color=INK, sw=1.2))
    f.append(text((fb_x1 + fr_x1)/2, cy + 62, 'Хроматичний зсув δs\'_C', 11, INK, 'middle', bold=True))

    # --- Права панель: Ахроматичний дублет ---
    cx2 = 540
    f.append(text(cx2 + 90, 56, 'б) Ахроматичний дублет (крон + флінт)', 13, INK, 'middle', bold=True))
    f.append(text(cx2 + 90, 74, 'Поєднання збиральної та розсіювальної лінз', 11, MUTED, 'middle'))

    f.append(line(410, cy, 800, cy, color=MUTED_LINE, sw=1.2, dash='6,4'))

    crown_path = f"M {cx2} {cy-120} Q {cx2+25} {cy} {cx2} {cy+120} Q {cx2-25} {cy} {cx2} {cy-120} Z"
    f.append(path_d(crown_path, fill="#dbeafe", stroke=GLASS_BORDER, sw=1.8))

    flint_path = f"M {cx2} {cy-120} L {cx2+35} {cy-120} Q {cx2+15} {cy} {cx2+35} {cy+120} L {cx2} {cy+120} Q {cx2+25} {cy} {cx2} {cy-120} Z"
    f.append(path_d(flint_path, fill="#fef3c7", stroke="#d97706", sw=1.8))

    f.append(text(cx2 - 10, cy - 130, 'Крон (V_1 високе)', 11, GLASS_BORDER, 'middle', bold=True))
    f.append(text(cx2 + 35, cy - 130, 'Флінт (V_2 мале)', 11, "#d97706", 'middle', bold=True))

    fbr_x = 730

    f.append(circle(fbr_x, cy, 5, fill=POS, stroke=INK, sw=1.2))
    f.append(text(fbr_x, cy - 14, 'Спільний фокус F_{BR}', 11, POS, 'middle', bold=True))

    for y_in in [cy - 90, cy + 90]:
        f.append(arrow(420, y_in, cx2, y_in, color=INK, sw=2))
        f.append(line(cx2, y_in, cx2 + 25, y_in + (10 if y_in > cy else -10), color=BLUE_RAY, sw=1.5))
        f.append(line(cx2, y_in, cx2 + 25, y_in + (5 if y_in > cy else -5), color=RED_RAY, sw=1.5))
        f.append(line(cx2 + 25, y_in + (10 if y_in > cy else -10), fbr_x, cy, color=BLUE_RAY, sw=1.8))
        f.append(line(cx2 + 25, y_in + (5 if y_in > cy else -5), fbr_x, cy, color=RED_RAY, sw=1.8))

    render(os.path.join(IMG, 'chromatic-aberration-doublet.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Кома та утворення кометичного конуса
# ═══════════════════════════════════════════════════════════════════════════
def fig_coma():
    W, H = 820, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Аберація коматичного пучка: асиметрія похилих променів поза віссю', 16, INK, 'middle', bold=True))

    cx = 200
    cy = 220
    lens_h = 260
    lens_w = 50

    # Оптична вісь
    f.append(line(30, cy, W - 30, cy, color=MUTED_LINE, sw=1.2, dash='6,4'))

    # Лінза
    lens_path = f"M {cx} {cy - lens_h/2} Q {cx + lens_w} {cy} {cx} {cy + lens_h/2} Q {cx - lens_w} {cy} {cx} {cy - lens_h/2} Z"
    f.append(path_d(lens_path, fill=GLASS, stroke=GLASS_BORDER, sw=2))

    # Головна лінія фокальної площини поза віссю
    img_x = 640
    f.append(line(img_x, 40, img_x, H - 30, color=MUTED_LINE, sw=1.2, dash='4,3'))
    f.append(text(img_x, 52, 'Фокальна площина', 11, MUTED, 'middle'))

    # Головний параксіальний зображуваний центр для похилого кута θ
    y_chief_img = 120
    f.append(circle(img_x, y_chief_img, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(img_x + 12, y_chief_img + 4, 'Головне зображення H\'', 11, POS, 'start', bold=True))

    # Головний промінь (Chief Ray) під кутом θ
    f.append(arrow(30, cy + 70, cx, cy, color=POS, sw=2.0))
    f.append(line(cx, cy, img_x, y_chief_img, color=POS, sw=2.0))
    f.append(text(75, cy - 20, 'Головний промінь (кута θ)', 11, POS, 'start', bold=True))

    # Крайові промені верхньої та нижньої зон
    f.append(arrow(30, cy - 30, cx, cy - 100, color=NEG, sw=1.6))
    f.append(arrow(30, cy + 170, cx, cy + 100, color=NEG, sw=1.6))

    y_marginal_top = y_chief_img - 60
    y_marginal_bot = y_chief_img - 20

    f.append(line(cx, cy - 100, img_x, y_marginal_top, color=NEG, sw=1.6))
    f.append(line(cx, cy + 100, img_x, y_marginal_bot, color=NEG, sw=1.6))

    # Утворення кометичного спалаху (конус під кутом 60°)
    coma_flare = f"M {img_x} {y_chief_img} L {img_x + 90} {y_chief_img - 70} A 40 40 0 0 1 {img_x + 90} {y_chief_img + 15} Z"
    f.append(path_d(coma_flare, fill="#fef08a", stroke="#d97706", sw=1.8))
    f.append(text(img_x + 45, y_chief_img - 15, 'Кометична', 11, "#b45309", 'middle', bold=True))
    f.append(text(img_x + 45, y_chief_img + 0, 'пляма (60°)', 11, "#b45309", 'middle', bold=True))

    # Кільця зон лінзи
    cx_spot = 730
    cy_spot = 280
    f.append(rect(cx_spot - 70, cy_spot - 70, 140, 140, fill="#f8fafc", stroke=MUTED_LINE, sw=1, rx=6))
    f.append(text(cx_spot, cy_spot - 78, 'Структура плями коми', 12, INK, 'middle', bold=True))

    f.append(circle(cx_spot - 35, cy_spot + 35, 4, fill=POS, stroke=INK, sw=1))
    f.append(circle(cx_spot - 25, cy_spot + 23, 14, fill="none", stroke="#f59e0b", sw=1.5))
    f.append(circle(cx_spot - 10, cy_spot + 8, 28, fill="none", stroke="#ef4444", sw=1.5))
    f.append(circle(cx_spot + 12, cy_spot - 14, 44, fill="none", stroke="#dc2626", sw=1.5))

    f.append(text(cx_spot - 42, cy_spot + 50, 'H\'', 10, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'coma-aberration-geometry.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Плями Зайделя (Spot Diagrams)
# ═══════════════════════════════════════════════════════════════════════════
def fig_spots():
    W, H = 820, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Характерні плями аберацій Зайделя у фокальній площині', 16, INK, 'middle', bold=True))

    panels = [
        ('а) Сферична', 110, 190),
        ('б) Кома', 310, 190),
        ('в) Астигматизм', 510, 190),
        ('г) Дисторсія', 710, 190)
    ]

    for title, cx, cy in panels:
        f.append(rect(cx - 85, cy - 95, 170, 190, fill="#f8fafc", stroke=MUTED_LINE, sw=1.2, rx=8))
        f.append(text(cx, cy - 105, title, 13, INK, 'middle', bold=True))

    cx1, cy1 = 110, 190
    f.append(circle(cx1, cy1, 3, fill=NEG, stroke=INK, sw=1))
    for r in [12, 25, 42, 60]:
        f.append(circle(cx1, cy1, r, fill="none", stroke=GLASS_BORDER, sw=1.2))
    f.append(text(cx1, cy1 + 78, 'Кругова симетрія', 10, MUTED, 'middle'))

    cx2, cy2 = 310, 190
    f.append(circle(cx2 - 40, cy2 + 35, 3, fill=POS, stroke=INK, sw=1))
    coma_shape = f"M {cx2-40} {cy2+35} L {cx2+45} {cy2-45} A 35 35 0 0 1 {cx2+40} {cy2+40} Z"
    f.append(path_d(coma_shape, fill="#fef08a", stroke="#d97706", sw=1.5))
    f.append(text(cx2, cy2 + 78, 'Асиметричний хвіст', 10, MUTED, 'middle'))

    cx3, cy3 = 510, 190
    f.append(ellipse_svg(cx3, cy3, 50, 12, fill="none", stroke="#dc2626", sw=1.8))
    f.append(ellipse_svg(cx3, cy3, 12, 50, fill="none", stroke="#2563eb", sw=1.8))
    f.append(text(cx3, cy3 + 78, 'Тангенц. / сагіт. овал', 10, MUTED, 'middle'))

    cx4, cy4 = 710, 190
    grid_barrel = (
        f"M {cx4-40} {cy4-40} Q {cx4} {cy4-52} {cx4+40} {cy4-40} "
        f"Q {cx4+52} {cy4} {cx4+40} {cy4+40} "
        f"Q {cx4} {cy4+52} {cx4-40} {cy4+40} "
        f"Q {cx4-52} {cy4} {cx4-40} {cy4-40} Z"
    )
    f.append(path_d(grid_barrel, fill="none", stroke="#16a34a", sw=1.8))

    grid_inner = (
        f"M {cx4-20} {cy4-20} Q {cx4} {cy4-26} {cx4+20} {cy4-20} "
        f"Q {cx4+26} {cy4} {cx4+20} {cy4+20} "
        f"Q {cx4} {cy4+26} {cx4-20} {cy4+20} "
        f"Q {cx4-26} {cy4} {cx4-20} {cy4-20} Z"
    )
    f.append(path_d(grid_inner, fill="none", stroke="#16a34a", sw=1.2, dash="2,2"))
    f.append(text(cx4, cy4 + 78, 'Викривлення сітки', 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'seidel-spot-diagrams.svg'), W, H, *f)

if __name__ == '__main__':
    fig_spherical()
    fig_chromatic()
    fig_coma()
    fig_spots()
    print("Figures generated successfully.")
