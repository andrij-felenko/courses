# -*- coding: utf-8 -*-
"""Фігури до теми «Насичення й тріодний режим MOSFET».
Три фігури:
  decision.svg    — дерево рішень: Vgs проти Vth (відсічка/канал), тоді Vds проти Vov (тріод/насичення)
  output-char.svg — сімейство ID(Vds): тріод → коліно → полиця; коліна на межі Vds=Vov; полиця трохи похила
  two-faces.svg   — той самий MOSFET: у тріоді — малий резистор (вимикач), у насиченні — джерело струму (підсилювач)
Запуск швидкий, без зациклень.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

TRI = NEG            # тріод — холодний синій (резистор)
SAT = FIELD         # насичення — зелений (джерело струму)
OFF = MUTED         # відсічка — сірий


# ── 1. Дерево рішень: який режим ─────────────────────────────────────────────
def fig_decision():
    W, H = 820, 470
    f = [text(W / 2, 30, "Який режим? — два порівняння", size=17, bold=True)]

    # вузол-питання (овальна рамка)
    def qnode(cx, cy, s, sub=None):
        lines = [s] + ([sub] if sub else [])
        size = 13
        tw = max(text_width(ln, size, ln == s) for ln in lines)
        w = tw + 34
        h = len(lines) * size * 1.5 + 20
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
               'fill="#f4f6f8" stroke="%s" stroke-width="1.8"/>'
               % (cx - w / 2, cy - h / 2, w, h, int(h / 2), INK))
        out += text(cx, cy - (1 if sub else 0) * 9 + 5, s, size=13, bold=True)
        if sub:
            out += text(cx, cy + 20, sub, size=11, color=MUTED)
        return out, w, h

    # лист-режим (прямокутник з кольоровим заголовком)
    def leaf(cx, cy, name, sub, color):
        lines = [name, sub[0], sub[1]]
        size = 12
        tw = max(text_width(name, 13, True),
                 text_width(sub[0], 11), text_width(sub[1], 12))
        w = tw + 30
        h = 78
        x, y = cx - w / 2, cy - h / 2
        out = rect(x, y, w, h, fill="#fcfcfd", stroke=color, sw=1.9)
        out += text(cx, y + 22, name, size=13, bold=True, color=color)
        out += text(cx, y + 42, sub[0], size=11, color=MUTED)
        out += text(cx, y + 62, sub[1], size=12, color=INK)
        return out, w, h

    def branch(x1, y1, x2, y2, label, tox_hh):
        # стрілка від низу вузла до верху цілі; підпис — збоку від лінії
        ax2, ay2 = x2, y2 - tox_hh - 4
        out = arrow(x1, y1, ax2, ay2, color=LINE, sw=1.7)
        mx, my = (x1 + ax2) / 2, (y1 + ay2) / 2
        dx, dy = ax2 - x1, ay2 - y1
        L = math.hypot(dx, dy) or 1
        px, py = -dy / L, dx / L
        # відводимо підпис назовні від центра малюнка
        if (mx - W / 2) * px < 0:
            px, py = -px, -py
        lx0, ly0 = mx + px * 22, my + py * 22
        lw = text_width(label, 12, True)
        out += rect(lx0 - lw / 2 - 4, ly0 - 13, lw + 8, 18, fill="#ffffff", stroke="none", sw=0)
        out += text(lx0, ly0, label, size=12, bold=True, color=INK)
        return out

    # верхній вузол
    top, tw, thh = qnode(410, 78, "Vgs проти Vth ?")
    thh /= 2
    # відсічка (ліворуч)
    lf_off, wo, ho = leaf(150, 250, "ВІДСІЧКА", ("каналу нема", "ID ≈ 0"), OFF)
    # другий вузол (праворуч)
    q2, w2, h2 = qnode(560, 210, "Vds проти Vov ?", "Vov = Vgs − Vth")
    h2 /= 2
    # тріод / насичення (унизу)
    lf_tri, wt, ht = leaf(430, 390, "ТРІОД", ("канал суцільний · резистор",
                                              "ID = k·[Vov·Vds − Vds²/2]"), TRI)
    lf_sat, ws, hs = leaf(680, 390, "НАСИЧЕННЯ", ("стік защемлено · джерело струму",
                                                  "ID = (k/2)·Vov²"), SAT)

    # спершу стрілки (під рамками)
    f.append(branch(410, 78 + thh, 150, 250, "Vgs < Vth", ho / 2))
    f.append(branch(410, 78 + thh, 560, 210, "Vgs > Vth", h2))
    f.append(branch(560, 210 + h2, 430, 390, "Vds < Vov", ht / 2))
    f.append(branch(560, 210 + h2, 680, 390, "Vds ≥ Vov", hs / 2))
    # тоді рамки (над стрілками)
    f += [top, lf_off, q2, lf_tri, lf_sat]
    render(os.path.join(IMG, "decision.svg"), W, H, *f)


# ── 2. Вихідна характеристика ID(Vds): тріод → коліно → насичення ─────────────
def fig_output_char():
    W, H = 780, 470
    ox, oy = 110, 380
    axw, axh = 590, 300
    VDS_MAX, ID_MAX = 5.0, 3.5
    LAM = 0.05
    f = [text(W / 2, 30, "Вихідна характеристика: тріод, коліно, насичення", size=17, bold=True)]

    def X(vds):
        return ox + vds / VDS_MAX * axw

    def Y(idr):
        return oy - idr / ID_MAX * axh

    # осі
    f.append(arrow(ox, oy, ox + axw + 8, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh - 8, color=INK, sw=1.6))
    f.append(text(ox + axw + 4, oy + 26, "Vds", size=14, italic=True))
    f.append(text(ox - 58, oy - axh - 2, "ID", size=14, anchor="start", italic=True))

    covs = [(1.2, "#8fb0ef"), (1.8, TRI), (2.4, "#15306f")]
    knees = []
    for vov, col in covs:
        pts = []
        n = 44
        for i in range(n + 1):                       # тріод: 0 → Vov
            vds = vov * i / n
            idr = vov * vds - vds * vds / 2
            pts.append("%.1f,%.1f" % (X(vds), Y(idr)))
        idk = 0.5 * vov * vov                        # струм коліна
        m = 40
        for i in range(1, m + 1):                    # насичення: Vov → max, легкий нахил
            vds = vov + (VDS_MAX - vov) * i / m
            idr = idk * (1 + LAM * (vds - vov))
            pts.append("%.1f,%.1f" % (X(vds), Y(idr)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
        knees.append((X(vov), Y(idk), col))

    # межа Vds = Vov: парабола ID = (k/2)Vds², нанизана на коліна
    bpts = []
    vmax_b = covs[-1][0]
    k = 60
    for i in range(k + 1):
        vds = vmax_b * i / k
        bpts.append("%.1f,%.1f" % (X(vds), Y(0.5 * vds * vds)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-dasharray="7 5"/>' % (" ".join(bpts), POS))
    for kx, ky, col in knees:                         # позначки колін
        f.append(circle(kx, ky, 4, fill="#fff", stroke=col, sw=1.9))

    # підпис межі — біля верхнього коліна, збоку від параболи
    tkx, tky, _ = knees[-1]
    f.append(text(tkx + 12, tky - 14, "межа  Vds = Vov", size=12, bold=True, color=POS, anchor="start"))

    # зони
    f.append(text(ox + 78, oy - 150, "ТРІОД", size=14, bold=True, color=TRI))
    f.append(text(ox + 78, oy - 133, "(резистор)", size=11, color=TRI))
    f.append(text(ox + 400, oy - 250, "НАСИЧЕННЯ", size=14, bold=True, color=SAT))
    f.append(text(ox + 400, oy - 233, "(джерело струму)", size=11, color=SAT))
    f.append(text(ox + axw - 6, oy - 60, "більший Vgs → вища полиця", size=12, color=MUTED, anchor="end"))

    # нахил біля початку ≈ 1/Rds(on)
    f.append(text(ox + 150, oy - 40, "нахил біля 0  ≈  1/Rds(on)", size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "output-char.svg"), W, H, *f)


# ── 3. Дві особистості: вимикач (тріод) vs підсилювач (насичення) ────────────
def fig_two_faces():
    W, H = 800, 430
    f = [text(W / 2, 30, "Один MOSFET — два прилади", size=17, bold=True)]

    # центральний вузол
    cx0, cy0 = 400, 92
    bw, bh = 190, 54
    f.append(rect(cx0 - bw / 2, cy0 - bh / 2, bw, bh, fill="#f4f6f8", stroke=INK, sw=1.9))
    f.append(text(cx0, cy0 - 4, "той самий MOSFET", size=14, bold=True))
    f.append(text(cx0, cy0 + 16, "затвор відкрито (Vgs > Vth)", size=10, color=MUTED))

    def resistor(cx, cy, color):
        w, h = 66, 24
        out = line(cx - w / 2 - 20, cy, cx - w / 2, cy, color=INK, sw=1.7)
        out += line(cx + w / 2, cy, cx + w / 2 + 20, cy, color=INK, sw=1.7)
        out += rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2fb", stroke=color, sw=2.0, rx=3)
        return out

    def csource(cx, cy, color):
        r = 26
        out = circle(cx, cy, r, fill="#edf8f1", stroke=color, sw=2.0)
        out += arrow(cx, cy + 15, cx, cy - 15, color=color, sw=2.2)
        out += line(cx, cy - r - 18, cx, cy - r, color=INK, sw=1.7)
        out += line(cx, cy + r, cx, cy + r + 18, color=INK, sw=1.7)
        return out

    def branch_arrow(x2, label, color):
        out = arrow(cx0, cy0 + bh / 2, x2, 168, color=LINE, sw=1.8)
        side = -1 if x2 < cx0 else 1
        out += text((cx0 + x2) / 2 + side * 30, 130, label, size=12, bold=True, color=color)
        return out

    # ── ліва колонка: глибокий тріод → вимикач
    lx = 190
    f.append(branch_arrow(lx, "глибокий тріод", TRI))
    f.append(text(lx, 190, "ГЛИБОКИЙ ТРІОД", size=14, bold=True, color=TRI))
    f.append(text(lx, 208, "(мала Vds)", size=11, color=MUTED))
    f.append(resistor(lx, 262, TRI))
    f.append(text(lx, 302, "Rds(on) — малий і сталий", size=12, color=INK))
    b1, w1, h1 = textbox(lx, 350, "= ВИМИКАЧ", size=15, bold=True,
                         fill="#eef2fb", stroke=TRI, color=TRI, pad=12)
    f.append(b1)
    f.append(text(lx, 398, "падає міліволти, майже не гріється", size=10, color=MUTED))

    # ── права колонка: насичення → підсилювач
    rx = 610
    f.append(branch_arrow(rx, "насичення", SAT))
    f.append(text(rx, 190, "НАСИЧЕННЯ", size=14, bold=True, color=SAT))
    f.append(text(rx, 208, "(Vds ≥ Vov)", size=11, color=MUTED))
    f.append(csource(rx, 262, SAT))
    f.append(text(rx, 320, "струм ID — від Vgs", size=12, color=INK))
    b2, w2, h2 = textbox(rx, 350, "= ПІДСИЛЮВАЧ", size=15, bold=True,
                         fill="#edf8f1", stroke=SAT, color=SAT, pad=12)
    f.append(b2)
    f.append(text(rx, 398, "мала ΔVgs → велика ΔID", size=10, color=MUTED))

    render(os.path.join(IMG, "two-faces.svg"), W, H, *f)


# ── 4. Пастка: не тою формулою не в тому режимі (для proj-region-solver) ──────
def fig_region_traps():
    W, H = 860, 500
    ox, oy = 118, 400
    axw, axh = 660, 312
    VDS_MAX, ID_MAX = 6.0, 2.85
    K, VOV = 0.5, 3.0                       # той самий приклад теми: Vov=3, k=0.5
    SHELF = 0.5 * K * VOV * VOV             # висота полиці = 2.25
    WRONG_TRI = "#7c3aed"                   # тріодна формула скрізь — фіолетовий
    f = [text(W / 2, 30, "Дві типові помилки: не тою формулою не в тому режимі", size=17, bold=True)]

    def X(vds):
        return ox + vds / VDS_MAX * axw

    def Y(idr):
        return oy - idr / ID_MAX * axh

    def tri(vds):                           # тріодна парабола
        return K * (VOV * vds - vds * vds / 2)

    # осі (стрілка Х трохи довша за останню поділку 2·Vov, щоб підпис "Vds" не сів на неї)
    f.append(arrow(ox, oy, ox + axw + 42, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh - 10, color=INK, sw=1.6))
    f.append(text(ox + axw + 34, oy + 26, "Vds", size=14, italic=True))
    f.append(text(ox - 60, oy - axh - 4, "ID", size=14, anchor="start", italic=True))

    # межа режимів + мітки осей (Vov, 2·Vov, полиця)
    f.append(line(X(VOV), oy, X(VOV), Y(ID_MAX) + 4, color=MUTED, sw=1.2, dash="4 5"))
    f.append(line(ox, Y(SHELF), X(VOV), Y(SHELF), color=MUTED, sw=1.0, dash="3 5"))
    f.append(text(X(VOV), oy + 22, "Vov", size=12, bold=True, color=INK))
    f.append(text(X(2 * VOV), oy + 22, "2·Vov", size=12, color=MUTED))
    f.append(text(ox - 12, Y(SHELF) + 4, "(k/2)Vov²", size=11, color=MUTED, anchor="end"))

    # 1) тріодна формула СКРІЗЬ: парабола, що за коліном падає до нуля
    p = ["%.1f,%.1f" % (X(v * VDS_MAX / 80), Y(tri(v * VDS_MAX / 80))) for v in range(81)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="8 6"/>' % (" ".join(p), WRONG_TRI))

    # 2) формула насичення СКРІЗЬ: горизонталь на висоті полиці від самого нуля
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" stroke-dasharray="8 6"/>'
             % (X(0), Y(SHELF), X(VDS_MAX), Y(SHELF), POS))

    # 3) ПРАВИЛЬНО: тріод 0→Vov, тоді пласка полиця Vov→max (λ=0)
    pc = ["%.1f,%.1f" % (X(VOV * i / 40), Y(tri(VOV * i / 40))) for i in range(41)]
    pc += ["%.1f,%.1f" % (X(VOV + (VDS_MAX - VOV) * i / 40), Y(SHELF)) for i in range(1, 41)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join(pc), FIELD))

    # коліно — точка збігу всіх трьох
    f.append(circle(X(VOV), Y(SHELF), 5, fill="#fff", stroke=INK, sw=2.0))
    f.append(text(X(VOV) + 10, Y(SHELF) - 52, "коліно Vds = Vov:", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(X(VOV) + 10, Y(SHELF) - 36, "усі три збігаються", size=12, color=INK, anchor="start"))
    f.append(line(X(VOV) + 8, Y(SHELF) - 30, X(VOV) + 2, Y(SHELF) - 8, color=MUTED, sw=1.0))

    # підпис хибної насиченнєвої гілки — у тріодній зоні, над горизонталлю
    f.append(text(X(0.35), Y(SHELF) - 20, "насичення скрізь →", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(X(0.35), Y(SHELF) - 5, "завищено біля нуля", size=11, color=POS, anchor="start"))

    # підпис хибної тріодної гілки — де парабола вже падає
    f.append(text(X(4.75), Y(tri(4.75)) + 26, "тріод скрізь →", size=12, bold=True, color=WRONG_TRI, anchor="middle"))
    f.append(text(X(4.75), Y(tri(4.75)) + 42, "спадає замість полиці", size=11, color=WRONG_TRI, anchor="middle"))

    # зони
    f.append(text(X(1.5), oy - 16, "ТРІОД", size=12, bold=True, color=MUTED))
    f.append(text(X(4.5), oy - 16, "НАСИЧЕННЯ", size=12, bold=True, color=MUTED))

    # легенда (верхній лівий кут, над полицею)
    lx, ly = ox + 14, 62
    def legrow(y, col, dashed, s):
        d = ' stroke-dasharray="8 6"' if dashed else ''
        seg = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
               'stroke-width="3"%s/>' % (lx, y, lx + 34, y, col, d))
        return seg + text(lx + 44, y + 4, s, size=12, color=INK, anchor="start")
    f.append(legrow(ly, FIELD, False, "правильно: тріод → коліно → полиця"))
    f.append(legrow(ly + 20, POS, True, "лише формула насичення (хибно в тріоді)"))
    f.append(legrow(ly + 40, WRONG_TRI, True, "лише тріодна формула (хибно в насиченні)"))

    render(os.path.join(IMG, "region-traps.svg"), W, H, *f)


# ── 5. Лампові форми, що дали імена (вставка hist-region-names) ───────────────
def fig_tube_shapes():
    W, H = 900, 460
    f = [text(W / 2, 30, "Дві лампові форми — два імені режимів FET", size=17, bold=True)]

    def panel(ox, oy, aw, ah, curves, color, name, sub):
        out = ""
        out += arrow(ox, oy, ox + aw + 8, oy, color=INK, sw=1.5)
        out += arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.5)
        out += text(ox + aw + 6, oy + 20, "Uа", size=12, italic=True, anchor="end", color=MUTED)
        out += text(ox - 6, oy - ah - 2, "Iа", size=12, italic=True, anchor="end", color=MUTED)
        for fn in curves:
            pts = []
            n = 48
            for i in range(n + 1):
                xf = i / n
                yf = fn(xf)
                pts.append("%.1f,%.1f" % (ox + xf * aw, oy - yf * ah))
            out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                    % (" ".join(pts), color))
        out += text(ox + aw / 2, oy - ah - 30, name, size=15, bold=True, color=color)
        out += text(ox + aw / 2, oy - ah - 13, sub, size=11, color=MUTED)
        return out

    import math as _m
    # тріод: струм весь час росте (похило), ніколи не плаский
    tri = [(lambda x, s=s: s * (x ** 0.72)) for s in (0.92, 0.68, 0.45)]
    # пентод: круто злітає й лягає на майже сталу полицю
    pen = [(lambda x, a=a: a * (1 - _m.exp(-x / 0.11)) * (1 + 0.05 * x)) for a in (0.86, 0.62, 0.40)]

    ox1, oy1, aw1, ah1 = 95, 320, 285, 175
    ox2, oy2, aw2, ah2 = 545, 320, 285, 175
    f.append(panel(ox1, oy1, aw1, ah1, tri, NEG, "ТРІОД", "де Форест · США · 1908"))
    f.append(panel(ox2, oy2, aw2, ah2, pen, FIELD, "ПЕНТОД", "Голст і Теллеген · Philips · 1926"))

    f.append(text(ox1 + aw1 - 8, oy1 - ah1 + 30, "струм росте", size=12, color=NEG, anchor="end", bold=True))
    f.append(text(ox1 + aw1 - 8, oy1 - ah1 + 47, "з напругою", size=12, color=NEG, anchor="end"))
    f.append(text(ox2 + aw2 - 8, oy2 - 132, "пласка полиця", size=12, color=FIELD, anchor="end", bold=True))
    f.append(text(ox2 + aw2 - 8, oy2 - 115, "(джерело струму)", size=11, color=FIELD, anchor="end"))

    b1, w1, h1 = textbox(ox1 + aw1 / 2, 400, "→ ім'я ТРІОДНОМУ режиму FET",
                         size=13, bold=True, fill="#eef2fb", stroke=NEG, color=NEG, pad=11)
    f.append(b1)
    f.append(text(ox1 + aw1 / 2, 430, "похилий склон вихідної кривої", size=11, color=MUTED))
    b2, w2, h2 = textbox(ox2 + aw2 / 2, 400, "→ ім'я НАСИЧЕННЮ FET",
                         size=13, bold=True, fill="#edf8f1", stroke=FIELD, color=FIELD, pad=11)
    f.append(b2)
    f.append(text(ox2 + aw2 / 2, 430, "пласка полиця вихідної кривої", size=11, color=MUTED))

    render(os.path.join(IMG, "tube-shapes.svg"), W, H, *f)


# ── 6. Пастка «насичення»: той самий термін — протилежні стани ────────────────
def fig_sat_cross():
    W, H = 780, 400
    f = [text(W / 2, 30, "Пастка: «насичення» означає протилежне", size=17, bold=True)]

    col_m, col_b = 380, 600           # центри колонок MOSFET / BJT
    cw, chh = 175, 62                  # розмір клітини
    row1, row2 = 165, 275             # центри рядків (ключ / підсилювач)
    rlx = 250                          # правий край підписів рядків

    f.append(text(col_m, 92, "MOSFET", size=15, bold=True, color=INK))
    f.append(text(col_b, 92, "BJT", size=15, bold=True, color=INK))

    f.append(text(rlx, row1 - 6, "як ВИМИКАЧ", size=13, bold=True, anchor="end", color=INK))
    f.append(text(rlx, row1 + 12, "(Vds, Vce ≈ 0)", size=11, anchor="end", color=MUTED))
    f.append(text(rlx, row2 - 6, "як ПІДСИЛЮВАЧ", size=13, bold=True, anchor="end", color=INK))
    f.append(text(rlx, row2 + 12, "(активне підсилення)", size=11, anchor="end", color=MUTED))

    def cell(cx, cy, label, color, hot):
        x, y = cx - cw / 2, cy - chh / 2
        fill = "#fdecea" if hot else "#f4f6f8"
        sw = 2.4 if hot else 1.6
        out = rect(x, y, cw, chh, fill=fill, stroke=color, sw=sw)
        out += text(cx, cy + 6, label, size=15, bold=hot, color=color)
        return out

    # діагональ між двома клітинами «насичення» (під клітинами)
    f.append(line(col_b, row1 + chh / 2 - 4, col_m, row2 - chh / 2 + 4,
                  color=POS, sw=2.0, dash="7 5"))

    f.append(cell(col_m, row1, "тріод", NEG, False))
    f.append(cell(col_b, row1, "НАСИЧЕННЯ", POS, True))
    f.append(cell(col_m, row2, "НАСИЧЕННЯ", POS, True))
    f.append(cell(col_b, row2, "активний", FIELD, False))

    f.append(text(W / 2, 350, "Однаковий рядок = однаковий стан. «Насичення» ж — по діагоналі:",
                  size=12, color=INK))
    f.append(text(W / 2, 372, "у MOSFET це підсилювач, у BJT — замкнений ключ.",
                  size=12, color=POS, bold=True))

    render(os.path.join(IMG, "sat-cross.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision()
    fig_output_char()
    fig_two_faces()
    fig_region_traps()
    fig_tube_shapes()
    fig_sat_cross()
    print("OK: 6 figures ->", IMG)
