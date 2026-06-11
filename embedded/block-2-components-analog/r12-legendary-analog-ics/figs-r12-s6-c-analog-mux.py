# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки 2.12.6c —
«CD4051/74HC4066-класи: вісім давачів на один вимірювальний вхід»
(Модуль 2, Розділ 2.12, тема 2.12.6).

Окремий скрипт вставки (НЕ головний figs.py розділу). Чистий Python без
залежностей. Вивід → ./img/ із УНІКАЛЬНИМИ іменами (префікс mux-).
Допоміжні функції скопійовано зі стилю Розділу (AUTHORING §9):
білий фон; '+' червоний, '−' синій; стрілки через marker; шрифт sans-serif.
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fbf6e6"
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


def dot(cx, cy, r=3.4, col=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.6c.1 — нутрощі 8:1 мультиплексора (CD4051-клас):
# 8 каналів → один спільний вивід; 3 адресні біти крізь дешифратор; INH.
# Окремо показано суть «аналогового ключа»: двонапрямлений, з опором RON.
# ─────────────────────────────────────────────────────────────────────────────
def fig_inside():
    W, H = 760, 560
    s = header(W, H)
    s += text(W / 2, 26, "8:1 аналоговий мультиплексор (CD4051-клас): нутрощі", 17, INK, "middle", "bold")

    # корпус чипа
    bx, by, bw, bh = 250, 60, 230, 300
    s += rect(bx, by, bw, bh, fill="#fcfcfc", stroke=INK, sw=2, rx=8)
    s += text(bx + bw / 2, by + 22, "CD4051", 14, GREY, "middle", "bold")

    # спільна шина всередині (вертикальна), куди сходяться всі ключі
    busx = bx + bw - 46
    s += line(busx, by + 40, busx, by + bh - 24, GREY, 2.4, dash="2,3")

    # 8 каналів ліворуч: ключ із RON; лише канал 3 — замкнений (вибраний)
    ys = [by + 44 + i * 30 for i in range(8)]
    sel = 3
    for i, y in enumerate(ys):
        # зовнішній вивід каналу
        s += line(bx - 70, y, bx, y, INK, 2)
        s += dot(bx - 70, y, 3.2, INK)
        s += text(bx - 76, y + 5, f"Y{i}", 13, INK, "end", "bold")
        # ключ-резистор (RON) від виводу до спільної шини
        kx0 = bx + 18
        kx1 = busx
        if i == sel:
            # замкнений: зелений провідник + позначка RON
            s += line(bx, y, kx0, y, GREEN, 2.6)
            s += rect(kx0, y - 7, 34, 14, fill=LGRN, stroke=GREEN, sw=2, rx=3)
            s += text(kx0 + 17, y + 4, "Rᴏɴ", 10, GREEN, "middle", "bold")
            s += line(kx0 + 34, y, kx1, y, GREEN, 2.6)
            s += dot(kx1, y, 3.4, GREEN)
        else:
            # розімкнений: розрив (дві риски + проміжок)
            s += line(bx, y, kx0 + 8, y, GREY, 2)
            s += line(kx0 + 8, y, kx0 + 15, y - 8, GREY, 2)   # «відкинутий» контакт
            s += line(kx0 + 26, y, kx1, y, GREY, 2)
            s += dot(kx1, y, 2.6, GREY)

    # спільний вивід Z праворуч
    zx = bx + bw
    zy = by + bh / 2
    s += line(busx, zy, zx, zy, GREEN, 2.6)
    s += line(zx, zy, zx + 64, zy, GREEN, 2.6)
    s += dot(zx + 64, zy, 3.4, GREEN)
    s += text(zx + 70, zy - 8, "Z (спільний)", 13, GREEN, "start", "bold")
    s += text(zx + 70, zy + 12, "common", 11, GREY, "start", "italic")

    # дешифратор адреси знизу всередині
    dgx, dgy, dgw, dgh = bx + 18, by + bh - 18, 120, 0
    s += text(bx + 70, by + bh - 6, "дешифратор 3→8", 11, GREY, "middle", "italic")

    # 3 адресні входи + INH знизу
    addr = [("A", "0"), ("B", "1"), ("C", "1")]   # 011 = 3 → канал Y3
    for j, (nm, bit) in enumerate(addr):
        ax = bx + 34 + j * 44
        ay = by + bh
        s += arrow(ax, ay + 56, ax, ay, BLUE, 2)
        s += text(ax, ay + 72, nm, 13, BLUE, "middle", "bold")
        s += text(ax, ay + 88, f"={bit}", 11, GREY, "middle", "normal")
    # INH (enable)
    ix = bx + 34 + 3 * 44 + 10
    s += arrow(ix, by + bh + 56, ix, by + bh, RED, 2)
    s += text(ix, by + bh + 72, "INH", 12, RED, "middle", "bold")
    s += text(ix, by + bh + 88, "=0", 11, GREY, "middle", "normal")

    # підпис «адреса 011 → канал 3»
    s += rect(40, by + bh + 40, 168, 56, fill=LBLUE, stroke=BLUE, sw=1.4, rx=6)
    s += text(124, by + bh + 60, "адреса CBA = 011", 12, BLUE, "middle", "bold")
    s += text(124, by + bh + 78, "→ відкрито канал Y3", 12, INK, "middle", "normal")

    # живлення зверху
    s += text(bx + 30, by - 8, "VDD", 12, RED, "middle", "bold")
    s += text(bx + bw - 30, by - 8, "VSS/VEE", 11, BLUE, "middle", "bold")

    save("fig-r12-s6c-1-mux-inside.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.6c.2 — типове підключення: 8 давачів → один вхід АЦП;
# 3 лінії GPIO задають адресу; між перемиканням і вимірюванням — пауза t_settle.
# ─────────────────────────────────────────────────────────────────────────────
def fig_wiring():
    W, H = 770, 440
    s = header(W, H)
    s += text(W / 2, 26, "Вісім давачів на один вхід АЦП", 17, INK, "middle", "bold")

    # мікроконтролер ліворуч
    mx, my, mw, mh = 40, 96, 150, 250
    s += rect(mx, my, mw, mh, fill="#f6f8fc", stroke=INK, sw=2, rx=8)
    s += text(mx + mw / 2, my + 24, "МК", 15, INK, "middle", "bold")
    s += text(mx + mw / 2, my + 42, "(ESP32)", 11, GREY, "middle", "italic")

    # мультиплексор у центрі
    ux, uy, uw, uh = 360, 70, 150, 300
    s += rect(ux, uy, uw, uh, fill="#fcfcfc", stroke=INK, sw=2, rx=8)
    s += text(ux + uw / 2, uy + 22, "MUX 8:1", 14, INK, "middle", "bold")
    s += text(ux + uw / 2, uy + 40, "CD4051", 11, GREY, "middle", "italic")

    # 8 давачів праворуч → канали Y0..Y7
    ys = [uy + 52 + i * 32 for i in range(8)]
    for i, y in enumerate(ys):
        sx = 660
        s += rect(sx, y - 11, 88, 22, fill=LYEL, stroke=GREY, sw=1.4, rx=4)
        s += text(sx + 44, y + 4, f"давач {i}", 11, INK, "middle", "normal")
        s += arrow(sx, y, ux + uw, y, GREY, 1.8)
        s += text(ux + uw + 6, y - 6, f"Y{i}", 10, GREY, "start", "bold")

    # спільний вивід Z → один вхід АЦП
    zy = uy + uh / 2
    s += line(ux, zy, mx + mw + 40, zy, GREEN, 2.6)
    s += arrow(mx + mw + 40, zy, mx + mw, zy, GREEN, 2.6)
    s += dot(ux, zy, 3.6, GREEN)
    s += text((ux + mx + mw) / 2, zy - 10, "Z → ADC", 13, GREEN, "middle", "bold")
    s += text((ux + mx + mw) / 2, zy + 16, "одна аналогова лінія", 11, GREEN, "middle", "italic")

    # 3 адресні лінії GPIO → A,B,C
    for j, nm in enumerate(["A", "B", "C"]):
        gy = my + 80 + j * 26
        ty = uy + uh - 70 + j * 22
        s += line(mx + mw, gy, 290, gy, BLUE, 2)
        s += line(290, gy, 290, ty, BLUE, 2)
        s += arrow(290, ty, ux, ty, BLUE, 2)
        s += text(290 + 6, ty - 6, nm, 11, BLUE, "start", "bold")
    s += text(mx + mw + 8, my + 80 - 12, "3 × GPIO", 12, BLUE, "start", "bold")
    s += text(mx + mw + 8, my + 80 + 4, "(адреса)", 10, GREY, "start", "italic")

    # часова шкала знизу: select → settle → read
    tly = H - 44
    t0, t1, t2, t3 = 70, 300, 470, 700
    s += line(t0, tly, t3, tly, INK, 2)
    for tx in (t0, t1, t2, t3):
        s += line(tx, tly - 5, tx, tly + 5, INK, 2)
    s += text((t0 + t1) / 2, tly - 12, "виставити адресу", 12, BLUE, "middle", "bold")
    s += text((t1 + t2) / 2, tly - 12, "t_settle (пауза)", 12, RED, "middle", "bold")
    s += text((t2 + t3) / 2, tly - 12, "читати АЦП", 12, GREEN, "middle", "bold")
    s += text((t1 + t2) / 2, tly + 20, "Rᴏɴ · C заряджається", 10, GREY, "middle", "italic")

    save("fig-r12-s6c-2-mux-wiring.svg", s)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    print("done")
