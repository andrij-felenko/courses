# -*- coding: utf-8 -*-
"""Фігури до теми «ARQ: автоматичний запит на повтор».
Запуск: python figs.py  → створює SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Додаткові кольори палітри
COLOR_ACK     = "#27ae60"  # зелений: успішне підтвердження
COLOR_FRAME   = "#2457d6"  # синій: звичайний кадр даних
COLOR_LOSS    = "#c0392b"  # червоний: втрата / пошкодження / NACK
COLOR_BUFFER  = "#e67e22"  # помаранчевий: буфер очікування / LLR
COLOR_BG_BOX  = "#f8fafc"  # фон карток
COLOR_BORDER  = "#cbd5e1"  # межа карток


# ── 1. Порівняння часових діаграм Stop-and-Wait, Go-Back-N та Selective Repeat ─────
def fig_arq_timeline_comparison():
    W, H = 1000, 680
    f = []

    # Три колонки для трьох протоколів
    cols = [
        ("Stop-and-Wait ARQ", 30, 310, "SW"),
        ("Go-Back-N ARQ (N=4)", 350, 310, "GBN"),
        ("Selective Repeat ARQ (W=4)", 670, 310, "SR"),
    ]

    for title, x0, w_col, proto in cols:
        f.append(rect(x0, 45, w_col, 615, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
        f.append(text(x0 + w_col / 2, 70, title, size=13, bold=True, color=INK))

        tx_x = x0 + 55
        rx_x = x0 + w_col - 55
        y_top = 105
        y_bot = 635

        # Лінії часу TX та RX
        f.append(line(tx_x, y_top, tx_x, y_bot, color=LINE, sw=1.5))
        f.append(line(rx_x, y_top, rx_x, y_bot, color=LINE, sw=1.5))
        f.append(text(tx_x, y_top - 12, "TX", size=11, bold=True, color=LINE))
        f.append(text(rx_x, y_top - 12, "RX", size=11, bold=True, color=LINE))

        if proto == "SW":
            # Успішний кадр 0
            f.append(arrow(tx_x, 115, rx_x, 155, color=COLOR_FRAME, sw=2))
            f.append(text(tx_x - 18, 120, "F0", size=10, bold=True, color=COLOR_FRAME))
            f.append(arrow(rx_x, 155, tx_x, 195, color=COLOR_ACK, sw=2))
            f.append(text(rx_x + 20, 160, "ACK0", size=10, bold=True, color=COLOR_ACK))

            # Втрачений кадр 1
            f.append(line(tx_x, 210, tx_x + 95, 248, color=COLOR_LOSS, sw=2))
            f.append(text(tx_x + 105, 252, "×", size=18, bold=True, color=COLOR_LOSS))
            f.append(text(tx_x - 18, 215, "F1", size=10, bold=True, color=COLOR_LOSS))

            # Таймаут RTO
            f.append(line(tx_x - 30, 210, tx_x - 30, 340, color=COLOR_LOSS, sw=1.5, dash="3,3"))
            f.append(line(tx_x - 35, 210, tx_x - 25, 210, color=COLOR_LOSS, sw=1.5))
            f.append(line(tx_x - 35, 340, tx_x - 25, 340, color=COLOR_LOSS, sw=1.5))
            f.append(text(tx_x - 42, 280, "RTO", size=9, bold=True, color=COLOR_LOSS, anchor="end"))

            # Повтор кадру 1
            f.append(arrow(tx_x, 345, rx_x, 385, color=COLOR_FRAME, sw=2))
            f.append(text(tx_x - 18, 350, "F1", size=10, bold=True, color=COLOR_FRAME))
            f.append(arrow(rx_x, 385, tx_x, 425, color=COLOR_ACK, sw=2))
            f.append(text(rx_x + 20, 390, "ACK1", size=10, bold=True, color=COLOR_ACK))

            # Кадр 0 наступний
            f.append(arrow(tx_x, 440, rx_x, 480, color=COLOR_FRAME, sw=2))
            f.append(text(tx_x - 18, 445, "F0", size=10, bold=True, color=COLOR_FRAME))
            f.append(arrow(rx_x, 480, tx_x, 520, color=COLOR_ACK, sw=2))
            f.append(text(rx_x + 20, 485, "ACK0", size=10, bold=True, color=COLOR_ACK))

            f.append(fitbox(x0 + 10, 545, w_col - 20, 95,
                            "Простій = 2·t_prop\nПри втраті: простій на\nповний таймаут RTO\nЕфективність: η ~ 1/(1+2a)",
                            size=10, fill="#ffffff", stroke=COLOR_BORDER))

        elif proto == "GBN":
            # Безперервна відправка F0, F1, F2, F3
            f.append(arrow(tx_x, 115, rx_x, 155, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 118, "F0", size=9, bold=True, color=COLOR_FRAME))

            # F1 втрачено
            f.append(line(tx_x, 140, tx_x + 95, 178, color=COLOR_LOSS, sw=1.8))
            f.append(text(tx_x + 105, 182, "×", size=16, bold=True, color=COLOR_LOSS))
            f.append(text(tx_x - 16, 143, "F1", size=9, bold=True, color=COLOR_LOSS))

            # F2 і F3 відправлені
            f.append(arrow(tx_x, 165, rx_x, 205, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 168, "F2", size=9, bold=True, color=COLOR_FRAME))

            f.append(arrow(tx_x, 190, rx_x, 230, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 193, "F3", size=9, bold=True, color=COLOR_FRAME))

            # RX підтверджує F0
            f.append(arrow(rx_x, 155, tx_x, 195, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 158, "ACK0", size=9, bold=True, color=COLOR_ACK))

            # RX відкидає F2 і F3 (не за порядком)
            f.append(text(rx_x + 6, 210, "Drop F2", size=9, bold=True, color=COLOR_LOSS, anchor="start"))
            f.append(text(rx_x + 6, 235, "Drop F3", size=9, bold=True, color=COLOR_LOSS, anchor="start"))

            # Таймаут для F1 спливає на TX
            f.append(line(tx_x - 28, 140, tx_x - 28, 270, color=COLOR_LOSS, sw=1.5, dash="3,3"))
            f.append(text(tx_x - 33, 205, "RTO(F1)", size=10, bold=True, color=COLOR_LOSS, anchor="end"))

            # Груповий повтор F1, F2, F3, F4
            f.append(arrow(tx_x, 275, rx_x, 315, color=COLOR_LOSS, sw=1.8))
            f.append(text(tx_x - 16, 278, "F1", size=9, bold=True, color=COLOR_LOSS))

            f.append(arrow(tx_x, 300, rx_x, 340, color=COLOR_LOSS, sw=1.8))
            f.append(text(tx_x - 16, 303, "F2", size=9, bold=True, color=COLOR_LOSS))

            f.append(arrow(tx_x, 325, rx_x, 365, color=COLOR_LOSS, sw=1.8))
            f.append(text(tx_x - 16, 328, "F3", size=9, bold=True, color=COLOR_LOSS))

            f.append(arrow(tx_x, 350, rx_x, 390, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 353, "F4", size=9, bold=True, color=COLOR_FRAME))

            # RX успішно приймає F1, F2...
            f.append(arrow(rx_x, 315, tx_x, 355, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 318, "ACK1", size=9, bold=True, color=COLOR_ACK))

            f.append(arrow(rx_x, 340, tx_x, 380, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 343, "ACK2", size=9, bold=True, color=COLOR_ACK))

            f.append(fitbox(x0 + 10, 545, w_col - 20, 95,
                            "Приймач без буфера\nВідкидає всі кадри після збою\nПовтор ВСІХ N кадрів\nЧутливий до P_f при вел. N",
                            size=10, fill="#ffffff", stroke=COLOR_BORDER))

        elif proto == "SR":
            # Відправка F0, F1, F2, F3
            f.append(arrow(tx_x, 115, rx_x, 155, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 118, "F0", size=9, bold=True, color=COLOR_FRAME))

            # F1 втрачено
            f.append(line(tx_x, 140, tx_x + 95, 178, color=COLOR_LOSS, sw=1.8))
            f.append(text(tx_x + 105, 182, "×", size=16, bold=True, color=COLOR_LOSS))
            f.append(text(tx_x - 16, 143, "F1", size=9, bold=True, color=COLOR_LOSS))

            # F2 і F3 відправлені
            f.append(arrow(tx_x, 165, rx_x, 205, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 168, "F2", size=9, bold=True, color=COLOR_FRAME))

            f.append(arrow(tx_x, 190, rx_x, 230, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 193, "F3", size=9, bold=True, color=COLOR_FRAME))

            # RX підтверджує F0
            f.append(arrow(rx_x, 155, tx_x, 195, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 158, "ACK0", size=9, bold=True, color=COLOR_ACK))

            # RX буферизує F2 і F3 та надсилає SACK
            f.append(arrow(rx_x, 205, tx_x, 245, color=COLOR_BUFFER, sw=1.8))
            f.append(text(rx_x + 20, 208, "SACK2", size=9, bold=True, color=COLOR_BUFFER))

            f.append(arrow(rx_x, 230, tx_x, 270, color=COLOR_BUFFER, sw=1.8))
            f.append(text(rx_x + 20, 233, "SACK3", size=9, bold=True, color=COLOR_BUFFER))

            # Таймаут або NACK для F1
            f.append(line(tx_x - 28, 140, tx_x - 28, 280, color=COLOR_LOSS, sw=1.5, dash="3,3"))
            f.append(text(tx_x - 33, 210, "RTO(F1)", size=10, bold=True, color=COLOR_LOSS, anchor="end"))

            # Вибірковий повтор ТІЛЬКИ кадру F1!
            f.append(arrow(tx_x, 285, rx_x, 325, color=COLOR_LOSS, sw=2))
            f.append(text(tx_x - 16, 288, "F1*", size=9, bold=True, color=COLOR_LOSS))

            # Відправка нового кадру F4
            f.append(arrow(tx_x, 315, rx_x, 355, color=COLOR_FRAME, sw=1.8))
            f.append(text(tx_x - 16, 318, "F4", size=9, bold=True, color=COLOR_FRAME))

            # RX отримує F1 і видає впорядкований блок (F0,F1,F2,F3)
            f.append(arrow(rx_x, 325, tx_x, 365, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 328, "ACK3", size=9, bold=True, color=COLOR_ACK))

            f.append(arrow(rx_x, 355, tx_x, 395, color=COLOR_ACK, sw=1.8))
            f.append(text(rx_x + 20, 358, "ACK4", size=9, bold=True, color=COLOR_ACK))

            f.append(fitbox(x0 + 10, 545, w_col - 20, 95,
                            "Буфер приймача W_rx\nПовтор ТІЛЬКИ втраченого F1\nКадри F2, F3 не передаються знову\nЕфективність: η = 1 - P_f",
                            size=10, fill="#ffffff", stroke=COLOR_BORDER))

    return render(os.path.join(IMG, "arq-timeline-comparison.svg"), W, H, *f,
                  title="Порівняння часових послідовностей протоколів ARQ")


# ── 2. Механіка ковзного вікна та нумерація послідовностей ─────────────────────
def fig_sliding_window_mechanics():
    W, H = 880, 540
    f = []

    # Загальний контейнер TX вікна
    f.append(rect(30, 45, 820, 225, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
    f.append(text(50, 72, "Структура ковзного вікна передавача (TX Window, N = 6)", size=13, bold=True, color=INK, anchor="start"))

    # Кадри в послідовності від 0 до 15
    cell_w = 46
    cell_h = 42
    start_x = 55
    y_cells = 95

    # 4 категорії кадрів: Підтверджені (0..2), У польоті (3..5), Готові до відправки (6..8), Недоступні (9..13)
    categories = [
        (0, 3, "#e2e8f0", "#64748b", "Підтверджені (ACK)"),
        (3, 6, "#fee2e2", COLOR_LOSS, "У польоті (Unacked)"),
        (6, 9, "#dbeafe", COLOR_FRAME, "Дозволені до відправки"),
        (9, 15, "#f1f5f9", "#94a3b8", "Поза вікном (Заборонені)"),
    ]

    for idx in range(15):
        cx = start_x + idx * (cell_w + 5)
        # Колір
        fill_c = "#f1f5f9"
        stroke_c = "#94a3b8"
        for s_idx, e_idx, fc, sc, _ in categories:
            if s_idx <= idx < e_idx:
                fill_c = fc
                stroke_c = sc
                break

        f.append(rect(cx, y_cells, cell_w, cell_h, fill=fill_c, stroke=stroke_c, sw=2, rx=4))
        f.append(text(cx + cell_w / 2, y_cells + 26, str(idx), size=13, bold=True, color=INK))

    # Рамка вікна передавача W_TX = 6 (від кадру 3 до 8 включно)
    win_x = start_x + 3 * (cell_w + 5) - 3
    win_w = 6 * (cell_w + 5) + 1
    f.append(rect(win_x, y_cells - 5, win_w, cell_h + 10, fill="none", stroke=COLOR_FRAME, sw=3, rx=6))
    f.append(text(win_x + win_w / 2, y_cells + cell_h + 24, "Ковзне вікно передавача W_tx = 6 кадрів", size=11, bold=True, color=COLOR_FRAME))

    # Стрілки вказівників
    ptr_base_x = start_x + 3 * (cell_w + 5) + cell_w / 2
    ptr_next_x = start_x + 6 * (cell_w + 5) + cell_w / 2
    f.append(arrow(ptr_base_x, y_cells + cell_h + 48, ptr_base_x, y_cells + cell_h + 12, color=COLOR_LOSS, sw=2))
    f.append(text(ptr_base_x, y_cells + cell_h + 62, "Send_Base (3)", size=10, bold=True, color=COLOR_LOSS))

    f.append(arrow(ptr_next_x, y_cells + cell_h + 48, ptr_next_x, y_cells + cell_h + 12, color=COLOR_FRAME, sw=2))
    f.append(text(ptr_next_x, y_cells + cell_h + 62, "Next_Seq_Num (6)", size=10, bold=True, color=COLOR_FRAME))

    # Нижня частина: Обмеження розміру вікна через колізію номерів
    f.append(rect(30, 285, 820, 230, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
    f.append(text(50, 310, "Теорема нумерації: чому в Selective Repeat вікно W ≤ 2^(k-1)", size=13, bold=True, color=INK, anchor="start"))

    # Лівий блок: W = 2^(k-1) - Правильно (k=2, номери 0,1,2,3 -> W=2)
    f.append(rect(50, 330, 370, 165, fill="#f0fdf4", stroke=COLOR_ACK, sw=1.5, rx=6))
    f.append(text(235, 352, "Коректне вікно: W = 2^(2-1) = 2", size=11, bold=True, color=COLOR_ACK))
    f.append(fitbox(60, 365, 350, 120,
                    "• TX надсилає [0, 1], RX приймає [0, 1] та зсуває вікно на [2, 3]\n• Якщо всі ACK [0, 1] втрачено, TX повторює [0, 1]\n• RX бачить кадри [0, 1] поза новим вікном [2, 3] → відкидає як ДУБЛІКАТИ!\nНемає неоднозначності.",
                    size=10, fill="none", stroke="none"))

    # Правий блок: W > 2^(k-1) - Помилка колізії (k=2, номери 0,1,2,3 -> W=3)
    f.append(rect(450, 330, 380, 165, fill="#fef2f2", stroke=COLOR_LOSS, sw=1.5, rx=6))
    f.append(text(640, 352, "Помилкове вікно: W = 3 > 2^(2-1)", size=11, bold=True, color=COLOR_LOSS))
    f.append(fitbox(460, 365, 360, 120,
                    "• TX надсилає [0, 1, 2], RX приймає їх і зсуває вікно на [3, 0, 1]\n• Якщо всі ACK втрачено, TX повторює старий кадр 0\n• RX очікує новий кадр 0 у вікні [3, 0, 1] → сприймає дублікат як НОВІ ДАНІ!\nКритичне пошкодження потоку даних.",
                    size=10, fill="none", stroke="none"))

    return render(os.path.join(IMG, "sliding-window-mechanics.svg"), W, H, *f,
                  title="Механіка ковзного вікна та теорема однозначності нумерації")


# ── 3. Механізми HARQ: Chase Combining та Incremental Redundancy ───────────────
def fig_harq_combining_mechanisms():
    W, H = 940, 560
    f = []

    # Ліва частина: Chase Combining (CC)
    f.append(rect(30, 45, 425, 490, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
    f.append(text(242, 72, "HARQ Type II: Chase Combining (CC)", size=13, bold=True, color=INK))

    # Крок 1 CC
    f.append(fitbox(50, 95, 385, 75,
                    "Спроба 1: Передача блоку (RV = 0)\nСигнал проходить канал з шумом → CRC FAIL!\nМ'які біти (LLR_1) зберігаються в буфері",
                    size=10, fill="#ffffff", stroke=COLOR_BORDER))

    # Символ суми LLR
    f.append(arrow(242, 175, 242, 215, color=COLOR_FRAME, sw=2))

    # Крок 2 CC
    f.append(fitbox(50, 220, 385, 80,
                    "Спроба 2: Повторна передача ІДЕНТИЧНОЇ копії (RV = 0)\nОтримано зашумлені біти LLR_2\nSoft Combining: LLR_total = LLR_1 + LLR_2",
                    size=10, fill="#ffffff", stroke=COLOR_FRAME))

    f.append(arrow(242, 305, 242, 345, color=COLOR_ACK, sw=2))

    # Результат CC
    f.append(fitbox(50, 350, 385, 90,
                    "Ефект накопичення енергії:\n• Дисперсія шуму зменшується\n• Ефективне SNR зростає на +3 дБ з кожним повтором\n• Декодер FEC успішно декодує сумарний LLR → CRC PASS!",
                    size=10, fill="#f0fdf4", stroke=COLOR_ACK))

    f.append(fitbox(50, 450, 385, 65,
                    "Особливість: швидкість коду R_eff не змінюється.\nІдеально для стаціонарного каналу з білим шумом.",
                    size=10, fill="#ffffff", stroke=COLOR_BORDER))

    # Права частина: Incremental Redundancy (IR)
    f.append(rect(485, 45, 425, 490, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
    f.append(text(697, 72, "HARQ Type II: Incremental Redundancy (IR)", size=13, bold=True, color=INK))

    # Крок 1 IR
    f.append(fitbox(505, 95, 385, 75,
                    "Спроба 1: Передача систематичних бітів (RV0)\nКодова швидкість висока (R = 3/4, сильне пунктування)\nCRC FAIL → LLR_RV0 зберігається",
                    size=10, fill="#ffffff", stroke=COLOR_BORDER))

    f.append(arrow(697, 175, 697, 215, color=COLOR_BUFFER, sw=2))

    # Крок 2 IR
    f.append(fitbox(505, 220, 385, 80,
                    "Спроба 2: Передача НОВИХ бітів паритету (RV1)\nДекодер об'єднує RV0 та RV1\nЕквівалентна швидкість коду падає: R = 1/2",
                    size=10, fill="#ffffff", stroke=COLOR_BUFFER))

    f.append(arrow(697, 305, 697, 345, color=COLOR_ACK, sw=2))

    # Крок 3 IR
    f.append(fitbox(505, 350, 385, 90,
                    "Спроба 3 (за потреби): Додатковий паритет (RV2/RV3)\nКодова швидкість досягає базової (R = 1/3)\nКодовий виграш значно вищий, ніж простий приріст SNR → CRC PASS!",
                    size=10, fill="#f0fdf4", stroke=COLOR_ACK))

    f.append(fitbox(505, 450, 385, 65,
                    "Особливість: кожна спроба додає нову інформацію.\nВикористовується в LTE, 5G NR (LDPC/Polar) та Wi-Fi 6.",
                    size=10, fill="#ffffff", stroke=COLOR_BORDER))

    return render(os.path.join(IMG, "harq-combining-mechanisms.svg"), W, H, *f,
                  title="Механізми софт-комбінування в гібридному ARQ (HARQ)")


# ── 4. Залежність пропускної здатності від затримки каналу (a = t_prop / t_frame) ─
def fig_throughput_vs_delay():
    W, H = 860, 520
    f = []

    f.append(rect(30, 45, 800, 450, fill=COLOR_BG_BOX, stroke=COLOR_BORDER, sw=1.5, rx=8))
    f.append(text(430, 72, "Ефективність пропускної здатності η залежно від затримки a = t_prop / t_frame", size=13, bold=True, color=INK))

    # Координатна сітка графіка
    ox = 100
    oy = 420
    gw = 680
    gh = 300

    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))

    f.append(text(ox + gw - 15, oy + 25, "Нормалізована затримка a = t_prop / t_frame (лог. шкала)", size=11, color=INK, anchor="end"))
    f.append(text(ox - 15, oy - gh + 15, "Ефективність η", size=11, color=INK, anchor="end"))

    # Позначки осі Y (0, 0.2, 0.4, 0.6, 0.8, 1.0)
    for i in range(6):
        y_val = i * 0.2
        yp = oy - (y_val * gh)
        f.append(line(ox - 5, yp, ox, yp, color=LINE, sw=1))
        f.append(line(ox, yp, ox + gw, yp, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(ox - 12, yp + 4, "%.1f" % y_val, size=10, color=MUTED, anchor="end"))

    # Позначки осі X: a = 0.01, 0.1, 1, 10, 100
    x_ticks = [
        (0.01, 0.0, "0.01"),
        (0.1, 0.25, "0.1"),
        (1.0, 0.5, "1.0"),
        (10.0, 0.75, "10"),
        (100.0, 1.0, "100"),
    ]
    for _, frac, label in x_ticks:
        xp = ox + frac * (gw - 40)
        f.append(line(xp, oy, xp, oy + 5, color=LINE, sw=1))
        f.append(line(xp, oy - gh, xp, oy, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(xp, oy + 18, label, size=10, color=MUTED))

    # Допоміжна функція відображення (a, eta) -> (xp, yp)
    import math
    def map_pt(a_val, eta_val):
        # a_val від 0.01 до 100 (4 порядки)
        log_a = math.log10(a_val)  # від -2 до +2
        frac_x = (log_a + 2.0) / 4.0
        xp = ox + frac_x * (gw - 40)
        yp = oy - eta_val * gh
        return xp, yp

    # Криві для Pf = 0.05
    # 1. Selective Repeat (W >= 1 + 2a): eta = 1 - Pf = 0.95 (майже горизонтальна лінія)
    pts_sr = []
    for a_exp in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
        a_v = 10**a_exp
        eta = 0.95
        pts_sr.append(map_pt(a_v, eta))

    for i in range(len(pts_sr) - 1):
        f.append(line(pts_sr[i][0], pts_sr[i][1], pts_sr[i+1][0], pts_sr[i+1][1], color=COLOR_ACK, sw=3))

    # 2. Go-Back-N (N = 16, Pf = 0.05)
    # Якщо N >= 1 + 2a: eta = (1 - Pf)/(1 + (N-1)Pf) = 0.95 / (1 + 15*0.05) = 0.95 / 1.75 = 0.543
    # Якщо N < 1 + 2a: eta = N*(1 - Pf) / ((1+2a)*(1 + (N-1)Pf))
    pts_gbn = []
    N_gbn = 16
    for a_exp in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
        a_v = 10**a_exp
        denom_err = 1.0 + (N_gbn - 1) * 0.05
        if N_gbn >= 1.0 + 2.0 * a_v:
            eta = (1.0 - 0.05) / denom_err
        else:
            eta = (N_gbn * (1.0 - 0.05)) / ((1.0 + 2.0 * a_v) * denom_err)
        pts_gbn.append(map_pt(a_v, eta))

    for i in range(len(pts_gbn) - 1):
        f.append(line(pts_gbn[i][0], pts_gbn[i][1], pts_gbn[i+1][0], pts_gbn[i+1][1], color=COLOR_FRAME, sw=3))

    # 3. Stop-and-Wait (Pf = 0.05): eta = (1 - Pf) / (1 + 2a)
    pts_sw = []
    for a_exp in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
        a_v = 10**a_exp
        eta = (1.0 - 0.05) / (1.0 + 2.0 * a_v)
        pts_sw.append(map_pt(a_v, eta))

    for i in range(len(pts_sw) - 1):
        f.append(line(pts_sw[i][0], pts_sw[i][1], pts_sw[i+1][0], pts_sw[i+1][1], color=COLOR_LOSS, sw=3))

    # Легенда графіка
    f.append(rect(470, 95, 330, 105, fill="#ffffff", stroke=COLOR_BORDER, sw=1.5, rx=6))
    f.append(line(485, 115, 520, 115, color=COLOR_ACK, sw=3))
    f.append(text(530, 119, "Selective Repeat (W ≥ 1+2a, η = 0.95)", size=10, bold=True, color=INK, anchor="start"))

    f.append(line(485, 145, 520, 145, color=COLOR_FRAME, sw=3))
    f.append(text(530, 149, "Go-Back-N (N = 16, P_f = 0.05)", size=10, bold=True, color=INK, anchor="start"))

    f.append(line(485, 175, 520, 175, color=COLOR_LOSS, sw=3))
    f.append(text(530, 179, "Stop-and-Wait (P_f = 0.05)", size=10, bold=True, color=INK, anchor="start"))

    return render(os.path.join(IMG, "throughput-vs-delay.svg"), W, H, *f,
                  title="Залежність коефіцієнта використання каналу від затримки")


if __name__ == "__main__":
    fig_arq_timeline_comparison()
    fig_sliding_window_mechanics()
    fig_harq_combining_mechanisms()
    fig_throughput_vs_delay()
    print("All figures generated successfully.")
