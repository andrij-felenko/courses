# -*- coding: utf-8 -*-
"""Фігури до теми «Алгоритми стеження за MPP». Запуск із теки теми: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── помічники ────────────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-linejoin="round"%s/>' % (p, color, sw, d))


def dot(cx, cy, r=5, fill=INK, stroke=BG, sw=2):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)


def iv_points(Voc=1.0, Isc=1.0, c=0.11, n=90):
    """ВАХ: I(0)=Isc, I(Voc)=0, коліно керує параметр c (менший c — різкіше)."""
    denom = 1 - math.exp(-Voc / c)
    out = []
    for i in range(n + 1):
        V = Voc * i / n
        I = Isc * (1 - math.exp((V - Voc) / c)) / denom
        out.append((V, max(0.0, I)))
    return out


def pv_points(Voc=1.0, Isc=1.0, c=0.11, n=90):
    return [(V, V * I) for (V, I) in iv_points(Voc, Isc, c, n)]


def pv_peak(Voc=1.0, Isc=1.0, c=0.11, n=400):
    best = (0.0, 0.0)
    denom = 1 - math.exp(-Voc / c)
    for i in range(n + 1):
        V = Voc * i / n
        I = Isc * (1 - math.exp((V - Voc) / c)) / denom
        P = V * I
        if P > best[1]:
            best = (V, P)
    return best  # (Vmp, Pmp)


def axes(px, py, pw, ph, xlabel, ylabel):
    """Осі L-подібні; підписи винесені з запасом за межі поля."""
    s = line(px, py, px, py + ph, color=INK, sw=2)
    s += line(px, py + ph, px + pw, py + ph, color=INK, sw=2)
    s += text(px + pw, py + ph + 26, xlabel, size=15, color=MUTED, anchor="end")
    s += text(px - 14, py - 14, ylabel, size=15, color=MUTED, anchor="start")
    return s


def mapper(px, py, pw, ph, xmax, ymax):
    def m(x, y):
        return (px + pw * (x / xmax), py + ph - ph * (y / ymax))
    return m


# ── Фігура 1: контур стеження (де живе алгоритм і що він крутить) ────────────
def fig_loop():
    W, H = 820, 400
    frags = []
    ytop = 120
    # три силові блоки
    b1, w1, h1 = textbox(140, ytop, "Сонячна\nпанель", size=15, bold=True,
                         fill="#eafaf1", stroke=FIELD, min_w=150)
    b2, w2, h2 = textbox(430, ytop, "Перетворювач\n(buck / boost)", size=15, bold=True,
                         fill=FILL, stroke=LINE, min_w=180)
    b3, w3, h3 = textbox(710, ytop, "Батарея /\nнавантаження", size=15, bold=True,
                         fill="#eaf0fd", stroke=NEG, min_w=160)
    # силовий потік
    frags.append(arrow(140 + w1 / 2 + 4, ytop, 430 - w2 / 2 - 6, ytop, color=POS, sw=3))
    frags.append(arrow(430 + w2 / 2 + 4, ytop, 710 - w3 / 2 - 6, ytop, color=POS, sw=3))
    frags.append(text(285, ytop - 20, "потужність", size=13, color=POS))
    frags.append(text(575, ytop - 20, "потужність", size=13, color=POS))
    frags.append(b1); frags.append(b2); frags.append(b3)

    # вузол відбору V,I на вході перетворювача
    xnode = 300
    frags.append(dot(xnode, ytop, 5, fill=INK))
    yctl = 315
    # лінія відбору вниз
    frags.append(line(xnode, ytop + h1 / 2 - 2, xnode, yctl, color=NEG, sw=2))
    frags.append(arrow(xnode, yctl, 335, yctl, color=NEG, sw=2))
    frags.append(text(xnode - 12, (ytop + yctl) / 2, "V, I", size=14, color=NEG,
                      anchor="end", bold=True))

    # контролер
    bc, wc, hc = textbox(470, yctl,
                         "Контролер MPP:  виміряти V, I  →  P = V·I  →  повернути шпаруватість D",
                         size=14, bold=False, fill="#fff8e1", stroke="#b8860b", min_w=380)
    frags.append(bc)

    # керувальний вихід D назад у перетворювач
    xduty = 560
    frags.append(line(470 + wc / 2, yctl, xduty, yctl, color="#b8860b", sw=2))
    frags.append(arrow(xduty, yctl, xduty, ytop + h2 / 2 + 2, color="#b8860b", sw=2.4))
    frags.append(text(xduty + 12, (ytop + yctl) / 2 + 6, "D  (ШІМ)", size=14,
                      color="#b8860b", anchor="start", bold=True))

    return render(os.path.join(IMG, 'loop.svg'), W, H, *frags,
                  title="Контур стеження: алгоритм крутить одну ручку — шпаруватість")


# ── Фігура 2: P&O лізе на горб і довіку коливається ─────────────────────────
def fig_po_climb():
    W, H = 820, 470
    px, py, pw, ph = 90, 70, 620, 320
    Voc, Isc, c = 1.0, 1.0, 0.11
    Vmp, Pmp = pv_peak(Voc, Isc, c)
    pv = pv_points(Voc, Isc, c)
    ymax = Pmp * 1.18
    m = mapper(px, py, pw, ph, Voc, ymax)

    frags = [axes(px, py, pw, ph, "напруга панелі V", "потужність P = V·I")]
    frags.append(polyline([m(V, P) for V, P in pv], color=INK, sw=2.8))

    # лінія MPP
    xmp, ymp = m(Vmp, Pmp)
    frags.append(line(xmp, py, xmp, py + ph, color=FIELD, sw=1.6, dash="5 5"))
    frags.append(dot(xmp, ymp, 6, fill=FIELD))
    frags.append(text(xmp, py - 12, "MPP", size=15, color=FIELD, bold=True))

    # кроки вгору лівим схилом
    def P_at(V):
        denom = 1 - math.exp(-Voc / c)
        I = Isc * (1 - math.exp((V - Voc) / c)) / denom
        return V * I
    climbV = [0.30, 0.44, 0.57, 0.68]
    prev = None
    for V in climbV:
        pt = m(V, P_at(V))
        frags.append(dot(*pt, r=4.5, fill=NEG))
        if prev:
            frags.append(arrow(prev[0], prev[1], pt[0], pt[1], color=NEG, sw=2.2))
        prev = pt

    # коливання астрид піка (зигзаг чотирма точками)
    osc = [Vmp - 0.05, Vmp + 0.05, Vmp - 0.05, Vmp + 0.05]
    prev = None
    for V in osc:
        pt = m(V, P_at(V))
        frags.append(dot(*pt, r=4.5, fill=POS))
        if prev:
            frags.append(arrow(prev[0], prev[1], pt[0], pt[1], color=POS, sw=2.0))
        prev = pt

    # легенда у вільному верхньому-лівому куті (там крива низько)
    lx, ly = px + 24, py + 34
    frags.append(dot(lx, ly - 4, 5, fill=NEG))
    frags.append(text(lx + 14, ly, "лізе вгору, поки P росте", size=13, color=NEG, anchor="start"))
    frags.append(dot(lx, ly + 22 - 4, 5, fill=POS))
    frags.append(text(lx + 14, ly + 22, "P впала → розворот, далі коливання",
                      size=13, color=POS, anchor="start"))
    frags.append(text(xmp, py + ph + 52,
                      "довічні коливання навколо MPP: більший крок — швидше, але тряскіше",
                      size=13, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, 'po-climb.svg'), W, H, *frags,
                  title="Perturb & Observe: наосліп угору схилом, тоді танець навколо піка")


# ── Фігура 3: перевірка нахилу (умова приростової провідності) ───────────────
def fig_slope():
    W, H = 820, 470
    px, py, pw, ph = 90, 70, 620, 320
    Voc, Isc, c = 1.0, 1.0, 0.11
    Vmp, Pmp = pv_peak(Voc, Isc, c)
    pv = pv_points(Voc, Isc, c)
    ymax = Pmp * 1.18
    m = mapper(px, py, pw, ph, Voc, ymax)

    def P_at(V):
        denom = 1 - math.exp(-Voc / c)
        I = Isc * (1 - math.exp((V - Voc) / c)) / denom
        return V * I

    frags = [axes(px, py, pw, ph, "напруга панелі V", "потужність P")]
    frags.append(polyline([m(V, P) for V, P in pv], color=INK, sw=2.8))

    xmp, ymp = m(Vmp, Pmp)
    frags.append(line(xmp, py, xmp, py + ph, color=FIELD, sw=1.6, dash="5 5"))
    frags.append(dot(xmp, ymp, 6, fill=FIELD))

    # дотичні у трьох точках
    def tangent(V0, dx, color, sw=2.6):
        h = 0.0025
        slope = (P_at(V0 + h) - P_at(V0 - h)) / (2 * h)
        x0, y0 = m(V0, P_at(V0))
        # намалювати відрізок ±dx у даних-координатах
        xa, ya = m(V0 - dx, P_at(V0) - slope * dx)
        xb, yb = m(V0 + dx, P_at(V0) + slope * dx)
        return line(xa, ya, xb, yb, color=color, sw=sw), (x0, y0)

    seg, p_left = tangent(0.55, 0.13, NEG)
    frags.append(seg); frags.append(dot(*p_left, r=5, fill=NEG))
    seg, p_top = tangent(Vmp, 0.13, FIELD)
    frags.append(seg)
    seg, p_right = tangent(0.92, 0.09, POS)
    frags.append(seg); frags.append(dot(*p_right, r=5, fill=POS))

    # підписи нахилів — рознесені, повз криву
    frags.append(text(px + 40, py + 40, "лівий схил", size=14, color=NEG, anchor="start", bold=True))
    frags.append(text(px + 40, py + 62, "dP/dV > 0", size=14, color=NEG, anchor="start"))
    frags.append(text(px + 40, py + 82, "→ підняти V", size=13, color=NEG, anchor="start"))

    frags.append(text(xmp, py - 12, "MPP:  dP/dV = 0", size=15, color=FIELD, bold=True))

    frags.append(text(px + pw - 20, py + 40, "правий схил", size=14, color=POS, anchor="end", bold=True))
    frags.append(text(px + pw - 20, py + 62, "dP/dV < 0", size=14, color=POS, anchor="end"))
    frags.append(text(px + pw - 20, py + 82, "→ спустити V", size=13, color=POS, anchor="end"))

    frags.append(text(px + pw / 2, py + ph + 52,
                      "те саме без множення: dI/dV  порівняти з  −I/V   (рівні — це і є MPP)",
                      size=14, color=INK, anchor="middle"))

    return render(os.path.join(IMG, 'slope-test.svg'), W, H, *frags,
                  title="Перевірка нахилу: з якого боку від піка ми стоїмо")


# ── Фігура 4: MPP — рухома ціль (світло й температура зсувають горб) ─────────
def fig_moving():
    W, H = 820, 460
    px, py, pw, ph = 90, 70, 640, 310
    Voc, Isc, c = 1.0, 1.0, 0.11
    _, Pmp_hi = pv_peak(Voc, Isc, c)
    ymax = Pmp_hi * 1.20
    m = mapper(px, py, pw, ph, 1.05, ymax)

    frags = [axes(px, py, pw, ph, "напруга панелі V", "потужність P")]

    # яскраве сонце
    pv_hi = pv_points(Voc, Isc, c)
    frags.append(polyline([m(V, P) for V, P in pv_hi], color=POS, sw=2.8))
    Vh, Ph = pv_peak(Voc, Isc, c)
    frags.append(dot(*m(Vh, Ph), r=6, fill=POS))
    frags.append(text(*[m(Vh, Ph)[0] + 6, m(Vh, Ph)[1] - 14], s="яскраво",
                      size=13, color=POS, anchor="start", bold=True))

    # слабке світло (менший Isc)
    pv_lo = pv_points(Voc, 0.5, c)
    frags.append(polyline([m(V, P) for V, P in pv_lo], color=NEG, sw=2.8))
    Vl, Pl = pv_peak(Voc, 0.5, c)
    frags.append(dot(*m(Vl, Pl), r=6, fill=NEG))
    frags.append(text(*[m(Vl, Pl)[0] + 8, m(Vl, Pl)[1] - 12], s="хмара",
                      size=13, color=NEG, anchor="start", bold=True))

    # гаряча панель за яскравого світла (зсув Voc уліво)
    pv_hot = pv_points(0.82, 0.98, c)
    frags.append(polyline([m(V, P) for V, P in pv_hot], color="#b8860b", sw=2.4, dash="7 5"))
    Vt, Pt = pv_peak(0.82, 0.98, c)
    frags.append(dot(*m(Vt, Pt), r=6, fill="#b8860b"))
    frags.append(text(*[m(Vt, Pt)[0] - 8, m(Vt, Pt)[1] - 14], s="гаряче",
                      size=13, color="#b8860b", anchor="end", bold=True))

    # дуга «ціль рухається» між піками
    a = m(Vl, Pl); b = m(Vh, Ph)
    frags.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="3 4"/>'
                 % (a[0], a[1] - 8, (a[0] + b[0]) / 2, py - 6, b[0], b[1] - 12, MUTED))

    frags.append(text(px + pw / 2, py + ph + 54,
                      "MPP гуляє з освітленням і температурою — тому ціль ловлять безперервно, а не задають раз",
                      size=13, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, 'moving-mpp.svg'), W, H, *frags,
                  title="MPP — рухома ціль: горб повзе за сонцем і теплом")


# ── Фігура 5 (вставка): влягання перед виміром ──────────────────────────────
def fig_settle():
    W, H = 880, 450
    px, py, pw, ph = 100, 95, 690, 240
    T, t_settle, t_meas_end = 10.0, 4.0, 7.2
    Pss, A, tau, per = 0.72, 0.22, 1.5, 2.5
    m = mapper(px, py, pw, ph, T, 1.0)

    def Pt(t):
        return Pss + A * math.exp(-t / tau) * math.cos(2 * math.pi * t / per)

    xa, _ = m(0, 0); xb, _ = m(t_settle, 0); xc, _ = m(t_meas_end, 0)
    frags = [rect(xa, py, xb - xa, ph, fill="#fdecea", stroke="none", sw=0, rx=0),
             rect(xb, py, xc - xb, ph, fill="#eafaf1", stroke="none", sw=0, rx=0),
             axes(px, py, pw, ph, "час після збурення, мс", "виміряна P")]
    frags.append(polyline([m(T * i / 180, Pt(T * i / 180)) for i in range(181)], color=INK, sw=2.6))

    frags.append(line(xa, py - 6, xa, py + ph, color="#b8860b", sw=2, dash="5 4"))
    frags.append(text(xa + 4, py + ph + 24, "збурення D  (t = 0)", size=12, color="#b8860b", anchor="start", bold=True))
    frags.append(line(xb, py, xb, py + ph, color=FIELD, sw=1.6, dash="4 4"))
    frags.append(text(xb, py + ph + 24, "кінець влягання", size=12, color=FIELD, anchor="middle"))

    tx = 1.15
    ptx = m(tx, Pt(tx))
    frags.append(text(ptx[0], ptx[1] + 6, "✕", size=22, color=POS, bold=True))
    frags.append(text(ptx[0] + 10, ptx[1] + 24, "вимір тут → брехня", size=12, color=POS, anchor="start", bold=True))

    for j in range(5):
        t = t_settle + (t_meas_end - t_settle) * (j + 0.5) / 5
        pt = m(t, Pt(t))
        frags.append(dot(pt[0], pt[1], 4, fill=FIELD))

    frags.append(text((xa + xb) / 2, py + 18, "НЕ міряти", size=14, color=POS, bold=True))
    frags.append(text((xb + xc) / 2, py + 18, "усереднити тут", size=14, color=FIELD, bold=True))
    frags.append(text(px + pw / 2, py + ph + 52,
                      "після кожного збурення — дочекатися влягання, і лише тоді усереднювати вимір",
                      size=13, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'settle-window.svg'), W, H, *frags,
                  title="Влягання перед виміром: інакше міряєш перехідний процес, а не робочу точку")


# ── Фігура 6 (вставка): адаптивний крок проти фіксованого ───────────────────
def fig_adaptive():
    W, H = 880, 460
    px, py, pw, ph = 100, 80, 680, 300
    Voc, Isc, c = 1.0, 1.0, 0.11
    Vmp, Pmp = pv_peak(Voc, Isc, c)

    def P_of(V):
        V = min(max(V, 0.0), Voc)
        denom = 1 - math.exp(-Voc / c)
        I = Isc * (1 - math.exp((V - Voc) / c)) / denom
        return V * max(0.0, I)

    N = 32

    def sim(step_fn):
        V, d, pprev, tr = 0.30, +1, P_of(0.30), [P_of(0.30)]
        for _ in range(1, N):
            p = P_of(V)
            if p < pprev - 1e-9:
                d = -d
            V = min(max(V + d * step_fn(abs(p - pprev)), 0.04), 0.99)
            pprev = p
            tr.append(P_of(V))
        return tr

    tr_small = sim(lambda dp: 0.020)
    tr_big = sim(lambda dp: 0.085)
    tr_adapt = sim(lambda dp: min(0.085, max(0.014, 2.6 * dp)))

    ymin, ymax = 0.30 * Pmp, Pmp * 1.12

    def mm(k, P):
        return (px + pw * (k / (N - 1)), py + ph - ph * ((P - ymin) / (ymax - ymin)))

    frags = [axes(px, py, pw, ph, "крок алгоритму", "потужність P")]
    ymp = py + ph - ph * ((Pmp - ymin) / (ymax - ymin))
    frags.append(line(px, ymp, px + pw, ymp, color=FIELD, sw=1.6, dash="6 5"))
    frags.append(text(px + pw, ymp - 8, "Pmp (стеля)", size=13, color=FIELD, anchor="end", bold=True))
    frags.append(polyline([mm(k, tr_small[k]) for k in range(N)], color=NEG, sw=2.4))
    frags.append(polyline([mm(k, tr_big[k]) for k in range(N)], color=POS, sw=2.2))
    frags.append(polyline([mm(k, tr_adapt[k]) for k in range(N)], color="#b8860b", sw=3.0))

    lx, ly = px + pw - 352, py + ph - 66

    def leg(y, color, txt):
        return line(lx, y, lx + 26, y, color=color, sw=3) + \
               text(lx + 34, y + 4, txt, size=13, color=color, anchor="start", bold=True)

    frags.append(leg(ly, NEG, "малий крок — повільно, зате тихо"))
    frags.append(leg(ly + 24, POS, "великий крок — швидко, зате тряско на піку"))
    frags.append(leg(ly + 48, "#b8860b", "адаптивний — здалеку широко, біля піка дрібно"))
    frags.append(text(px + pw / 2, py + ph + 52,
                      "крок задають від |ΔP|: далеко від MPP схил крутий (крок росте), біля піка пологий (крок гасне)",
                      size=13, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'adaptive-step.svg'), W, H, *frags,
                  title="Адаптивний крок: великий здалеку, дрібний біля піка")


# ── Фігура 7 (вставка): передача керма MPPT → CC → CV ───────────────────────
def fig_handoff():
    W, H = 940, 400
    yb = 155
    b1, w1, h1 = textbox(165, yb, "MPPT\nстеження за піком", size=14, bold=True,
                         fill="#eafaf1", stroke=FIELD, min_w=215)
    b2, w2, h2 = textbox(470, yb, "CC\nструмовий ліміт", size=14, bold=True,
                         fill="#fff8e1", stroke="#b8860b", min_w=200)
    b3, w3, h3 = textbox(775, yb, "CV\nнапруга повна", size=14, bold=True,
                         fill="#eaf0fd", stroke=NEG, min_w=200)
    frags = []
    frags.append(arrow(165 + w1 / 2 + 4, yb - 12, 470 - w2 / 2 - 6, yb - 12, color=INK, sw=2.2))
    frags.append(arrow(470 + w2 / 2 + 4, yb - 12, 775 - w3 / 2 - 6, yb - 12, color=INK, sw=2.2))
    frags.append(text((165 + 470) / 2, yb - 34, "I_бат уперся в ліміт", size=13, color=INK, bold=True))
    frags.append(text((470 + 775) / 2, yb - 34, "V_бат = V_повна", size=13, color=INK, bold=True))
    frags.append(b1); frags.append(b2); frags.append(b3)

    yr = yb + 78
    frags.append(line(775, yb + h3 / 2, 775, yr, color=MUTED, sw=2))
    frags.append(line(470, yb + h2 / 2, 470, yr, color=MUTED, sw=2))
    frags.append(line(775, yr, 165, yr, color=MUTED, sw=2))
    frags.append(arrow(165, yr, 165, yb + h1 / 2 + 2, color=MUTED, sw=2))
    frags.append(text((165 + 775) / 2, yr + 24,
                      "панель уже не тягне ліміт  •  V просіла нижче (V_повна − гістерезис)",
                      size=13, color=MUTED, anchor="middle"))
    frags.append(text(W / 2, yb + h1 / 2 + 128,
                      "кермо шпаруватістю віддає то P&O, то регулятор струму, то регулятор напруги — з гістерезисом на стиках",
                      size=13, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'mode-handoff.svg'), W, H, *frags,
                  title="Три режими одного контролера: хто зараз крутить шпаруватість")


# ── Фігура 8 (вставка hist): родовід стеження за MPP ────────────────────────
def fig_timeline():
    W, H = 1040, 470
    baseY = 250
    off = 100
    x0, x1 = 110, 880
    xs = [x0 + (x1 - x0) * i / 5 for i in range(6)]
    frags = []
    bx = (xs[0] + xs[1]) / 2  # розрив осі між 1840 і 1968 (велика прогалина)

    # базова вісь: короткий обрубок під першим вузлом, розрив, довга стрілка далі
    frags.append(line(xs[0] - 10, baseY, bx - 14, baseY, color=MUTED, sw=2.6))
    frags.append(arrow(bx + 14, baseY, x1 + 34, baseY, color=MUTED, sw=2.6))
    frags.append(line(bx - 9, baseY - 11, bx - 1, baseY + 11, color=MUTED, sw=2))
    frags.append(line(bx + 1, baseY - 11, bx + 9, baseY + 11, color=MUTED, sw=2))
    frags.append(text(x1 + 34, baseY + 26, "час", size=13, color=MUTED, anchor="end"))

    cards = [
        (xs[0], "above", "1840",       "Правило максимуму віддачі\n(Якобі, Нева)",       FILL,      MUTED,     MUTED),
        (xs[1], "below", "1968",       "Самопідлаштовний\nперетворювач · Бьорінгер",     "#eafaf1", FIELD,     INK),
        (xs[2], "above", "1970–80-ті", "P&O: сходження на горб\nна земних панелях",      FILL,      LINE,      INK),
        (xs[3], "below", "1985",       "«Перший комерційний»\nMPPT — претензія AERL",    "#fff8e1", "#b8860b", INK),
        (xs[4], "above", "1995",       "Приростова провідність\nХуссейн та ін. · Кіото", "#eaf0fd", NEG,       INK),
        (xs[5], "below", "2007",       "Огляд Есрама–Чепмена:\n19 методів",              FILL,      LINE,      INK),
    ]
    for (x, side, year, label, fill, stroke, color) in cards:
        cy = baseY - off if side == "above" else baseY + off
        box, w, h = textbox(x, cy, label, size=13, fill=fill, stroke=stroke,
                            color=color, min_w=200)
        if side == "above":
            frags.append(line(x, baseY - 6, x, cy + h / 2, color=stroke, sw=2))
            frags.append(text(x, cy - h / 2 - 12, year, size=18, color=stroke, bold=True))
        else:
            frags.append(line(x, baseY + 6, x, cy - h / 2, color=stroke, sw=2))
            frags.append(text(x, cy + h / 2 + 24, year, size=18, color=stroke, bold=True))
        frags.append(box)
        frags.append(dot(x, baseY, 6, fill=stroke))

    return render(os.path.join(IMG, 'timeline.svg'), W, H, *frags,
                  title="Родовід стеження за MPP: від правила на Неві до зоопарку методів")


# ── Вставка math-mpp-condition: однодіодна модель (звідки крива й горб) ──────
def fig_singlediode():
    W, H = 820, 440
    frags = []
    xL = 150
    ytop, ybot = 150, 330
    xbox = 660
    # силові рейки (+ згори, − знизу)
    frags.append(line(xL, ytop, xbox, ytop, color=INK, sw=2))
    frags.append(line(xL, ybot, xbox, ybot, color=INK, sw=2))
    # гілка джерела фотоструму
    xs = 210
    frags.append(line(xs, ytop, xs, 216, color=INK, sw=2))
    frags.append(line(xs, 264, xs, ybot, color=INK, sw=2))
    frags.append(circle(xs, 240, 24, fill=BG, stroke=INK, sw=2))
    frags.append(arrow(xs, 258, xs, 222, color=POS, sw=2.4))
    frags.append(text(xs - 36, 236, "Iph", size=15, color=POS, anchor="end", bold=True))
    frags.append(text(xs - 36, 256, "світло", size=12, color=MUTED, anchor="end"))
    # гілка внутрішнього діода (анод угорі, катод унизу)
    xd = 370
    frags.append(line(xd, ytop, xd, 194, color=INK, sw=2))
    frags.append(line(xd, 224, xd, ybot, color=INK, sw=2))
    frags.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s" '
                 'stroke="%s" stroke-width="2"/>' % (xd - 15, 194, xd + 15, 194, xd, 222, "#eaf0fd", INK))
    frags.append(line(xd - 17, 224, xd + 17, 224, color=INK, sw=2.6))  # смужка катода
    frags.append(text(xd + 28, 205, "внутрішній діод", size=13, color=INK, anchor="start"))
    frags.append(text(xd + 28, 226, "I₀·(e^(V/nV_T) − 1)", size=13, color=NEG, anchor="start"))
    # вихідний порт
    xo = 520
    frags.append(dot(xo, ytop, 5, fill=INK))
    frags.append(dot(xo, ybot, 5, fill=INK))
    frags.append(text(xo - 14, ytop - 8, "+", size=17, color=POS, anchor="end", bold=True))
    frags.append(text(xo - 14, ybot + 22, "−", size=17, color=NEG, anchor="end", bold=True))
    frags.append(line(xo + 22, ytop + 10, xo + 22, ybot - 10, color=MUTED, sw=1.4))
    frags.append(text(xo + 34, (ytop + ybot) / 2 + 5, "V", size=16, color=INK, anchor="start", bold=True))
    # стрілка вихідного струму на верхній рейці
    frags.append(arrow(430, ytop, 500, ytop, color=POS, sw=2.6))
    frags.append(text(465, ytop - 12, "I", size=16, color=POS, anchor="middle", bold=True))
    # блок навантаження на всю висоту праворуч
    frags.append(rect(xbox, ytop, 150, ybot - ytop, fill=FILL, stroke=LINE, sw=1.6))
    frags.append(mtext(xbox + 75, (ytop + ybot) / 2 - 6, ["перетворювач", "(навантаження)"],
                       size=14, color=INK, bold=True))
    # вузлові точки
    for xx in (xs, xd):
        frags.append(dot(xx, ytop, 4, fill=INK))
        frags.append(dot(xx, ybot, 4, fill=INK))
    frags.append(text(405, 400, "I = Iph − Iдіода : фотострум ділиться між внутрішнім діодом і виходом",
                      size=13, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'single-diode.svg'), W, H, *frags,
                  title="Однодіодна модель: джерело фотоструму паралельно з діодом")


# ── Вставка math-mpp-condition: умова MPP як геометрія (хорда/дотична) ───────
def fig_conductance():
    W, H = 820, 480
    px, py, pw, ph = 100, 70, 590, 320
    Voc, Isc, c = 1.0, 1.0, 0.11
    denom = 1 - math.exp(-Voc / c)

    def I_of(V):
        return Isc * (1 - math.exp((V - Voc) / c)) / denom

    def dIdV(V):
        return -(Isc / (c * denom)) * math.exp((V - Voc) / c)

    Vmp, _ = pv_peak(Voc, Isc, c)
    Imp = I_of(Vmp)
    xmax, ymax = 1.06, 1.14
    m = mapper(px, py, pw, ph, xmax, ymax)
    x0, y0 = m(0, 0)
    xm, ym = m(Vmp, Imp)

    frags = [axes(px, py, pw, ph, "напруга V", "струм I")]
    # прямокутник потужності на MPP
    frags.append(rect(x0, ym, xm - x0, y0 - ym, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=0))
    frags.append(text((x0 + xm) / 2, y0 - 16, "P = V·I  (площа)", size=13, color=FIELD, anchor="middle"))
    # крива ВАХ
    frags.append(polyline([m(V, I) for V, I in iv_points(Voc, Isc, c)], color=INK, sw=2.8))
    # хорда з початку координат
    frags.append(line(x0, y0, xm, ym, color=FIELD, sw=2.4))
    # дотична на MPP
    s = dIdV(Vmp)
    dx = 0.20
    frags.append(line(*m(Vmp - dx, Imp - s * dx), *m(Vmp + dx, Imp + s * dx), color=POS, sw=2.6))
    # напрямні й точки
    frags.append(line(xm, py, xm, y0, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(x0, ym, xm, ym, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(dot(xm, ym, 6, fill=INK))
    frags.append(dot(x0, y0, 4, fill=INK))
    frags.append(text(xm, ym - 14, "MPP", size=14, color=INK, anchor="middle", bold=True))
    frags.append(text(xm + 20, py + 12, "Vmp", size=12, color=MUTED, anchor="start"))
    frags.append(text(x0 - 8, ym - 6, "Imp", size=12, color=MUTED, anchor="end"))
    # підписи хорди й дотичної у вільних зонах
    frags.append(text(px + 118, py + 128, "хорда з 0:", size=13, color=FIELD, anchor="start", bold=True))
    frags.append(text(px + 118, py + 146, "нахил = I/V (статична)", size=12, color=FIELD, anchor="start"))
    frags.append(text(px + pw - 8, py + 30, "дотична: нахил = dI/dV", size=13, color=POS, anchor="end", bold=True))
    frags.append(text(px + pw - 8, py + 48, "(приростова провідність)", size=12, color=POS, anchor="end"))
    frags.append(text(px + pw / 2, py + ph + 56,
                      "на MPP нахил дотичної = −нахил хорди   ⇔   dI/dV = −I/V   ⇔   найбільший прямокутник",
                      size=14, color=INK, anchor="middle"))
    return render(os.path.join(IMG, 'conductance.svg'), W, H, *frags,
                  title="Умова MPP як геометрія: приростова провідність = −статична")


# ── Вставка math-mpp-condition: навантажувальні прямі й повзунок D ───────────
def fig_loadline():
    W, H = 820, 480
    px, py, pw, ph = 100, 70, 590, 320
    Voc, Isc, c = 1.0, 1.0, 0.11
    denom = 1 - math.exp(-Voc / c)

    def I_of(V):
        return Isc * (1 - math.exp((V - Voc) / c)) / denom

    Vmp, _ = pv_peak(Voc, Isc, c)
    xmax, ymax = 1.06, 1.14
    m = mapper(px, py, pw, ph, xmax, ymax)
    x0, y0 = m(0, 0)

    frags = [axes(px, py, pw, ph, "напруга V", "струм I")]
    frags.append(polyline([m(V, I) for V, I in iv_points(Voc, Isc, c)], color=INK, sw=2.8))

    pts = [(0.30, NEG, "R_in малий → біля Isc"),
           (Vmp, FIELD, "R_in = R_mpp → MPP (горб)"),
           (0.97, POS, "R_in великий → біля Voc")]
    for V0, col, _lbl in pts:
        I0v = I_of(V0)
        ext = 1.06
        Vx, Ix = min(V0 * ext, xmax), min(I0v * ext, ymax)
        frags.append(line(x0, y0, *m(Vx, Ix), color=col, sw=1.8, dash="6 4"))
        frags.append(dot(*m(V0, I0v), r=6, fill=col))
    # легенда у вільному верхньому-правому куті
    lx = px + pw - 8
    for i, (_V0, col, lbl) in enumerate(pts):
        frags.append(text(lx, py + 22 + i * 22, lbl, size=13, color=col, anchor="end", bold=True))
    # повзунок D під полем
    sy = py + ph + 40
    frags.append(line(px, sy, px + pw, sy, color=MUTED, sw=3))
    frags.append(text(px - 8, sy + 5, "D=0", size=12, color=MUTED, anchor="end"))
    frags.append(text(px + pw + 8, sy + 5, "D=1", size=12, color=MUTED, anchor="start"))
    frags.append(text(px + pw / 2, sy + 26,
                      "крутиш D → міняється R_in → навантажувальна пряма совгає робочу точку від Isc до Voc",
                      size=13, color=INK, anchor="middle"))
    return render(os.path.join(IMG, 'load-line.svg'), W, H, *frags,
                  title="Ручка: шпаруватість перетворює опір, а опір совгає робочу точку")


if __name__ == "__main__":
    fig_loop()
    fig_po_climb()
    fig_slope()
    fig_moving()
    fig_settle()
    fig_adaptive()
    fig_handoff()
    fig_timeline()
    fig_singlediode()
    fig_conductance()
    fig_loadline()
    print("OK: figures written to", IMG)
