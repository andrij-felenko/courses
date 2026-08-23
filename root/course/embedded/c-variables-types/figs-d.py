# -*- coding: utf-8 -*-
# Фігури ДЕТАЛЬНОЇ статті «Змінні й типи». Окремий файл, щоб не чіпати базовий figs.py.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_struct_padding():
    """Розкладка struct sensor: де набивка й чому sizeof = 12, а не 7."""
    W, H = 760, 370
    p = []
    p.append(text(W/2, 30, "Прокладка у структурі: чому sizeof = 12, а не 7", size=17, bold=True))

    # стрічка з 12 байтів
    bx, by = 70, 120
    cw, ch = 52, 48
    # тип кожного байта: 0=id,1..3=pad,4..7=value,8..9=flags,10..11=pad
    kinds = ['id', 'pad', 'pad', 'pad', 'v', 'v', 'v', 'v', 'f', 'f', 'pad', 'pad']
    col = {'id': ("#eafaf0", FIELD), 'v': ("#eef7ff", NEG),
           'f': ("#f3eefb", "#7b4fb0"), 'pad': ("#f0f0f0", MUTED)}
    lbl = {'id': "id", 'v': "value", 'f': "flags", 'pad': "•"}
    for i in range(12):
        x = bx + i*cw
        fill, stroke = col[kinds[i]]
        dashed = (kinds[i] == 'pad')
        p.append(rect(x, by, cw, ch, fill=fill, stroke=stroke, sw=1.8))
        if dashed:
            p.append(text(x+cw/2, by+ch/2+6, "×", size=18, color=MUTED, bold=True))
        else:
            p.append(text(x+cw/2, by+ch/2+6, lbl[kinds[i]], size=13, color=INK, bold=True))
        # адреса-зсув під коміркою
        p.append(text(x+cw/2, by+ch+16, str(i), size=11, color=MUTED))
    p.append(text(bx+6*cw, by-14, "зсув байта в структурі", size=12, color=MUTED))

    # дужки-підписи полів згори
    def brace_label(i0, i1, txt, color):
        x0 = bx + i0*cw
        x1 = bx + (i1+1)*cw
        ytop = by - 6
        p.append(line(x0+4, ytop, x1-4, ytop, color=color, sw=2))
        p.append(line(x0+4, ytop, x0+4, ytop+8, color=color, sw=2))
        p.append(line(x1-4, ytop, x1-4, ytop+8, color=color, sw=2))
    # (дужки прибрано над рядком, щоб не накладалися на підпис зсуву — підписи полів у самих клітинах)

    # пояснення двох ділянок набивки — окремими рамками ПІД стрічкою, не над лініями
    b1, w1, h1 = textbox(bx + 2*cw, by+ch+66,
                         "3 байти набивки:\nщоб value стало на зсув 4",
                         size=12, fill="#fbfbfb", stroke=MUTED)
    p.append(b1)
    b2, w2, h2 = textbox(bx + 10*cw, by+ch+66,
                         "2 байти в кінці:\nщоб масив зберіг межу",
                         size=12, fill="#fbfbfb", stroke=MUTED)
    p.append(b2)

    # висновок унизу
    b, bw, bh = textbox(W/2, H-24,
                        "7 корисних байтів, але sizeof = 12: п'ять байтів набивки (×) — заради вирівнювання.",
                        size=13, fill="#fffef2", stroke="#caa53d")
    p.append(b)
    render(os.path.join(IMG, 'struct-padding.svg'), W, H, *p)


def fig_wrap_and_dual():
    """Ліворуч: обгортання 255+1→0 (дев'ятий біт відкинуто).
       Праворуч: ті самі біти 11111111 — 255 як uint8, −1 як int8."""
    W, H = 800, 380
    p = []
    p.append(text(W/2, 30, "Ті самі біти: обгортання й подвійне читання", size=17, bold=True))

    # ── ЛІВА половина: додавання з переносом ──
    lx = 60
    p.append(text(lx+130, 66, "uint8_t: 255 + 1", size=14, bold=True, color=NEG))
    rows = [
        ("11111111", "255", INK, 8),
        ("00000001", "+  1", INK, 8),
    ]
    yb = 92
    for i, (bits, dec, color, nb) in enumerate(rows):
        y = yb + i*34
        p.append(text(lx, y, bits, size=18, color=color, anchor="start"))
        p.append(text(lx+210, y, dec, size=13, color=MUTED, anchor="start"))
    p.append(line(lx-4, yb+2*34-14, lx+195, yb+2*34-14, color=INK, sw=1.6))
    # результат 9 біт
    p.append(text(lx, yb+2*34+8, "100000000", size=18, color=POS, anchor="start"))
    p.append(text(lx+210, yb+2*34+8, "256, 9 біт", size=13, color=MUTED, anchor="start"))
    # відкинутий біт
    p.append(circle(lx+9, yb+2*34, 13, fill="none", stroke=POS, sw=2.2))
    p.append(text(lx+40, yb+2*34+44, "↑ дев'ятий біт нема куди діти → відкинуто", size=12, color=POS, anchor="start"))
    p.append(text(lx, yb+2*34+72, "лишилось 00000000 = 0", size=14, color=INK, bold=True, anchor="start"))

    # роздільник
    p.append(line(W/2, 58, W/2, H-70, color=MUTED, sw=1.2, dash="4 4"))

    # ── ПРАВА половина: подвійне читання одного візерунка ──
    rx = W/2 + 40
    p.append(text(rx+150, 66, "той самий байт 11111111", size=14, bold=True, color=INK))
    # великий візерунок
    p.append(fitbox(rx, 82, 300, 40, "1 1 1 1 1 1 1 1", size=20, fill="#f7f7f7", stroke=INK, color=INK, bold=True))

    # дві стрілки на два прочитання
    p.append(text(rx+40, 150, "як uint8_t", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx+40, 172, "усі ваги +:", size=11, color=MUTED, anchor="start"))
    p.append(text(rx+40, 194, "128+64+…+1 = 255", size=14, color=FIELD, anchor="start"))

    p.append(text(rx+40, 240, "як int8_t", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(rx+40, 262, "старший біт має вагу −128:", size=11, color=MUTED, anchor="start"))
    p.append(text(rx+40, 284, "−128 + 127 = −1", size=14, color=POS, anchor="start"))

    # висновок унизу на всю ширину
    b, bw, bh = textbox(W/2, H-30,
                        "Зайвий біт відкидається — це обгортання. Знаковість не міняє біти, лише вагу старшого біта.",
                        size=13, fill="#fffef2", stroke="#caa53d")
    p.append(b)
    render(os.path.join(IMG, 'wrap-and-dual.svg'), W, H, *p)


if __name__ == '__main__':
    fig_struct_padding()
    fig_wrap_and_dual()
    print("ok")
