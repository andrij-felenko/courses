# -*- coding: utf-8 -*-
"""Фігури для кроку «Стереозір» (root/course/embedded/davachi/stereo-vision).
Запуск:  python figs.py   →  ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: геометрія стереозору — база, два промені, диспаритет ───────────
def fig_geometry():
    W, H = 760, 470
    f = []
    f.append(text(W/2, 26, "Та сама точка — різне місце на двох матрицях", size=17, bold=True))

    # дві камери (центри проєкції) — рознесені по базі b
    yL = 380                      # рівень оптичних центрів
    xL, xR = 250, 510             # лівий і правий центри
    f.append(circle(xL, yL, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(circle(xR, yL, 7, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(xL, yL+26, "ліва камера", size=12, color=NEG))
    f.append(text(xR, yL+26, "права камера", size=12, color=POS))

    # база між центрами
    f.append(line(xL, yL+40, xR, yL+40, color=MUTED, sw=1.2))
    f.append(line(xL, yL, xL, yL+44, color=MUTED, sw=1, dash="3,3"))
    f.append(line(xR, yL, xR, yL+44, color=MUTED, sw=1, dash="3,3"))
    f.append(text((xL+xR)/2, yL+56, "база  b", size=13, bold=True, color=INK))

    # площини матриць (нижче центрів — як у камері-обскурі, але малюємо спереду
    # для наочності: лінійка пікселів на рівні фокуса f над центром)
    yImg = yL - 70
    halfw = 78
    for (cx, col, nm) in ((xL, NEG, "L"), (xR, POS, "R")):
        f.append(line(cx-halfw, yImg, cx+halfw, yImg, color=col, sw=3))
        # позначки центрів матриці (оптична вісь)
        f.append(line(cx, yImg-6, cx, yL, color=MUTED, sw=1, dash="2,3"))
    # відстань центр→матриця = фокус f
    f.append(line(xL-halfw-18, yImg, xL-halfw-18, yL, color=MUTED, sw=1))
    f.append(text(xL-halfw-30, (yImg+yL)/2, "f", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(xL-halfw-30, (yImg+yL)/2+18, "(фокус)", size=10, color=MUTED, anchor="end"))

    # ціль-точка P (далека) і промені в обидва центри
    Px, Py = 405, 95
    f.append(circle(Px, Py, 8, fill=FIELD, stroke=INK, sw=1.8))
    f.append(text(Px+16, Py-4, "точка P", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(Px+16, Py+14, "(на глибині Z)", size=11, color=MUTED, anchor="start"))

    # промені P→центр; перетин із площиною матриці дає піксель xL', xR'
    def hit_x(cx):
        # параметрично: від P до (cx,yL), знайти x на y=yImg
        t = (yImg - Py) / (yL - Py)
        return Px + t * (cx - Px)
    hxL, hxR = hit_x(xL), hit_x(xR)
    f.append(line(Px, Py, xL, yL, color=NEG, sw=1.6))
    f.append(line(Px, Py, xR, yL, color=POS, sw=1.6))
    # точки попадання на матриці
    f.append(circle(hxL, yImg, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(hxR, yImg, 5, fill=POS, stroke=POS, sw=1))

    # диспаритет: різниця координат тієї самої точки на двох матрицях.
    # покажемо обидві координати, зведені до спільної осі (внизу під матрицями)
    yD = yImg - 34
    # позначки x' відносно власних оптичних осей
    f.append(line(xL, yD, hxL, yD, color=NEG, sw=2))
    f.append(text((xL+hxL)/2, yD-7, "x′L", size=12, color=NEG, bold=True))
    f.append(line(xR, yD, hxR, yD, color=POS, sw=2))
    f.append(text((xR+hxR)/2, yD-7, "x′R", size=12, color=POS, bold=True))

    # формула-підказка праворуч
    box, bw, bh = textbox(648, 150,
                          "диспаритет\nd = x′L − x′R\n\nZ = f · b / d",
                          size=13, bold=False, fill="#eafaf1", stroke=FIELD)
    f.append(box)

    render(os.path.join(OUT, "stereo-geometry.svg"), W, H, *f)


# ── Фігура 2: глибина з диспаритету — гіпербола й вибух похибки вдалині ──────
def fig_depth_disparity():
    W, H = 760, 460
    f = []
    f.append(text(W/2, 26, "Рівні кроки диспаритету — нерівні кроки глибини", size=17, bold=True))

    # осі: X = диспаритет (пікселі, спадає вправо), Y = глибина Z
    ox, oy = 110, 380        # початок осей
    ax_w, ax_h = 560, 300
    f.append(arrow(ox, oy, ox+ax_w, oy, color=INK, sw=1.8))         # вісь диспаритету
    f.append(arrow(ox, oy, ox, oy-ax_h, color=INK, sw=1.8))         # вісь глибини
    f.append(text(ox+ax_w-4, oy+30, "диспаритет d (пікселі) →", size=12, anchor="end"))
    f.append(text(ox-14, oy-ax_h+6, "глибина Z", size=12, anchor="end", bold=True))
    f.append(text(ox-14, oy-ax_h+22, "(метри)", size=10, anchor="end", color=MUTED))
    f.append(text(ox+ax_w-4, oy+46, "(чим менший d — тим далі)", size=10, anchor="end", color=MUTED))

    # гіпербола Z = k/d. Намалюємо точками.
    import math
    k = 4200.0
    dmin, dmax = 7.0, 60.0
    def px_d(d):  # диспаритет → x (велике d ліворуч)
        return ox + (1 - (d - dmin)/(dmax - dmin)) * ax_w
    Zmax = k/dmin
    def px_Z(Z):
        return oy - min(Z, Zmax)/Zmax * ax_h
    pts = []
    d = dmax
    while d >= dmin:
        pts.append((px_d(d), px_Z(k/d)))
        d -= 0.5
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, FIELD))

    # один піксель диспаритету біля кривої — крок угорі (далеко) і внизу (близько)
    def step(dval, col, label):
        x1, y1 = px_d(dval), px_Z(k/dval)
        x2, y2 = px_d(dval-1), px_Z(k/(dval-1))
        # горизонтальний крок диспаритету (1 px) і відповідний стрибок глибини
        f.append(line(x1, y1, x2, y1, color=col, sw=2))
        f.append(line(x2, y1, x2, y2, color=col, sw=2, dash="4,3"))
        f.append(circle(x1, y1, 4, fill=col, stroke=col))
        f.append(circle(x2, y2, 4, fill=col, stroke=col))
        dZ = k/(dval-1) - k/dval
        f.append(text((x1+x2)/2, y1-8, "1 px", size=10, color=col, bold=True))
        f.append(text(x2-8, (y1+y2)/2, "ΔZ ≈ %.1f м" % dZ, size=11, color=col,
                      anchor="end", bold=True))
        return label
    step(48, NEG, "близько")   # великий d → крихітний ΔZ
    step(9,  POS, "далеко")    # малий d → величезний ΔZ

    # підписи зон (багаторядкові — через mtext)
    f.append(mtext(px_d(48), oy-14, ["близько:", "крок дрібний"], size=11, color=NEG))
    f.append(mtext(px_d(9)-14, px_Z(k/9)+18, ["далеко: той самий 1 px", "= величезний стрибок"],
                   size=11, color=POS, anchor="end"))

    # висновок-рамка — у вільний нижній лівий кут, подалі від кривої
    box, bw, bh = textbox(290, 150, "похибка глибини\nΔZ ≈ (Z² / f·b) · Δd\nросте як Z²",
                          size=13, fill="#fdecea", stroke=POS)
    f.append(box)

    render(os.path.join(OUT, "depth-disparity.svg"), W, H, *f)


# ── Фігура 3: стерео проти ToF — де чий вибір ───────────────────────────────
def fig_stereo_vs_tof():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Пасивний стереозір проти активного далекоміра", size=17, bold=True))

    colW = 330
    xS, xT = 60, 60 + colW + 20
    y0, boxH = 56, 350

    # ліва колонка — стерео
    f.append(rect(xS, y0, colW, boxH, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(xS+colW/2, y0+30, "Стереозір (дві камери)", size=15, bold=True, color=NEG))
    rows_s = [
        "пасивний — лише природне світло",
        "сонце — друг, а не засліплення",
        "дає густу карту глибини всієї сцени",
        "потребує текстури на цілі",
        "сліпне на гладкій стіні без візерунка",
        "точність падає як Z² (далеко — грубо)",
        "обчислень багато (пошук відповідності)",
    ]
    # права колонка — ToF/лазер
    f.append(rect(xT, y0, colW, boxH, fill="#fdf0e9", stroke=POS, sw=2))
    f.append(text(xT+colW/2, y0+30, "ToF / лазерний далекомір", size=15, bold=True, color=POS))
    rows_t = [
        "активний — сам шле зондувальний промінь",
        "працює в повній пітьмі",
        "часто одна точка / рідкий промінь",
        "байдужий до візерунка цілі",
        "гладка стіна — добра ціль",
        "точність тримається рівніше з відстанню",
        "засічка часу / фази, мало математики",
    ]
    yy = y0 + 62
    for s, t in zip(rows_s, rows_t):
        f.append(text(xS+18, yy, "•", size=13, color=NEG, anchor="start"))
        f.append(fitbox(xS+30, yy-15, colW-44, 36, s, size=12, fill="none",
                        stroke="none", color=INK))
        f.append(text(xT+18, yy, "•", size=13, color=POS, anchor="start"))
        f.append(fitbox(xT+30, yy-15, colW-44, 36, t, size=12, fill="none",
                        stroke="none", color=INK))
        yy += 42

    render(os.path.join(OUT, "stereo-vs-tof.svg"), W, H, *f)


# ── Фігура 4 (історія): дзеркальний стереоскоп Вітстона, вид згори ───────────
def fig_wheatstone():
    W, H = 760, 470
    f = []
    f.append(text(W/2, 26, "Дзеркальний стереоскоп Вітстона (вид згори)", size=17, bold=True))

    # Геометрія згори: спостерігач унизу по центру, дивиться ВГОРУ.
    # Двоє очей трохи рознесені. Перед ними — пара дзеркал під 45°,
    # зведених кутом (як «дашок»). Ліве дзеркало дивиться вліво,
    # праве — вправо; кожне відбиває бічний малюнок у своє око.
    cx = W/2
    eyeY = 410
    exL, exR = cx-34, cx+34        # ліве/праве око

    # очі
    f.append(circle(exL, eyeY, 9, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(circle(exR, eyeY, 9, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(exL, eyeY+24, "ліве око", size=12, color=NEG))
    f.append(text(exR, eyeY+24, "праве око", size=12, color=POS))

    # пара дзеркал під 45°, зведених кутом (вершина по центру вгорі)
    apex = (cx, 235)               # спільний кут «дашка»
    mLo  = (cx-60, 295)            # лівий нижній край лівого дзеркала
    mRo  = (cx+60, 295)            # правий нижній край правого дзеркала
    f.append(line(apex[0], apex[1], mLo[0], mLo[1], color=NEG, sw=4))   # ліве дзеркало
    f.append(line(apex[0], apex[1], mRo[0], mRo[1], color=POS, sw=4))   # праве дзеркало
    # перегородка між дзеркалами (щоб око не бачило чужу картинку)
    f.append(line(apex[0], apex[1]+4, cx, eyeY-16, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(cx, 224, "дзеркала під 45°", size=12, bold=True, color=INK))

    # позначка кута 45° біля лівого дзеркала
    f.append(text(cx-44, 276, "45°", size=11, color=NEG, bold=True))
    f.append(text(cx+44, 276, "45°", size=11, color=POS, bold=True))

    # бічні малюнки (стереопара): ліворуч і праворуч від голови
    drwY = 300
    dwL = (90, drwY)               # лівий малюнок (для лівого ока)
    dwR = (W-90, drwY)             # правий малюнок (для правого ока)
    f.append(rect(dwL[0]-34, dwL[1]-26, 68, 52, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(rect(dwR[0]-34, dwR[1]-26, 68, 52, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(dwL[0], dwL[1]+46, "лівий малюнок", size=11, color=NEG))
    f.append(text(dwR[0], dwR[1]+46, "правий малюнок", size=11, color=POS))
    # схематичний «зсунутий куб» у кожному малюнку — натяк на диспаритет
    def mini_cube(x, y, dx, col):
        a = rect(x-12, y-8, 18, 16, fill="none", stroke=col, sw=1.3)
        b = rect(x-12+dx, y-12, 18, 16, fill="none", stroke=col, sw=1.3)
        return a + b
    f.append(mini_cube(dwL[0], dwL[1], 4, NEG))
    f.append(mini_cube(dwR[0], dwR[1], -4, POS))

    # промені: бічний малюнок → дзеркало (горизонтально) → око (вниз, 90°)
    # лівий тракт
    midL = (cx-30, 268)            # точка відбиття на лівому дзеркалі
    f.append(arrow(dwL[0]+34, dwL[1]-10, midL[0], midL[1], color=NEG, sw=1.8))
    f.append(arrow(midL[0], midL[1], exL, eyeY-9, color=NEG, sw=1.8))
    # правий тракт
    midR = (cx+30, 268)
    f.append(arrow(dwR[0]-34, dwR[1]-10, midR[0], midR[1], color=POS, sw=1.8))
    f.append(arrow(midR[0], midR[1], exR, eyeY-9, color=POS, sw=1.8))

    # уявний об'ємний предмет, що «висить» прямо перед очима (вгорі по центру)
    ph = (cx, 115)
    # куб у перспективі
    s = 24
    front = [(ph[0]-s, ph[1]-s), (ph[0]+s, ph[1]-s), (ph[0]+s, ph[1]+s), (ph[0]-s, ph[1]+s)]
    off = 15
    back = [(p[0]+off, p[1]-off) for p in front]
    fpoly = " ".join("%.0f,%.0f" % p for p in front)
    bpoly = " ".join("%.0f,%.0f" % p for p in back)
    f.append('<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="2"/>' % (bpoly, FIELD))
    for a, b in zip(front, back):
        f.append(line(a[0], a[1], b[0], b[1], color=FIELD, sw=1.6))
    f.append('<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="2.2"/>' % (fpoly, FIELD))
    f.append(text(ph[0], ph[1]-s-off-9, "об'ємний предмет", size=12, bold=True, color=FIELD))
    f.append(text(ph[0], ph[1]+s+18, "(його перед очима НЕМАЄ —", size=10, color=MUTED))
    f.append(text(ph[0], ph[1]+s+32, "мозок зливає дві картинки)", size=10, color=MUTED))
    # лінії-погляди від очей крізь дзеркала «в порожнечу», де збирається куб
    f.append(line(exL, eyeY-9, ph[0]-6, ph[1]+s, color=MUTED, sw=1, dash="2,4"))
    f.append(line(exR, eyeY-9, ph[0]+6, ph[1]+s, color=MUTED, sw=1, dash="2,4"))

    render(os.path.join(OUT, "wheatstone-stereoscope.svg"), W, H, *f)


if __name__ == "__main__":
    fig_geometry()
    fig_depth_disparity()
    fig_stereo_vs_tof()
    fig_wheatstone()
    print("OK: figures written to", OUT)
