# -*- coding: utf-8 -*-
"""
Фігури для вставки ⚙️ «CLZ і бітова карта готовності»
(тема 4.10.4, файл ch27-s4-a-clz-bitmap.md).

fig-27-4a-clz-1-bitmap    — бітова карта готовності + крок CLZ
fig-27-4a-clz-2-scan-vs-clz — контраст: лінійне сканування проти одного CLZ

Стиль §9 AUTHORING: білий фон, sans-serif, рамки через textbox()/fitbox().
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# Фігура 1: бітова карта готовності — біти пріоритетів + CLZ
# viewBox 760×340
# ──────────────────────────────────────────────────────────────────────────────
def fig_bitmap():
    W, H = 760, 340

    # Покажемо 12 бітів (пріоритети 0..11), щоб уміщалося і читалося
    N_BITS = 12
    # які біти зведені в 1
    SET_BITS = {1, 3, 8}   # готові пріоритети
    HIGHEST  = 8           # найстарший (найлівіший) серед SET_BITS
    CLZ_COUNT = N_BITS - 1 - HIGHEST   # = 3 провідних нулі (біти 11..9 рівні 0)

    CELL_W = 46
    CELL_H = 46
    CELLS_LEFT = (W - N_BITS * CELL_W) / 2
    CELLS_TOP  = 100

    frags = []

    # ── Верхній підпис ──────────────────────────────────────────────────────
    frags.append(text(W / 2, 38,
                      "Бітова карта готовності (ready bitmap)",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62,
                      "Bit i = 1  →  на пріоритеті i є готова задача",
                      size=13, color=MUTED))

    # ── Клітинки-біти ───────────────────────────────────────────────────────
    # Найстарший біт (MSB) — ліворуч, молодший (LSB) — праворуч
    for i in range(N_BITS):
        bit_idx = N_BITS - 1 - i   # індекс пріоритету (11 → 0)
        cx = CELLS_LEFT + i * CELL_W + CELL_W / 2
        cy = CELLS_TOP + CELL_H / 2
        bx = CELLS_LEFT + i * CELL_W
        by = CELLS_TOP

        if bit_idx in SET_BITS:
            if bit_idx == HIGHEST:
                # найстарша одиниця — червоний акцент
                fill_c  = POS
                text_c  = "#ffffff"
                stroke_c = POS
            else:
                # інші одиниці — зелені
                fill_c  = FIELD
                text_c  = "#ffffff"
                stroke_c = FIELD
        else:
            # нульові біти — сірі
            fill_c  = "#e8eaed"
            text_c  = MUTED
            stroke_c = "#b0b4bb"

        frags.append(rect(bx, by, CELL_W - 2, CELL_H,
                          fill=fill_c, stroke=stroke_c, sw=2, rx=5))
        # значення біта
        val = "1" if bit_idx in SET_BITS else "0"
        frags.append(text(cx, cy + 6, val, size=18, color=text_c, bold=True))
        # номер пріоритету під клітинкою
        frags.append(text(cx, CELLS_TOP + CELL_H + 18,
                          str(bit_idx), size=11, color=MUTED))

    # підпис осі пріоритетів
    frags.append(text(W / 2, CELLS_TOP + CELL_H + 34,
                      "← пріоритет (11 = найвищий)      (0 = найнижчий) →",
                      size=11, color=MUTED))

    # ── Дужка-стрілка «clz = 3 провідних нулі» над кліт. 0..2 (біти 11..9) ──
    BKT_Y = CELLS_TOP - 18
    BKT_X0 = CELLS_LEFT + 1            # ліво — над бітом 11
    BKT_X1 = CELLS_LEFT + (N_BITS - 1 - HIGHEST) * CELL_W - 2  # право — перед бітом 8
    BKT_MID = (BKT_X0 + BKT_X1) / 2

    frags.append(line(BKT_X0, BKT_Y, BKT_X0, BKT_Y - 10, color=NEG, sw=2))
    frags.append(line(BKT_X1, BKT_Y, BKT_X1, BKT_Y - 10, color=NEG, sw=2))
    frags.append(line(BKT_X0, BKT_Y - 10, BKT_X1, BKT_Y - 10, color=NEG, sw=2))
    frags.append(arrow(BKT_MID, BKT_Y - 10, BKT_MID, BKT_Y - 42, color=NEG, sw=2))
    tb, _, _ = textbox(BKT_MID, BKT_Y - 56,
                       f"clz = {CLZ_COUNT}  (провідних нулі)",
                       size=13, fill="#eaf0fd", stroke=NEG, sw=1.5, color=NEG, bold=True)
    frags.append(tb)

    # ── Стрілка й мітка на найстаршій одиниці ───────────────────────────────
    HIGHEST_I = N_BITS - 1 - HIGHEST   # позиція клітинки ліворуч (0-based)
    HIGH_CX = CELLS_LEFT + HIGHEST_I * CELL_W + CELL_W / 2
    HIGH_TOP = CELLS_TOP - 4
    frags.append(arrow(HIGH_CX, HIGH_TOP - 6, HIGH_CX, HIGH_TOP - 28, color=POS, sw=2))
    tb2, _, _ = textbox(HIGH_CX, HIGH_TOP - 42,
                        "найстарша\nодиниця",
                        size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS)
    frags.append(tb2)

    # ── Формула-підсумок у рамці ─────────────────────────────────────────────
    FORM_Y = CELLS_TOP + CELL_H + 68
    tb3, _, _ = textbox(W / 2, FORM_Y,
                        f"найвищий = 31 − clz(bitmap) = 31 − {CLZ_COUNT} = {HIGHEST}",
                        size=14, fill="#fffde7", stroke="#f0a500", sw=2,
                        color=INK, bold=True, pad=14)
    frags.append(tb3)

    render(os.path.join(OUT, "fig-27-4a-clz-1-bitmap.svg"), W, H,
           *frags,
           title="Рис. 4.10.4a.1. Бітова карта готовності + CLZ")


# ──────────────────────────────────────────────────────────────────────────────
# Фігура 2: контраст — наївне сканування проти бітмапа+CLZ
# viewBox 760×380
# ──────────────────────────────────────────────────────────────────────────────
def fig_scan_vs_clz():
    W, H = 760, 380

    frags = []

    frags.append(text(W / 2, 34,
                      "Пошук найвищого готового пріоритету: два способи",
                      size=17, bold=True, color=INK))

    # ── Розмірності колонок ─────────────────────────────────────────────────
    COL_W = 310
    COL_H = 270
    LEFT_X  = 40
    RIGHT_X = W - 40 - COL_W
    TOP_Y   = 60

    # ── Ліва колонка: наївне сканування ─────────────────────────────────────
    frags.append(fitbox(LEFT_X, TOP_Y, COL_W, 36,
                        "Наївне сканування (O(N): цикл щотіку)",
                        size=13, fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True))

    LEVELS = [("рівень 7", False), ("рівень 6", False),
              ("рівень 5", False), ("рівень 4", True),   # перший непорожній
              ("рівень 3", False), ("рівень 2", False)]
    STEP_H = 34
    ARROW_X = LEFT_X + COL_W / 2
    SCAN_TOP = TOP_Y + 42

    for idx, (lbl, found) in enumerate(LEVELS):
        sy = SCAN_TOP + idx * STEP_H
        fill_c = FIELD if found else "#f4f6f8"
        stroke_c = FIELD if found else "#b0b4bb"
        frags.append(rect(LEFT_X + 20, sy, COL_W - 40, 28,
                          fill=fill_c, stroke=stroke_c, sw=1.5, rx=5))
        frags.append(text(ARROW_X, sy + 18,
                          lbl + (" ← є готова!" if found else " — порожній"),
                          size=12,
                          color="#ffffff" if found else MUTED))
        if idx < len(LEVELS) - 1:
            frags.append(arrow(ARROW_X, sy + 28, ARROW_X, sy + STEP_H - 2,
                               color=POS, sw=1.5))

    # нижній підпис лівої колонки
    LEFT_BOT = SCAN_TOP + len(LEVELS) * STEP_H + 8
    tb_l, _, _ = textbox(LEFT_X + COL_W / 2, LEFT_BOT + 14,
                         "O(N) — залежить від числа рівнів",
                         size=12, fill="#fdecea", stroke=POS, sw=1.5, color=POS)
    frags.append(tb_l)

    # ── Права колонка: бітмапа + CLZ ────────────────────────────────────────
    frags.append(fitbox(RIGHT_X, TOP_Y, COL_W, 36,
                        "Бітмапа + CLZ (O(1): один такт)",
                        size=13, fill="#eafaf1", stroke=FIELD, sw=2, color=FIELD, bold=True))

    # Схематичне 8-бітне слово
    BITS_TOP = TOP_Y + 50
    BITS_LEFT = RIGHT_X + 14
    NBITS = 8
    BW = (COL_W - 28) / NBITS
    BH = 36
    set_bits_r = {4}   # біт 4 — найвищий готовий
    for i in range(NBITS):
        bit_idx_r = NBITS - 1 - i
        bx = BITS_LEFT + i * BW
        if bit_idx_r in set_bits_r:
            fc = POS; sc = POS; tc = "#ffffff"
        elif bit_idx_r in {1}:
            fc = FIELD; sc = FIELD; tc = "#ffffff"
        else:
            fc = "#e8eaed"; sc = "#b0b4bb"; tc = MUTED
        frags.append(rect(bx, BITS_TOP, BW - 2, BH,
                          fill=fc, stroke=sc, sw=1.5, rx=4))
        val = "1" if (bit_idx_r in set_bits_r or bit_idx_r in {1}) else "0"
        frags.append(text(bx + BW / 2, BITS_TOP + BH / 2 + 6,
                          val, size=15, color=tc, bold=True))

    # підпис «bitmap = 0b00010010»
    frags.append(text(RIGHT_X + COL_W / 2, BITS_TOP + BH + 18,
                      "readyBits = 0b00010010",
                      size=12, color=MUTED))

    # стрілка від bitmap до результату
    ARROW_R_X = RIGHT_X + COL_W / 2
    ARROW_TOP = BITS_TOP + BH + 34
    ARROW_BOT = ARROW_TOP + 56
    frags.append(arrow(ARROW_R_X, ARROW_TOP, ARROW_R_X, ARROW_BOT, color=FIELD, sw=2.5))
    tb_mid, _, _ = textbox(ARROW_R_X, (ARROW_TOP + ARROW_BOT) / 2,
                           "одна інструкція\nnsau / clz",
                           size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    frags.append(tb_mid)

    # результат у рамці
    tb_res, _, _ = textbox(ARROW_R_X, ARROW_BOT + 26,
                           "найвищий = 4",
                           size=15, fill="#fffde7", stroke="#f0a500", sw=2,
                           color=INK, bold=True, pad=14)
    frags.append(tb_res)

    # нижній підпис правої колонки
    RIGHT_BOT = ARROW_BOT + 62
    tb_r, _, _ = textbox(ARROW_R_X, RIGHT_BOT + 14,
                         "O(1) — не залежить від числа рівнів",
                         size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, color=FIELD)
    frags.append(tb_r)

    # ── Роздільник між колонками ─────────────────────────────────────────────
    MID_X = W / 2
    frags.append(line(MID_X, TOP_Y + 10, MID_X, TOP_Y + COL_H,
                      color="#cccccc", sw=1.5, dash="6,4"))
    frags.append(text(MID_X, TOP_Y + COL_H / 2 + 10,
                      "vs", size=20, color=MUTED, bold=True))

    render(os.path.join(OUT, "fig-27-4a-clz-2-scan-vs-clz.svg"), W, H,
           *frags,
           title="Рис. 4.10.4a.2. Сканування O(N) проти CLZ O(1)")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_bitmap()
    print("  fig-27-4a-clz-1-bitmap.svg: OK")
    fig_scan_vs_clz()
    print("  fig-27-4a-clz-2-scan-vs-clz.svg: OK")
    print("Done. Files in ./img/")
