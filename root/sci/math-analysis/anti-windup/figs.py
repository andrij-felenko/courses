# -*- coding: utf-8 -*-
"""Генератор фігур для теми anti-windup (Анти-windup)."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_windup_mechanism():
    """Фігура 1: Механізм інтегрального насичення без Anti-Windup."""
    w, h = 820, 480
    frags = []

    # Заголовок фігури
    frags.append(text(410, 24, "Механізм інтегрального насичення (Windup) без захисту", size=16, bold=True))

    # Спільні параметри для трьох часових графіків
    gx0, gx1 = 120, 770
    gw = gx1 - gx0
    t_step = gx0 + int(gw * 0.10)       # t = 1.0 c: стрибок уставки
    t_reach = gx0 + int(gw * 0.40)      # t = 4.0 c: PV досягає SP (e = 0)
    t_desat = gx0 + int(gw * 0.70)      # t = 7.0 c: розряд інтегратора до u_max
    t_end = gx1                         # t = 10.0 c: заспокоєння

    # ── Графік 1: Похибка та процес (SP vs PV) ───────────────────────────────
    y1_top, y1_bot = 60, 160
    # Вісь Y і X
    frags.append(line(gx0, y1_bot, gx1, y1_bot, color=LINE, sw=1.2))
    frags.append(line(gx0, y1_bot, gx0, y1_top, color=LINE, sw=1.2))
    frags.append(text(gx0 - 12, (y1_top + y1_bot) / 2, "y(t), r(t)", size=12, color=INK, anchor="end"))
    frags.append(text(gx0 - 12, y1_top + 15, "100%", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx0 - 12, y1_bot, "0%", size=11, color=MUTED, anchor="end"))

    # Лінія SP (уставка)
    sp_y = y1_top + 20
    sp_path = (
        f'<path d="M {gx0} {y1_bot} L {t_step} {y1_bot} L {t_step} {sp_y} L {gx1} {sp_y}" '
        f'fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="5,3"/>'
    )
    frags.append(sp_path)
    frags.append(text(gx1 - 10, sp_y - 8, "Уставка r(t)", size=11, color=POS, anchor="end", bold=True))

    # Траєкторія PV (вихід об'єкта) з великим перерегулюванням
    pv_peak_x = int(gx0 + gw * 0.65)
    pv_peak_y = y1_top - 5
    pv_path = (
        f'<path d="M {gx0} {y1_bot} L {t_step} {y1_bot} '
        f'Q {t_step + 60} {y1_bot - 5} {t_reach} {sp_y} '
        f'Q {pv_peak_x} {pv_peak_y - 20} {t_desat + 40} {sp_y + 10} '
        f'Q {gx1 - 40} {sp_y - 5} {gx1} {sp_y}" '
        f'fill="none" stroke="{NEG}" stroke-width="2.2"/>'
    )
    frags.append(pv_path)
    frags.append(text(pv_peak_x + 10, pv_peak_y - 6, "Перерегулювання (Overshoot)", size=11, color=NEG, bold=True))

    # ── Графік 2: Вихід регулятора u(t) та фізичне насичення ─────────────────
    y2_top, y2_bot = 190, 290
    frags.append(line(gx0, y2_bot, gx1, y2_bot, color=LINE, sw=1.2))
    frags.append(line(gx0, y2_bot, gx0, y2_top, color=LINE, sw=1.2))
    frags.append(text(gx0 - 12, (y2_top + y2_bot) / 2, "u(t)", size=12, color=INK, anchor="end"))

    u_sat_y = y2_top + 35
    frags.append(line(gx0, u_sat_y, gx1, u_sat_y, color=POS, sw=1.2, dash="3,3"))
    frags.append(text(gx0 - 12, u_sat_y + 4, "u_max", size=11, color=POS, anchor="end", bold=True))

    # Область надлишкового розгону (заливка)
    windup_poly = (
        f'<polygon points="{t_step},{u_sat_y} {t_step},{y2_top} {t_reach},{y2_top + 10} '
        f'{t_desat},{u_sat_y}" fill="#fee2e2" opacity="0.6"/>'
    )
    frags.append(windup_poly)

    # Ненасичений розрахунковий вихід u_ideal(t)
    u_ideal_path = (
        f'<path d="M {gx0} {y2_bot} L {t_step} {y2_bot} L {t_step} {y2_top} '
        f'Q {t_step + 80} {y2_top + 5} {t_reach} {y2_top + 15} '
        f'Q {t_reach + 80} {y2_top + 30} {t_desat} {u_sat_y} '
        f'Q {t_desat + 40} {y2_bot - 10} {gx1} {y2_bot - 30}" '
        f'fill="none" stroke="#991b1b" stroke-width="1.8" stroke-dasharray="4,3"/>'
    )
    frags.append(u_ideal_path)
    frags.append(text(t_step + 90, y2_top + 12, "Розрахунковий вихід u(t) >> u_max", size=11, color="#991b1b"))

    # Фізичний насичений сигнал sat(u)
    u_sat_path = (
        f'<path d="M {gx0} {y2_bot} L {t_step} {y2_bot} L {t_step} {u_sat_y} '
        f'L {t_desat} {u_sat_y} '
        f'Q {t_desat + 40} {y2_bot - 10} {gx1} {y2_bot - 30}" '
        f'fill="none" stroke="{INK}" stroke-width="2.4"/>'
    )
    frags.append(u_sat_path)
    frags.append(text(t_reach + 40, u_sat_y - 8, "Фізичний сигнал sat(u) = 100%", size=11, color=INK, bold=True))

    # ── Графік 3: Стан інтегратора I(t) ───────────────────────────────────────
    y3_top, y3_bot = 320, 420
    frags.append(line(gx0, y3_bot, gx1, y3_bot, color=LINE, sw=1.2))
    frags.append(line(gx0, y3_bot, gx0, y3_top, color=LINE, sw=1.2))
    frags.append(text(gx0 - 12, (y3_top + y3_bot) / 2, "I(t)", size=12, color=INK, anchor="end"))
    frags.append(text(gx1, y3_bot + 16, "Час t", size=12, color=INK, anchor="end"))

    # Траєкторія інтегратора I(t)
    i_path = (
        f'<path d="M {gx0} {y3_bot} L {t_step} {y3_bot} '
        f'Q {t_step + 80} {y3_top + 10} {t_reach} {y3_top + 5} '
        f'Q {t_reach + 90} {y3_top + 10} {t_desat} {y3_top + 50} '
        f'Q {gx1 - 50} {y3_bot - 25} {gx1} {y3_bot - 25}" '
        f'fill="none" stroke="{POS}" stroke-width="2.2"/>'
    )
    frags.append(i_path)

    # Вертикальні лінії критичних моментів
    for xt, lbl, ytxt in [
        (t_step, "t₁: Стрибок SP\n(удар у насичення)", 445),
        (t_reach, "t₂: PV досяг SP\n(помилка e = 0)", 445),
        (t_desat, "t₃: Вихід із насичення\n(запізнілий розряд)", 445),
    ]:
        frags.append(line(xt, y1_top - 10, xt, y3_bot + 10, color=MUTED, sw=1.0, dash="3,3"))
        frags.append(textbox(xt, ytxt, lbl, size=10, fill="#f8fafc", stroke=MUTED, pad=4)[0])

    # Стрілка пояснення затримки виходу
    frags.append(arrow(t_reach, y3_top + 30, t_desat, y3_top + 30, color=POS, sw=1.5))
    frags.append(text((t_reach + t_desat) / 2, y3_top + 22, "Затримка розряду (Windup Lag)", size=10, color=POS, bold=True))

    return render(os.path.join(IMG_DIR, "windup-mechanism.svg"), w, h, *frags)


def fig_anti_windup_topologies():
    """Фігура 2: Структурні схеми методів Clamping та Back-Calculation."""
    w, h = 820, 480
    frags = []

    frags.append(text(410, 24, "Топології захисту від інтегрального насичення", size=16, bold=True))

    # ── БЛОК А: Умовне інтегрування (Clamping) ────────────────────────────────
    ay = 120
    frags.append(text(20, ay - 45, "А. Умовне інтегрування (Clamping / Conditional Integration)", size=13, color=INK, anchor="start", bold=True))

    # Вхідна помилка
    frags.append(text(40, ay, "e(t)", size=12, color=INK, bold=True))
    frags.append(arrow(65, ay, 120, ay, color=LINE, sw=1.5))

    # Вузол розгалуження
    frags.append(circle(120, ay, 3, fill=LINE, stroke=LINE))

    # Гілка P
    frags.append(arrow(120, ay, 120, ay - 35, color=LINE, sw=1.5))
    frags.append(arrow(120, ay - 35, 170, ay - 35, color=LINE, sw=1.5))
    frags.append(textbox(205, ay - 35, "Kp", size=12, pad=6, fill="#eff6ff", stroke=NEG)[0])
    frags.append(arrow(240, ay - 35, 450, ay - 35, color=LINE, sw=1.5))

    # Гілка I через ключ Clamping
    frags.append(arrow(120, ay, 160, ay, color=LINE, sw=1.5))
    frags.append(textbox(195, ay, "Ключ\nClamping", size=10, pad=5, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    frags.append(arrow(230, ay, 270, ay, color=LINE, sw=1.5))
    frags.append(textbox(310, ay, "∫ (1/Ti) dt", size=11, pad=6, fill="#ecfdf5", stroke=FIELD)[0])
    frags.append(arrow(350, ay, 450, ay, color=LINE, sw=1.5))

    # Гілка D
    frags.append(arrow(120, ay, 120, ay + 35, color=LINE, sw=1.5))
    frags.append(arrow(120, ay + 35, 170, ay + 35, color=LINE, sw=1.5))
    frags.append(textbox(215, ay + 35, "Kd · s/(1+sTf)", size=10, pad=5, fill="#fdf4ff", stroke="#9333ea")[0])
    frags.append(arrow(260, ay + 35, 450, ay + 35, color=LINE, sw=1.5))

    # Суматор регулятора
    frags.append(circle(460, ay, 14, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(460, ay + 4, "Σ", size=14, bold=True))
    frags.append(arrow(474, ay, 540, ay, color=LINE, sw=1.5))
    frags.append(text(505, ay - 8, "u(t)", size=11, color=INK))

    # Блок насичення sat(u)
    frags.append(textbox(580, ay, "Насичення\nsat(·)", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True)[0])
    frags.append(arrow(620, ay, 710, ay, color=LINE, sw=1.8))
    frags.append(text(665, ay - 8, "u_sat(t)", size=11, color=POS, bold=True))

    # Логічний зв'язок керування ключем Clamping
    frags.append(circle(505, ay, 3, fill=LINE, stroke=LINE))
    frags.append(line(505, ay, 505, ay + 65, color="#d97706", sw=1.2, dash="3,2"))
    frags.append(line(505, ay + 65, 195, ay + 65, color="#d97706", sw=1.2, dash="3,2"))
    frags.append(arrow(195, ay + 65, 195, ay + 22, color="#d97706", sw=1.2))
    frags.append(text(350, ay + 75, "Логіка блокування: (u ≥ u_max ∧ e > 0) ∨ (u ≤ u_min ∧ e < 0)", size=10, color="#b45309", bold=True))

    # Розділювальна лінія між частинами А і Б
    frags.append(line(30, 240, 790, 240, color="#e2e8f0", sw=1.5))

    # ── БЛОК Б: Зворотний перерахунок (Back-Calculation) ──────────────────────
    by = 350
    frags.append(text(20, by - 70, "Б. Зворотний перерахунок (Back-Calculation / Tracking Loop)", size=13, color=INK, anchor="start", bold=True))

    # Вхідна помилка e(t)
    frags.append(text(40, by, "e(t)", size=12, color=INK, bold=True))
    frags.append(arrow(65, by, 120, by, color=LINE, sw=1.5))
    frags.append(circle(120, by, 3, fill=LINE, stroke=LINE))

    # Пропорційний канал
    frags.append(arrow(120, by, 120, by - 40, color=LINE, sw=1.5))
    frags.append(arrow(120, by - 40, 170, by - 40, color=LINE, sw=1.5))
    frags.append(textbox(205, by - 40, "Kp", size=12, pad=6, fill="#eff6ff", stroke=NEG)[0])
    frags.append(arrow(240, by - 40, 450, by - 40, color=LINE, sw=1.5))

    # Інтегральний канал з локальним суматором зворотного зв'язку
    frags.append(textbox(160, by, "Kp / Ti", size=11, pad=5, fill="#eff6ff", stroke=NEG)[0])
    frags.append(arrow(195, by, 235, by, color=LINE, sw=1.5))

    # Локальний суматор перед інтегратором
    frags.append(circle(245, by, 10, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(245, by + 3.5, "Σ", size=11, bold=True))
    frags.append(arrow(255, by, 295, by, color=LINE, sw=1.5))

    # Інтегратор 1/s
    frags.append(textbox(325, by, "∫ dt", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)[0])
    frags.append(arrow(355, by, 450, by, color=LINE, sw=1.5))

    # Суматор регулятора
    frags.append(circle(460, by, 14, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(460, by + 4, "Σ", size=14, bold=True))
    frags.append(arrow(474, by, 540, by, color=LINE, sw=1.5))
    frags.append(text(505, by - 8, "u(t)", size=11, color=INK))

    # Блок насичення
    frags.append(textbox(580, by, "Насичення\nsat(·)", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True)[0])
    frags.append(arrow(620, by, 710, by, color=LINE, sw=1.8))
    frags.append(text(665, by - 8, "u_sat(t)", size=11, color=POS, bold=True))

    # Контур зворотного перерахунку: різниця (sat(u) - u)
    frags.append(circle(645, by, 3, fill=LINE, stroke=LINE))
    frags.append(circle(505, by, 3, fill=LINE, stroke=LINE))

    # Віднімач різниці насичення
    frags.append(line(645, by, 645, by + 60, color=LINE, sw=1.2))
    frags.append(line(505, by, 505, by + 45, color=LINE, sw=1.2))
    frags.append(arrow(505, by + 45, 595, by + 45, color=LINE, sw=1.2))
    frags.append(arrow(645, by + 60, 605, by + 60, color=LINE, sw=1.2))

    frags.append(circle(600, by + 52, 10, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(600, by + 55, "Σ", size=11, bold=True))
    frags.append(text(615, by + 65, "+", size=9, color=LINE))
    frags.append(text(585, by + 42, "−", size=9, color=LINE))

    # Ланка підсилення 1/Tt
    frags.append(arrow(590, by + 52, 450, by + 52, color=LINE, sw=1.5))
    frags.append(textbox(410, by + 52, "1 / Tt", size=11, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    frags.append(arrow(370, by + 52, 245, by + 52, color=LINE, sw=1.5))
    frags.append(arrow(245, by + 52, 245, by + 10, color=LINE, sw=1.5))
    frags.append(text(253, by + 20, "+", size=10, color=LINE))
    frags.append(text(390, by + 75, "Сигнал неузгодженості: e_s = sat(u) − u ≤ 0", size=10, color="#b45309", bold=True))

    return render(os.path.join(IMG_DIR, "anti-windup-topologies.svg"), w, h, *frags)


def fig_step_response_comparison():
    """Фігура 3: Порівняння перехідних процесів з різними методами Anti-Windup."""
    w, h = 820, 460
    frags = []

    frags.append(text(410, 24, "Порівняння перехідних процесів при великому стрибку уставки", size=16, bold=True))

    # Спільні межі графіка
    gx0, gx1 = 100, 770
    gw = gx1 - gx0
    gy_top, gy_bot = 60, 360
    gh = gy_bot - gy_top

    # Вісі координат
    frags.append(line(gx0, gy_bot, gx1, gy_bot, color=LINE, sw=1.5))
    frags.append(line(gx0, gy_bot, gx0, gy_top, color=LINE, sw=1.5))
    frags.append(text(gx0 - 12, (gy_top + gy_bot) / 2, "Вихід процесу y(t)", size=13, color=INK, anchor="end"))
    frags.append(text(gx1, gy_bot + 24, "Час t (секунди)", size=12, color=INK, anchor="end"))

    # Сітка та мітки по осі Y
    sp_y = gy_top + int(gh * 0.35)   # Рівень уставки r(t) = 1.0
    frags.append(line(gx0, sp_y, gx1, sp_y, color=POS, sw=1.2, dash="4,3"))
    frags.append(text(gx0 - 10, sp_y + 4, "1.0 (Уставка SP)", size=11, color=POS, anchor="end", bold=True))
    frags.append(text(gx0 - 10, gy_bot + 4, "0.0", size=11, color=MUTED, anchor="end"))

    # Мітки часу по осі X
    for tx, sec in [(gx0, "0"), (gx0 + gw*0.2, "2"), (gx0 + gw*0.4, "4"), (gx0 + gw*0.6, "6"), (gx0 + gw*0.8, "8"), (gx1, "10")]:
        frags.append(line(tx, gy_bot, tx, gy_bot + 5, color=LINE, sw=1.0))
        frags.append(text(tx, gy_bot + 18, sec, size=11, color=MUTED))

    # 1. Траєкторія без обмеження (Ідеальна лінійна система)
    ideal_path = (
        f'<path d="M {gx0} {gy_bot} '
        f'Q {gx0 + 60} {gy_bot - 40} {gx0 + 120} {sp_y - 20} '
        f'Q {gx0 + 180} {sp_y + 10} {gx0 + 260} {sp_y} '
        f'L {gx1} {sp_y}" '
        f'fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="3,3"/>'
    )
    frags.append(ideal_path)

    # 2. Траєкторія з насиченням БЕЗ Anti-Windup (катастрофічний овершут)
    no_aw_peak_x = gx0 + int(gw * 0.55)
    no_aw_peak_y = gy_top + 10
    no_aw_path = (
        f'<path d="M {gx0} {gy_bot} '
        f'L {gx0 + int(gw * 0.35)} {sp_y} '
        f'Q {no_aw_peak_x} {no_aw_peak_y - 30} {gx0 + int(gw * 0.75)} {sp_y + 25} '
        f'Q {gx0 + int(gw * 0.88)} {sp_y - 10} {gx1} {sp_y}" '
        f'fill="none" stroke="{POS}" stroke-width="2.6"/>'
    )
    frags.append(no_aw_path)

    # 3. Траєкторія з Clamping (Умовне інтегрування)
    clamp_path = (
        f'<path d="M {gx0} {gy_bot} '
        f'L {gx0 + int(gw * 0.35)} {sp_y + 10} '
        f'Q {gx0 + int(gw * 0.45)} {sp_y - 8} {gx0 + int(gw * 0.60)} {sp_y} '
        f'L {gx1} {sp_y}" '
        f'fill="none" stroke="#d97706" stroke-width="2.4"/>'
    )
    frags.append(clamp_path)

    # 4. Траєкторія з Back-Calculation (Зворотний перерахунок)
    bc_path = (
        f'<path d="M {gx0} {gy_bot} '
        f'L {gx0 + int(gw * 0.34)} {sp_y + 18} '
        f'Q {gx0 + int(gw * 0.44)} {sp_y - 2} {gx0 + int(gw * 0.55)} {sp_y} '
        f'L {gx1} {sp_y}" '
        f'fill="none" stroke="{FIELD}" stroke-width="2.4"/>'
    )
    frags.append(bc_path)

    # Пояснювальна легенда знизу
    leg_y = 395
    # Лінійна
    frags.append(line(110, leg_y, 140, leg_y, color=MUTED, sw=1.8, dash="3,3"))
    frags.append(text(145, leg_y + 4, "Ідеальна лінійна (без ліміту)", size=11, color=MUTED, anchor="start"))

    # Без Anti-Windup
    frags.append(line(310, leg_y, 340, leg_y, color=POS, sw=2.6))
    frags.append(text(345, leg_y + 4, "Без Anti-Windup (Overshoot ~65%)", size=11, color=POS, anchor="start", bold=True))

    # Clamping
    frags.append(line(550, leg_y, 580, leg_y, color="#d97706", sw=2.4))
    frags.append(text(585, leg_y + 4, "Clamping (Overshoot ~5%)", size=11, color="#d97706", anchor="start", bold=True))

    # Back-Calculation
    frags.append(line(310, leg_y + 30, 340, leg_y + 30, color=FIELD, sw=2.4))
    frags.append(text(345, leg_y + 34, "Back-Calculation (Overshoot < 2%, швидке заспокоєння)", size=11, color=FIELD, anchor="start", bold=True))

    return render(os.path.join(IMG_DIR, "step-response-comparison.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_windup_mechanism()
    fig_anti_windup_topologies()
    fig_step_response_comparison()
    print("Всі SVG-фігури згенеровано успішно.")
