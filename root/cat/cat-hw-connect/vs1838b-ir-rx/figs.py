# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «VS1838B — ІЧ-приймач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: ланцюг від фотодіода до виходу ──────────────────────────
def fig_inside():
    W, H = 1040, 430
    f = [text(W / 2, 30, "Що всередині VS1838B: увесь ланцюг «світло → чистий цифровий сигнал» в одному корпусі",
              size=15, bold=True)]

    # корпус
    bx, by, bw, bh = 60, 70, 920, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "корпус VS1838B (3 ніжки)", size=11, bold=True, color=MUTED, anchor="start"))

    # ланцюг блоків зліва направо
    cy = by + 118
    blocks = [
        ("PIN-\nфотодіод", "#fdecea"),
        ("перед-\nпідсилювач", FILL),
        ("АРП\n(AGC)", FILL),
        ("смуговий\nфільтр\n~38 кГц", "#eaf5ec"),
        ("демоду-\nлятор", FILL),
        ("вихідний\nключ", "#eef1f5"),
    ]
    n = len(blocks)
    x0 = bx + 40
    gap = 22
    bwid = (bw - 80 - gap * (n - 1)) / n
    centers = []
    for i, (label, fill) in enumerate(blocks):
        x = x0 + i * (bwid + gap)
        f.append(fitbox(x, cy - 40, bwid, 80, label, size=11, fill=fill, stroke=INK, bold=True))
        centers.append(x + bwid / 2)
        if i > 0:
            f.append(arrow(centers[i - 1] + bwid / 2 + 3, cy, x - 3, cy, color=INK, sw=1.8))

    # вхід світла ліворуч у фотодіод
    for k in range(3):
        ay = cy - 22 + k * 14
        f.append(arrow(bx - 2, ay - 6, x0 - 4, ay, color=FIELD, sw=1.6))
    f.append(text(bx + 2, by + bh - 14, "ІЧ-світло 940 нм, мигтить на 38 кГц", size=10, color=FIELD, anchor="start"))

    # вихід OUT праворуч
    ox = x0 + (n - 1) * (bwid + gap) + bwid
    f.append(line(ox + 3, cy, ox + 46, cy, color=NEG, sw=2.2))
    f.append(circle(ox + 52, cy, 5, fill=BG, stroke=NEG, sw=2.2))
    f.append(text(ox + 34, cy - 12, "OUT", size=12, bold=True, color=NEG))

    # підпис-висновок
    b, _, _ = textbox(W / 2, 350,
                      "Фотодіод ловить світло; підсилювач і АРП піднімають кволий струм до робочого рівня; смуговий фільтр\n"
                      "пропускає ЛИШЕ ~38 кГц (усе інше — сонце, лампи — відсіює); демодулятор здирає несучу й лишає обвідну;\n"
                      "вихідний ключ віддає чистий рівень. На OUT — уже готовий цифровий сигнал, читати звичайним GPIO.",
                      size=11, fill="#eaf5ec", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Несуча → обвідна: що робить приймач із сигналом ───────────────────────
def fig_carrier():
    W, H = 1000, 480
    f = [text(W / 2, 30, "Несуча 38 кГц і обвідна: приймач бачить пачки мигтіння, а віддає лише «горить / не горить»",
              size=14.5, bold=True)]

    import math as _m
    ax0 = 80
    axw = 840

    # ── верх: те, що в повітрі (несуча) ──
    top = 90
    trow = 46
    f.append(text(ax0 - 8, top - 6, "у повітрі:", size=11, bold=True, color=INK, anchor="end"))
    # пачки: логічна одиниця NEC = burst 560 мкс + пауза 1690 мкс; нуль = burst 560 + пауза 560
    # намалюємо схематично 3 пачки різної довжини паузи
    baseline = top + trow
    f.append(line(ax0, baseline, ax0 + axw, baseline, color=MUTED, sw=1.0))
    # опишемо сегменти (burst?, довжина_px)
    segs = [(True, 60), (False, 170), (True, 60), (False, 60), (True, 60), (False, 130), (True, 60)]
    x = ax0 + 20
    for on, wpx in segs:
        if on:
            # частокіл — несуча
            k = 0
            xx = x
            while xx < x + wpx:
                f.append(line(xx, baseline, xx, baseline - 30, color=POS, sw=1.4))
                xx += 5
                k += 1
        x += wpx
    f.append(text(ax0 + 20 + 30, top - 6, "пачки мигтіння на 38 кГц (несуча увімкнена / вимкнена)",
                  size=10, color=POS, anchor="start"))

    # мітка одного burst
    f.append(text(ax0 + 20 + 26, baseline + 18, "560 мкс\n(≈21 період)", size=9, color=MUTED, anchor="middle")
             if False else text(ax0 + 46, baseline + 16, "≈21 період несучої в пачці", size=9, color=MUTED, anchor="start"))

    # ── низ: те, що на OUT (обвідна, активний 0) ──
    bot = 250
    brow = 46
    f.append(text(ax0 - 8, bot - 6, "на OUT:", size=11, bold=True, color=INK, anchor="end"))
    hi = bot            # рівень висоти = спокій (HIGH)
    lo = bot + brow     # низ = активний LOW
    f.append(text(ax0 + axw + 6, hi + 4, "HIGH (спокій)", size=9, color=MUTED, anchor="start"))
    f.append(text(ax0 + axw + 6, lo + 4, "LOW (є несуча)", size=9, color=MUTED, anchor="start"))
    # обвідна: там де burst → LOW, де пауза → HIGH (інвертовано!)
    x = ax0 + 20
    pts = [(ax0, hi)]
    for on, wpx in segs:
        y = lo if on else hi
        pts.append((x, y))
        pts.append((x + wpx, y))
        x += wpx
    pts.append((x, hi))
    pts.append((ax0 + axw, hi))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, NEG))

    # вертикальні пунктири, що звʼязують пачку з провалом на OUT
    x = ax0 + 20
    for on, wpx in segs:
        if on:
            f.append(line(x, baseline - 30, x, lo, color=MUTED, sw=0.8, dash="2 4"))
        x += wpx

    b, _, _ = textbox(W / 2, 400,
                      "Пульт передає не рівний промінь, а ПАЧКИ мигтіння на 38 кГц. Приймач для кожної пачки опускає OUT у LOW,\n"
                      "а в паузах тримає HIGH — тобто віддає обвідну (яка пачка коротка, яка довга), уже без самої несучої.\n"
                      "Довжина пауз кодує біти (протокол); вихід ІНВЕРТОВАНИЙ — спокій = 1, прийом = 0.",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "carrier-envelope.svg"), W, H, *f)


# ── 3. Розпіновка й підключення пін-у-пін (орієнтація — банька до тебе) ───────
def fig_wiring():
    W, H = 1000, 470
    f = [text(W / 2, 30, "Розпіновка й підключення: банька до тебе, зліва направо GND · VCC · OUT",
              size=15, bold=True)]

    # ── зліва: сам приймач, вигляд спереду (банька до читача) ──
    dx, dy = 150, 150
    # банька-купол
    f.append('<path d="M %.0f %.0f a 58 58 0 0 1 116 0 Z" fill="#111827" stroke="%s" stroke-width="2"/>'
             % (dx - 58, dy, INK))
    f.append('<rect x="%.0f" y="%.0f" width="116" height="30" fill="#1f2937" stroke="%s" stroke-width="2"/>'
             % (dx - 58, dy, INK))
    f.append(text(dx, dy - 20, "вигляд СПЕРЕДУ", size=10, bold=True, color=BG))
    f.append(text(dx, dy - 4, "(банька до тебе)", size=9, color="#cbd5e1"))

    # три ніжки вниз; підписи ліворуч від кожної (щоб дроти не перетнули текст)
    legs = [("1  GND", NEG, dx - 40), ("2  VCC", POS, dx), ("3  OUT", FIELD, dx + 40)]
    for lab, col, lx in legs:
        f.append(line(lx, dy + 30, lx, dy + 92, color=INK, sw=2.6))
        f.append(circle(lx, dy + 100, 6, fill=BG, stroke=col, sw=2.4))
    # підписи ставимо збоку рядком під баньку, з розведенням, поза дротами
    f.append(text(dx, dy + 150, "ніжки 1·2·3, зліва направо:", size=10, color=MUTED))
    f.append(text(dx, dy + 168, "GND · VCC · OUT", size=11, bold=True, color=INK))

    # ── праворуч: плата ──
    bx, by, bw, bh = 660, 120, 250, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("GND", NEG, by + 80, "земля"),
            ("3.3–5 В", POS, by + 130, "живлення"),
            ("GPIO", FIELD, by + 180, "будь-який цифровий вхід")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.4))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # дроти від ніжок до плати — прямі діагоналі з майданчика ніжки (y≈106),
    # ідуть у верхній зоні й не перетинають підписи ніжок унизу
    wire_map = [(dx - 40, NEG, by + 80), (dx, POS, by + 130), (dx + 40, FIELD, by + 180)]
    for lx, col, ty in wire_map:
        f.append(line(lx, dy + 106, bx - 6, ty, color=col, sw=2.4))

    b, _, _ = textbox(W / 2, 410,
                      "OUT іде на БУДЬ-ЯКИЙ цифровий пін — усередині вже стоїть підтяжка, вихід чистий, зовнішніх деталей не треба.\n"
                      "Живлення бери під логіку плати: ESP32 — 3.3 В. Переплутаєш VCC і GND — мікросхема гріється й гине, звір орієнтацію.",
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_carrier()
    fig_wiring()
    print("VS1838B figs done ->", IMG)
