# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"
AMBER_D = "#b06d0a"


def wave(x1, x2, y, amp=7, step=24, color=POS, sw=2.4):
    """Хвиляста лінія від x1 до x2 на висоті y (для «розходяться»)."""
    d = "M %.1f %.1f" % (x1, y)
    n = max(1, int(abs(x2 - x1) / step))
    step = (x2 - x1) / n
    up = True
    for i in range(n):
        cx = x1 + step * (i + 0.5)
        ex = x1 + step * (i + 1)
        cy = y - amp if up else y + amp
        d += " Q %.1f %.1f %.1f %.1f" % (cx, cy, ex, y)
        up = not up
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def tri_left(cx, cy, color=POS, s=8):
    """Маленький трикутник-вістря, спрямований ліворуч."""
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (cx, cy, cx + s, cy - s * 0.72, cx + s, cy + s * 0.72, color))


def vtext(x, y, s, size=13, color=INK, bold=False):
    """Вертикальний напис (читається знизу вгору)."""
    b = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" transform="rotate(-90 %.1f %.1f)" '
            'font-family="%s" font-size="%d" fill="%s" text-anchor="middle"%s>%s</text>'
            % (x, y, x, y, FONT, size, color, b, esc(s)))


# ── Фігура 1: кеш як парі на несвіжість ──────────────────────────────────────
def fig_cache_as_bet():
    W, H = 1140, 470
    f = []

    # три учасники в ряд
    f.append(fitbox(60, 200, 150, 78, "читач", size=16, bold=True, fill=BG, stroke=INK))
    f.append(fitbox(370, 190, 240, 96, "копія (кеш)\nблизька, швидка,\nале лише знімок",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(830, 190, 240, 96, "джерело правди\nповільне, зате\nзавжди точне",
                    size=14, bold=True, fill=NEUT, stroke=INK))
    # письменник згори над джерелом
    f.append(fitbox(855, 58, 190, 58, "письменник", size=14, bold=True, fill=BG, stroke=INK))
    f.append(arrow(950, 120, 950, 186, color=INK, sw=2))
    f.append(text(972, 158, "запис", size=13, color=INK, anchor="start"))

    # читач → копія: читання (зелене)
    f.append(arrow(212, 238, 366, 238, color=FIELD, sw=2.4))
    f.append(text(289, 220, "читання", size=13, color=FIELD, bold=True))
    f.append(text(289, 262, "швидко, можливо несвіже", size=11, color=MUTED))

    # копія ↔ джерело: розходяться (червона хвиля, вістря до копії)
    f.append(wave(826, 622, 210, amp=7, color=POS))
    f.append(tri_left(614, 210, color=POS))
    f.append(text(720, 192, "розходяться", size=13, color=POS, bold=True))
    f.append(text(720, 232, "інвалідація — скинути копію", size=12, color=MUTED))

    # копія → джерело: промах (пунктир)
    f.append(arrow(614, 266, 826, 266, color=MUTED, sw=1.8))
    f.append(line(614, 266, 826, 266, color=MUTED, sw=1.8, dash="6 5"))
    f.append(text(720, 288, "промах → до джерела", size=12, color=MUTED))

    # ціна кешу — дві бирки
    f.append(text(120, 406, "ціна кешу:", size=13, color=MUTED, anchor="start"))
    f.append(fitbox(300, 380, 250, 48, "розрив свіжості", size=13, bold=True,
                    fill=RED_T, stroke=POS))
    f.append(fitbox(600, 380, 290, 48, "друге джерело правди", size=13, bold=True,
                    fill=BLUE_T, stroke=NEG))

    render(os.path.join(OUT, "cache-as-bet.svg"), W, H, *f)


# ── Фігура 2: п'ять воріт рішення ────────────────────────────────────────────
def fig_cache_gates():
    W, H = 1000, 792
    f = []

    gates = [
        "1 · Є реальна проблема читання?\n(спершу зміряй)",
        "2 · Є гарячий набір?\n(перекіс доступу)",
        "3 · Який бюджет несвіжості?",
        "4 · Де покласти й який патерн?",
        "5 · Що ламається на масштабі\nі коли кеш упав?",
    ]
    gy = [72, 196, 320, 444, 568]
    bx, bw, bh = 140, 440, 72

    for i, (g, cy) in enumerate(zip(gates, gy)):
        f.append(fitbox(bx, cy - bh / 2, bw, bh, g, size=14, bold=True,
                        fill=FILL, stroke=INK))
        # бічний вихід «ні»
        f.append(arrow(bx + bw + 2, cy, 690, cy, color=MUTED, sw=1.7))
        f.append(fitbox(694, cy - 24, 250, 48, "ні → не кешуй / деградуй",
                        size=12, fill=NEUT, stroke=MUTED, color=MUTED))
        # стрілка «так ↓» до наступних воріт
        ny = gy[i + 1] if i + 1 < len(gy) else 656
        f.append(arrow(bx + bw / 2, cy + bh / 2 + 1, bx + bw / 2, ny - bh / 2 - 1,
                       color=FIELD, sw=2.2))
        f.append(text(bx + bw / 2 + 16, (cy + bh / 2 + ny - bh / 2) / 2 + 4,
                      "так", size=12, color=FIELD, bold=True, anchor="start"))

    # підсумок
    f.append(fitbox(bx, 656 - 31, bw, 62, "Кешуй — і запиши рішення в ADR",
                    size=15, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, "cache-gates.svg"), W, H, *f)


# ── Фігура 3: карта «терпимість × перекіс» ───────────────────────────────────
def fig_staleness_skew_map():
    W, H = 940, 720
    x0, y0, x1, y1 = 150, 80, 820, 600
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    f = []

    # чотири квадранти-регіони
    f.append(rect(x0, y0, mx - x0, my - y0, fill=AMBER_T, stroke="#e6d3b0", sw=1))   # верх-ліво
    f.append(rect(mx, y0, x1 - mx, my - y0, fill=GREEN_T, stroke="#bfe3cb", sw=1))    # верх-право
    f.append(rect(x0, my, mx - x0, y1 - my, fill=RED_T, stroke="#eecac6", sw=1))      # низ-ліво
    f.append(rect(mx, my, x1 - mx, y1 - my, fill=NEUT, stroke="#d7dde3", sw=1))       # низ-право
    # осьові поділки
    f.append(line(mx, y0, mx, y1, color=MUTED, sw=1.4, dash="5 5"))
    f.append(line(x0, my, x1, my, color=MUTED, sw=1.4, dash="5 5"))
    f.append(rect(x0, y0, x1 - x0, y1 - y0, fill="none", stroke=INK, sw=1.8))

    # заголовки регіонів
    f.append(mtext(317, 122, "Кешуй, та коротко /\nскид на запис", size=14, color=AMBER_D, bold=True))
    f.append(mtext(652, 122, "Кешуй сміливо\n(довгий TTL)", size=14, color=FIELD, bold=True))
    f.append(text(317, 466, "Не кешуй", size=16, color=POS, bold=True))
    f.append(mtext(652, 460, "Кеш майже не влучає —\nсумнівно", size=13, color=MUTED))

    # позначки класів даних DH
    def marker(cx, cy, label, lx=None):
        s = [circle(cx, cy, 6, fill=INK, stroke=INK, sw=1)]
        s.append(text(cx, cy + 24, label, size=12, color=INK, bold=True))
        return "".join(s)

    f.append(marker(700, 250, "реєстр пристроїв"))
    f.append(marker(560, 300, "агрегати телеметрії"))
    f.append(marker(320, 250, "стан твіна наживо"))
    f.append(marker(300, 505, "права доступу"))

    # вісь X — терпимість до несвіжості
    f.append(arrow(x0, 628, x1 + 8, 628, color=INK, sw=1.8))
    f.append(text(mx, 660, "терпимість до несвіжості", size=14, color=INK, bold=True))
    f.append(text(188, 618, "низька", size=11, color=MUTED))
    f.append(text(788, 618, "висока", size=11, color=MUTED))

    # вісь Y — перекіс доступу
    f.append(arrow(125, y1, 125, y0 - 8, color=INK, sw=1.8))
    f.append(vtext(55, my, "перекіс доступу", size=14, color=INK, bold=True))
    f.append(vtext(100, 210, "гарячий набір", size=11, color=MUTED))
    f.append(vtext(100, 470, "рівномірно", size=11, color=MUTED))

    render(os.path.join(OUT, "staleness-skew-map.svg"), W, H, *f)


# ── Фігура 4 (вставка proj): лог як стенд — ворота стають вимірами ────────────
def fig_proj_log_as_bench():
    W, H = 1180, 470
    f = []

    # чотири стадії конвеєра
    f.append(fitbox(40, 150, 235, 130,
                    "лог доступу\n\nt · клас · ключ\n(реальні читання)",
                    size=14, bold=True, fill=BG, stroke=INK))
    f.append(fitbox(360, 150, 250, 130,
                    "симулятор\ncache-aside\n+ годинник TTL\n(протухання, промахи)",
                    size=14, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(700, 165, 200, 100,
                    "лічильники\nвлучань / промахів",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(960, 150, 190, 130,
                    "таблиця\nTTL → влучність\n→ QPS джерела",
                    size=14, bold=True, fill=FILL, stroke=INK))

    f.append(arrow(278, 215, 356, 215, color=INK, sw=2.2))
    f.append(arrow(613, 215, 696, 215, color=INK, sw=2.2))
    f.append(arrow(903, 215, 956, 215, color=INK, sw=2.2))

    # які ворота міряє кожна стадія (підписи знизу з запасом)
    f.append(text(157, 322, "ворота 1: скільки читань?", size=12, color=MUTED))
    f.append(text(157, 344, "ворота 2: перекіс ключів", size=12, color=MUTED))
    f.append(text(485, 322, "ворота 3: TTL — регулятор", size=12, color=MUTED))
    f.append(text(485, 344, "бюджету несвіжості", size=12, color=MUTED))
    f.append(text(1055, 322, "ворота 5: навантаження", size=12, color=MUTED))
    f.append(text(1055, 344, "й розвантаження джерела", size=12, color=MUTED))

    f.append(text(W / 2, 404, "один прогін логу — і кожні ворота стають числом, а не думкою",
                  size=14, color=INK, bold=True))
    render(os.path.join(OUT, "proj-log-as-bench.svg"), W, H, *f)


# ── Фігура 5 (вставка proj): криві TTL→влучність зі стінами бюджету ────────────
def fig_proj_ttl_curves():
    import math
    W, H = 1040, 640
    x0, x1, yb, yt = 118, 812, 520, 74      # межі поля (yb — низ 0%, yt — верх 100%)
    f = []

    ttls = [1, 5, 30, 60, 300, 600]
    lg = [math.log10(t) for t in ttls]
    lgmax = math.log10(600)

    def px(t):
        return x0 + math.log10(t) / lgmax * (x1 - x0)

    def py(h):
        return yb - h / 100.0 * (yb - yt)

    # виміряно cache_gates.py (seed 42), лише протухання (оптимістична межа)
    series = [
        ("реєстр",     FIELD,  [66.3, 79.6, 91.2, 94.3, 98.3, 99.2], 3600, 99.9),
        ("права",      POS,    [65.8, 77.7, 86.6, 89.2, 93.6, 94.9], 0,    0.0),
        ("телеметрія", NEG,    [27.2, 45.7, 66.3, 74.0, 87.8, 92.3], 30,   66.3),
        ("твін",       AMBER_D,[22.0, 44.5, 75.0, 84.1, 95.8, 97.9], 2,    31.7),
    ]

    # горизонтальна сітка + осі (вертикальних ліній НЕ веду — лише низові засічки)
    for h in (0, 25, 50, 75, 100):
        y = py(h)
        f.append(line(x0, y, x1, y, color="#e3e8ee", sw=1.2))
        f.append(text(x0 - 14, y + 4, f"{h}", size=12, color=MUTED, anchor="end"))
    for t in ttls:
        f.append(line(px(t), yb, px(t), yb - 6, color=MUTED, sw=1.4))
        f.append(text(px(t), yb + 22, f"{t}", size=12, color=MUTED))
    f.append(rect(x0, yt, x1 - x0, yb - yt, fill="none", stroke=INK, sw=1.6))
    f.append(text((x0 + x1) / 2, yb + 52, "TTL, секунд (логарифмічна вісь)",
                  size=14, color=INK, bold=True))
    f.append(vtext(46, (yb + yt) / 2, "влучність, %", size=14, color=INK, bold=True))

    # криві + маркер «що реально дозволяє бюджет»
    for name, col, ys, budget, ach in series:
        for i in range(len(ttls) - 1):
            f.append(line(px(ttls[i]), py(ys[i]), px(ttls[i + 1]), py(ys[i + 1]),
                          color=col, sw=2.6))
        if budget == 0:                       # права — TTL заборонено (X на нулі)
            f.append(line(x0 - 6, yb - 6, x0 + 6, yb + 6, color=POS, sw=2.6))
            f.append(line(x0 - 6, yb + 6, x0 + 6, yb - 6, color=POS, sw=2.6))
        elif budget <= 600:                   # твін / телеметрія — засічка бюджету
            bx = px(budget)
            f.append(line(bx, yb, bx, py(ach), color=col, sw=1.4, dash="5 5"))
            f.append(circle(bx, py(ach), 7, fill=col, stroke=BG, sw=2))
        else:                                 # реєстр — бюджет далеко за полем
            f.append(circle(x1, py(ys[-1]), 7, fill=col, stroke=BG, sw=2))

    # легенда-картка в порожньому нижньому-правому куті (між лініями сітки h0..h25)
    lx, ly, lw = 505, 416, 300
    f.append(rect(lx, ly, lw, 98, fill=BG, stroke="#d7dde3", sw=1.2))
    rows = [
        (FIELD,  "реєстр — бюджет 1 год → 99%"),
        (NEG,    "телеметрія — бюджет 30 с → 66%"),
        (AMBER_D,"твін — бюджет 2 с → 32%"),
        (POS,    "права — бюджет 0 с → заборонено"),
    ]
    for i, (col, s) in enumerate(rows):
        ry = ly + 22 + i * 21
        f.append(line(lx + 14, ry - 4, lx + 42, ry - 4, color=col, sw=3))
        f.append(text(lx + 52, ry, s, size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "proj-ttl-curves.svg"), W, H, *f)


# ── Спільні помічники для графіків вставки math ───────────────────────────────
_SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def sup10(e):
    if e == 0:
        return "1"
    return "10" + "".join(_SUP[c] for c in str(e))


def poly(pts, color=INK, sw=2.6, dash=None):
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


# ── Math-фігура 1: гіпербола розвантаження = 1/(1−h) ──────────────────────────
def fig_math_offload_hyperbola():
    W, H = 980, 560
    px0, px1 = 155, 900
    pyb, pyt = 470, 95

    def X(h):
        return px0 + h * (px1 - px0)

    def Yt(t):                       # t = log10(розвантаження), 0..3
        return pyb - (t / 3.0) * (pyb - pyt)

    f = []
    for t in (0, 1, 2, 3):
        y = Yt(t)
        f.append(line(px0, y, px1, y, color="#e3e8ee", sw=1.2))
        f.append(text(px0 - 12, y + 4, "%d×" % (10 ** t), size=12, color=MUTED, anchor="end"))
    f.append(line(px0, pyt - 12, px0, pyb, color=INK, sw=1.8))
    f.append(line(px0, pyb, px1, pyb, color=INK, sw=1.8))
    for h in (0.0, 0.5):
        f.append(line(X(h), pyb, X(h), pyb + 6, color=INK, sw=1.3))
        f.append(text(X(h), pyb + 22, ("%g" % h), size=12, color=MUTED))

    pts = []
    t = 0.0
    while t <= 3.0001:
        pts.append((X(1 - 10 ** (-t)), Yt(t)))
        t += 0.03
    f.append(poly(pts, color=POS, sw=3.0))

    for t, hh, lab in ((1, 0.9, "90% → 10×"), (2, 0.99, "99% → 100×"),
                       (3, 0.999, "99.9% → 1000×")):
        x, y = X(hh), Yt(t)
        f.append(line(x, pyb, x, y, color=MUTED, sw=1.2, dash="4 4"))
        f.append(circle(x, y, 5, fill=POS, stroke=POS))
        f.append(text(x - 10, y - 10, lab, size=13, color=INK, bold=True, anchor="end"))

    f.append(text((px0 + px1) / 2, pyb + 50, "влучність  h", size=14, color=INK, bold=True))
    f.append(vtext(60, (pyt + pyb) / 2, "розвантаження джерела = 1 / (1 − h)",
                   size=14, color=INK, bold=True))
    f.append(text((px0 + px1) / 2, 58,
                  "кожна дев'ятка влучності коштує вдесятеро — і живе в останніх відсотках",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "math-offload-hyperbola.svg"), W, H, *f)


# ── Math-фігура 2: закон Зіпфа проти рівномірного ─────────────────────────────
def fig_math_zipf_vs_uniform():
    W, H = 980, 590
    px0, px1 = 155, 880
    pyb, pyt = 485, 95
    K = 1_000_000
    G = 0.5772156649
    lnK = math.log(K)

    def X(C):
        return px0 + (math.log10(C) / 6.0) * (px1 - px0)

    def Y(h):
        return pyb - h * (pyb - pyt)

    f = []
    for h in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = Y(h)
        f.append(line(px0, y, px1, y, color="#e3e8ee", sw=1.2))
        f.append(text(px0 - 12, y + 4, "%d%%" % int(h * 100), size=12, color=MUTED, anchor="end"))
    for e in range(0, 7):
        x = X(10 ** e)
        f.append(line(x, pyb, x, pyb + 6, color=INK, sw=1.3))
        f.append(text(x, pyb + 22, sup10(e), size=12, color=MUTED))
    f.append(line(px0, pyt - 12, px0, pyb, color=INK, sw=1.8))
    f.append(line(px0, pyb, px1, pyb, color=INK, sw=1.8))

    def hz(C):
        return min(1.0, (math.log(C) + G) / (lnK + G))

    pz = []
    C = 10.0
    while C <= K + 1:
        pz.append((X(C), Y(hz(C))))
        C *= 10 ** 0.1
    f.append(poly(pz, color=FIELD, sw=3.0))

    pu = []
    C = 1.0
    while C <= K + 1:
        pu.append((X(C), Y(C / K)))
        C *= 10 ** 0.1
    f.append(poly(pu, color=MUTED, sw=2.4, dash="7 5"))

    xc = X(1000)
    f.append(line(xc, pyt - 8, xc, pyb, color="#c9d2db", sw=1.2, dash="4 4"))
    f.append(circle(xc, Y(0.52), 5, fill=FIELD, stroke=FIELD))
    f.append(circle(xc, Y(0.001), 5, fill=MUTED, stroke=MUTED))
    f.append(text(xc + 12, Y(0.52) - 6, "Зіпф: 52%", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(xc + 12, Y(0.001) - 8, "рівномірно: 0.1%", size=12, color=MUTED, anchor="start"))
    f.append(text(xc, pyt - 16, "кеш = 0.1% ключів", size=12, color=INK, bold=True))

    lx = px0 + 26
    f.append(line(lx, 128, lx + 30, 128, color=FIELD, sw=3))
    f.append(text(lx + 40, 132, "закон Зіпфа  (s = 1)", size=13, color=INK, anchor="start"))
    f.append(line(lx, 152, lx + 30, 152, color=MUTED, sw=3, dash="7 5"))
    f.append(text(lx + 40, 156, "рівномірний доступ", size=13, color=INK, anchor="start"))

    f.append(text((px0 + px1) / 2, pyb + 50, "розмір кешу  C  (ключів, лог-шкала)",
                  size=14, color=INK, bold=True))
    f.append(vtext(66, (pyt + pyb) / 2, "влучність кешу top-C", size=14, color=INK, bold=True))
    render(os.path.join(OUT, "math-zipf-vs-uniform.svg"), W, H, *f)


# ── Math-фігура 3: коліно min(r, 1/T) — межа робочого набору ───────────────────
def fig_math_offload_knee():
    W, H = 980, 560
    px0, px1 = 165, 900
    pyb, pyt = 470, 95

    def X(v):                        # v = r·T, лог 1e-2..1e5
        return px0 + (math.log10(v) + 2) / 7.0 * (px1 - px0)

    def Y(o):                        # o = розвантаження, лог 1..1e5
        return pyb - (math.log10(o) / 5.0) * (pyb - pyt)

    f = []
    for e in range(0, 6):
        y = Y(10 ** e)
        f.append(line(px0, y, px1, y, color="#e3e8ee", sw=1.2))
        f.append(text(px0 - 12, y + 4, "%d×" % (10 ** e), size=12, color=MUTED, anchor="end"))
    for e in range(-2, 6):
        x = X(10 ** e)
        f.append(line(x, pyb, x, pyb + 6, color=INK, sw=1.3))
        f.append(text(x, pyb + 22, sup10(e), size=11, color=MUTED))
    f.append(line(px0, pyt - 12, px0, pyb, color=INK, sw=1.8))
    f.append(line(px0, pyb, px1, pyb, color=INK, sw=1.8))

    # крива: розвантаження = max(1, r·T)
    f.append(line(X(1e-2), Y(1), X(1), Y(1), color=POS, sw=3.0))
    f.append(line(X(1), Y(1), X(1e5), Y(1e5), color=POS, sw=3.0))
    f.append(line(X(1), pyt - 8, X(1), pyb, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text(X(1), pyt - 16, "поріг  r·T = 1", size=12, color=INK, bold=True))

    f.append(mtext(X(0.06), 432, "ліворуч: кеш не влучає\n(холодний хвіст — прохід у джерело)",
                   size=12, color=MUTED))
    f.append(text(530, 208, "розвантаження = r·T", size=13, color=POS, bold=True))

    f.append(circle(X(60), Y(60), 6, fill=INK, stroke=INK))
    f.append(text(X(60) - 10, Y(60) - 24, "гаряча оселя DH  (0.2/с · 300 с = 60)",
                  size=12, color=INK, bold=True, anchor="end"))
    f.append(circle(X(60000), Y(60000), 6, fill=POS, stroke=POS))
    f.append(text(X(60000) - 8, Y(60000) - 30, "гарячий ключ  (1000/с · 60 с)  →  60000→1",
                  size=12, color=POS, bold=True, anchor="end"))

    f.append(text((px0 + px1) / 2, pyb + 50, "читань за одне вікно TTL   (r · T)",
                  size=14, color=INK, bold=True))
    f.append(vtext(64, (pyt + pyb) / 2, "розвантаження джерела на один ключ",
                   size=14, color=INK, bold=True))
    render(os.path.join(OUT, "math-offload-knee.svg"), W, H, *f)


# ── Вставка hist-cache-birth 1: дві важкі речі — одна тріщина ─────────────────
def fig_two_hard_things():
    W, H = 1110, 500
    f = []

    f.append(text(290, 44, "НАЙМЕННЯ", size=16, color=NEG, bold=True))
    f.append(text(820, 44, "ІНВАЛІДАЦІЯ КЕШУ", size=16, color=POS, bold=True))

    # ліва колонка — наймення
    f.append(fitbox(150, 72, 280, 58, "ім'я — фіксоване", size=15, bold=True,
                    fill=BLUE_T, stroke=NEG))
    f.append(arrow(290, 132, 290, 172, color=MUTED, sw=1.8))
    f.append(text(348, 158, "минає час", size=11, color=MUTED, anchor="start"))
    f.append(fitbox(150, 176, 280, 58, "поняття дрейфує", size=14, fill=NEUT, stroke=MUTED))
    f.append(arrow(290, 236, 290, 276, color=MUTED, sw=1.8))
    f.append(fitbox(148, 280, 284, 62, "розрив:\nім'я вже бреше", size=14, bold=True,
                    fill=RED_T, stroke=POS))

    # права колонка — кеш
    f.append(fitbox(680, 72, 280, 58, "копія — фіксована", size=15, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(arrow(820, 132, 820, 172, color=MUTED, sw=1.8))
    f.append(text(878, 158, "минає час", size=11, color=MUTED, anchor="start"))
    f.append(fitbox(680, 176, 280, 58, "джерело змінилося", size=14, fill=NEUT, stroke=MUTED))
    f.append(arrow(820, 236, 820, 276, color=MUTED, sw=1.8))
    f.append(fitbox(678, 280, 284, 62, "розрив:\nкопія несвіжа", size=14, bold=True,
                    fill=RED_T, stroke=POS))

    # спільний корінь
    f.append(arrow(290, 344, 470, 402, color=INK, sw=2))
    f.append(arrow(820, 344, 640, 402, color=INK, sw=2))
    f.append(fitbox(255, 406, 600, 64, "та сама тріщина:\nсталий знак проти рухомої правди",
                    size=15, bold=True, fill=FILL, stroke=INK))

    render(os.path.join(OUT, "two-hard-things.svg"), W, H, *f)


# ── Вставка hist-cache-birth 2: шлях слова «кеш» і жарт ───────────────────────
def fig_cache_word_timeline():
    W, H = 1180, 500
    f = []
    nodes = [200, 590, 985]

    boxes = [
        (40, "Морис Вілкс описує\n«slave memory» —\nмалу швидку пам'ять\nперед великою повільною",
         BLUE_T, NEG, 320),
        (430, "IBM 360/85: інженери пишуть\n«high-speed buffer»;\nредактор бере словник\n"
              "синонімів → «cache»\n(фр. cacher — ховати)", GREEN_T, FIELD, 320),
        (820, "Тім Брей записує жарт\nФіла Карлтона: «дві важкі\nречі — інвалідація кешу\n"
              "й наймення»", FILL, INK, 330),
    ]
    years = ["1965", "1968", "1996–97"]

    for (bx, body, fill, stroke, bw), nx, yr in zip(boxes, nodes, years):
        f.append(fitbox(bx, 64, bw, 168, yr + "\n" + body, size=14, fill=fill, stroke=stroke))
        f.append(line(nx, 232, nx, 297, color=MUTED, sw=1.6))

    # вісь часу
    f.append(arrow(60, 300, 1150, 300, color=INK, sw=2))
    f.append(text(1146, 292, "час →", size=12, color=MUTED, anchor="end"))
    for nx in nodes:
        f.append(circle(nx, 300, 9, fill=INK, stroke=INK, sw=1))

    # дуга-іронія: 1968 (наймення) → 1996–97 (жарт)
    f.append('<path d="M 600 318 Q 790 442 975 318" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="6 5"/>' % POS)
    f.append('<path d="M 975 318 L 968 330 L 962 320 z" fill="%s"/>' % POS)
    f.append(text(788, 470, "саме наймення дало ім'я одній із двох важких речей",
                  size=13, color=POS, italic=True))

    render(os.path.join(OUT, "cache-word-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cache_as_bet()
    fig_cache_gates()
    fig_staleness_skew_map()
    fig_proj_log_as_bench()
    fig_proj_ttl_curves()
    fig_math_offload_hyperbola()
    fig_math_zipf_vs_uniform()
    fig_math_offload_knee()
    fig_two_hard_things()
    fig_cache_word_timeline()
    print("OK: figures written to", OUT)
