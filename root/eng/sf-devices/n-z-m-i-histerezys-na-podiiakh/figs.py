# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'N з M і гістерезис на подіях'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище: root/eng/sf-devices/n-z-m-i-histerezys-na-podiiakh -> ../../../../scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_timing_diagram():
    """Часова діаграма фільтрації сигналу алгоритмом N-з-M з асиметричним гістерезисом."""
    W, H = 940, 480
    frags = []

    # Заголовок блоків
    frags.append(text(W / 2, 28, "Часова діаграма фільтрації дискретних подій N-з-M (M=8, Non=6, Noff=2)", size=16, bold=True))

    # Сітка та часова шкала
    t_start_x = 180
    t_end_x = 880
    dt = (t_end_x - t_start_x) / 20.0

    # Вертикальні пунктирні лінії тактування
    for i in range(21):
        x = t_start_x + i * dt
        frags.append(line(x, 50, x, 430, color="#e5e7eb", sw=1.0, dash="3,3"))
        if i % 2 == 0:
            frags.append(text(x, 445, f"t{i}", size=11, color=MUTED))

    # Вісь часу знизу
    frags.append(arrow(t_start_x - 10, 430, t_end_x + 30, 430, color=LINE, sw=1.5))
    frags.append(text(t_end_x + 40, 434, "t", size=13, bold=True, color=INK))

    # ── 1. Сирий зашумлений сигнал (Raw Input) ────────────────────────────────
    y_raw_base = 110
    frags.append(text(90, y_raw_base - 15, "Сирий вхід", size=13, bold=True, anchor="middle", color=INK))
    frags.append(text(90, y_raw_base + 3, "(GPIO / шум)", size=11, color=MUTED, anchor="middle"))

    # Базова лінія 0
    frags.append(line(t_start_x, y_raw_base, t_end_x, y_raw_base, color="#cbd5e1", sw=1.0))

    # Сирий сигнал з імпульсним шумом, брязкотом і провалами
    raw_points = [
        (0, 0), (2, 0), (2.1, 1), (2.4, 0), (4, 0), (4.2, 1), (4.5, 0),
        (6, 0), (6.1, 1), (6.3, 0), (6.5, 1), (6.7, 0), (7, 1),
        (8.5, 1), (8.7, 0), (8.9, 1),
        (13, 1), (13.2, 0), (13.4, 1), (13.6, 0), (14, 0),
        (16, 0), (16.2, 1), (16.4, 0), (20, 0)
    ]
    raw_path_d = []
    prev_x = t_start_x
    prev_y = y_raw_base
    for t_val, level in raw_points:
        curr_x = t_start_x + t_val * dt
        curr_y = y_raw_base - 32 if level == 1 else y_raw_base
        raw_path_d.append(f"L {curr_x:.1f} {prev_y:.1f}")
        raw_path_d.append(f"L {curr_x:.1f} {curr_y:.1f}")
        prev_x = curr_x
        prev_y = curr_y
    raw_path_d.append(f"L {t_end_x:.1f} {prev_y:.1f}")
    raw_svg_path = f'<path d="M {t_start_x:.1f} {y_raw_base:.1f} ' + " ".join(raw_path_d) + f'" fill="none" stroke="{POS}" stroke-width="2.2"/>'
    frags.append(raw_svg_path)

    # Підписи шумів
    frags.append(text(t_start_x + 3.3 * dt, y_raw_base - 38, "Імпульсний шум", size=11, color=POS, bold=True))
    frags.append(text(t_start_x + 6.6 * dt, y_raw_base - 38, "Брязкіт контакту", size=11, color=POS))
    frags.append(text(t_start_x + 8.8 * dt, y_raw_base - 38, "Провал", size=11, color=POS))

    # ── 2. Лічильник одиниць у вікні (Popcount S[k]) ───────────────────────────
    y_pop_base = 260
    y_pop_top = 160
    frags.append(text(90, 205, "Кількість '1' у вікні", size=13, bold=True, anchor="middle", color=INK))
    frags.append(text(90, 223, "Popcount S[k] (0..8)", size=11, color=MUTED, anchor="middle"))

    # Смуга гістерезису між Noff=2 та Non=6
    y_non = y_pop_base - (6 / 8.0) * (y_pop_base - y_pop_top)
    y_noff = y_pop_base - (2 / 8.0) * (y_pop_base - y_pop_top)
    h_band = y_noff - y_non
    frags.append(rect(t_start_x, y_non, t_end_x - t_start_x, h_band, fill="#fef3c7", stroke="none", rx=0))

    # Лінії порогів
    frags.append(line(t_start_x, y_non, t_end_x, y_non, color=POS, sw=1.5, dash="5,3"))
    frags.append(text(t_start_x - 12, y_non + 4, "Non = 6", size=11, bold=True, color=POS, anchor="end"))

    frags.append(line(t_start_x, y_noff, t_end_x, y_noff, color=NEG, sw=1.5, dash="5,3"))
    frags.append(text(t_start_x - 12, y_noff + 4, "Noff = 2", size=11, bold=True, color=NEG, anchor="end"))

    # Базова лінія 0
    frags.append(line(t_start_x, y_pop_base, t_end_x, y_pop_base, color="#94a3b8", sw=1.2))
    frags.append(text(t_start_x - 12, y_pop_base + 4, "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(t_start_x - 12, y_pop_top + 4, "8", size=11, color=MUTED, anchor="end"))

    # Пояснення мертвої зони
    frags.append(text(t_start_x + 50, y_non + 22, "Мертва зона гістерезису (стан утримується)", size=11, color="#b45309", italic=True, anchor="start"))

    # Графік popcount S[k] по тактах
    pop_values = [
        0, 0, 1, 0, 1, 0, 1, 3, 5, 6, 7, 7, 7, 6, 4, 2, 1, 0, 1, 0, 0
    ]
    pop_path_d = []
    for i, p_val in enumerate(pop_values):
        px = t_start_x + i * dt
        py = y_pop_base - (p_val / 8.0) * (y_pop_base - y_pop_top)
        if i == 0:
            pop_path_d.append(f"M {px:.1f} {py:.1f}")
        else:
            prev_px = t_start_x + (i - 1) * dt
            pop_path_d.append(f"L {px:.1f} {prev_py:.1f}")
            pop_path_d.append(f"L {px:.1f} {py:.1f}")
        prev_py = py
    frags.append(f'<path d="{" ".join(pop_path_d)}" fill="none" stroke="#0284c7" stroke-width="2.5"/>')

    # Точки перемикання на графіку popcount
    # Активація в t9 (S=6 >= Non)
    act_x = t_start_x + 9 * dt
    frags.append(circle(act_x, y_non, 4.5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(act_x, y_non - 10, "Активація (S ≥ 6)", size=11, bold=True, color=POS))

    # Деактивація в t15 (S=2 <= Noff)
    deact_x = t_start_x + 15 * dt
    frags.append(circle(deact_x, y_noff, 4.5, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(text(deact_x, y_noff + 16, "Скидання (S ≤ 2)", size=11, bold=True, color=NEG))

    # ── 3. Відфільтрований вихід (Filtered Output) ───────────────────────────
    y_out_base = 380
    frags.append(text(90, y_out_base - 15, "Очищений вихід", size=13, bold=True, anchor="middle", color=FIELD))
    frags.append(text(90, y_out_base + 3, "Y[k] (N-з-M стан)", size=11, color=MUTED, anchor="middle"))

    # Базова лінія 0
    frags.append(line(t_start_x, y_out_base, t_end_x, y_out_base, color="#cbd5e1", sw=1.0))

    # Траєкторія очищеного сигналу: 0 до t9, потім 1 до t15, потім 0
    out_points = [
        (0, 0), (9, 0), (9, 1), (15, 1), (15, 0), (20, 0)
    ]
    out_path_d = []
    for i, (t_val, lvl) in enumerate(out_points):
        ox = t_start_x + t_val * dt
        oy = y_out_base - 32 if lvl == 1 else y_out_base
        if i == 0:
            out_path_d.append(f"M {ox:.1f} {oy:.1f}")
        else:
            out_path_d.append(f"L {ox:.1f} {oy:.1f}")
    frags.append(f'<path d="{" ".join(out_path_d)}" fill="none" stroke="{FIELD}" stroke-width="3.0"/>')

    # Підписи захисту
    frags.append(text(t_start_x + 3.0 * dt, y_out_base - 12, "Шум придушено", size=11, bold=True, color=FIELD))
    frags.append(text(t_start_x + 12.0 * dt, y_out_base - 40, "Стабільний активний стан", size=11, bold=True, color=FIELD))
    frags.append(text(t_start_x + 18.0 * dt, y_out_base - 12, "Шум придушено", size=11, bold=True, color=FIELD))

    # Вертикальні маркери затримки реакції
    frags.append(line(act_x, y_pop_top - 10, act_x, y_out_base + 10, color=POS, sw=1.2, dash="3,3"))
    frags.append(line(deact_x, y_pop_top - 10, deact_x, y_out_base + 10, color=NEG, sw=1.2, dash="3,3"))

    return render(os.path.join(OUT, "n-of-m-sliding-window-timing.svg"), W, H, *frags)


def fig_transfer_curve():
    """Статична характеристика та петля гістерезису в просторі подій."""
    W, H = 880, 460
    frags = []

    frags.append(text(W / 2, 28, "Петля гістерезису в просторі відліків N-з-M", size=16, bold=True))

    cx = 440
    cy = 240
    w_box = 560
    h_box = 240

    x_min = cx - w_box / 2
    x_max = cx + w_box / 2
    y_zero = cy + h_box / 2
    y_one = cy - h_box / 2

    # Сітка координат
    frags.append(line(x_min, y_zero, x_max + 30, y_zero, color=LINE, sw=1.8))
    frags.append(line(x_min, y_zero, x_min, y_one - 30, color=LINE, sw=1.8))

    # Стрілки осей
    frags.append(arrow(x_max + 20, y_zero, x_max + 35, y_zero, color=LINE, sw=1.8))
    frags.append(arrow(x_min, y_one - 20, x_min, y_one - 35, color=LINE, sw=1.8))

    frags.append(text(x_max + 40, y_zero + 18, "Кількість подій у вікні S = Popcount(W)", size=12, bold=True, anchor="middle", color=INK))
    frags.append(text(x_min - 15, y_one - 25, "Вихід Y", size=12, bold=True, anchor="end", color=INK))

    # Мітки по Y
    frags.append(text(x_min - 12, y_zero + 4, "0", size=12, bold=True, anchor="end", color=INK))
    frags.append(text(x_min - 12, y_one + 4, "1", size=12, bold=True, anchor="end", color=INK))
    frags.append(line(x_min - 5, y_one, x_min, y_one, color=LINE, sw=1.5))

    # Шкала X (0 до M=8)
    dx = w_box / 8.0
    for k in range(9):
        xk = x_min + k * dx
        frags.append(line(xk, y_zero, xk, y_zero + 6, color=LINE, sw=1.2))
        frags.append(text(xk, y_zero + 20, str(k), size=12, color=INK))

    # Пороги Noff=2 та Non=6
    x_noff = x_min + 2 * dx
    x_non = x_min + 6 * dx

    # Мертва зона (заливка)
    frags.append(rect(x_noff, y_one, x_non - x_noff, y_zero - y_one, fill="#fef3c7", stroke="none", rx=0))
    frags.append(text((x_noff + x_non) / 2, cy - 20, "Мертва зона гістерезису", size=13, bold=True, color="#b45309"))
    frags.append(text((x_noff + x_non) / 2, cy + 2, "ΔN = Non − Noff = 4", size=12, color="#b45309"))
    frags.append(text((x_noff + x_non) / 2, cy + 22, "(стан не змінюється)", size=11, color=MUTED, italic=True))

    # Вертикальні пунктири для порогів
    frags.append(line(x_noff, y_zero, x_noff, y_one, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(x_non, y_zero, x_non, y_one, color=POS, sw=1.5, dash="4,3"))

    frags.append(text(x_noff, y_zero + 36, "Noff = 2", size=12, bold=True, color=NEG))
    frags.append(text(x_non, y_zero + 36, "Non = 6", size=12, bold=True, color=POS))

    # Верхня гілка (перехід 0 -> 1 при русі вправо)
    frags.append(line(x_min, y_zero, x_non, y_zero, color=POS, sw=3.0))
    frags.append(line(x_non, y_zero, x_non, y_one, color=POS, sw=3.0))
    frags.append(line(x_non, y_one, x_max, y_one, color=POS, sw=3.0))

    # Стрілочка на прямій гілці
    frags.append(arrow(x_min + 3.5 * dx, y_zero - 8, x_min + 4.5 * dx, y_zero - 8, color=POS, sw=1.8))
    frags.append(text(x_min + 4.0 * dx, y_zero - 18, "Зростання S (вмикання)", size=11, bold=True, color=POS))

    # Нижня гілка (перехід 1 -> 0 при русі вліво)
    frags.append(line(x_max, y_one, x_noff, y_one, color=NEG, sw=2.5))
    frags.append(line(x_noff, y_one, x_noff, y_zero, color=NEG, sw=2.5))
    frags.append(line(x_noff, y_zero, x_min, y_zero, color=NEG, sw=2.5))

    # Стрілочка на зворотній гілці
    frags.append(arrow(x_min + 4.5 * dx, y_one + 8, x_min + 3.5 * dx, y_one + 8, color=NEG, sw=1.8))
    frags.append(text(x_min + 4.0 * dx, y_one + 22, "Спад S (вимикання)", size=11, bold=True, color=NEG))

    # Пояснення блоків
    frags.append(textbox(200, 390, "Стан 0 (IDLE):\nАктивується лише при S ≥ 6", size=11, fill="#eff6ff", stroke=POS, pad=6)[0])
    frags.append(textbox(680, 390, "Стан 1 (ACTIVE):\nСкидається лише при S ≤ 2", size=11, fill="#f0fdf4", stroke=NEG, pad=6)[0])

    return render(os.path.join(OUT, "event-hysteresis-transfer-curve.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_timing_diagram()
    fig_transfer_curve()
    print("SVG figures successfully generated.")
