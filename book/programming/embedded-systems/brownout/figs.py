# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Brown-out».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три зони напруги — «недокормлено» гірше за «вимкнено» ───────────
# Ідея: між нормою і нулем є СІРА ЗОНА, де чіп ще працює, але хибно. Просадка
# від сплеску радіо саме туди й затягує — гірше, ніж чистий нуль.
def fig_gray_zone():
    W, H = 815, 410
    P = [text(W / 2, 28, "Сіра зона brown-out: «недокормлено» гірше за «вимкнено»",
              size=15, bold=True)]

    L, R = 70.0, 710.0          # межі смуг по X
    y_top = 88.0                 # верх «норми»
    y_bod = 214.0                # лінія порога BOD
    y_off = 286.0                # верх «вимкнено»
    y_bot = 316.0                # дно

    # три кольорові смуги (заливки без рамок)
    P.append(rect(L, y_top, R - L, y_bod - y_top, fill="#e8f5e9", stroke=FIELD, sw=0, rx=0))
    P.append(rect(L, y_bod, R - L, y_off - y_bod, fill="#f5f5dc", stroke=POS, sw=0, rx=0))
    P.append(rect(L, y_off, R - L, y_bot - y_off, fill="#d0d0d0", stroke=MUTED, sw=0, rx=0))

    # підписи смуг праворуч
    P.append(mtext(R + 6, y_top + 56, ["НОРМА", "(чиста робота)"], size=11,
                   color=FIELD, anchor="start", bold=True))
    P.append(mtext(R + 6, y_bod + 26, ["СІРА ЗОНА", "(недетермінований", "збій)"],
                   size=11, color=POS, anchor="start", bold=True))
    P.append(mtext(R + 6, y_off + 18, ["≈ 0 В", "(чисто вимкнено)"], size=10,
                   color=MUTED, anchor="start"))

    # лінія порога BOD
    P.append(line(L, y_bod, R, y_bod, color="#c0392b", sw=2, dash="8 4"))
    P.append(text(L - 6, y_bod + 4, "поріг BOD", size=11, color="#c0392b",
                  anchor="end", bold=True))

    # крива напруги: рівна, провал у сіру зону від сплеску, відновлення
    pts = []
    x = L
    dx = (R - L)
    while x <= R:
        t = (x - L) / dx
        v = 0.0                       # 0 = верх норми, 1 = глибина провалу
        # провал десь біля третини смуги
        if 0.27 <= t <= 0.50:
            u = (t - 0.27) / (0.50 - 0.27)
            v = math.sin(u * math.pi)            # 0→1→0
        y = y_top + 22 + v * (y_off - y_top - 8)  # переводимо у Y
        pts.append((x, y))
        x += 5.5
    for i in range(1, len(pts)):
        P.append(line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1],
                      color="#2457d6", sw=2.5))

    # стрілка-причина: сплеск Wi-Fi штовхає напругу вниз
    cause_y = 372.0
    bx_cx = L + (R - L) * 0.385
    box, bw, bh = textbox(bx_cx, cause_y, "сплеск Wi-Fi TX (300+ мА)", size=11,
                          fill="#fdecea", stroke="#c0392b", sw=2, color="#c0392b", bold=True)
    P.append(box)
    P.append(arrow(bx_cx, cause_y - bh / 2, bx_cx, y_bod + 18, color="#c0392b", sw=1.5))

    # наслідки в сірій зоні
    cons_y = y_bod + 26
    P.append(mtext(L + (R - L) * 0.36, cons_y, ["биті", "читання"], size=10, color="#c07000"))
    P.append(mtext(L + (R - L) * 0.50, cons_y, ["зриви", "Flash"], size=10, color="#c07000"))
    P.append(mtext(L + (R - L) * 0.64, cons_y, ["стрибки", "PC"], size=10, color="#c07000"))

    render(os.path.join(IMG, "gray-zone.svg"), W, H, *P)


# ── Фігура 2: діагностична таблиця «живлення чи код» ──────────────────────────
# Ідея: п'ять ознак, кожна тягне вирок у один бік. Причина reset + кореляція з
# навантаженням → живлення; стабільна відтворюваність + той самий backtrace → код.
def fig_power_or_bug():
    W, H = 740, 386
    P = [text(W / 2, 28, "Діагностика: збій живлення чи баг прошивки?", size=15, bold=True)]

    Lx, Rx = 40.0, 700.0
    col_sign = (Lx + 480.0) / 2     # центр колонки «ознака»
    col_verdict = 580.0
    P.append(text(col_sign, 64, "Ознака", size=12, bold=True))
    P.append(text(col_verdict, 64, "Вирок", size=12, bold=True))
    P.append(line(Lx, 78, Rx, 78, color=MUTED, sw=1))

    rows = [
        (["Причина reset = BROWNOUT", "(esp_reset_reason())"], "ЖИВЛЕННЯ", True),
        (["Корелює зі сплеском", "навантаження (Wi-Fi TX, мотор)"], "ЖИВЛЕННЯ", True),
        (["Зникає від кращого БЖ /", "конденсатора / кабелю"], "ЖИВЛЕННЯ", True),
        (["Відтворюється на стенді", "при стабільному живленні"], "КОД", False),
        (["Завжди в одному місці коду", "(backtrace збігається)"], "КОД", False),
    ]
    y = 88.0
    rh, gap = 46.0, 6.0
    for i, (sign, verdict, is_power) in enumerate(rows):
        sfill = "#f4f6f8" if i % 2 == 0 else BG
        P.append(rect(Lx, y, 440, rh, fill=sfill, stroke=MUTED, sw=0.8, rx=6))
        P.append(mtext(col_sign, y + rh / 2 - 6, sign, size=11, color=INK))
        if is_power:
            vfill, vstroke = "#e8f5e9", FIELD
        else:
            vfill, vstroke = "#fdecea", "#c0392b"
        P.append(rect(490, y, 180, rh, fill=vfill, stroke=vstroke, sw=2, rx=6))
        P.append(text(col_verdict, y + rh / 2 + 4, verdict, size=13, bold=True))
        y += rh + gap

    # підсумкова смуга
    sb = textbox(W / 2, y + 13,
                 "Причина reset + кореляція з навантаженням → живлення. Не шукай баг там, де його немає.",
                 size=11, fill="#e8f5e9", stroke=FIELD, sw=2, color=INK, bold=True)[0]
    P.append(sb)

    render(os.path.join(IMG, "power-or-bug.svg"), W, H, *P)


if __name__ == "__main__":
    fig_gray_zone()
    fig_power_or_bug()
    print("OK: figs written to", IMG)
