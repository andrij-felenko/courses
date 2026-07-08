# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def box(cx, cy, s, size=13, pad=10, fill=FILL, stroke=LINE, bold=False, min_w=0):
    """Обгортка над textbox: повертає лише SVG-фрагмент (тіло), розміри ігноруємо."""
    body, w, h = textbox(cx, cy, s, size=size, pad=pad, fill=fill, stroke=stroke,
                         bold=bold, min_w=min_w)
    return body


# ── Фігура 1: принципова (блокова) схема тракту живлення HAT ─────────────────
def fig_block():
    W, H = 860, 470
    f = []
    # ліворуч — акумулятор
    f.append(box(120, 240, ["Акумулятор", "14500 Li-ion", "3.0–4.2 В"], size=13,
                 fill="#eaf0fd", stroke=NEG, bold=False, min_w=150))
    f.append(plus(120, 188, r=9))
    f.append(minus(120, 300, r=9))

    # центр — SW6106 велика рамка
    f.append(rect(300, 90, 300, 300, fill="#fff8f0", stroke=POS, sw=2, rx=10))
    f.append(text(450, 116, "SW6106", size=16, bold=True, color=POS))
    f.append(text(450, 136, "power-bank контролер", size=11, color=MUTED))
    # три блоки всередині
    f.append(box(450, 178, ["Зарядник 3-фазний", "до 4 А · ККД ≈96%"], size=11, min_w=210))
    f.append(box(450, 242, ["Синхронний boost", "3.7 В → 5 В · до 18 Вт"], size=11, min_w=210))
    f.append(box(450, 306, ["Паливомір 12-біт", "+ контролер шляху"], size=11, min_w=210))
    f.append(box(450, 360, "Захист: OV · OC · КЗ · темп.", size=10, min_w=210,
                 fill="#fdecea", stroke=POS))

    # праворуч — виходи
    f.append(box(760, 150, ["GPIO-гребінка", "5 В → пін 2/4"], size=12, min_w=150,
                 fill="#eafaf1", stroke=FIELD))
    f.append(box(760, 240, ["USB-A", "5 В вихід"], size=12, min_w=150))
    f.append(box(760, 330, ["USB-C / micro", "заряд + вихід"], size=12, min_w=150))

    # стрілки: акумулятор ⇄ SW6106 (двобічна — заряд і розряд)
    f.append(arrow(196, 226, 300, 200, color=INK))
    f.append(arrow(300, 285, 196, 258, color=NEG))
    f.append(text(248, 205, "розряд", size=10, color=INK))
    f.append(text(248, 300, "заряд", size=10, color=NEG))

    # SW6106 → виходи
    f.append(arrow(600, 190, 685, 156, color=FIELD))
    f.append(arrow(600, 242, 685, 240, color=INK))
    # USB-C двобічний (вхід заряду / вихід)
    f.append(arrow(600, 300, 685, 322, color=INK))
    f.append(arrow(685, 344, 600, 330, color=NEG))

    render(os.path.join(OUT, 'block.svg'), W, H, *f,
           title="Тракт живлення HAT: акумулятор ⇄ SW6106 ⇄ виходи")


# ── Фігура 2: розводка пін-у-пін (гребінка HAT → 40-пінова RPi) ──────────────
def fig_pinout():
    W, H = 820, 430
    f = []
    f.append(text(W/2, 52, "Гребінка HAT сідає на всі 40 пінів; живлення йде лише по цих:",
                  size=12, color=MUTED))

    # дві колонки пінів (парні праворуч, непарні ліворуч) — фрагмент кутка гребінки
    rows = [
        ("1", "3V3", "#eee", "5", "3V3", "#eee"),  # placeholder, replaced below
    ]
    # Малюємо перші 6 фізичних пінів як приклад кутка гребінки
    # ліва колонка = непарні (1,3,5), права = парні (2,4,6)
    labels_odd = [("1", "3V3", MUTED), ("3", "GPIO2/SDA", INK), ("5", "GPIO3/SCL", INK)]
    labels_even = [("2", "5V", FIELD), ("4", "5V", FIELD), ("6", "GND", NEG)]

    x_odd, x_even = 250, 340
    y0, dy = 120, 66
    r = 15
    for i, (pn, nm, col) in enumerate(labels_odd):
        cy = y0 + i*dy
        f.append(circle(x_odd, cy, r, fill="#fff", stroke=col, sw=2.5))
        f.append(text(x_odd, cy+5, pn, size=12, bold=True, color=col))
        f.append(text(x_odd-r-12, cy+5, nm, size=12, color=col, anchor="end"))
    for i, (pn, nm, col) in enumerate(labels_even):
        cy = y0 + i*dy
        f.append(circle(x_even, cy, r, fill="#fff", stroke=col, sw=2.5))
        f.append(text(x_even, cy+5, pn, size=12, bold=True, color=col))
        f.append(text(x_even+r+12, cy+5, nm, size=12, color=col, anchor="start"))
    # рамка навколо гребінки
    f.append(rect(x_odd-r-8, y0-r-10, (x_even-x_odd)+2*r+16, 3*dy-dy+2*r+20,
                  fill="none", stroke=MUTED, sw=1.2, rx=8))
    f.append(text((x_odd+x_even)/2, y0-r-20, "40-пінова гребінка (кут)", size=11, color=MUTED))

    # праворуч — що куди йде
    f.append(box(650, 152, ["Піни 2 і 4 = +5 В", "від boost SW6106"], size=12,
                 fill="#eafaf1", stroke=FIELD, min_w=210))
    f.append(box(650, 246, ["Пін 6 (та ін. GND)", "спільна земля"], size=12,
                 fill="#eaf0fd", stroke=NEG, min_w=210))
    f.append(box(650, 340, ["Піни 3/5 = SDA/SCL", "I²C, якщо потрібен"], size=12, min_w=210))

    f.append(arrow(x_even+r+70, 154, 545, 152, color=FIELD))
    f.append(arrow(x_even+r+70, 200, 545, 246, color=NEG))
    # SDA/SCL: ведемо від правого краю рамки гребінки вниз-праворуч, повз піни
    f.append(arrow(x_even+r+70, 300, 545, 336, color=INK))

    # застереження
    f.append(box(W/2, 400, "Живлення через пін 2/4 обходить запобіжник Pi — струм ЗАХИЩАЄ лише SW6106",
                 size=11, fill="#fdecea", stroke=POS, min_w=520))

    render(os.path.join(OUT, 'pinout.svg'), W, H, *f,
           title="Розводка живлення: HAT → 40-пінова гребінка Raspberry Pi")


# ── Фігура 3: профіль заряду (3 фази) ───────────────────────────────────────
def fig_charge():
    W, H = 760, 420
    f = []
    ox, oy = 90, 330      # початок осей
    axw, axh = 600, 250
    # осі
    f.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.6))       # X
    f.append(line(ox, oy, ox, oy-axh, color=INK, sw=1.6))       # Y
    f.append(text(ox+axw, oy+24, "час", size=12, color=MUTED, anchor="end"))
    f.append(text(ox-14, oy-axh, "струм / напруга", size=11, color=MUTED, anchor="start"))

    # межі фаз
    x1, x2, x3 = ox+140, ox+380, ox+axw
    for xx in (x1, x2):
        f.append(line(xx, oy, xx, oy-axh, color=MUTED, sw=1, dash="4 4"))

    # крива напруги (росте, тоді плато)
    vpts = "M %d %d L %d %d L %d %d L %d %d" % (
        ox, oy-40, x1, oy-70, x2, oy-axh+20, x3, oy-axh+20)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (vpts, NEG))
    f.append(text(x3-6, oy-axh+8, "4.2 В", size=11, color=NEG, anchor="end"))

    # крива струму: мала (TC) → плато CC → спад CV
    ipts = "M %d %d L %d %d L %d %d L %d %d Q %d %d %d %d" % (
        ox, oy-30, x1, oy-30, x1, oy-axh+40, x2, oy-axh+40,
        (x2+x3)//2, oy-60, x3, oy-24)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (ipts, POS))
    f.append(text(x1+8, oy-axh+34, "CC ≈2.5 А (вхід 5 В)", size=11, color=POS, anchor="start"))

    # підписи фаз
    f.append(box((ox+x1)/2, oy+52, ["TC", "трикл"], size=11, min_w=90))
    f.append(box((x1+x2)/2, oy+52, ["CC", "пост. струм"], size=11, min_w=120))
    f.append(box((x2+x3)/2, oy+52, ["CV", "пост. напруга"], size=11, min_w=130))

    # легенда
    f.append(line(ox+300, 60, ox+330, 60, color=NEG, sw=2.6))
    f.append(text(ox+338, 64, "напруга акумулятора", size=11, color=INK, anchor="start"))
    f.append(line(ox+300, 84, ox+330, 84, color=POS, sw=2.6))
    f.append(text(ox+338, 88, "струм заряду", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'charge.svg'), W, H, *f,
           title="Три фази заряду Li-ion, які веде SW6106")


if __name__ == "__main__":
    fig_block()
    fig_pinout()
    fig_charge()
    print("figures written to", OUT)
