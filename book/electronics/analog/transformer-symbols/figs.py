# -*- coding: utf-8 -*-
"""Фігури до статті «Символи трансформаторів і зв'язаних котушок».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CARD_FILL = "#f6f8fc"
CARD_STK  = "#dcdcdc"
WIRE_SW   = 2.0


def wire(x1, y1, x2, y2, sw=WIRE_SW, color=INK):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, color, sw))


def card(x, y, w, h):
    return rect(x, y, w, h, fill=CARD_FILL, stroke=CARD_STK, sw=1.4, rx=8)


def dot(cx, cy, r=4.5, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, color)


# ── Вертикальна обмотка: стовпчик півкіл (bumps) уздовж осі x=cx ─────────────
def coil_v(cx, top, n=4, bump=12, side=+1, sw=2.2, color=INK):
    """Малює n півкіл одне над одним; side=+1 — горби вправо, -1 — вліво.
    Повертає (svg, y_bottom). Верхній і нижній виводи додаються окремо."""
    out = []
    y = top
    for i in range(n):
        # півколо: від (cx,y) до (cx,y+bump), вигин у бік side
        rx = bump * 0.62
        sweep = 1 if side > 0 else 0
        out.append('<path d="M %.1f,%.1f A %.1f %.1f 0 0 %d %.1f,%.1f" '
                   'fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (cx, y, rx, bump / 2.0, sweep, cx, y + bump, color, sw))
        y += bump
    return "".join(out), y


def core_lines(cx, y0, y1, style="iron"):
    """Лінії осердя між двома обмотками: 'iron' — дві суцільні,
    'ferrite' — дві штрихові, 'air' — нічого."""
    if style == "air":
        return ""
    x1, x2 = cx - 3, cx + 3
    if style == "iron":
        return (wire(x1, y0, x1, y1, sw=2.4) + wire(x2, y0, x2, y1, sw=2.4))
    # ferrite — штрихові
    d = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
         'stroke-width="2.4" stroke-dasharray="5,4"/>')
    return (d % (x1, y0, x1, y1, INK)) + (d % (x2, y0, x2, y1, INK))


def transformer(cx, cy, np_=4, ns=4, core="iron", dot_p="top", dot_s="top",
                bump=12, gap=26, lead=18, sw=2.2):
    """Базовий трансформатор: ліва обмотка (первинна) горбами вправо,
    права (вторинна) горбами вліво; між ними осердя.
    dot_p/dot_s ∈ {'top','bottom',None} — де крапка фазування.
    Повертає (svg, dict-із-координатами-виводів)."""
    out = []
    hp = np_ * bump
    hs = ns * bump
    h = max(hp, hs)
    topP = cy - hp / 2
    topS = cy - hs / 2
    xP = cx - gap / 2
    xS = cx + gap / 2

    cP, botP = coil_v(xP, topP, n=np_, bump=bump, side=+1, sw=sw)
    cS, botS = coil_v(xS, topS, n=ns, bump=bump, side=-1, sw=sw)
    out.append(cP)
    out.append(cS)
    # осердя
    y0 = cy - h / 2
    y1 = cy + h / 2
    out.append(core_lines(cx, y0, y1, core))
    # виводи (горизонтальні «ніжки»)
    out.append(wire(xP, topP, xP - lead, topP))
    out.append(wire(xP, botP, xP - lead, botP))
    out.append(wire(xS, topS, xS + lead, topS))
    out.append(wire(xS, botS, xS + lead, botS))

    def place_dot(x, yt, yb, where, off):
        if where == "top":
            return dot(x + off, yt - 2)
        if where == "bottom":
            return dot(x + off, yb + 2)
        return ""
    if dot_p:
        out.append(place_dot(xP, topP, botP, dot_p, -9))
    if dot_s:
        out.append(place_dot(xS, topS, botS, dot_s, +9))

    coords = dict(xP=xP, xS=xS, topP=topP, botP=botP, topS=topS, botS=botS,
                  leadPx=xP - lead, leadSx=xS + lead, cx=cx, cy=cy)
    return "".join(out), coords


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — анатомія символу + три осердя
# ════════════════════════════════════════════════════════════════════════════
def fig_anatomy():
    W, H = 760, 430
    frags = [text(W / 2, 28, "Символ трансформатора: дві обмотки й осердя між ними",
                  size=17, bold=True)]

    # ── велика анатомічна панель ──
    px, py, pw, ph = 60, 56, 360, 300
    frags.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=CARD_STK, sw=1.4, rx=10))
    bx, by = px + pw / 2 - 28, py + ph / 2 + 6
    tsvg, c = transformer(bx, by, np_=4, ns=3, core="iron",
                          dot_p="top", dot_s="top", bump=18, gap=30, lead=26, sw=2.4)
    frags.append(tsvg)

    # підписи-виноски
    frags.append(text(c["leadPx"] - 6, c["topP"] - 6, "первинна", size=12,
                      color=NEG, anchor="end", bold=True))
    frags.append(text(c["leadSx"] + 6, c["topS"] - 6, "вторинна", size=12,
                      color=POS, anchor="start", bold=True))
    # осердя — стрілка від підпису
    frags.append(arrow(bx + 80, by - 70, bx + 6, by - 40, color=MUTED, sw=1.6))
    frags.append(text(bx + 86, by - 74, "осердя", size=12, color=MUTED,
                      anchor="start", bold=True))
    # крапки
    frags.append(arrow(c["xP"] - 50, c["topP"] + 40, c["xP"] - 12, c["topP"] - 2,
                       color=FIELD, sw=1.6))
    frags.append(text(c["xP"] - 54, c["topP"] + 46, "крапки", size=12, color=FIELD,
                      anchor="end", bold=True))
    frags.append(text(c["xP"] - 54, c["topP"] + 62, "фазування", size=12, color=FIELD,
                      anchor="end", bold=True))

    # ── права колонка: три осердя ──
    items = [("Дві суцільні лінії", "залізо / сталь · 50 Гц", "iron"),
             ("Дві штрихові лінії", "ферит · десятки кГц", "ferrite"),
             ("Лінії немає", "повітря · радіочастоти", "air")]
    cx0 = 560
    cys = [120, 230, 340]
    frags.append(text(cx0, 86, "Що між обмотками — те й осердя", size=12.5,
                      color=INK, bold=True))
    for (t1, t2, st), cyy in zip(items, cys):
        ts, _ = transformer(cx0, cyy, np_=3, ns=3, core=st,
                            dot_p=None, dot_s=None, bump=12, gap=24, lead=14, sw=2.0)
        frags.append(ts)
        frags.append(text(cx0 + 64, cyy - 6, t1, size=11.5, color=INK,
                          anchor="start", bold=True))
        frags.append(text(cx0 + 64, cyy + 10, t2, size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *frags)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — крапки фазування: ті самі обмотки, крапку перенесли — вихід перевернувся
# ════════════════════════════════════════════════════════════════════════════
def sine(cx, cy, w, amp, inv=False, color=INK, sw=2.2, n=60):
    import math
    pts = []
    for i in range(n + 1):
        t = i / n
        x = cx - w / 2 + t * w
        s = math.sin(2 * math.pi * t)
        if inv:
            s = -s
        pts.append((x, cy - amp * s))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (poly, color, sw)


def fig_dots():
    W, H = 760, 360
    frags = [text(W / 2, 28, "Крапки кажуть фазу: перенесли крапку — вихід перевернувся",
                  size=16.5, bold=True)]

    panels = [("Крапки з одного боку", "вторинна напруга у фазі", "top", False, 60),
              ("Крапки з різних боків", "вторинна напруга у протифазі", "bottom", True, 400)]

    for title, sub, dot_s, inv, px in panels:
        pw, ph = 300, 280
        py = 52
        frags.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=CARD_STK, sw=1.4, rx=10))
        frags.append(text(px + pw / 2, py + 24, title, size=12.5, color=INK, bold=True))

        bx, by = px + 88, py + 150
        ts, c = transformer(bx, by, np_=4, ns=4, core="iron",
                            dot_p="top", dot_s=dot_s, bump=15, gap=26, lead=20, sw=2.3)
        frags.append(ts)

        # вхідна синусоїда ліворуч від первинної (маленька, вертикальна позначка «вхід»)
        frags.append(text(c["leadPx"] - 4, c["topP"] - 8, "вхід", size=10.5,
                          color=NEG, anchor="end", bold=True))
        # вихідна синусоїда праворуч
        sx = px + pw - 64
        frags.append(sine(sx, by, 70, 30, inv=False, color=NEG, sw=2.0))   # опорна (вхід)
        frags.append(sine(sx, by, 70, 22, inv=inv, color=POS, sw=2.6))     # вихід
        frags.append(text(sx, by + 58, sub, size=11, color=(POS if inv else FIELD),
                          anchor="middle", bold=True))
        frags.append(text(sx, py + 44, "вхід", size=10, color=NEG, anchor="middle"))
        frags.append(text(sx + 46, py + 44, "вихід", size=10, color=POS, anchor="middle"))

    render(os.path.join(IMG, "dots.svg"), W, H, *frags)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — родина: відвід, автотрансформатор, трансформатор струму
# ════════════════════════════════════════════════════════════════════════════
def center_tap(cx, cy):
    """Трансформатор із відводом посередині вторинної."""
    out, c = transformer(cx, cy, np_=4, ns=4, core="iron",
                         dot_p="top", dot_s="top", bump=13, gap=26, lead=16, sw=2.2)
    # середній відвід від вторинної
    ymid = (c["topS"] + c["botS"]) / 2
    out += wire(c["xS"], ymid, c["leadSx"], ymid)
    out += dot(c["xS"], ymid, r=3.2)
    return out


def autotransformer(cx, cy):
    """Одна обмотка з відводом — спільний провідник, без розв'язки."""
    bump = 13
    n = 6
    h = n * bump
    top = cy - h / 2
    xC = cx
    coil, bot = coil_v(xC, top, n=n, bump=bump, side=+1, sw=2.2)
    out = coil
    out += wire(xC, top, xC - 16, top)              # верх
    out += wire(xC, bot, xC - 16, bot)              # низ (спільний)
    # відвід посередині — праворуч
    ymid = top + 4 * bump
    out += wire(xC, ymid, xC + 18, ymid)
    out += dot(xC + bump * 0.62 + 1, top - 2, r=3.2)
    return out


def current_transformer(cx, cy):
    """ТС: товстий провідник-первинна крізь кільце-осердя, багатовиткова вторинна."""
    bump = 12
    n = 5
    h = n * bump
    top = cy - h / 2
    xS = cx + 8
    coil, bot = coil_v(xS, top, n=n, bump=bump, side=-1, sw=2.0)
    out = coil
    out += wire(xS, top, xS + 16, top)
    out += wire(xS, bot, xS + 16, bot)
    # осердя — кільце (коло) навколо первинного провідника
    out += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.2"/>' % (cx - 6, cy, h * 0.42, INK)
    # первинна — товстий прямий провідник крізь центр
    out += wire(cx - 6, cy - h / 2 - 8, cx - 6, cy + h / 2 + 8, sw=4.2)
    out += dot(xS - bump * 0.62 - 1, top - 2, r=3.2)
    return out


def fig_family():
    W, H = 760, 250
    frags = [text(W / 2, 28, "Та сама абетка: відвід, автотрансформатор, трансформатор струму",
                  size=16, bold=True)]
    cells = [(center_tap, "Відвід (середня точка)", "дві рівні половини вторинної"),
             (autotransformer, "Автотрансформатор", "обмотка СПІЛЬНА — без розв'язки"),
             (current_transformer, "Трансформатор струму", "первинна — провід крізь кільце")]
    cw = 233
    gap = 12
    margin = 27
    top = 50
    ch = 168
    for i, (fn, t1, t2) in enumerate(cells):
        x = margin + i * (cw + gap)
        frags.append(card(x, top, cw, ch))
        frags.append(fn(x + cw / 2, top + ch / 2 - 8))
        frags.append(text(x + cw / 2, top + ch - 30, t1, size=12, color=INK, bold=True))
        frags.append(text(x + cw / 2, top + ch - 13, t2, size=10.5, color=MUTED))
    render(os.path.join(IMG, "family.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_anatomy()
    fig_dots()
    fig_family()
    print("OK: фігури згенеровано у", IMG)
