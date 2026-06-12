# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 r09-s6-c-i2s-mic (I2S-мікрофон INMP441-класу).
Дві фігури:
  fig-r09-6c-1-block.svg  — блок-схема корпусу INMP441-класу
  fig-r09-6c-2-i2s-timing.svg — часова діаграма SCK/WS/SD

Запуск: python figs-r09-s6-c-i2s-mic.py
Вивід → ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.9.6c.1 — Блок-схема корпусу INMP441-класу ──────────────────────────
def fig1_block():
    W, H = 820, 400

    parts = []

    # ── Заголовок ──
    parts.append(text(W / 2, 30, "Усередині корпусу INMP441-класу", size=17, bold=True))
    parts.append(text(W / 2, 52, "мікрофонна капсула → сигма-дельта АЦП → I2S-передавач; назовні — три цифрові лінії",
                      size=11, color=MUTED))

    # ── Великий прямокутник «корпус мікрофона» ──
    parts.append(rect(60, 72, 530, 270, fill="#f0f4ff", stroke="#4a6fa5", sw=2.5, rx=14))
    parts.append(text(325, 92, "Корпус мікрофона INMP441 (3 × 4 мм)", size=12, color="#4a6fa5", bold=True))

    # ── Блок 1: MEMS-капсула ──
    tb1, w1, h1 = textbox(155, 200, "MEMS\nкапсула", size=13, pad=14,
                           fill=FILL, stroke=LINE, bold=True, min_w=110)
    parts.append(tb1)

    # ── Блок 2: АЦП (сигма-дельта) ──
    tb2, w2, h2 = textbox(325, 200, "АЦП\n(σ-Δ)", size=13, pad=14,
                           fill=FILL, stroke=LINE, bold=True, min_w=110)
    parts.append(tb2)

    # ── Блок 3: I2S-передавач ──
    tb3, w3, h3 = textbox(500, 200, "I2S\nпередавач", size=13, pad=14,
                           fill=FILL, stroke=LINE, bold=True, min_w=110)
    parts.append(tb3)

    # ── Стрілки між блоками всередині корпусу ──
    # Капсула → АЦП
    parts.append(arrow(155 + w1 / 2, 200, 325 - w2 / 2, 200, color=LINE, sw=2))
    parts.append(text(240, 185, "звуковий\nтиск→струм", size=9, color=MUTED))

    # АЦП → I2S-передавач
    parts.append(arrow(325 + w2 / 2, 200, 500 - w3 / 2, 200, color=LINE, sw=2))
    parts.append(text(412, 185, "цифр.\nвідлік", size=9, color=MUTED))

    # ── Вихідні лінії назовні ──
    # Права стінка корпусу → лінії I2S
    x_out_start = 590 + 20   # трохи за корпус
    x_out_end   = 750

    line_y = {"SCK": 160, "WS": 200, "SD": 240}
    line_colors = {"SCK": "#2457d6", "WS": "#27ae60", "SD": "#c0392b"}
    line_labels = {
        "SCK": "SCK — бітовий такт",
        "WS":  "WS  — вибір каналу",
        "SD":  "SD  — дані (24 біти)",
    }

    for sig, y in line_y.items():
        parts.append(arrow(x_out_start - 20, y, x_out_end - 20, y,
                           color=line_colors[sig], sw=2))
        parts.append(text(x_out_end - 16, y + 5, line_labels[sig],
                          size=11, color=line_colors[sig], anchor="start"))

    # Підпис «три лінії I2S»
    parts.append(text(x_out_start + 40, 290, "три лінії I2S", size=10, color=MUTED, anchor="middle"))

    # Живлення (VDD/GND) — зверху й знизу корпусу, символічно
    parts.append(text(325, 122, "VDD / GND — живлення", size=10, color=MUTED))

    # ── Підсумкова рамка внизу ──
    note = "Мікроконтролер отримує готові 24-бітні PCM-відліки — аналогового тракту немає"
    tb_note, wn, hn = textbox(W / 2, 370, note, size=11, pad=10,
                               fill="#f0fff4", stroke="#27ae60", sw=1.5, min_w=640)
    parts.append(tb_note)

    render(os.path.join(OUT, "fig-r09-6c-1-block.svg"), W, H, *parts,
           title=None)
    print("wrote fig-r09-6c-1-block.svg")


# ── Рис. 4.9.6c.2 — Часова діаграма I2S: SCK / WS / SD ───────────────────────
def fig2_timing():
    W, H = 860, 420

    parts = []

    # ── Заголовок ──
    parts.append(text(W / 2, 28, "Часова діаграма I2S: SCK / WS / SD", size=17, bold=True))
    parts.append(text(W / 2, 50, "SCK тактує кожен біт; WS перемикається раз на відлік; SD несе біти MSB-first",
                      size=11, color=MUTED))

    # ── Параметри сітки ──
    LEFT   = 90    # ліво підпису сигналу
    X0     = 160   # початок хвилі
    X1     = 780   # кінець хвилі
    ROW_H  = 72    # відстань між рядками
    Y_SCK  = 110
    Y_WS   = 182
    Y_SD   = 260
    SIG_H  = 32    # висота прямокутної хвилі

    CLK_COL  = "#2457d6"
    WS_COL   = "#27ae60"
    SD_COL   = "#c0392b"

    # ── Підписи сигналів ──
    for label, y, col in [("SCK", Y_SCK, CLK_COL), ("WS", Y_WS, WS_COL), ("SD", Y_SD, SD_COL)]:
        parts.append(text(LEFT - 6, y + SIG_H / 2 + 5, label, size=13, color=col,
                          anchor="end", bold=True))
        # базова лінія
        parts.append(line(X0, y + SIG_H, X1, y + SIG_H, color="#e0e0e0", sw=1))

    # ── SCK: 16 пар пів-тактів (рівномірний меандр) ──
    n_bits = 16
    bit_w  = (X1 - X0) / n_bits   # ширина одного біта
    clk_half = bit_w / 2

    for i in range(n_bits):
        x = X0 + i * bit_w
        # висхідний фронт
        parts.append(line(x, Y_SCK + SIG_H, x, Y_SCK, color=CLK_COL, sw=1.8))
        # верхня частина
        parts.append(line(x, Y_SCK, x + clk_half, Y_SCK, color=CLK_COL, sw=1.8))
        # спадний фронт
        parts.append(line(x + clk_half, Y_SCK, x + clk_half, Y_SCK + SIG_H, color=CLK_COL, sw=1.8))
        # нижня частина
        parts.append(line(x + clk_half, Y_SCK + SIG_H, x + bit_w, Y_SCK + SIG_H, color=CLK_COL, sw=1.8))
    # Завершити останній правий фронт
    parts.append(line(X1, Y_SCK + SIG_H, X1, Y_SCK, color=CLK_COL, sw=1.8))

    # ── WS: перемикається посередині (показуємо один відлік + перехід до наступного) ──
    # Лівий канал — перші 8 бітів (WS = LOW), правий — наступні 8 бітів (WS = HIGH)
    ws_mid = X0 + 8 * bit_w

    # LOW зліва
    parts.append(line(X0, Y_WS + SIG_H, ws_mid, Y_WS + SIG_H, color=WS_COL, sw=2.2))
    # фронт вгору
    parts.append(line(ws_mid, Y_WS + SIG_H, ws_mid, Y_WS, color=WS_COL, sw=2.2))
    # HIGH справа
    parts.append(line(ws_mid, Y_WS, X1, Y_WS, color=WS_COL, sw=2.2))

    # Підписи каналів
    parts.append(text(X0 + 4 * bit_w, Y_WS - 8, "ЛІВИЙ канал (WS = LOW)", size=9,
                      color=WS_COL, anchor="middle"))
    parts.append(text(X0 + 12 * bit_w, Y_WS - 8, "ПРАВИЙ канал (WS = HIGH)", size=9,
                      color=WS_COL, anchor="middle"))

    # Вертикальна позначка переходу WS
    parts.append(line(ws_mid, Y_SCK - 10, ws_mid, Y_SD + SIG_H + 14,
                      color="#aaaaaa", sw=1, dash="4,3"))

    # ── SD: MSB-first, 24 значущих у 32-бітному слоті ──
    # Перші 8 бітів: показуємо схематичні дані (лівий відлік)
    # Слот 32 біти: старші 24 — значущі, молодші 8 — нулі
    bit_labels_left  = ["B23","B22","B21","B20","B19","B18","…","B0"]   # 8 "бітів" зліва
    bit_labels_right = ["B23","B22","B21","B20","B19","B18","…","00"]   # 8 справа

    for i, label in enumerate(bit_labels_left):
        x = X0 + i * bit_w
        hi = (i % 3 != 1)   # чергуємо H/L для наочності
        y_top = Y_SD if hi else Y_SD + SIG_H / 2
        y_bot = Y_SD + SIG_H if not hi else Y_SD + SIG_H / 2
        # просто прямокутник-клітина
        parts.append(rect(x + 1, Y_SD + 1, bit_w - 2, SIG_H - 2,
                          fill="#fdecea", stroke=SD_COL, sw=1.2, rx=2))
        parts.append(text(x + bit_w / 2, Y_SD + SIG_H / 2 + 5, label, size=8,
                          color=SD_COL, anchor="middle"))

    for i, label in enumerate(bit_labels_right):
        x = ws_mid + i * bit_w
        fill = "#fdecea" if label != "00" else "#f9f9f9"
        parts.append(rect(x + 1, Y_SD + 1, bit_w - 2, SIG_H - 2,
                          fill=fill, stroke=SD_COL, sw=1.2, rx=2))
        parts.append(text(x + bit_w / 2, Y_SD + SIG_H / 2 + 5, label, size=8,
                          color=SD_COL, anchor="middle"))

    # ── Підпис зсуву >>8 ──
    note_x = X1 + 6
    tb_shift, ws_, hs_ = textbox(X1 - 90, Y_SD + SIG_H + 30,
                                  "молодші 8 = 0\n→ зсув >>8 у коді",
                                  size=9, pad=6, fill="#fff8f0",
                                  stroke="#e08030", sw=1.2, min_w=130)
    parts.append(tb_shift)

    # ── Нижня рамка-пояснення ──
    expl = "Два тактових сигнали (SCK + WS) — бо звук строго ритмічний і канал «вшитий» у такт"
    tb_ex, wx, hx = textbox(W / 2, 390, expl, size=10, pad=10,
                             fill="#f0f4ff", stroke="#4a6fa5", sw=1.5, min_w=620)
    parts.append(tb_ex)

    render(os.path.join(OUT, "fig-r09-6c-2-i2s-timing.svg"), W, H, *parts,
           title=None)
    print("wrote fig-r09-6c-2-i2s-timing.svg")


if __name__ == "__main__":
    fig1_block()
    fig2_timing()
    print("Done.")
