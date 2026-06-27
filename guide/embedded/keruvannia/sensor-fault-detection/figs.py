# -*- coding: utf-8 -*-
"""Фігури до теми «Виявлення відмови давача».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

GOLD = "#b9770e"     # дрейф / тепле застереження
MED  = "#8e44ad"     # резервний / голосування


def _poly(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % q for q in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (p, color, sw, d))


# ── 1. Галерея почерків відмови davача ───────────────────────────────────────
def fig_failure_modes():
    W, H = 760, 430
    f = [text(W / 2, 26, "Почерк відмови: як саме давач бреше", size=15, bold=True)]

    pw, ph = 218, 118
    xs = [26, 271, 516]
    ys = [46, 188]

    def panel(x, y, color, title_, note, draw):
        f.append(rect(x, y, pw, ph, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4))
        f.append(text(x + pw / 2, y + 20, title_, size=12.5, color=color, bold=True))
        mid = y + ph / 2 + 6
        f.append(line(x + 12, mid + 30, x + pw - 12, mid + 30, color="#ededf0", sw=1.2))
        draw(x + 14, mid, pw - 28, color)
        f.append(text(x + pw / 2, y + ph - 6, note, size=9.5, color=MUTED, italic=True))

    random.seed(11)

    def healthy(x, y, w, col):
        pts = [(x + w * i / 40, y + random.uniform(-9, 9)) for i in range(41)]
        f.append(_poly(pts, FIELD, 1.8))

    def stuck(x, y, w, col):
        pts = [(x + w * i / 40, y + random.uniform(-7, 7)) for i in range(18)]
        flat = pts[-1][1]
        pts += [(x + w * i / 40, flat) for i in range(18, 41)]
        f.append(_poly(pts, col, 2.0))

    def rail(x, y, w, col):
        pts = [(x + w * i / 40, y + random.uniform(-7, 7)) for i in range(14)]
        pts += [(x + w * i / 40, y - 30) for i in range(14, 41)]     # вилетіло на стелю
        f.append(_poly(pts, col, 2.0))
        f.append(line(x, y - 30, x + w, y - 30, color=GOLD, sw=1.0, dash="3,3"))

    def dropout(x, y, w, col):
        for seg in ((0, 12), (16, 26), (32, 41)):
            pts = [(x + w * i / 40, y + random.uniform(-8, 8)) for i in range(*seg)]
            f.append(_poly(pts, col, 2.0))
        for i in (14, 29):
            f.append(text(x + w * i / 40, y + 2, "?", size=12, color=POS, bold=True))

    def noise(x, y, w, col):
        pts = []
        for i in range(41):
            amp = 9 if i < 18 else 30
            pts.append((x + w * i / 40, y + random.uniform(-amp, amp)))
        f.append(_poly(pts, col, 1.6))

    def drift(x, y, w, col):
        pts = [(x + w * i / 40, y + 22 - 44 * i / 40 + random.uniform(-5, 5)) for i in range(41)]
        f.append(_poly(pts, col, 2.0))
        f.append(line(x, y, x + w, y, color=FIELD, sw=1.0, dash="3,3"))

    panel(xs[0], ys[0], FIELD, "здоровий", "рівний шум довкола правди", healthy)
    panel(xs[1], ys[0], POS,   "завмер (stuck)", "значення прилипло намертво", stuck)
    panel(xs[2], ys[0], POS,   "виліт за межу (rail)", "вискочило за фізику", rail)
    panel(xs[0], ys[1], POS,   "пропадання (dropout)", "шина мовчить, NaN", dropout)
    panel(xs[1], ys[1], POS,   "вибух шуму", "розкид раптом зріс", noise)
    panel(xs[2], ys[1], GOLD,  "дрейф", "тихо сповзає вбік", drift)

    f.append(text(W / 2, 420,
                  "найпідступніший — «завмер»: брехня виходить чистою, гладшою за правду",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "failure-modes.svg"), W, H, *f)


# ── 2. Три швидкі ворота: межа, швидкість, тайм-аут ──────────────────────────
def fig_quick_gates():
    W, H = 900, 300
    f = [text(W / 2, 26, "Перший рубіж: три дешеві ворота на кожен відлік", size=15, bold=True)]

    f.append(rect(18, 110, 96, 56, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(66, 134, "сирий", size=12, bold=True))
    f.append(text(66, 152, "відлік", size=12, bold=True))

    gw = 144
    gates = [
        ("межа", "MIN ≤ x ≤ MAX", "фізично можливе?", 154),
        ("швидкість", "|x−x₋₁| ≤ ΔMAX", "стрибок реальний?", 336),
        ("свіжість", "оновився ≤ T тому", "давач ще живий?", 518),
    ]
    px = 114
    for name, rule, q, x in gates:
        f.append(arrow(px, 138, x, 138, color=INK, sw=2))
        f.append(rect(x, 104, gw, 68, fill="#eef6ff", stroke=NEG, sw=1.8))
        f.append(text(x + gw / 2, 124, name, size=12.5, color=NEG, bold=True))
        f.append(text(x + gw / 2, 143, rule, size=11, color=INK))
        f.append(text(x + gw / 2, 161, q, size=9.5, color=MUTED, italic=True))
        # «ні» вниз — у прапор відмови
        f.append(arrow(x + gw / 2, 172, x + gw / 2, 214, color=POS, sw=1.6))
        f.append(text(x + gw / 2 + 16, 196, "ні", size=10, color=POS, anchor="start", italic=True))
        px = x + gw

    f.append(arrow(px, 138, px + 30, 138, color=FIELD, sw=2))
    f.append(rect(px + 30, 110, 116, 56, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(px + 88, 134, "усі «так»:", size=11.5, color=FIELD, bold=True))
    f.append(text(px + 88, 152, "вірю числу", size=11.5, color=FIELD, bold=True))

    f.append(rect(170, 224, 560, 40, fill="#fdf3f2", stroke=POS, sw=1.6))
    f.append(text(450, 248, "будь-яке «ні» → давач під підозрою (прапор відмови)",
                  size=12, color=POS, bold=True))

    f.append(text(W / 2, 288,
                  "три перевірки, десяток рядків — ловлять найгрубіші відмови ще до решти тракту",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "quick-gates.svg"), W, H, *f)


# ── 3. Голосування й пастка спільної причини ─────────────────────────────────
def fig_voting():
    W, H = 860, 366
    f = [text(W / 2, 26, "Голосування ловить незалежну відмову — і сліпне до спільної", size=14.5, bold=True)]

    def scene(x, title_, vals, verdict, vcol, note):
        f.append(text(x + 170, 64, title_, size=12.5, bold=True))
        for i, (v, ok) in enumerate(vals):
            cy = 96 + i * 56
            col = POS if not ok else FIELD
            f.append(circle(x + 40, cy, 18, fill=("#fdf3f2" if not ok else "#eafaf0"),
                            stroke=col, sw=2))
            f.append(text(x + 40, cy + 5, "D%d" % (i + 1), size=11, color=col, bold=True))
            f.append(text(x + 76, cy + 5, v, size=12, color=col, anchor="start",
                          bold=(not ok)))
            f.append(arrow(x + 190, cy, x + 236, 152, color=col, sw=1.4))
        # голосувальник
        f.append(rect(x + 236, 130, 104, 44, fill=FILL, stroke=INK, sw=1.8))
        f.append(text(x + 288, 148, "голос", size=11, bold=True))
        f.append(text(x + 288, 165, "(медіана)", size=9, color=MUTED, italic=True))
        f.append(arrow(x + 288, 174, x + 288, 214, color=vcol, sw=2))
        f.append(rect(x + 224, 216, 128, 40, fill=("#eafaf0" if vcol == FIELD else "#fdf3f2"),
                      stroke=vcol, sw=1.8))
        f.append(text(x + 288, 240, verdict, size=11.5, color=vcol, bold=True))
        f.append(fitbox(x + 12, 272, 364, 46, note, size=11, color=MUTED, italic=True,
                        fill=BG, stroke="none", sw=0))

    scene(18, "Незалежна відмова: один збожеволів",
          [("12.0 м", True), ("12.1 м", True), ("47 м ✗", False)],
          "→ 12.05 м: вірно", FIELD,
          "двоє згодні, третій — викид:\nмедіана бере здорову пару, брехуна відкидає")

    f.append(line(W / 2, 70, W / 2, 322, color="#dddddd", sw=1.4, dash="4,4"))

    scene(448, "Спільна причина: обмерзли всі",
          [("47 м ✗", False), ("46 м ✗", False), ("48 м ✗", False)],
          "→ 47 м: брехня!", POS,
          "усі троє збрехали однаково (один лід):\nголос «згоден» і впевнено видає сміття")

    f.append(text(W / 2, 354,
                  "резерв рятує від випадкового збою кожного зокрема, не від однієї біди на всіх",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "voting.svg"), W, H, *f)


# ── 4. Що робити після виявлення: політика реакції ───────────────────────────
def fig_react_policy():
    W, H = 780, 270
    f = [text(W / 2, 26, "Виявив — мало; треба ще й безпечно відреагувати", size=15, bold=True)]

    steps = [
        ("підозра", "ворота / голос\nпідняли прапор", POS),
        ("підтвердь", "не з одного —\nN відліків поспіль", GOLD),
        ("познач bad", "геть із поєднання,\nвага → 0", NEG),
        ("підстрахуй", "останнє добре →\nмодель → fail-safe", FIELD),
    ]
    x = 22
    cx_list = []
    for name, body, col in steps:
        f.append(rect(x, 70, 162, 96, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 81, 92, name, size=12.5, color=col, bold=True))
        f.append(fitbox(x + 8, 104, 146, 54, body, size=10.5, color=INK,
                        fill=FILL, stroke="none", sw=0))
        cx_list.append(x + 81)
        x += 188
    for i in range(3):
        f.append(arrow(cx_list[i] + 81, 118, cx_list[i + 1] - 81, 118, color=INK, sw=2))

    # повернення з гістерезисом
    f.append(arrow(cx_list[3], 166, cx_list[1], 212, color=MED, sw=1.6, ))
    f.append(rect(cx_list[1] - 150, 214, 360, 38, fill="#f6f0fb", stroke=MED, sw=1.6))
    f.append(text(cx_list[1] + 30, 238,
                  "назад «здоровий» — лише через гістерезис, щоб не миготіти на межі",
                  size=11, color=MED, bold=True))

    f.append(text(W / 2, 264,
                  "знизити число виявності D (з FMEA) — пів справи; друга половина — що робити далі",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "react-policy.svg"), W, H, *f)


# ── 5. Багаторазовий модуль: усе на один канал ───────────────────────────────
def fig_module_anatomy():
    W, H = 880, 470
    f = [text(W / 2, 26, "Один канал — один детектор: що всередині модуля", size=15, bold=True)]

    # сирий відлік ліворуч
    f.append(rect(20, 200, 96, 64, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(68, 224, "сирий", size=12, bold=True))
    f.append(text(68, 242, "відлік", size=12, bold=True))
    f.append(text(68, 282, "x, now_ms", size=9.5, color=MUTED, italic=True))

    # блок воріт (миттєві перевірки)
    gx, gy, gw, gh = 152, 70, 196, 196
    f.append(rect(gx, gy, gw, gh, fill="#eef6ff", stroke=NEG, sw=1.8))
    f.append(text(gx + gw / 2, gy + 22, "миттєві ворота", size=12.5, color=NEG, bold=True))
    f.append(text(gx + gw / 2, gy + 38, "(стан майже не треба)", size=9, color=MUTED, italic=True))
    gates = ["NaN / ∞", "діапазон  MIN…MAX", "швидкість  |Δx|≤ΔMAX", "свіжість  Δt ≤ T"]
    for i, g in enumerate(gates):
        yy = gy + 64 + i * 30
        f.append(circle(gx + 18, yy - 4, 4, fill=NEG, stroke=NEG, sw=1))
        f.append(text(gx + 32, yy, g, size=11, color=INK, anchor="start"))

    # блок стану-завмеру (тримає пам'ять)
    sx, sy, sw_, sh = 152, 286, 196, 150
    f.append(rect(sx, sy, sw_, sh, fill="#fdf7ee", stroke=GOLD, sw=1.8))
    f.append(text(sx + sw_ / 2, sy + 22, "детектор завмеру", size=12.5, color=GOLD, bold=True))
    f.append(text(sx + sw_ / 2, sy + 38, "(тримає опору й лічильник)", size=9, color=MUTED, italic=True))
    f.append(text(sx + sw_ / 2, sy + 66, "|x − ref| < eps ?", size=11.5, color=INK))
    f.append(text(sx + sw_ / 2, sy + 90, "still++  →  still ≥ limit", size=11, color=INK))
    f.append(text(sx + sw_ / 2, sy + 118, "(eps > власного шуму)", size=10, color=MUTED, italic=True))

    f.append(arrow(116, 232, 152, 168, color=INK, sw=2))
    f.append(arrow(116, 232, 152, 360, color=INK, sw=2))

    # зведення «погано/добре» → лічильник довіри
    cx, cy, cw, ch = 388, 150, 150, 168
    f.append(rect(cx, cy, cw, ch, fill="#f6f0fb", stroke=MED, sw=1.8))
    f.append(text(cx + cw / 2, cy + 22, "лічильник", size=12.5, color=MED, bold=True))
    f.append(text(cx + cw / 2, cy + 40, "довіри", size=12.5, color=MED, bold=True))
    f.append(text(cx + cw / 2, cy + 70, "будь-яке «ні»", size=10.5, color=POS))
    f.append(text(cx + cw / 2, cy + 88, "→ bad++", size=11, color=POS, bold=True))
    f.append(text(cx + cw / 2, cy + 116, "«так»", size=10.5, color=FIELD))
    f.append(text(cx + cw / 2, cy + 134, "→ good++", size=11, color=FIELD, bold=True))
    f.append(arrow(gx + gw, gy + gh / 2, cx, cy + 60, color=POS, sw=1.6))
    f.append(arrow(sx + sw_, sy + 40, cx, cy + 60, color=POS, sw=1.6))
    f.append(arrow(gx + gw, gy + gh / 2, cx, cy + 120, color=FIELD, sw=1.6))

    # гістерезис → прапор
    hx, hy, hw, hh = 578, 150, 168, 168
    f.append(rect(hx, hy, hw, hh, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(hx + hw / 2, hy + 22, "гістерезис", size=12.5, bold=True))
    f.append(text(hx + hw / 2, hy + 48, "TRUST", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(text(hx + hw / 2, hy + 66, "bad ≥ TRIP", size=10.5, color=POS))
    f.append(arrow(hx + hw / 2, hy + 74, hx + hw / 2, hy + 98, color=POS, sw=1.8))
    f.append(text(hx + hw / 2, hy + 116, "FAULT", size=11, color=POS, bold=True))
    f.append(text(hx + hw / 2, hy + 134, "good ≥ HEAL", size=10.5, color=FIELD))
    f.append(arrow(hx + hw / 2 + 40, hy + 120, hx + hw / 2 + 40, hy + 70, color=FIELD, sw=1.8))
    f.append(arrow(cx + cw, cy + ch / 2, hx, hy + hh / 2, color=INK, sw=2))

    # вихід: is_valid()
    f.append(rect(776, 196, 92, 76, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(822, 220, "is_valid()", size=11.5, color=FIELD, bold=True))
    f.append(text(822, 240, "+ режим", size=10, color=INK))
    f.append(text(822, 256, "+ код причини", size=9, color=MUTED, italic=True))
    f.append(arrow(hx + hw, hy + hh / 2, 776, 234, color=FIELD, sw=2))

    f.append(text(W / 2, 460,
                  "одна структура стану, один виклик на відлік — і той самий код під будь-який давач",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "module-anatomy.svg"), W, H, *f)


# ── 6. Два пороги довіри: гістерезис «впав легко — піднявся важко» ────────────
def fig_trust_hysteresis():
    W, H = 820, 360
    f = [text(W / 2, 26, "Довіра з гістерезисом: впасти легко, піднятися важко", size=15, bold=True)]

    # два стани як дві смуги
    yT, yF = 86, 250
    f.append(rect(70, yT - 26, 680, 52, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(110, yT + 5, "TRUST — числу вірю", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(rect(70, yF - 26, 680, 52, fill="#fdf3f2", stroke=POS, sw=1.8))
    f.append(text(110, yF + 5, "FAULT — давач відкинуто", size=13, color=POS, bold=True, anchor="start"))

    # перехід вниз: дешевий поріг (підпис ЛІВОРУЧ від стрілки)
    f.append(arrow(250, yT + 26, 250, yF - 26, color=POS, sw=2.2))
    f.append(fitbox(34, yT + 40, 200, 56,
                    "bad ≥ TRIP\n(мало поганих поспіль)\nпідозра підтвердилась",
                    size=10.5, color=POS, fill=BG, stroke="none", sw=0))

    # перехід угору: дорогий поріг (підпис ПРАВОРУЧ від стрілки)
    f.append(arrow(590, yF - 26, 590, yT + 26, color=FIELD, sw=2.2))
    f.append(fitbox(606, yT + 40, 200, 56,
                    "good ≥ HEAL\n(БАГАТО добрих поспіль)\nдовіру повертаємо нехотя",
                    size=10.5, color=FIELD, fill=BG, stroke="none", sw=0))

    # підпис під смугами: чому несиметрично
    f.append(line(70, 312, 750, 312, color="#e6e6ea", sw=1.2))
    f.append(text(410, 332,
                  "TRIP мале, HEAL велике (HEAL ≫ TRIP) — щоб давач на межі справності не миготів",
                  size=11, color=INK, bold=True))
    f.append(text(W / 2, 352,
                  "симетричні пороги дали б «блимання» на самій межі; різні — стабільне рішення",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "trust-hysteresis.svg"), W, H, *f)


# ── 7. Родовід ідеї голосування: парадокс → теорія → TMR → космос → межа ─────
#     (вставка hist-tmr-voting.md)
def fig_tmr_genealogy():
    W, H = 920, 392
    f = [text(W / 2, 26, "Родовід голосування за більшістю: від парадокса до польоту", size=14.5, bold=True)]

    # горизонтальна вісь часу
    ax_y = 92
    f.append(line(40, ax_y, W - 40, ax_y, color="#cfcfd6", sw=2))
    for yr, x in (("1945", 78), ("1956", 300), ("1962", 510), ("1967", 700), ("1981", 858)):
        f.append(line(x, ax_y - 5, x, ax_y + 5, color=MUTED, sw=1.5))
        f.append(text(x, ax_y - 12, yr, size=10.5, color=MUTED, bold=True))

    def milestone(cx, who, what, gist, col):
        f.append(circle(cx, ax_y, 5, fill=col, stroke=col, sw=1))
        f.append(line(cx, ax_y + 5, cx, 120, color=col, sw=1.4, dash="2,3"))
        bw, bh = 172, 156
        x = min(max(cx - bw / 2, 8), W - 8 - bw)
        f.append(rect(x, 122, bw, bh, fill="#fcfcfd", stroke=col, sw=1.8))
        f.append(fitbox(x + 8, 132, bw - 16, 30, who, size=11.5, color=col, bold=True,
                        fill="#fcfcfd", stroke="none", sw=0))
        f.append(line(x + 12, 164, x + bw - 12, 164, color="#ededf0", sw=1.1))
        f.append(fitbox(x + 8, 166, bw - 16, 24, what, size=10.5, color=INK, bold=True,
                        fill="#fcfcfd", stroke="none", sw=0))
        f.append(fitbox(x + 8, 192, bw - 16, 82, gist, size=9.6, color=MUTED, italic=True,
                        fill="#fcfcfd", stroke="none", sw=0))

    milestone(78,  "ENIAC, 1945", "парадокс",
              "тисячі ламп, кожна\nперегоряє — машина\nстоїть через одну.\nЧи є стеля складності?", POS)
    milestone(300, "Джон фон Нейман\n1956", "теорія: це можливо",
              "мажоритарний орган\n(двоє з трьох) + поріг\nпомилки ≈ 0.0107:\nнадійне з ненадійного", NEG)
    milestone(510, "Лайонс і\nВандеркульк, 1962", "TMR на практиці",
              "рівно 3 копії + голос;\nперевірка Монте-Карло;\nсам голос — нова\nточка відмови", FIELD)
    milestone(700, "Saturn V LVDC\n1967", "у космос",
              "3 канали, голос на\n7 ступенях; ~99.6 %\nза 250 год — до Місяця", GOLD)
    milestone(858, "Space Shuttle\n1981", "межа: спільна причина",
              "4 однакові + 5-й з\nІНШОЮ програмою:\nпроти бага на всіх —\nрізнорідний резерв", MED)

    f.append(text(W / 2, 382,
                  "голос маскує НЕЗАЛЕЖНИЙ збій одного; проти СПІЛЬНОЇ біди рятує лише різнорідність каналів",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tmr-genealogy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_failure_modes()
    fig_quick_gates()
    fig_voting()
    fig_react_policy()
    fig_module_anatomy()
    fig_trust_hysteresis()
    fig_tmr_genealogy()
    print("OK: 7 figures ->", IMG)
