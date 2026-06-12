# -*- coding: utf-8 -*-
"""
Фігури для вставки ch27-s6-a-deadlock.md
«Deadlock: чотири умови і дисципліна порядку захоплення»
Дві фігури:
  fig-27-6-a-1-deadlock-cycle.svg    — кільце очікування (дедлок)
  fig-27-6-a-2-order-discipline.svg  — дисципліна порядку: ліворуч кільце, праворуч розімкнено
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори для цих фігур
RED_BG  = "#fbeaea"
GRN_BG  = "#e8f6eb"
RED_STR = "#c0271e"
GRN_STR = "#1f8a3b"
TASK_BG = "#e9eefb"
TASK_STR = "#1f47b5"
RES_BG  = "#fff6e0"
RES_STR = "#b07a10"
MUTED   = "#8a8a8a"


def fig6a_deadlock_cycle():
    """Рис. 4.10.6.a.1 — кільце взаємного блокування."""
    W, H = 860, 480
    parts = []

    # Заголовок
    parts.append(text(W / 2, 34,
        "Взаємне блокування: кільце очікування, з якого нема виходу",
        size=17, bold=True))
    parts.append(text(W / 2, 56,
        "кожна задача коректна сама по собі — смертельний лише перехресний порядок у одну мить",
        size=10.5, color=MUTED, italic=True))

    # ── Ресурс spiMtx (ліворуч-знизу) ──────────────────────────────────────
    RX1, RY1 = 120, 270
    parts.append(fitbox(RX1, RY1, 160, 54, "SPI Mutex\n(spiMtx)",
                        fill=RES_BG, stroke=RES_STR, sw=2.0, rx=10, color=RES_STR, bold=True))

    # ── Ресурс sdMtx (праворуч-знизу) ───────────────────────────────────────
    RX2, RY2 = 580, 270
    parts.append(fitbox(RX2, RY2, 160, 54, "SD Mutex\n(sdMtx)",
                        fill=RES_BG, stroke=RES_STR, sw=2.0, rx=10, color=RES_STR, bold=True))

    # ── Задача A (ліворуч-зверху) ────────────────────────────────────────────
    AX, AY = 120, 130
    parts.append(fitbox(AX, AY, 160, 54, "Задача A\n(дисплей → SD)",
                        fill=TASK_BG, stroke=TASK_STR, sw=2.0, rx=10, color=TASK_STR, bold=True))

    # ── Задача B (праворуч-зверху) ───────────────────────────────────────────
    BX, BY = 580, 130
    parts.append(fitbox(BX, BY, 160, 54, "Задача B\n(SD → дисплей)",
                        fill=TASK_BG, stroke=TASK_STR, sw=2.0, rx=10, color=TASK_STR, bold=True))

    # ── Стрілка: A ТРИМАЄ spiMtx (пряма, синя) ──────────────────────────────
    # A → spiMtx: вертикально вниз
    parts.append(arrow(200, 184, 200, 270, color=TASK_STR, sw=2.2))
    parts.append(text(213, 232, "тримає", size=10, color=TASK_STR, bold=True))

    # ── Стрілка: B ТРИМАЄ sdMtx (пряма, синя) ──────────────────────────────
    # B → sdMtx: вертикально вниз
    parts.append(arrow(660, 184, 660, 270, color=TASK_STR, sw=2.2))
    parts.append(text(673, 232, "тримає", size=10, color=TASK_STR, bold=True))

    # ── Стрілка: A ЧЕКАЄ на sdMtx (червона, горизонтально) ─────────────────
    # від правого боку spiMtx → до лівого боку sdMtx, але дугою через низ
    # Насправді від A → sdMtx: від правого краю A до верхнього краю sdMtx
    parts.append(arrow(280, 157, 580, 157, color=RED_STR, sw=2.4))
    parts.append(text(430, 147, "чекає →", size=10.5, color=RED_STR, bold=True, anchor="middle"))

    # ── Стрілка: B ЧЕКАЄ на spiMtx (червона, горизонтально — зворотна) ─────
    parts.append(arrow(580, 183, 280, 183, color=RED_STR, sw=2.4))
    parts.append(text(430, 198, "← чекає", size=10.5, color=RED_STR, bold=True, anchor="middle"))

    # ── Символ кільця / "нескінченна очікування" ────────────────────────────
    # Центральний значок замкненого кола
    parts.append(circle(430, 168, 14, fill="#fbeaea", stroke=RED_STR, sw=2.2))
    parts.append(text(430, 173, "∞", size=16, color=RED_STR, bold=True, anchor="middle"))

    # ── Рамка-висновок ──────────────────────────────────────────────────────
    box, bw, bh = textbox(W / 2, 385,
        "A тримає SPI, чекає SD  ·  B тримає SD, чекає SPI\n"
        "Кільце замкнулось: ні A, ні B не зрушать НІКОЛИ.\n"
        "Watchdog (§4.6.7) зрештою перезавантажить чип — мовчки.",
        size=12, fill=RED_BG, stroke=RED_STR, sw=1.8, color="#7a1010", pad=12, rx=10)
    parts.append(box)

    # ── Виноска: задачі самі по собі коректні ───────────────────────────────
    parts.append(text(W / 2, 460,
        "Кожна задача окремо правильна: взяла замок, попрацювала, віддала. Фатальний лише збіг порядку + часу.",
        size=9.5, color=MUTED, anchor="middle", italic=True))

    path = os.path.join(OUT, "fig-27-6-a-1-deadlock-cycle.svg")
    render(path, W, H, *parts)
    print("wrote fig-27-6-a-1-deadlock-cycle.svg")


def fig6a_order_discipline():
    """Рис. 4.10.6.a.2 — дисципліна порядку: ліворуч кільце (погано), праворуч нема (добре)."""
    W, H = 920, 440
    parts = []

    # Заголовок
    parts.append(text(W / 2, 34,
        "Єдиний порядок захоплення розриває кільце — задарма",
        size=17, bold=True))
    parts.append(text(W / 2, 56,
        "ліворуч: різний порядок → кільце можливе; праворуч: однаковий порядок → кільце неможливе в принципі",
        size=10, color=MUTED, italic=True))

    # ════════════════════════════════════════════════════════════════
    # ЛІВА ПАНЕЛЬ — «✗ різний порядок» (червона)
    # ════════════════════════════════════════════════════════════════
    LX = 40   # лівий край панелі
    LW = 380  # ширина панелі

    # Фон панелі
    parts.append(rect(LX, 76, LW, 310, fill=RED_BG, stroke=RED_STR, sw=2.0, rx=12))
    parts.append(fitbox(LX + 60, 76, 260, 34, "✗  Різний порядок → дедлок",
                        fill=RED_BG, stroke=RED_STR, sw=0, rx=8, color=RED_STR, bold=True))

    # Задача A (ліва панель)
    LA_X, LA_Y = LX + 20, 126
    parts.append(fitbox(LA_X, LA_Y, 150, 46, "Задача A\nspi → sd",
                        fill="#f4f6fb", stroke=TASK_STR, sw=1.8, rx=8, color=TASK_STR, bold=True))

    # Задача B (ліва панель) — протилежний порядок!
    LB_X, LB_Y = LX + 210, 126
    parts.append(fitbox(LB_X, LB_Y, 150, 46, "Задача B\nsd → spi",
                        fill="#f4f6fb", stroke=TASK_STR, sw=1.8, rx=8, color=TASK_STR, bold=True))

    # Ресурс spiMtx (ліва панель, ліворуч-знизу)
    parts.append(fitbox(LA_X, 240, 150, 46, "spiMtx",
                        fill=RES_BG, stroke=RES_STR, sw=1.8, rx=8, color=RES_STR, bold=True))

    # Ресурс sdMtx (ліва панель, праворуч-знизу)
    parts.append(fitbox(LB_X, 240, 150, 46, "sdMtx",
                        fill=RES_BG, stroke=RES_STR, sw=1.8, rx=8, color=RES_STR, bold=True))

    # A тримає spi (синя стрілка вниз)
    parts.append(arrow(LA_X + 75, 172, LA_X + 75, 240, color=TASK_STR, sw=2.0))

    # B тримає sd (синя стрілка вниз)
    parts.append(arrow(LB_X + 75, 172, LB_X + 75, 240, color=TASK_STR, sw=2.0))

    # A чекає sd → червона стрілка вправо між ресурсами
    parts.append(arrow(LA_X + 150, 263, LB_X, 263, color=RED_STR, sw=2.2))
    parts.append(text(LX + LW / 2, 258, "чекає →", size=9.5, color=RED_STR, bold=True, anchor="middle"))

    # B чекає spi → червона стрілка вліво між ресурсами
    parts.append(arrow(LB_X, 282, LA_X + 150, 282, color=RED_STR, sw=2.2))
    parts.append(text(LX + LW / 2, 297, "← чекає", size=9.5, color=RED_STR, bold=True, anchor="middle"))

    # Значок кільця
    parts.append(circle(LX + LW / 2, 272, 12, fill=RED_BG, stroke=RED_STR, sw=2.0))
    parts.append(text(LX + LW / 2, 277, "∞", size=14, color=RED_STR, bold=True, anchor="middle"))

    # Висновок лівої панелі
    parts.append(fitbox(LX + 20, 332, LW - 40, 40,
        "Кільце замкнулось: дедлок можливий",
        fill=RED_BG, stroke=RED_STR, sw=1.4, rx=7, color=RED_STR, bold=True))

    # ════════════════════════════════════════════════════════════════
    # ПРАВА ПАНЕЛЬ — «✓ єдиний порядок» (зелена)
    # ════════════════════════════════════════════════════════════════
    RX = 500  # лівий край правої панелі
    RW = 380

    # Фон панелі
    parts.append(rect(RX, 76, RW, 310, fill=GRN_BG, stroke=GRN_STR, sw=2.0, rx=12))
    parts.append(fitbox(RX + 60, 76, 260, 34, "✓  Єдиний порядок → без дедлоку",
                        fill=GRN_BG, stroke=GRN_STR, sw=0, rx=8, color=GRN_STR, bold=True))

    # Задача A (права панель)
    RA_X, RA_Y = RX + 20, 126
    parts.append(fitbox(RA_X, RA_Y, 150, 46, "Задача A\nspi → sd",
                        fill="#f4f6fb", stroke=TASK_STR, sw=1.8, rx=8, color=TASK_STR, bold=True))

    # Задача B (права панель) — ТОЙ САМИЙ порядок!
    RB_X, RB_Y = RX + 210, 126
    parts.append(fitbox(RB_X, RB_Y, 150, 46, "Задача B\nspi → sd",
                        fill="#f4f6fb", stroke=TASK_STR, sw=1.8, rx=8, color=TASK_STR, bold=True))

    # Ресурс spiMtx (права панель, ліворуч-знизу)
    parts.append(fitbox(RA_X, 240, 150, 46, "spiMtx",
                        fill=RES_BG, stroke=RES_STR, sw=1.8, rx=8, color=RES_STR, bold=True))

    # Ресурс sdMtx (права панель, праворуч-знизу)
    parts.append(fitbox(RB_X, 240, 150, 46, "sdMtx",
                        fill=RES_BG, stroke=RES_STR, sw=1.8, rx=8, color=RES_STR, bold=True))

    # A тримає spi (зелена стрілка вниз)
    parts.append(arrow(RA_X + 75, 172, RA_X + 75, 240, color=GRN_STR, sw=2.0))
    # B тримає spi (зелена стрілка — але вже A попереду; B стає в чергу)
    # B чекає spi (пунктир — «хоче, але поступається»)
    parts.append(arrow(RB_X + 75, 172, RA_X + 150, 263, color=MUTED, sw=1.8))
    parts.append(text(RX + 180, 220, "чекає\n(поступається)", size=9, color=MUTED, anchor="middle", italic=True))

    # Від spiMtx → sdMtx (зелений потік — після spi беруть sd)
    parts.append(arrow(RA_X + 150, 263, RB_X, 263, color=GRN_STR, sw=2.0))
    parts.append(text(RX + RW / 2, 258, "spi → sd", size=9.5, color=GRN_STR, bold=True, anchor="middle"))

    # Значок «розімкнено»
    parts.append(circle(RX + RW / 2, 282, 12, fill=GRN_BG, stroke=GRN_STR, sw=2.0))
    parts.append(text(RX + RW / 2, 287, "✓", size=12, color=GRN_STR, bold=True, anchor="middle"))

    # Висновок правої панелі
    parts.append(fitbox(RX + 20, 332, RW - 40, 40,
        "Хтось завжди попереду — кільце неможливе",
        fill=GRN_BG, stroke=GRN_STR, sw=1.4, rx=7, color=GRN_STR, bold=True))

    # ── Загальний підпис ────────────────────────────────────────────────────
    parts.append(text(W / 2, 415,
        "Умова №4 (кругове очікування) розірвана самою домовленістю — нульова вартість.",
        size=10.5, color=MUTED, anchor="middle", italic=True))

    path = os.path.join(OUT, "fig-27-6-a-2-order-discipline.svg")
    render(path, W, H, *parts)
    print("wrote fig-27-6-a-2-order-discipline.svg")


if __name__ == "__main__":
    fig6a_deadlock_cycle()
    fig6a_order_discipline()
