# -*- coding: utf-8 -*-
"""Фігура до вставки «📜 Як bandgap навчився прокидатися».
Одна фігура:
  lineage.svg — родовід bandgap як ланцюг придатності: Хілбібер (1964, ідея) →
                Відлар (1969–1971, перша куповна реалізація, патент із Добкіним) →
                Брокау (1974, класичний осередок). Під лінією часу — що саме додано;
                окремою смугою — коли усвідомили два стани й потребу старт-вузла.
Запуск:  python figs_hist.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def lineage():
    """Три внески на одній лінії часу — ідея, реалізація, класична схема."""
    W, H = 760, 430
    p = [text(W / 2, 30, "Bandgap — ланцюг придатності, а не один «винахід»",
              size=17, bold=True)]

    # ── вісь часу ──
    ax0, ax1, ay = 70, 690, 110
    p.append(line(ax0, ay, ax1 + 14, ay, color=INK, sw=2.2))
    p.append(arrow(ax1 - 2, ay, ax1 + 16, ay, color=INK, sw=2.2))
    p.append(text(ax1 + 8, ay - 12, "час", size=12, color=MUTED, anchor="end"))

    # три віхи: (x, рік, заголовок, автор, що додано, колір рамки/заливки, текст-колір)
    nodes = [
        (170, "1964", "Ідея", "Девід Хілбібер",
         ["довів: із самих переходів", "можна зібрати стабільну", "опору (≈1.2567 В);", "стовпчики транзисторів"],
         NEG, "#eaf0fd", NEG),
        (390, "1969–71", "Перша реалізація", "Боб Відлар",
         ["перший куповний чип:", "LM109 → LM113 (1.2 В);", "патент US 3 617 859", "разом із Р. Добкіним"],
         FIELD, "#eafaf0", "#1e7a45"),
        (610, "1974", "Класична схема", "Пол Брокау",
         ["осередок Брокау:", "зчитування колектор-", "ного струму; виріб", "AD580 (2.5 В)"],
         POS, "#fdecea", POS),
    ]

    for x, yr, head, who, lines, col, fill, tcol in nodes:
        # вузол на осі
        p.append(circle(x, ay, 8, fill=fill, stroke=col, sw=2.6))
        p.append(text(x, ay - 18, yr, size=14, bold=True, color=col))
        # картка під віхою
        b, w, h = textbox(x, ay + 96, lines, size=11, fill=fill, stroke=col,
                          color=tcol, pad=10, min_w=180)
        # шапка картки (заголовок + автор) над тілом
        top = ay + 96 - h / 2
        p.append(line(x, ay + 8, x, top - 34, color=col, sw=1.6, dash="4,4"))
        p.append(text(x, top - 18, head, size=13, bold=True, color=tcol))
        p.append(text(x, top - 2, who, size=12, color=MUTED))
        p.append(b)

    # стрілки «зробив придатнішим» між віхами
    for xa, xb in [(170, 390), (390, 610)]:
        midx = (xa + xb) / 2
        p.append(arrow(xa + 70, ay, xb - 70, ay, color=MUTED, sw=1.6))
        p.append(text(midx, ay + 4, "зробив", size=10, color=MUTED))
        p.append(text(midx, ay + 16, "придатнішим", size=10, color=MUTED))

    # ── нижня смуга: коли усвідомили два стани й потребу старту ──
    by = 300
    bx0, bw, bh = 70, 620, 110
    p.append(rect(bx0, by, bw, bh, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(bx0 + 16, by + 26, "Що зрозуміли вже тут — і що тримається досі:",
                  size=13, bold=True, anchor="start"))
    p.append(fitbox(bx0 + 16, by + 38, bw - 32, 56,
                    "Самозміщення дарує незалежність від живлення — але петля I = f(I) завжди\n"
                    "має f(0) = 0, тож «нуль» теж стійка рівновага. Мертву точку не «вилікувати»\n"
                    "розумнішою петлею; її ОБХОДЯТЬ окремим старт-вузлом, що штовхне й вчасно піде.",
                    size=12, fill=BG, stroke=MUTED, color=INK))

    return render(os.path.join(OUT, "lineage.svg"), W, H, *p)


if __name__ == "__main__":
    print(lineage())
