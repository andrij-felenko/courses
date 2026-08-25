# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PAT   = "#c0392b"   # роки під патентом / дорога гілка
FREE  = "#16a34a"   # вільна гілка
NEUT  = "#2457d6"   # нейтральні позначки


# ── hist-timeline: дорога від SIFT до ORB, і смуга «під патентом» ──────────────
# Ідея однією картинкою: SIFT з'явився 1999/2004 і був накритий патентом до 2020;
# рівно під тінню цього патенту виросла вільна гілка FAST→BRIEF→ORB.

def fig_timeline():
    W, H = 860, 430
    p = []

    # вісь років
    x0, x1 = 70, W - 40
    axy = 250
    yr0, yr1 = 1999, 2021
    def X(year):
        return x0 + (year - yr0) / (yr1 - yr0) * (x1 - x0)

    # смуга «патент чинний» 2004–2020 (видано → сплив)
    px0, px1 = X(2004), X(2020)
    p.append(rect(px0, 96, px1 - px0, 300, fill="#fbeae7", stroke="none", rx=4))
    p.append(text((px0 + px1) / 2, 116, "патент US 6,711,293 чинний — вільне комерційне вживання під замком",
                  size=11, color=PAT, bold=True))

    # сама вісь
    p.append(line(x0 - 10, axy, x1 + 6, axy, color=INK, sw=2))
    for yr in range(2000, 2021, 5):
        xx = X(yr)
        p.append(line(xx, axy - 5, xx, axy + 5, color=INK, sw=1.4))
        p.append(text(xx, axy + 22, str(yr), size=11, color=MUTED))

    def event(year, yoff, label, col, up=True):
        xx = X(year)
        ey = axy + yoff
        p.append(line(xx, axy, xx, ey, color=col, sw=1.6, dash="3,3"))
        p.append(circle(xx, axy, 5, fill=col, stroke=BG, sw=1.5))
        body, bw, bh = textbox(xx, ey + (0 if up else 0), label, size=11,
                               color=col, stroke=col, fill=BG, bold=False, pad=7)
        p.append(body)
        return xx

    # верхня (SIFT) гілка — над віссю
    event(1999, -150, "SIFT\nЛоу, ICCV 1999", PAT)
    event(2004, -96,  "SIFT розгорнуто\nIJCV 2004; патент видано", PAT)
    event(2020, -150, "патент сплив\nбер. 2020", NEUT)

    # нижня (вільна) гілка — під віссю
    event(2006, 70,  "FAST\nRosten–Drummond", FREE, up=False)
    event(2010, 130, "BRIEF\nEPFL, ECCV 2010", FREE, up=False)
    event(2011, 70,  "ORB\nWillow Garage, ICCV 2011", FREE, up=False)

    # підпис вільної гілки
    p.append(text((X(2006) + X(2011)) / 2, 408,
                  "вільна гілка: безпатентні швидкі дескриптори", size=11,
                  color=FREE, bold=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Від SIFT до двійкових дескрипторів")


# ── hist-descriptor-cost: чому двійковий опис дешевший на порядки ──────────────
# Не «більше-менше», а СУТЬ: SIFT — 128 дійсних чисел, звірка = евклід (сотні
# множень); ORB — 256 бітів, звірка = XOR+popcount (дві інструкції).

def fig_cost():
    W, H = 820, 360
    p = []
    colw = 360
    xL, xR = 30, W - 30 - colw
    ytop = 70

    def panel(x, title, col, lines, cost):
        pp = []
        pp.append(rect(x, ytop, colw, 250, fill=BG, stroke=col, sw=1.8, rx=10))
        pp.append(text(x + colw / 2, ytop + 26, title, size=14, color=col, bold=True))
        yy = ytop + 58
        for ln in lines:
            pp.append(text(x + 20, yy, ln, size=11.5, color=INK, anchor="start"))
            yy += 22
        # рядок ціни звірки
        pp.append(line(x + 16, ytop + 176, x + colw - 16, ytop + 176, color=MUTED, sw=1, dash="4,3"))
        pp.append(text(x + colw / 2, ytop + 200, "звірити дві точки:", size=11, color=MUTED))
        pp.append(fitbox(x + 24, ytop + 212, colw - 48, 30, cost, size=12,
                         color=col, stroke=col, fill=BG, bold=True))
        return pp

    p += panel(xL, "SIFT — числовий вектор", NEUT, [
        "окіл → 128 дійсних чисел",
        "(сітка 4×4 × 8 напрямків градієнта)",
        "≈ 512 байтів на точку",
        "інваріантний, дуже розрізнюваний",
    ], "евклід: ≈128 множень + 128 віднімань")

    p += panel(xR, "ORB — двійковий рядок", FREE, [
        "окіл → 256 бітів",
        "(256 тестів «яскравіше?»)",
        "= 32 байти на точку",
        "порівнянно точний, у сотні разів дешевший",
    ], "Гаммінг: 8× (XOR + popcount)")

    # підсумковий місток «на ~2 порядки швидше»
    p.append(text(W / 2, ytop + 274, "≈ на два порядки швидше при близькій якості",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "hist-descriptor-cost.svg"), W, H, *p,
           title="Числовий опис проти двійкового")


if __name__ == "__main__":
    fig_timeline()
    fig_cost()
    print("ok")
