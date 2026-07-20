# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CHECK = NEG          # контрольні біти — сині
COVER = "#eafaf0"    # покрита позиція / окіл кодового слова
FADED = "#f4f6f8"    # непокрита позиція
HOT   = "#fdecea"    # перекинутий біт / небезпека


# ── geometry: чому виправлення дорожче за виявлення ───────────────────────────
# Ідея: кодові слова — точки, биток — крок. За d=2 помилка сідає точно між двома
# словами (тільки виявити), за d=3 — лишається в околі свого (виправити одну).

def fig_geometry():
    W, H = 900, 470
    p = []

    # ── рядок A: d = 2 (парність) ──
    p.append(text(W / 2, 74, "d = 2 (парність): одна помилка лягає точно між кодовими словами",
                  size=13, color=INK, bold=True))
    yA = 140
    ax, mx, bx = 300, 460, 620
    p.append(line(ax, yA, bx, yA, color=MUTED, sw=1.6))
    p.append(rect(mx - 30, yA - 30, 60, 60, fill=HOT, stroke=POS, sw=1.4, rx=8))
    p.append(text((ax + mx) / 2, yA - 22, "1 биток", size=10.5, color=MUTED))
    p.append(text((mx + bx) / 2, yA - 22, "1 биток", size=10.5, color=MUTED))
    for x, lab in ((ax, "A"), (bx, "B")):
        p.append(circle(x, yA, 14, fill=FIELD, stroke=FIELD, sw=1.5))
        p.append(text(x, yA + 5, lab, size=13, color=BG, bold=True))
    p.append(circle(mx, yA, 11, fill=BG, stroke=POS, sw=2.2))
    p.append(text(mx, yA + 4, "×", size=13, color=POS, bold=True))
    p.append(text(mx, yA + 52, "однаково далеко від A і B — чиє це слово?", size=11, color=POS, bold=True))
    p.append(text(mx, yA + 70, "виявити можна, виправити — ні", size=10.5, color=MUTED))

    p.append(line(60, 232, W - 60, 232, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── рядок B: d = 3 ──
    p.append(text(W / 2, 270, "d = 3: одна помилка лишається ближчою до СВОГО слова",
                  size=13, color=INK, bold=True))
    yB = 344
    xs = [300, 410, 520, 630]     # A, m1, m2, B — рівні кроки, сумарна відстань 3
    p.append(line(xs[0], yB, xs[3], yB, color=MUTED, sw=1.6))
    p.append(rect(xs[0] - 26, yB - 28, (xs[1] - xs[0]) + 52, 56, fill=COVER, stroke=FIELD, sw=1.3, rx=10))
    p.append(rect(xs[2] - 26, yB - 28, (xs[3] - xs[2]) + 52, 56, fill=COVER, stroke=FIELD, sw=1.3, rx=10))
    p.append(text((xs[0] + xs[1]) / 2, yB - 36, "окіл A", size=10, color=FIELD, bold=True))
    p.append(text((xs[2] + xs[3]) / 2, yB - 36, "окіл B", size=10, color=FIELD, bold=True))
    for x, lab in ((xs[0], "A"), (xs[3], "B")):
        p.append(circle(x, yB, 14, fill=FIELD, stroke=FIELD, sw=1.5))
        p.append(text(x, yB + 5, lab, size=13, color=BG, bold=True))
    for x in (xs[1], xs[2]):
        p.append(circle(x, yB, 11, fill=BG, stroke=POS, sw=2.2))
        p.append(text(x, yB + 4, "×", size=13, color=POS, bold=True))
    p.append(text(xs[1], yB + 50, "→ до A", size=10.5, color=FIELD, bold=True))
    p.append(text(xs[2], yB + 50, "→ до B", size=10.5, color=FIELD, bold=True))
    p.append(text((xs[1] + xs[2]) / 2, yB + 70, "будь-який один крок → найближче слово однозначне",
                  size=11, color=INK))

    b, _, _ = textbox(W / 2, 442, "виявляє  d − 1  помилок      ·      виправляє  ⌊(d − 1)/2⌋",
                      size=12, pad=10, fill="#fbfcfd", stroke=INK, sw=1.4, bold=True)
    p.append(b)

    render(os.path.join(OUT, "geometry.svg"), W, H, *p,
           title="Виправлення дорожче за виявлення — воно вимагає більшої відстані між словами")


# ── syndrome: контрольні біти за степенями двійки → синдром = номер битка ─────
# Ідея: биток на позиції p ламає рівно ті контролі, чиї розряди стоять у p; тож
# зчитані згори вниз зламані контролі складають двійковий номер p.

def fig_syndrome():
    W, H = 940, 560
    p = []
    recv = [0, 1, 1, 0, 1, 1, 1]                      # прочитане слово (позиція 5 перекинута)
    roles = ["c1", "c2", "d1", "c4", "d2", "d3", "d4"]
    is_check = [True, True, False, True, False, False, False]
    flip_idx = 4                                      # позиція 5

    pitch, cw = 74, 60
    x0 = W / 2 - 7 * pitch / 2 + (pitch - cw) / 2

    # ── верх: прочитане слово ──
    p.append(text(W / 2, 62, "Прочитане слово — позицію 5 перекинуто", size=13, color=INK, bold=True))
    yw = 92
    for i in range(7):
        x = x0 + i * pitch
        hot = (i == flip_idx)
        col = CHECK if is_check[i] else INK
        p.append(text(x + cw / 2, yw - 10, str(i + 1), size=10, color=MUTED))
        p.append(rect(x, yw, cw, 44, fill=(HOT if hot else BG),
                      stroke=(POS if hot else col), sw=(2.4 if hot else 1.5), rx=5))
        p.append(text(x + cw / 2, yw + 29, str(recv[i]), size=17,
                      color=(POS if hot else INK), bold=True))
        p.append(text(x + cw / 2, yw + 62, roles[i], size=10.5,
                      color=(CHECK if is_check[i] else MUTED), bold=is_check[i]))
    p.append(text(W / 2, yw + 90, "сині — контрольні (позиції 1, 2, 4) · чорні — дані (3, 5, 6, 7)",
                  size=10.5, color=MUTED))

    # ── середина: три контролі та їхнє покриття ──
    covers = [
        ("№1", [0, 2, 4, 6], 1),
        ("№2", [1, 2, 5, 6], 0),
        ("№4", [3, 4, 5, 6], 1),
    ]
    ys, row_h = 232, 66
    scw, spitch = 30, 40
    sx0 = W / 2 - 7 * spitch / 2 + (spitch - scw) / 2 + 44
    for r, (lab, cov, parity) in enumerate(covers):
        y = ys + r * row_h
        p.append(text(sx0 - 58, y + scw / 2 + 4, "контроль " + lab, size=11,
                      color=CHECK, bold=True, anchor="end"))
        for i in range(7):
            x = sx0 + i * spitch
            covered = i in cov
            hot = (i == flip_idx and covered)
            fill = HOT if hot else (COVER if covered else FADED)
            stroke = POS if hot else (FIELD if covered else "#d8dde3")
            p.append(rect(x, y, scw, scw, fill=fill, stroke=stroke, sw=1.3, rx=3))
            if covered:
                p.append(text(x + scw / 2, y + scw / 2 + 5, str(recv[i]), size=12,
                              color=(POS if hot else INK), bold=True))
        ok = (parity == 0)
        p.append(text(sx0 + 7 * spitch + 10, y + scw / 2 + 5,
                      "= %d   %s" % (parity, "ціле" if ok else "зламано"),
                      size=12, color=(FIELD if ok else POS), bold=True, anchor="start"))

    # ── низ: збірка синдрому за вагами розрядів ──
    yb = 478
    p.append(text(W / 2, yb - 24, "Кожен зламаний контроль засвічує свій двійковий розряд:",
                  size=12, color=INK, bold=True))
    trio = [("c4", 4, 1), ("c2", 2, 0), ("c1", 1, 1)]     # (мітка, вага розряду, значення)
    tw = 52
    tx0 = W / 2 - (3 * tw + 170) / 2
    for k, (lab, wt, val) in enumerate(trio):
        x = tx0 + k * tw
        p.append(text(x + (tw - 8) / 2, yb - 8, lab, size=10.5, color=MUTED))
        p.append(rect(x, yb, tw - 8, 40, fill=(HOT if val else FADED),
                      stroke=(POS if val else MUTED), sw=1.6, rx=4))
        p.append(text(x + (tw - 8) / 2, yb + 26, str(val), size=17,
                      color=(POS if val else MUTED), bold=True))
        p.append(text(x + (tw - 8) / 2, yb + 55, "вага %d" % wt, size=9.5, color=MUTED))
    eqx = tx0 + 3 * tw + 12
    p.append(text(eqx, yb + 24, "= 4 + 1 = 5", size=16, color=INK, bold=True, anchor="start"))
    p.append(text(eqx, yb + 48, "→ биток на позиції 5", size=12, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "syndrome.svg"), W, H, *p,
           title="Синдром, прочитаний як двійкове число, дорівнює номеру перекинутого біта")


# ── layout: мапа 72-бітового слова (дані / контроль / загальна парність) ──────
# Ідея: показати, ДЕ у слові дані, а де контроль — контроль на степенях двійки,
# позиція 0 — загальна парність; звідси видно, чому код розкладає дані несуміжно.

def fig_layout():
    W, H = 880, 400
    p = []
    p.append(text(W / 2, 58, "72-бітове слово: 64 біти даних + 7 контрольних + 1 загальної парності",
                  size=13, color=INK, bold=True))

    cols = 24
    cw, gap = 28, 5
    grid_w = cols * (cw + gap) - gap
    x0 = (W - grid_w) / 2
    y0, rgap = 92, 20

    def is_pow2(n):
        return n > 0 and (n & (n - 1)) == 0

    for pos in range(72):
        r, c = pos // cols, pos % cols
        x = x0 + c * (cw + gap)
        y = y0 + r * (cw + rgap)
        if pos == 0:
            fill, stroke, lc, bold = COVER, FIELD, FIELD, True
        elif is_pow2(pos):
            fill, stroke, lc, bold = "#eaf0fd", CHECK, CHECK, True
        else:
            fill, stroke, lc, bold = BG, "#d8dde3", MUTED, False
        p.append(rect(x, y, cw, cw, fill=fill, stroke=stroke, sw=1.4, rx=4))
        p.append(text(x + cw / 2, y + cw / 2 + 4, str(pos), size=10, color=lc, bold=bold))

    # ── легенда: три ряди зі зразком-клітинкою ──
    ly = y0 + 3 * (cw + rgap) + 22
    legend = [
        (COVER, FIELD, "позиція 0 — біт загальної парності над усім словом (це вона робить SECDED)"),
        ("#eaf0fd", CHECK, "позиції 1, 2, 4, 8, 16, 32, 64 — сім контрольних бітів, по одному на розряд синдрому"),
        (BG, "#d8dde3", "решта 64 клітинки — біти даних 0…63, розкладені по позиціях за зростанням"),
    ]
    for i, (fill, stroke, s) in enumerate(legend):
        y = ly + i * 30
        p.append(rect(x0, y, cw, cw, fill=fill, stroke=stroke, sw=1.4, rx=4))
        p.append(text(x0 + cw + 12, y + cw / 2 + 5, s, size=11.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "layout.svg"), W, H, *p,
           title="Мапа 72-бітового слова: де дані, де контроль, де загальна парність")


# ── decode: рішення SECDED за синдромом s і загальною парністю g ──────────────
# Ідея: s каже ЯКИЙ біт битий, g каже СКІЛЬКИ (за парністю); разом — три випадки.

def fig_decode():
    W, H = 940, 430
    p = []
    p.append(text(W / 2, 50, "Рішення декодера: синдром s і загальна парність g — разом", size=13, color=INK, bold=True))
    p.append(text(W / 2, 72, "s = XOR номерів позицій з одиницею  ·  g = парність усіх 72 бітів",
                  size=11, color=MUTED))

    rows = [
        (["s = 0", "g = 0"], "СЛОВО ЦІЛЕ\nвіддати дані як є", FIELD, COVER),
        (["g = 1"],          "ВИПРАВИТИ позицію s\nперекинути біт s і віддати", CHECK, "#eaf0fd"),
        (["s ≠ 0", "g = 0"], "ПОДВІЙНА ПОМИЛКА\nтривога — дані не довіряти", POS, HOT),
    ]
    y = 128
    rh = 96
    for cond, outcome, col, bg in rows:
        cy = y
        chx = 96
        for ch in cond:
            b, w, h = textbox(chx + 0, cy, ch, size=13, pad=10, fill=BG, stroke=col, sw=1.7,
                              color=col, bold=True, min_w=64)
            p.append(b)
            chx += w + 16
        p.append(arrow(chx + 4, cy, chx + 62, cy, color=MUTED, sw=1.9))
        ob, ow, oh = textbox(W / 2 + 190, cy, outcome, size=12.5, pad=13, fill=bg, stroke=col,
                             sw=1.7, color=INK, bold=True, min_w=280)
        p.append(ob)
        y += rh

    render(os.path.join(OUT, "decode.svg"), W, H, *p,
           title="SECDED у трьох рядках: ціле · виправити один · виявити два")


# ── matrix-syndrome: s = H·e — помилка вибирає p-й стовпець, а він = двійка p ──
# Ідея: стовпець матриці перевірки з номером i — це двійковий запис i; одиночна
# помилка на позиції 5 витягає рівно 5-й стовпець (101), і це вже синдром = 5.

def fig_matrix_syndrome():
    W, H = 980, 440
    p = []

    mx0, pitch, cell = 200, 58, 46
    my0, rpitch = 120, 56
    hot_i = 4                                   # позиція 5 (індекс 4)
    grid = [[0, 0, 0, 1, 1, 1, 1],              # вага 4 (c4)
            [0, 1, 1, 0, 0, 1, 1],              # вага 2 (c2)
            [1, 0, 1, 0, 1, 0, 1]]              # вага 1 (c1)
    rlab = ["вага 4", "вага 2", "вага 1"]

    p.append(text(96, my0 + rpitch + 5, "H =", size=18, color=INK, bold=True))

    for i in range(7):                           # заголовки-номери позицій
        cx = mx0 + i * pitch + cell / 2
        hot = (i == hot_i)
        p.append(text(cx, my0 - 12, str(i + 1), size=12,
                      color=(POS if hot else MUTED), bold=hot))

    for r in range(3):                           # клітини матриці
        y = my0 + r * rpitch
        p.append(text(mx0 - 18, y + cell / 2 + 5, rlab[r], size=12, color=CHECK,
                      anchor="end"))
        for i in range(7):
            x = mx0 + i * pitch
            hot = (i == hot_i)
            p.append(rect(x, y, cell, cell,
                          fill=(COVER if hot else BG),
                          stroke=(FIELD if hot else "#cfd6de"), sw=1.3, rx=4))
            p.append(text(x + cell / 2, y + cell / 2 + 6, str(grid[r][i]), size=16,
                          color=(FIELD if hot else INK), bold=True))

    hx = mx0 + hot_i * pitch                      # рамка-виділення стовпця 5
    p.append(rect(hx - 5, my0 - 5, cell + 10, 2 * rpitch + cell + 10,
                  fill="none", stroke=POS, sw=1.8, rx=6))

    ax1, ax2, ay = 606, 700, my0 + rpitch + 5     # стрілка «вибирає стовпець 5»
    p.append(text((ax1 + ax2) / 2, ay - 16, "вибирає", size=11, color=POS, bold=True))
    p.append(arrow(ax1, ay, ax2, ay, color=POS, sw=2.0))
    p.append(text((ax1 + ax2) / 2, ay + 24, "стовпець 5", size=11, color=MUTED))

    sx = 716                                      # синдром-вектор s
    p.append(text(sx + cell / 2, my0 - 12, "синдром s", size=12, color=INK, bold=True))
    for r in range(3):
        y = my0 + r * rpitch
        v = grid[r][hot_i]
        p.append(rect(sx, y, cell, cell, fill=(HOT if v else FADED),
                      stroke=(POS if v else MUTED), sw=1.6, rx=4))
        p.append(text(sx + cell / 2, y + cell / 2 + 6, str(v), size=16,
                      color=(POS if v else MUTED), bold=True))
    p.append(text(sx + cell + 20, my0 + rpitch + 1, "= 101₂ = 5",
                  size=16, color=INK, bold=True, anchor="start"))
    p.append(text(sx + cell + 20, my0 + rpitch + 26, "→ биток на позиції 5",
                  size=12, color=POS, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, 402,
                      "Усі 7 стовпців — різні ненульові числа 1…7 → кожна одиночна помилка дає свій, ні з чим не сплутуваний синдром.",
                      size=12, pad=11, fill="#fbfcfd", stroke=INK, sw=1.3)
    p.append(b)

    render(os.path.join(OUT, "matrix-syndrome.svg"), W, H, *p,
           title="Синдром — це p-й стовпець матриці перевірки, а він = двійковий запис p")


# ── overhead-curve: надлишок (k+1)/n падає, поки k ледь росте ─────────────────
# Ідея: k росте як log₂n, тож частка надлишку тане з шириною слова.

def fig_overhead_curve():
    W, H = 940, 530
    p = []

    ns   = [8, 16, 32, 64, 128, 256, 512, 1024]
    ksec = [4, 5, 6, 7, 8, 9, 10, 11]
    ov   = [62.5, 37.5, 21.9, 12.5, 7.0, 3.9, 2.1, 1.2]

    xL, xR = 120, 880
    yTop, yBot = 140, 410
    scale = (yBot - yTop) / 65.0

    def X(i): return 150 + i * 100
    def Y(v): return yBot - v * scale

    for t in range(0, 61, 10):                    # сітка й вісь Y
        gy = Y(t)
        p.append(line(xL, gy, xR, gy, color="#e6eaef", sw=1.0, dash="4 5"))
        p.append(text(xL - 10, gy + 4, "%d%%" % t, size=11, color=MUTED, anchor="end"))
    p.append(line(xL, yTop, xL, yBot, color=INK, sw=1.5))
    p.append(line(xL, yBot, xR, yBot, color=INK, sw=1.5))
    p.append(text(xL, 112, "надлишок (k+1)/n", size=12, color=INK, bold=True, anchor="start"))

    for i in range(len(ns) - 1):                  # крива
        p.append(line(X(i), Y(ov[i]), X(i + 1), Y(ov[i + 1]), color=POS, sw=2.4))
    for i, v in enumerate(ov):
        x, y = X(i), Y(v)
        p.append(circle(x, y, 5.5, fill=BG, stroke=POS, sw=2.2))
        p.append(text(x, y - 14, "%.1f%%" % v, size=11, color=POS, bold=True))

    for i, n in enumerate(ns):                    # підписи осі X: n та k
        x = X(i)
        p.append(text(x, yBot + 22, str(n), size=12, color=INK, bold=True))
        p.append(text(x, yBot + 46, "k=%d" % ksec[i], size=11, color=CHECK, bold=True))
    p.append(text((xL + xR) / 2, yBot + 70,
                  "ширина слова n (біти даних)  ·  сині — контрольних бітів для SEC",
                  size=12, color=MUTED))

    b, _, _ = textbox(W / 2, yBot + 100,
                      "Дані більшають у 128 разів (8 → 1024), а контрольних бітів лише 4 → 11: k росте як log₂n, тож надлишок тане.",
                      size=12, pad=11, fill="#fbfcfd", stroke=INK, sw=1.3)
    p.append(b)

    render(os.path.join(OUT, "overhead-curve.svg"), W, H, *p,
           title="Ширше слово — дешевший захист: надлишок падає, а контрольних бітів ледь більшає")


if __name__ == "__main__":
    fig_geometry()
    fig_syndrome()
    fig_layout()
    fig_decode()
    fig_matrix_syndrome()
    fig_overhead_curve()
    print("figs: готово")
