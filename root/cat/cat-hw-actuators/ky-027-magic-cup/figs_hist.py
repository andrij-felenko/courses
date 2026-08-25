# -*- coding: utf-8 -*-
"""Фігури до вставки «Історія: від ртутної краплі до сталевої кульки»
(вставка hist-mercury-to-ball.md теми «KY-027 — Magic Light Cup»).
Запуск:  python figs_hist.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MERC = "#8a8f98"   # рідкий метал (ртуть)
BALL = "#5a6270"   # сталева кулька


def _tube(cx, cy, w=134, h=44):
    """Горизонтальна колба вимикача з двома контактами на ЛІВОМУ торці.
    Повертає (svg, ліва_межа, права_межа)."""
    s = []
    s.append(rect(cx - w / 2, cy - h / 2, w, h, fill="#eef1f4", stroke=INK, sw=1.6, rx=h / 2))
    # два контакти-стрижні входять з лівого торця
    s.append(line(cx - w / 2, cy - 9, cx - w / 2 + 34, cy - 9, color=INK, sw=2.2))
    s.append(line(cx - w / 2, cy + 9, cx - w / 2 + 34, cy + 9, color=INK, sw=2.2))
    return "".join(s), cx - w / 2, cx + w / 2


# ── 1. Два вимикачі поруч: ртутна крапля vs сталева кулька ────────────────────
def fig_two_switches():
    W, H = 820, 520
    f = []
    f.append(text(W / 2, 32, "Один нахил — два способи замкнути коло", size=17, bold=True))

    # низький кінець ПОЗНАЧАЄМО стрілкою вниз (без обертання колби — щоб координати були прямі)
    def tilt_arrow(cx, cy):
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
                'marker-end="url(#arrow)"/>' % (cx, cy, cx, cy + 26, MUTED))

    # ── ЛІВА колонка: ртутний ──
    lx = 220
    f.append(text(lx, 70, "ртутний вимикач", size=14, bold=True, color=POS))
    tube, tl, tr = _tube(lx, 130)
    f.append(tube)
    # ртуть — калюжка на контактах (лівий, «низький» кінець)
    f.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f z" fill="%s"/>'
             % (tl + 4, 130 + 18, tl + 4, 130 - 8, lx - 30, 130 - 10,
                lx + 2, 130 - 4, lx + 14, 130 + 8, lx + 14, 130 + 18, MERC))
    f.append(tilt_arrow(tl + 16, 130 + 24))
    f.append(text(tl + 46, 130 + 40, "низький кінець", size=10, color=MUTED, anchor="start"))
    box, bw, bh = textbox(lx, 205, "крапля ртуті стікає на контакти\nі ЗМОЧУЄ їх → замкнено",
                          size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(box)

    # ── ПРАВА колонка: кульковий ──
    rx = 600
    f.append(text(rx, 70, "кульковий вимикач", size=14, bold=True, color=NEG))
    tube2, tl2, tr2 = _tube(rx, 130)
    f.append(tube2)
    # тверда кулька в лівому («низькому») кінці
    bxc = tl2 + 22
    f.append(circle(bxc, 130, 13, fill=BALL, stroke=INK, sw=1.4))
    f.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#cfd4da"/>' % (bxc - 4, 130 - 4))
    f.append(tilt_arrow(tl2 + 16, 130 + 24))
    f.append(text(tl2 + 46, 130 + 40, "низький кінець", size=10, color=MUTED, anchor="start"))
    box2, _, _ = textbox(rx, 205, "тверда кулька котиться на контакти\nй ТОРКАЄТЬСЯ їх → замкнено",
                         size=11, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(box2)

    # ── роздільник ──
    f.append(line(60, 258, W - 60, 258, color=MUTED, sw=1, dash="4 4"))
    f.append(text(W / 2, 286, "а що бачить мікроконтролер у мить замикання?", size=13, bold=True, color=MUTED))

    # осцилограми: ртуть — чистий фронт; кулька — брязкіт
    gy = 400  # рівень «0»
    hi = gy - 44  # рівень «1»

    # ліворуч: ртуть
    f.append(text(lx, 322, "рідина не рветься —", size=11, color=POS))
    f.append(text(lx, 338, "різкий, чистий фронт", size=11, color=POS))
    gxL = 130
    f.append(line(gxL, hi, gxL + 84, hi, color=INK, sw=2))
    f.append(line(gxL + 84, hi, gxL + 84, gy, color=INK, sw=2))
    f.append(line(gxL + 84, gy, gxL + 176, gy, color=INK, sw=2))
    f.append(text(gxL + 40, hi - 8, "1", size=10, color=MUTED))
    f.append(text(gxL + 150, gy + 15, "0", size=10, color=MUTED))

    # праворуч: кулька — зубчастий брязкіт
    gxR = 470
    f.append(text(rx, 322, "тверді поверхні відскакують —", size=11, color=NEG))
    f.append(text(rx, 338, "коротка «пилка», тоді спокій", size=11, color=NEG))
    f.append(line(gxR, hi, gxR + 70, hi, color=INK, sw=2))
    zx = gxR + 70
    ys = [gy, hi + 8, gy, hi + 14, gy, hi + 20, gy]
    step = 11
    d = "M%.1f %.1f" % (zx, hi)
    d += " L%.1f %.1f" % (zx, gy)
    for i, yv in enumerate(ys):
        d += " L%.1f %.1f" % (zx + i * step, yv)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, INK))
    endx = zx + (len(ys) - 1) * step
    f.append(line(endx, gy, endx + 70, gy, color=INK, sw=2))
    f.append(text(gxR + 34, hi - 8, "1", size=10, color=MUTED))
    f.append(text(zx + 30, gy + 15, "брязкіт", size=10, color=MUTED))

    # підсумок унизу — БАГАТОРЯДКОВИЙ, щоб не вилазив за полотно
    box3, _, _ = textbox(W / 2, 480,
                         "Ртуть замикала безшумно й без брязкоту — тому її колись і ставили.\n"
                         "Кулька дешевша й безпечніша, та брязкіт доводиться гасити в коді.",
                         size=11, color=INK, fill=FILL, stroke=MUTED)
    f.append(box3)

    render(os.path.join(IMG, 'merc-vs-ball.svg'), W, H, "".join(f))


# ── 2. Часова смуга: від ртуті до заборони ───────────────────────────────────
def fig_timeline():
    W, H = 860, 340
    f = []
    f.append(text(W / 2, 32, "Шлях ртутного вимикача: розквіт і захід", size=17, bold=True))

    x0, x1 = 80, 790
    axisY = 170
    f.append(line(x0, axisY, x1, axisY, color=INK, sw=2))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
             % (x1 + 10, axisY, x1 - 4, axisY - 6, x1 - 4, axisY + 6, INK))

    # (позиція 0..1, рік, угорі?, текст)
    marks = [
        (0.03, "1920-ті", True, "L. A. M. Phelan:\nртутні вимикачі,\n52 патенти"),
        (0.24, "1953", False, "Honeywell T87 —\nмільйони термостатів\nз ртутною колбою"),
        (0.45, "1960–80-ті", True, "авто: підсвітка\nбагажника й капота\nна ртутному вимикачі"),
        (0.66, "2006", False, "RoHS (ЄС):\nртуть з електроніки\nфактично геть"),
        (0.83, "2013 → 2017", True, "Мінаматська\nконвенція:\nприйнято → чинна"),
        (0.99, "2025", False, "світова заборона\nртутних вимикачів\nі реле"),
    ]
    for pos, yr, up, txt in marks:
        x = x0 + (x1 - x0) * pos
        col = POS if pos < 0.6 else NEG
        f.append(circle(x, axisY, 6, fill=col, stroke=INK, sw=1.4))
        f.append(text(x, axisY + (-18 if up else 24), yr, size=12, bold=True, color=col))
        # центр рамки з запасом від осі
        cyb = axisY - 86 if up else axisY + 92
        box, bw, bh = textbox(x, cyb, txt, size=10, color=INK,
                              fill=("#fdecea" if col == POS else "#eaf0fd"), stroke=col, pad=7)
        # поводок: від точки (трохи відступивши) РІВНО до КРАЮ рамки — не входить усередину
        if up:
            f.append(line(x, axisY - 30, x, cyb + bh / 2, color=MUTED, sw=1, dash="3 3"))
        else:
            f.append(line(x, axisY + 36, x, cyb - bh / 2, color=MUTED, sw=1, dash="3 3"))
        f.append(box)

    render(os.path.join(IMG, 'merc-timeline.svg'), W, H, "".join(f))


if __name__ == "__main__":
    fig_two_switches()
    fig_timeline()
    print("OK: merc-vs-ball.svg, merc-timeline.svg")
