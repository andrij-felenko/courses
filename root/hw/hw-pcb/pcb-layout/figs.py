# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Доріжка — це не дріт, а опір + котушка ───────────────────────────────
def fig_trace_is_rl():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 28, "Те, що схема малює дротом, плата робить опором і котушкою", size=16, bold=True))

    # ── зверху: ідеальний дріт зі схеми
    y0 = 78
    f.append(text(150, y0 - 18, "на схемі", size=13, color=MUTED))
    f.append(line(70, y0, 360, y0, color=NEG, sw=2.4))
    f.append(circle(70, y0, 4, fill=NEG, stroke=NEG))
    f.append(circle(360, y0, 4, fill=NEG, stroke=NEG))
    f.append(text(215, y0 + 20, "ідеальне з'єднання: 0 Ом, 0 нГн", size=12, color=MUTED))

    # ── знизу: реальна доріжка = R послідовно з L
    y1 = 168
    f.append(text(150, y1 - 22, "на платі", size=13, color=INK, bold=True))
    f.append(circle(70, y1, 4, fill=INK, stroke=INK))
    f.append(line(70, y1, 150, y1, color=INK, sw=2))
    # резистор-зиґзаґ
    zx = [150, 162, 174, 186, 198, 210, 222, 234]
    zy = [y1, y1 - 11, y1 + 11, y1 - 11, y1 + 11, y1 - 11, y1 + 11, y1]
    pts = " ".join("%d,%d" % (x, yy) for x, yy in zip(zx, zy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, INK))
    f.append(text(192, y1 - 22, "R", size=14, bold=True, color=POS))
    f.append(line(234, y1, 270, y1, color=INK, sw=2))
    # котушка-дуги
    arcs = []
    for i in range(4):
        ax = 270 + i * 22
        arcs.append('<path d="M%d %d a11 11 0 0 1 22 0" fill="none" stroke="%s" stroke-width="2"/>' % (ax, y1, INK))
    f.append("".join(arcs))
    f.append(text(303, y1 - 20, "L", size=14, bold=True, color=NEG))
    f.append(line(358, y1, 410, y1, color=INK, sw=2))
    f.append(circle(410, y1, 4, fill=INK, stroke=INK))

    # ── права колонка: числа на 1 oz міді
    bx, by, bw, bh = 470, 70, 218, 188
    f.append(rect(bx, by, bw, bh, fill="#f0f7ff", stroke=NEG, sw=1.6))
    f.append(text(bx + bw / 2, by + 26, "мідь 1 oz ≈ 35 мкм", size=14, bold=True, color=NEG))
    rows = [
        "опір шару ≈ 0.5 мОм/□",
        "доріжка 0.25 мм × 50 мм:",
        "R ≈ 0.1 Ом",
        "індуктивність ≈ 1 нГн/мм",
        "та сама доріжка:",
        "L ≈ 50 нГн",
    ]
    for i, r in enumerate(rows):
        col = INK if i in (0, 3) else MUTED
        bold = i in (0, 3)
        f.append(text(bx + 14, by + 54 + i * 23, r, size=12.5, color=col, anchor="start", bold=bold))

    return render(os.path.join(IMG, "trace-is-rl.svg"), W, H, *f)


# ── 2. Зворотний струм тулиться під доріжкою ────────────────────────────────
def fig_return_path():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Струм завжди вертається — і на високій частоті йде прямо під доріжкою", size=15, bold=True))

    # шар землі (мідна площина) — широка смуга знизу
    gy = 250
    f.append(rect(60, gy, 600, 54, fill="#fde9b8", stroke="#c8922a", sw=1.6))
    f.append(text(355, gy + 33, "суцільний шар землі (мідь)", size=13, color="#8a6510"))

    # сигнальна доріжка зверху
    sy = 96
    f.append(rect(60, sy, 600, 16, fill=POS, stroke="#8a2418", sw=1.4, rx=4))
    f.append(text(355, sy - 12, "сигнальна доріжка (струм туди →)", size=13, color=POS))

    # вертикальні з'єднання (джерело / навантаження)
    f.append(line(78, sy + 16, 78, gy, color=INK, sw=2))
    f.append(line(642, sy + 16, 642, gy, color=INK, sw=2))
    f.append(textbox(78, 185, "джерело", size=12, fill=FILL, stroke=INK)[0])
    f.append(textbox(642, 185, "наван-\nтаження", size=12, fill=FILL, stroke=INK)[0])

    # стрілка сигналу вправо
    f.append(arrow(150, sy + 8, 560, sy + 8, color="#ffffff", sw=2.2))

    # зворотний струм у площині — тулиться ПІД доріжкою (висока частота)
    ry = gy + 14
    f.append(arrow(560, ry, 150, ry, color=POS, sw=2.6))
    f.append(text(355, ry + 22, "висока частота: зворотний струм біжить тонкою смужкою прямо під доріжкою",
                  size=12.5, color=POS, bold=True))

    # розповзання на низькій частоті — широка бліда дуга
    f.append('<path d="M150 %d C 150 %d, 660 %d, 642 %d" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="6 5"/>' % (gy + 40, gy + 80, gy + 80, gy + 40, MUTED))
    f.append(text(355, gy + 86, "низька частота: розтікається широко (шлях найменшого опору)",
                  size=12, color=MUTED))

    # підпис про петлю
    f.append(text(355, 60, "уся доріжка + зворотний шлях = петля; її площа й вирішує наводки",
                  size=12.5, color=MUTED))
    return render(os.path.join(IMG, "return-path.svg"), W, H, *f)


# ── 3. Decoupling: де поставити конденсатор — питання площі петлі ────────────
def fig_decoupling_loop():
    W, H = 720, 330
    f = []
    f.append(text(W / 2, 26, "Чим ближче конденсатор до виводу живлення — тим менша петля", size=15, bold=True))

    def chip(cx, cy):
        b, w, h = textbox(cx, cy, "мікросхема\n(різкий ривок струму)", size=12,
                          fill="#eef1f4", stroke=INK, pad=11)
        return b, w, h

    def cap(cx, cy):
        # символ конденсатора
        s = (line(cx, cy - 14, cx, cy - 3, color=INK, sw=2) +
             line(cx - 12, cy - 3, cx + 12, cy - 3, color=INK, sw=2.4) +
             line(cx - 12, cy + 3, cx + 12, cy + 3, color=INK, sw=2.4) +
             line(cx, cy + 3, cx, cy + 14, color=INK, sw=2) +
             text(cx + 22, cy + 4, "C", size=13, bold=True, color=FIELD, anchor="start"))
        return s

    # ── ліворуч: погано (далеко) — велика петля
    cbx = 175
    b, w, h = chip(cbx, 120)
    f.append(b)
    capx = cbx + 150
    f.append(cap(capx, 120))
    # шина живлення VCC (верх) і земля (низ) утворюють контур
    top = 86
    bot = 200
    f.append(line(cbx, top, capx, top, color=POS, sw=2.2))            # VCC
    f.append(line(cbx, 120 - h / 2, cbx, top, color=POS, sw=2.2))
    f.append(line(capx, 106, capx, top, color=POS, sw=2.2))
    f.append(line(cbx, bot, capx, bot, color=NEG, sw=2.2))            # GND
    f.append(line(cbx, 120 + h / 2, cbx, bot, color=NEG, sw=2.2))
    f.append(line(capx, 134, capx, bot, color=NEG, sw=2.2))
    # заштрихувати площу петлі
    f.append(rect(cbx, top, capx - cbx, bot - top, fill="rgba(192,57,43,0.10)", stroke="none", sw=0))
    f.append(text(175, 250, "далеко: велика петля →", size=13, color=POS, bold=True))
    f.append(text(175, 270, "велика індуктивність,", size=12, color=POS))
    f.append(text(175, 287, "просадка живлення", size=12, color=POS))

    # ── праворуч: добре (впритул) — крихітна петля
    dbx = 500
    b, w, h = chip(dbx, 120)
    f.append(b)
    capx2 = dbx + 70
    f.append(cap(capx2, 120))
    top2, bot2 = 102, 138
    f.append(line(dbx + w / 2, top2, capx2, top2, color=POS, sw=2.2))
    f.append(line(capx2, 106, capx2, top2, color=POS, sw=2.2))
    f.append(line(dbx + w / 2, bot2, capx2, bot2, color=NEG, sw=2.2))
    f.append(line(capx2, 134, capx2, bot2, color=NEG, sw=2.2))
    f.append(rect(dbx + w / 2, top2, capx2 - dbx - w / 2, bot2 - top2, fill="rgba(39,174,96,0.16)", stroke="none", sw=0))
    f.append(text(530, 250, "впритул: петля крихітна →", size=13, color=FIELD, bold=True))
    f.append(text(530, 270, "мала індуктивність,", size=12, color=FIELD))
    f.append(text(530, 287, "живлення тримається", size=12, color=FIELD))

    return render(os.path.join(IMG, "decoupling-loop.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trace_is_rl()
    fig_return_path()
    fig_decoupling_loop()
    print("ok: 3 figures")
