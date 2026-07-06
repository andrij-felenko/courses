# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def uncertainty_lever():
    """Конус невизначеності як важіль: пасивно він звужується сам аж під кінець;
    дешеві дослідники (спайки) втягують його рано — знання приходить тоді,
    коли рішення ще дешеве відкотити."""
    W, H = 820, 480
    x0, y0 = 110, 70          # початок осі часу (ліворуч)
    x1, y1 = 720, 380         # кінець графіка (низ-право)
    ymid = (y0 + y1) / 2      # лінія «правильної відповіді» — центр конуса
    frags = []

    # Осі
    frags.append(line(x0, y0 - 6, x0, y1, color=INK, sw=2))          # вісь величини (розкид)
    frags.append(line(x0, y1, x1 + 12, y1, color=INK, sw=2))         # вісь часу
    frags.append(arrow(x1 - 6, y1, x1 + 16, y1, color=INK))
    frags.append(text((x0 + x1) / 2, y1 + 40,
                      "час і вкладені зусилля  →", size=13, color=MUTED))
    frags.append('<text x="42" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 42 %.1f)">'
                 'розкид можливих результатів</text>'
                 % (ymid, FONT, MUTED, ymid))

    # Лінія істини (куди насправді збіжиться відповідь)
    frags.append(line(x0, ymid, x1, ymid, color=MUTED, sw=1.2, dash="2,6"))

    span = (y1 - y0) * 0.46   # піврозхил конуса на старті

    # ── ПАСИВНИЙ конус: широкий майже до кінця, звужується різко під фініш ──
    def passive(t):
        # тримає широчінь, спадає лише в останній чверті
        return span * (1 - 0.12 * t - 0.9 * max(0.0, t - 0.7) / 0.3)
    n = 60
    top_p = []
    bot_p = []
    for i in range(n + 1):
        t = i / n
        px = x0 + t * (x1 - x0)
        s = max(4.0, passive(t))
        top_p.append((px, ymid - s))
        bot_p.append((px, ymid + s))
    poly_p = top_p + list(reversed(bot_p))
    dpath = " ".join("%.1f,%.1f" % p for p in poly_p)
    frags.append('<polygon points="%s" fill="#fdecea" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="7,5" opacity="0.55"/>'
                 % (dpath, POS))

    # ── АКТИВНИЙ конус: втягнутий рано трьома дешевими дослідами ──
    def active(t):
        return span * (1 - t) ** 1.9 + 3.0
    top_a = []
    bot_a = []
    for i in range(n + 1):
        t = i / n
        px = x0 + t * (x1 - x0)
        s = max(3.0, active(t))
        top_a.append((px, ymid - s))
        bot_a.append((px, ymid + s))
    poly_a = top_a + list(reversed(bot_a))
    apath = " ".join("%.1f,%.1f" % p for p in poly_a)
    frags.append('<polygon points="%s" fill="#eafaf0" stroke="%s" '
                 'stroke-width="2" opacity="0.85"/>' % (apath, FIELD))

    # Позначки дешевих дослідів (спайки) на активному конусі — де він стрибком вужчає
    for t in (0.16, 0.34, 0.55):
        px = x0 + t * (x1 - x0)
        frags.append(circle(px, ymid, 5.5, fill=BG, stroke=FIELD, sw=2.4))
    # один спільний підпис під ланцюжком спайків (щоб не тіснити три написи)
    sx = x0 + 0.34 * (x1 - x0)
    sy = y1 - 34
    b1, bw1, bh1 = textbox(sx, sy, "дешеві досліди\n(спайк, ходячий кістяк)",
                           size=12, bold=True, fill="#eafaf0", stroke=FIELD, pad=8)
    # поводок від ВЕРХУ рамки вгору до конуса — не заходить у власну рамку
    frags.append(line(sx, sy - bh1 / 2 - 2, sx, ymid + active(0.34) + 4,
                      color=FIELD, sw=1.3, dash="3,4"))
    frags.append(b1)

    # Підпис пасивного конуса — угорі праворуч, у широкій зоні, поза активним
    pxp = x0 + 0.62 * (x1 - x0)
    b2, bw2, bh2 = textbox(pxp, y0 + 34, "чекати й не діяти:\nтуман тримається до кінця",
                           size=12, bold=True, fill="#fdecea", stroke=POS, pad=8)
    frags.append(b2)

    # Мітка лінії істини — біля правого кінця, трохи вище лінії
    frags.append(text(x1 - 70, ymid - 8, "правильна відповідь", size=11,
                      color=MUTED, italic=True))

    render(os.path.join(OUT, 'uncertainty-lever.svg'), W, H, *frags,
           title="Невизначеність можна не перечікувати, а збивати заздалегідь")


def bet_vs_guess():
    """Дві доріжки в часі: наосліп великий коміт → пізнє й дороге відкриття (стіна);
    проти дешевого циклу ставка→факт→рішення, що доводить до зваженого вибору."""
    W, H = 820, 470
    frags = []
    xL = 90                    # старт доріжок
    xR = 700                   # правий край
    # ── Верхня доріжка: здогад і великий коміт ──
    yT = 150
    frags.append(text(xL - 6, yT - 66, "Наосліп: угадати й забетонувати",
                      size=15, color=POS, bold=True, anchor="start"))
    # крок 1 — велика ставка одразу
    s1, w1, h1 = textbox(xL + 95, yT, "велике рішення\nодразу, на здогад",
                         size=13, bold=True, fill="#fdecea", stroke=POS, pad=10)
    frags.append(s1)
    # стрілка «місяці коду на припущенні»
    ax1 = xL + 95 + w1 / 2
    ax2 = xR - 150
    frags.append(arrow(ax1 + 6, yT, ax2 - 6, yT, color=POS, sw=2.4))
    frags.append(text((ax1 + ax2) / 2, yT - 16, "місяці коду на припущенні",
                      size=12, color=MUTED))
    # стіна — дороге відкриття помилки
    wall_x = xR - 96
    frags.append(rect(wall_x, yT - 44, 150, 88, fill="#f7d7d2", stroke=POS, sw=2.4, rx=8))
    frags.append(mtext(wall_x + 75, yT - 8, ["припущення", "хибне —", "переробити все"],
                       size=12.5, color=POS, bold=True))

    # ── Нижня доріжка: дешевий цикл ставок ──
    yB = 340
    frags.append(text(xL - 6, yB - 96, "Під невизначеністю: ставити дешево й вчитися",
                      size=15, color=FIELD, bold=True, anchor="start"))
    # цикл: ставка → факт → (звузити) назад; три оберти зі зростанням певності
    cyc_x = [xL + 95, xL + 280, xL + 465]
    labels = ["дешева\nставка", "факт із\nживого", "звузити\nваріанти"]
    fills  = ["#eafaf0", "#eaf0fd", "#eafaf0"]
    strokes = [FIELD, NEG, FIELD]
    boxes = []
    for i, (cx, lab, fl, st) in enumerate(zip(cyc_x, labels, fills, strokes)):
        b, bw, bh = textbox(cx, yB, lab, size=12.5, bold=True, fill=fl, stroke=st, pad=9)
        boxes.append((cx, bw, bh))
        frags.append(b)
    # стрілки по циклу вперед
    for i in range(len(cyc_x) - 1):
        c1 = cyc_x[i] + boxes[i][1] / 2
        c2 = cyc_x[i + 1] - boxes[i + 1][1] / 2
        frags.append(arrow(c1 + 5, yB, c2 - 5, yB, color=INK, sw=2))
    # зворотна дуга «повтори, поки туман» — під доріжкою, щоб не чіпати рамки
    arc_y = yB + 60
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,5" '
                 'marker-end="url(#arrow)"/>'
                 % (cyc_x[2], yB + boxes[2][2] / 2 + 2,
                    cyc_x[2], arc_y, cyc_x[0], arc_y,
                    cyc_x[0], yB + boxes[0][2] / 2 + 4, MUTED))
    frags.append(text((cyc_x[0] + cyc_x[2]) / 2, arc_y + 18,
                      "повторюй, поки певність не окупить ціну рішення",
                      size=12, color=MUTED))
    # фінал — зважене рішення
    dec_x = xR - 40
    frags.append(arrow(cyc_x[2] + boxes[2][1] / 2 + 5, yB, dec_x - 46, yB, color=INK, sw=2))
    d, dw, dh = textbox(dec_x, yB, "рішення\nна фактах", size=13, bold=True,
                        fill="#d8f3e3", stroke=FIELD, pad=10)
    frags.append(d)

    render(os.path.join(OUT, 'bet-vs-guess.svg'), W, H, *frags,
           title="Не вгадати наосліп, а зробити ставку дешевою й зворотною")


if __name__ == "__main__":
    uncertainty_lever()
    bet_vs_guess()
    print("done")
