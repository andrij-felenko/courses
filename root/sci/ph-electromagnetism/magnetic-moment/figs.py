# -*- coding: utf-8 -*-
"""Фігури до теми «Магнітний момент».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Струмовий контур та вектор магнітного моменту ──────────────────
def fig_current_loop():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Плоский струмовий контур та вектор магнітного моменту μ = I·S·n", size=16, bold=True))

    # Зліва: Схема контуру
    cx1, cy1 = 220, 200
    rx_loop, ry_loop = 130, 55

    # Малюємо еліпс контуру через path
    f.append('<path d="M %f %f A %f %f 0 1 0 %f %f A %f %f 0 1 0 %f %f" fill="#f4f6f9" stroke="#2b6cb0" stroke-width="2.5"/>' % (
        cx1 - rx_loop, cy1, rx_loop, ry_loop, cx1 + rx_loop, cy1, rx_loop, ry_loop, cx1 - rx_loop, cy1
    ))

    # Напрям струму I (стрілки на контурі)
    f.append(arrow(cx1 + 80, cy1 + 40, cx1 + 20, cy1 + 54, color='#e53e3e', sw=2.5))
    f.append(arrow(cx1 - 60, cy1 - 42, cx1, cy1 - 53, color='#e53e3e', sw=2.5))
    f.append(text(cx1 + 100, cy1 + 55, "Струм I", size=13, bold=True, color='#e53e3e'))

    # Площа S (зафарбування біля центру)
    f.append(text(cx1, cy1 + 15, "Площа контуру S", size=12, bold=True, color='#4a5568'))

    # Вектор нормалі n та магнітного моменту μ (вгору)
    f.append(arrow(cx1, cy1, cx1, cy1 - 130, color='#2b6cb0', sw=3))
    f.append(text(cx1 + 15, cy1 - 110, "μ = I · S · n", size=15, bold=True, color='#2b6cb0'))
    f.append(text(cx1 + 15, cy1 - 85, "n — одинична нормаль", size=11, color='#4a5568'))

    # Пунктирний продовження вниз
    f.append(line(cx1, cy1, cx1, cy1 + 70, color='#cbd5e1', sw=1.5, dash='4,4'))

    # Справа: Правило правої руки
    cx2, cy2 = 540, 190
    f.append(rect(cx2 - 130, cy2 - 120, 260, 240, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=8))
    f.append(text(cx2, cy2 - 95, "Правило правої руки", size=14, bold=True, color=INK))

    # Схематичний візерунок руки / пальців
    f.append(text(cx2, cy2 - 60, "4 пальці → напрям струму I", size=12, color='#e53e3e'))
    f.append(text(cx2, cy2 - 35, "Великий палець → напрям моменту μ", size=12, color='#2b6cb0'))

    # Опис властивостей
    props = [
        "• μ не залежить від форми контуру",
        "• Модуль |μ| = I · S  [А·м²]",
        "• Вектор μ перпендикулярний до площини",
        "• Створення поля B на відстані"
    ]
    for i, p in enumerate(props):
        f.append(text(cx2 - 110, cy2 + 10 + i * 24, p, size=11, color='#2d3748', anchor='start'))

    b_bot, _, _ = textbox(W / 2, H - 20, "Магнітний момент μ повністю визначає дипольне магнітне поле контуру на великих відстанях", size=11, pad=6, fill='#eef6ef', stroke=FIELD, sw=1.2)
    f.append(b_bot)

    return render(os.path.join(IMG, "current-loop-moment.svg"), W, H, *f)


# ── Фігура 2: Обертальний момент та потенціальна енергія диполя ──────────────
def fig_torque_energy():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Магнітний диполь у зовнішньому полі B: обертальний момент та енергія", size=16, bold=True))

    # Зліва: Обертальний момент τ = μ × B
    cx1, cy1 = 220, 180

    # Поле B (паралельні сині стрілки вправо)
    for y in range(cy1 - 100, cy1 + 110, 35):
        f.append(arrow(cx1 - 140, y, cx1 + 140, y, color='#3182ce', sw=1.8))
    f.append(text(cx1 + 110, cy1 - 110, "Поле B", size=13, bold=True, color='#3182ce'))

    # Диполь (повернута рамка під кутом 40 градусів)
    angle = math.radians(40)
    dx = 70 * math.cos(angle)
    dy = 70 * math.sin(angle)

    # Вектор μ під кутом
    f.append(arrow(cx1, cy1, cx1 + dx, cy1 - dy, color='#e53e3e', sw=3))
    f.append(text(cx1 + dx + 10, cy1 - dy, "μ", size=14, bold=True, color='#e53e3e'))

    # Кут θ між μ та B
    f.append(line(cx1, cy1, cx1 + 60, cy1, color='#718096', sw=1, dash='3,3'))
    f.append(text(cx1 + 45, cy1 - 12, "θ", size=13, bold=True, color='#2d3748'))

    # Стрілка обертання τ (дуга за годинниковою стрілкою)
    f.append(arrow(cx1 + 35, cy1 - 45, cx1 + 50, cy1 - 15, color='#d69e2e', sw=2.5))
    f.append(text(cx1 - 60, cy1 - 60, "Момент τ = μ × B", size=13, bold=True, color='#b7791f'))

    # Справа: Енергетичні рівні U = -μ·B cos θ
    cx2 = 540
    f.append(rect(cx2 - 130, 70, 260, 220, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=8))
    f.append(text(cx2, 95, "Потенціальна енергія U(θ)", size=14, bold=True, color=INK))

    states = [
        ("θ = 0° (паралельно)", "U = − μ · B  [мінімум, стійкий]", "#2b6cb0", 130),
        ("θ = 90° (перпендикулярно)", "U = 0", "#4a5568", 175),
        ("θ = 180° (антипаралельно)", "U = + μ · B  [максимум, нестійкий]", "#e53e3e", 220)
    ]
    for title, formula, col, y_pos in states:
        f.append(text(cx2 - 110, y_pos, title, size=11, bold=True, color=col, anchor='start'))
        f.append(text(cx2 - 110, y_pos + 16, formula, size=11, color='#2d3748', anchor='start'))

    b_bot, _, _ = textbox(W / 2, H - 20, "Зовнішнє поле намагається повернути магнітний момент паралельно до векторів B (мінімум енергії)", size=11, pad=6, fill='#eef6ef', stroke=FIELD, sw=1.2)
    f.append(b_bot)

    return render(os.path.join(IMG, "torque-energy-dipole.svg"), W, H, *f)


# ── Фігура 3: Сила в неоднорідному магнітному полі ───────────────────────────
def fig_gradient_force():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Диполь у неоднорідному полі: сила F = ∇(μ · B)", size=16, bold=True))

    # Зліва: Паралельний диполь (притягується)
    cx1, cy1 = 200, 180
    f.append(text(cx1, 55, "Орієнтація паралельно полю (μ ↑, ∇B ↑)", size=12, bold=True, color='#2b6cb0'))

    # Силові лінії, що збігаються догори (неоднорідне поле)
    for offset in [-60, -30, 0, 30, 60]:
        x1 = cx1 + offset * 1.6
        x2 = cx1 + offset * 0.5
        f.append(arrow(x1, cy1 + 90, x2, cy1 - 90, color='#3182ce', sw=1.5))
    f.append(text(cx1 + 80, cy1 - 70, "Густе поле B", size=10, color='#3182ce'))

    # Диполь μ вгору
    f.append(arrow(cx1, cy1 + 25, cx1, cy1 - 45, color='#e53e3e', sw=3))
    f.append(text(cx1 + 12, cy1 - 10, "μ", size=14, bold=True, color='#e53e3e'))

    # Результуюча сила F вгору (у бік сильнішого поля)
    f.append(arrow(cx1 - 45, cy1, cx1 - 45, cy1 - 65, color='#2b6cb0', sw=3.5))
    f.append(text(cx1 - 95, cy1 - 35, "Сила F > 0", size=12, bold=True, color='#2b6cb0'))

    # Розділювальна лінія
    f.append(line(W / 2, 50, W / 2, H - 45, color='#cbd5e1', sw=1.5, dash='4,4'))

    # Справа: Антипаралельний диполь (відштовхується)
    cx2, cy2 = 540, 180
    f.append(text(cx2, 55, "Орієнтація проти поля (μ ↓, ∇B ↑)", size=12, bold=True, color='#e53e3e'))

    # Силові лінії поля
    for offset in [-60, -30, 0, 30, 60]:
        x1 = cx2 + offset * 1.6
        x2 = cx2 + offset * 0.5
        f.append(arrow(x1, cy2 + 90, x2, cy2 - 90, color='#3182ce', sw=1.5))

    # Диполь μ вниз
    f.append(arrow(cx2, cy2 - 45, cx2, cy2 + 25, color='#e53e3e', sw=3))
    f.append(text(cx2 + 12, cy2 - 10, "μ", size=14, bold=True, color='#e53e3e'))

    # Результуюча сила F вниз (у бік слабшого поля)
    f.append(arrow(cx2 + 45, cy2, cx2 + 45, cy2 + 65, color='#e53e3e', sw=3.5))
    f.append(text(cx2 + 55, cy2 + 35, "Сила F < 0", size=12, bold=True, color='#e53e3e'))

    b_bot, _, _ = textbox(W / 2, H - 20, "У неоднорідному полі диполь втягується в область сильнішого поля (якщо μ || B) або виштовхується (якщо μ anti-|| B)", size=11, pad=6, fill='#eef6ef', stroke=FIELD, sw=1.2)
    f.append(b_bot)

    return render(os.path.join(IMG, "gradient-force-dipole.svg"), W, H, *f)


# ── Фігура 4: Орбітальний та спіновий магнітні моменти електрона ──────────────
def fig_electron_spin():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Орбітальний та спіновий магнітні моменти електрона", size=16, bold=True))

    # Зліва: Орбітальний момент μ_L
    cx1, cy1 = 200, 190
    f.append(text(cx1, 55, "Орбітальний рух (g_L = 1)", size=13, bold=True, color='#2b6cb0'))

    # Ядро в центрі
    f.append(circle(cx1, cy1, 10, fill='#e53e3e', stroke='none'))
    f.append(text(cx1, cy1 + 3, "+e", size=10, bold=True, color='#ffffff'))

    # Орбіта електрона через path
    f.append('<path d="M %f %f A 75 35 0 1 0 %f %f A 75 35 0 1 0 %f %f" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4,4"/>' % (
        cx1 - 75, cy1, cx1 + 75, cy1, cx1 - 75, cy1
    ))

    # Електрон на орбіті
    ex, ey = cx1 + 75, cy1
    f.append(circle(ex, ey, 7, fill='#3182ce', stroke='none'))
    f.append(text(ex, ey + 3, "−e", size=9, bold=True, color='#ffffff'))

    # Швидкість v (вгору) та Момент імпульсу L (вгору)
    f.append(arrow(ex, ey, ex, ey - 45, color='#718096', sw=2))
    f.append(text(ex + 10, ey - 30, "v", size=11, color='#718096'))

    # Момент L (вгору від центра)
    f.append(arrow(cx1, cy1, cx1, cy1 - 90, color='#2b6cb0', sw=2.5))
    f.append(text(cx1 + 12, cy1 - 75, "L", size=13, bold=True, color='#2b6cb0', anchor='start'))

    # Магнітний момент μ_L (вниз, бо знак заряду мінус!)
    f.append(arrow(cx1, cy1, cx1, cy1 + 90, color='#e53e3e', sw=2.5))
    f.append(text(cx1 + 12, cy1 + 75, "μ_L = − (e / 2m_e) L", size=12, bold=True, color='#e53e3e', anchor='start'))

    # Справа: Спіновий момент μ_S
    cx2, cy2 = 540, 190
    f.append(text(cx2, 55, "Власний спін електрона (g_S ≈ 2)", size=13, bold=True, color='#805ad5'))

    # Сфера електрона (спін)
    f.append(circle(cx2, cy2, 35, fill='#ebf8ff', stroke='#3182ce', sw=2))
    f.append(text(cx2, cy2 + 4, "−e", size=12, bold=True, color='#2b6cb0'))

    # Власний момент S (вгору)
    f.append(arrow(cx2, cy2, cx2, cy2 - 95, color='#805ad5', sw=2.5))
    f.append(text(cx2 + 12, cy2 - 75, "S = ½ ℏ", size=13, bold=True, color='#805ad5', anchor='start'))

    # Спіновий магнітний момент μ_S (вниз, подвоєне гіромагнітне відношення)
    f.append(arrow(cx2, cy2, cx2, cy2 + 95, color='#e53e3e', sw=2.5))
    f.append(text(cx2 + 12, cy2 + 75, "μ_S = − g_S (e / 2m_e) S", size=12, bold=True, color='#e53e3e', anchor='start'))

    # Магнетон Бора в рамці
    f.append(text(cx2 + 80, cy2 - 20, "μ_B = e·ℏ / (2m_e)", size=11, bold=True, color='#2d3748', anchor='start'))
    f.append(text(cx2 + 80, cy2 + 5, "≈ 9.274 × 10⁻²⁴ Дж/Тл", size=10, color='#4a5568', anchor='start'))

    b_bot, _, _ = textbox(W / 2, H - 20, "Через негативний заряд електрона магнітні моменти μ_L та μ_S направлені протилежно до моментів імпульсу L та S", size=11, pad=6, fill='#eef6ef', stroke=FIELD, sw=1.2)
    f.append(b_bot)

    return render(os.path.join(IMG, "electron-orbital-spin.svg"), W, H, *f)


if __name__ == '__main__':
    fig_current_loop()
    fig_torque_energy()
    fig_gradient_force()
    fig_electron_spin()
    print("Всі SVG успішно згенеровано у ./img/")
