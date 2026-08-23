# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_variable_box():
    """Змінна = ім'я → комірка в пам'яті з адресою й значенням; = записує туди."""
    W, H = 720, 340
    p = []
    p.append(text(W/2, 30, "Змінна: ім'я, за яким ховається комірка пам'яті", size=17, bold=True))

    # рядок коду
    p.append(fitbox(40, 58, 300, 40, "uint8_t speed = 42;", size=17,
                    fill="#eef7ff", stroke=NEG, color=INK, bold=True))

    # ← ім'я / значення підписи під кодом
    p.append(text(90, 118, "тип", size=12, color=MUTED))
    p.append(text(200, 118, "ім'я", size=12, color=MUTED))
    p.append(text(300, 118, "значення", size=12, color=MUTED))

    # стрілка «ім'я показує на комірку»
    ax1, ay = 200, 130
    p.append(arrow(ax1, ay, 470, ay+40, color=INK, sw=2))
    p.append(text(340, 150, "показує на", size=12, color=MUTED, italic=True))

    # пам'ять — стрічка байтів
    bx, by, bw, bh = 470, 150, 60, 56
    addrs = ["0x20", "0x21", "0x22", "0x23"]
    vals = ["", "42", "", ""]
    for i in range(4):
        x = bx + i*bw
        hot = (i == 1)
        p.append(rect(x, by, bw, bh, fill=("#eafaf0" if hot else FILL),
                      stroke=(FIELD if hot else LINE), sw=(2.2 if hot else 1.4)))
        if vals[i]:
            p.append(text(x+bw/2, by+bh/2+7, vals[i], size=20, color=FIELD, bold=True))
        p.append(text(x+bw/2, by+bh+16, addrs[i], size=11, color=MUTED))
    p.append(text(bx+2*bw, by-12, "пам'ять (по одному байту в комірці)", size=12, color=MUTED))
    p.append(text(bx+bw/2, by+bh+34, "адреса комірки", size=11, color=MUTED, italic=True))

    # напис знизу
    b, bw2, bh2 = textbox(W/2, 300, "Ім'я speed — для нас; машина працює з адресою 0x21.\n«= 42» означає «поклади 42 в цю комірку», а не «speed дорівнює 42».",
                          size=13, fill="#fffef2", stroke="#caa53d")
    p.append(b)
    render(os.path.join(IMG, 'variable-box.svg'), W, H, *p)


def fig_type_families():
    """Чотири щоденні родини типів: що зберігають, який приклад, яке ключове слово."""
    W, H = 820, 380
    p = []
    p.append(text(W/2, 30, "Чотири родини типів на щодень", size=17, bold=True))

    rows = [
        ("Ціле число", "лічильники, індекси, коди",  "137,  −5,  40000", "uint8_t / int32_t", "#eafaf0", FIELD),
        ("Дробове число", "напруга, температура, кут", "3.14,  −0.5,  1e6", "float / double", "#eef7ff", NEG),
        ("Один символ", "літера, знак ASCII",        "'A',  '7',  '\\n'", "char", "#f3eefb", "#7b4fb0"),
        ("Так / ні", "прапорці, стан, умова",         "true,  false",      "bool", "#fdecea", POS),
    ]

    x0, y0 = 40, 60
    rw, rh, gap = W-80, 66, 8
    # шапка (колонки «приклад» і «тип у C» розсунуто із запасом, щоб написи не налазили)
    cols_x = [x0+14, x0+210, x0+400, x0+rw-14]
    p.append(text(cols_x[0], y0-8, "що зберігає", size=11, color=MUTED, anchor="start"))
    p.append(text(cols_x[1], y0-8, "де вживають", size=11, color=MUTED, anchor="start"))
    p.append(text(cols_x[2], y0-8, "приклад", size=11, color=MUTED, anchor="start"))
    p.append(text(cols_x[3], y0-8, "тип у C", size=11, color=MUTED, anchor="end"))

    y = y0
    for name, use, ex, kw, fill, col in rows:
        p.append(rect(x0, y, rw, rh, fill=fill, stroke=col, sw=1.8))
        p.append(text(cols_x[0], y+rh/2+6, name, size=15, color=INK, bold=True, anchor="start"))
        p.append(text(cols_x[1], y+rh/2+6, use, size=12, color=MUTED, anchor="start"))
        p.append(text(cols_x[2], y+rh/2+6, ex, size=13, color=INK, anchor="start"))
        p.append(text(cols_x[3], y+rh/2+6, kw, size=13, color=col, bold=True, anchor="end"))
        y += rh + gap

    render(os.path.join(IMG, 'type-families.svg'), W, H, *p)


def fig_history_timeline():
    """Три епохи змінної: гола адреса → ім'я+тип-за-літерою (FORTRAN) → явний тип (C)."""
    W, H = 760, 380
    p = []
    p.append(text(W/2, 30, "Три епохи змінної: від номера комірки до типу-слова", size=17, bold=True))

    cx = [140, 380, 620]           # центри трьох карток
    cy = 150
    cw, ch = 210, 150

    # ── картка 1: гола адреса ──
    p.append(rect(cx[0]-cw/2, cy-ch/2, cw, ch, fill=FILL, stroke=MUTED, sw=1.8))
    p.append(text(cx[0], cy-ch/2-10, "до мов", size=12, color=MUTED))
    p.append(text(cx[0], cy-ch/2+26, "гола адреса", size=15, color=INK, bold=True))
    p.append(fitbox(cx[0]-cw/2+14, cy-14, cw-28, 34, "клади 42\nу комірку 0x21", size=13,
                    fill="#ffffff", stroke=MUTED, color=INK))
    p.append(text(cx[0], cy+ch/2-16, "номери — руками", size=11, color=MUTED, italic=True))

    # ── картка 2: FORTRAN ──
    p.append(rect(cx[1]-cw/2, cy-ch/2, cw, ch, fill="#eef7ff", stroke=NEG, sw=1.8))
    p.append(text(cx[1], cy-ch/2-10, "FORTRAN · 1957", size=12, color=NEG, bold=True))
    p.append(text(cx[1], cy-ch/2+26, "ім'я замість номера", size=14, color=INK, bold=True))
    p.append(fitbox(cx[1]-cw/2+14, cy-14, cw-28, 34, "X = A + B * C", size=14,
                    fill="#ffffff", stroke=NEG, color=INK, bold=True))
    p.append(text(cx[1], cy+ch/2-16, "тип — за 1-ю літерою (I…N)", size=11, color=MUTED, italic=True))

    # ── картка 3: C ──
    p.append(rect(cx[2]-cw/2, cy-ch/2, cw, ch, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(cx[2], cy-ch/2-10, "C · 1972", size=12, color=FIELD, bold=True))
    p.append(text(cx[2], cy-ch/2+26, "тип оголошено словом", size=14, color=INK, bold=True))
    p.append(fitbox(cx[2]-cw/2+14, cy-14, cw-28, 34, "int speed = 42;", size=14,
                    fill="#ffffff", stroke=FIELD, color=INK, bold=True))
    p.append(text(cx[2], cy+ch/2-16, "перевірка — до запуску", size=11, color=MUTED, italic=True))

    # стрілки між картками
    p.append(arrow(cx[0]+cw/2+4, cy, cx[1]-cw/2-4, cy, color=INK, sw=2))
    p.append(arrow(cx[1]+cw/2+4, cy, cx[2]-cw/2-4, cy, color=INK, sw=2))

    # підпис-висновок знизу
    b, bw, bh = textbox(W/2, 335,
                        "Кожен щабель прибирає одну ручну роботу — і одну нагоду тихо помилитися.",
                        size=13, fill="#fffef2", stroke="#caa53d")
    p.append(b)
    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *p)


if __name__ == '__main__':
    fig_variable_box()
    fig_type_families()
    fig_history_timeline()
    print("ok")
