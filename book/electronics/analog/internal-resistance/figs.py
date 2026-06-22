# -*- coding: utf-8 -*-
"""Фігури до ВСТАВОК теми «Внутрішній опір»:
  comp-source-impedances.md → source-impedances.svg, source-sag.svg
  math-load-line.md         → load-line.svg, nonlinear-load-line.svg

Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Фігури самої СТАТТІ (ideal-vs-real, internal-r, vi-characteristic, measure-r,
examples) тут НЕ чіпаємо — стаття готова."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Шпаргалка опорів на логарифмічній осі ────────────────────────────────
def fig_source_impedances():
    W, H = 900, 430
    f = [text(W / 2, 30, "Внутрішній опір поширених джерел: від міліомів до десятків омів",
              size=17, bold=True),
         text(W / 2, 52, "що менший r, то «жорсткіше» джерело й більший струм воно дасть без просідання",
              size=11, color=MUTED, italic=True)]

    # вісь log10(r): декади від 1 мОм (-3) до 100 Ом (+2)
    x0, x1, axis_y = 92, 808, 232
    lo_dec, hi_dec = -3, 2                      # 10^-3 Ω .. 10^2 Ω
    def X(r_ohm):
        d = math.log10(r_ohm)
        return x0 + (d - lo_dec) / (hi_dec - lo_dec) * (x1 - x0)

    f.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    decade_lbl = {-3: "1 мΩ", -2: "10 мΩ", -1: "0.1 Ω", 0: "1 Ω", 1: "10 Ω", 2: "100 Ω"}
    for d in range(lo_dec, hi_dec + 1):
        xx = x0 + (d - lo_dec) / (hi_dec - lo_dec) * (x1 - x0)
        f.append(line(xx, axis_y - 5, xx, axis_y + 5, color=INK, sw=1.4))
        f.append(text(xx, axis_y + 22, decade_lbl[d], size=10, color=MUTED))

    # підписи країв осі
    f.append(text(x0, axis_y - 96, "◄ жорсткі (великий струм)", size=11, color=FIELD,
                  anchor="start", bold=True))
    f.append(text(x1, axis_y - 96, "м'які (малий струм) ►", size=11, color=POS,
                  anchor="end", bold=True))

    # джерела: (r_Ω, назва, струм, колір, вгору?)
    src = [
        (0.010, "авто (свинц.)", "сотні А",   FIELD, True),
        (0.05,  "Li-Ion, NiMH",  "кілька А",  FIELD, False),
        (0.22,  "AA лужна",      "сотні мА",  "#e08030", True),
        (0.30,  "USB-кабель",    "просідає",  "#e08030", False),
        (1.5,   "9В «крона»",    "десятки мА", POS,     True),
        (25.0,  "CR2032",        "мкА–мА",    POS,      False),
    ]
    for r_ohm, name, cur, col, up in src:
        cx = X(r_ohm)
        f.append(circle(cx, axis_y, 6, fill=col, stroke=col, sw=1))
        if up:
            f.append(line(cx, axis_y - 6, cx, axis_y - 46, color="#cccccc", sw=1))
            f.append(text(cx, axis_y - 58, name, size=10, color=col, bold=True))
            f.append(text(cx, axis_y - 44, cur, size=9, color=MUTED))
        else:
            f.append(line(cx, axis_y + 6, cx, axis_y + 40, color="#cccccc", sw=1))
            f.append(text(cx, axis_y + 52, name, size=10, color=col, bold=True))
            f.append(text(cx, axis_y + 66, cur, size=9, color=MUTED))

    # нижня рамка-висновок
    box = fitbox(110, 360, 680, 50,
                 "r росте, коли батарея сідає й на холоді, — тому стара чи мерзла «помирає під навантаженням».\n"
                 "Імпульсному споживачеві високоомне джерело (крона, таблетка) часто треба конденсатор поряд.",
                 size=11, fill="#f4f7f4", stroke=MUTED)
    f.append(box)
    render(os.path.join(IMG, "source-impedances.svg"), W, H, *f)


# ── 2. Просідання V = ε − I·r на чотирьох джерелах (таблиця-стовпчики) ───────
def fig_source_sag():
    W, H = 860, 400
    f = [text(W / 2, 30, "Просідання в дії: V = ε − I·r на реальних джерелах", size=17, bold=True),
         text(W / 2, 52, "той самий струм по-різному просаджує джерела — усе вирішує внутрішній опір",
              size=11, color=MUTED, italic=True)]

    cols = [(80, "джерело", "start"), (250, "ЕРС ε", "middle"), (350, "опір r", "middle"),
            (450, "струм I", "middle"), (570, "спад I·r", "middle"), (700, "на клемах", "middle")]
    for x, lbl, anc in cols:
        f.append(text(x, 96, lbl, size=10, color=MUTED, anchor=anc, bold=True))

    rows = [
        ("Li-Ion 18650", "3.7 В", "r=0.05 Ω", "3 А",   "0.15 В", "3.55 В", FIELD),
        ("AA лужна",     "1.5 В", "r=0.25 Ω", "1 А",   "0.25 В", "1.25 В", "#e08030"),
        ("9В «крона»",   "9.0 В", "r=1.5 Ω",  "0.3 А", "0.45 В", "8.55 В", "#e08030"),
        ("CR2032",       "3.0 В", "r=20 Ω",   "20 мА", "0.40 В", "2.6 В",  POS),
    ]
    y = 116
    for name, emf, r, cur, drop, vout, col in rows:
        f.append(rect(70, y, 740, 48, fill="#fafafa", stroke="#dddddd", sw=1.2))
        cy = y + 30
        f.append(text(80, cy, name, size=11, color=col, anchor="start", bold=True))
        f.append(text(250, cy, emf, size=11))
        f.append(text(350, cy, r, size=11))
        f.append(text(450, cy, cur, size=11))
        f.append(text(570, cy, drop, size=11, color=POS, bold=True))
        f.append(text(700, cy, vout, size=11, color=FIELD, bold=True))
        y += 58

    f.append(text(W / 2, 380,
                  "Мале r (Li-Ion) майже не просідає; велике r (крона, таблетка) втрачає помітну частку — звідси й вибір джерела.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "source-sag.svg"), W, H, *f)


# ── осі для графіків V–I ────────────────────────────────────────────────────
def _vi_axes(f, ox, oy, top, right):
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.8))          # вісь V →
    f.append(text(right, oy + 22, "напруга V", size=11))
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.8))           # вісь I ↑
    f.append(text(ox - 8, top - 4, "струм I", size=11, anchor="start", bold=True))


# ── 3. Лінія навантаження: джерело × резистор → перетин ─────────────────────
def fig_load_line():
    W, H = 820, 420
    f = [text(W / 2, 30, "Лінія навантаження: робоча точка — це перетин", size=18, bold=True),
         text(W / 2, 52, "джерело й навантаження мають спільні V та I — реальна точка там, де характеристики перетинаються",
              size=10, color=MUTED, italic=True)]
    ox, oy, top, right = 110, 360, 84, 720
    _vi_axes(f, ox, oy, top, right)

    # фізика: eps=10 В, r=100 Ω, R=200 Ω → V=6.667, I=33.3 мА
    eps, r, R = 10.0, 100.0, 200.0
    Vop = eps * R / (r + R)            # 6.667 В
    Iop = eps / (r + R)               # 33.3 мА
    Isc = eps / r                     # 100 мА
    # масштаб
    Vmax, Imax = 11.0, 110.0          # В, мА
    px = lambda v: ox + v / Vmax * (right - ox)
    py = lambda i: oy - i / Imax * (oy - top)

    # лінія джерела: (eps,0) → (0, Isc)
    f.append(line(px(eps), py(0), px(0), py(Isc), color=POS, sw=2.8))
    # лінія навантаження R з початку координат: V=I·R → точка (Vmax, Vmax/R*1000 мА)
    i_at_vmax = Vmax / R * 1000.0     # мА на правому краю
    f.append(line(px(0), py(0), px(Vmax), py(i_at_vmax), color=NEG, sw=2.6))

    # робоча точка + пунктири
    f.append(line(px(Vop), py(Iop), px(Vop), py(0), color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(px(Vop), py(Iop), px(0), py(Iop), color=MUTED, sw=1.2, dash="3 3"))
    f.append(circle(px(Vop), py(Iop), 6, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px(Vop) + 12, py(Iop) - 12, "робоча: 6.7 В, 33 мА", size=10, color=FIELD,
                  anchor="start", bold=True))

    # кінці
    f.append(circle(px(eps), py(0), 4, fill=POS, stroke=POS, sw=1))
    f.append(text(px(eps), py(0) + 20, "ε (хол. хід)", size=10, color=POS, bold=True))
    f.append(circle(px(0), py(Isc), 4, fill=POS, stroke=POS, sw=1))
    f.append(text(px(0) - 8, py(Isc), "I_кз = ε/r", size=10, color=POS, anchor="end", bold=True))

    f.append(text(px(7.0), py(78), "джерело: V = ε − I·r  (нахил −1/r)", size=10, color=POS, bold=True))
    f.append(text(px(8.4), py(38), "навантаження R: V = I·R", size=10, color=NEG, bold=True))
    render(os.path.join(IMG, "load-line.svg"), W, H, *f)


# ── 4. Сила методу: нелінійне навантаження (крива світлодіода) ──────────────
def fig_nonlinear_load_line():
    W, H = 860, 420
    f = [text(W / 2, 30, "Сила методу: нелінійне навантаження (діод, світлодіод)", size=17, bold=True),
         text(W / 2, 52, "для діода нема формули V=I·R — та перетин лінії навантаження з його кривою однаково дає робочу точку",
              size=10, color=MUTED, italic=True)]
    ox, oy, top, right = 110, 360, 84, 740
    _vi_axes(f, ox, oy, top, right)

    Vmax, Imax = 4.0, 60.0
    px = lambda v: ox + v / Vmax * (right - ox)
    py = lambda i: oy - i / Imax * (oy - top)

    # експоненційна крива світлодіода: I = Is*(exp((V-Vk)/n)-1), коліно ~2.0 В
    Is, n, Vk = 0.02, 0.13, 1.6
    pts = []
    for k in range(0, 51):
        V = Vmax * k / 50.0
        I = Is * (math.exp((V - Vk) / n) - 1.0)
        if I < 0:
            I = 0.0
        if I > Imax:
            I = Imax
        pts.append("%.1f,%.1f" % (px(V), py(I)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), FIELD))
    f.append(text(px(3.05), py(54), "крива світлодіода", size=10, color=FIELD,
                  anchor="middle", bold=True))

    # лінія навантаження джерела: ε=3.0 В, I_кз=50 мА (r=60 Ω) → (3,0)-(0,50)
    eps, Isc = 3.0, 50.0
    f.append(line(px(eps), py(0), px(0), py(Isc), color=POS, sw=2.4))
    f.append(text(px(0) - 8, py(Isc), "I_кз", size=9, color=POS, anchor="end", bold=True))

    # робоча точка: перетин (приблизно V≈2.18 В, I≈13.7 мА — оцінимо чисельно)
    def diode_I(V):
        return max(0.0, Is * (math.exp((V - Vk) / n) - 1.0))
    def load_I(V):
        return Isc * (1.0 - V / eps)
    Vop = 0.0
    for k in range(1, 4000):
        V = Vmax * k / 4000.0
        if diode_I(V) >= load_I(V):
            Vop = V
            break
    Iop = load_I(Vop)
    f.append(circle(px(Vop), py(Iop), 6, fill=POS, stroke=POS, sw=1))
    f.append(text(px(Vop) + 10, py(Iop) - 12, "робоча точка", size=10, color=POS,
                  anchor="start", bold=True))

    # штрихова лінія — більший r (менший нахил): I_кз=35 мА
    Isc2 = 35.0
    f.append(line(px(eps), py(0), px(0), py(Isc2), color="#e08030", sw=2.2, dash="6 4"))
    for k in range(1, 4000):
        V = Vmax * k / 4000.0
        if diode_I(V) >= Isc2 * (1.0 - V / eps):
            Vop2 = V
            break
    Iop2 = Isc2 * (1.0 - Vop2 / eps)
    f.append(circle(px(Vop2), py(Iop2), 5, fill="#e08030", stroke="#e08030", sw=1))
    f.append(text(px(Vop2) - 6, py(Iop2) + 22, "більший r → точка зсувається", size=9,
                  color="#e08030", anchor="middle", bold=True))

    # пояснювальна рамка
    f.append(fitbox(130, 104, 320, 96,
                    "Змінюєш ε чи r — лінія рухається,\n"
                    "а робоча точка ковзає\n"
                    "по кривій приладу.\n"
                    "Так задають режим діодів і транзисторів.",
                    size=11, fill="#eef7f0", stroke=FIELD))
    render(os.path.join(IMG, "nonlinear-load-line.svg"), W, H, *f)


if __name__ == "__main__":
    fig_source_impedances()
    fig_source_sag()
    fig_load_line()
    fig_nonlinear_load_line()
    print("OK: 4 фігури вставок у", IMG)
