# -*- coding: utf-8 -*-
"""Фігури до теми «Акустичне оформлення динаміка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Акустичне коротке замикання ───────────────────────────────────────────
def fig_short_circuit():
    W, H = 760, 380
    f = [text(W / 2, 28, "Акустичне коротке замикання голого динаміка", size=17, bold=True)]

    cx, cy = 300, 200

    # магніт + котушка (спрощено) ліворуч від конуса
    f.append(rect(cx - 78, cy - 26, 26, 52, fill="#dfe6ee", stroke=LINE, sw=2))
    f.append(text(cx - 65, cy + 4, "магніт", size=9, color=MUTED))
    # конус (два розхідні відрізки — трапеція збоку)
    f.append(line(cx - 40, cy - 6, cx + 8, cy - 60, color=INK, sw=3))
    f.append(line(cx - 40, cy + 6, cx + 8, cy + 60, color=INK, sw=3))
    f.append(line(cx + 8, cy - 60, cx + 8, cy + 60, color=INK, sw=2, dash="4 4"))
    f.append(text(cx - 20, cy + 82, "конус рухається →", size=10, color=MUTED))

    # СПЕРЕДУ: стиск (гребінь) — червоні дуги праворуч
    for k in range(3):
        r = 34 + k * 26
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (cx + 8, cy - r, r, r, cx + 8, cy + r, POS))
    f.append(text(cx + 120, cy - 96, "спереду: СТИСК (+)", size=12, bold=True, color=POS))

    # ЗЗАДУ: розрідження (западина) — сині дуги ліворуч
    for k in range(3):
        r = 34 + k * 26
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (cx - 52, cy - r, r, r, cx - 52, cy + r, NEG))
    f.append(text(cx - 150, cy - 96, "ззаду: РОЗРІДЖЕННЯ (−)", size=12, bold=True, color=NEG))

    # хвилі обтікають край і зустрічаються — стрілки що загинаються до обідка
    f.append(arrow(cx + 30, cy - 60, cx - 6, cy - 92, color=POS, sw=2))
    f.append(arrow(cx - 40, cy - 60, cx - 6, cy - 92, color=NEG, sw=2))
    b, _, _ = textbox(cx - 6, cy - 118, "+ і − зустрічаються\nна краї → гасяться",
                      size=11, fill=FILL, stroke=INK)
    f.append(b)

    # нижній підсумок — чому б'є по басу
    b2, _, _ = textbox(W / 2, cy + 140,
                       "довга басова хвиля: обхід краю — мізерна частка довжини,\n"
                       "фаза не встигає змінитись → бас гасне найсильніше",
                       size=12, fill="#fdecea", stroke=POS, bold=True)
    f.append(b2)

    render(os.path.join(IMG, 'short-circuit.svg'), W, H, *f)


# ── 2. Фазоінвертор = резонатор Гельмгольца ─────────────────────────────────
def fig_bass_reflex():
    W, H = 780, 470
    f = [text(W / 2, 26, "Фазоінвертор — це резонатор Гельмгольца", size=17, bold=True)]

    # коробка
    bx, by, bw, bh = 70, 80, 300, 250
    f.append(rect(bx, by, bw, bh, fill="#f0f4f8", stroke=LINE, sw=2.5, rx=6))

    # динамік на верхній частині передньої стінки (праворуч)
    dcx, dcy = bx + bw, by + 66
    f.append(line(dcx - 34, dcy - 40, dcx, dcy - 20, color=INK, sw=3))
    f.append(line(dcx - 34, dcy + 40, dcx, dcy + 20, color=INK, sw=3))
    f.append(line(dcx, dcy - 20, dcx, dcy + 20, color=INK, sw=2))
    f.append(text(dcx - 62, dcy - 50, "конус", size=10, color=INK))
    # передня хвиля назовні (у фазі, червона)
    f.append(arrow(dcx + 6, dcy, dcx + 62, dcy, color=POS, sw=2.4))
    f.append(text(dcx + 8, dcy - 30, "передня хвиля", size=10, color=POS, anchor="start"))

    # порт на нижній частині передньої стінки
    pcx, pcy = bx + bw, by + bh - 52
    f.append(rect(pcx - 6, pcy - 20, 40, 40, fill=BG, stroke=NEG, sw=2.5))
    # пробка повітря = маса
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="8" ry="15" fill="#dbe6ff" '
             'stroke="%s" stroke-width="2"/>' % (pcx + 14, pcy, NEG))
    f.append(arrow(pcx + 36, pcy, pcx + 90, pcy, color=NEG, sw=2.4))
    f.append(text(pcx + 8, pcy + 40, "з порту — у фазі!", size=10, bold=True,
                  color=NEG, anchor="start"))

    # тильна хвиля всередину коробки
    f.append(arrow(dcx - 40, dcy + 10, bx + 96, by + 128, color=MUTED, sw=1.8))
    f.append(text(bx + 84, by + 96, "тильна хвиля", size=10, color=MUTED))

    # позначки маса/пружина
    b, _, _ = textbox(bx + 96, by + 168, "об'єм повітря\n= ПРУЖИНА", size=11,
                      fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)
    b, _, _ = textbox(pcx + 14, by + bh + 52, "порт: повітря\n= МАСА", size=11,
                      fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b)

    # права колонка — суть (розведені по вертикалі, не чіпають заголовок)
    tx = 655
    b, _, _ = textbox(tx, 118,
                      "біля власної частоти\nрезонатор перевертає\nфазу на пів оберту",
                      size=11, fill=FILL, stroke=INK)
    f.append(b)
    b, _, _ = textbox(tx, 232,
                      "тильна хвиля з порту\nвиходить У ФАЗІ\n→ бас підсилюється",
                      size=11, fill="#fdecea", stroke=POS, bold=True)
    f.append(b)
    b, _, _ = textbox(tx, 340,
                      "нижче настройки\nфаза «падає» →\nобрив підсилення",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, 'bass-reflex.svg'), W, H, *f)


# ── 3. Що всередині коробки ──────────────────────────────────────────────────
def fig_inside_box():
    W, H = 760, 400
    f = [text(W / 2, 28, "Клопоти замкненого повітря — і як їх гасять", size=17, bold=True)]

    bx, by, bw, bh = 190, 70, 340, 260
    f.append(rect(bx, by, bw, bh, fill="#f0f4f8", stroke=LINE, sw=2.5, rx=6))

    # динамік спереду
    dcx, dcy = bx + bw, by + bh / 2
    f.append(line(dcx - 34, dcy - 40, dcx, dcy - 20, color=INK, sw=3))
    f.append(line(dcx - 34, dcy + 40, dcx, dcy + 20, color=INK, sw=3))
    f.append(line(dcx, dcy - 20, dcx, dcy + 20, color=INK, sw=2))

    # стояча хвиля між лівою і правою стінкою (синусоїда всередині)
    y0 = by + 55
    d = "M %.1f %.1f" % (bx + 12, y0)
    import math
    for i in range(1, 61):
        xx = bx + 12 + i * (bw - 60) / 60.0
        yy = y0 + 16 * math.sin(i / 60.0 * 2 * math.pi * 1.5)
        d += " L %.1f %.1f" % (xx, yy)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, POS))
    f.append(text(bx + bw / 2 - 20, y0 - 26, "стояча хвиля між стінками", size=10, color=POS))

    # поглинач (вата) — точковий шум у нижній частині
    import random
    random.seed(3)
    dots = []
    for _ in range(70):
        rx = bx + 16 + random.random() * (bw - 90)
        ry = by + bh - 70 + random.random() * 55
        dots.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s" opacity="0.5"/>'
                    % (rx, ry, FIELD))
    f.append("".join(dots))
    b, _, _ = textbox(bx + 95, by + bh - 30, "поглинач (вата):\nгасить хвилі тертям",
                      size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # розпірка (bracing) — брусок поперек
    f.append(rect(bx + bw / 2 - 8, by + 20, 16, bh - 40, fill="#e6d8b8",
                  stroke="#a8842c", sw=1.5, rx=2))
    f.append(text(bx + bw / 2, by - 4, "розпірка", size=10, color="#8a6d1e"))

    # гудіння стінки — хвилька біля лівої стінки назовні
    f.append('<path d="M %.1f %.1f q -12 -14 0 -28 q 12 -14 0 -28" '
             'fill="none" stroke="%s" stroke-width="2"/>' % (bx, by + 150, MUTED))
    f.append(arrow(bx - 6, by + 122, bx - 30, by + 122, color=MUTED, sw=1.8))
    b, _, _ = textbox(bx - 92, by + 122, "тонка стінка\nгуде сама", size=10,
                      fill=FILL, stroke=MUTED)
    f.append(b)

    # підсумок унизу
    b2, _, _ = textbox(W / 2, by + bh + 50,
                       "мета: звучить лише конус — усе інше (стінки, стоячі хвилі) мовчить",
                       size=12, fill=FILL, stroke=INK, bold=True)
    f.append(b2)

    render(os.path.join(IMG, 'inside-box.svg'), W, H, *f)


# ── 4. Дві пружини складаються (вставка math) ───────────────────────────────
def fig_two_springs():
    W, H = 760, 340
    f = [text(W / 2, 28, "Дві пружини паралельно: жорсткості додаються", size=17, bold=True)]

    import math as _m

    def coil(x0, y0, x1, turns, amp, color, sw=2):
        # горизонтальна пружинка від (x0,y0) до (x1,y0)
        n = turns * 12
        d = "M %.1f %.1f" % (x0, y0)
        for i in range(1, n + 1):
            xx = x0 + (x1 - x0) * i / n
            yy = y0 + amp * _m.sin(i / n * 2 * _m.pi * turns)
            d += " L %.1f %.1f" % (xx, yy)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    # ЛІВОРУЧ: тільки підвіс
    wallx = 90
    f.append(line(wallx, 90, wallx, 210, color=INK, sw=3))
    f.append(text(wallx - 6, 78, "стінка", size=9, color=MUTED, anchor="end"))
    f.append(coil(wallx, 150, wallx + 120, 6, 14, FIELD))
    f.append(text(wallx + 60, 118, "підвіс k_s", size=11, color=FIELD, bold=True))
    mcx = wallx + 150
    f.append(rect(mcx - 22, 128, 44, 44, fill="#dfe6ee", stroke=INK, sw=2))
    f.append(text(mcx, 154, "маса", size=10, color=INK))
    f.append(text(mcx, 200, "голий динамік", size=11, color=INK, bold=True))
    b, _, _ = textbox(mcx, 238, "f_s = (1/2π)·√(k_s/m)", size=12, fill=FILL, stroke=INK)
    f.append(b)

    # ПРАВОРУЧ: підвіс + повітряна пружина
    wx = 470
    f.append(line(wx, 90, wx, 210, color=INK, sw=3))
    f.append(coil(wx, 138, wx + 120, 6, 11, FIELD))
    f.append(text(wx + 60, 112, "підвіс k_s", size=10, color=FIELD, bold=True))
    # повітряна пружина другим шаром
    f.append(coil(wx, 168, wx + 120, 8, 11, NEG))
    f.append(text(wx + 60, 202, "повітря k_box", size=10, color=NEG, bold=True))
    mcx2 = wx + 150
    f.append(rect(mcx2 - 22, 128, 44, 44, fill="#dfe6ee", stroke=INK, sw=2))
    f.append(text(mcx2, 154, "маса", size=10, color=INK))
    f.append(text(mcx2, 96, "динамік у ящику", size=11, color=INK, bold=True, anchor="middle"))
    b, _, _ = textbox(mcx2 + 6, 250, "f_c = (1/2π)·√((k_s+k_box)/m)\n= f_s·√(1+V_as/V_box)",
                      size=11, fill="#fdecea", stroke=POS, bold=True)
    f.append(b)

    render(os.path.join(IMG, 'two-springs.svg'), W, H, *f)


# ── 5. Добротність Q_tc задає форму басу ────────────────────────────────────
def fig_q_curves():
    W, H = 760, 420
    f = [text(W / 2, 26, "Добротність ящика Q_tc задає форму нижнього краю", size=17, bold=True)]

    import math as _m
    # осі
    ox, oy = 90, 330          # початок координат
    axw, axh = 600, 250
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))        # X
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))        # Y
    f.append(text(ox + axw - 6, oy + 22, "частота (× f_c) →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - axh + 6, "рівень, дБ", size=11, color=MUTED, anchor="end"))
    # горизонталь 0 дБ
    y0db = oy - axh * 0.62
    f.append(line(ox, y0db, ox + axw, y0db, color=MUTED, sw=1, dash="4 4"))
    f.append(text(ox - 8, y0db + 4, "0", size=10, color=MUTED, anchor="end"))

    # частотна вісь: логарифм x у діапазоні 0.25..4 від f_c
    import math
    xr = (0.25, 4.0)
    def xf(r):
        t = (math.log(r) - math.log(xr[0])) / (math.log(xr[1]) - math.log(xr[0]))
        return ox + t * axw
    for r in (0.25, 0.5, 1, 2, 4):
        xx = xf(r)
        f.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.5))
        lbl = {0.25: "¼", 0.5: "½", 1: "1", 2: "2", 4: "4"}[r]
        f.append(text(xx, oy + 20, lbl, size=10, color=INK))
    # рівень: 20·log10 |H|, H другого порядку highpass: H = r²/√((1−r²)²+(r/Q)²), r у одиницях f_c
    def db(r, Q):
        r2 = r * r
        mag = r2 / math.sqrt((1 - r2) ** 2 + (r2 / (Q * Q)))
        return 20 * math.log10(max(mag, 1e-4))
    def ydb(v):
        # 0 дБ на y0db; шкала 10 дБ = 42 px
        return y0db - v * (42.0 / 10.0)
    curves = [(0.5, MUTED, "Q=0.5 (Bessel-подібна, м'яко)"),
              (0.707, FIELD, "Q=0.707 (Батерворт, максимально рівно)"),
              (1.2, POS, "Q=1.2 (горб — гучніше, але з дзвоном)")]
    for Q, col, _lab in curves:
        d = ""
        first = True
        rr = xr[0]
        while rr <= xr[1] + 1e-9:
            xx = xf(rr)
            yy = ydb(db(rr, Q))
            yy = max(oy - axh + 4, min(oy - 2, yy))
            d += ("M %.1f %.1f" % (xx, yy)) if first else (" L %.1f %.1f" % (xx, yy))
            first = False
            rr *= 1.04
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))

    # легенда праворуч унизу (у полі графіка, не чіпає криві зверху)
    ly = oy - axh + 8
    for i, (Q, col, lab) in enumerate(curves):
        yy = ly + i * 22
        f.append(line(ox + axw - 250, yy, ox + axw - 226, yy, color=col, sw=3))
        f.append(text(ox + axw - 220, yy + 4, lab, size=10, color=col, anchor="start", bold=(Q == 0.707)))

    b, _, _ = textbox(ox + 150, oy - 40,
                      "нижче f_c усі криві падають —\nпитання лише як круто й з яким горбом",
                      size=10, fill=FILL, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, 'q-curves.svg'), W, H, *f)


if __name__ == "__main__":
    fig_short_circuit()
    fig_bass_reflex()
    fig_inside_box()
    fig_two_springs()
    fig_q_curves()
    print("OK: figures written to", IMG)
