# -*- coding: utf-8 -*-
"""Фігури до статті «OPI та HyperRAM»
(book/electronics/digital/opi-hyperram).

Кут статті — багато даних дуже небагатьма дротами: 8 ліній DDR
розкладають у часі команду, адресу, паузу-латентність і потік даних.

Фігури:
  transaction.svg — одна DDR-транзакція читання: CS#, CK, фази по DQ, RWDS
  compare.svg     — дві дзеркальні шини: OPI (окремі фази) ↔ HyperBus (CA+RWDS)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

DATA = "#8e44ad"   # шина даних — фіолетовий (перекликається з текстом статті)


# ── локальні помічники малювання шини ───────────────────────────────────────
def waveband(x0, x1, y, h, label, col, fill_op=0.14, size=11):
    """Прямокутник-«вагон» на шині від x0 до x1 з підписом усередині."""
    out = [rect(x0, y - h / 2, x1 - x0, h, fill=col, stroke=col, sw=1.6, rx=3)]
    # заливка приглушена: домалюємо напівпрозорий шар
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" fill-opacity="%.2f"/>'
               % (x0, y - h / 2, x1 - x0, h, col, fill_op))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" stroke="%s" stroke-width="1.6"/>'
               % (x0, y - h / 2, x1 - x0, h, col))
    out.append(text((x0 + x1) / 2, y + size * 0.36, label, size=size, color=col, bold=True))
    return "".join(out)


def idle(x0, x1, y):
    """Тонка лінія-«нічого» (шина у спокої)."""
    return line(x0, x1 if False else x0, y, x1, y, color=MUTED, sw=1.4) if False else \
        line(x0, y, x1, y, color=MUTED, sw=1.4)


def clock(x0, x1, y, period, amp=9):
    """Меандр такту від x0 до x1 із заданим періодом."""
    pts = [(x0, y + amp)]
    x = x0
    high = True
    half = period / 2
    while x < x1 - 0.1:
        nx = min(x + half, x1)
        yy = y - amp if high else y + amp
        pts.append((x, yy))
        pts.append((nx, yy))
        x = nx
        high = not high
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path, INK)


def rowlabel(x, y, s, col=INK):
    return text(x, y + 4, s, size=12, color=col, bold=True, anchor="end")


# ════════════════════════════════════════════════════════════════════════════
# 1. transaction.svg — одна DDR-транзакція читання
# ════════════════════════════════════════════════════════════════════════════
def fig_transaction():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Одна транзакція читання: команда → адреса → пауза → дані", size=15, bold=True))

    left = 118            # де починаються доріжки
    right = 690
    lab = left - 12
    rowH = 30

    yCS = 78
    yCK = 128
    yDQ = 188
    yRW = 250

    # межі фаз по осі x
    x_start = left + 10          # CS# опускається
    x_cmd0 = left + 40
    x_cmd1 = x_cmd0 + 70         # команда (2 однакові байти)
    x_addr = x_cmd1 + 130        # адреса (4 байти)
    x_lat = x_addr + 110         # латентність
    x_data = right - 12          # дані до кінця
    x_end = right                # CS# піднімається

    # ── CS# ──
    f.append(rowlabel(lab, yCS, "CS#"))
    f.append(line(left, yCS - 12, x_start, yCS - 12, color=INK, sw=1.8))     # високо (не вибрано)
    f.append(line(x_start, yCS - 12, x_start, yCS + 12, color=INK, sw=1.8))  # ↓
    f.append(line(x_start, yCS + 12, x_end, yCS + 12, color=INK, sw=1.8))    # низько (вибрано)
    f.append(line(x_end, yCS + 12, x_end, yCS - 12, color=INK, sw=1.8))      # ↑
    f.append(text(x_start - 4, yCS - 18, "↓ вибрано", size=10, color=MUTED, anchor="start"))
    f.append(text(x_end + 2, yCS - 18, "↑", size=11, color=MUTED, anchor="start"))

    # ── CK (такт цокає всю транзакцію, зокрема під час латентності) ──
    f.append(rowlabel(lab, yCK, "CK"))
    f.append(clock(x_cmd0, x_data, yCK, period=28, amp=8))
    f.append(text((x_lat + x_data) / 2, yCK - 16, "такт не спиняється", size=9.5, color=MUTED))

    # ── DQ[7:0] ──
    f.append(rowlabel(lab, yDQ, "DQ[7:0]"))
    f.append(line(left, yDQ, x_cmd0, yDQ, color=MUTED, sw=1.4))
    f.append(waveband(x_cmd0, x_cmd1, yDQ, rowH, "CMD", DATA))
    f.append(waveband(x_cmd1, x_addr, yDQ, rowH, "адреса", NEG))
    f.append(line(x_addr, yDQ, x_lat, yDQ, color=MUTED, sw=1.4, dash="4 4"))
    # потік даних: кілька вагонів
    nseg = 4
    seg = (x_data - x_lat) / nseg
    for k in range(nseg):
        xa = x_lat + k * seg
        f.append(waveband(xa + 1.5, xa + seg - 1.5, yDQ, rowH,
                          "D%d" % k, FIELD, size=10))
    f.append(text((x_cmd0 + x_cmd1) / 2, yDQ - rowH / 2 - 6, "той самий байт", size=9, color=DATA))
    f.append(text((x_cmd0 + x_cmd1) / 2, yDQ + rowH / 2 + 13, "на 2 фронтах", size=9, color=DATA))
    f.append(text((x_lat + x_data) / 2, yDQ + rowH / 2 + 13, "по 2 байти на такт", size=9, color=FIELD))

    # ── RWDS / DQS ──
    f.append(rowlabel(lab, yRW, "RWDS"))
    f.append(line(left, yRW, x_addr, yRW, color=MUTED, sw=1.4))
    # під час латентності — тихо, під час даних — строб у такт вагонам
    f.append(line(x_addr, yRW, x_lat, yRW, color=MUTED, sw=1.4, dash="4 4"))
    strobe = []
    x = x_lat
    high = False
    hp = seg / 2
    strobe.append((x, yRW + 8))
    while x < x_data - 0.1:
        nx = min(x + hp, x_data)
        yy = yRW - 8 if high else yRW + 8
        strobe.append((x, yy)); strobe.append((nx, yy))
        x = nx; high = not high
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" L ".join("%.1f %.1f" % p for p in strobe), FIELD))
    f.append(text((x_lat + x_data) / 2, yRW + 24, "строб приходить разом із даними", size=9, color=FIELD))

    # фазові підписи-скоби зверху
    yб = 300
    spans = [(x_cmd0, x_addr, "команда й адреса", DATA),
             (x_addr, x_lat, "латентність", POS),
             (x_lat, x_data, "потік даних", FIELD)]
    for (xa, xb, name, col) in spans:
        f.append(line(xa, yб, xb, yб, color=col, sw=1.4))
        f.append(line(xa, yб - 4, xa, yб + 4, color=col, sw=1.4))
        f.append(line(xb, yб - 4, xb, yб + 4, color=col, sw=1.4))
        f.append(text((xa + xb) / 2, yб + 16, name, size=10.5, color=col, bold=True))
    # приписка про латентність (два рядки — через mtext)
    f.append(mtext((x_addr + x_lat) / 2, yб - 14, ["пам'ять піднімає", "дані з масиву"],
                   size=9, color=POS))

    render(os.path.join(IMG, "transaction.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. compare.svg — OPI (окремі фази) ↔ HyperBus (CA + RWDS)
# ════════════════════════════════════════════════════════════════════════════
def fig_compare():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 28, "Дві дзеркальні шини — той самий задум, різний почерк", size=15, bold=True))

    left = 150
    right = 688
    lab = left - 12
    rowH = 26

    def bus(y0, title, phases, col_title):
        """phases: список (частка_ширини, підпис, колір, dashed) для рядка DQ."""
        out = []
        out.append(text(left - 96, y0 + 4, title, size=13, color=col_title, bold=True, anchor="start"))
        # рядок DQ
        out.append(rowlabel(lab, y0, "DQ[7:0]"))
        total = sum(p[0] for p in phases)
        x = left
        span = right - left
        for (wfrac, name, col, dashed) in phases:
            xa = x
            xb = x + span * wfrac / total
            if dashed:
                out.append(line(xa, y0, xb, y0, color=MUTED, sw=1.4, dash="4 4"))
                out.append(text((xa + xb) / 2, y0 + 4, name, size=9.5, color=MUTED))
            else:
                out.append(waveband(xa + 1.5, xb - 1.5, y0, rowH, name, col, size=10))
            x = xb
        return out, y0

    # ── OPI ──
    out, yOPI = bus(110, "OPI (xSPI)",
                    [(1.0, "CMD", DATA, False),
                     (1.6, "адреса", NEG, False),
                     (1.1, "латентність", None, True),
                     (2.6, "дані · дані · дані", FIELD, False)], DATA)
    f.extend(out)
    # рядок DQS для OPI
    yDQS = yOPI + 46
    f.append(rowlabel(lab, yDQS, "DQS"))
    f.append(line(left, yDQS, right, yDQS, color=MUTED, sw=1.2))
    f.append(text(left, yDQS + 18, "окрема лінія-строб синхронізує дані на швидкому режимі", size=9.5, color=MUTED, anchor="start"))

    # роздільник
    f.append(line(60, 210, right, 210, color=MUTED, sw=1.0, dash="6 5"))

    # ── HyperBus ──
    out, yHB = bus(258, "HyperBus",
                   [(1.9, "CA (48 біт, 3 такти)", DATA, False),
                    (1.1, "латентність", None, True),
                    (2.6, "дані · дані · дані", FIELD, False)], DATA)
    f.extend(out)
    # рядок RWDS для HyperBus
    yRW = yHB + 46
    f.append(rowlabel(lab, yRW, "RWDS"))
    # три функції строба — короткі підписи над лінією
    f.append(line(left, yRW, right, yRW, color=FIELD, sw=1.4))
    f.append(text(left, yRW + 18,
                  "одна лінія: строб читання · маска запису · «потрібна подвійна латентність»",
                  size=9.5, color=FIELD, anchor="start"))

    # права винесена нотатка
    bb, _, _ = textbox(W / 2, 350,
                       "OPI розкладає команду й адресу окремо;  HyperBus пакує їх у 48-бітний CA "
                       "й вантажить одну лінію RWDS трьома ролями.\nДруга генерація HyperRAM розуміє обидві мови.",
                       size=10.5, color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)

    render(os.path.join(IMG, "compare.svg"), W, H, *f)


if __name__ == "__main__":
    fig_transaction()
    fig_compare()
    print("OK: 2 фігури у", IMG)
