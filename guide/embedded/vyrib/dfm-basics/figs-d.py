# -*- coding: utf-8 -*-
# Фігури ДЕТАЛЬНОЇ статті dfm-basics-d.md. Не чіпає базові SVG (їх робить figs.py).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура D1: геометрія апертури трафарету — чому «площинне» відношення 0.66 ──
def fig_area_ratio():
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 32, "Чому паста тримається за стінки: площа дна проти площі стінок апертури",
                      size=15, bold=True))

    # ── ліворуч: 3D-ескіз апертури (паралелепіпед пасти в отворі трафарету)
    ox, oy = 120, 130           # передня верхня ліва
    L, Wd, T = 150, 90, 70      # довжина(вглиб), ширина, товщина трафарету (в px)
    dx, dy = 46, -34            # ізометричний зсув «углиб»
    # передня грань (дно × товщина, вид збоку) — світла паста
    frags.append(rect(ox, oy, Wd, T, fill="#f6d9b8", stroke="#b07a35", sw=1.5, rx=0))
    # верхня грань (дно апертури) — паралелограм
    top = ('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
           'fill="#fbe8cf" stroke="#b07a35" stroke-width="1.5"/>'
           % (ox, oy, ox + Wd, oy, ox + Wd + dx, oy + dy, ox + dx, oy + dy))
    frags.append(top)
    # права грань (стінка × товщина)
    side = ('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
            'fill="#eccaa0" stroke="#b07a35" stroke-width="1.5"/>'
            % (ox + Wd, oy, ox + Wd + dx, oy + dy, ox + Wd + dx, oy + dy + T, ox + Wd, oy + T))
    frags.append(side)
    # виноски розмірів
    frags.append(line(ox, oy + T + 14, ox + Wd, oy + T + 14, color=INK, sw=1.2))
    frags.append(text(ox + Wd / 2, oy + T + 30, "W (ширина дна)", size=11, color=INK))
    frags.append(line(ox - 16, oy, ox - 16, oy + T, color=INK, sw=1.2))
    frags.append(text(ox - 22, oy + T / 2 + 4, "T", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(ox - 22, oy + T / 2 + 20, "товщина", size=9, color=MUTED, anchor="end"))
    frags.append(line(ox + Wd + dx + 12, oy + dy, ox + Wd + dx + 12, oy + dy + T, color=MUTED, sw=1))
    frags.append(text(ox + Wd + dx + 40, oy + dy + 6, "L (довжина", size=10, color=MUTED))
    frags.append(text(ox + Wd + dx + 40, oy + dy + 20, "углиб)", size=10, color=MUTED))
    # стрілка «паста хоче вийти вниз»
    frags.append(arrow(ox + Wd / 2, oy + T + 44, ox + Wd / 2, oy + T + 70, color=FIELD, sw=2))
    frags.append(text(ox + Wd / 2, oy + T + 86, "паста має вийти на площадку", size=11, color=FIELD))
    # стрілки «стінки тримають»
    frags.append(arrow(ox - 4, oy + T / 2, ox + 22, oy + T / 2, color=POS, sw=1.8))
    frags.append(arrow(ox + Wd + 4, oy + T / 2, ox + Wd - 22, oy + T / 2, color=POS, sw=1.8))
    frags.append(text(ox + Wd / 2, oy + 20, "стінки тримають пасту", size=10, color=POS))

    # ── праворуч: формула й два випадки
    fx = 470
    frags.append(fitbox(fx, 96, 320, 66,
                        "AR = площа дна / площа стінок\n= (L·W) / (2·(L+W)·T)",
                        size=13, fill="#eef2f7", stroke=INK, sw=1.5))
    frags.append(text(fx + 160, 182, "виходить, коли дна більше за стінки:", size=12, color=INK))

    # шкала AR
    sx0, sx1 = fx + 20, fx + 300
    sy = 250
    frags.append(line(sx0, sy, sx1, sy, color=INK, sw=2))
    # зона браку / зона норми
    xthr = sx0 + (sx1 - sx0) * (0.66 - 0.4) / (1.2 - 0.4)
    frags.append(rect(sx0, sy - 10, xthr - sx0, 20, fill="#fdecea", stroke="none", sw=0))
    frags.append(rect(xthr, sy - 10, sx1 - xthr, 20, fill="#eafaf1", stroke="none", sw=0))
    frags.append(line(xthr, sy - 16, xthr, sy + 16, color=POS, sw=2))
    frags.append(text(xthr, sy - 22, "AR = 0.66", size=11, color=POS, bold=True))
    for val, lab in [(0.4, "0.4"), (0.66, ""), (1.0, "1.0"), (1.2, "1.2")]:
        xx = sx0 + (sx1 - sx0) * (val - 0.4) / (1.2 - 0.4)
        frags.append(line(xx, sy, xx, sy + 6, color=MUTED, sw=1))
        if lab:
            frags.append(text(xx, sy + 20, lab, size=10, color=MUTED))
    frags.append(text(sx0 + 4, sy + 40, "паста лишається в трафареті", size=10, color=POS, anchor="start"))
    frags.append(text(sx1 - 4, sy + 40, "паста чисто виходить", size=10, color=FIELD, anchor="end"))

    frags.append(fitbox(fx, sy + 66, 320, 62,
                        "Дрібнішає апертура → стінок відносно більше →\n"
                        "AR падає. Ліки: тонший трафарет (менше T).",
                        size=11, fill="#fbfbfb", stroke=MUTED, sw=1.2))
    render(os.path.join(OUT, 'area-ratio.svg'), W, H, *frags)


# ── Фігура D2: дві криві прогріву площадок і момент, що перекидає деталь ──────
def fig_thermal_race():
    W, H = 840, 470
    frags = []
    frags.append(text(W / 2, 30, "Гонка двох площадок: хто розплавиться перший — той і перекине деталь",
                      size=15, bold=True))

    # ── лівий графік: T(t) двох площадок
    gx0, gx1 = 70, 400
    gy0, gy1 = 90, 300           # верх/низ поля графіка
    frags.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.8))    # вісь часу
    frags.append(line(gx0, gy1, gx0, gy0, color=INK, sw=1.8))    # вісь T
    frags.append(text(gx1, gy1 + 18, "час у печі", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx0 - 6, gy0 - 4, "T", size=12, color=INK, anchor="end", bold=True))

    # лінія ліквідусу (де припій плавиться)
    liq_y = gy0 + 46
    frags.append(line(gx0, liq_y, gx1, liq_y, color=POS, sw=1.4, dash="6,4"))
    frags.append(text(gx1 - 4, liq_y - 6, "ліквідус (плавлення)", size=10, color=POS, anchor="end"))

    # площадка на тонкій доріжці — швидко гріється (мала стала часу)
    import math
    def curve(tau, col, sw=2.4):
        pts = []
        for i in range(0, 101):
            t = i / 100.0
            xx = gx0 + (gx1 - gx0) * t
            # нормована температура 0..1 з насиченням; менша tau — швидше
            frac = 1 - math.exp(-t / tau)
            yy = gy1 - (gy1 - gy0 - 8) * frac
            pts.append("%.1f,%.1f" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), col, sw)
    frags.append(curve(0.18, NEG))     # тонка доріжка — швидка
    frags.append(curve(0.55, FIELD))   # велика заливка — повільна
    frags.append(text(gx0 + 96, gy0 + 20, "площадка на", size=10, color=NEG, anchor="start"))
    frags.append(text(gx0 + 96, gy0 + 33, "тонкій доріжці", size=10, color=NEG, anchor="start"))
    frags.append(text(gx0 + 150, gy1 - 30, "площадка на суцільній міді", size=10, color=FIELD, anchor="start"))

    # моменти перетину ліквідусу
    # для tau=0.18: 1-exp(-t/tau)=frac_liq → t = -tau*ln(1-frac)
    frac_liq = (gy1 - liq_y) / (gy1 - gy0 - 8)
    t1 = -0.18 * math.log(1 - frac_liq)
    t2 = -0.55 * math.log(1 - frac_liq)
    x1 = gx0 + (gx1 - gx0) * t1
    x2 = gx0 + (gx1 - gx0) * t2
    for xx, col in [(x1, NEG), (x2, FIELD)]:
        frags.append(line(xx, liq_y, xx, gy1, color=col, sw=1, dash="3,3"))
        frags.append(circle(xx, liq_y, 4, fill=col, stroke=INK, sw=1))
    frags.append(line(x1, gy1 + 6, x2, gy1 + 6, color=INK, sw=1.4))
    frags.append(text((x1 + x2) / 2, gy1 + 20, "Δt — вікно перекидання", size=11, color=INK, bold=True))
    frags.append(text((x1 + x2) / 2, gy1 + 34, "один бік уже рідкий, другий ще твердий", size=9, color=MUTED))

    # ── правий бік: баланс моментів навколо припаяного кінця
    bx = 620
    by = 210
    frags.append(text(bx, 90, "Момент навколо припаяного кінця", size=12, bold=True))
    # площадка й точка опори
    frags.append(rect(bx - 90, by, 60, 12, fill="#c9c9c9", stroke=INK, sw=1))   # ліва (припаяна)
    frags.append(rect(bx + 30, by, 60, 12, fill="#c9c9c9", stroke=INK, sw=1))   # права
    piv = (bx - 60, by)
    frags.append(circle(piv[0], piv[1], 4, fill=POS, stroke=INK, sw=1))
    frags.append(text(piv[0], by + 26, "вісь повороту", size=10, color=POS))
    # тіло деталі, нахилене
    frags.append(('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#444" stroke-width="10"/>'
                  % (piv[0], piv[1], piv[0] + 96, piv[1] - 70)))
    # сила натягу вгору на дальньому кінці (плече h)
    frags.append(arrow(piv[0] + 96, piv[1] - 70, piv[0] + 96, piv[1] - 118, color=POS, sw=2.2))
    frags.append(text(piv[0] + 100, piv[1] - 100, "F_натягу", size=11, color=POS, anchor="start", bold=True))
    # вага вниз у центрі мас
    cm = (piv[0] + 48, piv[1] - 35)
    frags.append(arrow(cm[0], cm[1], cm[0], cm[1] + 44, color=NEG, sw=2.2))
    frags.append(text(cm[0] + 6, cm[1] + 30, "m·g", size=11, color=NEG, anchor="start", bold=True))
    frags.append(fitbox(bx - 96, by + 60, 240, 58,
                        "перекине, коли\nF_натягу·h > m·g·(L/2)",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'thermal-race.svg'), W, H, *frags)


# ── Фігура D3: панелізація — V-скрайб проти містків-перфорацій і стрес МЛКК ───
def fig_panelization():
    W, H = 840, 500
    frags = []
    frags.append(text(W / 2, 30, "Як плату відділяють від панелі — і чому це небезпечно для керамічних конденсаторів",
                      size=14, bold=True))

    # ── ліворуч зверху: переріз V-скрайбу (1/3–1/3–1/3)
    ax, ay, aw, ah = 70, 90, 300, 60
    frags.append(text(ax + aw / 2, ay - 12, "V-скрайб: два клини згори й знизу", size=12, bold=True, color=NEG))
    frags.append(rect(ax, ay, aw, ah, fill="#eaf4ec", stroke=INK, sw=1.5, rx=0))
    # верхній клин
    cxm = ax + aw / 2
    d = ah / 3
    frags.append(('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#ffffff" stroke=%s stroke-width="1.3"/>'
                  % (cxm - 16, ay, cxm + 16, ay, cxm, ay + d, '"%s"' % NEG)))
    frags.append(('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#ffffff" stroke=%s stroke-width="1.3"/>'
                  % (cxm - 16, ay + ah, cxm + 16, ay + ah, cxm, ay + ah - d, '"%s"' % NEG)))
    # позначки третин
    frags.append(line(ax + aw + 12, ay, ax + aw + 12, ay + d, color=MUTED, sw=1))
    frags.append(line(ax + aw + 12, ay + d, ax + aw + 12, ay + 2 * d, color=INK, sw=1.4))
    frags.append(line(ax + aw + 12, ay + 2 * d, ax + aw + 12, ay + ah, color=MUTED, sw=1))
    frags.append(text(ax + aw + 18, ay + d - 4, "⅓ верх", size=9, color=MUTED, anchor="start"))
    frags.append(text(ax + aw + 18, ay + 1.5 * d + 3, "⅓ перемичка", size=9, color=INK, anchor="start"))
    frags.append(text(ax + aw + 18, ay + 2.5 * d + 3, "⅓ низ", size=9, color=MUTED, anchor="start"))

    # ── ліворуч знизу: містки-перфорації (mouse bites) — вид зверху
    bx, by, bw = 70, 250, 300
    frags.append(text(bx + bw / 2, by - 12, "Місток із перфорацією (mouse bites)", size=12, bold=True, color=FIELD))
    frags.append(rect(bx, by, 130, 70, fill="#eaf4ec", stroke=FIELD, sw=1.5))       # плата A
    frags.append(rect(bx + 170, by, 130, 70, fill="#eaf4ec", stroke=FIELD, sw=1.5)) # плата B
    frags.append(text(bx + 65, by + 40, "плата", size=11, color=FIELD))
    frags.append(text(bx + 235, by + 40, "плата", size=11, color=FIELD))
    # містковий перешийок з отворами
    tab_x = bx + 130
    frags.append(rect(tab_x, by + 24, 40, 22, fill="#fbe8cf", stroke="#b07a35", sw=1.2, rx=0))
    for k in range(4):
        frags.append(circle(tab_x + 6 + k * 9, by + 35, 2.4, fill=BG, stroke="#b07a35", sw=1))
    frags.append(text(tab_x + 20, by + 62, "рядок дрібних отворів", size=9, color="#8a5a1f"))
    frags.append(text(tab_x + 20, by + 74, "→ ламається м'якше", size=9, color=FIELD))

    # ── праворуч: поле напруги від зламу й правильна орієнтація МЛКК
    rx = 470
    frags.append(text(rx + 170, 90, "Злам вигинає край → напруга біжить у плату", size=12, bold=True, color=POS))
    # край плати
    edge_y = 130
    frags.append(rect(rx, edge_y, 340, 150, fill="#eaf4ec", stroke=INK, sw=1.5))
    frags.append(line(rx, edge_y, rx + 340, edge_y, color=POS, sw=3))
    frags.append(text(rx + 170, edge_y - 8, "лінія зламу (край)", size=10, color=POS))
    # дуги напруги, що згасають углиб
    for i, r in enumerate((26, 54, 82)):
        op = 0.9 - i * 0.28
        frags.append('<path d="M %.0f %.0f A %.0f %.0f 0 0 0 %.0f %.0f" fill="none" stroke="%s" stroke-width="1.4" opacity="%.2f"/>'
                     % (rx + 170 - r, edge_y, r, r, rx + 170 + r, edge_y, POS, op))
    frags.append(text(rx + 170, edge_y + 96, "стрес спадає з відстанню", size=10, color=MUTED))

    # МЛКК паралельно краю (погано) і перпендикулярно (добре)
    # поганий: довга вісь уздовж краю → обидва термінали ловлять вигин
    mb_y = edge_y + 44
    frags.append(rect(rx + 26, mb_y, 46, 16, fill="#f6c9c2", stroke=POS, sw=1.4))
    frags.append(text(rx + 49, mb_y + 30, "‖ краю: тріскає", size=9, color=POS))
    # добрий: далі й перпендикулярно
    frags.append(rect(rx + 250, edge_y + 96, 16, 40, fill="#cdeeda", stroke=FIELD, sw=1.4))
    frags.append(text(rx + 258, edge_y + 150, "⟂ і далі: цілий", size=9, color=FIELD))
    # мітка відступу
    frags.append(line(rx + 250, edge_y, rx + 250, edge_y + 96, color=FIELD, sw=1, dash="4,3"))
    frags.append(text(rx + 300, edge_y + 48, "≥ 3–4 мм", size=10, color=FIELD, anchor="start", bold=True))

    frags.append(fitbox(rx, edge_y + 168, 340, 58,
                        "Правило: крихкі МЛКК — далі від лінії поділу й довгою\n"
                        "віссю ПОПЕРЕК неї, щоб вигин не розтягував кераміку.",
                        size=11, fill="#fbfbfb", stroke=MUTED, sw=1.2))
    render(os.path.join(OUT, 'panelization-stress.svg'), W, H, *frags)


# ── Фігура D4: мапа стандартів IPC по стадіях від голої плати до готового виробу
def fig_ipc_map():
    W, H = 860, 400
    frags = []
    frags.append(text(W / 2, 30, "Хто чим керує: стандарти IPC вздовж шляху від голої плати до готового виробу",
                      size=15, bold=True))

    # стрічка стадій
    stages = ["Проєкт\nплати", "Посадкові\nмісця", "Гола\nплата", "Складання\n(процес)", "Приймання\nвиробу"]
    n = len(stages)
    bw, gap = 130, 24
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 96
    bh = 60
    for i, name in enumerate(stages):
        x = x0 + i * (bw + gap)
        frags.append(fitbox(x, ytop, bw, bh, name, size=13, bold=True,
                            fill="#eef2f7", stroke=INK, sw=1.6))
        if i < n - 1:
            frags.append(arrow(x + bw + 2, ytop + bh / 2, x + bw + gap - 2, ytop + bh / 2, color=INK, sw=2))

    # стандарт під кожною стадією
    stds = [
        ("IPC-2221", "загальні правила\nпроєкту: зазори,\nширини, отвори", POS),
        ("IPC-7351", "розміри посадкових\nмісць під SMD", FIELD),
        ("IPC-A-600", "приймання ГОЛОЇ\nдрукованої плати", NEG),
        ("IPC-7525", "апертури трафарету\n(відношення 0.66)", "#8a5a1f"),
        ("IPC-A-610", "приймання зборки;\nКлас 1 / 2 / 3", INK),
    ]
    yb = ytop + bh + 40
    for i, (code, desc, col) in enumerate(stds):
        x = x0 + i * (bw + gap)
        frags.append(line(x + bw / 2, ytop + bh, x + bw / 2, yb - 6, color=col, sw=1.4, dash="4,4"))
        frags.append(fitbox(x, yb, bw, 92, code + "\n" + desc, size=11, bold=False,
                            fill="#fbfbfb", stroke=col, sw=1.4))

    frags.append(fitbox(x0, yb + 108, total, 40,
                        "Наскрізь: IPC-A-610 задає КЛАС надійності (1 споживче · 2 промислове · 3 авіа/мед), "
                        "а решта стандартів каже, ЯК саме досягти його на кожній стадії.",
                        size=12, fill="#fdf6ec", stroke=POS, sw=1.5))
    render(os.path.join(OUT, 'ipc-map.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_area_ratio()
    fig_thermal_race()
    fig_panelization()
    fig_ipc_map()
    print("ok")
