# -*- coding: utf-8 -*-
"""Фігури до теми «Передискретизація UART».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARN = "#b07a00"   # попередження / шум / на межі


# ── 1. Фази бітового інтервалу при 16x ─────────────────────────────────────────
def fig_oversampling_phases_16x():
    W, H = 940, 420
    f = [
        text(W / 2, 30, "Фази бітового інтервалу при передискретизації 16×", size=17, bold=True),
        text(W / 2, 52, "один біт t_bit ділиться на 16 субтактів; вибірка береться у стабільному центрі (такти 7, 8, 9)",
             size=12, italic=True, color=MUTED)
    ]

    x0, y0 = 70, 120
    cell_w, cell_h = 50, 60
    total_w = 16 * cell_w  # 800 px

    # Фонова розмітка 16 комірок
    for i in range(16):
        cx = x0 + i * cell_w
        if i in (7, 8, 9):
            fill = "#e8f8ee"
            stroke_col = FIELD
            sw_val = 1.8
        elif i in (0, 1, 14, 15):
            fill = "#fdf2f2"
            stroke_col = "#e0a0a0"
            sw_val = 1.0
        else:
            fill = "#f8f9fa"
            stroke_col = "#d0d4d8"
            sw_val = 1.0

        f.append(rect(cx, y0, cell_w, cell_h, fill=fill, stroke=stroke_col, sw=sw_val, rx=0))
        f.append(text(cx + cell_w / 2, y0 + 35, str(i), size=12, bold=(i in (7, 8, 9)),
                      color=(FIELD if i in (7, 8, 9) else INK)))

    # Підпис осі тактів
    f.append(text(x0 - 12, y0 + 35, "субтакт →", size=11, bold=True, color=MUTED, anchor="end"))

    # Маркери трьох центральних вибірок
    for i in (7, 8, 9):
        cx = x0 + i * cell_w + cell_w / 2
        f.append(line(cx, y0 - 16, cx, y0 + cell_h + 16, color=FIELD, sw=1.5, dash="3,3"))
        f.append(circle(cx, y0 - 16, 5, fill="#fff", stroke=FIELD, sw=2))
        f.append(text(cx, y0 - 26, f"S{i}", size=11, bold=True, color=FIELD))

    # Стрілка загальної тривалості біта t_bit
    f.append(line(x0, y0 - 46, x0 + total_w, y0 - 46, color=INK, sw=1.5))
    f.append(line(x0, y0 - 54, x0, y0 - 38, color=INK, sw=1.5))
    f.append(line(x0 + total_w, y0 - 54, x0 + total_w, y0 - 38, color=INK, sw=1.5))
    f.append(text(x0 + total_w / 2, y0 - 54, "Тривалість бітового інтервалу t_bit (16 тактів f_sample = 16 × baud)",
                  size=12, bold=True))

    # Зони знизу
    zy = y0 + cell_h + 30
    # Крайова зона невизначеності зліва
    f.append(rect(x0, zy, 2 * cell_w, 24, fill="#fbecec", stroke=POS, sw=1, rx=4))
    f.append(text(x0 + cell_w, zy + 16, "фронт / джиттер", size=9.5, bold=True, color=POS))

    # Центральне вікно вибірок
    f.append(rect(x0 + 7 * cell_w, zy, 3 * cell_w, 24, fill="#e8f8ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x0 + 8.5 * cell_w, zy + 16, "3 вибірки: такти 7, 8, 9", size=10, bold=True, color=FIELD))

    # Крайова зона невизначеності справа
    f.append(rect(x0 + 14 * cell_w, zy, 2 * cell_w, 24, fill="#fbecec", stroke=POS, sw=1, rx=4))
    f.append(text(x0 + 15 * cell_w, zy + 16, "спад / джиттер", size=9.5, bold=True, color=POS))

    # Пояснювальний блок унизу
    f.append(fitbox(70, 275, 800, 115, [
        "Кожен біт ділиться на 16 квантів часу. Спадом стартового біта лічильник синхронізується в 0.",
        "Перші 2 такти (0-1) і останні 2 такти (14-15) поглинають перехідні процеси, завал фронтів і фазовий джиттер.",
        "У центрі (такти 7, 8, 9) апаратура робить три вибірки S7, S8, S9 і визначає значення біта за більшістю голосів.",
        "Завдяки передискретизації 16× похибка початкової прив'язки до спаду не перевищує ±1/16 біта (±6.25%)."
    ], size=11.5, fill="#f4f6f8"))

    render(os.path.join(IMG, "oversampling-phases-16x.svg"), W, H, *f)


# ── 2. Фільтрація завад та верифікація стартового біта ─────────────────────────
def fig_start_bit_glitch_filter():
    W, H = 940, 450
    f = [
        text(W / 2, 30, "Фільтрація завад та верифікація стартового біта", size=17, bold=True),
        text(W / 2, 52, "короткий сплеск шуму відсікається перевіркою середини; справжній старт фіксує 0",
             size=12, italic=True, color=MUTED)
    ]

    # Верхня половина: Короткий викид (завада / Glitch)
    y_top = 90
    f.append(rect(50, y_top, 840, 140, fill="#fffaf5", stroke="#f0d0b0", sw=1.5, rx=8))
    f.append(text(65, y_top + 24, "Випадок А: Хибний старт (коротка завада < 4 тактів)", size=13, bold=True,
                  color=POS, anchor="start"))

    # Осцилограма завади
    gx0, gy0 = 80, y_top + 70
    f.append(line(gx0, gy0, gx0 + 60, gy0, color=INK, sw=2))  # IDLE High
    f.append(line(gx0 + 60, gy0, gx0 + 60, gy0 + 35, color=INK, sw=2))  # Fall
    f.append(line(gx0 + 60, gy0 + 35, gx0 + 130, gy0 + 35, color=INK, sw=2))  # Glitch Low (2 такти)
    f.append(line(gx0 + 130, gy0 + 35, gx0 + 130, gy0, color=INK, sw=2))  # Rise
    f.append(line(gx0 + 130, gy0, gx0 + 420, gy0, color=INK, sw=2))  # High again

    f.append(text(gx0 + 30, gy0 - 10, "IDLE ('1')", size=10.5, color=MUTED))
    f.append(text(gx0 + 95, gy0 + 52, "завада 20 нс", size=10.5, bold=True, color=POS))

    # Точки перевірки фільтра завад на тактах 3, 5, 7 або 8
    f.append(line(gx0 + 60, gy0 - 15, gx0 + 60, gy0 + 55, color=POS, sw=1.2, dash="3,3"))
    f.append(text(gx0 + 60, gy0 - 20, "спад (такт 0)", size=10, color=POS))

    chk_x = gx0 + 260
    f.append(line(chk_x, gy0 - 15, chk_x, gy0 + 55, color=POS, sw=1.5, dash="3,3"))
    f.append(circle(chk_x, gy0, 5, fill="#fff", stroke=POS, sw=2))
    f.append(text(chk_x, gy0 - 22, "перевірка (такт 7, 8, 9): лінія = 1", size=11, bold=True, color=POS))

    f.append(fitbox(520, y_top + 45, 350, 75, [
        "1. Спад запускає лічильник 16×.",
        "2. На середині старт-біта (такти 7-9) зчитується '1'.",
        "3. Вердикт: ХИБНИЙ СТАРТ (Glitch).",
        "4. FSM скидається в IDLE, кадр не спотворюється."
    ], size=10.5, fill="#fdf2f2"))

    # Нижня половина: Справжній старт-біт
    y_bot = 245
    f.append(rect(50, y_bot, 840, 140, fill="#f6fbf7", stroke="#c5e8ce", sw=1.5, rx=8))
    f.append(text(65, y_bot + 24, "Випадок Б: Справжній старт-біт (тривалість = 16 тактів)", size=13, bold=True,
                  color=FIELD, anchor="start"))

    # Осцилограма справжнього старту
    bx0, by0 = 80, y_bot + 70
    f.append(line(bx0, by0, bx0 + 60, by0, color=INK, sw=2))  # IDLE High
    f.append(line(bx0 + 60, by0, bx0 + 60, by0 + 35, color=INK, sw=2))  # Fall
    f.append(line(bx0 + 60, by0 + 35, bx0 + 380, by0 + 35, color=INK, sw=2))  # Start Bit Low
    f.append(line(bx0 + 380, by0 + 35, bx0 + 380, by0, color=INK, sw=2))  # Next bit transition
    f.append(line(bx0 + 380, by0, bx0 + 420, by0, color=INK, sw=2))

    f.append(text(bx0 + 30, by0 - 10, "IDLE ('1')", size=10.5, color=MUTED))
    f.append(text(bx0 + 220, by0 + 52, "Старт-біт триває повні 16 тактів (рівень '0')", size=10.5, color=FIELD))

    # Точки вибірок
    bchk_x = bx0 + 220
    f.append(line(bchk_x, by0 - 15, bchk_x, by0 + 55, color=FIELD, sw=1.5, dash="3,3"))
    f.append(circle(bchk_x, by0 + 35, 5, fill="#fff", stroke=FIELD, sw=2))
    f.append(text(bchk_x, by0 - 22, "перевірка (такти 7, 8, 9): лінія = 0", size=11, bold=True, color=FIELD))

    f.append(fitbox(520, y_bot + 45, 350, 75, [
        "1. Спад запускає субтактовий лічильник.",
        "2. Усі 3 центральні вибірки підтверджують '0'.",
        "3. Вердикт: ДІЙСНИЙ СТАРТ-БІТ.",
        "4. FSM переходить до прийому бітів даних D0..D7."
    ], size=10.5, fill="#eef7f0"))

    render(os.path.join(IMG, "start-bit-glitch-filter.svg"), W, H, *f)


# ── 3. Логіка мажоритарного голосування 3 вибірок ─────────────────────────────
def fig_majority_voting_logic():
    W, H = 940, 400
    f = [
        text(W / 2, 30, "Логіка мажоритарного голосування 3 вибірок (3-Sample Majority Voting)", size=17, bold=True),
        text(W / 2, 52, "значення біта = (S7 ∧ S8) ∨ (S8 ∧ S9) ∨ (S7 ∧ S9); прапорець завади NF активується при 2:1",
             size=12, italic=True, color=MUTED)
    ]

    # Ліва частина: Структурна схема логіки
    lx0, ly0 = 60, 90
    f.append(rect(lx0, ly0, 420, 275, fill="#f8f9fa", stroke="#d0d4d8", sw=1.5, rx=8))
    f.append(text(lx0 + 210, ly0 + 26, "Апаратна логіка мажоритарного селектора", size=13, bold=True))

    # Входи S7, S8, S9
    vy = ly0 + 70
    for i, name in enumerate(["S7 (вибірка 1)", "S8 (вибірка 2)", "S9 (вибірка 3)"]):
        py = vy + i * 40
        f.append(rect(lx0 + 20, py - 14, 110, 28, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
        f.append(text(lx0 + 75, py + 4, name, size=11, bold=True))
        f.append(line(lx0 + 130, py, lx0 + 175, py, color=INK, sw=1.4))

    # Блок мажоритарного елемента
    f.append(rect(lx0 + 175, ly0 + 60, 110, 115, fill="#e8f8ee", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(lx0 + 230, ly0 + 105, "Більшість", size=12, bold=True, color=FIELD))
    f.append(text(lx0 + 230, ly0 + 125, "(≥ 2 однакових)", size=10, color=MUTED))
    f.append(text(lx0 + 230, ly0 + 145, "2 з 3", size=11, bold=True, color=FIELD))

    # Вихід значення біта
    f.append(arrow(lx0 + 285, ly0 + 115, lx0 + 340, ly0 + 115, color=FIELD, sw=1.8))
    f.append(rect(lx0 + 340, ly0 + 98, 65, 34, fill="#ffffff", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(lx0 + 372, ly0 + 120, "БІТ", size=13, bold=True, color=FIELD))

    # Детектор неодностайності (Noise Flag)
    f.append(rect(lx0 + 175, ly0 + 195, 110, 50, fill="#fdf2f2", stroke=WARN, sw=1.5, rx=6))
    f.append(text(lx0 + 230, ly0 + 216, "Детектор шуму", size=11, bold=True, color=WARN))
    f.append(text(lx0 + 230, ly0 + 234, "S7 ⊕ S8 ∨ S8 ⊕ S9", size=9.5, color=MUTED))

    f.append(arrow(lx0 + 285, ly0 + 220, lx0 + 340, ly0 + 220, color=WARN, sw=1.5))
    f.append(rect(lx0 + 340, ly0 + 203, 65, 34, fill="#fffaf0", stroke=WARN, sw=1.5, rx=4))
    f.append(text(lx0 + 372, ly0 + 225, "NF", size=12, bold=True, color=WARN))

    # Права частина: Таблиця істинності та стану
    rx0, ry0 = 500, 90
    f.append(rect(rx0, ry0, 390, 275, fill="#ffffff", stroke="#d0d4d8", sw=1.5, rx=8))
    f.append(text(rx0 + 195, ry0 + 26, "Таблиця станів 3 вибірок", size=13, bold=True))

    headers = ["S7", "S8", "S9", "Результат", "Прапорець NF", "Оцінка"]
    hx = [rx0 + 25, rx0 + 60, rx0 + 95, rx0 + 155, rx0 + 235, rx0 + 330]
    f.append(rect(rx0 + 10, ry0 + 42, 370, 26, fill="#f0f3f6", stroke="none", rx=3))
    for i, h in enumerate(headers):
        f.append(text(hx[i], ry0 + 59, h, size=10.5, bold=True))

    rows = [
        ("0", "0", "0", "0", "0 (чисто)", FIELD, "Ідеальний нуль"),
        ("0", "0", "1", "0", "1 (завада)", WARN, "Відновлено 0 (шум на S9)"),
        ("0", "1", "0", "0", "1 (завада)", WARN, "Відновлено 0 (сплеск на S8)"),
        ("0", "1", "1", "1", "1 (завада)", WARN, "Відновлено 1 (провал на S7)"),
        ("1", "0", "0", "0", "1 (завада)", WARN, "Відновлено 0 (сплеск на S7)"),
        ("1", "0", "1", "1", "1 (завада)", WARN, "Відновлено 1 (провал на S8)"),
        ("1", "1", "0", "1", "1 (завада)", WARN, "Відновлено 1 (провал на S9)"),
        ("1", "1", "1", "1", "0 (чисто)", FIELD, "Ідеальна одиниця"),
    ]
    for idx, (s7, s8, s9, res, nf, col, desc) in enumerate(rows):
        row_y = ry0 + 84 + idx * 22
        f.append(text(hx[0], row_y, s7, size=10))
        f.append(text(hx[1], row_y, s8, size=10))
        f.append(text(hx[2], row_y, s9, size=10))
        f.append(text(hx[3], row_y, res, size=10.5, bold=True, color=col))
        f.append(text(hx[4], row_y, nf, size=9.5, color=(WARN if "1" in nf else FIELD)))
        f.append(text(hx[5], row_y, desc, size=9, color=MUTED))

    render(os.path.join(IMG, "majority-voting-logic.svg"), W, H, *f)


# ── 4. Порівняння режимів передискретизації 16x та 8x ─────────────────────────
def fig_oversampling_16x_vs_8x():
    W, H = 940, 430
    f = [
        text(W / 2, 30, "Порівняння режимів передискретизації: 16× vs 8×", size=17, bold=True),
        text(W / 2, 52, "16× максимізує завадостійкість і часовий допуск; 8× подвоює максимальну швидкість baud",
             size=12, italic=True, color=MUTED)
    ]

    # Верхній блок: Режим 16x
    y1 = 90
    f.append(rect(50, y1, 840, 140, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(65, y1 + 24, "Режим 16× (Стандартний режим високої надійності)", size=13, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(875, y1 + 24, "f_baud_max = f_PCLK / 16", size=12, bold=True, color=MUTED, anchor="end"))

    # Сітка 16 тактів
    gx1 = 70
    tw1 = 28
    for i in range(16):
        fill = "#e8f8ee" if i in (7, 8, 9) else ("#fbecec" if i in (0, 15) else "#f4f6f8")
        f.append(rect(gx1 + i * tw1, y1 + 45, tw1, 35, fill=fill, stroke="#d0d4d8", sw=1, rx=0))
        f.append(text(gx1 + i * tw1 + tw1 / 2, y1 + 67, str(i), size=10,
                      bold=(i in (7, 8, 9)), color=(FIELD if i in (7, 8, 9) else INK)))

    f.append(text(gx1 + 8.5 * tw1, y1 + 100, "Центр: вибірки 7, 8, 9 (18.75% біта)", size=10.5, bold=True, color=FIELD))

    # Характеристики 16x праворуч
    f.append(fitbox(540, y1 + 42, 335, 85, [
        "• Квантування фронту: ±1/32 біта (±3.125%)",
        "• Вікно голосування: 3 такти з 16",
        "• Допуск розбіжності частот: до ±4.28%",
        "• Застосування: стандартні швидкості до 3-5 Мбод"
    ], size=10.5, fill="#f4fbf6"))

    # Нижній блок: Режим 8x
    y2 = 250
    f.append(rect(50, y2, 840, 140, fill="#ffffff", stroke=WARN, sw=1.5, rx=8))
    f.append(text(65, y2 + 24, "Режим 8× (Високошвидкісний режим High-Speed)", size=13, bold=True,
                  color=WARN, anchor="start"))
    f.append(text(875, y2 + 24, "f_baud_max = f_PCLK / 8 (у 2 рази швидше)", size=12, bold=True, color=WARN, anchor="end"))

    # Сітка 8 тактів
    gx2 = 70
    tw2 = 56
    for i in range(8):
        fill = "#fdf5e6" if i in (3, 4, 5) else ("#fbecec" if i in (0, 7) else "#f4f6f8")
        f.append(rect(gx2 + i * tw2, y2 + 45, tw2, 35, fill=fill, stroke="#d0d4d8", sw=1, rx=0))
        f.append(text(gx2 + i * tw2 + tw2 / 2, y2 + 67, str(i), size=11,
                      bold=(i in (3, 4, 5)), color=(WARN if i in (3, 4, 5) else INK)))

    f.append(text(gx2 + 4.5 * tw2, y2 + 100, "Центр: вибірки 3, 4, 5 (37.5% біта)", size=10.5, bold=True, color=WARN))

    # Характеристики 8x праворуч
    f.append(fitbox(540, y2 + 42, 335, 85, [
        "• Квантування фронту: ±1/16 біта (±6.25%)",
        "• Вікно голосування: 3 такти з 8",
        "• Допуск розбіжності частот: знижено до ±3.29%",
        "• Застосування: надвисокі швидкості (до 10-12.5 Мбод)"
    ], size=10.5, fill="#fffaf0"))

    render(os.path.join(IMG, "oversampling-16x-vs-8x.svg"), W, H, *f)


# ── 5. Накопичення часового зсуву на 10 бітах кадру ───────────────────────────
def fig_accumulated_drift_10bit():
    W, H = 960, 440
    f = [
        text(W / 2, 30, "Накопичення часового зсуву на 10 бітах кадру (Start + 8 Data + Stop)", size=17, bold=True),
        text(W / 2, 52, "синхронізація лише на старті; розбіжність годинників накопичується до стоп-біта (k = 9.5)",
             size=12, italic=True, color=MUTED)
    ]

    cells = ["START", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "STOP"]
    x0, cw = 110, 72
    ytop, ch = 110, 44

    # Кадр 10 бітів
    for i, name in enumerate(cells):
        cx = x0 + i * cw
        fill = "#fbecec" if name == "START" else ("#f0f3f6" if name == "STOP" else "#ffffff")
        f.append(rect(cx, ytop, cw, ch, fill=fill, stroke="#8c9ba5", sw=1.4, rx=0))
        f.append(text(cx + cw / 2, ytop + 26, name, size=11, bold=True))

        # Ідеальний центр TX
        midx = cx + cw / 2
        f.append(line(midx, ytop - 12, midx, ytop + ch + 12, color=FIELD, sw=1.2, dash="3,3"))
        f.append(circle(midx, ytop - 16, 3.5, fill=FIELD, stroke=FIELD, sw=0))

        # Зсув вибірки RX при +3.5% похибці частоти: k * 0.035 * cw
        k = i + 0.5  # центр біта
        drift_px = (k) * 0.038 * cw
        rxx = midx + drift_px
        col = FIELD if i < 4 else (WARN if i < 8 else POS)
        f.append(circle(rxx, ytop + ch + 20, 4.5, fill="#ffffff", stroke=col, sw=1.8))
        f.append(line(rxx, ytop + ch + 4, rxx, ytop + ch + 16, color=col, sw=1.2))

    f.append(text(x0 - 10, ytop - 16, "Центри передавача (TX) →", size=10.5, bold=True, color=FIELD, anchor="end"))
    f.append(text(x0 - 10, ytop + ch + 24, "Вибірки приймача (RX) →", size=10.5, bold=True, color=POS, anchor="end"))

    # Стрілка наростання похибки
    f.append(line(x0 + cw / 2, ytop + ch + 42, x0 + 9.5 * cw + 26, ytop + ch + 42, color=POS, sw=1.5))
    f.append(arrow(x0 + 8.5 * cw, ytop + ch + 42, x0 + 9.5 * cw + 28, ytop + ch + 42, color=POS, sw=1.5))
    f.append(text(x0 + 5 * cw, ytop + ch + 58, "Зсув росте лінійно: Δt = (k + 0.5) × (Δf / f) × t_bit",
                  size=11, bold=True, color=POS))

    # Порівняльний блок унізу
    by = ytop + ch + 75
    f.append(rect(50, by, 860, 185, fill="#f8f9fa", stroke="#d0d4d8", sw=1.5, rx=8))
    f.append(text(W / 2, by + 24, "Бюджет допустимого часу на стоп-біті (k = 9.5 бітових інтервалів)", size=13, bold=True))

    f.append(fitbox(70, by + 38, 395, 130, [
        "Режим 16× (широкий часовий запас):",
        "• Початкове квантування: 0.0625 біта (1 такт)",
        "• Вікно 3 вибірок: 0.125 біта (такти 7-9)",
        "• Залишок запасу на дрейф частоти: 0.3125 біта",
        "• Граничний розсинхрон: 0.40625 / 9.5 ≈ 4.28% (ідеал)"
    ], size=10.5, fill="#e8f8ee"))

    f.append(fitbox(495, by + 38, 395, 130, [
        "Режим 8× (стиснутий часовий запас):",
        "• Початкове квантування: 0.125 біта (1 такт)",
        "• Вікно 3 вибірок: 0.250 біта (такти 3-5)",
        "• Залишок запасу на дрейф частоти: 0.125 біта",
        "• Граничний розсинхрон: 0.3125 / 9.5 ≈ 3.29% (ідеал)"
    ], size=10.5, fill="#fffaf0"))

    render(os.path.join(IMG, "accumulated-drift-10bit.svg"), W, H, *f)


if __name__ == "__main__":
    fig_oversampling_phases_16x()
    fig_start_bit_glitch_filter()
    fig_majority_voting_logic()
    fig_oversampling_16x_vs_8x()
    fig_accumulated_drift_10bit()
    print("OK: all UART oversampling figures generated successfully in", IMG)
