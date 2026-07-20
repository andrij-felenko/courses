# -*- coding: utf-8 -*-
"""Фігури до теми «USB PD EPR».
Імпортує спільний svgkit зі scripts/ (НЕ переписувати тут). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

HOT = POS      # висока напруга / грів / небезпека — червоний
COOL = NEG     # низький струм / безпека — синій
SINK = FIELD   # пристрій (приймач) — зелений
SRC = POS      # джерело — гарячий


# ── 1. Напругу, а не струм: той самий ват, різний грів ───────────────────────
def fig_volts_not_amps():
    W, H = 860, 410
    p = []
    # ── ліва панель: низька напруга, великий струм → гарячий кабель
    lx, ly, lw, lh = 45, 58, 360, 300
    p.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=HOT, sw=2))
    cxl = lx + lw / 2
    p.append(text(cxl, ly + 34, "Низька напруга", size=15, bold=True, color=HOT))
    # кабель
    cab_y = ly + 92
    p.append(rect(lx + 55, cab_y, lw - 110, 18, fill="#d9a5a0", stroke=HOT, sw=1.4))
    # хвилі гріву над кабелем
    zig = []
    x = lx + 70
    while x < lx + lw - 70:
        zig.append("%.0f,%.0f" % (x, cab_y - 10))
        zig.append("%.0f,%.0f" % (x + 12, cab_y - 26))
        x += 24
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(zig), HOT))
    p.append(text(cxl, cab_y + 55, "20 В × 12 А = 240 Вт", size=15, bold=True))
    p.append(text(cxl, cab_y + 88, "грів жили ∝ 12² = 144", size=13, color=HOT))
    p.append(text(cxl, cab_y + 122, "12 А — понад стелю роз'єму 5 А:", size=12, color=HOT))
    p.append(text(cxl, cab_y + 142, "контакти б перегрілися", size=12, color=HOT))
    # ── права панель: висока напруга, малий струм → холодний кабель
    rx = 455
    p.append(rect(rx, ly, lw, lh, fill="#eaf0fd", stroke=COOL, sw=2))
    cxr = rx + lw / 2
    p.append(text(cxr, ly + 34, "Висока напруга", size=15, bold=True, color=COOL))
    p.append(rect(rx + 55, cab_y, lw - 110, 18, fill="#a7bdf0", stroke=COOL, sw=1.4))
    p.append(text(cxr, cab_y + 55, "48 В × 5 А = 240 Вт", size=15, bold=True))
    p.append(text(cxr, cab_y + 88, "грів жили ∝ 5² = 25", size=13, color=COOL))
    p.append(text(cxr, cab_y + 122, "5 А — у межах USB-C:", size=12, color=COOL))
    p.append(text(cxr, cab_y + 142, "кабель лишається холодним", size=12, color=COOL))
    # підсумок
    b, w, h = textbox(W / 2, 390,
                      "Та сама потужність — але майже вшестеро менший грів. Тому EPR піднімає напругу, а не струм",
                      size=12.5, fill="#f4f6f8", bold=True)
    p.append(b)
    render(os.path.join(IMG, "volts-not-amps.svg"), W, H, *p,
           title="240 Вт: напругою, а не струмом")


# ── 2. Сходи потужності SPR → EPR і смуга AVS ────────────────────────────────
def fig_ladder():
    W, H = 800, 460
    p = []
    x0, y0 = 92, 300
    p.append(line(x0, y0, 748, y0, color=INK, sw=1.5))
    p.append(line(x0, y0, x0, 92, color=INK, sw=1.5))
    p.append(text(x0 - 12, 100, "В", size=12, color=MUTED, anchor="end"))
    # щаблі: (напруга, колір, підпис потужності над стовпчиком або None)
    steps = [("5", COOL, None), ("9", COOL, None), ("15", COOL, None), ("20", COOL, None),
             ("28", HOT, "140 Вт"), ("36", HOT, "180 Вт"), ("48", HOT, "240 Вт")]
    bw, step = 46, 90
    scale = 3.6
    centers = []
    for i, (v, col, pw) in enumerate(steps):
        bx = 110 + i * step
        hgt = float(v) * scale
        p.append(rect(bx, y0 - hgt, bw, hgt, fill="none", stroke=col, sw=2.2))
        p.append(text(bx + bw / 2, y0 + 20, v + " В", size=12, bold=True, color=col))
        if pw:
            p.append(text(bx + bw / 2, y0 - hgt - 9, pw, size=11, color=col, bold=True))
        centers.append(bx + bw / 2)
    # групи SPR / EPR під віссю
    p.append(text((centers[0] + centers[3]) / 2, y0 + 46, "SPR — до 100 Вт",
                  size=12.5, bold=True, color=COOL))
    p.append(text((centers[4] + centers[6]) / 2, y0 + 46, "EPR — до 240 Вт",
                  size=12.5, bold=True, color=HOT))
    # смуга AVS (15 → 48 В)
    ax0 = centers[2] - bw / 2
    ax1 = centers[6] + bw / 2
    p.append(fitbox(ax0, 368, ax1 - ax0, 34,
                    "AVS: будь-яка напруга 15–48 В, крок 100 мВ",
                    size=12.5, fill="#eaf3ea", stroke=SINK, sw=1.6, color=SINK, bold=True))
    # підсумок
    b, w, h = textbox(W / 2, 432,
                      "Усі щаблі — на 5 А. Понижчі профілі бачать лише те, що їм по силі",
                      size=12, fill="#f4f6f8")
    p.append(b)
    render(os.path.join(IMG, "ladder.svg"), W, H, *p,
           title="Фіксовані щаблі EPR і плавна смуга AVS")


# ── 3. Вхід у режим EPR: церемонія поверх SPR-контракту ──────────────────────
def fig_entry():
    W, H = 820, 520
    p = []
    sx, dx = 200, 620
    # учасники
    p.append(rect(sx - 85, 46, 170, 30, fill="#fdecea", stroke=SRC, sw=2))
    p.append(text(sx, 66, "джерело", size=13, bold=True, color=SRC))
    p.append(rect(dx - 95, 46, 190, 30, fill="#eaf3ea", stroke=SINK, sw=2))
    p.append(text(dx, 66, "пристрій (sink)", size=13, bold=True, color=SINK))
    # лінії життя
    p.append(line(sx, 76, sx, 500, color=MUTED, sw=1.4, dash="4 4"))
    p.append(line(dx, 76, dx, 500, color=MUTED, sw=1.4, dash="4 4"))
    # верхні примітки
    p.append(text(W / 2, 104, "EPR умикається лише коли готові всі троє: джерело · пристрій · кабель з e-marker",
                  size=11.5, color=MUTED, italic=True))
    p.append(text(W / 2, 130, "спершу вже діє звичайний SPR-контракт → на VBUS безпечні 5 В",
                  size=11.5, color=MUTED, italic=True))

    def msg(y, a, b, label, color):
        p.append(line(a, y, b, y, color=color, sw=2.2))
        p.append(arrow(b - 18, y, b, y, color=color))
        p.append(text((a + b) / 2, y - 9, label, size=12, color=color, bold=True))

    msg(172, dx, sx, "EPR_Mode (Enter) — прошу EPR", SINK)
    msg(214, sx, dx, "Enter Acknowledged", SRC)
    # перевірка кабелю
    p.append(text(W / 2, 254, "джерело перевіряє кабель (e-marker: 50 В / 5 А?)",
                  size=11.5, color=MUTED, italic=True))
    p.append(text(W / 2, 276, "нема EPR-кабелю → лишаємось у SPR, ≤ 100 Вт",
                  size=11, color=HOT, italic=True))
    msg(316, sx, dx, "Enter Succeeded — EPR увімкнено", SRC)
    msg(358, sx, dx, "EPR_Source_Capabilities: видно 28/36/48 В", SRC)
    msg(400, dx, sx, "Request 48 В / 5 А", SINK)
    # контракт
    b, w, h = textbox(W / 2, 456, "EPR-контракт діє:  48 В × 5 А = 240 Вт",
                      size=13, fill="#eaf3ea", stroke=SINK, sw=1.8, color=SINK, bold=True)
    p.append(b)
    render(os.path.join(IMG, "entry.svg"), W, H, *p,
           title="Вхід у режим EPR — окрема церемонія поверх контракту")


# ── 4. Keep-alive: серцебиття тримає високу напругу ──────────────────────────
def fig_keepalive():
    W, H = 820, 400
    p = []
    x0, x1, y0 = 90, 760, 300
    xs = 520                      # мить, коли серцебиття урвалося
    y48, y5 = 132, 262
    # осі
    p.append(line(x0, y0, x1, y0, color=INK, sw=1.5))
    p.append(line(x0, y0, x0, 92, color=INK, sw=1.5))
    p.append(text(x0 - 12, y48 + 5, "48 В", size=12, bold=True, color=HOT, anchor="end"))
    p.append(text(x0 - 12, y5 + 5, "5 В", size=12, bold=True, color=COOL, anchor="end"))
    # крива напруги: тримається 48 → падіння → 5
    p.append(line(x0, y48, xs, y48, color=HOT, sw=3.2))
    p.append(line(xs, y48, xs, y5, color=INK, sw=2.2))
    p.append(line(xs, y5, x1, y5, color=COOL, sw=3.2))
    # позначка «серцебиття урвалося»
    p.append(line(xs, 104, xs, y0 + 44, color=MUTED, sw=1.3, dash="5 3"))
    p.append(text(xs, 100, "серцебиття урвалося", size=11.5, color=MUTED, italic=True))
    # лейн keep-alive: імпульси до xs, тиша після
    lane = 344
    p.append(line(x0, lane, x1, lane, color="#cfd4da", sw=1.2))
    x = x0 + 24
    while x < xs - 12:
        p.append(rect(x, lane - 20, 5, 20, fill=SINK, stroke=SINK, sw=1, rx=1))
        x += 48
    p.append(text((x0 + xs) / 2, lane + 22, "EPR_KeepAlive кожні ~0.5 с", size=11.5, color=SINK, bold=True))
    p.append(text((xs + x1) / 2, lane - 6, "— тиша —", size=11.5, color=MUTED, italic=True))
    # пояснення над кривою
    p.append(text((x0 + xs) / 2, 122, "поки серцебиття йде — 48 В тримаються", size=11.5, color=HOT))
    p.append(text((xs + x1) / 2, y5 - 14, "зникло → джерело само скидає до 5 В", size=11.5, color=COOL))
    render(os.path.join(IMG, "keepalive.svg"), W, H, *p,
           title="Keep-alive: висока напруга живе лише під активним наглядом")


# ── 5. Грів кабелю як 1/U² за фіксованої потужності (математика) ──────────────
def fig_heat_curve():
    W, H = 780, 470
    p = []
    xL, xR, yT, yB = 84, 720, 96, 382
    Vmin, Vmax, Hmax = 18.0, 50.0, 9.0
    R = 0.05
    Pdel = 240.0

    def px(v):
        return xL + (v - Vmin) / (Vmax - Vmin) * (xR - xL)

    def py(h):
        return yB - h / Hmax * (yB - yT)

    # осі
    p.append(line(xL, yB, xR + 6, yB, color=INK, sw=1.5))
    p.append(line(xL, yB, xL, yT - 6, color=INK, sw=1.5))
    p.append(text(xL - 52, (yT + yB) / 2, "грів", size=12, color=MUTED, anchor="middle"))
    p.append(text(xL - 52, (yT + yB) / 2 + 17, "жили, Вт", size=12, color=MUTED, anchor="middle"))
    p.append(text((xL + xR) / 2, yB + 54, "напруга шини за тих самих 240 Вт, В", size=12.5, color=MUTED))
    # поділки Y
    for hv in (0, 2, 4, 6, 8):
        yy = py(hv)
        p.append(line(xL - 5, yy, xL, yy, color=MUTED, sw=1.2))
        p.append(text(xL - 12, yy + 4, str(hv), size=11, color=MUTED, anchor="end"))
    # крива втрат (240/V)²·R
    pts = []
    v = Vmin
    while v <= Vmax + 0.01:
        pts.append("%.1f,%.1f" % (px(v), py((Pdel / v) ** 2 * R)))
        v += 0.5
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), INK))
    # межа роз'єму 5 А = єдина напруга, де 240 Вт влазять (48 В)
    x48 = px(48)
    p.append(line(x48, py(1.25), x48, yB, color=COOL, sw=1.4, dash="5 3"))
    p.append(circle(x48, py(1.25), 5.5, fill=COOL, stroke=COOL, sw=1))
    b, w, h = textbox(x48, py(1.25) - 42, "48 В × 5 А:  1.25 Вт",
                      size=12, fill="#eaf0fd", stroke=COOL, sw=1.5, color=COOL, bold=True)
    p.append(b)
    # точка 20 В × 12 А (гіпотетична — струм понад стелю)
    x20 = px(20)
    p.append(circle(x20, py(7.2), 5.5, fill=HOT, stroke=HOT, sw=1))
    b, w, h = textbox(x20 + 96, py(7.2) - 4, "20 В × 12 А:  7.2 Вт",
                      size=12, fill="#fdecea", stroke=HOT, sw=1.5, color=HOT, bold=True)
    p.append(b)
    # поділки X
    for vv, lab in ((20, "20"), (28, "28"), (36, "36"), (48, "48")):
        xx = px(vv)
        p.append(line(xx, yB, xx, yB + 5, color=MUTED, sw=1.2))
        p.append(text(xx, yB + 22, lab, size=11, color=MUTED))
    # підпис ліворуч від 48: нижча напруга → струм > 5 А, роз'єм не дасть
    b, w, h = textbox((xL + x48) / 2 - 4, yB - 20,
                      "ліворуч від 48 В той самий ват\nвимагає струму > 5 А — роз'єм не дасть",
                      size=10.5, fill="#fbfbfc", stroke="#d9dde2", sw=1, color=MUTED)
    p.append(b)
    render(os.path.join(IMG, "heat-curve.svg"), W, H, *p,
           title="Грів жили падає як 1/U²: удвічі вища напруга — вчетверо менше тепла")


# ── 6. Струмова обвідка AVS: I = min(5 А, PDP/U) ─────────────────────────────
def fig_avs_envelope():
    W, H = 780, 470
    p = []
    xL, xR, yT, yB = 84, 720, 96, 384
    Vmin, Vmax, Imax = 15.0, 48.0, 6.0

    def px(v):
        return xL + (v - Vmin) / (Vmax - Vmin) * (xR - xL)

    def py(i):
        return yB - i / Imax * (yB - yT)

    # осі
    p.append(line(xL, yB, xR + 6, yB, color=INK, sw=1.5))
    p.append(line(xL, yB, xL, yT - 6, color=INK, sw=1.5))
    p.append(text(xL - 50, (yT + yB) / 2, "струм", size=12, color=MUTED, anchor="middle"))
    p.append(text(xL - 50, (yT + yB) / 2 + 17, "A", size=12, color=MUTED, anchor="middle"))
    p.append(text((xL + xR) / 2, yB + 54, "обрана напруга AVS, В", size=12.5, color=MUTED))
    for iv in range(0, 7):
        yy = py(iv)
        p.append(line(xL - 5, yy, xL, yy, color=MUTED, sw=1.2))
        p.append(text(xL - 12, yy + 4, str(iv), size=11, color=MUTED, anchor="end"))
    for vv in (15, 20, 28, 36, 48):
        xx = px(vv)
        p.append(line(xx, yB, xx, yB + 5, color=MUTED, sw=1.2))
        p.append(text(xx, yB + 22, str(vv), size=11, color=MUTED))
    # стеля роз'єму 5 А
    p.append(line(xL, py(5), xR, py(5), color=MUTED, sw=1.2, dash="6 4"))
    p.append(text(xR - 6, py(5) - 8, "стеля роз'єму 5 А", size=11, color=MUTED, anchor="end", italic=True))
    # 240 Вт: рівні 5 А по всій смузі (PDP/U ≥ 5 скрізь до 48 В)
    p.append(line(px(15), py(5), px(48), py(5), color=COOL, sw=3.2))
    p.append(circle(px(48), py(5), 5.5, fill=COOL, stroke=COOL, sw=1))
    b, w, h = textbox(px(24), py(5) - 30, "джерело 240 Вт:  5 А від 15 до 48 В",
                      size=12, fill="#eaf0fd", stroke=COOL, sw=1.5, color=COOL, bold=True)
    p.append(b)
    # 180 Вт: 5 А до 36 В, далі гіпербола 180/U → 3.75 А на 48 В
    Vb = 36.0
    seg = [(px(15), py(5)), (px(Vb), py(5))]
    v = Vb
    while v <= Vmax + 0.01:
        seg.append((px(v), py(180.0 / v)))
        v += 0.5
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join("%.1f,%.1f" % (a, b2) for a, b2 in seg), HOT))
    p.append(circle(px(48), py(3.75), 5.5, fill=HOT, stroke=HOT, sw=1))
    # точка зламу V_b = PDP/5 = 36 В
    p.append(line(px(Vb), py(5), px(Vb), yB, color=HOT, sw=1.1, dash="4 3"))
    p.append(text(px(Vb), yB + 40, "злам U_b = PDP/5 = 36 В", size=10.5, color=HOT))
    b, w, h = textbox(px(43) + 8, py(3.75) + 30, "джерело 180 Вт:\nвище 36 В струм = 180/U",
                      size=11, fill="#fdecea", stroke=HOT, sw=1.5, color=HOT, bold=True)
    p.append(b)
    b, w, h = textbox(px(46), py(3.75) - 26, "3.75 А", size=11,
                      fill="#fdecea", stroke=HOT, sw=1.3, color=HOT, bold=True)
    p.append(b)
    # формула
    b, w, h = textbox((xL + xR) / 2, yT + 6, "I(U) = min(5 А,  PDP / U)",
                      size=13, fill="#f4f6f8", bold=True)
    p.append(b)
    render(os.path.join(IMG, "avs-envelope.svg"), W, H, *p,
           title="Струм AVS не задають — він падає з обвідки min(5 А, PDP/U)")


# ── 7. Стек запасу: 48 В під стелею 60 В дотикової безпеки ────────────────────
def fig_margin_stack():
    W, H = 660, 480
    p = []
    yB, Vtop = 432, 70.0
    ax_top = 74

    def py(v):
        return yB - v / Vtop * (yB - ax_top)

    # вісь V
    p.append(line(96, yB, 96, ax_top - 4, color=INK, sw=1.5))
    for vv in (0, 20, 40, 48, 60):
        yy = py(vv)
        p.append(line(91, yy, 96, yy, color=MUTED, sw=1.2))
        p.append(text(86, yy + 4, str(vv), size=11, color=MUTED, anchor="end"))
    p.append(text(58, (ax_top + yB) / 2, "В", size=12, color=MUTED))
    # стеля 60 В
    p.append(line(96, py(60), 600, py(60), color=SINK, sw=2, dash="7 4"))
    b, w, h = textbox(430, py(60) - 18, "60 В — стеля дотикової безпеки (ES1 / SELV)",
                      size=11.5, fill="#eaf3ea", stroke=SINK, sw=1.5, color=SINK, bold=True)
    p.append(b)

    # ── стовп 1: реальний бюджет 48 В ──
    x1, cw = 150, 96

    def seg(x, v0, v1, fill, stroke):
        p.append(rect(x, py(v1), cw, py(v0) - py(v1), fill=fill, stroke=stroke, sw=1.3, rx=2))

    seg(x1, 0, 48, "#dbe6fb", COOL)        # номінал
    seg(x1, 48, 50.4, "#ffe9c7", "#d9a441")  # +5 %
    seg(x1, 50.4, 50.9, "#ffd8b0", "#e07b39")  # +0.5 В викид
    seg(x1, 50.9, 58.7, "#fbd3ce", HOT)      # запас на перехідний
    p.append(text(x1 + cw / 2, py(24), "48 В", size=15, bold=True, color=COOL))
    p.append(text(x1 + cw / 2, py(24) + 18, "номінал", size=11, color=COOL))
    # виноски значень праворуч
    for v, lab, col in ((50.9, "50.9 В — очікуваний max (×1.05 +0.5)", "#c0651a"),
                        (58.7, "58.7 В — найгірший перехідний пік", HOT)):
        yy = py(v)
        p.append(line(x1 + cw, yy, x1 + cw + 14, yy, color=col, sw=1.1))
        p.append(text(x1 + cw + 18, yy + 4, lab, size=10.5, color=col, anchor="start"))
    # запас 1.3 В
    p.append(text(x1 + cw / 2, py(59.4), "запас", size=9.5, color=MUTED))
    p.append(text(x1 + cw / 2, py(59.4) + 12, "1.3 В", size=9.5, color=MUTED, bold=True))

    # ── стовп 2: якби 56 В — пік вилазить за 60 ──
    x2 = 430
    seg(x2, 0, 56, "#e6e0e0", MUTED)
    # перехідний пік ≈ 56·1.22 ≈ 68 В — обрізаємо на верху осі, стрілка вгору
    p.append(rect(x2, py(Vtop), cw, py(56) - py(Vtop), fill="#f6cfca", stroke=HOT, sw=1.3, rx=2))
    p.append(arrow(x2 + cw / 2, py(Vtop) + 6, x2 + cw / 2, ax_top - 2, color=HOT))
    p.append(text(x2 + cw / 2, py(28), "56 В?", size=15, bold=True, color=MUTED))
    p.append(text(x2 + cw / 2, py(64), "пік ≈ 68 В", size=11, color=HOT, bold=True))
    b, w, h = textbox(x2 + cw / 2, py(60) + 26, "за стелею —\nнебезпечно",
                      size=10.5, fill="#fdecea", stroke=HOT, sw=1.3, color=HOT, bold=True)
    p.append(b)

    render(os.path.join(IMG, "margin-stack.svg"), W, H, *p,
           title="48 В — найвищий номінал, чий найгірший пік ще влазить під 60 В")


# ── 8. Хроніка: дев'ять років стелі 100 Вт і стрибок до 240 (для hist) ───────
def fig_timeline():
    W, H = 860, 560
    p = []
    sx = 250                      # хребет часу
    top, bot = 96, 490
    p.append(line(sx, top, sx, bot, color=MUTED, sw=2))
    # легенда
    p.append(circle(300, 60, 7, fill="#fdecea", stroke=HOT, sw=2))
    p.append(text(314, 65, "віха стандарту USB PD", size=12, color=HOT, anchor="start", bold=True))
    p.append(circle(560, 60, 7, fill="#eaf0fd", stroke=COOL, sw=2))
    p.append(text(574, 65, "крок регулятора ЄС", size=12, color=COOL, anchor="start", bold=True))
    # (дата, рядки опису, вид, наголос)
    events = [
        ("лип. 2012",     ["PD 1.0 — стеля 100 Вт", "20 В × 5 А; вище не піднімались 9 років"], "pd", False),
        ("2017",          ["PD 3.0 — плавний режим PPS", "стеля та сама: 100 Вт"], "pd", False),
        ("26 трав. 2021", ["PD 3.1 — EPR: стеля стрибає до 240 Вт", "48 В × 5 А; нові щаблі 28 / 36 / 48 В"], "pd", True),
        ("23 лист. 2022", ["ЄС ухвалює Директиву 2022/2380", "єдиний зарядний роз'єм — USB-C"], "eu", False),
        ("28 груд. 2024", ["Телефони, планшети, камери →", "обов'язковий USB-C"], "eu", False),
        ("28 квіт. 2026", ["Ноутбуки → обов'язковий USB-C + USB PD", "потужним потрібен саме EPR"], "eu", False),
    ]
    n = len(events)
    y0, y1 = 128, 470
    stepy = (y1 - y0) / (n - 1)
    for i, (date, lines, kind, hot) in enumerate(events):
        cy = y0 + i * stepy
        col = HOT if kind == "pd" else COOL
        fillc = "#fdecea" if kind == "pd" else "#eaf0fd"
        p.append(text(sx - 26, cy - 4, date, size=13, color=col, anchor="end", bold=True))
        r = 9 if hot else 7
        p.append(circle(sx, cy, r, fill=fillc, stroke=col, sw=2.4 if hot else 2))
        p.append(line(sx + r, cy, sx + 24, cy, color=col, sw=2))
        bx, bw, bh = sx + 24, 556, 54
        p.append(fitbox(bx, cy - bh / 2, bw, bh, "\n".join(lines),
                        size=13.5 if hot else 12.5, fill=fillc if hot else FILL,
                        stroke=col, sw=2.4 if hot else 1.5, color=INK, bold=hot))
    render(os.path.join(IMG, "timeline.svg"), W, H, *p,
           title="Дев'ять років стелі 100 Вт — і стрибок до 240")


# ── 9. Кут, у який загнали 240 Вт: добуток двох стель (для hist) ─────────────
def fig_design_corner():
    W, H = 760, 566
    p = []
    ox, oy = 96, 476              # початок координат
    ax1, ay1 = 668, 88            # дальні кінці осей
    Imax, Umax = 6.0, 64.0
    sxA = (ax1 - ox) / Imax       # px на ампер
    syV = (oy - ay1) / Umax       # px на вольт
    def X(i): return ox + i * sxA
    def Y(u): return oy - u * syV
    # заборонені смуги (під усім): струм > 5 А і напруга > 60 В
    p.append(rect(X(5), ay1, ax1 - X(5), oy - ay1, fill="#fdecea", stroke="none", sw=0, rx=0))
    p.append(rect(ox, ay1, ax1 - ox, Y(60) - ay1, fill="#fdecea", stroke="none", sw=0, rx=0))
    # смуга запасу 48–60 В у дозволеному струмі
    p.append(rect(ox, Y(60), X(5) - ox, Y(48) - Y(60), fill="#eaf0fd", stroke="none", sw=0, rx=0))
    # осі
    p.append(line(ox, oy, ax1, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, ay1, color=INK, sw=1.6))
    p.append(text(ax1, oy + 30, "струм I, А →", size=12.5, color=INK, anchor="end", bold=True))
    p.append(text(ox + 26, ay1 - 14, "↑ напруга U, В", size=12.5, color=INK, anchor="start", bold=True))
    for i in range(1, 7):
        p.append(line(X(i), oy, X(i), oy + 5, color=INK, sw=1.2))
        p.append(text(X(i), oy + 20, str(i), size=11, color=MUTED))
    for u in (20, 48, 60):
        p.append(line(ox - 5, Y(u), ox, Y(u), color=INK, sw=1.2))
        p.append(text(ox - 10, Y(u) + 4, str(u), size=11, color=MUTED, anchor="end"))
    # стіни: 5 А (роз'єм) і 60 В (безпека) — червоні пунктири; 48 В (робоча) — синя
    p.append(line(X(5), oy, X(5), ay1, color=HOT, sw=2.2, dash="6 4"))
    p.append(line(ox, Y(60), ax1, Y(60), color=HOT, sw=2.2, dash="6 4"))
    p.append(line(ox, Y(48), X(5), Y(48), color=COOL, sw=2))
    # гіпербола P = 240 Вт (повна — сіра пунктирна)
    full = []
    i = 4.0
    while i <= 6.001:
        full.append("%.1f,%.1f" % (X(i), Y(240.0 / i)))
        i += 0.1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="3 3"/>'
             % (" ".join(full), MUTED))
    # досяжна дуга (4→5 А, у межах обох стін) — зелена суцільна
    arc = []
    i = 4.0
    while i <= 5.001:
        arc.append("%.1f,%.1f" % (X(i), Y(240.0 / i)))
        i += 0.1
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(arc), FIELD))
    p.append(text(X(4.55), Y(240 / 4.55) - 10, "P = 240 Вт", size=11, color=FIELD, bold=True))
    # точки: стара стеля SPR і робоча точка EPR
    p.append(circle(X(5), Y(20), 6, fill="#eaf0fd", stroke=COOL, sw=2))
    p.append(text(X(5) - 14, Y(20) + 4, "SPR · 100 Вт", size=11.5, color=COOL, anchor="end", bold=True))
    p.append(circle(X(5), Y(48), 8, fill=FIELD, stroke=INK, sw=2))
    p.append(text(X(5) - 14, Y(48) + 26, "240 Вт", size=14, color=INK, anchor="end", bold=True))
    # підписи стін
    p.append(text(X(5) + 8, ay1 + 44, "5 А — теплова", size=11.5, color=HOT, anchor="start", bold=True))
    p.append(text(X(5) + 8, ay1 + 60, "стеля роз'єму", size=11.5, color=HOT, anchor="start", bold=True))
    p.append(text(ox + 8, Y(60) - 8, "60 В — межа дотикової безпеки (ELV)", size=11.5, color=HOT, anchor="start", bold=True))
    p.append(text(ox + 8, Y(48) - 8, "48 В — робоча стеля (із запасом)", size=11.5, color=COOL, anchor="start", bold=True))
    p.append(text((ox + X(5)) / 2, (Y(60) + Y(48)) / 2 + 4, "запас на допуски й стрибки", size=10.5, color=MUTED, italic=True))
    # підсумок
    b, w, h = textbox(W / 2, 536, "240 = 48 × 5: добуток двох незалежних стель, а не обране число",
                      size=12.5, fill="#f4f6f8", bold=True)
    p.append(b)
    render(os.path.join(IMG, "design-corner.svg"), W, H, *p,
           title="Кут, у який загнали 240 Вт: 5 А × 48 В")


# ── 10. Машина станів прошивки EPR-приймача (для proj-epr-sink) ───────────────
def fig_sink_fsm():
    W, H = 780, 650
    p = []
    cx = 230
    bw, bh = 340, 56

    def state(cy, title, sub, color, fill):
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fill, stroke=color, sw=2.2))
        p.append(text(cx, cy - 6, title, size=14, bold=True, color=color))
        p.append(text(cx, cy + 15, sub, size=11.5, color=INK))

    # чотири стани вертикальним хребтом
    s1, s2, s3, s4 = 86, 214, 342, 486
    state(s1, "SPR-контракт", "5 В на VBUS — безпечний старт", COOL, "#eaf0fd")
    state(s2, "ВХІД У EPR", "EPR_Mode(Enter) → чекаю Enter Succeeded", INK, FILL)
    state(s3, "ЗАПИТ НАПРУГИ", "Request 48 В / AVS → чекаю PS_RDY", INK, FILL)
    state(s4, "EPR ACTIVE", "48 В · ключ замкнено · серцебиття живе", HOT, "#fdecea")

    # переходи по хребту + вартові умови праворуч
    def down(y_from, y_to, guard, gy):
        p.append(arrow(cx, y_from, cx, y_to, color=INK, sw=2))
        p.append(text(cx + 16, gy, guard, size=11.5, color=MUTED, anchor="start", italic=True))

    down(s1 + bh / 2, s2 - bh / 2 - 2, "SPR-контракт уже діє", (s1 + s2) / 2 + 4)
    down(s2 + bh / 2, s3 - bh / 2 - 2, "Enter Succeeded (≤ ~450 мс)", (s2 + s3) / 2 + 4)
    down(s3 + bh / 2, s4 - bh / 2 - 2, "PS_RDY → gate_enable()", (s3 + s4) / 2 + 4)

    # самопетля keep-alive на правому боці EPR ACTIVE
    rxe = cx + bw / 2
    p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (rxe, s4 - 16, rxe + 84, s4 - 30, rxe + 84, s4 + 30, rxe, s4 + 16, HOT))
    lx = rxe + 96
    p.append(text(lx, s4 - 14, "таймер 250 мс:", size=11.5, color=HOT, anchor="start", bold=True))
    p.append(text(lx, s4 + 4, "KeepAlive → ACK", size=11.5, color=HOT, anchor="start"))
    p.append(text(lx, s4 + 22, "misses = 0", size=11.5, color=HOT, anchor="start"))

    # аварійна гілка: прогаяли серцебиття → безпечні 5 В
    fb = 600
    fx = cx - 66
    p.append(line(fx, s4 + bh / 2, fx, fb - 26 - 2, color=HOT, sw=2, dash="6 4"))
    p.append(arrow(fx, fb - 26 - 9, fx, fb - 26 - 2, color=HOT, sw=2))
    my = (s4 + bh / 2 + fb - 26) / 2
    p.append(text(fx + 12, my, "keep-alive прогаяно →", size=11.5, color=HOT, anchor="start", italic=True))
    p.append(text(fx + 12, my + 18, "джерело скидає напругу", size=11.5, color=HOT, anchor="start", italic=True))
    # безпечний стан-приймач
    p.append(rect(cx - 190, fb - 26, 380, 52, fill="#eaf0fd", stroke=COOL, sw=2.2))
    p.append(text(cx, fb - 6, "FALLBACK → 5 В", size=14, bold=True, color=COOL))
    p.append(text(cx, fb + 15, "gate_disable() · знову SPR-контракт", size=11.5, color=INK))
    p.append(text(cx, fb + 44, "з 5 В усе починається спочатку", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "sink-fsm.svg"), W, H, *p,
           title="Машина станів прошивки EPR-приймача")


if __name__ == "__main__":
    fig_volts_not_amps()
    fig_ladder()
    fig_entry()
    fig_keepalive()
    fig_heat_curve()
    fig_avs_envelope()
    fig_margin_stack()
    fig_timeline()
    fig_design_corner()
    fig_sink_fsm()
    print("done")
