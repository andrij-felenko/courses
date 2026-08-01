# -*- coding: utf-8 -*-
"""Фігури до теми «Відрив потоку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ─────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def smooth(pts, fill='none', stroke=INK, sw=2.4, dash=None):
    """Гладка крива (квадратичні сегменти) через список точок."""
    if len(pts) < 3:
        return polyline(pts, stroke, sw, dash)
    d = "M %.1f %.1f" % pts[0]
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += " Q %.1f %.1f %.1f %.1f" % (pts[i][0], pts[i][1], mx, my)
    d += " L %.1f %.1f" % pts[-1]
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)


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


def hatch_below(x0, x1, y, color=MUTED, dh=9, step=13):
    out = [line(x0, y, x1, y, color=INK, sw=2.4)]
    x = x0
    while x < x1:
        out.append(line(x, y, x - dh, y + dh, color=color, sw=1.2))
        x += step
    return "".join(out)


# ── Фігура 1: пагорб тиску як гірка потенціальної енергії ─────────────────────
def fig_pressure_hill():
    W, H = 940, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Пагорб тиску — гірка, яку долає лише запас руху ½·ρ·u²",
                  size=18, bold=True))

    xL, xR = 150, 812
    ybase = 448
    Hmax = 250.0                      # 250 px ↔ 100 Па

    def hy(t):                        # висота пагорба в точці t∈[0,1]
        return ybase - Hmax * (t ** 1.25)

    # заливка терену (пагорб)
    terr = [(xL, ybase)]
    tt = 0.0
    while tt <= 1.0001:
        terr.append((xL + tt * (xR - xL), hy(tt)))
        tt += 0.02
    terr.append((xR, ybase))
    f.append(path_fill(terr, "#f0ece2"))
    f.append(smooth([(xL + (i / 50.0) * (xR - xL), hy(i / 50.0)) for i in range(51)],
                    stroke="#a9895e", sw=2.6))

    # ліва вісь тиску
    f.append(varrow(xL, ybase + 6, xL, hy(1.0) - 30, color=INK, sw=1.7, head=10))
    f.append(text(xL - 40, hy(1.0) - 20, "тиск", size=13, italic=True, anchor="middle"))
    f.append(text(xL - 40, hy(1.0) - 4, "(висота)", size=10.5, color=MUTED, anchor="middle"))
    f.append(text(xL - 12, ybase + 4, "0", size=11.5, color=MUTED, anchor="end"))
    # позначка Δp на вершині
    f.append(line(xL, hy(1.0), xR, hy(1.0), color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(xL + 118, hy(1.0) - 12, "Δp ≈ 100 Па  (до корми)", size=12,
                  color="#8a6d3b", anchor="start", bold=True))

    # рівень, до якого дістає пристінна рідина (21.6 Па)
    t_stall = (21.6 / 100.0) ** (1.0 / 1.25)
    xs = xL + t_stall * (xR - xL)
    ys = hy(t_stall)
    f.append(line(xL, ys, xs, ys, color=NEG, sw=1.4, dash="4 4"))
    f.append(text(xL + 10, ys - 18, "21.6 Па", size=11.5, color=NEG, anchor="start", bold=True))

    # вісь відстані
    f.append(varrow(xL, ybase, xR + 20, ybase, color=INK, sw=1.5, head=9))
    f.append(text((xL + xR) / 2, ybase + 30, "вздовж корми тіла  →", size=12.5, color=INK, bold=True))

    # ── пристінна рідина: маленька куля, глухне й котиться назад ──
    f.append(circle(xs, ys - 13, 13, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(varrow(xs - 34, ys + 6, xs - 8, ys - 6, color=POS, sw=2.0, head=9))  # заходила знизу-зліва
    # дуга «назад»
    back = [(xs + 6, ys - 26), (xs + 30, ys - 40), (xs + 40, ys - 20), (xs + 26, ys + 2)]
    f.append(smooth(back, stroke=POS, sw=2.2, dash="2 3"))
    f.append(head_at(xs + 26, ys + 2, -14, 22, POS, 9))
    f.append(circle(xs, ys, 4.5, fill=POS, stroke=BG, sw=1.4))
    bx, bw, bh = textbox(xs + 150, ys - 74,
                         "пристінна рідина\n½·ρ·u² = 21.6 Па\nглухне → скочується назад",
                         size=11.5, pad=9, fill="#fdecea", stroke=POS, sw=1.4)
    f.append(bx)
    f.append(text(xs + 96, ys + 18, "точка відриву", size=11.5, color=POS, anchor="middle", bold=True))

    # ── вільний потік: велика куля перевалює вершину ──
    tf = 0.9
    xf, yf = xL + tf * (xR - xL), hy(tf) - 16
    f.append(circle(xf, yf, 17, fill="#eaf0fd", stroke=NEG, sw=2.4))
    f.append(varrow(xf - 40, yf - 40, xf - 12, yf - 14, color=NEG, sw=2.2, head=10))
    f.append(varrow(xf + 12, yf - 12, xf + 44, yf - 30, color=NEG, sw=2.2, head=10))
    bx2, bw2, bh2 = textbox(xf - 30, yf - 96,
                            "вільний потік\n½·ρ·u² = 540 Па\nдолає з запасом",
                            size=11.5, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.4)
    f.append(bx2)

    b, w, h = textbox(W / 2, H - 26,
                      "Однакова гірка тиску — різний «пальний»: у пристінної рідини руху замало, і вона зривається назад",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "pressure-hill.svg"), W, H, *f)


# ── Фігура 2: профіль швидкості вздовж несприятливого градієнта ───────────────
def fig_profile_progression():
    W, H = 1000, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Профіль швидкості коло стінки: нахил падає до нуля й міняє знак",
                  size=17.5, bold=True))

    wall_y = 372
    x0, x1 = 84, 936
    Hp = 150.0          # висота профілю (px)
    Us = 104.0          # масштаб швидкості (px на u/U=1)

    # umono-family: u(η) з u(0)=0, u(1)=1, нахил коло стінки = m
    def prof(m, e):
        return m * e + (3 - 2 * m) * e * e + (m - 2) * e ** 3

    stations = [
        (210, 2.0,  "приліплений",   "нахил > 0", NEG),
        (400, 0.9,  "гальмується",   "нахил малий", "#b5651d"),
        (585, 0.0,  "точка відриву", "нахил = 0", POS),
        (775, -1.2, "зворотна течія", "нахил < 0", POS),
    ]

    # стінка
    f.append(hatch_below(x0 - 4, x1, wall_y))
    f.append(text(x0 + 2, wall_y + 24, "стінка", size=11.5, color=MUTED, anchor="start"))

    # верхні стрілки: вільний потік і напрям наростання тиску
    f.append(varrow(150, 88, 300, 88, color=MUTED, sw=2.0, head=9))
    f.append(text(150, 74, "вільний потік  U →", size=12.5, color=INK, anchor="start", bold=True))
    f.append(varrow(560, 88, 780, 88, color="#8a6d3b", sw=2.2, head=10))
    f.append(text(670, 74, "тиск наростає →", size=12.5, color="#8a6d3b", anchor="middle", bold=True))

    # роздільна лінія течії (сходить зі стінки після відриву)
    sep_x = stations[2][0]
    div = [(x0, wall_y - 6), (sep_x - 120, wall_y - 7), (sep_x, wall_y - 9),
           (sep_x + 90, wall_y - 46), (sep_x + 190, wall_y - 92), (x1 - 10, wall_y - 120)]
    f.append(smooth(div, stroke=FIELD, sw=2.6))
    f.append(text(x1 - 8, wall_y - 130, "шар сходить зі стінки", size=11.5,
                  color=FIELD, anchor="end", bold=True))

    # застійна зона зі зворотним обертанням (після відриву)
    f.append(text(sep_x + 150, wall_y - 20, "застійна зона", size=11, color=MUTED, anchor="middle"))
    eddy = [(sep_x + 210, wall_y - 18), (sep_x + 150, wall_y - 8),
            (sep_x + 96, wall_y - 22), (sep_x + 140, wall_y - 40),
            (sep_x + 210, wall_y - 40)]
    f.append(smooth(eddy, stroke=POS, sw=1.8, dash="2 3"))
    f.append(head_at(sep_x + 96, wall_y - 22, -30, 8, POS, 8))

    # профілі на станціях
    for (xb, m, name, note, col) in stations:
        f.append(line(xb, wall_y, xb, wall_y - Hp - 6, color="#dfe3e8", sw=1.2))
        pts = []
        e = 0.0
        while e <= 1.0001:
            pts.append((xb + prof(m, e) * Us, wall_y - e * Hp))
            e += 0.03
        # стрілки швидкості
        for e in [0.12, 0.28, 0.46, 0.68, 0.9]:
            u = prof(m, e)
            y = wall_y - e * Hp
            if abs(u) > 0.02:
                f.append(varrow(xb, y, xb + u * Us, y, color=col, sw=1.8, head=8))
        f.append(smooth(pts, stroke=col, sw=3.0))
        # підпис станції
        f.append(text(xb, wall_y - Hp - 20, name, size=12.5, bold=True, color=col))
        f.append(text(xb, wall_y - Hp - 4, note, size=11, color=MUTED))

    # точка відриву — мітка на стінці
    f.append(circle(sep_x, wall_y, 6, fill=POS, stroke=BG, sw=1.6))
    f.append(text(sep_x, wall_y + 40, "τ = μ·(∂u/∂y) = 0", size=12.5, color=POS, bold=True))

    b, w, h = textbox(W / 2, H - 22,
                      "Де нахил швидкості коло стінки вперше стає нульовим — там потік і відривається",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "profile-progression.svg"), W, H, *f)


# ── Фігура 3: одна причина — три обличчя (тіло · крило · дифузор) ──────────────
def fig_universality():
    W, H = 1080, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Один механізм — три обличчя відриву", size=18, bold=True))

    def wake_shade(x, y, w, h):
        return rect(x, y, w, h, fill="#fbe4e0", stroke='none', sw=0, rx=0)

    def sep_dot(x, y):
        return circle(x, y, 5, fill=POS, stroke=BG, sw=1.5)

    # роздільники
    f.append(line(360, 70, 360, H - 70, color="#e3e6ea", sw=1.3, dash="4 5"))
    f.append(line(720, 70, 720, H - 70, color="#e3e6ea", sw=1.3, dash="4 5"))

    # ── Панель A: тупе тіло ──
    f.append(text(180, 74, "тупе тіло", size=14, bold=True, color=POS))
    f.append(text(180, 92, "широкий слід", size=11, color=MUTED))
    cxA, cyA, R = 150, 250, 40
    f.append(wake_shade(cxA, cyA - R - 4, 150, 2 * (R + 4)))
    f.append(text(cxA + 78, cyA - R - 12, "слід: низький тиск", size=10, color=POS, anchor="middle"))
    f.append(circle(cxA, cyA, R, fill="#fdecea", stroke=POS, sw=2.0))
    # лінії течії, що відриваються
    for h in (16, 44):
        for sg in (+1, -1):
            pts = [(50, cyA - sg * h)]
            xx = 60
            while xx <= cxA:
                d = R * R - (xx - cxA) ** 2
                s = math.sqrt(d) if d > 0 else 0.0
                pts.append((xx, cyA - sg * max(h, s + 8)))
                xx += 6
            # після відриву — не змикається (широкий слід)
            pts.append((cxA + 40, cyA - sg * (R + 6)))
            pts.append((cxA + 150, cyA - sg * (R + 4)))
            f.append(smooth(pts, stroke=NEG, sw=2.0))
    for sg in (+1, -1):
        f.append(sep_dot(cxA, cyA - sg * R))
    # зворотна течія
    f.append(varrow(cxA + 120, cyA + 16, cxA + 40, cyA + 8, color=POS, sw=1.6, head=8))
    f.append(text(cxA + 84, cyA + 30, "зворотна течія", size=9.5, color=POS, anchor="middle"))

    # ── Панель B: крило під великим кутом ──
    f.append(text(540, 74, "крило під великим кутом", size=14, bold=True, color=POS))
    f.append(text(540, 92, "звалювання (зрив із верху)", size=11, color=MUTED))
    # профіль (нахилений витягнутий каплеподібний), кут атаки
    ax, ay = 470, 268
    aoa = math.radians(20)
    ch = 150.0
    prof = []
    N = 40
    for i in range(N + 1):
        t = i / N
        thick = 26 * math.sin(math.pi * t) * (1 - 0.35 * t)   # товщина
        xc = t * ch
        prof.append((xc, -thick))
    for i in range(N, -1, -1):
        t = i / N
        thick = 26 * math.sin(math.pi * t) * (1 - 0.35 * t)
        xc = t * ch
        prof.append((xc, thick * 0.35))
    def rot(px, py):
        return (ax + px * math.cos(aoa) + py * math.sin(aoa),
                ay + px * math.sin(aoa) - py * math.cos(aoa))
    wing = [rot(px, py) for (px, py) in prof]
    f.append(path_fill(wing, "#eef1f4", stroke=INK, sw=1.8))
    # набігаючий потік
    f.append(varrow(400, ay + 24, 452, ay + 15, color=MUTED, sw=2.0, head=9))
    f.append(text(408, ay + 40, "α", size=13, italic=True, bold=True, color=INK))
    # відірваний потік над верхом (хвилясті лінії)
    f.append(wake_shade(ax + 20, ay - 96, 150, 74))
    sepx, sepy = rot(ch * 0.32, -20)
    f.append(sep_dot(sepx, sepy))
    turb = [(ax + 30, ay - 30), (ax + 70, ay - 62), (ax + 110, ay - 44),
            (ax + 150, ay - 74), (ax + 190, ay - 52)]
    f.append(smooth(turb, stroke=POS, sw=2.0))
    f.append(smooth([(x, y + 22) for (x, y) in turb], stroke=POS, sw=2.0, dash="3 3"))
    f.append(text(ax + 108, ay - 92, "потік відірвався", size=10.5, color=POS, anchor="middle", bold=True))
    # приліплений низ
    f.append(smooth([(ax - 6, ay + 30), (ax + 60, ay + 40), (ax + 130, ay + 40),
                     (ax + 190, ay + 34)], stroke=NEG, sw=2.0))

    # ── Панель C: дифузор ──
    f.append(text(900, 74, "дифузор", size=14, bold=True, color=POS))
    f.append(text(900, 92, "розтруб зриває потік зі стінок", size=11, color=MUTED))
    tx = 762                       # горло
    ty0, ty1 = 240, 262            # горло: вузьке
    ex0, ey0, ey1 = 1040, 168, 336  # вихід: широке
    # стінки
    f.append(polyline([(tx, ty0), (ex0, ey0)], color=INK, sw=2.4))
    f.append(polyline([(tx, ty1), (ex0, ey1)], color=INK, sw=2.4))
    f.append(text((tx + ex0) / 2, ey0 - 12, "тиск наростає →", size=10.5, color="#8a6d3b",
                  anchor="middle", bold=True))
    # струмина, що відривається від нижньої стінки
    jet = [(tx + 4, 251), (tx + 90, 258), (tx + 150, 268), (tx + 210, 272), (tx + 270, 270)]
    f.append(smooth(jet, stroke=NEG, sw=2.4))
    f.append(smooth([(x, y - 20) for (x, y) in jet], stroke=NEG, sw=2.0))
    # відрив від нижньої стінки → рециркуляція
    sdx, sdy = tx + 96, 300
    f.append(sep_dot(tx + 70, 285))
    f.append(wake_shade(tx + 96, 300, 150, 30))
    f.append(varrow(tx + 250, 316, tx + 120, 312, color=POS, sw=1.6, head=8))
    f.append(text(tx + 180, 300, "застій / зворотна течія", size=9.5, color=POS, anchor="middle"))
    # вхідні стрілки
    for yy in (247, 256):
        f.append(varrow(tx - 42, yy, tx - 6, yy, color=MUTED, sw=1.8, head=8))

    b, w, h = textbox(W / 2, H - 24,
                      "Слід за тілом, звалювання крила, зрив у дифузорі — скрізь потік іде вгору по тиску й зривається",
                      size=12.5, pad=10, fill="#f4f6f8", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "universality.svg"), W, H, *f)


# ══ Фігури до вставки «math-adverse-gradient» ════════════════════════════════

# ── Розв'язувач Фолкнера–Скан:  f‴ + f·f″ + β·(1 − f′²) = 0 ──────────────────
def _fs_solve(beta, h0, eta_max=9.0, dt=0.004):
    """Інтегрування RK4. Повертає список (η, f′, f″, f‴)."""
    def rhs(s):
        f, g, h = s
        return (g, h, -f * h - beta * (1.0 - g * g))
    s = (0.0, 0.0, h0)
    out = [(0.0, 0.0, h0, -beta)]
    eta = 0.0
    for _ in range(int(eta_max / dt)):
        k1 = rhs(s)
        k2 = rhs(tuple(s[j] + dt / 2 * k1[j] for j in range(3)))
        k3 = rhs(tuple(s[j] + dt / 2 * k2[j] for j in range(3)))
        k4 = rhs(tuple(s[j] + dt * k3[j] for j in range(3)))
        s = tuple(s[j] + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(3))
        eta += dt
        out.append((eta, s[1], s[2], -s[0] * s[2] - beta * (1.0 - s[1] * s[1])))
        if abs(s[1]) > 3.0:
            break
    return out


def _fs_profile(beta):
    """Стрільба по f″(0) до f′(∞)=1. Повертає (точки [(u/U, y/δ)], f″(0)·η99, перегин)."""
    lo, hi = 0.0, 2.0
    for _ in range(28):
        mid = (lo + hi) / 2
        if _fs_solve(beta, mid)[-1][1] > 1.0:
            hi = mid
        else:
            lo = mid
    h0 = (lo + hi) / 2
    o = _fs_solve(beta, h0)
    e99 = next(e for e, g, _h, _p in o if g >= 0.99)
    keep = [(g, e / e99) for e, g, _h, _p in o if e <= e99 * 1.02]
    pts = keep[::6] + [keep[-1]]          # проріджуємо — крива й так гладка
    infl = None
    for k in range(2, len(o)):
        if o[k - 1][3] > 0.0 >= o[k][3]:
            infl = (o[k][1], o[k][0] / e99)
            break
    return pts, h0 * e99, infl


# ── Фігура 4: знак градієнта тиску = знак кривини профілю коло стінки ────────
def fig_wall_curvature_sign():
    W, H = 1040, 650
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "μ·(∂²u/∂y²)₀ = dp/dx — градієнт тиску просто диктує кривину профілю на стінці",
                  size=17.5, bold=True))
    # спільна легенда пунктиру
    f.append(line(W / 2 - 196, 54, W / 2 - 160, 54, color=MUTED, sw=1.8, dash="6 5"))
    f.append(text(W / 2 - 152, 58, "— дотична до профілю на стінці (нахил τ_w ⁄ μ);  ○ — точка перегину",
                  size=12, color=MUTED, anchor="start"))

    PW, PH = 230.0, 320.0
    PY0 = 490.0
    panels = [
        (105.0, 0.5, NEG, "розгін:  dp/dx < 0",
         "u″(0) < 0\nкрива йде ЛІВОРУЧ від дотичної\nнахил найбільший на самій стінці"),
        (425.0, 0.0, MUTED, "рівний тиск:  dp/dx = 0",
         "u″(0) = 0  (і u‴(0) = 0)\nколо стінки профіль — пряма\nперегин сидить на самій стінці"),
        (745.0, -0.18, POS, "гальмування:  dp/dx > 0",
         "u″(0) > 0\nкрива йде ПРАВОРУЧ від дотичної\nнахил на стінці — найменший"),
    ]

    for (PX0, beta, col, head, note) in panels:
        pts, tg, infl = _fs_profile(beta)
        f.append(text(PX0 + PW / 2, 78, head, size=15, bold=True, color=col))

        def sx(u):
            return PX0 + u * PW

        def sy(t):
            return PY0 - t * PH

        # осі
        f.append(hatch_below(PX0 - 22, PX0 + PW + 26, PY0))
        f.append(varrow(PX0, PY0, PX0, PY0 - PH - 26, color=INK, sw=1.6, head=9))
        f.append(text(PX0 - 16, PY0 - PH - 24, "y", size=13, italic=True, anchor="middle"))
        f.append(varrow(PX0, PY0, PX0 + PW + 26, PY0, color=INK, sw=1.6, head=9))
        f.append(text(PX0 + PW + 20, PY0 + 26, "u ⁄ U", size=12, anchor="middle"))
        f.append(line(PX0 - 6, sy(1.0), PX0 + 6, sy(1.0), color=MUTED, sw=1.6))
        f.append(text(PX0 - 14, sy(1.0) + 5, "δ", size=12.5, color=MUTED, anchor="end"))

        # дотична на стінці (пунктир) — обрізана рамкою графіка
        t_end = min(1.02, 1.02 / tg) if tg > 0 else 1.02
        tx1, ty1 = sx(min(1.02, tg * t_end)), sy(t_end)
        f.append(line(sx(0), sy(0), tx1, ty1, color=MUTED, sw=1.8, dash="6 5"))

        # заливка між дотичною і кривою — куди саме вигинає градієнт
        band = [(sx(u), sy(t)) for (u, t) in pts if t <= t_end]
        if band:
            back = [(sx(min(1.02, tg * t)), sy(t)) for t in
                    [i / 40.0 * t_end for i in range(41)]][::-1]
            shade = "#eaf0fd" if beta > 0 else ("#fdecea" if beta < 0 else "#f0f0f0")
            f.append(path_fill(band + back, shade))

        # сам профіль
        f.append(polyline([(sx(u), sy(t)) for (u, t) in pts], color=col, sw=2.8))

        # точка перегину
        if infl:
            f.append(circle(sx(infl[0]), sy(infl[1]), 5.5, fill=BG, stroke=POS, sw=2.4))
            f.append(text(PX0 + 10, sy(infl[1]) - 12, "перегин u″=0", size=11,
                          color=POS, anchor="start", bold=True))
        elif beta == 0.0:
            f.append(circle(sx(0.0), sy(0.0), 5.5, fill=BG, stroke=INK, sw=2.4))

        f.append(fitbox(PX0 - 22, PY0 + 44, PW + 48, 72, note, size=11.5, pad=8,
                        fill="#fbfbfc", stroke=col, sw=1.3))

    b, w, h = textbox(W / 2, H - 40,
                      "Профілі Фолкнера–Скан. Сприятливий градієнт вигинає профіль до стінки, несприятливий — від неї,\n"
                      "і тоді кривина мусить десь усередині шару змінити знак: там і сидить точка перегину",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "wall-curvature-sign.svg"), W, H, *f)


# ── Фігура 5: нульове тертя сумісне лише з несприятливим градієнтом ──────────
def fig_separation_parabola():
    W, H = 940, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Профіль у точці, де тертя на стінці зникло: u(y) = (1∕2μ)·(dp/dx)·y²",
                  size=17.5, bold=True))

    PH = 250.0
    PY0 = 410.0
    HALF = 150.0                     # піврозмах по u

    def panel(cx, sign, col, head, note, ok):
        g = [text(cx, 82, head, size=15, bold=True, color=col)]
        g.append(hatch_below(cx - HALF - 26, cx + HALF + 26, PY0))
        # вісь u = 0
        g.append(varrow(cx, PY0, cx, PY0 - PH - 26, color=INK, sw=1.6, head=9))
        g.append(text(cx - 16, PY0 - PH - 24, "y", size=13, italic=True, anchor="middle"))
        g.append(line(cx - HALF - 10, PY0, cx + HALF + 10, PY0, color=INK, sw=1.6))
        g.append(text(cx + HALF + 4, PY0 + 26, "u", size=13, italic=True, anchor="middle"))
        g.append(text(cx + 9, PY0 + 26, "0", size=11.5, color=MUTED, anchor="start"))
        # парабола u = ± k·y²
        pts = []
        for i in range(61):
            t = i / 60.0
            pts.append((cx + sign * HALF * t * t, PY0 - PH * t))
        g.append(polyline(pts, color=col, sw=3.0))
        # дотична на стінці — сама стінка (нульовий нахил)
        g.append(line(cx - 4, PY0, cx + sign * (HALF + 14), PY0, color=col, sw=2.0, dash="6 5"))
        g.append(text(cx + sign * 84, PY0 - 16, "u′(0) = 0", size=12, color=col,
                      anchor="middle", bold=True))
        # значок «можна / не можна»
        if ok:
            g.append(circle(cx - HALF + 2, PY0 - PH + 4, 15, fill="#eef6ef", stroke=FIELD, sw=2.2))
            g.append(text(cx - HALF + 2, PY0 - PH + 10, "✓", size=20, color=FIELD, bold=True))
        else:
            g.append(circle(cx + HALF - 2, PY0 - PH + 4, 15, fill="#fdecea", stroke=POS, sw=2.2))
            g.append(text(cx + HALF - 2, PY0 - PH + 11, "✗", size=20, color=POS, bold=True))
        g.append(fitbox(cx - HALF - 26, PY0 + 46, 2 * HALF + 52, 62, note,
                        size=11.5, pad=8, fill="#fbfbfc", stroke=col, sw=1.3))
        return "".join(g)

    f.append(panel(258, +1, POS, "dp/dx > 0 — гальмування",
                   "u ≥ 0 одразу над стінкою:\nрідина ще повзе вперед —\nпрофіль несуперечливий", True))
    f.append(panel(682, -1, NEG, "dp/dx < 0 — розгін",
                   "u < 0 одразу над стінкою:\nзворотна течія мала б бути ДО того,\nяк тертя дійшло нуля — суперечність", False))

    b, w, h = textbox(W / 2, H - 38,
                      "Нахил на стінці зник, тож перший ненульовий член — квадратичний, і його знак — це знак dp/dx.\n"
                      "У прискорювальній течії нульове тертя просто не має несуперечливого профілю",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "separation-parabola.svg"), W, H, *f)


# ── Фігура 6: тертя падає до нуля як √(x_s − x) ──────────────────────────────
def fig_tau_sqrt_approach():
    W, H = 940, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Останні міліметри: τ_w ∝ √(x_s − x) — тертя приходить у нуль із вертикальною дотичною",
                  size=17.5, bold=True))

    X0, XS = 130.0, 640.0
    PY0, PHT = 396.0, 250.0

    # осі
    f.append(varrow(X0, PY0, X0, PY0 - PHT - 28, color=INK, sw=1.6, head=9))
    f.append(mtext(X0 - 46, PY0 - PHT - 22, ["τ_w", "(тертя)"], size=12, color=INK, anchor="middle"))
    f.append(varrow(X0, PY0, W - 90, PY0, color=INK, sw=1.6, head=9))
    f.append(text(W - 132, PY0 + 30, "x  вздовж стінки  →", size=12.5, bold=True, anchor="middle"))
    f.append(text(X0 - 12, PY0 + 5, "0", size=11.5, color=MUTED, anchor="end"))

    # зона, куди розв'язок не продовжується
    f.append(rect(XS, PY0 - PHT - 10, W - 90 - XS, PHT + 10, fill="#f6f0f0", stroke='none', sw=0, rx=0))
    f.append(line(XS, PY0 + 10, XS, PY0 - PHT - 20, color=POS, sw=1.8, dash="6 5"))
    f.append(text(XS, PY0 - PHT - 30, "x_s", size=14, color=POS, bold=True, anchor="middle"))
    f.append(mtext(XS + 106, PY0 - 148, ["розв'язок", "примежового шару", "не продовжується"],
                   size=12, color=POS, anchor="middle"))

    # крива √
    pts = []
    for i in range(121):
        t = i / 120.0
        x = X0 + t * (XS - X0)
        pts.append((x, PY0 - PHT * ((1.0 - t) ** 0.5)))
    f.append(polyline(pts, color=POS, sw=3.0))
    f.append(text(X0 + 118, PY0 - PHT + 6, "τ_w = C·√(x_s − x)", size=13.5, color=POS,
                  anchor="start", bold=True))

    # наївна пряма для порівняння
    f.append(line(X0, PY0 - PHT, XS, PY0, color=MUTED, sw=2.0, dash="5 5"))
    f.append(text(X0 + 210, PY0 - 66, "якби спадало рівномірно", size=11.5, color=MUTED, anchor="start"))

    # вертикальна дотична в кінці
    f.append(varrow(XS - 2, PY0 - 96, XS - 2, PY0 - 8, color=INK, sw=2.2, head=10))
    f.append(mtext(XS - 128, PY0 - 118, ["dτ_w/dx → −∞", "вертикальна дотична"],
                   size=12, color=INK, anchor="middle", bold=True))

    b, w, h = textbox(W / 2, H - 40,
                      "Квадратний корінь — особливість Ґольдштейна (1948): у самій точці відриву похідна тертя\n"
                      "стає нескінченною, і задане ззовні поле тиску вже не може вести шар далі",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "tau-sqrt-approach.svg"), W, H, *f)


# ── Фігура 7: марш λ(s) до порога −0.09 на двох різних тілах ────────────────
def _lam_howarth(xi):
    """λ(x/L) для гальмівної течії U = U₀·(1 − x/L) за формулою Твейтса."""
    t = (1.0 - xi) ** 6
    return -0.075 * (1.0 - t) / t


def _lam_cylinder(phi):
    """λ(φ) для циліндра з потенціальною швидкістю U = 2·U∞·sin φ."""
    if phi < 1e-6:
        return 0.075
    c = math.cos(phi)
    I = -c + (2.0 / 3.0) * c ** 3 - 0.2 * c ** 5 + (1.0 - 2.0 / 3.0 + 0.2)
    return 0.45 * c * I / math.sin(phi) ** 6


def fig_thwaites_march():
    W, H = 1010, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    LAM_TOP, LAM_BOT = 0.10, -0.13          # межі вертикальної осі
    PY0, PY1 = 96.0, 352.0                  # верх / низ поля графіка
    PW = 366.0

    def ymap(lam):
        return PY0 + (LAM_TOP - lam) / (LAM_TOP - LAM_BOT) * (PY1 - PY0)

    panels = [
        dict(x0=96.0, head="Гальмівна течія   U = U₀·(1 − x/L)",
             sub="по вертикалі λ, по горизонталі x/L",
             xmax=0.14, ticks=[(0.0, "0"), (0.05, "0.05"), (0.10, "0.10")],
             fn=lambda t: _lam_howarth(t), cross=0.1231, clabel="0.1231",
             note="Твейтс 0.1231  ·  точний розв'язок 0.1198  →  завищення на 2.8 %"),
        dict(x0=548.0, head="Циліндр   U = 2·U∞·sin φ",
             sub="по вертикалі λ, по горизонталі φ, градуси",
             xmax=115.0, ticks=[(0.0, "0"), (30.0, "30"), (60.0, "60"), (90.0, "90")],
             fn=lambda t: _lam_cylinder(math.radians(t)), cross=103.1, clabel="103.1°",
             note="Твейтс 103.1°  ·  дослід ≈ 80°  →  винна нев'язка крива на вході"),
    ]

    for p in panels:
        x0, xmax = p["x0"], p["xmax"]
        xm = lambda t: x0 + t / xmax * PW

        f.append(text(x0 + PW / 2, 52, p["head"], size=14.5, bold=True))
        f.append(text(x0 + PW / 2, 74, p["sub"], size=11.5, color=MUTED))
        f.append(rect(x0, PY0, PW, PY1 - PY0, fill="#fbfcfd", stroke="#c9ced6", sw=1.2, rx=4))

        # горизонтальні орієнтири
        f.append(line(x0, ymap(0.0), x0 + PW, ymap(0.0), color=MUTED, sw=1.3, dash="6 5"))
        f.append(line(x0, ymap(-0.09), x0 + PW, ymap(-0.09), color=POS, sw=1.8, dash="7 5"))

        # підписи вертикальної осі
        for lam, lab, col in ((0.075, "0.075", MUTED), (0.0, "0", MUTED), (-0.09, "−0.09", POS)):
            f.append(line(x0 - 6, ymap(lam), x0, ymap(lam), color=col, sw=1.3))
            f.append(text(x0 - 11, ymap(lam) + 4, lab, size=11.5, color=col, anchor="end",
                          bold=(lam == -0.09)))

        # крива λ(s), обрізана знизу межею поля
        pts = []
        for i in range(241):
            t = xmax * i / 240.0
            lam = p["fn"](t)
            if lam < LAM_BOT + 0.002:
                break
            pts.append((xm(t), ymap(min(lam, LAM_TOP))))
        f.append(polyline(pts, color=NEG, sw=3.0))

        # точка перетину порога + опускання на вісь
        cx = xm(p["cross"])
        f.append(line(cx, ymap(-0.09), cx, PY1, color=POS, sw=1.3, dash="4 4"))
        f.append(circle(cx, ymap(-0.09), 5.5, fill=POS, stroke=POS, sw=1.4))

        # підписи горизонтальної осі
        for tv, lab in p["ticks"]:
            f.append(line(xm(tv), PY1, xm(tv), PY1 + 6, color=MUTED, sw=1.3))
            f.append(text(xm(tv), PY1 + 21, lab, size=11.5, color=MUTED))
        f.append(text(cx, PY1 + 21, p["clabel"], size=11.5, color=POS, bold=True))

        b, w, h = textbox(x0 + PW / 2, 412, p["note"], size=12, pad=9,
                          fill="#f8f2f1", stroke=POS, sw=1.3)
        f.append(b)

    f.append(text(panels[0]["x0"] + 10, ymap(-0.09) - 11, "поріг відриву:  S(λ) = 0",
                  size=11.5, color=POS, anchor="start"))

    b, w, h = textbox(W / 2, H - 32,
                      "Одна процедура на будь-якому тілі: інтеграл ∫U⁵ds → θ² → λ → перший перетин −0.09",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "thwaites-march.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_pressure_hill(), fig_profile_progression(), fig_universality(),
          fig_wall_curvature_sign(), fig_separation_parabola(), fig_tau_sqrt_approach(),
          fig_thwaites_march()]
    print("written:")
    for p in ps:
        print("  ", p)
