# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 🔌 4.9.6c — «SPI-дисплей ILI9341-класу: чому кадр без DMA смикається».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-4-9-6c-1-frame-cost.svg  — вартість кадру на SPI і де застрягає ядро без DMA
  fig-4-9-6c-2-dma-vs-nodma.svg — таймлайн без DMA і з DMA + ping-pong
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.9.6c.1 — вартість кадру і де застрягає ядро без DMA ─────────────
def fig1_frame_cost():
    W, H = 860, 330
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Один кадр 240×320 RGB565 на SPI 40 МГц: де минає час", 16, INK, "middle", bold=True))
    frags.append(text(W / 2, 48, "вузьке місце — не панель і не шина, а ядро, прикуте до регістра SPI", 12, MUTED, "middle"))

    # Мітки осей
    T_FRAME = 30.7  # мс
    X0 = 80   # ліво
    X1 = 760  # право
    Y_SPI = 100
    Y_CPU = 190

    # Вісь часу (горизонтальна лінія)
    frags.append(line(X0, 80, X1, 80, MUTED, 1, dash="4,3"))
    frags.append(text(X0, 74, "0 мс", 10, MUTED, "middle"))
    frags.append(text(X1, 74, f"≈{T_FRAME} мс", 10, MUTED, "middle"))

    # — Доріжка 1: SPI-шина —
    frags.append(text(X0 - 10, Y_SPI + 14, "SPI-шина", 12, INK, "end", bold=True))
    # Блок «150 КіБ на дроті» — суцільний, нейтральний колір
    frags.append(rect(X0, Y_SPI, X1 - X0, 32, FILL, INK, 1.5, 4))
    tb, tw, th = textbox((X0 + X1) / 2, Y_SPI + 16,
                          "150 КіБ пікселів (RGB565) → 1228800 біт / 40 МГц ≈ 30.7 мс «на дроті»",
                          size=11, fill=FILL, stroke=INK)
    frags.append(tb)

    # Міні-обчислення у кутку (права секція)
    calc_x = X1 + 14
    frags.append(text(calc_x, Y_SPI + 8,  "240×320 = 76 800 пікс.", 9, MUTED, "start"))
    frags.append(text(calc_x, Y_SPI + 20, "× 2 байти/пікс. = 150 КіБ", 9, MUTED, "start"))
    frags.append(text(calc_x, Y_SPI + 32, "× 8 біт / 40 МГц ≈ 30.7 мс", 9, MUTED, "start"))

    # — Доріжка 2: ядро без DMA —
    frags.append(text(X0 - 10, Y_CPU + 14, "Ядро (без DMA)", 12, POS, "end", bold=True))

    # Суцільний блок «вантажу байт у регістр SPI» — акцент POS (зайняте ядро)
    BW = X1 - X0  # ширина зайнятого блоку
    frags.append(rect(X0, Y_CPU, BW, 32, "#fde8e8", POS, 1.8, 4))
    tb2, tw2, th2 = textbox(X0 + BW / 2, Y_CPU + 16,
                             "безперервно: прочитати байт з RAM → записати в SPI DR → чекати TX-empty → ...",
                             size=11, fill="#fde8e8", stroke=POS, color=POS)
    frags.append(tb2)

    # Порожня зона «обчислення наступного кадру — нема часу»
    EMPTY_W = 160
    frags.append(rect(X1, Y_CPU, EMPTY_W, 32, FILL, MUTED, 1, 4))
    tb3, tw3, th3 = textbox(X1 + EMPTY_W / 2, Y_CPU + 16,
                             "наступний кадр:\nнема часу",
                             size=10, fill=FILL, stroke=MUTED, color=MUTED)
    frags.append(tb3)

    # Стрілка-виноска: стеля ≈ 32 кадри/с
    frags.append(line(X1, Y_SPI - 4, X1, 62, MUTED, 1, dash="3,2"))
    tb4, tw4, th4 = textbox(X1 - 70, 52, "стеля ≈ 32 кадри/с", size=10, fill="#fff8e8", stroke=FIELD, color=FIELD)
    frags.append(tb4)

    # Висновок внизу
    frags.append(rect(X0, 248, X1 - X0, 60, "#fde8e8", POS, 1.4, 8))
    tb5, tw5, th5 = textbox((X0 + X1) / 2, 278,
                             "Вузьке місце — не шина і не панель:\nядро 30+ мс не робить нічого, крім «байт → регістр SPI».",
                             size=12, fill="#fde8e8", stroke=POS, color=POS)
    frags.append(tb5)

    render(os.path.join(OUT, "fig-4-9-6c-1-frame-cost.svg"), W, H + 10, *frags,
           title=None)
    print("wrote fig-4-9-6c-1-frame-cost.svg")


# ── Рис. 4.9.6c.2 — таймлайн без DMA і з DMA + ping-pong ───────────────────
def fig2_dma_vs_nodma():
    W, H = 860, 380
    frags = []

    frags.append(text(W / 2, 28, "Той самий кадр: без DMA і з DMA + два буфери (ping-pong)", 16, INK, "middle", bold=True))
    frags.append(text(W / 2, 48, "та сама шина, той самий такт — але ядро або прикуте, або вільне", 12, MUTED, "middle"))

    X0 = 110
    X1 = 760
    BW = X1 - X0   # ширина одного кадру
    LH = 36        # висота доріжки

    # ━━━━ ВЕРХ: БЕЗ DMA ━━━━
    Y0 = 70
    frags.append(text(X0 - 10, Y0 - 12, "БЕЗ DMA", 13, POS, "end", bold=True))

    # Доріжка «CPU» — суцільний зайнятий
    frags.append(text(X0 - 10, Y0 + LH / 2 + 4, "CPU", 11, POS, "end"))
    frags.append(rect(X0, Y0, BW, LH, "#fde8e8", POS, 1.8, 4))
    tb, tw, th = textbox(X0 + BW / 2, Y0 + LH / 2,
                          "байт → SPI DR → чекати → байт → ... (150 КіБ без зупинки)",
                          size=11, fill="#fde8e8", stroke=POS, color=POS)
    frags.append(tb)

    # Доріжка «DMA/шина» — та сама зайнята (ядро саме й жене)
    frags.append(text(X0 - 10, Y0 + LH + LH / 2 + 4, "Шина", 11, MUTED, "end"))
    frags.append(rect(X0, Y0 + LH + 4, BW, LH, "#fde8e8", POS, 1.2, 4))
    tb2, _, _ = textbox(X0 + BW / 2, Y0 + LH + 4 + LH / 2,
                         "SPI зайнятий (дані від CPU)",
                         size=11, fill="#fde8e8", stroke=POS, color=POS)
    frags.append(tb2)

    # Наступний кадр — спізнюється (зсунутий праворуч)
    DELAY = 80
    frags.append(rect(X1 + DELAY, Y0, 90, LH, FILL, MUTED, 1, 4))
    tb3, _, _ = textbox(X1 + DELAY + 45, Y0 + LH / 2, "наступний\nкадр", size=10, fill=FILL, stroke=MUTED, color=MUTED)
    frags.append(tb3)
    frags.append(line(X1, Y0 + LH / 2, X1 + DELAY, Y0 + LH / 2, MUTED, 1.2, dash="4,3"))
    frags.append(text(X1 + DELAY / 2, Y0 + LH / 2 - 8, "спізнення", 9, MUTED, "middle"))

    SEP_Y = Y0 + LH * 2 + 30

    # Розділювач
    frags.append(line(50, SEP_Y, W - 30, SEP_Y, MUTED, 1, dash="6,4"))

    # ━━━━ НИЗ: DMA + PING-PONG ━━━━
    Y1 = SEP_Y + 20
    frags.append(text(X0 - 10, Y1 - 12, "DMA + 2 буфери", 13, FIELD, "end", bold=True))

    # Доріжка «CPU»: малює буфер B поки DMA жене A
    frags.append(text(X0 - 10, Y1 + LH / 2 + 4, "CPU", 11, FIELD, "end"))
    HALF = BW // 2

    # Перша половина: малює буфер B
    frags.append(rect(X0, Y1, HALF, LH, "#e8f8ef", FIELD, 1.8, 4))
    tb4, _, _ = textbox(X0 + HALF / 2, Y1 + LH / 2,
                         "малює буфер B (фізика, анімація...)",
                         size=11, fill="#e8f8ef", stroke=FIELD, color=FIELD)
    frags.append(tb4)

    # Лінія обміну
    SWAP_X = X0 + HALF
    frags.append(line(SWAP_X, Y1 - 6, SWAP_X, Y1 + LH * 2 + 14, POS, 2))
    frags.append(text(SWAP_X, Y1 - 12, "обмін A↔B", 10, POS, "middle", bold=True))

    # Друга половина: знову малює (наступний буфер)
    frags.append(rect(SWAP_X, Y1, HALF, LH, "#e8f8ef", FIELD, 1.8, 4))
    tb5, _, _ = textbox(SWAP_X + HALF / 2, Y1 + LH / 2,
                         "малює буфер A (наступний кадр)",
                         size=11, fill="#e8f8ef", stroke=FIELD, color=FIELD)
    frags.append(tb5)

    # Доріжка «DMA/шина»: жене буфер A, потім B
    frags.append(text(X0 - 10, Y1 + LH + LH / 2 + 4, "DMA/Шина", 11, NEG, "end"))
    frags.append(rect(X0, Y1 + LH + 4, HALF, LH, "#e8eefb", NEG, 1.8, 4))
    tb6, _, _ = textbox(X0 + HALF / 2, Y1 + LH + 4 + LH / 2,
                         "DMA жене буфер A → SPI",
                         size=11, fill="#e8eefb", stroke=NEG, color=NEG)
    frags.append(tb6)

    frags.append(rect(SWAP_X, Y1 + LH + 4, HALF, LH, "#e8eefb", NEG, 1.8, 4))
    tb7, _, _ = textbox(SWAP_X + HALF / 2, Y1 + LH + 4 + LH / 2,
                         "DMA жене буфер B → SPI",
                         size=11, fill="#e8eefb", stroke=NEG, color=NEG)
    frags.append(tb7)

    # Наступний кадр — одразу після (кадри впритул)
    frags.append(rect(X1, Y1, 60, LH, "#e8f8ef", FIELD, 1.2, 4))
    tb8, _, _ = textbox(X1 + 30, Y1 + LH / 2, "...", size=12, fill="#e8f8ef", stroke=FIELD, color=FIELD)
    frags.append(tb8)

    # Легенда
    LEG_Y = Y1 + LH * 2 + 24
    frags.append(rect(X0, LEG_Y, 180, 24, "#fde8e8", POS, 1, 6))
    tb9, _, _ = textbox(X0 + 90, LEG_Y + 12, "ядро прикуте / зайняте", size=10, fill="#fde8e8", stroke=POS, color=POS)
    frags.append(tb9)

    frags.append(rect(X0 + 200, LEG_Y, 180, 24, "#e8f8ef", FIELD, 1, 6))
    tba, _, _ = textbox(X0 + 290, LEG_Y + 12, "паралельна корисна робота", size=10, fill="#e8f8ef", stroke=FIELD, color=FIELD)
    frags.append(tba)

    frags.append(rect(X0 + 400, LEG_Y, 140, 24, "#e8eefb", NEG, 1, 6))
    tbb, _, _ = textbox(X0 + 470, LEG_Y + 12, "DMA жене шину", size=10, fill="#e8eefb", stroke=NEG, color=NEG)
    frags.append(tbb)

    render(os.path.join(OUT, "fig-4-9-6c-2-dma-vs-nodma.svg"), W, H, *frags, title=None)
    print("wrote fig-4-9-6c-2-dma-vs-nodma.svg")


if __name__ == "__main__":
    fig1_frame_cost()
    fig2_dma_vs_nodma()
    print("done.")
