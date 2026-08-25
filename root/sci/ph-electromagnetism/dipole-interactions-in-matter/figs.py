# -*- coding: utf-8 -*-
"""Фігури до теми «Електричний диполь і його поле».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_dipole_vector_setup():
    """Фігура 1: Геометрія електричного диполя та векторний розрахунок у точці P."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Геометрія електричного диполя та радіус-вектори", size=16, bold=True))

    # Панель для схеми
    f.append(rect(20, 48, W - 40, H - 76, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Полярна вісь z (вертикальна вісь диполя)
    cx, cy = 240, 240
    f.append(line(cx, 400, cx, 80, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx + 12, 90, "вісь z (вісь диполя)", size=12, color=MUTED, anchor="start"))

    # Заряди: -q внизу, +q вгорі
    d_half = 60
    y_neg = cy + d_half
    y_pos = cy - d_half

    # Вектор плеча d від -q до +q
    f.append(arrow(cx, y_neg, cx, y_pos, color=FIELD, sw=2.5))
    f.append(text(cx - 25, cy, "d", size=14, bold=True, color=FIELD, italic=True))

    # Точкові заряди
    f.append(circle(cx, y_neg, 14, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(cx, y_neg + 5, "−q", size=14, bold=True, color=NEG))

    f.append(circle(cx, y_pos, 14, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(cx, y_pos + 5, "+q", size=14, bold=True, color=POS))

    # Точка спостереження P
    px, py = 540, 110
    f.append(circle(px, py, 6, fill=INK, stroke='none'))
    f.append(text(px + 15, py - 5, "P(r, θ)", size=14, bold=True, anchor="start"))

    # Радіус-вектор r від центру диполя до P
    f.append(arrow(cx, cy, px, py, color=INK, sw=2))
    f.append(text(380, 160, "r", size=14, bold=True, color=INK, italic=True))

    # Радіус-вектор r_+ від +q до P
    f.append(line(cx, y_pos, px, py, color=POS, sw=1.5, dash="3,3"))
    f.append(text(400, 85, "r₊", size=13, bold=True, color=POS))

    # Радіус-вектор r_- від -q до P
    f.append(line(cx, y_neg, px, py, color=NEG, sw=1.5, dash="3,3"))
    f.append(text(410, 240, "r₋", size=13, bold=True, color=NEG))

    # Полярний кут θ між віссю z та вектором r
    # Дуга кута
    f.append('<path d="M 240,180 A 60,60 0 0,1 275,195" fill="none" stroke="#2563eb" stroke-width="1.8"/>')
    f.append(text(270, 175, "θ", size=14, bold=True, color="#2563eb", italic=True))

    # Дипольний момент p = q * d (вектор поруч)
    f.append(arrow(cx - 60, y_neg, cx - 60, y_pos, color="#059669", sw=3))
    f.append(text(cx - 85, cy, "p = q·d", size=13, bold=True, color="#059669"))

    # Формули справа в текстових блоках
    tb1, _, _ = textbox(600, 260, "Електричний потенціал:\nφ(r, θ) = (1 / 4πε₀) · (p · cos θ / r²)\n\nНапруженість поля:\nE_r = (1 / 4πε₀) · (2p cos θ / r³)\nE_θ = (1 / 4πε₀) · (p sin θ / r³)", size=12, pad=12, fill="#ffffff", stroke="#93c5fd", sw=1.5)
    f.append(tb1)

    return render(os.path.join(IMG, "dipole-vector-setup.svg"), W, H, *f)


def fig_dipole_field_lines():
    """Фігура 2: Картина силових ліній та векторів напруженості дипольного поля."""
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Силові лінії та вектори напруженості поля диполя", size=16, bold=True))
    f.append(rect(20, 46, W - 40, H - 70, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    cx, cy = 340, 230
    dy = 70

    # Силові лінії (криві Безьє)
    curves = [
        "M 340,160 C 260,160 260,300 340,300",
        "M 340,160 C 420,160 420,300 340,300",
        "M 340,160 C 180,140 180,320 340,300",
        "M 340,160 C 500,140 500,320 340,300",
        "M 340,160 C 100,100 100,360 340,300",
        "M 340,160 C 580,100 580,360 340,300",
    ]

    for c in curves:
        f.append(f'<path d="{c}" fill="none" stroke="#60a5fa" stroke-width="1.8" stroke-dasharray="none"/>')

    # Осьові лінії (полюс та екватор)
    f.append(line(cx, 60, cx, 400, color=MUTED, sw=1, dash="3,3"))
    f.append(line(60, cy, 620, cy, color=MUTED, sw=1, dash="3,3"))

    # Заряди
    f.append(circle(cx, cy - dy, 16, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(cx, cy - dy + 5, "+q", size=14, bold=True, color=POS))

    f.append(circle(cx, cy + dy, 16, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(cx, cy + dy + 5, "−q", size=14, bold=True, color=NEG))

    # Стрілки напрямку поля на силових лініях
    f.append(arrow(210, 230, 210, 240, color=NEG, sw=2))
    f.append(arrow(470, 230, 470, 240, color=NEG, sw=2))
    f.append(arrow(130, 230, 130, 240, color=NEG, sw=2))
    f.append(arrow(550, 230, 550, 240, color=NEG, sw=2))

    # Вектор E на полюсі (θ = 0)
    f.append(arrow(cx, 110, cx, 65, color=POS, sw=2.5))
    f.append(text(cx + 15, 85, "E_полюс ∥ p (учічі сильніше)", size=12, bold=True, color=POS, anchor="start"))

    # Вектор E на екваторі (θ = π/2)
    f.append(arrow(470, cy, 470, cy + 45, color=NEG, sw=2.5))
    f.append(text(485, cy + 25, "E_екватор ⇈ (−p)", size=12, bold=True, color=NEG, anchor="start"))

    # Пояснювальний блок справа
    tb, _, _ = textbox(630, 130, "Характеристики поля:\n• Спадання: E ~ 1/r³\n• Полюси (θ=0, π): E ∥ p\n• Екватор (θ=π/2): E ⇈ −p\n• E_полюс = 2 · E_екватор", size=11, pad=10, fill="#ffffff", stroke=MUTED, sw=1.2)
    f.append(tb)

    return render(os.path.join(IMG, "dipole-field-lines.svg"), W, H, *f)


def fig_dipole_torque_energy():
    """Фігура 3: Диполь у зовнішньому однорідному електричному полі: момент та енергія."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Диполь у зовнішньому полі: обертальний момент та потенціальна енергія", size=16, bold=True))

    # Ліва панель: Диполь і сили
    f.append(rect(20, 50, 360, 340, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(200, 75, "Обертальний момент τ = p × E", size=14, bold=True))

    # Лінії зовнішнього поля E_ext (горизонтальні)
    for y_line in [120, 170, 220, 270, 320]:
        f.append(arrow(40, y_line, 340, y_line, color="#93c5fd", sw=1.5))
    f.append(text(330, 110, "E_зовн", size=12, bold=True, color="#2563eb"))

    # Диполь під кутом θ
    x_center, y_center = 190, 220
    dx, dy = 60, 45
    x_pos, y_pos = x_center + dx, y_center - dy
    x_neg, y_neg = x_center - dx, y_center + dy

    # Вектор p
    f.append(arrow(x_neg, y_neg, x_pos, y_pos, color=FIELD, sw=2.5))
    f.append(text(x_center - 15, y_center - 15, "p", size=14, bold=True, color=FIELD, italic=True))

    # Заряди
    f.append(circle(x_pos, y_pos, 12, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(x_pos, y_pos + 4, "+q", size=11, bold=True, color=POS))

    f.append(circle(x_neg, y_neg, 12, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(x_neg, y_neg + 4, "−q", size=11, bold=True, color=NEG))

    # Сили F_+ та F_-
    f.append(arrow(x_pos, y_pos, x_pos + 60, y_pos, color=POS, sw=2.2))
    f.append(text(x_pos + 20, y_pos - 10, "F₊ = q·E", size=11, bold=True, color=POS))

    f.append(arrow(x_neg, y_neg, x_neg - 60, y_neg, color=NEG, sw=2.2))
    f.append(text(x_neg - 50, y_neg + 20, "F₋ = −q·E", size=11, bold=True, color=NEG))

    # Дуга кута θ
    f.append(line(x_neg, y_neg, x_neg + 80, y_neg, color=MUTED, sw=1, dash="2,2"))
    f.append('<path d="M 160,242 A 30,30 0 0,0 172,233" fill="none" stroke="#2563eb" stroke-width="1.8"/>')
    f.append(text(175, 252, "θ", size=13, bold=True, color="#2563eb"))

    # Права панель: Графік енергії U(θ)
    f.append(rect(395, 50, 345, 340, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(567, 75, "Енергія U(θ) = −p·E·cos θ", size=14, bold=True))

    # Осі графика
    gx0, gy0 = 430, 220
    f.append(line(gx0, 330, gx0, 110, color=INK, sw=1.5))  # U
    f.append(line(gx0, gy0, 710, gy0, color=INK, sw=1.5))  # θ

    f.append(text(gx0 - 15, 120, "U", size=13, bold=True))
    f.append(text(710, gy0 + 20, "θ", size=13, bold=True))

    # Пунктири +pE та -pE
    f.append(line(gx0, 140, 690, 140, color=MUTED, sw=1, dash="3,3"))
    f.append(text(gx0 - 25, 145, "+pE", size=11, color=MUTED))

    f.append(line(gx0, 300, 690, 300, color=MUTED, sw=1, dash="3,3"))
    f.append(text(gx0 - 25, 305, "−pE", size=11, color=MUTED))

    # Крива косинусоїди U(θ) від 0 до π
    f.append('<path d="M 430,300 C 490,300 510,140 690,140" fill="none" stroke="#dc2626" stroke-width="2.5"/>')

    # Позначки точок рівноваги
    f.append(circle(430, 300, 5, fill="#16a34a", stroke="none"))
    f.append(text(430, 320, "θ=0 (стійка)", size=11, color="#16a34a", bold=True))

    f.append(circle(690, 140, 5, fill="#dc2626", stroke="none"))
    f.append(text(670, 125, "θ=π (нестійка)", size=11, color="#dc2626", bold=True))

    return render(os.path.join(IMG, "dipole-torque-energy.svg"), W, H, *f)


def fig_dielectric_polarization():
    """Фігура 4: Поляризація діелектрика у зовнішньому полі: орієнтація диполів."""
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Орієнтаційна поляризація діелектрика у зовнішньому полі", size=16, bold=True))

    # Лівий блок: Без поля (E = 0)
    f.append(rect(20, 50, 350, 300, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(195, 75, "Без зовнішнього поля (E₀ = 0)", size=14, bold=True))

    # Хаотичні диполі
    dipoles_unpolarized = [
        (80, 130, 30), (160, 120, 140), (260, 140, 210), (310, 110, 80),
        (100, 200, 290), (190, 210, 45), (280, 220, 170),
        (90, 280, 110), (180, 290, 250), (290, 280, 15)
    ]

    import math
    for x, y, angle_deg in dipoles_unpolarized:
        rad = math.radians(angle_deg)
        length = 24
        dx = length * math.cos(rad)
        dy = length * math.sin(rad)
        f.append(line(x - dx, y - dy, x + dx, y + dy, color=MUTED, sw=1.5))
        f.append(circle(x + dx, y + dy, 4, fill=POS, stroke='none'))
        f.append(circle(x - dx, y - dy, 4, fill=NEG, stroke='none'))

    tb_left, _, _ = textbox(195, 320, "Хаотичний тепловий рух:\nСумарний момент P = ∑pᵢ = 0", size=11, pad=8, fill="#ffffff", stroke=MUTED, sw=1)
    f.append(tb_left)

    # Правий блок: У полі (E > 0)
    f.append(rect(390, 50, 350, 300, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(565, 75, "У зовнішньому полі E₀ > 0", size=14, bold=True))

    # Стрілки зовнішнього поля
    for y_e in [105, 175, 245]:
        f.append(arrow(410, y_e, 720, y_e, color="#93c5fd", sw=1.2))

    # Впорядковані диполі (переважно вздовж E₀)
    dipoles_polarized = [
        (450, 130, 15), (540, 120, -10), (640, 140, 5),
        (460, 200, -5), (550, 210, 10), (650, 200, -15),
        (450, 270, 20), (540, 280, 0), (630, 270, 10)
    ]

    for x, y, angle_deg in dipoles_polarized:
        rad = math.radians(angle_deg)
        length = 24
        dx = length * math.cos(rad)
        dy = length * math.sin(rad)
        f.append(line(x - dx, y - dy, x + dx, y + dy, color=INK, sw=1.8))
        f.append(circle(x + dx, y + dy, 4, fill=POS, stroke='none'))
        f.append(circle(x - dx, y - dy, 4, fill=NEG, stroke='none'))

    tb_right, _, _ = textbox(565, 320, "Переважна орієнтація диполів:\nВектор поляризації P = N·⟨p⟩ > 0", size=11, pad=8, fill="#ffffff", stroke="#2563eb", sw=1.2)
    f.append(tb_right)

    return render(os.path.join(IMG, "dielectric-polarization.svg"), W, H, *f)


if __name__ == '__main__':
    fig_dipole_vector_setup()
    fig_dipole_field_lines()
    fig_dipole_torque_energy()
    fig_dielectric_polarization()
    print("Усі фігури успішно згенеровано у ./img/")
