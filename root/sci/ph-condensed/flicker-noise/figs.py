# -*- coding: utf-8 -*-
"""Фігури до теми «Фліккер-шум і шум 1/f».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"


# ── Фігура 1: Порівняння спектральної щільності потужності шумів ─────────────
def fig_spectrum_comparison():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Спектральна щільність потужності: білий, рожевий (1/f) та коричневий шум", size=16, bold=True))

    # Осі координат (подвійний логарифмічний масштаб)
    f.append(line(80, 340, 700, 340, color=LINE, sw=1.8))  # Ось lg f
    f.append(line(80, 60, 80, 340, color=LINE, sw=1.8))    # Ось lg S(f)

    f.append(text(710, 344, "lg f", size=13, bold=True, color=INK))
    f.append(text(70, 50, "lg S(f)", size=13, bold=True, color=INK))

    # Сітка частот (декади)
    for x, label in [(150, "1 Hz"), (300, "10 Hz"), (450, "100 Hz"), (600, "1 kHz")]:
        f.append(line(x, 60, x, 340, color="#e5e7eb", sw=1, dash="4,4"))
        f.append(text(x, 358, label, size=11, color=MUTED))

    # 1. Білий шум S_white = const (горизонтальна лінія)
    f.append(line(80, 240, 680, 240, color=COLOR_BLUE, sw=2.2))
    f.append(text(620, 226, "Білий шум S(f) = const", size=12, bold=True, color=COLOR_BLUE))

    # 2. Рожевий шум 1/f (нахил -1)
    f.append(line(100, 80, 580, 320, color=COLOR_RED, sw=2.5))
    f.append(text(210, 110, "Фліккер-шум S(f) ~ 1/f^α  (α ≈ 1)", size=12, bold=True, color=COLOR_RED))

    # 3. Коричневий шум 1/f^2 (нахил -2)
    f.append(line(100, 70, 370, 330, color=COLOR_PURPLE, sw=2.0, dash="6,3"))
    f.append(text(130, 200, "1/f^2 (Random walk)", size=11, bold=True, color=COLOR_PURPLE))

    # Кутова частота fc (перетин білого та 1/f шуму)
    f.append(circle(420, 240, 6, fill=COLOR_GREEN, stroke=LINE, sw=1.5))
    f.append(line(420, 240, 420, 340, color=COLOR_GREEN, sw=1.5, dash="4,4"))
    f.append(text(420, 375, "fc (Кутова частота)", size=12, bold=True, color=COLOR_GREEN))

    # Пояснювальні рамки
    b1, w1, h1 = textbox(250, 290, "Низькі частоти (f < fc):\nДомінує фліккер-шум 1/f",
                         size=11, pad=6, fill="#fdeded", stroke="#f5c6cb", sw=1.2)
    f.append(b1)

    b2, w2, h2 = textbox(570, 290, "Високі частоти (f > fc):\nДомінує білий (тепловий) шум",
                         size=11, pad=6, fill="#eaf2ed", stroke="#c3e6cb", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "spectrum-comparison.svg"), W, H, *f)


# ── Фігура 2: Модель МакВортера (тунелювання в пастки оксиду) ──────────────
def fig_mcwhorter_tunneling():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Модель МакВортера: флуктуація кількості носіїв через тунелювання у пастки", size=15, bold=True))

    # 1. Напівпровідниковий канал (ліворуч)
    f.append(rect(60, 70, 240, 260, fill="#eef6ff", stroke=COLOR_BLUE, sw=2, rx=4))
    f.append(text(180, 95, "Кремнієвий канал (Si)", size=14, bold=True, color=COLOR_BLUE))

    # Електрони в каналі
    for cy in [140, 190, 240, 290]:
        f.append(circle(120, cy, 10, fill="#d0e1fd", stroke=COLOR_BLUE, sw=1.5))
        f.append(text(120, cy + 3.5, "e−", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(180, 310, "Вільно дрейфуючі носії", size=11, italic=True, color=MUTED))

    # 2. Межа розділу Si / SiO2
    f.append(line(300, 70, 300, 330, color=LINE, sw=2.5, dash="6,3"))
    f.append(text(300, 60, "Межа розділу Si / SiO2", size=11, bold=True, color=INK))

    # 3. Оксидний діелектрик (праворуч)
    f.append(rect(300, 70, 380, 260, fill="#fff9ec", stroke=COLOR_ORANGE, sw=2, rx=4))
    f.append(text(490, 95, "Оксидний шар діелектрика (SiO2)", size=14, bold=True, color=COLOR_ORANGE))

    # Пастки на різній глибині x від межі
    traps = [(350, 140, "x1 (близько)", "τ1 ~ 10⁻⁶ s"),
             (440, 190, "x2 (середньо)", "τ2 ~ 10⁻³ s"),
             (540, 240, "x3 (глибоко)", "τ3 ~ 1 s"),
             (630, 290, "x4 (дуже глибоко)", "τ4 ~ 10³ s")]

    for tx, ty, xlabel, taulabel in traps:
        # Хрестик або квадрат пастки
        f.append(rect(tx - 12, ty - 12, 24, 24, fill="#fdecea", stroke=COLOR_RED, sw=1.5, rx=3))
        f.append(text(tx, ty + 4, "T", size=11, bold=True, color=COLOR_RED))

        # Стрілка тунелювання від межі до пастки
        f.append(arrow(300, ty, tx - 14, ty, color=COLOR_RED, sw=1.5))
        f.append(text(tx, ty - 18, xlabel, size=10, bold=True, color=INK))
        f.append(text(tx, ty + 26, taulabel, size=10, color=COLOR_RED))

    # Вісь глибини x
    f.append(line(300, 355, 680, 355, color=LINE, sw=1.5))
    f.append(arrow(300, 355, 680, 355, color=LINE, sw=1.5))
    f.append(text(690, 359, "x", size=12, bold=True, color=INK))

    # Пояснення експоненціальної залежності часу
    b, w, h = textbox(W / 2, 380, "Час релаксації зростає експоненціально з глибиною: τ(x) = τ0 · exp(2κ x)   →   P(τ) ~ 1/τ",
                      size=11, pad=5, fill="#f4f6f8", stroke=LINE, sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "mcwhorter-tunneling.svg"), W, H, *f)


# ── Фігура 3: Суперпозиція лоренціанів ──────────────────────────────────────
def fig_lorentzian_superposition():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Формування спектра 1/f як суперпозиції огинаючих лоренціанів", size=16, bold=True))

    # Осі координат
    f.append(line(80, 340, 700, 340, color=LINE, sw=1.8))
    f.append(line(80, 60, 80, 340, color=LINE, sw=1.8))
    f.append(text(710, 344, "lg f", size=13, bold=True, color=INK))
    f.append(text(70, 50, "lg S(f)", size=13, bold=True, color=INK))

    # Окремі лоренціанові криві (S_i(f) = 4 A τ_i / (1 + (2π f τ_i)^2))
    lorentzians = [
        (130, 110, "τ1 (короткий)", COLOR_BLUE),
        (230, 140, "τ2", COLOR_GREEN),
        (330, 170, "τ3", COLOR_ORANGE),
        (430, 200, "τ4", COLOR_PURPLE),
        (530, 230, "τ5 (довгий)", COLOR_RED)
    ]

    for fx, fy, label, col in lorentzians:
        # Горизонтальна ділянка від 90 до fx, потім спад до (fx+130, fy+110)
        f.append(line(90, fy, fx, fy, color=col, sw=1.4, dash="5,3"))
        f.append(line(fx, fy, fx + 130, fy + 110, color=col, sw=1.4, dash="5,3"))
        f.append(circle(fx, fy, 4, fill=col, stroke=LINE, sw=1))
        f.append(text(fx, fy - 10, label, size=10, bold=True, color=col))

    # Огинаюча сума ∑ S_i(f) — прямолінійний нахил 1/f
    f.append(line(100, 95, 620, 275, color=COLOR_RED, sw=3.0))
    f.append(text(380, 150, "Сумарний спектр S(f) ~ 1/f", size=14, bold=True, color=COLOR_RED))

    # Позначення меж частотного діапазону [1/τ_max, 1/τ_min]
    f.append(line(120, 60, 120, 340, color=MUTED, sw=1, dash="3,3"))
    f.append(text(120, 358, "f_min = 1/τ_max", size=11, color=MUTED))

    f.append(line(580, 60, 580, 340, color=MUTED, sw=1, dash="3,3"))
    f.append(text(580, 358, "f_max = 1/τ_min", size=11, color=MUTED))

    # Пояснювальний бокс
    b, w, h = textbox(W / 2, 390, "Кожен релаксатор додає лоренціан. Якщо P(τ) ~ 1/τ, сума утворює гладку лінію 1/f у межах [f_min, f_max]",
                      size=11, pad=6, fill="#fff9ec", stroke="#ffeba6", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "lorentzian-superposition.svg"), W, H, *f)


# ── Фігура 4: Чоперне підсилення (Chopper stabilization) ───────────────────
def fig_chopper_stabilization():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Чоперне підсилення (Chopper Stabilization): винесення сигналу з зони 1/f шуму", size=15, bold=True))

    # 1. Вхідний сигнал x(t)
    f.append(text(60, 110, "Вхідний\nсигнал x(t)", size=11, bold=True, color=INK))
    f.append(arrow(100, 120, 150, 120, color=LINE, sw=1.8))

    # 2. Модулятор 1 (Chopper 1)
    f.append(circle(170, 120, 20, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8))
    f.append(text(170, 120, "M1", size=13, bold=True, color=COLOR_BLUE))
    f.append(arrow(170, 180, 170, 142, color=COLOR_BLUE, sw=1.5))
    f.append(text(170, 195, "f_m (Несуча)", size=10, bold=True, color=COLOR_BLUE))
    f.append(arrow(190, 120, 250, 120, color=LINE, sw=1.8))
    f.append(text(220, 105, "Сигнал на f_m", size=10, color=MUTED))

    # 3. Підсилювач (додає 1/f шум у низьких частотах)
    f.append(rect(250, 90, 90, 60, fill="#fdeded", stroke=COLOR_RED, sw=2, rx=4))
    f.append(text(295, 114, "Підсилювач", size=12, bold=True, color=COLOR_RED))
    f.append(text(295, 134, "+ 1/f шум!", size=10, bold=True, color=COLOR_RED))
    f.append(arrow(340, 120, 400, 120, color=LINE, sw=1.8))

    # 4. Демодулятор 2 (Chopper 2)
    f.append(circle(420, 120, 20, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8))
    f.append(text(420, 120, "M2", size=13, bold=True, color=COLOR_BLUE))
    f.append(arrow(420, 180, 420, 142, color=COLOR_BLUE, sw=1.5))
    f.append(text(420, 195, "f_m (Несуча)", size=10, bold=True, color=COLOR_BLUE))
    f.append(arrow(440, 120, 500, 120, color=LINE, sw=1.8))

    # 5. Фільтр низьких частот (ФНЧ)
    f.append(rect(500, 90, 80, 60, fill="#eafaf1", stroke=COLOR_GREEN, sw=2, rx=4))
    f.append(text(540, 120, "ФНЧ", size=13, bold=True, color=COLOR_GREEN))
    f.append(arrow(580, 120, 650, 120, color=LINE, sw=1.8))

    f.append(text(690, 120, "Чистий\nсигнал y(t)", size=11, bold=True, color=COLOR_GREEN))

    # Нижній ряд: Спектральні діаграми на кожному етапі
    # Спектр 1: Сигнал біля 0 Гц
    f.append(rect(40, 240, 130, 80, fill=BG, stroke=LINE, sw=1, rx=3))
    f.append(line(50, 300, 160, 300, color=LINE, sw=1))
    f.append(line(50, 250, 50, 300, color=LINE, sw=1))
    f.append(rect(55, 270, 20, 30, fill=COLOR_BLUE, stroke='none', sw=0, rx=0))
    f.append(text(105, 314, "1. Сигнал на 0 Гц", size=9, bold=True, color=INK))

    # Спектр 2: Сигнал перенесений на fm
    f.append(rect(200, 240, 130, 80, fill=BG, stroke=LINE, sw=1, rx=3))
    f.append(line(210, 300, 320, 300, color=LINE, sw=1))
    f.append(line(210, 250, 210, 300, color=LINE, sw=1))
    f.append(rect(275, 270, 20, 30, fill=COLOR_BLUE, stroke='none', sw=0, rx=0))
    f.append(text(265, 314, "2. Модуляція на fm", size=9, bold=True, color=INK))

    # Спектр 3: Після демодуляції
    f.append(rect(360, 240, 150, 80, fill=BG, stroke=LINE, sw=1, rx=3))
    f.append(line(370, 300, 500, 300, color=LINE, sw=1))
    f.append(line(370, 250, 370, 300, color=LINE, sw=1))
    f.append(rect(375, 270, 20, 30, fill=COLOR_BLUE, stroke='none', sw=0, rx=0))
    f.append(line(450, 260, 480, 300, color=COLOR_RED, sw=1.5))
    f.append(text(435, 314, "3. Демодуляція: шум -> fm", size=9, bold=True, color=INK))

    # Спектр 4: Після ФНЧ
    f.append(rect(550, 240, 150, 80, fill=BG, stroke=LINE, sw=1, rx=3))
    f.append(line(560, 300, 690, 300, color=LINE, sw=1))
    f.append(line(560, 250, 560, 300, color=LINE, sw=1))
    f.append(rect(565, 270, 20, 30, fill=COLOR_GREEN, stroke='none', sw=0, rx=0))
    f.append(line(640, 298, 670, 300, color=MUTED, sw=1, dash="2,2"))
    f.append(text(625, 314, "4. ФНЧ зрізає 1/f шум!", size=9, bold=True, color=COLOR_GREEN))

    return render(os.path.join(IMG, "chopper-stabilization.svg"), W, H, *f)


if __name__ == '__main__':
    fig_spectrum_comparison()
    fig_mcwhorter_tunneling()
    fig_lorentzian_superposition()
    fig_chopper_stabilization()
    print("Усі 4 фігури для теми flicker-noise успішно згенеровано у ./img/")
