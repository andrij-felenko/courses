# -*- coding: utf-8 -*-
"""Фігури до теми «Узгодження за шумом у LNA» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  two-optimums.svg   — на площині опору джерела ДВА різні оптимуми: за потужністю й за шумом
  noise-bowl.svg     — коефіцієнт шуму як «чаша» над Yopt: круто росте при відході (керує Rn)
  power-vs-noise.svg — той самий тракт, два узгодження: за шумом (тихо) vs за потужністю (гучно)
  degeneration.svg   — котушка в емітері/витоку тягне вхідний опір до спряженого з Zopt
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def two_optimums():
    """Площина опору джерела: точка узгодження за потужністю й точка узгодження за шумом — РІЗНІ.
    Навколо шумового оптимуму — кола сталого коефіцієнта шуму (мішень)."""
    W, H = 700, 430
    p = []
    cx, cy = 330, 215
    R = 150
    # межа «площини» (кружок як натяк на діаграму опорів)
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (cx, cy, R, BG, MUTED))
    p.append(text(cx, cy - R - 12, "площина опору джерела (Re, Im)", size=12, color=MUTED))

    # точка узгодження за потужністю (спряжений опір) — праворуч-униз
    pmx, pmy = cx + 78, cy + 46
    p.append(circle(pmx, pmy, 7, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(pmx + 12, pmy + 5, "узгодження за потужністю", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(pmx + 12, pmy + 21, "(спряжений опір — макс. віддача)", size=10, color=MUTED, anchor="start"))

    # шумовий оптимум — ліворуч-угорі; навколо нього мішень кіл сталого NF
    nx, ny = cx - 58, cy - 40
    for rr, lab, dash in [(34, "+0.5 дБ", "4 4"), (62, "+1 дБ", "4 4"), (92, "+2 дБ", "4 4")]:
        p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="%s"/>'
                 % (nx, ny, rr, FIELD, dash))
    p.append(circle(nx, ny, 7, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(nx - 10, ny - 100, "Yopt: узгодження за шумом", size=12, bold=True, color=FIELD, anchor="middle"))
    p.append(text(nx, ny + 14, "Fmin", size=11, bold=True, color=FIELD))
    p.append(text(nx + 40, ny - 30, "+0.5 дБ", size=9, color=FIELD, anchor="start"))

    # стрілка «відстань між двома оптимумами»
    p.append(line(nx + 6, ny + 4, pmx - 6, pmy - 4, color=INK, sw=1.6, dash="3 3"))
    p.append(text((nx + pmx) / 2 + 6, (ny + pmy) / 2 - 8, "вони НЕ збігаються", size=11, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 400,
                      "Точка макс. віддачі потужності й точка мінімального шуму лежать у РІЗНИХ місцях.\n"
                      "Кола — однаковий коефіцієнт шуму; що далі від Yopt, то він гірший.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'two-optimums.svg'), W, H, *p,
           title="Два різні оптимуми опору джерела: за потужністю й за шумом")


def noise_bowl():
    """Коефіцієнт шуму як функція опору джерела — парабола-чаша з дном Fmin при Yopt.
    Крутість стінок задає шумовий опір Rn: великий Rn — вузька гостра чаша."""
    W, H = 700, 400
    p = []
    ox, oy = 110, 300
    axw, axh = 470, 230
    # осі
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw - 4, oy + 26, "опір джерела Re(Ys)", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 16, oy - axh + 6, "F", size=14, bold=True, anchor="end"))
    p.append(text(ox - 16, oy - axh + 22, "(дБ)", size=11, color=MUTED, anchor="end"))

    # дно мінімуму
    minx = ox + axw * 0.42
    floor_y = oy - 36
    p.append(line(ox, floor_y, ox + axw, floor_y, color=MUTED, sw=1, dash="4 4"))
    p.append(text(ox - 6, floor_y + 4, "Fmin", size=11, bold=True, color=MUTED, anchor="end"))

    def bowl(k, col, lbl, lx):
        pts = []
        for i in range(0, 101):
            x = ox + 20 + (axw - 40) * i / 100
            d = (x - minx) / 60.0
            y = floor_y - k * d * d
            y = max(oy - axh + 6, y)
            pts.append((x, y))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        p.append(text(lx, oy - axh + 14, lbl, size=11, bold=True, color=col, anchor="start"))

    bowl(150, FIELD, "малий Rn: полога чаша (терпима)", ox + 150)
    bowl(420, POS, "великий Rn: гостра чаша (вимоглива)", ox + 150 + 0 )
    # позначка дна
    p.append(circle(minx, floor_y, 5, fill=BG, stroke=INK, sw=1.8))
    p.append(line(minx, floor_y, minx, oy, color=INK, sw=1, dash="3 3"))
    p.append(text(minx, oy + 22, "Yopt", size=12, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 372,
                      "Коефіцієнт шуму має чітке дно Fmin при оптимальному Yopt і росте в обидва боки.\n"
                      "Крутість стінок задає шумовий опір Rn: великий Rn — кожен крок убік дорогий.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'noise-bowl.svg'), W, H, *p,
           title="Коефіцієнт шуму як чаша над оптимальним опором джерела")


def power_vs_noise():
    """Один тракт, два узгодження джерела: за шумом (тихо, трохи менша віддача) vs
    за потужністю (гучно, але шумніше). Дві колонки-порівняння."""
    W, H = 700, 410
    p = []
    cols = [
        (175, "узгодження за ШУМОМ", FIELD,
         [("коеф. шуму", "Fmin — найтихіше", True),
          ("віддача потужності", "трохи нижча", False),
          ("підсилення", "трохи нижче", False)]),
        (505, "узгодження за ПОТУЖНІСТЮ", POS,
         [("коеф. шуму", "вищий за Fmin", False),
          ("віддача потужності", "максимальна", True),
          ("підсилення", "максимальне", True)]),
    ]
    top = 70
    for cx, title, col, rows in cols:
        fillc = "#eafaf0" if col == FIELD else "#fdecea"
        p.append(rect(cx - 140, top, 280, 250, fill=fillc, stroke=col, sw=2, rx=8))
        p.append(text(cx, top + 26, title, size=13, bold=True, color=col))
        p.append(line(cx - 120, top + 40, cx + 120, top + 40, color=col, sw=1))
        yy = top + 70
        for name, val, good in rows:
            mark = "✓" if good else "•"
            mc = FIELD if good else MUTED
            p.append(text(cx - 120, yy, name, size=12, bold=True, anchor="start"))
            p.append(text(cx + 120, yy, val, size=12, color=mc, anchor="end"))
            yy += 46
    # стрілка-вибір
    p.append(text(W / 2, top + 150, "той самий\nтранзистор,\nрізне джерело", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 386,
                      "Налаштувати джерело можна лише в ОДНУ з точок. LNA на вході обирають шум:\n"
                      "трохи жертвують віддачею й підсиленням заради найнижчого коефіцієнта шуму.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'power-vs-noise.svg'), W, H, *p,
           title="Узгодження за шумом проти узгодження за потужністю: що чим платиш")


def degeneration():
    """Котушка в емітері/витоку додає РЕЗИСТИВНУ частину вхідного опору без фізичного резистора —
    тягне вхід до спряженого з Zopt, тож шумовий і потужнісний оптимуми сходяться."""
    W, H = 700, 400
    p = []
    # ── ліворуч: схема — транзистор з котушкою в джерелі ──
    tx, ty = 150, 150
    # транзистор як трикутник-підсилювач
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (tx, ty - 34, tx, ty + 34, tx + 60, ty, FILL, LINE))
    p.append(text(tx + 22, ty + 5, "Q", size=15, bold=True))
    # вхід
    p.append(line(tx - 70, ty - 16, tx, ty - 16, color=INK, sw=2))
    p.append(text(tx - 74, ty - 16, "вхід", size=11, color=MUTED, anchor="end"))
    # вихід
    p.append(arrow(tx + 60, ty, tx + 110, ty, color=INK, sw=2))
    p.append(text(tx + 114, ty + 4, "вихід", size=11, color=MUTED, anchor="start"))
    # котушка в джерелі/емітері (донизу) — спіралька зі стрілкою
    sx = tx
    p.append(line(sx, ty + 34, sx, ty + 56, color=INK, sw=2))
    # катушка-зиґзаґ
    coil = "M%.1f %.1f" % (sx, ty + 56)
    yy = ty + 56
    for _ in range(3):
        coil += " q 12 8 0 16 q -12 8 0 16"
        yy += 32
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (coil, NEG))
    p.append(text(sx + 22, ty + 90, "Ls", size=13, bold=True, color=NEG, anchor="start"))
    p.append(line(sx, yy, sx, yy + 14, color=INK, sw=2))
    p.append(line(sx - 14, yy + 14, sx + 14, yy + 14, color=INK, sw=2.4))  # земля
    p.append(text(sx, yy + 30, "земля", size=10, color=MUTED))

    # ── праворуч: до/після на площині опору ──
    bx, by = 470, 165
    BR = 110
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="1.3"/>'
             % (bx, by, BR, BG, MUTED))
    # шумовий оптимум (ціль)
    ox_, oy_ = bx - 30, by - 36
    p.append(circle(ox_, oy_, 6, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(ox_, oy_ - 12, "Zopt*", size=11, bold=True, color=FIELD))
    # вхідний опір ДО — далеко, на самій осі (чисто реактивний, без резистивної частини)
    inx0, iny0 = bx + 70, by - 36
    p.append(circle(inx0, iny0, 6, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(inx0 + 10, iny0 - 4, "вхід до Ls", size=10, color=POS, anchor="start"))
    # вхідний опір ПІСЛЯ — присунувся до Zopt
    p.append(arrow(inx0 - 4, iny0 + 4, ox_ + 18, oy_ + 2, color=NEG, sw=2))
    p.append(text((inx0 + ox_) / 2 + 4, (iny0 + oy_) / 2 + 22, "Ls додає Re-частину →", size=10, bold=True, color=NEG))
    p.append(text((inx0 + ox_) / 2 + 4, (iny0 + oy_) / 2 + 37, "вхід присувається до Zopt*", size=10, color=NEG))
    p.append(text(bx, by + BR + 16, "площина вхідного опору", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 376,
                      "Котушка в емітері/витоку створює резистивну частину вхідного опору БЕЗ фізичного резистора\n"
                      "(тож без зайвого шуму) — і присуває вхід до спряженого з Zopt: обидва оптимуми сходяться.",
                      size=11, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'degeneration.svg'), W, H, *p,
           title="Котушка в джерелі: зводить шумовий і потужнісний оптимуми разом")


def rothe_dahlke_split():
    """Прийом Роте — Дальке (вставка hist): шумливий двопорт = тихий двопорт
    + дві ЗОВНІШНІ шумові величини на вході (напруга en послідовно, струм in паралельно)
    з кореляцією між ними."""
    W, H = 720, 360
    p = []

    # ЛІВОРУЧ: шумливий двопорт як «чорна скриня» з хвильками шуму всередині
    lx, ly, lw, lh = 40, 120, 150, 110
    p.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(lx + lw / 2, ly - 12, "шумливий двопорт", size=12, bold=True, color=POS))
    p.append(text(lx + lw / 2, ly + 26, "уся фізика шуму", size=11, color=INK))
    p.append(text(lx + lw / 2, ly + 44, "всередині —", size=11, color=INK))
    p.append(text(lx + lw / 2, ly + 62, "теплова, дробова…", size=10, color=MUTED))
    # хвилька-натяк на шум
    wy = ly + 86
    seg = "M%.0f %.0f" % (lx + 24, wy)
    import math as _m
    for k in range(1, 41):
        xx = lx + 24 + k * (lw - 48) / 40.0
        yy = wy + 7 * _m.sin(k * 0.9)
        seg += " L%.1f %.1f" % (xx, yy)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (seg, POS))

    # стрілка-«дорівнює»
    p.append(text(212, ly + lh / 2 + 6, "=", size=30, bold=True, color=INK))

    # ПРАВОРУЧ: тихий двопорт + два винесені джерела на вході
    rx, ry, rw, rh = 470, 120, 150, 110
    p.append(rect(rx, ry, rw, rh, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(rx + rw / 2, ry - 12, "ідеально ТИХИЙ двопорт", size=12, bold=True, color=FIELD))
    p.append(text(rx + rw / 2, ry + rh / 2 + 4, "0 шуму", size=13, bold=True, color=FIELD))

    # вхідна шина зліва від тихого двопорту
    bus_x = 300
    top_y, bot_y = ry + 24, ry + rh - 24
    p.append(line(bus_x, top_y, rx, top_y, color=LINE, sw=1.6))
    p.append(line(bus_x, bot_y, rx, bot_y, color=LINE, sw=1.6))

    # джерело шумової НАПРУГИ en — послідовно у верхній провід
    ev_x = 360
    p.append(circle(ev_x, top_y, 13, fill=BG, stroke=NEG, sw=2))
    p.append(text(ev_x, top_y + 5, "~", size=16, bold=True, color=NEG))
    p.append(text(ev_x, top_y - 22, "en", size=13, bold=True, color=NEG, italic=True))
    p.append(text(ev_x + 64, top_y - 22, "шумова напруга", size=10, color=NEG, anchor="middle"))

    # джерело шумового СТРУМУ in — паралельно (між шинами), ближче до входу
    ic_x = 318
    p.append(circle(ic_x, (top_y + bot_y) / 2, 13, fill=BG, stroke=NEG, sw=2))
    p.append(arrow(ic_x, (top_y + bot_y) / 2 + 9, ic_x, (top_y + bot_y) / 2 - 9, color=NEG, sw=2))
    p.append(line(ic_x, top_y, ic_x, (top_y + bot_y) / 2 - 13, color=LINE, sw=1.4))
    p.append(line(ic_x, (top_y + bot_y) / 2 + 13, ic_x, bot_y, color=LINE, sw=1.4))
    p.append(text(ic_x - 18, (top_y + bot_y) / 2 + 5, "in", size=13, bold=True, color=NEG, italic=True, anchor="end"))
    p.append(text(ic_x - 12, bot_y + 16, "шумовий струм", size=10, color=NEG, anchor="middle"))

    # дуга кореляції між двома джерелами
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>'
             % (ic_x + 10, (top_y + bot_y) / 2 - 8, 345, 150, ev_x - 6, top_y + 10, MUTED))
    p.append(text(352, 138, "кореляція", size=10, italic=True, color=MUTED))

    b, _, _ = textbox(W / 2, 312,
                      "Увесь внутрішній шум виноситься у ДВІ зовнішні величини на вході (напруга en + струм in),\n"
                      "частково скорельовані; сам двопорт оголошується тихим. Цей розклад задають 4 числа: Fmin, Rn, Gopt, Bopt.",
                      size=11, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'rothe-dahlke-split.svg'), W, H, *p,
           title="Прийом Роте — Дальке: тихий двопорт + дві зовнішні шумові величини з кореляцією")


if __name__ == '__main__':
    two_optimums()
    noise_bowl()
    power_vs_noise()
    degeneration()
    rothe_dahlke_split()
    print("OK: 5 figures ->", OUT)
