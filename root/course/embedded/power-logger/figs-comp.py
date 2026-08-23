# -*- coding: utf-8 -*-
"""Фігури до вставки «Давач струму з цифровим виходом» (comp) кроку «Логер споживання».
Запуск:  python figs-comp.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині чипа: аналоговий вхід → ΔΣ АЦП → усереднення → множник → регістри ──
def fig_chip_block():
    W, H = 820, 470
    f = [text(W / 2, 28,
              "Усередині давача струму: від мілівольтів на шунті до готових чисел по шині",
              size=14.5, bold=True)]

    # зліва — шунт між IN+/IN−
    sx, sy = 40, 150
    f.append(plus(sx + 14, sy - 6, 8))
    f.append(minus(sx + 14, sy + 86, 8))
    f.append(text(sx + 36, sy - 2, "IN+", size=11, color=POS, anchor="start"))
    f.append(text(sx + 36, sy + 90, "IN−", size=11, color=NEG, anchor="start"))
    # сам шунт як прямокутник у силовому проводі
    f.append('<rect x="%.1f" y="%.1f" width="14" height="64" rx="3" fill="#fff7e6" '
             'stroke="#b8860b" stroke-width="1.6"/>' % (sx + 6, sy + 12))
    f.append(text(sx + 13, sy + 110, "шунт", size=10.5, color="#b8860b"))
    f.append(text(sx + 13, sy + 124, "R_ш", size=10, color=MUTED, italic=True))
    # силова лінія крізь шунт
    f.append(line(sx + 13, sy + 6, sx + 13, sy + 12, color=MUTED, sw=2.2))
    f.append(line(sx + 13, sy + 76, sx + 13, sy + 80, color=MUTED, sw=2.2))
    f.append(text(sx + 13, sy - 22, "I", size=12, bold=True, color=INK))
    f.append(text(sx - 4, sy - 22, "→", size=13, color=MUTED, anchor="end"))

    # межа чипа
    cx0, cy0, cw, ch = 150, 70, 540, 300
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="12" fill="#fafbfc" '
             'stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (cx0, cy0, cw, ch, INK))
    f.append(text(cx0 + 12, cy0 + 20, "мікросхема давача струму", size=11, color=MUTED, anchor="start"))

    # дроти від IN+/IN− у чип
    f.append(line(sx + 22, sy - 6, cx0, sy - 6, color=POS, sw=1.6))
    f.append(line(sx + 22, sy + 86, cx0, sy + 86, color=NEG, sw=1.6))

    # ланцюг блоків усередині
    by = 150
    bh = 58
    blocks = [
        ("PGA\n(×1 / ×4)", "#eafaf1", FIELD),
        ("ΔΣ АЦП\n16…20 біт", "#eaf0fd", NEG),
        ("усереднення\n1…1024×", "#f4f6f8", INK),
    ]
    bx = cx0 + 28
    bw = 118
    gap = 26
    cen = []
    for i, (t, fill, col) in enumerate(blocks):
        x = bx + i * (bw + gap)
        f.append(fitbox(x, by, bw, bh, t, size=11.5, bold=True, fill=fill, stroke=col))
        cen.append(x + bw / 2)
        if i == 0:
            f.append(arrow(cx0 + 2, by + bh / 2, x - 4, by + bh / 2, color=LINE))
        else:
            f.append(arrow(cen[i - 1] + bw / 2 + 4, by + bh / 2, x - 4, by + bh / 2, color=LINE))

    # цифровий множник + регістр калібрування
    mulx = cen[2] + bw / 2 + 26
    muly = by - 6
    f.append(fitbox(mulx, muly, 120, bh + 12, "цифровий\nмножник", size=11.5, bold=True,
                    fill="#fdecea", stroke=POS))
    f.append(arrow(cen[2] + bw / 2 + 4, by + bh / 2, mulx - 4, by + bh / 2, color=LINE))
    # CAL зверху в множник
    f.append(fitbox(mulx + 4, cy0 + 34, 112, 34, "регістр\nкалібрування", size=10.5,
                    fill="#fffbe6", stroke="#b8860b"))
    f.append(arrow(mulx + 60, cy0 + 68, mulx + 60, muly - 4, color="#b8860b", sw=1.5))

    # регістри-результати справа
    regx = cx0 + cw - 150
    regy = by + bh + 34
    f.append(fitbox(regx, regy, 134, 88,
                    "регістри:\nструм (A)\nпотужність (W)\nзаряд (C)\nенергія (J)", size=10.5,
                    fill="#eafaf1", stroke=FIELD))
    f.append(line(mulx + 60, muly + bh + 12, mulx + 60, regy - 4, color=LINE, sw=1.5))
    f.append(arrow(mulx + 60, regy - 4, regx + 67, regy - 4, color=LINE))
    f.append(line(regx + 67, regy - 4, regx + 67, regy, color=LINE, sw=1.5))

    # шина назовні
    busx = cx0 + cw
    f.append(arrow(regx + 134, regy + 44, busx + 58, regy + 44, color=POS))
    f.append(mtext(busx + 92, regy + 32, ["I²C / SPI", "до МК"], size=11, bold=True,
                   color=POS, anchor="middle"))

    # ALERT-пін окремо
    f.append(line(cx0 + cw / 2, cy0 + ch, cx0 + cw / 2, cy0 + ch + 26, color="#c0392b",
                  sw=1.6, dash="4,3"))
    f.append(text(cx0 + cw / 2, cy0 + ch + 40, "ALERT — апаратна тривога повз шину",
                  size=10.5, color="#c0392b"))

    b, _, _ = textbox(W / 2, 448,
                      "Аналоговий тракт живе в чипі: код отримує вже готовий струм, "
                      "а накопичувач заряду рахує у фоні без нього",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "comp-chip-block.svg"), W, H, *f)


# ── 2. Накопичувач рахує у фоні; код читає рідко. Continuous держить, triggered морозить ──
def fig_accumulator():
    W, H = 820, 470
    f = [text(W / 2, 28,
              "Накопичувач заряду рахує у фоні: код будиться рідко й знімає підсумок",
              size=14.5, bold=True)]

    # верхня смуга — безперервні перетворення (зубчики) у continuous-режимі
    ox, oy = 60, 130
    span = 700
    f.append(text(ox - 8, oy - 38, "continuous", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(line(ox, oy, ox + span, oy, color=MUTED, sw=1.2))
    n = 40
    for i in range(n):
        x = ox + (i / n) * span
        w = span / n
        # маленькі стовпчики — окремі перетворення t_conv × усереднення
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="14" fill="%s" '
                 'fill-opacity="0.5" stroke="%s" stroke-width="0.6"/>'
                 % (x, oy - 14, w - 1.3, FIELD, FIELD))
    f.append(text(ox + span / 2, oy - 22, "перетворення без пауз: t_conv × усереднення",
                  size=10, color=MUTED, anchor="middle"))

    # сходинки накопичувача під смугою
    ay = 270
    f.append(text(ox - 8, ay - 70, "накопичувач\nзаряду", size=11, color=INK, anchor="start"))
    acc = 0.0
    prevx, prevy = ox, ay
    steps = [4, 4, 5, 16, 22, 16, 5, 4, 4, 4, 18, 24, 17, 5, 4, 4, 4, 4, 6, 5]
    total = sum(steps)
    m = len(steps)
    for i, s in enumerate(steps):
        acc += s
        x = ox + ((i + 1) / m) * span
        yv = ay - (acc / total) * 150
        f.append(line(prevx, prevy, x, prevy, color=INK, sw=1.6))
        f.append(line(x, prevy, x, yv, color=INK, sw=1.6))
        prevx, prevy = x, yv
    f.append(line(ox, ay, ox, ay - 158, color=MUTED, sw=1.2))

    # дві точки читання кодом (рідко) — вертикальні пунктири
    for frac, lab in [(7.0 / m, "read 1"), (14.0 / m, "read 2")]:
        rx = ox + frac * span
        f.append(line(rx, oy - 30, rx, ay + 6, color=POS, sw=1.3, dash="5,3"))
        f.append(text(rx, ay + 22, lab, size=10.5, color=POS, anchor="middle"))
    f.append(text(ox + span * 0.5, ay + 22, "← між читаннями код спить, заряд росте сам →",
                  size=10.5, color=MUTED, anchor="middle"))

    # нижня врізка: triggered морозить накопичувач
    ty = 350
    f.append(line(ox, ty + 40, ox + span, ty + 40, color=MUTED, sw=1.2))
    f.append(text(ox - 8, ty + 16, "triggered", size=11.5, bold=True, color=POS, anchor="start"))
    # один одиничний вимір, далі тиша
    f.append('<rect x="%.1f" y="%.1f" width="20" height="14" fill="%s" fill-opacity="0.5" '
             'stroke="%s" stroke-width="0.8"/>' % (ox + 40, ty + 26, POS, POS))
    f.append(line(ox + 80, ty + 40, ox + span, ty + 40, color=MUTED, sw=1.0, dash="3,4"))
    f.append(text(ox + 70, ty + 20, "один вимір на запит", size=10, color=POS, anchor="start"))
    f.append(text(ox + 360, ty + 20, "далі пауз нема чим інтегрувати — накопичувач НЕ дійсний",
                  size=10.5, color="#c0392b", anchor="start"))

    b, _, _ = textbox(W / 2, 448,
                      ["continuous: накопичувач — чесний інтеграл струму.",
                       "triggered: між поодинокими вимірами струм не лічиться — заряд/енергія беззмістовні"],
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "comp-accumulator.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chip_block()
    fig_accumulator()
    print("OK: 2 figures ->", IMG)
