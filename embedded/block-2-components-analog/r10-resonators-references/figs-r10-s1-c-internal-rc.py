# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 🔌 2.10.1.c — «Внутрішній RC-генератор
мікроконтролера проти кварцу: коли можна заощадити».

Чистий Python без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-10-1c-…), щоб не перетинатися з головним figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py попередніх розділів.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3df"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.10.1c.1 — «сходи точності»: логарифмічна шкала похибки джерел частоти
# з накладеним бюджетом допуску асинхронного UART (±2 %).
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Похибка джерела частоти проти бюджету UART", 17, INK, "middle", "bold")

    # Логарифмічна вісь: ppm від 1 до 100000 (1 ppm = 0.0001 %, 50000 ppm = 5 %)
    ax_x = 150
    ax_w = 540
    ax_y = 360
    decades = [0, 1, 2, 3, 4, 5]  # 10^0 … 10^5 ppm
    def X(ppm):
        lo, hi = 0.0, 5.0
        v = math.log10(max(ppm, 1.0))
        return ax_x + ax_w * (v - lo) / (hi - lo)

    # Смуга «UART ще працює»: ±2 % ≈ 20000 ppm сумарної неузгодженості;
    # на джерело з одного боку — приблизно половина, ~1 % = 10000 ppm.
    band_lo = X(10000)
    s += rect(band_lo, 70, ax_x + ax_w - band_lo, ax_y - 70, LRED, "none")
    s += line(band_lo, 70, band_lo, ax_y, RED, 2, "5,4")
    s += text(ax_x + ax_w - 6, 88, "тут UART уже сипле помилки", 12.5, RED, "end", "bold")
    s += text(ax_x + ax_w - 6, 104, "(>1 % на бік)", 12, RED, "end")

    # Вісь
    s += arrow(ax_x - 14, ax_y, ax_x + ax_w + 18, ax_y, INK, 2)
    s += text(ax_x + ax_w + 22, ax_y + 4, "ppm", 13, INK, "start", "bold")
    s += text(ax_x - 14, ax_y + 26, "точніше →", 11.5, GREEN, "start")
    s += text(ax_x + ax_w + 6, ax_y + 26, "← грубіше", 11.5, RED, "end")
    for d in decades:
        x = X(10 ** d)
        s += line(x, ax_y, x, ax_y + 6, INK, 1.6)
        lbl = {0: "1", 1: "10", 2: "100", 3: "1 000", 4: "10 000", 5: "100 000"}[d]
        s += text(x, ax_y + 22, lbl, 12, INK, "middle")

    # Маркери-діапазони джерел: (назва, ppm_lo, ppm_hi, колір, y, нотатка)
    rows = [
        ("Внутрішній RC, без калібрування", 10000, 50000, RED, 130,
         "±1…5 % — гуляє з температурою й живленням"),
        ("Внутрішній RC, заводське калібр.", 5000, 20000, SUN, 178,
         "±0.5…2 % при 25 °C, далі повзе"),
        ("Керамічний резонатор", 3000, 5000, SUN, 226,
         "±0.3…0.5 %"),
        ("Кварц, типовий", 10, 50, GREEN, 274,
         "±10…50 ppm = 0.001…0.005 %"),
        ("Кварц із компенсацією (клас TCXO)", 1, 5, GREEN, 322,
         "часи й радіо"),
    ]
    for name, lo, hi, col, y, note in rows:
        x0, x1 = X(lo), X(hi)
        s += line(x0, y, x1, y, col, 7)
        s += circle(x0, y, 4, col, col, 1)
        s += circle(x1, y, 4, col, col, 1)
        s += text(ax_x - 22, y - 5, name, 12.5, INK, "end", "bold")
        s += text(ax_x - 22, y + 11, note, 11, GREY, "end")

    s += text(ax_x + ax_w / 2, H - 8, "логарифмічна шкала: кожна поділка — у 10 разів менша похибка", 11, GREY, "middle", "normal")
    save("fig-10-1c-1-accuracy-ladder.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.10.1c.2 — дерево такту МК: внутрішній RC vs зовнішній кварц на двох
# виводах OSC; під ним — таблиця «можна заощадити / потрібен кварц».
# ─────────────────────────────────────────────────────────────────────────────
def fig2():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 28, "Звідки МК бере такт і коли кварц зайвий", 17, INK, "middle", "bold")

    # Чип
    cx, cy, cw, ch = 300, 70, 200, 150
    s += rect(cx, cy, cw, ch, "#fbfbfb", INK, 2, 8)
    s += text(cx + cw / 2, cy - 8, "мікроконтролер", 13, INK, "middle", "bold")

    # Внутрішній RC всередині чипа
    s += rect(cx + 14, cy + 18, 100, 42, LSUN, SUN, 1.8, 5)
    s += text(cx + 64, cy + 35, "внутр. RC", 12, INK, "middle", "bold")
    s += text(cx + 64, cy + 51, "8…20 МГц", 11, GREY, "middle")

    # Дільник/PLL
    s += rect(cx + 70, cy + 92, 110, 40, LBLUE, BLUE, 1.8, 5)
    s += text(cx + 125, cy + 109, "PLL / дільник", 12, INK, "middle", "bold")
    s += text(cx + 125, cy + 125, "→ ядро, шини", 10.5, GREY, "middle")

    # Мультиплексор вибору джерела
    mx = cx + 30
    my = cy + 100
    s += f'<path d="M {mx},{my-16} L {mx+22},{my-8} L {mx+22},{my+8} L {mx},{my+16} Z" fill="#eef0f3" stroke="{INK}" stroke-width="1.6"/>\n'
    s += text(mx + 11, my + 4, "MUX", 8.5, INK, "middle", "bold")
    # RC → MUX
    s += arrow(cx + 64, cy + 60, mx + 4, my - 8, SUN, 2)
    # MUX → PLL
    s += arrow(mx + 22, my, cx + 70, cy + 112, BLUE, 2)

    # Два виводи кристала
    px = cx + cw
    p1y = cy + 50
    p2y = cy + 100
    s += line(px, p1y, px + 26, p1y, INK, 2)
    s += line(px, p2y, px + 26, p2y, INK, 2)
    s += circle(px + 26, p1y, 3.5, "#fff", INK, 1.6)
    s += circle(px + 26, p2y, 3.5, "#fff", INK, 1.6)
    s += text(px + 32, p1y - 4, "XTAL_IN", 11, INK, "start", "bold")
    s += text(px + 32, p2y + 14, "XTAL_OUT", 11, INK, "start", "bold")

    # Кварц між виводами + два конденсатори на землю
    qx = px + 95
    s += line(px + 26, p1y, qx, p1y, INK, 2)
    s += line(px + 26, p2y, qx, p2y, INK, 2)
    # символ кварцу (прямокутник між двома рисками)
    s += line(qx, p1y, qx, p2y, INK, 2)
    s += line(qx + 12, p1y, qx + 12, p2y, INK, 2)
    s += rect(qx + 3, (p1y + p2y) / 2 - 16, 6, 32, "#eef0f3", INK, 1.6)
    s += text(qx + 6, p1y - 8, "кварц", 11, GREEN, "middle", "bold")
    # MUX-гілка від кварцу (логічно): зовнішнє джерело теж іде в MUX
    s += arrow(px - 2, (p1y + p2y) / 2, mx + 6, my + 2, GREEN, 1.8, "4,3")

    # Конденсатори навантаження: дві ємності вниз від точок виводів
    for tx, yy in ((px + 60, p1y), (px + 60, p2y)):
        s += line(tx, yy, tx, yy + 22, INK, 1.6)
        s += line(tx - 9, yy + 22, tx + 9, yy + 22, INK, 2)
        s += line(tx - 9, yy + 28, tx + 9, yy + 28, INK, 2)
        s += line(tx, yy + 28, tx, yy + 36, INK, 1.6)
        # земля
        s += line(tx - 8, yy + 36, tx + 8, yy + 36, INK, 2)
        s += line(tx - 5, yy + 40, tx + 5, yy + 40, INK, 2)
        s += line(tx - 2, yy + 44, tx + 2, yy + 44, INK, 2)
        s += text(tx + 12, yy + 30, "CL", 10.5, GREY, "start")
    # під'єднати конденсатори до ліній кварцу
    s += line(px + 26, p1y, px + 60, p1y, INK, 2)
    s += line(px + 26, p2y, px + 60, p2y, INK, 2)
    s += line(px + 60, p1y, qx, p1y, INK, 2)
    s += line(px + 60, p2y, qx, p2y, INK, 2)

    s += text(px + 70, cy + ch + 6, "зовнішня обв'язка (опція)", 11, GREY, "start")

    # Підпис під чипом — звідки старт
    s += text(cx + cw / 2, cy + ch + 26, "Старт завжди з внутрішнього RC; кварц під'єднують лише за потреби.",
              11.5, INK, "middle")

    # Таблиця рішення
    ty = 290
    s += text(W / 2, ty, "Чи можна лишити тільки внутрішній RC?", 14, INK, "middle", "bold")
    col_l = 70
    col_r = 400
    s += rect(col_l, ty + 14, 300, 150, LGRN, GREEN, 1.6, 6)
    s += rect(col_r, ty + 14, 300, 150, LRED, RED, 1.6, 6)
    s += text(col_l + 150, ty + 34, "✓ Можна заощадити", 13, GREEN, "middle", "bold")
    s += text(col_r + 150, ty + 34, "✗ Потрібен кварц", 13, RED, "middle", "bold")
    good = [
        "блимання, опитування кнопок, ШІМ",
        "вибірка АЦП, де темп не критичний",
        "I²C-ведучий (веденому байдуже)",
        "затримки «приблизно стільки-то»",
        "автономний логер без точного часу",
    ]
    bad = [
        "USB (треба ±0.25 %)",
        "точний UART на високій швидкості",
        "відлік реального часу / годинник",
        "будь-яке радіо й RF-синтез",
        "сумісність із зовнішнім тактом",
    ]
    for i, g in enumerate(good):
        s += text(col_l + 16, ty + 58 + i * 21, "• " + g, 11.5, INK, "start")
    for i, b in enumerate(bad):
        s += text(col_r + 16, ty + 58 + i * 21, "• " + b, 11.5, INK, "start")

    save("fig-10-1c-2-clock-tree.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
