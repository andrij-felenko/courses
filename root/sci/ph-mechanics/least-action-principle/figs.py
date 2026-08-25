# -*- coding: utf-8 -*-
"""Фігури до теми «Принцип найменшої дії».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def poly(pts, color=INK, sw=2.4, dash=None):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


def arc_path(a, b, bulge, n=48):
    """Дуга від a до b з піднятою серединою (bulge>0 — вигин угору, тобто вгору по екрану)."""
    ax, ay = a; bx, by = b
    out = []
    for k in range(n + 1):
        t = k / n
        x = ax + t * (bx - ax)
        y = ay + t * (by - ay) - bulge * math.sin(math.pi * t)
        out.append((x, y))
    return out


# ── Фігура 1: два описи руху — локальний Ньютон і глобальний принцип дії ──────
def fig_path_selection():
    W, H = 940, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Той самий рух — два описи", size=18, bold=True))

    # роздільник панелей
    f.append(line(400, 66, 400, 392, color="#d6dde6", sw=1.4, dash="5,6"))

    # ── ліва панель: Ньютон, локально ──
    f.append(text(210, 62, "Ньютон: зблизька, мить за миттю", size=14, bold=True, color=NEG))
    traj = arc_path((80, 330), (350, 180), 70)
    f.append(poly(traj, color=INK, sw=2.6))
    # точка на траєкторії з дотичною швидкістю і силою
    px, py = traj[22]
    f.append(circle(px, py, 7, fill=FILL, stroke=INK, sw=2))
    # дотична (швидкість)
    tx, ty = traj[26]
    dx, dy = tx - px, ty - py
    m = math.hypot(dx, dy) or 1
    f.append(arrow(px, py, px + 62 * dx / m, py + 62 * dy / m, color=MUTED, sw=2.0))
    f.append(text(px + 62 * dx / m + 8, py + 62 * dy / m - 6, "v", size=13, italic=True, color=MUTED, anchor="start"))
    # сила (вниз-ліворуч, до «поля»)
    f.append(arrow(px, py, px - 6, py + 66, color=POS, sw=2.6))
    f.append(text(px - 30, py + 46, "F = m·a", size=13, bold=True, color=POS, anchor="end"))
    f.append(fitbox(60, 360, 300, 44,
                    "знаєш силу в цій точці — знаєш\nприскорення, і рух будується далі",
                    size=12, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.4))

    # ── права панель: принцип дії, глобально ──
    f.append(text(670, 62, "Принцип дії: згори, весь шлях одразу", size=14, bold=True, color=FIELD))
    A = (445, 322); B = (872, 150)
    # кандидатні шляхи (сірі, пунктир) з їхніми значеннями дії
    cand = [(150, "S = 51"), (25, "S = 47"), (-55, "S = 58")]
    for bulge, lab in cand:
        pts = arc_path(A, B, bulge)
        f.append(poly(pts, color="#b6bfca", sw=1.8, dash="7,5"))
        ax, ay = pts[24]
        yy = ay - 12 if bulge >= 0 else ay + 20
        f.append(text(ax, yy, lab, size=11, color=MUTED))
    # справжній шлях (зелений, суцільний) — найменша дія
    true = arc_path(A, B, 92)
    f.append(poly(true, color=FIELD, sw=3.0))
    ax, ay = true[24]
    f.append(text(ax, ay - 14, "S = 36  (δS = 0)", size=12.5, bold=True, color=FIELD))
    # кінці A, B
    f.append(circle(A[0], A[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(A[0] - 6, A[1] + 20, "A  старт", size=12, color=INK, anchor="middle"))
    f.append(circle(B[0], B[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(B[0], B[1] - 14, "B  фініш", size=12, color=INK, anchor="middle"))
    f.append(fitbox(430, 360, 470, 44,
                    "кожному шляху — одне число (дія S); справжній той,\nде S найменша (точніше — стаціонарна: δS = 0)",
                    size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4))

    return render(os.path.join(IMG, "path-selection.svg"), W, H, *f)


# ── Фігура 2: чому T − U — торг між «побути високо» і «не гнати» ──────────────
def fig_action_tradeoff():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чому дія бере різницю T − U", size=18, bold=True))

    ground = 384
    x0, x1 = 150, 748
    # вісь висоти/потенціалу ліворуч
    f.append(arrow(96, ground, 96, 96, color=MUTED, sw=1.3))
    f.append(text(88, 104, "U (висота)", size=12, color=MUTED, anchor="end"))
    f.append(text(88, ground - 2, "0", size=11, color=MUTED, anchor="end"))
    # земля
    f.append(line(120, ground, 792, ground, color=INK, sw=2))
    for gx in range(140, 793, 34):
        f.append(line(gx, ground, gx - 10, ground + 12, color="#c8ced6", sw=1.2))

    # парабола підкинутого каменя
    top_h = 250
    par = []
    for k in range(61):
        t = k / 60
        x = x0 + t * (x1 - x0)
        y = ground - top_h * 4 * t * (1 - t)
        par.append((x, y))
    f.append(poly(par, color=INK, sw=3.0))
    # камінь у кількох точках
    for k in (6, 18, 30, 42, 54):
        f.append(circle(par[k][0], par[k][1], 5.5, fill=FILL, stroke=INK, sw=1.6))

    # апекс: тут U велике — вигідно
    apex = par[30]
    f.append(circle(apex[0], apex[1], 7, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(fitbox(apex[0] - 210, 74, 420, 40,
                    "нагорі U велике → −U тягне дію вниз: побути тут вигідно",
                    size=12.5, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.5))
    f.append(arrow(apex[0], 116, apex[0], apex[1] - 10, color=FIELD, sw=1.8))

    # висхідна гілка: розгін угору коштує T
    rise = par[12]
    f.append(arrow(rise[0] - 26, rise[1] + 34, rise[0] + 8, rise[1] - 6, color=POS, sw=2.2))
    f.append(fitbox(150, 250, 250, 44,
                    "підйом = розгін угору →\nвелике T: невигідно",
                    size=12.5, pad=7, fill="#fdecea", stroke=POS, sw=1.5))

    f.append(fitbox(430, 250, 320, 44,
                    "справжня парабола — точна\nрівновага цих двох жадоб",
                    size=12.5, pad=7, fill=FILL, stroke=MUTED, sw=1.4))

    f.append(fitbox(150, 410, 580, 40,
                    "мінімум дії ∫(T − U)dt виникає там, де виграш «побути високо» саме зрівноважує програш «розігнатися»",
                    size=12.5, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4))
    return render(os.path.join(IMG, "action-tradeoff.svg"), W, H, *f)


# ── Фігура 3: принцип Ферма — світло обирає найшвидший за часом шлях ──────────
def fig_fermat():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Прадід принципу: світло обирає найшвидший за часом шлях",
                  size=16.5, bold=True))

    iface = 258
    xL, xR = 80, 760
    # середовища
    f.append(rect(xL, 62, xR - xL, iface - 62, fill="#fbfcfd", stroke="#e3e8ee", sw=1.2, rx=0))
    f.append(rect(xL, iface, xR - xL, 396 - iface, fill="#eaf1fb", stroke="#d5e0f2", sw=1.2, rx=0))
    f.append(line(xL, iface, xR, iface, color=NEG, sw=2))
    f.append(text(xR - 8, iface - 10, "повітря — світло швидке", size=12.5, color=MUTED, anchor="end"))
    f.append(text(xR - 8, iface + 22, "вода — світло повільне", size=12.5, color=NEG, anchor="end"))

    A = (200, 120); B = (600, 372); P = (470, iface)
    # прямий шлях (сірий пунктир) — довший за часом
    f.append(poly([A, B], color="#b6bfca", sw=1.8, dash="7,5"))
    xs = A[0] + (iface - A[1]) / (B[1] - A[1]) * (B[0] - A[0])
    f.append(circle(xs, iface, 3.5, fill="#b6bfca", stroke="#b6bfca", sw=1))
    f.append(text(300, 210, "прямий — коротший у метрах,", size=12, color=MUTED, anchor="middle"))
    f.append(text(300, 227, "але довший у часі", size=12, color=MUTED, anchor="middle"))

    # заломлений шлях (зелений суцільний) — найшвидший
    f.append(poly([A, P], color=FIELD, sw=3.0))
    f.append(poly([P, B], color=FIELD, sw=3.0))
    f.append(circle(A[0], A[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(A[0] - 14, A[1] - 4, "A", size=14, bold=True, color=INK, anchor="end"))
    f.append(circle(B[0], B[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(B[0] + 14, B[1] + 6, "B", size=14, bold=True, color=INK, anchor="start"))
    f.append(circle(P[0], P[1], 5, fill=FIELD, stroke=FIELD, sw=1))

    # нормаль у точці зламу
    f.append(line(P[0], iface - 78, P[0], iface + 78, color=MUTED, sw=1.3, dash="4,5"))
    f.append(text(P[0] + 8, iface - 70, "нормаль", size=11, color=MUTED, anchor="start"))
    # кути
    f.append(text(P[0] - 40, iface - 30, "θ₁", size=14, italic=True, color=FIELD, anchor="middle"))
    f.append(text(P[0] - 20, iface + 52, "θ₂", size=14, italic=True, color=FIELD, anchor="middle"))

    f.append(text(560, 150, "заломлений —", size=12.5, bold=True, color=FIELD, anchor="middle"))
    f.append(text(560, 168, "найшвидший за часом", size=12.5, bold=True, color=FIELD, anchor="middle"))

    f.append(fitbox(80, 414, 680, 46,
                    "у повільній воді промінь іде крутіше (ближче до нормалі, θ₂ < θ₁), щоб менше пройти\n"
                    "повільним середовищем — саме тому світло й заломлюється на межі",
                    size=12.5, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4))
    return render(os.path.join(IMG, "fermat-refraction.svg"), W, H, *f)


# ── Фігура 4: часова лінія — народження принципу через двадцять століть ───────
def fig_timeline():
    W, H = 1260, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Народження принципу через двадцять століть", size=19, bold=True))

    axis_y = 250
    f.append(line(70, axis_y, 1160, axis_y, color=INK, sw=2.4))
    f.append(arrow(1150, axis_y, 1205, axis_y, color=INK, sw=2.4))
    f.append(text(1200, axis_y - 12, "час", size=12, color=MUTED, anchor="end"))

    # (cx, ім'я, рік, опис[2 рядки], колір, заливка, картка-вгорі?)
    nodes = [
        (150,  "Герон",           "~I ст. н.е.", ["відбиття світла —", "найкоротший шлях"],       NEG,   "#eaf0fd", True),
        (348,  "Ферма",           "1662",        ["світло обирає", "найменший ЧАС"],              NEG,   "#eaf0fd", False),
        (546,  "Мопертюї й Ейлер", "1744",        ["дія ∫mv·ds → мінімум;", "строгість дав Ейлер"], POS,   "#fdecea", True),
        (744,  "Скандал König",   "1751–52",     ["бійка за пріоритет;", "лист Ляйбніца 1707"],   POS,   "#fdecea", False),
        (942,  "Лагранж",         "1788",        ["δ-числення;", "аналітична механіка"],          FIELD, "#eef6ef", True),
        (1140, "Гамільтон",       "1834–35",     ["дія ∫L·dt = ∫(T−U)dt;", "прийшла з оптики"],   FIELD, "#eef6ef", False),
    ]
    cw, ch = 202, 92
    for cx, name, year, desc, col, fill, above in nodes:
        f.append(circle(cx, axis_y, 8, fill=col, stroke=INK, sw=1.8))
        if above:
            top = axis_y - 42 - ch
            f.append(rect(cx - cw / 2, top, cw, ch, fill=fill, stroke=col, sw=1.8))
            f.append(text(cx, top + 27, name, size=14.5, bold=True, color=col))
            f.append(mtext(cx, top + 52, desc, size=12.5, color=INK))
            f.append(line(cx, top + ch, cx, axis_y - 8, color=col, sw=1.6))
            f.append(text(cx, axis_y + 28, year, size=13.5, bold=True, color=INK))
        else:
            top = axis_y + 42
            f.append(rect(cx - cw / 2, top, cw, ch, fill=fill, stroke=col, sw=1.8))
            f.append(text(cx, top + 27, name, size=14.5, bold=True, color=col))
            f.append(mtext(cx, top + 52, desc, size=12.5, color=INK))
            f.append(line(cx, axis_y + 8, cx, top, color=col, sw=1.6))
            f.append(text(cx, axis_y - 16, year, size=13.5, bold=True, color=INK))

    f.append(fitbox(70, H - 54, 1120, 40,
                    "синє — оптичні витоки · червоне — суперечлива поява в механіці · зелене — математична зрілість",
                    size=13, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4))
    return render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── Фігура 5: дві різні «дії» — Мопертюї ∫p·ds проти Гамільтона ∫L·dt ─────────
def fig_two_actions():
    W, H = 1020, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дві несхожі величини на одне слово «дія»", size=18, bold=True))
    f.append(line(510, 58, 510, 388, color="#d6dde6", sw=1.4, dash="5,6"))

    # ── ліворуч: скорочена дія Мопертюї–Ейлера (форма шляху в просторі) ──
    f.append(text(255, 60, "Мопертюї й Ейлер (1744)", size=14.5, bold=True, color=POS))
    f.append(text(255, 80, "«скорочена» дія — лише форма шляху", size=12.5, color=MUTED))
    A, B = (95, 322), (430, 150)
    path = arc_path(A, B, 80)
    f.append(poly(path, color=INK, sw=2.8))
    f.append(circle(A[0], A[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(A[0] - 6, A[1] + 22, "A", size=13, bold=True))
    f.append(circle(B[0], B[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(B[0] + 14, B[1] - 4, "B", size=13, bold=True))
    for k in (9, 22, 35):
        px, py = path[k]; qx, qy = path[k + 4]
        dx, dy = qx - px, qy - py; m = math.hypot(dx, dy) or 1
        f.append(arrow(px, py, px + 44 * dx / m, py + 44 * dy / m, color=POS, sw=2.0))
    f.append(text(path[22][0] + 34, path[22][1] - 20, "p = m·v", size=12.5, italic=True, color=POS, anchor="start"))
    f.append(fitbox(70, 312, 372, 40, "W = ∫ p·ds = ∫ m·v·ds",
                    size=15, pad=8, fill="#fdecea", stroke=POS, sw=1.6, bold=True))
    f.append(fitbox(70, 364, 372, 44, "варіюють ФОРМУ шляху при сталій\nенергії — про час нічого не каже",
                    size=12.5, pad=7, fill="#f4f6f8", stroke=LINE, sw=1.3))

    # ── праворуч: повна дія Гамільтона (світова лінія в часі) ──
    f.append(text(765, 60, "Гамільтон (1834–35)", size=14.5, bold=True, color=FIELD))
    f.append(text(765, 80, "повна дія — шлях, розгорнутий у часі", size=12.5, color=MUTED))
    ox, oy = 590, 300
    f.append(arrow(ox, oy, 958, oy, color=MUTED, sw=1.6))
    f.append(text(953, oy + 18, "t (час)", size=12, color=MUTED, anchor="end"))
    f.append(arrow(ox, oy, ox, 108, color=MUTED, sw=1.6))
    f.append(text(ox - 8, 116, "x", size=12, color=MUTED, anchor="end"))
    wl = arc_path((ox + 6, oy - 8), (930, 148), 58)
    for k in range(3, 40, 5):
        xx, yy = wl[k]
        f.append(line(xx, yy, xx, oy, color="#cfe6d8", sw=1.3))
    f.append(poly(wl, color=INK, sw=2.8))
    f.append(circle(wl[0][0], wl[0][1], 5.5, fill=INK, stroke=INK, sw=1))
    f.append(circle(wl[-1][0], wl[-1][1], 5.5, fill=INK, stroke=INK, sw=1))
    f.append(line(ox + 6, oy, ox + 6, oy + 12, color=MUTED, sw=1.4))
    f.append(text(ox + 6, oy + 28, "t₁", size=12, italic=True, color=MUTED))
    f.append(line(930, oy, 930, oy + 12, color=MUTED, sw=1.4))
    f.append(text(930, oy + 28, "t₂", size=12, italic=True, color=MUTED))
    f.append(text(770, 250, "∫ L dt", size=14, italic=True, color=FIELD, anchor="middle"))
    f.append(fitbox(580, 312, 372, 40, "S = ∫ L·dt = ∫ (T − U)·dt",
                    size=15, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True))
    f.append(fitbox(580, 364, 372, 44, "варіюють шлях У ЧАСІ між двома\nмитями — це сучасний принцип δS = 0",
                    size=12.5, pad=7, fill="#f4f6f8", stroke=LINE, sw=1.3))
    return render(os.path.join(IMG, "two-actions.svg"), W, H, *f)


# ── Фігура: варіація шляху δq(t) із закріпленими кінцями ──────────────────────
def fig_variation():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Варіація шляху: справжня крива й сусідні — з тими самими кінцями",
                  size=16, bold=True))

    Ox, Oy, topY, rightX = 96, 400, 96, 848
    f.append(arrow(Ox, Oy, rightX, Oy, color=MUTED, sw=1.3))
    f.append(text(rightX + 6, Oy + 5, "t", size=14, italic=True, color=MUTED, anchor="start"))
    f.append(arrow(Ox, Oy, Ox, topY, color=MUTED, sw=1.3))
    f.append(text(Ox - 10, topY - 4, "q", size=14, italic=True, color=MUTED, anchor="end"))

    A = (176, 330); B = (786, 168)
    for (px, lab) in ((A[0], "a"), (B[0], "b")):
        f.append(line(px, Oy - 5, px, Oy + 5, color=MUTED, sw=1.2))
        f.append(text(px, Oy + 20, lab, size=13, italic=True, color=MUTED))

    true = arc_path(A, B, 52)
    vup = arc_path(A, B, 122)
    vdn = arc_path(A, B, -18)
    f.append(poly(vup, color="#b6bfca", sw=1.9, dash="7,5"))
    f.append(poly(vdn, color="#b6bfca", sw=1.9, dash="7,5"))
    f.append(poly(true, color=FIELD, sw=3.0))

    tx, ty = true[30]; ux, uy = vup[30]
    f.append(arrow(tx, ty, ux, uy, color=POS, sw=2.0))
    f.append(text(tx - 12, (ty + uy) / 2 + 4, "δq(t)", size=13, italic=True, color=POS, anchor="end"))

    f.append(circle(A[0], A[1], 6.5, fill=INK, stroke=INK, sw=1))
    f.append(circle(B[0], B[1], 6.5, fill=INK, stroke=INK, sw=1))
    f.append(text(A[0] - 6, A[1] + 26, "δq = 0", size=12, color=INK, anchor="middle"))
    f.append(text(B[0] + 10, B[1] - 12, "δq = 0", size=12, color=INK, anchor="start"))

    f.append(text(481, 112, "сусідній шлях  q + δq", size=12.5, color=MUTED))
    f.append(text(250, 352, "справжній шлях q(t):  δS = 0", size=12.5, bold=True, color=FIELD, anchor="start"))

    f.append(fitbox(130, 414, 640, 46,
                    "кінці приколоті: δq(a) = δq(b) = 0\n"
                    "умова δS = 0 виділяє справжню криву серед усіх сусідніх",
                    size=12.5, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4))
    return render(os.path.join(IMG, "variation.svg"), W, H, *f)


# ── Фігура: брахістохрона — найшвидший спуск є дугою циклоїди ─────────────────
def fig_brachistochrone():
    W, H = 860, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Брахістохрона: найшвидший з'їзд — циклоїда, а не пряма",
                  size=16, bold=True))

    Ax, Ay = 165, 108
    theta_max = 3.64
    r = 545.0 / (theta_max - math.sin(theta_max))
    N = 80
    cyc = []
    for k in range(N + 1):
        th = theta_max * k / N
        cyc.append((Ax + r * (th - math.sin(th)), Ay + r * (1 - math.cos(th))))
    B = cyc[-1]

    f.append(arrow(112, 92, 112, 166, color=MUTED, sw=1.8))
    f.append(text(120, 136, "g", size=14, italic=True, color=MUTED, anchor="start"))

    f.append(poly([(Ax, Ay), B], color="#b6bfca", sw=2.0, dash="8,6"))
    f.append(poly(cyc, color=FIELD, sw=3.2))

    f.append(circle(Ax, Ay, 7, fill=INK, stroke=INK, sw=1))
    f.append(text(Ax + 2, Ay - 12, "A — старт (спокій)", size=12.5, bold=True, color=INK, anchor="start"))
    f.append(circle(B[0], B[1], 7, fill=INK, stroke=INK, sw=1))
    f.append(text(B[0] + 12, B[1] + 6, "B — фініш", size=12.5, bold=True, color=INK, anchor="start"))

    mx, my = (Ax + B[0]) / 2, (Ay + B[1]) / 2
    f.append(text(mx + 10, my - 12, "пряма — коротша, але повільніша", size=12.5, color=MUTED, anchor="start"))
    f.append(text(cyc[58][0] - 6, cyc[58][1] + 28, "циклоїда — найшвидший спуск",
                  size=12.5, bold=True, color=FIELD, anchor="start"))

    f.append(fitbox(120, 420, 620, 46,
                    "мінімізуємо не довжину, а ЧАС   T = ∫ ds / v ;   розв'язок — дуга циклоїди\n"
                    "(слід точки на колесі, що котиться) — Йоганн Бернуллі, 1696",
                    size=12.5, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4))
    return render(os.path.join(IMG, "brachistochrone.svg"), W, H, *f)


# ══ proj-least-action: чисельна перевірка «справжній шлях мінімізує дію» ══════
T_P, G_P, M_P = 2.0, 9.8, 1.0        # час польоту (с), тяжіння (м/с²), маса (кг)


def _relax(N, snap_iters, seed=7):
    """Релаксація ламаної з N інтервалів градієнтним спуском по дискретній дії.
    Повертає {iter: [x_0..x_N]} для потрібних знімків."""
    dt = T_P / N
    x = [0.0] * (N + 1)
    r = seed
    for k in range(1, N):                         # безглуздий стартовий здогад
        r = (1103515245 * r + 12345) & 0x7fffffff
        x[k] = 3.0 + 5.0 * (r / 0x7fffffff - 0.5)
    snaps = {0: x[:]} if 0 in snap_iters else {}
    alpha = 0.35 * dt / M_P
    for it in range(1, max(snap_iters) + 1):
        nx = x[:]
        for j in range(1, N):
            d2 = x[j + 1] - 2 * x[j] + x[j - 1]   # друга різниця = прискорення·dt²
            nx[j] = x[j] - alpha * (-M_P * (d2 / dt + G_P * dt))   # x -= α·∂S/∂x
        x = nx
        if it in snap_iters:
            snaps[it] = x[:]
    return snaps


# ── Фігура proj-1: релаксація шляху до параболи ───────────────────────────────
def fig_path_relaxation():
    W, H = 920, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Релаксація: комп'ютер зсуває точки, доки дія не осяде", size=17, bold=True))

    L, R, Tp, Bt = 92, 660, 74, 402
    tmax, xmax = 2.0, 6.4

    def PX(t):
        return L + (t / tmax) * (R - L)

    def PY(x):
        return Bt - (x / xmax) * (Bt - Tp)

    f.append(arrow(L, Bt, R + 26, Bt, color=MUTED, sw=1.3))
    f.append(text(R + 32, Bt + 4, "t", size=13, italic=True, color=MUTED, anchor="start"))
    f.append(arrow(L, Bt, L, Tp - 14, color=MUTED, sw=1.3))
    f.append(text(L - 8, Tp - 4, "x  (висота)", size=12, color=MUTED, anchor="end"))
    f.append(text(L - 12, Bt + 4, "0", size=11, color=MUTED, anchor="end"))
    for tt in (0, 1, 2):
        f.append(line(PX(tt), Bt, PX(tt), Bt + 6, color=MUTED, sw=1.2))
        f.append(text(PX(tt), Bt + 22, "%g с" % tt, size=11, color=MUTED))

    N = 12
    snaps = _relax(N, [0, 2, 40000], seed=7)
    ts = [k * (T_P / N) for k in range(N + 1)]

    def draw(xs, color, sw, dash=None, dots=False, dotfill=FILL):
        pts = [(PX(ts[k]), PY(xs[k])) for k in range(N + 1)]
        f.append(poly(pts, color=color, sw=sw, dash=dash))
        if dots:
            for (px, py) in pts:
                f.append(circle(px, py, 3.6, fill=dotfill, stroke=color, sw=1.5))

    dense = [(PX(0.02 * i), PY(9.8 * (0.02 * i) - 0.5 * 9.8 * (0.02 * i) ** 2)) for i in range(101)]
    f.append(poly(dense, color=INK, sw=1.3, dash="2,4"))
    draw(snaps[0], "#aab4c0", 1.8, dash="6,5", dots=True, dotfill="#eef1f5")
    draw(snaps[2], "#d0902f", 2.2)
    draw(snaps[40000], FIELD, 3.0, dots=True, dotfill="#eef6ef")

    f.append(circle(PX(0), PY(0), 6, fill=INK, stroke=INK, sw=1))
    f.append(circle(PX(2), PY(0), 6, fill=INK, stroke=INK, sw=1))
    f.append(text(PX(0) + 2, Bt + 40, "старт", size=11, color=INK))
    f.append(text(PX(2), Bt + 40, "фініш", size=11, color=INK))

    lx, ly = R + 46, 150
    items = [("#aab4c0", "6,5", "початковий здогад", "#eef1f5", True),
             ("#d0902f", None, "проміжна ітерація", None, False),
             (FIELD, None, "збіглий шлях", "#eef6ef", True),
             (INK, "2,4", "точна парабола", None, False)]
    f.append(text(lx, ly - 26, "що на графіку:", size=12, bold=True, anchor="start"))
    for i, (col, dsh, lab, df, dot) in enumerate(items):
        yy = ly + i * 34
        f.append(line(lx, yy, lx + 34, yy, color=col, sw=2.6, dash=dsh))
        if dot:
            f.append(circle(lx + 17, yy, 3.4, fill=df, stroke=col, sw=1.4))
        f.append(text(lx + 44, yy + 4, lab, size=11.5, color=INK, anchor="start"))

    return render(os.path.join(IMG, "path-relaxation.svg"), W, H, *f)


# ── Фігура proj-2: дія одного вільного вузла — чаша з єдиним дном ──────────────
def fig_action_bowl():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Один вільний вузол — і дія стає чашею з єдиним дном", size=17, bold=True))

    L, R, Tp, Bt = 150, 700, 116, 410
    x1max = 9.8

    def SS(x1):
        return x1 * x1 - 9.8 * x1

    Slo, Shi = -28.0, 8.0

    def PX(x1):
        return L + (x1 / x1max) * (R - L)

    def PY(S):
        return Bt - (S - Slo) / (Shi - Slo) * (Bt - Tp)

    f.append(arrow(L, Bt + 6, L, Tp - 12, color=MUTED, sw=1.3))
    f.append(text(L - 10, Tp - 2, "S (дія)", size=12, color=MUTED, anchor="end"))
    f.append(arrow(L - 6, PY(0), R + 26, PY(0), color=MUTED, sw=1.3))
    f.append(text(R + 32, PY(0) + 4, "x₁", size=13, italic=True, color=MUTED, anchor="start"))
    for Sv in (0, -10, -20):
        f.append(line(L - 5, PY(Sv), L, PY(Sv), color=MUTED, sw=1.2))
        f.append(text(L - 12, PY(Sv) + 4, "%d" % Sv, size=11, color=MUTED, anchor="end"))
    f.append(text(PX(0) + 4, PY(0) - 10, "0", size=11, color=MUTED, anchor="start"))
    f.append(text(PX(9.8), PY(0) - 10, "9.8", size=11, color=MUTED))

    curve = [(PX(9.8 * i / 240), PY(SS(9.8 * i / 240))) for i in range(241)]
    f.append(poly(curve, color=FIELD, sw=3.2))

    xm = 4.9
    f.append(line(PX(xm), PY(0), PX(xm), PY(SS(xm)), color=MUTED, sw=1.2, dash="4,5"))
    f.append(circle(PX(xm), PY(SS(xm)), 6.5, fill="#eef6ef", stroke=FIELD, sw=2.4))
    f.append(text(PX(xm), PY(SS(xm)) + 26, "x₁ = 4.9 м", size=12.5, bold=True, color=FIELD))
    f.append(text(PX(xm), PY(SS(xm)) + 44, "дно — справжній апекс", size=11.5, color=FIELD))

    f.append(mtext(PX(1.4), 150, ["занизько:", "мало виграно на −U"], size=11.5, color=NEG, anchor="start"))
    f.append(arrow(PX(1.4) + 4, 162, PX(2.0), PY(SS(2.0)) - 6, color=NEG, sw=1.4))
    f.append(mtext(PX(8.4), 150, ["зависоко:", "½mẋ² ∝ x₁², задорого"], size=11.5, color=POS, anchor="end"))
    f.append(arrow(PX(8.4) - 4, 162, PX(7.8), PY(SS(7.8)) - 6, color=POS, sw=1.4))

    f.append(fitbox(160, 452, 540, 44,
                    "S(x₁) = x₁² − 9.8·x₁ — чиста парабола: похідна нульова рівно раз,\n"
                    "тож дно єдине, і градієнтному спуску нема де застрягти",
                    size=12, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4))
    return render(os.path.join(IMG, "action-bowl.svg"), W, H, *f)


# ── Фігура proj-3: збіжність дискретної дії до континууму зі зростанням N ─────
def fig_action_convergence():
    W, H = 820, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дрібніша сітка — точніша дія: збіжність до континууму", size=16.5, bold=True))

    data = [(2, -24.01), (4, -30.01), (8, -31.51), (16, -31.89),
            (50, -32.00), (100, -32.01), (500, -32.013), (2000, -32.013)]
    cont = -32.0133
    L, R, Tp, Bt = 96, 748, 86, 372
    Slo, Shi = -33.2, -23.0
    n = len(data)

    def PX(i):
        return L + i * (R - L) / (n - 1)

    def PY(S):
        return Bt - (S - Slo) / (Shi - Slo) * (Bt - Tp)

    f.append(arrow(L - 6, Bt, R + 24, Bt, color=MUTED, sw=1.3))
    f.append(text(R + 30, Bt + 4, "N", size=13, italic=True, color=MUTED, anchor="start"))
    f.append(arrow(L, Bt + 6, L, Tp - 12, color=MUTED, sw=1.3))
    f.append(text(L - 8, Tp - 2, "S (дія)", size=12, color=MUTED, anchor="end"))
    for Sv in (-24, -26, -28, -30, -32):
        f.append(line(L - 5, PY(Sv), L, PY(Sv), color=MUTED, sw=1.1))
        f.append(text(L - 12, PY(Sv) + 4, "%d" % Sv, size=11, color=MUTED, anchor="end"))

    f.append(line(L, PY(cont), R + 4, PY(cont), color=NEG, sw=1.8, dash="7,5"))
    f.append(text(R + 4, PY(cont) - 8, "континуум  −32.01", size=11.5, bold=True, color=NEG, anchor="end"))

    pts = [(PX(i), PY(S)) for i, (Nn, S) in enumerate(data)]
    f.append(poly(pts, color=FIELD, sw=2.6))
    for i, (Nn, S) in enumerate(data):
        f.append(circle(PX(i), PY(S), 5, fill="#eef6ef", stroke=FIELD, sw=2))
        f.append(text(PX(i), Bt + 22, str(Nn), size=11, color=INK))
        if Nn in (2, 4, 8, 16):
            f.append(text(PX(i), PY(S) - 12, "%.1f" % S, size=10.5, color=MUTED))

    f.append(text(PX(0) + 6, PY(-24.01) + 26, "N=2 — це трикутник", size=11.5, color=MUTED, anchor="start"))

    f.append(fitbox(80, 400, 660, 46,
                    "груба сітка завищує дію: кусково-пряма «зрізає» параболу;\n"
                    "з дрібнішим кроком Δt = T/N дискретна дія осідає на континуумні −32.01",
                    size=12, pad=8, fill="#f4f6f8", stroke=LINE, sw=1.4))
    return render(os.path.join(IMG, "action-convergence.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_path_selection(), fig_action_tradeoff(), fig_fermat(),
          fig_timeline(), fig_two_actions(),
          fig_variation(), fig_brachistochrone(),
          fig_path_relaxation(), fig_action_bowl(), fig_action_convergence()]
    print("written:")
    for p in ps:
        print("  ", p)
