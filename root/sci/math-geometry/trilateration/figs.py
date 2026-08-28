# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_trilateration_2d():
    """Фігура 1: Двовимірна трилатерація для 3 кіл та радикальні осі."""
    W, H = 840, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Двовимірна трилатерація: перетин трьох кіл та радикальні осі", size=16, bold=True))

    # Координати опорних точок (маяків)
    p1x, p1y, r1 = 180.0, 360.0, 150.0  # Маяк 1
    p2x, p2y, r2 = 460.0, 360.0, 150.0  # Маяк 2
    p3x, p3y, r3 = 320.0, 140.0, 130.0  # Маяк 3

    # Точка перетину P (ціль): (320, 270)
    px, py = 320.0, 270.0

    # Кола (напівпрозорі лінії)
    f.append(circle(p1x, p1y, r1, fill="#eef3fd", stroke=NEG, sw=1.8))
    f.append(circle(p2x, p2y, r2, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(circle(p3x, p3y, r3, fill="#eafaf1", stroke=FIELD, sw=1.8))

    # Радикальні осі (прямі лінеаризованих рівнянь)
    # Вісь між колом 1 та 2 (вертикальна пряма x = 320)
    f.append(line(px, 50, px, 480, color="#8e44ad", sw=2.0, dash="6,4"))
    tb_ax12, _, _ = textbox(px, 65, "Радикальна вісь L₁₂ (x = 320)", size=11, color="#8e44ad", bold=True, fill="#f5eef8", stroke="#8e44ad")
    f.append(tb_ax12)

    # Радикальна вісь між колом 1 та 3
    ang13 = math.atan2(p3y - p1y, p3x - p1x) + math.pi / 2
    dx13 = 180 * math.cos(ang13)
    dy13 = 180 * math.sin(ang13)
    f.append(line(px - dx13, py - dy13, px + dx13, py + dy13, color="#d35400", sw=1.8, dash="5,4"))

    # Радикальна вісь між колом 2 та 3
    ang23 = math.atan2(p3y - p2y, p3x - p2x) + math.pi / 2
    dx23 = 180 * math.cos(ang23)
    dy23 = 180 * math.sin(ang23)
    f.append(line(px - dx23, py - dy23, px + dx23, py + dy23, color="#2980b9", sw=1.8, dash="5,4"))

    # Радіуси-вектори від маяків до P
    f.append(line(p1x, p1y, px, py, color=NEG, sw=1.5))
    f.append(text((p1x + px) / 2 - 35, (p1y + py) / 2 + 15, "r₁ = 150", size=11, color=NEG, bold=True))

    f.append(line(p2x, p2y, px, py, color=POS, sw=1.5))
    f.append(text((p2x + px) / 2 + 35, (p2y + py) / 2 + 15, "r₂ = 150", size=11, color=POS, bold=True))

    f.append(line(p3x, p3y, px, py, color=FIELD, sw=1.5))
    f.append(text((p3x + px) / 2 + 40, (p3y + py) / 2 - 5, "r₃ = 130", size=11, color=FIELD, bold=True))

    # Опорні точки
    f.append(circle(p1x, p1y, 6, fill=NEG, stroke="#1b3f9b", sw=2))
    tb_p1, _, _ = textbox(p1x - 55, p1y + 24, "P₁ (x₁, y₁)", size=12, color=NEG, bold=True, fill="#eef3fd", stroke=NEG)
    f.append(tb_p1)

    f.append(circle(p2x, p2y, 6, fill=POS, stroke="#962d22", sw=2))
    tb_p2, _, _ = textbox(p2x + 55, p2y + 24, "P₂ (x₂, y₂)", size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    f.append(tb_p2)

    f.append(circle(p3x, p3y, 6, fill=FIELD, stroke="#1e8449", sw=2))
    tb_p3, _, _ = textbox(p3x, p3y - 24, "P₃ (x₃, y₃)", size=12, color=FIELD, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(tb_p3)

    # Шукана цільова точка P
    f.append(circle(px, py, 7, fill="#f39c12", stroke="#b9770e", sw=2.2))
    tb_p, _, _ = textbox(px + 70, py - 20, "Ціль P(x, y)", size=13, color="#b9770e", bold=True, fill="#fef9e7", stroke="#f39c12")
    f.append(tb_p)

    # Інформаційна картка праворуч
    card_info = (
        "Алгебра лінеаризації 2D:\n"
        "1. Рівняння 3 кіл:\n"
        "   (x − xᵢ)² + (y − yᵢ)² = rᵢ²\n\n"
        "2. Віднімання 1-го рівняння:\n"
        "   Квадрати (x² + y²) взаємно\n"
        "   знищуються.\n\n"
        "3. Система 2 лінійних прямих:\n"
        "   2(x₂−x₁)x + 2(y₂−y₁)y = b₁\n"
        "   2(x₃−x₁)x + 2(y₃−y₁)y = b₂\n\n"
        "4. Перетин радикальних осей:\n"
        "   Єдиний розв'язок (x, y) через\n"
        "   визначник Крамера 2×2."
    )
    fb = fitbox(580, 70, 240, 420, card_info, size=12, pad=12, fill=FILL, stroke=LINE)
    f.append(fb)

    render(os.path.join(IMG, "trilateration-2d-intersection.svg"), W, H, *f)


def fig_trilateration_3d():
    """Фігура 2: Тривимірна трилатерація в канонічній системі координат."""
    W, H = 840, 520
    f = []

    f.append(text(W / 2, 28, "Тривимірна трилатерація: канонічний локальний базис та 4 опорні точки", size=16, bold=True))

    # Центр початку локальних координат P1 (0, 0, 0)
    o_x, o_y = 130.0, 360.0

    # Осі локального базису
    # Вісь e_x (вздовж відрізка P1 -> P2)
    p2_x, p2_y = 360.0, 360.0
    f.append(arrow(o_x, o_y, p2_x + 90, o_y, color=NEG, sw=2.2))
    f.append(text(p2_x + 105, o_y + 5, "e_x (X')", size=13, color=NEG, bold=True))

    # Вісь e_y (в площині P1, P2, P3)
    p3_x, p3_y = 230.0, 200.0
    f.append(arrow(o_x, o_y, o_x + 150 * math.cos(0.95), o_y - 150 * math.sin(0.95), color=FIELD, sw=2.2))
    f.append(text(o_x + 165 * math.cos(0.95), o_y - 165 * math.sin(0.95), "e_y (Y')", size=13, color=FIELD, bold=True))

    # Вісь e_z (перпендикуляр до площини трикутника P1-P2-P3)
    f.append(arrow(o_x, o_y, o_x, o_y - 170, color=POS, sw=2.2))
    f.append(text(o_x, o_y - 185, "e_z (Z')", size=13, color=POS, bold=True))

    # Опорні точки P1, P2, P3
    f.append(circle(o_x, o_y, 6, fill=NEG, stroke="#1b3f9b", sw=2))
    tb_p1, _, _ = textbox(o_x - 55, o_y + 24, "P₁ (0, 0, 0)", size=12, color=NEG, bold=True, fill="#eef3fd", stroke=NEG)
    f.append(tb_p1)

    f.append(circle(p2_x, p2_y, 6, fill=NEG, stroke="#1b3f9b", sw=2))
    tb_p2, _, _ = textbox(p2_x + 20, p2_y - 24, "P₂ (d, 0, 0)", size=12, color=NEG, bold=True, fill="#eef3fd", stroke=NEG)
    f.append(tb_p2)

    f.append(circle(p3_x, p3_y, 6, fill=FIELD, stroke="#1e8449", sw=2))
    tb_p3, _, _ = textbox(p3_x - 45, p3_y - 20, "P₃ (i, j, 0)", size=12, color=FIELD, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(tb_p3)

    # Трикутник базової площини P1-P2-P3
    f.append(line(o_x, o_y, p2_x, p2_y, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(o_x, o_y, p3_x, p3_y, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(p2_x, p2_y, p3_x, p3_y, color=LINE, sw=1.5, dash="4,4"))

    # Дві симетричні точки перетину 3 сфер: P+ та P-
    pt_x, pt_y_base = 280.0, 290.0
    z_offset = 95.0

    # Точка P+ (z > 0)
    pt_plus_y = pt_y_base - z_offset
    f.append(circle(pt_x, pt_plus_y, 7, fill="#27ae60", stroke="#1e8449", sw=2.2))
    tb_pplus, _, _ = textbox(pt_x + 85, pt_plus_y - 12, "Кандидат P⁺ (x', y', +z')", size=12, color="#1e8449", bold=True, fill="#eafaf1", stroke="#27ae60")
    f.append(tb_pplus)

    # Точка P- (z < 0)
    pt_minus_y = pt_y_base + z_offset
    f.append(circle(pt_x, pt_minus_y, 7, fill="#e74c3c", stroke="#c0392b", sw=2.2))
    tb_pminus, _, _ = textbox(pt_x + 85, pt_minus_y + 18, "Кандидат P⁻ (x', y', −z')", size=12, color="#c0392b", bold=True, fill="#fdecea", stroke="#e74c3c")
    f.append(tb_pminus)

    # Вісь симетрії між P+ та P-
    f.append(line(pt_x, pt_plus_y, pt_x, pt_minus_y, color=MUTED, sw=1.8, dash="4,4"))
    f.append(circle(pt_x, pt_y_base, 4, fill=MUTED, stroke=LINE))
    f.append(text(pt_x - 55, pt_y_base + 4, "(x', y', 0)", size=11, color=MUTED, italic=True))

    # 4-та опорна точка P4, що усуває неоднозначність
    p4_x, p4_y = 480.0, 110.0
    f.append(circle(p4_x, p4_y, 6, fill="#8e44ad", stroke="#6c3483", sw=2))
    tb_p4, _, _ = textbox(p4_x + 65, p4_y - 15, "Маяк P₄ (усуває знак z)", size=12, color="#6c3483", bold=True, fill="#f5eef8", stroke="#8e44ad")
    f.append(tb_p4)

    # Лінії перевірки відстані від P4 до P+ та P-
    f.append(line(p4_x, p4_y, pt_x, pt_plus_y, color="#27ae60", sw=1.8))
    f.append(text((p4_x + pt_x) / 2 + 30, (p4_y + pt_plus_y) / 2 - 10, "d(P₄, P⁺) ≈ r₄ (ІСТИНА)", size=11, color="#1e8449", bold=True))

    f.append(line(p4_x, p4_y, pt_x, pt_minus_y, color="#e74c3c", sw=1.5, dash="6,4"))
    f.append(text((p4_x + pt_x) / 2 + 35, (p4_y + pt_minus_y) / 2 + 10, "d(P₄, P⁻) ≠ r₄ (ХИБА)", size=11, color="#c0392b", bold=True))

    # Інформаційна картка праворуч
    card_info = (
        "Канонічний розв'язок 3D:\n"
        "• x' = (r₁² − r₂² + d²) / (2d)\n"
        "• y' = (r₁² − r₃² + i² + j² − 2ix') / (2j)\n"
        "• z' = ± √(r₁² − x'² − y'²)\n"
        "• 4-та точка P₄ обирає правильний знак z'."
    )
    fb = fitbox(500, 350, 325, 150, card_info, size=12, pad=10, fill=FILL, stroke=LINE)
    f.append(fb)

    render(os.path.join(IMG, "trilateration-3d-local-frame.svg"), W, H, *f)


def fig_trilateration_gdop():
    """Фігура 3: Геометрія розміщення маяків та геометричний фактор похибки (GDOP)."""
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 28, "Геометрія розміщення маяків та просторовий фактор похибки (GDOP)", size=16, bold=True))

    # Ліва панель: Оптимальна геометрія (Низький GDOP)
    panel_w = 380
    f.append(rect(25, 55, panel_w, 425, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(25 + panel_w / 2, 82, "Оптимальна конфігурація (Низький GDOP)", size=13, color="#1e8449", bold=True))

    # Маяки навколо цілі
    g1_cx, g1_cy = 215.0, 255.0  # Ціль P
    b1_x, b1_y = 115.0, 190.0
    b2_x, b2_y = 315.0, 190.0
    b3_x, b3_y = 215.0, 360.0

    # Кола
    r_good = 120.0
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (b1_x, b1_y, r_good, NEG))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (b2_x, b2_y, r_good, POS))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (b3_x, b3_y, r_good, FIELD))

    # Маяки
    f.append(circle(b1_x, b1_y, 5, fill=NEG, stroke=LINE))
    f.append(circle(b2_x, b2_y, 5, fill=POS, stroke=LINE))
    f.append(circle(b3_x, b3_y, 5, fill=FIELD, stroke=LINE))

    # Компактна область невизначеності
    f.append(circle(g1_cx, g1_cy, 13, fill="#d5f5e3", stroke="#27ae60", sw=2.0))
    f.append(circle(g1_cx, g1_cy, 5, fill="#27ae60", stroke=LINE))
    tb_g1, _, _ = textbox(g1_cx, g1_cy - 28, "Ціль P (мала похибка)", size=11, color="#1e8449", bold=True, fill="#eafaf1", stroke="#27ae60")
    f.append(tb_g1)

    desc_good = (
        "• Маяки рівномірно оточують ціль\n"
        "• Перетин кіл під кутами, близькими до 90°\n"
        "• Еліпс невизначеності компактний і симетричний\n"
        "• Матриця нормальних рівнянь добре обумовлена"
    )
    fb_g = fitbox(35, 360, panel_w - 20, 105, desc_good, size=11, pad=8, fill="#f4fbf7", stroke="#27ae60")
    f.append(fb_g)

    # Права панель: Погана геометрія (Високий GDOP)
    f.append(rect(435, 55, panel_w, 425, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(435 + panel_w / 2, 82, "Вироджена геометрія (Високий GDOP)", size=13, color="#c0392b", bold=True))

    # Маяки на одній прямій / з одного боку
    g2_cx, g2_cy = 625.0, 275.0  # Ціль P
    mb1_x, mb1_y = 515.0, 185.0
    mb2_x, mb2_y = 625.0, 175.0
    mb3_x, mb3_y = 735.0, 185.0

    r_bad = 110.0
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (mb1_x, mb1_y, r_bad, NEG))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (mb2_x, mb2_y, r_bad, POS))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (mb3_x, mb3_y, r_bad, FIELD))

    # Маяки
    f.append(circle(mb1_x, mb1_y, 5, fill=NEG, stroke=LINE))
    f.append(circle(mb2_x, mb2_y, 5, fill=POS, stroke=LINE))
    f.append(circle(mb3_x, mb3_y, 5, fill=FIELD, stroke=LINE))

    # Видовжений еліпс невизначеності
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="60" ry="12" fill="#fadbd8" stroke="#e74c3c" stroke-width="2.0"/>' % (g2_cx, g2_cy))
    f.append(circle(g2_cx, g2_cy, 5, fill="#e74c3c", stroke=LINE))
    tb_g2, _, _ = textbox(g2_cx, g2_cy + 28, "Ціль P (велика похибка уздовж осі)", size=11, color="#c0392b", bold=True, fill="#fdecea", stroke="#e74c3c")
    f.append(tb_g2)

    desc_bad = (
        "• Маяки розташовані майже на одній прямій\n"
        "• Перетин кіл під гострими дотичними кутами\n"
        "• Невизначеність розтягнута у довгий еліпс\n"
        "• Матриця AᵀA близька до сингулярної (det ≈ 0)"
    )
    fb_b = fitbox(445, 360, panel_w - 20, 105, desc_bad, size=11, pad=8, fill="#fdf4f4", stroke="#e74c3c")
    f.append(fb_b)

    render(os.path.join(IMG, "trilateration-gdop-geometry.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trilateration_2d()
    fig_trilateration_3d()
    fig_trilateration_gdop()
    print("Figures generated successfully.")
