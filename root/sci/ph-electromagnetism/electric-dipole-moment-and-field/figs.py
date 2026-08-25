# -*- coding: utf-8 -*-
"""Фігури до теми «Електричний диполь».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_dipole_geometry():
    """Фігура 1: Геометрія електричного диполя та системи координат."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Геометрія точкового електричного диполя", size=16, bold=True))

    # Рамка для схеми
    f.append(rect(20, 48, W - 40, H - 74, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    cx, cy = 250, 230

    # Вісь z
    f.append(line(cx, 390, cx, 80, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx + 12, 90, "вісь z", size=12, color=MUTED, anchor="start"))

    # Заряди на осі z
    dy = 65
    y_neg = cy + dy
    y_pos = cy - dy

    # Плече d
    f.append(arrow(cx, y_neg, cx, y_pos, color=FIELD, sw=2.5))
    f.append(text(cx - 24, cy + 4, "d", size=14, bold=True, color=FIELD, italic=True))

    # Кружки зарядів
    f.append(circle(cx, y_neg, 15, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(cx, y_neg + 5, "−q", size=14, bold=True, color=NEG))

    f.append(circle(cx, y_pos, 15, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(cx, y_pos + 5, "+q", size=14, bold=True, color=POS))

    # Точка P
    px, py = 520, 110
    f.append(circle(px, py, 6, fill=INK, stroke='none'))
    f.append(text(px + 14, py - 6, "P(r, θ)", size=14, bold=True, anchor="start"))

    # Радіус-вектор r
    f.append(arrow(cx, cy, px, py, color=INK, sw=2))
    f.append(text(380, 160, "r", size=14, bold=True, color=INK, italic=True))

    # r_+ та r_-
    f.append(line(cx, y_pos, px, py, color=POS, sw=1.5, dash="3,3"))
    f.append(text(400, 85, "r₊", size=13, bold=True, color=POS))

    f.append(line(cx, y_neg, px, py, color=NEG, sw=1.5, dash="3,3"))
    f.append(text(410, 240, "r₋", size=13, bold=True, color=NEG))

    # Кут theta
    f.append('<path d="M 250,170 A 60,60 0 0,1 285,185" fill="none" stroke="#2563eb" stroke-width="1.8"/>')
    f.append(text(278, 166, "θ", size=14, bold=True, color="#2563eb", italic=True))

    # Вектор дипольного моменту p
    f.append(arrow(cx - 65, y_neg, cx - 65, y_pos, color="#059669", sw=3))
    f.append(text(cx - 88, cy + 4, "p = q·d", size=13, bold=True, color="#059669"))

    # Формульний блок
    tb, _, _ = textbox(570, 275,
                       "Формули дипольного поля (r » d):\n\n"
                       "Потенціал:\n"
                       "Φ(r, θ) = (1 / 4πε₀) · (p · cos θ / r²)\n\n"
                       "Радіальна напруженість:\n"
                       "E_r = (1 / 4πε₀) · (2p cos θ / r³)\n\n"
                       "Тангенціальна напруженість:\n"
                       "E_θ = (1 / 4πε₀) · (p sin θ / r³)",
                       size=11, pad=10, fill="#ffffff", stroke="#93c5fd", sw=1.5)
    f.append(tb)

    return render(os.path.join(IMG, "dipole-geometry.svg"), W, H, *f)


def fig_dipole_torque():
    """Фігура 2: Диполь у зовнішньому однорідному електричному полі (обертальний момент)."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Диполь у зовнішньому однорідному електричному полі", size=16, bold=True))
    f.append(rect(20, 48, W - 40, H - 74, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Лінії зовнішнього поля E (горизонтальні, не заходять під текстовий блок)
    for y in range(90, 390, 50):
        f.append(arrow(50, y, 460, y, color="#86efac", sw=1.8))
    f.append(text(450, 80, "E", size=16, bold=True, color=FIELD))

    # Диполь під кутом theta = 45 deg
    cx, cy = 340, 230
    length = 100
    angle_rad = math.radians(45)
    dx = length * math.cos(angle_rad)
    dy = length * math.sin(angle_rad)

    x_pos, y_pos = cx + dx / 2, cy - dy / 2
    x_neg, y_neg = cx - dx / 2, cy + dy / 2

    # Плече d
    f.append(line(x_neg, y_neg, x_pos, y_pos, color=MUTED, sw=2, dash="4,4"))

    # Заряди
    f.append(circle(x_neg, y_neg, 14, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(x_neg, y_neg + 4, "−q", size=13, bold=True, color=NEG))

    f.append(circle(x_pos, y_pos, 14, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(x_pos, y_pos + 4, "+q", size=13, bold=True, color=POS))

    # Вектор p
    f.append(arrow(x_neg + 12 * math.cos(angle_rad), y_neg - 12 * math.sin(angle_rad),
                   x_pos - 12 * math.cos(angle_rad), y_pos + 12 * math.sin(angle_rad),
                   color="#059669", sw=2.5))
    f.append(text(cx - 20, cy - 15, "p", size=14, bold=True, color="#059669", italic=True))

    # Сила F+ праворуч
    f.append(arrow(x_pos, y_pos, x_pos + 80, y_pos, color=POS, sw=2.5))
    f.append(text(x_pos + 45, y_pos - 10, "F₊ = q·E", size=12, bold=True, color=POS))

    # Сила F- ліворуч
    f.append(arrow(x_neg, y_neg, x_neg - 80, y_neg, color=NEG, sw=2.5))
    f.append(text(x_neg - 50, y_neg + 20, "F₋ = −q·E", size=12, bold=True, color=NEG))

    # Пунктирна лінія від осі для кута theta
    f.append(line(cx, cy, cx + 80, cy, color=MUTED, sw=1, dash="3,3"))
    f.append('<path d="M 390,230 A 50,50 0 0,0 375,195" fill="none" stroke="#2563eb" stroke-width="1.8"/>')
    f.append(text(395, 215, "θ", size=14, bold=True, color="#2563eb"))

    # Блок динаміки
    tb, _, _ = textbox(570, 310,
                       "Рівновага та енергія:\n\n"
                       "Результуюча сила:\n"
                       "F_net = F₊ + F₋ = 0\n\n"
                       "Обертальний момент:\n"
                       "τ = p × E  =>  τ = p·E·sin θ\n\n"
                       "Потенціальна енергія:\n"
                       "U(θ) = −p · E = −p·E·cos θ\n\n"
                       "Мінімум U при θ = 0 (стійкий)",
                       size=11, pad=10, fill="#ffffff", stroke="#93c5fd", sw=1.5)
    f.append(tb)

    return render(os.path.join(IMG, "dipole-torque.svg"), W, H, *f)


def fig_dipole_force():
    """Фігура 3: Диполь у неоднорідному електричному полі (результуюча сила)."""
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Втягування диполя в область сильнішого поля", size=16, bold=True))
    f.append(rect(20, 48, W - 40, H - 74, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Сбіжні лінії поля E (неоднорідне поле, згущується праворуч)
    lines_y = [
        "M 60,80 C 300,140 500,190 700,210",
        "M 60,150 C 300,180 500,210 700,220",
        "M 60,230 C 300,230 500,230 700,230",
        "M 60,310 C 300,280 500,250 700,240",
        "M 60,380 C 300,320 500,270 700,250"
    ]
    for d in lines_y:
        f.append('<path d="%s" fill="none" stroke="#86efac" stroke-width="1.8"/>' % d)
    f.append(arrow(680, 250, 710, 250, color=FIELD, sw=2))
    f.append(text(660, 195, "∇|E| (градієнт поля)", size=12, bold=True, color=FIELD))

    # Диполь, зорієнтований за полем (горизонтально)
    x_neg, y_neg = 240, 230
    x_pos, y_pos = 360, 230

    f.append(line(x_neg, y_neg, x_pos, y_pos, color=MUTED, sw=2, dash="3,3"))

    f.append(circle(x_neg, y_neg, 14, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(x_neg, y_neg + 4, "−q", size=13, bold=True, color=NEG))

    f.append(circle(x_pos, y_pos, 14, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(x_pos, y_pos + 4, "+q", size=13, bold=True, color=POS))

    # Вектор p
    f.append(arrow(x_neg + 14, y_neg, x_pos - 14, y_pos, color="#059669", sw=2.5))
    f.append(text(300, 215, "p", size=14, bold=True, color="#059669", italic=True))

    # Сили: F+ праворуч (велика, бо поле сильніше), F- ліворуч (менша, бо поле слабше)
    f.append(arrow(x_pos, y_pos, x_pos + 110, y_pos, color=POS, sw=3))
    f.append(text(x_pos + 55, y_pos - 12, "F₊ = q·E(r₊) [більша]", size=11, bold=True, color=POS))

    f.append(arrow(x_neg, y_neg, x_neg - 60, y_neg, color=NEG, sw=2))
    f.append(text(x_neg - 35, y_neg + 20, "F₋ = −q·E(r₋) [менша]", size=11, bold=True, color=NEG))

    # Результуюча сила F_net
    f.append(arrow(300, 310, 420, 310, color=INK, sw=3.5))
    f.append(text(360, 335, "F_net = (p·∇)E > 0", size=13, bold=True, color=INK))

    # Текстовий блок
    tb, _, _ = textbox(570, 325,
                       "Принцип діелектрофорезу:\n\n"
                       "1. Однорідне поле: F_net = 0\n"
                       "2. Неоднорідне поле:\n"
                       "   |F₊| > |F₋|, бо E(r₊) > E(r₋)\n"
                       "3. Результуюча сила:\n"
                       "   F = (p · ∇) E\n\n"
                       "Нейтральне полярне тіло\n"
                       "ВТЯГУЄТЬСЯ в сильне поле!",
                       size=11, pad=10, fill="#ffffff", stroke="#93c5fd", sw=1.5)
    f.append(tb)

    return render(os.path.join(IMG, "dipole-force.svg"), W, H, *f)


def fig_dipole_fieldlines():
    """Фігура 4: Силові лінії та еквіпотенціальні поверхні диполя."""
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Картина силових ліній та еквіпотенціалей диполя", size=16, bold=True))
    f.append(rect(20, 46, W - 40, H - 70, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    cx, cy = 340, 230
    dy = 60

    # Еквіпотенціальні кола / овали (ортогональні до ліній)
    f.append('<circle cx="%.1f" cy="%.1f" r="40" fill="none" stroke="#fca5a5" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy - dy))
    f.append('<circle cx="%.1f" cy="%.1f" r="75" fill="none" stroke="#fca5a5" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy - dy))
    f.append('<circle cx="%.1f" cy="%.1f" r="115" fill="none" stroke="#fca5a5" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy - dy))

    f.append('<circle cx="%.1f" cy="%.1f" r="40" fill="none" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy + dy))
    f.append('<circle cx="%.1f" cy="%.1f" r="75" fill="none" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy + dy))
    f.append('<circle cx="%.1f" cy="%.1f" r="115" fill="none" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy + dy))

    # Нульова еквіпотенціаль (площина симетрії)
    f.append(line(50, cy, 630, cy, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(580, cy - 8, "Φ = 0 (площина симетрії)", size=11, color=MUTED))

    # Силові лінії
    curves = [
        "M 340,170 C 260,170 260,290 340,290",
        "M 340,170 C 420,170 420,290 340,290",
        "M 340,170 C 180,140 180,320 340,290",
        "M 340,170 C 500,140 500,320 340,290",
        "M 340,170 C 100,90 100,370 340,290",
        "M 340,170 C 580,90 580,370 340,290",
    ]
    for c in curves:
        f.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="1.8"/>' % c)

    # Стрілки напрямку поля на силових лініях
    f.append(arrow(260, 230, 260, 235, color="#2563eb", sw=2))
    f.append(arrow(420, 230, 420, 235, color="#2563eb", sw=2))
    f.append(arrow(180, 230, 180, 235, color="#2563eb", sw=2))
    f.append(arrow(500, 230, 500, 235, color="#2563eb", sw=2))

    # Заряди
    f.append(circle(cx, cy - dy, 15, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(cx, cy - dy + 5, "+q", size=14, bold=True, color=POS))

    f.append(circle(cx, cy + dy, 15, fill="#eff6ff", stroke=NEG, sw=2))
    f.append(text(cx, cy + dy + 5, "−q", size=14, bold=True, color=NEG))

    # Легенда
    f.append(rect(580, 60, 140, 110, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    f.append(line(590, 80, 620, 80, color="#2563eb", sw=2))
    f.append(text(630, 84, "Силові лінії E", size=11, anchor="start"))
    f.append(line(590, 110, 620, 110, color="#fca5a5", sw=1.5, dash="3,3"))
    f.append(text(630, 114, "Еквіпотенціалі Φ > 0", size=11, anchor="start"))
    f.append(line(590, 140, 620, 140, color="#93c5fd", sw=1.5, dash="3,3"))
    f.append(text(630, 144, "Еквіпотенціалі Φ < 0", size=11, anchor="start"))

    return render(os.path.join(IMG, "dipole-fieldlines.svg"), W, H, *f)


if __name__ == '__main__':
    fig_dipole_geometry()
    fig_dipole_torque()
    fig_dipole_force()
    fig_dipole_fieldlines()
    print("Успішно згенеровано 4 фігури в ./img/")
