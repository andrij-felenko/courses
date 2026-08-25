# -*- coding: utf-8 -*-
"""Фігури до статті «GaN-транзистор у силовій електроніці». Запуск: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GAN = "#1e8a5a"      # GaN / 2DEG — зелений (провідний канал)
GANFILL = "#e6f4ec"
ALGAN = "#d9c26a"    # бар'єр AlGaN
ALFILL = "#f6efd3"
SUB = "#c8cdd4"      # підкладка
SUBFILL = "#eceef1"
METAL = "#8a8f96"    # контакти


# ── Фігура 1: латеральний GaN-HEMT (переріз) ────────────────────────────────
def fig_structure():
    W, H = 780, 430
    f = []
    # межі стека
    sx, sw = 90, 500          # ліва межа, ширина стека
    # шари (зверху вниз): контакти над AlGaN; AlGaN; GaN; підкладка
    y_algan, h_algan = 168, 22
    y_gan,   h_gan   = 190, 92
    y_sub,   h_sub   = 282, 52
    y_2deg = y_gan + 4        # 2DEG — при верхній межі GaN

    # підкладка
    f.append(rect(sx, y_sub, sw, h_sub, fill=SUBFILL, stroke=SUB, sw=1.5, rx=0))
    f.append(text(sx + sw/2, y_sub + h_sub/2 + 5, "Підкладка (кремній)", size=15, color=MUTED))
    # GaN буфер
    f.append(rect(sx, y_gan, sw, h_gan, fill=GANFILL, stroke=GAN, sw=1.5, rx=0))
    f.append(text(sx + sw/2, y_gan + h_gan/2 + 22, "GaN (буфер)", size=15, color=GAN, bold=True))
    # AlGaN бар'єр (тонкий)
    f.append(rect(sx, y_algan, sw, h_algan, fill=ALFILL, stroke=ALGAN, sw=1.5, rx=0))

    # 2DEG — яскрава зелена лінія при межі
    f.append(line(sx + 20, y_2deg, sx + sw - 20, y_2deg, color=GAN, sw=4.5))
    # струм тече вбік у 2DEG
    f.append(arrow(sx + 70, y_2deg + 20, sx + sw - 70, y_2deg + 20, color=GAN, sw=2.4))
    f.append(text(sx + sw/2, y_2deg + 40, "струм тече вбік у шарі електронів", size=12.5, color=GAN))

    # контакти згори (S, G, D)
    cw = 58
    xs = sx + 30
    xg = sx + sw/2 - cw/2
    xd = sx + sw - 30 - cw
    for cx, lab in [(xs, "витік S"), (xg, "затвор G"), (xd, "стік D")]:
        f.append(rect(cx, 138, cw, 30, fill="#e9ebee", stroke=METAL, sw=1.5, rx=3))
        f.append(text(cx + cw/2, 130, lab, size=13, color=INK, bold=True))
    # витік/стік дістають до 2DEG (омічні), затвор сидить на AlGaN
    f.append(line(xs + cw/2, 168, xs + cw/2, y_2deg, color=METAL, sw=2))
    f.append(line(xd + cw/2, 168, xd + cw/2, y_2deg, color=METAL, sw=2))

    # права підпис-колонка з винесеннями (добре рознесені по вертикалі)
    lx = sx + sw + 22
    # AlGaN
    f.append(line(sx + sw, y_algan + h_algan/2, lx - 8, y_algan + h_algan/2, color=ALGAN, sw=1.4))
    f.append(text(lx, y_algan + h_algan/2 + 5, "AlGaN — тонкий бар'єр", size=13, color="#a8842e", anchor="start"))
    # 2DEG (нижче, щоб не злипалось)
    f.append(line(sx + sw - 20, y_2deg, lx - 8, y_2deg + 42, color=GAN, sw=1.4))
    f.append(text(lx, y_2deg + 46, "2DEG — рухливий", size=13, color=GAN, anchor="start", bold=True))
    f.append(text(lx, y_2deg + 63, "шар електронів", size=13, color=GAN, anchor="start", bold=True))

    # нижній акцент
    box, bw, bh = textbox(W/2, 400, "немає ні вертикальної дрейфової області, ні p-n переходу на шляху струму",
                          size=13.5, pad=11, fill="#eef6f1", stroke=GAN, color="#146")
    f.append(box)

    render(os.path.join(IMG, "hemt-structure.svg"), W, H, *f,
           title="Латеральний GaN-HEMT: канал — шар електронів на межі кристалів")


# ── Фігура 2: заряд за цикл — кремній проти GaN ─────────────────────────────
def fig_charge():
    W, H = 780, 440
    f = []
    base = 300                     # базова лінія стовпчиків
    groups = [("Qg", "заряд затвора", 175, 46),
              ("Qoss", "вихідний заряд", 150, 40),
              ("Qrr", "зворотне\nвідновлення", 120, 0)]
    gx = [170, 385, 600]
    bw, gap = 46, 16
    # легенда
    f.append(rect(W - 250, 70, 16, 16, fill="#cdd2d8", stroke=METAL, sw=1.4, rx=3))
    f.append(text(W - 228, 83, "кремній (Si)", size=13, color=INK, anchor="start"))
    f.append(rect(W - 130, 70, 16, 16, fill=GANFILL, stroke=GAN, sw=1.6, rx=3))
    f.append(text(W - 108, 83, "GaN", size=13, color=GAN, anchor="start", bold=True))

    for (lab, sub, hsi, hgan), cx in zip(groups, gx):
        xsi = cx - bw - gap/2
        xg = cx + gap/2
        # Si
        f.append(rect(xsi, base - hsi, bw, hsi, fill="#cdd2d8", stroke=METAL, sw=1.4, rx=3))
        # GaN
        if hgan > 0:
            f.append(rect(xg, base - hgan, bw, hgan, fill=GANFILL, stroke=GAN, sw=1.8, rx=3))
        else:
            f.append(text(xg + bw/2, base - 8, "0", size=20, color=GAN, bold=True))
            f.append(text(xg + bw/2, base - 30, "нема", size=11.5, color=GAN))
        # підписи груп
        f.append(text(cx, base + 26, lab, size=15, color=INK, bold=True))
        f.append(mtext(cx, base + 46, sub, size=11.5, color=MUTED))

    f.append(line(90, base, 690, base, color=LINE, sw=1.5))

    # причинний ланцюжок унизу
    chain = ["менший заряд", "фронт за нс", "частота в МГц", "менші котушки"]
    cy = 400
    n = len(chain)
    bxw = 150
    total = n * bxw + (n - 1) * 26
    startx = (W - total) / 2 + bxw/2
    prev_right = None
    for i, txt in enumerate(chain):
        cx = startx + i * (bxw + 26)
        box, bwd, bhd = textbox(cx, cy, txt, size=12.5, pad=9, fill=GANFILL, stroke=GAN, color="#146")
        if prev_right is not None:
            f.append(arrow(prev_right, cy, cx - bwd/2 - 2, cy, color=GAN, sw=2))
        f.append(box)
        prev_right = cx + bwd/2 + 2

    render(os.path.join(IMG, "charge-compare.svg"), W, H, *f,
           title="Заряд, який доводиться платити за один цикл перемикання")


# ── Фігура 3: два способи зробити GaN нормально-закритим ─────────────────────
def fig_normally_off():
    W, H = 800, 420
    f = []
    mid = W/2
    f.append(line(mid, 56, mid, H - 24, color="#d0d4d9", sw=1.4, dash="6,6"))

    # ── ЛІВА панель: p-GaN затвор ──
    f.append(text(200, 60, "p-GaN затвор", size=16, color=INK, bold=True))
    sx, sw = 60, 280
    y_alg, h_alg = 150, 20
    y_gan, h_gan = 170, 70
    y_2deg = y_gan + 4
    # GaN
    f.append(rect(sx, y_gan, sw, h_gan, fill=GANFILL, stroke=GAN, sw=1.4, rx=0))
    f.append(text(sx + sw/2, y_gan + h_gan - 12, "GaN", size=13, color=GAN, bold=True))
    # AlGaN
    f.append(rect(sx, y_alg, sw, h_alg, fill=ALFILL, stroke=ALGAN, sw=1.4, rx=0))
    # 2DEG з РОЗРИВОМ під затвором
    gate_cx = sx + sw/2
    f.append(line(sx + 16, y_2deg, gate_cx - 42, y_2deg, color=GAN, sw=4.2))
    f.append(line(gate_cx + 42, y_2deg, sx + sw - 16, y_2deg, color=GAN, sw=4.2))
    f.append(text(gate_cx, y_2deg + 20, "розрив", size=12, color=POS, bold=True))
    # p-GaN блок під затвором
    f.append(rect(gate_cx - 34, y_alg - 26, 68, 26, fill="#f3d9e0", stroke=POS, sw=1.6, rx=3))
    f.append(text(gate_cx, y_alg - 8, "p-GaN", size=12.5, color=POS, bold=True))
    # затвор згори
    f.append(rect(gate_cx - 28, y_alg - 52, 56, 24, fill="#e9ebee", stroke=METAL, sw=1.4, rx=3))
    f.append(text(gate_cx, y_alg - 36, "G", size=13, color=INK, bold=True))
    # S, D
    f.append(text(sx + 22, y_alg - 30, "S", size=13, color=INK, bold=True))
    f.append(text(sx + sw - 22, y_alg - 30, "D", size=13, color=INK, bold=True))
    box, bw1, bh1 = textbox(200, 330, ["за 0 В канал під затвором", "розірваний → закрито"],
                            size=13, pad=10, fill=GANFILL, stroke=GAN, color="#146")
    f.append(box)

    # ── ПРАВА панель: каскод ──
    f.append(text(mid + 200, 60, "Каскод", size=16, color=INK, bold=True))
    cxr = mid + 150            # спільна вертикаль приладів
    # вузли
    y_top, y_nodeS, y_gnd = 100, 170, 300
    # GaN (нормально-відкритий) — верхній
    f.append(rect(cxr - 60, y_top + 6, 120, 46, fill=GANFILL, stroke=GAN, sw=1.8, rx=6))
    f.append(text(cxr, y_top + 24, "GaN", size=13, color=GAN, bold=True))
    f.append(text(cxr, y_top + 42, "нормально-відкр.", size=10.5, color=GAN))
    # Si MOSFET — нижній
    f.append(rect(cxr - 60, y_nodeS + 30, 120, 46, fill="#eef0f2", stroke=METAL, sw=1.6, rx=6))
    f.append(text(cxr, y_nodeS + 48, "Si MOSFET", size=12.5, color=INK, bold=True))
    f.append(text(cxr, y_nodeS + 65, "нормально-закр.", size=10.5, color=MUTED))
    # провідники: стік GaN угору (висока напруга)
    f.append(line(cxr, y_top, cxr, y_top + 6, color=LINE, sw=2))
    f.append(text(cxr, y_top - 8, "стік (висока напруга)", size=11.5, color=MUTED))
    # GaN витік → Si стік (спільний вузол)
    f.append(line(cxr, y_top + 52, cxr, y_nodeS + 30, color=LINE, sw=2))
    # Si витік → земля
    f.append(line(cxr, y_nodeS + 76, cxr, y_gnd, color=LINE, sw=2))
    f.append(line(cxr - 20, y_gnd, cxr + 20, y_gnd, color=LINE, sw=2.4))
    f.append(text(cxr, y_gnd + 16, "земля", size=11.5, color=MUTED))
    # затвор GaN прив'язаний донизу (до витоку Si)
    f.append(line(cxr - 60, y_top + 29, cxr - 100, y_top + 29, color=LINE, sw=1.8))
    f.append(line(cxr - 100, y_top + 29, cxr - 100, y_nodeS + 76, color=LINE, sw=1.8))
    f.append(line(cxr - 100, y_nodeS + 76, cxr, y_nodeS + 76, color=LINE, sw=1.8))
    f.append(text(cxr - 104, y_top + 20, "затвор GaN", size=10.5, color=MUTED, anchor="end"))
    # керування — на затвор Si
    f.append(arrow(cxr + 130, y_nodeS + 53, cxr + 60, y_nodeS + 53, color=POS, sw=2))
    f.append(text(cxr + 134, y_nodeS + 57, "керування", size=12, color=POS, anchor="start", bold=True))

    box, bw2, bh2 = textbox(mid + 200, 360, ["малий Si-ключ замикає", "нормально-відкритий GaN"],
                            size=13, pad=10, fill=GANFILL, stroke=GAN, color="#146")
    f.append(box)

    render(os.path.join(IMG, "normally-off.svg"), W, H, *f,
           title="Два способи зробити GaN нормально-закритим")


# ── Фігура 4 (вставка hist): дві лінії — світло і транзистор ────────────────
LIGHT = "#2457d6"        # лінія світла (синій світлодіод)
LIGHTFILL = "#eaf0fd"


def fig_two_lines():
    W, H = 900, 860
    f = []
    LX, LW = 55, 335          # ліва колонка (лінія світла)
    RX, RW = 490, 375         # права колонка (лінія транзистора)
    L_RAIL, R_RAIL = 410, 470
    BH = 54                   # висота картки
    y0, step = 108, 62

    rows = [
        ("L", ["1969 · перша монокристалічна плівка", "GaN на сапфірі (RCA)"]),
        ("L", ["1971 · синє свічення з GaN", "але p-типу так і немає"]),
        ("R", ["1980 · HEMT на GaAs", "канал без домішок"]),
        ("L", ["1986 · буферний шар AlN", "кристал нарешті став придатним"]),
        ("L", ["1989 · p-тип GaN", "магній + електронний промінь"]),
        ("L", ["1992 · відпал замість променя", "p-тип стає заводською операцією"]),
        ("L", ["1993 · серійний синій світлодіод", "Nichia"]),
        ("R", ["1993 · перший AlGaN/GaN HEMT", "Хан і колеги"]),
        ("R", ["1999–2006 · GaN на кремнієвій пластині", "діаметр і ціна кремнієвої фабрики"]),
        ("R", ["2007 · нормально-закритий", "p-GaN затвор і каскод"]),
        ("R", ["2009–2010 · перші серійні силові ключі", "EPC та інші"]),
        ("R", ["2018 · GaN у зарядці для телефона", "мегагерцові перетворювачі"]),
    ]

    ys = [y0 + i * step for i in range(len(rows))]
    yL = [y for y, (s, _) in zip(ys, rows) if s == "L"]
    yR = [y for y, (s, _) in zip(ys, rows) if s == "R"]

    # рейки
    f.append(line(L_RAIL, min(yL) - 26, L_RAIL, max(yL) + 26, color=LIGHT, sw=2.2))
    f.append(line(R_RAIL, min(yR) - 26, R_RAIL, max(yR) + 26, color=GAN, sw=2.2))

    # заголовки колонок
    f.append(text(LX + LW / 2, 66, "лінія світла", size=16, color=LIGHT, bold=True))
    f.append(text(RX + RW / 2, 66, "лінія транзистора", size=16, color=GAN, bold=True))

    for y, (side, lines) in zip(ys, rows):
        if side == "L":
            f.append(line(LX + LW, y, L_RAIL - 7, y, color=LIGHT, sw=1.4))
            f.append(circle(L_RAIL, y, 6, fill=LIGHTFILL, stroke=LIGHT, sw=2))
            f.append(fitbox(LX, y - BH / 2, LW, BH, lines, size=13,
                            fill=LIGHTFILL, stroke=LIGHT, sw=1.5, color="#14306b"))
        else:
            f.append(line(R_RAIL + 7, y, RX, y, color=GAN, sw=1.4))
            f.append(circle(R_RAIL, y, 6, fill=GANFILL, stroke=GAN, sw=2))
            f.append(fitbox(RX, y - BH / 2, RW, BH, lines, size=13,
                            fill=GANFILL, stroke=GAN, sw=1.5, color="#0f5a3a"))

    # примітка у вільному лівому полі (нижче останнього лівого рядка)
    box, bw, bh = textbox(LX + LW / 2, max(yL) + 210,
                          ["Лінія світла не обірвалася — вона",
                           "віддала головне: придатний кристал",
                           "і вміння його вирощувати."],
                          size=13, pad=12, fill="#f4f6f8", stroke=MUTED, color=INK)
    f.append(box)

    render(os.path.join(IMG, "gan-two-lines.svg"), W, H, *f,
           title="Дві лінії: кристал заради світла й транзистор заради потужності")


# ── Фігура 5 (вставка hist): що силовий ключ успадкував від світлодіода ─────
def fig_inheritance():
    W, H = 920, 440
    f = []
    LX, LW = 40, 380
    RX, RW = 520, 380
    BH = 58
    ys = [130, 206, 282]

    f.append(text(LX + LW / 2, 74, "зроблено заради синього світла",
                  size=15, color=LIGHT, bold=True))
    f.append(text(RX + RW / 2, 74, "що з цього дісталося силовому ключу",
                  size=15, color=GAN, bold=True))

    pairs = [
        (["вирощувати GaN на чужій підкладці", "(буферний шар, 1986)"],
         ["GaN на звичайній кремнієвій пластині", "— велика фабрика, мала ціна"]),
        (["цехи MOCVD під мільярди світлодіодів", "(1990-ті — 2000-ні)"],
         ["епітаксія, за яку є кому платити", "ще до першого силового ключа"]),
        (["p-GaN, легований магнієм", "(1989–1992)"],
         ["затвор, що тримає ключ закритим", "за нуля вольт"]),
    ]

    for y, (lt, rt) in zip(ys, pairs):
        f.append(fitbox(LX, y - BH / 2, LW, BH, lt, size=13,
                        fill=LIGHTFILL, stroke=LIGHT, sw=1.5, color="#14306b"))
        f.append(fitbox(RX, y - BH / 2, RW, BH, rt, size=13,
                        fill=GANFILL, stroke=GAN, sw=1.5, color="#0f5a3a"))
        f.append(arrow(LX + LW + 8, y, RX - 10, y, color=GAN, sw=2.2))

    box, bw, bh = textbox(W / 2, 385,
                          ["А канал світлодіод не дав: 2DEG на межі AlGaN/GaN — власна",
                           "знахідка транзисторної лінії, і для світла та сама поляризація шкодить."],
                          size=13, pad=12, fill="#f4f6f8", stroke=MUTED, color=INK)
    f.append(box)

    render(os.path.join(IMG, "gan-inheritance.svg"), W, H, *f,
           title="Що силовий GaN успадкував від синього світлодіода")


if __name__ == "__main__":
    fig_structure()
    fig_charge()
    fig_normally_off()
    fig_two_lines()
    fig_inheritance()
    print("OK: figures written to", IMG)
