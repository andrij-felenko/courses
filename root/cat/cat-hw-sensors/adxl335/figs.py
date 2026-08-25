# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: диференційний конденсатор усередині — принцип роботи ──────────
def fig_principle():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Що всередині: рухома маса між нерухомими пластинами", size=17, bold=True))

    # два нерухомі якорі (верх/низ) і рухома маса між ними
    topY, botY = 120, 300
    plateL, plateR = 150, 430
    # верхня нерухома пластина
    f.append(rect(plateL, topY, plateR-plateL, 22, fill="#eef1f4", stroke=LINE, sw=1.5, rx=3))
    f.append(text((plateL+plateR)/2, topY-8, "нерухома пластина (закріплена)", size=12, color=MUTED))
    # нижня нерухома пластина
    f.append(rect(plateL, botY, plateR-plateL, 22, fill="#eef1f4", stroke=LINE, sw=1.5, rx=3))
    f.append(text((plateL+plateR)/2, botY+38, "нерухома пластина (закріплена)", size=12, color=MUTED))

    # рухома маса (посередині, трохи зміщена вниз — показуємо прискорення)
    massY = 220
    f.append(rect(plateL+20, massY-14, plateR-plateL-40, 28, fill="#fff3cd", stroke=POS, sw=2, rx=4))
    f.append(text((plateL+plateR)/2, massY+5, "рухома маса", size=13, bold=True))

    # пружини від маси до країв
    for xx in (plateL+20, plateR-20):
        f.append(line(xx-15 if xx<plateL+30 else xx, massY, xx-15 if xx<plateL+30 else xx+15, massY, color=FIELD, sw=1))
    # намалюємо пружинки як зигзаг зліва і справа
    def spring(x0, x1, y):
        n=6; seg=(x1-x0)/n; pts=[];
        for i in range(n+1):
            yy = y + (8 if i%2 else -8) if 0<i<n else y
            pts.append((x0+i*seg, yy))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f"%(px,py) for px,py in pts[1:])
        return '<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, FIELD)
    f.append(spring(105, plateL+20, massY))
    f.append(spring(plateR-20, plateR+45, massY))
    f.append(circle(105, massY, 4, fill=INK, stroke=INK))
    f.append(circle(plateR+45, massY, 4, fill=INK, stroke=INK))
    f.append(text(105, massY-18, "кріплення", size=10, color=MUTED, anchor="middle"))

    # зазори — це два конденсатори (лінія зазору + підпис ПОРУЧ, не на лінії)
    gapx = (plateL+plateR)/2-70
    f.append(line(gapx, topY+22, gapx, massY-14, color=NEG, sw=1.2, dash="4,3"))
    f.append(line(gapx, massY+14, gapx, botY, color=POS, sw=1.2, dash="4,3"))
    b1 = textbox(gapx-24, (topY+massY)/2-6, "C1", size=12, color=NEG, pad=5)
    f.append(b1[0])
    b2 = textbox(gapx-24, (massY+botY)/2+6, "C2", size=12, color=POS, pad=5)
    f.append(b2[0])

    # стрілка прискорення (маса «відстає» → зміщується)
    f.append(arrow((plateL+plateR)/2+95, massY-2, (plateL+plateR)/2+95, massY+42, color=INK))
    f.append(text((plateL+plateR)/2+150, massY+22, "прискорення", size=12, bold=True))

    # висновок унизу
    concl = ("Зсув маси зменшує один зазор і збільшує інший:  C1 ↑, C2 ↓.\n"
             "Різниця ємностей → напруга, пропорційна прискоренню.")
    f.append(fitbox(150, 360, 420, 52, concl, size=12, pad=8, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'principle.svg'), W, H, *f)


# ── Фігура 2: розводка GY-61 пін-у-пін до 5 В МК ────────────────────────────
def fig_wiring():
    W, H = 720, 440
    f = []
    f.append(text(W/2, 26, "Підключення GY-61 до 5-вольтового мікроконтролера", size=17, bold=True))

    # плата GY-61 зліва
    bx, by, bw, bh = 60, 80, 190, 300
    f.append(rect(bx, by, bw, bh, fill="#e8f0fe", stroke=NEG, sw=2, rx=8))
    f.append(text(bx+bw/2, by-10, "GY-61 (модуль ADXL335)", size=13, bold=True))
    f.append(text(bx+bw/2, by+22, "на борту: LDO 3.3 В", size=11, color=MUTED))
    f.append(text(bx+bw/2, by+40, "+ конденсатори фільтра", size=11, color=MUTED))

    pins = ["VCC", "GND", "X", "Y", "Z", "ST"]
    py0 = by+70; step=(bh-90)/ (len(pins)-1)
    pin_y = {}
    for i, p in enumerate(pins):
        yy = py0 + i*step
        pin_y[p] = yy
        f.append(circle(bx+bw-14, yy, 6, fill=BG, stroke=INK, sw=1.6))
        f.append(text(bx+bw-34, yy+4, p, size=13, bold=True, anchor="end"))

    # МК справа
    mx, my, mw, mh = 500, 80, 180, 300
    f.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(text(mx+mw/2, my-10, "МК / плата (5 В)", size=13, bold=True))
    mpins = ["5V", "GND", "A0", "A1", "A2", "(не тр.)"]
    mpin_y = {}
    for i, p in enumerate(mpins):
        yy = py0 + i*step
        mpin_y[i] = yy
        f.append(circle(mx+14, yy, 6, fill=BG, stroke=INK, sw=1.6))
        f.append(text(mx+34, yy+4, p, size=13, bold=True, anchor="start"))

    # зʼєднання
    def wire(p, mi, col, lbl):
        x1 = bx+bw-8; y1 = pin_y[p]; x2 = mx+8; y2 = mpin_y[mi]
        midx = (x1+x2)/2
        d = "M %.1f %.1f H %.1f V %.1f H %.1f" % (x1, y1, midx, y2, x2)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, col))
        # підпис ЛІВОРУЧ від вертикального сегмента траси, на висоті пінів модуля
        f.append(text(midx-10, y1-6, lbl, size=10, color=col, anchor="end"))
    wire("VCC", 0, POS, "живлення")
    wire("GND", 1, INK, "спільна земля")
    wire("X", 2, FIELD, "аналог. вхід")
    wire("Y", 3, FIELD, "аналог. вхід")
    wire("Z", 4, FIELD, "аналог. вхід")
    # ST лишаємо вільним
    f.append(text(bx+bw+18, pin_y["ST"]+4, "→ вільний", size=11, color=MUTED, anchor="start"))

    note = ("VCC живиться 5 В — вбудований LDO дає чипу його 3.3 В.\n"
            "X/Y/Z — аналогові напруги на АЦП (A0..A2). ST не чіпаємо.")
    f.append(fitbox(60, 398, 620, 30, note, size=12, pad=6, fill="#fff8e1", stroke=POS))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── Фігура 3: карта вихідної напруги (bias + нахил) ─────────────────────────
def fig_output():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 26, "Вихід осі: 1.5 В у спокої, ±0.3 В на кожен g", size=17, bold=True))

    # осі графіка: X = прискорення (g), Y = напруга (В)
    ox, oy = 110, 320          # початок координат
    ax_w, ax_h = 500, 250
    f.append(line(ox, oy, ox+ax_w, oy, color=INK, sw=1.6))         # вісь g
    f.append(line(ox, oy, ox, oy-ax_h, color=INK, sw=1.6))         # вісь V
    f.append(text(ox+ax_w/2, oy+40, "прискорення вздовж осі, g", size=12))
    f.append(text(ox-70, oy-ax_h/2, "вихід, В", size=12))

    # діапазон -3g..+3g по X, 0.6..2.4 В по Y (1.5 центр)
    def gx(g): return ox + (g+3)/6*ax_w
    def vy(v): return oy - (v-0.6)/(2.4-0.6)*ax_h

    # сітка/мітки g
    for g in (-3,-2,-1,0,1,2,3):
        x = gx(g)
        f.append(line(x, oy, x, oy+5, color=INK, sw=1.2))
        f.append(text(x, oy+20, ("%+d" % g) if g else "0", size=11, color=MUTED))
    for v in (0.6, 1.5, 2.4):
        y = vy(v)
        f.append(line(ox-5, y, ox, y, color=INK, sw=1.2))
        f.append(text(ox-16, y+4, "%.1f" % v, size=11, color=MUTED, anchor="end"))

    # лінія передавання: V = 1.5 + 0.3*g
    x1,y1 = gx(-3), vy(0.6); x2,y2 = gx(3), vy(2.4)
    f.append(line(x1,y1,x2,y2, color=NEG, sw=2.5))

    # горизонталь bias 1.5 В
    f.append(line(ox, vy(1.5), ox+ax_w, vy(1.5), color=MUTED, sw=1, dash="5,4"))
    b = textbox(gx(-2.1), vy(1.72), "0g → 1.5 В", size=11, color=INK, pad=5)
    f.append(b[0])

    # точка спокою (0g)
    f.append(circle(gx(0), vy(1.5), 5, fill=FIELD, stroke=FIELD))
    f.append(text(gx(0)+8, vy(1.5)+22, "спокій 0g", size=11, color=FIELD, anchor="start"))
    # точка нахилу на бік (вісь дивиться вниз → -1g); підпис у порожній зоні НИЖЧЕ лінії
    f.append(circle(gx(-1), vy(1.2), 5, fill=POS, stroke=POS))
    b2 = textbox(gx(1.0), vy(1.02), "нахил 90°: вісь бачить\n−1g → 1.2 В", size=11, color=POS, pad=6)
    bx2, bw2, bh2 = gx(1.0), b2[1], b2[2]
    f.append(line(gx(-1), vy(1.2), gx(1.0)-bw2/2, vy(1.02)-2, color=POS, sw=1, dash="3,3"))
    f.append(b2[0])

    # нахил лінії — підпис над діагоналлю у вільному куті
    f.append(text(gx(1.7), vy(2.28), "нахил = 0.3 В/g", size=11, color=NEG, bold=True))

    render(os.path.join(IMG, 'output.svg'), W, H, *f)


# ── Фігура 4: фільтрація — сирий vs ковзне середнє vs IIR ────────────────────
def fig_filters():
    import math
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Фiльтрацiя шуму: сирий сигнал, ковзне середнє, IIR", size=17, bold=True))

    # область графіка
    ox, oy = 70, 300
    ax_w, ax_h = 590, 230
    f.append(line(ox, oy, ox+ax_w, oy, color=INK, sw=1.4))          # час
    f.append(line(ox, oy-ax_h, ox, oy, color=INK, sw=1.4))          # величина
    f.append(text(ox+ax_w/2, oy+34, "час (вiдлiки)", size=12))
    f.append(text(ox-46, oy-ax_h/2, "сигнал", size=12))

    # синтетичний сигнал: спокій, потім різкий стрибок, з накладеним шумом
    N = 60
    random_state = 12345
    def prng():
        nonlocal random_state
        random_state = (1103515245*random_state + 12345) & 0x7fffffff
        return random_state / 0x7fffffff - 0.5   # -0.5..0.5
    base = []
    for i in range(N):
        step = 0.0 if i < 24 else 0.7           # різкий стрибок на 24-му відліку
        base.append(step)
    raw = [b + 0.16*prng() for b in base]       # сирий = крок + шум

    # ковзне середнє (вікно 6)
    WIN = 6
    ma = []
    for i in range(N):
        s = 0.0; c = 0
        for j in range(max(0, i-WIN+1), i+1):
            s += raw[j]; c += 1
        ma.append(s/c)
    # IIR (alpha 0.2)
    iir = []
    y = raw[0]
    for i in range(N):
        y += 0.2*(raw[i]-y)
        iir.append(y)

    def px(i): return ox + i/(N-1)*ax_w
    def py(v): return oy - (v+0.25)/(1.15)*ax_h   # діапазон приблизно -0.25..0.9

    def poly(vals, col, sw, dash=None):
        d = "M %.1f %.1f " % (px(0), py(vals[0]))
        d += " ".join("L %.1f %.1f" % (px(i), py(vals[i])) for i in range(1, N))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, da))

    poly(raw, MUTED, 1.2)        # сирий — тонкий сірий
    poly(ma,  NEG, 2.2)          # ковзне середнє — синій
    poly(iir, POS, 2.2)          # IIR — червоний

    # позначка моменту стрибка
    f.append(line(px(24), oy-ax_h, px(24), oy, color=FIELD, sw=1, dash="4,4"))
    b0 = textbox(px(24), oy-ax_h+16, "стрибок", size=10, color=FIELD, pad=4)
    f.append(b0[0])

    # легенда — у правому вільному куті, кожен рядок зі своїм зразком-лінією
    lx, ly = ox+ax_w-206, oy-ax_h+8
    f.append(rect(lx, ly, 200, 66, fill=BG, stroke=LINE, sw=1, rx=5))
    items = [("сирий (з шумом)", MUTED), ("ковзне середнє", NEG), ("IIR (α=0.2)", POS)]
    for k, (lbl, col) in enumerate(items):
        yy = ly + 18 + k*18
        f.append(line(lx+12, yy-4, lx+40, yy-4, color=col, sw=2.4))
        f.append(text(lx+48, yy, lbl, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'filters.svg'), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_wiring()
    fig_output()
    fig_filters()
    print("ok")
