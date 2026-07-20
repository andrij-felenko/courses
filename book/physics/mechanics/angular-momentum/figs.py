# -*- coding: utf-8 -*-
"""Фігури до теми «Момент імпульсу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, op=1.0):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, op, stroke, sw))


def right_angle(px, py, u, v, s=12, color=MUTED):
    """Квадратик прямого кута у точці (px,py) між напрямами u і v (одиничні)."""
    ax, ay = px + u[0] * s, py + u[1] * s
    bx, by = px + v[0] * s, py + v[1] * s
    cx, cy = ax + v[0] * s, ay + v[1] * s
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.2"/>' % (ax, ay, cx, cy, bx, by, color))


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=10):
    """Дуга-стрілка (коло) від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def ell_pt(cx, cy, rx, ry, t_deg):
    t = math.radians(t_deg)
    return (cx + rx * math.cos(t), cy + ry * math.sin(t))


def ell_arc_arrow(cx, cy, rx, ry, a0_deg, a1_deg, color=LINE, sw=2.6, head=11):
    """Дуга по еліпсу від a0 до a1 (0°=праворуч), зі стрілкою на кінці."""
    x0, y0 = ell_pt(cx, cy, rx, ry, a0_deg)
    x1, y1 = ell_pt(cx, cy, rx, ry, a1_deg)
    sweep = 0 if a1_deg > a0_deg else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, rx, ry, large, sweep, x1, y1, color, sw))
    # напрям дотичної в кінці (похідна параметризації)
    t1 = math.radians(a1_deg)
    dir_sign = 1 if a1_deg > a0_deg else -1
    tx = -rx * math.sin(t1) * dir_sign
    ty = ry * math.cos(t1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.3
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def out_of_plane(cx, cy, r=15, color=NEG):
    """Символ ⊙ — вектор із площини (до глядача)."""
    return (circle(cx, cy, r, fill="#eef2fb", stroke=color, sw=2.2)
            + circle(cx, cy, 2.6, fill=color, stroke=color, sw=1))


# ── Фігура 1: момент імпульсу точки — імпульс із плечем ───────────────────────
def fig_moment():
    W, H = 780, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Момент імпульсу точки — це імпульс, узятий із плечем",
                  size=17, bold=True))

    Ly = 210                       # висота прямої руху
    F = (150, Ly)                  # основа перпендикуляра (найближча точка лінії)
    O = (150, 360)                 # точка (вісь), відносно якої рахуємо
    P = (460, Ly)                  # частинка

    # лінія руху (від основи перпендикуляра праворуч)
    f.append(line(F[0], Ly, 700, Ly, color=INK, sw=2.2))
    f.append(text(650, Ly - 12, "лінія руху", size=12, color=MUTED, anchor="middle"))

    # частинка та її імпульс
    f.append(circle(P[0], P[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(arrow(P[0], P[1], P[0] + 150, P[1], color=POS, sw=3.2))
    f.append(text(P[0] + 78, P[1] - 12, "p = m·v", size=15, bold=True, color=POS,
                  anchor="middle"))

    # точка O
    f.append(circle(O[0], O[1], 8, fill=FILL, stroke=INK, sw=2))
    f.append(text(O[0] - 16, O[1] + 6, "O", size=14, bold=True, anchor="end"))

    # плече r⊥ — перпендикуляр з O на лінію
    f.append(line(O[0], O[1], F[0], F[1], color=NEG, sw=2.0, dash="6 5"))
    f.append(text(O[0] - 14, (O[1] + F[1]) / 2 + 4, "r⊥", size=15, italic=True,
                  color=NEG, anchor="end"))
    f.append(right_angle(F[0], F[1], (1, 0), (0, 1), s=13))

    # радіус-вектор r від O до частинки
    f.append(arrow(O[0], O[1], P[0], P[1], color=INK, sw=2.4))
    f.append(text((O[0] + P[0]) / 2 - 6, (O[1] + P[1]) / 2 - 12, "r", size=15,
                  italic=True, anchor="middle"))

    # момент імпульсу — з площини
    f.append(out_of_plane(632, 322, r=16, color=NEG))
    f.append(text(632, 322 + 40, "L (уздовж осі,", size=12, color=NEG))
    f.append(text(632, 322 + 56, "із площини)", size=12, color=NEG))

    b, w, h = textbox(W / 2, H - 30,
                      "L = r × p     |L| = m·v·r⊥     (плече r⊥ і швидкість сталі → L стале)",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "moment-of-momentum.svg"), W, H, *f)


# ── Фігура 2: фігуристка — J падає, ω росте, L=J·ω стале ──────────────────────
def fig_skater():
    W, H = 820, 490
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Складені руки зменшують J — і швидкість обертання росте",
                  size=17, bold=True))

    def skater(cx, arms_out):
        g = []
        hy = 108
        g.append(circle(cx, hy, 15, fill=FILL, stroke=INK, sw=2.4))     # голова
        g.append(line(cx, hy + 15, cx, 230, color=INK, sw=3.4))         # тулуб
        sh = 150                                                        # плечі
        if arms_out:
            g.append(line(cx, sh, cx - 96, 132, color=NEG, sw=3.6))
            g.append(line(cx, sh, cx + 96, 132, color=NEG, sw=3.6))
        else:
            g.append(line(cx, sh, cx - 24, 214, color=NEG, sw=3.6))
            g.append(line(cx, sh, cx + 24, 214, color=NEG, sw=3.6))
        g.append(line(cx, 230, cx - 22, 292, color=INK, sw=3.4))        # ноги
        g.append(line(cx, 230, cx + 22, 292, color=INK, sw=3.4))
        return g

    xL, xR = 200, 620
    f += skater(xL, True)
    f += skater(xR, False)
    f.append(text(xL, 74, "руки розкинуто", size=13, bold=True, color=MUTED))
    f.append(text(xR, 74, "руки притиснуто", size=13, bold=True, color=MUTED))

    # оберт: повільний зліва, швидкий справа
    f.append(arc_arrow(xL, 330, 40, 210, -20, color=FIELD, sw=2.6, head=10))
    f.append(text(xL, 388, "ω₁ мала", size=13, bold=True, color=FIELD))
    f.append(arc_arrow(xR, 330, 40, 250, -80, color=FIELD, sw=3.4, head=12))
    f.append(arc_arrow(xR, 330, 54, 250, -80, color=FIELD, sw=2.0, head=9))
    f.append(text(xR, 388, "ω₂ велика", size=13, bold=True, color=FIELD))

    # спільний L посередині
    f.append(arrow(330, 150, 490, 150, color=INK, sw=2.0))
    f.append(arrow(490, 150, 330, 150, color=INK, sw=2.0))
    f.append(text(W / 2, 132, "L = J·ω = 8.0  —  стале", size=14, bold=True))
    f.append(text(W / 2, 170, "×3.3", size=13, color=POS, bold=True))

    # значення під кожним
    b1, w1, h1 = textbox(xL, 428, "J₁ = 4.0 кг·м²\nω₁ = 2.0 рад/с", size=13, pad=9,
                         fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(xR, 428, "J₂ = 1.2 кг·м²\nω₂ ≈ 6.7 рад/с", size=13, pad=9,
                         fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b2)

    b, w, h = textbox(W / 2, H - 26,
                      "J₁·ω₁ = J₂·ω₂   →   ω₂ = 8.0 / 1.2 ≈ 6.7 рад/с",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "skater-spin.svg"), W, H, *f)


# ── Фігура 3: L — вектор уздовж осі; збереження застигає й напрям ─────────────
def fig_vector():
    W, H = 760, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Момент імпульсу — вектор уздовж осі; застигає й напрям",
                  size=17, bold=True))

    C = (300, 300)
    rx, ry = 130, 44
    # диск
    f.append(ellipse(C[0], C[1], rx, ry, fill="#eef2fb", stroke=INK, sw=1.8))
    # обертання диска
    f.append(ell_arc_arrow(C[0], C[1], rx - 10, ry - 6, 205, -18, color=FIELD, sw=2.8))
    f.append(text(C[0], C[1] + ry + 26, "обертання", size=13, color=FIELD, bold=True))

    # вісь та вектор L угору
    f.append(circle(C[0], C[1], 5, fill=INK, stroke=INK, sw=1))
    f.append(arrow(C[0], C[1], C[0], 152, color=NEG, sw=3.6))
    f.append(text(C[0] - 16, 168, "L", size=19, bold=True, color=NEG, anchor="end"))
    f.append(text(C[0] - 16, 190, "(уздовж осі)", size=12, color=NEG, anchor="end"))

    # спроба нахилити: пунктирна нахилена вісь + дуга-спроба
    f.append(line(C[0], C[1], 366, 168, color=MUTED, sw=1.6, dash="6 5"))
    f.append(arc_arrow(C[0], C[1], 150, 90, 72, color=POS, sw=2.2, head=9))
    f.append(text(384, 150, "✗", size=20, bold=True, color=POS, anchor="start"))

    # пояснювальна рамка
    b0, bw, bh = textbox(590, 250,
                         "щоб завалити вісь,\nтреба повернути L,\nа для цього — момент",
                         size=13, pad=11, fill="#fdecea", stroke=POS, sw=1.3, bold=False)
    f.append(b0)

    b, w, h = textbox(W / 2, H - 28,
                      "нема зовнішнього моменту → застигає ввесь вектор L: і довжина, і напрям",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "angular-momentum-vector.svg"), W, H, *f)


# ── Фігура 4: рівні площі Кеплера = збереження моменту імпульсу ───────────────
def fig_areas():
    W, H = 820, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Рівні площі за рівний час — це збереження моменту імпульсу",
                  size=17, bold=True))

    EC = (450, 250)
    rx, ry = 250, 168
    c = math.sqrt(rx * rx - ry * ry)
    S = (EC[0] - c, EC[1])          # Сонце у фокусі

    # орбіта
    f.append(ellipse(EC[0], EC[1], rx, ry, fill="none", stroke=INK, sw=1.8))

    def sector(t0, t1, step, col, tint):
        pts = [S]
        t = t0
        while t <= t1 + 1e-6:
            pts.append(ell_pt(EC[0], EC[1], rx, ry, t))
            t += step
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:]) + " Z"
        return ('<path d="%s" fill="%s" fill-opacity="0.30" stroke="%s" '
                'stroke-width="1.6"/>' % (d, tint, col))

    # ближній сектор (перигелій, ліворуч від Сонця) — широкий і короткий
    f.append(sector(150, 210, 10, FIELD, FIELD))
    # дальній сектор (афелій, праворуч) — вузький і довгий
    f.append(sector(-15, 15, 6, NEG, NEG))

    # Сонце
    for a in range(0, 360, 45):
        ar = math.radians(a)
        f.append(line(S[0] + 15 * math.cos(ar), S[1] + 15 * math.sin(ar),
                      S[0] + 23 * math.cos(ar), S[1] + 23 * math.sin(ar),
                      color=POS, sw=1.8))
    f.append(circle(S[0], S[1], 14, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(S[0], S[1] + 40, "Сонце", size=13, bold=True, color=POS))

    # планета й швидкості
    Pp = ell_pt(EC[0], EC[1], rx, ry, 180)        # перигелій
    Pa = ell_pt(EC[0], EC[1], rx, ry, 0)          # афелій
    f.append(circle(Pp[0], Pp[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(circle(Pa[0], Pa[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(arrow(Pp[0], Pp[1], Pp[0], Pp[1] - 84, color=POS, sw=3.0))
    f.append(text(Pp[0] - 10, Pp[1] - 92, "v велика", size=12, bold=True, color=POS,
                  anchor="end"))
    f.append(arrow(Pa[0], Pa[1], Pa[0], Pa[1] - 36, color=NEG, sw=2.6))
    f.append(text(Pa[0] + 10, Pa[1] - 44, "v мала", size=12, bold=True, color=NEG,
                  anchor="start"))

    f.append(text(S[0] - 18, 150, "мала r → швидко", size=12, color=FIELD, anchor="middle"))
    f.append(text(Pa[0] - 10, 358, "велика r → повільно", size=12, color=NEG, anchor="middle"))

    b, w, h = textbox(W / 2, H - 26,
                      "m·r²·θ̇ = стале   —   ближче до Сонця (мале r) означає більшу швидкість",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "equal-areas.svg"), W, H, *f)


# ── Фігура 5: Ньютонів доказ рівних площ (полігон з поштовхами в центр) ───────
def fig_newton():
    W, H = 880, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Ньютонів доказ: поштовх завжди в центр робить площі рівними",
                  size=17, bold=True))

    S = (440, 490)                 # центр сили (Сонце)
    A = (130, 258)
    B = (320, 198)
    c = (510, 138)                 # куди полетіло б без сили (B + AB)
    C = (548, 231)                 # справжня наступна точка (cC ∥ SB)

    def poly(pts, fill, op, stroke, sw=1.6):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:]) + " Z"
        return ('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                'stroke-width="%.1f"/>' % (d, fill, op, stroke, sw))

    # дві рівновеликі заметені площі
    f.append(poly([S, A, B], FIELD, 0.22, FIELD))
    f.append(poly([S, B, C], NEG, 0.16, NEG))

    # радіуси до центра
    for P in (A, B, C):
        f.append(line(S[0], S[1], P[0], P[1], color=MUTED, sw=1.3))
    f.append(line(S[0], S[1], c[0], c[1], color=MUTED, sw=1.1, dash="4 4"))

    # справжній шлях A→B→C
    f.append(line(A[0], A[1], B[0], B[1], color=INK, sw=2.6))
    f.append(line(B[0], B[1], C[0], C[1], color=INK, sw=2.6))
    # без сили B→c та зсув поштовхом c→C
    f.append(line(B[0], B[1], c[0], c[1], color=MUTED, sw=2.0, dash="6 5"))
    f.append(line(c[0], c[1], C[0], C[1], color=POS, sw=2.0, dash="5 4"))

    # поштовх у B, спрямований у центр S
    ux, uy = S[0] - B[0], S[1] - B[1]
    Ln = math.hypot(ux, uy); ux, uy = ux / Ln, uy / Ln
    f.append(arrow(B[0], B[1], B[0] + ux * 58, B[1] + uy * 58, color=POS, sw=3.2))
    f.append(text(362, 258, "поштовх до S", size=11, color=POS, anchor="start"))

    # Сонце — центр сили
    for a in range(0, 360, 45):
        ar = math.radians(a)
        f.append(line(S[0] + 14 * math.cos(ar), S[1] + 14 * math.sin(ar),
                      S[0] + 22 * math.cos(ar), S[1] + 22 * math.sin(ar),
                      color=POS, sw=1.8))
    f.append(circle(S[0], S[1], 13, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(470, 500, "S — центр сили", size=13, bold=True, color=POS, anchor="start"))

    # точки й підписи
    for (P, lab, ax, ay, anc) in [
            (A, "A", -18, 6, "end"),
            (B, "B", -16, 22, "end"),
            (C, "C", 16, 6, "start"),
            (c, "c", 15, -6, "start")]:
        f.append(circle(P[0], P[1], 5, fill=INK, stroke=INK, sw=1))
        f.append(text(P[0] + ax, P[1] + ay, lab, size=15, bold=True, anchor=anc))

    # ключові факти доказу
    f.append(text(452, 112, "без сили →", size=11, color=MUTED, anchor="start"))
    f.append(text(346, 118, "AB = Bc", size=14, bold=True, color=MUTED, anchor="middle"))
    f.append(text(346, 136, "(рівні часи — рівні кроки)", size=10.5, color=MUTED, anchor="middle"))
    f.append(text(636, 150, "cC ∥ SB", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(636, 168, "(поштовх у центр)", size=10.5, color=POS, anchor="start"))

    # мітки рівних площ у трикутниках
    f.append(text(298, 322, "площа", size=13, bold=True, color=FIELD, anchor="middle"))
    f.append(text(444, 324, "= площа", size=13, bold=True, color=NEG, anchor="middle"))

    b, w, h = textbox(W / 2, H - 28,
                      "сила завжди в центр S  →  SAB = SBc = SBC  →  рівні площі за рівні часи",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "newton-polygon.svg"), W, H, *f)


# ── Фігура 6: сходинки поняття — від рівних площ Кеплера до назви Ренкіна ──────
def fig_ladder():
    W, H = 900, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Сходинки одного поняття: від правила Кеплера до назви",
                  size=17, bold=True))

    rows = [
        ("1609 · Кеплер (нім.)\nрівні площі — збережене число ще без назви й без причини",
         "#eef2fb", NEG),
        ("1687 · Ньютон (англ.)\nпричина: сила в центр не має плеча → площі рівні",
         "#eef6ef", FIELD),
        ("1744–1746 · Бернуллі, Ойлер, д'Арсі\n«момент обертального руху», «принцип площ» — для цілих систем",
         FILL, MUTED),
        ("1799–1803 · Лаплас, Пуансо\nнапрямлений відрізок уздовж осі — момент стає вектором",
         "#fdecea", POS),
        ("1858 · Ренкін (шотл.)\nсучасне означення й сама назва «angular momentum»",
         "#f2ecf7", "#7d3c98"),
    ]

    cx, cy0, pitch = 460, 108, 88
    for i, (s, fill, stroke) in enumerate(rows):
        cy = cy0 + i * pitch
        b, w, h = textbox(cx, cy, s, size=13, pad=11, fill=fill, stroke=stroke,
                          sw=1.6, bold=False)
        f.append(b)
        if i < len(rows) - 1:
            f.append(arrow(cx, cy + 31, cx, cy + pitch - 31, color=MUTED, sw=2.0))

    b, w, h = textbox(W / 2, H - 34,
                      "закон збереження (площі) помітили на ~150 років раніше, ніж поняттю дали ім'я й вектор",
                      size=13, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "concept-ladder.svg"), W, H, *f)


def _sqbracket(x, y_top, y_bot, side="left", color=INK, sw=2.2, tick=9):
    """Квадратна дужка (вертикальна лінія + верхній/нижній зубчик)."""
    d = tick if side == "left" else -tick
    return (line(x, y_top, x, y_bot, color=color, sw=sw)
            + line(x, y_top, x + d, y_top, color=color, sw=sw)
            + line(x, y_bot, x + d, y_bot, color=color, sw=sw))


def _colvec(cx, cy, labels, color=INK, size=17, gap=34):
    """Стовпчик-вектор у квадратних дужках, центр (cx,cy)."""
    g = []
    n = len(labels)
    top = cy - (n - 1) * gap / 2 - 16
    bot = cy + (n - 1) * gap / 2 + 16
    g.append(_sqbracket(cx - 24, top, bot, "left", color=color))
    g.append(_sqbracket(cx + 24, top, bot, "right", color=color))
    for i, lab in enumerate(labels):
        y = cy - (n - 1) * gap / 2 + i * gap
        g.append(text(cx, y + size * 0.35, lab, size=size, bold=True, color=color))
    return "".join(g)


# ── Фігура: тензор інерції — машина, що обертає ω в L ──────────────────────────
def fig_inertia_tensor():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тензор інерції: L = I·ω — вектор ω обертає матриця, не число",
                  size=17, bold=True))

    # ── ліворуч: тіло з трьома головними осями ──
    Cb = (150, 250)
    f.append(ellipse(Cb[0], Cb[1], 66, 46, fill="#eef2fb", stroke=INK, sw=1.8))
    f.append(arrow(Cb[0], Cb[1], Cb[0] + 108, Cb[1] + 16, color=FIELD, sw=2.6))
    f.append(text(Cb[0] + 122, Cb[1] + 34, "e₁, I₁", size=13, bold=True, color=FIELD,
                  anchor="middle"))
    f.append(arrow(Cb[0], Cb[1], Cb[0], Cb[1] - 100, color=FIELD, sw=2.6))
    f.append(text(Cb[0], Cb[1] - 110, "e₂, I₂", size=13, bold=True, color=FIELD))
    f.append(arrow(Cb[0], Cb[1], Cb[0] - 84, Cb[1] + 62, color=FIELD, sw=2.6))
    f.append(text(Cb[0] - 98, Cb[1] + 80, "e₃, I₃", size=13, bold=True, color=FIELD,
                  anchor="middle"))
    f.append(circle(Cb[0], Cb[1], 4, fill=INK, stroke=INK, sw=1))
    f.append(text(Cb[0], 384, "головні осі тіла:", size=13, bold=True, color=MUTED))
    f.append(text(Cb[0], 404, "I діагональна → L ∥ ω", size=13, color=MUTED))

    # ── праворуч: рівняння L = I·ω ──
    cy = 232
    f.append(_colvec(372, cy, ["Lx", "Ly", "Lz"], color=NEG))
    f.append(text(424, cy + 7, "=", size=26, bold=True))

    cw, ch = 64, 44
    cols = [488, 552, 616]
    rows = [cy - ch, cy, cy + ch]
    labels = [["Ixx", "Ixy", "Ixz"],
              ["Iyx", "Iyy", "Iyz"],
              ["Izx", "Izy", "Izz"]]
    for ri, ry in enumerate(rows):
        for ci, cxx in enumerate(cols):
            diag = (ri == ci)
            fill = "#eaf6ee" if diag else "#f7f8fa"
            f.append(rect(cxx - cw / 2, ry - ch / 2, cw, ch,
                          fill=fill, stroke="#d7dbe0", sw=1.0, rx=4))
            f.append(text(cxx, ry + 5, labels[ri][ci], size=15, bold=diag,
                          color=(FIELD if diag else INK)))
    mL = cols[0] - cw / 2 - 6
    mR = cols[-1] + cw / 2 + 6
    f.append(_sqbracket(mL, rows[0] - ch / 2 - 4, rows[-1] + ch / 2 + 4, "left"))
    f.append(_sqbracket(mR, rows[0] - ch / 2 - 4, rows[-1] + ch / 2 + 4, "right"))

    f.append(text(mR + 26, cy + 7, "·", size=26, bold=True))
    f.append(_colvec(mR + 70, cy, ["ωx", "ωy", "ωz"], color=INK))

    f.append(text(552, 356, "діагональ — моменти інерції", size=12.5, color=FIELD,
                  bold=True))
    f.append(text(552, 376, "поза нею — добутки інерції", size=12.5, color=MUTED))

    b, w, h = textbox(W / 2, H - 26,
                      "добутки інерції = 0   ⟺   вісь головна   ⟺   L = I·ω ∥ ω",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "inertia-tensor.svg"), W, H, *f)


# ── Фігура: перекошена гантеля — L не паралельний до ω ────────────────────────
def fig_l_not_parallel():
    W, H = 820, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Розкручена повз головну вісь: L відхиляється від осі ω",
                  size=17, bold=True))

    O = (400, 315)
    th = math.radians(35)
    Lr = 155
    ux, uy = math.sin(th), -math.cos(th)             # напрям стрижня (екран)
    m1 = (O[0] + Lr * ux, O[1] + Lr * uy)            # верхня маса
    m2 = (O[0] - Lr * ux, O[1] - Lr * uy)            # нижня маса

    # вісь обертання (вертикаль) + вектор ω
    f.append(line(O[0], 118, O[0], 470, color=MUTED, sw=1.4, dash="6 6"))
    f.append(arrow(O[0], O[1], O[0], 138, color=FIELD, sw=3.4))
    f.append(text(O[0] + 14, 150, "ω", size=19, bold=True, color=FIELD, anchor="start"))
    f.append(text(O[0] + 14, 170, "(вісь)", size=12, color=FIELD, anchor="start"))

    # конус, що його замітає кінець L (натяк)
    f.append(ellipse(O[0], 231, 123, 19, fill="none", stroke=MUTED, sw=1.3))

    # стрижень і маси
    f.append(line(m1[0], m1[1], m2[0], m2[1], color=INK, sw=3.2))
    f.append(circle(m1[0], m1[1], 11, fill=INK, stroke=INK, sw=1))
    f.append(circle(m2[0], m2[1], 11, fill=INK, stroke=INK, sw=1))
    f.append(text(m1[0] + 20, m1[1] + 5, "m", size=15, italic=True, anchor="start"))
    f.append(text(m2[0] - 20, m2[1] + 5, "m", size=15, italic=True, anchor="end"))

    # плече ρ до осі (для верхньої маси)
    f.append(line(m1[0], m1[1], O[0], m1[1], color=NEG, sw=1.6, dash="5 4"))
    f.append(right_angle(O[0], m1[1], (1, 0), (0, 1), s=11))
    f.append(text((m1[0] + O[0]) / 2, m1[1] - 10, "ρ = a·sinθ", size=12, italic=True,
                  color=NEG, anchor="middle"))

    # кут θ між віссю і стрижнем
    f.append('<path d="M %.1f %.1f A 44 44 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.4"/>'
             % (O[0], O[1] - 44, O[0] + 44 * ux, O[1] + 44 * uy, MUTED))
    f.append(text(O[0] + 27, O[1] - 30, "θ", size=15, italic=True, bold=True))

    # вектор L — перпендикуляр до стрижня, відхилений від осі
    lx, ly = -math.cos(th), -math.sin(th)            # напрям L (екран)
    Le = (O[0] + 150 * lx, O[1] + 150 * ly)
    f.append(arrow(O[0], O[1], Le[0], Le[1], color=NEG, sw=3.6))
    f.append(text(Le[0] - 8, Le[1] - 12, "L", size=20, bold=True, color=NEG, anchor="end"))
    # прямий кут між L і стрижнем
    f.append(right_angle(O[0], O[1], (lx, ly), (ux, uy), s=13))

    b, w, h = textbox(W / 2, H - 28,
                      "L ⊥ стрижня. Осьова частка = J·ω; поперечна обертається з тілом → потрібен момент.",
                      size=13.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "l-not-parallel.svg"), W, H, *f)


# ── Фігура (proj): три головні осі — перекидає лише проміжна ──────────────────
def fig_dz_axes():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три головні осі телефона — перекидає лише проміжна",
                  size=17, bold=True))

    cx, cy = 330, 310
    a, b, c = 82, 150, 22          # пів-ширина(w), пів-висота(h), пів-товщина(t)

    def P(x, y, z):                # x=ширина, y=висота, z=товщина(глибина)
        return (cx + x + 0.55 * z, cy - y - 0.42 * z)

    def face(pts, fill, op=1.0):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:]) + " Z"
        return ('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                'stroke-width="1.6"/>' % (d, fill, op, INK))

    back = [P(-a, -b, -c), P(a, -b, -c), P(a, b, -c), P(-a, b, -c)]
    front = [P(-a, -b, c), P(a, -b, c), P(a, b, c), P(-a, b, c)]
    top = [P(-a, b, -c), P(a, b, -c), P(a, b, c), P(-a, b, c)]
    side = [P(a, -b, -c), P(a, b, -c), P(a, b, c), P(a, -b, c)]
    f.append(face(back, "#e7ecf5"))
    f.append(face(top, "#dce4f0"))
    f.append(face(side, "#d3ddec"))
    f.append(face(front, "#eef2fb", op=0.92))

    # осі крізь центр
    f.append(arrow(*P(0, 0, 0), *P(0, b + 78, 0), color=INK, sw=3.0))     # вісь 1 (довга)
    f.append(arrow(*P(0, 0, 0), *P(0, 0, 210), color=NEG, sw=3.0))        # вісь 3 (товщина)
    f.append(arrow(*P(0, 0, 0), *P(a + 120, 0, 0), color=POS, sw=3.4))    # вісь 2 (ширина)
    px2, py2 = P(a + 62, 0, 0)
    f.append(arc_arrow(px2, py2, 34, 60, 300, color=POS, sw=2.4, head=10))

    b1, _, _ = textbox(330, 92, "вісь 1 · довга · I₁ найменший\n«свердло» · стійка",
                       size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b1)
    b3, _, _ = textbox(690, 150, "вісь 3 · товщина · I₃ найбільший\n«тарілка» · стійка",
                       size=13, pad=10, fill="#eef2fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b3)
    b2, _, _ = textbox(720, 330, "вісь 2 · ширина · I₂ проміжний\nПЕРЕКИД · нестійка",
                       size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.6, bold=True)
    f.append(b2)

    bc, _, _ = textbox(W / 2, H - 30,
                       "I₁ < I₂ < I₃   —   найбільша й найменша осі обступають проміжну; коверзує саме вона",
                       size=14, pad=11, fill=FILL, stroke=MUTED, sw=1.3, bold=True)
    f.append(bc)
    return render(os.path.join(IMG, "dzhanibekov-axes.svg"), W, H, *f)


# ── Фігура (proj): полодії на сфері — центри проти сідла ──────────────────────
def fig_polhode():
    W, H = 840, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Полодії на сфері моменту: петлі-центри проти хреста-сідла",
                  size=17, bold=True))

    C = (300, 300)
    R = 205
    f.append(circle(C[0], C[1], R, fill="#f7f9fc", stroke=INK, sw=1.8))
    f.append(ellipse(C[0], C[1], R, R * 0.34, fill="none", stroke=MUTED, sw=1.0))
    f.append(ellipse(C[0], C[1], R * 0.34, R, fill="none", stroke=MUTED, sw=1.0))

    # полюси крайніх осей: ліво/право = вісь 1 (найменша), верх/низ = вісь 3 (найбільша)
    poles = [(-1, 0, "1"), (1, 0, "1"), (0, -1, "3"), (0, 1, "3")]
    for sx, sy, lab in poles:
        px, py = C[0] + sx * (R - 46), C[1] + sy * (R - 46)
        for rr in (24, 40):
            f.append(ellipse(px, py, rr * (0.7 if sy == 0 else 1.0),
                             rr * (1.0 if sy == 0 else 0.7),
                             fill="none",
                             stroke=(NEG if lab == "1" else FIELD), sw=1.8))
        col = NEG if lab == "1" else FIELD
        f.append(circle(px, py, 5, fill=col, stroke=col, sw=1))

    # сепаратриса — хрест по діагоналях крізь центр (полюс осі 2, до глядача)
    d = R * 0.90 * 0.71
    f.append(line(C[0] - d, C[1] - d, C[0] + d, C[1] + d, color=POS, sw=3.0))
    f.append(line(C[0] - d, C[1] + d, C[0] + d, C[1] - d, color=POS, sw=3.0))
    f.append(out_of_plane(C[0], C[1], r=15, color=POS))

    f.append(text(C[0] + R - 44, C[1] - 54, "вісь 1", size=12, bold=True, color=NEG))
    f.append(text(C[0] + 6, C[1] - R + 22, "вісь 3", size=12, bold=True, color=FIELD))

    b2, _, _ = textbox(650, 150, "вісь 2 (проміжна)\nдивиться на глядача\nсідло — хрест ✕",
                       size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.5, bold=True)
    f.append(b2)
    bc0, _, _ = textbox(650, 320,
                        "петлі навколо осей\n1 і 3 — стійкі центри:\nточка лишається біля осі",
                        size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=False)
    f.append(bc0)

    bc, _, _ = textbox(W / 2, H - 28,
                       "траєкторія біля сідла сповзає геть і обходить сферу до протилежного полюса — це перекид",
                       size=14, pad=11, fill=FILL, stroke=MUTED, sw=1.3, bold=True)
    f.append(bc)
    return render(os.path.join(IMG, "polhode-separatrix.svg"), W, H, *f)


# ── Фігура (proj): часовий ряд ω та сталість інваріантів (реальний RK4) ───────
def _polyline(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def fig_timeseries():
    m = 0.170
    tt_, ww_, hh_ = 0.008, 0.070, 0.150
    I1 = m / 12 * (tt_ * tt_ + ww_ * ww_)
    I2 = m / 12 * (tt_ * tt_ + hh_ * hh_)
    I3 = m / 12 * (ww_ * ww_ + hh_ * hh_)

    def rhs(o):
        return [(I2 - I3) * o[1] * o[2] / I1,
                (I3 - I1) * o[2] * o[0] / I2,
                (I1 - I2) * o[0] * o[1] / I3]

    def rk4(o, dt):
        k1 = rhs(o)
        k2 = rhs([o[i] + 0.5 * dt * k1[i] for i in range(3)])
        k3 = rhs([o[i] + 0.5 * dt * k2[i] for i in range(3)])
        k4 = rhs([o[i] + dt * k3[i] for i in range(3)])
        return [o[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3)]

    def Lm(o):
        return math.sqrt((I1 * o[0]) ** 2 + (I2 * o[1]) ** 2 + (I3 * o[2]) ** 2)

    def E2(o):
        return I1 * o[0] ** 2 + I2 * o[1] ** 2 + I3 * o[2] ** 2

    o = [0.02, 10.0, 0.0]
    dt = 1e-3
    N = 4000
    L0, E0 = Lm(o), E2(o)
    ts, W1, W2, W3, RL, RE = [], [], [], [], [], []
    for k in range(N + 1):
        if k % 4 == 0:
            ts.append(k * dt)
            W1.append(o[0]); W2.append(o[1]); W3.append(o[2])
            RL.append(Lm(o) / L0); RE.append(E2(o) / E0)
        o = rk4(o, dt)

    W, H = 880, 650
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "ω перекидається, а |L| і 2T стоять — реальний вивід інтегратора",
                  size=17, bold=True))

    Tmax = ts[-1]
    px, py, pw, ph = 95, 66, 690, 250
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.3))

    def x_of(t):
        return px + pw * (t / Tmax)

    wlo, whi = -11.5, 11.5

    def y_top(v):
        return py + ph * (whi - v) / (whi - wlo)

    for v in (-10, 0, 10):
        yy = y_top(v)
        f.append(line(px, yy, px + pw, yy, color="#e3e7ee" if v else MUTED,
                      sw=1.4 if v == 0 else 1.0))
        f.append(text(px - 10, yy + 4, "%d" % v, size=12, color=MUTED, anchor="end"))
    for tk in range(0, int(Tmax) + 1):
        f.append(line(x_of(tk), py + ph, x_of(tk), py + ph + 5, color=MUTED, sw=1.0))
        f.append(text(x_of(tk), py + ph + 20, "%d" % tk, size=12, color=MUTED))
    f.append(text(px + pw / 2, py + ph + 40, "час t, с", size=13, color=INK))
    f.append(text(px - 60, py + ph / 2, "ω, рад/с", size=13, color=INK))

    f.append(_polyline([(x_of(ts[i]), y_top(W1[i])) for i in range(len(ts))], POS, sw=2.0))
    f.append(_polyline([(x_of(ts[i]), y_top(W3[i])) for i in range(len(ts))], NEG, sw=2.0))
    f.append(_polyline([(x_of(ts[i]), y_top(W2[i])) for i in range(len(ts))], INK, sw=3.0))

    qx, qy, qw, qh = 95, 410, 690, 130
    f.append(rect(qx, qy, qw, qh, fill="#ffffff", stroke=MUTED, sw=1.3))
    rlo, rhi = 0.9999, 1.0001

    def y_bot(v):
        return qy + qh * (rhi - v) / (rhi - rlo)

    for v, lab in ((1.0001, "1.0001"), (1.0, "1.0000"), (0.9999, "0.9999")):
        yy = y_bot(v)
        f.append(line(qx, yy, qx + qw, yy, color="#e3e7ee" if v != 1.0 else MUTED,
                      sw=1.0 if v != 1.0 else 1.3))
        f.append(text(qx - 10, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    for tk in range(0, int(Tmax) + 1):
        f.append(text(x_of(tk), qy + qh + 20, "%d" % tk, size=12, color=MUTED))
    f.append(text(qx + qw / 2, qy + qh + 38, "час t, с", size=13, color=INK))

    f.append(_polyline([(x_of(ts[i]), y_bot(RL[i])) for i in range(len(ts))], NEG, sw=2.6))
    f.append(_polyline([(x_of(ts[i]), y_bot(RE[i])) for i in range(len(ts))], FIELD,
                       sw=2.0, dash="7 5"))
    f.append(text(qx + 12, qy + 22, "|L|/L₀  та  2T/2T₀  —  дрейф < 10⁻¹¹ (рівні лінії)",
                  size=12, color=INK, anchor="start", bold=True))

    # легенда — окремим рядком під панелями, щоб криві її не перетинали
    yL = 616
    f.append(line(230, yL, 258, yL, color=INK, sw=3.0))
    f.append(text(264, yL + 4, "ω₂ (спін навколо осі 2, перекид)", size=12, color=INK,
                  anchor="start"))
    f.append(line(560, yL, 588, yL, color=POS, sw=2.0))
    f.append(text(594, yL + 4, "ω₁", size=12, color=POS, anchor="start"))
    f.append(line(624, yL, 652, yL, color=NEG, sw=2.0))
    f.append(text(658, yL + 4, "ω₃", size=12, color=NEG, anchor="start"))

    return render(os.path.join(IMG, "omega-timeseries.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_moment(), fig_skater(), fig_vector(), fig_areas(),
          fig_newton(), fig_ladder(),
          fig_inertia_tensor(), fig_l_not_parallel(),
          fig_dz_axes(), fig_polhode(), fig_timeseries()]
    print("written:")
    for p in ps:
        print("  ", p)
