# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WARM = "#fdecea"   # світло-червона заливка (грів)
COOL = "#eafaf0"   # світло-зелена заливка (холодно)

def poly(points, color, sw=2.2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-linejoin="round"%s/>' % (pts, color, sw, d))


# ─────────────────────────────────────────────────────────────────────────────
# Фігура A — куди йде грів від перетворення
# ─────────────────────────────────────────────────────────────────────────────
def fig_heat():
    W, H = 920, 500
    f = []
    # ── ряд 1: класична зарядка ──
    f.append(text(30, 66, "Класична зарядка: перетворювач усередині телефона",
                  size=15, color=INK, anchor="start", bold=True))
    # телефон-обгортка
    f.append(rect(258, 80, 470, 152, fill=BG, stroke=MUTED, sw=1.4))
    f.append('<rect x="258" y="80" width="470" height="152" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="6 5"/>' % MUTED)
    f.append(text(268, 100, "Телефон", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(30, 106, 160, 66, "Адаптер\n9 В (фіксовано)", size=14, bold=True))
    f.append(arrow(190, 139, 256, 139, color=LINE, sw=2))
    f.append(text(223, 128, "кабель", size=11, color=MUTED))
    f.append(fitbox(284, 108, 180, 62, "Buck\n9 В → 4.4 В", size=14, fill=WARM, stroke=POS, bold=True))
    f.append(fitbox(300, 182, 148, 34, "грів ≈ 1.3 Вт", size=13, fill=WARM, stroke=POS, color=POS, bold=True))
    f.append(arrow(464, 139, 534, 139, color=LINE, sw=2))
    f.append(fitbox(534, 108, 172, 62, "Комірка\n4.4 В", size=14, bold=True))
    f.append(fitbox(748, 108, 150, 62, "15 Вт у батарею\nгрів у телефоні", size=12, color=POS, fill=WARM, stroke=POS, bold=True))

    # ── ряд 2: PPS + дільник ──
    f.append(text(30, 286, "PPS + дільник 2:1: важке перетворення — у бриці",
                  size=15, color=INK, anchor="start", bold=True))
    f.append('<rect x="258" y="300" width="470" height="152" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="6 5"/>' % MUTED)
    f.append(text(268, 320, "Телефон", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(30, 326, 160, 62, "Адаптер PPS\nстежить ~8.9 В", size=14, bold=True))
    f.append(fitbox(40, 400, 150, 32, "грів у бриці", size=13, fill=WARM, stroke=POS, color=POS, bold=True))
    f.append(arrow(190, 357, 256, 357, color=LINE, sw=2))
    f.append(text(223, 346, "кабель", size=11, color=MUTED))
    f.append(fitbox(284, 328, 180, 62, "Дільник 2:1\n(без котушки)", size=14, fill=COOL, stroke=FIELD, bold=True))
    f.append(fitbox(300, 402, 148, 32, "холодний ≈ 0.9 Вт", size=13, fill=COOL, stroke=FIELD, color=FIELD, bold=True))
    f.append(arrow(464, 357, 534, 357, color=LINE, sw=2))
    f.append(fitbox(534, 328, 172, 62, "Комірка\n4.4 В", size=14, bold=True))
    f.append(fitbox(748, 328, 150, 62, "60 Вт у батарею\nгрів — у бриці", size=12, color=FIELD, fill=COOL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "heat-path.svg"), W, H, *f,
           title="Куди йде грів від перетворення")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура B — PPS веде батарею кривою CC/CV
# ─────────────────────────────────────────────────────────────────────────────
def fig_track():
    W, H = 860, 470
    XL, XR, YT, YB = 92, 660, 96, 384
    Vmin, Vmax = 3.0, 4.9
    tk = 0.60

    def X(t): return XL + t * (XR - XL)
    def YV(v): return YB - (v - Vmin) / (Vmax - Vmin) * (YB - YT)
    def YI(i): return YB - i * (YB - YT) * 0.92

    def vbatt(t):
        if t <= tk:
            return 3.45 + (4.40 - 3.45) * (t / tk) ** 0.80
        return 4.40

    def vpps(t):
        if t <= tk:
            return vbatt(t) + 0.30
        return 4.42 + 0.28 * math.exp(-(t - tk) / 0.11)

    def icur(t):
        if t <= tk:
            return 1.0
        return math.exp(-(t - tk) / 0.14)

    ts = [i / 120.0 for i in range(121)]
    f = []
    # затінення CC-зони
    f.append(rect(XL, YT, X(tk) - XL, YB - YT, fill="#f4f6f8", stroke="none", sw=0))
    # осі
    f.append(line(XL, YT, XL, YB, color=INK, sw=1.6))
    f.append(line(XL, YB, XR, YB, color=INK, sw=1.6))
    # тики напруги (ліва вісь)
    for v in (3.0, 3.5, 4.0, 4.5):
        y = YV(v)
        f.append(line(XL - 5, y, XL, y, color=INK, sw=1.2))
        f.append(text(XL - 12, y + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    f.append(text(XL - 30, YT - 12, "напруга, В", size=12, color=INK, anchor="start"))
    f.append(text(XR, YB + 22, "час заряду →", size=12, color=MUTED, anchor="end"))
    # коліно
    f.append(line(X(tk), YT, X(tk), YB, color=MUTED, sw=1.3, dash="5 5"))
    # зони
    f.append(text((XL + X(tk)) / 2, 84, "CC — сталий струм", size=13, color=INK, bold=True))
    f.append(text((X(tk) + XR) / 2, 84, "CV — напруга тримається, струм спадає", size=12, color=INK, bold=True))
    f.append(text(X(tk), YB + 22, "коліно 4.4 В", size=11, color=MUTED))
    # криві
    f.append(poly([(X(t), YI(icur(t))) for t in ts], FIELD, sw=2.4))
    f.append(poly([(X(t), YV(vpps(t))) for t in ts], NEG, sw=2.4, dash="7 5"))
    f.append(poly([(X(t), YV(vbatt(t))) for t in ts], INK, sw=2.6))
    # легенда праворуч
    lx, ly = 690, 150
    def leg(y, color, s, dash=None):
        seg = ('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.6"%s/>'
               % (lx, y, lx + 40, y, color, ' stroke-dasharray="7 5"' if dash else ''))
        return seg + text(lx + 48, y + 4, s, size=12, color=INK, anchor="start")
    f.append(leg(ly, INK, "напруга комірки"))
    f.append(leg(ly + 30, NEG, "напруга PPS", dash=True))
    f.append(leg(ly + 60, FIELD, "струм заряду"))
    f.append(fitbox(680, ly + 92, 168, 92,
                    "PPS тримає напругу\nтрохи вище комірки,\nа в CV сходиться\nна 4.4 В",
                    size=12, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "cc-cv-track.svg"), W, H, *f,
           title="PPS веде батарею кривою CC/CV")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура C — дільник 2:1
# ─────────────────────────────────────────────────────────────────────────────
def fig_divider():
    W, H = 900, 340
    f = []
    f.append(fitbox(60, 96, 200, 96, "Адаптер PPS\n9 В · 5 А\n= 45 Вт", size=15, bold=True))
    f.append(arrow(260, 144, 336, 144, color=LINE, sw=2.2))
    f.append(text(298, 132, "5 А", size=12, color=MUTED))
    f.append(fitbox(336, 86, 224, 116, "Дільник 2:1\nперемикані\nконденсатори · ≈ 99 %",
                    size=15, fill=COOL, stroke=FIELD, bold=True))
    f.append(arrow(560, 144, 636, 144, color=LINE, sw=2.2))
    f.append(text(598, 132, "10 А", size=12, color=MUTED))
    f.append(fitbox(636, 96, 204, 96, "Комірка\n4.5 В · 10 А\n= 45 Вт", size=15, bold=True))
    f.append(text(450, 252,
                  "Напруга ÷ 2, струм × 2 — та сама потужність, але грів майже нульовий: без котушки, ключі на ~50 %.",
                  size=12.5, color=INK))
    f.append(text(450, 280,
                  "Крок PPS 20 мВ на вході → 10 мВ на комірці — досить тонко, щоб утримати CV-коліно.",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, "divider-2to1.svg"), W, H, *f,
           title="Дільник 2:1: половинить напругу, подвоює струм")


CELL = "#eef2ff"   # світло-синя заливка (комірка)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура D — три числа роздільності: крок, опір, дільник (ΔI = ΔU/R)
# ─────────────────────────────────────────────────────────────────────────────
def fig_resolution():
    W, H = 940, 452
    f = []
    # ── ряд 1: прямий заряд ──
    f.append(text(40, 66, "Прямий заряд: крок напруги ворушить струм через опір шляху",
                  size=15, color=INK, anchor="start", bold=True))
    yb = 108
    f.append(fitbox(40, yb, 170, 74, "PPS\nкрок ΔU = 20 мВ", size=13.5, bold=True))
    f.append(arrow(214, yb + 37, 292, yb + 37, color=LINE, sw=2))
    f.append(fitbox(292, yb, 200, 74, "R = ESR + провідники\n≈ 30 мОм", size=13.5, bold=True))
    f.append(arrow(496, yb + 37, 574, yb + 37, color=LINE, sw=2))
    f.append(fitbox(574, yb, 180, 74, "Комірка\nEMF ≈ 4.40 В", size=13.5, fill=CELL, stroke=NEG, bold=True))
    f.append(text(768, yb + 30, "ΔU повністю", size=11.5, color=MUTED, anchor="start"))
    f.append(text(768, yb + 48, "лягає на R", size=11.5, color=MUTED, anchor="start"))
    f.append(fitbox(292, yb + 94, 400, 40, "ΔI = ΔU / R = 20 мВ / 30 мОм ≈ 0.67 А",
                    size=14, fill="#fff8e1", stroke=POS, bold=True))

    # ── ряд 2: дільник ──
    y2 = 300
    f.append(text(40, y2 - 22, "Дільник 2:1: половинить крок напруги, подвоює крок струму",
                  size=15, color=INK, anchor="start", bold=True))
    f.append(fitbox(40, y2, 170, 74, "PPS\nΔU = 20 мВ", size=13.5, bold=True))
    f.append(arrow(214, y2 + 37, 292, y2 + 37, color=LINE, sw=2))
    f.append(fitbox(292, y2, 200, 74, "Дільник 2:1\n(заряд-помпа)", size=13.5, fill=COOL, stroke=FIELD, bold=True))
    f.append(arrow(496, y2 + 37, 574, y2 + 37, color=LINE, sw=2))
    f.append(fitbox(574, y2, 180, 74, "Комірка\nкрок = 10 мВ", size=13.5, fill=CELL, stroke=NEG, bold=True))
    f.append(text(470, y2 + 108,
                  "на комірці 10 мВ (÷2)     ·     I комірки = 2·I входу     ·     опір комірки з входу × 4",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "resolution-map.svg"), W, H, *f,
           title="Три числа роздільності: крок, опір, дільник")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура E — дискретний інтегратор: поведінка за петльовим підсиленням L
# ─────────────────────────────────────────────────────────────────────────────
def fig_loopgain():
    W, H = 900, 512
    XL, XR, YT, YB = 92, 700, 92, 384
    kmax = 12
    ymin, ymax = -0.28, 2.18

    def X(k): return XL + k / kmax * (XR - XL)
    def Y(v): return YB - (v - ymin) / (ymax - ymin) * (YB - YT)

    def series(L):
        ys = [0.0]
        for _ in range(kmax):
            ys.append(ys[-1] + L * (1 - ys[-1]))
        return ys

    f = []
    f.append(line(XL, YT, XL, YB, color=INK, sw=1.6))
    f.append(line(XL, Y(0), XR, Y(0), color=INK, sw=1.6))
    f.append(line(XL, Y(1), XR, Y(1), color=MUTED, sw=1.3, dash="6 5"))
    f.append(text(XR + 6, Y(1) + 4, "ціль", size=11, color=MUTED, anchor="start"))
    for v in (0, 0.5, 1, 1.5, 2):
        f.append(line(XL - 5, Y(v), XL, Y(v), color=INK, sw=1.1))
        f.append(text(XL - 11, Y(v) + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    for k in range(0, kmax + 1, 2):
        f.append(line(X(k), Y(0), X(k), Y(0) + 5, color=INK, sw=1.1))
        f.append(text(X(k), Y(0) + 20, str(k), size=11, color=MUTED))
    f.append(text(XL - 34, YT - 14, "вихід (ціль = 1)", size=12, color=INK, anchor="start"))
    f.append(text(XR, Y(0) + 38, "крок k →", size=12, color=MUTED, anchor="end"))

    curves = [(0.5, NEG, "L = 0.5 — повзе, без перельоту"),
              (1.0, FIELD, "L = 1 — точно за один крок"),
              (1.5, POS, "L = 1.5 — переліт, дзвенить"),
              (2.0, "#8e44ad", "L = 2 — сталі коливання")]
    for L, col, _ in curves:
        ys = series(L)
        pts = [(X(k), Y(min(max(ys[k], ymin), ymax))) for k in range(kmax + 1)]
        f.append(poly(pts, col, sw=2.2))
        for k in range(kmax + 1):
            yy = min(max(ys[k], ymin), ymax)
            f.append(circle(X(k), Y(yy), 2.7, fill=col, stroke=col, sw=1))

    # легенда двома стовпцями під графіком
    rows = [(120, 435), (120, 463), (486, 435), (486, 463)]
    for (L, col, lab), (lx, ly) in zip(curves, rows):
        f.append(line(lx, ly, lx + 28, ly, color=col, sw=2.8))
        f.append(text(lx + 36, ly + 4, lab, size=12.5, color=INK, anchor="start"))
    f.append(fitbox(330, 484, 240, 30, "стійко: 0 < L < 2", size=13.5,
                    fill="#eafaf0", stroke=FIELD, bold=True))
    render(os.path.join(IMG, "loop-gain.svg"), W, H, *f,
           title="Дискретний інтегратор: поведінка за петльовим підсиленням L")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура F — точність утримання CV проти шкідливого вікна
# ─────────────────────────────────────────────────────────────────────────────
def fig_cv_band():
    W, H = 920, 396
    XL, XR = 118, 806
    vmin, vmax = 4.26, 4.54

    def X(v): return XL + (v - vmin) / (vmax - vmin) * (XR - XL)

    axisY = 300
    top = 70
    f = []
    # зони: зелене безпечне вікно ±40 мВ, червоне поза ним
    f.append(rect(X(vmin), top, X(4.36) - X(vmin), axisY - top, fill="#fdecea", stroke="none", sw=0, rx=0))
    f.append(rect(X(4.44), top, X(vmax) - X(4.44), axisY - top, fill="#fdecea", stroke="none", sw=0, rx=0))
    f.append(rect(X(4.36), top, X(4.44) - X(4.36), axisY - top, fill="#eafaf0", stroke="none", sw=0, rx=0))
    # вісь
    f.append(line(XL, axisY, XR, axisY, color=INK, sw=1.6))
    for v in (4.30, 4.35, 4.40, 4.45, 4.50):
        f.append(line(X(v), axisY, X(v), axisY + 5, color=INK, sw=1.1))
        f.append(text(X(v), axisY + 20, "%.2f" % v, size=11, color=MUTED))
    f.append(text(XR, axisY + 38, "напруга комірки, В →", size=12, color=MUTED, anchor="end"))
    # ціль
    f.append(line(X(4.40), 58, X(4.40), axisY, color=INK, sw=1.4, dash="5 5"))
    f.append(text(X(4.40), 50, "ціль 4.40 В", size=12, color=INK, bold=True))
    # підписи зон
    f.append(text(X(4.40), 90, "безпечно ±40 мВ", size=11.5, color=FIELD, bold=True))
    f.append(text(X(4.305), 90, "шкідливо", size=11.5, color=POS, bold=True))
    f.append(text(X(4.495), 90, "шкідливо", size=11.5, color=POS, bold=True))

    def whisk(y, lo, hi, col, lab):
        out = line(X(lo), y, X(hi), y, color=col, sw=3.2)
        out += line(X(lo), y - 7, X(lo), y + 7, color=col, sw=2.4)
        out += line(X(hi), y - 7, X(hi), y + 7, color=col, sw=2.4)
        out += circle(X(4.40), y, 3.2, fill=col, stroke=col, sw=1)
        out += text(XL - 10, y + 4, lab, size=12, color=INK, anchor="end")
        return out

    f.append(whisk(126, 4.30, 4.50, POS, "QC 200 мВ"))
    f.append(whisk(174, 4.39, 4.41, NEG, "PPS 20 мВ"))
    f.append(whisk(220, 4.395, 4.405, FIELD, "PPS + дільник"))
    f.append(text(X(4.50) + 8, 130, "±100 мВ — далеко за межу", size=11, color=POS, anchor="start"))
    f.append(text(X(4.41) + 8, 178, "±10 мВ", size=11, color=NEG, anchor="start"))
    f.append(text(X(4.405) + 8, 224, "±5 мВ", size=11, color=FIELD, anchor="start"))
    render(os.path.join(IMG, "cv-hold-band.svg"), W, H, *f,
           title="Точність утримання CV: крок напруги проти шкідливого вікна")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура G — машина станів кола керування PPS-зарядкою
# ─────────────────────────────────────────────────────────────────────────────
def fig_loop_fsm():
    W, H = 1000, 470
    yb, bh = 140, 68

    def selfloop(cx, label):
        hw, up = 34, 38
        x1, x2, yt = cx + hw, cx - hw, yb - up
        p = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (x1, yb, x1, yt, x2, yt, x2, yb, MUTED))
        p += text(cx, yt - 8, label, size=11, color=MUTED, italic=True)
        return p

    f = []
    # ── стани ──
    f.append(fitbox(28, yb, 132, bh, "INIT\nпорт 5 В", size=13.5, bold=True))
    f.append(fitbox(196, yb, 158, bh, "NEGOTIATE\nобрати APDO", size=13.5, fill=CELL, stroke=NEG, bold=True))
    f.append(fitbox(396, yb, 150, bh, "CC\nсталий струм", size=13.5, fill=COOL, stroke=FIELD, bold=True))
    f.append(fitbox(598, yb, 150, bh, "CV\nстала напруга", size=13.5, fill=COOL, stroke=FIELD, bold=True))
    f.append(fitbox(812, yb, 150, bh, "DONE\nзавершено", size=13.5, bold=True))

    ym = yb + bh / 2
    # ── переходи вздовж ряду ──
    f.append(arrow(160, ym, 196, ym, color=LINE, sw=2))
    f.append(arrow(354, ym, 396, ym, color=LINE, sw=2))
    f.append(arrow(546, ym, 598, ym, color=LINE, sw=2))
    f.append(text(572, 126, "коліно 4.4 В", size=11.5, color=INK, bold=True))
    f.append(arrow(748, ym, 812, ym, color=LINE, sw=2))
    f.append(text(780, 126, "I ≤ поріг", size=11.5, color=INK, bold=True))

    # ── самопетлі керування ──
    f.append(selfloop(471, "щокроку: OMF + запит"))
    f.append(selfloop(673, "щокроку: OMF + запит"))

    # ── аварійна гілка ──
    fx, fy, fw, fh = 386, 346, 180, 66
    f.append(fitbox(fx, fy, fw, fh, "FAULT · порт 5 В\nрозімкнути ключ", size=13, fill=WARM, stroke=POS, bold=True))
    # входи у FAULT з CC і CV
    f.append(arrow(471, yb + bh, 458, fy, color=POS, sw=1.9))
    f.append(arrow(673, yb + bh, 566, fy + 18, color=POS, sw=1.9))
    f.append(text(600, 292, "hard reset / перегрів (PTF)", size=11.5, color=POS, anchor="start"))
    # вихід з FAULT назад у NEGOTIATE
    f.append(arrow(fx, fy + fh / 2, 275, yb + bh, color=MUTED, sw=1.9))
    f.append(text(214, 300, "завести наново", size=11.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "loop-fsm.svg"), W, H, *f,
           title="Машина станів кола PPS-зарядки")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура H — компенсація падіння в кабелі: запит = комірка + I·R
# ─────────────────────────────────────────────────────────────────────────────
def fig_cable_comp():
    W, H = 1000, 430
    XL, XR = 150, 740
    vmin, vmax = 3.8, 4.5
    axisY = 318

    def X(v): return XL + (v - vmin) / (vmax - vmin) * (XR - XL)

    f = []
    f.append(text(W / 2, 58, "запит порту = напруга комірки + I·R", size=15, color=INK, bold=True))

    # ── вертикальна лінія цілі CV ──
    f.append(line(X(4.40), 92, X(4.40), axisY, color=MUTED, sw=1.3, dash="5 5"))
    f.append(text(X(4.40), 84, "ціль CV 4.40 В", size=11.5, color=INK, bold=True))

    # ── вісь напруги ──
    f.append(line(XL, axisY, XR, axisY, color=INK, sw=1.6))
    for v in (3.8, 4.0, 4.2, 4.4):
        f.append(line(X(v), axisY, X(v), axisY + 5, color=INK, sw=1.1))
        f.append(text(X(v), axisY + 20, "%.1f" % v, size=11, color=MUTED))
    f.append(text(XR, axisY + 20, "напруга, В →", size=11.5, color=MUTED, anchor="start"))

    def bar(y, vc, vp, clab, plab, ilab):
        out = rect(X(vc), y, X(vp) - X(vc), 20, fill=WARM, stroke=POS, sw=1.6, rx=3)
        out += line(X(vc), y - 8, X(vc), y + 28, color=INK, sw=2.6)      # комірка
        out += line(X(vp), y - 8, X(vp), y + 28, color=NEG, sw=2.6)      # порт
        out += text(X(vc) - 12, y + 15, clab, size=12, color=INK, anchor="end", bold=True)
        out += text(X(vp) + 12, y + 15, plab, size=12, color=NEG, anchor="start", bold=True)
        out += text((X(vc) + X(vp)) / 2, y + 48, ilab, size=12.5, color=POS, bold=True)
        return out

    # CC: великий струм — широке падіння
    f.append(bar(150, 3.90, 4.02, "комірка 3.90 В", "порт 4.02 В", "CC:  I = 3.0 А  →  I·R = 120 мВ"))
    # CV: струм спав — падіння змаліло
    f.append(bar(250, 4.40, 4.412, "комірка 4.40 В", "порт 4.412 В", "CV:  I = 0.3 А  →  I·R = 12 мВ"))

    f.append(fitbox(240, 356, 520, 50,
                    "Струм спадає — падіння I·R тане само,\nі запит порту сходить до цілі без окремої логіки.",
                    size=13, fill=BG, stroke=MUTED))
    render(os.path.join(IMG, "cable-comp.svg"), W, H, *f,
           title="Компенсація падіння в кабелі: запит = комірка + I·R")


if __name__ == "__main__":
    fig_heat()
    fig_track()
    fig_divider()
    fig_resolution()
    fig_loopgain()
    fig_cv_band()
    fig_loop_fsm()
    fig_cable_comp()
    print("OK: figures written to", IMG)
