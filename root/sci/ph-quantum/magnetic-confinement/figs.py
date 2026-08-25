# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Магнітне утримання плазми»."""

import os
import sys
import math

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def make_fig1_larmor_mirror():
    """Фігура 1: Ларморівське обертання та магнітне дзеркало."""
    w, h = 800, 440
    frags = []

    # Заголовок / роздільник панелей
    frags.append(line(400, 55, 400, 395, color=MUTED, sw=1.2, dash="4,4"))

    # ── Ліва панель: Ларморівський рух (x: 20..380) ──
    frags.append(textbox(200, 38, "Ларморівська спіраль у силовій лінії", size=15, bold=True, fill="#eef2ff", stroke="#3b82f6")[0])

    # Магнітні лінії B (горизонтальні зеленого кольору)
    for y in [130, 190, 250, 310]:
        frags.append(line(30, y, 370, y, color=FIELD, sw=1.5, dash="6,3"))
        frags.append(arrow(350, y, 370, y, color=FIELD, sw=1.8))
    frags.append(text(375, 130, "B", size=14, color=FIELD, bold=True, anchor="start"))

    # Спіраль ларморівської орбіти електрона / іона
    cx, cy = 200, 220
    r_x, r_y = 65, 38
    path_d = []
    for step in range(3):
        x_shift = (step - 1) * 70
        for deg in range(0, 360, 10):
            rad = math.radians(deg)
            px = cx + x_shift + r_x * math.cos(rad) * 0.4
            py = cy + r_y * math.sin(rad)
            if deg == 0 and step == 0:
                path_d.append("M %.1f %.1f" % (px, py))
            else:
                path_d.append("L %.1f %.1f" % (px, py))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), POS))

    # Центр обертання та радіус r_L
    frags.append(circle(cx + 10, cy, 6, fill=POS, stroke=LINE, sw=1.2))
    frags.append(text(cx + 10, cy - 12, "+q (іон)", size=12, color=POS, bold=True))

    # Стрілка радіуса r_L
    frags.append(line(cx + 10, cy, cx + 10, cy + r_y, color=LINE, sw=1.5))
    frags.append(text(cx + 25, cy + 20, "r_L", size=13, color=INK, bold=True, italic=True))

    # Стрілка швидкості v_perp та сили Лоренца F_L
    frags.append(arrow(cx + 10, cy + r_y, cx - 40, cy + r_y, color=NEG, sw=1.8))
    frags.append(text(cx - 20, cy + r_y + 18, "v_perp", size=12, color=NEG, bold=True))

    frags.append(arrow(cx + 10, cy + r_y, cx + 10, cy + 10, color=POS, sw=1.8))
    frags.append(text(cx + 26, cy + 18, "F_L", size=12, color=POS, bold=True))

    # Формула Лармора у рамці
    frags.append(textbox(200, 375, "r_L = (m · v_perp) / (q · B)\nω_c = (q · B) / m", size=13, fill=FILL, stroke=LINE, pad=8)[0])

    # ── Права панель: Магнітне дзеркало (x: 420..780) ──
    frags.append(textbox(600, 38, "Принцип магнітного дзеркала", size=15, bold=True, fill="#eef2ff", stroke="#3b82f6")[0])

    top_line = "M 430 110 Q 600 190 770 120"
    bot_line = "M 430 330 Q 600 250 770 320"
    mid_top = "M 430 170 Q 600 205 770 180"
    mid_bot = "M 430 270 Q 600 235 770 260"

    for p in [top_line, bot_line, mid_top, mid_bot]:
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' % (p, FIELD))

    frags.append(text(760, 100, "B_max", size=13, color=FIELD, bold=True))
    frags.append(text(440, 95, "B_min", size=13, color=FIELD, bold=True))

    path_reflect = []
    for deg in range(0, 540, 15):
        t = deg / 540.0
        x_pos = 460 + 190 * math.sin(t * math.pi)
        r_current = 45 * (1.0 - 0.45 * math.sin(t * math.pi))
        y_pos = 220 + r_current * math.sin(math.radians(deg))
        if deg == 0:
            path_reflect.append("M %.1f %.1f" % (x_pos, y_pos))
        else:
            path_reflect.append("L %.1f %.1f" % (x_pos, y_pos))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_reflect), NEG))

    # Силовий вектор гальмування F_z = -\mu \nabla B
    frags.append(arrow(620, 220, 550, 220, color=POS, sw=2.2))
    frags.append(text(585, 205, "F_z = -μ · ∇_z B", size=13, color=POS, bold=True))

    # Конус втрат у рамці
    frags.append(textbox(600, 375, "Збереження магнітного моменту: μ = m·v_perp² / (2B) = const\nКонус втрат: sin²(θ_loss) = B_min / B_max", size=12, fill=FILL, stroke=LINE, pad=8)[0])

    render(os.path.join(IMG_DIR, "magnetic-bottle-larmor.svg"), w, h, *frags)


def make_fig2_drift_charge_separation():
    """Фігура 2: Дрейфи та розділення зарядів у тороїдальному полів."""
    w, h = 820, 440
    frags = []

    # Ліва панель: Тороїдальний зріз та розділення зарядів (x: 20..400)
    frags.append(textbox(200, 35, "Розділення зарядів у торі (без B_θ)", size=14, bold=True, fill="#fee2e2", stroke="#ef4444")[0])

    cx, cy = 190, 220
    r_plasma = 85
    frags.append(circle(cx, cy, r_plasma, fill="#f8fafc", stroke="#94a3b8", sw=2))

    frags.append(text(cx, cy - 35, "B_φ (⊗)", size=13, color=FIELD, bold=True))
    frags.append(text(cx, cy - 10, "∇B (←)", size=12, color=MUTED, bold=True))

    for i, x_off in enumerate([-45, -15, 15, 45]):
        frags.append(circle(cx + x_off, cy - r_plasma + 20, 11, fill="#fee2e2", stroke=POS, sw=1.5))
        frags.append(text(cx + x_off, cy - r_plasma + 20, "+", size=13, color=POS, bold=True))

        frags.append(circle(cx + x_off, cy + r_plasma - 20, 11, fill="#dbeafe", stroke=NEG, sw=1.5))
        frags.append(text(cx + x_off, cy + r_plasma - 20, "-", size=13, color=NEG, bold=True))

    frags.append(arrow(cx, cy + 10, cx, cy + 50, color=POS, sw=2))
    frags.append(text(cx + 15, cy + 30, "E_z", size=14, color=POS, bold=True))

    # Викид плазми назовні (стрілка праворуч)
    frags.append(arrow(cx + r_plasma, cy, cx + r_plasma + 35, cy, color="#dc2626", sw=2.5))
    frags.append(textbox(cx + r_plasma + 75, cy, "v_E = (E × B) / B²\n(викид на стінку!)", size=11, color="#dc2626", bold=True, fill="#fff1f2", stroke="#fca5a5")[0])

    # Права панель: Компенсація через обертальне перетворення (x: 420..800)
    frags.append(textbox(610, 35, "Компенсація через обертальне перетворення B_θ", size=14, bold=True, fill="#dcfce7", stroke="#16a34a")[0])

    cx2, cy2 = 610, 220
    frags.append(circle(cx2, cy2, r_plasma, fill="#f8fafc", stroke="#16a34a", sw=2))

    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (cx2, cy2, r_plasma - 25, FIELD))
    frags.append(arrow(cx2 + r_plasma - 25, cy2, cx2 + r_plasma - 25, cy2 - 20, color=FIELD, sw=2))
    frags.append(text(cx2 + r_plasma - 10, cy2 - 35, "B_θ", size=14, color=FIELD, bold=True))

    frags.append(arrow(cx2 - 40, cy2 - 50, cx2 + 40, cy2 + 50, color=INK, sw=2))
    frags.append(text(cx2 + 55, cy2 + 55, "j_∥ (струм Пфірша — Шлютера)", size=11, color=INK, bold=True))

    frags.append(textbox(610, 375, "Гвинтова силова лінія з'єднує верх і низ тора:\nструм j_∥ вирівнює потенціал та нейтралізує E_z", size=12, fill=FILL, stroke=LINE, pad=8)[0])

    render(os.path.join(IMG_DIR, "drift-charge-separation.svg"), w, h, *frags)


def make_fig3_tokamak_vs_stellarator():
    """Фігура 3: Порівняння геології токамака та стеларатора."""
    w, h = 840, 460
    frags = []

    frags.append(textbox(215, 35, "ТОКАМАК (Аксисиметрична система)", size=15, bold=True, fill="#eef2ff", stroke="#3b82f6")[0])

    cx1, cy1 = 215, 230
    rx_out, ry_out = 150, 85
    rx_in, ry_in = 70, 40

    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="2"/>' % (cx1, cy1, rx_out, ry_out, "#94a3b8"))
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="2"/>' % (cx1, cy1, rx_in, ry_in, "#94a3b8"))

    # Центральний соленоїд
    frags.append(rect(cx1 - 35, cy1 - 35, 70, 70, fill="#dbeafe", stroke="#2563eb", sw=2, rx=4))
    frags.append(mtext(cx1, cy1 - 10, "Соленоїд\n(індуктор)", size=11, color="#1e40af", bold=True))

    frags.append(arrow(cx1 + 100, cy1 + 50, cx1 + 125, cy1 + 40, color=POS, sw=2.5))
    frags.append(text(cx1 + 130, cy1 + 65, "I_p (струм плазми)", size=12, color=POS, bold=True))

    for angle_deg in [-120, -60, 0, 60, 120]:
        rad = math.radians(angle_deg)
        px = cx1 + (rx_out + rx_in) / 2 * math.cos(rad)
        py = cy1 + (ry_out + ry_in) / 2 * math.sin(rad)
        frags.append(circle(px, py, 20, fill="none", stroke=FIELD, sw=2))
    frags.append(text(cx1 - 135, cy1 - 65, "Котушки B_φ", size=12, color=FIELD, bold=True))

    frags.append(textbox(215, 395, "Обертальне перетворення формується\nСТРУМОМ ПЛАЗМИ I_p (аксіальна симетрія)", size=12, fill=FILL, stroke=LINE, pad=8)[0])

    frags.append(textbox(625, 35, "СТЕЛАРАТОР (3D-модульна система)", size=15, bold=True, fill="#fef3c7", stroke="#d97706")[0])

    cx2, cy2 = 625, 230

    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,3"/>' % (cx2, cy2, rx_out, ry_out, "#94a3b8"))
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,3"/>' % (cx2, cy2, rx_in, ry_in, "#94a3b8"))

    for i in range(8):
        ang = i * (2 * math.pi / 8)
        px = cx2 + 110 * math.cos(ang)
        py = cy2 + 60 * math.sin(ang)
        tilt = (i % 2) * 35 - 15
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="18" ry="28" transform="rotate(%d %.1f %.1f)" fill="none" stroke="%s" stroke-width="2.2"/>' % (px, py, tilt, px, py, "#b45309"))

    frags.append(text(cx2, cy2 - 10, "I_p = 0", size=16, color="#b45309", bold=True))
    frags.append(text(cx2, cy2 + 12, "(без струму плазми)", size=11, color=INK))

    frags.append(textbox(625, 395, "Поле створюється ЗОВНІШНІМИ 3D-КОТУШКАМИ\nСтаціонарний режим без зірваних нестійкостей", size=12, fill=FILL, stroke=LINE, pad=8)[0])

    render(os.path.join(IMG_DIR, "tokamak-vs-stellarator.svg"), w, h, *frags)


def make_fig4_grad_shafranov_flux():
    """Фігура 4: Рівноважні магнітні поверхні та дивертор."""
    w, h = 820, 520
    frags = []

    frags.append(textbox(410, 35, "Магнітна конфігурація токамака з X-точкою та дивертором", size=15, bold=True, fill="#eef2ff", stroke="#3b82f6")[0])

    cx, cy = 410, 215

    axis_x, axis_y = cx + 25, cy - 20
    frags.append(circle(axis_x, axis_y, 4, fill=POS, stroke=LINE, sw=1.2))
    frags.append(text(axis_x + 12, axis_y - 8, "Магнітна вісь (ψ_0)", size=12, color=POS, bold=True))

    radii = [(25, 38), (55, 80), (90, 130), (125, 175)]
    for rx, ry in radii:
        dx = (140 - rx) * 0.18
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.6"/>' % (axis_x - dx, axis_y, rx, ry, "#2563eb"))

    frags.append(text(axis_x - 110, axis_y, "ψ = const", size=12, color="#2563eb", bold=True))

    frags.append(line(cx, axis_y, axis_x, axis_y, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(cx + 10, axis_y + 16, "ΔR (зсув Шафранова)", size=11, color=POS, bold=True))

    x_point_x, x_point_y = axis_x - 15, cy + 165
    frags.append(circle(x_point_x, x_point_y, 5, fill="#dc2626", stroke=LINE, sw=1.2))
    frags.append(text(x_point_x + 15, x_point_y, "X-точка (ψ_edge)", size=13, color="#dc2626", bold=True))

    sep_path = "M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (
        x_point_x, x_point_y,
        axis_x + 160, axis_y + 100, axis_x + 150, axis_y - 200, x_point_x, x_point_y - 350,
        axis_x - 180, axis_y - 200, axis_x - 170, axis_y + 100, x_point_x, x_point_y
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (sep_path, "#dc2626"))

    sol_left = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x_point_x, x_point_y, x_point_x - 40, x_point_y + 40, x_point_x - 70, x_point_y + 70)
    sol_right = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x_point_x, x_point_y, x_point_x + 40, x_point_y + 40, x_point_x + 70, x_point_y + 70)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,2"/>' % (sol_left, FIELD))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,2"/>' % (sol_right, FIELD))

    frags.append(rect(x_point_x - 90, x_point_y + 60, 35, 12, fill="#475569", stroke=LINE, sw=1.5, rx=2))
    frags.append(rect(x_point_x + 55, x_point_y + 60, 35, 12, fill="#475569", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(x_point_x, x_point_y + 68, "Дивертор (W)", size=12, color="#334155", bold=True))

    frags.append(textbox(410, 480, "Рівняння Града — Шафранова: R · ∂/∂R ((1/R) · ∂ψ/∂R) + ∂²ψ/∂Z² = -μ₀ R² p'(ψ) - F(ψ) F'(ψ)", size=12, fill=FILL, stroke=LINE, pad=8)[0])

    render(os.path.join(IMG_DIR, "grad-shafranov-flux.svg"), w, h, *frags)


if __name__ == '__main__':
    make_fig1_larmor_mirror()
    make_fig2_drift_charge_separation()
    make_fig3_tokamak_vs_stellarator()
    make_fig4_grad_shafranov_flux()
    print("Всі фігури успішно згенеровано у", IMG_DIR)
