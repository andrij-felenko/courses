# -*- coding: utf-8 -*-
"""
Фігури до вставки r12-s5-a-hid-reports.md (⚙️ HID-звіти: як МК прикидається клавіатурою)
fig-r12-5a-1-report-layout.svg  — розкладка 8 байтів boot keyboard report
fig-r12-5a-2-press-flow.svg     — часова стрічка одного натиску (interrupt-IN)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Фіг. 1 — розкладка 8-байтового boot keyboard report
# ═══════════════════════════════════════════════════════════════════════════════

def fig1():
    W, H = 820, 430
    frags = []

    # ── Заголовок ──────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "8-байтовий Boot Keyboard Input Report", size=16, bold=True))

    # ── Загальна смуга байтів (горизонтальна) ─────────────────────────────────
    # byte0..7: x-позиції
    BYTE_W = 72
    BYTE_H = 48
    BAR_Y  = 72
    BAR_X0 = 30

    byte_labels = ["byte 0\nmodifier", "byte 1\nreserved",
                   "byte 2\nkey[0]", "byte 3\nkey[1]",
                   "byte 4\nkey[2]", "byte 5\nkey[3]",
                   "byte 6\nkey[4]", "byte 7\nkey[5]"]
    byte_fills  = [POS + "22", MUTED + "22",
                   NEG + "22", NEG + "22",
                   NEG + "22", NEG + "22",
                   NEG + "22", NEG + "22"]

    byte_xs = []
    for i, (lbl, fill) in enumerate(zip(byte_labels, byte_fills)):
        bx = BAR_X0 + i * (BYTE_W + 4)
        byte_xs.append(bx + BYTE_W / 2)
        frags.append(rect(bx, BAR_Y, BYTE_W, BYTE_H, fill=fill, stroke=LINE, sw=1.5, rx=4))
        frags.append(mtext(bx + BYTE_W / 2, BAR_Y + 16, lbl.split("\n"), size=11, color=INK))

    # Підпис «1 байт» під кожним
    for bx_cx in byte_xs:
        frags.append(text(bx_cx, BAR_Y + BYTE_H + 14, "1 байт", size=9, color=MUTED))

    # ── Розгортка byte0: 8 біт модифікаторів ─────────────────────────────────
    BIT_Y = BAR_Y + BYTE_H + 36
    BIT_W = 62
    BIT_H = 36
    # 8 бітів розміщуємо під byte0, зсунуті вліво щоб влізти
    bit_names = ["RGUI\n0x80", "RAlt\n0x40", "RShift\n0x20", "RCtrl\n0x10",
                 "LGUI\n0x08", "LAlt\n0x04", "LShift\n0x02", "LCtrl\n0x01"]
    BIT_X0 = BAR_X0

    frags.append(text(BIT_X0 + 4 * BIT_W, BIT_Y - 8,
                      "byte 0 — бітова маска модифікаторів (bit 7 … bit 0):",
                      size=11, color=INK, anchor="middle"))

    for i, bname in enumerate(bit_names):
        bx = BIT_X0 + i * (BIT_W + 2)
        is_lgui = (bname.startswith("LGUI"))
        fill = POS + "33" if is_lgui else FILL
        stroke_c = POS if is_lgui else LINE
        frags.append(rect(bx, BIT_Y, BIT_W, BIT_H, fill=fill, stroke=stroke_c, sw=1.5, rx=3))
        frags.append(mtext(bx + BIT_W / 2, BIT_Y + 11, bname.split("\n"), size=10,
                           color=POS if is_lgui else INK))

    # стрілка від byte0 вниз до розгортки
    frags.append(arrow(byte_xs[0], BAR_Y + BYTE_H, byte_xs[0], BIT_Y - 2, color=MUTED, sw=1.3))

    # ── Права панель: два приклади заповнення ─────────────────────────────────
    EX_X = BAR_X0 + 8 * (BYTE_W + 4) + 12
    EX_W = W - EX_X - 10

    # Рамка «Приклад: А»
    ex1_y = BAR_Y
    frags.append(rect(EX_X, ex1_y, EX_W, 88, fill="#eaf7ea", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(EX_X + EX_W / 2, ex1_y + 16, "Приклад: клавіша «A»", size=12,
                      bold=True, color=FIELD, anchor="middle"))
    ex1_lines = ["modifier = 0x00", "reserved = 0x00",
                 "key[0]  = 0x04  ← usage ID 'A'",
                 "key[1..5] = 0x00"]
    for j, ln in enumerate(ex1_lines):
        frags.append(text(EX_X + 8, ex1_y + 32 + j * 14, ln, size=10, color=INK, anchor="start"))

    # Рамка «Приклад: Win+R»
    ex2_y = ex1_y + 96
    frags.append(rect(EX_X, ex2_y, EX_W, 88, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(EX_X + EX_W / 2, ex2_y + 16, "Приклад: Win+R", size=12,
                      bold=True, color=POS, anchor="middle"))
    ex2_lines = ["modifier = 0x08  ← LGUI (bit2)", "reserved = 0x00",
                 "key[0]  = 0x15  ← usage ID 'R'",
                 "key[1..5] = 0x00"]
    for j, ln in enumerate(ex2_lines):
        frags.append(text(EX_X + 8, ex2_y + 32 + j * 14, ln, size=10, color=INK, anchor="start"))

    # ── Нижній рядок: byte1 та key-слоти ──────────────────────────────────────
    NOTE_Y = BIT_Y + BIT_H + 22
    frags.append(text(BAR_X0 + BYTE_W / 2 + (BYTE_W + 4),
                      NOTE_Y, "byte 1 = 0x00 завжди (reserved)", size=10, color=MUTED, anchor="middle"))
    frags.append(text(BAR_X0 + BYTE_W / 2 + 2 * (BYTE_W + 4) + 3 * (BYTE_W + 4),
                      NOTE_Y, "byte 2..7: до 6 одночасних usage ID (Keyboard/Keypad page 0x07)",
                      size=10, color=NEG, anchor="middle"))

    # ── Висновок ───────────────────────────────────────────────────────────────
    CONC_Y = NOTE_Y + 28
    b, bw, bh = textbox(W / 2, CONC_Y + 16,
                         "Натиск = заповнити біти модифікаторів + usage у слоти key[]\n"
                         "Відпускання = надіслати весь звіт нулями (0x00 × 8)",
                         size=12, pad=10, fill="#f0f9f0", stroke=FIELD, sw=1.8, bold=False)
    frags.append(b)

    render(os.path.join(OUT, "fig-r12-5a-1-report-layout.svg"), W, H, *frags)
    print("fig-r12-5a-1-report-layout.svg — готово")


# ═══════════════════════════════════════════════════════════════════════════════
# Фіг. 2 — часова стрічка одного натиску (interrupt-IN polling)
# ═══════════════════════════════════════════════════════════════════════════════

def fig2():
    W, H = 760, 310
    frags = []

    frags.append(text(W / 2, 26, "Один натиск макро-паду: interrupt-IN polling", size=16, bold=True))

    # ── Вісь часу ─────────────────────────────────────────────────────────────
    AX_Y  = 220
    AX_X0 = 50
    AX_X1 = W - 30
    frags.append(arrow(AX_X0, AX_Y, AX_X1, AX_Y, color=MUTED, sw=1.5))
    frags.append(text(AX_X1 - 4, AX_Y + 16, "час", size=12, color=MUTED, anchor="end"))

    # ── Позиції подій ─────────────────────────────────────────────────────────
    # poll0  poll1(звіт з натиском)  poll2(порожній звіт)  poll3
    polls = [90, 210, 360, 510, 650]
    POLL_H = 52   # висота стрілки від осі вгору

    for px in polls:
        frags.append(arrow(px, AX_Y, px, AX_Y - POLL_H, color=MUTED, sw=1.3))
        frags.append(text(px, AX_Y + 14, "poll", size=9, color=MUTED, anchor="middle"))

    # ── bInterval підпис ──────────────────────────────────────────────────────
    frags.append(line(polls[0], AX_Y + 28, polls[1], AX_Y + 28, color=MUTED, sw=1, dash="4,3"))
    frags.append(text((polls[0] + polls[1]) / 2, AX_Y + 42, "bInterval (напр. 1 мс)",
                      size=10, color=MUTED, anchor="middle"))

    # ── Звіт-стан {LGUI,R} над poll1 ─────────────────────────────────────────
    b1, w1, _ = textbox(polls[1], AX_Y - POLL_H - 44,
                         "звіт: modifier=0x08\nkey[0]=0x15 (R)",
                         size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.6)
    frags.append(b1)
    frags.append(text(polls[1], AX_Y - POLL_H - 88, "пристрій надсилає →", size=10,
                      color=POS, anchor="middle"))

    # ── Порожній звіт над poll2 ───────────────────────────────────────────────
    b2, w2, _ = textbox(polls[2], AX_Y - POLL_H - 44,
                         "звіт: 0x00 × 8\n(відпускання)",
                         size=11, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.6)
    frags.append(b2)
    frags.append(text(polls[2], AX_Y - POLL_H - 88, "пристрій надсилає →", size=10,
                      color=NEG, anchor="middle"))

    # ── Реакція ОС між poll1 і poll2 ─────────────────────────────────────────
    react_x = (polls[1] + polls[2]) / 2
    b3, _, _ = textbox(react_x, AX_Y - 20,
                        "ОС реєструє\nнатиск Win+R",
                        size=10, pad=6, fill="#f0f9f0", stroke=FIELD, sw=1.4)
    frags.append(b3)

    # ── Висновок ───────────────────────────────────────────────────────────────
    b4, _, _ = textbox(W / 2, H - 24,
                        "Темп визначає bInterval endpoint'а (§4.12.4), а не delay() у коді",
                        size=11, pad=9, fill=FILL, stroke=MUTED, sw=1.4)
    frags.append(b4)

    render(os.path.join(OUT, "fig-r12-5a-2-press-flow.svg"), W, H, *frags)
    print("fig-r12-5a-2-press-flow.svg — готово")


if __name__ == "__main__":
    fig1()
    fig2()
    print("Усі фігури збережено у", OUT)
