# -*- coding: utf-8 -*-
"""Фігури до теми «Похибки вимірювання відстані».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Локальні відтінки понад палітру svgkit
PURP = "#8e44ad"     # багатопроменевість / привид
GOLD = "#b9770e"     # геометрія / межі (тепле, читабельне)
GREY = "#8a8a8a"


# ── 1. Таксономія: шість родин похибок за джерелом ──────────────────────────
def fig_taxonomy():
    W, H = 720, 270
    f = [text(W / 2, 26, "Шість родин похибок відстані за джерелом", size=15, bold=True)]
    cells = [
        ("ціль",              "колір, м'якість, скло",  POS,  21,  52),
        ("геометрія",         "кут, конус, межі",       GOLD, 251, 52),
        ("середовище",        "температура, туман",     FIELD, 481, 52),
        ("засвітка / завади", "сонце, чужі пінги",      NEG,  21,  152),
        ("багатопроменевість", "привиди манівцем",      PURP, 251, 152),
        ("електроніка",       "поріг, годинник",        INK,  481, 152),
    ]
    for name, note, col, x, y in cells:
        f.append(rect(x, y, 218, 84, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + 109, y + 32, name, size=13, color=col, bold=True))
        f.append(text(x + 109, y + 56, note, size=11, color=INK, italic=True))
    render(os.path.join(IMG, "taxonomy.svg"), W, H, *f)


# ── 2. Пастки геометрії: конус чує найближче; похиле відбиває вбік ───────────
def fig_cone_trap():
    W, H = 700, 280
    f = [text(W / 2, 26, "Пастки геометрії: конус чує найближче, похиле відбиває вбік",
              size=13, bold=True)]

    # ліва панель — дрібничка затуляє стіну
    f.append(rect(24, 48, 330, 210, fill="#fbf7ee", stroke=GOLD, sw=1.4))
    f.append(text(189, 70, "дрібничка затуляє стіну", size=12, color=GOLD, bold=True))
    # давач
    f.append(rect(49, 140, 22, 40, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(line(53, 160, 67, 160, color=FIELD, sw=1.2))
    # конус (дві межі + дуга)
    f.append(line(76, 160, 335, 234, color=FIELD, sw=1.2, dash="5,4"))
    f.append(line(76, 160, 335, 86, color=FIELD, sw=1.2, dash="5,4"))
    f.append('<path d="M 335,86 A 270,270 0 0 1 335,234" fill="none" stroke="%s" '
             'stroke-width="1.2" stroke-dasharray="5,4"/>' % FIELD)
    # дрібний предмет
    f.append(rect(170, 145, 12, 30, fill="#eeeeee", stroke=POS, sw=1.5, rx=0))
    f.append(text(176, 138, "дрібне", size=9, color=POS, bold=True))
    # справжня стіна
    f.append(rect(330, 100, 12, 120, fill="#cfd6de", stroke=INK, sw=1.5, rx=0))
    f.append(text(330, 234, "справжня стіна", size=9.5, color=INK, bold=True))
    # стрілка виміру до дрібного
    f.append(arrow(168, 168, 84, 168, color=POS, sw=1.6))
    f.append(text(189, 250, "чує дрібне, «не бачить» стіни", size=9.5, color=INK, italic=True))

    # права панель — похила поверхня
    f.append(rect(366, 48, 330, 210, fill="#fbf2f1", stroke=POS, sw=1.4))
    f.append(text(531, 70, "похила поверхня", size=12, color=POS, bold=True))
    f.append(rect(399, 130, 22, 40, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(line(403, 150, 417, 150, color=FIELD, sw=1.2))
    f.append('<polygon points="560,100 600,120 575,210 535,190" fill="#cfd6de" '
             'stroke="%s" stroke-width="1.2"/>' % INK)
    f.append(arrow(426, 140, 556, 140, color=FIELD, sw=1.8))
    f.append(arrow(566, 132, 660, 90, color=POS, sw=1.8))
    f.append(text(531, 234, "промінь відбився вбік → промах", size=9.5, color=INK, italic=True))
    render(os.path.join(IMG, "cone-trap.svg"), W, H, *f)


# ── 3. Багатопроменевість: відлуння манівцем читається дальшим ──────────────
def fig_multipath():
    W, H = 700, 290
    f = [text(W / 2, 26, "Багатопроменевість: відлуння манівцем читається дальшим",
              size=14, bold=True)]
    # давач
    f.append(rect(59, 90, 22, 40, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(line(63, 110, 77, 110, color=FIELD, sw=1.2))
    # ціль
    f.append(rect(540, 70, 14, 90, fill="#eeeeee", stroke=INK, sw=1.5, rx=0))
    f.append(text(547, 178, "ціль (1.0 м)", size=10, color=INK, bold=True))
    # прямий шлях
    f.append(line(86, 100, 534, 100, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(300, 90, "прямий (слабкий / закритий)", size=9.5, color=FIELD, italic=True))
    # підлога
    f.append(line(40, 230, 660, 230, color=GREY, sw=4))
    f.append(text(80, 248, "підлога", size=9.5, color=GREY, italic=True))
    # манівець
    f.append(line(86, 128, 330, 226, color=PURP, sw=2))
    f.append(line(330, 226, 536, 130, color=PURP, sw=2))
    f.append(text(330, 210, "манівець (довший)", size=10, color=PURP, bold=True))
    f.append(text(W / 2, 274, "довший шлях → давач читає 1.3 м (привид, завжди дальший)",
                  size=12, color=PURP, bold=True))
    render(os.path.join(IMG, "multipath.svg"), W, H, *f)


# ── 4. «Прогулянка» порога: слабке відлуння перетинає поріг пізніше ──────────
def fig_threshold_walk():
    W, H = 660, 300
    f = [text(W / 2, 26, "«Прогулянка» порога: слабке відлуння перетинає поріг пізніше",
              size=13, bold=True)]
    # осі
    f.append(arrow(90, 250, 90, 48, color=INK, sw=1.6))
    f.append(arrow(90, 250, 582, 250, color=INK, sw=1.6))
    f.append(text(82, 56, "амплітуда", size=11, color=INK, anchor="end", bold=True))
    f.append(text(560, 268, "час →", size=11, color=INK, bold=True))
    # поріг
    f.append(line(90, 165, 568, 165, color=POS, sw=1.6, dash="6,4"))
    f.append(text(566, 158, "поріг", size=10, color=POS, anchor="end", bold=True))

    base, top_s, top_w = 250.0, 75.0, 145.0
    # сильне відлуння: круте наростання до плато
    rise_s = 20
    pts_s = []
    for i in range(31):
        x = 90 + 16 * i
        y = base - (base - top_s) * min(1.0, i / rise_s)
        pts_s.append((x, y))
    poly_s = " ".join("%.1f,%.1f" % p for p in pts_s)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly_s, FIELD))
    # слабке відлуння: пологе наростання до нижчого плато
    rise_w = 27
    pts_w = []
    for i in range(31):
        x = 90 + 16 * i
        y = base - (base - top_w) * min(1.0, i / rise_w)
        pts_w.append((x, y))
    poly_w = " ".join("%.1f,%.1f" % p for p in pts_w)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly_w, NEG))
    f.append(text(378, 88, "сильне", size=10, color=FIELD, anchor="start", bold=True))
    f.append(text(436, 155, "слабке", size=10, color=NEG, anchor="start", bold=True))

    # точки перетину порога
    def cross_x(rise, top):
        # лінійне наростання base→top за rise кроків; поріг y=165
        frac = (base - 165.0) / (base - top)
        return 90 + 16 * (frac * rise)
    xs, xw = cross_x(rise_s, top_s), cross_x(rise_w, top_w)
    f.append(circle(xs, 165, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(circle(xw, 165, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(line(xs, 250, xs, 165, color=FIELD, sw=1, dash="2,2"))
    f.append(line(xw, 250, xw, 165, color=NEG, sw=1, dash="2,2"))
    f.append(text(W / 2, 288,
                  "слабке засікається пізніше → читається дальшим (відбивність лізе у відстань)",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(IMG, "threshold-walk.svg"), W, H, *f)


# ── 5. Класифікуй, тоді лікуй: три кошики похибок ───────────────────────────
def fig_classes():
    W, H = 720, 240
    f = [text(W / 2, 26, "Класифікуй, тоді лікуй: три кошики похибок", size=15, bold=True)]
    cols = [
        ("систематичне", "зсув, прогулянка, нелінійність", "калібрування / компенсація", POS,  16),
        ("випадкове",    "шум, тремтіння",                 "усереднення / фільтр",       NEG,  248),
        ("грубий викид", "привид, пропуск, стрибок",       "відсів (медіана, межі)",     PURP, 480),
    ]
    for name, what, cure, col, x in cols:
        f.append(rect(x, 52, 224, 160, fill=FILL, stroke=col, sw=1.5))
        f.append(text(x + 112, 80, name, size=13.5, color=col, bold=True))
        f.append(text(x + 112, 116, what, size=11, color=INK, italic=True))
        f.append(line(x + 20, 136, x + 204, 136, color="#e4e4e4", sw=1))
        f.append(text(x + 112, 160, "лік:", size=10.5, color=GREY, bold=True))
        f.append(text(x + 112, 180, cure, size=11, color=col, bold=True))
    render(os.path.join(IMG, "classes.svg"), W, H, *f)


# ── 6. Чотири щити надійного далекоміра ─────────────────────────────────────
def fig_mitigations():
    W, H = 720, 260
    f = [text(W / 2, 26, "Чотири щити надійного далекоміра", size=15, bold=True)]

    # щит 1: медіана — крива з піком і крива без піка
    x = 14
    f.append(rect(x, 52, 166, 188, fill=FILL, stroke=FIELD, sw=1.4))
    f.append(text(x + 83, 76, "медіана", size=11.5, color=FIELD, bold=True))
    raw = [(30, 162), (50, 158), (70, 164), (90, 188), (110, 160), (130, 165), (150, 159)]
    out = [(30, 162), (50, 158), (70, 164), (90, 166), (110, 160), (130, 165), (150, 159)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%d,%d" % p for p in raw), GREY))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%d,%d" % p for p in out), FIELD))
    f.append(text(90, 140, "пік прибрано", size=9, color=FIELD, bold=True))
    f.append(text(x + 83, 228, "вбиває викиди", size=9.5, color=INK, italic=True))

    # щит 2: межі здорового глузду
    x = 190
    f.append(rect(x, 52, 166, 188, fill=FILL, stroke=GOLD, sw=1.4))
    f.append(text(x + 83, 76, "межі здорового глузду", size=11.5, color=GOLD, bold=True))
    f.append(line(x + 20, 162, x + 70, 156, color=FIELD, sw=2))
    f.append(arrow(x + 70, 156, x + 130, 110, color=POS, sw=1.8))
    f.append(text(x + 110, 132, "✗ стрибок", size=9, color=POS, bold=True))
    f.append(text(x + 83, 228, "відсіює неможливе", size=9.5, color=INK, italic=True))

    # щит 3: довіра за сигналом — сильна (велика амплітуда) vs кволa
    x = 366
    f.append(rect(x, 52, 166, 188, fill=FILL, stroke=NEG, sw=1.4))
    f.append(text(x + 83, 76, "довіра за сигналом", size=11.5, color=NEG, bold=True))
    big, small = [], []
    for i in range(33):
        xx = x + 18 + i * 1.9
        big.append((xx, 158 - 14 * math.sin(i * 0.9)))
        small.append((xx + 72, 158 - 4 * math.sin(i * 0.9)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%.1f,%.1f" % p for p in big), FIELD))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%.1f,%.1f" % p for p in small), POS))
    f.append(text(x + 48, 196, "сильне ✓", size=9, color=FIELD))
    f.append(text(x + 120, 196, "кволе ✗", size=9, color=POS))
    f.append(text(x + 83, 228, "кволе = не вірю", size=9.5, color=INK, italic=True))

    # щит 4: поєднання давачів
    x = 542
    f.append(rect(x, 52, 166, 188, fill=FILL, stroke=PURP, sw=1.4))
    f.append(text(x + 83, 76, "поєднання", size=11.5, color=PURP, bold=True))
    f.append(rect(x + 32, 141, 16, 26, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(line(x + 36, 154, x + 44, 154, color=FIELD, sw=1.2))
    f.append(rect(x + 101, 142, 18, 24, fill="#fbf2f1", stroke=POS, sw=1.6))
    f.append('<polygon points="%d,149 %d,154 %d,159" fill="%s"/>'
             % (x + 119, x + 129, x + 119, POS))
    f.append(arrow(x + 50, 178, x + 100, 178, color=INK, sw=1.4))
    f.append(text(x + 83, 198, "звук + оптика", size=9, color=INK))
    f.append(text(x + 83, 228, "давачі прикривають", size=9.5, color=INK, italic=True))
    render(os.path.join(IMG, "mitigations.svg"), W, H, *f)


# ── 7. Похибка → причина → лік: шпаргалка ───────────────────────────────────
def fig_table():
    W, H = 700, 300
    f = [text(W / 2, 26, "Похибка → причина → лік (шпаргалка)", size=15, bold=True)]
    # шапка
    f.append(rect(24, 48, 676, 36, fill="#eef1f6", stroke=GREY, sw=1, rx=0))
    f.append(text(34, 71, "похибка", size=12, color=INK, anchor="start", bold=True))
    f.append(text(234, 71, "причина", size=12, color=INK, anchor="start", bold=True))
    f.append(text(464, 71, "лік", size=12, color=INK, anchor="start", bold=True))

    rows = [
        ("«не бачить» цілі", "м'яка / похила / прозора",    "інша фізика, ретрорефлектор", POS),
        ("показ дальший",    "привид (багатопроменевість)", "медіана, межі, вузький промінь", PURP),
        ("темне = дальше",   "прогулянка порога",           "поправка за амплітудою",       POS),
        ("повзе з теплом",   "швидкість звуку (T)",         "термокомпенсація",             FIELD),
        ("сліпне на сонці",  "ІЧ-засвітка",                 "модуляція, фільтр, віднімання", NEG),
        ("дикий стрибок",    "збій / викид",                "перевірка на здоровий глузд",  GOLD),
    ]
    y = 84
    for err, cause, cure, col in rows:
        f.append(rect(24, y, 676, 36, fill=BG, stroke=GREY, sw=0.8, rx=0))
        f.append(text(34, y + 23, err, size=11, color=col, anchor="start", bold=True))
        f.append(text(234, y + 23, cause, size=10.5, color=INK, anchor="start"))
        f.append(text(464, y + 23, cure, size=10.5, color=INK, anchor="start"))
        y += 36
    render(os.path.join(IMG, "table.svg"), W, H, *f)


if __name__ == "__main__":
    fig_taxonomy()
    fig_cone_trap()
    fig_multipath()
    fig_threshold_walk()
    fig_classes()
    fig_mitigations()
    fig_table()
    print("OK: 7 figures ->", IMG)
