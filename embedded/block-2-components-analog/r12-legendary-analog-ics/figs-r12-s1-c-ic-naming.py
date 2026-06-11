# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки 🔌 до теми 2.12.1 —
«Розшифровка назв ІМС: префікси NE/LM/TL/CD/74 і суфікси корпусів».
(Модуль 2, Розділ 12, тема 1, компонентна вставка.)

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
ОКРЕМИЙ скрипт: не чіпає головний figs.py розділу. Імена SVG унікальні
(префікс fig-r12-s1c-*), щоб не зіткнутися з іншими фігурами розділу.

Стиль (AUTHORING §9): білий фон; шрифт sans-serif; стрілки через marker.
Підписи вставки до теми — секція «c» (Рис. 2.12.1c.k).
Допоміжні функції скопійовано з figs.py розділу 13 (єдиний вигляд курсу).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
PURP  = "#7a3aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
LPUR  = "#f2ecf7"
LGREY = "#f2f2f2"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.12.1c.1 — Анатомія назви ІМС: розбираємо два реальні позначення
#   на іменовані поля (виробник · ядро · підсімейство · корпус · стрічка).
# ---------------------------------------------------------------------------
def fig_anatomy():
    W, H = 940, 470
    body = text(W / 2, 34, "Анатомія назви ІМС: ті самі поля у двох позначеннях",
                size=20, anchor="middle", weight="bold")

    # Кольори полів: виробник, ядро, підсімейство логіки, корпус, темп/стрічка
    C_MFR = (BLUE,  LBLUE)
    C_FAM = (RED,   LRED)
    C_SUB = (PURP,  LPUR)
    C_PKG = (GREEN, LGRN)
    C_OPT = (SUN,   LSUN)

    def field_row(y, segments, label):
        """segments: list of (text, (stroke,fill), w) ; малює рядок коробочок."""
        nonlocal body
        x = 150.0
        boxh = 56
        # підпис рядка ліворуч
        body += text(132, y + boxh / 2 + 6, label, size=14, anchor="end",
                     color=GREY, style="italic")
        cells = []
        for txt, (stroke, fill), w in segments:
            body += rect(x, y, w, boxh, fill=fill, stroke=stroke, sw=2.2, rx=7)
            body += text(x + w / 2, y + boxh / 2 + 9, txt, size=26,
                         anchor="middle", weight="bold", color=stroke, font=MONO)
            cells.append((x, x + w, stroke, fill))
            x += w + 4
        return cells, boxh, x

    # ---- Перший приклад: SN 74 HC 595 D R --------------------------------
    y1 = 92
    seg1 = [
        ("SN", C_MFR, 78),
        ("74", C_FAM, 70),
        ("HC", C_SUB, 76),
        ("595", C_FAM, 100),
        ("D",  C_PKG, 56),
        ("R",  C_OPT, 56),
    ]
    cells1, bh, _ = field_row(y1, seg1, "цифрова логіка")

    # підписи-виноски під першим рядком
    notes1 = [
        (cells1[0], C_MFR, "виробник", "(Texas Instr.)"),
        (cells1[1], C_FAM, "сімейство", "74xx-логіка"),
        (cells1[2], C_SUB, "підсімейство", "HC = CMOS, швидке"),
        (cells1[3], C_FAM, "функція", "595 = зсувний регістр"),
        (cells1[4], C_PKG, "корпус", "D = SOIC"),
        (cells1[5], C_OPT, "стрічка", "R = на котушці"),
    ]
    ynote = y1 + bh + 26
    for cell, (col, _fill), lab, sub in notes1:
        x0, x1c = cell[0], cell[1]
        cx = (x0 + x1c) / 2
        body += line(cx, y1 + bh + 2, cx, ynote - 14, color=col, w=1.6)
        body += text(cx, ynote, lab, size=13, anchor="middle", weight="bold", color=col)
        body += text(cx, ynote + 16, sub, size=11.5, anchor="middle", color=INK)

    # ---- Другий приклад: NE 555 P ---------------------------------------
    y2 = 286
    seg2 = [
        ("NE",  C_MFR, 86),
        ("555", C_FAM, 116),
        ("P",   C_OPT, 64),
    ]
    cells2, bh2, _ = field_row(y2, seg2, "аналогова ІМС")
    notes2 = [
        (cells2[0], C_MFR, "префікс-серія", "NE = «commercial»"),
        (cells2[1], C_FAM, "функція", "555 = таймер"),
        (cells2[2], C_OPT, "корпус", "P = DIP"),
    ]
    ynote2 = y2 + bh2 + 26
    for cell, (col, _fill), lab, sub in notes2:
        x0, x1c = cell[0], cell[1]
        cx = (x0 + x1c) / 2
        body += line(cx, y2 + bh2 + 2, cx, ynote2 - 14, color=col, w=1.6)
        body += text(cx, ynote2, lab, size=13, anchor="middle", weight="bold", color=col)
        body += text(cx, ynote2 + 16, sub, size=11.5, anchor="middle", color=INK)

    # нижня плашка-висновок
    yb = 408
    body += rect(150, yb, W - 200, 44, fill=LGREY, stroke=GREY, sw=1.4, rx=8)
    body += text(W / 2, yb + 19, "Завжди три питання до позначення:",
                 size=14.5, anchor="middle", weight="bold")
    body += text(W / 2, yb + 37,
                 "1) хто й що це за функція (середина)   ·   2) яке підсімейство (швидкість/живлення)   "
                 "·   3) який корпус і пакування (хвіст)",
                 size=12.5, anchor="middle", color=INK)

    save("fig-r12-s1c-1-anatomy.svg", header(W, H) + body + footer())


# ---------------------------------------------------------------------------
# Рис. 2.12.1c.2 — Та сама функція у трьох корпусах: суфікс міняє лише пайку,
#   а не схему. Силуети DIP / SOIC / SOT-23 з типовими суфіксами.
# ---------------------------------------------------------------------------
def fig_packages():
    W, H = 940, 320
    body = text(W / 2, 34, "Один кристал — багато корпусів: суфікс міняє пайку, не функцію",
                size=20, anchor="middle", weight="bold")

    def pins_side(cx_left, cx_right, ytop, n, color):
        """малює n виводів зліва й справа (вивідний корпус)."""
        s = ""
        step = 16
        for i in range(n):
            yy = ytop + 14 + i * step
            s += line(cx_left - 16, yy, cx_left, yy, color=color, w=2.4)
            s += line(cx_right, yy, cx_right + 16, yy, color=color, w=2.4)
        return s

    # --- DIP-8 ---
    bx, by, bw, bh = 120, 90, 120, 150
    body += text(bx + bw / 2, 70, "DIP / PDIP", size=15, anchor="middle", weight="bold", color=INK)
    body += rect(bx, by, bw, bh, fill="#f7f7f7", stroke=INK, sw=2.4, rx=4)
    body += pins_side(bx, bx + bw, by, 4, GREY)
    # виїмка-ключ
    body += (f'<path d="M{bx + bw/2 - 12},{by} a12,12 0 0,0 24,0" '
             f'fill="#ffffff" stroke="{INK}" stroke-width="2"/>\n')
    body += text(bx + bw / 2, by + bh + 26, "наскрізний монтаж", size=12.5, anchor="middle", color=GREY)
    body += text(bx + bw / 2, by + bh + 46, "суфікс P / N", size=14, anchor="middle",
                 weight="bold", color=GREEN, font=MONO)

    # --- SOIC-8 ---
    bx2, by2, bw2, bh2 = 410, 110, 120, 110
    body += text(bx2 + bw2 / 2, 70, "SOIC / SO", size=15, anchor="middle", weight="bold", color=INK)
    body += rect(bx2, by2, bw2, bh2, fill="#f7f7f7", stroke=INK, sw=2.4, rx=4)
    body += pins_side(bx2, bx2 + bw2, by2, 4, GREY)
    body += (f'<circle cx="{bx2 + 16}" cy="{by2 + 16}" r="4" fill="{INK}"/>\n')
    body += text(bx2 + bw2 / 2, by2 + bh2 + 26, "SMD, крок 1.27 мм", size=12.5, anchor="middle", color=GREY)
    body += text(bx2 + bw2 / 2, by2 + bh2 + 46, "суфікс D", size=14, anchor="middle",
                 weight="bold", color=GREEN, font=MONO)

    # --- SOT-23 ---
    bx3, by3, bw3, bh3 = 700, 130, 96, 64
    body += text(bx3 + bw3 / 2, 70, "SOT-23 / TSSOP", size=15, anchor="middle", weight="bold", color=INK)
    body += rect(bx3, by3, bw3, bh3, fill="#f7f7f7", stroke=INK, sw=2.4, rx=3)
    # три ноги знизу-зверху (мінікорпус)
    for i, xx in enumerate([bx3 + 22, bx3 + bw3 - 22]):
        body += line(xx, by3, xx, by3 - 14, color=GREY, w=2.4)
    body += line(bx3 + bw3 / 2, by3 + bh3, bx3 + bw3 / 2, by3 + bh3 + 14, color=GREY, w=2.4)
    body += text(bx3 + bw3 / 2, by3 + bh3 + 40, "дрібний SMD", size=12.5, anchor="middle", color=GREY)
    body += text(bx3 + bw3 / 2, by3 + bh3 + 60, "суфікс DBV / PW", size=14, anchor="middle",
                 weight="bold", color=GREEN, font=MONO)

    # масштабна підказка (розмір падає зліва направо)
    body += arrow(265, 285, 670, 285, color=GREY, w=2.2)
    body += text(465, 305, "менший корпус, дрібніша пайка — функція та сама",
                 size=13, anchor="middle", color=GREY, style="italic")

    save("fig-r12-s1c-2-packages.svg", header(W, H) + body + footer())


if __name__ == "__main__":
    fig_anatomy()
    fig_packages()
    print("done")
