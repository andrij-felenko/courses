# -*- coding: utf-8 -*-
"""Фігури до теми «Вільне падіння».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GRAV = "#2457d6"   # тяжіння / g — холодне синє
VEL  = "#c0392b"   # швидкість / рух — гаряче червоне


def ball(cx, cy, r=10):
    return circle(cx, cy, r, fill="#fef6e7", stroke=VEL, sw=2)


def ground(x1, x2, y, n=8):
    out = line(x1, x2 * 0 + x1, x2, y, color=LINE, sw=2) if False else line(x1, y, x2, y, color=LINE, sw=2)
    step = (x2 - x1) / n
    for i in range(n):
        gx = x1 + i * step
        out += line(gx, y, gx - 7, y + 8, color=MUTED, sw=1.1)
    return out


# ── Фігура 1: «вільне» — про сили, а не про напрямок ────────────────────────
def fig_what_is_free_fall():
    W, H = 900, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "«Вільне падіння» — про сили, а не про напрямок руху", size=16, bold=True))
    for dx in (305, 595):
        f.append(line(dx, 56, dx, 330, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── А: просто падає ──
    cxA = 160
    f.append(text(cxA, 78, "Падає з висоти", size=14, bold=True))
    f.append(line(cxA, 100, cxA, 300, color=MUTED, sw=1.1, dash="3,5"))
    f.append(ball(cxA, 175))
    # швидкість униз
    f.append(arrow(cxA, 190, cxA, 250, color=VEL, sw=3))
    f.append(text(cxA + 16, 228, "v", size=14, bold=True, color=VEL, anchor="start"))
    # g униз (збоку)
    f.append(arrow(cxA - 60, 150, cxA - 60, 210, color=GRAV, sw=2.6))
    f.append(text(cxA - 72, 184, "g", size=14, bold=True, color=GRAV, anchor="end"))
    f.append(ground(cxA - 80, cxA + 80, 300, n=7))
    f.append(text(cxA, 322, "рух і g — обидва вниз", size=11.5, color=MUTED))

    # ── B: підкинутий угору ──
    cxB = 450
    f.append(text(cxB, 78, "Підкинутий угору", size=14, bold=True))
    f.append(line(cxB, 100, cxB, 300, color=MUTED, sw=1.1, dash="3,5"))
    f.append(ball(cxB, 200))
    # швидкість УГОРУ (ще летить вгору)
    f.append(arrow(cxB, 190, cxB, 130, color=VEL, sw=3))
    f.append(text(cxB + 16, 150, "v", size=14, bold=True, color=VEL, anchor="start"))
    # g УНИЗ
    f.append(arrow(cxB - 60, 175, cxB - 60, 235, color=GRAV, sw=2.6))
    f.append(text(cxB - 72, 210, "g", size=14, bold=True, color=GRAV, anchor="end"))
    f.append(ground(cxB - 80, cxB + 80, 300, n=7))
    f.append(text(cxB, 322, "рух угору, а g усе одно вниз", size=11.5, color=MUTED))

    # ── C: кинутий під кутом ──
    cxC = 745
    f.append(text(cxC, 78, "Кинутий під кутом", size=14, bold=True))
    # параболічна дуга
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" '
             'stroke-width="1.3" stroke-dasharray="3,5"/>' % (660, 290, 745, 96, 830, 290, MUTED))
    bx, by = 812, 250
    f.append(ball(bx, by))
    # швидкість — по дотичній униз-праворуч
    f.append(arrow(bx + 6, by + 8, bx + 40, by + 44, color=VEL, sw=3))
    f.append(text(bx + 44, by + 40, "v", size=14, bold=True, color=VEL, anchor="start"))
    # g униз
    f.append(arrow(bx - 34, by + 4, bx - 34, by + 56, color=GRAV, sw=2.6))
    f.append(text(bx - 46, by + 34, "g", size=14, bold=True, color=GRAV, anchor="end"))
    f.append(ground(cxC - 90, cxC + 90, 300, n=7))
    f.append(text(cxC, 322, "летить по дузі, g тягне вниз", size=11.5, color=MUTED))

    # ── спільний висновок ──
    b, bw, bh = textbox(W / 2, 388,
                        "У всіх трьох єдина сила — тяжіння, тож прискорення однакове: g, спрямоване вниз",
                        size=13, pad=11, fill="#eafaf1", stroke=FIELD, sw=1.6)
    f.append(b)
    return render(os.path.join(IMG, "what-is-free-fall.svg"), W, H, *f)


# ── Фігура 2: стробоскоп — відстань ~ t², швидкість ~ t ─────────────────────
def fig_strobe():
    W, H = 760, 496
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Рівні проміжки часу: відстань росте як t², швидкість — як t", size=15.5, bold=True))

    axis = 250
    y0 = 76
    unit = (430 - y0) / 16.0        # 16 одиниць висоти на всю шкалу
    ys = [y0 + unit * d for d in (0, 1, 4, 9, 16)]   # кумулятивні t²

    # заголовки колонок
    f.append(text(150, 60, "відстань ~ t²", size=12.5, bold=True, color=GRAV))
    f.append(text(470, 60, "швидкість ~ t", size=12.5, bold=True, color=VEL))

    # вертикальна вісь падіння
    f.append(line(axis, y0 - 6, axis, ys[-1] + 6, color="#c7ced6", sw=1.4))

    odd = [1, 3, 5, 7]
    for i in range(5):
        yy = ys[i]
        # горизонтальна пунктирна напрямна (до початку стрілок, щоб не чіпати підписів)
        f.append(line(axis, yy, 272, yy, color="#e2e7ee", sw=1.0, dash="3,5"))
        # позначка часу
        f.append(text(axis - 150, yy + 4, "t = %d" % i, size=12, color=MUTED, anchor="start"))
        # м'ячик
        f.append(ball(axis, yy, 9))
        # приріст (непарні числа) — дужка ліворуч між сусідніми
        if i > 0:
            ymid = (ys[i - 1] + ys[i]) / 2
            bx = 205
            f.append(line(bx, ys[i - 1] + 3, bx, ys[i] - 3, color=GRAV, sw=1.6))
            f.append(line(bx, ys[i - 1] + 3, bx + 6, ys[i - 1] + 3, color=GRAV, sw=1.6))
            f.append(line(bx, ys[i] - 3, bx + 6, ys[i] - 3, color=GRAV, sw=1.6))
            f.append(text(bx - 8, ymid + 4, "+%d" % odd[i - 1], size=12.5, bold=True, color=GRAV, anchor="end"))
        # стрілка швидкості праворуч, довжина ~ t
        L = i * 34
        if L > 0:
            f.append(arrow(axis + 24, yy, axis + 24 + L, yy, color=VEL, sw=2.6))
        else:
            f.append(text(axis + 30, yy + 4, "0", size=12, color=MUTED, anchor="start"))

    # підсумок унизу
    b, bw, bh = textbox(W / 2, 470,
                        "Прирости за рівні кроки: 1, 3, 5, 7 (непарні) — сума 16 = 4²; швидкість натомість росте рівними порціями",
                        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "strobe-fall.svg"), W, H, *f)


# ── Фігура 3: v(t) — вакуум проти повітря, гранична швидкість ────────────────
def fig_terminal():
    W, H = 760, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Швидкість у часі: у вакуумі — без межі, у повітрі — до граничної", size=15, bold=True))

    ox, oy = 96, 366           # початок координат
    xmax, ytop = 680, 74
    vt_y = 168                 # рівень граничної швидкості
    tau = 105.0                # характерний масштаб (px по осі часу)

    # осі
    f.append(arrow(ox, oy, xmax + 8, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, ytop - 4, color=LINE, sw=1.6))
    f.append(text(xmax + 4, oy + 22, "час  t", size=12.5, color=INK, anchor="end"))
    f.append(text(ox - 8, ytop + 4, "швидкість  v", size=12.5, color=INK, anchor="end"))

    # асимптота граничної швидкості
    f.append(line(ox, vt_y, xmax, vt_y, color=FIELD, sw=1.5, dash="6,5"))
    f.append(text(xmax - 4, vt_y - 10, "гранична швидкість", size=12, bold=True, color=FIELD, anchor="end"))

    vt = oy - vt_y             # висота асимптоти в px (= v_terminal)

    # пряма вакууму: v = g·t, дотична до кривої в нулі (нахил vt/tau)
    slope = vt / tau
    # доводимо пряму до верху графіка
    dx_top = (oy - ytop) / slope
    f.append(line(ox, oy, ox + dx_top, ytop, color=GRAV, sw=2.6))
    f.append(text(ox + dx_top + 6, ytop + 12, "вакуум:  v = g·t", size=12.5, bold=True, color=GRAV, anchor="start"))

    # крива повітря: v = v_t · tanh(t/tau)
    pts = []
    x = ox
    while x <= xmax:
        t = (x - ox) / tau
        y = oy - vt * math.tanh(t)
        pts.append("%.1f,%.1f" % (x, y))
        x += 6
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), VEL))
    f.append(text(408, 246, "повітря", size=12.5, bold=True, color=VEL, anchor="middle"))

    # підпис зони початкового збігу
    f.append(text(ox + 150, oy - 24, "спершу опір малий —", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(ox + 150, oy - 9, "падає майже як у вакуумі", size=11.5, color=MUTED, anchor="middle"))

    b, bw, bh = textbox(W / 2, 426,
                        "Опір повітря росте зі швидкістю; коли він зрівняє вагу — прискорення стає нулем, а швидкість застигає",
                        size=11, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "terminal-velocity.svg"), W, H, *f)


# ── Фігура 4: площа під v(t) — шлях = прямокутник + трикутник (звідки ½) ──────
def fig_vt_area():
    W, H = 760, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Площа під графіком швидкості — це пройдений шлях", size=15.5, bold=True))

    ox, oy = 100, 392          # початок координат
    xaxis, ytop = 662, 80
    t_end = 560                # обрана мить t
    v0y = oy - 96              # рівень v₀ (верх прямокутника)
    vEy = oy - 246             # рівень v = v₀+g·t (кінець похилої)

    # заливки: прямокутник v₀·t (синій тон) + трикутник ½g·t² (червоний тон)
    f.append(rect(ox, v0y, t_end - ox, oy - v0y, fill="#eaf0fd", stroke='none', sw=0, rx=0))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="none"/>'
             % (ox, v0y, t_end, v0y, t_end, vEy))

    # осі
    f.append(arrow(ox, oy, xaxis, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, ytop, color=LINE, sw=1.6))
    f.append(text(xaxis - 2, oy + 22, "час  t", size=12.5, color=INK, anchor="end"))
    f.append(text(ox + 8, ytop + 4, "швидкість  v", size=12.5, color=INK, anchor="start"))

    # похила лінія швидкості v = v₀ + g·t
    f.append(line(ox, v0y, t_end, vEy, color=INK, sw=2.8))
    f.append(text(t_end + 8, vEy - 2, "v = v₀ + g·t", size=13, bold=True, color=INK, anchor="start"))

    # межі прямокутника й трикутника
    f.append(line(ox, v0y, t_end, v0y, color=MUTED, sw=1.2, dash="4,5"))
    f.append(line(t_end, oy, t_end, vEy, color=MUTED, sw=1.2, dash="4,5"))

    # v₀ на осі
    f.append(line(ox - 5, v0y, ox + 5, v0y, color=INK, sw=1.6))
    f.append(text(ox - 12, (oy + v0y) / 2 + 4, "v₀", size=13, bold=True, color=NEG, anchor="end"))
    # приріст g·t праворуч
    f.append(text(t_end + 8, (v0y + vEy) / 2 + 4, "g·t", size=13, bold=True, color=POS, anchor="start"))
    # t на осі
    f.append(line(t_end, oy - 4, t_end, oy + 4, color=INK, sw=1.6))
    f.append(text(t_end, oy + 22, "t", size=12.5, color=MUTED))

    # підписи площ
    f.append(text((ox + t_end) / 2, (v0y + oy) / 2 + 5, "v₀·t", size=15, bold=True, color=NEG))
    f.append(text((ox + 2 * t_end) / 3 + 22, v0y - 44, "½ g·t²", size=15, bold=True, color=POS))

    b, bw, bh = textbox(W / 2, 452,
                        "Прямокутник дає v₀·t, трикутник — ½g·t². Трикутник удвічі менший за g·t·t, бо приріст g·t набігав поступово",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "vt-area.svg"), W, H, *f)


# ── Фігура 5: розклад параболи — інерція вбік мінус падіння вниз ──────────────
def fig_parabola_decompose():
    W, H = 780, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Кинуте під кутом = рівномірний рух убік + вільне падіння вниз", size=15, bold=True))

    lx, ly = 94, 404           # точка кидка
    dxk = 138.0                # крок по горизонталі за рівний час
    upk = 84.0                 # підйом по інерції за крок
    gu = 15.0                  # одиниця падіння (½g·t² ∝ k²)
    ax_of = lambda k: lx + dxk * k
    iner_y = lambda k: ly - upk * k
    act_y = lambda k: (ly - upk * k) + gu * k * k

    # земля
    f.append(ground(70, 712, ly, n=14))

    # інерційна пряма (якби не тяжіння)
    f.append(line(lx, ly, ax_of(4.15), iner_y(4.15), color=NEG, sw=2.2, dash="7,6"))
    f.append(text(556, 92, "якби не тяжіння —", size=12.5, bold=True, color=NEG, anchor="start"))
    f.append(text(556, 109, "летіло б по прямій", size=12.5, color=NEG, anchor="start"))

    # парабола (справжній політ)
    pts = []
    k = 0.0
    while k <= 4.001:
        pts.append("%.1f,%.1f" % (ax_of(k), act_y(k)))
        k += 0.2
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), VEL))

    # провали ∝ t²
    props = {1: "1", 2: "4", 3: "9", 4: "16"}
    for kk in (1, 2, 3, 4):
        x = ax_of(kk)
        f.append(line(x, iner_y(kk), x, act_y(kk), color=MUTED, sw=1.4, dash="4,4"))
        f.append(circle(x, iner_y(kk), 3, fill=NEG, stroke=NEG, sw=1))     # точка на прямій
        f.append(circle(x, act_y(kk), 4, fill="#fef6e7", stroke=VEL, sw=2))  # справжня точка
        ymid = (iner_y(kk) + act_y(kk)) / 2
        f.append(text(x + 11, ymid + 4, "×" + props[kk], size=12.5, bold=True, color=POS, anchor="start"))

    # точка кидка
    f.append(circle(lx, ly, 5, fill="#fef6e7", stroke=VEL, sw=2))

    # рівні кроки часу на осі
    for kk in range(5):
        x = ax_of(kk)
        f.append(line(x, ly, x, ly + 6, color=INK, sw=1.5))
        f.append(text(x, ly + 22, "t=%d" % kk, size=11.5, color=MUTED))
    f.append(text((ax_of(0) + ax_of(4)) / 2, ly + 40, "рівні проміжки часу  →  рівні кроки вбік",
                  size=11.5, color=MUTED))

    b, bw, bh = textbox(W / 2, 476,
                        "Горизонталь — рівномірний рух (рівні кроки).\n"
                        "Вертикаль — падіння з провалом ∝ t² (1 : 4 : 9 : 16). Сума двох — парабола",
                        size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "parabola-decompose.svg"), W, H, *f)


AMBER = "#d68910"   # легенда / непевне


def openmark(cx, cy, r=6):
    return circle(cx, cy, r, fill=BG, stroke=NEG, sw=1.8)


# ── Фігура 6 (hist): жолоб Ґалілея + водяний годинник ────────────────────────
def fig_incline_clock():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Ґалілеїв жолоб і водяний годинник: як зміряти те, що падає надто швидко",
                  size=15.5, bold=True))
    f.append(line(655, 58, 655, 412, color="#dfe4ea", sw=1.2, dash="4,6"))
    f.append(text(300, 70, "похилий жолоб", size=13, bold=True))

    A = (110.0, 120.0)
    B = (600.0, 360.0)
    dx, dy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nux, nuy = uy, -ux            # нормаль «угору-праворуч»
    ndx, ndy = -uy, ux           # нормаль «униз-ліворуч»

    def onramp(fr):
        return (A[0] + fr * dx, A[1] + fr * dy)

    f.append(ground(90, 645, 360, n=12))
    f.append(line(A[0], A[1], A[0], 360, color=MUTED, sw=1.2, dash="4,5"))
    f.append('<path d="M 568 360 A 32 32 0 0 1 571.3 345.9" fill="none" '
             'stroke="%s" stroke-width="1.2"/>' % MUTED)
    f.append(text(559, 350, "θ", size=12, color=MUTED, italic=True))

    f.append(line(A[0], A[1], B[0], B[1], color=INK, sw=6))
    f.append(line(A[0], A[1], B[0], B[1], color="#cfd6df", sw=2))

    fracs = [1.0 / 9, 4.0 / 9, 1.0]        # позиції за t = 1, 2, 3 (відстань 1, 4, 9)
    beats = ["t = 1", "t = 2", "t = 3"]
    pts = [A] + [onramp(fr) for fr in fracs]

    f.append(text(A[0] + 26 * nux, A[1] + 26 * nuy, "старт", size=11.5, color=MUTED))
    f.append(ball(A[0], A[1], 11))

    for i, fr in enumerate(fracs):
        px, py = onramp(fr)
        f.append(line(px - 8 * nux, py - 8 * nuy, px + 8 * nux, py + 8 * nuy, color="#8a94a6", sw=1.4))
        f.append(openmark(px, py, 6))
        f.append(text(px + 24 * nux, py + 24 * nuy, beats[i], size=12, bold=True, color=NEG))

    odd = ["+1", "+3", "+5"]
    offs = [(p[0] + 14 * ndx, p[1] + 14 * ndy) for p in pts]
    for i in range(3):
        x1, y1 = offs[i]
        x2, y2 = offs[i + 1]
        f.append(line(x1, y1, x2, y2, color=GRAV, sw=1.6))
        for (ex, ey) in (offs[i], offs[i + 1]):
            f.append(line(ex, ey, ex + 6 * nux, ey + 6 * nuy, color=GRAV, sw=1.4))
        mx = (pts[i][0] + pts[i + 1][0]) / 2 + 26 * ndx
        my = (pts[i][1] + pts[i + 1][1]) / 2 + 26 * ndy
        f.append(text(mx, my, odd[i], size=12.5, bold=True, color=GRAV))

    f.append(text(770, 86, "водяний годинник", size=13, bold=True, color=NEG))
    f.append(rect(735, 100, 70, 50, fill="#dce9fb", stroke=NEG, sw=1.6, rx=10))
    f.append(line(742, 112, 798, 112, color=NEG, sw=1, dash="3,3"))
    f.append(line(770, 150, 770, 170, color=NEG, sw=1.2))
    f.append(circle(770, 178, 3, fill="#cfe0fb", stroke=NEG, sw=1.2))
    f.append(circle(770, 188, 2.4, fill="#cfe0fb", stroke=NEG, sw=1.2))
    f.append(rect(740, 196, 60, 40, fill="#dce9fb", stroke=NEG, sw=1.6, rx=4))
    f.append(line(746, 214, 794, 214, color=NEG, sw=1, dash="3,3"))
    f.append(mtext(770, 262, ["ловиш воду за спуск,", "важиш — це і є час"], size=11, color=MUTED))
    bb, bw, bh = textbox(770, 322, "рівні порції води =\nрівні проміжки часу",
                         size=11.5, pad=10, fill="#eef4fd", stroke=NEG, sw=1.4)
    f.append(bb)

    bb, bw, bh = textbox(W / 2, 442,
                         "Пологий жолоб «розбавляє» падіння — і воно стає досить повільним, щоб зміряти водою.\n"
                         "Сам закон h ∝ t² від нахилу не залежить: змінюється лише масштаб часу.",
                         size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(bb)
    return render(os.path.join(IMG, "incline-clock.svg"), W, H, *f)


# ── Фігура 7 (hist): думка-спростування Арістотеля ──────────────────────────
def fig_reductio():
    W, H = 900, 448
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Думка, що не потребує досліду: чому Арістотель мусив помилятися",
                  size=15.5, bold=True))
    for dxv in (305, 595):
        f.append(line(dxv, 58, dxv, 332, color="#dfe4ea", sw=1.2, dash="4,6"))

    # А: за Арістотелем
    f.append(text(155, 74, "За Арістотелем", size=14, bold=True))
    f.append(ball(130, 120, 15))
    f.append(text(107, 124, "M", size=12, bold=True))
    f.append(arrow(130, 138, 130, 236, color=VEL, sw=3))
    f.append(text(150, 196, "швидко", size=10.5, color=VEL, anchor="start"))
    f.append(ball(196, 120, 8))
    f.append(text(212, 124, "m", size=12, bold=True))
    f.append(arrow(196, 130, 196, 178, color=VEL, sw=2.6))
    f.append(text(210, 165, "повільно", size=10.5, color=VEL, anchor="start"))
    f.append(ground(70, 245, 262, n=8))
    f.append(mtext(155, 300, ["важче — начебто", "швидше, ∝ вазі"], size=11, color=MUTED))

    # B: зв'яжемо разом
    f.append(text(450, 74, "Зв'яжемо їх ниткою", size=14, bold=True))
    f.append(ball(450, 116, 15))
    f.append(text(427, 120, "M", size=12, bold=True))
    f.append(line(450, 131, 450, 143, color=INK, sw=2))
    f.append(ball(450, 152, 8))
    f.append(text(470, 156, "m", size=12, bold=True))
    f.append(fitbox(325, 176, 250, 44, "легкий гальмує важкий →\nпара ПОВІЛЬНІША за M",
                    size=12, stroke=NEG, fill="#eef4fd"))
    f.append(fitbox(325, 232, 250, 44, "та пара важча (M+m) →\nШВИДША за M",
                    size=12, stroke=POS, fill="#fdeeec"))
    f.append(text(450, 306, "і повільніша, і швидша — так не буває", size=11.5, bold=True, color=POS))

    # C: єдиний вихід
    f.append(text(745, 74, "Єдиний вихід", size=14, bold=True))
    f.append(ball(718, 120, 15))
    f.append(text(695, 124, "M", size=12, bold=True))
    f.append(ball(775, 120, 8))
    f.append(text(792, 124, "m", size=12, bold=True))
    f.append(arrow(718, 142, 718, 236, color=VEL, sw=3))
    f.append(arrow(775, 142, 775, 236, color=VEL, sw=3))
    f.append(ground(660, 832, 250, n=8))
    bb, bw, bh = textbox(745, 302, "усі падають однаково", size=12.5, pad=9,
                         fill="#eafaf1", stroke=FIELD, sw=1.5, bold=True, color=FIELD)
    f.append(bb)

    bb, bw, bh = textbox(W / 2, 418,
                         "Хай навіть Арістотель має рацію — зв'язана пара мусила б падати і повільніше, і швидше за важчий камінь.\n"
                         "Суперечності немає лише тоді, коли швидкість падіння від ваги взагалі не залежить.",
                         size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(bb)
    return render(os.path.join(IMG, "reductio.svg"), W, H, *f)


# ── Фігура 8 (hist): часова стрічка розуміння + статус доказовості ───────────
def fig_timeline():
    W, H = 940, 322
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дві тисячі років до відповіді — і статус кожного кроку", size=15.5, bold=True))

    axis_y = 156
    f.append(arrow(70, axis_y, 898, axis_y, color=LINE, sw=1.8))

    xs = [130, 315, 495, 665, 835]
    cols = [POS, NEG, NEG, NEG, AMBER]
    dates = ["≈350 до н.е.", "1586", "1604", "1638", "1654 / 1717"]
    names = ["Арістотель:\nважче падає швидше",
             "Стевін і де Ґроот:\nдослід у Делфті",
             "Ґалілей → Сарпі:\nзакон h ∝ t²",
             "«Бесіди»:\nдрук у Лейдені",
             "Вівіані:\nлегенда про Пізу"]
    stat = ["пануюча хиба", "усталено", "усталено", "усталено", "легенда"]

    for i, x in enumerate(xs):
        c = cols[i]
        f.append(text(x, 128, dates[i], size=12.5, bold=True))
        f.append(line(x, axis_y - 7, x, 182, color=c, sw=1.4))
        f.append(circle(x, axis_y, 7, fill=c, stroke=c, sw=1.4))
        bx, by, bw, bh = x - 78, 184, 156, 50
        if c == AMBER:
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
                     'fill="%s" stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>'
                     % (bx, by, bw, bh, FILL, c))
            f.append(mtext(x, by + 21, names[i].split("\n"), size=11.5))
        else:
            f.append(fitbox(bx, by, bw, bh, names[i], size=12, stroke=c))
        f.append(text(x, 250, stat[i], size=10.5, bold=True, color=c))

    ly = 288
    items = [(250, NEG, "усталений факт", False), (430, POS, "пануюча догма", False),
             (620, AMBER, "легенда", True)]
    for lx, c, lab, dash in items:
        if dash:
            f.append('<rect x="%.1f" y="%.1f" width="14" height="14" rx="2" fill="none" '
                     'stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (lx, ly - 11, c))
        else:
            f.append(rect(lx, ly - 11, 14, 14, fill=c, stroke=c, sw=1, rx=2))
        f.append(text(lx + 20, ly, lab, size=11, color=INK, anchor="start"))
    return render(os.path.join(IMG, "fall-timeline.svg"), W, H, *f)


# ── Фігура 9 (proj): метод Ейлера — сходинки вздовж дотичної до граничної ─────
def fig_euler_steps():
    W, H = 760, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Метод Ейлера: крок за кроком уздовж нахилу — до граничної швидкості", size=14.5, bold=True))

    ox, oy = 92, 384
    xmax, ytop = 690, 74
    Tmax, Vmax = 3.2, 1.15

    def X(t): return ox + (xmax - ox) * (t / Tmax)
    def Y(v): return oy - (oy - ytop) * (v / Vmax)

    # осі
    f.append(arrow(ox, oy, xmax + 8, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, ytop - 4, color=LINE, sw=1.6))
    f.append(text(xmax + 4, oy + 22, "час  t / τ", size=12, color=INK, anchor="end"))
    f.append(text(ox - 6, ytop + 2, "v / v_t", size=12, color=INK, anchor="end"))

    # рівень граничної швидкості
    f.append(line(ox, Y(1), xmax, Y(1), color=FIELD, sw=1.5, dash="6,5"))
    f.append(text(xmax - 4, Y(1) - 9, "гранична швидкість v_t", size=11.5, bold=True, color=FIELD, anchor="end"))

    # точна крива tanh
    pts, t = [], 0.0
    while t <= Tmax + 1e-9:
        pts.append("%.1f,%.1f" % (X(t), Y(math.tanh(t))))
        t += 0.04
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), GRAV))

    # сходинки Ейлера з навмисне грубим кроком, щоб їх було видно
    dt = 0.4
    ev, v, t = [(0.0, 0.0)], 0.0, 0.0
    while t < Tmax - 1e-9:
        a = 1.0 - v * v
        v = v + a * dt
        t = t + dt
        ev.append((t, v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % (X(t), Y(v)) for t, v in ev), VEL))
    for t, v in ev:
        f.append(circle(X(t), Y(v), 4.2, fill=BG, stroke=VEL, sw=2))

    # підписи у порожньому нижньому куті
    f.append(text(X(2.35), Y(0.42), "точний розв'язок  v_t·tanh(t/τ)", size=11.5, color=GRAV, anchor="middle"))
    f.append(text(X(2.35), Y(0.24), "Ейлер, крок Δt = 0.4·τ", size=11.5, bold=True, color=VEL, anchor="middle"))

    b, bw, bh = textbox(W / 2, 448,
                        "Кожен крок: узяти нахил a = g − β·v² у поточній точці, ступити вздовж нього Δt,\n"
                        "перерахувати нахил. Дрібніший Δt — ближче до точної кривої.",
                        size=11, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "euler-steps.svg"), W, H, *f)


# ── Фігура 10 (proj): стійкість — завеликий крок ламає розрахунок ─────────────
def fig_euler_stability():
    W, H = 760, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Завеликий крок ламає розрахунок: та сама формула, різний Δt", size=14.5, bold=True))

    ox, oy = 92, 398
    xmax, ytop = 660, 84
    Tmax, Vmax = 6.0, 1.30

    def X(t): return ox + (xmax - ox) * (t / Tmax)
    def Y(v): return oy - (oy - ytop) * (v / Vmax)

    runs = [(0.2, GRAV, "Δt=0.2τ: точно"),
            (0.85, "#e67e22", "Δt=0.85τ: дзвенить"),
            (1.1, VEL, "Δt=1.1τ: розходиться")]

    # легенда — рядок над полем (порожня смуга між заголовком і графіком)
    for lx, (dt, col, lab) in zip((90, 250, 470), runs):
        f.append(line(lx, 58, lx + 24, 58, color=col, sw=2.8))
        f.append(text(lx + 28, 62, lab, size=10.5, color=INK, anchor="start"))

    # осі
    f.append(arrow(ox, oy, xmax + 8, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, ytop - 4, color=LINE, sw=1.6))
    f.append(text(xmax + 4, oy + 22, "час  t / τ", size=12, color=INK, anchor="end"))
    f.append(text(ox - 6, ytop + 2, "v / v_t", size=12, color=INK, anchor="end"))

    # гранична швидкість
    f.append(line(ox, Y(1), xmax, Y(1), color=FIELD, sw=1.4, dash="6,5"))
    f.append(text(xmax - 4, Y(1) - 8, "v_t", size=11.5, bold=True, color=FIELD, anchor="end"))

    # точна крива — сірим пунктиром
    pts, t = [], 0.0
    while t <= Tmax + 1e-9:
        pts.append("%.1f,%.1f" % (X(t), Y(math.tanh(t))))
        t += 0.05
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2,4"/>'
             % (" ".join(pts), MUTED))

    def euler(dt):
        out, v, t = [(0.0, 0.0)], 0.0, 0.0
        while t < Tmax - 1e-9:
            a = 1.0 - v * v
            v = v + a * dt
            t = t + dt
            out.append((t, v))
        return out

    for dt, col, _ in runs:
        r = [(t, v) for t, v in euler(dt) if t <= Tmax]
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join("%.1f,%.1f" % (X(t), Y(max(-0.3, min(Vmax, v)))) for t, v in r), col))
        for t, v in r:
            if -0.3 <= v <= Vmax:
                f.append(circle(X(t), Y(v), 3.4, fill=BG, stroke=col, sw=1.8))

    b, bw, bh = textbox(W / 2, 470,
                        "Стійкість вимагає Δt < τ = v_t/g: менший крок — монотонно й точно;\n"
                        "між τ/2 і τ — загасні коливання; більший за τ — амплітуда наростає, числа стають безглуздими.",
                        size=10.5, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "euler-stability.svg"), W, H, *f)


if __name__ == "__main__":
    fig_what_is_free_fall()
    fig_strobe()
    fig_terminal()
    fig_vt_area()
    fig_parabola_decompose()
    fig_incline_clock()
    fig_reductio()
    fig_timeline()
    fig_euler_steps()
    fig_euler_stability()
    print("OK: фігури у", IMG)
