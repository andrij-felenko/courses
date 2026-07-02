# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Один опір проти частотної залежності: імпеданс як спектр ─────────────
def fig_spectrum():
    W, H = 720, 360
    els = []
    # осі
    ox, oy = 90, 300           # початок координат
    ax_r = 640                 # правий край осі X
    ax_t = 60                  # верх осі Y
    els.append(line(ox, oy, ax_r, oy, INK, 2))          # X
    els.append(line(ox, oy, ox, ax_t, INK, 2))          # Y
    els.append(arrow(ax_r - 4, oy, ax_r + 8, oy, INK))
    els.append(arrow(ox, ax_t + 4, ox, ax_t - 8, INK))
    els.append(text(ax_r + 4, oy + 20, "частота (лог)", size=13, color=MUTED, anchor="end"))
    els.append(text(ox - 12, ax_t + 4, "|Z|", size=14, color=INK, anchor="end", bold=True))

    # мітки частот
    for xf, lab in [(150, "0.1 Гц"), (300, "10 Гц"), (450, "1 кГц"), (580, "100 кГц")]:
        els.append(line(xf, oy, xf, oy + 5, MUTED, 1.2))
        els.append(text(xf, oy + 20, lab, size=11, color=MUTED))

    # крива |Z|(f): високий на низьких f (дифузія), спад до мінімуму (омічний),
    # ріст на високих f (індуктивність)
    pts = [(150, 110), (210, 160), (270, 210), (330, 245), (400, 262),
           (460, 255), (520, 230), (580, 190)]
    d = "M %.0f %.0f" % pts[0]
    for i in range(1, len(pts)):
        xm = (pts[i-1][0] + pts[i][0]) / 2
        d += " Q %.0f %.0f %.0f %.0f" % (xm, pts[i-1][1], pts[i][0], pts[i][1])
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # три зони
    els.append(line(270, oy, 270, ax_t, MUTED, 1, dash="4 4"))
    els.append(line(470, oy, 470, ax_t, MUTED, 1, dash="4 4"))
    els.append(text(200, ax_t + 20, "дифузія", size=12, color=MUTED))
    els.append(text(370, ax_t + 20, "омічний +", size=12, color=MUTED))
    els.append(text(370, ax_t + 36, "перенесення", size=12, color=MUTED))
    els.append(text(540, ax_t + 20, "індуктивність", size=12, color=MUTED))

    # точка мінімуму = ESR
    els.append(circle(400, 262, 5, fill=FIELD, stroke=INK, sw=1.5))
    b, _, _ = textbox(400, 300 - 8, "мінімум ≈ ESR", size=12, fill="#eafaf1", stroke=FIELD)
    # зсунемо підпис нижче осі — намалюємо окремо
    els.append(text(400, 335, "мінімум |Z| ≈ ESR", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'spectrum.svg'), W, H, *els,
           title="Імпеданс батареї — не число, а крива за частотою")


# ── 2. Модель Рендлса: еквівалентна схема комірки ────────────────────────────
def fig_randles():
    W, H = 720, 300
    els = []
    y = 150
    xL = 70
    # клема +
    els.append(line(xL, y, xL + 30, y, INK, 2))
    els.append(text(xL - 6, y + 5, "+", size=18, color=POS, bold=True, anchor="end"))

    # ESL (котушка) — індуктивність виводів/фольги
    x0 = xL + 30
    els.append(text(x0 + 25, y - 34, "ESL", size=12, color=MUTED))
    els.append(text(x0 + 25, y - 20, "(виводи)", size=10, color=MUTED))
    # проста «спіраль» котушки
    coil = "M %.0f %.0f" % (x0, y)
    for k in range(4):
        cx = x0 + 6 + k * 12
        coil += " q 3 -12 6 0 q 3 12 6 0" if k == 0 else " q 3 -12 6 0 q 3 12 6 0"
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (coil, INK))
    x1 = x0 + 54
    els.append(line(x0 + 54, y, x1 + 20, y, INK, 2))

    # Rs (омічний опір електроліту/контактів) — резистор
    xr = x1 + 20
    els.append('<rect x="%.0f" y="%.0f" width="46" height="18" fill="%s" stroke="%s" stroke-width="2"/>'
               % (xr, y - 9, FILL, INK))
    els.append(text(xr + 23, y - 18, "Rs", size=13, color=INK, bold=True))
    els.append(text(xr + 23, y + 34, "омічний", size=11, color=MUTED))
    xj = xr + 46 + 24      # вузол розгалуження

    els.append(line(xr + 46, y, xj, y, INK, 2))

    # паралель: зверху Cdl (подвійний шар), знизу Rct послідовно з Warburg
    top_y = y - 45
    bot_y = y + 45
    xpar1 = xj
    xpar2 = xj + 150
    # стійки
    els.append(line(xpar1, top_y, xpar1, bot_y, INK, 2))
    els.append(line(xpar2, top_y, xpar2, bot_y, INK, 2))
    els.append(line(xpar1, y, xpar1, y, INK, 2))
    # верхня вітка: Cdl (дві риски конденсатора)
    cxm = (xpar1 + xpar2) / 2
    els.append(line(xpar1, top_y, cxm - 8, top_y, INK, 2))
    els.append(line(cxm - 8, top_y - 14, cxm - 8, top_y + 14, INK, 2.5))
    els.append(line(cxm + 8, top_y - 14, cxm + 8, top_y + 14, INK, 2.5))
    els.append(line(cxm + 8, top_y, xpar2, top_y, INK, 2))
    els.append(text(cxm, top_y - 22, "Cdl — подвійний шар", size=12, color=NEG))

    # нижня вітка: Rct + Warburg
    els.append(line(xpar1, bot_y, xpar1 + 26, bot_y, INK, 2))
    els.append('<rect x="%.0f" y="%.0f" width="40" height="16" fill="%s" stroke="%s" stroke-width="2"/>'
               % (xpar1 + 26, bot_y - 8, FILL, INK))
    els.append(text(xpar1 + 46, bot_y + 26, "Rct", size=12, color=INK, bold=True))
    els.append(line(xpar1 + 66, bot_y, xpar1 + 96, bot_y, INK, 2))
    # Warburg — ромб-«W»
    wx = xpar1 + 96
    els.append('<rect x="%.0f" y="%.0f" width="30" height="16" fill="#fff6e0" stroke="%s" stroke-width="2"/>'
               % (wx, bot_y - 8, "#b8860b"))
    els.append(text(wx + 15, bot_y + 4, "W", size=12, color="#8a6d0b", bold=True))
    els.append(text(wx + 15, bot_y + 26, "дифузія", size=11, color="#8a6d0b"))
    els.append(line(wx + 30, bot_y, xpar2, bot_y, INK, 2))

    # хвіст до клеми −
    els.append(line(xpar2, y, xpar2 + 40, y, INK, 2))
    els.append(text(xpar2 + 50, y + 5, "−", size=18, color=NEG, bold=True))

    render(os.path.join(OUT, 'randles.svg'), W, H, *els,
           title="Модель Рендлса: що ховається за клемами комірки")


# ── 3. Годограф (Nyquist): відбиток імпедансу ───────────────────────────────
def fig_nyquist():
    W, H = 700, 380
    els = []
    ox, oy = 90, 300
    ax_r = 640
    ax_t = 70
    els.append(line(ox, oy, ax_r, oy, INK, 2))
    els.append(arrow(ax_r - 4, oy, ax_r + 8, oy, INK))
    els.append(line(ox, oy, ox, ax_t, INK, 2))
    els.append(arrow(ox, ax_t + 4, ox, ax_t - 8, INK))
    els.append(text(ax_r + 6, oy + 20, "Re(Z)  →", size=13, color=MUTED, anchor="end"))
    els.append(text(ox + 6, ax_t - 6, "−Im(Z)", size=13, color=MUTED, anchor="start"))

    # напівколо (перенесення заряду) від Rs до Rs+Rct
    x_rs = 180          # Re = Rs
    x_rct = 400         # Re = Rs + Rct
    cx = (x_rs + x_rct) / 2
    r = (x_rct - x_rs) / 2
    # верхнє напівколо (−Im додатне вгору)
    d = "M %.0f %.0f A %.0f %.0f 0 0 1 %.0f %.0f" % (x_rs, oy, r, r, x_rct, oy)
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # хвіст Варбурга під 45°
    tail_len = 150
    tx = x_rct + tail_len * 0.72
    ty = oy - tail_len * 0.72
    els.append(line(x_rct, oy, tx, ty, "#b8860b", 3))
    els.append(text(tx + 30, ty - 6, "45° — дифузія", size=12, color="#8a6d0b"))
    els.append(text(tx + 30, ty + 10, "(Варбург)", size=11, color="#8a6d0b"))

    # індуктивний «ниж» на високих частотах: нижче осі, зліва від Rs
    els.append(line(x_rs - 40, oy + 34, x_rs, oy, NEG, 2.5))
    els.append(circle(x_rs - 40, oy + 34, 4, fill="#eaf0fd", stroke=NEG))
    els.append(text(x_rs - 44, oy + 52, "ESL: −Im<0", size=11, color=NEG, anchor="middle"))

    # мітки перетинів осі
    els.append(line(x_rs, oy, x_rs, oy + 6, INK, 1.5))
    els.append(text(x_rs, oy + 24, "Rs", size=12, color=INK, bold=True))
    els.append(text(x_rs, oy + 40, "(омічний,", size=10, color=MUTED))
    els.append(text(x_rs, oy + 54, "≈1 кГц)", size=10, color=MUTED))
    els.append(line(x_rct, oy, x_rct, oy + 6, INK, 1.5))
    els.append(text(x_rct, oy + 24, "Rs+Rct", size=12, color=INK, bold=True))

    # діаметр = Rct
    els.append(line(x_rs, oy - r - 16, x_rct, oy - r - 16, MUTED, 1, dash="4 3"))
    els.append(text(cx, oy - r - 22, "діаметр = Rct", size=12, color=MUTED))

    # напрям частоти
    els.append(text(cx, ax_t - 4, "частота росте  ⟵", size=12, color=MUTED))
    els.append(circle(x_rs, oy, 4, fill=INK, stroke=INK))
    els.append(circle(x_rct, oy, 4, fill=INK, stroke=INK))

    render(os.path.join(OUT, 'nyquist.svg'), W, H, *els,
           title="Годограф імпедансу (Nyquist): відбиток комірки")


# ── 4. Три методи виміру: одна комірка, різні числа ─────────────────────────
def fig_methods():
    W, H = 720, 320
    els = []
    cols = [
        ("AC-IR @ 1 кГц", "мала синусоїда\n1 кГц через комірку", "Re(Z) на 1 кГц",
         "швидко, дешево;\nлише омічна точка", "≈ 36 мОм", NEG),
        ("DC-імпульс (DCIR)", "східець струму\n0.2C→1C, читаємо\nпровал напруги", "ΔV/ΔI за 1–10 с",
         "як реальний пік;\nвключає й повільне", "≈ 110 мОм", POS),
        ("EIS (спектр)", "качаємо частоту\nвід мГц до кГц", "увесь годограф",
         "розкладає на Rs,\nRct, дифузію", "крива Z(f)", "#8a6d0b"),
    ]
    bw = 210
    gap = 15
    x0 = 20
    for i, (title, how, reads, note, val, col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        els.append(rect(x, 55, bw, 235, fill=FILL, stroke=col, sw=2))
        els.append(text(x + bw/2, 80, title, size=14, color=col, bold=True))
        els.append(line(x + 14, 92, x + bw - 14, 92, col, 1))
        els.append(mtext(x + bw/2, 112, "як: " + how, size=12, color=INK))
        yy = 112 + how.count("\n") * 16 + 26
        els.append(mtext(x + bw/2, yy, "дає: " + reads, size=12, color=INK))
        yy2 = yy + 22
        els.append(mtext(x + bw/2, yy2, note, size=11, color=MUTED))
        # значення внизу
        els.append(text(x + bw/2, 268, val, size=15, color=col, bold=True))

    els.append(text(W/2, 305, "та сама комірка 18650 — методи дають РІЗНІ числа, і всі правильні",
                    size=12, color=MUTED))
    render(os.path.join(OUT, 'methods.svg'), W, H, *els,
           title="Три способи зміряти імпеданс — три різні відповіді")


# ── 5. Історія: як склалася модель (Варбург → Ершлер/Рендлс → EIS) ──────────
def fig_history():
    W, H = 760, 360
    els = []
    # горизонтальна вісь часу
    ax_y = 120
    x0, x1 = 60, 700
    els.append(line(x0, ax_y, x1, ax_y, INK, 2))
    els.append(arrow(x1 - 4, ax_y, x1 + 10, ax_y, INK))
    els.append(text(x1 + 8, ax_y - 10, "час", size=12, color=MUTED, anchor="end"))

    # чотири віхи: (x, рік, хто, що додав, колір)
    marks = [
        (150, "1899", "Е. Варбург", "дифузійний елемент\n(45°) — з рівняння\nдифузії, ще до\nтеорії кінетики", "#8a6d0b"),
        (330, "1940", "Долін · Ершлер\n· Фрумкін (СРСР)", "та сама схема\nRs · Cdl · Rct+W —\nвійна поховала\nроботу на Заході", NEG),
        (470, "1947", "Дж. Рендлс\n(Британія)", "схема під кінетику\nшвидких реакцій;\nзвідси й ім'я", POS),
        (630, "сьогодні", "EIS", "діагностика й\nсортування\nбатарей: Rs, Rct,\nдифузія окремо", FIELD),
    ]
    for x, year, who, what, col in marks:
        els.append(circle(x, ax_y, 6, fill=col, stroke=INK, sw=1.5))
        els.append(line(x, ax_y, x, ax_y - 34, MUTED, 1, dash="3 3"))
        els.append(text(x, ax_y - 40, year, size=14, color=col, bold=True))
        els.append(mtext(x, ax_y - 40 + 18, who, size=11, color=INK))
        # опис під віссю
        yb = ax_y + 26
        els.append(mtext(x, yb, what, size=10.5, color=MUTED))

    # дужка «незалежно та сама схема» під 1940 і 1947
    br_y = 300
    els.append(line(330, br_y, 470, br_y, MUTED, 1.4))
    els.append(line(330, br_y, 330, br_y - 8, MUTED, 1.4))
    els.append(line(470, br_y, 470, br_y - 8, MUTED, 1.4))
    els.append(text(400, br_y + 16, "незалежно → строго «схема Рендлса–Ершлера»",
                    size=11, color=MUTED))

    render(os.path.join(OUT, 'history.svg'), W, H, *els,
           title="Модель складалася поетапно — і не однією людиною")


if __name__ == "__main__":
    fig_spectrum()
    fig_randles()
    fig_nyquist()
    fig_methods()
    fig_history()
    print("ok")
