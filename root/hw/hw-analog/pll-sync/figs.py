# -*- coding: utf-8 -*-
"""Фігури до статті «PLL-синхронізація приймача у аналоговому відео»
   (book/electronics/analog/pll-sync). Чотири фігури:

  line.svg    — анатомія рядка: рівень чорного, синхроімпульс, задня площадка з burst
  flywheel.svg— маховик-петля: фазовий детектор → ФНЧ → керований генератор → назад
  noise.svg   — навіщо петля: одиночний імпульс губиться в завадах, маховик усереднює
  twoloops.svg— дві петлі приймача: повільна (рядкова) і швидка (кольорова піднесена)

Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні помічники ──────────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.2),
           line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=1.9),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.7)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def block(cx, cy, w, h, lines, fill=FILL, stroke=LINE, size=12, bold=True):
    """Прямокутний блок-цеглинка зі стислим підписом усередині (через fitbox)."""
    s = "\n".join(lines) if isinstance(lines, (list, tuple)) else lines
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, fill=fill,
                  stroke=stroke, sw=1.8, bold=bold)


# ════════════════════════════════════════════════════════════════════════════
# 1. line.svg — анатомія одного телевізійного рядка
# ════════════════════════════════════════════════════════════════════════════
def fig_line():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Один рядок композитного відео", size=16, bold=True))

    # осі-орієнтири
    x0, x1 = 70, 660
    y_white = 90      # рівень білого (верх картинки)
    y_black = 210     # рівень чорного / гасіння
    y_sync = 270      # дно синхроімпульсу

    # підписи рівнів
    f.append(line(x0 - 6, y_white, x1, y_white, color="#e3e6ea", sw=1.0, dash="4 4"))
    f.append(line(x0 - 6, y_black, x1, y_black, color="#e3e6ea", sw=1.0, dash="4 4"))
    f.append(line(x0 - 6, y_sync, x1, y_sync, color="#e3e6ea", sw=1.0, dash="4 4"))
    f.append(text(x0 - 10, y_white + 4, "білий", size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 10, y_black + 4, "чорний / гасіння", size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 10, y_sync + 4, "дно синхро", size=10, color=NEG, anchor="end"))

    # сам сигнал рядка (ламана): активна картинка → площадка → синхро → задня площадка → burst → картинка
    # координати ключових точок по X
    xa = 90      # кінець активної частини попереднього (тут — активна картинка)
    xb = 250     # передня площадка
    xc = 270     # спад у синхро
    xd = 360     # дно синхро
    xe = 380     # підйом до чорного
    xf = 520     # задня площадка (тут сидить burst)
    xg = 660     # знов активна картинка

    # активна картинка (гойдається трохи навколо середини між білим і чорним)
    pts = []
    import random
    random.seed(3)
    xx = x0
    pts.append((xx, y_black))
    # «картинка» зліва — хвиляста яскравість
    for k in range(7):
        xx += (xa - x0) / 7
        yy = y_black - (y_black - y_white) * (0.35 + 0.45 * (0.5 + 0.5 * math.sin(k * 1.3)))
        pts.append((xx, yy))
    # вихід на передню площадку (рівень гасіння)
    pts.append((xb, y_black))
    pts.append((xc, y_black))
    # синхроімпульс вниз
    pts.append((xc, y_sync))
    pts.append((xd, y_sync))
    # підйом назад до рівня гасіння (задня площадка)
    pts.append((xe, y_sync))
    pts.append((xe, y_black))
    pts.append((xf, y_black))
    # після burst — знову картинка
    xx = xf
    for k in range(6):
        xx += (xg - xf) / 6
        yy = y_black - (y_black - y_white) * (0.3 + 0.5 * (0.5 + 0.5 * math.sin(k * 1.6 + 1)))
        pts.append((xx, yy))

    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))

    # колірний burst на задній площадці (8–9 циклів синусоїди близько рівня гасіння)
    bx0, bx1 = 430, 505
    by = y_black
    amp = 16
    bp = []
    n = 9
    for i in range(n * 6 + 1):
        t = i / 6.0
        xx = bx0 + (bx1 - bx0) * (t / n)
        yy = by - amp * math.sin(2 * math.pi * t)
        bp.append((xx, yy))
    bd = "M " + " L ".join("%.1f %.1f" % p for p in bp)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (bd, POS))

    # підписи-виноски
    f.append(text((xc + xd) / 2, y_sync + 22, "синхроімпульс", size=12, color=NEG, bold=True))
    f.append(text((xc + xd) / 2, y_sync + 37, "«ось межа рядка»", size=10, color=MUTED))

    f.append(text((bx0 + bx1) / 2, by - amp - 10, "колірний burst", size=12, color=POS, bold=True))
    f.append(text((bx0 + bx1) / 2, by - amp - 25, "8–9 циклів 3.58 МГц", size=10, color=MUTED))
    f.append(line((bx0 + bx1) / 2, by + 6, (bx0 + bx1) / 2, by + 30, color=POS, sw=1.2, dash="3 3"))
    f.append(text((bx0 + bx1) / 2, by + 44, "задня площадка", size=10, color=MUTED))

    f.append(text((x0 + xa) / 2, y_white - 12, "яскравість картинки", size=11, color=MUTED))

    render(os.path.join(IMG, "line.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. flywheel.svg — петля синхронізації як маховик
# ════════════════════════════════════════════════════════════════════════════
def fig_flywheel():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Петля синхронізації: фаза → напруга → частота → назад", size=15, bold=True))

    cy = 175
    # вхід ліворуч
    f.append(arrow(40, cy, 110, cy, color=NEG, sw=2.6))
    f.append(text(75, cy - 12, "синхро з", size=11, color=NEG, anchor="middle"))
    f.append(text(75, cy + 22, "ефіру", size=11, color=NEG, anchor="middle"))

    # 1) фазовий детектор
    f.append(block(180, cy, 130, 76, ["фазовий", "детектор", "(хто попереду?)"], size=12,
                   fill="#eaf0fd", stroke=NEG))

    # 2) ФНЧ-усереднювач
    f.append(block(360, cy, 130, 76, ["ФНЧ", "усереднює", "за багато рядків"], size=12,
                   fill="#eef7f0", stroke=FIELD))

    # 3) керований генератор
    f.append(block(560, cy, 140, 76, ["керований", "генератор", "(маховик)"], size=12,
                   fill="#fdecea", stroke=POS))

    # стрілки вперед
    f.append(arrow(245, cy, 295, cy, color=INK, sw=2.2))
    f.append(text(270, cy - 10, "похибка", size=10, color=MUTED))
    f.append(arrow(425, cy, 490, cy, color=INK, sw=2.2))
    f.append(text(458, cy - 10, "керна", size=10, color=MUTED))
    f.append(text(458, cy + 12, "напруга", size=10, color=MUTED))

    # вихід — місцева розгортка/піднесена
    f.append(arrow(630, cy, 690, cy, color=POS, sw=2.6))
    f.append(text(690, cy - 12, "місцевий", size=11, color=POS, anchor="end"))
    f.append(text(690, cy + 22, "такт", size=11, color=POS, anchor="end"))

    # зворотний зв'язок: вихід генератора → назад у фазовий детектор
    fb_y = 290
    f.append(line(560, cy + 38, 560, fb_y, color=INK, sw=1.8))
    f.append(line(560, fb_y, 180, fb_y, color=INK, sw=1.8))
    f.append(arrow(180, fb_y, 180, cy + 38, color=INK, sw=2.0))
    f.append(text(370, fb_y - 8, "порівнюємо власну фазу з вхідною  —  від’ємний зворотний зв’язок", size=11, color=INK, anchor="middle"))

    render(os.path.join(IMG, "flywheel.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. noise.svg — навіщо петля: усереднення проти завад
# ════════════════════════════════════════════════════════════════════════════
def fig_noise():
    W, H = 720, 330
    f = []
    f.append(text(W / 2, 28, "Чому маховик, а не «йти за кожним імпульсом»", size=15, bold=True))

    import random
    random.seed(7)

    # ліва панель — зашумлений вхід
    lx0, lx1 = 60, 350
    base = 150
    f.append(text((lx0 + lx1) / 2, 60, "сирий синхро у завадах", size=12, color=NEG, bold=True))
    # шумна лінія з кількома «справжніми» імпульсами і фальшивими сплесками
    pts = []
    xx = lx0
    pulses = [120, 200, 280]   # справжні позиції
    while xx <= lx1:
        yy = base + random.uniform(-10, 10)
        # фальшиві сплески
        if random.random() < 0.06:
            yy = base - random.uniform(25, 45)
        pts.append((xx, yy))
        xx += 4
    # домалюємо справжні імпульси (глибокі вниз)
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (d, MUTED))
    for px in pulses:
        f.append(line(px, base, px, base - 60, color=NEG, sw=2.4))
        f.append(line(px - 6, base - 60, px + 6, base - 60, color=NEG, sw=2.4))
    # фальшивий сплеск, що збиває
    f.append(line(165, base, 165, base - 40, color=POS, sw=2.2, dash="3 3"))
    f.append(text(165, base + 18, "фальшивий", size=9, color=POS, anchor="middle"))
    f.append(text(165, base + 30, "сплеск", size=9, color=POS, anchor="middle"))
    body, _, _ = textbox((lx0 + lx1) / 2, 250, "підеш за кожним —\nрядок стрибне від однієї завади",
                         size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(body)

    # роздільник
    f.append(line(W / 2, 80, W / 2, 300, color="#e3e6ea", sw=1.2))

    # права панель — маховик усереднює
    rx0, rx1 = 370, 660
    f.append(text((rx0 + rx1) / 2, 60, "маховик тримає темп", size=12, color=FIELD, bold=True))
    # рівний такт від генератора (стабільні мітки)
    ry = 150
    f.append(line(rx0, ry, rx1, ry, color="#e3e6ea", sw=1.0))
    step = (rx1 - rx0) / 9
    for i in range(10):
        xx = rx0 + i * step
        f.append(line(xx, ry, xx, ry - 55, color=FIELD, sw=2.4))
        f.append(line(xx - 6, ry - 55, xx + 6, ry - 55, color=FIELD, sw=2.4))
    f.append(text((rx0 + rx1) / 2, ry + 20, "рівні власні мітки — фаза підправляється помалу", size=10, color=MUTED))
    body, _, _ = textbox((rx0 + rx1) / 2, 250, "велика стала часу ФНЧ:\nодна завада майже не зрушує темп",
                         size=11, color=FIELD, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "noise.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. twoloops.svg — дві окремі петлі в кольоровому приймачі
# ════════════════════════════════════════════════════════════════════════════
def fig_twoloops():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 28, "Дві петлі в кольоровому приймачі", size=16, bold=True))

    # спільний вхід
    f.append(arrow(40, 200, 110, 200, color=INK, sw=2.6))
    f.append(text(75, 184, "композит", size=11, color=INK, anchor="middle"))
    f.append(block(180, 200, 110, 70, ["розділювач", "(що це за", "частина?)"], size=11,
                   fill=FILL, stroke=LINE))

    # верхня гілка — повільна рядкова петля (від синхроімпульсів)
    yA = 120
    f.append(line(235, 185, 300, yA, color=NEG, sw=1.8))
    f.append(block(420, yA, 200, 70, ["ПОВІЛЬНА петля — рядкова",
                                      "веде за синхроімпульсами",
                                      "≈15.6 кГц, проста RC-настройка"], size=11,
                   fill="#eaf0fd", stroke=NEG))
    f.append(arrow(522, yA, 600, yA, color=NEG, sw=2.2))
    f.append(text(660, yA - 10, "розгортка", size=11, color=NEG, anchor="middle"))
    f.append(text(660, yA + 12, "(де малювати)", size=10, color=MUTED, anchor="middle"))

    # нижня гілка — швидка кольорова петля (від burst, кварц)
    yB = 285
    f.append(line(235, 215, 300, yB, color=POS, sw=1.8))
    f.append(block(420, yB, 200, 70, ["ШВИДКА петля — кольорова",
                                      "веде за burst, кварц 3.58 МГц",
                                      "вузька смуга, точна фаза"], size=11,
                   fill="#fdecea", stroke=POS))
    f.append(arrow(522, yB, 600, yB, color=POS, sw=2.2))
    f.append(text(660, yB - 10, "піднесена", size=11, color=POS, anchor="middle"))
    f.append(text(660, yB + 12, "(який колір)", size=10, color=MUTED, anchor="middle"))

    # підпис-суть
    body, _, _ = textbox(W / 2, 355,
                         "Та сама ідея петлі — двічі: одна тримає ГЕОМЕТРІЮ кадру, друга — ФАЗУ кольору",
                         size=12, color=INK, fill="#f4f6f8", stroke=LINE)
    f.append(body)

    render(os.path.join(IMG, "twoloops.svg"), W, H, *f)


if __name__ == "__main__":
    fig_line()
    fig_flywheel()
    fig_noise()
    fig_twoloops()
    print("OK: 4 фігури у", IMG)
