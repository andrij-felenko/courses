# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Ethernet-кабель RJ45».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори жил T568B (для наочності)
WIRE = {
    "wo": ("#e08a2c", "біло-жовтогар."),   # white/orange
    "o":  ("#e8630a", "жовтогарячий"),
    "wg": ("#3aa655", "біло-зелений"),
    "g":  ("#1f8b3f", "зелений"),
    "wb": ("#3b6fd6", "біло-синій"),
    "b":  ("#2457d6", "синій"),
    "wbr":("#9c6b3f", "біло-коричн."),
    "br": ("#6b4423", "коричневий"),
}


# ── 1. Чому кручена пара: спільна завада йде синфазно, приймач бере різницю ────
def fig_twisted_pair():
    W, H = 880, 470
    f = [text(W / 2, 30, "Кручена пара: завада б'є в обидві жили однаково, приймач бере РІЗНИЦЮ — і завада зникає",
              size=14.5, bold=True)]

    # Ліворуч: дві скручені жили як дві синусоїди в протифазі
    x0, x1 = 60, 470
    ymid = 150
    amp = 26
    turns = 5
    stepN = 200
    pa, pb = [], []
    for i in range(stepN + 1):
        t = i / stepN
        xx = x0 + (x1 - x0) * t
        ang = t * turns * 2 * math.pi
        pa.append((xx, ymid + amp * math.sin(ang)))
        pb.append((xx, ymid - amp * math.sin(ang)))

    def poly(pts, color, sw):
        d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    f.append(poly(pa, WIRE["wg"][0], 3.2))
    f.append(poly(pb, WIRE["g"][0], 3.2))
    f.append(text(x0 - 10, ymid - amp + 2, "A", size=13, color=WIRE["wg"][0], bold=True, anchor="end"))
    f.append(text(x0 - 10, ymid + amp + 4, "B", size=13, color=WIRE["g"][0], bold=True, anchor="end"))
    # підпис пари — ПІД хвилями, де немає стрілок
    f.append(text((x0 + x1) / 2, ymid + amp + 34, "одна кручена пара (два дроти сплетено)", size=11, color=MUTED))

    # Завада-стрілки згори — б'ють в обидві жили однаково (синфазно)
    for k in range(4):
        zx = x0 + 70 + k * 100
        f.append(arrow(zx, ymid - amp - 44, zx, ymid - amp - 12, color=POS, sw=2.0))
    f.append(text((x0 + x1) / 2, ymid - amp - 56, "зовнішня завада (наведення) — в обидві жили ОДНАКОВО",
                  size=10.5, color=POS, bold=True))

    # Праворуч: приймач-віднімач
    rx, ry, rw, rh = 560, 96, 260, 150
    f.append(rect(rx, ry, rw, rh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(rx + rw / 2, ry + 26, "приймач бере A − B", size=13, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, ry + 58, "сигнал:  +s − (−s) = 2s", size=12, color=INK))
    f.append(text(rx + rw / 2, ry + 84, "завада:  +z − (+z) = 0", size=12, color=POS))
    f.append(text(rx + rw / 2, ry + 118, "корисне подвоюється,", size=10.5, color=INK))
    f.append(text(rx + rw / 2, ry + 136, "спільна завада гине", size=10.5, color=FIELD, italic=True))
    f.append(arrow(x1 + 6, ymid, rx - 6, ry + 40, color=INK, sw=1.8))

    # Низ: чому саме СКРУТКА (а не просто дві паралельні жили)
    b, _, _ = textbox(W / 2, 330,
                      "скрутка дає рівність: обидві жили по черзі бувають ближчою до джерела завади, тож наводка на них ЗРІВНЮЄТЬСЯ — тому віднімання її вбиває",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    b2, _, _ = textbox(W / 2, 392,
                       "більше витків на метр → щільніше зрівнювання → вища категорія кабелю тримає вищу частоту",
                       size=11, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b2)
    b3, _, _ = textbox(W / 2, 446,
                       "чотири такі пари в одній оболонці, кожна зі СВОЇМ кроком скрутки — щоб пари не наводили одна на одну",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b3)
    render(os.path.join(IMG, "twisted-pair.svg"), W, H, *f)


# ── 2. Розпіновка T568B: 8 пінів, 4 пари, хто що несе на різних швидкостях ─────
def fig_pinout():
    W, H = 900, 560
    f = [text(W / 2, 30, "Розводка RJ45 за T568B: 8 пінів = 4 кручені пари",
              size=15, bold=True)]

    order = ["wo", "o", "wg", "b", "wb", "g", "wbr", "br"]  # T568B зліва направо, пін 1..8
    pair_of = {"wo": 2, "o": 2, "wg": 3, "b": 1, "wb": 1, "g": 3, "wbr": 4, "br": 4}
    pair_col = {1: WIRE["wb"][0], 2: WIRE["o"][0], 3: WIRE["g"][0], 4: WIRE["br"][0]}

    # Роз'єм: 8 контактів рядком, широкі клітини щоб підписи не злипались
    n = 8
    cw = 88
    gx = (W - n * cw) / 2
    top = 76
    plug_h = 74
    f.append(rect(gx, top, n * cw, plug_h, fill="#fafbfc", stroke=INK, sw=1.8, rx=8))
    f.append(text(W / 2, top - 12, "прозорий роз'єм 8P8C, фіксатор ВНИЗУ, дивимось на контакти",
                  size=10.5, color=MUTED))
    for i, key in enumerate(order):
        cx = gx + cw * i + cw / 2
        col, name = WIRE[key]
        # контакт-жила
        f.append(rect(cx - 16, top + 12, 32, plug_h - 24, fill=col, stroke=INK, sw=1.2, rx=3))
        # номер піна над роз'ємом
        f.append(text(cx, top - 30, str(i + 1), size=13, color=INK, bold=True))
        # назва кольору під роз'ємом (двома рядками, дрібно, у своїй клітині)
        nm = name.split()
        f.append(text(cx, top + plug_h + 20, nm[0], size=9, color=INK))
        if len(nm) > 1:
            f.append(text(cx, top + plug_h + 33, nm[1], size=9, color=INK))
        # номер пари ще нижче
        f.append(text(cx, top + plug_h + 52, "пара %d" % pair_of[key], size=9,
                      color=pair_col[pair_of[key]], bold=True))

    # Дуги, що показують, які піни утворюють ОДНУ скручену пару
    arc_y = top + plug_h + 70
    def arc(i, j, depth, color):
        xi = gx + cw * i + cw / 2
        xj = gx + cw * j + cw / 2
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="2.2"/>' % (xi, arc_y, (xi + xj) / 2, arc_y + depth, xj, arc_y, color))
    # пари за T568B: (1,2)=пара2 ; (3,6)=пара3 ; (4,5)=пара1 ; (7,8)=пара4
    f.append(arc(0, 1, 26, pair_col[2]))
    f.append(arc(2, 5, 54, pair_col[3]))
    f.append(arc(3, 4, 26, pair_col[1]))
    f.append(arc(6, 7, 26, pair_col[4]))
    f.append(text(W / 2, arc_y + 74, "дуги — які піни сплетено в одну кручену пару (пара 3 «стрибає» через 4-5)",
                  size=10, color=MUTED, italic=True))

    # Дві колонки: що несуть піни на 100 Мбіт проти 1 Гбіт
    cy = 380
    lx, lw = 70, 360
    f.append(rect(lx, cy, lw, 150, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(lx + lw / 2, cy + 26, "100BASE-TX (100 Мбіт)", size=12.5, bold=True))
    f.append(text(lx + lw / 2, cy + 52, "пари 2 і 3 працюють, 1 і 4 — вільні", size=10.5, color=INK))
    f.append(text(lx + lw / 2, cy + 82, "пін 1,2  →  передавання (TX)", size=11, color=WIRE["o"][0]))
    f.append(text(lx + lw / 2, cy + 104, "пін 3,6  →  приймання (RX)", size=11, color=WIRE["g"][0]))
    f.append(text(lx + lw / 2, cy + 132, "тому старий лінк живе навіть на 2 парах", size=10, color=MUTED, italic=True))

    rx2, rw2 = 470, 360
    f.append(rect(rx2, cy, rw2, 150, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=10))
    f.append(text(rx2 + rw2 / 2, cy + 26, "1000BASE-T (1 Гбіт)", size=12.5, bold=True, color=FIELD))
    f.append(text(rx2 + rw2 / 2, cy + 52, "усі 4 пари, кожна в ОБИДВА боки водночас", size=10.5, color=INK))
    f.append(text(rx2 + rw2 / 2, cy + 80, "4 пари × 250 Мбіт = 1000 Мбіт", size=11, color=INK))
    f.append(text(rx2 + rw2 / 2, cy + 104, "дуплекс на одній парі — гібридна схема", size=10.5, color=INK))
    f.append(text(rx2 + rw2 / 2, cy + 132, "тому для гігабіта потрібні ВСІ 8 жил цілі", size=10, color=FIELD, italic=True))

    render(os.path.join(IMG, "t568b-pinout.svg"), W, H, *f)


# ── 3. Телефонне коріння розкладки: концентричне вкладення пар (USOC → RJ45) ───
def fig_usoc_nesting():
    W, H = 1010, 560
    f = [text(W / 2, 30, "Звідки «розірвана пара» в RJ45: телефонні пари вкладено концентрично від центру",
              size=14.5, bold=True)]

    # Малює один роз'єм: n контактів рядком + вкладені дуги пар знизу.
    # pairs: список (i, j, color, label) — 0-based індекси контактів.
    def connector(cx0, top, n, cw, pairs, title, sub):
        parts = []
        gx = cx0
        plug_h = 58
        parts.append(rect(gx, top, n * cw, plug_h, fill="#fafbfc", stroke=INK, sw=1.7, rx=7))
        parts.append(text(gx + n * cw / 2, top - 14, title, size=13, bold=True))
        parts.append(text(gx + n * cw / 2, top - 32, sub, size=10, color=MUTED))
        # контакти + номери
        for i in range(n):
            ccx = gx + cw * i + cw / 2
            parts.append(rect(ccx - 8, top + 10, 16, plug_h - 20, fill="#e9edf1", stroke=INK, sw=1.0, rx=2))
            parts.append(text(ccx, top - 2 + plug_h + 16, str(i + 1), size=11, color=INK, bold=True))
        # вкладені дуги: глибша дуга = зовнішніша пара, щоб вони не накладались
        arc_base = top + plug_h + 26
        for (i, j, col, lab) in pairs:
            xi = gx + cw * i + cw / 2
            xj = gx + cw * j + cw / 2
            span = j - i
            depth = 16 + span * 15         # ширша пара — глибша дуга
            parts.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                         'stroke="%s" stroke-width="2.6"/>'
                         % (xi, arc_base, (xi + xj) / 2, arc_base + depth, xj, arc_base, col))
            # підпис пари — на дні своєї дуги, по центру, кожен на своїй глибині (не злипаються)
            parts.append(text((xi + xj) / 2, arc_base + depth + 13, lab, size=9.5, color=col, bold=True))
        return parts

    # ЛІВОРУЧ: телефонний 6-контактний роз'єм USOC (RJ11/14/25)
    cwL = 58
    nL = 6
    xL = 60
    topL = 110
    pairsL = [
        (2, 3, FIELD, "лінія 1 (центр)"),
        (1, 4, NEG,   "лінія 2"),
        (0, 5, POS,   "лінія 3"),
    ]
    f += connector(xL, topL, nL, cwL, pairsL,
                   "Телефон USOC — 6 контактів", "RJ11 / RJ14 / RJ25")
    f.append(text(xL + nL * cwL / 2, topL + 210,
                  "кожна нова лінія — кільцем ЗЗОВНІ", size=10.5, color=INK, italic=True))
    f.append(text(xL + nL * cwL / 2, topL + 228,
                  "→ дволінійний шнур працює й в однолінійному гнізді", size=10, color=MUTED))

    # ПРАВОРУЧ: мережевий 8-контактний роз'єм RJ45 / 8P8C
    cwR = 58
    nR = 8
    xR = 498
    topR = 110
    pairsR = [
        (3, 4, NEG,   "пара 1 (центр 4-5)"),
        (2, 5, FIELD, "пара 3 (розсунута!)"),
        (0, 1, POS,   "пара 2"),
        (6, 7, "#8a6d3b", "пара 4"),
    ]
    f += connector(xR, topR, nR, cwR, pairsR,
                   "Мережа RJ45 / 8P8C — 8 контактів", "той самий каркас, ще одне кільце")
    f.append(text(xR + nR * cwR / 2, topR + 210,
                  "центральна пара 4-5 і РОЗСУНУТА нею пара 3-6", size=10.5, color=INK, italic=True))
    f.append(text(xR + nR * cwR / 2, topR + 228,
                  "= успадкована телефонна геометрія, не мережевий винахід", size=10, color=MUTED))

    # стрілка спадковості між панелями
    f.append(arrow(xL + nL * cwL + 8, topL + 30, xR - 8, topR + 30, color=INK, sw=2.0))
    f.append(text((xL + nL * cwL + xR) / 2, topL + 18, "успадковано", size=10, color=INK, bold=True))

    # Нижня рамка: що ж тоді роблять T568A/T568B
    b, _, _ = textbox(W / 2, 430,
                      "T568A і T568B НЕ чіпають цей каркас: центр 4-5 і край 7-8 у них однакові.",
                      size=12, fill=FILL, stroke=LINE, bold=False)
    f.append(b)
    b2, _, _ = textbox(W / 2, 480,
                       "уся різниця A ↔ B — лише ЯКА пара лягає в кільце 1-2, а яка в 3-6 (зелена ↔ помаранчева)",
                       size=12, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b2)
    b3, _, _ = textbox(W / 2, 528,
                       "телефонний принцип 1970-х досі диктує форму роз'єма 2020-х",
                       size=11, fill=FILL, stroke=LINE, color=MUTED)
    f.append(b3)

    render(os.path.join(IMG, "usoc-nesting.svg"), W, H, *f)


if __name__ == "__main__":
    fig_twisted_pair()
    fig_pinout()
    fig_usoc_nesting()
    print("OK: 3 figures ->", IMG)
