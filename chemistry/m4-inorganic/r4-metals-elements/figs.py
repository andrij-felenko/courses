# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.4 — «Метали й елементи навколо нас» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; метали сіро-фіолетові,
кисень червоний; усі підписи українською. Хелпери скопійовані.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
INK    = "#1b1b1b"
GREY   = "#8a8a8a"
FAINT  = "#e9e9e9"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
MET    = "#8a7fae"
MET_LN = "#6f6394"
GOLD   = "#c9a22e"
RUST   = "#a6552f"
IRON   = "#b3aebd"
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def chip(cx, cy, w, h, label, fill, border, tcol=INK):
    s = rect(cx - w / 2, cy - h / 2, w, h, fill, border, 1.8, 9)
    s += text(cx, cy + 5, label, 13, tcol, "middle", "bold")
    return s


def o2(cx, cy):
    return circle(cx - 6, cy, 7, O_FILL, O_LINE, 1.5) + circle(cx + 6, cy, 7, O_FILL, O_LINE, 1.5)


def rustpatch(cx, cy):
    s = ""
    for dx, dy, r, c in [(-9, 0, 7, "#8a3f22"), (2, -3, 8, RUST), (9, 2, 6, "#c06a3a"), (-2, 4, 6, "#8a3f22")]:
        s += circle(cx + dx, cy + dy, r, c, "none", 0)
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 4.4.1-1 — ряд активності ────────────────────────────────────────────
def fig_activity():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 30, "Ряд активності: хто легше віддає електрони", 21, INK, "middle", "bold")
    s += text(W / 2, 52, "ліворуч — щедрі (швидко реагують, іржавіють), праворуч — скупі (лежать віками)",
              12.5, GREY, "middle", style="italic")

    metals = ["натрій", "магній", "алюміній", "цинк", "залізо", "мідь", "срібло", "золото"]
    cxs = [120 + i * (680 / 7) for i in range(8)]

    s += arrow(90, 112, 838, 112, GREY, 2)
    s += text(96, 100, "віддають електрони ЛЕГКО", 12, RED, "start", "bold")
    s += text(832, 100, "тримають МІЦНО", 12, GOLD, "end", "bold")

    for i, (cx, m) in enumerate(zip(cxs, metals)):
        if i == 3:      # цинк
            fill, bd, tc = "#e9f0e6", GREEN, INK
        elif i == 4:    # залізо
            fill, bd, tc = "#fde4e4", RED, INK
        elif i == 7:    # золото
            fill, bd, tc = "#f7edbf", GOLD, INK
        else:
            fill, bd, tc = "#ece9f3", MET_LN, INK
        s += chip(cx, 150, 90, 34, m, fill, bd, tc)

    s += text(cxs[0], 192, "реагує бурхливо", 11, RED, "middle")
    s += text(cxs[4], 192, "іржавіє", 11.5, RED, "middle", "bold")
    s += text(cxs[7], 192, "вічний блиск", 11.5, GOLD, "middle", "bold")

    # дужка цинк → залізо
    bx1, bx2 = cxs[3], cxs[4]
    s += line(bx1, 214, bx2, 214, GREEN, 1.6)
    s += line(bx1, 210, bx1, 214, GREEN, 1.6)
    s += line(bx2, 210, bx2, 214, GREEN, 1.6)
    s += text((bx1 + bx2) / 2, 232, "цинк активніший → жертовний для заліза", 12, GREEN, "middle", "bold")

    s += text(W / 2, 268, "активніший метал витісняє лінивішого з його солі — й іржавіє замість нього",
              12.5, GREY, "middle", style="italic")
    save("fig-4-4-1-1-activity.svg", s)


# ── Рис. 4.4.1-2 — три способи захистити залізо ──────────────────────────────
def fig_protection():
    W, H = 880, 340
    s = header(W, H)
    s += text(W / 2, 30, "Як захистити залізо від іржі", 20, INK, "middle", "bold")

    panels = [(160, "голе залізо"), (440, "фарба або мастило"), (720, "оцинковане (цинк)")]
    by, bw, bh = 178, 180, 30
    for cx, title in panels:
        s += text(cx, 86, title, 14.5, INK, "middle", "bold")

    # 1 — голе залізо
    cx = 160
    s += rect(cx - bw / 2, by, bw, bh, IRON, INK, 1.8, 3)
    for dx in (-50, 0, 50):
        s += o2(cx + dx, by - 40)
        s += arrow(cx + dx, by - 28, cx + dx, by - 4, INK, 1.8)
    for dx in (-46, -2, 46):
        s += rustpatch(cx + dx, by + 4)
    s += text(cx, by + bh + 36, "кисень дістає залізо → іржа", 12.5, RED, "middle", "bold")

    # 2 — фарба/мастило: бар'єр
    cx = 440
    s += rect(cx - bw / 2, by, bw, bh, IRON, INK, 1.8, 3)
    s += rect(cx - bw / 2, by - 9, bw, 9, "#3f9e54", "#256b34", 1.4, 2)
    for dx in (-50, 0, 50):
        s += o2(cx + dx, by - 42)
        s += arrow(cx + dx, by - 30, cx + dx, by - 14, INK, 1.8)
    s += text(cx, by - 56, "✕ не доходить", 11.5, GREEN, "middle", "bold")
    s += text(cx, by + bh + 36, "бар'єр не пускає кисень і воду", 12.5, GREEN, "middle", "bold")

    # 3 — оцинковане: цинк жертвує собою (з подряпиною)
    cx = 720
    s += rect(cx - bw / 2, by, bw, bh, IRON, INK, 1.8, 3)
    # шар цинку з подряпиною посередині
    s += rect(cx - bw / 2, by - 9, bw / 2 - 6, 9, MET, MET_LN, 1.4, 2)
    s += rect(cx + 6, by - 9, bw / 2 - 6, 9, MET, MET_LN, 1.4, 2)
    s += text(cx, by - 16, "подряпина", 10, GREY, "middle")
    for dx in (-50, 0, 50):
        s += o2(cx + dx, by - 44)
        s += arrow(cx + dx, by - 32, cx + dx, by - 12, INK, 1.8)
    s += rustpatch(cx - 50, by - 7)
    s += rustpatch(cx + 50, by - 7)
    s += text(cx, by + bh + 36, "цинк жертвує собою — залізо ціле", 12.5, GREEN, "middle", "bold")

    s += text(W / 2, 322, "відгородити залізо (фарба) або підставити активніший метал (цинк)",
              12.5, GREY, "middle", style="italic")
    save("fig-4-4-1-2-protection.svg", s)


# ── Рис. 4.4.2-1 — галерея характерів ────────────────────────────────────────
def tile(cx, top, w, h, sym, name, role1, role2, fill, border, symcol):
    s = rect(cx - w / 2, top, w, h, fill, border, 1.8, 12)
    s += text(cx, top + 42, sym, 30, symcol, "middle", "bold")
    s += text(cx, top + 68, name, 14, INK, "middle", "bold")
    s += text(cx, top + 90, role1, 10.5, GREY, "middle")
    s += text(cx, top + 106, role2, 10.5, GREY, "middle")
    return s


def fig_gallery():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Головні елементи довкола — їхні характери", 21, INK, "middle", "bold")
    s += text(W / 2, 52, "неметали повітря, життя та солі — і метали, якими будуємо й живемо",
              12.5, GREY, "middle", style="italic")

    NM, NMB, NMS = "#e8f1f0", "#4f9a92", "#2f6f68"
    ME, MEB, MES = "#efeaf6", MET_LN, MET_LN
    row1 = [("N", "Нітроген", "більшість", "повітря, лінивий"),
            ("O", "Оксиген", "ним дихаємо;", "вогонь, іржа"),
            ("C", "Карбон", "кістяк", "усього живого"),
            ("Si", "Силіцій", "пісок, скло,", "мікросхеми"),
            ("Cl", "Хлор", "пів солі;", "чистить воду")]
    row2 = [("Fe", "Ферум", "каркас;", "кисень у крові"),
            ("Al", "Алюміній", "легкий: банки,", "фольга, літаки"),
            ("Ca", "Кальцій", "кістки, зуби,", "крейда"),
            ("Na", "Натрій", "сіль і", "нервовий сигнал"),
            ("K", "Калій", "пара до", "Натрію в тілі")]
    tw, th = 158, 138
    xs = [20 + i * 170 for i in range(5)]
    for i, (sym, name, r1, r2) in enumerate(row1):
        s += tile(xs[i] + tw / 2, 76, tw, th, sym, name, r1, r2, NM, NMB, NMS)
    for i, (sym, name, r1, r2) in enumerate(row2):
        s += tile(xs[i] + tw / 2, 230, tw, th, sym, name, r1, r2, ME, MEB, MES)
    s += text(46, 408, "● неметали", 12, NMS, "start", "bold")
    s += text(170, 408, "● метали", 12, MES, "start", "bold")
    save("fig-4-4-2-1-gallery.svg", s)


# ── Рис. 4.4.2-2 — де елементи живуть у таблиці ──────────────────────────────
def fig_table_spots():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 30, "Де ці елементи живуть у таблиці", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "ті самі характери на карті періодичної таблиці", 12.5, GREY, "middle", style="italic")

    x0, y0, cell = 110, 92, 30
    occ = {2: [1, 2, 13, 14, 15, 16, 17, 18],
           3: [1, 2, 13, 14, 15, 16, 17, 18],
           4: list(range(1, 19))}
    our = {(2, 14): "C", (2, 15): "N", (2, 16): "O",
           (3, 1): "Na", (3, 13): "Al", (3, 14): "Si", (3, 17): "Cl",
           (4, 1): "K", (4, 2): "Ca", (4, 8): "Fe"}
    nonmet = {"C", "N", "O", "Si", "Cl"}

    def cellxy(col, period):
        return x0 + (col - 1) * cell, y0 + (period - 2) * (cell + 2)

    for period, cols in occ.items():
        s += text(x0 - 16, y0 + (period - 2) * (cell + 2) + 20, str(period), 12, GREY, "end", "bold")
        for col in cols:
            cx, cy = cellxy(col, period)
            sym = our.get((period, col))
            if sym:
                fill = "#e8f1f0" if sym in nonmet else "#efeaf6"
                bd = "#4f9a92" if sym in nonmet else MET_LN
                s += rect(cx, cy, cell - 2, cell - 2, fill, bd, 1.8, 4)
                s += text(cx + cell / 2 - 1, cy + 20, sym, 13, INK, "middle", "bold")
            else:
                s += rect(cx, cy, cell - 2, cell - 2, "#f6f6f6", "#dcdcdc", 1, 3)

    # родина Na/K — стовпчик 1
    fx, fy = cellxy(1, 3)
    s += rect(fx - 3, fy - 3, cell + 4, (cell + 2) + cell, "none", GREEN, 2.2, 6)
    s += text(fx + cell + 8, fy + cell, "один стовпчик —", 12, GREEN, "start", "bold")
    s += text(fx + cell + 8, fy + cell + 16, "одна родина (Na, K)", 12, GREEN, "start", "bold")

    s += text(46, 200, "● неметали", 12, "#2f6f68", "start", "bold")
    s += text(46, 218, "● метали", 12, MET_LN, "start", "bold")
    s += text(W / 2, 338, "номер ряду — це період, стовпчик — родина; сусіди по стовпчику поводяться схоже",
              12, GREY, "middle", style="italic")
    save("fig-4-4-2-2-table-spots.svg", s)


if __name__ == "__main__":
    fig_activity()
    fig_protection()
    fig_gallery()
    fig_table_spots()
