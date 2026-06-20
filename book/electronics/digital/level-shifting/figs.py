# -*- coding: utf-8 -*-
"""Фігури до теми «Зсув логічних рівнів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дві шкали напруг: де «1» одного не дотягує до порога іншого ───────────
def fig_two_scales():
    W, H = 720, 400
    f = [text(W / 2, 28, "Дві мікросхеми — дві шкали напруг; пороги не збігаються", size=16, bold=True)]

    base = 350           # рівень GND (низ шкал)
    top5 = 70            # верх 5-вольтової шкали
    top3 = 175           # верх 3.3-вольтової шкали (нижчий — менша напруга)
    x5, x3 = 200, 520    # центри двох вертикальних шкал
    bw = 70              # ширина смуги шкали

    def scale(cx, vtop, vdd, vil, vih, voh):
        # вертикальна смуга 0..VDD
        f.append(rect(cx - bw / 2, vtop, bw, base - vtop, fill="#f4f6f8", stroke=LINE, sw=1.6))
        f.append(text(cx, vtop - 12, "%.1f В" % vdd, size=13, bold=True))
        f.append(text(cx, base + 20, "0 В (GND)", size=11, color=MUTED))

        def y(v):       # напруга → координата
            return base - (v / vdd) * (base - vtop)

        # зона гарантованого LOW (зелена), HIGH (синя), невизначеність (сіра)
        f.append(rect(cx - bw / 2, y(vil), bw, base - y(vil), fill="#eaf6ee", stroke=None, sw=0))
        f.append(rect(cx - bw / 2, vtop, bw, y(vih) - vtop, fill="#eaf0fd", stroke=None, sw=0))
        # рамка поверх заливок
        f.append(rect(cx - bw / 2, vtop, bw, base - vtop, fill="none", stroke=LINE, sw=1.6))
        # лінії порогів
        for v, lab, col in [(vil, "VIL", FIELD), (vih, "VIH", NEG)]:
            f.append(line(cx - bw / 2, y(v), cx + bw / 2, y(v), color=col, sw=2))
            f.append(text(cx - bw / 2 - 8, y(v) + 4, "%s %.1f" % (lab, v), size=11,
                          color=col, anchor="end", bold=True))
        # рівень VOH цієї мікросхеми як вихід — маленька стрілка-мітка
        f.append(text(cx + bw / 2 + 8, y(voh) + 4, "VOH %.1f" % voh, size=11,
                      color=POS, anchor="start"))
        f.append(line(cx + bw / 2, y(voh), cx + bw / 2 + 6, y(voh), color=POS, sw=2))
        return y

    y5 = scale(x5, top5, 5.0, 1.5, 3.5, 4.4)     # 5 В TTL/CMOS-вхід орієнтовно
    y3 = scale(x3, top3, 3.3, 0.99, 2.31, 3.2)   # 3.3 В CMOS: 0.3·VDD / 0.7·VDD

    f.append(text(x5, base + 44, "5-вольтова логіка", size=12, bold=True))
    f.append(text(x3, base + 44, "3.3-вольтова логіка", size=12, bold=True))

    # головна стрілка: «1» від 3.3-чипа (VOH 3.2) → чи бачить її 5-вольтовий вхід (VIH 3.5)?
    f.append(line(x3 - bw / 2, y3(3.2), x5 + bw / 2, y3(3.2), color=POS, sw=1.6, dash="5,4"))
    b, _, _ = textbox((x3 + x5) / 2, y3(3.2) - 26,
                      "«1» з 3.3 В = 3.2 В\nале 5-вольтовому входу треба VIH = 3.5 В → НЕ бачить",
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "two-scales.svg"), W, H, *f)


# ── 2. Дві біди: вхід «не бачить» одиниці vs вхід згорів від перенапруги ─────
def fig_two_failures():
    W, H = 720, 360
    f = [text(W / 2, 28, "Два способи, якими пряме з'єднання різних рівнів ламається", size=16, bold=True)]

    # ЛІВА панель: «не бачить одиниці» (тиха відмова)
    lx = 30
    f.append(rect(lx, 56, 320, 270, fill="#fbfdfb", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(lx + 160, 80, "Сліпий вхід: 1 не дотягує", size=13, bold=True, color=INK))
    # драйвер 3.3 → приймач 5
    bd, _, _ = textbox(lx + 78, 130, "драйвер\n3.3 В\nVOH=3.2 В", size=11, fill="#eef2f8", stroke=NEG)
    f.append(bd)
    f.append(arrow(lx + 130, 130, lx + 210, 130, color=INK))
    br, _, _ = textbox(lx + 256, 130, "вхід\n5 В\nVIH=3.5 В", size=11, fill="#eef2f8", stroke=NEG)
    f.append(br)
    f.append(text(lx + 160, 182, "3.2 В < 3.5 В", size=13, bold=True, color=POS))
    b1, _, _ = textbox(lx + 160, 226, "вхід читає «1» як «0» (або як завгодно):\nзв'язок мовчки не працює",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b1)
    f.append(text(lx + 160, 296, "ніщо не гріється — просто не передається", size=11,
                  color=MUTED, italic=True))

    # ПРАВА панель: «горить вхід» (перенапруга)
    rx = 370
    f.append(rect(rx, 56, 320, 270, fill="#fffaf9", stroke=POS, sw=1.6, rx=10))
    f.append(text(rx + 160, 80, "Спалений вхід: перенапруга", size=13, bold=True, color=INK))
    bd2, _, _ = textbox(rx + 78, 130, "драйвер\n5 В\nVOH=4.4 В", size=11, fill="#fdecea", stroke=POS)
    f.append(bd2)
    f.append(arrow(rx + 130, 130, rx + 210, 130, color=POS, sw=2.4))
    br2, _, _ = textbox(rx + 256, 130, "вхід 3.3 В\nVDD=3.3 В", size=11, fill="#fdecea", stroke=POS)
    f.append(br2)
    f.append(text(rx + 160, 182, "4.4 В  ≫  3.3 В + 0.5 В", size=12.5, bold=True, color=POS))
    b2, _, _ = textbox(rx + 160, 226, "захисний діод входу відмикається,\nкрізь нього тече струм → деградація/смерть",
                       size=10.5, fill="#fdecea", stroke=POS)
    f.append(b2)
    f.append(text(rx + 160, 296, "може згоріти одразу або «жити» й тихо вмирати", size=11,
                  color=MUTED, italic=True))
    render(os.path.join(IMG, "two-failures.svg"), W, H, *f)


# ── 3. Резистивний дільник: зсув ТІЛЬКИ вниз, з числами ─────────────────────
def fig_divider():
    W, H = 720, 380
    f = [text(W / 2, 28, "Резистивний дільник: опускає 5 В → 3.3 В (лише в один бік)", size=16, bold=True)]

    # схема дільника зліва
    sx = 150
    vtop, vbot = 70, 300
    # верхня лінія = вхід 5 В
    f.append(text(sx, vtop - 16, "вхід 5 В (драйвер)", size=12, bold=True, color=POS))
    f.append(line(sx, vtop, sx, vtop + 30, color=LINE, sw=2))
    # R1
    f.append(rect(sx - 16, vtop + 30, 32, 60, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(sx + 44, vtop + 64, "R1 = 1.7 кОм", size=12, color=INK, anchor="start"))
    f.append(line(sx, vtop + 90, sx, vtop + 120, color=LINE, sw=2))
    # вузол виходу
    f.append(circle(sx, vtop + 120, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(sx, vtop + 120, sx + 150, vtop + 120, color=NEG, sw=2))
    bv, _, _ = textbox(sx + 240, vtop + 120, "вихід ≈ 3.3 В\n→ на 3.3-В вхід", size=11,
                       fill="#eef2f8", stroke=NEG, bold=True)
    f.append(bv)
    # R2
    f.append(rect(sx - 16, vtop + 120 + 10, 32, 60, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(sx + 44, vtop + 124 + 40, "R2 = 3.3 кОм", size=12, color=INK, anchor="start"))
    f.append(line(sx, vtop + 120 + 70, sx, vbot, color=LINE, sw=2))
    # GND
    f.append(line(sx - 18, vbot, sx + 18, vbot, color=INK, sw=2.4))
    f.append(line(sx - 12, vbot + 6, sx + 12, vbot + 6, color=INK, sw=2))
    f.append(line(sx - 6, vbot + 12, sx + 6, vbot + 12, color=INK, sw=2))
    f.append(text(sx, vbot + 30, "GND", size=11, color=MUTED))

    # формула праворуч
    b, _, _ = textbox(530, 130, "Vвих = Vвх · R2/(R1+R2)\n= 5 · 3.3/(1.7+3.3)\n= 5 · 0.66 = 3.3 В",
                      size=13, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)
    b2, _, _ = textbox(530, 250,
                       "Тільки ВНИЗ: 3.3 В назад\nне підняти. І дільник\nгальмує фронт (RC).",
                       size=11.5, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "divider.svg"), W, H, *f)


# ── 4. MOSFET-двонапрямний зсувач (класична схема BSS138) ───────────────────
def fig_mosfet():
    W, H = 720, 420
    f = [text(W / 2, 28, "MOSFET-зсувач: один транзистор зшиває обидва боки в обидва напрямки", size=15.5, bold=True)]

    yL = 150     # лінія низької сторони (3.3 В)
    yH = 280     # лінія високої сторони (5 В)
    xL, xR = 110, 610

    # дві шини живлення (підтяжки)
    f.append(text(xL - 4, 70, "3.3 В", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(text(xR + 4, 70, "5 В", size=12, bold=True, color=POS, anchor="middle"))
    # підтяжки
    f.append(line(xL, 80, xL, 110, color=NEG, sw=2))
    f.append(rect(xL - 14, 110, 28, 36, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(xL - 40, 132, "Rп", size=11, color=MUTED, anchor="middle"))
    f.append(line(xL, 146, xL, yL, color=NEG, sw=2))
    f.append(line(xR, 80, xR, 110, color=POS, sw=2))
    f.append(rect(xR - 14, 110, 28, 36, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(xR + 40, 132, "Rп", size=11, color=MUTED, anchor="middle"))
    f.append(line(xR, 146, xR, yH, color=POS, sw=2))

    # лінії сторін
    f.append(line(xL, yL, 300, yL, color=NEG, sw=2))
    f.append(line(420, yH, xR, yH, color=POS, sw=2))
    f.append(text(xL, yL - 12, "низька сторона (3.3 В)", size=11, color=NEG, anchor="start"))
    f.append(text(xR, yH + 26, "висока сторона (5 В)", size=11, color=POS, anchor="end"))
    f.append(circle(xL, yL, 4, fill=INK, stroke=INK, sw=1))
    f.append(circle(xR, yH, 4, fill=INK, stroke=INK, sw=1))

    # транзистор у центрі
    tx = 360
    f.append(rect(tx - 50, yL - 20, 100, (yH - yL) + 40, fill="#f7f9fb", stroke=LINE, sw=1.5, rx=8))
    f.append(text(tx, yL - 30, "N-MOSFET", size=12, bold=True))
    # затвор на низьку напругу
    f.append(line(tx - 50, (yL + yH) / 2, tx - 90, (yL + yH) / 2, color=FIELD, sw=2))
    bg, _, _ = textbox(tx - 150, (yL + yH) / 2, "затвор\nна 3.3 В", size=10.5,
                       fill="#eef6ef", stroke=FIELD)
    f.append(bg)
    # стік/витік
    f.append(line(300, yL, tx - 8, yL, color=NEG, sw=2))
    f.append(line(tx + 8, yH, 420, yH, color=POS, sw=2))
    f.append(text(tx, (yL + yH) / 2 + 4, "S↔D", size=13, bold=True, color=INK))

    # пояснення дій знизу — два короткі рядки
    b1, _, _ = textbox(W / 2, 360,
                       "низька сторона тягне в 0 → транзистор відкривається → висока теж падає в 0",
                       size=11, fill="#eef2f8", stroke=NEG)
    f.append(b1)
    b2, _, _ = textbox(W / 2, 392,
                       "обидві відпущені → підтяжки тримають кожну сторону на її власному VDD",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "mosfet.svg"), W, H, *f)


# ── 5. Швидкість vs ємність: RC-фронт на лінії з підтяжкою ──────────────────
def fig_speed():
    W, H = 720, 380
    f = [text(W / 2, 28, "Чим слабша підтяжка й більша ємність — тим лінивіший фронт", size=16, bold=True)]

    ox, oy = 90, 300
    ax_w, ax_h = 560, 220
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 40, "час після того, як ніжку відпустили", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h / 2, "напруга", size=12, color=INK))
    f.append(text(ox - 56, oy - ax_h / 2 + 16, "на лінії", size=11, color=MUTED))

    # рівень VDD і поріг VIH
    yVDD = oy - ax_h
    yVIH = oy - 0.7 * ax_h
    f.append(line(ox, yVDD, ox + ax_w, yVDD, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(ox + ax_w, yVDD - 6, "VDD", size=11, color=MUTED, anchor="end"))
    f.append(line(ox, yVIH, ox + ax_w, yVIH, color=NEG, sw=1.4, dash="3,4"))
    f.append(text(ox + ax_w, yVIH - 6, "VIH (поріг «1»)", size=11, color=NEG, anchor="end"))

    import math
    def curve(tau, color, sw=2.6):
        pts = []
        for i in range(0, 561, 6):
            t = i / ax_w * 6.0       # умовний час
            v = 1 - math.exp(-t / tau)
            pts.append("%.1f,%.1f" % (ox + i, oy - v * ax_h))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' %
                 (" ".join(pts), color, sw))

    curve(0.7, FIELD)     # сильна підтяжка / мала ємність — швидко
    curve(2.2, POS)       # слабка підтяжка / велика ємність — мляво

    f.append(text(ox + 150, oy - 0.92 * ax_h, "сильна підтяжка,\nмала ємність", size=11,
                  color=FIELD, anchor="start"))
    f.append(mtext(ox + 150, oy - 0.95 * ax_h, ["сильна підтяжка,", "мала ємність"],
                   size=11, color=FIELD, anchor="start"))
    f.append(mtext(ox + 330, oy - 0.42 * ax_h, ["слабка підтяжка,", "велика ємність →", "пізно перетинає поріг"],
                   size=11, color=POS, anchor="start"))
    f.append(text(W / 2, oy + 64, "фронт = τ = R · C; на швидкій шині млявий фронт не встигає піднятися до VIH",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "speed.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_scales()
    fig_two_failures()
    fig_divider()
    fig_mosfet()
    fig_speed()
    print("OK: 5 figures ->", IMG)
