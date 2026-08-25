# -*- coding: utf-8 -*-
"""Фігури до теми «Механічний резонанс».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CQ = [FIELD, NEG, POS]   # кольори трьох кривих за Q


# ── допоміжне ────────────────────────────────────────────────────────────────
def spring(x1, x2, y, coils=7, amp=13, lead=16):
    """Зигзаг-пружина від (x1,y) до (x2,y)."""
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def dashpot(x1, x2, y):
    """Демпфер (дашпот): циліндр біля стіни + поршень від маси."""
    out = []
    cyl_x, cyl_w, cyl_h = x1 + 14, 40, 30
    # шток від стіни до циліндра
    out.append(line(x1, y, cyl_x, y, color=INK, sw=2.2))
    # циліндр (відкритий праворуч): три сторони
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x + cyl_w, y - cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y + cyl_h / 2, cyl_x + cyl_w, y + cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x, y + cyl_h / 2, color=INK, sw=2.2))
    # поршень-плита всередині
    px = cyl_x + cyl_w - 12
    out.append(line(px, y - cyl_h / 2 + 4, px, y + cyl_h / 2 - 4, color=INK, sw=3.4))
    # шток поршня до маси
    out.append(line(px, y, x2, y, color=INK, sw=2.2))
    return "".join(out)


def wall(x, y1, y2, side=1):
    """Вертикальна стіна з штрихуванням (side=1 — штрихи праворуч)."""
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    step = 14
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.4))
        yy += step
    return "".join(out)


def ground(x1, x2, y):
    out = [line(x1, y, x2, y, color=INK, sw=3)]
    xx = x1 + 6
    while xx < x2:
        out.append(line(xx, y, xx - 12, y + 12, color=MUTED, sw=1.4))
        xx += 14
    return "".join(out)


def amp_resp(r, Q):
    """Нормоване підсилення A/A₀ вимушеного загасного осцилятора."""
    return 1.0 / math.sqrt((1 - r * r) ** 2 + (r / Q) ** 2)


def phase_resp(r, Q):
    """Відставання фази (радіани, 0…π)."""
    return math.atan2(r / Q, 1 - r * r)


# ── Фігура 1: рушій — маса, пружина, демпфер, зовнішня сила ──────────────────
def fig_driven_model():
    W, H = 760, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Модель резонансу: маса на пружині з демпфером і зовнішньою силою",
                  size=16, bold=True))

    wx = 70                       # стіна
    gy = 250                      # підлога
    f.append(wall(wx, 90, gy))
    f.append(ground(wx, W - 40, gy))

    # маса
    mx, my, mw, mh = 470, 175, 120, 92
    f.append(rect(mx, my - mh / 2, mw, mh, fill="#e8edf3", stroke=INK, sw=2, rx=6))
    f.append(text(mx + mw / 2, my + 8, "m", size=26, bold=True))

    # пружина (верхній ряд) і демпфер (нижній ряд) від стіни до маси
    f.append(spring(wx, mx, my - 24))
    f.append(text((wx + mx) / 2, my - 24 - 26, "пружина k  (жорсткість)", size=13,
                  color=INK))
    f.append(dashpot(wx, mx, my + 26))
    f.append(text((wx + mx) / 2 + 6, my + 26 + 34, "демпфер c  (втрати)", size=13,
                  color=INK))

    # зовнішня сила праворуч
    fx0 = mx + mw
    f.append(arrow(fx0 + 6, my, fx0 + 92, my, color=POS, sw=3.4))
    f.append(text(fx0 + 100, my - 8, "F(t) = F₀·cos(ω t)", size=14, bold=True,
                  color=POS, anchor="start"))
    f.append(text(fx0 + 100, my + 14, "зовнішня «розгойдувальна» сила", size=11,
                  color=MUTED, anchor="start"))

    # координата зміщення x
    f.append(arrow(mx + mw / 2, gy - 6, mx + mw / 2 + 60, gy - 6, color=INK, sw=1.6))
    f.append(text(mx + mw / 2 + 66, gy - 2, "x", size=14, italic=True, anchor="start"))

    # плашка з власною частотою
    b, bw, bh = textbox(210, 300, "власна частота:  ω₀ = √(k / m)", size=13, pad=9,
                        fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "driven-model.svg"), W, H, *f)


# ── Фігура 2: крива резонансу — підсилення проти частоти для трьох Q ─────────
def fig_resonance_curve():
    W, H = 800, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Крива резонансу: підсилення різко зростає, коли ω наближається до ω₀",
                  size=16, bold=True))

    ox, oy = 96, 400              # початок осей
    rx, ty = 748, 70             # праворуч / вершина
    rmax = 3.0
    amax = 7.0

    def PX(r):
        return ox + (rx - ox) * (r / rmax)

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    # осі
    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω₀  →", size=13, anchor="end"))
    f.append(text(ox - 66, ty + 30, "A / A₀", size=13, bold=True, anchor="start"))
    f.append(text(ox - 66, ty + 48, "(підсилення)", size=11, color=MUTED, anchor="start"))

    # риски осей
    for rr in (0, 1, 2, 3):
        f.append(line(PX(rr), oy, PX(rr), oy + 6, color=INK, sw=1.4))
        f.append(text(PX(rr), oy + 22, "%d" % rr, size=12, color=MUTED))
    for aa in (1, 3, 5, 7):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.4))
        f.append(text(ox - 14, PY(aa) + 4, "%d" % aa, size=12, color=MUTED, anchor="end"))

    # лінія статичного прогину A₀ = 1
    f.append(line(ox, PY(1), rx, PY(1), color=MUTED, sw=1.2, dash="5,6"))
    f.append(text(rx - 4, PY(1) - 8, "A₀ — статичний прогин (ω→0)", size=11,
                  color=MUTED, anchor="end"))
    # вертикаль ω=ω₀
    f.append(line(PX(1), oy, PX(1), ty + 10, color=MUTED, sw=1.2, dash="4,6"))
    f.append(text(PX(1), ty + 4, "ω = ω₀", size=12, color=MUTED))

    Qs = [1.2, 2.5, 6.0]
    for k, Q in enumerate(Qs):
        pts = []
        r = 0.02
        while r <= rmax + 1e-9:
            pts.append((PX(r), PY(amp_resp(r, Q))))
            r += 0.02
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, CQ[k]))

    # підписи кривих (рознесені, з запасом)
    f.append(text(PX(1.02) + 8, PY(amp_resp(1.0, 6.0)) + 4, "Q = 6  (слабке загасання — гострий пік)",
                  size=12, bold=True, color=CQ[2], anchor="start"))
    f.append(text(PX(1.30), PY(amp_resp(1.15, 2.5)) - 6, "Q = 2.5", size=12, bold=True,
                  color=CQ[1], anchor="start"))
    f.append(text(PX(1.7), PY(amp_resp(1.5, 1.2)) - 8, "Q = 1.2  (сильне загасання)",
                  size=12, bold=True, color=CQ[0], anchor="start"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "висота піка ≈ Q · A₀   ·   ширина піка ≈ ω₀ / Q",
                        size=13, pad=9, fill=FILL, stroke=LINE, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "resonance-curve.svg"), W, H, *f)


# ── Фігура 3: поворот фази від 0 через 90° до 180° ──────────────────────────
def fig_phase_curve():
    W, H = 800, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Поворот фази: відгук відстає від сили — 0° → 90° → 180°",
                  size=16, bold=True))

    ox, oy = 96, 360
    rx, ty = 748, 74
    rmax = 3.0

    def PX(r):
        return ox + (rx - ox) * (r / rmax)

    def PY(deg):
        return oy - (oy - ty) * (deg / 180.0)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω₀  →", size=13, anchor="end"))
    f.append(text(ox - 70, ty + 22, "відставання", size=12, bold=True, anchor="start"))
    f.append(text(ox - 70, ty + 40, "фази φ", size=12, bold=True, anchor="start"))

    for rr in (0, 1, 2, 3):
        f.append(line(PX(rr), oy, PX(rr), oy + 6, color=INK, sw=1.4))
        f.append(text(PX(rr), oy + 22, "%d" % rr, size=12, color=MUTED))
    for dd in (0, 90, 180):
        f.append(line(ox - 6, PY(dd), ox, PY(dd), color=INK, sw=1.4))
        f.append(text(ox - 14, PY(dd) + 4, "%d°" % dd, size=12, color=MUTED, anchor="end"))

    # горизонталь 90° і вертикаль ω₀
    f.append(line(ox, PY(90), rx, PY(90), color=MUTED, sw=1.2, dash="5,6"))
    f.append(line(PX(1), oy, PX(1), ty + 10, color=MUTED, sw=1.2, dash="4,6"))
    f.append(text(PX(1), ty + 4, "ω = ω₀", size=12, color=MUTED))

    Qs = [1.2, 2.5, 6.0]
    for k, Q in enumerate(Qs):
        pts = []
        r = 0.02
        while r <= rmax + 1e-9:
            pts.append((PX(r), PY(math.degrees(phase_resp(r, Q)))))
            r += 0.02
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, CQ[k]))
    f.append(text(PX(2.3), PY(150) - 4, "круті криві — це велике Q", size=12,
                  color=MUTED, anchor="start"))

    # три словесні мітки режимів
    f.append(text(PX(0.42), PY(18) + 4, "нижче ω₀:\nвідгук у фазі", size=11, color=CQ[0]))
    f.append(text(PX(1.0), PY(96) - 30, "на ω₀: рівно 90°\n(сила в такт зі швидкістю)",
                  size=11, color=INK))
    f.append(text(PX(2.5), PY(168) + 4, "вище ω₀:\nу протифазі", size=11, color=CQ[2]))
    return render(os.path.join(IMG, "phase-curve.svg"), W, H, *f)


# ── Фігура 4: накопичення — амплітуда росте й виходить на межу ───────────────
def fig_buildup():
    W, H = 800, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Накопичення на резонансі: щоцикла сила підкачує енергію",
                  size=16, bold=True))

    ox, oy = 70, 185             # вісь часу проходить посередині
    rx = 700
    top, bot = 60, 310
    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.7))
    f.append(text(rx + 4, oy + 22, "час →", size=12, anchor="end"))
    f.append(text(ox - 8, top + 4, "x", size=13, italic=True, anchor="end"))

    Amax = (oy - top) - 8
    tau = 2.4                    # стала часу наростання (у періодах)
    ncyc = 9.0
    w = 2 * math.pi
    pts = []
    env_top = []
    env_bot = []
    N = 900
    for i in range(N + 1):
        t = ncyc * i / N
        env = Amax * (1 - math.exp(-t / tau))
        x = env * math.sin(w * t)
        px = ox + (rx - ox) * (t / ncyc)
        pts.append((px, oy - x))
        env_top.append((px, oy - env))
        env_bot.append((px, oy + env))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, POS))
    # обвідні (пунктир)
    for env in (env_top, env_bot):
        de = "M %.1f %.1f " % env[0] + " ".join("L %.1f %.1f" % p for p in env[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                 'stroke-dasharray="6,6"/>' % (de, MUTED))

    # лінія стелі
    f.append(line(ox, oy - Amax, rx, oy - Amax, color=FIELD, sw=1.4, dash="2,7"))
    f.append(text(rx - 4, oy - Amax - 8, "стеля: підкачка = втрати (задає загасання)",
                  size=11, color=FIELD, anchor="end"))
    f.append(text(ox + 150, bot - 4, "спершу амплітуда росте майже лінійно…",
                  size=11, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, "buildup.svg"), W, H, *f)


# ── Фігура (до hist-bridges): дві різні причини одного сплеску ────────────────
def fig_forced_vs_selfexcited():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому «резонанс» — це не одне явище", size=16, bold=True))
    f.append(line(W / 2, 52, W / 2, H - 18, color=LINE, sw=1.1, dash="3,7"))

    # ── ліва панель: вимушений резонанс (сторонній двигун, один бік) ──
    lx = 225
    f.append(text(lx, 74, "Вимушений резонанс", size=15, bold=True, color=NEG))
    f.append(text(lx, 93, "приклад: солдати в ногу", size=12, color=MUTED))
    b1, _, _ = textbox(lx, 150, "зовнішній двигун\nF₀·cos(ω t)\nчастота ω — стороння",
                       size=12, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.6)
    f.append(b1)
    f.append(arrow(lx, 187, lx, 249, color=NEG, sw=2.6))
    f.append(text(lx + 18, 222, "штовхає", size=11, color=MUTED, anchor="start"))
    b2, _, _ = textbox(lx, 287, "система (міст)\nвласна частота ω₀",
                       size=12, pad=10, fill=FILL, stroke=INK, sw=1.6, bold=True)
    f.append(b2)
    b3, _, _ = textbox(lx, 392, "сплеск ЛИШЕ коли ω ≈ ω₀\nприбери ту частоту — зникне",
                       size=11, pad=9, fill="#f7f7f7", stroke=LINE, sw=1.2)
    f.append(b3)

    # ── права панель: самозбудні коливання (зворотний зв'язок, петля) ──
    rxp = 655
    f.append(text(rxp, 74, "Самозбудні коливання", size=15, bold=True, color=POS))
    f.append(text(rxp, 93, "приклад: флатер Такоми, юрба Міленіуму", size=12, color=MUTED))
    c1, _, _ = textbox(560, 215, "система (міст)\nрух x(t)",
                       size=12, pad=10, fill=FILL, stroke=INK, sw=1.6, bold=True)
    f.append(c1)
    c2, _, _ = textbox(762, 215, "рівне джерело\nвітер / крок юрби",
                       size=12, pad=10, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(c2)
    # петля зворотного зв'язку в проміжку між боксами
    f.append(text(657, 184, "зв'язок", size=11, color=POS))
    f.append(arrow(619, 208, 691, 208, color=POS, sw=2.4))
    f.append(arrow(691, 222, 619, 222, color=POS, sw=2.4))
    f.append(plus(657, 215, r=7))
    b4, _, _ = textbox(rxp, 392, "рух САМ породжує силу, що штовхає в такт руху:\n"
                                 "від'ємне загасання, енергія з рівного джерела",
                       size=11, pad=9, fill="#f7f7f7", stroke=LINE, sw=1.2)
    f.append(b4)
    return render(os.path.join(IMG, "hist-forced-vs-selfexcited.svg"), W, H, *f)


# ── Фігура (до hist-bridges): часова шкала — тиха знахідка, гучна ганьба ──────
def fig_timeline():
    W, H = 900, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Триста років резонансу: тиха знахідка, гучна ганьба, плутанина",
                  size=16, bold=True))
    f.append(text(W / 2, 50, "події за справжньою шкалою часу", size=12, color=MUTED))

    ax0, ax1, ay = 90, 810, 250
    y0, y1 = 1620, 2010

    def YR(y):
        return ax0 + (y - y0) * (ax1 - ax0) / (y1 - y0)

    # вісь часу з рисками
    f.append(line(ax0 - 10, ay, ax1 + 18, ay, color=INK, sw=2))
    f.append(arrow(ax1 + 6, ay, ax1 + 24, ay, color=INK, sw=2))
    for yr in (1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000):
        x = YR(yr)
        f.append(line(x, ay - 4, x, ay + 4, color=MUTED, sw=1.2))
        f.append(text(x, ay + 18, str(yr), size=9, color=MUTED))

    # брекет «≈ 200 років тихо» між Галілеєм і Броутоном (над віссю)
    gx0, gx1, by = YR(1638), YR(1831), 214
    f.append(line(gx0, by, gx1, by, color=MUTED, sw=1.3))
    f.append(line(gx0, by - 5, gx0, by + 5, color=MUTED, sw=1.3))
    f.append(line(gx1, by - 5, gx1, by + 5, color=MUTED, sw=1.3))
    f.append(text((gx0 + gx1) / 2, by - 6, "≈ 200 років поняття лежить тихо",
                  size=11, color=MUTED))

    events = [
        (1638, "1638 · Галілей", "«вчасність б'є силу»", "up"),
        (1831, "1831 · Броутон", "рота в ногу → «збити ногу»", "down"),
        (1850, "1850 · Анже", "226 загиблих: буря + іржа", "up"),
        (1940, "1940 · Такома", "НЕ резонанс, а флатер", "down"),
        (2000, "2000 · Міленіум", "юрба в такт: синхронізація", "up"),
    ]
    for yr, t1, t2, side in events:
        x = YR(yr)
        odd = yr in (1940, 2000)                 # «не той підручниковий резонанс»
        f.append(circle(x, ay, 5, fill=(POS if odd else INK), stroke=INK, sw=1.4))
        if side == "up":
            f.append(line(x, ay - 5, x, 172, color=MUTED, sw=1.1))
            cy = 150
        else:
            f.append(line(x, ay + 5, x, 330, color=MUTED, sw=1.1))
            cy = 352
        b, _, _ = textbox(x, cy, t1 + "\n" + t2, size=11, pad=8,
                          fill=FILL, stroke=(POS if odd else INK), sw=1.4)
        f.append(b)
    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── math-вставка, фіг. 1: баланс фазорів (0° → 90° → 180°) ──────────────────
def _phasor_panel(f, cx, cy, r, Q, reg):
    L, axh, up, dn, ra = 92, 106, 118, 26, 30
    a = math.atan2(r / Q, 1 - r * r)          # φ у радіанах (0…π)
    ca, sa = math.cos(a), math.sin(a)
    # осі: Re — горизонтальна (вона ж вісь зміщення x), Im — вертикальна
    f.append(arrow(cx - axh, cy, cx + axh, cy, color=MUTED, sw=1.2))
    f.append(arrow(cx, cy + dn, cx, cy - up, color=MUTED, sw=1.2))
    f.append(text(cx + axh, cy + 16, "Re (вісь x)", size=10, color=MUTED, anchor="end"))
    f.append(text(cx + 10, cy - up + 4, "Im", size=10, color=MUTED, anchor="start"))
    Fx, Fy = cx + L * ca, cy - L * sa
    # катети трикутника (пунктир)
    f.append(line(cx, cy, Fx, cy, color=NEG, sw=2.0, dash="4,4"))       # пружно-інерційний
    f.append(line(Fx, cy, Fx, Fy, color=FIELD, sw=2.0, dash="4,4"))     # загасний
    # сама сила
    f.append(arrow(cx, cy, Fx, Fy, color=POS, sw=3.2))
    f.append(text(Fx + (12 if ca >= 0 else -12), Fy - 8, "F₀", size=14, bold=True,
                  color=POS, anchor="start" if ca >= 0 else "end"))
    # дуга кута φ
    pts = [(cx + ra * math.cos(a * i / 24), cy - ra * math.sin(a * i / 24))
           for i in range(25)]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, INK))
    mt = a / 2
    f.append(text(cx + (ra + 20) * math.cos(mt), cy - (ra + 20) * math.sin(mt) + 4,
                  "φ", size=14, italic=True, color=INK))
    f.append(text(cx, cy + dn + 32, reg, size=13, bold=True))
    f.append(text(cx, cy + dn + 52, "φ ≈ %d°" % round(math.degrees(a)), size=12, color=MUTED))


def fig_phasor_balance():
    W, H = 820, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Баланс фазорів: сила F₀ — гіпотенуза, її нахил — відставання φ",
                  size=16, bold=True))
    cy = 178
    _phasor_panel(f, 150, cy, 0.70, 2.0, "ω < ω₀")
    _phasor_panel(f, 410, cy, 1.00, 2.0, "ω = ω₀")
    _phasor_panel(f, 670, cy, 1.40, 2.0, "ω > ω₀")
    b, bw, bh = textbox(W / 2, H - 40,
                        "F₀ (червона) — зовнішня сила, гіпотенуза трикутника\n"
                        "синій катет = пружно-інерційна k(1−r²)A (уздовж x)   ·   "
                        "зелений катет = загасна k(r/Q)A (уздовж швидкості)\n"
                        "A = (F₀/k)/√((1−r²)²+(r/Q)²) — довжина;   φ = atan2(r/Q, 1−r²) — нахил",
                        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "phasor-balance.svg"), W, H, *f)


# ── math-вставка, фіг. 2: три близькі частоти ω_r < ω_d < ω₀ ────────────────
def fig_three_frequencies():
    W, H = 800, 430
    Q = 1.6
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три близькі, але різні частоти коло ω₀", size=16, bold=True))
    ox, oy, rx, ty = 92, 350, 760, 84
    r0, r1, amax = 0.5, 1.5, 2.0

    def PX(r):
        return ox + (rx - ox) * ((r - r0) / (r1 - r0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω₀  →", size=13, anchor="end"))
    f.append(text(ox - 60, ty + 24, "A / A₀", size=13, bold=True, anchor="start"))
    for rr in (0.5, 0.75, 1.0, 1.25, 1.5):
        f.append(line(PX(rr), oy, PX(rr), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(rr), oy + 22, "%.2f" % rr, size=11, color=MUTED))
    for aa in (1, 2):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 12, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))
    f.append(line(ox, PY(1), rx, PY(1), color=MUTED, sw=1.1, dash="5,6"))

    pts = []
    r = r0
    while r <= r1 + 1e-9:
        pts.append((PX(r), PY(amp_resp(r, Q))))
        r += 0.005
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))

    rr_r = math.sqrt(1 - 1 / (2 * Q * Q))
    rr_d = math.sqrt(1 - 1 / (4 * Q * Q))
    for rf, col in ((rr_r, POS), (rr_d, NEG), (1.0, FIELD)):
        ytop = PY(amp_resp(rf, Q)) - 6
        f.append(line(PX(rf), oy, PX(rf), ytop, color=col, sw=1.8, dash="3,4"))
    f.append(circle(PX(rr_r), PY(amp_resp(rr_r, Q)), 4.2, fill=POS, stroke=POS, sw=1))

    # легенда (ліворуч від ліній, що тісняться коло r≈0.9…1.0)
    lx, ly = ox + 14, ty + 6
    rows = [(POS, "ω_r — пік зміщення"),
            (NEG, "ω_d — вільний дзвін"),
            (FIELD, "ω₀ — пік швидкості (φ=90°)")]
    for i, (col, tx) in enumerate(rows):
        yy = ly + i * 22
        f.append(line(lx, yy - 4, lx + 22, yy - 4, color=col, sw=3))
        f.append(text(lx + 30, yy, tx, size=12, color=INK, anchor="start"))
    f.append(text(lx, ly + 3 * 22 + 6, "Q = 1.6 — навмисно мале, щоб рознести лінії;",
                  size=11, color=MUTED, anchor="start"))
    f.append(text(lx, ly + 3 * 22 + 24, "з ростом Q усі три зливаються в ω₀.",
                  size=11, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, "three-frequencies.svg"), W, H, *f)


# ── math-вставка, фіг. 3: смуга половинної потужності Δω = ω₀/Q ──────────────
def fig_half_power():
    W, H = 800, 420
    Q = 5.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Смуга за рівнем половинної потужності:  Δω = ω₀ / Q",
                  size=16, bold=True))
    ox, oy, rx, ty = 92, 350, 760, 82
    r0, r1, amax = 0.6, 1.4, 6.0

    def PX(r):
        return ox + (rx - ox) * ((r - r0) / (r1 - r0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω₀  →", size=13, anchor="end"))
    f.append(text(ox - 60, ty + 24, "A / A₀", size=13, bold=True, anchor="start"))
    for rr in (0.6, 0.8, 1.0, 1.2, 1.4):
        f.append(line(PX(rr), oy, PX(rr), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(rr), oy + 22, "%.1f" % rr, size=11, color=MUTED))
    for aa in (1, 2, 3, 4, 5, 6):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 12, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))
    f.append(line(ox, PY(1), rx, PY(1), color=MUTED, sw=1.1, dash="5,6"))
    f.append(text(rx - 4, PY(1) - 8, "A₀  (r → 0)", size=11, color=MUTED, anchor="end"))

    pts = []
    r = r0
    while r <= r1 + 1e-9:
        pts.append((PX(r), PY(amp_resp(r, Q))))
        r += 0.004
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))

    rpk = math.sqrt(1 - 1 / (2 * Q * Q))
    apk = amp_resp(rpk, Q)
    f.append(circle(PX(rpk), PY(apk), 4.2, fill=POS, stroke=POS, sw=1))
    f.append(text(PX(rpk), PY(apk) - 12, "A_max ≈ Q", size=12, bold=True, color=POS))

    half = apk / math.sqrt(2)
    # перетини кривої з рівнем половинної потужності
    xs = []
    r = r0
    prev = amp_resp(r, Q) - half
    while r <= r1:
        cur = amp_resp(r, Q) - half
        if (prev < 0) != (cur < 0):
            xs.append(r)
        prev = cur
        r += 0.0008
    w1, w2 = min(xs), max(xs)

    f.append(line(PX(r0), PY(half), PX(r1), PY(half), color=NEG, sw=1.4, dash="6,5"))
    f.append(text(PX(r1) - 4, PY(half) - 8, "A_max/√2   (−3 дБ, півпотужності)",
                  size=11, color=NEG, anchor="end"))
    for wv, lab in ((w1, "ω₁"), (w2, "ω₂")):
        f.append(line(PX(wv), oy, PX(wv), PY(half), color=NEG, sw=1.3, dash="3,4"))
        f.append(text(PX(wv), PY(half) - 10, lab, size=12, bold=True, color=NEG))
    f.append(line(PX(1), oy, PX(1), PY(apk) - 8, color=MUTED, sw=1.2, dash="4,6"))
    f.append(text(PX(1) + 8, PY(apk) + 8, "ω₀", size=12, color=MUTED, anchor="start"))

    # двобічна стрілка ширини Δω (у вільному просторі під піком)
    yb = PY(half) + 24
    f.append(arrow(PX(w1), yb, PX(w2), yb, color=INK, sw=1.8))
    f.append(arrow(PX(w2), yb, PX(w1), yb, color=INK, sw=1.8))
    f.append(text((PX(w1) + PX(w2)) / 2, yb + 18, "Δω = ω₀ / Q", size=13, bold=True))
    return render(os.path.join(IMG, "half-power.svg"), W, H, *f)


import cmath


# ── допоміжне для режектора (вставка proj-resonance-sweep) ───────────────────
def _notch_coeffs(f0, fs, Q):
    """Коефіцієнти режекторного біквада (RBJ), нормовані a0=1."""
    w0 = 2 * math.pi * f0 / fs
    alpha = math.sin(w0) / (2 * Q)
    cw = math.cos(w0)
    a0 = 1 + alpha
    return (1 / a0, -2 * cw / a0, 1 / a0, -2 * cw / a0, (1 - alpha) / a0)


def _H(coef, f, fs):
    """Комплексний відгук H(e^{jΩ}) на частоті f."""
    b0, b1, b2, a1, a2 = coef
    Om = 2 * math.pi * f / fs
    z1 = cmath.exp(-1j * Om)
    z2 = cmath.exp(-2j * Om)
    return (b0 + b1 * z1 + b2 * z2) / (1 + a1 * z1 + a2 * z2)


# ── Фігура 5 (proj): характеристика режектора — амплітуда (дБ) + фаза ────────
def fig_notch_response():
    W, H = 820, 560
    fs, f0, Qf = 8000.0, 63.7, 6.0
    coef = _notch_coeffs(f0, fs, Qf)
    fmax = 200.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Характеристика режектора: глибокий провал на fᵣ — і фазова ціна",
                  size=16, bold=True))

    ox, rx = 100, 776
    ty1, oy1 = 66, 268          # верхня панель — амплітуда
    dbmin, dbmax = -45.0, 5.0
    ty2, oy2 = 352, 508         # нижня панель — фаза
    phmax = 120.0

    def PX(fr):
        return ox + (rx - ox) * (fr / fmax)

    def PY1(db):
        db = max(dbmin, min(dbmax, db))
        return oy1 - (oy1 - ty1) * ((db - dbmin) / (dbmax - dbmin))

    mid2 = (ty2 + oy2) / 2

    def PY2(deg):
        deg = max(-phmax, min(phmax, deg))
        return mid2 - (oy2 - ty2) / 2 * (deg / phmax)

    for (tyy, oyy) in ((ty1, oy1), (ty2, oy2)):
        f.append(arrow(ox, oyy, rx + 6, oyy, color=INK, sw=1.6))
        f.append(arrow(ox, oyy, ox, tyy - 6, color=INK, sw=1.6))

    for fr in (0, 50, 100, 150, 200):
        f.append(line(PX(fr), oy1, PX(fr), oy1 + 5, color=INK, sw=1.2))
        f.append(line(PX(fr), oy2, PX(fr), oy2 + 5, color=INK, sw=1.2))
        f.append(text(PX(fr), oy2 + 22, "%d" % fr, size=11, color=MUTED))
    f.append(text(rx - 4, oy2 + 40, "частота, Гц  →", size=12, anchor="end"))

    for db in (0, -10, -20, -30, -40):
        f.append(line(ox - 5, PY1(db), ox, PY1(db), color=INK, sw=1.2))
        f.append(text(ox - 12, PY1(db) + 4, "%d" % db, size=10, color=MUTED, anchor="end"))
        f.append(line(ox, PY1(db), rx, PY1(db), color="#eef1f4", sw=1.0))
    f.append(text(ox - 8, ty1 - 14, "підсилення, дБ", size=12, bold=True, anchor="start"))

    for dd in (90, 0, -90):
        f.append(line(ox - 5, PY2(dd), ox, PY2(dd), color=INK, sw=1.2))
        f.append(text(ox - 12, PY2(dd) + 4, "%d°" % dd, size=10, color=MUTED, anchor="end"))
        f.append(line(ox, PY2(dd), rx, PY2(dd), color="#eef1f4", sw=1.0))
    f.append(text(ox - 8, ty2 - 14, "фаза", size=12, bold=True, anchor="start"))

    f.append(line(PX(f0), oy1, PX(f0), ty1 + 8, color=POS, sw=1.2, dash="4,5"))
    f.append(line(PX(f0), oy2, PX(f0), ty2 + 8, color=POS, sw=1.2, dash="4,5"))
    f.append(text(PX(f0), ty1 - 14, "fᵣ = 63.7 Гц", size=12, bold=True, color=POS))

    pts = []
    fr = 0.5
    while fr <= fmax + 1e-9:
        mag = abs(_H(coef, fr, fs))
        db = 20 * math.log10(mag) if mag > 1e-9 else dbmin
        pts.append((PX(fr), PY1(db)))
        fr += 0.25
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, NEG))
    f.append(text(PX(108), PY1(2.2), "0 дБ — сигнал проходить недоторканим", size=11,
                  color=MUTED, anchor="start"))
    f.append(text(PX(64) + 10, PY1(-33), "виріз (ідеально → −∞)", size=11, color=POS,
                  anchor="start"))

    pts = []
    fr = 0.5
    while fr <= fmax + 1e-9:
        deg = math.degrees(cmath.phase(_H(coef, fr, fs)))
        pts.append((PX(fr), PY2(deg)))
        fr += 0.25
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, FIELD))
    f.append(text(PX(98), PY2(-104), "круте фазове провалля тут = додаткова затримка",
                  size=11, color=FIELD, anchor="start"))
    return render(os.path.join(IMG, "notch-response.svg"), W, H, *f)


# ── Фігура 6 (proj): ланцюг сигналу гіро → режектор → ПІД ────────────────────
def _mini_spectrum(x, y, w, h, spike_frac=None):
    out = [rect(x, y, w, h, fill="#fbfcfd", stroke=LINE, sw=1.1, rx=4)]
    bx0, bx1 = x + 9, x + w - 7
    base, top = y + h - 11, y + 11
    out.append(line(bx0, base, bx1, base, color=MUTED, sw=1.0))
    out.append(line(bx0, base, bx0, top, color=MUTED, sw=1.0))
    pts = []
    n = 44
    for i in range(n + 1):
        fx = bx0 + (bx1 - bx0) * i / n
        fy = base - (3 + 2 * abs(math.sin(i * 1.7)))          # низький шумовий поміст
        if spike_frac is not None:
            dd = i / n - spike_frac
            fy -= (base - top - 4) * math.exp(-(dd * dd) / (2 * 0.022 ** 2))
        pts.append((fx, fy))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    col = POS if spike_frac is not None else FIELD
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7"/>' % (d, col))
    return "".join(out)


def fig_notch_chain():
    W, H = 900, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ланцюг сигналу: рамний резонанс вирізається дорогою до керування",
                  size=16, bold=True))

    by, bh = 178, 74            # ряд блоків
    f.append(fitbox(44, by, 152, bh, "Гіроскоп\n(кутова швидкість)", size=13, bold=True,
                    fill="#eef2f7"))
    f.append(fitbox(374, by, 176, bh, "Режектор (біквад)\nцентр = fᵣ\n8 кГц · на вісь",
                    size=12, bold=True, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(724, by, 140, bh, "ПІД-контур\n→ мотори", size=13, bold=True,
                    fill="#eef2f7"))

    f.append(arrow(198, by + bh / 2, 370, by + bh / 2, color=INK, sw=2.2))
    f.append(arrow(552, by + bh / 2, 720, by + bh / 2, color=INK, sw=2.2))

    f.append(_mini_spectrum(218, 92, 132, 66, spike_frac=0.34))
    f.append(text(284, 170, "сирий: сплеск на fᵣ", size=11, color=POS))
    f.append(_mini_spectrum(570, 92, 132, 66, spike_frac=None))
    f.append(text(636, 170, "чистий: піка нема", size=11, color=FIELD))

    b, bw, bh2 = textbox(W / 2, 338,
                         "рама резонує на fᵣ ≈ 64 Гц  →  біквад лишає весь сигнал, "
                         "вирізає лише цю смугу",
                         size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "notch-chain.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_driven_model(), fig_resonance_curve(), fig_phase_curve(), fig_buildup(),
          fig_forced_vs_selfexcited(), fig_timeline(),
          fig_phasor_balance(), fig_three_frequencies(), fig_half_power(),
          fig_notch_response(), fig_notch_chain()]
    print("written:")
    for p in ps:
        print("  ", p)
