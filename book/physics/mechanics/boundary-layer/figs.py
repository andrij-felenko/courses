# -*- coding: utf-8 -*-
"""Фігури до теми «Примежовий шар».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def hatch_below(x0, x1, y, n=None, color=MUTED, dh=9, step=13):
    """Штрихування «твердого» під горизонтальною стінкою."""
    out = [line(x0, y, x1, y, color=INK, sw=2.4)]
    x = x0
    while x < x1:
        out.append(line(x, y, x - dh, y + dh, color=color, sw=1.2))
        x += step
    return "".join(out)


# ── Фігура 1: профіль швидкості в примежовому шарі (ламінарний ↔ турбулентний) ─
def fig_velocity_profile():
    W, H = 880, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Профіль швидкості в примежовому шарі", size=18, bold=True))
    f.append(text(W / 2, 54, "від нуля на стінці (прилипання) до U на краю шару — увесь перепад у товщині δ",
                  size=12.5, color=MUTED))

    wall_y, top_y = 408, 118
    umax = 244
    etas = [0.10, 0.22, 0.35, 0.50, 0.66, 0.83, 1.0]

    def panel(ax, prof, col, tint, name, note):
        g = []
        # заливка області шару (за профілем)
        band = [(ax, wall_y)]
        tips = []
        for e in [i / 40.0 for i in range(41)]:
            y = wall_y - e * (wall_y - top_y)
            u = prof(e) * umax
            tips.append((ax + u, y))
        band += tips + [(ax, top_y)]
        g.append(path_fill(band, tint))
        # вісь y
        g.append(varrow(ax, wall_y + 4, ax, top_y - 34, color=INK, sw=1.7, head=10))
        g.append(text(ax - 14, top_y - 30, "y", size=13, italic=True, color=INK, anchor="middle"))
        # стінка з штрихуванням
        g.append(hatch_below(ax - 26, ax + umax + 52, wall_y))
        g.append(text(ax + umax + 30, wall_y + 26, "стінка", size=11.5, color=MUTED, anchor="middle"))
        # межа шару δ
        g.append(line(ax, top_y, ax + umax + 24, top_y, color=col, sw=1.5, dash="6 4"))
        g.append(text(ax + umax + 40, top_y + 5, "δ", size=15, italic=True, color=col, anchor="middle", bold=True))
        # стрілки швидкості
        for e in etas:
            y = wall_y - e * (wall_y - top_y)
            u = prof(e) * umax
            if u > 3:
                g.append(varrow(ax, y, ax + u, y, color=col, sw=2.0, head=9))
        # профіль-крива
        g.append(polyline([(ax, wall_y)] + tips, color=col, sw=3.0))
        # U на краю
        g.append(text(ax + umax + 6, top_y - 8, "U", size=16, italic=True, bold=True, color=INK, anchor="start"))
        g.append(text(ax + umax * 0.5, top_y - 46, name, size=13.5, bold=True, color=col, anchor="middle"))
        g.append(text(ax + umax * 0.5, top_y - 28, note, size=11.5, color=MUTED, anchor="middle"))
        # позначка дотичного напруження коло стінки
        g.append(text(ax + 6, wall_y - 12, "τ = μ·(du/dy)", size=12, color=INK, anchor="start", bold=True))
        return "".join(g)

    # ламінарний: пологий, увігнутий (sin)
    f.append(panel(112, lambda e: math.sin(math.pi / 2 * e), NEG, "#eef1fb",
                   "ламінарний", "пологий профіль"))
    # турбулентний: повніший, степеневий 1/7
    f.append(panel(520, lambda e: e ** (1.0 / 7.0), POS, "#fdecea",
                   "турбулентний", "повніший, крутіший коло стінки"))

    # підсумок унизу
    b, w, h = textbox(W / 2, H - 30,
                      "Що крутіший спад коло стінки, то більше тертя об поверхню",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "velocity-profile.svg"), W, H, *f)


# ── Фігура 2: ріст шару вздовж пластини (ламінарний → перехід → турбулентний) ──
def fig_plate_growth():
    W, H = 940, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Примежовий шар росте вздовж пластини", size=18, bold=True))

    x0, x1 = 100, 858            # ніс і хвіст пластини
    xtr = 415                    # точка переходу
    plate_y = 338

    kL = 34.0 / math.sqrt(xtr - x0)          # ламінарна δ ~ √x
    kT = 48.0 / (xtr - x0) ** 0.8            # турбулентна δ ~ x^0.8, помітно товща

    def dlam(x): return kL * math.sqrt(max(0.0, x - x0))
    def dtur(x): return kT * (x - x0) ** 0.8

    # заливки областей (між пластиною та огинальною δ)
    lam = [(x0, plate_y)]
    xx = x0
    while xx <= xtr:
        lam.append((xx, plate_y - dlam(xx))); xx += 6
    lam.append((xtr, plate_y))
    f.append(path_fill(lam, "#eef1fb"))

    tur = [(xtr, plate_y)]
    xx = xtr
    while xx <= x1:
        tur.append((xx, plate_y - dtur(xx))); xx += 6
    tur.append((x1, plate_y))
    f.append(path_fill(tur, "#fdecea"))

    # огинальні криві δ(x)
    f.append(polyline([(x, plate_y - dlam(x)) for x in range(x0, xtr + 1, 5)], color=NEG, sw=2.6))
    f.append(polyline([(x, plate_y - dtur(x)) for x in range(xtr, x1 + 1, 5)], color=POS, sw=2.6))

    # дрібні вихори в турбулентній зоні (натяк на перемішування)
    for (cx, cy, r) in [(560, 300, 8), (620, 292, 7), (690, 285, 9),
                        (760, 280, 8), (820, 276, 7), (600, 312, 6), (720, 305, 7)]:
        f.append(circle(cx, cy, r, fill="none", stroke=POS, sw=1.5))

    # пластина + штрихування знизу
    f.append(hatch_below(x0 - 8, x1 + 8, plate_y, color=MUTED, dh=10, step=15))

    # вільний потік згори
    fy = 108
    for xs in range(140, 840, 96):
        f.append(varrow(xs, fy, xs + 58, fy, color=MUTED, sw=2.0, head=9))
    f.append(text(x0 + 4, fy - 14, "вільний потік  U →", size=13, color=INK, anchor="start", bold=True))

    # точка переходу
    f.append(line(xtr, plate_y + 8, xtr, 150, color="#b5651d", sw=1.6, dash="6 4"))
    f.append(text(xtr, 142, "перехід", size=13, bold=True, color="#b5651d", anchor="middle"))
    f.append(text(xtr, 128, "Re_x ≈ 5×10⁵", size=11.5, color="#b5651d", anchor="middle"))

    # мітка δ (вертикальний двобічний вимір у турбулентній частині)
    xm = 800
    ytop = plate_y - dtur(xm)
    f.append(varrow(xm, plate_y - 2, xm, ytop + 2, color=INK, sw=1.6, head=8))
    f.append(varrow(xm, ytop + 2, xm, plate_y - 2, color=INK, sw=1.6, head=8))
    f.append(text(xm + 16, (plate_y + ytop) / 2 + 4, "δ", size=15, italic=True, bold=True, anchor="start"))

    # підписи зон під пластиною
    f.append(text((x0 + xtr) / 2, plate_y + 30, "ламінарний  (δ ~ √x)", size=13, bold=True, color=NEG))
    f.append(text((xtr + x1) / 2, plate_y + 30, "турбулентний  (товщий, більше руху коло стінки)",
                  size=13, bold=True, color=POS))
    f.append(text(x0 - 6, plate_y + 30, "ніс", size=11, color=MUTED, anchor="end"))

    b, w, h = textbox(W / 2, H - 26,
                      "Шар лишається тонкою плівкою проти довжини тіла, але біля стінки два режими поводяться різно",
                      size=12.5, pad=10, fill="#f4f6f8", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "plate-growth.svg"), W, H, *f)


# ── Фігура 3: відрив — обтічне тіло проти тупого ─────────────────────────────
def fig_separation():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Відрив примежового шару — звідки береться опір тиску", size=18, bold=True))

    cy = 280
    offs = [14, 40, 74]

    def stream(sil, xs, xe, h, sign, cx, separates):
        pts = []
        peak = h
        x = xs
        while x <= xe:
            s = sil(x)
            base = max(h, s + 9)
            if separates:
                if x <= cx:
                    base = max(h, s + 9)
                    peak = base
                else:
                    base = max(peak, h)     # позаду — не спадає: широкий слід
            pts.append((x, cy - sign * base))
            x += 5
        return pts

    # ── лівий панель: обтічне тіло (крапля) ──
    f.append(text(240, 78, "обтічне тіло", size=15, bold=True, color=FIELD))
    f.append(text(240, 98, "потік тримається · вузький слід · малий опір", size=11.5, color=MUTED))
    tx0, tx1, xm, Rt = 150, 356, 214, 46

    def sil_drop(x):
        if x < tx0 or x > tx1:
            return 0.0
        if x <= xm:
            return Rt * math.sqrt(max(0.0, 1 - ((xm - x) / (xm - tx0)) ** 2))
        return Rt * (tx1 - x) / (tx1 - xm)

    # тіло
    body = [(x, cy - sil_drop(x)) for x in range(tx0, tx1 + 1, 3)]
    body += [(x, cy + sil_drop(x)) for x in range(tx1, tx0 - 1, -3)]
    f.append(path_fill(body, "#eafaf1", stroke=FIELD, sw=2.0))
    # лінії течії
    for h in offs:
        for sg in (+1, -1):
            pts = stream(sil_drop, 66, 424, h, sg, xm, False)
            f.append(polyline(pts, color=NEG, sw=2.0))
            hx, hy = pts[-1]
            px, py = pts[-6]
            f.append(head_at(hx, hy, hx - px, hy - py, NEG, 9))
    f.append(text(240, cy + 150, "малий опір", size=13, bold=True, color=FIELD, anchor="middle"))

    # ── правий панель: тупе тіло (куля) ──
    f.append(text(700, 78, "тупе тіло", size=15, bold=True, color=POS))
    f.append(text(700, 98, "відрив · широкий слід · великий опір тиску", size=11.5, color=MUTED))
    cx, R = 660, 48

    def sil_ball(x):
        d = R * R - (x - cx) ** 2
        return math.sqrt(d) if d > 0 else 0.0

    # слід (низький тиск) — тінь позаду кулі
    f.append(rect(cx, cy - R - 6, 168, 2 * (R + 6), fill="#fbe4e0", stroke='none', sw=0, rx=0))
    f.append(text(cx + 92, cy - R - 16, "слід: низький тиск", size=11, color=POS, anchor="middle"))

    # тіло
    f.append(circle(cx, cy, R, fill="#fdecea", stroke=POS, sw=2.0))
    # лінії течії з відривом
    for h in offs:
        for sg in (+1, -1):
            pts = stream(sil_ball, 470, 828, h, sg, cx, True)
            f.append(polyline(pts, color=NEG, sw=2.0))
            hx, hy = pts[-1]
            px, py = pts[-6]
            f.append(head_at(hx, hy, hx - px, hy - py, NEG, 9))

    # точки відриву (верх і низ кулі)
    for sg in (+1, -1):
        f.append(circle(cx, cy - sg * R, 5, fill=POS, stroke=BG, sw=1.5))
    f.append(varrow(cx + 96, cy - R - 2, cx + 8, cy - R + 2, color=POS, sw=1.5, head=8))
    f.append(text(cx + 100, cy - R - 2, "точка відриву", size=11.5, color=POS, anchor="start", bold=True))

    # зворотна (реверсна) течія в сліді
    rev = [(cx + 150, cy + 26), (cx + 96, cy + 40), (cx + 60, cy + 20),
           (cx + 66, cy - 16), (cx + 104, cy - 34), (cx + 150, cy - 22)]
    f.append(polyline(rev, color=POS, sw=2.0, dash="2 3"))
    f.append(head_at(cx + 60, cy + 20, -36, -20, POS, 9))
    f.append(text(cx + 116, cy + 8, "зворотна течія", size=11, color=POS, anchor="middle"))

    # напрям наростання тиску
    f.append(varrow(cx - 30, cy + R + 30, cx + 40, cy + R + 30, color=MUTED, sw=1.8, head=9))
    f.append(text(cx + 6, cy + R + 46, "тиск наростає →", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(700, cy + 150, "великий опір тиску", size=13, bold=True, color=POS, anchor="middle"))

    # роздільник панелей
    f.append(line(W / 2, 70, W / 2, H - 70, color="#e3e6ea", sw=1.4, dash="4 5"))

    b, w, h = textbox(W / 2, H - 28,
                      "Ідеальна рідина відриву не знає — та сама крихта в'язкості, що зриває течію, і створює опір",
                      size=12.5, pad=10, fill="#f4f6f8", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "separation.svg"), W, H, *f)


# ── Розв'язок Блазіуса (RK4 + пристрілка) — дані для математичних фігур ───────
def _blasius(eta_max=6.6, h=0.01):
    """f''' + ½·f·f'' = 0, f(0)=f'(0)=0, f'(∞)=1. Повертає (таблиця, f''(0), h).
    Таблиця — рядки (η, f, f', f'')."""
    def deriv(f, fp, fpp):
        return (fp, fpp, -0.5 * f * fpp)

    def step(s, h):
        f, fp, fpp = s
        a = deriv(f, fp, fpp)
        b = deriv(f + h / 2 * a[0], fp + h / 2 * a[1], fpp + h / 2 * a[2])
        c = deriv(f + h / 2 * b[0], fp + h / 2 * b[1], fpp + h / 2 * b[2])
        d = deriv(f + h * c[0], fp + h * c[1], fpp + h * c[2])
        return tuple(v + h / 6 * (a_ + 2 * b_ + 2 * c_ + d_)
                     for v, a_, b_, c_, d_ in zip(s, a, b, c, d))

    n = int(eta_max / h)
    lo, hi = 0.1, 0.6                       # пристрілка по f''(0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        s = (0.0, 0.0, mid)
        for _ in range(n):
            s = step(s, h)
        if s[1] > 1.0:
            hi = mid
        else:
            lo = mid
    fpp0 = 0.5 * (lo + hi)
    tab, s, eta = [], (0.0, 0.0, fpp0), 0.0
    for _ in range(n + 1):
        tab.append((eta, s[0], s[1], s[2]))
        s = step(s, h)
        eta += h
    return tab, fpp0, h


def _interp(tab, h, e, col):
    """col: 1=f, 2=f', 3=f''. Лінійна інтерполяція таблиці за η=e."""
    if e <= 0:
        return tab[0][col]
    if e >= tab[-1][0]:
        return tab[-1][col]
    j = int(e / h)
    j2 = min(j + 1, len(tab) - 1)
    e0, e1 = tab[j][0], tab[j2][0]
    v0, v1 = tab[j][col], tab[j2][col]
    return v0 if e1 == e0 else v0 + (v1 - v0) * (e - e0) / (e1 - e0)


# ── Фігура 4: автомодельність — різні профілі збігаються в одну криву ─────────
def fig_blasius_similarity():
    W, H = 1000, 540
    tab, fpp0, h = _blasius(6.0, 0.01)
    def fp(e): return _interp(tab, h, e, 2)
    ETA = 5.8

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Автомодельність: різні профілі — одна крива", size=18, bold=True))
    f.append(text(W / 2, 52, "профілі на різних x збігаються, коли висоту міряти в η = y·√(U/(νx))",
                  size=12.5, color=MUTED))

    wall_y, top_y = 452, 152
    yH = wall_y - top_y
    cols = ["#2457d6", "#e08a1e", "#c0392b"]
    labs = ["x₁", "x₂", "x₃"]
    Hf = [0.42, 0.66, 0.94]

    # ── лівий панель: фізичні координати (u, y) ──
    lx0, uW = 108, 244
    f.append(text(lx0 + uW * 0.5, top_y - 44, "фізичні координати  (u, y)", size=13, bold=True))
    f.append(text(lx0 + uW * 0.5, top_y - 26, "три відстані x → три товщини δ", size=11.5, color=MUTED))
    f.append(varrow(lx0, wall_y + 4, lx0, top_y - 18, color=INK, sw=1.7, head=10))
    f.append(text(lx0 - 14, top_y - 12, "y", size=14, italic=True))
    f.append(hatch_below(lx0 - 22, lx0 + uW + 66, wall_y))
    f.append(text(lx0 + uW + 40, wall_y + 26, "стінка", size=11.5, color=MUTED))
    f.append(line(lx0 + uW, wall_y, lx0 + uW, top_y + 4, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text(lx0 + uW + 8, top_y + 4, "U", size=15, italic=True, bold=True, anchor="start"))
    f.append(text(lx0 + uW * 0.5, wall_y + 28, "u →", size=12.5, color=INK, bold=True))
    for k in range(3):
        Hs = Hf[k] * yH
        pts, e = [], 0.0
        while e <= ETA:
            pts.append((lx0 + fp(e) * uW, wall_y - (e / ETA) * Hs))
            e += 0.08
        f.append(polyline(pts, color=cols[k], sw=2.6))
        f.append(text(pts[-1][0] + 9, pts[-1][1] + 4, labs[k], size=13, bold=True,
                      color=cols[k], anchor="start"))

    # ── стрілка-перетворення ──
    f.append(varrow(430, 306, 590, 306, color=INK, sw=2.2, head=13))
    f.append(text(510, 280, "η = y·√(U/(νx))", size=13, bold=True))
    f.append(text(510, 298, "u/U = f′(η)", size=12, color=MUTED))

    # ── правий панель: змінна подібності η ──
    rx0, uW2 = 604, 244
    f.append(text(rx0 + uW2 * 0.5, top_y - 44, "змінна подібності  η", size=13, bold=True))
    f.append(text(rx0 + uW2 * 0.5, top_y - 26, "усі станції — одна крива f′(η)", size=11.5, color=MUTED))
    f.append(varrow(rx0, wall_y + 4, rx0, top_y - 18, color=INK, sw=1.7, head=10))
    f.append(text(rx0 - 16, top_y - 12, "η", size=15, italic=True))
    f.append(varrow(rx0 - 4, wall_y, rx0 + uW2 + 24, wall_y, color=INK, sw=1.7, head=10))
    f.append(text(rx0 + uW2 + 22, wall_y + 24, "u/U", size=13, italic=True))
    f.append(text(rx0, wall_y + 24, "0", size=11.5, color=MUTED))
    f.append(text(rx0 + uW2, wall_y + 24, "1", size=11.5, color=MUTED))
    f.append(line(rx0 + uW2, wall_y, rx0 + uW2, top_y + 4, color=MUTED, sw=1.3, dash="5 4"))
    pts, e = [], 0.0
    while e <= ETA:
        pts.append((rx0 + fp(e) * uW2, wall_y - (e / ETA) * yH))
        e += 0.05
    f.append(polyline(pts, color=INK, sw=3.2))
    for k, e in enumerate([1.6, 3.0, 4.3]):
        f.append(circle(rx0 + fp(e) * uW2, wall_y - (e / ETA) * yH, 6, fill=cols[k], stroke=BG, sw=1.6))
    y5 = wall_y - (5.0 / ETA) * yH
    f.append(line(rx0, y5, rx0 + fp(5.0) * uW2, y5, color=FIELD, sw=1.5, dash="6 4"))
    f.append(text(rx0 + fp(5.0) * uW2 + 10, y5 - 5, "η ≈ 5", size=12.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(rx0 + fp(5.0) * uW2 + 10, y5 + 12, "u/U = 0.992", size=11, color=FIELD, anchor="start"))

    b, w, hh = textbox(W / 2, H - 26,
                       "Товщина δ росте як √(νx/U), але ФОРМА профілю однакова на кожному x",
                       size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "blasius-similarity.svg"), W, H, *f)


# ── Фігура 5: функції Блазіуса — звідки беруться числа ───────────────────────
def fig_blasius_functions():
    W, H = 1000, 560
    tab, fpp0, h = _blasius(6.6, 0.01)
    def fval(e): return _interp(tab, h, e, 1)
    def fp(e):   return _interp(tab, h, e, 2)
    def fpp(e):  return _interp(tab, h, e, 3)

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Функції Блазіуса: звідки беруться числа", size=18, bold=True))

    px0, px1 = 92, 700
    EMAX = 6.5
    sx = (px1 - px0) / EMAX
    vy0, vtop = 460, 96
    VMAX = 1.08
    sv = (vy0 - vtop) / VMAX
    def X(e): return px0 + e * sx
    def Y(v): return vy0 - v * sv

    # осі
    f.append(varrow(px0, vy0, px1 + 26, vy0, color=INK, sw=1.7, head=10))
    f.append(text(px1 + 26, vy0 + 24, "η", size=15, italic=True))
    f.append(varrow(px0, vy0, px0, vtop - 6, color=INK, sw=1.7, head=10))
    for e in range(1, 7):
        f.append(line(X(e), vy0, X(e), vy0 + 5, color=INK, sw=1.4))
        f.append(text(X(e), vy0 + 20, str(e), size=11.5, color=MUTED))
    for v in [0.5, 1.0]:
        f.append(line(px0 - 5, Y(v), px0, Y(v), color=INK, sw=1.4))
        f.append(text(px0 - 12, Y(v) + 4, ("%.1f" % v), size=11.5, color=MUTED, anchor="end"))

    # площа витіснення (між f'=1 і f')
    band = [(X(i * 0.05), Y(fp(i * 0.05))) for i in range(int(EMAX / 0.05) + 1)]
    band += [(X(EMAX), Y(1.0)), (X(0), Y(1.0))]
    f.append(path_fill(band, "#eaf0fb"))

    # асимптота f'→1 (лише праворуч, щоб не лізти під рамку)
    f.append(line(X(0.7), Y(1.0), px1, Y(1.0), color=MUTED, sw=1.3, dash="6 4"))
    f.append(text(px1 - 6, Y(1.0) - 9, "f′ → 1   (u → U)", size=12, color=MUTED, anchor="end", bold=True))

    # криві
    def curve(g, col, sw, dash=None):
        pts = [(X(i * 0.04), Y(g(i * 0.04))) for i in range(int(EMAX / 0.04) + 1)]
        return polyline(pts, color=col, sw=sw, dash=dash)
    f.append(curve(lambda e: fval(e) / 5.0, MUTED, 2.0, dash="5 4"))
    f.append(curve(lambda e: fpp(e), POS, 2.8))
    f.append(curve(lambda e: fp(e), NEG, 3.3))

    # мітка витіснення в смузі
    f.append(text(X(2.55), Y(1.0) + 22, "площа = δ*/√(νx/U) = 1.72", size=11.5,
                  color="#3a5bbf", anchor="start"))

    # маркер η=5 (край шару)
    f.append(line(X(5), vy0, X(5), Y(fp(5)), color=FIELD, sw=1.4, dash="5 4"))
    f.append(circle(X(5), Y(fp(5)), 6, fill=FIELD, stroke=BG, sw=1.6))
    f.append(text(X(5) + 12, Y(fp(5)) - 24, "η ≈ 5 → u/U = 0.992", size=12.5, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(X(5) + 12, Y(fp(5)) - 8, "δ ≈ 5·x/√Re_x", size=11.5, color=FIELD, anchor="start"))

    # маркер f''(0)=0.332 + рамка у вільному верхньо-лівому куті
    f.append(circle(X(0), Y(fpp0), 6.5, fill=POS, stroke=BG, sw=1.6))
    f.append(line(X(0.06), Y(fpp0), 250, 172, color=POS, sw=1.2, dash="3 3"))
    f.append(fitbox(120, 110, 200, 62,
                    "f″(0) = 0.332  (нахил коло стінки)\n→ C_f = 0.664/√Re_x  (тертя)",
                    size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.4))

    # легенда праворуч (вільне поле)
    lx = 748
    ly = 250
    f.append(rect(lx, ly, 226, 118, fill="#fbfcfd", stroke=FIELD, sw=1.2, rx=8))
    rows = [("f′(η) = u/U  (профіль)", NEG, None),
            ("f″(η)  (напруження зсуву)", POS, None),
            ("f(η)/5  (функція течії)", MUTED, "5 4")]
    for i, (t, c, d) in enumerate(rows):
        yy = ly + 26 + i * 30
        f.append(line(lx + 14, yy, lx + 46, yy, color=c, sw=3.0, dash=d))
        f.append(text(lx + 54, yy + 4, t, size=11.5, color=INK, anchor="start"))

    b, w, hh = textbox(W / 2, H - 24,
                       "Нахил f″(0)=0.332 → тертя стінки · площа під (1−f′) → витіснення 1.72 · f′ виходить на 1 при η≈5",
                       size=12, pad=10, fill="#f4f6f8", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "blasius-functions.svg"), W, H, *f)


# ── локальний RK4-інтегратор для фігури пристрілки (повертає траєкторію f′(η)) ─
def _traj(fpp0, emax=7.0, h=0.02):
    def rhs(s):
        ff, fp, fpp = s
        return (fp, fpp, -0.5 * ff * fpp)

    def step(s):
        a = rhs(s)
        b = rhs(tuple(v + h / 2 * a_ for v, a_ in zip(s, a)))
        c = rhs(tuple(v + h / 2 * b_ for v, b_ in zip(s, b)))
        d = rhs(tuple(v + h * c_ for v, c_ in zip(s, c)))
        return tuple(v + h / 6 * (a_ + 2 * b_ + 2 * c_ + d_)
                     for v, a_, b_, c_, d_ in zip(s, a, b, c, d))

    s, e, out = (0.0, 0.0, fpp0), 0.0, [(0.0, 0.0)]
    while e < emax:
        s = step(s); e += h
        out.append((e, s[1]))
    return out


# ── Фігура 6: метод пристрілки для рівняння Блазіуса ──────────────────────────
def fig_shooting_method():
    W, H = 1080, 566
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Метод пристрілки: вгадуй f″(0), поки f′ далеко не сяде на 1",
                  size=18, bold=True))

    # ── лівий панель: пробні траєкторії f′(η) ──
    lx0, lx1 = 92, 512
    ly0, lyt = 480, 120
    EMAX, VMAX = 7.0, 1.34
    def X(e): return lx0 + e * (lx1 - lx0) / EMAX
    def Y(v): return ly0 - v * (ly0 - lyt) / VMAX
    f.append(varrow(lx0, ly0, lx1 + 20, ly0, color=INK, sw=1.7, head=10))
    f.append(text(lx1 + 18, ly0 + 22, "η", size=15, italic=True))
    f.append(varrow(lx0, ly0, lx0, lyt - 6, color=INK, sw=1.7, head=10))
    f.append(text(lx0 - 16, lyt - 2, "f′", size=15, italic=True))
    for e in range(1, 8):
        f.append(line(X(e), ly0, X(e), ly0 + 5, color=INK, sw=1.3))
        f.append(text(X(e), ly0 + 20, str(e), size=11, color=MUTED))
    for v in [0.5, 1.0]:
        f.append(line(lx0 - 5, Y(v), lx0, Y(v), color=INK, sw=1.3))
        f.append(text(lx0 - 12, Y(v) + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    # ціль f′=1
    f.append(line(X(0), Y(1.0), X(EMAX), Y(1.0), color=FIELD, sw=1.5, dash="7 5"))
    f.append(text(X(1.15), Y(1.0) - 9, "ціль:  f′(∞) = 1", size=12, color=FIELD,
                  anchor="start", bold=True))
    # пробні траєкторії
    trials = [(0.20, NEG, "6 4", "недоліт · s = 0.20"),
              (0.33206, INK, None, "влучив · s = 0.332"),
              (0.46, POS, "6 4", "переліт · s = 0.46")]
    for (s0, col, dsh, lab) in trials:
        t = _traj(s0, EMAX, 0.02)
        pts = [(X(e), Y(min(v, VMAX))) for (e, v) in t]
        f.append(polyline(pts, color=col, sw=3.2 if dsh is None else 2.4, dash=dsh))
        ex, ey = pts[-1]
        f.append(text(ex + 10, ey + 4, lab, size=11.5, color=col,
                      anchor="start", bold=(dsh is None)))
    f.append(circle(X(0), Y(0), 4, fill=INK, stroke=BG, sw=1.2))
    f.append(text(X(0.2), Y(0.14), "нахил коло стінки = f″(0) = s  (наш здогад)",
                  size=11.5, color=INK, anchor="start"))

    # ── правий панель: функція пристрілки F(s) = f′(η_max) − 1 ──
    rx0, rx1 = 700, 1044
    ry0, ryt = 480, 152
    S0, S1, FLO, FHI = 0.15, 0.50, -0.45, 0.37
    def Xs(s): return rx0 + (s - S0) * (rx1 - rx0) / (S1 - S0)
    def Yf(v): return ry0 - (v - FLO) * (ry0 - ryt) / (FHI - FLO)
    f.append(text((rx0 + rx1) / 2, ryt - 22, "функція пристрілки  F(s) = f′(η_max) − 1",
                  size=13, bold=True))
    y0 = Yf(0.0)
    f.append(varrow(rx0, y0, rx1 + 18, y0, color=INK, sw=1.5, head=9))
    f.append(text(rx1 + 16, y0 + 20, "s", size=14, italic=True))
    f.append(varrow(rx0, ry0, rx0, ryt - 6, color=INK, sw=1.5, head=9))
    f.append(text(rx0 - 12, ryt - 2, "F", size=14, italic=True))
    f.append(text(rx0 - 8, y0 - 6, "0", size=11, color=MUTED, anchor="end"))
    for s in [0.2, 0.3, 0.4, 0.5]:
        f.append(line(Xs(s), y0, Xs(s), y0 + 5, color=INK, sw=1.2))
        f.append(text(Xs(s), y0 + 20, "%.1f" % s, size=10.5, color=MUTED))
    pts, ss = [], S0
    while ss <= S1 + 1e-9:
        v = _traj(ss, 7.0, 0.02)[-1][1] - 1.0
        pts.append((Xs(ss), Yf(v))); ss += 0.01
    f.append(polyline(pts, color="#7a3fb0", sw=3.0))
    f.append(circle(Xs(0.33206), Yf(0.0), 6.5, fill=FIELD, stroke=BG, sw=1.7))
    f.append(line(Xs(0.33206), Yf(0.0), Xs(0.33206), ry0, color=FIELD, sw=1.3, dash="5 4"))
    f.append(text(Xs(0.33206), ry0 + 20, "корінь  s* = 0.332", size=12, bold=True, color=FIELD))
    f.append(text(Xs(0.375), Yf(-0.30), "F монотонна за s —", size=11, color=MUTED, anchor="start"))
    f.append(text(Xs(0.375), Yf(-0.355), "бісекція завжди збігається", size=11, color=MUTED, anchor="start"))

    b, w, hh = textbox(W / 2, H - 26,
                       "Крайова задача (умови на двох кінцях) стає початковою: підбором f″(0) заганяємо f′ на далекому краю в одиницю",
                       size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "shooting-method.svg"), W, H, *f)


# ── Фігура 7: опір поверхневого тертя vs Re (ламінар / турбулент / змішаний) ───
def fig_drag_vs_re():
    import math as _m
    W, H = 1000, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Опір тертя пластини: ламінарний, турбулентний і змішаний",
                  size=18, bold=True))
    f.append(text(W / 2, 52, "повний коефіцієнт тертя C_f у залежності від Re_L (обидві осі логарифмічні)",
                  size=12.5, color=MUTED))

    px0, px1 = 104, 812
    py0, pyt = 470, 108
    LX0, LX1 = 4.0, 9.0            # log10(Re)
    LY0, LY1 = -4.3, -1.75        # log10(Cf)  (низ, верх)
    def X(lre): return px0 + (lre - LX0) * (px1 - px0) / (LX1 - LX0)
    def Y(lcf): return py0 - (lcf - LY0) * (py0 - pyt) / (LY1 - LY0)
    def XR(Re): return X(_m.log10(Re))
    def YC(Cf): return Y(_m.log10(Cf))

    # смуга переходу
    f.append(rect(XR(1e5), pyt, XR(3e6) - XR(1e5), py0 - pyt,
                  fill="#fff6e9", stroke='none', sw=0, rx=0))
    f.append(text((XR(1e5) + XR(3e6)) / 2, pyt + 16, "смуга переходу", size=11,
                  color="#b5651d"))
    f.append(text((XR(1e5) + XR(3e6)) / 2, pyt + 31, "Re_x ≈ 3×10⁵…3×10⁶", size=10, color="#b5651d"))

    # осі + сітка декад
    f.append(varrow(px0, py0, px1 + 24, py0, color=INK, sw=1.7, head=10))
    f.append(text(px1 + 22, py0 + 24, "Re_L", size=13, italic=True))
    f.append(varrow(px0, py0, px0, pyt - 6, color=INK, sw=1.7, head=10))
    f.append(text(px0 - 22, pyt - 2, "C_f", size=13, italic=True))
    for k in range(int(LX0), int(LX1) + 1):
        f.append(line(X(k), py0, X(k), pyt, color="#eef0f3", sw=1.0))
        f.append(line(X(k), py0, X(k), py0 + 5, color=INK, sw=1.3))
        f.append(text(X(k), py0 + 20, "10%s" % _sup(k), size=11, color=MUTED))
    for lc in [-2, -3, -4]:
        f.append(line(px0, Y(lc), px1, Y(lc), color="#eef0f3", sw=1.0))
        f.append(line(px0 - 5, Y(lc), px0, Y(lc), color=INK, sw=1.3))
        f.append(text(px0 - 10, Y(lc) + 4, "10%s" % _sup(lc), size=11, color=MUTED, anchor="end"))

    def curve(fn, re_a, re_b, col, sw, dash=None):
        pts, n = [], 90
        for i in range(n + 1):
            Re = 10 ** (_m.log10(re_a) + (_m.log10(re_b) - _m.log10(re_a)) * i / n)
            pts.append((XR(Re), YC(fn(Re))))
        return polyline(pts, color=col, sw=sw, dash=dash)

    Cf_lam = lambda Re: 1.328 / _m.sqrt(Re)
    Cf_turb = lambda Re: 0.074 / Re ** 0.2
    Cf_mix = lambda Re: 0.074 / Re ** 0.2 - 1742.0 / Re

    # ламінарний: суцільний до 5×10⁵, далі пунктир (гіпотетичне продовження)
    f.append(curve(Cf_lam, 1e4, 5e5, NEG, 3.0))
    f.append(curve(Cf_lam, 5e5, 1e9, NEG, 1.8, dash="4 5"))
    # турбулентний від переднього краю
    f.append(curve(Cf_turb, 3e5, 1e9, POS, 3.0))
    f.append(curve(Cf_turb, 1e5, 3e5, POS, 1.8, dash="4 5"))
    # змішаний (ламінарний ніс + турбулент)
    f.append(curve(Cf_mix, 5e5, 1e9, FIELD, 3.0))

    # підписи кривих
    f.append(text(XR(2e4) + 6, YC(Cf_lam(2e4)) - 10, "ламінарний", size=12, color=NEG,
                  anchor="start", bold=True))
    f.append(text(XR(2e4) + 6, YC(Cf_lam(2e4)) + 6, "1.328/√Re", size=11, color=NEG, anchor="start"))
    f.append(text(XR(4e8), YC(Cf_turb(4e8)) - 12, "турбулентний  0.074/Re⁰·²", size=12,
                  color=POS, anchor="middle", bold=True))
    f.append(text(XR(6e7), YC(Cf_mix(6e7)) + 20, "змішаний  0.074/Re⁰·² − 1742/Re", size=12,
                  color=FIELD, anchor="middle", bold=True))

    # робоча точка Re_L = 4×10⁶
    Re0, Cf0 = 4e6, Cf_mix(4e6)
    f.append(circle(XR(Re0), YC(Cf0), 7, fill=INK, stroke=BG, sw=1.8))
    f.append(line(XR(Re0), YC(Cf0), XR(Re0), py0, color=INK, sw=1.2, dash="4 4"))
    bb = fitbox(XR(Re0) - 250, YC(Cf0) - 96, 236, 70,
                "наша пластина 2 м · 30 м/с\nRe_L = 4×10⁶ → C_f ≈ 0.0031\nтертя ≈ 6.7 Н (обидві сторони)",
                size=11.5, pad=8, fill="#f4f6f8", stroke=INK, sw=1.3)
    f.append(bb)
    f.append(line(XR(Re0) - 14, YC(Cf0) - 26, XR(Re0) - 2, YC(Cf0) - 4, color=INK, sw=1.1))

    b, w, hh = textbox(W / 2, H - 26,
                       "За великих Re турбулентний шар тре в рази дужче за ламінарний — і реальна пластина живе тут",
                       size=12.5, pad=10, fill="#f4f6f8", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "drag-vs-re.svg"), W, H, *f)


def _sup(n):
    m = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
         "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(m[c] for c in str(n))


if __name__ == "__main__":
    ps = [fig_velocity_profile(), fig_plate_growth(), fig_separation(),
          fig_blasius_similarity(), fig_blasius_functions(),
          fig_shooting_method(), fig_drag_vs_re()]
    print("written:")
    for p in ps:
        print("  ", p)
