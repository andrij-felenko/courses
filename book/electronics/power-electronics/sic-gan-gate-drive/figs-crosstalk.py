# -*- coding: utf-8 -*-
"""Фігури для вставки math-crosstalk-margin: капацитивний дільник, важелі запасу, SiC vs GaN."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def crosstalk_divider():
    """Струм наведення розгалужується: частина в Cgs, частина крізь Rg у драйвер.
    Показуємо два кінці: статичний ліміт (усе в Cgs) і динамічний (усе крізь R)."""
    W, H = 760, 470
    frags = []
    frags.append(text(W / 2, 30, "Наведений струм і два його шляхи в затворі", size=17, bold=True))

    # Вузол-стік угорі (він валиться з dV/dt) -> через Cgd -> вузол затвора G
    dx = 380          # вісь x стоку/Cgd/затвора
    drain_y = 78
    gate_y = 220
    src_y = 340

    # СТІК: символ швидкого перепаду
    frags.append(text(dx, drain_y - 24, "стік сусіда: dV/dt", size=13, bold=True, color=POS))
    frags.append(line(dx, drain_y - 14, dx, drain_y, color=POS, sw=2.4))
    frags.append(circle(dx, drain_y, 4, fill=POS, stroke=POS))

    # Cgd між стоком і затвором
    def cap(cx, cy, label, col=INK):
        f = []
        f.append(line(cx, cy - 16, cx, cy - 5, color=col, sw=2.2))
        f.append(line(cx - 16, cy - 5, cx + 16, cy - 5, color=col, sw=2.6))
        f.append(line(cx - 16, cy + 5, cx + 16, cy + 5, color=col, sw=2.6))
        f.append(line(cx, cy + 5, cx, cy + 16, color=col, sw=2.2))
        f.append(text(cx + 22, cy + 4, label, size=13, bold=True, color=col, anchor="start"))
        return f

    # Cgd (стік -> затвор): несе наведений струм I = Cgd·dV/dt
    cgd_y = (drain_y + gate_y) / 2
    frags.append(line(dx, drain_y, dx, cgd_y - 16, color=POS, sw=2.2))
    frags += cap(dx, cgd_y, "Cgd", col=POS)
    frags.append(line(dx, cgd_y + 16, dx, gate_y, color=POS, sw=2.2))
    frags.append(text(dx - 150, cgd_y + 5, "I = Cgd·dV/dt", size=13, bold=True, color=POS, anchor="start"))

    # Вузол затвора G
    frags.append(circle(dx, gate_y, 5, fill=INK, stroke=INK))
    frags.append(text(dx + 14, gate_y - 8, "затвор G", size=13, bold=True, anchor="start"))
    frags.append(text(dx + 14, gate_y + 12, "Vgs(хибна)", size=12, color=INK, anchor="start"))

    # Шлях 1: униз крізь Cgs до витоку (статичний, високочастотний дільник)
    frags.append(line(dx, gate_y, dx, (gate_y + src_y) / 2 - 16, color=NEG, sw=2.2))
    frags += cap(dx, (gate_y + src_y) / 2, "Cgs", col=NEG)
    frags.append(line(dx, (gate_y + src_y) / 2 + 16, dx, src_y, color=NEG, sw=2.2))
    frags.append(line(dx - 40, src_y, dx + 40, src_y, color=INK, sw=2.6))
    frags.append(text(dx, src_y + 18, "витік S", size=12, color=MUTED))

    # Шлях 2: ліворуч крізь Rg у драйвер (на Voff)
    drv_x = 120
    # резистор Rg як прямокутник; лінію ведемо ДВОМА відрізками, що впираються в його краї (не крізь напис)
    rgx = (dx + drv_x + 70) / 2
    rgw = 66
    frags.append(line(dx, gate_y, rgx + rgw / 2, gate_y, color=FIELD, sw=2.2))          # справа від R до затвора
    frags.append(line(rgx - rgw / 2, gate_y, drv_x + 70, gate_y, color=FIELD, sw=2.2))  # зліва від R до драйвера
    frags.append(rect(rgx - rgw / 2, gate_y - 12, rgw, 24, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    frags.append(text(rgx, gate_y + 5, "R = Roff+Rg", size=11, bold=True, color=FIELD))
    # драйвер-джерело Voff
    frags.append(rect(drv_x - 4, gate_y - 26, 74, 52, fill=FILL, stroke=INK, sw=1.6, rx=6))
    frags.append(text(drv_x + 33, gate_y - 6, "драйвер", size=12, bold=True))
    frags.append(text(drv_x + 33, gate_y + 14, "тримає Voff", size=11, color=NEG))

    # Дві межі-підписи
    b1, w1, h1 = textbox(200, 400, ["Ємнісна межа (R→0):", "поділ заряду в Cgs",
                                    "Vgs = ΔVds·Cgd/(Cgd+Cgs)"],
                         size=11, pad=8, fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b1)
    b2, w2, h2 = textbox(560, 400, ["Резистивна межа (R помітний):", "спад на опорі",
                                    "Vgs = Cgd·(dV/dt)·R"],
                         size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD)
    frags.append(b2)

    render(os.path.join(IMG, 'crosstalk-divider.svg'), W, H, *frags)


def margin_levers():
    """Стовпчикова: хибна напруга Vgs проти порога; три важелі опускають стартову точку /
    зменшують спайк, збільшуючи запас. Осі — напруга В."""
    W, H = 780, 470
    frags = []
    frags.append(text(W / 2, 30, "Запас проти хибного відмикання: чотири колонки", size=17, bold=True))

    # Вертикальна шкала напруги −6..+8 В
    vmin, vmax = -6.0, 8.0
    top, bot = 70.0, 380.0

    def yv(v):
        return bot - (v - vmin) / (vmax - vmin) * (bot - top)

    axx = 60
    frags.append(line(axx, top - 6, axx, bot + 6, color=INK, sw=1.5))
    for v in (-6, -4, -2, 0, 2, 4, 6, 8):
        y = yv(v)
        frags.append(line(axx - 4, y, axx + 4, y, color=INK, sw=1.2))
        frags.append(text(axx - 9, y + 4, ("%+d" % v) if v else "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(axx - 9, top - 14, "В", size=12, color=MUTED, anchor="end"))
    # нуль
    frags.append(line(axx, yv(0), W - 24, yv(0), color=MUTED, sw=1.0, dash="4 4"))
    # ПОРІГ Vth = 2.5 В — червона межа через усю картину
    frags.append(line(axx, yv(2.5), W - 24, yv(2.5), color=POS, sw=1.8, dash="6 4"))
    frags.append(text(W - 26, yv(2.5) - 6, "поріг Vth = 2.5 В", size=12, bold=True, color=POS, anchor="end"))

    # чотири колонки: (назва, старт Voff, спайк ΔV)
    cols = [
        ("база\n0 В, R=3 Ω", 130, 0.0, 4.5),
        ("−4 В\nзсув", 300, -4.0, 4.5),
        ("менший R\n−4 В, R=1.5", 470, -4.0, 2.25),
        ("+коротка\nпетля", 640, -4.0, 1.6),
    ]
    barw = 96
    for name, cx, voff, spike in cols:
        top_v = voff + spike       # куди злітає затвор
        x = cx - barw / 2
        y_top = yv(top_v)
        y_base = yv(voff)
        # стовпчик від Voff до піку
        col_fill = "#fdecea" if top_v > 2.5 else "#eafaf0"
        col_stroke = POS if top_v > 2.5 else FIELD
        frags.append(rect(x, min(y_top, y_base), barw, abs(y_base - y_top),
                          fill=col_fill, stroke=col_stroke, sw=1.6, rx=4))
        # стартова точка Voff (синя риска)
        frags.append(line(x - 4, y_base, x + barw + 4, y_base, color=NEG, sw=2.6))
        frags.append(text(cx, y_base + 16, "старт %+g" % voff, size=10, color=NEG))
        # пік (верх стовпчика)
        frags.append(text(cx, y_top - 7, "%+g В" % top_v, size=12, bold=True, color=col_stroke))
        # назва колонки під віссю
        lines = name.split("\n")
        for i, ln in enumerate(lines):
            frags.append(text(cx, bot + 34 + i * 15, ln, size=11, color=INK))

    render(os.path.join(IMG, 'margin-levers.svg'), W, H, *frags)


def sic_vs_gan():
    """Дві шкали поруч: у SiC запас будують ВНИЗ (−Voff), у GaN — тиснуть УГОРУ (обмежити спайк),
    бо стеля впритул. Показати, куди «тікати» кожному."""
    W, H = 780, 480
    frags = []
    frags.append(text(W / 2, 30, "Куди тікати за запасом: SiC вниз, GaN — нікуди вгору", size=16, bold=True))

    vmin, vmax = -6.0, 9.0
    top, bot = 70.0, 400.0

    def yv(v):
        return bot - (v - vmin) / (vmax - vmin) * (bot - top)

    def scale(ox, name, vth, vmax_abs, voff, spike, note, note_col):
        f = []
        axx = ox + 46
        f.append(line(axx, top - 6, axx, bot + 6, color=INK, sw=1.4))
        for v in range(-6, 10, 2):
            y = yv(v)
            f.append(line(axx - 3, y, axx + 3, y, color=INK, sw=1.0))
            f.append(text(axx - 7, y + 4, ("%+d" % v) if v else "0", size=10, color=MUTED, anchor="end"))
        f.append(text(ox + 155, top - 30, name, size=15, bold=True))

        barx, barw = axx + 30, 120
        # нуль — тягнемо лише до правого краю стовпчика, щоб не різати підпис OFF на нулі (GaN: Voff=0)
        f.append(line(axx, yv(0), barx + barw, yv(0), color=MUTED, sw=0.9, dash="3 3"))
        # абсолютний максимум згори — червона стеля (тільки якщо в межах шкали)
        if vmax_abs <= vmax:
            f.append(line(barx, yv(vmax_abs), barx + barw, yv(vmax_abs), color=POS, sw=2.4))
            f.append(text(barx + barw + 4, yv(vmax_abs) + 4, "абс.макс %+g" % vmax_abs, size=10, color=POS, anchor="start"))
        # поріг Vth — головна межа хибного відмикання
        f.append(line(barx, yv(vth), barx + barw, yv(vth), color=INK, sw=1.6, dash="3 3"))
        f.append(text(barx + 4, yv(vth) - 5, "поріг %g" % vth, size=10, anchor="start"))
        # старт Voff
        f.append(line(barx, yv(voff), barx + barw, yv(voff), color=NEG, sw=2.4))
        f.append(text(barx + barw + 4, yv(voff) + 4, "OFF %+g" % voff, size=10, color=NEG, anchor="start"))
        # спайк від Voff угору (стрілка)
        peak = voff + spike
        f.append(arrow(barx + barw / 2, yv(voff), barx + barw / 2, yv(peak), color=MUTED, sw=2.0))
        f.append(text(barx + barw / 2 + 8, (yv(voff) + yv(peak)) / 2 + 4, "спайк", size=10, color=MUTED, anchor="start"))
        # пік
        pcol = POS if peak > vth else FIELD
        f.append(circle(barx + barw / 2, yv(peak), 4, fill=pcol, stroke=pcol))
        f.append(text(barx + barw / 2 - 6, yv(peak) - 7, "пік %+g" % peak, size=11, bold=True, color=pcol, anchor="end"))
        # нотатка знизу
        box, bw, bh = textbox(ox + 155, bot + 56, note, size=11, pad=8,
                              fill="#f4f6f8", stroke=note_col, color=note_col)
        f.append(box)
        return f

    # SiC: старт −4 В, той самий спайк 4.5 → пік +0.5 < поріг 2.5. Стеля −10..+25 поза шкалою згори.
    frags += scale(20, "SiC: старт −4 В", 2.5, 99.0, -4.0, 4.5,
                   ["запас будують ВНИЗ:", "старт −4 → пік +0.5", "нижче порога 2.5 → тримається"], NEG)
    frags.append(line(W / 2, 60, W / 2, H - 20, color=MUTED, sw=1.0, dash="5 5"))
    # GaN: старт 0 В, той самий спайк 4.5 → пік +4.5 > поріг 1.5; стеля +7 впритул.
    frags += scale(400, "GaN: старт 0 В", 1.5, 7.0, 0.0, 4.5,
                   ["вниз тікати мало, вгору —", "стеля +7 впритул до ON+6;", "лишається тиснути спайк"], POS)

    render(os.path.join(IMG, 'sic-vs-gan-margin.svg'), W, H, *frags)


if __name__ == '__main__':
    crosstalk_divider()
    margin_levers()
    sic_vs_gan()
    print("done")
