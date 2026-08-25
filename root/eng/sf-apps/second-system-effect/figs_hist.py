# -*- coding: utf-8 -*-
# Фігури для вставки hist-second-system.md (окремий генератор, щоб не конфліктувати
# з figs.py статті-власника; вивід у ту саму теку ./img/).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_os_contrast():
    """Контраст двох поколінь ОС: простий пакетний монітор (одна програма) vs роздута OS/360."""
    W, H = 760, 440
    parts = []

    # ── ЛІВОРУЧ: проста система ──
    lx = 195
    parts.append(text(lx, 40, "Серія 700/7000", size=15, color=INK, bold=True))
    parts.append(text(lx, 60, "стрічковий пакетний монітор", size=12, color=MUTED))
    mx, my, mw, mh = lx - 110, 84, 220, 210
    parts.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=INK, sw=1.6))
    parts.append(text(lx, my + 20, "пам'ять", size=11, color=MUTED))
    parts.append(fitbox(mx + 26, my + 36, mw - 52, 96,
                        "ОДНА програма\nвиконується зараз",
                        size=13, fill="#eafaf1", stroke=FIELD, bold=True))
    parts.append(fitbox(mx + 26, my + 146, mw - 52, 46,
                        "монітор: бере\nнаступне завдання",
                        size=11, fill="#eef1f4", stroke=MUTED))
    # черга завдань зі стрічки
    ty = my + mh + 30
    for i, xx in enumerate((mx + 20, mx + 88, mx + 156)):
        parts.append(rect(xx, ty, 46, 26, fill="#eef1f4", stroke=MUTED, sw=1.2))
        parts.append(text(xx + 23, ty + 17, "зад.%d" % (i + 1), size=9, color=MUTED))
    parts.append(text(lx, ty + 50, "черга зі стрічки — по черзі", size=11, color=MUTED))

    # ── роздільник ──
    parts.append(line(W / 2, 74, W / 2, H - 30, color=FIELD, sw=1.4, dash="6 6"))

    # ── ПРАВОРУЧ: OS/360 ──
    rx = 570
    parts.append(text(rx, 40, "OS/360", size=15, color=POS, bold=True))
    parts.append(text(rx, 60, "друга система — охопити ВСЕ", size=12, color=MUTED))
    mx2, my2 = rx - 110, 84
    parts.append(rect(mx2, my2, mw, mh, fill="#fdecea", stroke=POS, sw=1.6))
    parts.append(text(rx, my2 + 20, "та сама пам'ять", size=11, color=MUTED))
    subs = ["багато-\nзадачність", "поділ\nпам'яті", "весь\nдіапазон", "наука +\nбізнес",
            "накла-\nдання", "…і ще"]
    sy = my2 + 32
    for i, s in enumerate(subs):
        col = i % 2
        row = i // 2
        bx = mx2 + 16 + col * 100
        by = sy + row * 50
        parts.append(fitbox(bx, by, 90, 42, s, size=10,
                            fill="#fadbd8", stroke=POS))
    parts.append(text(rx, my2 + mh - 10, "усе разом, в один захід", size=11, color=POS, bold=True))
    parts.append(text(rx, ty + 50, "кожна риса тягне власну машинерію", size=11, color=MUTED))

    render(os.path.join(IMG, 'os-contrast.svg'), W, H, *parts)


def fig_dinosaur():
    """Пік майстерності статичних накладань збігається з моментом їх непотрібності."""
    W, H = 760, 440
    parts = []
    ox, oy = 80, 320
    ax_w, ax_h = 640, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # X — час
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # Y
    parts.append(text(ox + ax_w, oy + 26, "час →", size=12, color=MUTED, anchor="end"))

    x0, xp = ox + 20, ox + 380
    y0, yp = oy - 24, oy - 200
    # крива майстерності техніки — росте до вершини (POS)
    parts.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" '
                  'fill="none" stroke="%s" stroke-width="3"/>' % (
                      x0, y0, (x0 + xp) / 2, yp - 46, xp, yp, POS)))
    parts.append(circle(xp, yp, 7, fill=POS, stroke=POS, sw=1))
    parts.append(text(x0, oy - 40, "майстерність техніки накладань", size=12, color=POS, anchor="start"))
    b1, w1, h1 = textbox(xp + 118, yp + 4, "вершина: «останній\nі найдовершеніший\nз динозаврів»",
                         size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b1)

    # лінія чинності припущення "пам'ять мала" — спадає (NEG, пунктир)
    ya, yb = oy - 178, oy - 34
    parts.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" '
                  'fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7 5"/>' % (
                      x0, ya, (x0 + xp) / 2 + 60, ya + 6, xp + 40, yb, NEG)))
    parts.append(text(x0, ya - 12, "чинність припущення «пам'ять мала, план наперед»",
                      size=12, color=NEG, anchor="start"))

    # обвід точки інтересу — де пік зустрічає майже-хибне припущення
    parts.append(circle(xp, yp, 12, fill="none", stroke=INK, sw=1.6))

    # підпис під віссю — що прийшло на зміну
    b3, w3, h3 = textbox(ox + ax_w / 2, oy + 78,
                         "на зміну: багатозадачність · динамічний розподіл пам'яті — система планує сама, на льоту",
                         size=11, fill="#eafaf1", stroke=FIELD, color=INK, min_w=560)
    parts.append(b3)

    render(os.path.join(IMG, 'dinosaur.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_os_contrast()
    fig_dinosaur()
    print("ok")
