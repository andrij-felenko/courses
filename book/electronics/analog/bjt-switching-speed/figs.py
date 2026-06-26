# -*- coding: utf-8 -*-
"""Фігури до теми «BJT: швидкість комутації та заряд бази».
Чотири фігури:
  waveform.svg  — вхідний імпульс ↔ Ic з чотирма часами (td, tr, ts, tf)
  charge.svg    — профіль заряду неосновних носіїв у базі: активний ↔ глибоке насичення
  speedup.svg   — пришвидшувальний конденсатор поверх Rб і його струмовий сплеск
  cures.svg     — три способи проти насичення: примусове β · Бейкерів затиск · Шотткі-транзистор
Запуск:  python figs.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#b5732e"


# ── локальні примітиви ──────────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 33, label, size=11, color=INK, bold=True))
    return "".join(out)


def res_h(cx, cy, w=40, label=None, lab_above=True):
    h = 15
    xl, xr = cx - w / 2, cx + w / 2
    out = [rect(xl, cy - h / 2, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        if lab_above:
            out.append(text(cx, cy - h / 2 - 6, label, size=12, color=INK))
        else:
            out.append(text(cx, cy + h / 2 + 14, label, size=12, color=INK))
    return "".join(out), xl, xr


def cap_h(cx, cy, w=26, label=None):
    """Горизонтальний конденсатор (дві пластини)."""
    g = 7
    xl, xr = cx - g / 2, cx + g / 2
    out = [line(xl, cy - 13, xl, cy + 13, color=INK, sw=2.4),
           line(xr, cy - 13, xr, cy + 13, color=INK, sw=2.4),
           line(cx - w / 2, cy, xl, cy, color=INK, sw=1.6),
           line(xr, cy, cx + w / 2, cy, color=INK, sw=1.6)]
    if label:
        out.append(text(cx, cy - 20, label, size=12, color=INK))
    return "".join(out), cx - w / 2, cx + w / 2


def diode_h(cx, cy, w=30, point_right=True, color=INK, label=None):
    """Горизонтальний діод (трикутник + смужка-катод)."""
    xl, xr = cx - w / 2, cx + w / 2
    out = [line(xl, cy, cx - 7, cy, color=color, sw=1.8),
           line(cx + 7, cy, xr, cy, color=color, sw=1.8)]
    if point_right:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                   % (cx - 7, cy - 8, cx + 7, cy, cx - 7, cy + 8, color))
        out.append(line(cx + 7, cy - 8, cx + 7, cy + 8, color=color, sw=2.2))
    else:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                   % (cx + 7, cy - 8, cx - 7, cy, cx + 7, cy + 8, color))
        out.append(line(cx - 7, cy - 8, cx - 7, cy + 8, color=color, sw=2.2))
    if label:
        out.append(text(cx, cy - 16, label, size=11, color=color, bold=True))
    return "".join(out)


def schottky_h(cx, cy, w=34, point_right=True, color=INK, label=None):
    """Діод Шотткі: трикутник + катод у вигляді літери S (гачки)."""
    out = [diode_h(cx, cy, w, point_right, color)]
    bx = cx + 7 if point_right else cx - 7
    # S-подібні гачки замість прямої смужки
    out.append(line(bx - 5, cy - 8, bx, cy - 8, color=color, sw=2.2))
    out.append(line(bx, cy - 8, bx, cy + 8, color=color, sw=2.2))
    out.append(line(bx, cy + 8, bx + 5, cy + 8, color=color, sw=2.2))
    if label:
        out.append(text(cx, cy - 16, label, size=11, color=color, bold=True))
    return "".join(out)


class Tr:
    __slots__ = ("svg", "xb", "xc", "yc", "ye", "yb")
    def __init__(self, svg, xb, xc, yc, ye, yb):
        self.svg, self.xb, self.xc, self.yc, self.ye, self.yb = svg, xb, xc, yc, ye, yb


def npn(cx, cy, label=None, scale=1.0):
    """Символ NPN. Повертає Tr із координатами виводів."""
    out = []
    bt, bb = cy - 26 * scale, cy + 26 * scale
    out.append(line(cx, bt, cx, bb, color=INK, sw=3))
    out.append(line(cx - 28, cy, cx, cy, color=INK, sw=2))
    cx2 = cx + 28
    out.append(line(cx, bt + 8, cx2, bt - 9, color=INK, sw=2))
    yC = bt - 30
    out.append(line(cx2, bt - 9, cx2, yC, color=INK, sw=2))
    out.append(line(cx, bb - 8, cx2, bb + 9, color=INK, sw=2))
    yE = bb + 30
    out.append(line(cx2, bb + 9, cx2, yE, color=INK, sw=2))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
               % (cx + 16, bb + 2, cx2, bb + 10, cx + 14, bb + 11, INK))
    if label:
        out.append(text(cx2 + 8, cy + 4, label, size=12, color=INK, bold=True, anchor="start"))
    return Tr("".join(out), cx - 28, cx2, yC, yE, cy)


# ── Фігура 1: waveform.svg — вхід ↔ Ic з чотирма часами ─────────────────────
def fig_waveform():
    W, H = 880, 470
    f = [text(W / 2, 30, "Чому комутація не миттєва: чотири затримки в одному перемиканні",
              size=16, bold=True)]

    L, R = 90, 760           # межі осі часу
    # дві смуги: вхід (Ib) угорі, вихід (Ic) унизу
    yIb0, yIbH = 130, 80     # рівень 0 і «високо» для вхідного імпульсу
    yIc0, yIcH = 360, 240    # рівень 0 і «насичення» для Ic

    # ── маркери ключових моментів часу по осі ──
    t_on   = 200             # фронт увімкнення вхідного імпульсу
    t_d_e  = 270             # кінець затримки td
    t_r_e  = 360             # кінець наростання tr
    t_off  = 520             # фронт вимкнення вхідного імпульсу
    t_s_e  = 620             # кінець часу розсмоктування ts
    t_f_e  = 700             # кінець спаду tf

    # вертикальні пунктири крізь обидві смуги
    for x in (t_on, t_d_e, t_r_e, t_off, t_s_e, t_f_e):
        f.append(line(x, yIbH - 18, x, yIc0 + 14, color="#dcdcdc", sw=1, dash="3,3"))

    # ── вхідний імпульс Ib (зелений) ──
    f.append(text(L - 14, yIbH - 22, "вхід (струм бази Ib)", size=12, color=FIELD,
                  bold=True, anchor="start"))
    f.append(line(L, yIb0, t_on, yIb0, color=FIELD, sw=2.4))
    f.append(line(t_on, yIb0, t_on, yIbH, color=FIELD, sw=2.4))
    f.append(line(t_on, yIbH, t_off, yIbH, color=FIELD, sw=2.4))
    f.append(line(t_off, yIbH, t_off, yIb0, color=FIELD, sw=2.4))
    f.append(line(t_off, yIb0, R, yIb0, color=FIELD, sw=2.4))
    f.append(line(L, yIb0, L, yIb0 + 6, color=INK, sw=1.4))

    # ── вихід Ic (чорний) з реальними фронтами ──
    f.append(text(L - 14, yIcH - 14, "вихід (струм колектора Ic)", size=12, color=INK,
                  bold=True, anchor="start"))
    f.append(line(L, yIc0, t_d_e, yIc0, color=INK, sw=2.6))          # затримка: Ic ще 0
    f.append(line(t_d_e, yIc0, t_r_e, yIcH, color=INK, sw=2.6))      # наростання
    f.append(line(t_r_e, yIcH, t_s_e, yIcH, color=INK, sw=2.6))      # насичення + плато розсмоктування
    f.append(line(t_s_e, yIcH, t_f_e, yIc0, color=INK, sw=2.6))      # спад
    f.append(line(t_f_e, yIc0, R, yIc0, color=INK, sw=2.6))
    f.append(text(R + 6, yIcH + 4, "Ic(нас)", size=11, color=MUTED, anchor="start"))
    f.append(line(L, yIc0, R, yIc0, color="#bbbbbb", sw=1))          # вісь часу низу

    # 90% / 10% орієнтири на наростанні/спаді (легка пунктирна сітка)
    y90 = yIcH + (yIc0 - yIcH) * 0.1
    y10 = yIcH + (yIc0 - yIcH) * 0.9
    f.append(line(L, y90, R, y90, color="#eeeeee", sw=1, dash="2,4"))
    f.append(line(L, y10, R, y10, color="#eeeeee", sw=1, dash="2,4"))
    f.append(text(L - 6, y90 + 4, "90%", size=9, color=MUTED, anchor="end"))
    f.append(text(L - 6, y10 + 4, "10%", size=9, color=MUTED, anchor="end"))

    # ── підсвітити плато розсмоктування (найдорожчий час) ──
    f.append(rect(t_off, yIcH - 4, t_s_e - t_off, 8, fill="#fdecea", stroke=POS, sw=1.6, rx=3))

    # ── чотири фігурні позначки часів під низом ──
    yb = yIc0 + 30
    def span(x1, x2, lab, col, sub):
        mid = (x1 + x2) / 2
        out = [line(x1, yb, x2, yb, color=col, sw=2),
               line(x1, yb - 5, x1, yb + 5, color=col, sw=2),
               line(x2, yb - 5, x2, yb + 5, color=col, sw=2),
               text(mid, yb - 9, lab, size=12, color=col, bold=True),
               text(mid, yb + 18, sub, size=10, color=MUTED)]
        return "".join(out)

    f.append(span(t_on, t_d_e, "t_d", INK, "затримка"))
    f.append(span(t_d_e, t_r_e, "t_r", INK, "наростання"))
    f.append(span(t_off, t_s_e, "t_s", POS, "розсмоктування"))
    f.append(span(t_s_e, t_f_e, "t_f", INK, "спад"))

    # дужки «увімкнення» / «вимкнення»
    f.append(text((t_on + t_r_e) / 2, yb + 44, "УВІМКНЕННЯ", size=11, color=FIELD, bold=True))
    f.append(text((t_off + t_f_e) / 2, yb + 44, "ВИМКНЕННЯ", size=11, color=POS, bold=True))

    f.append(fitbox(150, H - 34, 580, 26,
                    "Ic «висить» на стелі весь час t_s, поки з бази вимітається накопичений заряд — аж тоді починає спадати.",
                    size=11, fill="#ffffff", stroke="#e7c9c5", color=MUTED))

    render(os.path.join(IMG, "waveform.svg"), W, H, *f)


# ── Фігура 2: charge.svg — профіль заряду в базі ────────────────────────────
def fig_charge():
    W, H = 880, 420
    f = [text(W / 2, 30, "Звідки час розсмоктування: зайвий заряд неосновних носіїв у базі",
              size=16, bold=True)]

    def panel(px, title, deep):
        pw, ph = 360, 320
        f.append(rect(px, 56, pw, ph, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
        f.append(text(px + pw / 2, 78, title, size=13, bold=True))

        # вісь: ліворуч емітерний край бази (B-E), праворуч колекторний (B-C)
        ax_l, ax_r = px + 60, px + pw - 50
        base_y = 320
        top_y = 130
        f.append(line(ax_l, base_y, ax_r, base_y, color=INK, sw=1.6))   # вісь x (ширина бази)
        f.append(line(ax_l, base_y, ax_l, top_y, color=INK, sw=1.6))    # вісь концентрації
        f.append(text(ax_l - 6, top_y - 6, "n", size=12, color=INK, anchor="end", italic=True))
        f.append(text(ax_l, base_y + 18, "B-E", size=11, color=POS, bold=True))
        f.append(text(ax_r, base_y + 18, "B-C", size=11, color=NEG, bold=True))
        f.append(text((ax_l + ax_r) / 2, base_y + 18, "ширина бази", size=10, color=MUTED))

        hi = top_y + 14        # висока концентрація біля емітера
        if not deep:
            # активний: трикутник — лінійний спад до ~0 на колекторі
            f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" opacity="0.85"/>'
                     % (ax_l, hi, ax_r, base_y - 2, ax_l, base_y - 2, "#9ec7ff"))
            f.append(line(ax_l, hi, ax_r, base_y - 2, color=NEG, sw=2.4))
            f.append(text((ax_l + ax_r) / 2, 240, "градієнт = струм", size=11, color=NEG, bold=True))
            f.append(fitbox(px + 30, base_y + 36, pw - 60, 30,
                            "колекторний край ≈ 0:\nзайвого заряду нема → вимикається миттєво",
                            size=10, fill="#eef4ff", stroke=NEG, color=INK))
        else:
            # насичення: трапеція — концентрація піднята й на колекторному краї
            hc = base_y - 90    # ненульова концентрація на колекторі
            f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" opacity="0.85"/>'
                     % (ax_l, hi, ax_r, hc, ax_r, base_y - 2, ax_l, base_y - 2, "#f3b6ae"))
            f.append(line(ax_l, hi, ax_r, hc, color=POS, sw=2.4))
            # підсвітити «зайвий» блок під колекторним краєм
            f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,3"/>'
                     % (ax_l, base_y - 2, ax_r, base_y - 2, ax_r, hc, ax_l, base_y - 2, POS))
            f.append(text((ax_l + ax_r) / 2, hc - 14, "ЗАЙВИЙ заряд Qs", size=11, color=POS, bold=True))
            f.append(fitbox(px + 30, base_y + 36, pw - 60, 30,
                            "колекторний край ПІДНЯТИЙ:\nцей заряд треба вимести → час t_s",
                            size=10, fill="#fdecea", stroke=POS, color="#9a2b22"))

    panel(40, "Активний / на межі насичення", deep=False)
    panel(480, "Глибоке насичення (перекачана база)", deep=True)

    render(os.path.join(IMG, "charge.svg"), W, H, *f)


# ── Фігура 3: speedup.svg — пришвидшувальний конденсатор ────────────────────
def fig_speedup():
    W, H = 880, 420
    f = [text(W / 2, 30, "Пришвидшувальний конденсатор: сплеск струму на кожному фронті",
              size=16, bold=True)]

    # ── ліва панель: схема ──
    px, py, pw, ph = 30, 56, 360, 330
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(px + pw / 2, py + 22, "C паралельно резистору бази", size=13, bold=True))

    topY, botY = py + 60, py + ph - 36
    t = npn(px + 250, (topY + botY) / 2 + 6, "")
    Sx = t.xc
    f.append(rail_pos(Sx - 40, Sx + 40, topY))
    f.append(line(Sx, topY, Sx, t.yc, color=INK, sw=2))             # колектор → +V
    f.append(t.svg)
    f.append(line(Sx, t.ye, Sx, botY, color=INK, sw=2))            # емітер → GND
    f.append(gnd(Sx, botY))
    f.append(text(Sx + 36, t.yc + 8, "+V", size=11, color=POS, anchor="start", bold=True))

    # вхід ліворуч → вузол A → Rб (низ) та C (верх) паралельно → база
    inX = px + 30
    nodeA = px + 70
    by = t.yb
    f.append(line(inX, by, nodeA, by, color=FIELD, sw=2.2))
    f.append(text(inX - 2, by + 4, "вхід", size=11, color=FIELD, bold=True, anchor="end"))
    f.append(dot_(nodeA, by))
    # Rб (нижче) і C (вище) між nodeA та базою
    rs, rl, rr = res_h(nodeA + (t.xb - nodeA) / 2, by + 26, t.xb - nodeA - 8, "Rб", lab_above=False)
    f.append(rs)
    f.append(line(nodeA, by, nodeA, by + 26, color=INK, sw=1.8))
    f.append(line(nodeA, by + 26, rl, by + 26, color=INK, sw=1.8))
    f.append(line(rr, by + 26, t.xb, by + 26, color=INK, sw=1.8))
    f.append(line(t.xb, by + 26, t.xb, by, color=INK, sw=1.8))
    cs, cl, cr = cap_h(nodeA + (t.xb - nodeA) / 2, by - 26, t.xb - nodeA - 14, "C")
    f.append(cs)
    f.append(line(nodeA, by, nodeA, by - 26, color=INK, sw=1.8))
    f.append(line(nodeA, by - 26, cl, by - 26, color=INK, sw=1.8))
    f.append(line(cr, by - 26, t.xb, by - 26, color=INK, sw=1.8))
    f.append(line(t.xb, by - 26, t.xb, by, color=INK, sw=1.8))
    f.append(dot_(t.xb, by))

    # ── права панель: дві криві струму бази ──
    qx, qy, qw, qh = 430, 56, 420, 330
    f.append(rect(qx, qy, qw, qh, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(qx + qw / 2, qy + 22, "струм бази в часі", size=13, bold=True))

    axL, axR = qx + 50, qx + qw - 30
    zero = qy + 200
    f.append(line(axL, zero, axR, zero, color="#bbbbbb", sw=1.4))
    f.append(text(axL - 6, zero + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(axR, zero + 16, "час", size=11, color=MUTED, anchor="end"))

    ton, toff = qx + 130, qx + 300
    steady = 28          # сталий рівень Ib через Rб
    spikeP = 95          # піковий додатний сплеск (увімкнення)
    spikeN = 78          # піковий від'ємний (вимкнення — витягує заряд)

    # без конденсатора (сірий, прямокутний)
    f.append(line(axL, zero, ton, zero, color="#c9c9c9", sw=2))
    f.append(line(ton, zero, ton, zero - steady, color="#c9c9c9", sw=2))
    f.append(line(ton, zero - steady, toff, zero - steady, color="#c9c9c9", sw=2))
    f.append(line(toff, zero - steady, toff, zero, color="#c9c9c9", sw=2))
    f.append(line(toff, zero, axR, zero, color="#c9c9c9", sw=2))
    f.append(text(axR - 4, zero - steady - 6, "без C", size=10, color="#9a9a9a", anchor="end"))

    # з конденсатором (синій, зі сплесками, що спадають до сталого)
    pts = ["%.1f,%.1f" % (axL, zero)]
    pts.append("%.1f,%.1f" % (ton, zero))
    pts.append("%.1f,%.1f" % (ton, zero - spikeP))            # стрибок угору
    for i in range(1, 26):                                    # спад до steady
        x = ton + i * 2.2
        y = zero - (steady + (spikeP - steady) * math.exp(-i / 5.0))
        pts.append("%.1f,%.1f" % (x, y))
    pts.append("%.1f,%.1f" % (toff, zero - steady))
    pts.append("%.1f,%.1f" % (toff, zero + spikeN))           # стрибок ВНИЗ (від'ємний)
    for i in range(1, 26):
        x = toff + i * 2.2
        y = zero + spikeN * math.exp(-i / 5.0)
        pts.append("%.1f,%.1f" % (x, y))
    pts.append("%.1f,%.1f" % (axR, zero))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" L ".join(pts), NEG))

    f.append(text(ton + 6, zero - spikeP - 4, "сплеск +: швидко заганяє", size=10, color=NEG, anchor="start"))
    f.append(text(toff + 6, zero + spikeN + 16, "сплеск −: витягує заряд", size=10, color=POS, anchor="start"))
    f.append(line(ton, zero - steady, ton, zero, color="#eeeeee", sw=1, dash="2,3"))
    f.append(text(qx + qw / 2, zero - steady - 2, "сталий Ib (через Rб)", size=9, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "На фронті конденсатор — майже коротке: уся напруга йде в базу сплеском; між фронтами струм задає Rб.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "speedup.svg"), W, H, *f)


def rail_pos(x1, x2, y):
    return line(x1, y, x2, y, color=POS, sw=2.4)


def dot_(cx, cy):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (cx, cy, INK)


# ── Фігура 4: cures.svg — три способи проти насичення ───────────────────────
def fig_cures():
    W, H = 900, 430
    f = [text(W / 2, 30, "Три способи не дати ключу глибоко насититися", size=16, bold=True)]

    pw, ph = 280, 330
    gap = 14
    x0 = 18

    def head(px, t1):
        f.append(rect(px, 56, pw, ph, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
        f.append(text(px + pw / 2, 80, t1, size=13, bold=True))

    # ── 1) примусове β ──
    p1 = x0
    head(p1, "1 · Примусове β")
    t = npn(p1 + 150, 200, "")
    Sx = t.xc
    f.append(rail_pos(Sx - 34, Sx + 34, 116))
    f.append(line(Sx, 116, Sx, t.yc, color=INK, sw=2))
    f.append(t.svg)
    f.append(line(Sx, t.ye, Sx, 300, color=INK, sw=2))
    f.append(gnd(Sx, 300))
    rs, rl, rr = res_h(t.xb - 40, t.yb, 36, "Rб")
    f.append(rs)
    f.append(line(rr, t.yb, t.xb, t.yb, color=INK, sw=2))
    f.append(line(rl - 30, t.yb, rl, t.yb, color=FIELD, sw=2))
    f.append(text(rl - 34, t.yb + 4, "вхід", size=11, color=FIELD, anchor="end", bold=True))
    f.append(fitbox(p1 + 16, 330, pw - 32, 48,
                    "просто не лити забагато в базу\n(Ib ≈ Ic/10). Дешево, та межа\nнасичення «гуляє» з екземпляром",
                    size=10, fill="#eef6ef", stroke=FIELD, color=INK))

    # ── 2) Бейкерів затиск ──
    p2 = x0 + pw + gap
    head(p2, "2 · Бейкерів затиск")
    t = npn(p2 + 130, 200, "")
    Sx = t.xc
    f.append(rail_pos(Sx - 34, Sx + 34, 116))
    f.append(line(Sx, 116, Sx, t.yc, color=INK, sw=2))
    f.append(t.svg)
    f.append(line(Sx, t.ye, Sx, 300, color=INK, sw=2))
    f.append(gnd(Sx, 300))
    # послідовний діод у базі (вказує до бази)
    serX = t.xb - 60
    f.append(diode_h(serX, t.yb, 28, point_right=True, color=INK, label="D1"))
    f.append(line(serX + 14, t.yb, t.xb, t.yb, color=INK, sw=2))
    nodeIn = serX - 14
    f.append(line(nodeIn - 30, t.yb, nodeIn, t.yb, color=FIELD, sw=2))
    f.append(text(nodeIn - 34, t.yb + 4, "вхід", size=11, color=FIELD, anchor="end", bold=True))
    f.append(dot_(nodeIn, t.yb))
    # зворотний діод база-вхід → колектор (D2): від вузла входу вгору до колектора
    f.append(line(nodeIn, t.yb, nodeIn, 150, color=INK, sw=1.8))
    f.append(diode_h(nodeIn + 40, 150, 28, point_right=True, color=POS, label="D2"))
    f.append(line(nodeIn, 150, nodeIn + 26, 150, color=INK, sw=1.8))
    f.append(line(nodeIn + 54, 150, Sx, 150, color=POS, sw=1.8))
    f.append(line(Sx, 150, Sx, t.yc, color=POS, sw=1.8))
    f.append(dot_(Sx, 150))
    f.append(fitbox(p2 + 16, 330, pw - 32, 48,
                    "D2 відводить надлишок бази в колектор,\nперш ніж той сяде надто низько —\nтранзистор спиняється НА МЕЖІ",
                    size=10, fill="#fdf3e8", stroke=ORANGE, color="#7a4e1d"))

    # ── 3) Шотткі-транзистор ──
    p3 = x0 + 2 * (pw + gap)
    head(p3, "3 · Шотткі-транзистор")
    t = npn(p3 + 135, 200, "")
    Sx = t.xc
    f.append(rail_pos(Sx - 34, Sx + 34, 116))
    f.append(line(Sx, 116, Sx, t.yc, color=INK, sw=2))
    f.append(t.svg)
    f.append(line(Sx, t.ye, Sx, 300, color=INK, sw=2))
    f.append(gnd(Sx, 300))
    rs, rl, rr = res_h(t.xb - 40, t.yb, 36, "Rб")
    f.append(rs)
    f.append(line(rr, t.yb, t.xb, t.yb, color=INK, sw=2))
    f.append(line(rl - 30, t.yb, rl, t.yb, color=FIELD, sw=2))
    f.append(text(rl - 34, t.yb + 4, "вхід", size=11, color=FIELD, anchor="end", bold=True))
    # діод Шотткі база→колектор (вбудований)
    f.append(line(t.xb, t.yb, t.xb, 150, color=NEG, sw=1.8))
    f.append(schottky_h(t.xb + 40, 150, 32, point_right=True, color=NEG))
    f.append(line(t.xb, 150, t.xb + 24, 150, color=NEG, sw=1.8))
    f.append(line(t.xb + 56, 150, Sx, 150, color=NEG, sw=1.8))
    f.append(line(Sx, 150, Sx, t.yc, color=NEG, sw=1.8))
    f.append(dot_(t.xb, t.yb))
    f.append(dot_(Sx, 150))
    f.append(fitbox(p3 + 16, 330, pw - 32, 48,
                    "діод Шотткі вбудований база-колектор;\nвідкриється раніше за B-C перехід →\nнасичення просто не настає",
                    size=10, fill="#eef4ff", stroke=NEG, color=INK))

    render(os.path.join(IMG, "cures.svg"), W, H, *f)


if __name__ == "__main__":
    fig_waveform()
    fig_charge()
    fig_speedup()
    fig_cures()
    print("OK: waveform, charge, speedup, cures -> img/")
