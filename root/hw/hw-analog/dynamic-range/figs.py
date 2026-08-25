# -*- coding: utf-8 -*-
"""Фігури до статті «Динамічний діапазон» (dynamic-range).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CEIL = "#c0392b"   # стеля (відсічка) — гаряча
FLOOR = "#2457d6"  # підлога (шум) — холодна
BAND = "#cfe8d6"   # «вікно», де живе сигнал
SIG = "#27ae60"    # корисний сигнал
GREY = "#e8eaed"


# ── 1. Дві стіни: стеля відсічки і підлога шуму, між ними — діапазон ──────────
def fig_two_walls():
    W, H = 720, 430
    parts = []
    # вертикальна вісь рівня (логарифмічна, у дБ)
    ax_x = 150
    rail_r = 470          # права межа горизонтальних ліній рівнів
    top, bot = 78, 360
    parts.append(line(ax_x, top - 14, ax_x, bot + 10, color=INK, sw=2))
    parts.append(text(ax_x - 12, top - 20, "рівень", size=13, color=MUTED, anchor="end"))
    parts.append(text(ax_x - 12, top - 6, "сигналу", size=13, color=MUTED, anchor="end"))

    # стеля
    ceil_y = top + 16
    parts.append(line(ax_x, ceil_y, rail_r, ceil_y, color=CEIL, sw=3))
    parts.append(text(ax_x + 124, ceil_y - 8, "стеля: відсічка / насичення",
                      size=13, color=CEIL, anchor="start", bold=True))
    # підлога
    floor_y = bot - 16
    parts.append(line(ax_x, floor_y, rail_r, floor_y, color=FLOOR, sw=3))
    parts.append(text(ax_x + 124, floor_y + 18, "підлога: шум",
                      size=13, color=FLOOR, anchor="start", bold=True))

    # смуга між ними — корисне вікно
    parts.append(rect(ax_x, ceil_y, 110, floor_y - ceil_y, fill=BAND, stroke="none", sw=0, rx=0))
    # три приклади сигналів усередині
    for frac, lab in [(0.20, "сильний"), (0.5, "середній"), (0.80, "слабкий")]:
        sy = ceil_y + frac * (floor_y - ceil_y)
        parts.append(line(ax_x + 14, sy, ax_x + 96, sy, color=SIG, sw=2.5))
        parts.append(text(ax_x + 55, sy - 6, lab, size=11, color="#1c7a43", anchor="middle"))

    # стрілка діапазону — у вільному полі праворуч від смуги
    arr_x = 320
    parts.append(line(arr_x, ceil_y, arr_x, floor_y, color=INK, sw=1.6, dash="4 3"))
    parts.append(arrow(arr_x, ceil_y + 4, arr_x, ceil_y, color=INK, sw=2.2))
    parts.append(arrow(arr_x, floor_y - 4, arr_x, floor_y, color=INK, sw=2.2))
    bx, bw, bh = textbox(arr_x + 96, (ceil_y + floor_y) / 2,
                         "ДИНАМІЧНИЙ\nДІАПАЗОН\n(стеля − підлога)",
                         size=13, bold=True, fill="#fff7e6", stroke=INK, sw=1.5)
    parts.append(bx)

    render(os.path.join(IMG, "two-walls.svg"), W, H, *parts)


# ── 2. Розклад на запас і SNR відносно робочого рівня ────────────────────────
def fig_headroom_snr():
    W, H = 720, 430
    parts = []
    ax_x = 230
    rail_r = 470          # права межа ліній рівнів (місце під підписи — справа)
    top, bot = 60, 380
    parts.append(line(ax_x, top - 10, ax_x, bot + 10, color=INK, sw=2))

    ceil_y = top + 10
    floor_y = bot - 10
    work_y = ceil_y + 0.42 * (floor_y - ceil_y)             # робочий рівень

    # три рівні з підписами праворуч (вирівняні по лівому краю, у межах полотна)
    for y, col, lab in [(ceil_y, CEIL, "межа відсічки"),
                        (floor_y, FLOOR, "шумова підлога")]:
        parts.append(line(ax_x, y, rail_r, y, color=col, sw=3))
        parts.append(text(rail_r + 8, y + 4, lab, size=12, color=col, anchor="start", bold=True))
    # робочий рівень
    parts.append(line(ax_x, work_y, rail_r, work_y, color=SIG, sw=2.5, dash="5 4"))
    parts.append(text(rail_r + 8, work_y + 4, "робочий рівень", size=12,
                      color="#1c7a43", anchor="start", bold=True))

    # запас (headroom): від робочого до стелі
    hx = ax_x - 70
    parts.append(line(hx, ceil_y, hx, work_y, color=INK, sw=1.4))
    parts.append(arrow(hx, ceil_y + 4, hx, ceil_y, color=INK, sw=2))
    parts.append(arrow(hx, work_y - 4, hx, work_y, color=INK, sw=2))
    b1, w1, h1 = textbox(hx - 56, (ceil_y + work_y) / 2, "ЗАПАС\n(headroom)",
                         size=12, bold=True, fill="#fdecea", stroke=CEIL, sw=1.4)
    parts.append(b1)

    # SNR: від робочого до підлоги
    parts.append(line(hx, work_y, hx, floor_y, color=INK, sw=1.4))
    parts.append(arrow(hx, work_y + 4, hx, work_y, color=INK, sw=2))
    parts.append(arrow(hx, floor_y - 4, hx, floor_y, color=INK, sw=2))
    b2, w2, h2 = textbox(hx - 56, (work_y + floor_y) / 2, "SNR\n(сигнал/шум)",
                         size=12, bold=True, fill="#eaf0fd", stroke=FLOOR, sw=1.4)
    parts.append(b2)

    # повний діапазон праворуч від підписів
    dx = rail_r + 132
    parts.append(line(dx, ceil_y, dx, floor_y, color=INK, sw=1.4, dash="3 3"))
    parts.append(arrow(dx, ceil_y + 4, dx, ceil_y, color=INK, sw=2))
    parts.append(arrow(dx, floor_y - 4, dx, floor_y, color=INK, sw=2))
    b3, w3, h3 = textbox(dx + 4, ceil_y - 30,
                         "ДІАПАЗОН =\nЗАПАС + SNR",
                         size=12, bold=True, fill="#fff7e6", stroke=INK, sw=1.4)
    parts.append(b3)

    render(os.path.join(IMG, "headroom-snr.svg"), W, H, *parts)


# ── 3. Драбина бітів: кожен біт ≈ 6 дБ діапазону ─────────────────────────────
def fig_bit_ladder():
    W, H = 660, 400
    parts = []
    base_x, base_y = 90, 340
    step_w = 52
    step_h = 26
    bits = [4, 8, 12, 16, 20, 24]
    maxbit = 24
    for i, n in enumerate(bits):
        x = base_x + i * (step_w + 30)
        h = (n / maxbit) * 250
        y = base_y - h
        col = BAND if n != 16 else "#bfe0c9"
        parts.append(rect(x, y, step_w, h, fill=col, stroke="#1c7a43", sw=1.6))
        db = round(6.02 * n + 1.76)
        parts.append(text(x + step_w / 2, y - 22, "%d біт" % n, size=12, bold=True))
        parts.append(text(x + step_w / 2, y - 7, "≈%d дБ" % db, size=12, color=INK))
        parts.append(text(x + step_w / 2, base_y + 16, "%d рівнів" % (2 ** n) if n <= 12
                          else "2^%d" % n, size=10, color=MUTED))
    parts.append(line(base_x - 20, base_y, W - 30, base_y, color=INK, sw=2))
    parts.append(text(W / 2, 40, "кожен доданий біт ≈ +6 дБ діапазону", size=14,
                      bold=True, color=INK))
    # позначка CD на 16 біт
    cd_x = base_x + 3 * (step_w + 30) + step_w / 2
    parts.append(text(cd_x, base_y - 250 - 4, "CD-аудіо", size=10, color=CEIL, bold=True))
    render(os.path.join(IMG, "bit-ladder.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_two_walls()
    fig_headroom_snr()
    fig_bit_ladder()
    print("OK: figures written to", IMG)
