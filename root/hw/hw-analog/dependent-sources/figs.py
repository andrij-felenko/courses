# -*- coding: utf-8 -*-
"""Фігури до теми «Залежні джерела».
Три фігури:
  four-types.svg  — таблиця 2×2 чотирьох керованих джерел (вхід × вихід)
  symbols.svg     — коло (незалежне) проти ромба (залежне) з формулою
  test-source.svg — метод пробного джерела для виходу з керованим джерелом
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def diamond(cx, cy, r, fill=FILL, stroke=LINE, sw=1.8):
    """Ромб (залежне джерело) з центром (cx,cy) та «радіусом» r."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


# ── 1) Таблиця 2×2 чотирьох типів ───────────────────────────────────────────
def fig_four_types():
    W, H = 760, 470
    parts = []
    # сітка клітинок
    x0, y0 = 250, 95          # лівий-верхній кут поля клітинок
    cw, ch = 235, 150         # розмір клітинки
    gx, gy = 18, 18           # проміжки
    cols = ["видає НАПРУГУ", "видає СТРУМ"]
    rows = ["керує\nНАПРУГА", "керує\nСТРУМ"]
    cells = [
        ["VCVS", "Vвих = A · Vвх", "A — безрозмірний", "(підсилення напруги)"],
        ["VCCS", "Iвих = gm · Vвх", "gm — сименс (А/В)", "(крутість)"],
        ["CCVS", "Vвих = rm · Iвх", "rm — ом (В/А)", "(передавальний опір)"],
        ["CCCS", "Iвих = β · Iвх", "β — безрозмірний", "(підсилення струму)"],
    ]
    # заголовки стовпців
    for j, c in enumerate(cols):
        cx = x0 + j * (cw + gx) + cw / 2
        parts.append(text(cx, y0 - 22, c, size=15, bold=True, color=NEG))
    # заголовки рядків (ліворуч)
    for i, rlbl in enumerate(rows):
        cy = y0 + i * (ch + gy) + ch / 2
        parts.append(mtext(x0 - 130, cy - 8, rlbl, size=15, bold=True, color=POS, anchor="middle"))
    # клітинки
    k = 0
    for i in range(2):
        for j in range(2):
            cx = x0 + j * (cw + gx)
            cy = y0 + i * (ch + gy)
            name, formula, dim, note = cells[k]
            parts.append(rect(cx, cy, cw, ch, fill="#f4f6f8"))
            parts.append(text(cx + cw / 2, cy + 32, name, size=22, bold=True, color=INK))
            parts.append(text(cx + cw / 2, cy + 70, formula, size=16, color=INK))
            parts.append(text(cx + cw / 2, cy + 100, dim, size=13, color=MUTED))
            parts.append(text(cx + cw / 2, cy + 124, note, size=12, italic=True, color=MUTED))
            k += 1
    return render(os.path.join(IMG, "four-types.svg"), W, H, *parts,
                  title="Чотири залежні джерела: вхід керує виходом")


# ── 2) Коло проти ромба ─────────────────────────────────────────────────────
def fig_symbols():
    W, H = 780, 360
    parts = []

    # --- ліворуч: незалежне джерело (коло) ---
    lx, cy = 185, 195
    r = 46
    # провідники
    parts.append(line(lx, cy - r - 38, lx, cy - r, color=LINE, sw=2))
    parts.append(line(lx, cy + r, lx, cy + r + 38, color=LINE, sw=2))
    parts.append(circle(lx, cy, r, fill="#ffffff", stroke=LINE, sw=2))
    parts.append(plus(lx, cy - 16, r=11))
    parts.append(minus(lx, cy + 16, r=11))
    parts.append(text(lx, cy + r + 70, "КОЛО = незалежне", size=15, bold=True))
    parts.append(text(lx, cy + r + 92, "сила задана наперед", size=13, color=MUTED, italic=True))
    parts.append(text(lx, cy - r - 52, "V = const", size=14, color=INK))

    # --- праворуч: залежне джерело (ромб) ---
    rx = 560
    dr = 52
    parts.append(line(rx, cy - dr - 38, rx, cy - dr, color=LINE, sw=2))
    parts.append(line(rx, cy + dr, rx, cy + dr + 38, color=LINE, sw=2))
    parts.append(diamond(rx, cy, dr, fill="#ffffff", stroke=LINE, sw=2))
    # стрілка струму всередині ромба
    parts.append(arrow(rx, cy + 22, rx, cy - 22, color=INK, sw=2.2))
    parts.append(text(rx, cy + dr + 70, "РОМБ = залежне", size=15, bold=True))
    parts.append(text(rx, cy + dr + 92, "слухається кола", size=13, color=MUTED, italic=True))
    # формула біля ромба
    b, bw, bh = textbox(rx + dr + 70, cy, "I = β · Iб", size=15, fill="#eaf0fd",
                        stroke=NEG, color=NEG, bold=True)
    parts.append(b)
    parts.append(text(rx - dr - 60, cy - dr - 6, "керувальна", size=12, color=MUTED))
    parts.append(text(rx - dr - 60, cy - dr + 12, "величина Iб", size=12, color=MUTED))

    # роздільна вертикаль
    parts.append(line(W / 2, 70, W / 2, H - 30, color="#d0d4da", sw=1.2, dash="5,5"))
    return render(os.path.join(IMG, "symbols.svg"), W, H, *parts,
                  title="Незалежне (коло) проти залежного (ромб)")


# ── 3) Метод пробного джерела ───────────────────────────────────────────────
def fig_test_source():
    W, H = 720, 400
    parts = []

    # рамка «коло з керованим джерелом» (усі незалежні вимкнені)
    bx, by, bw, bh = 70, 95, 330, 230
    parts.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=LINE, sw=1.6))
    parts.append(text(bx + bw / 2, by - 14, "коло (незалежні джерела вимкнені)",
                      size=14, bold=True))

    # залежне джерело (ромб) живе всередині
    dx, dy, dr = bx + 105, by + 115, 40
    parts.append(diamond(dx, dy, dr, fill="#ffffff", stroke=NEG, sw=2))
    parts.append(arrow(dx, dy + 18, dx, dy - 18, color=NEG, sw=2.2))
    parts.append(text(dx, dy + dr + 24, "залежне —", size=13, color=NEG, bold=True))
    parts.append(text(dx, dy + dr + 42, "лишається живим", size=13, color=NEG, italic=True))

    # резистори всередині (узагальнено)
    rrx = bx + 215
    parts.append(rect(rrx, by + 55, 26, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    parts.append(text(rrx + 13, by + 48, "R", size=13, italic=True, color=INK))

    # вузли-вимкнені незалежні (КЗ та розрив) — підпис
    parts.append(text(bx + bw / 2, by + bh - 18,
                      "V → коротке • I → розрив", size=12, color=MUTED, italic=True))

    # затискачі праворуч
    ax, ay = bx + bw, by + 60         # верхній затискач
    bx2, by2 = bx + bw, by + 170      # нижній затискач
    tx = 540                          # x пробного джерела
    parts.append(line(ax, ay, tx, ay, color=LINE, sw=2))
    parts.append(line(bx2, by2, tx, by2, color=LINE, sw=2))
    parts.append(circle(ax, ay, 4, fill=INK, stroke=INK))
    parts.append(circle(bx2, by2, 4, fill=INK, stroke=INK))

    # пробне джерело струму (коло зі стрілкою)
    tcy = (ay + by2) / 2
    parts.append(line(tx, ay, tx, tcy - 30, color=LINE, sw=2))
    parts.append(line(tx, tcy + 30, tx, by2, color=LINE, sw=2))
    parts.append(circle(tx, tcy, 30, fill="#fdecea", stroke=POS, sw=2))
    parts.append(arrow(tx, tcy + 14, tx, tcy - 14, color=POS, sw=2.4))
    b2, b2w, b2h = textbox(tx + 95, tcy - 22, "Iпроб = 1 А", size=14,
                           fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b2)

    # вимір напруги
    b3, b3w, b3h = textbox(tx + 95, tcy + 40, ["виміряти Vпроб", "R = Vпроб / 1 А"],
                           size=13, fill="#eafaf0", stroke=FIELD, color=INK)
    parts.append(b3)

    return render(os.path.join(IMG, "test-source.svg"), W, H, *parts,
                  title="Метод пробного джерела (вихідний опір)")


if __name__ == "__main__":
    fig_four_types()
    fig_symbols()
    fig_test_source()
    print("OK: 3 SVG written to ./img/")
