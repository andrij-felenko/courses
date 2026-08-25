# -*- coding: utf-8 -*-
"""Фігури до теми «Допуск годинника UART».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Накопичення фазового зсуву вздовж 10-бітного кадру ─────────────────────
def fig_phase_drift():
    W, H = 960, 460
    f = [text(W / 2, 28, "Фазове розходження стробів приймача вздовж 10-бітного кадру 8N1",
              size=15, bold=True)]

    # Координатні межі
    x0, y_tx, y_rx_fast, y_rx_slow = 150, 90, 200, 310
    bw_tx = 68    # номінальна ширина біта TX
    n_bits = 10   # Start, D0..D7, Stop

    bit_names = ["START", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "STOP"]

    # Підписи осей ліворуч
    f.append(text(x0 - 15, y_tx + 22, "TX (еталон)", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(x0 - 15, y_rx_fast + 22, "RX швидший (+5%)", size=10.5, color=NEG, bold=True, anchor="end"))
    f.append(text(x0 - 15, y_rx_slow + 22, "RX повільніший (-5%)", size=10.5, color=POS, bold=True, anchor="end"))

    # Сигнал TX (номінал)
    prev_val = 1
    # Зразок байта: 0x55 (чергування 0/1) -> Start=0, D0=1, D1=0, D2=1, D3=0, D4=1, D5=0, D6=1, D7=0, Stop=1
    pattern = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    # Фонова смуга для швидкого RX
    f.append(rect(x0, y_rx_fast + 8, n_bits * bw_tx, 28, fill="#eef3fd", stroke="none", rx=3))
    # Фонова смуга для повільного RX
    f.append(rect(x0, y_rx_slow + 8, n_bits * bw_tx, 28, fill="#fdf0ed", stroke="none", rx=3))

    # Малюємо сітку бітів TX
    for i in range(n_bits):
        bx = x0 + i * bw_tx
        val = pattern[i]
        y_lvl = y_tx if val == 1 else y_tx + 36
        y_prev = y_tx if prev_val == 1 else y_tx + 36

        # Вертикальний фронт
        if y_lvl != y_prev or i == 0:
            f.append(line(bx, y_prev, bx, y_lvl, color=INK, sw=2.2))
        # Горизонтальний рівень
        f.append(line(bx, y_lvl, bx + bw_tx, y_lvl, color=INK, sw=2.2))

        # Вертикальна пунктирна межа біта TX
        f.append(line(bx, y_tx - 15, bx, y_rx_slow + 65, color=MUTED, sw=0.9, dash="3,3"))

        # Підпис біта
        f.append(text(bx + bw_tx / 2, y_tx - 20, bit_names[i], size=10, color=INK, bold=True))

        prev_val = val

    # Кінцева лінія кадру TX
    end_tx = x0 + n_bits * bw_tx
    f.append(line(end_tx, y_tx - 15, end_tx, y_rx_slow + 65, color=MUTED, sw=0.9, dash="3,3"))
    f.append(line(end_tx, y_tx, end_tx + 30, y_tx, color=INK, sw=2.2))

    # Спад старту (T=0)
    f.append(line(x0, y_tx - 10, x0, y_rx_slow + 75, color=FIELD, sw=2.2))
    f.append(text(x0, y_rx_slow + 95, "T=0: синхронізація", size=10, color=FIELD, bold=True))

    # 1) RX швидший (+5% частота -> період менший на 5%: bw_rx = bw_tx * 0.950)
    bw_rx_fast = bw_tx * 0.950
    for i in range(n_bits):
        strobe_x = x0 + (i + 0.5) * bw_rx_fast

        # Стрілка або мітка стробу
        f.append(line(strobe_x, y_rx_fast + 5, strobe_x, y_rx_fast + 40, color=NEG, sw=2))
        f.append(circle(strobe_x, y_rx_fast + 22, 3.5, fill=NEG, stroke=NEG))

        # На останньому біті показуємо небезпеку
        if i == 9:
            f.append(line(strobe_x, y_rx_fast - 10, strobe_x, y_rx_fast + 55, color=NEG, sw=1.5, dash="2,2"))
            f.append(text(strobe_x, y_rx_fast + 62, "Зсув ліворуч до D7!", size=9.5, color=NEG, bold=True))

    # 2) RX повільніший (-5% частота -> період більший на 5%: bw_rx = bw_tx * 1.05)
    bw_rx_slow = bw_tx * 1.050
    for i in range(n_bits):
        strobe_x = x0 + (i + 0.5) * bw_rx_slow

        f.append(line(strobe_x, y_rx_slow + 5, strobe_x, y_rx_slow + 40, color=POS, sw=2))
        f.append(circle(strobe_x, y_rx_slow + 22, 3.5, fill=POS, stroke=POS))

        if i == 9:
            f.append(line(strobe_x, y_rx_slow - 10, strobe_x, y_rx_slow + 55, color=POS, sw=1.5, dash="2,2"))
            f.append(text(strobe_x, y_rx_slow + 62, "Зсув праворуч за STOP!", size=9.5, color=POS, bold=True))

    # Пояснювальна картка внизу
    b, _, _ = textbox(W / 2, 428,
                      "Старт-біт обнуляє лічильник, але далі фазова похибка росте щорозряду: на D7 і Stop-біті строб ризикує вийти за межі бітового вікна",
                      size=11, fill="#f9fafb", stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "phase-drift-accum.svg"), W, H, *f)


# ── 2. Анатомія вікна стробування та передискретизація 16x ────────────────────
def fig_strobe_window():
    W, H = 880, 400
    f = [text(W / 2, 28, "Вікно стробування біта при передискретизації 16x",
              size=15, bold=True)]

    x0, y0, bw, bh = 140, 110, 600, 140

    # Загальне вікно біта
    f.append(rect(x0, y0, bw, bh, fill="#f8fafc", stroke=LINE, sw=2, rx=8))

    # Межі фронтів біта
    f.append(line(x0, y0 - 30, x0, y0 + bh + 30, color=LINE, sw=1.8, dash="4,3"))
    f.append(line(x0 + bw, y0 - 30, x0 + bw, y0 + bh + 30, color=LINE, sw=1.8, dash="4,3"))
    f.append(text(x0, y0 - 38, "Початок біта (0%)", size=11, color=MUTED, bold=True))
    f.append(text(x0 + bw, y0 - 38, "Кінець біта (100%)", size=11, color=MUTED, bold=True))

    # Небезпечні зони фронтів (фронти наростання/спаду + завади)
    slew_w = bw * 0.15
    f.append(rect(x0, y0, slew_w, bh, fill="#fde8e8", stroke="none", rx=0))
    f.append(rect(x0 + bw - slew_w, y0, slew_w, bh, fill="#fde8e8", stroke="none", rx=0))
    f.append(text(x0 + slew_w / 2, y0 + bh / 2, "Перехідний\nпроцес", size=10, color=POS, bold=True))
    f.append(text(x0 + bw - slew_w / 2, y0 + bh / 2, "Перехідний\nпроцес", size=10, color=POS, bold=True))

    # 16 тактів передискретизації
    tick_w = bw / 16.0
    for k in range(16):
        tx = x0 + k * tick_w
        f.append(line(tx, y0 + bh - 20, tx, y0 + bh, color=MUTED, sw=1))
        f.append(text(tx + tick_w / 2, y0 + bh - 6, str(k), size=9, color=MUTED))

    # Вікно вибірки 3 з 16 (мажоритарне голосування: такти 7, 8, 9)
    vote_x1 = x0 + 7 * tick_w
    vote_x2 = x0 + 10 * tick_w
    f.append(rect(vote_x1, y0 + 20, vote_x2 - vote_x1, bh - 50, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    f.append(text((vote_x1 + vote_x2) / 2, y0 + 45, "Мажоритарна вибірка\n(такти 7, 8, 9)", size=10.5, color=FIELD, bold=True))

    # Номінальний центр 50%
    mid_x = x0 + bw / 2
    f.append(line(mid_x, y0 - 15, mid_x, y0 + bh + 15, color=NEG, sw=2))
    f.append(circle(mid_x, y0 + bh / 2 + 10, 5, fill=NEG, stroke=NEG))
    f.append(text(mid_x, y0 - 20, "Номінальний строб (50%)", size=11, color=NEG, bold=True))

    # Допустимий запас фазового зміщення
    safe_x1 = x0 + slew_w
    safe_x2 = x0 + bw - slew_w
    by = y0 + bh + 45
    f.append(line(safe_x1, by, safe_x2, by, color=FIELD, sw=2))
    f.append(line(safe_x1, by - 6, safe_x1, by + 6, color=FIELD, sw=2))
    f.append(line(safe_x2, by - 6, safe_x2, by + 6, color=FIELD, sw=2))
    f.append(text(mid_x, by + 18, "Реальне безпечне вікно вибірки: ±35% тривалості біта", size=11.5, color=FIELD, bold=True))

    # Пояснення внизу
    b, _, _ = textbox(W / 2, 365,
                      "Теоретичний запас ±50% звужується тривалістю фронтів, завадами та апертурою триточкового голосування 3-of-16",
                      size=11, fill="#f9fafb", stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "strobe-window.svg"), W, H, *f)


# ── 3. Розклад бюджету похибки (Error Budget Breakdown) ───────────────────────
def fig_error_budget():
    W, H = 920, 420
    f = [text(W / 2, 28, "Складові практичного бюджету похибки тактування UART",
              size=15, bold=True)]

    # Дві порівняльні колонки: внутрішній RC проти кварцового резонатора XTAL
    col_w, col_h = 370, 280
    x_rc, x_xtal, y_box = 80, 480, 65

    # 1. Колонка RC-генератора
    f.append(rect(x_rc, y_box, col_w, col_h, fill="#fff7ed", stroke="#ea580c", sw=2, rx=8))
    f.append(text(x_rc + col_w / 2, y_box + 26, "Внутрішній RC-генератор (HSI)", size=13, color="#ea580c", bold=True))

    rc_items = [
        ("Початкове калібрування (25°C):", "±1.0%"),
        ("Температурний дрейф (-40..+105°C):", "±2.0% ... ±3.0%"),
        ("Дрейф від напруги живлення:", "±0.5%"),
        ("Квантування дільника BRR:", "±0.5% ... ±1.5%"),
        ("Сумарна похибка вузла:", "±4.0% ... ±6.0%"),
    ]

    for idx, (label, val) in enumerate(rc_items):
        yy = y_box + 62 + idx * 36
        is_total = (idx == len(rc_items) - 1)
        col = POS if is_total else INK
        bld = is_total
        f.append(text(x_rc + 16, yy, label, size=11, color=col, anchor="start", bold=bld))
        f.append(text(x_rc + col_w - 16, yy, val, size=11, color=col, anchor="end", bold=bld))
        if not is_total:
            f.append(line(x_rc + 16, yy + 12, x_rc + col_w - 16, yy + 12, color="#fed7aa", sw=1))

    b_rc_warn, _, _ = textbox(x_rc + col_w / 2, y_box + col_h - 22,
                              "НЕБЕЗПЕЧНО: перевищує поріг 4.5%",
                              size=10.5, fill="#fee2e2", stroke=POS, bold=True)
    f.append(b_rc_warn)

    # 2. Колонка Кварцу (XTAL)
    f.append(rect(x_xtal, y_box, col_w, col_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    f.append(text(x_xtal + col_w / 2, y_box + 26, "Кварцовий резонатор (XTAL / HSE)", size=13, color=FIELD, bold=True))

    xtal_items = [
        ("Початкова точність резонансу:", "±20 ppm (0.002%)"),
        ("Температурна нестабільність:", "±30 ppm (0.003%)"),
        ("Старіння кристала за рік:", "±5 ppm (0.0005%)"),
        ("Квантування дільника BRR:", "±0.1% ... ±0.8%"),
        ("Сумарна похибка вузла:", "< 0.8% (визначається BRR)"),
    ]

    for idx, (label, val) in enumerate(xtal_items):
        yy = y_box + 62 + idx * 36
        is_total = (idx == len(xtal_items) - 1)
        col = FIELD if is_total else INK
        bld = is_total
        f.append(text(x_xtal + 16, yy, label, size=11, color=col, anchor="start", bold=bld))
        f.append(text(x_xtal + col_w - 16, yy, val, size=11, color=col, anchor="end", bold=bld))
        if not is_total:
            f.append(line(x_xtal + 16, yy + 12, x_xtal + col_w - 16, yy + 12, color="#bbf7d0", sw=1))

    b_xtal_ok, _, _ = textbox(x_xtal + col_w / 2, y_box + col_h - 22,
                              "НАДІЙНО: повний запас стійкості",
                              size=10.5, fill="#dcfce7", stroke=FIELD, bold=True)
    f.append(b_xtal_ok)

    # Загальний підсумок внизу
    b, _, _ = textbox(W / 2, 385,
                      "Правило надійності: похибка генератора разом із квантуванням дільника BRR не повинна перевищувати ±1.5% на кожен вузол",
                      size=11, fill="#f9fafb", stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "error-budget-breakdown.svg"), W, H, *f)


# ── 4. Квантування дробового дільника BRR ─────────────────────────────────────
def fig_brr_quantization():
    W, H = 900, 410
    f = [text(W / 2, 28, "Вплив тактової частоти ядра та дільника BRR на швидкість 115 200 бод",
              size=15, bold=True)]

    # Порівняння 3 сценаріїв
    scenarios = [
        {
            "title": "8 МГц, цілочисельний дільник (USART_BRR = 4)",
            "calc": "8 000 000 / (16 × 4) = 125 000 бод",
            "err": "+8.51%",
            "verdict": "КРАХ ЗВ'ЯЗКУ (помилка обрамлення)",
            "col": POS,
            "bg": "#fee2e2"
        },
        {
            "title": "8 МГц, дробовий дільник (USART_BRR = 4 + 5/16 = 4.3125)",
            "calc": "8 000 000 / (16 × 4.3125) = 115 942 бод",
            "err": "+0.64%",
            "verdict": "ПРАЦЮЄ (в межах норми)",
            "col": "#ea580c",
            "bg": "#ffedd5"
        },
        {
            "title": "11.0592 МГц, спеціальний «UART-кварц» (USART_BRR = 6.000)",
            "calc": "11 059 200 / (16 × 6) = 115 200 бод",
            "err": "0.000%",
            "verdict": "ІДЕАЛЬНО (нульова похибка квантування)",
            "col": FIELD,
            "bg": "#dcfce7"
        },
    ]

    box_y = 65
    box_h = 82
    bw = 820
    bx = 40

    for idx, sc in enumerate(scenarios):
        yy = box_y + idx * 98
        f.append(rect(bx, yy, bw, box_h, fill=sc["bg"], stroke=sc["col"], sw=1.8, rx=6))

        # Заголовок блоку
        f.append(text(bx + 18, yy + 24, sc["title"], size=12, color=INK, bold=True, anchor="start"))

        # Розрахунок
        f.append(text(bx + 18, yy + 54, sc["calc"], size=11, color=MUTED, anchor="start"))

        # Похибка
        f.append(text(bx + bw - 260, yy + 38, "Похибка:", size=11, color=MUTED, anchor="end"))
        f.append(text(bx + bw - 190, yy + 40, sc["err"], size=16, color=sc["col"], bold=True, anchor="end"))

        # Вердикт
        f.append(text(bx + bw - 20, yy + 40, sc["verdict"], size=10.5, color=sc["col"], bold=True, anchor="end"))

    # Висновок
    b, _, _ = textbox(W / 2, 375,
                      "«Магічні» частоти кварців (11.0592, 7.3728, 14.7456 МГц) кратні всім стандартним швидкостям бод",
                      size=11, fill="#f9fafb", stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "brr-divider-quant.svg"), W, H, *f)


if __name__ == "__main__":
    fig_phase_drift()
    fig_strobe_window()
    fig_error_budget()
    fig_brr_quantization()
    print("Всі фігури згенеровано успішно.")
