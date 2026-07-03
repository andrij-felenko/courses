# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Семисегментний індикатор 5161AS (1 розряд)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ON = "#c0392b"      # засвічений сегмент
OFFSEG = "#e3e6ea"  # погашений сегмент (тонка сіра форма)


def seg_shape(f, cx, cy, s, on):
    """Намалювати сім сегментів цифри з центром угорі-ліворуч у (cx,cy).
    s — довжина сегмента; on — множина літер, що світяться."""
    col = lambda k: ON if k in on else OFFSEG
    t = s * 0.16          # товщина смуги
    g = s * 0.10          # зазор між сегментами
    # опорні точки решітки 7-сегмента
    x0, x1 = cx, cx + s
    y0, y1, y2 = cy, cy + s, cy + 2 * s

    def hbar(x, y, key):   # горизонтальна смуга (шестикутник)
        p = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            x + g, y, x + g + t * 0.6, y - t / 2, x + s - g - t * 0.6, y - t / 2,
            x + s - g, y, x + s - g - t * 0.6, y + t / 2, x + g + t * 0.6, y + t / 2)
        f.append('<polygon points="%s" fill="%s"/>' % (p, col(key)))

    def vbar(x, y, key):   # вертикальна смуга
        p = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            x, y + g, x + t / 2, y + g + t * 0.6, x + t / 2, y + s - g - t * 0.6,
            x, y + s - g, x - t / 2, y + s - g - t * 0.6, x - t / 2, y + g + t * 0.6)
        f.append('<polygon points="%s" fill="%s"/>' % (p, col(key)))

    hbar(x0, y0, "a")            # a — верх
    vbar(x1, y0, "b")            # b — правий верхній
    vbar(x1, y1, "c")            # c — правий нижній
    hbar(x0, y2, "d")            # d — низ
    vbar(x0, y1, "e")            # e — лівий нижній
    vbar(x0, y0, "f")            # f — лівий верхній
    hbar(x0, y1, "g")            # g — середина
    # десяткова крапка
    f.append(circle(x1 + t, y2, t * 0.55, fill=col("dp"), stroke="none", sw=0))


# ── 1. Карта сегментів + порядок 10 виводів ───────────────────────────────────
def fig_anatomy():
    W, H = 820, 470
    f = [text(W / 2, 30, "Сім смужок + крапка, і десять ніжок, що ними керують",
              size=16, bold=True)]

    # ── ліва панель: сама цифра з підписаними сегментами ──
    s = 70
    cx, cy = 120, 110
    seg_shape(f, cx, cy, s, {"a", "b", "c", "d", "e", "f", "g", "dp"})
    lc = MUTED
    # підписи сегментів (винесені назовні, лінії-указки повз смуги)
    f.append(text(cx + s / 2, cy - 26, "a", size=15, bold=True, color=lc))
    f.append(text(cx + s + 34, cy + s / 2, "b", size=15, bold=True, color=lc))
    f.append(text(cx + s + 34, cy + s + s / 2, "c", size=15, bold=True, color=lc))
    f.append(text(cx + s / 2, cy + 2 * s + 30, "d", size=15, bold=True, color=lc))
    f.append(text(cx - 30, cy + s + s / 2, "e", size=15, bold=True, color=lc))
    f.append(text(cx - 30, cy + s / 2, "f", size=15, bold=True, color=lc))
    f.append(text(cx + s + 40, cy + s + 4, "g", size=15, bold=True, color=FIELD))
    # виправ: g у центрі середньої смуги
    f.pop()
    f.append(text(cx + s / 2, cy + s - 8, "g", size=15, bold=True, color="#ffffff"))
    f.append(text(cx + s + 30, cy + 2 * s + 4, "DP", size=13, bold=True, color=lc))
    f.append(text(cx + s / 2, cy + 2 * s + 66, "«8.» — усе засвічено", size=11, color=MUTED))

    # ── права панель: корпус DIP із двома рядами по 5 виводів ──
    bx, by, bw, bh = 430, 78, 320, 250
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=INK, sw=1.8, rx=10))
    f.append(text(bx + bw / 2, by + 26, "корпус 5161AS, вид згори", size=12, bold=True))
    f.append(text(bx + bw / 2, by + 44, "крапка внизу-праворуч → відлік", size=10, color=MUTED))

    # маленька орієнтир-крапка в кутку корпусу (як крапка на реальному корпусі)
    f.append(circle(bx + bw - 22, by + bh - 20, 5, fill=ON, stroke="none", sw=0))
    f.append(text(bx + bw - 54, by + bh - 16, "крапка", size=9, color=MUTED, anchor="end"))

    # два ряди контактів
    pins_bottom = [(1, "e"), (2, "d"), (3, "COM"), (4, "c"), (5, "DP")]
    pins_top = [(10, "g"), (9, "f"), (8, "COM"), (7, "a"), (6, "b")]
    n = 5
    x0 = bx + 42
    dx = (bw - 84) / (n - 1)
    ytop = by + 78
    ybot = by + bh - 78

    def pin(px, py, num, lab, up):
        com = (lab == "COM")
        fill = "#eef6ef" if com else "#eef2f8"
        stroke = FIELD if com else NEG
        f.append(rect(px - 20, py - 16, 40, 32, fill=fill, stroke=stroke, sw=1.6, rx=6))
        f.append(text(px, py - 2, lab, size=12, bold=True,
                      color=(FIELD if com else INK)))
        f.append(text(px, py + 12, str(num), size=9, color=MUTED))
        # «нога» контакту назовні корпусу
        ey = py - 26 if up else py + 26
        f.append(line(px, py - 16 if up else py + 16, px, ey, color=INK, sw=2.2))

    for i, (num, lab) in enumerate(pins_top):
        pin(x0 + i * dx, ytop, num, lab, up=True)
    for i, (num, lab) in enumerate(pins_bottom):
        pin(x0 + i * dx, ybot, num, lab, up=False)

    f.append(text(bx + bw / 2, ytop - 40, "верхній ряд:  10 · 9 · 8 · 7 · 6",
                  size=10, color=MUTED))
    f.append(text(bx + bw / 2, ybot + 42, "нижній ряд:  1 · 2 · 3 · 4 · 5",
                  size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 400,
                      "два виводи COM (3 і 8) — спільний катод: обидва на GND. Решта вісім — по одному сегменту.",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b2, _, _ = textbox(W / 2, 440,
                       "суфікс AS = common cathode (спільний катод); BS-версія = спільний анод, дзеркальна логіка",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: 8 сегментів через резистори, два COM на GND ────────
def fig_wiring():
    W, H = 840, 560
    f = [text(W / 2, 30, "Підключення: вісім ліній через резистори, обидва COM — на землю",
              size=16, bold=True)]

    # МК ліворуч
    mx, my, mw, mh = 40, 70, 150, 380
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mx + mw / 2, my + 44, "(будь-які 8 виводів)", size=10, color=MUTED))

    # індикатор праворуч (спрощений корпус із контактами-сегментами)
    dx0, dy0, dw, dh = 630, 70, 170, 380
    f.append(rect(dx0, dy0, dw, dh, fill="#fafbfc", stroke=INK, sw=1.8, rx=10))
    f.append(text(dx0 + dw / 2, dy0 + 26, "5161AS", size=12.5, bold=True))
    f.append(text(dx0 + dw / 2, dy0 + 44, "спільний катод", size=10, color=MUTED))

    rows = ["a", "b", "c", "d", "e", "f", "g", "DP"]
    ry0 = my + 74
    rdy = 40
    rx_mcu = mx + mw            # правий край МК
    rx_res_l = 250              # ліва межа резистора
    rx_res_r = 340             # права межа резистора
    rx_disp = dx0               # лівий край індикатора

    for i, seg in enumerate(rows):
        y = ry0 + i * rdy
        # вивід МК
        f.append(text(mx + mw - 14, y + 4, "IO", size=9, color=INK, anchor="end"))
        f.append(circle(rx_mcu, y, 3.5, fill=NEG, stroke="none", sw=0))
        # провід до резистора
        f.append(line(rx_mcu, y, rx_res_l, y, color=INK, sw=1.7))
        # резистор (прямокутник)
        f.append(rect(rx_res_l, y - 9, rx_res_r - rx_res_l, 18, fill="#fff6e5",
                      stroke="#b8860b", sw=1.5, rx=4))
        f.append(text((rx_res_l + rx_res_r) / 2, y + 4, "R", size=10, bold=True,
                      color="#8a6d00"))
        # провід від резистора до сегмента
        f.append(line(rx_res_r, y, rx_disp, y, color=ON, sw=1.7))
        f.append(circle(rx_disp, y, 3.5, fill=ON, stroke="none", sw=0))
        # підпис сегмента всередині індикатора
        f.append(text(rx_disp + 22, y + 4, seg, size=12, bold=True, color=INK))

    # напис над колонкою резисторів
    f.append(text((rx_res_l + rx_res_r) / 2, ry0 - 22,
                  "220–330 Ом", size=11, bold=True, color="#8a6d00"))
    f.append(text((rx_res_l + rx_res_r) / 2, ry0 - 6,
                  "на КОЖНУ лінію", size=9.5, color=MUTED))

    # два COM → GND
    comy1 = dy0 + dh - 26
    fx = dx0 + dw / 2
    # виводи COM усередині корпусу
    f.append(text(dx0 + 22, comy1 - 2, "COM 3", size=10, bold=True, color=FIELD))
    f.append(text(dx0 + dw - 22, comy1 - 2, "COM 8", size=10, bold=True, color=FIELD,
                  anchor="end"))
    # шина землі під індикатором
    gndy = dy0 + dh + 26
    f.append(line(dx0 + 30, comy1 + 6, dx0 + 30, gndy, color=FIELD, sw=2))
    f.append(line(dx0 + dw - 30, comy1 + 6, dx0 + dw - 30, gndy, color=FIELD, sw=2))
    f.append(line(dx0 + 30, gndy, dx0 + dw - 30, gndy, color=FIELD, sw=2))
    # символ землі
    gx = dx0 + dw / 2
    f.append(line(gx, gndy, gx, gndy + 14, color=FIELD, sw=2))
    f.append(line(gx - 16, gndy + 14, gx + 16, gndy + 14, color=FIELD, sw=2.4))
    f.append(line(gx - 10, gndy + 20, gx + 10, gndy + 20, color=FIELD, sw=2.4))
    f.append(line(gx - 5, gndy + 26, gx + 5, gndy + 26, color=FIELD, sw=2.4))
    f.append(text(gx, gndy + 44, "GND", size=11, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 540,
                      "резистор ОБОВ'ЯЗКОВИЙ на кожній лінії; обидва COM — на GND (для спільного анода — на +, і рівні інверсні)",
                      size=11, fill=FILL, stroke=LINE, min_w=760)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_wiring()
    print("OK: 2 figures ->", IMG)
