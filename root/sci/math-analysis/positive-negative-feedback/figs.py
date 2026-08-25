# -*- coding: utf-8 -*-
"""Фігури до теми «Додатний і від'ємний зворотний зв'язок».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: рельєф — долина, горб, двоямний профіль ────────────────────────
def _curve_path(f, cx, halfw, yt, yb, base, n=140):
    """Шлях кривої-рейки f(t)∈[-1,1] + заливка вниз до base."""
    pts = []
    for i in range(n + 1):
        t = -1 + 2.0 * i / n
        pts.append((cx + t * halfw, f(t, yt, yb)))
    line_d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    fill_d = (line_d + " L %.1f %.1f L %.1f %.1f Z"
              % (cx + halfw, base, cx - halfw, base))
    return line_d, fill_d, pts


def _ball(cx, cy, r=12, faint=False):
    if faint:
        return circle(cx, cy, r, fill="#e2e6eb", stroke=MUTED, sw=1.4)
    return (circle(cx, cy, r, fill="#eef2f7", stroke=INK, sw=2.0)
            + circle(cx - r * 0.32, cy - r * 0.32, r * 0.28, fill="#ffffff", stroke="none", sw=0))


def _panel(f, cx, header, sub, hcol, note, ball_t, arr_dir, arr_col, arr_lbl,
           eq_ball=True, extra_balls=()):
    halfw, yt, yb, base, r = 112, 150, 292, 316, 12
    out = []
    out.append(text(cx, 66, header, size=15, bold=True, color=hcol))
    out.append(text(cx, 85, sub, size=12, color=MUTED))
    line_d, fill_d, _ = _curve_path(f, cx, halfw, yt, yb, base)
    out.append('<path d="%s" fill="#f1f3f6" stroke="none"/>' % fill_d)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (line_d, INK))
    # рівновага (пунктирна вертикаль у центрі панелі)
    eqx = cx + 0.0 * halfw
    eqy = f(0.0, yt, yb)
    out.append(line(eqx, eqy + 4, eqx, min(eqy + 58, base), color=MUTED, sw=1.1, dash="3,5"))
    # додаткові стійкі положення (для двоямної) — бліді кульки
    for tb in extra_balls:
        bx = cx + tb * halfw
        out.append(_ball(bx, f(tb, yt, yb) - r, r=r, faint=True))
    # бліда кулька в рівновазі
    if eq_ball:
        out.append(_ball(eqx, eqy - r, r=r, faint=True))
    # активна кулька, зміщена
    bx = cx + ball_t * halfw
    by = f(ball_t, yt, yb) - r
    out.append(_ball(bx, by, r=r))
    # стрілка сили
    ax0 = bx + arr_dir * (r + 4)
    ax1 = bx + arr_dir * (r + 52)
    out.append(arrow(ax0, by, ax1, by, color=arr_col, sw=3.2))
    out.append(text((ax0 + ax1) / 2, by - 12, arr_lbl, size=11, bold=True, color=arr_col))
    # нижній підпис
    out.append(mtext(cx, 344, note, size=11.5, color=INK, lh=1.25))
    return out


def fig_landscape():
    W, H = 940, 388
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Знак зв'язку = вирок рівновазі: долина тримає, горб жене геть",
                  size=16, bold=True))

    def valley(t, yt, yb):
        return yb - (yb - yt) * t * t

    def hill(t, yt, yb):
        return yt + (yb - yt) * t * t

    gmax = (1 - 0.36) ** 2

    def dwell(t, yt, yb):
        g = (t * t - 0.36) ** 2
        return yt + (yb - yt) * (1 - g / gmax)

    f += _panel(valley, 168, "Від'ємний зв'язок", "стійка рівновага", NEG,
                "нахил повертає до дна:\nзбурення тане",
                ball_t=0.52, arr_dir=-1, arr_col=NEG, arr_lbl="повертає")
    f += _panel(hill, 470, "Додатний зв'язок", "нестійка рівновага", POS,
                "нахил жене геть, і що далі —\nто сильніше: втеча",
                ball_t=0.34, arr_dir=+1, arr_col=POS, arr_lbl="жене геть")
    f += _panel(dwell, 772, "Додатний зв'язок → вибір", "двоямний профіль", POS,
                "мала перевага наростає сама —\nскочується в одну з долин",
                ball_t=0.10, arr_dir=+1, arr_col=POS, arr_lbl="скочується",
                eq_ball=True, extra_balls=(-0.6, 0.6))
    # роздільники панелей
    for xd in (319, 621):
        f.append(line(xd, 54, xd, H - 20, color=LINE, sw=1.0, dash="3,7"))
    return render(os.path.join(IMG, "landscape.svg"), W, H, *f)


# ── Фігура 2: петля зворотного зв'язку — два знаки суматора ──────────────────
def _spark(x, y, w, h, kind):
    """Мінікрива поведінки виходу: спад (kind='decay') / розгін ('grow')."""
    out = [rect(x, y, w, h, fill="#fbfcfd", stroke=LINE, sw=1.0, rx=4)]
    bx0, bx1 = x + 10, x + w - 8
    base, top = y + h - 12, y + 12
    out.append(line(bx0, base, bx1, base, color=MUTED, sw=1.0))
    out.append(line(bx0, base, bx0, top, color=MUTED, sw=1.0))
    span = base - top - 2
    pts = []
    n = 80
    for i in range(n + 1):
        u = i / n
        if kind == "decay":
            v = math.exp(-3.2 * u)
        else:
            v = min(1.0, 0.07 * math.exp(3.3 * u))
        px = bx0 + (bx1 - bx0) * u
        py = base - v * span
        pts.append((px, py))
    col = NEG if kind == "decay" else POS
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, col))
    return "".join(out)


def _loop_panel(f, pcx, header, hcol, sign, spark_kind, verdict):
    Lx = pcx - 215
    ny, nr = 150, 17               # суматор
    nx = Lx + 100
    scol = NEG if sign == "−" else POS
    f.append(text(pcx, 60, header, size=15, bold=True, color=hcol))

    # вхід
    f.append(arrow(Lx + 22, ny, nx - nr - 3, ny, color=INK, sw=2.0))
    f.append(text(Lx + 20, ny - 12, "задане", size=11, color=MUTED, anchor="start"))
    # суматор
    f.append(circle(nx, ny, nr, fill="#ffffff", stroke=INK, sw=2.0))
    f.append(text(nx, ny + 6, "Σ", size=18, bold=True))
    f.append(text(nx - nr - 2, ny - nr - 2, "+", size=15, bold=True, color=INK, anchor="end"))
    # суматор → об'єкт
    f.append(arrow(nx + nr + 3, ny, Lx + 150, ny, color=INK, sw=2.0))
    # об'єкт
    f.append(fitbox(Lx + 150, ny - 27, 152, 54, "об'єкт\n(підсилення)", size=13, bold=True,
                    fill="#eef2f7"))
    # об'єкт → вихід
    f.append(arrow(Lx + 302, ny, Lx + 348, ny, color=INK, sw=2.0))
    f.append(text(Lx + 354, ny + 5, "вихід x", size=13, bold=True, anchor="start"))
    # петля відгуку: вниз → ліворуч → вгору в суматор
    fy = 252
    tap = Lx + 322
    f.append(line(tap, ny + 2, tap, fy, color=scol, sw=2.4))
    f.append(line(tap, fy, nx, fy, color=scol, sw=2.4))
    f.append(arrow(nx, fy, nx, ny + nr + 2, color=scol, sw=2.4))
    # знак відгуку на вертикалі входу в суматор
    if sign == "−":
        f.append(minus(nx - 22, (fy + ny + nr) / 2 + 4, r=9))
    else:
        f.append(plus(nx - 22, (fy + ny + nr) / 2 + 4, r=9))
    f.append(text((tap + nx) / 2, fy + 18, "відгук: вимір виходу", size=11,
                  color=scol, anchor="middle"))
    # мінікрива поведінки + вирок
    f.append(_spark(Lx + 58, 296, 300, 70, spark_kind))
    b, _, _ = textbox(pcx, 388, verdict, size=12, pad=8, fill=FILL, stroke=hcol, sw=1.4, bold=True)
    f.append(b)


def fig_loop():
    W, H = 920, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Одна петля, два знаки: суматор віднімає чи додає відгук",
                  size=16, bold=True))
    f.append(line(W / 2, 48, W / 2, H - 16, color=LINE, sw=1.0, dash="3,7"))
    _loop_panel(f, 235, "Від'ємний зв'язок", NEG, "−", "decay",
                "віднімає → тисне назустріч → стійко")
    _loop_panel(f, 685, "Додатний зв'язок", POS, "+", "grow",
                "додає → підганяє відхилення → розгін")
    return render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── Фігура 3: три долі відхилення в часі ─────────────────────────────────────
def fig_regimes():
    W, H = 840, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три долі відхилення в часі: спад · розгін · розгойдування",
                  size=16, bold=True))

    ox, rx = 92, 690
    mid, top, bot = 218, 74, 362
    vspan = mid - top                    # відповідає v=1.2
    VMAX = 1.2

    def PX(u):                           # u∈[0,1] уздовж осі часу
        return ox + (rx - ox) * u

    def PY(v):
        v = max(-VMAX, min(VMAX, v))
        return mid - v * (vspan / VMAX)

    # осі
    f.append(arrow(ox, mid, rx + 20, mid, color=INK, sw=1.6))
    f.append(line(ox, top - 4, ox, bot, color=INK, sw=1.6))
    f.append(text(rx + 16, mid + 22, "час →", size=12, anchor="end"))
    f.append(text(ox - 12, top + 4, "відхилення x", size=12, bold=True, anchor="start"))
    # лінія рівноваги
    f.append(line(ox, mid, rx + 10, mid, color=MUTED, sw=1.0, dash="5,6"))
    f.append(text(rx + 14, mid + 4, "рівновага", size=10, color=MUTED, anchor="start"))

    def plot(fn, col, sw=2.6, n=360):
        pts = []
        for i in range(n + 1):
            u = i / n
            pts.append((PX(u), PY(fn(u))))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw))

    T = 6.0
    # від'ємний зв'язок — спад до рівноваги
    plot(lambda u: 1.02 * math.exp(-1.15 * (u * T)), NEG)
    # додатний зв'язок — експоненційна втеча
    plot(lambda u: 0.10 * math.exp(0.74 * (u * T)), POS)
    # від'ємний із запізненням — розгойдування, що наростає
    plot(lambda u: 0.10 * math.exp(0.33 * (u * T)) * math.sin(2 * math.pi * (u * T) / 1.42),
         MUTED, sw=2.2)

    # підписи кривих — рознесені, з запасом
    f.append(text(PX(0.30) + 6, PY(0.62), "від'ємний зв'язок:", size=12, bold=True,
                  color=NEG, anchor="start"))
    f.append(text(PX(0.30) + 6, PY(0.62) + 17, "відхилення тане", size=11,
                  color=NEG, anchor="start"))
    f.append(text(PX(0.80), PY(1.02) - 10, "додатний зв'язок:", size=12, bold=True,
                  color=POS, anchor="middle"))
    f.append(text(PX(0.80), PY(1.02) + 7, "розгін", size=11, color=POS, anchor="middle"))
    f.append(text(PX(0.055), PY(-0.92) + 4, "від'ємний зв'язок із запізненням:", size=11.5,
                  bold=True, color=INK, anchor="start"))
    f.append(text(PX(0.055), PY(-0.92) + 20, "спізніле виправлення розгойдує", size=11,
                  color=MUTED, anchor="start"))
    return render(os.path.join(IMG, "regimes.svg"), W, H, *f)


# ═══ Фігури до вставки proj-feedback-sim ════════════════════════════════════
def _axes2(f, ox, rx, ytop, ybot, tmax, vmin, vmax, xlabel, ylabel, zeroline=False):
    """Осі часового графіка; повертає (PX, PY). v клампиться в [vmin, vmax]."""
    def PX(t):
        return ox + (rx - ox) * (t / tmax)

    def PY(v):
        v = max(vmin, min(vmax, v))
        return ybot - (v - vmin) * ((ybot - ytop) / (vmax - vmin))

    f.append(line(ox, ybot, ox, ytop - 4, color=INK, sw=1.6))
    axy = PY(0) if vmin <= 0 <= vmax else ybot
    f.append(arrow(ox, axy, rx + 18, axy, color=INK, sw=1.6))
    f.append(text(rx + 16, axy + 20, xlabel, size=11, anchor="end"))
    f.append(text(ox - 4, ytop - 9, ylabel, size=12, bold=True, anchor="start"))
    if zeroline and vmin <= 0 <= vmax:
        f.append(line(ox, PY(0), rx + 6, PY(0), color=MUTED, sw=1.0, dash="5,6"))
    return PX, PY


def _poly(f, PX, PY, samples, col, sw=2.4, dash=None):
    pts = [(PX(t), PY(v)) for (t, v) in samples]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
             % (d, col, sw, da))


def _dots(f, PX, PY, samples, col, r=3.2):
    for (t, v) in samples:
        f.append(circle(PX(t), PY(v), r, fill=col, stroke=BG, sw=1.0))


def _legrow(f, x, y, col, s, sw=3.0, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="%.1f"%s/>' % (x, y, x + 30, y, col, sw, da))
    f.append(text(x + 40, y + 4, s, size=12, color=INK, anchor="start"))


# ── Фігура 4: крок Ейлера бреше, коли завеликий ──────────────────────────────
def fig_euler_step():
    W, H = 860, 402
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Завеликий крок Ейлера вигадує нестійкість, якої в системі нема",
                  size=16, bold=True))
    f.append(text(W / 2, 51,
                  "спадна система  dx/dt = k·x,  k = −0.5 1/с   ·   поріг стійкості кроку  dt = 2/|k| = 4 с",
                  size=11.5, color=MUTED))
    ox, rx, ytop, ybot = 82, 788, 82, 356
    tmax, vmax = 25.0, 4.0
    PX, PY = _axes2(f, ox, rx, ytop, ybot, tmax, -vmax, vmax, "час, с", "x", zeroline=True)

    exact = [(i * 0.25, math.exp(-0.5 * i * 0.25)) for i in range(int(tmax / 0.25) + 1)]
    _poly(f, PX, PY, exact, MUTED, sw=1.8, dash="6,5")

    def euler(dt):
        n = int(tmax / dt); x = 1.0; s = [(0.0, x)]
        for i in range(n):
            x = x + dt * (-0.5 * x); s.append(((i + 1) * dt, x))
        return s

    _poly(f, PX, PY, euler(0.5), NEG, sw=2.4)
    bad = euler(5.0)
    _poly(f, PX, PY, bad, POS, sw=2.6)
    _dots(f, PX, PY, bad, POS)

    f.append(text(PX(5.2), PY(0.95) - 8, "точний  e^(k·t)", size=11.5, color=MUTED, anchor="start"))
    f.append(text(PX(6.6), PY(-0.7), "Ейлер, dt = 0.5 с — тримається кривої", size=11.5,
                  bold=True, color=NEG, anchor="start"))
    f.append(text(PX(8.5), PY(3.5), "Ейлер, dt = 5 с > поріг:", size=12, bold=True,
                  color=POS, anchor="start"))
    f.append(text(PX(8.5), PY(3.5) + 17, "чисельний вибух на рівному місці", size=11.5,
                  color=POS, anchor="start"))
    return render(os.path.join(IMG, "euler-step.svg"), W, H, *f)


# ── Фігура 5: затримка обертає мінус на плюс ─────────────────────────────────
def fig_delay_onset():
    W, H = 860, 404
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Та сама від'ємна петля, три затримки: спад · межа · розгойдування",
                  size=16, bold=True))
    f.append(text(W / 2, 51,
                  "dx/dt = −k·x(t − τ_d),  k = 1 1/с   ·   поріг  τ_d = π/(2k) ≈ 1.57 с",
                  size=11.5, color=MUTED))
    ox, rx, ytop, ybot = 82, 788, 90, 360
    tmax, vmax = 22.0, 3.2
    PX, PY = _axes2(f, ox, rx, ytop, ybot, tmax, -vmax, vmax, "час, с", "x", zeroline=True)

    def sim(Td, dt=0.005):
        d = int(round(Td / dt)); n = int(tmax / dt)
        hist = [1.0] * (d + 1); x = 1.0; s = [(0.0, 1.0)]
        for i in range(n):
            x = x + dt * (-1.0 * hist[-d - 1]); hist.append(x)
            if i % 10 == 0:
                s.append(((i + 1) * dt, x))
        return s

    _poly(f, PX, PY, sim(1.0), NEG, sw=2.4)
    _poly(f, PX, PY, sim(1.5708), INK, sw=1.9)
    _poly(f, PX, PY, sim(2.0), POS, sw=2.7)

    lx, ly = PX(0.4), PY(3.02)
    _legrow(f, lx, ly, NEG, "τ_d = 1.0 с  <  поріг:  розгойдування тане (стійко)", sw=3.0)
    _legrow(f, lx, ly + 20, INK, "τ_d ≈ 1.57 с  =  поріг:  незгасні коливання", sw=2.6)
    _legrow(f, lx, ly + 40, POS, "τ_d = 2.0 с  >  поріг:  амплітуда наростає (розгін)", sw=3.2)
    f.append(text(PX(21.4), PY(2.65), "виходить", size=10.5, color=POS, anchor="end"))
    f.append(text(PX(21.4), PY(2.65) + 14, "за межі", size=10.5, color=POS, anchor="end"))
    return render(os.path.join(IMG, "delay-onset.svg"), W, H, *f)


# ── Фігура 6: насичення й двостійкість ───────────────────────────────────────
def fig_saturation():
    W, H = 908, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Нелінійність приборкує додатний зв'язок: насичення й вибір долини",
                  size=16, bold=True))
    f.append(line(W / 2, 48, W / 2, H - 16, color=LINE, sw=1.0, dash="3,7"))

    # ── ліва панель: логістика ──
    f.append(text(232, 66, "Логістика: розгін упирається в стелю", size=13.5, bold=True))
    f.append(text(232, 84, "dx/dt = r·x·(1 − x/K),  r = 1.2, K = 100", size=11, color=MUTED))
    ox1, rx1, ytop, ybot = 66, 398, 104, 356
    tmax1 = 10.0
    PX1, PY1 = _axes2(f, ox1, rx1, ytop, ybot, tmax1, 0, 150, "час, с", "x")
    f.append(line(ox1, PY1(100), rx1 + 6, PY1(100), color=FIELD, sw=1.4, dash="5,5"))
    f.append(text(rx1 + 4, PY1(100) - 6, "K = 100", size=10.5, color=FIELD, anchor="end"))

    def logi(x0, dt=0.02):
        n = int(tmax1 / dt); x = x0; s = [(0.0, x)]
        for i in range(n):
            x = x + dt * (1.2 * x * (1 - x / 100.0))
            if i % 3 == 0:
                s.append(((i + 1) * dt, x))
        return s

    for x0 in (3.0, 16.0, 55.0, 140.0):
        _poly(f, PX1, PY1, logi(x0), POS, sw=2.2)
    f.append(text(PX1(4.6), PY1(46), "S-крива", size=11, color=POS, anchor="middle"))

    # ── права панель: двостійкість ──
    f.append(text(680, 66, "Двостійкість: вибір однієї з двох долин", size=13.5, bold=True))
    f.append(text(680, 84, "dx/dt = x − x³   (старт майже з вершини x = 0)", size=11, color=MUTED))
    ox2, rx2 = 520, 852
    tmax2 = 8.0
    PX2, PY2 = _axes2(f, ox2, rx2, ytop, ybot, tmax2, -1.7, 1.7, "час, с", "x", zeroline=True)
    f.append(line(ox2, PY2(1), rx2 + 6, PY2(1), color=POS, sw=1.2, dash="4,5"))
    f.append(line(ox2, PY2(-1), rx2 + 6, PY2(-1), color=NEG, sw=1.2, dash="4,5"))
    f.append(text(rx2 + 4, PY2(1) - 6, "стійка +1", size=10, color=POS, anchor="end"))
    f.append(text(rx2 + 4, PY2(-1) + 14, "стійка −1", size=10, color=NEG, anchor="end"))
    f.append(text(ox2 + 8, PY2(0) - 7, "нестійка  x = 0", size=10, color=MUTED, anchor="start"))

    def well(x0, dt=0.01):
        n = int(tmax2 / dt); x = x0; s = [(0.0, x)]
        for i in range(n):
            x = x + dt * (x - x ** 3)
            if i % 4 == 0:
                s.append(((i + 1) * dt, x))
        return s

    for x0 in (0.4, 1.55):
        _poly(f, PX2, PY2, well(x0), POS, sw=1.8)
    for x0 in (-0.4, -1.55):
        _poly(f, PX2, PY2, well(x0), NEG, sw=1.8)
    _poly(f, PX2, PY2, well(0.03), POS, sw=2.8)
    _poly(f, PX2, PY2, well(-0.03), NEG, sw=2.8)
    f.append(text(PX2(3.4), PY2(0.55), "старт ±0.03 —", size=10.5, bold=True, color=INK, anchor="middle"))
    f.append(text(PX2(3.4), PY2(0.55) + 14, "мізерна перевага вирішує долю", size=10.5,
                  color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, "saturation.svg"), W, H, *f)


# ═══ Фігура до вставки hist-feedback-control ════════════════════════════════
def fig_timeline():
    W, H = 1040, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Історія зворотного зв'язку: будували руками, зрозуміли за одне життя",
                  size=16, bold=True))
    f.append(text(W / 2, 44, "дві сплячки завдовжки рівно у 80 років — теорія весь час відставала "
                             "(вісь: послідовність подій, не в масштабі)", size=11.5, color=MUTED))

    left, right = 40, 1000
    n = 7
    pitch = (right - left) / n
    cx = [left + pitch * (i + 0.5) for i in range(n)]

    cards = [
        ("Ктесібій",   ["поплавковий", "регулятор"],            "бл. 250 до н.е.", NEG),
        ("Дреббель",   ["терморегулятор", "печі"],              "бл. 1620",        NEG),
        ("Мід · Ватт", ["відцентровий", "регулятор"],           "1787–88",         NEG),
        ("Максвелл",   ["«Про регулятори»", "теорія стійкості"], "1868",           INK),
        ("Ларсен",     ["акустичний", "зв'язок"],               "бл. 1910",        POS),
        ("Блек",       ["підсилювач", "зі зв'язком"],           "1927",            NEG),
        ("Вінер",      ["«Кібернетика»", "єдиний принцип"],     "1948",            FIELD),
    ]

    baseline = 200
    cw, cyy, ch = 126, 52, 104
    f.append(arrow(24, baseline, right + 16, baseline, color=INK, sw=1.6))
    f.append(text(right + 8, baseline - 10, "час →", size=11, color=MUTED, anchor="end"))

    for i, (name, desc, year, col) in enumerate(cards):
        x = cx[i]
        f.append(rect(x - cw / 2, cyy, cw, ch, fill="#ffffff", stroke=col, sw=2.0, rx=7))
        f.append(line(x - cw / 2 + 8, cyy + 24, x + cw / 2 - 8, cyy + 24, color=col, sw=1.0))
        f.append(text(x, cyy + 18, name, size=13, bold=True, color=col))
        f.append(mtext(x, cyy + 44, desc, size=11, color=INK, lh=1.3))
        f.append(line(x, cyy + ch, x, baseline - 8, color=MUTED, sw=1.1))
        f.append(circle(x, baseline, 6, fill=col, stroke="#ffffff", sw=1.5))
        f.append(text(x, baseline + 24, year, size=11.5, bold=True, color=col))

    # дуга A: Ватт → Максвелл (машина працює, теорії ще нема)
    f.append('<path d="M %.1f 208 Q %.1f 356 %.1f 208" fill="none" stroke="%s" '
             'stroke-width="2.0"/>' % (cx[2], (cx[2] + cx[3]) / 2, cx[3], MUTED))
    midA = (cx[2] + cx[3]) / 2
    f.append(text(midA, 246, "≈ 80 років", size=12, bold=True, color=INK))
    f.append(text(midA, 261, "регулятор крутить світ,", size=10.5, color=MUTED))
    f.append(text(midA, 275, "а теорії стійкості ще нема", size=10.5, color=MUTED))

    # дуга B: Максвелл → Вінер (теорію написано й забуто)
    f.append('<path d="M %.1f 214 Q %.1f 500 %.1f 214" fill="none" stroke="%s" '
             'stroke-width="2.0"/>' % (cx[3], (cx[3] + cx[6]) / 2, cx[6], MUTED))
    midB = (cx[3] + cx[6]) / 2
    f.append(text(midB, 372, "≈ 80 років", size=12, bold=True, color=INK))
    f.append(text(midB, 387, "теорію написано — і забуто,", size=10.5, color=MUTED))
    f.append(text(midB, 401, "доки Вінер її не воскресив", size=10.5, color=MUTED))

    # легенда
    leg = [(NEG, "від'ємний зв'язок / регулювання"), (POS, "додатний зв'язок / виття"),
           (INK, "теорія стійкості"), (FIELD, "єдиний принцип")]
    lx = [150, 400, 610, 782]
    for (col, lbl), x in zip(leg, lx):
        f.append(rect(x, 427, 12, 12, fill=col, stroke="none", sw=0, rx=2))
        f.append(text(x + 18, 437, lbl, size=11, color=INK, anchor="start"))

    return render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ═══ Фігури до вставки math-linear-stability ════════════════════════════════
def _dot(x, y, col, r=6):
    return circle(x, y, r, fill=col, stroke=INK, sw=1.2)


# Комплексна площина власних чисел
def fig_lambda_plane():
    W, H = 880, 470
    cx, cy = 431, 236
    sx, sy = 120, 70

    def PX(re):
        return cx + re * sx

    def PY(im):
        return cy - im * sy

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Власні числа на комплексній площині: ліва половина гасить, права розганяє",
                  size=15, bold=True))
    x_l, x_r = PX(-2.7), PX(2.7)
    y_t, y_b = PY(2.55), PY(-2.55)
    f.append(rect(x_l, y_t, cx - x_l, y_b - y_t, fill="#eef3fd", stroke='none', sw=0, rx=0))
    f.append(rect(cx, y_t, x_r - cx, y_b - y_t, fill="#fdeeed", stroke='none', sw=0, rx=0))
    f.append(arrow(x_l - 6, cy, x_r + 10, cy, color=INK, sw=1.7))
    f.append(arrow(cx, y_b + 6, cx, y_t - 8, color=INK, sw=1.7))
    f.append(text(x_r + 8, cy + 20, "Re λ (темп)", size=11.5, color=INK, anchor="end"))
    f.append(text(cx + 10, y_t - 2, "Im λ (коливання)", size=11.5, color=INK, anchor="start"))
    f.append(mtext(PX(-1.55), y_t + 34, "Re λ < 0\nзгасання — стійко", size=13, color=NEG, bold=True, lh=1.25))
    f.append(mtext(PX(1.55), y_t + 34, "Re λ > 0\nрозгін — нестійко", size=13, color=POS, bold=True, lh=1.25))
    f.append(text(cx, y_b + 22, "уявна вісь — чисте коливання (центр)", size=11, color=MUTED))
    # фокус — позаосьова пара (згасна спіраль)
    fx, fuy, fly = PX(-0.85), PY(1.15), PY(-1.15)
    f.append(circle(fx, fuy, 5, fill="#dfe4ea", stroke=MUTED, sw=1.1))
    f.append(circle(fx, fly, 5, fill="#dfe4ea", stroke=MUTED, sw=1.1))
    f.append(line(fx, fuy, fx, fly, color=MUTED, sw=0.9, dash="2,4"))
    f.append(text(fx - 6, fuy - 8, "фокус (спіраль)", size=10.5, color=MUTED, anchor="end"))
    # перевернутий = сідло (пара на дійсній осі)
    f.append(text(cx, PY(0) - 46, "перевернутий маятник = сідло", size=12, bold=True, color=INK))
    dxr, dxl = PX(2.1), PX(-2.1)
    f.append(_dot(dxr, cy, POS))
    f.append(_dot(dxl, cy, NEG))
    f.append(text(dxr, cy - 16, "+√(g/L)", size=11, bold=True, color=POS))
    f.append(text(dxl, cy - 16, "−√(g/L)", size=11, color=NEG))
    # звисаючий = центр (пара на уявній осі)
    duy, dly = PY(1.6), PY(-1.6)
    f.append(_dot(cx, duy, NEG))
    f.append(_dot(cx, dly, NEG))
    f.append(mtext(cx, dly + 22, "звисаючий маятник\n±i√(g/L): центр", size=11.5, color=NEG, bold=True, lh=1.2))
    return render(os.path.join(IMG, "lambda-plane.svg"), W, H, *f)


# Площина слід–визначник
def fig_trace_det():
    W, H = 820, 500
    cx, cy = 410, 250
    sx, sy = 94, 54

    def TX(T):
        return cx + T * sx

    def DY(D):
        return cy - D * sy

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Площина слід–визначник: два числа матриці називають тип рівноваги",
                  size=15, bold=True))
    xl, xr = TX(-3.4), TX(3.4)
    yb, yt = DY(-3.0), DY(3.4)
    f.append(rect(xl, yt, cx - xl, cy - yt, fill="#eef3fd", stroke='none', sw=0, rx=0))
    f.append(rect(cx, yt, xr - cx, cy - yt, fill="#fdeeed", stroke='none', sw=0, rx=0))
    f.append(rect(xl, cy, xr - xl, yb - cy, fill="#f6eeee", stroke='none', sw=0, rx=0))
    # парабола дискримінанта D = T²/4
    pts = []
    Tt = -3.4
    while Tt <= 3.4001:
        pts.append((TX(Tt), DY(Tt * Tt / 4.0)))
        Tt += 0.1
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7" stroke-dasharray="5,5"/>' % (d, MUTED))
    f.append(arrow(xl - 6, cy, xr + 10, cy, color=INK, sw=1.7))
    f.append(arrow(cx, yb + 6, cx, yt - 8, color=INK, sw=1.7))
    f.append(text(xr + 8, cy - 8, "слід T", size=12, bold=True, anchor="end"))
    f.append(text(xr + 8, cy + 16, "(знак тертя)", size=10, color=MUTED, anchor="end"))
    f.append(text(cx + 10, yt - 2, "визначник D", size=12, bold=True, anchor="start"))
    f.append(text(cx + 10, yt + 14, "(знак пружини)", size=10, color=MUTED, anchor="start"))
    f.append(mtext(TX(-1.55), DY(2.55), "стійкий фокус\n(спіраль усередину)", size=12, color=NEG, bold=True, lh=1.2))
    f.append(mtext(TX(1.5), DY(2.55), "нестійкий фокус\n(спіраль назовні)", size=12, color=POS, bold=True, lh=1.2))
    f.append(mtext(TX(-2.7), DY(0.62), "стійкий\nвузол", size=12, color=NEG, bold=True, lh=1.2))
    f.append(mtext(TX(2.7), DY(0.62), "нестійкий\nвузол", size=12, color=POS, bold=True, lh=1.2))
    f.append(mtext(TX(-1.9), DY(-1.55), "сідло\n(завжди нестійке)", size=12, color=INK, bold=True, lh=1.2))
    f.append(text(TX(-2.75), DY(1.95), "D = T²/4", size=11, color=MUTED, anchor="middle"))
    # маятники
    f.append(_dot(cx, DY(2.0), NEG))
    f.append(text(cx, DY(2.0) - 16, "звисаючий (центр)", size=11, bold=True, color=NEG))
    f.append(_dot(cx, DY(-1.9), POS))
    f.append(text(cx, DY(-1.9) + 22, "перевернутий (сідло)", size=11, bold=True, color=POS))
    # стрілка «додаємо тертя» — зсув уліво
    f.append(arrow(cx - 6, DY(2.0) + 8, TX(-1.2), DY(2.0) + 8, color=MUTED, sw=2.0))
    f.append(text((cx + TX(-1.2)) / 2, DY(2.0) + 22, "додаємо тертя", size=10.5, color=MUTED))
    return render(os.path.join(IMG, "trace-det.svg"), W, H, *f)


# Підсилення й фаза петлі, запас фази
def fig_loop_phase():
    W, H = 840, 525
    x0, x1 = 110, 740
    xc = 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Петля на межі: де підсилення падає до 1 і скільки фази лишилось до зриву",
                  size=14.5, bold=True))
    # верхня панель — |L|
    tb_x, tb_y, tb_w, tb_h = 90, 60, 670, 180
    f.append(rect(tb_x, tb_y, tb_w, tb_h, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=5))
    f.append(text(tb_x + 12, tb_y + 22, "підсилення петлі |L|", size=12, bold=True, anchor="start"))

    def mag(u):
        return (tb_y + 30) + (tb_h - 56) * (u ** 0.85)

    N = 120
    pts = []
    for i in range(N + 1):
        u = i / N
        pts.append((x0 + (x1 - x0) * u, mag(u)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))
    uc = (xc - x0) / (x1 - x0)
    y1 = mag(uc)
    f.append(line(tb_x + 6, y1, tb_x + tb_w - 6, y1, color=MUTED, sw=1.2, dash="6,5"))
    f.append(text(tb_x + tb_w - 4, y1 - 6, "|L| = 1", size=11, color=MUTED, anchor="end"))
    f.append(_dot(xc, y1, INK, r=5))
    # нижня панель — фаза
    pb_x, pb_y, pb_w, pb_h = 90, 300, 670, 175
    f.append(rect(pb_x, pb_y, pb_w, pb_h, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=5))
    f.append(text(pb_x + 12, pb_y + 22, "фаза петлі ∠L", size=12, bold=True, anchor="start"))

    def PHY(phi):
        return 326 + (-phi) * 0.756

    def phase(u):
        return max(-198.0, -20.0 - 190.0 * (u ** 1.15))

    pp = []
    for i in range(N + 1):
        u = i / N
        pp.append((x0 + (x1 - x0) * u, PHY(phase(u))))
    dp = "M %.1f %.1f " % pp[0] + " ".join("L %.1f %.1f" % p for p in pp[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dp, INK))
    y180 = PHY(-180)
    f.append(line(pb_x + 6, y180, pb_x + pb_w - 6, y180, color=POS, sw=1.4, dash="6,5"))
    f.append(text(pb_x + pb_w - 4, y180 - 6, "−180°: зрив знаку", size=10.5, color=POS, anchor="end"))
    yc = PHY(phase(uc))
    f.append(_dot(xc, yc, INK, r=5))
    # спільна вертикаль ω_c
    f.append(line(xc, tb_y, xc, pb_y + pb_h, color=MUTED, sw=1.1, dash="4,6"))
    f.append(text(xc, 272, "ω_c: частота зрізу (|L| = 1)", size=11, bold=True, color=MUTED))
    # дужка запасу фази (ліворуч від ω_c, щоб не лягти на криву)
    bx = 454
    mid = (yc + y180) / 2
    f.append(line(bx, yc, xc, yc, color=MUTED, sw=0.8))
    f.append(arrow(bx, mid, bx, yc, color=INK, sw=1.6))
    f.append(arrow(bx, mid, bx, y180, color=INK, sw=1.6))
    f.append(text(bx - 8, mid - 4, "запас фази", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(bx - 8, mid + 12, "≈ 60°", size=10.5, color=INK, anchor="end"))
    f.append(text(W / 2, 505, "частота ω (логарифмічна шкала) →", size=11, color=MUTED))
    return render(os.path.join(IMG, "loop-phase.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_landscape(), fig_loop(), fig_regimes(),
          fig_euler_step(), fig_delay_onset(), fig_saturation(), fig_timeline(),
          fig_lambda_plane(), fig_trace_det(), fig_loop_phase()]
    print("written:")
    for p in ps:
        print("  ", p)
