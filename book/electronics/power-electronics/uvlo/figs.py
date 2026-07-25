# -*- coding: utf-8 -*-
"""Фігури до статті «Блокування за низькою напругою (UVLO)»
   (book/electronics/power-electronics/uvlo):
  - hysteresis.svg     — петля гістерезису: стан пристрою vs напруга живлення
  - partial-turnon.svg — Rds(on) MOSFET vs Vgs: чому недовідкритий ключ гріється
  - circuit.svg        — механізм: дільник + опора + компаратор + гістерезис
  - lineage.svg        — (вставка hist) родовід недонапругової оборони: дві гілки
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── фіг. 1. Петля гістерезису UVLO ───────────────────────────────────────────
def fig_hysteresis():
    W, H = 780, 440
    f = [text(W / 2, 30, "Два пороги й гістерезис: стан пристрою від напруги живлення",
              size=16, bold=True)]

    # осі
    x0, x1 = 130, 700          # вісь напруги
    yOFF, yON = 330, 130       # рівні станів
    yaxis_x = 130
    f.append(line(yaxis_x, 100, yaxis_x, 360, color=INK, sw=1.8))      # вісь Y (стан)
    f.append(line(x0, yOFF, 720, yOFF, color=INK, sw=1.8))             # вісь X (напруга)
    f.append(text(720, yOFF + 26, "напруга живлення →", size=12, color=MUTED, anchor="end"))

    # рівні станів
    f.append(text(120, yON + 5, "ON", size=13, bold=True, color=FIELD, anchor="end"))
    f.append(text(120, yOFF - 6, "OFF", size=13, bold=True, color=POS, anchor="end"))
    f.append(line(x0, yON, 700, yON, color="#d7dee6", sw=1, dash="3,4"))

    # два пороги
    xF, xR = 360, 510          # V_вимк (падіння), V_увімк (зростання)
    # смуга гістерезису
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff6e6" '
             'stroke="none"/>' % (xF, 110, xR - xF, 250))
    f.append(line(xF, 110, xF, yOFF, color="#b5732e", sw=1.6, dash="5,4"))
    f.append(line(xR, 110, xR, yOFF, color="#b5732e", sw=1.6, dash="5,4"))

    # петля: нижня гілка (OFF, напруга росте) → стрибок вгору на xR → верхня (ON, падає) → стрибок вниз на xF
    f.append(line(x0 + 8, yOFF, xR, yOFF, color=NEG, sw=3))            # OFF, росте
    f.append(line(xR, yOFF, xR, yON, color=NEG, sw=3))                # увімкнення
    f.append(line(xF, yON, 700, yON, color=POS, sw=3))                # ON, тримається/падає
    f.append(line(xF, yON, xF, yOFF, color=POS, sw=3))                # вимкнення
    # верхня гілка ON тягнеться і праворуч від xR (уже увімкнено) — та сама лінія вже є
    f.append(line(xR, yON, 700, yON, color=POS, sw=3))

    # стрілки напряму обходу
    f.append(arrow(250, yOFF, 300, yOFF, color=NEG, sw=2))            # → росте
    f.append(arrow(xR, 250, xR, 215, color=NEG, sw=2))               # ↑ увімкнення
    f.append(arrow(620, yON, 560, yON, color=POS, sw=2))            # ← падає
    f.append(arrow(xF, 215, xF, 250, color=POS, sw=2))              # ↓ вимкнення

    # підписи порогів (нижче осі, з запасом, щоб не налазили)
    f.append(text(xR, yOFF + 24, "V_увімк", size=12, bold=True, color="#b5732e"))
    f.append(text(xR, yOFF + 40, "(поріг зростання)", size=10.5, color=MUTED))
    f.append(text(xF, yOFF + 24, "V_вимк", size=12, bold=True, color="#b5732e"))
    f.append(text(xF, yOFF + 40, "(поріг падіння)", size=10.5, color=MUTED))

    # мітка гістерезису вгорі між порогами
    midx = (xF + xR) / 2
    f.append(line(xF, 96, xR, 96, color="#b5732e", sw=1.4))
    f.append(line(xF, 92, xF, 100, color="#b5732e", sw=1.4))
    f.append(line(xR, 92, xR, 100, color="#b5732e", sw=1.4))
    f.append(text(midx, 86, "гістерезис", size=12, bold=True, color="#b5732e"))

    # підписи гілок
    f.append(text(235, yON - 12, "працює — тримається ON, поки не впаде нижче V_вимк",
                  size=10.5, color=FIELD, anchor="start"))
    f.append(text(150, yOFF - 12, "заблоковано — тримається OFF, поки не підніметься до V_увімк",
                  size=10.5, color=NEG, anchor="start"))

    f.append(text(W / 2, 424,
                  "Немає порогу-точки: увімкнення й вимкнення рознесено. Проміжок між ними — гістерезис — не дає деренчати.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "hysteresis.svg"), W, H, *f)


# ── фіг. 2. Rds(on) vs Vgs: небезпека недовідкритого ключа ────────────────────
def fig_partial_turnon():
    W, H = 780, 450
    f = [text(W / 2, 30, "Чому недовідкритий ключ гріється: опір каналу від напруги на затворі",
              size=15.5, bold=True)]

    # рамка графіка
    gx0, gx1 = 120, 700
    gy0, gy1 = 90, 330         # gy0 — верх (великий Rds), gy1 — низ (малий Rds)
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.8))
    f.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.8))
    f.append(text(gx0 - 8, gy0 + 4, "Rds(on)", size=12, color=INK, anchor="end", bold=True))
    f.append(text(gx0 - 8, gy0 + 20, "великий", size=10, color=MUTED, anchor="end"))
    f.append(text(gx0 - 8, gy1 - 6, "малий", size=10, color=MUTED, anchor="end"))
    f.append(text(gx1, gy1 + 26, "Vgs (напруга затвір–витік) →", size=12, color=MUTED, anchor="end"))

    # мапа Vgs(В)→x та Rds(мОм)→y (лог по Rds)
    Vmin, Vmax = 2.5, 12.0
    def X(v): return gx0 + (v - Vmin) / (Vmax - Vmin) * (gx1 - gx0)
    rlo, rhi = 5.0, 3000.0
    def Y(r):
        t = (math.log10(r) - math.log10(rlo)) / (math.log10(rhi) - math.log10(rlo))
        return gy1 - t * (gy1 - gy0)   # більший Rds — вище

    pts = [(3.05, 3000), (3.3, 1400), (3.6, 500), (4.0, 160), (4.5, 50),
           (5.0, 26), (6.0, 12), (7.0, 8), (8.0, 6), (10.0, 5), (12.0, 5)]

    # небезпечна смуга: Vth..повне відкриття
    Vth, Vfull = 3.0, 7.0
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none"/>' % (X(Vth), gy0, X(Vfull) - X(Vth), gy1 - gy0))
    # безпечна смуга (повне відкриття)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" '
             'stroke="none"/>' % (X(Vfull), gy0, gx1 - X(Vfull), gy1 - gy0))

    # крива Rds(on)
    poly = " ".join("%.1f,%.1f" % (X(v), Y(r)) for v, r in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, INK))

    # поріг Vth
    f.append(line(X(Vth), gy0, X(Vth), gy1, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(X(Vth), gy1 + 16, "Vth", size=11, bold=True, color=MUTED))
    f.append(text(X(Vth), gy1 + 31, "(відкривається)", size=9.5, color=MUTED))

    # поріг UVLO у безпечній зоні
    xU = X(8.0)
    f.append(line(xU, gy0, xU, gy1, color=FIELD, sw=2, dash="6,4"))
    f.append(text(xU, gy0 - 4, "поріг UVLO", size=11, bold=True, color=FIELD))

    # підписи зон (короткі, у своїх смугах, над кривою)
    f.append(text((X(Vth) + X(Vfull)) / 2, 116, "сіра зона: недовідкрито", size=11.5, bold=True, color=POS))
    f.append(text((X(Vth) + X(Vfull)) / 2, 134, "Rds ↑↑ → ключ пече", size=10.5, color=POS))
    f.append(text(540, 300, "повне відкриття", size=11.5, bold=True, color=FIELD))

    # маркери двох точок на кривій (без виносних ліній — лише кружки)
    f.append(circle(X(4.5), Y(50), 4.2, fill=POS, stroke=POS, sw=1))
    f.append(circle(X(10.0), Y(5.0), 4.2, fill=FIELD, stroke=FIELD, sw=1))

    # єдина рамка-порівняння у відкритому верхньому правому полі
    body, bw, bh = textbox(585, 150,
        ["20 А через ключ:",
         "Vgs 4.5 В: Rds 50 мОм → 20 Вт",
         "Vgs 10 В: Rds 5 мОм → 2 Вт"],
        size=10.5, fill="#f8fafc", stroke="#c9d3dc", sw=1.3, pad=9)
    f.append(body)

    f.append(text(W / 2, 434,
                  "UVLO тримає ключ вимкненим, поки живлення не дійде в зелену зону — там, де затвор відкривається повністю.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "partial-turnon.svg"), W, H, *f)


# ── фіг. 3. Механізм UVLO: дільник + опора + компаратор + гістерезис ──────────
def fig_circuit():
    W, H = 780, 430
    f = [text(W / 2, 28, "Механізм: дільник вимірює живлення, компаратор рівняє його з опорою",
              size=15.5, bold=True)]

    # шина живлення
    railx0, railx1, raily = 90, 250, 78
    f.append(line(railx0, raily, railx1, raily, color=POS, sw=2.6))
    f.append(text(railx0, raily - 10, "V_in (живлення, що його стежимо)", size=11.5, color=POS, anchor="start", bold=True))

    # дільник R1/R2
    dx = 175
    f.append(line(dx, raily, dx, 118, color=INK, sw=2))
    f.append(rect(dx - 22, 118, 44, 46, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(dx, 146, "R1", size=12, bold=True))
    node_y = 196
    f.append(line(dx, 164, dx, node_y, color=INK, sw=2))
    f.append(circle(dx, node_y, 3.4, fill=INK, stroke=INK, sw=1))
    f.append(text(dx - 12, node_y - 6, "вузол", size=10, color=MUTED, anchor="end"))
    f.append(rect(dx - 22, 228, 44, 46, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(dx, 256, "R2", size=12, bold=True))
    f.append(line(dx, node_y, dx, 228, color=INK, sw=2))
    f.append(line(dx, 274, dx, 320, color=INK, sw=2))
    # земля
    f.append(line(dx - 20, 320, dx + 20, 320, color=INK, sw=2))
    f.append(line(dx - 12, 326, dx + 12, 326, color=INK, sw=2))
    f.append(line(dx - 5, 332, dx + 5, 332, color=INK, sw=2))
    f.append(text(dx, 348, "GND", size=10, bold=True))

    # компаратор (трикутник)
    cx0, cyt, cyb = 360, 150, 250      # ліва грань трикутника
    ctipx, ctipy = 470, 200
    f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f Z" fill="#eef2f7" '
             'stroke="%s" stroke-width="2"/>' % (cx0, cyt, cx0, cyb, ctipx, ctipy, INK))
    f.append(text((cx0 + ctipx) / 2 - 6, ctipy + 5, "компаратор", size=10.5, bold=True))

    # + вхід (від вузла дільника), зверху
    f.append(line(dx, node_y, cx0, 175, color=INK, sw=2))
    f.append(plus(cx0 + 16, 175, r=8))
    # − вхід (від опори), знизу
    f.append(minus(cx0 + 16, 225, r=8))

    # опорне джерело
    f.append(rect(230, 262, 96, 50, fill="#f0ecff", stroke="#6b46c1", sw=1.8))
    f.append(text(278, 284, "опора", size=11, bold=True, color="#6b46c1"))
    f.append(text(278, 300, "Uref ≈ 1.2 В", size=10.5, color="#6b46c1"))
    f.append(line(326, 287, 344, 287, color=INK, sw=2))
    f.append(line(344, 287, 344, 225, color=INK, sw=2))
    f.append(line(344, 225, cx0, 225, color=INK, sw=2))

    # вихід компаратора → вузол виходу → пристрій
    outx = 470
    f.append(line(ctipx, ctipy, 560, ctipy, color=INK, sw=2))
    f.append(circle(540, ctipy, 3.4, fill=INK, stroke=INK, sw=1))
    f.append(rect(560, 172, 150, 56, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(635, 196, "дозвіл (EN) →", size=11, bold=True, color=FIELD))
    f.append(text(635, 214, "драйвер / контролер", size=10.5, color=INK))

    # гістерезис: додатний зв'язок з виходу назад до «+» входу
    f.append(line(540, ctipy, 540, 120, color="#b5732e", sw=1.8))
    f.append(rect(430, 108, 44, 24, fill=BG, stroke="#b5732e", sw=1.6, rx=0))
    f.append(text(452, 125, "R_гіст", size=10.5, bold=True, color="#b5732e"))
    f.append(line(540, 120, 474, 120, color="#b5732e", sw=1.8))
    f.append(line(430, 120, 300, 120, color="#b5732e", sw=1.8))
    f.append(line(300, 120, 300, 175, color="#b5732e", sw=1.8))
    f.append(line(300, 175, cx0, 175, color="#b5732e", sw=1.8))
    f.append(text(452, 100, "додатний зв'язок → гістерезис", size=10, color="#b5732e", bold=True))

    # підпис знизу
    body, bw, bh = textbox(W / 2, 392,
        ["Вузол вище опори → вихід дозволяє роботу; нижче — блокує. R_гіст зсуває поріг залежно від",
         "стану виходу, тож увімкнення й вимкнення стаються за різних V_in — це і є гістерезис."],
        size=10.5, fill="#f6f8fb", stroke="#c9d3dc", sw=1.2, pad=9)
    f.append(body)

    render(os.path.join(IMG, "circuit.svg"), W, H, *f)


# ── фіг. 4 (вставка math). Той самий вузол EN — дві задачі ────────────────────
def fig_node_states():
    W, H = 860, 470
    f = [text(W / 2, 30, "Той самий дільник, дві задачі: увімкнення й вимкнення",
              size=16, bold=True)]

    # ── ліворуч: дільник R1/R2 на виводі EN з джерелом I_hys ──
    dx = 190
    f.append(line(dx - 72, 80, dx + 72, 80, color=POS, sw=2.6))
    f.append(text(dx, 68, "V_in (жива шина)", size=11.5, bold=True, color=POS))
    # R1
    f.append(line(dx, 80, dx, 110, color=INK, sw=2))
    f.append(rect(dx - 22, 110, 44, 46, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(dx, 138, "R1", size=12, bold=True))
    # вузол
    node_y = 210
    f.append(line(dx, 156, dx, node_y, color=INK, sw=2))
    f.append(circle(dx, node_y, 3.6, fill=INK, stroke=INK, sw=1))
    f.append(text(dx + 12, node_y - 8, "вузол EN (v)", size=10.5, color=MUTED, anchor="start"))
    # R2
    f.append(rect(dx - 22, 242, 44, 46, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(dx, 270, "R2", size=12, bold=True))
    f.append(line(dx, node_y, dx, 242, color=INK, sw=2))
    f.append(line(dx, 288, dx, 324, color=INK, sw=2))
    # земля
    f.append(line(dx - 18, 324, dx + 18, 324, color=INK, sw=2))
    f.append(line(dx - 11, 330, dx + 11, 330, color=INK, sw=2))
    f.append(line(dx - 4, 336, dx + 4, 336, color=INK, sw=2))
    f.append(text(dx, 352, "GND", size=10, bold=True))
    # порівняння з опорою — праворуч від вузла
    f.append(line(dx, node_y, dx + 74, node_y, color=INK, sw=1.6))
    f.append(text(dx + 80, node_y - 6, "спрацьовує коли", size=10, color=MUTED, anchor="start"))
    f.append(text(dx + 80, node_y + 10, "v = Uref ≈ 1.2 В", size=10.5, color="#6b46c1", anchor="start", bold=True))
    # джерело I_hys — вливається у вузол зліва, лише коли ON
    ihx, ihy = dx - 78, node_y
    f.append(circle(ihx, ihy, 16, fill="#fff6e6", stroke="#b5732e", sw=1.8))
    f.append(line(ihx, ihy - 9, ihx, ihy + 9, color="#b5732e", sw=1.6))
    f.append(line(ihx, ihy - 9, ihx - 4, ihy - 3, color="#b5732e", sw=1.6))
    f.append(line(ihx, ihy - 9, ihx + 4, ihy - 3, color="#b5732e", sw=1.6))
    f.append(arrow(ihx + 16, ihy, dx - 4, ihy, color="#b5732e", sw=1.8))
    f.append(text(ihx, ihy - 26, "I_hys", size=11.5, bold=True, color="#b5732e"))
    f.append(text(ihx - 4, ihy + 34, "тільки коли", size=9.5, color="#b5732e"))
    f.append(text(ihx - 4, ihy + 47, "вихід ON", size=9.5, color="#b5732e", bold=True))

    # ── праворуч: дві задачі + результат ──
    cxr = 620
    off, offw, offh = textbox(cxr, 120,
        ["Вихід OFF — чекаємо старту (I_hys нема):",
         "(V_in − Uref) / R1  =  Uref / R2",
         "⟹  V_увімк = Uref · (1 + R1/R2)"],
        size=11.5, fill="#fdecea", stroke="#c0392b", sw=1.4, pad=11)
    f.append(off)
    on, onw, onh = textbox(cxr, 232,
        ["Вихід ON — уже працює (+I_hys у вузол):",
         "(V_in − Uref) / R1 + I_hys = Uref / R2",
         "⟹  V_вимк = V_увімк − I_hys · R1"],
        size=11.5, fill="#eafaf0", stroke="#27ae60", sw=1.4, pad=11)
    f.append(on)
    res, rw, rh = textbox(cxr, 330,
        ["гістерезис:  ΔV = V_увімк − V_вимк = I_hys · R1"],
        size=12.5, fill="#fff6e6", stroke="#b5732e", sw=1.8, pad=12, bold=True, color="#8a5522")
    f.append(res)

    f.append(text(W / 2, 452,
                  "Різниця між станами — один доданок I_hys·R1. Він і зсуває нижній поріг униз від верхнього.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "uvlo-node-states.svg"), W, H, *f)


# ── фіг. 5 (вставка math). Коридор порогів із розкидом ────────────────────────
def fig_threshold_corridor():
    W, H = 820, 480
    f = [text(W / 2, 30, "Коридор порогів: обидва пороги з розкидом мусять влізти між стелею і підлогою",
              size=14.5, bold=True)]

    # вісь напруги
    ax = 150
    Vlo, Vhi = 6.4, 9.3
    ytop, ybot = 80, 400
    def Y(v): return ybot - (v - Vlo) / (Vhi - Vlo) * (ybot - ytop)
    f.append(line(ax, ytop - 6, ax, ybot + 6, color=INK, sw=1.8))
    f.append(text(ax - 40, ytop - 12, "В", size=12, color=INK, bold=True))
    for v in [6.5, 7.0, 7.5, 8.0, 8.5, 9.0]:
        f.append(line(ax - 5, Y(v), ax, Y(v), color=INK, sw=1.4))
        f.append(text(ax - 10, Y(v) + 4, "%.1f" % v, size=10.5, color=MUTED, anchor="end"))

    xL, xR = ax, 770
    # стеля: джерело гарантує під навантаженням (9.0)
    Vceil = 9.0
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" stroke="none"/>'
             % (xL, ytop, xR - xL, Y(Vceil) - ytop))
    f.append(line(xL, Y(Vceil), xR, Y(Vceil), color=FIELD, sw=2.2))
    f.append(text(xR, Y(Vceil) - 8, "стеля: джерело гарантує ≥ 9.0 В під навантаженням", size=10.5, color=FIELD, anchor="end", bold=True))
    # підлога: нижче — робота небезпечна (6.8)
    Vfloor = 6.8
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="none"/>'
             % (xL, Y(Vfloor), xR - xL, ybot - Y(Vfloor)))
    f.append(line(xL, Y(Vfloor), xR, Y(Vfloor), color=POS, sw=2.2))
    f.append(text(xR, Y(Vfloor) + 16, "підлога: нижче 6.8 В вузол уже працює хибно", size=10.5, color=POS, anchor="end", bold=True))

    # смуга V_увімк: 8.27..8.73 (розкид), номінал 8.5
    xa, xb = 250, 420
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dfe8ff" stroke="#2457d6" stroke-width="1.5"/>'
             % (xa, Y(8.73), xb - xa, Y(8.27) - Y(8.73)))
    f.append(line(xa, Y(8.5), xb, Y(8.5), color=NEG, sw=2, dash="5,4"))
    f.append(text((xa + xb) / 2, Y(8.73) - 10, "V_увімк", size=12, bold=True, color=NEG))
    f.append(text((xa + xb) / 2, Y(8.27) + 18, "8.5 ± 0.23 В", size=10, color=NEG))

    # смуга V_вимк: 7.0..8.0 (ширша — винен I_hys), номінал 7.5
    xc, xd = 470, 700
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ffe9d6" stroke="#b5732e" stroke-width="1.5"/>'
             % (xc, Y(8.0), xd - xc, Y(7.0) - Y(8.0)))
    f.append(line(xc, Y(7.5), xd, Y(7.5), color="#b5732e", sw=2, dash="5,4"))
    f.append(text((xc + xd) / 2, Y(8.0) - 10, "V_вимк", size=12, bold=True, color="#b5732e"))
    f.append(text((xc + xd) / 2, Y(7.0) + 18, "7.5 В, розкид 7.0–8.0", size=10, color="#b5732e"))
    f.append(text((xc + xd) / 2, Y(7.0) + 33, "(ширший — винен I_hys)", size=9.5, color="#b5732e", italic=True))

    f.append(text(W / 2, 462,
                  "V_увімк-мін мусить лишатись під стелею (пристрій стартує), V_вимк-макс — над підлогою (не гасне зарано).",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "uvlo-threshold-corridor.svg"), W, H, *f)


# ── фіг. 6 (вставка hist). Родовід недонапругової оборони: дві гілки ───────────
def fig_lineage():
    W, H = 900, 560
    PWR = "#b5732e"   # силова гілка (теплий)
    DIG = NEG         # цифрова гілка (холодний)
    f = [text(W / 2, 30, "Родовід недонапругової оборони: один принцип, дві гілки",
              size=16, bold=True)]

    # ── спільний корінь угорі ──
    rootx, rooty = W / 2, 92
    root, rw, rh = textbox(rootx, rooty,
        ["Спільна біда: живлення в «сірій зоні» — вже є, та замало",
         "Спільні цеглинки: опора (бандгеп) + компаратор + гістерезис"],
        size=11.5, fill="#f2f4f7", stroke=INK, sw=1.8, pad=12, bold=False)
    f.append(root)

    # заголовки гілок
    lx, rx = 235, 665           # центри колонок
    ytops = 190
    f.append(textbox(lx, ytops, ["Цифрова гілка", "сторож тримає ЧІП у скиданні"],
                     size=12, fill="#eaf0fd", stroke=DIG, sw=1.8, pad=9, color=DIG, bold=True)[0])
    f.append(textbox(rx, ytops, ["Силова гілка", "lockout вимикає СИЛОВИЙ каскад"],
                     size=12, fill="#fff2e2", stroke=PWR, sw=1.8, pad=9, color=PWR, bold=True)[0])

    # лінії від кореня до заголовків гілок
    f.append(line(rootx - 60, rooty + rh / 2, lx, ytops - 26, color=INK, sw=1.6))
    f.append(line(rootx + 60, rooty + rh / 2, rx, ytops - 26, color=INK, sw=1.6))

    # ── вузли-предки → нащадки (кожен: партномер + рік + роль) ──
    def node(cx, cy, name, year, role, col):
        body, bw, bh = textbox(cx, cy, [name + "   " + year, role],
                               size=11, fill=BG, stroke=col, sw=1.6, pad=9, min_w=210)
        return body, bh

    yA, yB, yC = 268, 360, 452

    # ліва колонка (цифрова): MC34064 → MAX690 / DS1232
    b, hA = node(lx, yA, "MC34064", "1980-ті", "трипіновий детектор: reset", DIG); f.append(b)
    b, hB = node(lx, yB, "MAX690 · DS1232", "кін. 1980-х", "супервізор: reset+watchdog", DIG); f.append(b)
    f.append(arrow(lx, yA + hA / 2, lx, yB - hB / 2, color=DIG, sw=2))

    # права колонка (силова): SG1524 → UC3842 → IR2110
    b, hA2 = node(rx, yA, "SG1524", "1976", "перший ШІМ-контролер", PWR); f.append(b)
    b, hB2 = node(rx, yB, "UC3842", "1980-ті", "UVLO 16/10 В у контролері", PWR); f.append(b)
    b, hC2 = node(rx, yC, "IR2110", "~1990", "UVLO в драйвері затвора", PWR); f.append(b)
    f.append(arrow(rx, yA + hA2 / 2, rx, yB - hB2 / 2, color=PWR, sw=2))
    f.append(arrow(rx, yB + hB2 / 2, rx, yC - hC2 / 2, color=PWR, sw=2))

    # підпис-висновок унизу
    body, bw, bh = textbox(W / 2, 520,
        ["Спільний предок — ідея «бандгеп + компаратор + гістерезис». Далі дороги розійшлися:",
         "цифрова гілка тримає процесор у reset, силова — глушить драйвер і перетворювач."],
        size=11, fill="#f6f8fb", stroke="#c9d3dc", sw=1.2, pad=10, color=MUTED)
    f.append(body)

    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hysteresis()
    fig_partial_turnon()
    fig_circuit()
    fig_node_states()
    fig_threshold_corridor()
    fig_lineage()
    print("Готово: 6 фігур (3 статті + 2 math + 1 hist) у", IMG)
