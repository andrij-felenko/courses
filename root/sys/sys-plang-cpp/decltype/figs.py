# -*- coding: utf-8 -*-
"""Фігури до теми «decltype: тип виразу разом із його категорією»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_answer():
    """Дві властивості виразу треба вмістити в один тип."""
    W, H = 1020, 560
    out = []

    b1, w1, h1 = textbox(150, 95, "c[i]", size=17, pad=16, bold=True)
    out.append(b1)

    b2, w2, h2 = textbox(505, 95, ["тип          int",
                                   "категорія    lvalue"],
                         size=15, pad=16, fill="#eef4ff", stroke=NEG)
    out.append(b2)

    b3, w3, h3 = textbox(880, 95, ["decltype(c[i])", "int&"],
                         size=16, pad=16, bold=True, fill="#eaf7ee", stroke=FIELD)
    out.append(b3)

    out.append(arrow(150 + w1 / 2 + 12, 95, 505 - w2 / 2 - 12, 95))
    out.append(arrow(505 + w2 / 2 + 12, 95, 880 - w3 / 2 - 12, 95))
    out.append(text((150 + w1 / 2 + 505 - w2 / 2) / 2, 78,
                    "що знає компілятор", size=13, color=MUTED))
    out.append(text((505 + w2 / 2 + 880 - w3 / 2) / 2, 78,
                    "закодовано в один тип", size=13, color=MUTED))

    out.append(text(W / 2, 185,
                    "категорію кодують посиланням — тим самим, чим її задають у типі повернення функції",
                    size=14, color=MUTED))

    M, GAP = 130, 6
    cols = [220, 260, 300]
    head = ["категорія виразу", "відповідь decltype",
            "так само оголосили б функцію,\nщоб її виклик дав такий вираз"]
    rows = [
        ["lvalue", "T&", "T&  f();"],
        ["xvalue", "T&&", "T&& f();"],
        ["prvalue", "T", "T   f();"],
    ]
    HH, RH = 70, 62
    y0 = 225
    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, y0, c - GAP, HH - GAP, head[i], size=14, bold=True,
                          fill="#e8edf3"))
        x += c

    y = y0 + HH
    for r in rows:
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=15,
                              bold=(i <= 1), fill=fill))
            x += cols[i]
        y += RH

    out.append(text(W / 2, y + 34,
                    "prvalue місця не має — кодувати нічого, тому тип лишається голим",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'decltype-answer.svg'), W, H, *out,
           title="Вираз має дві властивості, а віддати треба один тип")


def fig_two_rules():
    """Розвилка: ім'я чи вираз."""
    W, H = 1060, 540
    out = []

    b0, w0, h0 = textbox(W / 2, 58, "decltype( E )", size=18, pad=14, bold=True)
    out.append(b0)
    out.append(text(W / 2, 112, "int i = 0;    const int& r = i;    int&& x = 0;",
                    size=13, color=MUTED))

    bq, wq, hq = textbox(W / 2, 162, "E — це ім'я або звертання до члена, без дужок?",
                         size=15, pad=14, fill="#fff8e1", stroke="#b8860b")
    out.append(bq)
    out.append(arrow(W / 2, 58 + h0 / 2 + 4, W / 2, 162 - hq / 2 - 6))

    lx, rx, by = 265, 795, 285
    bl, wl, hl = textbox(lx, by, ["правило імені", "тип, як його оголошено;",
                                  "категорію не питають"],
                         size=15, pad=14, fill="#eef4ff", stroke=NEG)
    br, wr, hr = textbox(rx, by, ["правило виразу", "тип, доповнений категорією:",
                                  "lvalue → T&,  xvalue → T&&"],
                         size=15, pad=14, fill="#fdecea", stroke=POS)
    out.append(bl)
    out.append(br)
    out.append(arrow(W / 2 - 60, 162 + hq / 2 + 4, lx, by - hl / 2 - 8))
    out.append(arrow(W / 2 + 60, 162 + hq / 2 + 4, rx, by - hr / 2 - 8))
    out.append(text(W / 2 - 175, 218, "так", size=14, bold=True, color=NEG))
    out.append(text(W / 2 + 175, 218, "ні", size=14, bold=True, color=POS))

    ey = 415
    bel, _, hel = textbox(lx, ey, ["decltype(i)   →   int",
                                   "decltype(r)   →   const int&",
                                   "decltype(x)   →   int&&"],
                          size=15, pad=14, fill="#f7f9fb")
    ber, _, her = textbox(rx, ey, ["decltype((i))            →   int&",
                                   "decltype(i + 1)          →   int",
                                   "decltype(std::move(i))   →   int&&"],
                          size=15, pad=14, fill="#f7f9fb")
    out.append(bel)
    out.append(ber)
    out.append(arrow(lx, by + hl / 2 + 4, lx, ey - hel / 2 - 6))
    out.append(arrow(rx, by + hr / 2 + 4, rx, ey - her / 2 - 6))

    out.append(text(W / 2, 508,
                    "круглі дужки нічого не роблять зі значенням — вони лише переводять стрілку",
                    size=14, color=MUTED))

    render(os.path.join(IMG, 'decltype-two-rules.svg'), W, H, *out,
           title="Дві поведінки decltype і перемикач між ними")


def fig_unevaluated():
    """Операнд аналізують, але не обчислюють."""
    W, H = 1080, 420
    out = []

    b0, w0, h0 = textbox(W / 2, 62,
                         "decltype( std::declval<A>() + std::declval<B>() )",
                         size=17, pad=14, bold=True)
    out.append(b0)

    lx, rx, cy = 285, 800, 235
    bl, wl, hl = textbox(lx, cy, ["компілятор робить",
                                  "знаходить імена",
                                  "розв'язує перевантаження",
                                  "перевіряє доступ",
                                  "інстанціює сигнатури",
                                  "обчислює тип результату"],
                         size=15, pad=16, fill="#eef4ff", stroke=NEG)
    br, wr, hr = textbox(rx, cy, ["компілятор не робить",
                                  "не викликає функцію",
                                  "не вимагає її визначення",
                                  "не створює жодного об'єкта",
                                  "не змінює нічого: i++ не збільшує i",
                                  "не кладе в бінарник ані байта"],
                         size=15, pad=16, fill="#fdecea", stroke=POS)
    out.append(bl)
    out.append(br)
    out.append(arrow(W / 2 - 90, 62 + h0 / 2 + 4, lx, cy - hl / 2 - 8))
    out.append(arrow(W / 2 + 90, 62 + h0 / 2 + 4, rx, cy - hr / 2 - 8))

    out.append(text(W / 2, 390,
                    "тому питати тип операції можна навіть там, де виконати її нема на чому",
                    size=14, color=MUTED))

    render(os.path.join(IMG, 'decltype-unevaluated.svg'), W, H, *out,
           title="Операнд decltype аналізують, але не обчислюють")


def fig_return_order():
    """Порядок подій усередині `return std::invoke(...)`."""
    W, H = 1180, 430
    out = []

    xs = [165, 445, 730, 1010]
    y = 130
    labels = [
        ["tick_guard g{out};", "старт відліку"],
        ["std::invoke(f, a...)", "сам виклик"],
        ["ініціалізація", "об'єкта повернення"],
        ["~tick_guard()", "зупинка відліку"],
    ]
    fills = [FILL, "#eef4ff", "#eaf7ee", FILL]
    strokes = [LINE, NEG, FIELD, LINE]
    ws, hs = [], []
    for x, lab, fl, st in zip(xs, labels, fills, strokes):
        b, w, h = textbox(x, y, lab, size=15, pad=14, fill=fl, stroke=st)
        out.append(b)
        ws.append(w)
        hs.append(h)

    for i in range(3):
        out.append(arrow(xs[i] + ws[i] / 2 + 10, y,
                         xs[i + 1] - ws[i + 1] / 2 - 10, y))

    span_y = 262
    for i in (0, 3):
        out.append(line(xs[i], y + hs[i] / 2 + 6, xs[i], span_y - 8,
                        color=MUTED, sw=1.2, dash="5,5"))
    out.append(arrow(xs[0], span_y, xs[3], span_y, color=MUTED))
    out.append(arrow(xs[3], span_y, xs[0], span_y, color=MUTED))

    mid = (xs[0] + xs[3]) / 2
    out.append(text(mid, span_y + 34, "що потрапляє у вимір", size=15, bold=True))
    out.append(text(mid, span_y + 62,
                    "разом із побудовою результату: локальні змінні гинуть уже після неї",
                    size=14, color=MUTED))

    render(os.path.join(IMG, 'decltype-return-order.svg'), W, H, *out,
           title="Деструктор охоронця спрацьовує після ініціалізації об'єкта повернення")


fig_answer()
fig_two_rules()
fig_unevaluated()
fig_return_order()
print("ok")
