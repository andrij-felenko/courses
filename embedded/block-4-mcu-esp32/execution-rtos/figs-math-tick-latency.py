# -*- coding: utf-8 -*-
"""
Фігури для вставки 🧮 «Тік 1 мс: квант, джитер, tickless»
(тема 4.10.4, файл ch27-s4-m-tick-latency.md).

fig-27-4m-1-quantize   — квантування часу тіком; vTaskDelay(1) ≠ 1 мс точно
fig-27-4m-2-latency-budget — бюджет латентності: Lквант + Lчерга, джитер = Tтік

Стиль §9 AUTHORING: білий фон, sans-serif, рамки через textbox()/fitbox().
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# Фігура 1: квантування часу тіком — vTaskDelay(1) не дорівнює рівно 1 мс
# viewBox 720×300
# ──────────────────────────────────────────────────────────────────────────────
def fig_quantize():
    W, H = 720, 300
    frags = []

    # --- осьова лінія часу ---
    AXIS_Y = 160
    AXIS_X0, AXIS_X1 = 60, 660
    frags.append(arrow(AXIS_X0, AXIS_Y, AXIS_X1, AXIS_Y, color=INK, sw=2))
    frags.append(text(AXIS_X1 + 14, AXIS_Y + 5, "t", size=15, color=INK, anchor="middle", italic=True))

    # --- тік-мітки (0, 1, 2, 3 мс) ---
    TICK_MS = [0, 1, 2, 3]
    TICK_STEP = 170   # px на 1 мс
    TICK_X0 = 90      # позиція t=0 px

    def tick_x(ms):
        return TICK_X0 + ms * TICK_STEP

    for ms in TICK_MS:
        tx = tick_x(ms)
        frags.append(line(tx, AXIS_Y - 18, tx, AXIS_Y + 18, color=INK, sw=2))
        frags.append(text(tx, AXIS_Y + 36, f"{ms} мс", size=13, color=INK, anchor="middle"))

    # --- мітки «тік №0», «тік №1», «тік №2» між межами ---
    for i in range(3):
        cx = tick_x(i) + TICK_STEP / 2
        frags.append(text(cx, AXIS_Y - 30, f"тік №{i}", size=12, color=MUTED, anchor="middle"))

    # --- момент виклику vTaskDelay(1) всередині тіку №0 ---
    CALL_X = tick_x(0) + 0.3 * TICK_STEP   # t = 0.3 мс

    # пунктирна вертикаль до осі — «втрачений залишок»
    frags.append(line(CALL_X, AXIS_Y - 55, CALL_X, AXIS_Y, color=MUTED, sw=1.5, dash="5,4"))

    # стрілка «виклик vTaskDelay(1)»
    frags.append(arrow(CALL_X, AXIS_Y - 90, CALL_X, AXIS_Y - 58, color=POS, sw=2))
    tb, tw, th = textbox(CALL_X, AXIS_Y - 108, "виклик\nvTaskDelay(1)", size=12,
                         fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(tb)

    # --- «втрачений залишок» від 0.3 до 1 мс (сірий пунктир під віссю) ---
    LOST_Y = AXIS_Y + 60
    frags.append(line(CALL_X, LOST_Y, tick_x(1), LOST_Y, color=MUTED, sw=2.5, dash="6,4"))
    frags.append(line(CALL_X, LOST_Y - 8, CALL_X, LOST_Y + 8, color=MUTED, sw=1.5))
    frags.append(line(tick_x(1), LOST_Y - 8, tick_x(1), LOST_Y + 8, color=MUTED, sw=1.5))
    frags.append(text((CALL_X + tick_x(1)) / 2, LOST_Y + 22, "«втрачений» залишок тіку №0", size=11, color=MUTED, anchor="middle"))

    # --- зелена смуга: фактично проспаний інтервал (t=1 до t=2) ---
    SLEEP_Y = AXIS_Y - 6
    SLEEP_H = 12
    frags.append(f'<rect x="{tick_x(1)}" y="{SLEEP_Y - SLEEP_H // 2}" '
                 f'width="{TICK_STEP}" height="{SLEEP_H}" '
                 f'fill="{FIELD}" fill-opacity="0.35" stroke="{FIELD}" stroke-width="1.5" rx="3"/>')

    # дужка-підпис "1 тік = 1 мс (гарантований)"
    BKT_Y = AXIS_Y - 22
    frags.append(line(tick_x(1), BKT_Y, tick_x(2), BKT_Y, color=FIELD, sw=2))
    frags.append(line(tick_x(1), BKT_Y, tick_x(1), BKT_Y + 8, color=FIELD, sw=2))
    frags.append(line(tick_x(2), BKT_Y, tick_x(2), BKT_Y + 8, color=FIELD, sw=2))
    frags.append(text((tick_x(1) + tick_x(2)) / 2, BKT_Y - 10,
                      "1 тік відлічено (гарантований мінімум)", size=11, color=FIELD, anchor="middle"))

    # --- велика дужка: фактична пауза від виклику = (0, 1] мс ---
    REAL_Y = AXIS_Y + 78
    frags.append(line(CALL_X, REAL_Y, tick_x(2), REAL_Y, color=NEG, sw=2))
    frags.append(line(CALL_X, REAL_Y - 8, CALL_X, REAL_Y + 8, color=NEG, sw=2))
    frags.append(line(tick_x(2), REAL_Y - 8, tick_x(2), REAL_Y + 8, color=NEG, sw=2))
    frags.append(text((CALL_X + tick_x(2)) / 2, REAL_Y + 20,
                      "реальна пауза: (0 мс, 1 мс] від моменту виклику", size=12, color=NEG, anchor="middle"))

    # --- нижній висновок ---
    frags.append(text(W / 2, H - 12,
                      "vTaskDelay(N) → пауза у (N−1, N]·Tтік від моменту виклику; для N=1: (0, 1] мс",
                      size=12, color=INK, anchor="middle"))

    render(os.path.join(OUT, "fig-27-4m-1-quantize.svg"), W, H,
           *frags, title="Рис. 4.10.4m.1. Квантування часу тіком: vTaskDelay(1) ≠ рівно 1 мс")


# ──────────────────────────────────────────────────────────────────────────────
# Фігура 2: бюджет латентності пробудження — Lквант + Lчерга, джитер = Tтік
# viewBox 720×340
# ──────────────────────────────────────────────────────────────────────────────
def fig_latency_budget():
    W, H = 720, 340
    frags = []

    # ── Константи розмітки ──
    LEFT = 60
    RIGHT = 660
    BAR_W = RIGHT - LEFT   # 600 px = 1 мс + черга
    # Тік займає 2/3 смуги (≈1 мс), черга 1/3
    TICK_FRAC = 0.55
    TICK_PX = BAR_W * TICK_FRAC   # ~330 px = 1 мс

    # ── Ряд 1: «найкращий випадок» ──
    ROW1_Y = 90
    ROW_H = 44
    LABEL_X = LEFT - 8

    # мітка рядка
    frags.append(text(LABEL_X, ROW1_Y + ROW_H / 2 + 5, "найкращий", size=13,
                      color=FIELD, anchor="end", bold=True))

    # Lквант = 0 (подія на самій межі тіку) → зелений сегмент нульової ширини,
    # але покажемо мінімальний блок + підпис
    frags.append(rect(LEFT, ROW1_Y, 4, ROW_H, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    frags.append(text(LEFT + 2 + 50, ROW1_Y + ROW_H / 2 + 5,
                      "Lквант = 0 (подія на межі тіку)", size=12, color=FIELD, anchor="middle"))

    # Lчерга: жовто-бурштиновий сегмент — задача одразу біжить
    AMB = "#d4830a"
    LAMB2 = "#fff3cd"
    # у найкращому немає черги — показати символічно малим
    QUEUE_W1 = 80
    frags.append(rect(LEFT + 4, ROW1_Y, QUEUE_W1, ROW_H, fill=LAMB2, stroke=AMB, sw=1.5, rx=3))
    frags.append(text(LEFT + 4 + QUEUE_W1 / 2, ROW1_Y + ROW_H / 2 + 5,
                      "Lчерга ≈ 0", size=12, color=AMB, anchor="middle"))

    # ── Ряд 2: «найгірший випадок» ──
    ROW2_Y = ROW1_Y + ROW_H + 30

    frags.append(text(LABEL_X, ROW2_Y + ROW_H / 2 + 5, "найгірший", size=13,
                      color=POS, anchor="end", bold=True))

    # Lквант ≈ 1 мс (майже повний тік)
    frags.append(rect(LEFT, ROW2_Y, TICK_PX, ROW_H, fill="#d5f0e0", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(LEFT + TICK_PX / 2, ROW2_Y + ROW_H / 2 + 5,
                      "Lквант ≈ Tтік = 1 мс (чекати тіку)", size=13, color=FIELD, anchor="middle", bold=True))

    # Lчерга
    QUEUE_W2 = BAR_W - TICK_PX
    frags.append(rect(LEFT + TICK_PX, ROW2_Y, QUEUE_W2, ROW_H, fill=LAMB2, stroke=AMB, sw=1.5, rx=3))
    frags.append(text(LEFT + TICK_PX + QUEUE_W2 / 2, ROW2_Y + ROW_H / 2 + 5,
                      "Lчерга ≥ 0\n(вищі/рівні задачі)", size=11, color=AMB, anchor="middle"))

    # ── Фігурна дужка «джитер = worst − best = Tтік = 1 мс» праворуч ──
    BKT_X = RIGHT + 20
    BKT_TOP = ROW1_Y + ROW_H / 2
    BKT_BOT = ROW2_Y + ROW_H / 2
    BKT_MID = (BKT_TOP + BKT_BOT) / 2
    frags.append(line(BKT_X, BKT_TOP, BKT_X + 10, BKT_TOP, color=INK, sw=1.5))
    frags.append(line(BKT_X + 10, BKT_TOP, BKT_X + 10, BKT_MID - 5, color=INK, sw=1.5))
    frags.append(line(BKT_X + 10, BKT_MID + 5, BKT_X + 10, BKT_BOT, color=INK, sw=1.5))
    frags.append(line(BKT_X, BKT_BOT, BKT_X + 10, BKT_BOT, color=INK, sw=1.5))
    frags.append(line(BKT_X + 10, BKT_MID - 5, BKT_X + 20, BKT_MID, color=INK, sw=1.5))
    frags.append(line(BKT_X + 10, BKT_MID + 5, BKT_X + 20, BKT_MID, color=INK, sw=1.5))
    tb, tw, th = textbox(BKT_X + 20 + 58, BKT_MID, "джитер =\nworst − best\n= Tтік = 1 мс",
                         size=12, fill=FILL, stroke=INK, sw=1.5)
    frags.append(tb)

    # ── Легенда кольорів ──
    LEG_Y = ROW2_Y + ROW_H + 28
    frags.append(rect(LEFT, LEG_Y, 20, 14, fill="#d5f0e0", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(LEFT + 28, LEG_Y + 11, "Lквант — чекати наступного тіку (0 … Tтік)", size=12, color=INK, anchor="start"))
    frags.append(rect(LEFT + 340, LEG_Y, 20, 14, fill=LAMB2, stroke=AMB, sw=1.5, rx=3))
    frags.append(text(LEFT + 368, LEG_Y + 11, "Lчерга — черга готових задач", size=12, color=INK, anchor="start"))

    # ── Шкала-розподіл Lквант внизу ──
    DIST_Y = LEG_Y + 44
    DIST_W = 240
    DIST_H = 36
    DIST_X = LEFT

    # рівномірний прямокутник (гістограма)
    frags.append(rect(DIST_X, DIST_Y, DIST_W, DIST_H, fill="#d5f0e0", stroke=FIELD, sw=1.5, rx=4))
    # мітки 0 і 1 мс
    frags.append(text(DIST_X, DIST_Y + DIST_H + 16, "0", size=12, color=INK, anchor="middle"))
    frags.append(text(DIST_X + DIST_W, DIST_Y + DIST_H + 16, "1 мс", size=12, color=INK, anchor="middle"))
    # риска «середнє 0.5»
    frags.append(line(DIST_X + DIST_W / 2, DIST_Y, DIST_X + DIST_W / 2, DIST_Y + DIST_H,
                      color=FIELD, sw=2, dash="4,3"))
    frags.append(text(DIST_X + DIST_W / 2, DIST_Y - 6, "середнє 0.5 мс", size=11,
                      color=FIELD, anchor="middle"))

    # підпис розподілу
    frags.append(text(DIST_X + DIST_W + 14, DIST_Y + DIST_H / 2 + 5,
                      "Lквант ~ рівномірний розподіл [0, Tтік)", size=12, color=INK, anchor="start"))

    # ── Підпис формул зверху ──
    frags.append(text(W / 2, 28, "Lпробудж = Lквант + Lчерга", size=15, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 50, "Lквант ∈ [0, Tтік)   ·   Lчерга ≥ 0", size=13, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-27-4m-2-latency-budget.svg"), W, H,
           *frags, title="Рис. 4.10.4m.2. Бюджет латентності пробудження задачі планувальником")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_quantize()
    print("  fig-27-4m-1-quantize.svg: OK")
    fig_latency_budget()
    print("  fig-27-4m-2-latency-budget.svg: OK")
    print("Done. Files in ./img/")
