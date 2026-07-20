# -*- coding: utf-8 -*-
"""Фігури до теми «Гіпот-тест: перевірка ізоляції мережевих пристроїв».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT      = "#fbeee6"   # заливка «гарячого» первинного боку
HOTF     = "#eaf0fd"   # заливка «холодного» вторинного боку
EARTHF   = "#eef6ef"   # заливка землі
AMBER    = "#e0a32e"


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s stroke-linejoin="round" stroke-linecap="round"/>'
            % (p, color, sw, d))


# ── 1. Карта ізоляції: два боки, три містки, земля, дві проби ─────────────────
def fig_isolation_map():
    W, H = 900, 480
    f = [text(W / 2, 32, "Карта ізоляції мережевого приладу: де проходить рубіж", size=17, bold=True)]

    # первинний бік (гарячий)
    f.append(rect(55, 100, 300, 225, fill=HOT, stroke=POS, sw=2, rx=12))
    f.append(text(205, 132, "Первинний бік", size=14, bold=True, color=POS))
    f.append(mtext(205, 162, "мережа 230 В\n→ 325 В=", size=12, color=INK, lh=1.35))
    f.append(text(205, 250, "НЕБЕЗПЕЧНО", size=13, bold=True, color=POS))

    # вторинний бік (безпечний)
    f.append(rect(545, 100, 300, 225, fill=HOTF, stroke=NEG, sw=2, rx=12))
    f.append(text(695, 132, "Вторинний бік", size=14, bold=True, color=NEG))
    f.append(mtext(695, 162, "5 В USB, вихід\nдотик рукою", size=12, color=INK, lh=1.35))
    f.append(text(695, 250, "БЕЗПЕЧНО", size=13, bold=True, color=FIELD))

    # рубіж ізоляції — пунктир між боками
    f.append(text(450, 84, "рубіж ізоляції", size=12.5, bold=True, color=MUTED))
    f.append(line(450, 92, 450, 332, color=INK, sw=1.6, dash="6 5"))

    # три містки, що перетинають рубіж
    bridges = [("трансформатор", 152), ("оптопара", 217), ("Y-конденсатор", 282)]
    for name, cy in bridges:
        f.append(line(355, cy, 375, cy, color=MUTED, sw=1.6))
        f.append(line(525, cy, 545, cy, color=MUTED, sw=1.6))
        f.append(fitbox(375, cy - 17, 150, 34, name, size=11.5,
                        fill=BG, stroke=LINE, sw=1.5, rx=8))

    # захисне заземлення / корпус
    f.append(rect(55, 352, 790, 50, fill=EARTHF, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(450, 382, "захисне заземлення · металевий корпус (Клас I)", size=12.5, bold=True, color=FIELD))
    f.append(line(695, 325, 695, 352, color=FIELD, sw=1.8))

    # легенда двох проб (окремо, під усім — без накладань)
    f.append(arrow(80, 432, 120, 432, color=POS, sw=2.4))
    f.append(text(128, 436, "гіпот: висока напруга поперек рубежу — первинний ↔ вторинний і ↔ корпус",
                  size=11.5, color=INK, anchor="start"))
    f.append(arrow(80, 458, 120, 458, color=FIELD, sw=2.4))
    f.append(text(128, 462, "заземлювальний зв'язок: великий струм — корпус ↔ контакт заземлення",
                  size=11.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "isolation-map.svg"), W, H, *f)


# ── 2. Профіль проби в часі: наростання-витримка-скид, прохід vs провал ───────
def fig_ramp_trip():
    W, H = 880, 470
    f = [text(W / 2, 30, "Проба напругою в часі: той самий профіль — дві долі", size=16.5, bold=True)]

    x0, x1, x2, x3 = 110, 240, 650, 770      # старт, кінець наростання, кінець витримки, кінець скиду
    xt = 430                                  # мить пробою бракованого виробу

    # верхня панель: напруга
    f.append(rect(70, 58, 740, 150, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(440, 52, "Напруга проби", size=12.5, bold=True))
    f.append(text(92, 130, "U", size=13, bold=True, color=MUTED))
    vbase, vtop = 185, 82
    f.append(line(110, vtop, 780, vtop, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(795, vtop + 4, "V_проб", size=11, color=MUTED, anchor="start"))
    f.append(polyline([(x0, vbase), (x1, vtop), (x2, vtop), (x3, vbase), (780, vbase)], color=INK, sw=2.6))

    # нижня панель: струм витоку
    f.append(rect(70, 250, 740, 168, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(440, 240, "Струм витоку", size=12.5, bold=True))
    f.append(text(92, 336, "I", size=13, bold=True, color=MUTED))
    ibase = 404
    # поріг струму
    f.append(line(110, 332, 780, 332, color=POS, sw=1.3, dash="5 4"))
    f.append(text(795, 336, "поріг", size=11, color=POS, anchor="start"))
    # прохід — рівний низький виток
    f.append(polyline([(x0, ibase), (x1, 392), (x2, 392), (x3, ibase), (780, ibase)], color=FIELD, sw=2.6))
    f.append(text(560, 380, "прохід — рівний виток", size=11.5, bold=True, color=FIELD))
    # провал — стрибок на пробої
    f.append(polyline([(x0, ibase), (x1, 392), (xt - 8, 390), (xt, 268)], color=POS, sw=2.8))
    f.append(text(xt + 10, 300, "пробій → стрибок", size=11.5, bold=True, color=POS, anchor="start"))

    # мить розриву — вертикаль крізь обидві панелі
    f.append(line(xt, 58, xt, 418, color=POS, sw=1.2, dash="3 3"))

    # фази під нижньою панеллю
    f.append(line(x1, 250, x1, 418, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(x2, 250, x2, 418, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text((x0 + x1) / 2, 440, "наростання", size=11, color=MUTED))
    f.append(text((x1 + x2) / 2, 440, "витримка (60 с / 1 с)", size=11, color=MUTED))
    f.append(text((x2 + x3) / 2 + 8, 440, "скид", size=11, color=MUTED))

    render(os.path.join(IMG, "ramp-trip.svg"), W, H, *f)


# ── 3. Струм крізь Y-конденсатор: змінна vs постійна проба ────────────────────
def fig_ac_dc_leakage():
    W, H = 880, 470
    f = [text(W / 2, 30, "Струм крізь Y-конденсатор: чому постійна проба чутливіша", size=16, bold=True)]

    px0, px1 = 100, 600      # межі осі часу в панелях
    tx0 = 632                # ліва межа текстової колонки

    # ── верхня панель: змінна проба ──
    f.append(rect(70, 58, 545, 150, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(342, 52, "Змінна проба", size=12.5, bold=True, color=NEG))
    f.append(text(90, 138, "I", size=13, bold=True, color=MUTED))
    mid = 138
    amp = 40
    pts = [(x, mid - amp * math.sin((x - px0) / 34.0)) for x in range(px0, px1 + 1, 4)]
    f.append(polyline(pts, color=NEG, sw=2.4))
    # поріг вище піка
    f.append(line(px0, mid - amp - 22, px1, mid - amp - 22, color=POS, sw=1.3, dash="5 4"))
    f.append(text(px0 + 6, mid - amp - 28, "поріг (високий)", size=10.5, color=POS, anchor="start"))
    f.append(text(px1 - 6, mid + amp + 22, "≈ 2.2 мА весь час", size=10.5, color=NEG, anchor="end"))
    # пояснення праворуч
    f.append(fitbox(tx0, 78, 236, 110,
                    "Ємнісний струм тече\nрівно й великий.\nПоріг мусить стояти\nВИЩЕ за 2.2 мА —\nдрібний виток тоне\nпід ним.",
                    size=11, fill="#f7f9fb", stroke="#c9d3dc", sw=1.4, rx=10))

    # ── нижня панель: постійна проба ──
    f.append(rect(70, 250, 545, 150, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(342, 244, "Постійна проба", size=12.5, bold=True, color=FIELD))
    f.append(text(90, 330, "I", size=13, bold=True, color=MUTED))
    dbase = 372
    # кидок заряду й спад
    dpts = [(px0, dbase), (px0 + 12, 278)]
    for x in range(px0 + 12, px1 + 1, 4):
        dpts.append((x, dbase - 96 * math.exp(-(x - (px0 + 12)) / 26.0)))
    f.append(polyline(dpts, color=FIELD, sw=2.6))
    # низький поріг
    f.append(line(px0, dbase - 26, px1, dbase - 26, color=POS, sw=1.3, dash="5 4"))
    f.append(text(px0 + 6, dbase - 32, "поріг (низький)", size=10.5, color=POS, anchor="start"))
    f.append(text(px0 + 40, 268, "кидок заряду", size=10.5, color=FIELD, anchor="start"))
    f.append(text(px1 - 6, dbase + 18, "далі — лише опірний виток (мкА)", size=10.5, color=FIELD, anchor="end"))
    # пояснення праворуч
    f.append(fitbox(tx0, 268, 236, 110,
                    "Заряд минає одним\nкидком, тоді лишається\nтільки опірний виток.\nПоріг можна опустити —\nчутливо до слабкої\nізоляції.",
                    size=11, fill="#f7f9fb", stroke="#c9d3dc", sw=1.4, rx=10))

    f.append(text(342, 424, "час →", size=11, color=MUTED))

    render(os.path.join(IMG, "ac-dc-leakage.svg"), W, H, *f)


# ── 4. Поле, а не напруга: E = U/d проти діелектричної міцності ────────────────
def fig_field_gap():
    W, H = 920, 440
    f = [text(W / 2, 30, "Поле, а не напруга, вирішує: E = U/d проти межі діелектрика", size=16, bold=True)]

    # ── ліворуч: два електроди із зазором d і полем E ──
    ex0, ex1 = 120, 300
    yt, yb = 132, 300
    f.append(rect(ex0, yt - 12, ex1 - ex0, 12, fill=POS, stroke=POS, sw=1.5, rx=3))
    f.append(rect(ex0, yb, ex1 - ex0, 12, fill=NEG, stroke=NEG, sw=1.5, rx=3))
    for gx in range(ex0 + 26, ex1 - 5, 44):
        f.append(arrow(gx, yt + 4, gx, yb - 3, color=FIELD, sw=2.2))
    f.append(line(ex0 - 24, yt, ex0 - 24, yb, color=MUTED, sw=1.6))
    f.append(text(ex0 - 32, (yt + yb) / 2 + 5, "U", size=15, bold=True, color=INK, anchor="end"))
    f.append(line(ex1 + 22, yt, ex1 + 22, yb, color=MUTED, sw=1.4, dash="4 3"))
    f.append(text(ex1 + 32, (yt + yb) / 2 + 5, "d", size=15, bold=True, italic=True, color=INK, anchor="start"))
    f.append(text((ex0 + ex1) / 2, yt - 22, "електрод (+)", size=11, color=MUTED))
    f.append(text((ex0 + ex1) / 2, yb + 34, "електрод (−)", size=11, color=MUTED))
    f.append(text((ex0 + ex1) / 2, 362, "E = U / d", size=18, bold=True, color=FIELD))
    f.append(text((ex0 + ex1) / 2, 390, "поле в зазорі", size=11, color=MUTED))

    # ── праворуч: графік E(d) проти межі ──
    gx0, gx1 = 505, 885
    gyt, gyb = 92, 362
    dmax, Emax = 2.5, 6.0

    def px(d):
        return gx0 + (d / dmax) * (gx1 - gx0)

    def py(E):
        return gyb - (min(E, Emax) / Emax) * (gyb - gyt)

    f.append(line(gx0, gyt, gx0, gyb, color=MUTED, sw=1.5))
    f.append(line(gx0, gyb, gx1, gyb, color=MUTED, sw=1.5))
    f.append(text(gx0 - 6, gyt - 4, "E, кВ/мм", size=11, color=MUTED, anchor="end"))
    f.append(text(gx1, gyb + 24, "d, мм", size=11, color=MUTED, anchor="end"))
    f.append(line(gx0, py(3), gx1, py(3), color=POS, sw=1.6, dash="6 4"))
    f.append(text(gx1 - 4, py(3) - 8, "3 кВ/мм — межа повітря", size=11, bold=True, color=POS, anchor="end"))
    cpts = []
    d = 0.26
    while d <= dmax + 1e-9:
        cpts.append((px(d), py(1.5 / d)))
        d += 0.02
    f.append(polyline(cpts, color=FIELD, sw=2.6))
    f.append(text(px(1.12), py(1.5 / 1.12) - 14, "E = U/d  (U = 1.5 кВ)", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(line(px(0.5), py(3), px(0.5), gyb, color=MUTED, sw=1.2, dash="3 3"))
    f.append(circle(px(0.5), py(3), 4, fill=POS, stroke=POS, sw=1))
    f.append(text(px(0.5) + 8, gyb - 10, "d = U/E ≈ 0.5 мм", size=11, color=INK, anchor="start"))
    f.append(text(px(0.4), py(4.7), "пробій", size=12.5, bold=True, color=POS))
    f.append(text(px(1.75), py(1.35), "тримає", size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "field-gap.svg"), W, H, *f)


# ── 5. Пік вирішує напругу; ємність — поріг струму ────────────────────────────
def fig_peak_leakage():
    W, H = 920, 470
    f = [text(W / 2, 30, "Пік вирішує напругу проби, ємність — поріг струму", size=16, bold=True)]

    ax0, ax1 = 95, 615
    k = 520.0 / (3 * math.pi)        # рівно 1.5 періоду: кінці на осі
    tx = 648

    # ── верхня панель: напруга ──
    f.append(rect(70, 56, 560, 150, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(350, 50, "Напруга проби (змінна)", size=12.5, bold=True, color=NEG))
    mid, amp = 140, 38
    vpts = [(x, mid - amp * math.sin((x - ax0) / k)) for x in range(ax0, ax1 + 1, 3)]
    f.append(polyline(vpts, color=NEG, sw=2.4))
    f.append(line(ax0, mid - amp, ax1, mid - amp, color=POS, sw=1.2, dash="5 4"))
    f.append(text(ax0 + 2, mid - amp - 6, "V_пік = √2·V_дію = 2121 В", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(line(ax0, mid - amp * 0.707, ax1, mid - amp * 0.707, color=MUTED, sw=1.1, dash="4 4"))
    f.append(text(ax1 - 2, mid - amp * 0.707 + 14, "V_дію = 1500 В", size=10.5, color=MUTED, anchor="end"))
    xcrest = ax0 + k * (math.pi / 2)
    f.append(circle(xcrest, mid - amp, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(xcrest + 8, mid + 4, "тут поле найбільше", size=10, color=POS, anchor="start"))
    f.append(fitbox(tx, 74, 244, 114,
                    "Ізоляція пробивається\nна ПІКУ, не на\nдіючому. DC-проба\nмусить стояти на\nцьому піку весь час:\nV_пост = √2·V_змін.",
                    size=11, fill="#f7f9fb", stroke="#c9d3dc", sw=1.4, rx=10))

    # ── нижня панель: ємнісний струм ──
    f.append(rect(70, 268, 560, 150, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(350, 262, "Ємнісний струм крізь Y-конденсатор", size=12.5, bold=True, color=FIELD))
    mid2, amp2 = 345, 36
    ipts = [(x, mid2 - amp2 * math.cos((x - ax0) / k)) for x in range(ax0, ax1 + 1, 3)]
    f.append(polyline(ipts, color=FIELD, sw=2.4))
    f.append(line(ax0, mid2 - amp2 * 0.707, ax1, mid2 - amp2 * 0.707, color=POS, sw=1.2, dash="5 4"))
    f.append(text(ax1 - 2, mid2 - amp2 * 0.707 - 7, "I = 2πf·C·U ≈ 2.2 мА", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(fitbox(tx, 286, 244, 114,
                    "Тече крізь СПРАВНИЙ\nвиріб (випереджає\nнапругу на 90°). Поріг\nмусить бути ВИЩЕ —\nтож змінна проба\nсліпне до опірного\nвитоку.",
                    size=11, fill="#f7f9fb", stroke="#c9d3dc", sw=1.4, rx=10))

    f.append(text(350, 442, "час →", size=11, color=MUTED))

    render(os.path.join(IMG, "peak-leakage.svg"), W, H, *f)


# ── 6. Автомат станів станції гіпоту: послідовність проб і рейка помилок ───────
def fig_hipot_fsm():
    W, H = 1010, 430
    f = [text(W / 2, 30, "Автомат станції гіпоту: послідовність проб і спільний розряд", size=16.5, bold=True)]

    def node(cx, cy, w, h, title, sub, fill, stroke, tcolor=INK):
        x, y = cx - w / 2, cy - h / 2
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=11)
        if sub:
            out += text(cx, cy - 4, title, size=12.5, bold=True, color=tcolor)
            out += text(cx, cy + 15, sub, size=10.5, color=MUTED)
        else:
            out += text(cx, cy + 5, title, size=12.5, bold=True, color=tcolor)
        return out

    # верхній ряд — головна послідовність
    ytop = 100
    idle = (110, ytop); gb = (330, ytop); ir = (550, ytop); hp = (770, ytop)
    f.append(node(*idle, 150, 62, "IDLE", "два-руки + кожух", BG, MUTED))
    f.append(node(*gb, 150, 62, "ЗАЗЕМЛ. ЗВ'ЯЗОК", "25 А · R<0.1 Ω", HOTF, NEG))
    f.append(node(*ir, 150, 62, "ОПІР ІЗОЛЯЦІЇ", "500 В= · R>10 MΩ", HOTF, NEG))
    f.append(node(*hp, 150, 62, "ГІПОТ", "нарост·витримка", HOT, POS))

    for (a, b) in [(idle, gb), (gb, ir), (ir, hp)]:
        f.append(arrow(a[0] + 75, ytop, b[0] - 75, ytop, color=INK, sw=2.2))

    # рейка помилок — червона пунктирна шина під рядом
    ybus = 172
    f.append(line(230, ybus, 845, ybus, color=POS, sw=1.6, dash="6 5"))
    f.append(text(560, ytop + 31 + 10, "будь-яка помилка · відкритий кожух · тайм-аут",
                  size=10.5, color=POS))
    for cx in (gb[0], ir[0], hp[0]):
        f.append(arrow(cx, ytop + 31 + 19, cx, ybus, color=POS, sw=1.8))

    # ABORT · РОЗРЯД · PASS/FAIL
    ab = (230, 305); dis = (560, 305); ok = (890, 250); bad = (890, 360)
    f.append(line(230, ybus, 230, ab[1] - 31, color=POS, sw=1.6, dash="6 5"))
    f.append(arrow(230, ab[1] - 31.1, 230, ab[1] - 31, color=POS, sw=1.8))
    f.append(node(*ab, 150, 60, "ABORT", "негайно HV OFF", "#fdecea", POS, POS))
    f.append(node(*dis, 185, 62, "РОЗРЯД", "стекти до <50 В (вимір!)", EARTHF, FIELD))
    f.append(node(*ok, 150, 58, "PASS", "", "#eaf7ee", FIELD, FIELD))
    f.append(node(*bad, 150, 58, "FAIL", "", "#fdecea", POS, POS))

    f.append(arrow(ab[0] + 75, 305, dis[0] - 93, 305, color=POS, sw=2.0))
    f.append(arrow(hp[0] - 40, ytop + 31, dis[0] + 40, dis[1] - 31, color=FIELD, sw=2.2))
    f.append(text(692, 232, "витримка ок", size=10, color=FIELD))
    f.append(arrow(dis[0] + 93, 292, ok[0] - 75, ok[1] + 6, color=FIELD, sw=2.2))
    f.append(arrow(dis[0] + 93, 318, bad[0] - 75, bad[1] - 6, color=POS, sw=2.2))
    f.append(text(742, 260, "успіх", size=10, color=FIELD, anchor="start"))
    f.append(text(742, 352, "після ABORT", size=10, color=POS, anchor="start"))

    render(os.path.join(IMG, "hipot-fsm.svg"), W, H, *f)


# ── 7. Дві петлі: повільний автомат і швидкий ISR-тригер ──────────────────────
def fig_trip_arch():
    W, H = 980, 430
    f = [text(W / 2, 30, "Дві петлі керування: автомат веде послідовність, ISR ловить пробій", size=15.5, bold=True)]

    # ліва колонка — повільний автомат
    f.append(rect(38, 66, 250, 300, fill="#f7f9fb", stroke="#c9d3dc", sw=1.8, rx=12))
    f.append(text(163, 92, "Повільна петля", size=13, bold=True, color=NEG))
    f.append(text(163, 112, "автомат станів, головний цикл", size=10.5, color=MUTED))
    f.append(mtext(163, 150,
                   ["• веде фази проби", "• читає прапорці ISR", "• таймери витримки",
                    "• журнал прохід/провал"], size=11.5, color=INK, lh=1.55, anchor="middle"))
    f.append(fitbox(78, 300, 170, 44, "такт ~1 мс\n(не критичний до µs)",
                    size=11, fill=BG, stroke="#c9d3dc", sw=1.4, rx=9))

    # права область — швидкий ISR-ланцюг
    f.append(text(640, 92, "Швидка петля — переривання АЦП", size=13, bold=True, color=POS))

    adc = (430, 150)
    f.append(rect(adc[0] - 78, adc[1] - 28, 156, 56, fill=HOT, stroke=POS, sw=1.8, rx=10))
    f.append(text(adc[0], adc[1] - 4, "АЦП струму", size=12, bold=True))
    f.append(text(adc[0], adc[1] + 14, "10 кГц · 100 мкс", size=10.5, color=MUTED))

    c1 = (650, 118); c2 = (650, 190)
    f.append(fitbox(c1[0] - 92, c1[1] - 24, 184, 48, "|I| > поріг?", size=12,
                    fill=BG, stroke=POS, sw=1.6, rx=9))
    f.append(fitbox(c2[0] - 92, c2[1] - 24, 184, 48, "|I[n]−I[n−1]| > дуга?", size=12,
                    fill=BG, stroke=POS, sw=1.6, rx=9))
    f.append(arrow(adc[0] + 78, adc[1] - 6, c1[0] - 92, c1[1] + 4, color=INK, sw=1.8))
    f.append(arrow(adc[0] + 78, adc[1] + 6, c2[0] - 92, c2[1] - 4, color=INK, sw=1.8))

    orn = (812, 154)
    f.append(circle(orn[0], orn[1], 30, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(orn[0], orn[1] + 5, "≥1", size=14, bold=True, color=POS))
    f.append(arrow(c1[0] + 92, c1[1] + 2, orn[0] - 22, orn[1] - 12, color=POS, sw=1.8))
    f.append(arrow(c2[0] + 92, c2[1] - 2, orn[0] - 22, orn[1] + 12, color=POS, sw=1.8))

    hv = (700, 300)
    f.append(rect(hv[0] - 128, hv[1] - 30, 256, 60, fill=POS, stroke=POS, sw=2, rx=11))
    f.append(text(hv[0], hv[1] - 6, "HV OFF — реле + GPIO", size=12.5, bold=True, color=BG))
    f.append(text(hv[0], hv[1] + 15, "+ прапорець trip для автомата", size=10.5, color="#f7d9d4"))
    f.append(arrow(orn[0], orn[1] + 30, hv[0] + 20, hv[1] - 30, color=POS, sw=2.2))

    # зворотний прапорець до автомата (по низу)
    f.append(line(hv[0] - 128, hv[1] + 18, 163, hv[1] + 18, color=MUTED, sw=1.6, dash="5 4"))
    f.append(arrow(163, hv[1] + 18, 163, 348, color=MUTED, sw=1.6))
    f.append(text(300, hv[1] + 34, "прапорець → автомат завершує пробу як FAIL",
                  size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "trip-arch.svg"), W, H, *f)


# ── 8. Часова вісь народження проби: три течії сходяться (для hist-вставки) ────
def fig_birth_timeline():
    W, H = 880, 648
    f = []

    # легенда трьох течій (один рядок, з запасом по ширині)
    f.append(circle(74, 56, 7, fill=NEG, stroke=NEG))
    f.append(text(88, 60, "інженерія високих напруг", size=11.5, color=INK, anchor="start"))
    f.append(circle(352, 56, 7, fill=POS, stroke=POS))
    f.append(text(366, 60, "публічний страх удару", size=11.5, color=INK, anchor="start"))
    f.append(circle(600, 56, 7, fill=FIELD, stroke=FIELD))
    f.append(text(614, 60, "інституції та стандарти", size=11.5, color=INK, anchor="start"))

    # вертикальний хребет часу
    sx = 176
    f.append(line(sx, 92, sx, 606, color=MUTED, sw=2.2))

    events = [
        ("1886", NEG,   False, "Грейт-Баррінгтон: передача змінним струмом під ~3000 В (Стенлі)"),
        ("1890", POS,   False, "Електричний стілець (Кеммлер) — публічний жах перед струмом"),
        ("1893", FIELD, False, "Виставка в Чикаго: Мерілл перевіряє Палац електрики"),
        ("1894", FIELD, False, "Underwriters' Electrical Bureau — лабораторія від страховиків"),
        ("1901", FIELD, False, "Інкорпорація як Underwriters' Laboratories (UL)"),
        ("1906", FIELD, False, "IEC засновано в Лондоні · служба маркування UL"),
        ("1914", MUTED, True,  "Кодекс котлів ASME: проба тиском 1.3× — рідня пробі напругою"),
        ("нині", FIELD, False, "IEC 60950 / 62368: 2·U + 1000 В, гіпот на кожному виробі"),
    ]
    y0, pitch = 122, 66
    for i, (yr, col, hollow, label) in enumerate(events):
        cy = y0 + i * pitch
        f.append(text(sx - 26, cy + 5, yr, size=13, bold=True,
                      color=(MUTED if hollow else col), anchor="end"))
        f.append(line(sx, cy, sx + 26, cy, color=MUTED, sw=1.4))
        if hollow:
            f.append(circle(sx, cy, 6.5, fill=BG, stroke=MUTED, sw=2.2))
        else:
            f.append(circle(sx, cy, 7.5, fill=col, stroke=col, sw=1))
        f.append(fitbox(sx + 26, cy - 19, 650, 38, label, size=12.5, pad=10,
                        fill="#f7f9fb", stroke="#c9d3dc", sw=1.4, rx=9))

    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *f,
           title="Як зійшлися три течії в пробу ізоляції напругою")


if __name__ == "__main__":
    fig_isolation_map()
    fig_ramp_trip()
    fig_ac_dc_leakage()
    fig_field_gap()
    fig_peak_leakage()
    fig_hipot_fsm()
    fig_trip_arch()
    fig_birth_timeline()
    print("OK: 8 SVG у", IMG)
