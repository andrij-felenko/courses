# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

A_FILL = "#dfe8fc"
B_FILL = "#dff0e6"
GREY_FILL = "#e3e7ec"
WARM_FILL = "#fff4e0"
RED_FILL = "#fbe6e3"
FREE = "#ffffff"
WARM = "#b8860b"


# ── 1. Коли обирається номер блока ─────────────────────────────────────────
def fig_when_allocated():
    W, H = 1160, 720
    p = []
    p.append(text(W / 2, 40, "коли обирається номер блока", size=17, bold=True, color=INK))

    BX, BW, NC = 250, 840, 24
    CW = BW / NC

    def band(y, h, cells):
        out = ""
        for i in range(NC):
            kind = cells.get(i)
            fill = FREE if kind is None else (A_FILL if kind == "A" else B_FILL)
            stroke = MUTED if kind is None else (NEG if kind == "A" else FIELD)
            out += rect(BX + i * CW, y, CW, h, fill=fill, stroke=stroke, sw=1.2, rx=2)
            if kind is not None:
                out += text(BX + i * CW + CW / 2, y + h / 2 + 5, kind,
                            size=13, bold=True, color=(NEG if kind == "A" else FIELD))
        return out

    pill_xs = [250, 390, 530, 670, 810, 950]
    pill_kinds = ["A", "B", "A", "B", "A", "B"]

    def pills(y):
        out = ""
        for x, k in zip(pill_xs, pill_kinds):
            fill = A_FILL if k == "A" else B_FILL
            stroke = NEG if k == "A" else FIELD
            out += rect(x, y, 110, 42, fill=fill, stroke=stroke, sw=1.6, rx=6)
            out += text(x + 55, y + 27, "write " + k, size=13.5, bold=True,
                        color=(NEG if k == "A" else FIELD))
        return out

    # ── верхня доріжка: вибір на кожному write
    p.append(text(40, 86, "вибір під час кожного write", size=15, bold=True,
                  color=POS, anchor="start"))
    p.append(pills(112))
    for x in pill_xs:
        p.append(arrow(x + 55, 158, x + 55, 212, color=MUTED, sw=1.5))
    p.append(band(216, 54, {0: "A", 1: "B", 2: "A", 3: "B", 4: "A", 5: "B"}))
    p.append(text(BX, 300, "A: 3 екстенти", size=14, bold=True, color=NEG, anchor="start"))
    p.append(text(BX + 220, 300, "B: 3 екстенти", size=14, bold=True, color=FIELD, anchor="start"))
    p.append(text(BX + 470, 300, "кожен вибір спирався на знання про 4 КіБ",
                  size=13.5, color=MUTED, anchor="start"))

    p.append(line(40, 352, W - 40, 352, color=MUTED, sw=1, dash="6,6"))

    # ── нижня доріжка: відкладене виділення
    p.append(text(40, 400, "вибір на виштовхуванні", size=15, bold=True,
                  color=FIELD, anchor="start"))
    p.append(pills(428))
    for x in pill_xs:
        p.append(arrow(x + 55, 474, x + 55, 512, color=MUTED, sw=1.5))
    p.append(fitbox(BX, 516, BW, 62,
                    ["кеш сторінок: брудні сторінки A і B,",
                     "зарезервовано 6 блоків — адрес іще немає"],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2))
    p.append(arrow(BX + BW / 2, 582, BX + BW / 2, 630, color=WARM, sw=2))
    p.append(text(BX + BW / 2 + 22, 610, "виштовхування", size=13.5, color=WARM,
                  anchor="start", bold=True))
    p.append(band(634, 54, {0: "A", 1: "A", 2: "A", 3: "B", 4: "B", 5: "B"}))
    p.append(text(BX, 712, "A: 1 екстент", size=14, bold=True, color=NEG, anchor="start"))
    p.append(text(BX + 220, 712, "B: 1 екстент", size=14, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'when-allocated.svg'), W, H + 20, *p)


# ── 2. Три стани діапазону у файлі ─────────────────────────────────────────
def fig_three_states():
    W, H = 1200, 400
    p = []
    p.append(text(W / 2, 40, "три стани діапазону у файлі", size=17, bold=True, color=INK))

    cols = [210, 160, 270, 160, 300]
    heads = ["стан діапазону", "блоки\nзакріплено", "що поверне read",
             "враховує\nst_blocks", "що робить перший запис"]
    rows = [
        (GREY_FILL, MUTED, ["діра"], ["ні"], ["нулі"], ["ні"],
         ["виділяє блоки", "й пише в них"]),
        (WARM_FILL, WARM, ["незаписаний", "екстент"], ["так"],
         ["нулі, без звертання", "до носія"], ["так"],
         ["розколює екстент,", "знімає ознаку"]),
        (B_FILL, FIELD, ["записаний", "екстент"], ["так"], ["дані"], ["так"],
         ["перезаписує", "на місці"]),
    ]

    x0, y0 = 40, 76
    xs = []
    x = x0
    for c in cols:
        xs.append(x)
        x += c

    for i, h in enumerate(heads):
        p.append(fitbox(xs[i], y0, cols[i], 56, h.split("\n"), size=13.5,
                        fill=FILL, stroke=INK, sw=1.6, bold=True))

    ry = y0 + 62
    for fill, stroke, *cells in rows:
        for i, cell in enumerate(cells):
            p.append(fitbox(xs[i], ry, cols[i], 72, cell, size=13.5,
                            fill=(fill if i == 0 else FREE),
                            stroke=stroke, sw=(2 if i == 0 else 1.3),
                            bold=(i == 0)))
        ry += 78

    render(os.path.join(IMG, 'three-states.svg'), W, ry + 20, *p)


# ── 3. Занепад вільного місця ──────────────────────────────────────────────
def fig_free_space_decay():
    W, H = 1200, 600
    p = []
    p.append(text(W / 2, 40, "роздроблення вільного місця", size=17, bold=True, color=INK))

    BX, BW, NC = 40, 1120, 50
    CW = BW / NC

    def band(y, h, used):
        out = ""
        for i in range(NC):
            taken = i in used
            out += rect(BX + i * CW, y, CW, h,
                        fill=(GREY_FILL if taken else FREE),
                        stroke=(MUTED if taken else "#c3c9d2"), sw=1.1, rx=2)
        return out

    young = set(range(0, 12))
    aged = {1, 4, 5, 9, 14, 18, 19, 24, 28, 33, 37, 41, 46}

    p.append(text(BX, 84, "молода файлова система", size=15, bold=True,
                  color=FIELD, anchor="start"))
    p.append(band(100, 50, young))
    p.append(text(W / 2, 182,
                  "вільне лежить однією смугою — запит на 256 блоків поспіль дає один екстент",
                  size=14, color=INK))

    p.append(text(BX, 232, "та сама, через рік роботи", size=15, bold=True,
                  color=POS, anchor="start"))
    p.append(band(248, 50, aged))
    p.append(text(W / 2, 330,
                  "вільного стільки ж — але найдовша суцільна ділянка вже коротша за запит",
                  size=14, color=INK))

    boxes = [
        (60, "роздроблене\nвільне місце"),
        (450, "нові файли\nлягають шматками"),
        (840, "видалення лишає\nще дрібніші дірки"),
    ]
    by, bh, bw = 372, 92, 300
    for bx, label in boxes:
        p.append(fitbox(bx, by, bw, bh, label.split("\n"), size=14.5,
                        fill=RED_FILL, stroke=POS, sw=2, bold=True))
    p.append(arrow(60 + bw + 10, by + bh / 2, 440, by + bh / 2, color=POS, sw=2))
    p.append(arrow(450 + bw + 10, by + bh / 2, 830, by + bh / 2, color=POS, sw=2))

    p.append(line(990, by + bh, 990, 500, color=POS, sw=2))
    p.append(line(990, 500, 210, 500, color=POS, sw=2))
    p.append(arrow(210, 500, 210, by + bh + 4, color=POS, sw=2))
    p.append(text(W / 2, 534, "коло замикається саме на себе", size=14,
                  color=POS, bold=True))

    render(os.path.join(IMG, 'free-space-decay.svg'), W, 560, *p)


# ── 4. Частка накладних від довжини екстента ───────────────────────────────
def _polyline(pts, color, sw=2.4):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" />' % (s, color, sw)


def fig_threshold():
    import math
    W, H = 1080, 600
    X0, X1, YT, YB = 130.0, 1010.0, 110.0, 470.0
    LO2, HI2 = 12.0, 26.0          # log2 меж по осі L: 4 КіБ … 64 МіБ

    def xf(L):
        return X0 + (math.log(L, 2) - LO2) / (HI2 - LO2) * (X1 - X0)

    def yf(a):
        return YB - a * (YB - YT)

    p = []
    p.append(text(W / 2, 38, "яку частку часу з'їдають накладні", size=17, bold=True, color=INK))
    p.append(text(X0, 92, "α — частка часу читання, витрачена на початки запитів",
                  size=13.5, color=MUTED, anchor="start"))

    # осі та поділки
    p.append(line(X0, YT, X0, YB, color=INK, sw=1.6))
    p.append(line(X0, YB, X1, YB, color=INK, sw=1.6))
    for a in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        y = yf(a)
        p.append(line(X0 - 6, y, X0, y, color=INK, sw=1.4))
        p.append(text(X0 - 14, y + 5, ("%.1f" % a), size=13, color=MUTED, anchor="end"))
    for e, lab in ((12, "4 КіБ"), (16, "64 КіБ"), (18, "256 КіБ"), (20, "1 МіБ"),
                   (22, "4 МіБ"), (24, "16 МіБ"), (26, "64 МіБ")):
        x = xf(2.0 ** e)
        p.append(line(x, YB, x, YB + 6, color=INK, sw=1.4))
        p.append(text(x, YB + 25, lab, size=13, color=MUTED))
    p.append(text((X0 + X1) / 2, YB + 58, "середня довжина екстента L (шкала подвоєнь)",
                  size=14, color=INK))

    # рівень α = ½
    p.append(line(X0, yf(0.5), X1, yf(0.5), color=MUTED, sw=1.2, dash="7,6"))
    p.append(text(X1, yf(0.5) - 10, "α = ½: накладні зрівнялися з передаванням даних",
                  size=13, color=MUTED, anchor="end"))

    # криві α(L) = 1/(1 + L/L₀)
    for L0, col in ((1.2e6, POS), (240e3, NEG)):
        pts = []
        for i in range(121):
            L = 2.0 ** (LO2 + (HI2 - LO2) * i / 120.0)
            pts.append((xf(L), yf(1.0 / (1.0 + L / L0))))
        p.append(_polyline(pts, col))
        p.append(circle(xf(L0), yf(0.5), 6, fill=BG, stroke=col, sw=2.6))

    p.append(text(X1, 150, "обертовий диск: L₀ = 150 МБ/с · 8 мс = 1.2 МБ",
                  size=14, bold=True, color=POS, anchor="end"))
    p.append(text(X1, 182, "NVMe, черга 1: L₀ = 3 ГБ/с · 80 мкс = 240 кБ",
                  size=14, bold=True, color=NEG, anchor="end"))

    p.append(text(W / 2, 566, "кружок на кривій — точка L = L₀, де накладні дорівнюють часу передавання",
                  size=13.5, color=MUTED))

    render(os.path.join(IMG, 'fragmentation-threshold.svg'), W, 586, *p)


# ── 5. Розмір блока: два профілі ───────────────────────────────────────────
def fig_block_size():
    W = 1210
    cols = [250, 195, 210, 220, 285]
    heads = ["профіль", "хвости при\nb = 4 КіБ", "хвости при\nb = 64 КіБ",
             "стеля втрати часу, NVMe:\n4 КіБ → 64 КіБ", "що вибрати"]
    rows = [
        (A_FILL, NEG,
         ["10⁶ файлів по 6 КіБ", "корисних даних 5.7 ГіБ"],
         ["1.91 ГіБ", "+33 % обсягу"],
         ["55.3 ГіБ", "×10.7 обсягу"],
         ["×59 → ×4.7", "дах є, але задорого"],
         ["4 КіБ і дрібніше; далі рятує", "лише пакування хвостів", "у сам inode"]),
        (B_FILL, FIELD,
         ["100 файлів по 20 ГіБ", "корисних даних 1.95 ТіБ"],
         ["195 КіБ", "≈ 10⁻⁷ обсягу"],
         ["3.1 МіБ", "≈ 1.5·10⁻⁶ обсягу"],
         ["×59 → ×4.7", "дах задарма"],
         ["найбільший, який дозволяє", "файлова система"]),
    ]

    p = []
    p.append(text(W / 2, 38, "розмір блока: та сама формула, протилежні відповіді",
                  size=17, bold=True, color=INK))

    x0, y0 = 30, 72
    xs, x = [], x0
    for c in cols:
        xs.append(x)
        x += c

    for i, h in enumerate(heads):
        p.append(fitbox(xs[i], y0, cols[i], 62, h.split("\n"), size=13.5,
                        fill=FILL, stroke=INK, sw=1.6, bold=True))

    ry = y0 + 70
    for fill, stroke, *cells in rows:
        for i, cell in enumerate(cells):
            p.append(fitbox(xs[i], ry, cols[i], 88, cell, size=13.5,
                            fill=(fill if i == 0 else FREE),
                            stroke=stroke, sw=(2 if i == 0 else 1.3),
                            bold=(i == 0)))
        ry += 96

    p.append(text(W / 2, ry + 24,
                  "втрата місця залежить від профілю, стеля втрати часу — ні",
                  size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'block-size-tradeoff.svg'), W, ry + 46, *p)


# ── 6. Що показує FIEMAP до і після примусової синхронізації ───────────────
def fig_fiemap_sync():
    W = 1180
    p = []
    p.append(text(W / 2, 40, "той самий файл, дві відповіді FIEMAP",
                  size=17, bold=True, color=INK))

    LX, LW = 40, 250
    BX, BW = 330, 810

    # без прапорця — карта наміру
    y = 92
    p.append(fitbox(LX, y, LW, 66, ["fm_flags = 0"], size=14.5, bold=True,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(rect(BX, y, BW, 66, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=4))
    p.append(text(BX + BW / 2, y + 28, "1 екстент з ознакою delalloc",
                  size=14.5, bold=True, color=WARM))
    p.append(text(BX + BW / 2, y + 50, "fe_physical = 0: блоки ще не обрано",
                  size=13, color=MUTED))
    p.append(text(BX, y + 100, "виміряно намір програми, а не розкладку на носії",
                  size=14, color=INK, anchor="start"))

    # з прапорцем — карта носія
    y2 = 258
    p.append(fitbox(LX, y2, LW, 66, ["fm_flags =", "FIEMAP_FLAG_SYNC"],
                    size=13.5, bold=True, fill=B_FILL, stroke=FIELD, sw=1.8))
    segs = [70, 34, 96, 28, 52, 120, 40, 26, 84, 60, 32, 74]
    gap = 12
    scale = BW / (sum(segs) + gap * (len(segs) - 1))
    x = BX
    for s in segs:
        p.append(rect(x, y2, s * scale, 66, fill=B_FILL, stroke=FIELD, sw=1.5, rx=3))
        x += (s + gap) * scale
    p.append(text(BX, y2 + 100,
                  "той самий файл після виштовхування: 12 екстентів із фізичними адресами",
                  size=14, color=INK, anchor="start"))

    render(os.path.join(IMG, 'fiemap-sync.svg'), W, y2 + 124, *p)


fig_when_allocated()
fig_three_states()
fig_free_space_decay()
fig_threshold()
fig_block_size()
fig_fiemap_sync()
print("ok")
