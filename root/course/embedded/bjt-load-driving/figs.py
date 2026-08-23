# -*- coding: utf-8 -*-
"""Фігури до вставки «ULN2003 і ULN2803».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def npn(cx, cy, label=None):
    """Спрощений символ NPN: вертикальна база-планка, колектор угору, емітер униз (зі стрілкою)."""
    out = []
    bar_top, bar_bot = cy - 22, cy + 22
    # вертикальна планка бази
    out.append(line(cx, bar_top, cx, bar_bot, color=INK, sw=2.4))
    # вивід бази (ліворуч)
    out.append(line(cx - 26, cy, cx, cy, color=INK, sw=1.8))
    # колектор (угору-праворуч)
    out.append(line(cx, bar_top + 6, cx + 22, bar_top - 12, color=INK, sw=1.8))
    out.append(line(cx + 22, bar_top - 12, cx + 22, bar_top - 26, color=INK, sw=1.8))
    # емітер (униз-праворуч) зі стрілкою назовні
    out.append(line(cx, bar_bot - 6, cx + 22, bar_bot + 12, color=INK, sw=1.8))
    out.append(line(cx + 22, bar_bot + 12, cx + 22, bar_bot + 26, color=INK, sw=1.8))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 13, bar_bot + 2, cx + 22, bar_bot + 12, cx + 11, bar_bot + 11, INK))
    if label:
        out.append(text(cx - 2, cy + 2, label, size=11, color=MUTED, anchor="end"))
    return "".join(out), (cx + 22)  # повертаємо x правого виводу (колектор/емітер)


def diode_up(cx, y_anode, y_cathode):
    """Діод трикутником, провідність ЗНИЗУ ВГОРУ: анод унизу (y_anode), катод-планка вгорі (y_cathode).
    Трикутник вістрям угору вказує напрям струму — від OUT до COM (спільний катод)."""
    out = []
    s = 9
    bar_y = y_cathode + 12          # планка катода трохи нижче вузла COM
    tip_y = bar_y                   # вістря трикутника впирається в планку
    base_y = bar_y + 16             # основа трикутника нижче
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="1.8"/>' % (
        cx - s, base_y, cx + s, base_y, cx, tip_y, INK))
    out.append(line(cx - s, bar_y, cx + s, bar_y, color=INK, sw=2.4))   # планка катода (вгорі)
    out.append(line(cx, y_cathode, cx, bar_y, color=INK, sw=1.8))       # вивід катода → COM
    out.append(line(cx, base_y, cx, y_anode, color=INK, sw=1.8))        # вивід анода → OUT
    return "".join(out)


def fig_channel():
    W, H = 760, 430
    f = [text(W / 2, 28, "Один канал ULN2003: дарлінгтон із відкритим колектором + гасний діод",
              size=16, bold=True)]

    # рівні по вертикалі
    com_y = 58            # шина COM (катоди діодів) — угорі
    col_y = 96            # колекторна шина → OUTn
    in_y  = 196           # вхід / база T1
    gnd_y = 320           # шина землі (емітери) — унизу

    # межа мікросхеми (усе, що всередині корпусу)
    chip_x, chip_y, chip_w, chip_h = 150, 72, 320, 280
    f.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(chip_x + 12, chip_y + 20, "усередині ULN2003 (×7 однакових каналів)",
                  size=11, color=MUTED, anchor="start"))

    # ── вхід ліворуч: вивід INn → резистор 2.7 кОм ──
    f.append(text(58, in_y - 14, "INn", size=13, bold=True, anchor="middle"))
    f.append(text(58, in_y + 28, "з виводу логіки", size=10, color=MUTED))
    f.append(line(36, in_y, chip_x, in_y, color=INK, sw=1.8))
    rb_x = chip_x + 16
    f.append(rect(rb_x, in_y - 11, 54, 22, fill="#eef1f5", stroke=INK, sw=1.6, rx=3))
    f.append(text(rb_x + 27, in_y + 4, "2.7 кОм", size=11))
    f.append(line(rb_x + 54, in_y, rb_x + 84, in_y, color=INK, sw=1.8))

    # ── пара Дарлінгтона: T1 живить базу T2 ──
    t1x = rb_x + 108
    t1y = in_y - 26
    t2x = t1x + 78
    t2y = in_y + 26
    s1, _ = npn(t1x, t1y, "T1")
    s2, _ = npn(t2x, t2y, "T2")
    f.append(s1)
    f.append(s2)
    c1 = t1x + 22         # колектор/емітер-вивід T1 (правий)
    c2 = t2x + 22         # колектор/емітер-вивід T2 (правий)
    # емітер T1 → база T2 (характерна риса дарлінгтона)
    f.append(line(c1, t1y + 48, c1, t2y, color=INK, sw=1.8))
    f.append(line(c1, t2y, t2x - 26, t2y, color=INK, sw=1.8))
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (c1, t2y, INK))
    f.append(text((c1 + t2x) / 2 + 4, t2y - 7, "емітер→база", size=9, color=MUTED))

    # колектори обох з'єднані на колекторну шину → вихід OUTn (відкритий колектор)
    f.append(line(c1, t1y - 48, c1, col_y, color=INK, sw=1.8))
    f.append(line(c2, t2y - 48, c2, col_y, color=INK, sw=1.8))
    f.append(line(c1, col_y, c2, col_y, color=INK, sw=1.8))
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (c2, col_y, INK))
    # вихід OUTn назовні праворуч
    f.append(line(c2, col_y, 620, col_y, color=INK, sw=1.8))
    f.append(text(648, col_y + 4, "OUTn", size=13, bold=True, anchor="middle"))

    # ── емітери обох дарлінгтонів → спільна земля (локальний символ, без довгого райзера) ──
    f.append(line(c2, t2y + 48, c2, gnd_y, color=INK, sw=1.8))
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (c2, gnd_y, INK))
    # символ землі прямо під T2
    gx = c2
    f.append(line(gx, gnd_y, gx, gnd_y + 6, color=INK, sw=1.8))
    f.append(line(gx - 15, gnd_y + 6, gx + 15, gnd_y + 6, color=INK, sw=2.2))
    f.append(line(gx - 9, gnd_y + 12, gx + 9, gnd_y + 12, color=INK, sw=2.0))
    f.append(line(gx - 4, gnd_y + 18, gx + 4, gnd_y + 18, color=INK, sw=1.8))
    f.append(text(gx + 40, gnd_y + 12, "емітери → GND", size=10, color=MUTED, anchor="start"))

    # ── гасний діод (УСЕРЕДИНІ корпусу): анод на OUTn-рівні, катод угорі на шину COM ──
    d_x = 432
    f.append(diode_up(d_x, col_y, com_y))     # струм OUT → COM
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (d_x, col_y, INK))
    f.append(text(d_x + 13, (com_y + col_y) / 2 + 16, "гасний\nдіод", size=10, color=MUTED, anchor="start").replace("\n", " "))
    # шина COM назовні (пін праворуч)
    f.append(line(d_x, com_y, 620, com_y, color=INK, sw=1.8))
    f.append(text(648, com_y + 4, "COM", size=13, bold=True, anchor="middle"))

    # ── підказка зовнішнього підключення (під корпусом, поза ним) ──
    note = ("Підключення:  +V навантаження → COM   •   навантаження → між +V і OUTn\n"
            "Канал лише ТЯГНЕ OUTn до землі (відкритий колектор) — плюс він не дає.")
    f.append(fitbox(150, 372, 460, 46, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "uln-channel.svg"), W, H, *f)


if __name__ == "__main__":
    fig_channel()
    print("OK: img/uln-channel.svg")
