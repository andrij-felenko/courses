# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_package():
    """Чотири документи як пакет передачі: кожен відповідає на одне питання."""
    W, H = 720, 430
    parts = []
    parts.append(text(W/2, 30, "Пакет документації = відповіді на чотири питання", size=17, bold=True))

    # центр — проєкт (плата/прошивка)
    cx, cy = W/2, 232
    b, bw, bh = textbox(cx, cy, "ПРОЄКТ\nплата + прошивка", size=14, bold=True,
                        fill="#eef2ff", stroke=NEG, sw=2, pad=14)
    parts.append(b)

    # чотири картки-документи навколо
    cards = [
        (150, 110, "README", "Що це і як\nзапустити?", FIELD),
        (570, 110, "Схема",  "Як воно\nз'єднане?", NEG),
        (150, 355, "BOM",    "З чого\nскласти?", "#b8860b"),
        (570, 355, "Журнал змін", "Що і коли\nзмінилось?", POS),
    ]
    for x, y, name, q, col in cards:
        cb, cw, ch = textbox(x, y, name, size=15, bold=True, fill="#ffffff", stroke=col, sw=2, pad=10)
        parts.append(cb)
        parts.append(mtext(x, y + ch/2 + 20, q, size=12, color=MUTED))
        # лінія від картки до центру
        sx = x + (cw/2 if x < cx else -cw/2) if abs(x-cx) > 120 else x
        parts.append(line(x, y + (ch/2 if y < cy else -ch/2), cx, cy + (-bh/2 if y < cy else bh/2),
                          color=MUTED, sw=1.3, dash="4 4"))

    render(os.path.join(OUT, 'doc-package.svg'), W, H, *parts)


def fig_semver():
    """Анатомія номера версії 2.4.1 — що піднімає кожне число."""
    W, H = 720, 340
    parts = []
    parts.append(text(W/2, 30, "Номер версії: 2 . 4 . 1", size=17, bold=True))

    # три числа великим шрифтом
    y0 = 95
    nums = [(200, "2", "MAJOR", POS, "ламає\nсумісність"),
            (360, "4", "MINOR", FIELD, "нова функція,\nсумісно назад"),
            (520, "1", "PATCH", NEG, "виправлення,\nсумісно")]
    parts.append(text(280, y0, ".", size=46, bold=True, color=MUTED))
    parts.append(text(440, y0, ".", size=46, bold=True, color=MUTED))
    for x, n, name, col, what in nums:
        parts.append(text(x, y0, n, size=54, bold=True, color=col))
        parts.append(text(x, y0 + 40, name, size=15, bold=True, color=col))
        b, bw, bh = textbox(x, y0 + 115, what, size=13, fill="#ffffff", stroke=col, sw=1.8, pad=10)
        parts.append(b)
        parts.append(arrow(x, y0 + 55, x, y0 + 115 - bh/2, color=col, sw=1.6))

    # правило внизу
    fb = fitbox(90, 288, 540, 38,
                "Змінив так, що старий код зламається -> підніми MAJOR, молодші -> 0",
                size=13, fill="#fff8e6", stroke="#b8860b", sw=1.6)
    parts.append(fb)

    render(os.path.join(OUT, 'semver-anatomy.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_package()
    fig_semver()
    print("ok")
