# -*- coding: utf-8 -*-
"""Фігури до теми «Індукційний нагрів».
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

# ── Фігура 1: Принцип індукційного нагріву ──────────────────────────────────
def fig_induction_principle():
    W, H = 740, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Електродинамічний механізм індукційного нагріву", size=16, bold=True))

    # Джерело високочастотного струму I_AC
    f.append(circle(90, 200, 24, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(90, 194, "I(t)", size=14, bold=True, color=COLOR_BLUE))
    f.append(text(90, 212, "ВЧ струм", size=10, color=MUTED))

    # Індуктор (витки мідної трубки навколо деталі)
    # Провідники живлення
    f.append(line(114, 200, 180, 200, color=COLOR_BLUE, sw=2.5))
    f.append(arrow(140, 200, 170, 200, color=COLOR_BLUE, sw=2.2))

    # Витки індуктора (перерізи трубок зверху й знизу)
    coils_x = [220, 270, 320, 370, 420, 470]
    for cx in coils_x:
        # Верхній виток
        f.append(circle(cx, 100, 14, fill='#eef6ff', stroke=COLOR_BLUE, sw=2))
        f.append(circle(cx, 100, 4, fill=COLOR_BLUE, stroke='none', sw=0)) # Струм до нас (точка)
        # Нижній виток
        f.append(circle(cx, 300, 14, fill='#eef6ff', stroke=COLOR_BLUE, sw=2))
        f.append(line(cx - 5, 295, cx + 5, 305, color=COLOR_BLUE, sw=1.8)) # Струм від нас (хрестик)
        f.append(line(cx - 5, 305, cx + 5, 295, color=COLOR_BLUE, sw=1.8))

    # Металева деталь (заготовка) всередині індуктора
    f.append(rect(200, 130, 290, 140, fill='#fcf3cf', stroke='#b7950b', sw=2, rx=6))
    f.append(text(345, 155, "Металева деталь (заготовка)", size=13, bold=True, color='#7d6608'))

    # Магнітні силові лінії B(t) (зелений колір)
    f.append(line(170, 200, 520, 200, color=COLOR_GREEN, sw=1.8, dash="6,3"))
    f.append(arrow(340, 200, 380, 200, color=COLOR_GREEN, sw=2))
    f.append(line(170, 170, 520, 170, color=COLOR_GREEN, sw=1.4, dash="6,3"))
    f.append(arrow(340, 170, 380, 170, color=COLOR_GREEN, sw=1.6))
    f.append(line(170, 230, 520, 230, color=COLOR_GREEN, sw=1.4, dash="6,3"))
    f.append(arrow(340, 230, 380, 230, color=COLOR_GREEN, sw=1.6))
    f.append(text(545, 200, "Поле B(t)", size=12, bold=True, color=COLOR_GREEN))

    # Вихрові струми Фуко (червоні овальні контури у заготовці)
    f.append(rect(220, 145, 250, 110, fill='none', stroke=COLOR_RED, sw=2, rx=12))
    f.append(arrow(345, 145, 300, 145, color=COLOR_RED, sw=2))
    f.append(arrow(345, 255, 390, 255, color=COLOR_RED, sw=2))
    f.append(text(345, 220, "Вихрові струми (струми Фуко)", size=12, bold=True, color=COLOR_RED))

    # Пояснювальний блок
    b, w, h = textbox(W / 2, 355, "Змінне поле B(t) збуджує вихрові струми J_eddy → Тепло Джоуля Q = J² · ρ",
                      size=12, pad=8, fill='#fef9e7', stroke='#f5b041', sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "induction-principle.svg"), W, H, *f)


# ── Фігура 2: Розподіл густини струму (Скін-ефект) ─────────────────────────
def fig_skin_depth_distribution():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Скін-ефект: розподіл густини вихрових струмів j(z) по глибині", size=15, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Низька частота f_low ---
    f.append(text(midx / 2, 55, "Низька частота f_low (велика глибина δ)", size=13, bold=True, color=COLOR_BLUE))
    # Переріз деталі
    f.append(rect(40, 90, 280, 160, fill='#ebf5fb', stroke='#5dade2', sw=1.8, rx=4))
    f.append(text(180, 110, "Заготовка (поверхня z = 0)", size=11, color=MUTED))

    # Профіль струму (м'яка експонента)
    # Поверхнева густина
    f.append(rect(40, 130, 40, 100, fill='#a9cce3', stroke='none', sw=0))
    f.append(rect(80, 140, 60, 80, fill='#d4e6f1', stroke='none', sw=0))
    f.append(rect(140, 155, 80, 50, fill='#eaf2f8', stroke='none', sw=0))
    f.append(line(40, 230, 280, 230, color=LINE, sw=1.5)) # ось z

    # Глибина скін-шару δ_low
    f.append(line(40, 245, 160, 245, color=COLOR_BLUE, sw=2))
    f.append(arrow(40, 245, 160, 245, color=COLOR_BLUE, sw=2))
    f.append(text(100, 265, "δ_low (глибокий нагрів)", size=12, bold=True, color=COLOR_BLUE))

    f.append(fitbox(40, 285, 280, 50, "Об'ємний нагрів заготовки\n(для ковальського прогріву)",
                    size=11, pad=6, fill='#eaf2f8', stroke='#a9cce3', sw=1.2))

    # --- ПРАВА ЧАСТИНА: Висока частота f_high ---
    f.append(text(midx + midx / 2, 55, "Висока частота f_high (тонка глибина δ)", size=13, bold=True, color=COLOR_RED))
    # Переріз деталі
    f.append(rect(420, 90, 280, 160, fill='#fadbd8', stroke='#ec7063', sw=1.8, rx=4))
    f.append(text(560, 110, "Заготовка (поверхня z = 0)", size=11, color=MUTED))

    # Тонкий скін-шар
    f.append(rect(420, 130, 15, 100, fill='#e74c3c', stroke='none', sw=0))
    f.append(rect(435, 150, 15, 60, fill='#f1948a', stroke='none', sw=0))
    f.append(line(420, 230, 660, 230, color=LINE, sw=1.5)) # ось z

    # Глибина скін-шару δ_high
    f.append(line(420, 245, 450, 245, color=COLOR_RED, sw=2))
    f.append(arrow(420, 245, 450, 245, color=COLOR_RED, sw=2))
    f.append(text(435, 265, "δ_high (тонка кромка)", size=12, bold=True, color=COLOR_RED))

    f.append(fitbox(420, 285, 280, 50, "Поверхневий нагрів\n(для гартування зубів шестерень)",
                    size=11, pad=6, fill='#fadbd8', stroke='#f1948a', sw=1.2))

    return render(os.path.join(IMG, "skin-depth-distribution.svg"), W, H, *f)


# ── Фігура 3: Еквівалентна схема та резонансний інвертор ─────────────────────
def fig_equivalent_circuit_res():
    W, H = 740, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Еквівалентна трансформаторна схема та паралельний LC-резонанс", size=15, bold=True))

    # Джерело живлення DC
    f.append(rect(40, 120, 60, 100, fill='#eef6ff', stroke=COLOR_BLUE, sw=1.8, rx=4))
    f.append(text(70, 160, "DC V_in", size=12, bold=True, color=COLOR_BLUE))
    f.append(text(70, 180, "300V-600V", size=10, color=MUTED))

    # Мостовий інвертор (H-міст з ключами)
    f.append(rect(140, 100, 100, 140, fill='#f4f6f8', stroke=LINE, sw=1.6, rx=4))
    f.append(text(190, 130, "Інвертор", size=13, bold=True, color=INK))
    f.append(text(190, 150, "SiC MOSFET", size=11, color=COLOR_PURPLE))
    f.append(text(190, 170, "H-міст / ZVS", size=10, color=MUTED))

    # З'єднання DC -> Інвертор
    f.append(line(100, 140, 140, 140, color=LINE, sw=1.8))
    f.append(line(100, 200, 140, 200, color=LINE, sw=1.8))

    # Вихід інвертора до резонансного бака
    f.append(line(240, 130, 290, 130, color=COLOR_BLUE, sw=2))
    f.append(line(240, 210, 290, 210, color=COLOR_BLUE, sw=2))

    # Резонансний конденсатор C_res (паралельне або послідовне увімкнення)
    f.append(line(290, 130, 290, 150, color=LINE, sw=1.8))
    f.append(line(290, 210, 290, 190, color=LINE, sw=1.8))
    f.append(line(280, 150, 300, 150, color=COLOR_GREEN, sw=2.5)) # Обкладка C1
    f.append(line(280, 190, 300, 190, color=COLOR_GREEN, sw=2.5)) # Обкладка C2
    f.append(text(325, 170, "C_res", size=13, bold=True, color=COLOR_GREEN))

    # Лінії далі до індуктора
    f.append(line(290, 130, 380, 130, color=LINE, sw=1.8))
    f.append(line(290, 210, 380, 210, color=LINE, sw=1.8))

    # Трансформаторна модель індуктора та заготовки
    # Первинна індуктивність індуктора L_ind
    f.append(rect(380, 110, 120, 120, fill='#fff9e6', stroke='#f39c12', sw=1.8, rx=6))
    f.append(text(440, 135, "Індуктор", size=12, bold=True, color='#b9770e'))
    f.append(text(440, 155, "L_ind (первинна)", size=11, color=INK))
    f.append(text(440, 175, "R_ind (власні втрати)", size=10, color=MUTED))

    # Магнітний зв'язок k
    f.append(line(500, 140, 540, 140, color=COLOR_RED, sw=2, dash="4,2"))
    f.append(line(500, 200, 540, 200, color=COLOR_RED, sw=2, dash="4,2"))
    f.append(text(520, 165, "k (зв'язок)", size=10, bold=True, color=COLOR_RED))

    # Вторинне коло (заготовка як 1 виток: L_work, R_work)
    f.append(rect(540, 110, 140, 120, fill='#e8f8f5', stroke=COLOR_GREEN, sw=1.8, rx=6))
    f.append(text(610, 135, "Заготовка", size=12, bold=True, color=COLOR_GREEN))
    f.append(text(610, 155, "R_eq (нагрів)", size=11, bold=True, color=COLOR_RED))
    f.append(text(610, 175, "L_eq (внесена L)", size=10, color=MUTED))

    # Нижній інфо-блок
    b, w, h = textbox(W / 2, 285, "Коефіцієнт потужності cos φ ≪ 1 компенсується LC-резонансом: f_res = 1 / (2π √(L_eq · C_res))\nІнвертор працює у режимі ZVS (перемикання при нулі напруги) для ККД > 90%",
                      size=11, pad=8, fill='#eef6ff', stroke='#b3d7ff', sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "equivalent-circuit-res.svg"), W, H, *f)


# ── Фігура 4: Перехід через точку Кюрі ───────────────────────────────────────
def fig_curie_transition():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Зміна характеристик сталі при переході через точку Кюрі (T_C ≈ 770 °C)", size=15, bold=True))

    # Осі координат
    f.append(line(80, 270, 680, 270, color=LINE, sw=1.8)) # Ось Температури T
    f.append(text(685, 274, "T (°C)", size=13, bold=True, color=INK))

    f.append(line(80, 50, 80, 270, color=LINE, sw=1.8)) # Ось параметр
    f.append(text(50, 50, "Параметри", size=12, bold=True, color=INK))

    # Вертикальна лінія точки Кюрі T_C
    f.append(line(400, 50, 400, 270, color=COLOR_RED, sw=1.8, dash="5,4"))
    f.append(text(400, 40, "Точка Кюрі T_C ≈ 770°C", size=12, bold=True, color=COLOR_RED))

    # Крива 1: Магнітна проникність μ_r (падає з 500 до 1)
    f.append(line(90, 80, 360, 80, color=COLOR_BLUE, sw=2.5))
    f.append(line(360, 80, 430, 240, color=COLOR_BLUE, sw=2.5))
    f.append(line(430, 240, 660, 240, color=COLOR_BLUE, sw=2.5))
    f.append(text(220, 70, "Магнітна проникність μ_r (падає від ~500 до 1)", size=11, bold=True, color=COLOR_BLUE))

    # Крива 2: Глибина скін-шару δ (зростає у √μ_r разів, тобто у ~20 разів)
    f.append(line(90, 250, 360, 250, color=COLOR_GREEN, sw=2.5))
    f.append(line(360, 250, 430, 110, color=COLOR_GREEN, sw=2.5))
    f.append(line(430, 110, 660, 110, color=COLOR_GREEN, sw=2.5))
    f.append(text(520, 95, "Глибина скін-шару δ (зростає у ~20 разів)", size=11, bold=True, color=COLOR_GREEN))

    # Позначення двох фаз
    f.append(rect(120, 140, 200, 40, fill='#ebf5fb', stroke='#5dade2', sw=1.2, rx=4))
    f.append(text(220, 164, "Феромагнітна фаза (T < T_C)\nГістерезис + Вихрові струми", size=10, bold=True, color='#1b4f72'))

    f.append(rect(450, 140, 200, 40, fill='#fdedec', stroke='#fadbd8', sw=1.2, rx=4))
    f.append(text(550, 164, "Парамагнітна фаза (T > T_C)\nЛише вихрові струми", size=10, bold=True, color='#78281f'))

    # Формула внизу
    b, w, h = textbox(W / 2, 320, "При T > T_C еквівалентна індуктивність L_eq падає, а скін-шар δ розширюється → Резонансна частота f_r зростає!",
                      size=11, pad=6, fill='#fef9e7', stroke='#f5b041', sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "curie-transition.svg"), W, H, *f)


if __name__ == '__main__':
    fig_induction_principle()
    fig_skin_depth_distribution()
    fig_equivalent_circuit_res()
    fig_curie_transition()
    print("Всі 4 фігури для індукційного нагріву успішно згенеровано у ./img/")
