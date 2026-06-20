# -*- coding: utf-8 -*-
"""Фігури до статті «Умовні позначення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Спільне для всіх фігур ─────────────────────────────────────────────────
CARD_FILL = "#f6f8fc"
CARD_STK  = "#dcdcdc"
WIRE_SW   = 2.0


def card(x, y, w, h):
    """Світла картка-комірка під один символ."""
    return rect(x, y, w, h, fill=CARD_FILL, stroke=CARD_STK, sw=1.4, rx=8)


def wire(x1, y1, x2, y2, sw=WIRE_SW):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, INK, sw))


def lbl(cx, y, s):
    """Підпис символу під коміркою."""
    return text(cx, y, s, size=12, color=INK, bold=True)


# ── Примітиви-символи (центр символу — cy; вивід ліворуч lx, праворуч rx) ───
def sym_resistor_iec(cx, cy):
    bw, bh = 44, 18
    x = cx - bw / 2
    return (wire(x - 18, cy, x, cy) +
            rect(x, cy - bh / 2, bw, bh, fill=BG, stroke=INK, sw=2, rx=2) +
            wire(x + bw, cy, x + bw + 18, cy))


def sym_resistor_ansi(cx, cy):
    half = 24
    x0 = cx - half
    pts = [(x0, cy)]
    zig = [(6, -9), (12, 9), (18, -9), (24, 9), (30, -9), (36, 9), (40, 0)]
    for dx, dy in zig:
        pts.append((x0 + dx, cy + dy))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return (wire(x0 - 18, cy, x0, cy) +
            '<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (poly, INK) +
            wire(x0 + 40, cy, x0 + 58, cy))


def sym_potentiometer(cx, cy):
    base = sym_resistor_iec(cx, cy)
    # стрілка-повзунок зверху до центру тіла резистора
    arr = arrow(cx, cy + 16, cx, cy + 2, color=INK, sw=2)
    return base + arr


def sym_capacitor(cx, cy, polar=False):
    g = 10                      # півзазор між пластинами
    plh = 24                    # висота пластини
    left = cx - g
    right = cx + g
    out = wire(cx - 30, cy, left, cy)
    out += wire(left, cy - plh / 2, left, cy + plh / 2, sw=2.4)
    if polar:
        # друга пластина зігнута + позначка «+»
        out += ('<path d="M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="2.4"/>'
                % (right, cy - plh / 2, right - 6, cy, right, cy + plh / 2, INK))
        out += text(left - 4, cy - plh / 2 - 3, "+", size=13, color=POS, bold=True)
    else:
        out += wire(right, cy - plh / 2, right, cy + plh / 2, sw=2.4)
    out += wire(right, cy, cx + 30, cy)
    return out


def sym_inductor(cx, cy):
    n = 4
    arc_w = 9
    x0 = cx - n * arc_w / 2
    out = wire(x0 - 12, cy, x0, cy)
    for i in range(n):
        ax = x0 + i * arc_w
        out += ('<path d="M %.1f,%.1f q %.1f,-%.1f %.1f,0" fill="none" '
                'stroke="%s" stroke-width="2"/>'
                % (ax, cy, arc_w / 2, arc_w, arc_w, INK))
    out += wire(x0 + n * arc_w, cy, x0 + n * arc_w + 12, cy)
    return out


def sym_diode(cx, cy, kind="diode"):
    tw = 18                     # ширина трикутника
    x = cx - tw / 2
    out = wire(x - 22, cy, x, cy)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
            'stroke="%s" stroke-width="2"/>'
            % (x, cy - 11, x, cy + 11, x + tw, cy, BG, INK))
    if kind == "zener":
        # катод із загнутими кінцями
        out += ('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                'fill="none" stroke="%s" stroke-width="2.4"/>'
                % (x + tw - 6, cy - 14, x + tw, cy - 11, x + tw, cy + 11,
                   x + tw + 6, cy + 14, INK))
    else:
        out += wire(x + tw, cy - 11, x + tw, cy + 11, sw=2.6)
    out += wire(x + tw, cy, cx + 22, cy)
    if kind == "led":
        # дві стрілочки світла назовні
        out += arrow(x + tw - 2, cy - 12, x + tw + 4, cy - 19, color=POS, sw=1.6)
        out += arrow(x + tw + 5, cy - 11, x + tw + 11, cy - 18, color=POS, sw=1.6)
    return out


def sym_bjt(cx, cy, npn=True):
    r = 16
    out = circle(cx, cy, r, fill=BG, stroke=INK, sw=1.8)
    bx = cx - 8                 # вертикальна риска бази
    out += wire(cx - r - 8, cy, bx, cy)             # вивід бази
    out += wire(bx, cy - 9, bx, cy + 9, sw=2.6)     # риска бази
    # колектор (вгору) і емітер (вниз)
    out += wire(bx, cy - 4, cx + 9, cy - 8)
    out += wire(cx + 9, cy - 8, cx + 9, cy - r - 4)
    out += wire(bx, cy + 4, cx + 9, cy + 8)
    out += wire(cx + 9, cy + 8, cx + 9, cy + r + 4)
    # стрілка на емітері: NPN — назовні, PNP — до бази
    if npn:
        out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                % (cx + 3, cy + 6, cx + 9, cy + 12, cx + 1, cy + 13, INK))
    else:
        out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                % (bx, cy + 4, cx + 1, cy + 3, cx, cy + 11, INK))
    return out


def sym_mosfet(cx, cy):
    r = 16
    gx = cx - 11                # затвор
    chx = cx - 4                # канал
    out = wire(cx - r - 6, cy, gx, cy)
    out += wire(gx, cy - 13, gx, cy + 13, sw=2.0)        # пластина затвора
    out += wire(chx, cy - 13, chx, cy + 13, sw=2.6)      # канал
    out += wire(chx, cy - 9, cx + 13, cy - 9)            # стік
    out += wire(cx + 13, cy - 9, cx + 13, cy - r - 4)
    out += wire(chx, cy + 9, cx + 13, cy + 9)            # витік
    out += wire(cx + 13, cy + 9, cx + 13, cy + r + 4)
    out += arrow(chx, cy, cx + 6, cy, color=INK, sw=1.6)  # стрілка каналу
    return out


def sym_cell(cx, cy):
    out = wire(cx - 30, cy, cx - 4, cy)
    out += wire(cx - 4, cy - 13, cx - 4, cy + 13)         # довга «+»
    out += wire(cx + 4, cy - 7, cx + 4, cy + 7, sw=4)     # коротка «−»
    out += wire(cx + 4, cy, cx + 30, cy)
    out += text(cx - 10, cy - 16, "+", size=11, color=POS, bold=True)
    return out


def sym_battery(cx, cy):
    out = wire(cx - 34, cy, cx - 16, cy)
    xs = [(-16, 13, 2), (-9, 7, 4), (-1, 13, 2), (6, 7, 4)]
    for dx, hh, sw in xs:
        out += wire(cx + dx, cy - hh, cx + dx, cy + hh, sw=sw)
    out += wire(cx + 6, cy, cx + 34, cy)
    out += text(cx - 22, cy - 16, "+", size=11, color=POS, bold=True)
    return out


def sym_source(cx, cy, kind="dc"):
    r = 15
    out = circle(cx, cy, r, fill=BG, stroke=INK, sw=2)
    out += wire(cx - r - 16, cy, cx - r, cy)
    out += wire(cx + r, cy, cx + r + 16, cy)
    if kind == "dc":
        out += wire(cx - 8, cy - 3, cx + 8, cy - 3)
        out += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="1.2" stroke-dasharray="3,2"/>'
                % (cx - 8, cy + 3, cx + 8, cy + 3, INK))
    elif kind == "ac":
        out += ('<path d="M %.1f,%.1f q 4.5,-9 9,0 q 4.5,9 9,0" fill="none" '
                'stroke="%s" stroke-width="2"/>' % (cx - 9, cy, INK))
    elif kind == "current":
        out += arrow(cx, cy + 8, cx, cy - 8, color=INK, sw=2)
    return out


def sym_switch(cx, cy, kind="spst"):
    out = wire(cx - 30, cy, cx - 12, cy)
    out += circle(cx - 12, cy, 3, fill=INK, stroke=INK, sw=1)
    out += circle(cx + 12, cy, 3, fill=INK, stroke=INK, sw=1)
    out += wire(cx + 12, cy, cx + 30, cy)
    if kind == "button":
        out += wire(cx - 13, cy - 11, cx + 13, cy - 11, sw=2.2)
        out += wire(cx, cy - 11, cx, cy - 20)
    else:
        out += wire(cx - 12, cy, cx + 11, cy - 14, sw=2.2)
    return out


def sym_fuse(cx, cy):
    bw, bh = 36, 14
    out = wire(cx - 30, cy, cx - bw / 2, cy)
    out += rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=BG, stroke=INK, sw=2, rx=bh / 2)
    out += wire(cx - bw / 2, cy, cx + bw / 2, cy, sw=1.6)
    out += wire(cx + bw / 2, cy, cx + 30, cy)
    return out


def sym_relay(cx, cy):
    # котушка ліворуч + контакт праворуч, пунктир-зв'язок
    out = rect(cx - 30, cy - 12, 16, 24, fill=BG, stroke=INK, sw=1.8, rx=3)
    out += text(cx - 22, cy + 4, "L", size=11, color=INK, bold=True)
    out += wire(cx - 30, cy - 6, cx - 40, cy - 6)
    out += wire(cx - 30, cy + 6, cx - 40, cy + 6)
    out += circle(cx + 8, cy + 6, 3, fill=INK, stroke=INK, sw=1)
    out += circle(cx + 28, cy + 6, 3, fill=INK, stroke=INK, sw=1)
    out += wire(cx + 8, cy + 6, cx + 27, cy - 6, sw=2.2)
    out += wire(cx + 28, cy + 6, cx + 38, cy + 6)
    out += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="1.2" stroke-dasharray="3,3"/>'
            % (cx - 14, cy, cx + 14, cy - 2, MUTED))
    return out


def sym_ground(cx, cy):
    out = wire(cx, cy - 16, cx, cy)
    out += wire(cx - 13, cy, cx + 13, cy, sw=2.4)
    out += wire(cx - 8, cy + 5, cx + 8, cy + 5, sw=2.4)
    out += wire(cx - 3, cy + 10, cx + 3, cy + 10, sw=2.4)
    return out


def sym_lamp(cx, cy):
    r = 14
    out = circle(cx, cy, r, fill=BG, stroke=INK, sw=2)
    out += wire(cx - 10, cy - 10, cx + 10, cy + 10, sw=1.8)
    out += wire(cx - 10, cy + 10, cx + 10, cy - 10, sw=1.8)
    out += wire(cx - r - 16, cy, cx - r, cy)
    out += wire(cx + r, cy, cx + r + 16, cy)
    return out


def sym_motor(cx, cy):
    r = 15
    out = circle(cx, cy, r, fill=BG, stroke=INK, sw=2)
    out += text(cx, cy + 5, "M", size=14, color=INK, bold=True)
    out += wire(cx - r - 16, cy, cx - r, cy)
    out += wire(cx + r, cy, cx + r + 16, cy)
    return out


def sym_speaker(cx, cy):
    out = rect(cx - 16, cy - 8, 10, 16, fill=BG, stroke=INK, sw=2, rx=1)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
            'stroke="%s" stroke-width="2"/>'
            % (cx - 6, cy - 8, cx - 6, cy + 8, cx + 12, cy + 17, cx + 12, cy - 17, BG, INK))
    out += wire(cx - 30, cy, cx - 16, cy)
    return out


def sym_antenna(cx, cy):
    out = wire(cx, cy + 11, cx, cy - 11)
    out += wire(cx, cy - 11, cx - 13, cy - 24)
    out += wire(cx, cy - 11, cx + 13, cy - 24)
    return out


# ── Розкладка сітки символів ────────────────────────────────────────────────
def grid(path, title, items, cols=3, cw=233, ch=118, top=72, gap_x=12, gap_y=12,
         margin=56):
    """items: список (draw_fn, label). draw_fn(cx, cy) повертає SVG символу."""
    rows = (len(items) + cols - 1) // cols
    W = margin * 2 + cols * cw + (cols - 1) * gap_x
    H = top + rows * ch + (rows - 1) * gap_y + 30
    frags = []
    for i, (fn, label) in enumerate(items):
        r, c = divmod(i, cols)
        x = margin + c * (cw + gap_x)
        y = top + r * (ch + gap_y)
        cx = x + cw / 2
        cy = y + ch / 2 - 6
        frags.append(card(x, y, cw, ch))
        frags.append(fn(cx, cy))
        frags.append(lbl(cx, y + ch - 14, label))
    return render(path, W, H, *frags, title=title)


# ── Фігури статті ───────────────────────────────────────────────────────────
def fig_passives():
    grid(os.path.join(IMG, "passives.svg"),
         "Пасивні: форма повторює фізику",
         [(sym_resistor_iec, "Резистор (IEC)"),
          (sym_resistor_ansi, "Резистор (ANSI)"),
          (sym_potentiometer, "Потенціометр"),
          (lambda x, y: sym_capacitor(x, y, polar=False), "Конденсатор"),
          (lambda x, y: sym_capacitor(x, y, polar=True), "Електролітичний C (+)"),
          (sym_inductor, "Котушка / дросель")])


def fig_semiconductors():
    grid(os.path.join(IMG, "semiconductors.svg"),
         "Напівпровідники: трикутник пропускає в один бік",
         [(lambda x, y: sym_diode(x, y, "diode"), "Діод"),
          (lambda x, y: sym_diode(x, y, "led"), "Світлодіод"),
          (lambda x, y: sym_diode(x, y, "zener"), "Стабілітрон"),
          (lambda x, y: sym_bjt(x, y, npn=True), "Транзистор NPN"),
          (lambda x, y: sym_bjt(x, y, npn=False), "Транзистор PNP"),
          (sym_mosfet, "Польовий (MOSFET)")])


def fig_sources_switches():
    grid(os.path.join(IMG, "sources-switches.svg"),
         "Джерела й комутація",
         [(sym_cell, "Гальв. елемент"),
          (sym_battery, "Батарея"),
          (lambda x, y: sym_source(x, y, "dc"), "Джерело DC"),
          (lambda x, y: sym_source(x, y, "ac"), "Джерело AC"),
          (lambda x, y: sym_source(x, y, "current"), "Джерело струму"),
          (lambda x, y: sym_switch(x, y, "spst"), "Вимикач"),
          (lambda x, y: sym_switch(x, y, "button"), "Кнопка"),
          (sym_fuse, "Запобіжник"),
          (sym_relay, "Реле")])


def fig_ground_io():
    grid(os.path.join(IMG, "ground-io.svg"),
         "«Земля» та навантаження",
         [(sym_ground, "«Земля» (GND)"),
          (sym_lamp, "Лампа"),
          (sym_motor, "Мотор"),
          (sym_speaker, "Динамік"),
          (sym_antenna, "Антена")])


def fig_two_standards():
    W, H = 760, 300
    frags = []
    # ліва панель — резистор
    rb = rect(70, 64, 300, 168, fill="#eaf0fb", stroke=NEG, sw=1.6, rx=12)
    frags.append(rb)
    frags.append(text(220, 90, "Резистор", size=14, color=NEG, bold=True))
    frags.append(sym_resistor_iec(160, 140))
    frags.append(text(160, 178, "IEC (прямокутник)", size=11, color=MUTED))
    frags.append(sym_resistor_ansi(285, 140))
    frags.append(text(290, 178, "ANSI (зигзаг)", size=11, color=MUTED))
    frags.append(text(220, 214, "те саме — резистор", size=12, color=INK, bold=True))
    # права панель — конденсатор / полярність
    cb = rect(390, 64, 300, 168, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=12)
    frags.append(cb)
    frags.append(text(540, 90, "Конденсатор", size=14, color=FIELD, bold=True))
    frags.append(sym_capacitor(470, 140, polar=False))
    frags.append(text(470, 178, "неполярний", size=11, color=MUTED))
    frags.append(sym_capacitor(600, 140, polar=True))
    frags.append(text(606, 178, "полярний (+)", size=11, color=MUTED))
    frags.append(text(540, 214, "стежте за полярністю!", size=12, color=POS, bold=True))
    render(os.path.join(IMG, "two-standards.svg"), W, H, *frags,
           title="Два набори символів означають те саме")


if __name__ == "__main__":
    fig_passives()
    fig_semiconductors()
    fig_sources_switches()
    fig_ground_io()
    fig_two_standards()
    print("OK: фігури згенеровано у", IMG)
