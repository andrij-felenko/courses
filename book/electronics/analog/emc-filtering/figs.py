# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_cm_dm():
    """Дві природи завади: диференційна (туди-назад) і синфазна (обома проводами в землю)."""
    W, H = 760, 360
    p = []
    # ── ліворуч: диференційна ──
    lx = 40
    p.append(text(150, 56, "Диференційна (DM)", size=15, bold=True, color=NEG))
    # джерело — прямокутник
    p.append(rect(lx, 90, 70, 120, rx=8))
    p.append(mtext(lx + 35, 150, ["при-", "стрій"], size=12))
    # дві лінії L і N
    p.append(line(lx + 70, 115, 250, 115, color=NEG, sw=3))
    p.append(line(lx + 70, 185, 250, 185, color=NEG, sw=3))
    # стрілки протиходу
    p.append(arrow(150, 115, 200, 115, color=NEG, sw=2.4))
    p.append(arrow(200, 185, 150, 185, color=NEG, sw=2.4))
    p.append(text(230, 108, "L", size=12, color=MUTED, anchor="start"))
    p.append(text(230, 200, "N", size=12, color=MUTED, anchor="start"))
    p.append(mtext(150, 250, ["струм тече туди одним проводом,",
                              "назад другим — як корисний"], size=11.5, color=INK))
    p.append(mtext(150, 295, ["давить пара впоперек шин:", "X-конденсатор"],
                   size=11.5, color=POS, bold=True))

    # ── роздільник ──
    p.append(line(W / 2, 80, W / 2, 320, color=MUTED, sw=1, dash="4,4"))

    # ── праворуч: синфазна ──
    rx = 430
    p.append(text(610, 56, "Синфазна (CM)", size=15, bold=True, color=POS))
    p.append(rect(rx, 90, 70, 120, rx=8))
    p.append(mtext(rx + 35, 150, ["при-", "стрій"], size=12))
    p.append(line(rx + 70, 115, 700, 115, color=POS, sw=3))
    p.append(line(rx + 70, 185, 700, 185, color=POS, sw=3))
    # обидва в один бік
    p.append(arrow(560, 115, 610, 115, color=POS, sw=2.4))
    p.append(arrow(560, 185, 610, 185, color=POS, sw=2.4))
    # земля знизу — повернення
    p.append(line(rx, 330, 700, 330, color=FIELD, sw=2.5))
    p.append(text(rx - 4, 334, "земля (PE / паразитна ємність на корпус)",
                  size=10.5, color=FIELD, anchor="start"))
    p.append(line(700, 115, 700, 330, color=FIELD, sw=2, dash="3,3"))
    p.append(line(700, 185, 715, 185, color=FIELD, sw=2))
    p.append(arrow(640, 330, 560, 330, color=FIELD, sw=2.2))
    p.append(mtext(610, 250, ["той самий струм обома проводами в землю,",
                              "назад — паразитом по корпусу"], size=11.5, color=INK))
    p.append(mtext(610, 295, ["давить дросель + пара в землю:",
                              "синфазний дросель + Y-конденсатори"],
                   size=11.5, color=POS, bold=True))

    render(os.path.join(IMG, 'cm-dm.svg'), W, H, *p,
           title="Два сорти завади різняться шляхом струму")


def fig_topology():
    """Стандартний вхідний фільтр: X-cap, синфазний дросель, Y-cap — і що кожне глушить."""
    W, H = 780, 430
    p = []
    yL, yN = 110, 250          # рівні шин L і N
    gnd = 360                  # рівень землі/PE
    x0, x1 = 70, 720
    # шини
    p.append(line(x0, yL, x1, yL, sw=3))
    p.append(line(x0, yN, x1, yN, sw=3))
    p.append(line(x0, gnd, x1, gnd, color=FIELD, sw=2.5))
    p.append(text(x0 - 6, yL - 12, "L (мережа)", size=12, anchor="start", color=MUTED))
    p.append(text(x0 - 6, yN + 24, "N", size=12, anchor="start", color=MUTED))
    p.append(text(x1 + 4, gnd + 4, "PE", size=12, anchor="start", color=FIELD))

    # вхід ліворуч (шумний бік — пристрій), вихід праворуч (мережа). Малюємо зліва направо.
    # X-cap №1 (вхід)
    xc1 = 180
    p.append(line(xc1, yL, xc1, yN, color=POS, sw=2.5))
    p.append(rect(xc1 - 14, 165, 28, 30, fill="#fdecea", stroke=POS, rx=4))
    p.append(text(xc1, 158, "X", size=12, bold=True, color=POS, anchor="middle"))

    # синфазний дросель — дві обмотки на спільному осерді
    cmc_x = 300
    p.append(rect(cmc_x - 26, yL - 18, 52, 36, fill="#eef7f0", stroke=FIELD, rx=5))
    p.append(rect(cmc_x - 26, yN - 18, 52, 36, fill="#eef7f0", stroke=FIELD, rx=5))
    # позначка спільного осердя
    p.append(line(cmc_x, yL + 18, cmc_x, yN - 18, color=FIELD, sw=2, dash="3,3"))
    p.append(text(cmc_x, yL - 26, "синфазний", size=11, color=FIELD, bold=True))
    p.append(text(cmc_x, yN + 36, "дросель (CMC)", size=11, color=FIELD, bold=True))

    # Y-cap пара (після дроселя, в землю)
    yc = 430
    p.append(line(yc, yL, yc, gnd, color=POS, sw=2.2))
    p.append(line(yc, yN, yc, gnd, color=POS, sw=2.2))
    p.append(rect(yc - 12, 175, 24, 22, fill="#fdecea", stroke=POS, rx=3))
    p.append(rect(yc - 12, 285, 24, 22, fill="#fdecea", stroke=POS, rx=3))
    p.append(text(yc + 16, 188, "Y", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(yc + 16, 300, "Y", size=12, bold=True, color=POS, anchor="start"))

    # X-cap №2 (вихід до мережі)
    xc2 = 560
    p.append(line(xc2, yL, xc2, yN, color=POS, sw=2.5))
    p.append(rect(xc2 - 14, 165, 28, 30, fill="#fdecea", stroke=POS, rx=4))
    p.append(text(xc2, 158, "X", size=12, bold=True, color=POS, anchor="middle"))

    # bleeder-резистор біля входу
    br = 130
    p.append(line(br, yL, br, yN, color=MUTED, sw=1.6, dash="2,3"))
    p.append(text(br, 200, "R", size=11, color=MUTED))
    p.append(text(br, 215, "розряд", size=9, color=MUTED))

    # підписи зон
    p.append(text(x0 + 20, 400, "← до пристрою (джерело шуму)", size=11.5,
                  anchor="start", color=NEG))
    p.append(text(x1 - 10, 400, "до мережі →", size=11.5, anchor="end", color=NEG))

    # легенда «що глушить що»
    ly = 30
    p.append(fitbox(40, ly - 8, 330, 26,
                    "X-конденсатор: впоперек L–N → диференційна завада",
                    size=11, fill="#fdecea", stroke=POS))
    p.append(fitbox(410, ly - 8, 330, 26,
                    "CMC + Y у землю → синфазна завада",
                    size=11, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(IMG, 'topology.svg'), W, H, *p,
           title="Вхідний ЕМС-фільтр: кожна деталь б'є свій сорт завади")


def fig_limit():
    """Лінія ліміту CISPR 32 / EN 55032 клас B і де фільтр стягує спектр під неї."""
    W, H = 740, 400
    p = []
    # осі
    ox, oy = 90, 330      # початок
    ax, ay = 690, 60      # кінці
    p.append(line(ox, oy, ax, oy, sw=2))          # X
    p.append(line(ox, oy, ox, ay, sw=2))          # Y
    p.append(text(ax, oy + 30, "частота", size=12, anchor="end", color=MUTED))
    p.append(text(ox - 8, oy + 30, "0.15", size=10.5, anchor="middle", color=MUTED))
    p.append(text(ax - 10, oy + 30, "30 МГц", size=10.5, anchor="middle", color=MUTED))
    p.append(text(ox - 70, (oy + ay) / 2, "рівень,", size=12, anchor="start", color=MUTED))
    p.append(text(ox - 70, (oy + ay) / 2 + 16, "дБмкВ", size=12, anchor="start", color=MUTED))

    # шкала рівнів (орієнтири)
    for lvl, yy in [(40, 290), (56, 200), (66, 150), (80, 95)]:
        p.append(line(ox - 5, yy, ox, yy, sw=1.5, color=MUTED))
        p.append(text(ox - 10, yy + 4, str(lvl), size=10, anchor="end", color=MUTED))

    # лінія ліміту клас B (квазіпік): 66→56 у 0.15..0.5, 56 у 0.5..5, 60 у 5..30
    L = oy + ay  # не used
    p.append(line(ox, 150, 230, 200, color=POS, sw=2.6))       # 66→56
    p.append(line(230, 200, 430, 200, color=POS, sw=2.6))      # 56
    p.append(line(430, 200, 430, 176, color=POS, sw=2.6))      # сходинка вгору до 60
    p.append(line(430, 176, ax, 176, color=POS, sw=2.6))       # 60
    p.append(text(ax - 4, 168, "ліміт класу B (QP)", size=11.5, anchor="end",
                  color=POS, bold=True))

    # спектр ДО фільтра — стирчить над лінією (зубчастий)
    import math
    pre = []
    for i in range(0, 61):
        fx = ox + i * (ax - ox) / 60.0
        base = 230 - 70 * math.exp(-((i - 14) ** 2) / 120.0)  # горб у НЧ
        spikes = -22 * (1 if i % 6 == 0 else 0) - 10 * (1 if i % 4 == 0 else 0)
        fy = base + spikes
        pre.append((fx, max(min(fy, oy), 80)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in pre), NEG))
    p.append(text(150, 95, "без фільтра", size=11.5, color=NEG, anchor="middle", bold=True))

    # спектр ПІСЛЯ — під лінією
    post = []
    for i in range(0, 61):
        fx = ox + i * (ax - ox) / 60.0
        fy = 260 - 18 * math.exp(-((i - 14) ** 2) / 160.0) + (4 if i % 5 == 0 else 0)
        post.append((fx, fy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" ".join("%.1f,%.1f" % q for q in post), FIELD))
    p.append(text(150, 275, "після фільтра", size=11.5, color=FIELD, anchor="middle", bold=True))

    p.append(fitbox(150, 348, 440, 30,
                    "завдання фільтра — стягти весь спектр у смузі 150 кГц…30 МГц під лінію ліміту",
                    size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'limit.svg'), W, H, *p,
           title="Навіщо фільтр: спектр шуму проти лінії ліміту")


if __name__ == '__main__':
    fig_cm_dm()
    fig_topology()
    fig_limit()
    print("ok")
