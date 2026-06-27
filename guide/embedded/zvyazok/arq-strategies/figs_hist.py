# -*- coding: utf-8 -*-
"""Фігури до історичної вставки «Як народилося ARQ» (hist-arq-origins.md).
Окремий файл, щоб не чіпати figs.py теми. Запуск: python figs_hist.py → ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Код ван Дуурена: рівно три «крапки» з семи — порушив баланс → помилка ──
def fig_van_duuren():
    W, H = 760, 360
    parts = []
    parts.append(text(W/2, 30, "Код ван Дуурена: рівно 3 одиниці з 7", size=17, bold=True))
    parts.append(text(W/2, 52, "приймач рахує одиниці; не три — отже, спотворення",
                      size=12, color=MUTED))

    # клітинки 7-бітного символу
    cell = 46
    gap = 8
    roww = 7 * cell + 6 * gap
    x0 = (W - roww) / 2

    def draw_row(y, bits, label, ok):
        out = []
        ones = sum(bits)
        for i, b in enumerate(bits):
            cx = x0 + i * (cell + gap)
            fill = "#fdecea" if b else "#eef2f7"
            strk = POS if b else MUTED
            out.append(rect(cx, y, cell, cell, fill=fill, stroke=strk, sw=2, rx=6))
            out.append(text(cx + cell/2, y + cell/2 + 7, "1" if b else "0",
                            size=20, color=(POS if b else MUTED), bold=True))
        # підпис ліворуч
        out.append(text(x0 - 14, y + cell/2 + 5, label, size=13, anchor="end", color=INK))
        # вирок праворуч
        col = FIELD if ok else POS
        verdict = ("✓ 3 одиниці — ціле" if ok else "✗ %d ≠ 3 — помилка!" % ones)
        out.append(text(x0 + roww + 14, y + cell/2 + 5, verdict,
                        size=13, anchor="start", color=col, bold=True))
        return "".join(out)

    parts.append(draw_row(90,  [1, 0, 1, 1, 0, 0, 0], "вислано:", True))
    parts.append(draw_row(170, [1, 0, 1, 1, 0, 0, 0], "прийнято:", True))
    parts.append(draw_row(258, [1, 0, 0, 1, 0, 0, 0], "прийнято:", False))

    parts.append(text(W/2, 336,
                      "Один збитий біт ламає баланс 3-з-7 — приймач шле сигнал RQ «повтори»",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "van-duuren-code.svg"), W, H, *parts)


# ── 2. Родовід ідеї «надішли ще раз»: телеграф → ARQ → мережі → гібрид ────────
def fig_lineage():
    W, H = 820, 430
    parts = []
    parts.append(text(W/2, 30, "Родовід ідеї «надішли ще раз»", size=17, bold=True))

    boxes = [
        (1840, "Ручний телеграф", "оператор перепитує\nспотворену телеграму", MUTED),
        ("1947", "Ван Дуурен · ARQ", "код 3-з-7, автомат,\nАмстердам–Нью-Йорк", POS),
        ("1973", "Ле Ланн · вікно", "рухоме вікно в CYCLADES;\n1974 — у TCP", NEG),
        ("1979", "HDLC (ISO)", "Go-Back-N і\nSelective Repeat — у стандарт", INK),
        ("1985", "Чейз · складання", "code combining —\nоснова гібридного ARQ", FIELD),
    ]
    n = len(boxes)
    bw, bh = 138, 96
    margin = 24
    span = W - 2 * margin
    step = (span - bw) / (n - 1)
    y = 130
    centers = []
    for i, (yr, title, sub, col) in enumerate(boxes):
        x = margin + i * step
        cx = x + bw / 2
        centers.append(cx)
        parts.append(rect(x, y, bw, bh, fill=FILL, stroke=col, sw=2.2, rx=10))
        parts.append(text(cx, y - 12, str(yr), size=15, color=col, bold=True))
        parts.append(text(cx, y + 24, title, size=13, color=INK, bold=True))
        parts.append(mtext(cx, y + 46, sub, size=11, color=MUTED, lh=1.25))
    # стрілки між блоками
    for i in range(n - 1):
        x1 = margin + i * step + bw
        x2 = margin + (i + 1) * step
        parts.append(arrow(x1 + 4, y + bh/2, x2 - 4, y + bh/2, color=LINE, sw=2))

    # дві гілки призначення під лінією
    parts.append(text(W/2, 300,
                      "Одна ідея — дві долі:", size=13, color=INK, bold=True))
    b1, w1, h1 = textbox(W*0.30, 350,
                         "Радіотелеграф / телекс:\nавтомат-корекція в ефірі",
                         size=12, fill="#fdf0ee", stroke=POS, sw=2)
    b2, w2, h2 = textbox(W*0.70, 350,
                         "Комп'ютерні мережі:\nвікно, TCP, мобільний HARQ",
                         size=12, fill="#eef2fd", stroke=NEG, sw=2)
    parts.append(b1)
    parts.append(b2)
    # стрілки від лінії родоводу до гілок
    parts.append(arrow(centers[1], y + bh + 6, W*0.30, 350 - h2/2 - 6, color=POS, sw=1.8))
    parts.append(arrow(centers[2], y + bh + 6, W*0.70, 350 - h2/2 - 6, color=NEG, sw=1.8))

    render(os.path.join(IMG, "arq-lineage.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_van_duuren()
    fig_lineage()
    print("OK:", os.listdir(IMG))
