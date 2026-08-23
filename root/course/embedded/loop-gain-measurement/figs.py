# -*- coding: utf-8 -*-
"""Фігури до кроку «Вимірювання петлевого підсилення» (root/course/embedded/zhyvlennia)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_why_not_open():
    """Чому не можна просто розірвати петлю: DC-зміщення завалюється."""
    W, H = 760, 360
    f = []
    # дві панелі
    colL, colR = 30, 400
    pw = 330
    # ── ліва: розірвана петля ──
    f.append(fitbox(colL, 44, pw, 26, "Розірвати петлю фізично", size=14, bold=True,
                    fill="#fdecea", stroke=POS))
    bx, by, bw, bh = colL + 90, 92, 150, 60
    f.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE))
    f.append(text(bx + bw / 2, by + bh / 2 + 5, "регулятор", size=13))
    # вхід (опорна) і обірваний зворотний
    f.append(text(colL + 40, by + bh / 2 + 5, "опора", size=12, color=MUTED))
    f.append(arrow(colL + 70, by + bh / 2, bx, by + bh / 2, color=LINE))
    # вихід вниз і назад, але розрив
    f.append(arrow(bx + bw, by + bh / 2, bx + bw + 40, by + bh / 2, color=LINE))
    f.append(text(bx + bw + 60, by + bh / 2 + 5, "вихід", size=12, color=MUTED))
    # розрив зворотного шляху
    gap_y = by + bh + 70
    f.append(line(bx + bw + 55, by + bh / 2 + 6, bx + bw + 55, gap_y, color=LINE))
    f.append(line(bx + bw + 55, gap_y, colL + 120, gap_y, color=LINE))
    # ножиці-розрив
    cx = colL + 75
    f.append(line(colL + 55, gap_y, cx - 6, gap_y, color=LINE))
    f.append(line(cx + 6, gap_y, colL + 55, by + bh / 2, color=LINE, dash="4 3"))
    f.append(line(colL + 55, by + bh / 2, bx, by + bh / 2 + 2, color=LINE, dash="4 3"))
    f.append(text(cx, gap_y - 10, "✂ розрив", size=13, color=POS, bold=True))
    # наслідок
    f.append(fitbox(colL + 20, gap_y + 24, pw - 40, 50,
                    "Зник постійний зворотний зв'язок —\nвихід зразу впирається в рейку.\nМіряти вже нічого.",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # ── права: AC-ін'єкція, петля ЗАМКНЕНА ──
    f.append(fitbox(colR, 44, pw, 26, "Вставити малий AC-сигнал у замкнену петлю",
                    size=13, bold=True, fill="#eafaf1", stroke=FIELD))
    rx, ry, rw, rh = colR + 90, 92, 150, 60
    f.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE))
    f.append(text(rx + rw / 2, ry + rh / 2 + 5, "регулятор", size=13))
    f.append(arrow(colR + 70, ry + rh / 2, rx, ry + rh / 2, color=LINE))
    f.append(arrow(rx + rw, ry + rh / 2, rx + rw + 40, ry + rh / 2, color=LINE))
    f.append(text(rx + rw + 60, ry + rh / 2 + 5, "вихід", size=12, color=MUTED))
    # повна петля назад, з вузликом ін'єкції
    loop_y = ry + rh + 70
    f.append(line(rx + rw + 55, ry + rh / 2, rx + rw + 55, loop_y, color=LINE))
    f.append(line(rx + rw + 55, loop_y, colR + 55, loop_y, color=LINE))
    f.append(line(colR + 55, loop_y, colR + 55, ry + rh / 2, color=LINE))
    f.append(line(colR + 55, ry + rh / 2, rx, ry + rh / 2, color=LINE))
    # точка ін'єкції на зворотному шляху
    inj_x = (rx + rw + 55 + colR + 55) / 2
    f.append(circle(inj_x, loop_y, 5, fill=FIELD, stroke=FIELD))
    f.append(text(inj_x, loop_y + 26, "≈ малий AC", size=13, color=FIELD, bold=True))
    f.append(text(inj_x, loop_y + 44, "поверх постійного", size=11, color=MUTED))
    f.append(fitbox(colR + 20, loop_y + 56, pw - 40, 30,
                    "DC-режим цілий — петля бачить лише дрібну хвильку.",
                    size=12, fill="#eafaf1", stroke=FIELD, color="#15803d"))
    return render(os.path.join(IMG, "open-vs-inject.svg"), W, H, *f,
                  title="Розірвати петлю не можна — її треба тільки «підштовхнути»")


def fig_injection():
    """Точка ін'єкції за Міддлбруком: малий резистор у зворотному тракті, два щупи A і B."""
    W, H = 760, 410
    f = []
    # вихід перетворювача (низький імпеданс) ───[R_inj]─── вузол дільника (високий імпеданс)
    y = 150
    out_x = 90
    rinj_x1, rinj_x2 = 250, 330
    div_x = 470
    # блок «вихід перетворювача»
    f.append(rect(out_x - 60, y - 30, 120, 60, fill=FILL, stroke=LINE))
    f.append(mtext(out_x, y, ["вихід", "перетворювача"], size=12))
    f.append(text(out_x, y + 48, "низький Z", size=12, color=NEG, bold=True))
    # провід до резистора
    f.append(line(out_x + 60, y, rinj_x1, y, color=LINE, sw=2))
    # резистор ін'єкції
    f.append(rect(rinj_x1, y - 12, rinj_x2 - rinj_x1, 24, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text((rinj_x1 + rinj_x2) / 2, y - 22, "R_ін ≈ 10 Ω", size=13, color=FIELD, bold=True))
    # провід до вузла дільника
    f.append(line(rinj_x2, y, div_x, y, color=LINE, sw=2))
    # дільник зворотного зв'язку
    f.append(circle(div_x, y, 4, fill=INK, stroke=INK))
    f.append(rect(div_x - 14, y + 18, 28, 40, fill=FILL, stroke=LINE))
    f.append(rect(div_x - 14, y + 78, 28, 40, fill=FILL, stroke=LINE))
    f.append(line(div_x, y, div_x, y + 18, color=LINE))
    f.append(line(div_x, y + 58, div_x, y + 78, color=LINE))
    f.append(line(div_x, y + 118, div_x, y + 138, color=LINE))
    f.append(line(div_x - 12, y + 138, div_x + 12, y + 138, color=LINE))  # земля
    f.append(line(div_x - 8, y + 143, div_x + 8, y + 143, color=LINE))
    f.append(line(div_x - 4, y + 148, div_x + 4, y + 148, color=LINE))
    # відвід до підсилювача похибки
    f.append(arrow(div_x, y + 58, div_x + 90, y + 58, color=LINE))
    f.append(mtext(div_x + 130, y + 62, ["до підсилювача", "похибки"], size=11, color=MUTED))
    f.append(text(div_x + 70, y + 100, "високий Z", size=12, color=POS, bold=True))
    # генератор поверх резистора
    gx = (rinj_x1 + rinj_x2) / 2
    f.append(line(rinj_x1, y, rinj_x1, y - 70, color=FIELD, sw=1.8))
    f.append(line(rinj_x2, y, rinj_x2, y - 70, color=FIELD, sw=1.8))
    f.append(circle(gx, y - 70, 22, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(gx, y - 64, "≈", size=22, color=FIELD, bold=True))
    f.append(line(rinj_x1, y - 70, gx - 22, y - 70, color=FIELD, sw=1.8))
    f.append(line(gx + 22, y - 70, rinj_x2, y - 70, color=FIELD, sw=1.8))
    f.append(mtext(gx + 95, y - 74, ["джерело збурення", "(плаваюче)"], size=11, color="#15803d"))
    # щупи A (після резистора, бік дільника) і B (до резистора, бік виходу)
    f.append(circle(rinj_x2 + 8, y, 4, fill=NEG, stroke=NEG))
    f.append(text(rinj_x2 + 8, y + 34, "A", size=15, color=NEG, bold=True))
    f.append(text(rinj_x2 + 8, y + 52, "(бік дільника)", size=10, color=MUTED))
    f.append(circle(rinj_x1 - 8, y, 4, fill=POS, stroke=POS))
    f.append(text(rinj_x1 - 8, y + 34, "B", size=15, color=POS, bold=True))
    f.append(text(rinj_x1 - 8, y + 52, "(бік виходу)", size=10, color=MUTED))
    # формула
    f.append(fitbox(W / 2 - 180, y + 175, 360, 40,
                    "Петлеве підсилення  L = B / A  на кожній частоті",
                    size=15, bold=True, fill="#fff7e6", stroke="#b8860b"))
    f.append(text(W / 2, y + 238,
                  "Вставляємо там, де низький Z жене у високий — інакше резистор спотворить режим.",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "injection-point.svg"), W, H, *f,
                  title="Ін'єкція напруги: малий резистор у зворотному тракті")


def fig_bode_margins():
    """Що друкує аналізатор: |L| перетинає 0 дБ, фаза сповзає до −180°, два запаси."""
    W, H = 760, 470
    f = []
    x0, x1 = 90, 690          # вісь частоти
    # ── верхня панель: магнітуда ──
    yt, yb = 70, 200          # топ/дно панелі магнітуди
    zero_db = 130             # рівень 0 дБ
    f.append(text(x0 - 60, yt + 8, "|L|, дБ", size=12, color=MUTED, anchor="start"))
    f.append(line(x0, yt, x0, yb, color=LINE))                 # вісь Y
    f.append(line(x0, zero_db, x1, zero_db, color=MUTED, sw=1, dash="5 4"))
    f.append(text(x1 + 4, zero_db + 4, "0 дБ", size=11, color=MUTED, anchor="start"))
    # крива магнітуди: спадає зліва направо, перетинає 0 дБ у точці кросовера
    fc_x = 430               # частота кросовера (|L|=1)
    pts = []
    for i in range(0, 61):
        xx = x0 + (x1 - x0) * i / 60.0
        # лог-подібний спад
        t = i / 60.0
        yy = yt + 12 + (yb - yt - 18) * (t ** 0.85)
        pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    # точка кросовера
    f.append(circle(fc_x, zero_db, 5, fill=NEG, stroke=NEG))
    f.append(line(fc_x, zero_db, fc_x, yb + 70, color=MUTED, sw=1, dash="3 3"))
    f.append(text(fc_x, yt + 4, "крос", size=11, color=NEG, anchor="middle"))
    # запас по підсиленню: на частоті фази −180° (правіше) |L| вже нижче 0 дБ
    f180_x = 560
    gm_top = zero_db
    gm_bot = yb - 18
    f.append(line(f180_x, gm_top, f180_x, gm_bot, color=FIELD, sw=3))
    f.append(line(f180_x - 5, gm_top, f180_x + 5, gm_top, color=FIELD, sw=2))
    f.append(line(f180_x - 5, gm_bot, f180_x + 5, gm_bot, color=FIELD, sw=2))
    f.append(text(f180_x + 8, (gm_top + gm_bot) / 2 + 4, "запас по", size=11, color="#15803d", anchor="start"))
    f.append(text(f180_x + 8, (gm_top + gm_bot) / 2 + 18, "підсиленню", size=11, color="#15803d", anchor="start"))

    # ── нижня панель: фаза ──
    pt, pb = 290, 420
    neg180 = 400             # рівень −180°
    f.append(text(x0 - 60, pt + 8, "фаза L, °", size=12, color=MUTED, anchor="start"))
    f.append(line(x0, pt, x0, pb, color=LINE))
    f.append(line(x0, neg180, x1, neg180, color=POS, sw=1, dash="5 4"))
    f.append(text(x1 + 4, neg180 + 4, "−180°", size=11, color=POS, anchor="start"))
    # крива фази: сповзає від ~−20° до за −180°
    pph = []
    for i in range(0, 61):
        xx = x0 + (x1 - x0) * i / 60.0
        t = i / 60.0
        yy = pt + 14 + (pb - pt - 14) * (t ** 1.35)
        pph.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join("%.1f,%.1f" % p for p in pph), POS))
    # фаза на частоті кросовера
    # знайдемо y фази при fc_x
    tcx = (fc_x - x0) / (x1 - x0)
    phy_cx = pt + 14 + (pb - pt - 14) * (tcx ** 1.35)
    f.append(circle(fc_x, phy_cx, 5, fill=POS, stroke=POS))
    # запас по фазі: від фази на кросовері до −180°
    f.append(line(fc_x, phy_cx, fc_x, neg180, color=FIELD, sw=3))
    f.append(line(fc_x - 5, phy_cx, fc_x + 5, phy_cx, color=FIELD, sw=2))
    f.append(line(fc_x - 5, neg180, fc_x + 5, neg180, color=FIELD, sw=2))
    f.append(text(fc_x - 10, (phy_cx + neg180) / 2 + 4, "запас по фазі", size=11,
                  color="#15803d", anchor="end"))
    # частота −180° вниз
    f.append(line(f180_x, neg180, f180_x, pt, color=MUTED, sw=1, dash="3 3"))
    f.append(circle(f180_x, neg180, 5, fill=POS, stroke=POS))
    f.append(text(f180_x, pb + 16, "тут фаза = −180°", size=11, color=POS, anchor="middle"))
    f.append(text(fc_x, pb + 16, "тут |L| = 1", size=11, color=NEG, anchor="middle"))
    # підпис осі частоти
    f.append(text((x0 + x1) / 2, pb + 40, "частота →", size=12, color=MUTED))
    return render(os.path.join(IMG, "measured-bode.svg"), W, H, *f,
                  title="Що друкує аналізатор: дві криві — і два запаси на них")


def fig_fra_pipeline():
    """Будова прошивки-FRA: внутрішнє кільце однієї точки + зовнішній прохід і пошук запасів."""
    W, H = 780, 470
    f = []
    cx = W / 2

    # ── внутрішнє кільце вимірювання однієї точки (по колу) ──
    f.append(text(cx, 52, "Внутрішнє кільце — одна точка на одній частоті",
                  size=14, bold=True, color=NEG))
    # п'ять вузлів кільця, розкладені по овалу
    ring_cy = 210
    rx, ry = 270, 120
    nodes = [
        ("генератор\nсинуса", -90),
        ("ін'єкція\nв керування", -18),
        ("петля →\nАЦП виходу", 54),
        ("кореляція\nҐерцеля ×2", 126),
        ("L = вихід /\nзбурення", 198),
    ]
    pos = []
    for label, ang in nodes:
        a = math.radians(ang)
        nx = cx + rx * math.cos(a)
        ny = ring_cy + ry * math.sin(a)
        pos.append((nx, ny))
    # стрілки по колу між сусідніми вузлами
    for i in range(len(pos)):
        x1, y1 = pos[i]
        x2, y2 = pos[(i + 1) % len(pos)]
        # вкоротити, щоб стрілка не лізла в рамки
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        f.append(arrow(x1 + ux * 52, y1 + uy * 26, x2 - ux * 52, y2 - uy * 26,
                       color=NEG, sw=1.8))
    # самі вузли поверх стрілок
    for (label, _), (nx, ny) in zip(nodes, pos):
        body, w, h = textbox(nx, ny, label, size=12, fill="#eaf0fd",
                             stroke=NEG, color=INK, min_w=96)
        f.append(body)
    f.append(mtext(cx, ring_cy - 4, ["кільце крутиться", "для кожної частоти"],
                   size=11, color=MUTED))

    # ── зовнішній блок: масив точок → пошук запасів ──
    by = 380
    f.append(fitbox(cx - 330, by, 250, 64,
                    "Зовнішній цикл: лог-сітка частот\nзбирає масив точок\n{ f, |L|(дБ), фаза(°) }",
                    size=12, fill="#f4f6f8", stroke=LINE))
    f.append(arrow(cx - 80, by + 32, cx + 20, by + 32, color=LINE))
    f.append(fitbox(cx + 20, by, 310, 64,
                    "Над масивом: знайти кросовер (|L|=0 дБ)\nі точку −180° → запас по фазі\nй запас по підсиленню",
                    size=12, fill="#eafaf1", stroke=FIELD, color="#15803d"))
    return render(os.path.join(IMG, "fra-pipeline.svg"), W, H, *f,
                  title="Будова прошивки-аналізатора петлі (FRA)")


def fig_whole_periods():
    """Чому цілі періоди: замкнена хвиля проти обірваного хвоста (витік)."""
    W, H = 760, 380
    f = []
    x0, x1 = 80, 600          # межі вікна накопичення
    amp = 42

    def wave(cy, periods, color, n=240):
        pts = []
        for i in range(n + 1):
            t = i / n
            xx = x0 + (x1 - x0) * t
            yy = cy - amp * math.sin(2 * math.pi * periods * t)
            pts.append((xx, yy))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
                % (" ".join("%.1f,%.1f" % p for p in pts), color))

    # рамка вікна (вертикальні межі)
    def window_marks(cy):
        out = line(x0, cy - amp - 14, x0, cy + amp + 14, color=MUTED, sw=1, dash="4 3")
        out += line(x1, cy - amp - 14, x1, cy + amp + 14, color=MUTED, sw=1, dash="4 3")
        out += line(x0, cy, x1, cy, color=MUTED, sw=1)
        return out

    # ── верх: рівно 4 періоди ──
    cyA = 110
    f.append(text(x0, cyA - amp - 26, "Вікно = рівно 4 періоди", size=14, bold=True,
                  color=FIELD, anchor="start"))
    f.append(window_marks(cyA))
    f.append(wave(cyA, 4.0, FIELD))
    # позначка, що кінець стикується з початком
    f.append(circle(x0, cyA, 4, fill=FIELD, stroke=FIELD))
    f.append(circle(x1, cyA, 4, fill=FIELD, stroke=FIELD))
    f.append(fitbox(x1 + 20, cyA - 26, 130, 52,
                    "кінець = початок,\nхвиля замкнулась,\nвитоку нема",
                    size=11, fill="#eafaf1", stroke=FIELD, color="#15803d"))

    # ── низ: 4.4 періоду ──
    cyB = 290
    f.append(text(x0, cyB - amp - 26, "Вікно = 4.4 періоду", size=14, bold=True,
                  color=POS, anchor="start"))
    f.append(window_marks(cyB))
    f.append(wave(cyB, 4.4, POS))
    f.append(circle(x0, cyB, 4, fill=POS, stroke=POS))
    # кінцева точка хвилі при 4.4 періоду
    yend = cyB - amp * math.sin(2 * math.pi * 4.4)
    f.append(circle(x1, yend, 4, fill=POS, stroke=POS))
    # виділити «зайвий хвіст» останніх 0.4 періоду
    tail_x = x0 + (x1 - x0) * (4.0 / 4.4)
    f.append(line(tail_x, cyB - amp - 8, tail_x, cyB + amp + 8, color=POS, sw=1, dash="3 3"))
    f.append(text((tail_x + x1) / 2, cyB + amp + 26, "обірваний хвіст 0.4 періоду",
                  size=11, color=POS))
    f.append(fitbox(x1 + 20, cyB - 26, 130, 52,
                    "кінець ≠ початок,\nхвіст підмішує\nфальшиву складову",
                    size=11, fill="#fdecea", stroke=POS, color=POS))
    return render(os.path.join(IMG, "whole-periods.svg"), W, H, *f,
                  title="Накопичувати треба рівно цілі періоди — інакше витік кривить фазу")


def fig_injection_error():
    """Похибка ін'єкції напруги як функція відношення імпедансів Z_наз/Z_впер."""
    W, H = 760, 430
    f = []
    # осі: X — відношення Z_наз/Z_впер у лог-шкалі (1/1000 .. 1/1), Y — похибка у %
    x0, x1 = 110, 660
    y0, yb = 70, 330               # верх / низ області графіка
    f.append(line(x0, y0, x0, yb, color=LINE))
    f.append(line(x0, yb, x1, yb, color=LINE))
    f.append(text(x0 - 70, y0 + 6, "похибка", size=12, color=MUTED, anchor="start"))
    f.append(text(x0 - 70, y0 + 22, "виміру", size=12, color=MUTED, anchor="start"))
    ratios = [1e-3, 1e-2, 1e-1, 1.0]          # Z_наз/Z_впер
    labels = ["1:1000", "1:100", "1:10", "1:1"]
    lo, hi = math.log10(1e-3), math.log10(1.0)

    def X(r):
        return x0 + (x1 - x0) * (math.log10(r) - lo) / (hi - lo)

    def Y(pct):
        t = (pct / 100.0) ** 0.5              # корінь — щоб малі % не злипалися біля осі
        return yb - (yb - y0) * t
    # горизонтальна сітка
    for pct, lab in [(1, "1 %"), (10, "10 %"), (50, "50 %"), (100, "100 %")]:
        yy = Y(pct)
        f.append(line(x0, yy, x1, yy, color="#e5e7eb", sw=1))
        f.append(text(x0 - 8, yy + 4, lab, size=10, color=MUTED, anchor="end"))
    # крива похибки: похибка(%) ≈ 100 · (Z_наз/Z_впер)  (для T ≫ 1)
    pts = []
    rr = 1e-3
    while rr <= 1.0001:
        pts.append((X(rr), Y(min(100.0, 100.0 * rr))))
        rr *= 1.08
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))
    # ключові точки
    marks = [(1e-2, 1.0, "1 %  (0.09 дБ)", FIELD, "ідеал"),
             (1e-1, 10.0, "10 %  (0.8 дБ)", "#b8860b", "терпимо"),
             (1.0, 100.0, "×2  (6 дБ)", POS, "брехня")]
    for r, pct, lab, col, verdict in marks:
        xx, yy = X(r), Y(pct)
        f.append(circle(xx, yy, 5, fill=col, stroke=col))
        # підписи останньої (правокрайньої) точки зсуваємо ліворуч-униз, щоб не вилазили й не лізли в заголовок
        if r >= 1.0:
            f.append(text(xx - 12, yy + 22, lab, size=12, color=col, bold=True, anchor="end"))
            f.append(text(xx - 12, yy + 38, verdict, size=11, color=col, anchor="end"))
        else:
            f.append(text(xx, yy - 12, lab, size=12, color=col, bold=True))
            f.append(text(xx, yy - 28, verdict, size=11, color=col))
    # підписи осі X
    for r, lab in zip(ratios, labels):
        xx = X(r)
        f.append(line(xx, yb, xx, yb + 5, color=LINE))
        f.append(text(xx, yb + 20, lab, size=12, color=INK, bold=(lab == "1:100")))
    f.append(text((x0 + x1) / 2, yb + 44,
                  "відношення імпедансів  Z_наз : Z_впер  (низьке жене у високе →)",
                  size=12, color=MUTED))
    f.append(fitbox(x0, yb + 56, x1 - x0, 30,
                    "похибка ≈ Z_наз / Z_впер   (там, де петлеве підсилення велике)",
                    size=13, bold=True, fill="#fff7e6", stroke="#b8860b"))
    return render(os.path.join(IMG, "injection-error.svg"), W, H, *f,
                  title="Ціна порушення «сто до одного»: похибка проти відношення імпедансів")


if __name__ == "__main__":
    fig_why_not_open()
    fig_injection()
    fig_bode_margins()
    fig_fra_pipeline()
    fig_whole_periods()
    fig_injection_error()
    print("OK figs")
