#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Ваговий бюджет апарата: від задачі до злітної маси».
"""

import sys
import os
import math

# Підключення svgkit із кореневої теки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_weight_breakdown_tree(out_path):
    """Фігура 1: Ієрархічне дерево структури максимальної злітної маси (MTOW)."""
    W, H = 940, 520
    f = []

    # Головний вузол: MTOW
    top_box, tw, th = textbox(W / 2, 50, "MTOW: Повна злітна маса апарата (100%)\nСума мас усіх компонентів, конструкцій та корисного вантажу",
                              size=14, bold=True, fill="#e8f4fd", stroke=NEG, pad=12)
    f.append(top_box)

    # 5 гілок підсистем
    categories = [
        ("Корисне навантаження", "15–30% MTOW\n• Камера / тепловізор\n• Оптичний підвіс\n• Далекоміри / LiDAR\n• Супутній SBC / AI", "#fef5e7", "#d35400", 110),
        ("Батарея живлення", "35–55% MTOW\n• Li-ion / LiPo комірки\n• Силові кабелі й роз'єми\n• Зварні шини, BMS\n• Захисний кожух", "#fdecea", POS, 285),
        ("Силова установка", "15–25% MTOW\n• BLDC електромотори\n• Пропелери (гвинти)\n• ESC регулятори\n• Моторні дроти", "#eafaf1", FIELD, 470),
        ("Бортова авіоніка", "5–10% MTOW\n• Політний контролер (FC)\n• Модуль GNSS / компас\n• Приймач керування (RX)\n• Відеопередавач (VTX)", "#f4ecf7", "#8e44ad", 655),
        ("Планер і кріплення", "10–20% MTOW\n• Карбонові промені\n• Центральні пластини\n• Гвинти, стійки, кронштейни\n• Шасі та демпфери", "#eaeded", "#566573", 830)
    ]

    y_cat = 230
    for title, desc, bg_col, stroke_col, cx in categories:
        # Лінія від кореня до підсистеми
        f.append(line(W / 2, 78, cx, y_cat - 75, color="#7f8c8d", sw=1.5))
        f.append(arrow(cx, y_cat - 75, cx, y_cat - 65, color=stroke_col, sw=1.5))

        # Блок категорії
        box_str = f"{title}\n{desc}"
        b_svg, bw, bh = textbox(cx, y_cat, box_str, size=12, bold=False, fill=bg_col, stroke=stroke_col, pad=8, rx=6)
        f.append(b_svg)

    # Нижній пояс: конструкторський резерв і приховані маси
    res_y = 430
    res_box = rect(60, res_y - 35, W - 120, 85, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8)
    f.append(res_box)
    f.append(text(W / 2, res_y - 12, "Конструкторський резерв маси (5–10% MTOW) та неураховані дрібниці", size=13, color="#b7950b", bold=True))
    f.append(text(W / 2, res_y + 10, "Припій на силових платах (+15–30 г) • Кабельні стяжки, термоусадка, текстильні липучки (+25–40 г)", size=11, color=INK))
    f.append(text(W / 2, res_y + 30, "Мідь силових дротів 12/14 AWG (+40–70 г) • Демпферні силіконові втулки та фіксатор різьби (+10–15 г)", size=11, color=MUTED))

    # Стрілки від підсистем до резерву
    f.append(line(110, y_cat + 75, 200, res_y - 35, color="#bdc3c7", sw=1.2, dash="4,4"))
    f.append(line(830, y_cat + 75, 740, res_y - 35, color="#bdc3c7", sw=1.2, dash="4,4"))

    render(out_path, W, H, *f)


def fig_diminishing_returns_curve(out_path):
    """Фігура 2: Графік спадної віддачі акумулятора (час польоту від частки маси батареї)."""
    W, H = 880, 500
    f = []

    # Заголовок координат
    ox, oy = 90, 410
    gw, gh = 720, 330

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1, rx=4))

    # Горизонтальні лінії сітки (короткі поділки або тонкі пунктири)
    for i in range(1, 6):
        gy = oy - (gh / 5) * i
        f.append(line(ox, gy, ox + gw, gy, color="#edf2f7", sw=1, dash="4,4"))
        val = i * 10
        f.append(text(ox - 10, gy + 4, f"{val} хв", size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії сітки
    for i in range(1, 10):
        gx = ox + (gw / 10) * i
        f.append(line(gx, oy - gh, gx, oy, color="#edf2f7", sw=1, dash="4,4"))
        val = i * 10
        f.append(text(gx, oy + 20, f"{val}%", size=11, color=MUTED, anchor="middle"))

    # Осі координат
    f.append(arrow(ox, oy, ox + gw + 35, oy, color=LINE, sw=2))
    f.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=2))

    # Підписи осей
    f.append(text(ox + gw + 40, oy + 4, "m_bat / MTOW (частка батареї)", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(ox - 15, oy - gh - 30, "Час висіння (хвилини)", size=12, color=INK, bold=True, anchor="start"))

    # Розрахунок точок кривої висіння
    pts_ideal = []
    pts_real = []
    for step in range(1, 92):
        beta = step / 100.0
        val_ideal = 110.0 * beta * math.sqrt(1.0 - beta)
        val_real = 100.0 * beta * math.sqrt(1.0 - beta) * (1.0 - 0.45 * (beta ** 2))

        px = ox + beta * gw
        py_ideal = oy - (val_ideal / 50.0) * gh
        py_real = oy - (val_real / 50.0) * gh

        pts_ideal.append(f"{px:.1f},{py_ideal:.1f}")
        pts_real.append(f"{px:.1f},{py_real:.1f}")

    # Області графіка: корисна зона, оптимум, деградація
    f.append(rect(ox, oy - gh, gw * 0.35, gh, fill="#eafaf1", stroke="none"))
    f.append(rect(ox + gw * 0.35, oy - gh, gw * 0.25, gh, fill="#fefde8", stroke="none"))
    f.append(rect(ox + gw * 0.60, oy - gh, gw * 0.40, gh, fill="#fdecea", stroke="none"))

    # Малювання кривих
    f.append(f'<polyline points="{" ".join(pts_ideal)}" fill="none" stroke="#95a5a6" stroke-width="2" stroke-dasharray="6,4"/>')
    f.append(f'<polyline points="{" ".join(pts_real)}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Позначка реального піку (~55%)
    peak_beta = 0.55
    peak_val_real = 100.0 * peak_beta * math.sqrt(1.0 - peak_beta) * (1.0 - 0.45 * (peak_beta ** 2))
    peak_x = ox + peak_beta * gw
    peak_y = oy - (peak_val_real / 50.0) * gh

    f.append(circle(peak_x, peak_y, 6, fill=POS, stroke=BG, sw=2))
    f.append(line(peak_x, peak_y, peak_x, oy, color=POS, sw=1.5, dash="3,3"))

    # Текстова виноска до піку
    # Розміщено в прямокутнику між gx=234..306 та gy=146..212, де немає ліній
    box_peak, bw, bh = textbox(270, 178, "Практичний пік\n(~52–56% MTOW)\nМаксимум висіння",
                               size=11, bold=True, fill="#ffffff", stroke=POS, pad=6)
    f.append(box_peak)
    # Стрілка від правого краю виноски до маркера піку
    f.append(arrow(270 + bw / 2 + 4, 178, peak_x - 8, peak_y - 6, color=POS, sw=1.5))

    # Підписи зон угорі (над верхньою межею сітки oy - gh = 80)
    f.append(text(ox + gw * 0.175, 45, "Динамічна зона (30–35%)", size=11, color="#27ae60", bold=True))
    f.append(text(ox + gw * 0.175, 60, "Висока тягооснащеність TWR > 2.5", size=10, color="#27ae60"))

    f.append(text(ox + gw * 0.475, 45, "Long Range зона (45–55%)", size=11, color="#b7950b", bold=True))
    f.append(text(ox + gw * 0.475, 60, "Оптимум тривалості висіння", size=10, color="#b7950b"))

    f.append(text(ox + gw * 0.80, 45, "«Літаюча батарея» (>60%)", size=11, color=POS, bold=True))
    f.append(text(ox + gw * 0.80, 60, "Втрата керованості, перегрів ESC", size=10, color=POS))

    # Легенда
    f.append(line(ox + 40, oy - 40, ox + 75, oy - 40, color=POS, sw=3))
    f.append(text(ox + 85, oy - 36, "Реальний час з урахуванням просадки U та нагріву", size=11, color=INK, anchor="start"))
    f.append(line(ox + 40, oy - 20, ox + 75, oy - 20, color="#95a5a6", sw=2, dash="6,4"))
    f.append(text(ox + 85, oy - 16, "Теоретична імпульсна модель (без теплових втрат)", size=11, color=MUTED, anchor="start"))

    render(out_path, W, H, *f)


def fig_cg_balance_lever(out_path):
    """Фігура 3: Балансування центру тяжіння (CG) відносно центру тяги (COT)."""
    W, H = 880, 460
    f = []

    # Рама дрона (вид збоку)
    beam_y = 220
    f.append(line(160, beam_y, 720, beam_y, color="#34495e", sw=6))

    # Мотори ліворуч і праворуч
    f.append(rect(140, beam_y - 30, 40, 30, fill="#7f8c8d", stroke=INK, sw=1.5, rx=3))
    f.append(rect(700, beam_y - 30, 40, 30, fill="#7f8c8d", stroke=INK, sw=1.5, rx=3))

    # Пропелери
    f.append(line(100, beam_y - 30, 220, beam_y - 30, color="#2980b9", sw=3))
    f.append(line(660, beam_y - 30, 780, beam_y - 30, color="#2980b9", sw=3))

    # Вектори тяги моторів (ідеальний баланс проти зміщеного)
    # Геометричний центр тяги (Center of Thrust, CoT)
    cot_x = 440
    f.append(line(cot_x, beam_y - 140, cot_x, beam_y + 160, color="#27ae60", sw=1.5, dash="6,4"))
    f.append(text(cot_x, beam_y - 150, "CoT: Геометричний центр тяги", size=12, color="#27ae60", bold=True))

    # Зміщений центр тяжіння (Center of Gravity, CG)
    cg_x = 360  # зміщений вперед на 80px
    f.append(line(cg_x, beam_y - 90, cg_x, beam_y + 160, color=POS, sw=2, dash="4,4"))
    f.append(circle(cg_x, beam_y, 10, fill=POS, stroke=BG, sw=2))
    f.append(text(cg_x, beam_y + 30, "CG: Центр мас\n(зміщений вперед)", size=12, color=POS, bold=True))

    # Розмір плеча зсуву d_cg
    dim_y = beam_y + 90
    f.append(line(cg_x, dim_y, cot_x, dim_y, color=POS, sw=1.5))
    f.append(arrow(cg_x + 25, dim_y, cg_x, dim_y, color=POS, sw=1.5))
    f.append(arrow(cot_x - 25, dim_y, cot_x, dim_y, color=POS, sw=1.5))
    f.append(text((cg_x + cot_x) / 2, dim_y - 10, "Зсув Δx = 22 мм", size=12, color=POS, bold=True))

    # Навантаження на передні й задні мотори внаслідок зсуву
    # Передній мотор (ліворуч): тяга 72%
    f.append(arrow(160, beam_y - 35, 160, beam_y - 130, color=POS, sw=3.5))
    f.append(text(160, beam_y - 140, "T_front = 72%\n(перегрів, насичення)", size=11, color=POS, bold=True))

    # Задній мотор (праворуч): тяга 28%
    f.append(arrow(720, beam_y - 35, 720, beam_y - 75, color="#2980b9", sw=2))
    f.append(text(720, beam_y - 85, "T_rear = 28%\n(недовикористаний)", size=11, color="#2980b9", bold=True))

    # Наслідки асиметрії (нижній блок)
    bot_y = 390
    bot_box = rect(60, bot_y - 25, W - 120, 75, fill="#fdedec", stroke=POS, sw=1.5, rx=6)
    f.append(bot_box)
    f.append(text(W / 2, bot_y - 5, "Наслідки статичного перекосу центру тяжіння (CG ≠ CoT):", size=12, color=POS, bold=True))
    f.append(text(W / 2, bot_y + 15, "• Постійний компенсаційний момент I-терму в ПІД-регуляторі • Втрата запасу тяги на маневр тангажу", size=11, color=INK))
    f.append(text(W / 2, bot_y + 33, "• Асиметричний розряд і температурний перекіс ключів ESC • Зниження загального ККД системи на 12–18%", size=11, color=MUTED))

    render(out_path, W, H, *f)


def fig_design_iteration_spiral(out_path):
    """Фігура 4: Ітеративний цикл сходимості вагового бюджету (Design Iteration Loop)."""
    W, H = 880, 480
    f = []

    # 5 кроків у замкненому контурі
    steps = [
        ("1. Завдання місії", "Корисне навантаження m_p\nЦільовий час польоту t\nТип платформи (X4 / X6)", 130, 90, "#ebf5fb", "#2980b9"),
        ("2. Енергетичний розрахунок", "Потрібна енергія E = P·t\nМаса батареї m_bat = E / σ_e\nВибір конфігурації (6S2P)", 440, 90, "#fef5e7", "#d35400"),
        ("3. Силова установка", "Тяга висіння T_hov = MTOW·g\nПідбір мотора й пропелера\nМаса моторів + ESC + гвинтів", 750, 90, "#eafaf1", FIELD),
        ("4. Планер та конструктив", "Маса рами m_fr = k_str·MTOW\nБортова авіоніка й проводка\nКонструкторський резерв (+8%)", 750, 310, "#f4ecf7", "#8e44ad"),
        ("5. Перевірка сходимості", "Нова злітна маса MTOW_k+1\nЧи |ΔMTOW| < 2% ?\nПеревірка TWR > 1.8 та CG", 440, 310, "#e8f8f5", "#16a085"),
    ]

    for title, desc, cx, cy, fill_col, strk_col in steps:
        box_svg, bw, bh = textbox(cx, cy, f"{title}\n{desc}", size=12, bold=False, fill=fill_col, stroke=strk_col, pad=10, rx=8)
        f.append(box_svg)

    # Стрілки прямого потоку (1 -> 2 -> 3 -> 4 -> 5)
    f.append(arrow(245, 90, 325, 90, color=LINE, sw=2))
    f.append(arrow(555, 90, 635, 90, color=LINE, sw=2))
    f.append(arrow(750, 160, 750, 240, color=LINE, sw=2))
    f.append(arrow(635, 310, 555, 310, color=LINE, sw=2))

    # Гілка розгалуження від кроку 5:
    # 1) Якщо НЕ зійшлося -> зворотна стрілка до кроку 2 (Ітерація k+1)
    f.append(line(440, 240, 440, 190, color=POS, sw=2))
    f.append(arrow(440, 190, 440, 160, color=POS, sw=2))
    f.append(rect(340, 185, 200, 26, fill="#fdecea", stroke=POS, sw=1, rx=4))
    f.append(text(440, 202, "Ні: корекція MTOW (ітерація k+1)", size=10, color=POS, bold=True))

    # 2) Якщо ЗІЙШЛОСЯ -> вихід у виробництво (праворуч униз або ліворуч униз)
    f.append(arrow(325, 310, 235, 310, color="#27ae60", sw=2.5))
    done_box, _, _ = textbox(130, 310, "ФІНАЛЬНИЙ БЮДЖЕТ\n✓ MTOW затверджено\n✓ Запас тяги TWR підтверджено\n✓ Центрування CG в межах 2 мм\n✓ Специфікація закупівлі (BOM)",
                             size=11, bold=True, fill="#eafaf1", stroke="#27ae60", pad=10, rx=8)
    f.append(done_box)
    f.append(text(280, 298, "ТАК: ΔMTOW < 2%", size=11, color="#27ae60", bold=True))

    # Нижня примітка про збіжність
    f.append(text(W / 2, 440, "Зазвичай контур сходиться за 3–4 ітерації. Якщо маса росте експоненційно — задача вимагає легшого сенсора або більшого гвинта.",
                  size=11, color=MUTED, italic=True))

    render(out_path, W, H, *f)


def main():
    print("Генерація SVG-фігур для теми vahovyi-biudzhet-aparata...")
    fig_weight_breakdown_tree(os.path.join(IMG_DIR, "weight-breakdown-tree.svg"))
    fig_diminishing_returns_curve(os.path.join(IMG_DIR, "diminishing-returns-curve.svg"))
    fig_cg_balance_lever(os.path.join(IMG_DIR, "cg-balance-lever.svg"))
    fig_design_iteration_spiral(os.path.join(IMG_DIR, "design-iteration-spiral.svg"))
    print("Успішно згенеровано 4 фігури в", IMG_DIR)


if __name__ == "__main__":
    main()
