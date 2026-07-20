# -*- coding: utf-8 -*-
"""Фігури до статті «Перший закон Ньютона». Запуск із теки теми: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def arrow_c(x1, y1, x2, y2, color=INK, sw=2.4, hs=10, dash=None):
    """Стрілка суцільним кольором: шафт (можна пунктир) + залитий трикутник-вістря."""
    ang = math.atan2(y2 - y1, x2 - x1)
    ax = x2 - hs * math.cos(ang - 0.5)
    ay = y2 - hs * math.sin(ang - 0.5)
    bx = x2 - hs * math.cos(ang + 0.5)
    by = y2 - hs * math.sin(ang + 0.5)
    shaft = line(x1, y1, x2, y2, color=color, sw=sw, dash=dash)
    head = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
            % (x2, y2, ax, ay, bx, by, color))
    return shaft + head


# ── Фігура 1: уявний дослід Ґалілея ─────────────────────────────────────────
def fig_inclined(path):
    W, H, Hh = 760, 580, 70
    f = []
    # (baseline_y, end_x або None для рівної площини, підпис, чи перший рядок)
    rows = [(150, 250, "близько", True),
            (320, 470, "далі", False),
            (490, None, "без кінця", False)]
    for yb, ex, lab, first in rows:
        top = yb - Hh
        Ax, Ay, Vx, Vy = 70, top, 150, yb
        f.append(line(Ax, Ay, Vx, Vy, color=LINE, sw=3))          # лівий (пусковий) схил
        if ex is not None:
            f.append(line(Vx, Vy, ex, top, color=LINE, sw=3))     # правий схил
            f.append(line(Ax, top, ex, top, color=MUTED, sw=1.2, dash="5,5"))  # висота старту
            f.append(circle(ex, top - 9, 9, fill="#eaf0fd", stroke=NEG, sw=2))  # кулька в кінці
            f.append(text(ex + 18, top - 3, lab, size=15, color=INK, anchor="start", bold=True))
        else:
            Fx = 560
            f.append(line(Vx, Vy, Fx, yb, color=LINE, sw=3))       # рівна площина
            f.append(arrow_c(Fx, yb, 690, yb, INK, sw=3, hs=12))   # рух без кінця
            f.append(line(Ax, top, 690, top, color=MUTED, sw=1.2, dash="5,5"))
            f.append(text(150, top - 9, "висота старту — недосяжна", size=13,
                          color=MUTED, anchor="start"))
            f.append(circle(Fx - 40, yb - 9, 9, fill="#eaf0fd", stroke=NEG, sw=2))
            f.append(text(612, yb - 15, lab, size=15, color=INK, anchor="middle", bold=True))
        if first:
            f.append(circle(Ax, top - 9, 9, fill="#eaf0fd", stroke=NEG, sw=2))
            f.append(text(Ax, top - 24, "старт", size=13, color=MUTED, anchor="middle"))
            f.append(text(160, top - 11, "та сама висота", size=13, color=MUTED, anchor="middle"))
    render(path, W, H, *f, title="Уявний дослід Ґалілея")


# ── Фігура 2: що робить сила з рухом ────────────────────────────────────────
def fig_free_body(path):
    W, H = 760, 320
    f = [line(380, 48, 380, 288, color="#d0d5db", sw=1.2)]        # роздільник панелей
    # Панель А — немає сили
    f.append(text(200, 60, "Немає сили", size=16, color=INK, anchor="middle", bold=True))
    yA = 178
    xs = [70, 135, 200, 265]
    for i, x in enumerate(xs):
        last = (i == len(xs) - 1)
        f.append(circle(x, yA, 8, fill=("#eaf0fd" if last else "#eef1f4"),
                        stroke=(NEG if last else MUTED), sw=1.8))
    f.append(arrow_c(273, yA, 332, yA, FIELD, sw=2.6, hs=10))     # швидкість
    f.append(text(302, yA - 12, "v", size=16, color=FIELD, anchor="middle", bold=True, italic=True))
    f.append(line(332, yA, 364, yA, color=MUTED, sw=1.2, dash="4,4"))   # …так само далі
    f.append(text(200, 272, "рівно і прямо — однакові кроки за однаковий час",
                  size=13, color=MUTED, anchor="middle"))
    # Панель B — є сила
    f.append(text(575, 60, "Є сила", size=16, color=INK, anchor="middle", bold=True))
    pts = [(440, 118), (492, 122), (535, 136), (568, 160), (590, 192), (602, 226)]
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=INK, sw=2.6))
    for idx in (0, 2, 5):
        f.append(circle(pts[idx][0], pts[idx][1], 8, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(arrow_c(440, 118, 486, 120, FIELD, sw=2.4, hs=9))    # v на початку
    f.append(text(460, 108, "v", size=14, color=FIELD, anchor="middle", bold=True, italic=True))
    f.append(arrow_c(602, 226, 618, 256, FIELD, sw=2.4, hs=9))    # v у кінці (завернула)
    f.append(text(628, 250, "v", size=14, color=FIELD, anchor="middle", bold=True, italic=True))
    f.append(arrow_c(548, 118, 548, 166, POS, sw=2.8, hs=10))     # сила в бік увігнутості
    f.append(text(548, 108, "F", size=15, color=POS, anchor="middle", bold=True, italic=True))
    f.append(text(575, 272, "сила завертає рух — швидкість міняє напрям",
                  size=13, color=MUTED, anchor="middle"))
    render(path, W, H, *f, title="Що робить сила з рухом")


# ── Фігура 3: один м'яч у двох системах відліку ─────────────────────────────
def draw_bus(x, y, w, h):
    s = [rect(x, y, w, h, fill="#eef1f4", stroke=LINE, sw=2, rx=12)]
    s.append(circle(x + w * 0.22, y + h, 13, fill="#333333", stroke="#111111", sw=1))
    s.append(circle(x + w * 0.80, y + h, 13, fill="#333333", stroke="#111111", sw=1))
    return "".join(s)


def fig_bus(path):
    W, H = 780, 340
    f = [line(395, 44, 395, 312, color="#d0d5db", sw=1.2)]
    # Панель А — погляд із землі
    f.append(text(200, 58, "Погляд із землі", size=16, color=INK, anchor="middle", bold=True))
    f.append(text(200, 78, "інерціальна система", size=13, color=MUTED, anchor="middle"))
    f.append(draw_bus(55, 150, 250, 72))
    f.append(arrow_c(238, 132, 292, 132, INK, sw=2.6, hs=10))     # рух автобуса
    f.append(text(250, 122, "автобус гальмує", size=13, color=INK, anchor="middle"))
    f.append(text(150, 175, "тримає швидкість", size=13, color=FIELD, anchor="middle"))
    f.append(circle(100, 200, 11, fill="#eafaf0", stroke=FIELD, sw=2))   # м'яч
    f.append(arrow_c(114, 200, 172, 200, FIELD, sw=2.6, hs=10))
    f.append(mtext(200, 281, ["М'яч без сили береже свою швидкість —",
                              "автобус гальмує з-під нього."], size=13, color=MUTED))
    # Панель B — погляд із автобуса
    f.append(text(585, 58, "Погляд із автобуса", size=16, color=INK, anchor="middle", bold=True))
    f.append(text(585, 78, "неінерціальна система", size=13, color=MUTED, anchor="middle"))
    f.append(draw_bus(455, 150, 250, 72))
    f.append(text(546, 138, "фіктивна сила", size=13, color=POS, anchor="middle"))
    f.append(circle(500, 200, 11, fill="#eafaf0", stroke=FIELD, sw=2))   # м'яч
    f.append(arrow_c(514, 200, 578, 200, POS, sw=2.6, hs=10, dash="5,4"))  # уявна сила
    f.append(mtext(585, 281, ["Ривок м'яча пояснюють силою,",
                              "якої ніхто не прикладав."], size=13, color=MUTED))
    render(path, W, H, *f, title="Один і той самий м'яч у двох системах відліку")


# ── Помічники для історичних фігур ──────────────────────────────────────────
def pill(x_right, cy, s, color, size=12):
    """Пігулка-статус, вирівняна ПРАВИМ краєм по x_right."""
    w = text_width(s, size, True) + 24
    h = size + 14
    cx = x_right - w / 2.0
    x = x_right - w
    y = cy - h / 2.0
    return (rect(x, y, w, h, fill="#ffffff", stroke=color, sw=1.8, rx=h / 2.0) +
            text(cx, cy + size * 0.34, s, size=size, color=color, anchor="middle", bold=True))


def arc_pts(cx, cy, r, a0, a1, n=48):
    """Точки дуги кола (кут у градусах; y — донизу)."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts


def polyline(pts, color=LINE, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pstr = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (pstr, color, sw, d))


# ── Фігура 4: родовід закону інерції ────────────────────────────────────────
def fig_genealogy(path):
    W, H = 900, 700
    spine_x = 96
    y0, step = 84, 92
    rows = [
        ("IV ст. до н.е.", "Арістотель · грек",
         "рух потребує невпинного двигуна; спокій — природний", "ХИБНА ОСНОВА", POS),
        ("VI ст.", "Йоан Філопон · Александрія",
         "тілу вкладено внутрішню рушійну силу", "ПЕРША ТРІЩИНА", MUTED),
        ("XIV ст.", "Жан Бурідан · Франція",
         "імпетус ∝ вага · швидкість, сам не згасає", "ЗАРОДОК p = m·v", MUTED),
        ("1610-ті", "Йоганн Кеплер · Німеччина",
         "увів слово inertia — та в сенсі «тяга до спокою»", "ІМʼЯ БЕЗ ЗМІСТУ", MUTED),
        ("бл. 1632", "Ґалілео Ґалілей · Італія",
         "інерція є — але горизонтальна, «кругова»", "ОБМЕЖЕНА ФОРМА", MUTED),
        ("1640–1644", "Ґассенді й Декарт · Франція",
         "вільне тіло йде рівно і ПРЯМО, без кінця", "ЗАГАЛЬНИЙ ПРИНЦИП", FIELD),
        ("1687", "Ісаак Ньютон · Англія",
         "закріпив як Lex I у «Началах»", "КОДИФІКАЦІЯ", NEG),
    ]
    f = []
    ylast = y0 + (len(rows) - 1) * step
    f.append(line(spine_x, y0, spine_x, ylast, color="#c7ccd3", sw=3))
    for i, (era, name, what, tag, col) in enumerate(rows):
        y = y0 + i * step
        f.append(circle(spine_x, y, 8, fill="#ffffff", stroke=col, sw=3))
        f.append(text(spine_x - 22, y + 4, era, size=13, color=MUTED, anchor="end"))
        f.append(text(spine_x + 42, y - 8, name, size=15.5, color=INK, anchor="start", bold=True))
        f.append(text(spine_x + 42, y + 15, what, size=13.5, color="#4b5563", anchor="start"))
        f.append(pill(W - 24, y, tag, col))
    render(path, W, H, *f, title="Родовід закону інерції: сходинки одного відкриття")


# ── Фігура 5: кругова інерція Ґалілея проти прямої Декарта й Ґассенді ────────
def fig_circular_straight(path):
    W, H = 900, 440
    f = [line(450, 40, 450, 420, color="#d0d5db", sw=1.2)]
    Ey, R, Rs = 760, 560, 544

    def earth(Ex):
        s = [polyline(arc_pts(Ex, Ey, Rs, 108, 72), color=LINE, sw=3)]
        s.append(text(Ex, 322, "Земля", size=14, color=MUTED, anchor="middle"))
        return "".join(s)

    # ── Ліва панель: кругова інерція ──
    Ex = 225
    f.append(text(Ex, 52, "Ґалілей: інерція «по колу»", size=16, color=INK, anchor="middle", bold=True))
    f.append(earth(Ex))
    tp = arc_pts(Ex, Ey, R, 106, 74)                       # траєкторія — уздовж кривизни
    f.append(polyline(tp, color=FIELD, sw=2.6, dash="7,5"))
    f.append(arrow_c(tp[-2][0], tp[-2][1], tp[-1][0], tp[-1][1], FIELD, sw=2.6, hs=11))
    f.append(circle(Ex, Ey - R, 11, fill="#eafaf0", stroke=FIELD, sw=2))   # тіло на вершині
    f.append(mtext(Ex, 388, ["тіло тримає сталу відстань до центра —",
                             "тому «природний» шлях виходить кривим"], size=13, color=MUTED))
    # ── Права панель: пряма інерція ──
    Ex = 675
    f.append(text(Ex, 52, "Ґассенді й Декарт: по прямій", size=16, color=INK, anchor="middle", bold=True))
    f.append(earth(Ex))
    top = (Ex, Ey - R)
    f.append(arrow_c(top[0], top[1], 872, top[1], NEG, sw=2.8, hs=12))     # пряма дотична
    f.append(circle(top[0], top[1], 11, fill="#eaf0fd", stroke=NEG, sw=2))
    for gx, gr in ((762, 8), (818, 7)):                                     # тіні тіла, що летить
        f.append(circle(gx, top[1], gr, fill="#f0f4fd", stroke="#a9bdf0", sw=1.4))
    f.append(line(864, top[1] + 4, 864, 247, color="#a9bdf0", sw=1.3, dash="4,4"))  # зростання зазору
    f.append(text(864, 262, "зазор", size=11.5, color=MUTED, anchor="middle"))
    f.append(mtext(Ex, 388, ["без сили тіло йде рівно і ПРЯМО —",
                             "і назавжди покидає поверхню Землі"], size=13, color=MUTED))
    render(path, W, H, *f, title=None)


if __name__ == "__main__":
    fig_inclined(os.path.join(OUT, "inclined-plane.svg"))
    fig_free_body(os.path.join(OUT, "free-body.svg"))
    fig_bus(os.path.join(OUT, "bus-frames.svg"))
    fig_genealogy(os.path.join(OUT, "inertia-genealogy.svg"))
    fig_circular_straight(os.path.join(OUT, "circular-vs-straight.svg"))
    print("OK: 5 SVG у", OUT)
