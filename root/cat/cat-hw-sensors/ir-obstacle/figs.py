# -*- coding: utf-8 -*-
"""Фігури для статті «IR-давачі перешкод (FC-51 / KY-032)». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_reflect():
    """Принцип відбиття: діод світить ІЧ, перешкода відбиває, приймач ловить.
       Дві сцени поруч: є перешкода (промінь вертається) / немає (промінь гине)."""
    W, H = 820, 400
    p = []
    p.append(text(W / 2, 30, "Як давач «бачить» перешкоду: власне ІЧ-світло, що відбилось назад",
                  size=17, bold=True))

    # --- сцена А: Є перешкода ---
    ax = 40
    p.append(text(ax + 160, 66, "Є перешкода поруч", size=14, bold=True, color=FIELD))
    # плата давача (ліворуч)
    p.append(rect(ax, 110, 60, 170, fill="#123", stroke=INK, sw=2, rx=6))
    # ІЧ-діод (верхнє око) і приймач (нижнє око)
    p.append(circle(ax + 60, 150, 13, fill="#7a1f14", stroke=POS, sw=2))
    p.append(text(ax + 60, 154, "ІЧ", size=10, color="#fff", bold=True))
    p.append(circle(ax + 60, 240, 13, fill="#12303a", stroke=NEG, sw=2))
    p.append(text(ax + 60, 244, "пр", size=10, color="#fff", bold=True))
    # перешкода (стіна праворуч)
    wallx = ax + 300
    p.append(rect(wallx, 90, 22, 210, fill="#b8860b", stroke=INK, sw=2, rx=3))
    p.append(text(wallx + 11, 320, "перешкода", size=11, color=INK))
    # промінь туди (діод -> стіна)
    p.append(arrow(ax + 74, 150, wallx - 4, 150, color=POS, sw=2.4))
    # промінь назад (стіна -> приймач), відбитий
    p.append(arrow(wallx - 4, 200, ax + 74, 240, color=FIELD, sw=2.4))
    p.append(text(ax + 175, 138, "світить", size=11, color=POS))
    p.append(text(ax + 168, 232, "відбилось назад", size=11, color=FIELD))
    tb, tw, th = textbox(ax + 150, 350, "приймач ловить → вихід «є перешкода»",
                         size=12, color=INK, fill="#eafaf0")
    p.append(tb)

    # роздільник
    p.append(line(W / 2, 60, W / 2, 360, color=MUTED, sw=1, dash="4 5"))

    # --- сцена Б: Немає перешкоди ---
    bx = W / 2 + 40
    p.append(text(bx + 150, 66, "Нічого поруч немає", size=14, bold=True, color=MUTED))
    p.append(rect(bx, 110, 60, 170, fill="#123", stroke=INK, sw=2, rx=6))
    p.append(circle(bx + 60, 150, 13, fill="#7a1f14", stroke=POS, sw=2))
    p.append(text(bx + 60, 154, "ІЧ", size=10, color="#fff", bold=True))
    p.append(circle(bx + 60, 240, 13, fill="#12303a", stroke=NEG, sw=2))
    p.append(text(bx + 60, 244, "пр", size=10, color="#fff", bold=True))
    # промінь іде в порожнечу й гасне
    p.append(line(bx + 74, 150, bx + 260, 150, color=POS, sw=2.4, dash="7 6"))
    p.append(text(bx + 175, 138, "світить у порожнечу", size=11, color=POS))
    p.append(text(bx + 250, 205, "нема чому", size=11, color=MUTED))
    p.append(text(bx + 250, 222, "відбити", size=11, color=MUTED))
    tb, tw, th = textbox(bx + 150, 350, "приймач мовчить → вихід «вільно»",
                         size=12, color=INK, fill="#f2f3f5")
    p.append(tb)

    render(os.path.join(IMG, 'reflect.svg'), W, H, *p)


def fig_modulation():
    """Чому KY-032 не боїться сонця, а FC-51 боїться: постійне світло vs 38 кГц несуча.
       Дві доріжки — сигнал на приймачі й що з ним робить кожна схема."""
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 28, "Постійний промінь (FC-51) плутається із сонцем; мерехтіння 38 кГц (KY-032) — ні",
                  size=16, bold=True))

    def wave_const(x0, y0, w, level, color):
        # рівна лінія на висоті level (0..1 знизу)
        y = y0 - level * 46
        return line(x0, y, x0 + w, y, color=color, sw=2.6)

    def wave_square(x0, y0, w, color, n=9, hi=0.9, lo=0.12):
        # прямокутна «гребінка» — модульоване світло
        seg = w / (2 * n)
        segs = []
        x = x0
        yhi = y0 - hi * 46
        ylo = y0 - lo * 46
        cy = ylo
        for i in range(2 * n):
            ny = yhi if (i % 2 == 0) else ylo
            segs.append(line(x, cy, x, ny, color=color, sw=2.2))  # вертикаль
            segs.append(line(x, ny, x + seg, ny, color=color, sw=2.2))  # горизонталь
            cy = ny
            x += seg
        return segs

    # ---- Рядок 1: FC-51 (постійне світло) ----
    r1 = 120
    p.append(text(70, r1 - 74, "FC-51: давач світить РІВНО", size=14, bold=True, color=POS))
    # ось
    p.append(line(70, r1, 430, r1, color=MUTED, sw=1))
    # власне світло давача — рівна лінія
    p.append(wave_const(80, r1, 150, 0.55, POS))
    p.append(text(150, r1 - 60, "своє світло (рівне)", size=11, color=POS))
    # сонце додається — теж рівна, зверху
    p.append(wave_const(80, r1, 340, 0.9, "#e8a13a"))
    p.append(text(340, r1 - 52, "+ сонце (теж рівне)", size=11, color="#c07800"))
    # висновок
    tb, tw, th = textbox(600, r1 - 10, "приймач бачить один рівний рівень —\nвогонь-сонце й перешкоду НЕ розрізнити",
                         size=12, color=INK, fill="#fdecea")
    p.append(tb)

    # роздільна риса
    p.append(line(60, 235, W - 40, 235, color=MUTED, sw=1, dash="3 4"))

    # ---- Рядок 2: KY-032 (38 кГц несуча) ----
    r2 = 350
    p.append(text(70, r2 - 74, "KY-032: давач БЛИМАЄ 38 000 разів/с", size=14, bold=True, color=NEG))
    p.append(line(70, r2, 430, r2, color=MUTED, sw=1))
    for s in wave_square(80, r2, 300, NEG):
        p.append(s)
    p.append(text(175, r2 - 60, "своє світло (мерехтить 38 кГц)", size=11, color=NEG))
    # сонце — рівний фон під гребінкою
    p.append(wave_const(80, r2, 300, 0.12, "#e8a13a"))
    p.append(text(210, r2 + 24, "сонце — рівний фон", size=11, color="#c07800"))
    tb, tw, th = textbox(600, r2 - 10, "приймач шукає САМЕ 38 кГц —\nрівне сонце відкидає, ловить лише відбите мерехтіння",
                         size=12, color=INK, fill="#eafaf0")
    p.append(tb)

    render(os.path.join(IMG, 'modulation.svg'), W, H, *p)


def fig_wiring():
    """Розводка пін-у-пін: FC-51 (3 піни) і KY-032 (4 піни з EN) до плати."""
    W, H = 960, 470
    p = []
    p.append(text(W / 2, 28, "Підключення до плати: FC-51 (3 піни) і KY-032 (4 піни з EN)",
                  size=16, bold=True))

    def board(x, y, w, h, label):
        out = [rect(x, y, w, h, fill="#0f2a3a", stroke=INK, sw=2, rx=8)]
        out.append(text(x + w / 2, y + h / 2, label, size=13, color="#dfeaf2", bold=True))
        return out

    def pin(x, y, name, color):
        return [circle(x, y, 8, fill=color, stroke=INK, sw=1.5),
                text(x, y + 4, "", size=1)]

    # ---- ліворуч: FC-51 ----
    fx = 60
    p.append(text(fx + 90, 66, "FC-51 — 3 піни", size=14, bold=True, color=POS))
    for f in board(fx, 90, 180, 120, "FC-51"):
        p.append(f)
    # піни виходять праворуч від модуля
    py = [120, 150, 180]
    names = [("VCC", "3.3–5 В", "#c0392b"), ("GND", "земля", "#333"), ("OUT", "цифра → D2", "#2457d6")]
    for yy, (nm, note, col) in zip(py, names):
        p.append(circle(fx + 180, yy, 8, fill=col, stroke=INK, sw=1.5))
        p.append(text(fx + 150, yy - 12, nm, size=12, bold=True, anchor="end", color=INK))
    # плата-приймач (МК)
    mcux = fx + 300
    for f in board(mcux, 90, 120, 200, "плата\n(МК)"):
        pass
    p.append(rect(mcux, 90, 120, 200, fill="#123", stroke=INK, sw=2, rx=8))
    p.append(text(mcux + 60, 110, "плата (МК)", size=12, color="#dfeaf2", bold=True))
    # цільові піни
    tgt = [("5V", 140, "#c0392b"), ("GND", 175, "#333"), ("D2", 210, "#2457d6")]
    for nm, yy, col in tgt:
        p.append(circle(mcux, yy, 8, fill=col, stroke=INK, sw=1.5))
        p.append(text(mcux + 22, yy + 4, nm, size=11, anchor="start", color="#dfeaf2"))
    # дроти FC-51 -> плата
    wires = [(120, 140, "#c0392b"), (150, 175, "#333"), (180, 210, "#2457d6")]
    for sy, ty, col in wires:
        p.append(line(fx + 188, sy, mcux - 8, ty, color=col, sw=2.4))
    tb, tw, th = textbox(fx + 150, 340, "OUT = «0» коли перешкода є (активний нуль).\nЖивлення — під логіку плати.",
                         size=11, color=INK, fill="#fdecea")
    p.append(tb)

    # роздільник
    p.append(line(W / 2, 60, W / 2, 430, color=MUTED, sw=1, dash="4 5"))

    # ---- праворуч: KY-032 ----
    kx = W / 2 + 40
    p.append(text(kx + 90, 66, "KY-032 — 4 піни (+EN)", size=14, bold=True, color=NEG))
    p.append(rect(kx, 90, 180, 140, fill="#0f2a3a", stroke=INK, sw=2, rx=8))
    p.append(text(kx + 90, 150, "KY-032", size=13, color="#dfeaf2", bold=True))
    kpy = [110, 140, 170, 200]
    knm = [("EN", "вмик. (джампер=HIGH)", "#27ae60"),
           ("OUT", "цифра → D2", "#2457d6"),
           ("+", "3.3–5 В", "#c0392b"),
           ("GND", "земля", "#333")]
    for yy, (nm, note, col) in zip(kpy, knm):
        p.append(circle(kx + 180, yy, 8, fill=col, stroke=INK, sw=1.5))
        p.append(text(kx + 150, yy - 11, nm, size=12, bold=True, anchor="end", color=INK))
    # плата МК
    kmcux = kx + 300
    p.append(rect(kmcux, 90, 120, 220, fill="#123", stroke=INK, sw=2, rx=8))
    p.append(text(kmcux + 60, 110, "плата (МК)", size=12, color="#dfeaf2", bold=True))
    ktgt = [("3V3/5V", 130, "#27ae60"), ("D2", 165, "#2457d6"), ("VCC", 200, "#c0392b"), ("GND", 235, "#333")]
    # EN на HIGH (тут — на живлення джампером), OUT->D2, +->VCC, GND->GND
    for nm, yy, col in ktgt:
        p.append(circle(kmcux, yy, 8, fill=col, stroke=INK, sw=1.5))
        p.append(text(kmcux + 22, yy + 4, nm, size=11, anchor="start", color="#dfeaf2"))
    kwires = [(110, 130, "#27ae60"), (140, 165, "#2457d6"), (170, 200, "#c0392b"), (200, 235, "#333")]
    for sy, ty, col in kwires:
        p.append(line(kx + 188, sy, kmcux - 8, ty, color=col, sw=2.4))
    tb, tw, th = textbox(kx + 150, 370, "EN на HIGH (джампер) — модуль увімкнено.\nOUT = «0» коли перешкода є.",
                         size=11, color=INK, fill="#eafaf0")
    p.append(tb)

    render(os.path.join(IMG, 'wiring.svg'), W, H, *p)


if __name__ == '__main__':
    fig_reflect()
    fig_modulation()
    fig_wiring()
    print("OK: reflect.svg, modulation.svg, wiring.svg")
