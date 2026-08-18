# -*- coding: utf-8 -*-
"""Фігури до теми «Дробовий дільник baud».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARN = "#b07a00"   # «на межі» — між зеленим (безпечно) і червоним (збій)


# ── 1. Цілочисельне квантування проти дробового підбору швидкості ────────────
def fig_integer_vs_fractional_quantization():
    W, H = 940, 420
    f = [
        text(W / 2, 28, "Цілочисельне квантування проти дробового дільника baud", size=16, bold=True),
        text(W / 2, 50, "на високих швидкостях (921600 бод при f_CK = 42 МГц) цілий дільник дає помилку кадру",
             size=12, italic=True, color=MUTED)
    ]

    # Ліва колонка: Цілий дільник N
    x_l, y_top, col_w, col_h = 50, 75, 400, 240
    f.append(rect(x_l, y_top, col_w, col_h, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(x_l + col_w / 2, y_top + 24, "Цілочисельний дільник (Integer Prescaler)", size=13, bold=True, color=POS))
    
    f.append(fitbox(x_l + 15, y_top + 40, col_w - 30, 48, [
        "DIV = 42 000 000 / (16 × 921 600) = 2.8489",
        "Ціле число N вимагає округлення: N = 2 або N = 3"
    ], size=11, fill="#ffffff", stroke="#f0c0c0"))

    # Варіант N = 3
    f.append(rect(x_l + 15, y_top + 98, col_w - 30, 56, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(x_l + 25, y_top + 118, "N = 3 (округлення вгору):", size=11.5, bold=True, anchor="start"))
    f.append(text(x_l + 25, y_top + 138, "baud = 42 МГц / (16 × 3) = 875 000 бод  (−5.06%)", size=11, color=POS, anchor="start"))
    f.append(text(x_l + col_w - 25, y_top + 128, "✗ ЗБІЙ", size=12, bold=True, color=POS, anchor="end"))

    # Варіант N = 2
    f.append(rect(x_l + 15, y_top + 164, col_w - 30, 56, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(x_l + 25, y_top + 184, "N = 2 (округлення вниз):", size=11.5, bold=True, anchor="start"))
    f.append(text(x_l + 25, y_top + 204, "baud = 42 МГц / (16 × 2) = 1 312 500 бод  (+42.4%)", size=11, color=POS, anchor="start"))
    f.append(text(x_l + col_w - 25, y_top + 194, "✗ ЗБІЙ", size=12, bold=True, color=POS, anchor="end"))

    # Права колонка: Дробовий дільник N + F/16
    x_r = 490
    f.append(rect(x_r, y_top, col_w, col_h, fill="#f0f9f2", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x_r + col_w / 2, y_top + 24, "Дробовий дільник (Fractional Baud Rate)", size=13, bold=True, color=FIELD))

    f.append(fitbox(x_r + 15, y_top + 40, col_w - 30, 48, [
        "DIV = 2 + 14/16 = 2.8750  (мантиса 2, дріб 14/16)",
        "Акумулятор чергує цикли ділення на 2 та 3"
    ], size=11, fill="#ffffff", stroke="#c0e8cc"))

    # Результат 16x oversampling
    f.append(rect(x_r + 15, y_top + 98, col_w - 30, 56, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x_r + 25, y_top + 118, "16× передискретизація (OVER8 = 0, F = 14):", size=11.5, bold=True, anchor="start"))
    f.append(text(x_r + 25, y_top + 138, "baud = 42 МГц / (16 × 2.875) = 913 043 бод  (−0.93%)", size=11, color=FIELD, anchor="start"))
    f.append(text(x_r + col_w - 25, y_top + 128, "✓ В ДОПУСКУ", size=11.5, bold=True, color=FIELD, anchor="end"))

    # Результат 8x oversampling
    f.append(rect(x_r + 15, y_top + 164, col_w - 30, 56, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x_r + 25, y_top + 184, "8× передискретизація (OVER8 = 1, DIV = 5.698):", size=11.5, bold=True, anchor="start"))
    f.append(text(x_r + 25, y_top + 204, "baud = 42 МГц / (8 × 5.700) = 921 053 бод  (−0.06%)", size=11, color=FIELD, anchor="start"))
    f.append(text(x_r + col_w - 25, y_top + 194, "✓ ІДЕАЛЬНО", size=11.5, bold=True, color=FIELD, anchor="end"))

    # Нижній висновок
    f.append(fitbox(50, 330, 840, 72, [
        "Цілочисельний дільник на високих швидкостях має завеликий крок квантування, і похибка 5.06% виходить",
        "за поріг стійкості UART (±2.5% на пристрій). Дробовий дільник усуває квантування, зводячи похибку до 0.06–0.93%,",
        "що гарантує безпомилковий прийом байтів без заміни опорного кварцового резонатора."
    ], size=11.5, fill="#f8fafc"))

    render(os.path.join(IMG, "integer-vs-fractional-quantization.svg"), W, H, *f)


# ── 2. Схемотехніка дробового дільника: фазовий акумулятор ───────────────────
def fig_fractional_accumulator_bresenham():
    W, H = 960, 460
    f = [
        text(W / 2, 28, "Схемотехніка дробового дільника: фазовий акумулятор та подвійний модуль", size=16, bold=True),
        text(W / 2, 50, "динамічне подовження окремих циклів ділення на 1 такт для синтезу середнього дробового коефіцієнта",
             size=12, italic=True, color=MUTED)
    ]

    # Блок тактової частоти f_CK
    f.append(rect(40, 110, 100, 54, fill=FILL, stroke=INK, sw=1.5))
    f.append(text(90, 132, "f_CK", size=13, bold=True))
    f.append(text(90, 149, "тактовий сигнал", size=10, color=MUTED))
    f.append(arrow(140, 137, 200, 137, color=INK))

    # Дільник подвійного модуля (Dual-Modulus Prescaler)
    f.append(rect(200, 95, 230, 84, fill="#eef4fa", stroke=NEG, sw=1.8))
    f.append(text(315, 120, "Дільник з подвійним модулем", size=12.5, bold=True, color=NEG))
    f.append(text(315, 140, "Ділить на N або N+1", size=11.5, bold=True))
    f.append(text(315, 160, "керований лічильник тактів", size=10.5, color=MUTED))
    f.append(arrow(430, 137, 510, 137, color=NEG))

    # Блок виходу sampling clock
    f.append(rect(510, 110, 180, 54, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(600, 132, "Sampling Clock (16× baud)", size=12, bold=True, color=FIELD))
    f.append(text(600, 149, "імпульси стробування", size=10, color=MUTED))

    # Зворотний зв'язок на фазовий акумулятор
    f.append(line(470, 137, 470, 240, color=INK, sw=1.5))
    f.append(arrow(470, 240, 410, 240, color=INK))

    # Фазовий акумулятор (Bresenham Phase Accumulator)
    f.append(rect(180, 210, 230, 100, fill="#fdf8ec", stroke=WARN, sw=1.8))
    f.append(text(295, 232, "Фазовий акумулятор", size=13, bold=True, color=WARN))
    f.append(text(295, 252, "ACC = ACC + FRAC", size=12, bold=True))
    f.append(text(295, 272, "модуль M (16 або 8)", size=11, color=MUTED))
    f.append(text(295, 292, "регістр фази [m біт]", size=10.5, color=MUTED))

    # Сигнал Carry / Overflow
    f.append(line(240, 210, 240, 179, color=POS, sw=1.8))
    f.append(arrow(240, 185, 240, 179, color=POS))
    f.append(text(230, 195, "Carry (+1)", size=11, bold=True, color=POS, anchor="end"))

    # Вхід FRAC
    f.append(arrow(80, 260, 180, 260, color=WARN))
    f.append(text(125, 252, "FRAC", size=12, bold=True, color=WARN))
    f.append(text(125, 276, "дробова частина", size=10, color=MUTED))

    # Права панель: часова діаграма імпульсів (Waveform)
    wx, wy, ww, wh = 450, 195, 470, 125
    f.append(rect(wx, wy, ww, wh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(wx + ww / 2, wy + 18, "Часова послідовність періодів дільника (при FRAC/16 = 3/16)", size=11, bold=True))

    # Клітинки тактів
    tw_x = wx + 15
    periods = [("N", FILL), ("N", FILL), ("N", FILL), ("N+1", "#fde8e8"),
               ("N", FILL), ("N", FILL), ("N", FILL), ("N", FILL),
               ("N+1", "#fde8e8"), ("N", FILL), ("N", FILL), ("N", FILL),
               ("N", FILL), ("N+1", "#fde8e8"), ("N", FILL), ("N", FILL)]
    cell_w = 26
    for i, (p_label, p_fill) in enumerate(periods):
        cx = tw_x + i * cell_w + (i // 4) * 6
        f.append(rect(cx, wy + 32, cell_w, 36, fill=p_fill, stroke=LINE, sw=1, rx=2))
        f.append(text(cx + cell_w / 2, wy + 55, p_label, size=9.5, bold=(p_label == "N+1"),
                      color=(POS if p_label == "N+1" else INK)))

    f.append(text(wx + ww / 2, wy + 88, "16 циклів дільника = 13 циклів по N тактів + 3 цикли по (N+1) тактів", size=10.5, bold=True))
    f.append(text(wx + ww / 2, wy + 108, "Середній коефіцієнт ділення: DIV_avg = N + 3/16 (без накопичення фазового дрейфу)",
                  size=10, italic=True, color=FIELD))

    # Нижній блок пояснення
    f.append(fitbox(40, 335, 880, 105, [
        "Принцип роботи фазового акумулятора (алгоритм Брезенгема): на кожному вихідному такті до регістра ACC додається дріб FRAC.",
        "Коли ACC досягає модуля M (16 або 8), виникає переповнення (Carry), яке вмикає поділ на N+1 замість N на один цикл,",
        "а з акумулятора віднімається M. Завдяки рівномірному розподілу додаткових тактів у часі сумарна фазова похибка",
        "кадру UART утримується в межах 1/16 біта, що унеможливлює накопичення фазового розсинхрону."
    ], size=11.5, fill="#f8fafc"))

    render(os.path.join(IMG, "fractional-accumulator-bresenham.svg"), W, H, *f)


# ── 3. Структура регістра USART_BRR у STM32 ──────────────────────────────────
def fig_stm32_usart_brr_structure():
    W, H = 920, 440
    f = [
        text(W / 2, 28, "Структура регістра USART_BRR у мікроконтролерах STM32", size=16, bold=True),
        text(W / 2, 50, "розподіл бітів мантиси та дробової частини в режимах передискретизації 16× та 8×",
             size=12, italic=True, color=MUTED)
    ]

    # Режим OVER8 = 0 (16x oversampling)
    y1 = 80
    f.append(text(60, y1 + 18, "Режим 16× передискретизації (OVER8 = 0, стандартний):", size=12.5, bold=True, anchor="start"))

    # Бітова лінійка [15:0]
    bx, by, bw, bh = 60, y1 + 30, 800, 48
    # Мантиса [15:4] (12 біт)
    mw = (12 / 16) * bw
    f.append(rect(bx, by, mw, bh, fill="#e8f0fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx + mw / 2, by + 22, "DIV_Mantissa[11:0]  (біти 15..4)", size=12, bold=True, color=NEG))
    f.append(text(bx + mw / 2, by + 38, "Ціла частина коефіцієнта ділення N", size=10.5, color=MUTED))

    # Дробова частина [3:0] (4 біти)
    fw = (4 / 16) * bw
    f.append(rect(bx + mw, by, fw, bh, fill="#fef3d6", stroke=WARN, sw=1.5, rx=4))
    f.append(text(bx + mw + fw / 2, by + 22, "DIV_Fraction[3:0] (біти 3..0)", size=11.5, bold=True, color=WARN))
    f.append(text(bx + mw + fw / 2, by + 38, "Дріб: F / 16", size=10.5, color=MUTED))

    f.append(text(bx + bw / 2, by + bh + 18, "Формула: USARTDIV = DIV_Mantissa + (DIV_Fraction / 16) = BRR / 16",
                  size=11.5, bold=True))

    # Режим OVER8 = 1 (8x oversampling)
    y2 = 200
    f.append(text(60, y2 + 18, "Режим 8× передискретизації (OVER8 = 1, високошвидкісний):", size=12.5, bold=True, anchor="start"))

    by2 = y2 + 30
    # Мантиса [15:4]
    f.append(rect(bx, by2, mw, bh, fill="#e8f0fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx + mw / 2, by2 + 22, "DIV_Mantissa[11:0]  (біти 15..4)", size=12, bold=True, color=NEG))
    f.append(text(bx + mw / 2, by2 + 38, "Ціла частина коефіцієнта ділення N", size=10.5, color=MUTED))

    # Біт 3 (очищений) + Дріб [2:0] (3 біти)
    b3w = (1 / 16) * bw
    f.append(rect(bx + mw, by2, b3w, bh, fill="#f0f0f0", stroke=MUTED, sw=1.2, rx=2))
    f.append(text(bx + mw + b3w / 2, by2 + 22, "0", size=12, bold=True, color=POS))
    f.append(text(bx + mw + b3w / 2, by2 + 38, "[3]", size=9, color=MUTED))

    f3w = (3 / 16) * bw
    f.append(rect(bx + mw + b3w, by2, f3w, bh, fill="#e6f4ea", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(bx + mw + b3w + f3w / 2, by2 + 22, "DIV_Fraction[2:0] (біти 2..0)", size=11, bold=True, color=FIELD))
    f.append(text(bx + mw + b3w + f3w / 2, by2 + 38, "Дріб: F / 8", size=10.5, color=MUTED))

    f.append(text(bx + bw / 2, by2 + bh + 18, "Формула: USARTDIV = DIV_Mantissa + (DIV_Fraction[2:0] / 8), біт BRR[3] мусить бути 0",
                  size=11.5, bold=True))

    # Нижній приклад обчислення
    f.append(fitbox(60, 325, 800, 95, [
        "Приклад: тактова частота APB1 f_CK = 42 МГц, цільова швидкість 115 200 бод (OVER8 = 0).",
        "1. USARTDIV = 42 000 000 / (16 × 115 200) = 22.786458...",
        "2. Мантиса = 22 = 0x016. Дробова частина = round(0.786458 × 16) = round(12.58) = 13 = 0xD.",
        "3. Значення регістра BRR = (22 << 4) | 13 = 0x016D. Реальний baud = 42 МГц / (16 × 22.8125) = 115 068 бод (−0.11%)."
    ], size=11, fill="#f8fafc"))

    render(os.path.join(IMG, "stm32-usart-brr-structure.svg"), W, H, *f)


# ── 4. Фазовий джитер окремих тактів та око стробування кадру UART ───────────
def fig_uart_jitter_eye_budget():
    W, H = 940, 440
    f = [
        text(W / 2, 28, "Фазовий джитер дробового дільника та стробування бітів UART", size=16, bold=True),
        text(W / 2, 50, "тремтіння фази окремих тактів (±1 такт f_CK) повністю поглинається вікном стробування 3-з-16",
             size=12, italic=True, color=MUTED)
    ]

    # Верхня частина: один бітовий інтервал і 16 відліків
    bx, by, bw, bh = 80, 85, 780, 140
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx + bw / 2, by + 20, "Бітовий інтервал UART (розбитий на 16 тактів передискретизації)", size=12.5, bold=True))

    # 16 відліків (клітинки)
    cw = bw / 16
    for i in range(16):
        cx = bx + i * cw
        # Підсвічування точок вибірки 7, 8, 9
        if i in (7, 8, 9):
            f.append(rect(cx, by + 35, cw, 50, fill="#d4edda", stroke=FIELD, sw=1.2, rx=0))
            f.append(text(cx + cw / 2, by + 65, str(i), size=11, bold=True, color=FIELD))
        else:
            f.append(rect(cx, by + 35, cw, 50, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=0))
            f.append(text(cx + cw / 2, by + 65, str(i), size=10, color=MUTED))

    # Зони на біті
    f.append(text(bx + 3.5 * cw, by + 105, "← Перехідний процес (шум фронту) →", size=10, color=MUTED))
    f.append(text(bx + 8.5 * cw, by + 105, "Строби: 7, 8, 9 (3-з-16)", size=11, bold=True, color=FIELD))
    f.append(text(bx + 13.5 * cw, by + 105, "← Запас до наступного фронту →", size=10, color=MUTED))

    # Зсув фази від дробового такту
    f.append(circle(bx + 8.5 * cw, by + 125, 4, fill=POS, stroke=POS, sw=1))
    f.append(line(bx + 8.5 * cw - 8, by + 125, bx + 8.5 * cw + 8, by + 125, color=POS, sw=2))
    f.append(text(bx + 8.5 * cw + 18, by + 128, "Джитер дробового циклу: ±1/16 біта (±6.25%) — глибоко всередині зони стробування",
                  size=10.5, bold=True, color=POS, anchor="start"))

    # Нижня частина: Порівняння накопичення зсуву вздовж кадру 8-N-1
    ny = 245
    f.append(rect(bx, ny, bw, 175, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(bx + bw / 2, ny + 20, "Накопичення похибки вздовж кадру UART (10 бітів від Start до Stop)", size=12, bold=True))

    # Шкала бітів Start, D0..D7, Stop
    frame_bits = ["ST", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "SP"]
    fb_w = (bw - 60) / 10
    fb_x0 = bx + 30
    for i, b_name in enumerate(frame_bits):
        fcx = fb_x0 + i * fb_w
        f.append(rect(fcx, ny + 35, fb_w, 28, fill="#ffffff", stroke=LINE, sw=1, rx=2))
        f.append(text(fcx + fb_w / 2, ny + 53, b_name, size=10.5, bold=True))

    # Крива 1: Цілочисельний дільник з похибкою 5% (накопичувальний дрейф)
    f.append(text(fb_x0, ny + 85, "Цілий дільник (похибка 5.06%): зсув росте лінійно → на Stop-біті фазова помилка 50.6% (> 0.5 біта, ЗБІЙ)",
                  size=11, color=POS, bold=True, anchor="start"))

    # Крива 2: Дробовий дільник (періодична фазова корекція)
    f.append(text(fb_x0, ny + 110, "Дробовий дільник (похибка 0.06%): фазовий акумулятор коректує крок на кожному біті → зсув < 1/16 біта",
                  size=11, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(bx + 15, ny + 125, bw - 30, 42, [
        "Висновок: миттєвий джитер одного такту (±1/16 біта) абсолютно безпечний для приймача,",
        "оскільки він не накопичується між бітами і надійно утримує весь 10-бітовий кадр у центрі стробування."
    ], size=10.5, fill="#ffffff", stroke="#d0e0d5"))

    render(os.path.join(IMG, "uart-jitter-eye-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_integer_vs_fractional_quantization()
    fig_fractional_accumulator_bresenham()
    fig_stm32_usart_brr_structure()
    fig_uart_jitter_eye_budget()
    print("All figures generated successfully.")
