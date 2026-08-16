# -*- coding: utf-8 -*-
"""Фігури до теми «Метод дзеркальних зображень в електродинаміці».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Провідна площина та дзеркальне зображення ─────────────────────
def fig_plane_image():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Точковий заряд над заземленою провідною площиною", size=16, bold=True))

    mid_y = 210

    # Напівпростір z < 0 (провідник/заземлення)
    f.append(rect(40, mid_y, W - 80, H - mid_y - 40, fill="#f0f4f8", stroke="none", rx=0))

    # Лінія заземленої площини z = 0
    f.append(line(40, mid_y, W - 40, mid_y, color=INK, sw=2.5))

    # Штриховка заземлення знизу площини
    for x in range(50, W - 40, 20):
        f.append(line(x, mid_y, x - 10, mid_y + 12, color=MUTED, sw=1.2))

    # Позначка V = 0 для площини
    body, _, _ = textbox(W - 100, mid_y - 20, "V = 0 (заземлена площина)", size=12, pad=6, fill="#e8f4ea", stroke=FIELD, sw=1.2, color=FIELD, bold=True)
    f.append(body)

    # Реальний заряд +q на відстані d над площиною
    q_x, q_y = W / 2, mid_y - 120
    f.append(circle(q_x, q_y, 16, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(q_x, q_y + 5, "+q", size=15, color=POS, bold=True))
    f.append(text(q_x + 32, q_y + 4, "Реальний заряд", size=13, color=POS, bold=True, anchor="start"))

    # Фіктивний дзеркальний заряд -q на відстані -d під площиною
    img_x, img_y = W / 2, mid_y + 120
    f.append(circle(img_x, img_y, 16, fill="#d6eaf8", stroke=NEG, sw=2))
    f.append(text(img_x, img_y + 5, "−q", size=15, color=NEG, bold=True))
    f.append(text(img_x + 32, img_y + 4, "Дзеркальне зображення (фіктивне)", size=13, color=NEG, bold=True, anchor="start"))

    # Позначки відстаней d і -d
    f.append(line(q_x - 120, q_y, q_x - 120, mid_y, color=MUTED, sw=1.2, dash="3,3"))
    f.append(arrow(q_x - 120, mid_y, q_x - 120, q_y, color=MUTED, sw=1.2))
    f.append(text(q_x - 130, (q_y + mid_y) / 2 + 4, "d", size=13, color=MUTED, bold=True, anchor="end"))

    f.append(line(q_x - 120, mid_y, q_x - 120, img_y, color=MUTED, sw=1.2, dash="3,3"))
    f.append(arrow(q_x - 120, mid_y, q_x - 120, img_y, color=MUTED, sw=1.2))
    f.append(text(q_x - 130, (img_y + mid_y) / 2 + 4, "d", size=13, color=MUTED, bold=True, anchor="end"))

    # Силові лінії в верхній півплощині (z > 0)
    angles = [-75, -50, -25, 0, 25, 50, 75]
    for a in angles:
        rad = math.radians(a)
        dx = 140 * math.tan(rad)
        px = q_x + dx
        py = mid_y
        if 50 <= px <= W - 50:
            ctrl_x = q_x + dx * 0.5
            ctrl_y = (q_y + py) / 2
            path_str = f'<path d="M {q_x:.1f} {q_y:.1f} Q {ctrl_x:.1f} {ctrl_y:.1f} {px:.1f} {py:.1f}" fill="none" stroke="{FIELD}" stroke-width="1.4" stroke-dasharray="none"/>'
            f.append(path_str)

    # Позначка для індукованого заряду на поверхні
    f.append(text(W / 2 - 180, mid_y - 10, "Індукований поверхневий заряд σ(x,y) < 0", size=12, color=NEG, bold=True, anchor="end"))

    # Пояснювальний блок знизу
    body, _, _ = textbox(W / 2, H - 22, "У верхньому напівпросторі (z > 0) поле двох зарядів (+q та −q) ТОЧНО збігається з полем провідника", size=12, pad=6, fill="#f4f6f8", stroke=LINE, sw=1.2)
    f.append(body)

    return render(os.path.join(IMG, "plane-image.svg"), W, H, *f)


# ── Фігура 2: Сферична провідна поверхня та інверсія ─────────────────────────
def fig_sphere_image():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Точковий заряд біля заземленої провідної сфери", size=16, bold=True))

    cx, cy = 220, 210
    R = 100

    # Заземлена сфера
    f.append(circle(cx, cy, R, fill="#eaf2f8", stroke=INK, sw=2))
    f.append(text(cx, cy - 10, "Сфера", size=14, bold=True, color=INK))
    f.append(text(cx, cy + 12, "радіуса R", size=12, color=MUTED))
    f.append(text(cx, cy + 30, "V = 0", size=13, bold=True, color=FIELD))

    # Центр сфери O
    f.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx - 12, cy + 4, "O", size=13, bold=True, anchor="end"))

    # Вісь симетрії
    f.append(line(60, cy, W - 60, cy, color=MUTED, sw=1.2, dash="4,4"))

    # Реальний заряд q на відстані d від O
    d = 260
    q_x, q_y = cx + d, cy
    f.append(circle(q_x, q_y, 16, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(q_x, q_y + 5, "+q", size=15, color=POS, bold=True))
    f.append(text(q_x, q_y - 26, "Реальний заряд q", size=13, color=POS, bold=True))
    f.append(text(q_x, q_y + 34, "на відстані d", size=12, color=MUTED))

    # Дзеркальний заряд q' на відстані d' = R^2 / d від O
    dp = (R * R) / d
    qp_x, qp_y = cx + dp, cy
    f.append(circle(qp_x, qp_y, 11, fill="#d6eaf8", stroke=NEG, sw=2))
    f.append(text(qp_x, qp_y + 4, "q′", size=13, color=NEG, bold=True))

    # Виносний підпис для дзеркального заряду
    f.append(line(qp_x, qp_y - 12, qp_x + 30, cy - 70, color=NEG, sw=1.2))
    body, _, _ = textbox(qp_x + 90, cy - 80, "Дзеркальний заряд q′ = −q·(R/d)\nна відстані d′ = R²/d від центра O", size=11, pad=6, fill="#e8f4f8", stroke=NEG, sw=1.2, color=NEG)
    f.append(body)

    # Радіус R від центра до сфери
    r_angle = math.radians(-55)
    rx_end = cx + R * math.cos(r_angle)
    ry_end = cy + R * math.sin(r_angle)
    f.append(line(cx, cy, rx_end, ry_end, color=INK, sw=1.5))
    f.append(text((cx + rx_end) / 2 - 10, (cy + ry_end) / 2 - 6, "R", size=13, bold=True, color=INK))

    # Довільна точка P на поверхні сфери для геометрії
    p_angle = math.radians(45)
    px = cx + R * math.cos(p_angle)
    py = cy + R * math.sin(p_angle)
    f.append(circle(px, py, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px + 12, py + 14, "P (V=0)", size=12, bold=True, color=FIELD))

    # Відрізки від P до q та q'
    f.append(line(px, py, q_x, q_y, color=POS, sw=1.2, dash="3,3"))
    f.append(line(px, py, qp_x, qp_y, color=NEG, sw=1.2, dash="3,3"))

    # Співвідношення відстаней r / r' = d / R
    body, _, _ = textbox(W / 2 + 100, H - 35, "Для будь-якої точки P на сфері:  r / r′ = d / R = const  ⇒  V(P) = 0", size=12, pad=7, fill="#fcfcfd", stroke=FIELD, sw=1.4, color=INK, bold=True)
    f.append(body)

    return render(os.path.join(IMG, "sphere-image.svg"), W, H, *f)


# ── Фігура 3: Кутовий відбивач 90 градусів ──────────────────────────────────
def fig_corner_reflector():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Дзеркальні зображення у 90-градусному кутовому провіднику", size=16, bold=True))

    cx, cy = W / 2, 220

    # Провідні стінки
    f.append(line(cx, cy, cx + 220, cy, color=INK, sw=3))
    f.append(line(cx, cy, cx, cy - 180, color=INK, sw=3))

    # Заштрихований провідник поза 1-м квадрантом
    f.append(rect(cx - 220, cy - 180, 220, 340, fill="#f2f4f7", stroke="none", rx=0))
    f.append(rect(cx, cy, 220, 160, fill="#f2f4f7", stroke="none", rx=0))

    # Лінії осей
    f.append(line(cx - 220, cy, cx + 220, cy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx, cy - 180, cx, cy + 160, color=MUTED, sw=1.2, dash="4,4"))

    # Позначка заземлення V=0
    f.append(text(cx + 140, cy + 18, "V = 0", size=13, bold=True, color=FIELD))
    f.append(text(cx - 18, cy - 120, "V = 0", size=13, bold=True, color=FIELD, anchor="end"))

    # Координати реального заряду у 1-му квадранті
    dx, dy = 110, 90
    q1_x, q1_y = cx + dx, cy - dy
    q2_x, q2_y = cx - dx, cy - dy
    q3_x, q3_y = cx - dx, cy + dy
    q4_x, q4_y = cx + dx, cy + dy

    # 1. Реальний заряд +q в I квадранті
    f.append(circle(q1_x, q1_y, 16, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(q1_x, q1_y + 5, "+q", size=15, color=POS, bold=True))
    f.append(text(q1_x + 24, q1_y + 4, "Реальний (+q)", size=12, color=POS, bold=True, anchor="start"))

    # 2. Зображення -q у II квадранті
    f.append(circle(q2_x, q2_y, 15, fill="#d6eaf8", stroke=NEG, sw=2))
    f.append(text(q2_x, q2_y + 5, "−q", size=15, color=NEG, bold=True))
    f.append(text(q2_x - 24, q2_y + 4, "Зображення 1 (−q)", size=12, color=NEG, bold=True, anchor="end"))

    # 3. Зображення -q у IV квадранті
    f.append(circle(q4_x, q4_y, 15, fill="#d6eaf8", stroke=NEG, sw=2))
    f.append(text(q4_x, q4_y + 5, "−q", size=15, color=NEG, bold=True))
    f.append(text(q4_x + 24, q4_y + 4, "Зображення 2 (−q)", size=12, color=NEG, bold=True, anchor="start"))

    # 4. Зображення +q у III квадранті
    f.append(circle(q3_x, q3_y, 15, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(q3_x, q3_y + 5, "+q", size=15, color=POS, bold=True))
    f.append(text(q3_x - 24, q3_y + 4, "Зображення 3 (+q)", size=12, color=POS, bold=True, anchor="end"))

    # Пунктирний прямокутник симетрії
    f.append(rect(cx - dx, cy - dy, 2 * dx, 2 * dy, fill="none", stroke=MUTED, sw=1))

    # Пояснення кількості зображень
    body, _, _ = textbox(W / 2, H - 24, "Для кута α = 90° виникає N = (360° / 90°) − 1 = 3 дзеркальних зображення", size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.2, color=INK, bold=True)
    f.append(body)

    return render(os.path.join(IMG, "corner-reflector.svg"), W, H, *f)


# ── Фігура 4: Межа двох діелектриків ─────────────────────────────────────────
def fig_dielectric_interface():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Точковий заряд на межі двох діелектриків", size=16, bold=True))

    mid_y = 210

    # Середовище 1 (верх) ε1
    f.append(rect(40, 50, W - 80, mid_y - 50, fill="#fcf8f2", stroke="none", rx=0))
    f.append(text(70, 75, "Середовище 1 (проникність ε₁)", size=13, bold=True, color="#8e44ad", anchor="start"))

    # Середовище 2 (низ) ε2
    f.append(rect(40, mid_y, W - 80, H - mid_y - 50, fill="#edf7f6", stroke="none", rx=0))
    f.append(text(70, mid_y + 30, "Середовище 2 (проникність ε₂)", size=13, bold=True, color="#16a085", anchor="start"))

    # Межа розділу z = 0
    f.append(line(40, mid_y, W - 40, mid_y, color=INK, sw=2))
    f.append(text(W - 60, mid_y - 8, "Площина z = 0", size=12, color=MUTED, anchor="end"))

    # Реальний заряд q у середовищі 1
    q_x, q_y = W / 2 - 100, mid_y - 90
    f.append(circle(q_x, q_y, 15, fill="#fadbd8", stroke=POS, sw=2))
    f.append(text(q_x, q_y + 5, "+q", size=15, color=POS, bold=True))
    f.append(text(q_x - 24, q_y + 4, "Заряд q", size=13, color=POS, bold=True, anchor="end"))

    # Дзеркальний заряд q' для поля в середовищі 1
    qp_x, qp_y = q_x, mid_y + 90
    f.append(circle(qp_x, qp_y, 13, fill="#eaeded", stroke=MUTED, sw=1.8))
    f.append(text(qp_x, qp_y + 4, "q′", size=13, color=MUTED, bold=True))
    f.append(text(qp_x - 24, qp_y + 4, "Зображення q′", size=12, color=MUTED, bold=True, anchor="end"))

    # Пояснення формул для q' та q''
    f.append(line(W / 2 + 60, 60, W / 2 + 60, H - 60, color=MUTED, sw=1, dash="4,4"))

    text_box1 = "Поле в середовищі 1 (z > 0):\nутворено зарядом q та зображенням:\nq′ = −q · (ε₂ − ε₁) / (ε₁ + ε₂)"
    body1, _, _ = textbox(W / 2 + 190, mid_y - 65, text_box1, size=11, pad=7, fill="#ffffff", stroke="#8e44ad", sw=1.2, color=INK)
    f.append(body1)

    text_box2 = "Поле в середовищі 2 (z < 0):\nутворено фіктивним зарядом у точці q:\nq″ = q · 2ε₂ / (ε₁ + ε₂)"
    body2, _, _ = textbox(W / 2 + 190, mid_y + 65, text_box2, size=11, pad=7, fill="#ffffff", stroke="#16a085", sw=1.2, color=INK)
    f.append(body2)

    # Пояснювальний підпис знизу
    body, _, _ = textbox(W / 2, H - 22, "Граничні умови діелектрика вимагають неперервності E_t та D_n на межі z = 0", size=12, pad=6, fill="#f4f6f8", stroke=LINE, sw=1.2)
    f.append(body)

    return render(os.path.join(IMG, "dielectric-interface.svg"), W, H, *f)


# ── Фігура 5: Розподіл індукованого поверхневого заряду ──────────────────────
def fig_induced_density():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Густина індукованого поверхневого заряду σ(r) на площині", size=16, bold=True))

    ox, oy = 100, 290
    gw, gh = 580, 220

    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))  # Вісь r
    f.append(line(ox + gw / 2, oy, ox + gw / 2, oy - gh, color=INK, sw=1.8))  # Вісь |σ|

    f.append(text(ox + gw + 15, oy + 4, "r (відстань від проекції)", size=12, color=INK, anchor="start"))
    f.append(text(ox + gw / 2, oy - gh - 12, "Густина |σ(r)|", size=12, color=INK, bold=True))

    pts = []
    d_val = 60.0
    max_sigma = 180.0

    for px in range(-270, 271, 5):
        r_val = float(px)
        denom = math.pow(1.0 + (r_val / d_val) * (r_val / d_val), 1.5)
        sigma_val = max_sigma / denom
        scr_x = ox + gw / 2 + r_val
        scr_y = oy - sigma_val
        pts.append(f"{scr_x:.1f},{scr_y:.1f}")

    polyline_str = f'<polyline points="{" ".join(pts)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>'
    f.append(polyline_str)

    fill_pts = [f"{ox + gw / 2 - 270:.1f},{oy:.1f}"] + pts + [f"{ox + gw / 2 + 270:.1f},{oy:.1f}"]
    polygon_str = f'<polygon points="{" ".join(fill_pts)}" fill="#d6eaf8" opacity="0.4" stroke="none"/>'
    f.append(polygon_str)

    peak_x, peak_y = ox + gw / 2, oy - max_sigma
    f.append(circle(peak_x, peak_y, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(line(peak_x, peak_y, peak_x + 80, peak_y - 20, color=NEG, sw=1.2))

    body_pk, _, _ = textbox(peak_x + 160, peak_y - 20, "σ_max = −q / (2π·d²)\n(найбільша концентрація прямо під зарядом)", size=11, pad=6, fill="#ffffff", stroke=NEG, sw=1.2, color=NEG)
    f.append(body_pk)

    body_int, _, _ = textbox(ox + 130, oy - 140, "Повний індукований заряд:\nQ_ind = ∫ σ(r) dS = −q", size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.4, color=FIELD, bold=True)
    f.append(body_int)

    return render(os.path.join(IMG, "induced-density.svg"), W, H, *f)


if __name__ == "__main__":
    fig_plane_image()
    fig_sphere_image()
    fig_corner_reflector()
    fig_dielectric_interface()
    fig_induced_density()
    print("Всі 5 фігур успішно згенеровано у ./img/")
