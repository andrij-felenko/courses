# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def gate_windows():
    """Три вертикальні смуги напруги затвора: Si, SiC, GaN — у спільному масштабі."""
    W, H = 760, 500
    # Спільна вертикальна шкала напруги: від -12 В (низ) до +28 В (верх)
    vmin, vmax = -12.0, 28.0
    top, bot = 70.0, 410.0

    def yv(v):
        return bot - (v - vmin) / (vmax - vmin) * (bot - top)

    frags = []
    frags.append(text(W / 2, 34, "Вікно напруги затвора — у спільному масштабі", size=17, bold=True))

    # Вісь напруги зліва з поділками
    axx = 66
    frags.append(line(axx, top - 6, axx, bot + 6, color=INK, sw=1.5))
    for v in (-10, -5, 0, 5, 10, 15, 20, 25):
        y = yv(v)
        frags.append(line(axx - 4, y, axx + 4, y, color=INK, sw=1.2))
        frags.append(text(axx - 9, y + 4, ("%+d" % v) if v else "0", size=11, color=MUTED, anchor="end"))
    frags.append(text(axx - 9, top - 14, "В", size=12, color=MUTED, anchor="end"))
    # лінія нуля через усю картину
    frags.append(line(axx, yv(0), W - 24, yv(0), color=MUTED, sw=1.0, dash="4 4"))

    cols = [
        ("Si (кремній)", 175, 3.0, 10.0, 20.0, -20.0),   # назва, cx, поріг, відкр, макс+, макс-
        ("SiC", 405, 3.0, 15.0, 25.0, -10.0),
        ("GaN (e-mode)", 620, 1.5, 6.0, 7.0, -4.0),
    ]
    barw = 118

    for name, cx, vth, von, vmaxp, vmaxn in cols:
        x = cx - barw / 2
        # Смуга «дозволеної» роботи: від макс- до макс+ (світла)
        y_hi, y_lo = yv(vmaxp), yv(vmaxn)
        frags.append(rect(x, y_hi, barw, y_lo - y_hi, fill="#eef2f6", stroke=MUTED, sw=1.2, rx=5))
        # Заголовок стовпця
        frags.append(text(cx, top - 26, name, size=14, bold=True))

        # Небезпечна зона згори (над макс+): червона штриховка-заливка
        frags.append(rect(x, yv(vmaxp), barw, 10, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
        frags.append(text(cx, yv(vmaxp) - 6, "абс. макс", size=10, color=POS))

        # Робоча точка «відкрито» (зелена лінія)
        yo = yv(von)
        frags.append(line(x + 4, yo, x + barw - 4, yo, color=FIELD, sw=3))
        frags.append(text(x + barw + 6, yo + 4, "ON %+g" % von, size=11, color=FIELD, anchor="start"))

        # Поріг (сіра пунктирна)
        yt = yv(vth)
        frags.append(line(x + 4, yt, x + barw - 4, yt, color=INK, sw=1.4, dash="3 3"))
        frags.append(text(x + 6, yt - 5, "поріг %g" % vth, size=10, color=INK, anchor="start"))

        # Точка вимкнення (синя лінія) якщо від'ємна/нуль різниться
        yf = yv(vmaxn if False else (vmaxn))
        # Для SiC/GaN показати рекомендоване вимкнення (не абс.макс): SiC -4, GaN 0
        voff = {"SiC": -4.0, "GaN (e-mode)": 0.0, "Si (кремній)": 0.0}[name]
        yoff = yv(voff)
        frags.append(line(x + 4, yoff, x + barw - 4, yoff, color=NEG, sw=2.4))
        frags.append(text(x + barw + 6, yoff + 4, "OFF %+g" % voff, size=11, color=NEG, anchor="start"))

    # Підпис-акцент про GaN щілину — унизу під колонкою GaN, з достатнім відступом
    box, bw, bh = textbox(620, 470, "GaN: щілина ON↔пробій ≈ 1 В", size=11, pad=7,
                          fill="#fdecea", stroke=POS, color=POS)
    frags.append(box)

    render(os.path.join(IMG, 'gate-windows.svg'), W, H, *frags)


def kelvin_source():
    """Ліворуч 3-pin зі спільною Ls у петлі затвора; праворуч 4-pin із ніжкою Кельвіна."""
    W, H = 780, 470
    frags = []
    frags.append(text(W / 2, 30, "Спільна індуктивність витоку та ніжка Кельвіна", size=17, bold=True))

    def half(ox, kelvin):
        f = []
        # Транзистор — прямокутник-кристал
        tx, ty, tw, th = ox + 120, 90, 92, 120
        f.append(rect(tx, ty, tw, th, fill="#eef2f6", stroke=INK, sw=1.6, rx=8))
        f.append(text(tx + tw / 2, ty + th / 2 - 6, "SiC/GaN", size=13, bold=True))
        f.append(text(tx + tw / 2, ty + th / 2 + 14, "ключ", size=12, color=MUTED))
        gate_y = ty + 34
        drain_y = ty
        src_y = ty + th

        # Стік угору
        f.append(line(tx + tw / 2, drain_y, tx + tw / 2, drain_y - 34, color=INK, sw=2.2))
        f.append(text(tx + tw / 2 + 8, drain_y - 24, "стік (силовий струм Id)", size=11, color=INK, anchor="start"))

        # Драйвер зліва
        dxr = ox + 24
        dw, dh = 66, 46
        f.append(rect(dxr, gate_y - dh / 2, dw, dh, fill=FILL, stroke=INK, sw=1.5, rx=6))
        f.append(text(dxr + dw / 2, gate_y + 4, "драйвер", size=12, bold=True))
        # Затвор: драйвер -> затвор
        f.append(line(dxr + dw, gate_y, tx, gate_y, color=INK, sw=2.0))
        f.append(text((dxr + dw + tx) / 2, gate_y - 8, "затвор", size=11, color=INK))

        # Витік униз до спільного вузла
        node_y = src_y + 46
        f.append(line(tx + tw / 2, src_y, tx + tw / 2, node_y, color=INK, sw=2.4))

        # Індуктивність витоку Ls на силовому виводі (зигзаг-котушка як прямокутник-мітка)
        ls_y1, ls_y2 = node_y, node_y + 40
        f.append(rect(tx + tw / 2 - 16, ls_y1, 32, 34, fill="#fff6e6", stroke=POS, sw=1.5, rx=4))
        f.append(text(tx + tw / 2, ls_y1 + 22, "Ls", size=13, bold=True, color=POS))
        f.append(line(tx + tw / 2, ls_y1 + 34, tx + tw / 2, ls_y2 + 20, color=INK, sw=2.4))
        f.append(text(tx + tw / 2, ls_y2 + 40, "земля (силова)", size=11, color=MUTED))

        # Повернення струму затвора
        drv_ret_y = gate_y + dh / 2
        if not kelvin:
            # 3-pin: повернення затвора йде через ТОЙ САМИЙ вузол над Ls (спільна індуктивність)
            f.append(line(dxr + dw / 2, drv_ret_y, dxr + dw / 2, node_y, color=NEG, sw=2.0))
            f.append(line(dxr + dw / 2, node_y, tx + tw / 2, node_y, color=NEG, sw=2.0))
            f.append(circle(tx + tw / 2, node_y, 3.5, fill=NEG, stroke=NEG))
            lbl, bw, bh = textbox(ox + 155, ls_y2 + 82, ["петля затвора ділить Ls", "→ dId/dt гальмує ON"],
                                  size=11, pad=8, fill="#fdecea", stroke=POS, color=POS)
            f.append(lbl)
            f.append(text(ox + 175, 62, "3 виводи: спільний витік", size=13, bold=True, color=POS))
        else:
            # 4-pin: окрема ніжка Кельвіна прямо до кристала витоку (вище Ls)
            kel_x = tx + tw / 2
            kel_join_y = src_y + 22   # точка на витоку ДО Ls
            f.append(line(dxr + dw / 2, drv_ret_y, dxr + dw / 2, kel_join_y, color=FIELD, sw=2.2))
            f.append(line(dxr + dw / 2, kel_join_y, kel_x, kel_join_y, color=FIELD, sw=2.2))
            f.append(circle(kel_x, kel_join_y, 3.5, fill=FIELD, stroke=FIELD))
            f.append(text(dxr + dw / 2 - 4, kel_join_y - 8, "Кельвін", size=11, color=FIELD, anchor="start", bold=True))
            lbl, bw, bh = textbox(ox + 155, ls_y2 + 82, ["петля затвора повз Ls", "→ ON на повну швидкість"],
                                  size=11, pad=8, fill="#eafaf0", stroke=FIELD, color=FIELD)
            f.append(lbl)
            f.append(text(ox + 175, 62, "4 виводи: ніжка Кельвіна", size=13, bold=True, color=FIELD))
        return f

    frags += half(20, kelvin=False)
    # роздільник
    frags.append(line(W / 2, 52, W / 2, H - 20, color=MUTED, sw=1.0, dash="5 5"))
    frags += half(400, kelvin=True)

    render(os.path.join(IMG, 'kelvin-source.svg'), W, H, *frags)


def wbg_timeline():
    """Дві доріжки напруги затвора в часі: SiC осідає +20→+18→+15/−4; GaN застигає на +6."""
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 30, "Два шляхи напруги затвора, 2010 → сер. 2010-х", size=17, bold=True))

    # Часова вісь ліворуч→праворуч
    x0, x1 = 90.0, W - 40.0
    tmin, tmax = 2010.0, 2016.0

    def xt(t):
        return x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)

    # Спільна вертикальна шкала напруги для обох доріжок (щоб порівняння чесне)
    vmin, vmax = -8.0, 26.0
    # Смуга SiC — верхня половина, смуга GaN — нижня; кожна зі своєю базовою лінією
    sic_top, sic_bot = 70.0, 245.0
    gan_top, gan_bot = 260.0, 420.0

    def y_sic(v):
        return sic_bot - (v - vmin) / (vmax - vmin) * (sic_bot - sic_top)

    def y_gan(v):
        return gan_bot - (v - vmin) / (vmax - vmin) * (gan_bot - gan_top)

    # Роки на осі часу (унизу)
    for t in range(2010, 2017, 2):
        xx = xt(t)
        frags.append(line(xx, gan_bot + 4, xx, gan_bot + 10, color=MUTED, sw=1.0))
        frags.append(text(xx, gan_bot + 24, str(t), size=11, color=MUTED))

    # ── Смуга SiC ──
    frags.append(text(x0 - 4, sic_top - 14, "SiC — осідає й додає від'ємне", size=13, bold=True, anchor="start"))
    frags.append(line(x0 - 20, y_sic(0), x1, y_sic(0), color=MUTED, sw=1.0, dash="4 4"))
    frags.append(text(x0 - 24, y_sic(0) + 4, "0", size=10, color=MUTED, anchor="end"))
    # Лінія ON: східчастий спад 20 → 18 → 15
    sic_on = [(2011.05, 20.0, "CMF20120D"), (2013.0, 18.0, "+18"), (2015.0, 15.0, "+15")]
    prev = None
    for t, v, _ in sic_on:
        pt = (xt(t), y_sic(v))
        if prev:
            frags.append(line(prev[0], prev[1], pt[0], prev[1], color=POS, sw=3))
            frags.append(line(pt[0], prev[1], pt[0], pt[1], color=POS, sw=3))
        prev = pt
    frags.append(line(prev[0], prev[1], x1, prev[1], color=POS, sw=3))
    for t, v, lbl in sic_on:
        frags.append(circle(xt(t), y_sic(v), 4, fill="#fdecea", stroke=POS, sw=2))
        frags.append(text(xt(t), y_sic(v) - 9, ("+%g" % v), size=11, color=POS, bold=True))
    frags.append(text(x1, y_sic(15) + 4, "ON", size=11, color=POS, anchor="start"))
    # Лінія OFF: 0 → −4 (з'являється від'ємне зміщення)
    frags.append(line(xt(2011.05), y_sic(0), xt(2014.0), y_sic(0), color=NEG, sw=2.4))
    frags.append(line(xt(2014.0), y_sic(0), xt(2014.0), y_sic(-4), color=NEG, sw=2.4))
    frags.append(line(xt(2014.0), y_sic(-4), x1, y_sic(-4), color=NEG, sw=2.4))
    frags.append(circle(xt(2014.0), y_sic(-4), 4, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(x1, y_sic(-4) + 4, "OFF −4", size=11, color=NEG, anchor="start"))

    # ── Смуга GaN ──
    frags.append(text(x0 - 4, gan_top - 14, "GaN — застигає біля стелі", size=13, bold=True, anchor="start"))
    frags.append(line(x0 - 20, y_gan(0), x1, y_gan(0), color=MUTED, sw=1.0, dash="4 4"))
    frags.append(text(x0 - 24, y_gan(0) + 4, "0", size=10, color=MUTED, anchor="end"))
    # Абсолютна стеля +7 — червона межа над робочою точкою
    frags.append(line(xt(2010.2), y_gan(7), x1, y_gan(7), color=POS, sw=1.6, dash="5 4"))
    frags.append(text(x1, y_gan(7) - 5, "абс. макс +6…+7", size=10, color=POS, anchor="end"))
    # Лінія ON: рівна на +6 від самого початку (EPC1001 2010)
    frags.append(line(xt(2010.2), y_gan(6), x1, y_gan(6), color=FIELD, sw=3))
    frags.append(circle(xt(2010.2), y_gan(6), 4, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(xt(2010.2), y_gan(6) - 9, "EPC1001", size=11, color=FIELD, bold=True))
    frags.append(circle(xt(2014.0), y_gan(6), 4, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(xt(2014.0), y_gan(6) + 16, "GaN Systems", size=10, color=FIELD))
    frags.append(text(x1, y_gan(6) + 4, "ON +6", size=11, color=FIELD, anchor="start"))
    # Підпис-акцент: щілина ON↔стеля
    box, bw, bh = textbox(xt(2012.0), y_gan(-4), "щілина ON↔стеля ≈ 1 В", size=11, pad=7,
                          fill="#fdecea", stroke=POS, color=POS)
    frags.append(box)

    render(os.path.join(IMG, 'wbg-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    gate_windows()
    kelvin_source()
    wbg_timeline()
    print("done")
