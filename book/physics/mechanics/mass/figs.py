# -*- coding: utf-8 -*-
"""Фігури до теми «Маса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def hatch(x0, y0, x1, y1, step=14, color=MUTED, sw=1.0, dx=9, dy=9):
    """Штрихування вздовж лінії (лід/опора)."""
    out = [line(x0, y0, x1, y1, color=color, sw=1.6)]
    n = int(math.hypot(x1 - x0, y1 - y0) // step)
    if n <= 0:
        return "".join(out)
    ux, uy = (x1 - x0) / (n * step), (y1 - y0) / (n * step)
    for i in range(n + 1):
        px, py = x0 + ux * step * i, y0 + uy * step * i
        out.append(line(px, py, px - dx, py + dy, color=color, sw=sw))
    return "".join(out)


def coil_h(x0, x1, y, n, amp):
    """Горизонтальна пружинка-зигзаг (глюонна нитка)."""
    pts = [(x0, y)]
    seg = (x1 - x0) / (2 * n)
    for i in range(1, 2 * n):
        pts.append((x0 + seg * i, y + (amp if i % 2 else -amp)))
    pts.append((x1, y))
    return polyline(pts, color=FIELD, sw=2.0)


def coil_v(x, y0, y1, n, amp, color=INK):
    """Вертикальна пружинка-зигзаг (пружина під тілом)."""
    pts = [(x, y0)]
    seg = (y1 - y0) / (2 * n)
    for i in range(1, 2 * n):
        pts.append((x + (amp if i % 2 else -amp), y0 + seg * i))
    pts.append((x, y1))
    return polyline(pts, color=color, sw=2.0)


def sine(x0, x1, yc, amp, period, phase=0.0, color=INK, sw=2.4, steps=180):
    """Синусоїда x(t) уздовж осі часу: y = yc − amp·sin(2π(x−x0)/period + phase)."""
    pts = []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = yc - amp * math.sin(2 * math.pi * (x - x0) / period + phase)
        pts.append((x, y))
    return polyline(pts, color=color, sw=sw)


def cart(x, y, w, h, fill="#eef2fb", label=None, lsize=13):
    """Візок: кузов + два колеса; (x,y) — лівий-верхній кут кузова."""
    out = [rect(x, y, w, h, fill=fill, stroke=INK, sw=2, rx=6)]
    r = 9
    out.append(circle(x + w * 0.24, y + h + r - 2, r, fill="#ffffff", stroke=INK, sw=2))
    out.append(circle(x + w * 0.76, y + h + r - 2, r, fill="#ffffff", stroke=INK, sw=2))
    if label:
        out.append(text(x + w / 2, y + h / 2 + 5, label, size=lsize, bold=True, color=INK))
    return "".join(out)


def person(cx, base_y, col=INK, h=64):
    """Схематична фігурка людини, ноги на base_y."""
    hh = h * 0.28
    head_r = h * 0.16
    hy = base_y - h
    out = [circle(cx, hy + head_r, head_r, fill="#ffffff", stroke=col, sw=2)]
    ty = hy + 2 * head_r
    out.append(line(cx, ty, cx, base_y - h * 0.34, color=col, sw=2.4))        # тулуб
    out.append(line(cx, ty + 4, cx - h * 0.2, ty + h * 0.22, color=col, sw=2.4))  # руки
    out.append(line(cx, ty + 4, cx + h * 0.2, ty + h * 0.22, color=col, sw=2.4))
    out.append(line(cx, base_y - h * 0.34, cx - h * 0.16, base_y, color=col, sw=2.4))  # ноги
    out.append(line(cx, base_y - h * 0.34, cx + h * 0.16, base_y, color=col, sw=2.4))
    return "".join(out)


# ── Фігура 1: однаковий поштовх — різний відгук ───────────────────────────────
def fig_same_push():
    W, H = 940, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Однаковий поштовх — різний відгук: у цьому й є маса", size=17, bold=True))

    start = 150
    f.append(line(start, 78, start, 400, color=MUTED, sw=1.4, dash="5 6"))
    f.append(text(start, 70, "старт", size=12, color=MUTED))

    # спільний поштовх (однакова стрілка для обох)
    Flen = 78

    # ── верхня доріжка: легкий візок ──
    gy1 = 175
    f.append(hatch(70, gy1 + 30, W - 40, gy1 + 30, step=20, color=NEG))
    f.append(arrow(start - Flen - 8, gy1, start - 8, gy1, color=POS, sw=3.4))
    f.append(text(start - Flen - 16, gy1 - 8, "F", size=16, bold=True, color=POS, anchor="end"))
    f.append(cart(start + 4, gy1 - 18, 56, 36, fill="#eef2fb", label="2 кг"))
    # привид-візок далеко праворуч + довга стрілка швидкості
    gx1 = 720
    f.append(cart(gx1, gy1 - 18, 56, 36, fill="#f4f6f8", label="2 кг"))
    f.append(arrow(gx1 + 62, gy1, gx1 + 168, gy1, color=FIELD, sw=3.2))
    f.append(text(gx1 + 174, gy1 - 6, "v — велика", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(line(start + 60, gy1 + 44, gx1 - 4, gy1 + 44, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text((start + 60 + gx1) / 2, gy1 + 60, "далеко проїхав — велике прискорення", size=12, color=INK))

    # ── нижня доріжка: важкий візок ──
    gy2 = 330
    f.append(hatch(70, gy2 + 40, W - 40, gy2 + 40, step=20, color=NEG))
    f.append(arrow(start - Flen - 8, gy2, start - 8, gy2, color=POS, sw=3.4))
    f.append(text(start - Flen - 16, gy2 - 8, "F", size=16, bold=True, color=POS, anchor="end"))
    f.append(text(start - Flen - 16, gy2 + 12, "(та сама)", size=11, color=MUTED, anchor="end"))
    f.append(cart(start + 4, gy2 - 28, 80, 56, fill="#e7ecf7", label="20 кг"))
    # привид ледь зрушив + коротка стрілка
    gx2 = start + 150
    f.append(cart(gx2, gy2 - 28, 80, 56, fill="#f4f6f8", label="20 кг"))
    f.append(arrow(gx2 + 86, gy2, gx2 + 120, gy2, color=FIELD, sw=3.0))
    f.append(text(gx2 + 128, gy2 - 6, "v — мала", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(line(start + 84, gy2 + 52, gx2 - 4, gy2 + 52, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(gx2 + 220, gy2 + 68, "ледь зрушив — мале прискорення", size=12, color=INK))

    b, w, h = textbox(W / 2, H - 26,
                      "a = F / m   —   удесятеро більша маса дає вдесятеро менше прискорення від того самого поштовху",
                      size=13.5, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "same-push.svg"), W, H, *f)


# ── Фігура 2: маса стала, вага змінюється з місцем ────────────────────────────
def fig_mass_not_weight():
    W, H = 960, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Маса — та сама всюди; вага змінюється з місцем", size=17, bold=True))

    base = 430
    f.append(line(60, base, W - 60, base, color=INK, sw=1.8))
    cols = [(200, "Земля", 9.8, 686, "#eef6ef", FIELD),
            (490, "Місяць", 1.62, 114, "#f6f3ea", "#a9946b"),
            (790, "Орбіта (МКС)", 0.0, 0, "#fdf0ee", POS)]
    mass_h = 120                       # висота бруска маси — ОДНАКОВА скрізь
    wscale = 150.0 / 686.0             # px на ньютон ваги (Земля → 150 px)
    bw = 40
    for cx, name, g, wN, tint, col in cols:
        f.append(text(cx, 74, name, size=15, bold=True, color=col))
        f.append(person(cx, base - 2, col=INK, h=60))
        # два бруски: маса (ліворуч, синій) і вага (праворуч, за кольором сцени)
        mx = cx - bw - 12
        wx = cx + 12
        # маса — стала
        f.append(rect(mx, base - mass_h, bw, mass_h, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
        f.append(text(mx + bw / 2, base - mass_h - 10, "70 кг", size=12, bold=True, color=NEG))
        # вага — за g
        wh = max(4, wN * wscale)
        f.append(rect(wx, base - wh, bw, wh, fill=tint, stroke=col, sw=2, rx=4))
        wlbl = ("%d Н" % wN) if wN else "≈ 0 Н"
        f.append(text(wx + bw / 2, base - wh - 10, wlbl, size=12, bold=True, color=col))
        # g під сценою
        gtxt = ("g = %.2f м/с²" % g) if g else "g_еф ≈ 0"
        f.append(text(cx, base + 24, gtxt, size=12, color=INK))
        f.append(text(mx + bw / 2, base + 44, "маса", size=11, color=NEG))
        f.append(text(wx + bw / 2, base + 44, "вага", size=11, color=col))

    b, w, h = textbox(W / 2, H - 26,
                      "маса — стала властивість тіла (кг); вага — сила тяжіння на нього, P = m·g (Н), тож слабне там, де слабший g",
                      size=13, pad=11, fill="#f4f6f8", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "mass-not-weight.svg"), W, H, *f)


# ── Фігура 3: дві маси — одне число ───────────────────────────────────────────
def fig_two_masses():
    W, H = 960, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Дві маси — одне число", size=17, bold=True))

    # ── ліва панель: інерційна маса ──
    lx, ly = 235, 150
    f.append(fitbox(lx - 170, 66, 340, 34, "інерційна маса  mᵢ — опір розгону",
                    size=14, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True, color=NEG))
    f.append(hatch(lx - 150, ly + 60, lx + 150, ly + 60, step=18, color=NEG))
    f.append(cart(lx - 34, ly - 2, 68, 46, fill="#eef2fb", label="mᵢ"))
    f.append(arrow(lx - 150, ly + 20, lx - 40, ly + 20, color=POS, sw=3.2))
    f.append(text(lx - 158, ly + 14, "F", size=15, bold=True, color=POS, anchor="end"))
    f.append(arrow(lx + 40, ly + 20, lx + 132, ly + 20, color=FIELD, sw=3.0))
    f.append(text(lx + 138, ly + 15, "a", size=15, bold=True, color=FIELD, anchor="start"))
    b, w, h = textbox(lx, ly + 116, "F = mᵢ · a", size=16, pad=10,
                      fill="#eaf0fd", stroke=NEG, sw=1.4, bold=True)
    f.append(b)

    # ── права панель: гравітаційна маса ──
    rx, ry = 725, 150
    f.append(fitbox(rx - 170, 66, 340, 34, "гравітаційна маса  m_g — відгук на тяжіння",
                    size=14, fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    f.append(circle(rx, ry + 6, 22, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(rx, ry + 11, "m_g", size=13, bold=True, color=INK))
    f.append(arrow(rx, ry + 30, rx, ry + 118, color=INK, sw=3.4))
    f.append(text(rx + 14, ry + 80, "P", size=15, bold=True, color=INK, anchor="start"))
    # маленька планета
    f.append(circle(rx, ry + 190, 40, fill="#eaf7ee", stroke=FIELD, sw=2))
    f.append(text(rx, ry + 195, "M", size=14, bold=True, color=FIELD))
    b, w, h = textbox(rx - 120, ry + 116, "P = G·m_g·M / r²", size=15, pad=10,
                      fill="#eaf7ee", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)

    # ── знак рівності по центру ──
    cx = (lx + rx) / 2
    f.append(text(cx, ly + 24, "=", size=52, bold=True, color=INK))
    f.append(mtext(cx, ly + 92, ["з досліду —", "рівні до ~10⁻¹⁵"], size=12.5, color=MUTED, lh=1.3))

    # ── наслідок: усі падають однаково ──
    yb = 410
    f.append(line(120, yb, W - 120, yb, color=MUTED, sw=1.4, dash="5 6"))
    f.append(text(150, yb - 8, "з однієї висоти:", size=12.5, color=MUTED, anchor="start"))
    for px, r, lbl in [(360, 16, "важке"), (600, 9, "легке")]:
        f.append(circle(px, yb + 42, r, fill="#eef2fb", stroke=INK, sw=2))
        f.append(arrow(px, yb + 42 + r + 4, px, yb + 112, color=FIELD, sw=3.0))
        f.append(text(px, yb - 16, lbl, size=12, color=INK))
    f.append(line(300, yb + 124, 660, yb + 124, color=INK, sw=2.2))
    f.append(hatch(300, yb + 124, 660, yb + 124, step=20, color=MUTED, dx=9, dy=9))
    b, w, h = textbox(W / 2, H - 30,
                      "бо mᵢ = m_g, у падінні маса скорочується:  mᵢ·a = m_g·g  ⇒  a = g  — усі тіла падають однаково",
                      size=13, pad=11, fill="#eaf7ee", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "two-masses.svg"), W, H, *f)


# ── Фігура 4: звідки береться маса звичайної речовини ─────────────────────────
def fig_mass_origin():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Звідки береться маса звичайної речовини", size=17, bold=True))

    # ── ліворуч: протон з кварками й глюонними нитками ──
    px, py = 210, 205
    f.append(circle(px, py, 95, fill="#f7f9fc", stroke=MUTED, sw=1.6))
    f.append(text(px, py - 112, "протон  ≈ 938 МеВ/с²", size=14, bold=True, color=INK))
    q = [(px - 52, py + 20, "u"), (px + 52, py + 20, "u"), (px, py - 50, "d")]
    # глюонні нитки між кварками
    f.append(coil_h(q[0][0], q[1][0], py + 20, 6, 8))
    f.append(coil_h(q[0][0], q[2][0], (q[0][1] + q[2][1]) / 2, 5, 7))
    f.append(coil_h(q[1][0], q[2][0], (q[1][1] + q[2][1]) / 2, 5, 7))
    for qx, qy, ql in q:
        f.append(circle(qx, qy, 17, fill="#eef2fb", stroke=INK, sw=2))
        f.append(text(qx, qy + 5, ql, size=14, bold=True, color=INK))
    f.append(text(px, py + 118, "3 кварки + глюонні поля", size=12, color=MUTED))

    # ── праворуч: із чого складається ця маса (смуга-стек) ──
    bx, by, bw2, bh2 = 440, 150, 440, 60
    f.append(text(bx, by - 16, "із чого ця маса:", size=13.5, bold=True, color=INK, anchor="start"))
    seg1 = bw2 * 0.02                    # ~1% — Гіггс (візуально трохи побільшено)
    f.append(rect(bx, by, seg1, bh2, fill="#fdecea", stroke=POS, sw=2, rx=0))
    f.append(rect(bx + seg1, by, bw2 - seg1, bh2, fill="#eaf7ee", stroke=FIELD, sw=2, rx=0))
    f.append(text(bx + seg1 + (bw2 - seg1) / 2, by + bh2 / 2 + 5,
                  "≈ 99 %", size=17, bold=True, color=FIELD))
    # виноска на 1%-сегмент
    f.append(line(bx + seg1 / 2, by + bh2 + 4, bx + 40, by + bh2 + 40, color=POS, sw=1.2))
    f.append(fitbox(bx + 40, by + bh2 + 40, 400, 46,
                    "≈ 1 % — маса кварків та електронів від поля Гіггса (u+d < 10 МеВ)",
                    size=12.5, fill="#fdf0ee", stroke=POS, sw=1.3, color=POS))
    f.append(fitbox(bx, by + bh2 + 100, 440, 46,
                    "≈ 99 % — енергія глюонних полів і руху кварків усередині",
                    size=12.5, fill="#eaf7ee", stroke=FIELD, sw=1.3, color=FIELD))

    b, w, h = textbox(W / 2, H - 40,
                      ["майже вся маса тіла — це зв'язана всередині ЕНЕРГІЯ, а не «кількість речовини»:",
                       "E = m·c²   ⇒   енергія полів і руху важить. Гіггсів механізм дає лише крихту."],
                      size=13, pad=12, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "mass-origin.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до історичної вставки «hist-mass-concept»
# ══════════════════════════════════════════════════════════════════════════════

def carrow(x1, y1, x2, y2, cx, cy, color=LINE, sw=2.0):
    """Крива стрілка (квадратична безьє) з наконечником."""
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x1, y1, cx, cy, x2, y2, color, sw))


def flask(cx, top, col=INK, sealed=True):
    """Схематична колба/реторта з металом і полум'ям. top — верх шийки."""
    out = []
    body_cy = top + 78
    out.append(circle(cx, body_cy, 36, fill="#f7f9fc", stroke=col, sw=2))     # бульба
    out.append(rect(cx - 9, top, 18, 46, fill="#f7f9fc", stroke=col, sw=2, rx=3))  # шийка
    out.append(rect(cx - 16, body_cy + 20, 32, 11, fill="#e7ecf7", stroke=INK, sw=1.6, rx=2))  # метал
    out.append(text(cx, body_cy + 29, "метал", size=9, color=MUTED))
    if sealed:                                                                # запаяно
        out.append(line(cx - 9, top, cx + 9, top, color=col, sw=3.4))
    # полум'я під бульбою
    fy = body_cy + 40
    out.append(polyline([(cx - 12, fy), (cx - 4, fy - 14), (cx, fy - 4),
                         (cx + 4, fy - 16), (cx + 12, fy)], color=POS, sw=2.2))
    return "".join(out)


# ── Фігура: хроніка народження поняття маси ───────────────────────────────────
def fig_hist_timeline():
    W, H = 1300, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 36, "Як народжувалося поняття маси: дійові особи й дати",
                  size=18, bold=True))

    axis_y = 300
    f.append(line(80, axis_y, W - 50, axis_y, color=INK, sw=2))
    f.append(arrow(W - 60, axis_y, W - 42, axis_y, color=INK, sw=2))
    f.append(text(W - 46, axis_y + 22, "час", size=12, italic=True, color=MUTED, anchor="end"))

    nodes = [
        (160, MUTED,      "#f4f6f8", ["≈1618 · Кеплер", "уводить «інерцію» —",
                                      "але як хист тіла", "до спокою"]),
        (356, NEG,        "#eaf0fd", ["1687 · Ньютон", "«кількість матерії»",
                                      "= густина × об'єм;", "а міряє — вагою"]),
        (552, "#a9946b",  "#f6f3ea", ["1748 · Ломоносов", "лист Ойлерові:",
                                      "загальна теза", "збереження"]),
        (748, FIELD,      "#eaf7ee", ["1770-ті–89 · Лавуазьє", "запаяна посудина →",
                                      "дослідний закон", "збереження маси"]),
        (944, POS,        "#fdecea", ["1868 · Мах", "маса = відношення",
                                      "взаємних прискорень —", "облік, не «річ»"]),
        (1140, INK,       "#eef2fb", ["1905 · Айнштайн", "маса спокою,",
                                      "E = m·c²; поняття", "розколюється"]),
    ]
    bw, bh = 190, 118
    for i, (x, col, tint, lines) in enumerate(nodes):
        above = (i % 2 == 0)
        if above:
            by = axis_y - 40 - bh
            f.append(line(x, axis_y - 8, x, by + bh, color=col, sw=1.6))
        else:
            by = axis_y + 40
            f.append(line(x, axis_y + 8, x, by, color=col, sw=1.6))
        f.append(fitbox(x - bw / 2, by, bw, bh, lines, size=13, pad=9,
                        fill=tint, stroke=col, sw=1.8, color=INK))
        f.append(circle(x, axis_y, 8, fill=tint, stroke=col, sw=2.4))

    b, w, h = textbox(W / 2, H - 26,
                      "одне слово поволі розчепили на три: скільки речовини · як важко · як воно опирається розгону",
                      size=13.5, pad=11, fill="#f4f6f8", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── Фігура: Ньютонове коло і Махів вихід ──────────────────────────────────────
def fig_hist_circularity():
    W, H = 1160, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 36, "Означення, що кусає себе за хвіст — і як Мах його розтяв",
                  size=18, bold=True))

    # ── ліворуч: Ньютонове коло (двоцикл маса ↔ густина) ──
    f.append(fitbox(60, 74, 430, 32, "Ньютон (1687): коло «маса ↔ густина»",
                    size=14, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True, color=NEG))
    my = 205
    bm, wm, hm = textbox(175, my, "маса  m", size=16, pad=12,
                         fill="#eef2fb", stroke=INK, sw=2, bold=True)
    br, wr, hr = textbox(405, my, "густина  ρ", size=16, pad=12,
                         fill="#eef2fb", stroke=INK, sw=2, bold=True)
    # верхня дуга: ρ → m (щоб знати m, береш ρ)
    f.append(carrow(405, my - 23, 175, my - 23, 290, 150, color=NEG, sw=2.4))
    f.append(text(290, 138, "m = ρ · V", size=14, bold=True, color=NEG))
    # нижня дуга: m → ρ (щоб знати ρ, береш m)
    f.append(carrow(175, my + 23, 405, my + 23, 290, 300, color=POS, sw=2.4))
    f.append(text(290, 322, "ρ = m / V", size=14, bold=True, color=POS))
    f.append(bm)
    f.append(br)
    f.append(fitbox(70, 366, 440, 56,
                    ["масу означено через ρ, а ρ — через масу:",
                     "коло замкнене, «речовини» так і не видно"],
                    size=13, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    # ── стрілка-міст ──
    f.append(arrow(516, my, 620, my, color=INK, sw=3))
    f.append(text(568, my - 16, "Мах розтинає", size=13, bold=True, color=INK))

    # ── праворуч: Махів операційний вихід ──
    f.append(fitbox(660, 74, 440, 32, "Мах (1868): міряй взаємні прискорення",
                    size=14, fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    ay = 210
    f.append(text(874, ay - 42, "лишаєш два тіла у взаємодії — і тільки", size=12, color=MUTED))
    f.append(coil_h(816, 939, ay, 6, 9))
    f.append(circle(788, ay, 28, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(788, ay + 5, "A", size=16, bold=True))
    f.append(circle(960, ay, 21, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(960, ay + 5, "B", size=15, bold=True))
    f.append(arrow(756, ay, 680, ay, color=FIELD, sw=3))
    f.append(text(674, ay + 5, "a₁", size=15, bold=True, color=FIELD, anchor="end"))
    f.append(arrow(984, ay, 1068, ay, color=FIELD, sw=3))
    f.append(text(1076, ay + 5, "a₂", size=15, bold=True, color=FIELD, anchor="start"))
    b2, w2, h2 = textbox(880, 316, "m₁ · a₁ = m₂ · a₂   ⇒   m₁ / m₂ = a₂ / a₁",
                         size=15, pad=11, fill="#eaf7ee", stroke=FIELD, sw=1.5, bold=True)
    f.append(b2)
    f.append(fitbox(700, 372, 360, 44,
                    ["маса — число з досліду,", "а не прихована «речовина»"],
                    size=13, fill="#eaf7ee", stroke=FIELD, sw=1.3, color=FIELD))
    return render(os.path.join(IMG, "hist-circularity.svg"), W, H, *f)


# ── Фігура: Бойл проти Лавуазьє — що саме зважували ────────────────────────────
def fig_hist_sealed():
    W, H = 1080, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 36, "Збереження маси: уся різниця — ЩО поклали на терези",
                  size=18, bold=True))

    f.append(line(W / 2, 70, W / 2, H - 120, color=MUTED, sw=1.2, dash="6 7"))

    # ── ЛІВОРУЧ: Бойл ──
    lx = 285
    f.append(fitbox(lx - 200, 66, 400, 34,
                    "Бойл (1670-ті): важить ПІСЛЯ відкриття колби",
                    size=14, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))
    f.append(flask(lx, 130, col=INK, sealed=False))
    f.append(carrow(lx + 78, 118, lx + 14, 132, lx + 74, 96, color=POS, sw=2.4))
    f.append(mtext(lx + 86, 108, ["колбу", "відкрито —", "повітря", "влітає"],
                   size=12, color=POS, anchor="start", lh=1.3))
    f.append(fitbox(lx - 110, 300, 220, 40, "терези: стало важче",
                    size=13.5, fill="#fdecea", stroke=POS, sw=1.5, bold=True, color=POS))
    f.append(fitbox(lx - 175, 360, 350, 66,
                    ["висновок Бойла: крізь скло влетіли", "«вогняні частинки»  (хибно)"],
                    size=13, fill="#fdf0ee", stroke=POS, sw=1.4, color=POS))

    # ── ПРАВОРУЧ: Лавуазьє ──
    rx_ = 795
    f.append(fitbox(rx_ - 205, 66, 410, 34,
                    "Лавуазьє (1770-ті): важить ЗАПАЯНУ посудину",
                    size=14, fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    f.append(flask(rx_, 130, col=INK, sealed=True))
    f.append(text(rx_ + 60, 118, "запаяно", size=12, color=FIELD, anchor="start", italic=True))
    f.append(fitbox(rx_ - 120, 300, 240, 40, "терези: маса та сама",
                    size=13.5, fill="#eaf7ee", stroke=FIELD, sw=1.5, bold=True, color=FIELD))
    f.append(fitbox(rx_ - 185, 360, 370, 66,
                    ["висновок: повітря сполучилося з металом;", "повна маса стала — приросту нема"],
                    size=13, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=FIELD))

    b, w, h = textbox(W / 2, H - 54,
                      ["Бойл важив уже після того, як у колбу вдерлось повітря; Лавуазьє важив усю запаяну систему.",
                       "Маса зберігається; приріст при відкритті = маса поглинутого повітря, а не «вогняних частинок»."],
                      size=13, pad=12, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "hist-sealed-vessel.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до математичної вставки «math-inertial-mass»
# ══════════════════════════════════════════════════════════════════════════════

def _cart_top(ice_y, h):
    """Y-верх кузова так, щоб колеса стали на лінію льоду ice_y."""
    return ice_y - 16 - h


# ── Фігура: зважити тіло відкотом (означення Маха в дії) ──────────────────────
def fig_mach_recoil():
    W, H = 960, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34,
                  "Зважити тіло відкотом: легший еталон відлітає далеко, важче — ледь",
                  size=16, bold=True))

    ice = 300
    f.append(hatch(60, ice, W - 60, ice, step=20, color=NEG))

    # старт — де була стиснута пружина
    sx = 500
    f.append(line(sx, 100, sx, ice, color=MUTED, sw=1.4, dash="5 6"))
    f.append(text(sx, 92, "старт — тут була стиснута пружина", size=12, color=MUTED))
    f.append(coil_h(sx - 26, sx + 26, ice - 6, 4, 5))

    # ── еталон (легкий): далеко ліворуч, довга стрілка швидкості ──
    ex, ew, eh = 210, 58, 38
    ey = _cart_top(ice, eh)
    f.append(cart(ex - ew / 2, ey, ew, eh, fill="#eaf0fd", label="1 кг"))
    f.append(text(ex, ey - 12, "еталон", size=12.5, bold=True, color=NEG))
    ecy = ey + eh / 2
    f.append(arrow(ex - ew / 2 - 6, ecy, ex - ew / 2 - 150, ecy, color=FIELD, sw=3.2))
    f.append(text(ex - ew / 2 - 78, ecy - 12, "v₁ = 1.00 м/с", size=13, bold=True, color=FIELD))
    f.append(line(ex + ew / 2, ice + 18, sx, ice + 18, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text((ex + ew / 2 + sx) / 2, ice + 34, "відкотився далеко", size=12, color=INK))

    # ── невідоме тіло (важче): трохи праворуч, коротка стрілка ──
    ux, uw, uh = 630, 88, 58
    uy = _cart_top(ice, uh)
    f.append(cart(ux - uw / 2, uy, uw, uh, fill="#e7ecf7", label="m₂ = ?"))
    ucy = uy + uh / 2
    f.append(arrow(ux + uw / 2 + 6, ucy, ux + uw / 2 + 78, ucy, color=FIELD, sw=3.0))
    f.append(text(ux + uw / 2 + 42, ucy - 12, "v₂ = 0.40 м/с", size=13, bold=True, color=FIELD))
    f.append(line(sx, ice + 18, ux - uw / 2, ice + 18, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text((sx + ux - uw / 2) / 2, ice + 34, "трохи", size=12, color=INK))

    b, w, h = textbox(W / 2, H - 30,
                      "почали з нерухомості → повна кількість руху = 0:   "
                      "1·(−1.00) + m₂·(0.40) = 0   ⇒   m₂ = 2.5 кг",
                      size=13.5, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "mach-recoil.svg"), W, H, *f)


# ── Фігура: транзитивність — три виміри сходяться в одне число ────────────────
def fig_mach_transitivity():
    W, H = 960, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34,
                  "Транзитивність: три досліди відкоту сходяться в одне число маси",
                  size=17, bold=True))

    S = (480, 150)
    A = (250, 425)
    B = (710, 425)
    r = 33

    # ребра (кожне — окремий дослід відкоту); малюємо ПІД вузлами
    f.append(line(S[0], S[1], A[0], A[1], color=NEG, sw=2.4))
    f.append(line(S[0], S[1], B[0], B[1], color=FIELD, sw=2.4))
    f.append(line(A[0], A[1], B[0], B[1], color=POS, sw=2.4))

    # теги-виміри назовні від ребер
    b, w, h = textbox(305, 250, ["дослід S↔A", "m_A = 2.5 кг"],
                      size=13, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.5, color=NEG, bold=True)
    f.append(b)
    b, w, h = textbox(655, 250, ["дослід S↔B", "m_B = 4.0 кг"],
                      size=13, pad=9, fill="#eaf7ee", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    f.append(b)
    b, w, h = textbox(480, 478, ["прямий дослід A↔B", "m_A / m_B = 0.625"],
                      size=13, pad=9, fill="#fdecea", stroke=POS, sw=1.5, color=POS, bold=True)
    f.append(b)

    # вузли поверх ребер
    for (cx, cy), lab in [(S, "S"), (A, "A"), (B, "B")]:
        f.append(circle(cx, cy, r, fill="#eef2fb", stroke=INK, sw=2.4))
        f.append(text(cx, cy + 6, lab, size=18, bold=True, color=INK))
    f.append(text(S[0], S[1] - r - 12, "еталон  1 кг", size=12.5, bold=True, color=INK))
    f.append(text(A[0], A[1] + r + 24, "2.5 кг", size=12.5, bold=True, color=INK))
    f.append(text(B[0], B[1] + r + 24, "4.0 кг", size=12.5, bold=True, color=INK))

    # перевірка в осерді трикутника
    b, w, h = textbox(480, 345, ["через еталон:", "2.5 ⁄ 4.0 = 0.625  ✓", "коло замикається"],
                      size=13, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.6, color=INK)
    f.append(b)

    b, w, h = textbox(W / 2, H - 28,
                      "збіг не був зобов'язаний статися — а стається; тому масу кожного тіла "
                      "ловить одне-єдине число",
                      size=13, pad=11, fill="#f4f6f8", stroke=MUTED, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "mach-transitivity.svg"), W, H, *f)


# ── Фігура: інерційні терези — та сама пружина, різні періоди ─────────────────
def fig_inertial_balance():
    W, H = 1000, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34,
                  "Інерційні терези: та сама пружина, більша маса — довший період",
                  size=17, bold=True))

    f.append(line(497, 84, 497, 430, color=MUTED, sw=1.2, dash="6 7"))

    # ── ЛІВОРУЧ: два пружинні маятники з однаковою k ──
    f.append(hatch(90, 92, 430, 92, step=20, color=MUTED, dx=8, dy=-9))

    # легке тіло
    lx = 175
    f.append(coil_v(lx, 92, 180, 6, 10, color=NEG))
    f.append(rect(lx - 24, 180, 48, 40, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    f.append(text(lx, 205, "m", size=15, bold=True, color=NEG))
    f.append(text(lx, 240, "легке", size=12, color=NEG))
    f.append(arrow(lx + 40, 200, lx + 40, 172, color=FIELD, sw=2.2))
    f.append(arrow(lx + 40, 200, lx + 40, 228, color=FIELD, sw=2.2))

    # важке тіло — та сама пружина
    hx = 345
    f.append(coil_v(hx, 92, 180, 6, 10, color=POS))
    f.append(rect(hx - 33, 180, 66, 58, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(hx, 214, "M", size=16, bold=True, color=POS))
    f.append(text(hx, 258, "важке", size=12, color=POS))
    f.append(arrow(hx + 49, 209, hx + 49, 176, color=FIELD, sw=2.2))
    f.append(arrow(hx + 49, 209, hx + 49, 242, color=FIELD, sw=2.2))

    f.append(fitbox(107, 292, 300, 30, "дві однакові пружини — та сама k",
                    size=13, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    # ── ПРАВОРУЧ: записи коливань у часі (однакова амплітуда, різний період) ──
    tx0, tx1 = 545, 935

    # легке: короткий період
    yc1 = 165
    f.append(text(740, 108, "легке: швидкі коливання — короткий T₁", size=13, bold=True, color=NEG))
    f.append(line(tx0, yc1, tx1, yc1, color=MUTED, sw=1.1, dash="4 5"))
    f.append(sine(tx0, tx1, yc1, 40, 85, color=NEG))
    f.append(text(535, yc1 + 4, "x", size=12, italic=True, color=MUTED, anchor="end"))
    f.append(arrow(tx0, 227, tx0 + 85, 227, color=INK, sw=1.8))
    f.append(arrow(tx0 + 85, 227, tx0, 227, color=INK, sw=1.8))
    f.append(text(tx0 + 42, 244, "T₁", size=13, bold=True, color=INK))

    # важке: довгий період
    yc2 = 335
    f.append(text(740, 278, "важке: повільні коливання — довгий T₂", size=13, bold=True, color=POS))
    f.append(line(tx0, yc2, tx1, yc2, color=MUTED, sw=1.1, dash="4 5"))
    f.append(sine(tx0, tx1, yc2, 40, 170, color=POS))
    f.append(text(535, yc2 + 4, "x", size=12, italic=True, color=MUTED, anchor="end"))
    f.append(arrow(tx0, 397, tx0 + 170, 397, color=INK, sw=1.8))
    f.append(arrow(tx0 + 170, 397, tx0, 397, color=INK, sw=1.8))
    f.append(text(tx0 + 85, 414, "T₂  (>  T₁)", size=13, bold=True, color=INK))

    b, w, h = textbox(W / 2, H - 34,
                      ["T = 2π·√(m ⁄ k):  та сама пружина (k), більша маса — довший період.",
                       "зміряв період T → маса  m = k·(T ⁄ 2π)².  Тяжіння не входить — працює й у невагомості."],
                      size=13, pad=12, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "inertial-balance.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_same_push(), fig_mass_not_weight(), fig_two_masses(), fig_mass_origin(),
          fig_hist_timeline(), fig_hist_circularity(), fig_hist_sealed(),
          fig_mach_recoil(), fig_mach_transitivity(), fig_inertial_balance()]
    print("written:")
    for p in ps:
        print("  ", p)
