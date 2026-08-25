# -*- coding: utf-8 -*-
"""Фігури до теми «Пам'ять як масив» та її вставки про осердя.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

ADDR = "#6b7280"     # адреса — приглушена (це «де»)
VAL  = INK           # вміст — основний (це «що»)


# ── 1. Масив пронумерованих комірок: адреса ↔ вміст ──────────────────────────
def fig_array():
    W, H = 760, 470
    f = [text(W / 2, 28, "Пам'ять — масив пронумерованих комірок", size=16, bold=True),
         text(W / 2, 50, "кожна тримає один байт і має унікальний номер — адресу",
              size=11, color=MUTED, italic=True)]

    # колонка комірок праворуч
    cells = [("0x00", "0x2A"), ("0x01", "0xFF"), ("0x02", "0x00"),
             ("0x03", "0x41"), ("0x04", "0x7C"), ("0x05", "0x10"),
             ("0x06", "0x9B"), ("0x07", "0x03")]
    cx, cw, ch, top = 470, 120, 32, 92
    f.append(text(cx - cw / 2 - 14, top - 12, "адреса", size=11, color=ADDR, anchor="end", bold=True))
    f.append(text(cx, top - 12, "вміст (байт)", size=11, color=VAL, bold=True))
    for i, (addr, val) in enumerate(cells):
        y = top + i * (ch + 6)
        hot = (addr == "0x03")
        f.append(rect(cx - cw / 2, y, cw, ch,
                      fill="#fdecea" if hot else BG, stroke=POS if hot else INK,
                      sw=2 if hot else 1.4))
        f.append(text(cx - cw / 2 - 14, y + ch / 2 + 4, addr, size=11, color=ADDR, anchor="end", bold=True))
        f.append(text(cx, y + ch / 2 + 4, val, size=13, color=VAL, bold=True))
    yhot = top + 3 * (ch + 6) + ch / 2
    f.append(text(cx + cw / 2 + 14, yhot + 4,
                  "← комірка 0x03 тримає байт 0x41", size=11, color=POS, anchor="start", bold=True))

    # аналогія: вулиця будинків
    bx, by, bw, bh = 70, 110, 250, 230
    f.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(bx + bw / 2, by + 24, "Аналогія: вулиця будинків", size=12.5, color=FIELD, bold=True))
    for i in range(4):
        hy = by + 44 + i * 42
        f.append(rect(bx + 40, hy, 38, 30, fill="#eef7ee", stroke=FIELD, sw=1.4))
        f.append(text(bx + 59, hy + 21, "[ ]", size=12, color=INK))
        f.append(text(bx + 32, hy + 20, "№%d" % i, size=10, color=ADDR, anchor="end", bold=True))
        f.append(text(bx + 88, hy + 20, "← мешканець (дані)", size=9.5, color=INK, anchor="start"))
    f.append(text(bx + bw / 2, by + bh - 12, "номер будинку = адреса", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, H - 36,
                  "Дві різні речі: адреса каже, ДЕ комірка; вміст — ЩО в ній лежить.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 16,
                  "Адреси майже завжди пишуть шістнадцятково: 0x00, 0x1F, 0xFF — компактно лягає на біти.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "array.svg"), W, H, *f)


# ── 2. Адреса проти даних: дві шини ──────────────────────────────────────────
def fig_addr_data():
    W, H = 760, 360
    f = [text(W / 2, 28, "Адреса проти даних: розмова двома шинами", size=16, bold=True)]

    # процесор ліворуч
    px, py, pw, ph = 60, 110, 150, 140
    f.append(rect(px, py, pw, ph, fill=FILL, stroke=INK, sw=2))
    f.append(text(px + pw / 2, py + ph / 2 + 5, "процесор", size=14, bold=True))

    # пам'ять праворуч
    mx, my, mw, mh = 550, 110, 150, 140
    f.append(rect(mx, my, mw, mh, fill=FILL, stroke=INK, sw=2))
    f.append(text(mx + mw / 2, my + mh / 2 + 5, "пам'ять", size=14, bold=True))

    # адресна шина: процесор → пам'ять, «де»
    ya = py + 34
    f.append(arrow(px + pw, ya, mx, ya, color=ADDR, sw=2.2))
    f.append(text((px + pw + mx) / 2, ya - 12, "адресна шина — «де»", size=12, color=ADDR, bold=True))
    f.append(text((px + pw + mx) / 2, ya + 18, "0x20", size=12, color=ADDR, bold=True))

    # шина даних: двобічна, «що»
    yd = py + 86
    f.append(arrow(mx, yd, px + pw, yd, color=VAL, sw=2.2))
    f.append(arrow(px + pw, yd + 14, mx, yd + 14, color=VAL, sw=1.4))
    f.append(text((px + pw + mx) / 2, yd - 10, "шина даних — «що»", size=12, color=VAL, bold=True))
    f.append(text((px + pw + mx) / 2, yd + 34, "байт 0x41", size=12, color=VAL, bold=True))

    # шина керування внизу
    yc = py + ph - 6
    f.append(line(px + pw, yc, mx, yc, color=FIELD, sw=1.6, dash="5 4"))
    f.append(text((px + pw + mx) / 2, yc + 16, "шина керування — читати чи писати", size=10.5, color=FIELD, italic=True))

    f.append(text(W / 2, H - 22,
                  "0x20 і 0x41 — обидва числа, та сенс різний: одне — місце, інше — значення.",
                  size=11.5, bold=True))
    render(os.path.join(IMG, "addr-data.svg"), W, H, *f)


# ── 3. Побайтова адресація: багатобайтове число в сусідніх комірках ──────────
def fig_byte_addr():
    W, H = 760, 360
    f = [text(W / 2, 28, "Одна адреса = один байт", size=16, bold=True),
         text(W / 2, 50, "багатобайтове число займає кілька СУСІДНІХ адрес",
              size=11, color=MUTED, italic=True)]

    # 32-бітне 0x12345678 у чотирьох комірках
    cells = [("0x10", "0x12"), ("0x11", "0x34"), ("0x12", "0x56"), ("0x13", "0x78")]
    cw, ch = 130, 56
    x0 = (W - len(cells) * cw) / 2
    top = 120
    for i, (addr, val) in enumerate(cells):
        x = x0 + i * cw
        f.append(rect(x, top, cw - 8, ch, fill=FIELD if False else "#eef7ee", stroke=FIELD, sw=1.8))
        f.append(text(x + (cw - 8) / 2, top - 10, addr, size=11, color=ADDR, bold=True))
        f.append(text(x + (cw - 8) / 2, top + ch / 2 + 6, val, size=15, color=INK, bold=True))
    # дужка «одне 32-бітне число»
    by = top + ch + 24
    f.append(line(x0, by, x0 + len(cells) * cw - 8, by, color=INK, sw=1.6))
    f.append(text(W / 2, by + 20, "одне 32-бітне число 0x12345678", size=12.5, bold=True))

    f.append(text(W / 2, H - 56,
                  "16-бітне → 2 комірки · 32-бітне → 4 · 64-бітне → 8.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 34,
                  "У якому ПОРЯДКУ викладені байти (старший чи молодший першим) — це endianness;",
                  size=10, color=MUTED, italic=True))
    f.append(text(W / 2, H - 16,
                  "тут важливо лише те, що комірки сусідні (а кратна розміру адреса — вирівнювання).",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "byte-addr.svg"), W, H, *f)


# ── 4. Розмір адресного простору: 2^N ────────────────────────────────────────
def fig_space():
    W, H = 859, 400
    f = [text(W / 2, 28, "N бітів адреси → 2ᴺ комірок", size=16, bold=True),
         text(W / 2, 50, "кожен доданий біт адреси ПОДВОЮЄ обсяг, який можна адресувати",
              size=11, color=MUTED, italic=True)]

    rows = [("8 біт", "2⁸ = 256 байтів"),
            ("16 біт", "2¹⁶ = 65 536 (64 КБ)"),
            ("24 біт", "2²⁴ = 16 МБ"),
            ("32 біт", "2³² ≈ 4.3 млрд (4 ГБ)"),
            ("64 біт", "2⁶⁴ ≈ 1.8·10¹⁹ (16 ЕБ)")]
    top, rh = 92, 50
    lblx, barx, barmax = 150, 230, 470
    # ширини стовпчиків ростуть логарифмічно (інакше 64 біт розчавить решту)
    bits = [8, 16, 24, 32, 64]
    for i, (lbl, desc) in enumerate(rows):
        y = top + i * rh
        w = barmax * (bits[i] / 64.0)
        f.append(text(lblx, y + 22, lbl, size=12.5, anchor="end", bold=True))
        f.append(rect(barx, y + 6, max(w, 30), 30, fill="#eaf0fd", stroke=NEG, sw=1.6))
        f.append(text(barx + max(w, 30) + 12, y + 26, desc, size=11.5, color=INK, anchor="start", bold=True))

    f.append(text(W / 2, H - 20,
                  "Ширина адреси задає СТЕЛЮ пам'яті: 16-бітна не дотягнеться далі 64 КБ, скільки б чипів не приставив.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "space.svg"), W, H, *f)


# ── 5. Дві операції: читання й запис ─────────────────────────────────────────
def fig_rw():
    W, H = 760, 360
    f = [text(W / 2, 28, "Уся робота з пам'яттю — читання й запис", size=16, bold=True)]

    # ЧИТАННЯ — ліва половина
    lx = 190
    f.append(text(lx, 80, "ЧИТАННЯ (read)", size=13, color=NEG, bold=True))
    f.append(rect(lx - 130, 100, 110, 50, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(lx - 75, 130, "процесор", size=11.5, bold=True))
    f.append(rect(lx + 20, 100, 110, 50, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(lx + 75, 130, "пам'ять", size=11.5, bold=True))
    f.append(arrow(lx - 20, 116, lx + 20, 116, color=ADDR, sw=2))
    f.append(text(lx, 110, "адреса", size=9.5, color=ADDR))
    f.append(arrow(lx + 20, 138, lx - 20, 138, color=VAL, sw=2))
    f.append(text(lx, 156, "байт ←", size=9.5, color=VAL))
    f.append(text(lx, 188, "даю адресу — отримую байт", size=10.5, color=MUTED, italic=True))

    # ЗАПИС — права половина
    rx = 570
    f.append(text(rx, 80, "ЗАПИС (write)", size=13, color=POS, bold=True))
    f.append(rect(rx - 130, 100, 110, 50, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(rx - 75, 130, "процесор", size=11.5, bold=True))
    f.append(rect(rx + 20, 100, 110, 50, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(rx + 75, 130, "пам'ять", size=11.5, bold=True))
    f.append(arrow(rx - 20, 116, rx + 20, 116, color=ADDR, sw=2))
    f.append(text(rx, 110, "адреса", size=9.5, color=ADDR))
    f.append(arrow(rx - 20, 138, rx + 20, 138, color=VAL, sw=2))
    f.append(text(rx, 156, "+ байт →", size=9.5, color=VAL))
    f.append(text(rx, 188, "даю адресу І байт — пам'ять зберігає", size=10.5, color=MUTED, italic=True))

    f.append(line(W / 2, 70, W / 2, 210, color=MUTED, sw=1, dash="4 4"))

    f.append(text(W / 2, 252,
                  "Вибірка команди — читання. Збереження результату — запис. Змінна: присвоїв — запис, ужив — читання.",
                  size=11, bold=True))
    f.append(text(W / 2, H - 24,
                  "Доступ ВИПАДКОВИЙ (random access, звідси RAM): будь-яка комірка напряму й миттєво.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "rw.svg"), W, H, *f)


# ── 6. Комірка тримає число; сенс — за вживанням ─────────────────────────────
def fig_meaning():
    W, H = 760, 400
    f = [text(W / 2, 28, "Комірка тримає просто число — сенс надає вживання", size=16, bold=True)]

    # центральна комірка
    cx, cy = W / 2, 110
    f.append(rect(cx - 110, cy - 26, 220, 52, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, cy - 4, "комірка 0x20  =  0x41", size=14, bold=True))
    f.append(text(cx, cy + 16, "(бітами: 0100 0001)", size=11, color=MUTED, italic=True))

    # чотири тлумачення, розходяться донизу
    interp = [
        ("як ціле", "65", NEG),
        ("як символ", "'A'", FIELD),
        ("як команда", "шматок opcode", POS),
        ("як float", "кілька бітів дробу", "#8e44ad"),
    ]
    bw2, bh2 = 160, 56
    gap = (W - len(interp) * bw2) / (len(interp) + 1)
    by = 230
    for i, (lab, val, col) in enumerate(interp):
        x = gap + i * (bw2 + gap)
        f.append(arrow(cx, cy + 26, x + bw2 / 2, by, color=col, sw=1.5))
        f.append(rect(x, by, bw2, bh2, fill=BG, stroke=col, sw=1.6))
        f.append(text(x + bw2 / 2, by + 22, lab, size=12, color=col, bold=True))
        f.append(text(x + bw2 / 2, by + 42, val, size=11.5, color=INK))

    f.append(text(W / 2, H - 40,
                  "Той самий байт — і число, і буква, і код. Адреса каже лише ДЕ; що він ОЗНАЧАЄ — вирішує програма.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 18,
                  "Прочитати не за тією домовленістю (текст як команду, ціле як дріб) — і все ламається.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "meaning.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки 📜 hist-core-memory
# ════════════════════════════════════════════════════════════════════════════

GOLD = "#b9770e"


# ── h1. Дорога до надійної пам'яті: часова лінія ─────────────────────────────
def fig_timeline():
    W, H = 820, 360
    f = [text(W / 2, 28, "Як машини вчилися пам'ятати", size=16, bold=True)]

    y = 150
    f.append(line(60, y, W - 60, y, color=MUTED, sw=2))
    nodes = [
        ("~1946", "лінії затримки", "ртуть; біти по колу,\nпослідовно й повільно", MUTED, -1),
        ("1947", "трубки Вільямса", "плямки на екрані;\nшвидко, та крихко", MUTED, 1),
        ("~1950", "магнітні барабани", "місткі, але механічні —\nчекай оберту", MUTED, -1),
        ("1953", "пам'ять на осердях", "швидкість, надійність,\nвипадковий доступ,\nнелеткість", POS, 1),
    ]
    n = len(nodes)
    for i, (yr, name, desc, col, side) in enumerate(nodes):
        x = 110 + i * (W - 220) / (n - 1)
        f.append(circle(x, y, 8, fill=col if col == POS else BG, stroke=col, sw=2.4))
        f.append(text(x, y + (-22 if side < 0 else 30), yr, size=12, color=col, bold=True))
        boxy = y - 120 if side < 0 else y + 44
        lines = desc.split("\n")
        bh = 26 + len(lines) * 15
        f.append(rect(x - 95, boxy, 190, bh, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x, boxy + 18, name, size=12, color=col, bold=True))
        f.append(mtext(x, boxy + 36, lines, size=9.5, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "Осердя (червоний вузол) дали все одразу й панували ~20 років, аж поки DRAM не успадкувала їхню ідею.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── h2. Один біт у феритовому кільці ─────────────────────────────────────────
def fig_core_bit():
    W, H = 720, 360
    f = [text(W / 2, 28, "Один біт у феритовому кільці", size=16, bold=True)]

    def ring(cx, cy, cw_dir, col, label, sub):
        # кільце
        f.append('<circle cx="%.1f" cy="%.1f" r="46" fill="none" stroke="%s" stroke-width="14"/>'
                 % (cx, cy, col))
        # стрілка напрямку намагнічення (дуга зі стрілкою)
        if cw_dir > 0:  # за годинниковою
            f.append('<path d="M %.1f %.1f A 46 46 0 1 1 %.1f %.1f" fill="none" stroke="%s" '
                     'stroke-width="2.4" marker-end="url(#arrow)"/>' % (cx, cy - 60, cx + 4, cy - 60, INK))
        else:
            f.append('<path d="M %.1f %.1f A 46 46 0 1 0 %.1f %.1f" fill="none" stroke="%s" '
                     'stroke-width="2.4" marker-end="url(#arrow)"/>' % (cx, cy - 60, cx - 4, cy - 60, INK))
        f.append(text(cx, cy + 5, label, size=22, color=col, bold=True))
        f.append(text(cx, cy + 78, sub, size=11.5, color=MUTED, italic=True))

    ring(200, 160, +1, NEG, "0", "намагнічене за годинниковою")
    ring(520, 160, -1, POS, "1", "намагнічене проти")

    f.append(text(W / 2, H - 56,
                  "Ключ — гістерезис: петля майже прямокутна, тож стан «застрягає» і тримається сам собою.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 32,
                  "Тому осердя, на відміну від тригера, пам'ятає й знеструмлене:",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, H - 14,
                  "вимкнув машину — а пам'ять ціла (нелеткість).",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "core-bit.svg"), W, H, *f)


# ── h3. Збіг струмів: адресація X–Y ──────────────────────────────────────────
def fig_coincident():
    W, H = 720, 440
    f = [text(W / 2, 28, "Геній Форрестера: адресація збігом струмів", size=16, bold=True)]

    # сітка 4×4 кілець
    n = 4
    x0, y0, step = 200, 90, 70
    sel = (2, 1)  # обране осердя (рядок, стовпець) — на перетині
    for r in range(n):
        for c in range(n):
            cx, cy = x0 + c * step, y0 + r * step
            on = (r == sel[0] and c == sel[1])
            half = (r == sel[0]) or (c == sel[1])
            col = POS if on else (GOLD if half else MUTED)
            sw = 6 if on else 4
            f.append('<circle cx="%.1f" cy="%.1f" r="16" fill="none" stroke="%s" stroke-width="%d"/>'
                     % (cx, cy, col, sw))

    # дроти X (рядки) і Y (стовпці) — підсвічуємо обрані
    for r in range(n):
        yy = y0 + r * step
        col = POS if r == sel[0] else MUTED
        f.append(line(x0 - 40, yy, x0 + (n - 1) * step + 40, yy, color=col, sw=2.2 if r == sel[0] else 1))
    for c in range(n):
        xx = x0 + c * step
        col = POS if c == sel[1] else MUTED
        f.append(line(xx, y0 - 40, xx, y0 + (n - 1) * step + 40, color=col, sw=2.2 if c == sel[1] else 1))

    # підписи струмів
    f.append(text(x0 - 50, y0 + sel[0] * step + 4, "½", size=15, color=POS, anchor="end", bold=True))
    f.append(text(x0 + sel[1] * step, y0 - 50, "½", size=15, color=POS, bold=True))
    selx, sely = x0 + sel[1] * step, y0 + sel[0] * step
    f.append(text(selx + 30, sely - 22, "½+½ = повний → перемикається", size=11, color=POS, anchor="start", bold=True))

    f.append(text(x0 + (n - 1) * step + 60, y0 + 4, "X", size=14, color=MUTED, bold=True, anchor="start"))
    f.append(text(x0 + 4, y0 - 50, "Y", size=14, color=MUTED, bold=True))

    f.append(text(W / 2, H - 56,
                  "Пів-струму по рядку X плюс пів-струму по стовпцю Y дають повний струм РІВНО на перетині.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 34,
                  "Решта осердь дістають лише половину — замало, щоб перемкнутися.",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, H - 14,
                  "Так одне осердя з тисяч адресують ДВОМА дротами, а не дротом до кожного.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "coincident.svg"), W, H, *f)


# ── h4. Руйнівне читання й відновлення ───────────────────────────────────────
def fig_destructive():
    W, H = 760, 360
    f = [text(W / 2, 28, "Читання, що руйнує — і відновлення", size=16, bold=True)]

    steps = [
        ("1. було", "1", NEG, "осердя в стані 1"),
        ("2. читаємо", "→0", POS, "силоміць у 0;\nперемикання дає\n«клац» у сенс-дроті"),
        ("3. висновок", "був «клац»\n= там була 1", INK, "нема клацу = був 0"),
        ("4. відновлюємо", "1", NEG, "записуємо назад:\nцикл read-restore"),
    ]
    bw2, gap = 150, 30
    x = gap
    y = 110
    for i, (title, big, col, desc) in enumerate(steps):
        f.append(rect(x, y, bw2, 70, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + bw2 / 2, y + 22, title, size=12, color=col, bold=True))
        f.append(mtext(x + bw2 / 2, y + 44, big.split("\n"), size=13 if "\n" not in big else 11, color=col, bold=True))
        f.append(mtext(x + bw2 / 2, y + 92, desc.split("\n"), size=9.5, color=MUTED))
        if i < len(steps) - 1:
            f.append(arrow(x + bw2 + 2, y + 35, x + bw2 + gap - 2, y + 35, color=INK, sw=1.8))
        x += bw2 + gap

    f.append(text(W / 2, H - 40,
                  "Читання ЗНИЩИЛО значення (осердя тепер у 0), тож одразу його записують назад.",
                  size=11.5, bold=True))
    f.append(text(W / 2, H - 18,
                  "Цю саму логіку — прочитав, одразу відновив — успадкувала сучасна DRAM.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "destructive.svg"), W, H, *f)


# ── h5. Чому осердя змінили все ──────────────────────────────────────────────
def fig_significance():
    W, H = 720, 360
    f = [text(W / 2, 28, "Чому осердя змінили все", size=16, bold=True)]

    items = [
        ("випадковий доступ", "будь-яка комірка миттєво,\nне чекаючи оберту", NEG),
        ("надійність і швидкість", "не гасне, не плутає —\nнарешті можна покластися", FIELD),
        ("нелеткість", "тримала дані\nбез живлення", GOLD),
        ("сітка адрес X–Y", "пам'ять стала решіткою\nкомірок, кожна за адресою", POS),
    ]
    bw2, bh2 = 300, 90
    gapx, gapy = 40, 30
    x0 = (W - 2 * bw2 - gapx) / 2
    y0 = 70
    for i, (title, desc, col) in enumerate(items):
        r, c = divmod(i, 2)
        x = x0 + c * (bw2 + gapx)
        y = y0 + r * (bh2 + gapy)
        f.append(rect(x, y, bw2, bh2, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + bw2 / 2, y + 26, title, size=13.5, color=col, bold=True))
        f.append(mtext(x + bw2 / 2, y + 48, desc.split("\n"), size=11, color=MUTED))

    f.append(text(W / 2, H - 18,
                  "Остання — точнісінько та модель, що живе в кожному чипі: пам'ять як масив комірок із адресами.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "significance.svg"), W, H, *f)


if __name__ == "__main__":
    # тема
    fig_array()
    fig_addr_data()
    fig_byte_addr()
    fig_space()
    fig_rw()
    fig_meaning()
    # вставка про осердя
    fig_timeline()
    fig_core_bit()
    fig_coincident()
    fig_destructive()
    fig_significance()
    print("OK: figures written to", IMG)
