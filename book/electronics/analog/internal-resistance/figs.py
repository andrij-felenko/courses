# -*- coding: utf-8 -*-
"""Фігури до ВСТАВОК теми «Внутрішній опір»:
  comp-source-impedances.md → source-impedances.svg, source-sag.svg

(Метод навантажувальної прямої винесено в окрему тему book:electronics/load-line —
його фігури load-line.svg / nonlinear-load-line.svg тут більше не генеруються.)

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


if __name__ == "__main__":
    fig_source_impedances()
    fig_source_sag()
    print("OK: 2 фігури вставок у", IMG)
