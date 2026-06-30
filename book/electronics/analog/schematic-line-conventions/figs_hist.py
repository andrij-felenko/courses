# -*- coding: utf-8 -*-
"""Фігури до вставки «Звідки взялися умовні позначення на схемах» (hist).
Чистий Python, SVG через svgkit. Вивід — у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#1a1a1a"
WSW = 2.0


def dot(cx, cy, r=4.2):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, WIRE)


# ── Фігура 1: дві суперницькі домовленості про перетин ──────────────────────
# Ліворуч — СТАРА (хрест = з'єднано, горб = НЕ з'єднано).
# Праворуч — НОВА (крапка = з'єднано, голий хрест = НЕ з'єднано).
# Посередині — той самий голий хрест, що в двох системах читається ПРОТИЛЕЖНО.
def fig_two_conventions():
    W, H = 720, 360
    parts = []

    def cross(cx, cy, hop=False):
        # горизонталь
        parts.append(line(cx - 55, cy, cx + 55, cy, color=WIRE, sw=WSW))
        if hop:
            # вертикаль із горбом, що перестрибує горизонталь
            parts.append(line(cx, cy - 55, cx, cy - 8, color=WIRE, sw=WSW))
            parts.append(line(cx, cy + 8, cx, cy + 55, color=WIRE, sw=WSW))
            parts.append('<path d="M %.1f %.1f A 8 8 0 0 1 %.1f %.1f" fill="none" '
                         'stroke="%s" stroke-width="%.1f"/>'
                         % (cx, cy - 8, cx, cy + 8, WIRE, WSW))
        else:
            parts.append(line(cx, cy - 55, cx, cy + 55, color=WIRE, sw=WSW))

    # заголовки колонок
    parts.append(text(180, 38, "СТАРА школа", size=15, bold=True))
    parts.append(text(180, 58, "(до CAD)", size=12, color=MUTED))
    parts.append(text(540, 38, "СУЧАСНА (CAD)", size=15, bold=True))
    parts.append(text(540, 58, "норма стандартів", size=12, color=MUTED))

    # вертикальний роздільник
    parts.append(line(360, 75, 360, 330, color="#dddddd", sw=1))

    yA, yB = 145, 270

    # — стара: верх = хрест-з'єднано, низ = горб-не-з'єднано
    cross(120, yA, hop=False)
    parts.append(text(120, yA + 78, "хрест = З'ЄДНАНО", size=12, color=FIELD, bold=True))
    cross(240, yA, hop=True)
    parts.append(text(240, yA + 78, "горб = НЕ з'єднано", size=12, color=POS, bold=True))

    # — сучасна: верх = крапка-з'єднано, низ = голий хрест-не-з'єднано
    cross(480, yA, hop=False); parts.append(dot(480, yA))
    parts.append(text(480, yA + 78, "крапка = З'ЄДНАНО", size=12, color=FIELD, bold=True))
    cross(600, yA, hop=False)
    parts.append(text(600, yA + 78, "хрест = НЕ з'єднано", size=12, color=POS, bold=True))

    # — нижня смуга: КОНФЛІКТ. Той самий голий хрест.
    box = ("ОДИН І ТОЙ САМИЙ голий хрест:\n"
           "для старої школи — З'ЄДНАНО, для CAD — НЕ з'єднано.")
    parts.append(textbox(W / 2, 305, box, size=12.5, fill="#fff7e6", stroke="#b9770e")[0])

    return render(os.path.join(IMG, "two-conventions.svg"), W, H, *parts)


# ── Фігура 2: резистор — зигзаг (ANSI) проти прямокутника (IEC) ──────────────
def fig_resistor_ansi_iec():
    W, H = 720, 260
    parts = []

    parts.append(text(180, 40, "ANSI / IEEE 315", size=15, bold=True))
    parts.append(text(180, 60, "США, ECAD-бібліотеки", size=12, color=MUTED))
    parts.append(text(540, 40, "IEC 60617", size=15, bold=True))
    parts.append(text(540, 60, "міжнародний", size=12, color=MUTED))
    parts.append(line(360, 80, 360, 240, color="#dddddd", sw=1))

    cy = 140
    # — ANSI: зигзаг між двома виводами
    x0, x1 = 70, 290
    parts.append(line(x0, cy, x0 + 35, cy, color=WIRE, sw=WSW))      # лівий вивід
    # зигзаг
    zx = x0 + 35
    amp = 16
    seg = 14
    pts = [(zx, cy)]
    up = True
    for i in range(6):
        zx += seg
        pts.append((zx, cy - amp if up else cy + amp))
        up = not up
    zx += seg
    pts.append((zx, cy))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linejoin="round"/>' % (d, WIRE, WSW))
    parts.append(line(zx, cy, x1, cy, color=WIRE, sw=WSW))           # правий вивід
    parts.append(text(180, 210, "пилка — «намотаний дріт опору»", size=12.5, color=MUTED))

    # — IEC: прямокутник
    ox = 380
    bx0, bx1 = ox + 40, ox + 260
    parts.append(line(bx0 - 35, cy, bx0, cy, color=WIRE, sw=WSW))
    parts.append(rect(bx0, cy - 18, bx1 - bx0, 36, fill=BG, stroke=WIRE, sw=WSW, rx=0))
    parts.append(line(bx1, cy, bx1 + 35, cy, color=WIRE, sw=WSW))
    parts.append(text(540, 210, "коробка — «логічний» блок", size=12.5, color=MUTED))

    return render(os.path.join(IMG, "resistor-ansi-iec.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_two_conventions()
    fig_resistor_ansi_iec()
    print("hist figs done")
