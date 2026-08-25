# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GFILL = "#eafaf0"   # добрий стан (Good)
GSTRK = "#27ae60"
BFILL = "#fdecea"   # поганий стан (Bad)
BSTRK = "#c0392b"


def cpath(d, color=INK, sw=2.2, dash=None, arrow=True):
    """Дуга/крива <path>; arrow=True додає стрілку-маркер."""
    a = ' marker-end="url(#arrow)"' if arrow else ''
    dd = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>' % (d, color, sw, dd, a)


# ── 1. states.svg: Двостанова модель Маркова G ⇄ B ────────────────────────────

def fig_states():
    W, H = 820, 460
    p = []

    Gx, Gy, R = 230, 210, 68
    Bx = 590

    # Петля-самоперехід над G: 1 − P_GB
    p.append(cpath("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" %
                   (Gx - 32, Gy - 60, Gx - 82, Gy - 152, Gx + 82, Gy - 152, Gx + 32, Gy - 60),
                   color=GSTRK, sw=2.2))
    p.append(text(Gx, Gy - 130, "1 − P_GB  (лишитися в G)", size=13, color=GSTRK, bold=True))

    # Петля-самоперехід над B: 1 − P_BG
    p.append(cpath("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" %
                   (Bx - 32, Gy - 60, Bx - 82, Gy - 152, Bx + 82, Gy - 152, Bx + 32, Gy - 60),
                   color=BSTRK, sw=2.2))
    p.append(text(Bx, Gy - 130, "1 − P_BG  (лишитися в B)", size=13, color=BSTRK, bold=True))

    # G → B (верхня дуга): P_GB
    mx = (Gx + Bx) / 2
    p.append(cpath("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                   (Gx + 60, Gy - 32, mx, Gy - 94, Bx - 60, Gy - 32), color=INK, sw=2.4))
    tb_pgb, _, _ = textbox(mx, Gy - 86, "P_GB  (погіршення каналу)", size=13,
                           fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)
    p.append(tb_pgb)

    # B → G (нижня дуга): P_BG
    p.append(cpath("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                   (Bx - 60, Gy + 32, mx, Gy + 94, Gx + 60, Gy + 32), color=INK, sw=2.4))
    tb_pbg, _, _ = textbox(mx, Gy + 86, "P_BG  (відновлення каналу)", size=13,
                           fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)
    p.append(tb_pbg)

    # Вершина G
    p.append(circle(Gx, Gy, R, fill=GFILL, stroke=GSTRK, sw=3.0))
    p.append(text(Gx, Gy - 8, "G", size=32, color=GSTRK, bold=True))
    p.append(text(Gx, Gy + 20, "Добрий (Good)", size=13, color=GSTRK, bold=True))

    # Вершина B
    p.append(circle(Bx, Gy, R, fill=BFILL, stroke=BSTRK, sw=3.0))
    p.append(text(Bx, Gy - 8, "B", size=32, color=BSTRK, bold=True))
    p.append(text(Bx, Gy + 20, "Поганий (Bad)", size=13, color=BSTRK, bold=True))

    # Опис помилок під станами
    tb_g, _, _ = textbox(Gx, Gy + R + 56,
                         "Помилка e_G ≪ e_B\n(e_G ≈ 0 або 10⁻⁵)\nСер. довжина серії: 1 / P_GB",
                         size=12, fill=GFILL, stroke=GSTRK, sw=1.5, pad=8)
    p.append(tb_g)

    tb_b, _, _ = textbox(Bx, Gy + R + 56,
                         "Помилка e_B ≈ 0.5 (пачка)\n(або e_B = 1.0 для стирань)\nСер. довжина пачки: 1 / P_BG",
                         size=12, fill=BFILL, stroke=BSTRK, sw=1.5, pad=8)
    p.append(tb_b)

    render(os.path.join(OUT, "states.svg"), W, H, *p)


# ── 2. burst-trace.svg: Часова розгортка помилок: Гілберт–Елліот vs BSC ───────

def fig_burst_trace():
    W, H = 840, 430
    p = []

    # Заголовок та шкала часу
    p.append(text(420, 28, "Порівняння потоку помилок за однакового середнього BER", size=16, bold=True))

    x0, x1 = 180, 800
    y_state = 90
    y_ge = 200
    y_bsc = 310

    # Осі часу
    p.append(arrow(x0 - 10, y_state + 25, x1 + 20, y_state + 25, color=MUTED, sw=1.5))
    p.append(text(x1 + 10, y_state + 42, "Час (біти / пакети)", size=11, color=MUTED, anchor="end"))

    p.append(arrow(x0 - 10, y_ge + 25, x1 + 20, y_ge + 25, color=MUTED, sw=1.5))
    p.append(text(x1 + 10, y_ge + 42, "Час (біти / пакети)", size=11, color=MUTED, anchor="end"))

    p.append(arrow(x0 - 10, y_bsc + 25, x1 + 20, y_bsc + 25, color=MUTED, sw=1.5))
    p.append(text(x1 + 10, y_bsc + 42, "Час (біти / пакети)", size=11, color=MUTED, anchor="end"))

    # Підписи доріжок зліва
    tb_lbl1, _, _ = textbox(90, y_state + 15, "Стан каналу\n(G / B)", size=12,
                            fill=FILL, stroke=MUTED, sw=1.2, pad=6)
    p.append(tb_lbl1)

    tb_lbl2, _, _ = textbox(90, y_ge + 15, "Гілберт–Елліот\n(пакети помилок)", size=12,
                            fill="#fdf2e9", stroke="#d35400", sw=1.2, pad=6)
    p.append(tb_lbl2)

    tb_lbl3, _, _ = textbox(90, y_bsc + 15, "Канал без пам'яті\n(BSC / AWGN)", size=12,
                            fill="#eaf2f8", stroke=NEG, sw=1.2, pad=6)
    p.append(tb_lbl3)

    # Інтервали станів: (start_x, end_x, is_bad)
    intervals = [
        (x0, x0 + 160, False),
        (x0 + 160, x0 + 260, True),
        (x0 + 260, x0 + 470, False),
        (x0 + 470, x0 + 580, True),
        (x0 + 580, x1, False),
    ]

    # Доріжка 1: смуги станів
    for sx, ex, is_bad in intervals:
        fill_col = BFILL if is_bad else GFILL
        strk_col = BSTRK if is_bad else GSTRK
        lbl_txt = "Стан B (пачка)" if is_bad else "Стан G (чисто)"
        p.append(rect(sx, y_state, ex - sx, 30, fill=fill_col, stroke=strk_col, sw=1.5, rx=3))
        p.append(text((sx + ex) / 2, y_state + 19, lbl_txt, size=11, color=strk_col, bold=True))

    # Доріжка 2: помилки Гілберта–Елліота (згустки в B)
    burst_errors_1 = [x0 + 172, x0 + 185, x0 + 195, x0 + 215, x0 + 230, x0 + 248]
    burst_errors_2 = [x0 + 482, x0 + 498, x0 + 510, x0 + 526, x0 + 542, x0 + 560, x0 + 572]
    sparse_error = [x0 + 360]  # рідкісна помилка в G
    ge_all = burst_errors_1 + burst_errors_2 + sparse_error

    # Фонова розмітка зон пачок
    p.append(rect(x0 + 160, y_ge - 15, 100, 55, fill=BFILL, stroke=BSTRK, sw=1.0, rx=4))
    p.append(rect(x0 + 470, y_ge - 15, 110, 55, fill=BFILL, stroke=BSTRK, sw=1.0, rx=4))

    for bx in ge_all:
        p.append(line(bx, y_ge + 25, bx, y_ge - 10, color=POS, sw=2.5))
        p.append(circle(bx, y_ge - 10, 3, fill=POS, stroke=POS, sw=1.0))

    # Доріжка 3: помилки BSC (розсіяні по всій шкалі)
    bsc_errors = [x0 + 40, x0 + 95, x0 + 150, x0 + 205, x0 + 260, x0 + 315,
                  x0 + 375, x0 + 430, x0 + 490, x0 + 550, x0 + 605, x0 + 670, x0 + 735, x0 + 785]
    for bx in bsc_errors:
        p.append(line(bx, y_bsc + 25, bx, y_bsc - 10, color=NEG, sw=2.2))
        p.append(circle(bx, y_bsc - 10, 3, fill=NEG, stroke=NEG, sw=1.0))

    # Підсумкове пояснення внизу
    tb_btm, _, _ = textbox(420, 395,
                           "Сумарна кількість помилок однакова: у каналі з пам'яттю вони скупчуються в пачки,\n"
                           "перевантажуючи коди FEC (t помилок на блок), тоді як у каналі без пам'яті вони легко виправляються.",
                           size=12, fill=FILL, stroke=LINE, sw=1.2, pad=8)
    p.append(tb_btm)

    render(os.path.join(OUT, "burst-trace.svg"), W, H, *p)


# ── 3. interleaver-matrix.svg: Робота блокового переміжника ───────────────────

def fig_interleaver_matrix():
    W, H = 840, 480
    p = []

    p.append(text(420, 26, "Принцип роботи блокового переміжника (Interleaver)", size=16, bold=True))

    # Ліва частина: матриця N рядків × M стовпців
    mx0, my0 = 60, 75
    cell_w, cell_h = 50, 34
    rows, cols = 4, 6

    p.append(text(mx0 + (cols * cell_w) / 2, my0 - 16, "Матриця переміжника (глибина D = 4)", size=13, bold=True))

    # Запис по рядках (кодові слова FEC)
    p.append(arrow(mx0 - 30, my0 + 20, mx0 - 10, my0 + 20, color=FIELD, sw=2.0))
    p.append(text(mx0 - 40, my0 + 70, "Запис кодових\nслів FEC\n(по рядках)", size=11, color=FIELD, anchor="end"))

    # Зчитування по стовпцях (передача в ефір)
    p.append(arrow(mx0 + 50, my0 + rows * cell_h + 10, mx0 + 50, my0 + rows * cell_h + 30, color=POS, sw=2.0))
    p.append(text(mx0 + (cols * cell_w) / 2, my0 + rows * cell_h + 46, "Зчитування та передача в канал (по стовпцях)", size=12, color=POS, bold=True))

    colors_row = ["#e8f8f5", "#fef9e7", "#ebf5fb", "#f4ecf7"]
    strokes_row = ["#16a085", "#f39c12", "#2980b9", "#8e44ad"]

    for r in range(rows):
        for c in range(cols):
            cx = mx0 + c * cell_w
            cy = my0 + r * cell_h
            sym_lbl = "C%d,%d" % (r + 1, c + 1)
            # Виділяємо 2-й стовпець як такий, що потрапив під пачку помилок
            if c == 1:
                fill_c = "#fadbd8"
                strk_c = POS
                sw_c = 2.0
            else:
                fill_c = colors_row[r]
                strk_c = strokes_row[r]
                sw_c = 1.2
            p.append(rect(cx, cy, cell_w, cell_h, fill=fill_c, stroke=strk_c, sw=sw_c, rx=3))
            p.append(text(cx + cell_w / 2, cy + cell_h / 2 + 4, sym_lbl, size=11, color=INK, bold=(c == 1)))

    # Права частина: Передача в канал та деперемішування
    rx0 = 430
    p.append(text(rx0 + 190, my0 - 16, "Послідовність у каналі з пачкою помилок", size=13, bold=True))

    # Стрічка символів у каналі (стовпчик 2 передається поспіль)
    stream_w = 46
    stream_h = 32
    sy0 = my0 + 20
    channel_syms = ["C1,2", "C2,2", "C3,2", "C4,2"]

    tb_ch_hdr, _, _ = textbox(rx0 + 190, sy0 - 5, "Пачка помилок у каналі б'є 4 символи поспіль:", size=12,
                              fill="#fdf2e9", stroke="#e67e22", sw=1.2, pad=6)
    p.append(tb_ch_hdr)

    for i, s in enumerate(channel_syms):
        sx = rx0 + 50 + i * (stream_w + 12)
        sy = sy0 + 30
        p.append(rect(sx, sy, stream_w, stream_h, fill="#fadbd8", stroke=POS, sw=2.0, rx=4))
        p.append(text(sx + stream_w / 2, sy + stream_h / 2 + 4, s, size=11, color=POS, bold=True))
        p.append(text(sx + stream_w / 2, sy + stream_h + 16, "✕ помилка", size=10, color=POS))

    # Деперемішувач на приймачі
    dy0 = sy0 + 105
    tb_deint, _, _ = textbox(rx0 + 190, dy0, "Деперемішувач на приймачі (відновлює рядки):", size=12,
                             fill="#eafaf0", stroke=GSTRK, sw=1.2, pad=6)
    p.append(tb_deint)

    # 4 блоки FEC на виході
    for r in range(rows):
        bx = rx0 + 30
        by = dy0 + 30 + r * 30
        p.append(rect(bx, by, 320, 24, fill=colors_row[r], stroke=strokes_row[r], sw=1.2, rx=3))
        p.append(text(bx + 60, by + 16, "Блок FEC %d:" % (r + 1), size=11, color=strokes_row[r], bold=True))
        p.append(text(bx + 190, by + 16, "містить лише 1 помилку (C%d,2) → успішно виправлено" % (r + 1),
                      size=10.5, color=FIELD, bold=True))

    # Нижній висновок
    tb_res, _, _ = textbox(420, 440,
                           "Завдяки глибині перемішування D = 4 пачка з 4 суміжних помилок розсіюється\n"
                           "по одній на кожне кодове слово, укладаючись у спроможність коду (t = 1 помилка на блок).",
                           size=12, fill=FILL, stroke=LINE, sw=1.2, pad=8)
    p.append(tb_res)

    render(os.path.join(OUT, "interleaver-matrix.svg"), W, H, *p)


# ── 4. harq-retx-flow.svg: Взаємодія каналу з пам'яттю та HARQ ─────────────────

def fig_harq_flow():
    W, H = 840, 480
    p = []

    p.append(text(420, 26, "Гібридний ARQ (HARQ) у каналі з пам'яттю Гілберта–Елліота", size=16, bold=True))

    # Дві вертикальні часові осі: Передавач (TX) та Приймач (RX)
    tx_x = 180
    rx_x = 660
    t_top = 80
    t_bot = 420

    p.append(line(tx_x, t_top, tx_x, t_bot, color=MUTED, sw=2.0))
    p.append(line(rx_x, t_top, rx_x, t_bot, color=MUTED, sw=2.0))

    tb_tx, _, _ = textbox(tx_x, t_top - 18, "Передавач (TX)", size=13, fill="#ebf5fb", stroke="#2980b9", sw=1.5, pad=8)
    p.append(tb_tx)
    tb_rx, _, _ = textbox(rx_x, t_top - 18, "Приймач (RX)", size=13, fill="#ebf5fb", stroke="#2980b9", sw=1.5, pad=8)
    p.append(tb_rx)

    # Фонова смуга стану каналу справа
    cx_bg = 420
    p.append(rect(cx_bg - 75, 75, 150, 80, fill=GFILL, stroke=GSTRK, sw=1.2, rx=4))
    p.append(text(cx_bg, 115, "Канал у стані G\n(високий SNR)", size=11, color=GSTRK, bold=True))

    p.append(rect(cx_bg - 75, 165, 150, 140, fill=BFILL, stroke=BSTRK, sw=1.2, rx=4))
    p.append(text(cx_bg, 235, "Канал у стані B (пачка)\n(завмирання / низький SNR)", size=11, color=BSTRK, bold=True))

    p.append(rect(cx_bg - 75, 315, 150, 80, fill=GFILL, stroke=GSTRK, sw=1.2, rx=4))
    p.append(text(cx_bg, 355, "Канал у стані G\n(відновлення)", size=11, color=GSTRK, bold=True))

    # 1. Пакет 1 у стані G
    p.append(arrow(tx_x, 95, rx_x, 125, color=FIELD, sw=2.2))
    p.append(text(tx_x + 90, 100, "Пакет #1 [Дані + FEC]", size=11, color=FIELD, bold=True))
    p.append(text(rx_x + 65, 125, "CRC OK → декодовано", size=10.5, color=FIELD))
    p.append(arrow(rx_x, 135, tx_x, 155, color=FIELD, sw=1.8))
    p.append(text(rx_x - 90, 150, "ACK #1", size=11, color=FIELD, bold=True))

    # 2. Пакет 2 у стані B (перша спроба)
    p.append(arrow(tx_x, 185, rx_x, 215, color=POS, sw=2.2))
    p.append(text(tx_x + 90, 190, "Пакет #2 (Спроба 1)", size=11, color=POS, bold=True))
    p.append(text(rx_x + 85, 215, "CRC Помилка! Збереження\nм'яких бітів у HARQ-буфер", size=10, color=POS))
    p.append(arrow(rx_x, 230, tx_x, 250, color=POS, sw=1.8))
    p.append(text(rx_x - 90, 245, "NACK #2", size=11, color=POS, bold=True))

    # 3. Пакет 2 повторна передача (Chase Combining / IR)
    p.append(arrow(tx_x, 275, rx_x, 305, color="#d35400", sw=2.2))
    p.append(text(tx_x + 90, 280, "Пакет #2 (Спроба 2 / IR-надлишковість)", size=11, color="#d35400", bold=True))

    # 4. Об'єднання на приймачі
    p.append(text(rx_x + 90, 320, "Chase Combining: LLR₁ + LLR₂\nАкумуляція SNR перемагає пачку!\nCRC OK", size=10.5, color=FIELD, bold=True))
    p.append(arrow(rx_x, 345, tx_x, 365, color=FIELD, sw=1.8))
    p.append(text(rx_x - 90, 360, "ACK #2", size=11, color=FIELD, bold=True))

    # Нижній висновок
    tb_foot, _, _ = textbox(420, 445,
                            "Замість викидання пошкодженого пакета HARQ зберігає м'які рішення (LLR) у буфері.\n"
                            "Повторна передача накопичує енергію сигналу, забезпечуючи успішне декодування навіть у тривалій пачці.",
                            size=12, fill=FILL, stroke=LINE, sw=1.2, pad=8)
    p.append(tb_foot)

    render(os.path.join(OUT, "harq-retx-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_states()
    fig_burst_trace()
    fig_interleaver_matrix()
    fig_harq_flow()
    print("Всі фігури успішно згенеровано.")
