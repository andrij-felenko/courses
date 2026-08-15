# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Дарсі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольорова палітра для гідродинаміки пористих середовищ
WATER = "#2457d6"   # Потік води / флюїду
SAND  = "#d35400"   # Пористе середовище / пісок / порода
PRESS = "#c0392b"   # Високий тиск / напір
FLOW  = "#27ae60"   # Вектор швидкості фільтрації
GRAIN = "#7f8c8d"   # Зерна породи / тверді частки
TORT  = "#8e44ad"   # Звивиста траєкторія у порах


def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))


# ── Фігура 1: Оригінальний експеримент Анрі Дарсі (1856) ─────────────────────
def fig_darcy_experiment():
    W, H = 820, 520
    f = [text(W / 2, 28, "Експериментальна установка Анрі Дарсі (1856)", size=16, bold=True)]

    # Вертикальна колона з піском
    cX, cY = 320, 270
    cW, cH = 140, 260
    topY = cY - cH / 2
    botY = cY + cH / 2

    # Вода зверху та знизу колони
    f.append(rect(cX - cW/2, topY - 40, cW, 40, fill="#e8f1fd", stroke=WATER, sw=1.5))
    f.append(text(cX, topY - 20, "вхід води (тиск p₁)", size=12, color=WATER, bold=True))

    # Піщаний шар (шар заввишки L)
    f.append(rect(cX - cW/2, topY, cW, cH, fill="#fbeee6", stroke=SAND, sw=2))
    
    # Текстура зерен піску
    for gx, gy in [
        (cX-40, topY+30), (cX+20, topY+45), (cX-20, topY+80), (cX+45, topY+110),
        (cX-50, topY+150), (cX+10, topY+170), (cX-30, topY+210), (cX+30, topY+230)
    ]:
        f.append(circle(gx, gy, 8, fill="#e5c7b6", stroke=SAND, sw=1))

    f.append(text(cX, cY, "пористе середовище", size=13, color=SAND, bold=True))
    f.append(text(cX, cY + 20, "(пісок, довжина L)", size=12, color=SAND))

    # Вихід води знизу
    f.append(rect(cX - cW/2, botY, cW, 35, fill="#e8f1fd", stroke=WATER, sw=1.5))
    f.append(text(cX, botY + 20, "вихід води (тиск p₂)", size=12, color=WATER, bold=True))

    # Позначення довжини L
    f.append(line(cX + cW/2 + 25, topY, cX + cW/2 + 25, botY, color=INK, sw=1.5))
    f.append(arrow(cX + cW/2 + 25, topY + 30, cX + cW/2 + 25, topY, color=INK, sw=1.5))
    f.append(arrow(cX + cW/2 + 25, botY - 30, cX + cW/2 + 25, botY, color=INK, sw=1.5))
    f.append(text(cX + cW/2 + 45, cY, "довжина L", size=13, bold=True))

    # П'єзометричні трубки (манометри)
    # Верхня трубка (висота h1)
    p1X = cX - cW/2 - 60
    f.append(line(cX - cW/2, topY + 20, p1X, topY + 20, color=WATER, sw=1.5))
    f.append(rect(p1X - 15, topY - 120, 30, 140, fill="#ffffff", stroke=WATER, sw=1.5))
    f.append(rect(p1X - 14, topY - 80, 28, 100, fill="#c6dbfc", stroke="none"))
    f.append(text(p1X, topY - 95, "напір h₁", size=12, color=WATER, bold=True))

    # Нижня трубка (висота h2)
    p2X = cX - cW/2 - 140
    f.append(line(cX - cW/2, botY - 20, p2X, botY - 20, color=WATER, sw=1.5))
    f.append(rect(p2X - 15, botY - 140, 30, 120, fill="#ffffff", stroke=WATER, sw=1.5))
    f.append(rect(p2X - 14, botY - 60, 28, 40, fill="#c6dbfc", stroke="none"))
    f.append(text(p2X, topY + 65, "напір h₂", size=12, color=WATER, bold=True))

    # Різниця напорів Δh
    f.append(line(p2X - 30, topY - 80, p1X + 30, topY - 80, color=PRESS, sw=1.2, dash="3,3"))
    f.append(line(p2X - 30, botY - 60, p1X + 30, botY - 60, color=PRESS, sw=1.2, dash="3,3"))
    f.append(arrow(p2X - 30, topY - 20, p2X - 30, topY - 80, color=PRESS, sw=1.6))
    f.append(arrow(p2X - 30, topY - 120, p2X - 30, botY - 60, color=PRESS, sw=1.6))
    f.append(text(p2X - 55, topY - 55, "втрата напору", size=12, color=PRESS, bold=True))
    f.append(text(p2X - 55, topY - 38, "Δh = h₁ − h₂", size=12, color=PRESS))

    # Потік води Q на виході
    f.append(arrow(cX, botY + 35, cX, botY + 85, color=FLOW, sw=3))
    f.append(text(cX + 80, botY + 65, "об'ємна витрата Q ∝ A · (Δh / L)", size=13, color=FLOW, bold=True))

    # Текстова панель із формулою закону Дарсі
    box_content = "Закон Дарсі: Q = K · A · (Δh / L)\nK — коефіцієнт фільтрації (м/с), A — площа перерізу колони (м²)"
    f.append(fitbox(460, 420, 330, 65, box_content, size=12.5, fill="#f4f8f5", stroke=FLOW, sw=1.5))

    render(os.path.join(IMG, "darcy-experiment.svg"), W, H, *f)


# ── Фігура 2: Мікроструктура пористого середовища та REV ──────────────────────
def fig_pore_microscope():
    W, H = 840, 480
    f = [text(W / 2, 28, "Перехід від мікроструктури пор до макроскопічного об'єму (REV)", size=16, bold=True)]

    # Ліва частина: Мікроскопічний вигляд пор та зернистої матриці
    leftX, leftY, leftW, leftH = 40, 60, 360, 360
    f.append(rect(leftX, leftY, leftW, leftH, fill="#fdfefe", stroke=GRAIN, sw=1.5, rx=8))
    f.append(text(leftX + leftW/2, leftY + 25, "Мікрорівень: звивисті порові канали", size=13, color=INK, bold=True))

    # Хаотично розміщені зерна породи
    grains = [
        (100, 140, 35), (180, 130, 40), (280, 150, 42),
        (80, 230, 38), (170, 240, 45), (270, 230, 36),
        (110, 320, 40), (200, 330, 38), (300, 310, 44)
    ]
    for gx, gy, gr in grains:
        f.append(circle(gx, gy, gr, fill="#d5dbdb", stroke=GRAIN, sw=1.5))

    # Реальна звивиста траєкторія частинки флюїду
    tortuous_path = "M 50,180 Q 90,190 120,180 T 140,190 T 220,180 T 230,280 T 310,240 T 360,250"
    f.append(path(tortuous_path, fill="none", stroke=TORT, sw=2.5, dash="4,3"))
    f.append(text(190, 200, "порова швидкість vₚ = vⲇ / ϕ", size=12, color=TORT, bold=True))

    # Прямий вектор фільтрації Дарсі
    f.append(arrow(60, 380, 340, 380, color=FLOW, sw=2.5))
    f.append(text(200, 405, "фіктивна швидкість Дарсі vⲇ = Q / A", size=12, color=FLOW, bold=True))

    # Стрілка переходу REV
    f.append(arrow(415, 240, 465, 240, color=INK, sw=2.5))
    f.append(text(440, 220, "усереднення", size=11, color=MUTED))
    f.append(text(440, 260, "по REV", size=11, color=MUTED))

    # Права частина: Макроскопічний елемент REV
    rightX, rightY, rightW, rightH = 480, 60, 320, 360
    f.append(rect(rightX, rightY, rightW, rightH, fill="#fbeee6", stroke=SAND, sw=1.5, rx=8))
    f.append(text(rightX + rightW/2, rightY + 25, "Макрорівень: суцільне середовище", size=13, color=SAND, bold=True))

    # Суцільне середовище з ефективними параметрами
    f.append(fitbox(rightX + rightW/2, rightY + 90, 260, 50,
                    "Пористість: ϕ = Vₚₒᵣₑ / Vₜⲱₜⲱₗ\nПроникність: k (м² або Дарсі)",
                    size=12, fill="none", stroke="none"))

    # Потік крізь переріз A
    f.append(rect(rightX + 25, rightY + 160, 15, 120, fill="#2457d6", stroke="none"))
    f.append(text(rightX + 32, rightY + 300, "площа A", size=12, color=WATER, bold=True))

    f.append(arrow(rightX + 55, rightY + 220, rightX + 260, rightY + 220, color=FLOW, sw=3))
    f.append(text(rightX + 160, rightY + 205, "потік vⲇ = − (k / μ) ∇p", size=13, color=FLOW, bold=True))

    box_rev = "REV (Representative Elementary Volume) — найменший об'єм,\nу якому мікроскопічна хаотичність пор згладжується\nу стабільні макроскопічні характеристики k та ϕ."
    f.append(fitbox(W/2, 445, 680, 50, box_rev, size=11.5, fill="#f4f6f8", stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "pore-microscope.svg"), W, H, *f)


# ── Фігура 3: Градієнт гідравлічного напору та тиску ─────────────────────────
def fig_hydraulic_gradient():
    W, H = 800, 440
    f = [text(W / 2, 28, "Градієнт тиску, гравітація та вектор швидкості фільтрації", size=16, bold=True)]

    # Похилий пористий пласт
    x1, y1 = 120, 160
    x2, y2 = 640, 320

    # Шари пласта
    f.append(path(f"M {x1},{y1} L {x2},{y2} L {x2},{y2+80} L {x1},{y1+80} Z", fill="#f9ebea", stroke=SAND, sw=2))
    f.append(text(240, 210, "пористий пласт (проникність k)", size=13, color=SAND, bold=True))

    # Вектор тиску p1 та p2
    f.append(circle(x1, y1+40, 6, fill=PRESS, stroke=PRESS, sw=1))
    f.append(text(x1 - 40, y1 + 35, "тиск p₁", size=12, color=PRESS, bold=True))
    f.append(text(x1 - 40, y1 + 55, "висота z₁", size=12, color=MUTED))

    f.append(circle(x2, y2+40, 6, fill=WATER, stroke=WATER, sw=1))
    f.append(text(x2 + 45, y2 + 35, "тиск p₂", size=12, color=WATER, bold=True))
    f.append(text(x2 + 45, y2 + 55, "висота z₂", size=12, color=MUTED))

    # Вектор швидкості фільтрації v_d вздовж пласта
    f.append(arrow(x1 + 60, y1 + 40, x2 - 60, y2 + 40, color=FLOW, sw=3.5))
    f.append(text(460, 220, "вектор швидкості фільтрації vⲇ", size=13, color=FLOW, bold=True))

    # Сили: градієнт тиску ∇p та гравітація ρg
    f.append(arrow(340, 240, 420, 267, color=PRESS, sw=2))
    f.append(text(430, 255, "−∇p", size=12, color=PRESS, bold=True))

    f.append(arrow(340, 240, 340, 310, color=INK, sw=2))
    f.append(text(340, 330, "ρ g (гравітація)", size=12, color=INK, bold=True))

    # Загальне рівняння Дарсі з урахуванням сили тяжіння
    eq_box = "Повна форма закону Дарсі для стисливого/нестисливого флюїду під дією гравітації:\n" \
             "vⲇ = − (k / μ) · (∇p − ρ g)"
    f.append(fitbox(W/2, 395, 660, 50, eq_box, size=12.5, fill="#f4f8f5", stroke=FLOW, sw=1.5))

    render(os.path.join(IMG, "hydraulic-gradient.svg"), W, H, *f)


# ── Фігура 4: Межі застосовності та нелінійний режим Форхгеймера ─────────────
def fig_forchheimer_regime():
    W, H = 820, 460
    f = [text(W / 2, 28, "Перехід від лінійного закону Дарсі до режиму Форхгеймера", size=16, bold=True)]

    # Осі координат: X = швидкість v_d, Y = градієнт тиску -∇p
    oX, oY = 100, 380
    axisW, axisH = 640, 300

    f.append(arrow(oX, oY, oX + axisW, oY, color=INK, sw=2))
    f.append(text(oX + axisW + 15, oY + 5, "швидкість vⲇ", size=13, bold=True, anchor="start"))

    f.append(arrow(oX, oY, oX, oY - axisH, color=INK, sw=2))
    f.append(text(oX, oY - axisH - 15, "перепад тиску −∇p", size=13, bold=True))

    # Лінійна пряма Дарсі (низькі числа Рейнольдса Re_p < 1..10)
    # y = k * x
    f.append(line(oX, oY, oX + 240, oY - 140, color=FLOW, sw=2.5))
    f.append(text(oX + 160, oY - 130, "Закон Дарсі (лінійний)", size=12, color=FLOW, bold=True))
    f.append(text(oX + 160, oY - 110, "−∇p = (μ / k) vⲇ", size=11, color=FLOW))

    # Пунктирне продовження Дарсі
    f.append(line(oX + 240, oY - 140, oX + 500, oY - 290, color=FLOW, sw=1.5, dash="4,4"))

    # Параболічна крива Форхгеймера (високі Re_p > 10)
    forch_path = f"M {oX},{oY} Q {oX+240},{oY-140} {oX+520},{oY-300}"
    f.append(path(forch_path, fill="none", stroke=PRESS, sw=2.8))
    f.append(text(oX + 390, oY - 240, "Режим Форхгеймера (нелінійний)", size=12, color=PRESS, bold=True))
    f.append(text(oX + 390, oY - 220, "−∇p = (μ / k) vⲇ + β ρ vⲇ²", size=11, color=PRESS))

    # Вертикальна межа переходу Re_p ≈ 1...10
    transX = oX + 240
    f.append(line(transX, oY, transX, oY - axisH, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(transX, oY + 25, "Reₚ ≈ 1...10", size=12, color=MUTED, bold=True))
    f.append(text(transX, oY + 42, "(критичне число)", size=11, color=MUTED))

    # Зони
    f.append(rect(oX + 20, oY - 280, 180, 45, fill="#eef9f2", stroke=FLOW, sw=1))
    f.append(text(oX + 110, oY - 252, "Ламінарний режим\n(в'язке тертя панує)", size=11, color=FLOW))

    f.append(rect(oX + 320, oY - 70, 240, 45, fill="#fdf2e9", stroke=PRESS, sw=1))
    f.append(text(oX + 440, oY - 42, "Турбулентно-інерційний режим\n(вихори у порах гальмують потік)", size=11, color=PRESS))

    render(os.path.join(IMG, "forchheimer-regime.svg"), W, H, *f)


# ── Фігура 5: Тензор проникності та анізотропія ──────────────────────────────
def fig_anisotropic_tensor():
    W, H = 820, 460
    f = [text(W / 2, 28, "Анізотропія проникності в шаруватих породах", size=16, bold=True)]

    # Шарувата порода (наприклад, сланець чи пісковик із пластовою орієнтацією)
    cX, cY = 240, 240
    rW, rH = 340, 260

    f.append(rect(cX - rW/2, cY - rH/2, rW, rH, fill="#faf0e6", stroke=SAND, sw=2, rx=6))

    # Нахилені шари породи
    for sy in range(int(cY - rH/2 + 30), int(cY + rH/2), 35):
        f.append(line(cX - rW/2, sy, cX + rW/2, sy, color="#d5c3b5", sw=1.5, dash="6,4"))

    f.append(text(cX, cY - rH/2 + 20, "Шаруватий пласт породи", size=13, color=SAND, bold=True))

    # Осі проникності k_x (вздовж шарів) та k_y (поперек шарів)
    f.append(arrow(cX - 100, cY, cX + 120, cY, color=FLOW, sw=2.5))
    f.append(text(cX + 80, cY - 15, "kₓ (висока проникність)", size=12, color=FLOW, bold=True))

    f.append(arrow(cX, cY + 80, cX, cY - 100, color=PRESS, sw=2.5))
    f.append(text(cX + 15, cY - 80, "kᵧ (низька)", size=12, color=PRESS, bold=True))

    # Приклад: градієнт тиску під кутом до шарів
    f.append(arrow(cX, cY, cX + 100, cY - 80, color=INK, sw=2))
    f.append(text(cX + 105, cY - 85, "−∇p (градієнт тиску)", size=12, color=INK, bold=True))

    # Вектор швидкості відхиляється в бік легшого руху (уздовж k_x)
    f.append(arrow(cX, cY, cX + 140, cY - 30, color=TORT, sw=3))
    f.append(text(cX + 145, cY - 20, "vⲇ (вектор швидкості)", size=12, color=TORT, bold=True))

    # Права частина: Матрична (тензорна) формула
    rightX = 620
    box_tensor = "Тензорна форма закону Дарсі:\n\n" \
                 "┌ vₓ ┐       1   ┌ kₓₓ  kₓᵧ ┐   ┌ ∂p/∂x ┐\n" \
                 "│    │  =  − ──  │          │ · │       │\n" \
                 "└ vᵧ ┘       μ   └ kᵧₓ  kᵧᵧ ┘   └ ∂p/∂y ┘\n\n" \
                 "Вектор швидкості vⲇ НЕ паралельний\n" \
                 "вектору градієнта тиску ∇p!"
    f.append(fitbox(rightX, cY, 320, 240, box_tensor, size=12, fill="#fcf8f2", stroke=SAND, sw=1.5))

    render(os.path.join(IMG, "anisotropic-tensor.svg"), W, H, *f)


if __name__ == "__main__":
    fig_darcy_experiment()
    fig_pore_microscope()
    fig_hydraulic_gradient()
    fig_forchheimer_regime()
    fig_anisotropic_tensor()
    print("Всі 5 фігур для darcys-law успішно згенеровано у ./img/")
